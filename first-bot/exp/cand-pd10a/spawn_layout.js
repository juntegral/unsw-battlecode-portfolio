#!/usr/bin/env node
// 서버 Prisoners Dilemma 두 판본의 진주 생성 칸을 리플레이에서 잰다(서버 리플레이는 칸의 생성 간격을 0으로 숨긴다).
// usage (저장소 루트에서): node exp/cand-pd10a/spawn_layout.js [--until 2026-09-29T18:00:00Z]
//   --until: 상위권 경기는 대전 시각이 이 시각 이하인 것만 쓴다(기본 2026-09-29T18:00:00Z). 우리 기준점 경기는 모두 쓴다.
// 입력: data/top의 Prisoners Dilemma 경기 전부와 data/online/baseline-r1, -r1b, -r1c의 PD 경기(네트워크 없음).
// 방법: 라운드 시작의 tileChange(hasPearl=true)만 자연 생성으로 센다(사망 직후의 것은 주검 진주라 뺀다).
//   칸 묶음마다 판당 생성 수, 0라운드 생성 비율, 첫 생성 라운드 분포(자연 생성이 한 번이라도 있던 판)를 낸다.
//   로컬 지도 파일의 생성 칸 집합과 비교한다.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const { load } = require(path.join(ROOT, 'tools/replay.js'));
const argv = process.argv.slice(2);
const UNTIL = new Date((() => { const i = argv.indexOf('--until'); return i >= 0 ? argv[i + 1] : '2026-09-29T18:00:00Z'; })()).toISOString();

