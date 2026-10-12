#!/usr/bin/env node
// Stage 3 selection (rules fixed before reading any replay; research/observations/intake-gap.md section 12):
//   3a head deficit: on each of the two 500-round maps with the largest per-game gap in the primary sample (stack5-8), the game whose
//      r100 unit gap (opponent - us) is the median of that map's games (ties: lowest FNV-1a hash of the key). Film: territory film
//      'game' mode for our team at r10, r50, r100, and r300, r350, r400 (late collapse).
//   3b contest: contest-loss pearls of stack5-8 (our designated head nearer at spawn, the opponent ate it) with the designated head
//      within 3 steps and the pearl in its 7x7 view at spawn; per loss class (away, raced, stalled, died) the 2 with the lowest
//      FNV-1a hash of "key|spawn round|tile". Film: exp/intake-gap/film_contest.js.
// usage: node exp/intake-gap/picks.js  (reads .cache/intake-gap/numbers.json and exp/intake-gap/contest-examples.json)
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const fnv = s => { let x = 2166136261; for (let i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 16777619); } return x >>> 0; };
const R = JSON.parse(fs.readFileSync(path.join(ROOT, '.cache', 'intake-gap', 'numbers.json'), 'utf8'));
const prim = R.perGame.filter(g => /stack[5-8]/.test(g.set));
const byMap = {}; for (const g of prim) if (g.kind === 'r500') (byMap[g.map] = byMap[g.map] || []).push(g);
const mapGap = Object.entries(byMap).map(([m, gs]) => [m, gs.reduce((s, g) => s + g.gap, 0) / gs.length]).sort((a, b) => b[1] - a[1]);
console.log('500-round maps by mean gap (stack5-8):', mapGap.map(([m, v]) => `${m} ${v.toFixed(0)}`).join(', '));
for (const [m] of mapGap.slice(0, 2)) {
  const gs = byMap[m].map(g => ({ ...g, ug: g.oppUnits100 - g.units100 })).sort((a, b) => a.ug - b.ug || fnv(a.key) - fnv(b.key));
  const med = gs[Math.floor((gs.length - 1) / 2)];
  console.log(`3a ${m}: median r100 unit gap ${med.ug} -> ${med.key} (opp ${med.opp}, variant ${med.variant}; our units r100 ${med.units100}, theirs ${med.oppUnits100}; intake ${med.Iu} vs ${med.Io})`);
  console.log(`   node exp/territory-analysis/film.js game ${med.key} ${'<our side>'} --snaps 10,50,100,300,350,400`);
}
const exF = path.join(__dirname, 'contest-examples.json');
if (fs.existsSync(exF)) {
  const ex = JSON.parse(fs.readFileSync(exF, 'utf8')).filter(e => e.dU <= 3 && e.view === 1);
  for (const cls of ['away', 'raced', 'stalled', 'died']) {
    const xs = ex.filter(e => e.cls === cls).sort((a, b) => fnv(`${a.key}|${a.r0}|${a.k}`) - fnv(`${b.key}|${b.r0}|${b.k}`)).slice(0, 2);
    for (const e of xs) console.log(`3b ${cls}: ${e.key} ${e.map} pearl tile ${e.k} spawn r${e.r0} eaten r${e.eatR}; our #${e.hid} L${e.hlen} d${e.dU} vs their d${e.dO}; label majority ${e.top}; eater sprint ${e.eSpr}`);
  }
}
