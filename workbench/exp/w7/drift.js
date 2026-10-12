#!/usr/bin/env node
// W7d grounding (VERSION.md §13: our pieces are isolated before they are cornered): per move of a measured team's dragon, the Manhattan
// distance to the nearest ally head before and after the move (allies as they stand), and the head balance within 8 (allies + 1 - enemies)
// at the new head. "Drift" = the move takes a piece that is already >= 3 from every ally head further away; "drift into a minority" = a drift
// that ends where the balance within 8 is negative. Also the distribution of the nearest-ally distance over all moves.
// usage: node exp/w7/drift.js --population [--src online,top] [--limit N]   |   --sets exp/w7/s17-base[,..] [--label l]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const stats = new Map();
const S = l => { if (!stats.has(l)) stats.set(l, { games: 0, moves: 0, alone: 0, far: 0, drift: 0, driftMinor: 0, dist: [0, 0, 0, 0, 0, 0] }); return stats.get(l); };
const BIN = d => d <= 1 ? 0 : d <= 3 ? 1 : d <= 5 ? 2 : d <= 8 ? 3 : d <= 15 ? 4 : 5;   // 1, 2-3, 4-5, 6-8, 9-15, 16+ / no ally
function measure(file, teams, map) {
  const R = load(file);
  perGame(R, { map, variant: 'a' }, {
    action(d, e, round, ctx, hb) {
      const labs = teams[d.team]; if (!labs) return;
      const a = e.action; if (!a || a.kind !== 'move' || d.fate) return;
      const { drag, W, H } = ctx;
      const man = (p, q) => { const dx = Math.abs(p.x - q.x), dy = Math.abs(p.y - q.y); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
      const h0 = hb[0], h1 = d.body[0];
      let dA0 = 99, dA1 = 99, a8 = 0, e8 = 0;
      for (const o of drag.values()) {
        if (o.id === d.id || !o.body.length) continue;
        const q = o.body[0];
        if (o.team === d.team) { dA0 = Math.min(dA0, man(q, h0)); dA1 = Math.min(dA1, man(q, h1)); if (man(q, h1) <= 8) a8++; }
        else if (man(q, h1) <= 8) e8++;
      }
      const bal = a8 + 1 - e8;
      for (const l of labs) {
        const T = S(l); T.moves++;
        if (dA0 >= 99) { T.alone++; T.dist[5]++; continue; }
        T.dist[BIN(dA0)]++;
        if (dA0 >= 3) { T.far++; if (dA1 > dA0) { T.drift++; if (bal < 0) T.driftMinor++; } }
      }
    },
  });
}
if (opt('--sets')) {
  const label = opt('--label');
  for (const set of opt('--sets').split(',')) {
    const rows = fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => r.G !== undefined && !r.error);
    const l = label || path.basename(set);
    for (const r of rows) { S(l).games++; measure(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'), { [r.side]: [l] }, r.map); }
  }
} else {
  const P = JSON.parse(fs.readFileSync(path.join(ROOT, 'exp', 'small', 'population.json'), 'utf8'));
  const srcs = new Set(opt('--src', 'online,top').split(',')), limit = +opt('--limit', 1e9); let n = 0;
  for (const t of P.tasks) {
    if (!srcs.has(t.src) || (t.map || t.mapName) !== 'Trophy' || n >= limit) continue; n++;
    const teams = {};
    if (t.src === 'online' || t.src === 'local') teams[t.us] = [`${t.src} Trophy (ours)`];
    else { const w = (t.winner || '').toUpperCase(); teams[w] = [`${t.src} winner Trophy`]; teams[w === 'A' ? 'B' : 'A'] = [`${t.src} loser Trophy`]; }
    for (const ls of Object.values(teams)) for (const l of ls) S(l).games++;
    try { measure(t.file, teams, 'Trophy'); } catch (e) { console.error('skip', t.key, String(e).slice(0, 100)); }
    if (n % 200 === 0) console.error('progress', n);
  }
}
const pc = (a, b) => b ? (100 * a / b).toFixed(1) + '%' : '-';
for (const [l, T] of [...stats].sort()) console.log(`${l.padEnd(26)} games ${T.games} moves ${T.moves}: nearest ally head 1 / 2-3 / 4-5 / 6-8 / 9-15 / 16+ or none: ${T.dist.map(x => pc(x, T.moves)).join(' / ')} | of moves >= 3 from every ally (${pc(T.far, T.moves)}): **drift further ${pc(T.drift, T.far)}**, drift into a minority window ${pc(T.driftMinor, T.far)}`);
