#!/usr/bin/env node
// Q2: what do elite losers who survive do differently from those who are eliminated? Top-vs-top games (the reference) against
// our own teams on the same maps. Stage 1 and 2 from exp/eliminations/cache.
// usage: node --max-old-space-size=8192 exp/eliminations/top.js [--out exp/eliminations/numbers-top.md] [--json exp/eliminations/top-summary.json]
// Groups (per team-game): W = winner; LS = loser that still has a dragon at the end; LX = loser eliminated.
'use strict';
const fs = require('fs'), path = require('path');
const L = require('./lib.js');
const { table, f1, f2, pc, mean, med, quant, sum } = L;
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };

const TOPD = L.loadTop();
const G = TOPD.games.filter(g => g.winner === 'A' || g.winner === 'B');
const ON = L.loadOnline();
const out = []; const P = (...a) => out.push(a.join('\n'));
const CPS = [10, 30, 50, 100];
const PHC = { 30: 1, 50: 2, 100: 3 }; // number of death phases (PH = 0,30,50,100,...) before the checkpoint

// ---- team-game features
function feat(g, tm, grp) {
  const T = g.T[tm], o = tm === 'A' ? 'B' : 'A', E = g.T[o];
  const f = { g, tm, grp, ml: g.ml2, map: g.map, elim: T.elim, team: tm === 'A' ? g.teamA : g.teamB, opp: tm === 'A' ? g.teamB : g.teamA };
  for (const c of CPS) {
    f['u' + c] = L.at(g, tm, c, 'u'); f['t' + c] = L.at(g, tm, c, 't'); f['k' + c] = L.at(g, tm, c, 'k'); f['eu' + c] = L.at(g, o, c, 'u'); f['et' + c] = L.at(g, o, c, 't');
    f['al' + c] = (T.elim < 0 || T.elim >= c) && g.rounds > c ? 1 : 0;
    f['sp' + c] = sum(T.spl.slice(0, c / 10)); f['spc' + c] = sum(T.splC.slice(0, c / 10));
    const p = T.pos.find(r => r[0] === c), q = E.pos.find(r => r[0] === c);
    if (p && p[1] > 0) { f['own' + c] = p[2] / p[1]; f['neu' + c] = p[3] / p[1]; f['en' + c] = p[4] / p[1]; f['ad' + c] = p[5] / 10; f['a3' + c] = p[6] / p[1]; f['ed' + c] = p[7] / 10; f['e3' + c] = p[8] / p[1]; f['cor' + c] = p[9] / p[1]; }
    if (q && q[1] > 0) f['raid' + c] = q[4]; // enemy heads inside our territory
  }
  // deaths before r30 / r50 / r100 (stubs apart), from the aggregated table phase|cause|lc|sw|mech
  for (const c of [30, 50, 100]) {
    let ho = 0, trap = 0, body = 0, oth = 0, stub = 0, sw = 0, n = 0, len = 0;
    for (const [k, v] of Object.entries(T.dth)) {
      const [ph, cause, , s, mech] = k.split('|').map(Number);
      if (ph >= PHC[c]) continue;
      if (mech === 1 && cause !== 2 && cause !== 3) { stub += v[0]; continue; }
      n += v[0]; len += v[1]; if (s) sw += v[0];
      if (cause === 2 || cause === 3) ho += v[0]; else if (cause === 1) trap += v[0]; else if (cause === 4) body += v[0]; else oth += v[0];
    }
    f['dn' + c] = n; f['dho' + c] = ho; f['dtrap' + c] = trap; f['dbody' + c] = body; f['doth' + c] = oth; f['dstub' + c] = stub; f['dsw' + c] = sw; f['dlen' + c] = len;
  }
  // net splits (splits minus stub deaths: an escape-split loop adds no unit) by r50 / r100, and in r100-299; the lowest unit
  // count from r50 while the team is alive and the game runs; units at r150 / r200
  const stubBy = (a, b) => { let n = 0; for (const [k, v] of Object.entries(T.dth)) { const [ph, cause, , , mech] = k.split('|').map(Number); if (ph >= a && ph < b && mech === 1 && cause !== 2 && cause !== 3) n += v[0]; } return n; };
  f.nsp50 = sum(T.spl.slice(0, 5)) - stubBy(0, 2); f.nsp100 = sum(T.spl.slice(0, 10)) - stubBy(0, 3); f.nsp100_299 = sum(T.spl.slice(10, 30)) - stubBy(3, 5);
  { let mn = 99; const end = T.elim >= 0 ? T.elim : g.rounds; for (let r = 50; r < end; r += 5) mn = Math.min(mn, L.at(g, tm, r, 'u')); f.umin50 = end > 50 ? mn : null; }
  f.u150 = L.at(g, tm, 150, 'u'); f.u200 = L.at(g, tm, 200, 'u'); f.al150 = (T.elim < 0 || T.elim >= 150) && g.rounds > 150 ? 1 : 0; f.al200 = (T.elim < 0 || T.elim >= 200) && g.rounds > 200 ? 1 : 0;
  f.k100 = L.at(g, tm, 100, 'k'); f.eu150 = L.at(g, o, 150, 'u'); f.eu200 = L.at(g, o, 200, 'u');
  const turns = sum(T.turns.map(r => sum(r))), swT = sum(T.swT);
  f.swRate = turns ? swT / turns : 0; f.turns = turns; f.swT = swT; f.sw = T.sw; f.turnsM = T.turns; f.swTl = T.swT;
  f.cls = T.elim >= 0 ? L.classOf(T.elim, T.kd) : null;
  f.last = T.last; f.kd = T.kd;
  return f;
}
const TF = [];
for (const g of G) { const w = g.winner, l = w === 'A' ? 'B' : 'A'; TF.push(feat(g, w, 'W')); TF.push(feat(g, l, g.T[l].end.u === 0 ? 'LX' : 'LS')); }
// ours on the same maps: g4 family and proxy family, grouped by our outcome
const OF = [];
for (const g of ON) OF.push(feat(g, g.us, (g.fam === 'g4' ? 'g4' : 'px') + (g.win ? 'W' : g.elim ? 'LX' : 'LS')));

