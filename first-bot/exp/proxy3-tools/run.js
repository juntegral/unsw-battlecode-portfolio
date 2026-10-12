#!/usr/bin/env node
'use strict';
// run.js — plays local games for the proxy3 calibration with the official sandbox (tools/unswbc), politely:
// at most --jobs games of this runner at once, and a new game starts only while the machine runs fewer than --max-total
// judge processes (`ps -axo command | grep -c '[u]nswbc-clean.py run'`) and at least 20 GiB of disk are free.
//
// usage (repository root):
//   node exp/proxy3-tools/run.js --label <L> --bot <dir> --opps <name|dir>[,...] [--maps <dir>] [--seeds 1,2] [--jobs 2] [--max-total 6]
//       Our bot against each opponent, every map x both sides x seed. Output as tools/eval.js: exp/<L>/rows.jsonl
//       (key opp:map:side:seed) and exp/<L>/games/<opp>_<map>_<side>_<seed>/game.replay, so that
//       `node tools/proxy_check.js measure --label <L>` works.
//   node exp/proxy3-tools/run.js --label <L> --pairs a:b[,c:d] [--both-sides] [--maps <dir>] [--seeds 1,2,3] [...]
//       Proxy-vs-proxy games as tools/proxy_check.js run: exp/<L>/games.jsonl (key a__b__map__seed) and
//       exp/<L>/games/<key>/game.replay; then `node tools/proxy_check.js measure --label <L>`.
//   A bot or opponent is a directory path, or a name under bots/. Maps default to exp/proxy3-maps/all11.
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const argv = process.argv.slice(2);
const opt = {}; for (let i = 0; i < argv.length; i++) if (argv[i].startsWith('--')) { const k = argv[i].slice(2); opt[k] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true; }
if (!opt.label) { console.error('need --label'); process.exit(2); }
const out = path.join(ROOT, 'exp', opt.label);
const mapDir = path.resolve(ROOT, opt.maps || 'exp/proxy3-maps/all11');
const maps = fs.readdirSync(mapDir).filter(f => f.endsWith('.map')).sort().map(f => f.replace(/\.map$/, ''));
const seeds = String(opt.seeds || '1,2').split(',').map(Number);
const jobs = Math.min(2, +(opt.jobs || 2)), maxTotal = +(opt['max-total'] || 6);
const dirOf = n => n.includes('/') ? path.resolve(ROOT, n) : path.join(ROOT, 'bots', n);
const nameOf = n => n.includes('/') ? path.basename(n) : n;
fs.mkdirSync(path.join(out, 'games'), { recursive: true });

const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(Boolean).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];
const tasks = [];
let rowsFile;
if (opt.pairs) {
  rowsFile = path.join(out, 'games.jsonl');
  const done = new Set(readJsonl(rowsFile).map(r => r.key));
  for (const pr of String(opt.pairs).split(',')) {
    const [a, b] = pr.split(':');
    for (const m of maps) for (const sd of seeds) {
      const variants = opt['both-sides'] && a !== b ? [[a, b], [b, a]] : [[a, b]];
      for (const [x, y] of variants) { const key = [nameOf(x), nameOf(y), m, sd].join('__'); if (!done.has(key)) tasks.push({ mode: 'pair', key, A: x, B: y, map: m, seed: sd, dir: key }); }
    }
  }
} else {
  if (!opt.bot || !opt.opps) { console.error('need --bot and --opps (or --pairs)'); process.exit(2); }
  rowsFile = path.join(out, 'rows.jsonl');
  const done = new Set(readJsonl(rowsFile).filter(r => r.G !== undefined).map(r => r.key));
  for (const o of String(opt.opps).split(',')) for (const m of maps) for (const side of ['A', 'B']) for (const sd of seeds) {
    const key = [nameOf(o), m, side, sd].join(':');
    if (done.has(key)) continue;
    tasks.push({ mode: 'bot', key, opp: o, map: m, side, seed: sd, A: side === 'A' ? opt.bot : o, B: side === 'A' ? o : opt.bot, dir: key.replace(/:/g, '_') });
  }
}
console.log(`${opt.label}: ${tasks.length} games to play, jobs ${jobs}, machine cap ${maxTotal}`);

const judges = () => { try { return +cp.execSync("ps -axo command | grep -c '[u]nswbc-clean.py run' || true").toString().trim(); } catch { return 0; } };
const freeGiB = () => { const d = fs.statfsSync(ROOT); return d.bavail * d.bsize / 1024 ** 3; };
const sleep = ms => new Promise(r => setTimeout(r, ms));
let started = 0, finished = 0, stopDisk = false;
const t0 = Date.now();
async function slot() {
  // wait for a machine slot; the check and the spawn are close enough for two local workers (stagger by a second)
  for (;;) {
    if (freeGiB() < 20) { stopDisk = true; return false; }
    if (judges() < maxTotal) return true;
    await sleep(4000);
  }
}
function play(t) {
  return new Promise(res => {
    const dir = path.join(out, 'games', t.dir); fs.mkdirSync(dir, { recursive: true });
    const p = cp.spawn(path.join(ROOT, 'tools', 'unswbc'), ['run', path.join(mapDir, t.map + '.map'), dirOf(t.A), dirOf(t.B), '--sandbox', '--seed', String(t.seed), '--no-logs', '--no-draw', '--no-indicator', '-o', path.join(dir, 'game.replay')], { cwd: dir });
    let log = ''; p.stdout.on('data', d => log += d); p.stderr.on('data', d => log += d);
    p.on('error', e => res({ code: -1, log: String(e) }));
    p.on('close', code => res({ code, log }));
  });
}
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
async function worker(w) {
  await sleep(w * 1500);
  while (tasks.length) {
    if (!(await slot())) break;
    const t = tasks.shift(); if (!t) break;
    started++;
    const g0 = Date.now();
    const r = await play(t);
    const row = t.mode === 'pair' ? { key: t.key, a: nameOf(t.A), b: nameOf(t.B), map: t.map, seed: t.seed, exit: r.code } : { key: t.key, opp: nameOf(t.opp), map: t.map, side: t.side, seed: t.seed, exit: r.code };
    row.secs = +((Date.now() - g0) / 1000).toFixed(1);
    try {
      const R = load(path.join(out, 'games', t.dir, 'game.replay')), res = R.result;
      if (t.mode === 'pair') { row.winner = res.winner || 'draw'; row.rounds = null; }
      else {
        const us = res['team' + t.side], th = res['team' + (t.side === 'A' ? 'B' : 'A')];
        Object.assign(row, { G: us.dragonCount > 0 ? us.longestDragon : 0, alive: us.dragonCount > 0, total: us.totalLength, units: us.dragonCount, theirLongest: th.longestDragon, won: res.winner === t.side, endReason: res.endReason });
      }
    } catch (e) { row.error = String(e).slice(0, 200); }
    const prob = r.log.match(/.*(no reply|timed out|exceeded|Traceback|error:|out of points).*/i); if (prob) row.botProblem = prob[0].slice(0, 200);
    fs.appendFileSync(rowsFile, JSON.stringify(row) + '\n');
    finished++;
    console.log(`  [${finished}] ${t.key} ${row.error ? 'ERROR ' + row.error : t.mode === 'pair' ? row.winner : (row.won ? 'W' : 'L') + ' G' + row.G} ${row.secs}s${row.botProblem ? ' PROBLEM ' + row.botProblem : ''} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
}
(async () => {
  await Promise.all(Array.from({ length: jobs }, (_, i) => worker(i)));
  if (stopDisk) console.log('stopped: free disk < 20 GiB');
  console.log(`done: ${finished} games in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
})();
