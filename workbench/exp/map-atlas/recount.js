// recount.js — independent recount of the atlas's key per-map numbers (Claude, 2026-10-01 03:10 KST).
//
// Written from the rules and the replay event stream alone; it shares no counting code with extract.js (Codex) or the
// inherited tools. It shares only the byte decoder legacy/exp/intake-gap/rawload.js, whose events were checked equal to the
// official viewer conversion (rawload.validate; this script re-checks a stratified sample with `node recount.js validate`).
//
// Per game and team it recomputes:
//   heads at the start of r10/25/50/100/150/250/300/350/400 (alive-set bookkeeping: initial + splits - deaths);
//   lengths by arithmetic (initial, +1 per eaten pearl, -1 per executed step beyond the first in a turn, split bodies),
//     cross-checked against a head/tail body deque every turn (lenMismatch) and against the final result (finalMismatch);
//   the longest at r300/400/500, total length, eligible (length >= 4) head-rounds and splits per phase;
//   natural intake per phase; sacrifices by the same definition as the atlas (the mover dies with a free neighbour at its turn
//     start, not head-to-head, not into an enemy body, not a timeout, not a sprint death), with round and length;
//   king (longest, >= 8) nearest enemy head, torus Manhattan, at the first turn of r300-499;
//   layout from natural spawns (the pearl appearing right after roundStart) against the a/b/10 map files;
//   stall (>= 100 rounds, no sonar ping and <= 3 splits for a team).
// Output: exp/map-atlas/cache/recount.jsonl (one row per game). Workers: at most 3, niced by the caller.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '../..'), OUT = path.join(__dirname, 'cache');
const raw = require(path.join(ROOT, 'legacy/exp/intake-gap/rawload.js'));
const FILE = { 'Autarky': 'autarky', 'Default': 'default', 'Devil': 'devil', 'Portals': 'portals', 'Prisoners Dilemma': 'prisoners_dilemma',
  'Queen Of Spades': 'queen_of_spades', 'Schooltime': 'schooltime', 'Slithery Fight': 'slithery_fight', 'Trauma': 'trauma', 'Trophy': 'trophy' };
const TWO = new Set(['Devil', 'Queen Of Spades', 'Schooltime', 'Slithery Fight']);
const CPS = [10, 25, 50, 100, 150, 250, 300, 350, 400];
const PHASE_EDGES = [50, 100, 250, 350, 450];   // phases 0-49, 50-99, 100-249, 250-349, 350-449, 450-499
const phaseOf = r => { let p = 0; while (p < PHASE_EDGES.length && r >= PHASE_EDGES[p]) p++; return p; };

// ---- spawn tables (tiles whose max gap > 0) per layout, read from the map files ----
const spawnSets = new Map();
function spawnSet(map, lay) {
  const k = map + '/' + lay; if (spawnSets.has(k)) return spawnSets.get(k);
  const dir = lay === 'a' ? 'maps/online-20260927' : 'maps/variants';
  const name = FILE[map] + (lay === 'b' ? '_b' : lay === '10' ? '_10' : '') + '.map';
  const txt = fs.readFileSync(path.join(ROOT, dir, name), 'utf8').split('\n');
  const W = +txt[0].split(/\s+/)[1], s = new Set();
  for (const l of txt) { const a = l.trim().split(/\s+/); if (a[0] === 'TILE' && +a[4] > 0) s.add(+a[2] * W + +a[1]); }
  spawnSets.set(k, s); return s;
}

