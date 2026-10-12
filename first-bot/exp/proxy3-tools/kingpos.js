#!/usr/bin/env node
// usage (repository root): node exp/proxy3-tools/kingpos.js <replay> <side A|B> [from round]
// the side's longest dragon every 20 rounds from r200: id, length, head position, units
const { load } = require(process.cwd() + '/tools/replay.js');
const [,, f, side, from] = process.argv;
const R = load(f); const M = R.match.map;
const team = new Map(), len = new Map(), alive = new Set(), head = new Map();
for (const d of M.initialDragons) { team.set(d.id, d.team); len.set(d.id, d.body.length); alive.add(d.id); head.set(d.id, d.body[0]); }
let round = 0, actor = -1; const log = [];
for (const e of R.events) {
  if (e.type === 'roundStart') { round = e.round; if (round >= +(from || 200) && round % 20 === 0) { let best = -1, bl = 0, n = 0; for (const id of alive) if (team.get(id) === side) { n++; if (len.get(id) > bl) { bl = len.get(id); best = id; } } const h = head.get(best) || {}; log.push(`r${round} units ${n} longest #${best} L${bl} at ${h.x},${h.y}`); } }
  if (e.type === 'turnStart') actor = e.id;
  if (e.type === 'dragonSplit') { team.set(e.childId, e.team); alive.add(e.childId); len.set(e.childId, e.childBody.length); len.set(e.parentId, e.parentBody.length); head.set(e.childId, e.childBody[0]); }
  if (e.type === 'dragonUpdate') head.set(e.id, e.head);
  if (e.type === 'tileChange' && !e.hasPearl && actor >= 0) len.set(actor, (len.get(actor) || 0) + 1);
  if (e.type === 'dragonAction' && e.action && e.action.kind === 'move' && e.action.steps.length > 1) len.set(e.id, (len.get(e.id) || 0) - (e.action.steps.length - 1));
  if (e.type === 'dragonDeath') alive.delete(e.id);
}
console.log(log.join('\n'));
