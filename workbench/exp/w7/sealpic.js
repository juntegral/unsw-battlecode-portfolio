#!/usr/bin/env node
// W7c board check: moves where some legal one-step alternative would have sealed an adjacent ally head (left it no free exit, as boxing.js)
// and whether the chosen move sealed one. Counts per set; --show N prints the first N such scenes where the chosen move avoided the seal
// (9x9 around the mover: '@' head before, '!' head after, 'S' a sealing alternative, '=' our body, digits ally heads (length), '-' ally body,
// 'X' / 'x' enemy head / body).
// usage: node exp/w7/sealpic.js <setDir> [--show N] [--maps a,b]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), set = args[0], si = args.indexOf('--show'), SHOW = si >= 0 ? +args[si + 1] : 0, mi = args.indexOf('--maps'), MAPS = mi >= 0 ? new Set(args[mi + 1].split(',')) : null;
const DIRS = ['N', 'E', 'S', 'W'];
let shown = 0; const C = { moves: 0, sealOption: 0, sealedChosen: 0, avoided: 0 };
for (const l of fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean)) {
  const r = JSON.parse(l); if (MAPS && !MAPS.has(r.map)) continue;
  const R = load(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'));
  perGame(R, { map: r.map, variant: 'a' }, {
    action(d, e, round, ctx, hb) {
      if (d.team !== r.side) return;
      const a = e.action; if (!a || a.kind !== 'move' || d.fate) return;
      const { occ, key, across, drag, W, H } = ctx;
      const h0 = hb[0], ownBefore = new Set(hb.map(s => key(s.x, s.y)));
      const occB = k => (occ.has(k) && occ.get(k) !== d.id) || ownBefore.has(k);   // the board before our move
      const seals = k0 => {   // would our head on tile k0 (x, y) leave an adjacent ally head with no free exit?
        const [x, y] = k0;
        for (const dir of DIRS) {
          const u = across(x, y, dir); if (!u) continue;
          const ku = key(u.x, u.y); if (!occ.has(ku)) continue;
          const o = drag.get(occ.get(ku)); if (!o || o.id === d.id || o.team !== d.team || o.body[0].x !== u.x || o.body[0].y !== u.y) continue;
          let free = 0;
          for (const d2 of DIRS) { const v = across(u.x, u.y, d2); if (!v) continue; if (o.body.length >= 2 && v.x === o.body[1].x && v.y === o.body[1].y) continue; const kv = key(v.x, v.y);
            if (v.x === x && v.y === y) continue; if (occB(kv)) continue; free++; }
          if (free === 0) return true;
        }
        return false;
      };
      const neck = hb.length >= 2 ? hb[1] : null;
      const alts = [];
      for (const dir of DIRS) { const u = across(h0.x, h0.y, dir); if (!u || (neck && u.x === neck.x && u.y === neck.y)) continue; if (occB(key(u.x, u.y))) continue; alts.push(u); }
      const t = d.body[0];
      const sealAlts = alts.filter(u => (u.x !== t.x || u.y !== t.y) && seals([u.x, u.y]));
      const chosenSeals = seals([t.x, t.y]);
      C.moves++; if (sealAlts.length || chosenSeals) C.sealOption++; if (chosenSeals) C.sealedChosen++; if (sealAlts.length && !chosenSeals) C.avoided++;
      if (SHOW && shown < SHOW && sealAlts.length && !chosenSeals) {
        shown++;
        const rows = [];
        for (let dy = -4; dy <= 4; dy++) { let row = '';
          for (let dx = -4; dx <= 4; dx++) { const x = (h0.x + dx + W) % W, y = (h0.y + dy + H) % H, k = key(x, y); let c = '·';
            if (occ.has(k)) { const o = drag.get(occ.get(k)); const isHead = o && o.body[0].x === x && o.body[0].y === y; c = !o ? '?' : o.id === d.id ? (isHead ? '!' : '=') : o.team === d.team ? (isHead ? String(Math.min(9, o.body.length)) : '-') : (isHead ? 'X' : 'x'); }
            if (sealAlts.some(u => u.x === x && u.y === y)) c = 'S';
            if (x === h0.x && y === h0.y && !(t.x === x && t.y === y)) c = '@';
            row += c; }
          rows.push(row); }
        console.log(`${r.key} r${round} #${d.id} L${hb.length} moved ${a.steps.join('')}: a sealing alternative existed (S), the move did not seal\n    ${rows.join('\n    ')}\n`);
      }
    },
  });
}
const pc = (a, b) => b ? (100 * a / b).toFixed(2) + '%' : '-';
console.log(`${set}: moves ${C.moves}; a seal was possible ${pc(C.sealOption, C.moves)}; the move sealed ${pc(C.sealedChosen, C.moves)} (${C.sealedChosen}); a sealing alternative existed and the move avoided it ${C.avoided}`);
