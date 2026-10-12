#!/usr/bin/env node
// v1.4: how our heads get rammed (mass ledger cause 'rammed': an enemy head moved into ours; both die). Per our rammed death: the rammer's
// steps (a sprint of >= 2 steps, from its 'ram' record), the Manhattan distance between the two heads at the start of that round, our length vs
// the rammer's, and the frontier bin of our head. Distance 1 at the round start = we were left adjacent since the previous round; 2 with a
// single-step ram = one of the two closed in this round before the rammer moved (our move when our id is lower).
// usage: node exp/v14/ramctx.js <map file name> name=dir,dir [name2=dir,...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const { geometry } = require(path.join(ROOT, 'exp', 'spatial', 'lib.js'));
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const [mapName, ...setArgs] = process.argv.slice(2);
for (const sa of setArgs) {
  const [name, dirs] = sa.split('=');
  const agg = { n: 0, spr: 0, d1: 0, d2: 0, d3p: 0, ourIdLower: 0, lenLE: 0, bins: [0, 0, 0, 0, 0, 0], games: 0, ourHR2: 0 };
  for (const dir of dirs.split(',')) {
    const rowsF = path.join(dir, 'rows.jsonl'); if (!fs.existsSync(rowsF)) continue;
    const last = new Map();
    for (const r of fs.readFileSync(rowsF, 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l))) if (r.G !== undefined && !r.botProblem && r.map === mapName) last.set(r.key, r);
    for (const row of last.values()) {
      const f = path.join(dir, 'games', row.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
      const R = load(f), M = R.match.map, W = M.width, us = row.side;
      const g = geometry(M, 'x', '?'), bin = g.bin[us];
      agg.games++;
      let lastR = -1; const start = new Map(); const pend = [];
      ML.perGame(R, { map: M.mapName }, {
        turn(d, round, ctx) {
          if (round === lastR) return; lastR = round; start.clear();
          for (const o of ctx.drag.values()) start.set(o.id, { x: o.body[0].x, y: o.body[0].y, len: o.body.length });
        },
        death(d, rec, idx, other, round) {
          if (d.team === us && rec.cause === 2 && other) pend.push({ me: d.id, them: other.id, myLen: d.body.length, theirLen: other.body.length, b: bin[d.body[0].y * W + d.body[0].x], idx, round, s0: start.get(d.id), s1: start.get(other.id) });
          if (rec.cause === 3) for (const p of pend) if (p.idx === rec.pair) p.spr = rec.spr;
        },
      });
      for (const p of pend) {
        agg.n++; if (p.spr) agg.spr++;
        const b = p.b === undefined ? 5 : p.b; agg.bins[b]++;
        if (p.s0 && p.s1) { const dx = Math.abs(p.s0.x - p.s1.x), dy = Math.abs(p.s0.y - p.s1.y); const d = Math.min(dx, W - dx) + Math.min(dy, M.height - dy); if (d <= 1) agg.d1++; else if (d === 2) agg.d2++; else agg.d3p++; }
        if (p.me < p.them) agg.ourIdLower++;
        if (p.myLen <= p.theirLen) agg.lenLE++;
      }
    }
  }
  const pc = x => agg.n ? (100 * x / agg.n).toFixed(0) + '%' : '–';
  console.log(`${name} ${mapName}: ${agg.games} games, our rammed deaths ${agg.n} (${(agg.n / agg.games).toFixed(1)}/game) | rammer sprinted ${pc(agg.spr)} | heads at round start: adjacent ${pc(agg.d1)}, 2 apart ${pc(agg.d2)}, 3+ ${pc(agg.d3p)} | our id lower (we moved first) ${pc(agg.ourIdLower)} | our length <= theirs ${pc(agg.lenLE)} | our bin 0-4 ${agg.bins.slice(0, 5).join('/')}`);
}
