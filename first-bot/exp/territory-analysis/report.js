#!/usr/bin/env node
// report.js — tables for research/observations/top-territory.md from exp/territory-analysis/cache (extract.js).
// usage (repository root): node --max-old-space-size=12000 exp/territory-analysis/report.js [--top top-all] [--out exp/territory-analysis/report-all]
// Writes <out>.md (tables) and <out>.json (key numbers). Reads the cache only.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const S = require('./summarise.js');
const { CI, DB, OB, PHN, DEP, BOTS, hMed, epAddInto } = S;
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const OUT = path.resolve(ROOT, opt('out', 'exp/territory-analysis/report-all'));
const J = {};
const L = [];
const P = (...a) => L.push(a.join(''));
const f1 = (x, d = 1) => Number.isFinite(x) ? x.toFixed(d) : '–';
const pc = (a, b, d = 0) => b ? (100 * a / b).toFixed(d) + '%' : '–';
const pcx = (x, d = 0) => Number.isFinite(x) ? (100 * x).toFixed(d) + '%' : '–';
const sum = a => { let s = 0; for (const v of a) s += v; return s; };
const mean = a => a.length ? sum(a) / a.length : NaN;
const fmean = a => mean(a.filter(Number.isFinite));
const table = (head, rows) => { P('| ' + head.join(' | ') + ' |'); P('|' + head.map((h, i) => i ? '---:' : '---').join('|') + '|'); for (const r of rows) P('| ' + r.join(' | ') + ' |'); P(''); };
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function bootMean(a, B = 1000) { if (a.length < 2) return [NaN, NaN]; const r = rng(12345), bs = new Float64Array(B); for (let i = 0; i < B; i++) { let s = 0; for (let j = 0; j < a.length; j++) s += a[Math.floor(r() * a.length)]; bs[i] = s / a.length; } bs.sort(); return [bs[Math.floor(B * 0.025)], bs[Math.floor(B * 0.975)]]; }
const ci = (a, d = 1, scale = 1) => { const [lo, hi] = bootMean(a); return `${f1(mean(a) * scale, d)} [${f1(lo * scale, d)}, ${f1(hi * scale, d)}]`; };
function bootRatio(xs, num, den, B = 1000) { if (xs.length < 2) return [NaN, NaN]; const r = rng(99), bs = new Float64Array(B); const nu = xs.map(num), de = xs.map(den); for (let i = 0; i < B; i++) { let a = 0, b = 0; for (let j = 0; j < xs.length; j++) { const k = Math.floor(r() * xs.length); a += nu[k]; b += de[k]; } bs[i] = b ? a / b : NaN; } bs.sort(); return [bs[Math.floor(B * 0.025)], bs[Math.floor(B * 0.975)]]; }
const ciR = (xs, num, den) => { const a = sum(xs.map(num)), b = sum(xs.map(den)); const [lo, hi] = bootRatio(xs, num, den); return `${pcx(a / b)} [${pcx(lo)}, ${pcx(hi)}]`; };

