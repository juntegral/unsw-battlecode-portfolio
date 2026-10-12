#!/usr/bin/env node
// Intake-gap aggregation and decomposition (research/observations/intake-gap.md). Reads .cache/intake-gap/*.jsonl only.
// usage: node exp/intake-gap/aggregate.js [--out exp/intake-gap/report.md] [--json .cache/intake-gap/numbers.json]
//
// Groups: our online sets by bot era (primary sample stack5-8 = W5..W9), top-vs-top winners (W) vs losers (L).
// The per-team-game gap is opponent natural intake minus ours (top: W minus L). All values are per team-game of the group.
//
// View A (pearl race identity, exact): every natural pearl that appeared (initial + spawned) has a race class at appearance
//   from our side (U = our nearest head strictly nearer, T = tie, O = theirs nearer; static path distance, bodies ignored)
//   and a fate (u we ate, o they ate, n uneaten at the end). With nu_U = (N_U^u - N_U^o)/N_U, nu_O = (N_O^o - N_O^u)/N_O:
//     gap = (N_O - N_U)(nu_O + nu_U)/2                     coverage (race share of the pearls that appeared)
//         + Nbar * 2 (l_U - l_O)                           contest: their steals of our-nearer pearls minus ours of theirs
//         + Nbar * (n_U - n_O)                             left uneaten (ours minus theirs)
//         + (N_T^o - N_T^u)                                ties
//   (l = share eaten by the farther team, n = share uneaten, Nbar = (N_U + N_O)/2). Computed per phase on pooled counts and summed.
// Supply layer: N_c = expected attempts A_c (capacity by race at each round start) - expected blocked B_c (bodies, natural pearls
//   by renewal, drops) + residual e_c. The coverage term splits into attempts (A_O - A_U), blocked (B_U - B_O by blocker) and the
//   residual, each valued at (nu_O + nu_U)/2.
// Heads vs placement: the attempt race share s = A_U / (A_U + A_O) against the head share h = H_U / (H_U + H_O) (head-rounds of
//   the phase). The reference curve f(h) (per map and phase; family fallback) is fitted on top-vs-top team-games; per game
//   and phase the predicted A_U = (A_U + A_O) f(h). Heads term = (Apred_O - Apred_U) nubar, placement = 2 (Apred_U - A_U) nubar.
// View B (production): intake = head-rounds x pearls per head-round, Shapley per phase: (H_O - H_U) rbar + Hbar (r_O - r_U).
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const CACHE = path.join(ROOT, '.cache', 'intake-gap');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const OUT = path.resolve(ROOT, opt('out', 'exp/intake-gap/report.md')), JOUT = path.resolve(ROOT, opt('json', '.cache/intake-gap/numbers.json'));
const NPH = 6, NB = 50;
const PHN = ['r0–49', 'r50–99', 'r100–249', 'r250–349', 'r350–449', 'r450+'];
const PHB = [[0, 5], [5, 10], [10, 25], [25, 35], [35, 45], [45, 50]]; // 10-round bins of each phase
const LCN = ['2', '3', '4', '5–7', '8–14', '15+'];
const KINDS = ['plain', 'g', 'F', 'cov', 'cl', 'grab', 'esc', 'noexit', 'escsplit', 'feed', 'split', 'trade', 'lsplit', 'csplit', 'other'];
const ORIGS = ['csplit', 'lsplit', 'floor', 'kcap', 'frag', 'bsplit', 'split', 'escsplit', 'escsplit2', 'unl'];
const GROUPS = {
  'merge2': ['cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3'],
  'stack1-4': ['cand-stack1-online', 'cand-stack2-online', 'cand-stack3-online', 'cand-stack4-online'],
  'stack5-8': ['cand-stack5-online', 'cand-stack6-online', 'cand-stack6-online-r2', 'cand-stack7-online', 'cand-stack8-online'],
  'stack9': ['cand-stack9-online'],
  'g4r4': ['baseline-r1', 'baseline-r1b', 'baseline-r1c', 'cand-avoid6-online', 'cand-portal1-online'],
  'swarm8': ['cand-swarm8-online'],
  'px': ['base-px8-online', 'base-px9d-online', 'px-king-v2-online'],
};
const SETS = Object.values(GROUPS).flat();
const MAPS = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma', 'Default', 'Devil', 'Prisoners Dilemma', 'Queen Of Spades', 'Trophy'];
const R500 = new Set(['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma']);

const readLines = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => JSON.parse(l)) : [];

