#!/usr/bin/env node
// Sums every reconstruction check over the intake-gap caches (all expected 0):
//   chk  = tools/mass_ledger.js (sim, splits, drops, eatTC, ledger, final, lineage, natBal, dropBal, unknownDeath)
//   chkX = this pass (mirNone: a mirror that did not spawn with nothing on it; spawnMismatch vs the ledger; layout/sym file problems)
//   chkR = independent recount vs this pass (natural eats by phase, head-rounds by phase, race3 x fate, body blocking, mirror blocks, capacity by race)
// usage: node exp/intake-gap/check.js [.cache/intake-gap/*.jsonl ...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const files = process.argv.slice(2).length ? process.argv.slice(2) : fs.readdirSync(path.join(ROOT, '.cache', 'intake-gap')).filter(f => f.endsWith('.jsonl')).map(f => path.join(ROOT, '.cache', 'intake-gap', f));
const sum = { chk: {}, chkX: {}, chkR: {} }; let games = 0; const bad = [];
for (const f of files) for (const l of fs.readFileSync(f, 'utf8').split('\n')) {
  if (!l.trim()) continue; const g = JSON.parse(l); games++;
  let b = 0;
  for (const s of ['chk', 'chkX', 'chkR']) for (const [k, v] of Object.entries(g[s] || {})) { if (k === 'liveLeft') continue; sum[s][k] = (sum[s][k] || 0) + (v ? Math.abs(v) : 0); if (v) b++; }
  if (b) bad.push(g.key + ' ' + JSON.stringify({ chk: g.chk, chkX: g.chkX, chkR: g.chkR }));
}
console.log(`games ${games}; checks summed (all expected 0): ${JSON.stringify(sum)}`);
if (bad.length) console.log('games with a non-zero check:\n' + bad.slice(0, 20).join('\n'));
