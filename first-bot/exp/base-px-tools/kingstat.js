#!/usr/bin/env node
// King-centric metrics per side of eval.js labels (exp/<label>/rows.jsonl + games/<key>/game.replay).
// usage: node kingstat.js --labels a,b [--jobs 2] [--name bot]   -> writes exp/<label>/king.jsonl (cache) and prints a table
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = require('path').resolve(__dirname, '..', '..');
const TI = { A: 0, B: 1 };

function analyse(file, row) {
  const { load } = require(path.join(ROOT, 'tools/replay.js'));
  const fsd = require(path.join(ROOT, 'tools/fragment_study.js'));
  const tf = require(path.join(ROOT, 'tools/top_features.js'));
  const R = load(file);
  const f = tf.extract(R, row);
  const g = fsd.study(R);
  const out = {};
  for (const s of ['A', 'B']) {
    const o = s === 'A' ? 'B' : 'A';
    const tl = f[s].timeline.map(t => [t.units, t.total, t.longest]);
    const sp = g.splits.filter(t => t[0] === TI[s]);
    // [ti, round, lenBefore, child, unitsBefore, parentId, childId, parentLongest, parentBorn, parentSplitBorn, seq, freeN, dEnemy]
    const bigStubs = sp.filter(t => t[2] >= 8 && t[2] - t[3] <= 3);
    const kingStubs = bigStubs.filter(t => t[7] >= 1);
    const late = x => x[1] >= 250;
    const mine = g.deaths.filter(d => d.team === s);
    const bigDeaths = mine.filter(d => d.len >= 8);
    const modeOf = d => {
      if (d.reason === 'H') { if (d.mover) return d.hitTeam === s ? 'H-own' : 'ram'; return d.byTeam === s ? 'H-own' : 'rammed'; }
      if (d.reason === 'A') return d.freeN > 0 ? 'self-free' : 'self-trapped';
      if (d.reason === 'W' || d.reason === 'S') return d.step > 0 ? 'ws-sprint' : d.freeN > 0 ? 'ws-free' : 'ws-trapped';
      if (d.reason === 'O') return d.hitTeam === s ? 'O-own' : 'O-enemy';
      return d.reason;
    };
    const bd = {}; for (const d of bigDeaths) { const m = modeOf(d); bd[m] = (bd[m] || 0) + 1; }
    const bdLen = {}; for (const d of bigDeaths) { const m = modeOf(d); bdLen[m] = (bdLen[m] || 0) + d.len; }
    const kingDeaths = bigDeaths.filter(d => d.isLongest);
    // pearls eaten by the team's longest, per 100-round window and source [natural, ownSelfKill, ownOther, enemy]
    const E = g.eat[s];
    const kingEat = E.map(w => w[1]);
    const allEat = E.map(w => [w[0][0] + w[1][0], w[0][1] + w[1][1], w[0][2] + w[1][2], w[0][3] + w[1][3]]);
    // exit sacrifices (self-kill or W/S with a free neighbour on the first step) and their pearls' fates
    let sac = 0, sacDrop = 0, sacOwn20 = 0, sacKing20 = 0, sacKingAny = 0, sacNear2 = 0, sacDist = [];
    for (const d of mine) {
      const m = modeOf(d);
      if (m !== 'self-free' && m !== 'ws-free') continue;
      sac++; sacDrop += d.nDrop;
      if (d.distKing >= 0) { sacDist.push(d.distKing); if (d.distKing <= 2) sacNear2++; }
      for (const fa of d.fates) { if (fa[1] !== 0) continue; if (fa[0] <= 20) { sacOwn20++; if (fa[3] === 1) sacKing20++; } if (fa[2] === 1) sacKingAny++; }
    }
    // the longest's diet by the source death's mode: pearls from own deaths eaten by the then-longest, by eat round window
    const dietBy = { 3: {}, 4: {} };
    let vol = 0, volDrop = 0, volKing20 = 0, volL20 = 0, volOwn20 = 0;
    for (const d of mine) {
      const m = modeOf(d);
      const voluntary = m === 'self-free' || m === 'ws-free' || ((m === 'O-own' || m === 'H-own') && d.freeN > 0);
      if (voluntary && d.r >= 250) { vol++; volDrop += d.nDrop; }
      for (const fa of d.fates) {
        if (fa[1] !== 0) continue;
        const er = d.r + fa[0];
        if (voluntary && d.r >= 250 && fa[0] <= 20) { volOwn20++; if (fa[3] === 1) volKing20++; if (fa[2] === 1) volL20++; }
        if (fa[2] !== 1 || er < 300) continue;
        const w = er >= 400 ? 4 : 3; const k = voluntary ? 'vol' : m;
        dietBy[w][k] = (dietBy[w][k] || 0) + 1;
      }
    }
    // trapped deaths (no free neighbour) of any length, and length lost in them
    let trapN = 0, trapLen = 0; for (const d of mine) { const m = modeOf(d); if (m === 'self-trapped' || m === 'ws-trapped') { trapN++; trapLen += d.len; } }
    out[s] = {
      tl, rounds: g.rounds, win: f.meta.winner === s ? 1 : f.meta.winner === o ? 0 : 0.5, elim: f.meta.endReason === 'teamEliminated' ? 1 : 0,
      final: [f.meta.final[s].dragonCount, f.meta.final[s].longestDragon, f.meta.final[s].totalLength],
      bigStubs: bigStubs.length, bigStubsLate: bigStubs.filter(late).length, kingStubs: kingStubs.length, kingStubsLate: kingStubs.filter(late).length,
      kingStubLen: kingStubs.filter(late).map(t => t[2]),
      bigDeaths: bd, bigDeathLen: bdLen, kingDeathsLate: kingDeaths.filter(d => d.r >= 250).map(d => [d.r, d.len, modeOf(d)]),
      kingEat, allEat, sac, sacDrop, sacOwn20, sacKing20, sacKingAny, sacNear2, sacDistMed: sacDist.length ? sacDist.sort((a, b) => a - b)[Math.floor(sacDist.length / 2)] : null,
      trapN, trapLen, deaths: mine.length, splits: sp.length, dietBy, vol, volDrop, volKing20, volL20, volOwn20,
    };
  }
  return out;
}

