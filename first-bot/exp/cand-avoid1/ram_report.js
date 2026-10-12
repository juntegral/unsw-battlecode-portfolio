#!/usr/bin/env node
'use strict';
// ram_report.js — markdown tables from ram_audit.js outputs.
// usage: node exp/cand-avoid1/ram_report.js <label>=<audit.json> [<label>=<audit.json> ...] [--filter-opp archetype_hunter]
//   Each input is one data set (e.g. base-hunter=..., top=..., mid=...). Prints: cases per game, attacker features,
//   classes, the bot's own view, and the approach over our last four decisions.
const fs = require('fs');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const fOpp = opt('--filter-opp', null);
const sets = argv.filter(a => a.includes('=') && !a.startsWith('--')).map(a => { const [k, f] = a.split('='); return [k, JSON.parse(fs.readFileSync(f))]; });
const pct = (n, d) => d ? (100 * n / d).toFixed(0) + '%' : '-';
const table = (head, rows) => ['| ' + head.join(' | ') + ' |', '|' + head.map(() => '---').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');
const man = (W, H, a, b) => { let dx = Math.abs(a % W - b % W), dy = Math.abs(((a / W) | 0) - ((b / W) | 0)); dx = Math.min(dx, W - dx); dy = Math.min(dy, H - dy); return dx + dy; };

const data = sets.map(([k, r]) => {
  const games = fOpp ? r.games.filter(g => g.opp === fOpp) : r.games;
  const keys = new Set(games.map(g => g.game));
  return [k, games, r.cases.filter(c => keys.has(c.game))];
});

const out = [];
out.push('### 1. 박힌 길이 6 이상 사망과 들이받은 적');
out.push(table(['자료', '판', '사망', '판당', '적 길이 ≤3', '적 2칸+ 질주', '적이 분열로 태어남', '결정 때 7x7 안(위치 앎)', '결정 때 체비쇼프 1 / 2 / 3'],
  data.map(([k, g, C]) => {
    const known = C.filter(c => c.cheb != null);
    return [k, g.length, C.length, (C.length / g.length).toFixed(2), pct(C.filter(c => c.attLen <= 3).length, C.filter(c => c.attLen != null).length),
      pct(C.filter(c => c.attSteps >= 2).length, C.filter(c => c.attSteps != null).length), pct(C.filter(c => c.attFromSplit).length, C.filter(c => c.attFromSplit != null).length),
      `${pct(known.filter(c => c.cheb <= 3).length, known.length)} (${known.filter(c => c.cheb <= 3).length}/${known.length})`,
      [1, 2, 3].map(d => known.filter(c => c.cheb === d).length).join(' / ')];
  })));
out.push('');
const CLS = ['walkedIn', 'stayedIn', 'sprintOnly', 'cornered', 'unseen', 'newChild', 'noSnapshot'];
out.push('### 2. 분류 (우리 마지막 결정 때, 보이는 적 머리의 실제 도달 범위 기준)');
out.push(table(['자료', '사망', ...CLS], data.map(([k, g, C]) => [k, C.length, ...CLS.map(c => `${C.filter(x => x.cls === c).length} (${pct(C.filter(x => x.cls === c).length, C.length)})`)])));
out.push('');
out.push('### 3. 봇 자신의 판단 (적이 보였던 경우)');
out.push(table(['자료', '보임', '고른 칸을 봇 위협 지도가 표시', '한 걸음 수가 모두 표시됨', '고른 수의 값 중앙값', '진주 먹는 수', '모드: 보통 / 모이기 / 마지막 30라운드 / 기타', '적 길이 추정: 정확 / 과대 / 과소'],
  data.map(([k, g, C]) => {
    const V = C.filter(c => c.bot && c.bot.flagsChosen != null);
    const vs = C.filter(c => c.v != null).map(c => c.v).sort((a, b) => a - b);
    const est = C.filter(c => c.bot && c.bot.est != null);
    return [k, V.length, pct(V.filter(c => c.bot.flagsChosen).length, V.length), pct(V.filter(c => c.bot.flaggedAll).length, V.length),
      vs.length ? vs[vs.length >> 1].toFixed(1) : '-', pct(C.filter(c => c.ate > 0).length, C.filter(c => c.ate != null).length),
      ['normal', 'gather', 'late'].map(m => C.filter(c => c.mode === m).length).join(' / ') + ' / ' + C.filter(c => c.mode && !['normal', 'gather', 'late'].includes(c.mode)).length,
      ['exact', 'over', 'under'].map(t => est.filter(c => t === 'exact' ? c.bot.est === c.bot.true : t === 'over' ? c.bot.est > c.bot.true : c.bot.est < c.bot.true).length).join(' / ')];
  })));
out.push('');
out.push('### 4. 다가감: 마지막 네 결정에서 공격자까지 체비쇼프 거리와 우리 한 걸음 선택');
const approach = C => {
  const t = { back: {}, choice: {} };
  for (const c of C) {
    const h = c.hist; if (!h) continue;
    for (let k = Math.max(0, h.length - 4); k < h.length; k++) {
      const a = h[k], b = h.length - k;
      const cb = a.attCheb == null ? '>6' : a.attCheb; t.back[b] = t.back[b] || {}; t.back[b][cb] = (t.back[b][cb] || 0) + 1;
      if (a.attHead == null || !a.legal || !a.act || !/^[NESW]/.test(a.act)) continue;
      const ds = a.legal.map(([d, u]) => ({ d, dist: man(c.W, c.H, u, a.attHead) })), mine = ds.find(x => x.d === a.act[0]); if (!mine) continue;
      const mx = Math.max(...ds.map(x => x.dist)), mn = Math.min(...ds.map(x => x.dist));
      const cat = ds.length === 1 ? 'only1' : mx === mn ? 'equal' : mine.dist === mn ? 'closer' : mine.dist === mx ? 'farther' : 'middle';
      t.choice[b] = t.choice[b] || {}; t.choice[b][cat] = (t.choice[b][cat] || 0) + 1;
    }
  }
  return t;
};
const rowsA = [];
for (const [k, g, C] of data) {
  const t = approach(C);
  for (let b = 4; b >= 1; b--) {
    const bk = t.back[b] || {}, ch = t.choice[b] || {};
    rowsA.push([k, '−' + b, ['1', '2', '3'].map(x => bk[x] || 0).join(' / '), (bk['4'] || 0) + (bk['5'] || 0) + (bk['6'] || 0), bk['>6'] || 0,
      ch.only1 || 0, ch.closer || 0, ch.farther || 0, (ch.equal || 0) + (ch.middle || 0)]);
  }
}
out.push(table(['자료', '결정', '체비쇼프 1 / 2 / 3', '4–6', '>6 또는 없음', '한 걸음 수 1개뿐', '가장 가까워지는 수', '가장 멀어지는 수', '같음·중간'], rowsA));
out.push('');
out.push('### 5. 상대·지도별 판당 박힌 L≥6 사망');
for (const [k, g, C] of data) {
  const by = f => { const m = new Map(); for (const x of g) { const kk = f(x); if (!m.has(kk)) m.set(kk, { n: 0, c: 0 }); m.get(kk).n++; } for (const c of C) { const x = g.find(q => q.game === c.game); const kk = f(x); m.get(kk).c++; } return [...m.entries()].sort((a, b) => b[1].c / b[1].n - a[1].c / a[1].n); };
  out.push(`- ${k} 상대별: ` + by(x => x.oppName ? x.opp + ' ' + x.oppName : x.opp).map(([kk, v]) => `${kk} ${(v.c / v.n).toFixed(2)} (${v.c}/${v.n})`).join(', '));
  out.push(`- ${k} 지도별: ` + by(x => x.map).map(([kk, v]) => `${kk} ${(v.c / v.n).toFixed(2)} (${v.c}/${v.n})`).join(', '));
}
console.log(out.join('\n'));
