#!/usr/bin/env node
// v1 final spatial checks (coordinator 03:30) for local eval sets (tools/eval.js output), per map family:
//   1. our head share by x-band (r50-374, every turn start, mass-ledger bodies) vs natural pearl appearance by x-band (tileChange pearl outside a
//      death-drop run, same rounds); bands = 5 equal x-slices of the board;
//   2. the share of our " sd<d>@x,y" targets on tiles outside the 2-core (the bot's definition: kelp edges from the map, portal edges passable
//      and never pruned through) - must be 0;
//   3. trap deaths (mass-ledger cause 'trap'): the share inside a pocket (outside the 2-core) and by x-band.
// usage: node exp/v1/spatial.js <evalDir>[,<evalDir>] [--label name]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const NAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', devil_b: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma',
  prisoners_dilemma_10: 'Prisoners Dilemma', queen_of_spades: 'Queen Of Spades', queen_of_spades_b: 'Queen Of Spades', schooltime: 'Schooltime',
  schooltime_b: 'Schooltime', slithery_fight: 'Slithery Fight', slithery_fight_b: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const NB = 5;
function core2(M) {
  const W = M.width, H = M.height, N = W * H;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
  const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
  const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
  const portal = new Set();
  for (const pr of M.portals || []) for (const e of pr) { const c = canon(e); portal.add(c.x + ',' + c.y + ',' + c.side); }
  // edge kind on side d of (x, y): 0 open, 1 kelp, 2 portal
  const kind = (x, y, d) => {
    let ek, kelp;
    if (d === 0) { ek = x + ',' + y + ',N'; kelp = hk(x, y); }
    else if (d === 2) { ek = x + ',' + wy(y + 1) + ',N'; kelp = hk(x, y + 1); }
    else if (d === 3) { ek = x + ',' + y + ',W'; kelp = vk(x, y); }
    else { ek = wx(x + 1) + ',' + y + ',W'; kelp = vk(x + 1, y); }
    if (portal.has(ek)) return 2;
    return kelp ? 1 : 0;
  };
  const DX = [0, 1, 0, -1], DY = [-1, 0, 1, 0];
  const deg = new Int32Array(N), gone = new Uint8Array(N), q = [];
  for (let t = 0; t < N; t++) { const x = t % W, y = (t / W) | 0; for (let d = 0; d < 4; d++) if (kind(x, y, d) !== 1) deg[t]++; if (deg[t] <= 1) { gone[t] = 1; q.push(t); } }
  for (let i = 0; i < q.length; i++) {
    const t = q[i], x = t % W, y = (t / W) | 0;
    for (let d = 0; d < 4; d++) {
      if (kind(x, y, d) !== 0) continue;
      const u = wy(y + DY[d]) * W + wx(x + DX[d]);
      if (gone[u]) continue;
      if (--deg[u] <= 1) { gone[u] = 1; q.push(u); }
    }
  }
  return gone;   // 1 = outside the 2-core
}
const dirs = process.argv[2].split(',');
const label = (() => { const i = process.argv.indexOf('--label'); return i > 0 ? process.argv[i + 1] : dirs.join('+'); })();
const oppOnly = (() => { const i = process.argv.indexOf('--opp'); return i > 0 ? process.argv[i + 1] : null; })();
const agg = {};   // fam -> { heads[NB], pearls[NB], sd, sdOut, trap, trapPocket, trapBand[NB] }
const perMap = {};
for (const dir of dirs) {
  const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined && (!oppOnly || r.opp === oppOnly));
  for (const r of rows) {
    const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
    const R = load(file), M = R.match.map, W = M.width, H = M.height;
    const gone = core2(M);
    const map = NAME[r.map], fam = ['Autarky', 'Portals', 'Prisoners Dilemma'].includes(map) ? 'fortress' : 'swarm', us = r.side;
    const A = agg[fam] || (agg[fam] = { heads: Array(NB).fill(0), pearls: Array(NB).fill(0), sd: 0, sdOut: 0, trap: 0, trapPocket: 0, trapBand: Array(NB).fill(0) });
    const Pm = perMap[r.map] || (perMap[r.map] = { heads: Array(NB).fill(0), pearls: Array(NB).fill(0), sd: 0, sdOut: 0, trap: 0, trapPocket: 0, games: 0 });
    Pm.games++;
    const band = x => Math.min(NB - 1, Math.floor(x * NB / W));
    // natural pearl appearances by band (not a death-drop run), r50-374
    { let round = -1, dropping = false;
      for (const e of R.events) {
        if (dropping && !(e.type === 'tileChange' && e.hasPearl)) dropping = false;
        if (e.type === 'roundStart') round = e.round;
        else if (e.type === 'dragonDeath') dropping = true;
        else if (e.type === 'tileChange' && e.hasPearl && !dropping && round >= 50 && round <= 374) { A.pearls[band(e.tile.x)]++; Pm.pearls[band(e.tile.x)]++; }
      } }
    const hooks = {
      turn(d, round) { if (d.team !== us || round < 50 || round > 374) return; const b = band(d.body[0].x); A.heads[b]++; Pm.heads[b]++; },
      indicator(e) {
        const m = / sd\d+@(\d+),(\d+)/.exec(e.text || ''); if (!m) return;
        A.sd++; Pm.sd++; if (gone[(+m[2]) * W + (+m[1])]) { A.sdOut++; Pm.sdOut++; }
      },
      death(d, rec) {
        if (d.team !== us || ML.CAUSE[rec.cause] !== 'trap') return;
        const h = d.body[0]; A.trap++; Pm.trap++; A.trapBand[band(h.x)]++;
        if (gone[h.y * W + h.x]) { A.trapPocket++; Pm.trapPocket++; }
      },
    };
    ML.perGame(R, { map }, hooks);
  }
}
const pc = (a, n) => n ? (100 * a / n).toFixed(0) + '%' : '–';
const L = [`# Spatial checks: ${label}`, '', 'x-bands = 5 equal slices of the board width (left to right). Heads: our head at every turn start, r50-374. Pearls: natural appearances, r50-374.', ''];
L.push('| family | our heads by band | natural pearls by band | sd targets outside the 2-core | trap deaths / game-set · in a pocket | trap deaths by band |', '|---|---|---|---|---|---|');
for (const [fam, A] of Object.entries(agg)) {
  const hs = A.heads.reduce((a, b) => a + b, 0), ps = A.pearls.reduce((a, b) => a + b, 0), ts = A.trapBand.reduce((a, b) => a + b, 0);
  L.push(`| ${fam} | ${A.heads.map(v => pc(v, hs)).join(' · ')} | ${A.pearls.map(v => pc(v, ps)).join(' · ')} | ${pc(A.sdOut, A.sd)} (${A.sdOut}/${A.sd}) | ${A.trap} · ${pc(A.trapPocket, A.trap)} | ${A.trapBand.map(v => pc(v, ts)).join(' · ')} |`);
}
L.push('', '| map | games | our heads by band | natural pearls by band | sd outside 2-core | trap deaths · in a pocket |', '|---|---:|---|---|---|---|');
for (const [m, P] of Object.entries(perMap).sort()) {
  const hs = P.heads.reduce((a, b) => a + b, 0), ps = P.pearls.reduce((a, b) => a + b, 0);
  L.push(`| ${m} | ${P.games} | ${P.heads.map(v => pc(v, hs)).join(' · ')} | ${P.pearls.map(v => pc(v, ps)).join(' · ')} | ${pc(P.sdOut, P.sd)} (${P.sdOut}/${P.sd}) | ${P.trap} · ${pc(P.trapPocket, P.trap)} |`);
}
console.log(L.join('\n'));
