#!/usr/bin/env node
// Every elite value (top winners W, top losers L, our opponents X) that the text of research/observations/endgame-king.md
// quotes, computed in one place so that narrative.py fills them in (tokens ⟪name⟫) and a rerun on a larger population
// cannot leave a stale number in the prose. Population rule as report.js / doc.js.
// usage: node exp/endgame-king/numbers_wl.js [--lineage pass|ml] [--elim-lineage pass|ml] [--only-keys <file>] [--out <json>]
//   --lineage: source of the W/L final-king lineage values on 500-round maps: this study's pass (.cache/endgame-king/top.jsonl)
//     or the mass ledger's full cache (.cache/mass-ledger/top-sample.jsonl, 11:34 KST). --elim-lineage: the same for
//     elimination maps. --only-keys: restrict this study's top games to the keys in <file> (to rebuild the earlier numbers).
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'endgame-king');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const LIN = opt('lineage', 'pass'), ELIN = opt('elim-lineage', LIN), ONLY = opt('only-keys', null), OUT = opt('out', path.join(__dirname, 'numbers-wl.json'));
const only = ONLY ? new Set(fs.readFileSync(path.resolve(ROOT, ONLY), 'utf8').split('\n').map(s => s.trim()).filter(Boolean)) : null;
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const { FI } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
// ---- this study's top pass (W, L) and our online sets' opponents (X)
const pass = [], xs = [], ours = [];
const OURGRP = { 'cand-stack5-online': 'O57', 'cand-stack6-online': 'O57', 'cand-stack6-online-r2': 'O57', 'cand-stack7-online': 'O57',
  'cand-merge2-online': 'M2', 'cand-merge2-online-r2': 'M2', 'cand-merge2-online-r3': 'M2',
  'cand-stack1-online': 'S14', 'cand-stack2-online': 'S14', 'cand-stack3-online': 'S14', 'cand-stack4-online': 'S14' };