P('# 상위권 패자: 살아남는 쪽과 전멸하는 쪽 (exp/eliminations/top.js)', '');
P(`- 상위권끼리 모집단: 키 스냅숏 ${TOPD.n}판 중 제외 ${TOPD.excl.stalled + TOPD.excl.faults}판(멈춘 팀 ${TOPD.excl.stalled}, 시간 초과 사망 ≥3 ${TOPD.excl.faults}), 승자가 있는 판 ${G.length}판. 팀·경기 ${TF.length}개.`);
P(`- 복원 점검 합: ${JSON.stringify(TOPD.games.reduce((a, g) => { for (const [k, v] of Object.entries(g.chk)) a[k] = (a[k] || 0) + v; return a; }, {}))}`);
P(`- 우리 판: 온라인 ${ON.length}판(같은 캐시).`, '');

const MLS = [...new Set(TF.map(f => f.ml))].sort();
// ---- A. outcomes per map
P('## A. 지도·판본별 결과', '');
{
  const rows = [];
  for (const ml of MLS) {
    const S = TF.filter(f => f.ml === ml), W = S.filter(f => f.grp === 'W'), LS = S.filter(f => f.grp === 'LS'), LX = S.filter(f => f.grp === 'LX');
    const O = OF.filter(f => f.ml === ml && f.grp.startsWith('g4')), OX = O.filter(f => f.grp === 'g4LX');
    rows.push([ml, W.length, LS.length, LX.length, pc(LX.length, LS.length + LX.length), LX.length ? f1(med(LX.map(f => f.elim))) : '–', O.length, pc(OX.length, O.length - O.filter(f => f.grp === 'g4W').length), OX.length ? f1(med(OX.map(f => f.elim))) : '–']);
  }
  P(table(['지도·판본', '상위 판', '패자 생존(LS)', '패자 전멸(LX)', '패자 전멸률', 'LX 전멸 라운드 중앙', '우리 g4 판', '우리 g4 패배 중 전멸률', '우리 전멸 라운드 중앙'], rows, ['l']), '');
}

// ---- B. the elite eliminated losers' classes, vs ours
P('## B. 전멸 부류: 상위권 LX 대 우리(같은 규칙)', '');
{
  const CLS = ['E1', 'E2', 'E3m', 'E3l'];
  const rows = [];
  for (const ml of MLS) {
    const X = TF.filter(f => f.ml === ml && f.grp === 'LX'), O = OF.filter(f => f.ml === ml && f.elim >= 0);
    rows.push([ml, X.length, ...CLS.map(c => pc(X.filter(f => f.cls === c).length, X.length)), O.length, ...CLS.map(c => pc(O.filter(f => f.cls === c).length, O.length))]);
  }
  const X = TF.filter(f => f.grp === 'LX'), O = OF.filter(f => f.elim >= 0);
  rows.push(['전체', X.length, ...CLS.map(c => pc(X.filter(f => f.cls === c).length, X.length)), O.length, ...CLS.map(c => pc(O.filter(f => f.cls === c).length, O.length))]);
  P(table(['지도·판본', '상위 LX', ...CLS.map(c => '상위 ' + c), '우리 전멸', ...CLS.map(c => '우리 ' + c)], rows, ['l']), '');
}

