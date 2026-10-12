#!/usr/bin/env node
// W2: per process of our team, the state in its first " map=" tag and the delay (in its own turns) to its first decided tag
// (map=<Name>/<a|b|?>). Start processes = ids below the map's initial dragon count. Fast: events only.
// usage: node exp/w2/tagtiming.js <replay> ...
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const load = makeLoader(viewerSource());
const agg = {};
for (const f of process.argv.slice(2)) {
  const us = /_B_\d+\//.test(f) ? 'B' : 'A';
  const mapName = (/_(autarky|default|devil|portals|prisoners_dilemma|queen_of_spades|schooltime|slithery_fight|trauma|trophy|stronghold|arena|big_empty|Colosseum|default_small|dilemma)_[AB]_/.exec(f) || [])[1] || path.basename(path.dirname(path.dirname(f)));
  const R = load(f);
  const n0 = R.match.map.initialDragons.length;
  const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
  const P = new Map();   // id -> {turns, first, decAt}
  let cur = -1;
  for (const e of R.events) {
    if (e.type === 'dragonSplit') team.set(e.childId, e.team);
    if (e.type === 'turnStart') { cur = e.id; if (team.get(cur) === us) { const p = P.get(cur) || { turns: 0, first: null, decAt: null }; p.turns++; P.set(cur, p); } }
    if (e.type !== 'dragonIndicator' || team.get(e.id) !== us) continue;
    const p = P.get(e.id); if (!p) continue;
    const m = / ?map=(\S+)/.exec(e.text || ''); if (!m) continue;
    if (p.first === null) p.first = m[1];
    if (p.decAt === null && m[1] !== 'none' && m[1] !== '?') p.decAt = p.turns - 1;
  }
  const a = agg[mapName] = agg[mapName] || { start: [0, 0, 0], child: [0, 0, 0, 0], delays: [] };
  for (const [id, p] of P) {
    const isStart = id < n0;
    if (isStart) { a.start[0]++; if (p.decAt === 0) a.start[1]++; else if (p.decAt !== null) a.start[2]++; }
    else { a.child[0]++; if (p.decAt === 0) a.child[1]++; else if (p.decAt !== null) { a.child[2]++; a.delays.push(p.decAt); } else a.child[3]++; }
  }
}
for (const [m, a] of Object.entries(agg)) {
  const d = a.delays.sort((x, y) => x - y);
  console.log(`${m.padEnd(18)} start ${a.start[0]}: decided first turn ${a.start[1]}, later ${a.start[2]} | children ${a.child[0]}: first turn ${a.child[1]} (${(100 * a.child[1] / Math.max(1, a.child[0])).toFixed(0)}%), later ${a.child[2]} (median ${d.length ? d[d.length >> 1] : '-'}), never ${a.child[3]}`);
}
