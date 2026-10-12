#!/usr/bin/env node
// Final-king line decomposition for top-vs-top winners and losers from the mass ledger's full cache
// (.cache/mass-ledger/top-sample.jsonl = every game of data/top at 11:34 KST, `mass_ledger.js extract top --keys all`).
// Same quantities as exp/endgame-king/doc.js T1/T1b/T2/T2b/T1e, from lin.cp[t] (L_t and the flows after t): the flow in
// [t, t+50) = flows after t - flows after t+50. Population rule as report.js (stopped teams, >= 3 timeouts out).
// usage: node exp/endgame-king/ml_top.js > exp/endgame-king/ml-top.md
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { FI } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const f = path.join(ROOT, '.cache', 'mass-ledger', 'top-sample.jsonl');
const teams = []; let n = 0, kept = 0;
for (const l of fs.readFileSync(f, 'utf8').split('\n')) {
  if (!l.trim()) continue; let g; try { g = JSON.parse(l); } catch { continue; } n++;
  if (!g.winner) continue;
  const faults = t => g[t].fl[FI.dn_fault].reduce((a, b) => a + b, 0);
  if (['A', 'B'].some(t => g[t].splits <= 3 && g[t].sonar === 0) || faults('A') + faults('B') >= 3) continue;
  kept++;
  for (const t of ['A', 'B']) teams.push({ grp: t === g.winner ? '상위권 승자' : '상위권 패자', g, t });
}
const pct = (a, b) => b ? Math.round(100 * a / b) + '%' : '–', f1 = x => Number.isFinite(x) ? x.toFixed(1) : '–', f2 = x => Number.isFinite(x) ? x.toFixed(2) : '–';
const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN;
const md = (h, rows) => ['| ' + h.join(' | ') + ' |', '|' + h.map((x, i) => i ? '---:' : '---').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');
// flows after t: [nat, ownSac, ownOther, enemy, cost, lossOff, lossPath]
const after = (lin, t, rounds) => { const c = lin.cp[t]; if (!c) return null; const e = c.eat; return [e[0], e[1], e[2] + e[3] + e[4] + e[5], e[6] + e[7] + e[8] + e[9] + e[10], c.cost, c.lossOff, c.lossPath]; };
const bins = x => { // per-bin flows [300,350), [350,400), [400,450), [450,end)
  const lin = x.g[x.t].lin; if (!lin) return null;
  const a = [300, 350, 400, 450].map(t => after(lin, t)); if (a.some(v => !v)) return null;
  return [0, 1, 2, 3].map(i => a[i].map((v, k) => v - (i < 3 ? a[i + 1][k] : 0)));
};
const out = [`<!-- generated ${new Date().toISOString()} by exp/endgame-king/ml_top.js -->`, `질량 장부 전체 캐시: ${n}판 읽음, 남김 ${kept}판(11:34 KST의 data/top 전부).`];
const full = x => x.g.kind === 'r500' && x.g.rounds === 500 && x.g[x.t].lin && x.g[x.t].lin.cp[300];
out.push('\n### M1 최종 왕 계보의 r300–499 흐름 (500라운드형, 500라운드까지 간 판, 팀-경기당; 질량 장부 전체 캐시)');
const r1 = [], r1b = [], r2 = [], r2b = [];
for (const grp of ['상위권 승자', '상위권 패자']) {
  const T = teams.filter(x => x.grp === grp && full(x)).map(x => ({ x, b: bins(x) })).filter(o => o.b);
  const s = k => mean(T.map(o => o.b.reduce((a, v) => a + v[k], 0)));
  r1.push([grp, T.length, f1(mean(T.map(o => o.x.g[o.x.t].lin.cp[300].Lt))), f1(s(0)), f1(s(1)), f1(s(2)), f1(s(3)), f1(-s(4)), f1(-s(5) - s(6)), f1(mean(T.map(o => o.x.g[o.x.t].lin.len)))]);
  r1b.push([grp, T.length, ...[0, 1, 2, 3].map(i => `${f1(mean(T.map(o => o.b[i][0])))} / ${f1(mean(T.map(o => o.b[i][1])))}`)]);
  const L = t => mean(T.map(o => t === 500 ? o.x.g[o.x.t].lin.len : o.x.g[o.x.t].lin.cp[t].Lt));
  r2.push([grp, T.length, f1(mean(T.map(o => o.x.g[o.x.t].st.king[30]))), ...[300, 350, 400, 450, 500].map(t => f1(L(t))), ...[300, 350, 400, 450].map(t => f2((L(t + 50) - L(t)) / 50)), f2((L(500) - L(300)) / 200),
    pct(T.filter(o => o.x.g[o.x.t].lin.cp[350].wasKing).length, T.length), pct(T.filter(o => o.x.g[o.x.t].lin.cp[400].wasKing).length, T.length), pct(T.filter(o => o.x.g[o.x.t].lin.cp[450].wasKing).length, T.length)]);
  const row = [grp]; for (const [a, b] of [[0, 10], [11, 20], [21, 30], [31, 999]]) { const U = T.filter(o => o.x.g[o.x.t].lin.cp[300].Lt >= a && o.x.g[o.x.t].lin.cp[300].Lt <= b); row.push(U.length ? `${f2(mean(U.map(o => (o.x.g[o.x.t].lin.len - o.x.g[o.x.t].lin.cp[300].Lt) / 200)))} (${U.length})` : '–'); } r2b.push(row);
}
out.push(md(['집단', '팀-경기', 'L300', '+ 자연', '+ 우리 희생', '+ 우리 다른 사망', '+ 적 사망', '− 질주', '− 분열', '= 끝 왕'], r1));
out.push('\n### M1b 50라운드마다 자연 / 우리 희생 (같은 판)');
out.push(md(['집단', '팀-경기', 'r300–349', 'r350–399', 'r400–449', 'r450–499'], r1b));
out.push('\n### M2 계보 길이와 라운드당 성장, 계보 = 팀 최장 (같은 판)');
out.push(md(['집단', '팀-경기', 'r300 팀 최장', 'L300', 'L350', 'L400', 'L450', '끝', '성장 r300–349', 'r350–399', 'r400–449', 'r450–499', 'r300–500', '계보 = 최장 r350', 'r400', 'r450'], r2));
out.push('\n### M2b L300 부류별 라운드당 성장');
out.push(md(['집단', 'L300 ≤10', '11–20', '21–30', '31+'], r2b));
// elimination maps: winners that survived past r300
out.push('\n### M3 전멸형 지도: 끝까지 산 팀의 최종 왕 계보, 판이 r300을 넘긴 경우 (흐름은 r300 뒤 합)');
const r3 = [];
for (const grp of ['상위권 승자', '상위권 패자']) for (const end of ['500라운드', '전멸로 끝남']) {
  const T = teams.filter(x => x.grp === grp && x.g.kind === 'elim' && x.g.rounds > 300 && x.g[x.t].lin && x.g[x.t].lin.cp[300] && (end === '500라운드' ? x.g.rounds === 500 : x.g.rounds < 500));
  if (T.length < 3) continue;
  const s = k => mean(T.map(x => after(x.g[x.t].lin, 300)[k]));
  r3.push([grp, end, T.length, f1(mean(T.map(x => x.g[x.t].lin.cp[300].Lt))), f1(s(0)), f1(s(1)), f1(s(2)), f1(s(3)), f1(-s(4) - s(5) - s(6)), f1(mean(T.map(x => x.g[x.t].lin.len)))]);
}
out.push(md(['집단', '끝', '팀-경기', 'L300', '+ 자연', '+ 우리 희생', '+ 우리 다른 사망', '+ 적 사망', '− 질주·분열', '= 끝 왕'], r3));
console.log(out.join('\n'));
