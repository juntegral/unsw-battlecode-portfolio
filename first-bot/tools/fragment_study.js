#!/usr/bin/env node
// Fragment study of top-team replays: splitting, small fragments, deliberate self-kills, kills and trades.
// Observation only: reads replays, runs no games, no network.
//
// usage: node tools/fragment_study.js [--keys data/top/snapshot-20260929a.keys] [--jobs 4] [--out data/top/fragment_study.json]
//                                     [--cache FILE] [--limit N] [--quiet]
//   --keys   frozen game list, one `battleId:gameId` per line (default: the 2026-09-29a snapshot, 472 games).
//   --jobs   child processes that parse replays (default 4, at most 4).
//   --out    result JSON (default data/top/fragment_study.json). The tables are also printed to stdout.
//   --cache  optional JSON-lines file with the per-game reconstruction. A later run with the same file reuses it and
//            parses only the games that are missing (keep it outside the repo, e.g. in a scratch directory).
//   --limit  parse at most N games (for testing; the aggregation then covers only parsed games).
//   --quiet  print only the run summary, not the tables.
// Inputs: data/top/features.jsonl rows of the listed games (schema docs/top_features.md; the file may hold more games,
// they are ignored) and replays data/top/<battleId>/<gameId>.replay.gz, loaded with tools/replay.js.
// Method: bodies are rebuilt with the step simulation of tools/top_features.js extract() (moves, sprints, portals, kelp,
// splits, deaths, pearls via tileChange), copied here because extract() exposes no intermediate state. On top of it this
// tool keeps which death dropped each pearl and who ate it, the four neighbour tiles before each action, the team's
// longest dragon at deaths and at eats, and head distances on the torus (kelp and portals ignored).
// Checks (printed and stored in meta.checks, all expected 0): deaths and splits equal features.jsonl, head/tail equal the
// replay's dragonUpdate, dropped pearls = ceil(len/2), every eaten pearl was eaten in the simulation, unit counts.
// SSS: games where SSS made fewer than 10 splits (14 in the snapshot) are left out of every table except the SSS
// section; SSS's own side is also left out of pooled and per-team tables in its other games.
// Cost (2026-09-29, 4 jobs): about 150 s for 472 games without a cache, about 10 s with one. Write-up of the results:
// research/observations/top-fragments.md.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');

const ROOT = path.resolve(__dirname, '..'), TOP = path.join(ROOT, 'data', 'top');
const FEATURES = path.join(TOP, 'features.jsonl');
const DIRS = ['N', 'E', 'S', 'W'], DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 };
const TEAMS = ['A', 'B'], TI = { A: 0, B: 1 };
const SRC_INIT = -1, SRC_SPAWN = -2;
const SMALL = 4, MIDMAX = 9;                      // length classes: small <= 4, mid 5..9, large >= 10
const lenClass = L => L <= SMALL ? 0 : L <= MIDMAX ? 1 : 2;
const CLASS_NAMES = ['small(<=4)', 'mid(5-9)', 'large(>=10)'];
const HIST = 64, NW100 = 5, UNIT_CAP = 64, BIG_ENEMY = 8;
// team unit-count bins for per-turn rates: 1-9, 10-19, 20-29, 30-39, 40-49, 50-59, 60-62, 63-64
const UNIT_BINS = ['1-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-62', '63-64'];
const unitsBin = u => u >= 63 ? 7 : u >= 60 ? 6 : Math.min(5, Math.floor(u / 10));
const SSS = 'SSS', SSS_BROKEN_SPLITS = 10;
const EAT_SRC = ['natural', 'ownSelfKill', 'ownOtherDeath', 'enemyDeath'];
const isSelfKill = d => d.reason === 'A' && (d.why === 'suicide' || d.why === 'split');

// ---------------------------------------------------------------------------------------------------------------
// Per-game reconstruction (runs in a child process). Returns compact records for both teams.
function study(R) {
  const M = R.match.map, W = M.width, H = M.height;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const key = (x, y) => y * W + x;
  // --- map geometry: same code as tools/top_features.js extract() ---
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
  // --- torus distances (kelp and portals ignored) ---
  const tdx = (a, b) => { const d = Math.abs(a - b); return d < W - d ? d : W - d; };
  const tdy = (a, b) => { const d = Math.abs(a - b); return d < H - d ? d : H - d; };
  const manh = (p, q) => tdx(p.x, q.x) + tdy(p.y, q.y);
  const cheb = (p, q) => Math.max(tdx(p.x, q.x), tdy(p.y, q.y));

  // --- state ---
  const drag = new Map(), occ = new Map(), pearls = new Map(); // pearls: tile -> source (SRC_INIT, SRC_SPAWN or death index)
  const all = [], teamUnits = { A: 0, B: 0 };
  const setOcc = d => { for (const s of d.body) occ.set(key(s.x, s.y), d.id); };
  const clrOcc = d => { for (const s of d.body) if (occ.get(key(s.x, s.y)) === d.id) occ.delete(key(s.x, s.y)); };
  const mk = (id, team, body, born, parent) => {
    const o = { id, team, body, born, parent, birthLen: body.length, maxLen: body.length, fate: null, expect: [], act: null, tle: false,
      reqSplit: null, nSteps: 0, freeN: -1, nb: null, eat: [0, 0, 0, 0], deathR: -1, deathIdx: -1, endLen: -1 };
    drag.set(id, o); all.push(o); setOcc(o); teamUnits[team]++; return o;
  };
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearls.set(i, SRC_INIT);
  for (const d0 of M.initialDragons) mk(d0.id, d0.team, d0.body.map(s => ({ x: s.x, y: s.y })), 0, -1);
  const deaths = [], splits = [];
  const newGeo = () => ({
    dist: Array.from({ length: NW100 }, () => Array.from({ length: 3 }, () => ({ n: 0, visE: 0, eCloser: 0, hE: new Array(HIST).fill(0), hA: new Array(HIST).fill(0) }))),
    appr: Array.from({ length: 3 }, () => ({ nE: 0, aE: 0, rE: 0, bE: 0, brE: 0, nP: 0, aP: 0, rP: 0, bP: 0, brP: 0, nB: 0, aB: 0, rB: 0, bB: 0, brB: 0 })),
    turnsByUnits: new Array(UNIT_BINS.length).fill(0), // dragon-turns by the team's unit count at the turn
    // turns with an enemy (E) or ally (A) head one step away: n turns, rams (first step into that head), random = k/(free+k)
    ram: Array.from({ length: 3 }, () => ({ nE: 0, ramE: 0, rndE: 0, nA: 0, ramA: 0, rndA: 0 })),
  });
  const G = { A: newGeo(), B: newGeo() };
  // pearls eaten per team: [100-round window][eater was the team's longest 0/1][source EAT_SRC]
  const EAT = { A: Array.from({ length: NW100 }, () => [[0, 0, 0, 0], [0, 0, 0, 0]]), B: Array.from({ length: NW100 }, () => [[0, 0, 0, 0], [0, 0, 0, 0]]) };
  const chk = { updates: 0, deaths: 0, splits: 0, drops: 0, eatTile: 0, units: 0 };
  let round = -1, cur = -1, drop = null, seq = 0;
  const w100 = () => Math.max(0, Math.min(NW100 - 1, Math.floor(round / 100)));
  const units = tm => { let n = 0; for (const d of drag.values()) if (d.team === tm) n++; return n; };
  const longestOther = (tm, exclId) => { let best = null; for (const o of drag.values()) if (o.team === tm && o.id !== exclId && (!best || o.body.length > best.body.length)) best = o; return best; };
  const smallShare = tm => { let s = 0, t = 0; for (const o of drag.values()) if (o.team === tm) { t += o.body.length; if (o.body.length <= SMALL) s += o.body.length; } return t ? s / t : 0; };
  const closeDrop = () => { if (drop !== null) { const rec = deaths[drop]; if (rec.nDrop !== Math.ceil(rec.len / 2)) chk.drops++; drop = null; } };
  const onEat = (d, lenBefore, src) => {
    const lo = longestOther(d.team, d.id);
    const isL = !lo || lenBefore >= lo.body.length ? 1 : 0;
    let cls = 0;
    if (src >= 0) {
      const rec = deaths[src], own = rec.team === d.team;
      cls = own ? (isSelfKill(rec) ? 1 : 2) : 3;
      rec.fates.push([round - rec.r, own ? 0 : 1, isL, d.id === rec.kingId ? 1 : 0, lenBefore]);
    }
    EAT[d.team][w100()][isL][cls]++;
    d.eat[cls]++;
  };
  // Ramming: when another dragon's head is one step away, how often the first step goes into it.
  const sampleRam = (d, fr, hd, a) => {
    const g = G[d.team].ram[lenClass(d.body.length)], nf = fr.filter(Boolean).length;
    const first = a && a.kind === 'move' && a.steps.length ? DIRS.indexOf(a.steps[0]) : -1;
    for (const T of ['E', 'A']) {
      const k = hd.filter(v => v === T).length; if (!k) continue;
      g['n' + T]++; g['rnd' + T] += k / (nf + k);
      if (first >= 0 && hd[first] === T) g['ram' + T]++;
    }
  };
  // Head distances and approach behaviour of dragon d before its action (fr = destination per direction if free, else null).
  const sampleGeo = (d, fr, a) => {
    const tm = d.team, g = G[tm], h = d.body[0], c = lenClass(d.body.length);
    g.turnsByUnits[unitsBin(teamUnits[tm])]++;
    let dE = 999, dA = 999, vis = null, visD = 999, visB = null, visBD = 999;
    for (const o of drag.values()) {
      if (o === d) continue;
      const oh = o.body[0], m = manh(h, oh);
      if (o.team !== tm) {
        if (m < dE) dE = m;
        if (cheb(h, oh) <= 3) { if (m < visD) { visD = m; vis = oh; } if (o.body.length >= BIG_ENEMY && m < visBD) { visBD = m; visB = oh; } }
      } else if (m < dA) dA = m;
    }
    const cell = g.dist[w100()][c];
    cell.n++; cell.hE[Math.min(dE, HIST - 1)]++; cell.hA[Math.min(dA, HIST - 1)]++;
    if (vis) cell.visE++;
    if (dE < dA) cell.eCloser++;
    if (!a || a.kind !== 'move' || !a.steps.length) return;
    const di = DIRS.indexOf(a.steps[0]), dest = di >= 0 ? fr[di] : null, nf = fr.filter(Boolean);
    if (!dest || !nf.length) return; // first step fatal or no free neighbour: not a free choice
    const ap = g.appr[c];
    const score = (t, pre) => {
      const d0 = manh(h, t); let nA = 0, nR = 0;
      for (const f of nf) { const dd = manh(f, t) - d0; if (dd < 0) nA++; else if (dd > 0) nR++; }
      const dd = manh(dest, t) - d0;
      ap['n' + pre]++; ap['b' + pre] += nA / nf.length; ap['br' + pre] += nR / nf.length;
      if (dd < 0) ap['a' + pre]++; else if (dd > 0) ap['r' + pre]++;
    };
    if (vis) score(vis, 'E');
    if (visB) score(visB, 'B');
    let pBest = null, pD = 999;
    for (let yy = -3; yy <= 3; yy++) for (let xx = -3; xx <= 3; xx++) {
      const p = { x: wx(h.x + xx), y: wy(h.y + yy) };
      if (pearls.has(key(p.x, p.y))) { const m = manh(h, p); if (m < pD) { pD = m; pBest = p; } }
    }
    if (pBest) score(pBest, 'P');
  };

  for (const e of R.events) {
    seq++;
    if (drop !== null && !(e.type === 'tileChange' && e.hasPearl)) closeDrop();
    switch (e.type) {
      case 'roundStart': round = e.round; break;
      case 'turnStart': {
        cur = e.id;
        const d = drag.get(cur);
        if (d) { d.fate = null; d.expect = []; d.act = null; d.tle = false; d.reqSplit = null; d.nSteps = 0; }
        break;
      }
      case 'tileChange': {
        const k = key(e.tile.x, e.tile.y);
        if (e.hasPearl) {
          if (drop !== null) { pearls.set(k, drop); deaths[drop].nDrop++; }
          else pearls.set(k, SRC_SPAWN);
        } else if (pearls.has(k)) { chk.eatTile++; pearls.delete(k); } // the simulation removes eaten pearls first
        break;
      }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action;
        d.act = a ? a.kind : null; d.tle = !!e.tle;
        d.reqSplit = a && a.kind === 'split' ? a.childSegmentCount : null;
        const h0 = d.body[0];
        const nb = [0, 0, 0, 0]; // blocked neighbours by kind: kelp, own body, ally body, enemy body
        const hd = [null, null, null, null]; // direction leads into another dragon's head: 'E' enemy, 'A' ally
        const fr = DIRS.map((dir, i) => {
          const nx = across(h0.x, h0.y, dir);
          if (!nx) { nb[0]++; return null; }
          const o = occ.get(key(nx.x, nx.y));
          if (o === undefined) return nx;
          const od = drag.get(o);
          nb[o === d.id ? 1 : od.team === d.team ? 2 : 3]++;
          if (o !== d.id && od.body[0].x === nx.x && od.body[0].y === nx.y) hd[i] = od.team === d.team ? 'A' : 'E';
          return null;
        });
        d.freeN = fr.filter(Boolean).length; d.nb = nb;
        let dEc = 999; for (const o of drag.values()) if (o.team !== d.team) { const c = cheb(h0, o.body[0]); if (c < dEc) dEc = c; }
        d.dEnemyCheb = dEc;
        if (round >= 0) { sampleGeo(d, fr, a); sampleRam(d, fr, hd, a); }
        if (!a || a.kind !== 'move') break;
        d.nSteps = a.steps.length;
        // simulate the steps (execution-order.md): pay, kelp/portal, own body, other dragons, then move and eat
        clrOcc(d);
        const body = d.body.slice();
        let fate = null;
        for (let i = 0; i < a.steps.length; i++) {
          const st = a.steps[i];
          if (i > 0 && body.length <= 2) { fate = { reason: 'A', step: i, why: 'sprint' }; break; }
          const h = body[0], nx = across(h.x, h.y, st);
          if (!nx) { fate = { reason: 'W', step: i }; break; }
          if (body.some(s => s.x === nx.x && s.y === nx.y)) { fate = { reason: 'S', step: i, neck: body.length > 1 && body[1].x === nx.x && body[1].y === nx.y ? 1 : 0 }; break; }
          const o = occ.get(key(nx.x, nx.y));
          if (o !== undefined) {
            const od = drag.get(o), isHead = od.body[0].x === nx.x && od.body[0].y === nx.y;
            fate = { reason: isHead ? 'H' : 'O', step: i, hit: o, hitTeam: od.team, hitLen: od.body.length, hitBorn: od.born, hitSplitBorn: od.parent >= 0 ? 1 : 0, hitBirthLen: od.birthLen };
            if (!isHead) fate.smallShare = smallShare(od.team);
            break;
          }
          const lenBefore = body.length;
          body.unshift(nx);
          const k = key(nx.x, nx.y);
          if (pearls.has(k)) { const src = pearls.get(k); pearls.delete(k); onEat(d, lenBefore, src); } else body.pop();
          if (i > 0) body.pop();
          d.expect.push({ h: body[0], t: body[body.length - 1] });
        }
        d.fate = fate;
        d.body = body; // steps already taken stand, also when a later step is fatal
        if (body.length > d.maxLen) d.maxLen = body.length;
        setOcc(d);
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id);
        if (!d || round < 0) break;
        const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        if (x.h.x !== e.head.x || x.h.y !== e.head.y || x.t.x !== e.tail.x || x.t.y !== e.tail.y) {
          chk.updates++;
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
        const lenBefore = p.body.length;
        if (lenBefore !== e.parentBody.length + e.childBody.length) chk.splits++;
        const lo = longestOther(p.team, p.id), u = units(p.team);
        if (u !== teamUnits[p.team]) chk.units++;
        // [round, parentLenBefore, childLen, unitsBefore, parentId, childId, parent longest (2 strictly, 1 tied, 0 no), parentBorn,
        //  parentSplitBorn, seq, parent's free neighbours this turn, parent's Chebyshev distance to the nearest enemy head]
        splits.push({ t: p.team, v: [round, lenBefore, e.childBody.length, u, p.id, e.childId, !lo || lenBefore > lo.body.length ? 2 : lenBefore === lo.body.length ? 1 : 0, p.born, p.parent >= 0 ? 1 : 0, seq,
          cur === p.id ? p.freeN : -1, cur === p.id ? p.dEnemyCheb : -1] });
        clrOcc(p);
        p.body = e.parentBody.map(s => ({ x: s.x, y: s.y }));
        setOcc(p);
        mk(e.childId, e.team, e.childBody.map(s => ({ x: s.x, y: s.y })), round, p.id);
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        const tm = d.team, h = d.body[0];
        const rec = { r: round, id: d.id, team: tm, reason: e.reason, len: d.body.length, born: d.born, splitBorn: d.parent >= 0 ? 1 : 0,
          birthLen: d.birthLen, maxLen: d.maxLen, mover: cur === d.id, freeN: d.freeN, nb: d.nb, seq, nDrop: 0, fates: [] };
        if (rec.mover) {
          const f = d.fate;
          rec.step = f ? f.step : -1; rec.nSteps = d.nSteps;
          if (f && f.neck !== undefined) rec.neck = f.neck;
          if (f && f.hit !== undefined) {
            rec.hitId = f.hit; rec.hitTeam = f.hitTeam; rec.hitLen = f.hitLen; rec.hitSplitBorn = f.hitSplitBorn;
            rec.hitAge = round - f.hitBorn; rec.hitBirthLen = f.hitBirthLen;
            if (f.smallShare !== undefined) rec.hitSmallShare = +f.smallShare.toFixed(4);
          }
          if (e.reason === 'A') {
            rec.why = d.tle ? 'tle' : f ? f.why : d.act === 'split' ? 'split' : d.act === 'suicide' ? 'suicide' : d.act === null ? 'none' : 'other';
            if (rec.why === 'split') rec.reqSplit = d.reqSplit;
            if (f && f.reason !== 'A') chk.deaths++;
          } else if (!f || f.reason !== e.reason) chk.deaths++;
        } else {
          const m = drag.get(cur);
          if (m) { rec.byId = m.id; rec.byTeam = m.team; rec.byLen = m.body.length; rec.bySplitBorn = m.parent >= 0 ? 1 : 0; }
          if (e.reason !== 'H' || !m || !m.fate || m.fate.hit !== d.id) chk.deaths++;
        }
        rec.units = units(tm);
        const king = longestOther(tm, d.id);
        rec.kingId = king ? king.id : -1; rec.kingLen = king ? king.body.length : 0; rec.distKing = king ? cheb(h, king.body[0]) : -1;
        rec.isLongest = !king || rec.len >= king.body.length ? 1 : 0;
        let dE = 999; for (const o of drag.values()) if (o.team !== tm) { const c = cheb(h, o.body[0]); if (c < dE) dE = c; }
        rec.distEnemy = dE;
        deaths.push(rec);
        d.deathR = round; d.deathIdx = deaths.length - 1; d.endLen = rec.len;
        clrOcc(d); drag.delete(e.id); teamUnits[tm]--;
        drop = deaths.length - 1;
        break;
      }
    }
  }
  closeDrop();
  const rounds = round + 1;
  for (const o of all) if (o.deathR < 0) o.endLen = o.body.length;
  // rounds from each death to the next split of the same team (-1 if none)
  const splitSeq = { A: [], B: [] };
  for (const s of splits) splitSeq[s.t].push([s.v[9], s.v[0]]);
  for (const rec of deaths) {
    const arr = splitSeq[rec.team]; let lo = 0, hi = arr.length;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (arr[mid][0] <= rec.seq) lo = mid + 1; else hi = mid; }
    rec.nextSplitDt = lo < arr.length ? arr[lo][1] - rec.r : -1;
  }
  return {
    rounds, width: W, height: H, nInit: M.initialDragons.length,
    deaths, splits: splits.map(s => [TI[s.t], ...s.v]),
    // [id, team, born, parent, birthLen, maxLen, deathR, deathIdx, endLen, eat natural, eat own self-kill, eat own other, eat enemy]
    dragons: all.map(o => [o.id, TI[o.team], o.born, o.parent, o.birthLen, o.maxLen, o.deathR, o.deathIdx, o.endLen, ...o.eat]),
    geo: G, eat: EAT, chk,
  };
}

