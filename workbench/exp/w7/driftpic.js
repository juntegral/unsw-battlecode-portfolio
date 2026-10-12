#!/usr/bin/env node
// W7d board check: moves of a piece >= 3 from every ally head where some legal one-step alternative would have drifted further into a window of
// negative head balance within 8 (as drift.js), and whether the chosen move did. Counts per set; --show N prints scenes where the move avoided it
// (11x11 around the mover: '@' head before, '!' head after, 'D' a drifting alternative, '=' our body, digits ally heads (length), '-' ally body,
// 'X' / 'x' enemy head / body).
// usage: node exp/w7/driftpic.js <setDir> [--show N] [--maps a,b]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), set = args[0], si = args.indexOf('--show'), SHOW = si >= 0 ? +args[si + 1] : 0, mi = args.indexOf('--maps'), MAPS = mi >= 0 ? new Set(args[mi + 1].split(',')) : null;
const DIRS = ['N', 'E', 'S', 'W'];
let shown = 0; const C = { moves: 0, option: 0, drifted: 0, avoided: 0 };
for (const l of fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean)) {
  const r = JSON.parse(l); if (MAPS && !MAPS.has(r.map)) continue;
  const R = load(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'));
  perGame(R, { map: r.map, variant: 'a' }, {
    action(d, e, round, ctx, hb) {
      if (d.team !== r.side) return;
      const a = e.action; if (!a || a.kind !== 'move' || d.fate) return;
      const { occ, key, across, drag, W, H } = ctx;
      const man = (p, q) => { const dx = Math.abs(p.x - q.x), dy = Math.abs(p.y - q.y); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
      const allies = [], enemies = [];
      for (const o of drag.values()) { if (o.id === d.id || !o.body.length) continue; (o.team === d.team ? allies : enemies).push(o.body[0]); }
      if (!allies.length) return;
      const h0 = hb[0]; const dA0 = Math.min(...allies.map(q => man(q, h0))); if (dA0 < 3) return;
      const drifts = u => { const dA1 = Math.min(...allies.map(q => man(q, u))); if (dA1 <= dA0) return false; const a8 = allies.filter(q => man(q, u) <= 8).length, e8 = enemies.filter(q => man(q, u) <= 8).length; return a8 + 1 - e8 < 0; };
      const ownBefore = new Set(hb.map(s => key(s.x, s.y))), neck = hb.length >= 2 ? hb[1] : null;
      const alts = [];
      for (const dir of DIRS) { const u = across(h0.x, h0.y, dir); if (!u || (neck && u.x === neck.x && u.y === neck.y)) continue; const k = key(u.x, u.y); if ((occ.has(k) && occ.get(k) !== d.id) || ownBefore.has(k)) continue; alts.push(u); }
      const t = d.body[0];
      const dAlts = alts.filter(u => (u.x !== t.x || u.y !== t.y) && drifts(u));
      const chosen = drifts(t);
      C.moves++; if (dAlts.length || chosen) C.option++; if (chosen) C.drifted++; if (dAlts.length && !chosen) C.avoided++;
      if (SHOW && shown < SHOW && dAlts.length && !chosen) {
        shown++; const rows = [];
        for (let dy = -5; dy <= 5; dy++) { let row = '';
          for (let dx = -5; dx <= 5; dx++) { const x = (h0.x + dx + W) % W, y = (h0.y + dy + H) % H, k = key(x, y); let c = '·';
            if (occ.has(k)) { const o = drag.get(occ.get(k)); const isHead = o && o.body[0].x === x && o.body[0].y === y; c = !o ? '?' : o.id === d.id ? (isHead ? '!' : '=') : o.team === d.team ? (isHead ? String(Math.min(9, o.body.length)) : '-') : (isHead ? 'X' : 'x'); }
            if (dAlts.some(u => u.x === x && u.y === y)) c = 'D';
            if (x === h0.x && y === h0.y && !(t.x === x && t.y === y)) c = '@';
            row += c; }
          rows.push(row); }
        console.log(`${r.key} r${round} #${d.id} L${hb.length} (nearest ally ${dA0}) moved ${a.steps.join('')}: a drifting alternative existed (D), the move did not drift\n    ${rows.join('\n    ')}\n`);
      }
    },
  });
}
const pc = (a, b) => b ? (100 * a / b).toFixed(2) + '%' : '-';
console.log(`${set}: moves of pieces >= 3 from every ally ${C.moves}; a drift into a minority was possible ${pc(C.option, C.moves)}; the move drifted ${pc(C.drifted, C.moves)} (${C.drifted}); a drifting alternative existed and the move avoided it ${C.avoided}`);
