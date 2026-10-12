#!/usr/bin/env node
// Full-board pictures of one of our Portals games at chosen rounds (turn start of the round's first dragon).
// Legend: K / = our king's head / body; digits (length, # for >= 10) / . our other heads / bodies; o natural pearl; % death drop;
// , a room tile (ptmap ROOM: a walled compartment of <= 8 tiles, or outside the 2-core); blank open water. The other half is blank.
// usage: node pics.js <replay> <us A|B> <r1,r2,...>
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const PTM = JSON.parse(fs.readFileSync(path.join(__dirname, '../gen/ptmap.json'), 'utf8'));
const [file, us, rs] = process.argv.slice(2);
const want = new Set(rs.split(',').map(Number)); let last = -1;
const R = makeLoader(viewerSource())(file);
perGame(R, { map: 'Portals' }, {
  turn(d, round, ctx) {
    if (!want.has(round) || round === last) return; last = round;
    const { W, H, drag, pearls } = ctx;
    let king = null; for (const o of drag.values()) if (o.team === us && (!king || o.body.length > king.body.length)) king = o;
    const g = Array.from({ length: H }, (_, y) => Array.from({ length: W }, (_, x) => PTM.room[y * W + x] ? ',' : ' '));
    for (const [k, v] of pearls) { const x = k % W, y = (k / W) | 0; g[y][x] = v === -1 ? 'o' : '%'; }
    const L = [];
    for (const o of drag.values()) {
      if (o.team !== us) continue;
      for (let i = 1; i < o.body.length; i++) { const s = o.body[i]; g[s.y][s.x] = o === king ? '/' : '.'; }
      const h = o.body[0]; g[h.y][h.x] = o === king ? 'K' : o.body.length >= 10 ? '#' : String(o.body.length); L.push(o.body.length);
    }
    L.sort((a, b) => b - a);
    console.log(`r${round}: ours ${L.length} dragons [${L.join(' ')}] total ${L.reduce((a, b) => a + b, 0)}`);
    console.log('+' + '-'.repeat(W) + '+\n' + g.map(r => '|' + r.join('') + '|').join('\n') + '\n+' + '-'.repeat(W) + '+');
  },
});
