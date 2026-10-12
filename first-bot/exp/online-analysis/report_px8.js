#!/usr/bin/env node
'use strict';
// report_px8.js — tables for research/experiments/online-analysis-px8.md: why base-px8's local gain over px1 did not
// transfer online. Reads the outputs of exp/online-analysis/px8_study.js and exp/online-analysis/study.js.
// usage (repository root):
//   node exp/online-analysis/report_px8.js --px8 <px8_study.jsonl> --study <study.jsonl> [--only A,B,...]
//   px8_study.jsonl: px8_study.js --online base-px8-online,px-king-v2-online --local base-px8,base-px8-s3,base-px1,base-px1-s3,base-px8-pd10
//   study.jsonl:     study.js --sets baseline-r1,baseline-r1b,baseline-r1c,px-king-v2-online,base-px8-online
// Groups: "px1 흉내" = local px1 (exp/base-px1, -s3) against proxy_swarm/elim/king, "px8 흉내" likewise, "… r1" against our old
// bot, "px1 온라인" = px-king-v2-online, "px8 온라인" = base-px8-online. Local pairs share opp:map:side:seed; online pairs share
// team × map (Prisoners Dilemma split by 6/10 start dragons), averaged per key as tools/online_compare.js does.
// Sections: A–H and J–L from px8_study.jsonl, I (elimination maps, start lineage, fountains) from study.jsonl.
const L = require('./lib.js');
const { paired, sum, mean, median, quant, fx, sg, ci, pc, table } = L;
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const X = L.readJsonl(opt('px8'));
const S = opt('study') ? L.readJsonl(opt('study')) : [];
const only = opt('only') ? new Set(opt('only').split(',')) : null;
const P = (...a) => console.log(...a);
const sec = (id, title) => { const on = !only || only.has(id); if (on) P(`\n## ${id}. ${title}`); return on; };
const PROX = new Set(['proxy_swarm', 'proxy_elim', 'proxy_king']);
const R500 = new Set(L.R500);
const loc = (v, oppSel) => X.filter(g => g.src === 'local' && g.variant === v && g.set !== 'base-px8-pd10' && oppSel(g.opp));
const onl = v => X.filter(g => g.src === 'online' && g.variant === v);
const GR = {
  'px1 흉내': loc('px1', o => PROX.has(o)), 'px8 흉내': loc('px8', o => PROX.has(o)),
  'px1 r1': loc('px1', o => o === 'r1'), 'px8 r1': loc('px8', o => o === 'r1'),
  'px1 온라인': onl('px1'), 'px8 온라인': onl('px8'),
};
const MAIN = ['px1 흉내', 'px8 흉내', 'px1 온라인', 'px8 온라인'];
const WITH_R1 = ['px1 흉내', 'px8 흉내', 'px1 r1', 'px8 r1', 'px1 온라인', 'px8 온라인'];
const r5 = a => a.filter(g => R500.has(g.map));
const inProg = (g, r) => g.rounds > r || (r === 500 && g.rounds === 500);
const tlAt = (g, side, r, k) => g.tl[side][r / 10][k];            // k: 0 units, 1 total, 2 longest
const medAt = (a, side, r, k) => { const y = a.filter(g => inProg(g, r)); return y.length ? median(y.map(g => tlAt(g, side, r, k))) : NaN; };
const onKey = g => `${g.opp}|${g.mapKey}`;
const locKey = g => g.id;
const pairLocal = (sel, f) => paired(GR['px1 흉내'].filter(sel), GR['px8 흉내'].filter(sel), locKey, f);
const pairOnline = (sel, f) => paired(GR['px1 온라인'].filter(sel), GR['px8 온라인'].filter(sel), onKey, f);
const perGame = (a, f, d = 2) => a.length ? fx(sum(a.map(f)) / a.length, d) : '–';
const ratio = (a, f, g, d = 1) => { const num = sum(a.map(f)), den = sum(a.map(g)); return den ? (100 * num / den).toFixed(d) + '%' : '–'; };
const cz = (g, c, k = 'us') => (g.cause[k] || {})[c] || 0;
const czLen = (g, c, k = 'us') => (g.causeLen[k] || {})[c] || 0;
const n = a => a.length;

// ---------------------------------------------------------------------------------------------------------------
if (sec('A', '묶음과 표본')) {
  P(table(['묶음', '판', '500라운드형 지도 판', '승', '평균 G', '500라운드형 G', '전멸형 G'], Object.entries(GR).map(([k, a]) => [k, n(a), n(r5(a)), pc(sum(a.map(g => g.win)), n(a), 1),
    fx(mean(a.map(g => g.G)), 2), fx(mean(r5(a).map(g => g.G)), 2), fx(mean(a.filter(g => !R500.has(g.map)).map(g => g.G)), 2)])));
  const chk = { games: X.length, updates: sum(X.map(g => g.chk.updates)), deaths: sum(X.map(g => g.chk.deaths)), splits: sum(X.map(g => g.chk.splits)), finalBad: X.filter(g => !g.chk.final).length, massBad: X.filter(g => !g.chk.massOk).length };
  P('\n- 재구성 점검(모두 0이 정상):', JSON.stringify(chk));
}

