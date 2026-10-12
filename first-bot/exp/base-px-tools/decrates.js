#!/usr/bin/env node
'use strict';
// decrates.js — the key decision rules of research/observations/top-decisions.md measured on local eval games.
// usage: node exp/base-px-tools/decrates.js <label>[+<label>...] [<label2>...] [--maps m1,m2] [--opps a,b] [--jobs 3]
//   Each positional argument is one group (labels joined by + are pooled). For every game in exp/<label>/rows.jsonl it
//   runs extractGame() of tools/decisions.js (exported, unchanged) on exp/<label>/games/<key>/game.replay with our side
//   as ourSide, so every turn of our side is kept (weight 1), and applies the rule definitions of
//   tools/decisions_rules.js (copied below, same thresholds):
//     R3 free >= 1, nearest ally anywhere of length >= 8 within Manhattan 3, r >= 350: self-kill (S, W, Aq, Ax)
//     R3e as R3 but r 250-349 (the top rule's early rate, d1 tree)
//     R4 L <= 3, can ram an enemy head this turn, ally head in view, that enemy >= our length, <= 2 enemy heads in view,
//        action move or split: rammed head-on
//     b1-1 L <= 4, can ram, no ally head in view, free >= 1, the longest rammable enemy shorter than us: rammed
//     b1-7 L <= 4, can ram, exactly one ally head in view, that enemy shorter, >= 2 enemy heads in view: rammed
//     R8 L >= 6, a shorter enemy head in view, moved and survived, every single step exposed, a sprint escape exists:
//        sprinted (>= 2 steps)
//   and, for self-kills with a free neighbour in rounds 350-449 (sacrifices): the nearest ally's length (aLg) and the
//   pearls our longest dragon ate of the drop within 20 rounds (feedK), per sacrifice.
//   Rates are weighted turn rates with a game-clustered bootstrap 95% interval (1000 resamples, seed 7).
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { extractGame, C } = require(path.join(ROOT, 'tools', 'decisions.js'));
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const groupsArg = []; for (let i = 0; i < argv.length; i++) { if (argv[i].startsWith('--')) { i++; continue; } groupsArg.push(argv[i]); }
const mapsF = opt('maps', null) ? opt('maps').split(',') : null, oppsF = opt('opps', null) ? opt('opps').split(',') : null;

const n = (v, k) => +v[C[k]];
const SK = new Set(['S', 'W', 'Aq', 'Ax']);
const RULES = [
  { id: 'R3', pop: v => n(v, 'free') >= 1 && n(v, 'aLg') >= 8 && n(v, 'aDg') <= 3 && n(v, 'r') >= 350, act: v => SK.has(v[C.fate]) },
  { id: 'R3e', pop: v => n(v, 'free') >= 1 && n(v, 'aLg') >= 8 && n(v, 'aDg') <= 3 && n(v, 'r') >= 250 && n(v, 'r') < 350, act: v => SK.has(v[C.fate]) },
  { id: 'R4', pop: v => n(v, 'L') <= 3 && n(v, 'oppN') >= 1 && n(v, 'aN') >= 1 && n(v, 'oppL') >= n(v, 'L') && n(v, 'eN') <= 2 && (v[C.act] === 'M' || v[C.act] === 'P'), act: v => v[C.ram] === '1' },
  { id: 'b1-1', pop: v => n(v, 'L') <= 4 && n(v, 'oppN') >= 1 && n(v, 'aN') <= 0 && n(v, 'free') >= 1 && n(v, 'oppL') - n(v, 'L') <= -1, act: v => v[C.ram] === '1' },
  { id: 'b1-7', pop: v => n(v, 'L') <= 4 && n(v, 'oppN') >= 1 && n(v, 'aN') === 1 && n(v, 'oppL') - n(v, 'L') <= -1 && n(v, 'eN') >= 2, act: v => v[C.ram] === '1' },
  { id: 'R8', pop: v => n(v, 'L') >= 6 && n(v, 'eNs') >= 1 && v[C.act] === 'M' && v[C.fate] === '' && n(v, 'safe1') === 0 && n(v, 'exp1') > 0 && n(v, 'safe2') > 0, act: v => n(v, 'k') >= 2 },
];

