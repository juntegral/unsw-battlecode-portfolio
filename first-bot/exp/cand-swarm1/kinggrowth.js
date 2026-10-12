#!/usr/bin/env node
// Late king growth of our side on the 500-round maps (autarky, portals, schooltime, slithery_fight, trauma), games that
// reach round 500. usage: node exp/cand-swarm1/kinggrowth.js <label> [<label> ...]
// Columns: medians of our longest at r300 / r350 / r400 / r450 / r500 and of its growth r350 -> r500; mean of what the
// team's longest ate in r400-499 and the share of it that came from our own exit sacrifices (tools/proxy_check.js
// definitions: kingDiet400); exit sacrifices per side and their median round; per-map medians of the r500 longest.
'use strict';
const path = require('path'), fs = require('fs');
const ROOT = path.resolve(__dirname, '..', '..');
const pc = require(path.join(ROOT, 'tools', 'proxy_check.js'));
const ELIM = ['devil', 'trophy', 'prisoners_dilemma', 'queen_of_spades', 'default'];
const R500 = ['autarky', 'portals', 'schooltime', 'slithery_fight', 'trauma'];
const med = a => { if (!a.length) return null; const s = a.slice().sort((x, y) => x - y); const m = (s.length - 1) / 2; return (s[Math.floor(m)] + s[Math.ceil(m)]) / 2; };
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : NaN;
const f = x => x === null || Number.isNaN(x) ? '-' : (Math.round(x * 10) / 10).toString();
console.log('| label | games | longest r300 / r350 / r400 / r450 / r500 | growth r350→r500 | king ate r400+ (mean) | from own sacrifices | sacrifices/side (median round) | ' + R500.join(' | ') + ' |');
console.log('|---|---:|---|---:|---:|---:|---|' + R500.map(() => '---:').join('|') + '|');
for (const L of process.argv.slice(2)) {
  const file = path.join(ROOT, 'exp', L, 'sides.jsonl'); if (!fs.existsSync(file)) continue;
  const S = pc.readJsonl(file).filter(x => x.name === 'bot' && !ELIM.includes(x.map) && x.rounds === 500);
  const at = r => S.map(x => x.tl[r / 10] ? x.tl[r / 10][2] : null).filter(v => v !== null);
  const growth = S.map(x => x.tl[50][2] - x.tl[35][2]);
  const ate = mean(S.map(x => x.longest400)), fromSac = mean(S.map(x => x.fromFree400));
  const sac = S.map(x => x.free.length), sacR = []; for (const x of S) for (const q of x.free) sacR.push(q[0]);
  const perMap = R500.map(m => f(med(S.filter(x => x.map === m).map(x => x.tl[50][2]))));
  console.log(`| ${L} | ${S.length} | ${[300, 350, 400, 450, 500].map(r => f(med(at(r)))).join(' / ')} | ${f(med(growth))} | ${f(ate)} | ${(100 * fromSac / ate).toFixed(0)}% | ${f(mean(sac))} (r${f(med(sacR))}) | ${perMap.join(' | ')} |`);
}