// ---------------------------------------------------------------------------------------------------------------
if (sec('B', '지도별 G 차이: 로컬(px8 − px1, 흉내 3종, 같은 키) 대 온라인(px8 − px-king, 팀×지도)')) {
  const rows = [];
  for (const m of [...L.R500, ...L.ELIM]) {
    const sel = g => g.map === m;
    const a = pairLocal(sel, g => g.G), b = pairOnline(sel, g => g.G);
    const aw = pairLocal(sel, g => g.win), bw = pairOnline(sel, g => g.win);
    rows.push([m, a.keys, `${fx(a.meanA, 1)} → ${fx(a.meanB, 1)}`, ci(a), sg(100 * aw.mean, 1) + '%p', b.keys, `${fx(b.meanA, 1)} → ${fx(b.meanB, 1)}`, ci(b), sg(100 * bw.mean, 1) + '%p']);
  }
  for (const [lab, sel] of [['500라운드형 5개', g => R500.has(g.map)], ['전멸형 5개', g => !R500.has(g.map)], ['전체', () => true]]) {
    const a = pairLocal(sel, g => g.G), b = pairOnline(sel, g => g.G), aw = pairLocal(sel, g => g.win), bw = pairOnline(sel, g => g.win);
    rows.push(['**' + lab + '**', a.keys, `${fx(a.meanA, 1)} → ${fx(a.meanB, 1)}`, ci(a), sg(100 * aw.mean, 1) + '%p', b.keys, `${fx(b.meanA, 1)} → ${fx(b.meanB, 1)}`, ci(b), sg(100 * bw.mean, 1) + '%p']);
  }
  P(table(['지도', '로컬 짝', '로컬 G px1 → px8', '로컬 차 [95%]', '로컬 승 차', '온라인 짝', '온라인 G px-king → px8', '온라인 차 [95%]', '온라인 승 차'], rows));
  // local vs r1 too
  const a = paired(GR['px1 r1'].filter(g => R500.has(g.map)), GR['px8 r1'].filter(g => R500.has(g.map)), locKey, g => g.G);
  P(`\n- 참고: 로컬 r1 상대 500라운드형 지도 G ${fx(a.meanA, 1)} → ${fx(a.meanB, 1)}, ${ci(a)} (${a.keys}짝).`);
  // identical games locally
  const ids = new Map(GR['px1 흉내'].map(g => [g.id, g]));
  let same = 0, tot = 0; for (const g of GR['px8 흉내']) { const b0 = ids.get(g.id); if (!b0) continue; tot++; if (JSON.stringify(b0.tl) === JSON.stringify(g.tl) && b0.G === g.G) same++; }
  P(`- 로컬 흉내 짝 ${tot}개 중 ${same}개는 흐름(10라운드마다 양쪽 수·합·최장)까지 같은 경기다.`);
  // first round (10-round grid) at which a local px8 game and its px1 twin differ (proxies and r1)
  const firstDiv = (x, y) => { for (let i = 0; i <= 50; i++) if (JSON.stringify(x.tl.us[i]) !== JSON.stringify(y.tl.us[i]) || JSON.stringify(x.tl.them[i]) !== JSON.stringify(y.tl.them[i])) return i * 10; return null; };
  const twin = new Map([...GR['px1 흉내'], ...GR['px1 r1']].map(g => [g.id, g]));
  for (const [lab, sel] of [['500라운드형', g => R500.has(g.map)], ['전멸형', g => !R500.has(g.map)]]) {
    const d = []; let pairs = 0;
    for (const g of [...GR['px8 흉내'], ...GR['px8 r1']].filter(sel)) { const b0 = twin.get(g.id); if (!b0) continue; pairs++; const f = firstDiv(g, b0); if (f !== null) d.push(f); }
    P(`- ${lab} 로컬 짝(흉내 + r1) ${pairs}개: 끝까지 같은 경기 ${pairs - d.length}개, 갈라진 라운드(10라운드 격자) 중앙 r${fx(median(d), 0)} [${fx(quant(d, 0.25), 0)}–${fx(quant(d, 0.75), 0)}], r260 전에 갈라진 짝 ${d.filter(x => x < 260).length}개.`);
  }
}

// ---------------------------------------------------------------------------------------------------------------
if (sec('C', '500라운드형 지도: 왕 길이와 수 (진행 중인 판 중앙값)')) {
  const RR = [200, 300, 340, 350, 400, 450, 500];
  const rows = [];
  for (const k of WITH_R1) {
    const a = r5(GR[k]);
    rows.push([k, n(a), ...RR.map(r => fx(medAt(a, 'us', r, 2), 1)), ...RR.map(r => fx(medAt(a, 'them', r, 2), 1))]);
  }
  P('우리 왕(최장) | 상대 왕');
  P(table(['묶음', '판', ...RR.map(r => '우리 r' + r), ...RR.map(r => '상대 r' + r)], rows));
  const RU = [50, 100, 200, 300, 340, 400, 450];
  const rows2 = WITH_R1.map(k => { const a = r5(GR[k]); return [k, ...RU.map(r => `${fx(medAt(a, 'us', r, 0), 0)} / ${fx(medAt(a, 'them', r, 0), 0)}`), ...[300, 400].map(r => `${fx(medAt(a, 'us', r, 1), 0)} / ${fx(medAt(a, 'them', r, 1), 0)}`)]; });
  P('\n수 (우리 / 상대), 몸길이 합 (우리 / 상대)');
  P(table(['묶음', ...RU.map(r => '수 r' + r), '합 r300', '합 r400'], rows2));
  // per map king curves
  const rows3 = [];
  for (const m of L.R500) for (const k of MAIN) { const a = GR[k].filter(g => g.map === m); rows3.push([m, k, n(a), ...[300, 400, 450, 500].map(r => fx(medAt(a, 'us', r, 2), 1)), ...[300, 400, 500].map(r => fx(medAt(a, 'them', r, 2), 1)), `${a.filter(g => g.G === 0).length}`, fx(mean(a.map(g => g.G)), 1)]); }
  P('\n지도별');
  P(table(['지도', '묶음', '판', '우리 r300', 'r400', 'r450', 'r500', '상대 r300', '상대 r400', '상대 r500', '전멸', '평균 G'], rows3));
  // paired king at r400/r500 local vs online
  const rows4 = [];
  for (const r of [400, 450, 500]) {
    const f = g => inProg(g, r) ? tlAt(g, 'us', r, 2) : 0;   // eliminated or not reached: 0 (the G view)
    const a = pairLocal(g => R500.has(g.map), f), b = pairOnline(g => R500.has(g.map), f);
    rows4.push(['r' + r, `${fx(a.meanA, 1)} → ${fx(a.meanB, 1)}, ${ci(a)}`, `${fx(b.meanA, 1)} → ${fx(b.meanB, 1)}, ${ci(b)}`]);
  }
  P('\n짝 비교: 우리 최장(전멸이면 0) 평균');
  P(table(['라운드', '로컬 흉내 px1 → px8', '온라인 px-king → px8'], rows4));
}