function files() {
  const out = [];
  for (const l of fs.readFileSync(path.join(ROOT, 'data/top/index.jsonl'), 'utf8').trim().split('\n')) {
    const r = JSON.parse(l); if (r.map !== 'Prisoners Dilemma' || r.at > UNTIL) continue;
    const f = path.join(ROOT, 'data/top', String(r.battleId), r.gameId + '.replay.gz'); if (fs.existsSync(f)) out.push({ f, src: 'top' });
  }
  for (const set of ['baseline-r1', 'baseline-r1b', 'baseline-r1c']) {
    const idx = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/online', set, 'index.json'), 'utf8'));
    for (const g of idx.games) if (g.mapName === 'Prisoners Dilemma') out.push({ f: path.join(ROOT, 'data/online', set, `M${g.gameId}.replay`), src: 'ours' });
  }
  return out;
}
const groupOf = (x, y) => {
  if ((x === 14 || x === 17) && (y === 1 || y === 14)) return '통로 샘물 (14,1)(14,14)(17,1)(17,14)';
  if ((x === 14 || x === 17) && (y === 0 || y === 15)) return '통로 끝 (14,0)(14,15)(17,0)(17,15)';
  if ((x === 14 || x === 17) && (y === 2 || y === 13)) return '통로 안쪽 (14,2)(14,13)(17,2)(17,13)';
  if ((x === 15 || x === 16) && (y <= 1 || y >= 14)) return '가운데 끝 x15–16, y0–1·14–15';
  if (x === 15 || x === 16) return '가운데 x15–16, y2–13';
  return '옆 (x10–13, 18–21)';
};
const GROUPS = ['통로 샘물 (14,1)(14,14)(17,1)(17,14)', '통로 끝 (14,0)(14,15)(17,0)(17,15)', '통로 안쪽 (14,2)(14,13)(17,2)(17,13)', '가운데 x15–16, y2–13', '가운데 끝 x15–16, y0–1·14–15', '옆 (x10–13, 18–21)'];
function main() {
  const agg = { 6: {}, 10: {} }, n = { 6: 0, 10: 0 }, nSrc = { 6: { top: 0, ours: 0 }, 10: { top: 0, ours: 0 } }, tilesSeen = { 6: new Set(), 10: new Set() };
  for (const { f, src } of files()) {
    let R; try { R = load(f); } catch { continue; }
    const nd = R.match.map.initialDragons.length; if (nd !== 6 && nd !== 10) continue;
    n[nd]++; nSrc[nd][src]++;
    const first = {}, cnt = {};
    let round = -1, afterDeath = false;
    for (const e of R.events) {
      if (e.type === 'roundStart') { round = e.round; afterDeath = false; continue; }
      if (e.type === 'dragonDeath') { afterDeath = true; continue; }
      if (e.type === 'tileChange' && e.hasPearl) { if (afterDeath) continue; const k = e.tile.x + ',' + e.tile.y; cnt[k] = (cnt[k] || 0) + 1; if (!(k in first)) first[k] = round; continue; }
      afterDeath = false;
    }
    for (const [k, c] of Object.entries(cnt)) {
      tilesSeen[nd].add(k);
      const [x, y] = k.split(',').map(Number), g = groupOf(x, y);
      const a = agg[nd][g] || (agg[nd][g] = { spawns: 0, r0: 0, firsts: [] });
      a.spawns += c; if (first[k] === 0) a.r0++; a.firsts.push(first[k]);
    }
  }
  const tilesIn = g => { let c = 0; for (let x = 10; x <= 21; x++) for (let y = 0; y < 16; y++) if (groupOf(x, y) === g) c++; return c; };
  const q = (a, p) => { if (!a.length) return '-'; const b = [...a].sort((x, y) => x - y); return b[Math.floor((b.length - 1) * p)]; };
  console.log(`경기: 6마리 ${n[6]}판(상위권 ${nSrc[6].top}, 우리 ${nSrc[6].ours}), 10마리 ${n[10]}판(상위권 ${nSrc[10].top}, 우리 ${nSrc[10].ours})`);
  console.log('| 칸 묶음 | 판본 | 한 번이라도 생성된 칸 | 판·칸당 생성 | 0라운드 생성(판·칸 비율) | 첫 생성 라운드 p10 / p50 / p90 / 최대 |');
  console.log('|---|---|---:|---:|---:|---|');
  for (const g of GROUPS) for (const nd of [6, 10]) {
    const a = agg[nd][g] || { spawns: 0, r0: 0, firsts: [] };
    const tiles = [...tilesSeen[nd]].filter(k => { const [x, y] = k.split(',').map(Number); return groupOf(x, y) === g; }).length;
    const denom = n[nd] * (g.startsWith('옆') ? tiles || 1 : tilesIn(g));
    console.log(`| ${g} | ${nd} | ${tiles} | ${(a.spawns / denom).toFixed(2)} | ${(a.r0 / denom).toFixed(2)} | ${q(a.firsts, 0.1)} / ${q(a.firsts, 0.5)} / ${q(a.firsts, 0.9)} / ${a.firsts.length ? Math.max(...a.firsts) : '-'} |`);
  }
  // 지도 파일과 비교
  const mapTiles = file => { const s = new Set(); for (const l of fs.readFileSync(path.join(ROOT, file), 'utf8').split('\n')) { const p = l.trim().split(/\s+/); if (p[0] === 'TILE' && +p[4] > 0) s.add(p[1] + ',' + p[2]); } return s; };
  for (const [file, nd] of [['maps/online-20260927/prisoners_dilemma.map', 6], ['maps/variants/prisoners_dilemma_10.map', 10], ['exp/cand-pd10a/maps-pd/prisoners_dilemma_10s.map', 10]]) {
    const m = mapTiles(file), seen = tilesSeen[nd];
    const onlyMap = [...m].filter(k => !seen.has(k)), onlyServer = [...seen].filter(k => !m.has(k));
    console.log(`${file}: 생성 칸 ${m.size}, 서버 ${nd}마리 판본에서 생성이 관측된 칸 ${seen.size}; 파일에만 ${onlyMap.length}칸 ${onlyMap.join(' ')}; 서버에만 ${onlyServer.length}칸 ${onlyServer.join(' ')}`);
  }
}
main();
