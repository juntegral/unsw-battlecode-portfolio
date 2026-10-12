#!/usr/bin/env node
// Mass ledger: how teams gain, spend and convert length, from replays only (no network, no games).
// Written for research/observations/top-mass-spending.md (2026-09-30).
//
// usage (repository root):
//   node tools/mass_ledger.js sample [--per-map 150] [--out exp/mass-analysis/sample-top1500.keys]
//       Stratified sample of data/top (per map, balancing team appearances; deterministic hash order).
//   node tools/mass_ledger.js extract top --keys <file | all> [--name top-sample] [--jobs 2] [--limit N]
//   node tools/mass_ledger.js extract online <set> [<set> ...] [--jobs 2]
//       One JSON line per game in .cache/mass-ledger/<name>.jsonl (online: <set>.jsonl). Games already there are skipped.
//   node tools/mass_ledger.js check <cache.jsonl> [...]      sums the reconciliation checks (all expected 0).
//
// Reconstruction: the step simulation of tools/top_features.js / tools/timing_study.js (moves, sprints with their cost,
// kelp, portals, wrap, splits, deaths, pearls through tileChange). Every step is checked against the replay's own
// dragonUpdate head/tail (chk.sim), and the final units / total / longest of both teams against R.result (chk.final).
//
// Definitions (per team; "own" = the team, "enemy" = the other team):
//   Death causes (the dying dragon's team):
//     sac        self-inflicted with a free neighbour at the start of its turn: kelp, own body, ally body, no action,
//                illegal split. (A free neighbour = not kelp, no body of any dragon incl. its own tail.)
//     trap       self-inflicted or moved into an enemy body with no free neighbour (cornered).
//     rammed     an enemy head moved into its head (both die; the enemy is the mover).
//     ram        it moved into an enemy head (both die; it is the mover).
//     enemyBody  it moved into an enemy body with a free neighbour.
//     allyHead   head-on with an ally (either role).
//     fault      timeout.
//     sprintDeath  requested a sprint step it could not pay for (length 2).
//   Pearl origin (seen from the eater): nat (spawned or on the map at start); oX = dropped by an own-team death of cause
//     group X; eX = dropped by an enemy death. Groups: Sac, Trap, Rammed, Ram, Other (enemyBody, allyHead, fault,
//     sprintDeath).
//   King = the team's longest living dragon at that moment (ties -> lowest id). keat_* = pearls eaten by the king.
//   Territory: a tile belongs to the team whose starting bodies are closer by movement distance (kelp, portals, wrap);
//     equal distance or unreachable from both = neutral. Fountain: a tile whose spawn gap mean (min+max)/2 <= 12, read
//     from maps/online-20260927 (the 10-dragon Prisoners Dilemma from maps/variants/prisoners_dilemma_10.map).
//   Sprint purpose (priority order): ram (the move ends in a head-on with an enemy head), eat (a pearl eaten during
//     the move), esc (an enemy head within Chebyshev 3 of our head at turn start), other. Cost = segments paid.
//   Body kill (bk): an enemy that dies by moving into this team's body (any free count).
//   trapE: a trap death with at least one neighbour blocked by an enemy body.
//   Final-king lineage: the longest dragon at the end followed back through its parents. For checkpoint t, Lt = length of
//     the ancestor alive at round start t; final = Lt + eaten - sprint cost - lossOff - lossPath (checked; chk.lineage),
//     lossOff = children split off the line, lossPath = the parent's remaining body when the line continues in the child.
// Output per team: st (state at r = 0, 10, ..., 500 before round r; index 50 = final state carried to 500),
//   fl (flows per 10-round bin, categories FL), dt (deaths aggregated by cause|lenClass|phase|king|near|kdist|mech|blk with
//   [n, len, drops, eatOwn, eatOwnKing, eatEnemy, delaySumOwn, eatOwnBig]), ct (head-on contacts with the enemy, see
//   the code), lin (final-king lineage), misc.
//   near: nearest living ally head within Manhattan 3 at death: '0' none, 'S' shorter than 8, 'B' length >= 8.
//   kdist: Manhattan distance to the team's longest other dragon: k3 <= 3, k8 <= 8, kF farther, kN none.
//   mech: 'stub' = it split within the last 2 rounds and kept <= 3 segments; 'newborn' = born by a split within the last
//   2 rounds; 'other'. blk (trap deaths): 'e' a neighbour blocked by an enemy body, 'a' by an ally body, 's' only
//   its own body / kelp. eatOwnBig = drops eaten by an own dragon of length >= 8.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');

const ROOT = path.resolve(__dirname, '..'), TOP = path.join(ROOT, 'data', 'top'), ONLINE = path.join(ROOT, 'data', 'online');
const CACHE = path.join(ROOT, '.cache', 'mass-ledger');
const NR = 500, NB = 50, TEAMS = ['A', 'B'];
const DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 }, DIRS = ['N', 'E', 'S', 'W'];
const ELIM = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default'];
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const MAPFILE = { 'Autarky': 'autarky', 'Default': 'default', 'Devil': 'devil', 'Portals': 'portals', 'Prisoners Dilemma': 'prisoners_dilemma',
  'Queen Of Spades': 'queen_of_spades', 'Schooltime': 'schooltime', 'Slithery Fight': 'slithery_fight', 'Trauma': 'trauma', 'Trophy': 'trophy' };
