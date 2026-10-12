#!/usr/bin/env node
// exp/portals: the selection table on a fixed key set (PLAN.md): king500 median / P25 / P75 / mean / P10 / min, king deaths (all, r300+),
// eliminations, conversion, unconverted mass, handoffs; bootstrap 95% intervals of the median and mean difference against the first file.
// usage: node final.js --seeds 11-30 a.jsonl b.jsonl ...
'use strict';
const fs = require('fs'), path = require('path');
const argv = process.argv.slice(2);
const si = argv.indexOf('--seeds'); const [s0, s1] = (si >= 0 ? argv[si + 1] : '1-999').split('-').map(Number);
const files = argv.filter(a => a.endsWith('.jsonl'));
const q = (xs, p) => { const a = [...xs].sort((u, v) => u - v); const i = (a.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return a[lo] + (a[hi] - a[lo]) * (i - lo); };
const mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
let seed = 12345; const rnd = () => (seed = (Math.imul(seed, 1103515245) + 12345) >>> 0) / 4294967296;
const sets = files.map(f => { const rs = fs.readFileSync(f, 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.seed >= s0 && r.seed <= s1); return { name: path.basename(f, '.jsonl'), rs, by: new Map(rs.map(r => [r.key, r])) }; });
const keys = [...sets[0].by.keys()].filter(k => sets.every(s => s.by.has(k)));
console.log(`keys ${keys.length} (seeds ${s0}-${s1}; present in every file)`);
const row = (label, fn) => console.log(label.padEnd(44) + ' | ' + sets.map(s => fn(keys.map(k => s.by.get(k)))).join(' | '));
console.log('variant'.padEnd(44) + ' | ' + sets.map(s => s.name).join(' | '));
row('king500 median [P25-P75]', rs => { const k = rs.map(r => r.k500); return `${q(k, .5).toFixed(1)} [${q(k, .25).toFixed(1)}-${q(k, .75).toFixed(1)}]`; });
row('king500 mean / P10 / min', rs => { const k = rs.map(r => r.k500); return `${mean(k).toFixed(2)} / ${q(k, .1).toFixed(1)} / ${Math.min(...k)}`; });
row('eliminated (king500 0)', rs => String(rs.filter(r => r.k500 === 0).length));
row('king deaths / game (all | r300+)', rs => `${(rs.reduce((a, r) => a + r.kingDeaths.length, 0) / rs.length).toFixed(2)} | ${(rs.reduce((a, r) => a + r.kingDeaths.filter(k => k.r >= 300).length, 0) / rs.length).toFixed(2)}`);
row('king deaths r400+ (count)', rs => String(rs.reduce((a, r) => a + r.kingDeaths.filter(k => k.r >= 400).length, 0)));
row('king deaths in rooms before r300 / game', rs => (rs.reduce((a, r) => a + r.kingDeaths.filter(k => k.room && k.r < 300).length, 0) / rs.length).toFixed(2));
row('king r300 / r400 / r450 (median)', rs => [30, 40, 45].map(i => q(rs.map(r => r.king[i]), .5).toFixed(1)).join(' / '));
row('king growth r300->r400 (median of per-game)', rs => q(rs.map(r => r.king[40] - r.king[30]), .5).toFixed(1));
row('total mass r250 / r300 / r400 (mean)', rs => [25, 30, 40].map(i => mean(rs.map(r => r.total[i])).toFixed(1)).join(' / '));
row('conversion k500/total400 (median)', rs => q(rs.filter(r => r.total[40] > 0).map(r => r.k500 / r.total[40]), .5).toFixed(2));
row('total500 - king500 (median)', rs => q(rs.map(r => r.total[50] - r.k500), .5).toFixed(1));
row('king handoffs / game (r300+)', rs => `${(rs.reduce((a, r) => a + r.handoffs.length, 0) / rs.length).toFixed(1)} (${(rs.reduce((a, r) => a + r.handoffs.filter(h => h.r >= 300).length, 0) / rs.length).toFixed(1)})`);
for (let i = 1; i < sets.length; i++) {
  const a = keys.map(k => sets[0].by.get(k).k500), b = keys.map(k => sets[i].by.get(k).k500);
  const dMed = [], dMean = [];
  for (let r = 0; r < 4000; r++) { const ia = [], ib = []; for (let j = 0; j < a.length; j++) { ia.push(a[Math.floor(rnd() * a.length)]); ib.push(b[Math.floor(rnd() * b.length)]); } dMed.push(q(ib, .5) - q(ia, .5)); dMean.push(mean(ib) - mean(ia)); }
  dMed.sort((u, v) => u - v); dMean.sort((u, v) => u - v);
  const wins = keys.filter(k => sets[i].by.get(k).k500 > sets[0].by.get(k).k500).length, losses = keys.filter(k => sets[i].by.get(k).k500 < sets[0].by.get(k).k500).length;
  console.log(`${sets[i].name} - ${sets[0].name}: median ${(q(b, .5) - q(a, .5)).toFixed(1)} (95% ${dMed[100].toFixed(1)}..${dMed[3899].toFixed(1)}), mean ${(mean(b) - mean(a)).toFixed(2)} (95% ${dMean[100].toFixed(2)}..${dMean[3899].toFixed(2)}), same-key wins ${wins} / losses ${losses}`);
}
