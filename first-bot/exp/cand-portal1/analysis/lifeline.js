// per dragon of a team: birth, death, length over time (every 25 rounds), head region, crossings
const path = require('path');
const HR = '~/01. Project/개인 프로젝트/unsw-heuristic';
const { load } = require(path.join(HR, 'tools/replay.js'));
const R = load(process.argv[2]); const TEAM = process.argv[3] || 'A';
const M = R.match.map, W = M.width;
const team = new Map(), len = new Map(), head = new Map(), born = new Map(), died = new Map(), tl = new Map();
for (const d of M.initialDragons) { team.set(d.id, d.team); len.set(d.id, d.body.length); head.set(d.id, d.body[0]); born.set(d.id, 0); }
let round = 0, cur = -1, phase = 'tick';
for (const e of R.events) {
  if (e.type === 'roundStart') { round = e.round; phase = 'tick'; if (round % 25 === 0) for (const [id, t] of team) if (t === TEAM && !died.has(id) && born.has(id)) { if (!tl.has(id)) tl.set(id, []); const h = head.get(id); tl.get(id).push(`${round}:L${len.get(id)}@${h.x},${h.y}`); } }
  if (e.type === 'turnStart') { phase = 'turn'; cur = e.id; }
  if (e.type === 'tileChange' && !e.hasPearl && phase === 'turn') len.set(cur, (len.get(cur) || 0) + 1);
  if (e.type === 'dragonSplit') { team.set(e.childId, e.team); born.set(e.childId, round); len.set(e.childId, e.childBody.length); len.set(e.parentId, e.parentBody.length); head.set(e.childId, e.childBody[0]); }
  if (e.type === 'dragonUpdate') { head.set(e.id, e.head); }
  if (e.type === 'dragonAction' && e.action.kind === 'move' && e.action.steps.length > 1) len.set(e.id, len.get(e.id) - (e.action.steps.length - 1));
  if (e.type === 'dragonDeath') died.set(e.id, round + ':' + e.reason);
}
console.log(JSON.stringify(R.result));
for (const [id, t] of team) if (t === TEAM) console.log(`#${id} born ${born.get(id)} died ${died.get(id) || '-'} | ${(tl.get(id) || []).join(' ')}`);
