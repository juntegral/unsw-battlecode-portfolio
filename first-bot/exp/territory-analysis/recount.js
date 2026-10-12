#!/usr/bin/env node
// recount.js — independent recount of the key numbers of top-territory.md (rigour check). Replays only.
// It shares no code with extract.js or tools/mass_ledger.js except the replay parser (tools/top_features.js) and the
// map files. Its own rules (rules/kelp-and-portals.md, rules/execution-order.md, rules/pearls.md):
//   geometry: edges as lines. Vertical edge V(xe, y) lies between tiles (xe-1, y) and (xe, y); horizontal H(x, ye)
//     between (x, ye-1) and (x, ye); indices wrap. Kelp from initialHEdges / initialVEdges (value 1). A portal pair joins
//     two edge lines of the same orientation; crossing one moving in direction d comes out of the other still moving in d.
//   territory: breadth-first distance from each team's starting segments over that geometry; the nearer team owns it.
//   natural spawn: a pearl that appears after roundStart and before that round's first turnStart. Anything else that
//     appears is a death drop. Eat: a pearl that disappears during a turn goes to the acting dragon's team.
//   heads: initial dragons, then dragonUpdate (head), dragonSplit (child head), dragonDeath (removed).
// Per team it counts: own-territory natural spawns after round 0 and who ate them; heads inside the enemy territory at
// each roundStart (mean over rounds with the team alive); units and capacity-weighted own-territory Voronoi share at r100.
// usage (repository root):
//   node exp/territory-analysis/recount.js run top --keys <file> [--jobs 4]   |   run online <set> [...]
//   node exp/territory-analysis/recount.js compare [--top top-all]    (against exp/territory-analysis/cache)
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), cp = require('child_process'), readline = require('readline');
const ROOT = path.resolve(__dirname, '..', '..');
const TOP = path.join(ROOT, 'data', 'top'), ONLINE = path.join(ROOT, 'data', 'online'), CACHE = path.join(__dirname, 'cache');
const MAPFILE = { 'Autarky': 'autarky', 'Default': 'default', 'Devil': 'devil', 'Portals': 'portals', 'Prisoners Dilemma': 'prisoners_dilemma',
  'Queen Of Spades': 'queen_of_spades', 'Schooltime': 'schooltime', 'Slithery Fight': 'slithery_fight', 'Trauma': 'trauma', 'Trophy': 'trophy' };
const BFILE = { 'Devil': 'devil_b', 'Queen Of Spades': 'queen_of_spades_b', 'Schooltime': 'schooltime_b', 'Slithery Fight': 'slithery_fight_b' };

function readGaps(file) {
  const L = fs.readFileSync(file, 'utf8').split('\n'); const m = /^MAP (\d+) (\d+)/.exec(L[0]); const w = +m[1], h = +m[2];
  const g = new Float64Array(w * h);
  for (const l of L) if (l.startsWith('TILE ')) { const p = l.trim().split(/\s+/).map(Number); if (p[4] > 0) g[p[2] * w + p[1]] = 2 / (p[3] + p[4]); }
  return { w, h, g };
}

