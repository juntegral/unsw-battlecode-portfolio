// run gtrace over games of a label (our side) and summarise distances of small pieces to the king per 20-round bucket
const cp = require('child_process'), fs = require('fs'), path = require('path');
const ROOT = require('path').resolve(__dirname, '..', '..');
const [label, mapsArg] = process.argv.slice(2); const maps = mapsArg ? new Set(mapsArg.split(',')) : null;
const rows = fs.readFileSync(path.join(ROOT, 'exp', label, 'rows.jsonl'), 'utf8').trim().split('\n').map(JSON.parse).filter(r => r.G !== undefined && (!maps || maps.has(r.map)));
const acc = {};
for (const r of rows) {
  const file = path.join(ROOT, 'exp', label, 'games', r.key.replace(/:/g, '_'), 'game.replay');
  const out = cp.execFileSync('node', [path.join(__dirname, 'gtrace.js'), file, '--team', r.side, '--gather'], { encoding: 'utf8', maxBuffer: 1 << 26 });
  const o = JSON.parse(out.trim().split('\n').pop());
  for (const [b, a] of Object.entries(o)) (acc[b] = acc[b] || []).push(...a);
}
const q = (a, p) => { const s = a.slice().sort((x, y) => x - y); return s[Math.floor(p * (s.length - 1))]; };
for (const b of Object.keys(acc).map(Number).sort((a, b) => a - b)) console.log(`${label} r${b}-${b + 19}: samples ${acc[b].length} dist p25 ${q(acc[b], 0.25)} med ${q(acc[b], 0.5)} p75 ${q(acc[b], 0.75)}  within3 ${(100 * acc[b].filter(x => x <= 3).length / acc[b].length).toFixed(0)}%`);
