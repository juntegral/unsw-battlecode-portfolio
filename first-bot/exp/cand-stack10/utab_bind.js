#!/usr/bin/env node
// cand-stack10 utab: does csplit's unit target bind, and would the layout table bind? For every game of the pools, our living dragons at
// the first turn of each round r1-249 (csplit's window) against the area target (clamp(W x H / 45, 8, 40), stack9) and the table target
// (top winners' r50 median before r50, r100 median from r50; research/observations/economy-principles.md 7, 14). A target binds in a
// round when our units are at or above it (csplit cannot fire then). Also csplit firings by label (target and " tab").
// usage: node exp/cand-stack10/utab_bind.js <pool>[+<pool>] ... [--jobs 3]     (pool = online set name or local eval folder)
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const TAB = { 'Autarky/a': [17, 23], 'Default/a': [11, 19], 'Devil/a': [16, 30], 'Devil/b': [12, 24], 'Portals/a': [14, 26],
  'Prisoners Dilemma/a': [9, 13], 'Prisoners Dilemma/b': [9, 15], 'Queen Of Spades/a': [7, 13], 'Queen Of Spades/b': [7, 12],
  'Schooltime/a': [13, 44], 'Schooltime/b': [8, 16], 'Slithery Fight/a': [47, 62], 'Slithery Fight/b': [43, 55], 'Trauma/a': [7, 16], 'Trophy/a': [15, 31] };
const MAPNAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma',
  queen_of_spades: 'Queen Of Spades', schooltime: 'Schooltime', slithery_fight: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const LAYOUT_FILES = { 'Devil': ['devil', 'devil_b'], 'Queen Of Spades': ['queen_of_spades', 'queen_of_spades_b'], 'Schooltime': ['schooltime', 'schooltime_b'],
  'Slithery Fight': ['slithery_fight', 'slithery_fight_b'] };