// ---------------------------------------------------------------------------------------------------------------
// Child process: parse and study one game per message.
if (process.argv.includes('--child')) {
  const { load } = require('./replay.js');
  process.on('message', task => {
    try { process.send({ key: task.key, out: study(load(task.file)) }); }
    catch (err) { process.send({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 3).join(' | ') }); }
  });
}

// ---------------------------------------------------------------------------------------------------------------
// Statistics helpers
const sum = a => a.reduce((x, y) => x + y, 0);
const sorted = a => a.slice().sort((x, y) => x - y);
function quant(a, p) { if (!a.length) return null; const s = sorted(a), pos = (s.length - 1) * p, lo = Math.floor(pos), hi = Math.ceil(pos); return +(s[lo] + (s[hi] - s[lo]) * (pos - lo)).toFixed(2); }
const med = a => quant(a, 0.5);
const mean = a => a.length ? +(sum(a) / a.length).toFixed(3) : null;
const share = (n, d) => d ? +(n / d).toFixed(4) : null;
function histMed(h) { const n = sum(h); if (!n) return null; let c = 0; for (let i = 0; i < h.length; i++) { c += h[i]; if (c * 2 >= n) return i; } return null; }
function histQ(h, p) { const n = sum(h); if (!n) return null; let c = 0; for (let i = 0; i < h.length; i++) { c += h[i]; if (c >= n * p) return i; } return null; }
function counts(a, f) { const o = {}; for (const x of a) { const k = f(x); o[k] = (o[k] || 0) + 1; } return o; }
function shares(obj) { const t = sum(Object.values(obj)), o = {}; for (const [k, v] of Object.entries(obj)) o[k] = share(v, t); return o; }
const addArr = (a, b) => { for (let i = 0; i < b.length; i++) a[i] += b[i]; return a; };
function groupBy(a, f) { const m = new Map(); for (const x of a) { const k = f(x); if (!m.has(k)) m.set(k, []); m.get(k).push(x); } return m; }
const pct = x => x === null || x === undefined ? '-' : (100 * x).toFixed(1) + '%';
const fmt = x => x === null || x === undefined ? '-' : typeof x === 'number' ? (Number.isInteger(x) ? String(x) : x.toFixed(2)) : String(x);

// Split categories. L = parent length before, c = child length.
function splitCat(L, c) {
  if (L === 4 && c === 2) return '2+2';
  if (Math.abs(2 * c - L) <= 1) return 'half';   // halving (L >= 5)
  if (c <= 3) return 'peel';                      // child 2-3 taken off a longer parent (tail peel)
  if (L - c <= 3) return 'stub';                  // parent keeps 2-3, the child (old tail = new head) takes the rest
  return 'other';                                 // both parts >= 4 and unequal
}
const SPLIT_CATS = ['2+2', 'half', 'peel', 'stub', 'other'];
// Death cause of a death record, from the dead dragon's side.
function cause(d) {
  if (d.reason === 'A') return d.why === 'suicide' ? 'A-suicide' : d.why === 'split' ? 'A-split' : 'A-other';
  if (d.reason === 'O') return d.hitTeam === d.team ? 'O-own' : 'O-enemy';
  if (d.reason === 'H') { const other = d.mover ? d.hitTeam : d.byTeam; return other === d.team ? 'H-own' : 'H-enemy'; }
  return d.reason; // W, S
}
const CAUSES = ['A-suicide', 'A-split', 'A-other', 'W', 'S', 'O-enemy', 'O-own', 'H-enemy', 'H-own'];
// Death category for the pearl-drop comparison. Self-kills and W/S deaths are split by whether at least one neighbour
// tile was free (not kelp, no body) at the start of the turn; W/S on a later sprint step are kept apart.
function dropCat(d) {
  const c = cause(d);
  if (c === 'A-suicide' || c === 'A-split') return c + (d.freeN > 0 ? '-free' : '-trapped');
  if (c === 'W' || c === 'S') return d.step > 0 ? 'WS-sprint' : d.freeN > 0 ? 'WS-free' : 'WS-trapped';
  return c;
}
const DROP_CATS = ['A-suicide-free', 'A-suicide-trapped', 'A-split-free', 'A-split-trapped', 'WS-free', 'WS-trapped', 'WS-sprint', 'O-enemy', 'O-own', 'H-enemy', 'H-own', 'A-other'];
const MODE_CATS = ['self-free', 'self-trapped', 'WS-free', 'WS-trapped', 'WS-sprint', 'O-own', 'O-enemy', 'H-enemy', 'H-own', 'A-other'];
const modeCat = d => { const c = dropCat(d); return c.startsWith('A-suicide') || c.startsWith('A-split') ? (c.endsWith('-free') ? 'self-free' : 'self-trapped') : c; };
const ageClass = a => a === 0 ? '0' : a <= 9 ? '1-9' : a <= 49 ? '10-49' : a <= 149 ? '50-149' : '150+';
const AGE_CLASSES = ['0', '1-9', '10-49', '50-149', '150+'];
const birthClass = L => L <= 4 ? String(L) : L <= 9 ? '5-9' : '10+';
const BIRTH_CLASSES = ['2', '3', '4', '5-9', '10+'];
const lenBin = L => L <= 4 ? String(L) : L <= 9 ? '5-9' : L <= 19 ? '10-19' : '20+';
const LEN_BINS = ['1', '2', '3', '4', '5-9', '10-19', '20+'];

// ---------------------------------------------------------------------------------------------------------------
// Aggregation over team-sides. A side = one team in one game: {k, f (features row), g (study output), s, o, team, opp, win, ...}.
function sideDeaths(x) { return x.g.deaths.filter(d => d.team === x.s); }
function oppDeaths(x) { return x.g.deaths.filter(d => d.team === x.o); }
function sideSplits(x) { return x.g.splits.filter(t => t[0] === TI[x.s]); }
function sideDragons(x) { return x.g.dragons.filter(t => t[1] === TI[x.s]); }

