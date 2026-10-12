#!/usr/bin/env node
// Q2: how much our queen eats: per game, her eats in rounds 0-99 / 100-299 / 300-499 (while alive) and the share of her turns with a claim
// or grab tag (cl@ / grab@: she is foraging). usage: node exp/q2/queeneat.js <runq set dir>... [--nopocket]
'use strict';
process.env.UNSW_RULES = process.env.UNSW_RULES || '123';   // 1.2.3 replays (tools/mass_ledger.js step simulation)
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const skip = process.argv.includes('--nopocket') ? /autarky|dilemma|slithery/i : null;
for (const set of process.argv.slice(2).filter(a => !a.startsWith('--'))) {
  const rows = fs.readFileSync(path.join(set, 'rows.jsonl'), 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse);
  const T = { games: 0, eats: [0, 0, 0], turns: [0, 0, 0], forage: 0, aliveTurns: 0 };
  for (const r of rows) {
    if (skip && skip.test(r.map)) continue;
    const f = path.join(set, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
    const Q = r.side === 'A' ? 0 : 1;
    const band = round => round < 100 ? 0 : round < 300 ? 1 : 2;
    perGame(load(f), { map: r.map, variant: 'a' }, {
      eat(d, k, o, round) { if (d.id === Q) T.eats[band(round)]++; },
      indicator(e, round) { if (e.id !== Q) return; T.turns[band(round)]++; T.aliveTurns++; if (/ (cl|grab)@/.test(e.text || '')) T.forage++; },
    });
    T.games++;
  }
  const per = (a, b) => b ? (100 * a / b).toFixed(1) : '-';
  console.log(`${path.basename(set)}: games ${T.games}; queen eats per 100 of her turns r0-99 ${per(T.eats[0], T.turns[0])}, r100-299 ${per(T.eats[1], T.turns[1])}, r300-499 ${per(T.eats[2], T.turns[2])} (her turns ${T.turns.join('/')}); turns with a claim or grab ${per(T.forage, T.aliveTurns)}%`);
}
