#!/usr/bin/env node
// Map and matchup study of top-team games: how results and styles depend on the map and on the style-vs-style
// matchup, and where our bot's style sits. Reads replays only; runs no games and makes no network requests.
// usage: node tools/matchup_study.js [--keys data/top/snapshot-20260929a.keys] [--local exp/eval-r1]
//          [--out data/top/matchup_study.json] [--jobs 4] [--cache <file>] [--quiet]
//   Inputs: the data/top/features.jsonl rows of the snapshot keys (schema: docs/top_features.md), their replays
//   data/top/<battleId>/<gameId>.replay.gz, and our local benchmark <local>/rows.jsonl + <local>/games/<key>/game.replay
//   (key opp:map:side:seed, ':' -> '_' in the directory name; our side is the key's side).
//   Replays are parsed in worker processes (--jobs, capped at 4) for what features.jsonl does not keep: whether a
//   dragon that died on its own turn had a free neighbouring tile, where eaten pearls came from, and map geometry.
//   Local replays also go through tools/top_features.js extract() so both sides use one definition.
//   Excluded team: SSS (see EXCLUDED_TEAMS). Style rule, map adjustment and every table: see tables() below.
//   --cache <file> stores the per-replay results (JSON) and reuses them on the next run (development only).
//   Output: <out> (JSON with every table) and a markdown-style text report on stdout (--quiet: summary line only).
//   The write-up: research/observations/top-maps-matchups.md. Everything is deterministic (seeded resampling).
// Runtime (2026-09-29, 4 jobs, machine shared with other work): 96-199 s for 472 + 160 replays; main process ~0.5 GB.
'use strict';
const fs = require('fs'), path = require('path');
const cp = require('child_process');
// Workers are child processes, not worker threads: tools/top_features.js (required by tools/replay.js) starts its own
// worker loop when it is loaded inside a worker thread.
const IS_WORKER = process.argv.includes('--worker');

const ROOT = path.resolve(__dirname, '..');
const TEAMS = ['A', 'B'], DIRS = ['N', 'E', 'S', 'W'];
const DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 };
const NBIN = 5, bin = r => Math.max(0, Math.min(NBIN - 1, Math.floor(r / 100))); // 100-round bins 0..4
const other = s => (s === 'A' ? 'B' : 'A');
// Own-death categories. Enemy-involved: Hram (we moved into an enemy head), Hrammed (an enemy moved into our head),
// Oenemy (we moved into an enemy body). Everything else is self-inflicted: W kelp, S own body, Oally ally body,
// Hally head-on with an ally (either role), A_<why> no valid action (suicide, split, sprint, tle, none, other).
const ENEMY_CATS = new Set(['Hram', 'Hrammed', 'Oenemy']);
function catOf(tm, d) {
  if (d.reason === 'H') { const by = d.mover ? d.hitTeam : d.byTeam; return by === tm ? 'Hally' : d.mover ? 'Hram' : 'Hrammed'; }
  if (d.reason === 'O') return d.hitTeam === tm ? 'Oally' : 'Oenemy';
  if (d.reason === 'A') return 'A_' + (d.why || 'other');
  return d.reason; // W, S
}

// ---------------------------------------------------------------------------------------------------------------
// Map geometry: wrap-around, kelp and portal edges. Same rules as extract() in tools/top_features.js.
function geometry(M) {
  const W = M.width, H = M.height;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
  const portal = new Map();
  for (const pr of M.portals || []) { if (pr.length !== 2) continue; const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); }
  const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
  const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
  function across(x, y, d) {
    let ek, kelp;
    if (d === 'N') { ek = x + ',' + y + ',N'; kelp = hk(x, y); }
    else if (d === 'S') { ek = x + ',' + wy(y + 1) + ',N'; kelp = hk(x, y + 1); }
    else if (d === 'W') { ek = x + ',' + y + ',W'; kelp = vk(x, y); }
    else { ek = wx(x + 1) + ',' + y + ',W'; kelp = vk(x + 1, y); }
    const p = portal.get(ek);
    if (p) {
      if (d === 'N') return { x: p.x, y: wy(p.y - 1) };
      if (d === 'S') return { x: p.x, y: p.y };
      if (d === 'W') return { x: wx(p.x - 1), y: p.y };
      return { x: p.x, y: p.y };
    }
    if (kelp) return null;
    return { x: wx(x + DX[d]), y: wy(y + DY[d]) };
  }
  return { W, H, across, key: (x, y) => y * W + x };
}

// Static map features. Distances are moves (BFS over kelp, portals and wrap, bodies ignored).
function mapFeatures(M) {
  const G = geometry(M), W = M.width, H = M.height, area = W * H;
  let kelp = 0, portalEdges = 0;
  for (const arr of [M.initialHEdges, M.initialVEdges]) for (const v of arr) { if (v === 1) kelp++; else if (v === 2) portalEdges++; }
  // Spawn gaps: server replays carry zeros here (hidden), local replays the real values. Map-level spawn features come
  // from the .map file (mapFileFeatures); this copy is only used to check the file against local replays.
  let spawnTiles = 0, cap = 0, fountain = 0;
  for (const p of M.pearlRespawn || []) if (p.maxRounds > 0) { spawnTiles++; cap += 2 / (p.minRounds + p.maxRounds); if (p.maxRounds <= 10) fountain++; }
  const init = { A: [], B: [] };
  for (const d of M.initialDragons) init[d.team].push(d.body.length);
  const bfs = srcs => {
    const dist = new Int32Array(area).fill(-1), q = [];
    for (const s of srcs) { const k = G.key(s.x, s.y); if (dist[k] < 0) { dist[k] = 0; q.push(s); } }
    for (let i = 0; i < q.length; i++) {
      const c = q[i], dc = dist[G.key(c.x, c.y)];
      for (const d of DIRS) { const n = G.across(c.x, c.y, d); if (!n) continue; const k = G.key(n.x, n.y); if (dist[k] < 0) { dist[k] = dc + 1; q.push(n); } }
    }
    return dist;
  };
  const heads = tm => M.initialDragons.filter(d => d.team === tm).map(d => d.body[0]);
  const dA = bfs(heads('A')), dB = bfs(heads('B'));
  const toEnemy = heads('A').map(h => dB[G.key(h.x, h.y)]).concat(heads('B').map(h => dA[G.key(h.x, h.y)])).filter(x => x >= 0);
  let reach = 0; for (let k = 0; k < area; k++) if (dA[k] >= 0) reach++;
  const f = {
    name: M.mapName, width: W, height: H, area, symmetry: M.symmetry,
    kelpEdges: kelp, kelpDensity: kelp / (2 * area), portalPairs: (M.portals || []).length, portalEdges,
    replaySpawn: spawnTiles ? { spawnTiles, spawnCapPerRound: cap, fountainTiles: fountain } : null,
    initDragonsPerTeam: init.A.length, initLenPerTeam: init.A.reduce((a, b) => a + b, 0), initMaxLen: Math.max(...init.A, ...init.B),
    headDistMin: toEnemy.length ? Math.min(...toEnemy) : null, headDistMedian: median(toEnemy), reachShareFromA: reach / area,
  };
  // Geometry + starting dragons (not spawn gaps, which server replays hide). Two maps with one name differ here.
  f.sig = JSON.stringify([W, H, kelp, portalEdges, init.A.slice().sort((a, b) => a - b), init.B.slice().sort((a, b) => a - b), f.headDistMin]);
  return f;
}

// Map file maps/online-20260927/<name>.map: source of the spawn features (server replays hide spawn gaps) and a
// cross-check of the replay geometry (kelp, portal edges, dragons) and of local replays' spawn gaps.
function mapFileFeatures(file) {
  let kelp = 0, portalEdges = 0, spawnTiles = 0, cap = 0, fountain = 0, dragons = 0, area = 0;
  for (const l of fs.readFileSync(file, 'utf8').split('\n')) {
    const p = l.trim().split(/\s+/);
    if (p[0] === 'MAP') area = +p[1] * +p[2];
    else if (p[0] === 'EDGE') { if (p[2] === '1') kelp++; else if (p[2] === '2') portalEdges++; }
    else if (p[0] === 'TILE' && +p[4] > 0) { spawnTiles++; cap += 2 / (+p[3] + +p[4]); if (+p[4] <= 10) fountain++; }
    else if (p[0] === 'DRAGON' && p.length > 3) dragons++;
  }
  // spawnCapPerRound = sum over spawning tiles of 1 / mean gap: pearls per round if every attempt found its tile empty.
  return { kelp, portalEdges, dragons, spawnTiles, spawnTileShare: spawnTiles / area, spawnCapPerRound: cap, spawnCapPer100Tiles: 100 * cap / area, fountainTiles: fountain };
}

// ---------------------------------------------------------------------------------------------------------------
// Replay pass: bodies from dragonUpdate/dragonSplit/dragonDeath (the viewer's way; top_features.js showed 0
// mismatches against a step simulation on these games), then per team:
//  exit[cat] = [had a free neighbour, had none] for deaths on the dragon's own turn. Free = the first step in that
//    direction is not kelp and not any body segment (own tail included), on the board at its turnStart.
//  eat[src][bin] = pearls eaten by source: natural, initial, ownSelf / ownKilled (our corpse, self-inflicted or
//    enemy-involved death), oppSelf / oppKilled (enemy corpse).
//  king[bin] / eatAll[bin] = pearls eaten by the team's longest dragon (at its turnStart, ties count) / all.
//  drops.self|enemy = {n, own, opp}: pearls our deaths dropped, and how many our team / the enemy ate later.
// `deaths` = {A, B} death lists from extract(); deaths are matched by (round, id) to get their category.
function replayPass(R, deaths) {
  const M = R.match.map, G = geometry(M), key = G.key;
  const info = new Map();
  for (const tm of TEAMS) for (const d of deaths[tm]) info.set(d.r + ':' + d.id, catOf(tm, d));
  const drag = new Map(), occ = new Map();
  const put = d => { for (const s of d.body) occ.set(key(s.x, s.y), d.id); };
  const clear = d => { for (const s of d.body) { const k = key(s.x, s.y); if (occ.get(k) === d.id) occ.delete(k); } };
  for (const d0 of M.initialDragons) { const d = { id: d0.id, team: d0.team, body: d0.body.map(s => ({ x: s.x, y: s.y })) }; drag.set(d.id, d); put(d); }
  const pearl = new Map();
  (M.initialTiles || []).forEach((v, i) => { if (v === 2) pearl.set(i, { src: 'initial' }); });
  const zeros = () => new Array(NBIN).fill(0);
  const P = {};
  for (const tm of TEAMS) P[tm] = { exit: {}, eat: {}, king: zeros(), eatAll: zeros(), drops: { self: { n: 0, own: 0, opp: 0 }, enemy: { n: 0, own: 0, opp: 0 } } };
  const chk = { unmatchedDeaths: 0, unknownEater: 0, unknownPearl: 0 };
  let round = -1, cur = -1, curFree = -1, curKing = false, drop = null;
  let firstMover = null;
  for (const d of M.initialDragons) if (firstMover === null || d.id < firstMover.id) firstMover = d;
  for (const e of R.events) {
    if (drop && !(e.type === 'tileChange' && e.hasPearl)) drop = null;
    switch (e.type) {
      case 'roundStart': round = e.round; break;
      case 'turnStart': {
        cur = e.id; curFree = -1; curKing = false;
        const d = drag.get(cur); if (!d) break;
        const h = d.body[0]; let free = 0;
        for (const dir of DIRS) { const n = G.across(h.x, h.y, dir); if (n && !occ.has(key(n.x, n.y))) free++; }
        curFree = free;
        let max = 0; for (const o of drag.values()) if (o.team === d.team && o.id !== d.id && o.body.length > max) max = o.body.length;
        curKing = d.body.length >= max;
        break;
      }
      case 'tileChange': {
        const k = key(e.tile.x, e.tile.y);
        if (e.hasPearl) {
          if (drop) { pearl.set(k, { src: 'corpse', team: drop.team, self: drop.self }); P[drop.team].drops[drop.self ? 'self' : 'enemy'].n++; }
          else pearl.set(k, { src: 'natural' });
          break;
        }
        const d = drag.get(cur), src = pearl.get(k); pearl.delete(k);
        if (!d) { chk.unknownEater++; break; }
        if (!src) chk.unknownPearl++;
        const t = P[d.team], b = bin(round);
        const s = !src ? 'unknown' : src.src !== 'corpse' ? src.src : src.team === d.team ? (src.self ? 'ownSelf' : 'ownKilled') : (src.self ? 'oppSelf' : 'oppKilled');
        (t.eat[s] || (t.eat[s] = zeros()))[b]++;
        t.eatAll[b]++; if (curKing) t.king[b]++;
        if (src && src.src === 'corpse') P[src.team].drops[src.self ? 'self' : 'enemy'][src.team === d.team ? 'own' : 'opp']++;
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id); if (!d || round < 0) break;
        const h = d.body[0];
        if (h.x !== e.head.x || h.y !== e.head.y) { d.body.unshift({ x: e.head.x, y: e.head.y }); occ.set(key(e.head.x, e.head.y), d.id); }
        while (d.body.length > 1) {
          const t = d.body[d.body.length - 1];
          if (t.x === e.tail.x && t.y === e.tail.y) break;
          d.body.pop(); const k = key(t.x, t.y); if (occ.get(k) === d.id) occ.delete(k);
        }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        clear(p); p.body = e.parentBody.map(s => ({ x: s.x, y: s.y })); put(p);
        const c = { id: e.childId, team: e.team, body: e.childBody.map(s => ({ x: s.x, y: s.y })) };
        drag.set(c.id, c); put(c);
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        let c = info.get(round + ':' + e.id);
        if (c === undefined) { chk.unmatchedDeaths++; c = 'unknown'; }
        if (cur === e.id) { const x = P[d.team].exit[c] || (P[d.team].exit[c] = [0, 0]); x[curFree > 0 ? 0 : 1]++; }
        clear(d); drag.delete(e.id);
        drop = { team: d.team, self: !ENEMY_CATS.has(c) };
        break;
      }
    }
  }
  return { teams: P, firstMover: firstMover ? firstMover.team : null, checks: chk };
}

