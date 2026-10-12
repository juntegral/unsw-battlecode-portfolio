#!/usr/bin/env node
// v1.4: one game's timeline for our team: every 5 rounds up to --to, our heads by frontier bin (exp/spatial/lib.js geometry) and our deaths in
// the window by cause (mass ledger), with the dead dragon's length and bin
// usage: node exp/v14/timeline.js <game dir> <our side A|B> [to]
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const { geometry } = require(path.join(ROOT, 'exp', 'spatial', 'lib.js'));
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const [dir, us, to = 100] = process.argv.slice(2);
const fs = require('fs');
const file = path.join(dir, fs.readdirSync(dir).find(f => f.endsWith('.replay')));
const R = makeLoader(viewerSource())(file), M = R.match.map, W = M.width;
const g = geometry(M, 'x', '?'), bin = g.bin[us];
let last = -1; const rows = []; let cur = null;
ML.perGame(R, { map: M.mapName }, {
  turn(d, round, ctx) {
    if (round === last || round > +to) return;
    last = round;
    if (round % 5 === 0) {
      const h = [0, 0, 0, 0, 0, 0], L = [];
      for (const o of ctx.drag.values()) if (o.team === us) { const b = bin[o.body[0].y * W + o.body[0].x]; h[b === undefined ? 5 : b]++; L.push(o.body.length); }
      cur = { r: round, h, L: L.sort((a, b) => b - a), deaths: [] }; rows.push(cur);
    }
  },
  death(d, rec, idx, other, round) {
    if (d.team !== us || round > +to || !cur) return;
    cur.deaths.push(`${ML.CAUSE[rec.cause]}:L${d.body.length}@b${bin[d.body[0].y * W + d.body[0].x]}`);
  },
});
for (const x of rows) console.log(`r${x.r}\tbins ${x.h.slice(0, 5).join('/')}\tlens ${x.L.join(',')}\t${x.deaths.join(' ')}`);
console.log(JSON.stringify(R.result));
