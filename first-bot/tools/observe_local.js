#!/usr/bin/env node
'use strict';
// observe_local.js — observation facts from a local benchmark folder (tools/eval.js output).
// Per game it rebuilds every dragon's body from the replay events and records: outcome, every death with its cause and
// the dragon it ran into (length, team, who moved), splits (round, child size), unit/length flow per round, pearls eaten,
// sonar use (what each ray stopped on, message values, our own message format) and static map features.
// It reads replays only (never bot sources).
//
// usage: node tools/observe_local.js [--eval exp/eval-r1] [--out <aggregate.json>] [--games-out <games.json>] [--filter <regex>]
//   prints the aggregate tables as JSON on stdout; --out writes {meta, aggregate}; --games-out writes the per-game facts
//   (every death, split, sampled flow; several MB for 160 games); --filter keeps games whose key opp:map:side:seed matches.
// library: const O = require('./tools/observe_local.js');
//   O.load(dir)                  replay parse with the format-2 sonar fix (see below)
//   O.analyzeGame(dir, {side})   facts for one game (side = our team letter)
//   O.aggregate(games)           tables over many analyzeGame results
//
// Replay format note (checked 2026-09-29 on exp/eval-r1): the viewer bundled with unswbc knows format 1, and
// tools/viewer.js only lifts its version check. In format 2 the SonarPing struct grew from 16 to 32 data bytes:
// the old u32 `value` at byte 8 is always 0, the real u64 message sits at byte 16 (little endian) and a stop code at
// byte 24. So tools/viewer.js reports value 0 for every ping. This loader reads byte 16 (as a decimal string) and
// byte 24 (`stop`). All other event structs have the same size in both formats (checked), so they parse unchanged.
// These offsets are the ones the unswbc 1.1.0 viewer uses (value64 = getUint64(16), hitKind = getUint16(24), enum
// UNKNOWN 0, EMPTY 1, KELP 2, ALLY 3, ALLY_HEAD 4, ENEMY 5, ENEMY_HEAD 6; UNSW/.unswbc-110/unswbc/replay-viewer.vsix).
// The mapping was also checked against the rebuilt board: 0 mismatches over 902,106 pings in exp/eval-r1 (STOP below).
// ALLY/ENEMY are relative to the sender; a ray that comes back to the sender counts as ALLY(_HEAD).
const fs = require('fs'), path = require('path'), cp = require('child_process'), vm = require('vm');
const ROOT = path.resolve(__dirname, '..');

// ---------------------------------------------------------------------------------------------------------------
// loader
let parseReplay = null;
function initParser() {
  if (parseReplay) return parseReplay;
  const { root } = require(path.join(__dirname, 'viewer.js'));   // same vsix as tools/viewer.js
  const vsix = path.join(root, '.venv-ppo/lib/python3.13/site-packages/unswbc/replay-viewer.vsix');
  let src = cp.execFileSync('unzip', ['-p', vsix, 'extension/dist/webview/webview.js'], { maxBuffer: 8 << 20 }).toString();
  src = src.slice(0, src.indexOf('var Af=B(')).replace('if(n.formatVersion>1)', 'if(n.formatVersion>2)');
  const getter = 'get value(){return $.getUint32(8,this)}';
  const ret = 'hitId:t._isHitId?t.hitId:void 0}';
  if (!src.includes(getter) || src.split(ret).length !== 2) throw new Error('observe_local: viewer bundle changed; sonar patch points not found');
  src = src.replace(getter, 'get value(){const z=_u(this).dataByteLength;if(z>=24)return((BigInt($.getUint32(20,this))<<32n)|BigInt($.getUint32(16,this))).toString();return String($.getUint32(8,this))}' +
    'get stopCode(){return _u(this).dataByteLength>=26?$.getUint16(24,this):-1}');
  src = src.replace(ret, 'hitId:t._isHitId?t.hitId:void 0,stop:t.stopCode}');
  src += 'globalThis.parseReplay=kf;})();';
  const ctx = { TextEncoder, TextDecoder }; vm.runInNewContext(src, ctx, { timeout: 5000 });
  return (parseReplay = ctx.parseReplay);
}
function load(dir) {
  const f = fs.readdirSync(dir).find(x => x.endsWith('.replay'));
  if (!f) throw new Error('no .replay in ' + dir);
  return initParser()(fs.readFileSync(path.join(dir, f)));
}

