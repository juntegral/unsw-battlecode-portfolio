#!/usr/bin/env node
'use strict';
// report_avoid6.js — tables for research/experiments/online-analysis-avoid6.md (cand-avoid6-online vs the 210 baseline games).
// usage: node exp/online-analysis/report_avoid6.js --study <study.jsonl> --follow <follow.json> [--corner <corner.json>]
// Inputs come from exp/online-analysis/study.js, follow.js and exp/cand-avoid1/corner_study.js (see the report, section 6).
const fs = require('fs');
const L = require('./lib.js');
const { ELIM, R500, boot, paired, sum, mean, quant, median, fx, sg, ci, pc, table, flowAt, inProg } = L;
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const G = L.readJsonl(opt('study'));
const FOL = opt('follow') ? JSON.parse(fs.readFileSync(opt('follow'), 'utf8')) : [];
const BASE = G.filter(g => L.group(g.set) === 'base'), CAND = G.filter(g => L.group(g.set) === 'avoid6');
const P = (...a) => console.log(...a);
const key = g => `${g.opp}|${g.map}`;
const escN = g => g.x.ind.esc;
const q = (a, d = 0) => a.length ? `${fx(median(a), d)} [${fx(quant(a, 0.25), d)}–${fx(quant(a, 0.75), d)}]` : '–';