// ---- C. growth and position at r10/r30/r50/r100, per map, per group
const GRPS = [['W', '상위 승자'], ['LS', '상위 패자 생존'], ['LX', '상위 패자 전멸'], ['g4LS', '우리 g4 패배 생존'], ['g4LX', '우리 g4 전멸'], ['pxLX', '우리 흉내 전멸']];
function grpRows(S, cols) {
  const rows = [];
  for (const [k, lab] of GRPS) {
    const X = S.filter(f => f.grp === k); if (!X.length) continue;
    rows.push([lab, X.length, ...cols.map(([, fn]) => fn(X))]);
  }
  return rows;
}
const mAt = (key, alive) => X => { const Y = alive ? X.filter(f => f['al' + alive]) : X; const v = Y.map(f => f[key]).filter(v => v !== undefined); return f1(mean(v)); };
const mPct = (key, alive) => X => { const Y = alive ? X.filter(f => f['al' + alive]) : X; const v = Y.map(f => f[key]).filter(v => v !== undefined); return v.length ? Math.round(100 * mean(v)) + '%' : '–'; };
const COLS_GROW = [
  ['r10 수', mAt('u10')], ['r30 수', mAt('u30')], ['r50 수', mAt('u50')], ['r100 수', mAt('u100')], ['r100 수(살아 있는 팀)', mAt('u100', 100)],
  ['r30 총길이', mAt('t30')], ['r50 총길이', mAt('t50')], ['r100 총길이', mAt('t100')], ['r50 최장', mAt('k50')],
  ['r50까지 순분열', mAt('nsp50')], ['r100까지 순분열', mAt('nsp100')], ['r100–299 순분열(살아 있는 팀)', mAt('nsp100_299', 200)],
  ['r150 수(살아 있는 팀)', mAt('u150', 150)], ['r200 수(살아 있는 팀)', mAt('u200', 200)], ['r50 뒤 가장 적은 수', X => f1(mean(X.map(f => f.umin50).filter(v => v !== null)))],
  ['r30 상대 수', mAt('eu30')], ['r50 상대 수', mAt('eu50')], ['r100 상대 수', mAt('eu100')],
];
const COLS_POS = [
  ['r30 제 영토', mPct('own30', 30)], ['r30 적 영토', mPct('en30', 30)], ['r50 제 영토', mPct('own50', 50)], ['r50 적 영토', mPct('en50', 50)], ['r100 적 영토', mPct('en100', 100)],
  ['r50 가까운 아군 거리', mAt('ad50', 50)], ['r50 아군 3칸 안', mPct('a350', 50)], ['r50 가까운 적 거리', mAt('ed50', 50)], ['r50 적 3칸 안', mPct('e350', 50)],
  ['r50 통로 칸', mPct('cor50', 50)], ['r50 우리 영토 안 적 머리', mAt('raid50', 50)], ['r100 우리 영토 안 적 머리', mAt('raid100', 100)],
];
const COLS_DEATH = [
  ['r50 전 죽음(토막 제외)', mAt('dn50')], ['그중 머리 맞부딪힘', mAt('dho50')], ['갇힘', mAt('dtrap50')], ['떼 속', mAt('dsw50')], ['토막', mAt('dstub50')],
  ['r100 전 죽음', mAt('dn100')], ['그중 머리 맞부딪힘', mAt('dho100')], ['갇힘', mAt('dtrap100')], ['떼 속', mAt('dsw100')],
  ['떼 턴 비율', X => pc(sum(X.map(f => f.swT)), sum(X.map(f => f.turns)))],
];
for (const [title, cols] of [['C. 초반 성장(수·총길이·분열, 상대 수)', COLS_GROW], ['D. 머무는 곳(r30·r50·r100의 머리 위치; 살아 있는 팀만)', COLS_POS], ['E. 초반 손실과 떼(r50·r100 전, 판당)', COLS_DEATH]]) {
  P('## ' + title, '');
  const rowsAll = [];
  for (const kind of ['elim', 'r500']) {
    const S = TF.filter(f => L.kindOf(f.map) === kind).concat(OF.filter(f => L.kindOf(f.map) === kind));
    for (const r of grpRows(S, cols)) rowsAll.push([(kind === 'elim' ? '전멸형' : '500형') + ' ' + r[0], ...r.slice(1)]);
  }
  P('### 지도 종류별', '', table(['집단', 'N', ...cols.map(c => c[0])], rowsAll, ['l']), '');
  const rowsMap = [];
  for (const ml of MLS) {
    const S = TF.filter(f => f.ml === ml).concat(OF.filter(f => f.ml === ml));
    for (const r of grpRows(S, cols)) rowsMap.push([ml + ' ' + r[0], ...r.slice(1)]);
  }
  P('### 지도·판본별', '', table(['지도·판본 집단', 'N', ...cols.map(c => c[0])], rowsMap, ['l']), '');
}

