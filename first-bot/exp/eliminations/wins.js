#!/usr/bin/env node
// Q3: what happened in our wins against the elite? Mechanisms that fired (our labels), what the opponent did, map specificity.
// usage: node --max-old-space-size=8192 exp/eliminations/wins.js [--out exp/eliminations/numbers-wins.md] [--sel exp/eliminations/selection-wins.json]
'use strict';
const fs = require('fs'), path = require('path');
const L = require('./lib.js');
const { table, f1, f2, pc, mean, med, sum } = L;
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const G = L.loadOnline();
const out = []; const P = (...a) => out.push(a.join('\n'));
const EL = G.filter(g => g.elite), WIN = EL.filter(g => g.win);

P('# 우리가 극상위권을 이긴 판 (exp/eliminations/wins.js)', '');
P(`- 모집단: 온라인 ${L.SETS.length}세트 ${G.length}판. 극상위권 6팀 상대 ${EL.length}판에서 ${WIN.length}승, DEV 상대 ${G.filter(g => g.dev).length}판에서 ${G.filter(g => g.dev && g.win).length}승.`, '');

// ---- A. counts
P('## A. 승리 수', '');
{
  const MLS = [...new Set(G.map(g => g.ml2))].sort();
  const rows = [];
  for (const ml of MLS) {
    const S = EL.filter(g => g.ml2 === ml);
    const fam = f => { const x = S.filter(g => g.fam === f); return `${x.filter(g => g.win).length}/${x.length}`; };
    rows.push([ml, S.length, S.filter(g => g.win).length, pc(S.filter(g => g.win).length, S.length), fam('g4'), fam('proxy'), G.filter(g => g.dev && g.ml2 === ml && g.win).length + '/' + G.filter(g => g.dev && g.ml2 === ml).length]);
  }
  P('### 지도·판본별(극상위권 상대)', '', table(['지도·판본', '판', '승', '승률', 'g4 계열', '흉내 계열', 'DEV 상대 승'], rows, ['l']), '');
  const rows2 = [];
  for (const [set, bot, fam] of L.SETS) { const S = EL.filter(g => g.set === set), W = S.filter(g => g.win); rows2.push([set, bot, S.length, W.length, W.filter(g => g.map === 'Autarky').length, W.filter(g => g.map !== 'Autarky').map(g => g.ml2.replace('Prisoners Dilemma', 'PD')).join(', ') || '–']); }
  P('### 세트별(극상위권 상대)', '', table(['세트', '봇', '판', '승', 'Autarky 승', '다른 지도 승'], rows2, ['l', 'l']), '');
  const opps = Object.values(L.ELITE), rows3 = [];
  for (const o of opps) { const S = EL.filter(g => g.oppName === o); rows3.push([o, S.length, S.filter(g => g.win).length, S.filter(g => g.win && g.map === 'Autarky').length + '/' + S.filter(g => g.map === 'Autarky').length, S.filter(g => g.win && g.map !== 'Autarky').length]); }
  P('### 상대별', '', table(['상대', '판', '승', 'Autarky 승/판', '다른 지도 승'], rows3, ['l']), '');
}

