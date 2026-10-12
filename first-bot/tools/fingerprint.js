#!/usr/bin/env node
// Behaviour fingerprint: a hash of a game's event stream (actions, moves, splits, deaths, pearls; not timing or
// instruction counts and not our indicator text). Two bot versions that should behave identically (a refactor, or a
// new mechanism with its toggle off) must give identical fingerprints on the same map, opponent and seed. This is the
// "deterministic bench" practice from the coding deep research (research/external/INTEGRATION-2026-09-30.md).
// usage:
//   node tools/fingerprint.js <file.replay> [...]                       hash existing replays
//   node tools/fingerprint.js --run <botDir> <map.map> <oppDir> <seed>  play one sandboxed game and hash it
//   node tools/fingerprint.js --same <botA> <botB> [--maps a,b] [--opp bots/proxy4_king] [--seed 1]
//                                                                      compare two bots game by game
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..');
const { makeLoader, viewerSource } = require('./top_features.js');
let load = null;
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
function hashReplay(file) {
  if (!load) load = makeLoader(viewerSource());
  const R = load(file), h = crypto.createHash('sha256');
  let n = 0;
  for (const e of R.events) {
    if (SKIP.has(e.type)) continue;
    const o = {};
    for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; }
    h.update(JSON.stringify(o)); n++;
  }
  return { hash: h.digest('hex').slice(0, 16), events: n, rounds: R.result ? R.result.rounds || null : null };
}
function runGame(bot, map, opp, seed) {
  const dir = fs.mkdtempSync(path.join(require('os').tmpdir(), 'fp-'));
  const out = path.join(dir, 'game.replay');
  cp.execFileSync(path.join(__dirname, 'unswbc'), ['run', path.resolve(ROOT, map), path.resolve(ROOT, bot), path.resolve(ROOT, opp), '--sandbox', '--seed', String(seed), '--no-logs', '--no-draw', '-o', out], { cwd: dir, stdio: ['ignore', 'ignore', 'ignore'] });
  const r = hashReplay(out); fs.rmSync(dir, { recursive: true, force: true }); return r;
}
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
if (argv[0] === '--run') {
  const [bot, map, opp, seed] = argv.slice(1);
  const r = runGame(bot, map, opp, +seed); console.log(`${r.hash} events ${r.events}`);
} else if (argv[0] === '--same') {
  const [a, b] = argv.slice(1, 3);
  const maps = (opt('--maps', 'portals,slithery_fight')).split(',').map(m => `maps/online-20260927/${m}.map`);
  const opp = opt('--opp', 'bots/proxy4_king'), seed = +opt('--seed', 1);
  let same = 0;
  for (const m of maps) {
    const ra = runGame(a, m, opp, seed), rb = runGame(b, m, opp, seed);
    const eq = ra.hash === rb.hash; if (eq) same++;
    console.log(`${path.basename(m)}: ${ra.hash} vs ${rb.hash} ${eq ? 'IDENTICAL' : 'DIFFERENT'} (events ${ra.events} / ${rb.events})`);
  }
  console.log(`${same}/${maps.length} identical`); process.exit(same === maps.length ? 0 : 1);
} else {
  if (!argv.length) { console.error('usage: fingerprint.js <file.replay> ... | --run <bot> <map> <opp> <seed> | --same <botA> <botB>'); process.exit(2); }
  for (const f of argv) { const r = hashReplay(f); console.log(`${r.hash} events ${r.events} ${f}`); }
}
