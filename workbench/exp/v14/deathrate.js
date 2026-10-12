#!/usr/bin/env node
// v1.4 death calibration (lead 2026-10-01): our deaths per 1,000 head-rounds by cause and frontier bin, with the spatial study's definitions
// (exp/spatial/lib.js hooks): head-rounds = our living heads at the first turn of each round, by the bin of the head; a death counts in the bin
// of the dead dragon's head; windows all rounds, r50-374 (the study's "Mid") and r0-99 (the opening and the hold window). Against the study's
// classes (exp/spatial-all/tables.json maps[m].classes[c]: deaths / headRounds, deaths50_374 / headRounds50_374): elite winners, elite losers,
// our last online set before v1 (set:cand-stack11-online) and the top teams in our online games (opponents:online).
// usage: node exp/v14/deathrate.js --sets v14=dir,dir --sets v12=dir,dir [--bins 1,2,3] [--causes trap,rammed,ram] [--jobs 3]
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const NAME = { default: 'Default/a', devil: 'Devil/a', devil_b: 'Devil/b', schooltime: 'Schooltime/a', schooltime_b: 'Schooltime/b', slithery_fight: 'Slithery Fight/a',
  slithery_fight_b: 'Slithery Fight/b', trophy: 'Trophy/a' };
const W3 = ['all', 'mid', 'early'];   // all rounds, r50-374, r0-99

function analyseGame(file, row) {
  const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const { geometry } = require(path.join(ROOT, 'exp', 'spatial', 'lib.js'));
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const R = makeLoader(viewerSource())(file), M = R.match.map, W = M.width, us = row.side;
  const g = geometry(M, 'x', '?'), bin = g.bin[us];
  const z = () => [0, 0, 0, 0, 0, 0];
  const hr = { all: z(), mid: z(), early: z() }, dn = {};
  for (const w of W3) dn[w] = ML.CAUSE.map(() => z());
  let last = -1;
  ML.perGame(R, { map: NAME[row.map] }, {
    turn(d, round, ctx) {
      if (round === last) return; last = round;
      for (const a of ctx.drag.values()) {
        if (a.team !== us) continue;
        const b = bin[a.body[0].y * W + a.body[0].x]; const bb = b === undefined ? 5 : b;
        hr.all[bb]++; if (round >= 50 && round < 375) hr.mid[bb]++; if (round < 100) hr.early[bb]++;
      }
    },
    death(d, rec, idx, other, round) {
      if (d.team !== us) return;
      const b = bin[d.body[0].y * W + d.body[0].x]; const bb = b === undefined ? 5 : b;
      dn.all[rec.cause][bb]++; if (round >= 50 && round < 375) dn.mid[rec.cause][bb]++; if (round < 100) dn.early[rec.cause][bb]++;
    },
  });
  return { key: row.key, map: NAME[row.map], hr, dn };
}

if (process.argv[2] === '--worker') {
  process.on('message', t => { let r; try { r = analyseGame(t.file, t.row); } catch (e) { r = { key: t.row.key, error: String(e.stack || e).slice(0, 300) }; } process.send(r); });
  return;
}

const args = process.argv.slice(2), get = k => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const sets = []; for (let i = 0; i < args.length; i++) if (args[i] === '--sets') { const [nm, ds] = args[i + 1].split('='); sets.push({ name: nm, dirs: ds.split(',') }); }
const BINS = (get('--bins') || '1,2,3').split(',').map(Number), CAUSES = (get('--causes') || 'trap,rammed,ram').split(','), jobs = +(get('--jobs') || 3);
const cacheDir = path.join(ROOT, 'exp', 'v14', 'cache'); fs.mkdirSync(cacheDir, { recursive: true });
const clean = r => r.G !== undefined && !r.botProblem && (r.exit === 0 || r.exit === undefined);

