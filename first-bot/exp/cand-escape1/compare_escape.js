#!/usr/bin/env node
'use strict';
// compare_escape.js — paired comparison for the escape-split candidates (cand-escape1, cand-escape2, ...).
// usage: node exp/cand-escape1/compare_escape.js <baseline label> <candidate label> [--study-base f.json --study-cand f.json]
//   Pairs tools/eval.js rows by key opp:map:side:seed. For G, win (percentage points) and survival (pp): mean difference with a
//   paired 95% interval (mean +- 1.96 SD/sqrt(n)), overall, autarky, prisoners_dilemma, the other eight maps, per opponent
//   and per map; the map-cluster bootstrap of tools/eval.js for overall G. Win flips and elimination wins are counted.
//   With escape_study.js outputs (--study-base/--study-cand) it adds the mechanism table per map group: escape and peel
//   splits per game, natural and corpse pearls eaten by our team, the start lineage's length by round, the round its head
//   first leaves the start corridor, loops (escape-split chains of 5 or more).
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const pos = argv.filter((a, i) => !a.startsWith('--') && !(i > 0 && argv[i - 1].startsWith('--')));
const [baseL, candL] = pos;
const rowsOf = l => { const f = fs.existsSync(l) ? path.join(l, 'rows.jsonl') : path.join(ROOT, 'exp', l, 'rows.jsonl'); const seen = new Set(); return fs.readFileSync(f, 'utf8').trim().split('\n').map(x => JSON.parse(x)).filter(r => r.G !== undefined && !seen.has(r.key) && seen.add(r.key)); };
const B = new Map(rowsOf(baseL).map(r => [r.key, r])), C = rowsOf(candL).filter(r => B.has(r.key));
const mean = a => a.reduce((s, x) => s + x, 0) / Math.max(1, a.length);
const sd = a => { const m = mean(a); return Math.sqrt(a.reduce((s, x) => s + (x - m) ** 2, 0) / Math.max(1, a.length - 1)); };
const f = (x, d = 2) => (x >= 0 ? '+' : '') + x.toFixed(d);
const fci = (a, d = 2) => { const m = mean(a), h = 1.96 * sd(a) / Math.sqrt(Math.max(1, a.length)); return `${f(m, d)} [${f(m - h, d)}, ${f(m + h, d)}]`; };
function boot(P) {
  const maps = [...new Set(P.map(p => p.map))].map(m => P.filter(p => p.map === m));
  let s = 20260927; const rnd = () => (s = (Math.imul(s, 1103515245) + 12345) >>> 0) / 4294967296; const reps = [];
  for (let k = 0; k < 4000; k++) { const pick = maps.map(() => maps[Math.floor(rnd() * maps.length)]).flat(); reps.push(mean(pick.map(p => p.d))); }
  reps.sort((a, b) => a - b); return [reps[100], reps[3899]];
}
const pairs = C.map(r => { const b = B.get(r.key); return { key: r.key, opp: r.opp, map: r.map, side: r.side, d: r.G - b.G, gb: b.G, gc: r.G, wb: +b.won, wc: +r.won, ab: +b.alive, ac: +r.alive, eb: b.endReason === 'teamEliminated' && b.won, ec: r.endReason === 'teamEliminated' && r.won }; });
const table = (h, rs) => ['| ' + h.join(' | ') + ' |', '|' + h.map(() => '---').join('|') + '|', ...rs.map(r => '| ' + r.join(' | ') + ' |')].join('\n');
const grp = (name, P) => [name, P.length, mean(P.map(p => p.gb)).toFixed(2), mean(P.map(p => p.gc)).toFixed(2), fci(P.map(p => p.d)),
  `${P.reduce((s, p) => s + p.wb, 0)}→${P.reduce((s, p) => s + p.wc, 0)}`, fci(P.map(p => (p.wc - p.wb) * 100), 1),
  `${P.reduce((s, p) => s + p.ab, 0)}→${P.reduce((s, p) => s + p.ac, 0)}`, fci(P.map(p => (p.ac - p.ab) * 100), 1),
  `${P.filter(p => p.wb && !p.wc).length}/${P.filter(p => !p.wb && p.wc).length}`, `${P.filter(p => p.eb).length}→${P.filter(p => p.ec).length}`];
