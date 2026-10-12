#!/usr/bin/env node
'use strict';
// ram_audit.js — why do our long dragons get rammed head-on? (candidate cand-avoid1, 2026-09-29)
// Reads replays only (runs no games). For every death of one of our dragons of length >= 6 where an enemy moved its
// head into ours ("rammed"), it rebuilds the board at OUR LAST DECISION and asks:
//   - how long was the attacker, how many steps did it take, was it inside our 7x7 window at our decision,
//   - which of our legal actions (1, 2 or 3 steps) would have ended outside the reach of every visible enemy head
//     (reach of an enemy of length Le = Le - 1 steps; tails of other dragons count as free, our new body blocks),
//   - would the bot's own threat model (plan.cpp computeEnemyDistance + threatAt) flag the tile we chose,
//   - what mode the bot was in (indicator text: feed, gather goal, escape-split, TRADE, late) and whether we ate a pearl.
// It also counts, per game, deaths of our L>=6 dragons by cause and pearls eaten (side-effect metrics).
//
// usage:
//   node exp/cand-avoid1/ram_audit.js --local exp/eval-r1 [--filter archetype_hunter] [--out file.json] [--cases]
//   node exp/cand-avoid1/ram_audit.js --online data/online/r1-online [--own 583] [--out file.json]
//   (several --local/--online may be given; --report prints the markdown tables from --in file.json instead)
// Body reconstruction follows tools/top_features.js extract() (validated there against dragonUpdate); this script checks
// its own reconstruction too (meta.mismatch = head/tail disagreements, deathMismatch = death causes it cannot reproduce).
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));

const DIRS = ['N', 'E', 'S', 'W'], DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 };
const BIG = 6, SNAP_MIN = 5;

// ---------------------------------------------------------------------------------------------------------------
function geometry(M) {
  const W = M.width, H = M.height;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
  const portal = new Map();
  for (const pr of M.portals || []) { if (pr.length !== 2) continue; const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); }
  const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
  const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
  const isPortal = new Uint8Array(W * H * 4);
  // across(k, d) -> tile key or -1 (kelp). Same rule as tools/top_features.js.
  const cache = new Int32Array(W * H * 4).fill(-2);
  function across(k, di) {
    const c = cache[k * 4 + di]; if (c !== -2) return c;
    const x = k % W, y = (k / W) | 0, d = DIRS[di];
    let ek, kelp;
    if (d === 'N') { ek = x + ',' + y + ',N'; kelp = hk(x, y); }
    else if (d === 'S') { ek = x + ',' + wy(y + 1) + ',N'; kelp = hk(x, y + 1); }
    else if (d === 'W') { ek = x + ',' + y + ',W'; kelp = vk(x, y); }
    else { ek = wx(x + 1) + ',' + y + ',W'; kelp = vk(x + 1, y); }
    const p = portal.get(ek);
    let r;
    if (p) {
      isPortal[k * 4 + di] = 1;
      if (d === 'N') r = wy(p.y - 1) * W + p.x; else if (d === 'S') r = p.y * W + p.x;
      else if (d === 'W') r = p.y * W + wx(p.x - 1); else r = p.y * W + p.x;
    } else if (kelp) r = -1;
    else r = wy(y + DY[d]) * W + wx(x + DX[d]);
    cache[k * 4 + di] = r; return r;
  }
  const cheb = (a, b) => { let dx = Math.abs(a % W - b % W), dy = Math.abs(((a / W) | 0) - ((b / W) | 0)); dx = Math.min(dx, W - dx); dy = Math.min(dy, H - dy); return Math.max(dx, dy); };
  return { W, H, across, cheb, isPortal, key: (x, y) => wy(y) * W + wx(x) };
}

// BFS path distance from src to target over passable tiles, up to maxD. passable(k) excludes target handling.
function bfsDist(G, src, target, maxD, blocked) {
  if (src === target) return 0;
  const seen = new Map([[src, 0]]); let q = [src];
  for (let d = 1; d <= maxD; d++) {
    const nq = [];
    for (const t of q) for (let di = 0; di < 4; di++) {
      const u = G.across(t, di); if (u < 0 || seen.has(u)) continue;
      if (u === target) return d;
      if (blocked(u)) continue;
      seen.set(u, d); nq.push(u);
    }
    q = nq; if (!q.length) break;
  }
  return Infinity;
}

