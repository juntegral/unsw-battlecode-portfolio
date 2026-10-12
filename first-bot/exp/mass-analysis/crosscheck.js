#!/usr/bin/env node
// crosscheck.js — recompute a few numbers published by earlier tools from the mass-ledger cache, as an independent check.
// usage: node exp/mass-analysis/crosscheck.js [--top top-sample] [--keys data/top/snapshot-20260929a.keys]
//   With the snapshot keys it covers the same games as research/observations/top-timing.md and top-decisions.md.
// Compared numbers (all top-vs-top, SSS games excluded as in those documents):
//   - pearls eaten per team-game (all origins) and dragon-turns per team-game (top-decisions.md 3.1: 710.7 and 8,680)
//   - share of the king's pearls that come from own voluntary deaths in r400-499 (top-summary: 50.6%)
//   - deaths with a free neighbour that are self-inflicted, per team-game (top-summary: 30.9)
//   - data/top/features.jsonl: per game and team, total eaten / splits / deaths vs this cache (differences expected 0)
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const { FI, ORIG } = ML;
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const keys = new Set(fs.readFileSync(path.resolve(ROOT, opt('keys', 'data/top/snapshot-20260929a.keys')), 'utf8').split('\n').map(s => s.trim()).filter(Boolean));
const games = [];
for (const l of fs.readFileSync(path.join(ML.CACHE, opt('top', 'top-sample') + '.jsonl'), 'utf8').split('\n')) {
  if (!l.trim()) continue; let g; try { g = JSON.parse(l); } catch { continue; }
  if (keys.has(g.key)) games.push(g);
}
const main = games.filter(g => g.teamA !== 'SSS' && g.teamB !== 'SSS');
const sum = a => a.reduce((s, x) => s + x, 0);
let eaten = 0, turns = 0, tg = 0, kingAll = 0, kingSac = 0, volSelf = 0;
for (const g of main) for (const s of ['A', 'B']) {
  const T = g[s]; tg++;
  for (const o of ORIG) eaten += sum(T.fl[FI['eat_' + o]]);
  turns += sum(T.fl[FI.turns]);
  for (let b = 40; b < 50; b++) { for (const o of ORIG) kingAll += T.fl[FI['keat_' + o]][b]; kingSac += T.fl[FI.keat_oSac][b]; }
  volSelf += sum(T.fl[FI.dn_sac]);
}
console.log(`games in cache matching keys: ${games.length} (without SSS: ${main.length}), team-games ${tg}`);
console.log(`pearls eaten per team-game ${(eaten / tg).toFixed(1)} (top-decisions.md: 710.7); dragon-turns per team-game ${(turns / tg).toFixed(0)} (8,680)`);
console.log(`king pearls from own sacrifices r400-499: ${(100 * kingSac / kingAll).toFixed(1)}% (top-summary: 50.6%, 'voluntary' = free>0 self-kill incl. ally collisions)`);
console.log(`self-inflicted deaths with a free neighbour per team-game: ${(volSelf / tg).toFixed(1)} (top-summary: 30.9)`);
// features.jsonl per game and team: eaten per 50-round window, splits, deaths
const feats = new Map();
for (const l of fs.readFileSync(path.join(ROOT, 'data', 'top', 'features.jsonl'), 'utf8').split('\n')) {
  const m = /^\{"meta":\{"battleId":(\d+),"gameId":(\d+)[,}]/.exec(l); if (!m) continue;
  const k = m[1] + ':' + m[2]; if (!keys.has(k)) continue;
  feats.set(k, JSON.parse(l));
}
let cmp = 0, dEat = 0, dSplit = 0, dDeath = 0, dFinal = 0;
for (const g of games) {
  const f = feats.get(g.key); if (!f) continue; cmp++;
  for (const s of ['A', 'B']) {
    const T = g[s];
    let e = 0; for (const o of ORIG) e += sum(T.fl[FI['eat_' + o]]);
    if (e !== sum(f[s].eaten)) dEat++;
    if (sum(T.fl[FI.split_n]) !== f[s].splits.length) dSplit++;
    let dn = 0; for (const c of ML.CAUSE) dn += sum(T.fl[FI['dn_' + c]]);
    if (dn !== f[s].deaths.length) dDeath++;
    const tl = f[s].timeline[f[s].timeline.length - 1];
    if (tl.total !== T.st.total[50] || tl.longest !== T.st.king[50] || tl.units !== T.st.units[50]) dFinal++;
  }
}
console.log(`features.jsonl comparison: ${cmp} games; team-games differing in eaten ${dEat}, splits ${dSplit}, deaths ${dDeath}, final state ${dFinal} (all expected 0)`);
