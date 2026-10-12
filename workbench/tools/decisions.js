#!/usr/bin/env node
// Decision dataset: one row per dragon turn (plain turns sampled), with the state the dragon could see when it
// decided, the action it took and its short-horizon outcome. Reads replays only; runs no games; no network.
//
// usage:
//   node tools/decisions.js extract top [--keys data/top/snapshot-20260929a.keys] [--name top-20260929a]
//        [--jobs 3] [--force] [--limit N]
//   node tools/decisions.js extract top --top all [--name top-all] [--jobs 4]
//        every game of data/top/index.jsonl at start (the collector keeps appending; later runs add the new games).
//        data/decisions/top-all/manifest.json records the index rows read, the games and the last gameId.
//   node tools/decisions.js extract online [<set> ...] [--jobs 3] [--force]
//        no set: every data/online/<set>/index.json whose games are mostly against the fixed test teams
//   node tools/decisions.js validate [--games N] [--top all] [<replay file> ...]
//        re-simulates games, cross-checks against tools/top_features.js extract() and prints the checks
//        (--top all: the N games are spread over the whole index instead of the 2026-09-29a snapshot)
//   node tools/decisions.js refresh [--jobs 3]
//        extract every new online set (and the top snapshot if missing), then run tools/decisions_learn.js (report)
//        and tools/decisions_rules.js (key rules per team and per online group); outputs data/decisions/report.* and
//        data/decisions/rules.*
//   node tools/decisions.js refresh --top all [--jobs 4] [--legacy]
//        extract top-all (new games only) and every online set, then tools/decisions_scale.js (segment tables by map,
//        phase, team, winner/loser, length; rules R1-R8 and new ones; tree leaves; data/decisions/scale.*) and
//        tools/decisions_hyp.js (ranked hypotheses for our bot; data/decisions/hypotheses.*). --legacy also runs
//        decisions_learn.js and decisions_rules.js on top-all (data/decisions/report-all.*, rules-all.*).
// Worker threads: --jobs, at most 4 (other agents share the CPU).
// Output (incremental; --force recomputes; games extracted by an older extractor version are redone):
//   data/decisions/<set>/<game>.tsv.gz (header line + rows) and data/decisions/<set>/games.jsonl (one line per game:
//   meta, winner, our side, checks, row counts, xv = extractor version, initDragons, init = start dragons per team,
//   tl = units/total/longest per team every 10 rounds 0..500 (flat triples), tc = per-team turn counters:
//   turns, pings, pA / pE = pings stopped on another ally / an enemy, splits, none = turns with no valid action).
//   A set being written holds data/decisions/<set>/.lock (pid); a second writer skips that set.
//
// Reconstruction: the step simulation of tools/top_features.js (moves, sprints, kelp, portals, wrap, splits, deaths).
// Every simulated step is checked against the replay's dragonUpdate head/tail (checks.sim), and at every turnStart
// the acting dragon's head/tail must equal the last dragonUpdate/split for it (checks.turnHT) and its body must be a
// connected chain that owns its tiles (checks.body). All expected 0. checks.pingOrphan counts sonar pings that do not
// belong to the dragon whose turn it is (expected 0).
//
// Row = the acting dragon at its turnStart (the board it sees then; lower ids have already moved this round).
// "In view" = Chebyshev distance <= 3 on the wrapped map (the 7x7 window). "Free" = no dragon segment and no kelp
// across the edge (pearl tiles are free). Path distances are BFS steps over the map graph (kelp, portals, wrap).
// Keep rule: every turn with an enemy head in view, any action other than a 1-step move, any death on the turn,
// free <= 1, the team's longest dragon from round 300, and every turn of our side in online games (w = 1);
// otherwise 1 in SAMPLE turns (w = SAMPLE, deterministic hash). Weighted sums estimate all-turn totals.
//
// Columns (code: meaning; 99 = none / not reached; -1 = not applicable):
//  r id tm L born init fac      round, dragon id, team A/B, length at turn start, birth round, initial dragon 0/1,
//                               facing N/E/S/W
//  free nbE nbA                 free neighbour tiles; neighbours holding an enemy / ally head
//  room roomMax                 free tiles reachable from the head (flood fill, cap 64, static board); best room over
//                               the free first steps
//  tFree tE                     free neighbours of our tail (a split child's first exits); Manhattan tail to the
//                               nearest enemy head in view
//  eN eNs eNr eNrs              enemy heads in view; of those shorter than us; that can reach our head this turn
//                               (enemy BFS dist <= min(Le-1, 6), bodies block, tails free); shorter ones that can
//  eD0 eM0 eL eVis eKn eAft eFw focus enemy = in-view enemy head with the smallest path distance to our head (ties:
//                               shorter): path distance (cap 8), Manhattan, true length, its segments in our window,
//                               whole body in view 0/1, moves after us this round (higher id) 0/1, faces us 0/1
//  eLmin                        shortest enemy head in view
//  safe1 exp1 safe1a exp1a      free single steps outside / inside the reach of every shorter (a: any) enemy in view
//  safe2                        distinct end tiles of 2-3 step sprints outside shorter-enemy reach (-1 when no
//                               shorter enemy is in view)
//  oppN oppL oppD               enemy heads in view we can ram this turn (our BFS dist <= min(L-1, 6)); the longest
//                               of them and its distance
//  pN pD0 pEd pDang             pearls in view; path distance to the nearest one in view; nearest enemy path distance
//                               to that pearl; that pearl is inside some enemy's reach 0/1
//  aN aD aL aMaxL               ally heads in view, Manhattan to the nearest, its length, longest ally head in view
//  aDg aLg kD eDg               Manhattan to the nearest ally head anywhere and that ally's length; Manhattan to the
//                               team king's head (0 if we are it); to the nearest enemy head anywhere (not visible)
//  U TL TT king kRank EU EL     team units, longest, total; we are (co-)longest 0/1; team dragons longer than us;
//                               enemy units and longest (U is known to the bot; the rest are not)
//  ptlN ptlV                    portal edges around the head tile; any portal edge in view 0/1
//  act k c d1                   M move, P split, Q illegal split, X suicide action, N no action / time-out; steps;
//                               split child length; first step relative to facing F/L/R/B
//  eD1 eM1 pD1 aDg1             after the action: focus enemy path / Manhattan distance to our new head; path
//                               distance from our new head to the pearl (0 if eaten); Manhattan from our new head to
//                               the nearest ally head (as it stood at turn start)
//  endExp endExpA roomAct ate   new head inside shorter (A: any) enemy reach 0/1 (-1 not a surviving move); room of
//  ptlK                         the first step; pearls eaten this action; portal crossings in this action
//  fate hitT hitL ram           death on this action H/O/S/W or A (Ap sprint, Aq split, Ax suicide, At time-out,
//                               An none) ('' alive); team hit E/A; its length; head-on into an enemy 0/1
//  al1 al5 al10 L1 L5 L10       alive at its turn 1/5/10 rounds later (game over: alive at the end) and length then
//  eat5 eat10 eatS10            pearls eaten in rounds [r, r+5) / [r, r+10); of those, pearls dropped by own-team
//                               deaths
//  dr dwhy dbyL                 death round (-1 never); V rammed by a head (victim) or its own fate code; rammer's
//                               length (V only)
//  F10 Fu10 kill10              family at r+10: total length and living units of this dragon plus every descendant
//                               split off from round r on (robust to splits that move the body to a child); length
//                               of the enemy this dragon killed head-on in [r, r+10) (0 none)
//  feedS feedE feedK            rows with a death on this action: dropped pearls eaten within 20 rounds by own team /
//                               enemy / own team's longest dragon
//  cid cAl10 cL10               splits: child id, child alive 10 rounds later, its length then
//  w                            sampling weight
//  (extractor version 2 adds the columns below; readers must use the header, older files lack them)
//  sN sA sE                     sonar pings sent on this turn; of those, stopped on another ally dragon / an enemy one
//  rA rE                        pings delivered to this dragon since its previous turn (its inbox now): from allies /
//                               from enemies (a ray that returns to its sender is not counted)
//  pN3                          pearls in view within path distance 3
//  sp5 spD spD1                 in-view tiles where a pearl spawns in rounds r+1..r+5 (the bot sees each tile's
//                               countdown; replays show successful spawns only); path distance to the nearest
//                               reachable one; path distance from our new head to that tile after the action (99 none)
//  F30 Fu30 kill30              as F10 Fu10 kill10 at r+30
//  kc10                         enemy dragons that died on this dragon in [r, r+10): rammed head-on by it (its own
//                               death included) or ran into its body
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), cp = require('child_process');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

