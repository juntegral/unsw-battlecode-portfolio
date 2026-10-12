#!/usr/bin/env node
// film.js — stage 3 close reading of selected replays (classes.js picks). Replays only; no games, no network.
// usage (repository root):
//   node exp/territory-analysis/film.js raid <key> <dragonId> <r0> <r1> [--pad 3] [--snaps r,r,...]
//   node exp/territory-analysis/film.js game <key> <team A|B> [--every 25] [--snaps 100,250]
//   node exp/territory-analysis/film.js picks [exp/territory-analysis/classes.json] [--only <substring>]
//   <key> = <battleId>:<gameId> (data/top) or <set>:<gameId> (data/online).
// Raid film: one line per round for the raider (head, length, depth inside, what it ate), the defender heads within 6
// steps (id, length, distance) and its own team's heads within 6, then 17x11 snapshots around the raider.
// Snapshot legend: '*' the raider's head, raider team heads 'R' / bodies 'r', defender heads 'D' / bodies 'd',
// natural pearl 'o', dropped pearl '+', empty fountain tile 'F'; empty tiles: '.' defender territory, ',' raider
// territory, ':' neutral.
// Game film: every N rounds, for the chosen team: units, heads in own / enemy territory, enemy heads inside its
// territory, own-territory pearls spawned / eaten by it / eaten by the enemy in the window, then full-map snapshots
// (heads 'A'/'B' uppercase for the chosen team's side as given, bodies lowercase).
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const X = require('./extract.js');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const CAUSE = ['희생', '갇힘', '박힘', '박음', '적 몸', '아군 머리', '시간 초과', '질주 불가'];
let loadFn = null;
const loader = () => { if (!loadFn) { const tf = require(path.join(ROOT, 'tools', 'top_features.js')); loadFn = tf.makeLoader(tf.viewerSource()); } return loadFn; };

function locate(key) {
  const [a, b] = key.split(':');
  if (/^\d+$/.test(a)) {
    const f = path.join(ROOT, 'data', 'top', a, b + '.replay.gz');
    let row = null; for (const l of fs.readFileSync(path.join(ROOT, 'data', 'top', 'index.jsonl'), 'utf8').split('\n')) { if (!l.includes('"gameId":' + b)) continue; try { const r = JSON.parse(l); if (String(r.gameId) === b && String(r.battleId) === a) { row = r; break; } } catch { } }
    return { file: f, map: row ? row.map : null, gameId: +b, teamA: row && row.teamA, teamB: row && row.teamB, winner: row && row.winner };
  }
  const dir = path.join(ROOT, 'data', 'online', a), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  const g = (idx.games || idx).find(x => String(x.gameId) === b);
  return { file: path.join(dir, 'M' + b + '.replay'), map: g.mapName, gameId: +b, us: String(g.ourSide).toUpperCase(), opp: g.opponentTeam, winner: g.winner };
}

// run the reconstruction and call snap(round, ctx) at the first turn of every round
function replay(key, onRound, hooksExtra = {}) {
  const loc = locate(key), R = loader()(loc.file);
  const M = R.match.map, W = M.width, H = M.height, N = W * H;
  const G = X.geometry(R);
  const V = X.variantOf(loc.map, loc.gameId, R, M.initialDragons.length);
  const gf = X.fileOf(loc.map, V.tag), gg = gf && fs.existsSync(gf) ? X.gapsOfFile(gf) : null;
  const fount = new Uint8Array(N);
  if (gg && gg.w === W && gg.h === H) for (let k = 0; k < N; k++) { const g = gg.g[k]; if (g && g[1] > 0 && (g[0] + g[1]) / 2 <= 12) fount[k] = 1; }
  const info = { map: loc.map }; if (loc.map === 'Prisoners Dilemma') info.variant = M.initialDragons.length === 10 ? 'PD10' : 'PD6';
  let last = -1;
  const hooks = {
    ...hooksExtra,
    turn(d, r, ctx) { if (r !== last) { last = r; onRound(r, ctx); } if (hooksExtra.turn) hooksExtra.turn(d, r, ctx); },
  };
  const g = ML.perGame(R, info, hooks);
  return { loc, R, G, fount, W, H, N, g, V };
}
// static path distance from one tile (bodies ignored)
function bfsFrom(G, src, radius) {
  const d = new Int16Array(G.N).fill(-1), q = [src]; d[src] = 0;
  for (let i = 0; i < q.length; i++) { const k = q[i]; if (d[k] >= radius) continue; for (let j = 0; j < 4; j++) { const u = G.nb[k * 4 + j]; if (u < 0 || d[u] >= 0) continue; d[u] = d[k] + 1; q.push(u); } }
  return d;
}

