#!/usr/bin/env node
// Q1b2 identity (Q1.md §11 criterion 2): per key, the first round at which the Q1b2 game differs from the Q1b game, against the round of our
// queen's first feed indicator ("feed #", from r300) in the Q1b game. No queen feed in Q1b -> identical to the end; else the first difference
// is that round. usage: node exp/v16/q1/ana/q1b2id.js <q1b2 dir> <q1b dir>
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..', '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const load = makeLoader(viewerSource());
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
const [A, B] = process.argv.slice(2).map(d => path.resolve(ROOT, d));
const flat = (file, side) => {
  const R = load(file), out = []; let round = 0, Q = null, qFeed = null;
  for (const d of R.match.map.initialDragons) if (d.team === side && (Q === null || d.id < Q)) Q = d.id;
  for (const e of R.events) {
    if (e.type === 'roundStart') round++;
    if (e.type === 'dragonIndicator' && e.id === Q && round >= 300 && qFeed === null && /^feed #/.test(e.text || '')) qFeed = round;
    if (SKIP.has(e.type)) continue;
    const o = {}; for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; }
    out.push([round, JSON.stringify(o)]);
  }
  return { out, qFeed };
};
let ok = 0, bad = 0, same = 0;
for (const l of fs.readFileSync(path.join(A, 'rows.jsonl'), 'utf8').trim().split('\n')) {
  const row = JSON.parse(l), k = row.key.replace(/:/g, '_');
  const fa = path.join(A, 'games', k, 'game.replay'), fb = path.join(B, 'games', k, 'game.replay');
  if (!fs.existsSync(fa) || !fs.existsSync(fb)) continue;
  const a = flat(fa, row.side), b = flat(fb, row.side);
  let i = 0; while (i < a.out.length && i < b.out.length && a.out[i][1] === b.out[i][1]) i++;
  const identical = i === a.out.length && i === b.out.length, dr = identical ? null : (i < a.out.length ? a.out[i][0] : b.out[i][0]);
  // the queen's feed decision at round q is taken during round q; the action shows in the same round's events
  // (a feed's first step can coincide with the move Q1b2 makes instead, so a later first difference is consistent too)
  const good = b.qFeed === null ? identical : identical || dr >= b.qFeed;
  if (identical) same++;
  if (good) ok++; else bad++;
  if (!identical || b.qFeed !== null) console.log(`${k}: Q1b queen feed ${b.qFeed === null ? 'none' : 'r' + b.qFeed}; ${identical ? 'identical' : 'first difference r' + dr} ${good ? 'OK' : 'UNEXPECTED'}`);
}
console.log(`${ok} OK (${same} identical), ${bad} unexpected (${path.relative(ROOT, A)} vs ${path.relative(ROOT, B)})`);
