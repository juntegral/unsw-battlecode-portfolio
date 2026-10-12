// Render a map from a replay: kelp, portals (with ids), spawn tiles, start dragons; regions without portals.
// usage: node mapview.js <replay file>
const path = require('path');
const HR = '~/01. Project/개인 프로젝트/unsw-heuristic';
const { load } = require(path.join(HR, 'tools/replay.js'));
const R = load(process.argv[2]);
const M = R.match.map, W = M.width, H = M.height, N = W * H;
const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
const portal = new Map(), pid = new Map();
(M.portals || []).forEach((pr, i) => { if (pr.length !== 2) return; const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); pid.set(a.x + ',' + a.y + ',' + a.side, i); pid.set(b.x + ',' + b.y + ',' + b.side, i); });
const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
const DIRS = 'NESW', DXa = { N: 0, E: 1, S: 0, W: -1 }, DYa = { N: -1, E: 0, S: 1, W: 0 };
function edgeKey(x, y, d) {
  if (d === 'N') return x + ',' + y + ',N';
  if (d === 'S') return x + ',' + wy(y + 1) + ',N';
  if (d === 'W') return x + ',' + y + ',W';
  return wx(x + 1) + ',' + y + ',W';
}
function across(x, y, d, usePortal = true) {
  const ek = edgeKey(x, y, d);
  const kelp = d === 'N' ? hk(x, y) : d === 'S' ? hk(x, y + 1) : d === 'W' ? vk(x, y) : vk(x + 1, y);
  const p = portal.get(ek);
  if (p) {
    if (!usePortal) return null;
    if (d === 'N') return { x: p.x, y: wy(p.y - 1), portal: true };
    if (d === 'S') return { x: p.x, y: p.y, portal: true };
    if (d === 'W') return { x: wx(p.x - 1), y: p.y, portal: true };
    return { x: p.x, y: p.y, portal: true };
  }
  if (kelp) return null;
  return { x: wx(x + DXa[d]), y: wy(y + DYa[d]) };
}
// regions without portals
const reg = new Int32Array(N).fill(-1); let nreg = 0;
for (let s = 0; s < N; s++) {
  if (reg[s] >= 0) continue;
  const q = [s]; reg[s] = nreg;
  for (let i = 0; i < q.length; i++) { const t = q[i], x = t % W, y = (t / W) | 0; for (const d of DIRS) { const r = across(x, y, d, false); if (!r) continue; const u = r.y * W + r.x; if (reg[u] < 0) { reg[u] = nreg; q.push(u); } } }
  nreg++;
}
const spawn = t => M.pearlRespawn[t] && M.pearlRespawn[t].maxRounds > 0;
const regInfo = Array.from({ length: nreg }, () => ({ tiles: 0, spawn: 0, gapSum: 0, heads: [], portalsOut: new Map() }));
for (let t = 0; t < N; t++) { const r = regInfo[reg[t]]; r.tiles++; if (spawn(t)) { r.spawn++; r.gapSum += 2 / (M.pearlRespawn[t].minRounds + M.pearlRespawn[t].maxRounds); } }
for (const d0 of M.initialDragons) { const h = d0.body[0]; regInfo[reg[h.y * W + h.x]].heads.push(d0.team + d0.id); }
for (let t = 0; t < N; t++) { const x = t % W, y = (t / W) | 0; for (const d of DIRS) { const r = across(x, y, d, true); if (!r || !r.portal) continue; const u = r.y * W + r.x; const k = reg[u]; const m = regInfo[reg[t]].portalsOut; m.set(k, (m.get(k) || 0) + 1); } }
// ascii
const g = [];
for (let y = 0; y <= 2 * H; y++) g.push(Array(2 * W + 1).fill(' '));
const regCh = r => 'abcdefghijklmnopqrstuvwxyz0123456789'[r % 36];
for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
  const t = y * W + x; g[2 * y + 1][2 * x + 1] = spawn(t) ? '*' : regCh(reg[t]);
  // N edge
  const nk = edgeKey(x, y, 'N'); g[2 * y][2 * x + 1] = pid.has(nk) ? 'P' : hk(x, y) ? '-' : ' ';
  const wk = edgeKey(x, y, 'W'); g[2 * y + 1][2 * x] = pid.has(wk) ? 'P' : vk(x, y) ? '|' : ' ';
  g[2 * y][2 * x] = '+';
}
for (const d0 of M.initialDragons) d0.body.forEach((b, i) => { g[2 * b.y + 1][2 * b.x + 1] = i === 0 ? d0.team : d0.team.toLowerCase(); });
console.log(M.mapName, W + 'x' + H, 'sym', M.symmetry, 'portals', (M.portals || []).length);
console.log(g.map(r => r.join('')).join('\n'));
regInfo.forEach((r, i) => { if (r.tiles > 1 || r.spawn) console.log('region', regCh(i), 'tiles', r.tiles, 'spawnTiles', r.spawn, 'spawnRate/rd', r.gapSum.toFixed(2), 'heads', r.heads.join(','), 'portals->', [...r.portalsOut].map(([k, c]) => regCh(k) + ':' + c).join(' ')); });
// portal list
(M.portals || []).forEach((pr, i) => { const a = pr[0], b = pr[1]; const ta = a.y * W + a.x, tb = b.y * W + b.x; console.log('portal', i, JSON.stringify(a), JSON.stringify(b)); });
