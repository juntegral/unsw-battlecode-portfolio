#!/usr/bin/env node
// Trace a team's longest dragon in one replay and draw the board around it at chosen events.
// usage: node trace.js <replay> --team A|B [--from 250] [--every 10] [--draw stub|death|all|none] [--radius 6] [--at r1,r2]
'use strict';
const path = require('path');
const ROOT = require('path').resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools/replay.js'));
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const file = argv[0], GATHER = argv.includes('--gather'), ZX = +arg('zx', -1), ZY = +arg('zy', -1), team = arg('team', 'A'), from = +arg('from', 250), every = +arg('every', 10), drawMode = arg('draw', 'stub'), rad = +arg('radius', 6);
const atR = new Set(String(arg('at', '')).split(',').filter(Boolean).map(Number));
const R = load(file);
const M = R.match.map, W = M.width, H = M.height;
const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H, key = (x, y) => y * W + x;
const DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 };
const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
const portal = new Map();
for (const pr of M.portals || []) { if (pr.length !== 2) continue; const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); }
const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
const isPortalN = (x, y) => portal.has(x + ',' + wy(y) + ',N'), isPortalW = (x, y) => portal.has(wx(x) + ',' + y + ',W');
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
const drag = new Map(), occ = new Map(), pearls = new Set(); const GACC = {};
const setOcc = d => { for (const s of d.body) occ.set(key(s.x, s.y), d.id); };
const clrOcc = d => { for (const s of d.body) if (occ.get(key(s.x, s.y)) === d.id) occ.delete(key(s.x, s.y)); };
if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearls.add(i);
for (const d0 of M.initialDragons) { const o = { id: d0.id, team: d0.team, body: d0.body.map(s => ({ x: s.x, y: s.y })) }; drag.set(o.id, o); setOcc(o); }
function longest(tm) { let b = null; for (const d of drag.values()) if (d.team === tm && (!b || d.body.length > b.body.length)) b = d; return b; }
function draw(cx, cy, title, hl) {
  console.log('    ' + title);
  const lines = [];
  for (let yy = -rad; yy <= rad; yy++) {
    let top = '', mid = '';
    for (let xx = -rad; xx <= rad; xx++) {
      const x = wx(cx + xx), y = wy(cy + yy);
      top += '+' + (hk(x, y) ? '---' : isPortalN(x, y) ? '===' : '   ');
      const wch = vk(x, y) ? '|' : isPortalW(x, y) ? '#' : ' ';
      const o = occ.get(key(x, y));
      let c = pearls.has(key(x, y)) ? ' o ' : ' . ';
      if (o !== undefined) {
        const d = drag.get(o), i = d.body.findIndex(s => s.x === x && s.y === y);
        const mine = d.team === team;
        const ch = hl && d.id === hl ? (i === 0 ? 'K' : 'k') : mine ? (i === 0 ? 'A' : 'a') : (i === 0 ? 'E' : 'e');
        c = i === 0 ? `${ch}${String(d.body.length).padStart(2, ' ')}`.slice(0, 3) : ` ${ch} `;
      }
      mid += wch + c;
    }
    lines.push(top + '+'); lines.push(mid + '|');
  }
  console.log(lines.map(l => '    ' + l).join('\n'));
}
let round = -1, cur = -1, lastKing = -1;
const stubsSeen = [];
for (const e of R.events) {
  switch (e.type) {
    case 'roundStart': {
      round = e.round;
      if (GATHER && round >= 300 && round % 5 === 0) {
        const k = longest(team); if (k) { const b = Math.floor(round / 20) * 20;
          if (ZX >= 0) { const tdz = (p) => Math.min(Math.abs(p.x - ZX), W - Math.abs(p.x - ZX)) + Math.min(Math.abs(p.y - ZY), H - Math.abs(p.y - ZY));
            (GACC['K' + b] = GACC['K' + b] || []).push(tdz(k.body[0]));
            for (const d of drag.values()) if (d.team === team && d !== k && d.body.length <= 4) (GACC['P' + b] = GACC['P' + b] || []).push(tdz(d.body[0])); }
          for (const d of drag.values()) { if (d.team !== team || d === k || d.body.length > 4) continue;
            const dx = Math.min(Math.abs(d.body[0].x - k.body[0].x), W - Math.abs(d.body[0].x - k.body[0].x)), dy = Math.min(Math.abs(d.body[0].y - k.body[0].y), H - Math.abs(d.body[0].y - k.body[0].y));
            (GACC[b] = GACC[b] || []).push(dx + dy); } }
      }
      if (!GATHER && round >= from && round % every === 0) {
        const k = longest(team), o = longest(team === 'A' ? 'B' : 'A');
        let units = 0, total = 0; for (const d of drag.values()) if (d.team === team) { units++; total += d.body.length; }
        console.log(`r${round} king #${k ? k.id : '-'} L${k ? k.body.length : 0} at ${k ? k.body[0].x + ',' + k.body[0].y : '-'} units ${units} total ${total} | enemy longest ${o ? o.body.length : 0}`);
      }
      if (atR.has(round)) { const k = longest(team); if (k) draw(k.body[0].x, k.body[0].y, `r${round} board around king #${k.id} L${k.body.length}`, k.id); }
      break;
    }
    case 'turnStart': cur = e.id; break;
    case 'tileChange': { const k = key(e.tile.x, e.tile.y); if (e.hasPearl) pearls.add(k); else pearls.delete(k); break; }
    case 'dragonAction': {
      const d = drag.get(e.id); if (!d) break;
      const a = e.action; if (!a || a.kind !== 'move') break;
      clrOcc(d); const body = d.body.slice();
      for (let i = 0; i < a.steps.length; i++) {
        if (i > 0 && body.length <= 2) break;
        const h = body[0], nx = across(h.x, h.y, a.steps[i]);
        if (!nx) break; if (body.some(s => s.x === nx.x && s.y === nx.y)) break; if (occ.has(key(nx.x, nx.y))) break;
        body.unshift(nx); const k = key(nx.x, nx.y);
        if (pearls.has(k)) pearls.delete(k); else body.pop();
        if (i > 0) body.pop();
      }
      d.body = body; setOcc(d); break;
    }
    case 'dragonUpdate': {
      const d = drag.get(e.id); if (!d || round < 0) break;
      if (d.body[0].x !== e.head.x || d.body[0].y !== e.head.y || d.body[d.body.length - 1].x !== e.tail.x || d.body[d.body.length - 1].y !== e.tail.y) {
        clrOcc(d); const b = d.body.slice();
        if (b[0].x !== e.head.x || b[0].y !== e.head.y) b.unshift({ x: e.head.x, y: e.head.y });
        while (b.length > 1 && (b[b.length - 1].x !== e.tail.x || b[b.length - 1].y !== e.tail.y)) b.pop();
        d.body = b; setOcc(d);
      }
      break;
    }
    case 'dragonSplit': {
      const p = drag.get(e.parentId); if (!p) break;
      const lenBefore = p.body.length;
      const k = longest(p.team);
      const wasKing = k && k.id === p.id;
      if (!GATHER && p.team === team && round >= from && lenBefore >= 8 && e.parentBody.length <= 3) {
        console.log(`  r${round} STUB split #${p.id} L${lenBefore} -> parent ${e.parentBody.length} + child #${e.childId} ${e.childBody.length}${wasKing ? ' (king)' : ''}`);
        if (drawMode === 'stub' || drawMode === 'all') draw(p.body[0].x, p.body[0].y, `before split, r${round}`, p.id);
      } else if (!GATHER && p.team === team && round >= from && lenBefore >= 8) console.log(`  r${round} split #${p.id} L${lenBefore} -> ${e.parentBody.length} + ${e.childBody.length}${wasKing ? ' (king)' : ''}`);
      clrOcc(p); p.body = e.parentBody.map(s => ({ x: s.x, y: s.y })); setOcc(p);
      const c = { id: e.childId, team: e.team, body: e.childBody.map(s => ({ x: s.x, y: s.y })) }; drag.set(c.id, c); setOcc(c);
      break;
    }
    case 'dragonDeath': {
      const d = drag.get(e.id); if (!d) break;
      const k = longest(d.team);
      if (!GATHER && d.team === team && round >= from && d.body.length >= 8) {
        console.log(`  r${round} DEATH #${d.id} L${d.body.length} reason ${e.reason}${k && k.id === d.id ? ' (king)' : ''} mover ${cur === d.id}`);
        if (drawMode === 'death' || drawMode === 'all') draw(d.body[0].x, d.body[0].y, `at death r${round}`, d.id);
      }
      clrOcc(d); drag.delete(e.id); break;
    }
  }
}
if (GATHER) { const out = {}; for (const [b, a] of Object.entries(GACC)) out[b] = a; console.log(JSON.stringify(out)); } else console.log('result', JSON.stringify(R.result));