// ---------------------------------------------------------------------------------------------------------------
P('## A. 검증');
const chk = { games: G.length, analyse: 0, extra: 0, final: 0, mass: 0 };
for (const g of G) { chk.analyse += Object.values(g.a.checks).filter(v => typeof v === 'number').reduce((s, v) => s + v, 0); chk.extra += g.x.chk.updates + g.x.chk.deaths; if (!g.a.finalMatch) chk.final++; for (const m of g.a.mass) if (!m.ok) chk.mass++; }
P(`경기 ${chk.games}판. analyse() 점검 합 ${chk.analyse}, extra() 머리·꼬리·사망 불일치 ${chk.extra}, 끝 상태 불일치 ${chk.final}, 질량 항등식 불일치 ${chk.mass}.`);
{
  const e = paired(BASE.filter(g => g.type === 'elim'), CAND.filter(g => g.type === 'elim'), key, g => g.G);
  const r = paired(BASE.filter(g => g.type === 'r500'), CAND.filter(g => g.type === 'r500'), key, g => g.G);
  P(`online_compare.js 재현: 전멸형 G ${ci(e)} (짝 ${e.keys}), 500라운드형 G ${ci(r)} (짝 ${r.keys}).`);
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## B. Prisoners Dilemma 판본 (시작 드래곤 6마리 / 10마리)');
{
  const rows = [];
  for (const [name, set] of [['기준 210판', BASE], ['cand-avoid6', CAND], ['px-king-v2', G.filter(g => L.group(g.set) === 'pxking')]]) {
    const pd = set.filter(g => g.map === 'Prisoners Dilemma');
    for (const v of ['PD6', 'PD10']) {
      const x = pd.filter(g => g.variant === v);
      rows.push([name, v, x.length, x.filter(g => g.win).length, x.filter(g => g.elimUs).length, fx(mean(x.map(g => g.G)), 1), x.map(g => g.opp).join(',')]);
    }
  }
  P(table(['묶음', '판본', '판', '승', '우리 전멸', 'G 평균', '상대 팀'], rows));
  const b6 = BASE.filter(g => g.variant === 'PD6'), b10 = BASE.filter(g => g.variant === 'PD10');
  const p6 = b6.filter(g => g.win).length / b6.length, p10 = b10.filter(g => g.win).length / b10.length;
  const qs = BASE.filter(g => g.map === 'Queen Of Spades'), pq = qs.filter(g => g.win).length / qs.length;
  const oth = BASE.filter(g => g.type === 'elim' && g.map !== 'Prisoners Dilemma' && g.map !== 'Queen Of Spades');
  const po = oth.filter(g => g.win).length / oth.length;
  const c6 = CAND.filter(g => g.variant === 'PD6').length, c10 = CAND.filter(g => g.variant === 'PD10').length;
  const exp = c6 * p6 + c10 * p10 + 7 * pq + 21 * po;
  P(`\n기준의 판본별 승률: PD6 ${b6.filter(g => g.win).length}/${b6.length}, PD10 ${b10.filter(g => g.win).length}/${b10.length}, Queen Of Spades ${qs.filter(g => g.win).length}/${qs.length}, 나머지 전멸형 3지도 ${oth.filter(g => g.win).length}/${oth.length}.`);
  P(`cand-avoid6의 판본 뽑기(PD6 ${c6}, PD10 ${c10})에 기준 승률을 넣은 전멸형 기대 승수 = ${fx(exp, 2)} (푸아송 P(0승) = ${fx(Math.exp(-exp), 2)}). 기준 한 세트(70판)의 전멸형 승은 ${BASE.filter(g => g.type === 'elim' && g.win).length}/3 = ${fx(BASE.filter(g => g.type === 'elim' && g.win).length / 3, 2)}.`);
  let pAll = 1; for (let i = 0; i < c10; i++) pAll *= 0.5; const comb = (n, k) => { let c = 1; for (let i = 0; i < k; i++) c = c * (n - i) / (i + 1); return c; };
  let tail = 0; for (let k = c10; k <= 7; k++) tail += comb(7, k) / 128;
  P(`판본이 반반으로 나온다면(상위권 스냅숏 PD6 24판, PD10 23판) 7판 중 PD10이 ${c10}판 이상일 확률 = ${fx(tail, 3)}.`);
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## C. 전멸형 지도 결과 (지도·판본별)');
const mapRows = (sets, maps) => {
  const rows = [];
  for (const [label, sel] of maps) for (const [name, set] of sets) {
    const x = set.filter(sel);
    if (!x.length) continue;
    const el = x.filter(g => g.elimUs);
    rows.push([label, name, x.length, x.filter(g => g.win).length, el.length, q(el.map(g => g.a.rounds - 1)), fx(mean(x.map(g => g.G)), 1), fx(mean(x.map(g => g.theirLongest)), 1),
      fx(mean(x.map(g => escN(g))), 1), x.filter(g => escN(g) > 0).length]);
  }
  return rows;
};
const ELIM_SEL = [['Devil', g => g.map === 'Devil'], ['Trophy', g => g.map === 'Trophy'], ['PD6', g => g.variant === 'PD6'], ['PD10', g => g.variant === 'PD10'],
  ['Queen Of Spades', g => g.map === 'Queen Of Spades'], ['Default', g => g.map === 'Default'], ['전멸형 전체', g => g.type === 'elim'], ['전멸형(PD 제외)', g => g.type === 'elim' && g.map !== 'Prisoners Dilemma']];
P(table(['지도', '묶음', '판', '승', '우리 전멸', '전멸 라운드 중앙 [사분위]', 'G 평균', '상대 최장 평균', '탈출/판', '탈출 있는 판'], mapRows([['기준', BASE], ['avoid6', CAND]], ELIM_SEL)));

P('\n### C.1 짝 비교 (online_compare.js 방식: 팀×지도 평균의 차, 붓스트랩 95%)');
{
  const rows = [];
  const add = (label, sel, keyFn = key) => {
    for (const [f, name] of [[g => g.G, 'G'], [g => g.win, '승'], [g => g.survived, '생존']]) {
      const s = paired(BASE.filter(sel), CAND.filter(sel), keyFn, f);
      rows.push([label, name, s.keys, fx(s.meanA, 2), fx(s.meanB, 2), ci(s)]);
    }
  };
  add('전멸형 전체', g => g.type === 'elim');
  add('전멸형(PD 제외)', g => g.type === 'elim' && g.map !== 'Prisoners Dilemma');
  add('PD(판본 무시)', g => g.map === 'Prisoners Dilemma');
  add('PD(같은 판본끼리)', g => g.map === 'Prisoners Dilemma', g => `${g.opp}|${g.variant}`);
  P(table(['범위', '지표', '짝', '기준 평균', 'avoid6 평균', '차 [95%]'], rows));
  const pk = [];
  for (const g of CAND.filter(x => x.map === 'Prisoners Dilemma')) {
    const b = BASE.filter(x => x.map === 'Prisoners Dilemma' && x.opp === g.opp && x.variant === g.variant);
    pk.push([`${g.opp}|${g.variant}`, b.length ? b.map(x => x.G).join(', ') : '(기준에 같은 판본 없음)', g.G, g.x.ind.esc, g.elimUs ? `전멸 r${g.a.rounds - 1}` : '500라운드']);
  }
  P('\nPD 판별(avoid6 7판): 같은 팀·같은 판본의 기준 G');
  P(table(['팀|판본', '기준 G', 'avoid6 G', 'avoid6 탈출', 'avoid6 끝'], pk));
  // decomposition of the elimination-map G difference into maps (each map carries 1/5 of the 35-key mean)
  const dec = [];
  for (const m of ELIM) { const s = paired(BASE.filter(g => g.map === m), CAND.filter(g => g.map === m), key, g => g.G); dec.push([m, s.keys, fx(s.meanA, 2), fx(s.meanB, 2), sg(s.mean, 2), sg(s.mean * s.keys / 35, 2)]); }
  P('\n지도별 몫(전멸형 35짝 평균 차 = 지도별 평균 차 × 7/35의 합):');
  P(table(['지도', '짝', '기준', 'avoid6', '차', '전멸형 차에 대한 몫'], dec));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## D. 탈출 발동 (` esc`)과 신뢰 전환(` T`)');
{
  const rows = [];
  for (const m of [...ELIM, ...R500]) {
    const x = CAND.filter(g => g.map === m), es = x.flatMap(g => g.x.escs);
    rows.push([m, x.length, x.filter(g => escN(g) > 0).length, sum(x, escN), sum(x, g => g.x.ind.escLate), sum(x, g => g.x.ind.esc2), sum(x, g => g.x.ind.esc3), es.filter(e => e.lineage).length,
      sum(x, g => g.x.ind.T), q(es.map(e => e.r)), q(es.map(e => e.L)), es.filter(e => e.longestNow).length]);
  }
  P(table(['지도', '판', '탈출 있는 판', '탈출', '마지막 30라운드', '2칸', '3칸', '시작 계통의 탈출', '` T` 턴', '라운드 중앙 [사분위]', '길이 중앙 [사분위]', '그때 우리 최장'], rows));
  const all = CAND.flatMap(g => g.x.escs);
  P(`\n전체 탈출 ${all.length}회, 판당 ${fx(all.length / CAND.length, 2)}회. ` + '` T`(신뢰로 탈출 꺼짐) 턴 합 ' + sum(CAND, g => g.x.ind.T) + '.');
  const nearC = all.filter(e => e.near).map(e => e.near.cheb), nearL = all.filter(e => e.near).map(e => e.near.len);
  P(`탈출 때 가장 가까운 적 머리: 체비쇼프 ${q(nearC)}, 길이 ${q(nearL)}. 3칸 안의 짧은 적 머리 수 ${q(all.map(e => e.shortNear))}.`);
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## E. 시작 계통(요새) — Autarky, PD6, PD10');
{
  const rows = [];
  for (const [label, sel] of [['Autarky', g => g.map === 'Autarky'], ['PD6', g => g.variant === 'PD6'], ['PD10', g => g.variant === 'PD10']]) for (const [name, set] of [['기준', BASE], ['avoid6', CAND]]) {
    const x = set.filter(sel); if (!x.length) continue;
    const lin = x.map(g => g.x.lineage), f = x.map(g => g.x.fountains).filter(Boolean);
    const ex = lin.filter(l => l.exitRound !== null);
    rows.push([label, name, x.length, x.filter(g => g.win).length, `${ex.length} (${q(ex.map(l => l.exitRound))})`, sum(lin, l => l.escSprints), fx(mean(lin.map(l => l.escSplits)), 1),
      `${lin.filter(l => l.death).length}: ${Object.entries(lin.filter(l => l.death).reduce((o, l) => { o[l.death.cause] = (o[l.death.cause] || 0) + 1; return o; }, {})).map(([k, v]) => k + ' ' + v).join(', ')}`,
      `${fx(mean(lin.map(l => l.lens[100])), 1)} / ${fx(mean(lin.map(l => l.lens[300])), 1)} / ${fx(mean(lin.map(l => l.lens[500])), 1)}`,
      f.length ? `${fx(mean(f.map(z => z.us.natOwn)), 1)} : ${fx(mean(f.map(z => z.them.natOther)), 1)}` : '–']);
  }
  P(table(['지도', '묶음', '판', '승', '계통이 통로를 벗어난 판 (라운드)', '계통의 탈출 질주', '계통의 탈출 분열/판', '계통 사망 (원인)', '계통 길이 r100 / r300 / r500', '우리 샘물 자연 진주: 우리 : 상대'], rows));
  P('- 계통 사망 원인: selfFree = 빈 이웃이 있는 자해(대개 `feed` 먹이 넘기기), rammed = 적이 박음, trapped = 빈 이웃 0.');
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## F. 길이 6 이상 사망 (판당, baseline_study 분류 cls2)');
{
  const cls = ['H-rammed', 'feed', 'stub', 'trapped', 'H-attack', 'ally', 'W/S', 'A', 'O-enemy'];
  const rows = [];
  for (const [label, sel] of [['전멸형(PD 제외)', g => g.type === 'elim' && g.map !== 'Prisoners Dilemma'], ['PD10', g => g.variant === 'PD10'], ['500라운드형', g => g.type === 'r500'], ...R500.map(m => [m, g => g.map === m])]) for (const [name, set] of [['기준', BASE], ['avoid6', CAND]]) {
    const x = set.filter(sel); if (!x.length) continue;
    const per = c => fx(sum(x, g => (g.a.cls2[0][c] || {}).big || 0) / x.length, 2);
    rows.push([label, name, x.length, ...cls.map(per), fx(sum(x, g => sum(Object.values(g.a.cls2[0]), v => v.bigLen)) / x.length, 1), fx(sum(x, g => (g.a.cls2[0]['H-rammed'] || {}).bigLen || 0) / x.length, 1)]);
  }
  P(table(['범위', '묶음', '판', ...cls, 'L≥6 사망 길이 합/판', '그중 박힘 길이/판'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## G. 흐름 (진행 중인 판의 중앙값: 우리 수 / 몸길이 합 / 최장 — 상대 수 / 합 / 최장)');
{
  const R = [0, 20, 50, 100, 150, 200, 300, 400, 500];
  for (const [label, sel] of [['전멸형(PD 제외)', g => g.type === 'elim' && g.map !== 'Prisoners Dilemma'], ['PD10', g => g.variant === 'PD10'], ['500라운드형', g => g.type === 'r500']]) {
    const rows = [];
    for (const [name, set] of [['기준', BASE], ['avoid6', CAND]]) {
      const x = set.filter(sel);
      rows.push([name, ...R.map(r => { const y = x.filter(g => inProg(g, r)); if (!y.length) return '–'; const m = (si, k) => fx(median(y.map(g => flowAt(g, si, k, r))), 0); return `${m(0, 'u')}/${m(0, 't')}/${m(0, 'l')} — ${m(1, 'u')}/${m(1, 't')}/${m(1, 'l')} (${y.length})`; })]);
    }
    P(`\n${label}`); P(table(['묶음', ...R.map(r => 'r' + r)], rows));
  }
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## H. 전멸되는 방식 (우리가 전멸한 판)');
{
  const rows = [];
  for (const [label, sel] of [['전멸형(PD 제외)', g => g.type === 'elim' && g.map !== 'Prisoners Dilemma'], ['PD10', g => g.variant === 'PD10'], ['500라운드형', g => g.type === 'r500']]) for (const [name, set] of [['기준', BASE], ['avoid6', CAND]]) {
    const x = set.filter(sel).filter(g => g.elimUs); if (!x.length) { rows.push([label, name, 0, '–', '–', '–', '–']); continue; }
    const last = x.map(g => g.a.usLast[g.a.usLast.length - 1]).filter(Boolean);
    const cnt = {}; for (const d of last) cnt[d.cls2] = (cnt[d.cls2] || 0) + 1;
    // round at which our longest first fell to <= 3 for good (from flow)
    const small = x.map(g => { const l = g.a.flow[0].l; let r = l.length - 1; while (r > 0 && l[r - 1] <= 3) r--; return r; });
    rows.push([label, name, x.length, q(x.map(g => g.a.rounds - 1)), Object.entries(cnt).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${v}`).join(', '), q(last.map(d => d.len)), q(small)]);
  }
  P(table(['범위', '묶음', '전멸 판', '전멸 라운드 중앙 [사분위]', '마지막 사망 분류', '마지막 드래곤 길이', '최장이 끝까지 3 이하가 된 라운드'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## I. 탈출이 없던 판 = 기준과 같은 봇');
P('cand-avoid6은 탈출 후보를 더할 뿐이다. 로컬 280판에서 갈라진 판은 모두 탈출 수에서 처음 갈라졌다(cand-avoid1.md 6절). 그래서 탈출이 0회인 판에서는 행동이 기준과 같고, 기준 평균과의 차이는 시드·상대의 잡음이다.');
{
  const bmean = new Map();
  for (const g of BASE) { const k = key(g); if (!bmean.has(k)) bmean.set(k, []); bmean.get(k).push(g); }
  const rows = [];
  for (const [label, sel] of [['전멸형(PD 제외)', g => g.type === 'elim' && g.map !== 'Prisoners Dilemma'], ['PD', g => g.map === 'Prisoners Dilemma'], ['500라운드형', g => g.type === 'r500'], ...R500.map(m => [m, g => g.map === m])]) {
    for (const [nm, f] of [['탈출 0', g => escN(g) === 0], ['탈출 ≥1', g => escN(g) > 0]]) {
      const x = CAND.filter(sel).filter(f); if (!x.length) { rows.push([label, nm, 0, '–', '–', '–', '–']); continue; }
      const d = x.map(g => g.G - mean(bmean.get(key(g)).map(b => b.G)));
      const dw = x.map(g => g.win - mean(bmean.get(key(g)).map(b => b.win)));
      const ds = x.map(g => g.survived - mean(bmean.get(key(g)).map(b => b.survived)));
      const alive = g => g.elimUs ? g.a.rounds - 1 : 500;
      const da = x.map(g => alive(g) - mean(bmean.get(key(g)).map(alive)));
      rows.push([label, nm, x.length, ci(boot(d)), sg(mean(dw), 2), sg(mean(ds), 2), ci(boot(da), 0), fx(sum(x, escN) / x.length, 1)]);
    }
  }
  P(table(['범위', '판', 'n', 'G − 같은 팀×지도 기준 평균 [95%]', '승 차', '생존 차', '버틴 라운드 차 [95%] (전멸 라운드, 살면 500)', '탈출/판'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## J. 500라운드형 지도: 지도별 짝 비교와 몫');
{
  const rows = [];
  for (const m of R500) {
    const s = paired(BASE.filter(g => g.map === m), CAND.filter(g => g.map === m), key, g => g.G);
    const w = paired(BASE.filter(g => g.map === m), CAND.filter(g => g.map === m), key, g => g.win);
    const sv = paired(BASE.filter(g => g.map === m), CAND.filter(g => g.map === m), key, g => g.survived);
    const x = CAND.filter(g => g.map === m);
    rows.push([m, s.keys, fx(s.meanA, 2), fx(s.meanB, 2), ci(s), sg(s.mean / 5, 2), sg(w.mean, 2), sg(sv.mean, 2), sum(x, escN), x.filter(g => escN(g) > 0).length]);
  }
  const all = paired(BASE.filter(g => g.type === 'r500'), CAND.filter(g => g.type === 'r500'), key, g => g.G);
  rows.push(['합(35짝)', all.keys, fx(all.meanA, 2), fx(all.meanB, 2), ci(all), sg(all.mean, 2), '', '', sum(CAND.filter(g => g.type === 'r500'), escN), CAND.filter(g => g.type === 'r500' && escN(g) > 0).length]);
  const noA = paired(BASE.filter(g => g.type === 'r500' && g.map !== 'Autarky' && g.map !== 'Portals'), CAND.filter(g => g.type === 'r500' && g.map !== 'Autarky' && g.map !== 'Portals'), key, g => g.G);
  rows.push(['탈출이 있는 3지도(Schooltime, Slithery Fight, Trauma)', noA.keys, fx(noA.meanA, 2), fx(noA.meanB, 2), ci(noA), '', '', '', '', '']);
  P(table(['지도', '짝', '기준 G', 'avoid6 G', '차 [95%]', '500라운드형 차에 대한 몫', '승 차', '생존 차', '탈출', '탈출 있는 판'], rows));
  // noise reference: baseline replicate vs the other two
  const ref = [];
  for (const [a, b] of [[['baseline-r1', 'baseline-r1b'], 'baseline-r1c'], [['baseline-r1', 'baseline-r1c'], 'baseline-r1b'], [['baseline-r1b', 'baseline-r1c'], 'baseline-r1']]) {
    const A = BASE.filter(g => a.includes(g.set)), B = BASE.filter(g => g.set === b);
    ref.push([b + ' 대 나머지 둘', ...R500.map(m => sg(paired(A.filter(g => g.map === m), B.filter(g => g.map === m), key, g => g.G).mean, 1)), sg(paired(A.filter(g => g.type === 'r500'), B.filter(g => g.type === 'r500'), key, g => g.G).mean, 2)]);
  }
  P('\n잡음 기준: 같은 봇의 기준 세트 하나를 나머지 둘과 짝지은 G 차(지도별, 7짝):');
  P(table(['비교', ...R500, '500라운드형 35짝'], ref));
  // same-bot standard error of a 7-key mean difference (one candidate game against the mean of three baseline games)
  const se = [];
  for (const m of R500) {
    const ks = [...new Set(BASE.filter(g => g.map === m).map(g => g.opp))];
    let v = 0; for (const k of ks) { const x = BASE.filter(g => g.map === m && g.opp === k).map(g => g.G), mu = mean(x); v += x.reduce((s2, y) => s2 + (y - mu) ** 2, 0) / (x.length - 1); }
    const sw = Math.sqrt(v / ks.length); se.push([m, fx(sw, 1), fx(sw * Math.sqrt(1 + 1 / 3) / Math.sqrt(ks.length), 1)]);
  }
  P('\n같은 봇이라면 기대되는 잡음: 기준 세 판(팀×지도)의 판 사이 SD와, 후보 1판 대 기준 3판 평균의 7짝 평균 차의 표준오차:');
  P(table(['지도', '팀×지도 안 SD', '7짝 평균 차의 SE'], se));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## K. 탈출 뒤에 일어난 일 (cand-avoid6의 모든 탈출, 탈출한 드래곤 → 분열 때 더 긴 조각)');
{
  const rows = [];
  for (const [label, sel] of [['전멸형', g => g.type === 'elim'], ['500라운드형', g => g.type === 'r500'], ...R500.filter(m => m !== 'Portals').map(m => [m, g => g.map === m])]) {
    const es = CAND.filter(sel).flatMap(g => g.x.escs.map(e => ({ ...e, G: g.G, rounds: g.a.rounds })));
    if (!es.length) continue;
    const died = w => es.filter(e => e.death && e.death.dr <= w).length;
    const rammed = w => es.filter(e => e.death && e.death.dr <= w && e.death.cause === 'rammed').length;
    const alive50 = es.filter(e => e.r + 50 < e.rounds ? e.len50 > 0 : !e.death);
    rows.push([label, es.length, `${died(1)} (${rammed(1)})`, `${died(20)} (${rammed(20)})`, `${alive50.length}`, fx(mean(es.filter(e => e.len50 > 0).map(e => e.len50 - e.L)), 1),
      `${es.filter(e => !e.death).length}`, `${es.filter(e => e.finalLongest).length}`, fx(mean(es.filter(e => e.finalLongest).map(e => e.final)), 1), sum(es, e => e.steps - 1)]);
  }
  P(table(['범위', '탈출', '1라운드 안 사망 (박힘)', '20라운드 안 사망 (박힘)', '50라운드 뒤 살아 있음', '50라운드 뒤 길이 − 탈출 때 길이', '끝까지 삶', '끝에 우리 최장', '그 최장 길이 평균', '탈출 비용(칸)'], rows));
  const gamesG = CAND.filter(g => g.type === 'r500' && g.x.escs.some(e => e.finalLongest));
  P(`\n500라운드형에서 우리 끝 최장(G)이 탈출했던 드래곤의 계통인 판: ${gamesG.length}/${CAND.filter(g => g.type === 'r500').length}판 (${gamesG.map(g => `${g.map} ${g.opp} G${g.G}`).join(', ')}).`);
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## L. 한 걸음이 모두 노출된 결정 (corner_study 기준, 짧은 적 머리의 실제 사거리) — 기준 대 avoid6');
{
  const rows = [];
  const byGrp = s => FOL.filter(f => L.group(f.set) === s);
  const TYPE = m => ELIM.includes(m) ? 'elim' : 'r500';
  for (const [label, sel] of [['전멸형', f => TYPE(f.map) === 'elim'], ['500라운드형', f => TYPE(f.map) === 'r500'], ['Slithery Fight', f => f.map === 'Slithery Fight'], ['Schooltime', f => f.map === 'Schooltime'], ['Trauma', f => f.map === 'Trauma']]) {
    const nG = s => (s === 'base' ? BASE : CAND).filter(g => sel({ map: g.map })).length;
    for (const [name, x0] of [['기준', byGrp('base')], ['avoid6', byGrp('avoid6')], ['avoid6 탈출 수', byGrp('avoid6').filter(f => f.esc)], ['avoid6 그 밖', byGrp('avoid6').filter(f => !f.esc)]]) {
      const x = x0.filter(sel); if (!x.length) continue;
      const n = name === '기준' ? nG('base') : nG('avoid6');
      const rb = x.filter(f => f.death && f.death.beforeNext && f.death.cause === 'rammed').length;
      const d20 = x.filter(f => f.death && f.death.dr <= 20).length;
      const alive50 = x.filter(f => f.len50 > 0 || (!f.death && f.len50 === undefined));
      rows.push([label, name, x.length, fx(x.length / n, 2), pc(x.filter(f => f.steps > 1).length, x.length), `${rb} (${pc(rb, x.length, 1)})`, `${d20} (${pc(d20, x.length)})`, pc(alive50.length, x.length),
        fx(mean(x.filter(f => f.len50 > 0).map(f => f.len50 - f.L)), 1), `${x.filter(f => f.finalLongest).length} (${pc(x.filter(f => f.finalLongest).length, x.length)})`]);
    }
  }
  P(table(['범위', '묶음', '결정', '판당', '질주한 비율', '다음 결정 전 박힘', '20라운드 안 사망', '50라운드 뒤 삶', '50라운드 뒤 길이 변화', '끝에 우리 최장'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## M. 비용: 질주 비용과 먹이 (판당)');
{
  const rows = [];
  for (const [label, sel] of [['전멸형', g => g.type === 'elim'], ['500라운드형', g => g.type === 'r500'], ...R500.map(m => [m, g => g.map === m])]) for (const [name, set] of [['기준', BASE], ['avoid6', CAND]]) {
    const x = set.filter(sel); if (!x.length) continue;
    rows.push([label, name, x.length, fx(mean(x.map(g => sum(g.a.paid[0]))), 1), fx(mean(x.map(g => sum(g.x.escs, e => e.steps - 1))), 1), fx(mean(x.map(g => sum(g.a.eat[0].nat))), 1), fx(mean(x.map(g => sum(g.a.eat[0].own) + sum(g.a.eat[0].opp))), 1), fx(mean(x.map(g => sum(g.a.eat[1].nat))), 1)]);
  }
  P(table(['범위', '묶음', '판', '질주 비용 합', '그중 탈출 비용', '우리 자연 진주', '우리 주검 진주', '상대 자연 진주'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## N. 한 걸음 모두 노출 → 다음 결정 전 박힘: 세트별, 질주 여부별 (500라운드형 / 전멸형)');
{
  const rows = [];
  const TYPE = m => ELIM.includes(m) ? '전멸형' : '500라운드형';
  const rr = a => { const k = a.filter(f => f.death && f.death.beforeNext && f.death.cause === 'rammed').length; return `${k}/${a.length} (${pc(k, a.length, 1)})`; };
  for (const t of ['500라운드형', '전멸형']) for (const s of ['baseline-r1', 'baseline-r1b', 'baseline-r1c', '기준 3세트', 'cand-avoid6-online']) {
    const x = FOL.filter(f => (s === '기준 3세트' ? L.group(f.set) === 'base' : f.set === s) && TYPE(f.map) === t);
    rows.push([t, s, rr(x), rr(x.filter(f => f.steps > 1)), rr(x.filter(f => f.steps <= 1 && f.kind === 'move')), rr(x.filter(f => f.kind === 'split')), rr(x.filter(f => f.esc))]);
  }
  P(table(['지도 종류', '세트', '전체', '질주함', '한 걸음', '분열', '탈출(` esc`)'], rows));
  // expected rams of the candidate's one-step decisions on 500-round maps under the baseline's per-opponent rates
  const base = FOL.filter(f => L.group(f.set) === 'base' && TYPE(f.map) === '500라운드형' && f.steps <= 1 && f.kind === 'move');
  const cand = FOL.filter(f => L.group(f.set) === 'avoid6' && TYPE(f.map) === '500라운드형' && f.steps <= 1 && f.kind === 'move');
  let expd = 0;
  for (const o of L.OPPS) { const b = base.filter(f => f.opp === o), c = cand.filter(f => f.opp === o); if (!b.length) continue; expd += c.length * b.filter(f => f.death && f.death.beforeNext && f.death.cause === 'rammed').length / b.length; }
  const obs = cand.filter(f => f.death && f.death.beforeNext && f.death.cause === 'rammed').length;
  let pl = 0, term = Math.exp(-expd); for (let k = 0; k <= obs; k++) { pl += term; term *= expd / (k + 1); }
  for (const t of ['500라운드형', '전멸형']) { const e = CAND.filter(g => TYPE(g.map) === t).flatMap(g => g.x.escs).length, f = FOL.filter(x => L.group(x.set) === 'avoid6' && TYPE(x.map) === t && x.esc).length; P(`${t}: 탈출 ${e}회 중 실제 사거리로 "한 걸음 모두 노출"이던 결정 ${f}회, 아니던 결정 ${e - f}회.`); }
  P(`\n500라운드형 한 걸음 결정: avoid6 ${cand.length}건에 상대별 기준 박힘률을 적용한 기대 박힘 ${fx(expd, 1)}건, 관측 ${obs}건(푸아송 P(≤관측) = ${fx(pl, 3)}).`);
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## O. 짝 비교: 버틴 라운드, 길이 6 이상 박힘 (팀×지도 평균의 차, 붓스트랩 95%)');
{
  const alive = g => g.elimUs ? g.a.rounds - 1 : 500;
  const rows = [];
  for (const [label, sel] of [['전멸형(PD 제외)', g => g.type === 'elim' && g.map !== 'Prisoners Dilemma'], ['Devil', g => g.map === 'Devil'], ['Trophy', g => g.map === 'Trophy'], ['Queen Of Spades', g => g.map === 'Queen Of Spades'], ['Default', g => g.map === 'Default'],
    ['500라운드형', g => g.type === 'r500'], ['탈출 3지도(Schooltime, Slithery Fight, Trauma)', g => ['Schooltime', 'Slithery Fight', 'Trauma'].includes(g.map)]]) {
    const a = paired(BASE.filter(sel), CAND.filter(sel), key, alive);
    const r = paired(BASE.filter(sel), CAND.filter(sel), key, g => (g.a.cls2[0]['H-rammed'] || {}).big || 0);
    const rl = paired(BASE.filter(sel), CAND.filter(sel), key, g => (g.a.cls2[0]['H-rammed'] || {}).bigLen || 0);
    rows.push([label, a.keys, `${fx(a.meanA, 0)} → ${fx(a.meanB, 0)}, ${ci(a, 0)}`, `${fx(r.meanA, 2)} → ${fx(r.meanB, 2)}, ${ci(r, 2)}`, ci(rl, 1)]);
  }
  P(table(['범위', '짝', '버틴 라운드 (전멸 라운드, 살면 500)', '길이 6 이상 박힘/판', '박혀 잃은 길이/판'], rows));
}

P('\n## P. 탈출 뒤 결과: 맥락별 (cand-avoid6의 모든 탈출)');
{
  const es = CAND.flatMap(g => g.x.escs.map(e => ({ ...e, type: g.type, rounds: g.a.rounds })));
  const rows = [];
  for (const t of ['elim', 'r500']) {
    const X = es.filter(e => e.type === t);
    for (const [label, f] of [['전체', () => true], ['길이 6–7', e => e.L <= 7], ['길이 8–10', e => e.L >= 8 && e.L <= 10], ['길이 11+', e => e.L >= 11], ['그때 우리 최장', e => e.longestNow], ['마지막 30라운드', e => e.late],
      ['우리 수 ≤3', e => e.units <= 3], ['우리 수 ≥4', e => e.units >= 4], ['가장 가까운 적 머리 체비쇼프 1', e => e.near && e.near.cheb <= 1], ['체비쇼프 2', e => e.near && e.near.cheb === 2]]) {
      const x = X.filter(f); if (!x.length) continue;
      rows.push([t === 'elim' ? '전멸형' : '500라운드형', label, x.length, x.filter(e => e.death && e.death.dr <= 1).length, x.filter(e => e.death && e.death.dr <= 20).length, x.filter(e => !e.death).length, x.filter(e => e.finalLongest).length,
        fx(mean(x.map(e => e.death ? e.death.dr : e.rounds - 1 - e.r)), 0)]);
    }
  }
  P(table(['지도 종류', '맥락', '탈출', '1라운드 안 사망', '20라운드 안 사망', '끝까지 삶', '끝에 우리 최장', '탈출 뒤 평균 수명(라운드)'], rows));
  const cause = {}; for (const e of es) if (e.death) { const k = (e.type === 'elim' ? '전멸형 ' : '500라운드형 ') + e.death.cause; cause[k] = (cause[k] || 0) + 1; }
  P('\n탈출한 드래곤(또는 그 긴 조각)의 사망 원인: ' + Object.entries(cause).map(([k, v]) => `${k} ${v}`).join(', ') + '.');
}

P('\n## Q. 전멸형 지도 팀×지도별 기록 (기준 r1 | r1b | r1c | avoid6). W/L, e=전멸 라운드 또는 G, 우리/상대 수 r100, 우리 최대 최장, 탈출 [라운드·길이·†탈출 뒤 사망까지 라운드]');
{
  for (const m of ['Devil', 'Trophy', 'Queen Of Spades', 'Default']) {
    const rows = [];
    for (const o of L.OPPS) {
      const row = [o];
      for (const s of ['baseline-r1', 'baseline-r1b', 'baseline-r1c', 'cand-avoid6-online']) {
        const g = G.find(x => x.set === s && x.map === m && x.opp === o); if (!g) { row.push('–'); continue; }
        const esc = g.x.escs.map(e => `r${e.r}L${e.L}${e.death ? '†' + e.death.dr : ''}`).join(',');
        row.push(`${g.win ? 'W' : 'L'} ${g.elimUs ? 'e' + (g.a.rounds - 1) : 'G' + g.G} ${flowAt(g, 0, 'u', 100)}/${flowAt(g, 1, 'u', 100)} ${Math.max(...g.a.flow[0].l)}${esc ? ' [' + esc + ']' : ''}`);
      }
      rows.push(row);
    }
    P(`\n${m}`); P(table(['상대', 'baseline-r1', 'baseline-r1b', 'baseline-r1c', 'avoid6'], rows));
  }
}

// ---------------------------------------------------------------------------------------------------------------
P('\n## R. 500라운드형 팀×지도별 기록 (W/L, G 또는 e전멸 라운드 / 상대 최장; avoid6은 탈출 수)');
{
  for (const m of R500) {
    const rows = [];
    for (const o of L.OPPS) {
      const row = [o];
      for (const s of ['baseline-r1', 'baseline-r1b', 'baseline-r1c', 'cand-avoid6-online']) {
        const g = G.find(x => x.set === s && x.map === m && x.opp === o); if (!g) { row.push('–'); continue; }
        row.push(`${g.win ? 'W' : 'L'} ${g.elimUs ? 'e' + (g.a.rounds - 1) : 'G' + g.G}/${g.theirLongest}${s.startsWith('cand') ? ' 탈출 ' + g.x.ind.esc + (g.x.escs.some(e => e.finalLongest) ? ' (G가 탈출 계통)' : '') : ''} [${g.gameId}]`);
      }
      rows.push(row);
    }
    const mt = s => fx(mean(G.filter(x => x.set === s && x.map === m).map(x => x.theirLongest)), 1), mg = s => fx(mean(G.filter(x => x.set === s && x.map === m).map(x => x.G)), 1);
    rows.push(['평균 G / 상대 최장', ...['baseline-r1', 'baseline-r1b', 'baseline-r1c', 'cand-avoid6-online'].map(s => `${mg(s)} / ${mt(s)}`)]);
    P(`\n${m}`); P(table(['상대', 'baseline-r1', 'baseline-r1b', 'baseline-r1c', 'avoid6'], rows));
  }
}