// ---------------------------------------------------------------------------------------------------------------
// Exposure at one decision of a long dragon: does the chosen move end inside the true reach of a visible SHORTER enemy
// head, and how many single steps would not have? (Same board rules as analyse().)
function exposureAt(S, G, us) {
  const myHead = S.body[0], L = S.body.length;
  const vis = S.others.filter(o => o.team !== us && o.body.length < L && G.cheb(myHead, o.body[0]) <= 3);
  if (!vis.length) return null;
  const occ = new Map();
  for (const o of S.others) o.body.forEach((k, i) => occ.set(k, { id: o.id, tail: i === o.body.length - 1 && o.body.length > 1 }));
  function sim(steps) {
    let body = S.body.slice(); const eaten = new Set();
    for (let i = 0; i < steps.length; i++) {
      if (i > 0 && body.length <= 2) return null;
      const nx = G.across(body[0], steps[i]); if (nx < 0 || body.includes(nx) || occ.has(nx)) return null;
      body.unshift(nx);
      if (S.pearls.has(nx) && !eaten.has(nx)) eaten.add(nx); else body.pop();
      if (i > 0) body.pop();
    }
    return body;
  }
  const threatened = body => { const mine = new Set(body); const blocked = u => { if (mine.has(u)) return true; const c = occ.get(u); return !!c && !c.tail; };
    return vis.some(o => bfsDist(G, o.body[0], body[0], Math.max(1, o.body.length - 1), blocked) <= Math.max(1, o.body.length - 1)); };
  const singles = [0, 1, 2, 3].map(d => sim([d])).filter(Boolean);
  const safe1 = singles.filter(b => !threatened(b)).length;
  let exposed = null;
  if (S.act.kind === 'move') { const b = sim(S.act.steps.map(x => DIRS.indexOf(x))); exposed = b ? threatened(b) : null; }
  return { exposed, safe1, n1: singles.length };
}

