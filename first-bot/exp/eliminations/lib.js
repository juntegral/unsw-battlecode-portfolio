// Shared loading, labels and the pre-registered classification rules of the elimination study (research/observations/our-eliminations.md).
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib');
const ROOT = path.resolve(__dirname, '..', '..');
const CACHE = path.join(__dirname, 'cache');

// The primary sample: every online set against the elite except r1-online, r1-autoscrim, g1, g2 (user rule), in wave order.
const SETS = [
  ['baseline-r1', 'g4r4', 'g4'], ['baseline-r1b', 'g4r4', 'g4'], ['baseline-r1c', 'g4r4', 'g4'], ['px-king-v2-online', 'pxking', 'proxy'],
  ['cand-avoid6-online', 'avoid6', 'g4'], ['cand-portal1-online', 'portal1', 'g4'], ['base-px8-online', 'px8', 'proxy'], ['cand-merge2-online', 'merge2', 'g4'],
  ['cand-swarm8-online', 'swarm8', 'g4'], ['base-px9d-online', 'px9d', 'proxy'], ['cand-merge2-online-r2', 'merge2', 'g4'], ['cand-merge2-online-r3', 'merge2', 'g4'],
  ['cand-stack1-online', 'stack1', 'g4'], ['cand-stack2-online', 'stack2', 'g4'], ['cand-stack3-online', 'stack3', 'g4'],
];
const BOT = Object.fromEntries(SETS.map(s => [s[0], s[1]])), FAMILY = Object.fromEntries(SETS.map(s => [s[0], s[2]]));
const ELITE = { 306: 'Cutlery', 70: 'cheji bt', 20: 'calc', 801: '中国必须人能飞😡', 264: 'forgot to mention', 46: 'Sabotage-d' };
const DEV = 545;
const ELIM_MAPS = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default'];
const R500_MAPS = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const kindOf = m => ELIM_MAPS.includes(m) ? 'elim' : 'r500';
const CAUSE = ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'];
const CAUSE_KO = ['자해(빈 이웃 있음)', '갇힘', '박힘', '돌진(우리가 박음)', '적 몸통에 부딪힘', '아군 머리', '시간 초과', '질주 불가'];

function readGz(file) {
  if (!fs.existsSync(file)) return [];
  // Z_SYNC_FLUSH tolerates a member still being written at the end of the file (extraction running); a cut line is dropped
  const txt = zlib.gunzipSync(fs.readFileSync(file), { finishFlush: zlib.constants.Z_SYNC_FLUSH }).toString('utf8');
  const out = []; for (const l of txt.split('\n')) { if (!l.trim()) continue; try { out.push(JSON.parse(l)); } catch { /* partial line */ } }
  return out;
}
// pearl layout of a game: PD by start dragons (6 = a, 10 = b); the four two-layout maps by the replay's discriminating spawns
// (tools/mech_check.js layoutTruth), else exp/territory-analysis variantOf (variants.json, spawn counts); single-layout maps a
function layoutOf(g) {
  if (g.map === 'Prisoners Dilemma') return g.nInit === 10 ? 'b' : 'a';
  if (!['Devil', 'Queen Of Spades', 'Schooltime', 'Slithery Fight'].includes(g.map)) return 'a';
  if (g.lay === 'a' || g.lay === 'b') return g.lay;
  return g.lay2 || '?';
}
const mapLay = g => g.map === 'Prisoners Dilemma' ? (g.nInit === 10 ? 'PD10' : 'PD6') : ['Devil', 'Queen Of Spades', 'Schooltime', 'Slithery Fight'].includes(g.map) ? g.map + ' ' + layoutOf(g) : g.map;

function loadOnline() {
  const out = [];
  for (const [set, bot, fam] of SETS) for (const g of readGz(path.join(CACHE, 'online-' + set + '.jsonl.gz'))) {
    g.bot = bot; g.fam = fam; g.layout = layoutOf(g); g.ml2 = mapLay(g);
    g.elite = !!ELITE[g.oppId]; g.dev = +g.oppId === DEV;
    g.oppName = ELITE[g.oppId] || (g.dev ? 'dev test 1 :P' : g.opp);
    g.them = g.us === 'A' ? 'B' : 'A';
    g.U = g.T[g.us]; g.E = g.T[g.them];
    g.win = g.winner === g.us ? 1 : 0;
    g.elim = g.U.end.u === 0 ? 1 : 0;
    out.push(g);
  }
  return out;
}
// top games: stalled team (splits <= 3 and no sonar) or >= 3 timeouts -> excluded (the rule of the mass ledger / territory study)
function loadTop(file) {
  const all = readGz(file || path.join(CACHE, 'top.jsonl.gz')), out = [], excl = { stalled: 0, faults: 0 };
  for (const g of all) {
    const st = ['A', 'B'].some(t => g.health[t].splits <= 3 && g.health[t].sonar === 0);
    const fa = ['A', 'B'].some(t => g.T[t].faults >= 3);
    if (st) { excl.stalled++; continue; }
    if (fa) { excl.faults++; continue; }
    g.layout = layoutOf(g); g.ml2 = mapLay(g);
    out.push(g);
  }
  return { games: out, excl, n: all.length };
}
// value of a series at round r: units / total / longest at the first turn of round r; after the game ended the final state
function at(g, tm, r, what = 'u') {
  const T = g.T[tm];
  if (r >= g.rounds) return T.end[what];
  const i = Math.floor(r / g.step), v = T.ser[what][i];
  return v === undefined ? T.end[what] : v;
}
const alive = (g, tm, r) => !(g.T[tm].elim >= 0 && g.T[tm].elim < r);

