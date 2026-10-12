#!/usr/bin/env node
'use strict';
// escape_study.js — mechanism metrics for the escape-split loop (cand-escape1).
// usage: node exp/cand-escape1/escape_study.js --eval exp/<label> [--maps autarky,prisoners_dilemma] [--out f.json] [--trace <key>]
//   Reads exp/<label>/rows.jsonl and exp/<label>/games/<key>/game.replay (tools/eval.js layout). Replays every step with
//   the rules in rules/execution-order.md (same simulation as tools/top_features.js extract) and records, for our team:
//   - splits by the indicator printed in the same turn: escape ("escape-split"), policy ("split"), other prefixes as is
//   - pearls eaten by origin: natural (initial + spawn tick) or corpse (dropped by a death, the tileChange events that
//     directly follow a dragonDeath)
//   - the start lineage: our longest initial dragon; at each of its splits the lineage follows the longer piece
//     (the child on a tie, as the child holds the old tail). Length every round (state before the round), death round.
//   - corridor exit: first round the lineage head stands >= 2 tiles off the line of the start body (only when the
//     start body is a straight line; autarky x=18, prisoners_dilemma x=14 for team A)
//   - loops: escape-split chains (a child of an escape split that escape-splits again), chain length >= 5 = loop
//   With --trace <key> it prints the lineage per round for that game.
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const evalDir = path.resolve(ROOT, opt('eval', ''));
const mapsOpt = opt('maps', null), outFile = opt('out', null), traceKey = opt('trace', null);
const DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 };
const CHECK_ROUNDS = [0, 10, 25, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500];

