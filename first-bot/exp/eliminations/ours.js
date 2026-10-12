#!/usr/bin/env node
// Q1: how do we get eliminated? Stage 1 (compute over all 15 sets) and stage 2 (classify), from exp/eliminations/cache.
// usage: node exp/eliminations/ours.js [--out exp/eliminations/numbers-ours.md] [--sel exp/eliminations/selection-ours.json]
'use strict';
const fs = require('fs'), path = require('path');
const L = require('./lib.js');
const { table, f1, f2, pc, mean, med, quant, sum } = L;

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const G = L.loadOnline();
const out = [];
const P = (...a) => out.push(a.join('\n'));

const elimG = G.filter(g => g.elim);
P('# 우리 전멸 수치 (exp/eliminations/ours.js)', '');
P(`- 모집단: 온라인 ${L.SETS.length}세트 ${G.length}판. 극상위권 6팀 ${G.filter(g => g.elite).length}판, DEV ${G.filter(g => g.dev).length}판, 기타 ${G.filter(g => !g.elite && !g.dev).length}판.`);
P(`- 복원 점검 합: ${JSON.stringify(G.reduce((a, g) => { for (const [k, v] of Object.entries(g.chk)) a[k] = (a[k] || 0) + v; return a; }, {}))}`);
P(`- 우리 전멸: ${elimG.length}판 (${pc(elimG.length, G.length)}). 상대 전멸: ${G.filter(g => g.E.end.u === 0).length}판.`, '');

// ---- A. per set
P('## A. 세트(봇)별', '');
{
  const rows = [];
  for (const [set, bot, fam] of L.SETS) {
    const S = G.filter(g => g.set === set), E = S.filter(g => g.elim);
    const el = S.filter(g => L.ELIM_MAPS.includes(g.map)), r5 = S.filter(g => !L.ELIM_MAPS.includes(g.map));
    rows.push([set, bot, fam, S.length, S.filter(g => g.win).length, E.length, pc(E.length, S.length), `${el.filter(g => g.elim).length}/${el.length}`, `${r5.filter(g => g.elim).length}/${r5.length}`,
      E.length ? f1(med(E.map(g => g.U.elim))) : '–']);
  }
  P(table(['세트', '봇', '계열', '판', '승', '전멸', '전멸률', '전멸형 지도 전멸', '500형 지도 전멸', '전멸 라운드 중앙'], rows, ['l', 'l', 'l']), '');
}

// ---- B. per map x layout, per opponent
P('## B. 지도·판본별, 상대별', '');
const MLS = [...new Set(G.map(g => g.ml2))].sort();
{
  const rows = [];
  for (const ml of MLS) {
    const S = G.filter(g => g.ml2 === ml), E = S.filter(g => g.elim);
    const er = E.map(g => g.U.elim);
    rows.push([ml, L.kindOf(S[0].map), S.length, E.length, pc(E.length, S.length), er.length ? `${f1(quant(er, 0.25))} / ${f1(med(er))} / ${f1(quant(er, 0.75))}` : '–',
      `${S.filter(g => g.fam === 'g4' && g.elim).length}/${S.filter(g => g.fam === 'g4').length}`, `${S.filter(g => g.fam === 'proxy' && g.elim).length}/${S.filter(g => g.fam === 'proxy').length}`]);
  }
  P(table(['지도·판본', '종류', '판', '전멸', '전멸률', '전멸 라운드 q1 / 중앙 / q3', 'g4 계열 전멸', '흉내 계열 전멸'], rows, ['l', 'l']), '');
  const unknownLay = G.filter(g => g.layout === '?' || g.layout === 'x');
  P(`- 판본을 못 가린 판: ${unknownLay.length} (${unknownLay.map(g => g.key).slice(0, 10).join(', ')}). lay(생성 판별)와 lay2(variants.json/생성 수)가 다른 판: ${G.filter(g => ['Devil', 'Queen Of Spades', 'Schooltime', 'Slithery Fight'].includes(g.map) && (g.lay === 'a' || g.lay === 'b') && g.lay2 && g.lay2 !== g.lay).length}.`, '');
  const opps = [...new Set(G.map(g => g.oppName))];
  const rows2 = [];
  for (const o of opps) {
    const S = G.filter(g => g.oppName === o), E = S.filter(g => g.elim);
    rows2.push([o, S.length, S.filter(g => g.win).length, E.length, pc(E.length, S.length), E.length ? f1(med(E.map(g => g.U.elim))) : '–',
      `${E.filter(g => L.ELIM_MAPS.includes(g.map)).length}/${S.filter(g => L.ELIM_MAPS.includes(g.map)).length}`, `${E.filter(g => !L.ELIM_MAPS.includes(g.map)).length}/${S.filter(g => !L.ELIM_MAPS.includes(g.map)).length}`]);
  }
  rows2.sort((a, b) => b[3] - a[3]);
  P(table(['상대', '판', '우리 승', '전멸', '전멸률', '전멸 라운드 중앙', '전멸형 지도', '500형 지도'], rows2, ['l']), '');
}

