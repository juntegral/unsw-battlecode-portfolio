#!/usr/bin/env node
// system_report.js — the judgement report of unsw-swarm (EVAL.md): outcome against the top 7 teams, the five diagnostic
// indicators and the engine labels, for one online set or a pool of sets, optionally against a comparison pool (--vs).
// Replaces tools/mech_check.js as the primary report (mech_check stays for the old per-mechanism tags). Replays and caches
// only: no games, no network.
//
// usage (repository root):
//   node eval/system_report.js <set>[+<set>...] [<set> ...] [--vs <set>[+<set>...]] [--name <label>] [--vs-name <label>]
//                              [--out <report.md>] [--json <report.json>] [--no-extract] [--online <dir>]
//   node eval/system_report.js cand-stack11-online --out exp/system-report/w12.md --json exp/system-report/w12.json
//   node eval/system_report.js cand-stack6-online+cand-stack6-online-r2 --vs cand-stack11-online
//   A set is a folder of data/online (index.json, game-<id>.json, M<id>.replay). Without --out the Markdown goes to stdout.
//
// Population: the games of the sets against the top 6 (TOP6 below) and DEV 545. Games against anyone else are skipped
// (counted under "sources").
// Sources per game:
//   outcome   index.json (ourSide, winner, ourWin) and game-<id>.json replay.result (endReason, dragonCount, longestDragon)
//   ledger    tools/mass_ledger.js cache .cache/mass-ledger/online-<set>.jsonl (shared through the .cache link). Games
//             with a replay but no ledger line are extracted with `node tools/mass_ledger.js extract online <set> --jobs 2`
//             unless --no-extract.
//   endgame   legacy/exp/endgame-king/extract.js analyse() (the endgame king study's extractor, unchanged). Read from its
//             cache .cache/endgame-king/online-<set>.jsonl when there, else computed here and cached in
//             exp/system-report/cache/endgame-online-<set>.jsonl (the same line format).
//   labels    our dragonIndicator texts in the replay, cached in exp/system-report/cache/labels-online-<set>.jsonl. A set
//             is probed with its first replay; a set whose probe has no " E=" label is taken as unlabelled.
// Definitions:
//   W / D / L  ourWin true / winner null (a draw) / otherwise.
//   E          we were eliminated: endReason teamEliminated and our dragonCount 0. "They eliminated" is counted apart.
//   Wilson     95% score interval (z = 1.96) for every rate.
//   families   fortress maps = Autarky, Prisoners Dilemma, Portals; swarm maps = the other seven (ENGINE.md, bot/policy.hpp).
//   kinds      500-round maps (r500) = Autarky, Portals, Schooltime, Slithery Fight, Trauma; elimination maps (elim) =
//              Default, Devil, Prisoners Dilemma, Queen Of Spades, Trophy (tools/mass_ledger.js R500 / ELIM; the research
//              docs' "500형" / "전멸형"). The indicators are split by family x kind.
//   indicators (EVAL.md section 2; population: top 6 + DEV 545 games in the ledger; per team, ours and theirs):
//     r100 heads         st.units[10]: living dragons at the start of r100 (0 once eliminated); mean per game.
//     natural intake     sum over the game of fl nat_own + nat_enemy + nat_neutral (natural pearls eaten); mean per game;
//                        the ratio is ours / theirs of the pool sums.
//     line sacrifice     endgame-king dec[b][1] summed over the bins b = 1..4 (r300-349 ... r450-499): own-sacrifice drops
//                        eaten by the final king's line; mean over the team's full games (500 rounds and a final king), as
//                        mech_check's gh / kx rows ("500형 끝까지").
//     final longest      st.king[50]: the longest dragon at the end (0 once eliminated); mean per game.
//     elimination        our eliminations / games (Wilson).
//   comparison (--vs)  top-6 win rate difference with the Newcombe (Wilson-based) 95% interval; one-sided Fisher exact
//                      p-values (candidate > vs, and candidate < vs for the fortress regression watch). Power: the exact
//                      power of that one-sided Fisher test at alpha 0.05, both pools binomial, the vs pool at its observed
//                      rate and size, the candidate at 12/14/17/20% (EVAL.md's table rows) for 1-6 waves of 60 top-6 games
//                      and for the candidate's own size. Without --vs the same table is given against EVAL.md's baseline
//                      (stack11 lineage, 81/900).
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');

