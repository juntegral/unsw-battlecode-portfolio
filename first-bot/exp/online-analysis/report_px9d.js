#!/usr/bin/env node
'use strict';
// report_px9d.js — tables for research/experiments/online-analysis-px9d.md from px9d_study.js output.
// usage (repository root):
//   node exp/online-analysis/report_px9d.js --study <px9d_study.jsonl> [--local <fortstat --out jsonl of base-px9d+base-px9d-s3>]
// Sections (letters are cited in the document):
//   A  paired B - A by map (key = opponent team x map, Prisoners Dilemma by version), bootstrap as tools/online_compare.js
//   B  Autarky: per game (px9d), by set, king intake by source, swarm deaths and sacrifices, local vs online
//   C  round-500 maps: end-state concentration, king timeline, king intake per window, king deaths, sacrifices, their longest
//   D  elimination maps: timing, exchange, regeneration; Prisoners Dilemma by version
//   E  fortress turns on other maps (misfires)
// Definitions are in px9d_study.js. "Outside king" = our longest dragon that is not the lineage while the lineage holds
// the corridor (Autarky, Prisoners Dilemma); elsewhere it is the longest dragon. "Swarm" = dragons that were never the
// lineage nor split off it. Means are per game unless marked "med" (median).
const fs = require('fs'), path = require('path');
const L = require('./lib.js');
const { boot, mean, median, quant, fx, sg, ci, table, readJsonl } = L;
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const recs = readJsonl(path.resolve(opt('study', '.cache/online-analysis/px9d_study.jsonl')));
const localFile = opt('local', null);
const grp = s => s.startsWith('baseline') ? 'base' : s.replace('-online', '');
const NAME = { base: '기준 g4-r4 (210)', 'cand-merge2': 'merge2 (bot/)', 'base-px9d': 'px9d', 'base-px8': 'px8', 'px-king-v2': 'px-king', 'cand-swarm8': 'swarm8' };
const SETS = ['base', 'cand-merge2', 'base-px9d', 'base-px8', 'px-king-v2'];
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'], M4 = ['Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const ELIM4 = ['Default', 'Devil', 'Trophy', 'Queen Of Spades'];
const ALLMAPS = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma', 'Default', 'Devil', 'Trophy', 'Queen Of Spades', 'PD6', 'PD10'];
const of = (s, maps) => recs.filter(r => grp(r.set) === s && (!maps || maps.includes(r.mapKey)));
const per = (g, f) => g.length ? g.reduce((a, r) => a + f(r), 0) / g.length : NaN;
const snapM = (g, side, ri, i, fn = mean) => fn(g.map(r => r.x.snaps[side][ri][i]));
const f0 = x => fx(x, 0), f1 = x => fx(x, 1), f2 = x => fx(x, 2);
const out = [];
const H = s => out.push('\n## ' + s + '\n');
const P = s => out.push(s);
const key = r => r.opp + '|' + r.mapKey;