// ---- C. trajectories
P('## C. 수와 총길이의 궤적 (전멸한 판 대 전멸하지 않은 판, 같은 지도)', '');
const CPS = [0, 10, 20, 30, 50, 75, 100, 150, 200, 250, 300, 400];
function traj(S, label) {
  const row = w => CPS.map(r => { const xs = S.map(g => L.at(g, w === 'us' ? g.us : g.them, r, 'u')); return f1(mean(xs)); });
  const rowT = w => CPS.map(r => { const xs = S.map(g => L.at(g, w === 'us' ? g.us : g.them, r, 't')); return f1(mean(xs)); });
  return [[label + ' 우리 수', S.length, ...row('us')], [label + ' 상대 수', S.length, ...row('them')], [label + ' 우리 총길이', S.length, ...rowT('us')], [label + ' 상대 총길이', S.length, ...rowT('them')]];
}
{
  const rows = [];
  for (const kind of ['elim', 'r500']) {
    const S = G.filter(g => L.kindOf(g.map) === kind);
    rows.push(...traj(S.filter(g => g.elim), (kind === 'elim' ? '전멸형' : '500형') + ' 전멸'));
    rows.push(...traj(S.filter(g => !g.elim), (kind === 'elim' ? '전멸형' : '500형') + ' 생존'));
  }
  P(table(['집단', 'N', ...CPS.map(r => 'r' + r)], rows, ['l']), '');
  P('- 전멸 뒤는 0으로 센다(우리 쪽). 판이 끝난 뒤는 끝 상태를 그대로 쓴다.', '');
}

