#!/usr/bin/env node
// 온라인 PD 경기에서 우리 시작 드래곤별(자손 포함) 먹은 진주 수와 마지막 자손이 죽은 라운드를 센다.
// usage (저장소 루트에서): node exp/cand-pd10a/lineage_eat.js
// 방법: 그 드래곤의 턴에 진주가 사라지는 tileChange = 그 드래곤이 먹음. 분열 자식은 부모의 시작 드래곤에 묶는다.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const { load } = require(path.join(ROOT, 'tools/replay.js'));
const rows = [];
for (const set of ['baseline-r1', 'baseline-r1b', 'baseline-r1c']) {
  const idx = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/online', set, 'index.json'), 'utf8'));
  for (const g of idx.games) {
    if (g.mapName !== 'Prisoners Dilemma') continue;
    const R = load(path.join(ROOT, 'data/online', set, `M${g.gameId}.replay`));
    const US = String(g.ourSide).toUpperCase(), init = R.match.map.initialDragons, nd = init.length;
    const root = new Map(), team = new Map();
    for (const d of init) { root.set(d.id, d.id); team.set(d.id, d.team); }
    const role = id => { const d = init.find(x => x.id === id); return d.body.length >= 10 ? '시작(11)' : d.body.length === 3 ? '옆(3)' : '덤(2)'; };
    const eat = {}, last = {}, alive = {};
    for (const d of init) if (d.team === US) { eat[d.id] = 0; alive[d.id] = new Set([d.id]); last[d.id] = null; }
    let round = -1, cur = -1;
    for (const e of R.events) {
      if (e.type === 'roundStart') { round = e.round; continue; }
      if (e.type === 'turnStart') { cur = e.id; continue; }
      if (e.type === 'dragonSplit') { root.set(e.childId, root.get(e.parentId)); team.set(e.childId, e.team); if (e.team === US) alive[root.get(e.parentId)].add(e.childId); continue; }
      if (e.type === 'tileChange' && !e.hasPearl && team.get(cur) === US) { eat[root.get(cur)]++; continue; }
      if (e.type === 'dragonDeath' && team.get(e.id) === US) { const r0 = root.get(e.id); alive[r0].delete(e.id); if (!alive[r0].size) last[r0] = round; }
    }
    for (const id of Object.keys(eat).map(Number)) rows.push({ game: g.gameId, nd, role: role(id), eat: eat[id], end: last[id] });
  }
}
const med = a => { if (!a.length) return null; const b = [...a].sort((x, y) => x - y), m = b.length >> 1; return b.length % 2 ? b[m] : (b[m - 1] + b[m]) / 2; };
console.log('| 판본 | 시작 드래곤 | 수(판×마리) | 먹은 진주(자손 포함, 판당 평균) | 계통이 끝난 라운드 중앙값 | 500라운드까지 산 계통 |');
console.log('|---|---|---:|---:|---:|---:|');
for (const nd of [6, 10]) for (const role of ['시작(11)', '옆(3)', '덤(2)']) {
  const rs = rows.filter(r => r.nd === nd && r.role === role); if (!rs.length) continue;
  console.log(`| ${nd} | ${role} | ${rs.length} | ${(rs.reduce((a, r) => a + r.eat, 0) / rs.length).toFixed(1)} | ${med(rs.filter(r => r.end !== null).map(r => r.end)) ?? '-'} | ${rs.filter(r => r.end === null).length} |`);
}
