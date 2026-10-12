#!/usr/bin/env node
// W15a diagnosis: our deaths at given dead-end termini in one replay; for each, the dead dragon's birth (split round, parent, parent and child
// bodies), the parent's indicator on the split turn (which split rule fired), and the child's indicators until its death.
// usage: node exp/w7/looptrace.js <replay> <us A|B> <x,y> [<x,y> ...] [--n 6]
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const args = process.argv.slice(2), file = args[0], us = args[1];
const ni = args.indexOf('--n'), N = ni >= 0 ? +args[ni + 1] : 6;
const termini = new Set(args.slice(2).filter((a, i) => /^\d+,\d+$/.test(a)));
const R = makeLoader(viewerSource())(file);
const births = new Map(), inds = new Map(), splitInd = new Map(); let shown = 0, cur = -1;
const lastInd = new Map();
perGame(R, { map: '?', variant: 'a' }, {
  turn(d) { cur = d.id; },
  indicator(e, round) { lastInd.set(e.id, { round, text: e.text || '' }); const a = inds.get(e.id) || []; a.push(`r${round}: ${e.text}`); inds.set(e.id, a); },
  split(p, ch, e, round) { if (p.team !== us) return; births.set(ch.id, { round, parent: p.id, pb: e.parentBody, cb: e.childBody, pInd: (lastInd.get(p.id) || {}).text || '?' }); },
  death(d, rec, idx, other, round, ctx) {
    if (d.team !== us || shown >= N) return;
    const h = d.body[0];
    // the terminus: the wall-hit happens from the head's tile; report the head tile at death
    const k = `${h.x},${h.y}`;
    if (termini.size && !termini.has(k)) return;
    shown++;
    const b = births.get(d.id);
    console.log(`#${d.id} died r${round} at (${k}) cause ${CAUSE[rec.cause]} len ${d.body.length}`);
    if (b) console.log(`  born r${b.round} from #${b.parent}: parent body ${b.pb.map(s => s.x + ',' + s.y).join(' ')} | child body ${b.cb.map(s => s.x + ',' + s.y).join(' ')}\n  parent's indicator that turn: ${b.pInd}`);
    else console.log('  a start dragon');
    for (const l of (inds.get(d.id) || []).slice(-6)) console.log('    ' + l);
  },
});
