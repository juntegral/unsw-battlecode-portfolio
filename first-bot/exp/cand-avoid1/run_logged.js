#!/usr/bin/env node
// Runs benchmark games like tools/eval.js but keeps LOG lines in the replay (for the diag build of the baseline).
// usage: node exp/cand-avoid1/run_logged.js --bot exp/cand-avoid1/diag-base --out exp/cand-avoid1-diag [--opps archetype_hunter]
//        [--seeds 1,2] [--jobs 3] [--maps maps/online-20260927]
// Game folders are named like tools/eval.js (<opp>_<map>_<side>_<seed>/game.replay), so ram_audit.js --local reads them.
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const bot = path.resolve(ROOT, arg('bot', '')), out = path.resolve(ROOT, arg('out', ''));
const opps = arg('opps', 'archetype_hunter').split(','), seeds = arg('seeds', '1,2').split(',').map(Number), jobs = Math.min(3, +arg('jobs', '3'));
const mapDir = path.resolve(ROOT, arg('maps', 'maps/online-20260927'));
const maps = fs.readdirSync(mapDir).filter(f => f.endsWith('.map')).sort();
const tasks = [];
for (const opp of opps) for (const map of maps) for (const side of ['A', 'B']) for (const seed of seeds) {
  const dir = path.join(out, 'games', [opp, map.replace('.map', ''), side, seed].join('_'));
  if (!fs.existsSync(path.join(dir, 'game.replay'))) tasks.push({ opp, map, side, seed, dir });
}
const run = t => new Promise(res => {
  const disk = fs.statfsSync(ROOT);
  if (disk.bavail * disk.bsize < 20 * 1024 ** 3) { console.error('disk free < 20 GiB; not starting', t.dir); return res(); }
  fs.mkdirSync(t.dir, { recursive: true });
  const oppDir = path.join(ROOT, 'bots', t.opp), a = t.side === 'A' ? bot : oppDir, b = t.side === 'A' ? oppDir : bot;
  const p = cp.spawn(path.join(ROOT, 'tools', 'unswbc'), ['run', path.join(mapDir, t.map), a, b, '--sandbox', '--seed', String(t.seed), '--no-draw', '-o', path.join(t.dir, 'game.replay')], { cwd: t.dir });
  let log = ''; p.stdout.on('data', d => log += d); p.stderr.on('data', d => log += d);
  p.on('close', code => { if (code) console.error('exit', code, t.dir, log.slice(-300)); res(); });
});
(async () => {
  let i = 0; await Promise.all(Array.from({ length: jobs }, async () => { while (i < tasks.length) await run(tasks[i++]); }));
  console.log('done', tasks.length, 'games ->', path.relative(ROOT, out));
})();
