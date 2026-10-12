#!/usr/bin/env node
'use strict';
// loop_mass.js — mass balance of the start dragon's escape-split loop (cand-escape1 report, section 3).
// usage: node exp/cand-escape1/loop_mass.js --eval exp/eval-r1 [--maps autarky,prisoners_dilemma]
//   Replays every step of our team (same rules as escape_study.js) and puts each of our dragons in a group:
//   'lin' = the start lineage (our longest initial dragon; at each of its splits the longer piece, the child on a tie),
//   'loop' = pieces the lineage left behind (the stubs), 'other' = everything else. Per game: pearls eaten by origin
//   (natural = initial or spawn tick, corpse = dropped by a death), deaths and their lengths, length alive at the end.
//   Prints per-map means: the loop (lin + loop) eats vs loses to deaths, and what the other dragons eat.
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const evalDir = path.resolve(ROOT, opt('eval', 'exp/eval-r1'));
const maps = opt('maps', 'autarky,prisoners_dilemma').split(',');
const DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 };

function massflow(R, side) {
  const M = R.match.map, W = M.width, H = M.height;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H, K = (x, y) => y * W + x;
  const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
  const portal = new Map();
  for (const pr of M.portals || []) { if (pr.length !== 2) continue; const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); }
  const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
  const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
  const across = (x, y, d) => {
    const ek = d === 'N' ? x + ',' + y + ',N' : d === 'S' ? x + ',' + wy(y + 1) + ',N' : d === 'W' ? x + ',' + y + ',W' : wx(x + 1) + ',' + y + ',W';
    const p = portal.get(ek);
    if (p) return d === 'N' ? { x: p.x, y: wy(p.y - 1) } : d === 'S' ? { x: p.x, y: p.y } : d === 'W' ? { x: wx(p.x - 1), y: p.y } : { x: p.x, y: p.y };
    const kelp = d === 'N' ? hk(x, y) : d === 'S' ? hk(x, y + 1) : d === 'W' ? vk(x, y) : vk(x + 1, y);
    return kelp ? null : { x: wx(x + DX[d]), y: wy(y + DY[d]) };
  };
  const drag = new Map(), occ = new Map(), pearls = new Map();
  for (let i = 0; i < (M.initialTiles ? M.initialTiles.length : 0); i++) if (M.initialTiles[i] === 2) pearls.set(i, 'nat');
  for (const d0 of M.initialDragons) drag.set(d0.id, { id: d0.id, team: d0.team, body: d0.body.map(s => ({ ...s })), grp: 'other', expect: [] });
  for (const d of drag.values()) for (const s of d.body) occ.set(K(s.x, s.y), d.id);
  const ours = M.initialDragons.filter(d => d.team === side);
  let lin = ours.reduce((a, b) => b.body.length > a.body.length ? b : a).id;
  drag.get(lin).grp = 'lin';
  const st = {}; const S = g => st[g] = st[g] || { eatNat: 0, eatCorpse: 0, deaths: 0, deathLen: 0 };
  let cur = -1, round = -1, drop = false;
  const clr = d => { for (const s of d.body) if (occ.get(K(s.x, s.y)) === d.id) occ.delete(K(s.x, s.y)); };
  const put = d => { for (const s of d.body) occ.set(K(s.x, s.y), d.id); };
  for (const e of R.events) {
    if (drop && !(e.type === 'tileChange' && e.hasPearl)) drop = false;
    if (e.type === 'roundStart') round = e.round;
    else if (e.type === 'turnStart') cur = e.id;
    else if (e.type === 'tileChange') { const k = K(e.tile.x, e.tile.y); if (e.hasPearl) pearls.set(k, drop ? 'corpse' : 'nat'); else pearls.delete(k); }
    else if (e.type === 'dragonAction' && e.action && e.action.kind === 'move') {
      const d = drag.get(e.id); if (!d) continue;
      clr(d); const b = d.body.slice(); d.expect = [];
      for (let i = 0; i < e.action.steps.length; i++) {
        if (i > 0 && b.length <= 2) break;
        const nx = across(b[0].x, b[0].y, e.action.steps[i]); if (!nx) break;
        if (b.some(s => s.x === nx.x && s.y === nx.y) || occ.has(K(nx.x, nx.y))) break;
        b.unshift(nx);
        const o = pearls.get(K(nx.x, nx.y));
        if (o) { pearls.delete(K(nx.x, nx.y)); if (d.team === side) { if (o === 'nat') S(d.grp).eatNat++; else S(d.grp).eatCorpse++; } } else b.pop();
        if (i > 0) b.pop();
        d.expect.push({ h: b[0], t: b[b.length - 1] });
      }
      d.body = b; put(d);
    } else if (e.type === 'dragonUpdate') {
      const d = drag.get(e.id); if (!d || round < 0) continue;
      const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
      if (x.h.x !== e.head.x || x.h.y !== e.head.y || x.t.x !== e.tail.x || x.t.y !== e.tail.y) {
        clr(d); const b = d.body.slice();
        if (b[0].x !== e.head.x || b[0].y !== e.head.y) b.unshift({ x: e.head.x, y: e.head.y });
        while (b.length > 1 && (b[b.length - 1].x !== e.tail.x || b[b.length - 1].y !== e.tail.y)) b.pop();
        d.body = b; d.expect = []; put(d); st.simMismatch = (st.simMismatch || 0) + 1;
      }
    } else if (e.type === 'dragonSplit') {
      const p = drag.get(e.parentId); if (!p) continue;
      clr(p); p.body = e.parentBody.map(s => ({ ...s })); put(p);
      const c = { id: e.childId, team: e.team, body: e.childBody.map(s => ({ ...s })), grp: p.grp === 'lin' || p.grp === 'loop' ? 'loop' : 'other', expect: [] };
      if (p.id === lin && c.body.length >= p.body.length) { p.grp = 'loop'; c.grp = 'lin'; lin = c.id; }
      drag.set(c.id, c); put(c);
    } else if (e.type === 'dragonDeath') {
      const d = drag.get(e.id); if (!d) continue;
      if (d.team === side) { S(d.grp).deaths++; S(d.grp).deathLen += d.body.length; }
      clr(d); drag.delete(e.id); drop = true;
    }
  }
  const fin = {}; for (const d of drag.values()) if (d.team === side) fin[d.grp] = (fin[d.grp] || 0) + d.body.length;
  return { st, fin };
}

