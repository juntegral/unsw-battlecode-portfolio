#!/usr/bin/env node
'use strict';
// compare.js — paired comparison of two local evaluations (tools/eval.js outputs) by key opp:map:side:seed.
// usage: node exp/cand-avoid1/compare.js <baseline label> <candidate label> [--audit-base f.json --audit-cand f.json] [--md]
//   G, win and survival differences with paired 95% intervals (normal approximation, mean +- 1.96 SD/sqrt(n)) and the
//   map-cluster bootstrap that tools/eval.js prints for G. With ram_audit.js outputs for both sides it adds the mechanism
//   metric (rams of our L>=6 dragons per game) and side effects (pearls eaten, deaths of L>=6 by cause, sprint cost).
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const [baseL, candL] = argv.filter((a, i) => !a.startsWith('--') && !(i > 0 && argv[i - 1].startsWith('--')));
const rows = l => { const seen = new Set(); return fs.readFileSync(path.join(ROOT, 'exp', l, 'rows.jsonl'), 'utf8').trim().split('\n').map(x => JSON.parse(x)).filter(r => r.G !== undefined && !seen.has(r.key) && seen.add(r.key)); };
const B = new Map(rows(baseL).map(r => [r.key, r])), C = rows(candL).filter(r => B.has(r.key));
const mean = a => a.reduce((s, x) => s + x, 0) / Math.max(1, a.length);
const sd = a => { const m = mean(a); return Math.sqrt(a.reduce((s, x) => s + (x - m) ** 2, 0) / Math.max(1, a.length - 1)); };
const ci = a => { const m = mean(a), h = 1.96 * sd(a) / Math.sqrt(Math.max(1, a.length)); return [m, m - h, m + h]; };
const f = (x, d = 2) => (x >= 0 ? '+' : '') + x.toFixed(d);
const fci = a => { const [m, lo, hi] = ci(a); return `${f(m)} [${f(lo)}, ${f(hi)}]`; };
function boot(pairs) {
  const maps = [...new Set(pairs.map(p => p.map))].map(m => pairs.filter(p => p.map === m));
  let s = 20260927; const rnd = () => (s = (Math.imul(s, 1103515245) + 12345) >>> 0) / 4294967296; const reps = [];
  for (let k = 0; k < 4000; k++) { const pick = maps.map(() => maps[Math.floor(rnd() * maps.length)]).flat(); reps.push(mean(pick.map(p => p.d))); }
  reps.sort((a, b) => a - b); return [reps[100], reps[3899]];
}
const pairs = C.map(r => { const b = B.get(r.key); return { key: r.key, opp: r.opp, map: r.map, side: r.side, d: r.G - b.G, dw: (+r.won) - (+b.won), da: (+r.alive) - (+b.alive), gb: b.G, gc: r.G, wb: +b.won, wc: +r.won, ab: +b.alive, ac: +r.alive }; });
const out = [];
const grp = (name, P) => [name, P.length, mean(P.map(p => p.gb)).toFixed(2), mean(P.map(p => p.gc)).toFixed(2), fci(P.map(p => p.d)),
  `${P.reduce((s, p) => s + p.wb, 0)}→${P.reduce((s, p) => s + p.wc, 0)}`, fci(P.map(p => p.dw * 100)).replace(/\+?(-?[\d.]+)/g, (m) => m) + ' pp',
  `${P.reduce((s, p) => s + p.ab, 0)}→${P.reduce((s, p) => s + p.ac, 0)}`];
