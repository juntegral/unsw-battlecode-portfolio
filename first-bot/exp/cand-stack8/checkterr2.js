const fs = require('fs'), path = require('path'); const ROOT = path.resolve(__dirname, '..', '..');
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js')); const load = makeLoader(viewerSource());
const src = fs.readFileSync(path.join(__dirname, 'bot', 'terrdb.hpp'), 'utf8');
const rows = [...src.matchAll(/"([012]+)", \/\/ (\S+) \((\S+)\)/g)].map(m => ({ T: m[1], name: m[2].replace(/_/g, ' '), key: m[3] }));
const sw = T => T.replace(/[12]/g, c => c === '1' ? '2' : '1');
const res = {};
for (const set of process.argv.slice(2)) { const dir = path.join(ROOT, 'data', 'online', set); const idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  for (const g of (idx.games || idx).slice(0, 200)) { const f = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
    const R = load(f); let T = null; perGame(R, { map: '', variant: 'a' }, { turn(d, r, c) { if (!T) T = Array.from(c.terr).join(''); } });
    const same = rows.some(r => r.name === g.mapName && r.T === T), swapped = rows.some(r => r.name === g.mapName && sw(r.T) === T);
    const k = `${g.mapName} ours=${g.ourSide}: ${same ? 'same' : swapped ? 'SWAPPED' : 'other'}`; res[k] = (res[k] || 0) + 1;
    const d0 = R.match.map.initialDragons[0]; if (!res['ex:' + g.mapName + g.ourSide]) res['ex:' + g.mapName + g.ourSide] = JSON.stringify({ team: d0.team, head: d0.body[0] }); } }
for (const k of Object.keys(res).sort()) console.log(k, res[k]);
