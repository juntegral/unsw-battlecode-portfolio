#!/usr/bin/env node
// v1.6g step 4 (docs/arch/README.md): the actual picture of a scene, to set beside the expected one in versions/v1.6/VERSION.md §8.3.
// At each chosen round (start of the round): our dragons of length >= 5 by length (id, length, head, Manhattan distance to our longest's head, the
// CONV2 declaration of that turn " ck#<id>" / " ck=", " cp<d>"), the mass of our other dragons >= 8; between rounds: every labelled feed (round, donor
// length, declared id, whether that id was our longest then, and the distance between the donor's head and the declared dragon's head).
// usage: node exp/v16/scene.js <replay> <mapName> <a|b|?> <A|B> <rounds comma list>
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const [file, mapName, variant, us, roundsArg] = process.argv.slice(2);
const SNAP = roundsArg.split(',').map(Number), want = new Set(SNAP);
const R = makeLoader(viewerSource())(file);
const snaps = new Map(), ind = new Map(), feeds = [];
const man = (a, b) => Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
const ourLongest = ctx => { let best = null; for (const [id, d] of ctx.drag) if (d.team === us && (!best || d.body.length > best[1].body.length)) best = [id, d]; return best; };
perGame(R, { map: mapName, variant }, {
  turn(d, round, ctx) {
    if (!want.has(round) || snaps.has(round)) return;
    const L = ourLongest(ctx), rows = [];
    for (const [id, q] of ctx.drag) if (q.team === us && q.body.length >= 5) rows.push({ id, L: q.body.length, x: q.body[0].x, y: q.body[0].y, d: L ? man(q.body[0], L[1].body[0]) : 0 });
    rows.sort((a, b) => b.L - a.L);
    let other = 0; for (const [id, q] of ctx.drag) if (q.team === us && q.body.length >= 8 && (!L || id !== L[0])) other += q.body.length;
    snaps.set(round, { rows, other, longest: L ? L[0] : -1 });
  },
  indicator(e, round, ctx) {
    const id = e.dragonId ?? e.id, d = ctx.drag.get(id); if (!d || d.team !== us) return;
    const s = String(e.text || '');
    if (want.has(round)) ind.set(round + ':' + id, s);
    const f = /^feed #(\d+) d(\d+) L(\d+)\s*(\S*)/.exec(s);
    if (f) { const L = ourLongest(ctx), t = ctx.drag.get(+f[1]); feeds.push({ r: round, L: +f[3], to: +f[1], kind: (f[4] || 'sf') + (/ jit/.test(s) ? ' jit' : / m(\s|$)/.test(s) ? ' m' : ''), longest: L && L[0] === +f[1], dist: t ? man(d.body[0], t.body[0]) : null }); }
  },
});
let prev = 0;
for (const r of SNAP) {
  const s = snaps.get(r); if (!s) { console.log(`r${r}: no turn`); continue; }
  const fs = feeds.filter(f => f.r > prev && f.r <= r); prev = r;
  if (fs.length) console.log(`  feeds before r${r}: ` + fs.map(f => `r${f.r} L${f.L}→#${f.to}${f.longest ? '(longest)' : ''} d${f.dist} ${f.kind}`).join('; '));
  console.log(`r${r}: longest #${s.longest}; other L>=8 mass ${s.other}`);
  for (const q of s.rows) {
    const t = ind.get(r + ':' + q.id) || '', ck = (/ ck(#\d+|=)/.exec(t) || [, ''])[1], cp = (/ cp(\d+)/.exec(t) || [, ''])[1];
    const sg = / sg(\s|$)/.test(t), gk = (/ ([Kg]\d+)/.exec(t) || [, ''])[1];   // v1.6h: the spread gate; FORTRESS's gathering goal tag
    console.log(`   #${q.id} L${q.L} @${q.x},${q.y} d${q.d} ${ck ? 'ck' + ck : ''}${cp ? ' cp' + cp : ''}${sg ? ' sg' : ''}${gk ? ' ' + gk : ''}`);
  }
}
const rest = feeds.filter(f => f.r > prev);
if (rest.length) console.log(`  feeds after r${prev}: ` + rest.map(f => `r${f.r} L${f.L}→#${f.to}${f.longest ? '(longest)' : ''} d${f.dist} ${f.kind}`).join('; '));
