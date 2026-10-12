#!/usr/bin/env node
'use strict';
// child_ab.js — what happens to the 2-segment children of early splits (rounds <= 166) on Schooltime a and b
// (research/experiments/cand-mapid.md, bsplit baselines). Decision rows of data/decisions (every split row is kept, w = 1):
// cAl10 = the child is alive 10 rounds later, cL10 = its length then (>= 3: it ate at least one pearl).
// usage (repository root): node exp/mapid/child_ab.js [--map Schooltime] [--rmax 166]
const fs = require('fs'), path = require('path'), zlib = require('zlib');
const ROOT = path.resolve(__dirname, '..', '..'), DEC = path.join(ROOT, 'data', 'decisions');
const argv = process.argv.slice(2), opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const mapName = opt('map', 'Schooltime'), rmax = +opt('rmax', 166);
const NOT_ELITE = new Set(['r1-autoscrim', 'r1-online', 'g1', 'g2', 'top-20260929a']);
const lay = new Map();
for (const l of fs.readFileSync(path.join(__dirname, 'cache', 'feat.jsonl'), 'utf8').split('\n')) { if (!l.trim()) continue; const g = JSON.parse(l); if (g.map === mapName) lay.set(+g.gameId, g.layout); }
const acc = {}; let games = 0;
for (const s of fs.readdirSync(DEC).filter(x => fs.existsSync(path.join(DEC, x, 'games.jsonl')) && !NOT_ELITE.has(x))) {
  for (const g of fs.readFileSync(path.join(DEC, s, 'games.jsonl'), 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l))) {
    if (g.map !== mapName) continue;
    const L0 = lay.get(+String(g.key).split(':').pop()); if (!(L0 === 'a' || L0 === 'b')) continue;
    const f = path.join(DEC, s, g.out); if (!fs.existsSync(f)) continue;
    const lines = zlib.gunzipSync(fs.readFileSync(f)).toString().split('\n'), C = Object.fromEntries(lines[0].split('\t').map((k, i) => [k, i]));
    games++;
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i]) continue; const row = lines[i].split('\t');
      if (row[C.act] !== 'P' || +row[C.c] !== 2 || +row[C.r] > rmax) continue;
      const tm = row[C.tm];
      const grp = s.startsWith('top') ? (g.winner === tm ? 'top winner' : g.winner ? 'top loser' : 'top tie') : g.ourSide === tm ? (/swarm8|px-king|base-px/.test(s) ? 'ours swarm/px' : 'ours merge2-line') : 'elite vs us';
      const k = L0 + '|' + grp, a = acc[k] || (acc[k] = { n: 0, al10: 0, grew10: 0, len10: 0, parentAl10: 0 });
      a.n++; a.al10 += +row[C.cAl10] > 0 ? 1 : 0; a.grew10 += +row[C.cL10] >= 3 ? 1 : 0; a.len10 += Math.max(0, +row[C.cL10]); a.parentAl10 += +row[C.al10] > 0 ? 1 : 0;
    }
  }
}
console.log(`# ${mapName}: 2-segment children of splits in rounds <= ${rmax} (games ${games})\n`);
console.log('| 판본 | 집단 | 분열 | 새끼 10라운드 생존 | 새끼가 10라운드 안 1개 이상 먹음(길이 ≥3) | 새끼 평균 길이 +10 | 부모 10라운드 생존 |');
console.log('|---|---|---:|---:|---:|---:|---:|');
for (const k of Object.keys(acc).sort()) { const a = acc[k], [L0, grp] = k.split('|'); console.log(`| ${L0} | ${grp} | ${a.n} | ${Math.round(100 * a.al10 / a.n)}% | ${Math.round(100 * a.grew10 / a.n)}% | ${(a.len10 / a.n).toFixed(2)} | ${Math.round(100 * a.parentAl10 / a.n)}% |`); }
