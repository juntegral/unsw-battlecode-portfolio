#!/usr/bin/env node
// Replay triage for one wave (or a pool): which games to study first. Adopted from the Halite III practice of ranking
// losses by margin (research/external/INTEGRATION-2026-09-30.md; user rule 2026-09-30 11:25: classify the full
// population with scripts, then read only selected replays).
//   - losses by margin: their longest / our longest at the end (our longest 0 when eliminated), per opponent and map
//   - upset wins: games we won against the elite, the rarest and most instructive wins
//   - classes: loss margin by opponent x map, so the reader picks the worst of each class
// usage: node tools/wave_triage.js <set>[+<set>] [--top 12] [--out file.md]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..'), ONLINE = path.join(ROOT, 'data', 'online');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const pool = argv.find((a, i) => !a.startsWith('--') && !['--top', '--out'].includes(argv[i - 1]));
if (!pool) { console.error('usage: wave_triage.js <set>[+<set>] [--top 12] [--out file.md]'); process.exit(2); }
const TOP = +opt('--top', 12);
let names = {};
try { for (const t of JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'top', 'leaderboard.json'), 'utf8'))) names[t.id] = t.name; } catch { /* optional */ }
const rows = [];
for (const set of pool.split('+')) {
  const dir = fs.existsSync(path.join(path.resolve(ROOT, set), 'index.json')) ? path.resolve(ROOT, set) : path.join(ONLINE, set);
  const idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  for (const g of idx.games || idx) {
    if (g.ourWin === null || g.ourWin === undefined) continue;
    let res = null;
    try { res = JSON.parse(fs.readFileSync(path.join(dir, `game-${g.gameId}.json`), 'utf8')).replay.result; } catch { continue; }
    const us = res['team' + g.ourSide], them = res['team' + (g.ourSide === 'A' ? 'B' : 'A')];
    const ourL = us.dragonCount > 0 ? us.longestDragon : 0, theirL = them.dragonCount > 0 ? them.longestDragon : 0;
    rows.push({ set, game: g.gameId, map: g.mapName, opp: names[g.opponentTeam] || String(g.opponentTeam), win: g.ourWin ? 1 : 0,
      ourL, theirL, ratio: (theirL + 1) / (ourL + 1), end: res.endReason, ourTotal: us.totalLength, theirTotal: them.totalLength });
  }
}
const L = [];
L.push(`# 기보 선별 목록: ${pool}`, '');
L.push(`- 모집단 ${rows.length}판(승 ${rows.filter(r => r.win).length}). 격차 = (상대 최장 + 1) / (우리 최장 + 1), 전멸이면 우리 최장 0.`);
L.push(`- 선별 규칙: 격차가 가장 큰 패배 ${TOP}판, 극상위권을 이긴 판 전부, 상대 × 지도 부류마다 가장 크게 진 판 하나.`, '');
const losses = rows.filter(r => !r.win).sort((a, b) => b.ratio - a.ratio);
L.push(`## 격차가 가장 큰 패배 ${Math.min(TOP, losses.length)}판`, '', '| 세트 | 게임 | 상대 | 지도 | 우리 최장 | 상대 최장 | 격차 | 끝 |', '|---|---|---|---|---:|---:|---:|---|');
for (const r of losses.slice(0, TOP)) L.push(`| ${r.set} | ${r.game} | ${r.opp} | ${r.map} | ${r.ourL} | ${r.theirL} | ${r.ratio.toFixed(1)} | ${r.end} |`);
const wins = rows.filter(r => r.win && !/dev test/.test(r.opp));
L.push('', `## 극상위권을 이긴 판 ${wins.length}판`, '', '| 세트 | 게임 | 상대 | 지도 | 우리 최장 | 상대 최장 | 끝 |', '|---|---|---|---|---:|---:|---|');
for (const r of wins) L.push(`| ${r.set} | ${r.game} | ${r.opp} | ${r.map} | ${r.ourL} | ${r.theirL} | ${r.end} |`);
const cls = new Map();
for (const r of losses) { const k = r.opp + '|' + r.map; if (!cls.has(k)) cls.set(k, []); cls.get(k).push(r); }
L.push('', `## 부류(상대 × 지도)별 가장 크게 진 판`, '', '| 상대 | 지도 | 패배 수 | 가장 크게 진 판 | 격차 |', '|---|---|---:|---|---:|');
for (const [k, rs] of [...cls].sort((a, b) => b[1][0].ratio - a[1][0].ratio)) { const [o, m] = k.split('|'); L.push(`| ${o} | ${m} | ${rs.length} | ${rs[0].set} ${rs[0].game} | ${rs[0].ratio.toFixed(1)} |`); }
const md = L.join('\n') + '\n';
if (opt('--out')) { fs.writeFileSync(path.resolve(ROOT, opt('--out')), md); console.log('wrote ' + opt('--out')); } else process.stdout.write(md);
