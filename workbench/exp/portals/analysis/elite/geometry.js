#!/usr/bin/env node
// Portals geometry for the king-safety reading: territory (movement BFS from each team's starting bodies), the static 2-core of the
// movement graph (kelp, portals, wrap), and the spawning tiles (maps/online-20260927/portals.map TILE min max, max > 0) by territory.
// usage: node exp/portals/analysis/elite/geometry.js <any Portals replay>
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../../../..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const R = makeLoader(viewerSource())(process.argv[2]);
const gap = {}; for (const l of fs.readFileSync(path.join(ROOT, 'maps/online-20260927/portals.map'), 'utf8').split('\n')) if (l.startsWith('TILE ')) { const [x, y, a, b] = l.split(/\s+/).slice(1).map(Number); gap[y * 32 + x] = [a, b]; }
let done = false;
try { perGame(R, { map: 'Portals' }, { turn(d, r, ctx) {
  if (done) return; done = true;
  const { W, H, across, terr } = ctx, N = W * H, DIRS = ['N', 'E', 'S', 'W'];
  const nb = []; for (let k = 0; k < N; k++) { const s = new Set(); for (const dd of DIRS) { const n = across(k % W, (k / W) | 0, dd); if (n) { const nk = n.y * W + n.x; if (nk !== k) s.add(nk); } } nb.push([...s]); }
  const deg = nb.map(a => a.length), core = new Uint8Array(N).fill(1), q = [];
  for (let k = 0; k < N; k++) if (deg[k] <= 1) { core[k] = 0; q.push(k); }
  for (let i = 0; i < q.length; i++) for (const u of nb[q[i]]) if (core[u] && --deg[u] <= 1) { core[u] = 0; q.push(u); }
  for (const t of [1, 2, 0]) {
    const tiles = [...Array(N).keys()].filter(k => terr[k] === t);
    const sp = tiles.filter(k => gap[k] && gap[k][1] > 0), f1 = sp.filter(k => gap[k][1] === 1);
    console.log(`${t === 0 ? 'neutral' : 'team ' + (t === 1 ? 'A' : 'B')}: tiles ${tiles.length}, in 2-core ${tiles.filter(k => core[k]).length}, spawning ${sp.length} (gap 1-1: ${f1.length}), spawning in 2-core ${sp.filter(k => core[k]).length}, spawning with 1 exit ${sp.filter(k => nb[k].length <= 1).length}`);
  }
  // picture: one char per tile. S spawning tile in the 2-core, d spawning dead end (outside the 2-core), . other 2-core tile, , other non-core tile, blank neutral
  console.log('legend: A-side tiles: S spawn in 2-core, d spawn outside the 2-core, . 2-core, , outside 2-core; B-side lower case s d : ;  neutral #');
  for (let y = 0; y < H; y++) { let row = ''; for (let x = 0; x < W; x++) { const k = y * W + x, s = gap[k] && gap[k][1] > 0; row += terr[k] === 0 ? '#' : terr[k] === 1 ? (s ? (core[k] ? 'S' : 'd') : core[k] ? '.' : ',') : (s ? (core[k] ? 's' : 'd') : core[k] ? ':' : ';'); } console.log(row); }
  throw new Error('stop');
} }); } catch (e) { if (e.message !== 'stop') throw e; }