// ---- D. classes
P('## D. 전멸 부류', '');
for (const g of elimG) {
  g.cls = L.classOf(g.U.elim, g.U.kd);
  g.kingEarlier = L.kingLostEarlier(g.U.elim, g.U.kd) ? 1 : 0;
  let pk = 0, pkR = 0; for (let r = 0; r < g.rounds; r++) { const u = L.at(g, g.us, r, 'u'); if (u > pk) { pk = u; pkR = r; } }
  g.peakU = pk; g.peakR = pkR;
  let pkT = 0; for (let r = 0; r < g.rounds; r++) pkT = Math.max(pkT, L.at(g, g.us, r, 't'));
  g.peakT = pkT;
  const ourD = g.deaths.slice().sort((a, b) => a.r - b.r || a.id - b.id);
  g.last3 = ourD.slice(-3);
  g.lastMode = g.last3.length ? L.modeOf(rowOf(g.last3[g.last3.length - 1])) : null;
  g.eAtE = L.at(g, g.them, Math.max(0, g.U.elim - 20), 'u'); g.uAtE = L.at(g, g.us, Math.max(0, g.U.elim - 20), 'u');
}
function rowOf(d) { return [d.r, d.len, d.cause, d.ks, d.eV, d.aV, d.king, d.klen, d.kage, d.u, d.eu, d.blk, d.eMin, d.portal, d.mech]; }
const CLS = ['E1', 'E2', 'E3m', 'E3l'];
{
  const rows = [];
  for (const c of CLS) {
    const S = elimG.filter(g => g.cls === c);
    rows.push([c + ' ' + L.CLASS_KO[c], S.length, pc(S.length, elimG.length), f1(med(S.map(g => g.U.elim))), f1(mean(S.map(g => g.peakU))), f1(mean(S.map(g => g.peakT))),
      f1(mean(S.map(g => L.at(g, g.us, 30, 'u')))), f1(mean(S.map(g => L.at(g, g.them, 30, 'u')))), f1(mean(S.map(g => g.uAtE))), f1(mean(S.map(g => g.eAtE))),
      S.filter(g => g.kingEarlier).length]);
  }
  P(table(['부류', '판', '비율', '전멸 라운드 중앙', '최대 수(평균)', '최대 총길이(평균)', 'r30 우리 수', 'r30 상대 수', '전멸 20라운드 전 우리 수', '같은 때 상대 수', '더 일찍 왕을 잃음'], rows, ['l']), '');
  // by map/layout
  const rows2 = [];
  for (const ml of MLS) {
    const S = elimG.filter(g => g.ml2 === ml); if (!S.length) continue;
    rows2.push([ml, G.filter(g => g.ml2 === ml).length, S.length, ...CLS.map(c => S.filter(g => g.cls === c).length)]);
  }
  P('### 지도·판본별 부류 크기', '', table(['지도·판본', '판', '전멸', ...CLS], rows2, ['l']), '');
  const rows3 = [];
  for (const o of [...new Set(G.map(g => g.oppName))]) {
    const S = elimG.filter(g => g.oppName === o); if (!S.length) continue;
    rows3.push([o, G.filter(g => g.oppName === o).length, S.length, ...CLS.map(c => S.filter(g => g.cls === c).length)]);
  }
  rows3.sort((a, b) => b[2] - a[2]);
  P('### 상대별 부류 크기', '', table(['상대', '판', '전멸', ...CLS], rows3, ['l']), '');
  const rows4 = [];
  for (const [set, bot, fam] of L.SETS) {
    const S = elimG.filter(g => g.set === set);
    rows4.push([set, fam, 70, S.length, ...CLS.map(c => S.filter(g => g.cls === c).length)]);
  }
  P('### 세트별 부류 크기', '', table(['세트', '계열', '판', '전멸', ...CLS], rows4, ['l', 'l']), '');
  // class x map kind x layout (b maps)
  const rows5 = [];
  for (const lay of ['a', 'b']) for (const m of ['Devil', 'Queen Of Spades', 'Schooltime', 'Slithery Fight', 'Prisoners Dilemma']) {
    const S = G.filter(g => g.map === m && g.layout === lay), E = S.filter(g => g.elim);
    rows5.push([m + ' ' + (m === 'Prisoners Dilemma' ? (lay === 'a' ? '6마리' : '10마리') : lay), S.length, E.length, pc(E.length, S.length), ...CLS.map(c => E.filter(g => g.cls === c).length)]);
  }
  P('### 판본이 둘인 지도: 판본별', '', table(['지도 판본', '판', '전멸', '전멸률', ...CLS], rows5, ['l']), '');
}

