#!/usr/bin/env node
// exp/portals v2: the rooms of each team's half: compartments over open edges, their tiles, spawn gaps, exits (portal edges) and where
// each exit leads (compartment id). Uses the same parse as genptmap.js. usage: node exp/portals/gen/rooms.js
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const L = fs.readFileSync(path.join(ROOT, 'maps/online-20260927/portals.map'), 'utf8').split('\n');
const [W, H] = /^MAP (\d+) (\d+)/.exec(L[0]).slice(1).map(Number), N = W * H;
const eN = new Array(N).fill(-1), eW = new Array(N).fill(-1), gap = new Array(N).fill(null), starts = [];
for (const l of L) { const t = l.trim().split(/\s+/);
  if (t[0] === 'EDGE') { const idx = +t[1], kind = +t[2], pid = +t[3], r = Math.floor(idx / (W + 1)), c = idx % (W + 1); if (c >= W || r >= 2 * H) continue; const tile = (r >> 1) * W + c, tok = kind === 1 ? -2 : kind === 2 ? pid : -1; if (r % 2 === 0) eN[tile] = tok; else eW[tile] = tok; }
  else if (t[0] === 'TILE') { const [x, y, mn, mx] = t.slice(1).map(Number); gap[y * W + x] = [mn, mx]; }
  else if (t[0] === 'DRAGON') { const team = +t[1], n = +t[2]; for (let i = 0; i < n; i++) starts.push([team, +t[4 + 2 * i] * W + +t[3 + 2 * i]]); } }
const wX = x => ((x % W) + W) % W, wY = y => ((y % H) + H) % H;
const step = (t, d) => { const x = t % W, y = (t / W) | 0; return [wY(y - 1) * W + x, y * W + wX(x + 1), wY(y + 1) * W + x, y * W + wX(x - 1)][d]; };
const tok = (t, d) => d === 0 ? eN[t] : d === 3 ? eW[t] : d === 2 ? eN[step(t, 2)] : eW[step(t, 1)];
const ends = new Map(); for (let t = 0; t < N; t++) { if (eN[t] >= 0) (ends.get(eN[t]) || ends.set(eN[t], []).get(eN[t])).push([t, 0]); if (eW[t] >= 0) (ends.get(eW[t]) || ends.set(eW[t], []).get(eW[t])).push([t, 3]); }
const canon = (t, d) => d === 0 ? [t, 0] : d === 3 ? [t, 3] : d === 2 ? [step(t, 2), 0] : [step(t, 1), 3];
const across = (t, d) => { const k = tok(t, d); if (k === -2) return -1; if (k === -1) return step(t, d); const [ct, cs] = canon(t, d), e = ends.get(k).find(([u, s]) => !(u === ct && s === cs)); return d === e[1] ? step(e[0], e[1]) : e[0]; };
const comp = new Array(N).fill(-1); let nc = 0;
for (let t = 0; t < N; t++) { if (comp[t] >= 0) continue; const st = [t]; comp[t] = nc; while (st.length) { const a = st.pop(); for (let d = 0; d < 4; d++) { if (tok(a, d) !== -1) continue; const u = step(a, d); if (comp[u] < 0) { comp[u] = nc; st.push(u); } } } nc++; }
const bfs = src => { const dist = new Array(N).fill(-1), q = []; for (const s of src) if (dist[s] < 0) { dist[s] = 0; q.push(s); } for (let i = 0; i < q.length; i++) { const t = q[i]; for (let d = 0; d < 4; d++) { const u = across(t, d); if (u >= 0 && dist[u] < 0) { dist[u] = dist[t] + 1; q.push(u); } } } return dist; };
const dA = bfs(starts.filter(s => s[0] === 0).map(s => s[1]));
const C = {};
for (let t = 0; t < N; t++) { const c = comp[t]; (C[c] = C[c] || { tiles: [], exits: [], spawn: 0, reachA: false }).tiles.push(t); if (gap[t] && gap[t][1] > 0) C[c].spawn++; if (dA[t] >= 0) C[c].reachA = true;
  for (let d = 0; d < 4; d++) if (tok(t, d) >= 0) { const u = across(t, d); C[c].exits.push({ from: `${t % W},${(t / W) | 0}`, dir: 'NESW'[d], to: `${u % W},${(u / W) | 0}`, toComp: comp[u] }); } }
const big = Object.entries(C).filter(([, v]) => v.tiles.length > 8).map(([k, v]) => `comp ${k}: ${v.tiles.length} tiles, reachA ${v.reachA}`);
console.log('large compartments:', big.join(' | '));
for (const [k, v] of Object.entries(C)) { if (v.tiles.length > 8 || !v.reachA) continue;
  const xy = v.tiles.map(t => `${t % W},${(t / W) | 0}`), gaps = [...new Set(v.tiles.map(t => gap[t] ? gap[t].join('-') : '0'))];
  console.log(`room ${k}: tiles ${xy.join(' ')} spawn ${v.spawn} gaps ${gaps.join('/')} exits ${v.exits.map(e => `${e.from}${e.dir}->${e.to}(c${e.toComp})`).join(' ')}`); }
