#!/usr/bin/env node
// Territory, pearl races, raids and defence, from replays only (no games, no network).
// Written for research/observations/top-territory.md (2026-09-30).
//
// usage (repository root):
//   node exp/territory-analysis/extract.js top --keys <file|all> [--name top-sample] [--jobs 4] [--limit N]
//   node exp/territory-analysis/extract.js online <set> [<set> ...] [--jobs 4]
//   One gzip member (one JSON line) per game in exp/territory-analysis/cache/<name>.jsonl.gz (online: online-<set>.jsonl.gz).
//   Games already in the file are skipped.
//
// Reconstruction: tools/mass_ledger.js perGame() with hooks (its checks must stay 0). On top of it, per game:
//   Territory = the ledger's static split (a tile belongs to the team whose starting bodies are closer by movement distance,
//     kelp, portals and wrap included). Checked against the ledger's own terr (chk.terr).
//   Pearl map = the map file of the game's pearl variant (maps/online-20260927 a, maps/variants b / PD10). The variant comes
//     from data/pearl_layout/variants.json, else from the spawns of this game (the file whose never-spawning tiles saw the
//     fewest spawns). Fountain = mean gap (min+max)/2 <= 12 (the ledger's rule, but with the right variant file).
//     Capacity weight of a tile = 1 / mean gap (expected spawn attempts per round).
//   Head distance = static path distance over the map (kelp, portals, wrap; bodies ignored), multi-source BFS from every
//     living head of a team at the start of each round (= the moment pearls spawn).
//   Natural spawns: new natural pearls seen at the first turn of a round (spawns happen before any dragon moves).
//   Raid episode: a dragon whose head is in the other team's territory after its action (or that eats a pearl there), until
//     its head is back outside that territory after an action (exit 0), it dies (exit 1) or the game ends (exit 2).
// Output per game: see `analyse()` (pearl rows P, raid episodes E, deaths D, coverage checkpoints C, location bins LOC).
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), cp = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const TOP = path.join(ROOT, 'data', 'top'), ONLINE = path.join(ROOT, 'data', 'online');
const CACHE = path.join(__dirname, 'cache');
const DIRS = ['N', 'E', 'S', 'W'], DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 };
const MAPFILE = { 'Autarky': 'autarky', 'Default': 'default', 'Devil': 'devil', 'Portals': 'portals', 'Prisoners Dilemma': 'prisoners_dilemma',
  'Queen Of Spades': 'queen_of_spades', 'Schooltime': 'schooltime', 'Slithery Fight': 'slithery_fight', 'Trauma': 'trauma', 'Trophy': 'trophy' };
const BVARIANT = { 'Devil': 'devil_b', 'Queen Of Spades': 'queen_of_spades_b', 'Schooltime': 'schooltime_b', 'Slithery Fight': 'slithery_fight_b' };
const INF = 999;

