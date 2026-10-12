#!/usr/bin/env node
// cand-stack11 local helper: count our stack11 tags (gh, ghd, kx, kxm, lwk) and a few neighbours in local replays, with the
// per-turn instruction maximum of our side. Firing and safety only (the gates are tools/mech_check.js's stack11 section).
// usage: node exp/cand-stack11/tags.js <game.replay | eval folder> [...]
'use strict';
const fs = require('fs'), path = require('path');
const { load } = require(path.resolve(__dirname, '..', '..', 'tools', 'replay.js'));
const files = [];
for (const a of process.argv.slice(2)) {
  const p = path.resolve(a);
  if (fs.statSync(p).isDirectory()) {
    const g = path.join(p, 'games');
    if (fs.existsSync(g)) for (const d of fs.readdirSync(g)) { const f = path.join(g, d, 'game.replay'); if (fs.existsSync(f)) files.push(f); }
    else { const f = path.join(p, 'game.replay'); if (fs.existsSync(f)) files.push(f); }
  } else files.push(p);
}
const tot = { games: 0, turns: 0, labelled: 0, gh: 0, ghd: 0, kx: 0, kxm: 0, lwk: 0, g: 0, feed: 0, conv: 0, grab: 0, maxInstr: 0, degraded: 0, over: 0, kxd: {} };
const per = [];
for (const f of files) {
  let R; try { R = load(f); } catch (e) { console.error('load', f, String(e).slice(0, 80)); continue; }
  const init = R.match && R.match.map ? R.match.map.initialDragons : [];
  // our team: the side whose indicators carry the seed0 move label format (both sides label in a mirror game; count all)
  const team = new Map(); for (const d of init) team.set(d.id, d.team);
  const o = { f: path.relative(process.cwd(), f), gh: 0, ghd: 0, kx: 0, kxm: 0, lwk: 0, turns: 0, maxInstr: 0 };
  for (const e of R.events) {
    if (e.type === 'dragonSplit') team.set(e.childId, e.team);
    if (e.type === 'dragonIndicator') {
      const s = e.text || ''; tot.labelled++;
      if (/^feed #\d+ d\d+ L\d+ conv/.test(s)) tot.conv++; else if (/^feed #/.test(s)) tot.feed++;
      if (/^degraded/.test(s)) tot.degraded++;
      const head = s.split('|')[0];
      for (const t of head.split(/\s+/)) {
        if (t === 'gh') { o.gh++; tot.gh++; }
        else if (/^ghd@\d+,\d+$/.test(t)) { o.ghd++; tot.ghd++; }
        else if (/^kx\d+$/.test(t)) { o.kx++; tot.kx++; const d = t.slice(2); tot.kxd[d] = (tot.kxd[d] || 0) + 1; }
        else if (t === 'kxm') { o.kxm++; tot.kxm++; }
        else if (t === 'lwk') { o.lwk++; tot.lwk++; }
        else if (/^g\d+$/.test(t)) tot.g++;
        else if (/^grab@/.test(t)) tot.grab++;
      }
    }
    if (e.type === 'dragonAction' || e.instructions) {
      const n = e.instructions && (e.instructions.count || 0);
      if (n) { if (n > o.maxInstr) o.maxInstr = n; if (n > 80e6) tot.over++; }
    }
  }
  tot.games++; tot.maxInstr = Math.max(tot.maxInstr, o.maxInstr);
  per.push(o);
}
for (const o of per) console.log(`${o.f}: gh ${o.gh} ghd ${o.ghd} kx ${o.kx} kxm ${o.kxm} lwk ${o.lwk} maxInstr ${(o.maxInstr / 1e6).toFixed(1)}M`);
console.log(JSON.stringify(tot));
