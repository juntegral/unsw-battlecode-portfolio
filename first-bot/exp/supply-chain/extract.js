#!/usr/bin/env node
// Supply chain of the middle links (conv, feed / gather, grab, piece recycling), the life ledger of every split piece and
// the formation of pieces around big allies. Replays only (no games, no network). Written for
// research/observations/supply-chain.md (2026-09-30).
//
// usage (repository root):
//   node exp/supply-chain/extract.js top --keys <file> [--name top-all] [--jobs 3] [--limit N]
//   node exp/supply-chain/extract.js online <set> [<set> ...] [--jobs 3]
//   node exp/supply-chain/extract.js one <replay file> <map name> [<us A|B>]     (debug: timing and a summary)
//   Output: one gzip member (one JSON line) per game in .cache/supply-chain/<name>.jsonl.gz (online: online-<set>.jsonl.gz).
//   Games already in the file are skipped.
//
// Reconstruction: tools/mass_ledger.js perGame() with hooks (its checks must stay 0). Geometry, territory, pearl layout and
// spawn capacity: exp/territory-analysis/extract.js (geometry, variantOf, fileOf, gapsOfFile).
//
// Link states (evaluated for every dragon at the start of its turn = its decision moment; bot rules in
// exp/cand-stack6/bot/plan.cpp decide()):
//   conv  csGeo: length 2-4 and an ally of length >= 8 and >= L+4 in the 7x7 view (Chebyshev 3; plan.cpp allyHeadsNow) within
//         path distance 3 (from our head through free tiles and our own body, portals included; plan.cpp CONV_*). cs = csGeo and no enemy head in the 7x7 view (Chebyshev 3).
//         csE = cs and the bot's other conditions: r >= 300, team units >= 3, not a young piece (born by a split <= 2 long
//         within 20 rounds), not within 3 rounds of its own split that left it <= 3 (stub).
//         csV = csGeo with an enemy head in view. csN = length 2-4, not csGeo, an ally >= 8 within Manhattan 6.
//   feed  (r >= 250) fsGeo: not the team's longest and a longer ally in the 7x7 view within path distance 5 (same BFS).
//         fs = fsGeo, no enemy head within Manhattan 4 (plan.cpp: enemyDist > 4), team units >= 3.
//         fsK = fs and the team's longest (the king) is within path 5. fsG = fs, units >= 4, length >= 4 (gathering feed).
//   gather (r >= 340) gs: not the team's longest, length >= 4, units >= 4 (plan.cpp computeGoal); Manhattan distance to the
//         king and whether it fell since this dragon's previous turn.
//   grab  every death drop (pearl): static path distance (bodies ignored, plan.cpp headDist_) from each team's nearest head
//         when it appears and at the next 6 round starts (GRAB_ROUNDS); within6 = <= 6 (GRAB_REACH) during that window;
//         view = a head of the team within Chebyshev 3 when it appears. Its eater, delay; our grab labels on it.
//   Acting: for every team, a sacrifice (mass ledger cause 'sac': self-inflicted with a free neighbour) at a turn in the
//         state. Our bot: its labels (conv / feed / g goal / grab). Episodes: a dragon's consecutive turns in a state; fired
//         = it sacrificed at a turn in the state; success = >= half of the dropped pearls eaten by its team and none by the
//         opponent (tools/mech_check.js), successBig = >= half eaten by own dragons of length >= 8.
// Pieces (life ledger): every child born by a split with length <= 3. Birth context, lifetime, steps, territory turns,
//   natural and dropped pearls eaten, sprint cost, children, end (alive / cause), death drops eaten by whom, distance to the
//   nearest own head of length >= 8 over its life, natural spawns it was the unique nearest head of within 30 rounds.
//   Identity checked: birth + eaten - sprint - children = final length (chk.piece).
//   Piece array (P): 0 team(0 A, 1 B) 1 born 2 birthLen 3 parentLen(before) 4 class(ours: 1 csplit 2 frag 3 bsp 4 split 5 escape-split
//   6 esc-split 7 pocket 9 unlabelled; top 0) 5 parentWasLongest 6 birthTerr(0 own 1 neutral 2 enemy) 7 enemyHeadInView 8 nearest own
//   >=8 head (Manhattan, 99 none) 9 nearest own head 10 own heads within 5 11 life(rounds) 12 end(0 alive, 1+cause: 1 sac 2 trap
//   3 rammed 4 ram 5 enemyBody 6 allyHead 7 fault 8 sprintDeath) 13 final length 14 max length 15 steps 16 natural eaten 17 in own
//   territory 18 in enemy territory 19 own drops eaten 20 enemy drops eaten 21 sprint cost 22 splits 23 mass to children 24 turns
//   25 turns in own territory 26 in enemy territory 27 natural eaten within 30 rounds 28 alive 30 rounds on (or at the end)
//   29 death drops 30 eaten by own 31 by own >=8 32 by the opponent 33 nearest own >=8 head at the last turn 34 its max over life
//   (99 never one) 35 ten turns before the last 36 spawns it was the unique nearest head of within 30 rounds 37 of those eaten by it
//   38 turns in conv state 39 turns in feed state 40 death drops eaten by own pieces (<=4) 41 by own dragons longer than it
//   42 dragon id 43 team units at birth
// Formation: per turn histograms of pieces' nearest big ally, nearest own head and own heads within 5; big allies' pieces
//   within 5; every 10 rounds (first turn): Voronoi of all heads over static paths (capacity = expected spawns per round
//   from the layout file), own-territory share, unclaimed and enemy-nearer capacity, service distance, cell capacity per head.
// Natural spawns: nearest head of each team (static path, <= 12), unique nearest head, eater.
// Deaths (dt): phase|cause|length class (<=4, 5-7, >=8)|nearest own head within Manhattan 3 (0, S <8, B >=8)|mech (s = a stub
//   left by its own split within 2 rounds with <= 3 segments, n = born by a split within 2 rounds, o = other; mass ledger)
//   -> [n, length, pearls, own, own piece, own mid, own big, opponent, delay sum of own eats].
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const X = require(path.join(ROOT, 'exp', 'territory-analysis', 'extract.js'));
const TOP = path.join(ROOT, 'data', 'top'), ONLINE = path.join(ROOT, 'data', 'online'), CACHE = path.join(ROOT, '.cache', 'supply-chain');
let parseInd = null;
const NB = 50;
const phaseOf = r => r < 100 ? 0 : r < 250 ? 1 : r < 350 ? 2 : r < 450 ? 3 : 4;
const binOf = r => Math.max(0, Math.min(NB - 1, Math.floor(r / 10)));
// histogram bins
const bDist = m => m <= 3 ? 0 : m <= 5 ? 1 : m <= 8 ? 2 : m <= 12 ? 3 : m <= 20 ? 4 : m < 99 ? 5 : 6;       // nearest big ally
const bNnd = m => m <= 1 ? 0 : m === 2 ? 1 : m === 3 ? 2 : m <= 5 ? 3 : m <= 8 ? 4 : m < 99 ? 5 : 6;       // nearest own head
const bCnt5 = n => n === 0 ? 0 : n === 1 ? 1 : n === 2 ? 2 : n <= 4 ? 3 : n <= 8 ? 4 : 5;                   // own heads within 5
const bPc = n => n === 0 ? 0 : n === 1 ? 1 : n === 2 ? 2 : n <= 4 ? 3 : 4;                                     // pieces near a big
const bKd = m => m <= 3 ? 0 : m <= 5 ? 1 : m <= 8 ? 2 : m <= 15 ? 3 : 4;                                      // gather: to the king
const bCell = v => v < 0.5 ? 0 : v < 1 ? 1 : v < 2 ? 2 : v < 4 ? 3 : v < 8 ? 4 : v < 16 ? 5 : 6;             // cell spawns / 30 rounds
const lc3 = L => L <= 4 ? 0 : L <= 7 ? 1 : 2;
const TAGCODE = { csplit: 1, frag: 2, bsplit: 3, split: 4, escsplit: 5, escsplit2: 6, pocket: 7 };

