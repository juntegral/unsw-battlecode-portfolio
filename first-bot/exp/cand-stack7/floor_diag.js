#!/usr/bin/env node
// stack7 local diagnostic (research/experiments/cand-stack7.md, "로컬 확인"): in the low-unit episode window of each floor-map game
// (the elimination study's definition, exp/eliminations/top.js I), what did our dragons of length >= 4 do on each turn, and what
// could have kept floor from splitting them? Replays only.
// usage: node exp/cand-stack7/floor_diag.js <eval folder> [...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const MAPNAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma',
  queen_of_spades: 'Queen Of Spades', schooltime: 'Schooltime', slithery_fight: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const ON = new Set(['Trophy', 'Queen Of Spades', 'Devil', 'Default', 'Schooltime', 'Trauma', 'Slithery Fight']);
const load = makeLoader(viewerSource());
const tally = {}, add = (k, n = 1) => { tally[k] = (tally[k] || 0) + n; };
let games = 0, eps = 0;
for (const dir of process.argv.slice(2)) {
  for (const l of fs.readFileSync(path.join(ROOT, dir, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean)) {
    const row = JSON.parse(l), [opp, map, side, seed] = row.key.split(':'), name = MAPNAME[map.replace(/_(b|10)$/, '')];
    if (!ON.has(name)) continue;
    const f = path.join(ROOT, dir, 'games', `${opp}_${map}_${side}_${seed}`, 'game.replay'); if (!fs.existsSync(f)) continue;
    const R = load(f), us = side, u = [], eu = [], turns = [];
    let lastR = -1, lastDeath = -1, nEnd = 0;
    perGame(R, { map: name }, {
      turn(d, r, c) {
        if (r !== lastR) { lastR = r; let a = 0, b = 0; for (const o of c.drag.values()) { if (o.team === us) a++; else b++; } u[r] = a; eu[r] = b; }
        if (d.team !== us) return;
        let eM = 99; for (const o of c.drag.values()) if (o.team !== us) eM = Math.min(eM, c.tdist(o.body[0], d.body[0]));
        turns.push({ r, id: d.id, L: d.body.length, king: c.kingOf(us) === d ? 1 : 0, eM });
      },
      indicator(e) { const t = turns[turns.length - 1]; if (t && t.id === e.id) t.text = e.text || ''; },
      death(d, rec, idx, other, r) { if (d.team === us) lastDeath = r; },
      end(n, c) { for (const o of c.drag.values()) if (o.team === us) nEnd++; },
    });
    games++;
    const rounds = R.result.rounds || 500, elimR = nEnd === 0 ? lastDeath : -1, end = elimR >= 0 ? elimR : rounds;
    let r0 = -1;
    for (let r = 50; r + 20 < rounds && r < end; r += 5) { const a = u[r] === undefined ? nEnd : u[r], b = eu[r] === undefined ? 0 : eu[r]; if (a > 3 || a === 0 || b < 8) continue; r0 = r; break; }
    if (r0 < 0) continue;
    eps++;
    const W = turns.filter(t => t.r >= r0 && t.r < r0 + 20), late = r0 >= 340;
    add('window turns', W.length); add(late ? 'episodes from r340' : 'episodes before r340');
    for (const t of W) {
      const tx = t.text || '', split = /^(split|csplit|escape-split)/.test(tx);
      if (t.L < 4) { add('turns L<4 (cannot split)'); continue; }
      add('turns L>=4');
      if (split) { add('  L>=4: split (' + (tx.match(/ (floor|kcap|frag|bsp)(?:\s|$)/) || [, tx.split(/\d/)[0]])[1] + ')'); continue; }
      if (t.r >= 340 && t.king) { add('  L>=4 no split: r>=340 and the king (excluded by design)'); continue; }
      if (/^feed|^no-exit|^last-trade|^pocket/.test(tx)) { add('  L>=4 no split: ' + tx.split(/[ #\d]/)[0] + ' label'); continue; }
      if (/ TRADE/.test(tx)) { add('  L>=4 no split: trade move'); continue; }
      if ((u[t.r] || 0) > 3) { add('  L>=4 no split: our units > 3 at the round start (floor off by design)'); continue; }
      if (t.r >= 340 && !t.king) { add('  L>=4 no split: r>=340, not the ledger king (floor needs a longer ally known)'); continue; }
      if (t.eM <= 2) { add('  L>=4 no split: enemy head within Manhattan 2 (split gate)'); continue; }
      const v = +((/ v(-?[\d.]+)/.exec(tx) || [])[1]);
      if (v < 0) { add('  L>=4 no split: move value < 0 (threat priced)'); continue; }
      add('  L>=4 no split: other before r340 (pearl first step, threatened tiles, child spot, recognition)' + (t.king ? ' [king]' : ' [not king]'));
    }
  }
}
console.log(`floor-map games ${games}, with a low-unit episode ${eps}`);
for (const [k, v] of Object.entries(tally).sort()) console.log(`${k}: ${v}`);