// ---------------------------------------------------------------------------------------------------------------
// map
const DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 };
function parseMap(text) {
  let W = 0, H = 0, sym = '', name = '';
  const tiles = [], edges = [], dragons = [];
  for (const line of text.split('\n')) {
    const t = line.trim().split(/\s+/);
    if (t[0] === 'MAP') { W = +t[1]; H = +t[2]; }
    else if (t[0] === 'SYMMETRY') sym = t[1];
    else if (t[0] === 'MAP_NAME') name = t.slice(1).join(' ');
    else if (t[0] === 'TILE') tiles.push([+t[1], +t[2], +t[3], +t[4]]);
    else if (t[0] === 'EDGE') edges.push([+t[1], +t[2], +t[3]]);
    else if (t[0] === 'DRAGON') { const n = +t[2], body = []; for (let k = 0; k < n; k++) body.push([+t[3 + 2 * k], +t[4 + 2 * k]]); dragons.push({ team: +t[1] ? 'B' : 'A', body }); }
  }
  // hK[y*W+x]: north edge of tile (x,y); vK[y*W+x]: west edge of tile (x,y). Row H / column W fold onto row 0 / column 0.
  const hK = new Int8Array(W * H), vK = new Int8Array(W * H), hP = new Int32Array(W * H).fill(-1), vP = new Int32Array(W * H).fill(-1);
  const portals = new Map();
  for (const [idx, kind, pid] of edges) {
    const row = Math.floor(idx / (W + 1)), col = idx % (W + 1);
    let o, x, y;
    if (row % 2 === 0) { o = 'h'; y = (row / 2) % H; x = col; if (x >= W) continue; }
    else { o = 'v'; y = (row - 1) / 2; x = col % W; if (y >= H) continue; }
    const K = o === 'h' ? hK : vK, P = o === 'h' ? hP : vP, i = y * W + x;
    if (kind > K[i]) { K[i] = kind; P[i] = pid; }
    if (kind === 2) {
      if (!portals.has(pid)) portals.set(pid, []);
      const L = portals.get(pid); if (!L.some(e => e.o === o && e.x === x && e.y === y)) L.push({ o, x, y });
    }
  }
  const spawn = tiles.filter(t => t[3] > 0);
  const kelp = [...hK, ...vK].filter(k => k === 1).length;
  const M = {
    W, H, sym, name, hK, vK, hP, vP, portals,
    features: {
      name, W, H, tiles: W * H, symmetry: sym, kelpEdges: kelp, portalPairs: portals.size,
      spawnTiles: spawn.length, meanGap: spawn.length ? +(spawn.reduce((s, t) => s + (t[2] + t[3]) / 2, 0) / spawn.length).toFixed(1) : null,
      // expected spawn attempts per round if every tile were free (each tile ~ 1 / mean gap)
      spawnPerRound: +spawn.reduce((s, t) => s + 2 / (t[2] + t[3]), 0).toFixed(2),
      dragonsPerTeam: dragons.filter(d => d.team === 'A').length, startLens: dragons.filter(d => d.team === 'A').map(d => d.body.length),
    },
  };
  // board structure ignoring dragons: connected regions (portals included), the region each team starts in, dead ends
  const comp = new Int32Array(W * H).fill(-1), sizes = [];
  for (let s = 0; s < W * H; s++) {
    if (comp[s] >= 0) continue;
    const id = sizes.length, q = [s]; comp[s] = id;
    for (let i = 0; i < q.length; i++) {
      const x = q[i] % W, y = Math.floor(q[i] / W);
      for (const d of ['N', 'E', 'S', 'W']) { const p = step(M, x, y, d); if (!p) continue; const k = p[1] * W + p[0]; if (comp[k] < 0) { comp[k] = id; q.push(k); } }
    }
    sizes.push(q.length);
  }
  const rate = new Map(); for (const t of spawn) { const c = comp[t[1] * W + t[0]]; rate.set(c, (rate.get(c) || 0) + 2 / (t[2] + t[3])); }
  const startComp = team => [...new Set(dragons.filter(d => d.team === team).map(d => comp[d.body[0][1] * W + d.body[0][0]]))];
  const ca = startComp('A'), cb = startComp('B');
  let deadEnds = 0;
  for (let k = 0; k < W * H; k++) { let open = 0; for (const d of ['N', 'E', 'S', 'W']) if (step(M, k % W, Math.floor(k / W), d)) open++; if (open === 1) deadEnds++; }
  // the same for team A's starts when portals are never used (open edges only)
  const seen = new Set(dragons.filter(d => d.team === 'A').map(d => d.body[0][1] * W + d.body[0][0])), q = [...seen];
  for (let i = 0; i < q.length; i++) {
    const x = q[i] % W, y = Math.floor(q[i] / W);
    for (const d of ['N', 'E', 'S', 'W']) { if (edgeKind(M, x, y, d) !== 0) continue; const p = step(M, x, y, d); const k = p[1] * W + p[0]; if (!seen.has(k)) { seen.add(k); q.push(k); } }
  }
  Object.assign(M.features, {
    components: sizes.length,
    startRegionTiles: ca.reduce((s, c) => s + sizes[c], 0),
    startRegionSpawnPerRound: +ca.reduce((s, c) => s + (rate.get(c) || 0), 0).toFixed(2),
    startRegionSpawnTiles: spawn.filter(t => ca.includes(comp[t[1] * W + t[0]])).length,
    startRegionTilesNoPortal: seen.size,
    startRegionSpawnTilesNoPortal: spawn.filter(t => seen.has(t[1] * W + t[0])).length,
    startRegionSpawnPerRoundNoPortal: +spawn.filter(t => seen.has(t[1] * W + t[0])).reduce((s, t) => s + 2 / (t[2] + t[3]), 0).toFixed(2),
    teamsShareRegion: ca.some(c => cb.includes(c)),
    deadEndTiles: deadEnds,
  });
  return M;
}
// destination of one step from (x,y) in direction d: [x,y], or null for kelp
function step(M, x, y, d) {
  const { W, H } = M; let K, P;
  if (d === 'N') { K = M.hK[y * W + x]; P = M.hP[y * W + x]; }
  else if (d === 'S') { const yy = (y + 1) % H; K = M.hK[yy * W + x]; P = M.hP[yy * W + x]; }
  else if (d === 'W') { K = M.vK[y * W + x]; P = M.vP[y * W + x]; }
  else { const xx = (x + 1) % W; K = M.vK[y * W + xx]; P = M.vP[y * W + xx]; }
  if (K === 1) return null;
  if (K === 2) {
    const pair = M.portals.get(P) || [];
    const here = d === 'N' ? { o: 'h', x, y } : d === 'S' ? { o: 'h', x, y: (y + 1) % H } : d === 'W' ? { o: 'v', x, y } : { o: 'v', x: (x + 1) % W, y };
    const other = pair.find(e => !(e.o === here.o && e.x === here.x && e.y === here.y));
    if (other) {
      if (other.o === 'h') return d === 'N' ? [other.x, (other.y - 1 + H) % H] : [other.x, other.y];
      return d === 'W' ? [(other.x - 1 + W) % W, other.y] : [other.x, other.y];
    }
  }
  return [(x + DX[d] + W) % W, (y + DY[d] + H) % H];
}

// kind of the edge crossed by a step from (x,y) in direction d: 0 open, 1 kelp, 2 portal
function edgeKind(M, x, y, d) {
  const { W, H } = M;
  if (d === 'N') return M.hK[y * W + x];
  if (d === 'S') return M.hK[((y + 1) % H) * W + x];
  if (d === 'W') return M.vK[y * W + x];
  return M.vK[y * W + (x + 1) % W];
}

// ---------------------------------------------------------------------------------------------------------------
// our own message format (bot/world.cpp encodeMsg / encodeKingMsg), used only to classify our pings
const MSG_WHITEN = 0x9E3779B97F4A7C15n;
function decodeOurs(value) {
  let v; try { v = BigInt(value); } catch { return null; }
  v ^= MSG_WHITEN;
  const g = (s, m) => Number((v >> BigInt(s)) & BigInt(m));
  const magic = g(58, 63); if (magic !== 0x2D && magic !== 0x1B) return null;
  const relay = magic === 0x1B;
  const m = { relay, id: g(50, 255), round: g(41, 511), x: g(35, 63), y: g(29, 63), len: g(21, 255), hx: g(15, 63), hy: g(9, 63), team: g(8, 1) };
  const chk = (m.id * 131 + m.round * 7 + m.x * 17 + m.y * 31 + m.len * 3 + m.hx * 5 + m.hy * 13 + m.team * 101 + (relay ? 0x7F : 0x2A)) & 255;
  return chk === g(0, 255) ? m : null;
}

// ---------------------------------------------------------------------------------------------------------------
// one game
const STOP = { 1: 'none', 2: 'kelp', 3: 'ally', 4: 'allyHead', 5: 'enemy', 6: 'enemyHead' };
const PHASE_ROUND = 300;             // sonar phases: before / from round 300 (our bot broadcasts on all four rays from 300)
const FLOW_EVERY = 10;               // per-game flow sampled every 10 rounds, plus FLOW_MARKS and the final state
const FLOW_MARKS = [25];             // flowTable checkpoints that are not multiples of FLOW_EVERY (sampled exactly)