// ---------------------------------------------------------------------------------------------------------------
if (sec('D', '500라운드형 지도: 우리 사망 원인 (판당 건수, 괄호는 잃은 길이)')) {
  const C = ['rammed', 'ram', 'trapped', 'vol', 'volAlly', 'allyHead', 'enemyBody', 'sprintCost'];
  const rows = WITH_R1.map(k => { const a = r5(GR[k]); return [k, n(a), ...C.map(c => `${perGame(a, g => cz(g, c), 1)} (${perGame(a, g => czLen(g, c), 0)})`)]; });
  P(table(['묶음', '판', ...C], rows));
  P('- rammed 적이 우리 머리를 박음, ram 우리가 적 머리를 박음, trapped 빈 이웃 0에서 죽음(stub 뒤 남은 머리 포함), vol 빈 이웃이 있는데 자기 목·해초·행동 없음(희생), volAlly 빈 이웃이 있는데 아군 몸으로(희생), allyHead 아군 머리 충돌, enemyBody 적 몸, sprintCost 질주 비용 부족.');
  // L>=8 and king deaths
  const rows2 = WITH_R1.map(k => {
    const a = r5(GR[k]); const big = g => g.ourDeaths.filter(d => d.len >= 8);
    const kd = g => g.ourDeaths.filter(d => d.king && d.r >= 250);
    const byc = {}; for (const g of a) for (const d of kd(g)) byc[d.c] = (byc[d.c] || 0) + 1;
    return [k, n(a), perGame(a, g => big(g).length), perGame(a, g => sum(big(g).map(d => d.len)), 1), perGame(a, g => kd(g).length),
      Object.entries(byc).sort((x, y) => y[1] - x[1]).map(([c, v]) => `${c} ${fx(v / n(a), 2)}`).join(', '),
      perGame(a, g => big(g).filter(d => d.c === 'rammed').length), perGame(a, g => big(g).filter(d => d.c === 'rammed' && d.bySteps >= 2).length),
      perGame(a, g => big(g).filter(d => d.c === 'rammed' && d.byLen <= 3).length)];
  });
  P('\nstub 분열(길이 ≥5 부모가 머리 2칸만 남김), 판당');
  P(table(['묶음', '전체', '부모 L≥8', '부모 L≥8, r250+', '갇혀서(빈 이웃 0)'], WITH_R1.map(k => { const a = r5(GR[k]); return [k, perGame(a, g => g.stubs.us, 1), perGame(a, g => g.stubs.usBig, 1), perGame(a, g => g.stubs.usBigLate, 1), perGame(a, g => g.stubs.usTrapped, 1)]; })));
  P('\n길이 8 이상과 왕');
  P(table(['묶음', '판', 'L≥8 사망/판', '잃은 길이/판', '왕 사망 r250+/판', '왕 사망 원인/판', 'L≥8 박힘/판', '그중 질주', '그중 박은 적 길이 ≤3'], rows2));
}

// ---------------------------------------------------------------------------------------------------------------
if (sec('E', '바뀐 것 1: 왕 앞 희생과 왕의 몫 (500라운드형 지도)')) {
  const rows = MAIN.map(k => {
    const a = r5(GR[k]), T = g => g.T1;
    return [k, n(a), perGame(a, g => T(g).turns, 1), perGame(a, g => T(g).frontTurns, 1), perGame(a, g => T(g).frontAdjTurns, 1),
      perGame(a, g => T(g).q8, 2), perGame(a, g => T(g).q1, 2), perGame(a, g => T(g).deaths, 2), perGame(a, g => T(g).frontDeaths, 2), perGame(a, g => T(g).nearDeaths, 2), perGame(a, g => T(g).excl, 1)];
  });
  P(table(['묶음', '판', '희생 조건 턴/판', '그중 왕 앞(px8 조건)', '그중 머리 옆', '기대 희생 px8 코드', '기대 희생 px1 코드', '실제 희생', '왕 앞 조건에서 희생', '가까운 큰 아군 조건에서 희생', '제외(갇힘·박치기 우선)'], rows));
  P('- 희생 조건 턴: r340–496, 수 4 이상, 작은 조각(≤4) 또는 r360부터 중간 조각(≤15), 보이는 더 긴 아군이 있는 턴. 기대 희생은 그 턴마다 wantSacrifice()의 확률을 두 판의 코드로 다시 계산해 더한 값이다(봇이 믿는 왕과 보는 길이는 재구성한 기억으로 넣었다).');
  const rows2 = MAIN.map(k => {
    const a = r5(GR[k]); const s = g => g.sacLate;
    return [k, n(a), perGame(a, g => s(g).n, 2), perGame(a, g => s(g).drop, 1), ratio(a, g => s(g).king20, g => s(g).drop), ratio(a, g => s(g).own20, g => s(g).drop), ratio(a, g => s(g).enemy20, g => s(g).drop),
      ratio(a, g => s(g).recv, g => s(g).n), ratio(a, g => s(g).recvFront, g => s(g).recv), ratio(a, g => s(g).recv20, g => s(g).drop)];
  });
  P('\n희생(빈 이웃이 있는 자발 사망, r300+)의 진주');
  P(table(['묶음', '판', '희생/판', '떨군 진주/판', '→ 그때 왕 20라운드', '→ 아군 20라운드', '→ 적 20라운드', '받는 쪽(2칸 안 더 긴 아군) 있음', '그중 받는 쪽 앞', '→ 받는 쪽 20라운드'], rows2));
  const BN = ['0–1', '2', '3–4', '5–8', '9+'];
  const rows3 = [];
  for (const k of MAIN) { const a = r5(GR[k]); for (let i = 0; i < 5; i++) { const s = g => g.sac[i]; rows3.push([k, BN[i], perGame(a, g => s(g).n, 2), perGame(a, g => s(g).drop, 1), ratio(a, g => s(g).king20, g => s(g).drop), ratio(a, g => s(g).longest20, g => s(g).drop), ratio(a, g => s(g).own20, g => s(g).drop), ratio(a, g => s(g).enemy20, g => s(g).drop)]); } }
  P('\n왕까지 거리(체비쇼프)별');
  P(table(['묶음', '왕까지', '희생/판', '진주/판', '→ 그때 왕 20r', '→ 그때 최장 20r', '→ 아군 20r', '→ 적 20r'], rows3));
  const rows4 = MAIN.map(k => { const a = r5(GR[k]); const e = g => g.kingEat; const tot = g => e(g).nat + e(g).vol + e(g).own + e(g).enemy;
    return [k, n(a), perGame(a, tot, 1), perGame(a, g => e(g).nat, 1), perGame(a, g => e(g).vol, 1), perGame(a, g => e(g).own, 1), perGame(a, g => e(g).enemy, 1), ratio(a, g => e(g).vol, tot)]; });
  P('\n왕(그 순간 팀 최장)이 r300부터 먹은 진주 (판당)');
  P(table(['묶음', '판', '합', '자연', '아군 희생', '아군 그 밖 사망', '적 사망', '희생 몫'], rows4));
}

