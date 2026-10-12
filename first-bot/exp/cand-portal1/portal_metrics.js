#!/usr/bin/env node
// Portal mechanism metrics for one eval label (exp/<label>/rows.jsonl + games/<key>/game.replay).
// usage: node exp/cand-portal1/portal_metrics.js <label | eval dir> [--maps portals,trauma|all] [--json out.json]
// Per game, for our side (row.side): portal steps (steps of our dragons that crossed a portal edge), crossing actions,
// natural pearls spawned / eaten by us / eaten by them, our deaths within 3 rounds after that dragon's last crossing,
// blind entries (indicator " PORTAL?"), and the row's G / won / alive.
// Natural pearl = a pearl that appeared in the tick phase of a round (spawn) or was on the board at round 0.
// Eaten = the pearl disappeared during a dragon's turn; the eater is the dragon whose turn it is.
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const { load } = require(path.join(ROOT, 'tools/replay.js'));
const label = process.argv[2];
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const maps = arg('maps', 'portals,trauma').split(',');
const DIR = label.includes('/') ? path.resolve(label) : path.join(ROOT, 'exp', label);
const rows = fs.readFileSync(path.join(DIR, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l))
  .filter(r => r.G !== undefined && (maps[0] === 'all' || maps.includes(r.map)));
const seen = new Set();
const out = [];
for (const row of rows) {
  if (seen.has(row.key)) continue; seen.add(row.key);
  const file = path.join(DIR, 'games', row.key.replace(/:/g, '_'), 'game.replay');
  if (!fs.existsSync(file)) continue;
  out.push({ key: row.key, opp: row.opp, map: row.map, side: row.side, seed: row.seed, G: row.G, won: row.won, alive: row.alive, ...analyse(load(file), row.side) });
}
function analyse(R, US) {
  const M = R.match.map, W = M.width, H = M.height;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
  const portal = new Map();
  (M.portals || []).forEach(pr => { if (pr.length !== 2) return; const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); });
  const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
  const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
  const DXa = { N: 0, E: 1, S: 0, W: -1 }, DYa = { N: -1, E: 0, S: 1, W: 0 };
  function across(x, y, d) {
    let ek, kelp;
    if (d === 'N') { ek = x + ',' + y + ',N'; kelp = hk(x, y); }
    else if (d === 'S') { ek = x + ',' + wy(y + 1) + ',N'; kelp = hk(x, y + 1); }
    else if (d === 'W') { ek = x + ',' + y + ',W'; kelp = vk(x, y); }
    else { ek = wx(x + 1) + ',' + y + ',W'; kelp = vk(x + 1, y); }
    const p = portal.get(ek);
    if (p) {
      if (d === 'N') return { x: p.x, y: wy(p.y - 1), portal: true };
      if (d === 'S') return { x: p.x, y: p.y, portal: true };
      if (d === 'W') return { x: wx(p.x - 1), y: p.y, portal: true };
      return { x: p.x, y: p.y, portal: true };
    }
    if (kelp) return null;
    return { x: wx(x + DXa[d]), y: wy(y + DYa[d]) };
  }
  const team = new Map(), head = new Map(), lastCross = new Map();
  for (const d of M.initialDragons) { team.set(d.id, d.team); head.set(d.id, d.body[0]); }
  const origin = new Map(); // tile -> 'nat' | 'drop'
  (Array.from(M.initialTiles || [])).forEach((v, i) => { if (v) origin.set(i, 'nat'); });
  const r = { portalSteps: 0, crossActions: 0, natSpawn: 0, natEatUs: 0, natEatThem: 0, eatUs: 0, deathsAfterCross: 0, deathsUs: 0, blind: 0,
    deadEndLandings: 0, afterCrossReason: {}, crossRounds: [] };
  // a landing tile whose only way out is back through the portal it was entered by (a one-tile pocket)
  const deadEnd = (t, inDir) => { const x = t.x, y = t.y; let exits = 0; const back = { N: 'S', S: 'N', E: 'W', W: 'E' }[inDir];
    for (const d of ['N', 'E', 'S', 'W']) { if (d === back) continue; if (across(x, y, d)) exits++; } return exits === 0; };
  const len = new Map(); for (const d of M.initialDragons) len.set(d.id, d.body.length);
  let round = 0, phase = 'tick', cur = -1;
  for (const e of R.events) {
    switch (e.type) {
      case 'roundStart': round = e.round; phase = 'tick'; break;
      case 'turnStart': phase = 'turn'; cur = e.id; break;
      case 'tileChange': {
        const t = e.tile.y * W + e.tile.x;
        if (e.hasPearl) { const o = phase === 'tick' ? 'nat' : 'drop'; origin.set(t, o); if (o === 'nat') r.natSpawn++; }
        else if (phase === 'turn') {
          const o = origin.get(t); origin.delete(t);
          const us = team.get(cur) === US;
          if (us) { r.eatUs++; len.set(cur, (len.get(cur) || 0) + 1); }
          if (o === 'nat') { if (us) r.natEatUs++; else r.natEatThem++; }
        }
        break;
      }
      case 'dragonIndicator': if (team.get(e.id) === US && / PORTAL\?/.test(e.text || '')) r.blind++; break;
      case 'dragonSplit': team.set(e.childId, e.team); head.set(e.childId, e.childBody[0]); head.set(e.parentId, e.parentBody[0]); len.set(e.childId, e.childBody.length); len.set(e.parentId, e.parentBody.length); break;
      case 'dragonUpdate': head.set(e.id, e.head); break;
      case 'dragonDeath':
        if (team.get(e.id) === US) {
          r.deathsUs++;
          if (lastCross.has(e.id) && round - lastCross.get(e.id) <= 3) { r.deathsAfterCross++; r.afterCrossReason[e.reason] = (r.afterCrossReason[e.reason] || 0) + 1; }
        }
        break;
      case 'dragonAction':
        if (e.action.kind === 'move') {
          let h = head.get(e.id); if (!h) break;
          let any = false;
          for (const d of e.action.steps) { const nx = across(h.x, h.y, d); if (!nx) break; if (nx.portal) { any = true; if (team.get(e.id) === US) { r.portalSteps++; if (deadEnd(nx, d)) r.deadEndLandings++; } } h = nx; }
          if (any && team.get(e.id) === US) { r.crossActions++; lastCross.set(e.id, round); if (r.crossRounds.length < 400) r.crossRounds.push(round); }
        }
        break;
    }
  }
  return r;
}
const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN;
const byMap = {};
for (const g of out) (byMap[g.map] = byMap[g.map] || []).push(g);
const fields = ['G', 'portalSteps', 'crossActions', 'blind', 'deadEndLandings', 'natSpawn', 'natEatUs', 'natEatThem', 'eatUs', 'deathsUs', 'deathsAfterCross'];
console.log(['map', 'n', ...fields].join('\t'));
for (const m of Object.keys(byMap).sort()) console.log([m, byMap[m].length, ...fields.map(f => mean(byMap[m].map(g => +g[f])).toFixed(2))].join('\t'));
console.log(['all', out.length, ...fields.map(f => mean(out.map(g => +g[f])).toFixed(2))].join('\t'));
for (const m of Object.keys(byMap).sort()) { const agg = {}; for (const g of byMap[m]) for (const [k, v] of Object.entries(g.afterCrossReason)) agg[k] = (agg[k] || 0) + v;
  console.log(`${m}: deaths within 3 rounds after crossing by reason (per game):`, Object.entries(agg).map(([k, v]) => k + ' ' + (v / byMap[m].length).toFixed(2)).join(', ') || '-'); }
const jf = arg('json'); if (jf) fs.writeFileSync(jf, JSON.stringify(out, null, 1));