function recount(R, info) {
  const M = R.match.map, W = M.width, H = M.height, N = W * H;
  const md = (a, n) => ((a % n) + n) % n;
  // edge lines: kelp and portals
  const kelpV = (xe, y) => { xe = md(xe, W); y = md(y, H); return M.initialVEdges[y * (W + 1) + xe] === 1 || (xe === 0 && M.initialVEdges[y * (W + 1) + W] === 1); };
  const kelpH = (x, ye) => { x = md(x, W); ye = md(ye, H); return M.initialHEdges[ye * W + x] === 1 || (ye === 0 && M.initialHEdges[H * W + x] === 1); };
  const line = e => e.side === 'E' ? ['V', md(e.x + 1, W), e.y] : e.side === 'W' ? ['V', md(e.x, W), e.y] : e.side === 'N' ? ['H', e.x, md(e.y, H)] : ['H', e.x, md(e.y + 1, H)];
  const portal = new Map();
  for (const pr of M.portals || []) { if (pr.length !== 2) continue; const a = line(pr[0]), b = line(pr[1]); portal.set(a.join(','), b); portal.set(b.join(','), a); }
  function step(x, y, d) {
    let e;
    if (d === 0) e = ['H', x, md(y, H)]; else if (d === 2) e = ['H', x, md(y + 1, H)]; else if (d === 1) e = ['V', md(x + 1, W), y]; else e = ['V', md(x, W), y];
    const p = portal.get(e.join(','));
    if (p) { // come out of the partner line moving the same way
      if (d === 0) return [p[1], md(p[2] - 1, H)]; if (d === 2) return [p[1], p[2]]; if (d === 1) return [p[1], p[2]]; return [md(p[1] - 1, W), p[2]];
    }
    if (e[0] === 'H' ? kelpH(e[1], e[2]) : kelpV(e[1], e[2])) return null;
    return d === 0 ? [x, md(y - 1, H)] : d === 2 ? [x, md(y + 1, H)] : d === 1 ? [md(x + 1, W), y] : [md(x - 1, W), y];
  }
  const adj = []; for (let k = 0; k < N; k++) { const x = k % W, y = Math.floor(k / W), a = []; for (let d = 0; d < 4; d++) { const s = step(x, y, d); if (s) a.push(s[1] * W + s[0]); } adj.push(a); }
  const bfs = srcs => { const dist = new Int32Array(N).fill(-1), q = []; for (const s of srcs) if (dist[s] < 0) { dist[s] = 0; q.push(s); } for (let i = 0; i < q.length; i++) for (const u of adj[q[i]]) if (dist[u] < 0) { dist[u] = dist[q[i]] + 1; q.push(u); } return dist; };
  const startA = [], startB = [];
  for (const d of M.initialDragons) for (const s of d.body) (d.team === 'A' ? startA : startB).push(s.y * W + s.x);
  const dA = bfs(startA), dB = bfs(startB);
  const owner = new Int8Array(N); // 1 A, 2 B, 0 neutral
  for (let k = 0; k < N; k++) { const a = dA[k] < 0 ? 1e9 : dA[k], b = dB[k] < 0 ? 1e9 : dB[k]; owner[k] = a < b ? 1 : b < a ? 2 : 0; }
  // variant for the capacity weights: the same decision data (variants.json, else spawns) is not re-derived here; the
  // caller passes the tag it trusts (info.variant) and the recount checks the Voronoi share against that file
  const vf = info.map === 'Prisoners Dilemma' ? (info.variant === '10' ? 'variants/prisoners_dilemma_10' : 'online-20260927/prisoners_dilemma') : info.variant === 'b' && BFILE[info.map] ? 'variants/' + BFILE[info.map] : 'online-20260927/' + MAPFILE[info.map];
  const gp = readGaps(path.join(ROOT, 'maps', vf + '.map'));
  const cap = gp.w === W && gp.h === H ? gp.g : new Float64Array(N);
  // replay
  const team = new Map(), head = new Map();
  for (const d of M.initialDragons) { team.set(d.id, d.team); head.set(d.id, d.body[0].y * W + d.body[0].x); }
  const pearl = new Map(); // tile -> 'n' natural (spawned after round 0), 'i' initial, 'd' drop
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearl.set(i, 'i');
  const T = { A: { sp: 0, own: 0, en: 0, raidSum: 0, rounds: 0, u100: -1, vor100: -1 }, B: { sp: 0, own: 0, en: 0, raidSum: 0, rounds: 0, u100: -1, vor100: -1 } };
  let round = -1, inSpawn = false, actor = -1;
  const roundStartCount = () => {
    for (const tm of ['A', 'B']) {
      let n = 0, inE = 0; const en = tm === 'A' ? 2 : 1;
      for (const [id, t] of team) if (t === tm && head.has(id)) { n++; if (owner[head.get(id)] === en) inE++; }
      if (n > 0) { T[tm].raidSum += inE; T[tm].rounds++; }
    }
    if (round === 100) {
      const hs = { A: [], B: [] }; for (const [id, t] of team) if (head.has(id)) hs[t].push(head.get(id));
      const da = bfs(hs.A), db = bfs(hs.B);
      for (const tm of ['A', 'B']) {
        const mine = tm === 'A' ? da : db, theirs = tm === 'A' ? db : da, own = tm === 'A' ? 1 : 2;
        let c = 0, v = 0;
        for (let k = 0; k < N; k++) { if (owner[k] !== own || !(cap[k] > 0)) continue; c += cap[k]; const a = mine[k] < 0 ? 1e9 : mine[k], b = theirs[k] < 0 ? 1e9 : theirs[k]; v += cap[k] * (a < b ? 1 : a === b ? 0.5 : 0); }
        T[tm].u100 = hs[tm].length; T[tm].vor100 = c ? v / c : -1;
      }
    }
  };
  for (const e of R.events) {
    switch (e.type) {
      case 'roundStart': round = e.round; inSpawn = true; roundStartCount(); break;
      case 'turnStart': inSpawn = false; actor = e.id; break;
      case 'tileChange': {
        const k = e.tile.y * W + e.tile.x;
        if (e.hasPearl) { pearl.set(k, inSpawn && round >= 0 ? 'n' : 'd'); if (inSpawn && round >= 0 && owner[k]) T[owner[k] === 1 ? 'A' : 'B'].sp++; }
        else {
          const o = pearl.get(k); pearl.delete(k);
          if (o === 'n' && owner[k]) { const own = owner[k] === 1 ? 'A' : 'B', t = team.get(actor); if (t === own) T[own].own++; else if (t) T[own].en++; }
        }
        break;
      }
      case 'dragonUpdate': if (round >= 0 && head.has(e.id)) head.set(e.id, e.head.y * W + e.head.x); break;
      case 'dragonSplit': team.set(e.childId, e.team); head.set(e.childId, e.childBody[0].y * W + e.childBody[0].x); break;
      case 'dragonDeath': head.delete(e.id); break;
    }
  }
  return { key: info.key, rounds: round + 1, owner: [0, 1, 2].map(v => owner.reduce((s, x) => s + (x === v ? 1 : 0), 0)), A: T.A, B: T.B };
}

