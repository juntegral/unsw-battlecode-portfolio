#!/usr/bin/env node
// The top winner / loser values that the observation text quotes from this study's own extraction (T3c, T3d, T4, T4b, T4c,
// T5, T5b, T5c, T5d and the per-map cohort table), printed in one place for the closing check of the text.
// usage: node exp/endgame-king/wl_sheet.js
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'endgame-king');
const teams = [];
for (const l of fs.readFileSync(path.join(CACHE, 'top.jsonl'), 'utf8').split('\n')) {
  if (!l.trim()) continue; const g = JSON.parse(l); if (!g.winner) continue;
  if (['A', 'B'].some(t => g[t].splits <= 3 && g[t].sonar === 0) || g.A.faults + g.B.faults >= 3) continue;
  for (const t of ['A', 'B']) teams.push({ grp: t === g.winner ? 'W' : 'L', g, t });
}
const pct = (a, b) => b ? (100 * a / b).toFixed(0) + '%' : '–', f1 = x => x.toFixed(1), f2 = x => x.toFixed(2);
const full = x => x.g.kind === 'r500' && x.g.rounds === 500 && x.g[x.t].kid >= 0 && x.g[x.t].Lt[300] !== undefined;
for (const grp of ['W', 'L']) {
  const T = teams.filter(x => x.grp === grp && full(x)), A = teams.filter(x => x.grp === grp && x.g.kind === 'r500');
  const o = [`${grp}: full ${T.length}, r500 all ${A.length}`];
  // T3c
  const a = new Array(60).fill(0); for (const x of A) for (let i = 0; i < 60; i++) a[i] += x.g[x.t].nk[i];
  let tot = 0; for (let i = 0; i < 12; i++) tot += a[i * 5];
  const c = []; for (let k = 0; k < 4; k++) { let t = 0, n = 0; for (let p = 0; p < 3; p++) { t += a[(p * 4 + k) * 5]; n += a[(p * 4 + k) * 5 + 1]; } c.push(`${pct(t, tot)}·${f2(n / t)}`); }
  let pv = 0, ap = 0; for (let i = 0; i < 12; i++) { pv += a[i * 5 + 3]; ap += a[i * 5 + 4]; }
  o.push(`T3c nonking dist ≤3/4–8/9–16/17+: ${c.join(' ')} approach ${pct(ap, pv)}`);
  // T3d
  const C = []; for (const x of T) for (const q of x.g[x.t].coh) C.push(q); const s = i => C.reduce((u, q) => u + q[i], 0);
  o.push(`T3d cohort/game ${f1(C.length / T.length)} L0 ${f1(s(1) / C.length)} far ${pct(C.filter(q => q[2] > 16).length, C.length)} ends ${[0, 1, 2, 3, 4].map(k => pct(C.filter(q => q[3] === k).length, C.length)).join('/')} toLine/game ${f1(s(4) / T.length)} enemy ${pct(s(20), s(17))}→${pct(s(10), s(7))} self ${pct(s(18), s(17))}→${pct(s(8), s(7))}`);
  // T4
  const r4 = []; let tn = 0;
  for (const dc of [0, 1, 2, 3]) { const v = new Array(11).fill(0); for (const x of T) for (const [k, w] of Object.entries(x.g[x.t].sac)) if (+k.split('|')[1] === dc) for (let i = 0; i < 11; i++) v[i] += w[i]; tn += v[0];
    r4.push(`d${dc}: ${f1(v[0] / T.length)}/g line ${pct(v[3], v[2])} offLonger ${pct(v[4], v[2])} came ${pct(v[8], v[0])} fam ${pct(v[9], v[4] + v[5])}/${pct(v[10], v[4] + v[5])}`); }
  o.push('T4 ' + r4.join(' | ') + ` total ${f1(tn / T.length)}/g`);
  { let d = 0, l = 0; for (const x of T) for (const v of Object.values(x.g[x.t].sac)) { d += v[2]; l += v[3]; } o.push(`sac pearls to line (all r300+ sacrifices) ${pct(l, d)}`); }
  // T4b
  o.push('T4b ' + [0, 1, 2, 3].map(b => { const v = [0, 1, 2, 3, 4].map(i => T.reduce((u, x) => u + x.g[x.t].lineSac[b][i], 0)); return `${f1(v[0] / T.length)}·${pct(v[1], v[0])}·${pct(v[2], v[0])}·${pct(v[4], v[0])}`; }).join(' '));
  // T4c
  const lr = [300, 350, 400, 450].map(t => { const U = T.filter(x => x.g[x.t].lr && x.g[x.t].lr[t]); return pct(U.filter(x => x.g[x.t].lr[t][1] === x.g[x.t].lr[t][2]).length, U.length); });
  const first = T.map(x => x.g[x.t].lr && x.g[x.t].lr[450] ? x.g[x.t].lr[450][3] : 0).filter(v => v > 0).sort((p, q) => p - q);
  const coh = T.filter(x => x.g[x.t].coh.some(q => q[3] === 0)), kng = T.filter(x => !x.g[x.t].coh.some(q => q[3] === 0)), CC = coh.map(x => x.g[x.t].coh.find(q => q[3] === 0));
  const med = arr => { const b = arr.slice().sort((p, q) => p - q); return b[Math.floor(b.length / 2)]; };
  o.push(`T4c lineLongest ${lr.join('/')} first ${first[Math.floor(first.length / 2)]} fromCohort ${pct(coh.length, T.length)} L ${f1(CC.reduce((u, q) => u + q[1], 0) / CC.length)} rank ${med(CC.map(q => q[16]))} dK ${med(CC.map(q => q[2]))} final ${f1(coh.reduce((u, x) => u + x.g[x.t].king, 0) / coh.length)}/${f1(kng.reduce((u, x) => u + x.g[x.t].king, 0) / kng.length)}`);
  // T5
  for (const [lab, bins] of [['r300–399', [0, 1]], ['r400–499', [2, 3]]]) { const e = new Array(9).fill(0); for (const x of T) for (const b of bins) for (let i = 0; i < 9; i++) e[i] += x.g[x.t].env[b][i]; o.push(`T5 ${lab}: ≤3 ${pct(e[1], e[0])} ≤6 ${pct(e[2], e[0])} eD ${f1(e[3] / e[0])} p5 ${f2(e[4] / e[0])} own ${pct(e[5], e[0])} e6 ${f2(e[7] / e[0])} a6 ${f2(e[8] / e[0])}`); }
  // T5b
  o.push('T5b ' + ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'].map(m => { const U = T.filter(x => x.g.map === m); let n = 0, k = 0; for (const x of U) for (let b = 0; b < 4; b++) { n += x.g[x.t].env[b][0]; k += x.g[x.t].env[b][2]; } return `${m} ${pct(k, n)}`; }).join(', '));
  // T5c
  const ex = x => { const e = x.g[x.t].env; const n = e[0][0] + e[1][0] + e[2][0]; return n ? (e[0][2] + e[1][2] + e[2][2]) / n : null; };
  const S = (x, i) => [1, 2, 3, 4].reduce((u, b) => u + x.g[x.t].dec[b][i], 0);
  o.push('T5c ' + [[0, 0.1], [0.1, 0.3], [0.3, 0.6], [0.6, 1.01]].map(([p, q]) => { const U = T.filter(x => x.g.map !== 'Portals' && ex(x) !== null && ex(x) >= p && ex(x) < q); return `${p}-${q}: n${U.length} sac ${f1(U.reduce((u, x) => u + S(x, 1), 0) / U.length)} nat ${f1(U.reduce((u, x) => u + S(x, 0), 0) / U.length)} g ${f2(U.reduce((u, x) => u + (x.g[x.t].king - x.g[x.t].Lt[300]) / 200, 0) / U.length)}`; }).join(' | '));
  // T5d
  o.push('T5d ' + [[300, 350], [350, 400], [400, 450], [450, 500]].map(([lo, hi]) => { const U = A.filter(x => x.g.rounds > lo); const K = []; for (const x of U) for (const k of x.g[x.t].kd) if (k[0] >= lo && k[0] < hi) K.push(k); const cc = f => (K.filter(f).length / U.length).toFixed(2); return `r${lo}: enemy ${cc(k => k[2] === 2 || k[2] === 3)} ally ${cc(k => k[2] === 5)} trap ${cc(k => k[2] === 1)} sac ${cc(k => k[2] === 0)}`; }).join(' | '));
  // per-map cohort enemy-head deaths
  o.push('cohort enemy-head deaths ' + ['Schooltime', 'Slithery Fight'].map(m => { const U = teams.filter(x => x.grp === grp && x.g.map === m && x.g.rounds === 500); const CC2 = []; for (const x of U) for (const q of x.g[x.t].coh) CC2.push(q); return `${m} ${pct(CC2.filter(q => (q[3] === 3 || q[3] === 4) && (q[21] === 2 || q[21] === 3)).length, CC2.length)}`; }).join(', '));
  console.log(o.join('\n  ') + '\n');
}