// ---------------------------------------------------------------------------------------------------------------
// Worker process (--worker): one replay per message.
if (IS_WORKER) {
  const { load } = require(path.join(__dirname, 'replay.js'));
  const { extract } = require(path.join(__dirname, 'top_features.js'));
  process.on('message', task => {
    try {
      const R = load(task.file);
      let f = null, deaths = task.deaths;
      if (task.kind === 'local') { f = extract(R, task.row); deaths = { A: f.A.deaths, B: f.B.deaths }; }
      const pass = replayPass(R, deaths);
      const map = mapFeatures(R.match.map);
      process.send({ key: task.key, pass, map, f });
    } catch (err) {
      process.send({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 3).join(' | ') });
    }
  });
  process.on('disconnect', () => process.exit(0));
}

// ---------------------------------------------------------------------------------------------------------------
// Small statistics helpers (deterministic).
function median(xs) {
  const a = xs.filter(x => x !== null && x !== undefined && !Number.isNaN(x)).sort((p, q) => p - q);
  if (!a.length) return null;
  const m = a.length >> 1;
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}
function quantile(xs, q) {
  const a = xs.filter(x => x !== null && x !== undefined).sort((p, r) => p - r);
  if (!a.length) return null;
  const pos = (a.length - 1) * q, lo = Math.floor(pos), hi = Math.ceil(pos);
  return a[lo] + (a[hi] - a[lo]) * (pos - lo);
}
const sum = xs => xs.reduce((a, b) => a + (b || 0), 0);
const mean = xs => { const a = xs.filter(x => x !== null && x !== undefined && !Number.isNaN(x)); return a.length ? sum(a) / a.length : null; };
const ratio = (a, b) => (b ? a / b : null);
function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function ranks(xs) {
  const idx = xs.map((x, i) => [x, i]).sort((a, b) => a[0] - b[0]), r = new Array(xs.length);
  for (let i = 0; i < idx.length;) { let j = i; while (j + 1 < idx.length && idx[j + 1][0] === idx[i][0]) j++; for (let k = i; k <= j; k++) r[idx[k][1]] = (i + j) / 2 + 1; i = j + 1; }
  return r;
}
function pearson(x, y) {
  const n = x.length, mx = sum(x) / n, my = sum(y) / n;
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) { sxy += (x[i] - mx) * (y[i] - my); sxx += (x[i] - mx) ** 2; syy += (y[i] - my) ** 2; }
  return sxx && syy ? sxy / Math.sqrt(sxx * syy) : null;
}
function spearman(x, y, perms = 10000, seed = 20260929) {
  const pairs = x.map((v, i) => [v, y[i]]).filter(p => p[0] !== null && p[1] !== null);
  if (pairs.length < 4) return { n: pairs.length, rho: null, p: null };
  const rx = ranks(pairs.map(p => p[0])), ry = ranks(pairs.map(p => p[1]));
  const rho = pearson(rx, ry);
  if (rho === null) return { n: pairs.length, rho: null, p: null };
  const rand = rng(seed), yy = ry.slice(); let hit = 0;
  for (let k = 0; k < perms; k++) {
    for (let i = yy.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [yy[i], yy[j]] = [yy[j], yy[i]]; }
    const r = pearson(rx, yy); if (r !== null && Math.abs(r) >= Math.abs(rho) - 1e-12) hit++;
  }
  return { n: pairs.length, rho, p: r4((hit + 1) / (perms + 1)) };
}
// Cluster bootstrap of a win rate: items {cluster, win (1/0/0.5)}; clusters (battles) resampled with replacement.
function clusterBootWin(items, reps = 2000, seed = 7) {
  const by = new Map();
  for (const it of items) { const c = by.get(it.cluster) || { w: 0, n: 0 }; c.w += it.win; c.n++; by.set(it.cluster, c); }
  const cl = [...by.values()];
  if (cl.length < 2) return null;
  const rand = rng(seed), out = [];
  for (let k = 0; k < reps; k++) { let w = 0, n = 0; for (let i = 0; i < cl.length; i++) { const c = cl[Math.floor(rand() * cl.length)]; w += c.w; n += c.n; } out.push(w / n); }
  return [quantile(out, 0.025), quantile(out, 0.975)];
}
const eloExpect = (a, b) => 1 / (1 + Math.pow(10, (b - a) / 400));
const r2 = x => (x === null || x === undefined ? null : Math.round(x * 100) / 100);
const r3 = x => (x === null || x === undefined ? null : Math.round(x * 1000) / 1000);
const r4 = x => (x === null || x === undefined ? null : Math.round(x * 10000) / 10000);

// ---------------------------------------------------------------------------------------------------------------
// One row per team per game (main-set top games, and our side / the opponent side of local games).
const TL_R = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500];
function teamGame(f, s, pass) {
  const o = other(s), m = f.meta, t = f[s], u = f[o], P = pass.teams[s];
  const limit = m.endReason === 'roundLimit', rounds = m.rounds;
  const live = r => r < rounds || (r === 500 && limit); // timeline point r is real (not carried after the end)
  const own = {};
  for (const d of t.deaths) { const c = catOf(s, d); own[c] = (own[c] || 0) + 1; }
  let selfKills = 0; for (const [c, n] of Object.entries(own)) if (!ENEMY_CATS.has(c)) selfKills += n;
  let kHInit = 0, kHRecv = 0, kBody = 0, killLen = 0;
  for (const d of u.deaths) {
    const c = catOf(o, d);
    if (c === 'Hrammed') kHInit++; else if (c === 'Hram') kHRecv++; else if (c === 'Oenemy') kBody++; else continue;
    killLen += d.len;
  }
  let trades = 0, tradeOwn = 0, tradeEnemy = 0, lostToEnemyLen = 0;
  for (const d of t.deaths) {
    const c = catOf(s, d);
    if (c === 'Hram') { trades++; tradeOwn += d.len; tradeEnemy += d.hitLen; }
    else if (c === 'Hrammed') { trades++; tradeOwn += d.len; tradeEnemy += d.byLen; }
    if (ENEMY_CATS.has(c)) lostToEnemyLen += d.len;
  }
  let selfExit = 0, selfTrapped = 0, ramExit = 0, ramTrapped = 0;
  for (const [c, [a, b]] of Object.entries(P.exit)) {
    if (!ENEMY_CATS.has(c)) { selfExit += a; selfTrapped += b; }
    else if (c === 'Hram') { ramExit += a; ramTrapped += b; }
  }
  const eatBy = k => sum(P.eat[k] || []);
  const units = {}, longest = {}, total = {};
  for (const r of TL_R) { const p = t.timeline[r / 10]; units[r] = live(r) ? p.units : null; longest[r] = live(r) ? p.longest : null; total[r] = live(r) ? p.total : null; }
  let peakUnits = 0, merge15 = null;
  for (const p of t.timeline) {
    if (!live(p.r)) continue;
    if (p.units > peakUnits) peakUnits = p.units;
    if (merge15 === null && p.r > 0 && p.longest >= 15) merge15 = p.r;
  }
  const children = t.splits.map(sp => sp[2]);
  const lastD = t.deaths.length ? t.deaths[t.deaths.length - 1] : null;
  const win = m.winner === s ? 1 : m.winner === o ? 0 : 0.5;
  return {
    key: m.battleId + ':' + m.gameId, battle: m.battleId, map: m.map, side: s,
    team: m.teams[s].name, opp: m.teams[o].name, elo: m.teams[s].elo, oppElo: m.teams[o].elo,
    win, limit, rounds, rush: win === 1 && !limit && rounds <= 100 ? 1 : 0, earlyEnd: !limit && rounds <= 100 ? 1 : 0,
    elimWin: win === 1 && !limit ? 1 : 0, firstMover: pass.firstMover === s ? 1 : 0,
    splits: t.splits.length, children, child2: children.filter(c => c === 2).length, split10: t.splits.filter(sp => sp[0] < 10).length,
    own, selfKills, suicides: own.A_suicide || 0, deaths: t.deaths.length,
    selfExit, selfTrapped, ramExit, ramTrapped,
    kHInit, kHRecv, kBody, kills: kHInit + kHRecv + kBody, killLen, trades, tradeOwn, tradeEnemy, lostToEnemyLen,
    finUnits: m.final[s].dragonCount, finLongest: m.final[s].longestDragon, finTotal: m.final[s].totalLength,
    oppFinLongest: m.final[o].longestDragon, oppFinUnits: m.final[o].dragonCount,
    units, longest, total, peakUnits, merge15, merge15Never: limit && merge15 === null ? 1 : 0,
    eaten: sum(t.eaten), eatenEarly: t.eaten[0] + t.eaten[1],
    eatNatural: eatBy('natural') + eatBy('initial'), eatOwnSelf: eatBy('ownSelf'), eatOwnKilled: eatBy('ownKilled'),
    eatOppSelf: eatBy('oppSelf'), eatOppKilled: eatBy('oppKilled'), eatTotal: sum(P.eatAll),
    kingLate: P.king[3] + P.king[4], eatLate: P.eatAll[3] + P.eatAll[4], kingAll: sum(P.king),
    dropSelfN: P.drops.self.n, dropSelfOwn: P.drops.self.own, dropSelfOpp: P.drops.self.opp,
    sprints: sum(t.sprints), pings: sum(t.sonar.sent), dr: t.sonar.dragonRounds, exitByCat: P.exit,
    lastDeathCat: lastD ? catOf(s, lastD) : null, lastDeathLen: lastD ? lastD.len : null,
  };
}

