#!/usr/bin/env node
'use strict';
// fountain_keepers.js — who harvests a team's corridor fountains on Autarky and Prisoners Dilemma (2026-09-30 online analysis).
// Reads replays only.
// usage (repository root):
//   node exp/online-analysis/fountain_keepers.js [--sets baseline-r1,baseline-r1b,baseline-r1c,px-king-v2-online] [--top] [--out file.json]
// Fountains as exp/cand-escape1/fountain_online.js: tiles with max spawn gap <= 5 within one tile of the team's start line
// (maps/online-20260927/<map>.map; the 10-dragon Prisoners Dilemma has the same tiles). For every natural pearl eaten on a
// team's own fountains it records the eater: its length before eating, whether it is the start lineage (longest start
// dragon, then the longer piece at each split), and the round. Per team it reports: own-fountain natural eaten, distinct
// eaters, the share of the top eater, eater length classes, the lineage's share, pearls taken by the other team, and
// "keeper rounds": rounds in which the team has a dragon head within one tile of its start line.
// Online sets: side = our team (583). --top: the snapshot's top-team games (SSS excluded), both teams, labelled winner/loser.
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const SETS = opt('sets', 'baseline-r1,baseline-r1b,baseline-r1c,px-king-v2-online').split(',');
const MAPS = { Autarky: 'autarky.map', 'Prisoners Dilemma': 'prisoners_dilemma.map' };

function study(file, mapName, label) {
  const R = load(file), M = R.match.map, W = M.width, H = M.height;
  const gaps = fs.readFileSync(path.join(ROOT, 'maps/online-20260927', MAPS[mapName]), 'utf8').split('\n').filter(l => l.startsWith('TILE ')).map(l => l.trim().split(/\s+/).slice(1).map(Number));
  const start = {}, fount = {}, col = {};
  for (const t of ['A', 'B']) {
    const d = M.initialDragons.filter(x => x.team === t).sort((a, b) => b.body.length - a.body.length || a.id - b.id)[0];
    start[t] = d.id; col[t] = d.body[0].x; fount[t] = new Set();
    if (!d.body.every(s => s.x === d.body[0].x)) continue;
    for (const [x, y, , mx] of gaps) if (mx >= 1 && mx <= 5 && Math.abs(x - d.body[0].x) <= 1) fount[t].add(y * W + x);
  }
  const team = new Map(), len = new Map(), head = new Map(), lin = { A: start.A, B: start.B };
  for (const d of M.initialDragons) { team.set(d.id, d.team); len.set(d.id, d.body.length); head.set(d.id, d.body[0].y * W + d.body[0].x); }
  const pearls = new Map(), spawnAt = new Map(); let drop = false, round = -1, cur = -1;
  const T = {}; for (const t of ['A', 'B']) T[t] = { eaters: new Map(), lens: [], lin: 0, nat: 0, stolen: 0, keeper: 0, rounds: 0, stolenByWin: new Array(10).fill(0) };
  for (const e of R.events) {
    if (drop && !(e.type === 'tileChange' && e.hasPearl)) drop = false;
    switch (e.type) {
      case 'roundStart':
        round = e.round;
        for (const t of ['A', 'B']) {
          T[t].rounds++;
          for (const [id, h] of head) if (team.get(id) === t) { const dx = Math.abs(h % W - col[t]); if (Math.min(dx, W - dx) <= 1) { T[t].keeper++; break; } }
        }
        break;
      case 'turnStart': cur = e.id; break;
      case 'dragonAction': if (e.action && e.action.kind === 'move' && len.has(e.id)) len.set(e.id, len.get(e.id) - (e.action.steps.length - 1)); break;   // sprint cost
      case 'dragonUpdate': { head.set(e.id, e.head.y * W + e.head.x); break; }
      case 'dragonSplit':
        team.set(e.childId, e.team); len.set(e.childId, e.childBody.length); len.set(e.parentId, e.parentBody.length);
        head.set(e.childId, e.childBody[0].y * W + e.childBody[0].x); head.set(e.parentId, e.parentBody[0].y * W + e.parentBody[0].x);
        for (const t of ['A', 'B']) if (lin[t] === e.parentId && e.childBody.length >= e.parentBody.length) lin[t] = e.childId;
        break;
      case 'dragonDeath': drop = true; team.delete(e.id); head.delete(e.id); for (const t of ['A', 'B']) if (lin[t] === e.id) lin[t] = -1; break;
      case 'tileChange': {
        const k = e.tile.y * W + e.tile.x;
        if (e.hasPearl) { pearls.set(k, drop ? 'c' : 'n'); if (!drop && round >= 0) spawnAt.set(k, (spawnAt.get(k) || 0) + 1); break; }
        const o = pearls.get(k) || 'n'; pearls.delete(k);
        const t = team.get(cur); if (!t || round < 0) break;
        if (len.has(cur)) len.set(cur, len.get(cur) + 1);           // eating grows the eater by one
        if (o !== 'n') break;
        for (const own of ['A', 'B']) {
          if (!fount[own].has(k)) continue;
          if (own === t) { const S = T[t]; S.nat++; S.eaters.set(cur, (S.eaters.get(cur) || 0) + 1); S.lens.push(len.get(cur) - 1); if (cur === lin[t]) S.lin++; }
          else { T[own].stolen++; T[own].stolenByWin[Math.min(9, Math.floor(round / 50))]++; }
        }
        break;
      }
      default: break;
    }
  }
  const out = {};
  for (const t of ['A', 'B']) {
    const S = T[t], top = Math.max(0, ...S.eaters.values());
    out[t] = { nat: S.nat, eaters: S.eaters.size, topShare: S.nat ? top / S.nat : null, lin: S.lin, stolen: S.stolen, stolenByWin: S.stolenByWin,
      small: S.lens.filter(x => x <= 4).length, mid: S.lens.filter(x => x >= 5 && x <= 10).length, big: S.lens.filter(x => x > 10).length, keeperShare: S.keeper / Math.max(1, S.rounds) };
  }
  const spawns = {}; for (const [k, n] of spawnAt) spawns[(k % W) + ',' + Math.floor(k / W)] = n;
  return { label, map: mapName, nInit: M.initialDragons.length, winner: R.result.winner, rounds: R.events.filter(e => e.type === 'roundStart').length, A: out.A, B: out.B, spawns };
}

