// 2-core of the tile graph (portals included): spawn tiles outside the 2-core sit in 1-wide dead-end branches.
const path = require('path');
const HR = '~/01. Project/개인 프로젝트/unsw-heuristic';
const { load } = require(path.join(HR, 'tools/replay.js'));
const R = load(process.argv[2]);
const M = R.match.map, W = M.width, H = M.height, N = W * H;
const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
const portal = new Map();
(M.portals || []).forEach(pr => { const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); });
const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
const DXa = { N: 0, E: 1, S: 0, W: -1 }, DYa = { N: -1, E: 0, S: 1, W: 0 };
function across(x, y, d, up) {
  let ek, kelp;
  if (d === 'N') { ek = x + ',' + y + ',N'; kelp = hk(x, y); } else if (d === 'S') { ek = x + ',' + wy(y + 1) + ',N'; kelp = hk(x, y + 1); }
  else if (d === 'W') { ek = x + ',' + y + ',W'; kelp = vk(x, y); } else { ek = wx(x + 1) + ',' + y + ',W'; kelp = vk(x + 1, y); }
  const p = portal.get(ek);
  if (p) { if (!up) return null; if (d === 'N') return { x: p.x, y: wy(p.y - 1), portal: true }; if (d === 'S') return { x: p.x, y: p.y, portal: true }; if (d === 'W') return { x: wx(p.x - 1), y: p.y, portal: true }; return { x: p.x, y: p.y, portal: true }; }
  if (kelp) return null; return { x: wx(x + DXa[d]), y: wy(y + DYa[d]) };
}
const nb = t => 'NESW'.split('').map(d => across(t % W, (t / W) | 0, d, true)).filter(Boolean).map(r => r.y * W + r.x);
const reg = new Int32Array(N).fill(-1), size = [];
for (let s = 0; s < N; s++) { if (reg[s] >= 0) continue; const q = [s]; reg[s] = size.length; for (let i = 0; i < q.length; i++) { const t = q[i]; for (const d of 'NESW') { const r = across(t % W, (t / W) | 0, d, false); if (!r) continue; const u = r.y * W + r.x; if (reg[u] < 0) { reg[u] = size.length; q.push(u); } } } size.push(q.length); }
const deg = new Int32Array(N), alive = new Uint8Array(N).fill(1);
for (let t = 0; t < N; t++) deg[t] = new Set(nb(t)).size;
const q = []; for (let t = 0; t < N; t++) if (deg[t] <= 1) q.push(t);
while (q.length) { const t = q.pop(); if (!alive[t]) continue; alive[t] = 0; for (const u of new Set(nb(t))) if (alive[u]) { deg[u]--; if (deg[u] <= 1) q.push(u); } }
const spawn = t => M.pearlRespawn[t].maxRounds > 0;
const byReg = new Map();
for (let t = 0; t < N; t++) { if (!spawn(t)) continue; const r = reg[t]; if (!byReg.has(r)) byReg.set(r, { n: 0, core: 0, rate: 0, rateCore: 0 }); const o = byReg.get(r); const rt = 2 / (M.pearlRespawn[t].minRounds + M.pearlRespawn[t].maxRounds); o.n++; o.rate += rt; if (alive[t]) { o.core++; o.rateCore += rt; } }
console.log(M.mapName);
for (const [r, o] of [...byReg].sort((a, b) => size[b[0]] - size[a[0]])) console.log(`reg${r} size ${size[r]} spawnTiles ${o.n} in2core ${o.core} rate ${o.rate.toFixed(2)} rateIn2core ${o.rateCore.toFixed(2)}`);
