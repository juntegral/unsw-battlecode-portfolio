#!/usr/bin/env node
// exp/gen/PLAN.md §3.2: the event-stream hash (tools/fingerprint.js hashReplay: actions, moves, splits, deaths, pearls; not indicators) of each
// game in a check set against the game with the same key in the reference set
// usage: node exp/gen/idcheck.js <check dir> <reference dir> [more pairs ...]
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
function hash(file) {
  const R = load(file), h = crypto.createHash('sha256'); let n = 0;
  for (const e of R.events) { if (SKIP.has(e.type)) continue; const o = {}; for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; } h.update(JSON.stringify(o)); n++; }
  return h.digest('hex').slice(0, 16) + ' ' + n;
}
const a = process.argv.slice(2); let same = 0, total = 0;
for (let i = 0; i + 1 < a.length; i += 2) {
  const [chk, ref] = [a[i], a[i + 1]];
  for (const l of fs.readFileSync(path.join(chk, 'rows.jsonl'), 'utf8').trim().split('\n')) {
    const r = JSON.parse(l); if (r.G === undefined) continue;
    const g = r.key.replace(/:/g, '_'), f1 = path.join(chk, 'games', g, 'game.replay'), f2 = path.join(ref, 'games', g, 'game.replay');
    if (!fs.existsSync(f1) || !fs.existsSync(f2)) { console.log(`${chk} ${r.key}: missing replay`); continue; }
    const h1 = hash(f1), h2 = hash(f2); total++; if (h1 === h2) same++;
    console.log(`${path.basename(chk)} vs ${path.basename(ref)} ${r.key}: ${h1 === h2 ? 'IDENTICAL' : 'DIFFERENT'} (${h1} / ${h2})`);
  }
}
console.log(`${same}/${total} identical`);
process.exit(same === total ? 0 : 1);
