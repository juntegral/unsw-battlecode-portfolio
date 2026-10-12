#!/usr/bin/env node
// W15a: which maps start a dragon inside a dead branch (its r0 head off the 2-core of the true graph, portals included), with the dragon's
// length, its head and tail, and whether its tail is off the core too (the Autarky / Dilemma column: both ends in pockets).
// usage: node exp/w15a/pocketmaps.js <map files...>
'use strict';
const fs = require('fs'), path = require('path');
for (const file of process.argv.slice(2)) {
  const L = fs.readFileSync(file, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  let W = 0, H = 0; const edges = [], drag = [];
  for (const l of L) { const t = l.split(/\s+/); if (t[0] === 'MAP') { W = +t[1]; H = +t[2]; } else if (t[0] === 'EDGE') edges.push([+t[1], +t[2], +t[3]]); else if (t[0] === 'DRAGON') { const team = t[1], n = +t[2], body = []; for (let i = 0; i < n; i++) body.push([+t[3 + 2 * i], +t[4 + 2 * i]]); drag.push({ team, body }); } }
  const N = W * H, nk = new Uint8Array(N), wk = new Uint8Array(N), portalOf = new Map();
  for (const [i, kind, pid] of edges) { const r = Math.floor(i / (W + 1)), c = i % (W + 1); let k, side; if (r % 2 === 0) { k = ((r / 2) % H) * W + c % W; side = 'N'; nk[k] = kind; } else { k = ((r - 1) / 2) * W + c % W; side = 'W'; wk[k] = kind; } if (kind === 2) { const a = portalOf.get(pid) || []; a.push([k, side]); portalOf.set(pid, a); } }
  const DX = { N: 0, S: 0, E: 1, W: -1 }, DY = { N: -1, S: 1, E: 0, W: 0 };
  const nb = (k, d) => { const x = k % W, y = (k / W) | 0; let kind, edgeTile, side;
    if (d === 'N') { kind = nk[k]; edgeTile = k; side = 'N'; } else if (d === 'S') { edgeTile = ((y + 1) % H) * W + x; kind = nk[edgeTile]; side = 'N'; }
    else if (d === 'W') { kind = wk[k]; edgeTile = k; side = 'W'; } else { edgeTile = y * W + (x + 1) % W; kind = wk[edgeTile]; side = 'W'; }
    if (kind === 1) return -1;
    if (kind === 2) { for (const ends of portalOf.values()) { const i = ends.findIndex(([t, s]) => t === edgeTile && s === side); if (i < 0) continue; const [t2, s2] = ends[1 - i]; const x2 = t2 % W, y2 = (t2 / W) | 0; if (s2 === 'N') return d === 'N' ? ((y2 - 1 + H) % H) * W + x2 : t2; return d === 'W' ? y2 * W + (x2 - 1 + W) % W : t2; } return -1; }
    return ((y + DY[d] + H) % H) * W + (x + DX[d] + W) % W; };
  const deg = new Int32Array(N), gone = new Uint8Array(N), q = [];
  for (let k = 0; k < N; k++) { for (const d of 'NESW') if (nb(k, d) >= 0) deg[k]++; if (deg[k] <= 1) { gone[k] = 1; q.push(k); } }
  for (let i = 0; i < q.length; i++) for (const d of 'NESW') { const u = nb(q[i], d); if (u < 0 || gone[u]) continue; if (--deg[u] <= 1) { gone[u] = 1; q.push(u); } }
  const hits = drag.filter(d => gone[d.body[0][1] * W + d.body[0][0]]).map(d => { const t = d.body[d.body.length - 1]; return `team ${d.team} L${d.body.length} head ${d.body[0]} tail ${t}${gone[t[1] * W + t[0]] ? ' (tail in a branch too)' : ''}`; });
  if (hits.length) console.log(`${path.basename(file)}: ${hits.join('; ')}`);
}
