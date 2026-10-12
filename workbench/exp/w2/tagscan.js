#!/usr/bin/env node
// W2: recognition tags in our indicators, per game: how many of our processes printed each " map=" state, and the first turn
// (relative to the process's first turn) of its first decided tag. Counts processes that ever printed map=none.
// usage: node exp/w2/tagscan.js <replay> ...
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const load = makeLoader(viewerSource());
const tot = {}; let games = 0;
for (const f of process.argv.slice(2)) {
  const us = /_B_\d+\//.test(f) ? 'B' : 'A';
  const R = load(f); games++;
  const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
  const seen = new Map();
  let round = 0;
  for (const e of R.events) {
    if (e.type === 'roundStart') round = e.round;
    if (e.type === 'dragonSplit') team.set(e.childId, e.team);
    if (e.type !== 'dragonIndicator' || team.get(e.id) !== us) continue;
    for (const m of (e.text || '').matchAll(/ ?map=(\S+)/g)) {
      const s = seen.get(e.id) || { states: [] }; seen.set(e.id, s);
      s.states.push(m[1] + '@' + round);
    }
  }
  const mapName = (/_(autarky|default|devil|portals|prisoners_dilemma|queen_of_spades|schooltime|slithery_fight|trauma|trophy|stronghold|arena|big_empty|Colosseum|default_small|dilemma)_[AB]_/.exec(f) || [])[1] || '?';
  const t = tot[mapName] = tot[mapName] || { games: 0, procs: 0, none: 0, noneAfterDecided: 0, decided: {}, ex: [] };
  t.games++;
  for (const [id, s] of seen) {
    t.procs++;
    const st = s.states.map(x => x.split('@')[0]);
    if (st.includes('none')) { t.none++; if (st.some(x => x !== 'none' && x !== '?')) { t.noneAfterDecided++; if (t.ex.length < 3) t.ex.push(`${path.basename(path.dirname(f))} id${id}: ${s.states.join(' ')}`); } }
    for (const x of st) if (x !== 'none' && x !== '?') t.decided[x] = (t.decided[x] || 0) + 1;
  }
}
for (const [m, t] of Object.entries(tot)) console.log(`${m.padEnd(18)} games ${t.games} processes ${t.procs} ever-none ${t.none} none-after-a-decision ${t.noneAfterDecided} decided-tags ${JSON.stringify(t.decided)} ${t.ex.join(' | ')}`);