// ---------------------------------------------------------------------------------------------------------------
if (sec('F', '바뀐 것 2·3·4: 진주 남기기와 아군 길이 기억 (500라운드형 지도)')) {
  const rows = MAIN.map(k => { const a = r5(GR[k]); const T = g => g.T23;
    return [k, n(a), perGame(a, g => T(g).eatsLate, 1), perGame(a, g => T(g).kingEats, 1), perGame(a, g => T(g).eatsNonKing, 1), perGame(a, g => T(g).stealKing, 2), perGame(a, g => T(g).stealVisBig, 2), perGame(a, g => T(g).stealAny, 2), ratio(a, g => T(g).stealAny, g => T(g).eatsNonKing)]; });
  P(table(['묶음', '판', 'r320+ 우리 먹이/판', '왕이 먹음', '왕 아닌 조각이 먹음', '그중 왕 머리 맨해튼 3 안', '보이는 큰 아군(≥8, 나+3) 머리 3 안', '둘 중 하나', '왕 아닌 먹이 중 몫'], rows));
  P('- 남겨야 할 진주를 작은 조각이 먹은 수다. px8 규칙이 작동하면 px1보다 줄어야 한다.');
  const rows2 = MAIN.map(k => { const a = r5(GR[k]); const T = g => g.T4; return [k, n(a), perGame(a, g => T(g).turns, 0), perGame(a, g => T(g).hidden, 1), perGame(a, g => T(g).flip, 2), perGame(a, g => T(g).miss, 2)]; });
  P('\n아군 길이 기억(작은 조각 r340+, 체비쇼프 2 안의 아군)');
  P(table(['묶음', '판', '작은 조각 턴/판', '꼬리가 시야 밖인 아군/판', '기억 덕에 큰 받는 쪽이 됨/판', '진짜는 큰데 봇은 작게 봄/판'], rows2));
  const rows3 = MAIN.map(k => { const a = r5(GR[k]); const s = g => g.SON;
    const tot = (b, f) => sum(a.map(g => Object.values(s(g)[b]).reduce((x, y) => x + y, 0)));
    const part = (b, key) => sum(a.map(g => s(g)[b][key] || 0));
    return [k, n(a), ...['sentEarly', 'sentLate'].flatMap(b => [pc(part(b, 'ally'), tot(b), 1), pc(part(b, 'enemy'), tot(b), 1), pc(part(b, 'kelp'), tot(b), 1), pc(part(b, 'self'), tot(b), 1)]),
      ratio(a, g => s(g).kingKnow, g => s(g).kingKnowTurns), ratio(a, g => s(g).kingAny, g => s(g).kingKnowTurns), ratio(a, g => s(g).kingStale, g => s(g).kingKnowTurns), perGame(a, g => s(g).kingKnowTurns, 0)]; });
  const rows4 = L.R500.map(m => [m, ...MAIN.map(k => { const a = GR[k].filter(g => g.map === m); const t = f => sum(a.map(f)); return `${pc(t(g => g.SON.kingKnow), t(g => g.SON.kingKnowTurns), 0)} (${fx(t(g => g.SON.kingKnowTurns) / Math.max(1, n(a)), 0)})`; })]);
  P('\n지도별: 왕 아닌 조각이 진짜 왕을 믿는 비율 (괄호는 해당 턴/판)');
  P(table(['지도', ...MAIN], rows4));
  P('\n음파와 왕 정보');
  P(table(['묶음', '판', 'r<300 음파: 아군에 닿음', '적에 막힘', '해초', '자기 몸', 'r300+: 아군', '적', '해초', '자기 몸', '왕 아닌 조각이 진짜 왕을 앎(r340+)', '길이 8+ 왕을 믿음', '진짜 왕 소식이 40라운드 넘게 없음', '해당 턴/판'], rows3));
}

