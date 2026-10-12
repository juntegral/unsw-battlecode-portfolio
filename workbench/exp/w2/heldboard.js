#!/usr/bin/env node
// W2 board pictures of the recognition delay (docs/arch/README.md step 4): eval/board.js's snapshot with our heads marked by recognition state:
// '?' a process the gate holds (its last " map=" tag was "?": runs DEFAULT F0 and no table), a digit / '#' a decided one (length, '#' >= 10),
// '.' our bodies, 'X' / 'K' enemy heads (K >= 10), 'x' enemy bodies, '%' pearls. Under each picture, our held processes with their length,
// birth round and the engine label of their last turn, and the decided ones' feature tags this round (sd, hv, ck/cp/cy, pt).
// usage: node exp/w2/heldboard.js <replay> <mapName> <ourTeam A|B> <rounds comma list>
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const [file, mapName, us, roundsArg] = process.argv.slice(2);
const SNAP = new Set((roundsArg || '50,100,200,300,400,450').split(',').map(Number));
const R = makeLoader(viewerSource())(file);
const state = new Map(), born = new Map(), lastText = new Map();
let lastSnap = -1;
const out = [];
function snapshot(round, ctx) {
  const { W, H, drag, pearls } = ctx;
  const g = Array.from({ length: H }, () => Array(W).fill(' '));
  for (const [k] of pearls) g[(k / W) | 0][k % W] = '%';
  const held = [], dec = [];
  for (const d of drag.values()) {
    const L = d.body.length;
    for (let i = 1; i < L; i++) { const s = d.body[i]; g[s.y][s.x] = d.team === us ? '.' : 'x'; }
    const h = d.body[0];
    if (d.team === us) {
      const st = state.get(d.id);
      const isHeld = st === '?';
      g[h.y][h.x] = isHeld ? '?' : (L >= 10 ? '#' : String(Math.min(L, 9)));
      const t = lastText.get(d.id) || '';
      if (isHeld) held.push(`#${d.id} L${L} born r${born.has(d.id) ? born.get(d.id) : 0} ${(/ E=([A-Z])$/.exec(t) || [, '?'])[1]}`);
      else { const f = (t.match(/ (sd\S*|hv\S*|c[kpy]\S*|pt)(?= |$)/g) || []).map(s => s.trim()).join(','); if (f) dec.push(`#${d.id} L${L} ${f}`); }
    } else g[h.y][h.x] = L >= 10 ? 'K' : 'X';
  }
  out.push(`--- r${round}: held ${held.length} [${held.join('; ')}]`);
  out.push(`    decided with feature tags: ${dec.slice(0, 12).join('; ')}${dec.length > 12 ? ' …' : ''}`);
  out.push('+' + '-'.repeat(W) + '+');
  for (const row of g) out.push('|' + row.join('') + '|');
  out.push('+' + '-'.repeat(W) + '+');
}
perGame(R, { map: mapName, variant: 'a' }, {
  split(p, ch, e, round) { if (ch.team === us) born.set(ch.id, round); },
  indicator(e, round, ctx) {
    const d = ctx.drag.get(e.id); if (!d || d.team !== us) return;
    lastText.set(e.id, e.text || '');
    const m = /(?:^| )map=(\S+)/.exec(e.text || ''); if (m) state.set(e.id, m[1]);
  },
  turn(d, round, ctx) { if (SNAP.has(round) && round !== lastSnap) { lastSnap = round; snapshot(round, ctx); } },
});
console.log(out.join('\n'));