const rows = [];
for (const set of SETS) {
  const dir = path.join(ROOT, 'data', 'online', set);
  for (const g of JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8')).games) {
    if (!MAPS[g.mapName]) continue;
    const r = study(path.join(dir, `M${g.gameId}.replay`), g.mapName, set);
    const us = String(g.ourSide).toUpperCase(), them = us === 'A' ? 'B' : 'A';
    rows.push({ set, game: g.gameId, map: g.mapName, variant: g.mapName === 'Prisoners Dilemma' ? (r.nInit === 10 ? 'PD10' : 'PD6') : 'Autarky', opp: g.opponentTeam, win: g.ourWin ? 1 : 0, rounds: r.rounds, us: r[us], them: r[them], spawns: r.spawns });
  }
}
if (argv.includes('--top')) {
  const keys = new Set(fs.readFileSync(path.join(ROOT, 'data/top/snapshot-20260929a.keys'), 'utf8').trim().split('\n'));
  for (const l of fs.readFileSync(path.join(ROOT, 'data/top/features.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue;
    const m = JSON.parse(l).meta;
    if (!keys.has(m.battleId + ':' + m.gameId) || !MAPS[m.map]) continue;
    if (m.teams.A.name === 'SSS' || m.teams.B.name === 'SSS' || (m.winner !== 'A' && m.winner !== 'B')) continue;
    const r = study(path.join(ROOT, 'data/top', String(m.battleId), m.gameId + '.replay.gz'), m.map, 'top');
    const w = m.winner, lz = w === 'A' ? 'B' : 'A';
    rows.push({ set: 'top', game: m.gameId, map: m.map, variant: m.map === 'Prisoners Dilemma' ? (r.nInit === 10 ? 'PD10' : 'PD6') : 'Autarky', opp: m.teams[lz].name, winnerName: m.teams[w].name, win: 1, rounds: r.rounds, us: r[w], them: r[lz], endReason: m.endReason });
  }
}
const outFile = opt('out', null);
if (outFile) fs.writeFileSync(path.resolve(ROOT, outFile), JSON.stringify(rows));
// summary
const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN, fx = (x, d = 1) => Number.isFinite(x) ? x.toFixed(d) : '–';
const grp = s => s.startsWith('baseline') ? '기준' : s.startsWith('px-king') ? 'px-king' : s.startsWith('cand') ? 'avoid6' : '상위권 승자';
console.log('| 지도 | 묶음 | 판 | 자기 샘물 자연 진주 먹음 | 먹은 드래곤 수 | 가장 많이 먹은 드래곤 몫 | 시작 계통 몫 | 먹을 때 길이 ≤4 / 5–10 / 11+ | 상대가 가져감 | 시작 줄 1칸 안에 머리가 있던 라운드 비율 | 상대의 같은 값(상대 샘물을 우리가 가져감) |');
console.log('|---|---|---|---|---|---|---|---|---|---|---|');
for (const v of ['Autarky', 'PD6', 'PD10']) for (const gname of ['기준', 'px-king', '상위권 승자']) {
  const x = rows.filter(r => r.variant === v && grp(r.set) === gname); if (!x.length) continue;
  const nat = x.reduce((s, r) => s + r.us.nat, 0);
  console.log(`| ${v} | ${gname} | ${x.length} | ${fx(mean(x.map(r => r.us.nat)))} | ${fx(mean(x.map(r => r.us.eaters)))} | ${fx(100 * mean(x.filter(r => r.us.topShare !== null).map(r => r.us.topShare)), 0)}% | ${fx(100 * x.reduce((s, r) => s + r.us.lin, 0) / Math.max(1, nat), 0)}% | ` +
    `${fx(100 * x.reduce((s, r) => s + r.us.small, 0) / Math.max(1, nat), 0)}% / ${fx(100 * x.reduce((s, r) => s + r.us.mid, 0) / Math.max(1, nat), 0)}% / ${fx(100 * x.reduce((s, r) => s + r.us.big, 0) / Math.max(1, nat), 0)}% | ${fx(mean(x.map(r => r.us.stolen)))} | ${fx(100 * mean(x.map(r => r.us.keeperShare)), 0)}% | ${fx(mean(x.map(r => r.them.stolen)))} |`);
}
// top teams that run a corridor loop (the start lineage eats >= 100 natural pearls on its own fountains), per map variant
if (argv.includes('--top')) {
  const top = rows.filter(r => r.set === 'top');
  console.log('\n| 지도 | 상위권끼리 판 | 승자가 고리 | 패자가 고리 | 고리를 쓴 팀: 판(승) |\n|---|---|---|---|---|');
  for (const v of ['Autarky', 'PD6', 'PD10']) {
    const x = top.filter(r => r.variant === v), T = new Map();
    for (const r of x) for (const [name, side, win] of [[r.winnerName, r.us, 1], [r.opp, r.them, 0]]) if (side.lin >= 100) { const t = T.get(name) || { n: 0, w: 0 }; t.n++; t.w += win; T.set(name, t); }
    const all = new Map(); for (const r of x) for (const [name, win] of [[r.winnerName, 1], [r.opp, 0]]) { const t = all.get(name) || { n: 0, w: 0 }; t.n++; t.w += win; all.set(name, t); }
    console.log(`| ${v} | ${x.length} | ${x.filter(r => r.us.lin >= 100).length} | ${x.filter(r => r.them.lin >= 100).length} | ${[...T].sort((a, b) => b[1].n - a[1].n).map(([k, t]) => `${k} ${t.n}(${t.w}) / 전체 ${all.get(k).n}(${all.get(k).w})`).join('; ') || '없음'} |`);
  }
  // the best non-loop winners on Autarky
  const x = top.filter(r => r.variant === 'Autarky'), all = new Map();
  for (const r of x) for (const [name, side, win] of [[r.winnerName, r.us, 1], [r.opp, r.them, 0]]) { const t = all.get(name) || { n: 0, w: 0, loop: 0, nat: 0 }; t.n++; t.w += win; if (side.lin >= 100) t.loop++; t.nat += side.nat; all.set(name, t); }
  console.log('\nAutarky, 고리 없이 5판 이상 둔 팀(판, 승, 자기 샘물 자연 진주/판): ' + [...all].filter(([, t]) => t.loop === 0 && t.n >= 5).sort((a, b) => b[1].w / b[1].n - a[1].w / a[1].n).map(([k, t]) => `${k} ${t.n}판 ${t.w}승 ${fx(t.nat / t.n)}`).join('; '));
}

// natural spawns per tile in the baseline Prisoners Dilemma games, by variant, with the 6-dragon map file's spawn gap:
// shows that the server's 10-dragon variant spawns on tiles whose gap in the 6-dragon file is long (its gaps differ).
{
  const gaps = new Map(fs.readFileSync(path.join(ROOT, 'maps/online-20260927/prisoners_dilemma.map'), 'utf8').split('\n').filter(l => l.startsWith('TILE ')).map(l => { const [x, y, a, b] = l.trim().split(/\s+/).slice(1).map(Number); return [x + ',' + y, a + '–' + b]; }));
  for (const v of ['PD6', 'PD10']) {
    const x = rows.filter(r => r.variant === v && r.set.startsWith('baseline')); if (!x.length) continue;
    const c = new Map(); for (const r of x) for (const [k, n] of Object.entries(r.spawns)) c.set(k, (c.get(k) || 0) + n);
    const tot = [...c.values()].reduce((s2, n) => s2 + n, 0);
    console.log(`\n기준 ${v} ${x.length}판: 자연 생성 판당 ${fx(tot / x.length)}. 많이 생긴 칸(판당, 6마리 판 지도의 간격): ` + [...c].sort((p, q) => q[1] - p[1]).slice(0, 12).map(([k, n]) => `${k} ${fx(n / x.length)} (${gaps.get(k)})`).join(', '));
  }
}
