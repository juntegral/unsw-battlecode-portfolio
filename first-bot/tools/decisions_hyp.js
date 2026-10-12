#!/usr/bin/env node
// Ranked hypotheses for our bot from the large-scale decision tables (tools/decisions_scale.js). Reads
// data/decisions/scale.json only. For each binary rule and each focus bot (default merge2 = bot/ 12142 and swarm8
// 12186): the stratified impact of moving the bot to the top winners' rate (map x phase x length cells), times a
// confidence built from support, consistency across maps and top teams, agreement of two independent signals (the
// outcome difference and the winners-vs-losers contrast), the bootstrap interval of the gap, and the sign of the
// 30-round outcome. Rules that one code change moves together are one hypothesis. Each carries the code gate in bot/.
//
// usage: node tools/decisions_hyp.js [--in data/decisions/scale] [--out data/decisions/hypotheses] [--ours 12142,12186]
//                                    [--n 15]
// Output: <out>.json and <out>.md (Korean).
//
// score = |impact| x confidence, impact in length per team-game (net30 = family length change over 30 rounds plus
// enemy length killed head-on: splits, sacrifices and portals pay off later than 10 rounds; fk = sacrificed pearls
// eaten by the own king within 20 rounds, for sacrifice rules).
// confidence = support x (mapCons + teamCons) / 2 x signals x gapCI x horizon, each in [0, 1]:
//   support  = min(1, our rows / 200) x min(1, top rows / 2000)
//   mapCons  = share of maps (>= 300 top and >= 30 of our rows) whose own (winners - ours) x (outcome difference) has
//              the sign of the total impact
//   teamCons = share of top teams (>= 100 rows) whose rate differs from ours in the direction of the within-cell gap
//   signals  = the winners-vs-losers contrast as a second, independent signal. When it is small next to our gap
//              (|W - L| < 0.25 |W - ours|) it says nothing about our distance: 0.8. Otherwise 1 when it points the way
//              the outcome difference does (0.9 if its interval covers 0), 0.5 when it points the other way
//   gapCI    = 1 when the bootstrap interval of the overall (winners - ours) excludes 0 and has the sign of the
//              within-cell gap, else 0.6
//   horizon  = 0.7 when the 10-round impact (net10) has the other sign (net30 rules only), else 1
// "keep" = impact < 0: moving to the winners' rate would cost length; our behaviour is the better one there.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const IN = path.resolve(ROOT, opt('in', path.join('data', 'decisions', 'scale')));
const OUT = path.resolve(ROOT, opt('out', path.join('data', 'decisions', 'hypotheses')));
const OURS = opt('ours', '12142,12186').split(',').map(s => 'O' + s.trim());
const NTOP = +opt('n', 15);
const J = JSON.parse(fs.readFileSync(IN + '.json', 'utf8'));
const { maps: MAPS, phases: PHASES, groups } = J.meta;
const ELIM = new Set(J.meta.elimMaps);

