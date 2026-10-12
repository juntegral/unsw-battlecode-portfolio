#!/usr/bin/env node
// report.js — tables for research/observations/top-mass-spending.md from the mass-ledger cache (tools/mass_ledger.js).
// Reads .cache/mass-ledger/*.jsonl only (no replays, no network).
// usage (repository root):
//   node exp/mass-analysis/report.js [--top top-sample] [--keys <key file>] [--out exp/mass-analysis/report] [--boot 2000]
//   --keys restricts the top games in the cache to a key list (e.g. exp/mass-analysis/sample-top1500.keys).
//   Writes <out>.md (tables) and <out>.json (the same numbers).
// Groups (team-games):
//   TW / TL   top-vs-top winner / loser (data/top; games with an inactive or broken team are excluded, see `data`)
//   T7W       TW restricted to the 7 teams we test against (Cutlery, cheji bt, calc, 中国必须人能飞😡, forgot to mention,
//             Sabotage-d, dev test 1 :P)
//   X         the top opponents in our online test games (all sets pooled)
//   g4r4, merge2, swarm8, px9d, px8, pxking, avoid6, portal1   our side of each online set (g4r4 = baseline-r1+b+c)
// Map kinds: elim = Devil, Trophy, Prisoners Dilemma, Queen Of Spades, Default; r500 = Autarky, Portals, Schooltime,
// Slithery Fight, Trauma.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const { FI, ORIG, CAUSE } = ML;
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const TOPNAME = opt('top', 'top-sample'), OUT = path.resolve(ROOT, opt('out', 'exp/mass-analysis/report')), NBOOT = +opt('boot', 2000);
const SETS = { 'baseline-r1': 'g4r4', 'baseline-r1b': 'g4r4', 'baseline-r1c': 'g4r4', 'cand-merge2-online': 'merge2', 'cand-merge2-online-r2': 'merge2', 'cand-merge2-online-r3': 'merge2', 'cand-swarm8-online': 'swarm8',
  'base-px9d-online': 'px9d', 'base-px8-online': 'px8', 'px-king-v2-online': 'pxking', 'cand-avoid6-online': 'avoid6', 'cand-portal1-online': 'portal1' };
const OURS = ['g4r4', 'merge2', 'swarm8', 'px9d', 'px8', 'pxking'];
const T7 = new Set(['Cutlery', 'cheji bt', 'calc', '中国必须人能飞😡', 'forgot to mention', 'Sabotage-d', 'dev test 1 :P']);
const MAPS = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default', 'Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];

// ---------------------------------------------------------------------------------------------------------------
// Load
function readLines(f) { // a partially written last line (extraction still running) is skipped
  if (!fs.existsSync(f)) return [];
  const out = []; for (const l of fs.readFileSync(f, 'utf8').split('\n')) { if (!l.trim()) continue; try { out.push(JSON.parse(l)); } catch { /* partial line */ } }
  return out;
}
const KEYFILE = opt('keys', null); // optional: restrict the top games to this key list (e.g. the stratified sample)
const KEEP = KEYFILE ? new Set(fs.readFileSync(path.resolve(ROOT, KEYFILE), 'utf8').split('\n').map(x => x.trim()).filter(Boolean)) : null;
const games = [];
for (const g of readLines(path.join(ML.CACHE, TOPNAME + '.jsonl'))) if (!KEEP || KEEP.has(g.key)) games.push(g);
for (const s of Object.keys(SETS)) for (const g of readLines(path.join(ML.CACHE, 'online-' + s + '.jsonl'))) games.push(g);
const chkSum = {}; for (const g of games) for (const [k, v] of Object.entries(g.chk)) chkSum[k] = (chkSum[k] || 0) + v;

// helpers
const sumA = a => { let s = 0; for (const x of a) s += x; return s; };
const binSum = (T, cat, r0 = 0, r1 = 500) => { const a = T.fl[FI[cat]]; let s = 0; for (let b = Math.floor(r0 / 10); b < Math.ceil(r1 / 10); b++) s += a[b]; return s; };
const other = s => s === 'A' ? 'B' : 'A';
const faultN = T => binSum(T, 'dn_fault');
const inactive = T => T.splits <= 3 && T.sonar === 0;

// team-game records
const TG = [];
const excluded = { inactive: 0, fault: 0, draw: 0, games: 0 };
for (const g of games) {
  const winner = g.winner; // result winner 'A' | 'B' | null
  if (g.src === 'top') {
    const bad = TEAMSIDES => TEAMSIDES.some(s => inactive(g[s]));
    if (['A', 'B'].some(s => inactive(g[s]))) { excluded.inactive++; excluded.games++; continue; }
    if (['A', 'B'].some(s => faultN(g[s]) >= 3)) { excluded.fault++; excluded.games++; continue; }
    if (!winner) { excluded.draw++; excluded.games++; continue; }
    for (const s of ['A', 'B']) {
      const name = s === 'A' ? g.teamA : g.teamB;
      const grp = s === winner ? 'TW' : 'TL';
      TG.push({ g, s, T: g[s], O: g[other(s)], name, grp, win: s === winner, t7: T7.has(name) });
    }
  } else {
    const bot = SETS[g.set];
    TG.push({ g, s: g.us, T: g[g.us], O: g[other(g.us)], name: bot, grp: bot, win: g.us === winner });
    const os = other(g.us);
    TG.push({ g, s: os, T: g[os], O: g[g.us], name: os === 'A' ? g.teamA : g.teamB, grp: 'X', xOf: bot, win: os === winner });
  }
}
const mapKey = tg => tg.g.map === 'Prisoners Dilemma' ? (tg.g.variant || 'PD') : tg.g.map;
const kindOf = tg => tg.g.kind;
const running = (tg, r) => r < tg.g.rounds || (r === 500 && tg.g.rounds === 500);
const alive = (tg, r) => tg.T.st.units[r / 10] > 0;