// Q1: split anatomy
function splitStats(list) {
  const sp = [], perSide = [];
  for (const x of list) { const s = sideSplits(x); perSide.push(s.length); for (const t of s) sp.push(t); }
  // t = [team, round, L, c, unitsBefore, parentId, childId, parentWasLongest, parentBorn, parentSplitBorn, seq]
  const cats = {}; for (const c of SPLIT_CATS) cats[c] = 0;
  for (const t of sp) cats[splitCat(t[2], t[3])]++;
  const byWindow = [];
  for (let w = 0; w < NW100; w++) {
    const running = list.filter(x => x.rounds > w * 100);
    const inW = sp.filter(t => Math.floor(t[1] / 100) === w);
    const c = {}; for (const k of SPLIT_CATS) c[k] = 0; for (const t of inW) c[splitCat(t[2], t[3])]++;
    const chi = counts(inW, t => t[3] <= 3 ? String(t[3]) : t[3] <= 9 ? '4-9' : '10+');
    byWindow.push({ w: `${w * 100}-${w * 100 + 99}`, sidesRunning: running.length, splits: inW.length, perSide: running.length ? +(inW.length / running.length).toFixed(1) : null,
      medParentLen: med(inW.map(t => t[2])), medChildLen: med(inW.map(t => t[3])), cats: shares(c), childLen: shares(chi), atCap: share(inW.filter(t => t[4] >= 60).length, inW.length) });
  }
  return {
    sides: list.length, splits: sp.length, perSideMean: mean(perSide), perSideMedian: med(perSide), sidesWithoutSplits: perSide.filter(n => !n).length,
    parentLen: { p10: quant(sp.map(t => t[2]), 0.1), median: med(sp.map(t => t[2])), p90: quant(sp.map(t => t[2]), 0.9), bins: shares(counts(sp, t => lenBin(t[2]))) },
    childLen: { median: med(sp.map(t => t[3])), p90: quant(sp.map(t => t[3]), 0.9), bins: shares(counts(sp, t => lenBin(t[3]))) },
    childShare: { p10: quant(sp.map(t => t[3] / t[2]), 0.1), median: med(sp.map(t => t[3] / t[2])), p90: quant(sp.map(t => t[3] / t[2]), 0.9) },
    cats: shares(cats), catCounts: cats,
    parentStrictLongest: share(sp.filter(t => t[7] === 2).length, sp.length),
    parentSplitBorn: share(sp.filter(t => t[9]).length, sp.length),
    unitsBeforeAtLeast60: share(sp.filter(t => t[4] >= 60).length, sp.length),
    bigParent: subSplits(sp.filter(t => t[2] >= 8)),
    kingSplits: subSplits(sp.filter(t => t[7] === 2 && t[2] >= 8)),
    byWindow,
  };
}
// Split categories and child length for a subset of splits (e.g. parents of length >= 8).
function subSplits(sp) {
  const cats = {}; for (const c of SPLIT_CATS) cats[c] = 0; for (const t of sp) cats[splitCat(t[2], t[3])]++;
  return { n: sp.length, medParentLen: med(sp.map(t => t[2])), medChildLen: med(sp.map(t => t[3])), childLe3: share(sp.filter(t => t[3] <= 3).length, sp.length),
    medChildShare: med(sp.map(t => t[3] / t[2])), cats: shares(cats), byWindow100: counts(sp, t => String(Math.min(4, Math.floor(t[1] / 100)) * 100)) };
}
// Units, longest and total over time from features timelines; a side counts at r while its game is still running
// (r < rounds), and at r = 500 only if the game reached round 500.
function unitsOverTime(list) {
  const out = [];
  for (let r = 0; r <= 500; r += 50) {
    const run = list.filter(x => r < x.rounds || (r === 500 && x.rounds === 500));
    const tl = run.map(x => x.f[x.s].timeline[r / 10]);
    out.push({ r, sides: run.length, units: med(tl.map(t => t.units)), unitsP90: quant(tl.map(t => t.units), 0.9), longest: med(tl.map(t => t.longest)), total: med(tl.map(t => t.total)) });
  }
  return out;
}

// Q2: fate of split-born dragons (and initial dragons for comparison)
function fateStats(list, splitBorn) {
  const rows = [];
  for (const x of list) {
    const ds = x.g.deaths;
    for (const t of sideDragons(x)) {
      // t = [id, team, born, parent, birthLen, maxLen, deathR, deathIdx, endLen, eat...]
      if ((t[3] >= 0) !== splitBorn) continue;
      const d = t[7] >= 0 ? ds[t[7]] : null;
      rows.push({ born: t[2], birthLen: t[4], maxLen: t[5], dead: !!d, age: d ? d.r - t[2] : x.rounds - 1 - t[2], cause: d ? cause(d) : 'alive', obs: x.rounds - 1 - t[2], endLen: t[8] });
    }
  }
  const dead = rows.filter(r => r.dead);
  const within = a => { const el = rows.filter(r => r.obs >= a); return { eligible: el.length, died: share(el.filter(r => r.dead && r.age <= a).length, el.length) }; };
  const causeShares = rs => { const c = {}; for (const k of CAUSES) c[k] = 0; for (const r of rs) if (r.dead) c[r.cause]++; return shares(c); };
  const byBirth = {}; for (const b of BIRTH_CLASSES) { const rs = rows.filter(r => birthClass(r.birthLen) === b); byBirth[b] = { n: rs.length, alive: share(rs.filter(r => !r.dead).length, rs.length), medAgeAtDeath: med(rs.filter(r => r.dead).map(r => r.age)), causes: causeShares(rs) }; }
  const byAge = {}; for (const a of AGE_CLASSES) { const rs = dead.filter(r => ageClass(r.age) === a); byAge[a] = { n: rs.length, causes: causeShares(rs) }; }
  const byDeathLen = {}; for (const b of LEN_BINS) { const rs = dead.filter(r => lenBin(r.endLen) === b); if (rs.length) byDeathLen[b] = { n: rs.length, causes: causeShares(rs) }; }
  return {
    n: rows.length, perSide: +(rows.length / Math.max(1, list.length)).toFixed(1), aliveAtEnd: share(rows.length - dead.length, rows.length),
    medAgeAtDeath: med(dead.map(r => r.age)), p90AgeAtDeath: quant(dead.map(r => r.age), 0.9), grewAfterBirth: share(rows.filter(r => r.maxLen > r.birthLen).length, rows.length),
    diedWithin: { 0: within(0), 5: within(5), 20: within(20), 50: within(50), 100: within(100) },
    causes: causeShares(rows), byBirthLen: byBirth, byAgeAtDeath: byAge, byLenAtDeath: byDeathLen,
  };
}

// Q3: drop fates for a set of death records
function fateTable(recs) {
  const dropped = sum(recs.map(d => d.nDrop));
  const n = (f) => sum(recs.map(d => d.fates.filter(f).length));
  const o = { deaths: recs.length, pearls: dropped, pearlsPerDeath: recs.length ? +(dropped / recs.length).toFixed(2) : null };
  for (const T of [5, 10, 20]) {
    o['own' + T] = share(n(f => f[0] <= T && f[1] === 0), dropped);
    o['enemy' + T] = share(n(f => f[0] <= T && f[1] === 1), dropped);
  }
  o.ownLongest20 = share(n(f => f[0] <= 20 && f[1] === 0 && f[2] === 1), dropped);
  o.ownKingAtDrop20 = share(n(f => f[0] <= 20 && f[1] === 0 && f[3] === 1), dropped);
  o.ownEver = share(n(f => f[1] === 0), dropped);
  o.enemyEver = share(n(f => f[1] === 1), dropped);
  o.neverEaten = share(dropped - n(() => true), dropped);
  o.ownPearls20PerDeath = recs.length ? +(n(f => f[0] <= 20 && f[1] === 0) / recs.length).toFixed(2) : null;
  const ownEaterLens = []; for (const d of recs) for (const f of d.fates) if (f[0] <= 20 && f[1] === 0) ownEaterLens.push(f[4]);
  o.ownEaterLenMedian = med(ownEaterLens);
  o.distKingMedian = med(recs.filter(d => d.distKing >= 0).map(d => d.distKing));
  o.distKingLe2 = share(recs.filter(d => d.distKing >= 0 && d.distKing <= 2).length, recs.filter(d => d.distKing >= 0).length);
  o.lenMedian = med(recs.map(d => d.len));
  return o;
}
function selfKillStats(list) {
  const all = [], self = [];
  for (const x of list) for (const d of sideDeaths(x)) { all.push(d); if (isSelfKill(d)) self.push(d); }
  const other = all.filter(d => !isSelfKill(d));
  const rq = counts(self.filter(d => d.why === 'split'), d => d.reqSplit < 2 ? 'child<2' : d.len - d.reqSplit < 2 ? 'parent<2' : d.units >= UNIT_CAP ? 'cap' : 'unknown');
  return {
    sides: list.length, n: self.length, perSide: +(self.length / Math.max(1, list.length)).toFixed(1), shareOfDeaths: share(self.length, all.length),
    why: counts(self, d => d.why),
    round: { p10: quant(self.map(d => d.r), 0.1), median: med(self.map(d => d.r)), p90: quant(self.map(d => d.r), 0.9) },
    byWindow100: shares(counts(self, d => String(Math.min(4, Math.floor(d.r / 100)) * 100))),
    len: { median: med(self.map(d => d.len)), bins: shares(counts(self, d => lenBin(d.len))) },
    age: { age0: share(self.filter(d => d.r === d.born).length, self.length), le2: share(self.filter(d => d.r - d.born <= 2).length, self.length), median: med(self.map(d => d.r - d.born)) },
    splitBorn: share(self.filter(d => d.splitBorn).length, self.length),
    trappedShare: share(self.filter(d => d.freeN === 0).length, self.length),
    wasLongest: share(self.filter(d => d.isLongest).length, self.length),
    unitsMedian: med(self.map(d => d.units)), unitsAtLeast60: share(self.filter(d => d.units >= 60).length, self.length),
    otherDeathsUnitsAtLeast60: share(other.filter(d => d.units >= 60).length, other.length),
    splitWithin1: share(self.filter(d => d.nextSplitDt >= 0 && d.nextSplitDt <= 1).length, self.length),
    otherDeathsSplitWithin1: share(other.filter(d => d.nextSplitDt >= 0 && d.nextSplitDt <= 1).length, other.length),
    kingLenMedian: med(self.filter(d => d.kingId >= 0).map(d => d.kingLen)),
    illegalSplitRequest: { reason: rq, requested: counts(self.filter(d => d.why === 'split'), d => String(d.reqSplit)) },
    trappedBlockers: blockers(self.filter(d => d.freeN === 0)),
    free: { n: self.filter(d => d.freeN > 0).length, perSide: +(self.filter(d => d.freeN > 0).length / Math.max(1, list.length)).toFixed(1),
      round: { p10: quant(self.filter(d => d.freeN > 0).map(d => d.r), 0.1), median: med(self.filter(d => d.freeN > 0).map(d => d.r)), p90: quant(self.filter(d => d.freeN > 0).map(d => d.r), 0.9) },
      lenMedian: med(self.filter(d => d.freeN > 0).map(d => d.len)), drops: fateTable(self.filter(d => d.freeN > 0)) },
    trapped: { n: self.filter(d => d.freeN === 0).length, drops: fateTable(self.filter(d => d.freeN === 0)) },
    drops: fateTable(self),
  };
}
// What blocks the four neighbour tiles of trapped dragons: shares of kelp, own body, ally body, enemy body.
function blockers(recs) {
  const s = [0, 0, 0, 0]; for (const d of recs) if (d.nb) addArr(s, d.nb);
  const t = sum(s); return { n: recs.length, kelp: share(s[0], t), ownBody: share(s[1], t), allyBody: share(s[2], t), enemyBody: share(s[3], t) };
}
// Per dragon-turn rates (per 1000 turns) by the team's unit count at the turn.
function unitRates(list) {
  const z = () => new Array(UNIT_BINS.length).fill(0);
  const turns = z(), selfFree = z(), selfTrapped = z(), trappedWS = z(), splitsB = z(), other = z();
  for (const x of list) {
    addArr(turns, x.g.geo[x.s].turnsByUnits);
    for (const d of sideDeaths(x)) {
      const b = unitsBin(d.units), m = modeCat(d);
      if (m === 'self-free') selfFree[b]++; else if (m === 'self-trapped') selfTrapped[b]++; else { other[b]++; if (m === 'WS-trapped') trappedWS[b]++; }
    }
    for (const t of sideSplits(x)) splitsB[unitsBin(t[4])]++;
  }
  const r = (n, t) => t ? +(1000 * n / t).toFixed(2) : null;
  return UNIT_BINS.map((b, i) => ({ units: b, turns: turns[i], selfFree: r(selfFree[i], turns[i]), selfTrapped: r(selfTrapped[i], turns[i]), wsTrapped: r(trappedWS[i], turns[i]), otherDeaths: r(other[i], turns[i]), splits: r(splitsB[i], turns[i]) }));
}
// How a team's dragons die: deaths per side by mode.
function deathModes(list) {
  const c = {}; for (const k of MODE_CATS) c[k] = 0;
  let n = 0; for (const x of list) for (const d of sideDeaths(x)) { c[modeCat(d)]++; n++; }
  const o = { deathsPerSide: +(n / Math.max(1, list.length)).toFixed(1) }; for (const k of MODE_CATS) o[k] = +(c[k] / Math.max(1, list.length)).toFixed(1);
  o.trappedPerSide = +((c['self-trapped'] + c['WS-trapped']) / Math.max(1, list.length)).toFixed(1); o.trappedShare = share(c['self-trapped'] + c['WS-trapped'], n);
  o.freePerSide = +((c['self-free'] + c['WS-free']) / Math.max(1, list.length)).toFixed(1); o.freeShare = share(c['self-free'] + c['WS-free'], n);
  return o;
}
// Where the pearls eaten by the team's current longest dragon come from.
function kingDiet(list) {
  const acc = Array.from({ length: NW100 }, () => [[0, 0, 0, 0], [0, 0, 0, 0]]);
  for (const x of list) { const E = x.g.eat[x.s]; for (let w = 0; w < NW100; w++) for (let l = 0; l < 2; l++) addArr(acc[w][l], E[w][l]); }
  const tot = [[0, 0, 0, 0], [0, 0, 0, 0]]; for (let w = 0; w < NW100; w++) for (let l = 0; l < 2; l++) addArr(tot[l], acc[w][l]);
  const mkS = a => { const o = { total: sum(a) }; EAT_SRC.forEach((k, i) => { o[k] = share(a[i], sum(a)); }); return o; };
  // pearls from own deaths eaten by the (then) longest, by the death's mode, as a share of everything the longest ate in that window
  const byMode = Array.from({ length: NW100 }, () => ({}));
  for (const x of list) for (const d of sideDeaths(x)) for (const f of d.fates) if (f[1] === 0 && f[2] === 1) {
    const w = Math.min(NW100 - 1, Math.floor((d.r + f[0]) / 100)), m = modeCat(d); byMode[w][m] = (byMode[w][m] || 0) + 1;
  }
  const ownByMode = byMode.map((m, w) => { const t = sum(acc[w][1]), o = { w: w * 100, eaten: t }; for (const k of MODE_CATS) o[k] = share(m[k] || 0, t);
    o.ownFreeDeaths = share((m['self-free'] || 0) + (m['WS-free'] || 0), t); o.ownTrappedDeaths = share((m['self-trapped'] || 0) + (m['WS-trapped'] || 0), t); return o; });
  return { longest: mkS(tot[1]), others: mkS(tot[0]), longestByWindow: acc.map((a, w) => ({ w: w * 100, ...mkS(a[1]) })), longestOwnDeathsByMode: ownByMode, perSideLongestEaten: +(sum(tot[1]) / Math.max(1, list.length)).toFixed(1) };
}

