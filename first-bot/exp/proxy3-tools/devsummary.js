#!/usr/bin/env node
'use strict';
// devsummary.js — one line of key calibration numbers per run (for the proxy3 calibration record).
// usage: node exp/proxy3-tools/devsummary.js --target px8|r1 --runs "<name>=<src>[+<src>]" [--runs ...]
//   <src> as in calib.js. The first run should be the online truth. Columns:
//   n; win / our elimination on 500-round and elimination-type maps; reach r340 on Autarky and Schooltime;
//   their r300 mass and r500 longest on 500-round maps (medians of the pooled games); mean abs map error vs the first run
//   for win, elim and reach (maps where both have games).
const path = require('path');
const C = require(path.join(__dirname, 'calib.js'));
const argv = process.argv.slice(2); const runs = [];
for (let i = 0; i < argv.length; i++) if (argv[i] === '--runs') { const s = argv[++i], j = s.indexOf('='); runs.push({ name: s.slice(0, j), spec: s.slice(j + 1) }); }
const pc = v => v === null || v === undefined ? '–' : (100 * v).toFixed(0) + '%';
const f0 = v => v === null || v === undefined ? '–' : v.toFixed(0);
const res = runs.map(r => { const G = C.games(r.spec); const by = {}; for (const m of C.MAPS) by[m] = C.stats(G.filter(g => g.map === m)); return { r, G, by, r5: C.stats(G.filter(g => C.R500.has(g.map))), el: C.stats(G.filter(g => !C.R500.has(g.map))) }; });
const ref = res[0];
const err = (x, k) => { const d = []; for (const m of C.MAPS) { const a = x.by[m][k], b = ref.by[m][k]; if (a === undefined || a === null || b === undefined || b === null) continue; d.push(Math.abs(a - b)); } return d.length ? (100 * d.reduce((s, v) => s + v, 0) / d.length).toFixed(1) + '%p' : '–'; };
console.log('| run | games | win 500 / elim-maps | our elim 500 / elim-maps | reach Autarky / Schooltime | their mass r300 (500) | their longest r500 (500) | map error win / elim / reach |');
console.log('|---|---:|---|---|---|---:|---:|---|');
for (const x of res) {
  console.log(`| ${x.r.name} | ${x.G.length} | ${pc(x.r5.win)} / ${pc(x.el.win)} | ${pc(x.r5.elim)} / ${pc(x.el.elim)} | ${pc(x.by.autarky.reach)} / ${pc(x.by.schooltime.reach)} | ${f0(x.r5.oM300)} | ${f0(x.r5.oK500)} | ${x === ref ? '–' : err(x, 'win') + ' / ' + err(x, 'elim') + ' / ' + err(x, 'reach')} |`);
}
