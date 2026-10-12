#!/usr/bin/env node
// v1.3 HV check (versions/v1.3/VERSION.md §3): our fountain-pocket economy per game with the Codex pocket study's own extractor
// (exp/pocket/extract.js analyse(): head episodes in pockets; natural / own drop / enemy drop pearls eaten inside, sprint cost, death lengths),
// summed over our team's episodes in fountain pockets: net = natural + drops eaten - sprint cost - death lengths (the study's rawNet), plus
// pocket deaths, our pocket drops recovered by us / the enemy, and the harvest tags (" hvs" split, " hv<p>i" inside turns) from the replay.
// usage: node exp/v13/pocketnet.js --sets name=dir[,dir] [--sets name2=dir] [--maps trauma,slithery_fight,slithery_fight_b] [--out file.md]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const S = require(path.join(ROOT, 'exp', 'spatial', 'lib.js'));
const { analyse } = require(path.join(ROOT, 'exp', 'pocket', 'extract.js'));
const NAME = { trauma: 'Trauma', slithery_fight: 'Slithery Fight', slithery_fight_b: 'Slithery Fight', prisoners_dilemma: 'Prisoners Dilemma', prisoners_dilemma_10: 'Prisoners Dilemma' };
const LAY = { trauma: 'a', slithery_fight: 'a', slithery_fight_b: 'b', prisoners_dilemma: '6', prisoners_dilemma_10: '10' };
const args = process.argv.slice(2), get = k => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const sets = []; for (let i = 0; i < args.length; i++) if (args[i] === '--sets') { const [nm, ds] = args[i + 1].split('='); sets.push({ name: nm, dirs: ds.split(',') }); }
const maps = (get('--maps') || 'trauma,slithery_fight,slithery_fight_b').split(','), out = get('--out');
function one(file, row) {
  const R = S.raw.load(file);
  // online sets (exp/online-eval) name both Slithery layouts "slithery_fight": the layout (and so the fountains) from the natural spawn support
  let lay = LAY[row.map];
  if (row.map === 'slithery_fight' && row.set) { const id = S.identify(R, { map: NAME[row.map], gameId: row.gameId || 0 }); if (id.layout === 'a' || id.layout === 'b') lay = id.layout; }
  const x = analyse(R, { key: row.key, map: NAME[row.map], localLayout: lay, src: 'local', us: row.side });
  const g = S.geometry(R.match.map, NAME[row.map], lay);
  const fountainPocket = new Set(g.pockets.filter(p => g.fountains.some(k => g.component[k] === p.id)).map(p => p.id));
  const us = row.side, eps = x.episodes.filter(e => e.team === us && fountainPocket.has(e.pocket));
  const sum = k => eps.reduce((a, e) => a + (e[k] || 0), 0);
  const deaths = x.deaths.filter(d => d.team === us && fountainPocket.has(d.pocket));
  const net = sum('natural') + sum('ownDrop') + sum('enemyDrop') - sum('sprintCost') - sum('deathLength');
  let hvs = 0, hvi = 0;
  const team = new Map(R.match.map.initialDragons.map(d => [d.id, d.team]));
  for (const e of R.events) {
    if (e.type === 'dragonSplit') team.set(e.childId, e.team);
    else if (e.type === 'dragonIndicator' && team.get(e.id) === us) { const t = e.text || ''; if (/ hvs\d/.test(t)) hvs++; if (/ hv\d+i\d/.test(t)) hvi++; }
  }
  return { key: row.key, map: row.map, won: R.result.winner === us ? 1 : 0, net, natural: sum('natural'), drops: sum('ownDrop') + sum('enemyDrop'), sprint: sum('sprintCost'),
    deathLen: sum('deathLength'), deaths: deaths.length, recOwn: deaths.reduce((a, d) => a + d.recoveredOwn, 0), recEnemy: deaths.reduce((a, d) => a + d.recoveredEnemy, 0),
    dropsLeft: deaths.reduce((a, d) => a + d.drops, 0), episodes: eps.length, hvs, hvi, final: R.result['team' + us].dragonCount > 0 ? R.result['team' + us].longestDragon : 0 };
}
const res = {};
for (const S0 of sets) {
  res[S0.name] = [];
  for (const dir of S0.dirs) {
    const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined && maps.includes(r.map));
    for (const r of rows) {
      const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
      try { res[S0.name].push(one(file, r)); } catch (e) { console.error(r.key, String(e.stack || e).slice(0, 200)); }
    }
  }
}
const names = sets.map(s => s.name);
const keys = n => new Set(res[n].map(r => r.key));
const common = [...keys(names[0])].filter(k => names.every(n => keys(n).has(k)));
const C = new Set(common);
const L = [`# v1.3 HV: fountain-pocket economy per game (${names.join(' vs ')})`, '', `Paired games: ${common.length}. Net = natural + drops eaten - sprint cost - death lengths over our episodes in fountain pockets (exp/pocket/extract.js). Local proxies: sanity only.`, ''];
L.push('| map | set | games | wins | net / game | natural / game | drops eaten | pocket deaths (length) / game | our pocket drops recovered us / enemy / left | harvest splits · inside turns / game | final longest |', '|---|---|---:|---:|---:|---:|---:|---|---|---|---:|');
for (const m of [...maps, 'all']) for (const n of names) {
  const rs = res[n].filter(r => C.has(r.key) && (m === 'all' || r.map === m)); if (!rs.length) continue;
  const mean = k => (rs.reduce((a, r) => a + r[k], 0) / rs.length);
  L.push(`| ${m} | ${n} | ${rs.length} | ${rs.reduce((a, r) => a + r.won, 0)} | ${mean('net').toFixed(1)} | ${mean('natural').toFixed(1)} | ${mean('drops').toFixed(1)} | ${mean('deaths').toFixed(1)} (${mean('deathLen').toFixed(1)}) | ${rs.reduce((a, r) => a + r.recOwn, 0)} / ${rs.reduce((a, r) => a + r.recEnemy, 0)} / ${rs.reduce((a, r) => a + r.dropsLeft - r.recOwn - r.recEnemy, 0)} | ${mean('hvs').toFixed(1)} · ${mean('hvi').toFixed(1)} | ${mean('final').toFixed(1)} |`);
}
const text = L.join('\n') + '\n';
if (out) fs.writeFileSync(out, text); process.stdout.write(text);