// ---------------------------------------------------------------------------------------------------------------
// Code gates in bot/ (2026-09-30: bot/ = merge2, submission 12142; swarm8 = exp/cand-swarm8/bot, submission 12186).
// Line numbers are those of bot/plan.cpp at that date.
const CODE = {
  split: { loc: 'plan.cpp `Planner::wantSplit()`(L440–476), `decide()` "split instead of moving"(L989–1001); params.hpp split policy',
    now: '길이 조건 `SPLIT_LEN` 8(수가 1이면 `SPLIT_FIRST_LEN` 5), 자식 `SPLIT_CHILD` 3, 수 상한 `SPLIT_CAP_BASE` 3/`SPLIT_CAP_RICH` 5, 적 머리가 보이면 금지(`enemyHeadsNow.empty()`), `GATHER_START` 340부터 금지, 왕은 보험 분열만. swarm8은 r1–249에 길이 4–7을 2+2식으로 나눈다(S1, 상한 `SWARM_CAP_*`, 시작 6마리 이상 팀의 시작 드래곤은 제외).',
    change: '길이 4 → 2+2(왕 포함), 길이 5–9는 r≤166 넓은 곳에서 자식 2, 적이 보여도 허용, 수 상한을 지도 면적 기준으로(swarm8의 S1·S2 방향).' },
  stub: { loc: 'plan.cpp `decide()` escape split(L893–978: `act.splitSize = w_.myLen - 2`)',
    now: '막힘 탈출 분열은 늘 부모 2칸 + 몸 대부분을 자식에게(stub) 준다.', change: '넓은 곳의 분열은 자식 2(몸을 부모에 남김), 막힘 탈출만 stub.' },
  corridor: { loc: 'plan.cpp `decide()` escape split + pocket eat(L893–978), params.hpp `POCKET_*`, `DOOM_VALUE`',
    now: '길이 ≥8이 좁은 방에서 막히면 탈출 분열 고리(샘 펌프·요새)를 돈다.', change: '유지(보호 조건). 이 고리를 풀면 로컬 G −3.81이었다(`cand-escape1.md`).' },
  exposure: { loc: 'plan.cpp `Planner::threatAt()`(L124–140), params.hpp `T1`–`T4`, `TRADE_BAD_FOR_THEM`, `KING_THREAT_MULT`',
    now: '더 짧은 적 머리의 도달 칸에 큰 위협 벌점을 준다. 긴 드래곤은 노출 칸을 피한다.', change: '유지(보호 조건).' },
  sprintEscape: { loc: 'plan.cpp `decide()` ram escape(L739–785), params.hpp `ESCAPE_MIN_LEN` 6, `RAMMER_TRUST` 4',
    now: '한 걸음이 모두 노출이면 2–3칸 질주로 도달 밖에 간다(avoid6).', change: '유지(보호 조건).' },
  approachLong: { loc: 'plan.cpp `computeSoftPenalty()` `HEAD_PATH_PENALTY`, `threatAt()`', now: '긴 드래곤은 짧은 적 머리 쪽으로 덜 간다.', change: '유지(보호 조건).' },
  ram: { loc: 'plan.cpp `Planner::tradeValue()`(L417–437), `decide()` 한 걸음 박치기 후보(L687–692); params.hpp `KILL_MIN_DIFF` 3, `KILL_MIN_RATIO` 2',
    now: '적이 우리보다 3칸 이상 길고 2배 이상일 때만 박는다. 수가 1이면 0, 왕은 박지 않는다. swarm8은 길이 ≤4 조각이 수 ≥4, r≤339에서 같거나 긴 적과 맞바꾼다(S3, 쫓지는 않음).',
    change: '길이 ≤4 조각은 적이 같거나 길면 박는다(아군이 보일 때 우선). 적 머리가 바로 옆이면 한 걸음 박치기를 허용.' },
  approachSmall: { loc: 'plan.cpp `computeAttract()` 사냥 원천(L237–244: `tradeValue() > 0`, `HUNT_MAX_LEN` 5)', now: '박을 수 없는 적에게는 끌리지 않는다.', change: '유지(보호 조건).' },
  sacrifice: { loc: 'plan.cpp `decide()` late consolidation(L621–667); params.hpp `FEED_FIRST_ROUND` 430, `GATHER_START` 340, `FEED_MAX_DIST` 5, `GATHER_FEED_UNITS` 4, `GATHER_FEED_MIN_LEN` 4',
    now: '340부터 왕(가장 긴 아군)에게만, 430부터는 더 긴 아군에게 경로 ≤5에서 자기 목으로 죽는다. 먹이 조각 길이 ≥4, 팀 수 ≥3(≥4). swarm8은 360부터 가까운 더 긴(+2) 아군에게도(T1), 먹이 길이 ≥3(T2).',
    change: '250라운드부터, 보이는(또는 음파로 아는) 길이 ≥8 또는 4칸 이상 긴 아군 머리가 3칸 안이고 적 머리가 없으면 작은 조각이 자기 목으로 죽는다. 왕이 아니라 가까운 큰 아군이 먹는다.' },
  kingApproach: { loc: 'plan.cpp `computeGoal()`(L519–550), `GATHER_W`', now: '왕은 제자리에서 먹고, 아군이 왕에게 온다.', change: '왕이 가장 가까운 아군 쪽으로 가는 비율은 상위와 비슷하게.' },
  pearlContest: { loc: 'plan.cpp `computeAttract()` 경쟁 계수(L263–269): `CONTEST_ENEMY_CLOSER` 0.15, `CONTEST_ENEMY_ONE_CLOSER` 0.3, `CONTEST_EQUAL` 0.9; `threatAt()`',
    now: '적이 더 가까운 진주는 값을 0.15–0.3배로 깎고, 적 도달 칸은 위협 벌점을 준다.', change: '작은 조각(L≤4)은 적이 같거나 가까운 진주도 쫓는다(경쟁 계수 완화, 작은 조각의 위협 벌점 완화).' },
  pearlSprint: { loc: 'plan.cpp `decide()` 2걸음 질주 후보(L709–736): `p2 >= 0.5`, `SPRINT_COST` 1.6, `!late_`',
    now: '2걸음 질주는 진주를 먹거나 위협을 피할 때만, 비용 1.6.', change: '적과 다투는 2걸음 진주는 질주로 먼저 먹는다(길이 ≥3).' },
  spawn: { loc: 'plan.cpp `computeAttract()` 미래 생성 원천(L229), params.hpp `FUTURE_SPAWN_HORIZON` 120, `SPAWN_CONF`, `GAMMA_WAIT`, `BLOCK_SPAWN_PENALTY`',
    now: '본 카운트다운으로 미래 생성 칸을 원천으로 쓴다(대기 할인 0.97/라운드).', change: '5라운드 안에 생길 칸의 가중을 올린다.' },
  portal: { loc: 'plan.cpp `Planner::portalPenalty()`(L160–174), `decide()` 포털 후보(L693–699), `computeFrontier()`; params.hpp `PORTAL_*`, `FRONTIER_*`',
    now: 'portal1: 모르는 포털은 탐침 뒤에만, 출구가 안 보이면 벌점 0.5–8.', change: '진주가 먼 포털 변에서는 통과를 더 허용(출구 붐빔은 swarm9처럼 아군 확인).' },
  deadend: { loc: 'plan.cpp `decide()` doomed/deadEnd 판정과 escape split(L893–978), `areaSafety()`(L322–363)',
    now: '모든 수가 지평선 안에서 죽을 때만 탈출 분열(부모 2칸).', change: '막다른 곳의 처리(분열·질주·자해)를 상위 비율로.' },
  sonar: { loc: 'main.cpp 음파 보내기(L45–50), plan.cpp `setSonar()`/`pickSonarDir()`(L481–515), world.cpp `encodeMsg()`/`ingestSonar()`; params.hpp `GATHER_BROADCAST` 300',
    now: '300라운드 전에는 한 방향, 뒤에는 네 방향으로 같은 메시지.', change: '처음부터 네 방향 방송.' },
};
// Prior experiments on the same code gate (research/experiments/online-tests.md, OVERNIGHT-2026-09-29.md). verdict
// 'keep' = removing or reversing our behaviour there was measured to hurt; 'adopted' = already moved toward the top
// teams in bot/; 'partial' = a tested candidate moved part of the way.
const EXPERIMENTS = {
  corridor: { verdict: 'keep', note: 'cand-escape1이 고리를 풀자 로컬 G −3.81 [−6.70, −0.91], 흉내 상대 −7.50' },
  sprintEscape: { verdict: 'keep', note: 'avoid6 채택: 온라인 G +2.12 [0.28, 4.11], 길이 ≥6이 박히는 수 판당 −0.60' },
  portal: { verdict: 'adopted', note: 'portal1 채택: Portals G +18.86 [13.11, 24.60]; swarm8은 Portals 0/7(출구 아군 충돌)' },
  split: { verdict: 'partial', note: 'px-king-v2 비통로 8지도 G +6.64 [3.60, 9.89]; swarm8(S1·S2) 기준점 대비 +4.24 [1.59, 6.98], merge2 대비 +1.25 [−2.21, 4.73]' },
  ram: { verdict: 'partial', note: 'swarm8의 S3(길이 ≤4, 수 ≥4, r≤339 맞바꿈)만 시험됨. 따로 잰 적 없음' },
  sacrifice: { verdict: 'partial', note: 'swarm8의 T1(360부터 가까운 더 긴 아군)·T2(먹이 길이 ≥3)만 시험됨' },
};
const NOT_RANKED = new Set(['S2', 'S3', 'S7', 'K5', 'G4']); // descriptive: sonar usage (no turn-level outcome) and supersets
// our escape split (decide(), dead end -> child = body - 2) is one gate for D3 (corridor loop), D2 (dead-end split) and
// C5 (stub splits: nearly all our splits of length >= 6 are escape splits), so they share the corridor experiment
const RULE_CODE = { R1: 'split', R2: 'split', C3: 'split', E1: 'split', C4: 'split', C5: 'corridor', D3: 'corridor', D2: 'corridor', R5: 'exposure', R8: 'sprintEscape', A3: 'approachLong',
  R4: 'ram', B1a: 'ram', B1b: 'ram', B3: 'ram', D1: 'ram', R7: 'approachSmall', R3: 'sacrifice', K1: 'sacrifice', K5: 'sacrifice', K3: 'kingApproach',
  P1: 'pearlContest', P2: 'pearlContest', P3: 'pearlContest', P4: 'pearlSprint', P5: 'spawn', R6: 'portal', G2: 'portal', G3: 'portal', G4: 'portal',
  D1b: 'deadend', D2b: 'deadend', D2c: 'deadend' };

