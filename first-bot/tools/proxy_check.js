#!/usr/bin/env node
// Top-team proxy bots (bots/proxy_*): run games, measure them with the tools used on the top teams, compare.
//
// usage (from the repo root):
//   node tools/proxy_check.js targets [--jobs 3]
//       Per-side metrics of the top-team snapshot (data/top/snapshot-20260929a.keys; features from data/top/features.jsonl,
//       bodies re-simulated by tools/fragment_study.js study()). Cached in exp/proxy-check/top-sides.jsonl.
//   node tools/proxy_check.js run --label <L> --pairs a:b[,c:d...] [--maps all|name,name] [--seeds 1,2] [--jobs 3] [--both-sides]
//       Plays every pair x map x seed (and swapped sides with --both-sides) on maps/online-20260927 with tools/unswbc
//       --sandbox into exp/<L>/games/<a>__<b>__<map>__<seed>/game.replay (manifest exp/<L>/games.jsonl), then measures
//       each game into exp/<L>/sides.jsonl. A bot is `bot` (our bot/), a name under bots/, or a directory path.
//       At most --jobs games at once (capped at 3); no new game when free disk < 20 GiB.
//   node tools/proxy_check.js measure --label <L>
//       (Re)measures the replays of an eval.js or run label (exp/<L>/games/*/game.replay) into exp/<L>/sides.jsonl.
//   node tools/proxy_check.js online --dir data/online/<batch> --out exp/<L> [--team 583]
//       Measures our bot's online games (M<id>.replay + game-<id>.json) into exp/<L>/sides.jsonl.
//   node tools/proxy_check.js report --label <L>[,<L2>...] --bot <name> [--target all|cheji|K|<team name>] [--json <file>]
//       Prints the distributions of bot <name>'s sides next to the top-team target (all = every top team but SSS;
//       cheji = cheji bt; K = Kamikaze and 中国必须人能飞😡).
//   node tools/proxy_check.js vsbot --label <L>[,...] [--online <L>[,...]] [--by-team] [--brief] [--json <file>]
//       Our bot (sides named "bot" / team 583) against each opponent: win rate and G by map, how its long dragons die,
//       units and longest curves; online labels are shown next to the local ones.
//   node tools/proxy_check.js summary --runs <label>:<bot>:<target>[,...]
//       One line of key numbers per run (value and value/target), for the calibration record.
//   node tools/proxy_check.js mass --label <L>[,...] [--bot <name>]
//       Per 50-round window and running side: pearls eaten, length lost in own deaths, deaths, splits (default: the
//       non-bot sides, e.g. the opponents of our bot).
//   node tools/proxy_check.js sync
//       Copies the shared proxy sources from bots/proxy_swarm to the other bots/proxy_* directories (style.hpp stays).
//
// Definitions follow research/observations/top-fragments.md (tools/fragment_study.js): a side = one team in one game;
// "free exit" = at least one of the four neighbour tiles was neither kelp nor body at the start of the dying turn;
// exit sacrifices = self-kills (no action or illegal split) plus first-step kelp/own-body deaths with a free exit.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const TOP = path.join(ROOT, 'data', 'top');
const PC = path.join(ROOT, 'exp', 'proxy-check');
const TOP_CACHE = path.join(PC, 'top-sides.jsonl');
const KEYS = path.join(TOP, 'snapshot-20260929a.keys');
const MAPDIR = path.join(ROOT, 'maps', 'online-20260927');
const TEAMS = ['A', 'B'], TI = { A: 0, B: 1 };
const SSS = 'SSS', SSS_BROKEN_SPLITS = 10;
const OUR_TEAM_ID = 583;
const K_TEAMS = ['Kamikaze', '中国必须人能飞😡'];
const MAP_KEYS = ['autarky', 'default', 'devil', 'portals', 'prisoners_dilemma', 'queen_of_spades', 'schooltime', 'slithery_fight', 'trauma', 'trophy'];
const ELIM_MAPS = ['devil', 'trophy', 'prisoners_dilemma', 'queen_of_spades', 'default'];
const mapKey = name => String(name).toLowerCase().replace(/\.map$/, '').replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');

// ---------------------------------------------------------------------------------------------------------------
// Statistics helpers
const sum = a => a.reduce((x, y) => x + y, 0);
const mean = a => a.length ? sum(a) / a.length : null;
const sorted = a => a.slice().sort((x, y) => x - y);
function quant(a, p) { if (!a.length) return null; const s = sorted(a), pos = (s.length - 1) * p, lo = Math.floor(pos), hi = Math.ceil(pos); return s[lo] + (s[hi] - s[lo]) * (pos - lo); }
const med = a => quant(a, 0.5);
const share = (n, d) => d ? n / d : null;
const f1 = x => x === null || x === undefined || Number.isNaN(x) ? '-' : Math.abs(x) >= 100 ? x.toFixed(0) : Math.abs(x) >= 10 ? x.toFixed(1) : x.toFixed(2);
const pc = x => x === null || x === undefined || Number.isNaN(x) ? '-' : (100 * x).toFixed(1) + '%';
const ratio = (a, b) => a === null || b === null || !b ? '-' : (a / b).toFixed(2);

// ---------------------------------------------------------------------------------------------------------------
// Measurement of one replay: features (tools/top_features.js extract) + body simulation (tools/fragment_study.js study).
let _load = null;
function loader() { if (!_load) { const tf = require('./top_features.js'); _load = tf.makeLoader(tf.viewerSource()); } return _load; }
function fragStudy() {
  // fragment_study.js installs a child-process handler when argv holds --child; this worker uses another flag.
  return require('./fragment_study.js');
}

