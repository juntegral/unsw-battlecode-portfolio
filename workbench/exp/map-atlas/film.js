// film.js — a compact timeline of one replay for the atlas's deep reads (Claude, 2026-10-01).
// usage: node exp/map-atlas/film.js <task key> [step=25]
// Per window of <step> rounds and team: living heads and longest at the window start, total length, heads standing in the
// enemy's territory (path-distance Voronoi from the start bodies), the longest's nearest enemy head (path distance); during the
// window: splits (children <= 3), deaths (head-on = either side of a head-to-head; own-move = the mover died on its own step:
// kelp, itself, a body of either team, a suicide or an unpaid sprint), pearls eaten (natural / dropped, of which dropped by our
// own dead). Events: king (longest >= 8) deaths, eliminations.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../..'), OUT = path.join(__dirname, 'cache');
const raw = require(path.join(ROOT, 'legacy/exp/intake-gap/rawload.js'));
const { buildGraph } = require('./recount.js');
const key = process.argv[2], step = +(process.argv[3] || 25);
const task = fs.readFileSync(path.join(OUT, 'tasks.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).find(t => t.key === key);
if (!task) throw Error('no task ' + key);
const R = raw.load(task.file), M = R.match.map, W = M.width, G = buildGraph(M), ix = p => p.y * W + p.x;
const bfs = seeds => { const d = new Int32Array(G.N).fill(-1), q = []; for (const s of seeds) if (d[s] < 0) { d[s] = 0; q.push(s); } for (let i = 0; i < q.length; i++) { const k = q[i]; for (let z = 0; z < 4; z++) { const v = G.nb[k * 4 + z]; if (v >= 0 && d[v] < 0) { d[v] = d[k] + 1; q.push(v); } } } return d; };
const dA = bfs(M.initialDragons.filter(d => d.team === 'A').flatMap(d => d.body.map(ix))), dB = bfs(M.initialDragons.filter(d => d.team === 'B').flatMap(d => d.body.map(ix)));
const terr = k => { const a = dA[k] < 0 ? 1e9 : dA[k], b = dB[k] < 0 ? 1e9 : dB[k]; return a < b ? 'A' : b < a ? 'B' : '-'; };
const team = new Map(), len = new Map(), head = new Map(), alive = { A: new Set(), B: new Set() };
for (const d of M.initialDragons) { team.set(d.id, d.team); len.set(d.id, d.body.length); head.set(d.id, ix(d.body[0])); alive[d.team].add(d.id); }
const pearl = new Int8Array(W * M.height); for (let k = 0; k < W * M.height; k++) if (M.initialTiles[k] === 2) pearl[k] = 1;
const blank = () => ({ splits: 0, small: 0, dEnemy: 0, dOwn: 0, headOn: 0, nat: 0, drop: 0, dropOwn: 0 });
let win = { A: blank(), B: blank() }, round = -1, cur = -1, updates = 0, block = '', lastDeath = null;
const rows = [], events = [];
const kingOf = t => { let kid = -1, kl = 0; for (const id of alive[t]) { const L = len.get(id); if (L > kl || (L === kl && id < kid)) { kl = L; kid = id; } } return [kid, kl]; };
const dropOwner = new Map();
const snap = r => {
  const s = { r };
  for (const t of ['A', 'B']) {
    const [kid, kl] = kingOf(t); let tot = 0, raid = 0; for (const id of alive[t]) { tot += len.get(id); if (terr(head.get(id)) === (t === 'A' ? 'B' : 'A')) raid++; }
    let near = null; if (kid >= 0) { const d = bfs([head.get(kid)]); let b = 999; for (const id of alive[t === 'A' ? 'B' : 'A']) { const x = d[head.get(id)]; if (x >= 0 && x < b) b = x; } near = b; }
    s[t] = { heads: alive[t].size, king: kl, total: tot, raid, near };
  }
  return s;
};
let pending = snap(0);
for (const e of R.events) {
  if (e.type === 'roundStart') {
    round = e.round; block = 'round';
    if (round > 0 && round % step === 0) { pending.win = win; rows.push(pending); win = { A: blank(), B: blank() }; pending = snap(round); }
    continue;
  }
  if (e.type === 'tileChange' && e.hasPearl) { const k = ix(e.tile); if (block === 'death') { pearl[k] = 2; dropOwner.set(k, lastDeath); } else pearl[k] = 1; continue; }
  if (e.type !== 'tileChange') block = e.type === 'dragonDeath' ? 'death' : '';
  if (e.type === 'turnStart') { cur = e.id; updates = 0; continue; }
  if (e.type === 'tileChange') {
    const k = ix(e.tile), t = team.get(cur); len.set(cur, len.get(cur) + 1);
    if (pearl[k] === 1) win[t].nat++; else if (pearl[k] === 2) { win[t].drop++; if (dropOwner.get(k) === t) win[t].dropOwn++; }
    pearl[k] = 0; continue;
  }
  if (e.type === 'dragonUpdate') { if (round < 0) continue; updates++; if (updates > 1) len.set(e.id, len.get(e.id) - 1); head.set(e.id, ix(e.head)); continue; }
  if (e.type === 'dragonSplit') { len.set(e.parentId, e.parentBody.length); head.set(e.parentId, ix(e.parentBody[0])); team.set(e.childId, e.team); len.set(e.childId, e.childBody.length); head.set(e.childId, ix(e.childBody[0])); alive[e.team].add(e.childId); win[e.team].splits++; if (e.childBody.length <= 3) win[e.team].small++; continue; }
  if (e.type === 'dragonDeath') {
    const id = e.id, t = team.get(id), L = len.get(id), [kid, kl] = kingOf(t), mover = id === cur, other = team.get(cur);
    if (e.reason === 'H') win[t].headOn++; else if (!mover && other !== t) win[t].dEnemy++; else win[t].dOwn++;
    if (kid === id && L >= 8) events.push(`r${round} ${t} king L${L} died (${e.reason}${mover ? ', own move' : ', by ' + (other === t ? 'ally' : 'enemy') + ' L' + len.get(cur)})`);
    alive[t].delete(id); lastDeath = t;
    if (alive[t].size === 0) events.push(`r${round} ${t} eliminated`);
    continue;
  }
}
pending.win = win; rows.push(pending); const end = snap(round + 1);
console.log(`${key} ${task.map} rounds ${round + 1} winner ${R.result.winner || 'draw'} ${task.us ? 'us=' + task.us : ''} ${task.teamA ? task.teamA + ' vs ' + task.teamB : ''}`);
console.log('start r | team: heads king total raid near | splits(small) deaths head-on/own-move | eat nat/drop(own)');
for (const s of rows) {
  const line = ['A', 'B'].map(t => { const x = s[t], w = s.win[t]; return `${t}: ${String(x.heads).padStart(2)} ${String(x.king).padStart(2)} ${String(x.total).padStart(3)} ${String(x.raid).padStart(2)} ${x.near === 999 || x.near === null ? ' -' : String(x.near).padStart(2)} | ${String(w.splits).padStart(3)}(${w.small}) ${w.headOn}/${w.dOwn} | ${w.nat}/${w.drop}(${w.dropOwn})`; });
  console.log(`r${String(s.r).padStart(3)}  ${line.join('   ')}`);
}
console.log(`end   A: ${end.A.heads} ${end.A.king} ${end.A.total}   B: ${end.B.heads} ${end.B.king} ${end.B.total}  result A ${JSON.stringify(R.result.teamA)} B ${JSON.stringify(R.result.teamB)}`);
for (const e of events) console.log('  ' + e);