const ROOT = path.resolve(__dirname, '..');
const DATA = path.join(ROOT, 'data'), OUTROOT = path.join(DATA, 'decisions');
const TOP_TEAMS = [306, 70, 20, 801, 264, 46, 545]; // fixed online test opponents (research/OVERNIGHT-2026-09-29.md)
const SAMPLE = 8, ROOM_CAP = 64, DIST_CAP = 8, REACH_CAP = 6, FEED_WINDOW = 20, KING_KEEP_ROUND = 300, ROUNDS = 500;
const SPAWN_H = 5, MAX_JOBS = 4;
const XV = 2; // extractor version (1: 2026-09-30 first study; 2: sonar, spawn, pN3, 30-round outcomes, kills, game meta)
const DIRS = ['N', 'E', 'S', 'W'], DI = { N: 0, E: 1, S: 2, W: 3 }, DX = [0, 1, 0, -1], DY = [-1, 0, 1, 0];
const REL = ['F', 'R', 'B', 'L']; // (step - facing) mod 4
const COLS = ('r id tm L born init fac free nbE nbA room roomMax tFree tE eN eNs eNr eNrs eD0 eM0 eL eVis eKn eAft eFw ' +
  'eLmin safe1 exp1 safe1a exp1a safe2 oppN oppL oppD pN pD0 pEd pDang aN aD aL aMaxL aDg aLg kD eDg U TL TT king kRank EU EL ' +
  'ptlN ptlV act k c d1 eD1 eM1 pD1 aDg1 endExp endExpA roomAct ate ptlK fate hitT hitL ram al1 al5 al10 L1 L5 L10 eat5 eat10 eatS10 dr ' +
  'dwhy dbyL F10 Fu10 kill10 feedS feedE feedK cid cAl10 cL10 w ' +
  'sN sA sE rA rE pN3 sp5 spD spD1 F30 Fu30 kill30 kc10').split(' ');
const C = Object.fromEntries(COLS.map((k, i) => [k, i]));
const mix32 = x => { x ^= x >>> 16; x = Math.imul(x, 0x7feb352d); x ^= x >>> 15; x = Math.imul(x, 0x846ca68b); x ^= x >>> 16; return x >>> 0; };

// ---------------------------------------------------------------------------------------------------------------
// Map graph: nb[t*4+d] = tile across edge d of tile t (portals, wrap), -1 = kelp. Same rules as top_features.js.
function buildGeo(M) {
  const W = M.width, H = M.height, n = W * H;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
  const portal = new Map();
  for (const pr of M.portals || []) { if (pr.length !== 2) continue; const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); }
  const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
  const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
  function across(x, y, d) {
    let ek, kelp;
    if (d === 'N') { ek = x + ',' + y + ',N'; kelp = hk(x, y); }
    else if (d === 'S') { ek = x + ',' + wy(y + 1) + ',N'; kelp = hk(x, y + 1); }
    else if (d === 'W') { ek = x + ',' + y + ',W'; kelp = vk(x, y); }
    else { ek = wx(x + 1) + ',' + y + ',W'; kelp = vk(x + 1, y); }
    const p = portal.get(ek);
    if (p) {
      if (d === 'N') return { x: p.x, y: wy(p.y - 1) };
      if (d === 'S') return { x: p.x, y: p.y };
      if (d === 'W') return { x: wx(p.x - 1), y: p.y };
      return { x: p.x, y: p.y };
    }
    if (kelp) return null;
    return { x: wx(x + DX[DI[d]]), y: wy(y + DY[DI[d]]) };
  }
  const nb = new Int32Array(n * 4), ptl = new Uint8Array(n * 4);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) for (let d = 0; d < 4; d++) {
    const r = across(x, y, DIRS[d]);
    nb[(y * W + x) * 4 + d] = r ? r.y * W + r.x : -1;
    const ek = d === 0 ? x + ',' + y + ',N' : d === 2 ? x + ',' + wy(y + 1) + ',N' : d === 3 ? x + ',' + y + ',W' : wx(x + 1) + ',' + y + ',W';
    ptl[(y * W + x) * 4 + d] = portal.has(ek) ? 1 : 0;
  }
  const view = new Int32Array(n * 49); // the 7x7 window of every head tile
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    let i = 0;
    for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) view[(y * W + x) * 49 + i++] = wy(y + dy) * W + wx(x + dx);
  }
  const axd = (a, b, m) => { const d = Math.abs(a - b); return Math.min(d, m - d); };
  const man = (a, b) => axd(a % W, b % W, W) + axd((a / W) | 0, (b / W) | 0, H);
  const cheb = (a, b) => Math.max(axd(a % W, b % W, W), axd((a / W) | 0, (b / W) | 0, H));
  return { W, H, n, nb, ptl, view, man, cheb };
}