// ---------------------------------------------------------------------------------------------------------------
// Statistics
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const mean = a => a.length ? sumA(a) / a.length : NaN;
const quant = (a, p) => { if (!a.length) return NaN; const b = [...a].sort((x, y) => x - y), i = (b.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return b[lo] + (b[hi] - b[lo]) * (i - lo); };
const median = a => quant(a, 0.5);
function bootMean(a, B = NBOOT) {
  if (a.length < 2) return [NaN, NaN];
  const r = rng(12345), bs = new Float64Array(B);
  for (let i = 0; i < B; i++) { let s = 0; for (let j = 0; j < a.length; j++) s += a[Math.floor(r() * a.length)]; bs[i] = s / a.length; }
  bs.sort(); return [bs[Math.floor(B * 0.025)], bs[Math.floor(B * 0.975)]];
}
function bootDiff(a, b, B = NBOOT) { // mean(b) - mean(a), independent resampling
  if (a.length < 2 || b.length < 2) return [NaN, NaN];
  const r = rng(777), bs = new Float64Array(B);
  for (let i = 0; i < B; i++) {
    let sa = 0, sb = 0;
    for (let j = 0; j < a.length; j++) sa += a[Math.floor(r() * a.length)];
    for (let j = 0; j < b.length; j++) sb += b[Math.floor(r() * b.length)];
    bs[i] = sb / b.length - sa / a.length;
  }
  bs.sort(); return [bs[Math.floor(B * 0.025)], bs[Math.floor(B * 0.975)]];
}
const f1 = (x, d = 1) => Number.isFinite(x) ? x.toFixed(d) : '–';
const sg = (x, d = 1) => Number.isFinite(x) ? (x >= 0 ? '+' : '−') + Math.abs(x).toFixed(d) : '–';
const pc = (x, d = 0) => Number.isFinite(x) ? (100 * x).toFixed(d) + '%' : '–';
const ciS = (a, d = 1) => { const [lo, hi] = bootMean(a); return `${f1(mean(a), d)} [${f1(lo, d)}, ${f1(hi, d)}]`; };
const table = (head, rows) => ['| ' + head.join(' | ') + ' |', '|' + head.map((h, i) => i ? '---:' : '---').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');

// ---------------------------------------------------------------------------------------------------------------
// Per team-game metrics
const PH = [[0, 100], [100, 250], [250, 350], [350, 450], [450, 500]];
const PHN = ['r0–99', 'r100–249', 'r250–349', 'r350–449', 'r450–499'];
const OWN = ORIG.slice(1, 6), ENEMY = ORIG.slice(6);
function metrics(tg) {
  const T = tg.T, O = tg.O, g = tg.g, st = T.st, R = g.rounds;
  const m = {};
  m.start = st.total[0];
  m.nat = binSum(T, 'eat_nat');
  for (const o of ORIG.slice(1)) m[o] = binSum(T, 'eat_' + o);
  m.ownDrop = OWN.reduce((s, o) => s + m[o], 0); m.enemyDrop = ENEMY.reduce((s, o) => s + m[o], 0);
  m.inflow = m.nat + m.ownDrop + m.enemyDrop;
  for (const p of ['ram', 'eat', 'esc', 'other']) m['spr_' + p] = binSum(T, 'spr_' + p);
  m.sprint = m.spr_ram + m.spr_eat + m.spr_esc + m.spr_other;
  m.sprN = binSum(T, 'spr_n');
  for (const c of CAUSE) { m['dl_' + c] = binSum(T, 'dl_' + c); m['dn_' + c] = binSum(T, 'dn_' + c); }
  m.deathLen = CAUSE.reduce((s, c) => s + m['dl_' + c], 0);
  m.final = st.total[50]; m.finalKing = st.king[50]; m.finalUnits = st.units[50];
  m.ledgerOK = m.start + m.inflow - m.sprint - m.deathLen === m.final ? 1 : 0;
  m.turns = binSum(T, 'turns');
  m.rounds = R; m.limit = g.rounds === 500 ? 1 : 0;
  // net mass returned by own deaths: length lost minus own re-eaten (whole game)
  // territory / denial
  m.natOwn = binSum(T, 'nat_own'); m.natEnemy = binSum(T, 'nat_enemy'); m.natNeutral = binSum(T, 'nat_neutral');
  m.fOwn = binSum(T, 'nat_fOwn'); m.fEnemy = binSum(T, 'nat_fEnemy');
  const mine = tg.s === 'A' ? 0 : 1, theirs = 1 - mine;
  m.supplyOwn = sumA(g.gf[mine]); m.supplyEnemy = sumA(g.gf[theirs]); m.fSupplyOwn = sumA(g.gf[3 + mine]); m.fSupplyEnemy = sumA(g.gf[3 + theirs]);
  m.oppNatInOurs = binSum(O, 'nat_enemy'); m.oppFInOurs = binSum(O, 'nat_fEnemy');
  m.oppAteOurDrops = ENEMY.reduce((s, o) => s + binSum(O, 'eat_' + o), 0);
  // offense
  m.ramN = m.dn_ram; m.ramOwn = m.dl_ram; m.ramEnemy = binSum(T, 'ram_elen'); m.ramSpr = m.spr_ram;
  m.rammedN = m.dn_rammed; m.rammedOwn = m.dl_rammed; m.rammedEnemy = binSum(T, 'rammed_elen');
  m.bkN = binSum(T, 'bk_n'); m.bkLen = binSum(T, 'bk_len');
  m.trapEn = binSum(T, 'trapE_n'); m.trapElen = binSum(T, 'trapE_len');
  m.contactLost = m.ramOwn + m.rammedOwn + m.dl_enemyBody;
  m.contactKilled = m.ramEnemy + m.rammedEnemy + m.bkLen;
  // king deaths
  m.kdN = binSum(T, 'kd_n'); m.kdLen = binSum(T, 'kd_len');
  // splits
  m.splitN = binSum(T, 'split_n'); m.splitStub = binSum(T, 'split_stub');
  // state snapshots
  for (const r of [50, 100, 200, 300, 350, 400, 450, 500]) {
    const i = r / 10, ok = running(tg, r) && st.units[i] > 0;
    m['u' + r] = ok ? st.units[i] : NaN; m['tot' + r] = ok ? st.total[i] : NaN; m['k' + r] = ok ? st.king[i] : NaN;
    m['sh' + r] = ok && st.total[i] > 0 ? st.king[i] / st.total[i] : NaN;
    m['sec' + r] = ok ? st.second[i] : NaN;
    m['small' + r] = ok ? st.small[i] : NaN; m['mid' + r] = ok ? st.mid[i] : NaN; m['big' + r] = ok ? st.big[i] : NaN;
  }
  // tempo
  let pu = 0, pur = 0, pt = 0, ptr = 0;
  const last = Math.min(50, Math.ceil(R / 10));
  for (let i = 0; i <= last && i <= 50; i++) { if (st.units[i] > pu) { pu = st.units[i]; pur = i * 10; } if (st.total[i] > pt) { pt = st.total[i]; ptr = i * 10; } }
  m.peakUnits = pu; m.peakUnitsR = pur; m.peakTotal = pt; m.peakTotalR = ptr;
  const sacBins = T.fl[FI.dl_sac], sacTot = sumA(sacBins);
  m.sacTot = sacTot;
  const cum = f => { if (sacTot < 10) return NaN; let c = 0; for (let b = 0; b < 50; b++) { c += sacBins[b]; if (c >= f * sacTot) return b * 10; } return NaN; };
  m.sacOnset = cum(0.1); m.sacMed = cum(0.5);
  const cross = th => { for (let i = 0; i <= last; i++) if (st.total[i] > 0 && st.king[i] >= th * st.total[i] && st.king[i] >= 8) return i * 10; return NaN; };
  m.sh30 = cross(0.3); m.sh50 = cross(0.5);
  const reach = L => { for (let i = 0; i <= last; i++) if (st.king[i] >= L) return i * 10; return NaN; };
  m.k10r = reach(10); m.k20r = reach(20); m.k30r = reach(30);
  // phase flows
  m.ph = PH.map(([a, b]) => {
    if (!(a < R)) return null;
    const o = { nat: binSum(T, 'eat_nat', a, b), own: OWN.reduce((s, x) => s + binSum(T, 'eat_' + x, a, b), 0), enemy: ENEMY.reduce((s, x) => s + binSum(T, 'eat_' + x, a, b), 0),
      spr: ['spr_ram', 'spr_eat', 'spr_esc', 'spr_other'].reduce((s, x) => s + binSum(T, x, a, b), 0) };
    for (const c of CAUSE) o[c] = binSum(T, 'dl_' + c, a, b);
    o.knat = binSum(T, 'keat_nat', a, b); o.kown = OWN.reduce((s, x) => s + binSum(T, 'keat_' + x, a, b), 0); o.kenemy = ENEMY.reduce((s, x) => s + binSum(T, 'keat_' + x, a, b), 0);
    o.koSac = binSum(T, 'keat_oSac', a, b); o.koTrap = binSum(T, 'keat_oTrap', a, b);
    o.ramN = binSum(T, 'dn_ram', a, b); o.ramOwn = binSum(T, 'dl_ram', a, b); o.ramEnemy = binSum(T, 'ram_elen', a, b);
    o.rammedOwn = binSum(T, 'dl_rammed', a, b); o.rammedEnemy = binSum(T, 'rammed_elen', a, b); o.bkLen = binSum(T, 'bk_len', a, b);
    o.natEnemy = binSum(T, 'nat_enemy', a, b); o.fEnemy = binSum(T, 'nat_fEnemy', a, b);
    o.split = binSum(T, 'split_n', a, b); o.turns = binSum(T, 'turns', a, b);
    o.sacN = binSum(T, 'dn_sac', a, b); o.trapN = binSum(T, 'dn_trap', a, b);
    o.kd = binSum(T, 'kd_len', a, b);
    return o;
  });
  // deaths table
  m.dt = T.dt;
  // lineage
  const L = T.lin;
  m.lin = null;
  if (L && L.cp && L.cp[350] && g.rounds === 500) {
    const c = L.cp[350];
    m.lin = { Lt: c.Lt, nat: c.eat[0], own: c.eat.slice(1, 6).reduce((s, x) => s + x, 0), oSac: c.eat[1], oTrap: c.eat[2], oOther: c.eat[3] + c.eat[4] + c.eat[5],
      enemy: c.eat.slice(6).reduce((s, x) => s + x, 0), cost: c.cost, lossOff: c.lossOff, lossPath: c.lossPath, final: L.len, wasKing: c.wasKing, transfers: c.transfers };
    if (L.win) {
      const w = L.win[0].map((x, i) => x + L.win[1][i] + L.win[2][i]), tot = sumA(w);
      const s = [...w].sort((a, b) => b - a);
      m.lin.burstTop1 = tot ? s[0] / tot : NaN; m.lin.burstTop3 = tot ? (s[0] + s[1] + s[2]) / tot : NaN; m.lin.windowsWithEat = w.filter(x => x > 0).length;
      m.lin.gain350_400 = sumA(w.slice(0, 5)); m.lin.gain400_450 = sumA(w.slice(5, 10)); m.lin.gain450_500 = sumA(w.slice(10, 15));
      m.lin.ownW = [sumA(L.win[1].slice(0, 5)), sumA(L.win[1].slice(5, 10)), sumA(L.win[1].slice(10, 15))];
      m.lin.natW = [sumA(L.win[0].slice(0, 5)), sumA(L.win[0].slice(5, 10)), sumA(L.win[0].slice(10, 15))];
      // Gini of 15 windows
      let gs = 0; for (const a of w) for (const b of w) gs += Math.abs(a - b);
      m.lin.gini = tot ? gs / (2 * w.length * tot) : NaN;
    }
    if (L.cp[450]) { const c4 = L.cp[450]; m.lin.Lt450 = c4.Lt; m.lin.wasKing450 = c4.wasKing; }
    if (L.cp[400]) { const c4 = L.cp[400]; m.lin.Lt400 = c4.Lt; m.lin.wasKing400 = c4.wasKing; }
    if (L.cp[300]) { const c3 = L.cp[300]; m.lin.Lt300 = c3.Lt; m.lin.wasKing300 = c3.wasKing; }
  }
  return m;
}
for (const tg of TG) tg.m = metrics(tg);

// ---------------------------------------------------------------------------------------------------------------
// Grouping helpers
const GROUPS = ['TW', 'TL', 'T7W', 'X', ...OURS];
function sel(grp, filt = () => true) {
  if (grp === 'T7W') return TG.filter(t => t.grp === 'TW' && t.t7 && filt(t));
  return TG.filter(t => t.grp === grp && filt(t));
}
const byKind = k => t => kindOf(t) === k;
const out = { data: {}, tables: {} };
const md = [];
const P = s => md.push(s);

// ---------------------------------------------------------------------------------------------------------------
// 0. Data
{
  const top = games.filter(g => g.src === 'top');
  P(`# mass ledger report (generated by exp/mass-analysis/report.js)\n`);
  P(`- top cache: .cache/mass-ledger/${TOPNAME}.jsonl, games ${top.length}; excluded ${excluded.games} (inactive team ${excluded.inactive}, fault deaths ≥3 ${excluded.fault}, draw ${excluded.draw}).`);
  P(`- online sets: ${Object.keys(SETS).map(s => s + ' ' + games.filter(g => g.set === s).length).join(', ')}.`);
  P(`- reconciliation checks summed over ${games.length} games: ${JSON.stringify(chkSum)} (all expected 0). ledger identity per team-game ok: ${TG.filter(t => t.m.ledgerOK).length}/${TG.length}.`);
  const rows = GROUPS.map(gp => { const a = sel(gp); return [gp, a.length, sel(gp, byKind('elim')).length, sel(gp, byKind('r500')).length, pc(mean(a.map(t => t.win ? 1 : 0))), pc(mean(a.map(t => t.m.limit)))]; });
  P(table(['group', 'team-games', 'elim', 'r500', 'win', 'reached r500'], rows));
  out.data = { games: games.length, top: top.length, excluded, chkSum };
}

// ---------------------------------------------------------------------------------------------------------------
// 1. Ledger per team-game (whole game) by kind
function ledgerTable(kind, onlyLimit) {
  const cols = ['start', 'nat', 'oSac', 'oTrap', 'oRammed+oRam', 'oOther', 'enemyDrop', 'sprint', 'dl_sac', 'dl_trap', 'dl_rammed', 'dl_ram', 'dl_other', 'final', 'finalKing', 'finalUnits'];
  const get = (m, c) => c === 'oRammed+oRam' ? m.oRammed + m.oRam : c === 'dl_other' ? m.dl_enemyBody + m.dl_allyHead + m.dl_fault + m.dl_sprintDeath : m[c];
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind && (!onlyLimit || t.m.limit));
    if (!a.length) continue;
    const r = [gp + ` (${a.length})`];
    res[gp] = {};
    for (const c of cols) { const v = mean(a.map(t => get(t.m, c))); res[gp][c] = v; r.push(f1(v)); }
    rows.push(r);
  }
  out.tables['ledger_' + kind + (onlyLimit ? '_limit' : '')] = res;
  return table(['group (n)', 'start', '+nat', '+oSac', '+oTrap', '+oContact', '+oOther', '+enemy drops', '−sprint', '−sac', '−trap', '−rammed', '−ram', '−other', '=final', 'king', 'units'], rows);
}
P(`\n## 1. Ledger per team-game (whole game)`);
P(`\n### elim maps\n` + ledgerTable('elim', false));
P(`\n### r500 maps (all games)\n` + ledgerTable('r500', false));
P(`\n### r500 maps, games that reached round 500\n` + ledgerTable('r500', true));

