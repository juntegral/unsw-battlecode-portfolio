#!/usr/bin/env node
// Sonar use of top teams (data/top): volume, delivery, aiming, 64-bit message decoding. Reads replays only; runs no
// games and makes no network access.
//
// usage: node tools/sonar_study.js [--rows N] [--jobs K] [--sample K] [--min-games G] [--out FILE] [--limit N]
//        node tools/sonar_study.js --tables [FILE]   (prints the Markdown tables and protocol cards of a finished run;
//                                                    reads only the JSON, default data/top/sonar_study.json)
//   --rows N       use only the first N rows of data/top/index.jsonl. The index is append-only, so this reproduces a
//                  frozen snapshot. Default: all rows present when the run starts. research/observations/top-sonar.md
//                  was made with --rows 377.
//   --jobs K       worker threads, at most 4 (default 4).
//   --sample K     first-occurrence messages sampled per team per game for the field search (default 500).
//   --min-games G  teams with fewer games are pooled as "others" in the pooled rows (default 15). Every team is still
//                  decoded on its own, because protocols are team-specific.
//   --out FILE     output JSON (default data/top/sonar_study.json).
//   --limit N      process only the first N games of the snapshot (for testing).
// Output: one JSON file (field meanings in its `definitions` object) and a console summary.
//
// Method notes
// * Replays are server format 2. The sent 64-bit value is UInt64 @16 of EventSonarPing and UInt32 @24 says what the
//   ray stopped on (1 empty/lost, 2 kelp, 3 ally body, 4 ally head, 5 enemy body, 6 enemy head; relative to the
//   sender). The loader below repeats the few lines of tools/top_features.js (makeLoader/viewerSource) because
//   requiring that module inside a worker thread starts its own worker message handler.
// * Bodies are rebuilt step by step (moves, sprints, portals, pearls, splits, deaths) and checked against every
//   dragonUpdate head/tail. Every recorded ray is re-cast on the rebuilt board and checked against the replay (stop
//   kind, end tile, origin, direction). Rays that were not sent (aiming test) use the same caster.
// * A "message" is one distinct value in one dragon turn (a value sent in several directions counts once). A message is
//   "first" if nobody in the game sent that value before. Fields are searched on first messages only, because relayed
//   and repeated values describe some other dragon or an earlier turn.
// * Field search: for every window of width 1-16 at every offset and every candidate feature f of the sender at cast
//   time, the match rate is the share of messages whose (window XOR f) equals the most common such value (the constant
//   may be 0), and the same for (window - f) mod 2^w. A field is kept when the rate is >= 0.85, the rate among messages
//   whose f differs from its most common value is >= 0.75 (so a constant window cannot match a nearly constant
//   feature), and there are >= 30 such messages. The reported width is capped at the bits needed for f's range.
//   Fields are searched on all first messages, then inside message classes split by a tag window when one exists and,
//   for teams that usually send different values in different directions, inside classes by first requested direction;
//   for teams whose same-round message pairs share structure across games, with a per-round key (the constant may
//   depend on the round). Fields found on the sample are then counted on all first messages of the team (pass 2).
// * Also measured: a coordinate detector (every pair of 6-bit windows against the heads of the sender, other own
//   dragons and enemies, and pearls in the sender's view), whose state a message carries for teams with an id field,
//   the age of round fields, XOR-pair structure tests, relays, delivery per phase, and aiming (every direction re-cast).
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), vm = require('vm'), cp = require('child_process');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

const ROOT = path.resolve(__dirname, '..'), TOP = path.join(ROOT, 'data', 'top'), INDEX = path.join(TOP, 'index.jsonl');
const DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 };
const DIRS = ['N', 'E', 'S', 'W'], DIRI = { N: 0, E: 1, S: 2, W: 3 }, OPP = { N: 'S', S: 'N', E: 'W', W: 'E' };
const NONE = -2147483648, NWIN = 5, WINLEN = 100;
const STOP_CODE = { 1: 'lost', 2: 'kelp', 3: 'ally', 4: 'allyHead', 5: 'enemy', 6: 'enemyHead' };
// delivery kinds (sender-relative). self = the sender's own body or head.
const KINDS = ['lost', 'kelp', 'self', 'allyBody', 'allyHead', 'enemyBody', 'enemyHead'];
const KIND_OF = { lost: 0, kelp: 1, self: 2, selfHead: 2, ally: 3, allyHead: 4, enemy: 5, enemyHead: 6 };
// Candidate features of the sender. Suffix 0 = at turn start (before the action); no suffix = at cast time (after it).
// v* = nearest thing in the sender's 7x7 view at turn start (Chebyshev <= 3, wrapped); g* = global, not necessarily
// known to the sender; king = longest own dragon (ties: lowest id); eKing = longest enemy dragon.
const FEATS = [
  'round', 'id', 'side', 'age', 'born', 'parent',
  'hx', 'hy', 'hidx', 'hidxT', 'hx0', 'hy0', 'hidx0', 'hidxT0', 'tx', 'ty', 'tx0', 'ty0',
  'len', 'len0', 'fac', 'fac0', 'steps', 'splitLen',
  'nOwn', 'nEnemy', 'ownTotal', 'ownLongest', 'enemyTotal', 'enemyLongest',
  'kingX', 'kingY', 'kingId', 'eKingX', 'eKingY',
  'vEnX', 'vEnY', 'vEnDx', 'vEnDy', 'vAlX', 'vAlY', 'vAlDx', 'vAlDy', 'vPeX', 'vPeY', 'vPeDx', 'vPeDy',
  'nVisEnH', 'nVisEnSeg', 'nVisAlH', 'nVisPe', 'gEnX', 'gEnY', 'W', 'H',
  'dirMask', 'nDirs', 'firstDir', 'nVals', 'msgIdx', 'rcvKind', 'rcvId', 'rcvX', 'rcvY', 'rcvLen',
];
const NF = FEATS.length, FI = Object.fromEntries(FEATS.map((f, i) => [f, i]));
const FEAT_DOC = {
  round: 'round number', id: 'sender id', side: '0 = team A, 1 = team B', age: 'round - born', born: 'round the sender was created (0 = initial)',
  parent: 'parent id (-1 = initial)', hx: 'head x after the action', hy: 'head y after the action', hidx: 'hy*W+hx after the action',
  hidxT: 'hx*H+hy after the action', hx0: 'head x at turn start', hy0: 'head y at turn start', hidx0: 'hy0*W+hx0', hidxT0: 'hx0*H+hy0',
  tx: 'tail x after the action', ty: 'tail y after the action', tx0: 'tail x at turn start', ty0: 'tail y at turn start',
  len: 'length after the action', len0: 'length at turn start', fac: 'facing after the action (N0 E1 S2 W3)', fac0: 'facing at turn start',
  steps: 'steps moved this turn (0 = no move)', splitLen: 'child length if the action was a split, else 0',
  nOwn: 'own dragons alive after the action', nEnemy: 'enemy dragons alive', ownTotal: 'own total length', ownLongest: 'own longest length',
  enemyTotal: 'enemy total length', enemyLongest: 'enemy longest length', kingX: 'head x of the longest own dragon', kingY: 'head y of the longest own dragon',
  kingId: 'id of the longest own dragon', eKingX: 'head x of the longest enemy dragon', eKingY: 'head y of the longest enemy dragon',
  vEnX: 'nearest visible enemy head x (turn start)', vEnY: 'nearest visible enemy head y', vEnDx: 'its dx from the sender head (signed)', vEnDy: 'its dy',
  vAlX: 'nearest visible other own head x', vAlY: 'nearest visible other own head y', vAlDx: 'its dx', vAlDy: 'its dy',
  vPeX: 'nearest visible pearl x', vPeY: 'nearest visible pearl y', vPeDx: 'its dx', vPeDy: 'its dy',
  nVisEnH: 'visible enemy heads', nVisEnSeg: 'visible enemy segments', nVisAlH: 'visible other own heads', nVisPe: 'visible pearls',
  gEnX: 'nearest enemy head x anywhere (torus Manhattan; not necessarily known)', gEnY: 'its y', W: 'map width', H: 'map height',
  dirMask: 'requested directions carrying this value (bit0 N, bit1 E, bit2 S, bit3 W)', nDirs: 'directions sent this turn',
  firstDir: 'first requested direction carrying this value', nVals: 'distinct values sent this turn', msgIdx: 'index of this value among the turn values (N,E,S,W order)',
  rcvKind: 'value sent in exactly one direction: what its ray stopped on (0 kelp/lost, 1 self, 2 other own dragon, 3 enemy)', rcvId: 'id of the dragon that ray reached', rcvX: 'its head x', rcvY: 'its head y', rcvLen: 'its length',
};

// ---------------------------------------------------------------------------------------------------------------
// Replay loader (see header).
function viewerSource() {
  const src = fs.readFileSync(path.join(__dirname, 'viewer.js'), 'utf8');
  const m = src.match(/const root='([^']+)'/);
  if (!m) throw Error('viewer root not found in tools/viewer.js');
  const vsix = path.join(m[1], '.venv-ppo/lib/python3.13/site-packages/unswbc/replay-viewer.vsix');
  return cp.execFileSync('unzip', ['-p', vsix, 'extension/dist/webview/webview.js'], { maxBuffer: 8 << 20 }).toString();
}
function makeLoader(src) {
  const cut = src.indexOf('var Af=B(');
  if (cut < 0) throw Error('unexpected replay-viewer build (parser cut point not found)');
  const code = src.slice(0, cut).replace('if(n.formatVersion>1)', 'if(n.formatVersion>2)') + 'globalThis.__tf={Df:Df,bf:bf,Of:Of,cu:$};})();';
  const ctx = { TextEncoder, TextDecoder };
  vm.runInNewContext(code, ctx, { timeout: 5000 });
  const { Df, bf, Of, cu } = ctx.__tf || {};
  if (![Df, bf, Of].every(f => typeof f === 'function') || !cu || typeof cu.getUint64 !== 'function') throw Error('unexpected replay-viewer build (parser internals not found)');
  return function load(file) {
    const raw = fs.readFileSync(file);
    const root = Df(file.endsWith('.gz') ? zlib.gunzipSync(raw) : raw);
    const list = root.events, n = list.length, events = new Array(n);
    for (let i = 0; i < n; i++) {
      const ev = list.get(i), o = bf(ev);
      if (o.type === 'sonarPing') {
        const sp = ev.sonarPing;
        if (cu.getSize(sp).dataByteLength >= 32) { o.value64 = cu.getUint64(16, sp); o.stop = cu.getUint32(24, sp); }
        else o.value64 = BigInt(o.value);
      }
      events[i] = o;
    }
    const R = Of(root, events);
    R.formatVersion = root.formatVersion;
    return R;
  };
}
const replayFile = row => path.join(TOP, String(row.battleId), row.gameId + '.replay.gz');

// ---------------------------------------------------------------------------------------------------------------
// Board geometry (kelp edges, portals, wrap) and the game walker.
function geometry(M) {
  const W = M.width, H = M.height;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
  const portal = new Map();
  for (const pr of M.portals || []) { if (pr.length !== 2) continue; const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); }
  const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
  const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
  // tile across the edge faced from (x,y) in direction d (portals keep the direction), or null for kelp
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
  return { W, H, wx, wy, across };
}

