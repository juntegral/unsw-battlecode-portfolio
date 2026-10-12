#!/usr/bin/env node
'use strict';
// px8_study.js — replay study of the base-px line (px8 = exp/base-px8/bot, px1 = proxy_king v2 = exp/base-px1/bot)
// online (top-6 + DEV test sets) and in the local evaluations against the proxies and r1. Reads replays only: no network,
// no games. Written for research/experiments/online-analysis-px8.md (2026-09-30).
//
// usage (repository root):
//   node exp/online-analysis/px8_study.js [--online base-px8-online,px-king-v2-online] [--local base-px8,base-px8-s3,...]
//                                         [--jobs 3] [--out .cache/online-analysis/px8_study.jsonl] [--limit N]
//   Online sets: data/online/<set>/ (index.json, M<id>.replay; our team is 583). Local labels: exp/<label>/rows.jsonl and
//   exp/<label>/games/<key>/game.replay (our side = row.side). The bot variant (px8 or px1) follows the set/label name.
//
// Per game it rebuilds the board with the step simulation of tools/baseline_study.js (buildGeo; moves, sprints, portals,
// kelp, splits, deaths, pearls through tileChange; checked against every dragonUpdate) and adds, for our side:
//   - timeline every 10 rounds (units, total length, longest) for both sides;
//   - our deaths with a cause class (rammed, ram, allyHead, allyBody-free, enemyBody, trapped, vol, sprintCost), length,
//     king flag (longest at death, len >= 8), distance to the king, the killer's length and sprint, portal crossing in the
//     last 3 rounds, enemy heads seen at the last turn;
//   - the px bots' memory: every px dragon is its own process. For each of our dragons the script keeps the ally book the
//     bot keeps (vision of ally heads in the 7x7 window at its own turn, and our sonar messages delivered to it, decoded
//     with the px format: tag 0xB5 ^ SALT, team bit, kind 0 self / 1 king relay, id, round, x, y, length, 10-bit check).
//     A split child starts with an empty book. From the book: the believed king (kingInfo in pxcore.cpp) and the bot-view
//     length of each visible ally (px8: raised to a recent remembered length when the tail is out of view; px1: visible
//     segments);
//   - trigger counts of the six px8 changes (research/experiments/base-px.md 3.2):
//       T1 front feeding: late small/mid pieces with a big receiver (or the believed king) within Chebyshev 2 and not behind
//          its head. The sacrifice probability of wantSacrifice() is recomputed with both variants' code (q8, q1) and summed
//          as the expected number of sacrifices, next to the actual voluntary deaths of those turns;
//       T2/T3 reserve: pearls eaten from r320 by a smaller ally inside the Manhattan-3 zone of the true king's head or of a
//          visible big ally (len >= 8, >= eater + 3) — the pearls the change tells non-kings to leave;
//       T4 remembered lengths: late decisions where the bot-view length of a visible ally passes the big-receiver bar
//          (>= max(6, 2L)) while its visible segments do not (a flip caused by the change), and where the true length passes
//          but the bot-view length does not (a miss);
//       T5 trapped big dragon: turns with no free neighbour and length >= 5 (enemy head adjacent or not), and the action
//          taken: stub split, ram, or death; whether a stub was possible (units < 64, a free tile at the tail);
//       T6 big-dragon portal caution: turns of length >= 8 (and shorter, for contrast) with a free neighbour through a
//          portal edge, and whether the first step went through it; ally-collision deaths of length >= 8 within 3 rounds of
//          a portal crossing;
//   - king intake: pearls eaten by the team's longest from r300 by source (natural, own voluntary death, own other death,
//     enemy death); voluntary deaths from r300 by Chebyshev distance to the king with the fate of their pearls (eaten by
//     the king at death / the then-longest / any ally / the enemy within 20 rounds);
//   - pressure on our king: enemy heads within Chebyshev 3 at the king's turns from r300, own small pieces within 3, the
//     king's pearls eaten on turns with and without an enemy head in view; sacrifices within Chebyshev 4 of the king split
//     by enemy heads around the king; non-king pieces' Manhattan distance to the king from r340;
//   - sonar: our pings by landing (self, ally, enemy, kelp, none) before and from r300; messages delivered to allies;
//     whether non-king pieces from r340 believe the true king.
// Checks (all expected 0): step simulation vs dragonUpdate, death causes vs the simulation, final state vs the result,
// mass identity, split lengths.
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const TF = require(path.join(ROOT, 'tools', 'top_features.js'));
const BS = require(path.join(ROOT, 'tools', 'baseline_study.js'));
const CHILD = process.argv.includes('--px8-child');
const OWN_TEAM = 583, UNIT_LIMIT = 64;
const DIRS = 'NESW', DX = [0, 1, 0, -1], DY = [-1, 0, 1, 0];
const ELIM_MAPS = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default'];
const MAP_NAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma',
  queen_of_spades: 'Queen Of Spades', schooltime: 'Schooltime', slithery_fight: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const NWIN = 10, WINLEN = 50;
const win = r => Math.max(0, Math.min(NWIN - 1, Math.floor(r / WINLEN)));
const variantOf = s => /px-king|base-px1/.test(s) ? 'px1' : /base-px8|px8/.test(s) ? 'px8' : 'other';