// ---------------------------------------------------------------------------------------------------------------
// Map files and pearl variants
const gapFiles = new Map();
function gapsOfFile(f) {
  if (!gapFiles.has(f)) {
    const L = fs.readFileSync(f, 'utf8').split('\n');
    const m = /^MAP (\d+) (\d+)/.exec(L[0]); const w = +m[1], h = +m[2];
    const g = new Array(w * h).fill(null);
    for (const l of L) if (l.startsWith('TILE ')) { const [x, y, mn, mx] = l.trim().split(/\s+/).slice(1).map(Number); g[y * w + x] = [mn, mx]; }
    gapFiles.set(f, { w, h, g });
  }
  return gapFiles.get(f);
}
const fileOf = (map, tag) => {
  if (map === 'Prisoners Dilemma' && tag === '10') return path.join(ROOT, 'maps', 'variants', 'prisoners_dilemma_10.map');
  if (tag === 'b' && BVARIANT[map]) return path.join(ROOT, 'maps', 'variants', BVARIANT[map] + '.map');
  return MAPFILE[map] ? path.join(ROOT, 'maps', 'online-20260927', MAPFILE[map] + '.map') : null;
};
let VASSIGN = null;
function variantAssign() {
  if (!VASSIGN) {
    VASSIGN = {};
    try {
      const V = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'pearl_layout', 'variants.json'), 'utf8'));
      for (const c of Object.values(V.cats)) for (const [g, t] of Object.entries(c.assign || {})) VASSIGN[g] = t;
    } catch { /* optional */ }
  }
  return VASSIGN;
}
// natural spawn tiles of a replay, decided as perGame decides drops (tileChange+pearl right after a death = drop)
function spawnCounts(R) {
  const W = R.match.map.width, cnt = new Map(); let drop = false, started = false;
  for (const e of R.events) {
    if (e.type === 'roundStart') started = true;
    if (e.type === 'dragonDeath') { drop = true; continue; }
    if (e.type === 'tileChange' && e.hasPearl) { if (!drop && started) { const k = e.tile.y * W + e.tile.x; cnt.set(k, (cnt.get(k) || 0) + 1); } continue; }
    drop = false;
  }
  return cnt;
}
function variantOf(map, gameId, R, nInit) {
  if (map === 'Prisoners Dilemma') return { tag: nInit === 10 ? '10' : 'a', how: 'dragons' };
  if (!BVARIANT[map]) return { tag: 'a', how: 'single' };
  const W = R.match.map.width, H = R.match.map.height;
  const ga = gapsOfFile(fileOf(map, 'a')), gb = gapsOfFile(fileOf(map, 'b'));
  let ca = 0, cb = 0;
  if (ga.w === W && ga.h === H && gb.w === W && gb.h === H)
    for (const [k, n] of spawnCounts(R)) { if (!(ga.g[k] && ga.g[k][1] > 0)) ca += n; if (!(gb.g[k] && gb.g[k][1] > 0)) cb += n; }
  const guess = cb < ca ? 'b' : 'a';
  const A = variantAssign(), as = gameId !== undefined && gameId !== null ? A['g' + gameId] : undefined;
  if (as === 'a' || as === 'b') return { tag: as, how: 'assign', guess, ca, cb };
  return { tag: guess, how: 'spawns', guess, ca, cb };
}

// ---------------------------------------------------------------------------------------------------------------
// Geometry (same rules as tools/mass_ledger.js perGame)
function geometry(R) {
  const M = R.match.map, W = M.width, H = M.height, N = W * H;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const key = (x, y) => y * W + x;
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
  const nb = new Int32Array(N * 4).fill(-1);
  for (let k = 0; k < N; k++) { const x = k % W, y = (k / W) | 0; for (let j = 0; j < 4; j++) { const r = across(x, y, DIRS[j]); if (r) nb[k * 4 + j] = key(r.x, r.y); } }
  const distFrom = team => {
    const dist = new Int32Array(N).fill(-1), q = [];
    for (const d0 of M.initialDragons) if (d0.team === team) for (const s of d0.body) { const k = key(s.x, s.y); if (dist[k] < 0) { dist[k] = 0; q.push(k); } }
    for (let i = 0; i < q.length; i++) { const k = q[i]; for (let j = 0; j < 4; j++) { const u = nb[k * 4 + j]; if (u < 0 || dist[u] >= 0) continue; dist[u] = dist[k] + 1; q.push(u); } }
    return dist;
  };
  const dA = distFrom('A'), dB = distFrom('B');
  const terr = new Int8Array(N);
  for (let k = 0; k < N; k++) { const a = dA[k] < 0 ? Infinity : dA[k], b = dB[k] < 0 ? Infinity : dB[k]; terr[k] = a < b ? 1 : b < a ? 2 : 0; }
  // margin from A's side: > 0 in A's territory (how many steps closer A's start is), < 0 in B's
  const marginA = new Int16Array(N);
  for (let k = 0; k < N; k++) { const a = dA[k] < 0 ? INF : dA[k], b = dB[k] < 0 ? INF : dB[k]; marginA[k] = Math.max(-99, Math.min(99, b - a)); }
  return { W, H, N, nb, terr, marginA, wx, wy, key };
}