// Walk one replay. onTurn(t) is called after each dragon turn with
// t = { round, id, team, pre, post, action, died, feats (Int32Array, turn-level part), sim (kinds of the four requested
//       directions at cast time, or null if nothing was cast), pings: [{ req, dir, v, stop, kind, fromTail, hitId }] }.
function walkGame(R, onTurn, chk, ctx) {
  const M = R.match.map, { W, H, wx, wy, across } = geometry(M);
  const key = (x, y) => y * W + x;
  const drag = new Map(), occ = new Map(), pearls = new Set();
  if (ctx) { ctx.drag = drag; ctx.W = W; ctx.H = H; }
  const setOcc = d => { for (const s of d.body) occ.set(key(s.x, s.y), d.id); };
  const clrOcc = d => { for (const s of d.body) if (occ.get(key(s.x, s.y)) === d.id) occ.delete(key(s.x, s.y)); };
  for (const d0 of M.initialDragons) {
    const o = { id: d0.id, team: d0.team, body: d0.body.map(s => ({ x: s.x, y: s.y })), facing: d0.facing, expect: [], born: 0, parent: -1 };
    drag.set(o.id, o); setOcc(o);
  }
  const tman = (ax, ay, bx, by) => { let dx = Math.abs(ax - bx), dy = Math.abs(ay - by); dx = Math.min(dx, W - dx); dy = Math.min(dy, H - dy); return dx + dy; };
  function cast(x, y, d) {
    for (let step = 0; step < W + H; step++) {
      const nx = across(x, y, d);
      if (!nx) return { kind: 'kelp', end: { x, y } };
      x = nx.x; y = nx.y;
      const id = occ.get(key(x, y));
      if (id !== undefined) return { kind: 'hit', id, end: { x, y } };
    }
    return { kind: 'lost', end: { x, y } };
  }
  function kindOf(s, res) {
    if (res.kind !== 'hit') return res.kind;
    const h = drag.get(res.id), onHead = h.body[0].x === res.end.x && h.body[0].y === res.end.y;
    if (res.id === s.id) return onHead ? 'selfHead' : 'self';
    if (h.team === s.team) return onHead ? 'allyHead' : 'ally';
    return onHead ? 'enemyHead' : 'enemy';
  }
  // a ray requested opposite to the facing leaves the tail, in the direction the tail points away from the body
  function rayStart(s, req) {
    const b = s.body;
    if (req === OPP[s.facing]) {
      if (b.length < 2) return null;
      const pv = b[b.length - 2], tl = b[b.length - 1];
      for (const dd of DIRS) { const nx = across(pv.x, pv.y, dd); if (nx && nx.x === tl.x && nx.y === tl.y) return { x: tl.x, y: tl.y, d: dd, fromTail: true }; }
      return null;
    }
    return { x: b[0].x, y: b[0].y, d: req, fromTail: false };
  }
  let round = -1, turn = null, lastVisPearls = [];
  function preFeatures(d) {
    const f = new Int32Array(NF).fill(NONE);
    const h = d.body[0], t = d.body[d.body.length - 1];
    f[FI.round] = round; f[FI.id] = d.id; f[FI.side] = d.team === 'A' ? 0 : 1; f[FI.age] = round - d.born; f[FI.born] = d.born; f[FI.parent] = d.parent;
    f[FI.hx0] = h.x; f[FI.hy0] = h.y; f[FI.hidx0] = h.y * W + h.x; f[FI.hidxT0] = h.x * H + h.y; f[FI.tx0] = t.x; f[FI.ty0] = t.y;
    f[FI.len0] = d.body.length; f[FI.fac0] = DIRI[d.facing]; f[FI.W] = W; f[FI.H] = H;
    let bE = null, bA = null, bP = null, nEH = 0, nES = 0, nAH = 0, nP = 0;
    const visP = []; lastVisPearls = visP;
    for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) {
      const x = wx(h.x + dx), y = wy(h.y + dy), k = key(x, y);
      const score = Math.max(Math.abs(dx), Math.abs(dy)) * 100 + Math.abs(dx) + Math.abs(dy);
      if (pearls.has(k)) { nP++; visP.push(x, y); if (!bP || score < bP.s) bP = { s: score, x, y, dx, dy }; }
      const id = occ.get(k);
      if (id === undefined || id === d.id) continue;
      const o = drag.get(id), isHead = o.body[0].x === x && o.body[0].y === y;
      if (o.team !== d.team) { nES++; if (isHead) { nEH++; if (!bE || score < bE.s) bE = { s: score, x, y, dx, dy }; } }
      else if (isHead) { nAH++; if (!bA || score < bA.s) bA = { s: score, x, y, dx, dy }; }
    }
    f[FI.nVisEnH] = nEH; f[FI.nVisEnSeg] = nES; f[FI.nVisAlH] = nAH; f[FI.nVisPe] = nP;
    if (bE) { f[FI.vEnX] = bE.x; f[FI.vEnY] = bE.y; f[FI.vEnDx] = bE.dx; f[FI.vEnDy] = bE.dy; }
    if (bA) { f[FI.vAlX] = bA.x; f[FI.vAlY] = bA.y; f[FI.vAlDx] = bA.dx; f[FI.vAlDy] = bA.dy; }
    if (bP) { f[FI.vPeX] = bP.x; f[FI.vPeY] = bP.y; f[FI.vPeDx] = bP.dx; f[FI.vPeDy] = bP.dy; }
    let g = null;
    for (const o of drag.values()) if (o.team !== d.team) { const m = tman(h.x, h.y, o.body[0].x, o.body[0].y); if (!g || m < g.m || (m === g.m && o.id < g.id)) g = { m, id: o.id, x: o.body[0].x, y: o.body[0].y }; }
    if (g) { f[FI.gEnX] = g.x; f[FI.gEnY] = g.y; }
    return f;
  }
  function postFeatures(t, d) {
    const f = t.feats;
    if (d) {
      const h = d.body[0], tl = d.body[d.body.length - 1];
      f[FI.hx] = h.x; f[FI.hy] = h.y; f[FI.hidx] = h.y * W + h.x; f[FI.hidxT] = h.x * H + h.y; f[FI.tx] = tl.x; f[FI.ty] = tl.y;
      f[FI.len] = d.body.length; f[FI.fac] = DIRI[d.facing];
    }
    f[FI.steps] = t.action && t.action[0] === 'm' ? +t.action.slice(1) : 0;
    f[FI.splitLen] = t.action && t.action[0] === 's' && t.action !== 'suicide' ? +t.action.slice(1) : 0;
    let nOwn = 0, nEn = 0, oT = 0, oL = 0, eT = 0, eL = 0, king = null, eking = null;
    for (const o of drag.values()) {
      const L = o.body.length;
      if (o.team === t.team) { nOwn++; oT += L; if (L > oL) oL = L; if (!king || L > king.L || (L === king.L && o.id < king.id)) king = { L, id: o.id, x: o.body[0].x, y: o.body[0].y }; }
      else { nEn++; eT += L; if (L > eL) eL = L; if (!eking || L > eking.L || (L === eking.L && o.id < eking.id)) eking = { L, id: o.id, x: o.body[0].x, y: o.body[0].y }; }
    }
    f[FI.nOwn] = nOwn; f[FI.nEnemy] = nEn; f[FI.ownTotal] = oT; f[FI.ownLongest] = oL; f[FI.enemyTotal] = eT; f[FI.enemyLongest] = eL;
    if (king) { f[FI.kingX] = king.x; f[FI.kingY] = king.y; f[FI.kingId] = king.id; }
    if (eking) { f[FI.eKingX] = eking.x; f[FI.eKingY] = eking.y; }
  }
  const finish = () => {
    if (!turn) return;
    const d = drag.get(turn.id);
    postFeatures(turn, d && !turn.died ? d : null);
    onTurn(turn);
    turn = null;
  };
  for (const e of R.events) {
    switch (e.type) {
      case 'roundStart': finish(); round = e.round; break;
      case 'turnStart': {
        finish();
        const d = drag.get(e.id);
        if (!d || round < 0) break;
        d.expect = [];
        turn = { round, id: d.id, team: d.team, action: null, died: false, feats: preFeatures(d), sim: null, pings: [] };
        turn.visPearls = lastVisPearls;
        break;
      }
      case 'tileChange': { const k = key(e.tile.x, e.tile.y); if (e.hasPearl) pearls.add(k); else pearls.delete(k); break; }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action;
        if (turn && turn.id === e.id) turn.action = a ? (a.kind === 'move' ? 'm' + a.steps.length : a.kind === 'split' ? 's' + a.childSegmentCount : a.kind) : 'none';
        if (!a || a.kind !== 'move') break;
        clrOcc(d);
        const body = d.body.slice();
        for (let i = 0; i < a.steps.length; i++) {
          if (i > 0 && body.length <= 2) break;
          const h = body[0], nx = across(h.x, h.y, a.steps[i]);
          if (!nx) break;
          if (body.some(s => s.x === nx.x && s.y === nx.y)) break;
          if (occ.has(key(nx.x, nx.y))) break;
          body.unshift(nx);
          const k = key(nx.x, nx.y);
          if (pearls.has(k)) pearls.delete(k); else body.pop();
          if (i > 0) body.pop();
          d.expect.push({ h: body[0], t: body[body.length - 1] });
        }
        d.body = body; setOcc(d);
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id); if (!d) break;
        if (round < 0) { d.facing = e.facing; break; }
        chk.updates++;
        const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        if (x.h.x !== e.head.x || x.h.y !== e.head.y || x.t.x !== e.tail.x || x.t.y !== e.tail.y) {
          chk.bodyMismatches++;
          clrOcc(d);
          const b = d.body.slice();
          if (b[0].x !== e.head.x || b[0].y !== e.head.y) b.unshift({ x: e.head.x, y: e.head.y });
          while (b.length > 1 && (b[b.length - 1].x !== e.tail.x || b[b.length - 1].y !== e.tail.y)) b.pop();
          d.body = b; d.expect = [];
          setOcc(d);
        }
        d.facing = e.facing;
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        clrOcc(p); p.body = e.parentBody.map(s => ({ x: s.x, y: s.y })); setOcc(p);
        const c = { id: e.childId, team: e.team, body: e.childBody.map(s => ({ x: s.x, y: s.y })), facing: e.childFacing, expect: [], born: round, parent: p.id };
        drag.set(c.id, c); setOcc(c);
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        if (turn && turn.id === e.id) turn.died = e.reason;
        clrOcc(d); drag.delete(e.id);
        break;
      }
      case 'sonarPing': {
        chk.pings++;
        const s = drag.get(e.senderId);
        if (!turn || turn.id !== e.senderId || !s) { chk.orphanPings++; break; }
        const fromTail = !(e.origin.x === s.body[0].x && e.origin.y === s.body[0].y);
        const p = { dir: e.direction, req: fromTail ? OPP[s.facing] : e.direction, v: e.value64, stop: e.stop, fromTail, hitId: e.hitId };
        if (e.hitId !== undefined) {
          const h = drag.get(e.hitId);
          if (!h) p.kind = 'unknown';
          else {
            const onHead = h.body[0].x === e.end.x && h.body[0].y === e.end.y;
            p.kind = e.hitId === s.id ? (onHead ? 'selfHead' : 'self') : h.team === s.team ? (onHead ? 'allyHead' : 'ally') : (onHead ? 'enemyHead' : 'enemy');
            p.rcv = { kind: e.hitId === s.id ? 1 : h.team === s.team ? 2 : 3, id: h.id, x: h.body[0].x, y: h.body[0].y, len: h.body.length };
          }
        } else p.kind = STOP_CODE[e.stop] === 'lost' ? 'lost' : 'kelp';
        const sk = String(e.stop) + '>' + p.kind; chk.stopKinds[sk] = (chk.stopKinds[sk] || 0) + 1;
        const rs = rayStart(s, p.req);
        if (!rs) chk.simMissing++;
        else {
          const res = cast(rs.x, rs.y, rs.d), k = kindOf(s, res);
          const same = (k === 'selfHead' ? 'self' : k) === (p.kind === 'selfHead' ? 'self' : p.kind) && res.end.x === e.end.x && res.end.y === e.end.y && rs.x === e.origin.x && rs.y === e.origin.y && rs.d === e.direction;
          if (same) chk.simAgree++; else chk.simDisagree++;
        }
        if (!turn.sim) turn.sim = DIRS.map(req => { const r2 = rayStart(s, req); return r2 ? kindOf(s, cast(r2.x, r2.y, r2.d)) : null; });
        turn.pings.push(p);
        break;
      }
    }
  }
  finish();
  return { W, H };
}

// Group a turn's pings into messages (distinct values), with per-message features.
function turnMessages(t) {
  const reqSet = new Set(t.pings.map(p => p.req));
  const vals = new Map();
  for (const p of t.pings) {
    let m = vals.get(p.v);
    if (!m) { m = { v: p.v, mask: 0, first: DIRI[p.req], idx: 0, pings: [] }; vals.set(p.v, m); }
    m.mask |= 1 << DIRI[p.req]; m.pings.push(p);
  }
  const msgs = [...vals.values()];
  msgs.sort((a, b) => a.first - b.first);
  msgs.forEach((m, i) => { m.idx = i; });
  for (const m of msgs) {
    const f = Int32Array.from(t.feats);
    f[FI.dirMask] = m.mask; f[FI.nDirs] = reqSet.size; f[FI.firstDir] = m.first; f[FI.nVals] = msgs.length; f[FI.msgIdx] = m.idx;
    if (m.pings.length === 1) {
      const p = m.pings[0];
      if (p.rcv) { f[FI.rcvKind] = p.rcv.kind; f[FI.rcvId] = p.rcv.id; f[FI.rcvX] = p.rcv.x; f[FI.rcvY] = p.rcv.y; f[FI.rcvLen] = p.rcv.len; }
      else f[FI.rcvKind] = 0;
    }
    m.f = f; delete m.pings;
  }
  return { msgs, reqSet };
}
function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const lo32 = v => Number(v & 0xffffffffn), hi32 = v => Number(v >> 32n);
function addXorBits(acc, a, b) { const x = a ^ b, l = lo32(x), h = hi32(x); acc.n++; for (let i = 0; i < 32; i++) { acc.c[i] += (l >>> i) & 1; acc.c[32 + i] += (h >>> i) & 1; } }
const newAcc = () => ({ n: 0, c: new Array(64).fill(0) });

// Position detector: for every pair of 6-bit windows (x at ox, y at oy, not overlapping), does (x, y) equal the head of
// the sender (at turn start or after its action), of another own dragon, of an enemy dragon, or a pearl in the
// sender's view? Counts are per first message (a message counts once per category and window pair).
const POS_CATS = ['self', 'otherOwn', 'enemy', 'anyDragon', 'visiblePearl'];
function posDetect(acc, v, t, ctx) {
  const idx = Array.from({ length: 64 }, () => []);
  for (let o = 0; o + 6 <= 64; o++) idx[Number((v >> BigInt(o)) & 63n)].push(o);
  const marks = { self: new Set(), otherOwn: new Set(), enemy: new Set(), anyDragon: new Set(), visiblePearl: new Set() };
  const add = (cat, x, y) => { for (const ox of idx[x & 63]) for (const oy of idx[y & 63]) if (ox >= oy + 6 || oy >= ox + 6) { marks[cat].add(ox * 64 + oy); if (cat !== 'visiblePearl') marks.anyDragon.add(ox * 64 + oy); } };
  const f = t.feats;
  add('self', f[FI.hx0], f[FI.hy0]);
  if (f[FI.hx] !== NONE && (f[FI.hx] !== f[FI.hx0] || f[FI.hy] !== f[FI.hy0])) add('self', f[FI.hx], f[FI.hy]);
  for (const d of ctx.drag.values()) { if (d.id === t.id) continue; add(d.team === t.team ? 'otherOwn' : 'enemy', d.body[0].x, d.body[0].y); }
  const vp = t.visPearls || []; for (let i = 0; i < vp.length; i += 2) add('visiblePearl', vp[i], vp[i + 1]);
  for (const c of POS_CATS) for (const k of marks[c]) acc[c][k]++;
}

