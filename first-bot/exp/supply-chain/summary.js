#!/usr/bin/env node
// Compact tables for research/observations/supply-chain.md from the aggregate (exp/supply-chain/aggregate.js).
// usage (repository root): node exp/supply-chain/summary.js [--agg .cache/supply-chain/agg.json] [--out exp/supply-chain/summary.md]
// Same definitions as exp/supply-chain/report.js ("per game" = per team-game in progress at the phase's first round).
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const AGG = JSON.parse(fs.readFileSync(path.resolve(ROOT, opt('agg', '.cache/supply-chain/agg.json')), 'utf8'));
const acc = AGG.acc;
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const ELIM = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Prisoners Dilemma (10)', 'Queen Of Spades', 'Default'];
const KN = { r500: '500라운드형', elim: '전멸형' };
const G = ['TW', 'TL', 'X', 'merge2', 'stack1', 'stack2', 'stack3', 'stack4', 'stack5', 'stack6'].filter(g => acc[g]);
const GN = { TW: '상위권 승자', TL: '상위권 패자', X: '우리 판의 상대', merge2: 'merge2', stack1: 'stack1', stack2: 'stack2', stack3: 'stack3', stack4: 'stack4', stack5: 'stack5', stack6: 'stack6' };
const PH = [[0, 10], [10, 25], [25, 35], [35, 45], [45, 50]];
const out = []; const P = s => out.push(s);
const f1 = v => v === null || v === undefined || !isFinite(v) ? '–' : (Math.round(v * 10) / 10).toFixed(1);
const f2 = v => v === null || v === undefined || !isFinite(v) ? '–' : (Math.round(v * 100) / 100).toFixed(2);
const pc = (a, b) => b > 0 ? Math.round(100 * a / b) + '%' : '–';
const table = (head, rows) => { P('| ' + head.join(' | ') + ' |'); P('|' + head.map((_, i) => i === 0 ? '---' : '---:').join('|') + '|'); for (const r of rows) P('| ' + r.join(' | ') + ' |'); P(''); };
function merged(group, maps) {
  const A = acc[group]; if (!A) return null;
  const m = { n: 0, nPh: [0, 0, 0, 0, 0], b: {}, ep: {}, tag: {}, tagD: {}, dr: {}, sp: {}, dt: {}, cp: {}, h: {}, pc: {}, ph: {} };
  const addArr = (o, k, a) => { const t = o[k] || (o[k] = new Array(a.length).fill(0)); for (let i = 0; i < a.length; i++) t[i] += a[i] || 0; };
  for (const mp of maps) {
    const x = A[mp]; if (!x) continue;
    m.n += x.n; for (let i = 0; i < 5; i++) m.nPh[i] += x.nPh[i];
    for (const s of ['b', 'ep', 'tag', 'tagD', 'dr', 'sp', 'dt', 'h', 'pc']) for (const [k, v] of Object.entries(x[s])) addArr(m[s], k, v);
    for (const [k, v] of Object.entries(x.cp)) { const c = m.cp[k] || (m.cp[k] = { s: new Array(50).fill(0), c: new Array(50).fill(0) }); for (let i = 0; i < 50; i++) { c.s[i] += v.s[i]; c.c[i] += v.c[i]; } }
    for (const [k, v] of Object.entries(x.ph)) { const t = m.ph[k] || (m.ph[k] = {}); for (const [h, a] of Object.entries(v)) addArr(t, h, a); }
  }
  return m.n ? m : null;
}
const M = {}; for (const g of G) M[g] = { r500: merged(g, R500), elim: merged(g, ELIM) };
const bsum = (m, name, p0, p1) => { const a = m.b[name]; if (!a) return 0; let s = 0; for (let i = PH[p0][0]; i < PH[p1][1]; i++) s += a[i]; return s; };
const epv = (m, e, p0, p1, i) => { const a = m.ep[e]; if (!a) return 0; let s = 0; for (let p = p0; p <= p1; p++) s += a[p * 9 + i]; return s; };
const ours = g => !['TW', 'TL', 'X'].includes(g);
function dtSum(m, f) { const s = new Array(9).fill(0); for (const [k, v] of Object.entries(m.dt)) { const [ph, c, lc, nr, mh] = k.split('|'); if (!f(+ph, +c, +lc, nr, mh || 'o')) continue; for (let i = 0; i < 9; i++) s[i] += v[i]; } return s; }
function drSum(m, f) { const s = new Array(11).fill(0); for (const [k, v] of Object.entries(m.dr)) { const [ph, o, cg, w6, view, cont] = k.split('|').map(Number); if (!f(ph, o, cg, w6, view, cont)) continue; for (let i = 0; i < 11; i++) s[i] += v[i]; } return s; }
function pcv(m, keys) { const v = new Array(64).fill(0), h = {}; for (const k of keys) { const a = m.pc[k]; if (a) for (let i = 0; i < 64; i++) v[i] += a[i]; const hh = m.ph[k]; if (hh) for (const [n, arr] of Object.entries(hh)) { const t = h[n] || (h[n] = new Array(arr.length).fill(0)); for (let i = 0; i < arr.length; i++) t[i] += arr[i]; } } return { v, h }; }
const LIFE_E = ['0', '1-4', '5-9', '10-19', '20-49', '50-99', '100-199', '200+'];
const hmed = (h, edges) => { if (!h) return '–'; const n = h.reduce((a, b) => a + b, 0); let c = 0; for (let i = 0; i < h.length; i++) { c += h[i]; if (c * 2 >= n) return edges[i]; } return '–'; };

