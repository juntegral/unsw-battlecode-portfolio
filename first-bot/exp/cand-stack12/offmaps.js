#!/usr/bin/env node
// cand-stack12: pf labels (splits, pfx, pfc) of our side in every local game of the given labels, by map (the pf-off maps must show 0)
'use strict';
const fs = require('fs'), path = require('path'), { load } = require(path.resolve(__dirname, '..', '..', 'tools', 'replay.js'));
const by = {};
for (const lab of process.argv.slice(2)) for (const l of fs.readFileSync(path.resolve(__dirname, '..', lab, 'rows.jsonl'), 'utf8').split('\n')) {
  if (!l.trim()) continue; const r = JSON.parse(l); const [opp, map, side, seed] = r.key.split(':');
  const f = path.resolve(__dirname, '..', lab, 'games', `${opp}_${map}_${side}_${seed}`, 'game.replay'); if (!fs.existsSync(f)) continue;
  const R = load(f), team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
  const o = by[map] || (by[map] = { games: 0, pf: 0, pfx: 0, pfc: 0 }); o.games++;
  for (const e of R.events) {
    if (e.type === 'dragonSplit') team.set(e.childId, e.team);
    else if (e.type === 'dragonIndicator' && team.get(e.id) === side && e.text) { if (/^pf\d/.test(e.text)) o.pf++; if (/ pfx(\s|$)/.test(e.text)) o.pfx++; if (/ pfc(\s|$)/.test(e.text)) o.pfc++; }
  }
}
for (const [m, o] of Object.entries(by).sort()) console.log(`${m}: ${o.games} games, pf ${o.pf}, pfx ${o.pfx}, pfc ${o.pfc}`);
