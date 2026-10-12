#!/usr/bin/env node
// Economy principles E1-E9 (research/external/INTEGRATION-2026-09-30.md section 5) tested on replays only (no games, no
// network). Written for research/observations/economy-principles.md (2026-09-30).
//
// usage (repository root; run heavy passes under `nice -n 10`, at most 3 workers):
//   node exp/econ-principles/extract.js top [--name top-all] [--jobs 3] [--limit N]     every game of data/top/index.jsonl
//   node exp/econ-principles/extract.js online <set> [<set> ...] [--jobs 3]
//   node exp/econ-principles/extract.js one <replay file> <map name> [<us A|B>]          debug: timing + summary
//   node exp/econ-principles/extract.js check <cache.jsonl> [...]                       sums the checks (all expected 0)
//   Output: one JSON line per game in .cache/econ-principles/<name>.jsonl (online: online-<set>.jsonl). Done games skipped.
//
// Note (2026-09-30 18:00): the cache of that day was written before the chN0 fix below, so its BK rows carry chN <= 2
// (a chase of >= 3 turns was reset before the row was written and shows as 'no chase'); the report reads chase-ending body
// kills from the CH episode counts, which were not affected.
// Reconstruction: tools/mass_ledger.js perGame() with hooks (its checks must stay 0). Geometry, territory and the pearl
// layout variant: exp/territory-analysis/extract.js. Extra checks (expected 0): pair = a head-on victim without its mover
// record; mirNone = a natural spawn whose mirror tile (map SYMMETRY) did not spawn although it held no body and no pearl.
//
// Definitions ("team" t = 0 for A, 1 for B; "own" = the deciding / moving dragon's team; heads = living dragons' heads):
//   Local counts exclude the two dragons of the pair (the deciding dragon and its adjacent / hit enemy):
//     v3 = heads within Chebyshev 3 of the deciding dragon's head at its turn start (its 7x7 view),
//     m3 / m8 = within Manhattan 3 / 8 of the contact tile (the enemy head), c8 = Chebyshev 8 of the contact tile,
//     L8 = summed length of the heads' dragons within Manhattan 8 of the contact tile. Distances wrap; kelp ignored.
//   Opportunity (O): a dragon's turn start with an enemy head on a neighbouring tile across an open edge (portals
//     included). taken: 1 = a one-step move into that head, 2 = a sprint that ended head-on with an enemy, 0 = no.
//   Contact (C): every head-on death pair between the teams (mover = the dragon that moved into the other head).
//     Drops of both deaths (ceil(Lm/2) + ceil(Lv/2)) with the team and round of each eater.
//   King = the team's longest living dragon (ties: lowest id), recorded at every round's first turn.
//   King death (K): a dragon that was its team's longest when it died (any cause). The other dragon = the rammer / the
//     head it rammed / the body owner.
//   Body kill (BK): an enemy dies by moving into this team's body (mass ledger enemyBody or trap into an enemy body).
//   Chase: at each turn start, the nearest head of the other team within Manhattan 3; a chase episode = the same
//     target for >= 3 consecutive turns of the chaser. Episode ends: separation, chaser death (by cause, body owner =
//     target / third dragon), target death (head-on with the chaser / other).
//   Spawn block (mirror): mirrored tiles share one countdown (rules/map-files.md SYMMETRY). A natural spawn on tile k whose
//     mirror m (y: x -> W-1-x, x: y -> H-1-y, xy: both) did not spawn in the same round means m's attempt was blocked; the blocker is what occupied m at the
//     round's first turn (A body, B body, natural pearl, dropped pearl). Occupancy (OCC): each round, the capacity
//     1/mean gap of every spawn tile under a team's body = expected spawn attempts blocked by that body.
//   Sacrifice (S): mass ledger cause 'sac' at r >= 200 of a dragon that is not its team's king. dK = static path
//     distance (kelp, portals, wrap; bodies ignored) from its head to its king's head at its turn start.
//   Checkpoint (CP): every non-king dragon alive at the first turn of r300 / r350: dK then, fate round and cause.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const X = require(path.join(ROOT, 'exp', 'territory-analysis', 'extract.js'));
const TOP = path.join(ROOT, 'data', 'top'), ONLINE = path.join(ROOT, 'data', 'online'), CACHE = path.join(ROOT, '.cache', 'econ-principles');
const TI = tm => tm === 'A' ? 0 : 1;
let parseInd = null;

