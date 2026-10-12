#!/usr/bin/env node
// confirm.js — key numbers of two report.js outputs side by side (the stratified sample vs all top games).
// usage: node exp/mass-analysis/confirm.js exp/mass-analysis/report-sample1500.json exp/mass-analysis/report-all.json
// Only top-vs-top numbers differ between the two files (the online sets are the same); rows are TW/TL values.
'use strict';
const fs = require('fs');
const [fa, fb] = process.argv.slice(2);
if (!fa || !fb) { console.error('usage: confirm.js <report A .json> <report B .json>'); process.exit(2); }
const A = JSON.parse(fs.readFileSync(fa, 'utf8')), B = JSON.parse(fs.readFileSync(fb, 'utf8'));
const f1 = (x, d = 1) => Number.isFinite(x) ? x.toFixed(d) : '–';
const pc = x => Number.isFinite(x) ? (100 * x).toFixed(0) + '%' : '–';
const rows = [];
const add = (name, get, fmt = f1) => { let a, b; try { a = get(A); } catch { a = NaN; } try { b = get(B); } catch { b = NaN; } rows.push([name, fmt(a), fmt(b)]); };
const T = (o, t) => o.tables[t];
const games = o => o.data.top - o.data.excluded.games;
add('top-vs-top games analysed', games, x => String(x));
for (const g of ['TW', 'TL']) {
  add(`${g} r500 (reached): external inflow`, o => T(o, 'bridge_r500_limit')[g].ext);
  add(`${g} r500 (reached): natural`, o => T(o, 'bridge_r500_limit')[g].nat);
  add(`${g} r500 (reached): net loss trap`, o => T(o, 'bridge_r500_limit')[g].trap);
  add(`${g} r500 (reached): net loss sac`, o => T(o, 'bridge_r500_limit')[g].sac);
  add(`${g} r500 (reached): final total`, o => T(o, 'bridge_r500_limit')[g].final);
  add(`${g} r500 (reached): final king`, o => T(o, 'bridge_r500_limit')[g].king);
  add(`${g} lineage r350: L350`, o => T(o, 'lineage_r500')[g].Lt);
  add(`${g} lineage r350+: own sacrifice`, o => T(o, 'lineage_r500')[g].oSac);
  add(`${g} lineage r350+: natural`, o => T(o, 'lineage_r500')[g].nat);
  add(`${g} lineage: king at r350 is final king`, o => T(o, 'lineage_r500')[g].wasKing350, pc);
  add(`${g} king share r400 (r500 maps)`, o => T(o, 'conv_r500')[g][400].share, pc);
  add(`${g} king share r500 (r500 maps)`, o => T(o, 'conv_r500')[g][500].share, pc);
  add(`${g} sac drops r250+ eaten by own king`, o => T(o, 'convEff_r500')[g].sacKing, pc);
  add(`${g} sac onset (median, r500 reached)`, o => T(o, 'tempo_r500')[g].sacOnset, x => f1(x, 0));
  add(`${g} own-terr. spawns eaten by enemy (r500 maps)`, o => T(o, 'denial_r500')[g].oppShareOurSupply, pc);
  add(`${g} own-terr. spawns eaten by enemy (elim maps)`, o => T(o, 'denial_elim')[g].oppShareOurSupply, pc);
  add(`${g} r450-499 king death length (r500 maps)`, o => T(o, 'phase_flows_r500')[g]['r450–499'].v[14]);
}
const paired = (k, m) => o => T(o, 'pairedWL_' + k)[m];
for (const [k, m] of [['r500', 'finalKing'], ['r500', 'linSac'], ['r500', 'linL350'], ['r500', 'linLeft'], ['r500', 'natInEnemyTerr'], ['r500', 'contactNet'], ['r500', 'kingDeathLen'], ['r500', 'peakTotalR'], ['elim', 'u100']])
  add(`W − L ${k} ${m} [95%]`, paired(k, m), x => x ? `${f1(x.d)} [${f1(x.lo)}, ${f1(x.hi)}]` : '–');
for (const [k, m] of [['elim', 'contact net (game)'], ['r500', 'contact net (game)'], ['elim', 'units r100'], ['elim', 'nat in enemy terr. (game)'], ['r500', 'nat in enemy terr. (game)'], ['r500', 'king r450'], ['r500', 'king lineage sac gain r350+']])
  add(`P(win | ahead) ${k}: ${m}`, o => T(o, 'leadPredicts')[k][m].P, pc);
// contact recapture: share of a trade's pearls eaten by the side that rammed (TW rams, TL rams)
const initShare = (o, g) => { const F = T(o, 'contact_r500')[g].fate.ram; const us = F.ours[3] + F.theirs[5], drops = F.ours[2] + F.theirs[2]; return us / drops; };
add('TW rams: share of the dropped trade pearls eaten by TW (r500 maps)', o => initShare(o, 'TW'), pc);
add('TL rams: share of the dropped trade pearls eaten by TL (r500 maps)', o => initShare(o, 'TL'), pc);
console.log('| metric | ' + fa.split('/').pop() + ' | ' + fb.split('/').pop() + ' |');
console.log('|---|---:|---:|');
for (const r of rows) console.log('| ' + r.join(' | ') + ' |');
