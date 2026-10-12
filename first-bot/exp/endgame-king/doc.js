#!/usr/bin/env node
// Korean tables for research/observations/endgame-king.md, straight from .cache/endgame-king/*.jsonl (same population rules as
// report.js). usage: node exp/endgame-king/doc.js > exp/endgame-king/doc-tables.md
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'endgame-king');
const SETGRP = {
  'cand-stack1-online': 'stack1–4', 'cand-stack2-online': 'stack1–4', 'cand-stack3-online': 'stack1–4', 'cand-stack4-online': 'stack1–4',
  'cand-stack5-online': 'stack5–7', 'cand-stack6-online': 'stack5–7', 'cand-stack6-online-r2': 'stack5–7', 'cand-stack7-online': 'stack5–7', 'cand-stack8-online': 'stack8',
  'cand-merge2-online': 'merge2', 'cand-merge2-online-r2': 'merge2', 'cand-merge2-online-r3': 'merge2',
  'cand-swarm8-online': '옛 봇', 'cand-avoid6-online': '옛 봇', 'cand-portal1-online': '옛 봇', 'baseline-r1': 'g4r4', 'baseline-r1b': 'g4r4', 'baseline-r1c': 'g4r4',
  'base-px8-online': 'px', 'base-px9d-online': 'px', 'px-king-v2-online': 'px',
};
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const OURS = ['g4r4', 'merge2', 'stack1–4', 'stack5–7', 'stack8', 'px'];
const G = ['상위권 승자', '상위권 패자', '우리 판의 상대', ...OURS];
const teams = []; const chk = {}, chk2 = {}; let nTop = 0, nTopKept = 0; const nSet = {};
for (const f of fs.readdirSync(CACHE).filter(f => f.endsWith('.jsonl'))) {
  const isTop = f.startsWith('top');
  for (const l of fs.readFileSync(path.join(CACHE, f), 'utf8').split('\n')) {
    if (!l.trim()) continue; const g = JSON.parse(l);
    for (const [k, v] of Object.entries(g.chk)) chk[k] = (chk[k] || 0) + v; for (const [k, v] of Object.entries(g.chk2)) chk2[k] = (chk2[k] || 0) + v;
    if (isTop) { nTop++; if (!g.winner) continue; if (['A', 'B'].some(t => g[t].splits <= 3 && g[t].sonar === 0) || g.A.faults + g.B.faults >= 3) continue; nTopKept++; for (const t of ['A', 'B']) teams.push({ grp: t === g.winner ? '상위권 승자' : '상위권 패자', g, t }); }
    else { const grp = SETGRP[g.set]; if (!grp) continue; nSet[g.set] = (nSet[g.set] || 0) + 1; teams.push({ grp, g, t: g.us, ours: 1 }); teams.push({ grp: '우리 판의 상대', g, t: g.us === 'A' ? 'B' : 'A' }); }
  }
}
// W/L rows of the lineage tables (T1, T1b, T1c, T1e, T2, T2b) come from the mass ledger's full cache (every data/top game at
// 11:34 KST), converted to this file's per-team shape: Lt[t] and dec[bin][nat, ownSac, ownOther, enemy, sprint, lossOff, lossPath].
const { FI } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const ARGV = process.argv.slice(2), aopt = (k, d) => { const i = ARGV.indexOf('--' + k); return i >= 0 ? ARGV[i + 1] : d; };
const LIN = aopt('lineage', 'pass'), ELIN = aopt('elim-lineage', LIN); // source of the W/L rows of the lineage tables
const mlTeams = []; let nMl = 0, nMlKept = 0;
if (LIN === 'ml' || ELIN === 'ml') for (const l of fs.readFileSync(path.join(ROOT, '.cache', 'mass-ledger', 'top-sample.jsonl'), 'utf8').split('\n')) {
  if (!l.trim()) continue; let g; try { g = JSON.parse(l); } catch { continue; } nMl++; // a line being appended right now is skipped
  if (!g.winner) continue;
  const faults = t => g[t].fl[FI.dn_fault].reduce((a, b) => a + b, 0);
  if (['A', 'B'].some(t => g[t].splits <= 3 && g[t].sonar === 0) || faults('A') + faults('B') >= 3) continue;
  nMlKept++;
  for (const t of ['A', 'B']) {
    const lin = g[t].lin; if (!lin) continue;
    const after = tt => { const c = lin.cp[tt]; if (!c) return null; const e = c.eat; return [e[0], e[1], e[2] + e[3] + e[4] + e[5], e[6] + e[7] + e[8] + e[9] + e[10], c.cost, c.lossOff, c.lossPath]; };
    const a = [300, 350, 400, 450].map(after);
    const dec = [new Array(7).fill(0)];
    for (let i = 0; i < 4; i++) dec.push(a[i] ? a[i].map((v, k) => v - (i < 3 && a[i + 1] ? a[i + 1][k] : 0)) : new Array(7).fill(0));
    const Lt = {}; for (const tt of [300, 350, 400, 450]) if (lin.cp[tt]) Lt[tt] = lin.cp[tt].Lt;
    const lr = {}; for (const tt of [350, 400, 450]) if (lin.cp[tt]) lr[tt] = lin.cp[tt].wasKing;
    const r = { king: lin.len, kid: 1, Lt, dec, st: { king: g[t].st.king.slice(30) }, wasKing: lr };
    mlTeams.push({ grp: t === g.winner ? '상위권 승자' : '상위권 패자', g: { kind: g.kind, rounds: g.rounds, map: g.map, winner: g.winner, [t]: r }, t, ml: 1 });
  }
}
const pct = (a, b) => b ? Math.round(100 * a / b) + '%' : '–', f1 = x => Number.isFinite(x) ? x.toFixed(1) : '–', f2 = x => Number.isFinite(x) ? x.toFixed(2) : '–';
const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN;
const median = a => { if (!a.length) return NaN; const b = a.slice().sort((x, y) => x - y); return b[Math.floor(b.length / 2)]; };
const md = (h, rows) => ['| ' + h.join(' | ') + ' |', '|' + h.map((x, i) => i ? '---:' : '---').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');
const full = x => x.g.kind === 'r500' && x.g.rounds === 500 && x.g[x.t].kid >= 0 && x.g[x.t].Lt[300] !== undefined;
const sel = (grp, f) => teams.filter(x => x.grp === grp && f(x));
// snapshot notes for the captions (the mass ledger cache holds every data/top game at its extraction time)
const ML_SNAP = (() => { try { return JSON.parse(fs.readFileSync(path.join(__dirname, 'ml-snapshot.json'), 'utf8')).at; } catch { return '2026-09-30 11:34 KST'; } })();
const PASS_SNAP = '2026-09-30 22:46 KST';
const srcNote = which => which === 'ml' ? `상위권 행: 질량 장부 캐시(${ML_SNAP}의 data/top 전부, ${nMl.toLocaleString('en-US')}판 읽음·${nMlKept.toLocaleString('en-US')}판 남김)` : `상위권 행: 이 연구의 추출(${PASS_SNAP} 스냅숏)`;
const selL = (grp, f) => { // lineage tables: W/L rows from the mass ledger cache or this study's pass, per map kind
  if (grp !== '상위권 승자' && grp !== '상위권 패자') return teams.filter(x => x.grp === grp && f(x));
  const r500 = (LIN === 'ml' ? mlTeams : teams).filter(x => x.grp === grp && x.g.kind === 'r500' && f(x));
  const elim = (ELIN === 'ml' ? mlTeams : teams).filter(x => x.grp === grp && x.g.kind === 'elim' && f(x));
  return r500.concat(elim);
};
const S = (x, i, bins = [1, 2, 3, 4]) => bins.reduce((s, b) => s + x.g[x.t].dec[b][i], 0);
const out = [];
out.push(`<!-- generated ${new Date().toISOString()} by exp/endgame-king/doc.js -->`);
{ const zero = o => Object.values(o).every(v => v === 0); const nOn = Object.values(nSet).reduce((a, b) => a + b, 0);
  out.push(`생성 기록: 상위권(이 연구의 추출) ${nTop.toLocaleString('en-US')}판 읽음, 규칙으로 남김 ${nTopKept.toLocaleString('en-US')}판. 계보 표(T1·T1b·T1c·T2·T2b)의 상위권 행은 ${LIN === 'ml' ? `질량 장부 전체 캐시 ${nMl.toLocaleString('en-US')}판(남김 ${nMlKept.toLocaleString('en-US')}판)` : '이 연구의 추출'}, 전멸형 계보 표(T1e·T1f)는 ${ELIN === 'ml' ? `질량 장부 전체 캐시 ${nMl.toLocaleString('en-US')}판(남김 ${nMlKept.toLocaleString('en-US')}판)` : '이 연구의 추출'}. 우리 ${Object.keys(nSet).length}세트 ${nOn.toLocaleString('en-US')}판. 재구성 점검 합: 장부 ${zero(chk) ? '모두 0' : JSON.stringify(chk)}, 이 연구 ${zero(chk2) ? '모두 0' : JSON.stringify(chk2)}.`); }
// T1
out.push(`\n### T1 최종 왕 계보의 r300–499 흐름 (500라운드형, 500라운드까지 간 판, 팀-경기당; ${srcNote(LIN)})`);
const t1 = [];
for (const grp of G) { const T = selL(grp, full); if (!T.length) continue;
  const m = f => mean(T.map(f));
  t1.push([grp, T.length, f1(m(x => x.g[x.t].Lt[300])), f1(m(x => S(x, 0))), f1(m(x => S(x, 1))), f1(m(x => S(x, 2))), f1(m(x => S(x, 3))), f1(-m(x => S(x, 4))), f1(-m(x => S(x, 5) + S(x, 6))), f1(m(x => x.g[x.t].king)), pct(T.filter(x => x.g.winner === x.t).length, T.length)]); }
out.push(md(['집단', '팀-경기', 'L300', '+ 자연', '+ 우리 희생', '+ 우리 다른 사망', '+ 적 사망', '− 질주', '− 분열(떼어 냄·넘김)', '= 끝 왕', '승'], t1));
// T1b per bin
out.push(`\n### T1b 50라운드마다 계보가 먹은 자연 진주 / 우리 희생 진주 (같은 판; ${srcNote(LIN)})`);
const t1b = [];
for (const grp of G) { const T = selL(grp, full); if (!T.length) continue; t1b.push([grp, T.length, ...[1, 2, 3, 4].map(b => `${f1(mean(T.map(x => x.g[x.t].dec[b][0])))} / ${f1(mean(T.map(x => x.g[x.t].dec[b][1])))}`)]); }
out.push(md(['집단', '팀-경기', 'r300–349', 'r350–399', 'r400–449', 'r450–499'], t1b));
// T1c per map
out.push(`\n### T1c 지도별 (500라운드까지 간 판): L300 → 끝 왕, r300–499 자연 / 우리 희생 (${srcNote(LIN)})`);
const t1c = [];
for (const m of R500) for (const grp of ['상위권 승자', '상위권 패자', '우리 판의 상대', 'merge2', 'stack1–4', 'stack5–7', 'stack8']) { const T = selL(grp, x => full(x) && x.g.map === m); if (!T.length) continue;
  t1c.push([m, grp, T.length, `${f1(mean(T.map(x => x.g[x.t].Lt[300])))} → ${f1(mean(T.map(x => x.g[x.t].king)))}`, `${f1(mean(T.map(x => S(x, 0))))} / ${f1(mean(T.map(x => S(x, 1))))}`, f1(mean(T.map(x => -S(x, 5) - S(x, 6))))]); }
out.push(md(['지도', '집단', '팀-경기', 'L300 → 끝 왕', '자연 / 우리 희생', '분열'], t1c));
// T1e elimination maps
out.push(`\n### T1e 전멸형 지도: 최종 왕 계보 (끝까지 산 팀; 판이 r300을 넘긴 경우; ${srcNote(ELIN)})`);
const t1e = [];
for (const grp of G) for (const end of ['500라운드', '전멸로 끝남']) {
  const T = selL(grp, x => x.g.kind === 'elim' && x.g.rounds > 300 && x.g[x.t].kid >= 0 && x.g[x.t].Lt[300] !== undefined && (end === '500라운드' ? x.g.rounds === 500 : x.g.rounds < 500)); if (T.length < 3) continue;
  t1e.push([grp, end, T.length, f1(mean(T.map(x => x.g[x.t].Lt[300]))), f1(mean(T.map(x => S(x, 0)))), f1(mean(T.map(x => S(x, 1)))), f1(mean(T.map(x => S(x, 2)))), f1(mean(T.map(x => S(x, 3)))), f1(mean(T.map(x => -S(x, 5) - S(x, 6) - S(x, 4)))), f1(mean(T.map(x => x.g[x.t].king))), f1(median(T.map(x => x.g.rounds)))]);
}
out.push(md(['집단', '끝', '팀-경기', 'L300', '+ 자연', '+ 우리 희생', '+ 우리 다른 사망', '+ 적 사망', '− 질주·분열', '= 끝 왕', '끝 라운드(중앙)'], t1e));
// T1f elimination maps, games that ran to r500: per 50-round bin
out.push(`\n### T1f 전멸형 지도, 500라운드까지 간 판: 50라운드마다 계보가 먹은 자연 / 우리 희생 진주 (${srcNote(ELIN)})`);
const t1f = [];
for (const grp of G) { const T = selL(grp, x => x.g.kind === 'elim' && x.g.rounds === 500 && x.g[x.t].kid >= 0 && x.g[x.t].Lt[300] !== undefined); if (T.length < 3) continue;
  t1f.push([grp, T.length, ...[1, 2, 3, 4].map(b => `${f1(mean(T.map(x => x.g[x.t].dec[b][0])))} / ${f1(mean(T.map(x => x.g[x.t].dec[b][1])))}`), f1(mean(T.map(x => x.g[x.t].king)))]); }
out.push(md(['집단', '팀-경기', 'r300–349', 'r350–399', 'r400–449', 'r450–499', '끝 왕'], t1f));
// T2
out.push(`\n### T2 계보 길이와 라운드당 성장 (500라운드형, 500라운드까지 간 판; ${srcNote(LIN)})`);
const t2 = [];
for (const grp of G) { const T = selL(grp, full); if (!T.length) continue;
  const L = t => mean(T.map(x => t === 500 ? x.g[x.t].king : x.g[x.t].Lt[t]));
  t2.push([grp, T.length, f1(mean(T.map(x => x.g[x.t].st.king[0]))), ...[300, 350, 400, 450, 500].map(t => f1(L(t))), ...[300, 350, 400, 450].map(t => f2((L(t + 50) - L(t)) / 50)), f2((L(500) - L(300)) / 200)]); }
out.push(md(['집단', '팀-경기', 'r300 팀 최장', '계보 L300', 'L350', 'L400', 'L450', '끝', '성장 r300–349', 'r350–399', 'r400–449', 'r450–499', 'r300–500'], t2));
out.push(`\n### T2b L300 부류별 r300→500 라운드당 성장 (팀-경기; ${srcNote(LIN)})`);
const t2b = [];
for (const grp of G) { const T = selL(grp, full); if (!T.length) continue; const row = [grp];
  for (const [a, b] of [[0, 10], [11, 20], [21, 30], [31, 999]]) { const U = T.filter(x => x.g[x.t].Lt[300] >= a && x.g[x.t].Lt[300] <= b); row.push(U.length ? `${f2(mean(U.map(x => (x.g[x.t].king - x.g[x.t].Lt[300]) / 200)))} (${U.length})` : '–'); }
  t2b.push(row); }
out.push(md(['집단', 'L300 ≤10', '11–20', '21–30', '31+'], t2b));
// T3 gathering root episodes
const fateOf = q => q[42] ? 0 : q[22] ? 1 : q[44] ? 2 : q[43] === 0 ? 3 : 4;
out.push('\n### T3 모이기 뿌리 에피소드 (우리 봇; 500라운드형 모든 판)');
const t3 = [];
for (const grp of OURS) for (const kind of ['r500', 'elim']) {
  const T = sel(grp, x => x.g.kind === kind && x.g[x.t].gath); if (!T.length) continue;
  const E = []; for (const x of T) for (const q of x.g[x.t].gath) if (!q[40]) E.push(q); if (!E.length) continue;
  const n = E.length, s = i => E.reduce((a, q) => a + q[i], 0), fc = [0, 1, 2, 3, 4].map(k => E.filter(q => fateOf(q) === k).length);
  const aliveLen = E.filter(q => fateOf(q) === 1).reduce((u, q) => u + q[35], 0);
  t3.push([grp, kind === 'r500' ? '500형' : '전멸형', T.length, f1(n / T.length), f1(s(2) / n), median(E.map(q => q[1])), median(E.map(q => q[6])), f1(s(9) / n), `${f2(s(12) / s(13))} / ${f2(s(10) / s(8))}`, pct(E.filter(q => q[14] <= 5).length, n), fc.map(v => pct(v, n)).join(' / '), pct(s(34), s(46)), `${f1(s(2) / T.length)} / ${f1(s(34) / T.length)} / ${f1(aliveLen / T.length)}`, pct(E.filter(q => q[32]).length, n), `${pct(s(39), s(36))} → ${pct(s(26), s(24))}`]);
}
out.push(md(['봇', '지도', '판', '뿌리 에피소드/판', 'L0', '시작 라운드(중앙)', '시작 때 왕까지(중앙)', '걸음', '자연/턴: 시작 전 20라운드 / 모이는 턴', '왕 5칸 안 도달', '가족의 끝: 계보 / 계보 밖 삶 / 표식 먹이 / 다른 희생 / 다른 죽음', '가족 사망 진주 → 계보', '판당 시작 길이 합 / 계보로 간 진주 / 계보 밖에서 끝까지 산 길이', '시작 때 왕 = 최종 계보', '시작 칸 5칸 안 자연 진주 → 적: 앞 40라운드 → 뒤 40라운드'], t3));
out.push('\n### T3b 지도별 모이기 뿌리 에피소드 (merge2, stack1–4, stack5–7, stack8; 500라운드형)');
const t3b = [];
for (const m of R500) for (const grp of ['merge2', 'stack1–4', 'stack5–7', 'stack8']) {
  const T = sel(grp, x => x.g.map === m && x.g[x.t].gath); if (!T.length) continue;
  const E = []; for (const x of T) for (const q of x.g[x.t].gath) if (!q[40]) E.push(q); if (!E.length) continue;
  const n = E.length, s = i => E.reduce((a, q) => a + q[i], 0), fc = [0, 1, 2, 3, 4].map(k => E.filter(q => fateOf(q) === k).length);
  t3b.push([m, grp, T.length, f1(n / T.length), fc.map(v => pct(v, n)).join(' / '), pct(s(34), s(46)), pct(E.filter(q => q[32]).length, n), `${pct(s(39), s(36))} → ${pct(s(26), s(24))}`]);
}
out.push(md(['지도', '봇', '판', '뿌리 에피소드/판', '가족의 끝: 계보 / 삶 / 표식 먹이 / 다른 희생 / 다른 죽음', '가족 사망 진주 → 계보', '시작 때 왕 = 최종 계보', '시작 칸 둘레 자연 진주 → 적: 앞 → 뒤'], t3b));
// T3c non-king by distance
out.push('\n### T3c r340 뒤 왕 아닌 드래곤(길이 ≥4)의 턴: 왕까지 거리별 몫 · 턴당 자연 진주 (500라운드형 모든 판)');
const t3c = [];
for (const grp of G) { const T = sel(grp, x => x.g.kind === 'r500'); if (!T.length) continue;
  const a = new Array(60).fill(0); for (const x of T) { const v = x.g[x.t].nk; for (let i = 0; i < 60; i++) a[i] += v[i]; }
  let tot = 0; for (let i = 0; i < 12; i++) tot += a[i * 5];
  const row = [grp, T.length, f1(tot / T.length)];
  for (let c = 0; c < 4; c++) { let t = 0, n = 0; for (let p = 0; p < 3; p++) { const b = (p * 4 + c) * 5; t += a[b]; n += a[b + 1]; } row.push(`${pct(t, tot)} · ${f2(n / t)}`); }
  let pv = 0, ap = 0; for (let i = 0; i < 12; i++) { pv += a[i * 5 + 3]; ap += a[i * 5 + 4]; } row.push(pct(ap, pv));
  t3c.push(row); }
out.push(md(['집단', '팀-경기', '턴/판', '≤3', '4–8', '9–16', '17+', '한 턴에 왕 쪽으로 가까워짐'], t3c));
// T3d cohort before/after
out.push('\n### T3d r340 무리(왕 아닌 길이 ≥4): r340 머리 5칸 안 자연 진주를 누가 먹나, r300–339 → r340–379 (500라운드형, 500라운드까지 간 판)');
const t3d = [];
for (const grp of G) for (const gf of ['all', 'g', 'noG']) {
  if (gf !== 'all' && !OURS.includes(grp)) continue;
  const T = sel(grp, full); if (!T.length) continue;
  const C = []; for (const x of T) for (const c of x.g[x.t].coh) if (gf === 'all' || (gf === 'g' ? c[11] > 0 : c[11] === 0)) C.push(c); if (!C.length) continue;
  const s = i => C.reduce((a, c) => a + c[i], 0);
  const ends = [0, 1, 2, 3, 4].map(k => pct(C.filter(c => c[3] === k).length, C.length)).join(' / ');
  t3d.push([grp, gf === 'all' ? '전부' : gf === 'g' ? '모인 것' : '안 모인 것', T.length, f1(C.length / T.length), f1(s(1) / C.length), pct(C.filter(c => c[2] > 16).length, C.length), ends, f1(s(4) / T.length), `${pct(s(20), s(17))} → ${pct(s(10), s(7))}`, `${pct(s(18), s(17))} → ${pct(s(8), s(7))}`]);
}
out.push(md(['집단', '무리', '판', '무리/판', 'L0', '왕까지 >16', '끝: 계보 / 가족 삶 / 희생 / 다른 죽음 / 분열 뒤 가족 죽음', '계보에 준 사망 진주/판', '→ 적: 앞 → 뒤', '→ 자기: 앞 → 뒤'], t3d));
// T3e labelled feeds
out.push('\n### T3e 우리 표식 먹이(feed·conv, r300 뒤)의 대상과 진주 (500라운드형 모든 판)');
const t3e = [];
for (const grp of ['merge2', 'stack1–4', 'stack5–7', 'stack8']) for (const [lab, lo, hi] of [['conv', 300, 500], ['feed', 340, 430], ['feed', 430, 500]]) {
  const T = sel(grp, x => x.g.kind === 'r500' && x.g[x.t].conv); if (!T.length) continue;
  const C = []; for (const x of T) for (const v of x.g[x.t].conv) if (v[0] === lab && v[6] && v[1] >= lo && v[1] < hi) C.push(v); if (!C.length) continue;
  const d = C.reduce((a, v) => a + v[7], 0), L = C.filter(v => v[12]), dl = L.reduce((a, v) => a + v[7], 0);
  t3e.push([grp, `${lab} r${lo}–${hi - 1}`, T.length, f2(C.length / T.length), pct(L.length, C.length), pct(C.reduce((a, v) => a + v[8], 0), d), pct(L.reduce((a, v) => a + v[10], 0), dl), pct(C.reduce((a, v) => a + v[11], 0), d), pct(C.filter(v => v[13]).length, C.length)]);
}
out.push(md(['봇', '표식', '판', '회/판', '대상이 그때 계보', '진주 → 계보', '대상이 계보일 때 다른 우리 드래곤이 먹음', '진주 → 적', '모이던 드래곤이 함'], t3e));
out.push('\n### T3f 계보가 r300–499에 먹은 우리 희생 진주의 출처 (500라운드형, 500라운드까지 간 판, 판당)');
const t3f = [];
for (const grp of ['merge2', 'stack1–4', 'stack5–7', 'stack8']) { const T = sel(grp, x => full(x) && x.g[x.t].conv); if (!T.length) continue;
  let all = 0, gf = 0, f = 0, c = 0; for (const x of T) { all += S(x, 1); for (const v of x.g[x.t].conv) { if (!v[6] || v[1] < 300) continue; if (v[0] === 'feed') { f += v[8]; if (v[13]) gf += v[8]; } else c += v[8]; } }
  t3f.push([grp, T.length, f1(all / T.length), f1(f / T.length), f1(gf / T.length), pct(gf, all), f1(c / T.length)]); }
out.push(md(['봇', '판', '계보의 우리 희생 진주', 'feed 표식에서', '그중 모이던 드래곤의 feed', '몫', 'conv 표식에서'], t3f));
// T4 sacrifices by distance to the line
out.push('\n### T4 r300 뒤 희생: 죽을 때 계보 드래곤까지 거리별 (500라운드형, 500라운드까지 간 판, 판당)');
const t4 = [];
for (const grp of G) { const T = sel(grp, full); if (!T.length) continue;
  for (const dc of [0, 1, 2, 3]) { const a = new Array(11).fill(0); for (const x of T) for (const [k, v] of Object.entries(x.g[x.t].sac)) if (+k.split('|')[1] === dc) for (let i = 0; i < 11; i++) a[i] += v[i];
    t4.push([grp, ['≤3', '4–8', '9–16', '17+'][dc], f1(a[0] / T.length), f1(a[2] / T.length), pct(a[3], a[2]), pct(a[4], a[2]), pct(a[5], a[2]), pct(a[6] + a[7], a[2]), pct(a[8], a[0]), `${pct(a[9], a[4] + a[5])} / ${pct(a[10], a[4] + a[5])}`]); } }
out.push(md(['집단', '계보까지', '희생/판', '진주/판', '→ 계보', '→ 계보 밖 더 긴 아군', '→ 계보 밖 다른 아군', '→ 적·안 먹힘', '20라운드 전 8칸 밖에서 옴', '계보 밖 먹은 쪽 가족: 끝까지 삶 / 죽으며 계보에 줌'], t4));
out.push('\n### T4b 계보가 먹은 희생 진주 (판당) · 먹이가 죽을 때 3칸 안 · 20라운드 전 8칸 밖에서 옴 · 먹이 길이 ≥8');
const t4b = [];
for (const grp of G) { const T = sel(grp, full); if (!T.length) continue; t4b.push([grp, T.length, ...[0, 1, 2, 3].map(b => { const v = [0, 1, 2, 3, 4].map(i => T.reduce((s, x) => s + x.g[x.t].lineSac[b][i], 0)); return `${f1(v[0] / T.length)} · ${pct(v[1], v[0])} · ${pct(v[2], v[0])} · ${pct(v[4], v[0])}`; })]); }
out.push(md(['집단', '팀-경기', 'r300–349', 'r350–399', 'r400–449', 'r450–499'], t4b));
out.push('\n### T4c 누가 최종 왕이 되나 (500라운드형, 500라운드까지 간 판)');
const t4c = [];
for (const grp of G) { const T = sel(grp, full); if (!T.length) continue;
  const row = [grp, T.length];
  for (const t of [300, 350, 400, 450]) { const U = T.filter(x => x.g[x.t].lr && x.g[x.t].lr[t]); row.push(pct(U.filter(x => x.g[x.t].lr[t][1] === x.g[x.t].lr[t][2]).length, U.length)); }
  const first = T.map(x => x.g[x.t].lr && x.g[x.t].lr[450] ? x.g[x.t].lr[450][3] : 0).filter(v => v > 0);
  const coh = T.filter(x => x.g[x.t].coh.some(c => c[3] === 0)), kng = T.filter(x => !x.g[x.t].coh.some(c => c[3] === 0));
  const C = coh.map(x => x.g[x.t].coh.find(c => c[3] === 0));
  row.push(median(first), pct(coh.length, T.length), C.length ? `L${f1(mean(C.map(c => c[1])))} · ${median(C.map(c => c[16]))}위 · ${median(C.map(c => c[2]))}칸` : '–', `${f1(mean(coh.map(x => x.g[x.t].king)))} / ${f1(mean(kng.map(x => x.g[x.t].king)))}`, `${pct(coh.filter(x => x.g.winner === x.t).length, coh.length)} / ${pct(kng.filter(x => x.g.winner === x.t).length, kng.length)}`);
  t4c.push(row); }
out.push(md(['집단', '팀-경기', '계보 = 팀 최장: r300', 'r350', 'r400', 'r450', '처음 최장이 된 라운드(중앙)', '최종 왕이 r340 무리에서 나옴', '그 드래곤의 r340 길이 · 순위 · 왕까지', '끝 왕: 무리에서 / r340 왕에서', '승: 무리에서 / r340 왕에서'], t4c));
// T5 exposure
out.push('\n### T5 계보 드래곤의 턴(길이 ≥8일 때): 적 머리와의 거리, 둘레 먹이, 곁의 아군 (500라운드형, 500라운드까지 간 판)');
const t5 = [];
for (const grp of G) { const T = sel(grp, full); if (!T.length) continue;
  for (const [lab, bins] of [['r300–399', [0, 1]], ['r400–499', [2, 3]]]) { const a = new Array(9).fill(0); for (const x of T) for (const b of bins) for (let i = 0; i < 9; i++) a[i] += x.g[x.t].env[b][i];
    t5.push([grp, lab, T.length, pct(a[1], a[0]), pct(a[2], a[0]), f1(a[3] / a[0]), f2(a[4] / a[0]), pct(a[5], a[0]), f2(a[7] / a[0]), f2(a[8] / a[0])]); } }
out.push(md(['집단', '구간', '팀-경기', '적 머리 ≤3', '≤6', '가장 가까운 적 머리(평균, 30에서 자름)', '5칸 안 자연 진주', '자기 영토', '6칸 안 적 머리', '6칸 안 우리 머리'], t5));
out.push('\n### T5b 지도별 적 머리 ≤6 몫 (계보 드래곤의 턴(길이 ≥8일 때), r300–499; 괄호는 팀-경기)');
const t5b = [];
for (const m of R500) { const row = [m]; for (const grp of ['상위권 승자', '상위권 패자', '우리 판의 상대', 'merge2', 'stack1–4', 'stack5–7', 'stack8']) { const T = sel(grp, x => full(x) && x.g.map === m); if (!T.length) { row.push('–'); continue; } let n = 0, k = 0; for (const x of T) for (let b = 0; b < 4; b++) { n += x.g[x.t].env[b][0]; k += x.g[x.t].env[b][2]; } row.push(`${pct(k, n)} (${T.length})`); } t5b.push(row); }
out.push(md(['지도', '상위권 승자', '상위권 패자', '우리 판의 상대', 'merge2', 'stack1–4', 'stack5–7', 'stack8'], t5b));
out.push('\n### T5c 계보의 노출(길이 ≥8인 계보 드래곤의 r300–449 턴 가운데 적 머리 ≤6 몫)과 성장 (Portals 제외, 500라운드까지 간 판)');
const t5c = [];
for (const grp of G) { const T = sel(grp, x => full(x) && x.g.map !== 'Portals'); if (!T.length) continue;
  const ex = x => { const e = x.g[x.t].env; const n = e[0][0] + e[1][0] + e[2][0]; return n ? (e[0][2] + e[1][2] + e[2][2]) / n : null; };
  for (const [a, b] of [[0, 0.1], [0.1, 0.3], [0.3, 0.6], [0.6, 1.01]]) { const U = T.filter(x => { const v = ex(x); return v !== null && v >= a && v < b; }); if (!U.length) continue;
    t5c.push([grp, `${Math.round(a * 100)}–${Math.min(100, Math.round(b * 100))}%`, U.length, f1(mean(U.map(x => x.g[x.t].Lt[300]))), f1(mean(U.map(x => S(x, 0)))), f1(mean(U.map(x => S(x, 1)))), f1(mean(U.map(x => x.g[x.t].king))), f2(mean(U.map(x => (x.g[x.t].king - x.g[x.t].Lt[300]) / 200))), pct(U.filter(x => x.g.winner === x.t).length, U.length)]); } }
out.push(md(['집단', '노출', '팀-경기', 'L300', '자연 r300+', '우리 희생 r300+', '끝 왕', '성장/라운드', '승'], t5c));
out.push('\n### T5d 길이 ≥8 우리 드래곤의 죽음 r300–499 (500라운드형, 그 구간 시작까지 간 팀-경기당): 적 머리(박힘·박음) / 아군 머리 / 갇힘 / 희생');
const t5d = [];
for (const grp of G) { const T = sel(grp, x => x.g.kind === 'r500'); if (!T.length) continue; const row = [grp, T.length];
  for (const [lo, hi] of [[300, 350], [350, 400], [400, 450], [450, 500]]) { const U = T.filter(x => x.g.rounds > lo); const K = []; for (const x of U) for (const k of x.g[x.t].kd) if (k[0] >= lo && k[0] < hi) K.push(k); const c = f => K.filter(f).length / U.length;
    row.push(`${f2(c(k => k[2] === 2 || k[2] === 3))} / ${f2(c(k => k[2] === 5))} / ${f2(c(k => k[2] === 1))} / ${f2(c(k => k[2] === 0))}`); }
  t5d.push(row); }
out.push(md(['집단', '팀-경기', 'r300–349', 'r350–399', 'r400–449', 'r450–499'], t5d));
console.log(out.join('\n'));
