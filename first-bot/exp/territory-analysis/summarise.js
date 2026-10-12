// summarise.js — per team-game summaries from exp/territory-analysis/cache/*.jsonl.gz (written by extract.js).
// Used by report.js and examples.js. Reads the cache only (no replays, no network). Streams the gzip files and keeps only
// aggregated numbers per team-game (raid episodes as histograms plus a few pointer rows).
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), readline = require('readline');
const ROOT = path.resolve(__dirname, '..', '..');
const CACHE = path.join(__dirname, 'cache');
const INF = 999;
const ELIM = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default'];
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
// every online set against the elite (user rule 2026-09-30 11:17): our bot name per set
const SETS = { 'baseline-r1': 'g4r4', 'baseline-r1b': 'g4r4', 'baseline-r1c': 'g4r4', 'cand-avoid6-online': 'avoid6', 'cand-portal1-online': 'portal1',
  'cand-merge2-online': 'merge2', 'cand-merge2-online-r2': 'merge2', 'cand-merge2-online-r3': 'merge2', 'cand-swarm8-online': 'swarm8',
  'base-px8-online': 'px8', 'base-px9d-online': 'px9d', 'px-king-v2-online': 'pxking' };
const BOTS = ['g4r4', 'avoid6', 'portal1', 'merge2', 'swarm8', 'px8', 'px9d', 'pxking'];
const T7 = new Set(['Cutlery', 'cheji bt', 'calc', '中国必须人能飞😡', 'forgot to mention', 'Sabotage-d', 'dev test 1 :P']);

// pearl row fields (extract.js)
const PR = { r: 0, k: 1, terr: 2, f: 3, m: 4, dA: 5, dB: 6, vA: 7, vB: 8, lA: 9, lB: 10, xA: 11, xB: 12, eater: 13, eatR: 14, eatLen: 15, eatAge: 16 };
// episode row fields
const ER = ['ti', 'id', 'r0', 'r1', 'L0', 'Lmax', 'L1', 'nat', 'fnt', 'drop', 'exit', 'cause', 'killer', 'killerLen', 'blkE', 'dmax', 'dDef0', 'dDefMin', 'nDef6', 'appr', 'retr', 'kills', 'trades', 'born', 'upd', 'fr', 'units', 'defUnits', 'dEnd'];
const EI = Object.fromEntries(ER.map((k, i) => [k, i]));
// coverage checkpoint fields
const CI = { r: 0, units: 1, total: 2, uOwn: 3, uEn: 4, vorOwn: 5, vorAll: 6, visOwn: 7, visEn: 8, near5: 9, vorEn: 10, fHeld: 11, fHeldEn: 12, fVor: 13, spacing: 14, near2: 15 };
const DB = ['≤-6', '-5..-3', '-2..-1', '0', '1..2', '3..5', '≥6', 'noEn', 'noOwn'];
const dBucket = (dO, dE) => {
  if (dO >= INF) return 8; if (dE >= INF) return 7;
  const x = dE - dO; return x <= -6 ? 0 : x <= -3 ? 1 : x <= -1 ? 2 : x === 0 ? 3 : x <= 2 ? 4 : x <= 5 ? 5 : 6;
};
const OB = ['≤1', '2-3', '4-6', '7-10', '11-20', '21+'];
const oBucket = d => d <= 1 ? 0 : d <= 3 ? 1 : d <= 6 ? 2 : d <= 10 ? 3 : d <= 20 ? 4 : 5;
const PH = [[0, 100], [100, 250], [250, 350], [350, 450], [450, 501]];
const PHN = ['r0-99', 'r100-249', 'r250-349', 'r350-449', 'r450+'];
const phaseOf = r => r < 100 ? 0 : r < 250 ? 1 : r < 350 ? 2 : r < 450 ? 3 : 4;
const DEP = ['1-2', '3-5', '6-10', '11+'];
const depBucket = m => m <= 2 ? 0 : m <= 5 ? 1 : m <= 10 ? 2 : 3;
const zeros = n => new Array(n).fill(0);
const contactKill = e => e[EI.exit] === 1 && e[EI.killer] === 2 && ([2, 3, 4].includes(e[EI.cause]) || (e[EI.cause] === 1 && e[EI.blkE]));