// ---------------------------------------------------------------------------------------------------------------
if (sec('G', '바뀐 것 5·6: 갇힌 큰 드래곤, 큰 드래곤의 포털')) {
  const rows = WITH_R1.map(k => { const a = GR[k]; const T = g => g.T5;
    return [k, n(a), perGame(a, g => T(g).turns, 2), perGame(a, g => T(g).enemyAdj, 2), perGame(a, g => T(g).canStub, 2), perGame(a, g => T(g).capBlocked, 2), perGame(a, g => T(g).stub, 2), perGame(a, g => T(g).ram, 2), perGame(a, g => T(g).die, 2), perGame(a, g => T(g).stubEnemyAdj, 2), perGame(a, g => T(g).ramEnemyAdj, 2), perGame(a, g => T(g).turnsKing, 2)]; });
  P('모든 지도, 판당. 갇힘 = 빈 이웃 0, 길이 ≥5.');
  P(table(['묶음', '판', '갇힌 턴', '옆에 적 머리', 'stub 가능', '유닛 64로 막힘', 'stub 분열', '박음', '죽음', '적 머리 옆에서 stub', '적 머리 옆에서 박음', '그중 왕'], rows));
  const rows2 = WITH_R1.map(k => { const a = GR[k]; const T = g => g.T6;
    return [k, n(a), perGame(a, g => T(g).big.turns, 0), perGame(a, g => T(g).big.opt, 1), ratio(a, g => T(g).big.took, g => T(g).big.opt), perGame(a, g => T(g).mid.opt, 1), ratio(a, g => T(g).mid.took, g => T(g).mid.opt), perGame(a, g => T(g).small.opt, 1), ratio(a, g => T(g).small.took, g => T(g).small.opt),
      perGame(a, g => T(g).crossBig, 2), perGame(a, g => T(g).crossAll, 1), perGame(a, g => T(g).bigAllyDeaths, 2), perGame(a, g => T(g).bigAllyDeathsAfterPortal, 2)]; });
  P('\n포털 (모든 지도, 판당). 포털 선택지 = 빈 이웃 중 포털 변을 지나는 방향이 있는 턴.');
  P(table(['묶음', '판', 'L≥8 턴', 'L≥8 포털 선택지 턴', '그중 통과', 'L5–7 선택지', '통과', 'L≤4 선택지', '통과', 'L≥8 포털 걸음', '모든 포털 걸음', 'L≥8 아군 충돌 사망', '그중 포털 3라운드 안'], rows2));
  const rows3 = [];
  for (const m of ['Portals', 'Trauma']) for (const k of MAIN) { const a = GR[k].filter(g => g.map === m); const T = g => g.T6;
    rows3.push([m, k, n(a), perGame(a, g => T(g).big.opt, 1), ratio(a, g => T(g).big.took, g => T(g).big.opt), perGame(a, g => T(g).crossBig, 1), perGame(a, g => T(g).bigAllyDeaths, 2), perGame(a, g => T(g).bigAllyDeathsAfterPortal, 2),
      fx(medAt(a, 'us', 400, 2), 1), fx(medAt(a, 'us', 500, 2), 1), perGame(a, g => g.ourDeaths.filter(d => d.king && d.r >= 250).length, 2)]); }
  P('\nPortals·Trauma');
  P(table(['지도', '묶음', '판', 'L≥8 선택지/판', '통과', 'L≥8 포털 걸음/판', 'L≥8 아군 충돌/판', '포털 뒤', '왕 r400', '왕 r500', '왕 사망 r250+/판'], rows3));
}

// ---------------------------------------------------------------------------------------------------------------
if (sec('H', '상대의 압박과 왕 주변 (500라운드형 지도)')) {
  const per = (a, f, g, d = 2) => { const m = sum(a.map(g)); return m ? fx(sum(a.map(f)) / m, d) : '–'; };
  const rows = WITH_R1.map(k => { const a = r5(GR[k]); const K = g => g.K;
    return [k, n(a), perGame(a, g => K(g).kingTurnsLate, 0), per(a, g => K(g).enemyNear, g => K(g).kingTurnsLate), ratio(a, g => K(g).turnsThreat, g => K(g).kingTurnsLate), ratio(a, g => K(g).enemyNear2, g => K(g).kingTurnsLate),
      per(a, g => K(g).feeders, g => K(g).kingTurnsLate), per(a, g => 100 * K(g).eatSafe, g => K(g).turnsSafe, 1), per(a, g => 100 * K(g).eatThreat, g => K(g).turnsThreat, 1)]; });
  P(table(['묶음', '판', '왕 턴 r300+ (L≥8)/판', '왕 시야(7×7)의 적 머리/턴', '적 머리가 보이는 왕 턴', '적 머리가 맨해튼 2 안', '왕 시야의 우리 작은 조각(≤4)/턴', '왕 먹이/100턴: 적 없음', '적 있음'], rows));
  const rows1 = WITH_R1.map(k => { const a = r5(GR[k]); const s = g => g.sacNear;
    return [k, perGame(a, g => s(g).calm.n, 1), ratio(a, g => s(g).calm.king20, g => s(g).calm.drop), perGame(a, g => s(g).threat.n, 1), ratio(a, g => s(g).threat.king20, g => s(g).threat.drop),
      ...[0, 1, 2, 3].map(i => ratio(a, g => g.KD[i], g => sum(g.KD)))]; });
  P('\n왕(길이 ≥8) 체비쇼프 4 안의 희생(r300+): 왕 시야에 적 머리가 없을 때 / 있을 때, 그리고 왕 아닌 조각(r340+)의 왕까지 맨해튼 거리');
  P(table(['묶음', '희생/판 (적 없음)', '→ 왕 20r', '희생/판 (적 있음)', '→ 왕 20r', '왕까지 ≤3', '4–8', '9–16', '17+'], rows1));
  const rows0 = WITH_R1.map(k => { const a = r5(GR[k]);
    return [k, n(a), perGame(a, g => cz(g, 'rammed'), 1), perGame(a, g => cz(g, 'ram', 'them') + cz(g, 'rammed', 'them'), 1), perGame(a, g => sum(g.splitsW.them), 0), perGame(a, g => sum(g.natW.them), 0), perGame(a, g => sum(g.natW.us), 0)]; });
  P('\n접촉과 경제 (판당)');
  P(table(['묶음', '판', '우리 박힘', '상대 접촉 사망', '상대 분열', '상대 자연 진주', '우리 자연 진주'], rows0));
  const rows2 = [];
  for (const k of WITH_R1) { const a = r5(GR[k]); const w = (f) => [0, 2, 4, 6, 7, 8, 9].map(i => fx(mean(a.map(g => f(g)[i])), 1)).join(' / ');
    rows2.push([k, w(g => (g.causeW.us.rammed || new Array(10).fill(0))), w(g => g.splitsW.us), w(g => g.natW.us)]); }
  P('\n창별(50라운드: 0, 2, 4, 6, 7, 8, 9) 판당: 우리 박힘 / 우리 분열 / 우리 자연 진주');
  P(table(['묶음', '박힘', '분열', '자연 진주'], rows2));
}

