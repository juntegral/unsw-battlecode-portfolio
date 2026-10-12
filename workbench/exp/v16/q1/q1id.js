#!/usr/bin/env node
// Q1 identity (exp/v16/q1/Q1.md §5.6): per key, the first round at which the Q1 game differs from the base game (the event stream of
// exp/v16/identity.js), against our queen's death round. Every game must be the base's before r300; a game whose queen died before r280
// (her news gone by r300) must be the base's to the end. usage: node exp/v16/q1/q1id.js <q1 dir> <base dir> [<base dir> ...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const load = makeLoader(viewerSource());
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
const [A, ...Bs] = process.argv.slice(2).map(d => path.resolve(ROOT, d));
const flat = file => { const out = []; let round = 0, qd = {}; const R = load(file); qd.init = R.match.map.initialDragons; for (const e of R.events) { if (e.type === 'roundStart') round++; if (e.type === 'dragonDeath' && (e.id === 0 || e.id === 1) && qd[e.id] === undefined) qd[e.id] = round; if (SKIP.has(e.type)) continue; const o = {}; for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; } out.push([round, JSON.stringify(o)]); } return { out, qd }; };
const rows = fs.readFileSync(path.join(A, 'rows.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
let same = 0, before300 = 0, deadEarlyDiff = 0, ok = 0;
for (const row of rows) {
  const k = row.key.replace(/:/g, '_'), fa = path.join(A, 'games', k, 'game.replay');
  const B = Bs.find(b => fs.existsSync(path.join(b, 'games', k, 'game.replay'))); if (!B || !fs.existsSync(fa)) continue;
  const a = flat(fa), b = flat(path.join(B, 'games', k, 'game.replay'));
  let Q = null; for (const d of b.qd.init) if (d.team === row.side && (Q === null || d.id < Q)) Q = d.id;   // our queen: our lowest starting id
  const qd = b.qd[Q];
  let i = 0; while (i < a.out.length && i < b.out.length && a.out[i][1] === b.out[i][1]) i++;
  const identical = i === a.out.length && i === b.out.length, dr = identical ? null : (i < a.out.length ? a.out[i][0] : b.out[i][0]);
  let verdict = 'OK';
  if (identical) same++;
  else if (dr < 300) { before300++; verdict = 'DIFFERS BEFORE r300'; }
  else if (qd !== undefined && qd < 280) { deadEarlyDiff++; verdict = 'DIFFERS though the queen died before r280'; }
  if (verdict === 'OK') ok++;
  console.log(`${k}: queen ${qd === undefined ? 'alive' : 'died r' + qd}; ${identical ? 'identical' : 'first difference r' + dr} ${verdict}`);
}
console.log(`${ok} OK (${same} identical), ${before300} differ before r300, ${deadEarlyDiff} differ though the queen died before r280 (${path.relative(ROOT, A)} vs ${Bs.map(b => path.relative(ROOT, b)).join(', ')})`);