// ---- movement graph: kelp blocks, portals carry the head to the tile beyond the paired edge in the direction of travel ----
function buildGraph(M) {
  const W = M.width, H = M.height, N = W * H;
  const vec = { N: [0, -1], E: [1, 0], S: [0, 1], W: [-1, 0] };
  const tileIdx = (x, y) => ((y % H + H) % H) * W + ((x % W + W) % W);
  // an edge is named by the pair of tiles it separates, ordered (lower index first) plus orientation
  const edgeName = (x, y, side) => { const [dx, dy] = vec[side]; const a = tileIdx(x, y), b = tileIdx(x + dx, y + dy); const h = side === 'N' || side === 'S' ? 'h' : 'v'; return h + Math.min(a, b) + ':' + Math.max(a, b); };
  const portalOut = new Map();   // edgeName -> the paired edge {x, y, side}
  for (const [p, q] of M.portals || []) { portalOut.set(edgeName(p.x, p.y, p.side), q); portalOut.set(edgeName(q.x, q.y, q.side), p); }
  const hEdge = (x, y) => M.initialHEdges[y * W + x] === 1;                // north edge of (x, y); row H = south border
  const vEdge = (x, y) => M.initialVEdges[y * (W + 1) + x] === 1;          // west edge of (x, y); column W = east border
  const kelp = (x, y, d) => {
    if (d === 'N') return hEdge(x, y) || (y === 0 && hEdge(x, H));
    if (d === 'S') return y === H - 1 ? (hEdge(x, H) || hEdge(x, 0)) : hEdge(x, y + 1);
    if (d === 'W') return vEdge(x, y) || (x === 0 && vEdge(W, y));
    return x === W - 1 ? (vEdge(W, y) || vEdge(0, y)) : vEdge(x + 1, y);
  };
  const nb = new Int32Array(N * 4).fill(-1), DIRS = ['N', 'E', 'S', 'W'];
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) for (let z = 0; z < 4; z++) {
    const d = DIRS[z], q = portalOut.get(edgeName(x, y, d));
    if (q) {
      // tiles beside the paired edge: (q.x, q.y) and one step toward q.side; arrive at the one lying in direction d
      const [dx, dy] = vec[q.side], other = [q.x + dx, q.y + dy];
      nb[(y * W + x) * 4 + z] = d === q.side ? tileIdx(other[0], other[1]) : tileIdx(q.x, q.y);
    } else if (!kelp(x, y, d)) nb[(y * W + x) * 4 + z] = tileIdx(x + vec[d][0], y + vec[d][1]);
  }
  return { W, H, N, nb };
}

