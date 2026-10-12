#!/usr/bin/env node
'use strict';
// doctable.js — compact per-map tables for research/experiments/proxies-v3.md from calib.js --json outputs:
// each cell "online / v3 / v2" for the chosen metrics.
// usage: node exp/proxy3-tools/doctable.js <calib.json> "<online group>" "<v3 group>" "<v2 group>" metric[,metric...]
const fs = require('fs');
const [,, file, gOn, g3, g2, mets] = process.argv;
const R = JSON.parse(fs.readFileSync(file, 'utf8'));
const MAPS = ['autarky', 'portals', 'schooltime', 'slithery_fight', 'trauma', 'default', 'devil', 'pd6', 'pd10', 'queen_of_spades', 'trophy', '500-round', 'elimination', 'all'];
const NAME = { autarky: 'Autarky', portals: 'Portals', schooltime: 'Schooltime', slithery_fight: 'Slithery Fight', trauma: 'Trauma', default: 'Default', devil: 'Devil', pd6: 'PD6', pd10: 'PD10', queen_of_spades: 'Queen Of Spades', trophy: 'Trophy', '500-round': '**500라운드형**', elimination: '**전멸형**', all: '**전체**' };
const KN = { n: '판', win: '승', elim: '우리 전멸', elimR: '전멸 라운드 중앙', reach: 'r340 도달', G: 'G', oU100: '상대 수 r100', oM300: '상대 몸 합 r300', oU300: '상대 수 r300', oK400: '상대 왕 r400', oK500: '상대 왕 r500', uM300: '우리 몸 합 r300' };
const pct = new Set(['win', 'elim', 'reach']);
const f = (k, v) => v === null || v === undefined || Number.isNaN(v) ? '–' : pct.has(k) ? (100 * v).toFixed(0) + '%' : k === 'G' ? v.toFixed(1) : v.toFixed(0);
const M = mets.split(',');
console.log('| 지도 | ' + M.map(k => KN[k] || k).join(' | ') + ' |');
console.log('|---|' + M.map(() => '---').join('|') + '|');
for (const m of MAPS) {
  const cells = M.map(k => [gOn, g3, g2].map(g => f(k, ((R[g] || {})[m] || {})[k])).join(' / '));
  console.log(`| ${NAME[m]} | ${cells.join(' | ')} |`);
}