// ---------------------------------------------------------------------------------------------------------------
// One game
function analyse(R, info) {
  const M = R.match.map, W = M.width, H = M.height;
  const nInit = M.initialDragons.length;
  const linfo = { map: info.map };
  if (info.map === 'Prisoners Dilemma') linfo.variant = nInit === 10 ? 'PD10' : 'PD6';
  const G = geometry(R), N = G.N, nb = G.nb, terr = G.terr;
  const V = variantOf(info.map, info.gameId, R, nInit);
  const gf = fileOf(info.map, V.tag), gg = gf && fs.existsSync(gf) ? gapsOfFile(gf) : null;
  const gaps = gg && gg.w === W && gg.h === H ? gg.g : null;
  const wgt = new Float64Array(N), fount = new Uint8Array(N), spawnable = new Uint8Array(N);
  if (gaps) for (let k = 0; k < N; k++) { const g = gaps[k]; if (g && g[1] > 0) { const m = (g[0] + g[1]) / 2; wgt[k] = 1 / Math.max(1, m); spawnable[k] = 1; if (m <= 12) fount[k] = 1; } }
  // tiles within path distance 3 of a fountain of territory t (1 A, 2 B)
  const nearF = [null, new Uint8Array(N), new Uint8Array(N)];
  {
    for (const tv of [1, 2]) {
      const d = new Int16Array(N).fill(-1), q = [];
      for (let k = 0; k < N; k++) if (fount[k] && terr[k] === tv) { d[k] = 0; q.push(k); }
      for (let i = 0; i < q.length; i++) { const k = q[i]; if (d[k] >= 3) continue; for (let j = 0; j < 4; j++) { const u = nb[k * 4 + j]; if (u < 0 || d[u] >= 0) continue; d[u] = d[k] + 1; q.push(u); } }
      for (let k = 0; k < N; k++) if (d[k] >= 0) nearF[tv][k] = 1;
    }
  }
  const TI = tm => tm === 'A' ? 0 : 1;              // team index
  const OWNT = ti => ti + 1, ENT = ti => 2 - ti;    // own / enemy territory value
  const relTerr = (ti, k) => terr[k] === OWNT(ti) ? 0 : terr[k] === 0 ? 1 : 2; // 0 own, 1 neutral, 2 enemy
  const depthIn = (ti, k) => ti === 0 ? -G.marginA[k] : G.marginA[k];         // > 0 inside the enemy's territory

  // per-round state
  const dist = [new Int16Array(N), new Int16Array(N)], srcLen = [new Int16Array(N), new Int16Array(N)], srcId = [new Int32Array(N), new Int32Array(N)];
  const vis = [new Uint8Array(N), new Uint8Array(N)];
  const queue = new Int32Array(N + 8);
  const heads = [[], []];
  function bfsHeads(ti) {
    const d = dist[ti], sl = srcLen[ti], si = srcId[ti]; d.fill(-1);
    let qh = 0, qt = 0;
    for (const h of heads[ti]) if (d[h.t] < 0) { d[h.t] = 0; sl[h.t] = h.len; si[h.t] = h.id; queue[qt++] = h.t; }
    while (qh < qt) { const k = queue[qh++], dk = d[k]; for (let j = 0; j < 4; j++) { const u = nb[k * 4 + j]; if (u < 0 || d[u] >= 0) continue; d[u] = dk + 1; sl[u] = sl[k]; si[u] = si[k]; queue[qt++] = u; } }
  }
  function markVis(ti) {
    const v = vis[ti]; v.fill(0);
    for (const h of heads[ti]) { const hx = h.t % W, hy = (h.t / W) | 0; for (let dy = -3; dy <= 3; dy++) { const yy = G.wy(hy + dy) * W; for (let dx = -3; dx <= 3; dx++) v[yy + G.wx(hx + dx)] = 1; } }
  }
  // local BFS from one tile, radius r (stamped)
  const lbD = new Int16Array(N), lbS = new Int32Array(N); let lbStamp = 0;
  function localBfs(src, r) {
    lbStamp++; let qh = 0, qt = 0; lbS[src] = lbStamp; lbD[src] = 0; queue[qt++] = src;
    while (qh < qt) { const k = queue[qh++], dk = lbD[k]; if (dk >= r) continue; for (let j = 0; j < 4; j++) { const u = nb[k * 4 + j]; if (u < 0 || lbS[u] === lbStamp) continue; lbS[u] = lbStamp; lbD[u] = dk + 1; queue[qt++] = u; } }
  }
  const lbGet = k => lbS[k] === lbStamp ? lbD[k] : INF;

  // pearls: row = [r, k, terr, fount, marginA, dHA, dHB, visA, visB, lenNearA, lenNearB, nearAinB, nearBinA, eater, eatR, eatLen, eatAge]
  const P = [], known = new Map();
  const PR = { r: 0, k: 1, terr: 2, f: 3, m: 4, dA: 5, dB: 6, vA: 7, vB: 8, lA: 9, lB: 10, xA: 11, xB: 12, eater: 13, eatR: 14, eatLen: 15, eatAge: 16 };
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) { const row = [-1, i, terr[i], fount[i], G.marginA[i], -1, -1, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1]; P.push(row); known.set(i, row); }
  // raid episodes
  const open = new Map(), E = [];
  const unitsOf = (ctx, ti) => { let n = 0; for (const d of ctx.drag.values()) if (TI(d.team) === ti) n++; return n; };
  function openEp(d, round, k, ctx) {
    const ti = TI(d.team);
    const ep = { ti, id: d.id, r0: round, r1: -1, L0: d.body.length, Lmax: d.body.length, L1: 0, nat: 0, fnt: 0, drop: 0, exit: -1, cause: -1, killer: 0, killerLen: 0,
      blkE: 0, dmax: depthIn(ti, k), dDef0: -1, dDefMin: INF, nDef6: -1, appr: -1, retr: -1, kills: 0, trades: 0, born: d.parent >= 0 && d.born === round ? 1 : 0,
      upd: 0, near: null, fr: 0, units: unitsOf(ctx, ti), defUnits: unitsOf(ctx, 1 - ti), dEnd: -1 };
    open.set(d.id, ep); return ep;
  }
  function closeEp(ep, round, exit, L) { ep.r1 = round; ep.exit = exit; ep.L1 = L; open.delete(ep.id); delete ep.near; E.push(ep); }
  // deaths: [ti, r, L, cause, relTerr, otherRel(0 none,1 ally,2 enemy), otherLen, blkE, raiderAge(-1), otherRaider, depth]
  const D = [];
  // location bins per team: sums over rounds of units own / neutral / enemy territory, raider length, rounds counted
  const LOC = [0, 1].map(() => ({ own: new Array(50).fill(0), neu: new Array(50).fill(0), en: new Array(50).fill(0), enLen: new Array(50).fill(0), rounds: new Array(50).fill(0), nearEF: new Array(50).fill(0) }));
  // coverage checkpoints per team (every 10 rounds)
  const C = [[], []];
  let capT = [0, 0, 0], capF = [0, 0, 0], nFount = [0, 0, 0];
  for (let k = 0; k < N; k++) { capT[terr[k]] += wgt[k]; if (fount[k]) { capF[terr[k]] += wgt[k]; nFount[terr[k]]++; } }
  // encounter counts ENC[ti][loc][relLen] = [pairs, closer, farther, same, dead]; relLen: ours shorter / equal / longer
  const ENC = [0, 1].map(() => [0, 1, 2].map(() => [0, 1, 2].map(() => [0, 0, 0, 0, 0])));
  const pend = [];
  let lastRound = -99, chkTerr = -1, spawnsSeen = 0;
  const chk = { terr: 0, spawnMismatch: 0 };

  function roundStart(round, ctx) {
    if (chkTerr < 0) { chkTerr = 0; for (let k = 0; k < N; k++) if (ctx.terr[k] !== terr[k]) chkTerr++; chk.terr = chkTerr; }
    heads[0] = []; heads[1] = [];
    for (const d of ctx.drag.values()) { const h = d.body[0]; heads[TI(d.team)].push({ t: G.key(h.x, h.y), len: d.body.length, id: d.id, d }); }
    bfsHeads(0); bfsHeads(1); markVis(0); markVis(1);
    // new natural pearls (spawned at this round's start)
    for (const [k, o] of ctx.pearls) {
      if (o !== -1 || known.has(k)) continue;
      const dA = dist[0][k] < 0 ? INF : dist[0][k], dB = dist[1][k] < 0 ? INF : dist[1][k];
      let xA = 0, xB = 0;
      if (dist[0][k] >= 0) { const id = srcId[0][k], dd = ctx.drag.get(id); if (dd) { const h = dd.body[0]; xA = terr[G.key(h.x, h.y)] === 2 ? 1 : 0; } }
      if (dist[1][k] >= 0) { const id = srcId[1][k], dd = ctx.drag.get(id); if (dd) { const h = dd.body[0]; xB = terr[G.key(h.x, h.y)] === 1 ? 1 : 0; } }
      const row = [round, k, terr[k], fount[k], G.marginA[k], dA, dB, vis[0][k], vis[1][k], dist[0][k] >= 0 ? srcLen[0][k] : 0, dist[1][k] >= 0 ? srcLen[1][k] : 0, xA, xB, 0, -1, 0, -1];
      P.push(row); known.set(k, row); spawnsSeen++;
    }
    // locations
    const b = Math.min(49, Math.floor(round / 10));
    for (const ti of [0, 1]) {
      const L = LOC[ti]; L.rounds[b]++;
      for (const h of heads[ti]) { const rt = relTerr(ti, h.t); if (rt === 0) L.own[b]++; else if (rt === 1) L.neu[b]++; else { L.en[b]++; L.enLen[b] += h.len; if (nearF[ENT(ti)][h.t]) L.nearEF[b]++; } }
    }
    // open raid episodes: distance of the nearest defender head, and whether the defenders near the raider close in
    for (const ep of open.values()) {
      const d = ctx.drag.get(ep.id); if (!d) continue;
      const h = d.body[0], k = G.key(h.x, h.y), di = 1 - ep.ti;
      const dd = dist[di][k] < 0 ? INF : dist[di][k];
      if (ep.upd === 0) {
        ep.dDef0 = dd; ep.k0 = k;
        localBfs(k, 8);
        ep.near = []; for (const x of heads[di]) { const z = lbGet(x.t); if (z <= 6) ep.near.push([x.id, z]); }
        ep.nDef6 = ep.near.length;
      } else if (ep.upd === 3 && ep.near) {
        // did the defenders that were within 6 move toward the tile where the raider stood 3 rounds ago?
        localBfs(ep.k0, 12); let a = 0, r = 0;
        for (const [id, z0] of ep.near) { const x = heads[di].find(q => q.id === id); if (!x) continue; const z = lbGet(x.t); if (z < z0) a++; else if (z > z0) r++; }
        ep.appr = a; ep.retr = r;
      }
      if (dd < ep.dDefMin) ep.dDefMin = dd;
      if (nearF[ENT(ep.ti)][k]) ep.fr++;
      ep.dEnd = dd;
      ep.upd++;
    }
    // encounters (every 5 rounds): our heads within 6 of an enemy head; 3 rounds later, are they closer to the tile where
    // that enemy head stood? Split by where the enemy head is (0 in our territory = a raid on us, 1 neutral, 2 its own).
    for (let i = pend.length - 1; i >= 0; i--) {
      const x = pend[i]; if (x.due > round) continue;
      pend.splice(i, 1);
      localBfs(x.t, 12);
      const a = ENC[x.ti][x.loc];
      for (const [id, z0, rl] of x.pairs) {
        const c = a[rl]; c[0]++;
        const h = heads[x.ti].find(q => q.id === id);
        if (!h) { c[4]++; continue; }
        const z = lbGet(h.t); if (z < z0) c[1]++; else if (z > z0) c[2]++; else c[3]++;
      }
    }
    if (round % 5 === 0) {
      for (const ti of [0, 1]) for (const e of heads[1 - ti]) {
        if (!(dist[ti][e.t] >= 0 && dist[ti][e.t] <= 6)) continue;
        localBfs(e.t, 8);
        const pairs = [];
        for (const h of heads[ti]) { const z = lbGet(h.t); if (z >= 1 && z <= 6) pairs.push([h.id, z, h.len < e.len ? 0 : h.len === e.len ? 1 : 2]); }
        if (pairs.length) pend.push({ due: round + 3, ti, t: e.t, loc: relTerr(ti, e.t), pairs });
      }
    }
    // coverage every 10 rounds
    if (round % 10 === 0) {
      for (const ti of [0, 1]) {
        const dO = dist[ti], dE = dist[1 - ti], own = OWNT(ti), en = ENT(ti);
        let vorOwn = 0, vorAll = 0, visOwn = 0, visEn = 0, near5 = 0, vorEn = 0, fHeld = 0, fHeldEn = 0, fVor = 0;
        for (let k = 0; k < N; k++) {
          const w = wgt[k]; if (!(w > 0)) continue;
          const a = dO[k] < 0 ? INF : dO[k], b2 = dE[k] < 0 ? INF : dE[k];
          const s = a < b2 ? 1 : a === b2 ? 0.5 : 0;
          vorAll += w * s;
          if (terr[k] === own) { vorOwn += w * s; if (vis[ti][k]) visOwn += w; if (a <= 5) near5 += w; if (fount[k]) { if (a <= 3) fHeld++; fVor += s; } }
          else if (terr[k] === en) { vorEn += w * s; if (vis[ti][k]) visEn += w; if (fount[k] && a <= 3) fHeldEn++; }
        }
        let units = 0, total = 0, uOwn = 0, uEn = 0;
        for (const h of heads[ti]) { units++; total += h.len; const rt = relTerr(ti, h.t); if (rt === 0) uOwn++; else if (rt === 2) uEn++; }
        // spacing: path distance from each head to its nearest ally head (capped at 13), and heads with an ally within 2
        let spSum = 0, spN = 0, near2 = 0;
        if (heads[ti].length >= 2) for (const h of heads[ti]) {
          localBfs(h.t, 12); let best = 13;
          for (const o of heads[ti]) { if (o === h) continue; const z = lbGet(o.t); if (z < best) best = z; }
          spSum += best; spN++; if (best <= 2) near2++;
        }
        const r3 = x => Math.round(x * 1000) / 1000;
        C[ti].push([round, units, total, uOwn, uEn, r3(vorOwn), r3(vorAll), r3(visOwn), r3(visEn), r3(near5), r3(vorEn), fHeld, fHeldEn, r3(fVor), spN ? r3(spSum / spN) : -1, near2]);
      }
    }
  }

  const hooks = {
    turn(d, round, ctx) { if (round !== lastRound) { lastRound = round; roundStart(round, ctx); } },
    action(d, e, round, ctx) {
      if (d.fate) return; // it dies on this move: the death hook closes its episode
      const h = d.body[0], k = G.key(h.x, h.y), ti = TI(d.team);
      const inE = terr[k] === ENT(ti);
      let ep = open.get(d.id);
      if (inE && !ep) ep = openEp(d, round, k, ctx);
      if (ep) {
        if (d.body.length > ep.Lmax) ep.Lmax = d.body.length;
        const dp = depthIn(ti, k); if (dp > ep.dmax) ep.dmax = dp;
        if (!inE) closeEp(ep, round, 0, d.body.length);
      }
    },
    eat(d, k, o, round, ctx) {
      const ti = TI(d.team), inE = terr[k] === ENT(ti);
      let ep = open.get(d.id);
      if (inE && !ep) ep = openEp(d, round, k, ctx);
      if (o < 0) {
        const row = known.get(k);
        if (row) { row[PR.eater] = ti + 1; row[PR.eatR] = round; row[PR.eatLen] = d.body.length; row[PR.eatAge] = ep ? round - ep.r0 : -1; known.delete(k); }
        if (ep && inE) { ep.nat++; if (fount[k]) ep.fnt++; }
      } else if (ep && inE) ep.drop++;
    },
    split(p, ch, e, round, ctx) { /* the child's first action opens its episode if it is born inside */ },
    death(d, rec, idx, other, round, ctx) {
      const ti = TI(d.team), h = d.body[0], k = G.key(h.x, h.y);
      const ep = open.get(d.id);
      const oRel = other ? (other.team === d.team ? 1 : 2) : 0;
      const oEp = other && oRel === 2 ? open.get(other.id) : null;
      D.push([ti, round, rec.len, rec.cause, relTerr(ti, k), oRel, other ? other.body.length : 0, rec.blk === 'e' ? 1 : 0, ep ? round - ep.r0 : -1, oEp ? 1 : 0, depthIn(ti, k)]);
      if (oEp && relTerr(ti, k) === 0) { if (rec.cause === 2 || rec.cause === 3) oEp.trades++; else oEp.kills++; }
      if (ep) { ep.cause = rec.cause; ep.killer = oRel; ep.killerLen = other ? other.body.length : 0; ep.blkE = rec.blk === 'e' ? 1 : 0; closeEp(ep, round, 1, rec.len); }
    },
    end(rounds, ctx) { for (const ep of [...open.values()]) { const d = ctx.drag.get(ep.id); closeEp(ep, rounds - 1, 2, d ? d.body.length : 0); } },
  };
  const g = ML.perGame(R, linfo, hooks);
  if (spawnsSeen !== g.natSpawned) chk.spawnMismatch = spawnsSeen - g.natSpawned;
  const team = tm => {
    const T = g[tm], fl = T.fl, sum = cat => fl[ML.FI[cat]].reduce((s, v) => s + v, 0);
    return { splits: T.splits, sonar: T.sonar, faults: sum('dn_fault'), natOwn: sum('nat_own'), natEnemy: sum('nat_enemy'), eatNat: sum('eat_nat'),
      units: T.st.units, total: T.st.total, king: T.st.king };
  };
  const epRow = ep => [ep.ti, ep.id, ep.r0, ep.r1, ep.L0, ep.Lmax, ep.L1, ep.nat, ep.fnt, ep.drop, ep.exit, ep.cause, ep.killer, ep.killerLen, ep.blkE, ep.dmax,
    ep.dDef0, ep.dDefMin, ep.nDef6, ep.appr, ep.retr, ep.kills, ep.trades, ep.born, ep.upd, ep.fr, ep.units, ep.defUnits, ep.dEnd];
  return {
    rounds: g.rounds, endReason: g.endReason, winner: g.winner, W, H, variant: V, chkLedger: g.chk, chk,
    capT: capT.map(x => Math.round(x * 1000) / 1000), capF: capF.map(x => Math.round(x * 1000) / 1000), nFount, nearFShare: [1, 2].map(tv => { let a = 0, b = 0; for (let k = 0; k < N; k++) if (terr[k] === tv) { b++; if (nearF[tv][k]) a++; } return b ? Math.round(1000 * a / b) / 1000 : 0; }),
    terrTiles: [0, 1, 2].map(v => terr.reduce((s, x) => s + (x === v ? 1 : 0), 0)),
    A: team('A'), B: team('B'), P, E: E.map(epRow), D, C, LOC, ENC,
  };
}