// ---- C2. share of team-games at or above a unit count (elimination maps), alive or not
P('## C2. 전멸형 지도: 수가 기준 이상인 팀·경기 비율', '');
{
  const rows = [];
  for (const [k, lab] of GRPS) {
    const X = TF.concat(OF).filter(f => f.grp === k && L.kindOf(f.map) === 'elim'); if (!X.length) continue;
    rows.push([lab, X.length, ...[[30, 4], [30, 6], [50, 4], [50, 6], [50, 8], [100, 6], [100, 10]].map(([c, u]) => pc(X.filter(f => f['u' + c] >= u).length, X.length)), f1(mean(X.map(f => f.umin50).filter(v => v !== null)))]);
  }
  P(table(['집단', 'N', 'r30 ≥4', 'r30 ≥6', 'r50 ≥4', 'r50 ≥6', 'r50 ≥8', 'r100 ≥6', 'r100 ≥10', 'r50 뒤 최소 수(평균)'], rows, ['l']), '');
}

// ---- F. within-opponent comparison: same map, same winning team; LS - LX
P('## F. 같은 지도·같은 승자 팀 안에서 LS − LX (상대 세기 통제)', '');
{
  const KEYS = [['u10', 'r10 수'], ['u30', 'r30 수'], ['u50', 'r50 수'], ['t30', 'r30 총길이'], ['t50', 'r50 총길이'], ['k50', 'r50 최장'], ['sp30', 'r30까지 분열'], ['sp50', 'r50까지 분열'],
    ['u100', 'r100 수'], ['k100', 'r100 최장'], ['nsp50', 'r50까지 순분열'], ['nsp100', 'r100까지 순분열'], ['raid50', 'r50 우리 영토 안 적 머리'],
    ['eu30', 'r30 상대 수'], ['eu50', 'r50 상대 수'], ['own30', 'r30 제 영토'], ['en30', 'r30 적 영토'], ['a330', 'r30 아군 3칸 안'], ['ad30', 'r30 가까운 아군 거리'], ['e330', 'r30 적 3칸 안'], ['cor30', 'r30 통로 칸'], ['dn50', 'r50 전 죽음'], ['dho50', 'r50 전 맞부딪힘'], ['swRate', '떼 턴 비율']];
  const rows = [];
  for (const kind of ['elim', 'r500', 'all']) {
    const cells = new Map();
    for (const f of TF) {
      if (f.grp === 'W' || (kind !== 'all' && L.kindOf(f.map) !== kind)) continue;
      const k = f.ml + '|' + f.opp; if (!cells.has(k)) cells.set(k, { S: [], X: [] });
      cells.get(k)[f.grp === 'LS' ? 'S' : 'X'].push(f);
    }
    const use = [...cells.values()].filter(c => c.S.length && c.X.length);
    const nS = sum(use.map(c => c.S.length)), nX = sum(use.map(c => c.X.length));
    for (const [key, lab] of KEYS) {
      let wsum = 0, dsum = 0, sS = 0, sX = 0; const diffs = [];
      for (const c of use) {
        const a = c.S.map(f => f[key]).filter(v => v !== undefined), b = c.X.map(f => f[key]).filter(v => v !== undefined);
        if (!a.length || !b.length) continue;
        const w = Math.min(a.length, b.length), d = mean(a) - mean(b);
        wsum += w; dsum += w * d; sS += w * mean(a); sX += w * mean(b); diffs.push({ w, d });
      }
      // bootstrap over cells
      let s = 7; const rnd = () => { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; };
      const bs = []; for (let b = 0; b < 400; b++) { let W = 0, D = 0; for (let i = 0; i < diffs.length; i++) { const x = diffs[Math.floor(rnd() * diffs.length)]; W += x.w; D += x.w * x.d; } bs.push(D / W); }
      const pct = /^(own|en|a3|e3|cor|swRate)/.test(key);
      const fmt = v => pct ? (Math.round(1000 * v) / 10).toFixed(1) + '%p' : f2(v);
      rows.push([kind === 'elim' ? '전멸형' : kind === 'r500' ? '500형' : '전체', lab, use.length, nS, nX, pct ? (Math.round(1000 * sS / wsum) / 10).toFixed(1) + '%' : f2(sS / wsum), pct ? (Math.round(1000 * sX / wsum) / 10).toFixed(1) + '%' : f2(sX / wsum), fmt(dsum / wsum), `[${fmt(quant(bs, 0.025))}, ${fmt(quant(bs, 0.975))}]`]);
    }
  }
  P(table(['지도 종류', '특징', '칸(지도×승자)', 'LS', 'LX', 'LS 평균', 'LX 평균', 'LS − LX', '95% 구간(칸 붓스트랩)'], rows, ['l', 'l']), '');
  P('- 칸 = (지도·판본, 승자 팀). LS와 LX가 모두 있는 칸만 쓴다. 칸마다 평균 차이를 min(LS 수, LX 수)로 가중한다. 살아 있지 않은 팀의 r30·r50 값은 0(수)이거나 비어 있다(위치).', '');
}

