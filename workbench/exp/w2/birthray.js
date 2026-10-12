#!/usr/bin/env node
// W2 next-step estimate (versions/v1.6.1/VERSION.md §2.6, the birth ray): in a set of v1.6.1 games, for every child of ours, whether it decided
// on its first turn (its first " map=" tag names a map), whether its parent had decided when it split, and whether the old body was straight at
// the split point (the child's tail on the line parent second-last -> parent tail: a ray the parent sends into its own neck leaves at its tail
// in that direction and hits the child's tail; checked on local replays, exp/w2 notes). The union is the share a birth ray would have
// confirmed on the first turn. usage: node exp/w2/birthray.js <setDir> [...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const by = {};
for (const set of process.argv.slice(2)) {
  const rowsF = path.join(ROOT, set, 'rows.jsonl');
  for (const r of fs.readFileSync(rowsF, 'utf8').split('\n').filter(Boolean).map(JSON.parse)) {
    if (r.G === undefined || r.error) continue;
    const R = load(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'));
    const W = R.match.map.width, H = R.match.map.height, us = r.side;
    const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
    const decided = new Map();   // id -> true once a decided tag was printed
    const kids = new Map();      // child id -> {straight, parentDec, first: null|bool}
    for (const e of R.events) {
      if (e.type === 'dragonSplit') {
        team.set(e.childId, e.team);
        if (e.team !== us) continue;
        const pb = e.parentBody, cb = e.childBody, t = pb[pb.length - 1], s = pb[pb.length - 2], c = cb[cb.length - 1];
        const dx = ((t.x - s.x + W + 1) % W) - 1, dy = ((t.y - s.y + H + 1) % H) - 1;   // -1, 0, 1 on the torus
        const straight = c.x === (t.x + dx + W) % W && c.y === (t.y + dy + H) % H;
        kids.set(e.childId, { straight, parentDec: !!decided.get(e.parentId), first: null });
      } else if (e.type === 'dragonIndicator' && team.get(e.id) === us) {
        const m = /(?:^| )map=(\S+)/.exec(e.text || '');
        if (!m) continue;
        const dec = m[1] !== 'none' && m[1] !== '?';
        const k = kids.get(e.id); if (k && k.first === null) k.first = dec;
        decided.set(e.id, dec);   // the state the tag reports (tags are printed on the first turn and on changes)
      }
    }
    const B = by[r.map] = by[r.map] || { kids: 0, first: 0, straight: 0, straightPD: 0, union: 0 };
    for (const k of kids.values()) {
      if (k.first === null) continue;   // never acted
      B.kids++; if (k.first) B.first++; if (k.straight) B.straight++;
      const ray = k.straight && k.parentDec; if (ray) B.straightPD++;
      if (k.first || ray) B.union++;
    }
  }
}
const pc = (a, b) => (100 * a / Math.max(1, b)).toFixed(0) + '%';
console.log('map: children; decided on the first turn now; straight split point; straight with a decided parent; first turn with a birth ray (union)');
let T = { kids: 0, first: 0, straight: 0, straightPD: 0, union: 0 };
for (const [m, B] of Object.entries(by)) { for (const k of Object.keys(T)) T[k] += B[k]; console.log(`${m.padEnd(18)} ${String(B.kids).padStart(5)}  now ${pc(B.first, B.kids)}  straight ${pc(B.straight, B.kids)}  straight+decided parent ${pc(B.straightPD, B.kids)}  union ${pc(B.union, B.kids)}`); }
console.log(`${'ALL'.padEnd(18)} ${String(T.kids).padStart(5)}  now ${pc(T.first, T.kids)}  straight ${pc(T.straight, T.kids)}  straight+decided parent ${pc(T.straightPD, T.kids)}  union ${pc(T.union, T.kids)}`);
