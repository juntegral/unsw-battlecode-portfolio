#!/usr/bin/env node
// W15a diagnosis: our deaths inside dead branches (tiles off the 2-core of the true passable graph, portals included: once a dragon of
// length >= 2 is in one it can never leave, because it cannot step into its neck and a tree has no way round) and how each got there.
//   esc-stub   the head part left behind by its own escape split ("escape-split" indicator on the split turn)
//   born-in    a split child born inside the branch that never reached the core
//   start-in   a start dragon placed inside the branch
//   entered    stepped from the core into the branch. At that step (turnStart knowledge of this process: the union of its own 7x7
//              windows since birth, no mirror): known-dead = the region beyond the step (not back through the neck) is a finite tree of
//              known edges; room = it is finite and known but has a cycle; unknown = it reaches a tile this process never saw (unknown
//              edges are open in the bot's model). bait = a pearl lay in the true branch. depth = longest path from the entry tile.
// usage: node exp/w15a/deadclass.js <replay dir or file> <us A|B> [--detail N]   (several dirs: a set; the map comes from the replay)
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const args = process.argv.slice(2);
const di = args.indexOf('--detail'), DETAIL = di >= 0 ? +args[di + 1] : 0;
const pos = args.filter((a, i) => !a.startsWith('--') && (i === 0 || !args[i - 1].startsWith('--')));
const us = pos[pos.length - 1];
const files = [];
for (const p of pos.slice(0, -1)) {
  if (p.endsWith('.replay')) { files.push(p); continue; }
  const walk = d => { for (const f of fs.readdirSync(d)) { const q = path.join(d, f); if (fs.statSync(q).isDirectory()) walk(q); else if (f.endsWith('.replay')) files.push(q); } };
  walk(p);
}
const DIRS = ['N', 'E', 'S', 'W'];
const load = makeLoader(viewerSource());
const tot = {};
const add = (o, k, v = 1) => { o[k] = (o[k] || 0) + v; };
for (const file of files) {
  let R; try { R = load(file); } catch (e) { console.error('skip', file, e.message); continue; }
  const name = path.basename(path.dirname(file));
  let G = null;   // geometry, built on the first hook (ctx.across)
  const geo = ctx => {
    if (G) return G;
    const { W, H, across } = ctx, N = W * H;
    const nb = new Array(N);
    for (let k = 0; k < N; k++) { const x = k % W, y = (k / W) | 0; nb[k] = DIRS.map(d => { const u = across(x, y, d); return u ? u.y * W + u.x : -1; }); }
    const deg = new Int32Array(N), gone = new Uint8Array(N), q = [];
    for (let k = 0; k < N; k++) { for (const u of nb[k]) if (u >= 0) deg[k]++; if (deg[k] <= 1) { gone[k] = 1; q.push(k); } }
    for (let i = 0; i < q.length; i++) for (const u of nb[q[i]]) { if (u < 0 || gone[u]) continue; if (--deg[u] <= 1) { gone[u] = 1; q.push(u); } }
    G = { W, H, N, nb, gone };
    return G;
  };
  // the true branch beyond a core->branch step a->b: tiles, longest path from b, pearls in it
  const branch = (g, a, b) => {
    const dist = new Map([[b, 0]]), q = [b]; let far = 0;
    for (let i = 0; i < q.length; i++) for (const u of g.nb[q[i]]) { if (u < 0 || u === a || !g.gone[u] || dist.has(u)) continue; dist.set(u, dist.get(q[i]) + 1); far = Math.max(far, dist.get(u)); q.push(u); }
    return { tiles: dist, far };
  };
  // what this process could know: the region beyond a->b over its known edges (an edge is known when either tile was seen)
  const botView = (g, seen, a, b) => {
    const { W, H } = g;
    const plain = (k, di) => { const x = k % W, y = (k / W) | 0, dx = [0, 1, 0, -1][di], dy = [-1, 0, 1, 0][di]; return ((y + dy + H) % H) * W + (x + dx + W) % W; };
    const par = new Map([[b, a]]), q = [b]; let cycles = 0;
    for (let i = 0; i < q.length; i++) {
      const t = q[i];
      if (!seen.has(t)) return 'unknown';
      if (q.length > 600) return 'unknown';
      for (let di = 0; di < 4; di++) {
        const pl = plain(t, di);
        const known = seen.has(t) || seen.has(pl);
        const u = known ? g.nb[t][di] : pl;
        if (u < 0 || u === a) continue;
        if (par.has(u)) { if (par.get(t) !== u) cycles++; continue; }
        par.set(u, t); q.push(u);
      }
    }
    return cycles > 0 ? 'room' : 'known-dead';
  };
  const seenBy = new Map(), state = new Map(), lastInd = new Map();
  const res = { deaths: 0, inBranch: 0, cls: {}, lenLost: {}, entered: { 'known-dead': 0, room: 0, unknown: 0 }, bait: 0, depth: [], life: [], details: [], eatB: 0, eatC: 0, lostB: 0, lostC: 0, escL: [], roots: {}, escChild: {}, rootSeen: new Set(), rootList: [], rootsL: {} };
  perGame(R, { map: '?', variant: 'a' }, {
    turn(d, round, ctx) {
      if (d.team !== us) return;
      const g = geo(ctx), h = d.body[0];
      let s = seenBy.get(d.id); if (!s) { s = new Set(); seenBy.set(d.id, s); }
      for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) s.add(((h.y + dy + g.H) % g.H) * g.W + (h.x + dx + g.W) % g.W);
      if (!state.has(d.id)) { const k = h.y * g.W + h.x; state.set(d.id, { kind: g.gone[k] ? 'start-in' : 'core', entry: null }); }
    },
    indicator(e, round) { lastInd.set(e.id, { round, text: e.text || '' }); },
    eat(d, k, o, round, ctx) { if (d.team !== us) return; const g = geo(ctx); if (g.gone[k]) res.eatB++; else res.eatC++; },
    split(p, ch, e, round, ctx) {
      if (p.team !== us) return;
      const g = geo(ctx), h = ch.body[0], k = h.y * g.W + h.x;
      const li = lastInd.get(p.id), esc = li && li.round === round && /^escape-split/.test(li.text);
      const rule = li && li.round === round ? (li.text.match(/^[a-z-]+/) || ['?'])[0] : '?';
      state.set(ch.id, { kind: g.gone[k] ? 'born-in' : 'core', entry: null, born: round, parent: p.id, rule });
      if (esc) add(res.escChild, g.gone[k] ? 'child in branch' : 'child on core');
      if (esc) { const s = state.get(p.id) || { kind: 'core', entry: null }; s.esc = round; state.set(p.id, s); res.escL.push(p.body.length + ch.body.length); }
    },
    action(d, e, round, ctx, hb) {
      if (d.team !== us || !e.action || e.action.kind !== 'move') return;
      const g = geo(ctx), a = hb[0].y * g.W + hb[0].x, b = d.body[0].y * g.W + d.body[0].x;
      const s = state.get(d.id) || { kind: 'core', entry: null }; state.set(d.id, s);
      if (!g.gone[b]) { s.kind = 'core'; s.entry = null; return; }
      if (g.gone[a] || s.entry) return;
      const br = branch(g, a, b);
      let bait = false; for (const [pk] of ctx.pearls) if (br.tiles.has(pk)) { bait = true; break; }
      const li = lastInd.get(d.id);
      s.kind = 'entered';
      s.entry = { round, view: botView(g, seenBy.get(d.id) || new Set(), a, b), bait, far: br.far, size: br.tiles.size, len: hb.length, ind: li && li.round === round ? li.text : '?', from: `${hb[0].x},${hb[0].y}`, to: `${d.body[0].x},${d.body[0].y}` };
    },
    death(d, rec, idx, other, round, ctx) {
      if (d.team !== us) return;
      res.deaths++;
      const g = geo(ctx), h = d.body[0], k = h.y * g.W + h.x;
      if (!g.gone[k]) { res.lostC += d.body.length; return; }
      res.lostB += d.body.length;
      res.inBranch++;
      const s = state.get(d.id) || { kind: '?', entry: null };
      const cls = s.esc != null ? 'esc-stub' : s.kind;
      add(res.cls, cls); add(res.lenLost, cls, d.body.length);
      // root cause: walk up through ancestors that were born inside a branch until one entered, started inside, or was born inside by a non-escape split
      let id = d.id, r = '?', hops = 0;
      for (;;) {
        const st = state.get(id); if (!st) { r = 'unknown-ancestor'; break; }
        if (st.kind === 'entered' && st.entry) { const vm = /\bv(-?[0-9.]+)/.exec(st.entry.ind); const v = vm ? +vm[1] : NaN; r = 'entered ' + st.entry.view + (v < -100 ? ' doomed' : ' free') + (st.entry.len < 4 ? ' L<4' : ' L>=4'); if (!res.rootSeen.has(id)) { res.rootSeen.add(id); res.rootList.push(`#${id} r${st.entry.round} ${st.entry.from}->${st.entry.to} L${st.entry.len} ${st.entry.view}${st.entry.bait ? ' bait' : ''} depth ${st.entry.far} size ${st.entry.size} | ${st.entry.ind}`); } break; }
        if (st.kind === 'start-in') { r = 'start-in'; break; }
        if (st.kind === 'born-in') { if (st.rule === 'escape-split' && st.parent != null && hops < 400) { id = st.parent; hops++; continue; } r = 'born-in by ' + st.rule; break; }
        r = 'core?'; break;
      }
      add(res.roots, r); add(res.rootsL, r, d.body.length);
      if (cls === 'entered' && s.entry) {
        res.entered[s.entry.view]++; if (s.entry.bait) res.bait++; res.depth.push(s.entry.far); res.life.push(round - s.entry.round);
        if (res.details.length < DETAIL) res.details.push(`#${d.id} r${s.entry.round} ${s.entry.from}->${s.entry.to} L${s.entry.len} ${s.entry.view}${s.entry.bait ? ' bait' : ''} depth ${s.entry.far} size ${s.entry.size}; died r${round} ${CAUSE[rec.cause]} L${d.body.length} | ${s.entry.ind}`);
      }
    },
  });
  const med = a => { const s = a.slice().sort((x, y) => x - y); return s.length ? s[s.length >> 1] : '-'; };
  const cl = Object.entries(res.cls).map(([c, n]) => `${c} ${n} (L ${res.lenLost[c]})`).join(', ');
  const en = res.cls.entered || 0;
  console.log(`${name}: our deaths ${res.deaths}, in a dead branch ${res.inBranch}: ${cl}` + (en ? ` | entered: known-dead ${res.entered['known-dead']}, room ${res.entered.room}, unknown ${res.entered.unknown}; bait ${res.bait}; depth med ${med(res.depth)}; rounds to death med ${med(res.life)}` : ''));
  console.log(`   roots of branch deaths: ${Object.entries(res.roots).sort((a, b) => b[1] - a[1]).map(([k, n]) => k + ' ' + n).join(', ')}; escape-split children: ${Object.entries(res.escChild).map(([k, n]) => k + ' ' + n).join(', ')}`);
  console.log(`   economy: in dead branches ate ${res.eatB}, lost ${res.lostB} in deaths (net ${res.eatB - res.lostB}); on the core ate ${res.eatC}, lost ${res.lostC}; escape splits ${res.escL.length} at L med ${med(res.escL)}`);
  for (const l of res.details) console.log('   ' + l);
  if (process.argv.includes('--roots')) for (const l of res.rootList) console.log('   root ' + l);
  add(tot, 'deaths', res.deaths); add(tot, 'inBranch', res.inBranch);
  for (const [c, n] of Object.entries(res.cls)) { add(tot, c, n); add(tot, 'L:' + c, res.lenLost[c]); }
  for (const [v, n] of Object.entries(res.entered)) add(tot, 'entered:' + v, n);
  for (const [k, n] of Object.entries(res.roots)) { add(tot, 'root:' + k, n); add(tot, 'rootL:' + k, res.rootsL[k]); }
  add(tot, 'bait', res.bait); for (const k of ['eatB', 'eatC', 'lostB', 'lostC']) add(tot, k, res[k]); add(tot, 'esc', res.escL.length);
}
if (files.length > 1) {
  console.log('TOTAL deaths ' + tot.deaths + ', in dead branches ' + tot.inBranch + '; economy in branches ate ' + tot.eatB + ' lost ' + tot.lostB + ', core ate ' + tot.eatC + ' lost ' + tot.lostC + '; escape splits ' + tot.esc);
  for (const [k, n] of Object.entries(tot).filter(([k]) => k.startsWith('root:')).sort((a, b) => b[1] - a[1])) console.log('  ' + k.slice(5).padEnd(40) + String(n).padStart(6) + ' deaths, L ' + tot['rootL:' + k.slice(5)]);
}
