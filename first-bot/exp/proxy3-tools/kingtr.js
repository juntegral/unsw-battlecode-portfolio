#!/usr/bin/env node
// usage (repository root): node exp/proxy3-tools/kingtr.js <replay> <side A|B> [from round]
// track a side's longest dragon from r300: every 10 rounds id/len/units; list big-dragon (>=10) splits and deaths
const { load } = require(process.cwd() + '/tools/replay.js');
const [,, f, side, from] = process.argv;
const R = load(f); const M = R.match.map;
const team = new Map(), len = new Map(), alive = new Set();
for (const d of M.initialDragons) { team.set(d.id, d.team); len.set(d.id, d.body.length); alive.add(d.id); }
let round = 0, actor = -1; const log = [];
for (const e of R.events) {
  if (e.type === 'roundStart') {
    round = e.round;
    if (round >= +(from || 300) && round % 10 === 0) {
      let best = -1, bl = 0, n = 0; for (const id of alive) if (team.get(id) === side) { n++; if (len.get(id) > bl) { bl = len.get(id); best = id; } }
      log.push(`r${round} units ${n} longest #${best} L${bl}`);
    }
  }
  if (e.type === 'turnStart') actor = e.id;
  if (e.type === 'dragonSplit') { team.set(e.childId, e.team); alive.add(e.childId); const pl = len.get(e.parentId); len.set(e.childId, e.childBody.length); len.set(e.parentId, e.parentBody.length); if (e.team === side && pl >= 10 && round >= +(from || 300)) log.push(`  r${round} split #${e.parentId} L${pl} -> parent ${e.parentBody.length} child #${e.childId} ${e.childBody.length}`); }
  if (e.type === 'tileChange' && !e.hasPearl && actor >= 0) len.set(actor, (len.get(actor) || 0) + 1);
  if (e.type === 'dragonAction' && e.action && e.action.kind === 'move' && e.action.steps.length > 1) len.set(e.id, (len.get(e.id) || 0) - (e.action.steps.length - 1));
  if (e.type === 'dragonDeath') { if (team.get(e.id) === side && len.get(e.id) >= 10 && round >= +(from || 300)) log.push(`  r${round} death #${e.id} L${len.get(e.id)} reason ${e.reason}`); alive.delete(e.id); }
}
console.log(log.join('\n'));
