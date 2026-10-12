#!/usr/bin/env node
// Paired comparison of two eval.js labels (same keys = opponent:map:side:seed).
// usage: node exp/cand-swarm1/pair.js <candidate label> <baseline label> [--json <file>] [--md]
// Prints mean differences of G (our longest at the end, 0 if eliminated), win and survival with two 95% intervals:
//   t: paired normal interval (mean +- 1.96 sd/sqrt(n));  boot: map-cluster bootstrap (maps resampled, 4000 draws,
//   the same generator and seed as tools/eval.js).
// Groups: all, map type (elim = devil, trophy, prisoners_dilemma, queen_of_spades, default; r500 = the other five),
// each opponent, each map.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ELIM = ['devil', 'trophy', 'prisoners_dilemma', 'queen_of_spades', 'default'];
const [cand, base] = process.argv.slice(2).filter(a => !a.startsWith('--'));
const jsonOut = process.argv.includes('--json') ? process.argv[process.argv.indexOf('--json') + 1] : null;
const md = process.argv.includes('--md');
function rows(label) {
  const f = path.join(ROOT, 'exp', label, 'rows.jsonl');
  const seen = new Map();
  for (const l of fs.readFileSync(f, 'utf8').split('\n')) { if (!l.trim()) continue; let r; try { r = JSON.parse(l); } catch { continue; } if (r.G === undefined || seen.has(r.key)) continue; seen.set(r.key, r); }
  return seen;
}
const C = rows(cand), B = rows(base);
const pairs = [];
for (const [k, c] of C) { const b = B.get(k); if (!b) continue; pairs.push({ key: k, opp: c.opp, map: c.map, type: ELIM.includes(c.map) ? 'elim' : 'r500', c, b, dG: c.G - b.G, dW: (+c.won) - (+b.won), dA: (+c.alive) - (+b.alive) }); }
const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN;
const sd = a => { const m = mean(a); return Math.sqrt(a.reduce((s, x) => s + (x - m) ** 2, 0) / Math.max(1, a.length - 1)); };
function boot(ps, f) {
  const maps = [...new Set(ps.map(p => p.map))]; const byMap = maps.map(m => ps.filter(p => p.map === m));
  if (byMap.length < 2) return [NaN, NaN];
  let s = 20260927; const rnd = () => (s = (Math.imul(s, 1103515245) + 12345) >>> 0) / 4294967296; const reps = [];
  for (let i = 0; i < 4000; i++) { const pick = byMap.map(() => byMap[Math.floor(rnd() * byMap.length)]).flat(); reps.push(mean(pick.map(f))); }
  reps.sort((a, b) => a - b); return [reps[100], reps[3899]];
}
function stat(ps, f) { const d = ps.map(f), m = mean(d), se = sd(d) / Math.sqrt(d.length); return { n: d.length, mean: m, t: [m - 1.96 * se, m + 1.96 * se], boot: boot(ps, f) }; }
function group(ps) {
  return {
    n: ps.length,
    base: { G: mean(ps.map(p => p.b.G)), win: mean(ps.map(p => +p.b.won)), alive: mean(ps.map(p => +p.b.alive)), wins: ps.filter(p => p.b.won).length, alives: ps.filter(p => p.b.alive).length },
    cand: { G: mean(ps.map(p => p.c.G)), win: mean(ps.map(p => +p.c.won)), alive: mean(ps.map(p => +p.c.alive)), wins: ps.filter(p => p.c.won).length, alives: ps.filter(p => p.c.alive).length },
    dG: stat(ps, p => p.dG), dW: stat(ps, p => p.dW), dA: stat(ps, p => p.dA),
  };
}
const out = { cand, base, pairs: pairs.length, all: group(pairs), type: {}, opp: {}, map: {} };
for (const t of ['elim', 'r500']) out.type[t] = group(pairs.filter(p => p.type === t));
for (const o of [...new Set(pairs.map(p => p.opp))].sort()) out.opp[o] = group(pairs.filter(p => p.opp === o));
for (const m of [...new Set(pairs.map(p => p.map))].sort()) out.map[m] = group(pairs.filter(p => p.map === m));
const f2 = x => Number.isNaN(x) ? '-' : (x >= 0 ? '+' : '') + x.toFixed(2);
const ci = s => `[${f2(s.t[0])}, ${f2(s.t[1])}]` + (Number.isNaN(s.boot[0]) ? '' : ` b[${f2(s.boot[0])}, ${f2(s.boot[1])}]`);
const line = (name, g) => `| ${name} | ${g.n} | ${g.base.G.toFixed(2)} → ${g.cand.G.toFixed(2)} | ${f2(g.dG.mean)} ${ci(g.dG)} | ${g.base.wins} → ${g.cand.wins} | ${f2(100 * g.dW.mean)}%p [${f2(100 * g.dW.t[0])}, ${f2(100 * g.dW.t[1])}] | ${g.base.alives} → ${g.cand.alives} | ${f2(100 * g.dA.mean)}%p [${f2(100 * g.dA.t[0])}, ${f2(100 * g.dA.t[1])}] |`;
console.log(`${cand} vs ${base}: ${pairs.length} pairs`);
console.log('| group | n | G base → cand | dG [t 95%] b[map bootstrap] | wins | d win [t 95%] | alive | d alive [t 95%] |');
console.log('|---|---:|---|---|---|---|---|---|');
console.log(line('all', out.all));
for (const t of ['elim', 'r500']) console.log(line(t === 'elim' ? 'elim maps' : '500-round maps', out.type[t]));
for (const o of Object.keys(out.opp)) console.log(line(o, out.opp[o]));
if (md || true) for (const m of Object.keys(out.map)) console.log(line(m, out.map[m]));
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(out, null, 1));
