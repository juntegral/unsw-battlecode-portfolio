#!/usr/bin/env node
// W2: what the misrecognising processes did on an unseen map of a table size (stronghold = Trauma's size). Per set and game: our processes
// with a decided " map=<Name>/<l>" tag, the round of the decision, their turns with E=S after it, their length then and whether (and when)
// they died; and v1.6.1's gate tags. usage: node exp/w2/strongdetail.js <setDir> [<setDir> ...] [--map stronghold]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const args = process.argv.slice(2), mi = args.indexOf('--map'), MAP = mi >= 0 ? args[mi + 1] : 'stronghold';
const sets = args.filter((a, i) => !a.startsWith('--') && (mi < 0 || i !== mi + 1));
const load = makeLoader(viewerSource());
for (const set of sets) {
  const rowsF = path.join(ROOT, set, 'rows.jsonl'); if (!fs.existsSync(rowsF)) continue;
  const rows = fs.readFileSync(rowsF, 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => r.map === MAP && r.G !== undefined && !r.error);
  let games = 0, gamesMis = 0, procs = 0, sTurns = 0, died10 = 0, died = 0, decRounds = [], lens = [];
  const tags = { mg: 0, ms: 0, mn: 0, mc: 0 };
  for (const r of rows.sort((a, b) => a.key < b.key ? -1 : 1)) {
    const R = load(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'));
    const us = r.side, team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
    const dec = new Map(), sT = new Map(), deadAt = new Map(), len = new Map();
    let round = 0;
    for (const e of R.events) {
      if (e.type === 'roundStart') round = e.round;
      else if (e.type === 'dragonSplit') team.set(e.childId, e.team);
      else if (e.type === 'dragonDeath' && team.get(e.id) === us) deadAt.set(e.id, round);
      else if (e.type === 'dragonIndicator' && team.get(e.id) === us) {
        const t = e.text || '';
        for (const x of t.matchAll(/(?:^| )(mg=\S+|ms\d+|mn|mc)(?= |$)/g)) tags[x[1].slice(0, 2)]++;
        const m = /(?:^| )map=(\S+)/.exec(t);
        if (m && m[1] !== 'none' && m[1] !== '?' && !dec.has(e.id)) { dec.set(e.id, round); const L = / L(\d+)/.exec(t); len.set(e.id, L ? +L[1] : null); }
        if (dec.has(e.id) && / E=S$/.test(t)) sT.set(e.id, (sT.get(e.id) || 0) + 1);
      }
    }
    games++; if (dec.size) gamesMis++;
    const lines = [];
    for (const [id, r0] of dec) {
      procs++; sTurns += sT.get(id) || 0; decRounds.push(r0); if (len.get(id) !== null) lens.push(len.get(id));
      const d = deadAt.get(id); if (d !== undefined) { died++; if (d - r0 <= 10) died10++; }
      if (lines.length < 6) lines.push(`#${id} r${r0}${len.get(id) ? ' L' + len.get(id) : ''} S-turns ${sT.get(id) || 0}${d !== undefined ? ' died r' + d : ''}`);
    }
    console.log(`${path.basename(set)} ${r.key}: ${r.won ? 'W' : 'L'} G ${r.G} vs ${r.theirLongest}${r.alive ? '' : ' (eliminated)'}; misrecognising ${dec.size}${dec.size ? ': ' + lines.join(', ') + (dec.size > 6 ? ' …' : '') : ''}`);
  }
  const med = a => { const s = a.slice().sort((x, y) => x - y); return s.length ? s[s.length >> 1] : '-'; };
  console.log(`== ${set} on ${MAP}: games with misrecognition ${gamesMis}/${games}; processes ${procs}; their E=S turns ${sTurns}; died ${died} (within 10 rounds of the decision ${died10}); decision round median ${med(decRounds)}; length then median ${med(lens)}; gate tags ${JSON.stringify(tags)}\n`);
}
