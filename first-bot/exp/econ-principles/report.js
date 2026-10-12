#!/usr/bin/env node
// Tables for research/observations/economy-principles.md from .cache/econ-principles/*.jsonl (exp/econ-principles/extract.js).
// usage: node exp/econ-principles/report.js [--top top-all] [--sets a,b,...] > exp/econ-principles/report.txt
'use strict';
const fs = require('fs'), path = require('path'), readline = require('readline');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'econ-principles');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const TOPNAME = opt('top', 'top-all');
const SETS = opt('sets', 'cand-stack1-online,cand-stack2-online,cand-stack3-online,cand-stack4-online,cand-stack5-online,cand-stack6-online,cand-merge2-online,cand-merge2-online-r2,cand-merge2-online-r3,cand-swarm8-online,cand-avoid6-online,cand-portal1-online,base-px8-online,base-px9d-online,px-king-v2-online,baseline-r1,baseline-r1b,baseline-r1c').split(',');
const ELIM = new Set(['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default']);
const MAPS = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma', 'Default', 'Devil', 'Prisoners Dilemma', 'Queen Of Spades', 'Trophy'];
const f1 = v => (v === null || v === undefined || !isFinite(v)) ? '–' : (Math.round(v * 10) / 10).toFixed(1);
const f2 = v => (v === null || v === undefined || !isFinite(v)) ? '–' : v.toFixed(2);
const pc = v => (v === null || v === undefined || !isFinite(v)) ? '–' : (100 * v).toFixed(0) + '%';
const out = [];
const D = {}; // derived values for exp/econ-principles/doc.js
const P = (...a) => out.push(a.join(' '));
const tbl = (head, rows) => { P('| ' + head.join(' | ') + ' |'); P('|' + head.map(() => '---').join('|') + '|'); for (const r of rows) P('| ' + r.join(' | ') + ' |'); P(''); };
const inc = (o, k, v = 1) => { o[k] = (o[k] || 0) + v; };
const acc = (o, k, vals) => { const a = o[k] || (o[k] = new Array(vals.length).fill(0)); for (let i = 0; i < vals.length; i++) a[i] += vals[i]; };
const bkt8 = d => d <= -3 ? '≤−3' : d >= 3 ? '≥+3' : (d > 0 ? '+' : d < 0 ? '−' : '') + Math.abs(d);
const B8 = ['≤−3', '−2', '−1', '0', '+1', '+2', '≥+3'];
const bkt3 = d => d <= -2 ? '≤−2' : d >= 2 ? '≥+2' : (d > 0 ? '+' : d < 0 ? '−' : '') + Math.abs(d);
const B3 = ['≤−2', '−1', '0', '+1', '≥+2'];
const lenC = L => L <= 2 ? '2' : L <= 4 ? '3-4' : L <= 7 ? '5-7' : L <= 14 ? '8-14' : '15+';
const LC = ['2', '3-4', '5-7', '8-14', '15+'];
const kindOf = m => ELIM.has(m) ? 'elim' : 'r500';

// ---------------------------------------------------------------------------------------------------------------
// accumulators
const A = {
  n: { top: 0, topW: 0, ours: 0 }, nSet: {}, chk: {},
  // E4 contacts: key role|kind|bucket -> [n, drops, own20, opp20, net20, own10, opp10, Lm, Lv, win]
  C8: {}, C3: {}, Clen: {}, Cking: {}, C8x3: {}, Cdef: {},
  // E4 opportunities: role|Lclass|bucket -> [n, taken1, takenAny, died10, rammed1]
  O8: {}, O3: {}, Ob3: {}, Ob3map: {}, Ob3ph: {}, B3pmap: {}, Oteam: {},
  // B3 (L<=4) taken payoff by d3/d8: role|bucket -> [n, drops, own20, opp20, net20]
  B3p8: {}, B3p3: {}, B3pX: {}, B3pAlly: {}, eliteO3: {}, eliteB3p: {}, eliteN: 0,
  // ours
  oursC: {}, oursC8: {}, oursRam4: [], oursO: {}, oursB3: {},
  // E7 king deaths
  K: {}, Kx: {}, Kgame: {},
  // E1/E2/E3
  split: {}, units: {}, track: {}, resp: {}, layout: {}, oursUnits: {}, rr: [], tgN: 0,
  // E5
  nat: {}, natOurs: {}, natGap: [],
  // E6
  occ: {}, sb: {}, sbOurs: {},
  // E8
  S: {}, Sonset: [], CP: {}, Sours: {}, SoursRows: [], E8tg: [], E8near: [],
  // E9
  BK: {}, CH: {}, CHdef: {}, BKours: {}, CHours: {},
};

function roleOf(g, t) { if (!g.winner) return 'D'; return (g.winner === 'A' ? 0 : 1) === t ? 'W' : 'L'; }

