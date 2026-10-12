#!/usr/bin/env node
'use strict';
// fountain_online.js — online Autarky and Prisoners Dilemma games: who harvests the corridor fountains (cand-escape1 report).
// usage: node exp/cand-escape1/fountain_online.js baseline-r1 baseline-r1b baseline-r1c
//   Reads data/online/<set>/game-<id>.json and M<id>.replay (no network). Our team is the side whose botId is 10365.
//   Server replays hide spawn gaps, so the corridor fountains come from maps/online-20260927/<map>.map: tiles with a max
//   spawn gap <= 5 within one column of the team's start line (its longest start dragon is a vertical line).
//   Per team: natural spawns on its own fountains, natural and corpse pearls it ate there, natural pearls eaten elsewhere
//   (natural = initial or spawn tick, corpse = dropped by a death). A game "has our loop" when we ate >= 100 natural pearls
//   on our own fountains. Also the number of start dragons (Prisoners Dilemma comes as 6 or 10) and early splits of the
//   opponent's start dragon (rounds 0-10).
const path = require('path'), fs = require('fs');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const rows = [];
for (const set of process.argv.slice(2)) {
  const dir = path.join(ROOT, 'data/online', set);
  for (const f of fs.readdirSync(dir).filter(f => /^game-\d+\.json$/.test(f)).sort()) {
    const meta = JSON.parse(fs.readFileSync(path.join(dir, f)));
    if (!['Autarky', 'Prisoners Dilemma'].includes(meta.mapName)) continue;
    const R = load(path.join(dir, 'M' + meta.id + '.replay'));
    const M = R.match.map, W = M.width;
    const us = R.teams.A.botId === '10365' ? 'A' : 'B', them = us === 'A' ? 'B' : 'A';
    const mapFile = path.join(ROOT, 'maps/online-20260927', meta.mapName === 'Autarky' ? 'autarky.map' : 'prisoners_dilemma.map');
    const gaps = fs.readFileSync(mapFile, 'utf8').split('\n').filter(l => l.startsWith('TILE ')).map(l => l.trim().split(/\s+/).slice(1).map(Number));
    const longest = t => M.initialDragons.filter(d => d.team === t).sort((a, b) => b.body.length - a.body.length)[0];
    const fount = {};
    for (const t of ['A', 'B']) {
      const d = longest(t); fount[t] = new Set();
      if (!d.body.every(s => s.x === d.body[0].x)) continue;
      for (const [x, y, , mx] of gaps) if (mx >= 1 && mx <= 5 && Math.abs(x - d.body[0].x) <= 1) fount[t].add(y * W + x);
    }
    const team = new Map(); for (const d of M.initialDragons) team.set(d.id, d.team);
    const pearls = new Map(); let drop = false, round = -1, cur = -1;
    const st = { A: { natF: 0, corF: 0, natElse: 0, spawnsF: 0 }, B: { natF: 0, corF: 0, natElse: 0, spawnsF: 0 } };
    const early = { A: [], B: [] };
    for (const e of R.events) {
      if (drop && !(e.type === 'tileChange' && e.hasPearl)) drop = false;
      if (e.type === 'roundStart') round = e.round;
      else if (e.type === 'turnStart') cur = e.id;
      else if (e.type === 'dragonDeath') drop = true;
      else if (e.type === 'dragonSplit') { team.set(e.childId, e.team); if (round <= 10 && e.parentId === longest(e.team).id) early[e.team].push(round + ':' + (e.parentBody.length + e.childBody.length) + '>' + e.parentBody.length + '+' + e.childBody.length); }
      else if (e.type === 'tileChange') {
        const k = e.tile.y * W + e.tile.x;
        if (e.hasPearl) { pearls.set(k, drop ? 'c' : 'n'); for (const t of ['A', 'B']) if (!drop && round >= 0 && fount[t].has(k)) st[t].spawnsF++; }
        else { const o = pearls.get(k) || 'n'; pearls.delete(k); const t = team.get(cur); if (!t || round < 0) continue; if (fount[t].has(k)) { if (o === 'n') st[t].natF++; else st[t].corF++; } else if (o === 'n') st[t].natElse++; }
      }
    }
    rows.push({ set, id: meta.id, map: meta.mapName, dragons: M.initialDragons.length, opp: us === 'A' ? meta.teamBName : meta.teamAName, won: R.result.winner === us, us: st[us], them: st[them], oppEarly: early[them].join(' ') });
  }
}
const mean = a => a.reduce((s, x) => s + x, 0) / Math.max(1, a.length);
for (const r of rows) console.log(JSON.stringify(r));
for (const m of ['Autarky', 'Prisoners Dilemma']) {
  const rs = rows.filter(r => r.map === m), loop = rs.filter(r => r.us.natF >= 100), none = rs.filter(r => r.us.natF < 100);
  const f = (set, k) => `${mean(set.map(r => r.us[k])).toFixed(1)} : ${mean(set.map(r => r.them[k])).toFixed(1)}`;
  const tot = t => mean(rs.map(r => r[t].natF + r[t].natElse)).toFixed(1);
  console.log(`${m}: ${rs.length} games, wins ${rs.filter(r => r.won).length}. We : they — own-fountain natural spawns ${f(rs, 'spawnsF')}, natural eaten on own fountains ${f(rs, 'natF')}, corpse eaten on own fountains ${f(rs, 'corF')}, natural eaten elsewhere ${f(rs, 'natElse')}, natural eaten in all ${tot('us')} : ${tot('them')}`);
  console.log(`  with our loop: ${loop.length} games (start dragons ${[...new Set(loop.map(r => r.dragons))].join('/')}), wins ${loop.filter(r => r.won).length}; without: ${none.length} games (start dragons ${[...new Set(none.map(r => r.dragons))].join('/')}), wins ${none.filter(r => r.won).length}`);
}