function study(R, side, wantTrace) {
  const M = R.match.map, W = M.width, H = M.height;
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
  const drag = new Map(), occ = new Map();
  const setOcc = d => { for (const s of d.body) occ.set(key(s.x, s.y), d.id); };
  const clrOcc = d => { for (const s of d.body) if (occ.get(key(s.x, s.y)) === d.id) occ.delete(key(s.x, s.y)); };
  const pearls = new Map(); // tile -> 'nat' | 'corpse'
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearls.set(i, 'nat');
  for (const d0 of M.initialDragons) { const o = { id: d0.id, team: d0.team, body: d0.body.map(s => ({ x: s.x, y: s.y })), born: 0, esc: 0 }; drag.set(o.id, o); setOcc(o); }
  // start lineage: our longest initial dragon (lowest id on a tie)
  const ours = M.initialDragons.filter(d => d.team === side);
  let startId = ours[0].id; for (const d of ours) if (d.body.length > drag.get(startId).body.length) startId = d.id;
  const start = drag.get(startId), startLen = start.body.length;
  let lineX = null, lineY = null;
  if (start.body.every(s => s.x === start.body[0].x)) lineX = start.body[0].x;
  else if (start.body.every(s => s.y === start.body[0].y)) lineY = start.body[0].y;
  const offLine = h => lineX !== null ? Math.min(Math.abs(h.x - lineX), W - Math.abs(h.x - lineX)) >= 2 : lineY !== null ? Math.min(Math.abs(h.y - lineY), H - Math.abs(h.y - lineY)) >= 2 : false;
  // our corridor fountains: tiles with max spawn gap <= 5 next to (or on) the start line (autarky, prisoners_dilemma pockets)
  const fountain = new Set();
  if (M.pearlRespawn && (lineX !== null || lineY !== null)) for (let t = 0; t < W * H; t++) {
    const pr = M.pearlRespawn[t]; if (!pr || pr.maxRounds < 1 || pr.maxRounds > 5) continue;
    const x = t % W, y = Math.floor(t / W);
    const off = lineX !== null ? Math.min(Math.abs(x - lineX), W - Math.abs(x - lineX)) : Math.min(Math.abs(y - lineY), H - Math.abs(y - lineY));
    if (off <= 1) fountain.add(t);
  }
  const g = {
    startLen, escapeSplits: 0, policySplits: 0, otherSplits: {}, splits: 0, linSplits: 0, linEscapeSplits: 0,
    eatNat: 0, eatCorpse: 0, eatNatLin: 0, deaths: 0, deathLen: 0, stubDeaths: 0,
    fountains: fountain.size, eatNatFountain: 0, eatCorpseFountain: 0, fountainSpawns: 0, oppEatFountain: 0,
    linLen: {}, linMaxBy: {}, linDeathRound: null, linDeathReason: null, exitRound: null, loops: 0, loopSplits: 0, maxChain: 0,
    lastEscapeRound: null, rounds: 0, linEnd: 0, splitRounds: [],
  };
  let lin = startId, linMax = startLen, round = -1, cur = -1, curText = '', drop = null;
  const trace = [];
  const chain = new Map(); // dragon id -> escape chain length it belongs to (child of an escape split)
  const linLenNow = () => { const d = drag.get(lin); return d ? d.body.length : 0; };
  for (const e of R.events) {
    if (drop && !(e.type === 'tileChange' && e.hasPearl)) drop = null;
    switch (e.type) {
      case 'roundStart': {
        round = e.round; g.rounds = round + 1;
        const L = linLenNow(); if (L > linMax) linMax = L;
        if (CHECK_ROUNDS.includes(round)) { g.linLen[round] = L; g.linMaxBy[round] = linMax; }
        if (wantTrace) { const d = drag.get(lin); trace.push(`r${round} lin#${lin} L${L}` + (d ? ` head ${d.body[0].x},${d.body[0].y} tail ${d.body[d.body.length - 1].x},${d.body[d.body.length - 1].y}` : ' dead')); }
        break;
      }
      case 'turnStart': cur = e.id; curText = ''; break;
      case 'dragonIndicator': if (e.id === cur) curText = e.text || ''; break;
      case 'tileChange': {
        const k = key(e.tile.x, e.tile.y);
        if (e.hasPearl) { pearls.set(k, drop ? 'corpse' : 'nat'); if (!drop && round >= 0 && fountain.has(k)) g.fountainSpawns++; }
        else pearls.delete(k);
        break;
      }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action; if (!a || a.kind !== 'move') break;
        clrOcc(d);
        const body = d.body.slice();
        d.expect = [];
        for (let i = 0; i < a.steps.length; i++) {
          if (i > 0 && body.length <= 2) break;
          const h = body[0], nx = across(h.x, h.y, a.steps[i]);
          if (!nx) break;
          if (body.some(s => s.x === nx.x && s.y === nx.y)) break;
          if (occ.get(key(nx.x, nx.y)) !== undefined) break;
          body.unshift(nx);
          const k = key(nx.x, nx.y);
          if (pearls.has(k)) {
            const o = pearls.get(k); pearls.delete(k);
            if (d.team === side) {
              if (o === 'nat') { g.eatNat++; if (d.id === lin) g.eatNatLin++; if (fountain.has(k)) g.eatNatFountain++; }
              else { g.eatCorpse++; if (fountain.has(k)) g.eatCorpseFountain++; }
            } else if (fountain.has(k)) g.oppEatFountain++;
          } else body.pop();
          if (i > 0) body.pop();
          d.expect.push({ h: body[0], t: body[body.length - 1] });
        }
        d.body = body; setOcc(d);
        if (d.id === lin && g.exitRound === null && offLine(body[0])) g.exitRound = round;
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id); if (!d || round < 0) break;
        const x = d.expect && d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        if (x.h.x !== e.head.x || x.h.y !== e.head.y || x.t.x !== e.tail.x || x.t.y !== e.tail.y) {
          clrOcc(d); const b = d.body.slice();
          if (b[0].x !== e.head.x || b[0].y !== e.head.y) b.unshift({ x: e.head.x, y: e.head.y });
          while (b.length > 1 && (b[b.length - 1].x !== e.tail.x || b[b.length - 1].y !== e.tail.y)) b.pop();
          d.body = b; d.expect = []; setOcc(d); g.simMismatch = (g.simMismatch || 0) + 1;
        }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        clrOcc(p); p.body = e.parentBody.map(s => ({ x: s.x, y: s.y })); setOcc(p);
        const c = { id: e.childId, team: e.team, body: e.childBody.map(s => ({ x: s.x, y: s.y })), born: round };
        drag.set(c.id, c); setOcc(c);
        if (e.team !== side) break;
        g.splits++;
        const text = e.parentId === cur ? curText : '';
        const isEsc = text.startsWith('escape-split'), isPol = /^split\d/.test(text);
        if (isEsc) g.escapeSplits++; else if (isPol) g.policySplits++;
        else { const k = (text.match(/^[a-z-]+/) || ['?'])[0]; g.otherSplits[k] = (g.otherSplits[k] || 0) + 1; }
        g.splitRounds.push([round, e.parentBody.length + e.childBody.length, e.childBody.length, isEsc ? 'E' : isPol ? 'P' : text.split(' ')[0]]);
        if (isEsc) {
          g.lastEscapeRound = round;
          const ch = (chain.get(e.parentId) || 0) + 1; chain.set(e.childId, ch);
          if (ch > g.maxChain) g.maxChain = ch;
          if (ch === 5) { g.loops++; g.loopSplits += 5; } else if (ch > 5) g.loopSplits++;
        }
        if (e.parentId === lin) {
          g.linSplits++; if (isEsc) g.linEscapeSplits++;
          if (e.childBody.length >= e.parentBody.length) lin = e.childId;
          if (g.exitRound === null) { const d = drag.get(lin); if (offLine(d.body[0])) g.exitRound = round; }
        }
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        if (d.team === side) { g.deaths++; g.deathLen += d.body.length; if (d.body.length <= 3 && d.born === round - 1 || d.body.length <= 3 && round - d.born <= 3 && d.born > 0) g.stubDeaths++; }
        if (e.id === lin) { g.linDeathRound = round; g.linDeathReason = e.reason; g.linDeathLen = d.body.length; }
        clrOcc(d); drag.delete(e.id);
        drop = true;
        break;
      }
    }
  }
  const L = linLenNow(); if (L > linMax) linMax = L;
  g.linLen[500] = L; g.linMaxBy[500] = linMax; g.linEnd = L;
  for (const r of CHECK_ROUNDS) if (g.linLen[r] === undefined) { g.linLen[r] = r >= g.rounds ? L : 0; g.linMaxBy[r] = linMax; }
  g.lineShape = lineX !== null ? 'x=' + lineX : lineY !== null ? 'y=' + lineY : null;
  if (!g.lineShape) g.exitRound = null;
  if (wantTrace) g.trace = trace;
  return g;
}

