#!/usr/bin/env node
// Independent recount of the split-speed claims (research/observations/intake-gap.md sections 3 and 13): no ledger, no step
// simulation, no extract.js. Bodies from dragonUpdate head/tail + dragonSplit bodies; the parent's split label from the turn's
// dragonIndicator; natural pearls from the event order (spawned after roundStart before the round's first turnStart).
// Per team and phase (r0-49, r50-99, r100-249): births (our side split by label: escape-split / esc-split vs the rest), natural
// eats, head-rounds with length >= 4 (heads at each round's first turn). Open 500-round maps and open elimination maps.
// usage: node exp/intake-gap/recount_split.js [sets...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const RL = require('./rawload.js');
const sets = process.argv.slice(2).length ? process.argv.slice(2) : ['cand-stack5-online', 'cand-stack6-online', 'cand-stack6-online-r2', 'cand-stack7-online', 'cand-stack8-online'];
const FAM = { open500: new Set(['Portals', 'Schooltime', 'Slithery Fight', 'Trauma']), openElim: new Set(['Default', 'Devil', 'Queen Of Spades', 'Trophy']) };
const acc = {}; for (const f of Object.keys(FAM)) acc[f] = { n: 0, bu: [0, 0, 0], bune: [0, 0, 0], bo: [0, 0, 0], eu: [0, 0, 0], eo: [0, 0, 0], h4u: [0, 0, 0], h4o: [0, 0, 0] };
const ph = r => r < 50 ? 0 : r < 100 ? 1 : r < 250 ? 2 : -1;
for (const set of sets) {
  const dir = path.join(ROOT, 'data', 'online', set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  for (const gm of idx.games || idx) {
    const fam = Object.keys(FAM).find(f => FAM[f].has(gm.mapName)); if (!fam) continue;
    const file = path.join(dir, 'M' + gm.gameId + '.replay'); if (!fs.existsSync(file)) continue;
    const R = RL.load(file), M = R.match.map, W = M.width, us = String(gm.ourSide).toUpperCase() === 'A' ? 0 : 1;
    const A = acc[fam]; A.n++;
    const dr = new Map(); for (const d0 of M.initialDragons) dr.set(d0.id, { team: d0.team === 'A' ? 0 : 1, body: d0.body.map(s => [s.x, s.y]) });
    const nat = new Set(); if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) nat.add(i);
    let round = -1, inTurn = false, first = false, cur = -1, curTeam = -1; const label = new Map();
    for (const e of R.events) {
      switch (e.type) {
        case 'roundStart': round = e.round; inTurn = false; first = false; break;
        case 'turnStart': {
          if (!first) { first = true; const p = ph(round); if (p >= 0) for (const d of dr.values()) if (d.body.length >= 4) { if (d.team === us) A.h4u[p]++; else A.h4o[p]++; } }
          inTurn = true; cur = e.id; const d = dr.get(e.id); curTeam = d ? d.team : -1; label.set(e.id, null); break;
        }
        case 'dragonIndicator': label.set(e.id, e.text); break;
        case 'tileChange': {
          const k = e.tile.y * W + e.tile.x;
          if (e.hasPearl) { if (!inTurn && round >= 0) nat.add(k); else nat.delete(k); }
          else if (nat.has(k)) { nat.delete(k); const p = ph(round); if (p >= 0 && curTeam >= 0) { if (curTeam === us) A.eu[p]++; else A.eo[p]++; } }
          break;
        }
        case 'dragonUpdate': { const d = dr.get(e.id); if (!d) break; const b = d.body; if (b[0][0] !== e.head.x || b[0][1] !== e.head.y) b.unshift([e.head.x, e.head.y]); while (b.length > 1 && (b[b.length - 1][0] !== e.tail.x || b[b.length - 1][1] !== e.tail.y)) b.pop(); break; }
        case 'dragonSplit': {
          const p0 = dr.get(e.parentId); if (p0) p0.body = e.parentBody.map(s => [s.x, s.y]);
          const t = e.team === 'A' ? 0 : 1; dr.set(e.childId, { team: t, body: e.childBody.map(s => [s.x, s.y]) });
          const p = ph(round); if (p < 0) break;
          if (t === us) { A.bu[p]++; const lab = label.get(e.parentId) || ''; if (!/^(escape-split|esc-split)/.test(lab)) A.bune[p]++; } else A.bo[p]++;
          break;
        }
        case 'dragonDeath': dr.delete(e.id); break;
      }
    }
  }
}
const r = (a, b) => b ? (a / b).toFixed(3) : '–';
for (const [f, A] of Object.entries(acc)) {
  console.log(`${f}: ${A.n} games`);
  ['r0-49', 'r50-99', 'r100-249'].forEach((nm, i) => console.log(`  ${nm}: births/natural pearl us non-escape ${r(A.bune[i], A.eu[i])} (all ${r(A.bu[i], A.eu[i])}), opp ${r(A.bo[i], A.eo[i])} | births per L>=4 head-round us non-escape ${r(A.bune[i], A.h4u[i])}, opp ${r(A.bo[i], A.h4o[i])} | per game: births us ${(A.bu[i] / A.n).toFixed(1)} (non-esc ${(A.bune[i] / A.n).toFixed(1)}) opp ${(A.bo[i] / A.n).toFixed(1)}, natural us ${(A.eu[i] / A.n).toFixed(1)} opp ${(A.eo[i] / A.n).toFixed(1)}`));
}