// ---------------------------------------------------------------------------------------------------------------
// one team-game view: everything from the team's side (me = 0/1), opponent = 1 - me
function teamView(g, me) {
  const op = 1 - me, T = me ? 'B' : 'A', O = me ? 'A' : 'B';
  const flipR3 = r3 => me ? 2 - r3 : r3;              // A-perspective race3 (0 A nearer) -> mine (0 me nearer)
  const flipTerr = t => t === 0 ? 0 : (me ? 3 - t : t); // 1 = my territory
  const flipFate = f => f === 2 ? 2 : (me ? 1 - f : f); // 0 = me
  const flipCls = c => c === 8 ? 8 : (me ? 6 - c : c);
  const v = { g, me, rounds: g.rounds, map: g.map, kind: g.kind, variant: g.variant };
  // race counts [ph][r3][fate], by class [ph][cls][fate], by terr, fountain, vision
  v.race = [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 0, 0]));
  v.cls = [...Array(NPH)].map(() => [...Array(9)].map(() => [0, 0, 0]));
  v.raceT = [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 1, 2].map(() => [0, 0, 0]))); // [ph][terr][r3][fate]
  v.raceF = [...Array(NPH)].map(() => [0, 1].map(() => [0, 1, 2].map(() => [0, 0, 0])));   // [ph][fount][r3][fate]
  v.raceV = [...Array(NPH)].map(() => [0, 1, 2, 3].map(() => [0, 1, 2].map(() => [0, 0, 0]))); // [ph][visMask(me bit0, op bit1)][r3][fate]
  v.clsD = {}; // contest: our-nearer pearls by class x vision -> fate
  for (const [k, n] of Object.entries(g.RACE)) {
    const [ph, terr, f, cls, vis, fate] = k.split('|').map(Number);
    const c = flipCls(cls), r3 = c === 8 ? 1 : c <= 2 ? 2 : c === 3 ? 1 : 0, fa = flipFate(fate), t = flipTerr(terr);
    const vm = me ? ((vis >> 1) & 1) | ((vis & 1) << 1) : vis;
    v.race[ph][r3][fa] += n; v.cls[ph][c][fa] += n; v.raceT[ph][t][r3][fa] += n; v.raceF[ph][f][r3][fa] += n; v.raceV[ph][vm][r3][fa] += n;
  }
  v.near = {}; // "ph|r3|myLcs|opLcs|fate"
  for (const [k, n] of Object.entries(g.NEAR)) {
    const [ph, r3, lA, lB, fate] = k.split('|').map(Number);
    const kk = ph + '|' + flipR3(r3) + '|' + (me ? lB : lA) + '|' + (me ? lA : lB) + '|' + flipFate(fate);
    v.near[kk] = (v.near[kk] || 0) + n;
  }
  v.del = {}; for (const [k, a] of Object.entries(g.DEL)) { const [ph, r3, fate] = k.split('|').map(Number); const kk = ph + '|' + flipR3(r3) + '|' + flipFate(fate); const b = v.del[kk] || (v.del[kk] = [0, 0]); b[0] += a[0]; b[1] += a[1]; }
  // attempts by phase x terr x r3
  v.att = [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 0, 0]));
  for (let b = 0; b < NB; b++) { const ph = PHB.findIndex(p => b >= p[0] && b < p[1]); for (let t = 0; t < 3; t++) for (let r = 0; r < 3; r++) v.att[ph][flipTerr(t)][flipR3(r)] += g.CAPR[(b * 3 + t) * 3 + r]; }
  v.attF = [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 0, 0]));
  for (let ph = 0; ph < NPH; ph++) for (let t = 0; t < 3; t++) for (let r = 0; r < 3; r++) v.attF[ph][flipTerr(t)][flipR3(r)] += g.CAPRF[(ph * 3 + t) * 3 + r];
  // blocked: bodies [whose 0 me 1 op][ph][terr][r3][f], natural pearls [ph][terr][r3][fate], drops [ph][terr][r3], mirror [ph][blk][terr][r3]
  v.ob = [0, 1].map(() => [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 1, 2].map(() => [0, 0]))));
  for (let tm = 0; tm < 2; tm++) for (let ph = 0; ph < NPH; ph++) for (let t = 0; t < 3; t++) for (let r = 0; r < 3; r++) for (let f = 0; f < 2; f++)
    v.ob[tm === me ? 0 : 1][ph][flipTerr(t)][flipR3(r)][f] += g.OB[((((tm * NPH + ph) * 3 + t) * 3 + r) * 2) + f];
  v.pb = [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 1, 2].map(() => [0, 0, 0])));
  for (let ph = 0; ph < NPH; ph++) for (let t = 0; t < 3; t++) for (let r = 0; r < 3; r++) for (let fa = 0; fa < 3; fa++) v.pb[ph][flipTerr(t)][flipR3(r)][flipFate(fa)] += g.PB[((ph * 3 + t) * 3 + r) * 3 + fa];
  v.pbr = [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 0, 0]));
  if (g.PBR) for (let ph = 0; ph < NPH; ph++) for (let t = 0; t < 3; t++) for (let r = 0; r < 3; r++) v.pbr[ph][flipTerr(t)][flipR3(r)] += g.PBR[(ph * 3 + t) * 3 + r];
  v.steal = [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 1].map(() => [0, 0, 0]))); // [ph][r3 mine][eater 0 me 1 op][lcs]
  if (g.STEAL) for (let ph = 0; ph < NPH; ph++) for (let r = 0; r < 3; r++) for (let e = 0; e < 2; e++) for (let l = 0; l < 3; l++) v.steal[ph][flipR3(r)][e === me ? 0 : 1][l] += g.STEAL[((ph * 3 + r) * 2 + e) * 3 + l];
  v.db = [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 0, 0]));
  for (let ph = 0; ph < NPH; ph++) for (let t = 0; t < 3; t++) for (let r = 0; r < 3; r++) v.db[ph][flipTerr(t)][flipR3(r)] += g.DB[(ph * 3 + t) * 3 + r];
  v.sbm = [...Array(NPH)].map(() => [0, 1, 2, 3, 4].map(() => [0, 1, 2].map(() => [0, 0, 0])));
  for (let ph = 0; ph < NPH; ph++) for (let bl = 0; bl < 5; bl++) for (let t = 0; t < 3; t++) for (let r = 0; r < 3; r++) {
    const b2 = bl <= 1 ? (bl === me ? 0 : 1) : bl; v.sbm[ph][b2][flipTerr(t)][flipR3(r)] += g.SBM[((ph * 5 + bl) * 3 + t) * 3 + r];
  }
  // heads and eats
  const ph10 = b => PHB.findIndex(p => b >= p[0] && b < p[1]);
  v.hr = [me, op].map(t => [...Array(NPH)].map((_, ph) => { let s = 0; for (let lc = 0; lc < 6; lc++) for (let b = PHB[ph][0]; b < PHB[ph][1]; b++) s += g.HR[t][lc][b]; return s; }));
  v.hrLc = [me, op].map(t => [...Array(NPH)].map((_, ph) => [0, 1, 2, 3, 4, 5].map(lc => { let s = 0; for (let b = PHB[ph][0]; b < PHB[ph][1]; b++) s += g.HR[t][lc][b]; return s; })));
  v.hrT = [me, op].map(t => [...Array(NPH)].map((_, ph) => [0, 1, 2].map(r => { let s = 0; for (let b = PHB[ph][0]; b < PHB[ph][1]; b++) s += g.HRT[t][r][b]; return s; })));
  v.hrP = [me, op].map(t => [...Array(NPH)].map((_, ph) => [0, 1, 2].map(lcs => [0, 1, 2, 3].map(dnp => g.HRP[t][(lcs * 4 + dnp) * NPH + ph]))));
  v.eat = [me, op].map(t => [...Array(NPH)].map((_, ph) => [0, 1, 2, 3, 4, 5].map(lc => [0, 1, 2].map(r => { let s = 0; for (let b = PHB[ph][0]; b < PHB[ph][1]; b++) s += g.EAT[t][lc][r][b]; return s; }))));
  v.nat = [T, O].map(x => [...Array(NPH)].map((_, ph) => { let s = 0; for (let b = PHB[ph][0]; b < PHB[ph][1]; b++) s += g[x].eatNat[b]; return s; }));
  v.drop = [T, O].map(x => g[x].eatDrop.reduce((s, y) => s + y, 0));
  v.spr = [T, O].map(x => g[x].spr.reduce((s, y) => s + y, 0));
  v.sprN = [T, O].map(x => g[x].sprN.reduce((s, y) => s + y, 0));
  v.turns = [me, op].map(t => g.TURNS[t].reduce((s, y) => s + y, 0));
  v.steps = [me, op].map(t => g.STEPS[t].reduce((s, y) => s + y, 0));
  v.turnsPh = [me, op].map(t => [...Array(NPH)].map((_, ph) => { let s = 0; for (let b = PHB[ph][0]; b < PHB[ph][1]; b++) s += g.TURNS[t][b]; return s; }));
  v.stepsPh = [me, op].map(t => [...Array(NPH)].map((_, ph) => { let s = 0; for (let b = PHB[ph][0]; b < PHB[ph][1]; b++) s += g.STEPS[t][b]; return s; }));
  v.units = [T, O].map(x => g[x].units); v.king = [T, O].map(x => g[x].king); v.total = [T, O].map(x => g[x].total);
  // head dynamics: births = splits in the bin; deaths = births - (units after - units before) (units before rounds 0, 10, ..., 500)
  v.birthPh = [T, O].map(x => [...Array(NPH)].map((_, ph) => { let s = 0; for (let b = PHB[ph][0]; b < PHB[ph][1]; b++) s += g[x].splitN[b]; return s; }));
  v.deathPh = [T, O].map(x => [...Array(NPH)].map((_, ph) => { let s = 0; for (let b = PHB[ph][0]; b < PHB[ph][1]; b++) s += g[x].splitN[b] - ((g[x].units[b + 1] || 0) - (g[x].units[b] || 0)); return s; }));
  v.act = g.ACT; v.acte = g.ACTE; v.org = g.ORG; v.orge = g.ORGE; v.orghr = g.ORGHR;
  v.elim = g.endReason === 'teamEliminated' ? 1 : 0;
  v.win = g.winner === (me ? 'B' : 'A') ? 1 : g.winner ? 0 : 0.5;
  v.natStart = g.natStart; v.spawned = g.natSpawned;
  return v;
}

