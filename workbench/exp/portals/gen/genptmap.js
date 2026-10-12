#!/usr/bin/env node
// Generates exp/portals/bot/ptmap.hpp from maps/online-20260927/portals.map: every tile's north and west edge in the protocol's
// token encoding (-2 kelp, -1 open, >= 0 portal id), plus static tables for the Portals module (ptmod.cpp):
//   PT_TERR  territory by movement distance from each file team's starting bodies ('1' file team A, '2' file team B, '0' neutral)
//   PT_DEAD  1 on a tile a long dragon must not enter: outside the 2-core of the movement graph, or inside a compartment (a set of
//            tiles joined by open edges and walled off from the rest except through portals) with a single way out.
// usage: node exp/portals/gen/genptmap.js [--check <replay>]   (--check compares the parsed edges with a replay's map)
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const L = fs.readFileSync(path.join(ROOT, 'maps/online-20260927/portals.map'), 'utf8').split('\n');
const [W, H] = /^MAP (\d+) (\d+)/.exec(L[0]).slice(1).map(Number);
const N = W * H;
const edgeN = new Array(N).fill(-1), edgeW = new Array(N).fill(-1);
const spawn = new Array(N).fill(null);
const starts = [];
for (const l of L) {
  const t = l.trim().split(/\s+/);
  if (t[0] === 'EDGE') {
    const idx = +t[1], kind = +t[2], pid = +t[3];
    const r = Math.floor(idx / (W + 1)), c = idx % (W + 1);
    if (c >= W || r >= 2 * H) continue;           // the east / south border repeats the west / north one
    const y = r >> 1, tile = y * W + c, tok = kind === 1 ? -2 : kind === 2 ? pid : -1;
    if (r % 2 === 0) edgeN[tile] = tok; else edgeW[tile] = tok;
  } else if (t[0] === 'TILE') { const [x, y, mn, mx] = t.slice(1).map(Number); spawn[y * W + x] = [mn, mx]; }
  else if (t[0] === 'DRAGON') { const team = +t[1], n = +t[2]; const b = []; for (let i = 0; i < n; i++) b.push([+t[3 + 2 * i], +t[4 + 2 * i]]); starts.push({ team, b }); }
}
// movement: across(t, d) as World::across with everything known
const wrapX = x => ((x % W) + W) % W, wrapY = y => ((y % H) + H) % H;
const step = (t, d) => { const x = t % W, y = (t / W) | 0; return [wrapY(y - 1) * W + x, y * W + wrapX(x + 1), wrapY(y + 1) * W + x, y * W + wrapX(x - 1)][d]; };
const edgeTok = (t, d) => d === 0 ? edgeN[t] : d === 3 ? edgeW[t] : d === 2 ? edgeN[step(t, 2)] : edgeW[step(t, 1)];
// portal ends by id: canonical (tile, side N=0 / W=3)
const ends = new Map();
for (let t = 0; t < N; t++) { if (edgeN[t] >= 0) (ends.get(edgeN[t]) || ends.set(edgeN[t], []).get(edgeN[t])).push([t, 0]); if (edgeW[t] >= 0) (ends.get(edgeW[t]) || ends.set(edgeW[t], []).get(edgeW[t])).push([t, 3]); }
const canon = (t, d) => d === 0 ? [t, 0] : d === 3 ? [t, 3] : d === 2 ? [step(t, 2), 0] : [step(t, 1), 3];
const across = (t, d) => {
  const tok = edgeTok(t, d);
  if (tok === -2) return -1;
  if (tok === -1) return step(t, d);
  const [ct, cs] = canon(t, d), e = ends.get(tok).find(([u, s]) => !(u === ct && s === cs));
  const opp = (d + 2) & 3;
  if (e[1] !== d && e[1] !== opp) throw Error('portal orientation');
  return d === e[1] ? step(e[0], e[1]) : e[0];
};
for (const [id, e] of ends) if (e.length !== 2) throw Error('portal ' + id + ' has ' + e.length + ' ends');
// territory by movement distance from each file team's starting bodies
const bfs = srcs => { const dist = new Array(N).fill(-1), q = []; for (const s of srcs) if (dist[s] < 0) { dist[s] = 0; q.push(s); } for (let i = 0; i < q.length; i++) { const t = q[i]; for (let d = 0; d < 4; d++) { const u = across(t, d); if (u >= 0 && dist[u] < 0) { dist[u] = dist[t] + 1; q.push(u); } } } return dist; };
const dA = bfs(starts.filter(s => s.team === 0).flatMap(s => s.b.map(([x, y]) => y * W + x))), dB = bfs(starts.filter(s => s.team === 1).flatMap(s => s.b.map(([x, y]) => y * W + x)));
const terr = new Array(N).fill('0'); for (let t = 0; t < N; t++) { const a = dA[t] < 0 ? 1e9 : dA[t], b = dB[t] < 0 ? 1e9 : dB[t]; terr[t] = a < b ? '1' : b < a ? '2' : '0'; }
// 2-core of the movement graph
const nb = []; for (let t = 0; t < N; t++) { const s = new Set(); for (let d = 0; d < 4; d++) { const u = across(t, d); if (u >= 0 && u !== t) s.add(u); } nb.push([...s]); }
const core = new Array(N).fill(1), deg = nb.map(a => a.length), q = []; for (let t = 0; t < N; t++) if (deg[t] < 2) q.push(t);
while (q.length) { const t = q.pop(); if (!core[t]) continue; core[t] = 0; for (const u of nb[t]) if (core[u] && --deg[u] < 2) q.push(u); }
// compartments: components over open (non-portal, non-kelp) edges; the ways out are the portal edges and open edges to other components
const comp = new Array(N).fill(-1); let nc = 0;
for (let t = 0; t < N; t++) { if (comp[t] >= 0) continue; const st = [t]; comp[t] = nc; while (st.length) { const a = st.pop(); for (let d = 0; d < 4; d++) { if (edgeTok(a, d) !== -1) continue; const u = step(a, d); if (comp[u] < 0) { comp[u] = nc; st.push(u); } } } nc++; }
const size = new Array(nc).fill(0), exits = Array.from({ length: nc }, () => new Set());
for (let t = 0; t < N; t++) { size[comp[t]]++; for (let d = 0; d < 4; d++) { const tok = edgeTok(t, d); if (tok >= 0) exits[comp[t]].add(t * 4 + d); } }
const dead = new Array(N).fill(0), room = new Array(N).fill(0), pocket = new Array(N).fill(0);
for (let t = 0; t < N; t++) { if (!core[t]) dead[t] = 1; else if (size[comp[t]] <= 8 && exits[comp[t]].size <= 1) dead[t] = 1; if (dead[t] || size[comp[t]] <= 8) room[t] = 1; if (size[comp[t]] === 1 && exits[comp[t]].size >= 1) pocket[t] = 1; }
// U-rooms: 2 x 2 compartments with two portal exits into open water. uexit[t * 4 + d] = the far mouth for a step from open-water tile t across
// edge d into a U-room (enter at one mouth, leave at the other after 5 moves), else -1 (analysis only since the v2 A2 rule was rejected).
const uexit = new Array(N * 4).fill(-1);
for (let t = 0; t < N; t++) for (let d = 0; d < 4; d++) {
  if (room[t]) continue;
  const u = across(t, d); if (u < 0 || size[comp[u]] !== 4 || exits[comp[u]].size !== 2) continue;
  const ex = [...exits[comp[u]]].map(k => [Math.floor(k / 4), k % 4]);   // (room tile, dir) of each exit edge
  const far = ex.find(([rt]) => rt !== u); if (!far) continue;
  uexit[t * 4 + d] = across(far[0], far[1]);
}
// report
const byComp = {}; for (let t = 0; t < N; t++) if (size[comp[t]] <= 8) { const c = comp[t]; (byComp[c] = byComp[c] || { tiles: [], exits: exits[c].size }).tiles.push(`${t % W},${(t / W) | 0}`); }
const small = Object.values(byComp);
console.error(`room ${room.reduce((a, b) => a + b, 0)}, pocket ${pocket.reduce((a, b) => a + b, 0)}, U-room entries ${uexit.filter(x => x >= 0).length}, tiles ${N}, portals ${ends.size}, 2-core ${core.reduce((a, b) => a + b, 0)}, compartments <= 8 tiles: ${small.length} (exits: ${JSON.stringify(small.map(c => c.exits))}), dead ${dead.reduce((a, b) => a + b, 0)}`);
console.error('territory A/B/neutral', ['1', '2', '0'].map(c => terr.filter(x => x === c).length).join('/'));
let pic = ''; for (let y = 0; y < H; y++) { for (let x = 0; x < W; x++) { const t = y * W + x; const sp = spawn[t] && spawn[t][1] > 0; pic += dead[t] ? (sp ? 'D' : 'd') : sp ? (terr[t] === '1' ? 'A' : terr[t] === '2' ? 'B' : 'N') : terr[t] === '1' ? '.' : terr[t] === '2' ? ':' : ' '; } pic += '\n'; }
console.error(pic);
// --check against a replay's map
const ci = process.argv.indexOf('--check');
if (ci > 0) {
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
  const M = makeLoader(viewerSource())(path.resolve(process.argv[ci + 1])).match.map;
  let bad = 0;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const t = y * W + x;
    if ((M.initialHEdges[y * W + x] === 1) !== (edgeN[t] === -2)) bad++;
    if ((M.initialVEdges[y * (W + 1) + x] === 1) !== (edgeW[t] === -2)) bad++;
  }
  const key = e => { const c = e.side === 'S' ? [e.x, wrapY(e.y + 1), 0] : e.side === 'E' ? [wrapX(e.x + 1), e.y, 3] : [e.x, e.y, e.side === 'N' ? 0 : 3]; return c[1] * W + c[0] + ':' + c[2]; };
  let pbad = 0;
  for (const pr of M.portals) { const a = key(pr[0]).split(':'), b = key(pr[1]).split(':'); const ta = +a[0], da = +a[1], tb = +b[0], db = +b[1]; const ia = da === 0 ? edgeN[ta] : edgeW[ta], ib = db === 0 ? edgeN[tb] : edgeW[tb]; if (ia < 0 || ia !== ib) pbad++; }
  console.error(`check: kelp mismatches ${bad}, portal pairs ${M.portals.length}, pair mismatches ${pbad}`);
}
// header
const arr = a => a.join(',');
const out = `// ptmap.hpp — generated by exp/portals/gen/genptmap.js from maps/online-20260927/portals.map. Do not edit.
// The Portals map (32 x 16) for the Portals module (ptmod.cpp): every tile's north and west edge as the protocol sends them (-2 kelp,
// -1 open, >= 0 portal id; Planner::ptExit reads where a portal leads even before this process has seen its far end). DEAD: 1 on a tile a
// long dragon must not enter (outside the 2-core of the movement graph, or in a walled compartment of <= 8 tiles with one way out).
#pragma once
#include <cstdint>
namespace seed0 { namespace ptmap {
constexpr int W = ${W}, H = ${H};
static const int16_t EDGE_N[${N}] = {${arr(edgeN)}};
static const int16_t EDGE_W[${N}] = {${arr(edgeW)}};
static const uint8_t DEAD[${N}] = {${arr(dead)}};
// ROOM: DEAD or any walled compartment of <= 8 tiles (the 2 x 2 rooms, pass-through ones included; a long dragon inside one depends on
// what stands across its portals, which it cannot see)
static const uint8_t ROOM[${N}] = {${arr(room)}};
// POCKET: a one-tile compartment with a portal exit (a head that enters cannot leave; exp/portals v2).
static const uint8_t POCKET[${N}] = {${arr(pocket)}};${process.argv.includes('--uexit') ? `
// UEXIT[t * 4 + d]: the far mouth of the U-room a step from t across d enters (-1 otherwise; exp/portals v3 X2)
static const int16_t UEXIT[${N * 4}] = {${arr(uexit)}};` : ''}
// EXIT[t * 4 + d]: the tile across edge d of t (-1 kelp), portals resolved (Planner::ptExit in O(1))
static const int16_t EXIT[${N * 4}] = {${arr(Array.from({ length: N * 4 }, (_, i) => across(i >> 2, i & 3)))}};
} }
`;
const oi = process.argv.indexOf('--out'); const OUTD = oi > 0 ? path.resolve(process.argv[oi + 1]) : path.join(ROOT, 'exp/portals/bot');
if (!(oi > 0)) { console.error('v2 tables need --out <bot dir> (the v1 bot keeps its table)'); }
else fs.writeFileSync(path.join(OUTD, 'ptmap.hpp'), out);
fs.writeFileSync(path.join(ROOT, 'exp/portals/gen/ptmap.json'), JSON.stringify({ W, H, dead, room, terr, core, spawn: spawn.map(g => g && g[1] > 0 ? 1 : 0), compSize: comp.map(c => size[c]), compExits: comp.map(c => exits[c].size) }));
console.error(oi > 0 ? 'wrote ' + OUTD + '/ptmap.hpp' : 'no header written');
