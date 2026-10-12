#!/usr/bin/env node
// exp/gen unknown-map baseline report (exp/gen/PLAN.md §4): per map and pooled, for local eval sets (exp/v14/runq14.js layout):
//   outcome: wins, eliminated, final longest ours / theirs;
//   chain: our units at r100, natural pearls we ate (mass ledger nat_*), all and r0-99;
//   firing: our turns by engine label (the indicator's " E=<F|S|W>"), and whether recognition fired (a " map=<Name>/<layout>" tag naming a map).
//   With two sets: paired final longest (higher / lower / equal, median difference, two-sided sign test) per map and pooled.
// usage: node exp/gen/genreport.js --sets F=dir,dir --sets S=dir,dir [--jobs 3]
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');

function analyseGame(file, row) {
  const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const R = makeLoader(viewerSource())(file), us = row.side, them = us === 'A' ? 'B' : 'A';
  const label = { F: 0, S: 0, W: 0, other: 0 }, maps = {};
  let units100 = null, last = -1;
  const hooks = {
    turn(d, round, ctx) {
      if (round === last) return; last = round;
      if (round === 100) { let c = 0; for (const o of ctx.drag.values()) if (o.team === us) c++; units100 = c; }
    },
    indicator(e, round, ctx) {
      const d = ctx && ctx.drag ? ctx.drag.get(e.id) : null;
      if (!d || d.team !== us) return;
      const t = e.text || '';
      const m = / E=([A-Z])$/.exec(t); if (m) { if (label[m[1]] !== undefined) label[m[1]]++; else label.other++; }
      for (const x of t.matchAll(/(?:^| )map=([^ ]+)/g)) maps[x[1]] = (maps[x[1]] || 0) + 1;
    },
  };
  const G = ML.perGame(R, { map: row.map }, hooks);
  const nat = (X, nb = 50) => ['nat_own', 'nat_enemy', 'nat_neutral'].reduce((a, k) => a + X.fl[ML.FI[k]].slice(0, nb).reduce((p, q) => p + q, 0), 0);
  const res = R.result;
  const recog = Object.keys(maps).filter(k => k !== '?' && k !== 'none');
  return { key: row.key, map: row.map, won: res.winner === us ? 1 : 0, elim: res['team' + us].dragonCount === 0 ? 1 : 0,
    final: [res['team' + us].dragonCount > 0 ? res['team' + us].longestDragon : 0, res['team' + them].longestDragon],
    units100: units100 === null ? 0 : units100, nat: nat(G[us]), nat100: nat(G[us], 10), label, maps, recog };
}

if (process.argv[2] === '--worker') {
  process.on('message', t => { let r; try { r = analyseGame(t.file, t.row); } catch (e) { r = { key: t.row.key, error: String(e.stack || e).slice(0, 300) }; } process.send(r); });
  return;
}

const args = process.argv.slice(2), get = k => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const sets = []; for (let i = 0; i < args.length; i++) if (args[i] === '--sets') { const [nm, ds] = args[i + 1].split('='); sets.push({ name: nm, dirs: ds.split(',') }); }
const jobs = +(get('--jobs') || 3), cacheDir = path.join(ROOT, 'exp', 'gen', 'cache');
fs.mkdirSync(cacheDir, { recursive: true });