function analyzeGame(dir, meta) {
  const R = load(dir), M = parseMap(R.map);
  const us = meta.side, them = us === 'A' ? 'B' : 'A';
  const rel = t => (t === us ? 'us' : 'them');
  const key = (x, y) => y * M.W + x;
  const alive = new Map();            // id -> {id, team, body:[[x,y]...], born, maxLen}
  const teamOf = new Map();
  for (const d of R.match.map.initialDragons) {
    alive.set(d.id, { id: d.id, team: d.team, body: d.body.map(p => [p.x, p.y]), born: 0, maxLen: d.body.length, facing: d.facing, hist: [[-1, d.body[0].x, d.body[0].y]] });
    teamOf.set(d.id, d.team);
  }
  // head position at the end of round R (from the last few updates), toroidal Manhattan distance between two dragons' heads
  const posAt = (d, R) => { for (let i = d.hist.length - 1; i >= 0; i--) if (d.hist[i][0] <= R) return d.hist[i]; return null; };
  const dist = (a, b) => { if (!a || !b) return null; const dx = Math.abs(a[1] - b[1]), dy = Math.abs(a[2] - b[2]); return Math.min(dx, M.W - dx) + Math.min(dy, M.H - dy); };
  const approach = (mover, victim, R) => ({ d1: dist(posAt(mover, R - 1), posAt(victim, R - 1)), d3: dist(posAt(mover, R - 3), posAt(victim, R - 3)), d5: dist(posAt(mover, R - 5), posAt(victim, R - 5)) });
  const OPPDIR = { N: 'S', S: 'N', E: 'W', W: 'E' };
  const lastSplitIdx = new Map();     // parent id -> index in splits of its latest split
  const check = { moves: 0, moveMismatch: 0, bodyMismatch: 0, splitMismatch: 0, deathChecked: 0, deathMismatch: 0, finalMismatch: 0, stopMismatch: 0 };
  const stopTab = {};                 // stop code x board class (for the STOP table)
  const deaths = [], splits = [];
  const flow = { us: { n: [], max: [], tot: [], eat: [] }, them: { n: [], max: [], tot: [], eat: [] } };
  const eaten = { us: 0, them: 0 }; let spawns = 0, drops = 0; const pearls = new Set();
  const son = {
    us: { pings: 0, turnsWithPing: 0, byStop: { pre: {}, post: {} }, dirs: {}, valuesZero: 0, ours: { main: 0, relay: 0, other: 0 }, distinct: new Set() },
    them: { pings: 0, turnsWithPing: 0, byStop: { pre: {}, post: {} }, dirs: {}, valuesZero: 0, ours: { main: 0, relay: 0, other: 0 }, distinct: new Set(), sample: [] },
  };
  const turns = { us: 0, them: 0 };
  const sprints = { us: 0, them: 0 }, moves = { us: 0, them: 0 };
  let r = 0, cur = -1, action = null, stepIdx = 0, pingThisTurn = false, pendingH = null, lastInd = new Map(), sprintPending = -1;
  const portalSteps = { us: 0, them: 0 };
  const sprintCost = { us: 0, them: 0 }, sprintCostLong = { us: 0, them: 0 }, sprintCostByRound = { us: [0, 0, 0, 0, 0], them: [0, 0, 0, 0, 0] };

  const snapshot = () => {
    const s = { us: { n: 0, max: 0, tot: 0 }, them: { n: 0, max: 0, tot: 0 } };
    for (const d of alive.values()) { const t = s[rel(d.team)]; t.n++; t.tot += d.body.length; t.max = Math.max(t.max, d.body.length); }
    for (const w of ['us', 'them']) { flow[w].n.push(s[w].n); flow[w].max.push(s[w].max); flow[w].tot.push(s[w].tot); flow[w].eat.push(eaten[w]); }
  };
  const endTurn = () => { if (cur >= 0 && pingThisTurn) son[rel(teamOf.get(cur))].turnsWithPing++; pingThisTurn = false; };
  const occupant = (x, y) => {       // [dragon, segmentIndex] at tile, or null
    for (const d of alive.values()) { const i = d.body.findIndex(p => p[0] === x && p[1] === y); if (i >= 0) return [d, i]; }
    return null;
  };

  for (const e of R.events) {
    switch (e.type) {
      case 'roundStart':
        endTurn();
        if (e.round > 0) snapshot();   // state at the end of round e.round-1
        r = e.round; cur = -1; action = null; break;
      case 'turnStart':
        endTurn();
        cur = e.id; action = null; stepIdx = 0; pendingH = null; sprintPending = -1;
        if (teamOf.has(cur)) turns[rel(teamOf.get(cur))]++;
        break;
      case 'dragonIndicator': lastInd.set(e.id, { r, text: e.text }); break;
      case 'dragonAction': {
        action = e.action;
        const w = rel(teamOf.get(e.id));
        if (action && action.kind === 'move') { moves[w]++; if (action.steps.length > 1) sprints[w]++; }
        sprintPending = action && action.kind === 'move' && action.steps.length > 1 ? e.id : -1;
        break;
      }
      case 'tileChange':
        if (e.hasPearl) { pearls.add(key(e.tile.x, e.tile.y)); if (cur < 0) spawns++; else drops++; }
        else { pearls.delete(key(e.tile.x, e.tile.y)); if (cur >= 0) eaten[rel(teamOf.get(cur))]++; }
        break;
      case 'dragonUpdate': {
        const d = alive.get(e.id); if (!d) { check.bodyMismatch++; break; }
        const h = [e.head.x, e.head.y], t = [e.tail.x, e.tail.y];
        if (action && action.kind === 'move' && e.id === cur && stepIdx < action.steps.length) {
          check.moves++;
          const p = step(M, d.body[0][0], d.body[0][1], action.steps[stepIdx]);
          if (!p || p[0] !== h[0] || p[1] !== h[1]) check.moveMismatch++;
          if (edgeKind(M, d.body[0][0], d.body[0][1], action.steps[stepIdx]) === 2) portalSteps[rel(d.team)]++;
        }
        stepIdx++;
        // every step after the first costs one segment (paid only for steps actually taken)
        if (e.id === sprintPending && stepIdx >= 2) {
          const w = rel(d.team); sprintCost[w]++; sprintCostByRound[w][Math.min(4, Math.floor(r / 100))]++;
          if (d.body.length >= 10) sprintCostLong[w]++;
        }
        if (d.body[0][0] !== h[0] || d.body[0][1] !== h[1]) d.body.unshift(h);
        while (d.body.length > 1 && (d.body[d.body.length - 1][0] !== t[0] || d.body[d.body.length - 1][1] !== t[1])) d.body.pop();
        if (d.body.length < 2) check.bodyMismatch++;
        d.maxLen = Math.max(d.maxLen, d.body.length);
        d.facing = e.facing;
        if (d.hist.at(-1)[0] === r) d.hist[d.hist.length - 1] = [r, h[0], h[1]]; else { d.hist.push([r, h[0], h[1]]); if (d.hist.length > 8) d.hist.shift(); }
        break;
      }
      case 'dragonSplit': {
        const p = alive.get(e.parentId); if (!p) { check.splitMismatch++; break; }
        const before = p.body.length, pb = e.parentBody.map(q => [q.x, q.y]), cb = e.childBody.map(q => [q.x, q.y]);
        if (pb.length + cb.length !== before) check.splitMismatch++;
        // context before the split: is the tile straight ahead blocked (kelp or any body), how many non-reverse exits are free
        const [hx, hy] = p.body[0];
        const fwd = p.facing ? step(M, hx, hy, p.facing) : null;
        const fwdBlocked = !fwd || !!occupant(fwd[0], fwd[1]);
        let exits = 0;
        for (const dd of ['N', 'E', 'S', 'W']) { if (dd === OPPDIR[p.facing]) continue; const q = step(M, hx, hy, dd); if (q && !occupant(q[0], q[1])) exits++; }
        const li = lastInd.get(e.parentId);
        p.body = pb; p.lastSplitR = r;
        alive.set(e.childId, { id: e.childId, team: e.team, body: cb, born: r, maxLen: cb.length, facing: e.childFacing, hist: [[r, cb[0][0], cb[0][1]]] });
        teamOf.set(e.childId, e.team);
        lastSplitIdx.set(e.parentId, splits.length);
        splits.push({ r, team: rel(e.team), parent: e.parentId, child: e.childId, lenBefore: before, childLen: cb.length, parentLen: pb.length, fwdBlocked, exits, ...(li && li.r === r ? { ind: li.text } : {}) });
        break;
      }
      case 'dragonDeath': {
        const d = alive.get(e.id); if (!d) { check.bodyMismatch++; break; }
        let teamMaxOther = 0;             // longest other living teammate at this moment
        for (const o of alive.values()) if (o.team === d.team && o.id !== d.id) teamMaxOther = Math.max(teamMaxOther, o.body.length);
        const rec = { r, id: e.id, team: rel(d.team), reason: e.reason, len: d.body.length, maxLen: d.maxLen, born: d.born, mover: e.id === cur, teamMaxOther };
        const li = lastInd.get(e.id); if (li && li.r === r) rec.ind = li.text;
        // our bot prints "feed #<id>" when it sacrifices itself for teammate <id>: record that target's state now
        const fm = rec.ind && /^feed #(\d+)/.exec(rec.ind);
        if (fm) { const t = alive.get(+fm[1]); Object.assign(rec, { feedTarget: +fm[1], feedTargetLen: t ? t.body.length : null, feedTargetTeam: t ? rel(t.team) : null }); }
        if (d.lastSplitR !== undefined) {
          rec.sinceSplit = r - d.lastSplitR;
          const si = lastSplitIdx.get(e.id);
          if (si !== undefined && splits[si].r === d.lastSplitR) Object.assign(splits[si], { parentDiedAfter: r - d.lastSplitR, parentDeath: e.reason });
        }
        if (rec.mover) {
          const dir = action && action.kind === 'move' ? action.steps[stepIdx] : null;
          rec.step = dir || (action ? action.kind : 'none');
          rec.stepNo = stepIdx + 1;
          if (dir) {
            const p = step(M, d.body[0][0], d.body[0][1], dir);
            check.deathChecked++;
            if (!p) { if (e.reason !== 'W') check.deathMismatch++; }
            else if (e.reason === 'H') {
              if (!pendingH) check.deathMismatch++;
              else Object.assign(rec, { byId: pendingH.id, byTeam: pendingH.team, byLen: pendingH.len, byBorn: pendingH.dragon.born, byMoved: false, approach: approach(d, pendingH.dragon, r) });
            } else {
              const o = occupant(p[0], p[1]);
              if (!o) check.deathMismatch++;
              else {
                const [od, oi] = o;
                if (e.reason === 'S' ? od.id !== d.id : (od.id === d.id || oi === 0)) check.deathMismatch++;
                if (e.reason === 'O') Object.assign(rec, { byId: od.id, byTeam: rel(od.team), byLen: od.body.length, bySeg: oi, byTail: oi === od.body.length - 1, byMoved: false });
              }
            }
          }
        } else if (e.reason === 'H' && cur >= 0) {
          const m = alive.get(cur);
          Object.assign(rec, { byId: cur, byTeam: m ? rel(m.team) : null, byLen: m ? m.body.length : null, byBorn: m ? m.born : null, byMoved: true, ...(m ? { approach: approach(m, d, r) } : {}) });
          pendingH = { id: e.id, team: rel(d.team), len: d.body.length, dragon: d };
        }
        deaths.push(rec);
        alive.delete(e.id);
        break;
      }
      case 'sonarPing': {
        const w = rel(teamOf.get(e.senderId)), S = son[w];
        S.pings++; pingThisTurn = true;
        S.dirs[e.direction] = (S.dirs[e.direction] || 0) + 1;
        // board class of the stop point
        // no dragon: kelp if the edge ahead of the stop tile is kelp, otherwise the ray ran out (WIDTH+HEIGHT tiles)
        let cls = step(M, e.end.x, e.end.y, e.direction) === null ? 'kelpGeom' : 'lostGeom';
        if (e.hitId !== undefined) {
          const h = alive.get(e.hitId);
          const isHead = h && h.body[0][0] === e.end.x && h.body[0][1] === e.end.y;
          if (e.hitId === e.senderId) cls = isHead ? 'selfHead' : 'self';
          else if (h && h.team === teamOf.get(e.senderId)) cls = isHead ? 'allyHead' : 'ally';
          else cls = isHead ? 'enemyHead' : 'enemy';
        }
        const tk = e.stop + ':' + cls; stopTab[tk] = (stopTab[tk] || 0) + 1;
        const s = STOP[e.stop] || ('code' + e.stop);
        const geom = cls.endsWith('Geom');
        if (geom ? s !== (cls === 'kelpGeom' ? 'kelp' : 'none') : (cls.startsWith('self') ? !s.startsWith('ally') : !cls.startsWith(s.replace('Head', '')) || cls.endsWith('Head') !== s.endsWith('Head'))) check.stopMismatch++;
        const lab = cls.startsWith('self') ? cls : (geom ? s : cls);
        const ph = r < PHASE_ROUND ? 'pre' : 'post';
        S.byStop[ph][lab] = (S.byStop[ph][lab] || 0) + 1;
        if (e.value === '0') S.valuesZero++;
        if (S.distinct.size < 5000) S.distinct.add(e.value);
        const m = decodeOurs(e.value);
        if (m) S.ours[m.relay ? 'relay' : 'main']++; else S.ours.other++;
        if (w === 'them' && S.sample.length < 200) S.sample.push({ r, id: e.senderId, dir: e.direction, value: e.value, hitId: e.hitId, stop: e.stop, origin: e.origin });
        break;
      }
    }
  }
  endTurn();
  snapshot();                                           // final state (after the last round)
  const lastRound = r;
  // cross-check against the engine's result
  const res = R.result, mine = res['team' + us], theirs = res['team' + them];
  const fin = i => ({ n: flow[i].n.at(-1), max: flow[i].max.at(-1), tot: flow[i].tot.at(-1) });
  const fu = fin('us'), ft = fin('them');
  if (fu.n !== mine.dragonCount || fu.max !== mine.longestDragon || fu.tot !== mine.totalLength) check.finalMismatch++;
  if (ft.n !== theirs.dragonCount || ft.max !== theirs.longestDragon || ft.tot !== theirs.totalLength) check.finalMismatch++;

  // flow landmarks: flow index i = state at the end of round i
  const U = flow.us.max, T = flow.them.max, n = U.length;
  let firstBehind = -1, lastLead = -1;
  for (let i = 0; i < n; i++) { if (T[i] > U[i] && firstBehind < 0) firstBehind = i; if (U[i] >= T[i]) lastLead = i; }
  const behindAtEnd = U[n - 1] < T[n - 1];
  let bigDrop = { round: -1, drop: 0 };
  for (let i = 1; i < n; i++) if (U[i - 1] - U[i] > bigDrop.drop) bigDrop = { round: i, drop: U[i - 1] - U[i], from: U[i - 1] };
  // sampled rounds (flow index i = state at the end of round i): every FLOW_EVERY-th round, the FLOW_MARKS rounds, the final state.
  // flowSampled.rounds lists them so that flowTable reads a checkpoint at its exact round (2026-09-29 fix: before, the '25' and
  // '499' checkpoints read the samples of rounds 20 and 490).
  const sampledRounds = U.map((_, i) => i).filter(i => i % FLOW_EVERY === 0 || FLOW_MARKS.includes(i) || i === n - 1);
  const sample = a => sampledRounds.map(i => a[i]);
  const finSon = w => { const S = son[w]; return { pings: S.pings, turns: turns[w], turnsWithPing: S.turnsWithPing, byStop: S.byStop, dirs: S.dirs, valuesZero: S.valuesZero, distinct: S.distinct.size, ours: S.ours, ...(w === 'them' ? { sample: S.sample } : {}) }; };
  return {
    key: meta.key, opp: meta.opp, map: meta.map, side: us, seed: meta.seed,
    won: res.winner === us, draw: !res.winner, alive: mine.dragonCount > 0, G: mine.dragonCount > 0 ? mine.longestDragon : 0,
    endReason: res.endReason, lastRound, map_: M.features,
    final: { us: fu, them: ft },
    flowSampled: { every: FLOW_EVERY, rounds: sampledRounds, us: { n: sample(flow.us.n), max: sample(flow.us.max), tot: sample(flow.us.tot), eat: sample(flow.us.eat) }, them: { n: sample(flow.them.n), max: sample(flow.them.max), tot: sample(flow.them.tot), eat: sample(flow.them.eat) } },
    landmarks: { firstBehind, lastLead, behindAtEnd, fallBehind: behindAtEnd ? lastLead + 1 : null, peakUs: Math.max(...U), peakThem: Math.max(...T), bigDrop },
    deaths, splits, eaten, spawns, drops, pearlsLeft: pearls.size, sonar: { us: finSon('us'), them: finSon('them') }, moves, sprints, turns, check, stopTab,
    sprintCost, sprintCostLong, sprintCostByRound, portalSteps,
  };
}

