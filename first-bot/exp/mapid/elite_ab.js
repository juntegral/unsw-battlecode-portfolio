#!/usr/bin/env node
'use strict';
// elite_ab.js — stage 2 of the layout study (research/experiments/cand-mapid.md, part B): classify every team-game of
// exp/mapid/cache/feat.jsonl (exp/mapid/extract.js) by map, true layout (a / b) and group, and compare the groups.
// Groups: top winner / top loser (top-vs-top games, data/top), ours (our online sets against the elite), elite vs us
// (the opponent side of those games). Values per team-game; medians [p25, p75] and means.
// usage (repository root): node exp/mapid/elite_ab.js [--map Schooltime] [--json out.json] [--by-set]
const fs = require('fs'), path = require('path');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const FILE = path.join(__dirname, 'cache', 'feat.jsonl');
const rows = []; const seen = new Set();
for (const l of fs.readFileSync(FILE, 'utf8').split('\n')) { if (!l.trim()) continue; const r = JSON.parse(l); if (seen.has(r.key)) continue; seen.add(r.key); rows.push(r); }
const sum = (a, i, j) => { let s = 0; for (let b = i; b < j; b++) s += a[b] || 0; return s; };
const med = xs => { if (!xs.length) return null; const s = xs.slice().sort((a, b) => a - b); return s[Math.floor((s.length - 1) / 2)]; };
const q = (xs, p) => { if (!xs.length) return null; const s = xs.slice().sort((a, b) => a - b); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
const mean = xs => xs.length ? xs.reduce((s, v) => s + v, 0) / xs.length : null;
// one team-game -> features
function feat(g, tm) {
  const T = g[tm], O = g[tm === 'A' ? 'B' : 'A'], st = T.st, fl = T.fl, x = T.x;
  const at = (a, r) => a[Math.min(50, r / 10)];
  const turns = (i, j) => sum(x.hOwn, i, j) + sum(x.hEnemy, i, j) + sum(x.hNeutral, i, j);
  const elim = st.units[50] === 0, oppElim = O.st.units[50] === 0;
  const kids = x.splits100.map(s => s[1]);
  return {
    won: g.winner === tm ? 1 : 0, elim: elim ? 1 : 0, oppElim: oppElim ? 1 : 0, rounds: g.rounds, G: elim ? 0 : st.king[50],
    u10: at(st.units, 10), u20: at(st.units, 20), u30: at(st.units, 30), u50: at(st.units, 50), u100: at(st.units, 100), u150: at(st.units, 150), u200: at(st.units, 200), u300: at(st.units, 300),
    L50: at(st.total, 50), L100: at(st.total, 100), L200: at(st.total, 200), L300: at(st.total, 300), K100: at(st.king, 100), K300: at(st.king, 300),
    sp0_50: sum(fl.split_n, 0, 5), sp50_100: sum(fl.split_n, 5, 10), sp100_200: sum(fl.split_n, 10, 20), sp200_300: sum(fl.split_n, 20, 30),
    firstSplit: x.firstSplit === null ? 999 : x.firstSplit, kid2: kids.filter(k => k === 2).length, kidMean: kids.length ? mean(kids) : null,
    nat0_100: sum(fl.eat_nat, 0, 10), nat100_250: sum(fl.eat_nat, 10, 25), natAll: sum(fl.eat_nat, 0, 50),
    natOwn0_100: sum(fl.nat_own, 0, 10), natEn0_100: sum(fl.nat_enemy, 0, 10), natNe0_100: sum(fl.nat_neutral, 0, 10),
    natOwn100_250: sum(fl.nat_own, 10, 25), natEn100_250: sum(fl.nat_enemy, 10, 25), natNe100_250: sum(fl.nat_neutral, 10, 25),
    fount0_100: sum(x.eatF, 0, 10),
    dropsE0_150: sum(fl.eat_enemy, 0, 15), dropsO0_150: sum(fl.eat_own, 0, 15), dropsE_all: sum(fl.eat_enemy, 0, 50),
    ram0_150: sum(fl.dn_ram, 0, 15), rammed0_150: sum(fl.dn_rammed, 0, 15), ramAll: sum(fl.dn_ram, 0, 50), rammedAll: sum(fl.dn_rammed, 0, 50),
    bk0_150: sum(fl.bk_n, 0, 15), sac0_150: sum(fl.dn_sac, 0, 15), trap0_150: sum(fl.dn_trap, 0, 15), eBody0_150: sum(fl.dn_enemyBody, 0, 15),
    deaths0_150: sum(fl.dn_sac, 0, 15) + sum(fl.dn_trap, 0, 15) + sum(fl.dn_rammed, 0, 15) + sum(fl.dn_ram, 0, 15) + sum(fl.dn_enemyBody, 0, 15) + sum(fl.dn_allyHead, 0, 15),
    lostRammed0_150: sum(fl.dl_rammed, 0, 15), sprRam0_150: sum(fl.spr_ram, 0, 15), sprEsc0_150: sum(fl.spr_esc, 0, 15),
    enemyTerr0_100: turns(0, 10) ? sum(x.hEnemy, 0, 10) / turns(0, 10) : null, enemyTerr100_250: turns(10, 25) ? sum(x.hEnemy, 10, 25) / turns(10, 25) : null,
    ownTerr0_100: turns(0, 10) ? sum(x.hOwn, 0, 10) / turns(0, 10) : null,
    eNear0_100: turns(0, 10) ? sum(x.eNear, 0, 10) / turns(0, 10) : null, eNear100_250: turns(10, 25) ? sum(x.eNear, 10, 25) / turns(10, 25) : null,
    turns0_100: turns(0, 10),
  };
}
function groups(mapName) {
  const G = {};
  const put = (k, f) => (G[k] = G[k] || []).push(f);
  for (const g of rows) {
    if (g.map !== mapName || !(g.layout === 'a' || g.layout === 'b')) continue;
    if (Object.values(g.chk || {}).some(v => v)) continue;           // reconstruction checks must be 0
    if (g.src === 'top') {
      for (const tm of ['A', 'B']) { const f = feat(g, tm); f.team = g['team' + tm]; f.set = 'top'; put(`${g.layout}|top ${f.won ? 'winner' : 'loser'}`, f); put(`${g.layout}|top all`, f); }
    } else {
      const us = g.us, them = us === 'A' ? 'B' : 'A';
      const f = feat(g, us); f.set = g.set; f.opp = g.opp; put(`${g.layout}|ours`, f);
      const e = feat(g, them); e.set = g.set; e.opp = g.opp; put(`${g.layout}|elite vs us`, e);
    }
  }
  return G;
}
const KEYS = [
  ['won', '이김', 'm'], ['elim', '전멸당함', 'm'], ['oppElim', '상대를 전멸시킴', 'm'], ['rounds', '경기 길이', 'q'], ['G', '끝 최장(전멸 0)', 'q'],
  ['u10', '드래곤 수 r10', 'q'], ['u20', 'r20', 'q'], ['u30', 'r30', 'q'], ['u50', 'r50', 'q'], ['u100', 'r100', 'q'], ['u200', 'r200', 'q'], ['u300', 'r300', 'q'],
  ['L50', '몸 합 r50', 'q'], ['L100', 'r100', 'q'], ['L200', 'r200', 'q'], ['L300', 'r300', 'q'], ['K100', '최장 r100', 'q'], ['K300', '최장 r300', 'q'],
  ['sp0_50', '분열 r0–49', 'q'], ['sp50_100', '분열 r50–99', 'q'], ['sp100_200', '분열 r100–199', 'q'], ['firstSplit', '첫 분열 라운드', 'q'], ['kidMean', 'r<100 새끼 길이 평균', 'm'],
  ['nat0_100', '자연 진주 먹음 r0–99', 'q'], ['natOwn0_100', '  우리 영토', 'm'], ['natNe0_100', '  중립', 'm'], ['natEn0_100', '  상대 영토', 'm'], ['fount0_100', '  샘(간격 평균 ≤12)', 'm'],
  ['nat100_250', '자연 진주 r100–249', 'q'], ['natOwn100_250', '  우리 영토', 'm'], ['natNe100_250', '  중립', 'm'], ['natEn100_250', '  상대 영토', 'm'],
  ['dropsE0_150', '상대 사망 진주 먹음 r0–149', 'm'], ['dropsO0_150', '우리 사망 진주 먹음 r0–149', 'm'],
  ['ram0_150', '머리로 박음(같이 죽음) r0–149', 'm'], ['rammed0_150', '박힘 r0–149', 'm'], ['bk0_150', '상대가 우리 몸에 박아 죽음 r0–149', 'm'],
  ['deaths0_150', '사망 r0–149', 'm'], ['sac0_150', '  희생', 'm'], ['trap0_150', '  갇힘', 'm'], ['eBody0_150', '  적 몸', 'm'],
  ['enemyTerr0_100', '머리가 상대 영토에 있던 턴 r0–99', 'm%'], ['enemyTerr100_250', '  r100–249', 'm%'], ['eNear0_100', '적 머리 체비셰프 3 안 턴 r0–99', 'm%'], ['eNear100_250', '  r100–249', 'm%'],
];
function fmt(xs, how) {
  const v = xs.filter(x => x !== null && x !== undefined);
  if (!v.length) return '–';
  if (how === 'm') return (Math.round(mean(v) * 100) / 100).toString();
  if (how === 'm%') return Math.round(100 * mean(v)) + '%';
  return `${med(v)} [${q(v, 0.25)}, ${q(v, 0.75)}]`;
}
const maps = (opt('map', 'Schooltime,Devil')).split(',');
const out = {};
for (const m of maps) {
  const G = groups(m);
  const cols = ['a|top winner', 'b|top winner', 'a|top loser', 'b|top loser', 'a|ours', 'b|ours', 'a|elite vs us', 'b|elite vs us'];
  console.log(`\n## ${m}\n`);
  console.log(`| 지표 | ${cols.map(c => `${c.replace('|', ' ')} (${(G[c] || []).length})`).join(' | ')} |`);
  console.log(`|---|${cols.map(() => '---:').join('|')}|`);
  for (const [k, label, how] of KEYS) console.log(`| ${label} | ${cols.map(c => fmt((G[c] || []).map(f => f[k]), how)).join(' | ')} |`);
  out[m] = Object.fromEntries(Object.entries(G).map(([k, v]) => [k, v.length]));
  if (argv.includes('--by-set')) {
    for (const lay of ['a', 'b']) {
      const xs = G[lay + '|ours'] || []; const bySet = {};
      for (const f of xs) (bySet[f.set] = bySet[f.set] || []).push(f);
      console.log(`\n${m} ${lay}: ours by set`);
      for (const [s, a] of Object.entries(bySet)) console.log(`  ${s}: n ${a.length}, elim ${fmt(a.map(f => f.elim), 'm')}, won ${fmt(a.map(f => f.won), 'm')}, u30 ${fmt(a.map(f => f.u30), 'q')}, u100 ${fmt(a.map(f => f.u100), 'q')}, L100 ${fmt(a.map(f => f.L100), 'q')}, nat0_100 ${fmt(a.map(f => f.nat0_100), 'q')}, G ${fmt(a.map(f => f.G), 'q')}`);
    }
  }
}
if (opt('json')) fs.writeFileSync(opt('json'), JSON.stringify(out, null, 1));
