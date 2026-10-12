#!/usr/bin/env node
// v1.4 local report (versions/v1.4/VERSION.md §3 b-d): opening metrics against the elite targets of the Codex opening study, and outcome / chain
// v1.4 against v1.2 on the same keys, from local eval sets (exp/v11/runq.js layout: rows.jsonl + games/<key>/game.replay).
//   opening (our team, the study's definitions where the replay allows): frontier bin of every head of ours at the first turn of r5 / r10 / r25
//   (exp/spatial/lib.js geometry, bin 2 = the middle), the first round a head of ours stands in bin 2 at its turn start (games that got there by r50),
//   our splits in r0-10;
//   outcome: win, eliminated, final longest, our units at r50 / r100, natural intake (mass ledger nat_*), deaths of ours by cause (trap, rammed, ram);
//   module: the " op" tags (roles matched, scheduled splits, hand-back reasons).
// usage: node exp/v14/opreport.js --sets v14=dir[,dir] --sets v12=dir[,dir] [--out file.md] [--jobs 3]
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const NAME = { default: 'Default/a', devil: 'Devil/a', devil_b: 'Devil/b', schooltime: 'Schooltime/a', schooltime_b: 'Schooltime/b', slithery_fight: 'Slithery Fight/a',
  slithery_fight_b: 'Slithery Fight/b', trophy: 'Trophy/a', trauma: 'Trauma/a', queen_of_spades: 'Queen Of Spades/a', queen_of_spades_b: 'Queen Of Spades/b' };
// the study's top winners (opening-book.md: key facts, §2 table, §4 tables): r0-10 splits a game, first middle round (mean over arrivals), r10 / r25 middle share
// + r25 heads, the §11 r25 bin targets (sides A | B, cluster means), r50 middle share and heads (§4)
const ELITE = {
  'Default/a': [4.32, 1.28, 24.6, 53.5, 7.5, '0/2/4/1/1 \\| 0/2/4/1/1', 65.4, 10.9], 'Devil/a': [2.97, 14.22, 0.0, 54.1, 8.2, '1/2/5/0/0 \\| 1/2/5/0/0', 58.1, 16.1],
  'Devil/b': [2.96, 13.75, 0.0, 55.9, 7.1, '1/2/4/0/0 \\| 1/2/4/0/0', 60.1, 11.8], 'Trophy/a': [0.66, 7.66, 34.6, 55.3, 5.6, '0/1/3/1/0 \\| 0/1/4/0/0', 50.8, 14.5],
  'Schooltime/a': [2.99, 7.67, 10.2, 45.7, 6.0, '1/2/2/1/0 \\| 0/1/4/1/0', 62.8, 13.6], 'Schooltime/b': [3.00, 7.71, 12.9, 39.4, 5.9, '1/2/2/1/0 \\| 0/2/3/1/0', 45.9, 7.9],
  'Slithery Fight/a': [23.81, 6.42, 3.2, 17.5, 31.1, '16/7/4/1/0 \\| 16/9/7/0/0', 19.6, 47.1], 'Slithery Fight/b': [23.68, 6.54, 3.4, 18.1, 30.1, '15/9/6/0/1 \\| 15/9/6/0/0', 20.8, 43.5],
  'Trauma/a': [1.78, 46.38, 0.0, 0.0, 4.3, '4/0/0/0/0 \\| 4/0/0/0/0', 0.8, 7.5], 'Queen Of Spades/a': [0.20, 12.34, 1.3, 32.2, 4.0, '0/2/1/1/0 \\| 0/2/2/0/0', 27.7, 7.3],
  'Queen Of Spades/b': [0.36, 13.46, 1.2, 29.9, 3.8, '1/2/1/0/0 \\| 1/2/1/0/0', 24.5, 6.8] };
const CPR = [5, 10, 15, 20, 25, 35, 50, 75, 100];