// aggregated raid episodes (deep = dmax >= 3)
function epAgg(eps) {
  const a = { n: 0, dur: 0, durH: zeros(62), L0H: zeros(22), LmaxH: zeros(22), born: 0, nat: 0, fnt: 0, drop: 0, fr: 0, upd: 0, exit: [0, 0, 0],
    dContact: 0, dSac: 0, dTrap: 0, dAlly: 0, dOther: 0, kills: 0, trades: 0, dDef0H: zeros(42), contact: 0, near6: 0, appr: 0, retr: 0,
    natH: zeros(12) };
  for (const e of eps) {
    a.n++; const d = e[EI.r1] - e[EI.r0] + 1; a.dur += d; a.durH[Math.min(61, d)]++;
    a.L0H[Math.min(21, e[EI.L0])]++; a.LmaxH[Math.min(21, e[EI.Lmax])]++;
    if (e[EI.born]) a.born++;
    a.nat += e[EI.nat]; a.fnt += e[EI.fnt]; a.drop += e[EI.drop]; a.fr += e[EI.fr]; a.upd += e[EI.upd]; a.natH[Math.min(11, e[EI.nat])]++;
    a.exit[e[EI.exit]]++;
    if (e[EI.exit] === 1) {
      if (contactKill(e)) a.dContact++;
      else if (e[EI.killer] === 1) a.dAlly++;
      else if (e[EI.cause] === 0) a.dSac++;
      else if (e[EI.cause] === 1) a.dTrap++;
      else a.dOther++;
    }
    a.kills += e[EI.kills]; a.trades += e[EI.trades];
    if (e[EI.dDef0] >= 0) a.dDef0H[Math.min(41, e[EI.dDef0])]++;
    if (e[EI.dDefMin] <= 1) a.contact++;
    if (e[EI.nDef6] > 0) a.near6++;
    a.appr += Math.max(0, e[EI.appr]); a.retr += Math.max(0, e[EI.retr]);
  }
  return a;
}
function epAddInto(t, a) { for (const [k, v] of Object.entries(a)) { if (Array.isArray(v)) { if (!t[k]) t[k] = zeros(v.length); for (let i = 0; i < v.length; i++) t[k][i] += v[i]; } else t[k] = (t[k] || 0) + v; } return t; }
const hMed = (h, p = 0.5) => { const tot = h.reduce((s, v) => s + v, 0); if (!tot) return NaN; let c = 0; for (let i = 0; i < h.length; i++) { c += h[i]; if (c >= p * tot) return i; } return h.length - 1; };

