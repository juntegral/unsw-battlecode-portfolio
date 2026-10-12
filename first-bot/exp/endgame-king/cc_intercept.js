#!/usr/bin/env node
// Cross-check of the interception share with the conversion-chain cache (its own hooks and classes): labelled feed/conv whose
// target was the final-king line member at that moment; share of their pearls eaten by other own dragons (not the line).
// Compared with the same share from .cache/endgame-king (this study's rows). usage: node exp/endgame-king/cc_intercept.js
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const rd = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l)) : [];
const CLS = ['K0', 'KA', 'E', 'U', 'Ms', 'Mm', 'S2Ks', 'S2Km', 'Ss', 'Sm', 'Xs', 'Xm'];
for (const set of ['cand-stack1-online', 'cand-stack2-online', 'cand-stack3-online', 'cand-stack4-online', 'cand-stack5-online', 'cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3']) {
  // conversion chain
  let cd = 0, co = 0;
  for (const g of rd(path.join(ROOT, '.cache', 'conv-chain', 'online-' + set + '.jsonl'))) {
    if (g.kind !== 'r500') continue;
    for (const v of (g[g.us] && g[g.us].conv) || []) { if (!v.died || !v.tOnLine || !v.c || v.r < 300) continue; const n = v.c.reduce((a, b) => a + b, 0) - v.c[3]; cd += n + v.c[3]; co += n - v.c[0] - v.c[1] - v.c[2]; }
  }
  // this study
  let ed = 0, eo = 0;
  for (const g of rd(path.join(ROOT, '.cache', 'endgame-king', 'online-' + set + '.jsonl'))) {
    if (g.kind !== 'r500') continue;
    for (const v of g[g.us].conv || []) { if (!v[6] || !v[12] || v[1] < 300) continue; ed += v[7]; eo += v[10]; }
  }
  console.log(set.padEnd(24), 'conv-chain: drops', cd, 'other own', co, (100 * co / cd).toFixed(1) + '%', '| this study: drops', ed, 'other own', eo, (100 * eo / ed).toFixed(1) + '%');
}