// ---------------------------------------------------------------------------------------------------------------
const sgn = x => (x > 0 ? 1 : x < 0 ? -1 : 0);
const excl0 = ci => ci && ci[0] !== null && ci[1] !== null && (ci[0] > 0 || ci[1] < 0);
function score(id, gr) {
  const R = J.rules[id], I = J.impacts[id] && J.impacts[id][gr];
  if (!R || R.kind !== 'bin' || !I || NOT_RANKED.has(id) || R.fam === 'sonar') return null;
  const cur = R.cur === 'fk' ? 'fk' : 'net30';
  const imp = I[cur].impact, imp10 = I.net10.impact, imp30 = I.net30.impact;
  const pW = R.all.TW.p, pL = R.all.TL.p, pT = R.all.T.p, pO = R.all[gr] && R.all[gr].p;
  if (pO === null || pO === undefined || pW === null) return null;
  // direction from the gap within cells (our turns moved to the winners' rate), not from the overall rates: the overall
  // gap can have the other sign when our turns sit in different cells than the winners' (e.g. P1)
  const gapAll = pW - pO, gap = Number.isFinite(I[cur].gap) && I[cur].gap !== null ? I[cur].gap : gapAll, nO = R.all[gr].n, nT = R.all.T.n;
  const support = Math.min(1, nO / 200) * Math.min(1, nT / 2000);
  // maps
  let mElig = 0, mAgree = 0; const mapRows = [];
  MAPS.forEach((m, mi) => {
    const T = R.map.T[mi], W = R.map.TW[mi], O = R.map[gr][mi];
    if (!T || !W || !O || T.n < 300 || O.n < 30 || W.p === null || O.p === null || !T.out1 || T.n1 < 20 || T.n0 < 20) return;
    const dT = T.out1[cur] - T.out0[cur];
    if (!Number.isFinite(dT)) return;
    const x = (W.p - O.p) * dT;
    mElig++; if (sgn(x) === sgn(imp)) mAgree++;
    mapRows.push({ map: m, pW: W.p, pO: O.p, dT, nO: O.n });
  });
  const mapCons = mElig ? mAgree / mElig : 0.5;
  // teams
  let tElig = 0, tAgree = 0;
  for (const e of Object.values((R.teams && R.teams.T) || {})) { if (e.n < 100 || e.p === null) continue; tElig++; if (sgn(e.p - pO) === sgn(gap)) tAgree++; }
  const teamCons = tElig ? tAgree / tElig : 0.5;
  // two signals: outcome difference (all top rows) and winners vs losers
  const dAll = R.all.T.out1[cur] - R.all.T.out0[cur], wl = pW - pL, wlCI = J.boot[id] && J.boot[id]['TW-TL'];
  const signals = Math.abs(wl) < 0.25 * Math.abs(gap) ? 0.8 : sgn(dAll) === sgn(wl) ? (excl0(wlCI) ? 1 : 0.9) : 0.5;
  const gapCI = J.boot[id] && J.boot[id]['TW-' + gr];
  const gapF = excl0(gapCI) && sgn(gapAll) === sgn(gap) ? 1 : 0.6;
  const horizon = cur === 'net30' && Number.isFinite(imp10) && sgn(imp10) !== sgn(imp) ? 0.7 : 1;
  // a measured experiment on the same gate that contradicts the direction the tables suggest: keep, low confidence
  const ex = EXPERIMENTS[RULE_CODE[id]];
  const contra = ex && ex.verdict === 'keep' && imp > 0;
  const conf = support * (0.5 * mapCons + 0.5 * teamCons) * signals * gapF * horizon * (contra ? 0.3 : 1);
  // where it applies: map type x phase and maps carrying most of the impact
  const typ = I[cur].byType, ph = I[cur].byPhase, bm = I[cur].byMap;
  const share = (x, tot) => tot ? x / tot : 0;
  const segs = [];
  for (const [t, v] of Object.entries(typ)) if (share(v, imp) >= 0.25) segs.push(t === 'E' ? '전멸형' : '500형');
  const phs = PHASES.filter((p, i) => share(ph[i], imp) >= 0.2);
  const mps = MAPS.map((m, i) => [m, bm[i]]).filter(([, v]) => share(v, imp) >= 0.15).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1])).map(([m]) => m);
  return { id, gr, name: R.name, fam: R.fam, cur, imp, imp10, imp30, al10: I.al10.impact, kc10: I.kc10.impact, eat10: I.eat10.impact, pW, pL, pT, pO, gap, gapAll, nO, nT, turns: I[cur].turns,
    coverage: I[cur].coverage, support, mapCons, mElig, teamCons, tElig, signals, gapF, horizon, conf, score: Math.abs(imp) * conf, keep: imp < 0 || contra,
    contra, exp: ex || null,
    dAll, wl, wlCI, gapCI, segType: segs, segPhase: phs, segMaps: mps, mapRows, code: RULE_CODE[id] || null };
}