// ---- D2. per-class trajectories and exchange
{
  const rows = [];
  const pts = [['r10', g => 10], ['r30', g => 30], ['r50', g => 50], ['r100', g => 100], ['전멸−50', g => Math.max(0, g.U.elim - 50)], ['전멸−20', g => Math.max(0, g.U.elim - 20)], ['전멸−5', g => Math.max(0, g.U.elim - 5)]];
  for (const c of CLS) {
    const S = elimG.filter(g => g.cls === c);
    rows.push([c + ' 우리 수 / 상대 수', S.length, ...pts.map(([, f]) => f1(mean(S.map(g => L.at(g, g.us, f(g), 'u')))) + ' / ' + f1(mean(S.map(g => L.at(g, g.them, f(g), 'u')))))]);
    rows.push([c + ' 우리 총길이 / 상대 총길이', S.length, ...pts.map(([, f]) => f1(mean(S.map(g => L.at(g, g.us, f(g), 't')))) + ' / ' + f1(mean(S.map(g => L.at(g, g.them, f(g), 't')))))]);
    rows.push([c + ' 우리 최장 / 상대 최장', S.length, ...pts.map(([, f]) => f1(mean(S.map(g => L.at(g, g.us, f(g), 'k')))) + ' / ' + f1(mean(S.map(g => L.at(g, g.them, f(g), 'k')))))]);
  }
  P('### 부류별 궤적(평균)', '', table(['부류', '판', ...pts.map(p => p[0])], rows, ['l']), '');
  // exchange: our non-stub losses vs the enemy's losses caused by us (they rammed us / we rammed them / they hit our body)
  const rows2 = [];
  for (const c of [...CLS, 'none']) {
    const S = c === 'none' ? G.filter(g => !g.elim) : elimG.filter(g => g.cls === c);
    let ourL = 0, ourHeadOn = 0, ourBody = 0, ourTrap = 0, ourSelf = 0, theirL = 0, theirHeadOn = 0, theirBody = 0, ourLlen = 0, theirLlen = 0;
    for (const g of S) {
      const tEnd = g.elim ? g.U.elim : g.rounds;
      for (const d of g.deaths) { if (d.mech === 1 && d.cause !== 2 && d.cause !== 3) continue; ourL++; ourLlen += d.len; if (d.cause === 2 || d.cause === 3) ourHeadOn++; else if (d.cause === 4) ourBody++; else if (d.cause === 1) ourTrap++; else ourSelf++; }
      for (const d of g.oppDeaths) { if (d[0] > tEnd) continue; if (d[2] === 2 || d[2] === 3) { theirHeadOn++; theirL++; theirLlen += d[1]; } else if (d[2] === 4) { theirBody++; theirL++; theirLlen += d[1]; } }
    }
    rows2.push([c === 'none' ? '전멸하지 않은 판' : c, S.length, f1(ourL / S.length), f1(ourHeadOn / S.length), f1(ourTrap / S.length), f1(ourBody / S.length), f1(ourSelf / S.length), f1(theirHeadOn / S.length), f1(theirBody / S.length),
      f2(theirL / Math.max(1, ourL)), f1(ourLlen / Math.max(1, ourL)), f1(theirLlen / Math.max(1, theirL))]);
  }
  P('### 교환: 판당 우리 손실(토막 제외) 대 우리 때문에 죽은 상대', '', table(['부류', '판', '우리 손실', '그중 머리 맞부딪힘', '갇힘', '적 몸통', '기타 자해', '상대 머리 맞부딪힘 손실', '상대가 우리 몸에 부딪힘', '상대 손실 / 우리 손실', '우리 손실 평균 길이', '상대 손실 평균 길이'], rows2, ['l']), '');
  P('- 머리 맞부딪힘은 두 머리가 함께 죽는다. 그래서 우리 쪽과 상대 쪽 수가 같다(한쪽이 먼저 전멸하면 그 뒤는 없다).', '');
}

