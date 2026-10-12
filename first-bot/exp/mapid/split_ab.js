#!/usr/bin/env node
'use strict';
// split_ab.js — the split economy by pearl layout (research/experiments/cand-mapid.md, part B): does a length-4 piece
// that splits (4 -> 2+2) do better than one that keeps moving, on layout a and on layout b? Decision rows of
// data/decisions (tools/decisions.js: one row per dragon turn, plain turns sampled 1 in 8 with weight w = 8; every split,
// enemy-in-view turn and every turn of our side kept with w = 1). The layout of each game comes from
// exp/mapid/cache/feat.jsonl (exp/mapid/extract.js; natural spawns).
// Outcome: net10 / net30 = family length (this dragon plus every descendant split off from this round on) 10 / 30 rounds
// later minus the length now; alive10 = the family has a living unit 10 rounds later (Fu10 > 0).
// usage (repository root): node exp/mapid/split_ab.js [--map Schooltime] [--sets top-all,<online sets>] [--L 4] [--rmax 100]
const fs = require('fs'), path = require('path'), zlib = require('zlib');
const ROOT = path.resolve(__dirname, '..', '..'), DEC = path.join(ROOT, 'data', 'decisions');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const mapName = opt('map', 'Schooltime'), Lsel = (opt('L', '4')).split(',').map(Number), rmax = +opt('rmax', 100), rmin = +opt('rmin', 0);
const NOT_ELITE = new Set(['r1-autoscrim', 'r1-online', 'g1', 'g2', 'top-20260929a']);
const sets = opt('sets', null) ? opt('sets').split(',') : fs.readdirSync(DEC).filter(s => fs.existsSync(path.join(DEC, s, 'games.jsonl')) && !NOT_ELITE.has(s));
// layouts by gameId
const lay = new Map();
for (const l of fs.readFileSync(path.join(__dirname, 'cache', 'feat.jsonl'), 'utf8').split('\n')) { if (!l.trim()) continue; const g = JSON.parse(l); if (g.map === mapName) lay.set(+g.gameId, g.layout); }
// accumulators: key -> { w, split, n, net10S, net10M, net30S, net30M, al10S, al10M, wS, wM }
const acc = new Map();
const put = (key, isSplit, row, w, C) => {
  let a = acc.get(key); if (!a) acc.set(key, a = { rows: 0, wS: 0, wM: 0, n10S: 0, n10M: 0, n30S: 0, n30M: 0, a10S: 0, a10M: 0, w30S: 0, w30M: 0, games: new Set() });
  const L = +row[C.L], F10 = +row[C.F10], F30 = C.F30 !== undefined ? +row[C.F30] : NaN, Fu10 = +row[C.Fu10];
  a.rows++;
  if (isSplit) { a.wS += w; a.n10S += w * (F10 - L); a.a10S += w * (Fu10 > 0 ? 1 : 0); if (!isNaN(F30) && F30 >= 0) { a.n30S += w * (F30 - L); a.w30S += w; } }
  else { a.wM += w; a.n10M += w * (F10 - L); a.a10M += w * (Fu10 > 0 ? 1 : 0); if (!isNaN(F30) && F30 >= 0) { a.n30M += w * (F30 - L); a.w30M += w; } }
};
let files = 0, rowsRead = 0;
for (const s of sets) {
  const games = fs.readFileSync(path.join(DEC, s, 'games.jsonl'), 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l));
  for (const g of games) {
    if (g.map !== mapName) continue;
    const gid = +String(g.key).split(':').pop(), L0 = lay.get(gid);
    if (!(L0 === 'a' || L0 === 'b')) continue;
    if (g.checks && Object.entries(g.checks).some(([k, v]) => k !== 'finalMatch' && v)) continue;
    const f = path.join(DEC, s, g.out); if (!fs.existsSync(f)) continue;
    const lines = zlib.gunzipSync(fs.readFileSync(f)).toString().split('\n');
    const C = Object.fromEntries(lines[0].split('\t').map((k, i) => [k, i]));
    files++;
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i]) continue;
      const row = lines[i].split('\t'); rowsRead++;
      const r = +row[C.r], L = +row[C.L];
      if (r < rmin || r >= rmax || !Lsel.includes(L)) continue;
      const act = row[C.act]; if (act !== 'M' && act !== 'P') continue;
      const tm = row[C.tm], w = +row[C.w] || 1;
      let grp;
      if (s.startsWith('top')) grp = g.winner === tm ? 'top winner' : g.winner ? 'top loser' : 'top tie';
      else grp = g.ourSide === tm ? 'ours (' + s + ')' : 'elite vs us';
      const isSplit = act === 'P' && +row[C.c] === L / 2 | 0 ? true : act === 'P';
      const eIn = +row[C.eN] > 0 ? 'enemy in view' : 'no enemy in view';
      put(`${L0}|${grp}|all`, isSplit, row, w, C);
      put(`${L0}|${grp}|${eIn}`, isSplit, row, w, C);
      if (!s.startsWith('top')) { const g2 = g.ourSide === tm ? 'ours (all sets)' : 'elite vs us'; if (g2 !== grp) { put(`${L0}|${g2}|all`, isSplit, row, w, C); put(`${L0}|${g2}|${eIn}`, isSplit, row, w, C); } }
    }
  }
}
const f2 = v => v === null || isNaN(v) ? '–' : (Math.round(v * 100) / 100).toFixed(2);
console.log(`# 분열 경제 by 판본: ${mapName}, 길이 ${Lsel.join(',')}, r${rmin}–${rmax - 1} (게임 ${files}, 읽은 행 ${rowsRead})\n`);
console.log('| 판본 | 집단 | 상황 | 행 | 분열률(가중) | net10 분열 / 이동 (차이) | net30 분열 / 이동 (차이) | 10라운드 뒤 가족 생존 분열 / 이동 |');
console.log('|---|---|---|---:|---:|---|---|---|');
const keys = [...acc.keys()].sort();
for (const k of keys) {
  const a = acc.get(k), [L0, grp, sit] = k.split('|');
  const rate = a.wS / Math.max(1e-9, a.wS + a.wM);
  const s10 = a.wS ? a.n10S / a.wS : NaN, m10 = a.wM ? a.n10M / a.wM : NaN, s30 = a.w30S ? a.n30S / a.w30S : NaN, m30 = a.w30M ? a.n30M / a.w30M : NaN;
  console.log(`| ${L0} | ${grp} | ${sit} | ${a.rows} | ${(100 * rate).toFixed(1)}% | ${f2(s10)} / ${f2(m10)} (${f2(s10 - m10)}) | ${f2(s30)} / ${f2(m30)} (${f2(s30 - m30)}) | ${a.wS ? Math.round(100 * a.a10S / a.wS) + '%' : '–'} / ${a.wM ? Math.round(100 * a.a10M / a.wM) + '%' : '–'} |`);
}
