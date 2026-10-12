#!/usr/bin/env node
'use strict';
// fortstat.js — corridor-fortress mechanism metrics per game (base-px9).
// usage: node exp/base-px-tools/fortstat.js <label>[+<label>...] [--maps autarky,prisoners_dilemma] [--opps a,b] [--out f.jsonl]
//        node exp/base-px-tools/fortstat.js --replay <file> --side A|B
// Reads exp/<label>/rows.jsonl and exp/<label>/games/<key>/game.replay. Per game (our side):
//   - the start-lineage study of exp/cand-escape1/escape_study.js (reused, not changed): corridor fountain spawns
//     (tiles with max spawn gap <= 5 within one tile of the start line), natural fountain pearls eaten by us and by the
//     opponent, lineage length by round, lineage death round and reason, first round the lineage head is >= 2 off the line
//   - for both teams at rounds 50/100/200/300/400/500 (state at the start of the round; 500 = end): living dragons,
//     total length, longest
//   - our longest dragon at each check round that is not the start lineage ("swarm king")
// Output: one JSON line per game (--out) and a table by map and opponent.
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const { study } = require(path.join(ROOT, 'exp', 'cand-escape1', 'escape_study.js'));
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const CHECK = [50, 100, 200, 300, 400, 500];

// team census: replays every step with the rules of rules/execution-order.md (the same stepping as
// exp/cand-escape1/escape_study.js: eating keeps the tail, each extra sprint step drops one more tail segment), corrected
// by the engine's dragonUpdate head/tail when they differ
function census(R, side) {
  const M = R.match.map, W = M.width, H = M.height;
  const DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 };
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H, key = (x, y) => y * W + x;
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
    if (p) { if (d === 'N') return { x: p.x, y: wy(p.y - 1) }; if (d === 'S') return { x: p.x, y: p.y }; if (d === 'W') return { x: wx(p.x - 1), y: p.y }; return { x: p.x, y: p.y }; }
    if (kelp) return null;
    return { x: wx(x + DX[d]), y: wy(y + DY[d]) };
  }
  const drag = new Map(), occ = new Map(), pearls = new Set();
  const setOcc = d => { for (const s of d.body) occ.set(key(s.x, s.y), d.id); };
  const clrOcc = d => { for (const s of d.body) if (occ.get(key(s.x, s.y)) === d.id) occ.delete(key(s.x, s.y)); };
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearls.add(i);
  for (const d0 of M.initialDragons) { const o = { id: d0.id, team: d0.team, body: d0.body.map(s => ({ x: s.x, y: s.y })) }; drag.set(o.id, o); setOcc(o); }
  const out = {}; let round = -1, mismatch = 0;
  const snap = () => {
    const s = { A: { n: 0, total: 0, longest: 0 }, B: { n: 0, total: 0, longest: 0 } };
    for (const d of drag.values()) { const t = s[d.team]; const L = d.body.length; t.n++; t.total += L; if (L > t.longest) t.longest = L; }
    return s;
  };
  for (const e of R.events) {
    switch (e.type) {
      case 'roundStart': round = e.round; if (CHECK.includes(round)) out[round] = snap(); break;
      case 'tileChange': if (e.hasPearl) pearls.add(key(e.tile.x, e.tile.y)); else pearls.delete(key(e.tile.x, e.tile.y)); break;
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action; if (!a || a.kind !== 'move') break;
        clrOcc(d); const body = d.body.slice(); d.expect = [];
        for (let i = 0; i < a.steps.length; i++) {
          if (i > 0 && body.length <= 2) break;
          const h = body[0], nx = across(h.x, h.y, a.steps[i]);
          if (!nx || body.some(s => s.x === nx.x && s.y === nx.y) || occ.get(key(nx.x, nx.y)) !== undefined) break;
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
        const d = drag.get(e.id); if (!d || round < 0) break;
        const x = d.expect && d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        if (x.h.x !== e.head.x || x.h.y !== e.head.y || x.t.x !== e.tail.x || x.t.y !== e.tail.y) {
          clrOcc(d); const b = d.body.slice();
          if (b[0].x !== e.head.x || b[0].y !== e.head.y) b.unshift({ x: e.head.x, y: e.head.y });
          while (b.length > 1 && (b[b.length - 1].x !== e.tail.x || b[b.length - 1].y !== e.tail.y)) b.pop();
          d.body = b; d.expect = []; setOcc(d); mismatch++;
        }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        clrOcc(p); p.body = e.parentBody.map(s => ({ x: s.x, y: s.y })); setOcc(p);
        const c = { id: e.childId, team: e.team, body: e.childBody.map(s => ({ x: s.x, y: s.y })) }; drag.set(c.id, c); setOcc(c);
        break;
      }
      case 'dragonDeath': { const d = drag.get(e.id); if (!d) break; clrOcc(d); drag.delete(e.id); break; }
    }
  }
  const fin = snap();
  // the engine's final result is authoritative for the end state
  const res = R.result;
  if (res && res.teamA) { fin.A = { n: res.teamA.dragonCount, total: res.teamA.totalLength, longest: res.teamA.longestDragon }; fin.B = { n: res.teamB.dragonCount, total: res.teamB.totalLength, longest: res.teamB.longestDragon }; }
  out[500] = fin;
  for (const r of CHECK) if (!out[r]) out[r] = fin; // game ended early: the end state
  const us = side, them = side === 'A' ? 'B' : 'A';
  const o = {};
  for (const r of CHECK) { o['n' + r] = out[r][us].n; o['tot' + r] = out[r][us].total; o['lng' + r] = out[r][us].longest; o['on' + r] = out[r][them].n; o['otot' + r] = out[r][them].total; o['olng' + r] = out[r][them].longest; }
  return o;
}

