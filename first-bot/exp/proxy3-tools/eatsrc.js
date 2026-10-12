#!/usr/bin/env node
'use strict';
// eatsrc.js — where each side's pearls come from, per 100-round window: spawn tiles by gap class (from the local map
// files; fountain = max gap <= 10, fast <= 50, medium <= 300, slow > 300) and pearls dropped by deaths (own / enemy).
// usage: node exp/proxy3-tools/eatsrc.js --g "<name>=<src>[+<src>]" [...] [--maps autarky,trophy] [--side them|us] [--limit N]
//   <src> = online:<set> (data/online/<set>/M<id>.replay) | local:<label>[@opp,...] (exp/<label>/games/*/game.replay)
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const MAPFILES = { autarky: 'autarky', default: 'default', devil: 'devil', portals: 'portals', pd6: 'prisoners_dilemma', queen_of_spades: 'queen_of_spades', schooltime: 'schooltime', slithery_fight: 'slithery_fight', trauma: 'trauma', trophy: 'trophy' };
const gapCache = {};
function gaps(m) {
  if (gapCache[m]) return gapCache[m];
  const f = m === 'pd10' ? path.join(ROOT, 'maps', 'variants', 'prisoners_dilemma_10.map') : path.join(ROOT, 'maps', 'online-20260927', MAPFILES[m] + '.map');
  const L = fs.readFileSync(f, 'utf8').split('\n'); let W = 0; const g = new Map();
  for (const l of L) { const t = l.trim().split(/\s+/); if (t[0] === 'MAP') W = +t[1]; else if (t[0] === 'TILE') g.set(+t[2] * W + +t[1], +t[4]); }
  return (gapCache[m] = { W, g });
}
const cls = mx => mx <= 0 ? 'never' : mx <= 10 ? 'fountain' : mx <= 50 ? 'fast' : mx <= 300 ? 'medium' : 'slow';
const CLS = ['fountain', 'fast', 'medium', 'slow', 'never', 'dropOwn', 'dropEnemy'];
const mapKey = n => String(n).toLowerCase().replace(/\.map$/, '').replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
function listGames(spec) {
  const out = [];
  for (const src of spec.split('+')) {
    const [kind, rest] = src.split(/:(.*)/s);
    if (kind === 'online') {
      const dir = path.join(ROOT, 'data', 'online', rest);
      for (const f of fs.readdirSync(dir).filter(x => /^game-\d+\.json$/.test(x))) {
        const g = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')); if (g.status !== 'completed') continue;
        const ours = g.teamAId === 583 ? 'A' : g.teamBId === 583 ? 'B' : null; if (!ours) continue;
        out.push({ file: path.join(dir, 'M' + g.id + '.replay'), map: mapKey(g.mapName), ours });
      }
    } else {
      const [label, o] = rest.split('@'); const opps = o ? new Set(o.split(',')) : null;
      for (const l of fs.readFileSync(path.join(ROOT, 'exp', label, 'rows.jsonl'), 'utf8').trim().split('\n')) {
        const r = JSON.parse(l); if (r.G === undefined || (opps && !opps.has(r.opp))) continue;
        const file = path.join(ROOT, "exp", label, "games", r.key.replace(/:/g, "_"), "game.replay"); if (!fs.existsSync(file)) continue;
        out.push({ file, map: mapKey(r.map), ours: r.side });
      }
    }
  }
  return out;
}
function scan(gm) {
  const R = load(gm.file), M = R.match.map, W = M.width;
  const team = new Map(); for (const d of M.initialDragons) team.set(d.id, d.team);
  let m = gm.map; if (m.startsWith('prisoners_dilemma')) { const nA = M.initialDragons.filter(d => d.team === 'A').length; m = nA >= 5 ? 'pd10' : 'pd6'; }
  const G = gaps(m);
  const dropOf = new Map(); // tile -> team whose death dropped it
  const res = { A: {}, B: {} }; for (const s of ['A', 'B']) for (let w = 0; w < 5; w++) { res[s][w] = {}; for (const c of CLS) res[s][w][c] = 0; }
  let round = 0, actor = -1, lastDeathTeam = null;
  for (const e of R.events) {
    if (e.type === 'roundStart') { round = e.round; lastDeathTeam = null; actor = -1; }
    else if (e.type === 'turnStart') { actor = e.id; lastDeathTeam = null; }
    else if (e.type === 'dragonSplit') team.set(e.childId, e.team);
    else if (e.type === 'dragonDeath') lastDeathTeam = team.get(e.id);
    else if (e.type === 'tileChange') {
      const k = e.tile.y * W + e.tile.x;
      if (e.hasPearl) { if (lastDeathTeam) dropOf.set(k, lastDeathTeam); else dropOf.delete(k); }
      else if (actor >= 0 && round < 500) {
        const s = team.get(actor); const w = Math.min(4, Math.floor(round / 100));
        let c; if (dropOf.has(k)) c = dropOf.get(k) === s ? 'dropOwn' : 'dropEnemy'; else c = cls(G.g.get(k) || 0);
        dropOf.delete(k);
        if (s) res[s][w][c]++;
      }
    } else if (e.type === 'dragonUpdate' || e.type === 'dragonAction') { /* keep actor */ }
  }
  return { m, res, rounds: R.result ? null : null };
}
const argv = process.argv.slice(2); const groups = []; let side = 'them', maps = null, limit = 1e9;
for (let i = 0; i < argv.length; i++) { if (argv[i] === '--g') { const s = argv[++i], j = s.indexOf('='); groups.push([s.slice(0, j), s.slice(j + 1)]); } else if (argv[i] === '--side') side = argv[++i]; else if (argv[i] === '--maps') maps = new Set(argv[++i].split(',')); else if (argv[i] === '--limit') limit = +argv[++i]; }
const agg = {};
for (const [name, spec] of groups) {
  let n = 0;
  for (const gm of listGames(spec)) {
    const mk = gm.map.startsWith('prisoners') ? null : gm.map;
    if (maps && mk && !maps.has(mk)) continue;
    if (n++ >= limit) break;
    const { m, res } = scan(gm);
    if (maps && !maps.has(m)) continue;
    const s = side === 'us' ? gm.ours : (gm.ours === 'A' ? 'B' : 'A');
    const key = name + '|' + m; if (!agg[key]) { agg[key] = { n: 0, w: {} }; for (let w = 0; w < 5; w++) { agg[key].w[w] = {}; for (const c of CLS) agg[key].w[w][c] = 0; } }
    agg[key].n++; for (let w = 0; w < 5; w++) for (const c of CLS) agg[key].w[w][c] += res[s][w][c];
  }
}
console.log('| group | map | games | window | ' + CLS.join(' | ') + ' |\n|---|---|---:|---|' + CLS.map(() => '---:').join('|') + '|');
for (const [k, a] of Object.entries(agg).sort()) {
  const [g, m] = k.split('|');
  for (const w of [0, 1, 2]) console.log(`| ${g} | ${m} | ${a.n} | r${w * 100}-${w * 100 + 99} | ${CLS.map(c => (a.w[w][c] / a.n).toFixed(1)).join(' | ')} |`);
}
