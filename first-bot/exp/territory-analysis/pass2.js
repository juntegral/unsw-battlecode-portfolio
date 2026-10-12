#!/usr/bin/env node
// pass2.js — split context over the whole population, and the split gate of our bots. Replays only.
// usage (repository root):
//   node exp/territory-analysis/pass2.js top --keys <file> [--name top-all] [--jobs 4]
//   node exp/territory-analysis/pass2.js online <set> [...] [--jobs 4]
//   Output: exp/territory-analysis/cache/pass2-<name>.jsonl.gz (one line per game).
// Per team:
//   splits by [phase 0-4][where 0 own / 1 neutral / 2 enemy territory][enemy head within the parent's 7x7 view 0/1]
//   childBorn by where (own / neutral / enemy) and child length 2 / 3 / 4+
//   gate (every team, as a behavioural probe of merge2's rule): dragon-turns before r340 with length >= 8, not the team's
//     longest, team units < 5: [turns, turns with an enemy head in the 7x7 view, splits made on such turns,
//     splits made on the other turns]
//   Also our bot's own labels (online sets): split labels per phase, and turns whose label is a split.
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const X = require('./extract.js');
const TOP = path.join(ROOT, 'data', 'top'), ONLINE = path.join(ROOT, 'data', 'online'), CACHE = path.join(__dirname, 'cache');
const phaseOf = r => r < 100 ? 0 : r < 250 ? 1 : r < 350 ? 2 : r < 450 ? 3 : 4;

function analyse(R, info) {
  const G = X.geometry(R), W = G.W;
  const linfo = { map: info.map }; if (info.map === 'Prisoners Dilemma') linfo.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
  const TI = tm => tm === 'A' ? 0 : 1;
  const T = [0, 1].map(() => ({ splits: [0, 1, 2, 3, 4].map(() => [0, 1, 2].map(() => [0, 0])), child: [0, 1, 2].map(() => [0, 0, 0]), gate: [0, 0, 0, 0], gate2: [0, 1, 2, 3, 4].map(() => [0, 0, 0, 0, 0]), labels: [0, 0, 0, 0, 0], esc: [0, 0, 0, 0, 0],
    // children born before r300, by where they were born (own / neutral / enemy): [n, alive 30 rounds later (or at the end),
    // natural pearls eaten within 30 rounds in own / neutral / enemy territory, children that ate >= 1 natural pearl]
    child30: [0, 1, 2].map(() => [0, 0, 0, 0, 0, 0]) }));
  const kids = new Map();
  const inView = (ctx, d) => { const h = d.body[0]; for (const o of ctx.drag.values()) if (o.team !== d.team && ctx.cheb(o.body[0], h) <= 3) return 1; return 0; };
  const units = [0, 0]; let roundSeen = -1;
  const turnCtx = new Map(); // dragon id -> {elig, view}
  const hooks = {
    turn(d, r, ctx) {
      if (r !== roundSeen) { roundSeen = r; units[0] = 0; units[1] = 0; for (const o of ctx.drag.values()) units[TI(o.team)]++; }
      const ti = TI(d.team);
      let longest = true; for (const o of ctx.drag.values()) if (o !== d && o.team === d.team && o.body.length > d.body.length) { longest = false; break; }
      const elig = r < 340 && d.body.length >= 8 && !longest && units[ti] < 5;
      const view = inView(ctx, d);
      turnCtx.set(d.id, { elig, view, r });
      if (elig) { T[ti].gate[0]++; if (view) T[ti].gate[1]++; }
      // which of merge2's split rules (plan.cpp wantSplit) would block this turn, before r340: cap (5+ units), king
      // (the longest only splits when alone), short (length < 8), view (an enemy head in the 7x7 view), open (none of these)
      if (r < 340) {
        const ph = phaseOf(r), g2 = T[ti].gate2[ph];
        if (units[ti] >= 5) g2[0]++; else if (longest && units[ti] >= 2) g2[1]++; else if (units[ti] === 1 ? d.body.length < 5 : d.body.length < 8) g2[2]++; else if (view) g2[3]++; else g2[4]++;
      }
    },
    indicator(e, r, ctx) { const d = ctx.drag.get(e.id); if (!d) return; const t = e.text || ''; if (/^split\d+ u\d+ L\d+/.test(t)) T[TI(d.team)].labels[phaseOf(r)]++; else if (/^escape-split/.test(t)) T[TI(d.team)].esc[phaseOf(r)]++; },
    split(p, ch, e, r, ctx) {
      const ti = TI(p.team), h = p.body[0], k = G.key(h.x, h.y);
      const where = G.terr[k] === 0 ? 1 : G.terr[k] === ti + 1 ? 0 : 2;
      const tc = turnCtx.get(p.id), view = tc && tc.r === r ? tc.view : inView(ctx, p);
      T[ti].splits[phaseOf(r)][where][view]++;
      const ck = G.key(ch.body[0].x, ch.body[0].y), cw = G.terr[ck] === 0 ? 1 : G.terr[ck] === ti + 1 ? 0 : 2;
      T[ti].child[cw][Math.min(2, ch.body.length - 2)]++;
      if (r < 300) kids.set(ch.id, { ti, r, cw, eat: [0, 0, 0], died: -1 });
      if (tc && tc.r === r && tc.elig) { if (tc.view) T[ti].gate[2]++; else T[ti].gate[3]++; }
    },
  };
  hooks.eat = (d, k, o, r) => { const c = kids.get(d.id); if (!c || o >= 0 || r > c.r + 30) return; const t = G.terr[k]; c.eat[t === 0 ? 1 : t === c.ti + 1 ? 0 : 2]++; };
  hooks.death = (d, rec, idx, other, r) => { const c = kids.get(d.id); if (c && c.died < 0) c.died = r; };
  const g = ML.perGame(R, linfo, hooks);
  for (const c of kids.values()) {
    const a = T[c.ti].child30[c.cw]; a[0]++;
    if (c.died < 0 || c.died > c.r + 30) a[1]++;
    a[2] += c.eat[0]; a[3] += c.eat[1]; a[4] += c.eat[2]; if (c.eat[0] + c.eat[1] + c.eat[2] > 0) a[5]++;
  }
  return { rounds: g.rounds, winner: g.winner, chk: g.chk, T };
}

