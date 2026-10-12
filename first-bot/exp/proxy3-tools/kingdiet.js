#!/usr/bin/env node
'use strict';
// kingdiet.js — late king feeding of the opponents of our bot on the 500-round maps (games that reached r500), from
// tools/proxy_check.js side records: what the side's then-longest ate in r400-499 and how much of it came from own exit
// sacrifices (free = a free neighbour at death), the r300+ exit sacrifices, their dropped pearls, and the share eaten by
// the then-longest within 20 rounds (fragment_study fates).
// usage: node exp/proxy3-tools/kingdiet.js "<name>=<sides.jsonl>[+<sides.jsonl>]" ...
const path = require('path');
const PC = require(path.join(__dirname, '..', '..', 'tools', 'proxy_check.js'));
const R500 = new Set(['autarky', 'portals', 'schooltime', 'slithery_fight', 'trauma']);
console.log('| set | games (r500) | longest ate r400-499 | of which own sacrifices | share | sacrifices r300+ | dropped pearls | own team 20r | then-longest 20r |');
console.log('|---|---:|---:|---:|---:|---:|---:|---:|---:|');
for (const a of process.argv.slice(2)) {
  const [name, files] = a.split('=');
  const S = []; for (const f of files.split('+')) S.push(...PC.readJsonl(path.resolve(f)));
  const full = S.filter(x => x.opp === 'bot' && R500.has(PC.mapKey(x.map)) && x.rounds === 500);
  const n = full.length || 1;
  const L400 = full.reduce((s, x) => s + x.longest400, 0), F400 = full.reduce((s, x) => s + x.fromFree400, 0);
  const late = []; for (const x of full) late.push(...x.free.filter(f => f[0] >= 300));
  const drops = late.reduce((s, f) => s + f[3], 0), own = late.reduce((s, f) => s + f[4], 0), king = late.reduce((s, f) => s + f[5], 0);
  console.log(`| ${name} | ${full.length} | ${(L400 / n).toFixed(1)} | ${(F400 / n).toFixed(1)} | ${(100 * F400 / (L400 || 1)).toFixed(1)}% | ${(late.length / n).toFixed(1)} | ${(drops / n).toFixed(1)} | ${(100 * own / (drops || 1)).toFixed(0)}% | ${(100 * king / (drops || 1)).toFixed(1)}% |`);
}
