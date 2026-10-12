#!/usr/bin/env node
// Draw the Portals map from a replay: kelp walls, portal edges (letters), spawn gaps, territory (movement distance from each team's
// starting bodies) and the static 2-core. usage: node mapdraw.js <replay>
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const R = makeLoader(viewerSource())(process.argv[2]);
const M = R.match.map, W = M.width, H = M.height;
console.log(Object.keys(M));
console.log('portals', JSON.stringify(M.portals).slice(0, 600));
const wy = y => ((y % H) + H) % H, wx = x => ((x % W) + W) % W;
const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
// portal edge labels
const pl = new Map(); let c = 0; const letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
for (const pr of M.portals || []) { const ch = letters[c++ % letters.length]; for (const e of pr) pl.set(e.x + ',' + e.y + ',' + e.side, ch); }
// big grid: each tile = 3 chars wide, 2 rows (edge row, tile row)
const out = [];
for (let y = 0; y < H; y++) {
  let top = '', mid = '';
  for (let x = 0; x < W; x++) {
    const pN = pl.get(x + ',' + y + ',N') || pl.get(x + ',' + wy(y - 1) + ',S');
    top += '+' + (pN ? pN + pN : hk(x, y) ? '--' : '  ');
    const pW = pl.get(x + ',' + y + ',W') || pl.get(wx(x - 1) + ',' + y + ',E');
    mid += (pW ? pW : vk(x, y) ? '|' : ' ') + '  ';
  }
  out.push(top); out.push(mid);
}
console.log(out.join('\n'));