function gameRates(file, side, key) {
  const R = load(file);
  const { rows } = extractGame(R, { key, seedHash: 1, ourSide: side });
  const per = {}; const sac = { n: 0, aLg: 0, feedK: 0, feedS: 0 };
  for (const raw of rows) {
    const v = raw.map(String);
    if (v[C.tm] !== side) continue;
    const w = +v[C.w];
    for (const Rr of RULES) if (Rr.pop(v)) { const e = per[Rr.id] || (per[Rr.id] = [0, 0]); e[0] += w; if (Rr.act(v)) e[1] += w; }
    const r = n(v, 'r');
    if (SK.has(v[C.fate]) && n(v, 'free') >= 1 && r >= 350 && r < 450) { sac.n += w; sac.aLg += w * n(v, 'aLg'); sac.feedK += w * Math.max(0, n(v, 'feedK')); sac.feedS += w * Math.max(0, n(v, 'feedS')); }
  }
  return { per, sac };
}

let seed = 7; const rnd = () => { seed = (Math.imul(seed, 1103515245) + 12345) >>> 0; return seed / 4294967296; };
function boot(list, rid, B = 1000) {
  const xs = list.map(x => x.per[rid] || [0, 0]);
  const tw = xs.reduce((s, x) => s + x[0], 0), ta = xs.reduce((s, x) => s + x[1], 0);
  if (!tw) return { p: NaN, lo: NaN, hi: NaN, w: 0 };
  const ps = [];
  for (let b = 0; b < B; b++) { let w = 0, a = 0; for (let i = 0; i < xs.length; i++) { const x = xs[Math.floor(rnd() * xs.length)]; w += x[0]; a += x[1]; } if (w) ps.push(a / w); }
  ps.sort((p, q) => p - q);
  return { p: ta / tw, lo: ps[Math.floor(0.025 * ps.length)], hi: ps[Math.floor(0.975 * ps.length)], w: tw };
}

const f = x => Number.isFinite(x) ? (100 * x).toFixed(1) : '–';
const out = [];
for (const g of groupsArg) {
  const list = [];
  for (const lab of g.split('+')) {
    const dir = path.join(ROOT, 'exp', lab); const seen = new Set();
    for (const l of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').split('\n')) {
      if (!l.trim()) continue; const r = JSON.parse(l);
      if (r.G === undefined || seen.has(r.key)) continue; seen.add(r.key);
      if ((mapsF && !mapsF.includes(r.map)) || (oppsF && !oppsF.includes(r.opp))) continue;
      const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
      list.push(gameRates(file, r.side, r.key));
    }
  }
  const row = { group: g, games: list.length };
  for (const Rr of RULES) row[Rr.id] = boot(list, Rr.id);
  const S = list.reduce((s, x) => ({ n: s.n + x.sac.n, aLg: s.aLg + x.sac.aLg, feedK: s.feedK + x.sac.feedK, feedS: s.feedS + x.sac.feedS }), { n: 0, aLg: 0, feedK: 0, feedS: 0 });
  row.sac = { perGame: S.n / Math.max(1, list.length), aLg: S.n ? S.aLg / S.n : NaN, feedK: S.n ? S.feedK / S.n : NaN, feedS: S.n ? S.feedS / S.n : NaN };
  out.push(row);
}
console.log('| group | games | R3 (r>=350) | R3 r250-349 | R4 | rams shorter alone (b1-1) | rams shorter, 1 ally, >=2 enemies (b1-7) | R8 | sacrifices r350-449 / game | ally length at sacrifice | king ate / sacrifice | team ate / sacrifice |');
console.log('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
for (const r of out) {
  const c = id => `${f(r[id].p)}% [${f(r[id].lo)}–${f(r[id].hi)}] (w ${r[id].w})`;
  console.log(`| ${r.group} | ${r.games} | ${c('R3')} | ${c('R3e')} | ${c('R4')} | ${c('b1-1')} | ${c('b1-7')} | ${c('R8')} | ${r.sac.perGame.toFixed(1)} | ${Number.isFinite(r.sac.aLg) ? r.sac.aLg.toFixed(2) : '–'} | ${Number.isFinite(r.sac.feedK) ? r.sac.feedK.toFixed(2) : '–'} | ${Number.isFinite(r.sac.feedS) ? r.sac.feedS.toFixed(2) : '–'} |`);
}
if (opt('json', null)) fs.writeFileSync(opt('json'), JSON.stringify(out, null, 1));
