#!/usr/bin/env node
// Confound check for elite.js: is the top decile's early conversion a team style or a game-level difference?
// For each elite team with >= 8 top-decile and >= 8 median-band Portals team-games, compare its own top-decile games with its own
// median-band games (king r300 / r350 / r400, own sacrifice deaths r250-299 and r300-349, units r300). Reads the same cache.
'use strict';
const fs = require('fs'), path = require('path'), readline = require('readline');
const ROOT = path.resolve(__dirname, '../../../..');
const { FI } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const q = (xs, p) => { const a = xs.slice().sort((u, v) => u - v); if (!a.length) return null; const i = (a.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return a[lo] + (a[hi] - a[lo]) * (i - lo); };
const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : null;
const sb = (arr, a, b) => { let s = 0; for (let i = a; i <= b; i++) s += arr[i]; return s; };
(async () => {
  const rows = [];
  const rl = readline.createInterface({ input: fs.createReadStream(path.join(ROOT, '.cache/mass-ledger/top-sample.jsonl')), crlfDelay: Infinity });
  for await (const l of rl) {
    if (!l.includes('"map":"Portals"')) continue;
    const g = JSON.parse(l); if (g.map !== 'Portals') continue;
    const st = tm => g.rounds >= 100 && g[tm].sonar === 0 && g[tm].splits <= 3;
    if (st('A') || st('B')) continue;
    for (const tm of ['A', 'B']) {
      const T = g[tm];
      rows.push({ name: tm === 'A' ? g.teamA : g.teamB, k500: T.st.king[50], k300: T.st.king[30], k350: T.st.king[35], k400: T.st.king[40], u300: T.st.units[30],
        sac250: sb(T.fl[FI.dn_sac], 25, 29), sac300: sb(T.fl[FI.dn_sac], 30, 34), kd: sb(T.fl[FI.kd_n], 0, 49) });
    }
  }
  const ks = rows.map(r => r.k500), P90 = q(ks, 0.9), P40 = q(ks, 0.4), P60 = q(ks, 0.6);
  const top = rows.filter(r => r.k500 >= P90), med = rows.filter(r => r.k500 >= P40 && r.k500 <= P60);
  const cnt = {}; for (const r of top) cnt[r.name] = (cnt[r.name] || 0) + 1;
  console.log('top-decile composition (team-games):', Object.entries(cnt).sort((a, b) => b[1] - a[1]).slice(0, 12).map(([n, c]) => `${n} ${c}`).join(', '), `(of ${top.length})`);
  console.log('\nwithin-team: team | N top / N median | king r300 / r350 / r400 (median, top vs median) | sac deaths r250-299, r300-349 (mean) | units r300 | king deaths');
  const names = [...new Set(rows.map(r => r.name))];
  const pooled = { t: [], m: [] };
  for (const n of names) {
    const t = top.filter(r => r.name === n), m = med.filter(r => r.name === n);
    if (t.length < 8 || m.length < 8) continue;
    const f = (a, k) => q(a.map(r => r[k]), 0.5), mm = (a, k) => mean(a.map(r => r[k]));
    console.log(`${n} | ${t.length} / ${m.length} | ${f(t, 'k300')} vs ${f(m, 'k300')} / ${f(t, 'k350')} vs ${f(m, 'k350')} / ${f(t, 'k400')} vs ${f(m, 'k400')} | ${mm(t, 'sac250').toFixed(1)} vs ${mm(m, 'sac250').toFixed(1)}, ${mm(t, 'sac300').toFixed(1)} vs ${mm(m, 'sac300').toFixed(1)} | ${mm(t, 'u300').toFixed(1)} vs ${mm(m, 'u300').toFixed(1)} | ${mm(t, 'kd').toFixed(2)} vs ${mm(m, 'kd').toFixed(2)}`);
    pooled.t.push(...t); pooled.m.push(...m);
  }
  const f = (a, k) => q(a.map(r => r[k]), 0.5), mm = (a, k) => mean(a.map(r => r[k]));
  console.log(`POOLED (teams above) | ${pooled.t.length} / ${pooled.m.length} | ${f(pooled.t, 'k300')} vs ${f(pooled.m, 'k300')} / ${f(pooled.t, 'k350')} vs ${f(pooled.m, 'k350')} / ${f(pooled.t, 'k400')} vs ${f(pooled.m, 'k400')} | ${mm(pooled.t, 'sac250').toFixed(1)} vs ${mm(pooled.m, 'sac250').toFixed(1)}, ${mm(pooled.t, 'sac300').toFixed(1)} vs ${mm(pooled.m, 'sac300').toFixed(1)} | ${mm(pooled.t, 'u300').toFixed(1)} vs ${mm(pooled.m, 'u300').toFixed(1)} | ${mm(pooled.t, 'kd').toFixed(2)} vs ${mm(pooled.m, 'kd').toFixed(2)}`);
})();
