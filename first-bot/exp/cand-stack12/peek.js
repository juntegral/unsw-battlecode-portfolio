#!/usr/bin/env node
// cand-stack12: quick look at one local game: pf labels, pfx / pfc tags, our units at r10 / r50 / r100 (sanity check of the build)
'use strict';
const path = require('path'), { load } = require(path.resolve(__dirname, '..', '..', 'tools', 'replay.js'));
const [file, side] = process.argv.slice(2);
const R = load(file); const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
let round = -1; const pf = [], tags = { pfx: 0, pfc: 0 }, units = {}, alive = new Set([...team.keys()].filter(id => team.get(id) === side));
for (const e of R.events) {
  if (e.type === 'roundStart') { round = e.round; if ([10, 50, 100].includes(round)) units[round] = alive.size; }
  else if (e.type === 'dragonSplit') { team.set(e.childId, e.team); if (e.team === side) alive.add(e.childId); }
  else if (e.type === 'dragonDeath') alive.delete(e.id);
  else if (e.type === 'dragonIndicator' && team.get(e.id) === side && e.text) {
    if (/^pf\d/.test(e.text)) pf.push(`r${round} #${e.id} ${e.text}`);
    if (/ pfx(\s|$)/.test(e.text)) tags.pfx++; if (/ pfc(\s|$)/.test(e.text)) tags.pfc++;
  }
}
console.log(`pf ${pf.length}, pfx ${tags.pfx}, pfc ${tags.pfc}, units r10/r50/r100 ${units[10]}/${units[50]}/${units[100]}, rounds ${R.result && R.result.rounds}`);
console.log(pf.slice(0, 12).join('\n'));