P(`# 요약 표 (생성 ${new Date().toISOString()}, 집계 ${AGG.at})`);
P(`- 파일: ${Object.entries(AGG.counts).map(([f, n]) => f.replace('.jsonl.gz', '') + ' ' + n).join(', ')}`);
P(`- 상위권 제외: ${JSON.stringify(AGG.excluded)}; 재구성 점검 합: ${JSON.stringify(AGG.chkSum)}`);
P('');
P('## 모집단(팀-경기)');
table(['집단', '500라운드형', '전멸형', 'r250까지 간 500형', 'r250까지 간 전멸형'], G.map(g => [GN[g], M[g].r500 ? M[g].r500.n : 0, M[g].elim ? M[g].elim.n : 0, M[g].r500 ? M[g].r500.nPh[2] : 0, M[g].elim ? M[g].elim.nPh[2] : 0]));

for (const k of ['r500', 'elim']) {
  P(`## T1 conv 깔때기, r250–499, ${KN[k]}`);
  table(['집단', '판(r250까지)', '조각 턴/판', '상태 턴/판', '조각 턴 중', '에피소드/판', '발동(희생)', '우리 표식', '발동 중 성공', '발동 중 큰 아군 몫', '발동/판', '큰 아군 성공/판'],
    G.filter(g => M[g][k]).map(g => { const m = M[g][k], n = m.nPh[2]; const eps = epv(m, 'cs', 2, 4, 0), fi = epv(m, 'cs', 2, 4, 1);
      return [GN[g], n, f1(bsum(m, 'turnsP', 2, 4) / n), f1(bsum(m, 'cs', 2, 4) / n), pc(bsum(m, 'cs', 2, 4), bsum(m, 'turnsP', 2, 4)), f1(eps / n), pc(fi, eps), ours(g) ? pc(epv(m, 'cs', 2, 4, 2), eps) : '–', pc(epv(m, 'cs', 2, 4, 6), fi), pc(epv(m, 'cs', 2, 4, 7), fi), f2(fi / n), f2(epv(m, 'cs', 2, 4, 7) / n)]; }));
  P(`### T1b conv 상태 턴/판 국면별 (r250–349 / r350–449 / r450–499), ${KN[k]}`);
  table(['집단', 'r250–349', 'r350–449', 'r450–499', '상태가 있는 라운드 비율(r250–499)'], G.filter(g => M[g][k]).map(g => { const m = M[g][k]; return [GN[g], ...[2, 3, 4].map(p => f1(bsum(m, 'cs', p, p) / Math.max(1, m.nPh[p]))), pc(bsum(m, 'csR', 2, 4), bsum(m, 'rounds', 2, 4))]; }));
  P(`## T2 feed 깔때기, r250–499, ${KN[k]}`);
  table(['집단', '상태 턴/판', '에피소드/판', '발동(희생)', '우리 표식', '발동 중 큰 아군 몫', '발동/판', 'fsK 에피소드/판', 'fsK 발동', 'fsG 에피소드/판', 'fsG 발동'],
    G.filter(g => M[g][k]).map(g => { const m = M[g][k], n = m.nPh[2]; const eps = epv(m, 'fs', 2, 4, 0), fi = epv(m, 'fs', 2, 4, 1);
      return [GN[g], f1(bsum(m, 'fs', 2, 4) / n), f1(eps / n), pc(fi, eps), ours(g) ? pc(epv(m, 'fs', 2, 4, 2), eps) : '–', pc(epv(m, 'fs', 2, 4, 7), fi), f2(fi / n), f1(epv(m, 'fsK', 2, 4, 0) / n), pc(epv(m, 'fsK', 2, 4, 1), epv(m, 'fsK', 2, 4, 0)), f1(epv(m, 'fsG', 2, 4, 0) / n), pc(epv(m, 'fsG', 2, 4, 1), epv(m, 'fsG', 2, 4, 0))]; }));
  P(`## T3 모이기 상태(r340+, 왕 아님, 길이 ≥4, 수 ≥4), ${KN[k]}`);
  table(['집단', '상태 턴/판(r350까지 간 판)', '왕까지 ≤3', '4–5', '6–8', '9–15', '16+', '가까워진 턴'], G.filter(g => M[g][k]).map(g => { const m = M[g][k], n = m.nPh[3]; const gs = bsum(m, 'gs', 3, 4); return [GN[g], f1(gs / Math.max(1, n)), ...[0, 1, 2, 3, 4].map(i => pc(bsum(m, 'gsK' + i, 3, 4), gs)), pc(bsum(m, 'gsApp', 3, 4), bsum(m, 'gsPrev', 3, 4))]; }));
  P(`## T4 grab: 우리 머리 6걸음 안의 새 사망 진주(처음 6라운드), ${KN[k]}`);
  const rows4 = [];
  for (const g of G) { const m = M[g][k]; if (!m) continue;
    for (const [pn, p0, p1] of [['r0–249', 0, 1], ['r250–499', 2, 4]]) { const n = m.nPh[p0];
      const own = drSum(m, (ph, o, cg, w6) => ph >= p0 && ph <= p1 && o === 0 && w6 === 1), en = drSum(m, (ph, o, cg, w6) => ph >= p0 && ph <= p1 && o === 1 && w6 === 1);
      const enAll = drSum(m, (ph, o) => ph >= p0 && ph <= p1 && o === 1), enHo = drSum(m, (ph, o, cg, w6) => ph >= p0 && ph <= p1 && o === 1 && cg === 2 && w6 === 1);
      rows4.push([GN[g], pn, f1(own[0] / n), pc(own[1], own[0]), f1(en[0] / n), pc(en[1], en[0]), pc(en[0], enAll[0]), f1(enHo[0] / n), pc(enHo[1], enHo[0]), ours(g) ? pc(own[8] + en[8], own[0] + en[0]) : '–', ours(g) ? pc(own[9] + en[9], own[8] + en[8]) : '–']); } }
  table(['집단', '국면', '우리 사망 진주/판', '우리가 먹음', '적 사망 진주/판', '우리가 먹음', '적 사망 진주 중 6걸음 안', '적 박치기 진주/판', '우리가 먹음', '우리 grab 표식', '표식 → 우리가 먹음'], rows4);
  P(`## T5 고리별 재료(진주/판), ${KN[k]}`);
  const rows5 = [];
  for (const g of G) { const m = M[g][k]; if (!m) continue;
    for (const [pn, p0, p1] of [['r0–249', 0, 1], ['r250–499', 2, 4]]) { const n = m.nPh[p0];
      const d = f => dtSum(m, (ph, c, lc, nr, mh) => ph >= p0 && ph <= p1 && f(c, lc, nr, mh));
      const convB = d((c, lc, nr, mh) => c === 0 && lc === 0 && nr === 'B' && mh !== 's'), p2p = d((c, lc, nr, mh) => c === 0 && lc === 0 && nr === 'S' && mh !== 's');
      const mbs = d((c, lc) => c === 0 && lc >= 1), trap = d((c, lc, nr, mh) => c === 1 && lc === 0 && mh !== 's'), stub = d((c, lc, nr, mh) => lc === 0 && mh === 's');
      const gO = drSum(m, (ph, o, cg, w6) => ph >= p0 && ph <= p1 && o === 0 && w6 === 1), gE = drSum(m, (ph, o, cg, w6) => ph >= p0 && ph <= p1 && o === 1 && w6 === 1);
      const pv = pcv(m, p0 === 0 ? ['0|all', '1|all'] : ['2|all', '3|all', '4|all']).v;
      rows5.push([GN[g], pn, f1(pv[0] / n), f1(pv[3] / n), f1(convB[6] / n), f1(p2p[3] / n), f1(mbs[6] / n), f1(trap[3] / n), f1(stub[3] / n), f1(gO[1] / n), f1(gE[1] / n)]); } }
  table(['집단', '국면', '태어난 조각/판', '조각의 자연 진주', 'conv형(→≥8)', '조각→조각', '중간·큰 희생(→≥8)', '갇힘 재활용', 'stub 고리', '우리 사망 진주 줍기', '적 사망 진주 줍기'], rows5);
  P(`## T6 조각 생애 장부(태어난 길이 ≤3), ${KN[k]}`);
  const rows6 = [];
  for (const g of G) { const m = M[g][k]; if (!m) continue;
    for (const [pn, keys, n] of [['r0–249 탄생', ['0|all', '1|all'], m.n], ['r250+ 탄생', ['2|all', '3|all', '4|all'], m.nPh[2]]]) {
      const { v, h } = pcv(m, keys); const N = v[0]; if (!N) continue;
      rows6.push([GN[g], pn, f1(N / n), f1(v[1] / N), hmed(h.life, LIFE_E), f1(v[2] / N), f2(v[3] / N), pc(v[4], N), pc(v[5], N), pc(v[14], v[13]), pc(v[15], v[13]), pc(v[16], N), pc(v[17], N), pc(v[18], N), pc(v[19], N), pc(v[28], v[27]), pc(v[29], v[27]), pc(v[30], v[27]), f2(v[34] / N), f2(v[35] / N)]); } }
  table(['집단', '탄생', '조각/판', '수명 평균', '수명 중앙', '걸음', '자연 진주', '30라운드 안 먹음', '+30 생존', '자기 영토 턴', '적 영토 턴', '끝까지 삶', '희생', '갇힘', '박힘', '떨군 진주 우리', '≥8이 먹음', '상대', '순기여', '새 질량'], rows6);
  P(`## T7 부류별 조각, ${KN[k]} (우리: 분열 표식, 상위권: 분열 전 부모 길이)`);
  const CLS = { 1: 'csplit', 2: 'frag', 3: 'bsp', 4: '정책 분열', 5: '탈출 분열', 6: 'esc-split', 9: '표식 없음', 10: '부모 4', 11: '부모 5–7', 12: '부모 8+' };
  const rows7 = [];
  for (const g of G) { const m = M[g][k]; if (!m) continue;
    for (const c of ours(g) ? [1, 2, 3, 4, 5] : [10, 11, 12]) for (const [pn, ps] of [['<r250', ['0', '1']], ['r250+', ['2', '3', '4']]]) {
      const { v, h } = pcv(m, ps.map(p => p + '|' + c)); const N = v[0]; if (!N || N < 10) continue;
      rows7.push([GN[g], CLS[c] + ' ' + pn, N, f1(N / (pn === '<r250' ? m.n : m.nPh[2])), hmed(h.life, LIFE_E), f2(v[3] / N), pc(v[4], N), pc(v[5], N), pc(v[17], N), pc(v[18], N), pc(v[19], N), pc(v[29], v[27]), f2(v[34] / N), f2(v[36] / N), pc(v[37], v[36])]); } }
  table(['집단', '부류', '조각', '판당', '수명 중앙', '자연 진주', '30라운드 안 먹음', '+30 생존', '희생', '갇힘', '박힘', '≥8이 먹음', '순기여', '선점 진주(30라운드)', '선점 → 먹음'], rows7);
  P(`## T8 대형: 조각 턴의 분포(국면별), ${KN[k]}`);
  const rows8 = [];
  for (const g of G) { const m = M[g][k]; if (!m) continue;
    for (let p = 0; p < 5; p++) { const hb = m.h.pBig, hn = m.h.pNnd, h5 = m.h.pN5, hp = m.h.bPc5; if (!hb) continue;
      const B = hb.slice(p * 7, p * 7 + 7), Nn = hn.slice(p * 7, p * 7 + 7), F5 = h5.slice(p * 6, p * 6 + 6), Pc = hp ? hp.slice(p * 5, p * 5 + 5) : [0, 0, 0, 0, 0];
      const nb = B.reduce((a, b) => a + b, 0), np = Pc.reduce((a, b) => a + b, 0); if (!nb) continue;
      rows8.push([GN[g], ['r0–99', 'r100–249', 'r250–349', 'r350–449', 'r450–499'][p], pc(B[0] + B[1], nb), pc(B[6], nb), pc(Nn[0] + Nn[1], nb), pc(Nn[0] + Nn[1] + Nn[2], nb), pc(F5[3] + F5[4] + F5[5], nb), pc(np - Pc[0], np)]); } }
  table(['집단', '국면', '큰 아군 ≤5', '큰 아군 없음', '가장 가까운 아군 ≤2', '≤3', '5칸 안 아군 ≥3', '큰 아군 턴 중 5칸 안 조각 ≥1'], rows8);
  P(`## T9 기준 라운드의 배치, ${KN[k]}`);
  const rows9 = [];
  for (const g of G) { const m = M[g][k]; if (!m) continue;
    for (const r of [100, 250, 350]) { const i = r / 10, cv = nm => m.cp[nm] && m.cp[nm].c[i] ? m.cp[nm].s[i] / m.cp[nm].c[i] : null;
      const cellP = m.cp.cellP && m.cp.pieces && m.cp.pieces.s[i] ? m.cp.cellP.s[i] / 10 / m.cp.pieces.s[i] : null;
      rows9.push([GN[g], 'r' + r, m.cp.units ? m.cp.units.c[i] : 0, f1(cv('units')), f1(cv('pieces')), f1(cv('bigs')), f1(cv('pEn')), pc(cv('vor'), 1000), pc(cv('unc'), 1000), pc(cv('ecl'), 1000), f1(cv('svc') / 100), f2(cellP)]); } }
  table(['집단', '라운드', '판', '드래곤', '조각', '≥8', '적 영토의 조각', '자기 영토 보로노이', '빈 몫(양쪽 6 밖)', '적이 가까운 몫', '서비스 거리', '조각 셀(생성/30라운드)'], rows9);
  P(`## T10 r0–249에 태어난 조각의 30라운드 먹이: 조건별(비율 / 먹은 비율), ${KN[k]}`);
  for (const [nm, edges, title] of [['n30_claim', ['0', '1', '2', '3–5', '6+'], '선점 진주 수'], ['n30_n5', ['0', '1', '2', '3–4', '5–8', '9+'], '태어날 때 5칸 안 아군 머리'], ['n30_nnd', ['1', '2', '3', '4–5', '6–8', '9+', '없음'], '태어날 때 가장 가까운 아군 머리'], ['n30_big', ['≤3', '4–5', '6–8', '9–12', '13–20', '21+', '없음'], '태어날 때 가장 가까운 ≥8'], ['n30_bt', ['자기', '중립', '적'], '태어난 영토'], ['n30_view', ['없음', '있음'], '태어날 때 시야의 적 머리']]) {
    P(`### ${title}`);
    const rows = [];
    for (const g of G) { const m = M[g][k]; if (!m) continue; const { h } = pcv(m, ['0|all', '1|all']); const c = h[nm]; if (!c) continue; const nb = edges.length, tot = c.reduce((a, b) => a + b, 0); if (!tot) continue;
      rows.push([GN[g], tot, ...edges.map((_, i) => `${pc(c[2 * i] + c[2 * i + 1], tot)} / ${pc(c[2 * i + 1], c[2 * i] + c[2 * i + 1])}`)]); }
    table(['집단', '조각', ...edges], rows);
  }
  P(`## T11 희생으로 끝난 조각의 큰 아군(≥8) 거리, ${KN[k]}`);
  const DE = ['≤3', '4–5', '6–8', '9–12', '13–20', '21+', '없음'];
  for (const [nm, title] of [['fedBirth', '태어날 때'], ['fedMax', '생애 최대'], ['fed10', '끝 10턴 전'], ['fedLast', '마지막 턴']]) {
    const rows = []; for (const g of G) { const m = M[g][k]; if (!m) continue; const h = (m.ph['all|all'] || {})[nm]; if (!h) continue; const n = h.reduce((a, b) => a + b, 0); rows.push([GN[g], n, ...h.map(v => pc(v, n))]); }
    P(`### ${title}`); table(['집단', '희생한 조각', ...DE], rows);
  }
}
const outF = path.resolve(ROOT, opt('out', 'exp/supply-chain/summary.md'));
fs.writeFileSync(outF, out.join('\n') + '\n');
console.error(`wrote ${path.relative(ROOT, outF)} (${out.length} lines)`);