// summary of one team (ti) in one game
function teamSummary(g, ti) {
  const own = ti + 1, en = 2 - ti, T = ti === 0 ? g.A : g.B;
  const s = {
    // own-territory natural pearls (r >= 0): [spawned, ownEat, enemyEat, none] by delta bucket, by phase x fount, by own-distance bucket, by visibility
    byD: DB.map(() => zeros(4)), byDraid: DB.map(() => zeros(4)), byPF: PH.map(() => [zeros(4), zeros(4)]), byO: OB.map(() => zeros(4)), byVis: [zeros(4), zeros(4)],
    byDep: DEP.map(() => zeros(4)), byDF: [DB.map(() => zeros(4)), DB.map(() => zeros(4))], byDph: PH.map(() => DB.map(() => zeros(4))),
    enEatLen: zeros(4), enEatAge: zeros(5), // eater length class of enemy eats in our territory: 2-3, 4-7, 8-15, 16+; raid age: 0-2,3-9,10-29,30-99,100+
    neu: zeros(4), // neutral pearls: [spawned, ownEat, enemyEat, none]
    enT: zeros(4), // enemy-territory natural pearls from our side: [spawned there, we ate, fountain spawned there, we ate fountain]
    win50: Array.from({ length: 10 }, () => zeros(4)), // own-territory pearls by 50-round window: [spawned, own, enemy, none]
    ownSp: 0, ownEat: 0, enEat: 0, none: 0, fSp: 0, fOwn: 0, fEn: 0, latOwnSum: 0, latOwnN: 0, latEnSum: 0, latEnN: 0,
  };
  for (const p of g.P) {
    if (p[PR.r] < 0) continue;
    const t = p[PR.terr], eater = p[PR.eater];
    const res = eater === 0 ? 3 : eater === own ? 1 : 2;
    if (t === own) {
      const dO = ti === 0 ? p[PR.dA] : p[PR.dB], dE = ti === 0 ? p[PR.dB] : p[PR.dA];
      const vO = ti === 0 ? p[PR.vA] : p[PR.vB];
      const raidNear = ti === 0 ? p[PR.xB] : p[PR.xA]; // the nearest enemy head is inside our territory
      const b = dBucket(dO, dE), f = p[PR.f], ph = phaseOf(p[PR.r]);
      const dep = depBucket(ti === 0 ? p[PR.m] : -p[PR.m]);
      for (const a of [s.byD[b], s.byPF[ph][f], s.byO[oBucket(dO)], s.byVis[vO], s.byDep[dep], s.byDF[f][b], s.byDph[ph][b]]) { a[0]++; a[res]++; }
      if (raidNear) { s.byDraid[b][0]++; s.byDraid[b][res]++; }
      const w = Math.min(9, Math.floor(p[PR.r] / 50)); s.win50[w][0]++; s.win50[w][res]++;
      s.ownSp++; if (f) s.fSp++;
      if (res === 1) { s.ownEat++; if (f) s.fOwn++; s.latOwnSum += p[PR.eatR] - p[PR.r]; s.latOwnN++; }
      else if (res === 2) {
        s.enEat++; if (f) s.fEn++; s.latEnSum += p[PR.eatR] - p[PR.r]; s.latEnN++;
        const L = p[PR.eatLen]; s.enEatLen[L <= 3 ? 0 : L <= 7 ? 1 : L <= 15 ? 2 : 3]++;
        const a = p[PR.eatAge]; s.enEatAge[a < 0 ? 0 : a <= 2 ? 0 : a <= 9 ? 1 : a <= 29 ? 2 : a <= 99 ? 3 : 4]++;
      } else s.none++;
    } else if (t === 0) { s.neu[0]++; s.neu[res]++; }
    else if (t === en) { s.enT[0]++; if (res === 1) s.enT[1]++; if (p[PR.f]) { s.enT[2]++; if (res === 1) s.enT[3]++; } }
  }
  // raid episodes by this team (as raider) and against it (as defender): deep = 3+ steps past the border
  const mine = g.E.filter(e => e[EI.ti] === ti && e[EI.dmax] >= 3), theirs = g.E.filter(e => e[EI.ti] !== ti && e[EI.dmax] >= 3);
  s.epAllN = g.E.filter(e => e[EI.ti] === ti).length;
  s.raid = epAgg(mine); s.def = epAgg(theirs);
  // pointer rows: this team's two raids with the most natural pearls, and its raid killed by contact with the longest raider
  s.ptr = mine.slice().sort((a, b) => b[EI.nat] - a[EI.nat]).slice(0, 2);
  const kc = mine.filter(contactKill).sort((a, b) => b[EI.Lmax] - a[EI.Lmax]); if (kc.length) s.ptrKilled = kc[0];
  // coverage checkpoints, location bins, encounters
  s.C = g.C[ti]; s.LOC = g.LOC[ti]; s.ENC = g.ENC[ti];
  s.capOwn = g.capT[own]; s.capEn = g.capT[en]; s.capNeu = g.capT[0]; s.nFount = g.nFount[own]; s.nearFShareEn = g.nearFShare[en - 1]; s.terrTiles = g.terrTiles[own];
  // deaths of this team: counts by [relTerr][cause] and deaths by enemy contact by relTerr
  s.deaths = [0, 1, 2].map(() => zeros(8)); s.deathLen = [0, 1, 2].map(() => zeros(8));
  s.deathsEnemyKilled = zeros(3);
  for (const d of g.D) {
    if (d[0] !== ti) continue;
    s.deaths[d[4]][d[3]]++; s.deathLen[d[4]][d[3]] += d[2];
    const contact = d[5] === 2 && (d[3] === 2 || d[3] === 3 || d[3] === 4 || (d[3] === 1 && d[7]));
    if (contact) s.deathsEnemyKilled[d[4]]++;
  }
  s.team = { splits: T.splits, sonar: T.sonar, faults: T.faults, natOwn: T.natOwn, natEnemy: T.natEnemy, eatNat: T.eatNat, units: T.units, total: T.total, king: T.king };
  return s;
}

