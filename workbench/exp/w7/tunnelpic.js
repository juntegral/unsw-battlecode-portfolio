#!/usr/bin/env node
// W15a board pictures with walls: the region around a tile at the start of given rounds (kelp edges drawn, portals '=' / '#'), our dragons
// (head = its length digit, '#' >= 10, body '.'), enemies ('X' / 'x'), pearls ('o' natural, '%' drops). Works on any map file.
// usage: node exp/w7/tunnelpic.js <replay> <map file> <us A|B> <x,y> <rounds comma list> [--r 6]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const [file, mapFile, us, cxy, roundsArg] = process.argv.slice(2);
const ri = process.argv.indexOf('--r'), RAD = ri >= 0 ? +process.argv[ri + 1] : 6;
const [cx, cy] = cxy.split(',').map(Number), SNAP = new Set(roundsArg.split(',').map(Number));
// walls from the map file: N side kind per tile (index r even) and W side (r odd)
const L = fs.readFileSync(mapFile, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
let W = 0, H = 0; const edges = [];
for (const l of L) { const t = l.split(/\s+/); if (t[0] === 'MAP') { W = +t[1]; H = +t[2]; } else if (t[0] === 'EDGE') edges.push([+t[1], +t[2]]); }
const nk = new Uint8Array(W * H), wk = new Uint8Array(W * H);
for (const [i, kind] of edges) { const r = Math.floor(i / (W + 1)), c = i % (W + 1); if (r % 2 === 0) nk[((r / 2) % H) * W + c % W] = kind; else wk[((r - 1) / 2) * W + c % W] = kind; }
const R = makeLoader(viewerSource())(file);
let last = -1;
perGame(R, { map: '?', variant: 'a' }, {
  turn(d, round, ctx) {
    if (!SNAP.has(round) || round === last) return; last = round;
    const { drag, occ, key, pearls } = ctx;
    const out = [`--- r${round} around (${cx},${cy})`];
    for (let dy = -RAD; dy <= RAD; dy++) {
      const y = (cy + dy + H) % H; let top = '', mid = '';
      for (let dx = -RAD; dx <= RAD; dx++) {
        const x = (cx + dx + W) % W, k = y * W + x;
        top += '+' + (nk[k] === 1 ? '--' : nk[k] === 2 ? '==' : '  ');
        let c = ' ';
        if (pearls.has(key(x, y))) c = pearls.get(key(x, y)) === -1 ? 'o' : '%';
        if (occ.has(key(x, y))) { const o = drag.get(occ.get(key(x, y))); const isHead = o && o.body[0].x === x && o.body[0].y === y;
          c = !o ? '?' : o.team === us ? (isHead ? (o.body.length >= 10 ? '#' : String(o.body.length)) : '.') : (isHead ? 'X' : 'x'); }
        if (x === cx && y === cy && c === ' ') c = '*';
        mid += (wk[k] === 1 ? '|' : wk[k] === 2 ? '#' : ' ') + c + ' ';
      }
      out.push(top, mid);
    }
    console.log(out.join('\n'));
  },
});
