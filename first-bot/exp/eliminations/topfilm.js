#!/usr/bin/env node
// Stage 3 for the top-vs-top reference: pick losers by a fixed rule and print their games from the cache (no re-parse).
// Rule: for each map-layout in MAPS, the (map-layout, winner team) cell with the most losers that has both a surviving loser (LS)
// and an eliminated one (LX), the winner being one of the six elite teams of our sets; in that cell the LS and the LX whose
// r50 unit count is nearest the cell's LS / LX mean (ties: the later game id).
// usage: node --max-old-space-size=8192 exp/eliminations/topfilm.js [--maps "Default,Devil a,Queen Of Spades a,Schooltime b"]
'use strict';
const L = require('./lib.js');
const argv = process.argv.slice(2);
const MAPS = (argv.includes('--maps') ? argv[argv.indexOf('--maps') + 1] : 'Default,Devil a,Queen Of Spades a,Schooltime b,Trophy').split(',');
const ELITE_NAMES = new Set(Object.values(L.ELITE));
const T = L.loadTop().games.filter(g => g.winner === 'A' || g.winner === 'B');
const rowsOf = (g, tm) => {
  const o = tm === 'A' ? 'B' : 'A', out = [];
  for (let r = 0; r < g.rounds; r += 10) {
    const p = g.T[tm].pos.find(x => x[0] === r) || [], q = g.T[o].pos.find(x => x[0] === r) || [];
    out.push(`${String(r).padStart(4)} | ${String(L.at(g, tm, r, 'u')).padStart(3)} ${String(L.at(g, tm, r, 't')).padStart(3)} ${String(L.at(g, tm, r, 'k')).padStart(2)} | ${String(L.at(g, o, r, 'u')).padStart(3)} ${String(L.at(g, o, r, 't')).padStart(3)} ${String(L.at(g, o, r, 'k')).padStart(2)} | splits ${String(g.T[tm].spl[r / 10] || 0).padStart(2)} | heads own/neu/en ${p.length ? p[2] + '/' + p[3] + '/' + p[4] : '-'} ally<=3 ${p.length ? p[6] : '-'} | their heads in ours ${q.length ? q[4] : '-'}`);
  }
  return out;
};
for (const ml of MAPS) {
  const cells = new Map();
  for (const g of T) {
    if (g.ml2 !== ml) continue;
    const w = g.winner, l = w === 'A' ? 'B' : 'A', wn = w === 'A' ? g.teamA : g.teamB;
    if (!ELITE_NAMES.has(wn)) continue;
    if (!cells.has(wn)) cells.set(wn, { S: [], X: [] });
    cells.get(wn)[g.T[l].end.u === 0 ? 'X' : 'S'].push({ g, tm: l });
  }
  const best = [...cells.entries()].filter(([, c]) => c.S.length && c.X.length).sort((a, b) => (b[1].S.length + b[1].X.length) - (a[1].S.length + a[1].X.length))[0];
  if (!best) { console.log(`# ${ml}: no cell with both`); continue; }
  const [wn, c] = best;
  const pick = arr => { const m = L.mean(arr.map(x => L.at(x.g, x.tm, 50, 'u'))); return arr.slice().sort((a, b) => Math.abs(L.at(a.g, a.tm, 50, 'u') - m) - Math.abs(L.at(b.g, b.tm, 50, 'u') - m) || b.g.gameId - a.g.gameId)[0]; };
  for (const [lab, x] of [['LS', pick(c.S)], ['LX', pick(c.X)]]) {
    const g = x.g, tm = x.tm, name = tm === 'A' ? g.teamA : g.teamB;
    console.log(`\n# ${ml} | winner ${wn} (cell LS ${c.S.length}, LX ${c.X.length}) | ${lab}: ${name} | top ${g.key} | end ${g.endReason} r${g.rounds} | loser elim r${g.T[tm].elim} class ${g.T[tm].elim >= 0 ? L.classOf(g.T[tm].elim, g.T[tm].kd) : '-'}`);
    console.log('   r | loser u t k | winner u t k');
    for (const l of rowsOf(g, tm).filter((_, i) => i <= 12 || i % 5 === 0)) console.log(l);
    console.log('  last deaths [r, len, mode, killer len, steps, eV]: ' + g.T[tm].last.map(d => `[r${d[0]} L${d[1]} ${L.modeOf(d)} k${d[7]} s${d[3]} eV${d[4]}]`).join(' '));
    const sw = g.T[tm].sw, n = Object.values(sw).reduce((s, v) => s + v[0], 0);
    console.log(`  swarm turns ${n} of ${g.T[tm].turns.flat().reduce((s, v) => s + v, 0)} turns`);
  }
}