function gameStat(file, side) {
  const R = load(file);
  const g = study(R, side, false);
  const c = census(R, side);
  const linAlive = g.linDeathRound === null;
  return {
    startLen: g.startLen, fountainSpawns: g.fountainSpawns, fountUs: g.eatNatFountain, fountUsCorpse: g.eatCorpseFountain, fountThem: g.oppEatFountain,
    escSplits: g.escapeSplits, linEscSplits: g.linEscapeSplits, exitRound: g.exitRound, linDeathRound: g.linDeathRound, linDeathReason: g.linDeathReason,
    linAlive, lin100: g.linLen[100], lin200: g.linLen[200], lin300: g.linLen[300], lin400: g.linLen[400], lin500: g.linLen[500], linMax: g.linMaxBy[500],
    eatNat: g.eatNat, eatCorpse: g.eatCorpse, ...c,
  };
}

if (opt('replay', null)) { console.log(JSON.stringify(gameStat(path.resolve(opt('replay')), opt('side', 'A')))); process.exit(0); }

const labels = argv[0].split('+');
const mapsF = opt('maps', 'autarky,prisoners_dilemma').split(','), oppsF = opt('opps', null) ? opt('opps').split(',') : null;
const games = [];
for (const lab of labels) {
  const dir = path.join(ROOT, 'exp', lab); const seen = new Set();
  for (const l of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue; const r = JSON.parse(l);
    if (r.G === undefined || seen.has(r.key)) continue; seen.add(r.key);
    if (!mapsF.includes(r.map) || (oppsF && !oppsF.includes(r.opp))) continue;
    const f = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
    games.push({ label: lab, key: r.key, opp: r.opp, map: r.map, side: r.side, seed: r.seed, G: r.G, won: r.won, alive: r.alive, ...gameStat(f, r.side) });
  }
}
if (opt('out', null)) fs.writeFileSync(opt('out'), games.map(g => JSON.stringify(g)).join('\n') + '\n');
const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN;
const med = a => { const b = a.filter(x => x !== null && x !== undefined).sort((x, y) => x - y); return b.length ? b[Math.floor(b.length / 2)] : null; };
const f1 = x => Number.isFinite(x) ? x.toFixed(1) : '-';
console.log(`${labels.join('+')}: ${games.length} games`);
console.log('| map | opp | n | win | G | fountain spawns | fountain eaten us / them | lineage alive | lineage L r100/r200/r500 | lineage exit (games) | units r100/r200 (them) | longest r400/r500 |');
console.log('|---|---|---:|---:|---:|---:|---|---:|---|---|---|---|');
const groups = new Map();
for (const g of games) { for (const k of [g.map + '|(all)', g.map + '|' + g.opp]) { if (!groups.has(k)) groups.set(k, []); groups.get(k).push(g); } }
for (const [k, gs] of [...groups.entries()].sort()) {
  const [m, o] = k.split('|');
  const exits = gs.filter(g => g.exitRound !== null);
  console.log(`| ${m} | ${o} | ${gs.length} | ${gs.filter(g => g.won).length} | ${f1(mean(gs.map(g => g.G)))} | ${f1(mean(gs.map(g => g.fountainSpawns)))} | ${f1(mean(gs.map(g => g.fountUs)))} / ${f1(mean(gs.map(g => g.fountThem)))} | ${gs.filter(g => g.linAlive).length}/${gs.length} | ${f1(mean(gs.map(g => g.lin100)))}/${f1(mean(gs.map(g => g.lin200)))}/${f1(mean(gs.map(g => g.lin500)))} | ${exits.length ? med(exits.map(g => g.exitRound)) : '-'} (${exits.length}) | ${f1(mean(gs.map(g => g.n100)))}/${f1(mean(gs.map(g => g.n200)))} (${f1(mean(gs.map(g => g.on100)))}/${f1(mean(gs.map(g => g.on200)))}) | ${f1(mean(gs.map(g => g.lng400)))}/${f1(mean(gs.map(g => g.lng500)))} |`);
}