// ---------------------------------------------------------------------------------------------------------------
// pooled accumulator of team-game views
function newAcc() {
  return { n: 0, rounds: 0, elim: 0, win: 0,
    race: [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 0, 0])), cls: [...Array(NPH)].map(() => [...Array(9)].map(() => [0, 0, 0])),
    raceT: [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 1, 2].map(() => [0, 0, 0]))), raceF: [...Array(NPH)].map(() => [0, 1].map(() => [0, 1, 2].map(() => [0, 0, 0]))),
    raceV: [...Array(NPH)].map(() => [0, 1, 2, 3].map(() => [0, 1, 2].map(() => [0, 0, 0]))), near: {}, del: {},
    att: [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 0, 0])), attF: [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 0, 0])),
    attPred: [...Array(NPH)].map(() => [0, 0]), // predicted attempts near me / near them from the head-share curve (ties excluded)
    ob: [0, 1].map(() => [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 1, 2].map(() => [0, 0])))), pb: [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 1, 2].map(() => [0, 0, 0]))),
    pbr: [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 0, 0])), steal: [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 1].map(() => [0, 0, 0]))),
    db: [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 0, 0])), sbm: [...Array(NPH)].map(() => [0, 1, 2, 3, 4].map(() => [0, 1, 2].map(() => [0, 0, 0]))),
    hr: [0, 1].map(() => new Array(NPH).fill(0)), hrLc: [0, 1].map(() => [...Array(NPH)].map(() => new Array(6).fill(0))), hrT: [0, 1].map(() => [...Array(NPH)].map(() => [0, 0, 0])),
    hrP: [0, 1].map(() => [...Array(NPH)].map(() => [0, 1, 2].map(() => [0, 0, 0, 0]))),
    eat: [0, 1].map(() => [...Array(NPH)].map(() => [0, 1, 2, 3, 4, 5].map(() => [0, 0, 0]))), nat: [0, 1].map(() => new Array(NPH).fill(0)),
    drop: [0, 0], spr: [0, 0], sprN: [0, 0], turns: [0, 0], steps: [0, 0], turnsPh: [0, 1].map(() => new Array(NPH).fill(0)), stepsPh: [0, 1].map(() => new Array(NPH).fill(0)),
    unitsAt: [0, 1].map(() => new Array(51).fill(0)), kingAt: [0, 1].map(() => new Array(51).fill(0)), totalAt: [0, 1].map(() => new Array(51).fill(0)),
    act: new Array(KINDS.length * NB).fill(0), acte: new Array(KINDS.length * NB).fill(0), org: new Array(ORIGS.length * NB).fill(0), orge: new Array(ORIGS.length * NB).fill(0), orghr: new Array(ORIGS.length * NB).fill(0), hasAct: 0,
    appeared: 0, spawned: 0, birthPh: [0, 1].map(() => new Array(NPH).fill(0)), deathPh: [0, 1].map(() => new Array(NPH).fill(0)),
  };
}
const addDeep = (a, b) => { if (Array.isArray(a)) { for (let i = 0; i < a.length; i++) { if (Array.isArray(a[i])) addDeep(a[i], b[i]); else a[i] += b[i] || 0; } } };
function addView(A, v, curve) {
  A.n++; A.rounds += v.rounds; A.elim += v.elim; A.win += v.win;
  for (const k of ['birthPh', 'deathPh', 'race', 'cls', 'raceT', 'raceF', 'raceV', 'att', 'attF', 'ob', 'pb', 'pbr', 'steal', 'db', 'sbm', 'hr', 'hrLc', 'hrT', 'hrP', 'eat', 'nat', 'turnsPh', 'stepsPh']) addDeep(A[k], v[k]);
  for (const k of ['drop', 'spr', 'sprN', 'turns', 'steps']) { A[k][0] += v[k][0]; A[k][1] += v[k][1]; }
  for (const [k, n] of Object.entries(v.near)) A.near[k] = (A.near[k] || 0) + n;
  for (const [k, a] of Object.entries(v.del)) { const b = A.del[k] || (A.del[k] = [0, 0]); b[0] += a[0]; b[1] += a[1]; }
  for (let t = 0; t < 2; t++) for (let i = 0; i <= 50; i++) { A.unitsAt[t][i] += v.units[t][i] || 0; A.kingAt[t][i] += v.king[t][i] || 0; A.totalAt[t][i] += v.total[t][i] || 0; }
  if (v.act) { A.hasAct++; addDeep(A.act, v.act); addDeep(A.acte, v.acte); addDeep(A.org, v.org); addDeep(A.orge, v.orge); addDeep(A.orghr, v.orghr); }
  A.appeared += v.natStart + v.spawned; A.spawned += v.spawned;
  if (curve) for (let ph = 0; ph < NPH; ph++) {
    const aU = v.att[ph][0][0] + v.att[ph][1][0] + v.att[ph][2][0], aO = v.att[ph][0][2] + v.att[ph][1][2] + v.att[ph][2][2];
    const hU = v.hr[0][ph], hO = v.hr[1][ph];
    if (!(hU + hO > 0) || !(aU + aO > 0)) { A.attPred[ph][0] += aU; A.attPred[ph][1] += aO; continue; }
    const s = curve(v.map, ph, hU / (hU + hO));
    A.attPred[ph][0] += (aU + aO) * s; A.attPred[ph][1] += (aU + aO) * (1 - s);
  }
}

// ---------------------------------------------------------------------------------------------------------------
// head-share -> attempt race share reference curve (top-vs-top team-games, both sides)
const HBIN = h => Math.min(19, Math.floor(h * 20));
function buildCurve(topViews) {
  const byMap = {}, byFam = {};
  const put = (tab, key, ph, h, aU, aO) => { const t = tab[key] || (tab[key] = [...Array(NPH)].map(() => [...Array(20)].map(() => [0, 0, 0]))); const c = t[ph][HBIN(h)]; c[0] += aU; c[1] += aU + aO; c[2]++; };
  for (const v of topViews) for (let ph = 0; ph < NPH; ph++) {
    const aU = v.att[ph][0][0] + v.att[ph][1][0] + v.att[ph][2][0], aO = v.att[ph][0][2] + v.att[ph][1][2] + v.att[ph][2][2];
    const hU = v.hr[0][ph], hO = v.hr[1][ph]; if (!(hU + hO > 0) || !(aU + aO > 0)) continue;
    const h = hU / (hU + hO);
    put(byMap, v.map, ph, h, aU, aO); put(byFam, R500.has(v.map) ? 'r500' : 'elim', ph, h, aU, aO);
  }
  const look = (tab, key, ph, h) => {
    const t = tab[key]; if (!t) return null;
    const MINN = 20; // team-games per bin
    const b = HBIN(h), c = t[ph][b]; if (c[2] >= MINN) return c[0] / c[1];
    // nearest populated bins on both sides, linear interpolation
    let lo = b - 1, hi = b + 1; while (lo >= 0 && !(t[ph][lo][2] >= MINN)) lo--; while (hi < 20 && !(t[ph][hi][2] >= MINN)) hi++;
    const val = i => t[ph][i][0] / t[ph][i][1], mid = i => (i + 0.5) / 20;
    if (lo >= 0 && hi < 20) { const w = (h - mid(lo)) / (mid(hi) - mid(lo)); return val(lo) + w * (val(hi) - val(lo)); }
    if (lo >= 0) return val(lo); if (hi < 20) return val(hi); return null;
  };
  const curve = (map, ph, h) => { const x = look(byMap, map, ph, h); if (x !== null) return x; const y = look(byFam, R500.has(map) ? 'r500' : 'elim', ph, h); return y !== null ? y : h; };
  return { curve, byMap, byFam };
}

