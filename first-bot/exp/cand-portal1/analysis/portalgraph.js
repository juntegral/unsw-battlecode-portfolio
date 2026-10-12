// For the start region of team A (and B): each portal step out of it, what region it leads to, that region's spawn tiles,
// and whether it is a dead end (no other exit back to a big region) or a tunnel.
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
function across(x, y, d, up = true) {
  let ek, kelp;
  if (d === 'N') { ek = x + ',' + y + ',N'; kelp = hk(x, y); }
  else if (d === 'S') { ek = x + ',' + wy(y + 1) + ',N'; kelp = hk(x, y + 1); }
  else if (d === 'W') { ek = x + ',' + y + ',W'; kelp = vk(x, y); }
  else { ek = wx(x + 1) + ',' + y + ',W'; kelp = vk(x + 1, y); }
  const p = portal.get(ek);
  if (p) { if (!up) return null; if (d === 'N') return { x: p.x, y: wy(p.y - 1), portal: true }; if (d === 'S') return { x: p.x, y: p.y, portal: true }; if (d === 'W') return { x: wx(p.x - 1), y: p.y, portal: true }; return { x: p.x, y: p.y, portal: true }; }
  if (kelp) return null;
  return { x: wx(x + DXa[d]), y: wy(y + DYa[d]) };
}
const reg = new Int32Array(N).fill(-1), size = [], spawnN = [], rate = [];
for (let s = 0; s < N; s++) { if (reg[s] >= 0) continue; const q = [s]; reg[s] = size.length; for (let i = 0; i < q.length; i++) { const t = q[i]; for (const d of 'NESW') { const r = across(t % W, (t / W) | 0, d, false); if (!r) continue; const u = r.y * W + r.x; if (reg[u] < 0) { reg[u] = size.length; q.push(u); } } }
  size.push(q.length); spawnN.push(q.filter(t => M.pearlRespawn[t].maxRounds > 0).length); rate.push(q.reduce((s, t) => s + (M.pearlRespawn[t].maxRounds > 0 ? 2 / (M.pearlRespawn[t].minRounds + M.pearlRespawn[t].maxRounds) : 0), 0)); }
// exits of each region: list of (from tile, dir, to region)
const exits = size.map(() => []);
for (let t = 0; t < N; t++) for (const d of 'NESW') { const r = across(t % W, (t / W) | 0, d); if (r && r.portal) exits[reg[t]].push({ from: t, d, to: reg[r.y * W + r.x], toT: r.y * W + r.x }); }
const P = t => `(${t % W},${(t / W) | 0})`;
for (const team of ['A', 'B']) {
  const heads = M.initialDragons.filter(d => d.team === team).map(d => d.body[0].y * W + d.body[0].x);
  const home = [...new Set(heads.map(t => reg[t]))];
  console.log(`team ${team} home regions`, home.map(r => `reg${r} size ${size[r]} spawn ${spawnN[r]} rate ${rate[r].toFixed(2)}`).join('; '));
  for (const h of home) {
    const byTo = new Map();
    for (const e of exits[h]) { if (!byTo.has(e.to)) byTo.set(e.to, []); byTo.get(e.to).push(e); }
    for (const [to, es] of byTo) {
      const back = exits[to].map(e => e.to);
      console.log(`  -> reg${to} size ${size[to]} spawn ${spawnN[to]} rate ${rate[to].toFixed(2)} via ${es.map(e => P(e.from) + e.d + '->' + P(e.toT)).join(' ')} | its exits -> ${exits[to].map(e => 'reg' + e.to + '(' + size[e.to] + ')').join(',')}`);
    }
  }
}
