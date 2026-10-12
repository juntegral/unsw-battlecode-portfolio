#!/usr/bin/env node
'use strict';
// where_ab.js — where teams eat and where their heads are on each pearl layout (research/experiments/cand-mapid.md, part B).
// Stage 1-2 on the full population of one map: every top-vs-top game (data/top) and every game of our online sets
// against the elite, layout from exp/mapid/cache/feat.jsonl. Mirrored into team A's frame (x -> W-1-x for team B on a
// map with SYMMETRY y) so "own side" is always the left. Output: per layout and group, natural pearls eaten in r0-99 and
// r100-199 per game by 5x5 block, head-turns per block in r0-99, and the first round a team's head reaches the lower half.
// usage (repository root): node exp/mapid/where_ab.js [--map Schooltime] [--jobs 3] [--rmax 200]
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const mapName = opt('map', 'Schooltime'), B5 = 5;
if (argv[0] === '--worker') {
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const load = makeLoader(viewerSource());
  process.on('message', t => {
    try {
      const R = load(t.file), M = R.match.map, W = M.width, H = M.height, bw = Math.ceil(W / B5), bh = Math.ceil(H / B5);
      const mirror = (tm, x) => tm === 'B' && M.symmetry !== 'x' ? W - 1 - x : x;   // Schooltime: SYMMETRY y (left-right)
      const mk = () => ({ e0: new Array(bw * bh).fill(0), e1: new Array(bw * bh).fill(0), h0: new Array(bw * bh).fill(0), lower: null, eat0: 0 });
      const X = { A: mk(), B: mk() };
      const blk = (tm, x, y) => Math.floor(y / B5) * bw + Math.floor(mirror(tm, x) / B5);
      const hooks = {
        turn(d, r) { if (r < 100) X[d.team].h0[blk(d.team, d.body[0].x, d.body[0].y)]++; if (X[d.team].lower === null && d.body[0].y >= H / 2) X[d.team].lower = r; },
        eat(d, k, o, r) { if (o >= 0) return; const x = k % W, y = (k - x) / W; if (r < 100) { X[d.team].e0[blk(d.team, x, y)]++; X[d.team].eat0++; } else if (r < 200) X[d.team].e1[blk(d.team, x, y)]++; },
      };
      perGame(R, { map: t.map }, hooks);
      process.send({ ok: true, res: { ...t, bw, bh, sym: M.symmetry, A: X.A, B: X.B } });
    } catch (e) { process.send({ ok: false, key: t.key, error: String(e).slice(0, 200) }); }
  });
  return;
}
const feat = [];
for (const l of fs.readFileSync(path.join(__dirname, 'cache', 'feat.jsonl'), 'utf8').split('\n')) { if (!l.trim()) continue; const g = JSON.parse(l); if (g.map === mapName && (g.layout === 'a' || g.layout === 'b')) feat.push({ key: g.key, src: g.src, set: g.set, gameId: g.gameId, map: g.map, layout: g.layout, winner: g.winner, us: g.us }); }
// replay files
const topFile = new Map();
for (const l of fs.readFileSync(path.join(ROOT, 'data', 'top', 'index.jsonl'), 'utf8').split('\n')) { if (!l.trim()) continue; const g = JSON.parse(l); topFile.set(g.gameId, path.join(ROOT, 'data', 'top', String(g.battleId), g.gameId + '.replay.gz')); }
for (const g of feat) g.file = g.src === 'top' ? topFile.get(g.gameId) : path.join(ROOT, 'data', 'online', g.set, 'M' + g.gameId + '.replay');
const CACHE = path.join(__dirname, 'cache', `where-${mapName.replace(/ /g, '_')}.jsonl`);
const done = new Map(fs.existsSync(CACHE) ? fs.readFileSync(CACHE, 'utf8').split('\n').filter(Boolean).map(l => { const x = JSON.parse(l); return [x.key, x]; }) : []);
const q = feat.filter(g => !done.has(g.key) && g.file && fs.existsSync(g.file));
(async () => {
  if (q.length) {
    console.error(`where: ${q.length} games to read`);
    let n = 0;
    await Promise.all(Array.from({ length: Math.min(3, +opt('jobs', 3), q.length) }, () => new Promise(res => {
      const w = cp.fork(__filename, ['--worker'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
      const next = () => { const t = q.shift(); if (!t) { w.kill(); res(); return; } w.send(t); };
      w.on('message', m => { if (m.ok) { fs.appendFileSync(CACHE, JSON.stringify(m.res) + '\n'); done.set(m.res.key, m.res); } if (++n % 200 === 0) console.error(`  ${n}`); next(); });
      next();
    })));
  }
  const G = {};
  for (const x of done.values()) {
    const add = (grp, T) => { const k = x.layout + '|' + grp; const a = G[k] || (G[k] = { n: 0, bw: x.bw, bh: x.bh, e0: new Array(x.bw * x.bh).fill(0), e1: new Array(x.bw * x.bh).fill(0), h0: new Array(x.bw * x.bh).fill(0), lower: [], eat0: [] }); a.n++; for (let i = 0; i < a.e0.length; i++) { a.e0[i] += T.e0[i]; a.e1[i] += T.e1[i]; a.h0[i] += T.h0[i]; } a.lower.push(T.lower === null ? 999 : T.lower); a.eat0.push(T.eat0); };
    if (x.src === 'top') { if (!x.winner) continue; add('top winner', x[x.winner]); add('top loser', x[x.winner === 'A' ? 'B' : 'A']); }
    else { add('ours', x[x.us]); add('elite vs us', x[x.us === 'A' ? 'B' : 'A']); }
  }
  const med = a => { const s = a.slice().sort((p, q2) => p - q2); return s[Math.floor((s.length - 1) / 2)]; };
  for (const k of Object.keys(G).sort()) {
    const a = G[k];
    console.log(`\n### ${mapName} ${k} (${a.n} team-games): first head in the lower half r${med(a.lower)} (median), natural eaten r0-99 ${(a.eat0.reduce((s, v) => s + v, 0) / a.n).toFixed(1)}/game`);
    for (const [name, arr, scale] of [['eaten r0-99 per game (x10)', a.e0, 10], ['eaten r100-199 per game (x10)', a.e1, 10], ['head-turns r0-99 per game', a.h0, 1]]) {
      console.log(`  ${name}: own side = left`);
      for (let by = 0; by < a.bh; by++) { let line = '   '; for (let bx = 0; bx < a.bw; bx++) { const v = Math.round(arr[by * a.bw + bx] / a.n * scale); line += String(v).padStart(4); } console.log(line); }
    }
  }
})();
