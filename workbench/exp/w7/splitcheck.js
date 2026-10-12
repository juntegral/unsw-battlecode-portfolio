#!/usr/bin/env node
// W7b mechanism check (versions/v1.7/VERSION.md §5): per local set, our
//   fired: csplit labels with a target above 8 ("csplit<n> u<units> L<len> t<target>"), and csplit splits in all;
//   state: splits per turn at length >= 4 (the turn's start state), our units at r25 / r50 / r100 (round start), child +30-round survival
//          (the child alive 30 rounds after its birth; births later than the end - 30 left out), split by crowding at the split (>= 5 heads of
//          either team in the parent's 7x7 window);
//   side: natural and dropped pearls eaten per dragon-turn (the mass ledger's eat hook).
// usage: node exp/w7/splitcheck.js <setDir> [<setDir> ...] [--maps a,b]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), mi = args.indexOf('--maps'), MAPS = mi >= 0 ? new Set(args[mi + 1].split(',')) : null;
const sets = args.filter((a, i) => !a.startsWith('--') && (mi < 0 || i !== mi + 1));
for (const set of sets) {
  const rows = fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => r.G !== undefined && !r.error && (!MAPS || MAPS.has(r.map)));
  const A = { games: 0, csplit: 0, csplitBig: 0, turns: 0, l4: 0, splits: 0, u25: 0, u50: 0, u100: 0, eats: 0, kids: [0, 0], kidsCrowd: [0, 0], kidsOpen: [0, 0], elim: 0 };
  const perMap = {};
  for (const r of rows) {
    const us = r.side, R = load(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'));
    const M = perMap[r.map] = perMap[r.map] || { games: 0, l4: 0, splits: 0, csplitBig: 0, u50: 0, u100: 0, kids: [0, 0] };
    A.games++; M.games++; if (!r.alive) A.elim++;
    const births = [];   // {id, round, crowded}
    const deathRound = new Map(); let lastRound = 0, lastUnitsRound = -1;
    perGame(R, { map: r.map, variant: 'a' }, {
      turn(d, round, ctx) {
        lastRound = round;
        if (round !== lastUnitsRound && (round === 25 || round === 50 || round === 100)) {
          lastUnitsRound = round; let u = 0; for (const o of ctx.drag.values()) if (o.team === us) u++;
          A['u' + round] += u; if (round !== 25) M['u' + round] += u;
        }
        if (d.team !== us) return;
        A.turns++; if (d.body.length >= 4) { A.l4++; M.l4++; }
      },
      split(p, ch, e, round, ctx) {
        if (p.team !== us) return;
        A.splits++; M.splits++;
        const h = p.body[0]; let heads = 0;
        for (const o of ctx.drag.values()) { if (!o.body.length) continue; const q = o.body[0], dx = Math.abs(q.x - h.x), dy = Math.abs(q.y - h.y); if (Math.max(Math.min(dx, ctx.W - dx), Math.min(dy, ctx.H - dy)) <= 3) heads++; }
        births.push({ id: ch.id, round, crowded: heads >= 5 });
      },
      death(d, rec, idx, other, round) { if (d.team === us) deathRound.set(d.id, round); },
      eat(d) { if (d.team === us) A.eats++; },
      indicator(e, round, ctx) {
        const d = ctx.drag.get(e.id); if (!d || d.team !== us) return;
        const m = /^csplit\d+ u\d+ L\d+ t(\d+)/.exec(e.text || ''); if (!m) return;
        A.csplit++; if (+m[1] > 8) { A.csplitBig++; M.csplitBig++; }
      },
    });
    for (const b of births) {
      if (b.round + 30 > lastRound) continue;
      const alive = !deathRound.has(b.id) || deathRound.get(b.id) > b.round + 30;
      A.kids[0]++; if (alive) A.kids[1]++; M.kids[0]++; if (alive) M.kids[1]++;
      const K = b.crowded ? A.kidsCrowd : A.kidsOpen; K[0]++; if (alive) K[1]++;
    }
  }
  const pc = (a, b) => b ? (100 * a / b).toFixed(1) + '%' : '-';
  const g = A.games || 1;
  console.log(`== ${set}: ${A.games} games (eliminated ${A.elim}) | fired: csplit with target > 8 ${A.csplitBig} of ${A.csplit} csplits | splits ${A.splits} = ${pc(A.splits, A.l4)} of L>=4 turns (L>=4 ${pc(A.l4, A.turns)} of ${A.turns} turns) | units r25/50/100 ${(A.u25 / g).toFixed(1)} / ${(A.u50 / g).toFixed(1)} / ${(A.u100 / g).toFixed(1)} (finished games count 0) | child +30 survival ${pc(A.kids[1], A.kids[0])} of ${A.kids[0]}: crowded ${pc(A.kidsCrowd[1], A.kidsCrowd[0])} of ${A.kidsCrowd[0]}, open ${pc(A.kidsOpen[1], A.kidsOpen[0])} of ${A.kidsOpen[0]} | pearls eaten per dragon-turn ${(A.eats / Math.max(1, A.turns)).toFixed(3)}`);
  for (const [m, M] of Object.entries(perMap).sort()) console.log(`   ${m.padEnd(14)} games ${M.games}: splits ${pc(M.splits, M.l4)} of L>=4 turns, csplit t>8 ${M.csplitBig}, units r50/100 ${(M.u50 / M.games).toFixed(1)} / ${(M.u100 / M.games).toFixed(1)}, child +30 ${pc(M.kids[1], M.kids[0])} of ${M.kids[0]}`);
}