// 1c. Mass bridge: external inflow, net loss per death cause after own re-eating, sprint, final
function bridgeTable(kind, onlyLimit) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind && (!onlyLimit || t.m.limit)); if (!a.length) continue;
    const mm = f => mean(a.map(t => f(t.m)));
    const v = { n: a.length, start: mm(m => m.start), nat: mm(m => m.nat), enemy: mm(m => m.enemyDrop),
      sac: mm(m => m.dl_sac - m.oSac), trap: mm(m => m.dl_trap - m.oTrap), rammed: mm(m => m.dl_rammed - m.oRammed), ram: mm(m => m.dl_ram - m.oRam),
      other: mm(m => m.dl_enemyBody + m.dl_allyHead + m.dl_fault + m.dl_sprintDeath - m.oOther), sprint: mm(m => m.sprint), final: mm(m => m.final), king: mm(m => m.finalKing) };
    v.ext = v.start + v.nat + v.enemy;
    res[gp] = v;
    const p = x => pc(x / v.ext);
    rows.push([gp, v.n, f1(v.ext), f1(v.nat), f1(v.enemy), `${f1(v.sac)} (${p(v.sac)})`, `${f1(v.trap)} (${p(v.trap)})`, `${f1(v.rammed)} (${p(v.rammed)})`, `${f1(v.ram)} (${p(v.ram)})`, `${f1(v.other)} (${p(v.other)})`, `${f1(v.sprint)} (${p(v.sprint)})`, `${f1(v.final)} (${p(v.final)})`, `${f1(v.king)} (${p(v.king)})`]);
  }
  out.tables['bridge_' + kind + (onlyLimit ? '_limit' : '')] = res;
  return table(['group', 'n', 'external in (start+nat+enemy drops)', 'nat', 'enemy drops', 'net −sac', 'net −trap', 'net −rammed', 'net −ram', 'net −other', '−sprint', '=final', 'king'], rows);
}
P(`\n## 1c. Mass bridge: net loss per cause = length lost − own pearls re-eaten from those deaths (share of external inflow)`);
P(`\n### r500, games that reached r500\n` + bridgeTable('r500', true));
P(`\n### elim (all games)\n` + bridgeTable('elim', false));

// 1b. phase flows per running team-game
function phaseTable(kind, fields, label) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind); if (!a.length) continue;
    res[gp] = {};
    for (let p = 0; p < PH.length; p++) {
      const b = a.filter(t => t.m.ph[p] && t.T.st.units[PH[p][0] / 10] > 0);
      if (b.length < 3) continue;
      const vals = fields.map(f => mean(b.map(t => typeof f === 'function' ? f(t.m.ph[p], t) : t.m.ph[p][f])));
      res[gp][PHN[p]] = { n: b.length, v: vals };
      rows.push([gp, PHN[p], b.length, ...vals.map(v => f1(v))]);
    }
  }
  out.tables['phase_' + label + '_' + kind] = res;
  return rows;
}
P(`\n## 2. Flows by phase (per team-game alive at the phase start)`);
const phF = ['nat', 'own', 'enemy', 'spr', 'sac', 'trap', 'rammed', 'ram', ph => ph.enemyBody + ph.allyHead + ph.fault + ph.sprintDeath, 'split', 'turns', 'knat', 'kown', 'kenemy', 'kd'];
const phH = ['group', 'phase', 'n', '+nat', '+own drops', '+enemy drops', '−sprint', '−sac', '−trap', '−rammed', '−ram', '−other', 'splits', 'turns', 'king +nat', 'king +own', 'king +enemy', 'king death len'];
for (const k of ['elim', 'r500']) P(`\n### ${k}\n` + table(phH, phaseTable(k, phF, 'flows')));

