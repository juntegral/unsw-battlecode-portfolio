#!/usr/bin/env node
'use strict';
// deaths_phase.js — our deaths by phase and kind on one map of an eval (cand-escape1 report, section 7).
// usage: node exp/cand-escape1/deaths_phase.js <eval dir> <map>
//   kind: 'feed' = our dragon died on its own turn with an indicator starting "feed" (late consolidation), 'noexit' = its
//   indicator started "no-exit", 'rammed' = it died on another dragon's turn, otherwise the replay's reason (H, W, S, O, A).
//   Phases: r0-299, r300-339, r340-429, r430-499. Prints counts summed over the map's games.
const path = require('path'), fs = require('fs');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const [dir, mapf] = process.argv.slice(2);
const agg = {};
for (const k of fs.readdirSync(path.join(dir, 'games')).filter(k => k.includes('_' + mapf + '_'))) {
  const us = k.includes('_A_') ? 'A' : 'B';
  const R = load(path.join(dir, 'games', k, 'game.replay'));
  const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
  let round = 0, cur = -1; const ind = new Map();
  for (const e of R.events) {
    if (e.type === 'roundStart') round = e.round;
    else if (e.type === 'turnStart') cur = e.id;
    else if (e.type === 'dragonIndicator') ind.set(e.id, e.text);
    else if (e.type === 'dragonSplit') team.set(e.childId, e.team);
    else if (e.type === 'dragonDeath' && team.get(e.id) === us) {
      const t = ind.get(e.id) || '';
      const kind = e.id !== cur ? 'rammed' : t.startsWith('feed') ? 'feed' : t.startsWith('no-exit') ? 'noexit' : e.reason;
      const ph = round < 300 ? 'r0-299' : round < 340 ? 'r300-339' : round < 430 ? 'r340-429' : 'r430-499';
      agg[ph + ' ' + kind] = (agg[ph + ' ' + kind] || 0) + 1;
    }
  }
}
console.log(JSON.stringify(Object.fromEntries(Object.entries(agg).sort())));
