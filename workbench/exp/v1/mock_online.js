#!/usr/bin/env node
// Lay out a local eval set (tools/eval.js: rows.jsonl + games/<key>/game.replay) like data/online/<set> so that eval/system_report.js can read it
// with --online <dir> --no-extract (outcome, line sacrifice pearls, engine labels; the mass-ledger cells stay empty: .cache is read-only here).
// The proxy opponents get top-6 ids only so that the report counts them (proxy4_king 306, proxy4_swarm 70, proxy4_elim 20); they are local
// mimics, not those teams.
// usage: node exp/v1/mock_online.js <evalDir> <mockRoot> <setName>
'use strict';
const fs = require('fs'), path = require('path');
const [evalDir, mockRoot, setName] = process.argv.slice(2);
const OPP = { proxy4_king: 306, proxy4_swarm: 70, proxy4_elim: 20 };
const NAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', devil_b: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma',
  prisoners_dilemma_10: 'Prisoners Dilemma', queen_of_spades: 'Queen Of Spades', queen_of_spades_b: 'Queen Of Spades', schooltime: 'Schooltime',
  schooltime_b: 'Schooltime', slithery_fight: 'Slithery Fight', slithery_fight_b: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const out = path.join(mockRoot, setName);
fs.mkdirSync(out, { recursive: true });
const rows = fs.readFileSync(path.join(evalDir, 'rows.jsonl'), 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l)).filter(r => r.G !== undefined);
const games = [];
let id = 1;
for (const r of rows) {
  const rep = path.resolve(evalDir, 'games', r.key.replace(/:/g, '_'), 'game.replay');
  if (!fs.existsSync(rep)) continue;
  const gid = id++;
  const us = r.side, them = us === 'A' ? 'B' : 'A';
  const result = { endReason: r.endReason, winner: r.won ? us : (r.endReason === 'roundLimit' && r.G === r.theirLongest ? null : them),
    ['team' + us]: { dragonCount: r.units, longestDragon: r.G, totalLength: r.total }, ['team' + them]: { dragonCount: null, longestDragon: r.theirLongest } };
  games.push({ gameId: gid, opponentTeam: OPP[r.opp] || 0, ourSide: us, winner: result.winner, ourWin: !!r.won, mapName: NAME[r.map], key: r.key });
  fs.writeFileSync(path.join(out, `game-${gid}.json`), JSON.stringify({ replay: { result }, teamAName: us === 'A' ? 'us' : r.opp, teamBName: us === 'B' ? 'us' : r.opp }));
  const link = path.join(out, `M${gid}.replay`);
  try { fs.unlinkSync(link); } catch {}
  fs.symlinkSync(rep, link);
}
fs.writeFileSync(path.join(out, 'index.json'), JSON.stringify({ games }, null, 1));
console.log(`${setName}: ${games.length} games -> ${out}`);
