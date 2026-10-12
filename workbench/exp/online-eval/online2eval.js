// Turn online sets (data/online/<set>) into a tools/eval.js-style directory (rows.jsonl + games/<key>/game.replay symlinks), so the
// v1 local tools (exp/v1/local_report.js, exp/v1/spatial.js) run on online games. Key = <opponent>:<mapfile>:<replicate>, where the
// replicate is the set's position in the list; top-6 and DEV 545 only. Sides differ between replicates, so keys carry no side.
// usage: node online2eval.js <set>[,<set>...] <outDir>
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = '~/01. Project/개인 프로젝트/unsw-swarm';
const [setsArg, out] = process.argv.slice(2);
const FILE = { 'Autarky': 'autarky', 'Default': 'default', 'Devil': 'devil', 'Portals': 'portals', 'Prisoners Dilemma': 'prisoners_dilemma',
  'Queen Of Spades': 'queen_of_spades', 'Schooltime': 'schooltime', 'Slithery Fight': 'slithery_fight', 'Trauma': 'trauma', 'Trophy': 'trophy' };
const KEEP = new Set([306, 70, 20, 801, 264, 46, 545]);
fs.mkdirSync(path.join(out, 'games'), { recursive: true });
const rows = []; const seen = new Map();
setsArg.split(',').forEach((set, si) => {
  const dir = path.join(ROOT, 'data', 'online', set);
  const idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  for (const g of idx.games) {
    if (!KEEP.has(g.opponentTeam)) continue;
    const rep = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(rep)) continue;
    let res; try { res = JSON.parse(fs.readFileSync(path.join(dir, 'game-' + g.gameId + '.json'), 'utf8')).replay.result; } catch (e) { continue; }
    const mf = FILE[g.mapName]; if (!mf) continue;
    let key = `${g.opponentTeam}:${mf}:${si + 1}`; const n = (seen.get(key) || 0) + 1; seen.set(key, n); if (n > 1) key += 'x' + n;
    const us = res['team' + g.ourSide], them = res['team' + (g.ourSide === 'A' ? 'B' : 'A')];
    rows.push({ key, opp: String(g.opponentTeam), map: mf, side: g.ourSide, seed: g.gameId, exit: 0, G: us.longestDragon, alive: us.dragonCount > 0,
      total: us.totalLength, units: us.dragonCount, theirLongest: them.longestDragon, won: g.ourWin === true, endReason: res.endReason, set });
    const gd = path.join(out, 'games', key.replace(/:/g, '_')); fs.mkdirSync(gd, { recursive: true });
    const link = path.join(gd, 'game.replay'); try { fs.unlinkSync(link); } catch (e) { /* none */ }
    fs.symlinkSync(rep, link);
  }
});
fs.writeFileSync(path.join(out, 'rows.jsonl'), rows.map(r => JSON.stringify(r)).join('\n') + '\n');
console.log(`${rows.length} games -> ${out}`);