(async () => {
  const { TG, excluded, chkSum, nGames } = await S.load({ top: opt('top', 'top-all') });
  const GN = { TW: 'TW(상위 승자)', TL: 'TL(상위 패자)', X: 'X(우리 봇들의 상대, 합)', 'X-merge2': 'X(merge2의 상대)' };
  for (const b of BOTS) { GN[b] = b; if (!GN['X-' + b]) GN['X-' + b] = 'X(' + b + '의 상대)'; }
  const inGrp = (x, g) => g === 'X' ? x.grp2 === 'X' : x.grp === g;
  const sel = (g, kind, extra = () => true) => TG.filter(x => inGrp(x, g) && x.kind === kind && extra(x));
  const KINDS = [['r500', '500라운드형(모든 판)'], ['elim', '전멸형(모든 판)']];
  const MAIN = ['TW', 'TL', 'merge2', 'X-merge2', 'X'];
  const ALLG = ['TW', 'TL', ...BOTS, 'X', 'X-merge2'];

  P('# 영토 분석 표 (exp/territory-analysis/report.js)', '');
  P(`- 경기: 상위권 ${nGames.top}판(제외 뒤), 온라인 ${nGames.online}판. 제외 ${JSON.stringify(excluded)}. 팀·경기 ${TG.length}개.`);
  P(`- 점검 합(모두 0이어야 한다): ${JSON.stringify(chkSum)}`);
  const vh = {}; for (const x of TG) if (x.ti === 0 && ['Devil', 'Queen Of Spades', 'Schooltime', 'Slithery Fight'].includes(x.map)) { const k = x.vhow + (x.vhow === 'assign' ? (x.vguess === x.variant ? '=추정' : '≠추정') : ''); vh[k] = (vh[k] || 0) + 1; }
  P(`- 판본(b 판본이 있는 네 지도): ${JSON.stringify(vh)} (assign = data/pearl_layout/variants.json, spawns = 이 경기의 생성으로 판정; '=추정'은 두 방법이 같은 판)`);
  const cnt = {}; for (const x of TG) { const k = x.grp + '/' + x.kind; cnt[k] = (cnt[k] || 0) + 1; }
  P(`- 집단별 팀·경기 수: ${Object.entries(cnt).sort().map(([k, v]) => k + ' ' + v).join(', ')}`, '');

  // -------------------------------------------------------------------------------------------------------------
  P('## 1. 자기 영토 자연 진주의 행방 (r≥0 생성분, 판 전체)', '');
  for (const [kind, kn] of KINDS) {
    P(`### ${kn}`, '');
    const rows = [];
    for (const g of ALLG) {
      const xs = sel(g, kind); if (!xs.length) continue;
      const sp = sum(xs.map(x => x.s.ownSp)), fsp = sum(xs.map(x => x.s.fSp));
      const neu = [0, 1, 2, 3].map(i => sum(xs.map(x => x.s.neu[i])));
      const enT = [0, 1, 2, 3].map(i => sum(xs.map(x => x.s.enT[i])));
      rows.push([GN[g], xs.length, f1(sp / xs.length), ciR(xs, x => x.s.ownEat, x => x.s.ownSp), ciR(xs, x => x.s.enEat, x => x.s.ownSp), pc(sum(xs.map(x => x.s.none)), sp),
        f1(sum(xs.map(x => x.s.enEat)) / xs.length), pc(fsp, sp), pc(sum(xs.map(x => x.s.fOwn)), fsp), pc(sum(xs.map(x => x.s.fEn)), fsp), `${pc(neu[1], neu[0])} / ${pc(neu[2], neu[0])}`, f1(enT[1] / xs.length), pc(enT[1], enT[0])]);
      J['own_' + g + '_' + kind] = { n: xs.length, spawn: sp / xs.length, own: sum(xs.map(x => x.s.ownEat)) / sp, enemy: sum(xs.map(x => x.s.enEat)) / sp, lostPerGame: sum(xs.map(x => x.s.enEat)) / xs.length,
        fShare: fsp / sp, fOwn: sum(xs.map(x => x.s.fOwn)) / fsp, fEn: sum(xs.map(x => x.s.fEn)) / fsp, enTerrEat: enT[1] / xs.length, enTerrShare: enT[1] / enT[0] };
    }
    table(['집단', 'N(팀·경기)', '우리 영토 생성/판', '우리가 먹음 [95%]', '상대가 먹음 [95%]', '안 먹힘', '상대가 먹은 수/판', '샘 비중', '샘: 우리', '샘: 상대', '중립 진주 우리/상대', '상대 영토 자연 진주 우리가 먹음/판', '그 몫'], rows);
  }

  // -------------------------------------------------------------------------------------------------------------
  P('## 2. 생성 순간의 경주: Δ = (가장 가까운 적 머리 거리) − (가장 가까운 우리 머리 거리)', '');
  P('- 거리는 지도 위 이동 거리(해초·포털·감싸기, 몸은 무시)다. Δ>0이면 우리가 더 가깝다. noEn = 적 머리가 닿을 길이 없음(Portals 등). 괄호 = 그 칸에서 상대가 먹은 비율.', '');
  for (const [kind, kn] of KINDS) {
    P(`### ${kn}`, '');
    const rows = [], conv = {};
    for (const g of ALLG) {
      const xs = sel(g, kind); if (!xs.length) continue;
      const byD = DB.map((_, i) => [0, 1, 2, 3].map(j => sum(xs.map(x => x.s.byD[i][j]))));
      const tot = sum(byD.map(a => a[0]));
      rows.push([GN[g], xs.length, sum(byD.map(a => a[0])), ...DB.map((_, i) => `${pc(byD[i][0], tot)} (${pc(byD[i][2], byD[i][0])})`)]);
      conv[g] = byD;
      J['race_' + g + '_' + kind] = byD.map(a => ({ share: a[0] / tot, own: a[1] / a[0], enemy: a[2] / a[0] }));
    }
    table(['집단', 'N', '진주', ...DB.map(b => 'Δ ' + b)], rows);
    const lossWith = (gs, gh) => { const a = conv[gs], b = conv[gh]; if (!a || !b) return NaN; const tot = sum(a.map(x => x[0])); let s = 0; for (let i = 0; i < DB.length; i++) { const rate = b[i][0] ? b[i][2] / b[i][0] : (a[i][0] ? a[i][2] / a[i][0] : 0); s += a[i][0] / tot * rate; } return s; };
    const dec = [];
    for (const g of ['TL', ...BOTS]) if (conv[g]) { dec.push([GN[g], pcx(lossWith(g, g)), pcx(lossWith(g, 'TW')), pcx(lossWith('TW', g)), pcx(lossWith('TW', 'TW'))]); J['decomp_' + g + '_' + kind] = [lossWith(g, g), lossWith(g, 'TW'), lossWith('TW', g), lossWith('TW', 'TW')]; }
    P(`분해(${kn}): 상대가 먹는 비율 = Σ Δ칸 비율 × 그 칸의 전환율.`, '');
    table(['집단', '실제', '분포 그대로, 전환율만 TW', '분포만 TW, 전환율 그대로', 'TW 실제'], dec);
  }
  for (const [kind, kn] of KINDS) {
    P(`### ${kn}: 생성 순간 가장 가까운 우리 머리까지 거리(괄호 = 우리가 먹은 비율), 시야 안 생성, 먹기까지 걸린 라운드`, '');
    const rows = [];
    for (const g of ALLG) {
      const xs = sel(g, kind); if (!xs.length) continue;
      const byO = OB.map((_, i) => [0, 1, 2, 3].map(j => sum(xs.map(x => x.s.byO[i][j]))));
      const tot = sum(byO.map(a => a[0]));
      const vis = [0, 1].map(v => [0, 1, 2, 3].map(j => sum(xs.map(x => x.s.byVis[v][j]))));
      rows.push([GN[g], xs.length, ...OB.map((_, i) => `${pc(byO[i][0], tot)} (${pc(byO[i][1], byO[i][0])})`), `${pc(vis[1][0], tot)}`, `${pc(vis[1][1], vis[1][0])} / ${pc(vis[0][1], vis[0][0])}`,
        f1(sum(xs.map(x => x.s.latOwnSum)) / sum(xs.map(x => x.s.latOwnN))), f1(sum(xs.map(x => x.s.latEnSum)) / sum(xs.map(x => x.s.latEnN)))]);
      J['dist_' + g + '_' + kind] = { within3: (byO[0][0] + byO[1][0]) / tot, within6: (byO[0][0] + byO[1][0] + byO[2][0]) / tot, over10: (byO[4][0] + byO[5][0]) / tot, vis: vis[1][0] / tot };
    }
    table(['집단', 'N', ...OB.map(b => 'd ' + b), '시야 안 생성', '우리 먹음: 시야 안 / 밖', '우리가 먹기까지(라운드)', '상대가 먹기까지'], rows);
  }
  for (const [kind, kn] of KINDS) {
    P(`### ${kn}: 진주의 깊이(경계에서 몇 걸음 안쪽)별 생성 비율(괄호 = 상대가 먹은 비율)`, '');
    const rows = [];
    for (const g of MAIN) {
      const xs = sel(g, kind); if (!xs.length) continue;
      const byDep = DEP.map((_, i) => [0, 1, 2, 3].map(j => sum(xs.map(x => x.s.byDep[i][j]))));
      const tot = sum(byDep.map(a => a[0]));
      rows.push([GN[g], xs.length, ...DEP.map((_, i) => `${pc(byDep[i][0], tot)} (${pc(byDep[i][2], byDep[i][0])})`)]);
    }
    table(['집단', 'N', ...DEP.map(b => '깊이 ' + b)], rows);
  }
  for (const [kind, kn] of KINDS) {
    P(`### ${kn}: 우리 영토 진주를 먹은 적 드래곤의 길이와 침입 경과 라운드`, '');
    const rows = [];
    for (const g of ALLG) {
      const xs = sel(g, kind); if (!xs.length) continue;
      const Ls = [0, 1, 2, 3].map(i => sum(xs.map(x => x.s.enEatLen[i]))), A = [0, 1, 2, 3, 4].map(i => sum(xs.map(x => x.s.enEatAge[i])));
      const t = sum(Ls);
      rows.push([GN[g], xs.length, f1(t / xs.length), ...Ls.map(v => pc(v, t)), ...A.map(v => pc(v, t))]);
    }
    table(['집단(영토 주인)', 'N', '상대가 먹은 수/판', '먹은 적 L2–3', 'L4–7', 'L8–15', 'L16+', '침입 0–2라운드째', '3–9', '10–29', '30–99', '100+'], rows);
  }

  // -------------------------------------------------------------------------------------------------------------
  P('## 3. 덮기: 시간에 따른 머리 배치 (10라운드마다, 그 시점에 진행 중인 판)', '');
  P('- 몫은 칸별 생성 용량(1/평균 간격)으로 가중했다. 보로노이 = 우리 머리가 적 머리보다 가까운(같으면 반) 용량의 몫. 시야 = 우리 머리 7×7 안의 용량 몫. 샘 지킴 = 우리 영토 샘 칸 중 우리 머리가 3걸음 안에 있는 비율(샘이 있는 지도만). 간격 = 각 머리에서 가장 가까운 아군 머리까지 이동 거리(13에서 자름).', '');
  const RS = [20, 50, 100, 150, 200, 300, 400, 450];
  const covAt = (xs, r) => xs.map(x => ({ c: x.s.C.find(c => c[0] === r), x })).filter(o => o.c && o.c[CI.units] > 0);
  for (const [kind, kn] of KINDS) {
    P(`### ${kn}`, '');
    const rowsA = [], rowsB = [];
    for (const g of ALLG) {
      const xs = TG.filter(x => inGrp(x, g) && x.kind === kind); if (!xs.length) continue;
      const ca = [], cb = [];
      for (const r of RS) {
        const rr = covAt(xs, r);
        if (rr.length < 5) { ca.push('–'); cb.push('–'); continue; }
        const m = f => fmean(rr.map(f));
        const o = { n: rr.length, units: m(o => o.c[CI.units]), uEn: m(o => o.c[CI.uEn]), uOwn: m(o => o.c[CI.uOwn]), vorOwn: m(o => o.c[CI.vorOwn] / o.x.s.capOwn), vorEn: m(o => o.c[CI.vorEn] / o.x.s.capEn),
          visOwn: m(o => o.c[CI.visOwn] / o.x.s.capOwn), near5: m(o => o.c[CI.near5] / o.x.s.capOwn), fHeld: m(o => o.x.s.nFount ? o.c[CI.fHeld] / o.x.s.nFount : NaN),
          spacing: m(o => o.c[CI.spacing] >= 0 ? o.c[CI.spacing] : NaN), near2: m(o => o.c[CI.units] >= 2 && o.c[CI.near2] !== undefined ? o.c[CI.near2] / o.c[CI.units] : NaN) };
        J['cov_' + g + '_' + kind + '_' + r] = o;
        ca.push(`${f1(o.units, 0)}u ${f1(o.uEn, 1)}in · ${pcx(o.vorOwn)} · ${pcx(o.vorEn)}`);
        cb.push(`${pcx(o.visOwn)} · ${pcx(o.near5)} · ${pcx(o.fHeld)} · ${f1(o.spacing)} · ${pcx(o.near2)}`);
      }
      const n0 = covAt(xs, 20).length;
      rowsA.push([GN[g], n0, ...ca]); rowsB.push([GN[g], n0, ...cb]);
    }
    P('칸 = 드래곤 수 u, 적 영토 안 수 in · 우리 영토 보로노이 몫 · 적 영토 보로노이 몫', '');
    table(['집단', 'N(r20)', ...RS.map(r => 'r' + r)], rowsA);
    P('칸 = 우리 영토 시야 몫 · 5걸음 안 몫 · 샘 지킴 · 간격 · 2걸음 안에 아군이 있는 머리 비율', '');
    table(['집단', 'N(r20)', ...RS.map(r => 'r' + r)], rowsB);
  }
  P('### 같은 드래곤 수에서의 덮기(r50–300의 모든 10라운드 시점, 시점 수 n)', '');
  const UB = [[1, 3], [4, 7], [8, 15], [16, 31], [32, 99]];
  for (const [kind, kn] of KINDS) {
    P(`${kn}: 칸 = 5걸음 안 몫 · 시야 몫 · 보로노이 몫 · 간격 (n)`, '');
    const rows = [];
    for (const g of ALLG) {
      const xs = TG.filter(x => inGrp(x, g) && x.kind === kind); if (!xs.length) continue;
      const cells = [];
      for (const [a, b] of UB) {
        const rr = []; for (const x of xs) for (const c of x.s.C) if (c[0] >= 50 && c[0] <= 300 && c[CI.units] >= a && c[CI.units] <= b) rr.push({ c, x });
        if (rr.length < 20) { cells.push('–'); continue; }
        const m = f => fmean(rr.map(f));
        cells.push(`${pcx(m(o => o.c[CI.near5] / o.x.s.capOwn))} · ${pcx(m(o => o.c[CI.visOwn] / o.x.s.capOwn))} · ${pcx(m(o => o.c[CI.vorOwn] / o.x.s.capOwn))} · ${f1(m(o => o.c[CI.spacing] >= 0 ? o.c[CI.spacing] : NaN))} (${rr.length})`);
      }
      rows.push([GN[g], ...cells]);
    }
    table(['집단', ...UB.map(([a, b]) => `${a}–${b}마리`)], rows);
  }

  // -------------------------------------------------------------------------------------------------------------
  P('## 4. 침입(깊은 침입 = 경계에서 3걸음 이상 들어간 에피소드)', '');
  const aggOf = (xs, key) => { const t = {}; for (const x of xs) epAddInto(t, x.s[key]); return t; };
  for (const [kind, kn] of KINDS) {
    P(`### ${kn}: 침입하는 쪽`, '');
    const rows = [], rows2 = [];
    for (const g of ALLG) {
      const xs = sel(g, kind); if (!xs.length) continue;
      const a = aggOf(xs, 'raid');
      const ph = PHN.map((_, i) => { const [p, q] = [[0, 10], [10, 25], [25, 35], [35, 45], [45, 50]][i]; let en = 0, rd = 0; for (const x of xs) for (let k = p; k < q; k++) { en += x.s.LOC.en[k]; rd += x.s.LOC.rounds[k]; } return rd ? en / rd : NaN; });
      const enLen = sum(xs.map(x => sum(x.s.LOC.enLen))), enN = sum(xs.map(x => sum(x.s.LOC.en)));
      const enT = [0, 2].map(i => sum(xs.map(x => x.s.enT[i])));
      rows.push([GN[g], xs.length, ...ph.map(v => f1(v)), f1(enLen / enN), f1(a.n / xs.length), `${hMed(a.durH)} / ${hMed(a.durH, 0.9)}`, `${hMed(a.L0H)} / ${hMed(a.LmaxH)}`,
        pc(a.born, a.n), f1(a.nat / a.n, 2), f1(a.nat / a.dur, 3), `${pc(a.fnt, a.nat)} (${pc(enT[1], enT[0])})`, `${pc(a.fr, a.upd)} (${pcx(fmean(xs.map(x => x.s.nearFShareEn)))})`, pc(a.natH[0], a.n)]);
      const died = a.exit[1];
      rows2.push([GN[g], xs.length, pc(a.exit[0], a.n), pc(died, a.n), pc(a.exit[2], a.n), pc(a.dContact, a.n), pc(a.dSac, a.n), pc(a.dTrap, a.n), pc(a.dAlly, a.n), f1(a.trades / a.n, 2)]);
      J['raid_' + g + '_' + kind] = { n: xs.length, raidersPerRound: ph, raiderLen: enLen / enN, epsPerGame: a.n / xs.length, durMed: hMed(a.durH), L0Med: hMed(a.L0H), LmaxMed: hMed(a.LmaxH), born: a.born / a.n,
        natPerEp: a.nat / a.n, natPerRound: a.nat / a.dur, fShareEaten: a.fnt / a.nat, fShareSpawn: enT[1] / enT[0], nearFRounds: a.fr / a.upd, nearFTiles: fmean(xs.map(x => x.s.nearFShareEn)),
        left: a.exit[0] / a.n, died: died / a.n, killedByContact: a.dContact / a.n, sac: a.dSac / a.n, trap: a.dTrap / a.n, zeroNat: a.natH[0] / a.n };
    }
    table(['집단', 'N', ...PHN.map(p => '침입 수 ' + p), '침입자 평균 길이', '깊은 침입/판', '지속 중앙/90%', '처음 L / 최대 L(중앙)', '안에서 태어남', '자연 진주/침입', '자연 진주/침입 라운드', '먹은 자연 진주 중 샘 (그 영토 생성 중 샘)', '샘 3걸음 안 라운드 (그 영토 칸 중)', '하나도 못 먹은 침입'], rows);
    P(`${kn}: 침입의 끝`, '');
    table(['집단', 'N', '돌아감', '죽음', '판 끝', '수비 접촉으로 죽음', '스스로: 희생', '스스로: 갇힘', '아군과 부딪힘', '박치기 교환/침입'], rows2);
  }

  // -------------------------------------------------------------------------------------------------------------
  P('## 5. 수비: 침입에 어떻게 반응하나', '');
  P('접촉 = 침입 중 우리 머리가 1걸음 안까지 온 적이 있음. 다가감 = 침입 시작에 6걸음 안에 있던 우리 머리가 3라운드 뒤 그 침입자가 섰던 칸에 더 가까워진 비율(다가감/(다가감+멀어짐)). 기준선 = 5라운드마다 우리 머리 6걸음 안의 모든 적 머리에 대해 같은 값을, 적이 선 곳(우리 영토/중립/적 영토)별로 잰 것.', '');
  for (const [kind, kn] of KINDS) {
    P(`### ${kn}`, '');
    const rows = [], rows2 = [];
    for (const g of ALLG) {
      const xs = sel(g, kind); if (!xs.length) continue;
      const a = aggOf(xs, 'def');
      const enc = [0, 1, 2].map(loc => [0, 1, 2].map(rl => [0, 1, 2, 3, 4].map(j => sum(xs.map(x => x.s.ENC[loc][rl][j])))));
      const encAll = loc => [0, 1, 2, 3, 4].map(j => sum(enc[loc].map(r => r[j])));
      const cl = q => pc(q[1], q[0] - q[4]);
      rows.push([GN[g], xs.length, f1(a.n / xs.length), f1(hMed(a.dDef0H), 0), pc(a.near6, a.n), pc(a.contact, a.n), pc(a.dContact, a.n), pc(a.appr, a.appr + a.retr), cl(encAll(0)), cl(encAll(1)), cl(encAll(2)), `${cl(enc[0][0])} / ${cl(enc[0][1])} / ${cl(enc[0][2])}`]);
      J['def_' + g + '_' + kind] = { n: xs.length, epsAgainst: a.n / xs.length, dDef0Med: hMed(a.dDef0H), near6: a.near6 / a.n, contact: a.contact / a.n, killed: a.dContact / a.n, approachEp: a.appr / (a.appr + a.retr),
        encCloser: [0, 1, 2].map(loc => { const q = encAll(loc); return q[1] / (q[0] - q[4]); }) };
      const byDr = DB.map((_, i) => [0, 1, 2, 3].map(j => sum(xs.map(x => x.s.byDraid[i][j]))));
      const byD = DB.map((_, i) => [0, 1, 2, 3].map(j => sum(xs.map(x => x.s.byD[i][j]))));
      const tr = sum(byDr.map(q => q[0])), ta = sum(byD.map(q => q[0]));
      const dk = [0, 1, 2].map(i => sum(xs.map(x => x.s.deathsEnemyKilled[i])));
      rows2.push([GN[g], xs.length, pc(tr, ta), pc(sum(byDr.map(q => q[2])), tr), pc(sum(byD.map(q => q[2])) - sum(byDr.map(q => q[2])), ta - tr), ...[4, 5, 6].map(i => `${pc(byDr[i][2], byDr[i][0])}`), f1(dk[0] / xs.length), f1(dk[2] / xs.length)]);
    }
    table(['집단(수비)', 'N', '받은 깊은 침입/판', '시작 때 가장 가까운 우리 머리(중앙)', '6걸음 안 수비수 있음', '접촉', '접촉으로 죽임', '다가감(침입)', '기준선: 적이 우리 영토', '중립', '적 영토', '우리 영토의 적에게: 우리가 짧음/같음/김'], rows);
    P(`${kn}: 먹기 경쟁으로 막기(가장 가까운 적 머리가 우리 영토 안 침입자인 진주)`, '');
    table(['집단', 'N', '그런 진주 비율', '그중 상대가 먹음', '나머지에서 상대가 먹음', 'Δ 1..2에서 상대', 'Δ 3..5', 'Δ ≥6', '우리 영토에서 적 접촉으로 죽은 우리 드래곤/판', '적 영토에서 적 접촉으로 죽은 우리 드래곤/판'], rows2);
  }

  // -------------------------------------------------------------------------------------------------------------
  P('## 6. 수와 몫: 드래곤 수, 퍼짐, 지킨 몫 (Portals 제외: 두 영토가 이어지지 않는다)', '');
  const noP = x => x.map !== 'Portals';
  const lostNext = (x, r) => { const q = x.s.win50; let sp = 0, en = 0; for (const i of [r / 50, r / 50 + 1]) { if (!q[i]) continue; sp += q[i][0]; en += q[i][2]; } return [sp, en]; };
  for (const [kind, kn] of KINDS) {
    for (const r of [100, 200, 300]) {
      P(`### ${kn}: r${r}의 드래곤 수 → r${r}–${r + 99}에 상대가 먹은 우리 영토 진주 몫 (n = 팀·경기)`, '');
      const rows = [];
      for (const g of ALLG) {
        const xs = TG.filter(x => inGrp(x, g) && x.kind === kind && noP(x)); if (!xs.length) continue;
        const cells = [];
        for (const [a, b] of UB) {
          const ys = xs.map(x => ({ c: x.s.C.find(c => c[0] === r), x })).filter(o => o.c && o.c[CI.units] >= a && o.c[CI.units] <= b && o.x.rounds > r + 99);
          let sp = 0, en = 0; for (const o of ys) { const [s1, e1] = lostNext(o.x, r); sp += s1; en += e1; }
          cells.push(ys.length ? `${pc(en, sp)} (n${ys.length})` : '–');
        }
        rows.push([GN[g], ...cells]);
      }
      table(['집단', ...UB.map(([a, b]) => `${a}–${b}마리`)], rows);
    }
  }
  P('### 같은 판 승자 − 패자 (상위권끼리, Portals 제외)', '');
  {
    const rows = [];
    for (const [kind, kn] of KINDS) for (const r of [50, 100, 200, 300]) {
      const ws = TG.filter(x => x.grp === 'TW' && x.kind === kind && noP(x) && x.rounds > r + 99 && x.pair);
      const du = [], dv = [], dl = [], dvis = [], dsp = [], agree = [], agreeV = [];
      for (const w of ws) {
        const l = w.pair, cw = w.s.C.find(c => c[0] === r), cl = l.s.C.find(c => c[0] === r); if (!cw || !cl) continue;
        const [sw, ew] = lostNext(w, r), [sl, el] = lostNext(l, r); if (!sw || !sl) continue;
        const lw = ew / sw, ll = el / sl;
        du.push(cw[CI.units] - cl[CI.units]); dv.push(cw[CI.vorOwn] / w.s.capOwn - cl[CI.vorOwn] / l.s.capOwn); dvis.push(cw[CI.visOwn] / w.s.capOwn - cl[CI.visOwn] / l.s.capOwn); dl.push(lw - ll);
        if (cw[CI.spacing] >= 0 && cl[CI.spacing] >= 0) dsp.push(cw[CI.spacing] - cl[CI.spacing]);
        if (cw[CI.units] !== cl[CI.units]) agree.push((cw[CI.units] > cl[CI.units]) === (lw < ll) ? 1 : 0);
        const vw = cw[CI.vorOwn] / w.s.capOwn, vl = cl[CI.vorOwn] / l.s.capOwn; if (Math.abs(vw - vl) > 0.01) agreeV.push((vw > vl) === (lw < ll) ? 1 : 0);
      }
      rows.push([kn, 'r' + r, du.length, ci(du), ci(dv, 1, 100) + '%p', ci(dvis, 1, 100) + '%p', ci(dsp), ci(dl, 1, 100) + '%p', pcx(mean(agree)), pcx(mean(agreeV))]);
      J['pair_' + kind + '_' + r] = { n: du.length, dUnits: mean(du), dVor: mean(dv), dVis: mean(dvis), dSpacing: mean(dsp), dLost: mean(dl), agreeUnits: mean(agree), agreeVor: mean(agreeV) };
    }
    table(['지도', '시점', '짝', '드래곤 수 차', '우리 영토 보로노이 몫 차', '시야 몫 차', '간격 차', '다음 100라운드 잃은 몫 차', '수가 많은 쪽이 덜 잃음', '보로노이가 큰 쪽이 덜 잃음'], rows);
  }
  P('### 상위권 팀·경기(TW+TL, Portals 제외): 보로노이 몫 구간별 다음 100라운드에 잃은 몫', '');
  {
    const rows = [];
    const VB = [[0, 0.5], [0.5, 0.8], [0.8, 0.9], [0.9, 0.95], [0.95, 0.99], [0.99, 1.01]];
    for (const [kind, kn] of KINDS) for (const r of [100, 200, 300]) {
      const xs = TG.filter(x => (x.grp === 'TW' || x.grp === 'TL') && x.kind === kind && noP(x) && x.rounds > r + 99);
      const cells = VB.map(([a, b]) => { let sp = 0, en = 0, n = 0; for (const x of xs) { const c = x.s.C.find(c => c[0] === r); if (!c) continue; const v = c[CI.vorOwn] / x.s.capOwn; if (!(v >= a && v < b)) continue; n++; const [s1, e1] = lostNext(x, r); sp += s1; en += e1; } return n ? `${pc(en, sp)} (n${n})` : '–'; });
      rows.push([kn, 'r' + r, ...cells]);
    }
    table(['지도', '시점', '<50%', '50–80%', '80–90%', '90–95%', '95–99%', '≥99%'], rows);
  }

  // -------------------------------------------------------------------------------------------------------------
  P('## 7. 우리 봇별 요약과 merge2의 상대별·지도별', '');
  {
    const rows = [];
    for (const b of BOTS) {
      const xs = TG.filter(x => x.grp === b); if (!xs.length) continue;
      const sp = sum(xs.map(x => x.s.ownSp)), en = sum(xs.map(x => x.s.enEat)), own = sum(xs.map(x => x.s.ownEat));
      const opp = xs.map(x => x.pair);
      const raid = sum(opp.map(x => sum(x.s.LOC.en))) / sum(opp.map(x => sum(x.s.LOC.rounds)));
      const ours = sum(xs.map(x => sum(x.s.LOC.en))) / sum(xs.map(x => sum(x.s.LOC.rounds)));
      const c100 = covAt(xs, 100), c200 = covAt(xs, 200);
      const enT = sum(xs.map(x => x.s.enT[1]));
      const d = aggOf(xs, 'def');
      rows.push([b, xs.length, xs.filter(x => x.win).length, `${pc(en, sp)} (${f1(en / xs.length)})`, pc(own, sp), f1(enT / xs.length), f1(ours), f1(raid), pc(d.dContact, d.n),
        f1(fmean(c100.map(o => o.c[CI.units])), 1), pcx(fmean(c100.map(o => o.c[CI.vorOwn] / o.x.s.capOwn))), f1(fmean(c200.map(o => o.c[CI.units])), 1), pcx(fmean(c200.map(o => o.c[CI.vorOwn] / o.x.s.capOwn)))]);
      J['bot_' + b] = { n: xs.length, lost: en / sp, lostPerGame: en / xs.length, kept: own / sp, enTerrEat: enT / xs.length, ourRaiders: ours, theirRaiders: raid, killedRaids: d.dContact / d.n };
    }
    P('모든 지도, 모든 판.', '');
    table(['봇', 'N(판)', '승', '우리 영토 진주를 상대가 먹음(판당)', '우리가 먹음', '상대 영토에서 먹은 자연 진주/판', '우리 침입 수/라운드', '상대 침입 수/라운드', '우리가 접촉으로 죽인 깊은 침입', '수 r100', '보로노이 r100', '수 r200', '보로노이 r200'], rows);
  }
  {
    const us = TG.filter(x => x.grp === 'merge2');
    const by = {}; for (const x of us) (by[x.opp] = by[x.opp] || []).push(x);
    const rows = [];
    for (const [o, xs] of Object.entries(by).sort()) {
      const sp = sum(xs.map(x => x.s.ownSp)), en = sum(xs.map(x => x.s.enEat)), own = sum(xs.map(x => x.s.ownEat));
      const opp = xs.map(x => x.pair), a = aggOf(opp, 'raid');
      const raid = sum(opp.map(x => sum(x.s.LOC.en))) / sum(opp.map(x => sum(x.s.LOC.rounds)));
      const oc100 = covAt(opp, 100);
      const byD = DB.map((_, i) => [0, 1, 2, 3].map(j => sum(xs.map(x => x.s.byD[i][j]))));
      const Ls = [0, 1, 2, 3].map(i => sum(xs.map(x => x.s.enEatLen[i])));
      rows.push([o, xs.length, xs.filter(x => x.win).length, f1(sp / xs.length), `${pc(en, sp)} (${f1(en / xs.length)})`, pc(own, sp), f1(raid), f1(a.n / xs.length), hMed(a.durH), pc(a.born, a.n), f1(a.nat / a.n, 2), pc(a.fnt, a.nat),
        pc(a.dContact, a.n), f1(fmean(oc100.map(q => q.c[CI.units])), 0), pc(byD[0][0] + byD[1][0], sp), pc(Ls[0], sum(Ls))]);
      J['m2opp_' + o] = { games: xs.length, lost: en / sp, lostPerGame: en / xs.length, raiders: raid, epsPerGame: a.n / xs.length, natPerEp: a.nat / a.n, fShare: a.fnt / a.nat, killed: a.dContact / a.n };
    }
    P('### merge2의 상대별 (3세트 210판, 모든 지도)', '');
    table(['상대', '판', '우리 승', '우리 영토 생성/판', '상대가 먹음(판당)', '우리가 먹음', '상대 침입 수/라운드', '깊은 침입/판', '지속 중앙', '안에서 태어남', '자연 진주/침입', '그중 샘', '우리가 접촉으로 죽인 침입', '상대 드래곤 수 r100', 'Δ ≤ −3 생성', '먹은 적 L2–3'], rows);
    const bm = {}; for (const x of us) (bm[x.mapKey] = bm[x.mapKey] || []).push(x);
    const rows2 = [];
    for (const [m, xs] of Object.entries(bm).sort()) {
      const sp = sum(xs.map(x => x.s.ownSp)), en = sum(xs.map(x => x.s.enEat)), own = sum(xs.map(x => x.s.ownEat)), fsp = sum(xs.map(x => x.s.fSp)), fen = sum(xs.map(x => x.s.fEn));
      const opp = xs.map(x => x.pair), raid = sum(opp.map(x => sum(x.s.LOC.en))) / sum(opp.map(x => sum(x.s.LOC.rounds)));
      const c = covAt(xs, 100), c2 = covAt(xs, 200);
      rows2.push([m, xs.length, f1(sp / xs.length), `${pc(en, sp)} (${f1(en / xs.length)})`, pc(own, sp), pc(fsp, sp), pc(fen, fsp), f1(raid), f1(fmean(c.map(q => q.c[CI.units])), 1),
        pcx(fmean(c.map(q => q.c[CI.vorOwn] / q.x.s.capOwn))), pcx(fmean(c2.map(q => q.c[CI.vorOwn] / q.x.s.capOwn))), pcx(fmean(c.map(q => q.c[CI.visOwn] / q.x.s.capOwn)))]);
      J['m2map_' + m] = { games: xs.length, lost: en / sp, lostPerGame: en / xs.length };
    }
    P('### merge2의 지도별', '');
    table(['지도', '판', '우리 영토 생성/판', '상대가 먹음(판당)', '우리가 먹음', '샘 비중', '샘을 상대가', '상대 침입 수/라운드', '우리 수 r100', '보로노이 r100', '보로노이 r200', '시야 r100'], rows2);
  }

  // -------------------------------------------------------------------------------------------------------------
  P('## 8. 지도별: 상위권 승자·패자와 merge2 (상대가 먹은 우리 영토 진주 몫, 모든 판; 침입 수 = 라운드당 상대 영토 안 머리)', '');
  {
    const maps = [...new Set(TG.map(x => x.mapKey))].sort();
    const rows = [];
    for (const m of maps) {
      const cell = g => { const xs = TG.filter(x => inGrp(x, g) && x.mapKey === m); if (!xs.length) return '–'; const sp = sum(xs.map(x => x.s.ownSp)); return `${pc(sum(xs.map(x => x.s.enEat)), sp)} (n${xs.length})`; };
      const raid = g => { const xs = TG.filter(x => inGrp(x, g) && x.mapKey === m); if (!xs.length) return '–'; return f1(sum(xs.map(x => sum(x.s.LOC.en))) / sum(xs.map(x => sum(x.s.LOC.rounds)))); };
      const vor = g => { const xs = TG.filter(x => inGrp(x, g) && x.mapKey === m); const c = covAt(xs, 100); return c.length ? pcx(fmean(c.map(q => q.c[CI.vorOwn] / q.x.s.capOwn))) : '–'; };
      const un = g => { const xs = TG.filter(x => inGrp(x, g) && x.mapKey === m); const c = covAt(xs, 100); return c.length ? f1(fmean(c.map(q => q.c[CI.units])), 0) : '–'; };
      const tw = TG.filter(x => x.grp === 'TW' && x.mapKey === m), tiles = tw.length ? tw[0].s.terrTiles : NaN;
      const u50 = covAt(tw, 50), u100 = covAt(tw, 100);
      const fh = g => { const xs = TG.filter(x => inGrp(x, g) && x.mapKey === m); const c = covAt(xs, 100).filter(q => q.x.s.nFount > 0); return c.length ? pcx(fmean(c.map(q => q.c[CI.fHeld] / q.x.s.nFount))) : '–'; };
      rows.push([m, tiles, cell('TW'), cell('TL'), cell('merge2'), cell('X-merge2'), raid('TW'), raid('TL'), raid('X-merge2'), `${un('TW')} / ${un('TL')} / ${un('merge2')} / ${un('X-merge2')}`,
        `${f1(fmean(u50.map(q => q.c[CI.units])) / tiles * 100, 1)} / ${f1(fmean(u100.map(q => q.c[CI.units])) / tiles * 100, 1)}`, `${vor('TW')} / ${vor('TL')} / ${vor('merge2')}`, `${fh('TW')} / ${fh('TL')} / ${fh('merge2')}`]);
      J['map_' + m] = { tiles, twU50: fmean(u50.map(q => q.c[CI.units])), twU100: fmean(u100.map(q => q.c[CI.units])) };
    }
    table(['지도', '한 팀 영토 칸', 'TW 잃음', 'TL 잃음', 'merge2 잃음', 'X(merge2 상대) 잃음', 'TW 침입 수', 'TL 침입 수', 'X(merge2 상대) 침입 수', '수 r100: TW / TL / merge2 / X', 'TW 수 ÷ 영토 칸 ×100: r50 / r100', '보로노이 r100: TW / TL / merge2', '샘 지킴 r100: TW / TL / merge2'], rows);
  }

  // -------------------------------------------------------------------------------------------------------------
  P('## 9. 국면별 Δ 분포: 우리 영토 진주가 생길 때 적이 3걸음 이상 가까운 비율(Δ ≤ −3)과 그 진주를 상대가 먹은 비율', '');
  for (const [kind, kn] of KINDS) {
    const rows = [];
    for (const g of ALLG) {
      const xs = sel(g, kind); if (!xs.length) continue;
      rows.push([GN[g], xs.length, ...PHN.map((_, ph) => { const byD = DB.map((_, i) => [0, 1, 2, 3].map(j => sum(xs.map(x => x.s.byDph[ph][i][j])))); const tot = sum(byD.map(a => a[0])); const far = byD[0][0] + byD[1][0]; return `${pc(far, tot)} (${pc(byD[0][2] + byD[1][2], far)})`; })]);
    }
    P(`### ${kn}`, '');
    table(['집단', 'N', ...PHN], rows);
  }

  fs.writeFileSync(OUT + '.md', L.join('\n') + '\n');
  fs.writeFileSync(OUT + '.json', JSON.stringify(J, null, 1));
  console.log(`wrote ${path.relative(ROOT, OUT)}.md/.json (${TG.length} team-games; top ${nGames.top}, online ${nGames.online})`);
})().catch(e => { console.error(e); process.exit(1); });
