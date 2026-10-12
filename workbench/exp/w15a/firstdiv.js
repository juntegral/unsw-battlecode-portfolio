#!/usr/bin/env node
// W15a: the first event where two replays of the same key differ (indicators, logs and instruction counts ignored), with the acting dragon's
// indicator in each that turn. usage: node exp/w15a/firstdiv.js <base replay> <new replay>
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
const load = makeLoader(viewerSource());
const [fa, fb] = process.argv.slice(2);
const A = load(fa).events, B = load(fb).events;
const norm = e => { const o = {}; for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; } return JSON.stringify(o); };
const fil = E => E.map((e, i) => [e, i]).filter(([e]) => !SKIP.has(e.type));
const a = fil(A), b = fil(B);
let r = 0;
for (let i = 0; i < Math.max(a.length, b.length); i++) {
  const [ea, ia] = a[i] || [], [eb, ib] = b[i] || [];
  if (ea && ea.type === 'roundStart') r = ea.round;
  if (ea && eb && norm(ea) === norm(eb)) continue;
  // the indicator of the dragon acting: the last indicator before this event in each stream for the event's dragon id
  const id = (ea && (ea.id ?? ea.parentId)) ?? (eb && (eb.id ?? eb.parentId));
  const ind = (E, upto) => { for (let j = upto; j >= 0; j--) if (E[j].type === 'dragonIndicator' && E[j].id === id) return E[j].text; return '?'; };
  const near = (E, from) => { for (let j = from; j < Math.min(E.length, from + 40); j++) if (E[j].type === 'dragonIndicator' && E[j].id === id) return E[j].text; return '?'; };
  console.log(`r${r} first difference, dragon #${id}`);
  console.log(`  base: ${ea ? norm(ea).slice(0, 220) : '(end)'}\n        indicator: ${ind(A, ia ?? A.length - 1)} | next: ${near(A, (ia ?? 0) + 1)}`);
  console.log(`  new:  ${eb ? norm(eb).slice(0, 220) : '(end)'}\n        indicator: ${ind(B, ib ?? B.length - 1)} | next: ${near(B, (ib ?? 0) + 1)}`);
  break;
}