// ---------------------------------------------------------------------------------------------------------------
// Analysis of one rammed case at our last decision S.
function analyse(S, att, G, us) {
  const myHead = S.body[0], L = S.body.length;
  const occ = new Map();   // tile -> {id, team, head, tail}
  for (const o of S.others) o.body.forEach((k, i) => occ.set(k, { id: o.id, team: o.team, head: i === 0, tail: i === o.body.length - 1 && o.body.length > 1 }));
  const inWin = k => G.cheb(myHead, k) <= 3;
  const visEnemies = S.others.filter(o => o.team !== us && inWin(o.body[0]));
  const attS = S.others.find(o => o.id === att.id) || null;
  // simulate one of our actions (list of dirs) on the board at S; returns null if it kills us
  function sim(steps) {
    let body = S.body.slice(), ate = 0; const eaten = new Set();
    for (let i = 0; i < steps.length; i++) {
      if (i > 0 && body.length <= 2) return null;
      const nx = G.across(body[0], steps[i]); if (nx < 0) return null;
      if (body.includes(nx)) return null;
      if (occ.has(nx)) return null;           // another dragon's body or head (a head is a trade: we die too)
      body.unshift(nx);
      if (S.pearls.has(nx) && !eaten.has(nx)) { eaten.add(nx); ate++; } else body.pop();
      if (i > 0) body.pop();
    }
    return { body, head: body[0], ate, steps: steps.length };
  }
  // true reach of enemy o (length at S) to tile `target` given our new body `mine`: other dragons' tails are free
  const reachOf = o => Math.max(1, o.body.length - 1);
  function distFrom(o, target, mine) {
    const mineSet = new Set(mine);
    const blocked = u => { if (mineSet.has(u)) return true; const c = occ.get(u); if (!c) return false; if (c.id === o.id) return !c.tail; return !c.tail; };
    return bfsDist(G, o.body[0], target, reachOf(o), blocked);
  }
  const threatened = r => visEnemies.some(o => distFrom(o, r.head, r.body) <= reachOf(o));
  // candidate actions
  const cands = [];
  for (let a = 0; a < 4; a++) {
    const r1 = sim([a]); if (!r1) continue; cands.push({ dirs: [a], r: r1 });
    for (let b = 0; b < 4; b++) {
      const r2 = sim([a, b]); if (!r2) continue; cands.push({ dirs: [a, b], r: r2 });
      for (let c = 0; c < 4; c++) { const r3 = sim([a, b, c]); if (r3) cands.push({ dirs: [a, b, c], r: r3 }); }
    }
  }
  for (const c of cands) c.threat = threatened(c.r);
  const safe1 = cands.filter(c => c.dirs.length === 1 && !c.threat).length;
  const safe2 = cands.filter(c => c.dirs.length === 2 && !c.threat).length;
  const safe3 = cands.filter(c => c.dirs.length === 3 && !c.threat).length;
  const legal1 = cands.filter(c => c.dirs.length === 1).length;
  // what we actually did
  const act = S.act; let chosen = null;
  if (act.kind === 'move') chosen = sim(act.steps.map(s => DIRS.indexOf(s)));
  // pre-move: was our current head already inside the attacker's reach (with our current body blocking)?
  let preDist = null, postDist = null, attReach = null;
  if (attS) {
    attReach = reachOf(attS);
    preDist = distFrom(attS, myHead, S.body.slice(1));
    if (chosen) postDist = distFrom(attS, chosen.head, chosen.body);
  }
  // the bot's own view (plan.cpp): BFS from the enemy head through tiles free at S (every body blocks, our head is
  // passable), radius min(estLen-1, 4); estLen = exact if the whole enemy is in view, else max(visible, 4 if a visible
  // segment is on the window ring). History is not modelled (the bot keeps the max ever seen, so it can only be larger).
  let bot = null;
  if (attS && inWin(attS.body[0])) {
    const vis = attS.body.filter(inWin), all = vis.length === attS.body.length;
    const onRing = vis.some(k => G.cheb(myHead, k) >= 3);
    const est = all ? attS.body.length : Math.max(vis.length, onRing ? 4 : vis.length, 2);
    const rad = Math.max(1, Math.min(est - 1, 4));
    const occAll = new Set(S.body); for (const o of S.others) for (const k of o.body) occAll.add(k);
    const blocked = u => occAll.has(u) && u !== myHead;
    const dAt = t => bfsDist(G, attS.body[0], t, rad, blocked);
    let dChosen = null, flaggedAll = null;
    if (chosen && act.steps) {
      const firstT = G.across(myHead, DIRS.indexOf(act.steps[0]));
      dChosen = dAt(chosen.head);
      // single-step alternatives: how many would the bot's model flag (from this attacker)?
      let flagged = 0, n1 = 0;
      for (const c of cands) if (c.dirs.length === 1) { n1++; if (dAt(c.r.head) <= rad) flagged++; }
      flaggedAll = n1 > 0 && flagged === n1;
      bot = { est, true: attS.body.length, rad, dChosen: dChosen === Infinity ? null : dChosen, flagsChosen: dChosen <= rad, flaggedAll, firstT };
    } else bot = { est, true: attS.body.length, rad };
  }
  // class
  let cls;
  if (!attS) cls = 'newChild';
  else if (!inWin(attS.body[0])) cls = 'unseen';
  else if (safe1 + safe2 + safe3 === 0) cls = 'cornered';
  else if (safe1 === 0) cls = 'sprintOnly';
  else if (preDist > attReach) cls = 'walkedIn';
  else cls = 'stayedIn';
  const ind = S.ind || '';
  const mode = /^feed/.test(ind) ? 'feed' : /escape-split/.test(ind) ? 'escSplit' : /^split/.test(ind) ? 'split' : / TRADE/.test(ind) ? 'trade'
    : / g\d+/.test(ind) ? 'gather' : / late/.test(ind) ? 'late' : 'normal';
  const vm = /\sv(-?[\d.]+)/.exec(ind);
  return {
    cls, mode, ind, v: vm ? +vm[1] : null, ourLenDec: L, act: act.kind === 'move' ? act.steps.join('') : act.kind + (act.child || ''),
    ate: chosen ? chosen.ate : 0, attLen: att.len, attSteps: att.steps, attFromSplit: att.fromSplit, attAge: att.age,
    cheb: attS ? G.cheb(myHead, attS.body[0]) : null, preDist: preDist === Infinity ? null : preDist, postDist: postDist === Infinity ? null : postDist,
    attReach, safe1, safe2, safe3, legal1, nVis: visEnemies.length, bot, attId: att.id,
    ourId: S.id, decRound: S.round,
  };
}