// ---- E. death anatomy
P('## E. 죽음의 모양', '');
const MODES = ['sprintRam', 'stepRam', 'ourRam', 'trapE', 'trapSelf', 'enemyBody', 'sac', 'allyHead', 'stub', 'fault'];
{
  // all our deaths in eliminated games by phase x mode
  const PH = [[0, 30], [30, 50], [50, 100], [100, 200], [200, 300], [300, 400], [400, 501]];
  const rows = [];
  for (const [a, b] of PH) {
    const D = elimG.flatMap(g => g.deaths.filter(d => d.r >= a && d.r < b));
    const cnt = m => D.filter(d => L.modeOf(rowOf(d)) === m).length;
    rows.push([`r${a}–${b - 1}`, D.length, f1(mean(D.map(d => d.len))), ...MODES.map(m => cnt(m)), pc(D.filter(d => d.eV >= 2).length, D.length)]);
  }
  P('### 전멸한 판의 우리 죽음 전부(국면 × 방식)', '', table(['국면', '죽음', '평균 길이', ...MODES.map(m => L.MODE_KO[m]), '떼 속(eV≥2)'], rows, ['l']), '');
  // the last three deaths by class
  const rows2 = [];
  for (const c of [...CLS, 'all']) {
    const S = c === 'all' ? elimG : elimG.filter(g => g.cls === c);
    const D = S.flatMap(g => g.last3);
    const cnt = m => D.filter(d => L.modeOf(rowOf(d)) === m).length;
    rows2.push([c, S.length, D.length, f1(mean(D.map(d => d.len))), ...MODES.slice(0, 9).map(m => cnt(m)), pc(D.filter(d => d.eV >= 2).length, D.length), pc(D.filter(d => d.eV >= 3).length, D.length),
      f1(mean(D.filter(d => d.cause === 2).map(d => d.klen))), pc(D.filter(d => d.cause === 2 && d.kage <= 2).length, D.filter(d => d.cause === 2).length)]);
  }
  P('### 마지막 세 드래곤의 죽음(부류별)', '', table(['부류', '판', '죽음', '평균 길이', ...MODES.slice(0, 9).map(m => L.MODE_KO[m]), '떼 속(eV≥2)', 'eV≥3', '박은 적의 평균 길이', '박은 적이 갓 태어남(≤2라운드)'], rows2, ['l']), '');
  // very last death: length class and king
  const rows3 = [];
  for (const c of [...CLS, 'all']) {
    const S = c === 'all' ? elimG : elimG.filter(g => g.cls === c);
    const D = S.map(g => g.last3[g.last3.length - 1]).filter(Boolean);
    rows3.push([c, D.length, D.filter(d => d.len <= 2).length, D.filter(d => d.len >= 3 && d.len <= 4).length, D.filter(d => d.len >= 5 && d.len <= 7).length, D.filter(d => d.len >= 8).length,
      f1(mean(D.map(d => d.eu))), ...MODES.slice(0, 9).map(m => D.filter(d => L.modeOf(rowOf(d)) === m).length)]);
  }
  P('### 맨 마지막 드래곤', '', table(['부류', '판', 'L2', 'L3–4', 'L5–7', 'L8+', '그때 상대 수(평균)', ...MODES.slice(0, 9).map(m => L.MODE_KO[m])], rows3, ['l']), '');
  // long dragons (>= 8) lost in eliminated games vs other games
  const rows4 = [];
  for (const [lab, S] of [['전멸한 판', elimG], ['전멸하지 않은 판', G.filter(g => !g.elim)]]) {
    const D = S.flatMap(g => g.deaths.filter(d => d.len >= 8));
    rows4.push([lab, S.length, D.length, f2(D.length / S.length), f1(mean(D.map(d => d.len))), ...MODES.slice(0, 9).map(m => D.filter(d => L.modeOf(rowOf(d)) === m).length), pc(D.filter(d => d.eV >= 2).length, D.length)]);
  }
  P('### 길이 8 이상 드래곤의 죽음', '', table(['집단', '판', '죽음', '판당', '평균 길이', ...MODES.slice(0, 9).map(m => L.MODE_KO[m]), '떼 속'], rows4, ['l']), '');
}

