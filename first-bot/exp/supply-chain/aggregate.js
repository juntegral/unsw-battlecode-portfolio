#!/usr/bin/env node
// Aggregate the supply-chain cache (exp/supply-chain/extract.js) into group totals: stage 1 (every game) and stage 2 (classes
// with their sizes). Replays are not read here.
// usage (repository root): node exp/supply-chain/aggregate.js [--top top-all] [--out .cache/supply-chain/agg.json]
// Groups (one per team-game):
//   TW / TL  top-vs-top winner / loser (games with an inactive team, splits <= 3 and no sonar, or >= 3 timeout deaths, and draws
//            are left out; the rule of exp/mass-analysis/report.js)
//   T7W      TW whose team is one of the 7 elite teams our online sets play
//   X        the elite opponent in our online games; X:<bot> the opponents of one bot
//   <bot>    our side of an online set (SETGROUP)
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), readline = require('readline');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'supply-chain');
const SETGROUP = {
  'baseline-r1': 'g4r4', 'baseline-r1b': 'g4r4', 'baseline-r1c': 'g4r4',
  'cand-merge2-online': 'merge2', 'cand-merge2-online-r2': 'merge2', 'cand-merge2-online-r3': 'merge2',
  'cand-stack1-online': 'stack1', 'cand-stack2-online': 'stack2', 'cand-stack3-online': 'stack3', 'cand-stack4-online': 'stack4',
  'cand-stack5-online': 'stack5', 'cand-stack6-online': 'stack6', 'cand-swarm8-online': 'swarm8', 'base-px9d-online': 'px9d',
  'base-px8-online': 'px8', 'px-king-v2-online': 'pxking', 'cand-avoid6-online': 'avoid6', 'cand-portal1-online': 'portal1',
};
const T7 = new Set(['Cutlery', 'cheji bt', 'calc', '中国必须人能飞😡', 'forgot to mention', 'Sabotage-d', 'dev test 1 :P']);
const R500 = new Set(['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma']);
const NB = 50;
const PHSTART = [0, 100, 250, 350, 450];
const phaseOf = r => r < 100 ? 0 : r < 250 ? 1 : r < 350 ? 2 : r < 450 ? 3 : 4;
const bDist = m => m <= 3 ? 0 : m <= 5 ? 1 : m <= 8 ? 2 : m <= 12 ? 3 : m <= 20 ? 4 : m < 99 ? 5 : 6;
const bNnd = m => m <= 1 ? 0 : m === 2 ? 1 : m === 3 ? 2 : m <= 5 ? 3 : m <= 8 ? 4 : m < 99 ? 5 : 6;
const bCnt5 = n => n === 0 ? 0 : n === 1 ? 1 : n === 2 ? 2 : n <= 4 ? 3 : n <= 8 ? 4 : 5;
const bLife = v => v === 0 ? 0 : v <= 4 ? 1 : v <= 9 ? 2 : v <= 19 ? 3 : v <= 49 ? 4 : v <= 99 ? 5 : v <= 199 ? 6 : 7;
const bNat = v => v === 0 ? 0 : v === 1 ? 1 : v <= 3 ? 2 : v <= 7 ? 3 : v <= 15 ? 4 : 5;
const bClaim = v => v === 0 ? 0 : v === 1 ? 1 : v === 2 ? 2 : v <= 5 ? 3 : 4;
const bUnits = v => v <= 3 ? 0 : v <= 7 ? 1 : v <= 15 ? 2 : v <= 31 ? 3 : 4;
const PV = 64; // piece vector length (see pieceAdd)

function mapKey(g) { return g.map === 'Prisoners Dilemma' && g.variant === '10' ? 'Prisoners Dilemma (10)' : g.map; }
const acc = {};
function node(group, map) {
  const a = acc[group] || (acc[group] = {});
  return a[map] || (a[map] = { n: 0, nPh: [0, 0, 0, 0, 0], nBin: new Array(NB).fill(0), win: 0, b: {}, ep: {}, tag: {}, tagD: {}, dr: {}, sp: {}, dt: {}, cp: {}, h: {}, pc: {}, ph: {}, keys: [] });
}
const addArr = (obj, k, arr) => { if (!arr) return; const a = obj[k] || (obj[k] = new Array(arr.length).fill(0)); for (let i = 0; i < arr.length; i++) a[i] += arr[i] || 0; };
const addAt = (obj, k, len, i, v = 1) => { const a = obj[k] || (obj[k] = new Array(len).fill(0)); a[i] += v; };