const H = ['범위', '판', 'G 기준', 'G 후보', 'G 차이 [95%]', '승', '승 차이 %p [95%]', '생존', '생존 차이 %p [95%]', '승→패/패→승', '전멸승'];
const TARGET = ['autarky', 'prisoners_dilemma'];
const out = [];
const bt = boot(pairs);
out.push(`${baseL} → ${candL}: 짝 ${pairs.length}판. 전체 G 차이의 지도 묶음 부트스트랩 95% [${f(bt[0])}, ${f(bt[1])}], 경기별 G 차이 SD ${sd(pairs.map(p => p.d)).toFixed(1)}.`);
out.push('');
const rs = [grp('전체', pairs), grp('autarky', pairs.filter(p => p.map === 'autarky')), grp('prisoners_dilemma', pairs.filter(p => p.map === 'prisoners_dilemma')),
  grp('두 지도 합', pairs.filter(p => TARGET.includes(p.map))), grp('나머지 8개 지도', pairs.filter(p => !TARGET.includes(p.map)))];
for (const o of [...new Set(pairs.map(p => p.opp))]) rs.push(grp(o, pairs.filter(p => p.opp === o)));
out.push(table(H, rs));
out.push('');
out.push(table(['지도', ...H.slice(1)], [...new Set(pairs.map(p => p.map))].sort().map(m => grp(m, pairs.filter(p => p.map === m)))));
const sb = opt('--study-base', null), sc = opt('--study-cand', null);
if (sb && sc) {
  const gA = new Map(JSON.parse(fs.readFileSync(sb)).games.map(g => [g.key, g])), gC = new Map(JSON.parse(fs.readFileSync(sc)).games.map(g => [g.key, g]));
  const keys = pairs.map(p => p.key).filter(k => gA.has(k) && gC.has(k));
  const groups = [['전체', () => true], ['autarky', g => g.map === 'autarky'], ['prisoners_dilemma', g => g.map === 'prisoners_dilemma'], ['나머지 8개 지도', g => !TARGET.includes(g.map)]];
  const peel = g => (g.otherSplits && g.otherSplits['peel-split']) || 0;
  const dip = g => (g.otherSplits && g.otherSplits['dip-split']) || 0;
  const metrics = [
    ['탈출 분열(escape-split)', g => g.escapeSplits], ['벗기기 분열(peel-split)', peel], ['담그기 표시 분열(dip-split)', dip], ['정책 분열', g => g.policySplits],
    ['고리(탈출 사슬 5회 이상)', g => g.loops], ['고리 속 분열', g => g.loopSplits],
    ['자연 진주 먹음', g => g.eatNat], ['주검 진주 먹음', g => g.eatCorpse], ['시작 계통이 먹은 자연 진주', g => g.eatNatLin],
    ['통로 샘물 자연 생성', g => g.fountainSpawns || 0], ['통로 샘물에서 우리가 먹은 자연 진주', g => g.eatNatFountain || 0],
    ['통로 샘물 밖에서 먹은 자연 진주', g => g.eatNat - (g.eatNatFountain || 0)], ['상대가 우리 통로 샘물에서 먹음', g => g.oppEatFountain || 0],
    ['우리 사망 수', g => g.deaths], ['우리 사망 길이 합', g => g.deathLen]];
  out.push('');
  out.push('기전 (판당 평균 기준→후보, 짝 차이 [95%]):');
  const rows2 = metrics.map(([name, fn]) => [name, ...groups.map(([, sel]) => { const ks = keys.filter(k => sel(gA.get(k))); return `${mean(ks.map(k => fn(gA.get(k)))).toFixed(1)}→${mean(ks.map(k => fn(gC.get(k)))).toFixed(1)} (${fci(ks.map(k => fn(gC.get(k)) - fn(gA.get(k))), 1)})`; })]);
  out.push(table(['지표', ...groups.map(g => g[0])], rows2));
  out.push('');
  out.push('시작 계통의 길이 (그 라운드 시작 직전, 죽었으면 0; 판 평균 기준→후보) 와 통로를 벗어난 라운드:');
  const rounds = [10, 25, 50, 100, 150, 200, 300, 400, 500];
  const rows3 = [];
  for (const [gname, sel] of groups.slice(1, 3)) {
    const ks = keys.filter(k => sel(gA.get(k)));
    rows3.push([gname, ...rounds.map(r => `${mean(ks.map(k => gA.get(k).linLen[r])).toFixed(1)}→${mean(ks.map(k => gC.get(k).linLen[r])).toFixed(1)}`),
      (() => { const ex = ks.map(k => gC.get(k).exitRound).filter(x => x !== null).sort((a, b) => a - b); const eb = ks.map(k => gA.get(k).exitRound).filter(x => x !== null); return `기준 ${eb.length}/${ks.length}판, 후보 ${ex.length}/${ks.length}판 (중앙값 ${ex.length ? ex[Math.floor(ex.length / 2)] : '-'})`; })()]);
  }
  out.push(table(['지도', ...rounds.map(r => 'r' + r), '통로 벗어남'], rows3));
}
console.log(out.join('\n'));
