#!/usr/bin/env node
// cand-stack12: independent recount of key local numbers from the raw events (tools/replay.js; no mass ledger, no intake-gap extractor):
// pf splits (the parent's indicator that turn starts with "pf"), the pf child alive (id) 30 rounds later or at the end, our units at the
// first turn of r10 / r50 / r100 (living dragons of our side), and non-escape births per length >= 4 head-round in r0-99.
// usage: node exp/cand-stack12/recount.js <local label> [...]
'use strict';
const fs = require('fs'), path = require('path'), { load } = require(path.resolve(__dirname, '..', '..', 'tools', 'replay.js'));
const R500 = new Set(['slithery_fight', 'slithery_fight_b', 'schooltime', 'schooltime_b', 'trauma']);
for (const lab of process.argv.slice(2)) {
  const acc = { games: 0, g500: 0, pf: 0, pfAlive30: 0, u: { 10: 0, 50: 0, 100: 0 }, sf10: 0, sfN: 0, births: 0, hr4: 0 };
  for (const l of fs.readFileSync(path.resolve(__dirname, '..', lab, 'rows.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue; const row = JSON.parse(l); const [opp, map, side, seed] = row.key.split(':');
    const R = load(path.resolve(__dirname, '..', lab, 'games', `${opp}_${map}_${side}_${seed}`, 'game.replay'));
    acc.games++; const is500 = R500.has(map); if (is500) acc.g500++; if (map.startsWith('slithery')) acc.sfN++;
    const team = new Map(), len = new Map(), label = new Map(), born = new Map(), died = new Map();
    for (const d of R.match.map.initialDragons) { team.set(d.id, d.team); len.set(d.id, d.body.length); }
    let round = -1, first = false, lastRound = 0; const pfKids = [];
    for (const e of R.events) {
      if (e.type === 'roundStart') { round = e.round; lastRound = round; first = false; }
      else if (e.type === 'turnStart' && !first) {
        first = true; let u = 0; for (const [id, t] of team) if (t === side && !died.has(id)) { u++; if (round < 100 && len.get(id) >= 4) acc.hr4++; }
        if (is500 && (round === 10 || round === 50 || round === 100)) acc.u[round] += u;
        if (map.startsWith('slithery') && round === 10) acc.sf10 += u;
      }
      else if (e.type === 'dragonIndicator') label.set(e.id, e.text || '');
      else if (e.type === 'dragonUpdate') { /* length from split/death bookkeeping below */ }
      else if (e.type === 'dragonSplit') {
        team.set(e.childId, e.team); len.set(e.childId, e.childBody.length); len.set(e.parentId, e.parentBody.length); born.set(e.childId, round);
        if (e.team === side) { const lb = label.get(e.parentId) || ''; if (round < 100 && !/^(escape-split|esc-split)/.test(lb)) acc.births++; if (/^pf\d/.test(lb)) { acc.pf++; pfKids.push([e.childId, round]); } }
      }
      else if (e.type === 'dragonDeath') died.set(e.id, round);
      else if (e.type === 'tileChange' && false) {}
    }
    for (const [id, r] of pfKids) { const d = died.has(id) ? died.get(id) : Infinity; if (d > r + 30) acc.pfAlive30++; }
  }
  const n5 = Math.max(1, acc.g500);
  console.log(`${lab}: ${acc.games} games; pf ${acc.pf}, pf child (id) alive 30 ${acc.pf ? Math.round(100 * acc.pfAlive30 / acc.pf) + '%' : '–'}; pf 500 units r10/r50/r100 ${(acc.u[10] / n5).toFixed(1)} / ${(acc.u[50] / n5).toFixed(1)} / ${(acc.u[100] / n5).toFixed(1)} (${acc.g500} games); SF r10 ${(acc.sf10 / Math.max(1, acc.sfN)).toFixed(1)}; non-escape births r0-99 ${acc.births} on ${acc.hr4} L>=4 head-rounds (lengths at splits only) `);
}
