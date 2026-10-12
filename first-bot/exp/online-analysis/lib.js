'use strict';
// lib.js — shared helpers for the online analysis reports (exp/online-analysis/report_*.js).
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ELIM = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default'];
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const MAPS = [...ELIM, ...R500];
const OPPS = [306, 70, 20, 801, 264, 46, 545];

function readJsonl(file) { return fs.readFileSync(file, 'utf8').split('\n').filter(l => l.trim()).map(l => JSON.parse(l)); }
const group = s => s.startsWith('baseline') ? 'base' : s.startsWith('cand-avoid6') ? 'avoid6' : s.startsWith('px-king') ? 'pxking' : s;

// Deterministic bootstrap, same generator and seed as tools/online_compare.js (mulberry32, seed 12345, 10,000 resamples).
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function boot(d, B = 10000) {
  if (!d.length) return { n: 0, mean: NaN, lo: NaN, hi: NaN };
  const mean = d.reduce((s, x) => s + x, 0) / d.length, r = rng(12345), bs = [];
  for (let i = 0; i < B; i++) { let s = 0; for (let j = 0; j < d.length; j++) s += d[Math.floor(r() * d.length)]; bs.push(s / d.length); }
  bs.sort((x, y) => x - y);
  return { n: d.length, mean, lo: bs[Math.floor(B * 0.025) - 1], hi: bs[Math.floor(B * 0.975) - 1] };
}
// Paired comparison as tools/online_compare.js: rows of each side averaged per key, B - A per shared key, bootstrap over keys.
function paired(A, Bs, keyOf, f) {
  const avg = rows => { const m = new Map(); for (const r of rows) { const k = keyOf(r); if (!m.has(k)) m.set(k, []); m.get(k).push(f(r)); } const o = new Map(); for (const [k, v] of m) o.set(k, v.reduce((s, x) => s + x, 0) / v.length); return o; };
  const a = avg(A), b = avg(Bs), keys = [...a.keys()].filter(k => b.has(k));
  const d = keys.map(k => b.get(k) - a.get(k));
  return { ...boot(d), keys: keys.length, meanA: keys.reduce((s, k) => s + a.get(k), 0) / Math.max(1, keys.length), meanB: keys.reduce((s, k) => s + b.get(k), 0) / Math.max(1, keys.length) };
}
const sum = (a, f = x => x) => a.reduce((s, x) => s + f(x), 0);
const mean = a => a.length ? sum(a) / a.length : NaN;
const quant = (a, p) => { if (!a.length) return NaN; const b = [...a].sort((x, y) => x - y), i = (b.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return b[lo] + (b[hi] - b[lo]) * (i - lo); };
const median = a => quant(a, 0.5);
const fx = (x, d = 1) => Number.isFinite(x) ? x.toFixed(d) : '–';
const sg = (x, d = 2) => Number.isFinite(x) ? (x >= 0 ? '+' : '−') + Math.abs(x).toFixed(d) : '–';
const ci = (s, d = 2) => `${sg(s.mean, d)} [${sg(s.lo, d)}, ${sg(s.hi, d)}]`;
const pc = (a, b, d = 0) => b ? (100 * a / b).toFixed(d) + '%' : '–';
const table = (head, rows) => ['| ' + head.join(' | ') + ' |', '|' + head.map(() => '---').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');
// flow value at state index r (state before round r; the last element is the state after the final round)
const flowAt = (g, si, m, r) => { const a = g.a.flow[si][m]; return r < a.length ? a[r] : a[a.length - 1]; };
const inProg = (g, r) => g.a.rounds > r || (r === 500 && g.a.rounds === 500);
const mapKey = g => g.map === 'Prisoners Dilemma' ? g.variant : g.map;

module.exports = { ROOT, ELIM, R500, MAPS, OPPS, readJsonl, group, rng, boot, paired, sum, mean, quant, median, fx, sg, ci, pc, table, flowAt, inProg, mapKey };
