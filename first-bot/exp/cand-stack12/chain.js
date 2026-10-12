#!/usr/bin/env node
// cand-stack12: "intake is necessary but not sufficient" - where the px and swarm8 bots lost the mass they ate, next to our stacked bots,
// by the existing studies' own per-game records (no new reconstruction):
//   .cache/intake-gap/online-<set>.jsonl   (exp/intake-gap/extract.js; read through exp/cand-stack12/pfstats.js): natural intake, units, end longest,
//                                          end total length, eliminated (500-round maps, every game)
//   .cache/endgame-king/online-<set>.jsonl (exp/endgame-king/extract.js): the final king's line r300-499 (games that reached r500 on 500-round maps):
//                                          L300, pearls eaten by origin (natural / own sacrifice / own other deaths / enemy deaths), sprint cost,
//                                          split losses (bodies split off the line + the parent left behind when the line moves into a child);
//                                          our team's longest (>= 8) lost to an enemy head from r340 (kd rows: cause 2 rammed / 3 ram, was longest)
// usage: node exp/cand-stack12/chain.js
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const PS = require('./pfstats.js');
const FAM = [
  ['px (px-king-v2, px8, px9d)', ['px-king-v2-online', 'base-px8-online', 'base-px9d-online']],
  ['swarm8', ['cand-swarm8-online']],
  ['merge2 (3 waves)', ['cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3']],
  ['stack5-7 (W5-W8)', ['cand-stack5-online', 'cand-stack6-online', 'cand-stack6-online-r2', 'cand-stack7-online']],
  ['stack8 (W9)', ['cand-stack8-online']],
  ['stack9 (W10)', ['cand-stack9-online']],
  ['stack10 (W11)', ['cand-stack10-online']],
];
const read = (dir, s) => { const f = path.join(ROOT, '.cache', dir, 'online-' + s + '.jsonl'); return fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => JSON.parse(l)) : []; };
const f1 = v => v === null || v === undefined || Number.isNaN(v) ? '–' : (Math.round(v * 10) / 10).toFixed(1);
const pc = (a, b) => b ? Math.round(100 * a / b) + '%' : '–';
const rows = [];
for (const [name, sets] of FAM) {
  // intake-gap: 500-round maps, every game
  const IG = sets.flatMap(s => read('intake-gap', s)).filter(g => g.kind === 'r500');
  const st = IG.map(g => PS.gameStats(g, g.us === 'B' ? 1 : 0)), P = PS.pool(st);
  const nonAut = PS.pool(st.filter(x => x.map !== 'Autarky'));
  // endgame-king: games that reached r500 on 500-round maps with a final king
  const EG = sets.flatMap(s => read('endgame-king', s)).filter(g => g.kind === 'r500');
  const full = EG.filter(g => g.rounds === 500 && g[g.us] && g[g.us].kid >= 0);
  const sum = (gs, f) => gs.reduce((a, g) => a + f(g[g.us]), 0) / Math.max(1, gs.length);
  const binSum = (T, i) => [1, 2, 3, 4].reduce((a, b) => a + (T.dec[b] ? T.dec[b][i] : 0), 0);
  const L300 = sum(full, T => T.Lt && T.Lt[300] !== undefined ? T.Lt[300] : 0);
  const flows = [0, 1, 2, 3, 4, 5, 6].map(i => sum(full, T => binSum(T, i)));
  const kingEnd = sum(full, T => T.king);
  const lost340 = EG.filter(g => g.rounds > 340 && (g[g.us].kd || []).some(q => q[0] >= 340 && q[3] && (q[2] === 2 || q[2] === 3))).length;
  const n340 = EG.filter(g => g.rounds > 340).length;
  const kd300 = EG.filter(g => g.rounds > 300).reduce((a, g) => a + (g[g.us].kd || []).filter(q => q[0] >= 300 && q[3]).length, 0) / Math.max(1, EG.filter(g => g.rounds > 300).length);
  rows.push({ name, n: IG.length, P, nonAut, full: full.length, L300, flows, kingEnd, lost340, n340, kd300 });
}
const L = [];
L.push('## 500-round maps: intake and what happened to the mass (intake-gap cache, every game)', '');
L.push('| family | games | natural intake us / opp | units r100 · r250 | end longest (0 if eliminated) us / opp | end total length | eliminated |', '|---|---:|---|---|---|---:|---:|');
for (const r of rows) L.push(`| ${r.name} | ${r.n} | ${f1(r.P.nat)} / ${f1(r.P.natO)} | ${f1(r.P.units[2])} · ${f1(r.P.units[3])} | ${f1(r.P.kingEnd)} / ${f1(r.P.kingEndO)} | ${f1(r.P.totalEnd)} | ${pc(Math.round(r.P.elim * r.n), r.n)} |`);
L.push('', '## 500-round maps without Autarky (intake-gap cache)', '');
L.push('| family | games | natural intake us / opp | end longest us / opp | end total length |', '|---|---:|---|---|---:|');
for (const r of rows) L.push(`| ${r.name} | ${r.nonAut.n} | ${f1(r.nonAut.nat)} / ${f1(r.nonAut.natO)} | ${f1(r.nonAut.kingEnd)} / ${f1(r.nonAut.kingEndO)} | ${f1(r.nonAut.totalEnd)} |`);
L.push('', '## The final king\'s line r300-499 (endgame-king cache; games that reached r500 on 500-round maps)', '');
L.push('| family | games | L300 | + natural | + own sacrifice | + own other deaths | + enemy deaths | − sprint | − split off | − split path | = end king | games losing the team\'s longest (>= 8) to an enemy head from r340 | longest deaths from r300 per game |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
for (const r of rows) L.push(`| ${r.name} | ${r.full} | ${f1(r.L300)} | ${f1(r.flows[0])} | ${f1(r.flows[1])} | ${f1(r.flows[2])} | ${f1(r.flows[3])} | ${f1(-r.flows[4])} | ${f1(-r.flows[5])} | ${f1(-r.flows[6])} | ${f1(r.kingEnd)} | ${pc(r.lost340, r.n340)} (${r.lost340}/${r.n340}) | ${r.kd300.toFixed(2)} |`);
console.log(L.join('\n'));
