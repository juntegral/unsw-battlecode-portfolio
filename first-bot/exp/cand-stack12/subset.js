#!/usr/bin/env node
// cand-stack12: a local eval subset folder for tools/mech_check.js (rows.jsonl filtered by map, games linked), so that pools compare the same keys.
// usage: node exp/cand-stack12/subset.js <out label> <maps: pf|off> <src label> [<src label> ...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const [out, which, ...srcs] = process.argv.slice(2);
const PF = new Set(['default', 'devil', 'devil_b', 'queen_of_spades', 'queen_of_spades_b', 'schooltime', 'schooltime_b', 'slithery_fight', 'slithery_fight_b', 'trauma', 'trophy']);
const dir = path.join(ROOT, 'exp', out); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(path.join(dir, 'games'), { recursive: true });
const rows = [], seen = new Set();
for (const s of srcs) for (const l of fs.readFileSync(path.join(ROOT, 'exp', s, 'rows.jsonl'), 'utf8').split('\n')) {
  if (!l.trim()) continue; const r = JSON.parse(l); if (r.G === undefined || seen.has(r.key)) continue;
  const [opp, map, side, seed] = r.key.split(':'); if ((which === 'pf') !== PF.has(map)) continue;
  const g = `${opp}_${map}_${side}_${seed}`, src = path.join(ROOT, 'exp', s, 'games', g); if (!fs.existsSync(path.join(src, 'game.replay'))) continue;
  seen.add(r.key); rows.push(l); fs.symlinkSync(src, path.join(dir, 'games', g));
}
fs.writeFileSync(path.join(dir, 'rows.jsonl'), rows.join('\n') + '\n');
console.log(`${out}: ${rows.length} games (${which}) from ${srcs.join(', ')}`);