// ---- px sonar format (pxcore.cpp encode/decode, SALT 0x4B1D in both px1 and px8) ----
function mix32(x) { x >>>= 0; x ^= x >>> 16; x = Math.imul(x, 0x7feb352d) >>> 0; x ^= x >>> 15; x = Math.imul(x, 0x846ca68b) >>> 0; x ^= x >>> 16; return x >>> 0; }
const TAG = BigInt(0xB5 ^ (0x4B1D & 0xFF));
function decodePx(v, teamBit, round, W, H) {
  if (typeof v !== 'bigint') return null;
  if ((v >> 56n) !== TAG) return null;
  const body = v & ~1023n;
  const hi = Number((body >> 32n) & 0xFFFFFFFFn), lo = Number(body & 0xFFFFFFFFn);
  if ((mix32((hi ^ mix32(lo)) >>> 0) & 1023) !== Number(v & 1023n)) return null;
  if (Number((v >> 55n) & 1n) !== teamBit) return null;
  const kind = Number((v >> 53n) & 3n), id = Number((v >> 41n) & 4095n), r9 = Number((v >> 32n) & 511n);
  const x = Number((v >> 25n) & 127n), y = Number((v >> 18n) & 127n), len = Number((v >> 10n) & 255n);
  if (x >= W || y >= H || len < 2) return null;
  const back = ((round & 511) - r9 + 512) & 511;
  if (back > 60) return null;
  return { kind, id, rr: round - back, t: y * W + x, len };
}

