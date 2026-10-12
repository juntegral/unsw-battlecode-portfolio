#!/usr/bin/env node
// 온라인 기준점 PD 21판의 세부(2절): 판본별 우리 사망 분류, 10마리 판본에서 갓 태어난 계통 자식에게 일어난 일,
// 우리 통로 가까이 놓인 적 덤 드래곤의 r3–r5 위치.
// usage (저장소 루트에서): node exp/cand-pd10a/online_details.js
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const { load } = require(path.join(ROOT, 'tools/replay.js'));
const BS = require(path.join(ROOT, 'tools/baseline_study.js'));

const games = [];
for (const set of ['baseline-r1', 'baseline-r1b', 'baseline-r1c']) {
  const idx = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/online', set, 'index.json'), 'utf8'));
  for (const g of idx.games) if (g.mapName === 'Prisoners Dilemma') games.push({ g: { ...g, set }, file: path.join(ROOT, 'data/online', set, `M${g.gameId}.replay`) });
}
const cls = { 6: {}, 10: {} }, n = { 6: 0, 10: 0 }, ramByPhase = {};
const newborn = [], extras = [];
for (const { g, file } of games) {
  const R = load(file), init = R.match.map.initialDragons, nd = init.length, US = String(g.ourSide).toUpperCase();
  n[nd]++;
  const rec = BS.analyse(R, g);
  for (const d of rec.deaths.filter(x => x.side === 0)) {
    const c = cls[nd][d.cls2] || (cls[nd][d.cls2] = [0, 0]); c[0]++; c[1] += d.len;
    if (nd === 10 && d.cls2 === 'H-rammed') { const ph = d.r < 30 ? 'r0–29' : d.r < 100 ? 'r30–99' : 'r100+'; ramByPhase[ph] = (ramByPhase[ph] || 0) + d.len; }
  }
  if (nd !== 10) continue;
  // 갓 태어난 계통 자식: 시작 계통(가장 긴 시작 드래곤)의 탈출 분열 자식
  const start = init.filter(d => d.team === US).sort((a, b) => b.body.length - a.body.length)[0];
  const lineage = new Set([start.id]), births = new Map(), ind = {};
  let round = -1;
  const ours = new Set(init.filter(d => d.team === US).map(d => d.id));
  // 우리 통로 가까이 놓인 적 덤: 길이 2인 적 시작 드래곤 중 우리 시작 머리에서 맨해튼이 가장 가까운 것
  const W = R.match.map.width, H = R.match.map.height;
  const man = (a, b) => Math.min(Math.abs(a.x - b.x), W - Math.abs(a.x - b.x)) + Math.min(Math.abs(a.y - b.y), H - Math.abs(a.y - b.y));
  const enemyExtra = init.filter(d => d.team !== US && d.body.length === 2).sort((a, b) => man(a.body[0], start.body[0]) - man(b.body[0], start.body[0]))[0];
  const exPos = {}; let exHead = enemyExtra.body[0];
  // 우리 통로가 x=17이면(대칭 자리) 좌표를 (31−x, 15−y)로 돌려 x=14 기준으로 적는다
  const rot = start.body[0].x === 17 ? p => ({ x: W - 1 - p.x, y: H - 1 - p.y }) : p => p;
  for (const e of R.events) {
    if (e.type === 'roundStart') { if (round >= 3 && round <= 5) exPos[round] = rot(exHead); round = e.round; continue; }
    if (e.type === 'dragonIndicator') { ind[e.id] = e.text; continue; }
    if (e.type === 'dragonUpdate' && e.id === enemyExtra.id) { exHead = e.head; continue; }
    if (e.type === 'dragonSplit') {
      if (e.team === US) ours.add(e.childId);
      if (lineage.has(e.parentId) && /escape/.test(ind[e.parentId] || '')) { lineage.add(e.childId); births.set(e.childId, { r: round, x: e.childBody[0].x, y: e.childBody[0].y, facing: e.childFacing, parent: e.parentId, acted: false }); }
      continue;
    }
    if (e.type === 'dragonAction' && births.has(e.id)) {
      const b = births.get(e.id); if (b.acted) continue; b.acted = true;
      const a = e.action;
      if (a && a.kind === 'move' && a.steps[0] !== b.facing) newborn.push(`${g.gameId} 옆으로 나감 r${b.r} (${b.x},${b.y}) ${a.steps.join('')} [${ind[e.id] || ''}]`);
      if (a && a.kind === 'move' && a.steps.length > 1) newborn.push(`${g.gameId} 2걸음 질주 r${b.r} (${b.x},${b.y}) ${a.steps.join('')} [${ind[e.id] || ''}]`);
      continue;
    }
    if (e.type === 'turnStart') { newborn.cur = e.id; continue; }
    if (e.type === 'dragonDeath' && births.has(e.id)) {
      const b = births.get(e.id);
      if (!b.acted && round === b.r) newborn.push(`${g.gameId} 태어나자마자 박힘 r${b.r} (${b.x},${b.y}) 부모 #${b.parent} 자식 #${e.id} 박은 적 #${newborn.cur}`);
    }
  }
  extras.push(`${g.gameId} 적 덤 #${enemyExtra.id} (시작 ${rot(enemyExtra.body[0]).x},${rot(enemyExtra.body[0]).y}): ` + [3, 4, 5].map(r => exPos[r] ? `r${r} 끝 (${exPos[r].x},${exPos[r].y})` : `r${r} -`).join(' '));
}
console.log('## 우리 사망 분류 (판당 건수 / 길이)');
for (const nd of [6, 10]) console.log(`- ${nd}마리 ${n[nd]}판: ` + Object.entries(cls[nd]).map(([k, v]) => `${k} ${(v[0] / n[nd]).toFixed(1)}건 ${(v[1] / n[nd]).toFixed(1)}칸`).join(', '));
console.log(`- 10마리 판본에서 적이 박은 길이(7판 합): ` + Object.entries(ramByPhase).map(([k, v]) => `${k} ${v}칸`).join(', '));
console.log('## 10마리 판본: 갓 태어난 계통 자식');
for (const l of newborn) console.log('- ' + l);
console.log('## 10마리 판본: 우리 통로 가까이 놓인 적 덤의 위치(우리 통로가 x=14가 되게 돌린 좌표)');
for (const l of extras) console.log('- ' + l);
