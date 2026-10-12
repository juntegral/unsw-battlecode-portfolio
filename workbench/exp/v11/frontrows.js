#!/usr/bin/env node
'use strict';
// frontrows.js — prints the v1.1 FRONT_POLICY rows for policy.hpp: the elite winners' head share by frontier bin (own-deep 0 .. enemy-deep 4) at
// r25 / r50 / r100 / r250, in whole percent, from a spatial study table (maps["<Map>/<layout>"].classes["elite-winners"].checkpoints[r].headShare,
// headsPerGame, N). Family rows (layout not decided yet) take the mean of the two layouts. Maps without the class print a comment only.
// usage: node exp/v11/frontrows.js exp/spatial/tables.json [exp/spatial-all/cache/tables.json ...]   (later files win per map/layout)
const fs = require('fs');
const files = process.argv.slice(2);
const T = {};
for (const f of files) {
  const t = JSON.parse(fs.readFileSync(f, 'utf8'));
  for (const [k, m] of Object.entries(t.maps)) if (m.classes && m.classes['elite-winners']) T[k] = { c: m.classes['elite-winners'], src: f };
}
const ROWS = [['Trauma', 'Trauma', '*', ['a']], ['Slithery_Fight', 'Slithery Fight', 'a', ['a']], ['Slithery_Fight', 'Slithery Fight', 'b', ['b']],
  ['Schooltime', 'Schooltime', 'a', ['a']], ['Schooltime', 'Schooltime', 'b', ['b']], ['Default', 'Default', '*', ['a']],
  ['Devil', 'Devil', 'a', ['a']], ['Devil', 'Devil', 'b', ['b']], ['Queen_Of_Spades', 'Queen Of Spades', 'a', ['a']],
  ['Queen_Of_Spades', 'Queen Of Spades', 'b', ['b']], ['Trophy', 'Trophy', '*', ['a']]];
const FAM2 = [['Slithery_Fight', 'Slithery Fight'], ['Schooltime', 'Schooltime'], ['Devil', 'Devil'], ['Queen_Of_Spades', 'Queen Of Spades']];
const CPS = ['25', '50', '100', '250'];
const shareOf = (name, lay, r) => { const e = T[`${name}/${lay}`]; if (!e) return null; const cp = e.c.checkpoints[r]; return cp ? cp.headShare.slice(0, 5) : null; };
const pct = a => a.map(v => Math.round(100 * v));
const out = [];
const row = (fam, lay, shares, note) => out.push(`    {"${fam}", '${lay}', {${shares.map(s => '{' + pct(s).join(', ') + '}').join(', ')}}},   // ${note}`);
for (const [fam, name, lay, src] of ROWS) {
  const e = T[`${name}/${src[0]}`];
  if (!e) { out.push(`    // {"${fam}", '${lay}'}: no elite-winners class yet (v1 behaviour)`); continue; }
  const shares = CPS.map(r => shareOf(name, src[0], r));
  if (shares.some(s => !s)) { out.push(`    // {"${fam}", '${lay}'}: a checkpoint is missing`); continue; }
  const N = CPS.map(r => e.c.checkpoints[r].N).join('/'), hpg = CPS.map(r => e.c.checkpoints[r].headsPerGame.toFixed(1)).join('/');
  row(fam, lay, shares, `${name}/${src[0]} elite winners, N ${N} (r25/50/100/250), heads/game ${hpg}; ${e.src.replace(/.*\/exp\//, 'exp/')}`);
}
for (const [fam, name] of FAM2) {
  const a = CPS.map(r => shareOf(name, 'a', r)), b = CPS.map(r => shareOf(name, 'b', r));
  if (a.some(s => !s) || b.some(s => !s)) continue;
  row(fam, '*', a.map((s, i) => s.map((v, j) => (v + b[i][j]) / 2)), `${name} a/b mean (layout not decided yet)`);
}
console.log(out.join('\n'));