// Q4: kills and trades (from the side's point of view)
function killStats(list) {
  const O = [], Hr = [], Hv = [], enemyDeaths = [], bigOwn = [], bigEnemyByUs = [];
  let hp = 0, hpUs = 0, hpThem = 0, ePearls = 0, eUs = 0, oPearls = 0, oThem = 0;
  for (const x of list) {
    for (const d of oppDeaths(x)) {
      enemyDeaths.push(d);
      if (d.reason === 'O' && d.hitTeam === x.s) O.push(d);                              // enemy head into our body
      if (d.reason === 'H' && d.mover && d.hitTeam === x.s) Hv.push({ r: d.r, our: d.hitLen, their: d.len, ourSplitBorn: null }); // enemy rammed our head
      ePearls += d.nDrop; for (const f of d.fates) if (f[0] <= 20 && f[1] === 1) eUs++;
      if (cause(d) === 'H-enemy') { hp += d.nDrop; for (const f of d.fates) if (f[0] <= 20) { if (f[1] === 1) hpUs++; else hpThem++; } }
      if (d.len >= 10 && cause(d) === 'H-enemy') bigEnemyByUs.push(d.mover ? d.hitLen : d.byLen);
    }
    for (const d of sideDeaths(x)) {
      if (d.reason === 'H' && d.mover && d.hitTeam === x.o) Hr.push({ r: d.r, our: d.len, their: d.hitLen, ourSplitBorn: d.splitBorn, step: d.step }); // we rammed
      oPearls += d.nDrop; for (const f of d.fates) if (f[0] <= 20 && f[1] === 1) oThem++;
      if (cause(d) === 'H-enemy') { hp += d.nDrop; for (const f of d.fates) if (f[0] <= 20) { if (f[1] === 0) hpUs++; else hpThem++; } }
      if (d.len >= 10) bigOwn.push(d);
    }
  }
  const H = Hr.concat(Hv), n = list.length || 1;
  const eCause = counts(enemyDeaths, d => cause(d));
  const bigH = bigOwn.filter(d => cause(d) === 'H-enemy').map(d => d.mover ? d.hitLen : d.byLen);
  const hByW = new Array(NW100).fill(0); for (const t of H) hByW[Math.min(NW100 - 1, Math.floor(t.r / 100))]++;
  const runW = new Array(NW100).fill(0); for (const x of list) for (let w = 0; w < NW100; w++) if (x.rounds > w * 100) runW[w]++;
  return {
    pearls: { hDropped: hp, hEatenByUs20: share(hpUs, hp), hEatenByThem20: share(hpThem, hp), enemyDropsEatenByUs20: share(eUs, ePearls), ourDropsEatenByThem20: share(oThem, oPearls),
      enemyPearlsEatenPerSide20: +(eUs / n).toFixed(1), ourPearlsLostPerSide20: +(oThem / n).toFixed(1) },
    bigDeaths: { perSide: +(bigOwn.length / n).toFixed(2), causes: shares(counts(bigOwn, d => cause(d))), hEnemyPerSide: +(bigH.length / n).toFixed(2), hEnemyOtherLenMedian: med(bigH), hEnemyOtherLe3: share(bigH.filter(v => v <= 3).length, bigH.length),
      enemyBigKilledByHPerSide: +(bigEnemyByUs.length / n).toFixed(2), enemyBigKilledByOurLe3: share(bigEnemyByUs.filter(v => v <= 3).length, bigEnemyByUs.length) },
    hByWindowPerRunningSide: hByW.map((v, w) => ({ w: w * 100, sidesRunning: runW[w], perSide: runW[w] ? +(v / runW[w]).toFixed(1) : null })),
    sides: list.length, enemyDeathsPerSide: +(enemyDeaths.length / n).toFixed(1), enemyDeathCauses: shares(eCause),
    oKillsPerSide: +(O.length / n).toFixed(1), hTradesPerSide: +(H.length / n).toFixed(1), hWeRammedPerSide: +(Hr.length / n).toFixed(1), hTheyRammedPerSide: +(Hv.length / n).toFixed(1),
    hShareOfKills: share(H.length, H.length + O.length),
    h: { n: H.length, ourLenMedian: med(H.map(t => t.our)), theirLenMedian: med(H.map(t => t.their)), tradedUp: share(H.filter(t => t.our < t.their).length, H.length),
      even: share(H.filter(t => t.our === t.their).length, H.length), tradedDown: share(H.filter(t => t.our > t.their).length, H.length),
      ourLe3: share(H.filter(t => t.our <= 3).length, H.length), netLenPerSide: +(sum(H.map(t => t.their - t.our)) / n).toFixed(1),
      weRammed: { n: Hr.length, ourLenMedian: med(Hr.map(t => t.our)), theirLenMedian: med(Hr.map(t => t.their)), tradedUp: share(Hr.filter(t => t.our < t.their).length, Hr.length), ourSplitBorn: share(Hr.filter(t => t.ourSplitBorn).length, Hr.length),
        onSprintStep: share(Hr.filter(t => t.step > 0).length, Hr.length), sprintOurLenMedian: med(Hr.filter(t => t.step > 0).map(t => t.our)), sprintTheirLenMedian: med(Hr.filter(t => t.step > 0).map(t => t.their)) },
      theyRammed: { n: Hv.length, ourLenMedian: med(Hv.map(t => t.our)), theirLenMedian: med(Hv.map(t => t.their)) } },
    o: { n: O.length, blockerLenMedian: med(O.map(d => d.hitLen)), blockerLe2: share(O.filter(d => d.hitLen <= 2).length, O.length), blockerLe4: share(O.filter(d => d.hitLen <= SMALL).length, O.length),
      expectedLe4BySegments: mean(O.map(d => d.hitSmallShare)), blockerSplitBorn: share(O.filter(d => d.hitSplitBorn).length, O.length), blockerAgeMedian: med(O.map(d => d.hitAge)),
      victimLenMedian: med(O.map(d => d.len)), victimLenP90: quant(O.map(d => d.len), 0.9), victimSprint: share(O.filter(d => d.step > 0).length, O.length) },
  };
}

// Q5: geometry
function geoStats(list) {
  const cells = Array.from({ length: NW100 }, () => Array.from({ length: 3 }, () => ({ n: 0, visE: 0, eCloser: 0, hE: new Array(HIST).fill(0), hA: new Array(HIST).fill(0) })));
  const appr = Array.from({ length: 3 }, () => ({ nE: 0, aE: 0, rE: 0, bE: 0, brE: 0, nP: 0, aP: 0, rP: 0, bP: 0, brP: 0, nB: 0, aB: 0, rB: 0, bB: 0, brB: 0 }));
  for (const x of list) {
    const g = x.g.geo[x.s];
    for (let w = 0; w < NW100; w++) for (let c = 0; c < 3; c++) { const a = cells[w][c], b = g.dist[w][c]; a.n += b.n; a.visE += b.visE; a.eCloser += b.eCloser; addArr(a.hE, b.hE); addArr(a.hA, b.hA); }
    for (let c = 0; c < 3; c++) for (const k of Object.keys(appr[c])) appr[c][k] += g.appr[c][k];
  }
  const dist = [];
  for (let c = 0; c < 3; c++) for (let w = 0; w < NW100; w++) {
    const a = cells[w][c];
    dist.push({ cls: CLASS_NAMES[c], w: w * 100, turns: a.n, medEnemyHead: histMed(a.hE), medAllyHead: histMed(a.hA), enemyHeadInView: share(a.visE, a.n), enemyNearerThanAlly: share(a.eCloser, a.n) });
  }
  const allW = c => { const a = { n: 0, visE: 0, eCloser: 0, hE: new Array(HIST).fill(0), hA: new Array(HIST).fill(0) }; for (let w = 0; w < NW100; w++) { const b = cells[w][c]; a.n += b.n; a.visE += b.visE; a.eCloser += b.eCloser; addArr(a.hE, b.hE); addArr(a.hA, b.hA); } return a; };
  const overall = [0, 1, 2].map(c => { const a = allW(c); return { cls: CLASS_NAMES[c], turns: a.n, medEnemyHead: histMed(a.hE), q25EnemyHead: histQ(a.hE, 0.25), medAllyHead: histMed(a.hA), q75AllyHead: histQ(a.hA, 0.75), enemyHeadInView: share(a.visE, a.n), enemyNearerThanAlly: share(a.eCloser, a.n) }; });
  const approach = [0, 1, 2].map(c => { const a = appr[c]; return { cls: CLASS_NAMES[c],
    enemyVisibleMoves: a.nE, towardEnemy: share(a.aE, a.nE), towardEnemyRandom: share(a.bE, a.nE), awayEnemy: share(a.rE, a.nE), awayEnemyRandom: share(a.brE, a.nE),
    pearlVisibleMoves: a.nP, towardPearl: share(a.aP, a.nP), towardPearlRandom: share(a.bP, a.nP), awayPearl: share(a.rP, a.nP), awayPearlRandom: share(a.brP, a.nP),
    bigEnemyVisibleMoves: a.nB, towardBigEnemy: share(a.aB, a.nB), towardBigEnemyRandom: share(a.bB, a.nB), awayBigEnemy: share(a.rB, a.nB), awayBigEnemyRandom: share(a.brB, a.nB) }; });
  return { overall, byWindow: dist, approach };
}