function pieceAdd(A, p, top) {
  const [ti, born, bl, pl, cls0, pk, bt, bv, bdBig, bnnd, bn5, life, end, Lf, maxL, steps, nat, natOwn, natEnemy, dOwn, dEnemy, spr, splitsN, C,
    turns, tOwn, tEnemy, n30, alive30, drops, eOwn, eOwnBig, eEnemy, dBigLast, dBigMax, dBig10, claim30, claimEat30, csT, fsT, eOwnP, eLonger, id, bu] = p;
  const cls = top ? (pl <= 4 ? 10 : pl <= 7 ? 11 : 12) : cls0;
  const ph = phaseOf(born), dead = end > 0;
  const delivered = (dead ? eOwn : Lf) + C, net = delivered - bl, newMass = nat + dEnemy - spr - (dead ? Lf - eOwn : 0);
  for (const key of [ph + '|' + cls, ph + '|all', 'all|' + cls, 'all|all']) {
    const v = A.pc[key] || (A.pc[key] = new Array(PV).fill(0));
    v[0]++; v[1] += life; v[2] += steps; v[3] += nat; v[4] += n30 >= 1 ? 1 : 0; v[5] += alive30; v[6] += natOwn; v[7] += natEnemy; v[8] += dOwn; v[9] += dEnemy;
    v[10] += spr; v[11] += splitsN; v[12] += C; v[13] += turns; v[14] += tOwn; v[15] += tEnemy; v[16 + end]++; v[25] += Lf; v[26] += maxL; v[27] += drops;
    v[28] += eOwn; v[29] += eOwnBig; v[30] += eEnemy; v[31] += eOwnP; v[32] += eLonger; v[33] += delivered; v[34] += net; v[35] += newMass; v[36] += claim30;
    v[37] += claimEat30; v[38] += claim30 >= 1 ? 1 : 0; v[39] += csT; v[40] += fsT; v[41] += bl; v[42] += n30; v[43] += bv; v[44 + bt]++;
    const fedOk = end === 1 && eOwn * 2 >= drops && eEnemy === 0 ? 1 : 0; v[47] += fedOk; v[48] += end === 1 && eOwnBig * 2 >= drops ? 1 : 0; v[49] += net > 0 ? 1 : 0;
    v[50] += dead ? 1 : 0; v[51] += dead ? Lf : 0; v[52] += !dead ? Lf : 0; v[53] += nat + dOwn + dEnemy; v[54] += life >= 100 ? 1 : 0;
    v[55] += pk; v[56] += end === 1 && csT > 0 ? 1 : 0; v[57] += end === 1 && fsT > 0 ? 1 : 0; v[58] += (end === 1 || end === 2) && eOwnBig > 0 ? eOwnBig : 0;
    v[59] += tOwn + tEnemy < turns ? turns - tOwn - tEnemy : 0; v[60] += bu; v[61] += bn5; v[62] += bnnd < 99 ? bnnd : 0; v[63] += bnnd < 99 ? 1 : 0;
    // histograms and cross-tabs
    const h = A.ph[key] || (A.ph[key] = {});
    const hx = (name, len, i, v2 = 1) => { const a = h[name] || (h[name] = new Array(len).fill(0)); a[i] += v2; };
    hx('life', 8, bLife(life)); hx('nat', 6, bNat(nat)); hx('big', 7, bDist(bdBig)); hx('nnd', 7, bNnd(bnnd)); hx('n5', 6, bCnt5(bn5)); hx('end', 9, end);
    const ate = n30 >= 1 ? 1 : 0;
    hx('n30_nnd', 14, bNnd(bnnd) * 2 + ate); hx('n30_n5', 12, bCnt5(bn5) * 2 + ate); hx('n30_claim', 10, bClaim(claim30) * 2 + ate); hx('n30_bt', 6, bt * 2 + ate);
    hx('n30_big', 14, bDist(bdBig) * 2 + ate); hx('n30_view', 4, bv * 2 + ate); hx('n30_units', 10, bUnits(bu) * 2 + ate);
    hx('claim', 5, bClaim(claim30)); hx('claimEat', 5, bClaim(claimEat30));
    if (end === 1) { hx('fedBirth', 7, bDist(bdBig)); hx('fedMax', 7, bDist(dBigMax)); hx('fed10', 7, bDist(dBig10)); hx('fedLast', 7, bDist(dBigLast)); hx('fedLife', 8, bLife(life)); }
    if (end === 2) { hx('trapLast', 7, bDist(dBigLast)); hx('trapLife', 8, bLife(life)); }
    hx('net', 9, net <= -3 ? 0 : net === -2 ? 1 : net === -1 ? 2 : net === 0 ? 3 : net === 1 ? 4 : net === 2 ? 5 : net <= 4 ? 6 : net <= 8 ? 7 : 8);
  }
}

