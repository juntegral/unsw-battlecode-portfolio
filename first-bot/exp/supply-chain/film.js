#!/usr/bin/env node
// Stage 3 close reading of the pieces and formations picked by exp/supply-chain/cases.js. Replays only.
// usage (repository root):
//   node exp/supply-chain/film.js piece <key> <dragonId> [--after 30] [--pad 2]
//   node exp/supply-chain/film.js game <key> [--rounds 300,350,400]
//   <key> = <battleId>:<gameId> (data/top) or <set>:<gameId> (data/online).
// Piece film: one line per round from birth - pad to death (or birth + after): head, length, territory (own/neutral/enemy),
//   nearest other own head (id, length, Manhattan), nearest own head >= 8, own heads within 5, enemy heads within 5,
//   natural pearls within 4 steps (static path) and the nearest one, and what happened (eats, splits, death, spawns it was
//   the unique nearest head of). Snapshots (17x11 around the piece) at birth, +10, +20, +30 and the last round.
// Snapshot legend: '*' the piece's head; its team: heads 'p' piece (<= 4) / 'm' mid (5-7) / 'B' big (>= 8), bodies '=';
//   the other team: heads 'x' / 'X' / 'W', bodies '~'; natural pearl 'o', dropped pearl '+'; empty tiles: ',' the piece's
//   territory, '.' the other territory, ':' neutral.
// Game film: at each round, both teams' heads by length and full-map snapshots with the same legend (team A = the first team).
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const X = require(path.join(ROOT, 'exp', 'territory-analysis', 'extract.js'));
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const CAUSE = ['희생', '갇힘', '박힘', '박음', '적 몸', '아군 머리', '시간 초과', '질주 불가'];
const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = tf.makeLoader(tf.viewerSource());

function locate(key) {
  const [a, b] = key.split(':');
  if (/^\d+$/.test(a)) {
    let row = null; for (const l of fs.readFileSync(path.join(ROOT, 'data', 'top', 'index.jsonl'), 'utf8').split('\n')) { if (!l.includes('"gameId":' + b)) continue; try { const r = JSON.parse(l); if (String(r.gameId) === b && String(r.battleId) === a) { row = r; break; } } catch { } }
    return { file: path.join(ROOT, 'data', 'top', a, b + '.replay.gz'), map: row.map, gameId: +b, desc: `A=${row.teamA}, B=${row.teamB}, 승 ${String(row.winner).toUpperCase()}` };
  }
  const dir = path.join(ROOT, 'data', 'online', a), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  const g = (idx.games || idx).find(x => String(x.gameId) === b);
  return { file: path.join(dir, 'M' + b + '.replay'), map: g.mapName, gameId: +b, desc: `우리=${String(g.ourSide).toUpperCase()}, 상대 팀 ${g.opponentTeam}, 승 ${String(g.winner).toUpperCase()}` };
}
const lcode = (L, mine) => L <= 4 ? (mine ? 'p' : 'x') : L <= 7 ? (mine ? 'm' : 'X') : (mine ? 'B' : 'W');
function snapshot(ctx, G, team, center, rx, ry, focusId) {
  const cell = new Map(), rows = [];
  for (const o of ctx.drag.values()) o.body.forEach((s, i) => { const k = G.key(s.x, s.y), mine = o.team === team; cell.set(k, o.id === focusId && i === 0 ? '*' : i === 0 ? lcode(o.body.length, mine) : (mine ? '=' : '~')); });
  const own = team === 'A' ? 1 : 2;
  for (let dy = -ry; dy <= ry; dy++) {
    let row = '    ';
    for (let dx = -rx; dx <= rx; dx++) {
      const x = G.wx(center.x + dx), y = G.wy(center.y + dy), k = G.key(x, y);
      let c = cell.get(k);
      if (!c) { const p = ctx.pearls.get(k); if (p !== undefined) c = p < 0 ? 'o' : '+'; }
      if (!c) { const t = G.terr[k]; c = t === 0 ? ':' : t === own ? ',' : '.'; }
      row += c;
    }
    rows.push(row);
  }
  return rows.join('\n');
}
function man(G, a, b) { let dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); dx = Math.min(dx, G.W - dx); dy = Math.min(dy, G.H - dy); return dx + dy; }

