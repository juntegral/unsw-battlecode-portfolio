#!/usr/bin/env node
// v1.6g+H0 identity check (versions/v1.6/VERSION.md §12.2 item 3): per key, the first round at which the H0 game differs from v1.6g's, against the first
// round at which v1.6g's own replay shows an inflated king: one of our dragons declares (" ck#<id>") a dragon of ours whose true length is <= 3, or a
// labelled CONV2 feed goes to a king shorter than its gate (piece / mid: L + 2; merge: L). A game that differs before any such trace is listed.
// usage: node exp/v16/h0id.js <H0 dir> <v1.6g dir> [--map <name> <variant>]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const ML = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
const MAPS = { default: ['Default', 'a'], devil: ['Devil', 'a'], queen_of_spades: ['Queen Of Spades', 'a'], schooltime_b: ['Schooltime', 'b'], slithery_fight: ['Slithery Fight', 'a'],
  slithery_fight_b: ['Slithery Fight', 'b'], schooltime: ['Schooltime', 'a'], trauma: ['Trauma', 'a'] };
const [A, B] = process.argv.slice(2, 4).map(d => path.resolve(ROOT, d));
const flat = file => { const out = []; let round = 0; for (const e of load(file).events) { if (e.type === 'roundStart') round++; if (SKIP.has(e.type)) continue; const o = {}; for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; } out.push([round, JSON.stringify(o)]); } return out; };
function trace(file, row) {
  const [map, variant] = MAPS[row.map] || [row.map, '?'], us = row.side; let first = null, why = '';
  const last = new Map();
  ML.perGame(load(file), { map, variant }, {
    indicator(e, r, c) {
      const d = c.drag.get(e.id); if (!d || d.team !== us) return;
      last.set(e.id, [r, e.text || '']);
      if (first !== null) return;
      const m = / ck#(\d+)/.exec(e.text || ''); if (!m) return;
      const k = c.drag.get(+m[1]);
      if (k && k.team === us && k.body.length <= 3) { first = r; why = `#${e.id} declares #${m[1]} (true L${k.body.length})`; }
    },
    death(d, rec, i, o, r, c) {
      if (first !== null || d.team !== us) return;
      const t = last.get(d.id); if (!t || t[0] !== r) return;
      const m = /^feed #(\d+) d\d+ L(\d+) cv2 k(\d+)( m)?/.exec(t[1]); if (!m) return;
      const k = c.drag.get(+m[1]), L = +m[2];
      if (k && k.body.length < (m[4] ? L : L + 2)) { first = r; why = `feed L${L} into #${m[1]} (true L${k.body.length}, believed ${m[3]})`; }
    },
  });
  return { first, why };
}
const rows = new Map(fs.readFileSync(path.join(A, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l)).map(r => [r.key.replace(/:/g, '_'), r]));
let same = 0, explained = 0, unexplained = 0;
for (const [k, row] of [...rows.entries()].sort()) {
  const fa = path.join(A, 'games', k, 'game.replay'), fb = path.join(B, 'games', k, 'game.replay');
  if (!fs.existsSync(fa) || !fs.existsSync(fb)) continue;
  const a = flat(fa), b = flat(fb); let i = 0; while (i < a.length && i < b.length && a[i][1] === b[i][1]) i++;
  if (i === a.length && i === b.length) { same++; console.log(`${k}: identical`); continue; }
  const diffR = i < a.length ? a[i][0] : b[i][0], t = trace(fb, row);
  const ok = t.first !== null && t.first <= diffR;
  if (ok) explained++; else unexplained++;
  console.log(`${k}: first difference r${diffR}; v1.6g's first inflated-king trace ${t.first === null ? 'none' : 'r' + t.first + ' (' + t.why + ')'} ${ok ? 'EXPLAINED' : 'UNEXPLAINED'}`);
}
console.log(`${same} identical, ${explained} differ at or after an inflated-king trace, ${unexplained} differ without one (${path.relative(ROOT, A)} vs ${path.relative(ROOT, B)})`);
