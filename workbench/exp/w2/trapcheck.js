#!/usr/bin/env node
// W2 on the W8 recognition traps (maps/generated/gen_X_*: unseen maps with a known map's size, symmetry and start dragons): every decision is
// wrong. Per game and per our process: the first decided " map=<Name>/<l>" tag (round, start dragon or child), whether and how it reverted
// (a later " map=none": by a message when v1.6.1 printed " mn" that turn, else by the process's own contradiction), how many of its turns ran
// under the wrong decision, and what the wrong row switched on in those turns (engine label E=S / W / F, Portals module " pt", pocket harvest
// " hv", CONV2 " ck" / " cp" / " cy", swarm explosion / re-split / dispersal " sx" / " sr" / " sd"). Per map and side, and pooled per set.
// usage: node exp/w2/trapcheck.js <setDir> [...] [--games]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), SHOW = args.includes('--games');
const FEAT = { S: / E=S$/, W: / E=W$/, pt: / pt(?= |$)/, hv: / hv/, cv2: / c[kpy][#=0-9]/, sx: / sx(?= |$|\d)/, sr: / sr(?= |$|\d)/, sd: / sd/ };
for (const set of args.filter(a => !a.startsWith('--'))) {
  const rows = fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => r.G !== undefined && !r.error);
  const per = {};
  const pool = { games: 0, gamesWrong: 0, procs: 0, start: 0, child: 0, revMsg: 0, revOwn: 0, never: 0, wrongTurns: 0, feat: {} };
  for (const r of rows.sort((a, b) => a.key < b.key ? -1 : 1)) {
    const R = load(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'));
    const us = r.side, n0 = R.match.map.initialDragons.length;
    const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
    const P = new Map();   // id -> {dec, decRound, rev, revRound, viaMsg, turns, feat, died}
    let round = 0;
    for (const e of R.events) {
      if (e.type === 'roundStart') round = e.round;
      else if (e.type === 'dragonSplit') team.set(e.childId, e.team);
      else if (e.type === 'dragonDeath' && P.has(e.id)) { const p = P.get(e.id); if (p.dec && p.revRound === null) p.died = round; }
      else if (e.type === 'dragonIndicator' && team.get(e.id) === us) {
        const t = e.text || '';
        const m = /(?:^| )map=(\S+)/.exec(t);
        let p = P.get(e.id);
        if (m && m[1] !== 'none' && m[1] !== '?' && !p) { p = { dec: m[1], decRound: round, revRound: null, viaMsg: false, turns: 0, feat: {}, died: null }; P.set(e.id, p); }
        if (!p) continue;
        if (p.revRound === null) {
          if (m && m[1] === 'none') { p.revRound = round; p.viaMsg = / mn(?= |$)/.test(t); continue; }
          p.turns++;
          for (const [k, re] of Object.entries(FEAT)) if (re.test(t)) p.feat[k] = (p.feat[k] || 0) + 1;
        }
      }
    }
    const key = `${r.map} ${r.side}`, M = per[key] = per[key] || { games: 0, gamesWrong: 0, procs: 0, start: 0, child: 0, revMsg: 0, revOwn: 0, never: 0, wrongTurns: 0, maxTurns: 0, firstRound: null, maps: {}, feat: {} };
    M.games++; pool.games++;
    if (P.size) { M.gamesWrong++; pool.gamesWrong++; }
    for (const [id, p] of P) {
      for (const Q of [M, pool]) {
        Q.procs++; if (id < n0) Q.start++; else Q.child++;
        if (p.revRound !== null) { if (p.viaMsg) Q.revMsg++; else Q.revOwn++; } else Q.never++;
        Q.wrongTurns += p.turns;
        for (const [k, v] of Object.entries(p.feat)) Q.feat[k] = (Q.feat[k] || 0) + v;
      }
      M.maxTurns = Math.max(M.maxTurns, p.turns);
      M.firstRound = M.firstRound === null ? p.decRound : Math.min(M.firstRound, p.decRound);
      M.maps[p.dec] = (M.maps[p.dec] || 0) + 1;
    }
    if (SHOW && P.size) {
      const lines = [...P.entries()].slice(0, 8).map(([id, p]) => `#${id}${id < n0 ? '(start)' : ''} ${p.dec}@r${p.decRound} ${p.revRound !== null ? (p.viaMsg ? 'msg' : 'own') + '→none r' + p.revRound : p.died !== null ? 'died r' + p.died : 'never reverted'} turns ${p.turns} ${JSON.stringify(p.feat)}`);
      console.log(`  ${r.key}: ${P.size} wrong — ${lines.join(' | ')}${P.size > 8 ? ' …' : ''}`);
    }
  }
  console.log(`== ${set}: map side | games with a wrong decision | processes (start / child) | reverted by message / by own contradiction / never (death or end) | wrong turns (max per process) | first decision round | decided as | wrong-row turns: ${Object.keys(FEAT).join(' ')}`);
  for (const [k, M] of Object.entries(per).sort()) console.log(`${k.padEnd(12)} ${M.gamesWrong}/${M.games} | ${M.procs} (${M.start}/${M.child}) | ${M.revMsg}/${M.revOwn}/${M.never} | ${M.wrongTurns} (${M.maxTurns}) | r${M.firstRound ?? '-'} | ${JSON.stringify(M.maps)} | ${Object.keys(FEAT).map(f => M.feat[f] || 0).join(' ')}`);
  console.log(`POOLED       ${pool.gamesWrong}/${pool.games} | ${pool.procs} (${pool.start}/${pool.child}) | ${pool.revMsg}/${pool.revOwn}/${pool.never} | ${pool.wrongTurns} | | | ${Object.keys(FEAT).map(f => pool.feat[f] || 0).join(' ')}\n`);
}