// ---- B. list
P('## B. 극상위권을 이긴 판 전부', '');
const TOKS = ['escsplit', 'pocket', 'noexit', 'esc', 'multi', 'TRADE', 'feed', 'conv', 'frag', 'split', 'grab', 'g', 'K', 'PORTAL?', 'tg', 'tgx', 'escsplit2', 'doom'];
const labRate = (g, a = 0, b = 500) => { const c = {}; let n = 0; for (let bi = Math.floor(a / 10); bi <= Math.min(50, Math.floor(b / 10)); bi++) { const B = g.lab[bi] || {}; n += (B.move || 0) + ['feed', 'conv', 'escsplit', 'escsplit2', 'noexit', 'lasttrade', 'split', 'frag', 'pocket', 'degraded', 'csplit'].reduce((s, k) => s + (B[k] || 0), 0); for (const t of TOKS) c[t] = (c[t] || 0) + (B[t] || 0); } return { c, n }; };
function gsum(g) {
  const U = g.U, E = g.E;
  let eMaxK = 0, eMaxKr = 0; for (let r = 0; r < g.rounds; r++) { const k = L.at(g, g.them, r, 'k'); if (k > eMaxK) { eMaxK = k; eMaxKr = r; } }
  const eKingDeaths = E.kd.filter(d => d[6] === 1);
  const eKingLate = eKingDeaths.filter(d => d[0] >= 350);
  const fl = g.ml[g.us].fl, efl = g.ml[g.them].fl, S = a => sum(a || []);
  return { set: g.set, gameId: g.gameId, bot: g.bot, fam: g.fam, map: g.ml2, opp: g.oppName, win: g.win, end: g.endReason, rounds: g.rounds,
    ourK: U.end.k, ourU: U.end.u, ourT: U.end.t, theirK: E.end.k, theirU: E.end.u, theirT: E.end.t, eMaxK, eMaxKr, eKingDeaths: eKingDeaths.length, eKingLate: eKingLate.length,
    eKingLateLen: sum(eKingLate.map(d => d[1])), eKingLateModes: eKingLate.map(d => L.modeOf(d)),
    lin: g.ml[g.us].lin, elin: g.ml[g.them].lin,
    natOwn: S(fl.nat_own), natEnemy: S(fl.nat_enemy), fOwn: S(fl.nat_fOwn), dropOwn: S(fl.eat_oSac) + S(fl.eat_oTrap) + S(fl.eat_oRammed) + S(fl.eat_oRam) + S(fl.eat_oOther),
    dropEnemy: S(fl.eat_eSac) + S(fl.eat_eTrap) + S(fl.eat_eRammed) + S(fl.eat_eRam) + S(fl.eat_eOther),
    eNatOwn: S(efl.nat_own), eNatEnemy: S(efl.nat_enemy), eDropEnemy: S(efl.eat_eSac) + S(efl.eat_eTrap) + S(efl.eat_eRammed) + S(efl.eat_eRam) + S(efl.eat_eOther),
    u100: L.at(g, g.us, 100, 'u'), eu100: L.at(g, g.them, 100, 'u'), k300: L.at(g, g.us, 300, 'k'), ek300: L.at(g, g.them, 300, 'k'), k400: L.at(g, g.us, 400, 'k'), ek400: L.at(g, g.them, 400, 'k'),
    t300: L.at(g, g.us, 300, 't'), et300: L.at(g, g.them, 300, 't'), eu300: L.at(g, g.them, 300, 'u'), eu400: L.at(g, g.them, 400, 'u'),
    lab: g.fam === 'g4' ? labRate(g) : null };
}
const WS = WIN.map(gsum);
P(table(['세트', '게임', '지도', '상대', '끝', '우리 최장', '상대 최장', '상대 최대 최장(라운드)', '상대 왕 사망(r350+)', '우리 수', '상대 수', '우리 총길이', '상대 총길이', '우리 왕 세대', '탈출 분열/100턴'],
  WS.map(w => [w.set, w.gameId, w.map, w.opp, w.end === 'roundLimit' ? '500' : w.end, w.ourK, w.theirK, `${w.eMaxK} (r${w.eMaxKr})`, w.eKingLate ? `${w.eKingLate}회 ${w.eKingLateLen}칸` : '–', w.ourU, w.theirU, w.ourT, w.theirT,
    w.lin ? w.lin.gen : '–', w.lab && w.lab.n ? f1(100 * (w.lab.c.escsplit || 0) / w.lab.n) : '–']), ['l', 'l', 'l', 'l']), '');

