#!/usr/bin/env node
// Portals elite comparison (exp/portals step 1c). Reads the mass-ledger caches only (no games, no replays):
//   .cache/mass-ledger/top-sample.jsonl            top-vs-top games (rating >= 1900 teams)
//   .cache/mass-ledger/online-<set>.jsonl          our W0-W12 wave sets (our side = the line's `us`)
// Portals is solitaire (the two halves are disconnected: 240 / 240 tiles, no path), so each team-game is one sample of
// "how long a king this team grows on its own half". Games with a stalled team (>= 100 rounds, no sonar ping and <= 3
// splits for a team; exp/map-atlas rule) are dropped.
// Bands over the elite pool, by king500 (st.king[50]): top decile (>= P90), median band (P40..P60), bottom quartile (<= P25).
// usage: node exp/portals/analysis/elite/elite.js [--out exp/portals/analysis/elite/elite.json] > table.txt
'use strict';
const fs = require('fs'), path = require('path'), readline = require('readline');
const ROOT = path.resolve(__dirname, '../../../..');
const { FI, ORIG, CAUSE } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const CACHE = path.join(ROOT, '.cache/mass-ledger');
const OUT = path.resolve(ROOT, (() => { const i = process.argv.indexOf('--out'); return i > 0 ? process.argv[i + 1] : 'exp/portals/analysis/elite/elite.json'; })());

const WAVES = [ // KNOWLEDGE.md §1
  ['W0', 'cand-merge2-online'], ['W0', 'cand-merge2-online-r2'], ['W0', 'cand-merge2-online-r3'],
  ['W1', 'cand-stack1-online'], ['W2', 'cand-stack2-online'], ['W3', 'cand-stack3-online'], ['W4', 'cand-stack4-online'],
  ['W5', 'cand-stack5-online'], ['W6', 'cand-stack6-online'], ['W7', 'cand-stack6-online-r2'], ['W8', 'cand-stack7-online'],
  ['W9', 'cand-stack8-online'], ['W10', 'cand-stack9-online'], ['W11', 'cand-stack10-online'], ['W12', 'cand-stack11-online'],
];
const eraOf = w => { const n = +w.slice(1); return n <= 4 ? 'W0-W4' : n <= 9 ? 'W5-W9' : 'W10-W12'; };
const TOP6 = new Set([306, 70, 20, 801, 264, 46]);
const TOP6_NAMES = new Set(['forgot to mention', 'cheji bt', 'Cutlery', 'calc', '中国必须人能飞😡', 'Sabotage-d']);

const NB = 50;
const sumBins = (arr, a, b) => { let s = 0; for (let i = a; i <= b && i < arr.length; i++) s += arr[i]; return s; };
const OWN = ['oSac', 'oTrap', 'oRammed', 'oRam', 'oOther'], ENEMY = ['eSac', 'eTrap', 'eRammed', 'eRam', 'eOther'];

