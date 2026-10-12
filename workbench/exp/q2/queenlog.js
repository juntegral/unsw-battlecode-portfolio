#!/usr/bin/env node
// Q2: one queen's life in one game: her length each N rounds, every split she made (round, sizes, her indicator that turn), and her last
// indicators before death. usage: node exp/q2/queenlog.js <replay> <queen id 0|1> [--every 10] [--tail 8]
'use strict';
process.env.UNSW_RULES = process.env.UNSW_RULES || '123';   // 1.2.3 replays (tools/mass_ledger.js step simulation)
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const [file, qs] = process.argv.slice(2), Q = +qs;
const opt = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? +process.argv[i + 1] : d; };
const EVERY = opt('--every', 10), TAIL = opt('--tail', 8);
const R = makeLoader(viewerSource())(file);
const inds = []; let last = -1; const lens = [];
perGame(R, { map: '?', variant: 'a' }, {
  turn(d, round) { if (d.id === Q && round % EVERY === 0 && round !== last) { last = round; lens.push(`r${round}:L${d.body.length}`); } },
  indicator(e, round) { if (e.id === Q) inds.push(`r${round} ${e.text}`); },
  split(p, ch, e, round) { if (p.id === Q) console.log(`SPLIT r${round}: queen keeps ${p.body.length}, child #${ch.id} ${ch.body.length} | ${inds.length ? inds[inds.length - 1] : '?'}`); },
  death(d, rec, idx, other, round) { if (d.id === Q) console.log(`DEATH r${round} ${CAUSE[rec.cause]} L${d.body.length} other ${other ? '#' + other.id + ' L' + other.body.length + ' team ' + other.team : '-'}`); },
});
console.log('lengths: ' + lens.join(' '));
console.log('last indicators:\n  ' + inds.slice(-TAIL).join('\n  '));
