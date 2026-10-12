#!/usr/bin/env node
// Stage 2-3 selection for the endgame king study. Classes and their sizes over our online sets (500-round maps), and the
// replays to read, chosen by a rule fixed before reading: per class, the smallest FNV-1a hash of "<key>#<id>" (games not
// repeated), at most --per of them (default 2).
//   C1 root gathering episode (S58 + stack8) whose team longest at the start was not the final-king line member and whose family
//      ended by a labelled feed (mass sent to a dragon that did not become the final king).
//   C2 root gathering episode (S58 + stack8), start length >= 8, family ended by another cause (not a sacrifice).
//   C3 our final-king line member (S58 + stack8, games to r500) with the most turns within Manhattan 3 of an enemy head in r300-399.
//   C3b the same as C3 without Portals (added before reading: Manhattan distance crosses the Portals walls).
//   C4 elite reference: our opponent's final king that came from the r340 non-king cohort with rank >= 3 at r340.
//   C5 root gathering episode (S58 + stack8) whose family ended by a labelled feed with >= half of the family drops to the line
//      (the design case that works).
// usage: node exp/endgame-king/cases.js [--per 2] > exp/endgame-king/cases.md
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'endgame-king');
const argv = process.argv.slice(2);
const per = +((argv.indexOf('--per') >= 0) ? argv[argv.indexOf('--per') + 1] : 2);
const hash32 = s => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; };
const SETS = ['cand-stack5-online', 'cand-stack6-online', 'cand-stack6-online-r2', 'cand-stack7-online', 'cand-stack8-online'];
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const games = [];
for (const s of SETS) { const f = path.join(CACHE, 'online-' + s + '.jsonl'); if (!fs.existsSync(f)) continue; for (const l of fs.readFileSync(f, 'utf8').split('\n')) if (l.trim()) games.push(JSON.parse(l)); }
const fateOf = q => q[42] ? 'line' : q[22] ? 'alive' : q[44] ? 'fed' : q[43] === 0 ? 'sac' : 'died';
const cls = { C1: [], C2: [], C3: [], C3b: [], C4: [], C5: [] };
for (const g of games) {
  if (!R500.includes(g.map)) continue;
  const u = g[g.us], o = g[g.us === 'A' ? 'B' : 'A'];
  for (const q of u.gath || []) {
    if (q[40]) continue;
    const f = fateOf(q);
    if (!q[32] && f === 'fed') cls.C1.push({ key: g.key, map: g.map, id: q[0], r0: q[1], L0: q[2], end: q[16], note: `r0 ${q[1]} L0 ${q[2]} dKing0 ${q[6]} fam drops ${q[46]} → line ${q[34]}` });
    if (q[2] >= 8 && f === 'died') cls.C2.push({ key: g.key, map: g.map, id: q[0], r0: q[1], L0: q[2], end: q[16], note: `r0 ${q[1]} L0 ${q[2]} last cause ${q[43]} at r${q[16]}` });
    if (f === 'fed' && q[46] > 0 && q[34] * 2 >= q[46]) cls.C5.push({ key: g.key, map: g.map, id: q[0], r0: q[1], L0: q[2], end: q[16], note: `r0 ${q[1]} L0 ${q[2]} fam drops ${q[46]} → line ${q[34]}` });
  }
  if (g.rounds === 500 && u.kid >= 0 && g.map !== 'Portals') { const e = u.env[0][1] + u.env[1][1]; if (e > 0) cls.C3b.push({ key: g.key, map: g.map, id: u.kid, r0: 300, score: e, note: `line turns with enemy ≤3 in r300-399: ${e} of ${u.env[0][0] + u.env[1][0]}; final ${u.king}` }); }
  if (g.rounds === 500 && u.kid >= 0) { const e = u.env[0][1] + u.env[1][1]; if (e > 0) cls.C3.push({ key: g.key, map: g.map, id: u.kid, r0: 300, score: e, note: `line turns with enemy ≤3 in r300-399: ${e} of ${u.env[0][0] + u.env[1][0]}; final ${u.king}` }); }
  if (g.rounds === 500 && o.kid >= 0) for (const c of o.coh) if (c[3] === 0 && c[16] >= 3) cls.C4.push({ key: g.key, map: g.map, id: c[0], r0: 340, L0: c[1], note: `opp ${g.opp}: r340 L${c[1]} rank ${c[16]} dK ${c[2]}; final ${o.king}` });
}
const lines = ['# endgame-king: stage 2 classes and stage 3 picks (500-round maps; our S58 + stack8 sets present: ' + SETS.filter(s => fs.existsSync(path.join(CACHE, 'online-' + s + '.jsonl'))).join(', ') + ')', ''];
for (const [k, a] of Object.entries(cls)) {
  lines.push(`## ${k}: ${a.length} cases` + (k === 'C3' ? ' (games)' : ''));
  const byMap = {}; for (const c of a) byMap[c.map] = (byMap[c.map] || 0) + 1;
  lines.push('by map: ' + JSON.stringify(byMap));
  let pick;
  if (k === 'C3' || k === 'C3b') pick = a.slice().sort((x, y) => y.score - x.score || hash32(x.key) - hash32(y.key));
  else pick = a.slice().sort((x, y) => hash32(x.key + '#' + x.id) - hash32(y.key + '#' + y.id));
  const used = new Set(), out = [];
  for (const c of pick) { if (used.has(c.key)) continue; used.add(c.key); out.push(c); if (out.length >= per) break; }
  for (const c of out) lines.push(`- ${c.key} ${c.map} #${c.id}: ${c.note}`);
  lines.push('');
}
console.log(lines.join('\n'));
