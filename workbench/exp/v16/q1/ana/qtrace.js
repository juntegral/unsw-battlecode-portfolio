// scratch: our queen's head, length, nearest enemy head and our indicator text per round in a window. usage: qtrace.js <replay> <side> <r0> <r1>
'use strict';
const path = require('path');
const ROOT = '~/01. Project/개인 프로젝트/unsw-swarm';
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const ML = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const [file, us, r0, r1] = process.argv.slice(2);
const R = load(file);
let Q = null; for (const x of R.match.map.initialDragons) if (x.team === us && (Q === null || x.id < Q)) Q = x.id;
const ind = {};
ML.perGame(R, { map: '?', variant: '?', rules: '123' }, {
  indicator(e, r) { if (e.id === Q) ind[r] = e.text; },
  turn(d, r, c) {
    if (d.id !== Q || r < +r0 || r > +r1) return;
    const h = d.body[0]; let ne = null, nd = 99, na = 99;
    for (const o of c.drag.values()) { const t = c.tdist(o.body[0], h); if (o.team !== us && t < nd) { nd = t; ne = o; } if (o.team === us && o.id !== Q) na = Math.min(na, t); }
    console.log(`r${r} queen #${Q} L${d.body.length} head ${h.x},${h.y} | nearest enemy #${ne ? ne.id : '-'} L${ne ? ne.body.length : '-'} d${nd} | nearest ally head d${na} | ${ind[r - 1] || ''}`);
  },
  death(d, r, c, why) { if (d.id === Q) console.log(`r${r} QUEEN DIES ${JSON.stringify(why || '')}`); },
});