function analyseGame(file, row) {
  const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const { geometry } = require(path.join(ROOT, 'exp', 'spatial', 'lib.js'));
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const load = makeLoader(viewerSource());
  const R = load(file), M = R.match.map, W = M.width;
  const us = row.side, them = us === 'A' ? 'B' : 'A';
  const g = geometry(M, 'x', '?'), bin = g.bin[us];
  const snap = {}, units = {};
  let lastRound = -1, firstMid = null, splits10 = 0;
  const deaths = {}, deaths100 = {};
  const op = { procs: 0, roles: {}, splits: 0, why: {}, whyRound: {}, holdProcs: 0, holdTurns: 0, holdWhy: {}, holdWhyRound: {} };
  const holdProc = new Set(), holdEnd = new Set();
  const seenProc = new Set(), opProc = new Set();
  const hooks = {
    turn(d, round, ctx) {
      if (round !== lastRound) {
        lastRound = round;
        if (CPR.includes(round)) {
          const h = [0, 0, 0, 0, 0, 0];
          for (const o of ctx.drag.values()) if (o.team === us) { const b = bin[o.body[0].y * W + o.body[0].x]; h[b === undefined ? 5 : b]++; }
          snap[round] = h;
        }
        if (round === 50 || round === 100) { let c = 0; for (const o of ctx.drag.values()) if (o.team === us) c++; units[round] = c; }
      }
      if (d.team === us && firstMid === null && round <= 50 && bin[d.body[0].y * W + d.body[0].x] === 2) firstMid = round;
    },
    split(p, ch, e, round) { if (p.team === us && round <= 10) splits10++; },
    death(d, rec, idx, other, round) { if (d.team !== us) return; const c = ML.CAUSE[rec.cause] || String(rec.cause); deaths[c] = (deaths[c] || 0) + 1; if (round < 100) deaths100[c] = (deaths100[c] || 0) + 1; },
    indicator(e, round, ctx) {
      const d = ctx && ctx.drag ? ctx.drag.get(e.id) : null;
      if (!d || d.team !== us) return;
      const t = e.text || '';
      const s = / op(R[\d.]*)s(\s|$)/.exec(t);
      if (s) op.splits++;
      const a = / op(R[\d.]*)(>| |$)/.exec(t);
      if (a && !opProc.has(e.id)) { opProc.add(e.id); op.procs++; op.roles[a[1]] = (op.roles[a[1]] || 0) + 1; }
      const x = / opx([a-z])/.exec(t);
      if (x && !seenProc.has(e.id)) { seenProc.add(e.id); op.why[x[1]] = (op.why[x[1]] || 0) + 1; (op.whyRound[x[1]] = op.whyRound[x[1]] || []).push(round); }
      if (/ oph@/.test(t)) { op.holdTurns++; if (!holdProc.has(e.id)) { holdProc.add(e.id); op.holdProcs++; } }
      const hx = / ophx([a-z])/.exec(t);
      if (hx && !holdEnd.has(e.id)) { holdEnd.add(e.id); op.holdWhy[hx[1]] = (op.holdWhy[hx[1]] || 0) + 1; (op.holdWhyRound[hx[1]] = op.holdWhyRound[hx[1]] || []).push(round); }
    },
  };
  const G = ML.perGame(R, { map: NAME[row.map] }, hooks);
  const nat = (X, nb = 50) => ['nat_own', 'nat_enemy', 'nat_neutral'].reduce((acc, k) => acc + X.fl[ML.FI[k]].slice(0, nb).reduce((p, q) => p + q, 0), 0);
  const res = R.result;
  return { key: row.key, file: row.map, map: NAME[row.map], opp: row.opp, side: us, seed: row.seed, won: res.winner === us ? 1 : 0,
    elim: res['team' + us].dragonCount === 0 ? 1 : 0, final: [res['team' + us].dragonCount > 0 ? res['team' + us].longestDragon : 0, res['team' + them].longestDragon],
    snap, units, firstMid, splits10, nat: [nat(G[us]), nat(G[them])], nat50: nat(G[us], 5), nat100: nat(G[us], 10), deaths, deaths100, op };
}

if (process.argv[2] === '--worker') {
  process.on('message', t => { let r; try { r = analyseGame(t.file, t.row); } catch (e) { r = { key: t.row.key, error: String(e.stack || e).slice(0, 400) }; } process.send(r); });
  return;
}