if (process.argv.includes('--ks-worker')) {
  process.on('message', t => {
    try { process.send({ key: t.key, label: t.label, res: analyse(t.file, t.row) }); }
    catch (e) { process.send({ key: t.key, label: t.label, error: String(e && e.stack || e).split('\n').slice(0, 3).join(' | ') }); }
  });
  return;
}

const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const labels = String(arg('labels', '')).split(',').filter(Boolean);
const jobs = +arg('jobs', '2');
const SCR = require('path').join(__dirname, 'cache');
const cacheFile = L => L.startsWith('base-px') ? path.join(ROOT, 'exp', L, 'king.jsonl') : path.join(SCR, 'king-' + L + '.jsonl');
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(Boolean).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];

async function main() {
  const tasks = [];
  for (const L of labels) {
    const dir = path.join(ROOT, 'exp', L), cache = cacheFile(L);
    const have = new Set(readJsonl(cache).map(r => r.key));
    const seen = new Set();
    for (const r of readJsonl(path.join(dir, 'rows.jsonl'))) {
      if (r.G === undefined || seen.has(r.key)) continue; seen.add(r.key);
      if (have.has(r.key)) continue;
      const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay');
      if (!fs.existsSync(file)) continue;
      tasks.push({ label: L, key: r.key, file, row: { key: r.key, map: r.map }, side: r.side, opp: r.opp, mapName: r.map, seed: r.seed });
    }
  }
  if (tasks.length) {
    await new Promise(resolve => {
      const q = tasks.slice(); let live = 0;
      const n = Math.min(jobs, q.length);
      for (let i = 0; i < n; i++) {
        const c = cp.fork(__filename, ['--ks-worker'], { serialization: 'advanced' }); live++;
        const byKey = new Map(tasks.map(t => [t.label + '|' + t.key, t]));
        const next = () => { const t = q.shift(); if (!t) { c.kill(); if (--live === 0) resolve(); return; } c.send(t); };
        c.on('message', m => {
          if (m.error) console.error('error', m.label, m.key, m.error);
          else {
            const t = byKey.get(m.label + '|' + m.key);
            const us = t.side, th = us === 'A' ? 'B' : 'A';
            fs.appendFileSync(cacheFile(m.label), JSON.stringify({ key: m.key, opp: t.opp, map: t.mapName, side: us, seed: t.seed, us: m.res[us], them: m.res[th] }) + '\n');
          }
          next();
        });
        next();
      }
    });
  }
}
module.exports = { analyse };
main();
