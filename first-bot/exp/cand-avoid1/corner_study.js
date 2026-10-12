#!/usr/bin/env node
'use strict';
// corner_study.js — offline check of two predictors for "our long dragon gets rammed", at every decision of our dragons
// of length >= 6 with a shorter enemy head in the 7x7 window (true lengths from the replay):
//   exposed(m):    after move m our head is within the reach (length - 1 steps) of a visible shorter enemy head.
//   cornerable(m): not exposed, but one enemy action can put that enemy on a tile P' (j steps, its length then
//                  Le - (j - 1)) from which EVERY single step we could take next is within its reach, or is P' itself.
// For each decision it records what we chose, whether a clean alternative (neither) existed, and what happened next:
// rammed before our next decision, and whether at the next decision every single step was exposed.
// usage: node exp/cand-avoid1/corner_study.js --local exp/eval-r1 [--filter archetype_hunter] | --online data/online/baseline-r1
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const { geometry, bfsDist, listLocal, listOnline } = require('./ram_audit.js');
const DIRS = ['N', 'E', 'S', 'W'];

function study(file, us, info, acc) {
  const R = load(file), M = R.match.map, G = geometry(M);
  const drag = new Map(), occ = new Map(), pearls = new Set();
  const setOcc = d => { for (const k of d.body) occ.set(k, d.id); };
  const clrOcc = d => { for (const k of d.body) if (occ.get(k) === d.id) occ.delete(k); };
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearls.add(i);
  for (const d0 of M.initialDragons) { const o = { id: d0.id, team: d0.team, body: d0.body.map(s => G.key(s.x, s.y)), expect: [] }; drag.set(o.id, o); setOcc(o); }
  let round = -1, cur = -1;
  const pending = new Map();   // our id -> record of its last studied decision (resolved at its next decision or death)
  const close = (id, rammed) => { const p = pending.get(id); if (!p) return; pending.delete(id); p.rammed = rammed; acc.push(p); };
  for (const e of R.events) {
    switch (e.type) {
      case 'roundStart': round = e.round; break;
      case 'turnStart': cur = e.id; break;
      case 'tileChange': { const k = G.key(e.tile.x, e.tile.y); if (e.hasPearl) pearls.add(k); else pearls.delete(k); break; }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action || {};
        const prevHeadHere = d.body[0];
        if (d.team === us) {
          const prev = pending.get(d.id);
          const rec = d.body.length >= 6 ? decision(d, a) : null;
          if (prev) { prev.nextAllExposed = rec ? rec.allExposed : null; close(d.id, 0); }
          if (rec) pending.set(d.id, Object.assign(rec, { game: info.game, opp: info.opp, map: info.map, round, id: d.id, len: d.body.length }));
        }
        d.prevHead = prevHeadHere;
        if (a.kind !== 'move') break;
        clrOcc(d);
        const body = d.body.slice(); d.expect = [];
        for (let i = 0; i < a.steps.length; i++) {
          if (i > 0 && body.length <= 2) break;
          const nx = G.across(body[0], DIRS.indexOf(a.steps[i]));
          if (nx < 0 || body.includes(nx) || occ.has(nx)) break;
          body.unshift(nx); if (!pearls.has(nx)) body.pop(); if (i > 0) body.pop();
          d.expect.push({ h: body[0], t: body[body.length - 1] });
        }
        d.body = body; setOcc(d);
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id); if (!d || round < 0) break;
        const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        const h = G.key(e.head.x, e.head.y), t = G.key(e.tail.x, e.tail.y);
        if (x.h !== h || x.t !== t) { clrOcc(d); const b = d.body.slice(); if (b[0] !== h) b.unshift(h); while (b.length > 1 && b[b.length - 1] !== t) b.pop(); d.body = b; d.expect = []; setOcc(d); }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        clrOcc(p); p.body = e.parentBody.map(s => G.key(s.x, s.y)); setOcc(p);
        const c = { id: e.childId, team: e.team, body: e.childBody.map(s => G.key(s.x, s.y)), expect: [] }; drag.set(c.id, c); setOcc(c);
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        if (d.team === us && pending.has(d.id)) {
          const m = drag.get(cur);
          const rammed = cur !== e.id && e.reason === 'H' && m && m.team !== us ? 1 : 0;
          const p = pending.get(d.id); p.death = rammed ? 'rammed' : 'other'; close(d.id, rammed);
        }
        clrOcc(d); drag.delete(e.id);
        break;
      }
    }
  }
  for (const id of [...pending.keys()]) close(id, 0);

  function decision(d, a) {
    const me = d.body, L = me.length, head = me[0];
    const others = [...drag.values()].filter(o => o.id !== d.id);
    const vis = others.filter(o => o.team !== us && o.body.length < L && G.cheb(head, o.body[0]) <= 3);
    if (!vis.length) return null;
    const tailOf = new Set(others.filter(o => o.body.length > 1).map(o => o.body[o.body.length - 1]));
    const blockedOther = u => occ.has(u) && !tailOf.has(u) && occ.get(u) !== d.id;
    function sim(body0, steps) {
      let body = body0.slice();
      for (let i = 0; i < steps.length; i++) {
        if (i > 0 && body.length <= 2) return null;
        const nx = G.across(body[0], steps[i]); if (nx < 0 || body.includes(nx)) return null;
        const o = occ.get(nx); if (o !== undefined && o !== d.id) return null;
        body.unshift(nx); if (!pearls.has(nx)) body.pop(); if (i > 0) body.pop();
      }
      return body;
    }
    const reachOf = o => Math.max(1, o.body.length - 1);
    const exposedBody = body => { const mine = new Set(body); const bl = u => mine.has(u) || blockedOther(u);
      return vis.some(o => bfsDist(G, o.body[0], body[0], reachOf(o), bl) <= reachOf(o)); };
    function cornerable(body) {
      const nexts = [0, 1, 2, 3].map(x => sim(body, [x])).filter(Boolean);
      if (!nexts.length) return { noExit: true, corner: false };
      const mine = new Set(body); const bl = u => mine.has(u) || blockedOther(u);
      for (const o of vis) {
        const Le = o.body.length;
        // enemy positions after one action: BFS up to Le-1 steps (not onto our head: that is exposure)
        const seen = new Map([[o.body[0], 0]]); let q = [o.body[0]];
        for (let j = 1; j <= Le - 1; j++) {
          const nq = [];
          for (const t of q) for (let di = 0; di < 4; di++) {
            const u = G.across(t, di); if (u < 0 || seen.has(u) || bl(u) || u === body[0]) continue;
            seen.set(u, j); nq.push(u);
          }
          q = nq;
        }
        for (const [P, j] of seen) {
          if (j === 0) continue;
          const r2 = Math.max(1, Le - j);
          let all = true;
          for (const nb of nexts) {
            if (nb[0] === P) continue;                                   // stepping into its head: death too
            const m2 = new Set(nb); const bl2 = u => (m2.has(u) || blockedOther(u)) && u !== P;
            if (bfsDist(G, P, nb[0], r2, bl2) > r2) { all = false; break; }
          }
          if (all) return { noExit: false, corner: true };
        }
      }
      return { noExit: false, corner: false };
    }
    const singles = [0, 1, 2, 3].map(x => ({ dir: x, body: sim(me, [x]) })).filter(s => s.body);
    for (const s of singles) { s.exp = exposedBody(s.body); const c = s.exp ? { corner: false, noExit: false } : cornerable(s.body); s.corner = c.corner; s.noExit = c.noExit; }
    // sprints (2 and 3 steps) that end outside every visible shorter head's reach: counted only when every single step is exposed
    let safe2 = 0, safe3 = 0;
    if (singles.length && singles.every(s => s.exp)) for (let x = 0; x < 4; x++) for (let y = 0; y < 4; y++) {
      const b2 = sim(me, [x, y]); if (b2 && !exposedBody(b2)) safe2++;
      for (let z = 0; z < 4; z++) { const b3 = sim(me, [x, y, z]); if (b3 && !exposedBody(b3)) safe3++; }
    }
    // did an enemy that exposes one of our single steps move closer to our head on its last action?
    const man = (a2, b2) => { const W = G.W, H = G.H; let dx = Math.abs(a2 % W - b2 % W), dy = Math.abs(((a2 / W) | 0) - ((b2 / W) | 0)); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
    let approached = false, anyPrev = false;
    for (const o of vis) { if (o.prevHead === undefined) continue; anyPrev = true; if (man(o.prevHead, head) > man(o.body[0], head)) approached = true; }
    const rec = { approached, anyPrev, safe2, safe3, n1: singles.length, allExposed: singles.length > 0 && singles.every(s => s.exp), clean: singles.filter(s => !s.exp && !s.corner && !s.noExit).length,
      nCorner: singles.filter(s => s.corner).length, nExp: singles.filter(s => s.exp).length };
    if (a.kind === 'move') {
      const b = sim(me, a.steps.map(x => DIRS.indexOf(x)));
      if (b) { rec.chExp = exposedBody(b); const c = rec.chExp ? { corner: false, noExit: false } : cornerable(b); rec.chCorner = c.corner; rec.chNoExit = c.noExit; rec.sprint = a.steps.length > 1; }
    } else rec.split = 1;
    return rec;
  }
}

