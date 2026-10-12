#!/usr/bin/env node
'use strict';
// study.js — replay study of our online test sets against the baseline sets (2026-09-30 online analysis).
// Reads replays only: no network, no games.
// usage (repository root):
//   node exp/online-analysis/study.js [--sets baseline-r1,baseline-r1b,baseline-r1c,cand-avoid6-online,px-king-v2-online]
//                                     [--jobs 3] [--out .cache/online-analysis/study.jsonl] [--games id,id]
//   node exp/online-analysis/study.js --top Autarky,'Prisoners Dilemma' --out <file>   (top-team snapshot games; winner = side 0)
// Output: one JSON line per game (set, map, variant, result, tools/baseline_study.js analyse() summary, extra metrics).
// Per game it runs
//   1. analyse(R, g) from tools/baseline_study.js (validated body reconstruction: deaths with causes, splits, pearls by
//      origin, flow = units / total length / longest every round). Its internal checks must all be 0.
//   2. extra(R, g) below, a second step simulation (same rules as tools/top_features.js extract) that adds:
//      - our indicator counts: ' esc' (cand-avoid6 escape sprint), ' T' (escapes off by the trust switch), escape-split,
//        ' late'. Each escape sprint becomes a record: round, length, steps, nearest enemy head, whether it was the start
//        lineage, head offset from the start line before/after, and what happened next to the dragon it saved (the
//        escaping dragon, then the longer piece at each split): alive / length after 10, 20, 50 rounds, death round and
//        cause, and whether it is our longest dragon at the end.
//      - start lineage: our longest start dragon; at each split follow the longer piece (the child on a tie). Length at
//        check rounds, first round its head stands >= 2 tiles off the start line (corridor exit; only when the start body
//        is a straight line), death round and cause, escape splits and escape sprints of the lineage.
//      - corridor fountains (Autarky, Prisoners Dilemma): tiles with max spawn gap <= 5 within one tile of a team's
//        start line (maps/online-20260927/<map>.map, as exp/cand-escape1/fountain_online.js). Natural spawns there, natural
//        and corpse pearls eaten there by the owner and by the other team, natural pearls eaten elsewhere.
//      - death summaries by side, cause and length class, and by 50-round window.
//      A head/tail check against every dragonUpdate (sim mismatches, expected 0) and a death-cause check.
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const TF = require(path.join(ROOT, 'tools', 'top_features.js'));
const BS = require(path.join(ROOT, 'tools', 'baseline_study.js'));
const CHILD = process.argv.includes('--oa-child');   // not '--child': tools/baseline_study.js listens on that flag
const OWN_TEAM = 583;
const DEFAULT_SETS = ['baseline-r1', 'baseline-r1b', 'baseline-r1c', 'cand-avoid6-online', 'px-king-v2-online'];
const ELIM_MAPS = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default'];
const MAP_FILE = { Autarky: 'autarky.map', 'Prisoners Dilemma': 'prisoners_dilemma.map' };
const DIRS = 'NESW';
const CHECK_R = [0, 10, 25, 50, 100, 150, 200, 250, 300, 340, 350, 400, 430, 450, 480, 500];
const BIG = 6, WINLEN = 50, NWIN = 10;
const win = r => Math.max(0, Math.min(NWIN - 1, Math.floor(r / WINLEN)));

