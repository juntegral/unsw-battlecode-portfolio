#!/usr/bin/env node
// W7 hypothesis (b): is our reproduction gap a split-gate gap or a mass gap? For the small-map study's Trophy population (exp/small/population.json:
// our online games and the top teams' winners and losers), per round bin: the share of a team's dragon-turns at length >= 4 (a split is legal),
// splits per such turn, splits per game, and natural pearls eaten per dragon-turn (tileChange pearl removals by the mover; drops included).
// usage: node exp/w7/lenshare.js [--src online,top] [--limit N]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const P = JSON.parse(fs.readFileSync(path.join(ROOT, 'exp', 'small', 'population.json'), 'utf8'));
const srcs = new Set(opt('--src', 'online,top').split(',')), limit = +opt('--limit', 1e9);
const BINS = [[0, 24], [25, 49], [50, 99], [100, 199]];
const agg = {};
const G = l => (agg[l] = agg[l] || { games: 0, bins: BINS.map(() => ({ turns: 0, l4: 0, l3: 0, splits: 0, splitsL4: 0, eats: 0 })) });
let n = 0;
for (const t of P.tasks) {
  if (!srcs.has(t.src) || (t.map || t.mapName) !== 'Trophy' || n >= limit) continue;
  n++;
  const lab = {};
  if (t.src === 'online') lab[t.us] = /^v1-w/.test(t.set) ? 'online v1' : 'online W0-W12';
  else { const w = (t.winner || '').toUpperCase(); lab[w] = `${t.src} winner`; lab[w === 'A' ? 'B' : 'A'] = `${t.src} loser`; }
  for (const l of Object.values(lab)) G(l).games++;
  try {
    const R = load(t.file);
    const bin = r => BINS.findIndex(([a, b]) => r >= a && r <= b);
    perGame(R, { map: 'Trophy', variant: 'a' }, {
      turn(d, round) { const l = lab[d.team]; const bi = bin(round); if (!l || bi < 0) return; const B = agg[l].bins[bi]; B.turns++; if (d.body.length >= 4) B.l4++; else if (d.body.length === 3) B.l3++; },
      split(p, ch, e, round) { const l = lab[p.team]; const bi = bin(round); if (!l || bi < 0) return; const B = agg[l].bins[bi]; B.splits++; if (p.body.length + ch.body.length >= 4) B.splitsL4++; },
      eat(d, k, o, round) { const l = lab[d.team]; const bi = bin(round); if (!l || bi < 0) return; agg[l].bins[bi].eats++; },
    });
  } catch (e) { console.error('skip', t.key, String(e).slice(0, 100)); }
  if (n % 200 === 0) console.error('progress', n);
}
const pc = (a, b) => b ? (100 * a / b).toFixed(1) + '%' : '-';
for (const [l, A] of Object.entries(agg).sort()) {
  console.log(`== ${l}: ${A.games} games`);
  A.bins.forEach((B, i) => console.log(`  r${BINS[i][0]}-${BINS[i][1]}: dragon-turns ${B.turns}; at L>=4 ${pc(B.l4, B.turns)}, L3 ${pc(B.l3, B.turns)}; splits ${(B.splits / A.games).toFixed(1)}/game = ${pc(B.splits, B.l4)} of L>=4 turns; pearls eaten per dragon-turn ${(B.eats / Math.max(1, B.turns)).toFixed(3)} (${(B.eats / A.games).toFixed(1)}/game)`));
}
