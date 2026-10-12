#!/usr/bin/env node
// v1.5 identity on any map file and side (tools/fingerprint.js --same plays only maps/online-20260927 with our bot on side A): two bots, the same
// map, opponent, side and seed, one game at a time; equal event-stream hashes (tools/fingerprint.js hashReplay: actions, moves, splits, deaths,
// pearls; not indicators or instruction counts) = the same game. Each launch waits below the machine cap and stops below 21 GiB free.
// usage: node exp/v15/fp.js <botA> <botB> --maps maps/server-b/queen_of_spades_b.map,... [--sides A,B] [--seeds 1,2] [--opp bots/proxy4_king]
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process'), os = require('os');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const crypto = require('crypto');
let load = null;
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
function hashReplay(file) {   // tools/fingerprint.js hashReplay
  if (!load) load = makeLoader(viewerSource());
  const R = load(file), h = crypto.createHash('sha256');
  let n = 0;
  for (const e of R.events) {
    if (SKIP.has(e.type)) continue;
    const o = {};
    for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; }
    h.update(JSON.stringify(o)); n++;
  }
  return { hash: h.digest('hex').slice(0, 16), events: n };
}
const args = process.argv.slice(2), get = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const [botA, botB] = args;
const maps = get('--maps', '').split(',').filter(Boolean), sides = get('--sides', 'A').split(','), seeds = get('--seeds', '1').split(',').map(Number);
const opp = path.resolve(ROOT, get('--opp', 'bots/proxy4_king'));
const running = () => { try { return +cp.execSync('pgrep -f "unswbc-clean.py run" | wc -l').toString().trim(); } catch { return 0; } };
const sleep = ms => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
function play(bot, map, side, seed) {
  while (running() >= 6) sleep(2000);
  const st = fs.statfsSync(ROOT); if (st.bavail * st.bsize < 21 * 1024 ** 3) { console.log('disk < 21 GiB: stop'); process.exit(2); }
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fp15-')), out = path.join(dir, 'game.replay');
  const a = side === 'A' ? path.resolve(ROOT, bot) : opp, b = side === 'A' ? opp : path.resolve(ROOT, bot);
  cp.execFileSync('nice', ['-n', '10', path.join(ROOT, 'tools', 'unswbc'), 'run', path.resolve(ROOT, map), a, b, '--sandbox', '--seed', String(seed), '--no-logs', '--no-draw', '-o', out], { cwd: dir, stdio: 'ignore' });
  const r = hashReplay(out); fs.rmSync(dir, { recursive: true, force: true }); return r;
}
let same = 0, total = 0;
for (const m of maps) for (const side of sides) for (const seed of seeds) {
  const ra = play(botA, m, side, seed), rb = play(botB, m, side, seed);
  const eq = ra.hash === rb.hash; total++; if (eq) same++;
  console.log(`${path.basename(m)} side ${side} seed ${seed}: ${ra.hash} vs ${rb.hash} ${eq ? 'IDENTICAL' : 'DIFFERENT'} (events ${ra.events} / ${rb.events})`);
}
console.log(`${same}/${total} identical`);
process.exit(same === total ? 0 : 1);
