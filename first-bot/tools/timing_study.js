#!/usr/bin/env node
// Timing study of top-team games (data/top): when teams do what, and when games are decided. Reads replays only.
// usage: node tools/timing_study.js [--keys data/top/snapshot-20260929a.keys] [--jobs K] [--cache FILE] [--out FILE]
//   --keys   game keys `battleId:gameId`, one per line (default: the frozen snapshot data/top/snapshot-20260929a.keys).
//            Metadata comes from data/top/features.jsonl (rows filtered to these keys; later rows are ignored).
//   --jobs   worker processes for replay parsing, 1..4 (default 4; capped at 4 because other analyses share the CPU).
//   --cache  optional JSONL of per-game extractions. Read if it exists and covers every key, else written after
//            parsing. Only for speed while iterating; without it every replay is parsed (1-4 min with 4 jobs,
//            depending on machine load).
//   --out    result JSON (default data/top/timing_study.json).
// Reproduce the report: node tools/timing_study.js   (no network; reads data/top only)
// Output: one JSON object with `data`, `validation`, `q1_curves`, `q2_decided`, `q3_eliminations`, `q4_phases`,
// `q4_endgame`, `q5_triggers`, `q6_gates`, `sss`. A readable summary of the key numbers goes to stdout.
// Report: research/observations/top-timing.md.
//
// Per-game extraction (worker processes): the body reconstruction of tools/top_features.js (moves, sprints, portals,
// splits, deaths, pearls) re-run with per-round bookkeeping. `validation` compares it with data/top/features.jsonl
// (timeline every 10 rounds, splits, deaths by cause, eaten / sprints / sonar per 50-round window) and checks pearl
// balances and the length identity of the endgame accounting; every count except `games` is expected to be 0.
// Definitions used throughout:
//   - Main sample = snapshot games without team SSS (it looks broken in most of its games; reported under `sss`).
//   - State at round r = living dragons, total length, longest length just before round r starts; index `rounds` is
//     the final state. A game is "running" at r when r < rounds; round-limit games also use the final state at 500.
//     A game "ends in round rounds-1" (the last round played).
//   - Death categories: suicide (no MOVE/SPLIT, engine default), badSplit (illegal split), badSprint (unpayable
//     sprint), noAction (tle / none / other), kelp (W), selfBody (S), ownBody (O into own team), ownHead (H with own
//     team, both parties), enemyBody (O into enemy), enemyHead (H with enemy, both parties; `ram` = the mover,
//     `rammed` = the other). The first eight are self-inflicted (selfKill); enemyBody/enemyHead are enemy contact.
//     `free` = free neighbour tiles of the head at the start of the dragon's own turn (not kelp, not any body incl.
//     its own tail). volSelf = self-inflicted death of the mover with free > 0 (a safe step existed); forcedSelf =
//     free == 0 (cornered).
//   - Pearl origin: natural (spawned or on the map at start) or dropped by a death; seen from the eater a drop is
//     ownSelf (own team's self-kill), ownContact (own team's enemy-contact death), enemySelf, enemyContact.
//   - King = the team's longest dragon (ties -> lowest id): kingEat counts pearls eaten by the dragon that was the
//     longest at that moment; gatherDist/enemyDist use the longest at round start. Distances are torus Manhattan
//     distances between heads, ignoring kelp and portals (a rough proxy).
//   - Endgame lineage: a split may leave most of the body in the child, so the final longest dragon is followed back
//     through its parents. For a round t, L_t is the length of the ancestor alive at round start t, and
//     final = L_t + eaten - sprint cost - lengths split off the line (checked for every game).
//   - Triggers (q5): per team (>= 20 games in the main sample) and activity, per-round counts over its games are
//     divided by dragon-turns; a step is a round r* where the rates in [r*-10, r*) and [r*, r*+10) differ at least
//     2x with Poisson log-likelihood ratio >= 15 (r* in 20..490, local maxima). Per game, the best single change
//     point within [r*-50, r*+50) (Poisson, same direction, >= 5 events, LLR >= 3) is compared with r*: a fixed
//     clock puts most games at r* exactly. One-round bursts are tested separately (binomial, see q5 note).
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');

const ROOT = path.resolve(__dirname, '..'), TOP = path.join(ROOT, 'data', 'top');
const NR = 500, TEAMS = ['A', 'B'];
const DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 }, DIRS = ['N', 'E', 'S', 'W'];
const CAT = ['suicide', 'badSplit', 'badSprint', 'noAction', 'kelp', 'selfBody', 'ownBody', 'ownHead', 'enemyBody', 'enemyHead'];
const NSELF = 8; // CAT[0..7] are self-inflicted
const ORIG = ['natural', 'ownSelf', 'ownContact', 'enemySelf', 'enemyContact'];
const CHECK = [300, 340, 350, 400, 430, 450, 470, 480, 490, 495];
// death record fields (arrays keep the cache small)
const D = { r: 0, team: 1, cat: 2, mover: 3, len: 4, free: 5, born: 6, id: 7, kingDist: 8, wasLongest: 9, drops: 10, eatOwn: 11, eatOwnKing: 12, eatEnemy: 13, ownDelaySum: 14, units: 15 };
// endgame lineage record fields, per checkpoint round
const K = { Lt: 0, eat: 1 /* 1..5 by ORIG */, cost: 6, lossOff: 7, lossPath: 8, transfers: 9, longestAtT: 10, identityOK: 11 };
const replayFile = (b, g) => path.join(TOP, String(b), g + '.replay.gz');
const other = s => s === 'A' ? 'B' : 'A';

