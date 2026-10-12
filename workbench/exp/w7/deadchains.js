#!/usr/bin/env node
// W15a diagnosis: dead chains of a map (tiles that leave the 2-core of the passable graph: corridors ending in a terminus, kelp only; portals are
// passable) and, per replay, how our dragons that died in one got there: the turn their head first stepped from outside the chain into it
// (entry), the chain's depth there (steps to the terminus), whether the terminus was in the 7x7 window then (Chebyshev <= 3: the end could be
// seen), whether a pearl lay in the chain (natural or a death drop: bait), the dragon's length, and whether it was born inside the chain.
// usage: node exp/w7/deadchains.js <map file> [<replay> <us A|B> ...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const args = process.argv.slice(2), mapFile = args[0];
// map graph
const L = fs.readFileSync(mapFile, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
let W = 0, H = 0; const edges = [];
for (const l of L) { const t = l.split(/\s+/); if (t[0] === 'MAP') { W = +t[1]; H = +t[2]; } else if (t[0] === 'EDGE') edges.push([+t[1], +t[2], +t[3]]); }
const N = W * H, nk = new Uint8Array(N), wk = new Uint8Array(N), portalOf = new Map();
for (const [i, kind, pid] of edges) { const r = Math.floor(i / (W + 1)), c = i % (W + 1); let k, side; if (r % 2 === 0) { k = ((r / 2) % H) * W + c % W; side = 'N'; nk[k] = kind; } else { k = ((r - 1) / 2) * W + c % W; side = 'W'; wk[k] = kind; } if (kind === 2) { const a = portalOf.get(pid) || []; a.push([k, side]); portalOf.set(pid, a); } }
const DX = { N: 0, S: 0, E: 1, W: -1 }, DY = { N: -1, S: 1, E: 0, W: 0 };
const nb = (k, d) => {   // neighbour across side d, or -1 (kelp); portals: the paired tile
  const x = k % W, y = (k / W) | 0;
  let kind, edgeTile, side;
  if (d === 'N') { kind = nk[k]; edgeTile = k; side = 'N'; } else if (d === 'S') { edgeTile = ((y + 1) % H) * W + x; kind = nk[edgeTile]; side = 'N'; }
  else if (d === 'W') { kind = wk[k]; edgeTile = k; side = 'W'; } else { edgeTile = y * W + (x + 1) % W; kind = wk[edgeTile]; side = 'W'; }
  if (kind === 1) return -1;
  if (kind === 2) {   // through the portal: the other end's tile on the far side
    for (const ends of portalOf.values()) { const i = ends.findIndex(([t, s]) => t === edgeTile && s === side); if (i < 0) continue; const [t2, s2] = ends[1 - i];
      const x2 = t2 % W, y2 = (t2 / W) | 0; if (s2 === 'N') return d === 'N' ? ((y2 - 1 + H) % H) * W + x2 : t2; return d === 'W' ? y2 * W + (x2 - 1 + W) % W : t2; }
    return -1;
  }
  return ((y + DY[d] + H) % H) * W + (x + DX[d] + W) % W;
};
const deg = new Int32Array(N), gone = new Uint8Array(N); const q = [];
for (let k = 0; k < N; k++) { for (const d of ['N', 'E', 'S', 'W']) if (nb(k, d) >= 0) deg[k]++; if (deg[k] <= 1) { gone[k] = 1; q.push(k); } }
for (let i = 0; i < q.length; i++) for (const d of ['N', 'E', 'S', 'W']) { const u = nb(q[i], d); if (u < 0 || gone[u]) continue; if (--deg[u] <= 1) { gone[u] = 1; q.push(u); } }
// depth: steps to the farthest terminus inside the chain (BFS from termini over gone tiles)
const term = []; for (let k = 0; k < N; k++) if (gone[k]) { let c = 0; for (const d of ['N', 'E', 'S', 'W']) if (nb(k, d) >= 0) c++; if (c <= 1) term.push(k); }
const toTerm = new Int32Array(N).fill(-1); const q2 = [...term]; for (const t of term) toTerm[t] = 0;
for (let i = 0; i < q2.length; i++) for (const d of ['N', 'E', 'S', 'W']) { const u = nb(q2[i], d); if (u < 0 || !gone[u] || toTerm[u] >= 0) continue; toTerm[u] = toTerm[q2[i]] + 1; q2.push(u); }
const offCore = gone.reduce((a, b) => a + b, 0);
console.log(`${path.basename(mapFile)} ${W}x${H}: off-core (dead-chain) tiles ${offCore} (${(100 * offCore / N).toFixed(0)}%), termini ${term.length}`);
for (let i = 1; i + 1 < args.length; i += 2) {
  const file = args[i], us = args[i + 1];
  const R = makeLoader(viewerSource())(file);
  const where = new Map();   // dragon id -> {entry: {...} | null, bornIn}
  const out = { deaths: 0, inChain: 0, bornIn: 0, entered: 0, seenEnd: 0, bait: 0, depth: [], len: [] };
  perGame(R, { map: '?', variant: 'a' }, {
    split(p, ch, e, round) { if (ch.team !== us) return; const h = ch.body[0], k = h.y * W + h.x; where.set(ch.id, { bornIn: !!gone[k], entry: null }); },
    action(d, e, round, ctx, hb) {
      if (d.team !== us || !e.action || e.action.kind !== 'move') return;
      const h0 = hb[0], k0 = h0.y * W + h0.x, h1 = d.body[0], k1 = h1.y * W + h1.x;
      const w = where.get(d.id) || { bornIn: false, entry: null }; where.set(d.id, w);
      if (gone[k1] && !gone[k0] && !w.entry) {
        let tx = -1, ty = -1, best = 99; for (const t of term) { const dx = Math.abs(t % W - h1.x), dy = Math.abs(((t / W) | 0) - h1.y); const c = Math.max(Math.min(dx, W - dx), Math.min(dy, H - dy)); if (c < best) { best = c; tx = t % W; ty = (t / W) | 0; } }
        let bait = false; for (const [pk] of ctx.pearls) if (gone[pk]) { const dx = Math.abs(pk % W - h1.x), dy = Math.abs(((pk / W) | 0) - h1.y); if (Math.min(dx, W - dx) + Math.min(dy, H - dy) <= toTerm[k1] + 1) { bait = true; break; } }
        w.entry = { round, depth: toTerm[k1], seenEnd: best <= 3, bait, len: hb.length };
      }
      if (!gone[k1]) w.entry = null;   // left the chain again
    },
    death(d, rec) {
      if (d.team !== us) return; out.deaths++;
      const h = d.body[0], k = h.y * W + h.x; if (!gone[k]) return;
      out.inChain++; const w = where.get(d.id) || { bornIn: false, entry: null };
      if (w.entry) { out.entered++; if (w.entry.seenEnd) out.seenEnd++; if (w.entry.bait) out.bait++; out.depth.push(w.entry.depth); out.len.push(w.entry.len); }
      else if (w.bornIn) out.bornIn++;
    },
  });
  const med = a => { const s = a.slice().sort((x, y) => x - y); return s.length ? s[s.length >> 1] : '-'; };
  console.log(`  ${path.basename(path.dirname(file))}: our deaths ${out.deaths}, in a dead chain ${out.inChain}: born inside ${out.bornIn}, walked in ${out.entered} (end in view at entry ${out.seenEnd}, a pearl in the chain ${out.bait}; depth at entry median ${med(out.depth)}, length median ${med(out.len)})`);
}