// ---- G. swarm response
P('## G. 떼 턴(시야 안 적 머리 ≥2이고 아군보다 많음)의 대응과 결과', '');
function swRows(X, lab) {
  const acc = { turns: [0, 0, 0, 0, 0], swT: [0, 0, 0, 0, 0], resp: {} };
  for (const f of X) { for (let lc = 0; lc < 5; lc++) { acc.turns[lc] += sum(f.turnsM[lc]); acc.swT[lc] += f.swTl[lc]; } for (const [k, v] of Object.entries(f.sw)) { const a = acc.resp[k] || (acc.resp[k] = [0, 0, 0]); a[0] += v[0]; a[1] += v[1]; a[2] += v[2]; } }
  const rows = [];
  for (const lcs of [[0], [1], [2], [3, 4]]) {
    const R = Object.entries(acc.resp).filter(([k]) => lcs.includes(+k.split('|')[0]));
    const n = sum(R.map(([, v]) => v[0]));
    const by = fn => { const x = R.filter(([k]) => fn(k.split('|'))); return [sum(x.map(([, v]) => v[0])), sum(x.map(([, v]) => v[2]))]; };
    const sp = by(k => k[1] === 'split'), sr = by(k => k[1] === 'sprint'), aw = by(k => k[1] === 'step' && k[2] === '1'), st = by(k => k[1] === 'step' && k[2] === '0'), to = by(k => k[1] === 'step' && k[2] === '-1'), rm = by(k => k[1] === 'ram');
    const tt = sum(lcs.map(i => acc.turns[i])), sT = sum(lcs.map(i => acc.swT[i]));
    rows.push([lab, ['L2', 'L3–4', 'L5–7', 'L8+'][lcs[0] === 3 ? 3 : lcs[0]], X.length, tt, pc(sT, tt), n, pc(sp[0], n), pc(sr[0], n), pc(aw[0], n), pc(st[0], n), pc(to[0], n), pc(rm[0], n), pc(sum(R.map(([, v]) => v[2])), n), pc(sp[1], sp[0]), pc(aw[1], aw[0]), pc(st[1], st[0]), pc(to[1], to[0])]);
  }
  return rows;
}
{
  const rows = [];
  for (const kind of ['elim', 'r500']) for (const [k, lab] of GRPS) {
    const X = TF.concat(OF).filter(f => f.grp === k && L.kindOf(f.map) === kind); if (!X.length) continue;
    rows.push(...swRows(X, (kind === 'elim' ? '전멸형 ' : '500형 ') + lab));
  }
  P(table(['집단', '길이', '팀·경기', '턴', '떼 턴 비율', '떼 턴', '분열', '질주', '한 걸음 멀어짐', '그대로', '다가감', '박음', '10라운드 뒤 몸 생존', '생존: 분열', '생존: 멀어짐', '생존: 그대로', '생존: 다가감'], rows, ['l', 'l']), '');
}

