#!/usr/bin/env node
// v1.1 identity check (versions/v1.1/VERSION.md §3): the beacon-off build (exp/v11/bot-beaconoff) against v1 (versions/v1/bot) on the fortress maps,
// game by game on the same key (map, side, seed, opponent): tools/fingerprint.js's event hash (actions, moves, splits, deaths, pearls, sonar; not
// indicators or instruction counts). Same as `tools/fingerprint.js --same versions/v1/bot exp/v11/bot-beaconoff --maps ... --seed s` (our bot team A).
// usage: node exp/v11/identity.js <setA dir> <setB dir> [--label text]
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const [a, b] = process.argv.slice(2, 4);
const rows = d => new Map(fs.readFileSync(path.join(d, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined).map(r => [r.key, r]));
const ra = rows(a), rb = rows(b);
const hash = f => cp.execFileSync('node', [path.join(ROOT, 'tools', 'fingerprint.js'), f]).toString().trim().split(/\s+/);
let same = 0, n = 0;
const out = [];
for (const k of [...ra.keys()].sort()) {
  if (!rb.has(k)) continue;
  const f = d => path.join(d, 'games', k.replace(/:/g, '_'), 'game.replay');
  const [ha, , ea] = hash(f(a)), [hb, , eb] = hash(f(b));
  n++; if (ha === hb) same++;
  out.push(`${k}: ${ha} vs ${hb} ${ha === hb ? 'IDENTICAL' : 'DIFFERENT'} (events ${ea} / ${eb})`);
}
out.push(`${same}/${n} identical`);
console.log(out.join('\n'));
process.exit(same === n && n > 0 ? 0 : 1);
