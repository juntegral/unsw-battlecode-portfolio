#!/usr/bin/env node
// 평가 폴더의 prisoners_dilemma_10 경기가 어느 진주 배치로 돌았는지 리플레이에서 확인한다.
// 2026-09-30 04:00 KST(커밋 310dca9)에 maps/variants/prisoners_dilemma_10.map이 서버 추정 배치로 바뀌었다.
// exp/cand-pd10a/maps-pd/prisoners_dilemma_10.map은 그 파일을 가리키는 링크라서, 그 뒤에 돌린 경기는 새 배치다.
// 판정: 로컬 리플레이의 pearlRespawn에서 (14,2) 칸이 생성 칸(옛 88칸 배치)인지, 생성 없음(새 76칸 배치)인지 본다.
// usage (저장소 루트에서): node exp/cand-pd10a/layout_check.js <라벨> [<라벨> ...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const { load } = require(path.join(ROOT, 'tools/replay.js'));
for (const label of process.argv.slice(2)) {
  const dir = path.join(ROOT, 'exp', label), f = path.join(dir, 'rows.jsonl');
  if (!fs.existsSync(f)) { console.log(label, '없음'); continue; }
  const rows = fs.readFileSync(f, 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined && r.map === 'prisoners_dilemma_10');
  const c = { old: [], new: [], unknown: [] };
  for (const r of rows) {
    const rp = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay');
    if (!fs.existsSync(rp)) { c.unknown.push(r.key); continue; }
    const R = load(rp), M = R.match.map, t = 2 * M.width + 14, pr = M.pearlRespawn[t];
    (pr && pr.maxRounds > 0 ? c.old : c.new).push(r.key);
  }
  console.log(`${label}: _10 경기 ${rows.length}판, 옛 배치 ${c.old.length}, 새 배치 ${c.new.length}, 모름 ${c.unknown.length}` + (c.new.length ? ` | 새 배치: ${c.new.join(' ')}` : ''));
}