// ---- tasks
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];
let VA = null; const vassign = () => { if (!VA) { VA = {}; try { for (const c of Object.values(JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'pearl_layout', 'variants.json'), 'utf8')).cats)) Object.assign(VA, c.assign || {}); } catch { } } return VA; };
async function variantsFromCache() { // the variant tag the main extraction used, per game key (to check the Voronoi share on the same file)
  const out = new Map();
  for (const f of fs.readdirSync(CACHE).filter(f => /^(top-all|online-.*)\.jsonl\.gz$/.test(f))) {
    const rl = readline.createInterface({ input: fs.createReadStream(path.join(CACHE, f)).pipe(zlib.createGunzip()), crlfDelay: Infinity });
    for await (const l of rl) { const m = /^\{"key":"([^"]+)"/.exec(l); if (!m) continue; const v = /"variant":\{"tag":"([^"]+)"/.exec(l); if (v) out.set(m[1], v[1]); }
  }
  return out;
}
function topTasks(keysArg, vt) {
  const seen = new Set(), rows = new Map();
  for (const r of readJsonl(path.join(TOP, 'index.jsonl'))) { const k = r.battleId + ':' + r.gameId; if (seen.has(k)) continue; seen.add(k); rows.set(k, r); }
  return fs.readFileSync(path.resolve(ROOT, keysArg), 'utf8').split('\n').map(s => s.trim()).filter(Boolean).map(k => rows.get(k)).filter(Boolean)
    .map(r => ({ key: r.battleId + ':' + r.gameId, file: path.join(TOP, String(r.battleId), r.gameId + '.replay.gz'), info: { key: r.battleId + ':' + r.gameId, map: r.map, variant: vt.get(r.battleId + ':' + r.gameId) || 'a' } }))
    .filter(t => fs.existsSync(t.file));
}
function onlineTasks(set, vt) {
  const dir = path.join(ONLINE, set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  return (idx.games || idx).map(g => ({ key: set + ':' + g.gameId, file: path.join(dir, 'M' + g.gameId + '.replay'), info: { key: set + ':' + g.gameId, map: g.mapName, variant: vt.get(set + ':' + g.gameId) || 'a' } })).filter(t => fs.existsSync(t.file));
}
function workerMain() {
  const tf = require(path.join(ROOT, 'tools', 'top_features.js')); const load = tf.makeLoader(tf.viewerSource());
  process.on('message', t => { try { process.send({ line: JSON.stringify(recount(load(t.file), t.info)) }); } catch (err) { process.send({ error: t.key + ' ' + String(err && err.stack || err).split('\n').slice(0, 3).join(' | ') }); } });
}
async function run(tasks, out, jobs) {
  const done = new Set(); if (fs.existsSync(out)) { try { for (const l of zlib.gunzipSync(fs.readFileSync(out)).toString().split('\n')) { const m = /^\{"key":"([^"]+)"/.exec(l); if (m) done.add(m[1]); } } catch { } }
  const todo = tasks.filter(t => !done.has(t.key)); console.log(`${path.relative(ROOT, out)}: ${tasks.length}, to do ${todo.length}`);
  if (!todo.length) return;
  const fd = fs.openSync(out, 'a'), t0 = Date.now(); let n = 0;
  await new Promise((resolve, reject) => {
    const q = todo.slice(); let live = Math.min(jobs, q.length);
    for (let i = 0, k = live; i < k; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced', execArgv: ['--max-old-space-size=2048'] }); let fin = false;
      const next = () => { const t = q.shift(); if (!t) { fin = true; w.kill(); if (--live === 0) resolve(); return; } w.send(t); };
      w.on('message', m => { if (m.error) console.error('error', m.error); else fs.writeSync(fd, zlib.gzipSync(m.line + '\n')); n++; if (n % 500 === 0) console.log(`  ${n}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`); next(); });
      w.on('error', reject); w.on('exit', c => { if (!fin) reject(Error('worker exit ' + c)); }); next();
    }
  });
  fs.closeSync(fd); console.log(`done ${n} in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
async function compare(topName) {
  // main extraction per team-game: ownSp, ownEat, enEat (r >= 0 natural, own territory), raiders per round, units and Voronoi at r100
  const main = new Map();
  const add = async f => {
    if (!fs.existsSync(f)) return;
    const rl = readline.createInterface({ input: fs.createReadStream(f).pipe(zlib.createGunzip()), crlfDelay: Infinity });
    for await (const l of rl) {
      if (!l.trim()) continue; const g = JSON.parse(l);
      for (const ti of [0, 1]) {
        const own = ti + 1; let sp = 0, o = 0, en = 0;
        for (const p of g.P) { if (p[0] < 0 || p[2] !== own) continue; sp++; if (p[13] === own) o++; else if (p[13] === 3 - own) en++; }
        const L = g.LOC[ti], c = g.C[ti].find(c => c[0] === 100);
        main.set(g.key + ':' + ti, { sp, own: o, en, raid: L.en.reduce((a, b) => a + b, 0) / Math.max(1, L.rounds.reduce((a, b) => a + b, 0)), u100: c ? c[1] : -1, vor100: c ? c[5] / g.capT[own] : -1 });
      }
    }
  };
  await add(path.join(CACHE, topName + '.jsonl.gz'));
  for (const f of fs.readdirSync(CACHE).filter(f => /^online-.*\.jsonl\.gz$/.test(f))) await add(path.join(CACHE, f));
  const st = { games: 0, teamGames: 0, missing: 0, spEq: 0, ownEq: 0, enEq: 0, raidEq: 0, u100Eq: 0, vorEq: 0, vorN: 0, spDiff: 0, ownDiff: 0, enDiff: 0, maxRaidDiff: 0, maxVorDiff: 0, sums: { rsp: 0, ren: 0, msp: 0, men: 0 } };
  const bad = [];
  for (const f of fs.readdirSync(CACHE).filter(f => /^recount-.*\.jsonl\.gz$/.test(f))) {
    const rl = readline.createInterface({ input: fs.createReadStream(path.join(CACHE, f)).pipe(zlib.createGunzip()), crlfDelay: Infinity });
    for await (const l of rl) {
      if (!l.trim()) continue; const r = JSON.parse(l); st.games++;
      for (const [ti, tm] of [[0, 'A'], [1, 'B']]) {
        const m = main.get(r.key + ':' + ti); if (!m) { st.missing++; continue; }
        const x = r[tm]; st.teamGames++;
        const raid = x.raidSum / Math.max(1, x.rounds);
        if (x.sp === m.sp) st.spEq++; else st.spDiff += Math.abs(x.sp - m.sp);
        if (x.own === m.own) st.ownEq++; else st.ownDiff += Math.abs(x.own - m.own);
        if (x.en === m.en) st.enEq++; else st.enDiff += Math.abs(x.en - m.en);
        if (Math.abs(raid - m.raid) < 1e-9) st.raidEq++; st.maxRaidDiff = Math.max(st.maxRaidDiff, Math.abs(raid - m.raid));
        if (x.u100 === m.u100) st.u100Eq++;
        if (x.vor100 >= 0 && m.vor100 >= 0) { st.vorN++; const dv = Math.abs(x.vor100 - m.vor100); if (dv < 1e-6) st.vorEq++; st.maxVorDiff = Math.max(st.maxVorDiff, dv); }
        st.sums.rsp += x.sp; st.sums.ren += x.en; st.sums.msp += m.sp; st.sums.men += m.en;
        if ((x.sp !== m.sp || x.en !== m.en || x.own !== m.own) && bad.length < 10) bad.push({ key: r.key, tm, recount: [x.sp, x.own, x.en], main: [m.sp, m.own, m.en] });
      }
    }
  }
  console.log(JSON.stringify(st, null, 1));
  if (bad.length) console.log('first differences:', JSON.stringify(bad));
}
async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const jobs = Math.max(1, Math.min(4, +opt('jobs', 4)));
  if (argv[0] === 'run') {
    const vt = await variantsFromCache();
    if (argv[1] === 'top') return run(topTasks(opt('keys'), vt), path.join(CACHE, 'recount-top.jsonl.gz'), jobs);
    for (let i = 2; i < argv.length; i++) { if (argv[i].startsWith('--')) { i++; continue; } await run(onlineTasks(argv[i], vt), path.join(CACHE, 'recount-online-' + argv[i] + '.jsonl.gz'), jobs); }
    return;
  }
  if (argv[0] === 'compare') return compare(opt('top', 'top-all'));
  console.error('usage: see header'); process.exit(2);
}
module.exports = { recount };
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
