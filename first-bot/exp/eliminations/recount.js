#!/usr/bin/env node
// Independent recount of the key numbers (user rule: key numbers are counted again by separate code). It does not use
// tools/mass_ledger.js or exp/eliminations/extract.js: only the replay parser and the raw events (dragonSplit, dragonDeath,
// roundStart, turnStart, dragonAction) and R.result.
//   Per team: units at the start of rounds 30 / 50 / 100 (map dragons + split children - deaths), the elimination round (the
//   last death of a team whose result says 0 dragons), and for the last three deaths of an eliminated team: the death reason
//   ('H' head-on, 'O' body, 'S' self, 'W' wall/kelp, 'A' action) and, for a head-on, whether the dragon that moved took 2+ steps
//   (the requested steps of its action).
// usage: node exp/eliminations/recount.js online|top [--keys <file>] [--every K] [--jobs 4]
//   compares with the extraction cache and prints the number of disagreements per quantity (all expected 0; the sprint flag
//   compares requested steps with executed steps, so a sprint cut short by the collision may differ).
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const L = require('./lib.js');
const X = require('./extract.js');

function recount(R) {
  const team = new Map(), alive = { A: 0, B: 0 }, at = { A: {}, B: {} }, deaths = { A: [], B: [] };
  for (const d of R.match.map.initialDragons) { team.set(d.id, d.team); alive[d.team]++; }
  let round = -1, cur = -1; const steps = new Map();
  for (const e of R.events) {
    if (e.type === 'roundStart') { round = e.round; if ([30, 50, 100].includes(round)) for (const t of ['A', 'B']) at[t][round] = alive[t]; }
    else if (e.type === 'turnStart') cur = e.id;
    else if (e.type === 'dragonAction') steps.set(e.id, e.action && e.action.kind === 'move' ? e.action.steps.length : 0);
    else if (e.type === 'dragonSplit') { team.set(e.childId, e.team); alive[e.team]++; }
    else if (e.type === 'dragonDeath') {
      const t = team.get(e.id); alive[t]--;
      const mover = cur, ms = steps.get(mover) || 0;
      deaths[t].push({ r: round, reason: e.reason, moverOwn: team.get(mover) === t, moverSteps: ms, self: mover === e.id });
    }
  }
  const out = { rounds: round + 1 };
  for (const t of ['A', 'B']) {
    const dc = R.result['team' + t].dragonCount;
    out[t] = { u30: at[t][30], u50: at[t][50], u100: at[t][100], end: alive[t], resEnd: dc, elim: dc === 0 && deaths[t].length ? deaths[t][deaths[t].length - 1].r : -1,
      last3: deaths[t].slice(-3).map(d => ({ r: d.r, H: d.reason === 'H' ? 1 : 0, spr: d.reason === 'H' && !d.self && d.moverSteps >= 2 ? 1 : 0 })) };
  }
  return out;
}

function workerMain() {
  const { makeLoader, viewerSource } = require(path.join(L.ROOT, 'tools', 'top_features.js'));
  const load = makeLoader(viewerSource());
  process.on('message', t => { try { process.send({ key: t.key, res: recount(load(t.file)) }); } catch (err) { process.send({ key: t.key, error: String(err) }); } });
}
async function runAll(tasks, jobs) {
  const res = new Map(), q = tasks.slice();
  await Promise.all(Array.from({ length: Math.min(jobs, q.length) }, () => new Promise(resolve => {
    const w = cp.fork(__filename, ['--worker']);
    const next = () => { const t = q.shift(); if (!t) { w.kill(); resolve(); return; } w.send(t); };
    w.on('message', m => { if (!m.error) res.set(m.key, m.res); else console.error(m.key, m.error); next(); });
    next();
  })));
  return res;
}
async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const src = argv[0], every = +opt('every', 1), jobs = +opt('jobs', 4);
  let tasks, cache;
  if (src === 'online') { tasks = L.SETS.flatMap(s => X.onlineTasks(s[0])); cache = L.SETS.flatMap(s => L.readGz(path.join(L.CACHE, 'online-' + s[0] + '.jsonl.gz'))); }
  else { tasks = X.topTasks(opt('keys')); cache = L.readGz(path.join(L.CACHE, 'top.jsonl.gz')); }
  tasks = tasks.filter((t, i) => i % every === 0);
  const byKey = new Map(cache.map(g => [g.key, g]));
  tasks = tasks.filter(t => byKey.has(t.key));
  console.log(`${src}: recounting ${tasks.length} games (every ${every})`);
  const res = await runAll(tasks, jobs);
  const bad = { u30: 0, u50: 0, u100: 0, end: 0, elim: 0, last3H: 0, last3spr: 0 }, n = { teams: 0, elimTeams: 0, last3: 0, sprAgree: 0, spr: 0 };
  const ex = [];
  for (const t of tasks) {
    const g = byKey.get(t.key), r = res.get(t.key); if (!r) continue;
    for (const tm of ['A', 'B']) {
      n.teams++;
      const T = g.T[tm], q = r[tm];
      for (const c of [30, 50, 100]) if (g.rounds > c && q['u' + c] !== undefined && L.at(g, tm, c, 'u') !== q['u' + c]) { bad['u' + c]++; if (ex.length < 5) ex.push([t.key, tm, c, L.at(g, tm, c, 'u'), q['u' + c]]); }
      if (T.end.u !== q.resEnd) bad.end++;
      if (T.elim !== q.elim) bad.elim++;
      if (q.elim >= 0) {
        n.elimTeams++;
        const mine = T.last.slice(-3);
        for (let i = 0; i < Math.min(mine.length, q.last3.length); i++) {
          n.last3++;
          const a = mine[mine.length - 1 - i], b = q.last3[q.last3.length - 1 - i];
          const aH = a[2] === 2 || a[2] === 3 || a[2] === 5 ? 1 : 0; // head-on causes of the ledger: rammed, ram, allyHead
          if (aH !== b.H) bad.last3H++;
          if (a[2] === 2 && b.H) { n.spr++; if ((a[3] >= 2 ? 1 : 0) === b.spr) n.sprAgree++; }
        }
      }
    }
  }
  console.log(`teams ${n.teams}, eliminated ${n.elimTeams}; disagreements ${JSON.stringify(bad)}; rammed deaths compared ${n.spr}, sprint flag agrees ${n.sprAgree}`);
  if (ex.length) console.log('examples', JSON.stringify(ex));
}
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
