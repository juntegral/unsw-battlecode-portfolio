#!/usr/bin/env node
// W15a: how often would a "known exit" rule bind, and how often is it right? For every move of ours (first step h -> t), the bot-view status
// of the region beyond t (not back through h), from this process's own 7x7 windows since birth (optionally plus their mirror under the map's
// true symmetry, an upper bound on what the bot's symmetry inference can add):
//   cycle    a cycle of known open edges is reachable from t (BFS over known open edges only)
//   unknown  no known cycle, and the region runs into an edge this process never saw
//   dead     no known cycle and nothing unknown: a finite known tree
// against the truth: t off the 2-core of the true graph (a dead branch) or on it. Corridor = both edges of t across the move are kelp.
// usage: node exp/w15a/unkstep.js <us A|B> [--mirror] <game dirs or replays...>
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const args = process.argv.slice(2), us = args[0], MIRROR = args.includes('--mirror');
const files = [];
for (const p of args.slice(1).filter(a => !a.startsWith('--'))) {
  if (p.endsWith('.replay')) { files.push(p); continue; }
  const walk = d => { for (const f of fs.readdirSync(d)) { const q = path.join(d, f); if (fs.statSync(q).isDirectory()) walk(q); else if (f.endsWith('.replay')) files.push(q); } };
  walk(p);
}
const DIRS = ['N', 'E', 'S', 'W'], DX = [0, 1, 0, -1], DY = [-1, 0, 1, 0];
const load = makeLoader(viewerSource());
const tab = {};
const ALL = { has: () => true };   // full knowledge: the truth
const add = (k, n = 1) => { tab[k] = (tab[k] || 0) + n; };
for (const file of files) {
  let R; try { R = load(file); } catch (e) { console.error('skip', file, e.message); continue; }
  const sym = (R.match.map.symmetry || '').toLowerCase();
  let G = null;
  const geo = ctx => {
    if (G) return G;
    const { W, H, across } = ctx, N = W * H, nb = new Array(N);
    for (let k = 0; k < N; k++) { const x = k % W, y = (k / W) | 0; nb[k] = DIRS.map(d => { const u = across(x, y, d); return u ? u.y * W + u.x : -1; }); }
    const deg = new Int32Array(N), gone = new Uint8Array(N), q = [];
    for (let k = 0; k < N; k++) { for (const u of nb[k]) if (u >= 0) deg[k]++; if (deg[k] <= 1) { gone[k] = 1; q.push(k); } }
    for (let i = 0; i < q.length; i++) for (const u of nb[q[i]]) { if (u < 0 || gone[u]) continue; if (--deg[u] <= 1) { gone[u] = 1; q.push(u); } }
    const mir = k => { const x = k % W, y = (k / W) | 0; if (sym === 'y') return y * W + (W - 1 - x); if (sym === 'x') return (H - 1 - y) * W + x; if (sym === 'xy') return (H - 1 - y) * W + (W - 1 - x); return -1; };
    G = { W, H, N, nb, gone, mir };
    return G;
  };
  const plain = (g, k, di) => { const x = k % g.W, y = (k / g.W) | 0; return ((y + DY[di] + g.H) % g.H) * g.W + (x + DX[di] + g.W) % g.W; };
  let lastFront = 0;
  const view = (g, known, a, b) => {
    const par = new Map([[b, a]]), q = [b]; let unknown = false; lastFront = 0;
    for (let i = 0; i < q.length && q.length < 400; i++) {
      const t = q[i];
      for (let di = 0; di < 4; di++) {
        const pl = plain(g, t, di);
        if (!(known.has(t) || known.has(pl))) { unknown = true; lastFront++; continue; }
        const u = g.nb[t][di];
        if (u < 0 || u === a) continue;
        if (par.has(u)) { if (par.get(t) !== u) return 'cycle'; continue; }
        par.set(u, t); q.push(u);
      }
    }
    return unknown ? 'unknown' : 'dead';
  };
  const seenBy = new Map();
  const fam = process.argv.includes("--bymap") ? path.basename(path.dirname(file)).replace(/^proxy4_king_/, "").replace(/_[AB]_1$/, "").padEnd(14) : (path.basename(path.dirname(file)).includes("gen_") ? "generated" : "bundled");
  perGame(R, { map: '?', variant: 'a' }, {
    turn(d, round, ctx) {
      if (d.team !== us) return;
      const g = geo(ctx), h = d.body[0];
      let s = seenBy.get(d.id); if (!s) { s = new Set(); seenBy.set(d.id, s); }
      for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) { const k = ((h.y + dy + g.H) % g.H) * g.W + (h.x + dx + g.W) % g.W; s.add(k); if (MIRROR) { const m = g.mir(k); if (m >= 0) s.add(m); } }
    },
    action(d, e, round, ctx, hb) {
      if (d.team !== us || !e.action || e.action.kind !== 'move') return;
      const g = geo(ctx), a = hb[0].y * g.W + hb[0].x, b = d.body[0].y * g.W + d.body[0].x;
      if (!d.body.length || a === b) return;
      let di = -1; for (let k = 0; k < 4; k++) if (g.nb[a][k] === b) di = k;
      if (di < 0) return;   // a sprint or a portal step: skip
      const side1 = (di + 1) % 4, side2 = (di + 3) % 4;
      const corridor = g.nb[b][side1] < 0 && g.nb[b][side2] < 0;
      const known = seenBy.get(d.id) || new Set();
      const v = view(g, known, a, b), front = lastFront;
      let dens = '';
      if (process.argv.includes('--feat') && v === 'unknown') {
        let term = 0, n = 0;
        for (const k of known) { let all = true, open = 0; for (let q = 0; q < 4; q++) { const pl = plain(g, k, q); if (!(known.has(k) || known.has(pl))) all = false; if (g.nb[k][q] >= 0) open++; } if (!all) continue; n++; if (open === 1) term++; }
        const r = n ? term / n : 0;
        dens = ` front ${front >= 3 ? '3+' : front} termdens ${r < 0.02 ? '<2%' : r < 0.05 ? '2-5%' : r < 0.1 ? '5-10%' : '10%+'}`;
      }
      const truth = view(g, ALL, a, b) === 'cycle' ? 'open-ahead' : 'dead-ahead';
      add(`${fam} ${hb.length < 4 ? 'L<4 ' : 'L>=4'} ${corridor ? 'corridor' : 'open    '} ${v.padEnd(7)}${dens} truth ${truth}`);
    },
  });
}
const keys = Object.keys(tab).sort();
for (const k of keys) console.log(String(tab[k]).padStart(7) + '  ' + k);