function fountainTiles(mapName, M) {
  const f = MAP_FILE[mapName]; if (!f) return null;
  const W = M.width;
  const gaps = fs.readFileSync(path.join(ROOT, 'maps/online-20260927', f), 'utf8').split('\n').filter(l => l.startsWith('TILE ')).map(l => l.trim().split(/\s+/).slice(1).map(Number));
  const out = {};
  for (const t of ['A', 'B']) {
    const d = M.initialDragons.filter(x => x.team === t).sort((a, b) => b.body.length - a.body.length || a.id - b.id)[0];
    out[t] = new Set();
    if (!d || !d.body.every(s => s.x === d.body[0].x)) continue;
    for (const [x, y, , mx] of gaps) if (mx >= 1 && mx <= 5 && Math.abs(x - d.body[0].x) <= 1) out[t].add(y * W + x);
  }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------
function extra(R, g) {
  const M = R.match.map, { W, H, N, nb } = BS.buildGeo(M);
  const US = String(g.ourSide).toUpperCase(), THEM = US === 'A' ? 'B' : 'A';
  const tileOf = s => s.y * W + s.x, xy = t => [t % W, (t / W) | 0];
  const cheb = (a, b) => { let dx = Math.abs(a % W - b % W), dy = Math.abs(((a / W) | 0) - ((b / W) | 0)); dx = Math.min(dx, W - dx); dy = Math.min(dy, H - dy); return Math.max(dx, dy); };
  const man = (a, b) => { let dx = Math.abs(a % W - b % W), dy = Math.abs(((a / W) | 0) - ((b / W) | 0)); dx = Math.min(dx, W - dx); dy = Math.min(dy, H - dy); return dx + dy; };
  const drag = new Map(), occ = new Int32Array(N).fill(-1);
  const pearl = new Int8Array(N);            // 0 none, 1 natural, 2 corpse
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearl[i] = 1;
  const setOcc = d => { for (const t of d.body) occ[t] = d.id; };
  const clrOcc = d => { for (const t of d.body) if (occ[t] === d.id) occ[t] = -1; };
  for (const d0 of M.initialDragons) { const d = { id: d0.id, team: d0.team, body: d0.body.map(tileOf), born: 0, expect: [], ind: null, fate: null, act: null, free: null }; drag.set(d.id, d); setOcc(d); }
  const initCount = { us: M.initialDragons.filter(d => d.team === US).length, them: M.initialDragons.filter(d => d.team === THEM).length };
  const unitsOf = team => { let n = 0; for (const o of drag.values()) if (o.team === team) n++; return n; };
  const longestOf = team => { let m = 0; for (const o of drag.values()) if (o.team === team && o.body.length > m) m = o.body.length; return m; };
  const freeCount = h => { let f = 0; for (let k = 0; k < 4; k++) { const u = nb[h * 4 + k]; if (u >= 0 && occ[u] === -1) f++; } return f; };

  // start lineage (our longest start dragon; lowest id on a tie) and its start line
  const ours0 = M.initialDragons.filter(d => d.team === US).sort((a, b) => b.body.length - a.body.length || a.id - b.id);
  const s0 = ours0[0];
  const vertical = s0.body.every(s => s.x === s0.body[0].x), horizontal = s0.body.every(s => s.y === s0.body[0].y);
  const lineOff = t => { const [x, y] = xy(t); if (vertical) { const d = Math.abs(x - s0.body[0].x); return Math.min(d, W - d); } if (horizontal) { const d = Math.abs(y - s0.body[0].y); return Math.min(d, H - d); } return null; };
  const LIN = { startId: s0.id, startLen: s0.body.length, straight: vertical || horizontal, cur: s0.id, lens: {}, exitRound: null, maxOff: 0, death: null, escSplits: 0, escSprints: 0, splits: 0, offAt: {} };

  // fountains
  const F = fountainTiles(g.mapName, M);
  const fnt = F ? { tiles: { us: F[US].size, them: F[THEM].size },
    us: { spawns: 0, natOwn: 0, corOwn: 0, natOther: 0, natElse: 0 }, them: { spawns: 0, natOwn: 0, corOwn: 0, natOther: 0, natElse: 0 } } : null;
  // natOwn: natural eaten on own fountains; corOwn: corpse eaten on own fountains; natOther: natural eaten on the OTHER team's fountains

  // indicator counts and escape records
  const ind = { turns: 0, esc: 0, T: 0, Tturns: 0, escSplit: 0, late: 0, escLate: 0, esc2: 0, esc3: 0, feed: 0, trade: 0 };
  const escs = [];          // escape sprint records
  const follows = [];       // open escape followers
  const chk = { updates: 0, deaths: 0 };
  const deathsSum = { us: {}, them: {} };          // cause -> {n, len, big, bigLen}
  const deathsWin = { us: {}, them: {} };          // cause -> [per window count]
  const bigDeaths = [];                             // our deaths of length >= BIG
  const lastDeaths = [];                            // our deaths (kept small: last 6)
  const kingDeaths = [];                            // our deaths while our longest (len >= 8)
  const addDeath = (side, cause, len, r) => {
    const S = deathsSum[side], Wn = deathsWin[side];
    if (!S[cause]) { S[cause] = { n: 0, len: 0, big: 0, bigLen: 0 }; Wn[cause] = new Array(NWIN).fill(0); }
    S[cause].n++; S[cause].len += len; if (len >= BIG) { S[cause].big++; S[cause].bigLen += len; }
    Wn[cause][win(r)]++;
  };
  let round = -1, cur = -1, dropFrom = null;

  const snapLineage = () => {
    const d = drag.get(LIN.cur);
    if (CHECK_R.includes(round)) LIN.lens[round] = d && !LIN.death ? d.body.length : 0;
    if (d && !LIN.death && LIN.straight) {
      const off = lineOff(d.body[0]);
      if (off > LIN.maxOff) LIN.maxOff = off;
      if (off >= 2 && LIN.exitRound === null) LIN.exitRound = round;
      if (CHECK_R.includes(round)) LIN.offAt[round] = off;
    }
    for (const f of follows) {
      if (f.done) continue;
      const age = round - f.rec.r;
      for (const a of [10, 20, 50]) if (age === a) { const x = drag.get(f.cur); f.rec['len' + a] = x ? x.body.length : 0; }
    }
  };

  for (const e of R.events) {
    if (dropFrom && !(e.type === 'tileChange' && e.hasPearl)) dropFrom = null;
    switch (e.type) {
      case 'roundStart': round = e.round; snapLineage(); break;
      case 'turnStart': { cur = e.id; const d = drag.get(cur); if (d) { d.expect = []; d.ind = null; d.fate = null; d.act = null; d.free = null; } break; }
      case 'dragonIndicator': { const d = drag.get(e.id); if (d) d.ind = e.text; break; }
      case 'tileChange': {
        const k = tileOf(e.tile);
        if (e.hasPearl) {
          pearl[k] = dropFrom ? 2 : 1;
          if (!dropFrom && round >= 0 && fnt) { if (F[US].has(k)) fnt.us.spawns++; if (F[THEM].has(k)) fnt.them.spawns++; }
        } else {
          const kind = pearl[k]; pearl[k] = 0;
          const d = drag.get(cur);
          if (d && round >= 0 && fnt) {
            const side = d.team === US ? 'us' : 'them', own = F[d.team], other = F[d.team === US ? THEM : US];
            if (own.has(k)) { if (kind === 2) fnt[side].corOwn++; else fnt[side].natOwn++; }
            else if (kind !== 2) { if (other.has(k)) fnt[side].natOther++; else fnt[side].natElse++; }
          }
        }
        break;
      }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action;
        d.act = a ? a.kind : null; d.free = freeCount(d.body[0]);
        const mine = d.team === US && round >= 0;
        if (mine) {
          ind.turns++;
          const s = d.ind || '';
          const isEsc = / esc(\s|$)/.test(s);
          if (/ T(\s|$)/.test(s)) { ind.T++; }
          if (s.startsWith('escape-split')) ind.escSplit++;
          if (/ late(\s|$)/.test(s)) ind.late++;
          if (s.startsWith('feed')) ind.feed++;
          if (/ TRADE/.test(s)) ind.trade++;
          if (isEsc && a && a.kind === 'move') {
            ind.esc++; if (/ late(\s|$)/.test(s)) ind.escLate++;
            if (a.steps.length === 2) ind.esc2++; else if (a.steps.length >= 3) ind.esc3++;
            // context at the decision
            let near = null;
            for (const o of drag.values()) {
              if (o.team === d.team) continue;
              const c = cheb(o.body[0], d.body[0]);
              if (!near || c < near.cheb || (c === near.cheb && o.body.length < near.len)) near = { cheb: c, man: man(o.body[0], d.body[0]), len: o.body.length };
            }
            let shortNear = 0; for (const o of drag.values()) if (o.team !== d.team && o.body.length < d.body.length && cheb(o.body[0], d.body[0]) <= 3) shortNear++;
            const rec = { r: round, id: d.id, L: d.body.length, steps: a.steps.length, late: / late(\s|$)/.test(s) ? 1 : 0, lineage: d.id === LIN.cur && !LIN.death ? 1 : 0,
              near, shortNear, offPre: LIN.straight ? lineOff(d.body[0]) : null, longestNow: d.body.length >= longestOf(d.team) ? 1 : 0, units: unitsOf(d.team) };
            escs.push(rec); follows.push({ rec, cur: d.id, done: false, pending: true });
            if (rec.lineage) LIN.escSprints++;
          }
        }
        if (!a || a.kind !== 'move') break;
        clrOcc(d);
        const body = d.body.slice();
        let fate = null;
        for (let i = 0; i < a.steps.length; i++) {
          if (i > 0 && body.length <= 2) { fate = { reason: 'A', step: i }; break; }
          const h = body[0], nx = nb[h * 4 + DIRS.indexOf(a.steps[i])];
          if (nx < 0) { fate = { reason: 'W', step: i }; break; }
          if (body.includes(nx)) { fate = { reason: 'S', step: i }; break; }
          const o = occ[nx];
          if (o !== -1) { const od = drag.get(o); fate = { reason: od.body[0] === nx ? 'H' : 'O', step: i, hit: o, hitTeam: od.team, hitLen: od.body.length }; break; }
          body.unshift(nx);
          if (pearl[nx] === 0) body.pop();
          if (i > 0) body.pop();
          d.expect.push({ h: body[0], t: body[body.length - 1] });
        }
        d.fate = fate; d.body = body; setOcc(d);
        if (mine) for (const f of follows) if (f.pending && f.cur === d.id && f.rec.r === round) { f.pending = false; f.rec.offPost = LIN.straight ? lineOff(d.body[0]) : null; f.rec.fatal = fate ? fate.reason : null; }
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id); if (!d || round < 0) break;
        const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        const eh = tileOf(e.head), et = tileOf(e.tail);
        if (x.h !== eh || x.t !== et) {
          chk.updates++;
          clrOcc(d); const b = d.body.slice(); if (b[0] !== eh) b.unshift(eh);
          while (b.length > 1 && b[b.length - 1] !== et) b.pop();
          d.body = b; d.expect = []; setOcc(d);
        }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        const cl = e.childBody.length, pl = e.parentBody.length;
        clrOcc(p); p.body = e.parentBody.map(tileOf); setOcc(p);
        const c = { id: e.childId, team: e.team, body: e.childBody.map(tileOf), born: round, expect: [], ind: null, fate: null, act: null, free: null };
        drag.set(c.id, c); setOcc(c);
        if (p.id === LIN.cur && !LIN.death) { LIN.splits++; if ((p.ind || '').startsWith('escape-split')) LIN.escSplits++; if (cl >= pl) LIN.cur = c.id; }
        for (const f of follows) if (!f.done && f.cur === p.id && cl >= pl) f.cur = c.id;
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        const mover = cur === d.id, side = d.team === US ? 'us' : 'them', len = d.body.length;
        let cause;
        if (mover) {
          const f = d.fate;
          if (e.reason === 'H') cause = f && f.hitTeam !== d.team ? 'ramEnemy' : 'ally';       // we moved into a head: both die
          else if (e.reason === 'O') cause = f && f.hitTeam !== d.team ? 'enemyBody' : 'ally';
          else { const fr = d.free === null ? freeCount(d.body[0]) : d.free; cause = fr === 0 ? 'trapped' : 'selfFree'; }   // W, S, A with or without a free neighbour
          if (e.reason !== 'A' && (!f || f.reason !== e.reason)) chk.deaths++;
        } else {
          const m = drag.get(cur);
          if (e.reason === 'H' && m && m.team !== d.team) cause = 'rammed';
          else if (e.reason === 'H' && m) cause = 'ally';
          else { cause = 'other'; chk.deaths++; }
        }
        addDeath(side, cause, len, round);
        const longestNow = len >= longestOf(d.team);
        if (side === 'us') {
          const m = mover ? null : drag.get(cur);
          const rec = { r: round, id: d.id, len, cause, reason: e.reason, ind: d.ind || null, longest: longestNow ? 1 : 0, units: unitsOf(d.team),
            by: m ? { len: m.body.length, born: m.born } : null, lineage: d.id === LIN.cur && !LIN.death ? 1 : 0 };
          if (len >= BIG) bigDeaths.push(rec);
          if (longestNow && len >= 8) kingDeaths.push(rec);
          lastDeaths.push(rec); if (lastDeaths.length > 6) lastDeaths.shift();
        }
        if (d.id === LIN.cur && !LIN.death) LIN.death = { r: round, cause, len, ind: d.ind || null };
        for (const f of follows) if (!f.done && f.cur === d.id) { f.done = true; f.rec.death = { r: round, cause, len, dr: round - f.rec.r }; }
        clrOcc(d); drag.delete(e.id);
        dropFrom = { id: d.id };
        break;
      }
      default: break;
    }
  }
  const rounds = round + 1;
  // final state of followers and lineage
  const usLongest = longestOf(US);
  for (const f of follows) {
    if (f.done) continue;
    const x = drag.get(f.cur);
    f.rec.final = x ? x.body.length : 0; f.rec.finalLongest = x && x.body.length === usLongest ? 1 : 0;
  }
  const L = drag.get(LIN.cur);
  LIN.final = L && !LIN.death ? L.body.length : 0; LIN.finalLongest = L && !LIN.death && L.body.length === usLongest ? 1 : 0;
  for (const r of CHECK_R) if (r >= rounds && LIN.lens[r] === undefined) LIN.lens[r] = LIN.final;
  delete LIN.cur;
  return { initCount, ind, escs, lineage: LIN, fountains: fnt, deathsSum, deathsWin, bigDeaths, kingDeaths, lastDeaths, chk, rounds };
}

