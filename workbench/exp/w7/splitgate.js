#!/usr/bin/env node
// W7 hypothesis (b) groundwork (coordinator 15:15: "why do we split a quarter as often as elite winners on Trophy?"): over our games, every turn of
// ours by the indicator: length (" L<n>" or the split label's L), whether the turn split, and the split gate tags of the swarm engine (plan.cpp
// decideImpl: " sxx" / " srx" = the explosion / re-split wanted a split but the safety check stopped it (a pearl on the first step, a threatened
// tile on the chosen path, safety <= -1, or an enemy head within 2 of ours); " sxc" / " src" = the child's spot failed; " srn" = no service deficit)
// and of FORTRESS (" sx" alone = the split-tail rule stopped a policy split). Per round bin: turns at L >= 4 (a split is legal), splits, and why
// the others did not split; units (our dragons at the round's start) against the row's head curve when known.
// usage: node exp/w7/splitgate.js --population [--src online] [--sets cand-merge2-online,...]  |  --dirs <setDir>,...  [--map Trophy]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const MAP = opt('--map', 'Trophy');
const tasks = [];
if (args.includes('--population')) {
  const P = JSON.parse(fs.readFileSync(path.join(ROOT, 'exp', 'small', 'population.json'), 'utf8'));
  const srcs = new Set(opt('--src', 'online').split(',')), sets = opt('--sets') ? new Set(opt('--sets').split(',')) : null;
  for (const t of P.tasks) if (srcs.has(t.src) && (!sets || sets.has(t.set)) && (t.map || t.mapName) === MAP) tasks.push({ file: t.file, us: t.us, group: t.set && /^v1-w/.test(t.set) ? 'online v1' : 'online W0-W12' });
} else {
  for (const d of opt('--dirs', '').split(',').filter(Boolean)) {
    const rows = fs.readFileSync(path.join(ROOT, d, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => r.G !== undefined && !r.error && r.map.toLowerCase() === MAP.toLowerCase());
    for (const r of rows) tasks.push({ file: path.join(ROOT, d, 'games', r.key.replace(/:/g, '_'), 'game.replay'), us: r.side, group: path.basename(d) });
  }
}
const BINS = [[0, 24], [25, 49], [50, 99], [100, 199], [200, 499]];
const agg = {};
for (const t of tasks) {
  const R = load(t.file);
  const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
  const G = agg[t.group] = agg[t.group] || { games: 0, bins: BINS.map(() => ({ turns: 0, l4: 0, split: 0, sxx: 0, srx: 0, sxc: 0, srn: 0, tailx: 0, trade: 0, none: 0, units: 0, unitN: 0, engines: {} })) };
  G.games++;
  let round = 0; const alive = new Set(R.match.map.initialDragons.filter(d => d.team === t.us).map(d => d.id)); let lastUnitsRound = -1;
  for (const e of R.events) {
    if (e.type === 'roundStart') round = e.round;
    else if (e.type === 'dragonSplit') { team.set(e.childId, e.team); if (e.team === t.us) alive.add(e.childId); }
    else if (e.type === 'dragonDeath') alive.delete(e.id);
    else if (e.type === 'dragonIndicator' && team.get(e.id) === t.us) {
      const bi = BINS.findIndex(([a, b]) => round >= a && round <= b); if (bi < 0) continue;
      const B = G.bins[bi], s = e.text || '';
      if (round !== lastUnitsRound) { lastUnitsRound = round; B.units += alive.size; B.unitN++; }
      B.turns++;
      const eng = (/ E=([A-Z])$/.exec(s) || [, '?'])[1]; B.engines[eng] = (B.engines[eng] || 0) + 1;
      const split = /^(c|l)?split\d+/.test(s);
      const Lm = /(?:^| )L(\d+)/.exec(s); const L = Lm ? +Lm[1] : 0;
      if (split) { B.l4++; B.split++; continue; }
      if (L < 4) continue;
      B.l4++;
      if (/ sxx(?= |$)/.test(s)) B.sxx++;
      else if (/ srx(?= |$)/.test(s)) B.srx++;
      else if (/ (sxc|src)(?= |$)/.test(s)) B.sxc++;
      else if (/ srn(?= |$)/.test(s)) B.srn++;
      else if (/ sx(?= |$)/.test(s)) B.tailx++;
      else if (/ TRADE(?= |$)/.test(s)) B.trade++;
      else B.none++;
    }
  }
}
const pc = (a, b) => b ? (100 * a / b).toFixed(1) + '%' : '-';
for (const [g, G] of Object.entries(agg)) {
  console.log(`== ${g} on ${MAP}: ${G.games} games`);
  G.bins.forEach((B, i) => {
    const [a, b] = BINS[i];
    console.log(`  r${a}-${b}: our units at round start ${(B.units / Math.max(1, B.unitN)).toFixed(1)}; turns ${B.turns}, at L>=4 ${B.l4} (${pc(B.l4, B.turns)}); split ${B.split} (${pc(B.split, B.l4)} of L>=4 turns, ${(B.split / G.games).toFixed(1)}/game) | ` +
      `not split at L>=4: swarm safety stop sxx ${B.sxx} / srx ${B.srx}, child spot failed ${B.sxc}, no deficit srn ${B.srn}, tail rule ${B.tailx}, trade ${B.trade}, policy did not want ${B.none} | engines ${JSON.stringify(B.engines)}`);
  });
}
