#!/usr/bin/env node
// Mechanism numbers of our side (sides named "bot") per measured label, tools/proxy_check.js definitions:
// deaths per side and by mode (head-on with an ally, into an ally body, trapped kelp/own body, rams we made, rammed by
// the enemy), pearls eaten in r0-99 (median side), exit sacrifices per side. Top-team values in the last row.
// usage: node exp/cand-swarm1/mech.js <label> [<label> ...]
'use strict';
const path = require('path'), fs = require('fs');
const ROOT = path.resolve(__dirname, '..', '..');
const pc = require(path.join(ROOT, 'tools', 'proxy_check.js'));
const f = x => x === null || x === undefined || Number.isNaN(x) ? '-' : (Math.round(x * 100) / 100).toString();
console.log('| sides | n | deaths/side | ally head-on | into ally body | trapped kelp/own body | rams made | rammed | eaten r0-99 (median) | exit sacrifices/side |');
console.log('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
const row = (name, S) => { const m = pc.metrics(S); console.log(`| ${name} | ${S.length} | ${f(m.deathsPerSide)} | ${f(m.modes['H-own'])} | ${f(m.modes['O-own'])} | ${f(m.modes['WS-trapped'])} | ${f(m.rams.perSide)} | ${f(m.rammedPerSide)} | ${f(m.eaten100)} | ${f(m.free.perSide)} |`); };
for (const L of process.argv.slice(2)) {
  const file = path.join(ROOT, 'exp', L, 'sides.jsonl'); if (!fs.existsSync(file)) continue;
  row(L, pc.readJsonl(file).filter(x => x.name === 'bot'));
}
row('top teams (all)', pc.topSides());
