// check terrdb.hpp against the ledger territory of every online game of the given sets (any table map of the same name matches)
const fs = require('fs'), path = require('path'); const ROOT = path.resolve(__dirname, '..', '..');
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js')); const load = makeLoader(viewerSource());
const src = fs.readFileSync(path.join(__dirname, 'bot', 'terrdb.hpp'), 'utf8');
const rows = [...src.matchAll(/"([012]+)", \/\/ (\S+) \((\S+)\)/g)].map(m => ({ T: m[1], name: m[2].replace(/_/g, ' '), key: m[3] }));
let ok = 0, bad = 0; const badL = [];
for (const set of process.argv.slice(2)) { const dir = path.join(ROOT, 'data', 'online', set); const idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  for (const g of idx.games || idx) { const f = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
    let T = null; perGame(load(f), { map: '', variant: 'a' }, { turn(d, r, c) { if (!T) T = Array.from(c.terr).join(''); } });
    if (rows.some(r => r.name === g.mapName && r.T === T)) ok++; else { bad++; badL.push(set + ':' + g.gameId + ' ' + g.mapName); } } }
console.log('territory table matches', ok, 'mismatches', bad, badL.slice(0, 5).join(', '));
