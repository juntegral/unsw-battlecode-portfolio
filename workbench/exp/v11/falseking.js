#!/usr/bin/env node
// v1.1 diagnostic of the belief failure the beacon targets: our dragons of length >= 8 that are not the team's longest (true, at their turn start)
// but tag " k1" (iAmLongest). Split by what they believed: bl0 (no fresh ally at all: the king forgotten), bl < our length (a fresh ally known but
// believed shorter than us: a stale or low length), bl >= our length (should not happen with k1). For each, the true longest's length minus ours.
// usage: node exp/v11/falseking.js <evalDir>[,<evalDir>] [--label x]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const dirs = process.argv[2].split(','), label = (() => { const i = process.argv.indexOf('--label'); return i > 0 ? process.argv[i + 1] : dirs.join('+'); })();
const A = { n: 0, k1: 0, bl0: 0, stale: 0, other: 0, gap: [0, 0, 0, 0], blAge: [] , posFar: 0};
for (const dir of dirs) {
  const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined);
  for (const r of rows) {
    const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
    const R = load(file), us = r.side, snap = new Map();
    ML.perGame(R, { map: '' }, {
      turn(d, round, ctx) { if (d.team !== us) return; let mx = 0, kh = null; for (const o of ctx.drag.values()) if (o.team === us && o.id !== d.id && o.body.length > mx) { mx = o.body.length; kh = o.body[0]; } snap.set(d.id, { round, my: d.body.length, mx, kh, W: ctx.W, H: ctx.H }); },
      indicator(e, round) {
        const s = snap.get(e.id); if (!s || s.round !== round || s.my < 8 || s.my >= s.mx) return;
        const m = / bl(\d+)@(-|\d+,\d+) k([01])/.exec(e.text || ''); if (!m) return;
        A.n++; if (m[3] !== '1') return;
        A.k1++; const bl = +m[1];
        if (bl === 0) A.bl0++; else if (bl < s.my) { A.stale++; if (m[2] !== '-' && s.kh) { const [bx, by] = m[2].split(',').map(Number); const dx = Math.abs(bx - s.kh.x), dy = Math.abs(by - s.kh.y); if (Math.min(dx, s.W - dx) + Math.min(dy, s.H - dy) <= 3) A.posFar++; } } else A.other++;
        const g = s.mx - s.my; A.gap[g <= 2 ? 0 : g <= 5 ? 1 : g <= 10 ? 2 : 3]++;
      },
    });
  }
}
const pc = (a, n) => n ? (100 * a / n).toFixed(0) + '%' : '–';
console.log(`${label}: L>=8 not longest tagged ${A.n}; says king ${pc(A.k1, A.n)} (${A.k1}). Of those: no fresh ally (bl0) ${pc(A.bl0, A.k1)}, a fresh ally believed shorter than us ${pc(A.stale, A.k1)}, other ${pc(A.other, A.k1)}; of the believed-shorter cases the believed head is the true king's (Manhattan <= 3) in ${pc(A.posFar, A.stale)}; true king longer than us by 1-2 ${pc(A.gap[0], A.k1)}, 3-5 ${pc(A.gap[1], A.k1)}, 6-10 ${pc(A.gap[2], A.k1)}, 11+ ${pc(A.gap[3], A.k1)}`);
