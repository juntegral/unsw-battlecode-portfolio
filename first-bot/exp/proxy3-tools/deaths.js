#!/usr/bin/env node
'use strict';
// deaths.js — how a side's dragons die, per 100-round window: mode (tools/proxy_check.js modeCat) and length lost, for the
// opponents of our bot (default) or our side. Bodies re-simulated with tools/fragment_study.js study().
// usage: node exp/proxy3-tools/deaths.js --g "<name>=<src>[+<src>]" [...] [--maps schooltime,autarky] [--side them|us]
//   <src> = online:<set> (data/online/<set>) | local:<label>[@opp,...] (exp/<label>/rows.jsonl + games/)
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
const FS = require(path.join(ROOT, 'tools', 'fragment_study.js'));
const PC = require(path.join(ROOT, 'tools', 'proxy_check.js'));
const mapKey = n => String(n).toLowerCase().replace(/\.map$/, '').replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
function listGames(spec) {
  const out = [];
  for (const src of spec.split('+')) {
    const [kind, rest] = src.split(/:(.*)/s);
    if (kind === 'online') {
      const dir = path.join(ROOT, 'data', 'online', rest);
      for (const f of fs.readdirSync(dir).filter(x => /^game-\d+\.json$/.test(x))) {
        const g = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')); if (g.status !== 'completed') continue;
        const ours = g.teamAId === 583 ? 'A' : g.teamBId === 583 ? 'B' : null; if (!ours) continue;
        out.push({ file: path.join(dir, 'M' + g.id + '.replay'), map: mapKey(g.mapName), ours });
      }
    } else {
      const [label, o] = rest.split('@'); const opps = o ? new Set(o.split(',')) : null;
      for (const l of fs.readFileSync(path.join(ROOT, 'exp', label, 'rows.jsonl'), 'utf8').trim().split('\n')) {
        const r = JSON.parse(l); if (r.G === undefined || (opps && !opps.has(r.opp))) continue;
        const file = path.join(ROOT, 'exp', label, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
        out.push({ file, map: mapKey(r.map), ours: r.side });
      }
    }
  }
  return out;
}
const MODES = ['self-free', 'self-trapped', 'WS-free', 'WS-trapped', 'WS-sprint', 'O-own', 'O-enemy', 'H-ram', 'H-rammed', 'H-own', 'A-other'];
const argv = process.argv.slice(2); const groups = []; let side = 'them', maps = null;
for (let i = 0; i < argv.length; i++) { if (argv[i] === '--g') { const s = argv[++i], j = s.indexOf('='); groups.push([s.slice(0, j), s.slice(j + 1)]); } else if (argv[i] === '--side') side = argv[++i]; else if (argv[i] === '--maps') maps = new Set(argv[++i].split(',')); }
for (const [name, spec] of groups) {
  const agg = {}; let n = 0;
  for (const gm of listGames(spec)) {
    if (maps && !maps.has(gm.map.startsWith('prisoners') ? 'prisoners_dilemma' : gm.map)) continue;
    const R = load(gm.file), g = FS.study(R), s = side === 'us' ? gm.ours : (gm.ours === 'A' ? 'B' : 'A');
    n++;
    for (const d of g.deaths) {
      if (d.team !== s) continue;
      const w = Math.min(4, Math.floor(d.r / 100)), m = PC.modeCat(d), lc = d.len <= 4 ? 's' : d.len <= 9 ? 'm' : 'l';
      const k = w + '|' + m; if (!agg[k]) agg[k] = { n: 0, len: 0, s: 0, m: 0, l: 0 };
      agg[k].n++; agg[k].len += d.len; agg[k][lc]++;
    }
  }
  console.log(`\n### ${name}: ${n} games, per game: deaths (length lost) [small/mid/large count] by window`);
  console.log('| mode | ' + [0, 1, 2, 3, 4].map(w => 'r' + w * 100).join(' | ') + ' |\n|---|' + [0, 1, 2, 3, 4].map(() => '---').join('|') + '|');
  for (const m of MODES) {
    const cells = [0, 1, 2, 3, 4].map(w => { const a = agg[w + '|' + m]; return a ? `${(a.n / n).toFixed(1)} (${(a.len / n).toFixed(1)}) [${(a.s / n).toFixed(1)}/${(a.m / n).toFixed(1)}/${(a.l / n).toFixed(2)}]` : '–'; });
    if (cells.some(c => c !== '–')) console.log(`| ${m} | ${cells.join(' | ')} |`);
  }
}