// ---- C. wins vs losses on the same maps (g4 family, elite)
P('## C. 같은 지도에서 이긴 판 대 진 판 (극상위권 상대)', '');
{
  const maps = [...new Set(WIN.map(g => g.ml2))];
  const rows = [], rows2 = [], rows3 = [];
  for (const ml of maps) for (const fam of ['g4', 'proxy']) {
    const S = EL.filter(g => g.ml2 === ml && g.fam === fam); const W = S.filter(g => g.win).map(gsum), Lo = S.filter(g => !g.win).map(gsum);
    if (!W.length) continue;
    for (const [lab, X] of [['승', W], ['패', Lo]]) {
      rows.push([ml, fam, lab, X.length, f1(mean(X.map(x => x.ourK))), f1(mean(X.map(x => x.theirK))), f1(mean(X.map(x => x.eMaxK))), f1(mean(X.map(x => x.k300))) + ' / ' + f1(mean(X.map(x => x.ek300))), f1(mean(X.map(x => x.k400))) + ' / ' + f1(mean(X.map(x => x.ek400))),
        f1(mean(X.map(x => x.u100))) + ' / ' + f1(mean(X.map(x => x.eu100))), f1(mean(X.map(x => x.eu300))), pc(X.filter(x => x.eKingLate > 0).length, X.length), f1(mean(X.map(x => x.eKingLateLen))), pc(X.filter(x => x.ourU === 0).length, X.length)]);
      rows2.push([ml, fam, lab, X.length, f1(mean(X.map(x => x.natOwn))), f1(mean(X.map(x => x.fOwn))), f1(mean(X.map(x => x.natEnemy))), f1(mean(X.map(x => x.dropOwn))), f1(mean(X.map(x => x.dropEnemy))), f1(mean(X.map(x => x.eNatOwn))), f1(mean(X.map(x => x.eNatEnemy))), f1(mean(X.map(x => x.eDropEnemy))),
        f1(mean(X.filter(x => x.lin).map(x => x.lin.gen))), f1(mean(X.filter(x => x.lin).map(x => x.lin.born)))]);
      if (fam === 'g4') {
        const c = {}; let n = 0; for (const x of X) { n += x.lab.n; for (const t of TOKS) c[t] = (c[t] || 0) + (x.lab.c[t] || 0); }
        rows3.push([ml, lab, X.length, n, ...TOKS.map(t => f2(100 * (c[t] || 0) / Math.max(1, n)))]);
      }
    }
  }
  P('### 결과와 궤적(평균)', '', table(['지도', '계열', '결과', '판', '우리 끝 최장', '상대 끝 최장', '상대 최대 최장', 'r300 최장 우리/상대', 'r400 최장 우리/상대', 'r100 수 우리/상대', 'r300 상대 수', '상대 왕이 r350+에 죽은 판', '그 왕 길이 합(평균)', '우리 전멸'], rows, ['l', 'l', 'l']), '');
  P('### 먹이 출처(판당 진주)', '', table(['지도', '계열', '결과', '판', '우리: 제 영토 자연', '그중 샘', '적 영토 자연', '제 사망 진주', '적 사망 진주', '상대: 제 영토 자연', '상대: 우리 영토 자연', '상대: 우리 사망 진주', '우리 끝 왕의 세대', '우리 끝 왕이 태어난 라운드'], rows2, ['l', 'l', 'l']), '');
  P('### 우리 표식 비율(100턴당, g4 계열)', '', table(['지도', '결과', '판', '턴', ...TOKS], rows3, ['l', 'l']), '');
}

// ---- D. Autarky by opponent and bot
P('## D. Autarky', '');
{
  const A = EL.filter(g => g.map === 'Autarky');
  const rows = [];
  for (const [set, bot, fam] of L.SETS) { const S = A.filter(g => g.set === set); rows.push([set, bot, S.length, S.filter(g => g.win).length, S.filter(g => g.win).map(g => g.oppName).join(', ') || '–', f1(mean(S.map(g => g.U.end.k))), f1(mean(S.map(g => g.E.end.k)))]); }
  P(table(['세트', '봇', '판', '승', '이긴 상대', '우리 끝 최장(평균)', '상대 끝 최장(평균)'], rows, ['l', 'l']), '');
  // top-vs-top reference on Autarky: winners' final longest, share ending by elimination
}

