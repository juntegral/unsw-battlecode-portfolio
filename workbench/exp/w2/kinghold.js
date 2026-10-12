#!/usr/bin/env node
// W2: for each game of a set on given maps, our longest dragon at the end: its id, birth round and length at birth, and whether the recognition
// gate held it (" mg=" tag) and for how many of its turns it ran E=F before deciding; plus all our late children (born from r300) held by the gate.
// usage: node exp/w2/kinghold.js <setDir> <mapRegex>
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const [set, mapRe] = process.argv.slice(2);
const rows = fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => new RegExp(mapRe).test(r.map) && r.G !== undefined);
for (const r of rows.sort((a, b) => a.key < b.key ? -1 : 1)) {
  const R = load(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'));
  const us = r.side, team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
  const born = new Map(), held = new Map(), fTurns = new Map(), len = new Map(), alive = new Set(R.match.map.initialDragons.filter(d => d.team === us).map(d => d.id));
  let round = 0;
  for (const e of R.events) {
    if (e.type === 'roundStart') round = e.round;
    else if (e.type === 'dragonSplit') { team.set(e.childId, e.team); if (e.team === us) { born.set(e.childId, { r: round, L: e.childBody.length }); alive.add(e.childId); } }
    else if (e.type === 'dragonDeath') alive.delete(e.id);
    else if (e.type === 'dragonIndicator' && team.get(e.id) === us) {
      const t = e.text || '';
      if (/ mg=/.test(t)) held.set(e.id, round);
      const L = / L(\d+)/.exec(t); if (L) len.set(e.id, +L[1]);
      if (/ E=F$/.test(t)) fTurns.set(e.id, (fTurns.get(e.id) || 0) + 1);
    }
  }
  let best = null; for (const id of alive) if (!best || (len.get(id) || 0) > (len.get(best) || 0)) best = id;
  const lateHeld = [...held.entries()].filter(([id, r0]) => (born.get(id) || { r: 0 }).r >= 300);
  const b = born.get(best);
  console.log(`${r.key.padEnd(36)} G ${String(r.G).padStart(3)} ${r.won ? 'W' : 'L'} | longest #${best} ${b ? `born r${b.r} L${b.L}` : 'start dragon'}${held.has(best) ? ` HELD r${held.get(best)} F-turns ${fTurns.get(best) || 0}` : ''} | late children held ${lateHeld.length}${lateHeld.length ? ' (' + lateHeld.slice(0, 5).map(([id]) => `#${id} L${(born.get(id) || {}).L} F${fTurns.get(id) || 0}`).join(' ') + ')' : ''}`);
}