function pieceFilm(key, id) {
  const after = +opt('after', 30), pad = +opt('pad', 2);
  const loc = locate(key), R = load(loc.file), G = X.geometry(R);
  const info = { map: loc.map }; if (loc.map === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
  const lines = [], ev = new Map(); let born = null, team = null, dead = null, last = -1;
  const note = (r, s) => { if (!ev.has(r)) ev.set(r, []); ev.get(r).push(s); };
  const known = new Set(); if (R.match.map.initialTiles) R.match.map.initialTiles.forEach((v, i) => { if (v === 2) known.add(i); });
  const inWin = r => born !== null && r >= born - pad && r <= (dead !== null ? dead : born + after);
  const onRound = (r, ctx) => {
    // spawns of this round whose unique nearest head (static path) is the piece
    const d = ctx.drag.get(id);
    for (const [k, o] of ctx.pearls) { if (o !== -1 || known.has(k)) continue; known.add(k);
      if (!d || !inWin(r)) continue;
      const dist = new Int16Array(G.N).fill(-1), q = [k]; dist[k] = 0; let best = 99, who = [];
      const heads = new Map(); for (const x of ctx.drag.values()) heads.set(G.key(x.body[0].x, x.body[0].y), x);
      for (let i = 0; i < q.length; i++) { const t = q[i]; if (dist[t] > best || dist[t] > 12) break; const hd = heads.get(t); if (hd) { if (dist[t] < best) { best = dist[t]; who = [hd]; } else who.push(hd); }
        for (let j = 0; j < 4; j++) { const u = G.nb[t * 4 + j]; if (u < 0 || dist[u] >= 0) continue; dist[u] = dist[t] + 1; q.push(u); } }
      if (who.length && who.some(x => x.id === id)) note(r, `생성 (${k % G.W},${(k / G.W) | 0}) 가장 가까운 머리 ${who.map(x => '#' + x.id + (x.team === team ? '' : '적')).join('/')} 거리 ${best}`);
    }
    if (!d || !inWin(r)) return;
    const h = d.body[0];
    let nn = null, nb = null, own5 = 0; const en5 = [];
    for (const o of ctx.drag.values()) { if (o === d) continue; const m = man(G, o.body[0], h);
      if (o.team === team) { if (!nn || m < nn.m) nn = { o, m }; if (o.body.length >= 8 && (!nb || m < nb.m)) nb = { o, m }; if (m <= 5) own5++; }
      else if (m <= 5) en5.push(`#${o.id}L${o.body.length}d${m}`); }
    // natural pearls within 4 (static path)
    const dist = new Int16Array(G.N).fill(-1), q = [G.key(h.x, h.y)]; dist[q[0]] = 0; let np = 0, nd = 99;
    for (let i = 0; i < q.length; i++) { const t = q[i]; if (ctx.pearls.get(t) === -1 && dist[t] > 0) { np++; nd = Math.min(nd, dist[t]); } if (dist[t] >= 4) continue; for (let j = 0; j < 4; j++) { const u = G.nb[t * 4 + j]; if (u < 0 || dist[u] >= 0) continue; dist[u] = dist[t] + 1; q.push(u); } }
    const own = team === 'A' ? 1 : 2, t = G.terr[G.key(h.x, h.y)], terr = t === 0 ? '중립' : t === own ? '자기' : '적';
    lines.push(`r${r} (${h.x},${h.y}) L${d.body.length} ${terr} | 가까운 아군 ${nn ? '#' + nn.o.id + 'L' + nn.o.body.length + 'd' + nn.m : '-'} | 큰 아군 ${nb ? '#' + nb.o.id + 'L' + nb.o.body.length + 'd' + nb.m : '-'} | 5칸 안 아군 ${own5} 적 ${en5.join(' ') || '-'} | 자연 진주 4걸음 안 ${np}${np ? ' (가장 가까운 ' + nd + ')' : ''}${ev.has(r - 1) ? ' | ' + ev.get(r - 1).join('; ') : ''}`);
    const rel = r - born;
    if (rel === 0 || rel === 10 || rel === 20 || rel === 30) lines.push(`  스냅숏 r${r} (태어난 뒤 ${rel})\n` + snapshot(ctx, G, team, h, 8, 5, id));
  };
  const hooks = {
    turn(d, r, ctx) { if (r !== last) { last = r; onRound(r, ctx); } },
    split(p, ch, e, r) { if (ch.id === id) { born = r; team = ch.team; note(r, `태어남: 부모 #${p.id} (분열 전 L${p.body.length + ch.body.length})`); } else if (p.id === id) note(r, `분열 → #${ch.id} L${ch.body.length}`); },
    eat(d, t, o, r) { if (d.id === id) note(r, `먹음 (${t % G.W},${(t / G.W) | 0}) ${o < 0 ? '자연' : '사망 진주'}`); },
    death(d, rec, idx, other, r, ctx) { if (d.id === id) { dead = r; note(r, `죽음: ${CAUSE[rec.cause]} L${rec.len}${other ? ' (#' + other.id + ' L' + other.body.length + (other.team === d.team ? ' 아군' : ' 적') + ')' : ''}`); lines.push(`  스냅숏 r${r} (죽는 라운드, 죽기 직전)\n` + snapshot(ctx, G, team, d.body[0], 8, 5, id)); pendingDrop = idx; } },
  };
  let pendingDrop = -1; const dropEat = [];
  const hooks2 = { ...hooks, eat(d, t, o, r, ctx) { hooks.eat(d, t, o, r, ctx); if (o === pendingDrop && pendingDrop >= 0) dropEat.push(`#${d.id}${d.team === team ? '' : '적'} L${d.body.length} r${r}`); } };
  ML.perGame(R, info, hooks2);
  const tail = [...ev.entries()].filter(([r]) => r >= (dead !== null ? dead : born + after)).map(([r, v]) => `  (r${r}) ${v.join('; ')}`);
  return [`# 조각 기보: ${key} · ${loc.map} · 드래곤 #${id} (팀 ${team}) · ${loc.desc}`, ...lines, ...tail, dead !== null ? `  떨군 진주를 먹은 드래곤: ${dropEat.join(', ') || '없음'}` : ''].join('\n');
}

function gameFilm(key) {
  const rounds = new Set((opt('rounds', '300,350,400')).split(',').map(Number));
  const loc = locate(key), R = load(loc.file), G = X.geometry(R);
  const info = { map: loc.map }; if (loc.map === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
  const lines = [`# 판 기보: ${key} · ${loc.map} · ${loc.desc}`, '범례: A팀 머리 p(<=4)/m(5-7)/B(>=8), 몸 =; B팀 머리 x/X/W, 몸 ~; 자연 진주 o, 사망 진주 +; 빈칸 , A 영토 . B 영토 : 중립'];
  let last = -1;
  ML.perGame(R, info, { turn(d, r, ctx) {
    if (r === last) return; last = r; if (!rounds.has(r)) return;
    for (const tm of ['A', 'B']) { const L = [...ctx.drag.values()].filter(o => o.team === tm).map(o => o.body.length).sort((a, b) => b - a); lines.push(`r${r} 팀 ${tm}: ${L.length}마리, 길이 ${L.join(',')}`); }
    lines.push(snapshot(ctx, G, 'A', { x: (G.W / 2) | 0, y: (G.H / 2) | 0 }, (G.W / 2) | 0, (G.H / 2) | 0, -1));
  } });
  return lines.join('\n');
}

if (argv[0] === 'piece') console.log(pieceFilm(argv[1], +argv[2]));
else if (argv[0] === 'game') console.log(gameFilm(argv[1]));
else { console.error('usage: see the header of exp/supply-chain/film.js'); process.exit(2); }