// ---------------------------------------------------------------------------------------------------------------
// Tasks and workers
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];
function topTasks(keysArg) {
  const seen = new Set(), idx = [];
  for (const r of readJsonl(path.join(TOP, 'index.jsonl'))) { const k = r.battleId + ':' + r.gameId; if (seen.has(k)) continue; seen.add(k); idx.push(r); }
  const byKey = new Map(idx.map(r => [r.battleId + ':' + r.gameId, r]));
  const keys = keysArg === 'all' ? [...byKey.keys()] : fs.readFileSync(path.resolve(ROOT, keysArg), 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  const out = [];
  for (const k of keys) {
    const r = byKey.get(k); if (!r) continue;
    const f = path.join(TOP, String(r.battleId), r.gameId + '.replay.gz'); if (!fs.existsSync(f)) continue;
    out.push({ key: k, file: f, info: { src: 'top', map: r.map, gameId: r.gameId, battleId: r.battleId, teamA: r.teamA, teamB: r.teamB, eloA: r.eloA, eloB: r.eloB,
      rankA: r.rankA, rankB: r.rankB, winnerIdx: r.winner ? String(r.winner).toUpperCase() : null, ranked: !!r.ranked, at: r.at, us: null } });
  }
  return out;
}
function onlineTasks(set) {
  const dir = path.join(ONLINE, set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  let names = {};
  try { for (const t of JSON.parse(fs.readFileSync(path.join(TOP, 'leaderboard.json'), 'utf8'))) names[t.id] = t.name; } catch { /* optional */ }
  const out = [];
  for (const g of idx.games || idx) {
    const f = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
    const us = String(g.ourSide).toUpperCase(), opp = names[g.opponentTeam] || String(g.opponentTeam);
    out.push({ key: set + ':' + g.gameId, file: f, info: { src: 'online', set, map: g.mapName, gameId: g.gameId, teamA: us === 'A' ? set : opp, teamB: us === 'B' ? set : opp,
      oppId: g.opponentTeam, winnerIdx: g.winner ? String(g.winner).toUpperCase() : null, at: g.completedAt, us, sub: g.ourSubmission } });
  }
  return out;
}
function workerMain() {
  const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
  const load = tf.makeLoader(tf.viewerSource());
  process.on('message', task => {
    try {
      const R = load(task.file);
      const res = analyse(R, task.info);
      process.send({ key: task.key, line: JSON.stringify({ key: task.key, ...task.info, seed: R.seed, ...res }) });
    } catch (err) { process.send({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 5).join(' | ') }); }
  });
}
function cachedKeys(file) {
  const done = new Set(); if (!fs.existsSync(file)) return done;
  let txt; try { txt = zlib.gunzipSync(fs.readFileSync(file)).toString(); } catch { return done; }
  for (const l of txt.split('\n')) { const m = /^\{"key":"([^"]+)"/.exec(l); if (m) done.add(m[1]); }
  return done;
}
async function extract(tasks, cacheFile, jobs, limit) {
  fs.mkdirSync(path.dirname(cacheFile), { recursive: true });
  const done = cachedKeys(cacheFile);
  const todo = tasks.filter(t => !done.has(t.key)).slice(0, limit);
  console.log(`${path.relative(ROOT, cacheFile)}: ${tasks.length} games, cached ${done.size}, to do ${todo.length} (jobs ${jobs})`);
  if (!todo.length) return;
  const fd = fs.openSync(cacheFile, 'a'), t0 = Date.now(), errors = [];
  let n = 0;
  await new Promise((resolve, reject) => {
    const queue = todo.slice(); let live = Math.min(jobs, queue.length);
    for (let i = 0, k = live; i < k; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced', execArgv: ['--max-old-space-size=3072'] });
      let finished = false;
      const next = () => { const t = queue.shift(); if (!t) { finished = true; w.kill(); if (--live === 0) resolve(); return; } w.send(t); };
      w.on('message', m => {
        if (m.error) { errors.push(m.key + ' ' + m.error); console.error('error', m.key, m.error); }
        else fs.writeSync(fd, zlib.gzipSync(m.line + '\n'));
        n++;
        if (n % 100 === 0) console.log(`  ${n}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
        next();
      });
      w.on('error', reject);
      w.on('exit', code => { if (!finished) reject(Error('worker exited unexpectedly with code ' + code)); });
      next();
    }
  });
  fs.closeSync(fd);
  console.log(`done ${n} in ${((Date.now() - t0) / 1000).toFixed(0)}s, errors ${errors.length}`);
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const jobs = Math.max(1, Math.min(4, +opt('jobs', 4))), limit = +opt('limit', Infinity);
  if (argv[0] === 'top') {
    const keys = opt('keys', null); if (!keys) throw Error('--keys <file|all> required');
    return extract(topTasks(keys), path.join(CACHE, opt('name', 'top-sample') + '.jsonl.gz'), jobs, limit);
  }
  if (argv[0] === 'online') {
    const sets = []; for (let i = 1; i < argv.length; i++) { if (argv[i].startsWith('--')) { i++; continue; } sets.push(argv[i]); }
    for (const s of sets) await extract(onlineTasks(s), path.join(CACHE, 'online-' + s + '.jsonl.gz'), jobs, limit);
    return;
  }
  if (argv[0] === 'one') { // debug: node extract.js one <replay file> <map name>
    const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
    const load = tf.makeLoader(tf.viewerSource());
    const t0 = Date.now(); const R = load(argv[1]); const t1 = Date.now();
    const res = analyse(R, { map: argv[2], gameId: argv[3] });
    console.log(JSON.stringify({ ms: [t1 - t0, Date.now() - t1], rounds: res.rounds, winner: res.winner, variant: res.variant, chk: res.chk, chkLedger: res.chkLedger,
      pearls: res.P.length, eps: res.E.length, deaths: res.D.length, capT: res.capT, nFount: res.nFount, terrTiles: res.terrTiles, A: { natOwn: res.A.natOwn, natEnemy: res.A.natEnemy }, B: { natOwn: res.B.natOwn, natEnemy: res.B.natEnemy },
      bytes: JSON.stringify(res).length }));
    return;
  }
  console.error('usage: see the header of exp/territory-analysis/extract.js'); process.exit(2);
}
module.exports = { analyse, geometry, variantOf, fileOf, gapsOfFile };
if (require.main === module) main().catch(err => { console.error(err); process.exit(1); });