// ---------------------------------------------------------------------------------------------------------------
function auditGame(file, us, info) {
  const R = load(file);
  const M = R.match.map, G = geometry(M);
  const them = us === 'A' ? 'B' : 'A';
  const drag = new Map(), occ = new Map();
  const setOcc = d => { for (const k of d.body) occ.set(k, d.id); };
  const clrOcc = d => { for (const k of d.body) if (occ.get(k) === d.id) occ.delete(k); };
  const pearls = new Set();
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearls.add(i);
  for (const d0 of M.initialDragons) { const o = { id: d0.id, team: d0.team, body: d0.body.map(s => G.key(s.x, s.y)), born: 0, fromSplit: 0, expect: [] }; drag.set(o.id, o); setOcc(o); }
  let round = -1, cur = -1, ind = null, dlog = null;
  const hist = new Map();   // our id -> last decisions [{round, ind, log, head}] (diag builds write a LOG line)
  const lastDec = new Map(), pre = new Map();
  const cases = [];
  const g = { ...info, rounds: 0, mismatch: 0, deathMismatch: 0, eaten: { us: 0, them: 0 }, bigDeaths: {}, ourDeaths: {}, rammedBig: 0, rammedBigLen: 0,
    rammedAll: 0, won: null, G: null, bigTurns: 0, bigTurnsNearSmall: 0, sprints: 0, sprintCost: 0 };
  const cause = (victim, mover, fate) => {
    // victim died: returns a cause label
    return null;
  };
  for (const e of R.events) {
    switch (e.type) {
      case 'roundStart': round = e.round; break;
      case 'turnStart': cur = e.id; ind = null; dlog = null; break;
      case 'dragonIndicator': if (e.id === cur) ind = e.text; break;
      case 'dragonLog': if (e.id === cur) dlog = e.text; break;
      case 'tileChange': {
        const k = G.key(e.tile.x, e.tile.y);
        if (e.hasPearl) pearls.add(k);
        else { pearls.delete(k); const d = drag.get(cur); if (d && round >= 0) g.eaten[d.team === us ? 'us' : 'them']++; }
        break;
      }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action || {};
        pre.set(e.id, { round, head: d.body[0], len: d.body.length, steps: a.kind === 'move' ? a.steps.length : 0, kind: a.kind });
        if (d.team === us) {
          const h = hist.get(d.id) || [], near = [];
          if (d.body.length >= SNAP_MIN) for (const o of drag.values()) if (o.team !== us && G.cheb(d.body[0], o.body[0]) <= 6) near.push([o.id, o.body[0], o.body.length]);
          const legal = [];
          if (d.body.length >= SNAP_MIN) for (let di = 0; di < 4; di++) { const u = G.across(d.body[0], di); if (u >= 0 && !occ.has(u)) legal.push([DIRS[di], u, pearls.has(u) ? 1 : 0]); }
          h.push({ round, ind, log: dlog, head: d.body[0], len: d.body.length, act: a.kind === 'move' ? a.steps.join('') : a.kind, near, legal });
          if (h.length > 6) h.shift(); hist.set(d.id, h);
        }
        if (d.team === us && d.body.length >= SNAP_MIN) {
          const others = []; for (const o of drag.values()) if (o.id !== d.id) others.push({ id: o.id, team: o.team, body: o.body.slice() });
          lastDec.set(d.id, { id: d.id, round, body: d.body.slice(), act: { kind: a.kind, steps: a.kind === 'move' ? a.steps.slice() : null, child: a.childSegmentCount }, ind, others, pearls: new Set(pearls) });
          if (d.body.length >= BIG) {
            g.bigTurns++;
            const ex = exposureAt(lastDec.get(d.id), G, us);
            if (ex) { g.bigNearShort = (g.bigNearShort || 0) + 1; if (ex.exposed) { g.exposed = (g.exposed || 0) + 1; if (ex.safe1 > 0) g.exposedAvoidable = (g.exposedAvoidable || 0) + 1; } }
            for (const o of drag.values()) if (o.team !== us && o.body.length <= 3 && G.cheb(d.body[0], o.body[0]) <= 3) { g.bigTurnsNearSmall++; break; }
          }
        } else if (d.team === us) lastDec.delete(d.id);
        if (a.kind !== 'move') { d.fate = null; break; }
        if (d.team === us && a.steps.length > 1) { g.sprints++; g.sprintCost += a.steps.length - 1; }
        clrOcc(d);
        const body = d.body.slice(); let fate = null; d.expect = [];
        for (let i = 0; i < a.steps.length; i++) {
          if (i > 0 && body.length <= 2) { fate = { reason: 'A' }; break; }
          const nx = G.across(body[0], DIRS.indexOf(a.steps[i]));
          if (nx < 0) { fate = { reason: 'W' }; break; }
          if (body.includes(nx)) { fate = { reason: 'S' }; break; }
          const o = occ.get(nx);
          if (o !== undefined) { const od = drag.get(o); fate = { reason: od.body[0] === nx ? 'H' : 'O', hit: o, hitTeam: od.team, hitLen: od.body.length }; break; }
          body.unshift(nx);
          if (pearls.has(nx)) { /* eaten: tileChange follows */ } else body.pop();
          if (i > 0) body.pop();
          d.expect.push({ h: body[0], t: body[body.length - 1] });
        }
        d.fate = fate; d.body = body; setOcc(d);
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id); if (!d || round < 0) break;
        const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        const h = G.key(e.head.x, e.head.y), t = G.key(e.tail.x, e.tail.y);
        if (x.h !== h || x.t !== t) {
          g.mismatch++;
          clrOcc(d); const b = d.body.slice();
          if (b[0] !== h) b.unshift(h);
          while (b.length > 1 && b[b.length - 1] !== t) b.pop();
          d.body = b; d.expect = []; setOcc(d);
        }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        clrOcc(p); p.body = e.parentBody.map(s => G.key(s.x, s.y)); setOcc(p);
        const c = { id: e.childId, team: e.team, body: e.childBody.map(s => G.key(s.x, s.y)), born: round, fromSplit: 1, bornLen: e.childBody.length, expect: [] };
        drag.set(c.id, c); setOcc(c);
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        const len = d.body.length, mover = drag.get(cur);
        if (d.team === us) {
          let c;
          if (cur === e.id) {
            const f = d.fate;
            if (e.reason === 'H') c = f && f.hitTeam === us ? 'H-ally' : 'H-weRam';
            else if (e.reason === 'O') c = f && f.hitTeam === us ? 'O-ally' : 'O-enemy';
            else c = e.reason;
            if (e.reason !== 'A' && (!f || f.reason !== e.reason)) g.deathMismatch++;
          } else if (e.reason === 'H' && mover) c = mover.team === us ? 'H-ally' : 'H-rammed';
          else { c = 'other'; g.deathMismatch++; }
          g.ourDeaths[c] = (g.ourDeaths[c] || 0) + 1;
          if (len >= BIG) g.bigDeaths[c] = (g.bigDeaths[c] || 0) + 1;
          if (c === 'H-rammed') {
            g.rammedAll++;
            if (len >= BIG) {
              g.rammedBig++; g.rammedBigLen += len;
              const S = lastDec.get(e.id), p = pre.get(cur);
              const att = { id: cur, len: p ? p.len : null, steps: p ? p.steps : null, fromSplit: mover.fromSplit, age: round - mover.born };
              const rec = { game: info.game, opp: info.opp, map: info.map, side: us, round, ourLen: len, W: G.W, H: G.H, finalHead: d.body[0] };
              if (S) Object.assign(rec, analyse(S, att, G, us)); else rec.cls = 'noSnapshot';
              if (hist.has(e.id)) rec.hist = hist.get(e.id).map(x => { const n = x.near.find(q => q[0] === cur);
                return { round: x.round, ind: x.ind, log: x.log, act: x.act, len: x.len, head: x.head, legal: x.legal, attHead: n ? n[1] : null, attCheb: n ? G.cheb(x.head, n[1]) : null, attLen: n ? n[2] : null, nNear: x.near.length,
                  nSmall3: x.near.filter(q => q[2] <= 4 && G.cheb(x.head, q[1]) <= 3).length }; });
              if (S && p && S.others.find(o => o.id === cur) && S.others.find(o => o.id === cur).body[0] !== p.head) rec.attMovedSinceDec = 1;
              cases.push(rec);
            }
          }
        }
        clrOcc(d); drag.delete(e.id); lastDec.delete(e.id); hist.delete(e.id);
        break;
      }
    }
  }
  g.rounds = round + 1;
  const res = R.result, mine = res['team' + us], th = res['team' + them];
  g.won = res.winner === us; g.G = mine.dragonCount > 0 ? mine.longestDragon : 0; g.alive = mine.dragonCount > 0; g.theirLongest = th.longestDragon;
  let units = 0, longest = 0; for (const d of drag.values()) if (d.team === us) { units++; longest = Math.max(longest, d.body.length); }
  g.finalCheck = units === mine.dragonCount && longest === mine.longestDragon;
  return { game: g, cases };
}