// ---------------------------------------------------------------------------------------------------------------
function listGames(sets, only) {
  const tasks = [];
  for (const set of sets) {
    const dir = path.join(ROOT, 'data', 'online', set);
    const idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
    for (const g of idx.games || idx) {
      if (only && !only.has(g.gameId)) continue;
      if (g.ourWin === null || g.ourWin === undefined) continue;
      const meta = JSON.parse(fs.readFileSync(path.join(dir, `game-${g.gameId}.json`), 'utf8'));
      const us = String(g.ourSide).toUpperCase(), them = us === 'A' ? 'B' : 'A';
      if (meta['team' + us + 'Id'] !== OWN_TEAM) throw Error(`game ${g.gameId}: side ${us} is not team ${OWN_TEAM}`);
      const gg = { ...g, set, oppName: meta['team' + them + 'Name'], oppElo: meta['team' + them + 'Elo'], ourElo: meta['team' + us + 'Elo'] };
      tasks.push({ file: path.join(dir, `M${g.gameId}.replay`), g: gg });
    }
  }
  return tasks;
}

// --top <maps>: top-team games of the snapshot (data/top/snapshot-20260929a.keys, SSS excluded, as tools/baseline_study.js),
// with the winner as "us" (side 0) and the loser as "them". Used for the Autarky / Prisoners Dilemma comparison.
function listTop(maps) {
  const keys = new Set(fs.readFileSync(path.join(ROOT, 'data/top/snapshot-20260929a.keys'), 'utf8').trim().split('\n'));
  const tasks = [];
  for (const l of fs.readFileSync(path.join(ROOT, 'data/top/features.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue;
    const m = JSON.parse(l).meta;
    if (!keys.has(m.battleId + ':' + m.gameId) || !maps.includes(m.map)) continue;
    if (m.teams.A.name === 'SSS' || m.teams.B.name === 'SSS' || (m.winner !== 'A' && m.winner !== 'B')) continue;
    const us = m.winner, them = us === 'A' ? 'B' : 'A';
    tasks.push({ file: path.join(ROOT, 'data/top', String(m.battleId), m.gameId + '.replay.gz'),
      g: { gameId: m.gameId, set: 'top', mapName: m.map, ourSide: us, ourWin: true, opponentTeam: m.teams[them].name, oppName: m.teams[them].name,
        winnerName: m.teams[us].name, oppElo: m.teams[them].elo, ourElo: m.teams[us].elo, ranked: m.ranked, ourSubmission: null } });
  }
  return tasks;
}

// Trim analyse() output to what the reports use.
function trim(rec) {
  const us = rec.deaths.filter(d => d.side === 0);
  return {
    init: rec.init, endReason: rec.endReason, rounds: rec.rounds, final: rec.final, finalMatch: rec.finalMatch, checks: rec.checks,
    mass: rec.mass.map(m => ({ ...m })), flow: rec.flow, eat: rec.eat, kingEat: rec.kingEat, paid: rec.paid, sprints: rec.sprints, turns: rec.turns,
    ind: rec.ind, chains: rec.chains, portalSteps: rec.portalSteps, region: rec.region, peak: rec.peak,
    splitsN: rec.splits.map(s => s.length), splits2: rec.splits.map(s => s.filter(x => x[2] === 2).length),
    splitsKind: (() => { const o = {}; for (const s of rec.splits[0]) o[s[5] || 'none'] = (o[s[5] || 'none'] || 0) + 1; return o; })(),
    cls2: [0, 1].map(si => { const o = {}; for (const d of rec.deaths.filter(x => x.side === si)) { const c = d.cls2; if (!o[c]) o[c] = { n: 0, len: 0, big: 0, bigLen: 0 }; o[c].n++; o[c].len += d.len; if (d.len >= BIG) { o[c].big++; o[c].bigLen += d.len; } } return o; }),
    usBigDeaths: us.filter(d => d.len >= BIG).map(d => ({ r: d.r, len: d.len, cls2: d.cls2, by: d.by ? { len: d.by.len, steps: d.by.steps, bornLen: d.by.bornLen } : null, att: d.att || null, dec: d.dec || null, leader: d.leader })),
    usLast: us.slice(-5).map(d => ({ r: d.r, len: d.len, cls2: d.cls2, by: d.by ? { len: d.by.len, steps: d.by.steps } : null })),
  };
}

async function runWorkers(tasks, jobs, onRec) {
  let next = 0, done = 0; const errors = [];
  await new Promise((resolve, reject) => {
    const nw = Math.min(jobs, tasks.length); let live = nw; if (!nw) return resolve();
    for (let k = 0; k < nw; k++) {
      const w = cp.fork(__filename, ['--oa-child'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
      let finished = false;
      const feed = () => {
        if (next >= tasks.length) { finished = true; w.send('exit'); if (--live === 0) resolve(); return; }
        const i = next++; w.send({ i, file: tasks[i].file, g: tasks[i].g });
      };
      w.on('message', m => { if (m.error) errors.push(tasks[m.i].g.gameId + ' ' + m.error); else onRec(m.rec); if (++done % 25 === 0) process.stderr.write(`${done}/${tasks.length} `); feed(); });
      w.on('error', reject);
      w.on('exit', code => { if (!finished) reject(Error('child exited with code ' + code)); });
      feed();
    }
  });
  process.stderr.write('\n');
  if (errors.length) { console.error(errors.join('\n')); throw Error(errors.length + ' games failed'); }
}

if (CHILD) {
  const load = TF.makeLoader(TF.viewerSource());
  process.on('message', task => {
    if (task === 'exit') { process.exit(0); return; }
    try {
      const R = load(task.file), g = task.g;
      const a = BS.analyse(R, g);
      const x = extra(R, g);
      const res = R.result, us = res['team' + g.ourSide], them = res['team' + (g.ourSide === 'A' ? 'B' : 'A')];
      const rec = {
        set: g.set, gameId: g.gameId, map: g.mapName, type: ELIM_MAPS.includes(g.mapName) ? 'elim' : 'r500', opp: g.opponentTeam, oppName: g.oppName,
        sub: g.ourSubmission, win: g.ourWin ? 1 : 0, seed: R.seed, winnerName: g.winnerName || null, variant: g.mapName === 'Prisoners Dilemma' ? (M_init(R) === 10 ? 'PD10' : 'PD6') : null,
        nInit: M_init(R), G: us.dragonCount > 0 ? us.longestDragon : 0, theirLongest: them.longestDragon, total: us.totalLength, theirTotal: them.totalLength,
        survived: us.dragonCount > 0 ? 1 : 0, elimUs: res.endReason === 'teamEliminated' && us.dragonCount === 0 ? 1 : 0, elimThem: res.endReason === 'teamEliminated' && them.dragonCount === 0 ? 1 : 0,
        a: trim(a), x,
      };
      process.send({ i: task.i, rec });
    } catch (err) { process.send({ i: task.i, error: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | ') }); }
  });
}
function M_init(R) { return R.match.map.initialDragons.length; }

async function main() {
  const argv = process.argv.slice(2);
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const sets = opt('sets', DEFAULT_SETS.join(',')).split(',');
  const jobs = Math.min(3, Math.max(1, +opt('jobs', 3)));
  const out = path.resolve(ROOT, opt('out', '.cache/online-analysis/study.jsonl'));
  const only = opt('games', null) ? new Set(opt('games').split(',').map(Number)) : null;
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const topMaps = opt('top', null);
  const tasks = topMaps ? listTop(topMaps.split(',')) : listGames(sets, only);
  process.stderr.write(`study: ${tasks.length} games from ${sets.join(', ')} with ${jobs} workers -> ${out}\n`);
  const t0 = Date.now(), recs = [];
  await runWorkers(tasks, jobs, rec => recs.push(rec));
  recs.sort((p, q) => sets.indexOf(p.set) - sets.indexOf(q.set) || String(p.gameId).localeCompare(String(q.gameId)));
  fs.writeFileSync(out, recs.map(r => JSON.stringify(r)).join('\n') + '\n');
  // checks summary
  const c = { games: recs.length, analyse: {}, extraUpdates: 0, extraDeaths: 0, finalMismatch: 0, massMismatch: 0 };
  for (const r of recs) {
    for (const [k, v] of Object.entries(r.a.checks)) if (typeof v === 'number') c.analyse[k] = (c.analyse[k] || 0) + v;
    c.extraUpdates += r.x.chk.updates; c.extraDeaths += r.x.chk.deaths;
    if (!r.a.finalMatch) c.finalMismatch++; for (const m of r.a.mass) if (!m.ok) c.massMismatch++;
  }
  console.log(JSON.stringify(c));
  process.stderr.write(`done in ${((Date.now() - t0) / 1000).toFixed(1)}s\n`);
}
if (!CHILD && require.main === module) main().catch(err => { console.error(err); process.exit(1); });
module.exports = { extra };