// ---------------------------------------------------------------------------------------------------------------
function analyse(R, g) {
  const M = R.match.map, { W, H, N, nb, portalEdge } = BS.buildGeo(M);
  const US = g.ourSide, THEM = US === 'A' ? 'B' : 'A', teamBit = US === 'B' ? 1 : 0;
  const V = g.variant, PX = V === 'px8' || V === 'px1';
  const tileOf = s => s.y * W + s.x;
  const tdx = (a, b) => { const d = Math.abs(a % W - b % W); return Math.min(d, W - d); };
  const tdy = (a, b) => { const d = Math.abs(((a / W) | 0) - ((b / W) | 0)); return Math.min(d, H - d); };
  const cheb = (a, b) => Math.max(tdx(a, b), tdy(a, b));
  const man = (a, b) => tdx(a, b) + tdy(a, b);
  const sdx = (a, b) => { let d = b % W - a % W; if (d > W / 2) d -= W; else if (d < -(W / 2)) d += W; return d; };
  const sdy = (a, b) => { let d = ((b / W) | 0) - ((a / W) | 0); if (d > H / 2) d -= H; else if (d < -(H / 2)) d += H; return d; };
  const behind = (sh, sdir, t) => sdx(sh, t) * DX[sdir] + sdy(sh, t) * DY[sdir] < 0;
  const plainStep = (t, d) => (((((t / W) | 0) + DY[d]) % H + H) % H) * W + (((t % W) + DX[d]) % W + W) % W;
  const plainDir = (a, b) => { for (let d = 0; d < 4; d++) if (plainStep(a, d) === b) return d; return -1; };

  const drag = new Map(), occ = new Int32Array(N).fill(-1);
  const pearl = new Int32Array(N).fill(-1); // -1 none, -2 initial, -3 spawned, >= 0 index into deaths[]
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearl[i] = -2;
  const setOcc = d => { for (const t of d.body) occ[t] = d.id; };
  const clrOcc = d => { for (const t of d.body) if (occ[t] === d.id) occ[t] = -1; };
  const mk = (id, team, body, facing, born, parent) => {
    const d = { id, team, body, facing, born, parent, bornLen: body.length, maxLen: body.length, expect: [], fate: null, act: null, steps: 0,
      free: -1, ctx: null, book: team === US && PX ? new Map() : null, inbox: [], lastPortalR: -99, lastTurnR: -1 };
    drag.set(id, d); setOcc(d); return d;
  };
  for (const d0 of M.initialDragons) mk(d0.id, d0.team, d0.body.map(tileOf), DIRS.indexOf(d0.facing), 0, -1);
  const nInit = M.initialDragons.length;
  const teamDr = team => { const a = []; for (const o of drag.values()) if (o.team === team) a.push(o); return a; };
  const unitsOf = team => { let n = 0; for (const o of drag.values()) if (o.team === team) n++; return n; };
  const kingOf = team => { let b = null; for (const o of drag.values()) if (o.team === team && (!b || o.body.length > b.body.length || (o.body.length === b.body.length && o.id < b.id))) b = o; return b; };
  const longestOther = (team, id) => { let m = 0; for (const o of drag.values()) if (o.team === team && o.id !== id && o.body.length > m) m = o.body.length; return m; };
  const freeDirs = d => { const h = d.body[0], out = []; for (let k = 0; k < 4; k++) { if (d.body.length >= 2 && k === ((d.facing + 2) & 3)) continue; const u = nb[h * 4 + k]; if (u >= 0 && occ[u] === -1) out.push(k); } return out; };

  // ---- outputs ----
  const TL = { us: [], them: [] };
  const snap = () => { for (const [k, team] of [['us', US], ['them', THEM]]) { let u = 0, t = 0, l = 0; for (const o of drag.values()) if (o.team === team) { u++; t += o.body.length; if (o.body.length > l) l = o.body.length; } TL[k].push([u, t, l]); } };
  const Z = () => new Array(NWIN).fill(0);
  const deaths = [];       // all deaths (both sides), with pearl fates
  const ourDeaths = [];    // compact records of our deaths
  const cause = { us: {}, them: {} }, causeW = { us: {}, them: {} }, causeLen = { us: {}, them: {} };
  const addCause = (side, c, len, r) => { cause[side][c] = (cause[side][c] || 0) + 1; causeLen[side][c] = (causeLen[side][c] || 0) + len; (causeW[side][c] = causeW[side][c] || Z())[win(r)]++; };
  const splitsW = { us: Z(), them: Z() }, natW = { us: Z(), them: Z() }, eatW = { us: Z(), them: Z() };
  const stubs = { us: 0, usBig: 0, usBigLate: 0, usTrapped: 0 };
  const kingEat = { nat: 0, vol: 0, own: 0, enemy: 0 };            // our longest eats from r300
  const kingEatW = Z();                                            // our longest's eats per window
  const T1 = { turns: 0, q8: 0, q1: 0, deaths: 0, frontTurns: 0, frontAdjTurns: 0, frontDeaths: 0, nearTurns: 0, nearDeaths: 0, excl: 0,
    q8Front: 0, q1Front: 0 };
  const T23 = { eatsLate: 0, eatsNonKing: 0, stealKing: 0, stealVisBig: 0, stealAny: 0, kingEats: 0, kingEatsNearHead: 0 };
  const T4 = { turns: 0, hidden: 0, flip: 0, miss: 0 };
  const T5 = { turns: 0, enemyAdj: 0, canStub: 0, stub: 0, ram: 0, die: 0, other: 0, capBlocked: 0, stubEnemyAdj: 0, ramEnemyAdj: 0, turnsKing: 0 };
  const T6 = { big: { turns: 0, opt: 0, took: 0, blind: 0, tookBlind: 0 }, mid: { turns: 0, opt: 0, took: 0 }, small: { turns: 0, opt: 0, took: 0 },
    crossBig: 0, crossAll: 0, bigAllyDeathsAfterPortal: 0, bigAllyDeaths: 0 };
  const K = { turns: 0, enemyNear: 0, enemyNear2: 0, kingTurnsLate: 0, feeders: 0, turnsThreat: 0, turnsSafe: 0, eatThreat: 0, eatSafe: 0 };  // pressure at the king's turns r300+
  const KD = [0, 0, 0, 0];   // non-king pieces from r340 (true king >= 8): Manhattan distance to the king's head <= 3, 4-8, 9-16, 17+
  const SON = { sentEarly: {}, sentLate: {}, delivered: 0, deliveredLate: 0, decoded: 0, kingKnow: 0, kingKnowTurns: 0, kingAny: 0, kingStale: 0 };
  const chk = { updates: 0, deaths: 0, splits: 0, massOk: 1, final: 1 };
  let round = -1, cur = -1, dropCtx = -1, eatenUs = 0, eatenThem = 0, paidUs = 0, paidThem = 0, deathLenUs = 0, deathLenThem = 0;
  const initTotal = { us: 0, them: 0 }; for (const o of drag.values()) initTotal[o.team === US ? 'us' : 'them'] += o.body.length;

  // ---- per-turn decision context of our dragons ----
  function turnCtx(d) {
    const h = d.body[0], L = d.body.length, r = round;
    const units = unitsOf(d.team);
    const free = freeDirs(d);
    let enemyAdj = false; for (let k = 0; k < 4; k++) { const u = nb[h * 4 + k]; if (u >= 0 && occ[u] !== -1) { const o = drag.get(occ[u]); if (o.team !== d.team && o.body[0] === u) enemyAdj = true; } }
    let enemyNear2 = false, enemyVis = 0; for (const o of drag.values()) if (o.team !== d.team) { const c = cheb(o.body[0], h); if (c <= 3) enemyVis++; if (man(o.body[0], h) <= 2) enemyNear2 = true; }
    // visible allies (head in the 7x7 window)
    const vis = [];
    for (const o of drag.values()) {
      if (o.team !== d.team || o.id === d.id || cheb(o.body[0], h) > 3) continue;
      let nVis = 0; for (const t of o.body) if (cheb(t, h) <= 3) nVis++;
      let tailSeen = false;
      if (nVis === o.body.length && nVis >= 2) {
        const tl = o.body[nVis - 1], pd = plainDir(tl, o.body[nVis - 2]);
        if (pd >= 0) { const bh = plainStep(tl, (pd + 2) & 3); if (cheb(bh, h) <= 3 && occ[bh] !== o.id) tailSeen = true; }
      }
      vis.push({ o, id: o.id, head: o.body[0], hdir: o.facing, nVis, tailSeen, len: o.body.length, lenBot: nVis });
    }
    const ctx = { r, L, units, free: free.length, freeDirs: free, enemyAdj, enemyNear2, enemyVis, vis, kid: d.id, klen: L, kt: h, kr: r, lenBot: new Map() };
    if (d.book) {
      const book = d.book;
      // 1. vision (pxcore.cpp ingest): allies[s.id] = {round, head, keep}
      for (const s of vis) {
        const nw = book.get(s.id);
        const keep = V === 'px8' && !s.tailSeen && nw && nw.round >= r - 3 ? Math.max(nw.len, s.nVis) : s.nVis;
        book.set(s.id, { round: r, t: s.head, len: keep });
      }
      // 2. sonar inbox (delivered since our last turn)
      for (const m of d.inbox) {
        const x = decodePx(m, teamBit, r, W, H); if (!x) continue;
        SON.decoded++;
        if (x.kind === 2) continue;
        if (x.id === d.id) continue;
        const nw = book.get(x.id);
        if (!nw || x.rr >= nw.round) book.set(x.id, { round: x.rr, t: x.t, len: x.len });
      }
      d.inbox = [];
      // 3. bot-view length of visible allies
      for (const s of vis) {
        if (V === 'px8' && !s.tailSeen) { const nw = book.get(s.id); if (nw && nw.round >= r - 3) s.lenBot = Math.max(s.nVis, nw.len); }
      }
      // 4. kingInfo
      let kid = d.id, klen = L, kt = h, kr = r;
      for (const [id, nw] of book) { if (nw.round < r - 40 || nw.t < 0) continue; if (nw.len > klen || (nw.len === klen && id < kid)) { kid = id; klen = nw.len; kt = nw.t; kr = nw.round; } }
      Object.assign(ctx, { kid, klen, kt, kr });
    }
    return ctx;
  }
  // wantSacrifice() probability under a variant's code (pxcore.cpp; px8 adds the front feeding lines and bot-view lengths)
  function sacQ(d, ctx, variant) {
    const r = ctx.r, L = ctx.L, h = d.body[0];
    if (r < 340 || r > 496 || ctx.units <= 3) return { q: 0 };
    const small = L <= 4, mid = !small && r >= 360 && L <= 15;
    if (!small && !mid) return { q: 0 };
    const ramp = Math.min(1, (r - 340 + 1) / 40);
    let kid = ctx.kid; if (kid === d.id) return { q: 0 }; if (ctx.klen < 8) kid = -1;
    let best = 0, front = false, frontAdj = false, near = false;
    for (const s of ctx.vis) {
      const al = variant === 'px8' ? s.lenBot : s.nVis, c = cheb(s.head, h);
      const margin = r >= 440 ? 1 : 3;
      if (al <= L || (mid && al < L + margin)) continue;
      const bigRecv = al >= Math.max(6, 2 * L) || (mid && al >= L + margin);
      let q = 0;
      if (c <= 2 && bigRecv) { q = small ? 0.40 : 0.10; near = true; }
      else if (c <= 3) q = small ? 0.02 : 0.0;
      if (s.id === kid && man(s.head, h) <= 3) q = Math.max(q, 0.35);
      if ((bigRecv || s.id === kid) && c <= 2 && !behind(s.head, s.hdir, h)) {
        front = true; if (man(s.head, h) <= 1) frontAdj = true;
        if (variant === 'px8') q = Math.max(q, man(s.head, h) <= 1 ? 0.90 : 0.55);
      }
      best = Math.max(best, q * ramp);
    }
    return { q: best, front, frontAdj, near };
  }

  const onEat = (d, k, lenBefore) => {
    const src = pearl[k]; pearl[k] = -1;
    const side = d.team === US ? 'us' : 'them', w = win(round);
    eatW[side][w]++;
    if (src < 0) natW[side][w]++;
    const isLongest = lenBefore >= longestOther(d.team, d.id);
    if (src >= 0) { const D = deaths[src]; D.fates.push([round - D.r, side === 'us' ? 0 : 1, d.id, isLongest ? 1 : 0, d.id === D.kingId ? 1 : 0, d.id === D.recvId ? 1 : 0]); }
    if (side !== 'us' || round < 0) return;
    if (isLongest && round >= 300 && d.ctx && d.ctx.kingThreat !== undefined) { if (d.ctx.kingThreat) K.eatThreat++; else K.eatSafe++; }
    if (isLongest && round >= 300) {
      if (src < 0) kingEat.nat++; else { const D = deaths[src]; if (D.side !== 'us') kingEat.enemy++; else if (D.vol) kingEat.vol++; else kingEat.own++; }
    }
    if (isLongest) kingEatW[w]++;
    if (round >= 320) {
      T23.eatsLate++;
      const ctx = d.ctx;
      if (isLongest) { T23.kingEats++; }
      else if (ctx) {
        T23.eatsNonKing++;
        const L = ctx.L;
        const kg = kingOf(d.team);
        const inKing = kg && kg.id !== d.id && kg.body.length >= 8 && kg.body.length >= L + 3 && man(kg.body[0], k) <= 3;
        let inVis = false; for (const s of ctx.vis) if (s.len >= 8 && s.len >= L + 3 && man(s.head, k) <= 3) inVis = true;
        if (inKing) T23.stealKing++; if (inVis) T23.stealVisBig++; if (inKing || inVis) T23.stealAny++;
      }
    }
  };

  for (const e of R.events) {
    if (dropCtx >= 0 && !(e.type === 'tileChange' && e.hasPearl)) dropCtx = -1;
    switch (e.type) {
      case 'roundStart': {
        round = e.round;
        if (round % 10 === 0) snap();
        break;
      }
      case 'turnStart': {
        cur = e.id; const d = drag.get(cur); if (!d) break;
        d.expect = []; d.fate = null; d.act = null; d.steps = 0; d.ctx = null;
        if (d.team !== US || round < 0) break;
        const ctx = turnCtx(d); d.ctx = ctx; d.free = ctx.free;
        const L = ctx.L, r = round;
        // sonar knowledge of the true king (non-king pieces, late, when a real king exists)
        if (d.book && r >= 340) {
          const kg = kingOf(d.team);
          if (kg && kg.id !== d.id && kg.body.length >= 8) {
            SON.kingKnowTurns++;
            if (ctx.kid === kg.id) SON.kingKnow++;
            if (ctx.kid !== d.id && ctx.klen >= 8) SON.kingAny++;
            const nw = d.book.get(kg.id); if (!nw || nw.round < r - 40) SON.kingStale++;
          }
        }
        // T1 front feeding (px sets only; q from both variants' code)
        if (d.book && r >= 340 && r <= 496) {
          const a8 = sacQ(d, ctx, 'px8'), a1 = sacQ(d, ctx, 'px1');
          if (a8.q > 0 || a1.q > 0) {
            const excl = ctx.free === 0 || (L <= 4 && ctx.enemyNear2);   // trapped or a ram possible first
            if (excl) T1.excl++;
            else {
              T1.turns++; T1.q8 += a8.q; T1.q1 += a1.q;
              if (a8.front) { T1.frontTurns++; T1.q8Front += a8.q; T1.q1Front += a1.q; if (a8.frontAdj) T1.frontAdjTurns++; }
              if (a8.near) T1.nearTurns++;
              ctx.t1 = { front: a8.front, near: a8.near };
            }
          }
        }
        // T4 remembered lengths (px8 view vs visible segments vs truth), small pieces late
        if (d.book && r >= 340 && L <= 4) {
          T4.turns++;
          for (const s of ctx.vis) {
            if (cheb(s.head, d.body[0]) > 2) continue;
            const bar = Math.max(6, 2 * L);
            if (s.nVis < s.len) T4.hidden++;
            const botPass = (V === 'px8' ? s.lenBot : s.nVis) >= bar, visPass = s.nVis >= bar, truePass = s.len >= bar;
            if (botPass && !visPass) T4.flip++;
            if (truePass && !botPass) T4.miss++;
          }
        }
        // T5 trapped
        if (ctx.free === 0 && L >= 5) {
          T5.turns++; if (ctx.enemyAdj) T5.enemyAdj++;
          const kg = kingOf(d.team); if (kg && kg.id === d.id) T5.turnsKing++;
          const tail = d.body[L - 1]; let tailFree = false;
          for (let k = 0; k < 4; k++) { const u = nb[tail * 4 + k]; if (u >= 0 && occ[u] === -1) tailFree = true; }
          const canStub = ctx.units < UNIT_LIMIT && L - 2 >= 2 && tailFree;
          if (canStub) T5.canStub++; else if (ctx.units >= UNIT_LIMIT) T5.capBlocked++;
          ctx.t5 = { enemyAdj: ctx.enemyAdj };
        }
        // T6 portal options
        {
          const cls = L >= 8 ? 'big' : L >= 5 ? 'mid' : 'small';
          T6[cls].turns++;
          let opt = false, blind = false;
          for (const k of ctx.freeDirs) if (portalEdge[d.body[0] * 4 + k]) { opt = true; const u = nb[d.body[0] * 4 + k]; if (cheb(u, d.body[0]) > 3) blind = true; }
          if (opt) { T6[cls].opt++; if (cls === 'big' && blind) T6.big.blind++; ctx.t6 = { cls, blind }; }
        }
        // pressure on our king
        if (r >= 300) {
          const kg = kingOf(d.team);
          if (kg && kg.id === d.id && L >= 8) {
            K.kingTurnsLate++; K.enemyNear += ctx.enemyVis; if (ctx.enemyNear2) K.enemyNear2++;
            let fd = 0; for (const o of drag.values()) if (o.team === d.team && o.id !== d.id && o.body.length <= 4 && cheb(o.body[0], d.body[0]) <= 3) fd++;
            K.feeders += fd; ctx.kingThreat = ctx.enemyVis > 0; if (ctx.kingThreat) K.turnsThreat++; else K.turnsSafe++;
          } else if (kg && kg.id !== d.id && kg.body.length >= 8 && r >= 340) {
            const md = man(kg.body[0], d.body[0]); KD[md <= 3 ? 0 : md <= 8 ? 1 : md <= 16 ? 2 : 3]++;
          }
        }
        break;
      }
      case 'tileChange': {
        const k = tileOf(e.tile);
        if (e.hasPearl) { if (dropCtx >= 0) { pearl[k] = dropCtx; deaths[dropCtx].got++; } else pearl[k] = -3; }
        break;
      }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action; d.act = a ? a.kind : null;
        if (d.free < 0 || !d.ctx) d.free = freeDirs(d).length;
        const mine = d.team === US && round >= 0;
        if (mine && d.ctx) {
          const ctx = d.ctx;
          if (ctx.t5) {
            if (a && a.kind === 'split') { T5.stub++; if (ctx.t5.enemyAdj) T5.stubEnemyAdj++; }
            else if (a && a.kind === 'move' && a.steps.length) { const u = nb[d.body[0] * 4 + DIRS.indexOf(a.steps[0])]; const o = u >= 0 && occ[u] !== -1 ? drag.get(occ[u]) : null; if (o && o.team !== d.team && o.body[0] === u) { T5.ram++; if (ctx.t5.enemyAdj) T5.ramEnemyAdj++; } else T5.die++; }
            else T5.die++;
          }
          if (ctx.t6 && a && a.kind === 'move' && a.steps.length) {
            const k0 = DIRS.indexOf(a.steps[0]);
            if (portalEdge[d.body[0] * 4 + k0] && ctx.freeDirs.includes(k0)) { T6[ctx.t6.cls].took++; if (ctx.t6.cls === 'big' && ctx.t6.blind) T6.big.tookBlind++; }
          }
        }
        if (!a || a.kind !== 'move') break;
        d.steps = a.steps.length;
        clrOcc(d);
        const body = d.body.slice(); let fate = null;
        for (let i = 0; i < a.steps.length; i++) {
          if (i > 0 && body.length <= 2) { fate = { reason: 'A', step: i, why: 'sprint' }; break; }
          const h = body[0], di = DIRS.indexOf(a.steps[i]), nx = nb[h * 4 + di];
          if (nx < 0) { fate = { reason: 'W', step: i }; break; }
          if (body.includes(nx)) { fate = { reason: 'S', step: i }; break; }
          const o = occ[nx];
          if (o !== -1) { const od = drag.get(o); fate = { reason: od.body[0] === nx ? 'H' : 'O', step: i, hit: o, hitTeam: od.team, hitLen: od.body.length }; break; }
          if (portalEdge[h * 4 + di]) { d.lastPortalR = round; if (mine) { T6.crossAll++; if (body.length >= 8) T6.crossBig++; } }
          const lenBefore = body.length;
          body.unshift(nx);
          if (pearl[nx] !== -1) { if (d.team === US) eatenUs++; else eatenThem++; onEat(d, nx, lenBefore); } else body.pop();
          if (i > 0) { body.pop(); if (d.team === US) paidUs++; else paidThem++; }
          d.expect.push({ h: body[0], t: body[body.length - 1] });
        }
        d.fate = fate; d.body = body; setOcc(d);
        if (body.length > d.maxLen) d.maxLen = body.length;
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id); if (!d) break;
        if (e.facing) d.facing = DIRS.indexOf(e.facing);
        if (round < 0) break;
        const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        const eh = tileOf(e.head), et = tileOf(e.tail);
        if (x.h !== eh || x.t !== et) {
          chk.updates++;
          clrOcc(d); const b = d.body.slice(); if (b[0] !== eh) b.unshift(eh);
          while (b.length > 1 && b[b.length - 1] !== et) b.pop();
          d.body = b; d.expect = []; setOcc(d);
        }
        break;
      }
      case 'sonarPing': {
        const s = drag.get(e.senderId); if (!s || s.team !== US) break;
        const hk = e.hitKind || 'none', r = round;
        const bucket = r >= 300 ? SON.sentLate : SON.sentEarly;
        const et = e.end ? tileOf(e.end) : -1, rid = et >= 0 ? occ[et] : -1;
        let kind = hk === 'ally' || hk === 'allyHead' ? (rid === s.id ? 'self' : 'ally') : hk === 'enemy' || hk === 'enemyHead' ? 'enemy' : hk === 'kelp' ? 'kelp' : 'none';
        bucket[kind] = (bucket[kind] || 0) + 1;
        if ((hk === 'ally' || hk === 'allyHead') && rid >= 0) {
          const rcv = drag.get(rid);
          if (rcv && rcv.team === US && rcv.book) { rcv.inbox.push(e.value64); if (rid !== s.id) { SON.delivered++; if (r >= 300) SON.deliveredLate++; } }
        }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        const lenBefore = p.body.length, cl = e.childBody.length;
        if (lenBefore !== e.parentBody.length + cl) chk.splits++;
        const side = p.team === US ? 'us' : 'them';
        if (round >= 0) splitsW[side][win(round)]++;
        if (side === 'us') {
          const stub = lenBefore >= 5 && e.parentBody.length === 2;   // px STUB_KEEP 2 (normal splits keep >= 3 from length 5)
          if (stub) { stubs.us++; if (lenBefore >= 8) { stubs.usBig++; if (round >= 250) stubs.usBigLate++; } if (p.ctx && p.ctx.free === 0) stubs.usTrapped++; }
        }
        clrOcc(p); p.body = e.parentBody.map(tileOf); setOcc(p);
        const c = mk(e.childId, e.team, e.childBody.map(tileOf), DIRS.indexOf(e.childFacing), round, p.id);
        c.lastPortalR = -99;
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        const side = d.team === US ? 'us' : 'them', mover = cur === d.id, len = d.body.length, h = d.body[0];
        let c, m = null;
        if (mover) {
          const f = d.fate;
          if (e.reason === 'H') c = f && f.hitTeam !== d.team ? 'ram' : 'allyHead';
          else if (e.reason === 'O') c = f && f.hitTeam !== d.team ? 'enemyBody' : (d.free === 0 ? 'trapped' : 'volAlly');
          else if (e.reason === 'A' && f && f.why === 'sprint') c = 'sprintCost';
          else if (d.free === 0) c = 'trapped';
          else c = f && f.step > 0 ? 'sprintWS' : 'vol';
          if (e.reason === 'A') { if (f && f.reason !== 'A') chk.deaths++; }
          else if (!f || f.reason !== e.reason) chk.deaths++;
        } else {
          m = drag.get(cur);
          c = e.reason === 'H' && m && m.team !== d.team ? 'rammed' : e.reason === 'H' && m ? 'allyHead' : 'other';
          if (e.reason !== 'H' || !m || !m.fate || m.fate.hit !== d.id) chk.deaths++;
        }
        const kg = (() => { let b = null; for (const o of drag.values()) if (o.team === d.team && o.id !== d.id && (!b || o.body.length > b.body.length || (o.body.length === b.body.length && o.id < b.id))) b = o; return b; })();
        const isKing = !kg || len >= kg.body.length;
        const vol = c === 'vol' || c === 'volAlly';
        const rec = { side, r: round, id: d.id, len, c, vol, got: 0, fates: [], kingId: kg ? kg.id : -1, kingLen: kg ? kg.body.length : 0, distKing: kg ? cheb(h, kg.body[0]) : -1, recvId: -1,
          eVis: d.ctx ? d.ctx.enemyVis : -1, kingEVis: kg ? (() => { let c0 = 0; for (const o of drag.values()) if (o.team !== d.team && cheb(o.body[0], kg.body[0]) <= 3) c0++; return c0; })() : -1 };
        if (side === 'us' && vol && d.ctx) {   // receiver: the longest visible bigger ally head within Chebyshev 2
          let best = null; for (const s of d.ctx.vis) if (s.len > len && cheb(s.head, h) <= 2 && (!best || s.len > best.len)) best = s;
          if (best) { rec.recvId = best.id; rec.recvLen = best.len; rec.recvFront = !behind(best.head, best.hdir, h) ? 1 : 0; }
          if (d.ctx.t1) { T1.deaths++; if (d.ctx.t1.front) T1.frontDeaths++; if (d.ctx.t1.near) T1.nearDeaths++; }
        }
        deaths.push(rec);
        addCause(side, c, len, round);
        if (side === 'us') {
          deathLenUs += len;
          const o = { r: round, len, c, king: isKing && len >= 8 ? 1 : 0, dk: rec.distKing, portal: round - d.lastPortalR <= 3 ? 1 : 0, eVis: d.ctx ? d.ctx.enemyVis : -1 };
          if (m) { o.byLen = m.body.length; o.bySteps = m.steps; o.byBornSplit = m.parent >= 0 ? 1 : 0; }
          if (len >= 6 || o.king) ourDeaths.push(o);
          if (len >= 8 && (c === 'allyHead' || c === 'volAlly')) { T6.bigAllyDeaths++; if (o.portal) T6.bigAllyDeathsAfterPortal++; }
        } else deathLenThem += len;
        clrOcc(d); drag.delete(e.id);
        dropCtx = deaths.length - 1;
        break;
      }
      default: break;
    }
  }
  const rounds = round + 1;
  while (TL.us.length < 50) snap();           // after the end: repeat the final state (indices up to 49 = r490)
  snap();                                     // index 50 = final state
  // checks
  const res = R.result, rU = res['team' + US], rT = res['team' + THEM];
  const fin = TL.us[50], finT = TL.them[50];
  if (fin[0] !== rU.dragonCount || fin[1] !== rU.totalLength || fin[2] !== rU.longestDragon || finT[0] !== rT.dragonCount || finT[1] !== rT.totalLength || finT[2] !== rT.longestDragon) chk.final = 0;
  if (initTotal.us + eatenUs - paidUs - deathLenUs !== fin[1] || initTotal.them + eatenThem - paidThem - deathLenThem !== finT[1]) chk.massOk = 0;

  // sacrifice fates: our voluntary deaths from r300 by Chebyshev distance to the king
  const BINS = [[0, 1], [2, 2], [3, 4], [5, 8], [9, 999]];
  const sac = BINS.map(() => ({ n: 0, drop: 0, king20: 0, longest20: 0, own20: 0, enemy20: 0, recv20: 0 }));
  const sacLate = { n: 0, drop: 0, king20: 0, own20: 0, enemy20: 0, recv: 0, recvFront: 0, recv20: 0 };
  // sacrifices within Chebyshev 4 of the king from r300, split by enemy heads in the king's 7x7 at the death
  const sacNear = { calm: { n: 0, drop: 0, king20: 0 }, threat: { n: 0, drop: 0, king20: 0 } };
  for (const D of deaths) {
    if (D.side !== 'us' || !D.vol || D.r < 300) continue;
    const bi = D.distKing < 0 ? 4 : BINS.findIndex(([a, b]) => D.distKing >= a && D.distKing <= b);
    const S = sac[bi]; S.n++; S.drop += D.got; sacLate.n++; sacLate.drop += D.got;
    if (D.recvId >= 0) { sacLate.recv++; if (D.recvFront) sacLate.recvFront++; }
    if (D.distKing >= 0 && D.distKing <= 4 && D.kingLen >= 8) { const Q = sacNear[D.kingEVis > 0 ? 'threat' : 'calm']; Q.n++; Q.drop += D.got; for (const f of D.fates) if (f[0] <= 20 && f[1] === 0 && f[4]) Q.king20++; }
    for (const f of D.fates) {
      if (f[0] > 20) continue;
      if (f[1] === 0) { S.own20++; sacLate.own20++; if (f[4]) { S.king20++; sacLate.king20++; } if (f[3]) S.longest20++; if (f[5]) { S.recv20++; sacLate.recv20++; } }
      else { S.enemy20++; sacLate.enemy20++; }
    }
  }
  return { rounds, nInit, tl: TL, cause, causeW, causeLen, ourDeaths, splitsW, natW, eatW, stubs, kingEat, kingEatW, T1, T23, T4, T5, T6, K, KD, SON, sac, sacLate, sacNear, chk };
}

