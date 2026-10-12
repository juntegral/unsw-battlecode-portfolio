#!/usr/bin/env node
// W15a split safety: for each split of ours, the region ahead of the child (from its birth tile = our old tail, away from its neck) as the
// parent's process could know it (its own 7x7 windows since birth; cycle / unknown / dead as in unkstep.js) against the truth, by split rule
// (the parent's indicator that turn), with the child's fate (died without ever standing on the true 2-core, or lived / reached the core).
// usage: node exp/w15a/splitview.js <us A|B> <game dirs...>
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const args = process.argv.slice(2).filter(a => a !== '--list'), us = args[0];
const files = [];
for (const p of args.slice(1)) { const walk = d => { for (const f of fs.readdirSync(d)) { const q = path.join(d, f); if (fs.statSync(q).isDirectory()) walk(q); else if (f.endsWith('.replay')) files.push(q); } }; if (p.endsWith('.replay')) files.push(p); else walk(p); }
const DIRS = ['N', 'E', 'S', 'W'], DX = [0, 1, 0, -1], DY = [-1, 0, 1, 0];
const load = makeLoader(viewerSource());
const tab = {}, add = (k, n = 1) => { tab[k] = (tab[k] || 0) + n; };
const ALL = { has: () => true };
for (const file of files) {
  let R; try { R = load(file); } catch (e) { continue; }
  let G = null;
  const geo = ctx => {
    if (G) return G;
    const { W, H, across } = ctx, N = W * H, nb = new Array(N);
    for (let k = 0; k < N; k++) { const x = k % W, y = (k / W) | 0; nb[k] = DIRS.map(d => { const u = across(x, y, d); return u ? u.y * W + u.x : -1; }); }
    const deg = new Int32Array(N), gone = new Uint8Array(N), q = [];
    for (let k = 0; k < N; k++) { for (const u of nb[k]) if (u >= 0) deg[k]++; if (deg[k] <= 1) { gone[k] = 1; q.push(k); } }
    for (let i = 0; i < q.length; i++) for (const u of nb[q[i]]) { if (u < 0 || gone[u]) continue; if (--deg[u] <= 1) { gone[u] = 1; q.push(u); } }
    G = { W, H, N, nb, gone }; return G;
  };
  const plain = (g, k, di) => { const x = k % g.W, y = (k / g.W) | 0; return ((y + DY[di] + g.H) % g.H) * g.W + (x + DX[di] + g.W) % g.W; };
  const view = (g, known, a, b) => {   // region from b not back through a (a: the child's neck)
    const par = new Map([[b, a]]), q = [b]; let unknown = false;
    for (let i = 0; i < q.length && q.length < 400; i++) {
      const t = q[i];
      for (let di = 0; di < 4; di++) {
        const pl = plain(g, t, di);
        if (!(known.has(t) || known.has(pl))) { unknown = true; continue; }
        const u = g.nb[t][di];
        if (u < 0 || u === a) continue;
        if (par.has(u)) { if (par.get(t) !== u) return 'cycle'; continue; }
        par.set(u, t); q.push(u);
      }
    }
    return unknown ? 'unknown' : 'dead';
  };
  const seenBy = new Map(), lastInd = new Map(), kids = new Map();
  const map = path.basename(path.dirname(file)).replace(/^proxy4_king_/, '').replace(/_[AB]_1$/, '');
  perGame(R, { map: '?', variant: 'a' }, {
    turn(d, round, ctx) {
      if (d.team !== us) return;
      const g = geo(ctx), h = d.body[0];
      let s = seenBy.get(d.id); if (!s) { s = new Set(); seenBy.set(d.id, s); }
      for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) s.add(((h.y + dy + g.H) % g.H) * g.W + (h.x + dx + g.W) % g.W);
    },
    indicator(e, round) { lastInd.set(e.id, { round, text: e.text || '' }); },
    split(p, ch, e, round, ctx) {
      if (p.team !== us) return;
      const g = geo(ctx), b = ch.body[0].y * g.W + ch.body[0].x, a = ch.body[1].y * g.W + ch.body[1].x;
      const li = lastInd.get(p.id), rule = li && li.round === round ? (li.text.match(/^[a-z-]+/) || ['?'])[0] : '?';
      const v = view(g, seenBy.get(p.id) || new Set(), a, b), truth = view(g, ALL, a, b) === 'cycle' ? 'open-ahead' : 'dead-ahead';
      kids.set(ch.id, { key: `${rule.padEnd(13)} parent view ${v.padEnd(7)} truth ${truth}`, map, core: !g.gone[b] });
      if (process.argv.includes('--list') && v === 'dead' && rule !== 'escape-split') {
        // the region's pearls (now) and depth, as regionAhead sees them on the true graph
        const dist = new Map([[b, 0]]), q = [b]; let far = 0, pr = 0;
        for (let i = 0; i < q.length; i++) { const t = q[i]; far = Math.max(far, dist.get(t)); if (ctx.pearls.has(t)) pr++; for (const u of g.nb[t]) if (u >= 0 && u !== a && !dist.has(u)) { dist.set(u, dist.get(t) + 1); q.push(u); } }
        console.log(`   ${map} r${round} #${p.id} ${li ? li.text : '?'} -> child #${ch.id} size ${ch.body.length} at ${ch.body[0].x},${ch.body[0].y}: region ${dist.size} tiles, depth ${far}, pearls ${pr}`);
      }
    },
    action(d, e, round, ctx) { const k = kids.get(d.id); if (!k || k.core) return; const g = geo(ctx), h = d.body[0]; if (!g.gone[h.y * g.W + h.x]) k.core = true; },
    death(d) { const k = kids.get(d.id); if (k) k.died = true; },
    end() { for (const k of kids.values()) add(`${k.key} child ${k.died && !k.core ? 'died in the branch' : 'lived or reached the core'}`); },
  });
}
for (const k of Object.keys(tab).sort()) console.log(String(tab[k]).padStart(6) + '  ' + k);
