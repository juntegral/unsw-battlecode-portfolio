#!/usr/bin/env node
// v1.6 local game queue (exp/v11/runq.js's runner and layout: <out>/rows.jsonl + <out>/games/<key>/game.replay, so exp/v1/local_report.js and
// exp/v16/conv_report.js read it), over several sets at once, interleaved.
//   - at most --jobs games of ours at a time (default 3); before every launch the machine-wide count of running games (pgrep -f "unswbc-clean.py
//     run", every agent's) must be below --cap (default 6), and the disk must have >= 21 GiB free (else the game is not started and no row is written)
//   - resumable: a key with a clean row (a result, no error, no bot problem) is skipped; a killed or broken game (no result, an error, a timeout or
//     "no reply" in the judge's log: e.g. the laptop slept through a turn's wall-clock backstop) is not a result and runs again on the next start
//   - every game under nice -n 10
// usage: node exp/qsight/runq.js <spec.json> [--jobs 3] [--cap 6]   (exp/v16/runq.js's copy: an opponent may also be a bot dir path from the repo
//   root, e.g. exp/q2/bot-hunter; its key and row name it by the dir's base name)
//   spec: [{ "bot": dir, "out": dir, "opps": [..], "seeds": [..], "maps": dir, "sides": ["A","B"], "only": [map names] (optional),
//           "cpu": true (optional: unswbc -v, the judge's points per turn of both teams go into the row as cpu) }, ...]
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'viewer.js'));
const args = process.argv.slice(2), get = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const spec = JSON.parse(fs.readFileSync(args[0], 'utf8')), jobs = +get('--jobs', 3), cap = +get('--cap', 6);
const MIN_FREE = 21 * 1024 ** 3;
const clean = r => r.G !== undefined && r.exit === 0 && !r.error && !r.botProblem;
const lanes = spec.map(s => {
  const bot = path.resolve(ROOT, s.bot), out = path.resolve(ROOT, s.out), mapDir = path.resolve(ROOT, s.maps);
  fs.mkdirSync(path.join(out, 'games'), { recursive: true });
  const rowsFile = path.join(out, 'rows.jsonl');
  const done = new Set(fs.existsSync(rowsFile) ? fs.readFileSync(rowsFile, 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l)).filter(clean).map(r => r.key) : []);
  const maps = fs.readdirSync(mapDir).filter(f => f.endsWith('.map') && (!s.only || s.only.includes(f.replace('.map', '')))).sort();
  const tasks = [];
  for (const opp of s.opps) for (const map of maps) for (const side of s.sides || ['A', 'B']) for (const seed of s.seeds) {
    const key = [path.basename(opp), map.replace('.map', ''), side, seed].join(':');
    if (!done.has(key)) tasks.push({ key, opp, map, side, seed, bot, out, mapDir, rowsFile, cpu: !!s.cpu });
  }
  return tasks;
});
const tasks = []; for (let i = 0; lanes.some(l => i < l.length); i++) for (const l of lanes) if (i < l.length) tasks.push(l[i]);   // interleave the sets
const running = () => { try { return +cp.execSync('pgrep -f "unswbc-clean.py run" | wc -l').toString().trim(); } catch { return 0; } };
const diskFree = () => { const d = fs.statfsSync(ROOT); return d.bavail * d.bsize; };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const run = t => new Promise(res => {
  const dir = path.join(t.out, 'games', t.key.replace(/:/g, '_')); fs.mkdirSync(dir, { recursive: true });
  const oppDir = t.opp.includes('/') ? path.join(ROOT, t.opp) : path.join(ROOT, 'bots', t.opp), a = t.side === 'A' ? t.bot : oppDir, b = t.side === 'A' ? oppDir : t.bot;
  const p = cp.spawn('nice', ['-n', '10', path.join(ROOT, 'tools', 'unswbc123'), 'run', path.join(t.mapDir, t.map), a, b, '--sandbox', '--seed', String(t.seed), '--no-logs', '--no-draw', '-o', path.join(dir, 'game.replay'), ...(t.cpu ? ['-v'] : [])], { cwd: dir });
  let log = ''; p.stdout.on('data', d => log += d); p.stderr.on('data', d => log += d);
  p.on('close', code => {
    const row = { key: t.key, opp: path.basename(t.opp), map: t.map.replace('.map', ''), side: t.side, seed: t.seed, exit: code };
    try {
      const R = load(dir), us = R.result['team' + t.side], th = R.result['team' + (t.side === 'A' ? 'B' : 'A')];
      Object.assign(row, { G: us.dragonCount > 0 ? us.longestDragon : 0, alive: us.dragonCount > 0, total: us.totalLength, units: us.dragonCount, theirLongest: th.longestDragon, won: R.result.winner === t.side, endReason: R.result.endReason });
    } catch (e) { row.error = String(e).slice(0, 200); }
    if (code !== 0 && !row.error) row.error = 'exit ' + code;
    if (t.cpu) row.cpu = log.split('\n').filter(l => /points per turn/i.test(l)).map(l => l.trim());
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
    while (live >= jobs || running() >= cap) await sleep(3000);
    if (diskFree() < MIN_FREE) { console.log(new Date().toTimeString().slice(0, 8), 'disk free < 21 GiB: stop launching'); break; }
    live++; run(t).then(() => live--);
    await sleep(2000);   // let the launched judge show up in pgrep before the next check
  }
  while (live > 0) await sleep(2000);
  console.log(new Date().toTimeString().slice(0, 8), 'all done');
})();
