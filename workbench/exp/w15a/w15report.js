#!/usr/bin/env node
// W15a report: base and new sets on the same keys (exp/v14/runq14.js layout). Per game: strict identity (tools/fingerprint.js: every event
// but indicators, logs and instruction counts), the first round where the event streams differ, the W15a tags in our indicators (" ds",
// " dk<n>", " et<j>": count and first round) and the result row (G, won). Identity is expected wherever no tag fired before the divergence.
// usage: node exp/w15a/w15report.js --base exp/w15a/base --new exp/w15a/t [--keys <regex>]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);   // as tools/fingerprint.js
const arg = k => { const i = process.argv.indexOf(k); return i >= 0 ? process.argv[i + 1] : null; };
const baseDir = arg('--base'), newDir = arg('--new'), keyRe = arg('--keys') ? new RegExp(arg('--keys')) : null;
const rows = d => new Map(fs.readFileSync(path.join(d, 'rows.jsonl'), 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l)).map(r => [r.key, r]));
const B = rows(baseDir), N = rows(newDir);
const load = makeLoader(viewerSource());
const gameFile = (d, r) => path.join(d, 'games', `${r.opp}_${r.map}_${r.side}_${r.seed}`, 'game.replay');
const norm = e => { const o = {}; for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; } return JSON.stringify(o); };
let same = 0, tot = 0, untaggedSame = 0, untagged = 0, explained = 0, unexplained = [];
const tagTot = { ds: 0, dk: 0, et: 0 };
for (const [key, rb] of B) {
  if (keyRe && !keyRe.test(key)) continue;
  const rn = N.get(key); if (!rn) continue;
  let RB, RN; try { RB = load(gameFile(baseDir, rb)); RN = load(gameFile(newDir, rn)); } catch (e) { console.log(key, 'unreadable', e.message); continue; }
  const eb = RB.events.filter(e => !SKIP.has(e.type)), en = RN.events.filter(e => !SKIP.has(e.type));
  let div = -1, round = 0;
  for (let i = 0; i < Math.max(eb.length, en.length); i++) {
    const a = eb[i], b = en[i];
    if (a && a.type === 'roundStart') round = a.round;
    if (!a || !b || norm(a) !== norm(b)) { div = round; break; }
  }
  // our tags in the new game
  const us = rn.side, ourIds = new Set();
  for (const d of RN.match.map.initialDragons || []) if (d.team === us) ourIds.add(d.id);
  const tags = { ds: 0, dk: 0, et: 0 }, first = {}; let r = 0;
  const RE = { ds: /(^| )ds( |$)/, dk: /(^| )dk\d+( |$)/, et: /(^| )et\d+( |$)/ };
  for (const e of RN.events) {
    if (e.type === 'roundStart') r = e.round;
    if (e.type === 'dragonSplit' && e.team === us) ourIds.add(e.childId);
    if (e.type !== 'dragonIndicator' || !e.text || !ourIds.has(e.id)) continue;
    for (const t of ['ds', 'dk', 'et']) if (RE[t].test(e.text)) { tags[t]++; if (first[t] == null) first[t] = r; }
  }
  tot++; const ident = div < 0; if (ident) same++;
  const tagged = tags.ds + tags.dk + tags.et > 0, firstTag = Math.min(...Object.values(first).concat([Infinity]));
  for (const t in tags) tagTot[t] += tags[t];
  if (!tagged) { untagged++; if (ident) untaggedSame++; else unexplained.push(key + ' diverges r' + div + ' without a tag'); }
  else if (!ident) { if (firstTag <= div) explained++; else unexplained.push(`${key} diverges r${div} before its first tag r${firstTag}`); }
  console.log(`${key.padEnd(36)} ${ident ? 'identical ' : 'diverge r' + String(div).padEnd(4)} tags ds ${tags.ds} dk ${tags.dk} et ${tags.et}${tagged ? ' (first r' + firstTag + ')' : ''}  G ${rb.G} -> ${rn.G}${rb.won !== rn.won ? ` won ${rb.won} -> ${rn.won}` : ''}`);
}
console.log(`== identical ${same}/${tot}; games without a tag: ${untaggedSame}/${untagged} identical; diverged after a tag: ${explained}; tags ${JSON.stringify(tagTot)}`);
for (const u of unexplained) console.log('   UNEXPLAINED ' + u);