// ---------------------------------------------------------------------------------------------------------------
// 3. Deaths: cause x length, and what the drops feed
function deathAgg(a, filt) {
  const agg = {};
  for (const t of a) for (const [k, v] of Object.entries(t.m.dt)) {
    const [cause, lc, ph, king, near, kd, mech, blk] = k.split('|');
    if (filt && !filt({ cause, lc, ph, king, near, kd, mech, blk })) continue;
    const key = cause;
    const x = agg[key] || (agg[key] = [0, 0, 0, 0, 0, 0, 0, 0]);
    for (let i = 0; i < 8; i++) x[i] += v[i];
  }
  return agg;
}
P(`\n## 3. Deaths by cause: per team-game n / length, and the fate of their pearls (share of drops)`);
for (const kind of ['elim', 'r500']) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind); if (!a.length) continue;
    const agg = deathAgg(a);
    res[gp] = {};
    for (const c of CAUSE) {
      const x = agg[c]; if (!x || !x[0]) continue;
      res[gp][c] = x;
      rows.push([gp, c, f1(x[0] / a.length, 2), f1(x[1] / a.length), f1(x[1] / x[0], 2), pc(x[3] / x[2]), pc(x[4] / x[2]), pc(x[5] / x[2]), f1(x[3] ? x[6] / x[3] : NaN)]);
    }
  }
  out.tables['deaths_' + kind] = res;
  P(`\n### ${kind}\n` + table(['group', 'cause', 'n/tg', 'len/tg', 'mean len', 'drops eaten by own', 'by own king', 'by enemy', 'own delay (rounds)'], rows));
}

// sacrifice detail: length class, phase, context
P(`\n## 4. Sacrifices (sac): length class, phase, context. Per team-game; efficiency = own re-eaten / sacrificed length`);
for (const kind of ['elim', 'r500']) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind); if (!a.length) continue;
    const by = {};
    for (const t of a) for (const [k, v] of Object.entries(t.m.dt)) {
      const [cause, lc, ph, king, near, kd] = k.split('|'); if (cause !== 'sac') continue;
      for (const kk of ['len:' + lc, 'ph:' + ph, 'near:' + near, 'kd:' + kd, 'all']) { const x = by[kk] || (by[kk] = [0, 0, 0, 0, 0, 0, 0, 0]); for (let i = 0; i < 8; i++) x[i] += v[i]; }
    }
    res[gp] = by;
    const all = by.all || [0, 0, 0, 0, 0, 0, 0, 0];
    const lcs = ['2', '3', '4', '5-7', '8-14', '15+'].map(l => by['len:' + l] ? by['len:' + l][0] : 0);
    const nears = ['0', 'S', 'B'].map(l => by['near:' + l] ? by['near:' + l][0] : 0);
    const phs = ['p0', 'p1', 'p2', 'p3', 'p4'].map(l => by['ph:' + l] ? by['ph:' + l][1] : 0);
    rows.push([gp, f1(all[0] / a.length), f1(all[1] / a.length), lcs.map(x => pc(x / Math.max(1, all[0]))).join(' / '), phs.map(x => f1(x / a.length)).join(' / '),
      nears.map(x => pc(x / Math.max(1, all[0]))).join(' / '), pc(all[3] / Math.max(1, all[1])), pc(all[7] / Math.max(1, all[1])), pc(all[4] / Math.max(1, all[1])), pc(all[5] / Math.max(1, all[2]))]);
  }
  out.tables['sac_' + kind] = res;
  P(`\n### ${kind}\n` + table(['group', 'sac n/tg', 'sac len/tg', 'len 2 / 3 / 4 / 5–7 / 8–14 / 15+ (share of n)', 'sac len by phase p0/p1/p2/p3/p4', 'nearest ally ≤3: none / <8 / ≥8', 'own re-eat per len', 'by own L≥8 per len', 'by own king per len', 'enemy share of drops'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
// 5. Conversion: king share and state over time
P(`\n## 5. Conversion: king share, king, total, units at checkpoints (team-games alive, game running)`);
for (const kind of ['elim', 'r500']) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind); if (!a.length) continue;
    res[gp] = {};
    for (const r of [100, 200, 300, 400, 450, 500]) {
      const b = a.filter(t => Number.isFinite(t.m['sh' + r])); if (b.length < 3) continue;
      const v = { n: b.length, share: mean(b.map(t => t.m['sh' + r])), king: mean(b.map(t => t.m['k' + r])), kingMed: median(b.map(t => t.m['k' + r])), total: mean(b.map(t => t.m['tot' + r])), units: mean(b.map(t => t.m['u' + r])),
        second: mean(b.map(t => t.m['sec' + r])), small: mean(b.map(t => t.m['small' + r])), mid: mean(b.map(t => t.m['mid' + r])), big: mean(b.map(t => t.m['big' + r])) };
      res[gp][r] = v;
      rows.push([gp, r, v.n, pc(v.share), f1(v.king), f1(v.kingMed), f1(v.total), f1(v.units), f1(v.second), f1(v.small), f1(v.mid), f1(v.big)]);
    }
  }
  out.tables['conv_' + kind] = res;
  P(`\n### ${kind}\n` + table(['group', 'r', 'n', 'king share', 'king mean', 'king median', 'total', 'units', '2nd longest', 'mass in L≤4', 'L5–9', 'L≥10 non-king'], rows));
}

// 5c. Conversion efficiency after r300 (games that reached r500, both kinds)
P(`\n## 5c. Conversion efficiency (games that reached r500): king r500 relative to mass at r300; who eats from r250`);
for (const kind of ['r500', 'elim']) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind && t.m.limit && Number.isFinite(t.m.tot300)); if (a.length < 3) continue;
    const S = f => sumA(a.map(t => f(t.m)));
    const ph = (t, i) => t.m.ph[i] || {};
    const post = f => sumA(a.map(t => [2, 3, 4].reduce((s, i) => s + (f(ph(t, i)) || 0), 0)));
    const eatAll = post(p => p.nat + p.own + p.enemy), eatKing = post(p => p.knat + p.kown + p.kenemy);
    // sacrifice drops r250+ and their fate
    let drops = 0, own = 0, king = 0, big = 0, len = 0, n = 0;
    for (const t of a) for (const [k, v] of Object.entries(t.m.dt)) { const [cause, lc, phs] = k.split('|'); if (cause !== 'sac' || !['p2', 'p3', 'p4'].includes(phs)) continue; n += v[0]; len += v[1]; drops += v[2]; own += v[3]; king += v[4]; big += v[7]; }
    const v = { n: a.length, tot300: S(m => m.tot300) / a.length, k300: S(m => m.k300) / a.length, k500: S(m => m.finalKing) / a.length, tot500: S(m => m.final) / a.length,
      ratio: S(m => m.finalKing) / Math.max(1, S(m => m.tot300)), kingShareEat: eatKing / Math.max(1, eatAll), eatPost: eatAll / a.length, kingEatPost: eatKing / a.length,
      sacLen: len / a.length, sacDrops: drops / a.length, sacOwn: own / Math.max(1, drops), sacBig: big / Math.max(1, drops), sacKing: king / Math.max(1, drops), kingFromSac: king / a.length };
    res[gp] = v;
    rows.push([gp, v.n, f1(v.tot300), f1(v.k300), f1(v.k500), f1(v.tot500), f1(v.ratio, 2), f1(v.eatPost), f1(v.kingEatPost), pc(v.kingShareEat), f1(v.sacLen), f1(v.sacDrops), pc(v.sacOwn), pc(v.sacBig), pc(v.sacKing), f1(v.kingFromSac)]);
  }
  out.tables['convEff_' + kind] = res;
  P(`\n### ${kind}\n` + table(['group', 'n', 'total r300', 'king r300', 'king r500', 'total r500', 'king r500 / total r300', 'pearls eaten r250+', 'by the king (at eat time)', 'king share', 'sac len r250+', 'sac drops', 'eaten by own', 'by own L≥8', 'by own king', 'king pearls from sac'], rows));
}

