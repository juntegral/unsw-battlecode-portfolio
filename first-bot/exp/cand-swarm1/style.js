#!/usr/bin/env node
// Style metrics of our bot's sides (name "bot") in measured labels, next to the top-team target.
// usage: node exp/cand-swarm1/style.js <label>[,<label2>...] [<label> ...] [--maps elim|r500]
// Each argument is one row (labels joined by commas are pooled). Needs exp/<label>/sides.jsonl
// (node tools/proxy_check.js measure --label <label>) and the cached top sides (exp/proxy-check/top-sides.jsonl).
// Columns (medians over the sides whose game is still running at that round, as tools/proxy_check.js report):
// units r100 / r300, longest r300 / r400 / r500, 500-round-game winners' longest r300 / r400 / r500, splits per side,
// child length shares 2 / 3 / 4 / 5-9 / 10+, 4 -> 2+2 share.
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const pc = require(path.join(ROOT, 'tools', 'proxy_check.js'));
const ELIM = ['devil', 'trophy', 'prisoners_dilemma', 'queen_of_spades', 'default'];
const args = process.argv.slice(2);
const mi = args.indexOf('--maps'); const mapSel = mi >= 0 ? args[mi + 1] : null;
const labels = args.filter((a, i) => !a.startsWith('--') && !(mi >= 0 && i === mi + 1));
const keep = x => !mapSel || (mapSel === 'elim' ? ELIM.includes(x.map) : !ELIM.includes(x.map));
const f1 = x => x === null || x === undefined || Number.isNaN(x) ? '-' : Math.abs(x) >= 100 ? x.toFixed(0) : Math.abs(x) >= 10 ? x.toFixed(1) : x.toFixed(2);
const p0 = x => x === null || x === undefined ? '-' : (100 * x).toFixed(0) + '%';
const I = r => [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500].indexOf(r);
function row(name, S) {
  const m = pc.metrics(S);
  return `| ${name} | ${S.length} | ${f1(m.units[I(100)])} / ${f1(m.units[I(300)])} | ${f1(m.longest[I(300)])} / ${f1(m.longest[I(400)])} / ${f1(m.longest[I(500)])} | ${m.w500.n}: ${f1(m.w500.longest[I(300)])} / ${f1(m.w500.longest[I(400)])} / ${f1(m.w500.longest[I(500)])} | ${f1(m.splitsPerSide)} | ${['2', '3', '4', '5-9', '10+'].map(b => p0(m.child[b])).join(' / ')} | ${p0(m.cats['2+2'])} |`;
}
console.log(`maps: ${mapSel || 'all'}`);
console.log('| sides | n | units r100 / r300 | longest r300 / r400 / r500 | 500-game winners (n): longest r300 / r400 / r500 | splits/side | child 2 / 3 / 4 / 5-9 / 10+ | 2+2 |');
console.log('|---|---:|---|---|---|---:|---|---:|');
const fs = require('fs');
for (const L of labels) {
  const S = [];
  for (const l of L.split(',')) { const f = path.join(ROOT, 'exp', l, 'sides.jsonl'); if (fs.existsSync(f)) S.push(...pc.readJsonl(f)); }
  console.log(row(L, S.filter(x => x.name === 'bot' && keep(x))));
}
console.log(row('top teams (all)', pc.topSides().filter(keep)));
