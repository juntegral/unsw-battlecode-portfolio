// king and piece distances to the station Z per 20-round bucket (Z table from station.js, FRAC 2)
const cp = require('child_process'), fs = require('fs'), path = require('path');
const ROOT = require('path').resolve(__dirname, '..', '..');
const Z = { autarky: { A: [5, 9], B: [48, 8] }, default: { A: [7, 7], B: [24, 24] }, portals: { A: [2, 8], B: [29, 7] }, schooltime: { A: [21, 5], B: [38, 5] }, slithery_fight: { A: [15, 13], B: [47, 13] }, trauma: { A: [5, 15], B: [42, 8] } };
const [label, mapsArg] = process.argv.slice(2); const maps = mapsArg ? new Set(mapsArg.split(',')) : null;
const rows = fs.readFileSync(path.join(ROOT, 'exp', label, 'rows.jsonl'), 'utf8').trim().split('\n').map(JSON.parse).filter(r => r.G !== undefined && (!maps || maps.has(r.map)) && Z[r.map]);
const acc = {};
for (const r of rows) {
  const file = path.join(ROOT, 'exp', label, 'games', r.key.replace(/:/g, '_'), 'game.replay'); const z = Z[r.map][r.side];
  const out = cp.execFileSync('node', [path.join(__dirname, 'gtrace.js'), file, '--team', r.side, '--gather', '--zx', String(z[0]), '--zy', String(z[1])], { encoding: 'utf8', maxBuffer: 1 << 26 });
  const o = JSON.parse(out.trim().split('\n').pop());
  for (const [b, a] of Object.entries(o)) (acc[b] = acc[b] || []).push(...a);
}
const q = (a, p) => { const s = a.slice().sort((x, y) => x - y); return s[Math.floor(p * (s.length - 1))]; };
for (const b of [300, 320, 340, 360, 380, 400, 420, 440, 460, 480]) { const K = acc['K' + b] || [], P = acc['P' + b] || []; if (!K.length) continue;
  console.log(`${label} r${b}: king->Z med ${q(K, 0.5)} (p25 ${q(K, 0.25)}, p75 ${q(K, 0.75)}) | pieces->Z med ${q(P, 0.5)} within3 ${(100 * P.filter(x => x <= 3).length / P.length).toFixed(0)}% | pieces->king med ${q(acc[b] || [0], 0.5)}`); }
