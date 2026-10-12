#!/usr/bin/env node
// cand-stack11 local: our L >= 8 deaths from r300 by cause and window (r300-429 / r430-499), 500-round maps, per game; and whether the
// dragon was our longest at death (ledger king flag). usage: node exp/cand-stack11/l8deaths.js <pool a+b> [...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const MAPNAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma', queen_of_spades: 'Queen Of Spades', schooltime: 'Schooltime', slithery_fight: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const R500 = new Set(['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma']);
const CN = ['sac', 'trap', 'rammed', 'ram', 'body', 'allyHead', 'timeout', 'sprint'];
for (const pool of process.argv.slice(2)) {
  let games = 0; const c = {}; const add = (k) => { c[k] = (c[k] || 0) + 1; };
  for (const dirArg of pool.split('+')) {
    const dir = path.resolve(dirArg);
    for (const l of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean)) {
      const row = JSON.parse(l), [opp, map, side, seed] = row.key.split(':');
      const mapName = MAPNAME[map.replace(/_(b|10)$/, '')] || map; if (!R500.has(mapName)) continue;
      const f = path.join(dir, 'games', `${opp}_${map}_${side}_${seed}`, 'game.replay'); if (!fs.existsSync(f)) continue;
      games++;
      perGame(load(f), { map: mapName }, { death(d, rec, idx, other, r) { if (d.team !== side || r < 300 || rec.len < 8) return; add((r < 430 ? 'r300-429 ' : 'r430-499 ') + CN[rec.cause] + (rec.king ? ' (king)' : '')); } });
    }
  }
  console.log(`${pool}: 500-round games ${games}`);
  for (const k of Object.keys(c).sort()) console.log(`   ${k.padEnd(28)} ${(c[k] / games).toFixed(2)} (${c[k]})`);
}
