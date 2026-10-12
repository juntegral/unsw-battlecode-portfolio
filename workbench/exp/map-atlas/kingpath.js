// kingpath.js — king safety by path distance (Claude, 2026-10-01). The atlas's exposure counts torus-Manhattan distance, which
// ignores kelp and portals (on Portals the halves are disconnected, yet 50 % of king rounds show an enemy head within 6). Here:
// at the first turn of every round r300-499, each team's king (longest living dragon, ties to the lower id, length >= 8) and the
// path distance over the static map graph (kelp blocks, portals carry, wrap; bodies ignored) from its head to the nearest enemy
// head. Histogram 0..30 (31 = farther or unreachable). Also, for every king (>= 8) death at r >= 300: the path distance to the
// nearest enemy head at the round's first turn and the killer's length when an enemy head ended it.
// Heads and lengths are tracked without bodies (dragonUpdate heads, split bodies, +1 per eaten pearl, -1 per extra step);
// the end-of-game counts are checked against the result (mismatch expected 0).
// Output: cache/kingpath.jsonl. Population: cache/tasks.jsonl games (top and online) that reach r300. Workers <= 3.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '../..'), OUT = path.join(__dirname, 'cache');
const raw = require(path.join(ROOT, 'legacy/exp/intake-gap/rawload.js'));
const { buildGraph } = require('./recount.js');

function run(R, task) {
  const M = R.match.map, W = M.width, G = buildGraph(M), ix = p => p.y * W + p.x;
  const team = new Map(), len = new Map(), head = new Map(), alive = { A: new Set(), B: new Set() };
  for (const d of M.initialDragons) { team.set(d.id, d.team); len.set(d.id, d.body.length); head.set(d.id, ix(d.body[0])); alive[d.team].add(d.id); }
  const H = { A: new Array(32).fill(0), B: new Array(32).fill(0) }, KD = { A: [], B: [] };
  const dist = new Int32Array(G.N), q = new Int32Array(G.N);
  const bfsFrom = src => { dist.fill(-1); let t = 0; dist[src] = 0; q[t++] = src; for (let i = 0; i < t; i++) { const k = q[i]; for (let z = 0; z < 4; z++) { const v = G.nb[k * 4 + z]; if (v >= 0 && dist[v] < 0) { dist[v] = dist[k] + 1; q[t++] = v; } } } };
  const kingOf = t => { let kid = -1, kl = 0; for (const id of alive[t]) { const L = len.get(id); if (L > kl || (L === kl && id < kid)) { kl = L; kid = id; } } return [kid, kl]; };
  let round = -1, cur = -1, updates = 0, firstTurn = false, roundNear = { A: null, B: null }, roundKing = { A: -1, B: -1 };
  for (const e of R.events) {
    if (e.type === 'roundStart') { round = e.round; firstTurn = true; roundNear = { A: null, B: null }; roundKing = { A: -1, B: -1 }; continue; }
    if (e.type === 'turnStart') {
      cur = e.id; updates = 0;
      if (firstTurn && round >= 300) {
        for (const t of ['A', 'B']) {
          const [kid, kl] = kingOf(t); if (kid < 0 || kl < 8) continue;
          bfsFrom(head.get(kid)); let best = 999; const o = t === 'A' ? 'B' : 'A';
          for (const id of alive[o]) { const d = dist[head.get(id)]; if (d >= 0 && d < best) best = d; }
          H[t][Math.min(best, 31)]++; roundNear[t] = best; roundKing[t] = kid;
        }
      }
      firstTurn = false; continue;
    }
    if (e.type === 'tileChange' && !e.hasPearl) { len.set(cur, len.get(cur) + 1); continue; }
    if (e.type === 'dragonUpdate') { if (round < 0) continue; updates++; if (updates > 1) len.set(e.id, len.get(e.id) - 1); head.set(e.id, ix(e.head)); continue; }
    if (e.type === 'dragonSplit') { len.set(e.parentId, e.parentBody.length); head.set(e.parentId, ix(e.parentBody[0])); team.set(e.childId, e.team); len.set(e.childId, e.childBody.length); head.set(e.childId, ix(e.childBody[0])); alive[e.team].add(e.childId); continue; }
    if (e.type === 'dragonDeath') {
      const id = e.id, t = team.get(id);
      if (round >= 300 && roundKing[t] === id && len.get(id) >= 8) KD[t].push([round, len.get(id), e.reason, id === cur ? 1 : 0, roundNear[t] === null ? -1 : roundNear[t], id !== cur && team.get(cur) !== t ? len.get(cur) : 0]);
      alive[t].delete(id); continue;
    }
  }
  let mismatch = 0;
  for (const t of ['A', 'B']) { let mx = 0, tot = 0; for (const id of alive[t]) { const L = len.get(id); tot += L; if (L > mx) mx = L; } const r = R.result['team' + t]; if (alive[t].size !== r.dragonCount || mx !== r.longestDragon || tot !== r.totalLength) mismatch++; }
  return { key: task.key, src: task.src, set: task.set || null, map: task.map, rounds: round + 1, winner: R.result.winner || null, us: task.us || null, opp: task.oppId || null, mismatch, A: { hist: H.A, kd: KD.A }, B: { hist: H.B, kd: KD.B } };
}

