#!/usr/bin/env node
// Paired comparison of two online test sets of ours (e.g. baseline vs candidate) by (opponent team, map).
// usage: node tools/online_compare.js <setA> <setB> [--json out.json]
//   <set> is a folder under data/online/ (or a path) written by `tools/online.js download`: index.json + game-<id>.json.
//   Join folders with '+' to pool replicates of the same bot, e.g. baseline-r1+baseline-r1b.
// Per game: win, survived (we have a dragon at the end), G = our longest living dragon at the end (0 if eliminated),
// their longest, our total length. Games of the same (team, map) in one set are averaged, then B − A is taken per
// key and summarised with a bootstrap 95% interval over keys (10,000 resamples, fixed seed). Seeds differ between
// sets, so this is noisier than a local paired test. Prisoners Dilemma is keyed by its version (6 or 10 start dragons),
// read from the replay, because the two versions play very differently.
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const ELIM = new Set(['Devil', 'Trophy', 'Prisoners Dilemma', 'Prisoners Dilemma (6)', 'Prisoners Dilemma (10)', 'Queen Of Spades', 'Default']);
const { load: load_replay } = require('./replay.js');
const [a, b] = process.argv.slice(2).filter(s => !s.startsWith('--'));
const ji = process.argv.indexOf('--json'), jsonOut = ji > 0 ? process.argv[ji + 1] : null;
if (!a || !b) { console.error('usage: online_compare.js <setA> <setB> [--json out.json]'); process.exit(2); }
const dirOf = s => fs.existsSync(s) ? path.resolve(s) : path.join(ROOT, 'data', 'online', s);

function load(set) {
  const by = new Map(), subs = new Set();
  for (const part of set.split('+')) {
  const dir = dirOf(part), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  for (const g of idx.games || idx) {
    if (g.ourWin === null || g.ourWin === undefined) continue;
    const gj = JSON.parse(fs.readFileSync(path.join(dir, `game-${g.gameId}.json`), 'utf8'));
    const res = gj.replay && gj.replay.result; if (!res) continue;
    const us = res['team' + g.ourSide], them = res['team' + (g.ourSide === 'A' ? 'B' : 'A')];
    const row = { win: g.ourWin ? 1 : 0, survived: us.dragonCount > 0 ? 1 : 0, G: us.dragonCount > 0 ? us.longestDragon : 0, theirLongest: them.longestDragon, total: us.totalLength, elim: res.endReason === 'teamEliminated' ? 1 : 0 };
    // Prisoners Dilemma comes in a 6- and a 10-dragon version on the server; pair them separately.
    let mapKey = g.mapName;
    if (g.mapName === 'Prisoners Dilemma') {
      try { const n = load_replay(path.join(dir, `M${g.gameId}.replay`)).match.map.initialDragons.length; mapKey = `Prisoners Dilemma (${n})`; } catch (e) {}
    }
    const k = `${g.opponentTeam}|${mapKey}`; if (!by.has(k)) by.set(k, []); by.get(k).push(row); subs.add(g.ourSubmission);
  }
  }
  const avg = new Map(); for (const [k, rows] of by) { const m = {}; for (const f of Object.keys(rows[0])) m[f] = rows.reduce((s, r) => s + r[f], 0) / rows.length; m.n = rows.length; avg.set(k, m); }
  return { avg, games: [...by.values()].reduce((s, r) => s + r.length, 0), subs: [...subs] };
}

// Deterministic bootstrap (mulberry32).
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function summary(d) {
  if (!d.length) return null;
  const mean = d.reduce((s, x) => s + x, 0) / d.length, r = rng(12345), bs = [];
  for (let i = 0; i < 10000; i++) { let s = 0; for (let j = 0; j < d.length; j++) s += d[Math.floor(r() * d.length)]; bs.push(s / d.length); }
  bs.sort((x, y) => x - y);
  return { n: d.length, mean: +mean.toFixed(3), lo: +bs[249].toFixed(3), hi: +bs[9749].toFixed(3) };
}

const A = load(a), B = load(b);
const keys = [...A.avg.keys()].filter(k => B.avg.has(k));
const groups = { '전체': keys, '전멸형 지도': keys.filter(k => ELIM.has(k.split('|')[1])), '500라운드형 지도': keys.filter(k => !ELIM.has(k.split('|')[1])) };
const out = { a, b, gamesA: A.games, gamesB: B.games, subsA: A.subs, subsB: B.subs, pairs: keys.length, groups: {} };
console.log(`A=${a} (${A.games}판, 제출 ${A.subs.join(',')})  B=${b} (${B.games}판, 제출 ${B.subs.join(',')})  짝 ${keys.length}개(팀×지도)`);
console.log('| 묶음 | 짝 | 지표 | A 평균 | B 평균 | B−A [95% 구간] |\n|---|---:|---|---:|---:|---|');
for (const [g, ks] of Object.entries(groups)) {
  out.groups[g] = {};
  for (const f of ['win', 'survived', 'G', 'theirLongest', 'total']) {
    const s = summary(ks.map(k => B.avg.get(k)[f] - A.avg.get(k)[f])); if (!s) continue;
    const ma = ks.reduce((t, k) => t + A.avg.get(k)[f], 0) / ks.length, mb = ks.reduce((t, k) => t + B.avg.get(k)[f], 0) / ks.length;
    out.groups[g][f] = { ...s, meanA: +ma.toFixed(3), meanB: +mb.toFixed(3) };
    console.log(`| ${g} | ${s.n} | ${f} | ${ma.toFixed(2)} | ${mb.toFixed(2)} | ${s.mean >= 0 ? '+' : ''}${s.mean.toFixed(2)} [${s.lo.toFixed(2)}, ${s.hi.toFixed(2)}] |`);
  }
}
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(out, null, 2));
