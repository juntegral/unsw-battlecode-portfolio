#!/usr/bin/env node
// stub_shape.js — what the split before a "stub" death looks like (research/observations/top-mass-spending.md, 2026-09-30).
// A stub death (tools/mass_ledger.js, mech = 'stub') is a death that is not a head-on collision, of a dragon that split
// within the last 2 rounds keeping <= 3 segments. This script re-reads replays (no network, no games) and reports, for
// every such death, the split shape (length before > kept + child) and the rounds from the split to the death.
// usage: node exp/mass-analysis/stub_shape.js [--keys exp/mass-analysis/sample-top1500.keys] [--every 37]
//   Takes every N-th key of the key file (default 37 -> 41 games of the stratified sample).
// Tracking is light (lengths from splits only; eating is not needed for the split shape).
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const keys = fs.readFileSync(path.resolve(ROOT, opt('keys', 'exp/mass-analysis/sample-top1500.keys')), 'utf8').split('\n').filter(Boolean);
const every = +opt('every', 37);
const pick = []; for (let i = 0; i < keys.length; i += every) pick.push(keys[i]);
const stats = { stub: 0, shape: {}, gap: { 0: 0, 1: 0, 2: 0 }, before: {}, childLen: 0, kept2: 0 };
for (const k of pick) {
  const [b, g] = k.split(':');
  const R = load(path.join(ROOT, 'data', 'top', b, g + '.replay.gz'));
  const split = new Map(); let round = -1;
  for (const e of R.events) {
    if (e.type === 'roundStart') round = e.round;
    else if (e.type === 'dragonSplit') split.set(e.parentId, { r: round, before: e.parentBody.length + e.childBody.length, kept: e.parentBody.length, child: e.childBody.length });
    else if (e.type === 'dragonDeath') {
      const s = split.get(e.id);
      if (!s || s.r < round - 2 || s.kept > 3 || e.reason === 'H') continue;
      stats.stub++; if (s.kept === 2) stats.kept2++;
      const sh = s.before + '>' + s.kept + '+' + s.child; stats.shape[sh] = (stats.shape[sh] || 0) + 1;
      stats.gap[Math.min(2, round - s.r)]++;
      const bc = s.before <= 4 ? String(s.before) : s.before <= 7 ? '5-7' : '8+'; stats.before[bc] = (stats.before[bc] || 0) + 1;
      stats.childLen += s.child;
    }
  }
}
const top = Object.entries(stats.shape).sort((a, b) => b[1] - a[1]).slice(0, 10);
const pc = x => (100 * x / stats.stub).toFixed(1) + '%';
console.log(`games ${pick.length}; stub deaths (not head-on) ${stats.stub} (${(stats.stub / pick.length).toFixed(1)} per game, both teams)`);
console.log(`parent kept 2 segments: ${pc(stats.kept2)}; rounds from split to death: 0 ${pc(stats.gap[0])}, 1 ${pc(stats.gap[1])}, 2 ${pc(stats.gap[2])}`);
console.log(`length before split: 4 ${pc(stats.before['4'] || 0)}, 5-7 ${pc(stats.before['5-7'] || 0)}, 8+ ${pc(stats.before['8+'] || 0)}; mean child length ${(stats.childLen / stats.stub).toFixed(2)}`);
console.log('split shape before>kept+child (top 10): ' + top.map(([s, v]) => `${s} ${pc(v)}`).join(', '));
