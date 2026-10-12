// voluntary deaths r300+ by distance to the king (Chebyshev), with pearl fates. usage: node voldist.js <label> [--maps a,b] [--opps a,b] [--top]
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = require('path').resolve(__dirname, '..', '..');
if (process.argv.includes('--vd-worker')) {
  const { load } = require(path.join(ROOT, 'tools/replay.js'));
  const fsd = require(path.join(ROOT, 'tools/fragment_study.js'));
  process.on('message', t => {
    try {
      const g = fsd.study(load(t.file));
      const res = [];
      for (const d of g.deaths) {
        if (d.team !== t.side || d.r < 300) continue;
        const own = d.mover && ((d.reason === 'A' && d.freeN > 0) || ((d.reason === 'W' || d.reason === 'S') && d.step === 0 && d.freeN > 0) || ((d.reason === 'O' || d.reason === 'H') && d.hitTeam === t.side && d.freeN > 0));
        if (!own) continue;
        let k20 = 0, o20 = 0, kAny = 0, L20 = 0;
        for (const fa of d.fates) { if (fa[1] !== 0) continue; if (fa[3] === 1) kAny++; if (fa[0] <= 20) { o20++; if (fa[3] === 1) k20++; if (fa[2] === 1) L20++; } }
        res.push([d.distKing, d.nDrop, k20, o20, kAny, L20, d.len, d.kingLen, d.reason]);
      }
      process.send({ res });
    } catch (e) { process.send({ err: String(e) }); }
  });
  return;
}
const argv = process.argv.slice(2);
const arg = (k, dflt) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : dflt; };
const mapsF = arg('maps') ? new Set(arg('maps').split(',')) : null, oppsF = arg('opps') ? new Set(arg('opps').split(',')) : null;
const tasks = [];
if (argv[0].startsWith('ONLINE:')) {
  const dir = path.join(ROOT, 'data', 'online', argv[0].slice(7)); const who = arg('who', 'us');
  const M500 = ['trauma', 'slithery_fight', 'schooltime', 'portals', 'autarky'];
  for (const f of fs.readdirSync(dir).filter(x => /^game-\d+\.json$/.test(x))) {
    const g = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')); const rep = path.join(dir, 'M' + g.id + '.replay');
    if (!fs.existsSync(rep) || g.status !== 'completed') continue; if (!M500.includes(String(g.mapName).toLowerCase().replace(/[^a-z0-9]+/g, '_'))) continue;
    const us = g.teamAId === 583 ? 'A' : 'B'; tasks.push({ file: rep, side: who === 'us' ? us : (us === 'A' ? 'B' : 'A') });
  }
} else if (argv[0] === 'TOP') {
  const TOP = path.join(ROOT, 'data', 'top');
  const keys = [...new Set(fs.readFileSync(path.join(TOP, 'snapshot-20260929a.keys'), 'utf8').split('\n').map(x => x.trim()).filter(Boolean))];
  const meta = new Map();
  for (const l of fs.readFileSync(path.join(TOP, 'features.jsonl'), 'utf8').split('\n')) { const mm = /^\{"meta":\{"battleId":(\d+),"gameId":(\d+)[,}]/.exec(l); if (!mm) continue; const k = mm[1] + ':' + mm[2]; if (meta.has(k)) continue; const f = JSON.parse(l); meta.set(k, { rounds: f.meta.rounds, A: f.meta.teams.A.name, B: f.meta.teams.B.name, winner: f.meta.winner }); }
  const lim = +(arg('limit', '200'));
  for (const k of keys.slice(0, lim)) { const m = meta.get(k); if (!m || m.rounds < 500) continue; if (m.A === 'SSS' || m.B === 'SSS') continue; const [b, g] = k.split(':');
    for (const side of ['A', 'B']) { if (arg('winners') && m.winner !== side) continue; const nm = m[side]; if (arg('team') && !arg('team').split('|').includes(nm)) continue; tasks.push({ file: path.join(TOP, b, g + '.replay.gz'), side }); } }
} else
for (const L of argv[0].split(',')) {
  const seen = new Set();
  for (const l of fs.readFileSync(path.join(ROOT, 'exp', L, 'rows.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue; const r = JSON.parse(l); if (r.G === undefined || seen.has(r.key)) continue; seen.add(r.key);
    if (mapsF && !mapsF.has(r.map)) continue; if (oppsF && !oppsF.has(r.opp)) continue;
    tasks.push({ file: path.join(ROOT, 'exp', L, 'games', r.key.replace(/:/g, '_'), 'game.replay'), side: r.side });
  }
}
const all = []; let live = 0; const q = tasks.slice();
for (let i = 0; i < 2; i++) {
  const c = cp.fork(__filename, ['--vd-worker'], { serialization: 'advanced' }); live++;
  const next = () => { const t = q.shift(); if (!t) { c.kill(); if (--live === 0) report(); return; } c.send(t); };
  c.on('message', m => { if (m.res) all.push(...m.res); next(); }); next();
}
function report() {
  const B = [[0, 1], [2, 2], [3, 4], [5, 8], [9, 999]];
  console.log(`voluntary deaths r300+: ${all.length} in ${tasks.length} games`);
  console.log('| dist to king | deaths/game | share | pearls/game | ->king@death 20r | ->then-longest 20r | ->own 20r | ->king@death ever | median len | median king len |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
  for (const [a, b] of B) {
    const X = all.filter(x => x[0] >= a && x[0] <= b); const drop = X.reduce((s, x) => s + x[1], 0);
    const med = arr => { const s = arr.slice().sort((p, q) => p - q); return s.length ? s[Math.floor(s.length / 2)] : '-'; };
    const pc = (n) => drop ? (100 * n / drop).toFixed(1) + '%' : '-';
    console.log(`| ${a}-${b > 100 ? '+' : b} | ${(X.length / tasks.length).toFixed(1)} | ${(100 * X.length / all.length).toFixed(1)}% | ${(drop / tasks.length).toFixed(1)} | ${pc(X.reduce((s, x) => s + x[2], 0))} | ${pc(X.reduce((s, x) => s + x[5], 0))} | ${pc(X.reduce((s, x) => s + x[3], 0))} | ${pc(X.reduce((s, x) => s + x[4], 0))} | ${med(X.map(x => x[6]))} | ${med(X.map(x => x[7]))} |`);
  }
}