const ORIG = ['nat', 'oSac', 'oTrap', 'oRammed', 'oRam', 'oOther', 'eSac', 'eTrap', 'eRammed', 'eRam', 'eOther'];
const CAUSE = ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'];
const CGROUP = [0, 1, 2, 3, 4, 4, 4, 4]; // cause -> origin group (Sac, Trap, Rammed, Ram, Other)
const FL = [
  ...ORIG.map(o => 'eat_' + o), ...ORIG.map(o => 'keat_' + o),
  'nat_own', 'nat_enemy', 'nat_neutral', 'nat_fOwn', 'nat_fEnemy',
  'spr_n', 'spr_ram', 'spr_eat', 'spr_esc', 'spr_other',
  ...CAUSE.map(c => 'dl_' + c), ...CAUSE.map(c => 'dn_' + c),
  'ram_elen', 'rammed_elen', 'bk_n', 'bk_len', 'trapE_n', 'trapE_len',
  'split_n', 'split_child', 'split_stub', 'turns', 'kd_n', 'kd_len', 'eatTC',
];
const FI = Object.fromEntries(FL.map((k, i) => [k, i]));
const GFL = ['spawn_A', 'spawn_B', 'spawn_N', 'fspawn_A', 'fspawn_B', 'fspawn_N'];
const CP = [300, 350, 400, 450];
const lenClass = L => L <= 2 ? '2' : L === 3 ? '3' : L === 4 ? '4' : L <= 7 ? '5-7' : L <= 14 ? '8-14' : '15+';
const phaseOf = r => r < 100 ? 'p0' : r < 250 ? 'p1' : r < 350 ? 'p2' : r < 450 ? 'p3' : 'p4';

// ---------------------------------------------------------------------------------------------------------------
// Map spawn gaps (fountains). The server replays hide pearlRespawn, so the map files are used.
const gapCache = new Map();
function mapGaps(mapName, variant, W, H) {
  const f = variant === 'PD10' ? path.join(ROOT, 'maps', 'variants', 'prisoners_dilemma_10.map') : MAPFILE[mapName] ? path.join(ROOT, 'maps', 'online-20260927', MAPFILE[mapName] + '.map') : null;
  if (!f || !fs.existsSync(f)) return null;
  if (!gapCache.has(f)) {
    const L = fs.readFileSync(f, 'utf8').split('\n');
    const m = /^MAP (\d+) (\d+)/.exec(L[0]); const w = +m[1], h = +m[2];
    const g = new Array(w * h).fill(null);
    for (const l of L) if (l.startsWith('TILE ')) { const [x, y, mn, mx] = l.trim().split(/\s+/).slice(1).map(Number); g[y * w + x] = [mn, mx]; }
    gapCache.set(f, { w, h, g });
  }
  const c = gapCache.get(f);
  return c.w === W && c.h === H ? c.g : null;
}