function aggregate(keys, feats, results, checks) {
  const broken = new Set();
  for (const k of keys) { const f = feats.get(k); for (const s of TEAMS) if (f.meta.teams[s].name === SSS && f[s].splits.length < SSS_BROKEN_SPLITS) broken.add(k); }
  const mkSide = (k, s) => { const f = feats.get(k), o = s === 'A' ? 'B' : 'A'; return { k, f, g: results.get(k), s, o, team: f.meta.teams[s].name, opp: f.meta.teams[o].name, win: f.meta.winner === s, rounds: f.meta.rounds, elim: f.meta.endReason === 'teamEliminated', map: f.meta.map }; };
  const used = keys.filter(k => !broken.has(k) && results.has(k));
  const sides = []; for (const k of used) for (const s of TEAMS) sides.push(mkSide(k, s));
  const pooled = sides.filter(x => x.team !== SSS);
  const teamMeta = {};
  for (const k of keys) { const f = feats.get(k); for (const s of TEAMS) { const t = f.meta.teams[s]; const m = teamMeta[t.name] = teamMeta[t.name] || { rank: t.rank, elo: t.elo, gamesAll: 0, winsAll: 0 }; m.gamesAll++; if (f.meta.winner === s) m.winsAll++; } }
  const order = Object.keys(teamMeta).sort((a, b) => (teamMeta[a].rank ?? 999) - (teamMeta[b].rank ?? 999) || a.localeCompare(b));
  const byTeam = groupBy(pooled, x => x.team);
  const perTeam = f => { const o = {}; for (const t of order) if (byTeam.has(t)) o[t] = f(byTeam.get(t)); return o; };

  const out = {
    meta: {
      generated: new Date().toISOString(), keys: keys.length, parsed: results.size, gamesUsed: used.length, sssBrokenExcluded: [...broken].sort(),
      gameLength: { all: { before100: keys.filter(k => feats.get(k).meta.rounds < 100).length, reached500: keys.filter(k => feats.get(k).meta.rounds === 500).length, eliminated: keys.filter(k => feats.get(k).meta.endReason === 'teamEliminated').length },
        used: { before100: used.filter(k => feats.get(k).meta.rounds < 100).length, reached500: used.filter(k => feats.get(k).meta.rounds === 500).length, eliminated: used.filter(k => feats.get(k).meta.endReason === 'teamEliminated').length } },
      sidesPooled: pooled.length, checks,
      definitions: {
        side: 'one team in one game; per-side rates divide by the number of sides',
        exclusion: `games where ${SSS} made fewer than ${SSS_BROKEN_SPLITS} splits are dropped entirely; ${SSS}'s side is left out of pooled and per-team tables in its other games`,
        splitCats: '2+2: L=4; half: |2c-L|<=1; peel: child 2-3 (not half); stub: parent keeps 2-3 (not half); other: rest (L parent length before, c child length)',
        selfKill: "death reason A with why 'suicide' (no MOVE/SPLIT) or 'split' (illegal split)",
        dropCats: 'WS-free: W or S death on the first step while at least one neighbour tile was free (not kelp, no body); WS-trapped: none free; WS-sprint: fatal later step',
        kingAtDrop: "the team's longest other dragon when the death happened (ties: lowest id)", longestAtEat: "eater's length before the pearl >= every other dragon of its team",
        pearlWindows: 'a pearl counts as eaten within T rounds if eaten in rounds r..r+T of the death round r',
        distances: 'torus Manhattan (moves) or Chebyshev (vision) between heads; kelp and portals ignored',
        approach: 'first step of a move with a free first step and >=1 free neighbour; target = nearest enemy head in the 7x7 window or nearest visible pearl; random = share of free neighbour steps that would reduce (or increase) the Manhattan distance',
        units: 'timeline medians over sides whose game is still running at r (r < rounds; r = 500 only for games that reached 500)',
        lenClasses: CLASS_NAMES,
      },
    },
    teams: {},
  };
  for (const t of order) {
    const L = byTeam.get(t) || [];
    out.teams[t] = { ...teamMeta[t], gamesUsed: L.length, winsUsed: L.filter(x => x.win).length };
  }

  // Q1
  out.q1 = { pooled: splitStats(pooled), byTeam: perTeam(splitStats), units: { pooled: unitsOverTime(pooled), byTeam: perTeam(unitsOverTime) },
    bigSplitFates: { pooled: bigSplitFates(pooled), byTeam: perTeam(bigSplitFates) } };
  // Q2
  out.q2 = { splitBorn: fateStats(pooled, true), initial: fateStats(pooled, false), byTeam: perTeam(L => { const f = fateStats(L, true); return { n: f.n, perSide: f.perSide, aliveAtEnd: f.aliveAtEnd, medAgeAtDeath: f.medAgeAtDeath, diedWithin5: f.diedWithin[5].died, diedWithin20: f.diedWithin[20].died, causes: f.causes }; }) };
  // Q3
  const allDeaths = []; for (const x of pooled) for (const d of sideDeaths(x)) allDeaths.push(d);
  const unitRatesOut = { pooled: unitRates(pooled), byTeam: perTeam(unitRates) };
  const modesOut = { pooled: deathModes(pooled), byTeam: perTeam(deathModes) };
  const wsTrappedBlockers = blockers(allDeaths.filter(d => dropCat(d) === 'WS-trapped'));
  const dropByCat = {}; for (const c of DROP_CATS) dropByCat[c] = fateTable(allDeaths.filter(d => dropCat(d) === c));
  const smallDeaths = allDeaths.filter(d => d.len <= 3);
  const dropByCatLe3 = {}; for (const c of DROP_CATS) dropByCatLe3[c] = fateTable(smallDeaths.filter(d => dropCat(d) === c));
  const late = allDeaths.filter(d => d.r >= 250);
  const dropByCatLate = {}; for (const c of DROP_CATS) dropByCatLate[c] = fateTable(late.filter(d => dropCat(d) === c));
  out.q3 = {
    pooled: selfKillStats(pooled), byTeam: perTeam(selfKillStats),
    dropsByCategory: dropByCat, dropsByCategoryLen2to3: dropByCatLe3, dropsByCategoryFromR250: dropByCatLate,
    deathCategoryCounts: counts(allDeaths, dropCat),
    deathModes: modesOut, unitRates: unitRatesOut, wsTrappedBlockers, trappedByCause: trappedByCause(allDeaths),
    aDeathWhy: counts(allDeaths.filter(d => d.reason === 'A'), d => d.why),
    wsFree: { pooled: wsFreeStats(pooled), byTeam: perTeam(wsFreeStats) },
    kingDiet: { pooled: kingDiet(pooled), byTeam: perTeam(kingDiet) },
  };
  // Q4
  out.q4 = { pooled: killStats(pooled), byTeam: perTeam(killStats), hPairs: hPairs(pooled), ram: { pooled: ramStats(pooled), byTeam: perTeam(ramStats) } };
  out.q4.suppression = { r100: suppressionIndex(sides, 100, order), r200: suppressionIndex(sides, 200, order) };
  out.q4.cheji = chejiStudy(sides.filter(x => x.team === 'cheji bt'));
  out.q4.cheji.opponentUnitsVsCheji = opponentsVs(sides, 'cheji bt');
  out.q4.eliminators = perTeam(L => { const w = L.filter(x => x.win), e = w.filter(x => x.elim); return { games: L.length, wins: w.length, elimWins: e.length, elimLosses: L.filter(x => !x.win && x.elim).length, medElimRound: med(e.map(x => x.rounds)) }; });
  // Q5
  out.q5 = { pooled: geoStats(pooled), byTeam: perTeam(L => { const g = geoStats(L); return { overall: g.overall, approach: g.approach }; }) };
  // Q6 style cards
  out.q6 = order.filter(t => byTeam.has(t)).map(t => {
    const L = byTeam.get(t), s1 = out.q1.byTeam[t], s3 = out.q3.byTeam[t], s4 = out.q4.byTeam[t], dm = out.q3.deathModes.byTeam[t];
    const fin = L.map(x => x.f.meta.final[x.s]);
    return { team: t, rank: teamMeta[t].rank, elo: teamMeta[t].elo, games: L.length, winRate: share(L.filter(x => x.win).length, L.length),
      elimWinShare: share(L.filter(x => x.win && x.elim).length, L.filter(x => x.win).length),
      splitsPerGame: s1.perSideMean, medChildLen: s1.childLen.median, peelShare: s1.cats.peel, halfShare: +((s1.cats['2+2'] || 0) + (s1.cats.half || 0)).toFixed(4),
      selfKillsPerGame: s3.perSide, selfKillShareOfDeaths: s3.shareOfDeaths, selfKillWhy: s3.why, selfFreePerGame: dm['self-free'], selfTrappedPerGame: dm['self-trapped'],
      wsFreePerGame: dm['WS-free'], wsTrappedPerGame: dm['WS-trapped'], deathsPerGame: dm.deathsPerSide,
      oKillsPerGame: s4.oKillsPerSide, hTradesPerGame: s4.hTradesPerSide, hShareOfKills: s4.hShareOfKills, hTradedUp: s4.h.tradedUp,
      finalUnitsMedian: med(fin.map(v => v.dragonCount)), finalLongestMedian: med(fin.map(v => v.longestDragon)),
      finalLongestMedianFull: med(L.filter(x => x.rounds === 500).map(x => x.f.meta.final[x.s].longestDragon)),
      unitsR200: (out.q1.units.byTeam[t].find(u => u.r === 200) || {}).units };
  });
  // SSS separately
  out.sss = sssStudy(keys, feats, results, broken, mkSide);
  return out;
}

// Ramming when another head is one step away (per length class): observed share vs uniform choice among free steps + rams.
function ramStats(list) {
  const acc = Array.from({ length: 3 }, () => ({ nE: 0, ramE: 0, rndE: 0, nA: 0, ramA: 0, rndA: 0 }));
  for (const x of list) { const r = x.g.geo[x.s].ram; for (let c = 0; c < 3; c++) for (const k of Object.keys(acc[c])) acc[c][k] += r[c][k]; }
  return acc.map((a, c) => ({ cls: CLASS_NAMES[c], enemyAdjTurns: a.nE, ramEnemy: share(a.ramE, a.nE), ramEnemyRandom: share(a.rndE, a.nE), allyAdjTurns: a.nA, ramAlly: share(a.ramA, a.nA), ramAllyRandom: share(a.rndA, a.nA) }));
}
// What happens after big splits: the stub parent of 'stub' splits and the small child of 'peel' splits (parents L >= 8).
function bigSplitFates(list) {
  const stub = [], peel = [];
  for (const x of list) {
    if (!x.g._rows) { x.g._rows = new Map(); for (const t of x.g.dragons) x.g._rows.set(t[0], t); }
    for (const t of sideSplits(x)) {
      if (t[2] < 8) continue;
      const cat = splitCat(t[2], t[3]);
      if (cat !== 'stub' && cat !== 'peel') continue;
      const who = x.g._rows.get(cat === 'stub' ? t[5] : t[6]); // stub: the parent keeps the head part; peel: the child
      const dead = who && who[6] >= 0, d = dead ? x.g.deaths[who[7]] : null;
      // grew: the piece was longer at its death (or at the end) than right after the split (for a stub, maxLen would include the pre-split body)
      const pieceLen = cat === 'stub' ? t[2] - t[3] : t[3], endLen = who ? (d ? d.len : who[8]) : 0;
      (cat === 'stub' ? stub : peel).push({ r: t[1], L: t[2], free: t[11], dE: t[12], king: t[7] === 2, dt: dead ? who[6] - t[1] : null, mode: d ? modeCat(d) : 'alive', obs: x.rounds - 1 - t[1], grew: endLen > pieceLen });
    }
  }
  const sum1 = rs => ({ n: rs.length, medRound: med(rs.map(s => s.r)), medL: med(rs.map(s => s.L)), parentTrapped: share(rs.filter(s => s.free === 0).length, rs.length), enemyHeadWithin2: share(rs.filter(s => s.dE <= 2).length, rs.length),
    enemyHeadInView: share(rs.filter(s => s.dE <= 3).length, rs.length), byKing: share(rs.filter(s => s.king).length, rs.length),
    pieceDiedSameRound: share(rs.filter(s => s.dt === 0).length, rs.length), pieceDiedWithin5: share(rs.filter(s => s.dt !== null && s.dt <= 5).length, rs.filter(s => s.obs >= 5).length),
    pieceDiedWithin20: share(rs.filter(s => s.dt !== null && s.dt <= 20).length, rs.filter(s => s.obs >= 20).length), pieceAliveAtEnd: share(rs.filter(s => s.dt === null).length, rs.length),
    pieceGrew: share(rs.filter(s => s.grew).length, rs.length), pieceDeathModes: shares(counts(rs.filter(s => s.dt !== null), s => s.mode)) });
  return { stub: sum1(stub), peel: sum1(peel) };
}
// W/S deaths with a free neighbour (possible deliberate crashes): when, how long, where their pearls go.
function wsFreeStats(list) {
  const rs = []; for (const x of list) for (const d of sideDeaths(x)) if (dropCat(d) === 'WS-free') rs.push(d);
  return { n: rs.length, perSide: +(rs.length / Math.max(1, list.length)).toFixed(1), round: { p10: quant(rs.map(d => d.r), 0.1), median: med(rs.map(d => d.r)), p90: quant(rs.map(d => d.r), 0.9) },
    kelp: share(rs.filter(d => d.reason === 'W').length, rs.length), intoNeck: share(rs.filter(d => d.reason === 'S' && d.neck === 1).length, rs.filter(d => d.reason === 'S').length),
    lenMedian: med(rs.map(d => d.len)), drops: fateTable(rs) };
}
// Share of each death cause that happened with no free neighbour (movers only) or on a later sprint step.
function trappedByCause(recs) {
  const o = {};
  for (const c of CAUSES) { const rs = recs.filter(d => cause(d) === c && d.mover); o[c] = { n: rs.length, trapped: share(rs.filter(d => d.freeN === 0).length, rs.length), laterSprintStep: share(rs.filter(d => d.step > 0).length, rs.length) }; }
  return o;
}
// Head-on collisions by the pair of lengths (each collision once, from the rammer's side).
function hPairs(list) {
  const cls = L => L <= 3 ? String(L) : L <= 9 ? '4-9' : '10+';
  const m = {};
  for (const x of list) for (const d of sideDeaths(x)) if (d.reason === 'H' && d.mover && d.hitTeam === x.o) {
    const a = Math.min(d.len, d.hitLen), b = Math.max(d.len, d.hitLen), k = cls(a) + ' v ' + cls(b); m[k] = (m[k] || 0) + 1;
  }
  const n = sum(Object.values(m)); return { n, shares: shares(m), anyLen10plus: share(Object.entries(m).filter(([k]) => k.includes('10+')).reduce((a, [, v]) => a + v, 0), n) };
}
// How much smaller the opponent is at round r than usual: for each side, the opponent's units (and longest) at r minus
// the opponent's median at r in its games against other teams; median per team (sides still running at r).
function suppressionIndex(sides, r, order) {
  const run = sides.filter(x => r < x.rounds && x.team !== SSS && x.opp !== SSS), cache = new Map();
  const base = (opp, excl, f) => {
    const k = opp + '|' + excl + '|' + f;
    if (!cache.has(k)) cache.set(k, med(run.filter(y => y.team === opp && y.opp !== excl).map(y => y.f[y.s].timeline[r / 10][f])));
    return cache.get(k);
  };
  const o = {};
  for (const t of order) {
    const L = run.filter(x => x.team === t); if (!L.length) continue;
    const du = [], dl = [];
    for (const x of L) {
      const bu = base(x.opp, t, 'units'), bl = base(x.opp, t, 'longest');
      if (bu !== null) du.push(x.f[x.o].timeline[r / 10].units - bu);
      if (bl !== null) dl.push(x.f[x.o].timeline[r / 10].longest - bl);
    }
    o[t] = { sides: L.length, oppUnitsDiffMedian: med(du), oppLongestDiffMedian: med(dl) };
  }
  return o;
}
// Units of each team at r50/r100/r150 against `target` versus against everyone else (median, games still running).
function opponentsVs(sides, target) {
  const teams = [...new Set(sides.filter(x => x.opp === target && x.team !== SSS).map(x => x.team))];
  return teams.map(t => {
    const vs = sides.filter(x => x.team === t && x.opp === target), oth = sides.filter(x => x.team === t && x.opp !== target && x.opp !== SSS);
    const o = { team: t, gamesVs: vs.length, gamesOther: oth.length, winsVs: vs.filter(x => x.win).length };
    for (const r of [50, 100, 150]) {
      const u = x => x.f[x.s].timeline[r / 10].units;
      o['r' + r] = { vs: med(vs.filter(x => r < x.rounds).map(u)), other: med(oth.filter(x => r < x.rounds).map(u)),
        nVs: vs.filter(x => r < x.rounds).length, nOther: oth.filter(x => r < x.rounds).length,
        vsCarried: med(vs.map(u)), otherCarried: med(oth.map(u)) }; // carried: ended games keep their final state (0 if eliminated)
    }
    return o;
  });
}