// ---------------------------------------------------------------------------------------------------------------
// decomposition of one pooled accumulator (per team-game)
function decompose(A) {
  const n = A.n || 1, out = { n: A.n, byPh: [], tot: {} };
  const keys = ['Iu', 'Io', 'gap', 'cov', 'covAtt', 'covHeads', 'covPlace', 'covBlkBodyMe', 'covBlkBodyOp', 'covBlkNat', 'covBlkDrop', 'covResid', 'contest', 'uneaten', 'ties', 'NU', 'NO', 'NT', 'nuU', 'nuO', 'lU', 'lO', 'nU', 'nO', 'cU', 'cO', 'AU', 'AO', 'AT', 'check',
    'dRace', 'dSteal', 'dUneat', 'dTies', 'dCap', 'dCapHeads', 'dCapPlace', 'dBlkMe', 'dBlkOp', 'dBlkNat', 'dBlkDrop', 'dResid', 'stolenFromUs', 'stolenByUs', 'uneatU', 'uneatO', 'pU', 'pO', 'dCheck'];
  for (const k of keys) out.tot[k] = 0;
  for (let ph = 0; ph < NPH; ph++) {
    const r = A.race[ph], U = r[0], T = r[1], O = r[2];
    const NU = U[0] + U[1] + U[2], NT = T[0] + T[1] + T[2], NO = O[0] + O[1] + O[2];
    const Iu = U[0] + T[0] + O[0], Io = U[1] + T[1] + O[1];
    const nuU = NU ? (U[0] - U[1]) / NU : 0, nuO = NO ? (O[1] - O[0]) / NO : 0, nubar = (nuU + nuO) / 2, Nbar = (NU + NO) / 2;
    const lU = NU ? U[1] / NU : 0, lO = NO ? O[0] / NO : 0, nU = NU ? U[2] / NU : 0, nO = NO ? O[2] / NO : 0;
    const cov = (NO - NU) * nubar, contest = Nbar * 2 * (lU - lO), uneaten = Nbar * (nU - nO), ties = T[1] - T[0];
    // supply layer
    const att = A.att[ph], AU = att[0][0] + att[1][0] + att[2][0], AT = att[0][1] + att[1][1] + att[2][1], AO = att[0][2] + att[1][2] + att[2][2];
    const sumR = (arr, r3) => arr[0][r3] + arr[1][r3] + arr[2][r3];
    const obMe = [0, 1, 2].map(r3 => [0, 1, 2].reduce((s, t) => s + A.ob[0][ph][t][r3][0] + A.ob[0][ph][t][r3][1], 0));
    const obOp = [0, 1, 2].map(r3 => [0, 1, 2].reduce((s, t) => s + A.ob[1][ph][t][r3][0] + A.ob[1][ph][t][r3][1], 0));
    const pbR = [0, 1, 2].map(r3 => sumR(A.pbr[ph], r3)); // natural pearls blocking in this phase (renewal density), race of the tile now
    const dbR = [0, 1, 2].map(r3 => sumR(A.db[ph], r3));
    // multiplicative supply layer: N_c ~ A_c * o_c (o = open fraction = 1 - blocked / attempts), Shapley over (A, o):
    //   N_O - N_U ~ (A_O - A_U) * obar  [capacity Voronoi]  +  Abar * (o_O - o_U)  [blocking asymmetry, split by blocker type]
    const BU = obMe[0] + obOp[0] + pbR[0] + dbR[0], BO = obMe[2] + obOp[2] + pbR[2] + dbR[2];
    const oU = AU > 0 ? Math.max(0, (AU - BU) / AU) : 0, oO = AO > 0 ? Math.max(0, (AO - BO) / AO) : 0, obar = (oU + oO) / 2, Abar = (AU + AO) / 2;
    const covAtt = (AO - AU) * obar * nubar;
    const bshare = (bU, bO) => Abar * ((AU > 0 ? bU / AU : 0) - (AO > 0 ? bO / AO : 0)) * nubar; // positive = our side more blocked
    const covBlkBodyMe = bshare(obMe[0], obMe[2]), covBlkBodyOp = bshare(obOp[0], obOp[2]), covBlkNat = bshare(pbR[0], pbR[2]), covBlkDrop = bshare(dbR[0], dbR[2]);
    const covResid = cov - covAtt - covBlkBodyMe - covBlkBodyOp - covBlkNat - covBlkDrop;
    const pU = A.attPred[ph][0], pO = A.attPred[ph][1];
    const covHeads = (pO - pU) * obar * nubar, covPlace = covAtt - covHeads;
    const row = { ph: PHN[ph], Iu: Iu / n, Io: Io / n, gap: (Io - Iu) / n, cov: cov / n, covAtt: covAtt / n, covHeads: covHeads / n, covPlace: covPlace / n,
      covBlkBodyMe: covBlkBodyMe / n, covBlkBodyOp: covBlkBodyOp / n, covBlkNat: covBlkNat / n, covBlkDrop: covBlkDrop / n, covResid: covResid / n,
      contest: contest / n, uneaten: uneaten / n, ties: ties / n, NU: NU / n, NO: NO / n, NT: NT / n, nuU, nuO, lU, lO, nU, nO, cU: NU ? U[0] / NU : 0, cO: NO ? O[1] / NO : 0,
      AU: AU / n, AO: AO / n, AT: AT / n, oU, oO, bU: [obMe[0], obOp[0], pbR[0], dbR[0]].map(x => x / n), bO: [obMe[2], obOp[2], pbR[2], dbR[2]].map(x => x / n) };
    row.check = row.gap - (row.cov + row.contest + row.uneaten + row.ties);
    // direct-count identity (no interaction term): gap = (N_O - N_U) + 2 (stolen from us - stolen by us) - (their uneaten - ours) + ties
    //   race = N_O - N_U, split with the capacity model into capacity share (A_O - A_U) * obar, openness Abar * (o_O - o_U) by blocker,
    //   and the model residual; the capacity share into heads (reference curve) and placement.
    const dRace = NO - NU, dSteal = 2 * (U[1] - O[0]), dUneat = -(O[2] - U[2]), dTies = T[1] - T[0];
    const dCap = (AO - AU) * obar, dCapHeads = (pO - pU) * obar, dCapPlace = dCap - dCapHeads;
    const opn = (bU, bO) => Abar * ((AU > 0 ? bU / AU : 0) - (AO > 0 ? bO / AO : 0));
    const dBlkMe = opn(obMe[0], obMe[2]), dBlkOp = opn(obOp[0], obOp[2]), dBlkNat = opn(pbR[0], pbR[2]), dBlkDrop = opn(dbR[0], dbR[2]);
    const dResid = dRace - dCap - dBlkMe - dBlkOp - dBlkNat - dBlkDrop;
    Object.assign(row, { dRace: dRace / n, dSteal: dSteal / n, dUneat: dUneat / n, dTies: dTies / n, dCap: dCap / n, dCapHeads: dCapHeads / n, dCapPlace: dCapPlace / n,
      dBlkMe: dBlkMe / n, dBlkOp: dBlkOp / n, dBlkNat: dBlkNat / n, dBlkDrop: dBlkDrop / n, dResid: dResid / n, stolenFromUs: U[1] / n, stolenByUs: O[0] / n, uneatU: U[2] / n, uneatO: O[2] / n,
      pU: pU / n, pO: pO / n, obar });
    row.dCheck = row.gap - (row.dRace + row.dSteal + row.dUneat + row.dTies);
    out.byPh.push(row);
    for (const k of keys) if (!['nuU', 'nuO', 'lU', 'lO', 'nU', 'nO', 'cU', 'cO'].includes(k)) out.tot[k] += row[k];
    out.tot.bU = (out.tot.bU || [0, 0, 0, 0]).map((x, i) => x + row.bU[i]); out.tot.bO = (out.tot.bO || [0, 0, 0, 0]).map((x, i) => x + row.bO[i]);
  }
  // pooled rates over all phases (for the text)
  const all = [0, 1, 2].map(r3 => [0, 1, 2].map(f => A.race.reduce((s, p) => s + p[r3][f], 0)));
  const NU = all[0][0] + all[0][1] + all[0][2], NO = all[2][0] + all[2][1] + all[2][2], NT = all[1][0] + all[1][1] + all[1][2];
  Object.assign(out.tot, { cU: all[0][0] / NU, lU: all[0][1] / NU, nU: all[0][2] / NU, cO: all[2][1] / NO, lO: all[2][0] / NO, nO: all[2][2] / NO,
    shareU: NU / (NU + NO + NT), shareO: NO / (NU + NO + NT) });
  return out;
}
// View B: heads x rate (per phase Shapley), plus length-class mix split of the rate term
function viewB(A) {
  const n = A.n || 1, rows = []; let tot = { heads: 0, rate: 0, mix: 0, within: 0, gap: 0 };
  for (let ph = 0; ph < NPH; ph++) {
    const HU = A.hr[0][ph], HO = A.hr[1][ph];
    const IU = A.eat[0][ph].reduce((s, a) => s + a[0] + a[1] + a[2], 0), IO = A.eat[1][ph].reduce((s, a) => s + a[0] + a[1] + a[2], 0);
    const rU = HU ? IU / HU : 0, rO = HO ? IO / HO : 0;
    const heads = (HO - HU) * (rU + rO) / 2, rate = (HO + HU) / 2 * (rO - rU);
    // rate difference = sum_lc (m_O - m_U) rbar_lc + mbar_lc (r_O,lc - r_U,lc)
    let mix = 0, within = 0;
    for (let lc = 0; lc < 6; lc++) {
      const hu = A.hrLc[0][ph][lc], ho = A.hrLc[1][ph][lc];
      const eu = A.eat[0][ph][lc].reduce((s, x) => s + x, 0), eo = A.eat[1][ph][lc].reduce((s, x) => s + x, 0);
      const mu = HU ? hu / HU : 0, mo = HO ? ho / HO : 0, ru = hu ? eu / hu : 0, ro = ho ? eo / ho : 0;
      const rbar = hu && ho ? (ru + ro) / 2 : (hu ? ru : ro);
      mix += (mo - mu) * rbar; within += (mu + mo) / 2 * (ro - ru);
    }
    const scale = (HO + HU) / 2; // rate term = scale * (rO - rU) = scale * (mix + within) (up to lc classes where one side has no head-rounds)
    const row = { ph: PHN[ph], HU: HU / n, HO: HO / n, rU: rU * 10, rO: rO * 10, IU: IU / n, IO: IO / n, heads: heads / n, rate: rate / n, mix: scale * mix / n, within: scale * within / n, gap: (IO - IU) / n };
    rows.push(row); tot.heads += row.heads; tot.rate += row.rate; tot.mix += row.mix; tot.within += row.within; tot.gap += row.gap;
  }
  return { rows, tot };
}

