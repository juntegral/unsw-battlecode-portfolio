#!/usr/bin/env node
// 같은 키(상대:지도:진영:시드)로 기준 평가와 후보 평가를 짝지어 지도(판본)별·상대별로 비교한다.
// usage (저장소 루트에서): node exp/cand-pd10a/compare_pd.js <기준 라벨> <후보 라벨> [--by map|opp|all] [--maps a,b] [--md]
//   라벨은 exp/<라벨>/rows.jsonl. 여러 라벨을 +로 합칠 수 있다(예: cand-pd10-base+cand-pd10-base-px).
// 출력: 판 수, G 기준 → 후보, G 차이 [95%], 승 기준 → 후보, 승 차이 %p [95%], 생존 기준 → 후보, 생존 차이 %p [95%].
// 구간: 짝 차이의 평균 ± t(0.975, n−1)·SD/√n. 승·생존 차이도 짝 차이(−1/0/+1)로 같은 방식으로 잰다.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const [baseL, candL] = argv.slice(0, 2);   // 두 라벨이 먼저 온다
const readRows = label => {
  const m = new Map();
  for (const l of label.split('+')) {
    const f = path.join(ROOT, 'exp', l, 'rows.jsonl');
    for (const line of fs.readFileSync(f, 'utf8').trim().split('\n')) { if (!line) continue; const r = JSON.parse(line); if (r.G === undefined || m.has(r.key)) continue; m.set(r.key, r); }
  }
  return m;
};
const B = readRows(baseL), C = readRows(candL);
const mapsFilter = opt('maps') ? new Set(opt('maps').split(',')) : null;
let pairs = [...C.values()].filter(r => B.has(r.key) && (!mapsFilter || mapsFilter.has(r.map))).map(r => ({ key: r.key, map: r.map, opp: r.opp, b: B.get(r.key), c: r }));
// prisoners_dilemma_10 짝은 두 경기가 같은 진주 배치로 돌았을 때만 쓴다. 2026-09-30 04:00 KST(커밋 310dca9)에
// maps/variants/prisoners_dilemma_10.map이 서버 추정 배치로 바뀌어, 그 뒤 maps-pd 링크로 돌린 경기는 새 배치다.
// 배치는 리플레이의 (14,2) 칸 생성 간격으로 판정한다(옛 88칸 배치는 생성 칸, 새 76칸 배치는 생성 없음). 버린 짝 수를 알린다.
{
  const { load } = require(path.join(ROOT, 'tools/replay.js'));
  const layoutOf = (label, key) => {
    for (const l of label.split('+')) {
      const rp = path.join(ROOT, 'exp', l, 'games', key.replace(/:/g, '_'), 'game.replay');
      if (!fs.existsSync(rp)) continue;
      const M = load(rp).match.map, pr = M.pearlRespawn[2 * M.width + 14];
      return pr && pr.maxRounds > 0 ? 'old' : 'new';
    }
    return 'unknown';
  };
  const dropped = [];
  pairs = pairs.filter(p => {
    if (p.map !== 'prisoners_dilemma_10') return true;
    const lb = layoutOf(baseL, p.key), lc = layoutOf(candL, p.key);
    if (lb === lc && lb !== 'unknown') return true;
    dropped.push(`${p.key}(${lb}/${lc})`);
    return false;
  });
  if (dropped.length) console.error(`prisoners_dilemma_10: 배치가 다른 짝 ${dropped.length}개를 뺐다: ${dropped.join(' ')}`);
}
// t quantiles (0.975) for small n
const tq = n => { const T = { 1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26, 10: 2.23, 12: 2.18, 15: 2.13, 20: 2.09, 25: 2.06, 30: 2.04, 40: 2.02, 60: 2.00, 120: 1.98 }; const ks = Object.keys(T).map(Number).sort((a, b) => a - b); let q = 1.96; for (const k of ks) if (n <= k) { q = T[k]; break; } return q; };
const ci = d => { const n = d.length; if (!n) return [NaN, NaN, NaN]; const m = d.reduce((a, x) => a + x, 0) / n; if (n < 2) return [m, NaN, NaN]; const sd = Math.sqrt(d.reduce((a, x) => a + (x - m) ** 2, 0) / (n - 1)); const h = tq(n - 1) * sd / Math.sqrt(n); return [m, m - h, m + h]; };
const f = (x, d = 2) => Number.isFinite(x) ? (x >= 0 && d !== 0 ? '' : '') + x.toFixed(d) : '-';
const sg = (x, d = 2) => Number.isFinite(x) ? (x > 0 ? '+' : '') + x.toFixed(d) : '-';
function line(name, ps) {
  const n = ps.length; if (!n) return null;
  const gB = ps.reduce((a, p) => a + p.b.G, 0) / n, gC = ps.reduce((a, p) => a + p.c.G, 0) / n;
  const [dg, lo, hi] = ci(ps.map(p => p.c.G - p.b.G));
  const wB = ps.filter(p => p.b.won).length, wC = ps.filter(p => p.c.won).length;
  const [dw, wlo, whi] = ci(ps.map(p => (+p.c.won) - (+p.b.won)));
  const aB = ps.filter(p => p.b.alive).length, aC = ps.filter(p => p.c.alive).length;
  const [da, alo, ahi] = ci(ps.map(p => (+p.c.alive) - (+p.b.alive)));
  const same = ps.filter(p => p.b.G === p.c.G && p.b.won === p.c.won && p.b.endReason === p.c.endReason && p.b.theirLongest === p.c.theirLongest).length;
  return [name, n, `${f(gB)} → ${f(gC)}`, `${sg(dg)} [${sg(lo)}, ${sg(hi)}]`, `${wB} → ${wC}`, `${sg(100 * dw, 1)} [${sg(100 * wlo, 1)}, ${sg(100 * whi, 1)}]`, `${aB} → ${aC}`, `${sg(100 * da, 1)} [${sg(100 * alo, 1)}, ${sg(100 * ahi, 1)}]`, same];
}
const by = opt('by', 'map');
const groups = by === 'opp' ? [...new Set(pairs.map(p => p.opp))] : by === 'all' ? ['전체'] : [...new Set(pairs.map(p => p.map))].sort();
const rows = [];
for (const g of groups) rows.push(line(g, by === 'opp' ? pairs.filter(p => p.opp === g) : by === 'all' ? pairs : pairs.filter(p => p.map === g)));
if (by !== 'all') rows.push(line('전체', pairs));
const head = ['범위', '판', 'G 기준 → 후보', 'G 차이 [95%]', '승', '승 차이 %p [95%]', '생존', '생존 차이 %p [95%]', '결과 같은 판'];
if (argv.includes('--md')) { console.log('| ' + head.join(' | ') + ' |'); console.log('|' + head.map((h, i) => i === 0 ? '---' : '---:').join('|') + '|'); for (const r of rows.filter(Boolean)) console.log('| ' + r.join(' | ') + ' |'); }
else for (const r of rows.filter(Boolean)) console.log(r.join('  '));