async function forEachGame(file, fn) {
  if (!fs.existsSync(file)) return;
  const gz = zlib.createGunzip();
  let failed = null;
  gz.on('error', e => { failed = e; gz.end(); });
  const rl = readline.createInterface({ input: fs.createReadStream(file).pipe(gz), crlfDelay: Infinity });
  try { for await (const l of rl) { if (!l.trim()) continue; let g; try { g = JSON.parse(l); } catch { continue; } fn(g); } }
  catch (e) { failed = e; }
  if (failed) console.error(`warning: ${path.basename(file)} read stopped early (${String(failed.message || failed).slice(0, 80)}); a file still being written ends with a partial member`);
}

// all team-games
async function load(opts = {}) {
  const topName = opts.top || 'top-all';
  const keep = opts.keys ? new Set(fs.readFileSync(path.resolve(ROOT, opts.keys), 'utf8').split('\n').map(x => x.trim()).filter(Boolean)) : null;
  const TG = [], excluded = { inactive: 0, fault: 0, draw: 0, dup: 0 }, chkSum = {}, seen = new Set(), nGames = { top: 0, online: 0 };
  const inactive = T => T.splits <= 3 && T.sonar === 0;
  const files = [[path.join(CACHE, topName + '.jsonl.gz'), 'top']];
  if (!opts.noOnline) for (const s of Object.keys(SETS)) files.push([path.join(CACHE, 'online-' + s + '.jsonl.gz'), 'online']);
  for (const [file, src] of files) {
    await forEachGame(file, g => {
      if (src === 'top' && keep && !keep.has(g.key)) return;
      if (seen.has(g.key)) { excluded.dup++; return; }
      seen.add(g.key);
      for (const [k, v] of Object.entries(g.chkLedger || {})) chkSum[k] = (chkSum[k] || 0) + v;
      for (const [k, v] of Object.entries(g.chk || {})) chkSum['ta_' + k] = (chkSum['ta_' + k] || 0) + Math.abs(v);
      const kind = ELIM.includes(g.map) ? 'elim' : R500.includes(g.map) ? 'r500' : 'other';
      const mapKey = g.map === 'Prisoners Dilemma' ? (g.variant.tag === '10' ? 'PD10' : 'PD6') : (g.variant.tag === 'b' ? g.map + ' b' : g.map);
      const base = { key: g.key, src, map: g.map, mapKey, variant: g.variant.tag, vhow: g.variant.how, vguess: g.variant.guess, kind, rounds: g.rounds, limit: g.rounds === 500 ? 1 : 0,
        gameId: g.gameId, battleId: g.battleId, set: g.set, at: g.at };
      if (src === 'top') {
        if (inactive(g.A) || inactive(g.B)) { excluded.inactive++; return; }
        if (g.A.faults >= 3 || g.B.faults >= 3) { excluded.fault++; return; }
        if (!g.winner) { excluded.draw++; return; }
        nGames.top++;
        const pair = [];
        for (const ti of [0, 1]) {
          const tm = ti === 0 ? 'A' : 'B', name = ti === 0 ? g.teamA : g.teamB, oname = ti === 0 ? g.teamB : g.teamA;
          const x = { ...base, ti, name, opp: oname, win: tm === g.winner, grp: tm === g.winner ? 'TW' : 'TL', t7: T7.has(name), elo: ti === 0 ? g.eloA : g.eloB, s: teamSummary(g, ti) };
          TG.push(x); pair.push(x);
        }
        pair[0].pair = pair[1]; pair[1].pair = pair[0];
      } else {
        const bot = SETS[g.set], us = g.us === 'A' ? 0 : 1, pair = [];
        nGames.online++;
        for (const ti of [0, 1]) {
          const tm = ti === 0 ? 'A' : 'B', isUs = ti === us;
          const oppName = us === 0 ? g.teamB : g.teamA;
          const x = { ...base, ti, name: isUs ? bot : oppName, opp: isUs ? oppName : bot, win: tm === g.winner, grp: isUs ? bot : 'X-' + bot, grp2: isUs ? 'ours' : 'X', xOf: isUs ? null : bot, s: teamSummary(g, ti) };
          TG.push(x); pair.push(x);
        }
        pair[0].pair = pair[1]; pair[1].pair = pair[0];
      }
    });
  }
  return { TG, excluded, chkSum, nGames };
}

module.exports = { load, forEachGame, teamSummary, PR, ER, EI, CI, DB, OB, PH, PHN, DEP, phaseOf, INF, SETS, BOTS, ELIM, R500, epAgg, epAddInto, hMed, contactKill, CACHE };