// ---------------------------------------------------------------------------------------------------------------
H('A0. 지도별 승 / 생존 / 판 / G 평균');
{
  const sets = [...SETS, 'cand-swarm8'];
  P(table(['지도', ...sets.map(s => NAME[s])], [...ALLMAPS, 'ELIM4', '합'].map(m => [m, ...sets.map(s => { const G = of(s, m === '합' ? null : m === 'ELIM4' ? ELIM4 : [m]); return G.length ? `${G.filter(r => r.win).length} / ${G.filter(r => r.survived).length} / ${G.length} / ${f1(per(G, r => r.G))}` : '–'; })])));
}
H('A. 짝 비교 (팀×지도, PD는 판본별), B − A');
for (const [a, b] of [['base', 'base-px9d'], ['cand-merge2', 'base-px9d'], ['base-px8', 'base-px9d'], ['base', 'cand-merge2']]) {
  P(`\n### A: ${NAME[a]} → ${NAME[b]}`);
  const rows = [];
  for (const m of [...ALLMAPS, 'R500', 'ELIM', 'ALL']) {
    const maps = m === 'R500' ? R500 : m === 'ELIM' ? [...ELIM4, 'PD6', 'PD10'] : m === 'ALL' ? ALLMAPS : [m];
    const A = of(a, maps), B = of(b, maps);
    const pG = L.paired(A, B, key, r => r.G), pW = L.paired(A, B, key, r => r.win), pS = L.paired(A, B, key, r => r.survived);
    const pT = L.paired(A, B, key, r => r.theirLongest), pTot = L.paired(A, B, key, r => r.total);
    rows.push([m, pG.keys, `${f1(pG.meanA)} → ${f1(pG.meanB)}`, pG.keys > 1 ? ci(pG) : sg(pG.mean), sg(pW.mean), sg(pS.mean), sg(pT.mean), sg(pTot.mean)]);
  }
  P(table(['지도', '짝', 'G A → B', 'G 차 [95%]', '승 차', '생존 차', '상대 최장 차', '총길이 차'], rows));
  // contribution of each map to the pooled ELIM / R500 / ALL difference
  const contrib = [];
  for (const grpName of ['ELIM', 'R500']) {
    const maps = grpName === 'R500' ? R500 : [...ELIM4, 'PD6', 'PD10'];
    const A = of(a, maps), B = of(b, maps), all = L.paired(A, B, key, r => r.G);
    const parts = maps.map(m => { const p = L.paired(of(a, [m]), of(b, [m]), key, r => r.G); return `${m} ${sg(p.keys * p.mean / all.keys)}`; });
    contrib.push(`- ${grpName} G 차 ${sg(all.mean)}의 지도별 몫: ${parts.join(', ')}`);
  }
  P(contrib.join('\n'));
}

