#!/usr/bin/env node
// Stage 3 reading for the endgame king study: one line per round for chosen dragons (and their team's king).
// usage: node exp/endgame-king/film.js <key> <id[,id...]> [--from 330] [--to 500] [--every 1]
//   <key> = <battleId>:<gameId> (data/top) or <set>:<gameId> (data/online).
// Per round (first turn of each listed dragon): head, length, label (ours), team king id/length and Manhattan distance to it,
// nearest enemy head (distance, length), natural pearls within 5, and events of that round: eats (n natural / d drop / e enemy
// drop), splits, death (cause, drops and who ate them).
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const CAUSE = ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'];
function locate(key) {
  const [a, b] = key.split(':');
  if (/^\d+$/.test(a)) {
    for (const l of fs.readFileSync(path.join(ROOT, 'data', 'top', 'index.jsonl'), 'utf8').split('\n')) { if (!l.includes('"gameId":' + b)) continue; const r = JSON.parse(l); if (String(r.battleId) === a) return { file: path.join(ROOT, 'data', 'top', a, b + '.replay.gz'), map: r.map, desc: `A=${r.teamA} B=${r.teamB} winner ${r.winner}` }; }
  }
  const dir = path.join(ROOT, 'data', 'online', a), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  const g = (idx.games || idx).find(x => String(x.gameId) === b);
  return { file: path.join(dir, 'M' + b + '.replay'), map: g.mapName, us: String(g.ourSide).toUpperCase(), desc: `us=${String(g.ourSide).toUpperCase()} opp=${g.opponentTeam} winner ${String(g.winner).toUpperCase()}` };
}
const [key, idsArg] = argv;
const lineMode = /^line[AB]$/.test(String(argv[1]));
let ids = new Set(String(idsArg).split(',').filter(x => /^\d+$/.test(x)).map(Number));
const from = +opt('from', 330), to = +opt('to', 500), every = +opt('every', 1);
const loc = locate(key), load = tf.makeLoader(tf.viewerSource()), R = load(loc.file);
const info = { map: loc.map }; if (loc.map === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
const W = R.match.map.width, H = R.match.map.height;
// --line A|B: follow the final king line of that team (every ancestor; printed with birth rounds)
if (/^line[AB]$/.test(String(idsArg))) {
  const tm = String(idsArg).slice(4), par = new Map(), bornR = new Map(); let fin = null;
  perGame(R, info, { split(p, ch, e, r) { par.set(ch.id, p.id); bornR.set(ch.id, r); }, end(rounds, c) { let k = null; for (const d of c.drag.values()) if (d.team === tm && (!k || d.body.length > k.body.length || (d.body.length === k.body.length && d.id < k.id))) k = d; fin = k ? k.id : -1; } });
  const line = []; for (let x = fin; x !== undefined && x >= 0; x = par.get(x)) line.push(x);
  ids = new Set(line);
  console.log('line (final king first):', line.map(x => '#' + x + '@r' + (bornR.get(x) || 0)).join(' <- '));
}
const man = (a, b) => { const dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
const lines = [`${key} ${loc.map} ${loc.desc}`];
const labels = new Map(), evs = new Map(), tracked = new Set(ids);
const note = (id, s) => { if (!tracked.has(id)) return; const a = evs.get(id) || []; a.push(s); evs.set(id, a); };
let lastRound = -1;
const dropWatch = new Map();
perGame(R, info, {
  turn(d, r, c) {
    if (r !== lastRound) lastRound = r;
    if (!tracked.has(d.id) || r < from || r > to || (r - from) % every) return;
    let k = null; for (const x of c.drag.values()) if (x.team === d.team && (!k || x.body.length > k.body.length || (x.body.length === k.body.length && x.id < k.id))) k = x;
    let eD = 99, eL = 0; for (const x of c.drag.values()) if (x.team !== d.team) { const dd = man(x.body[0], d.body[0]); if (dd < eD) { eD = dd; eL = x.body.length; } }
    let p5 = 0; for (const [t, o] of c.pearls) if (o < 0 && man({ x: t % W, y: (t / W) | 0 }, d.body[0]) <= 5) p5++;
    const h = d.body[0];
    lines.push(`r${r} #${d.id} L${d.body.length} @${h.x},${h.y} king #${k.id} L${k.body.length} dK${man(k.body[0], h)} | enemy ${eD}(L${eL}) | pearls5 ${p5}` + (evs.get(d.id) ? ' | prev: ' + evs.get(d.id).join(', ') : ''));
    evs.delete(d.id);
  },
  indicator(e, r, c) { if (tracked.has(e.id) && r >= from && r <= to) lines.push(`      label #${e.id}: ${(e.text || '').split('|')[0].trim()}`); },
  eat(d, tile, o, r, c) { note(d.id, o < 0 ? 'n' : (c.deaths[o].team === d.team ? 'd' : 'e') + (c.deaths[o].cause === 0 ? 's' : '')); if (o >= 0 && dropWatch.has(o) && r >= from && r <= to + 10) lines.push(`      r${r} drop of #${dropWatch.get(o)} eaten by #${d.id} L${d.body.length} (${d.team === c.deaths[o].team ? 'own' : 'enemy'})`); },
  split(p, ch, e, r, c) { if (tracked.has(p.id)) { if (!lineMode) tracked.add(ch.id); note(p.id, `split -> #${ch.id} L${e.childBody.length} (kept ${e.parentBody.length})`); } },
  death(d, rec, idx, other, r, c) { if (tracked.has(d.id) && r >= from - 5) lines.push(`   r${r} #${d.id} DIES ${CAUSE[rec.cause]} L${rec.len} drops ${rec.drops}` + (other ? ` (other #${other.id} L${other.body.length})` : '')); if (tracked.has(d.id)) dropWatch.set(idx, d.id); },
});
console.log(lines.join('\n'));