// ---------------------------------------------------------------------------------------------------------------
const LOCAL_MAPS = 'autarky|default|devil|portals|prisoners_dilemma|queen_of_spades|schooltime|slithery_fight|trauma|trophy';
function listLocal(dir, filter) {
  const root = path.join(dir, 'games'), re = new RegExp(`^(.*?)_(${LOCAL_MAPS})_([AB])_(\\d+)$`);
  return fs.readdirSync(root).sort().map(k => {
    const m = re.exec(k); const f = path.join(root, k, 'game.replay');
    if (!m || !fs.existsSync(f)) return null;
    if (filter && !new RegExp(filter).test(k)) return null;
    return { file: f, us: m[3], info: { set: path.basename(dir), game: k, opp: m[1], map: m[2], seed: +m[4], key: [m[1], m[2], m[3], m[4]].join(':') } };
  }).filter(Boolean);
}
function listOnline(dir, own) {
  return fs.readdirSync(dir).filter(f => /^game-\d+\.json$/.test(f)).sort().map(f => {
    const j = JSON.parse(fs.readFileSync(path.join(dir, f))); const id = j.id, rf = path.join(dir, `M${id}.replay`);
    if (!fs.existsSync(rf) || j.status !== 'completed') return null;
    const us = j.teamAId === own ? 'A' : j.teamBId === own ? 'B' : null; if (!us) return null;
    const oppSide = us === 'A' ? 'B' : 'A';
    return { file: rf, us, info: { set: path.basename(dir), game: String(id), opp: String(j['team' + oppSide + 'Id']), oppName: j['team' + oppSide + 'Name'], oppElo: j['team' + oppSide + 'Elo'], map: j.mapName, ranked: j.ranked, at: j.completedAt, sub: j['submission' + us + 'Id'] } };
  }).filter(Boolean);
}