// ---------------------------------------------------------------------------------------------------------------
function listOnline(set) {
  const dir = path.join(ROOT, 'data', 'online', set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  const out = [];
  for (const g of idx.games || idx) {
    if (g.ourWin === null || g.ourWin === undefined) continue;
    const gj = JSON.parse(fs.readFileSync(path.join(dir, `game-${g.gameId}.json`), 'utf8'));
    const us = String(g.ourSide).toUpperCase(), them = us === 'A' ? 'B' : 'A';
    if (gj['team' + us + 'Id'] !== OWN_TEAM) throw Error(`${set} ${g.gameId}: side ${us} is not ${OWN_TEAM}`);
    const res = gj.replay.result;
    out.push({ src: 'online', set, id: String(g.gameId), file: path.join(dir, `M${g.gameId}.replay`), ourSide: us, map: g.mapName, opp: String(g.opponentTeam),
      oppName: gj['team' + them + 'Name'], win: g.ourWin ? 1 : 0, G: res['team' + us].dragonCount > 0 ? res['team' + us].longestDragon : 0,
      theirLongest: res['team' + them].longestDragon, endReason: res.endReason, variant: variantOf(set) });
  }
  return out;
}
function listLocal(label) {
  const dir = path.join(ROOT, 'exp', label), seen = new Set(), out = [];
  for (const l of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue; const r = JSON.parse(l); if (r.G === undefined || seen.has(r.key)) continue; seen.add(r.key);
    const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
    out.push({ src: 'local', set: label, id: r.key, file, ourSide: r.side, map: MAP_NAME[r.map] || r.map, opp: r.opp, oppName: r.opp, seed: r.seed,
      win: r.won ? 1 : 0, G: r.G, theirLongest: r.theirLongest, endReason: r.endReason, variant: variantOf(label) });
  }
  return out;
}

async function runWorkers(tasks, jobs, onRec) {
  let next = 0, done = 0; const errors = [];
  await new Promise((resolve, reject) => {
    const nw = Math.min(jobs, tasks.length); let live = nw; if (!nw) return resolve();
    for (let k = 0; k < nw; k++) {
      const w = cp.fork(__filename, ['--px8-child'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
      let finished = false;
      const feed = () => { if (next >= tasks.length) { finished = true; w.send('exit'); if (--live === 0) resolve(); return; } const i = next++; w.send({ i, task: tasks[i] }); };
      w.on('message', m => { if (m.error) errors.push(tasks[m.i].set + ' ' + tasks[m.i].id + ' ' + m.error); else onRec(m.rec); if (++done % 50 === 0) process.stderr.write(`${done}/${tasks.length} `); feed(); });
      w.on('error', reject);
      w.on('exit', code => { if (!finished) reject(Error('child exited with code ' + code)); });
      feed();
    }
  });
  process.stderr.write('\n');
  if (errors.length) { console.error(errors.join('\n')); throw Error(errors.length + ' games failed'); }
}

if (CHILD) {
  const load = TF.makeLoader(TF.viewerSource());
  process.on('message', m => {
    if (m === 'exit') { process.exit(0); return; }
    try {
      const R = load(m.task.file), t = m.task;
      const a = analyse(R, t);
      const mapKey = t.map === 'Prisoners Dilemma' ? 'PD' + a.nInit : t.map;
      process.send({ i: m.i, rec: { ...t, file: undefined, mapKey, type: ELIM_MAPS.includes(t.map) ? 'elim' : 'r500', ...a } });
    } catch (err) { process.send({ i: m.i, error: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | ') }); }
  });
}

async function main() {
  const argv = process.argv.slice(2);
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const online = opt('online', 'base-px8-online,px-king-v2-online').split(',').filter(Boolean);
  const local = opt('local', '').split(',').filter(Boolean);
  const jobs = Math.min(3, Math.max(1, +opt('jobs', 3)));
  const out = path.resolve(ROOT, opt('out', '.cache/online-analysis/px8_study.jsonl'));
  let tasks = [...online.flatMap(listOnline), ...local.flatMap(listLocal)];
  if (opt('limit', null)) tasks = tasks.slice(0, +opt('limit'));
  fs.mkdirSync(path.dirname(out), { recursive: true });
  process.stderr.write(`px8_study: ${tasks.length} games (${[...online, ...local].join(', ')}) with ${jobs} workers -> ${out}\n`);
  const t0 = Date.now(), recs = [];
  await runWorkers(tasks, jobs, r => recs.push(r));
  recs.sort((p, q) => p.set.localeCompare(q.set) || p.id.localeCompare(q.id));
  fs.writeFileSync(out, recs.map(r => JSON.stringify(r)).join('\n') + '\n');
  const c = { games: recs.length, updates: 0, deaths: 0, splits: 0, finalBad: 0, massBad: 0 };
  for (const r of recs) { c.updates += r.chk.updates; c.deaths += r.chk.deaths; c.splits += r.chk.splits; if (!r.chk.final) c.finalBad++; if (!r.chk.massOk) c.massBad++; }
  console.log(JSON.stringify(c));
  process.stderr.write(`done in ${((Date.now() - t0) / 1000).toFixed(1)}s\n`);
}
if (!CHILD && require.main === module) main().catch(err => { console.error(err); process.exit(1); });
module.exports = { analyse, decodePx, mix32 };