function cause(d) {
  if (d.reason === 'A') return d.why === 'suicide' ? 'A-suicide' : d.why === 'split' ? 'A-split' : 'A-other';
  if (d.reason === 'O') return d.hitTeam === d.team ? 'O-own' : 'O-enemy';
  if (d.reason === 'H') { const other = d.mover ? d.hitTeam : d.byTeam; return other === d.team ? 'H-own' : 'H-enemy'; }
  return d.reason;
}
function modeCat(d) {
  const c = cause(d);
  if (c === 'A-suicide' || c === 'A-split') return d.freeN > 0 ? 'self-free' : 'self-trapped';
  if (c === 'W' || c === 'S') return d.step > 0 ? 'WS-sprint' : d.freeN > 0 ? 'WS-free' : 'WS-trapped';
  if (c === 'H-enemy') return d.mover ? 'H-ram' : 'H-rammed';
  return c;
}
const MODES = ['self-free', 'self-trapped', 'WS-free', 'WS-trapped', 'WS-sprint', 'O-own', 'O-enemy', 'H-ram', 'H-rammed', 'H-own', 'A-other'];
function splitCat(L, c) {
  if (L === 4 && c === 2) return '2+2';
  if (Math.abs(2 * c - L) <= 1) return 'half';
  if (c <= 3) return 'peel';
  if (L - c <= 3) return 'stub';
  return 'other';
}
const SPLIT_CATS = ['2+2', 'half', 'peel', 'stub', 'other'];
const childBin = c => c <= 4 ? String(c) : c <= 9 ? '5-9' : '10+';
const CHILD_BINS = ['2', '3', '4', '5-9', '10+'];

