#!/usr/bin/env node
// Who intercepts the pearls of our labelled conversions (conv, feed) whose target was on the final king's line at that moment?
// For every such event (500-round maps, the stacked sets and merge2's waves) the eaters of its drops that were not on the line:
// their length, and their label on the turn they ate (gathering "g", grab "grab@", both, other).
// usage: node exp/conv-chain/intercept.js
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { readJsonl, OUR } = require('./report.js');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const tot = { ev: 0, drops: 0, line: 0, other: 0, enemy: 0, cls: {}, len: {}, kinds: {} };
for (const s of [...OUR.stack, ...OUR.merge2]) for (const g of readJsonl(path.join(ROOT, '.cache', 'conv-chain', 'online-' + s + '.jsonl'))) {
  if (g.kind !== 'r500') continue;
  const evs = (g[g.us].conv || []).filter(v => v.tOnLine && v.died);
  if (!evs.length) continue;
  const [set, gid] = g.key.split(':');
  const R = load(path.join(ROOT, 'data', 'online', set, 'M' + gid + '.replay'));
  const lab = new Map(), didx = new Map(), eats = [];
  const want = new Map(evs.map(v => [v.id + ':' + v.r, v]));
  perGame(R, { map: g.map }, {
    indicator(e) { lab.set(e.id, e.text || ''); },
    death(d, rec, idx, o, r) { const v = want.get(d.id + ':' + r); if (v) didx.set(idx, v); },
    eat(d, t, o, r) { if (o >= 0 && didx.has(o)) eats.push({ v: didx.get(o), id: d.id, team: d.team, r, L: d.body.length, text: lab.get(d.id) || '' }); },
  });
  // the line: the final king (kid) and its ancestors; an eater is "line" when it is the target or the line member at the event
  // (cheap proxy: the target was on the line at that moment, so its own eats count as line; other ids are checked against lineAt)
  for (const v of evs) {
    tot.ev++; tot.drops += v.drops; tot.kinds[v.k] = (tot.kinds[v.k] || 0) + 1;
    for (const q of eats.filter(q => q.v === v)) {
      if (q.team !== g.us) { tot.enemy++; continue; }
      if (q.id === v.target || q.id === v.lineAt) { tot.line++; continue; }
      tot.other++;
      const t = q.text, c = /\sg\d+/.test(t) && /grab@/.test(t) ? 'g+grab' : /\sg\d+/.test(t) ? 'g' : /grab@/.test(t) ? 'grab' : /^feed/.test(t) ? 'feed-label' : 'other';
      tot.cls[c] = (tot.cls[c] || 0) + 1;
      const lc = q.L <= 4 ? 'L<=4' : q.L <= 7 ? 'L5-7' : 'L8+'; tot.len[lc] = (tot.len[lc] || 0) + 1;
    }
  }
}
console.log(JSON.stringify(tot, null, 1));
