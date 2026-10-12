// rays that leave a tile through an adjacent portal edge: where they stop, split by the kind of place behind the portal
// (one-tile pocket vs anything else). Shows what a probe can and cannot tell.
const path = require('path'), fs = require('fs');
const HR = '~/01. Project/개인 프로젝트/unsw-heuristic';
const { load } = require(path.join(HR, 'tools/replay.js'));
const stat = {};
for (const dir of process.argv.slice(2)) for (const g of fs.readdirSync(dir + '/games')) {
  const R = load(dir + '/games/' + g + '/game.replay'); const M = R.match.map, W = M.width, H = M.height;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
  const portal = new Map(); (M.portals || []).forEach(pr => { const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); });
  const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
  const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
  const DXa = { N: 0, E: 1, S: 0, W: -1 }, DYa = { N: -1, E: 0, S: 1, W: 0 };
  const across = (x, y, d) => { let ek, kelp; if (d === 'N') { ek = x + ',' + y + ',N'; kelp = hk(x, y); } else if (d === 'S') { ek = x + ',' + wy(y + 1) + ',N'; kelp = hk(x, y + 1); } else if (d === 'W') { ek = x + ',' + y + ',W'; kelp = vk(x, y); } else { ek = wx(x + 1) + ',' + y + ',W'; kelp = vk(x + 1, y); }
    const p = portal.get(ek); if (p) { if (d === 'N') return { x: p.x, y: wy(p.y - 1), portal: true }; if (d === 'S') return { x: p.x, y: p.y, portal: true }; if (d === 'W') return { x: wx(p.x - 1), y: p.y, portal: true }; return { x: p.x, y: p.y, portal: true }; }
    if (kelp) return null; return { x: wx(x + DXa[d]), y: wy(y + DYa[d]) }; };
  const back = { N: 'S', S: 'N', E: 'W', W: 'E' };
  const dead = (t, d) => ['N', 'E', 'S', 'W'].filter(e => e !== back[d] && across(t.x, t.y, e)).length === 0;
  for (const e of R.events) {
    if (e.type !== 'sonarPing' || !e.origin) continue;
    const nx = across(e.origin.x, e.origin.y, e.direction); if (!nx || !nx.portal) continue;
    const kind = (M.mapName) + ' ' + (dead(nx, e.direction) ? 'pocket' : 'other');
    const where = (e.end && e.end.x === nx.x && e.end.y === nx.y) ? 'stopAtExit' : 'further';
    const k = kind + ' | ' + e.hitKind + ' ' + where; stat[k] = (stat[k] || 0) + 1;
  }
}
for (const k of Object.keys(stat).sort()) console.log(k, stat[k]);
