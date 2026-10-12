#!/usr/bin/env node
'use strict';
// follow.js — what happens after a long dragon of ours stands where every single step is exposed (2026-09-30 online analysis).
// Reads replays only.
// usage (repository root):
//   node exp/online-analysis/follow.js --corner <corner_study.js --out file> [--sets a,b,...] [--out follow.json]
// Input: the decision records of exp/cand-avoid1/corner_study.js (our dragons of length >= 6 with a shorter enemy head in
// the 7x7 window). It keeps the decisions where every legal single step ends inside the true reach of a visible shorter
// enemy head ("all singles exposed"), finds each one in its replay (same game, round and dragon) and follows the dragon:
//   - the action taken there: steps, sprint, our indicator (' esc' = cand-avoid6 escape sprint), sprint cost paid,
//   - rammed before its next decision (corner_study's own flag is kept too),
//   - then the dragon, following the longer piece at each split (the child on a tie): alive and length 10, 20 and 50
//     rounds later, death round and cause, final length and whether it is our longest dragon at the end.
// Body reconstruction as in tools/top_features.js extract(); head/tail mismatches against dragonUpdate are counted.
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const BS = require(path.join(ROOT, 'tools', 'baseline_study.js'));
const DIRS = 'NESW';
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const SETS = opt('sets', 'baseline-r1,baseline-r1b,baseline-r1c,cand-avoid6-online,px-king-v2-online').split(',');
const cornerFile = opt('corner', null), outFile = opt('out', null);
if (!cornerFile) { console.error('usage: follow.js --corner <file> [--sets ...] [--out file]'); process.exit(2); }