if (require.main === module) {
  const seen = new Set();
  const rows = fs.readFileSync(path.join(evalDir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined && !seen.has(r.key) && seen.add(r.key) && maps.includes(r.map));
  const mean = a => a.reduce((s, x) => s + x, 0) / Math.max(1, a.length);
  const g = (x, grp, f) => ((x.st[grp] || {})[f] || 0);
  for (const m of maps) {
    const games = rows.filter(r => r.map === m).map(r => massflow(load(path.join(evalDir, 'games', r.key.replace(/:/g, '_'), 'game.replay')), r.side));
    const loopEat = games.map(x => g(x, 'lin', 'eatNat') + g(x, 'lin', 'eatCorpse') + g(x, 'loop', 'eatNat') + g(x, 'loop', 'eatCorpse'));
    const loopNat = games.map(x => g(x, 'lin', 'eatNat') + g(x, 'loop', 'eatNat'));
    const loopDeathLen = games.map(x => g(x, 'lin', 'deathLen') + g(x, 'loop', 'deathLen'));
    console.log(JSON.stringify({
      map: m, games: games.length, simMismatch: games.reduce((s, x) => s + (x.st.simMismatch || 0), 0),
      loopEaten: +mean(loopEat).toFixed(1), loopEatenNatural: +mean(loopNat).toFixed(1), loopDeathLength: +mean(loopDeathLen).toFixed(1),
      loopStubDeaths: +mean(games.map(x => g(x, 'loop', 'deaths'))).toFixed(1), loopNet: +mean(loopEat.map((v, i) => v - loopDeathLen[i])).toFixed(1),
      lineageAliveAtEnd: +mean(games.map(x => x.fin.lin || 0)).toFixed(1),
      otherNatural: +mean(games.map(x => g(x, 'other', 'eatNat'))).toFixed(1), otherCorpse: +mean(games.map(x => g(x, 'other', 'eatCorpse'))).toFixed(1),
    }));
  }
}