// ---------------------------------------------------------------------------------------------------------------
// One game. meta: {key, map, teamName:{A,B}, winner:'A'|'B'|null, ourSide:'A'|'B'|null}. Returns {rows, info}.
function extractGame(R, meta) {
  const M = R.match.map, G = buildGeo(M), { W, n, nb, ptl, view, man, cheb } = G;
  const occ = new Int32Array(n).fill(-1), pearl = new Uint8Array(n);
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearl[i] = 1;
  const drag = new Map();
  const newDragon = (id, team, body, born, init) => {
    const d = { id, team, body, born, init, lens: new Int16Array(ROUNDS + 1).fill(-1), eat: new Uint8Array(ROUNDS + 1), eatS: new Uint8Array(ROUNDS + 1),
      dr: -1, dwhy: '', dbyL: -1, finalLen: 0, feed: null, expect: [], act: null, tle: false, fate: null, splits: [], ramR: -1, ramL: 0,
      sN: 0, sA: 0, sE: 0, rA: 0, rE: 0, kills: [] };
    drag.set(id, d);
    for (const t of body) occ[t] = id;
    return d;
  };
  const tileOf = s => s.y * W + s.x;
  for (const d0 of M.initialDragons) newDragon(d0.id, d0.team, d0.body.map(tileOf), 0, 1);
  const init = { A: 0, B: 0 }; for (const d0 of M.initialDragons) init[d0.team] = (init[d0.team] || 0) + 1;
  const lastHT = new Map(); // id -> [head, tail] from the last dragonUpdate / split
  const chk = { sim: 0, turnHT: 0, body: 0, deaths: 0, splits: 0, eaten: 0, drops: 0, unknownTurn: 0, pingOrphan: 0 };
  const tc = { A: { turns: 0, pings: 0, pA: 0, pE: 0, splits: 0, none: 0 }, B: { turns: 0, pings: 0, pA: 0, pE: 0, splits: 0, none: 0 } };
  const timeline = [];
  const eatEvents = { A: 0, B: 0 }, eatSim = { A: 0, B: 0 };
  const dropOwner = new Map(); // tile -> {team, d (dead dragon record), round}
  let round = -1, cur = -1, drop = null, pend = null, turns = 0;
  const rows = [], dead = [];

  // successful pearl spawns (not death drops) per tile in round order; the bot sees the countdown of every tile in view
  const spawnAt = new Map(), spPtr = new Map();
  {
    let rnd = -1, inDrop = false;
    for (const e of R.events) {
      if (inDrop && !(e.type === 'tileChange' && e.hasPearl)) inDrop = false;
      if (e.type === 'roundStart') rnd = e.round;
      else if (e.type === 'dragonDeath') inDrop = true;
      else if (e.type === 'tileChange' && e.hasPearl && !inDrop && rnd >= 0) {
        const k = e.tile.y * W + e.tile.x; let a = spawnAt.get(k); if (!a) spawnAt.set(k, a = []); a.push(rnd);
      }
    }
  }
  const nextSpawn = t => { // first successful spawn round after the current round (1e9 none)
    const a = spawnAt.get(t); if (!a) return 1e9;
    let i = spPtr.get(t) || 0; while (i < a.length && a[i] <= round) i++;
    spPtr.set(t, i); return i < a.length ? a[i] : 1e9;
  };

  // --- BFS scratch ---
  const Q = new Int32Array(n);
  let stamp = 1; const seen = new Int32Array(n);
  const MAXE = 16;
  const eDist = [], eStamp = [];
  for (let i = 0; i < MAXE; i++) { eDist.push(new Int16Array(n)); eStamp.push(new Int32Array(n)); }
  const pDist = new Int16Array(n), pStamp = new Int32Array(n);
  const sDist = new Int16Array(n), sStamp = new Int32Array(n), soonStamp = new Int32Array(n);
  let turnStamp = 0;
  const isTail = (o, u) => { const od = drag.get(o); return od.body[od.body.length - 1] === u; };

  function flood(start, cap, countStart) { // free tiles reachable from start (start itself counted if countStart)
    stamp++; let qh = 0, qt = 0; Q[qt++] = start; seen[start] = stamp; let cnt = countStart ? 1 : 0;
    while (qh < qt && cnt < cap) {
      const t = Q[qh++];
      for (let k = 0; k < 4; k++) {
        const u = nb[t * 4 + k];
        if (u < 0 || seen[u] === stamp || occ[u] >= 0) continue;
        seen[u] = stamp; Q[qt++] = u; if (++cnt >= cap) break;
      }
    }
    return cnt;
  }
  // enemy BFS from head e (slot i): bodies block except tails; target = our head (not expanded)
  function enemyBfs(i, src, ourHead) {
    const dist = eDist[i], st = eStamp[i];
    let qh = 0, qt = 0; Q[qt++] = src; st[src] = turnStamp; dist[src] = 0;
    while (qh < qt) {
      const t = Q[qh++], dd = dist[t];
      if (dd >= DIST_CAP || (t === ourHead && dd > 0)) continue;
      for (let k = 0; k < 4; k++) {
        const u = nb[t * 4 + k];
        if (u < 0 || st[u] === turnStamp) continue;
        const o = occ[u];
        if (o >= 0 && u !== ourHead && !isTail(o, u)) continue;
        st[u] = turnStamp; dist[u] = dd + 1; Q[qt++] = u;
      }
    }
  }
  const eD = (i, t) => (t >= 0 && eStamp[i][t] === turnStamp) ? eDist[i][t] : 99;
  // distances from a tile over free tiles (our new head tile is free before the move): pearls and spawn tiles
  function tileBfs(src, dist, st) {
    let qh = 0, qt = 0; Q[qt++] = src; st[src] = turnStamp; dist[src] = 0;
    while (qh < qt) {
      const t = Q[qh++], dd = dist[t];
      if (dd >= DIST_CAP) continue;
      for (let k = 0; k < 4; k++) {
        const u = nb[t * 4 + k];
        if (u < 0 || st[u] === turnStamp || occ[u] >= 0) continue;
        st[u] = turnStamp; dist[u] = dd + 1; Q[qt++] = u;
      }
    }
  }
  const pD = t => (t >= 0 && pStamp[t] === turnStamp) ? pDist[t] : 99;
  const sD = t => (t >= 0 && sStamp[t] === turnStamp) ? sDist[t] : 99;

  // --- state at turn start ---
  let ctx = null; // per-turn scratch used again when the pending row is finalised (before any other BFS runs)
  function beginTurn(d) {
    turnStamp++;
    const row = new Array(COLS.length).fill(-1);
    const h = d.body[0], L = d.body.length, tm = d.team, V = h * 49;
    row[C.r] = round; row[C.id] = d.id; row[C.tm] = tm; row[C.L] = L; row[C.born] = d.born; row[C.init] = d.init;
    row[C.rA] = d.rA; row[C.rE] = d.rE; d.rA = 0; d.rE = 0; // the sonar inbox is read and emptied at turn start
    let fac = -1;
    if (L >= 2) for (let k = 0; k < 4; k++) if (nb[d.body[1] * 4 + k] === h) { fac = k; break; }
    row[C.fac] = fac >= 0 ? DIRS[fac] : '?';
    // neighbours
    let free = 0, nbE = 0, nbA = 0; const stepT = [-1, -1, -1, -1], stepFree = [0, 0, 0, 0], stepRoom = [0, 0, 0, 0];
    for (let k = 0; k < 4; k++) {
      const u = nb[h * 4 + k]; stepT[k] = u;
      if (u < 0) continue;
      const o = occ[u];
      if (o < 0) { free++; stepFree[k] = 1; continue; }
      if (o !== d.id) { const od = drag.get(o); if (od.body[0] === u) { if (od.team === tm) nbA++; else nbE++; } }
    }
    row[C.free] = free; row[C.nbE] = nbE; row[C.nbA] = nbA;
    row[C.ptlN] = ptl[h * 4] + ptl[h * 4 + 1] + ptl[h * 4 + 2] + ptl[h * 4 + 3];
    let pv = 0; for (let i = 0; i < 49 && !pv; i++) { const t = view[V + i]; if (ptl[t * 4] | ptl[t * 4 + 1] | ptl[t * 4 + 2] | ptl[t * 4 + 3]) pv = 1; }
    row[C.ptlV] = pv;
    row[C.room] = flood(h, ROOM_CAP, false);
    let roomMax = 0;
    for (let k = 0; k < 4; k++) if (stepFree[k]) { stepRoom[k] = flood(stepT[k], ROOM_CAP, true); roomMax = Math.max(roomMax, stepRoom[k]); }
    row[C.roomMax] = roomMax;
    // tail surroundings (a split child's head is our tail)
    const tail = d.body[L - 1], neck2 = L >= 2 ? d.body[L - 2] : -1;
    let tFree = 0;
    for (let k = 0; k < 4; k++) { const u = nb[tail * 4 + k]; if (u >= 0 && u !== neck2 && occ[u] < 0) tFree++; }
    row[C.tFree] = tFree;
    // view scan: heads, pearls and tiles about to spawn
    const enemies = [], allies = []; let pN = 0, sp5 = 0;
    for (let i = 0; i < 49; i++) {
      const t = view[V + i];
      if (pearl[t]) pN++;
      if (soonStamp[t] !== turnStamp && nextSpawn(t) <= round + SPAWN_H) { soonStamp[t] = turnStamp; sp5++; }
      const o = occ[t];
      if (o < 0 || o === d.id) continue;
      const od = drag.get(o);
      if (od.body[0] !== t) continue;
      if (od.team === tm) allies.push(od); else enemies.push(od);
    }
    if (enemies.length > MAXE) enemies.sort((a, b) => man(a.body[0], h) - man(b.body[0], h));
    row[C.pN] = pN; row[C.sp5] = sp5;
    // enemy BFS (reach sets)
    const ne = Math.min(enemies.length, MAXE);
    let eNs = 0, eNr = 0, eNrs = 0, eLmin = 99, tE = 99;
    const reach = [], shorter = [];
    for (let i = 0; i < ne; i++) {
      const e = enemies[i], Le = e.body.length;
      enemyBfs(i, e.body[0], h);
      reach.push(Math.min(Le - 1, REACH_CAP)); shorter.push(Le < L);
      if (Le < L) eNs++;
      const dh = eD(i, h);
      if (dh <= reach[i]) { eNr++; if (Le < L) eNrs++; }
      eLmin = Math.min(eLmin, Le);
      tE = Math.min(tE, man(tail, e.body[0]));
    }
    row[C.eN] = enemies.length; row[C.eNs] = eNs; row[C.eNr] = eNr; row[C.eNrs] = eNrs; row[C.eLmin] = eLmin; row[C.tE] = tE;
    const inReach = (t, onlyShorter) => { for (let i = 0; i < ne; i++) if ((!onlyShorter || shorter[i]) && eD(i, t) <= reach[i]) return true; return false; };
    // focus enemy
    let fi = -1;
    for (let i = 0; i < ne; i++) {
      if (fi < 0) { fi = i; continue; }
      const a = eD(i, h), b = eD(fi, h);
      if (a < b || (a === b && (a === 99 ? man(enemies[i].body[0], h) < man(enemies[fi].body[0], h) : enemies[i].body.length < enemies[fi].body.length))) fi = i;
    }
    if (fi >= 0) {
      const e = enemies[fi], eh = e.body[0];
      row[C.eD0] = eD(fi, h); row[C.eM0] = man(eh, h); row[C.eL] = e.body.length;
      let vis = 0; for (const t of e.body) if (cheb(t, h) <= 3) vis++;
      row[C.eVis] = vis; row[C.eKn] = vis === e.body.length ? 1 : 0; row[C.eAft] = e.id > d.id ? 1 : 0;
      let efac = -1; if (e.body.length >= 2) for (let k = 0; k < 4; k++) if (nb[e.body[1] * 4 + k] === eh) { efac = k; break; }
      const fwd = efac >= 0 ? nb[eh * 4 + efac] : -1;
      row[C.eFw] = fwd >= 0 && man(fwd, h) < man(eh, h) ? 1 : 0;
    } else { row[C.eD0] = 99; row[C.eM0] = 99; row[C.eL] = 99; }
    // single steps and escape sprints
    let safe1 = 0, exp1 = 0, safe1a = 0, exp1a = 0;
    for (let k = 0; k < 4; k++) if (stepFree[k]) {
      if (inReach(stepT[k], true)) exp1++; else safe1++;
      if (inReach(stepT[k], false)) exp1a++; else safe1a++;
    }
    row[C.safe1] = safe1; row[C.exp1] = exp1; row[C.safe1a] = safe1a; row[C.exp1a] = exp1a;
    if (eNs > 0 && L >= 3) {
      const ends = new Set();
      for (let k1 = 0; k1 < 4; k1++) {
        if (!stepFree[k1]) continue; const u1 = stepT[k1];
        for (let k2 = 0; k2 < 4; k2++) {
          const u2 = nb[u1 * 4 + k2];
          if (u2 < 0 || u2 === h || occ[u2] >= 0) continue;
          if (!inReach(u2, true)) ends.add(u2);
          if (L < 4) continue;
          for (let k3 = 0; k3 < 4; k3++) {
            const u3 = nb[u2 * 4 + k3];
            if (u3 < 0 || u3 === h || u3 === u1 || occ[u3] >= 0) continue;
            if (!inReach(u3, true)) ends.add(u3);
          }
        }
      }
      row[C.safe2] = ends.size;
    } else row[C.safe2] = -1;
    // our BFS: nearest pearl in view, pearls within 3, nearest tile about to spawn, ram opportunities
    stamp++; let qh = 0, qt = 0; Q[qt++] = h; seen[h] = stamp;
    const ourD = new Map(); ourD.set(h, 0);
    let pTile = -1, pD0 = 99, oppN = 0, oppL = -1, oppD = -1, pN3 = 0, spTile = -1, spD = 99;
    const ramReach = Math.min(L - 1, REACH_CAP);
    const enemyHeadSet = new Map(); for (const e of enemies) enemyHeadSet.set(e.body[0], e);
    while (qh < qt) {
      const t = Q[qh++], dd = ourD.get(t);
      if (dd >= DIST_CAP) continue;
      for (let k = 0; k < 4; k++) {
        const u = nb[t * 4 + k];
        if (u < 0 || seen[u] === stamp) continue;
        seen[u] = stamp;
        const o = occ[u];
        if (o >= 0) {
          const e = enemyHeadSet.get(u);
          if (e && dd + 1 <= ramReach) { oppN++; if (e.body.length > oppL) { oppL = e.body.length; oppD = dd + 1; } }
          continue;
        }
        ourD.set(u, dd + 1); Q[qt++] = u;
        if (pearl[u] && cheb(u, h) <= 3) { if (pTile < 0) { pTile = u; pD0 = dd + 1; } if (dd + 1 <= 3) pN3++; }
        if (spTile < 0 && soonStamp[u] === turnStamp) { spTile = u; spD = dd + 1; }
      }
    }
    row[C.oppN] = oppN; row[C.oppL] = oppL; row[C.oppD] = oppD; row[C.pD0] = pD0; row[C.pN3] = pN3; row[C.spD] = spD;
    if (pTile >= 0) {
      let pEd = 99, dang = 0;
      for (let i = 0; i < ne; i++) { const x = eD(i, pTile); if (x < pEd) pEd = x; if (x <= reach[i]) dang = 1; }
      row[C.pEd] = pEd; row[C.pDang] = dang;
      tileBfs(pTile, pDist, pStamp);
    } else { row[C.pEd] = 99; row[C.pDang] = 0; }
    if (spTile >= 0) tileBfs(spTile, sDist, sStamp);
    // allies
    row[C.aN] = allies.length;
    if (allies.length) {
      let best = null, bd = 1e9, mx = 0;
      for (const a of allies) { const x = man(a.body[0], h); if (x < bd) { bd = x; best = a; } mx = Math.max(mx, a.body.length); }
      row[C.aD] = bd; row[C.aL] = best.body.length; row[C.aMaxL] = mx;
    } else { row[C.aD] = 99; row[C.aL] = -1; row[C.aMaxL] = -1; }
    // team and enemy team (global)
    let U = 0, TL = 0, TT = 0, EU = 0, EL = 0, kRank = 0, aDg = 99, aLg = -1, eDg = 99, king = null, aTile = -1;
    for (const o of drag.values()) {
      const lo = o.body.length;
      if (o.team === tm) {
        U++; TT += lo; if (lo > L) kRank++;
        if (!king || lo > king.body.length || (lo === king.body.length && o.id < king.id)) king = o;
        if (o !== d) { const x = man(o.body[0], h); if (x < aDg) { aDg = x; aLg = lo; aTile = o.body[0]; } }
      } else { EU++; if (lo > EL) EL = lo; eDg = Math.min(eDg, man(o.body[0], h)); }
    }
    TL = king.body.length;
    row[C.aDg] = aDg; row[C.aLg] = aLg; row[C.eDg] = eDg; row[C.kD] = king === d ? 0 : man(king.body[0], h);
    row[C.U] = U; row[C.TL] = TL; row[C.TT] = TT; row[C.king] = L === TL ? 1 : 0; row[C.kRank] = kRank; row[C.EU] = EU; row[C.EL] = EL;
    ctx = { d, row, h, L, fac, stepT, stepRoom, fi, fHead: fi >= 0 ? enemies[fi].body[0] : -1, pTile, spTile, inReach, aTile };
    d.lens[round] = L;
    return row;
  }

  function finishTurn() {
    if (!pend) return;
    const { d, row } = pend, c = ctx;
    pend = null;
    if (!c || c.d !== d || c.row !== row) return; // should not happen
    const a = d.act;
    let act = 'N';
    if (a === 'move') act = 'M'; else if (a === 'split') act = d.splitOk ? 'P' : 'Q'; else if (a === 'suicide') act = 'X';
    if (d.tle && act !== 'M' && act !== 'P') act = 'N';
    if (act === 'N') tc[d.team].none++;
    row[C.act] = act; row[C.k] = act === 'M' ? d.steps.length : 0; row[C.c] = d.childLen || 0;
    row[C.d1] = act === 'M' && c.fac >= 0 ? REL[(DI[d.steps[0]] - c.fac + 4) & 3] : '-';
    const f = d.fate;
    row[C.fate] = f ? (f.reason === 'A' ? 'A' + (f.why || 'n')[0] : f.reason) : '';
    row[C.hitT] = f && f.hitTeam ? (f.hitTeam === d.team ? 'A' : 'E') : '-';
    row[C.hitL] = f && f.hitLen ? f.hitLen : -1;
    row[C.ram] = f && f.reason === 'H' && f.hitTeam !== d.team ? 1 : 0;
    row[C.ate] = d.ateNow || 0;
    row[C.sN] = d.sN; row[C.sA] = d.sA; row[C.sE] = d.sE;
    if (act === 'M') {
      const tf = d.endTile;
      row[C.roomAct] = c.stepRoom[DI[d.steps[0]]] || 0;
      if (c.fi >= 0) { row[C.eD1] = eD(c.fi, tf); row[C.eM1] = man(c.fHead, tf); }
      else { row[C.eD1] = 99; row[C.eM1] = 99; }
      row[C.pD1] = c.pTile >= 0 ? (d.ateTiles && d.ateTiles.includes(c.pTile) ? 0 : pD(tf)) : 99;
      row[C.spD1] = c.spTile >= 0 ? (tf === c.spTile ? 0 : sD(tf)) : 99;
      row[C.aDg1] = c.aTile >= 0 ? man(c.aTile, tf) : 99;
      row[C.ptlK] = d.ptlK || 0;
      if (!f) { row[C.endExp] = c.inReach(tf, true) ? 1 : 0; row[C.endExpA] = c.inReach(tf, false) ? 1 : 0; }
    } else {
      row[C.eD1] = row[C.eD0]; row[C.eM1] = row[C.eM0]; row[C.pD1] = row[C.pD0]; row[C.aDg1] = row[C.aDg]; row[C.ptlK] = 0; row[C.spD1] = row[C.spD];
    }
    row[C.cid] = d.childId !== undefined ? d.childId : -1;
    // keep rule
    let keep = row[C.eN] > 0 || act !== 'M' || row[C.k] >= 2 || f || row[C.free] <= 1 || (row[C.king] === 1 && round >= KING_KEEP_ROUND) ||
      (meta.ourSide && d.team === meta.ourSide);
    row[C.w] = 1;
    if (!keep && mix32((meta.seedHash ^ Math.imul(d.id, 7919) ^ Math.imul(round, 131)) >>> 0) % SAMPLE === 0) { keep = true; row[C.w] = SAMPLE; }
    if (keep) rows.push(row);
  }

  const closeDrop = () => { if (drop) { if (drop.got !== drop.want) chk.drops++; drop = null; } };
  const kingOf = tm => { let best = null; for (const o of drag.values()) if (o.team === tm && (!best || o.body.length > best.body.length)) best = o; return best; };
  const snapshot = r => {
    const s = { r };
    for (const tm of ['A', 'B']) { let u = 0, tot = 0, lg = 0; for (const o of drag.values()) if (o.team === tm) { u++; tot += o.body.length; lg = Math.max(lg, o.body.length); } s[tm] = [u, tot, lg]; }
    timeline.push(s);
  };

  for (const e of R.events) {
    if (drop && !(e.type === 'tileChange' && e.hasPearl)) closeDrop();
    switch (e.type) {
      case 'roundStart':
        finishTurn();
        round = e.round;
        if (round % 10 === 0) snapshot(round);
        break;
      case 'turnStart': {
        finishTurn();
        cur = e.id;
        const d = drag.get(cur);
        if (!d) { chk.unknownTurn++; break; }
        if (round < 0) break;
        turns++; tc[d.team].turns++;
        // the state this dragon sees must match the replay's own head/tail for it, and be a connected chain
        const ht = lastHT.get(d.id);
        if (ht && (ht[0] !== d.body[0] || ht[1] !== d.body[d.body.length - 1])) chk.turnHT++;
        let ok = true;
        for (let i = 0; i < d.body.length; i++) {
          if (occ[d.body[i]] !== d.id) ok = false;
          if (i > 0) { let adj = false; for (let k = 0; k < 4; k++) if (nb[d.body[i] * 4 + k] === d.body[i - 1]) adj = true; if (!adj) ok = false; }
        }
        if (!ok) chk.body++;
        d.fate = null; d.expect = []; d.act = null; d.tle = false; d.steps = null; d.childLen = 0; d.splitOk = false; d.childId = undefined;
        d.ateNow = 0; d.ateTiles = null; d.endTile = d.body[0]; d.ptlK = 0; d.sN = 0; d.sA = 0; d.sE = 0;
        pend = { d, row: beginTurn(d) };
        break;
      }
      case 'tileChange': {
        const k = e.tile.y * W + e.tile.x;
        if (e.hasPearl) {
          pearl[k] = 1;
          if (drop) { drop.got++; dropOwner.set(k, { team: drop.team, rec: drop.rec, round }); } else dropOwner.delete(k);
        } else {
          pearl[k] = 0;
          const d = drag.get(cur);
          if (d && round >= 0) eatEvents[d.team]++;
        }
        break;
      }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action;
        d.act = a ? a.kind : null; d.tle = !!e.tle;
        if (a && a.kind === 'split') d.childLen = a.childSegmentCount;
        if (!a || a.kind !== 'move') break;
        d.steps = a.steps;
        for (const t of d.body) if (occ[t] === d.id) occ[t] = -1;
        const body = d.body.slice();
        let fate = null;
        for (let i = 0; i < a.steps.length; i++) {
          if (i > 0 && body.length <= 2) { fate = { reason: 'A', why: 'p' }; break; }
          const nx = nb[body[0] * 4 + DI[a.steps[i]]];
          if (nx < 0) { fate = { reason: 'W' }; break; }
          if (ptl[body[0] * 4 + DI[a.steps[i]]]) d.ptlK++;
          if (body.includes(nx)) { fate = { reason: 'S' }; break; }
          const o = occ[nx];
          if (o >= 0) {
            const od = drag.get(o), isHead = od.body[0] === nx;
            fate = { reason: isHead ? 'H' : 'O', hit: o, hitTeam: od.team, hitLen: od.body.length };
            break;
          }
          body.unshift(nx);
          if (pearl[nx]) {
            pearl[nx] = 0; eatSim[d.team]++; d.ateNow++; (d.ateTiles || (d.ateTiles = [])).push(nx);
            if (round >= 0 && round < ROUNDS) d.eat[round]++;
            const own = dropOwner.get(nx);
            if (own) {
              dropOwner.delete(nx);
              if (round - own.round <= FEED_WINDOW && own.rec.feed) {
                if (own.team === d.team) {
                  own.rec.feed.S++;
                  if (round >= 0 && round < ROUNDS) d.eatS[round]++;
                  const kg = kingOf(d.team);
                  if (kg && (kg === d || kg.body.length <= body.length)) own.rec.feed.K++;
                } else own.rec.feed.E++;
              }
            }
          } else body.pop();
          if (i > 0) body.pop();
          d.expect.push([body[0], body[body.length - 1]]);
        }
        d.fate = fate; d.body = body; d.endTile = body[0];
        for (const t of body) occ[t] = d.id;
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id);
        const hh = e.head.y * W + e.head.x, tt = e.tail.y * W + e.tail.x;
        lastHT.set(e.id, [hh, tt]);
        if (!d || round < 0) break;
        const x = d.expect.length ? d.expect.shift() : [d.body[0], d.body[d.body.length - 1]];
        if (x[0] !== hh || x[1] !== tt) {
          chk.sim++;
          for (const t of d.body) if (occ[t] === d.id) occ[t] = -1;
          const b = d.body.slice();
          if (b[0] !== hh) b.unshift(hh);
          while (b.length > 1 && b[b.length - 1] !== tt) b.pop();
          d.body = b; d.expect = [];
          for (const t of b) occ[t] = d.id;
        }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        if (p.body.length !== e.parentBody.length + e.childBody.length) chk.splits++;
        for (const t of p.body) if (occ[t] === p.id) occ[t] = -1;
        p.body = e.parentBody.map(tileOf);
        for (const t of p.body) occ[t] = p.id;
        p.splitOk = true; p.childId = e.childId; p.splits.push([round, e.childId]);
        if (round >= 0) tc[p.team].splits++;
        const c = newDragon(e.childId, e.team, e.childBody.map(tileOf), round, 0);
        lastHT.set(p.id, [p.body[0], p.body[p.body.length - 1]]);
        lastHT.set(c.id, [c.body[0], c.body[c.body.length - 1]]);
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        const len = d.body.length, mover = cur === d.id;
        d.dr = round; d.finalLen = 0;
        d.feed = { S: 0, E: 0, K: 0 };
        if (mover) {
          const f = d.fate;
          if (e.reason === 'A') {
            const why = d.tle ? 't' : f ? f.why : d.act === 'split' ? 'q' : d.act === 'suicide' ? 'x' : 'n';
            if (!f) d.fate = { reason: 'A', why };
            else if (f.reason !== 'A') chk.deaths++;
          } else if (!f || f.reason !== e.reason) chk.deaths++;
          if (f && f.reason === 'H' && f.hitTeam !== d.team) { d.ramR = round; d.ramL = f.hitLen; }
          // an enemy that ran into this dragon's body: the body's owner is credited with the kill
          if (f && f.reason === 'O' && f.hitTeam !== d.team) { const o = drag.get(f.hit); if (o) o.kills.push(round); }
          const ff = d.fate || { reason: e.reason, why: 'n' };
          d.dwhy = ff.reason === 'A' ? 'A' + ff.why : ff.reason;
        } else {
          const m = drag.get(cur);
          d.dwhy = 'V'; d.dbyL = m ? m.body.length : -1;
          if (e.reason !== 'H' || !m || !m.fate || m.fate.hit !== d.id) chk.deaths++;
          if (m && m.team !== d.team) m.kills.push(round); // rammed head-on by the mover
        }
        for (const t of d.body) if (occ[t] === d.id) occ[t] = -1;
        drag.delete(e.id);
        dead.push(d);
        drop = { want: Math.ceil(len / 2), got: 0, team: d.team, rec: d };
        break;
      }
      case 'sonarPing': {
        // cast after the sender's action, before the next turn: it belongs to the pending turn
        const s = drag.get(e.senderId);
        if (!s) { chk.pingOrphan++; break; }
        if (!pend || pend.d !== s) chk.pingOrphan++; else s.sN++;
        tc[s.team].pings++;
        if (e.hitId !== undefined && e.hitId !== e.senderId) {
          const hd = drag.get(e.hitId);
          if (hd) {
            if (hd.team === s.team) { s.sA++; hd.rA++; tc[s.team].pA++; } else { s.sE++; hd.rE++; tc[s.team].pE++; }
          }
        }
        break;
      }
    }
  }
  finishTurn();
  closeDrop();
  const rounds = round + 1;
  for (let r = (timeline.length ? timeline[timeline.length - 1].r : -10) + 10; r <= ROUNDS; r += 10) snapshot(r);
  for (const tm of ['A', 'B']) chk.eaten += Math.abs(eatSim[tm] - eatEvents[tm]);
  const res = R.result;
  const finalMatch = ['A', 'B'].every(tm => {
    const s = timeline[timeline.length - 1][tm], x = res['team' + tm];
    return s[0] === x.dragonCount && s[1] === x.totalLength && s[2] === x.longestDragon;
  });
  for (const d of drag.values()) d.finalLen = d.body.length;

  // --- outcomes ---
  const byId = new Map(); for (const d of dead) byId.set(d.id, d); for (const d of drag.values()) byId.set(d.id, d);
  const aliveAt = (d, R2) => R2 < rounds ? (d.lens[R2] >= 0 ? 1 : 0) : (d.dr < 0 ? 1 : 0);
  const lenAt = (d, R2) => R2 < rounds ? Math.max(d.lens[R2], 0) : (d.dr < 0 ? d.finalLen : 0);
  function fam(d, R2, r0) { // length and living units at R2 of d plus descendants split off in [r0, R2)
    let len = lenAt(d, R2), u = aliveAt(d, R2) && lenAt(d, R2) > 0 ? 1 : 0;
    for (const [s, cid] of d.splits) if (s >= r0 && s < R2) { const c = byId.get(cid); if (c) { const x = fam(c, R2, s); len += x.len; u += x.u; } }
    return { len, u };
  }
  for (const row of rows) {
    const d = byId.get(row[C.id]), r = row[C.r];
    const f10 = fam(d, r + 10, r);
    row[C.F10] = f10.len; row[C.Fu10] = f10.u;
    row[C.kill10] = d.ramR >= r && d.ramR < r + 10 ? d.ramL : 0;
    const f30 = fam(d, r + 30, r);
    row[C.F30] = f30.len; row[C.Fu30] = f30.u;
    row[C.kill30] = d.ramR >= r && d.ramR < r + 30 ? d.ramL : 0;
    let kc = 0; for (const x of d.kills) if (x >= r && x < r + 10) kc++;
    row[C.kc10] = kc;
    row[C.al1] = aliveAt(d, r + 1); row[C.al5] = aliveAt(d, r + 5); row[C.al10] = aliveAt(d, r + 10);
    row[C.L1] = lenAt(d, r + 1); row[C.L5] = lenAt(d, r + 5); row[C.L10] = lenAt(d, r + 10);
    let e5 = 0, e10 = 0, s10 = 0;
    for (let q = r; q < Math.min(r + 10, ROUNDS); q++) { e10 += d.eat[q]; s10 += d.eatS[q]; if (q < r + 5) e5 += d.eat[q]; }
    row[C.eat5] = e5; row[C.eat10] = e10; row[C.eatS10] = s10;
    row[C.dr] = d.dr; row[C.dwhy] = d.dr >= 0 ? d.dwhy : '-'; row[C.dbyL] = d.dbyL;
    if (row[C.fate] !== '' && d.feed) { row[C.feedS] = d.feed.S; row[C.feedE] = d.feed.E; row[C.feedK] = d.feed.K; }
    if (row[C.cid] >= 0) { const cd = byId.get(row[C.cid]); if (cd) { row[C.cAl10] = aliveAt(cd, r + 10); row[C.cL10] = lenAt(cd, r + 10); } }
  }
  const info = {
    rounds, endReason: res.endReason, resultWinner: res.winner, turns, rows: rows.length,
    final: { A: [res.teamA.dragonCount, res.teamA.longestDragon, res.teamA.totalLength], B: [res.teamB.dragonCount, res.teamB.longestDragon, res.teamB.totalLength] },
    checks: { ...chk, finalMatch },
    initDragons: M.initialDragons.length, init,
    tl: { A: timeline.flatMap(s => s.A), B: timeline.flatMap(s => s.B) },
    tc,
  };
  return { rows, info, timeline };
}

