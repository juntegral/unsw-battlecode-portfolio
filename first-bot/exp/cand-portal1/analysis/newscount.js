// count portal-news rays (cand-portal5 magic 0x15) sent by a team and how many hit an ally body/head
const path = require('path');
const HR = '~/01. Project/개인 프로젝트/unsw-heuristic';
const { load } = require(path.join(HR, 'tools/replay.js'));
const R = load(process.argv[2]); const TEAM = process.argv[3] || 'A';
const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
const WH = 0x9E3779B97F4A7C15n;
let sent = 0, hitAlly = 0, trap = 0, trapHit = 0, other = 0;
for (const e of R.events) {
  if (e.type === 'dragonSplit') team.set(e.childId, e.team);
  if (e.type !== 'sonarPing' || team.get(e.senderId) !== TEAM || e.value64 === undefined) continue;
  const v = BigInt(e.value64) ^ WH;
  if ((v >> 58n) !== 0x15n) { other++; continue; }
  sent++; const tr = Number((v >> 28n) & 15n);
  const ally = e.hitKind === 'ally' || e.hitKind === 'allyHead';
  if (ally) hitAlly++;
  if (tr) { trap++; if (ally) trapHit++; }
}
console.log({ portalNewsRays: sent, hitAlly, withTrapBits: trap, trapHitAlly: trapHit, otherRays: other });