const ROOT = path.resolve(__dirname, '..');
let ONLINE = path.join(ROOT, 'data', 'online');   // --online <dir> replaces it (a local set laid out like data/online; use with --no-extract)
const ML_PATH = path.join(ROOT, 'tools', 'mass_ledger.js');
const ML = require(ML_PATH), FI = ML.FI;
const LEDGER_CACHE = path.join(ROOT, '.cache', 'mass-ledger');
const EK_PATH = path.join(ROOT, 'legacy', 'exp', 'endgame-king', 'extract.js');
const EK_CACHE = path.join(ROOT, '.cache', 'endgame-king');
const CACHE = path.join(ROOT, 'exp', 'system-report', 'cache');

const TOP6 = [306, 70, 20, 801, 264, 46], DEV = 545;
const MAPS = ['Autarky', 'Prisoners Dilemma', 'Portals', 'Trauma', 'Slithery Fight', 'Schooltime', 'Default', 'Devil', 'Queen Of Spades', 'Trophy'];
const FORTRESS = new Set(['Autarky', 'Prisoners Dilemma', 'Portals']);
const R500 = new Set(ML.R500);
const famOf = m => FORTRESS.has(m) ? 'fortress' : 'swarm';
const kindOf = m => R500.has(m) ? 'r500' : 'elim';
const BASELINE = { name: 'EVAL.md baseline (stack11 lineage, 15 waves)', W: 81, n: 900 };
const TARGETS = { u100: '≥25', ratio: '≥50%', lineSac: '≥15', king: '≥35', elim: '≤40% (elimination maps)' };   // EVAL.md §2, v1 targets
const Z = 1.959964;

// ---------------------------------------------------------------------------------------------------------------
// statistics
const LF = [0];
const lf = n => { while (LF.length <= n) LF.push(LF[LF.length - 1] + Math.log(LF.length)); return LF[n]; };
const lC = (n, k) => lf(n) - lf(k) - lf(n - k);
const pmf = (n, k, p) => p <= 0 ? (k === 0 ? 1 : 0) : p >= 1 ? (k === n ? 1 : 0) : Math.exp(lC(n, k) + k * Math.log(p) + (n - k) * Math.log(1 - p));
const sf = (n, k, p) => { let s = 0; for (let i = Math.max(0, k); i <= n; i++) s += pmf(n, i, p); return Math.min(1, s); };  // P(X >= k)
function wilson(k, n) {
  if (!n) return [null, null, null];
  const p = k / n, d = 1 + Z * Z / n, c = (p + Z * Z / (2 * n)) / d, h = Z * Math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d;
  return [p, Math.max(0, c - h), Math.min(1, c + h)];
}
function newcombe(k1, n1, k0, n0) {   // 95% interval of p1 - p0 (Newcombe 1998, method 10)
  const [p1, l1, u1] = wilson(k1, n1), [p0, l0, u0] = wilson(k0, n0);
  if (p1 === null || p0 === null) return [null, null, null];
  const d = p1 - p0;
  return [d, d - Math.sqrt((p1 - l1) ** 2 + (u0 - p0) ** 2), d + Math.sqrt((u1 - p1) ** 2 + (p0 - l0) ** 2)];
}
// one-sided Fisher exact test on the 2x2 table (k1 of n1 vs k0 of n0): P(X1 >= k1 | margins) (greater) or P(X1 <= k1) (less)
function fisher(k1, n1, k0, n0, side) {
  const K = k1 + k0, N = n1 + n0, lo = Math.max(0, K - n0), hi = Math.min(n1, K), den = lC(N, K);
  let p = 0;
  for (let k = side === 'greater' ? k1 : lo; k <= (side === 'greater' ? hi : k1); k++) p += Math.exp(lC(n1, k) + lC(n0, K - k) - den);
  return Math.min(1, p);
}
function critical(n1, k0, n0, alpha) {   // the fewest candidate wins of n1 that reach p <= alpha against k0 of n0 (n1 + 1 = none)
  for (let k = 0; k <= n1; k++) if (fisher(k, n1, k0, n0, 'greater') <= alpha) return k;
  return n1 + 1;
}
function power(n1, p1, n0, p0, alpha) {  // exact power of the one-sided Fisher test, both pools binomial
  let pw = 0, crit = n1 + 1;
  for (let x0 = n0; x0 >= 0; x0--) {     // the critical count falls as x0 falls; walk it down
    const w0 = pmf(n0, x0, p0);
    if (w0 < 1e-13) continue;
    if (crit > n1) crit = critical(n1, x0, n0, alpha);
    else { while (crit > 0 && fisher(crit - 1, n1, x0, n0, 'greater') <= alpha) crit--; while (crit <= n1 && fisher(crit, n1, x0, n0, 'greater') > alpha) crit++; }
    pw += w0 * sf(n1, crit, p1);
  }
  return pw;
}