function chejiStudy(all) {
  const notBroken = all; // callers already dropped the SSS-broken games
  const wins = notBroken.filter(x => x.win), elimWins = wins.filter(x => x.elim);
  const perGame = elimWins.map(x => {
    const od = oppDeaths(x), c = counts(od, d => cause(d));
    const myO = od.filter(d => d.reason === 'O' && d.hitTeam === x.s), myH = od.filter(d => d.reason === 'H' && d.team === x.o && ((d.mover && d.hitTeam === x.s) || (!d.mover && d.byTeam === x.s)));
    return { key: x.k, map: x.map, opp: x.opp, endRound: x.rounds, enemyDeaths: od.length, enemyCauses: c, oKills: myO.length, hTrades: myH.length,
      enemyPeakUnits: Math.max(...x.f[x.o].timeline.map(t => t.units)), enemyPeakLongest: Math.max(...x.f[x.o].timeline.map(t => t.longest)),
      finalUnits: x.f.meta.final[x.s].dragonCount, finalLongest: x.f.meta.final[x.s].longestDragon };
  });
  // enemy and own state over absolute rounds (games still running) and aligned to the end round
  const tlAbs = [];
  for (let r = 0; r <= 500; r += 50) {
    const run = elimWins.filter(x => r < x.rounds);
    tlAbs.push({ r, games: run.length, enemyUnits: med(run.map(x => x.f[x.o].timeline[r / 10].units)), enemyTotal: med(run.map(x => x.f[x.o].timeline[r / 10].total)), enemyLongest: med(run.map(x => x.f[x.o].timeline[r / 10].longest)),
      ownUnits: med(run.map(x => x.f[x.s].timeline[r / 10].units)), ownTotal: med(run.map(x => x.f[x.s].timeline[r / 10].total)), ownLongest: med(run.map(x => x.f[x.s].timeline[r / 10].longest)) });
  }
  const tlEnd = [];
  for (const back of [200, 150, 100, 50, 20, 10]) {
    const v = elimWins.filter(x => x.rounds - back >= 0).map(x => { const i = Math.max(0, Math.floor((x.rounds - back) / 10)); return { e: x.f[x.o].timeline[i], m: x.f[x.s].timeline[i] }; });
    tlEnd.push({ roundsBeforeEnd: back, games: v.length, enemyUnits: med(v.map(t => t.e.units)), enemyTotal: med(v.map(t => t.e.total)), enemyLongest: med(v.map(t => t.e.longest)), ownUnits: med(v.map(t => t.m.units)), ownLongest: med(v.map(t => t.m.longest)) });
  }
  // enemy deaths by cause and 50-round window before the end, in elimination wins
  const byBack = {};
  for (const x of elimWins) for (const d of oppDeaths(x)) {
    const back = x.rounds - 1 - d.r, b = back < 10 ? '0-9' : back < 50 ? '10-49' : back < 100 ? '50-99' : back < 200 ? '100-199' : '200+';
    const c = d.reason === 'O' && d.hitTeam === x.s ? 'O-by-cheji' : d.reason === 'H' && ((d.mover && d.hitTeam === x.s) || (!d.mover && d.byTeam === x.s)) ? 'H-with-cheji' : cause(d);
    byBack[b] = byBack[b] || {}; byBack[b][c] = (byBack[b][c] || 0) + 1;
  }
  const lenLost = {}; // enemy length lost by cause
  for (const x of elimWins) for (const d of oppDeaths(x)) {
    const c = d.reason === 'O' && d.hitTeam === x.s ? 'O-by-cheji' : d.reason === 'H' && ((d.mover && d.hitTeam === x.s) || (!d.mover && d.byTeam === x.s)) ? 'H-with-cheji' : cause(d);
    lenLost[c] = (lenLost[c] || 0) + d.len;
  }
  // last enemy dragon: how it died
  const lastDeath = counts(elimWins, x => { const od = oppDeaths(x); const d = od[od.length - 1]; if (!d) return 'none'; return d.reason === 'O' && d.hitTeam === x.s ? 'O-by-cheji' : d.reason === 'H' && ((d.mover && d.hitTeam === x.s) || (!d.mover && d.byTeam === x.s)) ? 'H-with-cheji' : cause(d); });
  const kills = killStats(elimWins);
  return {
    games: notBroken.length, wins: wins.length, elimWins: elimWins.length, roundLimitWins: wins.filter(x => !x.elim).length, losses: notBroken.length - wins.length,
    lossesEliminated: notBroken.filter(x => !x.win && x.elim).length,
    elimRound: { p10: quant(elimWins.map(x => x.rounds), 0.1), median: med(elimWins.map(x => x.rounds)), p90: quant(elimWins.map(x => x.rounds), 0.9) },
    finalInElimWins: { units: med(elimWins.map(x => x.f.meta.final[x.s].dragonCount)), longest: med(elimWins.map(x => x.f.meta.final[x.s].longestDragon)), total: med(elimWins.map(x => x.f.meta.final[x.s].totalLength)) },
    finalInRoundLimitGames: { units: med(notBroken.filter(x => x.rounds === 500).map(x => x.f.meta.final[x.s].dragonCount)), longest: med(notBroken.filter(x => x.rounds === 500).map(x => x.f.meta.final[x.s].longestDragon)), oppLongest: med(notBroken.filter(x => x.rounds === 500).map(x => x.f.meta.final[x.o].longestDragon)), games: notBroken.filter(x => x.rounds === 500).length, wins: notBroken.filter(x => x.rounds === 500 && x.win).length },
    enemyPeak: { units: med(perGame.map(g => g.enemyPeakUnits)), longest: med(perGame.map(g => g.enemyPeakLongest)) },
    timelineAbs: tlAbs, timelineToEnd: tlEnd, enemyDeathsByRoundsBeforeEnd: byBack, enemyLengthLostByCause: shares(lenLost), lastEnemyDeath: lastDeath,
    killsInElimWins: kills, killsInOtherGames: killStats(notBroken.filter(x => !(x.win && x.elim))), perGame, ramInElimWins: ramStats(elimWins), ramInOtherGames: ramStats(notBroken.filter(x => !(x.win && x.elim))),
    opponents: counts(notBroken, x => x.opp),
  };
}

function sssStudy(keys, feats, results, broken, mkSide) {
  const all = []; for (const k of keys) { if (!results.has(k)) continue; for (const s of TEAMS) { const x = mkSide(k, s); if (x.team === SSS) all.push(x); } }
  const part = L => {
    const d = []; for (const x of L) for (const r of sideDeaths(x)) d.push(r);
    return { games: L.length, wins: L.filter(x => x.win).length, eliminated: L.filter(x => !x.win && x.elim).length, opponents: counts(L, x => x.opp), maps: counts(L, x => x.map),
      splitsPerGame: mean(L.map(x => sideSplits(x).length)), deathsPerGame: mean(L.map(x => sideDeaths(x).length)), deathCauses: counts(d, cause),
      medRounds: med(L.map(x => x.rounds)), finalLongestMedian: med(L.map(x => x.f.meta.final[x.s].longestDragon)), firstDeathRoundMedian: med(L.map(x => { const dd = sideDeaths(x); return dd.length ? dd[0].r : null; }).filter(v => v !== null)) };
  };
  return { broken: part(all.filter(x => broken.has(x.k))), normal: part(all.filter(x => !broken.has(x.k))), brokenKeys: all.filter(x => broken.has(x.k)).map(x => x.k) };
}

// Compare the reconstruction with the features row (deaths and splits must be identical).
function compareFeatures(g, f) {
  let bad = 0;
  for (const s of TEAMS) {
    const mine = g.deaths.filter(d => d.team === s), theirs = f[s].deaths;
    if (mine.length !== theirs.length) { bad += Math.abs(mine.length - theirs.length) || 1; continue; }
    for (let i = 0; i < mine.length; i++) {
      const a = mine[i], b = theirs[i];
      for (const k of ['r', 'id', 'reason', 'why', 'len', 'born', 'mover', 'hitTeam', 'hitLen', 'byTeam', 'byLen']) if (a[k] !== b[k] && !(a[k] === undefined && b[k] === undefined)) { bad++; break; }
    }
    const ms = g.splits.filter(t => t[0] === TI[s]), ts = f[s].splits;
    if (ms.length !== ts.length) { bad += Math.abs(ms.length - ts.length) || 1; continue; }
    for (let i = 0; i < ms.length; i++) if (ms[i][1] !== ts[i][0] || ms[i][2] !== ts[i][1] || ms[i][3] !== ts[i][2] || ms[i][4] !== ts[i][3]) bad++;
  }
  return bad;
}