// Team (or group) aggregate of team-game rows. Rates are pooled (sum / sum); medians are over games.
function aggregate(list) {
  const n = list.length; if (!n) return { games: 0 };
  const S = k => sum(list.map(g => g[k])), lim = list.filter(g => g.limit);
  const kills = S('kills'), selfCats = {};
  for (const g of list) for (const [c, v] of Object.entries(g.own)) if (!ENEMY_CATS.has(c)) selfCats[c] = (selfCats[c] || 0) + v;
  const methods = Object.entries(selfCats).sort((a, b) => b[1] - a[1]);
  const liveMed = (k, r) => median(list.map(g => g[k][r]));
  return {
    games: n, wins: S('win'), winRate: S('win') / n, eloMedian: median(list.map(g => g.elo)),
    splitsPerGame: S('splits') / n, childMedian: median(list.flatMap(g => g.children)), child2Share: ratio(S('child2'), S('splits')),
    split10PerGame: S('split10') / n,
    selfKillPerGame: S('selfKills') / n, suicidePerGame: S('suicides') / n, selfKillPer100DR: 100 * ratio(S('selfKills'), S('dr')),
    selfKillShareOfDeaths: ratio(S('selfKills'), S('deaths')), selfExitShare: ratio(S('selfExit'), S('selfExit') + S('selfTrapped')),
    selfMethod: methods.length ? methods[0][0] : null, selfMethodShare: methods.length ? methods[0][1] / S('selfKills') : null,
    selfMethods: Object.fromEntries(methods.map(([c, v]) => [c, r3(v / S('selfKills'))])),
    limitGames: lim.length, finalUnits500: median(lim.map(g => g.finUnits)), finalLongest500: median(lim.map(g => g.finLongest)),
    finalConc500: median(lim.map(g => (g.finTotal ? g.finLongest / g.finTotal : null))),
    killsPerGame: kills / n, killHeadShare: ratio(S('kHInit') + S('kHRecv'), kills), killBodyPerGame: S('kBody') / n,
    ramInitShare: ratio(S('kHInit'), S('kHInit') + S('kHRecv')), ramExitShare: ratio(S('ramExit'), S('ramExit') + S('ramTrapped')),
    tradesPerGame: S('trades') / n, tradeLenBalance: ratio(S('tradeEnemy') - S('tradeOwn'), S('trades')),
    tradeOwnLen: ratio(S('tradeOwn'), S('trades')), tradeEnemyLen: ratio(S('tradeEnemy'), S('trades')),
    killLenPerGame: S('killLen') / n, lostToEnemyLenPerGame: S('lostToEnemyLen') / n,
    pingsPerDR: ratio(S('pings'), S('dr')), noPingGames: list.filter(g => g.pings === 0).length,
    brokenLikeGames: list.filter(g => g.pings === 0 && g.splits <= 3).length, // the SSS signature
    earlyRushShare: S('rush') / n, earlyEndShare: S('earlyEnd') / n, elimWinShare: S('elimWin') / n, limitShare: lim.length / n,
    peakUnits: median(list.map(g => g.peakUnits)),
    units100: liveMed('units', 100), units200: liveMed('units', 200), units300: liveMed('units', 300), units400: liveMed('units', 400),
    longest200: liveMed('longest', 200), longest300: liveMed('longest', 300), longest400: liveMed('longest', 400),
    conc400: median(list.map(g => (g.total[400] ? g.longest[400] / g.total[400] : null))),
    merge15: median(lim.map(g => (g.merge15 === null ? 999 : g.merge15))), merge15NeverShare: lim.length ? S('merge15Never') / lim.length : null,
    eatenPerGame: S('eaten') / n, eatenPer100DR: 100 * ratio(S('eaten'), S('dr')),
    ownCorpseEatShare: ratio(S('eatOwnSelf') + S('eatOwnKilled'), S('eatTotal')), selfCorpseEatShare: ratio(S('eatOwnSelf'), S('eatTotal')),
    oppCorpseEatShare: ratio(S('eatOppSelf') + S('eatOppKilled'), S('eatTotal')),
    selfDropEatenOwnShare: ratio(S('dropSelfOwn'), S('dropSelfN')), selfDropEatenOppShare: ratio(S('dropSelfOpp'), S('dropSelfN')),
    kingEatShareLate: ratio(S('kingLate'), S('eatLate')), kingEatShareAll: ratio(S('kingAll'), S('eatTotal')),
    sprintsPer100DR: 100 * ratio(S('sprints'), S('dr')),
  };
}

// ---------------------------------------------------------------------------------------------------------------
// Main: load the snapshot, parse replays in workers, build the tables.
function runPool(tasks, jobs, onResult) {
  if (!tasks.length) return Promise.resolve();
  const queue = tasks.slice();
  return new Promise((resolve, reject) => {
    let live = Math.min(jobs, queue.length);
    for (let i = 0, n = live; i < n; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced', stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
      let finished = false;
      const next = () => {
        const t = queue.shift();
        if (!t) { finished = true; w.disconnect(); if (--live === 0) resolve(); return; }
        w.send(t);
      };
      w.on('message', m => { onResult(m); next(); });
      w.on('error', reject);
      w.on('exit', code => { if (!finished) reject(Error('worker exited unexpectedly with code ' + code)); });
      next();
    }
  });
}

