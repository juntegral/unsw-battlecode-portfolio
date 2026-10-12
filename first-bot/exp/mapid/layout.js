#!/usr/bin/env node
'use strict';
// layout.js — the true pearl layout (a / b) of a game, from the replay's own natural spawns. No games, no network.
// The server plays Devil, Queen Of Spades, Schooltime and Slithery Fight in two pearl layouts (a = maps/online-20260927,
// b = maps/variants/<file>_b.map) and Prisoners Dilemma with 6 (a) or 10 (b) dragons (research/observations/pearl-variants.md).
// A layout turns some mirror groups off (TILE max 0: never spawns). So one natural spawn on a tile that never spawns in
// layout X rules X out:
//   evA = natural spawns on tiles that never spawn in b (evidence for a), evB = on tiles that never spawn in a.
//   layout = 'a' if evA > 0 = evB, 'b' if evB > 0 = evA, '?' if neither (a short game), 'x' if both (contradiction).
// A natural spawn = a tileChange with a pearl after roundStart and before the round's first turnStart (tools/pearl_layout.js
// uses the same rule; death drops happen inside turns). Prisoners Dilemma: 10 starting dragons = b (spawns checked too).
//
// module: require('./exp/mapid/layout.js').classify(R, mapName) -> { layout, evA, evB, nInit, firstEv }
// usage (repository root):
//   node exp/mapid/layout.js scan [--jobs 3] [--src top,online] [--maps all|two]   -> exp/mapid/layouts.jsonl (append; skips done)
//   node exp/mapid/layout.js check                                                   agreement with data/pearl_layout/variants.json
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const FAM = {
  'Devil': ['devil', 'devil_b'], 'Queen Of Spades': ['queen_of_spades', 'queen_of_spades_b'], 'Schooltime': ['schooltime', 'schooltime_b'],
  'Slithery Fight': ['slithery_fight', 'slithery_fight_b'], 'Prisoners Dilemma': ['prisoners_dilemma', 'prisoners_dilemma_10'],
};
const TWO = new Set(Object.keys(FAM));
const tables = new Map();
function table(file) {   // Uint8Array: 1 if the tile can spawn (TILE max > 0)
  if (tables.has(file)) return tables.get(file);
  const L = fs.readFileSync(file, 'utf8').split('\n');
  const m = /^MAP (\d+) (\d+)/.exec(L[0]); const W = +m[1], H = +m[2];
  const on = new Uint8Array(W * H);
  for (const l of L) if (l.startsWith('TILE ')) { const [x, y, , mx] = l.trim().split(/\s+/).slice(1).map(Number); on[y * W + x] = mx > 0 ? 1 : 0; }
  const t = { W, H, on }; tables.set(file, t); return t;
}
function famTables(mapName) {
  const f = FAM[mapName]; if (!f) return null;
  return { a: table(path.join(ROOT, 'maps', 'online-20260927', f[0] + '.map')), b: table(path.join(ROOT, 'maps', 'variants', f[1] + '.map')) };
}
function naturalSpawns(R) {
  const out = []; let r = -1, rs = false;
  for (const e of R.events) {
    if (e.type === 'roundStart') { r = e.round; rs = true; }
    else if (e.type === 'turnStart') rs = false;
    else if (rs && e.type === 'tileChange' && e.hasPearl) out.push([r, e.tile.y * R.match.map.width + e.tile.x]);
  }
  return out;
}
function classify(R, mapName) {
  const M = R.match.map, nInit = M.initialDragons.length;
  const T = famTables(mapName);
  if (!T) return { layout: 'a', evA: 0, evB: 0, nInit, firstEv: null, one: true };
  if (T.a.W !== M.width || T.a.H !== M.height) return { layout: '?', evA: 0, evB: 0, nInit, firstEv: null, err: 'size' };
  let evA = 0, evB = 0, firstEv = null;
  for (const [r, k] of naturalSpawns(R)) {
    const a = T.a.on[k], b = T.b.on[k];
    if (a && !b) { evA++; if (firstEv === null) firstEv = r; }
    else if (b && !a) { evB++; if (firstEv === null) firstEv = r; }
  }
  let layout = evA > 0 && evB === 0 ? 'a' : evB > 0 && evA === 0 ? 'b' : evA > 0 && evB > 0 ? 'x' : '?';
  if (mapName === 'Prisoners Dilemma') {   // the dragon count decides; spawns only confirm
    const byN = nInit === 10 ? 'b' : 'a';
    return { layout: byN, evA, evB, nInit, firstEv, spawnSays: layout };
  }
  return { layout, evA, evB, nInit, firstEv };
}
module.exports = { classify, naturalSpawns, FAM, TWO, famTables };

