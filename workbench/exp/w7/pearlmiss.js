#!/usr/bin/env node
// W7 next-mechanism groundwork (versions/v1.7/VERSION.md §6.3: on small boards our mass stays flat while natural pearls lie on the board): for
// every move of the measured team, whether a pearl lay on a legal one-step tile (natural or a death drop, as the mass ledger tracks them), whether
// that tile was safe (no enemy head can reach it before the mover's next turn, as exp/w7/reach.js), and whether the move ate a pearl.
//   missed safe pearl = a safe one-step pearl existed and the move ate none.
// Cohorts as reach.js: our local sets (--sets) or the small-map study's population (--population [--src ...] [--limit N]).
// usage: node exp/w7/pearlmiss.js --sets exp/w7/s-base [--label base]  |  --population --src online,top [--limit 300]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const DIRS = ['N', 'E', 'S', 'W'];
const stats = new Map(); const S = l => { if (!stats.has(l)) stats.set(l, { games: 0, moves: 0, ate: 0, adjPearl: 0, adjSafePearl: 0, missedSafe: 0, missedUnsafeOnly: 0 }); return stats.get(l); };
function measure(file, teams, map) {
  const R = load(file);
  const pre = new Map();   // dragon id -> {adj, adjSafe} at its turn start (the pearls it saw: an eaten pearl is gone by the action hook)
  perGame(R, { map, variant: 'a' }, {
    turn(d0, round, ctx) {
      if (!teams[d0.team]) return;
      const hb = d0.body.slice(), d = d0;
      const { occ, key, across, drag, pearls, W, H } = ctx;
      const L = hb.length, head = hb[0];
      const own = new Set(); for (let i = 0; i < L - 1; i++) own.add(key(hb[i].x, hb[i].y));
      const blocked = k => (occ.has(k) && occ.get(k) !== d.id) || own.has(k);
      const reach = new Set();
      for (const o of drag.values()) {
        if (o.team === d.team || !o.body.length) continue;
        const r = Math.max(1, Math.min(o.body.length - 1, 6)), s0 = o.body[0];
        const dx = Math.abs(s0.x - head.x), dy = Math.abs(s0.y - head.y); if (Math.min(dx, W - dx) + Math.min(dy, H - dy) > r + 2) continue;
        const seen = new Map([[key(s0.x, s0.y), 0]]), q = [s0];
        for (let i = 0; i < q.length; i++) { const c = q[i], dc = seen.get(key(c.x, c.y)); if (dc >= r) continue;
          for (const dir of DIRS) { const u = across(c.x, c.y, dir); if (!u) continue; const k = key(u.x, u.y); if (seen.has(k)) continue; seen.set(k, dc + 1); reach.add(k); if (!blocked(k)) q.push(u); } }
      }
      let adj = false, adjSafe = false;
      for (const dir of DIRS) {
        const u = across(head.x, head.y, dir); if (!u) continue;
        const k = key(u.x, u.y); if (L >= 2 && u.x === hb[1].x && u.y === hb[1].y) continue;
        if (occ.has(k)) continue;
        if (!pearls.has(k)) continue;
        adj = true; if (!reach.has(k)) adjSafe = true;
      }
      pre.set(d.id, { adj, adjSafe });
    },
    action(d, e) {
      const lab = teams[d.team]; if (!lab) return;
      const a = e.action; if (!a || a.kind !== 'move') return;
      const p = pre.get(d.id) || { adj: false, adjSafe: false }; const { adj, adjSafe } = p;
      const ate = d.ateThisAct > 0;
      for (const l of lab) { const T = S(l); T.moves++; if (ate) T.ate++; if (adj) T.adjPearl++; if (adjSafe) T.adjSafePearl++; if (adjSafe && !ate) T.missedSafe++; if (adj && !adjSafe && !ate) T.missedUnsafeOnly++; }
    },
  });
}
if (opt('--sets')) {
  const label = opt('--label', 'ours');
  for (const set of opt('--sets').split(',')) {
    const rows = fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => r.G !== undefined && !r.error);
    for (const r of rows) { S(`${label} ${r.map}`).games++; S(`${label} ALL`).games++; measure(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'), { [r.side]: [`${label} ${r.map}`, `${label} ALL`] }, r.map); }
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
  }
}
const pc = (a, b) => b ? (100 * a / b).toFixed(1) + '%' : '-';
for (const [l, T] of [...stats].sort()) console.log(`${l.padEnd(26)} games ${T.games} moves ${T.moves}: ate ${pc(T.ate, T.moves)} | a pearl one step away ${pc(T.adjPearl, T.moves)}, a safe one ${pc(T.adjSafePearl, T.moves)} | **missed a safe adjacent pearl ${pc(T.missedSafe, T.adjSafePearl)} of those** (${T.missedSafe}); skipped only-unsafe pearls ${pc(T.missedUnsafeOnly, T.adjPearl - T.adjSafePearl)}`);