function symOf(file) {
  try { const L = fs.readFileSync(file, 'utf8').split('\n', 4); for (const l of L) { const m = /^SYMMETRY (\S+)/.exec(l); if (m) return m[1]; } } catch { /* none */ }
  return null;
}

function analyse(R, info) {
  if (!parseInd) parseInd = require(path.join(ROOT, 'tools', 'mech_check.js')).parseInd;
  const G = X.geometry(R), W = G.W, H = G.H, N = G.N, NBT = G.nb, TERR = G.terr;
  const M = R.match.map, nInit = M.initialDragons.length;
  const linfo = { map: info.map }; if (info.map === 'Prisoners Dilemma') linfo.variant = nInit === 10 ? 'PD10' : 'PD6';
  const vt = X.variantOf(info.map, info.gameId, R, nInit);
  const lf = X.fileOf(info.map, vt.tag), gg = lf && fs.existsSync(lf) ? X.gapsOfFile(lf) : null;
  const CAP = new Float64Array(N); let layoutOk = 0, nSpawnT = 0, nFount = 0; const capT = [0, 0, 0];
  if (gg && gg.w === W && gg.h === H) {
    layoutOk = 1;
    for (let k = 0; k < N; k++) { const q = gg.g[k]; if (q && q[1] > 0) { const mg = Math.max(1, (q[0] + q[1]) / 2); CAP[k] = 1 / mg; nSpawnT++; if (mg <= 12) nFount++; capT[TERR[k]] += CAP[k]; } }
  }
  // mirror map (SYMMETRY x: x -> W-1-x; y: y -> H-1-y; xy: both), confirmed against the layout's gaps
  const sym = lf ? symOf(lf) : null;
  const MIR = new Int32Array(N).fill(-1);
  let symOk = 0;
  if (sym && layoutOk) {
    // SYMMETRY y = mirror across the vertical axis (x -> W-1-x), x = across the horizontal axis (y -> H-1-y), xy = 180 degree
    // rotation; checked against the map files (devil, schooltime, trophy: y; the others: xy)
    for (let k = 0; k < N; k++) { const x = k % W, y = (k / W) | 0; const mx = sym.includes('y') ? W - 1 - x : x, my = sym.includes('x') ? H - 1 - y : y; MIR[k] = my * W + mx; }
    let bad = 0; for (let k = 0; k < N; k++) { const a = gg.g[k], b = gg.g[MIR[k]]; if ((a ? a[1] : 0) !== (b ? b[1] : 0) || (a ? a[0] : 0) !== (b ? b[0] : 0)) bad++; }
    symOk = bad === 0 ? 1 : 0;
  }
  // natural spawns per round (the same drop rule as perGame: a pearl tileChange right after a death is a drop)
  const spawnsAt = new Map();
  { let round = -1, drop = false;
    for (const e of R.events) {
      if (drop && !(e.type === 'tileChange' && e.hasPearl)) drop = false;
      if (e.type === 'roundStart') round = e.round;
      else if (e.type === 'dragonDeath') drop = true;
      else if (e.type === 'tileChange' && e.hasPearl && !drop && round >= 0) { let a = spawnsAt.get(round); if (!a) spawnsAt.set(round, a = []); a.push(e.tile.y * W + e.tile.x); }
    }
  }
  const us = info.us || null;
  const md = (a, b) => { let dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); if (W - dx < dx) dx = W - dx; if (H - dy < dy) dy = H - dy; return dx + dy; };
  const cd = (a, b) => { let dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); if (W - dx < dx) dx = W - dx; if (H - dy < dy) dy = H - dy; return dx > dy ? dx : dy; };
  const K = p => p.y * W + p.x;
  const rel = (k, t) => TERR[k] === 0 ? 1 : TERR[k] === t + 1 ? 0 : 2;   // 0 own, 1 neutral, 2 enemy territory
  const phase3 = r => r < 100 ? 0 : r < 250 ? 1 : 2;

  // per-round team state
  const kingLen = [new Int16Array(501), new Int16Array(501)], units = [new Int16Array(501), new Int16Array(501)];
  const kingId = [new Int32Array(501).fill(-1), new Int32Array(501).fill(-1)];
  // BFS from each king (r >= 200)
  const distK = [new Int16Array(N), new Int16Array(N)], Q = new Int32Array(N);
  const bfsFrom = (src, out) => { out.fill(-1); let qh = 0, qt = 0; Q[qt++] = src; out[src] = 0; while (qh < qt) { const t = Q[qh++]; for (let j = 0; j < 4; j++) { const u = NBT[t * 4 + j]; if (u < 0 || out[u] >= 0) continue; out[u] = out[t] + 1; Q[qt++] = u; } } };
  let lastRound = -99;
  const O = [], C = [], KD = [], BK = [], S = [], CP = [];
  const SB = new Array(3 * 5 * 3).fill(0); // phase x blocker(0 A body, 1 B body, 2 nat pearl, 3 drop pearl, 4 none) x terr(0 neutral, 1 A, 2 B)
  const SPN = new Array(3 * 3).fill(0);    // natural spawns: phase x terr
  const OCC = new Array(2 * 3 * 3).fill(0); // team x phase x rel(own, neutral, enemy): capacity under the team's bodies
  const CH = [new Array(10).fill(0), new Array(10).fill(0)]; // chaser team: episodes, sep, bkTarget, bkThird, headOnTarget, headOnOther, chaserOther, targetDied, gameEnd, turns
  const chk2 = { pair: 0, mirNone: 0, oppTaken: 0 };
  const deathOf = new Map();   // id -> [round, cause]
  const dropEats = [];         // death index -> [team, round, eaterKing, ...]
  const ind = new Map();       // our labels this turn
  const pendingC = new Map();  // victim death index -> contact row index (mover record fills it)

  const localCounts = (ctx, t, headV, center, exA, exB) => {
    // own (team t) minus enemy, excluding dragons exA/exB: [v3o, v3e, m3o, m3e, m8o, m8e, c8o, c8e, L8o, L8e]
    const r = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
    for (const o of ctx.drag.values()) {
      if (o.id === exA || o.id === exB) continue;
      const own = TI(o.team) === t ? 0 : 1, h = o.body[0];
      if (headV && cd(h, headV) <= 3) r[0 + own]++;
      const dm = md(h, center);
      if (dm <= 3) r[2 + own]++;
      if (dm <= 8) { r[4 + own]++; r[8 + own] += o.body.length; }
      if (cd(h, center) <= 8) r[6 + own]++;
    }
    return r;
  };
  const rankIn = (ctx, d) => { let n = 0; for (const o of ctx.drag.values()) if (o.team === d.team && o !== d && (o.body.length > d.body.length || (o.body.length === d.body.length && o.id < d.id))) n++; return n; };

  const hooks = {
    turn(d, round, ctx) {
      if (round !== lastRound) { // first turn of the round: team state, spawn blocks, occupancy, king BFS, checkpoints
        lastRound = round;
        for (let t = 0; t < 2; t++) { const k = ctx.kingOf(t ? 'B' : 'A'); kingLen[t][round] = k ? k.body.length : 0; kingId[t][round] = k ? k.id : -1; }
        for (const o of ctx.drag.values()) units[TI(o.team)][round]++;
        const ph = phase3(round);
        const sp = spawnsAt.get(round) || [];
        if (sp.length) {
          const set = new Set(sp);
          for (const k of sp) {
            SPN[ph * 3 + TERR[k]]++;
            if (!symOk) continue;
            const m = MIR[k]; if (m === k || set.has(m) || !(CAP[m] > 0)) continue;
            let b = 4; const o = ctx.occ.get(m);
            if (o !== undefined) { const od = ctx.drag.get(o); b = od ? TI(od.team) : 4; }
            else if (ctx.pearls.has(m)) b = ctx.pearls.get(m) < 0 ? 2 : 3;
            if (b === 4) chk2.mirNone++;
            SB[(ph * 5 + b) * 3 + TERR[m]]++;
          }
        }
        for (const o of ctx.drag.values()) { const t = TI(o.team); for (const s of o.body) { const k = s.y * W + s.x; if (CAP[k] > 0) OCC[(t * 3 + ph) * 3 + rel(k, t)] += CAP[k]; } }
        if (round >= 200) for (let t = 0; t < 2; t++) { const k = ctx.kingOf(t ? 'B' : 'A'); if (k) bfsFrom(K(k.body[0]), distK[t]); else distK[t].fill(-1); }
        if (round === 300 || round === 350) for (const o of ctx.drag.values()) {
          const t = TI(o.team); if (o.id === kingId[t][round]) continue;
          const dk = distK[t][K(o.body[0])];
          CP.push([round, t, o.body.length, dk, o.id]);
        }
      }
      const t = TI(d.team), h = d.body[0];
      d.h0 = { x: h.x, y: h.y }; d.L0 = d.body.length;
      if (round >= 200) { if (!d.kd) d.kd = new Int16Array(300).fill(-2); if (round < 500) d.kd[round - 200] = d.id === kingId[t][round] ? -3 : distK[t][K(h)]; }
      // opportunity: enemy head adjacent across an open edge
      const hk = K(h); let adj = null, nAdj = 0;
      for (let j = 0; j < 4; j++) {
        const u = NBT[hk * 4 + j]; if (u < 0) continue;
        const oid = ctx.occ.get(u); if (oid === undefined) continue;
        const od = ctx.drag.get(oid); if (!od || od.team === d.team) continue;
        const oh = od.body[0]; if (oh.y * W + oh.x !== u) continue;
        nAdj++; if (!adj || od.body.length > adj.body.length) adj = od;
      }
      d.opp = null;
      if (adj) {
        const lc = localCounts(ctx, t, h, adj.body[0], d.id, adj.id);
        const row = [round, t, d.body.length, adj.body.length, d.id === kingId[t][round] ? 1 : 0, adj.id === kingId[1 - t][round] ? 1 : 0, adj.id > d.id ? 1 : 0, nAdj, ...lc, 0, -1, -1, 0, d.id, adj.id, -1];
        //         0      1  2               3                4                                      5                                         6                   7    8..17    18 19 20 21 22    23      24
        // 18 taken, 19 fate round, 20 fate cause, 21 tag, 22 id, 23 enemy id, 24 contact index
        d.opp = O.length; O.push(row);
      }
      // chase bookkeeping (nearest enemy head within Manhattan 3)
      let best = null, bd = 99;
      for (const o of ctx.drag.values()) { if (o.team === d.team) continue; const dd = md(o.body[0], h); if (dd <= 3 && (dd < bd || (dd === bd && o.id < best.id))) { bd = dd; best = o; } }
      const tid = best ? best.id : -1;
      if (d.chT === tid && tid >= 0) { d.chN++; if (d.chN === 3) { CH[t][0]++; } if (d.chN >= 3) CH[t][9]++; }
      else { if (d.chN >= 3) CH[t][1]++; d.chT = tid; d.chN = tid >= 0 ? 1 : 0; }
      d.nearAlly3 = 0; // filled lazily at death
    },
    indicator(e, round, ctx) { const d = ctx.drag.get(e.id); if (d && us && d.team === us) ind.set(e.id, e.text || ''); },
    action(d, e, round, ctx) {
      let tag = 0;
      if (us && d.team === us) {
        const text = ind.get(d.id) || ''; ind.delete(d.id);
        const p = parseInd(text);
        if (p.kind === 'move') tag = p.ram4 === 'new' ? (p.coll === 1 ? 3 : 2) : p.ram4 === 'old' ? 4 : p.trade ? 1 : 0;
        else if (p.kind === 'conv') tag = 10; else if (p.kind === 'feed') tag = 11; else if (p.kind === 'k2') tag = 12;
        else if (p.kind === 'lasttrade') tag = 13;
      }
      d.tag = tag;
      if (d.opp !== null && d.opp !== undefined) {
        const row = O[d.opp]; row[21] = tag;
        const f = d.fate;
        if (f && f.reason === 'H' && f.hitTeam !== d.team) row[18] = d.steps === 1 && f.hit === row[23] ? 1 : d.steps >= 2 ? 2 : 3;
      }
    },
    eat(d, k, o, round, ctx) {
      if (o >= 0) { const a = dropEats[o] || (dropEats[o] = []); a.push(TI(d.team), round, ctx.isKingNow(d) ? 1 : 0); }
    },
    death(d, rec, idx, other, round, ctx) {
      const t = TI(d.team);
      deathOf.set(d.id, [round, rec.cause]);
      const wasKing = ctx.isKingNow(d);
      const chN0 = d.chN || 0; // before the episode bookkeeping resets it (the body-kill row below reads it)
      // chase episode ends: as chaser
      if (d.chN >= 3) {
        const tgt = d.chT;
        if (other && other.team !== d.team && (rec.cause === 4 || rec.cause === 1) && d.fate && d.fate.reason === 'O') CH[t][other.id === tgt ? 2 : 3]++;
        else if (other && other.team !== d.team && (rec.cause === 2 || rec.cause === 3)) CH[t][other.id === tgt ? 4 : 5]++;
        else CH[t][6]++;
        d.chN = 0;
      }
      // chase episode ends: as target (the chaser's episode closes here unless the chaser is the other of a head-on)
      for (const o of ctx.drag.values()) if (o.team !== d.team && o.chT === d.id && o.chN >= 3) {
        if (other && o.id === other.id && (rec.cause === 2 || rec.cause === 3)) continue; // closed at the chaser's own death (head-on)
        CH[TI(o.team)][7]++; o.chN = 0; o.chT = -1;
      }
      // contact (head-on pair between teams): victim first (cause 2, mover alive), then the mover (cause 3)
      if (rec.cause === 2 && other && other.team !== d.team) {
        const m = other, mt = TI(m.team), v = d;
        const lc = localCounts(ctx, mt, m.h0 || null, v.body[0], m.id, v.id);
        const row = [round, mt, m.body.length, v.body.length, ctx.isKingNow(m) ? 1 : 0, ctx.isKingNow(v) ? 1 : 0,
          m.steps >= 2 ? 1 : 0, m.opp !== null && m.opp !== undefined && O[m.opp][23] === v.id ? 1 : 0, rankIn(ctx, m), rankIn(ctx, v),
          kingLen[mt][round], kingLen[1 - mt][round], units[mt][round], units[1 - mt][round], ...lc, idx, -1, m.tag || 0, 0];
        //  0 r 1 mt 2 Lm 3 Lv 4 mK 5 vK 6 spr 7 adjStart 8 mRank 9 vRank 10 kLm 11 kLv 12 um 13 uv 14..23 lc 24 vIdx 25 mIdx 26 tag 27 (spare)
        pendingC.set(idx, C.length); C.push(row);
        if (m.opp !== null && m.opp !== undefined) O[m.opp][24] = C.length - 1;
      } else if (rec.cause === 3) {
        const ci = pendingC.get(rec.pair);
        if (ci === undefined) chk2.pair++; else { C[ci][25] = idx; pendingC.delete(rec.pair); }
      }
      // king death
      if (wasKing && d.body.length >= 4) {
        let oL = 0, oK = 0, ot = 1 - t;
        if (other && other.team !== d.team) { oL = other.body.length; oK = kingId[TI(other.team)][round] === other.id ? 1 : 0; }
        const center = d.body[0];
        let k3 = 0, k8 = 0, o3 = 0, o8 = 0, second = 0;
        for (const o of ctx.drag.values()) {
          if (o === d || (other && o === other)) continue;
          const dd = md(o.body[0], center);
          if (TI(o.team) === ot) { if (dd <= 3) k3++; if (dd <= 8) k8++; }
          else { if (dd <= 3) o3++; if (dd <= 8) o8++; if (o.body.length > second) second = o.body.length; }
        }
        KD.push([round, t, d.body.length, rec.cause, oL, oK, k3, k8, o3, o8, kingLen[ot][round], second, idx, (d.fate && d.fate.reason) || '', rec.cause === 2 ? 1 : 0]);
      }
      // body kill: d moved into an enemy body
      if (d.fate && d.fate.reason === 'O' && other && other.team !== d.team) {
        const ot = TI(other.team), h = d.h0 || d.body[0];
        let near = 0, nearL = 0;
        for (const o of ctx.drag.values()) { if (o.team !== other.team || o === other) continue; const dd = md(o.body[0], h); if (dd <= 3) { near++; if (o.body.length > nearL) nearL = o.body.length; } }
        const tgt = d.chT, tgtD = tgt >= 0 ? ctx.drag.get(tgt) : null;
        const chased = chN0 >= 1 && tgtD && tgtD.team === other.team ? (tgt === other.id ? 1 : 2) : 0; // 1 chasing the owner, 2 chasing another ally of the owner
        BK.push([round, t, d.body.length, other.body.length, kingId[ot][round] === other.id ? 1 : 0, chased, chN0, near, nearL, d.free, rec.cause, tgtD ? tgtD.body.length : 0]);
      }
      // sacrifice
      if (rec.cause === 0 && round >= 200 && d.kd && kingId[t][round] !== d.id) {
        const i = Math.min(299, round - 200);
        let mx = -1, mxR = -1; for (let j = Math.max(0, i - 60); j <= i; j++) if (d.kd[j] >= 0 && d.kd[j] > mx) { mx = d.kd[j]; mxR = j + 200; }
        const at = r => r - 200 >= 0 && r - 200 < 300 && r <= round ? d.kd[r - 200] : -9;
        let dLong = 99;
        for (const o of ctx.drag.values()) if (o.team === d.team && o !== d && o.body.length > d.body.length) dLong = Math.min(dLong, md(o.body[0], d.body[0]));
        S.push([round, t, d.body.length, d.kd[i], mx, mxR, at(300), at(350), at(400), kingLen[t][round], dLong, idx, d.tag || 0, d.born, d.parent >= 0 ? 1 : 0]);
      }
    },
  };
  const g = ML.perGame(R, linfo, hooks);
  const rounds = g.rounds;
  // resolve drops for contacts, king deaths and sacrifices
  const dstat = (idx, t, r0) => {
    const out = [0, 0, 0, 0, 0, 0, 0, 0]; if (idx < 0) return out;
    const a = dropEats[idx]; if (!a) return out;
    for (let i = 0; i < a.length; i += 3) {
      const own = a[i] === t ? 0 : 3, dr = a[i + 1] - r0;
      if (dr <= 10) out[own]++; if (dr <= 20) out[own + 1]++; out[own + 2]++;
      if (dr <= 20 && a[i + 2]) out[own === 0 ? 6 : 7]++;
    }
    return out;
  };
  const kAt = (t, r) => { r = Math.min(r, rounds - 1); return kingLen[t][r]; };
  for (const c of C) {
    const r = c[0], mt = c[1];
    const a = dstat(c[24], mt, r), b = dstat(c[25], mt, r);
    const e = a.map((v, i) => v + b[i]);
    c.push(...e, kAt(mt, r + 20) - kAt(1 - mt, r + 20), kAt(mt, r + 1) - kAt(1 - mt, r + 1));
    // 28..35 drops of both deaths eaten: mover team 10/20/all, victim team 10/20/all, mover-team king 20, victim-team king 20; 36 king diff r+20; 37 king diff r+1
  }
  for (const k of KD) { const r = k[0], t = k[1]; k.push(...dstat(k[12], t, r), kAt(t, r + 20) - kAt(1 - t, r + 20), kAt(t, r) - kAt(1 - t, r)); }
  for (const s of S) { const r = s[0], t = s[1]; s.push(...dstat(s[11], t, r)); }
  for (const row of O) { const f = deathOf.get(row[22]); if (f) { row[19] = f[0]; row[20] = f[1]; } }
  for (const row of CP) { const f = deathOf.get(row[4]); row.push(f ? f[0] : -1, f ? f[1] : -1); }
  // chase episodes still open at the end (gameEnd = episodes - closed)
  for (let t = 0; t < 2; t++) { const closed = CH[t][1] + CH[t][2] + CH[t][3] + CH[t][4] + CH[t][5] + CH[t][6] + CH[t][7]; CH[t][8] = CH[t][0] - closed; }
  const fl = (tm, name) => g[tm].fl[ML.FI[name]];
  const team = tm => ({
    u: g[tm].st.units, k: g[tm].st.king, tot: g[tm].st.total,
    sp: fl(tm, 'split_n'), spc: fl(tm, 'split_child'),
    natO: fl(tm, 'nat_own').slice(0, 20), natE: fl(tm, 'nat_enemy').slice(0, 20), natN: fl(tm, 'nat_neutral').slice(0, 20),
    eatNat: fl(tm, 'eat_nat'), dnSac: fl(tm, 'dn_sac'), dlSac: fl(tm, 'dl_sac'), bk: fl(tm, 'bk_n'),
  });
  return {
    lay: vt.tag, layHow: vt.how, layoutOk, sym, symOk, W, H, nInit, rounds, endReason: g.endReason, winner: g.winner,
    nSpawnT, nFount, cap: capT.reduce((s, v) => s + v, 0), capT, natSpawned: g.natSpawned, natStart: g.natStart,
    chk: { ...g.chk, ...chk2 },
    A: team('A'), B: team('B'),
    O, C, KD, BK, S, CP, CH, SB, SPN, OCC,
  };
}