// ---------------------------------------------------------------------------------------------------------------------
if (require.main !== module) return;
const argv = process.argv.slice(2), cmd = argv[0];
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const OUT = path.join(__dirname, 'layouts.jsonl');
// our online sets against the elite (research/OVERNIGHT-2026-09-29.md "분석 모집단"): every set with index.json except the
// auto-scrim and mid-table sets (r1-autoscrim, r1-online, g1, g2)
const NOT_ELITE = new Set(['r1-autoscrim', 'r1-online', 'g1', 'g2', 'snapshots', 'top-sample']);
function tasks(src, mapsSel) {
  const out = [], want = m => mapsSel === 'all' || TWO.has(m);
  if (src.includes('top')) {
    for (const l of fs.readFileSync(path.join(ROOT, 'data', 'top', 'index.jsonl'), 'utf8').split('\n')) {
      if (!l.trim()) continue; const g = JSON.parse(l); if (!want(g.map)) continue;
      const f = path.join(ROOT, 'data', 'top', String(g.battleId), g.gameId + '.replay.gz'); if (!fs.existsSync(f)) continue;
      out.push({ key: 'top:' + g.gameId, src: 'top', set: 'top', gameId: g.gameId, map: g.map, file: f, at: g.at, winner: g.winner });
    }
  }
  if (src.includes('online')) {
    const OD = path.join(ROOT, 'data', 'online');
    for (const s of fs.readdirSync(OD)) {
      if (NOT_ELITE.has(s) || !fs.existsSync(path.join(OD, s, 'index.json'))) continue;
      const idx = JSON.parse(fs.readFileSync(path.join(OD, s, 'index.json'), 'utf8'));
      for (const g of idx.games || idx) {
        if (!want(g.mapName)) continue;
        const f = path.join(OD, s, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
        out.push({ key: s + ':' + g.gameId, src: 'online', set: s, gameId: g.gameId, map: g.mapName, file: f, at: g.completedAt, us: String(g.ourSide).toUpperCase(), opp: g.opponentTeam, ourWin: g.ourWin });
      }
    }
  }
  return out;
}
if (cmd === '--worker') {
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const load = makeLoader(viewerSource());
  process.on('message', t => {
    try {
      const R = load(t.file), c = classify(R, t.map);
      process.send({ ok: true, row: { ...t, file: undefined, ...c, rounds: R.result ? R.result.rounds || null : null, endReason: R.result ? R.result.endReason : null } });
    } catch (e) { process.send({ ok: false, key: t.key, error: String(e).slice(0, 200) }); }
  });
} else if (cmd === 'scan') {
  const jobs = +opt('jobs', 3), src = opt('src', 'top,online').split(','), mapsSel = opt('maps', 'two');
  const done = new Set(fs.existsSync(OUT) ? fs.readFileSync(OUT, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l).key) : []);
  const q = tasks(src, mapsSel).filter(t => !done.has(t.key));
  console.log(`scan: ${q.length} games to classify (${done.size} already in ${path.relative(ROOT, OUT)})`);
  let n = 0, err = 0; const t0 = Date.now();
  Promise.all(Array.from({ length: Math.min(jobs, q.length) }, () => new Promise(res => {
    const w = cp.fork(__filename, ['--worker'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
    const next = () => { const t = q.shift(); if (!t) { w.kill(); res(); return; } w.send(t); };
    w.on('message', m => {
      if (m.ok) fs.appendFileSync(OUT, JSON.stringify(m.row) + '\n'); else { err++; console.error('error', m.key, m.error); }
      if (++n % 200 === 0) console.log(`  ${n} (${Math.round((Date.now() - t0) / 1000)}s)`);
      next();
    });
    next();
  }))).then(() => console.log(`done ${n} games, errors ${err}, ${Math.round((Date.now() - t0) / 1000)}s`));
} else if (cmd === 'check') {
  const V = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'pearl_layout', 'variants.json'), 'utf8'));
  const vj = new Map();
  for (const c of Object.values(V.cats)) for (const [g, tag] of Object.entries(c.assign || {})) vj.set(+g.slice(1), tag === '10' ? 'b' : tag);
  const rows = fs.readFileSync(OUT, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l));
  const seen = new Set(), by = {};
  for (const r of rows) {
    if (seen.has(r.key)) continue; seen.add(r.key);
    const b = by[r.map] || (by[r.map] = { n: 0, a: 0, b: 0, q: 0, x: 0, inV: 0, agree: 0, disagree: [], qInV: 0, top: 0, ours: 0 });
    b.n++; b[r.layout === 'a' ? 'a' : r.layout === 'b' ? 'b' : r.layout === 'x' ? 'x' : 'q']++; b[r.src === 'top' ? 'top' : 'ours']++;
    if (vj.has(r.gameId)) {
      b.inV++;
      if (r.layout === '?') b.qInV++;
      else if (r.layout === vj.get(r.gameId)) b.agree++; else b.disagree.push(`${r.key} ours=${r.layout} variants=${vj.get(r.gameId)}`);
    }
  }
  console.log('| 지도 | 판 (상위끼리 / 우리) | a | b | 판정 불가 | 모순 | variants.json에도 있는 판 | 일치 | 불일치 | 우리 쪽 판정 불가 |');
  console.log('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
  for (const [m, b] of Object.entries(by).sort()) console.log(`| ${m} | ${b.n} (${b.top} / ${b.ours}) | ${b.a} | ${b.b} | ${b.q} | ${b.x} | ${b.inV} | ${b.agree} | ${b.disagree.length} | ${b.qInV} |`);
  for (const b of Object.values(by)) for (const d of b.disagree.slice(0, 10)) console.log('  disagree:', d);
} else {
  console.error('usage: layout.js scan [--jobs 3] [--src top,online] [--maps two|all] | check'); process.exit(2);
}
