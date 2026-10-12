#!/usr/bin/env node
// E7 follow-up: did the dragon that killed an enemy king (>= 8, head-on) come from afar (interception) or was it already
// beside the king (opportunism)? Replays only. Games = those whose .cache/econ-principles row has such a king death.
// usage: nice -n 10 node exp/econ-principles/approach.js [--jobs 3]  -> .cache/econ-principles/approach.jsonl (one line per game)
//        node exp/econ-principles/approach.js summary               -> exp/econ-principles/approach-summary.json
// Per king death: round, king team, king length, attacker length, whether the attacker moved (rammer) or the king did,
//   attacker's Manhattan distance to the king's head at the first turn of rounds r-1, r-3, r-5, r-10, r-15 (-1: not alive),
//   attacker's birth round, attacker-team heads within Manhattan 3 of the king's head at r-1, and the same distances for
//   the nearest other attacker-team head (a baseline for "was anyone near the king anyway").
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process'), readline = require('readline');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const CACHE = path.join(ROOT, '.cache', 'econ-principles');
const ELIM = new Set(['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default']);
const LAGS = [1, 3, 5, 10, 15];

function analyse(R, info) {
  const M = R.match.map, W = M.width, H = M.height, nInit = M.initialDragons.length;
  const md = (a, b) => { let dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); if (W - dx < dx) dx = W - dx; if (H - dy < dy) dy = H - dy; return dx + dy; };
  const linfo = { map: info.map }; if (info.map === 'Prisoners Dilemma') linfo.variant = nInit === 10 ? 'PD10' : 'PD6';
  const hist = new Map(); // id -> Map(round -> {x, y, L})
  const kingAt = [new Map(), new Map()]; // team -> round -> {id, x, y}
  let last = -1; const rows = [];
  const hooks = {
    turn(d, round, ctx) {
      if (round === last) return; last = round;
      for (const o of ctx.drag.values()) { let h = hist.get(o.id); if (!h) hist.set(o.id, h = new Map()); h.set(round, { x: o.body[0].x, y: o.body[0].y, L: o.body.length }); if (h.size > 20) h.delete(h.keys().next().value); }
      for (const t of [0, 1]) { const k = ctx.kingOf(t ? 'B' : 'A'); if (k) kingAt[t].set(round, { id: k.id, x: k.body[0].x, y: k.body[0].y }); }
    },
    death(d, rec, idx, other, round, ctx) {
      if (!(rec.cause === 2 || rec.cause === 3) || !other || other.team === d.team) return;
      if (!ctx.isKingNow(d) || d.body.length < 8) return;
      const t = d.team === 'A' ? 0 : 1, a = other, ha = hist.get(a.id) || new Map(), hk = hist.get(d.id) || new Map();
      const dist = LAGS.map(l => { const p = ha.get(round - l), q = hk.get(round - l); return p && q ? md(p, q) : -1; });
      // nearest other attacker-team head to the king at each lag
      const base = LAGS.map(l => { const q = hk.get(round - l); if (!q) return -1; let best = 99; for (const [id, h] of hist) { if (id === a.id) continue; const o = ctx.all.get(id); if (!o || o.team === d.team) continue; const p = h.get(round - l); if (p) best = Math.min(best, md(p, q)); } return best; });
      let grp = 0; const q1 = hk.get(round - 1); if (q1) for (const [id, h] of hist) { if (id === a.id) continue; const o = ctx.all.get(id); if (!o || o.team === d.team) continue; const p = h.get(round - 1); if (p && md(p, q1) <= 3) grp++; }
      rows.push([round, t, d.body.length, a.body.length, rec.cause === 2 ? 1 : 0, ...dist, a.born, grp, ...base]);
    },
  };
  const g = ML.perGame(R, linfo, hooks);
  return { rows, chk: g.chk, winner: g.winner };
}
function workerMain() {
  const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
  const load = tf.makeLoader(tf.viewerSource());
  process.on('message', task => {
    try { const R = load(task.file); const res = analyse(R, task.info); process.send({ key: task.key, line: JSON.stringify({ key: task.key, map: task.info.map, src: task.info.src, set: task.info.set || null, us: task.info.us || null, ...res }) }); }
    catch (err) { process.send({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | ') }); }
  });
}
function summarise() {
  // attacker role (top: W / L by the game winner; ours: U / X) x map kind -> rows
  const A = {};
  for (const l of fs.readFileSync(path.join(CACHE, 'approach.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue; let g; try { g = JSON.parse(l); } catch { continue; } const kind = ELIM.has(g.map) ? 'elim' : 'r500';
    for (const r of g.rows) {
      const at = 1 - r[1]; let role;
      if (g.src === 'top') { if (!g.winner) continue; role = (g.winner === 'A' ? 0 : 1) === at ? 'W' : 'L'; } else role = (g.us === 'A' ? 0 : 1) === at ? 'U' : 'X';
      const k = role + '|' + kind; const a = A[k] || (A[k] = { n: 0, far10: 0, near5: 0, near1: 0, baseFar10: 0, baseNear5: 0, grp: 0, d: [[], [], [], [], []], b: [[], [], [], [], []], moved: 0, lenA: 0, lenK: 0, young: 0 });
      a.n++; a.lenA += r[3]; a.lenK += r[2]; a.moved += r[4];
      const dist = r.slice(5, 10), base = r.slice(12, 17);
      if (dist[3] >= 8) a.far10++; if (dist[2] >= 0 && dist[2] <= 3) a.near5++; if (dist[0] >= 0 && dist[0] <= 3) a.near1++;
      if (base[3] >= 8) a.baseFar10++; if (base[2] >= 0 && base[2] <= 3) a.baseNear5++;
      if (r[11] >= 1) a.grp++; if (r[0] - r[10] <= 15) a.young++;
      for (let i = 0; i < 5; i++) { if (dist[i] >= 0) a.d[i].push(dist[i]); if (base[i] >= 0 && base[i] < 99) a.b[i].push(base[i]); }
    }
  }
  const med = xs => { if (!xs.length) return null; const s = xs.slice().sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
  const out = {}; for (const [k, a] of Object.entries(A)) out[k] = { n: a.n, far10: a.far10 / a.n, near5: a.near5 / a.n, near1: a.near1 / a.n, baseFar10: a.baseFar10 / a.n, baseNear5: a.baseNear5 / a.n, grp: a.grp / a.n, moved: a.moved / a.n, lenA: a.lenA / a.n, lenK: a.lenK / a.n, young: a.young / a.n, medD: a.d.map(med), medB: a.b.map(med) };
  fs.writeFileSync(path.join(__dirname, 'approach-summary.json'), JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out, null, 1));
}
async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  if (argv[0] === 'summary') return summarise();
  const jobs = Math.max(1, Math.min(3, +((argv.indexOf('--jobs') >= 0 && argv[argv.indexOf('--jobs') + 1]) || 3)));
  // tasks: games whose cache row has a head-on death of a king >= 8 (any map)
  const tasks = [];
  const files = fs.readdirSync(CACHE).filter(f => /^(top-all|online-.*)\.jsonl$/.test(f));
  for (const f of files) {
    const rl = readline.createInterface({ input: fs.createReadStream(path.join(CACHE, f)), crlfDelay: Infinity });
    for await (const line of rl) {
      if (!line.trim()) continue; let g; try { g = JSON.parse(line); } catch { continue; }
      if (!g.KD.some(k => k[2] >= 8 && (k[3] === 2 || k[3] === 3))) continue;
      if (g.src === 'top' && ELIM.has(g.map)) continue; // top games: round-500 maps only (E7 is about the scorer; keeps the pass short)
      let file;
      if (g.src === 'top') file = path.join(ROOT, 'data', 'top', String(g.battleId), g.gameId + '.replay.gz');
      else file = path.join(ROOT, 'data', 'online', g.set, 'M' + g.gameId + '.replay');
      tasks.push({ key: g.key, file, info: { map: g.map, src: g.src, set: g.set, us: g.us } });
    }
  }
  const out = path.join(CACHE, 'approach.jsonl'); const done = new Set();
  if (fs.existsSync(out)) for (const l of fs.readFileSync(out, 'utf8').split('\n')) { const m = /^\{"key":"([^"]+)"/.exec(l); if (m) done.add(m[1]); }
  const todo = tasks.filter(t => !done.has(t.key));
  console.log(`approach: ${tasks.length} games, to do ${todo.length} (jobs ${jobs})`);
  const fd = fs.openSync(out, 'a'); let n = 0; const t0 = Date.now();
  await new Promise((resolve, reject) => {
    const queue = todo.slice(); let live = Math.min(jobs, queue.length); if (!live) return resolve();
    for (let i = 0, k = live; i < k; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced', execArgv: ['--max-old-space-size=2048'] }); let fin = false;
      const next = () => { const t = queue.shift(); if (!t) { fin = true; w.kill(); if (--live === 0) resolve(); return; } w.send(t); };
      w.on('message', m => { if (m.error) console.error('error', m.key, m.error); else fs.writeSync(fd, m.line + '\n'); n++; if (n % 200 === 0) console.log(`  ${n}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`); next(); });
      w.on('error', reject); w.on('exit', c => { if (!fin) reject(Error('worker exit ' + c)); });
      next();
    }
  });
  fs.closeSync(fd); console.log(`done ${n} in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
module.exports = { analyse };
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