// ---- F. mechanisms (g4 family: labels)
P('## F. 무너질 때 켜져 있던 우리 기능 (g4 계열, 표식)', '');
const TOK = ['single', 'multi', 'esc', 'TRADE', 'vneg', 'doom', 'tg', 'tgx', 'T', 'g', 'K', 'grab', 'px', 'pxx', 'gx', 'PORTAL?', 'late', 'feed', 'conv', 'escsplit', 'escsplit2', 'noexit', 'lasttrade', 'split', 'frag', 'pocket'];
const tokOf = t => require('./extract.js').tokens(t);
{
  const g4 = G.filter(g => g.fam === 'g4');
  // last label of dying dragons: eliminated games' last-3 deaths vs all other deaths of ours (same maps)
  const ns = d => d.mech !== 1 || d.cause === 2 || d.cause === 3; // not an escape-split stub
  const grp = [['전멸한 판의 마지막 세 죽음', g4.filter(g => g.elim).flatMap(g => g.last3)], ['전멸한 판의 다른 죽음(토막 제외)', g4.filter(g => g.elim).flatMap(g => g.deaths.filter(d => !g.last3.includes(d) && ns(d)))],
    ['전멸하지 않은 판의 죽음(토막 제외)', g4.filter(g => !g.elim).flatMap(g => g.deaths.filter(ns))]];
  const rows = [];
  for (const [lab, D] of grp) {
    const has = t => D.filter(d => d.lbl && d.lblR >= d.r - 1 && tokOf(d.lbl).includes(t)).length;
    const cur = D.filter(d => d.lbl && d.lblR >= d.r - 1);
    rows.push([lab, D.length, cur.length, ...TOK.map(t => pc(has(t), cur.length))]);
  }
  P('### 죽은 드래곤의 마지막 표식(죽기 전 1라운드 안의 표식이 있는 경우)', '', table(['집단', '죽음', '표식 있음', ...TOK], rows, ['l']), '');
  // label rates per turn in the collapse window vs the same window of games on the same map that were not eliminated
  const rows2 = [];
  const rate = (S, win) => {
    const c = {}; let n = 0;
    for (const g of S) { const [a, b] = win(g); for (let bi = Math.floor(a / 10); bi <= Math.min(50, Math.floor(b / 10)); bi++) { const B = g.lab[bi] || {}; n += (B.move || 0) + ['feed', 'conv', 'escsplit', 'escsplit2', 'noexit', 'lasttrade', 'split', 'frag', 'pocket', 'degraded', 'csplit'].reduce((s, k) => s + (B[k] || 0), 0); for (const t of TOK) c[t] = (c[t] || 0) + (B[t] || 0); } }
    return { c, n };
  };
  for (const c of CLS) {
    const E = g4.filter(g => g.elim && g.cls === c); if (!E.length) continue;
    const x = rate(E, g => [Math.max(0, g.U.elim - 50), g.U.elim]);
    // reference: non-eliminated g4 games on the same maps, window = the same rounds (per map, median elimination round of the class)
    const ref = { c: {}, n: 0 };
    for (const m of [...new Set(E.map(g => g.map))]) {
      const Em = E.filter(g => g.map === m), mr = Math.round(med(Em.map(g => g.U.elim)));
      const y = rate(g4.filter(g => !g.elim && g.map === m), () => [Math.max(0, mr - 50), mr]);
      ref.n += y.n; for (const t of TOK) ref.c[t] = (ref.c[t] || 0) + (y.c[t] || 0);
    }
    rows2.push([c + ' 무너짐 창', E.length, x.n, ...TOK.map(t => (Math.round(1000 * (x.c[t] || 0) / Math.max(1, x.n)) / 10).toFixed(1))]);
    rows2.push([c + ' 같은 지도·라운드, 전멸 안 함', g4.filter(g => !g.elim && E.some(e => e.map === g.map)).length, ref.n, ...TOK.map(t => (Math.round(1000 * (ref.c[t] || 0) / Math.max(1, ref.n)) / 10).toFixed(1))]);
  }
  P('### 턴당 표식 비율(%): 전멸 전 50라운드 창 대 같은 지도·같은 라운드의 전멸하지 않은 판', '', table(['집단', '판', '턴', ...TOK], rows2, ['l']), '');
}