// ---------------------------------------------------------------------------------------------------------------
// Pass 1: per game and side, sonar statistics plus a sample of first messages with features.
function pass1Game(load, row, K) {
  const R = load(replayFile(row));
  const chk = { updates: 0, bodyMismatches: 0, pings: 0, orphanPings: 0, simAgree: 0, simDisagree: 0, simMissing: 0, stopKinds: {} };
  const S = {};
  for (const side of ['A', 'B']) S[side] = {
    turns: new Array(NWIN).fill(0), pings: new Array(NWIN).fill(0), dirHist: Array.from({ length: NWIN }, () => new Array(5).fill(0)),
    kinds: Array.from({ length: NWIN }, () => new Array(KINDS.length).fill(0)),
    multiPingTurns: 0, sameValueTurns: 0, valuesPerPingedTurn: 0, pingedTurns: 0, zeroPings: 0, tailPings: 0, unknownKind: 0,
    msgs: 0, zeroMsgs: 0, relay: { first: 0, sameSender: 0, relayReceived: 0, shared: 0, enemyValue: 0 }, relayDelay: [0, 0],
    roundSenders: 0, roundValues: 0,
    aim: { turns: 0, chosen: 0, chosenAlly: 0, chosenEnemy: 0, all: 0, allAlly: 0, allEnemy: 0, dirsAlly: 0, chosenGivenAlly: 0, dirsNot: 0, chosenGivenNot: 0, backwardChosen: 0, backwardAvail: 0 },
    firstBits: new Array(64).fill(0), firstN: 0,
    pairs: { sameRound: newAcc(), sameSender: newAcc(), sameTurn: newAcc() },
    posPairs: Object.fromEntries(POS_CATS.map(c => [c, new Uint32Array(4096)])),
    roundFirst: [], sampleF: [], sampleV: [], seenFirst: 0,
    valueCount: new Map(),
  };
  const sentBy = new Map(); // value -> {A:Set(ids), B:Set(ids), round}
  const received = new Map(); // dragon id -> Map(value -> round received)
  const rand = rng(row.gameId);
  const lastInRound = { A: null, B: null }, lastBySender = new Map(), roundSeen = { A: new Set(), B: new Set() }, ctx = {};
  let curRound = -1; const roundAgg = { A: { senders: 0, values: new Set() }, B: { senders: 0, values: new Set() } };
  const flushRound = () => { for (const side of ['A', 'B']) { const a = roundAgg[side]; if (a.senders) { S[side].roundSenders += a.senders; S[side].roundValues += a.values.size; } a.senders = 0; a.values = new Set(); } };
  let lastRound = 0;
  walkGame(R, t => {
    if (t.round !== curRound) { flushRound(); curRound = t.round; }
    lastRound = t.round;
    const s = S[t.team], w = Math.min(NWIN - 1, Math.floor(t.round / WINLEN));
    s.turns[w]++; s.pings[w] += t.pings.length;
    const { msgs, reqSet } = turnMessages(t);
    s.dirHist[w][Math.min(4, reqSet.size)]++;
    for (const p of t.pings) { const ki = KIND_OF[p.kind]; if (ki === undefined) s.unknownKind++; else s.kinds[w][ki]++; if (p.v === 0n) s.zeroPings++; if (p.fromTail) s.tailPings++; s.valueCount.set(p.v, (s.valueCount.get(p.v) || 0) + 1); }
    if (t.pings.length) { s.pingedTurns++; s.valuesPerPingedTurn += msgs.length; }
    if (t.pings.length >= 2) { s.multiPingTurns++; if (msgs.length === 1) s.sameValueTurns++; }
    // aiming: turns with 1-3 requested directions; every direction re-cast in the cast-time state
    if (reqSet.size >= 1 && reqSet.size <= 3 && t.sim) {
      const a = s.aim; a.turns++;
      const back = OPP[DIRS[t.feats[FI.fac]]] ;
      for (let i = 0; i < 4; i++) {
        const k = t.sim[i]; if (k === null) continue;
        const ally = k === 'ally' || k === 'allyHead', enemy = k === 'enemy' || k === 'enemyHead', chosen = reqSet.has(DIRS[i]);
        a.all++; if (ally) a.allAlly++; if (enemy) a.allEnemy++;
        if (chosen) { a.chosen++; if (ally) a.chosenAlly++; if (enemy) a.chosenEnemy++; }
        if (ally) { a.dirsAlly++; if (chosen) a.chosenGivenAlly++; } else { a.dirsNot++; if (chosen) a.chosenGivenNot++; }
        if (DIRS[i] === back) { a.backwardAvail++; if (chosen) a.backwardChosen++; }
      }
    }
    // messages
    const rec = received.get(t.id);
    if (t.pings.length) roundAgg[t.team].senders++;
    for (const m of msgs) {
      s.msgs++;
      if (m.v === 0n) { s.zeroMsgs++; continue; }
      roundAgg[t.team].values.add(m.v);
      const sb = sentBy.get(m.v);
      let cat;
      if (!sb) cat = 'first';
      else if (sb[t.team].has(t.id)) cat = 'sameSender';
      else if (rec && rec.has(m.v)) { cat = 'relayReceived'; s.relayDelay[0] += t.round - sb.round; s.relayDelay[1]++; }
      else if (sb[t.team].size) cat = 'shared';
      else cat = 'enemyValue';
      s.relay[cat]++;
      if (cat !== 'first') continue;
      // first messages: bit counts, pair structure, position detector, sample
      s.firstN++;
      posDetect(s.posPairs, m.v, t, ctx);
      { const l = lo32(m.v), h = hi32(m.v); for (let i = 0; i < 32; i++) { s.firstBits[i] += (l >>> i) & 1; s.firstBits[32 + i] += (h >>> i) & 1; } }
      const lr = lastInRound[t.team];
      if (lr && lr.round === t.round && lr.id !== t.id) addXorBits(s.pairs.sameRound, lr.v, m.v);
      lastInRound[t.team] = { round: t.round, id: t.id, v: m.v };
      const ls = lastBySender.get(t.id);
      if (ls && ls.round !== t.round) addXorBits(s.pairs.sameSender, ls.v, m.v);
      lastBySender.set(t.id, { round: t.round, v: m.v });
      if (!roundSeen[t.team].has(t.round)) { roundSeen[t.team].add(t.round); s.roundFirst.push([t.round, m.v.toString(16)]); }
      s.seenFirst++;
      if (s.sampleV.length < K) { s.sampleV.push(m.v); s.sampleF.push(m.f); }
      else { const j = Math.floor(rand() * s.seenFirst); if (j < K) { s.sampleV[j] = m.v; s.sampleF[j] = m.f; } }
    }
    // same-turn pairs of first messages (different values in one turn)
    const fm = msgs.filter(m => m.v !== 0n);
    for (let i = 1; i < fm.length; i++) addXorBits(s.pairs.sameTurn, fm[i - 1].v, fm[i].v);
    for (const m of msgs) { if (m.v === 0n) continue; let sb = sentBy.get(m.v); if (!sb) { sb = { A: new Set(), B: new Set(), round: t.round }; sentBy.set(m.v, sb); } sb[t.team].add(t.id); }
    for (const p of t.pings) if (p.hitId !== undefined && p.v !== 0n) { let r = received.get(p.hitId); if (!r) { r = new Set(); received.set(p.hitId, r); } r.add(p.v); }
  }, chk, ctx);
  flushRound();
  const out = { battleId: row.battleId, gameId: row.gameId, map: row.map, W: R.match.map.width, H: R.match.map.height, winnerIndex: row.winner, winnerReplay: R.result.winner, rounds: lastRound + 1, checks: chk, sides: {} };
  for (const side of ['A', 'B']) {
    const s = S[side];
    let modal = 0; for (const c of s.valueCount.values()) if (c > modal) modal = c;
    s.modalPings = modal; s.distinctValues = s.valueCount.size; delete s.valueCount;
    const n = s.sampleV.length, F = new Int32Array(n * NF), V = new BigUint64Array(n);
    for (let i = 0; i < n; i++) { F.set(s.sampleF[i], i * NF); V[i] = s.sampleV[i]; }
    s.sample = { n, F, V }; delete s.sampleF; delete s.sampleV; delete s.seenFirst;
    out.sides[side] = s;
  }
  return out;
}

// Pass 2: count field matches on all first messages of the listed teams. For teams with an id field, also check whose
// state a message carries (the sender, another own dragon, an enemy), and for teams with a round field, how old it is.
const SUBJ = { hx: d => d.body[0].x, hx0: d => d.body[0].x, hy: d => d.body[0].y, hy0: d => d.body[0].y, len: d => d.body.length, len0: d => d.body.length,
  hidx: (d, W) => d.body[0].y * W + d.body[0].x, hidx0: (d, W) => d.body[0].y * W + d.body[0].x, hidxT: (d, W, H) => d.body[0].x * H + d.body[0].y, hidxT0: (d, W, H) => d.body[0].x * H + d.body[0].y };
const LAGS = ['0', '1', '2', '3-9', '10+', 'negative'];
const winOf = (v, sp) => Number((v >> BigInt(sp.o)) & BigInt((1 << sp.w) - 1));
const decodeWin = (v, sp) => { const mask = (1 << sp.w) - 1, win = winOf(v, sp); return sp.op === 'xor' ? ((win ^ sp.c) >>> 0) & mask : ((win - sp.c) & mask) >>> 0; };
const inClass = (m, cls) => !cls || (cls.feat !== undefined ? m.f[FI[cls.feat]] === cls.x : winOf(m.v, { o: cls.o, w: cls.w }) === cls.x);
function pass2Game(load, row, specs, extras) {
  const R = load(replayFile(row));
  const chk = { updates: 0, bodyMismatches: 0, pings: 0, orphanPings: 0, simAgree: 0, simDisagree: 0, simMissing: 0, stopKinds: {} };
  const bySide = { A: specs[row.teamA] || [], B: specs[row.teamB] || [] };
  const exBySide = { A: extras[row.teamA] || {}, B: extras[row.teamB] || {} };
  const counts = { A: bySide.A.map(() => [0, 0]), B: bySide.B.map(() => [0, 0]) };
  const firstN = { A: 0, B: 0 };
  const newSubj = ex => ex.id ? { n: 0, self: 0, ownOther: 0, enemy: 0, unknown: 0, pos: ex.pos.map(() => [0, 0]), posSender: ex.pos.map(() => [0, 0]) } : null;
  const subj = { A: newSubj(exBySide.A), B: newSubj(exBySide.B) };
  const lag = { A: exBySide.A.round ? new Array(LAGS.length).fill(0) : null, B: exBySide.B.round ? new Array(LAGS.length).fill(0) : null };
  const seen = new Set(), ctx = {};
  walkGame(R, t => {
    const { msgs } = turnMessages(t);
    const fl = bySide[t.team], cnt = counts[t.team], ex = exBySide[t.team];
    for (const m of msgs) {
      if (m.v === 0n || seen.has(m.v)) continue;
      seen.add(m.v);
      firstN[t.team]++;
      for (let j = 0; j < fl.length; j++) {
        const sp = fl[j];
        if (!inClass(m, sp.cls)) continue;
        const f = m.f[FI[sp.feat]]; if (f === NONE) continue;
        const mask = (1 << sp.w) - 1, win = winOf(m.v, sp), fm = (f & mask) >>> 0;
        const r = sp.op === 'xor' ? ((win ^ fm) >>> 0) : (((win - fm) & mask) >>> 0);
        cnt[j][0]++; if (r === sp.c) cnt[j][1]++;
      }
      if (ex.id && inClass(m, ex.id.cls)) {
        const S = subj[t.team], id = decodeWin(m.v, ex.id), mask = (1 << ex.id.w) - 1;
        S.n++;
        if (id === (t.id & mask)) S.self++;
        else {
          let d = null; for (const o of ctx.drag.values()) if ((o.id & mask) === id) { d = o; break; }
          if (!d) S.unknown++;
          else if (d.team !== t.team) S.enemy++;
          else {
            S.ownOther++;
            ex.pos.forEach((sp, j) => {
              if (!inClass(m, sp.cls)) return;
              const pm = (1 << sp.w) - 1, val = decodeWin(m.v, sp);
              S.pos[j][0]++; if (val === (SUBJ[sp.feat](d, ctx.W, ctx.H) & pm)) S.pos[j][1]++;
              const fs = m.f[FI[sp.feat]]; if (fs !== NONE) { S.posSender[j][0]++; if (val === (fs & pm)) S.posSender[j][1]++; }
            });
          }
        }
      }
      if (ex.round && inClass(m, ex.round.cls)) {
        const r = decodeWin(m.v, ex.round), mask = (1 << ex.round.w) - 1;
        let d = ex.round.trunc ? ((t.round & mask) - r) & mask : t.round - r;
        lag[t.team][d < 0 ? 5 : d === 0 ? 0 : d === 1 ? 1 : d === 2 ? 2 : d < 10 ? 3 : 4]++;
      }
    }
  }, chk, ctx);
  return { gameId: row.gameId, teamA: row.teamA, teamB: row.teamB, counts, firstN, subj, lag };
}

