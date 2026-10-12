#!/usr/bin/env node
// W7c grounding (coordinator 17:01): how often a move boxes in an ally. A move of dragon X "boxes" an ally head h when X's head ends on a tile
// that was one of h's free exits (h adjacent to it) and, after X's move, h has <= 1 free exit left; "seals" when h is left with none. A free exit
// is a neighbour across an open edge or portal (kelp blocks), not a tile of any dragon (heads included: stepping there is a trade or a death),
// and not h's neck. Checked on the board right after X's move (other dragons as they stand then). Outcome check: h dies within its next two
// turns (any cause; trap separately). Crowded = >= 5 heads of either team in X's 7x7 window before the move.
// Cohorts as reach.js: --sets <ourSetDirs> [--label l]  |  --population [--src online,top,elite] [--limit N] (Trophy only).
// usage: node exp/w7/boxing.js --sets exp/w7/s-base,exp/w7/s-b --label v17   |   node exp/w7/boxing.js --population --src online,top
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const DIRS = ['N', 'E', 'S', 'W'];
const stats = new Map();
const S = l => { if (!stats.has(l)) stats.set(l, { games: 0, moves: 0, nearAlly: 0, box: 0, seal: 0, crowdMoves: 0, crowdBox: 0, crowdSeal: 0, boxedDied: 0, boxedTrap: 0, boxedN: 0, ctrlDied: 0, ctrlTrap: 0, ctrlN: 0, allyTraps: 0, deaths: 0 }); return stats.get(l); };
function measure(file, teams, map) {
  const R = load(file);
  const watch = new Map();   // ally id -> {labels, until: its turns left, boxed}
  perGame(R, { map, variant: 'a' }, {
    turn(d) {
      const w = watch.get(d.id); if (!w) return;
      w.turnsLeft--; if (w.turnsLeft < 0) watch.delete(d.id);
    },
    death(d, rec) {
      const labs = teams[d.team]; if (labs) for (const l of labs) { const T = S(l); T.deaths++; if (CAUSE[rec.cause] === 'trap' && rec.blk === 'a') T.allyTraps++; }
      const w = watch.get(d.id); if (!w) return;
      for (const l of w.labels) { const T = S(l); if (w.boxed) { T.boxedDied++; if (CAUSE[rec.cause] === 'trap') T.boxedTrap++; } else { T.ctrlDied++; if (CAUSE[rec.cause] === 'trap') T.ctrlTrap++; } }
      watch.delete(d.id);
    },
    action(d, e, round, ctx, hb) {
      const labs = teams[d.team]; if (!labs) return;
      const a = e.action; if (!a || a.kind !== 'move' || d.fate) return;
      const { occ, key, across, drag, W, H } = ctx;
      const t = d.body[0], kt = key(t.x, t.y), h0 = hb[0];
      let heads = 0;
      for (const o of drag.values()) { if (!o.body.length) continue; const q = o.body[0], dx = Math.abs(q.x - h0.x), dy = Math.abs(q.y - h0.y); if (Math.max(Math.min(dx, W - dx), Math.min(dy, H - dy)) <= 3) heads++; }
      const crowded = heads >= 5;
      // ally heads adjacent to our new head tile
      let near = false, boxed = false, sealed = false; const victims = [];
      for (const dir of DIRS) {
        const u = across(t.x, t.y, dir); if (!u) continue;
        const ku = key(u.x, u.y); if (!occ.has(ku)) continue;
        const o = drag.get(occ.get(ku)); if (!o || o.id === d.id || o.team !== d.team) continue;
        if (o.body[0].x !== u.x || o.body[0].y !== u.y) continue;   // an ally head
        near = true;
        // its free exits now (after our move), and whether our tile was one of them before (it was free before we moved in)
        let free = 0;
        for (const d2 of DIRS) {
          const v = across(u.x, u.y, d2); if (!v) continue;
          const kv = key(v.x, v.y);
          if (o.body.length >= 2 && v.x === o.body[1].x && v.y === o.body[1].y) continue;
          if (occ.has(kv)) continue;
          free++;
        }
        const tookExit = !hb.some(s => key(s.x, s.y) === kt);   // our new head tile was not ours before: it was free (we could step there)
        if (tookExit && free <= 1) { boxed = true; victims.push(o.id); if (free === 0) sealed = true; }
        else victims.push(-o.id - 1);   // adjacent, not boxed: control
      }
      for (const l of labs) {
        const T = S(l); T.moves++; if (crowded) T.crowdMoves++;
        if (near) T.nearAlly++;
        if (boxed) { T.box++; if (crowded) T.crowdBox++; }
        if (sealed) { T.seal++; if (crowded) T.crowdSeal++; }
      }
      for (const v of victims) {
        const id = v >= 0 ? v : -v - 1, isBoxed = v >= 0;
        if (watch.has(id)) continue;
        watch.set(id, { labels: labs, turnsLeft: 2, boxed: isBoxed });
        for (const l of labs) { const T = S(l); if (isBoxed) T.boxedN++; else T.ctrlN++; }
      }
    },
  });
}
if (opt('--sets')) {
  const label = opt('--label', 'ours');
  for (const set of opt('--sets').split(',')) {
    const rows = fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => r.G !== undefined && !r.error);
    for (const r of rows) {
      const ls = [`${path.basename(set)} ${r.map}`, `${path.basename(set)} ALL`]; for (const l of ls) S(l).games++;
      measure(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'), { [r.side]: ls }, r.map);
    }
  }
} else {
  const P = JSON.parse(fs.readFileSync(path.join(ROOT, 'exp', 'small', 'population.json'), 'utf8'));
  const srcs = new Set(opt('--src', 'online,top').split(',')), limit = +opt('--limit', 1e9); let n = 0;
  for (const t of P.tasks) {
    if (!srcs.has(t.src) || (t.map || t.mapName) !== 'Trophy' || n >= limit) continue; n++;
    const teams = {};
    if (t.src === 'online' || t.src === 'local') teams[t.us] = [`${t.src} Trophy`];
    else { const w = (t.winner || '').toUpperCase(); teams[w] = [`${t.src} winner Trophy`]; teams[w === 'A' ? 'B' : 'A'] = [`${t.src} loser Trophy`]; }
    for (const ls of Object.values(teams)) for (const l of ls) S(l).games++;
    try { measure(t.file, teams, 'Trophy'); } catch (e) { console.error('skip', t.key, String(e).slice(0, 100)); }
    if (n % 200 === 0) console.error('progress', n);
  }
}
const pc = (a, b) => b ? (100 * a / b).toFixed(2) + '%' : '-';
for (const [l, T] of [...stats].sort()) console.log(`${l.padEnd(26)} games ${T.games} moves ${T.moves}: ends beside an ally head ${pc(T.nearAlly, T.moves)} | **boxes an ally (it keeps <= 1 exit) ${pc(T.box, T.moves)}**, seals one (0 exits) ${pc(T.seal, T.moves)} | crowded windows (${pc(T.crowdMoves, T.moves)} of moves): box ${pc(T.crowdBox, T.crowdMoves)}, seal ${pc(T.crowdSeal, T.crowdMoves)} | boxed ally dies within 2 of its turns ${pc(T.boxedDied, T.boxedN)} (trap ${pc(T.boxedTrap, T.boxedN)}) vs adjacent not boxed ${pc(T.ctrlDied, T.ctrlN)} (trap ${pc(T.ctrlTrap, T.ctrlN)}) | trap deaths beside our own pieces ${T.allyTraps} of ${T.deaths} deaths`);