// ---------------------------------------------------------------------------------------------------------------
// Per-game extraction: one parsed replay -> per-round series per team.
function perGame(R) {
  const M = R.match.map, W = M.width, H = M.height;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const key = (x, y) => y * W + x;
  const tdist = (a, b) => { const dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
  // map geometry, as in tools/top_features.js
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

  const drag = new Map(), all = new Map(), occ = new Map();
  const setOcc = d => { for (const s of d.body) occ.set(key(s.x, s.y), d.id); };
  const clrOcc = d => { for (const s of d.body) if (occ.get(key(s.x, s.y)) === d.id) occ.delete(key(s.x, s.y)); };
  const pearls = new Map(); // tile -> origin: -1 natural, else index into deaths
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearls.set(i, -1);
  let seq = 0; // event index; orders births, eats, costs and splits within a round
  const newDragon = (id, team, body, born, parent) => {
    const o = { id, team, body: body.map(s => ({ x: s.x, y: s.y })), born, parent, bornSeq: seq, fate: null, expect: [], act: null, tle: false, free: -1, eats: [], costs: [], splitsOut: [], lenAt: {} };
    drag.set(id, o); all.set(id, o); setOcc(o); return o;
  };
  for (const d0 of M.initialDragons) newDragon(d0.id, d0.team, d0.body, 0, -1);

  const I16 = () => new Int16Array(NR + 1), F32 = () => new Float32Array(NR).fill(NaN);
  const T = {};
  for (const tm of TEAMS) T[tm] = {
    units: I16(), total: I16(), longest: I16(), splits: I16(), splitChild: I16(), sprints: I16(), sprintCost: I16(),
    sonar: new Int32Array(NR + 1), turns: I16(), eat: ORIG.map(I16), kingEat: ORIG.map(I16),
    gatherDist: F32(), enemyDist: F32(), headDist: F32(),
  };
  const G = { pearlsNat: I16(), pearlsDrop: I16(), spawns: I16() };
  const seqAt = {};
  const deaths = [];
  let round = -1, cur = -1, drop = null;
  const better = (a, b) => !b || a.body.length > b.body.length || (a.body.length === b.body.length && a.id < b.id);
  const ownUnits = tm => { let n = 0; for (const d of drag.values()) if (d.team === tm) n++; return n; };
  const longestOther = (tm, ex) => { let b = null; for (const d of drag.values()) if (d.team === tm && d !== ex && better(d, b)) b = d; return b; };
  const isLongestNow = d => { for (const o of drag.values()) if (o.team === d.team && o !== d && better(o, d)) return false; return true; };

  const stateAt = r => {
    for (const tm of TEAMS) {
      const t = T[tm];
      let units = 0, total = 0, king = null;
      for (const d of drag.values()) if (d.team === tm) { units++; total += d.body.length; if (better(d, king)) king = d; }
      t.units[r] = units; t.total[r] = total; t.longest[r] = king ? king.body.length : 0;
      if (r >= NR || !king) continue;
      let gs = 0, gn = 0, ed = Infinity, hd = Infinity;
      for (const d of drag.values()) {
        if (d.team === tm) { if (d !== king) { gs += tdist(d.body[0], king.body[0]); gn++; } }
        else {
          const x = tdist(d.body[0], king.body[0]); if (x < ed) ed = x;
          for (const o of drag.values()) if (o.team === tm) { const y = tdist(o.body[0], d.body[0]); if (y < hd) hd = y; }
        }
      }
      if (gn) t.gatherDist[r] = gs / gn;
      if (ed < Infinity) { t.enemyDist[r] = ed; t.headDist[r] = hd; }
    }
    let n = 0, dr = 0; for (const o of pearls.values()) { if (o < 0) n++; else dr++; }
    G.pearlsNat[r] = n; G.pearlsDrop[r] = dr;
    if (CHECK.includes(r)) { seqAt[r] = seq; for (const d of drag.values()) d.lenAt[r] = d.body.length; }
  };
  const freeAround = d => {
    let n = 0; const h = d.body[0];
    for (const st of DIRS) { const nx = across(h.x, h.y, st); if (nx && !occ.has(key(nx.x, nx.y))) n++; }
    return n;
  };
  const eatAt = (d, k) => {
    const o = pearls.get(k); pearls.delete(k);
    const tm = d.team, t = T[tm], isKing = isLongestNow(d);
    let oi = 0;
    if (o >= 0) {
      const x = deaths[o], ownTeam = x[D.team] === (tm === 'A' ? 0 : 1), self = x[D.cat] < NSELF;
      oi = ownTeam ? (self ? 1 : 2) : (self ? 3 : 4);
      if (ownTeam) { x[D.eatOwn]++; if (isKing) x[D.eatOwnKing]++; x[D.ownDelaySum] += round - x[D.r]; } else x[D.eatEnemy]++;
    }
    t.eat[oi][round]++; if (isKing) t.kingEat[oi][round]++;
    d.eats.push(seq, oi);
  };

  for (const e of R.events) {
    seq++;
    if (drop && !(e.type === 'tileChange' && e.hasPearl)) drop = null;
    switch (e.type) {
      case 'roundStart':
        round = e.round;
        if (round <= NR) stateAt(round);
        break;
      case 'turnStart': {
        cur = e.id;
        const d = drag.get(cur);
        if (d) { T[d.team].turns[round]++; d.fate = null; d.expect = []; d.act = null; d.tle = false; d.free = freeAround(d); }
        break;
      }
      case 'tileChange': {
        const k = key(e.tile.x, e.tile.y);
        if (e.hasPearl) {
          if (drop) { pearls.set(k, drop.idx); drop.got++; }
          else { pearls.set(k, -1); if (round >= 0) G.spawns[round]++; }
        } else if (pearls.has(k)) { const d = drag.get(cur); if (d) eatAt(d, k); else pearls.delete(k); }
        break;
      }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action;
        d.act = a ? a.kind : null; d.tle = !!e.tle;
        if (!a || a.kind !== 'move') break;
        const t = T[d.team];
        if (a.steps.length >= 2) t.sprints[round]++;
        clrOcc(d);
        const body = d.body.slice();
        let fate = null, paid = 0;
        for (let i = 0; i < a.steps.length; i++) {
          const st = a.steps[i];
          if (i > 0 && body.length <= 2) { fate = { reason: 'A', step: i, why: 'sprint' }; break; }
          const h = body[0], nx = across(h.x, h.y, st);
          if (!nx) { fate = { reason: 'W', step: i }; break; }
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
        if (paid) { t.sprintCost[round] += paid; d.costs.push(seq, paid); }
        d.fate = fate;
        d.body = body; // steps already taken stand, also when a later step is fatal
        setOcc(d);
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id);
        if (!d || round < 0) break;
        const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        if (x.h.x !== e.head.x || x.h.y !== e.head.y || x.t.x !== e.tail.x || x.t.y !== e.tail.y) {
          // resync like the viewer (new head, drop segments up to the reported tail); counted in validation
          mismatch++;
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
        const t = T[p.team];
        t.splits[round]++; t.splitChild[round] += e.childBody.length;
        p.splitsOut.push(seq, e.childBody.length, e.childId, e.parentBody.length);
        clrOcc(p);
        p.body = e.parentBody.map(s => ({ x: s.x, y: s.y }));
        setOcc(p);
        newDragon(e.childId, e.team, e.childBody, round, p.id);
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        const mover = cur === d.id, tm = d.team;
        let cat;
        if (e.reason === 'A') {
          const f = d.fate, why = d.tle ? 'tle' : f ? f.why : d.act === 'split' ? 'split' : d.act === 'suicide' ? 'suicide' : d.act === null ? 'none' : 'other';
          cat = why === 'suicide' ? 0 : why === 'split' ? 1 : why === 'sprint' ? 2 : 3;
        } else if (e.reason === 'W') cat = 4;
        else if (e.reason === 'S') cat = 5;
        else {
          let ot;
          if (mover) ot = d.fate ? d.fate.hitTeam : undefined;
          else { const m = drag.get(cur); ot = m ? m.team : undefined; }
          cat = e.reason === 'O' ? (ot === tm ? 6 : 8) : (ot === tm ? 7 : 9);
        }
        const lo = longestOther(tm, d);
        const rec = [round, tm === 'A' ? 0 : 1, cat, mover ? 1 : 0, d.body.length, mover ? d.free : -1, d.born, d.id,
          lo ? tdist(d.body[0], lo.body[0]) : -1, !lo || d.body.length >= lo.body.length ? 1 : 0, Math.ceil(d.body.length / 2), 0, 0, 0, 0, ownUnits(tm)];
        deaths.push(rec);
        clrOcc(d); drag.delete(e.id);
        drop = { idx: deaths.length - 1, got: 0 };
        break;
      }
      case 'sonarPing': {
        const s = drag.get(e.senderId);
        if (s) T[s.team].sonar[round]++;
        break;
      }
    }
  }
  const rounds = round + 1;
  stateAt(rounds); // final state at index `rounds`
  for (const tm of TEAMS) { const t = T[tm]; for (let r = rounds + 1; r <= NR; r++) { t.units[r] = t.units[rounds]; t.total[r] = t.total[rounds]; t.longest[r] = t.longest[rounds]; } }

  // Final longest dragon of each team, followed back through its parents (see header).
  const kings = {};
  for (const tm of TEAMS) {
    const k = longestOther(tm, null);
    if (!k) { kings[tm] = null; continue; }
    const line = []; for (let x = k; x; x = x.parent >= 0 ? all.get(x.parent) : null) line.push(x);
    line.reverse();
    const byT = {};
    for (const t of CHECK) {
      if (!(t < rounds) || seqAt[t] === undefined) continue;
      let j = -1; for (let i = 0; i < line.length; i++) if (line[i].parent < 0 || line[i].bornSeq < seqAt[t]) j = i;
      const a = line[j], Lt = a.lenAt[t];
      const rec = new Array(12).fill(0);
      rec[K.Lt] = Lt; rec[K.longestAtT] = Lt === T[tm].longest[t] ? 1 : 0; rec[K.transfers] = line.length - 1 - j;
      for (let i = j; i < line.length; i++) {
        const x = line[i], from = i === j ? seqAt[t] : x.bornSeq, to = i + 1 < line.length ? line[i + 1].bornSeq : Infinity;
        for (let q = 0; q < x.eats.length; q += 2) if (x.eats[q] > from && x.eats[q] < to) rec[K.eat + x.eats[q + 1]]++;
        for (let q = 0; q < x.costs.length; q += 2) if (x.costs[q] > from && x.costs[q] < to) rec[K.cost] += x.costs[q + 1];
        for (let q = 0; q < x.splitsOut.length; q += 4) {
          if (!(x.splitsOut[q] > from && x.splitsOut[q] <= to)) continue;
          if (i + 1 < line.length && x.splitsOut[q + 2] === line[i + 1].id) rec[K.lossPath] += x.splitsOut[q + 3];
          else rec[K.lossOff] += x.splitsOut[q + 1];
        }
      }
      let eaten = 0; for (let o = 0; o < ORIG.length; o++) eaten += rec[K.eat + o];
      rec[K.identityOK] = Lt + eaten - rec[K.cost] - rec[K.lossOff] - rec[K.lossPath] === k.body.length ? 1 : 0;
      byT[t] = rec;
    }
    kings[tm] = { id: k.id, len: k.body.length, born: k.born, generations: line.length - 1, byT };
  }
  const res = R.result;
  const out = { rounds, endReason: res.endReason, winner: res.winner, width: W, height: H, G: {}, T: {}, deaths, kings, mismatch };
  for (const [k, v] of Object.entries(G)) out.G[k] = Array.from(v);
  for (const tm of TEAMS) {
    const t = T[tm], o = {};
    for (const [k, v] of Object.entries(t)) o[k] = Array.isArray(v) ? v.map(a => Array.from(a)) : Array.from(v, x => (Number.isNaN(x) ? null : x));
    out.T[tm] = o;
  }
  return out;
}
let mismatch = 0; // per process; reset by the worker before each game

// ---------------------------------------------------------------------------------------------------------------
// Worker (child process, so that requiring tools/top_features.js does not start its own worker-thread handler):
// parse and extract one game per message.
function workerMain() {
  const { makeLoader, viewerSource } = require('./top_features.js');
  const load = makeLoader(viewerSource());
  process.on('message', task => {
    try { mismatch = 0; process.send({ key: task.key, g: perGame(load(task.file)) }); }
    catch (err) { process.send({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 3).join(' | ') }); }
  });
}