function addGame(g, src) {
  for (const [k, v] of Object.entries(g.chk)) inc(A.chk, k, v);
  const kind = kindOf(g.map), us = g.us ? (g.us === 'A' ? 0 : 1) : -1;
  const role = t => src === 'top' ? roleOf(g, t) : (t === us ? 'U' : 'X'); // U = our team, X = the opponent (ours)
  if (src === 'top') { A.n.top++; if (g.winner) A.n.topW++; } else { A.n.ours++; inc(A.nSet, g.set); }
  const layout = g.map + '/' + g.lay;

  // ---- E4 contacts (mover perspective)
  for (const c of g.C) {
    const mt = c[1], Lm = c[2], Lv = c[3], rl = role(mt);
    const lc = c.slice(14, 24); // v3o v3e m3o m3e m8o m8e c8o c8e L8o L8e
    const d3 = lc[0] - lc[1], d8 = lc[4] - lc[5];
    const drops = Math.ceil(Lm / 2) + Math.ceil(Lv / 2);
    const own20 = c[29], opp20 = c[32], own10 = c[28], opp10 = c[31];
    const net20 = (Lv - Lm) + own20 - opp20;
    const v = [1, drops, own20, opp20, net20, own10, opp10, Lm, Lv];
    acc(A.C8, rl + '|' + kind + '|' + bkt8(d8), v); acc(A.C8, rl + '|all|' + bkt8(d8), v);
    acc(A.C3, rl + '|all|' + bkt3(d3), v);
    { const defs = { v3: lc[0] - lc[1], m3: lc[2] - lc[3], m8: lc[4] - lc[5], c8: lc[6] - lc[7], L8: lc[8] - lc[9] };
      for (const [dn, dv] of Object.entries(defs)) acc(A.Cdef, rl + '|' + dn + '|' + (dv > 0 ? '+' : dv < 0 ? '−' : '0'), v); }
    acc(A.C8x3, rl + '|' + (d3 > 0 ? 'v+' : d3 < 0 ? 'v−' : 'v0') + '|' + (d8 > 0 ? 'm+' : d8 < 0 ? 'm−' : 'm0'), v);
    const rel = Lm < Lv ? 'short→long' : Lm === Lv ? 'equal' : 'long→short';
    acc(A.Clen, rl + '|' + rel + '|' + (d8 > 0 ? '+' : d8 < 0 ? '−' : '0'), v);
    const kk = c[4] && Lm >= 8 ? 'moverKing≥8' : c[5] && Lv >= 8 ? 'victimKing≥8' : c[4] || c[5] ? 'king<8' : 'none';
    acc(A.Cking, rl + '|' + kk + '|' + (d8 > 0 ? '+' : d8 < 0 ? '−' : '0'), v);
    if (src !== 'top') {
      acc(A.oursC, g.set + '|' + rl, v);
      acc(A.oursC8, (rl === 'U' ? 'U' : 'X') + '|' + bkt8(d8), v);
      if (rl === 'U' && c[26] >= 2 && c[26] <= 4) A.oursRam4.push({ set: g.set, key: g.key, r: c[0], Lm, Lv, d3, d8, own20, opp20, drops, net20, tag: c[26], map: g.map, lc });
    }
  }
  // ---- E4 opportunities
  for (const o of g.O) {
    const t = o[1], L = o[2], Le = o[3], rl = role(t);
    const lc = o.slice(8, 18); const d3 = lc[0] - lc[1], d8 = lc[4] - lc[5];
    const taken1 = o[18] === 1 ? 1 : 0, takenAny = o[18] > 0 ? 1 : 0;
    const died10 = o[19] >= 0 && o[19] - o[0] <= 10 && !taken1 ? 1 : 0;
    const rammed1 = o[19] >= 0 && o[19] - o[0] <= 1 && o[20] === 2 ? 1 : 0;
    const lcl = L <= 4 ? 'L≤4' : L <= 7 ? 'L5-7' : 'L≥8';
    const v = [1, taken1, takenAny, died10, rammed1];
    acc(A.O8, rl + '|' + lcl + '|' + bkt8(d8), v);
    acc(A.O3, rl + '|' + lcl + '|' + bkt3(d3), v);
    if (L <= 4) acc(A.Ob3, rl + '|' + (Le >= L ? 'Le≥L' : 'Le<L') + '|' + bkt3(d3), v);
    if (L <= 4) acc(A.Ob3map, rl + '|' + g.map + '|' + (d3 >= 1 ? '+' : d3 === 0 ? '0' : '−'), v);
    if (L <= 4 && src === 'top') acc(A.Oteam, (t ? g.teamB : g.teamA) + '|' + (d3 >= 1 ? '+' : d3 === 0 ? '0' : '−'), v);
    if (L <= 4) { const ph = o[0] < 100 ? 'r0-99' : o[0] < 250 ? 'r100-249' : o[0] < 350 ? 'r250-349' : 'r350+'; acc(A.Ob3ph, rl + '|' + ph + '|' + (d3 >= 1 ? '+' : d3 === 0 ? '0' : '−'), v); }
    if (src !== 'top') acc(A.oursO, g.set + '|' + rl + '|' + lcl, v);
    if (src !== 'top' && L <= 4) acc(A.oursB3, g.set + '|' + rl + '|' + (d3 >= 1 ? '+' : d3 === 0 ? '0' : '−'), v);
  }
  // elite subset: both teams ranked <= 8 at collection time (index rankA/rankB)
  const elite = src === 'top' && g.rankA && g.rankB && g.rankA <= 8 && g.rankB <= 8;
  if (elite) for (const o of g.O) { if (o[2] > 4) continue; const d3 = o[8] - o[9]; acc(A.eliteO3, role(o[1]) + '|' + (d3 >= 1 ? '+' : d3 === 0 ? '0' : '−'), [1, o[18] === 1 ? 1 : 0, o[18] > 0 ? 1 : 0, 0, 0]); }
  if (elite) A.eliteN++;
  // B3 payoff (taken, L<=4, one step) — from the contacts that follow an adjacency
  for (const c of g.C) {
    const Lm = c[2]; if (Lm > 4 || c[6] || !c[7]) continue; // one-step ram of an adjacent head, mover length <= 4
    const rl = role(c[1]); const lc = c.slice(14, 24); const d3 = lc[0] - lc[1], d8 = lc[4] - lc[5];
    const drops = Math.ceil(Lm / 2) + Math.ceil(c[3] / 2), own20 = c[29], opp20 = c[32];
    const v = [1, drops, own20, opp20, (c[3] - Lm) + own20 - opp20, c[3] >= Lm ? 1 : 0];
    acc(A.B3p8, rl + '|' + bkt8(d8), v); acc(A.B3p3, rl + '|' + bkt3(d3), v);
    acc(A.B3pX, rl + '|' + (d3 >= 1 ? 'v≥+1' : d3 === 0 ? 'v0' : 'v≤−1') + '|' + (d8 >= 1 ? 'm≥+1' : d8 === 0 ? 'm0' : 'm≤−1'), v);
    acc(A.B3pmap, rl + '|' + g.map + '|' + (d3 >= 1 ? '+' : d3 === 0 ? '0' : '−'), v);
    if (elite) acc(A.eliteB3p, rl + '|' + (d3 >= 1 ? '+' : d3 === 0 ? '0' : '−'), v);
    { const a8 = lc[4], ab = a8 === 0 ? '0' : a8 <= 2 ? '1-2' : a8 <= 5 ? '3-5' : '6+'; acc(A.B3pAlly, rl + '|' + (d3 >= 1 ? '+' : d3 === 0 ? '0' : '−') + '|' + ab, v); }
  }
  // ---- E7 king deaths (L >= 8), attacker perspective
  for (const k of g.KD) {
    const t = k[1], L = k[2]; if (L < 8) continue;
    const cause = k[3], oL = k[4], rl = role(t); // rl = the king's team role
    const how = cause === 2 ? 'rammed' : cause === 3 ? 'rammer' : (cause === 4 || (cause === 1 && k[13] === 'O')) && oL > 0 ? 'body' : cause === 0 ? 'sac' : cause === 1 ? 'trap' : 'other';
    const ph = k[0] < 250 ? 'r<250' : k[0] < 400 ? 'r250-399' : 'r400+';
    const grp = k[6] >= 1 ? 'grp' : 'solo';
    const own20 = k[16], opp20 = k[19]; // king-team own20 (index 15+1), opp20 (15+4)
    const kd20 = k[23], kd0 = k[24];
    const lost = g.winner ? ((g.winner === 'A' ? 0 : 1) === t ? 0 : 1) : 0.5;
    const v = [1, L, oL, opp20, own20, kd0, kd20, lost, Math.ceil(L / 2)];
    acc(A.K, kind + '|' + rl + '|' + how, v);
    if (how === 'rammed' || how === 'rammer' || how === 'body') {
      const arl = role(1 - t); // the attacker team's role
      acc(A.Kx, kind + '|' + arl + '|' + how + '|' + lenC(oL) + '|' + ph + '|' + grp, v);
      acc(A.Kx, kind + '|' + arl + '|' + how + '|' + lenC(oL) + '|*|' + grp, v);
      acc(A.Kx, kind + '|' + arl + '|*|' + lenC(oL) + '|*|*', v);
      acc(A.Kx, kind + '|' + arl + '|*|*|' + ph + '|' + grp, v);
    }
  }
  // ---- E1/E2 splits and units
  for (const t of [0, 1]) {
    const T = t ? g.B : g.A, O = t ? g.A : g.B, rl = role(t);
    if (src === 'top' && rl === 'D') continue;
    const key = (src === 'top' ? rl : (rl === 'U' ? 'U' : 'X')) + '|' + g.map;
    const a = A.split[key] || (A.split[key] = { n: 0, sp: new Array(50).fill(0), u: new Array(51).fill(0), roundsAlive: new Array(50).fill(0) });
    a.n++; for (let b = 0; b < 50; b++) { a.sp[b] += T.sp[b]; if (b * 10 < g.rounds) a.roundsAlive[b]++; } for (let i = 0; i <= 50; i++) a.u[i] += T.u[i];
    // response: splits in bin b vs (own - opp) units at the start of bin b, b = 2..29 (r20-299), game still running
    if (src === 'top' && rl !== 'D') { A.tgN++; for (let b = 2; b < 30; b++) { if (b * 10 + 10 > g.rounds) break; A.rr.push(MAPS.indexOf(g.map), rl === 'W' ? 1 : 0, A.tgN, b, T.sp[b], T.u[b] - O.u[b], T.u[b]); } }
    if (src === 'top') for (let b = 2; b < 30; b++) {
      if (b * 10 + 10 > g.rounds) break;
      const d = T.u[b] - O.u[b], db = d <= -5 ? '≤−5' : d <= -2 ? '−4..−2' : d <= 1 ? '−1..+1' : d <= 4 ? '+2..+4' : '≥+5';
      acc(A.resp, rl + '|' + g.map + '|' + b + '|' + db, [1, T.sp[b], T.u[b]]);
      acc(A.resp, 'mapbin|' + g.map + '|' + b, [1, T.sp[b], T.u[b]]);
    }
    if (src === 'top' && rl === 'W') {
      const ly = A.layout[layout] || (A.layout[layout] = { n: 0, W: g.W, H: g.H, nSpawnT: g.nSpawnT, nFount: g.nFount, cap: g.cap, flow: 0, u50: [], u100: [], u200: [], oppU100: [], elim: kindOf(g.map) });
      ly.n++; ly.flow += g.natSpawned / Math.max(1, g.rounds); ly.u50.push(T.u[5]); if (g.rounds > 100) ly.u100.push(T.u[10]); if (g.rounds > 200) ly.u200.push(T.u[20]);
    }
    if (src !== 'top' && rl === 'U') {
      const k2 = g.set + '|' + layout; const o = A.oursUnits[k2] || (A.oursUnits[k2] = { u50: [], u100: [], u200: [] });
      o.u50.push(T.u[5]); if (g.rounds > 100) o.u100.push(T.u[10]); if (g.rounds > 200) o.u200.push(T.u[20]);
    }
    // tracking: own vs opp units at r50/100/200
    if (src === 'top') for (const i of [5, 10, 20]) if (i * 10 < g.rounds) acc(A.track, g.map + '|' + i, [1, T.u[i], O.u[i], T.u[i] * O.u[i], T.u[i] * T.u[i], O.u[i] * O.u[i]]);
    // ---- E5 early eating by territory (r0-99)
    let no = 0, ne = 0, nn = 0; for (let b = 0; b < 10; b++) { no += T.natO[b]; ne += T.natE[b]; nn += T.natN[b]; }
    let no5 = 0, ne5 = 0, nn5 = 0; for (let b = 0; b < 5; b++) { no5 += T.natO[b]; ne5 += T.natE[b]; nn5 += T.natN[b]; }
    const kk = (src === 'top' ? rl : (rl === 'U' ? 'U|' + g.set : 'X|' + g.set)) + '|' + kind;
    acc(A.nat, kk, [1, no, nn, ne, no5, nn5, ne5]);
    // ---- E6 occupancy and blocked spawns
    const ph3 = [0, 1, 2];
    const occ = ph3.map(ph => [0, 1, 2].map(r => g.OCC[(t * 3 + ph) * 3 + r])); // [phase][own, neutral, enemy]
    const sbOwnTerr = t + 1, sbEnemyTerr = 2 - t;
    let blkE = 0, blkO = 0, blkN = 0, pearlE = 0, pearlO = 0;
    for (const ph of ph3) { blkE += g.SB[(ph * 5 + t) * 3 + sbEnemyTerr]; blkO += g.SB[(ph * 5 + t) * 3 + sbOwnTerr]; blkN += g.SB[(ph * 5 + t) * 3 + 0];
      for (const b of [2, 3]) { pearlE += g.SB[(ph * 5 + b) * 3 + sbEnemyTerr]; pearlO += g.SB[(ph * 5 + b) * 3 + sbOwnTerr]; } }
    let spEnemy = 0, spOwn = 0; for (const ph of ph3) { spEnemy += g.SPN[ph * 3 + sbEnemyTerr]; spOwn += g.SPN[ph * 3 + sbOwnTerr]; }
    const natEnemyAll = (O.eatNat || []).reduce((s, v) => s + v, 0);
    acc(A.occ, kk, [1, ...occ[0], ...occ[1], ...occ[2], blkE, blkO, blkN, pearlE, pearlO, spEnemy, spOwn, natEnemyAll, g.rounds]);
    // ---- E9 chase episodes (as chaser team) and body kills (as killer team)
    acc(A.CH, kk, [1, ...g.CH[t]]); acc(A.CHdef, kk, [1, ...g.CH[1 - t]]);
  }
  // E6 winner - loser difference within a game
  if (src === 'top' && g.winner) {
    const w = g.winner === 'A' ? 0 : 1, l = 1 - w;
    const occE = t => g.OCC[(t * 3 + 0) * 3 + 2] + g.OCC[(t * 3 + 1) * 3 + 2] + g.OCC[(t * 3 + 2) * 3 + 2];
    acc(A.sb, kind, [1, occE(w), occE(l)]);
    const T = w ? g.B : g.A, L = w ? g.A : g.B; let we = 0, le = 0, wa = 0, la = 0;
    for (let b = 0; b < 10; b++) { we += T.natE[b]; le += L.natE[b]; wa += T.natE[b] + T.natO[b] + T.natN[b]; la += L.natE[b] + L.natO[b] + L.natN[b]; }
    A.natGap.push([kind, we, le, wa, la]);
  }
  for (const b of g.BK) {
    const killer = 1 - b[1], rl = role(killer);
    const kk = (src === 'top' ? rl : (rl === 'U' ? 'U|' + g.set : 'X|' + g.set)) + '|' + kind;
    const cls = b[5] === 2 ? 'chasing another ally, 1-2 turns' : b[5] === 1 ? 'chasing the owner, 1-2 turns' : 'no chase or chase >= 3 turns';
    acc(A.BK, kk + '|' + cls, [1, b[2], b[3], b[4]]);
  }
  // ---- E8 sacrifices (top: all teams; ours: our team)
  for (const s of g.S) {
    const t = s[1], rl = role(t);
    if (src !== 'top' && rl !== 'U') continue;
    const kk = (src === 'top' ? rl : 'U|' + g.set) + '|' + kind;
    const dk = s[3], dkb = dk < 0 ? 'none' : dk <= 1 ? '≤1' : dk <= 3 ? '2-3' : dk <= 8 ? '4-8' : dk <= 16 ? '9-16' : '17+';
    const own20 = s[16], opp20 = s[19], kingEat20 = s[21];
    acc(A.S, kk + '|' + dkb, [1, s[2], own20, opp20, kingEat20, s[0], dk >= 0 ? dk : 0, Math.ceil(s[2] / 2)]);
    if (src === 'top' && kind === 'r500') A.Sonset.push([rl === 'W' ? 1 : 0, s[0], s[3], s[4], s[5], s[2], s[6], s[7], s[8]]);
    if (src !== 'top') A.SoursRows.push([g.set, s[0], s[2], s[3], s[4], s[5], s[12], own20, opp20, kingEat20]);
  }
  if (src === 'top' && kind === 'r500' && g.winner && g.rounds >= 500) for (const t of [0, 1]) {
    // team-game: onset50 of sacrificed length (r>=200) and mean dK of non-king dragons at r300
    const ss = g.S.filter(x => x[1] === t).sort((a, b) => a[0] - b[0]); const tot = ss.reduce((q, x) => q + x[2], 0);
    const cps = g.CP.filter(c => c[0] === 300 && c[1] === t && c[3] >= 0);
    if (tot >= 10 && cps.length >= 3) { let c = 0, on = -1; for (const x of ss) { c += x[2]; if (c * 2 >= tot) { on = x[0]; break; } }
      A.E8tg.push([t ? g.teamB : g.teamA, roleOf(g, t) === 'W' ? 1 : 0, on, cps.reduce((q, x) => q + x[3], 0) / cps.length, g.map]); }
  }
  if (src === 'top' && kind === 'r500') for (const s of g.S) {
    // king-directed sacrifices (dK <= 3 at death) with the distance at r300 / r350 known: death round by that distance
    if (s[3] < 0 || s[3] > 3) continue; const rl = role(s[1]); if (rl === 'D') continue;
    for (const [cp, i] of [[300, 6], [350, 7]]) if (s[i] >= 0 && s[0] >= cp) A.E8near.push([rl === 'W' ? 1 : 0, cp, s[i], s[0], s[2]]);
  }
  if (src === 'top' && kind === 'r500') for (const c of g.CP) {
    // [cp, t, L, dK, id, fateRound, fateCause]
    const rl = role(c[1]); if (rl === 'D' || c[3] < 0) continue;
    const db = c[3] <= 3 ? '≤3' : c[3] <= 8 ? '4-8' : c[3] <= 16 ? '9-16' : '17+';
    const sac = c[6] === 0 ? 1 : 0, other = c[5] >= 0 && c[6] !== 0 ? 1 : 0;
    acc(A.CP, rl + '|' + c[0] + '|' + db + '|' + (c[2] <= 4 ? 'L≤4' : c[2] <= 7 ? 'L5-7' : 'L≥8'), [1, sac, sac ? c[5] : 0, other, c[3]]);
  }
}