function main() {
  const argv = process.argv.slice(2);
  const all = k => argv.map((a, i) => a === k ? argv[i + 1] : null).filter(Boolean);
  const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
  const own = +opt('--own', 583), filter = opt('--filter', null), out = opt('--out', null);
  const jobs = [...all('--local').flatMap(d => listLocal(path.resolve(ROOT, d), filter)), ...all('--online').flatMap(d => listOnline(path.resolve(ROOT, d), own))];
  const games = [], cases = [];
  let n = 0;
  for (const j of jobs) {
    try { const r = auditGame(j.file, j.us, j.info); games.push(r.game); cases.push(...r.cases); }
    catch (err) { console.error('error', j.file, String(err && err.stack || err).split('\n').slice(0, 3).join(' | ')); }
    if (++n % 20 === 0) process.stderr.write(n + ' ');
  }
  process.stderr.write('\n');
  const res = { at: new Date().toISOString(), games, cases };
  if (out) fs.writeFileSync(path.resolve(out), JSON.stringify(res));
  const mm = games.reduce((s, g) => s + g.mismatch, 0), dm = games.reduce((s, g) => s + g.deathMismatch, 0), fc = games.filter(g => !g.finalCheck).length;
  console.log(`games ${games.length}, rammed L>=${BIG} cases ${cases.length}, reconstruction: head/tail mismatches ${mm}, death mismatches ${dm}, final-state mismatches ${fc}`);
}
module.exports = { auditGame, listLocal, listOnline, geometry, bfsDist };
if (require.main === module) main();

