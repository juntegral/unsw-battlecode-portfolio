#!/usr/bin/env node
// v1.6: an ASCII view of a local game's board around a tile at the start of a round (tools/mass_ledger.js perGame state).
//   our dragons: the head is the id's last digit... every segment of ours shows 'a'..'z' by dragon (legend below, head in capitals); enemies 'x' (head 'X');
//   pearls '*'; kelp edges are not drawn (tiles only). usage: node exp/v16/board.js <game.replay> <side> <round> <x> <y> [radius 8] [map name] [variant]
//   (map name and variant as tools/mass_ledger.js knows them; default Slithery Fight a)
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const raw = require(path.join(ROOT, 'legacy', 'exp', 'intake-gap', 'rawload.js'));
const [file, us, RR, X, Y, RAD, MAP, VAR] = process.argv.slice(2); const rr = +RR, cx = +X, cy = +Y, rad = +(RAD || 8);
const R = raw.load(file);
let done = false;
ML.perGame(R, { map: MAP || 'Slithery Fight', variant: VAR || 'a' }, {
  turn(d, r, c) {
    if (done || r !== rr) return; done = true;
    const W = c.W, H = c.H, grid = new Map(), legend = [];
    const inWin = s => { const dx = Math.min(((s.x - cx) % W + W) % W, ((cx - s.x) % W + W) % W), dy = Math.min(((s.y - cy) % H + H) % H, ((cy - s.y) % H + H) % H); return dx <= rad && dy <= rad; };
    let li = 0;
    for (const o of c.drag.values()) {
      if (!o.body.some(inWin)) continue;   // letters only for the dragons in the window (fewer collisions)
      let ch;
      if (o.team === us) { ch = String.fromCharCode(97 + (li % 26)); legend.push(`${ch}=#${o.id} L${o.body.length}`); li++; } else ch = 'x';
      o.body.forEach((s, i) => grid.set(s.y * W + s.x, i === 0 ? ch.toUpperCase() : ch));
    }
    for (const k of c.pearls.keys()) if (!grid.has(k)) grid.set(k, '*');
    const rows = [];
    for (let dy = -rad; dy <= rad; dy++) {
      const y = ((cy + dy) % H + H) % H; let s = String(y).padStart(3) + ' ';
      for (let dx = -rad; dx <= rad; dx++) { const x = ((cx + dx) % W + W) % W; s += grid.get(y * W + x) || '.'; }
      rows.push(s);
    }
    console.log(`round ${rr} around ${cx},${cy} (x ${((cx - rad) % W + W) % W}..)`);
    console.log(rows.join('\n'));
    console.log(legend.filter(l => rows.join('').includes(l[0]) || rows.join('').includes(l[0].toUpperCase())).join('  '));
  },
});
