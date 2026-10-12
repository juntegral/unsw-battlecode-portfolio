// v1 final item 5b check: on Autarky and PD6 (prisoners_dilemma, a layout) our r100 heads (ledger st.units[10]) and r250 total length
// (st.total[25]) and final longest, per bot set, same keys
const fs = require('fs'), path = require('path');
const ML = require('../../tools/mass_ledger.js');
const { makeLoader, viewerSource } = require('../../tools/top_features.js');
const load = makeLoader(viewerSource());
const NAME = { autarky: 'Autarky', prisoners_dilemma: 'Prisoners Dilemma' };
for (const dir of process.argv.slice(2)) {
  const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined && NAME[r.map] && r.opp === 'proxy4_king');
  const by = {};
  for (const r of rows) {
    const f = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
    const R = load(f); const info = { map: NAME[r.map] }; if (info.map === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
    const g = ML.perGame(R, info); const T = g[r.side];
    const b = by[r.map] || (by[r.map] = []); b.push({ key: r.key, u100: T.st.units[10], m250: T.st.total[25], king: T.st.king[50], won: r.won });
  }
  for (const [m, a] of Object.entries(by)) {
    const mean = k => (a.reduce((s, x) => s + x[k], 0) / a.length).toFixed(1);
    console.log(`${path.basename(dir)} ${m}: games ${a.length}, r100 heads ${mean('u100')}, r250 mass ${mean('m250')}, final longest ${mean('king')}, wins ${a.filter(x => x.won).length}`);
  }
}