function resources() {
  const m = /System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure', [], { encoding: 'utf8' }));
  const d = cp.execFileSync('df', ['-g', '/'], { encoding: 'utf8' }).trim().split('\n').pop().trim().split(/\s+/);
  return { memory: m ? +m[1] : null, disk: +d[3] };
}
if (require.main === module && process.argv[2] === 'worker') {
  process.on('message', t => { try { process.send({ row: run(raw.load(t.file), t) }); } catch (e) { process.send({ key: t.key, error: String(e.stack) }); } });
} else if (require.main === module) {
  const reach = new Set(fs.readFileSync(path.join(OUT, 'recount.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => r.rounds > 300).map(r => r.key));
  const all = fs.readFileSync(path.join(OUT, 'tasks.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(t => t.src !== 'local' && reach.has(t.key));
  const outfile = path.join(OUT, 'kingpath.jsonl');
  const done = new Set(fs.existsSync(outfile) ? fs.readFileSync(outfile, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l).key) : []);
  const todo = all.filter(t => !done.has(t.key)); const nw = Math.min(3, +(process.argv[2] || 3));
  let i = 0, n = 0, busy = 0, stop = false; const start = Date.now(), ws = [];
  console.log('todo', todo.length, 'done', done.size, JSON.stringify(resources()));
  const next = w => {
    if (stop) return;
    if (i >= todo.length) { if (!busy) { ws.forEach(x => x.kill()); console.log('DONE', n, 'seconds', Math.round((Date.now() - start) / 1000)); } return; }
    if (n % 200 === 0) { const r = resources(); if (r.memory === null || r.memory < 10 || r.disk < 20) { stop = true; ws.forEach(x => x.kill()); console.log('PAUSED', JSON.stringify(r)); process.exitCode = 75; return; } }
    busy++; w.send(todo[i++]);
  };
  for (let z = 0; z < nw; z++) {
    const w = cp.fork(__filename, ['worker'], { execArgv: ['--max-old-space-size=900'], stdio: ['ignore', 'ignore', 'inherit', 'ipc'] }); ws.push(w);
    w.on('message', m => { busy--; n++; if (m.error) fs.appendFileSync(path.join(OUT, 'kingpath-errors.jsonl'), JSON.stringify(m) + '\n'); else fs.appendFileSync(outfile, JSON.stringify(m.row) + '\n');
      if (n % 1000 === 0) console.log('progress', n, '/', todo.length, 'seconds', Math.round((Date.now() - start) / 1000)); next(w); });
    next(w);
  }
}
module.exports = { run };
