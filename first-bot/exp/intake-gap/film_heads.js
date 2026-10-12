#!/usr/bin/env node
// Stage 3a close reading of one game's head build-up (exp/intake-gap/picks.js 3a). For every window of `every` rounds up to --to,
// per team: dragons at the window start (count and the lengths, longest first), splits in the window (our split labels by kind),
// deaths in the window, natural pearls eaten; for our team also the dragon-turns with length >= 4 (csplit's length rule) and the
// share of those turns that ended in a split, and the turn labels of our dragons of length >= 4 that did not split (kinds).
// usage: node exp/intake-gap/film_heads.js <set>:<gameId> [--every 10] [--to 120] [--also 250,300,350,400]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const RL = require('./rawload.js');
const E = require('./extract.js');
const argv = process.argv.slice(2), opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const [set, gid] = argv[0].split(':');
const every = +opt('every', 10), to = +opt('to', 120), also = (opt('also', '') || '').split(',').filter(Boolean).map(Number);
const dir = path.join(ROOT, 'data', 'online', set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
const gm = (idx.games || idx).find(g => String(g.gameId) === gid);
const us = String(gm.ourSide).toUpperCase();
const R = RL.load(path.join(dir, 'M' + gid + '.replay'));
const W = { splits: [0, 0], deaths: [0, 0], nat: [0, 0], kinds: {}, l4turns: 0, l4split: 0, l4kinds: {} };
const label = new Map();
const out = [];
let lastRound = -99;
const reset = () => { W.splits = [0, 0]; W.deaths = [0, 0]; W.nat = [0, 0]; W.kinds = {}; W.l4turns = 0; W.l4split = 0; W.l4kinds = {}; };
const snap = (r, ctx) => {
  const t = [[], []];
  for (const d of ctx.drag.values()) t[d.team === us ? 0 : 1].push(d.body.length);
  t.forEach(a => a.sort((x, y) => y - x));
  const fmt = a => `${a.length} [${a.slice(0, 12).join(',')}${a.length > 12 ? ',…' : ''}]`;
  out.push(`r${r}: us ${fmt(t[0])} | them ${fmt(t[1])}`);
};
const flush = (r0, r1) => {
  const top = o => Object.entries(o).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${v}`).join(', ');
  out.push(`  r${r0}–${r1 - 1}: splits us ${W.splits[0]} (${top(W.kinds) || '-'}) / them ${W.splits[1]}; deaths us ${W.deaths[0]} / them ${W.deaths[1]}; natural eaten us ${W.nat[0]} / them ${W.nat[1]}; our L>=4 turns ${W.l4turns}, split on ${W.l4split}; their labels: ${top(W.l4kinds) || '-'}`);
};
let wStart = 0;
const want = r => r <= to || also.includes(r) || also.some(a => r > a && r < a + every);
const hooks = {
  turn(d, round, ctx) {
    if (round !== lastRound) {
      if (lastRound >= 0 && (round % every === 0) && want(lastRound)) flush(wStart, round);
      if (round % every === 0) { if (want(round)) snap(round, ctx); reset(); wStart = round; }
      lastRound = round;
    }
    label.set(d.id, null);
  },
  indicator(e) { label.set(e.id, e.text); },
  action(d, e, round) {
    const mine = d.team === us;
    if (mine && d.body.length >= 4) {
      W.l4turns++;
      const k = E.labelKind(label.get(d.id));
      if (e.action && e.action.kind === 'split') W.l4split++; else W.l4kinds[k] = (W.l4kinds[k] || 0) + 1;
    }
  },
  eat(d, k, o) { if (o < 0) W.nat[d.team === us ? 0 : 1]++; },
  split(p, ch) { const mine = p.team === us; W.splits[mine ? 0 : 1]++; if (mine) { const k = E.splitOrigin(label.get(p.id)); W.kinds[k] = (W.kinds[k] || 0) + 1; } },
  death(d) { W.deaths[d.team === us ? 0 : 1]++; },
};
ML.perGame(R, { map: gm.mapName }, hooks);
console.log(`${argv[0]} ${gm.mapName} us=${us} vs ${gm.opponentTeam}; winner ${gm.winner}`);
console.log(out.join('\n'));
