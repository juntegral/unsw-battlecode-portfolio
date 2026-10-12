#!/usr/bin/env node
'use strict';
// report_pxking.js — tables for research/experiments/online-analysis-pxking.md (px-king-v2-online vs the 210 baseline games
// and the top-team snapshot games on the same maps).
// usage: node exp/online-analysis/report_pxking.js --study <study.jsonl> --top <top.jsonl>
//   study.jsonl: exp/online-analysis/study.js (default sets); top.jsonl: study.js --top (winner = side 0).
const L = require('./lib.js');
const { ELIM, R500, boot, paired, sum, mean, quant, median, fx, sg, ci, pc, table, flowAt, inProg } = L;
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const G = L.readJsonl(opt('study'));
const TOP = opt('top') ? L.readJsonl(opt('top')) : [];
const BASE = G.filter(g => L.group(g.set) === 'base'), PX = G.filter(g => L.group(g.set) === 'pxking');
const P = (...a) => console.log(...a);
const key = g => `${g.opp}|${g.map}`;
const q = (a, d = 0) => a.length ? `${fx(median(a), d)} [${fx(quant(a, 0.25), d)}–${fx(quant(a, 0.75), d)}]` : '–';
const SEL = [['Devil', g => g.map === 'Devil'], ['Trophy', g => g.map === 'Trophy'], ['PD6', g => g.variant === 'PD6'], ['PD10', g => g.variant === 'PD10'], ['Queen Of Spades', g => g.map === 'Queen Of Spades'],
  ['Default', g => g.map === 'Default'], ['Autarky', g => g.map === 'Autarky'], ['Portals', g => g.map === 'Portals'], ['Schooltime', g => g.map === 'Schooltime'], ['Slithery Fight', g => g.map === 'Slithery Fight'], ['Trauma', g => g.map === 'Trauma']];
const cls = (g, si, c, f = 'n') => ((g.a.cls2[si] || {})[c] || {})[f] || 0;
const eatSum = (g, si, k) => sum(g.a.eat[si][k]);

// ---------------------------------------------------------------------------------------------------------------
P('## A. 지도별 결과 (px-king 7판 대 기준 21판)');
{
  const rows = [];
  for (const [label, sel] of SEL) for (const [name, set] of [['기준', BASE], ['px-king', PX]]) {
    const x = set.filter(sel); if (!x.length) continue;
    rows.push([label, name, x.length, x.filter(g => g.win).length, x.filter(g => g.elimThem).length, x.filter(g => g.elimUs).length, q(x.filter(g => g.elimUs).map(g => g.a.rounds - 1)),
      fx(mean(x.map(g => g.G)), 1), fx(mean(x.map(g => g.theirLongest)), 1), fx(mean(x.map(g => g.total)), 1), fx(mean(x.map(g => g.theirTotal)), 1)]);
  }
  P(table(['지도', '묶음', '판', '승', '상대 전멸', '우리 전멸', '우리 전멸 라운드', 'G 평균', '상대 최장', '우리 몸 합', '상대 몸 합'], rows));
  const rows2 = [];
  for (const m of [...ELIM, ...R500]) { const s = paired(BASE.filter(g => g.map === m), PX.filter(g => g.map === m), key, g => g.G), w = paired(BASE.filter(g => g.map === m), PX.filter(g => g.map === m), key, g => g.win); rows2.push([m, s.keys, ci(s), sg(w.mean, 2)]); }
  P('\n짝 비교(팀×지도, online_compare.js 방식):'); P(table(['지도', '짝', 'G 차 [95%]', '승 차'], rows2));
  const rows3 = [];
  for (const [label, sel] of [['전체 70짝', () => true], ['Autarky·PD 제외 56짝', g => g.map !== 'Autarky' && g.map !== 'Prisoners Dilemma'], ['Autarky·PD 14짝', g => g.map === 'Autarky' || g.map === 'Prisoners Dilemma']]) {
    const s1 = paired(BASE.filter(sel), PX.filter(sel), key, g => g.G), s2 = paired(BASE.filter(sel), PX.filter(sel), key, g => g.win), s3 = paired(BASE.filter(sel), PX.filter(sel), key, g => g.theirLongest);
    rows3.push([label, s1.keys, `${fx(s1.meanA, 2)} → ${fx(s1.meanB, 2)}, ${ci(s1)}`, `${fx(s2.meanA, 3)} → ${fx(s2.meanB, 3)}, ${ci(s2, 3)}`, ci(s3)]);
  }
  P('\n묶음 짝 비교:'); P(table(['범위', '짝', 'G 기준 → px-king, 차 [95%]', '승', '상대 최장 차'], rows3));
}