// ---------------------------------------------------------------------------------------------------------------
H('B. Autarky');
{
  const g = of('base-px9d', ['Autarky']);
  P('\n### B1. px9d 7판');
  P(table(['경기', '상대', '승', 'G', '상대 최장', '요새 턴', '계통 길이 끝', '통로 라운드', '우리 샘물 생성 / 먹음', '상대가 먹음', '수 최대 r330–420', '탈출(peel)', '바깥 왕 r300 / r400 / 끝', '상대 최장 r300 / r400'],
    g.map(r => [r.id, r.oppName, r.win, r.G, r.theirLongest, r.x.ind.fort, r.x.lin.us.final, r.x.lin.us.inRounds, `${r.x.fnt.us.spawns} / ${r.x.eat.us.natF}`, r.x.eat.them.natX,
      r.x.units330.max, r.x.ind.peel, `${r.x.snaps.us[30][5]} / ${r.x.snaps.us[40][5]} / ${r.x.snaps.us[50][5]}`, `${r.x.snaps.them[30][2]} / ${r.x.snaps.them[40][2]}`])));
  P(`- 요새 턴 합 ${g.reduce((a, r) => a + r.x.ind.fort, 0)}, 그중 계통이 아닌 드래곤 ${g.reduce((a, r) => a + r.x.ind.fortNonLin, 0)}. 요새 분열 표지 ${g.reduce((a, r) => a + r.x.ind.fortSplit, 0)}, 계통 분열 판당 ${f1(per(g, r => r.x.lin.us.splits))}.`);

  P('\n### B2. 묶음별 (판당 평균, 괄호는 중앙값)');
  const rows = [];
  for (const s of [...SETS, 'cand-swarm8']) {
    const G = of(s, ['Autarky']); if (!G.length) continue;
    const alive = G.filter(r => !r.x.lin.us.death && r.x.lin.us.finalIn).length;
    rows.push([NAME[s], G.length, G.filter(r => r.win).length, `${G.filter(r => r.survived).length}`, f1(per(G, r => r.G)), f1(per(G, r => r.theirLongest)), `${alive}/${G.length}`,
      `${f1(per(G, r => r.x.fnt.us.spawns))} / ${f1(per(G, r => r.x.eat.us.natF))}`, f1(per(G, r => r.x.eat.them.natX)),
      `${f1(per(G, r => r.x.eat.us.natE))} / ${f1(per(G, r => r.x.eat.them.natE))} / ${f1(per(G, r => r.x.eat.them.natF))}`, f1(per(G, r => r.x.lin.them.inRounds)),
      `${f1(snapM(G, 'us', 30, 0))} / ${f1(snapM(G, 'them', 30, 0))}`,
      [20, 30, 40, 50].map(ri => f1(snapM(G, 'us', ri, 5))).join(' / '), `${f1(snapM(G, 'us', 30, 7))} / ${f1(snapM(G, 'us', 50, 7))}`,
      `${f1(snapM(G, 'them', 30, 1))}`, [30, 40, 50].map(ri => f1(snapM(G, 'them', ri, 2))).join(' / ')]);
  }
  P(table(['묶음', '판', '승', '생존', 'G', '상대 최장', '계통 끝까지 통로', '우리 샘물 생성 / 먹음', '상대가 우리 샘물 먹음', '샘물 밖 자연 진주 우리 / 상대, 상대가 자기 샘물에서', '상대 계통이 통로에 있던 라운드', '수 r300 우리 / 상대', '바깥 왕 r200 / r300 / r400 / 끝', '떼 총길이 r300 / 끝', '상대 총길이 r300', '상대 최장 r300 / r400 / 끝'], rows));

  P('\n### B3. 왕이 먹은 진주 (판당). 바깥 왕 = 요새가 아닌 우리 최장, 상대 왕 = 상대 최장');
  const rows3 = [];
  for (const s of ['base', 'cand-merge2', 'base-px9d']) {
    const G = of(s, ['Autarky']);
    const q = (k, side) => ['natE', 'corOwn', 'corOpp', 'natF'].map(x => f1(per(G, r => r.x[k][side][x]))).join(' / ');
    rows3.push([NAME[s], q('eatOK', 'us'), q('eatOK300', 'us'), q('eatKing300', 'them'), `${f1(per(G, r => r.x.eat.us.natE))}`]);
  }
  P(table(['묶음', '바깥 왕 전체: 자연 / 우리 시체 / 상대 시체 / 샘물', '바깥 왕 r300+', '상대 왕 r300+', '우리 팀 자연(샘물 밖) 전체'], rows3));

  P('\n### B4. 떼(계통과 무관한 드래곤)의 사망과 늦은 희생 (판당)');
  const rows4 = [];
  for (const s of ['base', 'cand-merge2', 'base-px9d']) {
    const G = of(s, ['Autarky']);
    const D = G.flatMap(r => r.x.deaths.filter(d => d.side === 'us' && !d.kin));
    const by = {}; for (const d of D) by[d.c] = (by[d.c] || 0) + 1;
    const top = Object.entries(by).sort((x, y) => y[1] - x[1]).slice(0, 5).map(([c, n]) => `${c} ${f1(n / G.length)}`).join(', ');
    const sl = G.map(r => r.px8.sacLate);
    rows4.push([NAME[s], f1(D.length / G.length), f1(D.reduce((a, d) => a + d.len, 0) / G.length), f1(D.filter(d => d.byEnemy).length / G.length), top,
      `${f1(D.reduce((a, d) => a + d.dropped, 0) / G.length)} → 우리 ${f1(D.reduce((a, d) => a + d.eaten[0], 0) / G.length)} (바깥 왕 ${f1(D.reduce((a, d) => a + d.eatenOK[0], 0) / G.length)}) / 상대 ${f1(D.reduce((a, d) => a + d.eaten[1], 0) / G.length)}`,
      `${f1(mean(sl.map(x => x.n)))} / ${f1(mean(sl.map(x => x.drop)))} / ${f1(mean(sl.map(x => x.king20)))} / ${f1(mean(sl.map(x => x.own20)))}`,
      f1(per(G, r => r.px8.sac[4].n))]);
  }
  P(table(['묶음', '사망', '잃은 길이', '적 때문', '원인 상위', '떨군 진주 → 먹은 쪽', '희생 r300+: 수 / 떨군 진주 / 최장이 20r 안에 / 우리 다른 조각', '그중 최장에서 9칸 이상'], rows4));
  P('- 원인: vol = 빈 이웃이 있는데 죽음(스스로 해초·자기 몸·무행동, 희생 포함), volAlly = 아군 몸에 박음, allyHead = 아군 머리, trapped = 빈 이웃 없음, rammed = 적이 우리 머리를 박음, ram = 우리가 적 머리를 박음.');
  for (const s of ['base', 'base-px9d']) {
    const G = of(s, ['Autarky']), Wd = new Array(10).fill(0);
    for (const r of G) for (const d of r.x.deaths) if (d.side === 'us' && !d.kin) Wd[Math.min(9, Math.floor(d.r / 50))]++;
    P(`- ${NAME[s]} 떼 사망, 50라운드 창별(판당): ${Wd.map(x => f1(x / G.length)).join(' / ')}`);
  }

  // old bot: winners vs losers
  const base = of('base', ['Autarky']);
  const W = base.filter(r => r.win), Lz = base.filter(r => !r.win);
  P(`\n- 기준 Autarky 승 ${W.length}판: 바깥 왕 끝 평균 ${f1(snapM(W, 'us', 50, 5))}, 상대 최장 ${f1(per(W, r => r.theirLongest))}. 패 ${Lz.length}판: ${f1(snapM(Lz, 'us', 50, 5))}, ${f1(per(Lz, r => r.theirLongest))}.`);
  P(`- 기준 Autarky 바깥 왕 r100 / r200 / r300 / r400 / 끝(중앙값): ${[10, 20, 30, 40, 50].map(ri => f0(snapM(base, 'us', ri, 5, median))).join(' / ')}. px9d: ${[10, 20, 30, 40, 50].map(ri => f0(snapM(g, 'us', ri, 5, median))).join(' / ')}. 상대(px9d 판): ${[10, 20, 30, 40, 50].map(ri => f0(snapM(g, 'them', ri, 2, median))).join(' / ')}.`);
  P(`- 우리 수 r100 / r200 / r300 / r400 / 끝(평균): 기준 ${[10, 20, 30, 40, 50].map(ri => f1(snapM(base, 'us', ri, 0))).join(' / ')}, px9d ${[10, 20, 30, 40, 50].map(ri => f1(snapM(g, 'us', ri, 0))).join(' / ')}.`);

  if (localFile && fs.existsSync(localFile)) {
    P('\n### B5. 로컬(시드 1–3) 대 온라인: Autarky의 px9d');
    const loc = readJsonl(localFile).filter(r => r.map === 'autarky');
    const rows5 = [];
    for (const o of ['proxy_swarm', 'proxy_elim', 'proxy_king', 'r1']) {
      const x = loc.filter(r => r.opp === o);
      rows5.push([`로컬 ${o}`, x.length, x.filter(r => r.won).length, f1(mean(x.map(r => r.G))), f1(mean(x.map(r => r.olng500))), f1(mean(x.map(r => r.n300))), f1(mean(x.map(r => r.on300))), x.filter(r => r.exitRound !== null).length]);
    }
    rows5.push(['온라인 7팀', g.length, g.filter(r => r.win).length, f1(per(g, r => r.G)), f1(per(g, r => r.theirLongest)), f1(snapM(g, 'us', 30, 0)), f1(snapM(g, 'them', 30, 0)), g.filter(r => r.x.ind.peel > 0).length]);
    P(table(['상대', '판', '승', 'G', '상대 최장 끝', '우리 수 r300', '상대 수 r300', '계통 탈출 판'], rows5));
    P('- 로컬 행은 `fortstat.js`의 값이다. 계통 탈출은 시작 줄에서 2칸 벗어난 첫 라운드가 있는 판이다.');
  }
}