function raidFilm(key, id, r0, r1, pad) {
  const lines = [], snaps = new Set((opt('snaps', '') || '').split(',').filter(Boolean).map(Number));
  snaps.add(r0); snaps.add(Math.round((r0 + r1) / 2)); snaps.add(r1);
  let raiderTeam = null, G0 = null, fountRef = null, W0 = 0, H0 = 0;
  const eats = new Map(), events = new Map();
  const note = (r, s) => { if (!events.has(r)) events.set(r, []); events.get(r).push(s); };
  const long = r1 - r0 > 45;
  const onRound = (r, ctx) => {
    if (r < r0 - pad || r > r1 + pad) return;
    if (long && r > r0 + 25 && r < r1 - 6 && (r - r0) % 5 !== 0 && !snaps.has(r)) return; // long raids: every 5th round in the middle
    const d = ctx.all.get(id); if (!d) return;
    raiderTeam = d.team;
    const alive = ctx.drag.has(id);
    if (!alive) { lines.push(`r${r}: #${id} 없음`); return; }
    const h = d.body[0], k = G0.key(h.x, h.y);
    const depth = raiderTeam === 'A' ? -G0.marginA[k] : G0.marginA[k];
    const dist = bfsFrom(G0, k, 6);
    const def = [], own = [];
    for (const o of ctx.drag.values()) { if (o === d) continue; const z = dist[G0.key(o.body[0].x, o.body[0].y)]; if (z < 0) continue; (o.team === raiderTeam ? own : def).push(`#${o.id}L${o.body.length}d${z}`); }
    let pearls = 0, fp = 0; for (const [t, o] of ctx.pearls) { if (dist[t] >= 0 && dist[t] <= 3) { pearls++; if (fountRef[t]) fp++; } }
    lines.push(`r${r}: (${h.x},${h.y}) L${d.body.length} 깊이${depth} | 진주3칸안 ${pearls}(샘${fp}) | 수비 ${def.join(' ') || '-'} | 아군 ${own.join(' ') || '-'}${events.has(r - 1) ? ' | ' + events.get(r - 1).join('; ') : ''}`);
    if (snaps.has(r)) lines.push(snapshot(ctx, G0, fountRef, W0, H0, h, id, raiderTeam, 8, 5, `스냅숏 r${r}`));
  };
  const hooksExtra = {
    eat(d, t, o, r, ctx) { if (d.id === id || (raiderTeam && d.team !== raiderTeam && r >= r0 - pad && r <= r1 + pad)) { const x = t % W0, y = (t / W0) | 0; note(r, `${d.id === id ? '침입자' : '수비 #' + d.id} 먹음 (${x},${y})${o < 0 ? (fountRef[t] ? '샘' : '') : '(사망 진주)'}`); } },
    split(p, ch, e, r) { if (p.id === id) note(r, `분열 → 새끼 #${ch.id} L${ch.body.length}`); },
    death(d, rec, idx, other, r) { if (d.id === id) note(r, `침입자 죽음: ${CAUSE[rec.cause]}${other ? ' (상대 #' + other.id + ' L' + other.body.length + (other.team === d.team ? ' 아군' : '') + ')' : ''}`); else if (other && other.id === id) note(r, `#${d.id} L${rec.len} 죽음(${CAUSE[rec.cause]}), 침입자와 접촉`); },
  };
  // geometry first (needed by onRound): a light pre-pass
  const loc = locate(key), R = loader()(loc.file);
  G0 = X.geometry(R); W0 = G0.W; H0 = G0.H;
  const V = X.variantOf(loc.map, loc.gameId, R, R.match.map.initialDragons.length);
  const gf = X.fileOf(loc.map, V.tag), gg = gf && fs.existsSync(gf) ? X.gapsOfFile(gf) : null;
  fountRef = new Uint8Array(G0.N); if (gg && gg.w === W0 && gg.h === H0) for (let k = 0; k < G0.N; k++) { const g = gg.g[k]; if (g && g[1] > 0 && (g[0] + g[1]) / 2 <= 12) fountRef[k] = 1; }
  const info = { map: loc.map }; if (loc.map === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
  let last = -1;
  ML.perGame(R, info, { ...hooksExtra, turn(d, r, ctx) { if (r !== last) { last = r; onRound(r, ctx); } } });
  const head = `# 침입 기보: ${key} · ${loc.map} (${V.tag}) · 드래곤 #${id} (팀 ${raiderTeam}) r${r0}–${r1}` + (loc.teamA ? ` · A=${loc.teamA}, B=${loc.teamB}, 승 ${loc.winner}` : loc.us ? ` · 우리=${loc.us}, 상대 ${loc.opp}, 승 ${loc.winner}` : '');
  const tail = [...events.entries()].filter(([r]) => r >= r1 + pad && r <= r1 + 20).map(([r, v]) => `  (r${r}) ${v.join('; ')}`);
  const mid = long ? [...events.entries()].filter(([r]) => r > r0 + 25 && r < r1 - 6).map(([r, v]) => `  (r${r}) ${v.join('; ')}`) : [];
  return [head, ...lines, ...(mid.length ? ['  중간 사건(5라운드마다 줄에 없는 라운드):', ...mid] : []), ...(tail.length ? ['  뒤 20라운드:', ...tail] : [])].join('\n');
}
function snapshot(ctx, G, fount, W, H, center, id, team, rx, ry, title) {
  const out = [`  ${title}`];
  const cell = new Map();
  for (const o of ctx.drag.values()) o.body.forEach((s, i) => { const k = G.key(s.x, s.y); const mine = o.team === team; cell.set(k, o.id === id && i === 0 ? '*' : i === 0 ? (mine ? 'R' : 'D') : (mine ? 'r' : 'd')); });
  for (let dy = -ry; dy <= ry; dy++) {
    let row = '  ';
    for (let dx = -rx; dx <= rx; dx++) {
      const x = G.wx(center.x + dx), y = G.wy(center.y + dy), k = G.key(x, y);
      let c = cell.get(k);
      if (!c) { const p = ctx.pearls.get(k); if (p !== undefined) c = p < 0 ? 'o' : '+'; }
      if (!c && fount[k]) c = 'F';
      if (!c) { const t = G.terr[k], own = team === 'A' ? 1 : 2; c = t === 0 ? ':' : t === own ? ',' : '.'; }
      row += c;
    }
    out.push(row);
  }
  return out.join('\n');
}

function gameFilm(key, team, every, snapRounds) {
  const lines = [];
  const loc = locate(key), R = loader()(loc.file);
  const G = X.geometry(R), W = G.W, H = G.H, N = G.N;
  const V = X.variantOf(loc.map, loc.gameId, R, R.match.map.initialDragons.length);
  const gf = X.fileOf(loc.map, V.tag), gg = gf && fs.existsSync(gf) ? X.gapsOfFile(gf) : null;
  const fount = new Uint8Array(N); if (gg && gg.w === W && gg.h === H) for (let k = 0; k < N; k++) { const g = gg.g[k]; if (g && g[1] > 0 && (g[0] + g[1]) / 2 <= 12) fount[k] = 1; }
  const own = team === 'A' ? 1 : 2, en = 3 - own;
  const win = { sp: 0, us: 0, them: 0, themF: 0, themL: [0, 0, 0, 0], usInEn: 0, known: new Map() };
  let lastR = -1;
  const info = { map: loc.map }; if (loc.map === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
  const flush = (r, ctx) => {
    let u = 0, uOwn = 0, uEn = 0, lens = [], eIn = 0, eLens = [];
    for (const d of ctx.drag.values()) { const k = G.key(d.body[0].x, d.body[0].y); if (d.team === team) { u++; lens.push(d.body.length); if (G.terr[k] === own) uOwn++; else if (G.terr[k] === en) uEn++; } else if (G.terr[k] === own) { eIn++; eLens.push(d.body.length); } }
    lens.sort((a, b) => b - a); eLens.sort((a, b) => b - a);
    lines.push(`r${r - every}–${r - 1}: 우리 영토 생성 ${win.sp} → 우리 ${win.us}, 상대 ${win.them}(샘 ${win.themF}; 먹은 적 L2–3 ${win.themL[0]}, L4–7 ${win.themL[1]}, L8+ ${win.themL[2] + win.themL[3]}) | r${r}: 우리 ${u}마리(영토 안 ${uOwn}, 적 영토 ${uEn}) 길이 ${lens.slice(0, 6).join(',')}${lens.length > 6 ? ',…' : ''} | 우리 영토 안 적 머리 ${eIn}(길이 ${eLens.slice(0, 8).join(',')}${eLens.length > 8 ? ',…' : ''})`);
    win.sp = 0; win.us = 0; win.them = 0; win.themF = 0; win.themL = [0, 0, 0, 0];
  };
  ML.perGame(R, info, {
    turn(d, r, ctx) {
      if (r === lastR) return; lastR = r;
      for (const [k, o] of ctx.pearls) if (o === -1 && !win.known.has(k)) { win.known.set(k, r); if (G.terr[k] === own) win.sp++; }
      if (r > 0 && r % every === 0) flush(r, ctx);
      if (snapRounds.includes(r)) lines.push(fullMap(ctx, G, fount, team, `전체 지도 r${r} (우리=${team}: 머리 'U' 몸 'u', 상대 머리 'E' 몸 'e', 진주 'o', 빈 샘 'F', 빈 칸: 우리 영토 ',' 상대 영토 '.' 중립 ':')`));
    },
    eat(d, k, o) { if (o < 0) { win.known.delete(k); if (G.terr[k] === own) { if (d.team === team) win.us++; else { win.them++; if (fount[k]) win.themF++; const L = d.body.length; win.themL[L <= 3 ? 0 : L <= 7 ? 1 : L <= 15 ? 2 : 3]++; } } } },
  });
  const head = `# 경기 기보: ${key} · ${loc.map} (${V.tag}) · 팀 ${team}` + (loc.us ? ` (우리=${loc.us}, 상대 ${loc.opp}, 승 ${loc.winner})` : ` (A=${loc.teamA}, B=${loc.teamB}, 승 ${loc.winner})`);
  return [head, ...lines].join('\n');
}
function fullMap(ctx, G, fount, team, title) {
  const cell = new Map();
  for (const o of ctx.drag.values()) o.body.forEach((s, i) => { const k = G.key(s.x, s.y); cell.set(k, o.team === team ? (i === 0 ? 'U' : 'u') : (i === 0 ? 'E' : 'e')); });
  const own = team === 'A' ? 1 : 2, out = ['  ' + title];
  for (let y = 0; y < G.H; y++) { let row = '  '; for (let x = 0; x < G.W; x++) { const k = G.key(x, y); let c = cell.get(k); if (!c) { const p = ctx.pearls.get(k); if (p !== undefined) c = 'o'; } if (!c && fount[k]) c = 'F'; if (!c) { const t = G.terr[k]; c = t === 0 ? ':' : t === own ? ',' : '.'; } row += c; } out.push(row); }
  return out.join('\n');
}

function main() {
  const cmd = argv[0];
  if (cmd === 'raid') console.log(raidFilm(argv[1], +argv[2], +argv[3], +argv[4], +opt('pad', 3)));
  else if (cmd === 'game') console.log(gameFilm(argv[1], argv[2], +opt('every', 25), (opt('snaps', '100,250')).split(',').map(Number)));
  else if (cmd === 'picks') {
    const J = JSON.parse(fs.readFileSync(path.resolve(ROOT, argv[1] && !argv[1].startsWith('--') ? argv[1] : 'exp/territory-analysis/classes.json'), 'utf8'));
    const only = opt('only', null);
    for (const p of J.picks) {
      if (only && !(p.hk + ' ' + p.type).includes(only)) continue;
      const key = p.src === 'top' ? `${p.battleId}:${p.gameId}` : `${p.set}:${p.gameId}`;
      console.log(`\n=== ${p.hk} · ${p.type} · 크기 ${p.n}`);
      if (p.type.startsWith('raid')) console.log(raidFilm(key, p.id, p.r0, p.r1, +opt('pad', 2)));
      else console.log(gameFilm(key, p.ti === 0 ? 'A' : 'B', +opt('every', 25), (opt('snaps', '100,250')).split(',').map(Number)));
    }
  } else { console.error('usage: see the header of film.js'); process.exit(2); }
}
main();
