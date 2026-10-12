#!/usr/bin/env node
'use strict';
// econ.js — per-map early/mid economy of the opponents of our bot (or of any named side), per 50-round window:
// pearls eaten, length lost in own deaths, deaths, splits (means over sides whose game is still running in that window).
// usage: node exp/proxy3-tools/econ.js --g "<name>=<src>[+<src>]" [...] [--side them|us] [--windows 0,1,2,3,4,5]
//   <src> as in calib.js (online:<set> | local:<label>[@opp,...]).
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const PC = require(path.join(ROOT, 'tools', 'proxy_check.js'));
const MAPS = ['autarky', 'portals', 'schooltime', 'slithery_fight', 'trauma', 'default', 'devil', 'pd6', 'pd10', 'queen_of_spades', 'trophy'];
function sides(spec, which) {
  const out = [];
  for (const src of spec.split('+')) {
    const [kind, rest] = src.split(/:(.*)/s);
    let file, opps = null;
    if (kind === 'online') file = path.join(ROOT, 'exp', 'proxy3-online', rest, 'sides.jsonl');
    else { const [label, o] = rest.split('@'); file = path.join(ROOT, 'exp', label, 'sides.jsonl'); if (o) opps = new Set(o.split(',')); }
    const S = PC.readJsonl(file), byKey = new Map();
    for (const x of S) { if (!byKey.has(x.key)) byKey.set(x.key, []); byKey.get(x.key).push(x); }
    for (const rs of byKey.values()) {
      const us = rs.find(x => x.name === 'bot'), them = rs.find(x => x.opp === 'bot');
      if (!us || !them || (opps && !opps.has(us.opp))) continue;
      let m = PC.mapKey(us.map); if (m.startsWith('prisoners_dilemma')) m = us.tl[0][0] >= 5 ? 'pd10' : 'pd6';
      const x = which === 'us' ? us : them; out.push({ m, x });
    }
  }
  return out;
}
const argv = process.argv.slice(2); const groups = []; let which = 'them', W = [0, 1, 2, 3, 4, 5];
for (let i = 0; i < argv.length; i++) { if (argv[i] === '--g') { const s = argv[++i], j = s.indexOf('='); groups.push([s.slice(0, j), s.slice(j + 1)]); } else if (argv[i] === '--side') which = argv[++i]; else if (argv[i] === '--windows') W = argv[++i].split(',').map(Number); }
const f = v => v.toFixed(v >= 100 ? 0 : 1);
for (const m of [...MAPS, 'ALL']) {
  console.log(`\n### ${m}: eaten / lost / deaths / splits per window (${W.map(w => w * 50 + '-' + (w * 50 + 49)).join(', ')})\n`);
  console.log('| group | sides | ' + W.map(w => 'r' + w * 50).join(' | ') + ' |\n|---|---:|' + W.map(() => '---').join('|') + '|');
  for (const [name, spec] of groups) {
    const S = sides(spec, which).filter(s => m === 'ALL' || s.m === m).map(s => s.x);
    if (!S.length) continue;
    const cells = W.map(w => { const R = S.filter(x => x.rounds > w * 50); if (!R.length) return '–'; const a = k => R.reduce((s, x) => s + x[k][w], 0) / R.length; return `${f(a('eatenW'))}/${f(a('lostW'))}/${f(a('deathsW'))}/${f(R.reduce((s, x) => s + x.splits.perW[w], 0) / R.length)} (${R.length})`; });
    console.log(`| ${name} | ${S.length} | ${cells.join(' | ')} |`);
  }
}