// ---------------------------------------------------------------------------------------------------------------
// Game lists
function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  const out = [];
  for (const l of fs.readFileSync(file, 'utf8').split('\n')) { if (!l.trim()) continue; try { out.push(JSON.parse(l)); } catch { /* partial line */ } }
  return out;
}
// keysFile: a snapshot key file, or 'all' = every row of data/top/index.jsonl as it stands now (games whose replay is
// missing are skipped). The list has .indexRows (rows read) and .missing.
function topGames(keysFile) {
  const all = keysFile === 'all';
  const want = all ? null : new Set(fs.readFileSync(keysFile, 'utf8').split('\n').map(s => s.trim()).filter(Boolean));
  const seen = new Set(), out = [];
  const index = readJsonl(path.join(DATA, 'top', 'index.jsonl'));
  let missing = 0;
  for (const row of index) {
    const k = row.battleId + ':' + row.gameId;
    if ((want && !want.has(k)) || seen.has(k)) continue;
    seen.add(k);
    const file = path.join(DATA, 'top', String(row.battleId), row.gameId + '.replay.gz');
    if (all && !fs.existsSync(file)) { missing++; continue; }
    out.push({
      key: k, file, out: row.battleId + '_' + row.gameId,
      map: row.map, teamName: { A: row.teamA, B: row.teamB }, elo: { A: row.eloA, B: row.eloB },
      winner: row.winner ? String(row.winner).toUpperCase() : null, ourSide: null, ranked: row.ranked, at: row.at,
    });
  }
  out.indexRows = index.length; out.missing = missing;
  return out;
}
function onlineSets() {
  const dir = path.join(DATA, 'online'), out = [];
  for (const s of fs.readdirSync(dir)) {
    const f = path.join(dir, s, 'index.json');
    if (!fs.existsSync(f)) continue;
    let x; try { x = JSON.parse(fs.readFileSync(f, 'utf8')); } catch { continue; }
    const g = (x.games || []).filter(q => q.replay && q.ourSide);
    if (!g.length) continue;
    const top = g.filter(q => TOP_TEAMS.includes(+q.opponentTeam)).length;
    if (top >= g.length / 2) out.push(s);
  }
  return out.sort();
}
function onlineGames(set) {
  const dir = path.join(DATA, 'online', set), x = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8')), out = [];
  for (const q of x.games || []) {
    if (!q.replay || !q.ourSide) continue;
    const file = path.join(dir, 'M' + q.gameId + '.replay');
    if (!fs.existsSync(file)) continue;
    let gj = {}; try { gj = JSON.parse(fs.readFileSync(path.join(dir, 'game-' + q.gameId + '.json'), 'utf8')); } catch { /* optional */ }
    out.push({
      key: String(q.gameId), file, out: String(q.gameId), map: q.mapName, teamName: { A: gj.teamAName || null, B: gj.teamBName || null },
      elo: { A: gj.teamAElo || null, B: gj.teamBElo || null }, winner: q.winner ? String(q.winner).toUpperCase() : null,
      ourSide: q.ourSide, opponentTeam: q.opponentTeam, ourSubmission: q.ourSubmission, ourWin: q.ourWin, ranked: q.ranked, at: q.completedAt,
    });
  }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------
// Worker: parse, extract, write the game's gz file (atomically), return its games.jsonl line.
function processGame(load, task) {
  const R = load(task.g.file);
  const meta = { ...task.g, seedHash: mix32(parseInt(String(task.g.key).replace(/\D/g, '').slice(-9), 10) || 1) };
  const { rows, info } = extractGame(R, meta);
  const lines = [COLS.join('\t')];
  for (const r of rows) lines.push(r.join('\t'));
  fs.writeFileSync(task.outFile + '.tmp', zlib.gzipSync(lines.join('\n') + '\n', { level: 6 }));
  fs.renameSync(task.outFile + '.tmp', task.outFile);
  const g = task.g;
  return {
    key: g.key, out: path.basename(task.outFile), map: g.map, teamName: g.teamName, elo: g.elo, winner: g.winner, ourSide: g.ourSide,
    opponentTeam: g.opponentTeam, ourSubmission: g.ourSubmission, ourWin: g.ourWin, ranked: g.ranked, at: g.at,
    width: R.match.map.width, height: R.match.map.height, xv: XV, ...info,
  };
}
// Replay loader for worker threads. Same code as makeLoader() in tools/top_features.js: requiring that module inside
// a worker thread would also install its own worker message handler, so the few lines are repeated here.
function makeLoader(src) {
  const vm = require('vm');
  const cut = src.indexOf('var Af=B(');
  if (cut < 0) throw Error('unexpected replay-viewer build (parser cut point not found)');
  const code = src.slice(0, cut).replace('if(n.formatVersion>1)', 'if(n.formatVersion>2)') + 'globalThis.__tf={Df:Df,bf:bf,Of:Of,cu:$};})();';
  const ctx = { TextEncoder, TextDecoder };
  vm.runInNewContext(code, ctx, { timeout: 5000 });
  const { Df, bf, Of } = ctx.__tf || {};
  if (![Df, bf, Of].every(f => typeof f === 'function')) throw Error('unexpected replay-viewer build (parser internals not found)');
  return function load(file) {
    const raw = fs.readFileSync(file);
    const root = Df(file.endsWith('.gz') ? zlib.gunzipSync(raw) : raw);
    const list = root.events, n = list.length, events = new Array(n);
    for (let i = 0; i < n; i++) events[i] = bf(list.get(i)); // sonar values are not needed here (sender, hit and landing are)
    const R = Of(root, events);
    R.formatVersion = root.formatVersion;
    return R;
  };
}
if (!isMainThread) {
  const load = makeLoader(workerData.src);
  parentPort.on('message', task => {
    const t0 = Date.now();
    try { parentPort.postMessage({ key: task.g.key, line: processGame(load, task), ms: Date.now() - t0 }); }
    catch (err) { parentPort.postMessage({ key: task.g.key, error: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | '), ms: Date.now() - t0 }); }
  });
}

// A set is written by one process at a time: data/decisions/<set>/.lock holds the writer's pid.
function takeLock(file) {
  try { fs.writeFileSync(file, String(process.pid), { flag: 'wx' }); return true; }
  catch (e) {
    if (e.code !== 'EEXIST') throw e;
    const pid = parseInt(fs.readFileSync(file, 'utf8'), 10);
    let alive = false;
    if (pid > 0 && pid !== process.pid) { try { process.kill(pid, 0); alive = true; } catch (err) { alive = err.code === 'EPERM'; } }
    if (alive) return false;
    fs.writeFileSync(file, String(process.pid)); return true; // stale lock of a dead process
  }
}
async function runSet(setName, games, opt) {
  const dir = path.join(OUTROOT, setName);
  fs.mkdirSync(dir, { recursive: true });
  const lock = path.join(dir, '.lock');
  if (!takeLock(lock)) { console.error(`${setName}: another process is writing this set (${path.relative(ROOT, lock)}); skipped`); process.exitCode = 1; return; }
  try { await runSetLocked(setName, dir, games, opt); } finally { fs.rmSync(lock, { force: true }); }
}
async function runSetLocked(setName, dir, games, opt) {
  const idxFile = path.join(dir, 'games.jsonl');
  const done = new Map(readJsonl(idxFile).map(x => [x.key, x]));
  const stale = x => (x.xv || 1) < XV; // extracted by an older extractor version: redo (adds the new columns)
  const todo = games.filter(g => opt.force || !done.has(g.key) || stale(done.get(g.key)) || !fs.existsSync(path.join(dir, done.get(g.key).out))).slice(0, opt.limit);
  console.log(`${setName}: ${games.length} games, done ${done.size}, to process ${todo.length}`);
  if (!todo.length) return;
  const src = require('./top_features.js').viewerSource();
  const queue = todo.slice(), t0 = Date.now(), results = new Map(done);
  let n = 0; const errors = [];
  // games.jsonl in the order of the game list (written every FLUSH games and at the end, atomically)
  const FLUSH = 200;
  const writeIndex = () => {
    const order = games.map(g => g.key).filter(k => results.has(k));
    fs.writeFileSync(idxFile + '.tmp', order.map(k => JSON.stringify(results.get(k))).join('\n') + '\n');
    fs.renameSync(idxFile + '.tmp', idxFile);
    return order;
  };
  await new Promise((resolve, reject) => {
    const nw = Math.min(opt.jobs, queue.length); let live = nw;
    for (let i = 0; i < nw; i++) {
      const w = new Worker(__filename, { workerData: { src }, resourceLimits: { maxOldGenerationSizeMb: 3072 } });
      let finished = false;
      const next = () => {
        const g = queue.shift();
        if (!g) { finished = true; w.terminate(); if (--live === 0) resolve(); return; }
        w.postMessage({ g, outFile: path.join(dir, g.out + '.tsv.gz') });
      };
      w.on('message', m => {
        if (m.error) { errors.push(m.key + ' ' + m.error); console.error('error', m.key, m.error); }
        else {
          results.set(m.key, m.line);
          if (++n % 25 === 0) console.log(`  ${n}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
          if (n % FLUSH === 0) writeIndex();
        }
        next();
      });
      w.on('error', reject);
      w.on('exit', code => { if (!finished) reject(Error('worker exited unexpectedly with code ' + code)); });
      next();
    }
  });
  const order = writeIndex();
  const all = order.map(k => results.get(k));
  const sum = {}; for (const x of all) for (const [k, v] of Object.entries(x.checks)) sum[k] = (sum[k] || 0) + (typeof v === 'boolean' ? (v ? 0 : 1) : v);
  console.log(`${setName}: wrote ${n}, errors ${errors.length}, ${((Date.now() - t0) / 1000).toFixed(0)}s; rows ${all.reduce((a, x) => a + x.rows, 0)}, turns ${all.reduce((a, x) => a + x.turns, 0)}; checks (sum, finalMatch = games failing) ${JSON.stringify(sum)}`);
  if (errors.length) process.exitCode = 1;
}
// top-all: what this run read from the index (the corpus is frozen at start; the collector keeps appending)
function writeManifest(name, games) {
  const dir = path.join(OUTROOT, name);
  fs.mkdirSync(dir, { recursive: true });
  const last = games[games.length - 1] || {};
  let maxGame = 0; for (const g of games) maxGame = Math.max(maxGame, +String(g.key).split(':')[1] || 0);
  const m = { set: name, created: new Date().toISOString(), indexRows: games.indexRows, games: games.length, missingReplays: games.missing,
    lastKey: last.key || null, lastGameId: last.key ? +String(last.key).split(':')[1] : null, maxGameId: maxGame, lastAt: last.at || null, xv: XV };
  fs.writeFileSync(path.join(dir, 'manifest.json.tmp'), JSON.stringify(m, null, 1));
  fs.renameSync(path.join(dir, 'manifest.json.tmp'), path.join(dir, 'manifest.json'));
  console.log(`${name}: index rows ${m.indexRows}, games ${m.games} (missing replays ${m.missingReplays}), last gameId ${m.lastGameId} (${m.lastAt})`);
  return m;
}

// ---------------------------------------------------------------------------------------------------------------
// validate: re-run a few games and compare with top_features.js extract() (deaths, splits, eaten, timeline, pings).
function validate(files, ngames, topAll) {
  const tf = require('./top_features.js');
  const load = tf.makeLoader(tf.viewerSource());
  if (!files.length) {
    const g = topAll ? topGames('all') : topGames(path.join(DATA, 'top', 'snapshot-20260929a.keys'));
    const pick = []; const step = Math.max(1, Math.floor(g.length / ngames));
    for (let i = 0; i < g.length && pick.length < ngames; i += step) pick.push(g[i].file);
    for (const s of onlineSets().slice(0, topAll ? 2 : 1)) pick.push(...onlineGames(s).slice(0, 2).map(x => x.file));
    files = pick;
  }
  let bad = 0;
  for (const f of files) {
    const R = load(f);
    const { rows, info, timeline } = extractGame(R, { key: f, seedHash: 1, ourSide: null });
    const F = tf.extract(R, { battleId: 0, gameId: 0, map: '', winner: null });
    // timeline (units, total, longest every 10 rounds) and deaths/splits/eaten totals must agree
    let tlDiff = 0;
    for (const tm of ['A', 'B']) F[tm].timeline.forEach((p, i) => { const q = timeline[i] && timeline[i][tm]; if (!q || q[0] !== p.units || q[1] !== p.total || q[2] !== p.longest) tlDiff++; });
    const deaths = F.A.deaths.length + F.B.deaths.length, splits = F.A.splits.length + F.B.splits.length;
    const eaten = [...F.A.eaten, ...F.B.eaten].reduce((a, b) => a + b, 0);
    const rowDeaths = rows.filter(r => r[C.fate] !== '').length;
    // sonar: pings per team (top_features counts every ping of a known sender) and ally / enemy landings
    const pingDiff = ['A', 'B'].reduce((a, tm) => a + Math.abs(F[tm].sonar.sent.reduce((x, y) => x + y, 0) - info.tc[tm].pings) +
      Math.abs(F[tm].sonar.ally.reduce((x, y) => x + y, 0) - info.tc[tm].pA) + Math.abs(F[tm].sonar.enemy.reduce((x, y) => x + y, 0) - info.tc[tm].pE), 0);
    const splitDiff = Math.abs(splits - info.tc.A.splits - info.tc.B.splits);
    const chkSum = Object.entries(info.checks).filter(([k, v]) => typeof v === 'number').reduce((a, [, v]) => a + v, 0);
    const okRow = tlDiff === 0 && chkSum === 0 && info.checks.finalMatch && F.meta.simMismatches === 0 && pingDiff === 0 && splitDiff === 0;
    if (!okRow) bad++;
    console.log(`${path.relative(ROOT, f)}: rounds ${info.rounds} turns ${info.turns} rows ${info.rows} | checks ${JSON.stringify(info.checks)} | ` +
      `vs top_features: timeline diffs ${tlDiff}, deaths ${deaths} (own-action deaths in rows ${rowDeaths}), splits ${splits} (diff ${splitDiff}), eaten ${eaten}, ` +
      `pings ${info.tc.A.pings + info.tc.B.pings} (diff ${pingDiff}) | ${okRow ? 'OK' : 'MISMATCH'}`);
  }
  console.log(bad ? `${bad} game(s) failed` : `all ${files.length} games OK`);
  if (bad) process.exitCode = 1;
}

async function main() {
  const argv = process.argv.slice(2);
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const flags = new Set(['--force', '--legacy']);
  const pos = []; for (let i = 0; i < argv.length; i++) { if (argv[i].startsWith('--')) { if (!flags.has(argv[i])) i++; continue; } pos.push(argv[i]); }
  const o = { jobs: Math.max(1, Math.min(MAX_JOBS, +opt('jobs', 3))), force: argv.includes('--force'), limit: opt('limit', null) === null ? Infinity : +opt('limit') };
  const topAll = opt('top', null) === 'all';
  const cmd = pos[0];
  const node = (tool, args) => cp.spawnSync(process.execPath, ['--max-old-space-size=6144', path.join(__dirname, tool), ...args], { stdio: 'inherit' });
  if (cmd === 'extract' && pos[1] === 'top') {
    if (topAll) {
      const name = opt('name', 'top-all'), games = topGames('all');
      writeManifest(name, games);
      await runSet(name, games, o);
    } else {
      const keys = opt('keys', path.join('data', 'top', 'snapshot-20260929a.keys'));
      const name = opt('name', 'top-' + path.basename(keys).replace(/^snapshot-/, '').replace(/\.keys$/, ''));
      await runSet(name, topGames(path.resolve(ROOT, keys)), o);
    }
  } else if (cmd === 'extract' && pos[1] === 'online') {
    const sets = pos.length > 2 ? pos.slice(2) : onlineSets();
    for (const s of sets) await runSet(s, onlineGames(s), o);
  } else if (cmd === 'validate') {
    validate(pos.slice(1).map(f => path.resolve(f)), +opt('games', 6), topAll);
  } else if (cmd === 'refresh' && topAll) {
    const t0 = Date.now();
    const name = opt('name', 'top-all'), games = topGames('all');
    writeManifest(name, games);
    await runSet(name, games, o);
    for (const s of onlineSets()) await runSet(s, onlineGames(s), o);
    const t1 = Date.now();
    const steps = [['decisions_scale.js', ['--top', name, '--jobs', String(o.jobs)]], ['decisions_hyp.js', []]];
    if (argv.includes('--legacy')) steps.push(['decisions_learn.js', ['--top', name, '--out', path.join('data', 'decisions', 'report-all')]],
      ['decisions_rules.js', ['--top', name, '--out', path.join('data', 'decisions', 'rules-all')]]);
    for (const [tool, args] of steps) { const r = node(tool, args); if (r.status) { process.exitCode = r.status; break; } }
    console.log(`refresh --top all: extraction ${((t1 - t0) / 60000).toFixed(1)} min, analysis ${((Date.now() - t1) / 60000).toFixed(1)} min`);
  } else if (cmd === 'refresh') {
    const keys = path.join(DATA, 'top', 'snapshot-20260929a.keys');
    await runSet('top-20260929a', topGames(keys), o);
    for (const s of onlineSets()) await runSet(s, onlineGames(s), o);
    for (const tool of ['decisions_learn.js', 'decisions_rules.js']) {
      const r = node(tool, []);
      if (r.status) { process.exitCode = r.status; break; }
    }
  } else {
    console.error('usage: node tools/decisions.js extract top [--keys F | --top all] [--name N] | extract online [<set>...] | validate [--top all] [files] | refresh [--top all [--legacy]]  [--jobs 3 (max 4)] [--force] [--limit N]');
    process.exit(2);
  }
}
module.exports = { extractGame, COLS, C, XV, topGames, onlineSets, onlineGames, TOP_TEAMS };
if (isMainThread && require.main === module) main().catch(err => { console.error(err); process.exit(1); });
