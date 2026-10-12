#!/usr/bin/env node
// W15a: our units, total length and longest every N rounds, plus deaths by cause per window, for one or more replays (side given).
// usage: node exp/w15a/timeline.js <us A|B> <replay>... [--every 25]
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const args = process.argv.slice(2), us = args[0], ei = args.indexOf('--every'), EVERY = ei >= 0 ? +args[ei + 1] : 25;
for (const file of args.slice(1).filter((a, i, all) => !a.startsWith('--') && all[i] !== String(EVERY))) {
  const R = makeLoader(viewerSource())(file);
  const rows = []; let lastR = -1; const deaths = {};
  perGame(R, { map: '?', variant: 'a' }, {
    turn(d, round, ctx) {
      if (round === lastR || round % EVERY) return; lastR = round;
      let n = 0, tot = 0, lo = 0, en = 0, elo = 0;
      for (const o of ctx.drag.values()) { if (o.team === us) { n++; tot += o.body.length; lo = Math.max(lo, o.body.length); } else { en++; elo = Math.max(elo, o.body.length); } }
      rows.push(`r${round}: us ${n} units, total ${tot}, longest ${lo} | them ${en}, longest ${elo}${Object.keys(deaths).length ? ' | our deaths since: ' + Object.entries(deaths).map(([k, v]) => k + ' ' + v).join(', ') : ''}`);
      for (const k in deaths) delete deaths[k];
    },
    death(d, rec) { if (d.team === us) { const c = CAUSE[rec.cause]; deaths[c] = (deaths[c] || 0) + 1; } },
  });
  console.log('== ' + file); for (const r of rows) console.log('  ' + r);
}
