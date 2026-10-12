#!/usr/bin/env node
'use strict';
// ab_matched.js — one bot on layout a against layout b of the five two-layout maps with the same seeds: games are paired
// by (opp, map, side, seed), so a pair differs only in the map's TILE lines (the pearl layout; Prisoners Dilemma 10 also
// adds two dragons per team). The standard screen (tools/pair_ab.js) runs a on seed 1 and b on seed 2, so its a -> b
// difference per map also carries the seed.
// usage (repository root):
//   node exp/proxy4-tools/ab_matched.js --a <label>[@seed][+...] --b <label>[@seed][+...] [--name <text>] [--json <file>]
//     Rows come from exp/<label>/rows.jsonl (tools/eval.js); @seed keeps one seed of a label. a rows: the five a map
//     files (devil, queen_of_spades, schooltime, slithery_fight, prisoners_dilemma); b rows: *_b and prisoners_dilemma_10.
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const TWO = ['devil', 'queen_of_spades', 'schooltime', 'slithery_fight', 'prisoners_dilemma'];
function rows(spec, layout) {
  const out = [], seen = new Set();
  for (const part of spec.split('+')) {
    const [L, sd] = part.split('@');
    for (const l of fs.readFileSync(path.join(ROOT, 'exp', L, 'rows.jsonl'), 'utf8').split('\n')) {
      if (!l.trim()) continue; const r = JSON.parse(l); if (r.G === undefined || (sd && r.seed !== +sd)) continue;
      const isB = /_b$|_10$/.test(r.map), bmap = r.map.replace(/_b$|_10$/, '');
      if (!TWO.includes(bmap) || isB !== (layout === 'b')) continue;
      const k = [r.opp, bmap, r.side, r.seed].join(':'); if (seen.has(k)) continue; seen.add(k);
      out.push({ ...r, bmap, k });
    }
  }
  return out;
}
const mean = a => a.reduce((s, x) => s + x, 0) / a.length;
function tq(nu) { const z = 1.959964; if (nu === 1) return 12.706; if (nu === 2) return 4.303; return z + (z ** 3 + z) / (4 * nu) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * nu * nu); }
function ci(a) { const n = a.length, m = mean(a); if (n < 2) return [m, NaN, NaN]; const sd = Math.sqrt(a.reduce((s, x) => s + (x - m) ** 2, 0) / (n - 1)), h = tq(n - 1) * sd / Math.sqrt(n); return [m, m - h, m + h]; }
const A = rows(arg('a'), 'a'), B = rows(arg('b'), 'b'), bk = new Map(B.map(r => [r.k, r]));
const P = A.filter(r => bk.has(r.k)).map(r => ({ a: r, b: bk.get(r.k), bmap: r.bmap, seed: r.seed }));
const f = (x, d = 1) => Number.isFinite(x) ? (x >= 0 ? '+' : '') + x.toFixed(d) : '-';
const pc = x => (100 * x).toFixed(0);
console.log(`# ${arg('name', 'a vs b, matched seeds')}: ${P.length} pairs (a rows ${A.length}, b rows ${B.length}), seeds ${[...new Set(P.map(p => p.seed))].sort().join(',')}`);
console.log('| 지도 | 짝 | G a / b | G b−a [95%] | 승 % a / b | 승 b−a %p [95%] | 생존 % a / b | 생존 b−a %p [95%] |');
console.log('|---|---:|---|---|---|---|---|---|');
const out = [];
for (const m of [...TWO, 'all']) {
  const Q = m === 'all' ? P : P.filter(p => p.bmap === m); if (!Q.length) continue;
  const dG = ci(Q.map(p => p.b.G - p.a.G)), dW = ci(Q.map(p => +p.b.won - +p.a.won)), dA = ci(Q.map(p => +p.b.alive - +p.a.alive));
  const row = { map: m, n: Q.length, Ga: mean(Q.map(p => p.a.G)), Gb: mean(Q.map(p => p.b.G)), dG, winA: mean(Q.map(p => +p.a.won)), winB: mean(Q.map(p => +p.b.won)), dW, aliveA: mean(Q.map(p => +p.a.alive)), aliveB: mean(Q.map(p => +p.b.alive)), dA };
  out.push(row);
  console.log(`| ${m === 'all' ? '**다섯 지도**' : m} | ${Q.length} | ${row.Ga.toFixed(1)} / ${row.Gb.toFixed(1)} | ${f(dG[0])} [${f(dG[1])}, ${f(dG[2])}] | ${pc(row.winA)} / ${pc(row.winB)} | ${f(100 * dW[0], 0)} [${f(100 * dW[1], 0)}, ${f(100 * dW[2], 0)}] | ${pc(row.aliveA)} / ${pc(row.aliveB)} | ${f(100 * dA[0], 0)} [${f(100 * dA[1], 0)}, ${f(100 * dA[2], 0)}] |`);
}
if (arg('json')) fs.writeFileSync(path.resolve(ROOT, arg('json')), JSON.stringify(out, null, 1) + '\n');
