// draw a map file: kelp edges, portals (letters by id), spawn classes (digit = palette index; . never)
const fs = require('fs');
const f = process.argv[2];
const L = fs.readFileSync(f, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
let W, H; const tiles = {}, hk = new Set(), vk = new Set(), hp = new Map(), vp = new Map(); const pal = new Map();
for (const l of L) { const t = l.split(/\s+/); if (t[0] === 'MAP') { W = +t[1]; H = +t[2]; } }
for (const l of L) { const t = l.split(/\s+/);
  if (t[0] === 'TILE') { const k = t[3] + '-' + t[4]; if (!pal.has(k)) pal.set(k, pal.size); tiles[t[1] + ',' + t[2]] = k; }
  if (t[0] === 'EDGE') { const i = +t[1], kind = +t[2], pid = +t[3]; const r = Math.floor(i / (W + 1)), c = i % (W + 1);
    if (r % 2 === 0) { const key = (c % W) + ',' + ((r / 2) % H); if (kind === 1) hk.add(key); if (kind === 2) hp.set(key, pid); }
    else { const key = (c % W) + ',' + ((r - 1) / 2); if (kind === 1) vk.add(key); if (kind === 2) vp.set(key, pid); } } }
const pc = id => String.fromCharCode(97 + (id % 26));
const out = [];
for (let y = 0; y < H; y++) {
  let a = '', b = '';
  for (let x = 0; x < W; x++) {
    const k = x + ',' + y;
    a += '+' + (hk.has(k) ? '--' : hp.has(k) ? pc(hp.get(k)) + pc(hp.get(k)) : '  ');
    const sp = tiles[k]; const cls = sp === '0-0' ? ' .' : sp === '1-1' ? ' F' : ' ' + pal.get(sp);
    b += (vk.has(k) ? '|' : vp.has(k) ? pc(vp.get(k)) : ' ') + cls;
  }
  out.push(a + '+', b + (vk.has('0,' + y) ? '|' : ' '));
}
console.log(out.join('\n'));
console.log('palette', JSON.stringify([...pal.entries()]));