const all = [];
for (const id of Object.keys(J.rules)) for (const gr of OURS) { const s = score(id, gr); if (s) all.push(s); }
// one hypothesis per code change: the best-scoring rule of each change family (per focus bot), others listed with it
function rank(gr) {
  const L = all.filter(s => s.gr === gr).sort((a, b) => b.score - a.score);
  const byCode = new Map();
  for (const s of L) {
    const key = (s.code || s.id) + (s.keep ? ':keep' : ':adopt');
    if (!byCode.has(key)) byCode.set(key, { head: s, also: [] }); else byCode.get(key).also.push(s);
  }
  return [...byCode.values()].sort((a, b) => b.head.score - a.head.score);
}
const ranked = Object.fromEntries(OURS.map(g => [g, rank(g)]));

// tree leaves: learned states where our focus bots diverge most from the winners, and where winners and losers differ
const leafFind = [];
for (const t of J.trees) for (const [li, l] of t.leaves.entries()) {
  const T = l.g.T, W = l.g.TW, Lo = l.g.TL;
  if (!T || T.n < 500 || !W || !Lo || W.p === null || Lo.p === null) continue;
  const dT = T.out1 && T.out0 ? T.out1[t.cur] - T.out0[t.cur] : null;
  const rec = { spec: t.id, title: t.title, yes: t.yes, leaf: li, text: l.text, nT: T.n, pT: T.p, pW: W.p, pL: Lo.p, dT, cur: t.cur, ours: {} };
  for (const gr of OURS) { const O = l.g[gr]; if (O && O.n >= 30 && O.p !== null) rec.ours[gr] = { p: O.p, n: O.n, perGame: O.perGame, imp: dT !== null ? O.perGame * (W.p - O.p) * dT : null }; }
  const teams = Object.values(l.teams || {}).filter(e => e.n >= 100).map(e => e.p);
  rec.teamSpread = teams.length ? [Math.min(...teams), Math.max(...teams), teams.length] : null;
  leafFind.push(rec);
}
const wlLeaves = leafFind.filter(r => r.nT >= 2000).sort((a, b) => Math.abs(b.pW - b.pL) - Math.abs(a.pW - a.pL)).slice(0, 20);
const gapLeaves = Object.fromEntries(OURS.map(gr => [gr, leafFind.filter(r => r.ours[gr] && r.ours[gr].imp !== null).sort((a, b) => Math.abs(b.ours[gr].imp) - Math.abs(a.ours[gr].imp)).slice(0, 20)]));