// ---------------------------------------------------------------------------------------------------------------
H('C. 500라운드형 지도');
{
  P('\n### C1. r500까지 산 판의 끝 상태');
  const rows = [];
  for (const [label, maps] of [['5개 지도', R500], ['Autarky', ['Autarky']], ['나머지 4개', M4]]) for (const s of SETS) {
    const G = of(s, maps), alive = G.filter(r => r.x.rounds === 500 && r.survived);
    rows.push([label, NAME[s], G.length, alive.length, alive.filter(r => r.win).length, alive.filter(r => r.total > r.theirLongest).length,
      alive.filter(r => r.total > r.theirLongest && r.G < r.theirLongest).length, f0(median(alive.map(r => r.theirLongest - r.G))), f1(mean(alive.map(r => r.G / Math.max(1, r.total)))), f1(mean(alive.map(r => r.theirLongest / Math.max(1, r.theirTotal))))]);
  }
  P(table(['지도', '묶음', '판', 'r500 생존', '승', '우리 총길이 > 상대 최장', '그중 우리 최장 < 상대 최장', '상대 최장 − 우리 최장(중앙)', '우리 최장/총길이', '상대 최장/총길이'], rows));

  P('\n### C2. 나머지 4개 지도, r350에 살아 있고 r500까지 간 판: 왕(최장) 길이 중앙값');
  const rows2 = [];
  for (const m of M4) for (const s of ['base', 'cand-merge2', 'base-px9d', 'base-px8']) {
    const G = of(s, [m]).filter(r => r.x.rounds === 500 && r.x.snaps.us[35][0] > 0);
    if (!G.length) continue;
    rows2.push([m, NAME[s], G.length, G.filter(r => r.win).length, [30, 35, 40, 45, 50].map(ri => f0(snapM(G, 'us', ri, 2, median))).join(' / '), [30, 35, 40, 45, 50].map(ri => f0(snapM(G, 'them', ri, 2, median))).join(' / '),
      `${f0(snapM(G, 'us', 35, 0, median))} / ${f0(snapM(G, 'them', 35, 0, median))}`, `${f0(snapM(G, 'us', 35, 1, median))} / ${f0(snapM(G, 'them', 35, 1, median))}`]);
  }
  P(table(['지도', '묶음', '판', '승', '우리 최장 r300 / 350 / 400 / 450 / 끝', '상대 최장 r300 / 350 / 400 / 450 / 끝', '수 r350 우리 / 상대', '총길이 r350 우리 / 상대'], rows2));

  P('\n### C3. 나머지 4개 지도, r500까지 산 판: 왕의 먹이, 왕의 죽음, 늦은 희생 (판당)');
  const rows3 = [];
  for (const s of SETS) {
    const G = of(s, M4).filter(r => r.x.rounds === 500 && r.survived); if (!G.length) continue;
    const kw = side => [6, 7, 8, 9].map(w => f1(per(G, r => r.x.kingEatW[side][w]))).join(' / ');
    const KD = side => { const K = G.flatMap(r => r.x.deaths.filter(d => d.side === side && d.longest && d.len >= 8 && d.r >= 250)); return `${f2(K.length / G.length)} (${f1(K.reduce((a, d) => a + d.len, 0) / G.length)})`; };
    const sl = G.map(r => r.px8.sacLate);
    rows3.push([NAME[s], G.length, kw('us'), kw('them'), KD('us'), KD('them'),
      `${f1(mean(sl.map(x => x.n)))} / ${f1(mean(sl.map(x => x.drop)))} / ${f1(mean(sl.map(x => x.king20)))} / ${f1(mean(sl.map(x => x.own20)))}`,
      `${f1(per(G, r => r.x.eatKing350.us.corOwn))} / ${f1(per(G, r => r.x.eatKing350.them.corOwn))}`,
      `${f1(snapM(G, 'us', 40, 2))} / ${f1(snapM(G, 'us', 40, 9))} / ${f1(snapM(G, 'us', 40, 8))} / ${f1(snapM(G, 'us', 40, 1))}`, `${f1(snapM(G, 'them', 40, 2))} / ${f1(snapM(G, 'them', 40, 9))} / ${f1(snapM(G, 'them', 40, 8))} / ${f1(snapM(G, 'them', 40, 1))}`]);
  }
  P(table(['묶음', '판', '우리 왕 먹이 r300–349 / 350–399 / 400–449 / 450–499', '상대 왕 먹이', '우리 왕 사망 r250+ (잃은 길이)', '상대 왕 사망 r250+', '우리 희생 r300+: 수 / 떨군 진주 / 최장 20r / 다른 아군 20r', '자기 편 시체를 왕이 먹음 r350+ 우리 / 상대', 'r400 우리 최장 / 둘째 / 8칸 이상 / 총길이', 'r400 상대 최장 / 둘째 / 8칸 이상 / 총길이'], rows3));
  P('- 왕 = 그 순간 팀의 최장(길이 8 이상은 사망 집계에만 적용). 왕 먹이는 먹는 순간 최장인 드래곤이 먹은 진주다.');

  // king deaths by map for px9d
  const rowsK = [];
  for (const m of M4) {
    const G = of('base-px9d', [m]).filter(r => r.x.rounds === 500 && r.survived);
    const K = G.flatMap(r => r.x.deaths.filter(d => d.side === 'us' && d.longest && d.len >= 8 && d.r >= 250));
    const by = {}; for (const d of K) by[d.c] = (by[d.c] || 0) + 1;
    const small = K.filter(d => d.c === 'rammed' && d.byLen > 0 && d.byLen <= 6);
    rowsK.push([m, G.length, K.length, K.reduce((a, d) => a + d.len, 0), Object.entries(by).map(([c, n]) => `${c} ${n}`).join(', '), `${small.length} (${small.map(d => d.byLen).join(', ')})`, f0(snapM(G, 'us', 30, 0, median))]);
  }
  P('\n px9d 왕 사망 r250+ (지도별 합):\n');
  P(table(['지도', '판', '왕 사망', '잃은 길이', '원인', '길이 6 이하 적에게 박힘 (박은 적 길이)', '우리 수 r300(중앙)'], rowsK));
  const rowsK2 = [];
  for (const s of SETS) {
    const G = of(s, M4).filter(r => r.x.rounds === 500 && r.survived); if (!G.length) continue;
    const K = G.flatMap(r => r.x.deaths.filter(d => d.side === 'us' && d.longest && d.len >= 8 && d.r >= 250));
    rowsK2.push([NAME[s], G.length, f2(K.length / G.length), f2(K.filter(d => d.c === 'rammed' && d.byLen > 0 && d.byLen <= 6).length / G.length), f2(K.filter(d => d.c === 'trapped').length / G.length), f2(K.filter(d => d.c === 'allyHead' || d.c === 'volAlly').length / G.length)]);
  }
  P('\n');
  P(table(['묶음(나머지 4개, r500 생존 판)', '판', '왕 사망 r250+', '길이 6 이하 적에게 박힘', '갇힘', '아군과 충돌'], rowsK2));

  P('\n### C4. 상대 최장은 우리가 오래 살수록 커진다');
  const rows4 = [];
  for (const s of SETS) {
    const G = of(s, R500);
    const full = G.filter(r => r.x.rounds === 500), early = G.filter(r => r.x.rounds < 500);
    rows4.push([NAME[s], G.length, `${full.length} / ${f1(mean(full.map(r => r.theirLongest)))}`, `${early.length} / ${f1(mean(early.map(r => r.theirLongest)))}`, f1(per(G, r => r.theirLongest))]);
  }
  P(table(['묶음', '판', 'r500까지 간 판 / 상대 최장', '일찍 끝난 판 / 상대 최장', '전체 상대 최장'], rows4));
}

