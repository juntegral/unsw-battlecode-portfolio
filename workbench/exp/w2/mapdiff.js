#!/usr/bin/env node
// W2: tile-by-tile comparison of two maps of the same size (N/W edge kinds and spawn ranges). Prints both maps as ASCII and a diff grid:
// '.' = same edges and same spawn flag, 'e' = edge differs, 's' = spawn flag differs, 'b' = both; also where the start heads are.
// usage: node exp/w2/mapdiff.js <a.map> <b.map>
'use strict';
const fs = require('fs');
function parse(file) {
  const L = fs.readFileSync(file, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  let W = 0, H = 0; const tiles = [], edges = [], starts = [];
  for (const l of L) { const t = l.split(/\s+/);
    if (t[0] === 'MAP') { W = +t[1]; H = +t[2]; } else if (t[0] === 'TILE') tiles.push([+t[1], +t[2], +t[3], +t[4]]);
    else if (t[0] === 'EDGE') edges.push([+t[1], +t[2], +t[3]]); else if (t[0] === 'DRAGON') starts.push([+t[1], +t[3], +t[4]]); }
  const n = W * H, nk = new Uint8Array(n), wk = new Uint8Array(n), sp = new Array(n).fill('0,0');
  for (const [i, kind] of edges) { const r = Math.floor(i / (W + 1)), c = i % (W + 1); let x, y, side;
    if (r % 2 === 0) { y = (r / 2) % H; x = c % W; side = 0; } else { y = (r - 1) / 2; x = c % W; side = 1; }
    const k = y * W + x; if (side === 0) nk[k] = kind; else wk[k] = kind; }
  for (const [x, y, mn, mx] of tiles) sp[y * W + x] = mx > 0 ? mn + ',' + mx : '0,0';
  return { W, H, nk, wk, sp, starts };
}
const A = parse(process.argv[2]), B = parse(process.argv[3]);
const { W, H } = A;
function draw(M) {
  const out = [];
  for (let y = 0; y < H; y++) {
    let top = '', mid = '';
    for (let x = 0; x < W; x++) { const k = y * W + x;
      top += '+' + (M.nk[k] === 1 ? '--' : M.nk[k] === 2 ? '==' : '  ');
      const st = M.starts.find(s => s[1] === x && s[2] === y);
      mid += (M.wk[k] === 1 ? '|' : M.wk[k] === 2 ? '#' : ' ') + (st ? 'H' + st[0] : M.sp[k] !== '0,0' ? ' *' : '  '); }
    out.push(top, mid);
  }
  return out.join('\n');
}
console.log(draw(A)); console.log(); console.log(draw(B)); console.log();
let same = 0;
for (let y = 0; y < H; y++) { let row = '';
  for (let x = 0; x < W; x++) { const k = y * W + x, e = A.nk[k] !== B.nk[k] || A.wk[k] !== B.wk[k], s = (A.sp[k] !== '0,0') !== (B.sp[k] !== '0,0');
    row += e && s ? 'b' : e ? 'e' : s ? 's' : (A.sp[k] !== B.sp[k] ? 'r' : '.'); if (!e && !s) same++; }
  console.log(row); }
console.log(`same tiles (edges + spawn flag): ${same}/${W * H}; 'r' = same flag, different range`);