// 5b. final-king lineage r350 -> 500 (round-limit games, r500 maps and all maps)
P(`\n## 6. Final-king lineage from r350 to r500 (games that reached r500)`);
for (const kind of ['r500', 'elim']) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind && t.m.lin); if (a.length < 3) continue;
    const L = a.map(t => t.m.lin);
    const v = { n: a.length, Lt: mean(L.map(x => x.Lt)), nat: mean(L.map(x => x.nat)), oSac: mean(L.map(x => x.oSac)), oTrap: mean(L.map(x => x.oTrap)), oOther: mean(L.map(x => x.oOther)), enemy: mean(L.map(x => x.enemy)),
      cost: mean(L.map(x => x.cost)), lossOff: mean(L.map(x => x.lossOff)), lossPath: mean(L.map(x => x.lossPath)), final: mean(L.map(x => x.final)),
      wasKing350: mean(L.map(x => x.wasKing)), wasKing450: mean(L.filter(x => x.wasKing450 !== undefined).map(x => x.wasKing450)),
      top1: mean(L.filter(x => Number.isFinite(x.burstTop1)).map(x => x.burstTop1)), top3: mean(L.filter(x => Number.isFinite(x.burstTop3)).map(x => x.burstTop3)), gini: mean(L.filter(x => Number.isFinite(x.gini)).map(x => x.gini)),
      g1: mean(L.map(x => x.gain350_400)), g2: mean(L.map(x => x.gain400_450)), g3: mean(L.map(x => x.gain450_500)) };
    res[gp] = v;
    rows.push([gp, v.n, f1(v.Lt), f1(v.nat), f1(v.oSac), f1(v.oTrap), f1(v.oOther), f1(v.enemy), f1(v.cost), f1(v.lossOff), f1(v.lossPath), f1(v.final), pc(v.wasKing350), pc(v.wasKing450),
      `${f1(v.g1)} / ${f1(v.g2)} / ${f1(v.g3)}`, pc(v.top1), pc(v.top3), f1(v.gini, 2)]);
  }
  out.tables['lineage_' + kind] = res;
  P(`\n### ${kind}\n` + table(['group', 'n', 'L350', '+nat', '+own sac', '+own trap', '+own contact/other', '+enemy drops', '−sprint', '−split off', '−left behind', '=final', 'king at 350', 'king at 450', 'eats 350–399 / 400–449 / 450–499', 'top 10-round window share', 'top 3 windows', 'Gini (15 windows)'], rows));
}