// ---------------------------------------------------------------------------------------------------------------
// data
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => JSON.parse(l)) : [];
const sum = a => a.reduce((s, v) => s + v, 0);
let loader = null;
function loadReplay(file) {
  if (!loader) { const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js')); loader = makeLoader(viewerSource()); }
  return loader(file);
}

function readSet(set, opts, notes) {
  const dir = path.join(ONLINE, set);
  if (!fs.existsSync(path.join(dir, 'index.json'))) throw Error(`no such set: ${path.relative(ROOT, dir)}`);
  const idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  const games = [], skipped = [];
  for (const g of idx.games || idx) {
    const opp = g.opponentTeam;
    if (!TOP6.includes(opp) && opp !== DEV) { skipped.push(g.gameId); continue; }
    let res = null, oppName = null;
    const gf = path.join(dir, `game-${g.gameId}.json`);
    if (fs.existsSync(gf)) {
      const j = JSON.parse(fs.readFileSync(gf, 'utf8'));
      res = j.replay && j.replay.result || null;
      oppName = String(g.ourSide).toUpperCase() === 'A' ? j.teamBName : j.teamAName;
    }
    const us = String(g.ourSide).toUpperCase(), them = us === 'A' ? 'B' : 'A';
    const ro = res && res['team' + us], rt = res && res['team' + them];
    const outcome = g.ourWin === true ? 'W' : g.winner == null || g.winner === 'null' ? 'D' : 'L';
    games.push({
      set, gameId: g.gameId, key: `${set}:${g.gameId}`, map: g.mapName, opp, oppName, us, them, outcome,
      endReason: res ? res.endReason : null,
      weElim: !!(res && res.endReason === 'teamEliminated' && ro && ro.dragonCount === 0),
      theyElim: !!(res && res.endReason === 'teamEliminated' && rt && rt.dragonCount === 0),
      longO: ro ? ro.longestDragon : null, longT: rt ? rt.longestDragon : null,
      replay: fs.existsSync(path.join(dir, `M${g.gameId}.replay`)) ? path.join(dir, `M${g.gameId}.replay`) : null,
      led: null, eg: null, eng: null,
    });
  }
  // ledger
  const ledFile = path.join(LEDGER_CACHE, `online-${set}.jsonl`);
  let led = new Map(readJsonl(ledFile).map(r => [r.key, r]));
  const missing = games.filter(g => g.replay && !led.has(g.key));
  if (missing.length && !opts.noExtract) {
    notes.push(`${set}: ${missing.length} games had no mass-ledger line; ran tools/mass_ledger.js extract online ${set}`);
    const r = cp.spawnSync('nice', ['-n', '10', process.execPath, ML_PATH, 'extract', 'online', set, '--jobs', '2'], { cwd: ROOT, stdio: ['ignore', process.stderr, process.stderr] });
    if (r.status !== 0) notes.push(`${set}: mass-ledger extraction exited with ${r.status}`);
    led = new Map(readJsonl(ledFile).map(r => [r.key, r]));
  }
  const chk = {};
  for (const g of games) {
    const r = led.get(g.key); if (!r) continue;
    for (const [k, v] of Object.entries(r.chk || {})) chk[k] = (chk[k] || 0) + v;
    const t = side => { const T = r[side]; return { u100: T.st.units[10], king: T.st.king[50], nat: sum(T.fl[FI.nat_own]) + sum(T.fl[FI.nat_enemy]) + sum(T.fl[FI.nat_neutral]) }; };
    g.led = { O: t(r.us), T: t(r.us === 'A' ? 'B' : 'A'), kind: r.kind };
  }
  // endgame (legacy cache, then ours; compute the rest) and labels (probe, then every game of a labelled set)
  fs.mkdirSync(CACHE, { recursive: true });
  const egOwnFile = path.join(CACHE, `endgame-online-${set}.jsonl`), labFile = path.join(CACHE, `labels-online-${set}.jsonl`);
  const eg = new Map(), egSrc = { legacy: 0, own: 0, computed: 0 };
  for (const r of readJsonl(path.join(EK_CACHE, `online-${set}.jsonl`))) { eg.set(r.key, r); egSrc.legacy++; }
  for (const r of readJsonl(egOwnFile)) if (!eg.has(r.key)) { eg.set(r.key, r); egSrc.own++; }
  const lab = new Map(readJsonl(labFile).map(r => [r.key, r]));
  const withReplay = games.filter(g => g.replay);
  let labelled = null;   // null unknown, true / false
  if (withReplay.length) {
    const probe = withReplay[0];
    if (!lab.has(probe.key)) { const R = loadReplay(probe.replay); const x = countLabels(R, probe); lab.set(probe.key, x); fs.appendFileSync(labFile, JSON.stringify(x) + '\n'); }
    labelled = [...lab.values()].some(x => x.F + x.S > 0);
  }
  let EK = null, perGame = null;
  for (const g of withReplay) {
    const needEg = !eg.has(g.key), needLab = labelled && !lab.has(g.key);
    if (!needEg && !needLab) continue;
    const R = loadReplay(g.replay);
    if (needEg) {
      if (!EK) { EK = require(EK_PATH); perGame = ML.perGame; }
      try {
        const X = EK.analyse(R, { key: g.key, map: g.map, us: g.us, set, src: 'online', opp: g.oppName || String(g.opp), oppId: g.opp }, perGame);
        eg.set(g.key, X); egSrc.computed++;
        fs.appendFileSync(egOwnFile, JSON.stringify(X) + '\n');
      } catch (err) { notes.push(`${g.key}: endgame analyse failed: ${String(err).slice(0, 120)}`); }
    }
    if (needLab) { const x = countLabels(R, g); lab.set(g.key, x); fs.appendFileSync(labFile, JSON.stringify(x) + '\n'); }
  }
  const chk2 = {};
  for (const g of games) {
    const X = eg.get(g.key); if (!X) continue;
    for (const o of [X.chk || {}, X.chk2 || {}]) for (const [k, v] of Object.entries(o)) chk2[k] = (chk2[k] || 0) + v;
    const t = side => { const T = X[side]; const full = X.rounds === 500 && T && T.kid >= 0; return { full, lineSac: full ? [1, 2, 3, 4].reduce((a, b) => a + T.dec[b][1], 0) : null }; };
    g.eg = { O: t(g.us), T: t(g.them) };
  }
  if (labelled) for (const g of games) { const x = lab.get(g.key); if (x) g.eng = { F: x.F, S: x.S, none: x.none }; }
  return { set, games, skipped: skipped.length, ledChk: chk, egChk: chk2, egSrc, labelled, ledFile, egOwnFile };
}

// our indicator labels by engine: " E=F" / " E=S" at the end of the text (bot/main.cpp, unsw-swarm v0 on)
function countLabels(R, g) {
  const team = new Map();
  for (const d of R.match.map.initialDragons || []) team.set(d.id, d.team);
  let F = 0, S = 0, none = 0;
  for (const e of R.events) {
    if (e.type === 'dragonSplit') team.set(e.childId, e.team);
    else if (e.type === 'dragonIndicator' && team.get(e.id) === g.us) {
      const m = / ?E=([A-Z])$/.exec(e.text || '');
      if (!m) none++; else if (m[1] === 'S') S++; else F++;
    }
  }
  return { key: g.key, map: g.map, F, S, none };
}

// ---------------------------------------------------------------------------------------------------------------
// aggregation
function outcomeStats(gs) {
  const n = gs.length, c = k => gs.filter(g => g.outcome === k).length;
  const W = c('W'), D = c('D'), L = c('L'), E = gs.filter(g => g.weElim).length, TE = gs.filter(g => g.theyElim).length;
  const lo = gs.filter(g => g.longO !== null), lt = gs.filter(g => g.longT !== null);
  return { n, W, D, L, E, TE, rW: wilson(W, n), rD: wilson(D, n), rL: wilson(L, n), rE: wilson(E, n),
    longO: lo.length ? sum(lo.map(g => g.longO)) / lo.length : null, longT: lt.length ? sum(lt.map(g => g.longT)) / lt.length : null };
}
function indicatorStats(gs) {
  const L = gs.filter(g => g.led), n = L.length, m = f => n ? sum(L.map(f)) / n : null;
  const natO = sum(L.map(g => g.led.O.nat)), natT = sum(L.map(g => g.led.T.nat));
  const fo = gs.filter(g => g.eg && g.eg.O.full), ft = gs.filter(g => g.eg && g.eg.T.full);
  const E = gs.filter(g => g.weElim).length;
  return { games: gs.length, ledger: n,
    u100: [m(g => g.led.O.u100), m(g => g.led.T.u100)],
    nat: [m(g => g.led.O.nat), m(g => g.led.T.nat)], natRatio: natT ? natO / natT : null,
    lineSac: [fo.length ? sum(fo.map(g => g.eg.O.lineSac)) / fo.length : null, ft.length ? sum(ft.map(g => g.eg.T.lineSac)) / ft.length : null], lineN: [fo.length, ft.length],
    king: [m(g => g.led.O.king), m(g => g.led.T.king)],
    elim: wilson(E, gs.length), E };
}
function build(pool, opts, notes) {
  const sets = pool.map(s => readSet(s, opts, notes));
  const games = sets.flatMap(s => s.games);
  const top = games.filter(g => TOP6.includes(g.opp)), dev = games.filter(g => g.opp === DEV);
  const names = {}; for (const g of games) if (g.oppName) names[g.opp] = g.oppName;
  const by = (gs, f, keys) => Object.fromEntries(keys.filter(k => gs.some(g => f(g) === k)).map(k => [k, outcomeStats(gs.filter(g => f(g) === k))]));
  const outcome = {
    top6: { all: outcomeStats(top), family: by(top, g => famOf(g.map), ['fortress', 'swarm']), map: by(top, g => g.map, MAPS), opp: by(top, g => g.opp, TOP6) },
    dev: { all: outcomeStats(dev), family: by(dev, g => famOf(g.map), ['fortress', 'swarm']), map: by(dev, g => g.map, MAPS) },
    top7: { all: outcomeStats(games) },
  };
  const cells = {
    'all maps': games,
    '500-round maps (r500)': games.filter(g => kindOf(g.map) === 'r500'),
    'elimination maps (elim)': games.filter(g => kindOf(g.map) === 'elim'),
    'fortress · r500 (Autarky, Portals)': games.filter(g => famOf(g.map) === 'fortress' && kindOf(g.map) === 'r500'),
    'fortress · elim (Prisoners Dilemma)': games.filter(g => famOf(g.map) === 'fortress' && kindOf(g.map) === 'elim'),
    'swarm · r500 (Schooltime, Slithery Fight, Trauma)': games.filter(g => famOf(g.map) === 'swarm' && kindOf(g.map) === 'r500'),
    'swarm · elim (Default, Devil, Queen Of Spades, Trophy)': games.filter(g => famOf(g.map) === 'swarm' && kindOf(g.map) === 'elim'),
  };
  const indicators = Object.fromEntries(Object.entries(cells).map(([k, gs]) => [k, indicatorStats(gs)]));
  const lab = games.filter(g => g.eng);
  const engine = lab.length ? Object.fromEntries(MAPS.filter(m => lab.some(g => g.map === m)).map(m => {
    const gs = lab.filter(g => g.map === m), F = sum(gs.map(g => g.eng.F)), S = sum(gs.map(g => g.eng.S)), none = sum(gs.map(g => g.eng.none));
    return [m, { games: gs.length, F, S, none, shareS: F + S ? S / (F + S) : null }];
  })) : null;
  if (engine) { const F = sum(lab.map(g => g.eng.F)), S = sum(lab.map(g => g.eng.S)), none = sum(lab.map(g => g.eng.none)); engine.all = { games: lab.length, F, S, none, shareS: F + S ? S / (F + S) : null }; }
  const sources = sets.map(s => ({ set: s.set, games: s.games.length, top6: s.games.filter(g => TOP6.includes(g.opp)).length, dev: s.games.filter(g => g.opp === DEV).length,
    skipped: s.skipped, noReplay: s.games.filter(g => !g.replay).length, ledger: s.games.filter(g => g.led).length, endgame: s.games.filter(g => g.eg).length,
    endgameFrom: s.egSrc, ledgerChecks: s.ledChk, endgameChecks: s.egChk, labelled: s.labelled }));
  return { sets: pool, games, names, outcome, indicators, engine, sources };
}
function compare(A, B) {
  const a = A.outcome.top6, b = B.outcome.top6, row = (x, y) => x && y ? {
    cand: [x.W, x.n], vs: [y.W, y.n], diff: newcombe(x.W, x.n, y.W, y.n),
    pGreater: fisher(x.W, x.n, y.W, y.n, 'greater'), pLess: fisher(x.W, x.n, y.W, y.n, 'less') } : null;
  const out = { all: row(a.all, b.all), fortress: row(a.family.fortress, b.family.fortress), swarm: row(a.family.swarm, b.family.swarm),
    dev: row(A.outcome.dev.all, B.outcome.dev.all), elim: null };
  const ea = A.outcome.top7.all, eb = B.outcome.top7.all;   // our eliminations over the top-7 games (lower is better)
  out.elim = { cand: [ea.E, ea.n], vs: [eb.E, eb.n], diff: newcombe(ea.E, ea.n, eb.E, eb.n), pLess: fisher(ea.E, ea.n, eb.E, eb.n, 'less') };
  return out;
}
function powerTable(nCand, W0, n0) {
  const p0 = n0 ? W0 / n0 : 0, sizes = [60, 120, 180, 240, 360];
  if (nCand && !sizes.includes(nCand)) sizes.push(nCand);
  sizes.sort((x, y) => x - y);
  const rows = [0.12, 0.14, 0.17, 0.20].map(p1 => ({ p1, power: sizes.map(n1 => power(n1, p1, n0, p0, 0.05)) }));
  return { vs: [W0, n0], sizes, rows, critical: sizes.map(n1 => critical(n1, W0, n0, 0.05)) };
}

// ---------------------------------------------------------------------------------------------------------------
// Markdown
const pc = (x, d = 1) => x === null || x === undefined || Number.isNaN(x) ? '–' : (100 * x).toFixed(d) + '%';
const f1 = x => x === null || x === undefined || Number.isNaN(x) ? '–' : x.toFixed(1);
const f2 = x => x === null || x === undefined || Number.isNaN(x) ? '–' : x.toFixed(2);
const pv = x => x === null || x === undefined ? '–' : x < 0.001 ? '<0.001' : x.toFixed(3);
const rate = (k, r) => r[0] === null ? '–' : `${k} (${pc(r[0])}, ${pc(r[1])}–${pc(r[2])})`;
function outcomeTable(L, rows) {
  L.push('| | games | W | D | L | E (we eliminated) | they eliminated | final longest ours / theirs |', '|---|---|---|---|---|---|---|---|');
  for (const [label, s] of rows) if (s) L.push(`| ${label} | ${s.n} | ${rate(s.W, s.rW)} | ${rate(s.D, s.rD)} | ${rate(s.L, s.rL)} | ${rate(s.E, s.rE)} | ${s.TE} | ${f1(s.longO)} / ${f1(s.longT)} |`);
  L.push('');
}
function indicatorTable(L, ind) {
  L.push('| cell | games (ledger) | r100 heads ours / theirs | natural intake ours / theirs (ratio) | line sacrifice pearls r300–499 ours / theirs (full games) | final longest ours / theirs | we eliminated |',
    '|---|---|---|---|---|---|---|');
  for (const [k, s] of Object.entries(ind)) {
    if (!s.games) continue;
    L.push(`| ${k} | ${s.games} (${s.ledger}) | ${f1(s.u100[0])} / ${f1(s.u100[1])} | ${f1(s.nat[0])} / ${f1(s.nat[1])} (${pc(s.natRatio, 0)}) | ${f1(s.lineSac[0])} / ${f1(s.lineSac[1])} (${s.lineN[0]} / ${s.lineN[1]}) | ${f1(s.king[0])} / ${f1(s.king[1])} | ${rate(s.E, s.elim)} |`);
  }
  L.push('');
}
function markdown(rep) {
  const A = rep.pool, B = rep.vsPool, L = [];
  const nm = id => `${id}${A.names[id] || (B && B.names[id]) ? ' ' + (A.names[id] || B.names[id]) : ''}`;
  L.push(`# System report: ${rep.name}`, '');
  L.push(`- Sets: ${A.sets.map(s => '`' + s + '`').join(', ')}`);
  if (B) L.push(`- Compared with (--vs): ${rep.vsName}: ${B.sets.map(s => '`' + s + '`').join(', ')}`);
  L.push(`- Games: top 6 ${A.outcome.top6.all.n}, DEV 545 ${A.outcome.dev.all.n} (other opponents skipped: ${sum(A.sources.map(s => s.skipped))})`);
  L.push(`- Tool: \`eval/system_report.js\` (definitions in its header and \`eval/README.md\`), generated ${rep.generated}`, '');

  L.push('## 1. Outcome', '');
  L.push('### Top 6 (306, 70, 20, 801, 264, 46)', '');
  const t = A.outcome.top6;
  outcomeTable(L, [['**all**', t.all], ['fortress maps (Autarky, PD, Portals)', t.family.fortress], ['swarm maps (the other seven)', t.family.swarm]]);
  L.push('By map:', '');
  outcomeTable(L, MAPS.map(m => [`${m} (${famOf(m)}, ${kindOf(m)})`, t.map[m]]));
  L.push('By opponent:', '');
  outcomeTable(L, TOP6.map(id => [nm(id), t.opp[id]]));
  L.push('### DEV 545 (apart)', '');
  const d = A.outcome.dev;
  outcomeTable(L, [['**all**', d.all], ['fortress maps', d.family.fortress], ['swarm maps', d.family.swarm], ...MAPS.map(m => [m, d.map[m]])]);
  if (B) {
    const c = rep.compare, bt = B.outcome.top6;
    L.push(`### Against ${rep.vsName}`, '');
    L.push(`- ${rep.vsName}: top 6 ${rate(bt.all.W, bt.all.rW)} of ${bt.all.n}; fortress ${bt.family.fortress ? rate(bt.family.fortress.W, bt.family.fortress.rW) : '–'}; swarm ${bt.family.swarm ? rate(bt.family.swarm.W, bt.family.swarm.rW) : '–'}; DEV ${rate(B.outcome.dev.all.W, B.outcome.dev.all.rW)}`, '');
    L.push('| | this pool | vs pool | difference (95% CI) | p one-sided: this > vs | p one-sided: this < vs |', '|---|---|---|---|---|---|');
    for (const [label, r] of [['top 6, all maps', c.all], ['top 6, fortress maps (watch: this < vs)', c.fortress], ['top 6, swarm maps (goal: this > vs)', c.swarm], ['DEV 545', c.dev]]) if (r)
      L.push(`| ${label} | ${r.cand[0]}/${r.cand[1]} (${pc(r.cand[0] / r.cand[1])}) | ${r.vs[0]}/${r.vs[1]} (${pc(r.vs[0] / r.vs[1])}) | ${r.diff[0] === null ? '–' : `${(100 * r.diff[0]).toFixed(1)} pp (${(100 * r.diff[1]).toFixed(1)} … ${(100 * r.diff[2]).toFixed(1)})`} | ${pv(r.pGreater)} | ${pv(r.pLess)} |`);
    const e = c.elim;
    L.push(`| we eliminated, top 7 (lower is better) | ${e.cand[0]}/${e.cand[1]} (${pc(e.cand[0] / e.cand[1])}) | ${e.vs[0]}/${e.vs[1]} (${pc(e.vs[0] / e.vs[1])}) | ${(100 * e.diff[0]).toFixed(1)} pp (${(100 * e.diff[1]).toFixed(1)} … ${(100 * e.diff[2]).toFixed(1)}) | – | ${pv(e.pLess)} |`, '');
  }
  const P = rep.power;
  L.push(`### Power (one-sided Fisher exact, α = 0.05, against ${B ? rep.vsName : BASELINE.name}: ${P.vs[0]}/${P.vs[1]} = ${pc(P.vs[0] / P.vs[1])})`, '');
  L.push(`| true top-6 win rate | ${P.sizes.map(n => `${n} games${n % 60 === 0 ? ` (${n / 60} wave${n === 60 ? '' : 's'})` : ''}${n === A.outcome.top6.all.n ? ' ← this pool' : ''}`).join(' | ')} |`, `|---|${P.sizes.map(() => '---|').join('')}`);
  for (const r of P.rows) L.push(`| ${pc(r.p1, 0)} | ${r.power.map(f2).join(' | ')} |`);
  L.push(`| wins needed for p < 0.05 | ${P.critical.map((k, i) => `${k} (${pc(k / P.sizes[i])})`).join(' | ')} |`, '');
  L.push('- EVAL.md §1 gives the same table against a fixed 9.0% without recording its method; against 81/900 this exact computation lands within about ±0.06 of it. The rule stays: judge a version on 3 pooled waves (180 top-6 games).', '');

  L.push('## 2. Diagnostic indicators (EVAL.md §2)', '');
  L.push(`- Population: top 6 + DEV 545 games. Per game means; the intake ratio is ours ÷ theirs of the pool sums. Line sacrifice: games that reached r500 with a final king (n in brackets, ours / theirs). v1 targets (swarm maps): r100 heads ${TARGETS.u100}, intake ratio ${TARGETS.ratio}, line sacrifice ${TARGETS.lineSac}, final longest ${TARGETS.king}, elimination ${TARGETS.elim}.`, '');
  indicatorTable(L, A.indicators);
  if (B) { L.push(`${rep.vsName}:`, ''); indicatorTable(L, B.indicators); }

  L.push('## 3. Engine labels (" E=F" / " E=S")', '');
  const eng = A.engine;
  if (!eng) L.push('- No engine labels in these sets (bots before unsw-swarm v0).', '');
  else {
    L.push('| map | games | our turns E=F | E=S | unlabelled | E=S share |', '|---|---|---|---|---|---|');
    for (const m of [...MAPS, 'all']) if (eng[m]) L.push(`| ${m === 'all' ? '**all**' : m} | ${eng[m].games} | ${eng[m].F} | ${eng[m].S} | ${eng[m].none} | ${pc(eng[m].shareS)} |`);
    L.push('');
  }

  L.push('## Sources and checks', '');
  L.push('| set | games (top 6 / DEV) | skipped | no replay | ledger | endgame (legacy cache / system-report cache / computed now) | ledger checks | endgame checks | E= labels |', '|---|---|---|---|---|---|---|---|---|');
  for (const s of [...A.sources, ...(B ? B.sources : [])]) {
    const bad = o => { const x = Object.entries(o).filter(([, v]) => v); return x.length ? x.map(([k, v]) => `${k} ${v}`).join(', ') : 'all 0'; };
    L.push(`| ${s.set} | ${s.games} (${s.top6} / ${s.dev}) | ${s.skipped} | ${s.noReplay} | ${s.ledger} | ${s.endgame} (${s.endgameFrom.legacy} / ${s.endgameFrom.own} / ${s.endgameFrom.computed}) | ${bad(s.ledgerChecks)} | ${bad(s.endgameChecks)} | ${s.labelled === null ? '–' : s.labelled ? 'yes' : 'no'} |`);
  }
  if (rep.notes.length) { L.push(''); for (const n of rep.notes) L.push(`- ${n}`); }
  L.push('');
  return L.join('\n');
}

// ---------------------------------------------------------------------------------------------------------------
function main() {
  const argv = process.argv.slice(2);
  const opt = k => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : null; };
  const pos = []; for (let i = 0; i < argv.length; i++) { if (argv[i] === '--no-extract') continue; if (argv[i].startsWith('--')) { i++; continue; } pos.push(argv[i]); }
  if (!pos.length) { console.error('usage: node eval/system_report.js <set>[+<set>...] [--vs <set>[+<set>...]] [--name N] [--vs-name N] [--out f.md] [--json f.json] [--no-extract]'); process.exit(2); }
  const opts = { noExtract: argv.includes('--no-extract') };
  if (opt('--online')) ONLINE = path.resolve(opt('--online'));
  const split = s => s.split('+').map(x => x.trim()).filter(Boolean);
  const pool = pos.flatMap(split), vs = opt('--vs') ? split(opt('--vs')) : null, notes = [];
  const A = build(pool, opts, notes), B = vs ? build(vs, opts, notes) : null;
  const rep = { name: opt('--name') || pool.join(' + '), vsName: vs ? opt('--vs-name') || vs.join(' + ') : null, generated: new Date().toLocaleString('sv-SE', { timeZone: 'Asia/Seoul' }) + ' KST', pool: A, vsPool: B, notes };
  rep.compare = B ? compare(A, B) : null;
  rep.power = B ? powerTable(A.outcome.top6.all.n, B.outcome.top6.all.W, B.outcome.top6.all.n) : powerTable(A.outcome.top6.all.n, BASELINE.W, BASELINE.n);
  const md = markdown(rep);
  const out = opt('--out'), js = opt('--json');
  if (out) { fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true }); fs.writeFileSync(out, md); console.error(`wrote ${out}`); } else process.stdout.write(md);
  if (js) {
    const strip = P => P && { sets: P.sets, names: P.names, outcome: P.outcome, indicators: P.indicators, engine: P.engine, sources: P.sources };
    fs.mkdirSync(path.dirname(path.resolve(js)), { recursive: true });
    fs.writeFileSync(js, JSON.stringify({ name: rep.name, vsName: rep.vsName, generated: rep.generated, pool: strip(A), vs: strip(B), compare: rep.compare, power: rep.power, notes }, null, 1));
    console.error(`wrote ${js}`);
  }
}
if (require.main === module) main();
module.exports = { wilson, newcombe, fisher, power, critical, countLabels, readSet, build };
