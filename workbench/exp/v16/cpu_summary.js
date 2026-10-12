#!/usr/bin/env node
// v1.6 CPU: our team's judge points per turn (unswbc -v, recorded by exp/v16/runq.js in a lane with "cpu": true) per map: the largest max and p99
// over the games, and the games' turn counts. usage: node exp/v16/cpu_summary.js <dir> [<dir> ...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const by = new Map();
for (const d of process.argv.slice(2)) {
  const f = path.join(path.resolve(ROOT, d), 'rows.jsonl'); if (!fs.existsSync(f)) continue;
  for (const l of fs.readFileSync(f, 'utf8').split('\n').filter(Boolean)) {
    const r = JSON.parse(l); if (!r.cpu || r.error || r.botProblem) continue;
    const line = r.cpu.find(s => s.startsWith('team ' + r.side)); if (!line) continue;
    const num = k => { const m = new RegExp(k + '\\s+([\\d.]+)M').exec(line); return m ? +m[1] : NaN; };
    const turns = +((/\((\d+) turns\)/.exec(line) || [])[1] || 0);
    const a = by.get(r.map) || { games: 0, max: 0, p99: 0, p50: [], turns: 0, worst: '' };
    a.games++; a.turns += turns; a.p50.push(num('p50'));
    if (num('max') > a.max) { a.max = num('max'); a.worst = r.key; }
    a.p99 = Math.max(a.p99, num('p99'));
    by.set(r.map, a);
  }
}
console.log('| map | games | our max points/turn (game) | largest p99 | median p50 | turns |');
console.log('|---|---|---|---|---|---|');
let all = 0;
for (const [m, a] of [...by].sort()) {
  const p50 = a.p50.sort((x, y) => x - y)[Math.floor(a.p50.length / 2)];
  console.log(`| ${m} | ${a.games} | ${a.max.toFixed(1)}M (${a.worst}) | ${a.p99.toFixed(1)}M | ${p50.toFixed(1)}M | ${a.turns} |`);
  all = Math.max(all, a.max);
}
console.log(`\nmax over all: ${all.toFixed(1)}M (limit 100M, alarm 80M)`);
