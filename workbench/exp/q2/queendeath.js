#!/usr/bin/env node
// Q2: what preceded each of our queen's deaths: her last split (round, kind from her indicator) if within 5 rounds, her length at death,
// the cause, and her last indicator. usage: node exp/q2/queendeath.js <runq set dir>... [--nopocket]
'use strict';
process.env.UNSW_RULES = process.env.UNSW_RULES || '123';   // 1.2.3 replays (tools/mass_ledger.js step simulation)
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const skip = process.argv.includes('--nopocket') ? /autarky|dilemma|slithery/i : null;
for (const set of process.argv.slice(2).filter(a => !a.startsWith('--'))) {
  const rows = fs.readFileSync(path.join(set, 'rows.jsonl'), 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse);
  const cls = {};
  for (const r of rows) {
    if (skip && skip.test(r.map)) continue;
    const f = path.join(set, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
    const Q = r.side === 'A' ? 0 : 1;
    let lastInd = '', lastSplit = null, out = null;
    perGame(load(f), { map: r.map, variant: 'a' }, {
      indicator(e, round) { if (e.id === Q) lastInd = `r${round} ${e.text}`; },
      split(p, ch, e, round) { if (p.id === Q) lastSplit = { round, kind: (lastInd.split(' ')[1] || '?').replace(/[0-9]+$/, '') }; },
      death(d, rec, idx, other, round) { if (d.id !== Q) return; const recent = lastSplit && round - lastSplit.round <= 5;
        out = `${CAUSE[rec.cause]} L${d.body.length}${recent ? ' after ' + lastSplit.kind + ' r' + lastSplit.round : ''}`;
        const k = `${CAUSE[rec.cause]}${recent ? ' after ' + lastSplit.kind : d.body.length <= 3 ? ' while L<=3' : ' while L>=4'}`; cls[k] = (cls[k] || 0) + 1;
        if (process.argv.includes('--games')) console.log(`  ${r.key} r${round} ${out} | ${lastInd}`); },
    });
  }
  console.log(`${path.basename(set)}: ` + Object.entries(cls).sort((a, b) => b[1] - a[1]).map(([k, v]) => k + ' ' + v).join(', '));
}