P('\n## B. px-king이 이긴 판');
{
  const rows = PX.filter(g => g.win).map(g => [g.gameId, g.map + (g.variant ? ' ' + g.variant : ''), `${g.opp} ${g.oppName}`, g.a.endReason === 'teamEliminated' ? `상대 전멸 r${g.a.rounds - 1}` : '500라운드',
    `${g.a.final[0].units}/${g.a.final[0].total}/${g.a.final[0].longest}`, `${g.a.final[1].units}/${g.a.final[1].total}/${g.a.final[1].longest}`,
    `${flowAt(g, 0, 'u', 100)}/${flowAt(g, 1, 'u', 100)}`, `${flowAt(g, 0, 'u', 300)}/${flowAt(g, 1, 'u', 300)}`, `${flowAt(g, 0, 'l', 400)}/${flowAt(g, 1, 'l', 400)}`]);
  P(table(['경기', '지도', '상대', '끝', '끝 우리 수/합/최장', '끝 상대 수/합/최장', '수 r100 우리/상대', '수 r300', '최장 r400 우리/상대'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## C. 이기기 시작한 지도의 기전 (판당 평균, 우리 : 상대)');
{
  const rows = [];
  for (const [label, sel] of [['Portals', g => g.map === 'Portals'], ['Default', g => g.map === 'Default'], ['Devil', g => g.map === 'Devil'], ['Slithery Fight', g => g.map === 'Slithery Fight'],
    ['Autarky', g => g.map === 'Autarky'], ['PD6', g => g.variant === 'PD6'], ['PD10', g => g.variant === 'PD10']]) for (const [name, set] of [['기준', BASE], ['px-king', PX]]) {
    const x = set.filter(sel); if (!x.length) continue;
    const r = (f, d = 1) => fx(mean(x.map(f)), d);
    rows.push([label, name, x.length,
      `${r(g => sum(g.a.eat[0].nat), 0)} : ${r(g => sum(g.a.eat[1].nat), 0)}`,
      `${r(g => eatSum(g, 0, 'own') + eatSum(g, 0, 'opp'), 0)} : ${r(g => eatSum(g, 1, 'own') + eatSum(g, 1, 'opp'), 0)}`,
      `${r(g => g.a.turns[0], 0)} : ${r(g => g.a.turns[1], 0)}`,
      `${r(g => g.a.splitsN[0], 0)} : ${r(g => g.a.splitsN[1], 0)}`,
      r(g => cls(g, 1, 'H-rammed') + cls(g, 1, 'O-enemy')), r(g => cls(g, 1, 'H-attack')), r(g => cls(g, 0, 'H-rammed')),
      `${r(g => g.a.portalSteps[0], 0)} : ${r(g => g.a.portalSteps[1], 0)}`]);
  }
  P(table(['지도', '묶음', '판', '자연 진주', '주검 진주', '드래곤 턴', '분열', '우리가 잡은 적(우리가 박음 + 우리 몸에 박음)', '적이 우리 머리를 박고 같이 죽음', '우리가 박힘', '포털 통과 걸음'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## D. 흐름 (진행 중인 판 중앙값: 우리 수/합/최장 — 상대 수/합/최장, 괄호는 판 수)');
const R = [0, 10, 20, 50, 100, 150, 200, 300, 400, 450, 500];
const flowRows = (sets, sel) => sets.map(([name, set]) => { const x = set.filter(sel); return [name, ...R.map(r => { const y = x.filter(g => inProg(g, r)); if (!y.length) return '–'; const m = (si, k) => fx(median(y.map(g => flowAt(g, si, k, r))), 0); return `${m(0, 'u')}/${m(0, 't')}/${m(0, 'l')} — ${m(1, 'u')}/${m(1, 't')}/${m(1, 'l')} (${y.length})`; })]; });
for (const [label, sel, tsel] of [['Autarky', g => g.map === 'Autarky', g => g.map === 'Autarky'], ['PD6', g => g.variant === 'PD6', g => g.variant === 'PD6'], ['PD10', g => g.variant === 'PD10', g => g.variant === 'PD10'],
  ['Portals', g => g.map === 'Portals', g => g.map === 'Portals'], ['Slithery Fight', g => g.map === 'Slithery Fight', g => g.map === 'Slithery Fight'], ['Default', g => g.map === 'Default', g => g.map === 'Default'], ['Devil', g => g.map === 'Devil', g => g.map === 'Devil']]) {
  P(`\n${label} (상위권은 승자 — 패자)`);
  P(table(['묶음', ...R.map(r => 'r' + r)], flowRows([['기준', BASE], ['px-king', PX], ['상위권끼리', TOP.filter(tsel)]], sel)));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## E. Autarky와 Prisoners Dilemma: 우리 사망 (판당, 우리 쪽 분류)');
{
  const C = ['H-rammed', 'trapped', 'stub', 'feed', 'W/S', 'A', 'ally', 'H-attack', 'O-enemy'];
  const rows = [];
  for (const [label, sel] of [['Autarky', g => g.map === 'Autarky'], ['PD6', g => g.variant === 'PD6'], ['PD10', g => g.variant === 'PD10']]) for (const [name, set] of [['기준', BASE], ['px-king', PX], ['상위권 승자', TOP]]) {
    const x = set.filter(sel); if (!x.length) continue;
    rows.push([label, name, x.length, ...C.map(c => `${fx(mean(x.map(g => cls(g, 0, c))), 1)} (${fx(mean(x.map(g => cls(g, 0, c, 'len'))), 0)})`),
      `${fx(mean(x.map(g => cls(g, 0, 'W/S') + cls(g, 0, 'A'))), 1)} (${fx(mean(x.map(g => cls(g, 0, 'W/S', 'len') + cls(g, 0, 'A', 'len'))), 0)})`]);
  }
  P(table(['지도', '묶음', '판', ...C.map(c => c + ' 건수 (길이)'), '희생 W/S+A 건수 (길이)'], rows));
  P('- 분류는 tools/baseline_study.js cls2다. 우리 쪽: H-rammed 적이 박음, trapped 빈 이웃 0(탈출 분열 조각 제외), stub 탈출 분열 조각, feed 왕 먹이기, W/S·A 빈 이웃이 있는 해초·자기 몸·무효(희생), ally 아군 충돌, H-attack 우리가 박음, O-enemy 적 몸.');
  P('- 상위권 승자는 우리 쪽 분류 규칙을 그대로 쓴다(표시가 없으므로 stub·feed는 0이고, 그 사망은 trapped·W/S·A로 잡힌다).');
}

P('\n## F. 길이별 사망 시기 (px-king, Autarky·PD: 창별 적이 박음 / 갇힘 / 빈 이웃 있는 자해, 판당)');
{
  const rows = [];
  for (const [label, sel] of [['Autarky', g => g.map === 'Autarky'], ['PD6', g => g.variant === 'PD6'], ['PD10', g => g.variant === 'PD10']]) for (const [name, set] of [['px-king', PX], ['기준', BASE], ['상위권 승자', TOP]]) {
    const x = set.filter(sel); if (!x.length) continue;
    const w = c => [0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(i => fx(mean(x.map(g => ((g.x.deathsWin.us || {})[c] || [])[i] || 0)), 1)).join(' ');
    rows.push([label, name, x.length, w('rammed'), w('trapped'), w('selfFree')]);
  }
  P(table(['지도', '묶음', '판', '적이 박음 (50라운드 창 0–9)', '갇힘', '빈 이웃 있는 자해'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## G. 통로 샘물 (Autarky, PD): 판당 평균');
{
  const rows = [];
  for (const [label, sel] of [['Autarky', g => g.map === 'Autarky'], ['PD6', g => g.variant === 'PD6'], ['PD10', g => g.variant === 'PD10']]) for (const [name, set] of [['기준', BASE], ['px-king', PX], ['상위권 승자(우리 자리)', TOP]]) {
    const x = set.filter(sel).filter(g => g.x.fountains); if (!x.length) continue;
    const f = x.map(g => g.x.fountains);
    rows.push([label, name, x.length, fx(mean(f.map(z => z.us.spawns)), 1), fx(mean(f.map(z => z.us.natOwn)), 1), fx(mean(f.map(z => z.them.natOther)), 1), fx(mean(f.map(z => z.us.corOwn)), 1),
      fx(mean(f.map(z => z.us.natOther)), 1), fx(mean(f.map(z => z.us.natElse)), 1), fx(mean(f.map(z => z.them.spawns)), 1), fx(mean(f.map(z => z.them.natOwn)), 1), fx(mean(f.map(z => z.them.natElse)), 1)]);
  }
  P(table(['지도', '묶음', '판', '우리 샘물 생성', '우리 샘물 자연: 우리가 먹음', '우리 샘물 자연: 상대가 먹음', '우리 샘물 주검: 우리', '상대 샘물 자연: 우리가 먹음', '샘물 밖 자연: 우리', '상대 샘물 생성', '상대 샘물 자연: 상대', '샘물 밖 자연: 상대'], rows));
}

P('\n## H. 시작 계통 (가장 긴 시작 드래곤, 분열 때 더 긴 조각): 길이 (판 평균)');
{
  const RR = [0, 10, 25, 50, 100, 200, 300, 400, 500];
  const rows = [];
  for (const [label, sel] of [['Autarky', g => g.map === 'Autarky'], ['PD6', g => g.variant === 'PD6'], ['PD10', g => g.variant === 'PD10']]) for (const [name, set] of [['기준', BASE], ['px-king', PX], ['상위권 승자', TOP]]) {
    const x = set.filter(sel); if (!x.length) continue;
    const lin = x.map(g => g.x.lineage);
    rows.push([label, name, x.length, ...RR.map(r => fx(mean(lin.map(l => l.lens[r] || 0)), 1)), `${lin.filter(l => l.exitRound !== null).length} (${q(lin.filter(l => l.exitRound !== null).map(l => l.exitRound))})`,
      `${lin.filter(l => l.death).length}: ${Object.entries(lin.filter(l => l.death).reduce((o, l) => { o[l.death.cause] = (o[l.death.cause] || 0) + 1; return o; }, {})).map(([k, v]) => k + ' ' + v).join(', ')}`,
      q(lin.filter(l => l.death).map(l => l.death.r))]);
  }
  P(table(['지도', '묶음', '판', ...RR.map(r => 'r' + r), '통로를 벗어난 판 (라운드)', '계통 사망', '계통 사망 라운드'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## I. 왕(그 순간 우리 최장) 사망: 길이 8 이상 (판당)');
{
  const rows = [];
  for (const [label, sel] of [['Autarky', g => g.map === 'Autarky'], ['PD', g => g.map === 'Prisoners Dilemma'], ['Portals', g => g.map === 'Portals'], ['Slithery Fight', g => g.map === 'Slithery Fight'], ['500라운드형', g => g.type === 'r500'], ['전멸형', g => g.type === 'elim']]) for (const [name, set] of [['기준', BASE], ['px-king', PX]]) {
    const x = set.filter(sel); if (!x.length) continue;
    const kd = x.flatMap(g => g.x.kingDeaths);
    const c = {}; for (const d of kd) c[d.cause] = (c[d.cause] || 0) + 1;
    rows.push([label, name, x.length, fx(kd.length / x.length, 2), Object.entries(c).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${v}`).join(', '), q(kd.map(d => d.len)), q(kd.map(d => d.r))]);
  }
  P(table(['범위', '묶음', '판', '왕 사망/판', '원인', '길이', '라운드'], rows));
  P('- 원인(extra 분류): rammed 적이 박음, trapped 빈 이웃 0, selfFree 빈 이웃 있는 자해(먹이 넘기기 포함), ramEnemy 우리가 박음, ally 아군 충돌, enemyBody 적 몸.');
}

P('\n## J. 상위권끼리: 지도별 승자·패자 최장과 수 (중앙값, 진행 중인 판)');
{
  const RR = [100, 200, 300, 400, 450, 500];
  const rows = [];
  for (const [label, sel] of [['Autarky', g => g.map === 'Autarky'], ['PD6', g => g.variant === 'PD6'], ['PD10', g => g.variant === 'PD10'], ['Portals', g => g.map === 'Portals'], ['Slithery Fight', g => g.map === 'Slithery Fight'], ['Default', g => g.map === 'Default'], ['Devil', g => g.map === 'Devil']]) {
    const x = TOP.filter(sel);
    rows.push([label, x.length, x.filter(g => g.a.endReason === 'teamEliminated').length, ...RR.map(r => { const y = x.filter(g => inProg(g, r)); if (!y.length) return '–'; const m = (si, k) => fx(median(y.map(g => flowAt(g, si, k, r))), 0); return `${m(0, 'l')}/${m(0, 'u')} — ${m(1, 'l')}/${m(1, 'u')} (${y.length})`; })]);
  }
  P(table(['지도', '판', '전멸', ...RR.map(r => `r${r} 최장/수 승자 — 패자`)], rows));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## K. 접촉 사망과 출생(분열): 판당 (우리 : 상대)');
{
  const contact = (g, side) => ['rammed', 'enemyBody', 'ramEnemy'].reduce((s, c) => s + ((g.x.deathsSum[side][c] || {}).n || 0), 0);
  const rows = [];
  for (const [label, sel] of [['Autarky', g => g.map === 'Autarky'], ['PD6', g => g.variant === 'PD6'], ['PD10', g => g.variant === 'PD10'], ['Default', g => g.map === 'Default'], ['Devil', g => g.map === 'Devil'], ['Portals', g => g.map === 'Portals'], ['Slithery Fight', g => g.map === 'Slithery Fight']]) for (const [name, set] of [['기준', BASE], ['px-king', PX]]) {
    const x = set.filter(sel); if (!x.length) continue;
    rows.push([label, name, x.length, `${fx(mean(x.map(g => contact(g, 'us'))), 1)} : ${fx(mean(x.map(g => contact(g, 'them'))), 1)}`, `${fx(mean(x.map(g => g.a.splitsN[0])), 0)} : ${fx(mean(x.map(g => g.a.splitsN[1])), 0)}`,
      `${fx(mean(x.map(g => sum(g.a.eat[0].nat))), 0)} : ${fx(mean(x.map(g => sum(g.a.eat[1].nat))), 0)}`]);
  }
  P(table(['지도', '묶음', '판', '접촉 사망(적 머리·몸)', '분열', '자연 진주'], rows));
  P('\npx-king이 이긴 판의 접촉과 경제:');
  const r2 = PX.filter(g => g.win).map(g => {
    const w = (side, lo, hi) => ['rammed', 'enemyBody', 'ramEnemy'].reduce((s, c) => { const a = (g.x.deathsWin[side] || {})[c] || []; let t = 0; for (let i = lo; i <= hi; i++) t += a[i] || 0; return s + t; }, 0);
    return [g.gameId, g.map, g.opp, `${w('us', 0, 1)} : ${w('them', 0, 1)}`, `${w('us', 0, 9)} : ${w('them', 0, 9)}`, `${flowAt(g, 1, 'u', 50)} / ${flowAt(g, 1, 'u', 100)} / ${flowAt(g, 1, 'u', 200)}`, `${sum(g.a.eat[0].nat)} : ${sum(g.a.eat[1].nat)}`];
  });
  P(table(['경기', '지도', '상대', '접촉 사망 r0–99 우리 : 상대', '전체', '상대 수 r50 / r100 / r200', '자연 진주 우리 : 상대'], r2));
  P('\n같은 상대(306 Cutlery)의 기준 판: 상대 수 r50 / r100 / r200, 자연 진주 우리 : 상대');
  const r3 = BASE.filter(g => g.opp === 306 && (g.map === 'Default' || g.map === 'Devil')).map(g => [g.set, g.map, g.win ? '승' : '패', `${flowAt(g, 1, 'u', 50)} / ${flowAt(g, 1, 'u', 100)} / ${flowAt(g, 1, 'u', 200)}`, `${sum(g.a.eat[0].nat)} : ${sum(g.a.eat[1].nat)}`]);
  P(table(['세트', '지도', '결과', '상대 수', '자연 진주'], r3));
}

// ---------------------------------------------------------------------------------------------------------------
// Local check (read only): px1 = proxy_king v2 copy, evaluated by the base-px agent (exp/base-px1, exp/base-px1-s3).
P('\n## L. 로컬: px1(= proxy_king v2) 대 흉내 상대·r1(고리를 쓰는 기준 봇), Autarky와 Prisoners Dilemma(6마리 판본 지도)');
{
  const fs = require('fs'), path = require('path');
  const rows = [];
  for (const lab of ['base-px1', 'base-px1-s3']) {
    const f = path.join(L.ROOT, 'exp', lab, 'rows.jsonl'); if (!fs.existsSync(f)) continue;
    for (const l of fs.readFileSync(f, 'utf8').split('\n')) { if (!l.trim()) continue; const r = JSON.parse(l); if (r.map === 'autarky' || r.map === 'prisoners_dilemma') rows.push(r); }
  }
  const out = [];
  for (const m of ['autarky', 'prisoners_dilemma']) for (const o of ['proxy_swarm', 'proxy_elim', 'proxy_king', 'r1']) {
    const x = rows.filter(r => r.map === m && r.opp === o); if (!x.length) continue;
    out.push([m, o, x.length, x.filter(r => r.won).length, fx(mean(x.map(r => r.G)), 1)]);
  }
  P(table(['지도', '상대', '판(시드 1–3, 양 진영)', 'px1 승', 'px1 G 평균'], out));
}