// ---------------------------------------------------------------------------------------------------------------
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];
function topTasks() {
  const seen = new Set(), out = [];
  for (const r of readJsonl(path.join(TOP, 'index.jsonl'))) {
    const k = r.battleId + ':' + r.gameId; if (seen.has(k)) continue; seen.add(k);
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
async function extract(tasks, cacheFile, jobs, limit) {
  fs.mkdirSync(path.dirname(cacheFile), { recursive: true });
  const done = new Set();
  if (fs.existsSync(cacheFile)) for (const l of fs.readFileSync(cacheFile, 'utf8').split('\n')) { const m = /^\{"key":"([^"]+)"/.exec(l); if (m) done.add(m[1]); }
  const todo = tasks.filter(t => !done.has(t.key)).slice(0, limit);
  console.log(`${path.relative(ROOT, cacheFile)}: ${tasks.length} games, cached ${done.size}, to do ${todo.length} (jobs ${jobs})`);
  if (!todo.length) return;
  const fd = fs.openSync(cacheFile, 'a'), t0 = Date.now(); let n = 0, nerr = 0;
  await new Promise((resolve, reject) => {
    const queue = todo.slice(); let live = Math.min(jobs, queue.length);
    for (let i = 0, k = live; i < k; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced', execArgv: ['--max-old-space-size=2048'] });
      let finished = false;
      const next = () => { const t = queue.shift(); if (!t) { finished = true; w.kill(); if (--live === 0) resolve(); return; } w.send(t); };
      w.on('message', m => {
        if (m.error) { nerr++; console.error('error', m.key, m.error); } else fs.writeSync(fd, m.line + '\n');
        n++; if (n % 100 === 0) console.log(`  ${n}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
        next();
      });
      w.on('error', reject);
      w.on('exit', code => { if (!finished) reject(Error('worker exited unexpectedly with code ' + code)); });
      next();
    }
  });
  fs.closeSync(fd);
  console.log(`done ${n} in ${((Date.now() - t0) / 1000).toFixed(0)}s, errors ${nerr}`);
}
function checkFiles(files) {
  const sum = {}; let games = 0; const lay = {};
  for (const f of files) for (const l of fs.readFileSync(f, 'utf8').split('\n')) {
    if (!l.trim()) continue; let g; try { g = JSON.parse(l); } catch { sum.badLines = (sum.badLines || 0) + 1; continue; } games++;
    for (const [k, v] of Object.entries(g.chk)) sum[k] = (sum[k] || 0) + v;
    const lk = g.map + '/' + g.lay + ' ok' + g.layoutOk + ' sym' + g.symOk; lay[lk] = (lay[lk] || 0) + 1;
  }
  console.log(`games ${games}; checks summed (all expected 0): ${JSON.stringify(sum)}`);
  console.log(JSON.stringify(lay, null, 1));
}
async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const jobs = Math.max(1, Math.min(3, +opt('jobs', 3))), limit = +opt('limit', Infinity);
  if (argv[0] === 'top') return extract(topTasks(), path.join(CACHE, opt('name', 'top-all') + '.jsonl'), jobs, limit);
  if (argv[0] === 'online') {
    const sets = []; for (let i = 1; i < argv.length; i++) { if (argv[i].startsWith('--')) { i++; continue; } sets.push(argv[i]); }
    for (const s of sets) await extract(onlineTasks(s), path.join(CACHE, 'online-' + s + '.jsonl'), jobs, limit);
    return;
  }
  if (argv[0] === 'one') {
    const tf = require(path.join(ROOT, 'tools', 'top_features.js')); const load = tf.makeLoader(tf.viewerSource());
    const t0 = Date.now(); const R = load(argv[1]); const t1 = Date.now();
    const res = analyse(R, { map: argv[2], us: argv[3] || null, gameId: null }); const t2 = Date.now();
    console.log(`load ${t1 - t0}ms analyse ${t2 - t1}ms`);
    console.log(JSON.stringify({ lay: res.lay, sym: res.sym, symOk: res.symOk, chk: res.chk, nO: res.O.length, nC: res.C.length, nKD: res.KD.length, nBK: res.BK.length, nS: res.S.length, nCP: res.CP.length, CH: res.CH, SB: res.SB, SPN: res.SPN }));
    console.log('C0', JSON.stringify(res.C.slice(0, 3)), '\nO0', JSON.stringify(res.O.slice(0, 3)), '\nKD', JSON.stringify(res.KD.slice(0, 3)), '\nS', JSON.stringify(res.S.slice(0, 3)), '\nBK', JSON.stringify(res.BK.slice(0, 3)));
    return;
  }
  if (argv[0] === 'check') return checkFiles(argv.slice(1).map(f => path.resolve(ROOT, f)));
  console.error('usage: see the header'); process.exit(2);
}
module.exports = { analyse };
if (require.main === module) main().catch(err => { console.error(err); process.exit(1); });