// one team-game -> feature record
function feat(g, tm, meta) {
  const T = g[tm], st = T.st, fl = T.fl, dt = T.dt, lin = T.lin;
  const bin = k => fl[FI[k]];
  const r = {
    ...meta, key: g.key, team: tm, rounds: g.rounds,
    k500: st.king[50], units: st.units.slice(), total: st.total.slice(), king: st.king.slice(), second: st.second.slice(),
  };
  r.conv = st.total[40] > 0 ? st.king[50] / st.total[40] : null;
  // king eats per 10-round bin by origin group
  r.keatNat = bin('keat_nat').slice();
  r.keatSac = bin('keat_oSac').slice();
  r.keatTrap = bin('keat_oTrap').slice();
  r.keatOwnOther = new Array(NB).fill(0); for (const o of ['oRammed', 'oRam', 'oOther']) bin('keat_' + o).forEach((v, i) => r.keatOwnOther[i] += v);
  r.keatEnemy = new Array(NB).fill(0); for (const o of ENEMY) bin('keat_' + o).forEach((v, i) => r.keatEnemy[i] += v);
  r.eatNat = bin('eat_nat').slice();
  r.eatOwn = new Array(NB).fill(0); for (const o of OWN) bin('eat_' + o).forEach((v, i) => r.eatOwn[i] += v);
  // deaths per bin
  for (const c of CAUSE) { r['dn_' + c] = bin('dn_' + c).slice(); r['dl_' + c] = bin('dl_' + c).slice(); }
  r.split_n = bin('split_n').slice(); r.split_child = bin('split_child').slice(); r.split_stub = bin('split_stub').slice();
  r.kd_n = bin('kd_n').slice(); r.kd_len = bin('kd_len').slice();
  r.spr_n = bin('spr_n').slice();
  // death records (aggregated): cause|lenClass|phase|king|near|kdist|mech|blk -> [n, len, drops, eatOwn, eatOwnKing, eatEnemy, delaySumOwn, eatOwnBig]
  r.dt = dt;
  // lineage
  r.lin = lin ? { len: lin.len, gen: lin.gen, born: lin.born, cp: lin.cp } : null;
  r.sonar = T.sonar; r.splits = T.splits;
  return r;
}
const stalled = (g, tm) => g.rounds >= 100 && g[tm].sonar === 0 && g[tm].splits <= 3;

async function readLines(file, filter, fn) {
  const rl = readline.createInterface({ input: fs.createReadStream(file), crlfDelay: Infinity });
  for await (const l of rl) { if (!l || !filter(l)) continue; fn(JSON.parse(l)); }
}