function analyse(R, info, debug) {
  if (!parseInd) parseInd = require(path.join(ROOT, 'tools', 'mech_check.js')).parseInd;
  const G = X.geometry(R), W = G.W, H = G.H, N = G.N, NBT = G.nb, TERR = G.terr;
  const M = R.match.map, nInit = M.initialDragons.length;
  const linfo = { map: info.map }; if (info.map === 'Prisoners Dilemma') linfo.variant = nInit === 10 ? 'PD10' : 'PD6';
  const vt = X.variantOf(info.map, info.gameId, R, nInit);
  const lf = X.fileOf(info.map, vt.tag), gg = lf && fs.existsSync(lf) ? X.gapsOfFile(lf) : null;
  const WGT = new Float64Array(N); let layoutOk = 0;
  if (gg && gg.w === W && gg.h === H) { layoutOk = 1; for (let k = 0; k < N; k++) { const q = gg.g[k]; if (q && q[1] > 0) WGT[k] = 1 / Math.max(1, (q[0] + q[1]) / 2); } }
  const capTerr = [0, 0, 0]; for (let k = 0; k < N; k++) capTerr[TERR[k]] += WGT[k];
  const us = info.us || null;
  const TI = tm => tm === 'A' ? 0 : 1;
  const rel = (k, ti) => TERR[k] === 0 ? 1 : TERR[k] === ti + 1 ? 0 : 2;   // 0 own, 1 neutral, 2 enemy territory
  const K = p => p.y * W + p.x;

  // ---- per-team aggregates
  const T = [0, 1].map(() => ({ b: {}, h: {}, ep: {}, dr: {}, sp: {}, dt: {}, cp: {}, tag: {} }));
  const addB = (ti, name, r, v = 1) => { const a = T[ti].b[name] || (T[ti].b[name] = new Array(NB).fill(0)); a[binOf(r)] += v; };
  const addH = (ti, name, ph, bin, nb, v = 1) => { const a = T[ti].h[name] || (T[ti].h[name] = new Array(5 * nb).fill(0)); a[ph * nb + bin] += v; };
  const addK = (obj, key, vals) => { const a = obj[key] || (obj[key] = new Array(vals.length).fill(0)); for (let i = 0; i < vals.length; i++) a[i] += vals[i]; };
  const addTag = (ti, name, r, v = 1) => { const a = T[ti].tag[name] || (T[ti].tag[name] = new Array(NB).fill(0)); a[binOf(r)] += v; };
  // episodes: [episodes, fired, tagFired, left, diedOther, gameEnd, ok, okBig, turns]
  const EPN = ['cs', 'csE', 'fs', 'fsK', 'fsG'];
  const epAdd = (ti, e, ph, i, v = 1) => { const a = T[ti].ep[e] || (T[ti].ep[e] = new Array(5 * 9).fill(0)); a[ph * 9 + i] += v; };

  // ---- BFS scratch
  const ST = new Int32Array(N), DD = new Int16Array(N), Q = new Int32Array(N); let stamp = 0;
  const found = [];
  let ctx = null;
  const headIdAt = u => { const o = ctx.occ.get(u); if (o === undefined) return -1; const od = ctx.drag.get(o); if (!od) return -1; const h = od.body[0]; return h.y * W + h.x === u ? o : -1; };
  // own heads reachable from d's head through free tiles and d's own body, within maxD (plan.cpp conv / feed BFS, reversed)
  function nearAllies(d, maxD) {
    stamp++; let qh = 0, qt = 0; const src = K(d.body[0]); Q[qt++] = src; ST[src] = stamp; DD[src] = 0; found.length = 0;
    while (qh < qt) {
      const t = Q[qh++], dd = DD[t]; if (dd >= maxD) continue;
      for (let j = 0; j < 4; j++) {
        const u = NBT[t * 4 + j]; if (u < 0 || ST[u] === stamp) continue; ST[u] = stamp;
        const o = ctx.occ.get(u);
        if (o === undefined || o === d.id) { DD[u] = dd + 1; Q[qt++] = u; continue; }
        const od = ctx.drag.get(o); if (!od || od.team !== d.team) continue;
        const hh = od.body[0]; if (hh.y * W + hh.x !== u) continue;
        found.push(od, dd + 1);
      }
    }
  }
  // nearest head of each team from tile k over static paths (bodies ignored), up to maxD; unique nearest head id
  const nearOut = { d: [99, 99], id: -1, tie: 0, best: 99 };
  function nearestHeads(k, maxD) {
    stamp++; let qh = 0, qt = 0; Q[qt++] = k; ST[k] = stamp; DD[k] = 0;
    const dT = nearOut.d; dT[0] = 99; dT[1] = 99; let best = 99, bestId = -1, tie = 0;
    while (qh < qt) {
      const t = Q[qh++], dd = DD[t];
      if (dd > best && dT[0] < 99 && dT[1] < 99) break;
      const id = headIdAt(t);
      if (id >= 0) {
        const ti = TI(ctx.drag.get(id).team);
        if (dd < dT[ti]) dT[ti] = dd;
        if (dd < best) { best = dd; bestId = id; tie = 0; } else if (dd === best && id !== bestId) tie = 1;
      }
      if (dd >= maxD) continue;
      for (let j = 0; j < 4; j++) { const u = NBT[t * 4 + j]; if (u < 0 || ST[u] === stamp) continue; ST[u] = stamp; DD[u] = dd + 1; Q[qt++] = u; }
    }
    nearOut.id = tie ? -1 : bestId; nearOut.tie = tie; nearOut.best = best;
    return nearOut;
  }
  const chebHead = (k, ti) => { // a head of team ti within Chebyshev 3 of tile k
    const x = k % W, y = (k / W) | 0;
    for (const o of ctx.drag.values()) { if (TI(o.team) !== ti) continue; const h = o.body[0]; let dx = Math.abs(h.x - x), dy = Math.abs(h.y - y); if (dx > W - dx) dx = W - dx; if (dy > H - dy) dy = H - dy; if (dx <= 3 && dy <= 3) return 1; }
    return 0;
  };

  // ---- state
  const SS = new Map();        // dragon id -> { r, cs, csE, csV, fs, fsK, fsG, gs, dK, ep: {e: {r0, tag}} }
  const bornLen = new Map();   // dragon id -> length at birth (children only)
  const lastInd = new Map();   // our dragon id -> { r, text }
  const piece = new Map();     // live piece id -> record
  const pieces = [];           // all piece records
  const DE = new Map();        // death idx -> [[team index, eater id, eater length, round], ...]
  const firedRecs = [];        // [ti, e, ph, death idx, deadLen]
  const tagDeaths = [];        // [ti, 'conv'|'feed', ph, death idx, inState, deadLen, targetId]
  const pendingDrops = [];     // { idx, tiles, r, ti, cause, L }
  const drops = new Map();     // tile:idx -> drop record
  const liveDrops = [];
  const spawnRec = new Map();  // tile -> spawn record (live natural pearls from r >= 0 spawns)
  const spawns = [];
  const known = new Set();     // tiles of natural pearls already registered
  let curR = -2, roundsSeen = 0;
  const chk = { piece: 0, head: 0, dropMiss: 0 };
  const tagMiss = { conv: 0, feed: 0 };
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) known.add(i);
  const roundFlag = [{}, {}];

  function processDrops() {
    while (pendingDrops.length) {
      const p = pendingDrops.shift();
      for (const k of p.tiles) {
        if (ctx.pearls.get(k) !== p.idx) continue;
        const key = k + ':' + p.idx; if (drops.has(key)) continue;
        const rec = { k, idx: p.idx, r: p.r, ti: p.ti, cause: p.cause, L: p.L, dmin: [99, 99], w6: [-1, -1], view: [0, 0], cont: 0, eat: null, grab: 0, grabR: -1 };
        const o = nearestHeads(k, 6);
        for (let t = 0; t < 2; t++) { rec.dmin[t] = o.d[t]; if (o.d[t] <= 6) rec.w6[t] = p.r; rec.view[t] = chebHead(k, t); }
        rec.d0 = [o.d[0], o.d[1]];
        drops.set(key, rec); liveDrops.push(rec);
      }
    }
  }
  function newRound(r) {
    curR = r; roundsSeen++;
    processDrops();
    // natural spawns (appear at the round start, before any move)
    for (const [k, o] of ctx.pearls) {
      if (o !== -1 || known.has(k)) continue;
      known.add(k);
      const q = nearestHeads(k, 12);
      const rec = { k, r, dA: q.d[0], dB: q.d[1], id: q.id, idLen: q.id >= 0 ? ctx.drag.get(q.id).body.length : 0, eat: null };
      spawnRec.set(k, rec); spawns.push(rec);
      if (q.id >= 0) { const pc = piece.get(q.id); if (pc && r <= pc.born + 30) { pc.claim30++; rec.pc = pc; } }
    }
    // fresh drops: nearest heads at the next GRAB_ROUNDS round starts
    for (let i = liveDrops.length - 1; i >= 0; i--) {
      const x = liveDrops[i];
      if (x.eat || r - x.r > 6) { liveDrops.splice(i, 1); continue; }
      const o = nearestHeads(x.k, 6);
      for (let t = 0; t < 2; t++) { if (o.d[t] < x.dmin[t]) x.dmin[t] = o.d[t]; if (o.d[t] <= 6 && x.w6[t] < 0) x.w6[t] = r; }
    }
    if (r % 10 === 0 && r >= 0 && r < 500) checkpoint(r);
  }

  // ---- Voronoi checkpoint (static paths, bodies ignored)
  const DA = new Int16Array(N), DBt = new Int16Array(N), OD = new Int16Array(N), OW1 = new Int32Array(N), OW2 = new Int32Array(N);
  function teamDist(ti, out) {
    out.fill(-1); let qh = 0, qt = 0;
    for (const o of ctx.drag.values()) { if (TI(o.team) !== ti) continue; const k = K(o.body[0]); if (out[k] < 0) { out[k] = 0; Q[qt++] = k; } }
    while (qh < qt) { const t = Q[qh++]; for (let j = 0; j < 4; j++) { const u = NBT[t * 4 + j]; if (u < 0 || out[u] >= 0) continue; out[u] = out[t] + 1; Q[qt++] = u; } }
  }
  function checkpoint(r) {
    teamDist(0, DA); teamDist(1, DBt);
    OD.fill(-1); OW1.fill(-1); OW2.fill(-1);
    let qh = 0, qt = 0;
    const heads = [];
    for (const o of ctx.drag.values()) { const k = K(o.body[0]); heads.push(o); if (OD[k] < 0) { OD[k] = 0; OW1[k] = o.id; Q[qt++] = k; } }
    while (qh < qt) {
      const t = Q[qh++], dn = OD[t] + 1;
      for (let j = 0; j < 4; j++) {
        const u = NBT[t * 4 + j]; if (u < 0) continue;
        if (OD[u] < 0) { OD[u] = dn; OW1[u] = OW1[t]; OW2[u] = OW2[t]; Q[qt++] = u; }
        else if (OD[u] === dn) {
          for (const w of [OW1[t], OW2[t]]) { if (w < 0 || w === OW1[u] || w === OW2[u]) continue; if (OW2[u] < 0) OW2[u] = w; }
        }
      }
    }
    const cell = new Map();
    for (let k = 0; k < N; k++) { const w = WGT[k]; if (!w || OW1[k] < 0) continue; if (OW2[k] >= 0) { cell.set(OW1[k], (cell.get(OW1[k]) || 0) + w / 2); cell.set(OW2[k], (cell.get(OW2[k]) || 0) + w / 2); } else cell.set(OW1[k], (cell.get(OW1[k]) || 0) + w); }
    for (let ti = 0; ti < 2; ti++) {
      const own = ti + 1, dO = ti === 0 ? DA : DBt, dE = ti === 0 ? DBt : DA;
      let vor = 0, unc = 0, ecl = 0, svc = 0, cap = capTerr[own];
      for (let k = 0; k < N; k++) {
        if (TERR[k] !== own) continue; const w = WGT[k]; if (!w) continue;
        const a = dO[k] < 0 ? 999 : dO[k], b = dE[k] < 0 ? 999 : dE[k];
        vor += w * (a < b ? 1 : a === b ? 0.5 : 0); if (a > 6 && b > 6) unc += w; if (b < a) ecl += w; svc += w * Math.min(a, 30);
      }
      const units = heads.filter(o => TI(o.team) === ti);
      const c = T[ti].cp, i = r / 10;
      const put = (name, v) => { const a = c[name] || (c[name] = new Array(NB).fill(null)); a[i] = v; };
      put('units', units.length); put('pieces', units.filter(o => o.body.length <= 4).length); put('bigs', units.filter(o => o.body.length >= 8).length);
      put('pEn', units.filter(o => o.body.length <= 4 && rel(K(o.body[0]), ti) === 2).length); put('pNe', units.filter(o => o.body.length <= 4 && rel(K(o.body[0]), ti) === 1).length);
      if (cap > 0) { put('vor', Math.round(1000 * vor / cap)); put('unc', Math.round(1000 * unc / cap)); put('ecl', Math.round(1000 * ecl / cap)); put('svc', Math.round(100 * svc / cap)); }
      let cp0 = 0, cp1 = 0, cp2 = 0;
      for (const o of units) {
        const v = (cell.get(o.id) || 0) * 30, l3 = lc3(o.body.length);
        if (l3 === 0) cp0 += v; else if (l3 === 1) cp1 += v; else cp2 += v;
        addH(ti, 'cell' + l3, phaseOf(r), bCell(v), 7);
      }
      put('cellP', Math.round(10 * cp0)); put('cellM', Math.round(10 * cp1)); put('cellB', Math.round(10 * cp2));
    }
  }

  // ---- hooks
  const hooks = {
    turn(d, r, c) {
      ctx = c;
      if (r !== curR) newRound(r);
      else processDrops();
      const tm = d.team, ti = TI(tm), L = d.body.length, h = d.body[0], hx = h.x, hy = h.y, ph = phaseOf(r);
      let units = 0, kingLen = -1, kingId = 1e9, king = null, eView = 0, eNear4 = 0, dBig = 99, nnd = 99, n3 = 0, n5 = 0, big3 = 0, long5 = 0, pn5 = 0;
      for (const o of c.drag.values()) {
        const oh = o.body[0];
        let dx = oh.x - hx; if (dx < 0) dx = -dx; if (dx > W - dx) dx = W - dx;
        let dy = oh.y - hy; if (dy < 0) dy = -dy; if (dy > H - dy) dy = H - dy;
        if (o.team !== tm) { if (dx <= 3 && dy <= 3) eView = 1; if (dx + dy <= 4) eNear4 = 1; continue; }
        units++;
        const ol = o.body.length;
        if (ol > kingLen || (ol === kingLen && o.id < kingId)) { kingLen = ol; kingId = o.id; king = o; }
        if (o === d) continue;
        const m = dx + dy;
        if (m < nnd) nnd = m;
        if (m <= 3) n3++;
        if (m <= 5) n5++;
        if (ol >= 8 && m < dBig) dBig = m;
        if (L <= 4 && ol >= 8 && ol >= L + 4 && dx <= 3 && dy <= 3) big3 = 1;   // plan.cpp: allies in the 7x7 view (allyHeadsNow)
        if (ol > L && dx <= 3 && dy <= 3) long5 = 1;
        if (ol <= 4 && m <= 5) pn5++;
      }
      const isKing = kingId === d.id;
      // BFS through free tiles (conv <= 3, feed <= 5)
      let convD = 99, feedD = 99, feedK = 99;
      const wantFeed = r >= 250 && long5 && !isKing;
      if ((L >= 2 && L <= 4 && big3) || wantFeed) {
        nearAllies(d, wantFeed ? 5 : 3);
        for (let i = 0; i < found.length; i += 2) {
          const o = found[i], dd = found[i + 1], ol = o.body.length, oh = o.body[0];
          let vx = Math.abs(oh.x - hx), vy = Math.abs(oh.y - hy); if (vx > W - vx) vx = W - vx; if (vy > H - vy) vy = H - vy;
          if (vx > 3 || vy > 3) continue;                                   // in view only (vision does not cross portals)
          if (L <= 4 && ol >= 8 && ol >= L + 4 && dd <= 3 && dd < convD) convD = dd;
          if (ol > L && dd < feedD) feedD = dd;
          if (o === king && dd < feedK) feedK = dd;
        }
      }
      const young = d.parent >= 0 && (bornLen.get(d.id) || 99) <= 2 && r - d.born < 20;
      const stub = d.lastSplitR >= r - 3 && d.lastSplitKept <= 3;
      const csGeo = L >= 2 && convD <= 3, cs = csGeo && !eView;
      const csE = cs && r >= 300 && units >= 3 && !young && !stub, csV = csGeo && eView === 1;
      const csN = L >= 2 && L <= 4 && !csGeo && dBig <= 6;
      const fs = r >= 250 && !isKing && L >= 2 && feedD <= 5 && !eNear4 && units >= 3;
      const fsK = fs && feedK <= 5, fsG = fs && units >= 4 && L >= 4;
      const gs = r >= 340 && !isKing && L >= 4 && units >= 4 && king;
      let dK = 99;
      if (gs) { const kh = king.body[0]; let dx = Math.abs(kh.x - hx), dy = Math.abs(kh.y - hy); if (dx > W - dx) dx = W - dx; if (dy > H - dy) dy = H - dy; dK = dx + dy; }
      // aggregates
      addB(ti, 'turns', r); addB(ti, ['turnsP', 'turnsM', 'turnsB'][lc3(L)], r);
      if (cs) addB(ti, 'cs', r); if (csE) addB(ti, 'csE', r); if (csV) addB(ti, 'csV', r); if (csN) addB(ti, 'csN', r);
      if (fs) addB(ti, 'fs', r); if (fsK) addB(ti, 'fsK', r); if (fsG) addB(ti, 'fsG', r);
      const rf = roundFlag[ti];
      if (cs && rf.cs !== r) { rf.cs = r; addB(ti, 'csR', r); }
      if (fs && rf.fs !== r) { rf.fs = r; addB(ti, 'fsR', r); }
      if (rf.t !== r) { rf.t = r; addB(ti, 'rounds', r); }
      const prev = SS.get(d.id);
      if (gs) {
        addB(ti, 'gs', r); addB(ti, 'gsK' + bKd(dK), r);
        if (prev && prev.gs && prev.r === r - 1 && prev.dK < 99) { addB(ti, 'gsPrev', r); if (dK < prev.dK) addB(ti, 'gsApp', r); }
      }
      if (L <= 4) { addH(ti, 'pBig', ph, bDist(dBig), 7); addH(ti, 'pNnd', ph, bNnd(nnd), 7); addH(ti, 'pN5', ph, bCnt5(n5), 6); }
      if (L >= 8) addH(ti, 'bPc5', ph, bPc(pn5), 5);
      // episodes
      const st = { r, cs, csE, fs, fsK, fsG, gs: !!gs, dK, ep: prev ? prev.ep : {} };
      const flags = { cs, csE, fs, fsK, fsG };
      for (const e of EPN) {
        const now = flags[e], open = st.ep[e];
        if (now) {
          if (!open || !(prev && prev.r === r - 1)) { if (open) epAdd(ti, e, open.ph, 3); st.ep[e] = { r0: r, ph, tag: 0 }; epAdd(ti, e, ph, 0); }
          epAdd(ti, e, st.ep[e].ph, 8);
        } else if (open) { epAdd(ti, e, open.ph, 3); st.ep[e] = null; }
      }
      SS.set(d.id, st);
      // pieces
      const pc = piece.get(d.id);
      if (pc) {
        pc.turns++; const rr = rel(K(h), ti); if (rr === 0) pc.tOwn++; else if (rr === 2) pc.tEnemy++;
        if (dBig < 99) pc.dBigMax = pc.dBigMax === 99 ? dBig : Math.max(pc.dBigMax, dBig);
        pc.ring[pc.ringN % 11] = dBig; pc.ringN++;
        if (cs) pc.csT++; if (fs) pc.fsT++;
        if (L > pc.maxL) pc.maxL = L;
      }
    },
    indicator(e, r, c) {
      ctx = c;
      const d = c.drag.get(e.id); if (!d || d.team !== us) return;
      lastInd.set(e.id, { r, text: e.text || '' });
      const ti = TI(us), st = SS.get(e.id), inR = st && st.r === r;
      const t = parseInd(e.text || '');
      if (t.kind === 'conv') {
        addTag(ti, 'conv', r); if (inR && st.cs) addTag(ti, 'convCs', r); if (inR && st.csE) addTag(ti, 'convCsE', r);
        if (inR && !st.cs) { const L = d.body.length; addTag(ti, L > 4 ? 'convOutLen' : 'convOutGeo', r); }
        if (inR) for (const k of ['cs', 'csE']) if (st[k] && st.ep[k]) st.ep[k].tag = 1;
      } else if (t.kind === 'feed' || t.kind === 'k2') {
        addTag(ti, 'feed', r); if (inR && st.fs) addTag(ti, 'feedFs', r); if (inR && st.fsK) addTag(ti, 'feedFsK', r);
        if (inR) for (const k of ['fs', 'fsK', 'fsG']) if (st[k] && st.ep[k]) st.ep[k].tag = 1;
      } else if (t.kind === 'move') {
        if (t.goal) { addTag(ti, 'g', r); if (inR && st.gs) addTag(ti, 'gGs', r); }
        if (t.fg) addTag(ti, 'F', r);
      }
      const g = /(?:^|\s)grab@(\d+),(\d+)(?:\s|$)/.exec(e.text || '');
      if (g) {
        addTag(ti, 'grabT', r);
        const k = (+g[2]) * W + (+g[1]), o = c.pearls.has(k) ? c.pearls.get(k) : null;
        if (o !== null && o >= 0) { processDrops(); const x = drops.get(k + ':' + o); if (x) { if (!x.grab) x.grabR = r; x.grab++; } else addTag(ti, 'grabNoRec', r); }
        else addTag(ti, o === -1 ? 'grabNat' : 'grabGone', r);
      }
    },
    action(d, e, r, c, before) {
      ctx = c;
      const pc = piece.get(d.id); if (!pc) return;
      const a = e.action;
      if (a && a.kind === 'move') pc.steps += d.fate ? d.fate.step : a.steps.length;
      if (d.body.length > pc.maxL) pc.maxL = d.body.length;
    },
    eat(d, k, o, r, c) {
      ctx = c;
      processDrops();
      const ti = TI(d.team), pc = piece.get(d.id);
      if (o < 0) {
        known.delete(k);                                   // a later spawn on this tile is a new one
        const s = spawnRec.get(k);
        if (s) { s.eat = [ti, d.id, r]; spawnRec.delete(k); if (s.pc && s.pc === pc) pc.claimEat30++; }
        if (pc) { pc.nat++; const rr = rel(k, ti); if (rr === 0) pc.natOwn++; else if (rr === 2) pc.natEnemy++; if (r <= pc.born + 30) pc.n30++; }
      } else {
        let a = DE.get(o); if (!a) DE.set(o, a = []); a.push([ti, d.id, d.body.length, r]);
        const x = drops.get(k + ':' + o); if (x) x.eat = [ti, d.id, d.body.length, r]; else chk.dropMiss++;
        if (pc) { if (TI(c.deaths[o].team) === ti) pc.dOwn++; else pc.dEnemy++; }
      }
    },
    split(p, ch, e, r, c) {
      ctx = c;
      processDrops();
      bornLen.set(ch.id, ch.body.length);
      const ti = TI(p.team), pp = piece.get(p.id);
      if (pp) { pp.splitsN++; pp.C += ch.body.length; }
      if (ch.body.length > 3) return;
      const h = ch.body[0], hk = K(h);
      let dBig = 99, nnd = 99, n5 = 0, eView = 0, kingLen = -1, kingId = 1e9, bu = 0;
      for (const o of c.drag.values()) {
        const oh = o.body[0];
        let dx = Math.abs(oh.x - h.x), dy = Math.abs(oh.y - h.y); if (dx > W - dx) dx = W - dx; if (dy > H - dy) dy = H - dy;
        if (o.team !== p.team) { if (dx <= 3 && dy <= 3) eView = 1; continue; }
        bu++;
        if (o !== ch) { const ol = o.body.length, m = dx + dy; if (m < nnd) nnd = m; if (m <= 5) n5++; if (ol >= 8 && m < dBig) dBig = m; }
        const ol = o === p ? p.body.length + ch.body.length : o.body.length; // the parent before the split
        if (ol > kingLen || (ol === kingLen && o.id < kingId)) { kingLen = ol; kingId = o.id; }
      }
      let cls = 0;
      if (p.team === us) { const li = lastInd.get(p.id); const t = li && li.r === r ? parseInd(li.text) : null; cls = t ? (TAGCODE[t.kind] || 9) : 9; }
      const pl = p.body.length + ch.body.length;
      const rec = { ti, id: ch.id, born: r, bl: ch.body.length, pl, cls, pk: kingId === p.id ? 1 : 0, bt: rel(hk, ti), bv: eView, bdBig: dBig, bnnd: nnd, bn5: n5,
        turns: 0, tOwn: 0, tEnemy: 0, steps: 0, nat: 0, natOwn: 0, natEnemy: 0, dOwn: 0, dEnemy: 0, n30: 0, maxL: ch.body.length, splitsN: 0, C: 0,
        dBigMax: 99, ring: new Int16Array(11).fill(99), ringN: 0, csT: 0, fsT: 0, claim30: 0, claimEat30: 0, end: 0, Lf: 0, deathIdx: -1, deathR: -1, bu };
      piece.set(ch.id, rec); pieces.push(rec);
    },
    death(d, rec, idx, other, r, c) {
      ctx = c;                                             // drops of an earlier death wait for the next hook (the mover of a head-on is still here)
      const ti = TI(d.team), ph = phaseOf(r);
      pendingDrops.push({ idx, tiles: d.body.map(K), r, ti, cause: rec.cause, L: d.body.length });
      const st = SS.get(d.id), inR = st && st.r === r;
      if (st) for (const e of EPN) {
        const open = st.ep[e]; if (!open) continue;
        if (rec.cause === 0 && inR && st[e]) { epAdd(ti, e, open.ph, 1); if (open.tag) epAdd(ti, e, open.ph, 2); firedRecs.push([ti, e, open.ph, idx, d.body.length]); }
        else epAdd(ti, e, open.ph, 4);
        st.ep[e] = null;
      }
      if (rec.cause === 0) { addB(ti, 'sac', r); if (d.body.length <= 4) addB(ti, 'sacP', r); if (inR && st.cs) addB(ti, 'sacCs', r); if (inR && st.fs) addB(ti, 'sacFs', r); }
      if (d.team === us) {
        const li = lastInd.get(d.id);
        if (li && li.r === r) {
          const t = parseInd(li.text);
          if (t.kind === 'conv' || t.kind === 'feed' || t.kind === 'k2') tagDeaths.push([ti, t.kind === 'conv' ? 'conv' : 'feed', ph, idx, inR ? (t.kind === 'conv' ? (st.cs ? 1 : 0) : (st.fs ? 1 : 0)) : -1, d.body.length, t.target]);
        }
      }
      const pc = piece.get(d.id);
      if (pc) { pc.end = 1 + rec.cause; pc.Lf = d.body.length; pc.deathIdx = idx; pc.deathR = r; piece.delete(d.id); }
    },
    end(n, c) {
      ctx = c;
      processDrops();
      for (const [id, st] of SS) {
        const d = c.drag.get(id); if (!d) continue;
        for (const e of EPN) if (st.ep[e]) { epAdd(TI(d.team), e, st.ep[e].ph, 5); st.ep[e] = null; }
      }
      for (const [id, pc] of piece) { const d = c.drag.get(id); pc.end = 0; pc.Lf = d ? d.body.length : 0; pc.deathR = n; }
    },
  };
  const g = ML.perGame(R, linfo, hooks);
  const rounds = g.rounds;
  const deaths = ctx ? ctx.deaths : [];
  const allD = ctx ? ctx.all : new Map();

  // ---- death drops: who ate them
  const eatSplit = (idx, ti) => { // [own, ownPiece, ownMid, ownBig, enemy, delaySumOwn]
    const a = DE.get(idx) || [], o = [0, 0, 0, 0, 0, 0];
    for (const q of a) { if (q[0] === ti) { o[0]++; o[1 + lc3(q[2])]++; o[5] += q[3] - deaths[idx].r; } else o[4]++; }
    return o;
  };
  // episodes fired: success
  for (const [ti, e, ph, idx, L] of firedRecs) {
    const x = eatSplit(idx, ti), drops = Math.ceil(L / 2);
    if (x[0] * 2 >= drops && x[4] === 0) epAdd(ti, e, ph, 6);
    if (x[3] * 2 >= drops) epAdd(ti, e, ph, 7);
  }
  // our labelled conv / feed deaths: [n, inState, drops, own, ownBig, enemy, target ate >= 1, ok]
  for (const [ti, k, ph, idx, inS, L, target] of tagDeaths) {
    const x = eatSplit(idx, ti), drops = Math.ceil(L / 2), tAte = (DE.get(idx) || []).some(q => q[1] === target) ? 1 : 0;
    addK(T[ti].tag, k + 'Death|' + ph, [1, inS === 1 ? 1 : 0, drops, x[0], x[3], x[4], tAte, x[0] * 2 >= drops && x[4] === 0 ? 1 : 0]);
  }
  // deaths by cause x length class x phase x nearest own head within 3 (0 none, S shorter than 8, B >= 8) -> drops eaten
  for (let i = 0; i < deaths.length; i++) {
    const x = deaths[i], ti = TI(x.team), e = eatSplit(i, ti);
    addK(T[ti].dt, phaseOf(x.r) + '|' + x.cause + '|' + lc3(x.len) + '|' + x.near + '|' + (x.mech === 'stub' ? 's' : x.mech === 'newborn' ? 'n' : 'o'), [1, x.len, x.drops, e[0], e[1], e[2], e[3], e[4], e[5]]);
  }
  // drops by the team that sees them: phase|origin (0 own, 1 enemy)|cause group|within6|view|contested ->
  //   [n, eatenOwn, eatenEnemy, none, eatenOwnPiece, eatenOwnMid, eatenOwnBig, delaySumOwn, grabbed(ours), grabbedEatenOwn, firstWithin6 delay sum]
  const cgrp = c => c === 0 ? 0 : c === 1 ? 1 : c === 2 || c === 3 ? 2 : 3;
  for (const x of drops.values()) {
    for (let ti = 0; ti < 2; ti++) {
      const w6 = x.w6[ti] >= 0 ? 1 : 0, cont = x.dmin[1 - ti] <= x.dmin[ti] ? 1 : 0;
      const key = phaseOf(x.r) + '|' + (x.ti === ti ? 0 : 1) + '|' + cgrp(x.cause) + '|' + w6 + '|' + x.view[ti] + '|' + cont;
      const e = x.eat, own = e && e[0] === ti ? 1 : 0, en = e && e[0] !== ti ? 1 : 0;
      const gb = us && ti === TI(us) ? (x.grab ? 1 : 0) : 0;
      addK(T[ti].dr, key, [1, own, en, e ? 0 : 1, own && lc3(e[2]) === 0 ? 1 : 0, own && lc3(e[2]) === 1 ? 1 : 0, own && lc3(e[2]) === 2 ? 1 : 0, own ? e[3] - x.r : 0, gb, gb && own ? 1 : 0, w6 ? x.w6[ti] - x.r : 0]);
    }
  }
  // natural spawns by team: phase|territory (0 own, 1 neutral, 2 enemy)|race (0 own nearer, 1 tie, 2 enemy nearer, 3 none <= 12)|
  //   unique nearest head of ours: length class (0-2) or 3 -> [n, eatenOwn, eatenEnemy, eatenByUniqueNearest]
  for (const s of spawns) {
    for (let ti = 0; ti < 2; ti++) {
      const dO = ti === 0 ? s.dA : s.dB, dE = ti === 0 ? s.dB : s.dA;
      const race = dO >= 99 && dE >= 99 ? 3 : dO < dE ? 0 : dO === dE ? 1 : 2;
      let cls = 3; if (s.id >= 0) { const o = allD.get(s.id); if (o && TI(o.team) === ti) cls = lc3(s.idLen); }
      const e = s.eat;
      addK(T[ti].sp, phaseOf(s.r) + '|' + rel(s.k, ti) + '|' + race + '|' + cls, [1, e && e[0] === ti ? 1 : 0, e && e[0] !== ti ? 1 : 0, e && e[1] === s.id ? 1 : 0]);
    }
  }
  // pieces: final fields; identity: bl + eaten - sprint - children = final length
  const P = [];
  for (const pc of pieces) {
    const d = allD.get(pc.id);
    let spr = 0; if (d) for (let q = 1; q < d.costs.length; q += 2) spr += d.costs[q];
    let eaten = 0; if (d) eaten = d.eats.length / 3;
    if (pc.bl + eaten - spr - pc.C !== pc.Lf) chk.piece++;
    const dead = pc.end > 0;
    const dropsN = dead ? Math.ceil(pc.Lf / 2) : 0;
    let eOwn = 0, eOwnBig = 0, eEnemy = 0, eOwnP = 0, eLonger = 0;
    if (dead) for (const q of DE.get(pc.deathIdx) || []) { if (q[0] === pc.ti) { eOwn++; if (q[2] >= 8) eOwnBig++; if (q[2] <= 4) eOwnP++; if (q[2] > pc.Lf) eLonger++; } else eEnemy++; }
    const life = pc.deathR - pc.born;
    const ringAt = back => pc.ringN > back ? pc.ring[(pc.ringN - 1 - back) % 11] : 99;
    P.push([pc.ti, pc.born, pc.bl, pc.pl, pc.cls, pc.pk, pc.bt, pc.bv, pc.bdBig, pc.bnnd, pc.bn5, life, pc.end, pc.Lf, pc.maxL, pc.steps,
      pc.nat, pc.natOwn, pc.natEnemy, pc.dOwn, pc.dEnemy, spr, pc.splitsN, pc.C, pc.turns, pc.tOwn, pc.tEnemy, pc.n30,
      life >= 30 || (!dead) ? 1 : 0, dropsN, eOwn, eOwnBig, eEnemy, ringAt(0), pc.dBigMax, ringAt(10), pc.claim30, pc.claimEat30, pc.csT, pc.fsT, eOwnP, eLonger, pc.id, pc.bu]);
  }
  const team = ti => { const tm = ti === 0 ? 'A' : 'B'; return { b: T[ti].b, h: T[ti].h, ep: T[ti].ep, dr: T[ti].dr, sp: T[ti].sp, dt: T[ti].dt, cp: T[ti].cp, tag: T[ti].tag,
    splits: g[tm].splits, sonar: g[tm].sonar, faults: deaths.filter(x => x.team === tm && x.cause === 6).length }; };
  if (debug) debug.drops = drops;
  return { rounds, endReason: g.endReason, winner: g.winner, W, H, variant: vt.tag, layoutOk, capTerr: capTerr.map(v => Math.round(1000 * v) / 1000),
    chk: { ...g.chk, ...chk }, A: team(0), B: team(1), P };
}