// ---------------------------------------------------------------------------------------------------------------
// aggregation
const mean = a => (a.length ? a.reduce((s, x) => s + x, 0) / a.length : null);
const r1 = x => (x === null || x === undefined ? null : Math.round(x * 10) / 10);
const r3 = x => (x === null || x === undefined ? null : Math.round(x * 1000) / 1000);
const quant = (a, q) => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(q * s.length))]; };
const inc = (o, k, v = 1) => { o[k] = (o[k] || 0) + v; };
const lenBucket = L => (L <= 2 ? '2' : L <= 3 ? '3' : L <= 5 ? '4-5' : L <= 9 ? '6-9' : L <= 19 ? '10-19' : '20+');

function outcome(gs) {
  return { n: gs.length, win: r3(mean(gs.map(g => +g.won))), draw: gs.filter(g => g.draw).length, alive: r3(mean(gs.map(g => +g.alive))), G: r1(mean(gs.map(g => g.G))), Gmed: quant(gs.map(g => g.G), 0.5), theirLongest: r1(mean(gs.map(g => g.final.them.max))), eliminated: gs.filter(g => !g.alive).length, oppEliminated: gs.filter(g => g.final.them.n === 0).length };
}
function deathTable(ds) {
  const out = { n: ds.length, mass: ds.reduce((s, d) => s + d.len, 0), byReason: {}, byReasonMass: {}, lenBuckets: {}, feed: 0, feedMass: 0 };
  for (const d of ds) { inc(out.byReason, d.reason); inc(out.byReasonMass, d.reason, d.len); inc(out.lenBuckets, lenBucket(d.len)); if ((d.ind || '').startsWith('feed')) { out.feed++; out.feedMass += d.len; } }
  return out;
}
function killerTable(ds) {             // our deaths caused by another dragon (H, O)
  const t = { H: { n: 0, mass: 0, theyMoved: 0, weMoved: 0, byTeam: {}, byLen: {}, byLenMass: {}, ourLen: {}, massTraded: { ours: 0, theirs: 0 } }, O: { n: 0, mass: 0, byTeam: {}, byLen: {}, intoTail: 0 } };
  for (const d of ds) {
    if (d.reason === 'H') {
      const h = t.H; h.n++; h.mass += d.len; inc(h.byTeam, d.byTeam || '?');
      if (d.byMoved) h.theyMoved++; else h.weMoved++;
      if (d.byTeam === 'them') { inc(h.byLen, lenBucket(d.byLen)); inc(h.byLenMass, lenBucket(d.byLen), d.len); h.massTraded.ours += d.len; h.massTraded.theirs += d.byLen || 0; }
      inc(h.ourLen, lenBucket(d.len));
    } else if (d.reason === 'O') {
      const o = t.O; o.n++; o.mass += d.len; inc(o.byTeam, d.byTeam || '?'); if (d.byTeam === 'them') inc(o.byLen, lenBucket(d.byLen)); if (d.byTail) o.intoTail++;
    }
  }
  return t;
}
function splitTable(gs, who) {
  const sp = gs.flatMap(g => g.splits.filter(s => s.team === who));
  const firsts = gs.map(g => { const s = g.splits.find(x => x.team === who); return s ? s.r : null; }).filter(x => x !== null);
  const byBin = {}; for (const s of sp) inc(byBin, String(Math.floor(s.r / 50) * 50));
  const child = {}; for (const s of sp) inc(child, lenBucket(s.childLen));
  const parent = {}; for (const s of sp) inc(parent, lenBucket(s.parentLen));
  return {
    splitsPerGame: r1(sp.length / gs.length), gamesWithSplit: firsts.length, firstSplit: { min: quant(firsts, 0), q25: quant(firsts, 0.25), med: quant(firsts, 0.5), q75: quant(firsts, 0.75) },
    childLen: child, childLenMean: r1(mean(sp.map(s => s.childLen))), parentLenAfter: parent, lenBeforeMean: r1(mean(sp.map(s => s.lenBefore))), byRound50: byBin,
  };
}
function flowTable(gs, marks = [0, 25, 50, 100, 150, 200, 250, 300, 350, 400, 450, 499]) {
  // state at the end of round rr; a game that ended before rr keeps its final state (so '499' = end of game)
  const at = (g, w, k, rr) => {
    const f = g.flowSampled, a = f[w][k], R = f.rounds;
    if (!R) throw new Error('flowTable: flowSampled.rounds missing (re-run analyzeGame)');
    if (rr >= R[R.length - 1]) return a[a.length - 1];
    const i = R.indexOf(rr);
    if (i < 0) throw new Error(`flowTable: round ${rr} not sampled in ${g.key}`);
    return a[i];
  };
  const rows = {};
  for (const m of marks) {
    const um = gs.map(g => at(g, 'us', 'max', m)), tm = gs.map(g => at(g, 'them', 'max', m));
    rows[m] = { usMax: r1(mean(um)), themMax: r1(mean(tm)), behind: r3(mean(gs.map((g, i) => +(tm[i] > um[i])))), usN: r1(mean(gs.map(g => at(g, 'us', 'n', m)))), themN: r1(mean(gs.map(g => at(g, 'them', 'n', m)))), usTot: r1(mean(gs.map(g => at(g, 'us', 'tot', m)))), themTot: r1(mean(gs.map(g => at(g, 'them', 'tot', m)))), usEat: r1(mean(gs.map(g => at(g, 'us', 'eat', m)))), themEat: r1(mean(gs.map(g => at(g, 'them', 'eat', m)))) };
  }
  return rows;
}
function sonarTable(gs, who) {
  const t = { games: gs.length, gamesWithPings: 0, pings: 0, turns: 0, turnsWithPing: 0, pre: {}, post: {}, valuesZero: 0, ours: { main: 0, relay: 0, other: 0 }, distinctMax: 0 };
  for (const g of gs) {
    const s = g.sonar[who]; if (s.pings) t.gamesWithPings++;
    t.pings += s.pings; t.turns += s.turns; t.turnsWithPing += s.turnsWithPing; t.valuesZero += s.valuesZero; t.distinctMax = Math.max(t.distinctMax, s.distinct);
    for (const ph of ['pre', 'post']) for (const [k, v] of Object.entries(s.byStop[ph])) inc(t[ph], k, v);
    for (const k of ['main', 'relay', 'other']) t.ours[k] += s.ours[k];
  }
  return t;
}
function aggregate(games) {
  const opps = [...new Set(games.map(g => g.opp))], maps = [...new Set(games.map(g => g.map))].sort();
  const A = { n: games.length, check: {}, stopTab: {}, outcome: { all: outcome(games), byOpp: {}, byMap: {}, oppMap: {} } };
  for (const g of games) { for (const [k, v] of Object.entries(g.check)) inc(A.check, k, v); for (const [k, v] of Object.entries(g.stopTab)) inc(A.stopTab, k, v); }
  for (const o of opps) A.outcome.byOpp[o] = outcome(games.filter(g => g.opp === o));
  for (const m of maps) A.outcome.byMap[m] = outcome(games.filter(g => g.map === m));
  for (const o of opps) { A.outcome.oppMap[o] = {}; for (const m of maps) { const gs = games.filter(g => g.opp === o && g.map === m); A.outcome.oppMap[o][m] = { G: r1(mean(gs.map(g => g.G))), wins: gs.filter(g => g.won).length, n: gs.length, alive: gs.filter(g => g.alive).length }; } }
  // our deaths
  const ours = gs => gs.flatMap(g => g.deaths.filter(d => d.team === 'us').map(d => ({ ...d, opp: g.opp, map: g.map, key: g.key, won: g.won })));
  const theirs = gs => gs.flatMap(g => g.deaths.filter(d => d.team === 'them').map(d => ({ ...d, opp: g.opp, map: g.map })));
  A.ourDeaths = { all: deathTable(ours(games)), byOpp: {}, byMap: {}, killers: {}, big: {} };
  for (const o of opps) {
    const ds = ours(games.filter(g => g.opp === o));
    A.ourDeaths.byOpp[o] = deathTable(ds);
    A.ourDeaths.killers[o] = killerTable(ds);
    A.ourDeaths.big[o] = deathTable(ds.filter(d => d.len >= 10));
  }
  for (const m of maps) A.ourDeaths.byMap[m] = deathTable(ours(games.filter(g => g.map === m)));
  // our lost length per opponent x map by cause (reason, other team, who moved; feed separated)
  A.ourDeaths.massByCauseOppMap = {};
  for (const o of opps) {
    A.ourDeaths.massByCauseOppMap[o] = {};
    for (const m of maps) {
      const t = {};
      for (const d of ours(games.filter(g => g.opp === o && g.map === m))) inc(t, (d.ind || '').startsWith('feed') ? 'feed' : d.reason + (d.byTeam ? ':' + d.byTeam + (d.byMoved ? '(they moved)' : '') : ''), d.len);
      A.ourDeaths.massByCauseOppMap[o][m] = t;
    }
  }
  // head-on collisions between the teams, from our side: they moved into our head / we moved into theirs
  const ageBucket = a => (a === null || a === undefined ? '?' : a <= 2 ? '0-2' : a <= 10 ? '3-10' : a <= 50 ? '11-50' : '51+');
  const headOn = ds => {
    const t = { n: ds.length, ourMass: 0, theirMass: 0, otherLen: {}, otherAge: {}, ourLen: {}, byRound100: {}, byMap: {}, ourLen10plus: 0, ourMass10plus: 0, approach: { withD5: 0, closing: 0, d5med: null, d1med: null, d5ge4: 0 } };
    const d5s = [], d1s = [];
    for (const d of ds) {
      t.ourMass += d.len; t.theirMass += d.byLen || 0;
      inc(t.byMap, d.map); inc(t.otherLen, lenBucket(d.byLen)); inc(t.otherAge, ageBucket(d.byBorn === null || d.byBorn === undefined ? null : d.r - d.byBorn)); inc(t.ourLen, lenBucket(d.len)); inc(t.byRound100, String(Math.floor(d.r / 100) * 100));
      if (d.len >= 10) { t.ourLen10plus++; t.ourMass10plus += d.len; }
      const a = d.approach; if (a && a.d5 !== null && a.d1 !== null) { t.approach.withD5++; if (a.d1 < a.d5) t.approach.closing++; if (a.d5 >= 4) t.approach.d5ge4++; d5s.push(a.d5); d1s.push(a.d1); }
    }
    t.approach.d5med = quant(d5s, 0.5); t.approach.d1med = quant(d1s, 0.5);
    return t;
  };
  A.headOn = {};
  for (const o of opps) {
    const ds = ours(games.filter(g => g.opp === o)).filter(d => d.reason === 'H' && d.byTeam === 'them');
    A.headOn[o] = { theyMoved: headOn(ds.filter(d => d.byMoved)), weMoved: headOn(ds.filter(d => !d.byMoved)) };
  }
  // our deaths by the indicator our bot printed on that turn (first word), with reason
  A.ourDeathIndicator = {};
  for (const d of ours(games)) { const k = (d.ind || 'none').split(' ')[0].replace(/[0-9]+$/, ''); const t = A.ourDeathIndicator[k] || (A.ourDeathIndicator[k] = { n: 0, mass: 0, byReason: {}, byMap: {} }); t.n++; t.mass += d.len; inc(t.byReason, d.reason); inc(t.byMap, d.map); }
  // deaths of our team's longest dragon (strictly longer than every other living teammate): cause, and the drop in our longest
  A.ourLongestDeaths = {};
  for (const o of opps) {
    const ds = ours(games.filter(g => g.opp === o)).filter(d => d.len > d.teamMaxOther && d.len >= 5);
    const t = { n: ds.length, lostToNextLongest: ds.reduce((s, d) => s + d.len - d.teamMaxOther, 0), byCause: {}, byCauseDrop: {}, feedWithPartnerAtMostHalf: 0 };
    for (const d of ds) {
      const k = d.reason === 'S' && (d.ind || '').startsWith('feed') ? 'feed' : d.reason + (d.byTeam ? ':' + d.byTeam + (d.byMoved ? '(they moved)' : '') : '');
      inc(t.byCause, k); inc(t.byCauseDrop, k, d.len - d.teamMaxOther);
      if (k === 'feed' && d.teamMaxOther * 2 <= d.len) t.feedWithPartnerAtMostHalf++;
    }
    A.ourLongestDeaths[o] = t;
  }
  // feeding sacrifices ("feed #<id>"): is the target alive, on our team, and longer than the feeder?
  A.feed = {};
  for (const o of opps) {
    const gs = games.filter(g => g.opp === o);
    const parentOf = new Map(gs.flatMap(g => g.splits.filter(s => s.team === 'us').map(s => [g.key + '#' + s.child, s.parent])));
    const ds = ours(gs).filter(d => d.feedTarget !== undefined);
    const t = { n: ds.length, mass: ds.reduce((s, d) => s + d.len, 0), targetDead: 0, targetEnemy: 0, targetShorter: 0, targetShorterMass: 0, targetShorterLen10plus: 0, fromFreshChild: 0, harmful: 0, harmfulFreshChild: 0, harmfulTargetIsOwnParent: 0, harmfulMaxDrop: 0, harmfulDropNow: 0, harmfulList: [] };
    for (const d of ds) {
      if (d.feedTargetLen === null) t.targetDead++;
      else if (d.feedTargetTeam !== 'us') t.targetEnemy++;
      else if (d.feedTargetLen < d.len) { t.targetShorter++; t.targetShorterMass += d.len; if (d.len >= 10) t.targetShorterLen10plus++; if (d.r - d.born <= 2 && d.born > 0) t.fromFreshChild++; }
      // harmful: the feeder was our longest and target + ceil(L/2) dropped pearls < L, so our longest must fall.
      // harmfulDropNow: drop of our longest seen right after the death (L - longest other living teammate).
      // harmfulMaxDrop: the guaranteed part of that drop, a lower bound (L - max(other longest, target + ceil(L/2)),
      // i.e. even if the target ate every dropped pearl).
      const best = d.feedTargetLen === null ? 0 : d.feedTargetLen + Math.ceil(d.len / 2);
      if (d.feedTargetTeam === 'us' && d.len > d.teamMaxOther && best < d.len) {
        t.harmful++; t.harmfulMaxDrop += d.len - Math.max(d.teamMaxOther, best); t.harmfulDropNow += d.len - d.teamMaxOther;
        if (d.r - d.born <= 2 && d.born > 0) t.harmfulFreshChild++;
        if (parentOf.get(d.key + '#' + d.id) === d.feedTarget) t.harmfulTargetIsOwnParent++;
        t.harmfulList.push(`${d.key} r${d.r} L${d.len} -> #${d.feedTarget} L${d.feedTargetLen} (next longest ${d.teamMaxOther}, age ${d.r - d.born})`);
      }
    }
    A.feed[o] = t;
  }
  // our length-3 wall deaths flagged no-exit: the stub left by an escape split, per map
  A.noExitStubs = {};
  for (const m of maps) {
    const gs = games.filter(g => g.map === m);
    const per = gs.map(g => g.deaths.filter(d => d.team === 'us' && d.reason === 'W' && d.ind === 'no-exit' && d.len <= 3));
    A.noExitStubs[m] = { perGame: r1(mean(per.map(x => x.length))), gamesWithAny: per.filter(x => x.length).length, lastRoundMed: quant(per.filter(x => x.length).map(x => Math.max(...x.map(d => d.r))), 0.5) };
  }
  // the biggest single-round drop of our longest dragon in lost games, and every death of ours with length >= 5 there
  A.lossAnatomy = {};
  for (const o of opps) {
    const lost = games.filter(g => g.opp === o && !g.won);
    A.lossAnatomy[o] = lost.map(g => {
      const bd = g.landmarks.bigDrop;
      const d = g.deaths.filter(x => x.team === 'us' && x.r === bd.round).sort((a, b) => b.len - a.len)[0];
      const bigDeaths = g.deaths.filter(x => x.team === 'us' && x.len >= 5).map(x => `r${x.r} ${x.reason} L${x.len}` + (x.byTeam ? ` by ${x.byTeam} L${x.byLen}${x.byMoved ? ' (they moved)' : ''}` : '') + (x.ind ? ` [${x.ind.split(' ')[0]}]` : ''));
      return { key: g.key, G: g.G, theirLongest: g.final.them.max, alive: g.alive, endRound: g.lastRound, fallBehind: g.landmarks.fallBehind, peakUs: g.landmarks.peakUs, bigDrop: bd, bigDropDeath: d ? { r: d.r, reason: d.reason, len: d.len, byTeam: d.byTeam, byLen: d.byLen, byMoved: d.byMoved, ind: d.ind } : null, deathsLen5plus: bigDeaths };
    });
  }
  // split context: was the tile ahead blocked, how many exits were free, what happened to the parent afterwards
  const splitCtx = sp => {
    const t = { n: sp.length, fwdBlocked: r3(mean(sp.map(s => +s.fwdBlocked))), exits: {}, parent2: 0, parent2DiedWithin5: 0, parent2DiedWithin20: 0, parent2DeathReason: {}, parent2DiedAfterMed: null };
    const after = [];
    for (const s of sp) {
      inc(t.exits, String(s.exits));
      if (s.parentLen === 2) {
        t.parent2++;
        if (s.parentDiedAfter !== undefined) { after.push(s.parentDiedAfter); inc(t.parent2DeathReason, s.parentDeath); if (s.parentDiedAfter <= 5) t.parent2DiedWithin5++; if (s.parentDiedAfter <= 20) t.parent2DiedWithin20++; }
      }
    }
    t.parent2DiedAfterMed = quant(after, 0.5);
    return t;
  };
  A.splitContext = {};
  for (const o of opps) { const gs = games.filter(g => g.opp === o); A.splitContext[o] = { them: splitCtx(gs.flatMap(g => g.splits.filter(s => s.team === 'them'))), us: splitCtx(gs.flatMap(g => g.splits.filter(s => s.team === 'us'))) }; }
  A.ourSplitIndicator = {};
  for (const s of games.flatMap(g => g.splits.filter(x => x.team === 'us'))) inc(A.ourSplitIndicator, (s.ind || 'none').split(' ')[0].replace(/[0-9]+$/, ''));
  // games that are identical between two opponents (same map, side, seed and the same end state and event counts)
  const sig = g => JSON.stringify([g.lastRound, g.G, g.final.us, g.final.them, g.deaths.length, g.splits.length]);
  A.twins = {};
  for (let i = 0; i < opps.length; i++) for (let j = i + 1; j < opps.length; j++) {
    let same = 0, n = 0;
    for (const g of games.filter(x => x.opp === opps[i])) { const h = games.find(x => x.opp === opps[j] && x.map === g.map && x.side === g.side && x.seed === g.seed); if (!h) continue; n++; if (sig(g) === sig(h)) same++; }
    A.twins[opps[i] + '|' + opps[j]] = { pairs: n, identical: same };
  }
  A.theirDeaths = { byOpp: {} };
  for (const o of opps) {
    const ds = theirs(games.filter(g => g.opp === o));
    const byUs = ds.filter(d => d.byTeam === 'us');
    A.theirDeaths.byOpp[o] = { ...deathTable(ds), perGame: r1(ds.length / games.filter(g => g.opp === o).length), causedByUs: byUs.length, causedByUsMass: byUs.reduce((s, d) => s + d.len, 0) };
  }
  // splits and unit counts
  A.splits = { them: {}, us: {} };
  for (const o of opps) { const gs = games.filter(g => g.opp === o); A.splits.them[o] = splitTable(gs, 'them'); A.splits.us[o] = splitTable(gs, 'us'); }
  // flow
  A.flow = { byOpp: {}, byMap: {}, lostFallBehind: {} };
  for (const o of opps) A.flow.byOpp[o] = flowTable(games.filter(g => g.opp === o));
  for (const m of maps) A.flow.byMap[m] = flowTable(games.filter(g => g.map === m));
  A.flow.byOppMap = {};
  for (const o of opps) {
    A.flow.byOppMap[o] = {};
    for (const m of maps) {
      const gs = games.filter(g => g.opp === o && g.map === m);
      const rows = flowTable(gs, [50, 100, 150, 200, 300, 499]);
      A.flow.byOppMap[o][m] = Object.fromEntries(Object.entries(rows).map(([k, v]) => [k, { usMax: v.usMax, themMax: v.themMax, usN: v.usN, themN: v.themN, usEat: v.usEat, themEat: v.themEat }]));
    }
  }
  for (const o of opps) {
    const lost = games.filter(g => g.opp === o && !g.won);
    const fb = lost.map(g => g.landmarks.fallBehind).filter(x => x !== null);
    const fbAll = games.filter(g => g.opp === o).map(g => g.landmarks.firstBehind).filter(x => x >= 0);
    A.flow.lostFallBehind[o] = { lost: lost.length, lostBehindAtEnd: fb.length, lostEliminated: lost.filter(g => !g.alive).length, fallBehind: { min: quant(fb, 0), q25: quant(fb, 0.25), med: quant(fb, 0.5), q75: quant(fb, 0.75), max: quant(fb, 1) }, gamesEverBehind: fbAll.length, firstBehindMed: quant(fbAll, 0.5) };
  }
  // sonar
  A.sonar = { us: sonarTable(games, 'us'), them: sonarTable(games, 'them'), usByOpp: {}, themByOpp: {} };
  for (const o of opps) { const gs = games.filter(g => g.opp === o); A.sonar.usByOpp[o] = sonarTable(gs, 'us'); A.sonar.themByOpp[o] = sonarTable(gs, 'them'); }
  // movement and the length paid for sprinting (one segment per extra step), per game
  const sprintTab = gs => {
    const t = {};
    for (const w of ['us', 'them']) t[w] = { moves: gs.reduce((s, g) => s + g.moves[w], 0), sprints: gs.reduce((s, g) => s + g.sprints[w], 0), costPerGame: r1(mean(gs.map(g => g.sprintCost[w]))), costLongPerGame: r1(mean(gs.map(g => g.sprintCostLong[w]))), costByRound100: [0, 1, 2, 3, 4].map(i => r1(mean(gs.map(g => g.sprintCostByRound[w][i])))), eatenPerGame: r1(mean(gs.map(g => g.eaten[w]))) };
    return t;
  };
  A.moves = { byOpp: {}, byMap: {} };
  for (const o of opps) A.moves.byOpp[o] = sprintTab(games.filter(g => g.opp === o));
  for (const m of maps) A.moves.byMap[m] = sprintTab(games.filter(g => g.map === m));
  A.moves.trophyByOpp = {};
  for (const o of opps) A.moves.trophyByOpp[o] = sprintTab(games.filter(g => g.opp === o && g.map === 'trophy'));
  // maps
  A.maps = {};
  for (const m of maps) {
    const gs = games.filter(g => g.map === m);
    A.maps[m] = { ...gs[0].map_, spawnsPerGame: r1(mean(gs.map(g => g.spawns))), dropsPerGame: r1(mean(gs.map(g => g.drops))), usEaten: r1(mean(gs.map(g => g.eaten.us))), themEaten: r1(mean(gs.map(g => g.eaten.them))), rounds: r1(mean(gs.map(g => g.lastRound + 1))), usPortalSteps: r1(mean(gs.map(g => g.portalSteps.us))), themPortalSteps: r1(mean(gs.map(g => g.portalSteps.them))), pearlsLeftAtEnd: r1(mean(gs.map(g => g.pearlsLeft))) };
  }
  return A;
}