// ---------------------------------------------------------------------------------------------------------------
H('D. 전멸형 지도');
{
  P('\n### D1. Default·Devil·Trophy·Queen Of Spades (판당)');
  const rows = [];
  for (const m of [...ELIM4, 'ALL4']) for (const s of ['base', 'cand-merge2', 'base-px9d', 'base-px8']) {
    const G = of(s, m === 'ALL4' ? ELIM4 : [m]); if (!G.length) continue;
    const el = G.filter(r => !r.survived).map(r => r.x.rounds);
    const u = (side, ri) => f0(median(G.filter(r => r.x.rounds > ri * 10).map(r => r.x.snaps[side][ri][0])));
    const Dus = G.flatMap(r => r.x.deaths.filter(d => d.side === 'us')), Dth = G.flatMap(r => r.x.deaths.filter(d => d.side === 'them'));
    const spl = side => f1(per(G, r => r.px8.splitsW[side].reduce((a, b) => a + b, 0)));
    const nat = side => f1(per(G, r => r.x.eat[side].natE + r.x.eat[side].natF + r.x.eat[side].natX));
    rows.push([m === 'ALL4' ? '넷 합' : m, NAME[s], G.length, G.filter(r => r.win).length, el.length, `r${f0(quant(el, 0.5))} [${f0(quant(el, 0.25))}–${f0(quant(el, 0.75))}]`,
      `${u('us', 5)} / ${u('them', 5)}`, `${u('us', 10)} / ${u('them', 10)}`, `${spl('us')} / ${spl('them')}`, `${nat('us')} / ${nat('them')}`,
      `${f1(Dus.length / G.length)} / ${f1(Dus.filter(d => d.byEnemy).length / G.length)} / ${f1(Dth.filter(d => d.byEnemy).length / G.length)}`,
      f1(Dus.filter(d => d.c === 'trapped').length / G.length)]);
  }
  P(table(['지도', '묶음', '판', '승', '전멸', '전멸 라운드 중앙 [사분위]', '수 r50 우리 / 상대', '수 r100', '분열 우리 / 상대', '자연 진주 우리 / 상대', '우리 사망 / 적 때문 / 우리가 잡음', '우리 갇힘 사망'], rows));
  P('- 수는 그 라운드에 진행 중인 판의 중앙값이다. 머리끼리 박으면 둘 다 죽으므로 "적 때문"과 "우리가 잡음"은 거의 같다.');

  P('\n### D2. Prisoners Dilemma (판본별)');
  const rows2 = [];
  for (const m of ['PD6', 'PD10']) for (const s of ['base', 'cand-merge2', 'base-px9d', 'base-px8']) {
    const G = of(s, [m]); if (!G.length) continue;
    const linDead = G.filter(r => r.x.lin.us.death);
    const lateFeed = linDead.filter(r => r.x.lin.us.death.r >= 450 && r.x.lin.us.death.c === 'vol').length;
    rows2.push([m, NAME[s], G.length, G.filter(r => r.win).length, G.filter(r => r.survived).length, f1(per(G, r => r.G)), f1(per(G, r => r.theirLongest)),
      `${f1(per(G, r => r.x.fnt.us.spawns))} / ${f1(per(G, r => r.x.eat.us.natF))} / ${f1(per(G, r => r.x.eat.them.natX))}`,
      `${G.filter(r => !r.x.lin.us.death && r.x.lin.us.inRounds >= 450).length} / ${lateFeed}`,
      [30, 40, 50].map(ri => f1(snapM(G, 'us', ri, 5))).join(' / '), [30, 40, 50].map(ri => f1(snapM(G, 'them', ri, 2))).join(' / ')]);
  }
  P(table(['판본', '묶음', '판', '승', '생존', 'G', '상대 최장', '우리 샘물 생성 / 먹음 / 상대가 먹음', '계통이 450라운드 이상 통로에 / r450 이후 스스로 죽음', '바깥 왕 r300 / r400 / 끝', '상대 최장 r300 / r400 / 끝'], rows2));
}

