#!/usr/bin/env node
// W15a-t grounding (lead, after the W15a diagnosis): on maps whose start dragon begins inside a dead branch (Autarky, Prisoners Dilemma: its
// head in a walled pocket, facing in), what does each team do with that dragon? Per start-pocket lineage (a start dragon whose r0 head is off
// the 2-core of the true graph, plus every child split off it or its descendants):
//   splits r0-30   round, parent length before the split, child size, and whether the child's birth tile (the old tail) is on the 2-core
//   out            the first round a lineage head stands on the 2-core (it left the pockets), or never
//   stubs          lineage deaths on branch tiles (pocket termini), r0-100 and all game
//   vault          share of rounds 0-300 in which some lineage dragon has its head in a pocket (the loop is running)
//   longest        the longest lineage dragon at r50 / 100 / 200 / 300 / end, and whether the team's longest at the end is of the lineage
// Cohorts: top-game winners and losers (data/top/index.jsonl), ours online (data/online/*/game-*.json), ours local (runq sets, --sets).
// usage: node exp/w15a/pocketstart.js --map Autarky|Prisoners [--src top,online] [--limit N] [--sets exp/w15a/base] [--json out.json]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const opt = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? process.argv[i + 1] : d; };
const MAPRE = new RegExp(opt('--map', 'Autarky').replace(/[ _]/g, '[ _]?'), 'i');
const srcs = new Set(opt('--src', 'top,online').split(',')), limit = +opt('--limit', 1e9);
const DIRS = ['N', 'E', 'S', 'W'];
const load = makeLoader(viewerSource());
const stats = new Map();
const S = l => { if (!stats.has(l)) stats.set(l, { games: 0, lineages: 0, outBy: { r10: 0, r30: 0, r100: 0, ever: 0 }, outRounds: [], stubs100: 0, stubsAll: 0, vault: 0, vaultN: 0, longest: { 50: [], 100: [], 200: [], 300: [], end: [] }, kingOfLineage: 0, splits: [], firstSplit: [], childCore30: 0, child30: 0 }); return stats.get(l); };
function measure(file, teams) {
  const R = load(file);
  let G = null;
  const geo = ctx => {
    if (G) return G;
    const { W, H, across } = ctx, N = W * H, nb = new Array(N);
    for (let k = 0; k < N; k++) { const x = k % W, y = (k / W) | 0; nb[k] = DIRS.map(d => { const u = across(x, y, d); return u ? u.y * W + u.x : -1; }); }
    const deg = new Int32Array(N), gone = new Uint8Array(N), q = [];
    for (let k = 0; k < N; k++) { for (const u of nb[k]) if (u >= 0) deg[k]++; if (deg[k] <= 1) { gone[k] = 1; q.push(k); } }
    for (let i = 0; i < q.length; i++) for (const u of nb[q[i]]) { if (u < 0 || gone[u]) continue; if (--deg[u] <= 1) { gone[u] = 1; q.push(u); } }
    G = { W, H, gone }; return G;
  };
  const lin = new Map(), L = new Map();   // dragon id -> lineage root; root -> record
  let started = false, curRound = -1;
  const startLineages = ctx => {
    const g = geo(ctx);
    for (const d0 of R.match.map.initialDragons) {
      if (!teams[d0.team]) continue;
      const h = d0.body[0];
      if (!g.gone[h.y * g.W + h.x]) continue;
      lin.set(d0.id, d0.id);
      L.set(d0.id, { team: d0.team, out: null, splits: [], stubs100: 0, stubsAll: 0, vault: 0, longest: {}, alive: new Set([d0.id]) });
    }
    started = true;
  };
  const roundTick = (round, ctx) => {
    const g = geo(ctx);
    for (const [root, rec] of L) {
      let inPocket = false, lo = 0;
      for (const id of rec.alive) { const d = ctx.drag.get(id); if (!d) continue; lo = Math.max(lo, d.body.length); const h = d.body[0]; if (g.gone[h.y * g.W + h.x]) inPocket = true; }
      if (round <= 300) rec.vault += inPocket ? 1 : 0;
      for (const cp of [50, 100, 200, 300]) if (round === cp) rec.longest[cp] = lo;
    }
  };
  perGame(R, { map: '?', variant: 'a' }, {
    turn(d, round, ctx) {
      if (!started) startLineages(ctx);
      if (round !== curRound) { curRound = round; roundTick(round, ctx); }
    },
    split(p, ch, e, round, ctx) {
      if (!started) startLineages(ctx);
      const root = lin.get(p.id); if (root == null) return;
      const g = geo(ctx), rec = L.get(root), h = ch.body[0], core = !g.gone[h.y * g.W + h.x];
      lin.set(ch.id, root); rec.alive.add(ch.id);
      if (round <= 30) rec.splits.push({ round, parentLen: p.body.length + ch.body.length, size: ch.body.length, core });
      if (core && rec.out == null) rec.out = round;
    },
    action(d, e, round, ctx) {
      const root = lin.get(d.id); if (root == null) return;
      const rec = L.get(root); if (rec.out != null) return;
      const g = geo(ctx), h = d.body[0];
      if (!g.gone[h.y * g.W + h.x]) rec.out = round;
    },
    death(d, rec0, idx, other, round, ctx) {
      const root = lin.get(d.id); if (root == null) return;
      const g = geo(ctx), rec = L.get(root), h = d.body[0];
      rec.alive.delete(d.id);
      if (g.gone[h.y * g.W + h.x]) { rec.stubsAll++; if (round <= 100) rec.stubs100++; }
    },
    end(rounds, ctx) {
      for (const [root, rec] of L) {
        let lo = 0, king = null;
        for (const id of rec.alive) { const d = ctx.drag.get(id); if (d) lo = Math.max(lo, d.body.length); }
        rec.longest.end = lo;
        for (const d of ctx.drag.values()) if (d.team === rec.team && (!king || d.body.length > king.body.length)) king = d;
        rec.king = !!(king && lin.get(king.id) === root);
      }
    },
  });
  for (const [root, rec] of L) for (const l of teams[rec.team]) {
    const T = S(l); T.lineages++;
    if (rec.out != null) { T.outBy.ever++; if (rec.out <= 10) T.outBy.r10++; if (rec.out <= 30) T.outBy.r30++; if (rec.out <= 100) T.outBy.r100++; T.outRounds.push(rec.out); }
    T.stubs100 += rec.stubs100; T.stubsAll += rec.stubsAll; T.vault += rec.vault; T.vaultN += 301;
    for (const k of [50, 100, 200, 300, 'end']) T.longest[k].push(rec.longest[k] || 0);
    if (rec.king) T.kingOfLineage++;
    for (const s of rec.splits) { T.splits.push(s); T.child30++; if (s.core) T.childCore30++; }
    if (rec.splits.length) T.firstSplit.push(rec.splits[0]);
  }
}
const files = [];
if (srcs.has('top')) {
  const rows = fs.readFileSync(path.join(ROOT, 'data', 'top', 'index.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => MAPRE.test(r.map));
  for (const r of rows.slice(0, limit)) {
    const f = path.join(ROOT, 'data', 'top', String(r.battleId), r.gameId + '.replay.gz'); if (!fs.existsSync(f)) continue;
    const w = (r.winner || '').toUpperCase(); if (w !== 'A' && w !== 'B') continue;
    files.push({ f, teams: { [w]: ['top winner'], [w === 'A' ? 'B' : 'A']: ['top loser'] } });
  }
}
if (srcs.has('online')) {
  for (const set of fs.readdirSync(path.join(ROOT, 'data', 'online'))) {
    const dir = path.join(ROOT, 'data', 'online', set); if (!fs.statSync(dir).isDirectory()) continue;
    for (const g of fs.readdirSync(dir).filter(f => /^game-\d+\.json$/.test(f))) {
      let m; try { m = JSON.parse(fs.readFileSync(path.join(dir, g), 'utf8')); } catch { continue; }
      if (!MAPRE.test(m.map || m.mapName || '')) continue;
      const id = m.gameId || m.id, side = m.ourSide || (m.teamAId === 583 ? 'A' : m.teamBId === 583 ? 'B' : null);   // team 583 = us
      const f = path.join(dir, `M${id}.replay`); if (!side || !fs.existsSync(f)) continue;
      const won = String(m.winner || '').toUpperCase() === side;
      files.push({ f, teams: { [side]: ['ours online', won ? 'ours online won' : 'ours online lost'] } });
    }
  }
}
for (const set of (opt('--sets', '') || '').split(',').filter(Boolean)) {
  for (const l of fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').trim().split('\n').map(JSON.parse)) {
    if (!MAPRE.test(l.map) && !(MAPRE.test('Prisoners Dilemma') && l.map === 'dilemma')) continue;
    files.push({ f: path.join(ROOT, set, 'games', l.key.replace(/:/g, '_'), 'game.replay'), teams: { [l.side]: [`local ${path.basename(set)}`] } });
  }
}
let n = 0;
const from = +opt('--from', 0), to = +opt('--to', 1e9);
if (opt('--merge')) {
  files.length = 0;
  for (const fj of opt('--merge').split(',')) for (const [l, T] of Object.entries(JSON.parse(fs.readFileSync(fj, 'utf8')))) {
    const A = S(l);
    for (const k of ['games', 'lineages', 'stubs100', 'stubsAll', 'vault', 'vaultN', 'kingOfLineage', 'childCore30', 'child30']) A[k] += T[k];
    for (const k of Object.keys(A.outBy)) A.outBy[k] += T.outBy[k];
    A.outRounds.push(...T.outRounds); A.firstSplit.push(...T.firstSplit); for (const k of Object.keys(A.longest)) A.longest[k].push(...T.longest[k]);
  }
}
for (const { f, teams } of files.slice(from, to)) {
  for (const ls of Object.values(teams)) for (const l of ls) S(l).games++;
  try { measure(f, teams); } catch (e) { console.error('skip', f, String(e).slice(0, 120)); }
  if (++n % 100 === 0) console.error('progress', n, '/', files.length);
}
const pc = (a, b) => b ? (100 * a / b).toFixed(1) + '%' : '-';
const med = a => { const s = a.slice().sort((x, y) => x - y); return s.length ? s[s.length >> 1] : '-'; };
const out = {};
for (const [l, T] of [...stats].sort()) {
  const sizes = {}; for (const s of T.firstSplit) { const k = `${s.size}/${s.parentLen}@r${s.round <= 5 ? '0-5' : s.round <= 15 ? '6-15' : '16-30'}${s.core ? ' core' : ''}`; sizes[k] = (sizes[k] || 0) + 1; }
  const top = Object.entries(sizes).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([k, v]) => `${k} ${v}`).join(', ');
  console.log(`${l.padEnd(18)} games ${T.games}, pocket lineages ${T.lineages}: out by r10 ${pc(T.outBy.r10, T.lineages)}, r30 ${pc(T.outBy.r30, T.lineages)}, r100 ${pc(T.outBy.r100, T.lineages)}, ever ${pc(T.outBy.ever, T.lineages)} (median round ${med(T.outRounds)})`);
  console.log(`${''.padEnd(18)} stubs per lineage r0-100 ${(T.stubs100 / Math.max(1, T.lineages)).toFixed(1)}, all game ${(T.stubsAll / Math.max(1, T.lineages)).toFixed(1)}; vault (head in a pocket) ${pc(T.vault, T.vaultN)} of rounds 0-300`);
  console.log(`${''.padEnd(18)} longest of the lineage, median r50/100/200/300/end: ${[50, 100, 200, 300, 'end'].map(k => med(T.longest[k])).join(' / ')}; the team's longest at the end is of the lineage ${pc(T.kingOfLineage, T.lineages)}`);
  console.log(`${''.padEnd(18)} splits r0-30: ${T.child30} (child born on the 2-core ${pc(T.childCore30, T.child30)}); first split (child/parent @round): ${top}`);
  out[l] = { games: T.games, lineages: T.lineages, outBy: T.outBy, outMedian: med(T.outRounds), stubs100: T.stubs100, stubsAll: T.stubsAll, vaultShare: T.vault / Math.max(1, T.vaultN), longestMedian: Object.fromEntries([50, 100, 200, 300, 'end'].map(k => [k, med(T.longest[k])])), kingOfLineage: T.kingOfLineage, splits30: T.child30, childCore30: T.childCore30, firstSplit: sizes };
}
if (opt('--json')) fs.writeFileSync(opt('--json'), JSON.stringify(out, null, 1));
if (opt('--raw')) fs.writeFileSync(opt('--raw'), JSON.stringify(Object.fromEntries([...stats].map(([l, T]) => [l, { ...T, splits: undefined }]))));