// ---------------------------------------------------------------------------------------------------------------
function main() {
  const games = { online: [], top: [] };
  for (const s of SETS) for (const g of readLines(path.join(CACHE, 'online-' + s + '.jsonl'))) games.online.push(g);
  const topRaw = []; for (const f of fs.readdirSync(CACHE).filter(f => /^top.*\.jsonl$/.test(f))) for (const g of readLines(path.join(CACHE, f))) topRaw.push(g);
  // exclusion (as exp/mass-analysis/report.js and the earlier studies): a stalled team (splits <= 3 and sonar 0) or >= 3 timeouts; draws
  let exStall = 0, exDraw = 0;
  for (const g of topRaw) {
    const stalled = [0, 1].some(t => (g[t ? 'B' : 'A'].splits <= 3 && g.sonar[t] === 0)) || g.A.faults >= 3 || g.B.faults >= 3;
    if (stalled) { exStall++; continue; }
    if (!g.winner) { exDraw++; continue; }
    games.top.push(g);
  }
  const chkSum = {}; for (const g of [...games.online, ...topRaw]) for (const s of ['chk', 'chkX', 'chkR']) for (const [k, v] of Object.entries(g[s] || {})) { if (k === 'liveLeft') continue; chkSum[s + '.' + k] = (chkSum[s + '.' + k] || 0) + Math.abs(v || 0); }

  // reference curve from top W and L views
  const topViews = []; for (const g of games.top) { topViews.push(teamView(g, 0)); topViews.push(teamView(g, 1)); }
  const CUR = buildCurve(topViews);

  const acc = {};
  const get = k => acc[k] || (acc[k] = newAcc());
  // online: our side (me) vs the opponent, by group x family, group x map, group x map x variant, set x family
  const setGroup = {}; for (const [gname, sets] of Object.entries(GROUPS)) for (const s of sets) setGroup[s] = gname;
  for (const g of games.online) {
    const me = g.us === 'B' ? 1 : 0, v = teamView(g, me), fam = g.kind, gr = setGroup[g.set];
    for (const k of [gr + '|' + fam, gr + '|all', gr + '|map|' + g.map, gr + '|mapv|' + g.map + '/' + g.variant, 'set|' + g.set + '|' + fam, gr + '|opp|' + (g.opp || g.oppId) + '|' + fam]) addView(get(k), v, CUR.curve);
    if (/stack[5-8]/.test(g.set)) addView(get('stack5-8w|' + fam), v, CUR.curve);
  }
  // top: winner side vs loser side
  for (const g of games.top) {
    const w = g.winner === 'B' ? 1 : 0, vW = teamView(g, w), vL = teamView(g, 1 - w), fam = g.kind;
    // "me" = the loser, so gap = W - L (like ours: opponent minus us)
    addView(get('topL|' + fam), vL, CUR.curve); addView(get('topL|map|' + g.map), vL, CUR.curve); addView(get('topL|mapv|' + g.map + '/' + g.variant), vL, CUR.curve);
    addView(get('topW|' + fam), vW, CUR.curve);
  }
  const perGame = [];
  for (const g of games.online) {
    const me = g.us === 'B' ? 1 : 0, v = teamView(g, me), A1 = newAcc(); addView(A1, v, null); const d = decompose(A1).tot;
    const r = [0, 1, 2].map(r3 => [0, 1, 2].map(f => v.race.reduce((s2, p) => s2 + p[r3][f], 0)));
    perGame.push({ key: g.key, set: g.set, map: g.map, variant: g.variant, kind: g.kind, opp: g.opp, rounds: g.rounds, Iu: d.Iu, Io: d.Io, gap: d.gap, cov: d.cov, contest: d.contest, uneaten: d.uneaten,
      lostU: r[0][1], stoleO: r[2][0], NU: r[0][0] + r[0][1] + r[0][2], NO: r[2][0] + r[2][1] + r[2][2], units100: v.units[0][10], oppUnits100: v.units[1][10] });
  }
  const curveFam = {}; for (const [fam, t] of Object.entries(CUR.byFam)) curveFam[fam] = t.map(ph => ph.map(c => c[2] ? [+(c[0] / c[1]).toFixed(3), c[2]] : null));
  const res = { generated: new Date().toISOString(), N: { online: games.online.length, topRaw: topRaw.length, top: games.top.length, exStall, exDraw }, chkSum, groups: {}, perGame, curveFam };
  for (const [k, A] of Object.entries(acc)) res.groups[k] = { n: A.n, dec: decompose(A), vb: viewB(A), A: summarize(A) };
  // heads vs placement, pooled per map and phase (no per-game Jensen term): for each map of the family, the group's pooled head share
  // h(map, phase) gives the reference capacity share f(map, phase, h) of an elite team; predicted A_U = (A_U + A_O) f. Summed over the
  // family's maps, per team-game of the group. heads = (pred A_O - pred A_U) * obar, placement = cap share term - heads.
  for (const gr of ['merge2', 'stack1-4', 'stack5-8', 'stack9', 'g4r4', 'swarm8', 'px', 'topL']) for (const fam of ['r500', 'elim']) {
    const G0 = res.groups[gr + '|' + fam]; if (!G0) continue;
    const pooled = [...Array(NPH)].map(() => [0, 0]);
    for (const m of MAPS) {
      if ((R500.has(m) ? 'r500' : 'elim') !== fam) continue;
      const A = acc[gr + '|map|' + m]; if (!A) continue;
      const GM = res.groups[gr + '|map|' + m]; let mh = 0;
      for (let ph = 0; ph < NPH; ph++) {
        const aU = A.att[ph][0][0] + A.att[ph][1][0] + A.att[ph][2][0], aO = A.att[ph][0][2] + A.att[ph][1][2] + A.att[ph][2][2];
        const hU = A.hr[0][ph], hO = A.hr[1][ph]; let pu = aU, po = aO;
        if (hU + hO > 0 && aU + aO > 0) { const sh = CUR.curve(m, ph, hU / (hU + hO)); pu = (aU + aO) * sh; po = (aU + aO) * (1 - sh); }
        pooled[ph][0] += pu; pooled[ph][1] += po;
        if (GM) mh += (po - pu) / GM.n * GM.dec.byPh[ph].obar;             // per map: heads term per team-game of that map
      }
      if (GM) { GM.dec.tot.dCapHeadsP = mh; GM.dec.tot.dCapPlaceP = GM.dec.tot.dCap - mh; }
    }
    const n = G0.n; let heads = 0;
    G0.dec.byPh.forEach((r, ph) => { r.pooledU = pooled[ph][0] / n; r.pooledO = pooled[ph][1] / n; r.dCapHeadsP = (r.pooledO - r.pooledU) * r.obar; r.dCapPlaceP = r.dCap - r.dCapHeadsP; heads += r.dCapHeadsP; });
    G0.dec.tot.dCapHeadsP = heads; G0.dec.tot.dCapPlaceP = G0.dec.tot.dCap - heads;
  }
  fs.mkdirSync(path.dirname(JOUT), { recursive: true });
  fs.writeFileSync(JOUT, JSON.stringify(res));
  fs.writeFileSync(OUT, report(res));
  console.log(`online ${games.online.length} games, top ${games.top.length} (raw ${topRaw.length}, stalled ${exStall}, draws ${exDraw}); checks ${JSON.stringify(chkSum)}`);
  console.log('-> ' + path.relative(ROOT, OUT) + ', ' + path.relative(ROOT, JOUT));
}

