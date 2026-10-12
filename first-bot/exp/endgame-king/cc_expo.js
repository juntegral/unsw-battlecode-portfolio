#!/usr/bin/env node
// Cross-check of the king's exposure on a larger top population: the conversion-chain cache's king-choice snapshots
// (.cache/conv-chain/top*.jsonl: every 500-round top game up to 16:46 KST) give, at the first turn of r300/350/400/450, every
// dragon's torus Manhattan distance to the nearest enemy head (eD) and whether it is the final-king line member.
// usage: node exp/endgame-king/cc_expo.js > exp/endgame-king/cc-expo.md
'use strict';
const fs = require('fs'), path = require('path');
const C = path.join(path.resolve(__dirname, '..', '..'), '.cache', 'conv-chain');
const seen = new Set(); const acc = {};
const add = (grp, map, t, eD) => { for (const m of [map, 'all', map === 'Portals' ? 'Portals' : 'noPortals']) { const k = grp + '|' + m + '|' + t; const a = acc[k] || (acc[k] = [0, 0, 0, 0]); a[0]++; if (eD <= 3) a[1]++; if (eD <= 6) a[2]++; a[3] += Math.min(eD, 30); } };
for (const f of fs.readdirSync(C).filter(f => f.endsWith('.jsonl'))) {
  for (const l of fs.readFileSync(path.join(C, f), 'utf8').split('\n')) {
    if (!l.trim()) continue; const g = JSON.parse(l); if (seen.has(g.key)) continue; seen.add(g.key);
    if (g.rounds !== 500 || !g.winner) continue;
    for (const t of ['A', 'B']) {
      const grp = g.src === 'top' ? (t === g.winner ? 'W' : 'L') : (t === g.us ? 'ours:' + (g.set || '').replace('cand-', '').replace('-online', '') : 'X');
      const kc = g[t] && g[t].kc; if (!kc) continue;
      for (const [cp, rows] of Object.entries(kc)) { const r = rows.find(x => x[10] === 1); if (r) add(grp, g.map, cp, r[2]); }
    }
  }
}
const out = ['| group | maps | r300 ≤3/≤6 (n) | r350 | r400 | r450 |', '|---|---|---:|---:|---:|---:|'];
const grps = [...new Set(Object.keys(acc).map(k => k.split('|')[0]))].sort();
for (const g of grps) for (const m of ['all', 'noPortals', 'Portals', 'Autarky', 'Schooltime', 'Slithery Fight', 'Trauma']) {
  const cells = ['300', '350', '400', '450'].map(t => { const a = acc[g + '|' + m + '|' + t]; return a ? `${Math.round(100 * a[1] / a[0])}% / ${Math.round(100 * a[2] / a[0])}% (${a[0]})` : '–'; });
  if (cells.every(c => c === '–')) continue;
  out.push(`| ${g} | ${m} | ${cells.join(' | ')} |`);
}
console.log(`games ${seen.size}\n` + out.join('\n'));