function addGame(g) {
  const top = g.src === 'top';
  const sides = [];
  if (top) {
    const inactive = s => g[s].splits <= 3 && g[s].sonar === 0;
    if (inactive('A') || inactive('B') || g.A.faults >= 3 || g.B.faults >= 3) { excluded.inactive++; return; }
    if (!g.winner) { excluded.draw++; return; }
    const w = g.winner, l = w === 'A' ? 'B' : 'A';
    sides.push([w, 'TW'], [l, 'TL']);
    if (T7.has(w === 'A' ? g.teamA : g.teamB)) sides.push([w, 'T7W']);
  } else {
    const bot = SETGROUP[g.set]; if (!bot) { excluded.unknownSet++; return; }
    const us = g.us, them = us === 'A' ? 'B' : 'A';
    sides.push([us, bot], [them, 'X'], [them, 'X:' + bot]);
  }
  const mk = mapKey(g);
  for (const [s, grp] of sides) {
    const A = node(grp, mk), T = g[s];
    A.n++; if (g.winner === s) A.win++;
    for (let p = 0; p < 5; p++) if (g.rounds > PHSTART[p]) A.nPh[p]++;
    for (let i = 0; i < NB; i++) if (g.rounds > i * 10) A.nBin[i]++;
    for (const [k, v] of Object.entries(T.b)) addArr(A.b, k, v);
    for (const [k, v] of Object.entries(T.ep)) addArr(A.ep, k, v);
    for (const [k, v] of Object.entries(T.tag)) { if (k.includes('|')) addArr(A.tagD, k, v); else addArr(A.tag, k, v); }
    for (const [k, v] of Object.entries(T.dr)) addArr(A.dr, k, v);
    for (const [k, v] of Object.entries(T.sp)) addArr(A.sp, k, v);
    for (const [k, v] of Object.entries(T.dt)) addArr(A.dt, k, v);
    for (const [k, v] of Object.entries(T.h)) addArr(A.h, k, v);
    for (const [k, v] of Object.entries(T.cp)) {
      const c = A.cp[k] || (A.cp[k] = { s: new Array(NB).fill(0), c: new Array(NB).fill(0) });
      for (let i = 0; i < NB; i++) if (v[i] !== null && v[i] !== undefined) { c.s[i] += v[i]; c.c[i]++; }
    }
    const ti = s === 'A' ? 0 : 1;
    for (const p of g.P) if (p[0] === ti) pieceAdd(A, p, top);
    if (A.keys.length < 4000) A.keys.push(g.key);
  }
}

const excluded = { inactive: 0, draw: 0, unknownSet: 0, chkBad: 0 };
const chkSum = {};
async function readFile(f) {
  let n = 0;
  const gz = zlib.createGunzip(); let tail = null;
  gz.on('error', e => { tail = e; });                       // a member still being written (preview while extracting)
  const rl = readline.createInterface({ input: fs.createReadStream(f).pipe(gz), crlfDelay: Infinity });
  gz.on('error', () => rl.close());
  for await (const l of rl) {
    if (!l.trim()) continue;
    const g = JSON.parse(l); n++;
    let bad = 0; for (const [k, v] of Object.entries(g.chk)) { chkSum[k] = (chkSum[k] || 0) + v; if (v) bad = 1; }
    if (bad) excluded.chkBad++;
    addGame(g);
  }
  if (tail) console.error(`${path.basename(f)}: stopped at an incomplete member after ${n} games (${tail.code || tail.message})`);
  return n;
}

async function main() {
  const argv = process.argv.slice(2);
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const out = path.resolve(ROOT, opt('out', '.cache/supply-chain/agg.json'));
  const files = fs.readdirSync(CACHE).filter(f => f.endsWith('.jsonl.gz'));
  const topName = opt('top', 'top-all') + '.jsonl.gz';
  const counts = {};
  for (const f of files) {
    if (f.startsWith('top-') && f !== topName) continue;
    const n = await readFile(path.join(CACHE, f)); counts[f] = n;
    console.error(`${f}: ${n} games`);
  }
  fs.writeFileSync(out, JSON.stringify({ at: new Date().toISOString(), counts, excluded, chkSum, acc }));
  console.error(`wrote ${path.relative(ROOT, out)}; excluded ${JSON.stringify(excluded)}; checks ${JSON.stringify(chkSum)}`);
}
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
module.exports = { SETGROUP, T7, R500, phaseOf };
