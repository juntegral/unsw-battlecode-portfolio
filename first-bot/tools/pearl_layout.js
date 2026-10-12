#!/usr/bin/env node
// Pearl spawn layout of every map, measured from replays (server replays hide the TILE gaps: pearlRespawn is all 0).
// Reads replays only; runs no games and uses no network.
//
// usage (repository root):
//   node tools/pearl_layout.js extract [--jobs 4] [--force] [--src top,online,old] [--local <exp dir>...] [--limit N]
//       Parses replays into data/pearl_layout/games.jsonl.gz (one gzip member per game, appended; games already there
//       are skipped). --src top: data/top (index.jsonl). online: every data/online/<set>/index.json. old: data/online/g1,
//       g2 (2026-09-27; before 11:00Z those replays still carry the true gaps). --local <dir>: local replays
//       <dir>/games/*/game.replay with their true gaps and countdown records, for validation (local.jsonl.gz).
//   node tools/pearl_layout.js report [--map <name>] [--variant a|b|10|all] [--ref <map file>] [--local] [--json <out>]
//       Per map (Prisoners Dilemma split by start dragons 6 / 10) and gap class of the reference file: spawns per tile and
//       game, first-spawn rounds, games without a spawn, single gaps (count, range, outside the reference), fitted
//       min-max [95%], LR against the reference, Kaplan-Meier mean vs uniform, eat -> next spawn; then the mirror groups
//       that disagree. Server games after the 2026-09-27 11:00Z change only. --variant: only the games of that variant
//       (data/pearl_layout/variants.json), checked against the online file (a) or maps/variants/<file>_<tag>.map.
//       --json: per-group numbers. --local: the local validation replays.
//   node tools/pearl_layout.js variants [--map <name>] [--k 3] [--bin 3] [--verbose]
//       Pearl variants of each map, their shares by source and time; writes data/pearl_layout/variants.json.
//   node tools/pearl_layout.js build [--map <name>] [--dry] [--force]
//       Writes maps/variants/<file>_<tag>.map for each variant that differs from the online file. An existing file whose
//       values lie inside the variant's 95% intervals is kept unless --force.
//   node tools/pearl_layout.js compare <replay...>
//       Spawn pattern of local replays played on a variant file against the server games of that variant.
//   node tools/pearl_layout.js selftest [local|synth|window]
//       Checks behind the method: the observation model on local replays with countdown records, the estimator on
//       synthetic schedules, and early-window against full fits on the server games.
//
// Observable (rules/pearls.md, rules/execution-order.md): a tile's countdown ticks at the start of every round; at 0 it
// attempts a spawn and redraws U[minGap, maxGap] whether or not the attempt succeeded. The attempt succeeds only when the
// tile is free (no pearl, no dragon segment). Mirror tiles share one countdown. So:
//   - a natural spawn (tileChange before the first turn of a round) marks an attempt of the tile's mirror group;
//   - an attempt on a round where every tile of the group is occupied leaves no trace;
//   - the first attempt is at round g0-1 (the initial countdown g0 ~ U[min,max] is ticked on round 0), i.e. an attempt
//     at virtual round -1.
// Hence per group we keep the observed attempt rounds and the rounds where no tile of the group was free ("blocked").
// A segment starts at an observed attempt u. For a candidate minGap m, rounds with age (r-u) < m cannot hold an attempt,
// blocked or not. The segment ends with an event (next spawn at age t, a single gap draw) or is censored at the first
// blocked round with age >= m (gap >= that age), or at the end of the game.
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), vm = require('vm');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

const ROOT = path.resolve(__dirname, '..');
const OUTDIR = path.join(ROOT, 'data', 'pearl_layout');
const CACHE = { server: path.join(OUTDIR, 'games.jsonl.gz'), local: path.join(OUTDIR, 'local.jsonl.gz') };