const where = new Map();   // gameId -> {set, dir, ourSide}
for (const set of SETS) {
  const dir = path.join(ROOT, 'data', 'online', set);
  for (const g of JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8')).games) where.set(String(g.gameId), { set, dir, us: String(g.ourSide).toUpperCase(), map: g.mapName, opp: g.opponentTeam });
}
const all = JSON.parse(fs.readFileSync(path.resolve(ROOT, cornerFile), 'utf8'));
const byGame = new Map();
for (const d of all) {
  if (!d.allExposed) continue;
  if (!where.has(String(d.game))) continue;
  if (!byGame.has(String(d.game))) byGame.set(String(d.game), []);
  byGame.get(String(d.game)).push(d);
}

function followGame(gid, decs) {
  const W0 = where.get(gid), R = load(path.join(W0.dir, `M${gid}.replay`));
  const M = R.match.map, { W, N, nb } = BS.buildGeo(M), US = W0.us;
  const tileOf = s => s.y * W + s.x;
  const drag = new Map(), occ = new Int32Array(N).fill(-1), pearl = new Uint8Array(N);
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearl[i] = 1;
  const setOcc = d => { for (const t of d.body) occ[t] = d.id; };
  const clrOcc = d => { for (const t of d.body) if (occ[t] === d.id) occ[t] = -1; };
  for (const d0 of M.initialDragons) { const d = { id: d0.id, team: d0.team, body: d0.body.map(tileOf), expect: [], ind: null, fate: null }; drag.set(d.id, d); setOcc(d); }
  const want = new Map(); for (const d of decs) want.set(d.round + ':' + d.id, d);
  const fol = []; let round = -1, cur = -1, mism = 0;
  const longest = team => { let m = 0; for (const o of drag.values()) if (o.team === team && o.body.length > m) m = o.body.length; return m; };
  for (const e of R.events) {
    switch (e.type) {
      case 'roundStart':
        round = e.round;
        for (const f of fol) { if (f.done) continue; const age = round - f.rec.round; for (const a of [10, 20, 50]) if (age === a) { const x = drag.get(f.cur); f.rec['len' + a] = x ? x.body.length : 0; } }
        break;
      case 'turnStart': { cur = e.id; const d = drag.get(cur); if (d) { d.expect = []; d.ind = null; d.fate = null; } break; }
      case 'dragonIndicator': { const d = drag.get(e.id); if (d) d.ind = e.text; break; }
      case 'tileChange': { const k = tileOf(e.tile); pearl[k] = e.hasPearl ? 1 : 0; break; }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action;
        // an open follower on this dragon that has not acted since its decision: this is its next decision
        for (const f of fol) if (!f.done && f.cur === d.id && f.acted && !f.nextSeen) f.nextSeen = true;
        const w = want.get(round + ':' + d.id);
        if (w && d.team === US) {
          const s = d.ind || '';
          const rec = { set: W0.set, game: +gid, map: W0.map, opp: W0.opp, round, id: d.id, L: d.body.length, kind: a ? a.kind : null,
            steps: a && a.kind === 'move' ? a.steps.length : 0, esc: / esc(\s|$)/.test(s) ? 1 : 0, escSplit: s.startsWith('escape-split') ? 1 : 0,
            late: / late(\s|$)/.test(s) ? 1 : 0, rammedCS: w.rammed, safe2: w.safe2, safe3: w.safe3, n1: w.n1 };
          fol.push({ rec, cur: d.id, done: false, acted: true, nextSeen: false });
          want.delete(round + ':' + d.id);
        }
        if (!a || a.kind !== 'move') break;
        clrOcc(d);
        const body = d.body.slice(); let fate = null;
        for (let i = 0; i < a.steps.length; i++) {
          if (i > 0 && body.length <= 2) { fate = 'A'; break; }
          const nx = nb[body[0] * 4 + DIRS.indexOf(a.steps[i])];
          if (nx < 0) { fate = 'W'; break; }
          if (body.includes(nx)) { fate = 'S'; break; }
          if (occ[nx] !== -1) { fate = 'X'; break; }
          body.unshift(nx); if (!pearl[nx]) body.pop(); if (i > 0) body.pop();
          d.expect.push({ h: body[0], t: body[body.length - 1] });
        }
        d.fate = fate; d.body = body; setOcc(d);
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id); if (!d || round < 0) break;
        const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        const eh = tileOf(e.head), et = tileOf(e.tail);
        if (x.h !== eh || x.t !== et) { mism++; clrOcc(d); const b = d.body.slice(); if (b[0] !== eh) b.unshift(eh); while (b.length > 1 && b[b.length - 1] !== et) b.pop(); d.body = b; d.expect = []; setOcc(d); }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        const cl = e.childBody.length, pl = e.parentBody.length;
        clrOcc(p); p.body = e.parentBody.map(tileOf); setOcc(p);
        const c = { id: e.childId, team: e.team, body: e.childBody.map(tileOf), expect: [], ind: null, fate: null }; drag.set(c.id, c); setOcc(c);
        for (const f of fol) if (!f.done && f.cur === p.id && cl >= pl) f.cur = c.id;
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        const mover = cur === d.id, m = drag.get(cur);
        const cause = !mover && e.reason === 'H' && m && m.team !== d.team ? 'rammed' : mover && e.reason === 'H' && d.fate === 'X' ? 'headOn' : e.reason === 'O' ? 'body' : mover ? 'self' : 'other';
        for (const f of fol) if (!f.done && f.cur === d.id) {
          f.done = true; f.rec.death = { r: round, dr: round - f.rec.round, cause, len: d.body.length, beforeNext: f.nextSeen ? 0 : 1 };
        }
        clrOcc(d); drag.delete(e.id);
        break;
      }
      default: break;
    }
  }
  const top = longest(US);
  for (const f of fol) { if (f.done) continue; const x = drag.get(f.cur); f.rec.final = x ? x.body.length : 0; f.rec.finalLongest = x && x.body.length === top ? 1 : 0; }
  return { recs: fol.map(f => f.rec), missing: [...want.values()].length, mism };
}

const out = []; let missing = 0, mism = 0, n = 0;
for (const [gid, decs] of byGame) {
  const r = followGame(gid, decs); out.push(...r.recs); missing += r.missing; mism += r.mism;
  if (++n % 20 === 0) process.stderr.write(n + ' ');
}
process.stderr.write('\n');
console.log(`games ${byGame.size}, all-exposed decisions ${[...byGame.values()].reduce((s, x) => s + x.length, 0)}, followed ${out.length}, not found ${missing}, head/tail mismatches ${mism}`);
if (outFile) fs.writeFileSync(path.resolve(ROOT, outFile), JSON.stringify(out));