// ---------------------------------------------------------------------------------------------------------------
// renderAt(file, us, ourId, rounds, radius): ASCII view of the board around our dragon `ourId` at its decisions in
// `rounds`. Tiles: H/h our head/body, 2-9 or X an enemy head (its length), e enemy body, O/o ally head/body,
// * pearl. Kelp: '|' between tiles in a row, '-' under a tile. Used for case studies only.
function renderAt(file, us, ourId, rounds, radius = 6) {
  const R = load(file), M = R.match.map, G = geometry(M), W = G.W, H = G.H;
  const hk = (x, y) => M.initialHEdges[(((y % H) + H) % H) * W + x] === 1;
  const vk = (x, y) => M.initialVEdges[y * (W + 1) + (((x % W) + W) % W)] === 1;
  const drag = new Map(); const pearls = new Set();
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearls.add(i);
  for (const d0 of M.initialDragons) drag.set(d0.id, { id: d0.id, team: d0.team, body: d0.body.map(s => G.key(s.x, s.y)) });
  let round = -1; const out = [];
  for (const e of R.events) {
    if (e.type === 'roundStart') round = e.round;
    else if (e.type === 'tileChange') { const k = G.key(e.tile.x, e.tile.y); if (e.hasPearl) pearls.add(k); else pearls.delete(k); }
    else if (e.type === 'dragonAction' && e.id === ourId && rounds.includes(round)) {
      const me = drag.get(ourId), h = me.body[0], hx = h % W, hy = (h / W) | 0;
      const cell = new Map();
      for (const d of drag.values()) d.body.forEach((k, i) => {
        let c;
        if (d.id === ourId) c = i === 0 ? 'H' : 'h';
        else if (d.team === us) c = i === 0 ? 'O' : 'o';
        else c = i === 0 ? (d.body.length <= 9 ? String(d.body.length) : 'X') : 'e';
        cell.set(k, c);
      });
      out.push(`round ${round} our #${ourId} L${me.body.length} action ${e.action.kind === 'move' ? e.action.steps.join('') : e.action.kind}`);
      for (let dy = -radius; dy <= radius; dy++) {
        let row = '', under = '';
        for (let dx = -radius; dx <= radius; dx++) {
          const x = ((hx + dx) % W + W) % W, y = ((hy + dy) % H + H) % H, k = y * W + x;
          row += cell.get(k) || (pearls.has(k) ? '*' : '.');
          row += vk(x + 1, y) ? '|' : ' ';
          under += (hk(x, y + 1) ? '-' : ' ') + ' ';
        }
        out.push('  ' + row); out.push('  ' + under);
      }
    }
    if (e.type === 'dragonUpdate') { const d = drag.get(e.id); if (d) { const hh = G.key(e.head.x, e.head.y), tt = G.key(e.tail.x, e.tail.y); if (d.body[0] !== hh) d.body.unshift(hh); while (d.body.length > 1 && d.body[d.body.length - 1] !== tt) d.body.pop(); } }
    else if (e.type === 'dragonSplit') { const p = drag.get(e.parentId); if (p) p.body = e.parentBody.map(s => G.key(s.x, s.y)); drag.set(e.childId, { id: e.childId, team: e.team, body: e.childBody.map(s => G.key(s.x, s.y)) }); }
    else if (e.type === 'dragonDeath') drag.delete(e.id);
  }
  return out.join('\n');
}
module.exports.renderAt = renderAt;
