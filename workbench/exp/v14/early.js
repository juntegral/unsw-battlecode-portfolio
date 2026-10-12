#!/usr/bin/env node
// v1.4: early-game detail over sets: our deaths in r0-50 by cause and frontier bin, our heads by bin at r15..r50, our pearls eaten by r50
// usage: node exp/v14/early.js <map file name e.g. devil> <set dir>[,<set dir>...] [more sets as name=dir,dir]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const { geometry } = require(path.join(ROOT, 'exp', 'spatial', 'lib.js'));
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const [mapName, ...setArgs] = process.argv.slice(2);
const CPR = [15, 20, 25, 30, 35, 40, 50];
for (const sa of setArgs) {
  const [name, dirs] = sa.split('=');
  const agg = { games: 0, deaths: {}, bins: {}, len50: 0, units50: 0 };
  for (const dir of dirs.split(',')) {
    const rowsF = path.join(dir, 'rows.jsonl'); if (!fs.existsSync(rowsF)) continue;
    for (const row of fs.readFileSync(rowsF, 'utf8').trim().split('\n').map(l => JSON.parse(l))) {
      if (row.map !== mapName || row.G === undefined) continue;
      const f = path.join(dir, 'games', row.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
      const R = load(f), M = R.match.map, W = M.width, us = row.side;
      const g = geometry(M, 'x', '?'), bin = g.bin[us];
      let last = -1; agg.games++;
      ML.perGame(R, { map: M.mapName }, {
        turn(d, round, ctx) {
          if (round === last) return; last = round;
          if (CPR.includes(round)) { const h = agg.bins[round] = agg.bins[round] || [0, 0, 0, 0, 0, 0]; for (const o of ctx.drag.values()) if (o.team === us) { const b = bin[o.body[0].y * W + o.body[0].x]; h[b === undefined ? 5 : b]++; } }
          if (round === 50) for (const o of ctx.drag.values()) if (o.team === us) { agg.units50++; agg.len50 += o.body.length; }
        },
        death(d, rec, idx, other, round) {
          if (d.team !== us || round > 50) return;
          const k = `${ML.CAUSE[rec.cause]}@b${bin[d.body[0].y * W + d.body[0].x]}`; agg.deaths[k] = (agg.deaths[k] || 0) + 1;
        },
      });
    }
  }
  console.log(`== ${name} ${mapName}: ${agg.games} games; r50 units ${(agg.units50 / agg.games).toFixed(1)}, r50 total length ${(agg.len50 / agg.games).toFixed(1)}`);
  console.log('  heads by bin (sum over games): ' + CPR.map(r => `r${r} ${(agg.bins[r] || []).slice(0, 5).join('/')}`).join('  '));
  console.log('  deaths r0-50 (cause@bin): ' + Object.entries(agg.deaths).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${v}`).join(', '));
}
