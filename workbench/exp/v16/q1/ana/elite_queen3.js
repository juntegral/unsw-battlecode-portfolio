// scratch: new-rule elite games: when and how queens die (death events), which side's queen dies first, and the end state by case
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = '~/01. Project/개인 프로젝트/unsw-swarm';
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const load = makeLoader(viewerSource());
const rows = fs.readFileSync(path.join(ROOT, 'data/elite/index.jsonl'), 'utf8').trim().split('\n').map(JSON.parse).filter(r => r.at >= '2026-10-01T11:08');
const bins = [[0, 10], [10, 50], [50, 100], [100, 200], [200, 300], [300, 400], [400, 430], [430, 470], [470, 501]];
const hist = { W: bins.map(() => 0), L: bins.map(() => 0) }, reasons = { W: {}, L: {} }, firstDead = { W: 0, L: 0, same: 0 };
let n = 0; const both = [], perMap = {};
for (const r of rows) {
  const f = path.join(ROOT, 'data/elite', String(r.battleId), r.gameId + '.replay.gz');
  if (!fs.existsSync(f)) continue;
  let R; try { R = load(f); } catch (e) { continue; }
  if (!R.result || !R.result.winner) continue;
  n++;
  const W = R.result.winner, Lt = W === 'A' ? 'B' : 'A', init = R.match.map.initialDragons, qOf = {};
  for (const d of init) if (qOf[d.team] === undefined || d.id < qOf[d.team]) qOf[d.team] = d.id;
  let round = 0; const qd = {}, qr = {};
  for (const e of R.events) { if (e.type === 'roundStart') round++; if (e.type === 'dragonDeath' && (e.id === qOf.A || e.id === qOf.B) && qd[e.id] === undefined) { qd[e.id] = round; qr[e.id] = e.reason; } }
  const pm = perMap[r.map] = perMap[r.map] || { n: 0, wDead: 0, lDead: 0, early: 0 };
  pm.n++;
  for (const [side, t] of [['W', W], ['L', Lt]]) {
    const q = qOf[t]; if (qd[q] === undefined) continue;
    const b = bins.findIndex(([a, z]) => qd[q] >= a && qd[q] < z); hist[side][b]++;
    reasons[side][qr[q]] = (reasons[side][qr[q]] || 0) + 1;
    if (side === 'W') pm.wDead++; else pm.lDead++;
    if (qd[q] < 10) pm.early++;
  }
  const dw = qd[qOf[W]], dl = qd[qOf[Lt]];
  if (dw !== undefined && dl !== undefined) { if (dw < dl) firstDead.W++; else if (dl < dw) firstDead.L++; else firstDead.same++; both.push(Math.max(dw, dl)); }
}
console.log(`games with a winner ${n}`);
console.log('queen death round bins', bins.map(b => b.join('-')).join(' | '));
console.log('  winner\'s queen', hist.W.join(' | '));
console.log('  loser\'s queen ', hist.L.join(' | '));
console.log('death reasons winner', JSON.stringify(reasons.W), 'loser', JSON.stringify(reasons.L));
console.log(`both dead: whose queen died first: winner's ${firstDead.W}, loser's ${firstDead.L}, same round ${firstDead.same}`);
const s = [...both].sort((a, b) => a - b); console.log(`both dead: round of the second queen death: p25 ${s[Math.floor(s.length * .25)]} median ${s[Math.floor(s.length / 2)]} p75 ${s[Math.floor(s.length * .75)]} (n${s.length}); after r430: ${s.filter(x => x >= 430).length}`);
for (const [m, v] of Object.entries(perMap)) console.log(`  ${m.padEnd(20)} n${v.n} winner's queen dead ${v.wDead}, loser's ${v.lDead}, before r10 ${v.early}`);
