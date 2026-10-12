// Trace portal crossings of one team's dragons in a replay: where they enter, where they land, what they do next.
// usage: node trace_portal.js <replay> <team A|B> [maxPrint]
const path = require('path');
const HR = '~/01. Project/개인 프로젝트/unsw-heuristic';
const { load } = require(path.join(HR, 'tools/replay.js'));
const R = load(process.argv[2]);
const TEAM = process.argv[3] || 'B', MAXP = +(process.argv[4] || 40);
const M = R.match.map, W = M.width, H = M.height;
const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
const portal = new Map();
(M.portals || []).forEach(pr => { if (pr.length !== 2) return; const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); });
const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
const DXa = { N: 0, E: 1, S: 0, W: -1 }, DYa = { N: -1, E: 0, S: 1, W: 0 };
function across(x, y, d) {
  let ek, kelp;
  if (d === 'N') { ek = x + ',' + y + ',N'; kelp = hk(x, y); }
  else if (d === 'S') { ek = x + ',' + wy(y + 1) + ',N'; kelp = hk(x, y + 1); }
  else if (d === 'W') { ek = x + ',' + y + ',W'; kelp = vk(x, y); }
  else { ek = wx(x + 1) + ',' + y + ',W'; kelp = vk(x + 1, y); }
  const p = portal.get(ek);
  if (p) {
    if (d === 'N') return { x: p.x, y: wy(p.y - 1), portal: true };
    if (d === 'S') return { x: p.x, y: p.y, portal: true };
    if (d === 'W') return { x: wx(p.x - 1), y: p.y, portal: true };
    return { x: p.x, y: p.y, portal: true };
  }
  if (kelp) return null;
  return { x: wx(x + DXa[d]), y: wy(y + DYa[d]) };
}
const team = new Map(), head = new Map();
for (const d of M.initialDragons) { team.set(d.id, d.team); head.set(d.id, d.body[0]); }
let round = 0, printed = 0, cross = 0; const log = [];
const lastCross = new Map();
for (const e of R.events) {
  if (e.type === 'roundStart') round = e.round;
  else if (e.type === 'dragonSplit') { team.set(e.childId, e.team); head.set(e.childId, e.childBody[0]); head.set(e.parentId, e.parentBody[0]); }
  else if (e.type === 'dragonUpdate') { head.set(e.id, e.head); }
  else if (e.type === 'dragonDeath') { if (team.get(e.id) === TEAM && lastCross.has(e.id) && round - lastCross.get(e.id).round <= 3) log.push(`  r${round} #${e.id} DIED ${e.reason} ${round - lastCross.get(e.id).round} rounds after crossing`); }
  else if (e.type === 'dragonAction' && team.get(e.id) === TEAM && e.action.kind === 'move') {
    let h = head.get(e.id); if (!h) continue;
    let s = `r${round} #${e.id} (${h.x},${h.y}) ${e.action.steps.join('')}`; let any = false;
    for (const d of e.action.steps) { const r = across(h.x, h.y, d); if (!r) { s += ' X'; break; } if (r.portal) { any = true; s += ` [P ${h.x},${h.y}->${r.x},${r.y}]`; } h = r; }
    if (any) { cross++; lastCross.set(e.id, { round }); if (printed < MAXP) { log.push(s); printed++; } }
  }
}
console.log(M.mapName, 'team', TEAM, 'crossing actions', cross);
console.log(log.slice(0, MAXP * 2).join('\n'));
