#!/usr/bin/env node
// Paired comparison of eval labels (or eval dirs) against a baseline, keyed by opp:map:side:seed.
// usage: node exp/cand-portal1/compare.js <cand label|dir> [--base eval-r1] [--by map|opp|side|all] [--md]
// Prints n, baseline and candidate means, and the paired difference with a 95% interval (mean +- 1.96 SD/sqrt(n))
// for G (our longest living dragon, 0 if eliminated), win and survival. "all" also gets the map-cluster bootstrap
// interval that tools/eval.js prints (resample whole maps, 4000 draws, same generator seed).
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const dirOf = l => l.includes('/') ? path.resolve(l) : path.join(ROOT, 'exp', l);
const rows = l => { const m = new Map(); for (const line of fs.readFileSync(path.join(dirOf(l), 'rows.jsonl'), 'utf8').trim().split('\n')) { const r = JSON.parse(line); if (r.G !== undefined && !m.has(r.key)) m.set(r.key, r); } return m; };
const cand = rows(process.argv[2]), base = rows(arg('base', 'eval-r1'));
const pairs = [...cand.values()].filter(r => base.has(r.key)).map(r => ({ c: r, b: base.get(r.key) }));
const mean = a => a.reduce((s, x) => s + x, 0) / a.length;
const ci = d => { const m = mean(d), n = d.length, sd = Math.sqrt(d.reduce((s, x) => s + (x - m) ** 2, 0) / Math.max(1, n - 1)); return [m, m - 1.96 * sd / Math.sqrt(n), m + 1.96 * sd / Math.sqrt(n), sd]; };
const f = (x, k = 2) => (x >= 0 ? '+' : '') + x.toFixed(k);
function bootstrap(ps) {
  const byMap = [...new Set(ps.map(p => p.c.map))].map(m => ps.filter(p => p.c.map === m).map(p => p.c.G - p.b.G));
  let s = 20260927; const rnd = () => (s = (Math.imul(s, 1103515245) + 12345) >>> 0) / 4294967296; const reps = [];
  for (let k = 0; k < 4000; k++) { const pick = byMap.map(() => byMap[Math.floor(rnd() * byMap.length)]).flat(); reps.push(mean(pick)); }
  reps.sort((a, b) => a - b); return [reps[Math.floor(0.025 * reps.length)], reps[Math.floor(0.975 * reps.length)]];
}
function line(label, ps, boot) {
  const g = ci(ps.map(p => p.c.G - p.b.G)), w = ci(ps.map(p => +p.c.won - +p.b.won)), a = ci(ps.map(p => +p.c.alive - +p.b.alive));
  const bs = boot ? ` boot[${bootstrap(ps).map(x => f(x)).join(', ')}]` : '';
  return { label, n: ps.length, Gb: mean(ps.map(p => p.b.G)), Gc: mean(ps.map(p => p.c.G)), g, bs,
    wb: mean(ps.map(p => +p.b.won)), wc: mean(ps.map(p => +p.c.won)), w, ab: mean(ps.map(p => +p.b.alive)), ac: mean(ps.map(p => +p.c.alive)), a };
}
const groups = [['all', pairs]];
for (const by of (arg('by', 'map') || 'map').split(',')) {
  if (by === 'all') continue;
  for (const k of [...new Set(pairs.map(p => p.c[by]))].sort()) groups.push([by + '=' + k, pairs.filter(p => p.c[by] === k)]);
}
const md = process.argv.includes('--md');
if (md) {
  console.log('| 범위 | 판 | G 기준 → 후보 | G 차이 [95% 구간] | 승 기준 → 후보 (차이 [구간]) | 생존 기준 → 후보 (차이 [구간]) |');
  console.log('|---|---:|---|---|---|---|');
}
for (const [label, ps] of groups) {
  if (!ps.length) continue;
  const L = line(label, ps, label === 'all');
  if (md) console.log(`| ${label.replace(/^map=|^opp=|^side=/, '')} | ${L.n} | ${L.Gb.toFixed(1)} → ${L.Gc.toFixed(1)} | ${f(L.g[0])} [${f(L.g[1])}, ${f(L.g[2])}]${L.bs ? ' (지도 묶음 붓스트랩 ' + L.bs.trim().replace('boot', '') + ')' : ''} | ${L.wb.toFixed(3)} → ${L.wc.toFixed(3)} (${f(L.w[0], 3)} [${f(L.w[1], 3)}, ${f(L.w[2], 3)}]) | ${L.ab.toFixed(3)} → ${L.ac.toFixed(3)} (${f(L.a[0], 3)} [${f(L.a[1], 3)}, ${f(L.a[2], 3)}]) |`);
  else console.log(`${label.padEnd(26)} n=${String(L.n).padStart(3)} G ${L.Gb.toFixed(1)} -> ${L.Gc.toFixed(1)} dG ${f(L.g[0])} [${f(L.g[1])}, ${f(L.g[2])}] sd ${L.g[3].toFixed(1)}${L.bs} | win ${L.wb.toFixed(3)}->${L.wc.toFixed(3)} ${f(L.w[0], 3)} [${f(L.w[1], 3)}, ${f(L.w[2], 3)}] | alive ${L.ab.toFixed(3)}->${L.ac.toFixed(3)} ${f(L.a[0], 3)} [${f(L.a[1], 3)}, ${f(L.a[2], 3)}]`);
}