if (!isMainThread) {
  const load = makeLoader(workerData.src);
  parentPort.on('message', task => {
    try {
      const res = task.pass === 1 ? pass1Game(load, task.row, task.K) : pass2Game(load, task.row, task.specs, task.extras);
      const transfer = [];
      if (task.pass === 1) for (const s of Object.values(res.sides)) transfer.push(s.sample.F.buffer, s.sample.V.buffer);
      parentPort.postMessage({ ok: true, res }, transfer);
    } catch (err) { parentPort.postMessage({ ok: false, gameId: task.row.gameId, err: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | ') }); }
  });
}

// ---------------------------------------------------------------------------------------------------------------
// Field search (main thread, on the sample of first messages of one team).
function makeTable(samples) { // samples: [{F: Int32Array(n*NF), V: BigUint64Array(n), game}]
  let n = 0; for (const s of samples) n += s.V.length;
  const lo = new Uint32Array(n), hi = new Uint32Array(n), F = FEATS.map(() => new Int32Array(n)), game = new Int32Array(n);
  let i = 0;
  for (const s of samples) for (let k = 0; k < s.V.length; k++, i++) {
    lo[i] = lo32(s.V[k]); hi[i] = hi32(s.V[k]); game[i] = s.game;
    for (let j = 0; j < NF; j++) F[j][i] = s.F[k * NF + j];
  }
  const sh = [];
  for (let o = 0; o < 64; o++) {
    const a = new Uint32Array(n);
    for (let k = 0; k < n; k++) a[k] = o === 0 ? lo[k] : o < 32 ? ((lo[k] >>> o) | (hi[k] << (32 - o))) >>> 0 : (hi[k] >>> (o - 32)) >>> 0;
    sh.push(a);
  }
  return { n, lo, hi, F, game, sh };
}
const H1 = new Uint32Array(65536), H2 = new Uint32Array(65536), H3 = new Uint32Array(65536);
// One window against one feature over the index groups (one group = global constant; one group per round = round key).
function testWindow(t, o, w, fcol, groups) {
  const mask = (1 << w) - 1, a = t.sh[o];
  let n = 0, mX = 0, mS = 0, nNM = 0, nmX = 0, nmS = 0, cXg = 0, cSg = 0;
  for (const g of groups) {
    const t1 = [], t2 = [], t3 = [];
    let bX = 0, cX = 0, bS = 0, cS = 0, bF = 0, cF = 0, gn = 0;
    for (const i of g) {
      const f = fcol[i]; if (f === NONE) continue; gn++;
      const win = a[i] & mask, fm = (f & mask) >>> 0, x = (win ^ fm) >>> 0, s = ((win - fm) & mask) >>> 0;
      if (H1[x]++ === 0) t1.push(x); if (H1[x] > bX) { bX = H1[x]; cX = x; }
      if (H2[s]++ === 0) t2.push(s); if (H2[s] > bS) { bS = H2[s]; cS = s; }
      if (H3[fm]++ === 0) t3.push(fm); if (H3[fm] > bF) { bF = H3[fm]; cF = fm; }
    }
    for (const x of t1) H1[x] = 0; for (const x of t2) H2[x] = 0; for (const x of t3) H3[x] = 0;
    if (gn < (groups.length > 1 ? 4 : 1)) continue;
    n += gn; mX += bX; mS += bS; cXg = cX; cSg = cS;
    for (const i of g) {
      const f = fcol[i]; if (f === NONE) continue;
      const fm = (f & mask) >>> 0; if (fm === cF) continue;
      nNM++; const win = a[i] & mask;
      if (((win ^ fm) >>> 0) === cX) nmX++;
      if ((((win - fm) & mask) >>> 0) === cS) nmS++;
    }
  }
  if (!n) return null;
  return { n, rX: mX / n, rS: mS / n, cX: cXg, cS: cSg, nNM, rXnm: nNM ? nmX / nNM : 0, rSnm: nNM ? nmS / nNM : 0 };
}
function natWidth(fcol, idx) {
  let mn = Infinity, mx = -Infinity;
  for (const i of idx) { const f = fcol[i]; if (f === NONE) continue; if (f < mn) mn = f; if (f > mx) mx = f; }
  if (mn === Infinity) return 0;
  const range = mn < 0 ? mx - mn : mx; let w = 0; while ((1 << w) <= range) w++;
  return Math.max(1, w);
}
const TH = { rate: 0.85, rateNM: 0.75, minNM: 30 };
function searchFields(t, idx, groups) {
  groups = groups || [idx];
  const keyed = groups.length > 1, found = [];
  for (let j = 0; j < NF; j++) {
    if (keyed && FEATS[j] === 'round') continue;
    const fcol = t.F[j], nw = natWidth(fcol, idx); if (!nw) continue;
    for (let o = 0; o < 64; o++) {
      if (!keyed) { // prefilter: the window's lowest bit must follow the feature's lowest bit (or its complement)
        let n = 0, ag = 0; const a = t.sh[o];
        for (const i of idx) { const f = fcol[i]; if (f === NONE) continue; n++; if ((a[i] & 1) === (f & 1)) ag++; }
        if (!n) continue;
        const r = ag / n; if (r > 1 - TH.rate * 0.95 && r < TH.rate * 0.95) continue;
      }
      let best = null;
      for (let w = 1; w <= 16 && o + w <= 64; w++) {
        const r = testWindow(t, o, w, fcol, groups); if (!r) break;
        const okX = r.rX >= TH.rate && r.rXnm >= TH.rateNM && r.nNM >= TH.minNM, okS = r.rS >= TH.rate && r.rSnm >= TH.rateNM && r.nNM >= TH.minNM;
        if (!okX && !okS) break;
        const op = okX && (r.rX >= r.rS || !okS) ? 'xor' : 'add';
        const rec = { feat: FEATS[j], o, w, op, c: keyed ? null : op === 'xor' ? r.cX : r.cS, rate: op === 'xor' ? r.rX : r.rS, rateNM: op === 'xor' ? r.rXnm : r.rSnm, n: r.n, nNM: r.nNM, nat: nw };
        if (w <= nw || !best) best = rec;
      }
      if (best && (best.w >= (keyed ? 3 : 2) || best.nat === 1)) found.push(best);
    }
  }
  // prune: drop windows inside a wider window of the same feature with about the same rate; one best feature per window
  found.sort((a, b) => b.w - a.w || b.rate - a.rate);
  const kept = [];
  for (const f of found) if (!kept.some(g => g.feat === f.feat && g.o <= f.o && g.o + g.w >= f.o + f.w && g.rate >= f.rate - 0.01)) kept.push(f);
  const byWin = new Map();
  for (const f of kept) { const k = f.o + ':' + f.w; if (!byWin.has(k)) byWin.set(k, []); byWin.get(k).push(f); }
  const res = [];
  for (const fs of byWin.values()) { fs.sort((a, b) => b.rate - a.rate || b.rateNM - a.rateNM); res.push({ ...fs[0], alts: fs.slice(1).filter(x => x.rate >= fs[0].rate - 0.02).map(x => x.feat) }); }
  // a window fully inside a better-or-equal window of another feature is a duplicate description; keep the wider one
  const out = res.filter(f => !res.some(g => g !== f && g.o <= f.o && g.o + g.w >= f.o + f.w && (g.w > f.w) && g.rate >= f.rate - 0.005 && (g.alts.includes(f.feat) || g.feat === f.feat)));
  return out.sort((a, b) => b.o - a.o);
}
function bitStats(t, idx) {
  const c = new Array(64).fill(0);
  for (const i of idx) for (let b = 0; b < 32; b++) { c[b] += (t.lo[i] >>> b) & 1; c[32 + b] += (t.hi[i] >>> b) & 1; }
  return c.map(x => idx.length ? x / idx.length : 0);
}
const constCount = p => p.filter(x => x < 0.01 || x > 0.99).length;
// Tag candidates: a window of width 1-4 outside the found fields whose values split the messages into a few classes that
// have more constant bits than the whole set (gain = extra constant bits per message, minus the tag's own width).
function findTags(t, idx, covered, maxN = 4) {
  const base = constCount(bitStats(t, idx));
  const cands = [];
  for (let w = 1; w <= 4; w++) for (let o = 0; o + w <= 64; o++) {
    let ov = false; for (let b = o; b < o + w; b++) if (covered.has(b)) ov = true; if (ov) continue;
    const mask = (1 << w) - 1, cnt = new Map();
    for (const i of idx) { const x = t.sh[o][i] & mask; cnt.set(x, (cnt.get(x) || 0) + 1); }
    const big = [...cnt].filter(([, c]) => c >= 0.03 * idx.length);
    if (big.length < 2) continue;
    if (big.reduce((a, [, c]) => a + c, 0) / idx.length < 0.97) continue;
    let gain = -w;
    for (const [x, c] of big) { const sub = idx.filter(i => (t.sh[o][i] & mask) === x); gain += (constCount(bitStats(t, sub)) - base) * c / idx.length; }
    if (gain >= 1) cands.push({ o, w, gain, classes: big.map(([x, c]) => ({ x, share: c / idx.length })).sort((a, b) => b.share - a.share) });
  }
  cands.sort((a, b) => b.gain - a.gain);
  const out = [];
  for (const c of cands) { if (out.some(d => d.o < c.o + c.w && c.o < d.o + d.w)) continue; out.push(c); if (out.length >= maxN) break; }
  return out;
}
const bitmapString = p => { let s = ''; for (let b = 63; b >= 0; b--) { const x = p[b]; s += x < 0.005 ? '0' : x > 0.995 ? '1' : x < 0.05 ? 'o' : x > 0.95 ? 'l' : String(Math.min(9, Math.floor(x * 10))); if (b % 8 === 0 && b) s += ' '; } return s; };
// meanDev = mean over bits of |P(bit of the XOR = 1) - 0.5|; for unrelated random values it is about 0.399/sqrt(n)
const pairSummary = acc => acc.n ? { n: acc.n, meanDev: +(acc.c.reduce((a, x) => a + Math.abs(x / acc.n - 0.5), 0) / 64).toFixed(4), randomExpect: +(0.399 / Math.sqrt(acc.n)).toFixed(4), excess: +(acc.c.reduce((a, x) => a + Math.abs(x / acc.n - 0.5), 0) / 64 - 0.399 / Math.sqrt(acc.n)).toFixed(4), bitmap: bitmapString(acc.c.map(x => x / acc.n)) } : { n: 0 };

function decodeTeam(team, samples, pairAcc, opts = {}) {
  const t = makeTable(samples), all = [...Array(t.n).keys()];
  const out = { nSample: t.n };
  if (t.n < 200) { out.verdict = 'too few first messages'; return { out, specs: [] }; }
  const p = bitStats(t, all);
  out.bitP = p.map(x => +x.toFixed(4)); out.bitmap = bitmapString(p);
  let cm = 0n, cv = 0n; p.forEach((x, b) => { if (x < 0.01 || x > 0.99) { cm |= 1n << BigInt(b); if (x > 0.99) cv |= 1n << BigInt(b); } });
  out.constBits = constCount(p); out.constMask = '0x' + cm.toString(16).padStart(16, '0'); out.constValue = '0x' + cv.toString(16).padStart(16, '0');
  out.varyingBits = p.filter(x => x >= 0.05 && x <= 0.95).length;
  out.pairs = Object.fromEntries(Object.entries(pairAcc).map(([k, a]) => [k, pairSummary(a)]));
  const specs = [];
  const toOut = (f, cls) => ({ bits: [f.o, f.o + Math.min(f.w, f.nat) - 1], width: Math.min(f.w, f.nat), feat: f.feat, op: f.op, c: f.c, rateSample: +f.rate.toFixed(4), rateNMSample: +f.rateNM.toFixed(4), nSample: f.n, nat: f.nat, truncated: f.w < f.nat, alts: f.alts, cls: cls || null });
  const addSpec = (f, cls) => { const w = Math.min(f.w, f.nat); const sp = { o: f.o, w, feat: f.feat, op: f.op, c: f.c, cls: cls || null }; if (w < f.w) { const mask = (1 << w) - 1; sp.c = f.c & mask; } specs.push(sp); return specs.length - 1; };
  // global fields (constant key)
  const glob = searchFields(t, all);
  out.fields = glob.map(f => ({ ...toOut(f), spec: addSpec(f) }));
  const covered = new Set(); for (const f of glob) for (let b = f.o; b < f.o + Math.min(f.w, f.nat); b++) covered.add(b);
  // classes: try up to four tag candidates and keep the one whose classes explain the most new bits
  const sameField = (f, g) => g.feat === f.feat && g.o === f.o && Math.min(g.w, g.nat) === Math.min(f.w, f.nat);
  const cands = findTags(t, all, covered);
  let bestTag = null;
  out.tagCandidates = [];
  for (const tg of cands) {
    const mask = (1 << tg.w) - 1, classes = [];
    const newBits = new Set();
    for (const c of tg.classes) {
      const sub = all.filter(i => (t.sh[tg.o][i] & mask) === c.x);
      const cls = { x: c.x, share: +c.share.toFixed(4), n: sub.length, sub };
      if (sub.length >= 200) {
        cls.found = searchFields(t, sub).filter(f => !glob.some(g => sameField(f, g)));
        for (const f of cls.found) for (let b = f.o; b < f.o + Math.min(f.w, f.nat); b++) if (!covered.has(b)) newBits.add(b);
      }
      classes.push(cls);
    }
    out.tagCandidates.push({ bits: [tg.o, tg.o + tg.w - 1], gain: +tg.gain.toFixed(2), classes: tg.classes.length, newBitsExplained: newBits.size });
    if (!bestTag || newBits.size > bestTag.newBits || (newBits.size === bestTag.newBits && tg.gain > bestTag.tg.gain)) bestTag = { tg, classes, newBits: newBits.size };
  }
  if (bestTag && bestTag.newBits > 0) {
    const tg = bestTag.tg;
    out.tag = { bits: [tg.o, tg.o + tg.w - 1], gain: +tg.gain.toFixed(2), classes: [] };
    for (const c of bestTag.classes) {
      const cls = { x: c.x, share: c.share, n: c.n };
      if (c.sub.length >= 200) {
        const pc = bitStats(t, c.sub); cls.bitmap = bitmapString(pc); cls.constBits = constCount(pc);
        cls.fields = c.found.map(f => ({ ...toOut(f, { o: tg.o, w: tg.w, x: c.x }), spec: addSpec(f, { o: tg.o, w: tg.w, x: c.x }) }));
      }
      out.tag.classes.push(cls);
    }
  }
  // direction classes (teams that usually send different values in different directions)
  if (opts.multiValue) {
    out.dirClasses = [];
    for (let d = 0; d < 4; d++) {
      const sub = all.filter(i => t.F[FI.firstDir][i] === d);
      const cls = { firstDir: DIRS[d], n: sub.length, share: +(sub.length / t.n).toFixed(4) };
      if (sub.length >= 200) {
        const pc = bitStats(t, sub); cls.bitmap = bitmapString(pc); cls.constBits = constCount(pc);
        const tagF = out.tag ? out.tag.classes.flatMap(c => c.fields || []).map(f => ({ feat: f.feat, o: f.bits[0], w: f.width, nat: f.width })) : [];
        const fc = searchFields(t, sub).filter(f => !glob.some(g => sameField(f, g)) && !tagF.some(g => sameField(f, g)));
        cls.fields = fc.map(f => ({ ...toOut(f, { feat: 'firstDir', x: d }), spec: addSpec(f, { feat: 'firstDir', x: d }) }));
      }
      out.dirClasses.push(cls);
    }
  }
  // round-derived bits: vary across first messages but are fixed within a round across games, and no found field explains
  // them (a plain round field would also cancel in same-round pairs, so found fields are excluded first)
  const sr = out.pairs.sameRoundDiffGame, rd = out.pairs.randomDiffGame;
  out.roundPairExcess = sr && rd && sr.n && rd.n ? +(sr.meanDev - rd.meanDev).toFixed(4) : null;
  const srAcc = pairAcc.sameRoundDiffGame;
  out.roundDerivedBits = [];
  if (srAcc.n >= 100) p.forEach((x, b) => { const q = srAcc.c[b] / srAcc.n; if (x >= 0.05 && x <= 0.95 && q <= 0.05 && !covered.has(b)) out.roundDerivedBits.push(b); });
  if (out.roundDerivedBits.length >= 4 || (out.roundPairExcess !== null && out.roundPairExcess > 0.03 && glob.every(f => f.feat !== 'round'))) {
    const byR = new Map(); for (const i of all) { const r = t.F[FI.round][i]; if (!byR.has(r)) byR.set(r, []); byR.get(r).push(i); }
    const groups = [...byR.values()];
    out.roundKeyFields = searchFields(t, all, groups).filter(f => !glob.some(g => g.feat === f.feat && g.o === f.o)).map(f => toOut(f));
    // strongest partial matches under a round key (width 5), ranked by lift over the same window against a constant
    const zero = new Int32Array(t.n), base = [], part = [];
    for (let o = 0; o + 5 <= 64; o++) { const z = testWindow(t, o, 5, zero, groups); base[o] = z ? z.rX : 0; }
    for (let j = 0; j < NF; j++) { if (FEATS[j] === 'round') continue; for (let o = 0; o + 5 <= 64; o++) { const r = testWindow(t, o, 5, t.F[j], groups); if (r && r.nNM >= 100) { const rate = Math.max(r.rX, r.rS); part.push({ feat: FEATS[j], bits: [o, o + 4], op: r.rX >= r.rS ? 'xor' : 'add', rate: +rate.toFixed(4), windowAlone: +base[o].toFixed(4), lift: +(rate - base[o]).toFixed(4) }); } } }
    part.sort((a, b) => b.lift - a.lift);
    out.roundKeyPartial = part.slice(0, 8);
  }
  // residual varying bits
  const cov = new Set(covered);
  if (out.tag) { for (let b = out.tag.bits[0]; b <= out.tag.bits[1]; b++) cov.add(b); for (const c of out.tag.classes) for (const f of c.fields || []) for (let b = f.bits[0]; b <= f.bits[1]; b++) cov.add(b); }
  for (const c of out.dirClasses || []) for (const f of c.fields || []) for (let b = f.bits[0]; b <= f.bits[1]; b++) cov.add(b);
  const varying = []; p.forEach((x, b) => { if (x >= 0.05 && x <= 0.95) varying.push(b); });
  out.varyingCovered = varying.filter(b => cov.has(b)).length;
  out.residualBits = varying.filter(b => !cov.has(b));
  const structured = Math.max(...['sameRound', 'sameSender', 'sameTurn', 'sameRoundDiffGame'].map(k => (out.pairs[k] && out.pairs[k].n >= 50) ? out.pairs[k].excess : 0));
  out.pairStructure = +structured.toFixed(4);
  out.verdict = out.fields.length + (out.tag ? out.tag.classes.reduce((a, c) => a + (c.fields ? c.fields.length : 0), 0) : 0) + (out.dirClasses || []).reduce((a, c) => a + (c.fields ? c.fields.length : 0), 0) > 0
    ? (out.varyingCovered >= 0.6 * varying.length ? 'decoded' : 'partly decoded')
    : out.constBits === 0 && structured < 0.01 ? 'no structure (hash or cipher)'
    : out.roundDerivedBits.length >= 4 || (out.roundPairExcess !== null && out.roundPairExcess > 0.03) ? 'round-dependent structure, fields not recovered'
    : 'structured, fields not recovered';
  return { out, specs };
}

// ---------------------------------------------------------------------------------------------------------------
// Main.
function runPool(tasks, jobs, src, onResult) {
  return new Promise((resolve, reject) => {
    const queue = tasks.slice(); let live = Math.min(jobs, queue.length);
    if (!live) return resolve();
    for (let i = 0; i < live; i++) {
      const w = new Worker(__filename, { workerData: { src } });
      const next = () => { const task = queue.shift(); if (!task) { w.terminate(); if (--live === 0) resolve(); return; } w.postMessage(task); };
      w.on('message', m => { onResult(m); next(); });
      w.on('error', reject);
      next();
    }
  });
}
const sum = a => a.reduce((x, y) => x + y, 0);
const r4 = x => (x === null || x === undefined || !isFinite(x)) ? null : +x.toFixed(4);
function spearman(xs, ys) {
  const rank = a => { const idx = a.map((v, i) => [v, i]).sort((p, q) => p[0] - q[0]); const r = new Array(a.length); for (let i = 0; i < idx.length;) { let j = i; while (j + 1 < idx.length && idx[j + 1][0] === idx[i][0]) j++; for (let k = i; k <= j; k++) r[idx[k][1]] = (i + j) / 2 + 1; i = j + 1; } return r; };
  const rx = rank(xs), ry = rank(ys), n = xs.length, mx = sum(rx) / n, my = sum(ry) / n;
  let a = 0, b = 0, c = 0; for (let i = 0; i < n; i++) { a += (rx[i] - mx) * (ry[i] - my); b += (rx[i] - mx) ** 2; c += (ry[i] - my) ** 2; }
  return b && c ? a / Math.sqrt(b * c) : null;
}

// ---------------------------------------------------------------------------------------------------------------
// --tables FILE: print the Markdown tables and protocol cards used in research/observations/top-sonar.md (Korean).
const FEAT_KO = { round: '라운드', id: '보낸 드래곤 id', side: '팀(A=0, B=1)', age: '나이', born: '태어난 라운드', parent: '부모 id',
  hx: '머리 x(행동 뒤)', hy: '머리 y(행동 뒤)', hidx: '머리 칸 번호 y·W+x(행동 뒤)', hidxT: '머리 칸 번호 x·H+y(행동 뒤)', hx0: '머리 x(턴 시작)', hy0: '머리 y(턴 시작)',
  hidx0: '머리 칸 번호(턴 시작)', hidxT0: '머리 칸 번호 x·H+y(턴 시작)', tx: '꼬리 x', ty: '꼬리 y', tx0: '꼬리 x(턴 시작)', ty0: '꼬리 y(턴 시작)', len: '길이(행동 뒤)', len0: '길이(턴 시작)',
  fac: '방향(행동 뒤)', fac0: '방향(턴 시작)', steps: '이번 턴 이동 칸 수', splitLen: '분열한 자식 길이', nOwn: '살아 있는 아군 수', nEnemy: '살아 있는 적 수',
  ownTotal: '아군 총길이', ownLongest: '아군 최장 길이', enemyTotal: '적 총길이', enemyLongest: '적 최장 길이', kingX: '가장 긴 아군 머리 x', kingY: '가장 긴 아군 머리 y', kingId: '가장 긴 아군 id',
  eKingX: '가장 긴 적 머리 x', eKingY: '가장 긴 적 머리 y', vEnX: '보이는 가장 가까운 적 머리 x', vEnY: '보이는 가장 가까운 적 머리 y', vEnDx: '그 적의 dx', vEnDy: '그 적의 dy',
  vAlX: '보이는 가장 가까운 아군 머리 x', vAlY: '보이는 가장 가까운 아군 머리 y', vAlDx: '그 아군의 dx', vAlDy: '그 아군의 dy', vPeX: '보이는 가장 가까운 진주 x', vPeY: '보이는 가장 가까운 진주 y',
  vPeDx: '그 진주의 dx', vPeDy: '그 진주의 dy', nVisEnH: '보이는 적 머리 수', nVisEnSeg: '보이는 적 마디 수', nVisAlH: '보이는 아군 머리 수', nVisPe: '보이는 진주 수',
  gEnX: '가장 가까운 적 머리 x(전역)', gEnY: '가장 가까운 적 머리 y(전역)', W: '지도 폭', H: '지도 높이', dirMask: '이 값을 보낸 방향 묶음', nDirs: '이번 턴 방향 수',
  firstDir: '이 값의 첫 방향', nVals: '이번 턴 서로 다른 값 수', msgIdx: '턴 안 값 순번', rcvKind: '받는 쪽 종류', rcvId: '받는 드래곤 id', rcvX: '받는 쪽 머리 x', rcvY: '받는 쪽 머리 y', rcvLen: '받는 쪽 길이' };
const VERDICT_KO = { 'decoded': '해독', 'partly decoded': '일부 해독', 'partly decoded (position field)': '일부 해독(좌표 창)', 'no structure (hash or cipher)': '구조 없음(해시·암호로 보임)',
  'round-dependent structure, fields not recovered': '라운드 의존 구조, 필드 못 찾음', 'structured, fields not recovered': '구조 있음, 필드 못 찾음', 'too few first messages': '처음 메시지 부족' };
const PAIR_KO = { sameRound: '같은 경기·같은 라운드·다른 발신자', sameSender: '같은 발신자·다른 라운드', sameTurn: '같은 턴의 다른 값', sameRoundDiffGame: '다른 경기·같은 라운드 번호', randomDiffGame: '다른 경기·다른 라운드' };
function printTables(J) {
  const V = v => VERDICT_KO[v] || v;
  const P = x => x === null || x === undefined ? '–' : (100 * x).toFixed(1);
  const N = (x, d = 2) => x === null || x === undefined ? '–' : (+x).toFixed(d);
  const names = Object.keys(J.teams).filter(n => !J.teams[n].pooledInOthers);
  const rows = [...names.map(n => [n, J.teams[n]]), ...(J.others ? [['기타 ' + J.others.members.length + '팀 합산', J.others]] : [])];
  const esc = s => s.replace(/\|/g, '\\|');
  const out = [];
  const table = (head, body) => { head = head.map(h => h.replace(/\|/g, '\\|')); out.push('| ' + head.join(' | ') + ' |', '|' + head.map((h, i) => i ? '---:' : '---').join('|') + '|'); for (const r of body) out.push('| ' + r.join(' | ') + ' |'); out.push(''); };
  const m = J.meta, ck = m.checks;
  out.push(`<!-- node tools/sonar_study.js --tables (generated ${m.generatedAt}, snapshot rows ${m.snapshot.rowsUsed}, last gameId ${m.snapshot.lastRow.gameId}) -->`, '');
  { let tg = 0, tu = 0, pi = 0, ms = 0, fm = 0; for (const t of Object.values(J.teams)) { tg += t.games; tu += t.volume.dragonTurns; pi += t.volume.pings; ms += t.volume.messages; fm += t.decode.firstMessagesAll; }
    out.push(`스냅숏: index.jsonl 앞 ${m.snapshot.rowsUsed}행 (실행 시 ${m.snapshot.indexRowsAtStart}행), ${m.snapshot.games}경기, 마지막 행 battleId ${m.snapshot.lastRow.battleId} gameId ${m.snapshot.lastRow.gameId}, 최대 gameId ${m.snapshot.maxGameId}, 대전 시각 ${m.snapshot.battleTimeRange.join(' ~ ')}. 팀 ${Object.keys(J.teams).length}개, 팀-경기 ${tg}, 드래곤-턴 ${tu}, 핑 ${pi}, 메시지(턴 안 서로 다른 값) ${ms}, 처음 메시지 ${fm}. 표본: 팀-경기당 처음 메시지 최대 ${m.samplePerTeamGame}개. 문턱: 일치율 ${m.thresholds.rate}, 최빈값 밖 일치율 ${m.thresholds.rateNM}, 최소 ${m.thresholds.minNM}개.`, ''); }
  out.push(`점검: 승자 일치 ${ck.winnerMatch}/${m.snapshot.games}, 몸 재구성 불일치 ${ck.bodyMismatches}/${ck.updates}, 음파 재현 ${ck.simAgree}/${ck.pings} (불일치 ${ck.simDisagree}), 멈춘 곳 코드 ${JSON.stringify(ck.stopKinds)}`, '');
  out.push('### 표 A1. 보내는 양'); table(['팀', '경기', '핑 없는 경기', '경기당 라운드', '드래곤-턴당 핑', '경기별 드래곤-턴당 핑 (최소/중앙/최대)', '방향 0/1/2/3/4 (턴 %)', '같은 값 % (2방향 이상 턴)', '턴당 값 수', '0 값 %', '경기당 서로 다른 값 (중앙값)'],
    rows.map(([n, t]) => [esc(n), t.games, t.volume.gamesWithoutPings, N(t.roundsPerGame, 0), N(t.volume.pingsPerDragonTurn), [t.volume.perGamePingsPerDragonTurn.min, t.volume.perGamePingsPerDragonTurn.median, t.volume.perGamePingsPerDragonTurn.max].map(x => N(x)).join(' / '), t.volume.dirsHist.map(P).join(' / '), P(t.volume.sameValueShareOfMultiPingTurns), N(t.volume.valuesPerPingedTurn), P(t.volume.zeroPingShare), t.volume.distinctValuesPerGameMedian ?? '–']));
  out.push('### 표 A2. 100라운드 구간별 드래곤-턴당 핑'); table(['팀', '0–99', '100–199', '200–299', '300–399', '400–499'], rows.map(([n, t]) => [esc(n), ...t.volume.byWindow.map(w => N(w.pingsPerDragonTurn))]));
  out.push('### 표 A3. 4방향 턴 비율, 구간별 (드래곤-턴 %)'); table(['팀', '0–99', '100–199', '200–299', '300–399', '400–499'], rows.map(([n, t]) => [esc(n), ...t.volume.byWindow.map(w => P(w.dirsHist[4]))]));
  out.push('### 표 A4. 반복과 중계 (0이 아닌 메시지 %)'); table(['팀', '처음', '같은 발신자 반복', '받은 값 중계', '받지 않고 같은 값', '적이 먼저 보낸 값', '중계까지 평균 라운드', '라운드·발신자당 서로 다른 값'],
    rows.map(([n, t]) => [esc(n), P(t.volume.relay.first), P(t.volume.relay.sameSender), P(t.volume.relay.relayReceived), P(t.volume.relay.shared), P(t.volume.relay.enemyValue), N(t.volume.relayDelayMeanRounds, 1), N(t.volume.nonZeroValuesPerSenderRound)]));
  out.push('### 표 B1. 음파가 멈춘 곳 (핑 %)'); table(['팀', '해초', '자기 몸·머리', '다른 아군 몸', '다른 아군 머리', '적 몸', '적 머리', '다른 아군 합', '적 합', '사라짐'],
    rows.map(([n, t]) => { const k = t.delivery.kinds; return [esc(n), P(k.kelp), P(k.self), P(k.allyBody), P(k.allyHead), P(k.enemyBody), P(k.enemyHead), P(t.delivery.otherAlly), P(t.delivery.enemy), P(k.lost)]; }));
  out.push('### 표 B2. 구간별 다른 아군 도달 (핑 %, 그 구간 핑이 200개 미만이면 –)'); table(['팀', '0–99', '100–199', '200–299', '300–399', '400–499'], rows.map(([n, t]) => [esc(n), ...t.volume.byWindow.map(w => w.pings >= 200 ? P(w.kinds.allyBody + w.kinds.allyHead) : '–')]));
  out.push('### 표 B3. 조준 (1~3방향만 보낸 턴, 네 방향을 모두 다시 쏴 본 결과)'); table(['팀', '해당 턴 (드래곤-턴 %)', '보낸 방향 → 다른 아군 %', '네 방향 평균 → 다른 아군 %', 'P(보냄 | 아군에 닿는 방향)', 'P(보냄 | 아니면)', '뒤쪽(꼬리) 방향을 보낸 %', '나머지 방향을 보낸 %'],
    rows.filter(([, t]) => t.aiming && t.aiming.turns >= 1000).map(([n, t]) => { const a = t.aiming; return [esc(n), P(a.shareOfDragonTurns), P(a.chosenAllyRate), P(a.allDirsAllyRate), P(a.pChosenGivenAlly), P(a.pChosenGivenNoAlly), P(a.backwardChosenRate), P(a.otherDirsChosenRate)]; }));
  const all = Object.keys(J.teams).map(n => [n, J.teams[n]]);
  out.push('### 표 C1. 해독 요약 (모든 팀, 처음 메시지 기준)'); table(['팀', '경기', '판정', '처음 메시지', '고정 비트', '변하는 비트', '필드로 설명된 변하는 비트', '쌍 구조 (excess 최대)', '같은 라운드·다른 경기 쌍 − 무작위 쌍'],
    all.map(([n, t]) => { const d = t.decode; return [esc(n), t.games, V(d.verdict), d.firstMessagesAll, d.constBits ?? '–', d.varyingBits ?? '–', d.varyingCovered ?? '–', N(d.pairStructure, 3), N(d.roundPairExcess, 3)]; }));
  out.push('### 표 C2. 좌표 창 탐지 (6비트 창 두 개가 누구의 머리 좌표와 같은가, 처음 메시지 %)'); table(['팀', 'x 비트', 'y 비트', '어느 드래곤이든', '보낸 자신', '다른 아군', '적', '보이는 진주', '우연 기준(모든 창 쌍 평균)', '적 최고 창 (비트, %)', '진주 최고 창 (비트, %)'],
    all.map(([n, t]) => { const p = t.positionFields, x = p.topAnyDragon[0], e = p.topEnemy[0], q = p.topVisiblePearl[0]; return [esc(n), x.xBits.join('–'), x.yBits.join('–'), P(x.anyDragon), P(x.self), P(x.otherOwn), P(x.enemy), P(x.visiblePearl), P(p.chanceMean.anyDragon), `${e.xBits.join('–')}/${e.yBits.join('–')} ${P(e.enemy)}`, `${q.xBits.join('–')}/${q.yBits.join('–')} ${P(q.visiblePearl)}`]; }));
  out.push('### 표 D. 레이더인가 메시지인가'); table(['팀', '4방향 턴 %', '같은 값 % (2방향 이상)', '0 값 %', '경기 최빈 값을 실은 핑 %', '처음 메시지 %', '해독 판정'],
    rows.map(([n, t]) => [esc(n), P(t.volume.dirsHist[4]), P(t.volume.sameValueShareOfMultiPingTurns), P(t.volume.zeroPingShare), P(t.volume.modalValuePingShare), P(t.volume.relay.first), t.decode ? V(t.decode.verdict) : '–']));
  out.push('### 표 E. 성적과 나란히 (기술 통계, 인과 아님)'); table(['팀', '경기', '승률', '평균 Elo', '드래곤-턴당 핑', '4방향 턴 %', '다른 아군 도달 %', '조준 차 P(보냄|아군)−P(보냄|아니면)', '해독 판정'],
    rows.map(([n, t]) => [esc(n), t.games, P(t.winRate), t.eloMean ?? '–', N(t.volume.pingsPerDragonTurn), P(t.volume.dirsHist[4]), P(t.delivery.otherAlly), t.aiming && t.aiming.turns >= 1000 ? P(t.aiming.pChosenGivenAlly - t.aiming.pChosenGivenNoAlly) : '–', t.decode ? V(t.decode.verdict) : '–']));
  const small = Object.keys(J.teams).filter(n => J.teams[n].pooledInOthers).map(n => [n, J.teams[n]]);
  if (small.length) { out.push('### 표 S. 소표본 팀 (' + J.meta.minGames + '경기 미만, 위 표에서는 "기타"로 합산)'); table(['팀', '경기', '승률', '평균 Elo', '드래곤-턴당 핑', '4방향 턴 %', '같은 값 %', '다른 아군 도달 %', '조준 차', '처음 메시지 %', '해독 판정'],
    small.map(([n, t]) => [esc(n), t.games, P(t.winRate), t.eloMean ?? '–', N(t.volume.pingsPerDragonTurn), P(t.volume.dirsHist[4]), P(t.volume.sameValueShareOfMultiPingTurns), P(t.delivery.otherAlly), t.aiming && t.aiming.turns >= 1000 ? P(t.aiming.pChosenGivenAlly - t.aiming.pChosenGivenNoAlly) : '–', P(t.volume.relay.first), V(t.decode.verdict)])); }
  out.push('승률과의 스피어만 순위 상관 (' + Object.values(J.association)[0].teams + '팀): ' + Object.entries(J.association).map(([k, v]) => `${k} ${N(v.spearmanWithWinRate)}`).join(', '), '');
  out.push('### 규약 카드 (필드: 비트 = 특징, 연산, 일치율 전체/표본, 경기별 중앙값·최소)');
  const fieldLine = (f, pre = '') => `  - ${pre}비트 ${f.bits[0]}–${f.bits[1]}: ${FEAT_KO[f.feat] || f.feat}${f.truncated ? ` (하위 ${f.width}비트)` : ''}${f.op === 'add' ? ` + ${f.c}` : f.c ? ` XOR ${f.c}` : ''} — ${P(f.rateAll)}% (n ${f.nAll}; 표본 ${P(f.rateSample)}%), 경기별 중앙값 ${P(f.perGameMedian)}%, 최소 ${P(f.perGameMin)}%`;
  for (const [n, t] of all) {
    const d = t.decode, p = t.positionFields;
    out.push('', `#### ${esc(n)} (${t.games}경기, 판정: ${V(d.verdict)})`);
    out.push(`- 처음 메시지 ${d.firstMessagesAll}개 (표본 ${d.nSample}). 고정 비트 ${d.constBits}개, 마스크 ${d.constMask}, 값 ${d.constValue}. 비트 지도(63→0): \`${d.bitmap}\``);
    for (const f of d.fields || []) out.push(fieldLine(f));
    if (d.tag) { out.push(`  - 종류 비트 ${d.tag.bits[0]}–${d.tag.bits[1]}: ` + d.tag.classes.map(c => `${c.x} (${P(c.share)}%)`).join(', ')); for (const c of d.tag.classes) for (const f of c.fields || []) out.push(fieldLine(f, `[종류 ${c.x}] `)); }
    if (d.dirClasses) out.push(`  - 첫 방향으로 나눈 몫(표본): ` + d.dirClasses.map(c => `${c.firstDir} ${P(c.share)}%`).join(', '));
    for (const c of d.dirClasses || []) for (const f of c.fields || []) out.push(fieldLine(f, `[첫 방향 ${c.firstDir}] `));
    if (d.subject) out.push(`  - 누구의 정보인가 (id 비트 ${d.subject.idBits.join('–')}, ${d.subject.messages}개): 자신 ${P(d.subject.self)}%, 다른 아군 ${P(d.subject.ownOther)}%, 적 ${P(d.subject.enemy)}%, 없는 id ${P(d.subject.unknown)}%` + (d.subject.counts.ownOther ? '; 다른 아군일 때 ' + d.subject.ownOtherFieldMatch.filter(x => x.n).map(x => `${FEAT_KO[x.feat] || x.feat}(비트 ${x.bits.join('–')})가 그 드래곤과 일치 ${P(x.matchesThatDragon)}% (n ${x.n})`).join(', ') : ''));
    if (d.roundLag) out.push(`  - 라운드 필드(비트 ${d.roundLag.bits.join('–')}${d.roundLag.truncated ? ', 하위 비트만' : ''})와 현재 라운드의 차이: ` + Object.entries(d.roundLag.share).map(([k, v]) => `${k}: ${P(v)}%`).join(', '));
    if (p) { const x = p.topAnyDragon[0]; out.push(`  - 좌표 창 최고: x 비트 ${x.xBits.join('–')}, y 비트 ${x.yBits.join('–')} — 어느 드래곤이든 ${P(x.anyDragon)}% (자신 ${P(x.self)}, 다른 아군 ${P(x.otherOwn)}, 적 ${P(x.enemy)}), 진주 ${P(x.visiblePearl)}%; 우연 기준 ${P(p.chanceMean.anyDragon)}%`); }
    if (p) { const e = p.topEnemy[0], q = p.topVisiblePearl[0]; out.push(`  - 적 머리 좌표 창 최고: x ${e.xBits.join('–')}, y ${e.yBits.join('–')} — ${P(e.enemy)}% (우연 기준 ${P(p.chanceMean.enemy)}%); 보이는 진주 창 최고: x ${q.xBits.join('–')}, y ${q.yBits.join('–')} — ${P(q.visiblePearl)}% (우연 기준 ${P(p.chanceMean.visiblePearl)}%)`); }
    if (d.roundDerivedBits && d.roundDerivedBits.length) out.push(`  - 라운드에만 달린 비트: ${d.roundDerivedBits.join(', ')}`);
    if (d.roundKeyPartial && d.roundKeyPartial.length) out.push(`  - 라운드별 키를 가정한 부분 일치 (5비트 창, 같은 창을 상수와 비교한 값이 우연 기준): ` + d.roundKeyPartial.slice(0, 3).map(x => `비트 ${x.bits.join('–')} ${FEAT_KO[x.feat] || x.feat} ${P(x.rate)}% (우연 ${P(x.windowAlone)}%)`).join(', '));
    for (const f of d.roundKeyFields || []) out.push(`  - (라운드별 키) 비트 ${f.bits[0]}–${f.bits[1]}: ${FEAT_KO[f.feat] || f.feat} ${P(f.rateSample)}%`);
    if (d.residualBits) { const rb = d.residualBits, runs = []; for (let i = 0; i < rb.length; i++) { if (i && rb[i] === rb[i - 1] + 1) runs[runs.length - 1][1] = rb[i]; else runs.push([rb[i], rb[i]]); } out.push(`  - 설명되지 않은 변하는 비트: ${rb.length ? runs.map(([a, b]) => a === b ? a : a + '–' + b).join(', ') : '없음'}`); }
    if (d.pairs) out.push(`  - 두 처음 메시지의 XOR 구조 (excess, 0 = 무관한 무작위 값): ` + Object.entries(d.pairs).filter(([, v]) => v.n).map(([k, v]) => `${PAIR_KO[k] || k} ${N(v.excess, 3)} (n ${v.n})`).join(', '));
  }
  console.log(out.join('\n'));
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--tables') { printTables(JSON.parse(fs.readFileSync(argv[1] || path.join(TOP, 'sonar_study.json'), 'utf8'))); return; }
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const jobs = Math.max(1, Math.min(4, +opt('jobs', 4) || 4)), K = +opt('sample', 500), minGames = +opt('min-games', 15);
  const outFile = path.resolve(opt('out', path.join(TOP, 'sonar_study.json'))), limit = opt('limit', null);
  const t0 = Date.now();
  const lines = fs.readFileSync(INDEX, 'utf8').split('\n').filter(l => l.trim());
  const nAtStart = lines.length, nRows = opt('rows', null) === null ? nAtStart : Math.min(+opt('rows'), nAtStart);
  let rows = lines.slice(0, nRows).map(l => JSON.parse(l));
  const seenKey = new Set(); rows = rows.filter(r => { const k = r.battleId + ':' + r.gameId; if (seenKey.has(k)) return false; seenKey.add(k); return true; });
  if (limit !== null) rows = rows.slice(0, +limit);
  const missing = rows.filter(r => !fs.existsSync(replayFile(r)));
  if (missing.length) throw Error(missing.length + ' replays missing, e.g. ' + replayFile(missing[0]));
  const ats = rows.map(r => r.at).sort();
  const snapshot = { indexRowsAtStart: nAtStart, rowsUsed: nRows, games: rows.length, lastRow: { battleId: rows[rows.length - 1].battleId, gameId: rows[rows.length - 1].gameId },
    maxGameId: Math.max(...rows.map(r => r.gameId)), battleTimeRange: [ats[0], ats[ats.length - 1]], limit: limit === null ? null : +limit };
  console.log(`snapshot: first ${nRows} of ${nAtStart} index rows, ${rows.length} games, last row gameId ${snapshot.lastRow.gameId}; jobs ${jobs}`);
  const src = viewerSource();

  // pass 1
  const res1 = [];
  await runPool(rows.map(row => ({ pass: 1, row, K })), jobs, src, m => {
    if (!m.ok) throw Error('pass 1 failed on ' + m.gameId + ': ' + m.err);
    res1.push(m.res); if (res1.length % 50 === 0) console.log(`  pass 1: ${res1.length}/${rows.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  });
  const rowByGame = new Map(rows.map(r => [r.gameId, r]));
  res1.sort((a, b) => rows.indexOf(rowByGame.get(a.gameId)) - rows.indexOf(rowByGame.get(b.gameId)));
  const checks = { winnerMatch: 0, winnerMismatch: [], updates: 0, bodyMismatches: 0, pings: 0, orphanPings: 0, simAgree: 0, simDisagree: 0, simMissing: 0, stopKinds: {} };
  for (const g of res1) {
    if (String(g.winnerIndex).toUpperCase() === g.winnerReplay) checks.winnerMatch++; else checks.winnerMismatch.push(g.gameId);
    for (const k of ['updates', 'bodyMismatches', 'pings', 'orphanPings', 'simAgree', 'simDisagree', 'simMissing']) checks[k] += g.checks[k];
    for (const [k, v] of Object.entries(g.checks.stopKinds)) checks.stopKinds[k] = (checks.stopKinds[k] || 0) + v;
  }

  // aggregate per team (and pooled "others")
  const T = new Map();
  const blank = name => ({
    name, games: 0, wins: 0, elo: [], rank: null, rounds: 0, turns: new Array(NWIN).fill(0), pings: new Array(NWIN).fill(0), dirHist: Array.from({ length: NWIN }, () => new Array(5).fill(0)),
    kinds: Array.from({ length: NWIN }, () => new Array(KINDS.length).fill(0)), multiPingTurns: 0, sameValueTurns: 0, valuesPerPingedTurn: 0, pingedTurns: 0,
    zeroPings: 0, tailPings: 0, msgs: 0, zeroMsgs: 0, relay: { first: 0, sameSender: 0, relayReceived: 0, shared: 0, enemyValue: 0 }, relayDelay: [0, 0],
    roundSenders: 0, roundValues: 0, modalPings: 0, distinctValues: 0, aim: {}, firstBits: new Array(64).fill(0), firstN: 0,
    pairs: { sameRound: newAcc(), sameSender: newAcc(), sameTurn: newAcc(), sameRoundDiffGame: newAcc(), randomDiffGame: newAcc() },
    samples: [], roundFirst: [], perGameDistinct: [], perGamePPT: [],
    posPairs: Object.fromEntries(POS_CATS.map(c => [c, new Float64Array(4096)])),
  });
  const addSide = (a, s, g, won, row, side) => {
    a.games++; if (won) a.wins++; a.rounds += g.rounds;
    a.elo.push(side === 'A' ? row.eloA : row.eloB); a.rank = side === 'A' ? row.rankA : row.rankB;
    for (let w = 0; w < NWIN; w++) { a.turns[w] += s.turns[w]; a.pings[w] += s.pings[w]; for (let k = 0; k < 5; k++) a.dirHist[w][k] += s.dirHist[w][k]; for (let k = 0; k < KINDS.length; k++) a.kinds[w][k] += s.kinds[w][k]; }
    for (const k of ['multiPingTurns', 'sameValueTurns', 'valuesPerPingedTurn', 'pingedTurns', 'zeroPings', 'tailPings', 'msgs', 'zeroMsgs', 'roundSenders', 'roundValues', 'modalPings', 'distinctValues', 'firstN']) a[k] += s[k];
    for (const k of Object.keys(a.relay)) a.relay[k] += s.relay[k];
    a.relayDelay[0] += s.relayDelay[0]; a.relayDelay[1] += s.relayDelay[1];
    for (const [k, v] of Object.entries(s.aim)) a.aim[k] = (a.aim[k] || 0) + v;
    for (let b = 0; b < 64; b++) a.firstBits[b] += s.firstBits[b];
    for (const k of ['sameRound', 'sameSender', 'sameTurn']) { a.pairs[k].n += s.pairs[k].n; for (let b = 0; b < 64; b++) a.pairs[k].c[b] += s.pairs[k].c[b]; }
    a.perGameDistinct.push(s.distinctValues);
    { const tu = sum(s.turns), pi = sum(s.pings); a.perGamePPT.push(tu ? pi / tu : 0); }
    for (const c of POS_CATS) { const src = s.posPairs[c], dst = a.posPairs[c]; for (let k = 0; k < 4096; k++) dst[k] += src[k]; }
    return a;
  };
  const others = blank('others');
  for (const g of res1) {
    const row = rowByGame.get(g.gameId);
    for (const side of ['A', 'B']) {
      const name = side === 'A' ? row.teamA : row.teamB, s = g.sides[side];
      if (!T.has(name)) T.set(name, blank(name));
      const a = addSide(T.get(name), s, g, g.winnerReplay === side, row, side);
      a.samples.push({ F: s.sample.F, V: s.sample.V, game: g.gameId });
      a.roundFirst.push({ game: g.gameId, list: s.roundFirst });
    }
  }
  // cross-game pairs of first messages: same round in different games, and different rounds in different games
  for (const a of T.values()) {
    const byRound = new Map();
    for (const { game, list } of a.roundFirst) for (const [r, hex] of list) { if (!byRound.has(r)) byRound.set(r, []); byRound.get(r).push({ game, v: BigInt('0x' + hex) }); }
    const rounds = [...byRound.keys()].sort((x, y) => x - y);
    for (const r of rounds) { const l = byRound.get(r); for (let i = 1; i < l.length; i++) if (l[i].game !== l[i - 1].game) addXorBits(a.pairs.sameRoundDiffGame, l[i - 1].v, l[i].v); }
    for (let k = 0; k < rounds.length; k++) {
      const l1 = byRound.get(rounds[k]), l2 = byRound.get(rounds[(k + Math.floor(rounds.length / 2)) % rounds.length]);
      if (rounds[k] === rounds[(k + Math.floor(rounds.length / 2)) % rounds.length]) continue;
      for (let i = 0; i < Math.min(l1.length, l2.length); i++) { const j = (i + 1) % l2.length; if (l1[i].game !== l2[j].game) addXorBits(a.pairs.randomDiffGame, l1[i].v, l2[j].v); }
    }
    delete a.roundFirst;
  }
  const teamNames = [...T.keys()].sort((x, y) => T.get(y).games - T.get(x).games || (x < y ? -1 : 1));
  for (const n of teamNames) if (T.get(n).games < minGames) { const a = T.get(n), o = others; o.games += a.games; o.wins += a.wins; o.elo.push(...a.elo); o.rounds += a.rounds;
    for (let w = 0; w < NWIN; w++) { o.turns[w] += a.turns[w]; o.pings[w] += a.pings[w]; for (let k = 0; k < 5; k++) o.dirHist[w][k] += a.dirHist[w][k]; for (let k = 0; k < KINDS.length; k++) o.kinds[w][k] += a.kinds[w][k]; }
    for (const k of ['multiPingTurns', 'sameValueTurns', 'valuesPerPingedTurn', 'pingedTurns', 'zeroPings', 'tailPings', 'msgs', 'zeroMsgs', 'roundSenders', 'roundValues', 'modalPings', 'distinctValues', 'firstN']) o[k] += a[k];
    for (const k of Object.keys(o.relay)) o.relay[k] += a.relay[k]; o.relayDelay[0] += a.relayDelay[0]; o.relayDelay[1] += a.relayDelay[1];
    for (const [k, v] of Object.entries(a.aim)) o.aim[k] = (o.aim[k] || 0) + v; o.perGameDistinct.push(...a.perGameDistinct); o.perGamePPT.push(...a.perGamePPT); }

  // decode each team
  const decoded = {}, specsByTeam = {};
  for (const n of teamNames) {
    const a = T.get(n), tt = Date.now();
    const multiValue = a.multiPingTurns > 0 && a.sameValueTurns / a.multiPingTurns < 0.5;
    const { out, specs } = decodeTeam(n, a.samples, a.pairs, { multiValue });
    decoded[n] = out; specsByTeam[n] = specs;
    console.log(`  decode ${n}: ${out.verdict}, sample ${out.nSample}, fields ${(out.fields || []).length}, ${Date.now() - tt} ms`);
    delete a.samples;
  }

  // pass 2: count every field on all first messages; subject (whose state) and round-lag checks where possible
  const extrasByTeam = {};
  for (const n of teamNames) {
    const d = decoded[n], sp = specsByTeam[n];
    const allF = [...(d.fields || []), ...(d.tag ? d.tag.classes.flatMap(c => c.fields || []) : []), ...(d.dirClasses ? d.dirClasses.flatMap(c => c.fields || []) : [])];
    const idF = allF.filter(f => f.feat === 'id' && !f.truncated).sort((a, b) => b.nSample - a.nSample)[0];
    const roundF = allF.filter(f => f.feat === 'round').sort((a, b) => (a.truncated ? 1 : 0) - (b.truncated ? 1 : 0) || b.nSample - a.nSample || b.width - a.width)[0];
    const ex = {};
    if (idF) { ex.id = { ...sp[idF.spec] }; ex.pos = allF.filter(f => SUBJ[f.feat]).map(f => ({ ...sp[f.spec], feat: f.feat, bits: f.bits })); ex.idBits = idF.bits; }
    if (roundF) { ex.round = { ...sp[roundF.spec], trunc: roundF.truncated }; ex.roundBits = roundF.bits; }
    extrasByTeam[n] = ex;
  }
  const totals = {};
  for (const n of teamNames) {
    const ex = extrasByTeam[n];
    totals[n] = { firstN: 0, counts: specsByTeam[n].map(() => [0, 0]), perGame: specsByTeam[n].map(() => []),
      subj: ex.id ? { n: 0, self: 0, ownOther: 0, enemy: 0, unknown: 0, pos: ex.pos.map(() => [0, 0]), posSender: ex.pos.map(() => [0, 0]) } : null,
      lag: ex.round ? new Array(LAGS.length).fill(0) : null };
  }
  let done2 = 0;
  const need2 = n => specsByTeam[n].length || extrasByTeam[n].id || extrasByTeam[n].round;
  await runPool(rows.filter(r => need2(r.teamA) || need2(r.teamB)).map(row => ({ pass: 2, row,
    specs: { [row.teamA]: specsByTeam[row.teamA], [row.teamB]: specsByTeam[row.teamB] },
    extras: { [row.teamA]: extrasByTeam[row.teamA], [row.teamB]: extrasByTeam[row.teamB] } })), jobs, src, m => {
    if (!m.ok) throw Error('pass 2 failed on ' + m.gameId + ': ' + m.err);
    for (const side of ['A', 'B']) {
      const n = side === 'A' ? m.res.teamA : m.res.teamB, tt = totals[n];
      tt.firstN += m.res.firstN[side];
      m.res.counts[side].forEach(([k, h], j) => { tt.counts[j][0] += k; tt.counts[j][1] += h; if (k >= 20) tt.perGame[j].push(h / k); });
      const S = m.res.subj[side];
      if (S && tt.subj) { for (const k of ['n', 'self', 'ownOther', 'enemy', 'unknown']) tt.subj[k] += S[k]; S.pos.forEach(([a, b], j) => { tt.subj.pos[j][0] += a; tt.subj.pos[j][1] += b; }); S.posSender.forEach(([a, b], j) => { tt.subj.posSender[j][0] += a; tt.subj.posSender[j][1] += b; }); }
      const L = m.res.lag[side];
      if (L && tt.lag) L.forEach((x, j) => { tt.lag[j] += x; });
    }
    if (++done2 % 50 === 0) console.log(`  pass 2: ${done2} games (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  });
  const med = a => { if (!a.length) return null; const s = a.slice().sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
  for (const n of teamNames) {
    const d = decoded[n], tt = totals[n];
    const fill = f => { const [k, h] = tt.counts[f.spec]; f.nAll = k; f.rateAll = k ? r4(h / k) : null; const pg = tt.perGame[f.spec]; f.gamesWith20 = pg.length; f.perGameMin = r4(pg.length ? Math.min(...pg) : null); f.perGameMedian = r4(med(pg)); f.gamesBelow90 = pg.filter(x => x < 0.9).length; };
    for (const f of d.fields || []) fill(f);
    if (d.tag) for (const c of d.tag.classes) for (const f of c.fields || []) fill(f);
    for (const c of d.dirClasses || []) for (const f of c.fields || []) fill(f);
    const ex = extrasByTeam[n];
    if (tt.subj) {
      const S = tt.subj;
      d.subject = { idBits: ex.idBits, messages: S.n, self: r4(S.self / S.n), ownOther: r4(S.ownOther / S.n), enemy: r4(S.enemy / S.n), unknown: r4(S.unknown / S.n), counts: { self: S.self, ownOther: S.ownOther, enemy: S.enemy, unknown: S.unknown },
        ownOtherFieldMatch: ex.pos.map((sp, j) => ({ feat: sp.feat, bits: sp.bits, n: S.pos[j][0], matchesThatDragon: S.pos[j][0] ? r4(S.pos[j][1] / S.pos[j][0]) : null, matchesSender: S.posSender[j][0] ? r4(S.posSender[j][1] / S.posSender[j][0]) : null })) };
    }
    if (tt.lag) { const tot = sum(tt.lag); d.roundLag = { bits: ex.roundBits, truncated: ex.round.trunc, messages: tot, share: Object.fromEntries(LAGS.map((k, j) => [k, r4(tt.lag[j] / tot)])) }; }
    d.firstMessagesAll = T.get(n).firstN; d.firstMessagesPass2 = tt.firstN;
  }

  // per-team summaries
  const pct = (a, b) => b ? r4(a / b) : null;
  const summarize = a => {
    const turns = sum(a.turns), pings = sum(a.pings), kindsAll = KINDS.map((_, k) => sum(a.kinds.map(w => w[k])));
    const dh = [0, 1, 2, 3, 4].map(k => sum(a.dirHist.map(w => w[k])));
    const relayTotal = sum(Object.values(a.relay)), am = a.aim;
    const byWindow = [];
    for (let w = 0; w < NWIN; w++) {
      const pw = a.pings[w];
      byWindow.push({ rounds: [w * WINLEN, w * WINLEN + WINLEN - 1], dragonTurns: a.turns[w], pings: pw, pingsPerDragonTurn: pct(pw, a.turns[w]),
        dirsHist: a.dirHist[w].map(x => pct(x, a.turns[w])), kinds: Object.fromEntries(KINDS.map((k, i) => [k, pct(a.kinds[w][i], pw)])) });
    }
    const elo = a.elo.length ? Math.round(sum(a.elo) / a.elo.length) : null;
    return {
      games: a.games, wins: a.wins, winRate: pct(a.wins, a.games), eloMean: elo, rank: a.rank, roundsPerGame: r4(a.rounds / a.games),
      volume: { dragonTurns: turns, pings, pingsPerDragonTurn: pct(pings, turns), dirsHist: dh.map(x => pct(x, turns)), byWindow,
        sameValueShareOfMultiPingTurns: pct(a.sameValueTurns, a.multiPingTurns), valuesPerPingedTurn: pct(a.valuesPerPingedTurn, a.pingedTurns),
        zeroPingShare: pct(a.zeroPings, pings), tailExitShare: pct(a.tailPings, pings), distinctValuesPerGame: r4(a.distinctValues / a.games),
        distinctValuesPerGameMedian: med(a.perGameDistinct), modalValuePingShare: pct(a.modalPings, pings), messages: a.msgs, zeroMessages: a.zeroMsgs,
        gamesWithoutPings: a.perGamePPT.filter(x => x === 0).length,
        perGamePingsPerDragonTurn: (() => { const q = a.perGamePPT.slice().sort((x, y) => x - y), at = f => r4(q[Math.min(q.length - 1, Math.floor(f * q.length))]); return { min: r4(q[0]), p25: at(0.25), median: at(0.5), p75: at(0.75), max: r4(q[q.length - 1]) }; })(),
        relay: Object.fromEntries(Object.entries(a.relay).map(([k, v]) => [k, pct(v, relayTotal)])), relayCounts: a.relay,
        relayDelayMeanRounds: a.relayDelay[1] ? r4(a.relayDelay[0] / a.relayDelay[1]) : null,
        nonZeroValuesPerSenderRound: pct(a.roundValues, a.roundSenders) },
      delivery: { kinds: Object.fromEntries(KINDS.map((k, i) => [k, pct(kindsAll[i], pings)])), otherAlly: pct(kindsAll[3] + kindsAll[4], pings), enemy: pct(kindsAll[5] + kindsAll[6], pings) },
      aiming: am.turns ? { turns: am.turns, chosen: am.chosen, chosenAllyRate: pct(am.chosenAlly, am.chosen), allDirsAllyRate: pct(am.allAlly, am.all),
        pChosenGivenAlly: pct(am.chosenGivenAlly, am.dirsAlly), pChosenGivenNoAlly: pct(am.chosenGivenNot, am.dirsNot),
        chosenEnemyRate: pct(am.chosenEnemy, am.chosen), allDirsEnemyRate: pct(am.allEnemy, am.all), backwardChosenRate: pct(am.backwardChosen, am.backwardAvail),
        otherDirsChosenRate: pct(am.chosen - am.backwardChosen, am.all - am.backwardAvail), shareOfDragonTurns: pct(am.turns, turns) } : null,
    };
  };
  const teams = {};
  const posSummary = a => {
    if (!a.firstN) return null;
    const rate = (c, k) => r4(a.posPairs[c][k] / a.firstN);
    const valid = []; for (let ox = 0; ox + 6 <= 64; ox++) for (let oy = 0; oy + 6 <= 64; oy++) if (ox >= oy + 6 || oy >= ox + 6) valid.push(ox * 64 + oy);
    const pack = k => ({ xBits: [k >> 6, (k >> 6) + 5], yBits: [k & 63, (k & 63) + 5], anyDragon: rate('anyDragon', k), self: rate('self', k), otherOwn: rate('otherOwn', k), enemy: rate('enemy', k), visiblePearl: rate('visiblePearl', k) });
    const top = c => valid.slice().sort((p, q) => a.posPairs[c][q] - a.posPairs[c][p]).slice(0, 3).map(pack);
    const mean = c => r4(valid.reduce((x, k) => x + a.posPairs[c][k], 0) / valid.length / a.firstN);
    return { firstMessages: a.firstN, chanceMean: Object.fromEntries(POS_CATS.map(c => [c, mean(c)])), topAnyDragon: top('anyDragon'), topEnemy: top('enemy').slice(0, 1), topVisiblePearl: top('visiblePearl').slice(0, 1) };
  };
  for (const n of teamNames) {
    const pf = posSummary(T.get(n)), d = decoded[n];
    teams[n] = { ...summarize(T.get(n)), pooledInOthers: T.get(n).games < minGames, decode: d, positionFields: pf };
    // a coordinate window pair far above chance (>= 20% of first messages and >= 5x the average pair) counts as a found field
    const top = pf && pf.topAnyDragon[0];
    d.positionFieldFound = !!(top && top.anyDragon >= 0.2 && top.anyDragon >= 5 * pf.chanceMean.anyDragon);
    if (d.positionFieldFound && !/decoded/.test(d.verdict)) d.verdict = 'partly decoded (position field)';
  }
  const othersSummary = others.games ? { members: teamNames.filter(n => T.get(n).games < minGames), ...summarize(others) } : null;

  // outcome association (descriptive): teams with >= minGames
  const big = teamNames.filter(n => T.get(n).games >= minGames);
  const metric = { pingsPerDragonTurn: n => teams[n].volume.pingsPerDragonTurn, fourDirShare: n => teams[n].volume.dirsHist[4], otherAllyDelivery: n => teams[n].delivery.otherAlly,
    firstMessageShare: n => teams[n].volume.relay.first, eloMean: n => teams[n].eloMean };
  const assoc = {};
  for (const [k, f] of Object.entries(metric)) { const xs = big.map(f), ys = big.map(n => teams[n].winRate); assoc[k] = { spearmanWithWinRate: r4(spearman(xs, ys)), teams: big.length }; }

  const result = {
    meta: { generatedAt: new Date().toISOString(), script: 'tools/sonar_study.js', args: argv, seconds: Math.round((Date.now() - t0) / 1000), snapshot, jobs, samplePerTeamGame: K, minGames,
      thresholds: TH, features: FEATS, featureDoc: FEAT_DOC, kinds: KINDS,
      checks: { ...checks, winnerMismatch: checks.winnerMismatch.length, winnerMismatchGames: checks.winnerMismatch } },
    definitions: {
      dragonTurn: 'one turnStart of a living dragon (round >= 0)', ping: 'one sonarPing event (one direction)',
      message: 'one distinct value within one dragon turn', firstMessage: 'a non-zero message whose value nobody in the game sent before',
      relay: 'non-zero messages: first / sameSender (this dragon sent it before) / relayReceived (another dragon sent it before and a ray of it stopped on this dragon earlier) / shared (another own dragon sent it before, never delivered to this one) / enemyValue (only the enemy sent it before)',
      kinds: 'what the ray stopped on, relative to the sender: self = own body or head; allyBody/allyHead = another own dragon; lost = nothing within W+H tiles',
      aiming: 'turns with 1-3 requested directions; all four directions are re-cast in the cast-time state (the caster reproduces every recorded ray); chosenAllyRate = share of sent rays that stop on another own dragon, allDirsAllyRate = same over all four directions; pChosenGivenAlly = share of directions whose ray would stop on another own dragon that were sent',
      fields: 'bits [lo, hi] (bit 0 = least significant); window XOR feature == c (op xor) or window - feature == c mod 2^width (op add); rateSample on the sampled first messages, rateAll on all first messages (pass 2); cls = only messages whose tag window equals x',
      pairs: 'XOR of two first messages; meanDev = mean over bits of |P(bit=1) - 0.5| (0.5 = the two values always differ in the same bits); randomExpect = 0.399/sqrt(n), its expected value for unrelated random values; excess = meanDev - randomExpect; sameRound = two senders in one round of one game; sameSender = one sender in two rounds; sameTurn = two values of one turn; sameRoundDiffGame = the same round number in two games; randomDiffGame = different rounds in two games',
      nonZeroValuesPerSenderRound: 'sum over rounds of distinct non-zero values divided by dragons that pinged in that round (1 = every dragon sends its own values; low = dragons share values)',
      positionFields: 'for every pair of 6-bit windows (x, y), the share of first messages where (x, y) is the head of the sender (turn start or after its action), of another own dragon, of an enemy dragon (any of them = anyDragon), or a pearl in the sender view; chanceMean = the average over all window pairs (what unrelated bits give)',
    },
    teams, others: othersSummary, association: assoc,
  };
  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  fs.writeFileSync(outFile, JSON.stringify(result, null, 1));

  // console summary
  const P = x => x === null || x === undefined ? '   -' : (100 * x).toFixed(1).padStart(5);
  console.log(`\nchecks: winner ${checks.winnerMatch}/${res1.length}, body mismatches ${checks.bodyMismatches}/${checks.updates}, rays re-cast ${checks.simAgree} agree / ${checks.simDisagree} disagree / ${checks.simMissing} not cast, orphan pings ${checks.orphanPings}`);
  console.log('team                      games win%  p/dt  4dir%  1val%  zero%  first%  ally%  enemy%  aim(chosen|ally vs |no)  verdict');
  for (const n of teamNames) {
    const t = teams[n], am = t.aiming;
    console.log(`${n.slice(0, 24).padEnd(25)} ${String(t.games).padStart(5)} ${P(t.winRate)} ${(t.volume.pingsPerDragonTurn || 0).toFixed(2).padStart(5)} ${P(t.volume.dirsHist[4])} ${P(t.volume.sameValueShareOfMultiPingTurns)} ${P(t.volume.zeroPingShare)} ${P(t.volume.relay.first)}  ${P(t.delivery.otherAlly)} ${P(t.delivery.enemy)}   ${am && am.turns > 1000 ? P(am.pChosenGivenAlly) + ' vs' + P(am.pChosenGivenNoAlly) : '       -        '}  ${t.decode.verdict}`);
  }
  console.log(`\nwrote ${path.relative(ROOT, outFile)} in ${Math.round((Date.now() - t0) / 1000)} s`);
}

module.exports = { viewerSource, makeLoader, walkGame, geometry, FEATS, KINDS };
if (isMainThread && require.main === module) main().catch(err => { console.error(err); process.exit(1); });