// ---- tasks and workers (as extract.js)
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];
function topTasks(keysArg) {
  const seen = new Set(), idx = [];
  for (const r of readJsonl(path.join(TOP, 'index.jsonl'))) { const k = r.battleId + ':' + r.gameId; if (seen.has(k)) continue; seen.add(k); idx.push(r); }
  const byKey = new Map(idx.map(r => [r.battleId + ':' + r.gameId, r]));
  const keys = fs.readFileSync(path.resolve(ROOT, keysArg), 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  return keys.map(k => byKey.get(k)).filter(Boolean).map(r => ({ key: r.battleId + ':' + r.gameId, file: path.join(TOP, String(r.battleId), r.gameId + '.replay.gz'),
    info: { src: 'top', map: r.map, gameId: r.gameId, battleId: r.battleId, teamA: r.teamA, teamB: r.teamB, winnerIdx: r.winner ? String(r.winner).toUpperCase() : null } })).filter(t => fs.existsSync(t.file));
}
function onlineTasks(set) {
  const dir = path.join(ONLINE, set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  return (idx.games || idx).map(g => ({ key: set + ':' + g.gameId, file: path.join(dir, 'M' + g.gameId + '.replay'), info: { src: 'online', set, map: g.mapName, gameId: g.gameId, us: String(g.ourSide).toUpperCase(), oppId: g.opponentTeam } })).filter(t => fs.existsSync(t.file));
}
function workerMain() {
  const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
  const load = tf.makeLoader(tf.viewerSource());
  process.on('message', task => {
    try { const R = load(task.file); process.send({ key: task.key, line: JSON.stringify({ key: task.key, ...task.info, ...analyse(R, task.info) }) }); }
    catch (err) { process.send({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | ') }); }
  });
}
function cachedKeys(file) { const done = new Set(); if (!fs.existsSync(file)) return done; let txt; try { txt = zlib.gunzipSync(fs.readFileSync(file)).toString(); } catch { return done; } for (const l of txt.split('\n')) { const m = /^\{"key":"([^"]+)"/.exec(l); if (m) done.add(m[1]); } return done; }
async function extract(tasks, cacheFile, jobs) {
  fs.mkdirSync(path.dirname(cacheFile), { recursive: true });
  const done = cachedKeys(cacheFile), todo = tasks.filter(t => !done.has(t.key));
  console.log(`${path.relative(ROOT, cacheFile)}: ${tasks.length} games, cached ${done.size}, to do ${todo.length}`);
  if (!todo.length) return;
  const fd = fs.openSync(cacheFile, 'a'), t0 = Date.now(); let n = 0, errors = 0;
  await new Promise((resolve, reject) => {
    const queue = todo.slice(); let live = Math.min(jobs, queue.length);
    for (let i = 0, k = live; i < k; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced', execArgv: ['--max-old-space-size=3072'] });
      let finished = false;
      const next = () => { const t = queue.shift(); if (!t) { finished = true; w.kill(); if (--live === 0) resolve(); return; } w.send(t); };
      w.on('message', m => { if (m.error) { errors++; console.error('error', m.key, m.error); } else fs.writeSync(fd, zlib.gzipSync(m.line + '\n')); n++; if (n % 200 === 0) console.log(`  ${n}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`); next(); });
      w.on('error', reject); w.on('exit', code => { if (!finished) reject(Error('worker exited ' + code)); });
      next();
    }
  });
  fs.closeSync(fd); console.log(`done ${n} in ${((Date.now() - t0) / 1000).toFixed(0)}s, errors ${errors}`);
}
async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const jobs = Math.max(1, Math.min(4, +opt('jobs', 4)));
  if (argv[0] === 'top') return extract(topTasks(opt('keys')), path.join(CACHE, 'pass2-' + opt('name', 'top-all') + '.jsonl.gz'), jobs);
  if (argv[0] === 'online') { for (let i = 1; i < argv.length; i++) { if (argv[i].startsWith('--')) { i++; continue; } await extract(onlineTasks(argv[i]), path.join(CACHE, 'pass2-online-' + argv[i] + '.jsonl.gz'), jobs); } return; }
  console.error('usage: see header'); process.exit(2);
}
module.exports = { analyse };
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
