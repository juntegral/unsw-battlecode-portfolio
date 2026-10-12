#!/usr/bin/env node
// divergence.js — first event where a candidate game departs from its baseline game (same key), and what our dragon
// was doing then (from the candidate's indicator: escape tag, length). Also counts escape moves and trust-mode turns.
// usage: node exp/cand-avoid1/divergence.js <baseline label> <candidate label>
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const [bl, cl] = process.argv.slice(2);
const js = e => JSON.stringify(e, (k, v) => typeof v === 'bigint' ? v.toString() : v);
const cat = {}, byOpp = {};
for (const g of fs.readdirSync(path.join(ROOT, 'exp', cl, 'games')).sort()) {
  const fb = path.join(ROOT, 'exp', bl, 'games', g, 'game.replay'), fc = path.join(ROOT, 'exp', cl, 'games', g, 'game.replay');
  if (!fs.existsSync(fb) || !fs.existsSync(fc)) continue;
  const A = load(fb), B = load(fc);
  const ev = R => R.events.filter(e => e.type !== 'dragonIndicator' && e.type !== 'pearlCountdown' && e.type !== 'dragonLog');
  const a = ev(A), b = ev(B); let round = -1, i = 0; const n = Math.min(a.length, b.length);
  for (; i < n; i++) { if (a[i].type === 'roundStart') round = a[i].round; if (js(a[i]) !== js(b[i])) break; }
  const opp = g.replace(/_(autarky|default|devil|portals|prisoners_dilemma|queen_of_spades|schooltime|slithery_fight|trauma|trophy)_[AB]_\d+$/, '');
  const o = byOpp[opp] = byOpp[opp] || { games: 0, esc: 0, trust: 0, bigTurns: 0 }; o.games++;
  for (const e of B.events) if (e.type === 'dragonIndicator') { if (/ esc/.test(e.text)) o.esc++; if (/ T$/.test(e.text)) o.trust++; const m = / L(\d+)/.exec(e.text); if (m && +m[1] >= 6) o.bigTurns++; }
  let k;
  if (i >= n) k = 'identical';
  else {
    const id = b[i].id ?? b[i].senderId ?? b[i].parentId; let ind = null, r = -1;
    for (const e of B.events) { if (e.type === 'roundStart') r = e.round; if (r === round && e.type === 'dragonIndicator' && e.id === id) ind = e.text; }
    const L = ind && / L(\d+)/.exec(ind) ? +/ L(\d+)/.exec(ind)[1] : null;
    k = ind && / esc/.test(ind) ? 'escape move' : L != null && L >= 6 ? 'long dragon, other move' : 'short dragon or no indicator';
  }
  cat[k] = (cat[k] || 0) + 1;
}
console.log('first divergence:', JSON.stringify(cat));
console.log('per opponent (escape moves, trust-mode turns, long-dragon turns):', JSON.stringify(byOpp));
