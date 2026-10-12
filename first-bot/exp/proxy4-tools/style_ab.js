#!/usr/bin/env node
'use strict';
// style_ab.js — style metrics of the five two-layout maps, layout a against layout b (Prisoners Dilemma: 6 against 10
// dragons), for the top teams and for local proxy games. Checks that the proxies react to layout b the way the top teams
// do (research/experiments/proxies-v3.md, v4 section).
//
// usage (repository root):
//   node exp/proxy4-tools/style_ab.js --g "<name>=<label>[+<label>][:<bot>]" [--g ...] [--json <file>]
//     Top: exp/proxy-check/top-sides.jsonl (top-vs-top snapshot, both sides) with each game's layout from
//     data/pearl_layout/variants.json (cats[*].assign). Local: exp/<label>/sides.jsonl (tools/proxy_check.js measure);
//     :<bot> keeps only the sides of that bot. Layout of a local side: b for map files *_b and prisoners_dilemma_10.
// Per side: pearls eaten in rounds 0-99, units and total length at r100 (sides whose game reached r100), total length at
// r300, longest at r500 (games that reached 500). Values are medians over sides; elim = share of games ending by
// elimination.
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const argv = process.argv.slice(2);
const groups = []; let jsonOut = null;
for (let i = 0; i < argv.length; i++) { if (argv[i] === '--g') groups.push(argv[++i]); else if (argv[i] === '--json') jsonOut = argv[++i]; }
const MAPS = ['devil', 'queen_of_spades', 'schooltime', 'slithery_fight', 'prisoners_dilemma'];
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(Boolean).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];
const med = a => { if (!a.length) return null; const s = a.slice().sort((x, y) => x - y), m = (s.length - 1) / 2; return (s[Math.floor(m)] + s[Math.ceil(m)]) / 2; };

function topSides() {
  const v = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'pearl_layout', 'variants.json'), 'utf8'));
  const asg = new Map(); for (const c of Object.values(v.cats)) for (const [g, t] of Object.entries(c.assign || {})) asg.set(g, t === 'a' ? 'a' : 'b');
  const out = [];
  for (const s of readJsonl(path.join(ROOT, 'exp', 'proxy-check', 'top-sides.jsonl'))) {
    if (!MAPS.includes(s.map)) continue;
    const lay = asg.get('g' + s.key.split(':')[1]); if (!lay) continue;
    out.push({ ...s, bmap: s.map, layout: lay });
  }
  return out;
}
function localSides(spec) {
  const [labels, bot] = spec.split(':'); const out = [];
  for (const L of labels.split('+')) for (const s of readJsonl(path.join(ROOT, 'exp', L, 'sides.jsonl'))) {
    if (bot && s.name !== bot) continue;
    const bmap = s.map.replace(/_b$|_10$/, ''); if (!MAPS.includes(bmap)) continue;
    out.push({ ...s, bmap, layout: /_b$|_10$/.test(s.map) ? 'b' : 'a' });
  }
  return out;
}
function stats(S) {
  const games = new Map(); for (const x of S) games.set(x.key, x);
  const at = (r, i, need) => med(S.filter(x => need(x)).map(x => x.tl[r / 10] ? x.tl[r / 10][i] : null).filter(v => v !== null));
  return {
    sides: S.length, games: games.size,
    elim: games.size ? [...games.values()].filter(x => x.elim).length / games.size : null,
    rounds: med([...games.values()].map(x => x.rounds)),
    eat100: med(S.map(x => x.eaten100)),
    units100: at(100, 0, x => x.rounds > 100), total100: at(100, 1, x => x.rounds > 100),
    total300: at(300, 1, x => x.rounds > 300), longest500: at(500, 2, x => x.rounds === 500),
  };
}
const all = [['top (top vs top)', topSides()], ...groups.map(g => { const [name, spec] = g.split('='); return [name, localSides(spec)]; })];
const f = x => x === null || x === undefined ? '-' : Math.abs(x) >= 100 ? x.toFixed(0) : x.toFixed(1);
const ratio = (b, a) => a && b !== null ? (b / a).toFixed(2) : '-';
const rows = [];
console.log('| 지도 | 묶음 | 편 a / b | 전멸 a / b | 라운드 중앙 a / b | r0–99 먹이 a / b (b/a) | 수 r100 a / b | 몸 합 r100 a / b (b/a) | 몸 합 r300 a / b | 최장 r500 a / b |');
console.log('|---|---|---|---|---|---|---|---|---|---|');
for (const m of MAPS) for (const [name, S] of all) {
  const A = stats(S.filter(x => x.bmap === m && x.layout === 'a')), B = stats(S.filter(x => x.bmap === m && x.layout === 'b'));
  if (!A.sides && !B.sides) continue;
  rows.push({ map: m, group: name, a: A, b: B });
  const pc = x => x === null ? '-' : (100 * x).toFixed(0) + '%';
  console.log(`| ${m} | ${name} | ${A.sides} / ${B.sides} | ${pc(A.elim)} / ${pc(B.elim)} | ${f(A.rounds)} / ${f(B.rounds)} | ${f(A.eat100)} / ${f(B.eat100)} (${ratio(B.eat100, A.eat100)}) | ${f(A.units100)} / ${f(B.units100)} | ${f(A.total100)} / ${f(B.total100)} (${ratio(B.total100, A.total100)}) | ${f(A.total300)} / ${f(B.total300)} | ${f(A.longest500)} / ${f(B.longest500)} |`);
}
if (jsonOut) fs.writeFileSync(path.resolve(ROOT, jsonOut), JSON.stringify(rows, null, 1) + '\n');