// ---------------------------------------------------------------------------------------------------------------
// Per-game extraction. `hooks` (optional, used by tools/mech_check.js) observes the reconstruction without changing it:
//   turn(d, round, ctx), indicator(e, round, ctx), action(d, e, round, ctx, bodyBefore), eat(d, tile, deathIdx, round, ctx),
//   split(parent, child, e, round, ctx), death(d, rec, deathIdx, other, round, ctx), end(rounds, ctx).
//   d.portalSteps = portal crossings in the dragon's last move.
function perGame(R, info, hooks) {
  const M = R.match.map, W = M.width, H = M.height, N = W * H;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const key = (x, y) => y * W + x;
  const tdist = (a, b) => { const dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
  const cheb = (a, b) => { const dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); return Math.max(Math.min(dx, W - dx), Math.min(dy, H - dy)); };
  // geometry (tools/top_features.js)
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
    return { x: wx(x + DX[d]), y: wy(y + DY[d]) };
  }
  // territory: movement distance from each team's starting bodies
  const distFrom = team => {
    const dist = new Int32Array(N).fill(-1), q = [];
    for (const d0 of M.initialDragons) if (d0.team === team) for (const s of d0.body) { const k = key(s.x, s.y); if (dist[k] < 0) { dist[k] = 0; q.push(k); } }
    for (let i = 0; i < q.length; i++) {
      const k = q[i], x = k % W, y = (k / W) | 0;
      for (const d of DIRS) { const nx = across(x, y, d); if (!nx) continue; const nk = key(nx.x, nx.y); if (dist[nk] < 0) { dist[nk] = dist[k] + 1; q.push(nk); } }
    }
    return dist;
  };
  const dA = distFrom('A'), dB = distFrom('B');
  const terr = new Int8Array(N); // 0 neutral, 1 A, 2 B
  for (let k = 0; k < N; k++) { const a = dA[k] < 0 ? Infinity : dA[k], b = dB[k] < 0 ? Infinity : dB[k]; terr[k] = a < b ? 1 : b < a ? 2 : 0; }
  const gaps = mapGaps(info.map, info.variant, W, H);
  const fount = new Uint8Array(N);
  let fountTiles = 0;
  if (gaps) for (let k = 0; k < N; k++) { const g = gaps[k]; if (g && g[1] > 0 && (g[0] + g[1]) / 2 <= 12) { fount[k] = 1; fountTiles++; } }
  const tIdx = tm => tm === 'A' ? 1 : 2;

  // state
  const drag = new Map(), all = new Map(), occ = new Map();
  const setOcc = d => { for (const s of d.body) occ.set(key(s.x, s.y), d.id); };
  const clrOcc = d => { for (const s of d.body) if (occ.get(key(s.x, s.y)) === d.id) occ.delete(key(s.x, s.y)); };
  const pearls = new Map(); // tile -> -1 natural, else death index
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearls.set(i, -1);
  let seq = 0, round = -1, cur = -1;
  const seqAtCP = {};
  const newDragon = (id, team, body, born, parent) => {
    const o = { id, team, body: body.map(s => ({ x: s.x, y: s.y })), born, parent, bornSeq: seq, fate: null, expect: [], act: null, tle: false,
      free: -1, enemyNear: 0, enemyBlock: 0, allyBlock: 0, eats: [], costs: [], splitsOut: [], lenAt: {}, ateThisAct: 0, steps: 0, lastSplitR: -9, lastSplitKept: 99 };
    drag.set(id, o); all.set(id, o); setOcc(o); return o;
  };
  for (const d0 of M.initialDragons) newDragon(d0.id, d0.team, d0.body, 0, -1);

  const T = {};
  for (const tm of TEAMS) T[tm] = {
    st: { units: [], total: [], king: [], second: [], small: [], mid: [], big: [] },
    fl: FL.map(() => new Array(NB).fill(0)),
    sonar: 0, splits: 0,
  };
  const GF = GFL.map(() => new Array(NB).fill(0));
  const deaths = []; // {r, team, cause, len, drops, eatOwn, eatOwnKing, eatEnemy, delayOwn, king, near, kdist}
  const chk = { sim: 0, splits: 0, drops: 0, eatTC: 0, ledger: 0, final: 0, lineage: 0, natBal: 0, dropBal: 0, unknownDeath: 0 };
  const bin = r => Math.max(0, Math.min(NB - 1, Math.floor(r / 10)));
  const add = (tm, cat, v = 1) => { if (round >= 0) T[tm].fl[FI[cat]][bin(round)] += v; };
  const better = (a, b) => !b || a.body.length > b.body.length || (a.body.length === b.body.length && a.id < b.id);
  const kingOf = tm => { let k = null; for (const d of drag.values()) if (d.team === tm && better(d, k)) k = d; return k; };
  const isKingNow = d => { for (const o of drag.values()) if (o.team === d.team && o !== d && better(o, d)) return false; return true; };
  let drop = null;
  let natSpawned = 0, natStart = 0, dropsTotal = 0;
  for (const o of pearls.values()) if (o < 0) natStart++;
  const tot = { A: 0, B: 0 };
  const flowRound = { A: 0, B: 0 }; // eat - cost - death length within the current round (ledger identity)
  let lastTot = null;

  const stateAt = r => { // r = 0,10,..,500 (state before round r) ; also the final state
    const i = r / 10;
    for (const tm of TEAMS) {
      const s = T[tm].st; let units = 0, total = 0, king = null, second = 0, small = 0, mid = 0, big = 0;
      for (const d of drag.values()) if (d.team === tm) { units++; total += d.body.length; if (better(d, king)) king = d; }
      for (const d of drag.values()) if (d.team === tm && d !== king) {
        const L = d.body.length; if (L > second) second = L;
        if (L <= 4) small += L; else if (L <= 9) mid += L; else big += L;
      }
      s.units[i] = units; s.total[i] = total; s.king[i] = king ? king.body.length : 0; s.second[i] = second; s.small[i] = small; s.mid[i] = mid; s.big[i] = big;
    }
  };
  const teamTotal = tm => { let t = 0; for (const d of drag.values()) if (d.team === tm) t += d.body.length; return t; };
  const checkLedger = () => { // at every round start: total(r) - total(r-1) = flows of round r-1
    for (const tm of TEAMS) { const t = teamTotal(tm); if (lastTot && t - lastTot[tm] !== flowRound[tm]) chk.ledger++; tot[tm] = t; flowRound[tm] = 0; }
    lastTot = { A: tot.A, B: tot.B };
  };
  const freeAround = d => {
    let n = 0, eb = 0, ab = 0; const h = d.body[0];
    for (const st of DIRS) {
      const nx = across(h.x, h.y, st); if (!nx) continue;
      const o = occ.get(key(nx.x, nx.y));
      if (o === undefined) n++; else { const od = drag.get(o); if (od && od.team !== d.team) eb = 1; else if (od && od !== d) ab = 1; }
    }
    d.enemyBlock = eb; d.allyBlock = ab;
    return n;
  };
  const enemyNear = d => { const h = d.body[0]; for (const o of drag.values()) if (o.team !== d.team && cheb(o.body[0], h) <= 3) return 1; return 0; };
  const eatAt = (d, k) => {
    const o = pearls.get(k); pearls.delete(k);
    const tm = d.team, king = isKingNow(d);
    let oi = 0;
    if (o >= 0) {
      const x = deaths[o], own = x.team === tm, g = CGROUP[x.cause];
      oi = own ? 1 + g : 6 + g;
      if (own) { x.eatOwn++; if (king) x.eatOwnKing++; if (d.body.length >= 8) x.eatOwnBig++; x.delayOwn += round - x.r; } else x.eatEnemy++;
    } else {
      const t = terr[k], mine = tIdx(tm);
      add(tm, t === 0 ? 'nat_neutral' : t === mine ? 'nat_own' : 'nat_enemy');
      if (fount[k]) { if (t === mine) add(tm, 'nat_fOwn'); else if (t !== 0) add(tm, 'nat_fEnemy'); }
    }
    add(tm, 'eat_' + ORIG[oi]); if (king) add(tm, 'keat_' + ORIG[oi]);
    flowRound[tm]++;
    d.eats.push(seq, round, oi);
    d.ateThisAct++;
    if (hooks && hooks.eat) hooks.eat(d, k, o, round, ctx);
  };
  const removeDragon = d => { clrOcc(d); drag.delete(d.id); };
  const ctx = { drag, all, deaths, occ, pearls, terr, W, H, key, across, tdist, cheb, isKingNow, kingOf };

  let eatTCteam = { A: 0, B: 0 };
  for (const e of R.events) {
    seq++;
    if (drop && !(e.type === 'tileChange' && e.hasPearl)) { if (drop.got !== drop.want) chk.drops++; drop = null; }
    switch (e.type) {
      case 'roundStart':
        round = e.round;
        checkLedger();
        if (round % 10 === 0 && round <= NR) stateAt(round);
        if (CP.includes(round)) { for (const d of drag.values()) d.lenAt[round] = d.body.length; }
        if (CP.includes(round)) seqAtCP[round] = seq;
        break;
      case 'turnStart': {
        cur = e.id;
        const d = drag.get(cur);
        if (d) { d.fate = null; d.expect = []; d.act = null; d.tle = false; d.free = freeAround(d); d.enemyNear = enemyNear(d); d.ateThisAct = 0; add(d.team, 'turns'); }
        if (d && hooks && hooks.turn) hooks.turn(d, round, ctx);
        break;
      }
      case 'dragonIndicator': if (hooks && hooks.indicator) hooks.indicator(e, round, ctx); break;
      case 'tileChange': {
        const k = key(e.tile.x, e.tile.y);
        if (e.hasPearl) {
          if (drop) { pearls.set(k, drop.idx); drop.got++; dropsTotal++; }
          else {
            pearls.set(k, -1);
            if (round >= 0) { natSpawned++; const t = terr[k], b = bin(round); GF[t === 1 ? 0 : t === 2 ? 1 : 2][b]++; if (fount[k]) GF[t === 1 ? 3 : t === 2 ? 4 : 5][b]++; }
          }
        } else {
          const d = drag.get(cur);
          if (d && round >= 0) { eatTCteam[d.team]++; add(d.team, 'eatTC'); }
          if (pearls.has(k)) { chk.eatTC++; if (d) eatAt(d, k); else pearls.delete(k); } // not predicted by the simulation
        }
        break;
      }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action;
        d.act = a ? a.kind : null; d.tle = !!e.tle; d.steps = a && a.kind === 'move' ? a.steps.length : 0; d.portalSteps = 0;
        const hb = hooks && hooks.action ? d.body.slice() : null;
        if (!a || a.kind !== 'move') { if (hb) hooks.action(d, e, round, ctx, hb); break; }
        const t = d.team;
        clrOcc(d);
        const body = d.body.slice();
        let fate = null, paid = 0;
        for (let i = 0; i < a.steps.length; i++) {
          const st = a.steps[i];
          if (i > 0 && body.length <= 2) { fate = { reason: 'A', step: i, why: 'sprint' }; break; }
          const h = body[0], nx = across(h.x, h.y, st);
          if (!nx) { fate = { reason: 'W', step: i }; break; }
          if (nx.x !== wx(h.x + DX[st]) || nx.y !== wy(h.y + DY[st])) d.portalSteps++;
          if (body.some(s => s.x === nx.x && s.y === nx.y)) { fate = { reason: 'S', step: i }; break; }
          const o = occ.get(key(nx.x, nx.y));
          if (o !== undefined) {
            const od = drag.get(o), isHead = od.body[0].x === nx.x && od.body[0].y === nx.y;
            fate = { reason: isHead ? 'H' : 'O', step: i, hit: o, hitTeam: od.team, hitLen: od.body.length };
            break;
          }
          body.unshift(nx);
          const k = key(nx.x, nx.y);
          if (pearls.has(k)) eatAt(d, k); else body.pop();
          if (i > 0) { body.pop(); paid++; }
          d.expect.push({ h: body[0], t: body[body.length - 1] });
        }
        if (a.steps.length >= 2) {
          add(t, 'spr_n');
          if (paid) {
            const ram = fate && fate.reason === 'H' && fate.hitTeam !== t;
            add(t, ram ? 'spr_ram' : d.ateThisAct ? 'spr_eat' : d.enemyNear ? 'spr_esc' : 'spr_other', paid);
            flowRound[t] -= paid;
            d.costs.push(seq, paid);
          }
        }
        d.fate = fate;
        d.body = body;
        setOcc(d);
        if (hb) hooks.action(d, e, round, ctx, hb);
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id);
        if (!d || round < 0) break;
        const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        if (x.h.x !== e.head.x || x.h.y !== e.head.y || x.t.x !== e.tail.x || x.t.y !== e.tail.y) {
          chk.sim++;
          clrOcc(d);
          const b = d.body.slice();
          if (b[0].x !== e.head.x || b[0].y !== e.head.y) b.unshift({ x: e.head.x, y: e.head.y });
          while (b.length > 1 && (b[b.length - 1].x !== e.tail.x || b[b.length - 1].y !== e.tail.y)) b.pop();
          d.body = b; d.expect = [];
          setOcc(d);
        }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        const before = p.body.length;
        if (before !== e.parentBody.length + e.childBody.length) chk.splits++;
        add(p.team, 'split_n'); add(p.team, 'split_child', e.childBody.length);
        if (e.parentBody.length <= 3 && e.childBody.length >= 4) add(p.team, 'split_stub');
        T[p.team].splits++;
        p.splitsOut.push(seq, e.childBody.length, e.childId, e.parentBody.length);
        p.lastSplitR = round; p.lastSplitKept = e.parentBody.length;
        clrOcc(p);
        p.body = e.parentBody.map(s => ({ x: s.x, y: s.y }));
        setOcc(p);
        const ch = newDragon(e.childId, e.team, e.childBody, round, p.id);
        if (hooks && hooks.split) hooks.split(p, ch, e, round, ctx);
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        const mover = cur === d.id, tm = d.team, L = d.body.length;
        let cause = -1, other = null;
        if (mover) {
          const f = d.fate;
          if (e.reason === 'A') {
            if (d.tle) cause = 6;
            else if (f && f.why === 'sprint') cause = 7;
            else cause = d.free > 0 ? 0 : 1;
          } else if (e.reason === 'W' || e.reason === 'S') cause = d.free > 0 ? 0 : 1;
          else if (e.reason === 'O') {
            other = f && f.hit !== undefined ? all.get(f.hit) : null;
            if (!f || f.reason !== 'O') chk.unknownDeath++;
            if (other && other.team === tm) cause = d.free > 0 ? 0 : 1;
            else { cause = d.free > 0 ? 4 : 1; if (other) { add(other.team, 'bk_n'); add(other.team, 'bk_len', L); } }
          } else if (e.reason === 'H') {
            other = f && f.hit !== undefined ? all.get(f.hit) : null;
            if (!f || f.reason !== 'H') chk.unknownDeath++;
            if (other && other.team === tm) cause = 5; else { cause = 3; add(tm, 'ram_elen', f ? f.hitLen : 0); }
          }
        } else {
          const m = drag.get(cur);
          if (e.reason !== 'H' || !m || !m.fate || m.fate.hit !== d.id) chk.unknownDeath++;
          if (m && m.team === tm) cause = 5; else { cause = 2; add(tm, 'rammed_elen', m ? m.body.length : 0); }
        }
        if (cause < 0) { chk.unknownDeath++; cause = 1; }
        if (cause === 1 && d.enemyBlock) { add(tm, 'trapE_n'); add(tm, 'trapE_len', L); }
        const wasKing = isKingNow(d) && L >= 8;
        if (wasKing) { add(tm, 'kd_n'); add(tm, 'kd_len', L); }
        // context: nearest living ally head within Manhattan 3 (its length class) and distance to the longest other ally
        let nearLen = 0, nearD = 99, kd = 99, ko = null;
        for (const o of drag.values()) {
          if (o === d || o.team !== tm) continue;
          const x = tdist(o.body[0], d.body[0]);
          if (x <= 3 && (x < nearD || (x === nearD && o.body.length > nearLen))) { nearD = x; nearLen = o.body.length; }
          if (better(o, ko)) ko = o;
        }
        if (ko) kd = tdist(ko.body[0], d.body[0]);
        add(tm, 'dl_' + CAUSE[cause], L); add(tm, 'dn_' + CAUSE[cause]);
        flowRound[tm] -= L;
        const mech = d.lastSplitR >= round - 2 && d.lastSplitKept <= 3 ? 'stub' : d.parent >= 0 && d.born >= round - 2 ? 'newborn' : 'other';
        const blk = cause !== 1 ? '-' : d.enemyBlock ? 'e' : d.allyBlock ? 'a' : 's';
        const rec = { r: round, team: tm, cause, len: L, drops: Math.ceil(L / 2), eatOwn: 0, eatOwnKing: 0, eatOwnBig: 0, eatEnemy: 0, delayOwn: 0, king: wasKing ? 1 : 0,
          near: nearD <= 3 ? (nearLen >= 8 ? 'B' : 'S') : '0', kdist: ko ? (kd <= 3 ? 'k3' : kd <= 8 ? 'k8' : 'kF') : 'kN', kingNow: ko ? ko.body.length : 0, mech, blk,
          pair: -1, spr: 0 };
        if (cause === 3) { // mover of a head-on with an enemy: the victim died just before (its record is the previous one)
          const v = deaths[deaths.length - 1];
          if (v && v.cause === 2 && v.r === round && v.pair === -2) { rec.pair = deaths.length - 1; v.pair = deaths.length; }
          rec.spr = d.steps >= 2 ? 1 : 0;
        }
        if (cause === 2) rec.pair = -2; // waiting for the mover's record
        deaths.push(rec);
        if (hooks && hooks.death) hooks.death(d, rec, deaths.length - 1, mover ? other : drag.get(cur) || null, round, ctx);
        removeDragon(d);
        drop = { idx: deaths.length - 1, got: 0, want: Math.ceil(L / 2) };
        break;
      }
      case 'sonarPing': { const s = drag.get(e.senderId); if (s) T[s.team].sonar++; break; }
    }
  }
  if (drop && drop.got !== drop.want) chk.drops++;
  const rounds = round + 1;
  if (hooks && hooks.end) hooks.end(rounds, ctx);
  checkLedger();
  // final state carried to 500
  for (let r = Math.ceil(rounds / 10) * 10; r <= NR; r += 10) stateAt(r);
  // final vs result
  const res = R.result;
  for (const tm of TEAMS) {
    const x = res['team' + tm], s = T[tm].st, i = 50;
    if (s.units[i] !== x.dragonCount || s.king[i] !== x.longestDragon || s.total[i] !== x.totalLength) chk.final++;
  }
  // pearl balances (natural and dropped)
  let natEnd = 0, dropEnd = 0; for (const o of pearls.values()) { if (o < 0) natEnd++; else dropEnd++; }
  let natEaten = 0, dropEaten = 0;
  for (const tm of TEAMS) { const fl = T[tm].fl; for (let b = 0; b < NB; b++) { natEaten += fl[FI.eat_nat][b]; for (let o = 1; o < ORIG.length; o++) dropEaten += fl[FI['eat_' + ORIG[o]]][b]; } }
  if (natStart + natSpawned - natEaten !== natEnd) chk.natBal++;
  if (dropsTotal - dropEaten !== dropEnd) chk.dropBal++;
  for (const tm of TEAMS) { let s = 0; for (let b = 0; b < NB; b++) s += T[tm].fl[FI.eat_nat][b] + ORIG.slice(1).reduce((a, o) => a + T[tm].fl[FI['eat_' + o]][b], 0); if (s !== eatTCteam[tm]) chk.eatTC++; }

  // deaths aggregated
  const dt = { A: {}, B: {} };
  for (const x of deaths) {
    const k = CAUSE[x.cause] + '|' + lenClass(x.len) + '|' + phaseOf(x.r) + '|' + x.king + '|' + x.near + '|' + x.kdist + '|' + x.mech + '|' + x.blk;
    const a = dt[x.team][k] || (dt[x.team][k] = [0, 0, 0, 0, 0, 0, 0, 0]);
    a[0]++; a[1] += x.len; a[2] += x.drops; a[3] += x.eatOwn; a[4] += x.eatOwnKing; a[5] += x.eatEnemy; a[6] += x.delayOwn; a[7] += x.eatOwnBig;
  }
  // head-on contacts with the enemy, from each side: role|ourLenClass|theirLenClass|phase|moverSprint|ourKing ->
  //   [n, ourLen, theirLen, our drops eaten by us, our drops eaten by them, their drops eaten by us, their drops eaten by them]
  const ct = { A: {}, B: {} };
  for (const x of deaths) {
    if (x.cause !== 3 || x.pair < 0) continue;
    const v = deaths[x.pair];
    const put = (me, them, role) => {
      const k = role + '|' + lenClass(me.len) + '|' + lenClass(them.len) + '|' + phaseOf(x.r) + '|' + x.spr + '|' + me.king;
      const a = ct[me.team][k] || (ct[me.team][k] = [0, 0, 0, 0, 0, 0, 0]);
      a[0]++; a[1] += me.len; a[2] += them.len; a[3] += me.eatOwn; a[4] += me.eatEnemy; a[5] += them.eatEnemy; a[6] += them.eatOwn;
    };
    put(x, v, 'ram'); put(v, x, 'rammed');
  }
  for (const x of deaths) if ((x.cause === 3 && x.pair < 0) || x.cause === 2 && x.pair < 0) chk.unknownDeath++;
  // final-king lineage
  const lin = {};
  for (const tm of TEAMS) {
    let k = null; for (const d of drag.values()) if (d.team === tm && better(d, k)) k = d;
    if (!k) { lin[tm] = null; continue; }
    const line = []; for (let x = k; x; x = x.parent >= 0 ? all.get(x.parent) : null) line.push(x);
    line.reverse();
    const out = { len: k.body.length, gen: line.length - 1, born: k.born, cp: {}, win: null };
    for (const t of CP) {
      if (!(t < rounds) || seqAtCP[t] === undefined) continue;
      let j = -1; for (let i = 0; i < line.length; i++) if (line[i].parent < 0 || line[i].bornSeq < seqAtCP[t]) j = i;
      if (j < 0) continue;
      const a = line[j], Lt = a.lenAt[t];
      if (Lt === undefined) continue;
      const eat = new Array(ORIG.length).fill(0); let cost = 0, lossOff = 0, lossPath = 0;
      const win = t === 350 ? [new Array(15).fill(0), new Array(15).fill(0), new Array(15).fill(0)] : null; // nat, own drops, enemy drops per 10 rounds from 350
      for (let i = j; i < line.length; i++) {
        const x = line[i], from = i === j ? seqAtCP[t] : x.bornSeq, to = i + 1 < line.length ? line[i + 1].bornSeq : Infinity;
        for (let q = 0; q < x.eats.length; q += 3) if (x.eats[q] > from && x.eats[q] < to) {
          eat[x.eats[q + 2]]++;
          if (win) { const w = Math.floor((x.eats[q + 1] - 350) / 10); if (w >= 0 && w < 15) win[x.eats[q + 2] === 0 ? 0 : x.eats[q + 2] <= 5 ? 1 : 2][w]++; }
        }
        for (let q = 0; q < x.costs.length; q += 2) if (x.costs[q] > from && x.costs[q] < to) cost += x.costs[q + 1];
        for (let q = 0; q < x.splitsOut.length; q += 4) {
          if (!(x.splitsOut[q] > from && x.splitsOut[q] <= to)) continue;
          if (i + 1 < line.length && x.splitsOut[q + 2] === line[i + 1].id) lossPath += x.splitsOut[q + 3];
          else lossOff += x.splitsOut[q + 1];
        }
      }
      const eaten = eat.reduce((s, v) => s + v, 0);
      const ok = Lt + eaten - cost - lossOff - lossPath === k.body.length;
      if (!ok) chk.lineage++;
      out.cp[t] = { Lt, eat, cost, lossOff, lossPath, transfers: line.length - 1 - j, wasKing: Lt === T[tm].st.king[t / 10] ? 1 : 0 };
      if (win) out.win = win;
    }
    lin[tm] = out;
  }
  const team = tm => ({ st: T[tm].st, fl: T[tm].fl, dt: dt[tm], ct: ct[tm], lin: lin[tm], sonar: T[tm].sonar, splits: T[tm].splits });
  return {
    rounds, endReason: res.endReason, winner: res.winner || null, W, H, fountTiles,
    terrTiles: [0, 1, 2].map(v => terr.reduce((s, x) => s + (x === v ? 1 : 0), 0)),
    natStart, natSpawned, gf: GF, chk, A: team('A'), B: team('B'),
  };
}