const args = process.argv.slice(2), get = k => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const sets = []; for (let i = 0; i < args.length; i++) if (args[i] === '--sets') { const [nm, ds] = args[i + 1].split('='); sets.push({ name: nm, dirs: ds.split(',') }); }
const out = get('--out'), jobs = +(get('--jobs') || 3), cacheDir = get('--cache') || path.join(ROOT, 'exp', 'v14', 'cache');
fs.mkdirSync(cacheDir, { recursive: true });

(async () => {
  const results = {};
  for (const S of sets) {
    const tasks = [];
    for (const dir of S.dirs) {
      const cache = path.join(cacheDir, dir.replace(/[\/]/g, '_') + '.op2.jsonl');
      const have = new Map(fs.existsSync(cache) ? fs.readFileSync(cache, 'utf8').trim().split('\n').filter(Boolean).map(l => { const o = JSON.parse(l); return [o.key, o]; }) : []);
      if (!fs.existsSync(path.join(dir, 'rows.jsonl'))) continue;
      // clean rows only (a result, exit 0, no error or bot problem), the last one per key (a rerun after a sleep or a kill)
      const lastClean = new Map();
      for (const r of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l)))
        if (r.G !== undefined && (r.exit === 0 || r.exit === undefined) && !r.error && !r.botProblem && NAME[r.map]) lastClean.set(r.key, r);
      const rows = [...lastClean.values()];
      for (const r of rows) {
        if (have.has(r.key)) continue;
        const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
        tasks.push({ file, row: r, cache });
      }
      for (const [k, o] of have) if (!tasks.some(t => t.row.key === k)) (results[S.name] = results[S.name] || new Map()).set(k, o);
    }
    const res = results[S.name] = results[S.name] || new Map();
    await new Promise(done => {
      if (!tasks.length) return done();
      let next = 0, live = 0;
      const spawn = () => {
        const w = cp.fork(__filename, ['--worker'], { stdio: ['ignore', 'ignore', 'inherit', 'ipc'] }); live++;
        const feed = () => {
          if (next >= tasks.length) { w.kill(); live--; if (!live) done(); return; }
          const t = tasks[next++];
          w.once('message', r => { if (!r.error) { res.set(r.key, r); fs.appendFileSync(t.cache, JSON.stringify(r) + '\n'); } else console.error(t.row.key, r.error); feed(); });
          w.send(t);
        };
        feed();
      };
      for (let j = 0; j < Math.min(jobs, tasks.length); j++) spawn();
    });
  }
  const names = sets.map(s => s.name);
  const common = [...results[names[0]].keys()].filter(k => names.every(n => results[n].has(k)));
  const byMap = {};
  for (const k of common) { const m = results[names[0]].get(k).map; (byMap[m] = byMap[m] || []).push(k); }
  const L = [];
  const f1 = x => (x === null || x === undefined || Number.isNaN(x)) ? '–' : (+x).toFixed(1);
  const pct = (a, b) => b ? (100 * a / b).toFixed(1) + '%' : '–';
  const mean = xs => xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : NaN;
  const median = xs => { if (!xs.length) return NaN; const s = [...xs].sort((a, b) => a - b); const m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
  L.push(`# v1.4 local report: ${names.join(' vs ')} (same keys: ${common.length})`, '');
  L.push('## Opening metrics against the elite winners (opening-book.md)', '');
  L.push('| map | set | games | r0-10 splits/game | first middle r (arrived/N) | r10 middle share | r25 middle share | r25 heads | r25 bins 0-4 | r50 middle share | r50 heads |');
  L.push('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |');
  const mapsSorted = Object.keys(byMap).sort();
  for (const m of mapsSorted) {
    const E = ELITE[m];
    if (E) L.push(`| ${m} | elite winners | study | ${E[0].toFixed(2)} | ${E[1].toFixed(2)} | ${E[2].toFixed(1)}% | ${E[3].toFixed(1)}% | ${E[4]} | ${E[5]} | ${E[6]}% | ${E[7]} |`);
    for (const n of names) {
      const G = byMap[m].map(k => results[n].get(k));
      const arr = G.filter(x => x.firstMid !== null).map(x => x.firstMid);
      const sum = r => { const h = [0, 0, 0, 0, 0, 0]; for (const x of G) if (x.snap[r]) x.snap[r].forEach((v, i) => h[i] += v); return h; };
      const h10 = sum(10), h25 = sum(25), h50 = sum(50), n10 = h10.reduce((a, b) => a + b, 0), n25 = h25.reduce((a, b) => a + b, 0), n50 = h50.reduce((a, b) => a + b, 0);
      const g50 = G.filter(x => x.snap[50]).length;
      L.push(`| ${m} | ${n} | ${G.length} | ${f1(mean(G.map(x => x.splits10)))} | ${f1(mean(arr))} (${arr.length}/${G.length}) | ${pct(h10[2], n10)} | ${pct(h25[2], n25)} | ${f1(n25 / G.length)} | ${h25.slice(0, 5).join('/')} | ${pct(h50[2], n50)} | ${f1(g50 ? n50 / g50 : NaN)} |`);
    }
  }
  // the chain after the opening (lead: middle share, heads, intake at r50 / r100), with the elite winners' and losers' checkpoint shares
  let ST = null; try { ST = JSON.parse(fs.readFileSync(path.join(ROOT, 'exp', 'spatial-all', 'tables.json'), 'utf8')).maps; } catch (e) {}
  L.push('', '## Chain after the opening: middle share (bin 2) and enemy bins (3-4) at r25-r100, heads, intake, early rammed deaths', '');
  L.push('| map | set | mid r25 / r50 / r75 / r100 | enemy bins r50 / r100 | heads r50 / r100 | intake r0-49 / r0-99 | rammed / ram / trap deaths r0-99 per game |');
  L.push('| --- | --- | --- | --- | --- | --- | --- |');
  for (const m of mapsSorted) {
    if (ST && ST[m]) for (const [cls, lab] of [['elite-winners', 'elite winners'], ['elite-losers', 'elite losers']]) {
      const c = ST[m].classes[cls]; if (!c) continue;
      const cpS = r => c.checkpoints[r] ? c.checkpoints[r].headShare : null;
      const mid = r => cpS(r) ? (100 * cpS(r)[2]).toFixed(1) + '%' : '–', en = r => cpS(r) ? (100 * (cpS(r)[3] + cpS(r)[4])).toFixed(1) + '%' : '–';
      const hp = r => c.checkpoints[r] ? c.checkpoints[r].headsPerGame.toFixed(1) : '–';
      L.push(`| ${m} | ${lab} | ${mid(25)} / ${mid(50)} / – / ${mid(100)} | ${en(50)} / ${en(100)} | ${hp(50)} / ${hp(100)} | – | – |`);
    }
    for (const n of names) {
      const G = byMap[m].map(k => results[n].get(k));
      const sh = (r, bins) => { let a = 0, t = 0; for (const x of G) if (x.snap[r]) { t += x.snap[r].slice(0, 5).reduce((p, q) => p + q, 0); for (const b of bins) a += x.snap[r][b]; } return t ? (100 * a / t).toFixed(1) + '%' : '–'; };
      const d100 = c => f1(mean(G.map(x => (x.deaths100 || {})[c] || 0)));
      L.push(`| ${m} | ${n} | ${sh(25, [2])} / ${sh(50, [2])} / ${sh(75, [2])} / ${sh(100, [2])} | ${sh(50, [3, 4])} / ${sh(100, [3, 4])} | ${f1(mean(G.map(x => x.units[50] || 0)))} / ${f1(mean(G.map(x => x.units[100] || 0)))} | ${f1(mean(G.map(x => x.nat50)))} / ${f1(mean(G.map(x => x.nat100)))} | ${d100('rammed')} / ${d100('ram')} / ${d100('trap')} |`);
    }
  }
  L.push('', '## Outcome and chain (same keys)', '');
  L.push('| map | set | games | wins | eliminated | final longest mean / median (theirs) | units r50 / r100 | intake ours / theirs | deaths trap / rammed / ram / enemyBody |');
  L.push('| --- | --- | --- | --- | --- | --- | --- | --- | --- |');
  const rowsFor = (label, keys) => {
    for (const n of names) {
      const G = keys.map(k => results[n].get(k));
      const d = c => G.reduce((a, x) => a + (x.deaths[c] || 0), 0);
      L.push(`| ${label} | ${n} | ${G.length} | ${G.reduce((a, x) => a + x.won, 0)} | ${G.reduce((a, x) => a + x.elim, 0)} | ${f1(mean(G.map(x => x.final[0])))} / ${f1(median(G.map(x => x.final[0])))} (${f1(mean(G.map(x => x.final[1])))}) | ${f1(mean(G.map(x => x.units[50] || 0)))} / ${f1(mean(G.map(x => x.units[100] || 0)))} | ${f1(mean(G.map(x => x.nat[0])))} / ${f1(mean(G.map(x => x.nat[1])))} | ${d('trap')} / ${d('rammed')} / ${d('ram')} / ${d('enemyBody')} |`);
    }
  };
  for (const m of mapsSorted) rowsFor(m, byMap[m]);
  rowsFor('all', common);
  const elimMaps = common.filter(k => /^(Default|Devil|Trophy|Queen)/.test(results[names[0]].get(k).map));
  if (elimMaps.length) rowsFor('elimination maps', elimMaps);
  L.push('', '## Paired (first set minus second, same key)', '');
  if (names.length === 2) {
    L.push('| map | pairs | final longest: higher / lower / equal | median diff | wins first / second |');
    L.push('| --- | --- | --- | --- | --- |');
    for (const m of [...mapsSorted, 'all']) {
      const keys = m === 'all' ? common : byMap[m];
      const dif = keys.map(k => results[names[0]].get(k).final[0] - results[names[1]].get(k).final[0]);
      L.push(`| ${m} | ${keys.length} | ${dif.filter(x => x > 0).length} / ${dif.filter(x => x < 0).length} / ${dif.filter(x => x === 0).length} | ${f1(median(dif))} | ${keys.reduce((a, k) => a + results[names[0]].get(k).won, 0)} / ${keys.reduce((a, k) => a + results[names[1]].get(k).won, 0)} |`);
    }
  }
  L.push('', '## Module tags (processes with a role; hand-back reasons and their mean round)', '');
  L.push('| map | set | role processes / game | scheduled splits / game | hand-back: reason n (mean round) |');
  L.push('| --- | --- | --- | --- | --- |');
  for (const m of mapsSorted) for (const n of names) {
    const G = byMap[m].map(k => results[n].get(k));
    const why = {}, wr = {};
    for (const x of G) for (const [c, v] of Object.entries(x.op.why)) { why[c] = (why[c] || 0) + v; (wr[c] = wr[c] || []).push(...x.op.whyRound[c]); }
    const procs = G.reduce((a, x) => a + x.op.procs, 0);
    if (!procs && !Object.keys(why).length) continue;
    L.push(`| ${m} | ${n} | ${f1(procs / G.length)} | ${f1(G.reduce((a, x) => a + x.op.splits, 0) / G.length)} | ${Object.keys(why).sort().map(c => `${c} ${why[c]} (${f1(mean(wr[c]))})`).join(', ')} |`);
  }
  L.push('', '## Hold phase tags (processes that held; end reasons, mean round)', '');
  L.push('| map | set | holding processes / game | holding turns / game | ends: reason n (mean round) |');
  L.push('| --- | --- | --- | --- | --- |');
  for (const m of mapsSorted) for (const n of names) {
    const G = byMap[m].map(k => results[n].get(k));
    const hp = G.reduce((a, x) => a + (x.op.holdProcs || 0), 0); if (!hp) continue;
    const why = {}, wr = {};
    for (const x of G) for (const [c, v] of Object.entries(x.op.holdWhy || {})) { why[c] = (why[c] || 0) + v; (wr[c] = wr[c] || []).push(...x.op.holdWhyRound[c]); }
    L.push(`| ${m} | ${n} | ${f1(hp / G.length)} | ${f1(G.reduce((a, x) => a + (x.op.holdTurns || 0), 0) / G.length)} | ${Object.keys(why).sort().map(c => `${c} ${why[c]} (${f1(mean(wr[c]))})`).join(', ')} |`);
  }
  const text = L.join('\n') + '\n';
  if (out) fs.writeFileSync(out, text);
  process.stdout.write(text);
})();
