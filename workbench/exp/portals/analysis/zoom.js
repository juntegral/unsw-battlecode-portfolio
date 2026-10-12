#!/usr/bin/env node
// Zoom on one of our deaths: for each turn of the given dragons in rounds [from, to], the action, the indicator and a local picture.
// usage: node zoom.js <replay> <us A|B> <from> <to> [ids comma] [--radius 5]
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const [file, us, fromS, toS, idsS] = process.argv.slice(2);
const from = +fromS, to = +toS, want = idsS ? new Set(idsS.split(',').map(Number)) : null;
const rad = (() => { const i = process.argv.indexOf('--radius'); return i > 0 ? +process.argv[i + 1] : 5; })();
const R = makeLoader(viewerSource())(file);
const ind = new Map();
const labelOf = new Map(); let nextLabel = 0; const LAB = 'abcdefghijklmnopqrstuvwxyz';
perGame(R, { map: 'Portals' }, {
  indicator(e, round) { ind.set(e.dragonId ?? e.id, e.text); },
  turn(d, round, ctx) {
    if (round < from || round > to || d.team !== us || (want && !want.has(d.id))) return;
    const { W, H, drag, pearls, key } = ctx, h = d.body[0];
    const lines = [];
    for (let dy = -rad; dy <= rad; dy++) {
      let s = '';
      for (let dx = -rad; dx <= rad; dx++) {
        const x = ((h.x + dx) % W + W) % W, y = ((h.y + dy) % H + H) % H, k = key(x, y);
        let c = pearls.has(k) ? (pearls.get(k) === -1 ? 'o' : '%') : '·';
        const o = ctx.occ.get(k);
        if (o !== undefined) { const od = drag.get(o); if (!labelOf.has(o)) labelOf.set(o, LAB[nextLabel++ % 26]); const hd = od.body[0].x === x && od.body[0].y === y; c = od.team !== us ? (hd ? 'X' : 'x') : hd ? labelOf.get(o).toUpperCase() : labelOf.get(o); }
        s += c;
      }
      lines.push(s);
    }
    const near = [...drag.values()].filter(o => o.team === us && ctx.tdist(o.body[0], h) <= rad + 2).map(o => `${labelOf.get(o.id) || '?'}=#${o.id} L${o.body.length}`).join(' ');
    console.log(`r${round} #${d.id} L${d.body.length} head ${h.x},${h.y} | ${near}`);
    console.log(lines.join('\n'));
  },
  action(d, e, round) { if (round >= from && round <= to && d.team === us && (!want || want.has(d.id))) console.log(`  -> #${d.id} ${JSON.stringify(e.action)} | ${ind.get(d.id) || ''}`); },
  death(d, rec, idx, other, round) { if (round >= from && round <= to && d.team === us) console.log(`  DEATH #${d.id} L${rec.len} ${CAUSE[rec.cause]} king ${rec.king} other ${other ? '#' + other.id + ' L' + other.body.length : '-'}`); },
  split(p, ch, e, round) { if (round >= from && round <= to && p.team === us) console.log(`  SPLIT #${p.id} keeps ${p.body.length} child #${ch.id} L${ch.body.length}`); },
});
