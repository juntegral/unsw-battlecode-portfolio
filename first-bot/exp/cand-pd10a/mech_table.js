#!/usr/bin/env node
// 8.3절 기전 표: 평가 폴더들의 PD 경기에서 고리 지표를 지도 판본별로 뽑아 마크다운 표로 낸다.
// usage (저장소 루트에서): node exp/cand-pd10a/mech_table.js [--map prisoners_dilemma_10s] <라벨> [<라벨> ...]
//   예: node exp/cand-pd10a/mech_table.js --map prisoners_dilemma_10s cand-pd10-base-px cand-pd10a-pd-px cand-pd10e-pd-px
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const S = require('./pd10_study.js');
const argv = process.argv.slice(2);
const mi = argv.indexOf('--map'), map = mi >= 0 ? argv[mi + 1] : 'prisoners_dilemma_10s';
const labels = argv.filter((a, i) => !a.startsWith('--') && i !== mi + 1);
const f1 = x => Number.isFinite(x) ? x.toFixed(1) : '-';
console.log(`지도: ${map}`);
console.log('| 평가 | 판 | 승 | 생존 | G | 고리 위상 | 탈출 분열/판 | 300라운드 넘게 간 고리 | 열린 칸 탄생 | 태어나자마자 박힌 판 | 옆으로 나간 판 | 계통(6+)이 박힌 판 | 주머니 먹기/판 | 자연 진주 우리:상대 |');
console.log('|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|');
for (const l of labels) {
  const tasks = S.listEval(path.join(ROOT, 'exp', l)).filter(t => t.row.map === map);
  const rows = tasks.map(S.study);
  const s = S.summarise(rows, l).find(x => x.ver === map);
  if (!s) continue;
  const ph = Object.entries(s.phase).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}(${v})`).join(' ');
  console.log(`| ${l} | ${s.n} | ${s.wins} | ${s.alive} | ${s.G.toFixed(2)} | ${ph} | ${f1(s.escMean)} | ${s.loopHeldTo300} | ${(100 * s.exposedShare).toFixed(1)}% | ${s.rammedAtBirthGames} | ${s.turnedAtBirthGames} | ${s.linRammedGames} | ${f1(s.pocketEats)} | ${f1(s.usNat)} : ${f1(s.themNat)} |`);
}