// ---------------------------------------------------------------------------------------------------------------
// CLI
if (require.main === module) {
  const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
  const evalDir = path.resolve(ROOT, arg('eval', 'exp/eval-r1')), out = arg('out'), gamesOut = arg('games-out'), filter = arg('filter');
  const rows = fs.readFileSync(path.join(evalDir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined && (!filter || new RegExp(filter).test(r.key)));
  const seen = new Set(), games = [];
  for (const row of rows) {
    if (seen.has(row.key)) continue; seen.add(row.key);
    const dir = path.join(evalDir, 'games', row.key.replace(/:/g, '_'));
    try {
      const g = analyzeGame(dir, row);
      if (g.won !== row.won || g.G !== row.G) g.check.rowMismatch = 1;
      games.push(g);
    } catch (e) { console.error('skip', row.key, String(e).slice(0, 200)); }
    if (games.length % 20 === 0) process.stderr.write(`${games.length}/${rows.length}\n`);
  }
  const A = aggregate(games);
  const meta = { evalDir: path.relative(ROOT, evalDir), games: games.length, at: new Date().toISOString(), tool: 'tools/observe_local.js' };
  const write = (f, obj) => { const p = path.resolve(ROOT, f); fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, JSON.stringify(obj, null, 1) + '\n'); };
  if (out) write(out, { meta, aggregate: A });
  if (gamesOut) write(gamesOut, { meta, games: games.map(g => { const { map_, stopTab, ...rest } = g; return rest; }) });
  console.log(JSON.stringify({ meta, aggregate: A }, null, 1));
}

module.exports = { load, parseMap, step, edgeKind, decodeOurs, analyzeGame, aggregate, STOP };
