#!/usr/bin/env node
// v1.6g: the first round at which two local sets' replays of the same key differ (the event stream of exp/v16/identity.js: no indicator, log or draw
// events, no instruction counts). usage: node exp/v16/firstdiff.js <dirA> <dirB> [--keys <regex>]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
const flat = file => {
  const out = []; let round = 0;
  for (const e of load(file).events) {
    if (e.type === 'roundStart') round++;
    if (SKIP.has(e.type)) continue;
    const o = {}; for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; }
    out.push([round, JSON.stringify(o)]);
  }
  return out;
};
const [A, B] = process.argv.slice(2, 4).map(d => path.resolve(ROOT, d));
const ki = process.argv.indexOf('--keys'), re = ki > 0 ? new RegExp(process.argv[ki + 1]) : null;
const games = d => new Set(fs.existsSync(path.join(d, 'games')) ? fs.readdirSync(path.join(d, 'games')).filter(k => fs.existsSync(path.join(d, 'games', k, 'game.replay'))) : []);
const ga = games(A), gb = games(B);
for (const k of [...ga].filter(k => gb.has(k) && (!re || re.test(k))).sort()) {
  const a = flat(path.join(A, 'games', k, 'game.replay')), b = flat(path.join(B, 'games', k, 'game.replay'));
  let i = 0; while (i < a.length && i < b.length && a[i][1] === b[i][1]) i++;
  console.log(`${k}: ${i === a.length && i === b.length ? 'IDENTICAL' : 'first difference in round ' + (i < a.length ? a[i][0] : b[i][0])} (events ${a.length} / ${b.length})`);
}