// ---- G. swarm turns of our dragons
P('## G. 떼 턴(시야 안 적 머리 ≥2이고 아군 머리보다 많음)', '');
function swarmRows(S, lab, tmOf) {
  const rows = [];
  const acc = { turns: [0, 0, 0, 0, 0], swT: [0, 0, 0, 0, 0], resp: {} };
  for (const g of S) { const T = g.T[tmOf(g)]; for (let lc = 0; lc < 5; lc++) { acc.turns[lc] += sum(T.turns[lc]); acc.swT[lc] += T.swT[lc]; } for (const [k, v] of Object.entries(T.sw)) { const a = acc.resp[k] || (acc.resp[k] = [0, 0, 0]); a[0] += v[0]; a[1] += v[1]; a[2] += v[2]; } }
  for (let lc = 0; lc < 5; lc++) {
    const R = Object.entries(acc.resp).filter(([k]) => +k.split('|')[0] === lc);
    const n = sum(R.map(([, v]) => v[0]));
    const by = f => { const x = R.filter(([k]) => f(k.split('|'))); return [sum(x.map(([, v]) => v[0])), sum(x.map(([, v]) => v[2]))]; };
    const sp = by(k => k[1] === 'split'), sr = by(k => k[1] === 'sprint'), aw = by(k => k[1] === 'step' && k[2] === '1'), st = by(k => k[1] === 'step' && k[2] === '0'), to = by(k => k[1] === 'step' && k[2] === '-1'), rm = by(k => k[1] === 'ram');
    const f10 = sum(R.map(([, v]) => v[2]));
    rows.push([lab, ['L2', 'L3–4', 'L5–7', 'L8–14', 'L15+'][lc], acc.turns[lc], pc(acc.swT[lc], acc.turns[lc]), n, pc(sp[0], n), pc(sr[0], n), pc(aw[0], n), pc(st[0], n), pc(to[0], n), pc(rm[0], n), pc(f10, n),
      pc(sp[1], sp[0]), pc(sr[1], sr[0]), pc(aw[1], aw[0]), pc(to[1], to[0])]);
  }
  return rows;
}
{
  const rows = [];
  for (const [lab, S] of [['g4 계열 전멸한 판', G.filter(g => g.fam === 'g4' && g.elim)], ['g4 계열 전멸 안 한 판', G.filter(g => g.fam === 'g4' && !g.elim)], ['흉내 계열 전멸한 판', G.filter(g => g.fam === 'proxy' && g.elim)], ['흉내 계열 전멸 안 한 판', G.filter(g => g.fam === 'proxy' && !g.elim)], ['상대(극상위권·DEV) 전부', G]])
    rows.push(...swarmRows(S, lab, g => lab.startsWith('상대') ? g.them : g.us));
  P(table(['집단', '길이', '턴', '떼 턴 비율', '떼 턴', '분열', '질주', '한 걸음 멀어짐', '한 걸음 그대로', '한 걸음 다가감', '박음', '10라운드 뒤 몸 생존', '생존: 분열', '생존: 질주', '생존: 멀어짐', '생존: 다가감'], rows, ['l', 'l']), '');
}

// ---- H. a natural experiment in our own family: swarm8 = merge2 + early swarm splits (cand-swarm8-online) vs merge2 (three sets)
P('## H. 우리 봇끼리의 자연 실험: swarm8(merge2 + 떼 초반) 대 merge2 세 세트', '');
{
  const rows = [];
  const grp = [['merge2 ×3', G.filter(g => g.bot === 'merge2')], ['swarm8', G.filter(g => g.bot === 'swarm8')], ['stack1–3', G.filter(g => ['stack1', 'stack2', 'stack3'].includes(g.bot))], ['g4r4 ×3', G.filter(g => g.bot === 'g4r4')]];
  for (const [lab, S] of grp) for (const kind of ['elim', 'r500']) {
    const X = S.filter(g => L.kindOf(g.map) === kind), E = X.filter(g => g.elim), w = L.wilson(E.length, X.length);
    const cl = c => E.filter(g => g.cls === c).length;
    rows.push([lab, kind === 'elim' ? '전멸형' : '500형', X.length, E.length, `${pc(E.length, X.length)} [${Math.round(100 * w[0])}, ${Math.round(100 * w[1])}]`, E.length ? f1(med(E.map(g => g.U.elim))) : '–',
      f1(mean(X.map(g => L.at(g, g.us, 30, 'u')))), f1(mean(X.map(g => L.at(g, g.us, 50, 'u')))), f1(mean(X.map(g => L.at(g, g.us, 100, 'u')))), `${cl('E1')}/${cl('E2')}/${cl('E3m')}/${cl('E3l')}`]);
  }
  P(table(['봇', '지도 종류', '판', '전멸', '전멸률 [95%]', '전멸 라운드 중앙', 'r30 수', 'r50 수', 'r100 수', 'E1/E2/E3m/E3l'], rows, ['l', 'l']), '');
  P('- 상대와 지도 구성은 세트마다 같다(상위 6팀 + DEV × 지도 10). 판본(a/b) 구성은 세트마다 다르다.', '');
}