// ---------------------------------------------------------------------------------------------------------------
// Report printing
function table(title, head, rows) {
  const w = head.map((h, i) => Math.max(String(h).length, ...rows.map(r => String(r[i]).length)));
  const line = r => r.map((c, i) => i === 0 ? String(c).padEnd(w[i]) : String(c).padStart(w[i])).join('  ');
  console.log('\n## ' + title); console.log(line(head)); for (const r of rows) console.log(line(r));
}
function printReport(o) {
  const teams = Object.keys(o.teams).filter(t => o.q1.byTeam[t]);
  const short = t => t.length > 22 ? t.slice(0, 21) + '~' : t;
  const cats5 = c => [pct(c['2+2']), pct(c.half), pct(c.peel), pct(c.stub), pct(c.other)];
  console.log(`\ngames used ${o.meta.gamesUsed}/${o.meta.keys} (SSS-broken excluded: ${o.meta.sssBrokenExcluded.length}), pooled sides ${o.meta.sidesPooled}, game length ${JSON.stringify(o.meta.gameLength)}`);
  // Q1
  const p1 = o.q1.pooled;
  console.log(`\n# Q1 split anatomy: ${p1.splits} splits, per side mean ${p1.perSideMean} median ${p1.perSideMedian}, sides without splits ${p1.sidesWithoutSplits}`);
  console.log('parent len', JSON.stringify(p1.parentLen)); console.log('child len', JSON.stringify(p1.childLen)); console.log('child share', JSON.stringify(p1.childShare));
  console.log('cats', JSON.stringify(p1.cats), 'parentStrictLongest', p1.parentStrictLongest, 'parentSplitBorn', p1.parentSplitBorn, 'unitsBefore>=60', p1.unitsBeforeAtLeast60);
  console.log('parents L>=8', JSON.stringify(p1.bigParent)); console.log('strict-longest parents L>=8', JSON.stringify(p1.kingSplits));
  table('Q1 pooled by 100-round window', ['window', 'sides', 'splits/side', 'medL', 'medC', '2+2', 'half', 'peel', 'stub', 'other', 'c=2', 'c=3', 'atCap'],
    p1.byWindow.map(b => [b.w, b.sidesRunning, fmt(b.perSide), fmt(b.medParentLen), fmt(b.medChildLen), ...cats5(b.cats), pct(b.childLen['2']), pct(b.childLen['3']), pct(b.atCap)]));
  table('Q1 by team', ['team', 'rank', 'games', 'splits/g', 'medL', 'p90L', 'medC', 'c=2', '2+2', 'half', 'peel', 'stub', 'other', 'atCap', 'L>=8 n', 'L>=8 c<=3', 'L>=8 stub', 'L>=8 half'],
    teams.map(t => { const s = o.q1.byTeam[t]; return [short(t), o.teams[t].rank ?? '-', s.sides, fmt(s.perSideMean), fmt(s.parentLen.median), fmt(s.parentLen.p90), fmt(s.childLen.median), pct(s.childLen.bins['2']), ...cats5(s.cats), pct(s.unitsBeforeAtLeast60), s.bigParent.n, pct(s.bigParent.childLe3), pct(s.bigParent.cats.stub), pct(s.bigParent.cats.half)]; }));
  const bsf = o.q1.bigSplitFates;
  console.log('big split fates (stub = parent keeps the head part; peel = small child)', JSON.stringify(bsf.pooled));
  table('Q1 stub splits (L>=8) by team: situation and the stub', ['team', 'n', 'medL', 'medR', 'king', 'trapped', 'enemy<=2', 'enemyInView', 'stubDied0', 'stubDied<=5', 'stubAlive', 'stubGrew', 'stub WS', 'stub self', 'stub H'],
    teams.filter(t => bsf.byTeam[t].stub.n >= 20).map(t => { const v = bsf.byTeam[t].stub, m = v.pieceDeathModes; return [short(t), v.n, fmt(v.medL), fmt(v.medRound), pct(v.byKing), pct(v.parentTrapped), pct(v.enemyHeadWithin2), pct(v.enemyHeadInView), pct(v.pieceDiedSameRound), pct(v.pieceDiedWithin5), pct(v.pieceAliveAtEnd), pct(v.pieceGrew), pct((m['WS-free'] || 0) + (m['WS-trapped'] || 0) + (m['WS-sprint'] || 0)), pct((m['self-free'] || 0) + (m['self-trapped'] || 0)), pct(m['H-enemy'])]; }));
  table('Q1 splits per side by window (team, sides running)', ['team', '0-99', '100-199', '200-299', '300-399', '400-499'], teams.map(t => [short(t), ...o.q1.byTeam[t].byWindow.map(b => fmt(b.perSide))]));
  table('Q1 units median over time (pooled)', ['r', 'sides', 'units', 'unitsP90', 'longest', 'total'], o.q1.units.pooled.map(u => [u.r, u.sides, fmt(u.units), fmt(u.unitsP90), fmt(u.longest), fmt(u.total)]));
  table('Q1 units median by team', ['team', ...o.q1.units.pooled.map(u => 'r' + u.r)], teams.map(t => [short(t), ...o.q1.units.byTeam[t].map(u => fmt(u.units))]));
  table('Q1 longest median by team', ['team', ...o.q1.units.pooled.map(u => 'r' + u.r)], teams.map(t => [short(t), ...o.q1.units.byTeam[t].map(u => fmt(u.longest))]));
  // Q2
  for (const [nm, f] of [['split-born', o.q2.splitBorn], ['initial', o.q2.initial]]) {
    console.log(`\n# Q2 ${nm}: n ${f.n} (${f.perSide}/side), alive at end ${pct(f.aliveAtEnd)}, median age at death ${f.medAgeAtDeath} (p90 ${f.p90AgeAtDeath}), grew after birth ${pct(f.grewAfterBirth)}`);
    console.log('died within (age<=a | observed >= a):', Object.entries(f.diedWithin).map(([a, v]) => `${a}: ${pct(v.died)} of ${v.eligible}`).join(', '));
    console.log('causes', Object.entries(f.causes).map(([k, v]) => k + ' ' + pct(v)).join(', '));
  }
  const f2 = o.q2.splitBorn;
  table('Q2 split-born by birth length', ['birthLen', 'n', 'alive', 'medAge', ...CAUSES], BIRTH_CLASSES.map(b => { const v = f2.byBirthLen[b]; return [b, v.n, pct(v.alive), fmt(v.medAgeAtDeath), ...CAUSES.map(c => pct(v.causes[c]))]; }));
  table('Q2 split-born deaths by age at death', ['age', 'n', ...CAUSES], AGE_CLASSES.map(a => { const v = f2.byAgeAtDeath[a]; return [a, v.n, ...CAUSES.map(c => pct(v.causes[c]))]; }));
  table('Q2 split-born deaths by length at death', ['len', 'n', ...CAUSES], Object.entries(f2.byLenAtDeath).map(([b, v]) => [b, v.n, ...CAUSES.map(c => pct(v.causes[c]))]));
  table('Q2 split-born by team', ['team', 'n/g', 'alive', 'medAge', 'die<=5', 'die<=20', ...CAUSES], teams.map(t => { const v = o.q2.byTeam[t]; return [short(t), fmt(v.perSide), pct(v.aliveAtEnd), fmt(v.medAgeAtDeath), pct(v.diedWithin5), pct(v.diedWithin20), ...CAUSES.map(c => pct(v.causes[c]))]; }));
  // Q3
  const s3 = o.q3.pooled;
  console.log(`\n# Q3 self-kills pooled: ${s3.n} (${s3.perSide}/side, ${pct(s3.shareOfDeaths)} of deaths) why ${JSON.stringify(s3.why)}`);
  console.log('round', JSON.stringify(s3.round), 'len', JSON.stringify(s3.len), 'age', JSON.stringify(s3.age), 'splitBorn', s3.splitBorn, 'trapped', s3.trappedShare, 'wasLongest', s3.wasLongest);
  console.log('units median', s3.unitsMedian, '>=60', s3.unitsAtLeast60, 'other deaths >=60', s3.otherDeathsUnitsAtLeast60, 'split within 1 round', s3.splitWithin1, 'other deaths', s3.otherDeathsSplitWithin1, 'king len', s3.kingLenMedian);
  console.log('illegal split', JSON.stringify(s3.illegalSplitRequest), 'all A deaths by why', JSON.stringify(o.q3.aDeathWhy));
  console.log('trapped self-kill blockers', JSON.stringify(s3.trappedBlockers), 'WS-trapped blockers', JSON.stringify(o.q3.wsTrappedBlockers));
  console.log('free self-kills', JSON.stringify({ n: s3.free.n, perSide: s3.free.perSide, round: s3.free.round, lenMedian: s3.free.lenMedian }));
  const selfTeams = teams.filter(t => o.q3.byTeam[t].n > 0);
  table('Q3 trapped share by death cause (movers, pooled)', ['cause', 'n', 'trapped', 'laterSprintStep'], CAUSES.map(c => { const v = o.q3.trappedByCause[c]; return [c, v.n, pct(v.trapped), pct(v.laterSprintStep)]; }));
  const wf = o.q3.wsFree;
  console.log('WS-free pooled', JSON.stringify({ n: wf.pooled.n, perSide: wf.pooled.perSide, round: wf.pooled.round, kelp: wf.pooled.kelp, intoNeck: wf.pooled.intoNeck, lenMedian: wf.pooled.lenMedian }));
  table('Q3 WS-free deaths by team (W/S with a free neighbour)', ['team', 'n/g', 'r p10', 'r med', 'r p90', 'kelp', 'S neck', 'len', 'own20', 'enemy20', 'ownLongest20', 'king20', 'eaterLen', 'distKing', 'king<=2'],
    teams.filter(t => wf.byTeam[t].n >= 20).map(t => { const v = wf.byTeam[t], d = v.drops; return [short(t), fmt(v.perSide), fmt(v.round.p10), fmt(v.round.median), fmt(v.round.p90), pct(v.kelp), pct(v.intoNeck), fmt(v.lenMedian), pct(d.own20), pct(d.enemy20), pct(d.ownLongest20), pct(d.ownKingAtDrop20), fmt(d.ownEaterLenMedian), fmt(d.distKingMedian), pct(d.distKingLe2)]; }));
  console.log('death modes pooled', JSON.stringify(o.q3.deathModes.pooled));
  table('Q3 death modes per game by team', ['team', 'deaths/g', ...MODE_CATS, 'trapped%', 'free%'], teams.map(t => { const v = o.q3.deathModes.byTeam[t]; return [short(t), fmt(v.deathsPerSide), ...MODE_CATS.map(k => fmt(v[k])), pct(v.trappedShare), pct(v.freeShare)]; }));
  table('Q3 self-kills by team', ['team', 'n/g', '%deaths', 'why', 'r p10', 'r med', 'r p90', 'len med', 'len2', 'len3', 'age0', 'ageMed', 'trapped', 'free/g', 'free r med', 'units med', 'u>=60', 'oth u>=60'],
    selfTeams.map(t => { const v = o.q3.byTeam[t]; return [short(t), fmt(v.perSide), pct(v.shareOfDeaths), Object.keys(v.why).join('/'), fmt(v.round.p10), fmt(v.round.median), fmt(v.round.p90), fmt(v.len.median), pct(v.len.bins['2']), pct(v.len.bins['3']), pct(v.age.age0), fmt(v.age.median), pct(v.trappedShare), fmt(v.free.perSide), fmt(v.free.round.median), fmt(v.unitsMedian), pct(v.unitsAtLeast60), pct(v.otherDeathsUnitsAtLeast60)]; }));
  const dropRow = (nm, v) => [nm, v.deaths, v.pearls, pct(v.own5), pct(v.own10), pct(v.own20), pct(v.enemy20), pct(v.ownLongest20), pct(v.ownKingAtDrop20), pct(v.neverEaten), fmt(v.ownPearls20PerDeath), fmt(v.ownEaterLenMedian), fmt(v.distKingMedian), pct(v.distKingLe2)];
  const dropHead = ['team', 'deaths', 'pearls', 'own5', 'own10', 'own20', 'enemy20', 'ownLongest20', 'king20', 'never', 'own20/death', 'eaterLen', 'distKing', 'king<=2'];
  table('Q3 self-kill drops by team (all)', dropHead, selfTeams.map(t => dropRow(short(t), o.q3.byTeam[t].drops)));
  table('Q3 self-kill drops by team (free only)', dropHead, selfTeams.filter(t => o.q3.byTeam[t].free.n > 0).map(t => dropRow(short(t), o.q3.byTeam[t].free.drops)));
  table('Q3 self-kill drops by team (trapped only)', dropHead, selfTeams.filter(t => o.q3.byTeam[t].trapped.n > 0).map(t => dropRow(short(t), o.q3.byTeam[t].trapped.drops)));
  for (const [nm, tb] of [['all deaths', o.q3.dropsByCategory], ['deaths at length 2-3', o.q3.dropsByCategoryLen2to3], ['deaths from r250', o.q3.dropsByCategoryFromR250]])
    table('Q3 drop fates by death category, ' + nm, ['category', 'deaths', 'pearls', 'lenMed', 'own5', 'own10', 'own20', 'enemy5', 'enemy20', 'ownLongest20', 'king20', 'never', 'eaterLen', 'distKing', 'king<=2'],
      DROP_CATS.map(c => { const v = tb[c]; return [c, v.deaths, v.pearls, fmt(v.lenMedian), pct(v.own5), pct(v.own10), pct(v.own20), pct(v.enemy5), pct(v.enemy20), pct(v.ownLongest20), pct(v.ownKingAtDrop20), pct(v.neverEaten), fmt(v.ownEaterLenMedian), fmt(v.distKingMedian), pct(v.distKingLe2)]; }));
  table('Q3 per 1000 dragon-turns by team unit count (pooled)', ['units', 'turns', 'selfFree', 'selfTrapped', 'wsTrapped', 'otherDeaths', 'splits'], o.q3.unitRates.pooled.map(v => [v.units, v.turns, fmt(v.selfFree), fmt(v.selfTrapped), fmt(v.wsTrapped), fmt(v.otherDeaths), fmt(v.splits)]));
  for (const t of selfTeams.filter(t => o.q3.byTeam[t].perSide >= 10))
    table(`Q3 per 1000 dragon-turns by unit count: ${t}`, ['units', 'turns', 'selfFree', 'selfTrapped', 'wsTrapped', 'otherDeaths', 'splits'], o.q3.unitRates.byTeam[t].map(v => [v.units, v.turns, fmt(v.selfFree), fmt(v.selfTrapped), fmt(v.wsTrapped), fmt(v.otherDeaths), fmt(v.splits)]));
  const kd = o.q3.kingDiet;
  table("Q3 pearls eaten by the team's current longest: source", ['team', 'eaten/g', 'natural', 'ownSelfKill', 'ownOther', 'enemy', 'others:natural', 'others:ownSelf'],
    [['POOLED', fmt(kd.pooled.perSideLongestEaten), pct(kd.pooled.longest.natural), pct(kd.pooled.longest.ownSelfKill), pct(kd.pooled.longest.ownOtherDeath), pct(kd.pooled.longest.enemyDeath), pct(kd.pooled.others.natural), pct(kd.pooled.others.ownSelfKill)],
      ...teams.map(t => { const v = kd.byTeam[t]; return [short(t), fmt(v.perSideLongestEaten), pct(v.longest.natural), pct(v.longest.ownSelfKill), pct(v.longest.ownOtherDeath), pct(v.longest.enemyDeath), pct(v.others.natural), pct(v.others.ownSelfKill)]; })]);
  table("Q3 longest's diet by window (pooled)", ['from r', 'eaten', 'natural', 'ownSelfKill', 'ownOther', 'enemy'], kd.pooled.longestByWindow.map(v => [v.w, v.total, pct(v.natural), pct(v.ownSelfKill), pct(v.ownOtherDeath), pct(v.enemyDeath)]));
  table("Q3 longest's pearls from own deaths by death mode (share of all it ate, pooled)", ['from r', 'eaten', ...MODE_CATS, 'allFree', 'allTrapped'], kd.pooled.longestOwnDeathsByMode.map(v => [v.w, v.eaten, ...MODE_CATS.map(k => pct(v[k])), pct(v.ownFreeDeaths), pct(v.ownTrappedDeaths)]));
  table("Q3 longest's pearls from own deaths by mode, r400-499, by team", ['team', 'eaten', ...MODE_CATS, 'allFree'], teams.map(t => { const v = kd.byTeam[t].longestOwnDeathsByMode[4]; return [short(t), v.eaten, ...MODE_CATS.map(k => pct(v[k])), pct(v.ownFreeDeaths)]; }));
  for (const t of selfTeams.filter(t => o.q3.byTeam[t].perSide >= 10))
    table(`Q3 longest's diet by window: ${t}`, ['from r', 'eaten', 'natural', 'ownSelfKill', 'ownOther', 'enemy'], kd.byTeam[t].longestByWindow.map(v => [v.w, v.total, pct(v.natural), pct(v.ownSelfKill), pct(v.ownOtherDeath), pct(v.enemyDeath)]));
  // Q4
  const k4 = o.q4.pooled;
  console.log(`\n# Q4 kills pooled: enemy deaths/side ${k4.enemyDeathsPerSide}, O-kills/side ${k4.oKillsPerSide}, H trades/side ${k4.hTradesPerSide} (we rammed ${k4.hWeRammedPerSide}, they rammed ${k4.hTheyRammedPerSide}), H share ${pct(k4.hShareOfKills)}`);
  console.log('H', JSON.stringify(k4.h)); console.log('O', JSON.stringify(k4.o)); console.log('enemy death causes', JSON.stringify(k4.enemyDeathCauses));
  console.log('pearls', JSON.stringify(k4.pearls)); console.log('big deaths', JSON.stringify(k4.bigDeaths)); console.log('H by window', JSON.stringify(k4.hByWindowPerRunningSide));
  console.log('H length pairs', JSON.stringify(o.q4.hPairs));
  table('Q4 ramming when a head is one step away (pooled)', ['class', 'enemyAdj turns', 'ram enemy', 'random', 'allyAdj turns', 'ram ally', 'random'], o.q4.ram.pooled.map(v => [v.cls, v.enemyAdjTurns, pct(v.ramEnemy), pct(v.ramEnemyRandom), v.allyAdjTurns, pct(v.ramAlly), pct(v.ramAllyRandom)]));
  table('Q4 ramming by team (enemy head one step away)', ['team', 'small n', 'small ram', 'rnd', 'mid n', 'mid ram', 'rnd', 'large n', 'large ram', 'rnd', 'small ally ram'],
    teams.map(t => { const r = o.q4.ram.byTeam[t]; return [short(t), r[0].enemyAdjTurns, pct(r[0].ramEnemy), pct(r[0].ramEnemyRandom), r[1].enemyAdjTurns, pct(r[1].ramEnemy), pct(r[1].ramEnemyRandom), r[2].enemyAdjTurns, pct(r[2].ramEnemy), pct(r[2].ramEnemyRandom), pct(r[0].ramAlly)]; }));
  table('Q4 kills by team', ['team', 'enemyD/g', 'O/g', 'H/g', 'weRam/g', 'ramSprint', 'H share', 'H ourLen', 'H theirLen', 'up', 'even', 'down', 'our<=3', 'net/g', 'O blkLen', 'blk<=4', 'exp<=4', 'O victimLen'],
    teams.map(t => { const v = o.q4.byTeam[t]; return [short(t), fmt(v.enemyDeathsPerSide), fmt(v.oKillsPerSide), fmt(v.hTradesPerSide), fmt(v.hWeRammedPerSide), pct(v.h.weRammed.onSprintStep), pct(v.hShareOfKills), fmt(v.h.ourLenMedian), fmt(v.h.theirLenMedian), pct(v.h.tradedUp), pct(v.h.even), pct(v.h.tradedDown), pct(v.h.ourLe3), fmt(v.h.netLenPerSide), fmt(v.o.blockerLenMedian), pct(v.o.blockerLe4), pct(v.o.expectedLe4BySegments), fmt(v.o.victimLenMedian)]; }));
  table('Q4 H timing, pearls and big dragons by team', ['team', 'H r0', 'H r100', 'H r200', 'H r300', 'H r400', 'Hpearl us', 'Hpearl them', 'enemyP us/g', 'ourP lost/g', 'big died/g', 'big by H/g', 'H other<=3', 'killed big/g', 'by our<=3'],
    teams.map(t => { const v = o.q4.byTeam[t]; return [short(t), ...v.hByWindowPerRunningSide.map(w => fmt(w.perSide)), pct(v.pearls.hEatenByUs20), pct(v.pearls.hEatenByThem20), fmt(v.pearls.enemyPearlsEatenPerSide20), fmt(v.pearls.ourPearlsLostPerSide20), fmt(v.bigDeaths.perSide), fmt(v.bigDeaths.hEnemyPerSide), pct(v.bigDeaths.hEnemyOtherLe3), fmt(v.bigDeaths.enemyBigKilledByHPerSide), pct(v.bigDeaths.enemyBigKilledByOurLe3)]; }));
  table('Q4 opponent suppression (opponent at r minus its usual, median)', ['team', 'sides r100', 'units r100', 'longest r100', 'sides r200', 'units r200', 'longest r200'],
    teams.filter(t => o.q4.suppression.r100[t]).map(t => { const a = o.q4.suppression.r100[t], b = o.q4.suppression.r200[t] || {}; return [short(t), a.sides, fmt(a.oppUnitsDiffMedian), fmt(a.oppLongestDiffMedian), b.sides ?? '-', fmt(b.oppUnitsDiffMedian), fmt(b.oppLongestDiffMedian)]; }));
  table('Q4 eliminations by team', ['team', 'games', 'wins', 'elimWins', 'elimLosses', 'medElimRound'], teams.map(t => { const v = o.q4.eliminators[t]; return [short(t), v.games, v.wins, v.elimWins, v.elimLosses, fmt(v.medElimRound)]; }));
  const c = o.q4.cheji;
  console.log(`\n# Q4 cheji bt: games ${c.games}, wins ${c.wins} (elim ${c.elimWins}, round-limit ${c.roundLimitWins}), losses ${c.losses} (eliminated ${c.lossesEliminated})`);
  console.log('elim round', JSON.stringify(c.elimRound), 'final in elim wins', JSON.stringify(c.finalInElimWins), 'round-limit games', JSON.stringify(c.finalInRoundLimitGames), 'enemy peak', JSON.stringify(c.enemyPeak));
  table('cheji elim wins: timeline (absolute rounds, running games)', ['r', 'games', 'eUnits', 'eTotal', 'eLongest', 'ownUnits', 'ownTotal', 'ownLongest'], c.timelineAbs.map(v => [v.r, v.games, fmt(v.enemyUnits), fmt(v.enemyTotal), fmt(v.enemyLongest), fmt(v.ownUnits), fmt(v.ownTotal), fmt(v.ownLongest)]));
  table('cheji elim wins: timeline aligned to end', ['before end', 'games', 'eUnits', 'eTotal', 'eLongest', 'ownUnits', 'ownLongest'], c.timelineToEnd.map(v => [v.roundsBeforeEnd, v.games, fmt(v.enemyUnits), fmt(v.enemyTotal), fmt(v.enemyLongest), fmt(v.ownUnits), fmt(v.ownLongest)]));
  const cats = [...new Set(Object.values(c.enemyDeathsByRoundsBeforeEnd).flatMap(v => Object.keys(v)))].sort();
  table('cheji elim wins: enemy deaths by rounds before end', ['before end', ...cats], ['200+', '100-199', '50-99', '10-49', '0-9'].map(b => [b, ...cats.map(k => (c.enemyDeathsByRoundsBeforeEnd[b] || {})[k] || 0)]));
  console.log('enemy length lost by cause', JSON.stringify(c.enemyLengthLostByCause)); console.log('last enemy death', JSON.stringify(c.lastEnemyDeath));
  console.log('kills in elim wins: H', JSON.stringify(c.killsInElimWins.h)); console.log('kills in other games: H', JSON.stringify(c.killsInOtherGames.h), 'pearls', JSON.stringify(c.killsInOtherGames.pearls), 'H/side', c.killsInOtherGames.hTradesPerSide, 'enemyD/side', c.killsInOtherGames.enemyDeathsPerSide, 'Hwin', JSON.stringify(c.killsInOtherGames.hByWindowPerRunningSide));
  console.log('elim wins H/side', c.killsInElimWins.hTradesPerSide, 'enemyD/side', c.killsInElimWins.enemyDeathsPerSide, 'Hwin', JSON.stringify(c.killsInElimWins.hByWindowPerRunningSide)); console.log('O', JSON.stringify(c.killsInElimWins.o)); console.log('pearls', JSON.stringify(c.killsInElimWins.pearls));
  console.log('opponents', JSON.stringify(c.opponents));
  console.log('cheji ramming in elim wins', JSON.stringify(c.ramInElimWins)); console.log('cheji ramming in other games', JSON.stringify(c.ramInOtherGames));
  table('cheji: opponent units vs cheji / vs others (running | carried)', ['team', 'g vs', 'wins vs', 'r50 vs', 'r50 oth', 'r100 vs', 'r100 oth', 'n100 vs', 'r100 vs*', 'r100 oth*', 'r150 vs*', 'r150 oth*'],
    c.opponentUnitsVsCheji.map(v => [short(v.team), v.gamesVs, v.winsVs, fmt(v.r50.vs), fmt(v.r50.other), fmt(v.r100.vs), fmt(v.r100.other), v.r100.nVs, fmt(v.r100.vsCarried), fmt(v.r100.otherCarried), fmt(v.r150.vsCarried), fmt(v.r150.otherCarried)]));
  // Q5
  const g5 = o.q5.pooled;
  table('Q5 head distances (pooled, all rounds)', ['class', 'turns', 'medEnemy', 'q25Enemy', 'medAlly', 'q75Ally', 'enemyInView', 'enemy<ally'], g5.overall.map(v => [v.cls, v.turns, fmt(v.medEnemyHead), fmt(v.q25EnemyHead), fmt(v.medAllyHead), fmt(v.q75AllyHead), pct(v.enemyHeadInView), pct(v.enemyNearerThanAlly)]));
  table('Q5 head distances by window (pooled)', ['class', 'from r', 'turns', 'medEnemy', 'medAlly', 'enemyInView', 'enemy<ally'], g5.byWindow.map(v => [v.cls, v.w, v.turns, fmt(v.medEnemyHead), fmt(v.medAllyHead), pct(v.enemyHeadInView), pct(v.enemyNearerThanAlly)]));
  table('Q5 approach (pooled)', ['class', 'E moves', 'toward E', 'random', 'away E', 'random', 'B moves', 'toward B', 'random', 'away B', 'random', 'P moves', 'toward P', 'random', 'away P', 'random'],
    g5.approach.map(v => [v.cls, v.enemyVisibleMoves, pct(v.towardEnemy), pct(v.towardEnemyRandom), pct(v.awayEnemy), pct(v.awayEnemyRandom), v.bigEnemyVisibleMoves, pct(v.towardBigEnemy), pct(v.towardBigEnemyRandom), pct(v.awayBigEnemy), pct(v.awayBigEnemyRandom), v.pearlVisibleMoves, pct(v.towardPearl), pct(v.towardPearlRandom), pct(v.awayPearl), pct(v.awayPearlRandom)]));
  table('Q5 small fragments by team', ['team', 'turns', 'medEnemy', 'medAlly', 'inView', 'E<A', 'towardE', 'rnd', 'towardB', 'rnd', 'nB', 'towardP', 'rnd', 'L:awayE', 'L:rnd'],
    teams.map(t => { const v = o.q5.byTeam[t], s = v.overall[0], a = v.approach[0], l = v.approach[2]; return [short(t), s.turns, fmt(s.medEnemyHead), fmt(s.medAllyHead), pct(s.enemyHeadInView), pct(s.enemyNearerThanAlly), pct(a.towardEnemy), pct(a.towardEnemyRandom), pct(a.towardBigEnemy), pct(a.towardBigEnemyRandom), a.bigEnemyVisibleMoves, pct(a.towardPearl), pct(a.towardPearlRandom), pct(l.awayEnemy), pct(l.awayEnemyRandom)]; }));
  // Q6
  table('Q6 style cards', ['team', 'rank', 'g', 'win', 'elimW', 'spl/g', 'medC', 'peel', 'half', 'self/g', 'free/g', 'trap/g', 'self%D', 'WSfree/g', 'O/g', 'H/g', 'H%', 'Hup', 'finU', 'finLong', 'finLong500', 'u200'],
    o.q6.map(v => [short(v.team), v.rank ?? '-', v.games, pct(v.winRate), pct(v.elimWinShare), fmt(v.splitsPerGame), fmt(v.medChildLen), pct(v.peelShare), pct(v.halfShare), fmt(v.selfKillsPerGame), fmt(v.selfFreePerGame), fmt(v.selfTrappedPerGame), pct(v.selfKillShareOfDeaths), fmt(v.wsFreePerGame), fmt(v.oKillsPerGame), fmt(v.hTradesPerGame), pct(v.hShareOfKills), pct(v.hTradedUp), fmt(v.finalUnitsMedian), fmt(v.finalLongestMedian), fmt(v.finalLongestMedianFull), fmt(v.unitsR200)]));
  console.log('\n# SSS', JSON.stringify(o.sss, null, 1));
}

