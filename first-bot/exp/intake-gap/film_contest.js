#!/usr/bin/env node
// Stage 3 close reading of one contest loss (exp/intake-gap/contest.js picks): a natural pearl that spawned nearer to our head
// but was eaten by the opponent. Prints, for every round from its spawn to its end: our designated head (id, length, path
// distance to the pearl, its INDICATOR text), our nearest head, the opponent heads within 8 of the pearl (id, length, distance,
// their move steps), and an 11x11 picture centred on the pearl at the spawn round and at the eating round.
// usage: node exp/intake-gap/film_contest.js <set>:<gameId> <x> <y> <spawnRound> [--pad 2]
// Picture legend: '*' the pearl, our heads 'U' / bodies 'u', opponent heads 'E' / bodies 'e', other natural pearls 'o',
// dropped pearls '+', kelp is not drawn; '.' empty.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const X = require(path.join(ROOT, 'exp', 'territory-analysis', 'extract.js'));
const RL = require('./rawload.js');
const [key, xs, ys, rs] = process.argv.slice(2);
const [set, gid] = key.split(':');
const dir = path.join(ROOT, 'data', 'online', set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
const gm = (idx.games || idx).find(g => String(g.gameId) === gid);
const us = String(gm.ourSide).toUpperCase();
const R = RL.load(path.join(dir, 'M' + gid + '.replay'));
const M = R.match.map, W = M.width, H = M.height, G = X.geometry(R), N = G.N, nb = G.nb;
const px = +xs, py = +ys, pk = py * W + px, r0 = +rs;
const Q = new Int32Array(N + 8), D = new Int16Array(N);
const bfsFrom = k0 => { D.fill(-1); let qh = 0, qt = 0; D[k0] = 0; Q[qt++] = k0; while (qh < qt) { const k = Q[qh++]; for (let j = 0; j < 4; j++) { const u = nb[k * 4 + j]; if (u < 0 || D[u] >= 0) continue; D[u] = D[k] + 1; Q[qt++] = u; } } };
bfsFrom(pk);
const label = new Map(), steps = new Map();
let lastRound = -99, designated = -1, done = false, eatInfo = null;
const lines = [];
const pic = (ctx, title) => {
  const rows = [title];
  for (let dy = -5; dy <= 5; dy++) {
    let s = '';
    for (let dx = -5; dx <= 5; dx++) {
      const x = G.wx(px + dx), y = G.wy(py + dy), k = y * W + x;
      let c = '.';
      const o = ctx.occ.get(k);
      if (o !== undefined) { const d = ctx.drag.get(o); const head = d && d.body[0].x === x && d.body[0].y === y; const mine = d && d.team === us; c = head ? (mine ? 'U' : 'E') : (mine ? 'u' : 'e'); }
      else if (ctx.pearls.has(k)) c = k === pk ? '*' : ctx.pearls.get(k) < 0 ? 'o' : '+';
      s += c;
    }
    rows.push('    ' + s);
  }
  return rows.join('\n');
};
const hooks = {
  turn(d, round, ctx) {
    if (round !== lastRound) {
      lastRound = round;
      if (!done && round >= r0) {
        const ours = [], theirs = [];
        for (const o of ctx.drag.values()) { const h = o.body[0], k = h.y * W + h.x, dd = D[k]; (o.team === us ? ours : theirs).push({ id: o.id, len: o.body.length, d: dd < 0 ? 999 : dd }); }
        ours.sort((a, b) => a.d - b.d); theirs.sort((a, b) => a.d - b.d);
        if (round === r0) { if (!ctx.pearls.has(pk)) { console.log('no pearl at', px, py, 'in round', r0); process.exit(1); } designated = ours.length ? ours[0].id : -1; lines.push(pic(ctx, `r${round} (spawn): designated head #${designated}`)); }
        const des = ours.find(o => o.id === designated);
        lines.push(`r${round}: ours ${des ? `#${des.id} L${des.len} d${des.d} "${label.get(des.id) || ''}"` : `#${designated} dead`}; nearest ours ${ours[0] ? `#${ours[0].id} L${ours[0].len} d${ours[0].d}` : '-'}; theirs ≤8: ${theirs.filter(t => t.d <= 8).map(t => `#${t.id} L${t.len} d${t.d}${(steps.get(t.id) || 0) >= 2 ? ' spr' : ''}`).join(', ') || '-'}`);
      }
      label.clear();
    }
  },
  indicator(e) { label.set(e.id, e.text); },
  action(d, e) { steps.set(d.id, e.action && e.action.kind === 'move' ? e.action.steps.length : 0); },
  eat(d, k, o, round, ctx) {
    if (done || k !== pk || round < r0) return;
    done = true; eatInfo = `eaten r${round} by #${d.id} (${d.team === us ? 'us' : 'them'}) L${d.body.length}, move ${(steps.get(d.id) || 0)} step(s)`;
    lines.push(pic(ctx, `r${round} (eaten, board before this move)`));
  },
};
ML.perGame(R, { map: gm.mapName }, hooks);
console.log(`${key} ${gm.mapName} us=${us} pearl (${px},${py}) spawn r${r0}: ${eatInfo || 'not eaten'}`);
console.log(lines.join('\n'));
