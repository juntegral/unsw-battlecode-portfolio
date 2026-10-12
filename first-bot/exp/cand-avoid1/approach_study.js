#!/usr/bin/env node
'use strict';
// approach_study.js — do shorter enemy heads near our long dragons move toward our head? Per opponent.
// For each decision of our dragon (length >= 6) and each enemy head of length < ours within Chebyshev 3 of our head,
// the enemy's next action is scored against our head after our move: closer / same / farther (Manhattan on the torus).
// usage: node exp/cand-avoid1/approach_study.js --local exp/eval-r1 | --online data/online/baseline-r1
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const { geometry, listLocal, listOnline } = require('./ram_audit.js');
const argv = process.argv.slice(2);
const all = k => argv.map((x, i) => x === k ? argv[i + 1] : null).filter(Boolean);
const jobs = [...all('--local').flatMap(d => listLocal(path.resolve(ROOT, d), null)), ...all('--online').flatMap(d => listOnline(path.resolve(ROOT, d), 583))];
const acc = {};
for (const j of jobs) {
  const R = load(j.file), G = geometry(R.match.map), W = G.W, H = G.H;
  const man = (a, b) => { let dx = Math.abs(a % W - b % W), dy = Math.abs(((a / W) | 0) - ((b / W) | 0)); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
  const head = new Map(), len = new Map(), team = new Map();
  for (const d of R.match.map.initialDragons) { head.set(d.id, G.key(d.body[0].x, d.body[0].y)); len.set(d.id, d.body.length); team.set(d.id, d.team); }
  const watch = new Map();   // enemy id -> list of {ourId, enemyHeadBefore}
  const pendingOur = new Map(); // our id -> list of enemy ids watched at our decision
  let cur = -1;
  const k = j.info.opp; acc[k] = acc[k] || { n: 0, closer: 0, same: 0, farther: 0 };
  for (const e of R.events) {
    if (e.type === 'turnStart') cur = e.id;
    else if (e.type === 'dragonAction') {
      const id = e.id;
      // resolve watches on this enemy: its head before this action is head.get(id); resolution after its update (below)
      if (team.get(id) === j.us && len.get(id) >= 6) {
        const h = head.get(id), list = [];
        for (const [oid, oh] of head) if (team.get(oid) !== j.us && len.get(oid) < len.get(id) && G.cheb(h, oh) <= 3) list.push(oid);
        pendingOur.set(id, list);
      }
    } else if (e.type === 'dragonUpdate') {
      const id = e.id, prevHead = head.get(id);
      head.set(id, G.key(e.head.x, e.head.y));
      // length bookkeeping is approximate here (updates per step); exact enough for the < comparison
    } else if (e.type === 'dragonSplit') {
      head.set(e.childId, G.key(e.childBody[0].x, e.childBody[0].y)); len.set(e.childId, e.childBody.length); team.set(e.childId, e.team);
      len.set(e.parentId, e.parentBody.length);
    } else if (e.type === 'dragonDeath') { head.delete(e.id); len.delete(e.id); }
    else if (e.type === 'tileChange' && !e.hasPearl && len.has(cur)) len.set(cur, len.get(cur) + 1);
    if (e.type === 'turnStart') {
      // before an enemy acts: register watches from our dragons' latest decisions (our head is where our move left it)
      const id = e.id;
      if (team.get(id) !== j.us) for (const [oid, list] of pendingOur) if (list.includes(id) && head.has(oid)) {
        const w = watch.get(id) || []; w.push({ our: oid, before: head.get(id), ourHead: head.get(oid) }); watch.set(id, w);
        pendingOur.set(oid, list.filter(x => x !== id));
      }
    }
    if (e.type === 'turnStart' && watch.size) {
      // resolve watches of the dragon that acted just before (its head has been updated by now)
      for (const [eid, w] of watch) if (eid !== e.id && head.has(eid)) {
        for (const x of w) { const d0 = man(x.before, x.ourHead), d1 = man(head.get(eid), x.ourHead); const a = acc[k]; a.n++; if (d1 < d0) a.closer++; else if (d1 > d0) a.farther++; else a.same++; }
        watch.delete(eid);
      }
    }
  }
}
for (const [k, a] of Object.entries(acc).sort((x, y) => y[1].closer / y[1].n - x[1].closer / x[1].n)) console.log(k.padEnd(22), 'n', a.n, 'closer', (100 * a.closer / a.n).toFixed(1) + '%', 'farther', (100 * a.farther / a.n).toFixed(1) + '%');