// ---- E. W3 (stack3) wins: label counts of the stacked mechanisms, whole game
P('## E. W3(stack3)가 극상위권을 이긴 7판: 기능 표식 수(판 전체)', '');
{
  const K = ['escsplit', 'noexit', 'pocket', 'esc', 'TRADE', 'feed', 'conv', 'frag', 'split', 'grab', 'ks2', 'g', 'PORTAL?', 'multi', 'doom'];
  const rows = [];
  for (const g of WIN.filter(g => g.set === 'cand-stack3-online')) {
    const c = {}; let n = 0;
    for (const B of g.lab) { n += (B.move || 0) + ['feed', 'conv', 'escsplit', 'escsplit2', 'noexit', 'lasttrade', 'split', 'frag', 'pocket', 'degraded', 'csplit'].reduce((s2, k) => s2 + (B[k] || 0), 0); for (const k of K) c[k] = (c[k] || 0) + (B[k] || 0); }
    rows.push([g.gameId, g.ml2, g.oppName, n, ...K.map(k => c[k] || 0)]);
  }
  // reference: stack3 losses against the elite on the same maps (mean per game)
  for (const ml of [...new Set(WIN.filter(g => g.set === 'cand-stack3-online').map(g => g.ml2))]) {
    const S = EL.filter(g => g.set === 'cand-stack3-online' && !g.win && g.ml2 === ml); if (!S.length) continue;
    const c = {}; let n = 0;
    for (const g of S) for (const B of g.lab) { n += (B.move || 0) + ['feed', 'conv', 'escsplit', 'escsplit2', 'noexit', 'lasttrade', 'split', 'frag', 'pocket', 'degraded', 'csplit'].reduce((s2, k) => s2 + (B[k] || 0), 0); for (const k of K) c[k] = (c[k] || 0) + (B[k] || 0); }
    rows.push(['(패 ' + S.length + '판 평균)', ml, '–', f1(n / S.length), ...K.map(k => f1((c[k] || 0) / S.length))]);
  }
  P(table(['게임', '지도', '상대', '턴', ...K], rows, ['l', 'l', 'l']), '');
}

// ---- selection: every stack3 (W3) win against the elite; for each other map with a win, the win with the largest final-longest
// margin (ties: latest wave); for each selected Autarky win, the same opponent's Autarky loss by a g4 bot of the latest wave
const waveIdx = Object.fromEntries(L.SETS.map((s, i) => [s[0], i]));
const sel = [];
for (const g of WIN.filter(g => g.set === 'cand-stack3-online')) sel.push({ why: 'W3 승', set: g.set, gameId: g.gameId, map: g.ml2, opp: g.oppName });
for (const ml of [...new Set(WIN.map(g => g.ml2))].filter(m => m !== 'Autarky')) {
  const W = WIN.filter(g => g.ml2 === ml && !sel.some(s => s.gameId === g.gameId)).sort((a, b) => (b.U.end.k - b.E.end.k) - (a.U.end.k - a.E.end.k) || waveIdx[b.set] - waveIdx[a.set]);
  if (W.length) sel.push({ why: '지도별 최대 격차 승', set: W[0].set, gameId: W[0].gameId, map: W[0].ml2, opp: W[0].oppName });
}
for (const s of sel.filter(s => s.map === 'Autarky')) {
  const Lo = EL.filter(g => g.map === 'Autarky' && !g.win && g.fam === 'g4' && g.oppName === s.opp).sort((a, b) => waveIdx[b.set] - waveIdx[a.set] || a.gameId - b.gameId);
  if (Lo.length) sel.push({ why: 'Autarky 같은 상대 패배(대조)', set: Lo[0].set, gameId: Lo[0].gameId, map: 'Autarky', opp: s.opp });
}
P('## 선별 기보', '', '규칙: W3(stack3)가 극상위권을 이긴 판 전부; Autarky 밖의 지도마다 끝 최장 격차가 가장 큰 승리 1판(같으면 최근 웨이브); 고른 Autarky 승리마다 같은 상대에게 진 g4 계열 Autarky 판 중 가장 최근 웨이브 1판(대조).', '');
P(table(['이유', '세트', '게임', '지도', '상대'], sel.map(s => [s.why, s.set, s.gameId, s.map, s.opp]), ['l', 'l', 'l', 'l', 'l']), '');
fs.writeFileSync(path.resolve(L.ROOT, opt('out', 'exp/eliminations/numbers-wins.md')), out.join('\n') + '\n');
fs.writeFileSync(path.resolve(L.ROOT, opt('sel', 'exp/eliminations/selection-wins.json')), JSON.stringify({ sel, wins: WS.map(w => { const { lab, ...rest } = w; return rest; }) }, null, 1));
console.log('wrote numbers-wins.md;', WIN.length, 'elite wins');
