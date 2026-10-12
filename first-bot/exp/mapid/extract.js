#!/usr/bin/env node
'use strict';
// extract.js — per team and game features for the layout study (research/experiments/cand-mapid.md, part B). No games,
// no network. Stage 1 of the three-stage method (full computation): every top-vs-top game of the chosen maps in data/top
// and every game of our online sets against the elite (data/online/<set>, not r1-autoscrim, r1-online, g1, g2), with the
// true pearl layout of each game (exp/mapid/layout.js, from the replay's natural spawns).
// The reconstruction is the mass ledger's (tools/mass_ledger.js perGame, checked against the replay: chk.* = 0); hooks add
// the head's territory per dragon-turn, the splits of the first 100 rounds, natural pearls eaten on layout "fountains"
// (gap mean <= 12 in that layout's map file), and head-ons in the first 150 rounds.
// usage (repository root):
//   node exp/mapid/extract.js [--maps Schooltime,Devil] [--jobs 3] [--src top,online]   -> exp/mapid/cache/feat.jsonl (append; skips done)
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const { classify, FAM } = require('./layout.js');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const OUTDIR = path.join(__dirname, 'cache'), OUT = path.join(OUTDIR, 'feat.jsonl');
const NOT_ELITE = new Set(['r1-autoscrim', 'r1-online', 'g1', 'g2', 'snapshots', 'top-sample']);
const KEEP = ['eat_nat', 'nat_own', 'nat_enemy', 'nat_neutral', 'split_n', 'split_child', 'split_stub', 'turns',
  'dn_sac', 'dn_trap', 'dn_rammed', 'dn_ram', 'dn_enemyBody', 'dn_allyHead', 'dn_fault', 'dn_sprintDeath',
  'dl_sac', 'dl_trap', 'dl_rammed', 'dl_ram', 'dl_enemyBody', 'bk_n', 'bk_len', 'spr_n', 'spr_ram', 'spr_eat', 'spr_esc', 'ram_elen', 'rammed_elen'];
const ORIGS = ['oSac', 'oTrap', 'oRammed', 'oRam', 'oOther', 'eSac', 'eTrap', 'eRammed', 'eRam', 'eOther'];

function fountains(mapName, layout, W, H) {   // tiles whose gap mean <= 12 in that layout's file
  const f = FAM[mapName] ? path.join(ROOT, 'maps', layout === 'b' ? 'variants' : 'online-20260927', FAM[mapName][layout === 'b' ? 1 : 0] + '.map') : null;
  const out = new Uint8Array(W * H); if (!f || !fs.existsSync(f)) return out;
  for (const l of fs.readFileSync(f, 'utf8').split('\n')) if (l.startsWith('TILE ')) { const [x, y, mn, mx] = l.trim().split(/\s+/).slice(1).map(Number); if (mx > 0 && (mn + mx) / 2 <= 12) out[y * W + x] = 1; }
  return out;
}

function work(R, t, perGame) {
  const lay = classify(R, t.map);
  const M = R.match.map, W = M.width, H = M.height;
  const layout = lay.layout === 'a' || lay.layout === 'b' ? lay.layout : 'a';
  const fount = fountains(t.map, layout, W, H);
  const NB = 50, bin = r => Math.max(0, Math.min(NB - 1, Math.floor(r / 10)));
  const mk = () => ({ hOwn: new Array(NB).fill(0), hEnemy: new Array(NB).fill(0), hNeutral: new Array(NB).fill(0), eatF: new Array(NB).fill(0),
    splits100: [], firstSplit: null, heads150: 0, eNear: new Array(NB).fill(0) });
  const X = { A: mk(), B: mk() };
  const info = { map: t.map, variant: t.map === 'Prisoners Dilemma' && M.initialDragons.length === 10 ? 'PD10' : undefined };
  const hooks = {
    turn(d, r, c) {
      const x = X[d.team], h = d.body[0], k = h.y * W + h.x, own = d.team === 'A' ? 1 : 2, tr = c.terr[k];
      if (tr === 0) x.hNeutral[bin(r)]++; else if (tr === own) x.hOwn[bin(r)]++; else x.hEnemy[bin(r)]++;
      if (d.enemyNear) x.eNear[bin(r)]++;
    },
    split(p, ch, e, r) {
      const x = X[p.team];
      if (x.firstSplit === null) x.firstSplit = r;
      if (r < 100) x.splits100.push([r, ch.body.length, p.body.length + ch.body.length]);
    },
    eat(d, k, o, r) { if (o < 0 && fount[k]) X[d.team].eatF[bin(r)]++; },
    death(d, rec, idx, other, r) { if (r < 150 && (rec.cause === 2 || rec.cause === 3)) X[d.team].heads150++; },
  };
  const L = perGame(R, info, hooks);
  const team = tm => {
    const T = L[tm], fl = {};
    for (const k of KEEP) { const i = require(path.join(ROOT, 'tools', 'mass_ledger.js')).FI[k]; fl[k] = T.fl[i]; }
    const FI = require(path.join(ROOT, 'tools', 'mass_ledger.js')).FI;
    fl.eat_own = new Array(NB).fill(0); fl.eat_enemy = new Array(NB).fill(0);
    for (const o of ORIGS) { const a = T.fl[FI['eat_' + o]], dst = o[0] === 'o' ? fl.eat_own : fl.eat_enemy; for (let b = 0; b < NB; b++) dst[b] += a[b]; }
    return { st: { units: T.st.units, total: T.st.total, king: T.st.king, small: T.st.small }, fl, x: X[tm], splits: T.splits, sonar: T.sonar };
  };
  return { ...t, file: undefined, layout: lay.layout, evA: lay.evA, evB: lay.evB, firstEv: lay.firstEv, nInit: lay.nInit,
    rounds: L.rounds, endReason: L.endReason, winner: L.winner, chk: L.chk, natSpawned: L.natSpawned, terrTiles: L.terrTiles, A: team('A'), B: team('B') };
}

