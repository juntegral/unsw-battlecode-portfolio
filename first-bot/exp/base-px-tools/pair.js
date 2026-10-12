#!/usr/bin/env node
// Paired comparison of two eval.js labels by key (opp:map:side:seed).
// usage: node pair.js <candLabel> <baseLabel> [--by opp|map|oppmap] [--opps a,b] [--maps m1,m2]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = require('path').resolve(__dirname, '..', '..');
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const load = L => { const m = new Map(); for (const lab of L.split('+')) for (const l of fs.readFileSync(path.join(ROOT, 'exp', lab, 'rows.jsonl'), 'utf8').split('\n')) { if (!l.trim()) continue; const r = JSON.parse(l); if (r.G === undefined || m.has(r.key)) continue; m.set(r.key, r); } return m; };
const A = load(argv[0]), B = load(argv[1]);
const oppsF = arg('opps') ? new Set(arg('opps').split(',')) : null, mapsF = arg('maps') ? new Set(arg('maps').split(',')) : null;
const pairs = [];
for (const [k, a] of A) { const b = B.get(k); if (!b) continue; if (oppsF && !oppsF.has(a.opp)) continue; if (mapsF && !mapsF.has(a.map)) continue; pairs.push({ k, opp: a.opp, map: a.map, a, b, d: a.G - b.G, dw: (a.won ? 1 : 0) - (b.won ? 1 : 0) }); }
const mean = x => x.length ? x.reduce((s, v) => s + v, 0) / x.length : NaN;
function boot(P, f, reps = 4000) {
  // cluster bootstrap by map
  const maps = [...new Set(P.map(p => p.map))]; const by = maps.map(m => P.filter(p => p.map === m));
  let s = 20260930; const rnd = () => (s = (Math.imul(s, 1103515245) + 12345) >>> 0) / 4294967296; const r = [];
  for (let i = 0; i < reps; i++) { const pick = []; for (let j = 0; j < by.length; j++) pick.push(...by[Math.floor(rnd() * by.length)]); r.push(mean(pick.map(f))); }
  r.sort((x, y) => x - y); return [r[Math.floor(0.025 * reps)], r[Math.floor(0.975 * reps)]];
}
function line(name, P) {
  if (!P.length) return;
  const dG = mean(P.map(p => p.d)), ci = boot(P, p => p.d), dW = mean(P.map(p => p.dw)), ciw = boot(P, p => p.dw);
  const winA = mean(P.map(p => p.a.won ? 1 : 0)), winB = mean(P.map(p => p.b.won ? 1 : 0));
  const GA = mean(P.map(p => p.a.G)), GB = mean(P.map(p => p.b.G));
  const sd = Math.sqrt(mean(P.map(p => (p.d - dG) ** 2)));
  console.log(`| ${name} | ${P.length} | ${(100 * winA).toFixed(1)}% | ${(100 * winB).toFixed(1)}% | ${(100 * dW).toFixed(1)} [${(100 * ciw[0]).toFixed(1)}, ${(100 * ciw[1]).toFixed(1)}] | ${GA.toFixed(2)} | ${GB.toFixed(2)} | ${dG.toFixed(2)} [${ci[0].toFixed(2)}, ${ci[1].toFixed(2)}] | ${sd.toFixed(1)} | ${P.filter(p => p.d === 0 && p.a.won === p.b.won).length} |`);
}
console.log(`${argv[0]} vs ${argv[1]}`);
console.log('| group | pairs | win cand | win base | dWin (pp) [95% CI] | G cand | G base | dG [95% CI] | SD | identical |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
const by = arg('by', 'opp');
line('(all)', pairs);
const keyOf = p => by === 'map' ? p.map : by === 'oppmap' ? p.opp + ' ' + p.map : p.opp;
for (const g of [...new Set(pairs.map(keyOf))].sort()) line(g, pairs.filter(p => keyOf(p) === g));