// compact per-team-game summary used by the report (rates and shares)
function summarize(A) {
  const n = A.n || 1, S = { n: A.n, rounds: A.rounds / n, elim: A.elim / n, win: A.win / n };
  S.Iu = A.nat[0].reduce((s, x) => s + x, 0) / n; S.Io = A.nat[1].reduce((s, x) => s + x, 0) / n;
  S.natPh = [0, 1].map(t => A.nat[t].map(x => x / n));
  S.hr = [0, 1].map(t => A.hr[t].map(x => x / n));
  S.unitsAt = [0, 1].map(t => [5, 10, 25, 35, 45, 50].map(i => A.unitsAt[t][i] / n));
  S.unitsEarly = [0, 1].map(t => [0, 1, 2, 3, 4, 5, 10, 15, 20, 25].map(i => A.unitsAt[t][i] / n));
  S.totalEarly = [0, 1].map(t => [0, 1, 2, 3, 4, 5, 10, 15, 20, 25].map(i => A.totalAt[t][i] / n));
  S.birthPh = [0, 1].map(t => A.birthPh[t].map(x => x / n)); S.deathPh = [0, 1].map(t => A.deathPh[t].map(x => x / n));
  S.kingAt = [0, 1].map(t => [10, 25, 35, 45, 50].map(i => A.kingAt[t][i] / n));
  S.totalAt = [0, 1].map(t => [10, 25, 35, 45, 50].map(i => A.totalAt[t][i] / n));
  // per-head rates (pearls per head per 10 rounds) by length class and by pearl territory, per phase and overall
  S.rateLc = [0, 1].map(t => [0, 1, 2, 3, 4, 5].map(lc => { let e = 0, h = 0; for (let ph = 0; ph < NPH; ph++) { e += A.eat[t][ph][lc].reduce((s, x) => s + x, 0); h += A.hrLc[t][ph][lc]; } return { h: h / n, e: e / n, r: h ? 10 * e / h : 0 }; }));
  S.rateTerr = [0, 1].map(t => [0, 1, 2].map(r => { let e = 0, h = 0; for (let ph = 0; ph < NPH; ph++) { for (let lc = 0; lc < 6; lc++) e += A.eat[t][ph][lc][r]; h += A.hr[t][ph]; } return { e: e / n, r: h ? 10 * e / h : 0 }; }));
  S.headTerr = [0, 1].map(t => [0, 1, 2].map(r => { let h = 0, all = 0; for (let ph = 0; ph < NPH; ph++) { h += A.hrT[t][ph][r]; all += A.hr[t][ph]; } return all ? h / all : 0; }));
  S.hrP = [0, 1].map(t => [0, 1, 2].map(lcs => [0, 1, 2, 3].map(d => { let s = 0; for (let ph = 0; ph < NPH; ph++) s += A.hrP[t][ph][lcs][d]; return s / n; })));
  S.hrPph = [0, 1].map(t => [...Array(NPH)].map((_, ph) => [0, 1, 2, 3].map(d => A.hrP[t][ph][0][d] + A.hrP[t][ph][1][d] + A.hrP[t][ph][2][d]).map(x => x / n)));
  // coverage: attempt race share by territory and phase, fountains
  S.att = [...Array(NPH)].map((_, ph) => A.att[ph].map(a => a.map(x => x / n)));
  S.attF = [...Array(NPH)].map((_, ph) => A.attF[ph].map(a => a.map(x => x / n)));
  S.attPred = A.attPred.map(a => a.map(x => x / n));
  // blocked per team-game: bodies (whose) x territory, natural pearls x territory x fate, drops x territory, mirror observed
  S.ob = [0, 1].map(w => [0, 1, 2].map(t => { let s = 0; for (let ph = 0; ph < NPH; ph++) for (let r = 0; r < 3; r++) s += A.ob[w][ph][t][r][0] + A.ob[w][ph][t][r][1]; return s / n; }));
  S.obF = [0, 1].map(w => [0, 1, 2].map(t => { let s = 0; for (let ph = 0; ph < NPH; ph++) for (let r = 0; r < 3; r++) s += A.ob[w][ph][t][r][1]; return s / n; }));
  S.obR = [0, 1].map(w => [0, 1, 2].map(r => { let s = 0; for (let ph = 0; ph < NPH; ph++) for (let t = 0; t < 3; t++) s += A.ob[w][ph][t][r][0] + A.ob[w][ph][t][r][1]; return s / n; }));
  S.pb = [0, 1, 2].map(t => [0, 1, 2].map(f => { let s = 0; for (let ph = 0; ph < NPH; ph++) for (let r = 0; r < 3; r++) s += A.pb[ph][t][r][f]; return s / n; }));
  S.pbR = [0, 1, 2].map(r => [0, 1, 2].map(f => { let s = 0; for (let ph = 0; ph < NPH; ph++) for (let t = 0; t < 3; t++) s += A.pb[ph][t][r][f]; return s / n; }));
  S.pbr = [0, 1, 2].map(t => { let s = 0; for (let ph = 0; ph < NPH; ph++) for (let r = 0; r < 3; r++) s += A.pbr[ph][t][r]; return s / n; });
  S.pbrR = [0, 1, 2].map(r => { let s = 0; for (let ph = 0; ph < NPH; ph++) for (let t = 0; t < 3; t++) s += A.pbr[ph][t][r]; return s / n; });
  S.dbR = [0, 1, 2].map(r => { let s = 0; for (let ph = 0; ph < NPH; ph++) for (let t = 0; t < 3; t++) s += A.db[ph][t][r]; return s / n; });
  S.steal = [0, 1, 2].map(r => [0, 1].map(e => [0, 1, 2].map(l => { let s = 0; for (let ph = 0; ph < NPH; ph++) s += A.steal[ph][r][e][l]; return s / n; })));
  S.db = [0, 1, 2].map(t => { let s = 0; for (let ph = 0; ph < NPH; ph++) for (let r = 0; r < 3; r++) s += A.db[ph][t][r]; return s / n; });
  S.sbm = [0, 1, 2, 3, 4].map(b => [0, 1, 2].map(t => { let s = 0; for (let ph = 0; ph < NPH; ph++) for (let r = 0; r < 3; r++) s += A.sbm[ph][b][t][r]; return s / n; }));
  S.attTot = [0, 1, 2].map(r => { let s = 0; for (let ph = 0; ph < NPH; ph++) for (let t = 0; t < 3; t++) s += A.att[ph][t][r]; return s / n; });
  S.appeared = A.appeared / n; S.spawned = A.spawned / n;
  // race detail: class x fate pooled, vision, territory, fountain
  S.cls = [...Array(9)].map((_, c) => [0, 1, 2].map(f => A.cls.reduce((s, p) => s + p[c][f], 0) / n));
  S.raceV = [0, 1, 2, 3].map(vm => [0, 1, 2].map(r3 => [0, 1, 2].map(f => A.raceV.reduce((s, p) => s + p[vm][r3][f], 0) / n)));
  S.raceT = [0, 1, 2].map(t => [0, 1, 2].map(r3 => [0, 1, 2].map(f => A.raceT.reduce((s, p) => s + p[t][r3][f], 0) / n)));
  S.raceF = [0, 1].map(fz => [0, 1, 2].map(r3 => [0, 1, 2].map(f => A.raceF.reduce((s, p) => s + p[fz][r3][f], 0) / n)));
  S.near = {}; for (const [k, v] of Object.entries(A.near)) S.near[k] = v / n;
  S.del = {}; for (const [k, v] of Object.entries(A.del)) S.del[k] = v[1] / Math.max(1, v[0]);
  // movement
  S.turns = A.turns.map(x => x / n); S.steps = A.steps.map(x => x / n); S.spr = A.spr.map(x => x / n); S.sprN = A.sprN.map(x => x / n); S.drop = A.drop.map(x => x / n);
  S.stepsPerPearl = [0, 1].map(t => { const I = A.nat[t].reduce((s, x) => s + x, 0); return I ? A.steps[t] / I : 0; });
  S.turnsPerPearl = [0, 1].map(t => { const I = A.nat[t].reduce((s, x) => s + x, 0); return I ? A.turns[t] / I : 0; });
  // our labels
  if (A.hasAct) {
    const na = A.hasAct;
    S.act = KINDS.map((k, i) => { let t = 0, e = 0; for (let b = 0; b < NB; b++) { t += A.act[i * NB + b]; e += A.acte[i * NB + b]; } return { k, turns: t / na, eat: e / na, rate: t ? 10 * e / t : 0 }; });
    S.org = ORIGS.map((k, i) => { let b0 = 0, e = 0, h = 0; for (let b = 0; b < NB; b++) { b0 += A.org[i * NB + b]; e += A.orge[i * NB + b]; h += A.orghr[i * NB + b]; } return { k, births: b0 / na, eat: e / na, hr: h / na, rate: h ? 10 * e / h : 0 }; });
  }
  return S;
}