let nTopRead = 0, nTopKept = 0, nR500Kept = 0, nElimKept = 0;
for (const f of fs.readdirSync(CACHE).filter(f => f.endsWith('.jsonl'))) {
  const isTop = f.startsWith('top');
  for (const l of fs.readFileSync(path.join(CACHE, f), 'utf8').split('\n')) {
    if (!l.trim()) continue; const g = JSON.parse(l);
    if (isTop) {
      if (only && !only.has(g.key)) continue;
      nTopRead++;
      if (!g.winner) continue;
      if (['A', 'B'].some(t => g[t].splits <= 3 && g[t].sonar === 0) || g.A.faults + g.B.faults >= 3) continue;
      nTopKept++; if (g.kind === 'r500') nR500Kept++; else nElimKept++;
      for (const t of ['A', 'B']) pass.push({ grp: t === g.winner ? 'W' : 'L', g, t });
    } else if (g.set && g.us) {
      xs.push({ grp: 'X', g, t: g.us === 'A' ? 'B' : 'A' });
      const og = OURGRP[g.set]; if (og) ours.push({ grp: og, g, t: g.us });
    }
  }
}
// ---- mass ledger full cache in the same per-team shape (lineage only)
let ml = null, nMl = 0, nMlKept = 0;
function loadMl() {
  ml = [];
  for (const l of fs.readFileSync(path.join(ROOT, '.cache', 'mass-ledger', 'top-sample.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue; let g; try { g = JSON.parse(l); } catch { continue; } nMl++; // a line being appended right now is skipped
    if (!g.winner) continue;
    const faults = t => g[t].fl[FI.dn_fault].reduce((a, b) => a + b, 0);
    if (['A', 'B'].some(t => g[t].splits <= 3 && g[t].sonar === 0) || faults('A') + faults('B') >= 3) continue;
    nMlKept++;
    for (const t of ['A', 'B']) {
      const lin = g[t].lin; if (!lin) continue;
      const after = tt => { const c = lin.cp[tt]; if (!c) return null; const e = c.eat; return [e[0], e[1], e[2] + e[3] + e[4] + e[5], e[6] + e[7] + e[8] + e[9] + e[10], c.cost, c.lossOff, c.lossPath]; };
      const a = [300, 350, 400, 450].map(after);
      const dec = [new Array(7).fill(0)];
      for (let i = 0; i < 4; i++) dec.push(a[i] ? a[i].map((v, k) => v - (i < 3 && a[i + 1] ? a[i + 1][k] : 0)) : new Array(7).fill(0));
      const Lt = {}; for (const tt of [300, 350, 400, 450]) if (lin.cp[tt]) Lt[tt] = lin.cp[tt].Lt;
      const lr = {}; for (const tt of [300, 350, 400, 450]) if (lin.cp[tt]) lr[tt] = [0, lin.cp[tt].Lt, lin.cp[tt].wasKing ? lin.cp[tt].Lt : -1, 0];
      ml.push({ grp: t === g.winner ? 'W' : 'L', t, g: { kind: g.kind, rounds: g.rounds, map: g.map, winner: g.winner, [t]: { king: lin.len, kid: 1, Lt, dec, st: { king: g[t].st.king.slice(30) }, lr } } });
    }
  }
}
if (LIN === 'ml' || ELIN === 'ml') loadMl();
const linTeams = kind => (kind === 'r500' ? LIN : ELIN) === 'ml' ? ml : pass;
// ---- helpers
const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN;
const median = a => { if (!a.length) return NaN; const b = a.slice().sort((x, y) => x - y); return b[Math.floor(b.length / 2)]; };
const R = x => x.g[x.t];
const full = x => x.g.kind === 'r500' && x.g.rounds === 500 && R(x).kid >= 0 && R(x).Lt[300] !== undefined;
const S = (x, i, bins = [1, 2, 3, 4]) => bins.reduce((s, b) => s + R(x).dec[b][i], 0);
const N = {}; // name -> number (the text formats them)
const put = (k, v) => { N[k] = v; };
const grpOf = (arr, g) => arr.filter(x => x.grp === g);
// ---- lineage, 500-round maps (T1, T1b, T1c, T2, T2b, line = longest)
for (const g of ['W', 'L']) {
  const T = grpOf(linTeams('r500'), g).filter(full);
  const m = f => mean(T.map(f));
  put(g + '_lin_n', T.length);
  put(g + '_L300', m(x => R(x).Lt[300])); put(g + '_fin', m(x => R(x).king));
  put(g + '_nat', m(x => S(x, 0))); put(g + '_sac', m(x => S(x, 1))); put(g + '_oth', m(x => S(x, 2))); put(g + '_en', m(x => S(x, 3)));
  put(g + '_spr', -m(x => S(x, 4))); put(g + '_split', -m(x => S(x, 5) + S(x, 6)));
  for (let b = 1; b <= 4; b++) { put(g + '_nat_b' + b, m(x => R(x).dec[b][0])); put(g + '_sac_b' + b, m(x => R(x).dec[b][1])); }
  put(g + '_top300', m(x => R(x).st.king[0]));
  const L = t => m(x => t === 500 ? R(x).king : R(x).Lt[t]);
  for (const t of [300, 350, 400, 450]) put(g + '_g' + t, (L(t + 50) - L(t)) / 50);
  put(g + '_g', (L(500) - L(300)) / 200);
  for (const [a, b, k] of [[0, 10, 'c10'], [11, 20, 'c20'], [21, 30, 'c30'], [31, 999, 'c31']]) { const U = T.filter(x => R(x).Lt[300] >= a && R(x).Lt[300] <= b); put(g + '_g_' + k, mean(U.map(x => (R(x).king - R(x).Lt[300]) / 200))); put(g + '_n_' + k, U.length); }
  for (const t of [300, 350, 400, 450]) { const U = T.filter(x => R(x).lr && R(x).lr[t]); put(g + '_longest' + t, 100 * U.filter(x => R(x).lr[t][1] === R(x).lr[t][2]).length / U.length); }
  // per map (W only in the text)
  const pm = {}; for (const mp of R500) { const U = T.filter(x => x.g.map === mp); pm[mp] = { sac: mean(U.map(x => S(x, 1))), fin: mean(U.map(x => R(x).king)), nat: mean(U.map(x => S(x, 0))), n: U.length }; }
  put(g + '_map_sac_min', Math.min(...R500.map(mp => pm[mp].sac))); put(g + '_map_sac_max', Math.max(...R500.map(mp => pm[mp].sac)));
  for (const mp of R500) { const k = mp.replace(/\s/g, ''); put(g + '_fin_' + k, pm[mp].fin); put(g + '_nat_' + k, pm[mp].nat); }
}
put('lin_src', LIN === 'ml' ? 0 : 1);
// lineage of our opponents (X) and of our groups (fixed populations; used for differences in the text)
for (const [g, arr] of [['X', xs], ['O57', ours.filter(x => x.grp === 'O57')], ['M2', ours.filter(x => x.grp === 'M2')], ['S14', ours.filter(x => x.grp === 'S14')]]) {
  const T = arr.filter(full); const m = f => mean(T.map(f));
  put(g + '_lin_n', T.length); put(g + '_L300', m(x => R(x).Lt[300])); put(g + '_fin', m(x => R(x).king));
  put(g + '_nat', m(x => S(x, 0))); put(g + '_sac', m(x => S(x, 1))); put(g + '_oth', m(x => S(x, 2))); put(g + '_split', -m(x => S(x, 5) + S(x, 6)));
  for (let b = 1; b <= 4; b++) put(g + '_sac_b' + b, m(x => R(x).dec[b][1]));
  for (const mp of R500) { const U = T.filter(x => x.g.map === mp); put(g + '_sac_' + mp.replace(/\s/g, ''), mean(U.map(x => S(x, 1)))); }
}
// derived: winners - losers, ours (stack5-7) - winners, per-bin ranges, per-map ratio
put('WL_dL300', N.W_L300 - N.L_L300); put('WL_dsac', N.W_sac - N.L_sac); put('WL_dsplitloss', (-N.W_split) - (-N.L_split)); put('WL_dnat', N.W_nat - N.L_nat); put('WL_dfin', N.W_fin - N.L_fin);
for (const k of ['L300', 'nat', 'sac', 'oth', 'split', 'fin']) put('OW_d' + k, N['O57_' + k] - N['W_' + k]);
for (const g of ['W', 'L']) { const nb = [1, 2, 3, 4].map(b => N[g + '_nat_b' + b]); put(g + '_nat_bmin', Math.min(...nb)); put(g + '_nat_bmax', Math.max(...nb)); }
{ const r = R500.map(mp => N['O57_sac_' + mp.replace(/\s/g, '')] / N['W_sac_' + mp.replace(/\s/g, '')] * 100); put('OW_mapratio_min', Math.min(...r)); put('OW_mapratio_max', Math.max(...r)); }
for (const mp of R500) { const k = mp.replace(/\s/g, ''); const U = grpOf(linTeams('r500'), 'W').filter(full).filter(x => x.g.map === mp); put('W_sac_' + k, mean(U.map(x => S(x, 1)))); }
{ const r = R500.map(mp => N['O57_sac_' + mp.replace(/\s/g, '')] / N['W_sac_' + mp.replace(/\s/g, '')] * 100); put('OW_mapratio_min', Math.min(...r)); put('OW_mapratio_max', Math.max(...r)); }
put('WM_dfin_min', Math.min(N.W_fin - N.M2_fin, N.W_fin - N.S14_fin)); put('WM_dfin_max', Math.max(N.W_fin - N.M2_fin, N.W_fin - N.S14_fin));
{ const c = ['c10', 'c20', 'c30', 'c31'].map(k => N['W_g_' + k]).filter(Number.isFinite); put('W_gc_min', Math.min(...c)); put('W_gc_max', Math.max(...c)); }
// ---- lineage, elimination maps (T1e, T1f)
for (const g of ['W', 'L']) {
  for (const end of ['r500', 'elim']) {
    const T = grpOf(linTeams('elim'), g).filter(x => x.g.kind === 'elim' && x.g.rounds > 300 && R(x).kid >= 0 && R(x).Lt[300] !== undefined && (end === 'r500' ? x.g.rounds === 500 : x.g.rounds < 500));
    const m = f => mean(T.map(f));
    const p = g + '_e' + (end === 'r500' ? '5' : 'x');
    put(p + '_n', T.length); put(p + '_L300', m(x => R(x).Lt[300])); put(p + '_fin', m(x => R(x).king));
    put(p + '_nat', m(x => S(x, 0))); put(p + '_sac', m(x => S(x, 1))); put(p + '_cost', -m(x => S(x, 4) + S(x, 5) + S(x, 6)));
    if (end === 'r500') { for (let b = 1; b <= 4; b++) put(p + '_sac_b' + b, m(x => R(x).dec[b][1])); const sb = [1, 2, 3, 4].map(b => N[p + '_sac_b' + b]); put(p + '_sac_bmin', Math.min(...sb)); put(p + '_sac_bmax', Math.max(...sb)); }
  }
}
// ---- this study's new metrics (pass only): W, L; X from our sets
const groups = { W: grpOf(pass, 'W'), L: grpOf(pass, 'L'), X: xs };
for (const [g, all] of Object.entries(groups)) {
  const A = all.filter(x => x.g.kind === 'r500'), T = all.filter(full);
  put(g + '_n_full', T.length); put(g + '_n_r500', A.length);
  // T3c: non-king dragons by distance
  const a = new Array(60).fill(0); for (const x of A) for (let i = 0; i < 60; i++) a[i] += R(x).nk[i];
  let tot = 0; for (let i = 0; i < 12; i++) tot += a[i * 5];
  const cls = [0, 1, 2, 3].map(c => { let t = 0, n = 0; for (let p = 0; p < 3; p++) { t += a[(p * 4 + c) * 5]; n += a[(p * 4 + c) * 5 + 1]; } return { share: 100 * t / tot, nat: n / t }; });
  put(g + '_nk_le3', cls[0].share); put(g + '_nk_4_8', cls[1].share); put(g + '_nk_9_16', cls[2].share); put(g + '_nk_17', cls[3].share);
  put(g + '_nk_nat_min', Math.min(...cls.map(c => c.nat))); put(g + '_nk_nat_max', Math.max(...cls.map(c => c.nat)));
  let pv = 0, ap = 0; for (let i = 0; i < 12; i++) { pv += a[i * 5 + 3]; ap += a[i * 5 + 4]; } put(g + '_approach', 100 * ap / pv);
  // T3d: r340 cohort
  const C = []; for (const x of T) for (const q of R(x).coh) C.push(q);
  const s = i => C.reduce((u, q) => u + q[i], 0);
  put(g + '_coh_pg', C.length / T.length); put(g + '_coh_L0', s(1) / C.length); put(g + '_coh_far', 100 * C.filter(q => q[2] > 16).length / C.length);
  [0, 1, 2, 3, 4].forEach(k => put(g + '_coh_end' + k, 100 * C.filter(q => q[3] === k).length / C.length));
  put(g + '_coh_toline', s(4) / T.length); put(g + '_coh_toline_per', s(4) / C.length);
  put(g + '_coh_enB', 100 * s(20) / s(17)); put(g + '_coh_enA', 100 * s(10) / s(7)); put(g + '_coh_selfB', 100 * s(18) / s(17)); put(g + '_coh_selfA', 100 * s(8) / s(7));
  // T4: sacrifices by distance to the line
  const d = [0, 1, 2, 3].map(dc => { const v = new Array(11).fill(0); for (const x of T) for (const [k, w] of Object.entries(R(x).sac)) if (+k.split('|')[1] === dc) for (let i = 0; i < 11; i++) v[i] += w[i]; return v; });
  d.forEach((v, i) => { put(`${g}_sac_d${i}_pg`, v[0] / T.length); put(`${g}_sac_d${i}_line`, 100 * v[3] / v[2]); put(`${g}_sac_d${i}_offlonger`, 100 * v[4] / v[2]); put(`${g}_sac_d${i}_famalive`, 100 * v[9] / (v[4] + v[5])); put(`${g}_sac_d${i}_famline`, 100 * v[10] / (v[4] + v[5])); });
  put(g + '_sac_came', 100 * d[0][8] / d[0][0]);
  put(g + '_sac_far_pg', (d[2][0] + d[3][0]) / T.length);
  for (const [k, i] of [['line', 3], ['offlonger', 4]]) { const v = [2, 3].map(c => 100 * d[c][i] / d[c][2]); put(`${g}_far_${k}_min`, Math.min(...v)); put(`${g}_far_${k}_max`, Math.max(...v)); }
  { const v = [2, 3].map(c => 100 * d[c][9] / (d[c][4] + d[c][5])); put(g + '_far_famalive_min', Math.min(...v)); put(g + '_far_famalive_max', Math.max(...v)); }
  { const v = [2, 3].map(c => 100 * d[c][10] / (d[c][4] + d[c][5])); put(g + '_far_famline_min', Math.min(...v)); put(g + '_far_famline_max', Math.max(...v)); }
  put(g + '_sac_pg', d.reduce((u, v) => u + v[0], 0) / T.length);
  { let dd = 0, l = 0; for (const x of T) for (const v of Object.values(R(x).sac)) { dd += v[2]; l += v[3]; } put(g + '_sac_toline', 100 * l / dd); }
  // T4b
  const lb = [0, 1, 2, 3].map(b => [0, 1, 2, 3, 4].map(i => T.reduce((u, x) => u + R(x).lineSac[b][i], 0)));
  put(g + '_ls_near_min', Math.min(...lb.map(v => 100 * v[1] / v[0]))); put(g + '_ls_near_max', Math.max(...lb.map(v => 100 * v[1] / v[0])));
  put(g + '_ls_big_b1', 100 * lb[0][4] / lb[0][0]); put(g + '_ls_big_b4', 100 * lb[3][4] / lb[3][0]);
  // T4c (pass lineage)
  for (const t of [300, 350, 400, 450]) { const U = T.filter(x => R(x).lr && R(x).lr[t]); put(`${g}_plongest${t}`, 100 * U.filter(x => R(x).lr[t][1] === R(x).lr[t][2]).length / U.length); }
  put(g + '_first', median(T.map(x => R(x).lr && R(x).lr[450] ? R(x).lr[450][3] : 0).filter(v => v > 0)));
  const coh = T.filter(x => R(x).coh.some(q => q[3] === 0)), kng = T.filter(x => !R(x).coh.some(q => q[3] === 0)), CC = coh.map(x => R(x).coh.find(q => q[3] === 0));
  put(g + '_fromcoh', 100 * coh.length / T.length); put(g + '_fromcoh_L', mean(CC.map(q => q[1]))); put(g + '_fromcoh_rank', median(CC.map(q => q[16]))); put(g + '_fromcoh_dK', median(CC.map(q => q[2])));
  put(g + '_fin_coh', mean(coh.map(x => R(x).king))); put(g + '_fin_kng', mean(kng.map(x => R(x).king)));
  // T5: exposure (line member, L >= 8)
  for (const [lab, bins] of [['a', [0, 1]], ['b', [2, 3]]]) { const e = new Array(9).fill(0); for (const x of T) for (const b of bins) for (let i = 0; i < 9; i++) e[i] += R(x).env[b][i]; put(`${g}_exp6_${lab}`, 100 * e[2] / e[0]); put(`${g}_exp3_${lab}`, 100 * e[1] / e[0]); put(`${g}_p5_${lab}`, e[4] / e[0]); put(`${g}_own_${lab}`, 100 * e[5] / e[0]); }
  for (const mp of R500) { const U = T.filter(x => x.g.map === mp); let n = 0, k = 0; for (const x of U) for (let b = 0; b < 4; b++) { n += R(x).env[b][0]; k += R(x).env[b][2]; } put(g + '_expmap_' + mp.replace(/\s/g, ''), 100 * k / n); }
  // T5c: exposure classes (Portals out)
  const ex = x => { const e = R(x).env; const n = e[0][0] + e[1][0] + e[2][0]; return n ? (e[0][2] + e[1][2] + e[2][2]) / n : null; };
  const cl = [[0, 0.1], [0.1, 0.3], [0.3, 0.6], [0.6, 1.01]].map(([p, q]) => { const U = T.filter(x => x.g.map !== 'Portals' && ex(x) !== null && ex(x) >= p && ex(x) < q); return { n: U.length, sac: mean(U.map(x => S(x, 1))), g: mean(U.map(x => (R(x).king - R(x).Lt[300]) / 200)) }; });
  put(g + '_hx_sac', cl[3].sac); put(g + '_hx_g', cl[3].g); put(g + '_hx_n', cl[3].n);
  put(g + '_lx_sac_min', Math.min(...cl.slice(0, 3).map(c => c.sac))); put(g + '_lx_sac_max', Math.max(...cl.slice(0, 3).map(c => c.sac)));
  put(g + '_lx_g_min', Math.min(...cl.slice(0, 3).map(c => c.g))); put(g + '_lx_g_max', Math.max(...cl.slice(0, 3).map(c => c.g)));
  put(g + '_allx_g_min', Math.min(...cl.map(c => c.g))); put(g + '_allx_g_max', Math.max(...cl.map(c => c.g)));
  // T5d: L >= 8 deaths per bin
  for (const [lo, hi, k] of [[300, 350, 'b1'], [350, 400, 'b2'], [400, 450, 'b3'], [450, 500, 'b4']]) {
    const U = A.filter(x => x.g.rounds > lo); const K = []; for (const x of U) for (const q of R(x).kd) if (q[0] >= lo && q[0] < hi) K.push(q);
    const c = f => K.filter(f).length / U.length;
    put(`${g}_kd_en_${k}`, c(q => q[2] === 2 || q[2] === 3)); put(`${g}_kd_ally_${k}`, c(q => q[2] === 5)); put(`${g}_kd_sac_${k}`, c(q => q[2] === 0));
  }
  // king (team longest) lost to an enemy / ally head from r340
  const F = all.filter(x => x.g.kind === 'r500' && x.g.rounds === 500 && R(x).kid >= 0);
  put(g + '_kloss_en', 100 * F.filter(x => R(x).kd.some(q => q[0] >= 340 && q[3] && (q[2] === 2 || q[2] === 3))).length / F.length);
  put(g + '_kloss_ally', 100 * F.filter(x => R(x).kd.some(q => q[0] >= 340 && q[3] && q[2] === 5)).length / F.length);
  { const L = []; for (const x of F) for (const q of R(x).kd) if (q[0] >= 340 && q[3] && (q[2] === 2 || q[2] === 3)) L.push(q[1]); put(g + '_kloss_len', mean(L)); }
  // per-map cohort: last family death by an enemy head (Schooltime, Slithery Fight)
  for (const mp of ['Schooltime', 'Slithery Fight']) { const U = all.filter(x => x.g.map === mp && x.g.rounds === 500); const CC2 = []; for (const x of U) for (const q of R(x).coh) CC2.push(q); put(g + '_cohenemy_' + mp.replace(/\s/g, ''), 100 * CC2.filter(q => (q[3] === 3 || q[3] === 4) && (q[21] === 2 || q[21] === 3)).length / CC2.length); }
}
put('n_top_read', nTopRead); put('n_top_kept', nTopKept); put('n_r500_kept', nR500Kept); put('n_elim_kept', nElimKept); put('n_ml', nMl); put('n_ml_kept', nMlKept);
fs.writeFileSync(path.resolve(ROOT, OUT), JSON.stringify({ lineage: LIN, elimLineage: ELIN, onlyKeys: ONLY, at: new Date().toISOString(), N }, null, 1));
console.log(`wrote ${path.relative(ROOT, path.resolve(ROOT, OUT))}: ${Object.keys(N).length} values; top read ${nTopRead}, kept ${nTopKept} (r500 ${nR500Kept}, elim ${nElimKept}); lineage ${LIN}/${ELIN}`);