async function collect(opts) {
  const keys = fs.readFileSync(opts.keysFile, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  const want = new Set(keys), feat = new Map();
  for (const l of fs.readFileSync(path.join(ROOT, 'data', 'top', 'features.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue;
    const m = /^\{"meta":\{"battleId":(\d+),"gameId":(\d+)[,}]/.exec(l);
    let k = m ? m[1] + ':' + m[2] : null, row = null;
    if (!k) { try { row = JSON.parse(l); k = row.meta.battleId + ':' + row.meta.gameId; } catch { continue; } }
    if (want.has(k) && !feat.has(k)) feat.set(k, row || JSON.parse(l));
  }
  const missing = keys.filter(k => !feat.has(k));
  if (missing.length) throw Error(`features.jsonl lacks ${missing.length} snapshot games, e.g. ${missing.slice(0, 3).join(' ')}`);
  const localRows = [], seen = new Set();
  for (const l of fs.readFileSync(path.join(opts.localDir, 'rows.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue;
    const r = JSON.parse(l);
    if (r.G === undefined || seen.has(r.key)) continue; // same rule as tools/eval.js: first complete row per key
    seen.add(r.key); localRows.push(r);
  }
  const tasks = [];
  for (const k of keys) {
    const f = feat.get(k);
    tasks.push({ kind: 'top', key: k, file: path.join(ROOT, 'data', 'top', String(f.meta.battleId), f.meta.gameId + '.replay.gz'), deaths: { A: f.A.deaths, B: f.B.deaths } });
  }
  for (const r of localRows) {
    tasks.push({ kind: 'local', key: 'local:' + r.key, file: path.join(opts.localDir, 'games', r.key.replace(/:/g, '_'), 'game.replay'),
      row: { battleId: 'local', gameId: r.key, map: r.map, teamA: r.side === 'A' ? 'r1' : r.opp, teamB: r.side === 'B' ? 'r1' : r.opp } });
  }
  let cache = {};
  if (opts.cacheFile && fs.existsSync(opts.cacheFile)) cache = JSON.parse(fs.readFileSync(opts.cacheFile, 'utf8'));
  const todo = tasks.filter(t => !cache[t.key]), errors = [];
  let done = 0;
  await runPool(todo, opts.jobs, m => {
    if (m.error) { errors.push(m.key + ' ' + m.error); return; }
    cache[m.key] = { pass: m.pass, map: m.map, f: m.f };
    if (++done % 100 === 0 && !opts.quiet) console.error(`  parsed ${done}/${todo.length} replays`);
  });
  if (errors.length) throw Error(`${errors.length} replays failed: ${errors.slice(0, 3).join(' ; ')}`);
  if (opts.cacheFile && todo.length) fs.writeFileSync(opts.cacheFile, JSON.stringify(cache));
  return { keys, feat, localRows, res: cache };
}

// Teams kept out of the main set (reported separately). SSS: 14 of its 19 snapshot games show no sonar and at most 3
// splits (the "broken" signature below); its other games look normal but are excluded too, so every table uses one set.
const EXCLUDED_TEAMS = ['SSS'];
const MIN_TEAM_GAMES = 10; // teams with fewer main-set games get no style vector / group

function analyse(data, opts) {
  const { keys, feat, localRows, res } = data;
  const checks = { mapSigConflicts: 0, mapFileMismatch: 0, unmatchedDeaths: 0, unknownEater: 0, unknownPearl: 0, eatenMismatch: 0,
    topSimMismatches: 0, topOtherChecks: 0, localSimMismatches: 0, localOtherChecks: 0, localWinnerMismatch: 0 };
  // --- maps: local replays were played on maps/online-20260927, so their signature is the file version. A top replay
  // with another signature under the same name is a map variant (Prisoners Dilemma has one), labelled "<name> [<k>]"
  // with k = starting dragons per team. ---
  const fileSig = new Map(), variants = new Map(), maps = {};
  for (const lr of localRows) {
    const mf = res['local:' + lr.key].map;
    if (!fileSig.has(mf.name)) fileSig.set(mf.name, mf);
    else if (fileSig.get(mf.name).sig !== mf.sig) checks.mapSigConflicts++;
  }
  const variantOf = mf => {
    const base = fileSig.get(mf.name);
    const label = base && base.sig === mf.sig ? mf.name : `${mf.name} [${mf.initDragonsPerTeam}]`;
    if (!variants.has(label)) variants.set(label, { name: mf.name, label, fileVersion: label === mf.name, features: mf });
    else if (variants.get(label).features.sig !== mf.sig) checks.mapSigConflicts++;
    return label;
  };
  const passChecks = (p, f) => {
    for (const k of ['unmatchedDeaths', 'unknownEater', 'unknownPearl']) checks[k] += p.checks[k];
    for (const s of TEAMS) if (sum(p.teams[s].eatAll) !== sum(f[s].eaten)) checks.eatenMismatch++;
  };
  // --- top games ---
  const main = [], sss = [];
  for (const k of keys) {
    const f = feat.get(k), r = res[k];
    passChecks(r.pass, f);
    checks.topSimMismatches += f.meta.simMismatches;
    const c = f.meta.checks;
    checks.topOtherChecks += c.deaths + c.splits + c.eaten + c.drops + c.hitKind + c.pings + (c.finalMatch ? 0 : 1) + (c.winnerMatch ? 0 : 1);
    const names = TEAMS.map(s => f.meta.teams[s].name);
    const variant = variantOf(r.map);
    const rows = TEAMS.map(s => { const g = teamGame(f, s, r.pass); g.mapVariant = variant; return g; });
    if (names.some(n => EXCLUDED_TEAMS.includes(n))) sss.push(...rows); else main.push(...rows);
  }
  // --- local games: our side (team 'r1') and the local opponent side ---
  const ours = [], localOpp = [];
  for (const lr of localRows) {
    const r = res['local:' + lr.key], f = r.f;
    f.meta.map = r.map.name;
    variantOf(r.map); passChecks(r.pass, f);
    checks.localSimMismatches += f.meta.simMismatches;
    const c = f.meta.checks;
    checks.localOtherChecks += c.deaths + c.splits + c.eaten + c.drops + c.hitKind + c.pings + (c.finalMatch ? 0 : 1);
    if ((f.meta.winner === lr.side) !== !!lr.won) checks.localWinnerMismatch++;
    const us = teamGame(f, lr.side, r.pass), them = teamGame(f, other(lr.side), r.pass);
    us.localOpp = lr.opp; them.localOpp = lr.opp; them.team = lr.opp;
    us.mapVariant = them.mapVariant = r.map.name;
    ours.push(us); localOpp.push(them);
  }
  for (const [name, base] of fileSig) {
    const file = path.join(ROOT, 'maps', 'online-20260927', name.toLowerCase().replace(/ /g, '_') + '.map');
    const x = mapFileFeatures(file), rs = base.replaySpawn;
    if (x.kelp !== base.kelpEdges || x.portalEdges !== base.portalEdges || x.dragons !== 2 * base.initDragonsPerTeam || !rs ||
      rs.spawnTiles !== x.spawnTiles || Math.abs(rs.spawnCapPerRound - x.spawnCapPerRound) > 1e-9 || rs.fountainTiles !== x.fountainTiles) checks.mapFileMismatch++;
    maps[name] = { file: path.relative(ROOT, file), spawn: x };
  }
  for (const v of variants.values()) {
    const { sig, replaySpawn, ...geo } = v.features;
    const sp = maps[v.name] ? maps[v.name].spawn : {};
    v.features = { ...geo, spawnTiles: sp.spawnTiles, spawnTileShare: sp.spawnTileShare, spawnCapPerRound: sp.spawnCapPerRound, spawnCapPer100Tiles: sp.spawnCapPer100Tiles, fountainTiles: sp.fountainTiles };
  }
  return { keys, main, sss, ours, localOpp, maps, variants, checks, opts, feat };
}
function rankOf(feat, name) {
  for (const f of feat.values()) for (const s of TEAMS) if (f.meta.teams[s].name === name) return f.meta.teams[s].rank;
  return null;
}

// ---------------------------------------------------------------------------------------------------------------
// Tables. Style rule (two independent axes; thresholds sit in visible gaps of the team distribution, printed below):
//  plan  = end concentration (longest / total length at round 500) in the team's WON 500-round games, map-adjusted:
//          per map, the team's median minus the median over all won 500-round games on that map, averaged over maps
//          weighted by the team's won 500-round games there. K ("concentrates more than other winners on the same map")
//          if >= +0.08, N otherwise; no label with fewer than 3 such wins. Won games because in lost games the end shape
//          mostly reflects what the opponent destroyed; map-adjusted because winners' concentration differs by map
//          (0.22 Schooltime .. 0.76 Autarky) and teams play different map mixes.
//          The unadjusted rule (median >= 0.5 -> K, else D) is kept as planRaw for comparison.
//  sonar = pings per dragon-round over all games: full >= 3.5, mid >= 2, low < 2.
const PLAN_MIN_WINS = 3, PLAN_RESID = 0.08, PLAN_RAW = 0.5, SONAR_FULL = 3.5, SONAR_MID = 2;
function styleOf(all, wins, concAdj) {
  const plan = wins.limitGames >= PLAN_MIN_WINS && concAdj !== null ? (concAdj >= PLAN_RESID ? 'K' : 'N') : null;
  const planRaw = wins.limitGames >= PLAN_MIN_WINS ? (wins.finalConc500 >= PLAN_RAW ? 'K' : 'D') : null;
  const sonar = all.pingsPerDR >= SONAR_FULL ? 'full' : all.pingsPerDR >= SONAR_MID ? 'mid' : 'low';
  return { plan, planRaw, sonar };
}
// Map adjustment: games-weighted mean over maps of (value on that map - baseline on that map). Metrics measured on
// 500-round games are weighted by those games. basis 'wins' compares won games with won games.
const LIMIT_METRICS = new Set(['finalConc500', 'finalUnits500', 'finalLongest500', 'merge15']);
function mapAdjusted(rows, baseline, metric, basis) {
  const sel = basis === 'wins' ? rows.filter(g => g.win === 1) : rows, byMap = new Map();
  for (const g of sel) { if (!byMap.has(g.map)) byMap.set(g.map, []); byMap.get(g.map).push(g); }
  let num = 0, den = 0;
  for (const [map, list] of byMap) {
    const a = aggregate(list), v = a[metric], b = baseline[basis][map] ? baseline[basis][map][metric] : null;
    const w = LIMIT_METRICS.has(metric) ? a.limitGames : list.length;
    if (v === null || v === undefined || b === null || b === undefined || !w) continue;
    num += w * (v - b); den += w;
  }
  return den ? num / den : null;
}
// Style vector (all games) as asked, plus stable fingerprints and plan metrics measured in won games.
const VECTOR = ['splitsPerGame', 'childMedian', 'child2Share', 'selfKillPerGame', 'selfKillPer100DR', 'selfExitShare', 'suicidePerGame',
  'finalUnits500', 'finalLongest500', 'finalConc500', 'limitGames', 'killsPerGame', 'killHeadShare', 'killBodyPerGame', 'ramInitShare', 'ramExitShare',
  'tradeLenBalance', 'pingsPerDR', 'earlyRushShare', 'earlyEndShare', 'peakUnits', 'units100', 'units200', 'units400', 'merge15', 'eatenPer100DR',
  'ownCorpseEatShare', 'kingEatShareLate', 'sprintsPer100DR', 'selfMethod', 'selfMethodShare', 'noPingGames', 'brokenLikeGames'];
const WIN_PROFILE = ['limitGames', 'finalConc500', 'finalUnits500', 'finalLongest500', 'units200', 'peakUnits', 'merge15', 'splitsPerGame', 'selfKillPer100DR'];
const pick = (o, ks) => Object.fromEntries(ks.map(k => [k, typeof o[k] === 'number' ? r3(o[k]) : o[k] === undefined ? null : o[k]]));
// Win/loss stability: across teams, correlation of a metric's value in wins with its value in losses, and the mean
// |win - loss| gap relative to the across-team SD (below 1 = teams differ more than their own wins and losses do).
const STABILITY = ['pingsPerDR', 'sprintsPer100DR', 'suicidePerGame', 'ramInitShare', 'selfExitShare', 'child2Share', 'units400', 'conc400', 'merge15',
  'finalUnits500', 'finalConc500', 'eatenPer100DR', 'selfKillPer100DR', 'tradeLenBalance', 'kingEatShareLate', 'finalLongest500', 'units200',
  'splitsPerGame', 'selfKillPerGame', 'killsPerGame', 'units100', 'peakUnits'];
// Our bot vs the top teams. basis 'all' = all games; 'wins' = won games only (our local games are 87% wins, so for
// outcome-driven metrics the fair comparison is the top teams' wins). kind: intrinsic (own choices) / interaction.
const COMPARE = [
  ['splitsPerGame', 'all', 'interaction'], ['childMedian', 'all', 'intrinsic'], ['child2Share', 'all', 'intrinsic'],
  ['selfKillPer100DR', 'all', 'interaction'], ['selfExitShare', 'all', 'intrinsic'], ['pingsPerDR', 'all', 'intrinsic'],
  ['sprintsPer100DR', 'all', 'intrinsic'], ['peakUnits', 'wins', 'interaction'], ['units200', 'wins', 'interaction'],
  ['merge15', 'wins', 'interaction'], ['finalConc500', 'wins', 'interaction'], ['finalUnits500', 'wins', 'interaction'],
  ['finalLongest500', 'wins', 'interaction'], ['killHeadShare', 'all', 'interaction'], ['ramInitShare', 'all', 'interaction'],
  ['earlyRushShare', 'all', 'interaction'], ['eatenPer100DR', 'all', 'interaction'], ['ownCorpseEatShare', 'all', 'interaction'],
];
const DISTANCE = ['child2Share', 'selfExitShare', 'pingsPerDR', 'sprintsPer100DR', 'units200', 'merge15', 'finalConc500', 'finalUnits500'];
const basisOf = m => (COMPARE.find(c => c[0] === m) || [m, 'all'])[1];
// Winner vs loser inside each game (paired). null values (game already over at that round) drop the pair.
const WL = [
  ['splits', g => g.splits], ['selfKills', g => g.selfKills], ['selfKillPer100DR', g => (g.dr ? 100 * g.selfKills / g.dr : null)],
  ['units50', g => g.units[50]], ['units100', g => g.units[100]], ['units200', g => g.units[200]],
  ['longest100', g => g.longest[100]], ['longest200', g => g.longest[200]],
  ['eatenFirst100', g => g.eatenEarly], ['eaten', g => g.eaten], ['pingsPerDR', g => (g.dr ? g.pings / g.dr : null)], ['kills', g => g.kills],
  ['killedEnemyLen', g => g.killLen], ['lostToEnemyLen', g => g.lostToEnemyLen],
];

function gamePairs(rows) {
  const m = new Map();
  for (const g of rows) { if (!m.has(g.key)) m.set(g.key, {}); m.get(g.key)[g.side] = g; }
  return [...m.values()].filter(p => p.A && p.B);
}
const winnerOf = p => (p.A.win === 1 ? p.A : p.B.win === 1 ? p.B : null), loserOf = p => (p.A.win === 1 ? p.B : p.B.win === 1 ? p.A : null);
function quant(xs) { return { n: xs.length, min: quantile(xs, 0), p25: quantile(xs, 0.25), median: median(xs), p75: quantile(xs, 0.75), max: quantile(xs, 1) }; }

function mapStats(list) {
  const n = list.length, lim = list.filter(p => p.A.limit), el = list.filter(p => !p.A.limit);
  const W = winnerOf, L = loserOf;
  const decided = list.filter(p => W(p));
  const fm = decided.filter(p => p.A.firstMover || p.B.firstMover);
  return {
    games: n, rounds: quant(list.map(p => p.A.rounds)), elimShare: r3(el.length / n),
    endBy100: el.filter(p => p.A.rounds <= 100).length, endBy200: el.filter(p => p.A.rounds <= 200).length,
    limit: { games: lim.length, winnerLongest: median(lim.map(p => W(p).finLongest)), loserLongest: median(lim.map(p => L(p).finLongest)),
      marginLongest: median(lim.map(p => W(p).finLongest - L(p).finLongest)), winnerTotal: median(lim.map(p => W(p).finTotal)),
      loserTotal: median(lim.map(p => L(p).finTotal)), winnerUnits: median(lim.map(p => W(p).finUnits)), loserUnits: median(lim.map(p => L(p).finUnits)),
      winnerConc: r3(median(lim.map(p => (W(p).finTotal ? W(p).finLongest / W(p).finTotal : null)))),
      winnerMoreTotalShare: lim.length ? r3(lim.filter(p => W(p).finTotal > L(p).finTotal).length / lim.length) : null,
      decidedByTotal: lim.filter(p => W(p).finLongest === L(p).finLongest).length },
    elim: { games: el.length, roundsMedian: median(el.map(p => p.A.rounds)), winnerUnits: median(el.map(p => W(p).finUnits)),
      winnerLongest: median(el.map(p => W(p).finLongest)), winnerTotal: median(el.map(p => W(p).finTotal)),
      loserLastDeath: el.reduce((o, p) => { const c = L(p) && L(p).lastDeathCat; if (c) o[c] = (o[c] || 0) + 1; return o; }, {}),
      loserLastDeathLen: median(el.map(p => L(p) && L(p).lastDeathLen)) },
    interaction: { enemyDeathsPerGame: median(list.map(p => p.A.kills + p.B.kills)), tradesPerGame: median(list.map(p => p.A.trades)),
      bodyBlockKills: sum(list.map(p => p.A.kBody + p.B.kBody)), gamesWithoutContact: list.filter(p => p.A.kills + p.B.kills === 0).length },
    selfKillsPerTeamGame: median(list.flatMap(p => [p.A.selfKills, p.B.selfKills])),
    firstMoverWins: fm.filter(p => W(p).firstMover).length, firstMoverGames: fm.length,
  };
}
function winnerVsLoser(list) {
  const out = {};
  for (const [name, f] of WL) {
    let n = 0, hi = 0; const wv = [], lv = [];
    for (const p of list) {
      const w = winnerOf(p), l = loserOf(p); if (!w) continue;
      const a = f(w), b = f(l); if (a === null || b === null || a === undefined || b === undefined) continue;
      n++; wv.push(a); lv.push(b); hi += a > b ? 1 : a === b ? 0.5 : 0;
    }
    out[name] = { n, winnerMedian: r3(median(wv)), loserMedian: r3(median(lv)), winnerHigherShare: n ? r3(hi / n) : null };
  }
  return out;
}
function matchupTable(pairs, labelOf) {
  const cells = {};
  for (const p of pairs) {
    const la = labelOf(p.A.team), lb = labelOf(p.B.team); if (!la || !lb) continue;
    for (const [x, y, lx, ly] of [[p.A, p.B, la, lb], [p.B, p.A, lb, la]]) {
      const k = lx + ' vs ' + ly;
      (cells[k] || (cells[k] = [])).push({ cluster: x.battle, win: x.win, exp: eloExpect(x.elo, y.elo), pair: [x.team, y.team].sort().join(' / ') });
    }
  }
  const out = {};
  for (const [k, items] of Object.entries(cells)) {
    const [a, b] = k.split(' vs ');
    if (a === b) { out[k] = { games: items.length / 2, note: 'same style: win rate 0.5 by construction' }; continue; }
    const pairCount = {}; for (const it of items) pairCount[it.pair] = (pairCount[it.pair] || 0) + 1;
    const top = Object.entries(pairCount).sort((x, y) => y[1] - x[1])[0];
    out[k] = { games: items.length, wins: sum(items.map(i => i.win)), winRate: r3(mean(items.map(i => i.win))), eloExpected: r3(mean(items.map(i => i.exp))),
      ci95: (clusterBootWin(items) || []).map(r3), battles: new Set(items.map(i => i.cluster)).size, teamPairs: Object.keys(pairCount).length,
      topPair: top[0], topPairShare: r3(top[1] / items.length) };
  }
  return out;
}

// Excess over Elo (observed - expected win rate) of style a vs style b on long maps minus the same on short maps.
// Battles are resampled with replacement (a battle can hold games of both families).
function familyContrast(pairs, labelOf, a, b, longMaps, reps = 4000, seed = 17) {
  const items = [];
  for (const p of pairs) for (const [x, y] of [[p.A, p.B], [p.B, p.A]]) {
    if (labelOf(x.team) !== a || labelOf(y.team) !== b) continue;
    items.push({ battle: x.battle, fam: longMaps.includes(x.map) ? 'long' : 'short', ex: x.win - eloExpect(x.elo, y.elo) });
  }
  const stat = list => {
    const l = list.filter(i => i.fam === 'long'), sh = list.filter(i => i.fam === 'short');
    return l.length && sh.length ? { long: mean(l.map(i => i.ex)), short: mean(sh.map(i => i.ex)), nLong: l.length, nShort: sh.length } : null;
  };
  const obs = stat(items); if (!obs) return null;
  const byB = new Map(); for (const it of items) { if (!byB.has(it.battle)) byB.set(it.battle, []); byB.get(it.battle).push(it); }
  const bl = [...byB.values()], rand = rng(seed), diffs = [];
  for (let k = 0; k < reps; k++) {
    const sample = []; for (let i = 0; i < bl.length; i++) sample.push(...bl[Math.floor(rand() * bl.length)]);
    const st = stat(sample); if (st) diffs.push(st.long - st.short);
  }
  return { gamesLong: obs.nLong, gamesShort: obs.nShort, excessLong: r3(obs.long), excessShort: r3(obs.short), difference: r3(obs.long - obs.short),
    ci95: [r3(quantile(diffs, 0.025)), r3(quantile(diffs, 0.975))], battles: bl.length };
}
// Does a team's win rate depend on the map more than chance? Statistic: sum over maps of (w - n p)^2 / (n p (1 - p)),
// p = the team's overall win rate; map labels are shuffled among the team's own games (opponents stay with games).
function mapSpecialization(list, perms = 10000, seed = 5) {
  const n = list.length, p = mean(list.map(g => g.win));
  if (!(p > 0 && p < 1)) return null;
  const maps = list.map(g => g.map), wins = list.map(g => g.win);
  const stat = ms => { const c = new Map(); ms.forEach((m, i) => { const x = c.get(m) || [0, 0]; x[0] += wins[i]; x[1]++; c.set(m, x); }); let s2 = 0; for (const [w, k] of c.values()) s2 += (w - k * p) ** 2 / (k * p * (1 - p)); return s2; };
  const obs = stat(maps), rand = rng(seed), ms = maps.slice(); let hit = 0; const null_ = [];
  for (let k = 0; k < perms; k++) { for (let i = ms.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [ms[i], ms[j]] = [ms[j], ms[i]]; } const v = stat(ms); null_.push(v); if (v >= obs - 1e-12) hit++; }
  return { games: n, stat: r2(obs), nullMedian: r2(median(null_)), p: r4((hit + 1) / (perms + 1)) };
}

function tables(base) {
  const { keys, main, sss, ours, localOpp, maps, variants, checks, feat } = base;
  const pairs = gamePairs(main);
  // ---------- teams: style vectors and labels ----------
  const byTeam = new Map();
  for (const g of main) { if (!byTeam.has(g.team)) byTeam.set(g.team, []); byTeam.get(g.team).push(g); }
  const baseline = { all: {}, wins: {} };
  for (const map of new Set(main.map(g => g.map))) {
    const rows = main.filter(g => g.map === map);
    baseline.all[map] = aggregate(rows); baseline.wins[map] = aggregate(rows.filter(g => g.win === 1));
  }
  const teams = {}, aggAll = {}, aggWins = {}, aggLoss = {}, adjusted = {};
  for (const [name, list] of byTeam) {
    const all = aggregate(list), wins = aggregate(list.filter(g => g.win === 1)), loss = aggregate(list.filter(g => g.win === 0));
    aggAll[name] = all; aggWins[name] = wins; aggLoss[name] = loss;
    adjusted[name] = Object.fromEntries(DISTANCE.map(m => [m, mapAdjusted(list, baseline, m, basisOf(m))]));
    const grouped = list.length >= MIN_TEAM_GAMES;
    teams[name] = { games: list.length, wins: all.wins, winRate: r3(all.winRate), eloMedian: all.eloMedian, rank: rankOf(feat, name), grouped,
      style: grouped ? styleOf(all, wins, adjusted[name].finalConc500) : { plan: null, planRaw: null, sonar: null }, vector: pick(all, VECTOR),
      winsProfile: pick(wins, WIN_PROFILE), lossProfile: pick(loss, WIN_PROFILE), mapAdjusted: pick(adjusted[name], DISTANCE), selfMethods: all.selfMethods };
  }
  const grouped = Object.keys(teams).filter(n => teams[n].grouped).sort((a, b) => teams[b].eloMedian - teams[a].eloMedian);
  const stability = {};
  for (const m of STABILITY) {
    const ok = grouped.filter(n => aggWins[n][m] !== null && aggLoss[n][m] !== null && aggWins[n][m] !== undefined && aggLoss[n][m] !== undefined);
    const x = ok.map(n => aggWins[n][m]), y = ok.map(n => aggLoss[n][m]), all = grouped.map(n => aggAll[n][m]).filter(v => v !== null);
    const mu = mean(all), sd = Math.sqrt(sum(all.map(v => (v - mu) ** 2)) / (all.length - 1));
    const gap = mean(ok.map(n => Math.abs(aggWins[n][m] - aggLoss[n][m])));
    stability[m] = { teams: ok.length, rWinLoss: r3(pearson(x, y)), teamSD: r3(sd), meanWinLossGap: r3(gap), gapOverSD: r3(gap / sd) };
  }
  const ruleEvidence = {
    planConcInWinsAdjusted: grouped.map(n => [n, r3(adjusted[n].finalConc500), aggWins[n].limitGames, r3(aggWins[n].finalConc500)])
      .sort((a, b) => (a[1] === null ? -9 : a[1]) - (b[1] === null ? -9 : b[1])),
    winnerConcByMap: Object.fromEntries(Object.entries(baseline.wins).map(([k, v]) => [k, r3(v.finalConc500)])),
    pingsPerDR: grouped.map(n => [n, r3(aggAll[n].pingsPerDR)]).sort((a, b) => a[1] - b[1]),
  };
  const planOf = n => (teams[n] && teams[n].style.plan) || null, sonarOf = n => (teams[n] && teams[n].style.sonar) || null;
  const planRawOf = n => (teams[n] && teams[n].style.planRaw) || null;
  const groupMembers = { plan: {}, sonar: {} };
  for (const n of grouped) {
    const st = teams[n].style;
    if (st.plan) (groupMembers.plan[st.plan] || (groupMembers.plan[st.plan] = [])).push(n);
    (groupMembers.sonar[st.sonar] || (groupMembers.sonar[st.sonar] = [])).push(n);
  }
  const groupProfile = {};
  for (const [axis, groups] of Object.entries(groupMembers)) for (const [lab, members] of Object.entries(groups)) {
    const rows = main.filter(g => members.includes(g.team));
    const a = aggregate(rows), w = aggregate(rows.filter(g => g.win === 1));
    groupProfile[axis + ':' + lab] = { teams: members.length, members, games: rows.length, winRate: r3(a.winRate), eloMedian: median(members.map(n => teams[n].eloMedian)),
      all: pick(a, VECTOR), wins: pick(w, WIN_PROFILE) };
  }
  // ---------- matchups ----------
  const matchups = { plan: matchupTable(pairs, planOf), sonar: matchupTable(pairs, sonarOf), planRaw: matchupTable(pairs, planRawOf) };
  matchups.combined = matchupTable(pairs, n => (planOf(n) ? planOf(n) + '-' + sonarOf(n) : null));
  const h2hMap = new Map();
  for (const p of pairs) {
    const [a, b] = [p.A.team, p.B.team].sort(), k = a + '\u0000' + b;
    const x = h2hMap.get(k) || { a, b, games: 0, aWins: 0, battles: new Set(), maps: {} };
    x.games++; x.aWins += (p.A.team === a ? p.A.win : p.B.win); x.battles.add(p.A.battle); x.maps[p.A.map] = (x.maps[p.A.map] || 0) + 1;
    h2hMap.set(k, x);
  }
  const h2h = [...h2hMap.values()].filter(x => x.games >= 3).map(x => ({ ...x, battles: x.battles.size }))
    .sort((x, y) => y.games - x.games || (x.a < y.a ? -1 : 1));
  // ---------- maps ----------
  const mapNames = [...new Set(pairs.map(p => p.A.map))].sort();
  const mapTable = {};
  for (const name of mapNames) {
    const list = pairs.filter(p => p.A.map === name);
    const vs = [...new Set(list.map(p => p.A.mapVariant))].sort();
    const entry = { spawn: maps[name] ? maps[name].spawn : null, file: maps[name] ? maps[name].file : null, stats: mapStats(list), winnerVsLoser: winnerVsLoser(list), variants: {} };
    for (const v of vs) entry.variants[v] = { features: variants.get(v).features, fileVersion: variants.get(v).fileVersion, stats: mapStats(list.filter(p => p.A.mapVariant === v)) };
    entry.family = entry.stats.rounds.median >= 500 ? 'long' : 'short';
    entry.planKvsN = matchupTable(list, planOf)['K vs N'] || null;
    entry.planRawKvsD = matchupTable(list, planRawOf)['K vs D'] || null;
    const sm = matchupTable(list, sonarOf);
    entry.sonar = Object.fromEntries(['full vs low', 'full vs mid', 'mid vs low'].filter(k => sm[k]).map(k => [k, sm[k]]));
    mapTable[name] = entry;
  }
  // Map families by median game length (long: median 500 rounds; short: below 500).
  const families = {};
  for (const fam of ['long', 'short']) {
    const names = mapNames.filter(n => mapTable[n].family === fam), list = pairs.filter(p => names.includes(p.A.map));
    const sm = matchupTable(list, sonarOf);
    families[fam] = { maps: names, games: list.length, stats: mapStats(list), planKvsN: matchupTable(list, planOf)['K vs N'] || null,
      planRawKvsD: matchupTable(list, planRawOf)['K vs D'] || null,
      sonar: Object.fromEntries(['full vs low', 'full vs mid', 'mid vs low'].filter(k => sm[k]).map(k => [k, sm[k]])) };
  }
  const contrast = {};
  for (const [key, lab, a, b] of [['planKvsN', planOf, 'K', 'N'], ['planRawKvsD', planRawOf, 'K', 'D'], ['sonarFullVsLow', sonarOf, 'full', 'low'],
    ['sonarFullVsMid', sonarOf, 'full', 'mid'], ['sonarMidVsLow', sonarOf, 'mid', 'low']]) {
    const c = familyContrast(pairs, lab, a, b, families.long.maps);
    if (c) { // leave one team out (drop all its games): range of the long-minus-short difference
      const loto = grouped.filter(n => lab(n) === a || lab(n) === b).map(n => {
        const x = familyContrast(pairs.filter(p => p.A.team !== n && p.B.team !== n), lab, a, b, families.long.maps, 1);
        return [n, x ? x.difference : null];
      }).filter(x => x[1] !== null).sort((u, v) => u[1] - v[1]);
      c.leaveOneTeamOut = { min: loto[0], max: loto[loto.length - 1] };
    }
    contrast[key] = c;
  }
  // First mover: the team whose dragon has the smallest id moves first every round. It alternates inside battles.
  const firstMover = {};
  for (const [label, list] of [['all', pairs], ['long', pairs.filter(p => families.long.maps.includes(p.A.map))], ['short', pairs.filter(p => families.short.maps.includes(p.A.map))]]) {
    const fm = list.map(p => (p.A.firstMover ? [p.A, p.B] : [p.B, p.A]));
    const ps = fm.map(([x, y]) => eloExpect(x.elo, y.elo)), obs = sum(fm.map(([x]) => x.win)), exp = sum(ps);
    const rand = rng(99); let extreme = 0; const R = 20000;
    for (let k = 0; k < R; k++) { let w = 0; for (const q of ps) if (rand() < q) w++; if (Math.abs(w - exp) >= Math.abs(obs - exp) - 1e-9) extreme++; }
    firstMover[label] = { games: list.length, firstMoverWins: obs, eloExpected: r2(exp), firstMoverIsSideA: fm.filter(([x]) => x.side === 'A').length,
      firstMoverHigherElo: fm.filter(([x, y]) => x.elo > y.elo).length, pTwoSided: r4((extreme + 1) / (R + 1)) };
  }
  const battleSides = new Map();
  for (const p of pairs) { const b = battleSides.get(p.A.battle) || new Set(); b.add(p.A.firstMover ? 'A' : 'B'); battleSides.set(p.A.battle, b); }
  firstMover.battles = battleSides.size; firstMover.battlesWithBothSidesFirst = [...battleSides.values()].filter(x => x.size > 1).length;
  // Map features vs outcomes across map variants (descriptive only).
  const mapLevel = [];
  for (const [label, v] of variants) {
    const list = pairs.filter(p => p.A.mapVariant === label); if (!list.length) continue;
    const st = mapStats(list), f = v.features;
    mapLevel.push({ label, games: list.length, elimShare: st.elimShare, roundsMedian: st.rounds.median, winnerLongest500: st.limit.winnerLongest,
      enemyDeathsPerGame: st.interaction.enemyDeathsPerGame, area: f.area, kelpDensity: r3(f.kelpDensity), portalPairs: f.portalPairs,
      spawnCapPerRound: r2(f.spawnCapPerRound), spawnCapPer100Tiles: r2(f.spawnCapPer100Tiles), headDistMin: f.headDistMin, initLenPerTeam: f.initLenPerTeam });
  }
  mapLevel.sort((a, b) => (a.label < b.label ? -1 : 1));
  const featureCorr = {};
  for (const fx of ['area', 'kelpDensity', 'portalPairs', 'spawnCapPerRound', 'spawnCapPer100Tiles', 'headDistMin', 'initLenPerTeam'])
    for (const oy of ['elimShare', 'roundsMedian', 'enemyDeathsPerGame', 'winnerLongest500']) {
      const s = spearman(mapLevel.map(m => m[fx]), mapLevel.map(m => m[oy]), 10000, 11);
      featureCorr[fx + ' ~ ' + oy] = { n: s.n, rho: r3(s.rho), p: s.p };
    }
  // ---------- team x map ----------
  const teamMap = {}, specialization = {};
  for (const n of Object.keys(teams)) {
    teamMap[n] = {};
    for (const g of byTeam.get(n)) {
      const c = teamMap[n][g.map] || (teamMap[n][g.map] = { games: 0, wins: 0, eloExpected: 0 });
      c.games++; c.wins += g.win; c.eloExpected += eloExpect(g.elo, g.oppElo);
    }
    for (const c of Object.values(teamMap[n])) c.eloExpected = r2(c.eloExpected);
    if (byTeam.get(n).length >= 20) specialization[n] = mapSpecialization(byTeam.get(n));
  }
  { // pooled over teams with >= 20 games: sum of statistics, map labels shuffled within each team
    const names = Object.keys(specialization).filter(n => specialization[n]);
    const obs = sum(names.map(n => specialization[n].stat));
    const rand = rng(8), R = 2000; let hit = 0;
    const prep = names.map(n => { const list = byTeam.get(n), p = mean(list.map(g => g.win)); return { maps: list.map(g => g.map), wins: list.map(g => g.win), p }; });
    for (let k = 0; k < R; k++) {
      let tot = 0;
      for (const t of prep) {
        const ms = t.maps.slice(); for (let i = ms.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [ms[i], ms[j]] = [ms[j], ms[i]]; }
        const c = new Map(); ms.forEach((m, i) => { const x = c.get(m) || [0, 0]; x[0] += t.wins[i]; x[1]++; c.set(m, x); });
        for (const [w, kk] of c.values()) tot += (w - kk * t.p) ** 2 / (kk * t.p * (1 - t.p));
      }
      if (tot >= obs - 1e-9) hit++;
    }
    specialization.pooled = { teams: names.length, stat: r2(obs), p: r4((hit + 1) / (R + 1)) };
  }
  // ---------- elo / win rate vs style (teams with a style vector) ----------
  const eloVsStyle = {};
  const ELO_METRICS = ['splitsPerGame', 'child2Share', 'selfKillPer100DR', 'selfExitShare', 'suicidePerGame', 'finalUnits500', 'finalLongest500', 'finalConc500',
    'killsPerGame', 'ramInitShare', 'tradeLenBalance', 'pingsPerDR', 'sprintsPer100DR', 'earlyRushShare', 'peakUnits', 'units200', 'merge15', 'eatenPer100DR', 'kingEatShareLate'];
  for (const m of ELO_METRICS) {
    const vals = grouped.map(n => aggAll[n][m]), wv = grouped.map(n => aggWins[n][m]);
    const e = spearman(grouped.map(n => teams[n].eloMedian), vals), w = spearman(grouped.map(n => teams[n].winRate), vals);
    const ew = spearman(grouped.map(n => teams[n].eloMedian), wv);
    eloVsStyle[m] = { n: e.n, rhoElo: r3(e.rho), pElo: e.p, rhoWinRate: r3(w.rho), pWinRate: w.p, rhoEloWinsProfile: r3(ew.rho), pEloWinsProfile: ew.p };
  }
  const eloWin = spearman(grouped.map(n => teams[n].eloMedian), grouped.map(n => teams[n].winRate));
  const decided = pairs.filter(p => winnerOf(p) && p.A.elo !== p.B.elo);
  const eloCal = { games: decided.length, higherEloWins: decided.filter(p => winnerOf(p).elo > loserOf(p).elo).length,
    expectedWins: r2(sum(decided.map(p => { const hi = p.A.elo > p.B.elo ? p.A : p.B, lo = hi === p.A ? p.B : p.A; return eloExpect(hi.elo, lo.elo); }))) };
  // ---------- our bot ----------
  const oursAll = aggregate(ours), oursWins = aggregate(ours.filter(g => g.win === 1));
  const ourVal = (m, basis) => (basis === 'wins' ? oursWins[m] : oursAll[m]);
  const teamVal = (n, m, basis) => (basis === 'wins' ? aggWins[n][m] : aggAll[n][m]);
  // Our map-adjusted value: deviation from the top-team baseline on the same maps (our maps are uniform: 16 games each).
  const oursAdj = Object.fromEntries(COMPARE.map(([m, basis]) => [m, mapAdjusted(ours, baseline, m, basis)]));
  const teamAdj = (n, m, basis) => (adjusted[n][m] !== undefined ? adjusted[n][m] : mapAdjusted(byTeam.get(n), baseline, m, basis));
  const comparison = [];
  for (const [m, basis, kind] of COMPARE) {
    const v = ourVal(m, basis), tv = grouped.map(n => [n, teamVal(n, m, basis)]).filter(x => x[1] !== null && x[1] !== undefined);
    const sorted = tv.slice().sort((a, b) => a[1] - b[1]);
    const av = oursAdj[m], ta = grouped.map(n => [n, teamAdj(n, m, basis)]).filter(x => x[1] !== null && x[1] !== undefined);
    const nearA = ta.slice().sort((a, b) => Math.abs(a[1] - av) - Math.abs(b[1] - av));
    comparison.push({ metric: m, basis, kind, ours: r3(v), teamMin: r3(sorted[0][1]), teamMedian: r3(median(tv.map(x => x[1]))), teamMax: r3(sorted[sorted.length - 1][1]),
      teamsBelow: tv.filter(x => x[1] < v).length, teamsAbove: tv.filter(x => x[1] > v).length, teams: tv.length,
      oursAdj: r3(av), teamAdjMin: r3(Math.min(...ta.map(x => x[1]))), teamAdjMax: r3(Math.max(...ta.map(x => x[1]))),
      teamsAdjBelow: ta.filter(x => x[1] < av).length, teamsAdjAbove: ta.filter(x => x[1] > av).length,
      nearestAdj: nearA.slice(0, 2).map(x => [x[0], r3(x[1])]), farthestAdj: [nearA[nearA.length - 1][0], r3(nearA[nearA.length - 1][1])] });
  }
  // Distance on map-adjusted values, z-scored across the grouped teams.
  const zStats = {};
  for (const m of DISTANCE) { const xs = grouped.map(n => adjusted[n][m]); const mu = mean(xs), sd = Math.sqrt(sum(xs.map(x => (x - mu) ** 2)) / (xs.length - 1)); zStats[m] = { mu, sd }; }
  const z = (m, v) => (v - zStats[m].mu) / zStats[m].sd;
  const ourZ = Object.fromEntries(DISTANCE.map(m => [m, r2(z(m, oursAdj[m]))]));
  const dist = grouped.map(n => {
    let d2 = 0; for (const m of DISTANCE) d2 += (z(m, adjusted[n][m]) - z(m, oursAdj[m])) ** 2;
    return { team: n, distance: r2(Math.sqrt(d2)), plan: teams[n].style.plan, sonar: teams[n].style.sonar };
  }).sort((a, b) => a.distance - b.distance);
  const teamSpread = [];
  for (let i = 0; i < grouped.length; i++) for (let j = i + 1; j < grouped.length; j++) {
    let d2 = 0; for (const m of DISTANCE) d2 += (z(m, adjusted[grouped[i]][m]) - z(m, adjusted[grouped[j]][m])) ** 2;
    teamSpread.push(Math.sqrt(d2));
  }
  const distNoChild = grouped.map(n => {
    let d2 = 0; for (const m of DISTANCE) if (m !== 'child2Share') d2 += (z(m, adjusted[n][m]) - z(m, oursAdj[m])) ** 2;
    return { team: n, distance: r2(Math.sqrt(d2)), plan: teams[n].style.plan, sonar: teams[n].style.sonar };
  }).sort((a, b) => a.distance - b.distance);
  const d7 = (x, y) => { let d2 = 0; for (const m of DISTANCE) if (m !== 'child2Share') d2 += (z(m, adjusted[x][m]) - z(m, adjusted[y][m])) ** 2; return Math.sqrt(d2); };
  const nn7 = grouped.map(n => Math.min(...grouped.filter(x => x !== n).map(x => d7(n, x))));
  const pair7 = []; for (let i = 0; i < grouped.length; i++) for (let j = i + 1; j < grouped.length; j++) pair7.push(d7(grouped[i], grouped[j]));
  const nearestPerTeam = grouped.map(n => Math.min(...grouped.filter(x => x !== n).map(x => { let d2 = 0; for (const m of DISTANCE) d2 += (z(m, adjusted[n][m]) - z(m, adjusted[x][m])) ** 2; return Math.sqrt(d2); })));
  const groupDist = {};
  for (const [key, gp] of Object.entries(groupProfile)) {
    const ds = dist.filter(d => gp.members.includes(d.team)).map(d => d.distance);
    groupDist[key] = { teams: ds.length, meanDistance: r2(mean(ds)), minDistance: r2(Math.min(...ds)) };
  }
  // Per map: ours vs the pooled top team-games on that map ([ours, top]); outcome-driven metrics in won games.
  const perMapOurs = {};
  for (const name of mapNames) {
    const o = ours.filter(g => g.map === name), t = main.filter(g => g.map === name);
    const oa = aggregate(o), ow = aggregate(o.filter(g => g.win === 1)), ta = aggregate(t), tw = aggregate(t.filter(g => g.win === 1));
    perMapOurs[name] = { ourGames: o.length, ourWins: oa.wins, topTeamGames: t.length,
      splitsPerGame: [r2(oa.splitsPerGame), r2(ta.splitsPerGame)], selfKillPer100DR: [r2(oa.selfKillPer100DR), r2(ta.selfKillPer100DR)],
      pingsPerDR: [r2(oa.pingsPerDR), r2(ta.pingsPerDR)], units200Wins: [ow.units200, tw.units200], peakUnitsWins: [ow.peakUnits, tw.peakUnits],
      finalLongest500Wins: [ow.finalLongest500, tw.finalLongest500], finalUnits500Wins: [ow.finalUnits500, tw.finalUnits500],
      finalConc500Wins: [r2(ow.finalConc500), r2(tw.finalConc500)], merge15Wins: [ow.merge15, tw.merge15], eatenPer100DR: [r2(oa.eatenPer100DR), r2(ta.eatenPer100DR)] };
  }
  const localOppProfiles = {};
  for (const opp of [...new Set(localOpp.map(g => g.team))].sort()) {
    const a = aggregate(localOpp.filter(g => g.team === opp));
    localOppProfiles[opp] = pick(a, ['games', 'winRate', 'splitsPerGame', 'childMedian', 'child2Share', 'selfKillPer100DR', 'selfExitShare', 'pingsPerDR', 'sprintsPer100DR',
      'peakUnits', 'units200', 'finalUnits500', 'finalLongest500', 'killsPerGame', 'killHeadShare', 'ramInitShare']);
  }
  // ---------- deaths, exits, eating (pooled main set) ----------
  const cat = {}, exitByCat = {};
  for (const g of main) {
    for (const [c, v] of Object.entries(g.own)) cat[c] = (cat[c] || 0) + v;
    for (const [c, v] of Object.entries(g.exitByCat)) { const x = exitByCat[c] || (exitByCat[c] = [0, 0]); x[0] += v[0]; x[1] += v[1]; }
  }
  const selfTotal = sum(Object.entries(cat).filter(([c]) => !ENEMY_CATS.has(c)).map(([, v]) => v));
  const deathTable = Object.fromEntries(Object.entries(cat).sort((a, b) => b[1] - a[1]).map(([c, v]) => [c, {
    deaths: v, perTeamGame: r2(v / main.length), shareOfSelf: ENEMY_CATS.has(c) ? null : r3(v / selfTotal),
    ownTurn: exitByCat[c] ? exitByCat[c][0] + exitByCat[c][1] : 0, exitShare: exitByCat[c] ? r3(exitByCat[c][0] / (exitByCat[c][0] + exitByCat[c][1])) : null }]));
  const S = k => sum(main.map(g => g[k]));
  const eating = { eaten: S('eatTotal'), natural: r3(S('eatNatural') / S('eatTotal')), ownSelfCorpse: r3(S('eatOwnSelf') / S('eatTotal')),
    ownKilledCorpse: r3(S('eatOwnKilled') / S('eatTotal')), oppSelfCorpse: r3(S('eatOppSelf') / S('eatTotal')), oppKilledCorpse: r3(S('eatOppKilled') / S('eatTotal')),
    selfDropPearls: S('dropSelfN'), selfDropEatenOwn: r3(S('dropSelfOwn') / S('dropSelfN')), selfDropEatenOpp: r3(S('dropSelfOpp') / S('dropSelfN')),
    selfKills: selfTotal, deaths: sum(Object.values(cat)), selfOwnTurn: S('selfExit') + S('selfTrapped'), selfExitShare: r3(S('selfExit') / (S('selfExit') + S('selfTrapped'))) };
  const SO = k => sum(ours.map(g => g[k]));
  const oursEating = { eaten: SO('eatTotal'), natural: r3(SO('eatNatural') / SO('eatTotal')), ownSelfCorpse: r3(SO('eatOwnSelf') / SO('eatTotal')),
    ownKilledCorpse: r3(SO('eatOwnKilled') / SO('eatTotal')), oppCorpse: r3((SO('eatOppSelf') + SO('eatOppKilled')) / SO('eatTotal')),
    selfDropEatenOwn: r3(SO('dropSelfOwn') / SO('dropSelfN')) };
  const oursDeaths = {}, oursExit = {};
  for (const g of ours) {
    for (const [c, v] of Object.entries(g.own)) oursDeaths[c] = (oursDeaths[c] || 0) + v;
    for (const [c, v] of Object.entries(g.exitByCat)) { const x = oursExit[c] || (oursExit[c] = [0, 0]); x[0] += v[0]; x[1] += v[1]; }
  }
  // ---------- SSS (excluded) ----------
  const sssPairs = gamePairs(sss);
  const sssGames = sssPairs.map(p => {
    const x = p.A.team === 'SSS' ? p.A : p.B, y = x === p.A ? p.B : p.A;
    return { key: x.key, map: x.map, opp: y.team, win: x.win, rounds: x.rounds, endReason: x.limit ? 'roundLimit' : 'teamEliminated', splits: x.splits, pings: x.pings,
      broken: x.pings === 0 && x.splits <= 3 };
  });
  return {
    meta: { generated: new Date().toISOString(), keysFile: path.relative(ROOT, base.opts.keysFile), snapshotGames: keys.length, mainGames: pairs.length,
      excludedTeams: EXCLUDED_TEAMS, excludedGames: sssPairs.length, localDir: path.relative(ROOT, base.opts.localDir), localGames: ours.length,
      teams: Object.keys(teams).length, groupedTeams: grouped.length, minTeamGames: MIN_TEAM_GAMES, checks,
      rule: { plan: `map-adjusted end concentration (longest/total at round 500) in won 500-round games; K >= +${PLAN_RESID}, N below; needs >= ${PLAN_MIN_WINS} such wins`,
        planRaw: `unadjusted median end concentration in won 500-round games; K >= ${PLAN_RAW}, D below`,
        sonar: `pings per dragon-round: full >= ${SONAR_FULL}, mid >= ${SONAR_MID}, low < ${SONAR_MID}` } },
    overall: { stats: mapStats(pairs), winnerVsLoser: winnerVsLoser(pairs), eloCalibration: eloCal, eloVsWinRate: { rho: r3(eloWin.rho), p: eloWin.p, n: eloWin.n }, firstMover },
    maps: mapTable, families, familyContrast: contrast, mapLevel, mapFeatureCorrelation: featureCorr,
    teams, stability, ruleEvidence, groups: groupProfile, matchups, h2h, teamMap, mapSpecialization: specialization,
    eloVsStyle, deaths: deathTable, eating,
    ours: { games: ours.length, winRate: r3(oursAll.winRate), all: pick(oursAll, VECTOR), wins: pick(oursWins, WIN_PROFILE), deaths: oursDeaths,
      exitByCat: oursExit, eating: oursEating, mapAdjusted: pick(oursAdj, Object.keys(oursAdj)), comparison, z: ourZ, distanceMetrics: DISTANCE, nearestTeams: dist,
      nearestTeamsWithoutChildSize: distNoChild,
      teamPairDistanceWithoutChildSize: { median: r2(median(pair7)), nearestNeighbourMedian: r2(median(nn7)), nearestNeighbourMax: r2(Math.max(...nn7)) },
      teamPairDistance: { median: r2(median(teamSpread)), min: r2(Math.min(...teamSpread)), max: r2(Math.max(...teamSpread)), nearestNeighbourMedian: r2(median(nearestPerTeam)), nearestNeighbourMax: r2(Math.max(...nearestPerTeam)) },
      groupDistance: groupDist, perMap: perMapOurs, localOpponents: localOppProfiles },
    sss: { games: sssGames.length, broken: sssGames.filter(g => g.broken).length, brokenWins: sum(sssGames.filter(g => g.broken).map(g => g.win)),
      otherWins: sum(sssGames.filter(g => !g.broken).map(g => g.win)), list: sssGames },
  };
}

async function main() {
  const argv = process.argv.slice(2);
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const opts = {
    keysFile: path.resolve(ROOT, opt('keys', 'data/top/snapshot-20260929a.keys')),
    localDir: path.resolve(ROOT, opt('local', 'exp/eval-r1')),
    outFile: path.resolve(ROOT, opt('out', 'data/top/matchup_study.json')),
    jobs: Math.max(1, Math.min(4, Math.floor(+opt('jobs', 4)) || 4)),
    cacheFile: opt('cache', null) ? path.resolve(opt('cache')) : null,
    quiet: argv.includes('--quiet'),
  };
  const t0 = Date.now();
  const data = await collect(opts);
  const out = tables(analyse(data, opts));
  out.meta.seconds = Math.round((Date.now() - t0) / 1000);
  fs.writeFileSync(opts.outFile, JSON.stringify(out, null, 1) + '\n');
  if (!opts.quiet) report(out);
  console.log(`wrote ${path.relative(ROOT, opts.outFile)}: ${out.meta.mainGames} main-set games, ${out.meta.localGames} local games, ` +
    `checks ${JSON.stringify(out.meta.checks)}, ${out.meta.seconds}s`);
}

// ---------------------------------------------------------------------------------------------------------------
// Text report (markdown tables). Every number in research/observations/top-maps-matchups.md comes from here or <out>.
function report(o) {
  const L = [];
  const f = (x, d = 2) => (x === null || x === undefined ? '-' : typeof x === 'number' ? (Number.isInteger(x) ? String(x) : x.toFixed(d)) : String(x));
  const pc = (x, d = 0) => (x === null || x === undefined ? '-' : (100 * x).toFixed(d) + '%');
  const wr = c => (c ? `${f(c.wins, 1).replace(/\.0$/, '')}/${c.games} (${pc(c.winRate)}, Elo ${pc(c.eloExpected)}, CI ${c.ci95 && c.ci95.length ? pc(c.ci95[0]) + '–' + pc(c.ci95[1]) : '-'}, battles ${c.battles}, top pair ${pc(c.topPairShare)})` : '-');
  const table = (head, rows) => { L.push('| ' + head.join(' | ') + ' |', '|' + head.map(() => '---').join('|') + '|'); for (const r of rows) L.push('| ' + r.map(x => f(x)).join(' | ') + ' |'); L.push(''); };
  const sec = t => L.push('', '## ' + t, '');
  const m = o.meta;
  L.push(`# matchup_study report (${m.generated})`, '', `snapshot ${m.keysFile}: ${m.snapshotGames} games; main set ${m.mainGames} (excluded ${m.excludedTeams.join(', ')}: ${m.excludedGames}); ` +
    `teams ${m.teams} (style vector for ${m.groupedTeams} with >= ${m.minTeamGames} games); local ${m.localDir}: ${m.localGames} games`, `checks ${JSON.stringify(m.checks)}`,
    `rule plan: ${m.rule.plan}`, `rule planRaw: ${m.rule.planRaw}`, `rule sonar: ${m.rule.sonar}`);

  sec('1. Overall');
  const os = o.overall.stats, fm = o.overall.firstMover, ec = o.overall.eloCalibration;
  L.push(`rounds ${JSON.stringify(os.rounds)}; teamEliminated ${pc(os.elimShare, 1)}; ended by r100 ${os.endBy100}, by r200 ${os.endBy200}`,
    `500-round games ${os.limit.games}: winner longest ${f(os.limit.winnerLongest)} / loser ${f(os.limit.loserLongest)} (margin ${f(os.limit.marginLongest)}), winner total ${f(os.limit.winnerTotal)} / loser ${f(os.limit.loserTotal)}, winner units ${f(os.limit.winnerUnits)} / loser ${f(os.limit.loserUnits)}, winner conc ${f(os.limit.winnerConc)}, winner more total ${pc(os.limit.winnerMoreTotalShare)}, decided by total ${os.limit.decidedByTotal}`,
    `elimination games ${os.elim.games}: rounds median ${f(os.elim.roundsMedian)}, winner units ${f(os.elim.winnerUnits)}, longest ${f(os.elim.winnerLongest)}, total ${f(os.elim.winnerTotal)}; loser last death ${JSON.stringify(os.elim.loserLastDeath)} (len median ${f(os.elim.loserLastDeathLen)})`,
    `interaction: enemy-involved deaths/game median ${f(os.interaction.enemyDeathsPerGame)}, trades/game ${f(os.interaction.tradesPerGame)}, body-block kills total ${os.interaction.bodyBlockKills}, games without contact ${os.interaction.gamesWithoutContact}`,
    `higher-elo team won ${ec.higherEloWins}/${ec.games} (Elo-expected ${ec.expectedWins}); team elo vs snapshot win rate Spearman ${f(o.overall.eloVsWinRate.rho)} (p ${f(o.overall.eloVsWinRate.p, 4)}, n ${o.overall.eloVsWinRate.n})`,
    `first mover (smallest dragon id): ${JSON.stringify(fm)}`);

  sec('2. Maps: features');
  table(['map', 'size', 'area', 'kelp density', 'portal pairs', 'spawn tiles', 'spawn cap/round', 'cap/100 tiles', 'fountain tiles', 'start dragons/team', 'start length/team', 'head dist min', 'reach from A'],
    o.mapLevel.map(x => { const v = Object.values(o.maps).flatMap(e => Object.entries(e.variants)).find(([k]) => k === x.label)[1].features;
      return [x.label, `${v.width}x${v.height}`, v.area, f(v.kelpDensity, 3), v.portalPairs, v.spawnTiles, f(v.spawnCapPerRound), f(v.spawnCapPer100Tiles), v.fountainTiles, v.initDragonsPerTeam, v.initLenPerTeam, v.headDistMin === null ? 'none' : v.headDistMin, f(v.reachShareFromA, 3)]; }));
  sec('3. Maps: game length and end state');
  const mrow = (name, st, fam) => [name, fam || '', st.games, `${f(st.rounds.p25, 0)}/${f(st.rounds.median, 0)}/${f(st.rounds.p75, 0)}`, pc(st.elimShare), st.endBy100, st.endBy200,
    st.limit.games, f(st.limit.winnerLongest), f(st.limit.loserLongest), f(st.limit.winnerTotal), f(st.limit.winnerUnits), f(st.limit.loserUnits), f(st.limit.winnerConc),
    f(st.elim.roundsMedian), f(st.elim.winnerUnits), f(st.interaction.enemyDeathsPerGame), f(st.interaction.tradesPerGame), st.interaction.gamesWithoutContact, f(st.selfKillsPerTeamGame)];
  const rowsM = [];
  for (const [name, e] of Object.entries(o.maps)) {
    rowsM.push(mrow(name, e.stats, e.family));
    if (Object.keys(e.variants).length > 1) for (const [v, x] of Object.entries(e.variants)) rowsM.push(mrow('  ' + v, x.stats, ''));
  }
  rowsM.push(mrow('ALL', o.overall.stats, ''));
  table(['map', 'family', 'games', 'rounds p25/med/p75', 'elim', 'end<=100', 'end<=200', '500-games', 'W longest', 'L longest', 'W total', 'W units', 'L units', 'W conc',
    'elim rounds', 'elim W units', 'enemy deaths/g', 'trades/g', 'no contact', 'self-kills/team-game'], rowsM);
  L.push('loser last death in elimination games (per map):');
  for (const [name, e] of Object.entries(o.maps)) L.push(`  ${name}: ${JSON.stringify(e.stats.elim.loserLastDeath)} len ${f(e.stats.elim.loserLastDeathLen)}; first mover ${e.stats.firstMoverWins}/${e.stats.firstMoverGames}`);
  sec('4. Maps: winner vs loser (paired; winner median / loser median, share of games where winner is higher)');
  const wlKeys = Object.keys(o.overall.winnerVsLoser);
  const wl = w => wlKeys.map(k => `${f(w[k].winnerMedian, 1)}/${f(w[k].loserMedian, 1)} ${pc(w[k].winnerHigherShare)}`);
  table(['map', ...wlKeys], [['ALL', ...wl(o.overall.winnerVsLoser)], ...Object.entries(o.maps).map(([n, e]) => [n, ...wl(e.winnerVsLoser)])]);
  L.push('pairs used: ' + wlKeys.map(k => k + ' ' + o.overall.winnerVsLoser[k].n).join(', '));
  sec('5. Maps: feature vs outcome across map variants (Spearman, descriptive)');
  table(['feature ~ outcome', 'n', 'rho', 'p'], Object.entries(o.mapFeatureCorrelation).map(([k, v]) => [k, v.n, f(v.rho), f(v.p, 4)]));

  sec('6. Teams: style vector (all main-set games)');
  const T = Object.entries(o.teams).sort((a, b) => b[1].eloMedian - a[1].eloMedian);
  table(['team', 'elo', 'rank', 'games', 'win', 'splits/g', 'child med', 'self-kills/g', 'self/100DR', 'final units 500 (n)', 'final longest 500', 'kills/g', 'head-on kill share', 'pings/DR', 'rush share'],
    T.map(([n, t]) => { const v = t.vector; return [n, t.eloMedian, t.rank === null ? '-' : t.rank, t.games, pc(t.winRate), f(v.splitsPerGame, 0), f(v.childMedian), f(v.selfKillPerGame, 0), f(v.selfKillPer100DR),
      `${f(v.finalUnits500)} (${v.limitGames})`, f(v.finalLongest500), f(v.killsPerGame, 1), pc(v.killHeadShare, 1), f(v.pingsPerDR), pc(v.earlyRushShare)]; }));
  sec('7. Teams: labels, stable fingerprints, plan in won games');
  table(['team', 'plan', 'raw plan', 'sonar', 'won 500-games', 'end conc (wins)', 'map-adj end conc', 'end units (wins)', 'end longest (wins)', 'units200 (wins)', 'merge15 (wins)', 'child=2 share', 'self-kill with exit', 'ram-first share', 'sprints/100DR', 'suicides/g', 'main self-kill (share)'],
    T.filter(([, t]) => t.grouped).map(([n, t]) => { const v = t.vector, w = t.winsProfile; return [n, t.style.plan || '-', t.style.planRaw || '-', t.style.sonar, w.limitGames, f(w.finalConc500), f(t.mapAdjusted.finalConc500, 3), f(w.finalUnits500), f(w.finalLongest500), f(w.units200), f(w.merge15),
      pc(v.child2Share), pc(v.selfExitShare), pc(v.ramInitShare), f(v.sprintsPer100DR), f(v.suicidePerGame, 1), `${v.selfMethod} (${pc(v.selfMethodShare)})`]; }));
  table(['team', ...Object.keys(Object.values(o.teams).find(t => t.grouped).mapAdjusted).map(k => 'adj ' + k)],
    T.filter(([, t]) => t.grouped).map(([n, t]) => [n, ...Object.values(t.mapAdjusted).map(x => f(x, 3))]));
  L.push('ungrouped (< ' + m.minTeamGames + ' games): ' + T.filter(([, t]) => !t.grouped).map(([n, t]) => `${n} ${t.games}`).join(', '));
  L.push('games without sonar (team: no-sonar games / SSS-like games with no sonar and <= 3 splits): ' +
    T.filter(([, t]) => t.vector.noPingGames).map(([n, t]) => `${n} ${t.vector.noPingGames}/${t.vector.brokenLikeGames}`).join(', '));
  L.push('rule evidence, plan (map-adjusted end conc in wins, n wins, raw): ' + o.ruleEvidence.planConcInWinsAdjusted.map(x => `${x[0]} ${f(x[1], 3)}(${x[2]}, raw ${f(x[3])})`).join(', '));
  L.push('winner end concentration by map (baseline): ' + JSON.stringify(o.ruleEvidence.winnerConcByMap));
  L.push('rule evidence, sonar: ' + o.ruleEvidence.pingsPerDR.map(x => `${x[0]} ${f(x[1])}`).join(', '));
  sec('8. Win/loss stability of metrics (grouped teams)');
  table(['metric', 'r(win value, loss value)', 'team SD', 'mean |win-loss|', 'gap / SD'], Object.entries(o.stability).map(([k, v]) => [k, f(v.rWinLoss), f(v.teamSD, 3), f(v.meanWinLossGap, 3), f(v.gapOverSD)]));
  sec('9. Groups');
  table(['group', 'teams', 'games', 'win', 'elo med', 'splits/g', 'self/100DR', 'pings/DR', 'peak units', 'units200', 'final units 500', 'final longest 500', 'end conc 500', 'wins: end conc', 'wins: units200', 'wins: merge15', 'members'],
    Object.entries(o.groups).map(([k, g]) => [k, g.teams, g.games, pc(g.winRate), f(g.eloMedian), f(g.all.splitsPerGame, 0), f(g.all.selfKillPer100DR), f(g.all.pingsPerDR), f(g.all.peakUnits), f(g.all.units200),
      f(g.all.finalUnits500), f(g.all.finalLongest500), f(g.all.finalConc500), f(g.wins.finalConc500), f(g.wins.units200), f(g.wins.merge15), g.members.join(', ')]));
  sec('10. Matchups (row style vs column style; wins / games, Elo-expected, battle-bootstrap 95% CI)');
  for (const [axis, t] of Object.entries(o.matchups)) {
    L.push(`[${axis}]`);
    for (const [k, v] of Object.entries(t)) L.push(`  ${k}: ${v.note ? `${v.games} games (same style)` : wr(v) + `, pairs ${v.teamPairs}, top ${v.topPair}`}`);
  }
  L.push('', 'by map family:');
  for (const [fam, x] of Object.entries(o.families)) {
    L.push(`  ${fam} (${x.maps.join(', ')}; ${x.games} games): K vs N ${wr(x.planKvsN)}; raw K vs D ${wr(x.planRawKvsD)}`);
    for (const [k, v] of Object.entries(x.sonar)) L.push(`    sonar ${k}: ${wr(v)}`);
  }
  L.push('', 'style excess over Elo, long maps minus short maps (battle bootstrap 95% CI):');
  for (const [k, v] of Object.entries(o.familyContrast)) L.push(`  ${k}: ${v ? `long ${pc(v.excessLong, 1)} (${v.gamesLong}) vs short ${pc(v.excessShort, 1)} (${v.gamesShort}), difference ${pc(v.difference, 1)} CI ${pc(v.ci95[0], 1)}..${pc(v.ci95[1], 1)}, battles ${v.battles}; leave-one-team-out ${pc(v.leaveOneTeamOut.min[1], 1)} (without ${v.leaveOneTeamOut.min[0]}) .. ${pc(v.leaveOneTeamOut.max[1], 1)} (without ${v.leaveOneTeamOut.max[0]})` : '-'}`);
  L.push('', 'by map:');
  for (const [name, e] of Object.entries(o.maps)) {
    L.push(`  ${name} [${e.family}]: K vs N ${wr(e.planKvsN)}${e.planKvsN ? ', top ' + e.planKvsN.topPair : ''}; raw K vs D ${wr(e.planRawKvsD)}`);
    for (const [k, v] of Object.entries(e.sonar)) L.push(`    sonar ${k}: ${wr(v)}`);
  }
  sec('11. Head-to-head (pairs with >= 3 games): a vs b, a wins - b wins, battles');
  table(['team a', 'team b', 'games', 'a-b', 'battles', 'maps'], o.h2h.map(h => [h.a, h.b, h.games, `${f(h.aWins, 1).replace(/\.0$/, '')}-${f(h.games - h.aWins, 1).replace(/\.0$/, '')}`, h.battles, Object.keys(h.maps).length]));

  sec('12. Our bot (exp/eval-r1, 160 local games vs 4 weak local bots)');
  const ob = o.ours;
  L.push(`games ${ob.games}, local win rate ${pc(ob.winRate)}; deaths ${JSON.stringify(ob.deaths)}; own-turn exits ${JSON.stringify(ob.exitByCat)}; eating ${JSON.stringify(ob.eating)}`);
  table(['metric', 'basis', 'kind', 'ours', 'top min', 'top median', 'top max', 'teams below/above', 'ours map-adj', 'teams adj min..max', 'adj below/above', 'nearest (adj)', 'farthest (adj)'],
    ob.comparison.map(c => [c.metric, c.basis, c.kind, f(c.ours, 3), f(c.teamMin, 3), f(c.teamMedian, 3), f(c.teamMax, 3), `${c.teamsBelow}/${c.teamsAbove}`, f(c.oursAdj, 3), `${f(c.teamAdjMin, 3)}..${f(c.teamAdjMax, 3)}`,
      `${c.teamsAdjBelow}/${c.teamsAdjAbove}`, c.nearestAdj.map(x => `${x[0]} ${f(x[1], 3)}`).join('; '), `${c.farthestAdj[0]} ${f(c.farthestAdj[1], 3)}`]));
  L.push(`z-scores of our map-adjusted values (vs grouped teams' map-adjusted values) on ${ob.distanceMetrics.join(', ')}: ${JSON.stringify(ob.z)}`,
    `distance to teams (sorted): ${ob.nearestTeams.map(d => `${d.team} ${f(d.distance)} [${d.plan || '-'}/${d.sonar}]`).join(', ')}`,
    `team-to-team distances: ${JSON.stringify(ob.teamPairDistance)}; by group: ${JSON.stringify(ob.groupDistance)}`,
    `distance without child2Share: ${ob.nearestTeamsWithoutChildSize.map(d => `${d.team} ${f(d.distance)}`).join(', ')}; team scale ${JSON.stringify(ob.teamPairDistanceWithoutChildSize)}`);
  L.push('', 'per map: [ours, pooled top team-games]; *Wins columns use won games only');
  const pmKeys = Object.keys(Object.values(ob.perMap)[0]).filter(k => Array.isArray(Object.values(ob.perMap)[0][k]));
  table(['map', 'our W/games', ...pmKeys], Object.entries(ob.perMap).map(([n, x]) => [n, `${x.ourWins}/${x.ourGames}`, ...pmKeys.map(k => `${f(x[k][0])} / ${f(x[k][1])}`)]));
  table(['local opponent', ...Object.keys(Object.values(ob.localOpponents)[0])], Object.entries(ob.localOpponents).map(([n, x]) => [n, ...Object.values(x).map(v => f(v))]));

  sec('13. Team x map (wins/games; * = fewer than 5 games)');
  const maps = Object.keys(o.maps);
  table(['team', ...maps], T.map(([n]) => [n, ...maps.map(mp => { const c = o.teamMap[n][mp]; return c ? `${f(c.wins, 1).replace(/\.0$/, '')}/${c.games}${c.games < 5 ? '*' : ''}` : ''; })]));
  table(['team (Elo-expected wins per map)', ...maps], T.filter(([, t]) => t.grouped).map(([n]) => [n, ...maps.map(mp => { const c = o.teamMap[n][mp]; return c ? `${f(c.wins, 1).replace(/\.0$/, '')}/${c.games} (E ${f(c.eloExpected, 1)})` : ''; })]));
  L.push('map specialization (teams with >= 20 games; permutation of map labels within the team): ' +
    Object.entries(o.mapSpecialization).map(([n, v]) => (v ? `${n}: ${n === 'pooled' ? `teams ${v.teams}, stat ${f(v.stat)}` : `games ${v.games}, stat ${f(v.stat)} (null median ${f(v.nullMedian)})`}, p ${f(v.p, 4)}` : `${n}: -`)).join('; '));

  sec('14. Elo and snapshot win rate vs style (Spearman over grouped teams; permutation p; many tests)');
  table(['metric', 'n', 'rho elo', 'p', 'rho win rate', 'p', 'rho elo (wins profile)', 'p'], Object.entries(o.eloVsStyle).map(([k, v]) => [k, v.n, f(v.rhoElo), f(v.pElo, 4), f(v.rhoWinRate), f(v.pWinRate, 4), f(v.rhoEloWinsProfile), f(v.pEloWinsProfile, 4)]));

  sec('15. Deaths, free neighbour, eating (pooled main set)');
  table(['category', 'deaths', 'per team-game', 'share of self-inflicted', 'on own turn', 'had a free neighbour'], Object.entries(o.deaths).map(([k, v]) => [k, v.deaths, f(v.perTeamGame), pc(v.shareOfSelf, 1), v.ownTurn, pc(v.exitShare, 1)]));
  L.push(`eating ${JSON.stringify(o.eating)}`);

  sec('16. SSS (excluded)');
  L.push(`games ${o.sss.games}, broken signature (no sonar and <= 3 splits) ${o.sss.broken}, wins in broken ${o.sss.brokenWins}, wins in the rest ${o.sss.otherWins}`);
  table(['game', 'map', 'opponent', 'win', 'rounds', 'end', 'splits', 'pings', 'broken'], o.sss.list.map(g => [g.key, g.map, g.opp, g.win, g.rounds, g.endReason, g.splits, g.pings, g.broken ? 'yes' : '']));
  console.log(L.join('\n'));
}

module.exports = { geometry, mapFeatures, replayPass, catOf, ENEMY_CATS, teamGame, aggregate, collect, analyse, tables, report };
if (!IS_WORKER && require.main === module) main().catch(err => { console.error(err); process.exit(1); });