// ---------------------------------------------------------------------------------------------------------------
// Worker (child process): parse and extract one game per message.
function workerMain() {
  const { makeLoader, viewerSource } = require('./top_features.js');
  const load = makeLoader(viewerSource());
  process.on('message', task => {
    try {
      const R = load(task.file);
      const nInit = R.match.map.initialDragons.length;
      const info = { ...task.info };
      if (info.map === 'Prisoners Dilemma') info.variant = nInit === 10 ? 'PD10' : 'PD6';
      const g = perGame(R, info);
      process.send({ key: task.key, line: JSON.stringify({ key: task.key, ...info, seed: R.seed, ...g }) });
    } catch (err) { process.send({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | ') }); }
  });
}

// ---------------------------------------------------------------------------------------------------------------
// Task lists
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];
function topIndex() {
  const seen = new Set(), out = [];
  for (const r of readJsonl(path.join(TOP, 'index.jsonl'))) { const k = r.battleId + ':' + r.gameId; if (seen.has(k)) continue; seen.add(k); out.push(r); }
  return out;
}
const kindOf = m => ELIM.includes(m) ? 'elim' : R500.includes(m) ? 'r500' : 'other';
function topTasks(keysArg) {
  const idx = topIndex(), byKey = new Map(idx.map(r => [r.battleId + ':' + r.gameId, r]));
  const keys = keysArg === 'all' ? [...byKey.keys()] : fs.readFileSync(path.resolve(ROOT, keysArg), 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  const out = [];
  for (const k of keys) {
    const r = byKey.get(k); if (!r) continue;
    const f = path.join(TOP, String(r.battleId), r.gameId + '.replay.gz'); if (!fs.existsSync(f)) continue;
    out.push({ key: k, file: f, info: { src: 'top', map: r.map, kind: kindOf(r.map), teamA: r.teamA, teamB: r.teamB, eloA: r.eloA, eloB: r.eloB,
      winnerIdx: r.winner ? String(r.winner).toUpperCase() : null, ranked: !!r.ranked, at: r.at, us: null } });
  }
  return out;
}
function onlineTasks(set) {
  const dir = path.join(ONLINE, set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  let names = {};
  try { for (const t of JSON.parse(fs.readFileSync(path.join(TOP, 'leaderboard.json'), 'utf8'))) names[t.id] = t.name; } catch { /* optional */ }
  const out = [];
  for (const g of idx.games) {
    const f = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
    const us = String(g.ourSide).toUpperCase(), opp = names[g.opponentTeam] || String(g.opponentTeam);
    out.push({ key: set + ':' + g.gameId, file: f, info: { src: 'online', set, map: g.mapName, kind: kindOf(g.mapName), teamA: us === 'A' ? set : opp, teamB: us === 'B' ? set : opp,
      oppId: g.opponentTeam, winnerIdx: g.winner ? String(g.winner).toUpperCase() : null, ranked: !!g.ranked, at: g.completedAt, us, sub: g.ourSubmission } });
  }
  return out;
}

// Stratified sample: per map, games in a deterministic hash order, greedily preferring games whose teams have appeared
// least so far on that map (balances team pairs). Teams: every team in data/top.
function hash32(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
function sample(perMap, outFile) {
  const idx = topIndex(), byMap = {};
  for (const r of idx) { if (!fs.existsSync(path.join(TOP, String(r.battleId), r.gameId + '.replay.gz'))) continue; (byMap[r.map] = byMap[r.map] || []).push(r); }
  const keys = [];
  for (const [m, list] of Object.entries(byMap).sort()) {
    list.sort((a, b) => hash32(a.battleId + ':' + a.gameId) - hash32(b.battleId + ':' + b.gameId));
    const cnt = {}, used = new Set();
    for (let n = 0; n < Math.min(perMap, list.length); n++) {
      let best = null, bs = Infinity;
      for (const r of list) { const k = r.battleId + ':' + r.gameId; if (used.has(k)) continue; const s = (cnt[r.teamA] || 0) + (cnt[r.teamB] || 0); if (s < bs) { bs = s; best = r; if (s === 0) break; } }
      if (!best) break;
      const k = best.battleId + ':' + best.gameId; used.add(k); keys.push(k);
      cnt[best.teamA] = (cnt[best.teamA] || 0) + 1; cnt[best.teamB] = (cnt[best.teamB] || 0) + 1;
    }
  }
  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  fs.writeFileSync(outFile, keys.join('\n') + '\n');
  console.log(`sample: ${keys.length} games (${Object.keys(byMap).length} maps, up to ${perMap} each) -> ${path.relative(ROOT, outFile)}`);
}

async function extract(tasks, cacheFile, jobs, limit) {
  fs.mkdirSync(path.dirname(cacheFile), { recursive: true });
  const done = new Set();
  if (fs.existsSync(cacheFile)) for (const l of fs.readFileSync(cacheFile, 'utf8').split('\n')) { const m = /^\{"key":"([^"]+)"/.exec(l); if (m) done.add(m[1]); }
  const todo = tasks.filter(t => !done.has(t.key)).slice(0, limit);
  console.log(`${path.relative(ROOT, cacheFile)}: ${tasks.length} games, cached ${done.size}, to do ${todo.length} (jobs ${jobs})`);
  if (!todo.length) return;
  const fd = fs.openSync(cacheFile, 'a'), t0 = Date.now(), errors = [];
  let n = 0;
  await new Promise((resolve, reject) => {
    const queue = todo.slice(); let live = Math.min(jobs, queue.length);
    for (let i = 0, k = live; i < k; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced', execArgv: ['--max-old-space-size=3072'] });
      let finished = false;
      const next = () => { const t = queue.shift(); if (!t) { finished = true; w.kill(); if (--live === 0) resolve(); return; } w.send(t); };
      w.on('message', m => {
        if (m.error) { errors.push(m.key + ' ' + m.error); console.error('error', m.key, m.error); }
        else { fs.writeSync(fd, m.line + '\n'); }
        n++;
        if (n % 50 === 0) console.log(`  ${n}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
        next();
      });
      w.on('error', reject);
      w.on('exit', code => { if (!finished) reject(Error('worker exited unexpectedly with code ' + code)); });
      next();
    }
  });
  fs.closeSync(fd);
  console.log(`done ${n} in ${((Date.now() - t0) / 1000).toFixed(0)}s, errors ${errors.length}`);
}

function checkFiles(files) {
  const sum = {}; let games = 0;
  for (const f of files) for (const l of fs.readFileSync(f, 'utf8').split('\n')) {
    if (!l.trim()) continue; const g = JSON.parse(l); games++;
    for (const [k, v] of Object.entries(g.chk)) sum[k] = (sum[k] || 0) + v;
  }
  console.log(`games ${games}; checks summed (all expected 0): ${JSON.stringify(sum)}`);
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const jobs = Math.max(1, Math.min(2, +opt('jobs', 2))), limit = +opt('limit', Infinity);
  const cmd = argv[0];
  if (cmd === 'sample') return sample(+opt('per-map', 150), path.resolve(ROOT, opt('out', 'exp/mass-analysis/sample-top1500.keys')));
  if (cmd === 'extract' && argv[1] === 'top') {
    const keys = opt('keys', null); if (!keys) throw Error('--keys <file|all> required');
    return extract(topTasks(keys), path.join(CACHE, opt('name', 'top-sample') + '.jsonl'), jobs, limit);
  }
  if (cmd === 'extract' && argv[1] === 'online') {
    const sets = []; for (let i = 2; i < argv.length; i++) { if (argv[i].startsWith('--')) { i++; continue; } sets.push(argv[i]); }
    for (const s of sets) await extract(onlineTasks(s), path.join(CACHE, 'online-' + s + '.jsonl'), jobs, limit);
    return;
  }
  if (cmd === 'check') return checkFiles(argv.slice(1).map(f => path.resolve(ROOT, f)));
  console.error('usage: see the header of tools/mass_ledger.js'); process.exit(2);
}
module.exports = { perGame, FL, FI, GFL, ORIG, CAUSE, CP, ELIM, R500, CACHE, topIndex, lenClass, phaseOf };
if (require.main === module) main().catch(err => { console.error(err); process.exit(1); });