// ---------------------------------------------------------------------------------------------------------------
H('E. 다른 지도에서 요새 판정 (px9d)');
{
  const G = of('base-px9d').filter(r => !['Autarky', 'PD6', 'PD10'].includes(r.mapKey) && r.x.ind.fort > 0);
  P(G.length ? table(['경기', '지도', '상대', '요새 턴', '라운드'], G.map(r => [r.id, r.map, r.oppName, r.x.ind.fort, r.x.ind.fortRounds.join(', ')])) : '없음');
  const fg = of('base-px9d', ['Autarky', 'PD6', 'PD10']);
  P(`- Autarky·PD ${fg.length}판: 요새 턴 판당 ${f1(per(fg, r => r.x.ind.fort))} (범위 ${Math.min(...fg.map(r => r.x.ind.fort))}–${Math.max(...fg.map(r => r.x.ind.fort))}), 그중 계통이 아닌 드래곤 ${fg.reduce((a, r) => a + r.x.ind.fortNonLin, 0)}, peel ${fg.reduce((a, r) => a + r.x.ind.peel, 0)}회, 계통이 끝까지 통로에 산 판 ${fg.filter(r => !r.x.lin.us.death && r.x.lin.us.finalIn).length}, 수 최대 r330–420 ${fg.map(r => r.x.units330.max).join(', ')}.`);
}

// checks
const c = { games: recs.length, px8: 0, fort: 0 };
for (const r of recs) { c.px8 += r.px8.chk.updates + r.px8.chk.deaths + r.px8.chk.splits + (r.px8.chk.final ? 0 : 1) + (r.px8.chk.massOk ? 0 : 1); c.fort += r.x.chk.updates + r.x.chk.deaths + r.x.chk.pearl + (r.x.chk.final ? 0 : 1) + (r.x.chk.mass ? 0 : 1); }
out.push(`\n점검: ${c.games}판, px8_study 점검 합 ${c.px8}, px9d_study 점검 합 ${c.fort} (모두 0이어야 한다).`);
console.log(out.join('\n'));
