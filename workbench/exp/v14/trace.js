#!/usr/bin/env node
// v1.4: print our dragons' indicators, splits and deaths for rounds [from, to] of one replay (the opening module's " op" tags)
// usage: node exp/v14/trace.js <game dir> <our team A|B> [from] [to]
'use strict';
const path = require('path');
const { load } = require(path.join(__dirname, '..', '..', 'tools', 'viewer.js'));
const [dir, team, from = 0, to = 30] = process.argv.slice(2);
const R = load(dir);
const ours = new Set();
for (const e of R.match.initEvents || []) if (e.type === 'dragonSpawn' || e.type === 'dragonUpdate') {}
let round = -1;
const teamOf = {};
for (const d of R.match.map.initialDragons || []) {}
for (const e of R.events) {
  if (e.type === 'roundStart') { round = e.round; if (round > +to) break; continue; }
  if (e.type === 'dragonSplit') { teamOf[e.childId] = e.team; teamOf[e.parentId] = e.team; if (round >= +from && e.team === team) console.log(round, 'SPLIT', e.parentId, '->', e.childId, 'L' + e.parentBody.length + '+' + e.childBody.length, 'child@' + e.childBody[0].x + ',' + e.childBody[0].y); continue; }
  if (e.type === 'dragonUpdate' && e.team) teamOf[e.id] = e.team;
  if (e.type === 'dragonDeath' || e.type === 'dragonDied' || e.type === 'death') { if (round >= +from) console.log(round, 'DEATH', JSON.stringify(e).slice(0, 160)); continue; }
  if (e.type === 'dragonIndicator' && round >= +from) console.log(round, e.id, e.text.slice(0, 150));
}