function recount(R, task) {
  const M = R.match.map, W = M.width, H = M.height, G = buildGraph(M);
  const ix = p => p.y * W + p.x;
  const team = new Map(), len = new Map(), body = new Map(), occ = new Int32Array(W * H).fill(-1);
  const alive = { A: new Set(), B: new Set() };
  const put = id => { for (const k of body.get(id)) occ[k] = id; }, lift = id => { for (const k of body.get(id)) if (occ[k] === id) occ[k] = -1; };
  const born = (id, t, b) => { team.set(id, t); len.set(id, b.length); body.set(id, b.map(ix)); alive[t].add(id); put(id); };
  for (const d of M.initialDragons) born(d.id, d.team, d.body);
  const T = {}; for (const t of ['A', 'B']) T[t] = { heads: {}, king: {}, total: {}, eligHR: [0, 0, 0, 0, 0, 0], headR: [0, 0, 0, 0, 0, 0], splits: [0, 0, 0, 0, 0, 0],
    small: [0, 0, 0, 0, 0, 0], nat: [0, 0, 0, 0, 0, 0], sac: [], deaths: [0, 0, 0, 0, 0, 0], kingR: [0, 0], kingNear3: [0, 0], kingNear6: [0, 0], pings: 0, splitAll: 0 };
  const snap = r => { for (const t of ['A', 'B']) { let mx = 0, tot = 0; for (const id of alive[t]) { const L = len.get(id); tot += L; if (L > mx) mx = L; } T[t].heads[r] = alive[t].size; T[t].king[r] = mx; T[t].total[r] = tot; } };
  const torus = (a, b) => { const dx = Math.abs(a % W - b % W), dy = Math.abs(((a / W) | 0) - ((b / W) | 0)); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
  const pearl = new Int8Array(W * H);   // 0 none, 1 natural, 2 dropped
  for (let k = 0; k < W * H; k++) if (M.initialTiles[k] === 2) pearl[k] = 1;   // initial pearls count as natural (as the atlas does)
  const natSpawn = new Set();
  let round = -1, cur = -1, turnSteps = [], updates = 0, eats = 0, free = 0, firstTurn = false, block = '';
  let lenMismatch = 0, dirty = false, tle = false, unpaired = 0, strayPearls = 0, initMismatch = 0;
  const endTurn = () => {
    if (cur >= 0 && len.has(cur) && dirty) { const L = len.get(cur); if (body.get(cur).length !== L) lenMismatch++; }
    cur = -1; dirty = false;
  };
  for (const e of R.events) {
    if (e.type === 'roundStart') {
      endTurn(); round = e.round; firstTurn = true; block = 'round';
      if (CPS.includes(round)) snap(round);
      const p = phaseOf(round);
      for (const t of ['A', 'B']) { T[t].headR[p] += alive[t].size; for (const id of alive[t]) if (len.get(id) >= 4) T[t].eligHR[p]++; }
      continue;
    }
    if (e.type === 'tileChange' && e.hasPearl) {
      const k = ix(e.tile);
      if (block === 'round') { pearl[k] = 1; natSpawn.add(k); } else if (block === 'death') pearl[k] = 2; else { pearl[k] = 1; strayPearls++; }
      continue;
    }
    if (e.type !== 'tileChange') block = e.type === 'dragonDeath' ? 'death' : '';
    if (e.type === 'turnStart') {
      endTurn(); cur = e.id; turnSteps = []; updates = 0; eats = 0; tle = false;
      const b = body.get(cur); if (!b) throw Error('turn of unknown dragon ' + cur);
      free = 0; for (let z = 0; z < 4; z++) { const v = G.nb[b[0] * 4 + z]; if (v >= 0 && occ[v] < 0) free++; }
      if (firstTurn && round >= 300) {
        firstTurn = false;
        for (const t of ['A', 'B']) {
          let kid = -1, kl = 0; for (const id of alive[t]) { const L = len.get(id); if (L > kl || (L === kl && id < kid)) { kl = L; kid = id; } }
          if (kid < 0 || kl < 8) continue;
          let near = 999; const o = t === 'A' ? 'B' : 'A'; for (const id of alive[o]) near = Math.min(near, torus(body.get(kid)[0], body.get(id)[0]));
          const h = round < 400 ? 0 : 1; T[t].kingR[h]++; T[t].kingNear3[h] += near <= 3; T[t].kingNear6[h] += near <= 6;
        }
      } else firstTurn = false;
      continue;
    }
    if (e.type === 'dragonAction') { if (e.id === cur) { turnSteps = e.action && e.action.kind === 'move' ? e.action.steps : []; tle = !!e.tle; } continue; }
    if (e.type === 'tileChange') {   // eaten
      const k = ix(e.tile), t = team.get(cur); if (!alive[t] || !alive[t].has(cur)) throw Error('eat by dead dragon');
      if (pearl[k] === 1) T[t].nat[phaseOf(round)]++; else if (pearl[k] === 0) unpaired++;
      pearl[k] = 0; len.set(cur, len.get(cur) + 1); eats++; dirty = true; continue;
    }
    if (e.type === 'dragonUpdate') {
      const id = e.id;
      if (round < 0) { const b = body.get(id); if (!b || b[0] !== ix(e.head) || b[b.length - 1] !== ix(e.tail)) initMismatch++; continue; }   // placement events
      if (id !== cur) throw Error('update outside own turn');
      updates++; if (updates > 1) len.set(id, len.get(id) - 1);
      lift(id); const b = body.get(id), h = ix(e.head), tl = ix(e.tail);
      if (b[0] !== h) b.unshift(h);
      while (b.length > 1 && b[b.length - 1] !== tl) b.pop();
      put(id); dirty = true; continue;
    }
    if (e.type === 'dragonSplit') {
      const t = e.team, p = phaseOf(round); lift(e.parentId);
      body.set(e.parentId, e.parentBody.map(ix)); len.set(e.parentId, e.parentBody.length); put(e.parentId);
      born(e.childId, t, e.childBody); T[t].splits[p]++; T[t].splitAll++; if (e.childBody.length <= 3) T[t].small[p]++;
      continue;
    }
    if (e.type === 'dragonDeath') {
      const id = e.id, t = team.get(id), L = len.get(id);
      let cause = 'other';
      if (id === cur) {
        if (e.reason === 'H') cause = 'head';
        else if (e.reason === 'O') {
          const z = 'NESW'.indexOf(turnSteps[updates]); const v = z < 0 ? -1 : G.nb[body.get(id)[0] * 4 + z]; const who = v >= 0 ? occ[v] : -1;
          cause = who >= 0 && team.get(who) === t ? (free ? 'sac' : 'trap') : (free ? 'enemyBody' : 'trap');
        } else if (e.reason === 'A' && tle) cause = 'fault';
        else if (e.reason === 'A' && turnSteps.length > updates && updates > 0 && L <= 2) cause = 'sprint';
        else cause = free ? 'sac' : 'trap';
      } else cause = 'hit';
      T[t].deaths[phaseOf(round)]++;
      if (cause === 'sac') T[t].sac.push([round, L]);
      lift(id); alive[t].delete(id); len.delete(id); body.delete(id);
      if (id === cur) { cur = -1; dirty = false; }
      continue;
    }
  }
  endTurn(); snap(500);
  let finalMismatch = 0;
  for (const t of ['A', 'B']) { const r = R.result['team' + t]; if (T[t].heads[500] !== r.dragonCount || T[t].king[500] !== r.longestDragon || T[t].total[500] !== r.totalLength) finalMismatch++; }
  for (const [id, n] of R.sonarBySender) if (team.has(id)) T[team.get(id)].pings += n;
  const rounds = round + 1;
  const stall = rounds >= 100 ? ['A', 'B'].filter(t => T[t].pings === 0 && T[t].splitAll <= 3) : [];
  // layout: natural spawn tiles that a layout's table does not spawn contradict that layout
  let layout = 'a', lay = null;
  if (task.map === 'Prisoners Dilemma') layout = M.initialDragons.length === 10 ? '10' : '6';
  else if (TWO.has(task.map)) {
    const a = spawnSet(task.map, 'a'), b = spawnSet(task.map, 'b'); let ca = 0, cb = 0;
    for (const k of natSpawn) { if (!a.has(k)) ca++; if (!b.has(k)) cb++; }
    layout = ca < cb ? 'a' : cb < ca ? 'b' : '?'; lay = [ca, cb];
  }
  return { key: task.key, src: task.src, set: task.set || null, map: task.map, layout, lay, rounds, winner: R.result.winner || null, endReason: R.result.endReason,
    us: task.us || null, opp: task.oppId || null, stall, lenMismatch, finalMismatch, unpaired, strayPearls, initMismatch, A: T.A, B: T.B };
}

function resources() {
  const m = /System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure', [], { encoding: 'utf8' }));
  const d = cp.execFileSync('df', ['-g', '/'], { encoding: 'utf8' }).trim().split('\n').pop().trim().split(/\s+/);
  return { memory: m ? +m[1] : null, disk: +d[3] };
}
function tasks() {
  // the same frozen population as extract.js (cache/tasks.jsonl lists top, online and local replays); local games are not recounted
  return fs.readFileSync(path.join(OUT, 'tasks.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(t => t.src !== 'local');
}
if (require.main === module && process.argv[2] === 'worker') {
  process.on('message', t => { try { process.send({ row: recount(raw.load(t.file), t) }); } catch (e) { process.send({ key: t.key, error: String(e.stack) }); } });
} else if (require.main === module && process.argv[2] === 'one') {
  const t = tasks().find(x => x.key === process.argv[3]); const s = Date.now(); const v = recount(raw.load(t.file), t); console.log(JSON.stringify({ ms: Date.now() - s, v }));
} else if (require.main === module && process.argv[2] === 'validate') {
  // decoder check: rawload's events equal the official viewer conversion on a stratified sample (3 per map x source)
  const all = tasks(), pick = new Map(); let seed = 12345; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
  const sh = all.slice().sort(() => rnd() - 0.5);
  for (const t of sh) { const k = t.map + '|' + t.src; const a = pick.get(k) || []; if (a.length < 3) { a.push(t); pick.set(k, a); } }
  let games = 0, bad = 0, events = 0;
  for (const a of pick.values()) for (const t of a) { const v = raw.validate(t.file); games++; events += v.events; bad += v.bad > 0; }
  console.log(JSON.stringify({ games, events, gamesWithDifferences: bad }));
} else if (require.main === module) {
  const outfile = path.join(OUT, 'recount.jsonl');
  const done = new Set(fs.existsSync(outfile) ? fs.readFileSync(outfile, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l).key) : []);
  const todo = tasks().filter(t => !done.has(t.key)); const nw = Math.min(3, +(process.argv[2] || 3));
  let i = 0, n = 0, busy = 0, stop = false; const start = Date.now(), ws = [];
  console.log('todo', todo.length, 'done', done.size, 'resources', JSON.stringify(resources()));
  const next = w => {
    if (stop) return;
    if (i >= todo.length) { if (!busy) { ws.forEach(x => x.kill()); console.log('DONE', n, 'seconds', Math.round((Date.now() - start) / 1000)); } return; }
    if (n % 200 === 0) { const r = resources(); if (r.memory === null || r.memory < 10 || r.disk < 20) { stop = true; ws.forEach(x => x.kill()); console.log('PAUSED', JSON.stringify(r)); process.exitCode = 75; return; } }
    busy++; w.send(todo[i++]);
  };
  for (let z = 0; z < nw; z++) {
    const w = cp.fork(__filename, ['worker'], { execArgv: ['--max-old-space-size=900'], stdio: ['ignore', 'ignore', 'inherit', 'ipc'] }); ws.push(w);
    w.on('message', m => { busy--; n++; if (m.error) fs.appendFileSync(path.join(OUT, 'recount-errors.jsonl'), JSON.stringify(m) + '\n'); else fs.appendFileSync(outfile, JSON.stringify(m.row) + '\n');
      if (n % 1000 === 0) console.log('progress', n, '/', todo.length, 'seconds', Math.round((Date.now() - start) / 1000)); next(w); });
    next(w);
  }
}
module.exports = { recount, buildGraph };
