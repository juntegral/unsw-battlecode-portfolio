#!/usr/bin/env node
// Q3 detail: on Autarky, how did our final king's line grow in wins vs losses (g4 family, elite opponents)? Re-reads the replays.
// For the final king's line (the dragon and its ancestors): the rounds it reached length 20 / 40, the unexplored-portal entries
// (label "PORTAL?") and escape splits (label "escape-split") made by the line while it was our longest, and our other dragons'
// count of those. The corridor loop (the start dragon of length 14 in a walled lane) is reported apart: its escape splits.
// usage: node exp/eliminations/autarky_king.js [--map Autarky]
'use strict';
const path = require('path');
const L = require('./lib.js'), X = require('./extract.js');
const { makeLoader, viewerSource } = require(path.join(L.ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(L.ROOT, 'tools', 'mass_ledger.js'));
const argv = process.argv.slice(2), mapName = argv.includes('--map') ? argv[argv.indexOf('--map') + 1] : 'Autarky';
const load = makeLoader(viewerSource());
const G = L.loadOnline().filter(g => g.fam === 'g4' && g.elite && g.map === mapName);
const rows = [];
for (const g of G) {
  const t = X.onlineTasks(g.set).find(x => x.gameId === g.gameId);
  const R = load(t.file), us = g.us;
  const parent = new Map(), born = new Map(), lab = new Map(), reach = new Map(), bornLen = new Map();
  let finalKing = -1;
  perGame(R, { map: g.map }, {
    turn(d, r, c) { if (d.team !== us) return; if (!born.has(d.id)) { born.set(d.id, d.born); parent.set(d.id, d.parent); bornLen.set(d.id, d.body.length); }
      const x = reach.get(d.id) || {}; if (d.body.length >= 20 && x.r20 === undefined) x.r20 = r; if (d.body.length >= 40 && x.r40 === undefined) x.r40 = r; reach.set(d.id, x); },
    indicator(e, r, c) { const d = c.drag.get(e.id); if (!d || d.team !== us) return; const k = c.kingOf(us) === d ? 'K' : 'o'; const m = lab.get(e.id) || { Kp: 0, Ke: 0, op: 0, oe: 0 };
      if (/PORTAL\?/.test(e.text)) m[k === 'K' ? 'Kp' : 'op']++; if (/^escape-split/.test(e.text)) m[k === 'K' ? 'Ke' : 'oe']++; lab.set(e.id, m); },
    split(p, ch, e, r) { if (p.team === us) { born.set(ch.id, r); parent.set(ch.id, p.id); } },
    end(n, c) { const k = c.kingOf(us); finalKing = k ? k.id : -1; },
  });
  const line = []; for (let x = finalKing; x !== undefined && x >= 0; x = parent.get(x)) line.push(x);
  const sumL = f => line.reduce((s, id) => s + ((lab.get(id) || {})[f] || 0), 0);
  let r20 = null, r40 = null; for (const id of line.slice().reverse()) { const x = reach.get(id) || {}; if (r20 === null && x.r20 !== undefined) r20 = x.r20; if (r40 === null && x.r40 !== undefined) r40 = x.r40; }
  let othP = 0, othE = 0; for (const [id, m] of lab) if (!line.includes(id)) { othP += m.Kp + m.op; othE += m.Ke + m.oe; }
  rows.push({ key: g.key, win: g.win, opp: g.oppName, gen: line.length - 1, root: line[line.length - 1], rootLen: bornLen.get(line[line.length - 1]), kingP: sumL('Kp'), kingE: sumL('Ke'), lineP: sumL('op'), lineE: sumL('oe'), r20, r40,
    ourK: g.U.end.k, theirK: g.E.end.k });
}
const S = w => rows.filter(x => x.win === w);
const m = (xs, f) => xs.length ? (xs.reduce((s, x) => s + f(x), 0) / xs.length).toFixed(2) : '–';
for (const w of [1, 0]) {
  const X2 = S(w);
  console.log(`${mapName} ${w ? 'wins' : 'losses'} ${X2.length}: final king line gen ${m(X2, x => x.gen)}, root = a start dragon of length 3 ${X2.filter(x => x.rootLen === 3).length}, of length 14 ${X2.filter(x => x.rootLen === 14).length}; ` +
    `line's PORTAL? while king ${m(X2, x => x.kingP)}, while not king ${m(X2, x => x.lineP)}; line's escape splits while king ${m(X2, x => x.kingE)}, not king ${m(X2, x => x.lineE)}; ` +
    `line reached L20 at r${m(X2.filter(x => x.r20 !== null), x => x.r20)} (${X2.filter(x => x.r20 !== null).length}), L40 at r${m(X2.filter(x => x.r40 !== null), x => x.r40)} (${X2.filter(x => x.r40 !== null).length}); final ours ${m(X2, x => x.ourK)} theirs ${m(X2, x => x.theirK)}`);
}
console.log(JSON.stringify(rows.filter(x => !x.win).slice(0, 40).map(x => [x.key.split(':')[1], x.opp.slice(0, 8), 'gen' + x.gen, 'root L' + x.rootLen, 'P' + x.kingP + '/' + x.lineP, 'E' + x.kingE + '/' + x.lineE, 'r20:' + x.r20, 'r40:' + x.r40, x.ourK + ':' + x.theirK])));
