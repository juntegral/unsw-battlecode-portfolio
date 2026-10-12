#!/usr/bin/env node
// 평가 폴더의 리플레이에서 주머니 먹기(pocket-eat 표시)가 일어난 자리를 센다: 지도별 횟수, 그 칸이 막힌 길(양옆 해초)인지,
// 머리 뒤로 이어진 막힌 길의 길이.
// usage (저장소 루트에서): node exp/cand-pd10a/pocket_sites.js exp/<평가 폴더>
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const { load } = require(path.join(ROOT, 'tools/replay.js'));
const BS = require(path.join(ROOT, 'tools/baseline_study.js'));
const dir = path.resolve(ROOT, process.argv[2]);
const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined);
const agg = {};
for (const r of rows) {
  const f = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
  const R = load(f), geo = BS.buildGeo(R.match.map), W = geo.W;
  const head = {}; for (const d of R.match.map.initialDragons) head[d.id] = d.body[0];
  let rd = -1, pend = null;
  const a = agg[r.map] || (agg[r.map] = { games: 0, n: 0, lane1: 0, lane3: 0 }); a.games++;
  for (const e of R.events) {
    if (e.type === 'roundStart') rd = e.round;
    if (e.type === 'dragonSplit') head[e.childId] = e.childBody[0];
    if (e.type === 'dragonIndicator' && /^pocket-eat/.test(e.text || '')) pend = { id: e.id, from: head[e.id] };
    if (e.type === 'dragonUpdate') {
      if (pend && pend.id === e.id) {
        const fx = pend.from.x, fy = pend.from.y, dx = e.head.x - fx, dy = e.head.y - fy;
        const along = dy === -1 ? 0 : dx === 1 ? 1 : dy === 1 ? 2 : 3, back = (along + 2) & 3;
        let t = fy * W + fx, lane = 0;
        for (let k = 0; k < 20 && t >= 0; k++) {
          if (geo.nb[t * 4 + ((along + 3) & 3)] >= 0 || geo.nb[t * 4 + ((along + 1) & 3)] >= 0) break;
          lane++; t = geo.nb[t * 4 + back];
        }
        a.n++; if (lane >= 1) a.lane1++; if (lane >= 3) a.lane3++;
        pend = null;
      }
      head[e.id] = e.head;
    }
  }
}
console.log('| 지도 | 판 | 주머니 먹기 | 그 칸이 막힌 길 | 막힌 길 3칸 이상 |');
console.log('|---|---:|---:|---:|---:|');
for (const [m, a] of Object.entries(agg).sort()) console.log(`| ${m} | ${a.games} | ${a.n} | ${a.lane1} | ${a.lane3} |`);
