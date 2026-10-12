#!/usr/bin/env node
// W7c groundwork: pictures of our trap deaths (no free exit at the last decision) beside our own pieces, at the dying dragon's last turn start.
// '@' its head, '=' its body, 'a' / '-' other ally heads / bodies (digits are their lengths when a head), 'X' / 'x' enemy head / body, '%' pearls.
// usage: node exp/w7/trappic.js <setDir> <map> [--show N]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const [set, map] = process.argv.slice(2); const si = process.argv.indexOf('--show'); const SHOW = si >= 0 ? +process.argv[si + 1] : 4;
let shown = 0; const stats = { traps: 0, allyHeadAdj: 0, allyBodyAdj: 0, prevAllyMovedIn: 0 };
for (const l of fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean)) {
  const r = JSON.parse(l); if (r.map !== map) continue;
  const R = load(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'));
  const snap = new Map();   // id -> picture at its last turn start
  perGame(R, { map: r.map, variant: 'a' }, {
    turn(d, round, ctx) {
      if (d.team !== r.side) return;
      const { W, H, drag, occ, key, pearls } = ctx, h = d.body[0];
      const rows = [];
      for (let dy = -4; dy <= 4; dy++) { let row = '';
        for (let dx = -4; dx <= 4; dx++) {
          const x = (h.x + dx + W) % W, y = (h.y + dy + H) % H, k = key(x, y);
          let c = pearls.has(k) ? '%' : '·';
          if (occ.has(k)) { const o = drag.get(occ.get(k)); const isHead = o && o.body[0].x === x && o.body[0].y === y;
            c = !o ? '?' : o.id === d.id ? (isHead ? '@' : '=') : o.team === d.team ? (isHead ? String(Math.min(9, o.body.length)) : '-') : (isHead ? 'X' : 'x'); }
          row += c; }
        rows.push(row); }
      snap.set(d.id, `r${round} #${d.id} L${d.body.length} free exits ${d.free}\n    ` + rows.join('\n    '));
    },
    death(d, rec, idx, other, round, ctx) {
      if (d.team !== r.side || CAUSE[rec.cause] !== 'trap' || rec.blk !== 'a') return;
      stats.traps++;
      if (shown < SHOW && snap.has(d.id)) { shown++; console.log(`${r.key}: trap death r${round}\n  ` + snap.get(d.id) + '\n'); }
    },
  });
}
console.log(JSON.stringify(stats));
