#!/usr/bin/env node
// v1.6 identity: tools/fingerprint.js's hash (the event stream without indicator, log and draw events and without instruction counts) of the replays
// of two local sets (exp/v16/runq.js layout), compared key by key. usage: node exp/v16/identity.js <dirA> <dirB> [--keys <regex>]
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
function hashReplay(file) {   // tools/fingerprint.js hashReplay, unchanged
  const R = load(file), h = crypto.createHash('sha256'); let n = 0;
  for (const e of R.events) {
    if (SKIP.has(e.type)) continue;
    const o = {}; for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; }
    h.update(JSON.stringify(o)); n++;
  }
  return { hash: h.digest('hex').slice(0, 16), events: n };
}
const [A, B] = process.argv.slice(2, 4).map(d => path.resolve(ROOT, d));
const ki = process.argv.indexOf('--keys'), re = ki > 0 ? new RegExp(process.argv[ki + 1]) : null;
const games = d => new Set(fs.existsSync(path.join(d, 'games')) ? fs.readdirSync(path.join(d, 'games')).filter(k => fs.existsSync(path.join(d, 'games', k, 'game.replay'))) : []);
const ga = games(A), gb = games(B);
let same = 0, n = 0;
for (const k of [...ga].filter(k => gb.has(k) && (!re || re.test(k))).sort()) {
  const a = hashReplay(path.join(A, 'games', k, 'game.replay')), b = hashReplay(path.join(B, 'games', k, 'game.replay'));
  n++; if (a.hash === b.hash) same++;
  console.log(`${k}: ${a.hash} vs ${b.hash} ${a.hash === b.hash ? 'IDENTICAL' : 'DIFFERENT'} (events ${a.events} / ${b.events})`);
}
console.log(`${same}/${n} identical (${path.relative(ROOT, A)} vs ${path.relative(ROOT, B)})`);
process.exit(same === n && n > 0 ? 0 : 1);
