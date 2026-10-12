#!/usr/bin/env node
// eff.js — eating, deaths by mode and splits per 1000 dragon-rounds of the opponents of our bot (or of a named side),
// from tools/proxy_check.js side records.
// usage (repository root): node exp/proxy3-tools/eff.js "<name>=<sides.jsonl>[+<sides.jsonl>][=<side name>]" ...
const PC = require(process.cwd() + '/tools/proxy_check.js');
const sets = {};
for (const a of process.argv.slice(2)) { const [name, files, filt] = a.split('='); let S = []; for (const f of files.split('+')) S.push(...PC.readJsonl(f)); S = S.filter(filt ? (x => x.name === filt) : (x => x.opp === 'bot')); sets[name] = S; }
const MODES = ['self-free', 'self-trapped', 'WS-free', 'WS-trapped', 'O-own', 'H-ram', 'H-rammed', 'H-own'];
console.log('set | sides | dragonRounds/side | eaten/1000dr | deaths/1000dr | ' + MODES.join(' | ') + ' | splits/1000dr');
for (const [k, S] of Object.entries(sets)) {
  const dr = S.reduce((s, x) => s + x.dragonRounds, 0);
  const per = f => (1000 * S.reduce((s, x) => s + f(x), 0) / dr).toFixed(1);
  console.log(`${k} | ${S.length} | ${(dr / S.length).toFixed(0)} | ${per(x => x.eatenAll)} | ${per(x => x.deaths)} | ${MODES.map(m => per(x => x.modes[m])).join(' | ')} | ${per(x => x.splits.n)}`);
}