// 6b. Final-king lineage per r500 map (games that reached r500)
P(`\n## 6b. Final-king lineage per r500 map (games that reached r500): n, L350, +sac, +nat, −left behind/split off, r500 king`);
{
  const rows = [];
  const res = {};
  for (const mp of ML.R500) {
    res[mp] = {};
    for (const gp of ['TW', 'TL', 'X', 'g4r4', 'merge2', 'swarm8', 'px9d', 'px8', 'pxking']) {
      const a = sel(gp, t => t.g.map === mp && t.m.lin); if (!a.length) continue;
      const L = a.map(t => t.m.lin);
      const v = { n: a.length, Lt: mean(L.map(x => x.Lt)), sac: mean(L.map(x => x.oSac)), nat: mean(L.map(x => x.nat)), left: mean(L.map(x => x.lossPath + x.lossOff)), final: mean(L.map(x => x.final)) };
      res[mp][gp] = v;
      rows.push([mp, gp, v.n, f1(v.Lt), f1(v.sac), f1(v.nat), f1(v.left), f1(v.final)]);
    }
  }
  out.tables.lineageMap = res;
  P(table(['map', 'group', 'n', 'L350', '+own sac', '+nat', '−left behind − split off', '=king r500'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
// 7. Offense
P(`\n## 7. Offense: rams, being rammed, body kills (per team-game)`);
for (const kind of ['elim', 'r500']) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind); if (!a.length) continue;
    const s = f => sumA(a.map(t => f(t.m)));
    const v = { n: a.length, ramN: s(m => m.ramN) / a.length, ramOwn: s(m => m.ramOwn) / a.length, ramEnemy: s(m => m.ramEnemy) / a.length, ramSpr: s(m => m.ramSpr) / a.length,
      rammedN: s(m => m.rammedN) / a.length, rammedOwn: s(m => m.rammedOwn) / a.length, rammedEnemy: s(m => m.rammedEnemy) / a.length,
      bkN: s(m => m.bkN) / a.length, bkLen: s(m => m.bkLen) / a.length, ebN: s(m => m.dn_enemyBody) / a.length, ebLen: s(m => m.dl_enemyBody) / a.length,
      trapE: s(m => m.trapElen) / a.length, killed: s(m => m.contactKilled) / a.length, lost: s(m => m.contactLost) / a.length,
      ratio: s(m => m.ramEnemy) / Math.max(1, s(m => m.ramOwn + m.ramSpr)), sprEsc: s(m => m.spr_esc) / a.length, sprEat: s(m => m.spr_eat) / a.length, sprOther: s(m => m.spr_other) / a.length };
    res[gp] = v;
    rows.push([gp, a.length, f1(v.ramN, 2), f1(v.ramOwn), f1(v.ramEnemy), f1(v.ramSpr, 2), f1(v.ratio, 2), f1(v.rammedN, 2), f1(v.rammedOwn), f1(v.rammedEnemy), f1(v.bkN, 2), f1(v.bkLen), f1(v.ebLen), f1(v.trapE), f1(v.killed), f1(v.lost), sg(v.killed - v.lost), `${f1(v.sprEsc)} / ${f1(v.sprEat)} / ${f1(v.sprOther)}`]);
  }
  out.tables['offense_' + kind] = res;
  P(`\n### ${kind}\n` + table(['group', 'n', 'rams', 'own len spent', 'enemy len killed', 'ram sprint cost', 'killed per spent', 'rammed', 'own len lost', 'rammer len (died)', 'body kills', 'their len', 'own into enemy body len', 'trapped by enemy body len', 'contact: enemy len killed', 'own len lost', 'net', 'sprint cost esc / eat / other'], rows));
}
// ram timing and length pairing
P(`\n### rams by phase (elim + r500): enemy length killed / own length spent, per team-game alive`);
{
  const rows = [];
  for (const gp of GROUPS) {
    const a = sel(gp); if (!a.length) continue;
    const r = [gp];
    for (let p = 0; p < PH.length; p++) {
      const b = a.filter(t => t.m.ph[p] && t.T.st.units[PH[p][0] / 10] > 0);
      const own = sumA(b.map(t => t.m.ph[p].ramOwn)), en = sumA(b.map(t => t.m.ph[p].ramEnemy)), n = sumA(b.map(t => t.m.ph[p].ramN));
      r.push(b.length ? `${f1(n / b.length, 2)} (${f1(en / b.length)} / ${f1(own / b.length)})` : '–');
    }
    rows.push(r);
  }
  P(table(['group', ...PHN.map(x => 'rams (killed / spent) ' + x)], rows));
}

// ---------------------------------------------------------------------------------------------------------------
// 8. Denial
P(`\n## 8. Denial: natural pearls by territory, fountains, enemy drops (per team-game)`);
for (const kind of ['elim', 'r500']) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind); if (!a.length) continue;
    const mm = f => mean(a.map(t => f(t.m)));
    const v = { natOwn: mm(m => m.natOwn), natEnemy: mm(m => m.natEnemy), natNeutral: mm(m => m.natNeutral), fOwn: mm(m => m.fOwn), fEnemy: mm(m => m.fEnemy),
      supplyOwn: mm(m => m.supplyOwn), supplyEnemy: mm(m => m.supplyEnemy), oppIn: mm(m => m.oppNatInOurs), oppF: mm(m => m.oppFInOurs), enemyDrop: mm(m => m.enemyDrop), oppAte: mm(m => m.oppAteOurDrops),
      shareOwnSupply: sumA(a.map(t => t.m.natOwn)) / Math.max(1, sumA(a.map(t => t.m.supplyOwn))), shareEnemySupply: sumA(a.map(t => t.m.natEnemy)) / Math.max(1, sumA(a.map(t => t.m.supplyEnemy))),
      oppShareOurSupply: sumA(a.map(t => t.m.oppNatInOurs)) / Math.max(1, sumA(a.map(t => t.m.supplyOwn))) };
    res[gp] = v;
    rows.push([gp, a.length, f1(v.natOwn), f1(v.natEnemy), f1(v.natNeutral), f1(v.fOwn), f1(v.fEnemy), pc(v.shareOwnSupply), pc(v.shareEnemySupply), f1(v.oppIn), pc(v.oppShareOurSupply), f1(v.enemyDrop), f1(v.oppAte), sg(v.natEnemy + v.enemyDrop - v.oppIn - v.oppAte)]);
  }
  out.tables['denial_' + kind] = res;
  P(`\n### ${kind}\n` + table(['group', 'n', 'nat eaten own terr.', 'in enemy terr.', 'neutral', 'own fountains', 'enemy fountains', 'share of own-terr. spawns we eat', 'share of enemy-terr. spawns we eat', 'enemy eats in our terr.', 'share of our spawns they eat', 'enemy drops we eat', 'our drops they eat', 'net taken'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
// 9. Tempo
P(`\n## 9. Tempo (medians; rounds)`);
for (const kind of ['elim', 'r500']) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind && (kind === 'elim' || t.m.limit)); if (a.length < 3) continue;
    const md = f => median(a.map(t => t.m[f]).filter(Number.isFinite));
    const cnt = f => a.map(t => t.m[f]).filter(Number.isFinite).length;
    const v = { n: a.length, peakUnitsR: md('peakUnitsR'), peakUnits: md('peakUnits'), peakTotalR: md('peakTotalR'), sacOnset: md('sacOnset'), sacMed: md('sacMed'), sacN: cnt('sacOnset'),
      sh30: md('sh30'), sh30n: cnt('sh30'), sh50: md('sh50'), sh50n: cnt('sh50'), k10r: md('k10r'), k20r: md('k20r'), k20n: cnt('k20r'), k30r: md('k30r'), k30n: cnt('k30r') };
    res[gp] = v;
    rows.push([gp, a.length, `${f1(v.peakUnitsR, 0)} (${f1(v.peakUnits, 0)})`, f1(v.peakTotalR, 0), `${f1(v.sacOnset, 0)} / ${f1(v.sacMed, 0)} (${v.sacN})`, `${f1(v.sh30, 0)} (${v.sh30n})`, `${f1(v.sh50, 0)} (${v.sh50n})`, f1(v.k10r, 0), `${f1(v.k20r, 0)} (${v.k20n})`, `${f1(v.k30r, 0)} (${v.k30n})`]);
  }
  out.tables['tempo_' + kind] = res;
  P(`\n### ${kind}${kind === 'r500' ? ' (games that reached r500)' : ''}\n` + table(['group', 'n', 'peak units round (units)', 'peak total round', 'sac onset 10% / median (n with sac ≥10)', 'king share ≥30% from (n)', '≥50% from (n)', 'king ≥10 from', 'king ≥20 from (n)', 'king ≥30 from (n)'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
// 3c. Deaths of long dragons (L >= 8): king (longest at death) or not, by cause
P(`\n## 3c. Deaths of dragons with L ≥ 8, by cause (per team-game: n / length); king = longest at death`);
for (const kind of ['elim', 'r500']) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind); if (!a.length) continue;
    const by = {};
    for (const t of a) for (const [k, v] of Object.entries(t.m.dt)) {
      const [cause, lc, ph, king] = k.split('|'); if (!(lc === '8-14' || lc === '15+')) continue;
      for (const kk of [cause + ':' + king, 'all:' + king]) { const x = by[kk] || (by[kk] = [0, 0, 0, 0, 0, 0, 0, 0]); for (let i = 0; i < 8; i++) x[i] += v[i]; }
    }
    res[gp] = by;
    const c = (k) => by[k] ? `${f1(by[k][0] / a.length, 2)} / ${f1(by[k][1] / a.length)}` : '–';
    rows.push([gp, a.length, c('all:1'), c('all:0'), ...CAUSE.slice(0, 6).map(x => `${c(x + ':1')} ; ${c(x + ':0')}`)]);
  }
  out.tables['bigdeaths_' + kind] = res;
  P(`\n### ${kind}\n` + table(['group', 'n', 'king deaths', 'other L≥8 deaths', ...CAUSE.slice(0, 6).map(x => x + ' (king ; other)')], rows));
}

// ---------------------------------------------------------------------------------------------------------------
// 3b. Cornered (trap) deaths: mechanism and what blocked them
P(`\n## 3b. Cornered deaths (trap): mechanism, blocker, length (per team-game)`);
for (const kind of ['elim', 'r500']) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind); if (!a.length) continue;
    const by = {};
    for (const t of a) for (const [k, v] of Object.entries(t.m.dt)) {
      const [cause, lc, ph, king, near, kd, mech, blk] = k.split('|'); if (cause !== 'trap') continue;
      const big = lc === '8-14' || lc === '15+' ? 'big' : lc === '5-7' ? 'mid' : 'small';
      for (const kk of ['mech:' + mech, 'blk:' + blk, 'size:' + big, 'king:' + king, 'all', 'bigph:' + (big === 'big' ? ph : '-')]) { const x = by[kk] || (by[kk] = [0, 0, 0, 0, 0, 0, 0, 0]); for (let i = 0; i < 8; i++) x[i] += v[i]; }
    }
    res[gp] = by;
    const n = k => by[k] ? by[k][0] / a.length : 0, l = k => by[k] ? by[k][1] / a.length : 0, all = by.all || [0, 0, 0, 0, 0, 0, 0, 0];
    const net = k => by[k] ? (by[k][1] - by[k][3]) / a.length : 0;
    rows.push([gp, f1(n('all')), f1(l('all')), f1(net('all')), `${f1(n('mech:stub'))} / ${f1(n('mech:newborn'))} / ${f1(n('mech:other'))}`, `${f1(l('mech:stub'))} / ${f1(l('mech:newborn'))} / ${f1(l('mech:other'))}`,
      `${f1(n('blk:e'))} / ${f1(n('blk:a'))} / ${f1(n('blk:s'))}`, `${f1(l('size:small'))} / ${f1(l('size:mid'))} / ${f1(l('size:big'))}`, `${f1(net('size:small'))} / ${f1(net('size:mid'))} / ${f1(net('size:big'))}`, f1(l('king:1')), pc(all[3] / Math.max(1, all[2]))]);
  }
  out.tables['trap_' + kind] = res;
  P(`\n### ${kind}\n` + table(['group', 'n', 'len', 'net loss (len − own re-eaten)', 'n stub / newborn / other', 'len stub / newborn / other', 'n blocked by enemy / ally / self-kelp', 'len L≤4 / 5–7 / ≥8', 'net loss L≤4 / 5–7 / ≥8', 'king (≥8) len', 'drops re-eaten by own'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
// 7b. Head-on contacts with the enemy by lengths
P(`\n## 7b. Head-on contacts with the enemy (per team-game): who rams whom, and who eats the pearls`);
for (const kind of ['elim', 'r500']) {
  const rows = [];
  const res = {};
  for (const gp of GROUPS) {
    const a = sel(gp, t => kindOf(t) === kind); if (!a.length) continue;
    const by = {};
    for (const t of a) for (const [k, v] of Object.entries(t.T.ct || {})) {
      const [role, olc, tlc, ph, spr, king] = k.split('|');
      const oc = ['2', '3'].includes(olc) ? 'L≤3' : olc === '4' || olc === '5-7' ? 'L4–7' : 'L≥8';
      const tc = ['2', '3'].includes(tlc) ? 'L≤3' : tlc === '4' || tlc === '5-7' ? 'L4–7' : 'L≥8';
      for (const kk of [role + ':' + oc + '>' + tc, role + ':all', role + ':spr' + spr, role + ':king' + king]) { const x = by[kk] || (by[kk] = [0, 0, 0, 0, 0, 0, 0]); for (let i = 0; i < 7; i++) x[i] += v[i]; }
    }
    // exact pearl fate from the death tables of both sides: ours (T.dt) and theirs (O.dt)
    const dsum = (tgs, side, cause) => { const x = [0, 0, 0, 0, 0, 0, 0, 0]; for (const t of tgs) for (const [k, v] of Object.entries(side === 'us' ? t.T.dt : t.O.dt)) if (k.startsWith(cause + '|')) for (let i = 0; i < 8; i++) x[i] += v[i]; return x; };
    const fate = {
      ram: { ours: dsum(a, 'us', 'ram'), theirs: dsum(a, 'them', 'rammed') },    // our rammers and their victims
      rammed: { ours: dsum(a, 'us', 'rammed'), theirs: dsum(a, 'them', 'ram') }, // our victims and their rammers
    };
    by.fate = fate;
    res[gp] = by;
    for (const role of ['ram', 'rammed']) {
      const all = by[role + ':all']; if (!all) continue;
      const cells = [];
      for (const oc of ['L≤3', 'L4–7', 'L≥8']) for (const tc of ['L≤3', 'L4–7', 'L≥8']) { const x = by[role + ':' + oc + '>' + tc]; if (x && x[0] / a.length >= 0.05) cells.push(`${oc}→${tc} ${f1(x[0] / a.length, 2)}`); }
      const F = fate[role];
      // ours: [n,len,drops,eatOwn(us),eatOwnKing,eatEnemy(them)]; theirs (their deaths): eatOwn = them, eatEnemy = us
      const usGain = F.ours[3] + F.theirs[5], themGain = F.ours[5] + F.theirs[3], drops = F.ours[2] + F.theirs[2];
      rows.push([gp, role, f1(all[0] / a.length, 2), f1(all[1] / a.length), f1(all[2] / a.length), pc((by[role + ':spr1'] || [0])[0] / all[0]), f1((by[role + ':king1'] || [0])[0] / a.length, 2),
        pc(F.ours[3] / Math.max(1, F.ours[2])), pc(F.ours[5] / Math.max(1, F.ours[2])), pc(F.theirs[5] / Math.max(1, F.theirs[2])), pc(F.theirs[3] / Math.max(1, F.theirs[2])),
        `${f1(usGain / a.length)} / ${f1(themGain / a.length)} (of ${f1(drops / a.length)})`, cells.join('; ')]);
    }
  }
  out.tables['contact_' + kind] = res;
  P(`\n### ${kind}\n` + table(['group', 'role', 'n', 'our len', 'their len', 'mover sprinted', 'our king (≥8) involved', 'our drops: we eat', 'they eat', 'their drops: we eat', 'they eat', 'pearls from these trades: us / them (of drops)', 'our class → their class (n/tg ≥0.05)'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
// 8b. Denial per map
P(`\n## 8b. Denial per map: share of each territory's natural spawns eaten by us / by them`);
{
  const rows = [];
  const res = {};
  for (const mp of ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma', 'Devil', 'Trophy', 'PD6', 'PD10', 'Queen Of Spades', 'Default']) {
    res[mp] = {};
    for (const gp of GROUPS) {
      const a = sel(gp, t => mapKey(t) === mp); if (!a.length) continue;
      const S = f => sumA(a.map(t => f(t.m)));
      const v = { n: a.length, ownByUs: S(m => m.natOwn) / Math.max(1, S(m => m.supplyOwn)), ownByThem: S(m => m.oppNatInOurs) / Math.max(1, S(m => m.supplyOwn)), theirsByUs: S(m => m.natEnemy) / Math.max(1, S(m => m.supplyEnemy)),
        fOwnByUs: S(m => m.fOwn) / Math.max(1, S(m => m.fSupplyOwn)), fOwnByThem: S(m => m.oppFInOurs) / Math.max(1, S(m => m.fSupplyOwn)), fTheirsByUs: S(m => m.fEnemy) / Math.max(1, S(m => m.fSupplyEnemy)),
        supplyOwn: S(m => m.supplyOwn) / a.length, natEnemy: S(m => m.natEnemy) / a.length, oppIn: S(m => m.oppNatInOurs) / a.length };
      res[mp][gp] = v;
      rows.push([mp, gp, a.length, f1(v.supplyOwn), pc(v.ownByUs), pc(v.ownByThem), pc(v.theirsByUs), f1(v.natEnemy), f1(v.oppIn), pc(v.fOwnByUs), pc(v.fOwnByThem), pc(v.fTheirsByUs)]);
    }
  }
  out.tables.denialMap = res;
  P(table(['map', 'group', 'n', 'own-terr. spawns', 'own spawns: we eat', 'they eat', 'their spawns: we eat', 'we eat in theirs (n)', 'they eat in ours (n)', 'own fountains: we', 'they', 'their fountains: we'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
// 11. Paired winner - loser (top-vs-top), per kind
const KEYM = {
  natIntake: m => m.nat, ownDropEaten: m => m.ownDrop, enemyDropEaten: m => m.enemyDrop, natInEnemyTerr: m => m.natEnemy, natOwnTerr: m => m.natOwn,
  enemyAteInOurs: m => m.oppNatInOurs, sprint: m => m.sprint, sacLen: m => m.dl_sac, sacNet: m => m.dl_sac - m.oSac, trapLen: m => m.dl_trap, trapNet: m => m.dl_trap - m.oTrap,
  rammedLen: m => m.dl_rammed, ramLen: m => m.dl_ram, ramKilled: m => m.ramEnemy, contactNet: m => m.contactKilled - m.contactLost, allyHead: m => m.dl_allyHead,
  kingDeathLen: m => m.kdLen, splits: m => m.splitN, u100: m => m.u100, tot300: m => m.tot300, k300: m => m.k300, k400: m => m.k400, sh400: m => m.sh400,
  finalTotal: m => m.final, finalKing: m => m.finalKing, finalShare: m => m.final > 0 ? m.finalKing / m.final : NaN, finalUnits: m => m.finalUnits,
  linSac: m => m.lin ? m.lin.oSac : NaN, linNat: m => m.lin ? m.lin.nat : NaN, linL350: m => m.lin ? m.lin.Lt : NaN, linLeft: m => m.lin ? m.lin.lossPath + m.lin.lossOff : NaN,
  sacOnset: m => m.sacOnset, sacMed: m => m.sacMed, peakUnitsR: m => m.peakUnitsR, peakTotalR: m => m.peakTotalR,
};
P(`\n## 11. Top-vs-top: winner − loser, paired within game (mean [95% bootstrap])`);
for (const kind of ['elim', 'r500']) {
  const byGame = new Map();
  for (const t of TG) if ((t.grp === 'TW' || t.grp === 'TL') && kindOf(t) === kind) { if (!byGame.has(t.g.key)) byGame.set(t.g.key, {}); byGame.get(t.g.key)[t.grp] = t; }
  const pairs = [...byGame.values()].filter(x => x.TW && x.TL);
  const rows = [];
  const res = {};
  for (const [name, f] of Object.entries(KEYM)) {
    const d = [], w = [], l = [];
    for (const p of pairs) { const a = f(p.TW.m), b = f(p.TL.m); if (Number.isFinite(a) && Number.isFinite(b)) { d.push(a - b); w.push(a); l.push(b); } }
    if (d.length < 5) continue;
    const [lo, hi] = bootMean(d);
    res[name] = { n: d.length, W: mean(w), L: mean(l), d: mean(d), lo, hi };
    rows.push([name, d.length, f1(mean(w)), f1(mean(l)), `${sg(mean(d))} [${sg(lo)}, ${sg(hi)}]`]);
  }
  out.tables['pairedWL_' + kind] = res;
  P(`\n### ${kind} (${pairs.length} games)\n` + table(['metric', 'n', 'winner', 'loser', 'W − L'], rows));
}

// 12. Contrast: our bots vs top winners (and vs the top opponents in our games), r500 games that reached r500 and elim
P(`\n## 12. Contrast: group means and differences vs TW (bootstrap 95%)`);
for (const [kind, lim] of [['r500', true], ['elim', false]]) {
  const cols = ['TW', 'TL', 'T7W', 'X', 'g4r4', 'merge2', 'swarm8', 'px9d', 'px8', 'pxking'];
  const rows = [];
  const res = {};
  const A = {}; for (const c of cols) A[c] = sel(c, t => kindOf(t) === kind && (!lim || t.m.limit));
  for (const [name, f] of Object.entries(KEYM)) {
    const vals = {}; for (const c of cols) vals[c] = A[c].map(t => f(t.m)).filter(Number.isFinite);
    const r = [name];
    for (const c of cols) r.push(f1(mean(vals[c])));
    for (const c of ['swarm8', 'px9d', 'merge2']) { const [lo, hi] = bootDiff(vals.TW, vals[c]); r.push(`${sg(mean(vals[c]) - mean(vals.TW))} [${sg(lo)}, ${sg(hi)}]`); }
    res[name] = Object.fromEntries(cols.map(c => [c, mean(vals[c])]));
    rows.push(r);
  }
  out.tables['contrast_' + kind] = res;
  P(`\n### ${kind}${lim ? ' (games that reached r500)' : ''}: n = ${cols.map(c => c + ' ' + A[c].length).join(', ')}\n` + table(['metric', ...cols, 'swarm8 − TW', 'px9d − TW', 'merge2 − TW'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
// 13. Top-vs-top: which leads predict the winner (share of games where the side ahead on the metric wins; ties dropped)
P(`\n## 13. Top-vs-top: P(win | ahead on metric), per kind (ties dropped; n = games with a leader)`);
{
  const LEAD = {
    'units r50': m => m.u50, 'units r100': m => m.u100, 'total r100': m => m.tot100, 'total r200': m => m.tot200, 'total r300': m => m.tot300, 'total r400': m => m.tot400,
    'king r300': m => m.k300, 'king r400': m => m.k400, 'king r450': m => m.k450, 'nat intake (game)': m => m.nat, 'nat in enemy terr. (game)': m => m.natEnemy,
    'sac len (game)': m => m.dl_sac, 'contact net (game)': m => m.contactKilled - m.contactLost, 'trap net loss (game, lower)': m => -(m.dl_trap - m.oTrap),
    'king lineage sac gain r350+': m => m.lin ? m.lin.oSac : NaN,
  };
  const rows = [];
  const res = {};
  for (const kind of ['elim', 'r500']) {
    const byGame = new Map();
    for (const t of TG) if ((t.grp === 'TW' || t.grp === 'TL') && kindOf(t) === kind) { if (!byGame.has(t.g.key)) byGame.set(t.g.key, {}); byGame.get(t.g.key)[t.grp] = t; }
    const pairs = [...byGame.values()].filter(x => x.TW && x.TL);
    res[kind] = {};
    for (const [name, f] of Object.entries(LEAD)) {
      let n = 0, w = 0;
      for (const p of pairs) { const a = f(p.TW.m), b = f(p.TL.m); if (!Number.isFinite(a) || !Number.isFinite(b) || a === b) continue; n++; if (a > b) w++; }
      res[kind][name] = { n, P: n ? w / n : NaN };
      rows.push([kind, name, n, pc(n ? w / n : NaN)]);
    }
  }
  out.tables.leadPredicts = res;
  P(table(['kind', 'metric', 'n games with a leader', 'leader wins'], rows));
}

// 14. Per top team (sample): r500 maps (games that reached r500) and elim maps
P(`\n## 14. Per top team (top-vs-top team-games): range of styles`);
{
  const rows = [];
  const res = {};
  const names = [...new Set(TG.filter(t => t.g.src === 'top').map(t => t.name))];
  for (const nm of names) {
    const a5 = TG.filter(t => t.g.src === 'top' && t.name === nm && kindOf(t) === 'r500' && t.m.limit);
    const ae = TG.filter(t => t.g.src === 'top' && t.name === nm && kindOf(t) === 'elim');
    const all = TG.filter(t => t.g.src === 'top' && t.name === nm);
    if (all.length < 30) continue;
    const mm = (a, f) => mean(a.map(t => f(t.m)).filter(Number.isFinite));
    const v = { n: all.length, win: mean(all.map(t => t.win ? 1 : 0)), n5: a5.length, k500: mm(a5, m => m.finalKing), tot500: mm(a5, m => m.final), share: mm(a5, m => m.final > 0 ? m.finalKing / m.final : NaN),
      linSac: mm(a5, m => m.lin ? m.lin.oSac : NaN), sacOn: median(a5.map(t => t.m.sacOnset).filter(Number.isFinite)), nat5: mm(a5, m => m.nat),
      invade5: sumA(a5.map(t => t.m.natEnemy)) / Math.max(1, sumA(a5.map(t => t.m.supplyEnemy))), lostOwn5: sumA(a5.map(t => t.m.oppNatInOurs)) / Math.max(1, sumA(a5.map(t => t.m.supplyOwn))),
      u100e: mm(ae, m => m.u100), contactE: mm(ae, m => m.contactKilled - m.contactLost), ramsE: mm(ae, m => m.ramN), invadeE: sumA(ae.map(t => t.m.natEnemy)) / Math.max(1, sumA(ae.map(t => t.m.supplyEnemy))) };
    res[nm] = v;
    rows.push([nm, v.n, pc(v.win), v.n5, f1(v.k500), f1(v.tot500), pc(v.share), f1(v.linSac), f1(v.sacOn, 0), f1(v.nat5, 0), pc(v.invade5), pc(v.lostOwn5), f1(v.u100e), f1(v.ramsE, 1), sg(v.contactE), pc(v.invadeE)]);
  }
  rows.sort((x, y) => parseFloat(y[2]) - parseFloat(x[2]));
  out.tables.perTeam = res;
  P(table(['team', 'team-games', 'win', 'r500 games (reached)', 'king r500', 'total r500', 'king share', 'lineage sac gain r350+', 'sac onset (median)', 'nat intake r500 maps', 'enemy-terr. spawns eaten', 'own-terr. spawns lost', 'units r100 (elim)', 'rams (elim)', 'contact net (elim)', 'enemy-terr. eaten (elim)'], rows));
}

// ---------------------------------------------------------------------------------------------------------------
// 10. Per map, key end-state and spending numbers (r500 maps: games that reached r500)
P(`\n## 10. Per map: final king, total, share, units; sac and trap length; king death length (per team-game)`);
{
  const rows = [];
  const res = {};
  for (const mp of ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma', 'Devil', 'Trophy', 'PD6', 'PD10', 'Queen Of Spades', 'Default']) {
    res[mp] = {};
    for (const gp of GROUPS) {
      const a = sel(gp, t => mapKey(t) === mp && (ML.R500.includes(t.g.map) ? t.m.limit : true)); if (!a.length) continue;
      const mm = f => mean(a.map(t => f(t.m)));
      const v = { n: a.length, win: mean(a.map(t => t.win ? 1 : 0)), king: mm(m => m.finalKing), total: mm(m => m.final), units: mm(m => m.finalUnits), share: mean(a.filter(t => t.m.final > 0).map(t => t.m.finalKing / t.m.final)),
        inflow: mm(m => m.inflow), sac: mm(m => m.dl_sac), trap: mm(m => m.dl_trap), contact: mm(m => m.contactLost), kd: mm(m => m.kdLen), sprint: mm(m => m.sprint), k400: mean(a.map(t => t.m.k400).filter(Number.isFinite)),
        tot300: mean(a.map(t => t.m.tot300).filter(Number.isFinite)), peakTotalR: median(a.map(t => t.m.peakTotalR)), sacOnset: median(a.map(t => t.m.sacOnset).filter(Number.isFinite)), nSac: a.filter(t => Number.isFinite(t.m.sacOnset)).length };
      res[mp][gp] = v;
      rows.push([mp, gp, v.n, pc(v.win), f1(v.king), f1(v.total), pc(v.share), f1(v.units), f1(v.k400), f1(v.tot300), f1(v.inflow), f1(v.sprint), f1(v.sac), f1(v.trap), f1(v.contact), f1(v.kd), f1(v.peakTotalR, 0), `${f1(v.sacOnset, 0)} (${v.nSac})`]);
    }
  }
  out.tables.perMap = res;
  P(table(['map', 'group', 'n', 'win', 'final king', 'final total', 'king share', 'units', 'king r400', 'total r300', 'inflow', '−sprint', '−sac', '−trap', '−contact', 'king death len', 'peak total round (median)', 'sac onset (median, n)'], rows));
}

fs.writeFileSync(OUT + '.md', md.join('\n') + '\n');
fs.writeFileSync(OUT + '.json', JSON.stringify(out, (k, v) => typeof v === 'number' && !Number.isInteger(v) ? Math.round(v * 1000) / 1000 : v));
console.log(`wrote ${path.relative(ROOT, OUT)}.md and .json (${TG.length} team-games)`);
module.exports = { TG, sel, metrics };