fs.writeFileSync(OUT + '.json', JSON.stringify({ meta: { created: new Date().toISOString(), in: path.relative(ROOT, IN), ours: OURS, scaleCreated: J.meta.created, top: J.meta.top, topGamesUsed: J.meta.topGamesUsed, manifest: J.meta.manifest },
  scores: all, ranked, wlLeaves, gapLeaves }, (k, v) => (typeof v === 'number' && !Number.isFinite(v)) ? null : v, 1));

// ---------------------------------------------------------------------------------------------------------------
const pc = (p, d = 1) => (p === null || p === undefined || !Number.isFinite(p)) ? '–' : (100 * p).toFixed(d) + '%';
const fx = (v, d = 2) => (v === null || v === undefined || !Number.isFinite(v)) ? '–' : (v > 0 && d >= 0 ? '+' : '') + v.toFixed(d);
const f2 = (v, d = 2) => (v === null || v === undefined || !Number.isFinite(v)) ? '–' : v.toFixed(d);
const tbl = (h, rows) => ['| ' + h.join(' | ') + ' |', '|' + h.map((_, i) => i === 0 ? '---' : '---:').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');
const nm = gr => { const s = gr.slice(1); return `${J.meta.subNames[s] || s}(${s})`; };
const md = ['# 가설 순위 (자동 생성)', '',
  `- 생성: ${new Date().toISOString()}. 명령: \`node tools/decisions_hyp.js${argv.length ? ' ' + argv.join(' ') : ''}\`. 입력: \`${path.relative(ROOT, IN)}.json\`(${J.meta.created}, \`${J.meta.command || 'node tools/decisions_scale.js'}\`, 상위끼리 ${J.meta.topGamesUsed}판).`,
  '- 점수 = |영향| × 신뢰도. 영향은 팀·경기당 길이다(net30: 30라운드 가족 길이 변화 + 머리로 죽인 적 길이; fk: 희생 진주 중 우리 왕이 먹은 수). 지도 × 국면 × 길이 칸마다 우리 비율을 상위 승자 비율로 옮긴다고 보고 더했다. 상관에서 나온 1차 추정이다. net10은 같은 방식의 10라운드 값이다.',
  '- 신뢰도 = 지원 × (지도 일관성 + 팀 일관성)/2 × 두 신호 일치 × 차이 구간 × 10라운드 부호. 정의는 `tools/decisions_hyp.js` 머리 주석에 있다.',
  '- "유지"는 영향이 음수인 항목이다. 상위 승자 쪽으로 옮기면 손해라서 지금 행동을 지킨다.', ''];
for (const gr of OURS) {
  md.push(`## ${nm(gr)}`);
  md.push(tbl(['순위', '규칙', '방향', '구간', '승자 / 패자 / 우리', '칸 안 차이', '영향(판당)', 'net10', '신뢰도', '점수', '같이 움직이는 규칙'], ranked[gr].slice(0, NTOP + 5).map((h, i) => {
    const s = h.head;
    const seg = [...s.segType, ...s.segPhase, ...(s.segMaps.length ? ['(' + s.segMaps.slice(0, 3).join(', ') + ')'] : [])].join(' ') || '전체';
    return [String(i + 1), `${s.id} ${s.name}`, s.contra ? '유지(실험)' : s.keep ? '유지' : (s.gap > 0 ? '더 자주' : '덜'), seg, `${pc(s.pW)} / ${pc(s.pL)} / ${pc(s.pO)}`, `${fx(100 * s.gap, 1)}%p`, `${fx(s.imp)} ${s.cur}`, s.cur === 'net30' ? fx(s.imp10) : '–', f2(s.conf), f2(s.score), h.also.map(x => x.id).join(', ') || '–'];
  })));
  md.push('');
  md.push('### 신뢰도 구성');
  md.push(tbl(['순위', '규칙', '우리 행', '상위 행', '지도 일치(개)', '팀 일치(개)', '두 신호', '차이 구간(승자−우리)', '승자−패자 [구간]', 'al10', 'kc10', '코드', '앞선 실험'], ranked[gr].slice(0, NTOP + 5).map((h, i) => {
    const s = h.head;
    return [String(i + 1), s.id, String(s.nO), String(s.nT), `${f2(s.mapCons)} (${s.mElig})`, `${f2(s.teamCons)} (${s.tElig})`, f2(s.signals),
      s.gapCI ? `[${pc(s.gapCI[0])}, ${pc(s.gapCI[1])}]` : '–', `${pc(s.wl)}${s.wlCI ? ` [${pc(s.wlCI[0])}, ${pc(s.wlCI[1])}]` : ''}`, fx(s.al10, 3), fx(s.kc10, 3), s.code || '–', s.exp ? s.exp.note : '–'];
  })));
  md.push('');
}
// focus: where the focus bots still diverge from the winners, by map type x phase
const FOCUS = ['E1', 'R1', 'R2', 'C4', 'R4', 'B3', 'B1a', 'R7', 'P2', 'P3', 'P4', 'P5', 'R6', 'G2', 'R3', 'K1', 'K3', 'R5', 'R8', 'A3', 'D2', 'D2c', 'D3', 'S3', 'S4'];
md.push('## 집중 비교: 상위 승자 대 우리, 지도 종류 × 국면');
md.push('- 칸 = 상위 승자 / ' + OURS.map(nm).join(' / ') + ' 비율(행 30개 미만은 –). 값 규칙(S4)은 비율 대신 평균이다.');
for (const t of ['E', 'R']) {
  md.push(`### ${t === 'E' ? '전멸형' : '500형'} 지도`);
  md.push(tbl(['규칙', ...PHASES], FOCUS.filter(id => J.rules[id]).map(id => {
    const R = J.rules[id], ti = t === 'E' ? 0 : 1;
    const fmt = st => !st || st.n < 30 || st.p === null ? '–' : R.kind === 'bin' ? (100 * st.p).toFixed(0) : st.p.toFixed(2);
    return [id, ...PHASES.map((p, ph) => [fmt(R.mapPhase.TW[ti][ph]), ...OURS.map(g => fmt(R.mapPhase[g] && R.mapPhase[g][ti][ph]))].join(' / '))];
  })));
  md.push('');
}
// detailed list: the first NTOP hypotheses of the first focus bot, each with the other focus bots' numbers
const MAIN = OURS[0];
const predict = s => {
  const seg = [...s.segType, ...s.segPhase].join(' ') || '전체';
  const unit = s.cur === 'fk' ? '왕이 먹는 희생 진주' : '30라운드 가족 길이(net30)';
  if (s.keep) return `${seg}에서 지금 비율 ${pc(s.pO)}를 지킨다(±5%p). 상위 승자 비율(${pc(s.pW)})로 옮기면 판당 ${unit} ${fx(s.imp)} 예상${s.contra ? '; 같은 관문을 바꾼 실험이 손해였다' : ''}.`;
  const tgt = s.pO + 0.5 * s.gap; // half of the within-cell gap, on our overall rate
  return `${seg}에서 비율 ${pc(s.pO)} → ${s.gap > 0 ? '≥' : '≤'} ${pc(tgt)}(같은 칸의 승자와의 차이 ${fx(100 * s.gap, 1)}%p를 절반 이상 좁힘). 그러면 판당 ${unit} 약 ${fx(0.5 * s.imp)}(다 옮기면 ${fx(s.imp)})${s.cur === 'net30' ? `, 10라운드 기준 ${fx(0.5 * s.imp10)}` : ''}. 보조 지표: 10라운드 생존 ${fx(0.5 * s.al10, 3)}/판, 처치 ${fx(0.5 * s.kc10, 3)}/판.`;
};
md.push(`## 상위 ${NTOP} 가설 상세 (${nm(MAIN)} 기준)`);
ranked[MAIN].slice(0, NTOP).forEach((h, i) => {
  const s = h.head, c = CODE[s.code] || {};
  md.push(`### ${i + 1}. ${s.id} ${s.name} — ${s.contra ? '유지(실험)' : s.keep ? '유지' : (s.gap > 0 ? '더 자주' : '덜')}`);
  md.push(`- **구간:** ${[...s.segType, ...s.segPhase].join(' ') || '전체'}${s.segMaps.length ? `; 영향이 큰 지도 ${s.segMaps.slice(0, 4).join(', ')}` : ''}. 판당 해당 턴 ${f2(s.turns, 1)}.`);
  md.push(`- **상위:** 승자 ${pc(s.pW)}, 패자 ${pc(s.pL)}(차이 ${fx(100 * s.wl, 1)}%p${s.wlCI ? ` [${fx(100 * s.wlCI[0], 1)}, ${fx(100 * s.wlCI[1], 1)}]` : ''}), 상위 행 ${s.nT}. 상위끼리 결과 차이(${s.cur}, 함 − 안 함) ${fx(s.dAll)}.`);
  md.push(`- **우리:** ${OURS.map(g => { const x = all.find(q => q.id === s.id && q.gr === g); return x ? `${nm(g)} ${pc(x.pO)}(행 ${x.nO}, 영향 ${fx(x.imp)})` : null; }).filter(Boolean).join('; ')}. 코드: ${c.now || '–'}`);
  md.push(`- **코드 위치:** ${c.loc || '–'}. **바꿀 것:** ${s.keep ? '바꾸지 않는다. 다른 변경을 넣을 때 이 비율이 상위 쪽으로 움직이지 않는지 보호 지표로 잰다.' + (s.contra ? ` (${c.change || ''})` : '') : (c.change || '–')}`);
  md.push(`- **예측:** ${predict(s)}`);
  md.push(`- **신뢰도 ${f2(s.conf)}:** 지원 ${f2(s.support)}, 지도 일치 ${f2(s.mapCons)}(${s.mElig}개), 팀 일치 ${f2(s.teamCons)}(${s.tElig}팀), 두 신호 ${f2(s.signals)}, 차이 구간 ${f2(s.gapF)}, 10라운드 부호 ${f2(s.horizon)}.${s.exp ? ` 앞선 실험: ${s.exp.note}.` : ''}${h.also.length ? ` 같은 변경으로 움직일 규칙: ${h.also.map(x => `${x.id}(영향 ${fx(x.imp)})`).join(', ')}.` : ''}`);
  md.push('');
});
md.push('## 코드 위치와 바꿀 것');
for (const [k, c] of Object.entries(CODE)) md.push(`- **${k}**: ${c.loc}. 지금: ${c.now} 바꿀 것: ${c.change}`);
md.push('');
md.push('## 나무 잎: 승자와 패자가 가장 다른 곳 (상위 행 ≥2,000)');
md.push(tbl(['결정', '잎', '조건', '상위 n', '승자', '패자', '차이', 'dT', ...OURS.map(nm)], wlLeaves.map(r => [r.spec + ' ' + r.yes, String(r.leaf), r.text, String(r.nT), pc(r.pW), pc(r.pL), `${(100 * (r.pW - r.pL)).toFixed(1)}%p`, f2(r.dT), ...OURS.map(gr => r.ours[gr] ? `${pc(r.ours[gr].p)} (${r.ours[gr].n})` : '–')])));
md.push('');
for (const gr of OURS) {
  md.push(`## 나무 잎: ${nm(gr)}이 승자와 가장 다른 곳 (|판당 턴 × (승자 − 우리) × dT| 순)`);
  md.push(tbl(['결정', '잎', '조건', '승자', '우리', '우리 판당 턴', 'dT', '영향', '팀 범위'], gapLeaves[gr].map(r => [r.spec + ' ' + r.yes, String(r.leaf), r.text, pc(r.pW), pc(r.ours[gr].p), f2(r.ours[gr].perGame, 1), f2(r.dT), fx(r.ours[gr].imp), r.teamSpread ? `${pc(r.teamSpread[0], 0)}–${pc(r.teamSpread[1], 0)} (${r.teamSpread[2]}팀)` : '–'])));
  md.push('');
}
fs.writeFileSync(OUT + '.md', md.join('\n') + '\n');
console.error(`wrote ${path.relative(ROOT, OUT)}.json and .md`);
