#!/usr/bin/env node
// v1.4: for our deaths in r0-<to> in a set, the dead dragon's last indicator before it died: steered by the opening (" op<role>" active),
// handed back earlier (" opx<why>" seen before), or never in the script; with the death cause (mass ledger) and the rounds since the hand-back
// usage: node exp/v14/deathctx.js <map file name> <set dir>[,<dir>...] [to]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const [mapName, dirs, to = 50] = process.argv.slice(2);
const agg = {};
for (const dir of dirs.split(',')) {
  for (const row of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l))) {
    if (row.map !== mapName || row.G === undefined) continue;
    const f = path.join(dir, 'games', row.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
    const R = load(f), us = row.side;
    const lastTag = new Map(), handRound = new Map();
    ML.perGame(R, { map: R.match.map.mapName }, {
      indicator(e, round, ctx) {
        const d = ctx && ctx.drag ? ctx.drag.get(e.id) : null; if (!d || d.team !== us) return;
        const t = e.text || '';
        const x = / opx([a-z])/.exec(t);
        if (x) handRound.set(e.id, [x[1], round]);
        lastTag.set(e.id, / op(R[\d.]*)(>| |$|s)/.test(t) ? 'steered' : 'other');
      },
      death(d, rec, idx, other, round) {
        if (d.team !== us || round > +to) return;
        const h = handRound.get(d.id);
        const ctxk = lastTag.get(d.id) === 'steered' ? 'steered' : h ? (h[0] === 'n' ? 'no role' : `after hand-back ${h[0]}`) : 'never scripted';
        const k = `${ctxk} | ${ML.CAUSE[rec.cause]}`;
        (agg[k] = agg[k] || []).push(h && h[0] !== 'n' ? round - h[1] : null);
      },
    });
  }
}
for (const [k, v] of Object.entries(agg).sort((a, b) => b[1].length - a[1].length)) {
  const r = v.filter(x => x !== null);
  console.log(`${k}: ${v.length}${r.length ? ` (rounds after the hand-back: median ${r.sort((a, b) => a - b)[r.length >> 1]})` : ''}`);
}