// ---------------------------------------------------------------------------------------------------------------
// Main: extraction (workers or cache), validation against features.jsonl, analyses, output.
function readFeatures(keys) {
  const rows = new Map();
  for (const l of fs.readFileSync(path.join(TOP, 'features.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue;
    const m = /^\{"meta":\{"battleId":(\d+),"gameId":(\d+)[,}]/.exec(l);
    if (m && !keys.has(m[1] + ':' + m[2])) continue;
    let f; try { f = JSON.parse(l); } catch { continue; }
    const k = f.meta.battleId + ':' + f.meta.gameId;
    if (keys.has(k)) rows.set(k, f);
  }
  return rows;
}

async function extractAll(todo, jobs) {
  const queue = todo.slice(), out = new Map(), errors = [];
  const t0 = Date.now();
  await new Promise((resolve, reject) => {
    let live = Math.min(jobs, queue.length);
    if (!live) return resolve();
    for (let i = 0, n = live; i < n; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced' });
      let finished = false;
      const next = () => {
        const t = queue.shift();
        if (!t) { finished = true; w.kill(); if (--live === 0) resolve(); return; }
        w.send(t);
      };
      w.on('message', m => {
        if (m.error) errors.push(m.key + ' ' + m.error); else out.set(m.key, m.g);
        if ((out.size + errors.length) % 50 === 0) console.error(`  parsed ${out.size + errors.length}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
        next();
      });
      w.on('error', reject);
      w.on('exit', code => { if (!finished) reject(Error('worker exited unexpectedly with code ' + code)); });
      next();
    }
  });
  if (errors.length) throw Error('replay errors:\n' + errors.join('\n'));
  return out;
}

// Compare the per-round extraction with tools/top_features.js output for the same game (all expected 0).
function validate(games, feats) {
  const v = { games: 0, timeline: 0, splits: 0, deathsByCause: 0, eaten: 0, sprints: 0, sonar: 0, rounds: 0, endReason: 0, winner: 0, mismatch: 0, naturalPearlBalance: 0, dropPearlBalance: 0, dropOverEaten: 0, lineageIdentity: 0 };
  const featCat = (d, tm) => {
    if (d.reason === 'A') return d.why === 'suicide' ? 0 : d.why === 'split' ? 1 : d.why === 'sprint' ? 2 : 3;
    if (d.reason === 'W') return 4; if (d.reason === 'S') return 5;
    const ot = d.mover ? d.hitTeam : d.byTeam;
    return d.reason === 'O' ? (ot === tm ? 6 : 8) : (ot === tm ? 7 : 9);
  };
  for (const [k, g] of games) {
    const f = feats.get(k); if (!f) continue;
    v.games++; v.mismatch += g.mismatch;
    if (f.meta.rounds !== g.rounds) v.rounds++;
    if (f.meta.endReason !== g.endReason) v.endReason++;
    if (f.meta.winner !== g.winner) v.winner++;
    // pearl balance: start + spawned - eaten = on board at the end (natural); dropped - eaten = on board (drops)
    let nat = g.G.pearlsNat[0], drp = 0;
    for (let r = 0; r < g.rounds; r++) { nat += g.G.spawns[r]; for (const tm of TEAMS) { nat -= g.T[tm].eat[0][r]; for (let o = 1; o < ORIG.length; o++) drp -= g.T[tm].eat[o][r]; } }
    for (const d of g.deaths) { drp += d[D.drops]; if (d[D.eatOwn] + d[D.eatEnemy] > d[D.drops]) v.dropOverEaten++; }
    if (nat !== g.G.pearlsNat[g.rounds]) v.naturalPearlBalance++;
    if (drp !== g.G.pearlsDrop[g.rounds]) v.dropPearlBalance++;
    TEAMS.forEach((tm, ti) => {
      const t = g.T[tm], F = f[tm];
      for (const p of F.timeline) { const r = Math.min(p.r, g.rounds); if (t.units[r] !== p.units || t.total[r] !== p.total || t.longest[r] !== p.longest) v.timeline++; }
      if (t.splits.reduce((a, b) => a + b, 0) !== F.splits.length) v.splits++;
      const c1 = new Array(CAT.length).fill(0), c2 = new Array(CAT.length).fill(0);
      for (const d of F.deaths) c1[featCat(d, tm)]++;
      for (const d of g.deaths) if (d[D.team] === ti) c2[d[D.cat]]++;
      if (c1.some((x, i) => x !== c2[i])) v.deathsByCause++;
      for (let w = 0; w < 10; w++) {
        let e = 0, s = 0, so = 0;
        for (let r = w * 50; r < w * 50 + 50; r++) { for (let o = 0; o < ORIG.length; o++) e += t.eat[o][r]; s += t.sprints[r]; so += t.sonar[r]; }
        if (e !== F.eaten[w]) v.eaten++;
        if (s !== F.sprints[w]) v.sprints++;
        if (so !== F.sonar.sent[w]) v.sonar++;
      }
      const kg = g.kings[tm];
      if (kg) for (const rec of Object.values(kg.byT)) if (!rec[K.identityOK]) v.lineageIdentity++;
    });
  }
  return v;
}

// ---------------------------------------------------------------------------------------------------------------
// Statistics helpers
const quant = (a, p) => {
  if (!a.length) return null;
  const s = Float64Array.from(a).sort(), i = (s.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i);
  return s[lo] + (s[hi] - s[lo]) * (i - lo);
};
const rd = (x, k = 3) => x === null || x === undefined || Number.isNaN(x) || !Number.isFinite(x) ? null : Math.round(x * 10 ** k) / 10 ** k;
const qs = a => [quant(a, 0.25), quant(a, 0.5), quant(a, 0.75)].map(x => rd(x, 2));
const sum = a => { let s = 0; for (const x of a) s += x; return s; };
const ranks = a => {
  const idx = a.map((v, i) => [v, i]).sort((x, y) => x[0] - y[0]), r = new Array(a.length);
  for (let i = 0; i < idx.length;) { let j = i; while (j + 1 < idx.length && idx[j + 1][0] === idx[i][0]) j++; for (let k = i; k <= j; k++) r[idx[k][1]] = (i + j) / 2; i = j + 1; }
  return r;
};
function spearman(x, y) {
  const ok = x.map((v, i) => v !== null && y[i] !== null && Number.isFinite(v) && Number.isFinite(y[i]));
  const xs = x.filter((_, i) => ok[i]), ys = y.filter((_, i) => ok[i]), n = xs.length;
  if (n < 8) return null;
  const rx = ranks(xs), ry = ranks(ys), mx = sum(rx) / n, my = sum(ry) / n;
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) { sxy += (rx[i] - mx) * (ry[i] - my); sxx += (rx[i] - mx) ** 2; syy += (ry[i] - my) ** 2; }
  return sxx && syy ? rd(sxy / Math.sqrt(sxx * syy), 2) : null;
}
const LLt = (c, e) => c > 0 ? c * Math.log(c / e) : 0;
const lgam = (() => { const t = [0]; for (let i = 1; i <= 1000; i++) t[i] = t[i - 1] + Math.log(i); return n => t[n]; })(); // log n!
const binomTail = (k, n, p) => { let s = 0; for (let i = k; i <= n; i++) s += Math.exp(lgam(n) - lgam(i) - lgam(n - i) + i * Math.log(p) + (n - i) * Math.log(1 - p)); return s; };
const running = (g, r) => r < g.rounds || (r === NR && g.rounds === NR);
const tname = (g, s) => g.meta.teams[s].name;

// ---------------------------------------------------------------------------------------------------------------
// Q1: winners vs losers by round, per end type
function q1Curves(main) {
  const out = {};
  for (const et of ['teamEliminated', 'roundLimit']) {
    out[et] = {};
    for (const m of ['units', 'total', 'longest']) {
      const rows = [];
      for (let r = 0; r <= NR; r += 10) {
        const w = [], l = [];
        for (const g of main) { if (g.endReason !== et || !running(g, r)) continue; w.push(g.T[g.winner][m][r]); l.push(g.T[other(g.winner)][m][r]); }
        if (w.length) rows.push({ r, n: w.length, W: qs(w), L: qs(l) });
      }
      out[et][m] = rows;
    }
  }
  return out;
}

// Q2: when is a game decided
function q2Decided(main) {
  const measures = ['units', 'total', 'longest', 'lexi'];
  const cmp = (g, m, r) => { // +1 winner ahead, -1 loser ahead, 0 tie
    const w = g.T[g.winner], l = g.T[other(g.winner)];
    if (m === 'lexi') { const d = w.longest[r] - l.longest[r]; return d ? Math.sign(d) : Math.sign(w.total[r] - l.total[r]); }
    return Math.sign(w[m][r] - l[m][r]);
  };
  const sets = { all: main, teamEliminated: main.filter(g => g.endReason === 'teamEliminated'), roundLimit: main.filter(g => g.endReason === 'roundLimit') };
  const T_REPORT = [50, 100, 150, 200, 250, 300, 350, 400, 450, 480, 490];
  const out = { measures, note: 'lexi = longest, then total (the round-500 rule)', lastLead: {}, condWin: {}, curve: {}, earliest: {} };
  for (const [name, gs] of Object.entries(sets)) {
    out.lastLead[name] = {}; out.condWin[name] = {}; out.curve[name] = {}; out.earliest[name] = {};
    for (const m of measures) {
      const ll = [], frac = [], lnb = []; let never = 0;
      for (const g of gs) {
        let a = -1, b = -1;
        for (let r = 0; r <= g.rounds; r++) { const c = cmp(g, m, r); if (c < 0) a = r; if (c <= 0) b = r; }
        if (a < 0) never++; else { ll.push(a); frac.push(a / g.rounds); }
        lnb.push(b);
      }
      out.lastLead[name][m] = { n: gs.length, loserNeverLed: never, lastLead: qs(ll), lastLeadFracOfGame: qs(frac), lastNotBehind: qs(lnb) };
      const curve = [];
      for (let t = 0; t < NR; t += 10) {
        let n = 0, lead = 0, win = 0;
        for (const g of gs) { if (!(t < g.rounds)) continue; n++; const c = cmp(g, m, t); if (c) { lead++; if (c > 0) win++; } }
        curve.push({ t, n, leaders: lead, leaderWins: win, P: lead ? rd(win / lead) : null });
      }
      out.curve[name][m] = curve;
      out.condWin[name][m] = T_REPORT.map(t => {
        let n = 0, lead = 0, win = 0;
        for (const g of gs) { if (!(t < g.rounds)) continue; n++; const c = cmp(g, m, t); if (c) { lead++; if (c > 0) win++; } }
        return { t, n, leaders: lead, leaderWins: win, P: lead ? rd(win / lead) : null };
      });
      const first = th => { const x = curve.find(c => c.leaders >= 30 && c.P !== null && c.P >= th); return x ? x.t : null; };
      out.earliest[name][m] = { P080: first(0.8), P090: first(0.9), P095: first(0.95), minLeaders: 30 };
    }
  }
  // late flips (round-limit games): the eventual loser led by the round-500 rule (lexi) at t; how was it overtaken?
  out.lateFlips = {};
  for (const t of [400, 450, 480, 490]) {
    const rows = sets.roundLimit.filter(g => cmp(g, 'lexi', t) < 0).map(g => {
      const w = g.T[g.winner], l = g.T[other(g.winner)];
      return { loserLongestFell: l.longest[NR] < l.longest[t], wGain: w.longest[NR] - w.longest[t], lGain: l.longest[NR] - l.longest[t] };
    });
    out.lateFlips[t] = { games: rows.length, of: sets.roundLimit.length, loserLongestFell: rows.filter(x => x.loserLongestFell).length, winnerLongestGain: qs(rows.map(x => x.wGain)), loserLongestGain: qs(rows.map(x => x.lGain)) };
  }
  return out;
}

// Q3: eliminations
function q3Eliminations(main) {
  const el = main.filter(g => g.endReason === 'teamEliminated');
  const endR = el.map(g => g.rounds - 1);
  const hist = new Array(10).fill(0); for (const r of endR) hist[Math.min(9, Math.floor(r / 50))]++;
  const out = {
    n: el.length, endRound: { q10: rd(quant(endR, 0.1), 1), q25: rd(quant(endR, 0.25), 1), q50: rd(quant(endR, 0.5), 1), q75: rd(quant(endR, 0.75), 1), q90: rd(quant(endR, 0.9), 1), min: Math.min(...endR), max: Math.max(...endR) },
    endRoundBy50: hist, byMap: {}, byTeam: {}, before: {}, lastDeath: {}, deathsLast20: {}, early: {},
  };
  // by map (all main games)
  for (const g of main) {
    const k = g.meta.map, x = out.byMap[k] || (out.byMap[k] = { size: g.width + 'x' + g.height, startUnits: g.T.A.units[0], startLongest: g.T.A.longest[0], games: 0, eliminated: 0, endBefore100: 0, elimRounds: [] });
    x.games++;
    if (g.endReason === 'teamEliminated') { x.eliminated++; x.elimRounds.push(g.rounds - 1); if (g.rounds - 1 < 100) x.endBefore100++; }
  }
  for (const x of Object.values(out.byMap)) { x.medianElimRound = rd(quant(x.elimRounds, 0.5), 1); delete x.elimRounds; }
  // by team
  for (const g of main) for (const s of TEAMS) {
    const nm = tname(g, s), x = out.byTeam[nm] || (out.byTeam[nm] = { rank: g.meta.teams[s].rank, games: 0, wins: 0, eliminated: 0, wasEliminated: 0, earlyWins: 0, earlyLosses: 0 });
    x.games++; const won = g.winner === s; if (won) x.wins++;
    if (g.endReason === 'teamEliminated') { if (won) x.eliminated++; else x.wasEliminated++; if (g.rounds - 1 < 100) { if (won) x.earlyWins++; else x.earlyLosses++; } }
  }
  // the same per team, only on maps where at least half of the main-sample games end by elimination
  out.elimMaps = Object.entries(out.byMap).filter(([, x]) => x.eliminated >= x.games / 2).map(([k]) => k);
  const em = new Set(out.elimMaps);
  for (const g of main) for (const s of TEAMS) {
    if (!em.has(g.meta.map)) continue;
    const x = out.byTeam[tname(g, s)], won = g.winner === s;
    x.gamesOnElimMaps = (x.gamesOnElimMaps || 0) + 1;
    x.eliminatedOnElimMaps = (x.eliminatedOnElimMaps || 0) + (g.endReason === 'teamEliminated' && won ? 1 : 0);
    x.wasEliminatedOnElimMaps = (x.wasEliminatedOnElimMaps || 0) + (g.endReason === 'teamEliminated' && !won ? 1 : 0);
  }
  // state shortly before the end
  for (const k of [50, 20, 10, 5, 1]) {
    const L = { units: [], total: [], longest: [] }, Wn = { units: [], total: [], longest: [] };
    for (const g of el) { const r = g.rounds - k; if (r < 0) continue; for (const m of Object.keys(L)) { L[m].push(g.T[other(g.winner)][m][r]); Wn[m].push(g.T[g.winner][m][r]); } }
    out.before[k] = { n: L.units.length, eliminated: Object.fromEntries(Object.entries(L).map(([m, a]) => [m, qs(a)])), eliminator: Object.fromEntries(Object.entries(Wn).map(([m, a]) => [m, qs(a)])) };
  }
  const label = d => d[D.cat] === 9 ? (d[D.mover] ? 'enemyHead-ram' : 'enemyHead-rammed') : CAT[d[D.cat]];
  for (const g of el) {
    const li = g.winner === 'A' ? 1 : 0, ds = g.deaths.filter(d => d[D.team] === li);
    const last = ds[ds.length - 1]; out.lastDeath[label(last)] = (out.lastDeath[label(last)] || 0) + 1;
    for (const d of ds) if (d[D.r] >= g.rounds - 20) out.deathsLast20[label(d)] = (out.deathsLast20[label(d)] || 0) + 1;
  }
  // early ends (last round < 100)
  const early = el.filter(g => g.rounds - 1 < 100), E = out.early;
  E.n = early.length; E.maps = {}; E.winners = {}; E.losers = {};
  for (const g of early) {
    E.maps[g.meta.map] = (E.maps[g.meta.map] || 0) + 1;
    E.winners[tname(g, g.winner)] = (E.winners[tname(g, g.winner)] || 0) + 1;
    E.losers[tname(g, other(g.winner))] = (E.losers[tname(g, other(g.winner))] || 0) + 1;
  }
  const rk = early.filter(g => g.meta.teams.A.rank && g.meta.teams.B.rank);
  E.winnerBetterRank = rk.filter(g => g.meta.teams[g.winner].rank < g.meta.teams[other(g.winner)].rank).length; E.withRanks = rk.length;
  E.trajectory = [0, 5, 10, 15, 20, 30, 40, 50].map(r => {
    const x = { r, n: 0, W: { units: [], total: [], longest: [] }, L: { units: [], total: [], longest: [] } };
    for (const g of early) { if (!(r < g.rounds)) continue; x.n++; for (const m of ['units', 'total', 'longest']) { x.W[m].push(g.T[g.winner][m][r]); x.L[m].push(g.T[other(g.winner)][m][r]); } }
    for (const s of ['W', 'L']) for (const m of ['units', 'total', 'longest']) x[s][m] = rd(quant(x[s][m], 0.5), 1);
    return x;
  });
  const per = { W: {}, L: {} };
  const add = (s, k, v) => (per[s][k] = per[s][k] || []).push(v);
  for (const g of early) for (const s of ['W', 'L']) {
    const tm = s === 'W' ? g.winner : other(g.winner), ti = tm === 'A' ? 0 : 1, t = g.T[tm], R = g.rounds;
    add(s, 'splitsR0to9', sum(t.splits.slice(0, 10))); add(s, 'splits', sum(t.splits.slice(0, R))); add(s, 'sprints', sum(t.sprints.slice(0, R)));
    let eat = 0; for (let o = 0; o < ORIG.length; o++) eat += sum(t.eat[o].slice(0, R)); add(s, 'eaten', eat);
    const ds = g.deaths.filter(d => d[D.team] === ti);
    add(s, 'ram', ds.filter(d => d[D.cat] === 9 && d[D.mover]).length); add(s, 'rammed', ds.filter(d => d[D.cat] === 9 && !d[D.mover]).length);
    add(s, 'selfKill', ds.filter(d => d[D.cat] < NSELF).length);
  }
  E.perGameMedian = { W: {}, L: {} }; E.perGameSum = { W: {}, L: {} };
  for (const s of ['W', 'L']) for (const [k, a] of Object.entries(per[s])) { E.perGameMedian[s][k] = rd(quant(a, 0.5), 1); E.perGameSum[s][k] = sum(a); }
  E.winnerMoreUnits = {};
  for (const r of [5, 10, 20]) { const gs = early.filter(g => r < g.rounds); E.winnerMoreUnits[r] = { n: gs.length, more: gs.filter(g => g.T[g.winner].units[r] > g.T[other(g.winner)].units[r]).length, fewer: gs.filter(g => g.T[g.winner].units[r] < g.T[other(g.winner)].units[r]).length }; }
  // the same maps, games that did not end before round 100: units at rounds 10 and 20
  const emaps = new Set(early.map(g => g.meta.map)), rest = main.filter(g => emaps.has(g.meta.map) && !(g.endReason === 'teamEliminated' && g.rounds - 1 < 100));
  E.sameMapsOtherGames = { n: rest.length };
  for (const r of [10, 20]) {
    E.sameMapsOtherGames['unitsR' + r] = { W: rd(quant(rest.map(g => g.T[g.winner].units[r]), 0.5), 1), L: rd(quant(rest.map(g => g.T[other(g.winner)].units[r]), 0.5), 1) };
    E['unitsR' + r] = { W: rd(quant(early.filter(g => r < g.rounds).map(g => g.T[g.winner].units[r]), 0.5), 1), L: rd(quant(early.filter(g => r < g.rounds).map(g => g.T[other(g.winner)].units[r]), 0.5), 1) };
  }
  return out;
}

// Q4: activity per 50-round window, winners vs losers
function q4Phases(main) {
  const sets = { all: main, roundLimit: main.filter(g => g.endReason === 'roundLimit'), teamEliminated: main.filter(g => g.endReason === 'teamEliminated') };
  const items = ['splits', 'sprints', 'sonar', 'turns', ...ORIG.map(o => 'eat_' + o), ...ORIG.map(o => 'kingEat_' + o),
    ...CAT.filter(c => c !== 'enemyHead').map(c => 'death_' + c), 'death_ram', 'death_rammed', 'selfKill', 'volSelf', 'forcedSelf', 'contact'];
  const out = { note: 'rates per team-game per 50 rounds of play (count * 50 / rounds played in the window); exposure = team-games * 50 rounds; perTurn = count / dragon-turns', windows: {}, dropFate: {} };
  for (const [name, gs] of Object.entries(sets)) {
    out.windows[name] = {};
    for (const side of ['W', 'L']) {
      const acc = { exposure: new Array(10).fill(0) }; for (const it of items) acc[it] = new Array(10).fill(0);
      for (const g of gs) {
        const tm = side === 'W' ? g.winner : other(g.winner), ti = tm === 'A' ? 0 : 1, t = g.T[tm];
        for (let r = 0; r < g.rounds; r++) {
          const w = Math.floor(r / 50);
          acc.exposure[w]++; acc.splits[w] += t.splits[r]; acc.sprints[w] += t.sprints[r]; acc.sonar[w] += t.sonar[r]; acc.turns[w] += t.turns[r];
          for (let o = 0; o < ORIG.length; o++) { acc['eat_' + ORIG[o]][w] += t.eat[o][r]; acc['kingEat_' + ORIG[o]][w] += t.kingEat[o][r]; }
        }
        for (const d of g.deaths) {
          if (d[D.team] !== ti) continue;
          const w = Math.min(9, Math.floor(d[D.r] / 50)), c = d[D.cat];
          if (c === 9) acc[d[D.mover] ? 'death_ram' : 'death_rammed'][w]++; else acc['death_' + CAT[c]][w]++;
          if (c < NSELF) { acc.selfKill[w]++; if (d[D.mover] && d[D.free] > 0) acc.volSelf[w]++; else if (d[D.mover]) acc.forcedSelf[w]++; }
          else acc.contact[w]++;
        }
      }
      const o = { teamGamesRunning: acc.exposure.map(x => rd(x / 50, 2)) };
      for (const it of items) o[it] = acc[it].map((c, w) => acc.exposure[w] ? rd(50 * c / acc.exposure[w], 2) : null);
      o.perTurn = {};
      for (const it of ['splits', 'sprints', 'sonar', 'volSelf', 'selfKill', 'eat_natural', 'eat_ownSelf']) o.perTurn[it] = acc[it].map((c, w) => acc.turns[w] ? rd(c / acc.turns[w], 4) : null);
      out.windows[name][side] = o;
    }
  }
  // what happens to pearls dropped by self-kills, by window of the death (main sample, both sides)
  for (const side of ['W', 'L', 'all']) {
    const a = { deaths: new Array(10).fill(0), drops: new Array(10).fill(0), own: new Array(10).fill(0), ownKing: new Array(10).fill(0), enemy: new Array(10).fill(0), delay: new Array(10).fill(0) };
    for (const g of main) for (const d of g.deaths) {
      if (d[D.cat] >= NSELF) continue;
      const tm = d[D.team] ? 'B' : 'A'; if (side !== 'all' && (side === 'W') !== (tm === g.winner)) continue;
      const w = Math.min(9, Math.floor(d[D.r] / 50));
      a.deaths[w]++; a.drops[w] += d[D.drops]; a.own[w] += d[D.eatOwn]; a.ownKing[w] += d[D.eatOwnKing]; a.enemy[w] += d[D.eatEnemy]; a.delay[w] += d[D.ownDelaySum];
    }
    out.dropFate[side] = { selfKills: a.deaths, drops: a.drops, ownShare: a.own.map((x, w) => a.drops[w] ? rd(x / a.drops[w]) : null), kingShare: a.ownKing.map((x, w) => a.drops[w] ? rd(x / a.drops[w]) : null), enemyShare: a.enemy.map((x, w) => a.drops[w] ? rd(x / a.drops[w]) : null), meanRoundsToOwnEat: a.delay.map((x, w) => a.own[w] ? rd(x / a.own[w], 1) : null) };
  }
  return out;
}

// Q4 endgame: where the final longest dragon's length came from (round-limit games)
function q4Endgame(main) {
  const rl = main.filter(g => g.endReason === 'roundLimit'), out = { n: rl.length, note: 'L_t = length at round start t of the ancestor (through splits) of the final longest dragon; gain = final - L_t = eaten - sprint cost - split-off lengths', bySide: {} };
  for (const side of ['W', 'L']) {
    out.bySide[side] = {};
    for (const t of [300, 400, 430, 450, 480, 490]) {
      const fin = [], Lt = [], gain = [], share = [], transfers = [], teamLongest = [], per = ORIG.map(() => []);
      let pooledEat = ORIG.map(() => 0), cost = 0, lossOff = 0, lossPath = 0, longestAtT = 0, n = 0, bad = 0, gainSum = 0;
      for (const g of rl) {
        const tm = side === 'W' ? g.winner : other(g.winner), k = g.kings[tm];
        if (!k || !k.byT[t]) continue;
        const x = k.byT[t]; n++;
        if (!x[K.identityOK]) bad++;
        fin.push(k.len); Lt.push(x[K.Lt]); gain.push(k.len - x[K.Lt]); gainSum += k.len - x[K.Lt]; share.push(k.len ? (k.len - x[K.Lt]) / k.len : 0);
        transfers.push(x[K.transfers]); teamLongest.push(g.T[tm].longest[t]); longestAtT += x[K.longestAtT];
        for (let o = 0; o < ORIG.length; o++) { pooledEat[o] += x[K.eat + o]; per[o].push(x[K.eat + o]); }
        cost += x[K.cost]; lossOff += x[K.lossOff]; lossPath += x[K.lossPath];
      }
      const eaten = sum(pooledEat);
      out.bySide[side][t] = {
        n, identityViolations: bad, finalLen: qs(fin), Lt: qs(Lt), teamLongestAtT: qs(teamLongest), gain: qs(gain), gainShareOfFinal: qs(share),
        ancestorWasLongestAtT: longestAtT, transfersAfterT: qs(transfers), gamesWithTransfer: transfers.filter(v => v > 0).length,
        pooled: { gain: gainSum, eaten, byOrigin: Object.fromEntries(ORIG.map((o, i) => [o, pooledEat[i]])), shareOfEaten: Object.fromEntries(ORIG.map((o, i) => [o, eaten ? rd(pooledEat[i] / eaten) : null])), sprintCost: cost, splitOffLine: lossOff, parentRemainderAtTransfers: lossPath },
        perGameMedianEaten: Object.fromEntries(ORIG.map((o, i) => [o, rd(quant(per[i], 0.5), 1)])),
      };
    }
  }
  return out;
}

// Q5: per-team steps in per-round activity, and whether each game switches at the same round
const ACTS = ['split', 'selfKill', 'volSelf', 'suicide', 'eat', 'ownDropEat', 'kingFeed', 'sprint', 'sonar', 'ram'];
function teamSeries(g, s) {
  const t = g.T[s], ti = s === 'A' ? 0 : 1, R = g.rounds, z = () => new Float64Array(NR);
  const o = { turns: z(), run: z() }; for (const a of ACTS) o[a] = z();
  for (let r = 0; r < R; r++) {
    o.turns[r] = t.turns[r]; o.run[r] = 1; o.split[r] = t.splits[r]; o.sprint[r] = t.sprints[r]; o.sonar[r] = t.sonar[r];
    let e = 0; for (let k = 0; k < ORIG.length; k++) e += t.eat[k][r];
    o.eat[r] = e; o.ownDropEat[r] = t.eat[1][r]; o.kingFeed[r] = t.kingEat[1][r];
  }
  for (const d of g.deaths) {
    if (d[D.team] !== ti) continue;
    const r = d[D.r];
    if (d[D.cat] < NSELF) { o.selfKill[r]++; if (d[D.mover] && d[D.free] > 0) o.volSelf[r]++; }
    if (d[D.cat] === 0) o.suicide[r]++;
    if (d[D.cat] === 9 && d[D.mover]) o.ram[r]++;
  }
  return o;
}
const exposureOf = a => a === 'kingFeed' ? 'run' : 'turns';
function detectSteps(C, E, W = 10, thr = 15, lo = 20, hi = 490) {
  const pc = new Float64Array(NR + 1), pe = new Float64Array(NR + 1);
  for (let i = 0; i < NR; i++) { pc[i + 1] = pc[i] + C[i]; pe[i + 1] = pe[i] + E[i]; }
  const cand = [];
  for (let r = lo; r <= hi; r++) {
    const a0 = Math.max(0, r - W), b1 = Math.min(NR, r + W);
    const cB = pc[r] - pc[a0], eB = pe[r] - pe[a0], cA = pc[b1] - pc[r], eA = pe[b1] - pe[r];
    if (eB <= 0 || eA <= 0) continue;
    const llr = LLt(cB, eB) + LLt(cA, eA) - LLt(cB + cA, eB + eA), lb = cB / eB, la = cA / eA;
    if (llr >= thr && (la >= 2 * lb || lb >= 2 * la)) cand.push({ r, llr, lb, la });
  }
  cand.sort((a, b) => b.llr - a.llr);
  const out = [];
  for (const c of cand) if (!out.some(o => Math.abs(o.r - c.r) < W)) out.push(c);
  return out.sort((a, b) => a.r - b.r);
}
function gameChangePoint(C, E, lo, hi, dir) {
  let cT = 0, eT = 0; for (let r = lo; r < hi; r++) { cT += C[r]; eT += E[r]; }
  if (eT <= 0) return { c: null, events: cT };
  let best = null, cB = 0, eB = 0;
  for (let c = lo + 1; c < hi; c++) {
    cB += C[c - 1]; eB += E[c - 1];
    const cA = cT - cB, eA = eT - eB; if (eB <= 0 || eA <= 0) continue;
    const lb = cB / eB, la = cA / eA; if (dir > 0 ? la <= lb : la >= lb) continue;
    const llr = LLt(cB, eB) + LLt(cA, eA) - LLt(cT, eT);
    if (!best || llr > best.llr) best = { c, llr };
  }
  return best ? { c: best.c, llr: best.llr, events: cT } : { c: null, events: cT };
}
function q5Triggers(main) {
  const t0 = Math.min(...main.map(g => Date.parse(g.meta.at)));
  const byTeam = {};
  for (const g of main) for (const s of TEAMS) (byTeam[tname(g, s)] = byTeam[tname(g, s)] || []).push({ g, s });
  const out = {
    note: 'steps: rate per dragon-turn (kingFeed: per team-round) in [r*-10,r*) vs [r*,r*+10), >=2x and Poisson LLR >= 15, r* in 20..490. Per game: best change point in [r*-50,r*+50) with >= 5 events and LLR >= 3; offsets are cp - r*. perMap = [change points, median offset, min offset, max offset]. label: clock = >=60% of change points within +-1 of r*; clockPlusLate = 30-60% within +-1 and <15% earlier than r*-2; mapDependent = <30% within +-1 and map eta^2 >= 0.6; spread = otherwise; few = < 5 change points. corr: Spearman of the change point with the state at r*-60 (map size W+H and battle time meta.at are per game). bursts: rounds where the number of running games with >= 1 event at exactly that round is improbable (binomial tail p < 1e-6, >= 5 games) given the higher of the mean shares of the 10 rounds before and the 10 rounds after (baseline at least 0.02). stateAtChange: quartiles and relative IQR of a state variable at the change point of each game vs at r* (a trigger on that state would make it more constant at the change point).',
    minGames: 20, teams: {}, opening: {},
  };
  for (const [nm, list] of Object.entries(byTeam).sort((a, b) => b[1].length - a[1].length)) {
    if (list.length < 20) continue;
    const S = list.map(x => ({ ...x, o: teamSeries(x.g, x.s) }));
    const agg = {}; for (const a of [...ACTS, 'turns', 'run']) { agg[a] = new Float64Array(NR); for (const x of S) for (let r = 0; r < NR; r++) agg[a][r] += x.o[a][r]; }
    // opening split burst: splits per team-game in rounds 0-9 vs per 10 rounds in 10-49
    out.opening[nm] = { splitsR0to9: rd(sum(agg.split.slice(0, 10)) / list.length, 2), splitsPer10R10to49: rd(sum(agg.split.slice(10, 50)) / sum(agg.run.slice(10, 50)) * 10, 2) };
    const steps = [];
    for (const a of ACTS) {
      const E = agg[exposureOf(a)];
      for (const st of detectSteps(agg[a], E)) {
        const dir = st.la > st.lb ? 1 : -1, offs = [], rows = [];
        let eligible = 0;
        for (const x of S) {
          const g = x.g; if (g.rounds < st.r + 20) continue;
          eligible++;
          const lo = Math.max(0, st.r - 50), hi = Math.min(g.rounds, st.r + 50);
          const c = gameChangePoint(x.o[a], x.o[exposureOf(a)], lo, hi, dir);
          if (c.c === null || c.events < 5 || c.llr < 3) continue;
          offs.push(c.c - st.r); rows.push({ x, c: c.c });
        }
        const n = offs.length, w1 = offs.filter(v => Math.abs(v) <= 1).length, early = offs.filter(v => v < -2).length, late = offs.filter(v => v > 2).length;
        // map dependence: share of change-point variance between maps (maps with >= 2 change points)
        const bym = {}; for (const { x, c } of rows) (bym[x.g.meta.map] = bym[x.g.meta.map] || []).push(c);
        const used = Object.values(bym).filter(v => v.length >= 2), allc = [].concat(...used);
        let eta2 = null;
        if (used.length >= 2) {
          const m = sum(allc) / allc.length, sst = sum(allc.map(v => (v - m) ** 2));
          const ssw = sum(used.map(v => { const mm = sum(v) / v.length; return sum(v.map(y => (y - mm) ** 2)); }));
          eta2 = sst > 0 ? rd(1 - ssw / sst, 2) : null;
        }
        const perMap = Object.fromEntries(Object.entries(bym).map(([k, v]) => [k, [v.length, rd(quant(v.map(c => c - st.r), 0.5), 1), Math.min(...v) - st.r, Math.max(...v) - st.r]]));
        // does the change point track the state before the step?
        const rr = Math.max(0, st.r - 60), cps = rows.map(y => y.c);
        const st0 = (f) => rows.map(({ x }) => f(x.g, x.s, rr));
        const corr = n >= 8 ? {
          units: spearman(cps, st0((g, s, r) => g.T[s].units[r])), total: spearman(cps, st0((g, s, r) => g.T[s].total[r])),
          longest: spearman(cps, st0((g, s, r) => g.T[s].longest[r])), longestLead: spearman(cps, st0((g, s, r) => g.T[s].longest[r] - g.T[other(s)].longest[r])),
          totalLead: spearman(cps, st0((g, s, r) => g.T[s].total[r] - g.T[other(s)].total[r])), pearlsOnBoard: spearman(cps, st0((g, s, r) => g.G.pearlsNat[r] + g.G.pearlsDrop[r])),
          enemyDist: spearman(cps, st0((g, s, r) => g.T[s].enemyDist[r])), mapSize: spearman(cps, st0(g => g.width + g.height)),
          time: spearman(cps, st0(g => (Date.parse(g.meta.at) - t0) / 60000)),
        } : null;
        // is some state more constant at the per-game change point than at the fixed round r*? (relative IQR = IQR / |median|)
        const relIQR = a => { const m = quant(a, 0.5); return m ? rd((quant(a, 0.75) - quant(a, 0.25)) / Math.abs(m), 2) : null; };
        const disp = fn => { const atC = rows.map(({ x, c: cc }) => fn(x.g, x.s, cc)), atR = rows.map(({ x }) => fn(x.g, x.s, st.r)); return { atChange: qs(atC), atStep: qs(atR), relIQRatChange: relIQR(atC), relIQRatStep: relIQR(atR) }; };
        const stateAtChange = n >= 8 ? {
          units: disp((g, s, r) => g.T[s].units[r]), total: disp((g, s, r) => g.T[s].total[r]), longest: disp((g, s, r) => g.T[s].longest[r]),
          pearlsOnBoard: disp((g, s, r) => g.G.pearlsNat[r] + g.G.pearlsDrop[r]), remainingPerLongest: disp((g, s, r) => (NR - r) / Math.max(1, g.T[s].longest[r])),
        } : null;
        const ex = n ? w1 / n : 0;
        const label = n < 5 ? 'few' : ex >= 0.6 ? 'clock' : ex >= 0.3 && early / n < 0.15 ? 'clockPlusLate' : eta2 !== null && eta2 >= 0.6 ? 'mapDependent' : 'spread';
        steps.push({
          activity: a, r: st.r, dir: dir > 0 ? 'up' : 'down', rateBefore: rd(st.lb, 4), rateAfter: rd(st.la, 4), ratio: st.lb > 0 ? rd(st.la / st.lb, 2) : null, llr: rd(st.llr, 1),
          games: { eligible, withChange: n, within1: w1, within2: offs.filter(v => Math.abs(v) <= 2).length, within10: offs.filter(v => Math.abs(v) <= 10).length, earlier: early, later: late, offsetQ: qs(offs) },
          mapEta2: eta2, perMap, corr, stateAtChange, label,
        });
      }
    }
    // one-round bursts: games with >= 1 event at exactly round r, tested against the higher of the mean shares over the
    // 10 rounds before and the 10 rounds after (binomial tail p < 1e-6, at least 2% baseline, >= 5 games)
    const bursts = [];
    for (const a of ACTS) {
      const share = new Float64Array(NR), runN = new Float64Array(NR), hit = new Float64Array(NR);
      for (const x of S) for (let r = 0; r < x.g.rounds; r++) { runN[r]++; if (x.o[a][r] > 0) hit[r]++; }
      for (let r = 0; r < NR; r++) share[r] = runN[r] ? hit[r] / runN[r] : 0;
      const side = (a0, b0) => { let t = 0, n = 0; for (let r = Math.max(0, a0); r < Math.min(NR, b0); r++) if (runN[r]) { t += share[r]; n++; } return n ? t / n : 0; };
      for (let r = 1; r < NR; r++) {
        const bef = side(r - 10, r), aft = side(r + 1, r + 11);
        if (hit[r] < 5) continue;
        const pv = binomTail(hit[r], runN[r], Math.max(0.02, bef, aft));
        if (pv < 1e-6) bursts.push({ activity: a, r, gamesWithEvent: hit[r], running: runN[r], share: rd(share[r], 2), shareBefore: rd(bef, 2), shareAfter: rd(aft, 2), p: Number(pv.toExponential(1)) });
      }
    }
    out.teams[nm] = { games: list.length, rank: list[0].g.meta.teams[list[0].s].rank, steps, bursts };
  }
  return out;
}

// Q6: our fixed gates vs what top teams do around them
function q6Gates(main) {
  const byTeam = {};
  for (const g of main) for (const s of TEAMS) (byTeam[tname(g, s)] = byTeam[tname(g, s)] || []).push({ g, s });
  const out = { note: 'our gates: 300 sonar sharing, 340 gather toward the longest ally, 430 fragments feed the king, 450 no more splits, 495 aggressive trades, last 30 rounds extra threat weight', teams: {}, pooled: null };
  const measure = list => {
    const rl = list.filter(x => x.g.rounds === NR);
    const m = { games: list.length, roundLimitGames: rl.length };
    // sonar per dragon-turn by 100 rounds
    const son = new Array(5).fill(0), tur = new Array(5).fill(0);
    for (const { g, s } of list) for (let r = 0; r < g.rounds; r++) { const w = Math.floor(r / 100); son[w] += g.T[s].sonar[r]; tur[w] += g.T[s].turns[r]; }
    m.sonarPerTurnBy100 = son.map((x, i) => tur[i] ? rd(x / tur[i], 3) : null);
    // gather distance (round-limit games): per game mean over the window, then median over games
    m.gatherDistBy50 = [];
    for (let w = 0; w < 10; w++) { const v = []; for (const { g, s } of rl) { let a = 0, n = 0; for (let r = w * 50; r < w * 50 + 50; r++) { const x = g.T[s].gatherDist[r]; if (x !== null && Number.isFinite(x)) { a += x; n++; } } if (n) v.push(a / n); } m.gatherDistBy50.push(rd(quant(v, 0.5), 1)); }
    // splits per dragon-turn 400-449 vs 450-499, last split round (round-limit games)
    const rate = (key, a, b, perDeath) => { let c = 0, t = 0; for (const { g, s } of list) { const ti = s === 'A' ? 0 : 1; for (let r = a; r < Math.min(b, g.rounds); r++) t += g.T[s].turns[r]; if (perDeath) { for (const d of g.deaths) if (d[D.team] === ti && d[D.r] >= a && d[D.r] < b && perDeath(d)) c++; } else for (let r = a; r < Math.min(b, g.rounds); r++) c += g.T[s][key][r]; } return t ? rd(c / t, 4) : null; };
    m.splitPerTurn = { r400to449: rate('splits', 400, 450), r450to499: rate('splits', 450, 500), r490to499: rate('splits', 490, 500) };
    const last = rl.map(({ g, s }) => { let l = -1; for (let r = 0; r < NR; r++) if (g.T[s].splits[r] > 0) l = r; return l; });
    m.lastSplitRound = { q10: rd(quant(last, 0.1), 1), q50: rd(quant(last, 0.5), 1), q90: rd(quant(last, 0.9), 1) };
    m.gamesSplittingAfter450 = rl.filter(({ g, s }) => sum(g.T[s].splits.slice(450, 500)) > 0).length;
    m.gamesSplittingAfter490 = rl.filter(({ g, s }) => sum(g.T[s].splits.slice(490, 500)) > 0).length;
    // head-on trades started by this team (ram) per dragon-turn
    const ram = d => d[D.cat] === 9 && d[D.mover];
    m.ramPerTurn = { r400to469: rate(null, 400, 470, ram), r470to499: rate(null, 470, 500, ram), r400to489: rate(null, 400, 490, ram), r490to499: rate(null, 490, 500, ram) };
    const cnt = (a, b) => { let c = 0; for (const { g, s } of list) { const ti = s === 'A' ? 0 : 1; for (const d of g.deaths) if (d[D.team] === ti && d[D.r] >= a && d[D.r] < b && ram(d)) c++; } return c; };
    m.ramCount = { r400to469: cnt(400, 470), r470to499: cnt(470, 500), r490to499: cnt(490, 500) };
    // voluntary self-kills per dragon-turn by 50 rounds
    m.volSelfPerTurnBy50 = []; for (let w = 0; w < 10; w++) m.volSelfPerTurnBy50.push(rate(null, w * 50, w * 50 + 50, d => d[D.cat] < NSELF && d[D.mover] && d[D.free] > 0));
    // how the team's dragons die (mean per game), and where voluntary self-kills happen relative to the longest other dragon
    m.deathsPerGame = {};
    for (let c = 0; c < CAT.length; c++) m.deathsPerGame[CAT[c]] = rd(sum(list.map(({ g, s }) => g.deaths.filter(d => d[D.team] === (s === 'A' ? 0 : 1) && d[D.cat] === c).length)) / list.length, 1);
    m.volSelfNearLongest = [[0, 250], [250, 350], [350, 450], [450, 500]].map(([a, b]) => {
      const kd = []; for (const { g, s } of list) { const ti = s === 'A' ? 0 : 1; for (const d of g.deaths) if (d[D.team] === ti && d[D.r] >= a && d[D.r] < b && d[D.cat] < NSELF && d[D.mover] && d[D.free] > 0 && d[D.kingDist] >= 0) kd.push(d[D.kingDist]); }
      return { rounds: `${a}-${b - 1}`, n: kd.length, medianDist: rd(quant(kd, 0.5), 1), within2: kd.length ? rd(kd.filter(x => x <= 2).length / kd.length, 2) : null };
    });
    // king build-up: first round the team's longest reaches 10 / 20 (round-limit games on maps whose dragons start at length <= 4)
    const small = rl.filter(({ g }) => g.T.A.longest[0] <= 4 && g.T.B.longest[0] <= 4);
    m.smallStartRoundLimitGames = small.length;
    for (const L of [10, 20]) { const v = []; let never = 0; for (const { g, s } of small) { let f = -1; for (let r = 0; r <= NR; r++) if (g.T[s].longest[r] >= L) { f = r; break; } if (f < 0) never++; else v.push(f); } m['firstLongest' + L] = { q25: rd(quant(v, 0.25), 1), q50: rd(quant(v, 0.5), 1), q75: rd(quant(v, 0.75), 1), never }; }
    return m;
  };
  for (const [nm, list] of Object.entries(byTeam).sort((a, b) => b[1].length - a[1].length)) if (list.length >= 20) out.teams[nm] = measure(list);
  out.pooled = measure([].concat(...Object.values(byTeam)));
  return out;
}

function sssReport(allGames) {
  const rows = [];
  for (const g of allGames) for (const s of TEAMS) {
    if (tname(g, s) !== 'SSS') continue;
    const t = g.T[s], ti = s === 'A' ? 0 : 1, R = g.rounds;
    let eat = 0; for (let o = 0; o < ORIG.length; o++) eat += sum(t.eat[o].slice(0, R));
    const turns = sum(t.turns.slice(0, R));
    rows.push({ key: g.key, battle: g.meta.battleId, map: g.meta.map, opponent: tname(g, other(s)), won: g.winner === s, endReason: g.endReason, rounds: R, splits: sum(t.splits.slice(0, R)), eaten: eat, sonarPerTurn: turns ? rd(sum(t.sonar.slice(0, R)) / turns, 2) : 0, deaths: g.deaths.filter(d => d[D.team] === ti).length, final: [t.units[R], t.longest[R], t.total[R]] });
  }
  const inactive = rows.filter(x => x.splits <= 3 && x.sonarPerTurn === 0);
  return { games: rows.length, wins: rows.filter(x => x.won).length, inactiveGames: inactive.length, inactiveDefinition: 'splits <= 3 and no sonar', inactiveBattles: [...new Set(inactive.map(x => x.battle))], rows };
}

function analyse(keyList, games, feats) {
  const all = keyList.map(k => { const g = games.get(k); g.key = k; g.meta = feats.get(k).meta; return g; });
  const isSSS = g => g.meta.teams.A.name === 'SSS' || g.meta.teams.B.name === 'SSS';
  const main = all.filter(g => !isSSS(g));
  const count = gs => ({ games: gs.length, teamEliminated: gs.filter(g => g.endReason === 'teamEliminated').length, roundLimit: gs.filter(g => g.endReason === 'roundLimit').length, endBefore100: gs.filter(g => g.rounds - 1 < 100).length, reach500: gs.filter(g => g.rounds === NR).length });
  return {
    data: { snapshot: keyList.length, all: count(all), main: count(main), excludedSSS: all.length - main.length, battles: new Set(all.map(g => g.meta.battleId)).size, battleTimes: [all.map(g => g.meta.at).sort()[0], all.map(g => g.meta.at).sort().slice(-1)[0]] },
    q1_curves: q1Curves(main), q2_decided: q2Decided(main), q3_eliminations: q3Eliminations(main), q4_phases: q4Phases(main), q4_endgame: q4Endgame(main),
    q5_triggers: q5Triggers(main), q6_gates: q6Gates(main), sss: sssReport(all),
  };
}

// ---------------------------------------------------------------------------------------------------------------
// Console summary (the same numbers as the JSON)
function summary(S) {
  const p = (...a) => console.log(...a), f = x => x === null || x === undefined ? '-' : String(x);
  p(`\n== data: ${JSON.stringify(S.data)}`);
  p('\n== Q1 medians (W / L), running games');
  for (const [et, ms] of Object.entries(S.q1_curves)) for (const [m, rows] of Object.entries(ms))
    p(`${et.padEnd(15)} ${m.padEnd(8)} ` + rows.filter(x => x.r % 50 === 0).map(x => `${x.r}:${f(x.W[1])}/${f(x.L[1])}(n${x.n})`).join(' '));
  p('\n== Q2 last round the loser led (q25/q50/q75; never = loser never led)');
  for (const [name, ms] of Object.entries(S.q2_decided.lastLead)) p(`${name.padEnd(15)} ` + Object.entries(ms).map(([m, x]) => `${m}: never ${x.loserNeverLed}/${x.n} lead ${x.lastLead.join('/')}`).join(' | '));
  p('P(win | leading at t) [n leaders]');
  for (const [name, ms] of Object.entries(S.q2_decided.condWin)) for (const [m, rows] of Object.entries(ms)) p(`${name.padEnd(15)} ${m.padEnd(8)} ` + rows.map(x => `${x.t}:${f(x.P)}[${x.leaders}]`).join(' '));
  p('earliest t with P >= 0.8 / 0.9 / 0.95 (>= 30 leaders): ' + JSON.stringify(S.q2_decided.earliest));
  p('late flips (round-limit, loser led by lexi at t): ' + JSON.stringify(S.q2_decided.lateFlips));
  const E = S.q3_eliminations;
  p(`\n== Q3 eliminations n=${E.n} end round ${JSON.stringify(E.endRound)} by50 ${E.endRoundBy50.join(' ')}`);
  for (const [k, x] of Object.entries(E.before)) p(`  ${k} rounds before end (n${x.n}): eliminated units/total/longest ${x.eliminated.units[1]}/${x.eliminated.total[1]}/${x.eliminated.longest[1]}  eliminator ${x.eliminator.units[1]}/${x.eliminator.total[1]}/${x.eliminator.longest[1]}`);
  p('  last death of eliminated team: ' + JSON.stringify(E.lastDeath));
  p('  by map: ' + Object.entries(E.byMap).map(([k, x]) => `${k} ${x.eliminated}/${x.games} early ${x.endBefore100} med ${x.medianElimRound}`).join(' | '));
  p(`  early (<100) n=${E.early.n} maps ${JSON.stringify(E.early.maps)}`);
  p('  early trajectory (median W/L units, total): ' + E.early.trajectory.map(x => `${x.r}:${x.W.units}/${x.L.units},${x.W.total}/${x.L.total}`).join(' '));
  p('  early per-game medians W ' + JSON.stringify(E.early.perGameMedian.W) + ' L ' + JSON.stringify(E.early.perGameMedian.L));
  p('\n== Q4 per 50 rounds (roundLimit games) W | L');
  const RL = S.q4_phases.windows.roundLimit;
  for (const it of ['splits', 'selfKill', 'volSelf', 'death_suicide', 'contact', 'death_ram', 'eat_natural', 'eat_ownSelf', 'kingEat_ownSelf', 'kingEat_natural', 'sprints', 'sonar'])
    p(`  ${it.padEnd(16)} ` + RL.W[it].map(f).join(' ') + '  |  ' + RL.L[it].map(f).join(' '));
  const EL = S.q4_phases.windows.teamEliminated;
  p('== Q4 per 50 rounds (elimination games) W | L');
  for (const it of ['splits', 'selfKill', 'contact', 'death_ram', 'death_rammed', 'eat_natural', 'eat_ownSelf', 'sonar'])
    p(`  ${it.padEnd(16)} ` + EL.W[it].map(f).join(' ') + '  |  ' + EL.L[it].map(f).join(' '));
  p('  self-kill drop fate (all): own ' + S.q4_phases.dropFate.all.ownShare.join(' ') + ' king ' + S.q4_phases.dropFate.all.kingShare.join(' '));
  p('\n== Q4 endgame (round-limit games)');
  for (const [side, byT] of Object.entries(S.q4_endgame.bySide)) for (const [t, x] of Object.entries(byT))
    p(`  ${side} t${t} n${x.n} final ${x.finalLen[1]} L_t ${x.Lt[1]} gain ${x.gain.join('/')} share ${x.gainShareOfFinal[1]} eaten ${x.pooled.eaten} ${JSON.stringify(x.pooled.shareOfEaten)} cost ${x.pooled.sprintCost} splitOff ${x.pooled.splitOffLine} remainder ${x.pooled.parentRemainderAtTransfers} ancestorLongest ${x.ancestorWasLongestAtT} transfers>0 ${x.gamesWithTransfer} idViol ${x.identityViolations}`);
  p('\n== Q5 steps (activity@r* ratio label [within1/withChange/eligible]) and bursts (activity@r games/running)');
  for (const [nm, x] of Object.entries(S.q5_triggers.teams)) p(`  ${nm} (${x.games}): ` + x.steps.map(s => `${s.activity}@${s.r} x${s.ratio === null ? 'inf' : s.ratio} ${s.label}[${s.games.within1}/${s.games.withChange}/${s.games.eligible}]`).join(', ') + (x.bursts.length ? ' | bursts ' + x.bursts.map(b => `${b.activity}@${b.r} ${b.gamesWithEvent}/${b.running}`).join(', ') : ''));
  p('\n== Q6 gates, pooled: ' + JSON.stringify(S.q6_gates.pooled));
  p(`\n== SSS: ${S.sss.games} games, ${S.sss.wins} wins, inactive ${S.sss.inactiveGames} (battles ${S.sss.inactiveBattles.join(', ')})`);
}

async function main() {
  const argv = process.argv.slice(2);
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const keysFile = path.resolve(ROOT, opt('keys', 'data/top/snapshot-20260929a.keys'));
  const jobs = Math.max(1, Math.min(4, +opt('jobs', 4) || 4));
  const cache = opt('cache', null), outFile = path.resolve(ROOT, opt('out', 'data/top/timing_study.json'));
  const keyList = fs.readFileSync(keysFile, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  const keys = new Set(keyList);
  const feats = readFeatures(keys);
  const missing = keyList.filter(k => !feats.has(k));
  if (missing.length) throw Error(`${missing.length} snapshot keys have no features.jsonl row (e.g. ${missing[0]})`);

  let games = new Map();
  if (cache && fs.existsSync(cache)) {
    for (const l of fs.readFileSync(cache, 'utf8').split('\n')) { if (!l.trim()) continue; const o = JSON.parse(l); if (keys.has(o.key)) games.set(o.key, o.g); }
    if (games.size !== keys.size) { console.error(`cache covers ${games.size}/${keys.size} keys; re-parsing`); games = new Map(); }
    else console.error(`loaded ${games.size} games from cache ${cache}`);
  }
  if (!games.size) {
    const todo = keyList.map(k => { const [b, g] = k.split(':'); return { key: k, file: replayFile(b, g) }; });
    games = await extractAll(todo, jobs);
    if (cache) fs.writeFileSync(cache, keyList.map(k => JSON.stringify({ key: k, g: games.get(k) })).join('\n') + '\n');
  }
  const validation = validate(games, feats);
  console.log('validation (every count except games should be 0): ' + JSON.stringify(validation));
  const study = { generated: new Date().toISOString(), keys: path.relative(ROOT, keysFile), validation, ...analyse(keyList, games, feats) };
  fs.writeFileSync(outFile, JSON.stringify(study, null, 1) + '\n');
  summary(study);
  console.log('\nwrote ' + path.relative(ROOT, outFile));
}

module.exports = { perGame, CAT, ORIG, D, K, NSELF };
if (require.main === module) {
  if (process.argv.includes('--worker')) workerMain();
  else main().catch(err => { console.error(err); process.exit(1); });
}