// ---------------------------------------------------------------------------------------------------------------
function report(res) {
  const f0 = x => (x === undefined || x === null || isNaN(x)) ? '–' : Math.round(x).toLocaleString('en-US');
  const f1 = x => (x === undefined || x === null || isNaN(x)) ? '–' : (Math.round(x * 10) / 10).toFixed(1);
  const f2 = x => (x === undefined || x === null || isNaN(x)) ? '–' : (Math.round(x * 100) / 100).toFixed(2);
  const pc = x => (x === undefined || x === null || isNaN(x)) ? '–' : Math.round(x * 100) + '%';
  const L = [];
  L.push('# intake-gap report (machine tables)', '', `generated ${res.generated}; online ${res.N.online} games, top ${res.N.top} (raw ${res.N.topRaw}, stalled ${res.N.exStall}, draws ${res.N.exDraw})`, '', 'checks: ' + JSON.stringify(res.chkSum), '');
  const G = res.groups;
  const order = ['merge2', 'stack1-4', 'stack5-8', 'stack9', 'g4r4', 'swarm8', 'px'];
  for (const fam of ['r500', 'elim']) {
    L.push(`## ${fam}: totals per team-game`, '', '| group | n | rounds | elim | I us | I opp | gap | cov | cov:att | cov:heads | cov:place | blk body me | blk body opp | blk nat | blk drop | resid | contest | uneaten | ties |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
    for (const gr of [...order, 'topL']) { const x = G[gr + '|' + fam]; if (!x) continue; const t = x.dec.tot, S = x.A;
      L.push(`| ${gr} | ${x.n} | ${f0(S.rounds)} | ${pc(S.elim)} | ${f0(t.Iu)} | ${f0(t.Io)} | ${f0(t.gap)} | ${f0(t.cov)} | ${f0(t.covAtt)} | ${f0(t.covHeads)} | ${f0(t.covPlace)} | ${f0(t.covBlkBodyMe)} | ${f0(t.covBlkBodyOp)} | ${f0(t.covBlkNat)} | ${f0(t.covBlkDrop)} | ${f0(t.covResid)} | ${f0(t.contest)} | ${f0(t.uneaten)} | ${f0(t.ties)} |`); }
    L.push('');
    for (const gr of ['stack5-8', 'merge2', 'topL']) { const x = G[gr + '|' + fam]; if (!x) continue;
      L.push(`### ${fam} ${gr}: by phase`, '', '| phase | I us | I opp | gap | cov | cov:att | heads | place | blk me | blk opp | blk nat | blk drop | resid | contest | uneaten | ties | N_U | N_O | N_T | c_U | l_U | n_U | c_O | l_O | n_O | A_U | A_O | o_U | o_O |', '|---|' + '---:|'.repeat(28));
      for (const r of x.dec.byPh) L.push(`| ${r.ph} | ${f1(r.Iu)} | ${f1(r.Io)} | ${f1(r.gap)} | ${f1(r.cov)} | ${f1(r.covAtt)} | ${f1(r.covHeads)} | ${f1(r.covPlace)} | ${f1(r.covBlkBodyMe)} | ${f1(r.covBlkBodyOp)} | ${f1(r.covBlkNat)} | ${f1(r.covBlkDrop)} | ${f1(r.covResid)} | ${f1(r.contest)} | ${f1(r.uneaten)} | ${f1(r.ties)} | ${f1(r.NU)} | ${f1(r.NO)} | ${f1(r.NT)} | ${pc(r.cU)} | ${pc(r.lU)} | ${pc(r.nU)} | ${pc(r.cO)} | ${pc(r.lO)} | ${pc(r.nO)} | ${f1(r.AU)} | ${f1(r.AO)} | ${pc(r.oU)} | ${pc(r.oO)} |`);
      L.push('');
      const vb = x.vb; L.push(`View B (heads x rate): heads ${f0(vb.tot.heads)}, rate ${f0(vb.tot.rate)} (mix ${f0(vb.tot.mix)}, within ${f0(vb.tot.within)}), gap ${f0(vb.tot.gap)}`, '');
      L.push('| phase | H us | H opp | rate us /10r | rate opp /10r | heads | rate |', '|---|---:|---:|---:|---:|---:|---:|');
      for (const r of vb.rows) L.push(`| ${r.ph} | ${f0(r.HU)} | ${f0(r.HO)} | ${f2(r.rU)} | ${f2(r.rO)} | ${f1(r.heads)} | ${f1(r.rate)} |`);
      L.push('');
      const S = x.A;
      L.push('per-head rate by length class (pearls / head / 10 rounds; head-rounds per game): ' + [0, 1].map(t => (t ? 'opp ' : 'us ') + S.rateLc[t].map((q, i) => `${LCN[i]}:${f2(q.r)}(${f0(q.h)})`).join(' ')).join(' | '), '');
      L.push('natural eaten by pearl territory (own/neutral/enemy, per game): ' + [0, 1].map(t => (t ? 'opp ' : 'us ') + S.rateTerr[t].map(q => f0(q.e)).join('/')).join(' | ') + '; head location share own/neu/enemy: ' + [0, 1].map(t => (t ? 'opp ' : 'us ') + S.headTerr[t].map(pc).join('/')).join(' | '), '');
      L.push('blocked attempts per game: bodies [me, opp] x terr [neutral, mine, theirs] = ' + JSON.stringify(S.ob.map(a => a.map(v => +v.toFixed(1)))) + '; natural pearls terr x fate = ' + JSON.stringify(S.pb.map(a => a.map(v => +v.toFixed(1)))) + '; drops by terr = ' + JSON.stringify(S.db.map(v => +v.toFixed(1))) + '; mirror observed [me body, opp body, nat, drop, none] x terr = ' + JSON.stringify(S.sbm.map(a => a.map(v => +v.toFixed(1)))), '');
      L.push(`attempts by race (me nearer / tie / opp nearer) per game: ${S.attTot.map(f1).join(' / ')}; appeared ${f1(S.appeared)} (spawned ${f1(S.spawned)})`, '');
      L.push(`movement: turns ${S.turns.map(f0).join('/')}, steps ${S.steps.map(f0).join('/')}, steps per natural pearl ${S.stepsPerPearl.map(f1).join('/')}, sprint cost ${S.spr.map(f1).join('/')}, sprints ${S.sprN.map(f1).join('/')}, drops eaten ${S.drop.map(f1).join('/')}`, '');
      if (S.act) L.push('our labels (turns / nat eaten / rate per 10 turns): ' + S.act.filter(a => a.turns > 0).map(a => `${a.k} ${f0(a.turns)}/${f1(a.eat)}/${f2(a.rate)}`).join(', '), '', 'child origins (births / nat eaten / head-rounds / rate): ' + S.org.filter(a => a.births > 0).map(a => `${a.k} ${f1(a.births)}/${f1(a.eat)}/${f0(a.hr)}/${f2(a.rate)}`).join(', '), '');
    }
  }
  for (const fam of ['r500', 'elim']) {
    L.push(`## ${fam}: direct-count identity per team-game`, '', '| group | n | gap | race N_O-N_U | cap share | cap:heads | cap:place | heads (pooled) | place (pooled) | open:our bodies | open:their bodies | open:nat pearls | open:drops | model resid | steals x2 | stolen from us | stolen by us | uneaten | ties | check |', '|---|' + '---:|'.repeat(19));
    for (const gr of [...order, 'topL']) { const x = G[gr + '|' + fam]; if (!x) continue; const t = x.dec.tot;
      L.push(`| ${gr} | ${x.n} | ${f0(t.gap)} | ${f0(t.dRace)} | ${f0(t.dCap)} | ${f0(t.dCapHeads)} | ${f0(t.dCapPlace)} | ${f0(t.dCapHeadsP)} | ${f0(t.dCapPlaceP)} | ${f0(t.dBlkMe)} | ${f0(t.dBlkOp)} | ${f0(t.dBlkNat)} | ${f0(t.dBlkDrop)} | ${f0(t.dResid)} | ${f0(t.dSteal)} | ${f1(t.stolenFromUs)} | ${f1(t.stolenByUs)} | ${f0(t.dUneat)} | ${f0(t.dTies)} | ${f1(t.dCheck)} |`); }
    L.push('');
    for (const gr of ['stack5-8', 'merge2', 'stack9', 'topL']) { const x = G[gr + '|' + fam]; if (!x) continue;
      L.push(`### ${fam} ${gr}: direct-count identity by phase`, '', '| phase | gap | race | cap | heads | place | bodies us | bodies them | nat pearls | drops | resid | steals x2 | uneaten | ties | pred A_U | pred A_O | obar |', '|---|' + '---:|'.repeat(16));
      for (const r of x.dec.byPh) L.push(`| ${r.ph} | ${f1(r.gap)} | ${f1(r.dRace)} | ${f1(r.dCap)} | ${f1(r.dCapHeads)} | ${f1(r.dCapPlace)} | ${f1(r.dBlkMe)} | ${f1(r.dBlkOp)} | ${f1(r.dBlkNat)} | ${f1(r.dBlkDrop)} | ${f1(r.dResid)} | ${f1(r.dSteal)} | ${f1(r.dUneat)} | ${f1(r.dTies)} | ${f1(r.pU)} | ${f1(r.pO)} | ${pc(r.obar)} |`);
      L.push('');
    }
  }
  L.push('## per map (stack5-8 and topL)', '', '| map | group | n | I us | I opp | gap | cov | heads | place | blk | resid | contest | uneaten | ties |', '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
  for (const m of MAPS) for (const gr of ['stack5-8', 'merge2', 'topL']) { const x = G[gr + '|map|' + m]; if (!x) continue; const t = x.dec.tot;
    L.push(`| ${m} | ${gr} | ${x.n} | ${f0(t.Iu)} | ${f0(t.Io)} | ${f0(t.gap)} | ${f0(t.cov)} | ${f0(t.covHeads)} | ${f0(t.covPlace)} | ${f0(t.covBlkBodyMe + t.covBlkBodyOp + t.covBlkNat + t.covBlkDrop)} | ${f0(t.covResid)} | ${f0(t.contest)} | ${f0(t.uneaten)} | ${f0(t.ties)} |`); }
  L.push('');
  L.push('## per map and layout (stack5-8)', '', '| map/layout | n | I us | I opp | gap | cov | heads | place | contest | uneaten |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
  for (const k of Object.keys(G).filter(k => k.startsWith('stack5-8|mapv|')).sort()) { const x = G[k], t = x.dec.tot; L.push(`| ${k.split('|')[2]} | ${x.n} | ${f0(t.Iu)} | ${f0(t.Io)} | ${f0(t.gap)} | ${f0(t.cov)} | ${f0(t.covHeads)} | ${f0(t.covPlace)} | ${f0(t.contest)} | ${f0(t.uneaten)} |`); }
  L.push('');
  L.push('## per set', '', '| set | fam | n | I us | I opp | gap | cov | heads | place | contest | uneaten |', '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
  for (const k of Object.keys(G).filter(k => k.startsWith('set|')).sort()) { const x = G[k], t = x.dec.tot; const [, s, fam] = k.split('|'); L.push(`| ${s} | ${fam} | ${x.n} | ${f0(t.Iu)} | ${f0(t.Io)} | ${f0(t.gap)} | ${f0(t.cov)} | ${f0(t.covHeads)} | ${f0(t.covPlace)} | ${f0(t.contest)} | ${f0(t.uneaten)} |`); }
  L.push('');
  return L.join('\n');
}
module.exports = { teamView, decompose, viewB, summarize, buildCurve, GROUPS };
if (require.main === module) main();