// ---------------------------------------------------------------------------------------------------------------
const reach = g => g.rounds > 340 && g.tl.us[34][0] >= 4;   // late conversion can start: alive at r340 with >= 4 units
if (sec('J', '변경별 발동과 효과: 로컬 짝 차이 대 온라인 짝 차이 (500라운드형 지도, 판당)')) {
  const kd = g => g.ourDeaths.filter(d => d.king && d.r >= 250);
  const M = [
    ['G(우리 최장, 전멸이면 0)', g => g.G],
    ['승', g => g.win],
    ['왕 r450 (없으면 0)', g => inProg(g, 450) ? tlAt(g, 'us', 450, 2) : 0],
    ['수 r300', g => inProg(g, 300) ? tlAt(g, 'us', 300, 0) : 0],
    ['수 r400', g => inProg(g, 400) ? tlAt(g, 'us', 400, 0) : 0],
    ['1 왕 앞 조건에서 희생', g => g.T1.frontDeaths],
    ['1 희생 r300+', g => g.sacLate.n],
    ['1 희생 진주 → 그때 왕 20r', g => g.sacLate.king20],
    ['1 왕이 먹은 희생 진주 r300+', g => g.kingEat.vol],
    ['왕이 먹은 자연 진주 r300+', g => g.kingEat.nat],
    ['왕이 먹은 진주 합 r300+', g => g.kingEat.nat + g.kingEat.vol + g.kingEat.own + g.kingEat.enemy],
    ['2·3 남길 진주를 작은 조각이 먹음', g => g.T23.stealAny],
    ['4 진짜 큰 받는 쪽을 작게 봄', g => g.T4.miss],
    ['5 갇힌 L≥5가 옆 적 머리를 박음', g => g.T5.ramEnemyAdj],
    ['5 갇힌 L≥5의 stub 분열', g => g.T5.stub],
    ['6 L≥8 포털 걸음', g => g.T6.crossBig],
    ['6 L≥8 아군 충돌 사망', g => g.T6.bigAllyDeaths],
    ['왕 사망 r250+', g => kd(g).length],
    ['왕 갇힘 사망 r250+', g => kd(g).filter(d => d.c === 'trapped').length],
    ['왕 박힘 사망 r250+', g => kd(g).filter(d => d.c === 'rammed').length],
  ];
  const rows = M.map(([name, f]) => {
    const a = pairLocal(g => R500.has(g.map), f), b = pairOnline(g => R500.has(g.map), f);
    const a2 = paired(GR['px1 흉내'].filter(g => R500.has(g.map) && reach(g)), GR['px8 흉내'].filter(g => R500.has(g.map) && reach(g)), locKey, f);
    const b2 = paired(GR['px1 온라인'].filter(g => R500.has(g.map) && reach(g)), GR['px8 온라인'].filter(g => R500.has(g.map) && reach(g)), onKey, f);
    return [name, `${fx(a.meanA, 2)} → ${fx(a.meanB, 2)}, ${ci(a)}`, `${fx(b.meanA, 2)} → ${fx(b.meanB, 2)}, ${ci(b)}`, `${ci(a2)}`, `${ci(b2)} (${b2.keys}짝)`];
  });
  P(table(['지표(앞 숫자는 바뀐 것 번호)', '로컬 흉내 px1 → px8, 차 [95%] (90짝)', '온라인 px-king → px8, 차 [95%] (35짝)', '로컬, r340 도달 판끼리', '온라인, r340 도달 판끼리'], rows));
  const d8 = a => fx(mean(a.map(g => g.T1.q8 - g.T1.q1)), 2);
  P(`\n- 같은 상태에서 px8 코드가 px1 코드보다 더 내는 희생 확률의 합(px8 판, 판당): 로컬 흉내 ${d8(r5(GR['px8 흉내']))}, 온라인 ${d8(r5(GR['px8 온라인']))}. r340 도달 판만: 로컬 ${d8(r5(GR['px8 흉내']).filter(reach))}, 온라인 ${d8(r5(GR['px8 온라인']).filter(reach))}.`);
  for (const k of MAIN) { const a = r5(GR[k]); P(`- ${k}: r340에 수 4 이상으로 살아 있던 판 ${a.filter(reach).length}/${n(a)}, r340 전 전멸 ${a.filter(g => g.rounds <= 340).length}판.`); }
}

// ---------------------------------------------------------------------------------------------------------------
if (sec('K', '로컬 효과를 온라인 상황에 옮기면 (계산)')) {
  const rows = []; let e5 = 0, o5 = 0;
  for (const m of L.R500) {
    const sel = g => g.map === m;
    const a = paired(GR['px1 흉내'].filter(g => sel(g) && reach(g)), GR['px8 흉내'].filter(g => sel(g) && reach(g)), locKey, g => g.G);
    const on = [...GR['px1 온라인'], ...GR['px8 온라인']].filter(sel), rr = on.filter(reach).length / on.length;
    const b = pairOnline(sel, g => g.G);
    e5 += a.mean * rr; o5 += b.mean;
    rows.push([m, `${ci(a)} (${a.keys}짝)`, pc(on.filter(reach).length, on.length, 0), sg(a.mean * rr, 2), ci(b)]);
  }
  rows.push(['**500라운드형 평균**', '', '', sg(e5 / 5, 2), sg(o5 / 5, 2)]);
  P(table(['지도', '로컬 r340 도달 판의 G 차 (px8 − px1)', '온라인 r340 도달 비율(두 봇 합)', '기대 온라인 G 차 = 곱', '실제 온라인 G 차'], rows));
  P(`- 가정: px8의 효과는 r340에 수 4 이상으로 살아 있는 판에서만 나고, 그 크기는 로컬과 같다. 전멸형 지도의 로컬 차는 ${ci(pairLocal(g => !R500.has(g.map), g => g.G))}이다.`);
}