const head = ['범위', '판', 'G 기준', 'G 후보', 'G 차이 [95%]', '승', '승률 차이 [95%]', '생존'];
const table = (h, rs) => ['| ' + h.join(' | ') + ' |', '|' + h.map(() => '---').join('|') + '|', ...rs.map(r => '| ' + r.join(' | ') + ' |')].join('\n');
const bt = boot(pairs);
out.push(`${baseL} → ${candL}: 짝 ${pairs.length}판. 전체 G 차이의 지도 묶음 부트스트랩 95% [${f(bt[0])}, ${f(bt[1])}], 경기별 차이 SD ${sd(pairs.map(p => p.d)).toFixed(1)}.`);
out.push('');
const rs = [grp('전체', pairs)];
for (const o of [...new Set(pairs.map(p => p.opp))]) rs.push(grp(o, pairs.filter(p => p.opp === o)));
for (const s of ['A', 'B']) rs.push(grp('진영 ' + s, pairs.filter(p => p.side === s)));
out.push(table(head, rs));
out.push('');
out.push(table(['지도', '판', 'G 기준', 'G 후보', 'G 차이 [95%]', '승', '승률 차이 [95%]', '생존'], [...new Set(pairs.map(p => p.map))].sort().map(m => grp(m, pairs.filter(p => p.map === m)))));
const ab = opt('--audit-base', null), ac = opt('--audit-cand', null);
if (ab && ac) {
  const gA = new Map(JSON.parse(fs.readFileSync(ab)).games.map(g => [g.key, g])), gC = new Map(JSON.parse(fs.readFileSync(ac)).games.map(g => [g.key, g]));
  const keys = pairs.map(p => p.key).filter(k => gA.has(k) && gC.has(k));
  const per = (k, fn) => keys.filter(x => !k || gA.get(x).opp === k).map(x => fn(gC.get(x)) - fn(gA.get(x)));
  const tot = (k, fn, M) => keys.filter(x => !k || gA.get(x).opp === k).reduce((s, x) => s + (fn(M.get(x)) || 0), 0);
  out.push('');
  out.push('기전과 부작용 (판당, 짝 차이와 95% 구간):');
  const metrics = [
    ['박힌 L≥6 사망', g => g.rammedBig], ['박혀 잃은 L≥6 길이', g => g.rammedBigLen], ['L≥6 노출 결정(실제 도달 범위)', g => g.exposed || 0],
    ['먹은 진주', g => g.eaten.us], ['질주 비용(잃은 칸)', g => g.sprintCost], ['L≥6 사망 전체', g => Object.values(g.bigDeaths).reduce((s, x) => s + x, 0)],
    ['L≥6 사망: 자기 몸(먹이 넘기기 포함)', g => g.bigDeaths.S || 0], ['L≥6 사망: 아군 머리', g => g.bigDeaths['H-ally'] || 0], ['L≥6 사망: 아군 몸', g => g.bigDeaths['O-ally'] || 0],
    ['L≥6 사망: 해초', g => g.bigDeaths.W || 0], ['우리 사망 전체(모든 길이)', g => Object.values(g.ourDeaths).reduce((s, x) => s + x, 0)]];
  const opps = [null, ...new Set(keys.map(k => gA.get(k).opp))];
  const rows2 = [];
  for (const [name, fn] of metrics) rows2.push([name, ...opps.map(o => { const n = keys.filter(x => !o || gA.get(x).opp === o).length; return `${(tot(o, fn, gA) / n).toFixed(2)}→${(tot(o, fn, gC) / n).toFixed(2)} (${fci(per(o, fn))})`; })]);
  out.push(table(['지표', ...opps.map(o => o || '전체')], rows2));
  // by map for the mechanism metric
  const maps = [...new Set(keys.map(k => gA.get(k).map))].sort();
  out.push('');
  out.push('박힌 L≥6 사망, 상대×지도 (기준→후보, 판 수 합):');
  const opps2 = [...new Set(keys.map(k => gA.get(k).opp))];
  out.push(table(['지도', ...opps2], maps.map(m => [m, ...opps2.map(o => { const ks = keys.filter(x => gA.get(x).opp === o && gA.get(x).map === m); return `${ks.reduce((s, x) => s + gA.get(x).rammedBig, 0)}→${ks.reduce((s, x) => s + gC.get(x).rammedBig, 0)}`; })])));
}
console.log(out.join('\n'));
