#!/usr/bin/env node
// Which elite values of research/observations/endgame-king.md moved when the top pass went from the partial population
// (numbers-wl-old.json: 4,257 500-round games of the 21:10 snapshot for the new metrics, the 11:34 mass-ledger cache for the
// lineage) to the full one (numbers-wl.json). A value "moved" when |new - old| > 1 point, where a point is 1 percentage point
// for shares, 1 pearl / 1 segment for lengths and pearl counts, 0.01 for growth per round and deaths per game, 0.1 for per-turn
// pearl rates. Only the values the text quotes are listed (the ⟪name⟫ tokens of narrative.py).
// usage: node exp/endgame-king/diff_numbers.js [--old numbers-wl-old.json] [--new numbers-wl.json] [--md out.md] [--json out.json]
'use strict';
const fs = require('fs'), path = require('path');
const argv = process.argv.slice(2), opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const O = JSON.parse(fs.readFileSync(path.resolve(__dirname, opt('old', 'numbers-wl-old.json')), 'utf8')).N;
const Nn = JSON.parse(fs.readFileSync(path.resolve(__dirname, opt('new', 'numbers-wl.json')), 'utf8')).N;
const text = fs.readFileSync(path.join(__dirname, 'narrative.py'), 'utf8');
const used = new Set([...text.matchAll(/⟪(\w+)\|/g)].map(m => m[1]));
// unit classes
const RATE = /(_g(300|350|400|450)?$|_g_c\d+$|_gc_(min|max)$|_hx_g$|_lx_g_(min|max)$|_allx_g_(min|max)$)/;
const PERGAME = /_kd_/;
const COUNT = /(_n$|_lin_n$|_n_c\d+$|_n_full$|_n_r500$|^n_)/;
const PERTURN = /(_nk_nat_|_p5_)/;
const SHARE = /(_exp6_|_exp3_|_expmap_|_kloss_en$|_kloss_ally$|_coh_en[AB]$|_coh_self[AB]$|_coh_end\d$|_coh_far$|_line$|_offlonger$|_famalive$|_famline$|_far_(line|offlonger|famalive|famline)_(min|max)$|_came$|_sac_toline$|longest\d+$|_fromcoh$|_nk_(le3|4_8|9_16|17)$|_approach$|_own_|_cohenemy_|_ls_near_|_ls_big_|_mapratio_)/;
const unitOf = k => RATE.test(k) ? ['0.01', 0.01] : PERGAME.test(k) ? ['0.1/판', 0.1] : PERTURN.test(k) ? ['0.1', 0.1] : SHARE.test(k) ? ['%p', 1] : ['1', 1];
const rows = [];
for (const k of [...used].sort()) {
  if (!(k in O) || !(k in Nn) || !Number.isFinite(O[k]) || !Number.isFinite(Nn[k]) || COUNT.test(k)) continue; // sizes change by construction
  const [u, th] = unitOf(k), d = Nn[k] - O[k];
  if (Math.abs(d) > th + 1e-9) rows.push({ k, old: O[k], neu: Nn[k], d, u });
}
const f = (v, u) => u === '%p' ? v.toFixed(0) : (u === '0.01' || u === '0.1/판') ? v.toFixed(2) : v.toFixed(1);
const md = ['| 값 | 앞(부분 추출·장부 캐시) | 뒤(전체 추출) | 차 | 단위 |', '|---|---:|---:|---:|---|', ...rows.map(r => `| \`${r.k}\` | ${f(r.old, r.u)} | ${f(r.neu, r.u)} | ${(r.d >= 0 ? '+' : '−') + f(Math.abs(r.d), r.u)} | ${r.u} |`)].join('\n');
console.log(`values quoted in the text: ${used.size}; compared ${[...used].filter(k => k in O && k in Nn).length}; moved beyond 1 point: ${rows.length}`);
console.log(md);
if (opt('md', null)) fs.writeFileSync(path.resolve(opt('md')), md + '\n');
if (opt('json', null)) fs.writeFileSync(path.resolve(opt('json')), JSON.stringify(rows, null, 1));
