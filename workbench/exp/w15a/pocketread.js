#!/usr/bin/env node
// W15a-t deep read: the start-pocket lineage's first rounds in one game: every action of its dragons (move with head before -> after and
// whether it ate, split with sizes and the child's birth tile, deaths), rounds 0..N.
// usage: node exp/w15a/pocketread.js <replay> <team A|B> [--rounds 12]
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const [file, team] = process.argv.slice(2), ri = process.argv.indexOf('--rounds'), NR = ri >= 0 ? +process.argv[ri + 1] : 12;
const R = makeLoader(viewerSource())(file);
const DIRS = ['N', 'E', 'S', 'W'];
let G = null; const lin = new Set(); let started = false;
const geo = ctx => { if (G) return G; const { W, H, across } = ctx, N = W * H, nb = new Array(N);
  for (let k = 0; k < N; k++) { const x = k % W, y = (k / W) | 0; nb[k] = DIRS.map(d => { const u = across(x, y, d); return u ? u.y * W + u.x : -1; }); }
  const deg = new Int32Array(N), gone = new Uint8Array(N), q = [];
  for (let k = 0; k < N; k++) { for (const u of nb[k]) if (u >= 0) deg[k]++; if (deg[k] <= 1) { gone[k] = 1; q.push(k); } }
  for (let i = 0; i < q.length; i++) for (const u of nb[q[i]]) { if (u < 0 || gone[u]) continue; if (--deg[u] <= 1) { gone[u] = 1; q.push(u); } }
  G = { W, H, gone }; return G; };
const st = (g, p) => `${p.x},${p.y}${g.gone[p.y * g.W + p.x] ? '' : '*'}`;   // * = on the 2-core
perGame(R, { map: '?', variant: 'a' }, {
  turn(d, round, ctx) { if (started) return; const g = geo(ctx); for (const d0 of R.match.map.initialDragons) if (d0.team === team && g.gone[d0.body[0].y * g.W + d0.body[0].x]) { lin.add(d0.id); console.log(`start #${d0.id} L${d0.body.length} head ${st(g, d0.body[0])} tail ${st(g, d0.body[d0.body.length - 1])}`); } started = true; },
  action(d, e, round, ctx, hb) {
    if (!lin.has(d.id) || round > NR) return; const g = geo(ctx);
    if (e.action && e.action.kind === 'move') console.log(`r${round} #${d.id} move ${(e.action.dirs || e.action.dir || '')} ${st(g, hb[0])} -> ${st(g, d.body[0])} L${hb.length}->${d.body.length} tail ${st(g, d.body[d.body.length - 1])}`);
  },
  split(p, ch, e, round, ctx) { if (!lin.has(p.id) || round > NR) { if (lin.has(p.id)) lin.add(ch.id); return; } const g = geo(ctx); lin.add(ch.id);
    console.log(`r${round} #${p.id} SPLIT child #${ch.id} size ${ch.body.length}, parent keeps ${p.body.length}; child head ${st(g, ch.body[0])} facing ${e.childFacing || '?'}; parent tail ${st(g, p.body[p.body.length - 1])}`); },
  death(d, rec, idx, other, round, ctx) { if (!lin.has(d.id) || round > NR + 20) return; const g = geo(ctx); console.log(`r${round} #${d.id} DIES ${CAUSE[rec.cause]} at ${st(g, d.body[0])} L${d.body.length}`); },
});
