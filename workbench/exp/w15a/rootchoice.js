#!/usr/bin/env node
// W15a: at each lineage-root entry into a dead branch (deadclass.js --roots, diag build), what the planner saw: the chosen candidate's area
// safety (s >= 0: the flood fill found room, i.e. the bot thought it open; s < 0: it knew the region was bounded) and whether another
// candidate was viable (b + s + c > -100). usage: node exp/w15a/rootchoice.js <diag game dirs...> (side A)
'use strict';
const cp = require('child_process'), path = require('path');
const out = {};
const add = k => { out[k] = (out[k] || 0) + 1; };
for (const d of process.argv.slice(2)) {
  const txt = cp.execFileSync('node', [path.join(__dirname, 'deadclass.js'), d, 'A', '--roots'], { encoding: 'utf8', maxBuffer: 1 << 26 });
  for (const l of txt.split('\n').filter(l => l.includes('root #'))) {
    const m = /L(\d+) (unknown|known-dead|room)( bait)? .*\| (\S+) v(-?[0-9.]+) .*?\[(.*?)\]/.exec(l);
    if (!m) { add('unparsed'); continue; }
    const [, L, view, bait, dir, v] = m; const cands = m[6].trim().split(/\s+/).map(c => { const q = /^(\w+):b(-?[0-9.]+)\/s(-?[0-9.]+)\/c(-?[0-9.]+)/.exec(c); return q && { dir: q[1], b: +q[2], s: +q[3], c: +q[4] }; }).filter(Boolean);
    const ch = cands.find(c => c.dir === dir); if (!ch) { add('no chosen'); continue; }
    const doomed = +v < -100;
    const alt = cands.filter(c => c.dir[0] !== dir[0]).some(c => c.b + c.s + c.c > -100);
    const k = `${view.padEnd(10)} ${doomed ? 'doomed' : 'free  '} L${+L < 4 ? '<4 ' : '>=4'} bot ${ch.s >= 0 ? 'open ' : 'dead '} ${alt ? 'had a viable other first step' : 'no viable other first step'}`;
    add(k);
  }
}
for (const [k, n] of Object.entries(out).sort()) console.log(String(n).padStart(5) + '  ' + k);
