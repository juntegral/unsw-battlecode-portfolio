#!/usr/bin/env node
// Q2: our queen's rammed deaths. For each: the rammer (id, length, its free steps ceil(L/4)), how far its head was from her head at the start of
// her last turn (path distance over free tiles, and Chebyshev: in her 7x7 window or not), the value of her last move (her indicator), her
// length, and how many enemy heads were within 4 of her then. usage: node exp/q2/rammed.js <runq set dir>... [--nopocket]
'use strict';
process.env.UNSW_RULES = process.env.UNSW_RULES || '123';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const skip = process.argv.includes('--nopocket') ? /autarky|dilemma|slithery/i : null;
for (const set of process.argv.slice(2).filter(a => !a.startsWith('--'))) {
  const rows = fs.readFileSync(path.join(set, 'rows.jsonl'), 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse);
  const agg = { n: 0, seen: 0, doomed: 0, distFree: 0, two: 0, near: [] };
  for (const r of rows) {
    if (skip && skip.test(r.map)) continue;
    const f = path.join(set, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
    const Q = r.side === 'A' ? 0 : 1;
    let snap = null, lastInd = '', out = null;
    perGame(load(f), { map: r.map, variant: 'a' }, {
      turn(d, round, ctx) {
        if (d.id !== Q) return;
        // snapshot at the start of her turn: enemy heads with their lengths and path distance to her head (free tiles only, heads may end on her)
        const { W, H, across, drag, occ } = ctx, h = d.body[0], key = (x, y) => y * W + x;
        const dist = new Map([[key(h.x, h.y), 0]]), q = [h];
        for (let i = 0; i < q.length; i++) { const t = q[i], dd = dist.get(key(t.x, t.y)); if (dd >= 8) continue;
          for (const dir of 'NESW') { const u = across(t.x, t.y, dir); if (!u) continue; const k = key(u.x, u.y); if (dist.has(k)) continue;
            const o = occ.get(k); if (o !== undefined) { const od = drag.get(o); if (od && od.team !== d.team && od.body[0].x === u.x && od.body[0].y === u.y) dist.set(k, dd + 1); continue; }
            dist.set(k, dd + 1); q.push(u); } }
        const heads = [];
        for (const o of drag.values()) { if (o.team === d.team) continue; const oh = o.body[0], k = key(oh.x, oh.y);
          const dx = Math.min(Math.abs(oh.x - h.x), W - Math.abs(oh.x - h.x)), dy = Math.min(Math.abs(oh.y - h.y), H - Math.abs(oh.y - h.y));
          heads.push({ id: o.id, L: o.body.length, path: dist.has(k) ? dist.get(k) : 99, cheb: Math.max(dx, dy) }); }
        snap = { round, L: d.body.length, heads };
      },
      indicator(e, round) { if (e.id === Q) lastInd = e.text || ''; },
      death(d, rec, idx, other, round) {
        if (d.id !== Q || CAUSE[rec.cause] !== 'rammed' || !snap) return;
        const k = other ? snap.heads.find(x => x.id === other.id) : null;
        out = { round, L: d.body.length, rammer: other ? `#${other.id} L${other.body.length}` : '?', at: k ? `path ${k.path} cheb ${k.cheb} free ${Math.ceil(k.L / 4)}` : 'not tracked',
          near4: snap.heads.filter(x => x.path <= 4).length, ind: lastInd };
        agg.n++; if (k && k.cheb <= 3) agg.seen++; if (/ v-[0-9]{3,}/.test(lastInd)) agg.doomed++; if (k && k.path <= Math.ceil(k.L / 4)) agg.distFree++; if (/^[NESW]{2,} /.test(lastInd)) agg.two++; agg.near.push(out.near4);
      },
    });
    if (out && process.argv.includes('--games')) console.log(`  ${r.key} r${out.round} L${out.L} by ${out.rammer} (${out.at}) enemy heads within 4: ${out.near4} | ${out.ind}`);
  }
  const med = a => { const s = a.slice().sort((x, y) => x - y); return s.length ? s[s.length >> 1] : '-'; };
  console.log(`${path.basename(set)}: rammed queens ${agg.n}; rammer in her 7x7 window at her last turn ${agg.seen}; her last move valued <= -100 (doomed) ${agg.doomed}; rammer within its free steps ${agg.distFree}; her last move a sprint ${agg.two}; enemy heads within path 4 (median) ${med(agg.near)}`);
}
