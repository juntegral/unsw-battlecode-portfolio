#!/usr/bin/env node
// Key decision rules of research/observations/top-decisions.md measured on our side of local eval games.
// usage: node exp/cand-swarm1/rules.js <label> [<label> ...] [--jobs 2] [--seeds 1,2]
// Rows come from tools/decisions.js extractGame() (same reconstruction and columns as the study; every turn of our side
// is kept with weight 1). The state/action definitions of R1, R2, R3, R4 are copied verbatim from
// tools/decisions_rules.js (RULES). Output per label: weighted rate = actions / states over our side's rows, the
// number of states, and a game-clustered bootstrap 95% interval (1000 draws, fixed seed).
'use strict';
const path = require('path'), fs = require('fs');
const cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');

const n = (v, C, k) => +v[C[k]];
const SK = new Set(['S', 'W', 'Aq', 'Ax']);
const RULES = [ // verbatim from tools/decisions_rules.js
  { id: 'R1', pop: (v, C) => n(v, C, 'L') === 4 && (v[C.act] === 'M' || v[C.act] === 'P'), act: (v, C) => v[C.act] === 'P' },
  { id: 'R2', pop: (v, C) => n(v, C, 'L') >= 5 && n(v, C, 'L') <= 9 && n(v, C, 'room') >= 6 && n(v, C, 'r') <= 166 && (v[C.act] === 'M' || v[C.act] === 'P'), act: (v, C) => v[C.act] === 'P' },
  { id: 'R3', pop: (v, C) => n(v, C, 'free') >= 1 && n(v, C, 'aLg') >= 8 && n(v, C, 'aDg') <= 3 && n(v, C, 'r') >= 350, act: (v, C) => SK.has(v[C.fate]) },
  { id: 'R4', pop: (v, C) => n(v, C, 'L') <= 3 && n(v, C, 'oppN') >= 1 && n(v, C, 'aN') >= 1 && n(v, C, 'oppL') >= n(v, C, 'L') && n(v, C, 'eN') <= 2 && (v[C.act] === 'M' || v[C.act] === 'P'), act: (v, C) => v[C.ram] === '1' },
];

if (process.argv.includes('--rules-child')) {
  const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
  const dec = require(path.join(ROOT, 'tools', 'decisions.js'));
  const load = tf.makeLoader(tf.viewerSource());
  process.on('message', t => {
    try {
      const R = load(t.file);
      const { rows } = dec.extractGame(R, { key: t.key, ourSide: t.side, seedHash: 12345 });
      const C = dec.C, out = {};
      for (const rule of RULES) out[rule.id] = [0, 0];
      for (const raw of rows) {
        const v = raw.map(x => String(x));
        if (v[C.tm] !== t.side) continue;
        const w = +v[C.w] || 1;
        for (const rule of RULES) if (rule.pop(v, C)) { out[rule.id][0] += w; if (rule.act(v, C)) out[rule.id][1] += w; }
      }
      process.send({ key: t.key, label: t.label, out });
    } catch (e) { process.send({ key: t.key, label: t.label, error: String(e).slice(0, 300) }); }
  });
}
else {

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const jobs = +opt('jobs', 2), seeds = opt('seeds', '1,2').split(',').map(Number);
const labels = argv.filter((a, i) => !a.startsWith('--') && !(i > 0 && argv[i - 1].startsWith('--')));
const tasks = [];
for (const label of labels) {
  const dir = path.join(ROOT, 'exp', label);
  for (const l of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue; const r = JSON.parse(l); if (r.G === undefined || !seeds.includes(r.seed)) continue;
    const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
    tasks.push({ label, key: r.key, side: r.side, file });
  }
}
const res = {}; for (const L of labels) res[L] = [];
let next = 0, done = 0;
(async () => {
  await Promise.all(Array.from({ length: jobs }, () => new Promise(resolve => {
    const w = cp.fork(__filename, ['--rules-child'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
    const feed = () => { if (next >= tasks.length) { w.kill(); resolve(); return; } w.send(tasks[next++]); };
    w.on('message', m => { done++; if (m.error) console.error(m.key, m.error); else res[m.label].push(m.out); feed(); });
    w.on('error', e => { console.error(e); resolve(); });
    feed();
  })));
  let s = 20260930; const rnd = () => (s = (Math.imul(s, 1103515245) + 12345) >>> 0) / 4294967296;
  console.log('| label | games | R1 L4 splits 2+2 | R2 L5-9 open r<=166 split | R3 beside ally L>=8, r>=350: self-kill | R4 L<=3, ally in view, equal/longer enemy rammable: ram |');
  console.log('|---|---:|---|---|---|---|');
  for (const L of labels) {
    const G = res[L];
    const cell = id => {
      const W = G.reduce((a, g) => a + g[id][0], 0), A = G.reduce((a, g) => a + g[id][1], 0);
      if (!W) return '- (0)';
      const reps = [];
      for (let b = 0; b < 1000; b++) { let w = 0, a = 0; for (let i = 0; i < G.length; i++) { const g = G[Math.floor(rnd() * G.length)]; w += g[id][0]; a += g[id][1]; } reps.push(w ? a / w : 0); }
      reps.sort((x, y) => x - y);
      return `${(100 * A / W).toFixed(1)}% [${(100 * reps[25]).toFixed(1)}–${(100 * reps[974]).toFixed(1)}] (n ${W})`;
    };
    console.log(`| ${L} | ${G.length} | ${cell('R1')} | ${cell('R2')} | ${cell('R3')} | ${cell('R4')} |`);
  }
})();
}