// ---- H. the last deaths of eliminated teams: elite LX vs ours
P('## H. 전멸한 팀의 마지막 세 죽음: 상위권 LX 대 우리', '');
{
  const MODES = ['sprintRam', 'stepRam', 'ourRam', 'trapE', 'trapSelf', 'enemyBody', 'sac', 'allyHead', 'stub'];
  const rows = [];
  for (const kind of ['elim', 'r500']) for (const [k, lab] of [['LX', '상위 LX'], ['g4LX', '우리 g4 전멸'], ['pxLX', '우리 흉내 전멸']]) {
    const X = TF.concat(OF).filter(f => f.grp === k && L.kindOf(f.map) === kind); if (!X.length) continue;
    const D = X.flatMap(f => f.last.slice(-3));
    const Rm = D.filter(d => d[2] === 2), longer = Rm.filter(d => d[7] + Math.max(0, d[3] - 1) > d[1]).length;
    rows.push([(kind === 'elim' ? '전멸형 ' : '500형 ') + lab, X.length, D.length, f1(mean(D.map(d => d[1]))), ...MODES.map(m => pc(D.filter(d => L.modeOf(d) === m).length, D.length)), pc(D.filter(d => d[4] >= 2).length, D.length), f1(mean(D.map(d => d[10]))), pc(longer, Rm.length)]);
  }
  P(table(['집단', '팀', '죽음', '평균 길이', ...MODES.map(m => L.MODE_KO[m]), '떼 속(eV≥2)', '그때 상대 수', '박힘 중 더 긴 적(이동 전)'], rows, ['l']), '');
}

// ---- I. low-unit episodes: the first time from r50 a team is down to <= 3 dragons while the enemy has >= 8. Recovery = >= 4 dragons
// 20 rounds later; death = eliminated within 50 rounds; splits in the 20 rounds (10-round bins, net of stub deaths is not
// available per bin, so gross splits)
P('## I. 수가 3 이하로 떨어진 뒤(상대 ≥8, r50 이후 처음): 회복과 전멸', '');
{
  const rows = [];
  for (const kind of ['elim', 'r500']) for (const [k, lab] of GRPS) {
    const X = TF.concat(OF).filter(f => f.grp === k && L.kindOf(f.map) === kind); if (!X.length) continue;
    let n = 0, rec = 0, die = 0, sp = 0, len = 0, kmax = 0; const at0 = [];
    for (const f of X) {
      const g = f.g, tm = f.tm, o = tm === 'A' ? 'B' : 'A', T = g.T[tm], end = T.elim >= 0 ? T.elim : g.rounds;
      for (let r = 50; r + 20 < g.rounds && r < end; r += 5) {
        const u = L.at(g, tm, r, 'u'), eu = L.at(g, o, r, 'u');
        if (u > 3 || u === 0 || eu < 8) continue;
        n++; at0.push(r); len += L.at(g, tm, r, 't'); kmax += L.at(g, tm, r, 'k');
        const u20 = L.at(g, tm, r + 20, 'u'); if (u20 >= 4 && L.alive(g, tm, r + 20)) rec++;
        if (T.elim >= 0 && T.elim <= r + 50) die++;
        sp += sum(T.spl.slice(Math.floor(r / 10), Math.floor(r / 10) + 2));
        break;
      }
    }
    rows.push([(kind === 'elim' ? '전멸형 ' : '500형 ') + lab, X.length, n, pc(n, X.length), f1(med(at0)), f1(len / Math.max(1, n)), f1(kmax / Math.max(1, n)), pc(rec, n), pc(die, n), f1(sp / Math.max(1, n))]);
  }
  P(table(['집단', '팀·경기', '그런 때가 있음', '비율', '처음 라운드(중앙)', '그때 총길이', '그때 최장', '20라운드 뒤 4마리 이상', '50라운드 안 전멸', '그 20라운드 분열'], rows, ['l']), '');
}

// summary json for the doc
const summary = { nTop: TOPD.n, excl: TOPD.excl, nGames: G.length, nTeamGames: TF.length };
fs.writeFileSync(path.resolve(L.ROOT, opt('out', 'exp/eliminations/numbers-top.md')), out.join('\n') + '\n');
fs.writeFileSync(path.resolve(L.ROOT, opt('json', 'exp/eliminations/top-summary.json')), JSON.stringify(summary, null, 1));
console.log('wrote numbers-top.md;', G.length, 'top games,', ON.length, 'online games');