// ---- selection for stage 3
// Rule (fixed before reading): pool = g4-family eliminated games. Per class: the extreme (the earliest elimination; ties -> the
// latest wave, then the smaller game id) and two representatives (elimination round nearest the class median; first an
// opponent not yet chosen, then a map not yet chosen; ties -> the latest wave, then the smaller game id).
const waveIdx = Object.fromEntries(L.SETS.map((s, i) => [s[0], i]));
const sel = [];
for (const c of CLS) {
  const S = elimG.filter(g => g.fam === 'g4' && g.cls === c).sort((a, b) => a.U.elim - b.U.elim || waveIdx[b.set] - waveIdx[a.set] || a.gameId - b.gameId);
  if (!S.length) continue;
  const chosen = [S[0]];
  const m = med(S.map(g => g.U.elim));
  const byMed = S.slice(1).sort((a, b) => Math.abs(a.U.elim - m) - Math.abs(b.U.elim - m) || waveIdx[b.set] - waveIdx[a.set] || a.gameId - b.gameId);
  for (let k = 0; k < 2; k++) {
    const pick = byMed.find(g => !chosen.includes(g) && !chosen.some(x => x.oppName === g.oppName)) || byMed.find(g => !chosen.includes(g) && !chosen.some(x => x.map === g.map)) || byMed.find(g => !chosen.includes(g));
    if (pick) chosen.push(pick);
  }
  chosen.forEach((g, i) => sel.push({ cls: c, role: i === 0 ? 'extreme' : 'median', set: g.set, gameId: g.gameId, map: g.ml2, opp: g.oppName, elim: g.U.elim, peakU: g.peakU, lastMode: g.lastMode }));
}
P('## 선별 기보 (3단계)', '', '규칙: g4 계열 전멸 판에서 부류마다 극단 1판(가장 이른 전멸)과 대표 2판(전멸 라운드가 부류 중앙값에 가장 가까운 판; 먼저 아직 안 고른 상대, 다음 아직 안 고른 지도; 같으면 최근 웨이브, 작은 게임 id).', '');
P(table(['부류', '역할', '세트', '게임', '지도', '상대', '전멸 라운드', '최대 수', '마지막 죽음'], sel.map(s => [s.cls, s.role, s.set, s.gameId, s.map, s.opp, s.elim, s.peakU, L.MODE_KO[s.lastMode] || '–']), ['l', 'l', 'l']), '');

// per-game list of eliminations (for the appendix)
const list = elimG.map(g => ({ set: g.set, gameId: g.gameId, bot: g.bot, map: g.ml2, opp: g.oppName, elim: g.U.elim, cls: g.cls, peakU: g.peakU, peakT: g.peakT, u30: L.at(g, g.us, 30, 'u'), e30: L.at(g, g.them, 30, 'u'),
  lastMode: g.lastMode, kingEarlier: g.kingEarlier }));
fs.writeFileSync(path.resolve(L.ROOT, opt('out', 'exp/eliminations/numbers-ours.md')), out.join('\n') + '\n');
fs.writeFileSync(path.resolve(L.ROOT, opt('sel', 'exp/eliminations/selection-ours.json')), JSON.stringify({ rule: 'see numbers-ours.md', sel, list }, null, 1));
console.log('wrote numbers-ours.md, selection-ours.json;', elimG.length, 'eliminations of', G.length);
