#!/usr/bin/env node
// W2 offline harness: how often a single 7x7 window (or a short walk) of a "truth" map leaves exactly one table candidate (mapid's decision
// rule: every N/W edge kind and every spawn flag of the 49 tiles equals the candidate's), and how much distinctive evidence that candidate
// had there: features = candidate kelp/portal edges (N, W) + candidate spawn tiles inside the checked tiles (all confirmed, since it matched).
// Truth maps: stronghold (unseen, Trauma's size), each known map left out of its own size class (32x16: Devil, Portals, PD), and synthetic
// unseen maps of every known size: the known map shifted by (W/3, H/3) and, for square maps, rotated 90 degrees.
// Tables: the generator's parse (legacy/exp/mapid/genmapdb.js; maps/online-20260927 + maps/variants), the same files mapdb.hpp was built from.
// usage: node exp/w2/fpsim.js [--walk 8]
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
  const n = W * H, hk = new Uint8Array(n), vk = new Uint8Array(n), hp = new Uint8Array(n), vp = new Uint8Array(n), sp = new Uint8Array(n);
  for (const [i, kind] of edges) {
    const r = Math.floor(i / (W + 1)), c = i % (W + 1);
    let x, y, side;
    if (r % 2 === 0) { y = (r / 2) % H; x = c % W; side = 0; } else { y = (r - 1) / 2; x = c % W; side = 1; }
    const k = y * W + x;
    if (kind === 1) { if (side === 0) hk[k] = 1; else vk[k] = 1; }
    else if (kind === 2) { if (side === 0) hp[k] = 1; else vp[k] = 1; }
  }
  for (const [x, y, mn, mx] of tiles) sp[y * W + x] = mx > 0 ? 1 : 0;
  // N side kind: 0 open, 1 kelp, 2 portal; W side likewise
  const nk = new Uint8Array(n), wk = new Uint8Array(n);
  for (let k = 0; k < n; k++) { nk[k] = hp[k] ? 2 : hk[k] ? 1 : 0; wk[k] = vp[k] ? 2 : vk[k] ? 1 : 0; }
  return { name, file, W, H, nk, wk, sp, starts };
}
// synthetic: shift by (dx, dy) on the torus; rotate 90 (square maps): tile (x, y) -> (H-1-y, x). Edges move with tiles: the N side of (x,y)
// becomes the E side of the rotated tile = the W side of its east neighbour; the W side becomes the N side.
function shifted(m, dx, dy) {
  const { W, H } = m, n = W * H, o = { ...m, name: `${m.name} shifted ${dx},${dy}`, nk: new Uint8Array(n), wk: new Uint8Array(n), sp: new Uint8Array(n) };
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const s = y * W + x, d = ((y + dy) % H) * W + (x + dx) % W; o.nk[d] = m.nk[s]; o.wk[d] = m.wk[s]; o.sp[d] = m.sp[s]; }
  return o;
}
function rotated(m) {
  const { W, H } = m; if (W !== H) return null;
  const n = W * H, o = { ...m, name: `${m.name} rotated 90`, nk: new Uint8Array(n), wk: new Uint8Array(n), sp: new Uint8Array(n) };
  const at = (x, y) => ((y + H) % H) * W + (x + W) % W;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const s = at(x, y), X = H - 1 - y, Y = x;   // (x,y) -> (X,Y)
    o.sp[at(X, Y)] = m.sp[s];
    o.nk[at(X, Y)] = m.wk[s];                   // old west side faces north after the turn... (approximate: the side set is rotated)
    o.wk[at(X + 1, Y)] = m.nk[s];               // old north side becomes the east side of (X,Y) = the west side of (X+1,Y)
  }
  return o;
}
const files = fs.readdirSync(path.join(ROOT, 'maps', 'online-20260927')).filter(f => f.endsWith('.map')).sort().map(f => path.join(ROOT, 'maps', 'online-20260927', f));
files.push(path.join(ROOT, 'maps', 'variants', 'prisoners_dilemma_10.map'));
for (const f of ['devil_b', 'queen_of_spades_b', 'schooltime_b', 'slithery_fight_b']) files.push(path.join(ROOT, 'maps', 'variants', f + '.map'));
const TABLE = files.map(parse);
TABLE.forEach(m => { m.fam = m.name; });
const args = process.argv.slice(2), WALK = +(args[args.indexOf('--walk') + 1] || 8);
// one window centred at (cx, cy): for each candidate, matched? and confirmed features
function windowCheck(T, C, cx, cy, seen) {
  const { W, H } = T;
  let feat = 0;
  for (let r = -3; r <= 3; r++) for (let c = -3; c <= 3; c++) {
    const k = ((cy + r + H) % H) * W + (cx + c + W) % W;
    if (T.nk[k] !== C.nk[k] || T.wk[k] !== C.wk[k] || T.sp[k] !== C.sp[k]) return -1;
    if (seen && seen.has(k)) continue;
    if (seen) seen.add(k);
    feat += (C.nk[k] ? 1 : 0) + (C.wk[k] ? 1 : 0) + (C.sp[k] ? 1 : 0);
  }
  return feat;
}
function analyse(T, cands, label) {
  const { W, H } = T, n = W * H;
  let fpWin = 0, maxFeat = -1; const featHist = {};
  // single windows
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const alive = cands.map(C => [C, windowCheck(T, C, x, y, null)]).filter(([, f]) => f >= 0);
    const fams = new Set(alive.map(([C]) => C.fam));
    if (fams.size === 1) {   // the bot decides a family (one map, or several layouts of one family)
      fpWin++;
      const f = Math.min(...alive.map(([, f]) => f));
      featHist[f] = (featHist[f] || 0) + 1; if (f > maxFeat) maxFeat = f;
    }
  }
  // straight walks of WALK steps from every tile in each direction: the candidate set over the union of windows, distinct-tile features
  let fpWalk = 0, maxWalkFeat = -1; const walkHist = {};
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) for (const [dx, dy] of [[1, 0], [0, 1], [-1, 0], [0, -1]]) {
    const st = cands.map(C => ({ C, seen: new Set(), feat: 0, ok: true }));
    for (let s = 0; s <= WALK; s++) {
      const cx = (x + dx * s + W * 9) % W, cy = (y + dy * s + H * 9) % H;
      for (const q of st) if (q.ok) { const f = windowCheck(T, q.C, cx, cy, q.seen); if (f < 0) q.ok = false; else q.feat += f; }
    }
    const alive = st.filter(q => q.ok), fams = new Set(alive.map(q => q.C.fam));
    if (fams.size === 1) { fpWalk++; const f = Math.min(...alive.map(q => q.feat)); walkHist[f] = (walkHist[f] || 0) + 1; if (f > maxWalkFeat) maxWalkFeat = f; }
  }
  const top = h => Object.entries(h).map(([k, v]) => [+k, v]).sort((a, b) => b[0] - a[0]).slice(0, 6).map(([k, v]) => `${k}:${v}`).join(' ');
  console.log(`${label.padEnd(44)} windows ${n}: false single-family ${fpWin} (max features ${maxFeat}; top ${top(featHist)}) | walks of ${WALK}: ${fpWalk}/${n * 4} (max ${maxWalkFeat}; top ${top(walkHist)})`);
}
console.log('== false recognition: the truth map is not in the candidate set');
const strong = parse(path.join(ROOT, 'maps', 'bundled', 'stronghold.map'));
analyse(strong, TABLE.filter(C => C.W === strong.W && C.H === strong.H), 'stronghold vs ' + TABLE.filter(C => C.W === strong.W && C.H === strong.H).map(c => c.name).join('/'));
for (const T of TABLE.filter(m => !/_b\.map$|_10\.map$/.test(m.file))) {
  const others = TABLE.filter(C => C.W === T.W && C.H === T.H && C.fam !== T.fam);
  if (others.length) analyse(T, others, `${T.name} (left out) vs ${[...new Set(others.map(c => c.name))].join('/')}`);
}
for (const T of TABLE.filter(m => !/_b\.map$|_10\.map$/.test(m.file))) {
  const cands = TABLE.filter(C => C.W === T.W && C.H === T.H);
  analyse(shifted(T, Math.floor(T.W / 3), Math.floor(T.H / 3)), cands, `${T.name} shifted (W/3,H/3)`);
  const R = rotated(T); if (R) analyse(R, cands, `${T.name} rotated 90`);
}
console.log('== recognition on the known maps: features in the start windows (true candidate) and share of windows with >= K features');
for (const T of TABLE.filter(m => !/_b\.map$|_10\.map$/.test(m.file))) {
  const C = T, sf = T.starts.map(s => windowCheck(T, C, s.x, s.y, null));
  const all = []; for (let y = 0; y < T.H; y++) for (let x = 0; x < T.W; x++) all.push(windowCheck(T, C, x, y, null));
  const share = K => (100 * all.filter(f => f >= K).length / all.length).toFixed(0) + '%';
  console.log(`${T.name.padEnd(20)} start windows: ${sf.join(',')} | single windows with >=6: ${share(6)}, >=8: ${share(8)}, >=10: ${share(10)}, >=12: ${share(12)}, >=16: ${share(16)}`);
}