(async () => {
  const res = {};
  for (const S of sets) {
    const out = res[S.name] = new Map(), tasks = [];
    for (const dir of S.dirs) {
      const cache = path.join(cacheDir, dir.replace(/[\/]/g, '_') + '.gen.jsonl');
      const have = new Map(fs.existsSync(cache) ? fs.readFileSync(cache, 'utf8').trim().split('\n').filter(Boolean).map(l => { const o = JSON.parse(l); return [o.key, o]; }) : []);
      const lastClean = new Map();
      for (const r of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l)))
        if (r.G !== undefined && (r.exit === 0 || r.exit === undefined) && !r.error && !r.botProblem) lastClean.set(r.key, r);
      for (const r of lastClean.values()) {
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
  const maps = [...new Set(common.map(k => res[names[0]].get(k).map))].sort();
  const f1 = x => (x === null || x === undefined || !isFinite(x)) ? '–' : (+x).toFixed(1);
  const mean = xs => xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : NaN;
  const median = xs => { if (!xs.length) return NaN; const s = [...xs].sort((a, b) => a - b); const m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
  const C2 = (n, k) => { let r = 1; for (let i = 1; i <= k; i++) r = r * (n - k + i) / i; return r; };
  const sign = (h, l) => { const n = h + l; if (!n) return 1; let p = 0; for (let i = 0; i <= Math.min(h, l); i++) p += C2(n, i); return Math.min(1, 2 * p / Math.pow(2, n)); };
  const L = [];
  L.push(`# Unknown-map baseline: ${names.join(' vs ')} (same keys: ${common.length})`, '');
  L.push('| map | set | games | wins | eliminated | final longest ours mean / median | theirs mean | r100 units | intake all / r0-99 | our turns E=F / E=S / E=W | recognition fired (games: tags) |');
  L.push('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |');
  const rowFor = (label, keys) => {
    for (const n of names) {
      const G = keys.map(k => res[n].get(k));
      const lab = G.reduce((a, x) => { for (const k of Object.keys(a)) a[k] += x.label[k] || 0; return a; }, { F: 0, S: 0, W: 0 });
      const tot = lab.F + lab.S + lab.W || 1;
      const rec = G.filter(x => x.recog.length);
      const tags = {}; for (const x of rec) for (const t of x.recog) tags[t] = (tags[t] || 0) + 1;
      L.push(`| ${label} | ${n} | ${G.length} | ${G.reduce((a, x) => a + x.won, 0)} | ${G.reduce((a, x) => a + x.elim, 0)} | ${f1(mean(G.map(x => x.final[0])))} / ${f1(median(G.map(x => x.final[0])))} | ${f1(mean(G.map(x => x.final[1])))} | ${f1(mean(G.map(x => x.units100)))} | ${f1(mean(G.map(x => x.nat)))} / ${f1(mean(G.map(x => x.nat100)))} | ${(100 * lab.F / tot).toFixed(0)}% / ${(100 * lab.S / tot).toFixed(0)}% / ${(100 * lab.W / tot).toFixed(0)}% | ${rec.length}${rec.length ? ': ' + Object.entries(tags).map(([t, c]) => `${t} ${c}`).join(', ') : ''} |`);
    }
  };
  for (const m of maps) rowFor(m, common.filter(k => res[names[0]].get(k).map === m));
  rowFor('**pooled**', common);
  if (names.length === 2) {
    L.push('', `## Paired final longest: ${names[0]} minus ${names[1]} (same key)`, '');
    L.push('| map | pairs | higher / lower / equal | median difference | sign test p | wins | eliminated |');
    L.push('| --- | --- | --- | --- | --- | --- | --- |');
    for (const m of [...maps, 'pooled']) {
      const ks = m === 'pooled' ? common : common.filter(k => res[names[0]].get(k).map === m);
      const d = ks.map(k => res[names[0]].get(k).final[0] - res[names[1]].get(k).final[0]);
      const h = d.filter(x => x > 0).length, l = d.filter(x => x < 0).length;
      const w = n => ks.reduce((a, k) => a + res[n].get(k).won, 0), e = n => ks.reduce((a, k) => a + res[n].get(k).elim, 0);
      L.push(`| ${m} | ${ks.length} | ${h} / ${l} / ${d.length - h - l} | ${f1(median(d))} | ${sign(h, l).toFixed(3)} | ${w(names[0])} vs ${w(names[1])} | ${e(names[0])} vs ${e(names[1])} |`);
    }
  }
  process.stdout.write(L.join('\n') + '\n');
})();