// ---- pre-registered classes (written before any result was looked at) ----
// Enemy action: rammed, ram, enemyBody, or a trap with an enemy body among the blockers.
const byEnemy = (cause, blk) => cause === 2 || cause === 3 || cause === 4 || (cause === 1 && blk === 'e');
// Death mode of one death row [r, len, cause, ks, eV, aV, king, klen, kage, u, eu, blk, eMin, portal, mech]
function modeOf(row) {
  const [, , cause, ks, , , , , , , , blk] = row;
  if (row[14] === 1 && cause !== 2 && cause !== 3) return 'stub'; // an escape-split loop's stub (or the front of a 2+2 split) dying in place
  if (cause === 2) return ks >= 2 ? 'sprintRam' : 'stepRam';
  if (cause === 3) return 'ourRam';
  if (cause === 1) return blk === 'e' ? 'trapE' : 'trapSelf';
  if (cause === 4) return 'enemyBody';
  if (cause === 0) return 'sac';
  if (cause === 5) return 'allyHead';
  return cause === 6 ? 'fault' : 'sprintDeath';
}
const MODE_KO = { stub: '분열 토막(2라운드 안에 ≤3칸 남기고 분열한 쪽)', sprintRam: '질주 박힘(2걸음+)', stepRam: '한 걸음 박힘', ourRam: '우리가 박음(맞교환)', trapE: '갇힘(적 몸 막음)', trapSelf: '갇힘(제 몸·아군·해초)',
  enemyBody: '적 몸통에 부딪힘', sac: '자해(빈 이웃 있음)', allyHead: '아군 머리', fault: '시간 초과', sprintDeath: '질주 불가' };
// Elimination class of an eliminated team-game. kd = its deaths of length >= 8 (rows), elim = elimination round.
//   E1 early overrun: eliminated before r100.
//   E2 king kill: from r100, the team's longest dragon (length >= 8) died by enemy action in the 30 rounds up to the elimination.
//   E3 attrition: from r100 otherwise; E3m mid (r100-299), E3l late (r300+).
function classOf(elim, kd) {
  if (elim < 100) return 'E1';
  const k = kd.find(row => row[6] === 1 && row[0] >= elim - 30 && byEnemy(row[2], row[11]));
  if (k) return 'E2';
  return elim < 300 ? 'E3m' : 'E3l';
}
const CLASS_KO = { E1: '조기 압도(r100 전 전멸)', E2: '왕 사냥(전멸 30라운드 안에 왕이 적에게 죽음)', E3m: '중반 소모(r100–299, 왕 사냥 아님)', E3l: '후반 소모(r300+, 왕 사냥 아님)' };
// the king was lost to the enemy earlier (more than 30 rounds before the elimination)
const kingLostEarlier = (elim, kd) => kd.some(row => row[6] === 1 && row[0] < elim - 30 && byEnemy(row[2], row[11]));

// ---- small stats and tables ----
const sum = xs => xs.reduce((s, v) => s + v, 0);
const mean = xs => xs.length ? sum(xs) / xs.length : null;
function quant(xs, q) { if (!xs.length) return null; const s = xs.slice().sort((a, b) => a - b); const i = (s.length - 1) * q, lo = Math.floor(i), hi = Math.ceil(i); return s[lo] + (s[hi] - s[lo]) * (i - lo); }
const med = xs => quant(xs, 0.5);
const f1 = v => v === null || v === undefined || Number.isNaN(v) ? '–' : (Math.round(v * 10) / 10).toFixed(1);
const f2 = v => v === null || v === undefined || Number.isNaN(v) ? '–' : (Math.round(v * 100) / 100).toFixed(2);
const pc = (a, b) => b ? Math.round(100 * a / b) + '%' : '–';
const pc1 = (a, b) => b ? (Math.round(1000 * a / b) / 10).toFixed(1) + '%' : '–';
function table(head, rows, align) {
  const L = ['| ' + head.join(' | ') + ' |', '|' + head.map((_, i) => (align && align[i] === 'l') || (!align && i === 0) ? '---' : '---:').join('|') + '|'];
  for (const r of rows) L.push('| ' + r.join(' | ') + ' |');
  return L.join('\n');
}
// Wilson 95% interval for a proportion
function wilson(k, n) { if (!n) return [null, null]; const z = 1.96, p = k / n, d = 1 + z * z / n, c = p + z * z / (2 * n), s = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return [(c - s) / d, (c + s) / d]; }
// bootstrap 95% interval of a mean (deterministic)
function bootMean(xs, B = 400) {
  if (xs.length < 2) return [null, null];
  let s = 12345; const rnd = () => { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; };
  const ms = []; for (let b = 0; b < B; b++) { let t = 0; for (let i = 0; i < xs.length; i++) t += xs[Math.floor(rnd() * xs.length)]; ms.push(t / xs.length); }
  return [quant(ms, 0.025), quant(ms, 0.975)];
}

module.exports = { ROOT, CACHE, SETS, BOT, FAMILY, ELITE, DEV, ELIM_MAPS, R500_MAPS, kindOf, CAUSE, CAUSE_KO, readGz, layoutOf, mapLay, loadOnline, loadTop, at, alive,
  byEnemy, modeOf, MODE_KO, classOf, CLASS_KO, kingLostEarlier, sum, mean, quant, med, f1, f2, pc, pc1, table, wilson, bootMean };
