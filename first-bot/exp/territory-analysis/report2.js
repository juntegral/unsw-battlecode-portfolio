#!/usr/bin/env node
// report2.js — tables from pass2 (split context, merge2's split rules, split children's first 30 rounds).
// usage (repository root): node exp/territory-analysis/report2.js [--out exp/territory-analysis/report2-all]
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), readline = require('readline');
const ROOT = path.resolve(__dirname, '..', '..');
const S = require('./summarise.js');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const OUT = path.resolve(ROOT, opt('out', 'exp/territory-analysis/report2-all'));
const CACHE = path.join(__dirname, 'cache');
const kindOf = m => S.ELIM.includes(m) ? 'elim' : S.R500.includes(m) ? 'r500' : 'other';
const PHN = ['r0-99', 'r100-249', 'r250-349', 'r350-449', 'r450+'];
async function each(file, fn) { if (!fs.existsSync(file)) return; const rl = readline.createInterface({ input: fs.createReadStream(file).pipe(zlib.createGunzip()), crlfDelay: Infinity }); for await (const l of rl) { if (l.trim()) fn(JSON.parse(l)); } }
(async () => {
  // exclusions as the main report: inactive / faulty top games (read from the main cache)
  const bad = new Set(), keep = new Set();
  await S.forEachGame(path.join(CACHE, 'top-all.jsonl.gz'), g => { const inactive = T => T.splits <= 3 && T.sonar === 0; if (inactive(g.A) || inactive(g.B) || g.A.faults >= 3 || g.B.faults >= 3 || !g.winner) bad.add(g.key); else keep.add(g.key); });
  const agg = {}; const nG = {};
  const A = (grp, kind) => { const k = grp + '|' + kind; if (!agg[k]) agg[k] = { n: 0, splits: [0, 1, 2, 3, 4].map(() => [0, 1, 2].map(() => [0, 0])), child: [0, 1, 2].map(() => [0, 0, 0]), gate2: [0, 1, 2, 3, 4].map(() => [0, 0, 0, 0, 0]), labels: [0, 0, 0, 0, 0], esc: [0, 0, 0, 0, 0], child30: [0, 1, 2].map(() => [0, 0, 0, 0, 0, 0]) }; return agg[k]; };
  const addInto = (t, x) => { t.n++; for (let p = 0; p < 5; p++) for (let w = 0; w < 3; w++) for (let v = 0; v < 2; v++) t.splits[p][w][v] += x.splits[p][w][v];
    for (let w = 0; w < 3; w++) for (let c = 0; c < 3; c++) t.child[w][c] += x.child[w][c];
    for (let p = 0; p < 5; p++) for (let j = 0; j < 5; j++) t.gate2[p][j] += x.gate2[p][j];
    for (let p = 0; p < 5; p++) { t.labels[p] += x.labels[p]; t.esc[p] += x.esc[p]; }
    for (let w = 0; w < 3; w++) for (let j = 0; j < 6; j++) t.child30[w][j] += x.child30[w][j]; };
  await each(path.join(CACHE, 'pass2-top-all.jsonl.gz'), g => {
    if (!keep.has(g.key)) return; nG.top = (nG.top || 0) + 1;
    const kind = kindOf(g.map);
    for (const [ti, tm] of [[0, 'A'], [1, 'B']]) addInto(A(tm === g.winner ? 'TW' : 'TL', kind), g.T[ti]);
  });
  for (const set of Object.keys(S.SETS)) await each(path.join(CACHE, 'pass2-online-' + set + '.jsonl.gz'), g => {
    nG.online = (nG.online || 0) + 1;
    const kind = kindOf(g.map), us = g.us === 'A' ? 0 : 1, bot = S.SETS[set];
    addInto(A(bot, kind), g.T[us]); addInto(A('X-' + bot, kind), g.T[1 - us]); addInto(A('X', kind), g.T[1 - us]);
  });
  const L = [], P = (...a) => L.push(a.join(''));
  const pc = (a, b) => b ? (100 * a / b).toFixed(0) + '%' : '–';
  const f1 = x => Number.isFinite(x) ? x.toFixed(1) : '–';
  const table = (head, rows) => { P('| ' + head.join(' | ') + ' |'); P('|' + head.map((h, i) => i ? '---:' : '---').join('|') + '|'); for (const r of rows) P('| ' + r.join(' | ') + ' |'); P(''); };
  const GR = ['TW', 'TL', ...S.BOTS, 'X', 'X-merge2'];
  P('# 분열의 맥락 (exp/territory-analysis/pass2.js → report2.js)', '');
  P(`- 경기: 상위권 ${nG.top || 0}판(제외 뒤), 온라인 ${nG.online || 0}판.`, '');
  for (const kind of ['r500', 'elim']) {
    P(`## ${kind === 'r500' ? '500라운드형' : '전멸형'}(모든 판): 판당 분열 수, 어디서, 적 머리가 보일 때`, '');
    const rows = [];
    for (const g of GR) {
      const t = agg[g + '|' + kind]; if (!t || !t.n) continue;
      const tot = t.splits.flat(2).reduce((a, b) => a + b, 0);
      const byPh = t.splits.map(p => p.flat().reduce((a, b) => a + b, 0) / t.n);
      const where = [0, 1, 2].map(w => t.splits.reduce((a, p) => a + p[w][0] + p[w][1], 0));
      const view = t.splits.reduce((a, p) => a + p[0][1] + p[1][1] + p[2][1], 0);
      const viewOwn = t.splits.reduce((a, p) => a + p[0][1], 0), own = where[0];
      const cl = [0, 1, 2].map(c => t.child.reduce((a, w) => a + w[c], 0));
      rows.push([g, t.n, f1(tot / t.n), byPh.map(v => f1(v)).join(' / '), `${pc(where[0], tot)} / ${pc(where[1], tot)} / ${pc(where[2], tot)}`, pc(view, tot), pc(viewOwn, own), cl.map(v => pc(v, tot)).join(' / ')]);
    }
    table(['집단', 'N(팀·경기)', '분열/판', '국면별 분열/판 (' + PHN.join(', ') + ')', '분열 위치: 우리 / 중립 / 적 영토', '적 머리가 7×7 안에 보일 때 분열', '그중 우리 영토 안 분열', '새끼 길이 2 / 3 / 4+'], rows);
    P(`### ${kind === 'r500' ? '500라운드형' : '전멸형'}: r300 전에 태어난 새끼의 첫 30라운드 (태어난 곳별)`, '');
    const rows2 = [];
    for (const g of GR) {
      const t = agg[g + '|' + kind]; if (!t || !t.n) continue;
      rows2.push([g, t.n, ...[0, 2].map(w => { const a = t.child30[w]; return a[0] ? `${f1(a[0] / t.n)} · 생존 ${pc(a[1], a[0])} · 1개 이상 ${pc(a[5], a[0])} · ${f1((a[2] + a[3] + a[4]) / a[0])}개(우리 ${f1(a[2] / a[0])}, 적 ${f1(a[4] / a[0])})` : '–'; })]);
    }
    table(['집단', 'N', '우리 영토에서 태어난 새끼/판 · 30라운드 생존 · 자연 진주 1개 이상 · 새끼당 자연 진주', '적 영토에서 태어난 새끼'], rows2);
  }
  P('## merge2의 분열 규칙: r340 전 드래곤·턴이 어느 규칙에 막히나 (plan.cpp wantSplit)', '');
  P('- 상한 = 팀 드래곤 5마리 이상. 왕 = 팀의 최장(2마리 이상일 때 왕은 보험 분열만). 짧음 = 길이 < 8(혼자일 때 < 5). 적 보임 = 7×7 안에 적 머리. 열림 = 이 넷에 안 걸림(다른 조건: 꼬리 주변, 먹을 진주, 안전 등은 봇 안에서 따로 본다).', '');
  for (const kind of ['r500', 'elim']) {
    const rows = [];
    for (const g of ['merge2', 'g4r4', 'swarm8', 'px9d']) {
      const t = agg[g + '|' + kind]; if (!t || !t.n) continue;
      for (let p = 0; p < 3; p++) { const a = t.gate2[p], tot = a.reduce((x, y) => x + y, 0); if (!tot) continue; rows.push([g, PHN[p], t.n, f1(tot / t.n), ...a.map(v => pc(v, tot)), f1(t.labels[p] / t.n), f1(t.esc[p] / t.n)]); }
    }
    P(`### ${kind === 'r500' ? '500라운드형' : '전멸형'}`, '');
    table(['봇', '국면', 'N', '드래곤·턴/판', '상한', '왕', '짧음', '적 보임', '열림', '정책 분열 표식/판', '탈출 분열 표식/판'], rows);
  }
  fs.writeFileSync(OUT + '.md', L.join('\n') + '\n');
  fs.writeFileSync(OUT + '.json', JSON.stringify({ nG, agg }, null, 1));
  console.log(`wrote ${path.relative(ROOT, OUT)}.md/.json`, nG);
})().catch(e => { console.error(e); process.exit(1); });
