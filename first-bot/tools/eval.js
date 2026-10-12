#!/usr/bin/env node
// Fixed local benchmark E1 (commander-side progress measurement; lineages may use it too).
// usage: node tools/eval.js --bot <dir> --label <name> [--out <dir>] [--opps replay_rules_v8,archetype_swarm,archetype_hunter,h2]
//        [--seeds 1,2] [--jobs 2] [--maps maps/online-20260927] [--opponent-root bots] [--baseline <label>]
// Plays every map x both sides x seeds x opponents with the official 1.1.0 sandbox (tools/unswbc).
// Metric G = our longest living dragon at the end (0 if eliminated). Also survival and win.
// Results: <out>/rows.jsonl (one per game), <out>/summary.json. --baseline pairs by (opp,map,side,seed) with an earlier label.
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..');
const { load } = require(path.join(__dirname, 'viewer.js'));
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const bot = path.resolve(arg('bot', '')), label = arg('label', ''), out = path.resolve(arg('out', path.join(ROOT, 'exp', label)));
if (!fs.existsSync(bot) || !label) { console.error('need --bot <dir> --label <name>'); process.exit(2); }
const opps = arg('opps', 'replay_rules_v8,archetype_swarm,archetype_hunter,h2').split(',');
const opponentRoot = path.resolve(arg('opponent-root', path.join(ROOT, 'bots')));
const seeds = arg('seeds', '1,2').split(',').map(Number), jobs = +arg('jobs', '2');
const mapDir = path.resolve(ROOT, arg('maps', 'maps/online-20260927'));
const maps = fs.readdirSync(mapDir).filter(f => f.endsWith('.map')).sort();
fs.mkdirSync(path.join(out, 'games'), { recursive: true });
const rowsFile = path.join(out, 'rows.jsonl');
// Single-runner guard: a rows file written in the last 10 minutes means another eval for this label is running.
try { if (!process.argv.includes('--force') && Date.now() - fs.statSync(rowsFile).mtimeMs < 600000) { console.log(JSON.stringify({ label, skipped: 'another eval for this label wrote rows in the last 10 min' })); process.exit(0); } } catch {}
const done = new Set(fs.existsSync(rowsFile) ? fs.readFileSync(rowsFile, 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l).key) : []);
const tasks = [];
for (const opp of opps) for (const map of maps) for (const side of ['A', 'B']) for (const seed of seeds) {
  const key = [opp, map.replace('.map', ''), side, seed].join(':');
  if (!done.has(key)) tasks.push({ key, opp, map, side, seed });
}
const run = t => new Promise(res => {
  const disk = fs.statfsSync(ROOT);
  if (disk.bavail * disk.bsize < 20 * 1024 ** 3) {
    fs.appendFileSync(rowsFile, JSON.stringify({ ...t, exit: null, error: 'disk free < 20 GiB; game not started' }) + '\n');
    return res();
  }
  const dir = path.join(out, 'games', t.key.replace(/:/g, '_')); fs.mkdirSync(dir, { recursive: true });
  const oppDir = path.join(opponentRoot, t.opp), a = t.side === 'A' ? bot : oppDir, b = t.side === 'A' ? oppDir : bot;
  const p = cp.spawn(path.join(__dirname, 'unswbc'), ['run', path.join(mapDir, t.map), a, b, '--sandbox', '--seed', String(t.seed), '--no-logs', '--no-draw', '-o', path.join(dir, 'game.replay')], { cwd: dir });
  let log = '', spawnError; p.stdout.on('data', d => log += d); p.stderr.on('data', d => log += d);
  p.on('error', e => { spawnError = String(e); });
  p.on('close', code => {
    const row = { key: t.key, opp: t.opp, map: t.map.replace('.map', ''), side: t.side, seed: t.seed, exit: code };
    if (spawnError) row.error = spawnError;
    try {
      const R = load(dir), us = R.result['team' + t.side], th = R.result['team' + (t.side === 'A' ? 'B' : 'A')];
      Object.assign(row, { G: us.dragonCount > 0 ? us.longestDragon : 0, alive: us.dragonCount > 0, total: us.totalLength, units: us.dragonCount, theirLongest: th.longestDragon, won: R.result.winner === t.side, endReason: R.result.endReason });
    } catch (e) { row.error = String(e).slice(0, 200); }
    if (/no reply|timed out|exceeded|Traceback|error:/i.test(log)) row.botProblem = (log.match(/.*(no reply|timed out|exceeded|Traceback|error:).*/i) || [''])[0].slice(0, 200);
    fs.appendFileSync(rowsFile, JSON.stringify(row) + '\n'); res();
  });
});
(async () => {
  let i = 0; const workers = Array.from({ length: jobs }, async () => { while (i < tasks.length) await run(tasks[i++]); });
  await Promise.all(workers);
  const seen = new Set();                          // duplicates (e.g. from concurrent runs) count once: keep the first row per key
  const rows = fs.readFileSync(rowsFile, 'utf8').trim().split('\n').map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(r => r && r.G !== undefined && !seen.has(r.key) && seen.add(r.key));
  const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : null;
  const sum = rs => ({ n: rs.length, G: mean(rs.map(r => r.G)), alive: mean(rs.map(r => +r.alive)), win: mean(rs.map(r => +r.won)) });
  const summary = { label, bot, at: new Date().toISOString(), benchmark: { maps: maps.length, opps, seeds, sides: 2 }, all: sum(rows), byOpp: Object.fromEntries(opps.map(o => [o, sum(rows.filter(r => r.opp === o))])), problems: rows.filter(r => r.botProblem || r.exit).length, errors: fs.readFileSync(rowsFile, 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.error).length };
  const base = arg('baseline');
  if (base) {
    const bf = path.join(ROOT, 'exp', base, 'rows.jsonl');
    if (fs.existsSync(bf)) {
      const bm = new Map(fs.readFileSync(bf, 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined).map(r => [r.key, r]));
      const pairs = rows.filter(r => bm.has(r.key)).map(r => ({ map: r.map, d: r.G - bm.get(r.key).G }));
      const byMap = [...new Set(pairs.map(p => p.map))].map(m => pairs.filter(p => p.map === m));
      let s = 20260927; const rnd = () => (s = (Math.imul(s, 1103515245) + 12345) >>> 0) / 4294967296; const reps = [];
      for (let k = 0; k < 4000; k++) { const pick = byMap.map(() => byMap[Math.floor(rnd() * byMap.length)]).flat(); reps.push(mean(pick.map(p => p.d))); }
      reps.sort((a, b) => a - b);
      summary.vsBaseline = { baseline: base, pairs: pairs.length, dG: mean(pairs.map(p => p.d)), ci95: [reps[Math.floor(0.025 * reps.length)], reps[Math.floor(0.975 * reps.length)]], note: 'map-cluster bootstrap' };
    }
  }
  fs.writeFileSync(path.join(out, 'summary.json'), JSON.stringify(summary, null, 2) + '\n');
  console.log(JSON.stringify({ label, n: summary.all.n, G: summary.all.G?.toFixed(2), alive: summary.all.alive?.toFixed(3), win: summary.all.win?.toFixed(3), problems: summary.problems, errors: summary.errors, vsBaseline: summary.vsBaseline && { dG: summary.vsBaseline.dG.toFixed(2), ci95: summary.vsBaseline.ci95.map(x => x.toFixed(2)) } }));
})();
