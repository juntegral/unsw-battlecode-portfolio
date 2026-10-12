// for crossings that land in a one-tile pocket: was the move before the crossing in the same direction (straight approach)?
const path = require('path'), fs = require('fs');
const HR = '~/01. Project/개인 프로젝트/unsw-heuristic';
const { load } = require(path.join(HR, 'tools/replay.js'));
let straight = 0, bent = 0, total = 0, splitAfter = 0; const perGame = [];
for (const dir of process.argv.slice(2)) for (const g of fs.readdirSync(dir + '/games')) {
  if (!/portals/.test(g)) continue;
  const US = /_A_/.test(g) ? 'A' : 'B';
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
  const team = new Map(), head = new Map(), lastDir = new Map(), pending = new Map(); let round = 0; const entries = new Map();
  for (const d of M.initialDragons) { team.set(d.id, d.team); head.set(d.id, d.body[0]); lastDir.set(d.id, d.facing); }
  for (const e of R.events) {
    if (e.type === 'roundStart') round = e.round;
    if (e.type === 'dragonSplit') { team.set(e.childId, e.team); head.set(e.childId, e.childBody[0]); head.set(e.parentId, e.parentBody[0]); lastDir.set(e.childId, e.childFacing); if (pending.has(e.parentId)) { splitAfter++; pending.delete(e.parentId); } }
    if (e.type === 'dragonUpdate') head.set(e.id, e.head);
    if (e.type === 'dragonAction' && e.action.kind === 'move' && team.get(e.id) === US) {
      let h = head.get(e.id); let prev = lastDir.get(e.id);
      for (const d of e.action.steps) { const nx = across(h.x, h.y, d); if (!nx) break; if (nx.portal && dead(nx, d)) { total++; const k = h.x + ',' + h.y + d; entries.set(k, (entries.get(k) || 0) + 1); if (prev === d) straight++; else bent++; pending.set(e.id, round); } prev = d; h = nx; }
      lastDir.set(e.id, e.action.steps[e.action.steps.length - 1]);
    }
  }
  perGame.push([g, [...entries.values()].reduce((a, b) => a + b, 0), entries.size]);
}
for (const p of perGame) console.log(p.join(' '));
console.log({ pocketLandings: total, straightApproach: straight, bentApproach: bent, escapeSplitAfter: splitAfter });
