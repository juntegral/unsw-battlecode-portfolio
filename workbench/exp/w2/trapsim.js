#!/usr/bin/env node
// W2 / W8 offline prediction for the recognition traps (maps/generated/gen_X_*): per map, the table candidates of its size; per start dragon,
// the candidates its round-0 7x7 window leaves (N/W edge kinds and spawn flags, as mapid.cpp without countdowns) and whether the start anchor
// holds (a candidate with more dragons than our id has a start dragon on our head with our length); and over all windows of the map, how many
// leave exactly one family (what a child born there would decide from one window).
// usage: node exp/w2/trapsim.js [maps/generated/gen_X_01.map ...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
function parse(file) {
  const L = fs.readFileSync(file, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  let W = 0, H = 0, name = path.basename(file, '.map');
  const tiles = [], edges = [], starts = [];
  for (const l of L) {
    const t = l.split(/\s+/);
    if (t[0] === 'MAP') { W = +t[1]; H = +t[2]; }
    else if (t[0] === 'MAP_NAME') name = l.slice(9).trim();
    else if (t[0] === 'TILE') tiles.push([+t[1], +t[2], +t[3], +t[4]]);
    else if (t[0] === 'EDGE') edges.push([+t[1], +t[2], +t[3]]);
    else if (t[0] === 'DRAGON') starts.push({ team: +t[1], len: +t[2], x: +t[3], y: +t[4] });
  }
  const n = W * H, nk = new Uint8Array(n), wk = new Uint8Array(n), sp = new Uint8Array(n);
  for (const [i, kind] of edges) {
    const r = Math.floor(i / (W + 1)), c = i % (W + 1);
    let x, y, side;
    if (r % 2 === 0) { y = (r / 2) % H; x = c % W; side = 0; } else { y = (r - 1) / 2; x = c % W; side = 1; }
    const k = y * W + x;
    if (side === 0) nk[k] = kind; else wk[k] = kind;
  }
  for (const [x, y, mn, mx] of tiles) sp[y * W + x] = mx > 0 ? 1 : 0;
  return { name, file, W, H, nk, wk, sp, starts };
}
const files = fs.readdirSync(path.join(ROOT, 'maps', 'online-20260927')).filter(f => f.endsWith('.map')).sort().map(f => path.join(ROOT, 'maps', 'online-20260927', f));
files.push(path.join(ROOT, 'maps', 'variants', 'prisoners_dilemma_10.map'));
for (const f of ['devil_b', 'queen_of_spades_b', 'schooltime_b', 'slithery_fight_b']) files.push(path.join(ROOT, 'maps', 'variants', f + '.map'));
const TABLE = files.map((f, i) => Object.assign(parse(f), { idx: i, fam: parse(f).name, lay: /_b\.map$|_10\.map$/.test(f) ? 'b' : 'a' }));
const fits = (T, C, cx, cy) => {
  for (let r = -3; r <= 3; r++) for (let c = -3; c <= 3; c++) {
    const k = ((cy + r + T.H * 4) % T.H) * T.W + (cx + c + T.W * 4) % T.W;
    if (T.nk[k] !== C.nk[k] || T.wk[k] !== C.wk[k] || T.sp[k] !== C.sp[k]) return false;
  }
  return true;
};
const args = process.argv.slice(2);
const maps = args.length ? args : fs.readdirSync(path.join(ROOT, 'maps', 'generated')).filter(f => /^gen_X_\d+\.map$/.test(f)).sort().map(f => path.join(ROOT, 'maps', 'generated', f));
for (const f of maps) {
  const T = parse(f), cands = TABLE.filter(C => C.W === T.W && C.H === T.H);
  console.log(`${path.basename(f)} ${T.W}x${T.H}: candidates ${cands.map(c => c.fam + '/' + c.lay).join(', ') || 'none'}; dragons ${T.starts.length}`);
  T.starts.forEach((s, id) => {
    const alive = cands.filter(C => fits(T, C, s.x, s.y));
    const fams = [...new Set(alive.map(c => c.fam))];
    const anchored = alive.filter(C => id < C.starts.length && C.starts.some(d => d.x === s.x && d.y === s.y && d.len === s.len));
    console.log(`   start #${id} team ${s.team} (${s.x},${s.y}) L${s.len}: window leaves ${alive.map(c => c.fam + '/' + c.lay).join(', ') || 'nothing'}${fams.length === 1 ? ' -> one family: ' + fams[0] + (anchored.length ? ' (start anchor holds: DECIDES at r0)' : ' (no start anchor: held)') : fams.length ? ' -> several families' : ' -> none'}`);
  });
  let one = 0; const famCount = {};
  for (let y = 0; y < T.H; y++) for (let x = 0; x < T.W; x++) {
    const fams = [...new Set(cands.filter(C => fits(T, C, x, y)).map(c => c.fam))];
    if (fams.length === 1) { one++; famCount[fams[0]] = (famCount[fams[0]] || 0) + 1; }
  }
  console.log(`   single windows leaving exactly one family: ${one}/${T.W * T.H} ${JSON.stringify(famCount)}`);
}
