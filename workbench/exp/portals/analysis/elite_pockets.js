#!/usr/bin/env node
// exp/portals v2: elite teams' use of the Portals pockets and U-rooms (top-vs-top replays, both teams). Per team-game: pocket and U-room
// visits (head steps onto a tile of the class from outside it), natural pearls eaten there, deaths there; split by king500 band.
// usage: node elite_pockets.js [--n 120]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const PTM = JSON.parse(fs.readFileSync(path.join(__dirname, '../gen/ptmap.json'), 'utf8'));
const cls = t => PTM.compSize[t] === 1 ? 'pocket' : !PTM.core[t] ? 'corridor' : PTM.room[t] ? 'Uroom' : 'open';
const nMax = +(process.argv[process.argv.indexOf('--n') + 1] || 120);
const idx = fs.readFileSync(path.join(ROOT, 'data/top/index.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.map === 'Portals');
const out = [];
for (const r of idx) {
  if (out.length >= 2 * nMax) break;
  const f = path.join(ROOT, 'data/top', String(r.battleId), r.gameId + '.replay.gz'); if (!fs.existsSync(f)) continue;
  let R; try { R = load(f); } catch { continue; }
  const T = { A: { vis: {}, eat: {}, die: {}, dieL: {} }, B: { vis: {}, eat: {}, die: {}, dieL: {} } }, prev = new Map();
  const add = (o, k, v = 1) => { o[k] = (o[k] || 0) + v; };
  const g = perGame(R, { map: 'Portals' }, {
    action(d, e, round) { const h = d.body[0], c = cls(h.y * 32 + h.x), p = prev.get(d.id); if (c !== 'open' && p !== c) add(T[d.team].vis, c); prev.set(d.id, c); },
    eat(d, tile, o) { if (o === -1) add(T[d.team].eat, cls(tile)); },
    death(d, rec) { const h = d.body[0], c = cls(h.y * 32 + h.x); add(T[d.team].die, c); add(T[d.team].dieL, c, rec.len); },
  });
  for (const tm of ['A', 'B']) out.push({ key: r.battleId + ':' + r.gameId, team: tm, name: tm === 'A' ? r.teamA : r.teamB, k500: g[tm].st.king[50], ...T[tm] });
}
const q = (xs, p) => { const a = [...xs].sort((u, v) => u - v); const i = (a.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return a[lo] + (a[hi] - a[lo]) * (i - lo); };
const bands = { 'k500 >= 51': out.filter(r => r.k500 >= 51), 'k500 31-50': out.filter(r => r.k500 >= 31 && r.k500 <= 50), 'k500 <= 30': out.filter(r => r.k500 <= 30), all: out };
for (const [b, rs] of Object.entries(bands)) {
  const m = (f, k) => (rs.reduce((s, r) => s + (r[f][k] || 0), 0) / Math.max(1, rs.length)).toFixed(1);
  console.log(`${b.padEnd(11)} N ${String(rs.length).padStart(3)} | pocket visits ${m('vis', 'pocket')} nat ${m('eat', 'pocket')} deaths ${m('die', 'pocket')} (len ${m('dieL', 'pocket')}) | U-room visits ${m('vis', 'Uroom')} nat ${m('eat', 'Uroom')} deaths ${m('die', 'Uroom')} | corridor visits ${m('vis', 'corridor')} nat ${m('eat', 'corridor')} deaths ${m('die', 'corridor')}`);
}
