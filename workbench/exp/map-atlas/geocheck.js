// geocheck.js — independent check of the geometry table (Claude): components, head-to-head path distance, and territory
// split recomputed with recount.js's own movement graph (not geometry.py), from the map objects stored by extract.js.
'use strict';
const fs = require('fs'), path = require('path');
const { buildGraph } = require('./recount.js');
const OUT = path.join(__dirname, 'cache');
const bfs = (G, seeds) => { const d = new Int32Array(G.N).fill(-1), q = []; for (const s of seeds) if (d[s] < 0) { d[s] = 0; q.push(s); }
  for (let i = 0; i < q.length; i++) { const k = q[i]; for (let z = 0; z < 4; z++) { const v = G.nb[k * 4 + z]; if (v >= 0 && d[v] < 0) { d[v] = d[k] + 1; q.push(v); } } } return d; };
const rows = {};
for (const f of fs.readdirSync(OUT).filter(f => /^geometry-.*\.json$/.test(f))) {
  const o = JSON.parse(fs.readFileSync(path.join(OUT, f), 'utf8')), M = o.M;
  for (const k of ['initialHEdges', 'initialVEdges', 'initialTiles']) if (!Array.isArray(M[k])) M[k] = Object.keys(M[k]).sort((a, b) => a - b).map(i => M[k][i]);
  const G = buildGraph(M), W = M.width;
  const heads = t => M.initialDragons.filter(d => d.team === t).map(d => d.body[0].y * W + d.body[0].x);
  const bodies = t => M.initialDragons.filter(d => d.team === t).flatMap(d => d.body.map(p => p.y * W + p.x));
  const dA = bfs(G, heads('A')); let hp = -1; for (const k of heads('B')) if (dA[k] >= 0 && (hp < 0 || dA[k] < hp)) hp = dA[k];
  const seen = new Int32Array(G.N).fill(-1); let comps = 0, sizes = [];
  for (let k = 0; k < G.N; k++) if (seen[k] < 0) { const d = bfs(G, [k]); let n = 0; for (let j = 0; j < G.N; j++) if (d[j] >= 0 && seen[j] < 0) { seen[j] = comps; n++; } sizes.push(n); comps++; }
  // undirected components are exact only if every move is reversible; report the directed-reachability count too
  const a = bfs(G, bodies('A')), b = bfs(G, bodies('B')); let tA = 0, tB = 0, t0 = 0;
  for (let k = 0; k < G.N; k++) { const x = a[k] < 0 ? 1e9 : a[k], y = b[k] < 0 ? 1e9 : b[k]; if (x < y) tA++; else if (y < x) tB++; else t0++; }
  rows[o.map + '/' + o.layout] = { headPath: hp < 0 ? null : hp, components: comps, sizes: sizes.sort((p, q) => q - p).slice(0, 3), terr: [t0, tA, tB] };
}
fs.writeFileSync(path.join(OUT, 'geocheck.json'), JSON.stringify(rows, null, 1));
const G0 = JSON.parse(fs.readFileSync(path.join(OUT, 'geometry.json'), 'utf8'));
for (const [k, r] of Object.entries(rows)) { const g = G0[k]; console.log(k, 'headPath', r.headPath, '/', g.headPath, 'comps', r.components, '/', g.components, 'sizes', r.sizes.join(','), '/', g.componentSizes.slice(0, 3).join(','), 'terr', r.terr.join(','), '/', g.terrTiles.join(',')); }
