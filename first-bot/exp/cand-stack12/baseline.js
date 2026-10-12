#!/usr/bin/env node
// cand-stack12 baselines (research/experiments/cand-stack12.md): the pf gates' and indicators' values on earlier online waves, from the intake-gap
// cache (.cache/intake-gap/online-<set>.jsonl; extend it with `nice -n 10 node exp/intake-gap/extract.js online <set> --jobs 2`).
// First it re-derives the study's published numbers (the check that exp/cand-stack12/pfstats.js reads the records as the study did), then it
// prints the same numbers on the pf maps (Portals is off in stack12, so the 500-round pf maps are Slithery Fight, Schooltime and Trauma).
// usage: node exp/cand-stack12/baseline.js
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'intake-gap');
const PS = require('./pfstats.js');
const GROUPS = {
  'stack5-8 (W5-W9)': ['cand-stack5-online', 'cand-stack6-online', 'cand-stack6-online-r2', 'cand-stack7-online', 'cand-stack8-online'],
  'stack9 (W10)': ['cand-stack9-online'],
  'stack10 (W11)': ['cand-stack10-online'],
  'merge2 (r1-r3)': ['cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3'],
  'swarm8': ['cand-swarm8-online'],
};
const read = s => { const f = path.join(CACHE, 'online-' + s + '.jsonl'); return fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => JSON.parse(l)) : []; };
const f1 = v => v === null || v === undefined ? '–' : (Math.round(v * 10) / 10).toFixed(1);
const f3 = v => v === null || v === undefined ? '–' : v.toFixed(3);
const pc = v => v === null || v === undefined ? '–' : Math.round(100 * v) + '%';
const OPEN500 = new Set(['Portals', 'Schooltime', 'Slithery Fight', 'Trauma']);
const out = [];
for (const [gname, sets] of Object.entries(GROUPS)) {
  const G = sets.flatMap(read);
  if (!G.length) { out.push(`## ${gname}: no cache`); continue; }
  const st = G.map(g => PS.gameStats(g, g.us === 'B' ? 1 : 0));
  const sel = f => PS.pool(st.filter(f));
  const r500 = sel(x => x.kind === 'r500'), open4 = sel(x => OPEN500.has(x.map)), el4 = sel(x => PS.PF_ELIM.has(x.map));
  const on500 = sel(x => PS.PF_500.has(x.map)), onAll = sel(x => PS.PF_MAPS.has(x.map)), sf = sel(x => x.map === 'Slithery Fight');
  const elimK = sel(x => x.kind === 'elim');
  out.push(`## ${gname} (${G.length} games)`);
  out.push(`- study check (500-type, 5 maps, n ${r500.n}): units r10/r50/r100/r250 ${r500.units.map(f1).join(' / ')} vs opp ${r500.unitsO.map(f1).join(' / ')}; territory share enemy-nearer ${pc(r500.terrNear)}; final longest ${f1(r500.kingEnd)} (opp ${f1(r500.kingEndO)}); eliminated ${pc(r500.elim)}; natural intake ${f1(r500.nat)} vs ${f1(r500.natO)}`);
  out.push(`- study check (open 500, 4 maps with Portals, n ${open4.n}): split speed ours r0-49/r50-99/r100-249 ${open4.speed.map(f3).join(' / ')}, opp ${open4.speedO.map(f3).join(' / ')}; r0-99 intake ${f1(open4.nat99)} vs ${f1(open4.nat99O)}; view-B heads r0-249 ${f1(open4.heads249)}; race share r0-249 ${f1(open4.race249)}`);
  out.push(`- study check (open elim, 4 maps, n ${el4.n}): split speed ours ${el4.speed.map(f3).join(' / ')}, opp ${el4.speedO.map(f3).join(' / ')}; view-B heads r0-249 ${f1(el4.heads249)}; units r10/r50/r100/r250 ${el4.units.map(f1).join(' / ')}; eliminated ${pc(elimK.elim)} (elim-type all 5 maps)`);
  out.push(`- pf maps, 500 (SF + Schooltime + Trauma, n ${on500.n}): units r10/r50/r100/r250 ${on500.units.map(f1).join(' / ')} vs opp ${on500.unitsO.map(f1).join(' / ')}; split speed r0-99 ${f3(on500.speed99)} (r0-49 ${f3(on500.speed[0])}, r50-99 ${f3(on500.speed[1])}) vs opp ${f3(on500.speed99O)}; r0-99 intake ${f1(on500.nat99)} vs ${f1(on500.nat99O)}; heads r0-249 ${f1(on500.heads249)}; race r0-249 ${f1(on500.race249)}; territory ${pc(on500.terrNear)}; final longest ${f1(on500.kingEnd)}`);
  out.push(`- pf maps, all 7 (n ${onAll.n}): split speed r0-99 ${f3(onAll.speed99)} (r0-49 ${f3(onAll.speed[0])}, r50-99 ${f3(onAll.speed[1])}) vs opp ${f3(onAll.speed99O)}; non-escape births r0-99 ${f1(onAll.births99)} a game on ${f1(onAll.l4hr99)} L>=4 head-rounds`);
  out.push(`- Slithery Fight (n ${sf.n}): units r10/r50/r100 ${sf.units.slice(0, 3).map(f1).join(' / ')} vs opp ${sf.unitsO.slice(0, 3).map(f1).join(' / ')}; split speed r0-99 ${f3(sf.speed99)}; r0-99 intake ${f1(sf.nat99)} vs ${f1(sf.nat99O)}`);
  out.push(`- pf elim maps (n ${el4.n}): units r10/r50/r100 ${el4.units.slice(0, 3).map(f1).join(' / ')} vs opp ${el4.unitsO.slice(0, 3).map(f1).join(' / ')}; split speed r0-99 ${f3(el4.speed99)}; r0-99 intake ${f1(el4.nat99)} vs ${f1(el4.nat99O)}`);
  for (const m of ['Slithery Fight', 'Schooltime', 'Trauma', 'Default', 'Devil', 'Queen Of Spades', 'Trophy']) {
    const P = sel(x => x.map === m);
    out.push(`  - ${m} (n ${P.n}): units r10/r50/r100 ${P.units.slice(0, 3).map(f1).join(' / ')} vs ${P.unitsO.slice(0, 3).map(f1).join(' / ')}; speed r0-99 ${f3(P.speed99)} vs ${f3(P.speed99O)}; r0-99 intake ${f1(P.nat99)} vs ${f1(P.nat99O)}`);
  }
}
console.log(out.join('\n'));
