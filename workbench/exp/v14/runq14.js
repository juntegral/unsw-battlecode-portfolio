#!/usr/bin/env node
// v1.4 resumable local game queue (a copy of exp/v11/runq.js; same rows.jsonl / games/<key>/game.replay layout). A key is done only when its
// row is clean: a result (G), exit 0, no error, no bot problem (timeouts included: a laptop sleep can stretch a turn past the judge's 10 s wall
// clock). Any other key is (re)run, so the same command resumes after a sleep or a kill; a game killed mid-run leaves no row and runs again.
// Every launch keeps the machine-wide cap (pgrep -f "unswbc-clean.py run" < --cap) and disk free >= 21 GiB.
// usage: node exp/v14/runq14.js <spec.json> [--jobs 3] [--cap 6]
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'viewer.js'));
const args = process.argv.slice(2), get = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const spec = JSON.parse(fs.readFileSync(args[0], 'utf8')), jobs = +get('--jobs', 3), cap = +get('--cap', 6);
const lanes = spec.map(s => {
  const bot = path.resolve(ROOT, s.bot), out = path.resolve(ROOT, s.out), mapDir = path.resolve(ROOT, s.maps);
  fs.mkdirSync(path.join(out, 'games'), { recursive: true });
  const rowsFile = path.join(out, 'rows.jsonl');
  const clean = r => r.G !== undefined && r.exit === 0 && !r.error && !r.botProblem;
  const done = new Set(fs.existsSync(rowsFile) ? fs.readFileSync(rowsFile, 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l)).filter(clean).map(r => r.key) : []);
  const maps = fs.readdirSync(mapDir).filter(f => f.endsWith('.map') && (!s.only || s.only.includes(f.replace('.map', '')))).sort();
  const tasks = [];
  for (const opp of s.opps) for (const map of maps) for (const side of s.sides || ['A', 'B']) for (const seed of s.seeds) {
    const key = [opp, map.replace('.map', ''), side, seed].join(':');
    if (!done.has(key)) tasks.push({ key, opp, map, side, seed, bot, out, mapDir, rowsFile });
  }
  return tasks;
});
const tasks = []; for (let i = 0; lanes.some(l => i < l.length); i++) for (const l of lanes) if (i < l.length) tasks.push(l[i]);   // interleave the sets
const running = () => { try { return +cp.execSync('pgrep -f "unswbc-clean.py run" | wc -l').toString().trim(); } catch { return 0; } };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const run = t => new Promise(res => {
  const disk = fs.statfsSync(ROOT);
  if (disk.bavail * disk.bsize < 21 * 1024 ** 3) { fs.appendFileSync(t.rowsFile, JSON.stringify({ key: t.key, exit: null, error: 'disk free < 20 GiB; game not started' }) + '\n'); return res(); }
  const dir = path.join(t.out, 'games', t.key.replace(/:/g, '_')); fs.mkdirSync(dir, { recursive: true });
  const oppDir = path.join(ROOT, 'bots', t.opp), a = t.side === 'A' ? t.bot : oppDir, b = t.side === 'A' ? oppDir : t.bot;
  const p = cp.spawn('nice', ['-n', '10', path.join(ROOT, 'tools', 'unswbc'), 'run', path.join(t.mapDir, t.map), a, b, '--sandbox', '--seed', String(t.seed), '--no-logs', '--no-draw', '-o', path.join(dir, 'game.replay')], { cwd: dir });
  let log = ''; p.stdout.on('data', d => log += d); p.stderr.on('data', d => log += d);
  p.on('close', code => {
    const row = { key: t.key, opp: t.opp, map: t.map.replace('.map', ''), side: t.side, seed: t.seed, exit: code };
    try {
      const R = load(dir), us = R.result['team' + t.side], th = R.result['team' + (t.side === 'A' ? 'B' : 'A')];
      Object.assign(row, { G: us.dragonCount > 0 ? us.longestDragon : 0, alive: us.dragonCount > 0, total: us.totalLength, units: us.dragonCount, theirLongest: th.longestDragon, won: R.result.winner === t.side, endReason: R.result.endReason });
    } catch (e) { row.error = String(e).slice(0, 200); }
    if (/no reply|timed out|exceeded|Traceback|error:/i.test(log)) row.botProblem = (log.match(/.*(no reply|timed out|exceeded|Traceback|error:).*/i) || [''])[0].slice(0, 200);
    fs.appendFileSync(t.rowsFile, JSON.stringify(row) + '\n');
    console.log(new Date().toTimeString().slice(0, 8), path.basename(t.out), t.key, row.won ? 'W' : 'L', row.G, row.error || row.botProblem || '');
    res();
  });
});
(async () => {
  let live = 0;
  console.log(new Date().toTimeString().slice(0, 8), 'tasks', tasks.length);
  for (const t of tasks) {
    while (live >= jobs || running() >= cap) await sleep(2000);
    live++; run(t).then(() => live--);
    await sleep(1500);   // let the launched judge show up in pgrep before the next check
  }
  while (live > 0) await sleep(2000);
  console.log(new Date().toTimeString().slice(0, 8), 'all done');
})();
