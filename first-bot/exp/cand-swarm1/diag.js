#!/usr/bin/env node
// Diagnostics of our bot's side over every game of an eval.js label (exp/<label>/games/*/game.replay + rows.jsonl).
// usage: node exp/cand-swarm1/diag.js <label> [--maps a,b] [--json <file>]
// Per game: our deaths by (reason : last indicator kind), per 100-round window; our splits by kind (swarm / policy /
// escape); feeds; trades we chose (indicator TRADE); units / longest at r100, r200, r300, r400, r500 (running games).
// Reasons: W kelp, S own body, O other body, H head-on, A no valid action.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
const loader = tf.makeLoader(tf.viewerSource());
const label = process.argv[2];
const onlyMaps = process.argv.includes('--maps') ? process.argv[process.argv.indexOf('--maps') + 1].split(',') : null;
const jsonOut = process.argv.includes('--json') ? process.argv[process.argv.indexOf('--json') + 1] : null;
const dir = path.join(ROOT, 'exp', label);
const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined);
const kind = t => {
  if (!t) return 'none';
  const w = t.split(' ')[0];
  if (/^[NESW]+$/.test(w)) { if (t.includes('TRADE')) return 'trade'; return w.length > 1 ? 'sprint' : 'move'; }
  return w.replace(/[-]?\d+$/, '');
};
const agg = { games: 0, deaths: {}, deathsW: {}, splits: {}, feeds: 0, trades: 0, tradeDeaths: 0, snap: {} };
const add = (o, k, v = 1) => { o[k] = (o[k] || 0) + v; };
const perGame = [];
const snaps = { 100: [], 200: [], 300: [], 400: [], 500: [] };
for (const r of rows) {
  if (onlyMaps && !onlyMaps.includes(r.map)) continue;
  const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay');
  if (!fs.existsSync(file)) continue;
  const R = loader(file), M = R.match.map, side = r.side;
  { const f = tf.extract(R, { map: r.map, teamA: 'A', teamB: 'B' }); const tl = f[r.side].timeline;
    for (const rr of [100, 200, 300, 400, 500]) { const t = tl.find(x => x.r === rr) || (rr === 500 && f.meta.rounds >= 499 ? tl[tl.length - 1] : null); if (t) snaps[rr].push([t.units, t.longest, t.total]); } }
  const team = new Map(), len = new Map();
  for (const d of M.initialDragons) { team.set(d.id, d.team); len.set(d.id, d.body.length); }
  let round = 0; const last = new Map(); const g = { key: r.key, map: r.map, deaths: {}, splits: {}, feeds: 0, trades: 0, snap: {} };
  const snapAt = new Set([100, 200, 300, 400]);
  const snap = rr => { let u = 0, L = 0; for (const [id, t] of team) if (t === side && len.has(id)) { u++; L = Math.max(L, len.get(id)); } g.snap[rr] = [u, L]; };
  for (const e of R.events) {
    if (e.type === 'roundStart') { if (snapAt.has(e.round)) snap(e.round); round = e.round; }
    else if (e.type === 'dragonSplit') {
      team.set(e.childId, e.team); len.set(e.parentId, e.parentBody.length); len.set(e.childId, e.childBody.length);
      if (e.team === side) { const k = kind(last.get(e.parentId)); add(g.splits, k); add(agg.splits, k); }
    }
    else if (e.type === 'dragonUpdate') { /* length changes are tracked through eat/sprint below */ }
    else if (e.type === 'dragonIndicator' && team.get(e.id) === side) {
      last.set(e.id, e.text); const k = kind(e.text);
      if (k === 'feed') { g.feeds++; agg.feeds++; }
      if (k === 'trade') { g.trades++; agg.trades++; }
    }
    else if (e.type === 'dragonDeath') {
      if (team.get(e.id) === side) {
        const k = e.reason + ':' + kind(last.get(e.id)); add(g.deaths, k); add(agg.deaths, k);
        const w = Math.min(4, Math.floor(round / 100)) * 100; agg.deathsW[w] = agg.deathsW[w] || {}; add(agg.deathsW[w], k);
        if (kind(last.get(e.id)) === 'trade' && e.reason === 'H') agg.tradeDeaths++;
      }
      len.delete(e.id);
    }
  }
  // lengths: rebuild from replay result for the end snapshot
  g.snap[500] = [r.units ?? 0, r.G];
  agg.games++; perGame.push(g);
}
const med = a => { if (!a.length) return null; const s = a.slice().sort((x, y) => x - y); const m = (s.length - 1) / 2; return (s[Math.floor(m)] + s[Math.ceil(m)]) / 2; };
console.log(`${label}: ${agg.games} games${onlyMaps ? ' maps ' + onlyMaps.join(',') : ''}`);
console.log('median over running games (units / longest / total):', Object.entries(snaps).map(([rr, a]) => `r${rr} ${med(a.map(x => x[0]))}/${med(a.map(x => x[1]))}/${med(a.map(x => x[2]))} (${a.length})`).join('  '));
const per = o => Object.entries(o).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${(v / agg.games).toFixed(2)}`).join(', ');
console.log('splits per game:', per(agg.splits));
console.log('feeds per game:', (agg.feeds / agg.games).toFixed(2), ' chosen trades per game:', (agg.trades / agg.games).toFixed(2));
console.log('deaths per game:', per(agg.deaths));
for (const w of Object.keys(agg.deathsW).map(Number).sort((a, b) => a - b)) console.log(`  r${w}-${w + 99}:`, per(agg.deathsW[w]));
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify({ agg, snaps, perGame }, null, 1));