function rowsOf(dir) {
  const seen = new Set();
  return fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined && !seen.has(r.key) && seen.add(r.key));
}

if (require.main === module && opt('replay', null)) {
  // one replay file: --replay <file> --side A|B, prints the lineage trace and the game record
  const g = study(load(path.resolve(opt('replay'))), opt('side', 'A'), true);
  console.log(g.trace.join('\n')); delete g.trace; console.log(JSON.stringify(g));
} else if (require.main === module) {
  const rows = rowsOf(evalDir).filter(r => !mapsOpt || mapsOpt.split(',').includes(r.map));
  const games = [];
  for (const r of rows) {
    if (traceKey && r.key !== traceKey) continue;
    const f = path.join(evalDir, 'games', r.key.replace(/:/g, '_'), 'game.replay');
    if (!fs.existsSync(f)) continue;
    const g = study(load(f), r.side, !!traceKey);
    games.push({ key: r.key, opp: r.opp, map: r.map, side: r.side, seed: r.seed, G: r.G, won: r.won, alive: r.alive, total: r.total, ...g });
  }
  if (traceKey) { const g = games[0]; console.log(g.trace.join('\n')); delete g.trace; console.log(JSON.stringify(g)); process.exit(0); }
  const res = { eval: path.relative(ROOT, evalDir), n: games.length, games };
  if (outFile) fs.writeFileSync(outFile, JSON.stringify(res));
  const by = {};
  for (const g of games) (by[g.map] = by[g.map] || []).push(g);
  const mean = a => a.reduce((s, x) => s + x, 0) / Math.max(1, a.length);
  console.log('map | n | escape splits | policy splits | natural eaten | lineage escape splits | exit round (median, never) | lin L r100/r200/r300/r500 | G');
  for (const [m, gs] of Object.entries(by).sort()) {
    const ex = gs.map(g => g.exitRound).filter(x => x !== null).sort((a, b) => a - b);
    console.log([m, gs.length, mean(gs.map(g => g.escapeSplits)).toFixed(1), mean(gs.map(g => g.policySplits)).toFixed(1), mean(gs.map(g => g.eatNat)).toFixed(1), mean(gs.map(g => g.linEscapeSplits)).toFixed(1),
      (ex.length ? ex[Math.floor(ex.length / 2)] : '-') + ', ' + (gs.length - ex.length), [100, 200, 300, 500].map(r => mean(gs.map(g => g.linLen[r])).toFixed(1)).join('/'), mean(gs.map(g => g.G)).toFixed(1)].join(' | '));
  }
}
module.exports = { study, rowsOf };
