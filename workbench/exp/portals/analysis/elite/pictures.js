#!/usr/bin/env node
// Board pictures and a conversion timeline for chosen elite Portals team-games (exp/portals step 1c).
// usage: node exp/portals/analysis/elite/pictures.js <battleId:gameId> <team A|B> [rounds, default 300,400,470] ...
//   (pairs may repeat: key team [rounds] key team [rounds] ...)
// Picture legend (our = the chosen team): K our king's head (longest now), 2-9 other heads by length, # a head >= 10,
//   . our body, X / x their head / body, o natural pearl, % dropped pearl, | and - kelp edges, = and : portal edges.
'use strict';
const path = require('path'), fs = require('fs');
const ROOT = path.resolve(__dirname, '../../../..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());

function picture(ctx, M, us, round) {
  const { W, H, drag, pearls } = ctx;
  const wy = y => ((y % H) + H) % H, wx = x => ((x % W) + W) % W;
  const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
  const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
  const portalEdge = new Set();
  const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
  for (const pr of M.portals || []) for (const e of pr) { const c = canon(e); portalEdge.add(c.x + ',' + c.y + ',' + c.side); }
  const cell = Array.from({ length: H }, () => Array(W).fill(' '));
  for (const [k, v] of pearls) cell[(k / W) | 0][k % W] = v === -1 ? 'o' : '%';
  let king = null;
  for (const d of drag.values()) if (d.team === us && (!king || d.body.length > king.body.length || (d.body.length === king.body.length && d.id < king.id))) king = d;
  const ours = [], theirs = [];
  for (const d of drag.values()) {
    const L = d.body.length, mine = d.team === us;
    for (let i = 1; i < L; i++) { const s = d.body[i]; cell[s.y][s.x] = mine ? '.' : 'x'; }
    const h = d.body[0];
    cell[h.y][h.x] = mine ? (d === king ? 'K' : L >= 10 ? '#' : String(L)) : 'X';
    (mine ? ours : theirs).push(L);
  }
  ours.sort((a, b) => b - a); theirs.sort((a, b) => b - a);
  const lines = [];
  lines.push(`--- r${round}: ours ${ours.length} [${ours.slice(0, 16).join(' ')}${ours.length > 16 ? ' …' : ''}] total ${ours.reduce((a, b) => a + b, 0)} | theirs ${theirs.length} total ${theirs.reduce((a, b) => a + b, 0)}`);
  for (let y = 0; y < H; y++) {
    // the north edge row of tile row y
    let top = '';
    for (let x = 0; x < W; x++) top += '+' + (portalEdge.has(x + ',' + y + ',N') ? '=' : hk(x, y) ? '-' : ' ');
    lines.push(top + '+');
    let row = '';
    for (let x = 0; x < W; x++) row += (portalEdge.has(x + ',' + y + ',W') ? ':' : vk(x, y) ? '|' : ' ') + cell[y][x];
    lines.push(row + (vk(W, y) ? '|' : ' '));
  }
  return lines.join('\n');
}

const args = process.argv.slice(2);
const jobs = [];
for (let i = 0; i < args.length;) {
  const key = args[i++], team = args[i++];
  let rounds = [300, 400, 470];
  if (i < args.length && /^[\d,]+$/.test(args[i]) && !args[i].includes(':')) rounds = args[i++].split(',').map(Number);
  jobs.push({ key, team, rounds });
}
for (const job of jobs) {
  const [bid, gid] = job.key.split(':');
  const file = path.join(ROOT, 'data/top', bid, gid + '.replay.gz');
  const idx = fs.readFileSync(path.join(ROOT, 'data/top/index.jsonl'), 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l)).find(r => String(r.battleId) === bid && String(r.gameId) === gid);
  const R = load(file), M = R.match.map, us = job.team;
  const SNAP = new Set(job.rounds);
  const pics = [], tl = [], sacs = [];
  let last = -1;
  perGame(R, { map: 'Portals' }, {
    turn(d, round, ctx) {
      if (round === last) return;
      last = round;
      if (SNAP.has(round)) pics.push(picture(ctx, M, us, round));
      if (round % 10 === 0 && round >= 200) {
        const o = [...ctx.drag.values()].filter(q => q.team === us).map(q => q.body.length).sort((a, b) => b - a);
        tl.push({ r: round, u: o.length, k: o[0] || 0, s: o[1] || 0, t: o.reduce((a, b) => a + b, 0) });
      }
    },
    death(d, rec, i, other, round, ctx) {
      if (d.team !== us || round < 200 || (rec.cause !== 0 && rec.cause !== 1)) return;
      let king = null;
      for (const o of ctx.drag.values()) if (o.team === us && o !== d && (!king || o.body.length > king.body.length)) king = o;
      sacs.push({ r: round, L: d.body.length, c: rec.cause === 0 ? 's' : 't', kd: king ? ctx.tdist(king.body[0], d.body[0]) : -1, kl: king ? king.body.length : 0 });
    },
  });
  const name = idx ? (us === 'A' ? idx.teamA : idx.teamB) : '?', opp = idx ? (us === 'A' ? idx.teamB : idx.teamA) : '?';
  console.log(`\n=== ${job.key} team ${us} (${name}) vs ${opp}: final ours longest ${R.result['team' + us].longestDragon}, total ${R.result['team' + us].totalLength}, units ${R.result['team' + us].dragonCount}; winner ${R.result.winner}`);
  console.log('timeline r: units / king / second / total');
  console.log(tl.map(x => `r${x.r} ${x.u}/${x.k}/${x.s}/${x.t}`).join('  '));
  const win = (a, b) => sacs.filter(s => s.r >= a && s.r < b);
  for (const [a, b] of [[200, 250], [250, 300], [300, 350], [350, 400], [400, 450], [450, 500]]) {
    const w = win(a, b), ss = w.filter(s => s.c === 's'), tt = w.filter(s => s.c === 't');
    const near = x => x.filter(s => s.kd >= 0 && s.kd <= 3).length;
    console.log(`r${a}-${b - 1}: sac ${ss.length} (L ${ss.reduce((q, s) => q + s.L, 0)}, <=3 of king ${near(ss)}), trap ${tt.length} (L ${tt.reduce((q, s) => q + s.L, 0)}, <=3 of king ${near(tt)}); sac lengths ${ss.map(s => s.L).join(',')}`);
  }
  for (const p of pics) console.log(p);
}