const tables = new Map();
function spawnTable(file) { // tools/mech_check.js spawnTable
  if (!tables.has(file)) { const L = fs.readFileSync(file, 'utf8').split('\n'), m = /^MAP (\d+) (\d+)/.exec(L[0]), W = +m[1], on = new Uint8Array(W * +m[2]);
    for (const l of L) if (l.startsWith('TILE ')) { const [x, y, , mx] = l.trim().split(/\s+/).slice(1).map(Number); on[y * W + x] = mx > 0 ? 1 : 0; } tables.set(file, on); }
  return tables.get(file);
}
function layoutOf(R, map, given) { // tools/mech_check.js layoutTruth (online: natural spawns on tiles that never spawn in the other layout)
  if (given) return given;
  if (map === 'Prisoners Dilemma') return R.match.map.initialDragons.length === 10 ? 'b' : 'a';
  const f = LAYOUT_FILES[map]; if (!f) return 'a';
  const M = R.match.map, a = spawnTable(path.join(ROOT, 'maps', 'online-20260927', f[0] + '.map')), b = spawnTable(path.join(ROOT, 'maps', 'variants', f[1] + '.map'));
  if (a.length !== M.width * M.height) return '?';
  let evA = 0, evB = 0, rs = false;
  for (const e of R.events) { if (e.type === 'roundStart') rs = true; else if (e.type === 'turnStart') rs = false;
    else if (rs && e.type === 'tileChange' && e.hasPearl) { const k = e.tile.y * M.width + e.tile.x; if (a[k] && !b[k]) evA++; else if (b[k] && !a[k]) evB++; } }
  return evA && !evB ? 'a' : evB && !evA ? 'b' : evA && evB ? 'x' : '?';
}
function tasksOf(pool) {
  const out = [];
  for (const part of pool.split('+')) {
    const abs = path.resolve(ROOT, part);
    if (fs.existsSync(path.join(abs, 'rows.jsonl'))) {
      for (const l of fs.readFileSync(path.join(abs, 'rows.jsonl'), 'utf8').split('\n')) { if (!l.trim()) continue; const row = JSON.parse(l), [opp, map, side, seed] = row.key.split(':');
        const f = path.join(abs, 'games', `${opp}_${map}_${side}_${seed}`, 'game.replay'); if (!fs.existsSync(f)) continue;
        out.push({ pool, file: f, map: MAPNAME[map.replace(/_(b|10)$/, '')] || map, us: side, layout: /_(b|10)$/.test(map) ? 'b' : 'a' }); }
    } else {
      const dir = path.join(ROOT, 'data', 'online', part), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
      for (const g of idx.games || idx) { if (g.ourWin === null || g.ourWin === undefined) continue; const f = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
        out.push({ pool, file: f, map: g.mapName, us: String(g.ourSide).toUpperCase(), layout: null }); }
    }
  }
  return out;
}
function one(task) {
  const tf = require(path.join(ROOT, 'tools', 'top_features.js')), ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const R = tf.makeLoader(tf.viewerSource())(task.file), lay = layoutOf(R, task.map, task.layout);
  const u = new Array(250).fill(null); let last = -1; const cs = [];
  const info = { map: task.map }; if (task.map === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
  ML.perGame(R, info, {
    turn(d, r, c) { if (r !== last) { last = r; if (r < 250) { let n = 0; for (const o of c.drag.values()) if (o.team === task.us) n++; u[r] = n; } } },
    indicator(e, r, c) { const d = c.drag.get(e.id); if (!d || d.team !== task.us || r >= 250) return; const m = /^csplit\d+ u(\d+) L\d+ t(\d+)((?: \S+)*)/.exec(e.text || ''); if (m) cs.push([r, +m[1], +m[2], / tab(?:\s|$)/.test(e.text) ? 1 : 0]); },
  });
  return { pool: task.pool, map: task.map, lay, W: R.match.map.width, H: R.match.map.height, u, cs };
}
async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') { process.on('message', t => { try { process.send({ ok: 1, res: one(t) }); } catch (err) { process.send({ ok: 0, err: String(err).slice(0, 200), file: t.file }); } }); return; }
  const ji = argv.indexOf('--jobs'), jobs = ji >= 0 ? +argv[ji + 1] : 3, pools = argv.filter((a, i) => !a.startsWith('--') && argv[i - 1] !== '--jobs');
  for (const pool of pools) {
    const q = tasksOf(pool), res = [];
    await Promise.all(Array.from({ length: Math.min(jobs, q.length) }, () => new Promise(done => {
      const w = cp.fork(__filename, ['--worker']); const next = () => { const t = q.shift(); if (!t) { w.kill(); done(); return; } w.send(t); };
      w.on('message', m => { if (m.ok) res.push(m.res); else console.error('error', m.file, m.err); next(); }); next(); })));
    const by = new Map(); for (const g of res) { const k = g.map + '/' + g.lay; if (!by.has(k)) by.set(k, []); by.get(k).push(g); }
    console.log(`\n## ${pool} (${res.length} games): units at each round's first turn r1-249 against the targets (binds = units >= target)`);
    console.log('| layout | games | area target | table r<50 · r50+ | max units r1-249 (mean) | games reaching area target · table target | rounds bound by area · by table | csplit firings (games) · with tab |');
    console.log('|---|---:|---:|---|---:|---|---|---|');
    for (const [k, G] of [...by.entries()].sort()) {
      const A = Math.min(40, Math.max(8, Math.floor(G[0].W * G[0].H / 45))), T = TAB[k];
      let reachA = 0, reachT = 0, rA = 0, rT = 0, rN = 0, mx = 0, csN = 0, csTab = 0;
      for (const g of G) { let ga = 0, gt = 0, m = 0;
        for (let r = 1; r < 250; r++) { const v = g.u[r]; if (v === null) continue; rN++; if (v > m) m = v; if (v >= A) { rA++; ga = 1; } if (T && v >= (r < 50 ? T[0] : T[1])) { rT++; gt = 1; } }
        reachA += ga; reachT += gt; mx += m; csN += g.cs.length; csTab += g.cs.filter(c => c[3]).length; }
      const pc = (a, b) => b ? Math.round(100 * a / b) + '%' : '–';
      console.log(`| ${k} | ${G.length} | ${A} | ${T ? T[0] + ' · ' + T[1] : '–'} | ${(mx / G.length).toFixed(1)} | ${pc(reachA, G.length)} · ${T ? pc(reachT, G.length) : '–'} | ${pc(rA, rN)} · ${T ? pc(rT, rN) : '–'} | ${csN} (${(csN / G.length).toFixed(1)}) · ${csTab} |`);
    }
  }
}
main().catch(e => { console.error(e); process.exit(1); });
