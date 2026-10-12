// Shared helpers for the decision dataset (tools/decisions.js output): streaming reader with game context and
// groups, weighted tables, a small CART decision tree, and formatting. Used by tools/decisions_learn.js.
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib');

const ROOT = path.resolve(__dirname, '..');
const DEC = path.join(ROOT, 'data', 'decisions');
const ELIM_MAPS = new Set(['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default']);
const EXCLUDE_TEAMS = new Set(['SSS']); // broken bot in 19 snapshot games (research/observations/top-timing.md)

function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  return fs.readFileSync(file, 'utf8').split('\n').filter(l => l.trim()).map(l => JSON.parse(l));
}

// Every game of a set with its rows as arrays of strings; header -> column index map `C`.
function* gamesOf(set) {
  const dir = path.join(DEC, set);
  for (const g of readJsonl(path.join(dir, 'games.jsonl'))) {
    const f = path.join(dir, g.out);
    if (!fs.existsSync(f)) continue;
    const lines = zlib.gunzipSync(fs.readFileSync(f)).toString().split('\n');
    const head = lines[0].split('\t'), C = Object.fromEntries(head.map((k, i) => [k, i]));
    const rows = [];
    for (let i = 1; i < lines.length; i++) if (lines[i]) rows.push(lines[i].split('\t'));
    yield { g, C, rows };
  }
}

// Weighted counter keyed by strings: add(key, w, values{}) keeps weight, raw count and weighted sums of values.
class Acc {
  constructor() { this.m = new Map(); }
  add(key, w, vals) {
    let e = this.m.get(key);
    if (!e) { e = { w: 0, n: 0, s: {} }; this.m.set(key, e); }
    e.w += w; e.n++;
    if (vals) for (const k in vals) { const v = vals[k]; if (v === null || v === undefined || Number.isNaN(v)) continue; e.s[k] = (e.s[k] || 0) + w * v; e.s[k + '#'] = (e.s[k + '#'] || 0) + w; }
  }
  get(key) { return this.m.get(key) || { w: 0, n: 0, s: {} }; }
  mean(key, v) { const e = this.get(key); const d = e.s[v + '#'] || 0; return d ? e.s[v] / d : NaN; }
  toJSON() { return Object.fromEntries(this.m); }
}

// ---------------------------------------------------------------------------------------------------------------
// CART classification tree with weights. X: array of number arrays, y: labels 0..K-1, w: weights.
// opts: maxDepth, minLeafW (weighted), minLeafN (raw), minGain (relative Gini decrease).
function fitTree(X, y, w, K, names, opts = {}) {
  const maxDepth = opts.maxDepth || 4, minLeafW = opts.minLeafW || 300, minLeafN = opts.minLeafN || 100, minGain = opts.minGain || 0.002;
  const nf = names.length;
  const gini = (cnt, tot) => { if (tot <= 0) return 0; let s = 0; for (let k = 0; k < K; k++) { const p = cnt[k] / tot; s += p * p; } return 1 - s; };
  let nextId = 0;
  function build(idx, depth) {
    const cnt = new Array(K).fill(0); let tot = 0;
    for (const i of idx) { cnt[y[i]] += w[i]; tot += w[i]; }
    const node = { id: nextId++, n: idx.length, w: tot, cnt, depth };
    if (depth >= maxDepth || idx.length < 2 * minLeafN) return node;
    const g0 = gini(cnt, tot);
    let best = null;
    for (let f = 0; f < nf; f++) {
      // per distinct value: class weights and raw counts
      const byV = new Map();
      for (const i of idx) {
        const v = X[i][f];
        let e = byV.get(v); if (!e) { e = { c: new Array(K).fill(0), n: 0, w: 0 }; byV.set(v, e); }
        e.c[y[i]] += w[i]; e.n++; e.w += w[i];
      }
      if (byV.size < 2) continue;
      const vals = [...byV.keys()].sort((a, b) => a - b);
      const lc = new Array(K).fill(0); let lw = 0, ln = 0;
      for (let j = 0; j < vals.length - 1; j++) {
        const e = byV.get(vals[j]);
        for (let k = 0; k < K; k++) lc[k] += e.c[k];
        lw += e.w; ln += e.n;
        const rw = tot - lw, rn = idx.length - ln;
        if (lw < minLeafW || rw < minLeafW || ln < minLeafN || rn < minLeafN) continue;
        const rc = cnt.map((c, k) => c - lc[k]);
        const g = (lw * gini(lc, lw) + rw * gini(rc, rw)) / tot;
        const gain = g0 - g;
        if (!best || gain > best.gain) best = { f, t: (vals[j] + vals[j + 1]) / 2, lo: vals[j], hi: vals[j + 1], gain };
      }
    }
    if (!best || best.gain < minGain * Math.max(g0, 1e-9)) return node;
    const L = [], R = [];
    for (const i of idx) (X[i][best.f] <= best.t ? L : R).push(i);
    node.split = { f: best.f, name: names[best.f], t: best.t, lo: best.lo, hi: best.hi, gain: best.gain };
    node.left = build(L, depth + 1); node.right = build(R, depth + 1);
    return node;
  }
  const idx = []; for (let i = 0; i < X.length; i++) idx.push(i);
  const root = build(idx, 0);
  return { root, K, names };
}
function leafOf(tree, x) { let n = tree.root; while (n.split) n = x[n.split.f] <= n.split.t ? n.left : n.right; return n; }
function leaves(tree) {
  const out = [];
  (function walk(n, conds) {
    if (!n.split) { out.push({ node: n, conds }); return; }
    const s = n.split;
    walk(n.left, conds.concat([{ name: s.name, op: '<=', v: s.lo }]));
    walk(n.right, conds.concat([{ name: s.name, op: '>=', v: s.hi }]));
  })(tree.root, []);
  // merge repeated conditions on the same feature into ranges
  for (const l of out) {
    const r = new Map();
    for (const c of l.conds) { const e = r.get(c.name) || { lo: -Infinity, hi: Infinity }; if (c.op === '<=') e.hi = Math.min(e.hi, c.v); else e.lo = Math.max(e.lo, c.v); r.set(c.name, e); }
    l.ranges = r;
    l.text = [...r.entries()].map(([k, e]) => e.lo === -Infinity ? `${k}≤${e.hi}` : e.hi === Infinity ? `${k}≥${e.lo}` : e.lo === e.hi ? `${k}=${e.lo}` : `${k} ${e.lo}–${e.hi}`).join(', ') || '(전체)';
  }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------
// formatting
const pct = (a, b, d = 1) => b > 0 ? (100 * a / b).toFixed(d) + '%' : '–';
const fx = (v, d = 2) => Number.isFinite(v) ? v.toFixed(d) : '–';
const fint = v => Number.isFinite(v) ? Math.round(v).toLocaleString('en-US') : '–';
function mdTable(head, rows, align) {
  const a = align || head.map((_, i) => i === 0 ? '---' : '---:');
  return ['| ' + head.join(' | ') + ' |', '|' + a.map(x => x).join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');
}
// Wilson 95% interval for a weighted proportion using the raw count as the sample size
function wilson(p, n) {
  if (!(n > 0)) return [NaN, NaN];
  const z = 1.96, d = 1 + z * z / n, c = p + z * z / (2 * n), s = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n));
  return [(c - s) / d, (c + s) / d];
}

module.exports = { ROOT, DEC, ELIM_MAPS, EXCLUDE_TEAMS, readJsonl, gamesOf, Acc, fitTree, leafOf, leaves, pct, fx, fint, mdTable, wilson };