// ---------------------------------------------------------------------------------------------------------------
// Tasks and workers (as exp/territory-analysis/extract.js)
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];
function topTasks(keysArg) {
  const seen = new Set(), idx = [];
  for (const r of readJsonl(path.join(TOP, 'index.jsonl'))) { const k = r.battleId + ':' + r.gameId; if (seen.has(k)) continue; seen.add(k); idx.push(r); }
  const byKey = new Map(idx.map(r => [r.battleId + ':' + r.gameId, r]));
  const keys = fs.readFileSync(path.resolve(ROOT, keysArg), 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  const out = [];
  for (const k of keys) {
    const r = byKey.get(k); if (!r) continue;
    const f = path.join(TOP, String(r.battleId), r.gameId + '.replay.gz'); if (!fs.existsSync(f)) continue;
    out.push({ key: k, file: f, info: { src: 'top', map: r.map, gameId: r.gameId, battleId: r.battleId, teamA: r.teamA, teamB: r.teamB, eloA: r.eloA, eloB: r.eloB,
      rankA: r.rankA, rankB: r.rankB, winnerIdx: r.winner ? String(r.winner).toUpperCase() : null, ranked: !!r.ranked, at: r.at, us: null } });
  }
  return out;
}
function onlineTasks(set) {
  const dir = path.join(ONLINE, set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  let names = {};
  try { for (const t of JSON.parse(fs.readFileSync(path.join(TOP, 'leaderboard.json'), 'utf8'))) names[t.id] = t.name; } catch { /* optional */ }
  const out = [];
  for (const g of idx.games || idx) {
    const f = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
    const us = String(g.ourSide).toUpperCase(), opp = names[g.opponentTeam] || String(g.opponentTeam);
    out.push({ key: set + ':' + g.gameId, file: f, info: { src: 'online', set, map: g.mapName, gameId: g.gameId, teamA: us === 'A' ? set : opp, teamB: us === 'B' ? set : opp,
      oppId: g.opponentTeam, winnerIdx: g.winner ? String(g.winner).toUpperCase() : null, at: g.completedAt, us, sub: g.ourSubmission } });
  }
  return out;
}
function workerMain() {
  const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
  const load = tf.makeLoader(tf.viewerSource());
  process.on('message', task => {
    try {
      const R = load(task.file);
      const res = analyse(R, task.info);
      process.send({ key: task.key, line: JSON.stringify({ key: task.key, ...task.info, seed: R.seed, ...res }) });
    } catch (err) { process.send({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 5).join(' | ') }); }
  });
}
async function cachedKeys(file) {
  // streamed: the top cache is larger than one string can hold; a member cut by a kill ends the read (its game is redone)
  const done = new Set(); if (!fs.existsSync(file)) return done;
  const gz = zlib.createGunzip(), rl = require('readline').createInterface({ input: fs.createReadStream(file).pipe(gz), crlfDelay: Infinity });
  gz.on('error', () => rl.close());
  for await (const l of rl) { const m = /^\{"key":"([^"]+)"/.exec(l); if (m) done.add(m[1]); }
  return done;
}
async function extract(tasks, cacheFile, jobs, limit) {
  fs.mkdirSync(path.dirname(cacheFile), { recursive: true });
  const done = await cachedKeys(cacheFile);
  const todo = tasks.filter(t => !done.has(t.key)).slice(0, limit);
  console.log(`${path.relative(ROOT, cacheFile)}: ${tasks.length} games, cached ${done.size}, to do ${todo.length} (jobs ${jobs})`);
  if (!todo.length) return;
  const fd = fs.openSync(cacheFile, 'a'), t0 = Date.now(), errors = [];
  let n = 0;
  await new Promise((resolve, reject) => {
    const queue = todo.slice(); let live = Math.min(jobs, queue.length);
    for (let i = 0, k = live; i < k; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced', execArgv: ['--max-old-space-size=2048'] });
      let finished = false;
      const next = () => { const t = queue.shift(); if (!t) { finished = true; w.kill(); if (--live === 0) resolve(); return; } w.send(t); };
      w.on('message', m => {
        if (m.error) { errors.push(m.key + ' ' + m.error); console.error('error', m.key, m.error); }
        else fs.writeSync(fd, zlib.gzipSync(m.line + '\n'));
        n++;
        if (n % 100 === 0) console.log(`  ${n}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
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

async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const jobs = Math.max(1, Math.min(3, +opt('jobs', 3))), limit = +opt('limit', Infinity);
  if (argv[0] === 'top') {
    const keys = opt('keys', null); if (!keys) throw Error('--keys <file> required');
    return extract(topTasks(keys), path.join(CACHE, opt('name', 'top-all') + '.jsonl.gz'), jobs, limit);
  }
  if (argv[0] === 'online') {
    const sets = []; for (let i = 1; i < argv.length; i++) { if (argv[i].startsWith('--')) { i++; continue; } sets.push(argv[i]); }
    for (const s of sets) await extract(onlineTasks(s), path.join(CACHE, 'online-' + s + '.jsonl.gz'), jobs, limit);
    return;
  }
  if (argv[0] === 'one') {
    const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
    const load = tf.makeLoader(tf.viewerSource());
    const t0 = Date.now(); const R = load(argv[1]); const t1 = Date.now();
    const res = analyse(R, { map: argv[2], us: argv[3] || null });
    const t2 = Date.now();
    const sum = o => Object.values(o).reduce((s, a) => s + (Array.isArray(a) ? a.reduce((x, y) => x + (y || 0), 0) : 0), 0);
    console.log(JSON.stringify({ ms: [t1 - t0, t2 - t1], rounds: res.rounds, winner: res.winner, variant: res.variant, layoutOk: res.layoutOk, chk: res.chk, pieces: res.P.length,
      bytes: JSON.stringify(res).length }));
    for (const s of ['A', 'B']) {
      const T = res[s], b = k => T.b[k] ? T.b[k].reduce((x, y) => x + y, 0) : 0;
      console.log(s, 'turns', b('turns'), 'cs', b('cs'), 'csE', b('csE'), 'csV', b('csV'), 'csN', b('csN'), 'fs', b('fs'), 'fsK', b('fsK'), 'gs', b('gs'), 'sac', b('sac'), 'sacCs', b('sacCs'), 'sacFs', b('sacFs'));
      console.log(s, 'ep', JSON.stringify(T.ep).slice(0, 400));
      console.log(s, 'tag', JSON.stringify(Object.fromEntries(Object.entries(T.tag).map(([k, v]) => [k, Array.isArray(v) && v.length === NB ? v.reduce((x, y) => x + y, 0) : v]))));
      console.log(s, 'cp vor', JSON.stringify(T.cp.vor), 'units', JSON.stringify(T.cp.units));
    }
    return;
  }
  console.error('usage: see the header of exp/supply-chain/extract.js'); process.exit(2);
}
module.exports = { analyse, topTasks, onlineTasks, CACHE };
if (require.main === module) main().catch(err => { console.error(err); process.exit(1); });
