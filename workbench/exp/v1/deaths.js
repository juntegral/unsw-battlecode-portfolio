// our deaths by cause and length class, and a label sample, from one replay (mass ledger dt keys: cause|lenClass|phase|king|near|kdist|mech|blk)
const ML = require('../../tools/mass_ledger.js');
const { makeLoader, viewerSource } = require('../../tools/top_features.js');
const load = makeLoader(viewerSource());
const [file, us, mapName, r0, r1] = process.argv.slice(2);
const R = load(file);
const g = ML.perGame(R, { map: mapName });
const agg = {};
for (const [k, v] of Object.entries(g[us].dt)) { const [cause, lc, phase] = k.split('|'); const key = cause + ' ' + phase; agg[key] = (agg[key] || 0) + v[0]; }
console.log(Object.entries(agg).sort((a, b) => b[1] - a[1]).map(([k, n]) => k + ':' + n).join('  '));
const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
let round = -1, shown = 0;
for (const e of R.events) {
  if (e.type === 'roundStart') round = e.round;
  else if (e.type === 'dragonSplit') team.set(e.childId, e.team);
  else if (e.type === 'dragonIndicator' && team.get(e.id) === us && round >= +r0 && round <= +r1 && shown < 60) { console.log(round, '#' + e.id, e.text); shown++; }
}