function main() {
  const argv = process.argv.slice(2);
  const all = k => argv.map((x, i) => x === k ? argv[i + 1] : null).filter(Boolean);
  const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
  const jobs = [...all('--local').flatMap(d => listLocal(path.resolve(ROOT, d), opt('--filter', null))), ...all('--online').flatMap(d => listOnline(path.resolve(ROOT, d), +opt('--own', 583)))];
  const acc = [];
  for (const j of jobs) study(j.file, j.us, j.info, acc);
  const out = opt('--out', null); if (out) fs.writeFileSync(out, JSON.stringify(acc));
  const grp = (name, f) => { const X = acc.filter(f); const r = X.filter(x => x.rammed).length; const n = X.filter(x => x.nextAllExposed != null); return `${name}: ${X.length} decisions, rammed before next ${r} (${(100 * r / Math.max(1, X.length)).toFixed(2)}%), next all-exposed ${n.filter(x => x.nextAllExposed).length}/${n.length} (${(100 * n.filter(x => x.nextAllExposed).length / Math.max(1, n.length)).toFixed(1)}%)`; };
  console.log(`games ${jobs.length}, studied decisions ${acc.length}`);
  console.log(grp('chosen exposed', x => x.chExp));
  console.log(grp('chosen cornerable', x => !x.chExp && x.chCorner));
  console.log(grp('chosen neither', x => x.chExp === false && !x.chCorner && !x.chNoExit));
  console.log(grp('chosen no-exit', x => x.chNoExit));
  console.log(grp('split', x => x.split));
  console.log(grp('exposed, clean alternative existed', x => x.chExp && x.clean > 0));
  console.log(grp('cornerable, clean alternative existed', x => !x.chExp && x.chCorner && x.clean > 0));
  console.log(grp('all singles exposed', x => x.allExposed));
  console.log(grp('all singles exposed, safe 2-step existed', x => x.allExposed && x.safe2 > 0));
  console.log(grp('all singles exposed, only a safe 3-step', x => x.allExposed && !x.safe2 && x.safe3 > 0));
  console.log(grp('all singles exposed, no safe sprint', x => x.allExposed && !x.safe2 && !x.safe3));
  console.log(grp('all singles exposed, we sprinted', x => x.allExposed && x.sprint));
  const R = acc.filter(x => x.rammed);
  console.log(`rammed ${R.length}: at that decision chosen exposed ${R.filter(x => x.chExp).length}, cornerable ${R.filter(x => !x.chExp && x.chCorner).length}, neither ${R.filter(x => x.chExp === false && !x.chCorner).length}, split ${R.filter(x => x.split).length}; clean alt existed ${R.filter(x => x.clean > 0).length}`);
}
if (require.main === module) main();