// ---------------------------------------------------------------------------------------------------------------
// Main
function readFeatures(keySet) {
  const m = new Map();
  for (const l of fs.readFileSync(FEATURES, 'utf8').split('\n')) {
    if (!l.trim()) continue;
    const mm = /^\{"meta":\{"battleId":(\d+),"gameId":(\d+)[,}]/.exec(l);
    let k = mm ? mm[1] + ':' + mm[2] : null, row = null;
    if (!k) { try { row = JSON.parse(l); k = row.meta.battleId + ':' + row.meta.gameId; } catch { continue; } }
    if (!keySet.has(k) || m.has(k)) continue;
    m.set(k, row || JSON.parse(l));
  }
  return m;
}
async function main() {
  const argv = process.argv.slice(2);
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const keysFile = path.resolve(ROOT, opt('keys', 'data/top/snapshot-20260929a.keys'));
  const outFile = path.resolve(ROOT, opt('out', 'data/top/fragment_study.json'));
  const cacheFile = opt('cache', null) ? path.resolve(opt('cache')) : null;
  const jobs = Math.min(4, Math.max(1, +opt('jobs', 4) || 4)), limit = opt('limit', null) === null ? Infinity : +opt('limit'), quiet = argv.includes('--quiet');
  const t0 = Date.now();
  const keys = [...new Set(fs.readFileSync(keysFile, 'utf8').split('\n').map(s => s.trim()).filter(Boolean))];
  const feats = readFeatures(new Set(keys));
  const missing = keys.filter(k => !feats.has(k));
  if (missing.length) { console.error(`features.jsonl lacks ${missing.length} listed games, e.g. ${missing.slice(0, 3).join(' ')}`); process.exit(1); }
  const results = new Map();
  if (cacheFile && fs.existsSync(cacheFile)) {
    for (const l of fs.readFileSync(cacheFile, 'utf8').split('\n')) { if (!l.trim()) continue; try { const r = JSON.parse(l); if (feats.has(r.key)) results.set(r.key, r.out); } catch { /* partial line */ } }
    console.log(`cache: ${results.size} games from ${cacheFile}`);
  }
  const todo = keys.filter(k => !results.has(k)).slice(0, limit);
  console.log(`games ${keys.length}, to parse ${todo.length}, jobs ${jobs}`);
  const errors = [];
  if (todo.length) {
    const cfd = cacheFile ? fs.openSync(cacheFile, 'a') : null;
    await new Promise((resolve, reject) => {
      const queue = todo.slice(); let live = 0, done = 0;
      const n = Math.min(jobs, queue.length);
      for (let i = 0; i < n; i++) {
        const child = cp.fork(__filename, ['--child'], { serialization: 'advanced', stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
        live++;
        const next = () => {
          const k = queue.shift();
          if (!k) { child.kill(); if (--live === 0) resolve(); return; }
          const [b, g] = k.split(':');
          child.send({ key: k, file: path.join(TOP, b, g + '.replay.gz') });
        };
        child.on('message', m => {
          if (m.error) { errors.push(m.key + ' ' + m.error); console.error('error', m.key, m.error); }
          else { results.set(m.key, m.out); if (cfd !== null) fs.writeSync(cfd, JSON.stringify({ key: m.key, out: m.out }) + '\n'); }
          if (++done % 50 === 0) console.log(`  ${done}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
          next();
        });
        child.on('error', reject);
        next();
      }
    });
    if (cfd !== null) fs.closeSync(cfd);
  }
  // checks
  const checks = { featureMismatch: 0, updates: 0, deaths: 0, splits: 0, drops: 0, eatTile: 0, units: 0, gamesWithIssues: [] };
  for (const [k, g] of results) {
    const bad = compareFeatures(g, feats.get(k));
    checks.featureMismatch += bad;
    for (const c of ['updates', 'deaths', 'splits', 'drops', 'eatTile', 'units']) checks[c] += g.chk[c];
    if (bad || Object.values(g.chk).some(v => v)) checks.gamesWithIssues.push(k);
  }
  const usedKeys = keys.filter(k => results.has(k));
  const out = aggregate(usedKeys, feats, results, checks);
  out.meta.keysFile = path.relative(ROOT, keysFile);
  out.meta.errors = errors;
  fs.writeFileSync(outFile, JSON.stringify(out, null, 1) + '\n');
  if (!quiet) printReport(out);
  console.log(`\nchecks ${JSON.stringify({ ...checks, gamesWithIssues: checks.gamesWithIssues.length })}`);
  console.log(`wrote ${path.relative(ROOT, outFile)} (${results.size} games parsed, errors ${errors.length}) in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  if (errors.length) process.exitCode = 1;
}

module.exports = { study, splitCat, cause, dropCat };
if (!process.argv.includes('--child') && require.main === module) main().catch(err => { console.error(err); process.exit(1); });