// ---------------------------------------------------------------------------------------------------------------
// statistics helpers
const q = (xs, p) => { const a = xs.filter(x => x !== null && x !== undefined && !Number.isNaN(x)).sort((u, v) => u - v); if (!a.length) return null; const i = (a.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return a[lo] + (a[hi] - a[lo]) * (i - lo); };
const mean = xs => { const a = xs.filter(x => x !== null && x !== undefined && !Number.isNaN(x)); return a.length ? a.reduce((s, x) => s + x, 0) / a.length : null; };
const nOk = xs => xs.filter(x => x !== null && x !== undefined && !Number.isNaN(x)).length;
const f1 = x => x === null || x === undefined ? '–' : (Math.abs(x) >= 100 ? x.toFixed(0) : x.toFixed(1));
const f2 = x => x === null || x === undefined ? '–' : x.toFixed(2);
const pct = x => x === null || x === undefined ? '–' : (100 * x).toFixed(0) + '%';

// onset: the round by which frac of the r300-499 length in `bins` happened (10-round bins, linear inside a bin)
function onset(bins, frac, from = 30) {
  const tot = sumBins(bins, from, NB - 1); if (tot <= 0) return null;
  let c = 0;
  for (let b = from; b < NB; b++) { const v = bins[b]; if (c + v >= frac * tot) return 10 * b + 10 * (frac * tot - c) / v; c += v; }
  return 500;
}
// dt helpers
const dtSum = (dt, pred, idx) => { let s = 0; for (const [k, v] of Object.entries(dt)) { const [cause, lc, ph, king, near, kdist, mech, blk] = k.split('|'); if (pred({ cause, lc, ph, king, near, kdist, mech, blk })) s += v[idx]; } return s; };

function bandStats(rs) {
  const o = { n: rs.length };
  const at = (arr, i) => arr[i];
  // 1. head curve (st every 10 rounds; r25 = mean of r20 and r30)
  const unitsAt = r => r.units;
  const HC = { r10: 1, r25: 2.5, r50: 5, r100: 10, r150: 15, r200: 20, r250: 25, r300: 30, r350: 35, r400: 40, r450: 45, r490: 49 };
  o.units = {}; for (const [k, i] of Object.entries(HC)) { const v = rs.map(r => Number.isInteger(i) ? r.units[i] : (r.units[Math.floor(i)] + r.units[Math.ceil(i)]) / 2); o.units[k] = { mean: mean(v), med: q(v, 0.5), n: nOk(v) }; }
  // 2. mass, king, second
  o.total = {}; for (const [k, i] of Object.entries({ r100: 10, r250: 25, r300: 30, r350: 35, r400: 40, r450: 45, r500: 50 })) { const v = rs.map(r => r.total[i]); o.total[k] = { mean: mean(v), med: q(v, 0.5), n: nOk(v) }; }
  o.king = {}; o.second = {};
  for (const [k, i] of Object.entries({ r250: 25, r300: 30, r350: 35, r400: 40, r450: 45, r470: 47, r500: 50 })) {
    const v = rs.map(r => r.king[i]), s = rs.map(r => r.second[i]);
    o.king[k] = { mean: mean(v), med: q(v, 0.5), n: nOk(v) }; o.second[k] = { mean: mean(s), med: q(s, 0.5), n: nOk(s) };
  }
  o.k500 = { mean: mean(rs.map(r => r.k500)), med: q(rs.map(r => r.k500), 0.5), p25: q(rs.map(r => r.k500), 0.25), p75: q(rs.map(r => r.k500), 0.75), n: rs.length };
  // king curve every 20 rounds from r200 (median, P25, P75) and the king's share of the team mass
  o.kingCurve = {}; for (let i = 20; i <= 50; i += 2) { const v = rs.map(r => r.king[i]); o.kingCurve['r' + 10 * i] = { p25: q(v, 0.25), med: q(v, 0.5), p75: q(v, 0.75) }; }
  o.kingShare = {}; for (const i of [25, 30, 35, 40, 45]) o.kingShare['r' + 10 * i] = q(rs.map(r => r.total[i] > 0 ? r.king[i] / r.total[i] : null), 0.5);
  const cv = rs.map(r => r.conv);
  o.conv = { mean: mean(cv), med: q(cv, 0.5), n: nOk(cv) };
  // 3. conversion flows: king eats by origin in 50-round windows, sacrifice deaths per 50-round window, onsets
  const W50 = [[20, 24, 'r200-249'], [25, 29, 'r250-299'], [30, 34, 'r300-349'], [35, 39, 'r350-399'], [40, 44, 'r400-449'], [45, 49, 'r450-499']];
  o.keat = {};
  for (const [a, b, name] of W50) {
    o.keat[name] = {
      nat: mean(rs.map(r => sumBins(r.keatNat, a, b))), sac: mean(rs.map(r => sumBins(r.keatSac, a, b))), trap: mean(rs.map(r => sumBins(r.keatTrap, a, b))),
      ownOther: mean(rs.map(r => sumBins(r.keatOwnOther, a, b))), enemy: mean(rs.map(r => sumBins(r.keatEnemy, a, b))),
      teamNat: mean(rs.map(r => sumBins(r.eatNat, a, b))), teamOwn: mean(rs.map(r => sumBins(r.eatOwn, a, b))), n: rs.length,
    };
  }
  o.deaths = {};
  for (const [a, b, name] of W50) {
    o.deaths[name] = {
      sacN: mean(rs.map(r => sumBins(r.dn_sac, a, b))), sacL: mean(rs.map(r => sumBins(r.dl_sac, a, b))),
      trapN: mean(rs.map(r => sumBins(r.dn_trap, a, b))), trapL: mean(rs.map(r => sumBins(r.dl_trap, a, b))),
      allOwnL: mean(rs.map(r => CAUSE.reduce((s, c) => s + sumBins(r['dl_' + c], a, b), 0))), n: rs.length,
    };
  }
  const selfL = r => r.dl_sac.map((v, i) => v + r.dl_trap[i]);
  o.onsetSac = { p20: q(rs.map(r => onset(r.dl_sac, 0.2)), 0.5), p50: q(rs.map(r => onset(r.dl_sac, 0.5)), 0.5), p80: q(rs.map(r => onset(r.dl_sac, 0.8)), 0.5), n: nOk(rs.map(r => onset(r.dl_sac, 0.5))) };
  o.onsetSelf = { p20: q(rs.map(r => onset(selfL(r), 0.2)), 0.5), p50: q(rs.map(r => onset(selfL(r), 0.5)), 0.5), p80: q(rs.map(r => onset(selfL(r), 0.8)), 0.5), n: nOk(rs.map(r => onset(selfL(r), 0.5))) };
  // king eats of own drops: onset of the r300-499 own-drop eats by the king
  const kOwn = r => r.keatSac.map((v, i) => v + r.keatTrap[i] + r.keatOwnOther[i]);
  o.onsetKingOwnEat = { p20: q(rs.map(r => onset(kOwn(r), 0.2)), 0.5), p50: q(rs.map(r => onset(kOwn(r), 0.5)), 0.5), p80: q(rs.map(r => onset(kOwn(r), 0.8)), 0.5), n: nOk(rs.map(r => onset(kOwn(r), 0.5))) };
  // sacrifice length classes and placement (dt, phases p2 = r250-349, p3 = r350-449, p4 = r450-499)
  const late = x => x.ph === 'p2' || x.ph === 'p3' || x.ph === 'p4';
  const sac = x => x.cause === 'sac', self = x => x.cause === 'sac' || x.cause === 'trap';
  o.sacLen = {};
  for (const lc of ['2', '3', '4', '5-7', '8-14', '15+']) o.sacLen[lc] = mean(rs.map(r => dtSum(r.dt, x => sac(x) && late(x) && x.lc === lc, 0)));
  o.selfLen = {};
  for (const lc of ['2', '3', '4', '5-7', '8-14', '15+']) o.selfLen[lc] = mean(rs.map(r => dtSum(r.dt, x => self(x) && late(x) && x.lc === lc, 0)));
  const place = pred => {
    const drops = rs.map(r => dtSum(r.dt, x => pred(x) && late(x), 2));
    const n = rs.map(r => dtSum(r.dt, x => pred(x) && late(x), 0));
    const k3 = rs.map(r => dtSum(r.dt, x => pred(x) && late(x) && x.kdist === 'k3', 0));
    const k8 = rs.map(r => dtSum(r.dt, x => pred(x) && late(x) && x.kdist === 'k8', 0));
    const nearB = rs.map(r => dtSum(r.dt, x => pred(x) && late(x) && x.near === 'B', 0));
    const eatOwn = rs.map(r => dtSum(r.dt, x => pred(x) && late(x), 3));
    const eatKing = rs.map(r => dtSum(r.dt, x => pred(x) && late(x), 4));
    const eatBig = rs.map(r => dtSum(r.dt, x => pred(x) && late(x), 7));
    const eatEnemy = rs.map(r => dtSum(r.dt, x => pred(x) && late(x), 5));
    const delay = rs.map(r => dtSum(r.dt, x => pred(x) && late(x), 6));
    const S = a => a.reduce((s, x) => s + x, 0);
    return { deathsPerGame: mean(n), dropsPerGame: mean(drops), k3Share: S(k3) / Math.max(1, S(n)), k8Share: S(k8) / Math.max(1, S(n)), nearBShare: S(nearB) / Math.max(1, S(n)),
      ownEatenShare: S(eatOwn) / Math.max(1, S(drops)), kingEatenShare: S(eatKing) / Math.max(1, S(drops)), bigEatenShare: S(eatBig) / Math.max(1, S(drops)), enemyEatenShare: S(eatEnemy) / Math.max(1, S(drops)),
      meanDelay: S(delay) / Math.max(1, S(eatOwn)) };
  };
  o.placeSac = place(sac); o.placeSelf = place(self);
  // 4. splits per phase
  const PH = [[0, 9, 'r0-99'], [10, 24, 'r100-249'], [25, 34, 'r250-349'], [35, 44, 'r350-449'], [45, 49, 'r450-499']];
  o.splits = {};
  for (const [a, b, name] of PH) {
    const n = rs.map(r => sumBins(r.split_n, a, b)), ch = rs.map(r => sumBins(r.split_child, a, b)), stub = rs.map(r => sumBins(r.split_stub, a, b));
    o.splits[name] = { n: mean(n), childLen: mean(ch) / Math.max(1e-9, mean(n)), stub: mean(stub) };
  }
  // 5. king deaths, mass lost after r300 by cause
  o.kingDeaths = { perGame: mean(rs.map(r => sumBins(r.kd_n, 0, NB - 1))), after300: mean(rs.map(r => sumBins(r.kd_n, 30, NB - 1))), lenMean: (() => { const n = rs.reduce((s, r) => s + sumBins(r.kd_n, 0, NB - 1), 0), l = rs.reduce((s, r) => s + sumBins(r.kd_len, 0, NB - 1), 0); return n ? l / n : null; })() };
  o.kingDeathCause = {}; for (const c of CAUSE) o.kingDeathCause[c] = mean(rs.map(r => dtSum(r.dt, x => x.king === '1' && x.cause === c, 0)));
  o.gamesWithKingDeath = rs.filter(r => sumBins(r.kd_n, 0, NB - 1) > 0).length / Math.max(1, rs.length);
  o.lossAfter300 = {}; for (const c of CAUSE) o.lossAfter300[c] = mean(rs.map(r => sumBins(r['dl_' + c], 30, NB - 1)));
  // 6. final-king lineage
  const L = rs.filter(r => r.lin);
  o.lin = { n: L.length, gen: q(L.map(r => r.lin.gen), 0.5), born: q(L.map(r => r.lin.born), 0.5), bornMean: mean(L.map(r => r.lin.born)), cp: {} };
  for (const t of [300, 350, 400, 450]) {
    const C = L.filter(r => r.lin.cp && r.lin.cp[t]).map(r => r.lin.cp[t]);
    const e = i => mean(C.map(c => c.eat[i]));
    const own = mean(C.map(c => c.eat.slice(1, 6).reduce((s, v) => s + v, 0))), en = mean(C.map(c => c.eat.slice(6).reduce((s, v) => s + v, 0)));
    o.lin.cp[t] = { n: C.length, Lt: mean(C.map(c => c.Lt)), LtMed: q(C.map(c => c.Lt), 0.5), nat: e(0), sac: e(1), trap: e(2), own, enemy: en,
      cost: mean(C.map(c => c.cost)), lossOff: mean(C.map(c => c.lossOff)), lossPath: mean(C.map(c => c.lossPath)), transfers: mean(C.map(c => c.transfers)), wasKing: mean(C.map(c => c.wasKing)) };
  }
  return o;
}

// ---------------------------------------------------------------------------------------------------------------
(async () => {
  const elite = [], dropped = { games: 0, stalledGames: 0 }, perTeam = {};
  await readLines(path.join(CACHE, 'top-sample.jsonl'), l => l.includes('"map":"Portals"'), g => {
    if (g.map !== 'Portals') return;
    dropped.games++;
    if (stalled(g, 'A') || stalled(g, 'B')) { dropped.stalledGames++; return; }
    for (const tm of ['A', 'B']) {
      const name = tm === 'A' ? g.teamA : g.teamB, elo = tm === 'A' ? g.eloA : g.eloB;
      elite.push(feat(g, tm, { src: 'top', name, elo, won: g.winnerIdx === tm, top6: TOP6_NAMES.has(name) }));
    }
  });
  const ours = [];
  for (const [w, set] of WAVES) {
    const f = path.join(CACHE, 'online-' + set + '.jsonl'); if (!fs.existsSync(f)) { console.error('missing', f); continue; }
    await readLines(f, l => l.includes('"map":"Portals"'), g => {
      if (g.map !== 'Portals' || !g.us) return;
      ours.push(feat(g, g.us, { src: 'ours', set, wave: w, era: eraOf(w), opp: g.oppId, won: g.winnerIdx === g.us, top6opp: TOP6.has(g.oppId) }));
    });
  }
  // bands
  const ks = elite.map(r => r.k500);
  const P = { p10: q(ks, 0.1), p25: q(ks, 0.25), p40: q(ks, 0.4), p50: q(ks, 0.5), p60: q(ks, 0.6), p75: q(ks, 0.75), p90: q(ks, 0.9) };
  const bands = {
    'top decile': elite.filter(r => r.k500 >= P.p90),
    'median band': elite.filter(r => r.k500 >= P.p40 && r.k500 <= P.p60),
    'bottom quartile': elite.filter(r => r.k500 <= P.p25),
    'all elite': elite,
    'top-6 teams': elite.filter(r => r.top6),
    'ours W0-W4': ours.filter(r => r.era === 'W0-W4'),
    'ours W5-W9': ours.filter(r => r.era === 'W5-W9'),
    'ours W10-W12': ours.filter(r => r.era === 'W10-W12'),
    'ours all': ours,
  };
  const stats = {}; for (const [k, rs] of Object.entries(bands)) stats[k] = bandStats(rs);
  // per-team king500 on Portals (elite), for context
  const byTeam = {};
  for (const r of elite) (byTeam[r.name] = byTeam[r.name] || []).push(r.k500);
  const teamRows = Object.entries(byTeam).filter(([, v]) => v.length >= 20).map(([n, v]) => ({ name: n, n: v.length, med: q(v, 0.5), p25: q(v, 0.25), p75: q(v, 0.75), top6: TOP6_NAMES.has(n) })).sort((a, b) => b.med - a.med);
  // candidates for replay pictures: top-decile team-games of 500 rounds, nearest to the band's median profile (king400, total400, units300)
  const td = stats['top decile'];
  const cand = bands['top decile'].filter(r => r.rounds === 500).map(r => ({ key: r.key, team: r.team, name: r.name, k500: r.k500, k400: r.king[40], t400: r.total[40], u300: r.units[30],
    d: Math.abs(r.king[40] - td.king.r400.med) / 5 + Math.abs(r.total[40] - td.total.r400.med) / 10 + Math.abs(r.units[30] - td.units.r300.med) / 5 })).sort((a, b) => a.d - b.d).slice(0, 12);
  const out = { at: new Date().toISOString(), population: { portalsGames: dropped.games, stalledGamesDropped: dropped.stalledGames, eliteTeamGames: elite.length, oursTeamGames: ours.length }, thresholds: P,
    stats, teamRows, pictureCandidates: cand,
    oursGames: ours.map(r => ({ key: r.key, wave: r.wave, opp: r.opp, k500: r.k500, t400: r.total[40], conv: r.conv, kd: sumBins(r.kd_n, 0, NB - 1), won: r.won })) };
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(out, null, 1));

  // ---- tables
  const cols = ['top decile', 'median band', 'bottom quartile', 'top-6 teams', 'ours W0-W4', 'ours W5-W9', 'ours W10-W12'];
  const hdr = '| | ' + cols.map(c => `${c} [N ${stats[c].n}]`).join(' | ') + ' |\n|' + '---|'.repeat(cols.length + 1);
  const row = (label, fn) => '| ' + label + ' | ' + cols.map(c => fn(stats[c])).join(' | ') + ' |';
  const L = [];
  L.push(`Population: Portals games in top-sample ${dropped.games}, stalled dropped ${dropped.stalledGames}, elite team-games ${elite.length}; ours ${ours.length} team-games (W0-W12).`);
  L.push(`Elite king500 quantiles: P10 ${P.p10} P25 ${P.p25} P40 ${P.p40} P50 ${P.p50} P60 ${P.p60} P75 ${P.p75} P90 ${P.p90}`);
  L.push('\n### 0. Outcome'); L.push(hdr);
  L.push(row('king500 median (P25–P75)', s => `${f1(s.k500.med)} (${f1(s.k500.p25)}–${f1(s.k500.p75)})`));
  L.push(row('conversion king500 / r400 total, median', s => f2(s.conv.med)));
  L.push('\n### 0b. King curve (median [P25-P75]) and king share of team mass (median)'); L.push(hdr);
  for (const k of Object.keys(stats['top decile'].kingCurve)) L.push(row('king ' + k, s => `${f1(s.kingCurve[k].med)} [${f1(s.kingCurve[k].p25)}-${f1(s.kingCurve[k].p75)}]`));
  for (const k of Object.keys(stats['top decile'].kingShare)) L.push(row('king / total ' + k, s => pct(s.kingShare[k])));
  L.push('\n### 1. Head curve (living units; mean, r25 = mean of r20 and r30)'); L.push(hdr);
  for (const k of Object.keys(stats['top decile'].units)) L.push(row(k, s => f1(s.units[k].mean)));
  L.push('\n### 2. Mass (mean total length) and king / second (median)'); L.push(hdr);
  for (const k of Object.keys(stats['top decile'].total)) L.push(row('total ' + k, s => f1(s.total[k].mean)));
  for (const k of Object.keys(stats['top decile'].king)) L.push(row('king ' + k + ' (med)', s => f1(s.king[k].med)));
  for (const k of Object.keys(stats['top decile'].second)) L.push(row('second ' + k + ' (med)', s => f1(s.second[k].med)));
  L.push('\n### 3a. King eats per game by window: natural / own sacrifice drops / own trap drops / other own / enemy (mean)'); L.push(hdr);
  for (const k of Object.keys(stats['top decile'].keat)) L.push(row(k, s => `${f1(s.keat[k].nat)} / ${f1(s.keat[k].sac)} / ${f1(s.keat[k].trap)} / ${f1(s.keat[k].ownOther)} / ${f1(s.keat[k].enemy)}`));
  L.push(row('team eats nat / own drops r300-349', s => `${f1(s.keat['r300-349'].teamNat)} / ${f1(s.keat['r300-349'].teamOwn)}`));
  L.push(row('team eats nat / own drops r350-399', s => `${f1(s.keat['r350-399'].teamNat)} / ${f1(s.keat['r350-399'].teamOwn)}`));
  L.push(row('team eats nat / own drops r400-449', s => `${f1(s.keat['r400-449'].teamNat)} / ${f1(s.keat['r400-449'].teamOwn)}`));
  L.push(row('team eats nat / own drops r450-499', s => `${f1(s.keat['r450-499'].teamNat)} / ${f1(s.keat['r450-499'].teamOwn)}`));
  L.push('\n### 3b. Own deaths per game by window: sacrifices n / length, traps n / length, all own death length (mean)'); L.push(hdr);
  for (const k of Object.keys(stats['top decile'].deaths)) L.push(row(k, s => `${f1(s.deaths[k].sacN)}/${f1(s.deaths[k].sacL)} · ${f1(s.deaths[k].trapN)}/${f1(s.deaths[k].trapL)} · ${f1(s.deaths[k].allOwnL)}`));
  L.push(row('sac length 20/50/80% round (r300-499, median)', s => `${f1(s.onsetSac.p20)}/${f1(s.onsetSac.p50)}/${f1(s.onsetSac.p80)} [${s.onsetSac.n}]`));
  L.push(row('sac+trap length 20/50/80% round', s => `${f1(s.onsetSelf.p20)}/${f1(s.onsetSelf.p50)}/${f1(s.onsetSelf.p80)} [${s.onsetSelf.n}]`));
  L.push(row('king own-drop eats 20/50/80% round', s => `${f1(s.onsetKingOwnEat.p20)}/${f1(s.onsetKingOwnEat.p50)}/${f1(s.onsetKingOwnEat.p80)} [${s.onsetKingOwnEat.n}]`));
  L.push('\n### 3c. Sacrifice length class, r250-499 (sac deaths per game, mean)'); L.push(hdr);
  for (const lc of ['2', '3', '4', '5-7', '8-14', '15+']) L.push(row('L ' + lc, s => f1(s.sacLen[lc])));
  L.push('\n### 3d. Placement of r250-499 sacrifices (sac) / sac+trap'); L.push(hdr);
  for (const [k, lab] of [['deathsPerGame', 'deaths per game'], ['dropsPerGame', 'drops per game']]) L.push(row(lab, s => `${f1(s.placeSac[k])} / ${f1(s.placeSelf[k])}`));
  for (const [k, lab] of [['k3Share', 'within Manhattan 3 of the longest other (k3)'], ['k8Share', 'within 4-8 (k8)'], ['nearBShare', 'an ally head >= 8 within 3 (near B)'], ['ownEatenShare', 'drops eaten by own team'], ['kingEatenShare', 'drops eaten by the king'], ['bigEatenShare', 'drops eaten by own L>=8'], ['enemyEatenShare', 'drops eaten by enemy']])
    L.push(row(lab, s => `${pct(s.placeSac[k])} / ${pct(s.placeSelf[k])}`));
  L.push(row('mean rounds from drop to own eat', s => `${f1(s.placeSac.meanDelay)} / ${f1(s.placeSelf.meanDelay)}`));
  L.push('\n### 4. Splits per game by phase: count (mean child length)'); L.push(hdr);
  for (const k of Object.keys(stats['top decile'].splits)) L.push(row(k, s => `${f1(s.splits[k].n)} (${f1(s.splits[k].childLen)})`));
  L.push('\n### 5. King deaths (longest living, L >= 8) and mass lost after r300'); L.push(hdr);
  L.push(row('king deaths per game (after r300)', s => `${f2(s.kingDeaths.perGame)} (${f2(s.kingDeaths.after300)})`));
  L.push(row('games with a king death', s => pct(s.gamesWithKingDeath)));
  L.push(row('mean length of a dying king', s => f1(s.kingDeaths.lenMean)));
  for (const c of ['sac', 'trap', 'allyHead', 'rammed', 'ram', 'enemyBody', 'fault', 'sprintDeath']) L.push(row('king deaths by ' + c, s => f2(s.kingDeathCause[c])));
  for (const c of ['sac', 'trap', 'allyHead', 'fault', 'sprintDeath']) L.push(row('length lost r300-499: ' + c, s => f1(s.lossAfter300[c])));
  L.push('\n### 6. Final-king lineage (from checkpoint t: ancestor length Lt, eats nat / own drops (sac, trap) / enemy, minus sprint cost, split-offs, path loss)'); L.push(hdr);
  L.push(row('generations (median) · final king born (median round)', s => `${f1(s.lin.gen)} · r${f1(s.lin.born)}`));
  for (const t of [300, 350, 400, 450]) {
    L.push(row(`t=${t}: Lt mean (med)`, s => s.lin.cp[t] ? `${f1(s.lin.cp[t].Lt)} (${f1(s.lin.cp[t].LtMed)})` : '–'));
    L.push(row(`t=${t}: +nat +own(sac,trap) +enemy`, s => s.lin.cp[t] ? `+${f1(s.lin.cp[t].nat)} +${f1(s.lin.cp[t].own)}(${f1(s.lin.cp[t].sac)},${f1(s.lin.cp[t].trap)}) +${f1(s.lin.cp[t].enemy)}` : '–'));
    L.push(row(`t=${t}: −cost −off −path · transfers · was king`, s => s.lin.cp[t] ? `−${f1(s.lin.cp[t].cost)} −${f1(s.lin.cp[t].lossOff)} −${f1(s.lin.cp[t].lossPath)} · ${f1(s.lin.cp[t].transfers)} · ${pct(s.lin.cp[t].wasKing)}` : '–'));
  }
  L.push('\n### Teams (elite, >= 20 Portals team-games): king500 median (P25–P75)');
  for (const t of teamRows.slice(0, 40)) L.push(`- ${t.name}${t.top6 ? ' [top6]' : ''}: ${t.med} (${t.p25}–${t.p75}) N ${t.n}`);
  L.push('\n### Picture candidates (top decile, nearest the band profile)');
  for (const c of cand) L.push(`- ${c.key} team ${c.team} (${c.name}): k500 ${c.k500}, king400 ${c.k400}, total400 ${c.t400}, units300 ${c.u300}`);
  console.log(L.join('\n'));
})();