// ---------------------------------------------------------------------------------------------------------------------
// Map geometry helpers
function mirrorOf(sym, W, H) {
  // SYMMETRY xy: point reflection (x,y) -> (W-1-x, H-1-y). y: (W-1-x, y). x: (x, H-1-y). Checked by the half-spawn count.
  if (sym === 'xy') return i => { const x = i % W, y = (i - x) / W; return (H - 1 - y) * W + (W - 1 - x); };
  if (sym === 'y') return i => { const x = i % W, y = (i - x) / W; return y * W + (W - 1 - x); };
  if (sym === 'x') return i => { const x = i % W, y = (i - x) / W; return (H - 1 - y) * W + x; };
  return i => i;
}
function parseMapText(text) {
  const out = { W: 0, H: 0, sym: '', name: '', tiles: new Map(), lines: text.split('\n'), dragons: [] };
  for (const l of out.lines) {
    const p = l.trim().split(/\s+/);
    if (p[0] === 'MAP') { out.W = +p[1]; out.H = +p[2]; }
    else if (p[0] === 'SYMMETRY') out.sym = p[1];
    else if (p[0] === 'MAP_NAME') out.name = l.trim().slice(9);
    else if (p[0] === 'TILE') out.tiles.set(+p[2] * out.W + +p[1], [+p[3], +p[4]]);
    else if (p[0] === 'DRAGON') out.dragons.push(p.slice(1).map(Number));
  }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------------
// Extraction of one parsed replay
function extract(R) {
  const M = R.match.map, W = M.width, H = M.height, N = W * H;
  const sym = M.symmetry || '';
  const mir = mirrorOf(sym, W, H);
  const canon = new Int32Array(N);
  for (let i = 0; i < N; i++) canon[i] = Math.min(i, mir(i));
  const occ = new Int16Array(N), pearl = new Uint8Array(N);
  if (M.initialTiles) for (let i = 0; i < N; i++) if (M.initialTiles[i] === 2) pearl[i] = 1;
  const bodies = new Map();
  const tidx = p => p.y * W + p.x;
  const put = (id, body) => { bodies.set(id, body); for (const t of body) occ[t]++; };
  const clear = id => { const b = bodies.get(id); if (b) for (const t of b) occ[t]--; bodies.delete(id); };
  for (const d of M.initialDragons) put(d.id, d.body.map(tidx));
  const team = new Map(M.initialDragons.map(d => [d.id, d.team]));
  const chk = { spawnBlocked: 0, eatNoPearl: 0, dropOther: 0, halfSpawn: 0, updateGap: 0 };
  const spawns = [], eats = [], drops = [];
  // blocked runs per group: at the start of round r (before the tick) no tile of the group is free
  const groups = [];
  const gOf = new Int32Array(N).fill(-1);
  for (let i = 0; i < N; i++) if (canon[i] === i) { gOf[i] = groups.length; groups.push({ c: i, tiles: [i] }); }
  for (let i = 0; i < N; i++) if (canon[i] !== i) { const g = gOf[canon[i]]; gOf[i] = g; groups[g].tiles.push(i); }
  const runStart = new Int32Array(groups.length).fill(-1);
  const runs = groups.map(() => []);
  let round = -1, preTurn = false, afterDeath = false, started = false;
  const freeTile = t => occ[t] === 0 && pearl[t] === 0;
  const onRoundStart = r => {
    for (let g = 0; g < groups.length; g++) {
      const ts = groups[g].tiles;
      let free = false;
      for (const t of ts) if (freeTile(t)) { free = true; break; }
      if (!free) { if (runStart[g] < 0) runStart[g] = r; }
      else if (runStart[g] >= 0) { runs[g].push(runStart[g], r - 1); runStart[g] = -1; }
    }
  };
  let roundSpawns = [];
  const flushSpawns = () => {
    // half spawn: a group attempt (some tile spawned) while another tile of the group was free and did not spawn
    if (!roundSpawns.length) return;
    const byG = new Map();
    for (const t of roundSpawns) { const g = gOf[t]; if (!byG.has(g)) byG.set(g, new Set()); byG.get(g).add(t); }
    for (const [g, set] of byG) for (const t of groups[g].tiles) if (!set.has(t) && freeAtStart.has(t)) chk.halfSpawn++;
    roundSpawns = [];
  };
  let freeAtStart = new Set();
  const att = {}; // local replays: per group (canonical tile) [initial countdown, attempt rounds...] from pearlCountdown
  for (const e of R.events) {
    switch (e.type) {
      case 'pearlCountdown': {
        const t = tidx(e.tile);
        if (canon[t] !== t) break;
        if (!started) att[t] = [e.countdown];
        else if (preTurn) (att[t] || (att[t] = [null])).push(round);
        break;
      }
      case 'roundStart': {
        flushSpawns();
        round = e.round; started = true; preTurn = true; afterDeath = false;
        onRoundStart(round);
        // tiles free at round start that belong to a group (kept only for the half-spawn check of this round)
        freeAtStart = new Set();
        break;
      }
      case 'turnStart': preTurn = false; afterDeath = false; flushSpawns(); break;
      case 'tileChange': {
        const t = tidx(e.tile);
        if (e.hasPearl) {
          if (preTurn && started) {
            if (!freeTile(t)) chk.spawnBlocked++;
            // record the group's free tiles lazily (state at round start = current state before this spawn is applied)
            for (const u of groups[gOf[t]].tiles) if (u !== t && freeTile(u)) freeAtStart.add(u);
            spawns.push(round, t); roundSpawns.push(t);
          } else if (afterDeath) drops.push(round, t);
          else chk.dropOther++;
          pearl[t] = 1;
        } else {
          if (!pearl[t]) chk.eatNoPearl++;
          pearl[t] = 0; eats.push(round, t);
        }
        break;
      }
      case 'dragonUpdate': {
        if (!started) break;
        const b = bodies.get(e.id); if (!b) { chk.updateGap++; break; }
        const h = tidx(e.head), tl = tidx(e.tail);
        if (b[0] !== h) { b.unshift(h); occ[h]++; }
        let guard = b.length;
        while (b.length > 1 && b[b.length - 1] !== tl && guard-- > 0) occ[b.pop()]--;
        if (b[b.length - 1] !== tl) chk.updateGap++;
        break;
      }
      case 'dragonSplit': {
        clear(e.parentId);
        put(e.parentId, e.parentBody.map(tidx));
        put(e.childId, e.childBody.map(tidx));
        team.set(e.childId, e.team);
        break;
      }
      case 'dragonDeath': clear(e.id); afterDeath = true; break;
      default: break;
    }
  }
  flushSpawns();
  const rounds = round + 1;
  // close runs at the end of the game (last round played)
  for (let g = 0; g < groups.length; g++) if (runStart[g] >= 0) { runs[g].push(runStart[g], rounds - 1); runStart[g] = -1; }
  // final check against the result
  const fin = { A: { n: 0, tot: 0, lon: 0 }, B: { n: 0, tot: 0, lon: 0 } };
  for (const [id, b] of bodies) { const f = fin[team.get(id)]; if (!f) continue; f.n++; f.tot += b.length; f.lon = Math.max(f.lon, b.length); }
  const res = R.result || {};
  chk.finalMismatch = ['A', 'B'].filter(tm => res['team' + tm] && (res['team' + tm].dragonCount !== fin[tm].n || res['team' + tm].totalLength !== fin[tm].tot || res['team' + tm].longestDragon !== fin[tm].lon)).length;
  // blocked runs, only for groups that were ever blocked
  const blk = {};
  for (let g = 0; g < groups.length; g++) if (runs[g].length) blk[groups[g].c] = runs[g];
  // true gaps (local replays only)
  let truth = null;
  if (M.pearlRespawn && M.pearlRespawn.some(p => p.maxRounds > 0)) {
    truth = [];
    for (let i = 0; i < N; i++) { const p = M.pearlRespawn[i]; if (p.maxRounds > 0) truth.push(i, p.minRounds, p.maxRounds); }
  }
  const dragons = M.initialDragons.map(d => d.team + d.body.map(s => s.x + '.' + s.y).join(':')).join(' ');
  return { W, H, sym, mapName: M.mapName, nd: M.initialDragons.length, dragons, rounds, spawns, eats, drops, blk, truth, att: Object.keys(att).length ? att : null, chk, endReason: res.endReason, seed: R.seed };
}

// ---------------------------------------------------------------------------------------------------------------------
// Sources
function serverSources() {
  const out = [], seen = new Set();
  const idxFile = path.join(ROOT, 'data/top/index.jsonl');
  if (fs.existsSync(idxFile)) for (const l of fs.readFileSync(idxFile, 'utf8').split('\n')) {
    if (!l.trim()) continue;
    let r; try { r = JSON.parse(l); } catch { continue; }
    const f = path.join(ROOT, 'data/top', String(r.battleId), r.gameId + '.replay.gz');
    const key = 'g' + r.gameId;
    if (seen.has(key) || !fs.existsSync(f)) continue;
    seen.add(key);
    out.push({ key, file: f, src: 'top', set: 'top', map: r.map, at: r.at, battleId: r.battleId, gameId: r.gameId, teams: [r.teamA, r.teamB] });
  }
  const odir = path.join(ROOT, 'data/online');
  for (const set of fs.existsSync(odir) ? fs.readdirSync(odir).sort() : []) {
    const idx = path.join(odir, set, 'index.json');
    if (!fs.existsSync(idx)) continue;
    let games; try { games = JSON.parse(fs.readFileSync(idx, 'utf8')).games || []; } catch { continue; }
    for (const g of games) {
      const f = path.join(odir, set, `M${g.gameId}.replay`);
      const key = 'g' + g.gameId;
      if (seen.has(key) || !fs.existsSync(f)) continue;
      seen.add(key);
      out.push({ key, file: f, src: 'online', set, map: g.mapName, at: g.completedAt || g.requestedAt, gameId: g.gameId, teams: [String(g.teamAId), String(g.teamBId)] });
    }
  }
  // older sets without index.json (2026-09-27 practice: data/online/g1, g2/<set>/game-<id>.json + M<id>.replay).
  // Games before 2026-09-27T11:00Z still carry the true gaps (pearlRespawn), later ones are hidden.
  for (const top of fs.existsSync(odir) ? fs.readdirSync(odir).sort() : []) {
    const d0 = path.join(odir, top);
    if (!/^g\d+$/.test(top) || !fs.statSync(d0).isDirectory()) continue;
    for (const set of fs.readdirSync(d0).sort()) {
      const d = path.join(d0, set);
      if (!fs.statSync(d).isDirectory()) continue;
      for (const gf of fs.readdirSync(d).filter(x => /^game-\d+\.json$/.test(x)).sort()) {
        let g; try { g = JSON.parse(fs.readFileSync(path.join(d, gf), 'utf8')); } catch { continue; }
        const f = path.join(d, `M${g.id}.replay`), key = 'g' + g.id;
        if (seen.has(key) || !fs.existsSync(f)) continue;
        seen.add(key);
        out.push({ key, file: f, src: 'old', set: top + '/' + set, map: null, at: g.completedAt, gameId: g.id, teams: [String(g.teamAId), String(g.teamBId)] });
      }
    }
  }
  return out;
}
function localSources(dirs) {
  const out = [];
  for (const d0 of dirs) {
    const d = path.resolve(ROOT, d0), gd = path.join(d, 'games');
    if (!fs.existsSync(gd)) continue;
    for (const g of fs.readdirSync(gd).sort()) {
      const f = path.join(gd, g, 'game.replay');
      if (fs.existsSync(f)) out.push({ key: path.relative(ROOT, f), file: f, src: 'local', set: path.relative(ROOT, d), map: null, at: null });
    }
  }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------------
// extract command (worker pool)
async function forEachRow(file, fn) {
  if (!fs.existsSync(file)) return;
  const rl = require('readline').createInterface({ input: fs.createReadStream(file).pipe(zlib.createGunzip()), crlfDelay: Infinity });
  for await (const l of rl) { if (!l.trim()) continue; let r; try { r = JSON.parse(l); } catch { continue; } fn(r); }
}
async function cmdExtract(args) {
  const jobs = Math.max(1, Math.min(4, +(args.jobs || 4)));
  const locals = args.local || [];
  const srcs = new Set(String(args.src || (locals.length ? '' : 'top,online,old')).split(',').filter(Boolean));
  let tasks = [];
  if (srcs.has('top') || srcs.has('online') || srcs.has('old')) tasks.push(...serverSources().filter(t => srcs.has(t.src)));
  const out = locals.length && !srcs.size ? CACHE.local : CACHE.server;
  if (locals.length) tasks.push(...localSources(locals));
  fs.mkdirSync(OUTDIR, { recursive: true });
  const have = new Set();
  if (args.force) { if (fs.existsSync(out)) fs.renameSync(out, out + '.old'); }
  else await forEachRow(out, r => have.add(r.key));
  tasks = tasks.filter(t => !have.has(t.key));
  if (args.limit) tasks = tasks.slice(0, +args.limit);
  console.error(`extract: ${tasks.length} replays to parse -> ${path.relative(ROOT, out)} (${jobs} workers)`);
  if (!tasks.length) return;
  const { viewerSource } = require('./top_features.js');
  const src = viewerSource();
  const fd = fs.openSync(out, 'a');
  let next = 0, done = 0, fail = 0;
  const t0 = Date.now();
  await new Promise(resolve => {
    let live = 0;
    const spawn = () => {
      const w = new Worker(__filename, { workerData: { src } });
      live++;
      const feed = () => { if (next < tasks.length) w.postMessage(tasks[next++]); else { w.terminate(); } };
      w.on('message', m => {
        if (m.ok) fs.writeSync(fd, zlib.gzipSync(JSON.stringify(m.row) + '\n')); else { fail++; console.error('fail', m.key, m.err); }
        done++;
        if (done % 200 === 0) console.error(`  ${done}/${tasks.length} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
        feed();
      });
      w.on('exit', () => { if (--live === 0) resolve(); });
      w.on('error', err => { console.error('worker error', err); });
      feed();
    };
    for (let i = 0; i < Math.min(jobs, tasks.length); i++) spawn();
  });
  fs.closeSync(fd);
  console.error(`extract: done ${done}, failed ${fail}, ${((Date.now() - t0) / 1000).toFixed(0)} s`);
}

// The official viewer's parser, as in tools/top_features.js makeLoader, without the sonar extras. top_features.js is not
// required inside a worker: it installs its own worker message handler when loaded off the main thread.
function makeLoader(src) {
  const cut = src.indexOf('var Af=B(');
  if (cut < 0) throw Error('unexpected replay-viewer build (parser cut point not found)');
  const code = src.slice(0, cut).replace('if(n.formatVersion>1)', 'if(n.formatVersion>2)') + 'globalThis.__pl={Df:Df,bf:bf,Of:Of};})();';
  const ctx = { TextEncoder, TextDecoder };
  vm.runInNewContext(code, ctx, { timeout: 5000 });
  const { Df, bf, Of } = ctx.__pl || {};
  if (![Df, bf, Of].every(f => typeof f === 'function')) throw Error('unexpected replay-viewer build (parser internals not found)');
  // event kinds (viewer enum): 0 roundStart, 1 turnStart, 2 pearlCountdown (local replays only), 3 tileChange,
  // 9 dragonUpdate, 10 dragonSplit, 11 dragonDeath. Actions, logs, draws and sonar are skipped.
  const KEEP = new Uint8Array(16); for (const k of [0, 1, 2, 3, 9, 10, 11]) KEEP[k] = 1;
  return file => {
    const raw = fs.readFileSync(file);
    const root = Df(file.endsWith('.gz') ? zlib.gunzipSync(raw) : raw);
    const list = root.events, n = list.length, events = [];
    for (let i = 0; i < n; i++) { const ev = list.get(i); if (KEEP[ev.which()]) events.push(bf(ev)); }
    const R = Of(root, events);
    R.formatVersion = root.formatVersion;
    return R;
  };
}
if (!isMainThread) {
  const load = makeLoader(workerData.src);
  parentPort.on('message', task => {
    try {
      const R = load(task.file);
      const x = extract(R);
      const row = { key: task.key, src: task.src, set: task.set, map: task.map || x.mapName, at: task.at, gameId: task.gameId, battleId: task.battleId, teams: task.teams, ...x };
      parentPort.postMessage({ ok: true, row });
    } catch (err) {
      parentPort.postMessage({ ok: false, key: task.key, err: String(err && err.stack || err) });
    }
  });
}

// ---------------------------------------------------------------------------------------------------------------------
// Local map files
const MAPDIR = path.join(ROOT, 'maps', 'online-20260927'), VARDIR = path.join(ROOT, 'maps', 'variants');
let mapFilesCache = null;
function mapFiles() {
  if (mapFilesCache) return mapFilesCache;
  mapFilesCache = { online: new Map(), variants: [] };
  for (const f of fs.readdirSync(MAPDIR).sort()) if (f.endsWith('.map')) {
    const m = parseMapText(fs.readFileSync(path.join(MAPDIR, f), 'utf8')); m.file = path.relative(ROOT, path.join(MAPDIR, f));
    mapFilesCache.online.set(m.name, m);
  }
  if (fs.existsSync(VARDIR)) for (const f of fs.readdirSync(VARDIR).sort()) if (f.endsWith('.map')) {
    const m = parseMapText(fs.readFileSync(path.join(VARDIR, f), 'utf8')); m.file = path.relative(ROOT, path.join(VARDIR, f));
    mapFilesCache.variants.push(m);
  }
  return mapFilesCache;
}
const catOf = r => r.map + '/' + r.nd;
// layout: Map canon -> [min, max] per mirror group (canonical tile), from a parsed map file
function layoutOf(mf) {
  const mir = mirrorOf(mf.sym, mf.W, mf.H), lay = new Map();
  for (const [t, v] of mf.tiles) { const c = Math.min(t, mir(t)); if (!lay.has(c) || t === c) lay.set(c, v); }
  return lay;
}
const tileName = (t, W) => `(${t % W},${Math.floor(t / W)})`;

// ---------------------------------------------------------------------------------------------------------------------
// Games: two streaming passes. Pass 1 finds, per category (map / start dragons), the groups that ever spawned. Pass 2
// keeps per game the observed attempt rounds (ep) and blocked runs (blk) of the relevant groups (file spawn groups and
// groups seen spawning), and per tile the spawn and eat rounds.
async function loadGames(file, filter = () => true) {
  const cats = new Map();
  await forEachRow(file, r => {
    if (!filter(r)) return;
    const k = catOf(r);
    let c = cats.get(k);
    if (!c) {
      c = { key: k, map: r.map, nd: r.nd, W: r.W, H: r.H, sym: r.sym, spawnGroups: new Set(), games: [], dragons: new Map() };
      c.mir = mirrorOf(r.sym, r.W, r.H);
      const mf = mapFiles().online.get(r.map);
      c.file = mf || null; c.fileLay = mf ? layoutOf(mf) : new Map();
      cats.set(k, c);
    }
    for (let i = 0; i < r.spawns.length; i += 2) { const t = r.spawns[i + 1]; c.spawnGroups.add(Math.min(t, c.mir(t))); }
  });
  for (const c of cats.values()) {
    c.relevant = new Set(c.spawnGroups);
    for (const [g, v] of c.fileLay) if (v[1] > 0) c.relevant.add(g);
  }
  await forEachRow(file, r => {
    if (!filter(r)) return;
    const c = cats.get(catOf(r));
    c.dragons.set(r.dragons, (c.dragons.get(r.dragons) || 0) + 1);
    c.games.push(gameFromRow(c, r));
  });
  return cats;
}
// compact game record for the relevant groups of category c
function gameFromRow(c, r) {
  const ep = new Map(), tsp = new Map(), teat = new Map();
  for (let i = 0; i < r.spawns.length; i += 2) {
    const rd = r.spawns[i], t = r.spawns[i + 1], g = Math.min(t, c.mir(t));
    let a = ep.get(g); if (!a) ep.set(g, a = []);
    if (a[a.length - 1] !== rd) a.push(rd);
    let b = tsp.get(t); if (!b) tsp.set(t, b = []); b.push(rd);
  }
  for (let i = 0; i < r.eats.length; i += 2) { const t = r.eats[i + 1]; let b = teat.get(t); if (!b) teat.set(t, b = []); b.push(r.eats[i]); }
  const blk = new Map();
  for (const g of c.relevant) if (r.blk[g]) blk.set(g, r.blk[g]);
  let truth = null;
  if (r.truth) { truth = new Map(); for (let i = 0; i < r.truth.length; i += 3) { const t = r.truth[i]; truth.set(Math.min(t, c.mir(t)), [r.truth[i + 1], r.truth[i + 2]]); } }
  return { key: r.key, src: r.src, set: r.set, at: r.at, rounds: r.rounds, dragons: r.dragons, teams: r.teams, seed: r.seed, ep, blk, tsp, teat, truth, att: r.att };
}

// ---------------------------------------------------------------------------------------------------------------------
// Segments and the censored-uniform likelihood
// A segment of group g in one game: an observed attempt at round u (u = -1 is the virtual start), the next observed attempt
// v (or null: none until the end), and the blocked rounds strictly between, as ages (round - u).
function segmentsOf(ep, blk, rounds) {
  const segs = [];
  const E = [-1, ...(ep || [])];
  let bi = 0;
  const B = blk || [];
  for (let i = 0; i < E.length; i++) {
    const u = E[i], v = i + 1 < E.length ? E[i + 1] : null, end = v === null ? rounds : v; // rounds u+1..end-1 lie between
    const runs = [];
    while (bi < B.length && B[bi + 1] <= u) bi += 2;
    for (let j = bi; j < B.length && B[j] < end; j += 2) {
      const r0 = Math.max(B[j], u + 1), r1 = Math.min(B[j + 1], end - 1);
      if (r0 <= r1) runs.push(r0 - u, r1 - u);
    }
    segs.push({ u, v, t: v === null ? null : v - u, T: end - u, runs });
  }
  return segs;
}
// Reduce a segment for candidate minGap m: { ev: t } (single gap), or { cs: c } (gap >= c).
function reduceSeg(s, m) {
  for (let j = 0; j < s.runs.length; j += 2) if (s.runs[j + 1] >= m) return { cs: Math.max(s.runs[j], m) };
  return s.t !== null ? { ev: s.t } : { cs: s.T };
}
// Histograms of events and censorings for a list of segments at m (weights optional)
function histAt(segs, m, wts) {
  const ev = new Map(), cs = new Map();
  for (let i = 0; i < segs.length; i++) {
    const w = wts ? wts[i] : 1; if (!w) continue;
    const x = reduceSeg(segs[i], m);
    if (x.ev !== undefined) ev.set(x.ev, (ev.get(x.ev) || 0) + w); else cs.set(x.cs, (cs.get(x.cs) || 0) + w);
  }
  return { ev: [...ev].sort((a, b) => a[0] - b[0]), cs: [...cs].sort((a, b) => a[0] - b[0]) };
}
function llUniform(h, m, M) {
  const { ev, cs } = h;
  if (!(M > 0)) return ev.length ? -Infinity : 0; // never spawns
  if (M === Infinity) return ev.length ? -Infinity : 0;
  const lw = Math.log(M - m + 1);
  let ll = 0;
  for (const [t, n] of ev) { if (t < m || t > M) return -Infinity; ll -= n * lw; }
  for (const [c, n] of cs) { const cc = Math.max(c, m); if (cc > M) return -Infinity; if (cc > m) ll += n * (Math.log(M - cc + 1) - lw); }
  return ll;
}
// Profile over M for fixed m. Returns the MLE and the 95% likelihood interval (drop 1.92). M = Infinity when no events.
function fitM(h, m) {
  let tmax = 0, cmax = 0, E = 0;
  for (const [t, n] of h.ev) { tmax = Math.max(tmax, t); E += n; }
  for (const [c] of h.cs) cmax = Math.max(cmax, Math.max(c, m));
  const lo = Math.max(tmax, cmax, m);
  const grid = [];
  for (let k = 0; k <= 400; k++) grid.push(lo + k);
  for (let M = (lo + 400) * 1.004; M < 2e7; M *= 1.004) grid.push(Math.round(M));
  let best = -Infinity, bestM = null;
  const ll = grid.map(M => llUniform(h, m, M));
  for (let i = 0; i < grid.length; i++) if (ll[i] > best) { best = ll[i]; bestM = grid[i]; }
  const llInf = llUniform(h, m, Infinity);
  if (llInf >= best) { best = llInf; bestM = Infinity; }
  let ciLo = null, ciHi = null;
  for (let i = 0; i < grid.length; i++) if (ll[i] >= best - 1.92) { if (ciLo === null) ciLo = grid[i]; ciHi = grid[i]; }
  if (llInf >= best - 1.92) ciHi = Infinity;
  if (ciLo === null) ciLo = bestM;
  return { m, M: bestM, ll: best, ciLo, ciHi, events: E, lo };
}
// Two-step fit of one group (or a pooled class): minGap from the clean single gaps (every blocked round censors, so the
// data do not depend on m), then maxGap by the profile likelihood with the segments reduced at that minGap.
function fitGroup(segs, wts) {
  const h1 = histAt(segs, 1, wts);
  let E1 = 0; for (const [, n] of h1.ev) E1 += n;
  // smallest gap between observed attempts (any segment): minGap cannot exceed it
  let mMax = Infinity; for (let i = 0; i < segs.length; i++) if ((!wts || wts[i]) && segs[i].t !== null) mMax = Math.min(mMax, segs[i].t);
  if (!E1 && mMax === Infinity) { return { never: true, m: null, M: 0, mLo: null, mHi: null, ciLo: 0, ciHi: 0, bound: noSpawnBound(h1), events: 0, cleanEvents: 0, segs: segs.length }; }
  const mHat = Math.min(mMax, h1.ev.length ? h1.ev[0][0] : mMax);
  // 95% interval for m: the smallest of n uniform draws exceeds m + k with probability ((w - k) / w)^n, so
  // m >= mHat - w (1 - 0.05^(1/n)). The clean gaps near the small end are hardly censored; w from the fit below.
  const f1 = fitM(h1, mHat);
  const w1 = (f1.M === Infinity ? Math.max(mHat, f1.lo) * 10 : f1.M) - mHat + 1;
  const mLo = Math.max(1, mHat - Math.ceil(w1 * (1 - Math.pow(0.05, 1 / Math.max(1, E1)))));
  const h = histAt(segs, mHat, wts);
  const f = fitM(h, mHat);
  return { never: false, m: mHat, mLo, mHi: mHat, M: f.M, ciLo: f.ciLo, ciHi: f.ciHi, ll: f.ll, events: f.events, cleanEvents: E1, segs: segs.length, h };
}
// For a group that never spawned: the smallest maxGap still compatible (95%) with seeing no spawn, taking minGap 1.
function noSpawnBound(h, runs) {
  // runs: free windows (length, count) that start after a blocked round, i.e. at an unknown countdown phase. For gaps
  // U[1, M] the stationary chance that a window of L rounds holds no attempt is (M-L)(M-L+1) / (M(M+1)).
  const llRuns = M => { let s = 0; for (const [L, n] of runs || []) { if (L >= M) return -Infinity; s += n * (Math.log(M - L) + Math.log(M - L + 1) - Math.log(M) - Math.log(M + 1)); } return s; };
  for (let M = 1; M < 1e9; M = Math.ceil(M * 1.01)) if (llUniform(h, 1, M) + llRuns(M) >= -1.92) return M;
  return Infinity;
}
// free windows after the first blocked round (unknown phase), for a game in which the group never spawned
function unanchoredRuns(blk, rounds, out) {
  const B = blk || [];
  for (let j = 0; j < B.length; j += 2) {
    const start = B[j + 1] + 1, end = j + 2 < B.length ? B[j + 2] : rounds; // free rounds start..end-1
    if (end > start) out.set(end - start, (out.get(end - start) || 0) + 1);
  }
}
// Kaplan-Meier survival of the gap from reduced segments; restricted mean up to A
function kmMean(h, A) {
  const maxAge = A;
  const dAt = new Map(h.ev), nAt = new Float64Array(maxAge + 2);
  // at risk at age a: events t >= a, censorings c > a
  const add = (a, n) => { for (let x = 0; x <= Math.min(a, maxAge + 1); x++) nAt[x] += n; };
  for (const [t, n] of h.ev) add(t, n);
  for (const [c, n] of h.cs) add(c - 1, n);
  let S = 1, mean = 0, minRisk = Infinity;
  for (let a = 0; a < maxAge; a++) {
    // S(a) = P(g > a)
    const d = dAt.get(a) || 0, n = nAt[a];
    if (a > 0 && n > 0) S *= 1 - d / n;
    if (a > 0) minRisk = Math.min(minRisk, n);
    mean += S;
  }
  return { mean, minRisk };
}
const uniformRestrictedMean = (m, M, A) => { let s = 0; for (let a = 0; a < A; a++) s += a < m ? 1 : Math.max(0, Math.min(1, (M - a) / (M - m + 1))); return s; };

// ---------------------------------------------------------------------------------------------------------------------
// Analysis of one category (or a subset of its games) against a reference layout (Map canon -> [min, max]).
const q = (a, p) => { if (!a.length) return null; const b = Float64Array.from(a).sort(); return b[Math.min(b.length - 1, Math.floor((b.length - 1) * p + 1e-9))]; };
function groupTiles(c, g) { const t2 = c.mir(g); return t2 === g ? [g] : [g, t2]; }
// Longest run of consecutive free rounds (some tile of the group free) without a spawn. Any maxGap <= this run is
// impossible: the run would contain an attempt on a free round, i.e. a spawn. Needs no known attempt, so it also covers
// groups that were blocked on round 0 and never spawned (their segments carry no anchored information).
function maxFreeRun(ep, blk, rounds) {
  const B = blk || [], E = ep || [];
  let best = 0, r = 0, bi = 0, ei = 0;
  while (r < rounds) {
    while (bi < B.length && B[bi + 1] < r) bi += 2;
    if (bi < B.length && B[bi] <= r) { r = B[bi + 1] + 1; continue; }
    const nextB = bi < B.length ? B[bi] : rounds;
    while (ei < E.length && E[ei] < r) ei++;
    const nextE = ei < E.length ? E[ei] : Infinity;
    const end = Math.min(nextB, nextE, rounds); // run r..end-1
    best = Math.max(best, end - r);
    r = end === nextE ? end + 1 : end;
  }
  return best;
}
function analyze(c, games, ref) {
  const groups = [...c.relevant].sort((a, b) => a - b);
  const per = new Map();
  for (const g of groups) {
    const segs = [], first = [], never = [], perGameSpawns = [];
    const tiles = groupTiles(c, g);
    const eatDelay = [];
    let freeRun = 0;
    const uRuns = new Map();
    for (const G of games) {
      const ep = G.ep.get(g);
      if (!ep || !ep.length) { freeRun = Math.max(freeRun, maxFreeRun(ep, G.blk.get(g), G.rounds)); unanchoredRuns(G.blk.get(g), G.rounds, uRuns); }
      segs.push(...segmentsOf(ep, G.blk.get(g), G.rounds));
      if (ep && ep.length) first.push(ep[0]); else never.push(G.rounds);
      let n = 0;
      for (const t of tiles) {
        const sp = G.tsp.get(t) || [], ea = G.teat.get(t) || [];
        n += sp.length;
        let j = 0;
        for (const e of ea) { while (j < sp.length && sp[j] <= e) j++; if (j < sp.length) eatDelay.push(sp[j] - e); }
      }
      perGameSpawns.push(n / tiles.length);
    }
    const f = fitGroup(segs);
    if (f.never) { f.freeRun = freeRun; f.bound = noSpawnBound(histAt(segs, 1), [...uRuns]); } // with unanchored windows
    per.set(g, { g, tiles, segs, first, never, perGameSpawns, eatDelay, fit: f, ref: ref.get(g) || [0, 0] });
  }
  // classes by the reference gaps
  const classes = new Map();
  for (const x of per.values()) { const k = x.ref.join('-'); if (!classes.has(k)) classes.set(k, []); classes.get(k).push(x); }
  const cls = [];
  for (const [k, xs] of classes) {
    const [mf, Mf] = k.split('-').map(Number);
    const segs = xs.flatMap(x => x.segs);
    const fit = fitGroup(segs);
    const out = { key: k, mf, Mf, groups: xs.length, tiles: xs.reduce((s, x) => s + x.tiles.length, 0), fit, xs };
    out.spawnsPerTile = xs.reduce((s, x) => s + x.perGameSpawns.reduce((a, b) => a + b, 0) * x.tiles.length, 0) / Math.max(1, out.tiles * games.length);
    out.first = xs.flatMap(x => x.first);
    out.neverShare = xs.reduce((s, x) => s + x.never.length, 0) / Math.max(1, xs.length * games.length);
    out.eatDelay = xs.flatMap(x => x.eatDelay);
    // single gaps at the reference minGap (or 1): range and count outside the reference range
    const h = histAt(segs, Math.max(1, mf || 1));
    let n = 0, lo = Infinity, hi = 0, outside = 0;
    for (const [t, c2] of h.ev) { n += c2; lo = Math.min(lo, t); hi = Math.max(hi, t); if (Mf > 0 && (t < mf || t > Mf)) outside += c2; else if (!(Mf > 0)) outside += c2; }
    out.gaps = { n, lo: n ? lo : null, hi: n ? hi : null, outside };
    if (Mf > 0) {
      out.llRef = llUniform(h, mf, Mf);
      out.fitAtRef = fitM(h, mf);
      out.lr = out.llRef === -Infinity ? Infinity : 2 * (out.fitAtRef.ll - out.llRef);
      const A = Math.min(Mf, 500);
      out.km = { A, obs: kmMean(h, A).mean, uni: uniformRestrictedMean(mf, Mf, A) };
    } else {
      out.llRef = h.ev.length ? -Infinity : 0; out.lr = h.ev.length ? Infinity : 0;
    }
    cls.push(out);
  }
  cls.sort((a, b) => (a.Mf === 0) - (b.Mf === 0) || a.mf - b.mf || a.Mf - b.Mf);
  return { per, cls };
}
// A group disagrees with its reference when: it never spawned though the reference spawns (and the data exclude the
// reference maxGap), it spawned though the reference says never, a single gap lies outside the reference range, or
// the reference is outside the group's own 95% interval by a margin (wide ranges: 25%, see the estimator check).
function groupVerdict(x) {
  const [mf, Mf] = x.ref, f = x.fit;
  if (f.never) return Mf > 0 ? (Math.max(f.bound, (f.freeRun || 0) + 1) > Mf ? 'never' : null) : null;
  if (!(Mf > 0)) return 'spawns';
  const h = histAt(x.segs, mf);
  for (const [t] of h.ev) if (t < mf || t > Mf) return 'outside';
  if (llUniform(h, mf, Mf) === -Infinity) return 'outside';
  const fr = fitM(h, mf);
  if (Mf < fr.ciLo / 1.25 || Mf > fr.ciHi * 1.25) return 'rate';
  if (f.mLo > mf) return 'min';
  return null;
}

// ---------------------------------------------------------------------------------------------------------------------
// report command
const fmtN = v => v === null || v === undefined ? '–' : v === Infinity ? '∞' : typeof v === 'number' && !Number.isInteger(v) ? v.toFixed(2) : String(v);
const fmtFit = f => f.never ? `생성 없음 (max ≥ ${fmtN(Math.max(f.bound, (f.freeRun || 0) + 1))})` : `${f.m}${f.mLo < f.m ? ` [${f.mLo}–${f.m}]` : ''} – ${fmtN(f.M)} [${fmtN(f.ciLo)}, ${fmtN(f.ciHi)}]`;
const pct = x => (100 * x).toFixed(0) + '%';
function catLabel(c) { return c.nd === undefined ? c.map : `${c.map} (${c.nd}마리)`; }
function describeGames(games) {
  const src = {}; let t0 = null, t1 = null;
  for (const G of games) { src[G.src] = (src[G.src] || 0) + 1; if (G.at) { if (!t0 || G.at < t0) t0 = G.at; if (!t1 || G.at > t1) t1 = G.at; } }
  return `${games.length}판 (${Object.entries(src).map(([k, v]) => `${k === 'top' ? '상위권끼리' : k === 'online' ? '우리 대 상위권' : k} ${v}`).join(', ')})${t0 ? `, ${t0.slice(0, 16)}Z – ${t1.slice(0, 16)}Z` : ''}`;
}
function printAnalysis(c, games, ref, refName, out = console.log) {
  const A = analyze(c, games, ref);
  out(`\n### ${catLabel(c)} — ${describeGames(games)}`);
  out(`기준 지도: ${refName}. 대칭 ${c.sym}, 묶음 = 칸 + 대칭 칸(카운트다운 공유).`);
  out('');
  out('| 파일 간격 | 묶음(칸) | 판·칸당 생성 | 첫 생성 p10/p50/p90 | 생성 없는 판 | 한 간격 표본 n (최소–최대) | 파일 범위 밖 | 관측 추정 min – max [95%] | LR(파일) | KM 평균 관측/균등 (<A) | 먹힘→다음 생성 p50/p90/최대 |');
  out('|---|---|---:|---|---:|---|---:|---|---:|---|---|');
  for (const k of A.cls) {
    const ed = k.eatDelay;
    out(`| ${k.Mf > 0 ? `${k.mf}–${k.Mf}` : '0 0 (생성 없음)'} | ${k.groups} (${k.tiles}) | ${k.spawnsPerTile.toFixed(2)} | ${fmtN(q(k.first, 0.1))} / ${fmtN(q(k.first, 0.5))} / ${fmtN(q(k.first, 0.9))} | ${pct(k.neverShare)} | ${k.gaps.n} (${fmtN(k.gaps.lo)}–${fmtN(k.gaps.hi)}) | ${k.gaps.outside} | ${fmtFit(k.fit)} | ${k.lr === Infinity ? '불가능' : k.lr.toFixed(1)} | ${k.km ? `${k.km.obs.toFixed(1)} / ${k.km.uni.toFixed(1)} (<${k.km.A})` : '–'} | ${ed.length ? `${q(ed, 0.5)} / ${q(ed, 0.9)} / ${Math.max(...ed.slice(0, 1e5))}` : '–'} |`);
  }
  const bad = [];
  for (const x of A.per.values()) { const v = groupVerdict(x); if (v) bad.push([x, v]); }
  if (bad.length) {
    out('');
    out(`기준과 어긋나는 묶음 ${bad.length}개:`);
    out('| 묶음 | 파일 간격 | 관측 추정 min – max [95%] | 한 간격 표본 | 첫 생성 p50 (생성한 판 / 전체) | 판정 |');
    out('|---|---|---|---:|---|---|');
    const why = { never: '한 번도 생성 안 됨', spawns: '파일은 0 0인데 생성됨', outside: '간격이 파일 범위 밖', rate: '생성 빈도가 파일과 다름', min: '최소 간격이 파일보다 큼' };
    for (const [x, v] of bad.sort((a, b) => a[0].g - b[0].g)) {
      out(`| ${x.tiles.map(t => tileName(t, c.W)).join(' ')} | ${x.ref[1] > 0 ? x.ref.join('–') : '0 0'} | ${fmtFit(x.fit)} | ${x.fit.events || 0} | ${fmtN(q(x.first, 0.5))} (${x.first.length}/${games.length}) | ${why[v]} |`);
    }
  } else out('\n기준과 어긋나는 묶음 없음.');
  return A;
}
async function cmdReport(args) {
  const file = args.local ? CACHE.local : CACHE.server;
  // server: only games after the 2026-09-27 11:00Z change (earlier replays carry the true gaps and are all the file's)
  const cats = await loadGames(file, r => (!args.map || r.map === args.map) && (args.local || !r.truth));
  const V = args.variant && fs.existsSync(VARJSON) ? JSON.parse(fs.readFileSync(VARJSON, 'utf8')) : null;
  const dump = {};
  for (const c of [...cats.values()].sort((a, b) => a.key.localeCompare(b.key))) {
    let ref = c.fileLay, refName = c.file ? c.file.file : '(없음)', games = c.games;
    if (V) {
      // --variant a|b|10|all: games assigned to that variant; reference = file (a) or the variant's built file
      const vc = V.cats[c.key]; if (!vc) continue;
      const tags = args.variant === 'all' ? vc.variants.map(v => v.tag) : [String(args.variant)];
      for (const tag of tags) {
        const v = vc.variants.find(x => x.tag === tag); if (!v) continue;
        const sub = games.filter(G => vc.assign[G.key] === tag);
        if (!sub.length) continue;
        let r2 = c.fileLay, n2 = refName;
        if (!v.isFile) { const f = path.join(VARDIR, `${path.basename(c.file.file, '.map')}_${tag}.map`); r2 = layoutOf(parseMapText(fs.readFileSync(f, 'utf8'))); n2 = path.relative(ROOT, f); }
        console.log(`\n## 판본 ${tag}${v.isFile ? ' (온라인 파일과 같음)' : ''}`);
        const A = printAnalysis(c, sub, r2, n2);
        dump[c.key + ' ' + tag] = dumpGroups(c, A, sub.length);
      }
      continue;
    }
    if (args.ref) { const mf = parseMapText(fs.readFileSync(path.resolve(ROOT, args.ref), 'utf8')); ref = layoutOf(mf); refName = args.ref; }
    const A = printAnalysis(c, games, ref, refName);
    dump[c.key] = dumpGroups(c, A, games.length);
  }
  if (args.json) { fs.writeFileSync(path.resolve(ROOT, args.json), JSON.stringify(dump)); console.error(`wrote ${args.json}`); }
}
// per group (tile + mirror) statistics for --json
function dumpGroups(c, A, nGames) {
  return [...A.per.values()].map(x => ({
    tiles: x.tiles.map(t => [t % c.W, Math.floor(t / c.W)]), ref: x.ref,
    spawnsPerGame: +(x.perGameSpawns.reduce((a, b) => a + b, 0) / Math.max(1, nGames)).toFixed(3),
    neverShare: +(x.never.length / Math.max(1, nGames)).toFixed(3),
    first: { n: x.first.length, p10: q(x.first, 0.1), p50: q(x.first, 0.5), p90: q(x.first, 0.9), min: x.first.length ? Math.min(...x.first) : null, max: x.first.length ? Math.max(...x.first) : null },
    eatToSpawn: { n: x.eatDelay.length, p50: q(x.eatDelay, 0.5), p90: q(x.eatDelay, 0.9) },
    fit: x.fit.never ? { never: true, maxGapAtLeast: Math.max(x.fit.bound, (x.fit.freeRun || 0) + 1) } : { m: x.fit.m, mLo: x.fit.mLo, M: x.fit.M, ciLo: x.fit.ciLo, ciHi: x.fit.ciHi, gaps: x.fit.events },
    verdict: groupVerdict(x),
  }));
}

// ---------------------------------------------------------------------------------------------------------------------
// Variants. A layout is Map canon -> [min, max] ([0, 0] = never). Each game is scored under each layout by the
// censored-uniform log-likelihood of its segments, group by group, with a floor per group (an impossible observation
// costs FLOOR instead of -infinity, so one odd group cannot decide alone). Two layouts are compared on the same data:
// each group's segments are reduced at the smaller of the two minGaps.
const FLOOR = -25;
function gameSegs(c, G) {
  if (G._segs) return G._segs;
  const m = new Map();
  for (const g of c.relevant) m.set(g, segmentsOf(G.ep.get(g), G.blk.get(g), G.rounds));
  G._segs = m;
  return m;
}
function llGameGroup(segs, mRed, mm, MM) {
  const h = histAt(segs, Math.max(1, mRed));
  const ll = llUniform(h, Math.max(1, mm || 1), MM);
  return Math.max(FLOOR, ll);
}
// per-game score of each layout (array of layouts), comparable across layouts
function scoreGame(c, G, layouts) {
  const segsBy = gameSegs(c, G);
  const sc = layouts.map(() => 0);
  for (const g of c.relevant) {
    const segs = segsBy.get(g);
    const ps = layouts.map(L => L.get(g) || [0, 0]);
    const mRed = Math.min(...ps.map(p => p[1] > 0 ? p[0] : Infinity));
    const mr = mRed === Infinity ? 1 : mRed;
    for (let i = 0; i < layouts.length; i++) sc[i] += llGameGroup(segs, mr, ps[i][0], ps[i][1]);
  }
  return sc;
}
// hard contradictions of a game with a layout: groups whose observations are impossible under it
function contradictions(c, G, L) {
  const segsBy = gameSegs(c, G), bad = [];
  for (const g of c.relevant) {
    const p = L.get(g) || [0, 0];
    const h = histAt(segsBy.get(g), Math.max(1, p[1] > 0 ? p[0] : 1));
    if (llUniform(h, Math.max(1, p[0] || 1), p[1]) === -Infinity) bad.push(g);
  }
  return bad;
}
// fit a layout from a set of games (per group, two-step fit). Groups with no spawn get [0, 0].
function fitLayout(c, games) {
  const L = new Map(), fits = new Map();
  for (const g of c.relevant) {
    const segs = [];
    for (const G of games) segs.push(...gameSegs(c, G).get(g));
    const f = fitGroup(segs);
    fits.set(g, f);
    L.set(g, f.never ? [0, 0] : [f.m, f.M === Infinity ? 1e7 : f.M]);
  }
  return { L, fits };
}
// Hard EM: start from the file layout and a layout fitted to the games that contradict it; assign each game to the
// better layout, refit the non-file layouts, repeat. A further layout is added while games still contradict all
// layouts (at most maxK). The file layout is kept fixed so that "same as the file" stays a testable answer.
function findVariants(c, fileL, maxK = 3, log = () => {}) {
  const games = c.games;
  const layouts = [{ name: 'file', L: fileL, fixed: true }];
  let assign = games.map(() => 0);
  for (let round = 0; round < 12; round++) {
    const orphan = games.filter(G => layouts.every(l => contradictions(c, G, l.L).length > 0));
    if (orphan.length >= Math.max(5, 0.02 * games.length) && layouts.length < maxK) {
      const { L } = fitLayout(c, orphan);
      layouts.push({ name: 'v' + layouts.length, L, fixed: false });
      log(`  새 판본 후보 v${layouts.length - 1}: 모든 판본과 모순인 ${orphan.length}판에서 맞춤`);
    }
    const scores = games.map(G => scoreGame(c, G, layouts.map(l => l.L)));
    const next = scores.map(s => s.indexOf(Math.max(...s)));
    const changed = next.filter((a, i) => a !== assign[i]).length;
    assign = next;
    for (let k = 0; k < layouts.length; k++) if (!layouts[k].fixed) {
      const sub = games.filter((G, i) => assign[i] === k);
      if (sub.length) layouts[k].L = fitLayout(c, sub).L;
    }
    log(`  반복 ${round + 1}: 판본별 판 ${layouts.map((l, k) => `${l.name} ${assign.filter(a => a === k).length}`).join(', ')}, 바뀐 판 ${changed}`);
    if (!changed && round > 0) break;
  }
  const used = layouts.map((l, k) => assign.filter(a => a === k).length);
  return { layouts, assign, used, scores: games.map(G => scoreGame(c, G, layouts.map(l => l.L))) };
}
// Clean layout of a set of games (one variant). Each group is 'never' (0 0), 'same' (file values) or 'changed'.
// 'same' groups of a file class are pooled and must agree with the file (no gap outside, LR < LR_SAME); otherwise they
// become 'changed'. Changed groups are pooled into classes greedily: seed = the changed group with most single gaps;
// members = changed groups whose own 95% interval (25% margin on the maximum) holds the pooled estimate; refit; repeat.
// Returns L (estimates), Ltol (loosest values inside the intervals, for contradiction counts), classes and statuses.
const LR_SAME = 20;
function compatible(x, f) {
  const g = x.fit;
  if (g.never) return false;
  if (f.m < g.mLo - 1 || f.m > g.m + 1) return false;
  const hi = g.ciHi === Infinity ? Infinity : g.ciHi * 1.25;
  return f.M >= g.ciLo / 1.25 && f.M <= hi;
}
function cleanLayout(c, games, fileL) {
  const A = analyze(c, games, fileL);
  const status = new Map();
  for (const x of A.per.values()) {
    const v = groupVerdict(x);
    status.set(x.g, x.fit.never ? (v === 'never' ? 'never' : 'same') : v ? 'changed' : 'same');
  }
  // 'same' groups per file class must agree with the file when pooled
  const sameCls = [];
  const byRef = new Map();
  for (const x of A.per.values()) if (status.get(x.g) === 'same' && x.ref[1] > 0) { const k = x.ref.join('-'); if (!byRef.has(k)) byRef.set(k, []); byRef.get(k).push(x); }
  for (const [k, xs] of byRef) {
    const [mf, Mf] = k.split('-').map(Number);
    const h = histAt(xs.flatMap(x => x.segs), mf);
    const ll = llUniform(h, mf, Mf), fa = fitM(h, mf), lr = ll === -Infinity ? Infinity : 2 * (fa.ll - ll);
    const fit = fitGroup(xs.flatMap(x => x.segs));
    sameCls.push({ key: k, groups: xs.length, lr, fit });
    if (lr >= LR_SAME) for (const x of xs) status.set(x.g, 'changed');
  }
  const changed = [...A.per.values()].filter(x => status.get(x.g) === 'changed');
  const classes = [];
  let rest = changed.slice().sort((a, b) => (b.fit.events || 0) - (a.fit.events || 0));
  while (rest.length) {
    let members = [rest[0]], fit = null;
    for (let it = 0; it < 8; it++) {
      fit = fitGroup(members.flatMap(x => x.segs));
      const next = rest.filter(x => x === rest[0] || compatible(x, fit));
      const same = next.length === members.length && next.every(x => members.includes(x));
      members = next;
      if (same) break;
    }
    fit = fitGroup(members.flatMap(x => x.segs));
    const from = new Map();
    for (const x of members) { const k = x.ref[1] ? x.ref.join('-') : '0'; from.set(k, (from.get(k) || 0) + 1); }
    classes.push({ members, fit, from });
    rest = rest.filter(x => !members.includes(x));
  }
  const L = new Map(), Ltol = new Map(), classOf = new Map();
  for (const x of A.per.values()) {
    const st = status.get(x.g);
    if (st === 'never') { L.set(x.g, [0, 0]); Ltol.set(x.g, [0, 0]); }
    else if (st === 'same') { L.set(x.g, x.ref.slice()); Ltol.set(x.g, x.ref.slice()); }
  }
  classes.forEach((k, i) => {
    const f = k.fit;
    for (const x of k.members) {
      L.set(x.g, [f.m, f.M]);
      Ltol.set(x.g, [Math.max(1, f.mLo), f.ciHi === Infinity ? 1e7 : f.ciHi]);
      classOf.set(x.g, i);
    }
  });
  return { A, L, Ltol, status, classes, sameCls, classOf };
}
const hourBin = (at, h) => { if (!at) return '?'; const d = new Date(at); d.setUTCMinutes(0, 0, 0); d.setUTCHours(Math.floor(d.getUTCHours() / h) * h); return d.toISOString().slice(5, 13) + 'Z'; };
const VARJSON = path.join(OUTDIR, 'variants.json');
// games before the 2026-09-27 11:00Z change still carry the true gaps; are they the file's?
function truthEqualsFile(G, c) {
  for (const g of c.relevant) {
    const a = c.fileLay.get(g) || [0, 0], b = G.truth.get(g) || [0, 0];
    if (a[1] !== b[1] || (a[1] > 0 && a[0] !== b[0])) return false;
  }
  for (const [g, b] of G.truth) { const a = c.fileLay.get(g) || [0, 0]; if (a[1] !== b[1] || (a[1] > 0 && a[0] !== b[0])) return false; }
  return true;
}
const variantTag = (c, k) => (k > 0 && c.file && c.nd !== c.file.dragons.length ? String(c.nd) + (k > 1 ? 'abcdefgh'[k] : '') : 'abcdefgh'[k]);
// chi-square upper tail (Wilson-Hilferty)
function chi2p(x, df) {
  if (df <= 0) return 1;
  const z = (Math.pow(x / df, 1 / 3) - (1 - 2 / (9 * df))) / Math.sqrt(2 / (9 * df));
  const t = 1 / (1 + 0.2316419 * Math.abs(z)), d = 0.3989423 * Math.exp(-z * z / 2);
  const pUpper = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  return z > 0 ? pUpper : 1 - pUpper;
}
function timeTest(games, assign, nv, binH) {
  const bins = new Map();
  games.forEach((G, i) => { const b = hourBin(G.at, binH); if (!bins.has(b)) bins.set(b, new Array(nv).fill(0)); bins.get(b)[assign[i]]++; });
  const rows = [...bins].sort((a, b) => a[0].localeCompare(b[0]));
  const used = rows.filter(([, n]) => n.reduce((a, b) => a + b, 0) >= 10);
  const tot = new Array(nv).fill(0); for (const [, n] of used) n.forEach((v, j) => tot[j] += v);
  const N = tot.reduce((a, b) => a + b, 0);
  let x2 = 0;
  for (const [, n] of used) { const r = n.reduce((a, b) => a + b, 0); for (let j = 0; j < nv; j++) { const e = r * tot[j] / N; if (e > 0) x2 += (n[j] - e) ** 2 / e; } }
  const df = (used.length - 1) * (tot.filter(v => v > 0).length - 1);
  return { rows, x2, df, p: chi2p(x2, df), binsUsed: used.length };
}
async function cmdVariants(args) {
  const cats = await loadGames(CACHE.server, r => !args.map || r.map === args.map);
  const binH = +(args.bin || 3);
  const byMap = new Map();
  const out = fs.existsSync(VARJSON) && args.map ? JSON.parse(fs.readFileSync(VARJSON, 'utf8')) : { cats: {} };
  out.generated = new Date().toISOString();
  out.method = 'tools/pearl_layout.js variants: hard EM from the file layout, clean layouts per variant, final assignment by the tolerant clean layouts';
  for (const c of [...cats.values()].sort((a, b) => a.key.localeCompare(b.key))) {
    const pre = c.games.filter(G => G.truth), post = c.games.filter(G => !G.truth);
    const preEq = pre.filter(G => truthEqualsFile(G, c)).length;
    const cc = Object.assign({}, c, { games: post });
    console.log(`\n### ${catLabel(c)} — 변경 뒤 ${describeGames(post)}`);
    if (pre.length) console.log(`변경 전(2026-09-27 11:00Z 전, 간격이 보이는 리플레이) ${pre.length}판: 파일과 같은 판 ${preEq}.`);
    const res = findVariants(cc, c.fileLay, +(args.k || 3), s => args.verbose && console.log(s));
    const variants = [{ tag: variantTag(c, 0), isFile: true, L: c.fileLay, Ltol: c.fileLay }];
    for (let k = 1; k < res.layouts.length; k++) if (res.used[k]) {
      const sub = post.filter((G, i) => res.assign[i] === k);
      const CL = cleanLayout(cc, sub, c.fileLay);
      variants.push({ tag: variantTag(c, variants.length), isFile: false, L: CL.L, Ltol: CL.Ltol, CL });
    }
    const scores = post.map(G => scoreGame(cc, G, variants.map(v => v.Ltol)));
    const assign = scores.map(sc => sc.indexOf(Math.max(...sc)));
    const contra = post.map((G, i) => contradictions(cc, G, variants[assign[i]].Ltol).length);
    const contraFile = post.map(G => contradictions(cc, G, c.fileLay).length);
    console.log('\n| 판본 | 판 | 비율 [95%] | 상위권끼리 / 우리 | 배정 판본과 모순인 판 | 파일과 모순인 묶음(판당) | 판본 점수 차 최소 |');
    console.log('|---|---:|---|---|---:|---:|---:|');
    const vout = [];
    for (let k = 0; k < variants.length; k++) {
      const idx = post.map((G, i) => i).filter(i => assign[i] === k);
      const n = idx.length, p0 = n / Math.max(1, post.length);
      const se = Math.sqrt(p0 * (1 - p0) / Math.max(1, post.length));
      const top = idx.filter(i => post[i].src === 'top').length;
      const margin = idx.map(i => { const sc = [...scores[i]].sort((a, b) => b - a); return sc.length > 1 ? sc[0] - sc[1] : Infinity; });
      const bad = idx.filter(i => contra[i] > 0).length;
      if (n || !variants[k].isFile) console.log(`| ${variants[k].tag}${variants[k].isFile ? ' (파일)' : ''} | ${n} | ${pct(p0)} [${pct(Math.max(0, p0 - 1.96 * se))}, ${pct(Math.min(1, p0 + 1.96 * se))}] | ${top} / ${n - top} | ${bad} | ${n ? (idx.reduce((s2, i) => s2 + contraFile[i], 0) / n).toFixed(2) : '–'} | ${n ? fmtN(Math.min(...margin)) : '–'} |`);
      const v = variants[k];
      const rec = { tag: v.tag, isFile: v.isFile, games: n, share: +p0.toFixed(4), top, ours: n - top, contradicted: bad };
      if (!v.isFile) {
        rec.layout = [...v.L].sort((a, b) => a[0] - b[0]).map(([g, x]) => [g % c.W, Math.floor(g / c.W), x[0], x[1]]);
        rec.tolerant = [...v.Ltol].sort((a, b) => a[0] - b[0]).map(([g, x]) => [g % c.W, Math.floor(g / c.W), x[0], x[1]]);
        const st = {};
        for (const [g, s2] of v.CL.status) { const ref = c.fileLay.get(g) || [0, 0]; const key = `${ref[1] ? ref.join('-') : '0'} → ${s2}`; st[key] = (st[key] || 0) + 1; }
        rec.status = st;
        rec.same = v.CL.sameCls.map(sc => ({ file: sc.key, groups: sc.groups, lr: +sc.lr.toFixed(2), fit: [sc.fit.m, sc.fit.mLo, sc.fit.M, sc.fit.ciLo, sc.fit.ciHi, sc.fit.events] }));
        rec.classes = v.CL.classes.map(cl => ({ groups: cl.members.length, from: Object.fromEntries(cl.from), fit: cl.fit.never ? null : [cl.fit.m, cl.fit.mLo, cl.fit.M, cl.fit.ciLo, cl.fit.ciHi, cl.fit.events], tiles: cl.members.map(x => groupTiles(c, x.g).map(t => [t % c.W, Math.floor(t / c.W)])) }));
      }
      vout.push(rec);
    }
    for (const v of variants.slice(1)) {
      const st = {};
      for (const [g, s2] of v.CL.status) { const ref = c.fileLay.get(g) || [0, 0]; const key = `${ref[1] ? ref.join('–') : '0 0'} → ${{ never: '생성 없음', same: '파일 그대로', changed: '새 부류' }[s2]}`; st[key] = (st[key] || 0) + 1; }
      console.log(`\n판본 ${v.tag}: 묶음 상태 ${Object.entries(st).sort().map(([k2, n]) => `${k2} ${n}`).join(', ')}`);
      for (const sc of v.CL.sameCls) console.log(`  파일 그대로 ${sc.key}: 묶음 ${sc.groups}, 합친 추정 ${fmtFit(sc.fit)}, LR(파일) ${sc.lr === Infinity ? '불가능' : sc.lr.toFixed(1)}`);
      v.CL.classes.forEach((cl, i) => console.log(`  새 부류 ${i + 1}: 묶음 ${cl.members.length} (파일에서 ${[...cl.from].map(([k2, n]) => `${k2 === '0' ? '0 0' : k2} ${n}`).join(', ')}), 추정 ${fmtFit(cl.fit)}, 한 간격 표본 ${cl.fit.events || 0}`));
    }
    const tt = timeTest(post, assign, variants.length, binH);
    if (variants.length > 1) {
      console.log(`\n시간대별 판 수 (${binH}시간 UTC, ${variants.map(v => v.tag).join('/')}): ${tt.rows.map(([b, n]) => `${b} ${n.join('/')}`).join(', ')}`);
      console.log(`시간대와 판본의 독립성 카이제곱 ${tt.x2.toFixed(1)}, 자유도 ${tt.df}, p ≈ ${tt.p.toFixed(3)} (10판 이상인 시간대 ${tt.binsUsed}개).`);
    }
    // ambiguous games, start configuration (A/B swap) by variant, natural pearls per game
    const amb = post.map((G, i) => { const sc = [...scores[i]].sort((a, b) => b - a); return sc.length > 1 ? sc[0] - sc[1] : Infinity; });
    const ambIdx = post.map((G, i) => i).filter(i => amb[i] < 10);
    if (variants.filter((v, k) => assign.includes(k)).length > 1)
      console.log(`판본 점수 차 < 10인 판 ${ambIdx.length}개${ambIdx.length ? ` (라운드 ${Math.min(...ambIdx.map(i => post[i].rounds))}–${Math.max(...ambIdx.map(i => post[i].rounds))})` : ''}.`);
    const sigs = [...new Set(post.map(G => G.dragons))];
    console.log(`시작 배치 ${sigs.length}가지(A/B 바꿈)별 판 수: ${variants.map((v, k) => `${v.tag} ${sigs.map(sg => post.filter((G, i) => assign[i] === k && G.dragons === sg).length).join('/')}`).join(', ')}.`);
    const supply = variants.map((v, k) => {
      const idx = post.map((G, i) => i).filter(i => assign[i] === k);
      let all = 0, early = 0;
      for (const i of idx) for (const sp of post[i].tsp.values()) { all += sp.length; for (const r of sp) if (r < 100) early++; }
      return idx.length ? `${v.tag} ${(all / idx.length).toFixed(1)} (첫 100라운드 ${(early / idx.length).toFixed(1)}, 500라운드까지 간 판 ${idx.filter(i => post[i].rounds === 500).length}/${idx.length})` : null;
    }).filter(Boolean);
    console.log(`판당 자연 진주: ${supply.join(', ')}.`);
    out.cats[c.key] = {
      map: c.map, nd: c.nd, file: c.file ? c.file.file : null, pre: { games: pre.length, equalToFile: preEq },
      post: { games: post.length, t0: post.reduce((a, G) => (!a || G.at < a ? G.at : a), null), t1: post.reduce((a, G) => (!a || G.at > a ? G.at : a), null) },
      variants: vout, time: { binHours: binH, rows: tt.rows, chi2: +tt.x2.toFixed(2), df: tt.df, p: +tt.p.toFixed(4) },
      assign: Object.fromEntries(post.map((G, i) => [G.key, variants[assign[i]].tag])),
    };
    (byMap.get(c.map) || byMap.set(c.map, []).get(c.map)).push(...post.map((G, i) => ({ at: G.at, label: `${c.nd}마리 ${variants[assign[i]].tag}` })));
  }
  // map level (Prisoners Dilemma: start dragons 6 / 10 together)
  for (const [map, rows] of byMap) {
    const labels = [...new Set(rows.map(r => r.label))].sort();
    if (labels.length < 2 || [...cats.values()].filter(c => c.map === map).length < 2) continue;
    const tt = timeTest(rows, rows.map(r => labels.indexOf(r.label)), labels.length, binH);
    const n = labels.map(l => rows.filter(r => r.label === l).length);
    console.log(`\n### ${map} 지도 단위 (${labels.join(' / ')}): ${n.join(' / ')}판 (${n.map(v => pct(v / rows.length)).join(' / ')})`);
    console.log(`시간대별 판 수: ${tt.rows.map(([b, k]) => `${b} ${k.join('/')}`).join(', ')}`);
    console.log(`시간대와 판본의 독립성 카이제곱 ${tt.x2.toFixed(1)}, 자유도 ${tt.df}, p ≈ ${tt.p.toFixed(3)}.`);
    out.maps = out.maps || {};
    out.maps[map] = { labels, games: n, chi2: +tt.x2.toFixed(2), df: tt.df, p: +tt.p.toFixed(4), rows: tt.rows };
  }
  // sets up to 2026-09-28: when did the gaps disappear and the variants start?
  if (!args.map) {
    const bySet = new Map();
    const affectedMaps = new Set([...cats.values()].filter(c => out.cats[c.key].variants.some(v => !v.isFile && v.games)).map(c => c.map));
    for (const c of cats.values()) {
      const oc = out.cats[c.key], affected = affectedMaps.has(c.map);
      for (const G of c.games) {
        if (!G.at || G.at >= '2026-09-29') continue;
        const s = bySet.get(G.set) || { t0: G.at, t1: G.at, pre: 0, preEq: 0, a: 0, b: 0, other: 0 };
        if (G.at < s.t0) s.t0 = G.at; if (G.at > s.t1) s.t1 = G.at;
        if (G.truth) { s.pre++; if (truthEqualsFile(G, c)) s.preEq++; }
        else if (!affected) s.other++;
        else if (oc.assign[G.key] === 'a') s.a++; else s.b++;
        bySet.set(G.set, s);
      }
    }
    console.log('\n### 변경 전후 세트 (2026-09-28까지)');
    console.log('| 세트 | 시각 (UTC) | 간격 보임 (파일과 같음) | 영향 지도: a / b·10마리 | 나머지 지도 |');
    console.log('|---|---|---|---|---:|');
    for (const [set, s] of [...bySet].sort((x, y) => x[1].t0.localeCompare(y[1].t0)))
      console.log(`| ${set} | ${s.t0.slice(5, 16)}–${s.t1.slice(11, 16)} | ${s.pre} (${s.preEq}) | ${s.a} / ${s.b} | ${s.other} |`);
    const firstB = {};
    for (const c of cats.values()) for (const G of c.games) { const tag = out.cats[c.key].assign[G.key]; if (tag && tag !== 'a' && (!firstB[c.map] || G.at < firstB[c.map])) firstB[c.map] = G.at; }
    console.log(`첫 비파일 판본: ${Object.entries(firstB).map(([m, t]) => `${m} ${t}`).join(', ')}`);
  }
  fs.writeFileSync(VARJSON, JSON.stringify(out));
  console.error(`wrote ${path.relative(ROOT, VARJSON)}`);
}

// ---------------------------------------------------------------------------------------------------------------------
// build command: maps/variants/<file base>_<tag>.map for every variant that differs from the online file. Kelp,
// portals, symmetry and dragons come from the online file (Prisoners Dilemma 10: dragons of the existing
// maps/variants/prisoners_dilemma_10.map, else of the most common start in the replays). TILE values come from the
// variant's clean layout (both tiles of a mirror group get the group's values; other tiles keep the file's).
function layoutFromList(list, W) { const L = new Map(); for (const [x, y, m, M] of list) L.set(y * W + x, [m, M]); return L; }
function mapTextWith(mf, L, dragonLines) {
  const mir = mirrorOf(mf.sym, mf.W, mf.H), out = [];
  let dragonsDone = false;
  for (const line of mf.lines) {
    const p = line.trim().split(/\s+/);
    if (p[0] === 'TILE') {
      const t = +p[2] * mf.W + +p[1], g = Math.min(t, mir(t));
      const v = L.has(g) ? L.get(g) : mf.tiles.get(t);
      out.push(v[1] > 0 ? `TILE ${p[1]} ${p[2]} ${v[0]} ${v[1]}` : `TILE ${p[1]} ${p[2]} 0 0`);
    } else if (dragonLines && p[0] === 'DRAGON_COUNT') out.push(`DRAGON_COUNT ${dragonLines.length}`);
    else if (dragonLines && p[0] === 'DRAGON') { if (!dragonsDone) { out.push(...dragonLines); dragonsDone = true; } }
    else out.push(line);
  }
  return out.join('\n');
}
function dragonLinesFromSig(sig) {
  return sig.split(' ').map(d => { const team = d[0] === 'A' ? 0 : 1; const segs = d.slice(1).split(':').map(s => s.split('.').join(' ')); return `DRAGON ${team} ${segs.length} ${segs.join(' ')}`; });
}
// is an existing file's layout inside the variant's 95% intervals (same never set, values within [loosest, estimate])?
function layoutAgrees(mfOld, v, c) {
  const Lold = layoutOf(mfOld), est = layoutFromList(v.layout, c.W), tol = layoutFromList(v.tolerant, c.W);
  const bad = [];
  for (const [g, e] of est) {
    const o = Lold.get(g) || [0, 0], t = tol.get(g);
    if ((o[1] > 0) !== (e[1] > 0)) { bad.push(g); continue; }
    if (e[1] > 0 && (o[0] < Math.min(t[0], e[0]) || o[0] > Math.max(t[0], e[0]) || o[1] < Math.min(e[1], t[1]) || o[1] > Math.max(e[1], t[1]))) bad.push(g);
  }
  return bad;
}
async function cmdBuild(args) {
  if (!fs.existsSync(VARJSON)) throw Error('run: node tools/pearl_layout.js variants');
  const V = JSON.parse(fs.readFileSync(VARJSON, 'utf8'));
  const built = [];
  for (const [key, vc] of Object.entries(V.cats)) {
    if (args.map && vc.map !== args.map) continue;
    const mf = mapFiles().online.get(vc.map);
    if (!mf) continue;
    const base = path.basename(mf.file, '.map');
    const c = { W: mf.W, H: mf.H, mir: mirrorOf(mf.sym, mf.W, mf.H) };
    for (const v of vc.variants) {
      if (v.isFile || !v.games) continue;
      const out = path.join(VARDIR, `${base}_${v.tag}.map`);
      let dragonLines = null;
      if (vc.nd !== mf.dragons.length) {
        const old = fs.existsSync(out) ? parseMapText(fs.readFileSync(out, 'utf8')) : null;
        if (old && old.dragons.length === vc.nd) dragonLines = old.dragons.map(d => `DRAGON ${d.join(' ')}`);
        else throw Error(`${key}: no dragon lines for ${vc.nd} dragons (add them from a replay)`);
      }
      const text = mapTextWith(mf, layoutFromList(v.layout, mf.W), dragonLines);
      if (fs.existsSync(out)) {
        const old = parseMapText(fs.readFileSync(out, 'utf8'));
        const bad = layoutAgrees(old, v, c);
        if (!bad.length && !args.force) { console.log(`${key} ${v.tag}: 기존 ${path.relative(ROOT, out)}가 추정 구간 안이라 그대로 둔다.`); built.push({ key, tag: v.tag, file: path.relative(ROOT, out), kept: true }); continue; }
        console.log(`${key} ${v.tag}: 기존 파일과 다른 묶음 ${bad.length}개 → 덮어쓴다.`);
      }
      if (!args.dry) fs.writeFileSync(out, text.endsWith('\n') ? text : text + '\n');
      // summary vs the online file
      const Lf = layoutOf(mf), Lv = layoutOf(parseMapText(text));
      let spawnF = 0, spawnV = 0, changed = 0;
      for (const [t, v2] of mf.tiles) if (v2[1] > 0) spawnF++;
      for (const [t, v2] of parseMapText(text).tiles) if (v2[1] > 0) spawnV++;
      for (const [g, a] of Lf) { const b = Lv.get(g) || [0, 0]; if (a[0] !== b[0] || a[1] !== b[1]) changed++; }
      console.log(`${key} ${v.tag}: ${args.dry ? '(dry) ' : ''}${path.relative(ROOT, out)} — 생성 칸 ${spawnF} → ${spawnV}, 값이 바뀐 묶음 ${changed}`);
      built.push({ key, tag: v.tag, file: path.relative(ROOT, out), kept: false, spawnTiles: [spawnF, spawnV], changedGroups: changed });
    }
  }
  return built;
}

// ---------------------------------------------------------------------------------------------------------------------
// compare command: spawn pattern of local replays (played on a variant file) against the server games of that variant.
async function cmdCompare(args) {
  if (!fs.existsSync(VARJSON)) throw Error('run: node tools/pearl_layout.js variants');
  const V = JSON.parse(fs.readFileSync(VARJSON, 'utf8'));
  const load = makeLoader(require('./top_features.js').viewerSource());
  const rows = args._.slice(1).map(f => { const R = load(path.resolve(ROOT, f)); const x = extract(R); return { key: f, src: 'local', set: 'compare', map: x.mapName, ...x }; });
  const catsCache = new Map();
  for (const r of rows) {
    const key = catOf(r), vc = V.cats[key];
    if (!vc) { console.log(`${r.key}: 서버 자료에 ${key}가 없다.`); continue; }
    if (!catsCache.has(r.map)) catsCache.set(r.map, await loadGames(CACHE.server, x => x.map === r.map && !x.truth));
    const c = catsCache.get(r.map).get(key);
    const G = gameFromRow(c, r);
    // which variant does the local file (true gaps of the replay) implement?
    const Ls = vc.variants.map(v => v.isFile ? c.fileLay : layoutFromList(v.layout, c.W));
    const diffs = Ls.map(L => { let d = 0; for (const g of c.relevant) { const a = L.get(g) || [0, 0], b = G.truth.get(g) || [0, 0]; if ((a[1] > 0) !== (b[1] > 0) || (a[1] > 0 && (Math.abs(a[0] - b[0]) > 1 || Math.abs(a[1] - b[1]) > Math.max(2, 0.02 * a[1])))) d++; } return d; });
    const k = diffs.indexOf(Math.min(...diffs)), v = vc.variants[k];
    const Ltol = v.isFile ? c.fileLay : layoutFromList(v.tolerant, c.W), Lest = Ls[k];
    const serverGames = c.games.filter(S => vc.assign[S.key] === v.tag);
    console.log(`\n### ${r.key}: ${catLabel(c)} 판본 ${v.tag} (지도 파일과 추정의 차이 묶음 ${diffs[k]}, 라운드 ${r.rounds})`);
    console.log(`모순 묶음 수: 판본 ${v.tag} 추정(구간) ${contradictions(c, G, Ltol).length}, 온라인 파일 ${contradictions(c, G, c.fileLay).length}` + vc.variants.filter(w => w !== v && !w.isFile).map(w => `, 판본 ${w.tag} ${contradictions(c, G, layoutFromList(w.tolerant, c.W)).length}`).join(''));
    const Aserv = analyze(c, serverGames, Lest), Aloc = analyze(c, [G], Lest);
    console.log(`| 판본 ${v.tag} 간격 | 묶음 | 서버 ${serverGames.length}판: 판·칸당 생성, 첫 생성 p10/p50/p90, 생성 없는 판 | 로컬 1판: 판·칸당 생성, 첫 생성 p10/p50/p90, 생성 없는 묶음 | 로컬 한 간격 표본 (범위 밖) |`);
    console.log('|---|---:|---|---|---|');
    for (const s of Aserv.cls) {
      const l = Aloc.cls.find(x => x.key === s.key);
      const name = s.Mf > 0 ? `${s.mf}–${s.Mf}` : '0 0';
      console.log(`| ${name} | ${s.groups} | ${s.spawnsPerTile.toFixed(2)}, ${fmtN(q(s.first, 0.1))}/${fmtN(q(s.first, 0.5))}/${fmtN(q(s.first, 0.9))}, ${pct(s.neverShare)} | ${l.spawnsPerTile.toFixed(2)}, ${fmtN(q(l.first, 0.1))}/${fmtN(q(l.first, 0.5))}/${fmtN(q(l.first, 0.9))}, ${pct(l.neverShare)} | ${l.gaps.n} (${l.gaps.outside}) |`);
    }
  }
}

// ---------------------------------------------------------------------------------------------------------------------
// Synthetic check of the estimator: independent schedules with known gaps drawn over the real blocked rounds of real
// games (blocking treated as independent of the schedule). Returns the fit of the pooled synthetic observations.
function mulberry32(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function synthEp(blk, rounds, m, M, rnd) {
  const B = new Uint8Array(rounds + 1);
  for (let j = 0; j < (blk || []).length; j += 2) for (let r = blk[j]; r <= blk[j + 1] && r < rounds; r++) B[r] = 1;
  const ep = [];
  let a = -1;
  for (;;) { a += m + Math.floor(rnd() * (M - m + 1)); if (a >= rounds) break; if (!B[a]) ep.push(a); }
  return ep;
}
// segments truncated at age A (optionally only the first segment of each game), reduced at m
function truncHist(segs, m, A, firstOnly) {
  const ev = new Map(), cs = new Map();
  for (const s of segs) {
    if (firstOnly && s.u !== -1) continue;
    const x = reduceSeg(s, m);
    if (x.ev !== undefined && x.ev <= A) ev.set(x.ev, (ev.get(x.ev) || 0) + 1);
    else { const c2 = Math.min(x.ev !== undefined ? A + 1 : x.cs, A + 1); cs.set(c2, (cs.get(c2) || 0) + 1); }
  }
  return { ev: [...ev].sort((a, b) => a[0] - b[0]), cs: [...cs].sort((a, b) => a[0] - b[0]) };
}
// selftest command: the checks behind the method (research/observations/pearl-variants.md sections 2-3).
//   local : local replays with countdown records: observed spawns are true attempts, clean intervals are single gaps,
//           the first attempt is at initial countdown - 1; distinct attempt schedules per map (local seeds repeat them).
//   synth : independent schedules with the true gaps over the blocked rounds of the local games; 95% interval coverage
//           of the pooled fit (3 repetitions per class, generator seed 12345).
//   window: server games of variant a, wide classes (max >= 200): fit of the first segment up to 50 / 100 / 200 rounds
//           against the fit of all segments.
async function cmdSelftest(args) {
  const part = args._[1] || 'all';
  if (part === 'local' || part === 'all') {
    let semOK = 0, semBad = 0, epNotAtt = 0, epTot = 0, single = 0, multi = 0, games = 0;
    const sched = new Map();
    await forEachRow(CACHE.local, r => {
      if (!r.att) return;
      games++;
      const m = sched.get(r.map) || new Map(); const s = JSON.stringify(r.att); m.set(s, (m.get(s) || 0) + 1); sched.set(r.map, m);
      const mir = mirrorOf(r.sym, r.W, r.H), ep = {};
      for (let i = 0; i < r.spawns.length; i += 2) { const t = r.spawns[i + 1], c = Math.min(t, mir(t)); (ep[c] = ep[c] || new Set()).add(r.spawns[i]); }
      for (const c in r.att) {
        const a = r.att[c], init = a[0], attempts = a.slice(1), as = new Set(attempts);
        if (attempts.length && init !== null) { if (attempts[0] === init - 1) semOK++; else semBad++; }
        for (const e of ep[c] || []) { epTot++; if (!as.has(e)) epNotAtt++; }
        const E = [-1, ...[...(ep[c] || [])].sort((x, y) => x - y)], blk = r.blk[c] || [], blocked = new Set();
        for (let i = 0; i < blk.length; i += 2) for (let q = blk[i]; q <= blk[i + 1]; q++) blocked.add(q);
        for (let i = 0; i + 1 < E.length; i++) {
          let clean = true;
          for (let q = E[i] + 1; q < E[i + 1]; q++) if (blocked.has(q)) { clean = false; break; }
          if (!clean) continue;
          let k = 0; for (const x of attempts) if (x > E[i] && x < E[i + 1]) k++;
          if (k === 0) single++; else multi++;
        }
      }
    });
    console.log(`로컬 ${games}판: 관측 생성(묶음·라운드) ${epTot}회 중 진짜 시도가 아닌 것 ${epNotAtt}; 깨끗한 간격 ${single + multi}개 중 숨은 시도가 낀 것 ${multi}; 첫 시도 = 초기 카운트다운 − 1: ${semOK}/${semOK + semBad}.`);
    console.log(`지도별 시도 일정 가짓수(판): ${[...sched].map(([mp, m]) => `${mp} ${m.size} (${[...m.values()].reduce((a, b) => a + b, 0)})`).join(', ')}`);
  }
  if (part === 'synth' || part === 'all') {
    const cats = await loadGames(CACHE.local);
    const rnd = mulberry32(12345);
    let n = 0, cover = 0;
    for (const c of [...cats.values()].sort((a, b) => a.key.localeCompare(b.key))) {
      const truth = c.games[0].truth, classes = new Map();
      for (const g of c.relevant) { const tr = truth.get(g); if (!tr || tr[1] <= 1) continue; const k = tr.join('-'); if (!classes.has(k)) classes.set(k, []); classes.get(k).push(g); }
      for (const [k, gs] of classes) {
        const [m, M] = k.split('-').map(Number), res = [];
        for (let rep = 0; rep < 3; rep++) {
          const segs = [];
          for (const g of gs) for (const G of c.games) segs.push(...segmentsOf(synthEp(G.blk.get(g), G.rounds, m, M, rnd), G.blk.get(g), G.rounds));
          const f = fitGroup(segs), ok = f.ciLo <= M && M <= f.ciHi;
          n++; if (ok) cover++;
          res.push(`${f.m}–${f.M} [${f.ciLo}, ${f.ciHi}]${ok ? '' : ' 밖'}`);
        }
        console.log(`  ${c.key} ${k}: ${res.join(' | ')}`);
      }
    }
    console.log(`합성 확인: 95% 구간 ${n}개 중 참값을 품은 것 ${cover}개.`);
  }
  if (part === 'window' || part === 'all') {
    if (!fs.existsSync(VARJSON)) throw Error('run: node tools/pearl_layout.js variants');
    const V = JSON.parse(fs.readFileSync(VARJSON, 'utf8'));
    const cats = await loadGames(CACHE.server, r => !r.truth);
    console.log('| 지도 부류 (판본 a) | 첫 구간 ≤50 | ≤100 | ≤200 | 전체 |');
    console.log('|---|---|---|---|---|');
    for (const c of [...cats.values()].sort((a, b) => a.key.localeCompare(b.key))) {
      const vc = V.cats[c.key]; if (!vc) continue;
      const games = c.games.filter(G => vc.assign[G.key] === 'a'); if (!games.length) continue;
      const classes = new Map();
      for (const g of c.relevant) { const ref = c.fileLay.get(g) || [0, 0]; if (ref[1] < 200) continue; const k = ref.join('-'); if (!classes.has(k)) classes.set(k, []); classes.get(k).push(g); }
      for (const [k, gs] of classes) {
        const m = +k.split('-')[0], segs = [];
        for (const g of gs) for (const G of games) segs.push(...segmentsOf(G.ep.get(g), G.blk.get(g), G.rounds));
        const cells = [[50, true], [100, true], [200, true], [500, false]].map(([A, first]) => { const f = fitM(truncHist(segs, m, A, first), m); return `${fmtN(f.M)} [${fmtN(f.ciLo)}, ${fmtN(f.ciHi)}]`; });
        console.log(`| ${c.map} ${k.replace('-', '–')} (${gs.length}묶음, ${games.length}판) | ${cells.join(' | ')} |`);
      }
    }
  }
}

// ---------------------------------------------------------------------------------------------------------------------
function parseArgs(argv) {
  const a = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const s = argv[i];
    if (s.startsWith('--')) {
      const k = s.slice(2), v = argv[i + 1] !== undefined && !argv[i + 1].startsWith('--') ? argv[++i] : true;
      if (k === 'local') (a.local = a.local || []).push(v); else a[k] = v;
    } else a._.push(s);
  }
  return a;
}
module.exports = { cleanLayout, compatible, maxFreeRun, gameFromRow, findVariants, fitLayout, contradictions, scoreGame, gameSegs, analyze, groupVerdict, printAnalysis, synthEp, mulberry32, extract, mirrorOf, parseMapText, forEachRow, CACHE, ROOT, mapFiles, layoutOf, loadGames, segmentsOf, reduceSeg, histAt, llUniform, fitM, fitGroup, noSpawnBound, kmMean, uniformRestrictedMean, tileName, catOf };

if (isMainThread && require.main === module) {
  const args = parseArgs(process.argv.slice(2));
  const cmd = args._[0];
  const run = { extract: cmdExtract, report: cmdReport, variants: cmdVariants, build: cmdBuild, compare: cmdCompare, selftest: cmdSelftest }[cmd];
  if (!run) { console.error('usage: node tools/pearl_layout.js extract|report|variants|build|compare|selftest ... (see header)'); process.exit(2); }
  Promise.resolve(run(args)).catch(e => { console.error(e); process.exit(1); });
}