async function readFile(f, src) {
  if (!fs.existsSync(f)) return 0;
  const rl = readline.createInterface({ input: fs.createReadStream(f), crlfDelay: Infinity });
  let n = 0;
  for await (const line of rl) { if (!line.trim()) continue; let g; try { g = JSON.parse(line); } catch { A.badLines = (A.badLines || 0) + 1; continue; } addGame(g, src); n++; }
  return n;
}

// ---------------------------------------------------------------------------------------------------------------
function rowC(a) { if (!a) return null; const n = a[0]; return [n, pc(a[5] / a[1]), pc(a[6] / a[1]), pc(a[2] / a[1]), pc(a[3] / a[1]), f2(a[4] / n), f1(a[7] / n), f1(a[8] / n)]; }
async function main() {
  const nTop = await readFile(path.join(CACHE, TOPNAME + '.jsonl'), 'top');
  for (const s of SETS) await readFile(path.join(CACHE, 'online-' + s + '.jsonl'), 'ours');
  P(`# econ-principles report (${new Date().toISOString()})`);
  P(`population: top ${A.n.top} games (with a winner ${A.n.topW}); ours ${A.n.ours} games: ${JSON.stringify(A.nSet)}`);
  P(`checks (all expected 0): ${JSON.stringify(A.chk)}`); P('');

  P('## E4 contacts: mover perspective, d8 = own - enemy heads within Manhattan 8 of the contact (pair excluded)');
  P('columns: n, drops eaten by mover team <=20R, by victim team <=20R, net20 = (Lv-Lm)+own20-opp20 per contact, mean Lm, mean Lv');
  for (const rl of ['W', 'L', 'U', 'X']) for (const kind of ['all', 'r500', 'elim']) {
    const rows = B8.map(b => { const r = rowC(A.C8[rl + '|' + kind + '|' + b]); return r ? [b, ...r] : null; }).filter(Boolean);
    if (!rows.length) continue; P(`### role ${rl}, ${kind}`); tbl(['d8', 'n', 'own10', 'opp10', 'own20', 'opp20', 'net20', 'Lm', 'Lv'], rows);
  }
  P('## E4 contacts by d3 (in view: Chebyshev 3 of the mover head at turn start)');
  for (const rl of ['W', 'L', 'U', 'X']) { const rows = B3.map(b => { const r = rowC(A.C3[rl + '|all|' + b]); return r ? [b, ...r] : null; }).filter(Boolean); if (rows.length) { P(`### ${rl}`); tbl(['d3', 'n', 'own10', 'opp10', 'own20', 'opp20', 'net20', 'Lm', 'Lv'], rows); } }
  P('## E4 contacts: sign of the local difference under five definitions (v3 view Chebyshev 3 of the mover head; m3/m8 Manhattan 3/8 of the contact; c8 Chebyshev 8; L8 summed length within Manhattan 8)');
  for (const rl of ['W', 'L', 'U', 'X']) { const rows = []; for (const dn of ['v3', 'm3', 'm8', 'c8', 'L8']) for (const sg of ['−', '0', '+']) { const r = rowC(A.Cdef[rl + '|' + dn + '|' + sg]); if (r) rows.push([dn, sg, ...r]); } if (rows.length) { P(`### ${rl}`); tbl(['def', 'sign', 'n', 'own10', 'opp10', 'own20', 'opp20', 'net20', 'Lm', 'Lv'], rows); } }
  P('## E4 contacts: view sign x radius-8 sign');
  for (const rl of ['W', 'L']) { const rows = []; for (const v of ['v−', 'v0', 'v+']) for (const m of ['m−', 'm0', 'm+']) { const r = rowC(A.C8x3[rl + '|' + v + '|' + m]); if (r) rows.push([v, m, ...r]); } P(`### ${rl}`); tbl(['view', 'r8', 'n', 'own10', 'opp10', 'own20', 'opp20', 'net20', 'Lm', 'Lv'], rows); }
  P('## E4 contacts by length relation and d8 sign');
  for (const rl of ['W', 'L']) { const rows = []; for (const rel of ['short→long', 'equal', 'long→short']) for (const s of ['−', '0', '+']) { const r = rowC(A.Clen[rl + '|' + rel + '|' + s]); if (r) rows.push([rel, s, ...r]); } P(`### ${rl}`); tbl(['relation', 'd8', 'n', 'own10', 'opp10', 'own20', 'opp20', 'net20', 'Lm', 'Lv'], rows); }
  P('## E4 contacts: king involvement and d8 sign');
  for (const rl of ['W', 'L']) { const rows = []; for (const kk of ['moverKing≥8', 'victimKing≥8', 'king<8', 'none']) for (const s of ['−', '0', '+']) { const r = rowC(A.Cking[rl + '|' + kk + '|' + s]); if (r) rows.push([kk, s, ...r]); } P(`### ${rl}`); tbl(['king', 'd8', 'n', 'own10', 'opp10', 'own20', 'opp20', 'net20', 'Lm', 'Lv'], rows); }

  P('## E4 opportunities (enemy head adjacent at turn start): take rate by d8 / d3');
  P('columns: n, one-step ram of it, any head-on ram, died within 10R without ramming, rammed by an enemy within 1R');
  for (const lcl of ['L≤4', 'L5-7', 'L≥8']) for (const rl of ['W', 'L', 'U', 'X']) {
    const rows = B8.map(b => { const a = A.O8[rl + '|' + lcl + '|' + b]; return a ? [b, a[0], pc(a[1] / a[0]), pc(a[2] / a[0]), pc(a[3] / a[0]), pc(a[4] / a[0])] : null; }).filter(Boolean);
    if (rows.length) { P(`### ${rl} ${lcl} by d8`); tbl(['d8', 'n', 'take1', 'takeAny', 'died10', 'rammed1'], rows); }
    const rows3 = B3.map(b => { const a = A.O3[rl + '|' + lcl + '|' + b]; return a ? [b, a[0], pc(a[1] / a[0]), pc(a[2] / a[0]), pc(a[3] / a[0]), pc(a[4] / a[0])] : null; }).filter(Boolean);
    if (rows3.length) { P(`### ${rl} ${lcl} by d3`); tbl(['d3', 'n', 'take1', 'takeAny', 'died10', 'rammed1'], rows3); }
  }
  P('## B3 (L<=4, adjacent enemy head) take rate by enemy length relation and d3');
  for (const rl of ['W', 'L', 'U', 'X']) { const rows = []; for (const le of ['Le≥L', 'Le<L']) for (const b of B3) { const a = A.Ob3[rl + '|' + le + '|' + b]; if (a) rows.push([le, b, a[0], pc(a[1] / a[0]), pc(a[3] / a[0]), pc(a[4] / a[0])]); } if (rows.length) { P(`### ${rl}`); tbl(['Le', 'd3', 'n', 'take1', 'died10', 'rammed1'], rows); } }
  P('## B3 payoff (one-step ram by L<=4 of an adjacent head): by d8, d3 and view x r8');
  const rowB = a => a ? [a[0], pc(a[2] / a[1]), pc(a[3] / a[1]), f2(a[4] / a[0]), pc(a[5] / a[0])] : null;
  for (const rl of ['W', 'L', 'U', 'X']) {
    const r8 = B8.map(b => { const r = rowB(A.B3p8[rl + '|' + b]); return r ? [b, ...r] : null; }).filter(Boolean);
    if (r8.length) { P(`### ${rl} by d8`); tbl(['d8', 'n', 'own20', 'opp20', 'net20', 'Lv≥Lm'], r8); }
    const r3 = B3.map(b => { const r = rowB(A.B3p3[rl + '|' + b]); return r ? [b, ...r] : null; }).filter(Boolean);
    if (r3.length) { P(`### ${rl} by d3`); tbl(['d3', 'n', 'own20', 'opp20', 'net20', 'Lv≥Lm'], r3); }
    const rx = []; for (const v of ['v≤−1', 'v0', 'v≥+1']) for (const m of ['m≤−1', 'm0', 'm≥+1']) { const r = rowB(A.B3pX[rl + '|' + v + '|' + m]); if (r) rx.push([v, m, ...r]); }
    if (rx.length) { P(`### ${rl} view x r8`); tbl(['view', 'r8', 'n', 'own20', 'opp20', 'net20', 'Lv≥Lm'], rx); }
  }
  P('## B3 per map: take rate (opportunities) and payoff (takes) by d3 sign');
  { const rows = []; for (const rl of ['W', 'L', 'U', 'X']) for (const m of MAPS) { const r = [rl, m]; let any = false; for (const sg of ['−', '0', '+']) { const a = A.Ob3map[rl + '|' + m + '|' + sg], b = A.B3pmap[rl + '|' + m + '|' + sg]; if (a) any = true; r.push(a ? `${pc(a[1] / a[0])} (${a[0]})` : '–', b ? `${pc(b[2] / b[1])}/${pc(b[3] / b[1])} ${f2(b[4] / b[0])}` : '–'); } if (any) rows.push(r); }
    tbl(['role', 'map', 'take d3−', 'pay d3− own/opp net', 'take d3=0', 'pay d3=0', 'take d3+', 'pay d3+'], rows); }
  P('## B3 by phase: take rate by d3 sign');
  tbl(['role|phase|d3', 'n', 'take1', 'died10', 'rammed1'], Object.entries(A.Ob3ph).sort().map(([k, a]) => [k, a[0], pc(a[1] / a[0]), pc(a[3] / a[0]), pc(a[4] / a[0])]));
  P('## ours: contacts per set (U = we moved)');
  tbl(['set|role', 'n', 'own10', 'opp10', 'own20', 'opp20', 'net20', 'Lm', 'Lv'], Object.entries(A.oursC).sort().map(([k, a]) => [k, ...rowC(a)]));
  P('## ours: ram4 contacts (stack1 tags)');
  { const R = A.oursRam4; const by = {}; for (const x of R) acc(by, x.set + '|tag' + x.tag + '|' + (x.d8 > 0 ? 'd8+' : x.d8 < 0 ? 'd8−' : 'd80') , [1, x.drops, x.own20, x.opp20, x.net20]);
    tbl(['set|tag|d8', 'n', 'own20', 'opp20', 'net20'], Object.entries(by).sort().map(([k, a]) => [k, a[0], pc(a[2] / a[1]), pc(a[3] / a[1]), f2(a[4] / a[0])]));
    P('ram4 rows: ' + R.map(x => `${x.key} r${x.r} Lm${x.Lm} Lv${x.Lv} d3=${x.d3} d8=${x.d8} own${x.own20}/opp${x.opp20}/${x.drops} tag${x.tag}`).join('; ')); P(''); }
  P('## ours: opportunities per set');
  tbl(['set|role|L', 'n', 'take1', 'takeAny', 'died10', 'rammed1'], Object.entries(A.oursO).sort().map(([k, a]) => [k, a[0], pc(a[1] / a[0]), pc(a[2] / a[0]), pc(a[3] / a[0]), pc(a[4] / a[0])]));

  P('## E7 king deaths (L>=8) by how (king-team role)');
  P('columns: n, mean king L, mean other L, king drops eaten by killer team 20R, by own team 20R, king diff before, after 20R, king team lost the game');
  tbl(['kind|role|how', 'n', 'L', 'oL', 'killer20', 'own20', 'kd0', 'kd20', 'lost'], Object.entries(A.K).sort().map(([k, a]) => [k, a[0], f1(a[1] / a[0]), f1(a[2] / a[0]), pc(a[3] / a[8]), pc(a[4] / a[8]), f1(a[5] / a[0]), f1(a[6] / a[0]), pc(a[7] / a[0])]));
  P('## E7 attacker length x phase x group (key: kind | attacker team role | how | attacker L | phase | group = another attacker-team head within Manhattan 3)');
  tbl(['kind|attacker role|how|attackerL|phase|group', 'n', 'L', 'oL', 'killer20', 'own20', 'kd0', 'kd20', 'lost'], Object.entries(A.Kx).sort().map(([k, a]) => [k, a[0], f1(a[1] / a[0]), f1(a[2] / a[0]), pc(a[3] / a[8]), pc(a[4] / a[8]), f1(a[5] / a[0]), f1(a[6] / a[0]), pc(a[7] / a[0])]));

  P('## E1 split curves: mean splits per team-game per 50 rounds (and units at r50/100/200/300/400)');
  { const rows = []; for (const [k, a] of Object.entries(A.split).sort()) { const s = []; for (let q = 0; q < 10; q++) { let v = 0; for (let b = q * 5; b < q * 5 + 5; b++) v += a.sp[b]; s.push(f1(v / a.n)); }
      const peak = Math.max(...a.sp.map(v => v / a.n)); let last = -1; for (let b = 0; b < 50; b++) if (a.sp[b] / a.n >= 0.25 * peak) last = b;
      let pre = 0, post = 0; for (let b = 30; b < 38; b++) pre += a.sp[b]; for (let b = 38; b < 50; b++) post += a.sp[b];
      rows.push([k, a.n, ...s, (last * 10) + '', f2(post / Math.max(1, pre) * (8 / 12)), [5, 10, 20, 30, 40].map(i => f1(a.u[i] / a.n)).join('/')]); }
    tbl(['role|map', 'n', 'r0', 'r50', 'r100', 'r150', 'r200', 'r250', 'r300', 'r350', 'r400', 'r450', 'last≥25%peak', 'rate r380-499 / r300-379', 'units r50/100/200/300/400'], rows); }
  P('## E1 split curve per 10 rounds, all maps pooled by kind (W/L), bins r300-499');
  for (const kind of ['r500', 'elim']) for (const rl of ['W', 'L']) {
    const sp = new Array(50).fill(0); let n = 0; for (const [k, a] of Object.entries(A.split)) { const [r, m] = k.split('|'); if (r !== rl || kindOf(m) !== kind) continue; n += a.n; for (let b = 0; b < 50; b++) sp[b] += a.sp[b]; }
    P(`${kind} ${rl} n=${n}: ` + sp.map((v, b) => (b * 10) + ':' + f2(v / n)).join(' ')); }
  P('');
  P('## E2 tracking: correlation of own and opponent units (top, per map, r50/r100/r200)');
  { const rows = []; for (const m of MAPS) { const row = [m]; for (const i of [5, 10, 20]) { const a = A.track[m + '|' + i]; if (!a) { row.push('–'); continue; } const n = a[0], mx = a[1] / n, my = a[2] / n; const cov = a[3] / n - mx * my, vx = a[4] / n - mx * mx, vy = a[5] / n - my * my; row.push(f2(cov / Math.sqrt(vx * vy)) + ` (n${n}, ${f1(mx)})`); } rows.push(row); } tbl(['map', 'r50', 'r100', 'r200'], rows); }
  P('## E2 split response: splits per 10R bin vs (own - opp) units at bin start, relative to the map-bin mean (top, r20-299)');
  { const agg = {}; for (const [k, a] of Object.entries(A.resp)) { const p = k.split('|'); if (p[0] === 'mapbin') continue; const [rl, m, b, db] = p; const mb = A.resp['mapbin|' + m + '|' + b]; const base = mb[1] / mb[0]; acc(agg, rl + '|' + kindOf(m) + '|' + db, [a[0], a[1], a[0] * base, a[2]]); }
    const DB = ['≤−5', '−4..−2', '−1..+1', '+2..+4', '≥+5'];
    const rows = []; for (const rl of ['W', 'L']) for (const kind of ['r500', 'elim']) for (const db of DB) { const a = agg[rl + '|' + kind + '|' + db]; if (a) rows.push([rl, kind, db, a[0], f2(a[1] / a[0]), f2(a[2] / a[0]), f2((a[1] - a[2]) / a[0]), f1(a[3] / a[0])]); }
    tbl(['role', 'kind', 'own−opp units', 'n bins', 'splits/bin', 'map-bin mean', 'excess', 'own units'], rows); }
  { // two-way demeaned: split - teamGameMean - mapBinMean + mapMean, by (own - opp) units bucket
    const R = A.rr, n = R.length / 7, tg = new Map(), mb = new Map(), mm = new Map();
    const addm = (m, k, v) => { const a = m.get(k) || [0, 0]; a[0]++; a[1] += v; m.set(k, a); };
    for (let i = 0; i < n; i++) { const o = i * 7; addm(tg, R[o + 2], R[o + 4]); addm(mb, R[o] * 100 + R[o + 3], R[o + 4]); addm(mm, R[o], R[o + 4]); }
    const mean = (m, k) => { const a = m.get(k); return a[1] / a[0]; };
    const agg = {}; const DB = ['≤−5', '−4..−2', '−1..+1', '+2..+4', '≥+5'];
    for (let i = 0; i < n; i++) { const o = i * 7, d = R[o + 5], db = d <= -5 ? '≤−5' : d <= -2 ? '−4..−2' : d <= 1 ? '−1..+1' : d <= 4 ? '+2..+4' : '≥+5';
      const ex = R[o + 4] - mean(tg, R[o + 2]) - mean(mb, R[o] * 100 + R[o + 3]) + mean(mm, R[o]);
      const kind = ELIM.has(MAPS[R[o]]) ? 'elim' : 'r500';
      acc(agg, (R[o + 1] ? 'W' : 'L') + '|' + kind + '|' + db, [1, ex, R[o + 4]]); }
    D.e2within = agg;
    P('## E2 split response within a team-game (two-way demeaned: team-game and map-bin), r20-299');
    tbl(['role', 'kind', 'own−opp units', 'n bins', 'excess splits/bin', 'raw splits/bin'], ['W', 'L'].flatMap(rl => ['r500', 'elim'].flatMap(kind => DB.map(db => { const a = agg[rl + '|' + kind + '|' + db]; return a ? [rl, kind, db, a[0], f2(a[1] / a[0]), f2(a[2] / a[0])] : null; }))).filter(Boolean));
  }
  P('## E3 per layout: winners units vs area / spawn tiles / fountains / capacity / observed flow; csplit target; ours');
  { const rows = [], X = [];
    const med = a => { if (!a.length) return NaN; const s = a.slice().sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
    for (const [ly, a] of Object.entries(A.layout).sort()) {
      const area = a.W * a.H, flow = a.flow / a.n, tgt = Math.max(8, Math.min(40, Math.floor(area / 45)));
      const o5 = A.oursUnits['cand-stack5-online|' + ly] || { u50: [], u100: [], u200: [] }, o6 = A.oursUnits['cand-stack6-online|' + ly] || { u50: [], u100: [], u200: [] };
      rows.push([ly, a.n, area, a.nSpawnT, a.nFount, f2(a.cap), f2(flow), med(a.u50), med(a.u100), med(a.u200), tgt, `${med(o5.u50)}/${med(o5.u100)}/${med(o5.u200)} (${o5.u50.length})`, `${med(o6.u50)}/${med(o6.u100)}/${med(o6.u200)} (${o6.u50.length})`]);
      X.push({ ly, area, sp: a.nSpawnT, fo: a.nFount, cap: a.cap, flow, u50: med(a.u50), u100: med(a.u100), u200: med(a.u200), elim: a.elim });
    }
    tbl(['layout', 'n W', 'W×H', 'spawn tiles', 'fountains', 'cap/round', 'nat spawned/round', 'W u50', 'W u100', 'W u200', 'csplit tgt', 'stack5 u50/100/200 (n)', 'stack6 u50/100/200 (n)'], rows);
    const corr = (xs, ys) => { const n = xs.length, mx = xs.reduce((s, v) => s + v, 0) / n, my = ys.reduce((s, v) => s + v, 0) / n; let c = 0, vx = 0, vy = 0; for (let i = 0; i < n; i++) { c += (xs[i] - mx) * (ys[i] - my); vx += (xs[i] - mx) ** 2; vy += (ys[i] - my) ** 2; } return c / Math.sqrt(vx * vy); };
    const preds = ['area', 'sp', 'fo', 'cap', 'flow'];
    const rows2 = []; for (const y of ['u50', 'u100', 'u200']) { const ok = X.filter(x => isFinite(x[y]) && x[y] > 0); rows2.push([y, ok.length, ...preds.map(p => { const r = corr(ok.map(x => Math.log(Math.max(0.5, x[p]))), ok.map(x => Math.log(x[y]))); return f2(r) + ' (R² ' + f2(r * r) + ')'; })]); }
    D.e3rows = X; D.e3corr = {}; for (const y of ['u50', 'u100', 'u200']) { const ok = X.filter(x => isFinite(x[y]) && x[y] > 0); D.e3corr[y] = {}; for (const p of preds) D.e3corr[y][p] = corr(ok.map(x => Math.log(Math.max(0.5, x[p]))), ok.map(x => Math.log(x[y]))); }
    D.e3ours = {}; for (const [k, o] of Object.entries(A.oursUnits)) D.e3ours[k] = { u50: med(o.u50), u100: med(o.u100), u200: med(o.u200), n: o.u50.length };
    P('log-log Pearson across layouts (winners median units):'); tbl(['units', 'layouts', 'area', 'spawn tiles', 'fountains', 'capacity', 'observed flow'], rows2);
    const rows3 = []; for (const x of X) rows3.push([x.ly, f2(x.u100 / x.area * 100), f2(x.u100 / x.cap), f2(x.u100 / x.flow), f2(x.u200 / x.cap)]);
    P('ratios:'); tbl(['layout', 'u100 per 100 tiles', 'u100 / capacity', 'u100 / observed flow', 'u200 / capacity'], rows3); }

  P('## E5 early natural pearls by territory (r0-99 and r0-49): per team-game');
  tbl(['role|kind', 'n', 'own', 'neutral', 'enemy', 'enemy share', 'r0-49 own/neu/enemy', 'r0-49 enemy share'], Object.entries(A.nat).sort().map(([k, a]) => { const n = a[0], s = a[1] + a[2] + a[3], s5 = a[4] + a[5] + a[6]; return [k, n, f1(a[1] / n), f1(a[2] / n), f1(a[3] / n), pc(a[3] / s), `${f1(a[4] / n)}/${f1(a[5] / n)}/${f1(a[6] / n)}`, pc(a[6] / s5)]; }));
  { const by = {}; for (const [kind, we, le, wa, la] of A.natGap) acc(by, kind, [1, we > le ? 1 : 0, we < le ? 1 : 0, we - le, wa - la]); D.e5gap = by;
    P('same game W - L (r0-99 enemy-territory natural pearls): ' + Object.entries(by).map(([k, a]) => `${k}: n${a[0]} W more ${pc(a[1] / a[0])}, L more ${pc(a[2] / a[0])}, mean diff ${f2(a[3] / a[0])}, total natural diff ${f2(a[4] / a[0])}`).join('; ')); P(''); }
  P('## E6 spawn capacity under own bodies (expected blocked attempts per team-game) by phase and territory; mirror-detected blocks');
  tbl(['role|kind', 'n', 'p0 own/neu/enemy', 'p1 own/neu/enemy', 'p2 own/neu/enemy', 'mirror blocks: our body on enemy / own / neutral', 'pearls blocking enemy / own terr', 'natural spawns enemy / own terr', 'enemy natural eaten'],
    Object.entries(A.occ).sort().map(([k, a]) => { const n = a[0]; return [k, n, `${f1(a[1] / n)}/${f1(a[2] / n)}/${f1(a[3] / n)}`, `${f1(a[4] / n)}/${f1(a[5] / n)}/${f1(a[6] / n)}`, `${f1(a[7] / n)}/${f1(a[8] / n)}/${f1(a[9] / n)}`, `${f1(a[10] / n)}/${f1(a[11] / n)}/${f1(a[12] / n)}`, `${f1(a[13] / n)}/${f1(a[14] / n)}`, `${f1(a[15] / n)}/${f1(a[16] / n)}`, f1(a[17] / n)]; }));
  P('same game: enemy-side capacity under bodies, winner vs loser: ' + Object.entries(A.sb).map(([k, a]) => `${k}: n${a[0]} W ${f1(a[1] / a[0])} L ${f1(a[2] / a[0])}`).join('; ')); P('');

  P('## E8 sacrifices (r>=200, not the king) by path distance to the king at death');
  P('columns: n, mean L, own20 share, opp20 share, eaten by (then) king 20R share, mean round');
  tbl(['role|kind|dK', 'n', 'L', 'own20', 'opp20', 'king20', 'round'], Object.entries(A.S).sort().map(([k, a]) => { const n = a[0]; return [k, n, f1(a[1] / n), pc(a[2] / a[7]), pc(a[3] / a[7]), pc(a[4] / a[7]), f1(a[5] / n)]; }));
  { // onset: sacrificers that approached their king (max dist in 60R before death >= dK + 5); slope of onset round on onset distance
    const reg = rows => { const n = rows.length; if (n < 5) return null; const mx = rows.reduce((s, r) => s + r[0], 0) / n, my = rows.reduce((s, r) => s + r[1], 0) / n; let c = 0, v = 0; for (const r of rows) { c += (r[0] - mx) * (r[1] - my); v += (r[0] - mx) ** 2; } return { n, slope: c / v, mx, my }; };
    for (const w of [1, 0]) {
      const R = A.Sonset.filter(s => s[0] === w && s[2] >= 0 && s[3] >= s[2] + 5 && s[4] >= 0);
      const g1 = reg(R.map(s => [s[3], s[4]])), g2 = reg(R.map(s => [s[3], s[1]]));
      D['e8onset' + (w ? 'W' : 'L')] = { n: R.length, s1: g1 && g1.slope, s2: g2 && g2.slope, byR: null };
      P(`E8 onset (${w ? 'W' : 'L'}, r500): approachers n=${R.length}; onset round on onset distance: slope ${g1 ? f2(g1.slope) : '–'} (mean dist ${g1 ? f1(g1.mx) : '–'}, mean onset r${g1 ? f1(g1.my) : '–'}); death round on onset distance: slope ${g2 ? f2(g2.slope) : '–'}`);
      const byD = {}; for (const s of R) { const b = s[3] <= 8 ? '5-8' : s[3] <= 12 ? '9-12' : s[3] <= 20 ? '13-20' : '21+'; acc(byD, b, [1, s[4], s[1], 500 - s[4]]); }
      P('   by onset distance: ' + Object.entries(byD).map(([b, a]) => `${b}: n${a[0]} onset r${f1(a[1] / a[0])} death r${f1(a[2] / a[0])} left-at-onset ${f1(a[3] / a[0])}`).join('; '));
      const all = A.Sonset.filter(s => s[0] === w);
      const byR = {}; for (const s of all) { const b = Math.floor(s[1] / 25) * 25; acc(byR, b, [1, s[2] >= 0 ? s[2] : 0, s[2] >= 0 && s[2] <= 3 ? 1 : 0]); }
      D['e8byR' + (w ? 'W' : 'L')] = byR;
      P('   all sacrifices by death round (25R): ' + Object.entries(byR).sort((a, b) => +a[0] - +b[0]).map(([b, a]) => `r${b}: n${a[0]} dK ${f1(a[1] / a[0])} ≤3 ${pc(a[2] / a[0])}`).join('; '));
    }
    P('');
    for (const w of [1, 0]) for (const cp of [300, 350]) {
      const R = A.E8near.filter(x => x[0] === w && x[1] === cp); const g = reg(R.map(x => [x[2], x[3]]));
      const by = {}; for (const x of R) { const b = x[2] <= 3 ? '≤3' : x[2] <= 8 ? '4-8' : x[2] <= 16 ? '9-16' : x[2] <= 32 ? '17-32' : '33+'; acc(by, b, [1, x[3], x[4]]); }
      D['e8near' + (w ? 'W' : 'L') + cp] = { n: R.length, slope: g && g.slope, by };
      P(`E8 king-directed sacrifices (dK<=3 at death, r500, ${w ? 'W' : 'L'}), by distance to the king at r${cp}: n=${R.length}, slope of death round on that distance ${g ? f2(g.slope) : '–'}; ` + ['≤3', '4-8', '9-16', '17-32', '33+'].filter(b => by[b]).map(b => `${b}: n${by[b][0]} death r${f1(by[b][1] / by[b][0])} L${f1(by[b][2] / by[b][0])}`).join('; '));
    }
    { // within-team: onset50 vs mean dK at r300
      const byT = {}; for (const x of A.E8tg) (byT[x[0]] = byT[x[0]] || []).push(x);
      const rows = []; for (const xs of Object.values(byT)) { if (xs.length < 5) continue; const mo = xs.reduce((q, x) => q + x[2], 0) / xs.length, md = xs.reduce((q, x) => q + x[3], 0) / xs.length; for (const x of xs) rows.push([x[3] - md, x[2] - mo]); }
      const g = reg(rows); const n = rows.length; let c = 0, vx = 0, vy = 0; for (const r of rows) { c += r[0] * r[1]; vx += r[0] * r[0]; vy += r[1] * r[1]; }
      D.e8tg = { n, slope: g && g.slope, r: c / Math.sqrt(vx * vy), tg: A.E8tg.length };
      P(`E8 team-game sacrifice onset50 vs mean dK of non-king dragons at r300 (r500 maps, within-team demeaned, teams with >= 5 team-games): n=${n}, slope ${g ? f2(g.slope) : '–'} rounds per tile, r=${f2(c / Math.sqrt(vx * vy))}; team-games ${A.E8tg.length}`);
      const all = A.E8tg; const byM = {}; for (const x of all) acc(byM, x[4], [1, x[2], x[3]]);
      P('   by map: ' + Object.entries(byM).map(([m, a]) => `${m}: n${a[0]} onset50 r${f1(a[1] / a[0])} mean dK300 ${f1(a[2] / a[0])}`).join('; '));
    }
    P('');
    P('## E8 checkpoints (r500 maps): non-king dragons alive at r300/r350 by dK, later sacrificed? mean sacrifice round');
    tbl(['role|cp|dK|L', 'n', 'sacrificed', 'mean sac round', 'died otherwise'], Object.entries(A.CP).sort().map(([k, a]) => [k, a[0], pc(a[1] / a[0]), a[1] ? f1(a[2] / a[1]) : '–', pc(a[3] / a[0])]));
    P('## E8 ours: sacrifices by set with tags (10 conv, 11 feed, 12 k2)');
    const by = {}; D.e8ours = by; for (const s of A.SoursRows) { const [set, r, L, dk, mx, mxR, tag, own20, opp20, k20] = s; acc(by, set + '|tag' + tag, [1, r, dk >= 0 ? dk : 0, L, own20, opp20, k20]); }
    tbl(['set|tag', 'n', 'mean round', 'dK', 'L', 'own20', 'opp20', 'king20'], Object.entries(by).sort().map(([k, a]) => [k, a[0], f1(a[1] / a[0]), f1(a[2] / a[0]), f1(a[3] / a[0]), f2(a[4] / a[0]), f2(a[5] / a[0]), f2(a[6] / a[0])]));
  }
  P('## E9 body kills by class (killer team role): n per class');
  { const tot = {}; for (const [k, a] of Object.entries(A.BK)) { const p = k.split('|'); const base = p.slice(0, -1).join('|'); acc(tot, base, [a[0]]); }
    tbl(['role|kind|class', 'n', 'share', 'victim L', 'owner L', 'owner king'], Object.entries(A.BK).sort().map(([k, a]) => { const base = k.split('|').slice(0, -1).join('|'); return [k, a[0], pc(a[0] / tot[base][0]), f1(a[1] / a[0]), f1(a[2] / a[0]), pc(a[3] / a[0])]; })); }
  P('## E9 chase episodes against this team (enemy chasers; defender perspective): per team-game');
  P('columns: n, episodes, sep, chaser died on the chased dragon body, on a third dragon of ours (rescue), head-on with the chased, head-on other, chaser other death, chased died, open at end, chase turns');
  tbl(['role|kind', 'n', 'episodes', 'sep', 'bkTarget', 'bkThird(rescue)', 'headOnTarget', 'headOnOther', 'chaserOther', 'chasedDied', 'open', 'turns'],
    Object.entries(A.CHdef).sort().map(([k, a]) => [k, a[0], ...a.slice(1).map(v => f1(v / a[0]))]));
  P('## E9 chase episodes (chaser team): per team-game');
  P('columns: n, episodes, sep, chaser died on target body, on third body, head-on with target, head-on other, chaser other death, target died, open at end, chase turns');
  tbl(['role|kind', 'n', 'episodes', 'sep', 'bkTarget', 'bkThird', 'headOnTarget', 'headOnOther', 'chaserOther', 'targetDied', 'open', 'turns'],
    Object.entries(A.CH).sort().map(([k, a]) => [k, a[0], ...a.slice(1).map(v => f1(v / a[0]))]));
  process.stdout.write(out.join('\n') + '\n');
  const dump = { ...A }; for (const k of ['rr', 'Sonset', 'E8near', 'natGap', 'SoursRows', 'E8tg']) delete dump[k];
  fs.writeFileSync(path.join(__dirname, 'acc.json'), JSON.stringify({ A: dump, D }));
}
main().catch(e => { console.error(e); process.exit(1); });
