#!/usr/bin/env node
// v1.6h H3 breakage check: per game, the first round any dragon of ours tags " sg" (the spread gate open, FORTRESS-late CONV2) against the first round
// at which the game differs from a reference set (exp/v16/firstdiff.js's event stream). Before the first gated turn the FORTRESS path must be v1.3's.
// usage: node exp/v16/sgdiff.js <dir> <reference dir>[?|!regex] [--keys regex]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const load = makeLoader(viewerSource());
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
const [A, Bspec] = process.argv.slice(2, 4);
const fm = /^([^?!]+)([?!])(.+)$/.exec(Bspec), B = fm ? fm[1] : Bspec, okB = fm ? (k => new RegExp(fm[3]).test(k) === (fm[2] === '?')) : (() => true);
const ki = process.argv.indexOf('--keys'), re = ki > 0 ? new RegExp(process.argv[ki + 1]) : null;
const dirA = path.resolve(ROOT, A), dirB = path.resolve(ROOT, B);
const rows = new Map(fs.readFileSync(path.join(dirA, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l)).map(r => [r.key.replace(/:/g, '_'), r]));
const flat = (file, us) => {
  const out = []; let round = 0, sg = null; const R = load(file);
  const teamOf = new Map(); for (const d of R.match.map.initialDragons) teamOf.set(d.id, d.team);
  for (const e of R.events) {
    if (e.type === 'roundStart') round++;
    if (e.type === 'dragonSplit' && e.childId !== undefined && e.parentId !== undefined) teamOf.set(e.childId, teamOf.get(e.parentId));
    if (e.type === 'dragonIndicator') { if (sg === null && / sg(\s|$)/.test(e.text || '') && (teamOf.get(e.id) === us || teamOf.get(e.id) === undefined)) sg = round; continue; }
    if (SKIP.has(e.type)) continue;
    const o = {}; for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; }
    out.push([round, JSON.stringify(o)]);
  }
  return { out, sg };
};
let ok = 0, bad = 0, nosg = 0;
for (const [k, row] of [...rows.entries()].sort()) {
  if (re && !re.test(k)) continue;
  if (!okB(row.key)) continue;
  const fa = path.join(dirA, 'games', k, 'game.replay'), fb = path.join(dirB, 'games', k, 'game.replay');
  if (!fs.existsSync(fa) || !fs.existsSync(fb)) continue;
  const a = flat(fa, row.side), b = flat(fb, row.side);
  let i = 0; while (i < a.out.length && i < b.out.length && a.out[i][1] === b.out[i][1]) i++;
  const same = i === a.out.length && i === b.out.length, diffR = same ? null : (i < a.out.length ? a.out[i][0] : b.out[i][0]);
  const good = a.sg === null ? same : (same || diffR >= a.sg);
  if (a.sg === null) nosg++;
  if (good) ok++; else bad++;
  console.log(`${k}: first sg ${a.sg === null ? '-' : 'r' + a.sg}, ${same ? 'identical' : 'first difference r' + diffR} ${good ? 'OK' : 'BEFORE THE GATE'}`);
}
console.log(`${ok} OK, ${bad} differ before the first gated turn (${nosg} games without a gated turn) (${path.relative(ROOT, dirA)} vs ${Bspec})`);