(async () => {
  const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const res = {};
  for (const S of sets) {
    const out = res[S.name] = new Map();
    const tasks = [];
    for (const dir of S.dirs) {
      const cache = path.join(cacheDir, dir.replace(/[\/]/g, '_') + '.dr.jsonl');
      const have = new Map(fs.existsSync(cache) ? fs.readFileSync(cache, 'utf8').trim().split('\n').filter(Boolean).map(l => { const o = JSON.parse(l); return [o.key, o]; }) : []);
      const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => clean(r) && NAME[r.map]);
      for (const r of rows) {
        if (out.has(r.key) || tasks.some(t => t.row.key === r.key)) continue;
        if (have.has(r.key)) { out.set(r.key, have.get(r.key)); continue; }
        const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
        tasks.push({ file, row: r, cache });
      }
    }
    await new Promise(done => {
      if (!tasks.length) return done();
      let next = 0, live = 0;
      const spawn = () => {
        const w = cp.fork(__filename, ['--worker'], { stdio: ['ignore', 'ignore', 'inherit', 'ipc'] }); live++;
        const feed = () => {
          if (next >= tasks.length) { w.kill(); live--; if (!live) done(); return; }
          const t = tasks[next++];
          w.once('message', r => { if (!r.error) { out.set(r.key, r); fs.appendFileSync(t.cache, JSON.stringify(r) + '\n'); } else console.error(t.row.key, r.error); feed(); });
          w.send(t);
        };
        feed();
      };
      for (let j = 0; j < Math.min(jobs, tasks.length); j++) spawn();
    });
  }
  const names = sets.map(s => s.name);
  const common = [...res[names[0]].keys()].filter(k => names.every(n => res[n].has(k)));
  const T = JSON.parse(fs.readFileSync(path.join(ROOT, 'exp', 'spatial-all', 'tables.json'), 'utf8'));
  const ci = c => ML.CAUSE.indexOf(c);
  const f2 = x => x === null || x === undefined || !isFinite(x) ? '–' : x.toFixed(2);
  const maps = [...new Set(common.map(k => res[names[0]].get(k).map))].sort();
  const L = [];
  L.push(`# Deaths per 1,000 head-rounds by frontier bin (bins ${BINS.join(', ')}; causes ${CAUSES.join(', ')}); local sets on ${common.length} common keys`, '');
  L.push('Cells: trap / rammed / ram per 1,000 head-rounds; HR = head-rounds in that bin (share of all head-rounds in the window).', '');
  for (const m of maps) {
    L.push(`## ${m}`, '');
    L.push(`| class | window | ${BINS.map(b => `bin ${b}: ${CAUSES.join(' / ')} (HR, share)`).join(' | ')} |`);
    L.push(`| --- | --- | ${BINS.map(() => '---').join(' | ')} |`);
    const study = T.maps[m] ? T.maps[m].classes : {};
    for (const [cls, label] of [['elite-winners', 'elite winners'], ['elite-losers', 'elite losers'], ['set:cand-stack11-online', 'ours online W12 (stack11)'], ['opponents:online', 'top teams vs us online']]) {
      const c = study[cls]; if (!c) continue;
      const hrAll = [0, 1, 2, 3, 4, 5].map(j => c.headRounds.reduce((a, x) => a + x[j], 0)), totAll = hrAll.reduce((a, b) => a + b, 0);
      const hrMid = c.headRounds50_374, totMid = hrMid.reduce((a, b) => a + b, 0);
      L.push(`| ${label} (N ${c.N}) | all | ${BINS.map(b => `${CAUSES.map(k => f2(1000 * c.deaths[ci(k)][b] / hrAll[b])).join(' / ')} (${hrAll[b]}, ${(100 * hrAll[b] / totAll).toFixed(0)}%)`).join(' | ')} |`);
      L.push(`| ${label} | r50-374 | ${BINS.map(b => `${CAUSES.map(k => f2(1000 * c.deaths50_374[ci(k)][b] / hrMid[b])).join(' / ')} (${hrMid[b]}, ${(100 * hrMid[b] / totMid).toFixed(0)}%)`).join(' | ')} |`);
    }
    for (const n of names) {
      const G = common.filter(k => res[n].get(k).map === m).map(k => res[n].get(k));
      for (const w of W3) {
        const hr = [0, 1, 2, 3, 4, 5].map(j => G.reduce((a, x) => a + x.hr[w][j], 0)), tot = hr.reduce((a, b) => a + b, 0);
        const dn = (k, b) => G.reduce((a, x) => a + x.dn[w][ci(k)][b], 0);
        L.push(`| local ${n} (${G.length} games) | ${w === 'all' ? 'all' : w === 'mid' ? 'r50-374' : 'r0-99'} | ${BINS.map(b => `${CAUSES.map(k => f2(1000 * dn(k, b) / hr[b])).join(' / ')} (${hr[b]}, ${tot ? (100 * hr[b] / tot).toFixed(0) : 0}%)`).join(' | ')} |`);
      }
    }
    L.push('');
  }
  process.stdout.write(L.join('\n') + '\n');
})();
