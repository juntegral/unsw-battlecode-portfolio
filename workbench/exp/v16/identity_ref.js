#!/usr/bin/env node
// v1.6: compare a local set's replay hashes (tools/fingerprint.js's hash, exp/v16/identity.js) with the v1.3 hashes recorded in exp/v16/identity.txt
// (the second hash of each line whose comparison had a v1.3 set second: p13-*, id-13-*). usage: node exp/v16/identity_ref.js <dir>
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
function hashReplay(file) {
  const R = load(file), h = crypto.createHash('sha256'); let n = 0;
  for (const e of R.events) { if (SKIP.has(e.type)) continue; const o = {}; for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; } h.update(JSON.stringify(o)); n++; }
  return h.digest('hex').slice(0, 16);
}
const ref = new Map(); let block = [];
for (const l of fs.readFileSync(path.join(__dirname, 'identity.txt'), 'utf8').split('\n')) {
  const m = /^(\S+): ([0-9a-f]{16}) vs ([0-9a-f]{16})/.exec(l);
  if (m) { block.push([m[1], m[3]]); continue; }
  const s = / vs (exp\/v16\/(p13-[ab]|id-13-\w+))\)/.exec(l);
  if (s) for (const [k, h] of block) ref.set(k, h);
  if (/identical \(/.test(l)) block = [];
}
const dir = path.resolve(ROOT, process.argv[2]);
let same = 0, n = 0;
for (const k of fs.readdirSync(path.join(dir, 'games')).sort()) {
  const f = path.join(dir, 'games', k, 'game.replay'); if (!fs.existsSync(f) || !ref.has(k)) continue;
  const h = hashReplay(f); n++; if (h === ref.get(k)) same++;
  console.log(`${k}: ${h} vs v1.3 ${ref.get(k)} ${h === ref.get(k) ? 'IDENTICAL' : 'DIFFERENT'}`);
}
console.log(`${same}/${n} identical (${path.relative(ROOT, dir)} vs the recorded v1.3 hashes)`);
process.exit(same === n && n > 0 ? 0 : 1);
