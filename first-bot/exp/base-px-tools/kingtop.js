#!/usr/bin/env node
// kingstat analyse() over the top snapshot (both sides), cache king-top.jsonl in the scratchpad.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = require('path').resolve(__dirname, '..', '..');
const TOP = path.join(ROOT, 'data', 'top');
const OUT = path.join(__dirname, 'cache', 'king-top.jsonl');
if (process.argv.includes('--kt-worker')) {
  const { analyse } = require('./kingstat.js');
  process.on('message', t => { try { process.send({ t, res: analyse(t.file, t.row) }); } catch (e) { process.send({ t, error: String(e).slice(0, 300) }); } });
  return;
}
const keys = [...new Set(fs.readFileSync(path.join(TOP, 'snapshot-20260929a.keys'), 'utf8').split('\n').map(s => s.trim()).filter(Boolean))];
const meta = new Map();
for (const l of fs.readFileSync(path.join(TOP, 'features.jsonl'), 'utf8').split('\n')) {
  const mm = /^\{"meta":\{"battleId":(\d+),"gameId":(\d+)[,}]/.exec(l); if (!mm) continue;
  const k = mm[1] + ':' + mm[2]; if (meta.has(k)) continue;
  const f = JSON.parse(l); meta.set(k, { map: f.meta.map, A: f.meta.teams.A.name, B: f.meta.teams.B.name, splitsA: f.A.splits.length, splitsB: f.B.splits.length });
}
const have = new Set(fs.existsSync(OUT) ? fs.readFileSync(OUT, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l).key) : []);
const tasks = keys.filter(k => meta.has(k) && !have.has(k)).map(k => { const [b, g] = k.split(':'); return { key: k, file: path.join(TOP, b, g + '.replay.gz'), row: { key: k, map: meta.get(k).map }, meta: meta.get(k) }; });
console.log('tasks', tasks.length);
const jobs = +(process.argv[process.argv.indexOf('--jobs') + 1] || 2);
const q = tasks.slice(); let live = 0, done = 0;
for (let i = 0; i < Math.min(jobs, q.length); i++) {
  const c = cp.fork(__filename, ['--kt-worker'], { serialization: 'advanced' }); live++;
  const next = () => { const t = q.shift(); if (!t) { c.kill(); live--; return; } c.send(t); };
  c.on('message', m => {
    if (!m.error) {
      const mapKey = String(m.t.meta.map).toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
      for (const s of ['A', 'B']) fs.appendFileSync(OUT, JSON.stringify({ key: m.t.key, map: mapKey, name: m.t.meta[s], oppName: m.t.meta[s === 'A' ? 'B' : 'A'], splitsSelf: m.t.meta['splits' + s], splitsOpp: m.t.meta['splits' + (s === 'A' ? 'B' : 'A')], us: m.res[s] }) + '\n');
    } else console.error(m.t.key, m.error);
    if (++done % 50 === 0) console.log(done);
    next();
  });
  next();
}