// ---------------------------------------------------------------------------------------------------------------
if (sec('L', '흉내 상대와 상위권: 같은 우리 봇이 만난 상태 (500라운드형 지도)')) {
  const kAt = (g, r) => inProg(g, r) ? tlAt(g, 'us', r, 2) : 0;
  const rows = MAIN.map(k => { const a = r5(GR[k]), r = a.filter(reach);
    return [k, `${r.length}/${n(a)}`, a.filter(g => g.rounds <= 340).length, fx(mean(r.map(g => tlAt(g, 'us', 340, 0))), 1), fx(mean(r.map(g => tlAt(g, 'them', 340, 0))), 1),
      fx(mean(r.map(g => tlAt(g, 'them', 300, 1))), 0), [340, 400, 450, 500].map(x => fx(mean(r.map(g => kAt(g, x))), 1)).join(' / '), [400, 500].map(x => fx(mean(r.map(g => tlAt(g, 'them', x, 2))), 1)).join(' / '),
      fx(mean(r.map(g => g.G)), 1), pc(sum(r.map(g => g.win)), n(r), 0)]; });
  P('r340에 수 4 이상으로 살아 있던 판(늦은 전환이 시작될 수 있는 판)의 평균');
  P(table(['묶음', '도달/판', 'r340 전 전멸', '우리 수 r340', '상대 수 r340', '상대 몸 합 r300', '우리 왕 r340 / r400 / r450 / r500', '상대 왕 r400 / r500', 'G', '승'], rows));
  const rows2 = L.R500.map(m => [m, ...MAIN.map(k => { const a = GR[k].filter(g => g.map === m); return `${fx(medAt(a, 'them', 300, 1), 0)} / ${fx(medAt(a, 'us', 300, 1), 0)} (${a.filter(g => g.rounds <= 340).length})`; })]);
  P('\n지도별 몸길이 합 r300 중앙값: 상대 / 우리 (괄호는 r340 전에 우리가 전멸한 판)');
  P(table(['지도', ...MAIN], rows2));
  const rows3 = ['px1 온라인', 'px8 온라인', 'px1 흉내', 'px8 흉내'].map(k => { const a = GR[k].filter(g => !R500.has(g.map)); const t = f => sum(a.map(f));
    return [k, n(a), a.filter(g => g.rounds > 320).length, t(g => g.T1.turns), t(g => g.T1.frontDeaths), t(g => g.sacLate.n), t(g => g.T5.enemyAdj), t(g => g.T5.ramEnemyAdj), t(g => g.T5.stubEnemyAdj), t(g => g.T6.big.opt), t(g => g.T6.big.took)]; });
  P('\n전멸형 지도: 변경이 작동한 횟수 (합계)');
  P(table(['묶음', '판', 'r320까지 산 판', '희생 조건 턴', '왕 앞 조건 희생', '희생 r300+', '갇힌 L≥5 옆 적 머리', '그때 박음', '그때 stub', 'L≥8 포털 선택지', '통과'], rows3));
  // per-map units, unit-cap blocking and king deaths (500-round maps)
  const kd = g => g.ourDeaths.filter(d => d.king && d.r >= 250);
  const rows4 = [];
  for (const m of L.R500) for (const k of MAIN) { const a = GR[k].filter(g => g.map === m); const c = cc => fx(mean(a.map(g => kd(g).filter(d => d.c === cc).length)), 2);
    rows4.push([m, k, n(a), [200, 300, 400].map(r => fx(medAt(a, 'us', r, 0), 0)).join(' / '), [200, 300, 400].map(r => fx(medAt(a, 'them', r, 0), 0)).join(' / '), fx(mean(a.map(g => g.T5.capBlocked)), 2),
      fx(mean(a.map(g => kd(g).length)), 2), c('trapped'), c('rammed'), c('allyHead'), c('ram')]); }
  P('\n지도별: 수(중앙값), 유닛 64 때문에 stub을 못 한 갇힌 턴, 왕 사망 r250+ (판당)');
  P(table(['지도', '묶음', '판', '우리 수 r200 / r300 / r400', '상대 수 r200 / r300 / r400', '한도로 stub 불가 턴', '왕 사망', '갇힘', '박힘', '아군 머리', '박음'], rows4));
  const tr = GR['px8 온라인'].filter(g => g.map === 'Slithery Fight').flatMap(g => kd(g).filter(d => d.c === 'trapped').map(d => d.r)).sort((x, y) => x - y);
  P(`- px8 온라인 Slithery Fight 왕 갇힘 사망 ${tr.length}건: 라운드 ${tr.join(', ')}.`);
}