// One side record per team: compact numbers the report aggregates.
function sideRecords(R, row, names) {
  const tf = require('./top_features.js');
  const f = tf.extract(R, row);
  const g = fragStudy().study(R);
  const out = [];
  const byId = new Map(); for (const d of g.deaths) byId.set(d.id + ':' + d.r + ':' + d.team, d);
  for (const s of TEAMS) {
    const o = s === 'A' ? 'B' : 'A', T = f[s];
    const tl = T.timeline.map(t => [t.units, t.total, t.longest]);
    // splits: g.splits rows = [teamIdx, round, L, c, unitsBefore, ...]
    const sp = g.splits.filter(t => t[0] === TI[s]);
    const cats = {}; for (const c of SPLIT_CATS) cats[c] = 0;
    const child = {}; for (const b of CHILD_BINS) child[b] = 0;
    let bigN = 0, bigStub = 0, last = -1, after450 = 0;
    const perW = new Array(10).fill(0);
    for (const t of sp) {
      cats[splitCat(t[2], t[3])]++; child[childBin(t[3])]++;
      if (t[2] >= 8) { bigN++; if (splitCat(t[2], t[3]) === 'stub') bigStub++; }
      if (t[1] > last) last = t[1];
      if (t[1] >= 450) after450++;
      perW[Math.min(9, Math.floor(t[1] / 50))]++;
    }
    // deaths of this side
    const mine = g.deaths.filter(d => d.team === s);
    const modes = {}; for (const m of MODES) modes[m] = 0;
    for (const d of mine) modes[modeCat(d)]++;
    const free = []; // exit sacrifices: [round, len, distKing, nDrop, own20, king20, kind 0 self-kill / 1 W-S]
    for (const d of mine) {
      const m = modeCat(d);
      if (m !== 'self-free' && m !== 'WS-free') continue;
      let own20 = 0, king20 = 0;
      for (const fa of d.fates) if (fa[0] <= 20 && fa[1] === 0) { own20++; if (fa[3] === 1) king20++; }
      free.push([d.r, d.len, d.distKing, d.nDrop, own20, king20, m === 'self-free' ? 0 : 1]);
    }
    // what the team's longest ate in 400-499 and how much of it came from own exit sacrifices
    let longest400 = 0; const E = g.eat[s]; longest400 = sum(E[4][1]);
    let fromFree400 = 0;
    for (const d of mine) { const m = modeCat(d); if (m !== 'self-free' && m !== 'WS-free') continue; for (const fa of d.fates) if (fa[1] === 0 && fa[2] === 1 && d.r + fa[0] >= 400) fromFree400++; }
    // head-on rams made by this side and the victims' lengths
    const rams = [];
    for (const d of mine) if (d.reason === 'H' && d.mover && d.hitTeam === o) rams.push([d.r, d.len, d.hitLen, d.step]);
    const rammed = mine.filter(d => d.reason === 'H' && !d.mover && d.byTeam === o).length;
    const oKills = g.deaths.filter(d => d.team === o && d.reason === 'O' && d.hitTeam === s).length;
    // ram rate with an enemy head one step away, per length class (<=4, 5-9, >=10)
    const ram = g.geo[s].ram.map(c => [c.nE, c.ramE, +c.rndE.toFixed(3)]);
    // approach toward the nearest visible enemy head (small class): moves, toward, random-toward
    const appr = g.geo[s].appr.map(c => [c.nE, c.aE, +c.bE.toFixed(3), c.nB, c.aB, +c.bB.toFixed(3)]);
    // deaths of long dragons (len >= 6): [round, len, mode, other len, other split-born, rammer sprint step, rammer born round]
    const big = [];
    for (const d of mine) {
      if (d.len < 6) continue;
      const m = modeCat(d);
      let oLen = -1, oSplit = -1, oStep = -1;
      if (m === 'H-rammed') {
        oLen = d.byLen; oSplit = d.bySplitBorn;
        const rm = g.deaths.find(x => x.r === d.r && x.id === d.byId && x.mover);
        if (rm) oStep = rm.step;
      } else if (m === 'H-ram' || m === 'O-enemy') { oLen = d.hitLen; oSplit = d.hitSplitBorn; }
      big.push([d.r, d.len, m, oLen, oSplit, oStep, d.freeN]);
    }
    // nearest ally / enemy head (torus Manhattan) of small pieces (<= 4) at their turns: histograms over all windows
    const hA = new Array(64).fill(0), hE = new Array(64).fill(0);
    for (const w of g.geo[s].dist) for (let i = 0; i < 64; i++) { hA[i] += w[0].hA[i]; hE[i] += w[0].hE[i]; }
    const eaten = T.eaten;
    // per 50-round window: length lost in own deaths and number of own deaths (pearls eaten per window are in eatenW)
    const lostW = new Array(10).fill(0), deathsW = new Array(10).fill(0);
    for (const d of mine) { const w = Math.min(9, Math.floor(d.r / 50)); lostW[w] += d.len; deathsW[w]++; }
    const win = f.meta.winner === s ? 1 : f.meta.winner === o ? 0 : 0.5;
    out.push({
      key: row.key, src: row.src, map: mapKey(row.map), side: s, name: names[s], opp: names[o], win,
      rounds: f.meta.rounds, elim: f.meta.endReason === 'teamEliminated' ? 1 : 0,
      final: [f.meta.final[s].dragonCount, f.meta.final[s].longestDragon, f.meta.final[s].totalLength],
      oppFinal: [f.meta.final[o].dragonCount, f.meta.final[o].longestDragon, f.meta.final[o].totalLength],
      tl, splits: { n: sp.length, cats, child, bigN, bigStub, last, after450, perW },
      modes, deaths: mine.length, free, longest400, fromFree400, rams, rammed, oKills, ram, appr, big,
      eaten100: eaten[0] + eaten[1], eatenAll: sum(eaten), sprints: sum(T.sprints), nearA: hA, nearE: hE,
      eatenW: eaten, lostW, deathsW,
      sonar: T.sonar.pingsPerDragonRound, dragonRounds: T.sonar.dragonRounds,
      checks: { sim: f.meta.simMismatches, ...g.chk },
    });
  }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------
// Worker pool: measure replays in child processes (analysis only, no games).
function measureMany(tasks, jobs, onDone) {
  return new Promise((resolve, reject) => {
    if (!tasks.length) return resolve();
    const queue = tasks.slice(); let live = 0, done = 0;
    const n = Math.min(jobs, queue.length);
    for (let i = 0; i < n; i++) {
      const child = cp.fork(__filename, ['--pc-worker'], { serialization: 'advanced', stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
      live++;
      const next = () => {
        const t = queue.shift();
        if (!t) { child.kill(); if (--live === 0) resolve(); return; }
        child.send(t);
      };
      child.on('message', m => { onDone(m, ++done); next(); });
      child.on('error', reject);
      next();
    }
  });
}
if (process.argv.includes('--pc-worker')) {
  process.on('message', t => {
    try { process.send({ key: t.row.key, recs: sideRecords(loader()(t.file), t.row, t.names), extra: t.extra }); }
    catch (err) { process.send({ key: t.row.key, error: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | ') }); }
  });
}

function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  const out = [];
  for (const l of fs.readFileSync(file, 'utf8').split('\n')) { if (!l.trim()) continue; try { out.push(JSON.parse(l)); } catch { /* partial */ } }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------
// targets: top-team snapshot sides
async function cmdTargets(opt) {
  fs.mkdirSync(PC, { recursive: true });
  const keys = [...new Set(fs.readFileSync(KEYS, 'utf8').split('\n').map(s => s.trim()).filter(Boolean))];
  const keySet = new Set(keys), meta = new Map();
  for (const l of fs.readFileSync(path.join(TOP, 'features.jsonl'), 'utf8').split('\n')) {
    const mm = /^\{"meta":\{"battleId":(\d+),"gameId":(\d+)[,}]/.exec(l); if (!mm) continue;
    const k = mm[1] + ':' + mm[2]; if (!keySet.has(k) || meta.has(k)) continue;
    const f = JSON.parse(l); meta.set(k, { map: f.meta.map, teams: f.meta.teams, winner: f.meta.winner, splitsA: f.A.splits.length, splitsB: f.B.splits.length });
  }
  const have = new Set(readJsonl(TOP_CACHE).map(r => r.key));
  const tasks = [];
  for (const k of keys) {
    if (have.has(k) || !meta.has(k)) continue;
    const m = meta.get(k), [b, gm] = k.split(':');
    tasks.push({ file: path.join(TOP, b, gm + '.replay.gz'), row: { key: k, src: 'top', battleId: +b, gameId: +gm, map: m.map, teamA: m.teams.A.name, teamB: m.teams.B.name, winner: m.winner }, names: { A: m.teams.A.name, B: m.teams.B.name } });
  }
  console.log(`top snapshot ${keys.length} games, cached ${have.size}, to measure ${tasks.length}`);
  const fd = fs.openSync(TOP_CACHE, 'a'); const t0 = Date.now(); let errs = 0;
  await measureMany(tasks, +(opt.jobs || 3), (m, done) => {
    if (m.error) { errs++; console.error('error', m.key, m.error); return; }
    for (const r of m.recs) fs.writeSync(fd, JSON.stringify(r) + '\n');
    if (done % 50 === 0) console.log(`  ${done}/${tasks.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  });
  fs.closeSync(fd);
  console.log(`done in ${((Date.now() - t0) / 1000).toFixed(0)}s, errors ${errs}`);
}

// Top sides used as targets: SSS-broken games dropped, SSS's own side dropped (as tools/fragment_study.js).
function topSides() {
  const all = readJsonl(TOP_CACHE);
  const byKey = new Map(); for (const r of all) { if (!byKey.has(r.key)) byKey.set(r.key, []); byKey.get(r.key).push(r); }
  const out = [];
  for (const [k, rs] of byKey) {
    if (rs.some(r => r.name === SSS && r.splits.n < SSS_BROKEN_SPLITS)) continue;
    for (const r of rs) if (r.name !== SSS) out.push(r);
  }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------
// run: proxy games
const botDir = name => name === 'bot' ? path.join(ROOT, 'bot') : name.includes('/') ? path.resolve(name) : path.join(ROOT, 'bots', name);
const botName = name => name.includes('/') ? path.basename(name) : name;
function freeDiskGiB() { const d = fs.statfsSync(ROOT); return d.bavail * d.bsize / 1024 ** 3; }
function playGame(a, b, mapFile, seed, dir) {
  return new Promise(res => {
    fs.mkdirSync(dir, { recursive: true });
    const p = cp.spawn(path.join(__dirname, 'unswbc'), ['run', mapFile, botDir(a), botDir(b), '--sandbox', '--seed', String(seed), '--no-logs', '--no-draw', '--no-indicator', '-o', path.join(dir, 'game.replay')], { cwd: dir });
    let log = ''; p.stdout.on('data', d => log += d); p.stderr.on('data', d => log += d);
    p.on('error', e => res({ code: -1, log: String(e) }));
    p.on('close', code => res({ code, log }));
  });
}
async function cmdRun(opt) {
  const label = opt.label; if (!label || !opt.pairs) { console.error('need --label and --pairs a:b,...'); process.exit(2); }
  const out = path.join(ROOT, 'exp', label); fs.mkdirSync(path.join(out, 'games'), { recursive: true });
  const maps = !opt.maps || opt.maps === 'all' ? MAP_KEYS : String(opt.maps).split(',').map(mapKey);
  const seeds = String(opt.seeds || '1,2').split(',').map(Number), jobs = Math.min(3, +(opt.jobs || 3));
  const pairs = String(opt.pairs).split(',').map(x => x.split(':'));
  const manifest = path.join(out, 'games.jsonl'), sidesFile = path.join(out, 'sides.jsonl');
  const done = new Set(readJsonl(manifest).map(r => r.key));
  const tasks = [];
  for (const [a, b] of pairs) for (const m of maps) for (const sd of seeds) {
    const variants = opt['both-sides'] && a !== b ? [[a, b], [b, a]] : [[a, b]];
    for (const [x, y] of variants) { const key = [botName(x), botName(y), m, sd].join('__'); if (!done.has(key)) tasks.push({ key, a: x, b: y, map: m, seed: sd }); }
  }
  console.log(`${label}: ${tasks.length} games to play (${done.size} done), jobs ${jobs}`);
  const t0 = Date.now(); let i = 0, n = 0;
  const worker = async () => {
    while (i < tasks.length) {
      const t = tasks[i++];
      if (freeDiskGiB() < 20) { console.error('free disk < 20 GiB: not starting', t.key); continue; }
      const dir = path.join(out, 'games', t.key), mapFile = path.join(MAPDIR, t.map + '.map');
      const g0 = Date.now();
      const r = await playGame(t.a, t.b, mapFile, t.seed, dir);
      const row = { key: t.key, a: botName(t.a), b: botName(t.b), map: t.map, seed: t.seed, exit: r.code, secs: +((Date.now() - g0) / 1000).toFixed(1) };
      const prob = r.log.match(/.*(timed out|exceeded|out of points|Traceback|error:|failed).*/i); if (prob) row.problem = prob[0].slice(0, 200);
      try {
        const recs = sideRecords(loader()(path.join(dir, 'game.replay')), { key: t.key, src: 'local', map: t.map, teamA: botName(t.a), teamB: botName(t.b) }, { A: botName(t.a), B: botName(t.b) });
        for (const rec of recs) fs.appendFileSync(sidesFile, JSON.stringify(rec) + '\n');
        row.winner = recs[0].win === 1 ? 'A' : recs[1].win === 1 ? 'B' : 'draw'; row.rounds = recs[0].rounds;
      } catch (e) { row.error = String(e).slice(0, 200); }
      fs.appendFileSync(manifest, JSON.stringify(row) + '\n');
      n++; console.log(`  [${n}/${tasks.length}] ${t.key} ${row.winner || row.error} r${row.rounds} ${row.secs}s${row.problem ? ' PROBLEM ' + row.problem : ''} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    }
  };
  await Promise.all(Array.from({ length: jobs }, worker));
}

// measure: (re)measure an eval.js label (rows.jsonl + games/<opp>_<map>_<side>_<seed>/game.replay) or a run label
async function cmdMeasure(opt) {
  const out = path.join(ROOT, 'exp', opt.label), sidesFile = path.join(out, 'sides.jsonl');
  const tasks = [];
  if (fs.existsSync(path.join(out, 'rows.jsonl'))) {
    for (const r of readJsonl(path.join(out, 'rows.jsonl'))) {
      if (r.G === undefined) continue;
      const dir = path.join(out, 'games', r.key.replace(/:/g, '_')), file = path.join(dir, 'game.replay');
      if (!fs.existsSync(file)) continue;
      const names = r.side === 'A' ? { A: 'bot', B: r.opp } : { A: r.opp, B: 'bot' };
      tasks.push({ file, row: { key: r.key, src: 'local', map: r.map, teamA: names.A, teamB: names.B }, names });
    }
  } else {
    for (const r of readJsonl(path.join(out, 'games.jsonl'))) {
      const file = path.join(out, 'games', r.key, 'game.replay'); if (!fs.existsSync(file)) continue;
      tasks.push({ file, row: { key: r.key, src: 'local', map: r.map, teamA: r.a, teamB: r.b }, names: { A: r.a, B: r.b } });
    }
  }
  if (fs.existsSync(sidesFile)) fs.renameSync(sidesFile, sidesFile + '.old');
  const fd = fs.openSync(sidesFile, 'a'); let errs = 0;
  await measureMany(tasks, Math.min(3, +(opt.jobs || 3)), m => { if (m.error) { errs++; console.error(m.key, m.error); return; } for (const r of m.recs) fs.writeSync(fd, JSON.stringify(r) + '\n'); });
  fs.closeSync(fd);
  if (fs.existsSync(sidesFile + '.old')) fs.rmSync(sidesFile + '.old');
  console.log(`measured ${tasks.length} games of ${opt.label}, errors ${errs}`);
}

// online: our bot's server games (M<id>.replay + game-<id>.json)
async function cmdOnline(opt) {
  const dir = path.resolve(ROOT, opt.dir), out = path.resolve(ROOT, opt.out || path.join('exp', 'online-' + path.basename(dir)));
  const team = +(opt.team || OUR_TEAM_ID);
  fs.mkdirSync(out, { recursive: true });
  const sidesFile = path.join(out, 'sides.jsonl');
  const tasks = [];
  for (const f of fs.readdirSync(dir).filter(x => /^game-\d+\.json$/.test(x)).sort()) {
    const g = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
    const rep = path.join(dir, 'M' + g.id + '.replay'); if (!fs.existsSync(rep) || g.status !== 'completed') continue;
    const ourSide = g.teamAId === team ? 'A' : g.teamBId === team ? 'B' : null; if (!ourSide) continue;
    const names = ourSide === 'A' ? { A: 'bot', B: g.teamBName } : { A: g.teamAName, B: 'bot' };
    tasks.push({ file: rep, row: { key: String(g.id), src: 'online', map: g.mapName, teamA: names.A, teamB: names.B, winner: g.winner }, names });
  }
  if (fs.existsSync(sidesFile)) fs.rmSync(sidesFile);
  const fd = fs.openSync(sidesFile, 'a'); let errs = 0;
  await measureMany(tasks, Math.min(3, +(opt.jobs || 3)), m => { if (m.error) { errs++; console.error(m.key, m.error); return; } for (const r of m.recs) fs.writeSync(fd, JSON.stringify(r) + '\n'); });
  fs.closeSync(fd);
  console.log(`online ${path.relative(ROOT, dir)}: measured ${tasks.length} games into ${path.relative(ROOT, sidesFile)}, errors ${errs}`);
}

// sync: shared sources from the master proxy directory to the others
function cmdSync() {
  const master = path.join(ROOT, 'bots', 'proxy_swarm'), shared = ['pxcore.cpp', 'pxproto.cpp', 'pxproto.hpp'];
  for (const d of fs.readdirSync(path.join(ROOT, 'bots')).filter(x => x.startsWith('proxy_') && x !== 'proxy_swarm')) {
    for (const f of shared) fs.copyFileSync(path.join(master, f), path.join(ROOT, 'bots', d, f));
    console.log('synced', d);
  }
}

// ---------------------------------------------------------------------------------------------------------------
// report
function loadSides(labels) { const out = []; for (const L of String(labels).split(',')) out.push(...readJsonl(path.join(ROOT, 'exp', L, 'sides.jsonl'))); return out; }
function targetSides(which) {
  const T = topSides();
  if (!which || which === 'all') return T;
  if (which === 'cheji') return T.filter(x => x.name === 'cheji bt');
  if (which === 'K') return T.filter(x => K_TEAMS.includes(x.name));
  return T.filter(x => x.name === which);
}
function curve(S, rs, idx, filt) {
  return rs.map(r => { const run = S.filter(x => (r < x.rounds || (r === 500 && x.rounds === 500)) && (!filt || filt(x))); return run.length ? med(run.map(x => x.tl[r / 10][idx])) : null; });
}
function metrics(S) {
  const n = S.length || 1, o = {};
  const games = new Map(); for (const x of S) if (!games.has(x.key)) games.set(x.key, x);
  o.sides = S.length;
  o.elimRate = share(S.filter(x => x.elim).length, S.length);
  o.roundsMed = med(S.map(x => x.rounds));
  const R = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500];
  o.R = R;
  o.units = curve(S, R, 0); o.total = curve(S, R, 1); o.longest = curve(S, R, 2);
  const full = S.filter(x => x.rounds === 500);
  o.w500 = { n: full.filter(x => x.win === 1).length, units: curve(full, R, 0, x => x.win === 1), longest: curve(full, R, 2, x => x.win === 1), total: curve(full, R, 1, x => x.win === 1) };
  o.l500 = { n: full.filter(x => x.win === 0).length, units: curve(full, R, 0, x => x.win === 0), longest: curve(full, R, 2, x => x.win === 0) };
  const el = S.filter(x => x.elim);
  o.elimW = { n: el.filter(x => x.win === 1).length, units: curve(el, R, 0, x => x.win === 1), longest: curve(el, R, 2, x => x.win === 1) };
  o.elimL = { n: el.filter(x => x.win === 0).length, units: curve(el, R, 0, x => x.win === 0) };
  // splits
  let sp = 0, child = {}, cats = {}, bigN = 0, bigStub = 0; for (const b of CHILD_BINS) child[b] = 0; for (const c of SPLIT_CATS) cats[c] = 0;
  for (const x of S) { sp += x.splits.n; for (const b of CHILD_BINS) child[b] += x.splits.child[b]; for (const c of SPLIT_CATS) cats[c] += x.splits.cats[c]; bigN += x.splits.bigN; bigStub += x.splits.bigStub; }
  o.splitsPerSide = sp / n; o.splitsMed = med(S.map(x => x.splits.n));
  o.child = {}; for (const b of CHILD_BINS) o.child[b] = share(child[b], sp);
  o.cats = {}; for (const c of SPLIT_CATS) o.cats[c] = share(cats[c], sp);
  o.bigStub = share(bigStub, bigN); o.bigN = bigN / n;
  o.after450 = share(full.filter(x => x.splits.after450 > 0).length, full.length);
  o.lastSplit500 = med(full.filter(x => x.splits.last >= 0).map(x => x.splits.last));
  // deaths
  o.deathsPerSide = sum(S.map(x => x.deaths)) / n;
  o.modes = {}; for (const m of MODES) o.modes[m] = sum(S.map(x => x.modes[m])) / n;
  o.trappedShare = share(sum(S.map(x => x.modes['self-trapped'] + x.modes['WS-trapped'])), sum(S.map(x => x.deaths)));
  // exit sacrifices
  const fr = []; for (const x of S) fr.push(...x.free);
  o.free = { perSide: fr.length / n, selfPerSide: fr.filter(f => f[6] === 0).length / n, wsPerSide: fr.filter(f => f[6] === 1).length / n,
    p10: quant(fr.map(f => f[0]), 0.1), med: med(fr.map(f => f[0])), p90: quant(fr.map(f => f[0]), 0.9), len: med(fr.map(f => f[1])),
    own20: share(sum(fr.map(f => f[4])), sum(fr.map(f => f[3]))), king20: share(sum(fr.map(f => f[5])), sum(fr.map(f => f[3]))),
    distKing: med(fr.filter(f => f[2] >= 0).map(f => f[2])), within2: share(fr.filter(f => f[2] >= 0 && f[2] <= 2).length, fr.filter(f => f[2] >= 0).length),
    perSide500: full.length ? sum(full.map(x => x.free.length)) / full.length : null };
  o.kingDiet400 = share(sum(S.map(x => x.fromFree400)), sum(S.map(x => x.longest400)));
  // rams
  const rams = []; for (const x of S) rams.push(...x.rams);
  o.rams = { perSide: rams.length / n, sprint: share(rams.filter(r => r[3] > 0).length, rams.length), ourLen: med(rams.map(r => r[1])), theirLen: med(rams.map(r => r[2])),
    theirLe3: share(rams.filter(r => r[2] <= 3).length, rams.length), victimGe6: rams.filter(r => r[2] >= 6).length / n };
  o.rammedPerSide = sum(S.map(x => x.rammed)) / n; o.oKillsPerSide = sum(S.map(x => x.oKills)) / n;
  const ram = [0, 1, 2].map(c => { let a = 0, b = 0, r = 0; for (const x of S) { a += x.ram[c][0]; b += x.ram[c][1]; r += x.ram[c][2]; } return { n: a, rate: share(b, a), rnd: share(r, a) }; });
  o.ramAdj = ram;
  const ap = [0, 1, 2].map(c => { let a = 0, b = 0, r = 0; for (const x of S) { a += x.appr[c][0]; b += x.appr[c][1]; r += x.appr[c][2]; } return { n: a, toward: share(b, a), rnd: share(r, a) }; });
  o.approach = ap;
  o.eaten100 = med(S.map(x => x.eaten100)); o.eaten100W = med(S.filter(x => x.win === 1).map(x => x.eaten100)); o.eaten100L = med(S.filter(x => x.win === 0).map(x => x.eaten100));
  o.sprintsPerSide = sum(S.map(x => x.sprints)) / n;
  const hmed = key => { const h = new Array(64).fill(0); for (const x of S) if (x[key]) for (let i = 0; i < 64; i++) h[i] += x[key][i]; const t = sum(h); if (!t) return null; let c = 0; for (let i = 0; i < 64; i++) { c += h[i]; if (c * 2 >= t) return i; } return null; };
  o.nearAlly = hmed('nearA'); o.nearEnemy = hmed('nearE');
  o.sonar = med(S.map(x => x.sonar));
  o.final500W = med(full.filter(x => x.win === 1).map(x => x.final[1])); o.final500L = med(full.filter(x => x.win === 0).map(x => x.final[1]));
  o.finalUnits500 = med(full.map(x => x.final[0]));
  // by map
  o.maps = {};
  for (const m of MAP_KEYS) {
    const G = [...games.values()].filter(x => x.map === m);
    if (!G.length) continue;
    o.maps[m] = { games: G.length, elim: share(G.filter(x => x.elim).length, G.length), rounds: med(G.map(x => x.rounds)) };
  }
  return o;
}
function printCompare(P, T, title) {
  const row = (name, a, b, fmt = f1) => console.log(`| ${name} | ${fmt(a)} | ${fmt(b)} | ${typeof a === 'number' && typeof b === 'number' && b ? (a / b).toFixed(2) : '-'} |`);
  console.log(`\n### ${title}\nproxy sides ${P.sides}, target sides ${T.sides}\n`);
  console.log('| metric | proxy | target | proxy/target |\n|---|---:|---:|---:|');
  row('elimination share (sides)', P.elimRate, T.elimRate, pc); row('game length median', P.roundsMed, T.roundsMed);
  for (let i = 0; i < P.R.length; i++) row(`units r${P.R[i]}`, P.units[i], T.units[i]);
  for (let i = 0; i < P.R.length; i++) row(`total r${P.R[i]}`, P.total[i], T.total[i]);
  for (let i = 0; i < P.R.length; i++) row(`longest r${P.R[i]}`, P.longest[i], T.longest[i]);
  for (const r of [300, 400, 500]) { const i = P.R.indexOf(r); row(`500-game winner longest r${r}`, P.w500.longest[i], T.w500.longest[i]); }
  for (const r of [100, 300, 400, 500]) { const i = P.R.indexOf(r); row(`500-game winner units r${r}`, P.w500.units[i], T.w500.units[i]); }
  row('500-game final longest (winner)', P.final500W, T.final500W); row('500-game final longest (loser)', P.final500L, T.final500L); row('500-game final units', P.finalUnits500, T.finalUnits500);
  row('splits per side', P.splitsPerSide, T.splitsPerSide);
  for (const b of CHILD_BINS) row(`child length ${b}`, P.child[b], T.child[b], pc);
  for (const c of SPLIT_CATS) row(`split ${c}`, P.cats[c], T.cats[c], pc);
  row('stub share of parent>=8 splits', P.bigStub, T.bigStub, pc); row('500-game sides splitting after r450', P.after450, T.after450, pc); row('last split (500 games)', P.lastSplit500, T.lastSplit500);
  row('deaths per side', P.deathsPerSide, T.deathsPerSide);
  for (const m of MODES) row(`deaths ${m}`, P.modes[m], T.modes[m]);
  row('trapped share of deaths', P.trappedShare, T.trappedShare, pc);
  row('exit sacrifices per side', P.free.perSide, T.free.perSide); row('  self-kill (no action/SPLIT 1)', P.free.selfPerSide, T.free.selfPerSide); row('  kelp/own body', P.free.wsPerSide, T.free.wsPerSide);
  row('  per side, 500-round games', P.free.perSide500, T.free.perSide500);
  row('  round p10', P.free.p10, T.free.p10); row('  round median', P.free.med, T.free.med); row('  round p90', P.free.p90, T.free.p90); row('  length median', P.free.len, T.free.len);
  row('  pearls eaten by own team in 20 rounds', P.free.own20, T.free.own20, pc); row('  ... by the then-longest', P.free.king20, T.free.king20, pc);
  row('  distance to the longest (Chebyshev) median', P.free.distKing, T.free.distKing); row('  within 2 of the longest', P.free.within2, T.free.within2, pc);
  row("longest's diet r400+ from exit sacrifices", P.kingDiet400, T.kingDiet400, pc);
  row('rams made per side', P.rams.perSide, T.rams.perSide); row('  on a sprint step', P.rams.sprint, T.rams.sprint, pc); row('  rammer length median', P.rams.ourLen, T.rams.ourLen); row('  victim length median', P.rams.theirLen, T.rams.theirLen);
  row('rammed per side', P.rammedPerSide, T.rammedPerSide); row('body-block kills per side', P.oKillsPerSide, T.oKillsPerSide);
  const cls = ['<=4', '5-9', '>=10'];
  for (let c = 0; c < 3; c++) { row(`ram rate, enemy head adjacent, len ${cls[c]}`, P.ramAdj[c].rate, T.ramAdj[c].rate, pc); row(`  random baseline`, P.ramAdj[c].rnd, T.ramAdj[c].rnd, pc); }
  for (let c = 0; c < 3; c++) { row(`toward visible enemy head, len ${cls[c]}`, P.approach[c].toward, T.approach[c].toward, pc); row(`  random baseline`, P.approach[c].rnd, T.approach[c].rnd, pc); }
  row('pearls eaten r0-99 (median side)', P.eaten100, T.eaten100); row('  winners', P.eaten100W, T.eaten100W); row('  losers', P.eaten100L, T.eaten100L);
  row('small pieces: nearest ally head (median)', P.nearAlly, T.nearAlly); row('small pieces: nearest enemy head (median)', P.nearEnemy, T.nearEnemy);
  row('sprints per side', P.sprintsPerSide, T.sprintsPerSide); row('sonar pings per dragon-turn (median side)', P.sonar, T.sonar);
  console.log('\n| map | proxy games | proxy elim | proxy rounds | top games | top elim | top rounds |\n|---|---:|---:|---:|---:|---:|---:|');
  for (const m of MAP_KEYS) { const a = P.maps[m] || {}, b = T.maps[m] || {}; console.log(`| ${m} | ${a.games || 0} | ${pc(a.elim)} | ${f1(a.rounds)} | ${b.games || 0} | ${pc(b.elim)} | ${f1(b.rounds)} |`); }
}
function cmdReport(opt) {
  const bot = opt.bot; const P = loadSides(opt.label).filter(x => !bot || x.name === bot);
  const which = opt.target || 'all';
  const T = targetSides(which);
  const mp = metrics(P), mt = metrics(T);
  printCompare(mp, mt, `${bot || 'all sides'} in ${opt.label} vs top target '${which}'`);
  const opps = [...new Set(P.map(x => x.opp))].sort();
  console.log('\n| opponent | games | wins | draws |\n|---|---:|---:|---:|');
  for (const o of opps) { const A = P.filter(x => x.opp === o); console.log(`| ${o} | ${A.length} | ${A.filter(x => x.win === 1).length} | ${A.filter(x => x.win === 0.5).length} |`); }
  if (opt.json) fs.writeFileSync(path.resolve(opt.json), JSON.stringify({ proxy: mp, target: mt }, null, 1));
}

// vsbot: our bot against the opponents, local labels and online references
function vsStats(S) {
  const o = { games: S.length, win: mean(S.map(x => x.win === 1 ? 1 : 0)), G: mean(S.map(x => x.final[0] > 0 ? x.final[1] : 0)), elimLoss: share(S.filter(x => x.elim && x.win === 0).length, S.length) };
  const n = S.length || 1;
  const big = []; for (const x of S) big.push(...x.big);
  o.bigDeathsPerGame = big.length / n;
  const by = {}; for (const b of big) { const k = b[2]; by[k] = (by[k] || 0) + 1; }
  o.bigBy = {}; for (const k of Object.keys(by)) o.bigBy[k] = by[k] / n;
  const hr = big.filter(b => b[2] === 'H-rammed');
  o.rammedBig = { perGame: hr.length / n, byLe3: share(hr.filter(b => b[3] <= 3).length, hr.length), bySplitBorn: share(hr.filter(b => b[4] === 1).length, hr.length), sprint: share(hr.filter(b => b[5] > 0).length, hr.length), lenMed: med(hr.map(b => b[1])) };
  o.bigLenLostRammed = sum(hr.map(b => b[1])) / n;
  const R = [0, 50, 100, 200, 300, 400, 500];
  o.R = R; o.units = curve(S, R, 0); o.longest = curve(S, R, 2);
  return o;
}
function cmdVsbot(opt) {
  if (opt.brief) return vsBrief(opt);
  const local = opt.label ? loadSides(opt.label) : [], online = opt.online ? loadSides(opt.online) : [];
  const ours = local.filter(x => x.name === 'bot'), theirs = local.filter(x => x.opp === 'bot');
  const onOurs = online.filter(x => x.name === 'bot'), onTheirs = online.filter(x => x.opp === 'bot');
  const opps = [...new Set(ours.map(x => x.opp))].sort();
  const res = { local: {}, online: {} };
  console.log('\n### our bot by opponent\n\n| opponent | games | win | G | our elim | our L>=6 deaths/game | rammed (L>=6)/game | rammer <=3 | rammer split-born | sprint | length lost to rams/game |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
  const line = (name, S) => { const v = vsStats(S); console.log(`| ${name} | ${v.games} | ${pc(v.win)} | ${f1(v.G)} | ${pc(v.elimLoss)} | ${f1(v.bigDeathsPerGame)} | ${f1(v.rammedBig.perGame)} | ${pc(v.rammedBig.byLe3)} | ${pc(v.rammedBig.bySplitBorn)} | ${pc(v.rammedBig.sprint)} | ${f1(v.bigLenLostRammed)} |`); return v; };
  for (const o of opps) res.local[o] = line(o, ours.filter(x => x.opp === o));
  if (onOurs.length) {
    res.online.all = line('online (' + opt.online + ')', onOurs);
    if (opt['by-team']) for (const t of [...new Set(onOurs.map(x => x.opp))].sort()) res.online[t] = line('  online vs ' + t, onOurs.filter(x => x.opp === t));
  }
  console.log('\n### our bot by map (win share / mean G)\n');
  const hdr = ['map', ...opps, ...(onOurs.length ? ['online'] : [])];
  console.log('| ' + hdr.join(' | ') + ' |\n|' + hdr.map(() => '---').join('|') + '|');
  for (const m of MAP_KEYS) {
    const cells = [m];
    for (const o of opps) { const S = ours.filter(x => x.opp === o && x.map === m); cells.push(S.length ? `${S.filter(x => x.win === 1).length}/${S.length} G${f1(mean(S.map(x => x.final[0] > 0 ? x.final[1] : 0)))}` : '-'); }
    if (onOurs.length) { const S = onOurs.filter(x => x.map === m); cells.push(S.length ? `${S.filter(x => x.win === 1).length}/${S.length} G${f1(mean(S.map(x => x.final[0] > 0 ? x.final[1] : 0)))}` : '-'); }
    console.log('| ' + cells.join(' | ') + ' |');
  }
  console.log('\n### how our L>=6 dragons die (per game)\n');
  const modes = [...new Set([...ours, ...onOurs].flatMap(x => x.big.map(b => b[2])))].sort();
  console.log('| opponent | ' + modes.join(' | ') + ' |\n|---|' + modes.map(() => '---:').join('|') + '|');
  for (const o of opps) { const v = res.local[o]; console.log(`| ${o} | ` + modes.map(k => f1(v.bigBy[k] || 0)).join(' | ') + ' |'); }
  if (onOurs.length) { const v = res.online.all; console.log(`| online | ` + modes.map(k => f1(v.bigBy[k] || 0)).join(' | ') + ' |'); }
  console.log('\n### curves (median over running games): our units / our longest / their units / their longest\n');
  const R = [0, 50, 100, 200, 300, 400, 500];
  console.log('| opponent | ' + R.map(r => 'r' + r).join(' | ') + ' |\n|---|' + R.map(() => '---').join('|') + '|');
  const cur = (name, A, B) => { const a0 = curve(A, R, 0), a2 = curve(A, R, 2), b0 = curve(B, R, 0), b2 = curve(B, R, 2); console.log(`| ${name} | ` + R.map((r, i) => `${f1(a0[i])}/${f1(a2[i])} v ${f1(b0[i])}/${f1(b2[i])}`).join(' | ') + ' |'); };
  for (const o of opps) cur(o, ours.filter(x => x.opp === o), theirs.filter(x => x.name === o));
  if (onOurs.length) cur('online', onOurs, onTheirs);
  if (opt.json) fs.writeFileSync(path.resolve(opt.json), JSON.stringify(res, null, 1));
}

// mass: per 50-round window, per side whose game is still running: pearls eaten, length lost in own deaths, deaths, splits
function cmdMass(opt) {
  const S = loadSides(opt.label).filter(x => opt.bot ? x.name === opt.bot : x.name !== 'bot');
  console.log(`### mass balance: ${opt.bot || 'non-bot sides'} in ${opt.label} (${S.length} sides)\n`);
  console.log('| window | running sides | eaten | lost in deaths | deaths | splits | net |\n|---|---:|---:|---:|---:|---:|---:|');
  for (let w = 0; w < 10; w++) {
    const R = S.filter(x => x.rounds > w * 50 && x.eatenW);
    if (!R.length) continue;
    const m = k => sum(R.map(x => x[k][w])) / R.length;
    const sp = sum(R.map(x => x.splits.perW[w])) / R.length;
    console.log(`| ${w * 50}-${w * 50 + 49} | ${R.length} | ${f1(m('eatenW'))} | ${f1(m('lostW'))} | ${f1(m('deathsW'))} | ${f1(sp)} | ${f1(m('eatenW') - m('lostW'))} |`);
  }
}

// summary: one line of key numbers per label (proxy value / target value)
const KEYS_SUMMARY = [
  ['u100', m => m.units[2]], ['u300', m => m.units[6]], ['u400', m => m.units[8]], ['L400', m => m.longest[8]], ['L500', m => m.longest[10]],
  ['wL500', m => m.final500W], ['2+2', m => m.cats['2+2']], ['free', m => m.free.perSide], ['freeR', m => m.free.med], ['diet400', m => m.kingDiet400],
  ['rams', m => m.rams.perSide], ['sprint', m => m.rams.sprint], ['trap', m => m.modes['self-trapped'] + m.modes['WS-trapped']], ['eat100', m => m.eaten100],
];
function elimMaps(m) { const v = ELIM_MAPS.map(k => (m.maps[k] || {}).elim).filter(x => x !== null && x !== undefined); return v.length ? mean(v) : null; }
function cmdSummary(opt) {
  const rows = String(opt.runs).split(',').map(x => x.split(':')); // label:bot:target
  const head = ['run', 'bot', 'target', ...KEYS_SUMMARY.map(k => k[0]), 'elim(short maps)'];
  console.log('| ' + head.join(' | ') + ' |\n|' + head.map(() => '---').join('|') + '|');
  for (const [label, bot, target] of rows) {
    const P = metrics(loadSides(label).filter(x => x.name === bot)), T = metrics(targetSides(target || 'all'));
    const cells = KEYS_SUMMARY.map(([k, f]) => { const a = f(P), b = f(T); const fm = ['2+2', 'diet400', 'sprint'].includes(k) ? pc : f1; return `${fm(a)} (${ratio(a, b)})`; });
    console.log(`| ${label} | ${bot} | ${target || 'all'} | ${cells.join(' | ')} | ${pc(elimMaps(P))} / ${pc(elimMaps(T))} |`);
  }
}

// one line per (label, opponent): our win share, G, eliminated share, rams on our L>=6 dragons, the opponent's units at r200
// and longest at r400/r500 (medians over running games)
function vsBrief(opt) {
  const labels = [...String(opt.label || '').split(',').filter(Boolean), ...String(opt.online || '').split(',').filter(Boolean)];
  console.log('| run | opponent | games | our win | G | we eliminated | rammed L>=6/game | their units r200 | their longest r400 | their longest r500 |\n|---|---|---:|---:|---:|---:|---:|---:|---:|---:|');
  for (const L of labels) {
    const S = loadSides(L), ours = S.filter(x => x.name === 'bot');
    const online = ours.length && ours[0].src === 'online';
    for (const o of online ? ['(all)'] : [...new Set(ours.map(x => x.opp))].sort()) {
      const A = online ? ours : ours.filter(x => x.opp === o), B = online ? S.filter(x => x.opp === 'bot') : S.filter(x => x.name === o && x.opp === 'bot');
      const v = vsStats(A), u = curve(B, [200, 400, 500], 0), l = curve(B, [200, 400, 500], 2);
      console.log(`| ${L} | ${o} | ${v.games} | ${pc(v.win)} | ${f1(v.G)} | ${pc(v.elimLoss)} | ${f1(v.rammedBig.perGame)} | ${f1(u[0])} | ${f1(l[1])} | ${f1(l[2])} |`);
    }
  }
}

module.exports = { sideRecords, readJsonl, topSides, mapKey, modeCat, cause, metrics };

async function main() {
  const argv = process.argv.slice(2), cmd = argv[0];
  const opt = {}; for (let i = 1; i < argv.length; i++) if (argv[i].startsWith('--')) { const k = argv[i].slice(2); opt[k] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true; }
  if (cmd === 'targets') return cmdTargets(opt);
  if (cmd === 'run') return cmdRun(opt);
  if (cmd === 'measure') return cmdMeasure(opt);
  if (cmd === 'online') return cmdOnline(opt);
  if (cmd === 'report') return cmdReport(opt);
  if (cmd === 'vsbot') return cmdVsbot(opt);
  if (cmd === 'sync') return cmdSync();
  if (cmd === 'summary') return cmdSummary(opt);
  if (cmd === 'mass') return cmdMass(opt);
  console.error('unknown command; see the header of tools/proxy_check.js'); process.exit(2);
}
if (!process.argv.includes('--pc-worker') && require.main === module) main().catch(e => { console.error(e); process.exit(1); });
