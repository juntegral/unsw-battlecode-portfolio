#!/usr/bin/env node
'use strict';
// window0.js — can a dragon tell layout a from b from its own 7x7 window? From the map files only (no games).
//  1. Start: for every map file of the spawn table (exp/proxy4-tools/genspawndb.js) and every starting dragon, the table
//     maps of the same size that still fit the round-0 window's kelp/portal edges and spawn flags (pearlIn >= 0), and
//     for each surviving wrong map the chance that the round-0 countdowns (g0 - 1, g0 ~ U[min, max]) all fit it too.
//  2. Anywhere: per two-layout map, the share of head positions whose window has no tile that spawns in only one of
//     a and b (such a window needs the countdowns or more moves; split children can be born there).
// usage (repository root): node exp/proxy4-tools/window0.js
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
function parse(file) {
  const L = fs.readFileSync(file, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  let W = 0, H = 0; const tiles = [], edges = [], dragons = [];
  for (const l of L) {
    const t = l.split(/\s+/);
    if (t[0] === 'MAP') { W = +t[1]; H = +t[2]; }
    else if (t[0] === 'TILE') tiles.push([+t[1], +t[2], +t[3], +t[4]]);
    else if (t[0] === 'EDGE') edges.push([+t[1], +t[2]]);
    else if (t[0] === 'DRAGON') dragons.push([+t[3], +t[4]]); // head
  }
  const N = W * H, hk = new Uint8Array(N), vk = new Uint8Array(N), lo = new Int32Array(N), hi = new Int32Array(N);
  for (const [i, kind] of edges) {
    const r = Math.floor(i / (W + 1)), c = i % (W + 1);
    if (r % 2 === 0) hk[((r / 2) % H) * W + (c % W)] = kind; else vk[((r - 1) / 2) * W + (c % W)] = kind;
  }
  for (const [x, y, mn, mx] of tiles) { lo[y * W + x] = mn; hi[y * W + x] = mx; }
  return { name: path.basename(file, '.map'), W, H, hk, vk, lo, hi, dragons };
}
const A = f => path.join(ROOT, 'maps', 'online-20260927', f + '.map'), V = f => path.join(ROOT, 'maps', 'variants', f + '.map');
const table = [...fs.readdirSync(path.join(ROOT, 'maps', 'online-20260927')).filter(f => f.endsWith('.map')).sort().map(f => A(f.replace('.map', ''))),
  V('prisoners_dilemma_10'), V('devil_b'), V('queen_of_spades_b'), V('schooltime_b'), V('slithery_fight_b')].map(parse);
const win = (m, hx, hy) => { const w = []; for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) w.push(((hy + dy + m.H) % m.H) * m.W + ((hx + dx + m.W) % m.W)); return w; };
const pFit = (lo, hi, lo2, hi2) => { const a = Math.max(lo, lo2), b = Math.min(hi, hi2); return b < a ? 0 : (b - a + 1) / (hi - lo + 1); };
console.log('## 1. 시작 드래곤의 0라운드 창');
console.log('| 지도 파일 | 시작 드래곤 | 가장자리·생성 여부로 가려짐 | 못 가린 드래곤 (남은 후보: 카운트다운이 그 후보에도 맞을 확률) |');
console.log('|---|---:|---:|---|');
for (const m of table) {
  const same = table.filter(o => o.W === m.W && o.H === m.H), amb = [];
  for (const [hx, hy] of m.dragons) {
    const w = win(m, hx, hy);
    const left = same.filter(o => o !== m && w.every(t => o.hk[t] === m.hk[t] && o.vk[t] === m.vk[t] && (o.hi[t] > 0) === (m.hi[t] > 0)));
    if (!left.length) continue;
    amb.push(`(${hx},${hy}): ` + left.map(o => { let p = 1; for (const t of w) if (m.hi[t] > 0 && o.hi[t] > 0 && (m.lo[t] !== o.lo[t] || m.hi[t] !== o.hi[t])) p *= pFit(m.lo[t], m.hi[t], o.lo[t], o.hi[t]); return `${o.name} ${p.toFixed(2)}`; }).join(', '));
  }
  console.log(`| ${m.name} | ${m.dragons.length} | ${m.dragons.length - amb.length} | ${amb.join('; ') || '-'} |`);
}
console.log('\n## 2. 모든 머리 위치');
console.log('| 지도 | 칸 | 한 판본에서만 생성하는 칸 | 간격만 다른 칸 | 생성 여부로 못 가리는 창 | 간격으로도 못 가리는 창 |');
console.log('|---|---:|---:|---:|---:|---:|');
for (const [a, b] of [['devil', 'devil_b'], ['queen_of_spades', 'queen_of_spades_b'], ['schooltime', 'schooltime_b'], ['slithery_fight', 'slithery_fight_b'], ['prisoners_dilemma', 'prisoners_dilemma_10']]) {
  const P = table.find(m => m.name === a), Q = table.find(m => m.name === b), N = P.W * P.H;
  const flag = t => (P.hi[t] > 0) !== (Q.hi[t] > 0), range = t => !flag(t) && P.hi[t] > 0 && (P.lo[t] !== Q.lo[t] || P.hi[t] !== Q.hi[t]);
  let nf = 0, nr = 0, wf = 0, wr = 0;
  for (let t = 0; t < N; t++) { if (flag(t)) nf++; if (range(t)) nr++; }
  for (let y = 0; y < P.H; y++) for (let x = 0; x < P.W; x++) { const w = win(P, x, y); const f = w.some(flag), r = w.some(range); if (!f) wf++; if (!f && !r) wr++; }
  console.log(`| ${a} / ${b} | ${N} | ${nf} | ${nr} | ${wf} (${(100 * wf / N).toFixed(1)}%) | ${wr} (${(100 * wr / N).toFixed(1)}%) |`);
}