// ---------------------------------------------------------------------------------------------------------------
if (S.length && sec('I', '전멸형 지도 (study.js, 기준 210판·px-king·px8)')) {
  const grp = s => s.startsWith('baseline') ? 'base' : s.startsWith('px-king') ? 'pxk' : s.startsWith('base-px8') ? 'px8' : s;
  const mk = g => g.map === 'Prisoners Dilemma' ? g.variant : g.map;
  const key = g => g.opp + '|' + mk(g);
  const SS = { '기준(g4-r4)': S.filter(g => grp(g.set) === 'base'), 'px-king': S.filter(g => grp(g.set) === 'pxk'), 'px8': S.filter(g => grp(g.set) === 'px8') };
  const EM = ['Default', 'Devil', 'Trophy', 'Queen Of Spades', 'PD6', 'PD10'];
  for (const [A, B] of [['기준(g4-r4)', 'px8'], ['px-king', 'px8'], ['기준(g4-r4)', 'px-king']]) {
    const all = paired(SS[A].filter(g => g.type === 'elim'), SS[B].filter(g => g.type === 'elim'), key, g => g.G);
    const rows = EM.map(m => { const a = SS[A].filter(g => mk(g) === m), b = SS[B].filter(g => mk(g) === m); const s = paired(a, b, key, g => g.G);
      return [m, s.keys, fx(s.mean, 2), fx(s.mean * s.keys / all.keys, 2), `${n(a)} / ${a.filter(g => g.win).length} / ${fx(mean(a.map(g => g.G)), 1)}`, `${n(b)} / ${b.filter(g => g.win).length} / ${fx(mean(b.map(g => g.G)), 1)}`]; });
    rows.push(['**전체**', all.keys, ci(all), ci(all), '', '']);
    P(`\n${B} − ${A}: 전멸형 지도 짝(팀×지도, PD 판본별)`);
    P(table(['지도', '짝', '짝 평균 차', '전체 평균에 보탠 몫', `${A} 판 / 승 / G`, `${B} 판 / 승 / G`], rows));
    // keys with a non-zero difference
    const avg = x => { const m = new Map(); for (const g of x) { const kk = key(g); if (!m.has(kk)) m.set(kk, []); m.get(kk).push(g); } return m; };
    const mA = avg(SS[A].filter(g => g.type === 'elim')), mB = avg(SS[B].filter(g => g.type === 'elim'));
    const nz = [...mA.keys()].filter(kk => mB.has(kk)).map(kk => { const a = mA.get(kk), b = mB.get(kk); return [kk, (b[0].oppName || ''), mean(b.map(g => g.G)) - mean(a.map(g => g.G)), a.map(g => (g.win ? 'W' : '') + g.G).join(','), b.map(g => (g.win ? 'W' : '') + g.G + (g.elimUs ? '@r' + (g.a.rounds - 1) : '')).join(',')]; }).filter(x => Math.abs(x[2]) > 1e-9).sort((x, y) => x[2] - y[2]);
    P(`- 차가 0이 아닌 짝(팀|지도, 상대, ${B} − ${A}, ${A} G들, ${B} G들): ` + nz.map(x => `${x[0]} ${x[1]} ${fx(x[2], 1)} [${x[3]} → ${x[4]}]`).join('; '));
  }
  const rows = [];
  for (const m of EM) for (const [k, a0] of Object.entries(SS)) {
    const a = a0.filter(g => mk(g) === m); if (!n(a)) continue;
    const e = a.filter(g => g.elimUs).map(g => g.a.rounds - 1);
    const fa = (si, kk, r) => fx(median(a.filter(g => L.inProg(g, r)).map(g => L.flowAt(g, si, kk, r))), 0);
    rows.push([m, k, n(a), a.filter(g => g.win).length, `${e.length} (r${fx(median(e), 0)} [${fx(quant(e, 0.25), 0)}–${fx(quant(e, 0.75), 0)}])`,
      `${fa(0, 'u', 50)} / ${fa(1, 'u', 50)}`, `${fa(0, 'u', 100)} / ${fa(1, 'u', 100)}`,
      `${fx(mean(a.map(g => g.a.splitsN[0])), 0)} / ${fx(mean(a.map(g => g.a.splitsN[1])), 0)}`, `${fx(mean(a.map(g => sum(g.a.eat[0].nat))), 0)} / ${fx(mean(a.map(g => sum(g.a.eat[1].nat))), 0)}`,
      `${fx(mean(a.map(g => ((g.a.cls2[0]['H-attack'] || {}).n || 0) + ((g.a.cls2[1]['O-enemy'] || {}).n || 0))), 1)} / ${fx(mean(a.map(g => (g.a.cls2[0]['H-rammed'] || {}).n || 0)), 1)}`]);
  }
  P('\n전멸 시기와 경제 (판 평균, 수는 진행 중인 판 중앙값)');
  P(table(['지도', '묶음', '판', '승', '우리 전멸 (중앙 라운드 [사분위])', '수 r50 우리/상대', '수 r100', '분열 우리/상대', '자연 진주 우리/상대', '접촉: 우리가 잡음 / 우리가 박힘'], rows));
  // per-opponent px8 elim outcomes
  const rows2 = [];
  for (const opp of [306, 70, 20, 801, 264, 46, 545]) {
    const a = SS['px8'].filter(g => g.type === 'elim' && +g.opp === opp), b = SS['기준(g4-r4)'].filter(g => g.type === 'elim' && +g.opp === opp), c = SS['px-king'].filter(g => g.type === 'elim' && +g.opp === opp);
    const e = x => x.filter(g => g.elimUs).map(g => g.a.rounds - 1);
    rows2.push([`${opp} ${(a[0] || b[0] || {}).oppName || ''}`, `${n(a)} / ${a.filter(g => g.win).length} / r${fx(median(e(a)), 0)} / ${fx(mean(a.map(g => g.G)), 1)}`, `${n(c)} / ${c.filter(g => g.win).length} / r${fx(median(e(c)), 0)} / ${fx(mean(c.map(g => g.G)), 1)}`, `${n(b)} / ${b.filter(g => g.win).length} / r${fx(median(e(b)), 0)} / ${fx(mean(b.map(g => g.G)), 1)}`]);
  }
  P('\n상대별 전멸형 지도 (판 / 승 / 전멸 중앙 라운드 / 평균 G)');
  P(table(['상대', 'px8', 'px-king', '기준(g4-r4)'], rows2));
  const rows3 = [];
  for (const m of ['PD6', 'PD10', 'Autarky']) for (const [k, a0] of Object.entries(SS)) {
    const a = a0.filter(g => mk(g) === m); if (!n(a)) continue;
    const lin = a.map(g => g.x.lineage), f = a.filter(g => g.x.fountains).map(g => g.x.fountains);
    const ex = lin.filter(l => l.exitRound !== null).map(l => l.exitRound), de = lin.filter(l => l.death);
    rows3.push([m, k, n(a), a.filter(g => g.win).length, [10, 50, 100].map(r => fx(mean(lin.map(l => l.lens[r] || 0)), 1)).join(' / '), `${ex.length}/${n(a)} (r${fx(median(ex), 0)})`,
      `${de.length} (r${fx(median(de.map(l => l.death.r)), 0)})`, fx(mean(f.map(z => z.us.spawns)), 1), fx(mean(f.map(z => z.us.natOwn)), 1), fx(mean(f.map(z => z.them.natOther)), 1)]);
  }
  P('\n시작 계통(가장 긴 시작 드래곤)과 통로 샘물 (study.js, 판 평균)');
  P(table(['지도', '묶음', '판', '승', '계통 길이 r10 / r50 / r100', '통로를 떠난 판 (중앙 라운드)', '계통 사망 (중앙 라운드)', '우리 샘물 생성', '우리가 먹음', '상대가 먹음'], rows3));
}
