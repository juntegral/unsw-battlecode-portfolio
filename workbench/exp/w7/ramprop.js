#!/usr/bin/env node
// W7a premise check (coordinator 16:5x): our threat model discounts a tile within a LONGER enemy's reach (x0.45 adjacent, x0.2 at sprint range,
// "bad for them": they would lose more mass). Do players actually decline such rams? For every move of a measured team's dragon D and every enemy
// head E that D could hit this turn (a path of at most L_D - 1 steps over free tiles ending on E's head), whether D's move rammed E (a head-on
// with E). Split by the length gap (D longer than E / equal / shorter) and by the local head balance in D's 7x7 window (D's team, D included,
// minus E's team: <= -1, 0, >= +1).
// Cohorts: the small-map study's Trophy population (top winners and losers, our online games) and, with --sets, both teams of our local sets
// (the opponent is a proxy: label "proxy").
// usage: node exp/w7/ramprop.js --population [--src online,top] [--limit N]   |   --sets exp/w7/s-base [--label v17]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const DIRS = ['N', 'E', 'S', 'W'];
const stats = new Map();
const key3 = (gap, bal) => `${gap}|${bal}`;
const S = l => { if (!stats.has(l)) stats.set(l, { games: 0, opp: {}, ram: {} }); return stats.get(l); };
function measure(file, teams, map) {
  const R = load(file);
  perGame(R, { map, variant: 'a' }, {
    action(d, e, round, ctx, hb) {
      const lab = teams[d.team]; if (!lab) return;
      const a = e.action; if (!a || a.kind !== 'move') return;
      const { occ, key, across, drag, W, H } = ctx;
      const L = hb.length, h = hb[0], r = Math.max(1, Math.min(L - 1, 6));
      // enemy heads now (the board before this move: d's own tiles from hb)
      const enemyHeads = new Map();
      for (const o of drag.values()) if (o.team !== d.team && o.body.length) enemyHeads.set(key(o.body[0].x, o.body[0].y), o);
      if (!enemyHeads.size) return;
      const ownBefore = new Set(hb.map(s => key(s.x, s.y)));
      const blocked = k => (occ.has(k) && occ.get(k) !== d.id) || ownBefore.has(k);
      const seen = new Map([[key(h.x, h.y), 0]]), q = [h], reachable = [];
      for (let i = 0; i < q.length; i++) {
        const c = q[i], dc = seen.get(key(c.x, c.y)); if (dc >= r) continue;
        for (const dir of DIRS) {
          const u = across(c.x, c.y, dir); if (!u) continue;
          if (L >= 2 && dc === 0 && u.x === hb[1].x && u.y === hb[1].y) continue;
          const k = key(u.x, u.y); if (seen.has(k)) continue; seen.set(k, dc + 1);
          if (enemyHeads.has(k)) { reachable.push(enemyHeads.get(k)); continue; }
          if (!blocked(k)) q.push(u);
        }
      }
      if (!reachable.length) return;
      let mine = 0, theirs = 0;
      for (const o of drag.values()) { if (!o.body.length) continue; const q2 = o.body[0], dx = Math.abs(q2.x - h.x), dy = Math.abs(q2.y - h.y); if (Math.max(Math.min(dx, W - dx), Math.min(dy, H - dy)) > 3) continue; if (o.team === d.team) mine++; else theirs++; }
      if (ownBefore.size && !mine) mine = 1;
      const bal = mine - theirs <= -1 ? 'outnumbered' : mine - theirs === 0 ? 'even' : 'ahead';
      const hitId = d.fate && d.fate.reason === 'H' && d.fate.hitTeam !== d.team ? d.fate.hit : null;
      for (const o of reachable) {
        const gap = L > o.body.length ? 'longer' : L === o.body.length ? 'equal' : 'shorter';
        const k = key3(gap, bal);
        for (const l of lab) { const T = S(l); T.opp[k] = (T.opp[k] || 0) + 1; if (hitId === o.id) T.ram[k] = (T.ram[k] || 0) + 1; }
      }
    },
  });
}
if (opt('--sets')) {
  const label = opt('--label', 'ours');
  for (const set of opt('--sets').split(',')) {
    const rows = fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => r.G !== undefined && !r.error);
    for (const r of rows) { S(label).games++; S('proxy').games++; measure(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'), { [r.side]: [label], [r.side === 'A' ? 'B' : 'A']: ['proxy'] }, r.map); }
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
for (const [l, T] of [...stats].sort()) {
  const cell = (g, b) => { const k = key3(g, b); return `${pc(T.ram[k] || 0, T.opp[k] || 0)} of ${T.opp[k] || 0}`; };
  const tot = g => { let o = 0, r = 0; for (const b of ['outnumbered', 'even', 'ahead']) { o += T.opp[key3(g, b)] || 0; r += T.ram[key3(g, b)] || 0; } return `${pc(r, o)} of ${o}`; };
  console.log(`== ${l} (${T.games} games): rams when an enemy head is within reach, by the rammer's length vs the target's`);
  for (const g of ['longer', 'equal', 'shorter']) console.log(`   rammer ${g.padEnd(7)}: all ${tot(g)} | outnumbered ${cell(g, 'outnumbered')} | even ${cell(g, 'even')} | ahead ${cell(g, 'ahead')}`);
}
