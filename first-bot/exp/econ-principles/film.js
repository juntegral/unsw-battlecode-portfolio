#!/usr/bin/env node
// Stage 3 close reading for research/observations/economy-principles.md. Replays only.
// usage (repository root):
//   node exp/econ-principles/film.js <key> <round> <dragonId | KA | KB> [--after 20] [--rad 8]   (KA/KB: that team's king at the round's first turn;
//   the snapshot is then taken at the round's first turn, since the king may die before its own turn)
//   <key> = <battleId>:<gameId> (data/top) or <set>:<gameId> (data/online).
// Prints, at the dragon's turn start in <round>: the 17x17 window around its head, every head within Manhattan <rad>
// (team, id, length, distance), our label (online), then what the dragon did, every death in that round and the next
// <after> rounds within Manhattan <rad> of the dragon's head, and who ate each dropped pearl (team, id, length, round).
// Legend: the dragon's team: head digit = length class (2,3,4 ... '9' for >= 9), body '='; the other team: head letter
//   a=2 b=3 c=4 d=5-7 e=8-14 f=15+, body '~'; '*' = the dragon's head; natural pearl 'o', dropped pearl '+'; empty '.'.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const CAUSE = ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'];

function locate(key) {
  const [a, b] = key.split(':');
  if (/^\d+$/.test(a)) {
    let row = null;
    for (const l of fs.readFileSync(path.join(ROOT, 'data', 'top', 'index.jsonl'), 'utf8').split('\n')) { if (!l.includes('"gameId":' + b)) continue; try { const r = JSON.parse(l); if (String(r.gameId) === b && String(r.battleId) === a) { row = r; break; } } catch { /* skip */ } }
    return { file: path.join(ROOT, 'data', 'top', a, b + '.replay.gz'), map: row.map, desc: `A=${row.teamA} (${row.eloA}), B=${row.teamB} (${row.eloB}), winner ${String(row.winner).toUpperCase()}`, us: null };
  }
  const idx = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'online', a, 'index.json'), 'utf8'));
  const g = (idx.games || idx).find(x => String(x.gameId) === b);
  return { file: path.join(ROOT, 'data', 'online', a, 'M' + b + '.replay'), map: g.mapName, desc: `${a} side ${g.ourSide} vs team ${g.opponentTeam}, winner ${String(g.winner).toUpperCase()}`, us: String(g.ourSide).toUpperCase() };
}

function main() {
  const key = argv[0], R0 = +argv[1], AFTER = +opt('after', 20), RAD = +opt('rad', 8);
  let ID = /^K[AB]$/.test(argv[2]) ? null : +argv[2]; const KTEAM = /^K[AB]$/.test(argv[2]) ? argv[2][1] : null; // K<team>: that team's king at r0
  const loc = locate(key);
  const R = tf.makeLoader(tf.viewerSource())(loc.file);
  const W = R.match.map.width, H = R.match.map.height;
  const md = (a, b) => { let dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); if (W - dx < dx) dx = W - dx; if (H - dy < dy) dy = H - dy; return dx + dy; };
  const out = [];
  out.push(`# ${key} ${loc.map} ${W}x${H}; ${loc.desc}; focus dragon ${argv[2]} at r${R0}`);
  let center = null, team = null, shown = false, label = null;
  const watch = new Map(); // death idx -> {r, id, team, L, cause, pos, eaten: []}
  const info = { map: loc.map }; if (loc.map === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
  const hooks = {
    indicator(e, r) { if (r === R0 && e.id === ID) label = e.text; },
    turn(d0, r, ctx) {
      if (!shown && r === R0 && KTEAM && ID === null) { const k = ctx.kingOf(KTEAM); if (k) ID = k.id; }
      // K mode: snapshot at the round's first turn (the king may die before its own turn)
      const d = KTEAM && r === R0 && !shown ? ctx.drag.get(ID) : d0;
      if (!d || shown || r !== R0 || d.id !== ID) return;
      shown = true; center = { x: d.body[0].x, y: d.body[0].y }; team = d.team;
      const grid = [];
      for (let dy = -8; dy <= 8; dy++) { const row = []; for (let dx = -8; dx <= 8; dx++) row.push('.'); grid.push(row); }
      const put = (p, ch) => { let dx = p.x - center.x, dy = p.y - center.y; if (dx > W / 2) dx -= W; if (dx < -W / 2) dx += W; if (dy > H / 2) dy -= H; if (dy < -H / 2) dy += H; if (Math.abs(dx) <= 8 && Math.abs(dy) <= 8) grid[dy + 8][dx + 8] = ch; };
      for (const [k, o] of ctx.pearls) put({ x: k % W, y: (k / W) | 0 }, o < 0 ? 'o' : '+');
      const heads = [];
      for (const o of ctx.drag.values()) {
        const own = o.team === team, L = o.body.length;
        for (let i = 1; i < o.body.length; i++) put(o.body[i], own ? '=' : '~');
        const ch = own ? (L >= 9 ? '9' : String(L)) : (L <= 2 ? 'a' : L === 3 ? 'b' : L === 4 ? 'c' : L <= 7 ? 'd' : L <= 14 ? 'e' : 'f');
        put(o.body[0], o.id === ID ? '*' : ch);
        const dd = md(o.body[0], center); if (dd <= RAD) heads.push(`${own ? 'own' : 'ENEMY'} #${o.id} L${L} d${dd}${ctx.isKingNow(o) ? ' KING' : ''}`);
      }
      out.push(`turn start r${R0}: #${ID} team ${team} L${d.body.length} head (${center.x},${center.y})${ctx.isKingNow(d) ? ' KING' : ''}; units own ${[...ctx.drag.values()].filter(o => o.team === team).length}, enemy ${[...ctx.drag.values()].filter(o => o.team !== team).length}`);
      out.push(grid.map(r => r.join('')).join('\n'));
      out.push('heads within ' + RAD + ': ' + heads.sort((a, b) => +a.split(' d')[1].split(' ')[0] - +b.split(' d')[1].split(' ')[0]).join('; '));
    },
    action(d, e, r) { if (r === R0 && d.id === ID) { const a = e.action; out.push(`action: ${a ? a.kind + (a.steps ? ' ' + a.steps.join('') : '') + (a.kind === 'split' ? ' ' + JSON.stringify(a) : '') : 'none'}${label ? ' | label "' + label + '"' : ''}${d.fate ? ' | fate ' + JSON.stringify(d.fate) : ''}`); } },
    death(d, rec, idx, other, r, ctx) {
      if (!center || r < R0 || r > R0 + AFTER) return;
      if (md(d.body[0], center) > RAD) return;
      watch.set(idx, { r, id: d.id, team: d.team, L: d.body.length, cause: CAUSE[rec.cause], other: other ? `#${other.id} ${other.team} L${other.body.length}` : '', eaten: [] });
    },
    eat(d, k, o, r) { if (watch.has(o)) watch.get(o).eaten.push(`${d.team === team ? 'own' : 'ENEMY'} #${d.id} L${d.body.length} r${r}`); },
  };
  ML.perGame(R, info, hooks);
  for (const [idx, w] of watch) out.push(`death r${w.r} #${w.id} ${w.team === team ? 'own' : 'ENEMY'} L${w.L} ${w.cause}${w.other ? ' (other ' + w.other + ')' : ''}: drops ${Math.ceil(w.L / 2)} eaten by ${w.eaten.join(', ') || 'nobody'}`);
  console.log(out.join('\n'));
}
main();