function tasks(maps, src) {
  const out = [];
  if (src.includes('top')) {
    for (const l of fs.readFileSync(path.join(ROOT, 'data', 'top', 'index.jsonl'), 'utf8').split('\n')) {
      if (!l.trim()) continue; const g = JSON.parse(l); if (!maps.includes(g.map)) continue;
      const f = path.join(ROOT, 'data', 'top', String(g.battleId), g.gameId + '.replay.gz'); if (!fs.existsSync(f)) continue;
      out.push({ key: 'top:' + g.gameId, src: 'top', set: 'top', gameId: g.gameId, map: g.map, file: f, at: g.at, teamA: g.teamA, teamB: g.teamB, eloA: g.eloA, eloB: g.eloB, rankA: g.rankA, rankB: g.rankB, ranked: g.ranked });
    }
  }
  if (src.includes('online')) {
    const OD = path.join(ROOT, 'data', 'online');
    for (const s of fs.readdirSync(OD)) {
      if (NOT_ELITE.has(s) || !fs.existsSync(path.join(OD, s, 'index.json'))) continue;
      const idx = JSON.parse(fs.readFileSync(path.join(OD, s, 'index.json'), 'utf8'));
      for (const g of idx.games || idx) {
        if (!maps.includes(g.mapName) || g.ourWin === null || g.ourWin === undefined) continue;
        const f = path.join(OD, s, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
        out.push({ key: s + ':' + g.gameId, src: 'online', set: s, gameId: g.gameId, map: g.mapName, file: f, at: g.completedAt, us: String(g.ourSide).toUpperCase(), opp: g.opponentTeam, sub: g.ourSubmission });
      }
    }
  }
  return out;
}

if (argv[0] === '--worker') {
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const load = makeLoader(viewerSource());
  process.on('message', t => {
    try { process.send({ ok: true, row: work(load(t.file), t, perGame) }); }
    catch (e) { process.send({ ok: false, key: t.key, error: String((e && e.stack) || e).split('\n').slice(0, 3).join(' | ') }); }
  });
} else {
  const maps = opt('maps', 'Schooltime,Devil').split(','), src = opt('src', 'top,online').split(','), jobs = Math.min(4, +opt('jobs', 3));
  fs.mkdirSync(OUTDIR, { recursive: true });
  const done = new Set(fs.existsSync(OUT) ? fs.readFileSync(OUT, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l).key) : []);
  const q = tasks(maps, src).filter(t => !done.has(t.key));
  console.log(`extract: ${q.length} games (${done.size} done) maps ${maps.join(',')}`);
  let n = 0, err = 0; const t0 = Date.now();
  Promise.all(Array.from({ length: Math.min(jobs, q.length) }, () => new Promise(res => {
    const w = cp.fork(__filename, ['--worker'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
    const next = () => { const t = q.shift(); if (!t) { w.kill(); res(); return; } w.send(t); };
    w.on('message', m => {
      if (m.ok) fs.appendFileSync(OUT, JSON.stringify(m.row) + '\n'); else { err++; console.error('error', m.key, m.error); }
      if (++n % 100 === 0) console.log(`  ${n} (${Math.round((Date.now() - t0) / 1000)}s)`);
      next();
    });
    next();
  }))).then(() => console.log(`done ${n}, errors ${err}, ${Math.round((Date.now() - t0) / 1000)}s`));
}
