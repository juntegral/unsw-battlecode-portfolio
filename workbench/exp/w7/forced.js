#!/usr/bin/env node
// W7 forced-exposure precursors (coordinator 16:5x, point 2): our online Trophy pieces end with no safe move 2.1% of their moves, elite winners
// 0.3%. What was different 3 turns earlier? At every turn start of a measured team's dragon: "forced" = it has a legal move but every legal
// one-step move (and, for L >= 3, two-step sprint) ends on a tile an enemy head can reach before its next turn (as exp/w7/reach.js). For each
// forced turn, the dragon's state 3 own turns earlier (the precursor); for comparison, the state 3 turns before a non-forced turn (control).
// State: distance to the nearest enemy head, enemy / ally heads within Manhattan 3 and 8 and the balance (allies + 1 - enemies) within 8,
// free exits (the ledger's), distance to the nearest ally head, a pearl within 2 (foraging), length.
// usage: node exp/w7/forced.js --population [--src online,top] [--limit N]   |   --sets exp/w7/s17-base [--label v17]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const DIRS = ['N', 'E', 'S', 'W'], OPP = { N: 'S', S: 'N', E: 'W', W: 'E' }, K = 3;
const FEATS = ['dE', 'e3', 'e8', 'a3', 'a8', 'bal8', 'free', 'dA', 'forage', 'len'];
const stats = new Map();
const S = l => { if (!stats.has(l)) stats.set(l, { games: 0, turns: 0, forced: 0, pre: { n: 0, sum: {}, hist: {} }, ctl: { n: 0, sum: {}, hist: {} } }); return stats.get(l); };
function add(B, f) { B.n++; for (const k of FEATS) { B.sum[k] = (B.sum[k] || 0) + f[k]; const hk = k + ':' + Math.min(f[k], k === 'dE' || k === 'dA' ? 9 : k === 'len' ? 6 : 8); B.hist[hk] = (B.hist[hk] || 0) + 1; } }
function measure(file, teams, map) {
  const R = load(file);
  const hist = new Map();   // dragon id -> its last K+1 states
  perGame(R, { map, variant: 'a' }, {
    turn(d, round, ctx) {
      const labs = teams[d.team]; if (!labs) return;
      const { occ, key, across, drag, pearls, W, H } = ctx;
      const body = d.body, L = body.length, h = body[0];
      const man = (p, q) => { const dx = Math.abs(p.x - q.x), dy = Math.abs(p.y - q.y); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
      // state
      let dE = 99, dA = 99, e3 = 0, e8 = 0, a3 = 0, a8 = 0;
      for (const o of drag.values()) {
        if (o.id === d.id || !o.body.length) continue;
        const m = man(o.body[0], h);
        if (o.team === d.team) { dA = Math.min(dA, m); if (m <= 3) a3++; if (m <= 8) a8++; }
        else { dE = Math.min(dE, m); if (m <= 3) e3++; if (m <= 8) e8++; }
      }
      let forage = 0;
      for (let dy = -2; dy <= 2 && !forage; dy++) for (let dx = -2; dx <= 2; dx++) { if (Math.abs(dx) + Math.abs(dy) > 2) continue; if (pearls.has(key((h.x + dx + W) % W, (h.y + dy + H) % H))) { forage = 1; break; } }
      const st = { dE: Math.min(dE, 99), e3, e8, a3, a8, bal8: a8 + 1 - e8, free: d.free, dA: Math.min(dA, 99), forage, len: L };
      // forced now? reach map of the enemies near us; our body without its tail as obstacles
      const own = new Set(); for (let i = 0; i < L - 1; i++) own.add(key(body[i].x, body[i].y));
      const blocked = k => (occ.has(k) && occ.get(k) !== d.id) || own.has(k);
      const reach = new Set();
      for (const o of drag.values()) {
        if (o.team === d.team || !o.body.length) continue;
        const r = Math.max(1, Math.min(o.body.length - 1, 6)); if (man(o.body[0], h) > r + 2) continue;
        const seen = new Map([[key(o.body[0].x, o.body[0].y), 0]]), q = [o.body[0]];
        for (let i = 0; i < q.length; i++) { const c = q[i], dc = seen.get(key(c.x, c.y)); if (dc >= r) continue;
          for (const dir of DIRS) { const u = across(c.x, c.y, dir); if (!u) continue; const k = key(u.x, u.y); if (seen.has(k)) continue; seen.set(k, dc + 1); reach.add(k); if (!blocked(k)) q.push(u); } }
      }
      const enemyHead = new Set(); for (const o of drag.values()) if (o.team !== d.team && o.body.length) enemyHead.add(key(o.body[0].x, o.body[0].y));
      const occBefore = k => occ.has(k) && (occ.get(k) !== d.id || body.some(s => key(s.x, s.y) === k));
      const neck = L >= 2 ? body[1] : null;
      let legal = 0, safe = 0;
      for (const d1 of DIRS) {
        const u1 = across(h.x, h.y, d1); if (!u1 || (neck && u1.x === neck.x && u1.y === neck.y)) continue;
        const k1 = key(u1.x, u1.y); if (occBefore(k1) || enemyHead.has(k1)) continue;
        legal++; if (!reach.has(k1)) safe++;
        if (L >= 3) for (const d2 of DIRS) { if (d2 === OPP[d1]) continue; const u2 = across(u1.x, u1.y, d2); if (!u2) continue; const k2 = key(u2.x, u2.y);
          if (occBefore(k2) || enemyHead.has(k2) || (u2.x === h.x && u2.y === h.y)) continue; legal++; if (!reach.has(k2)) safe++; }
      }
      const forcedNow = legal > 0 && safe === 0;
      const hs = hist.get(d.id) || []; hs.push(st); if (hs.length > K + 1) hs.shift(); hist.set(d.id, hs);
      for (const l of labs) {
        const T = S(l); T.turns++; if (forcedNow) T.forced++;
        if (hs.length === K + 1) { if (forcedNow) add(T.pre, hs[0]); else if ((round + d.id) % 7 === 0) add(T.ctl, hs[0]); }   // controls: a 1-in-7 sample
      }
    },
  });
}
if (opt('--sets')) {
  const label = opt('--label', 'ours');
  for (const set of opt('--sets').split(',')) {
    const rows = fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => r.G !== undefined && !r.error);
    for (const r of rows) { S(label).games++; measure(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'), { [r.side]: [label] }, r.map); }
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
const pc = (a, b) => b ? (100 * a / b).toFixed(2) + '%' : '-';
for (const [l, T] of [...stats].sort()) {
  const mean = (B, k) => B.n ? (B.sum[k] / B.n).toFixed(2) : '-';
  console.log(`== ${l} (${T.games} games): forced turns ${pc(T.forced, T.turns)} of ${T.turns}; state ${K} own turns before a forced turn (n ${T.pre.n}) vs before a non-forced one (sample n ${T.ctl.n})`);
  console.log('   ' + FEATS.map(k => `${k} ${mean(T.pre, k)} vs ${mean(T.ctl, k)}`).join(' | '));
}
