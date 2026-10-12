#!/usr/bin/env node
// exp/portals v2: where our half's natural pearls are eaten and at what cost. Per game, for our team: natural eats by tile class
// (open water, U-room = a 2 x 2 pass-through room, pocket = a one-tile dead end, corridor = the fountain column outside the 2-core) and by
// eater (king class = our longest >= 8 at that moment; big non-king >= 8; mid 4-7; piece 2-3); our deaths and splits by the class of the
// head's tile and the dragon's length. usage: node harvest.js <evalOutDir> [--seeds a-b]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const PTM = JSON.parse(fs.readFileSync(path.join(__dirname, '../gen/ptmap.json'), 'utf8'));
const argv = process.argv.slice(2), dir = path.resolve(argv[0]);
const si = argv.indexOf('--seeds'); const [s0, s1] = si >= 0 ? argv[si + 1].split('-').map(Number) : [1, 999];
const W = PTM.W;
// tile class: 0 open, 1 U-room (a 2 x 2 compartment), 2 pocket (a one-tile compartment), 3 corridor (outside the 2-core, main area)
const cls = t => PTM.compSize[t] === 1 ? 2 : !PTM.core[t] ? 3 : PTM.room[t] ? 1 : 0;   // pocket = a one-tile compartment; corridor = outside the 2-core in the main area
const CL = ['open', 'Uroom', 'pocket', 'corridor'];
const lc = (L, king) => king ? 'king' : L >= 8 ? 'big' : L >= 4 ? 'mid' : 'piece';
const tot = { games: 0, eat: {}, death: {}, split: {}, deathLen: {}, rounds: {} };
const add = (o, k, v = 1) => { o[k] = (o[k] || 0) + v; };
for (const l of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n')) {
  const r = JSON.parse(l); if (r.map !== 'portals' || r.G === undefined || r.seed < s0 || r.seed > s1) continue;
  const f = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
  const us = r.side; tot.games++;
  const R = load(f);
  const kingOf = ctx => { let k = null; for (const d of ctx.drag.values()) if (d.team === us && (!k || d.body.length > k.body.length || (d.body.length === k.body.length && d.id < k.id))) k = d; return k; };
  perGame(R, { map: 'Portals' }, {
    eat(d, tile, o, round, ctx) {
      if (d.team !== us || o !== -1) return;          // natural pearls only
      const k = kingOf(ctx), isK = k === d && d.body.length >= 8;
      add(tot.eat, CL[cls(tile)] + '|' + lc(d.body.length, isK) + '|' + (round < 300 ? 'r<300' : 'r300+'));
    },
    split(p, ch, e, round, ctx) {
      if (p.team !== us) return;
      const h = p.body[0], t = h.y * W + h.x;
      add(tot.split, CL[cls(t)] + '|' + (ch.body.length > p.body.length ? 'handoff' : 'child') + '|' + (round < 300 ? 'r<300' : 'r300+'));
    },
    death(d, rec, idx, other, round, ctx) {
      if (d.team !== us) return;
      const h = d.body[0], t = h.y * W + h.x;
      add(tot.death, CL[cls(t)] + '|' + CAUSE[rec.cause] + '|' + (rec.king ? 'king' : lc(rec.len, false)) + '|' + (round < 300 ? 'r<300' : 'r300+'));
      add(tot.deathLen, CL[cls(t)] + '|' + (round < 300 ? 'r<300' : 'r300+'), rec.len);
    },
  });
}
const G = tot.games, show = (title, o) => { console.log(`\n## ${title} (per game, ${G} games)`); for (const [k, v] of Object.entries(o).sort((a, b) => b[1] - a[1])) if (v / G >= 0.05) console.log(`${k.padEnd(40)} ${(v / G).toFixed(2)}`); };
show('natural eats: tile class | eater | phase', tot.eat);
const byCls = {}; for (const [k, v] of Object.entries(tot.eat)) add(byCls, k.split('|')[0], v); show('natural eats by tile class', byCls);
const byEater = {}; for (const [k, v] of Object.entries(tot.eat)) add(byEater, k.split('|')[0] + '|' + k.split('|')[1], v); show('natural eats by tile class and eater', byEater);
show('splits: tile class of the parent head | handoff/child | phase', tot.split);
show('deaths: tile class | cause | who | phase', tot.death);
show('death length: tile class | phase', tot.deathLen);
