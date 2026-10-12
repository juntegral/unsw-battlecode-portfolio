#!/usr/bin/env node
// Random 300 of the top games this resumed pass added (cached now, not cached before the resume), for the independent recount.
// The draw is fixed by a seed: order the new keys by FNV-1a hash of "<seed>|<key>" and take the first 300.
// usage: node exp/endgame-king/pick_new300.js [--seed endgame-king-2026-10-01] [--n 300] > exp/endgame-king/recount-new300.keys
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const argv = process.argv.slice(2), opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const seed = opt('seed', 'endgame-king-2026-10-01'), n = +opt('n', 300);
const hash32 = s => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; };
const before = new Set(fs.readFileSync(path.join(__dirname, 'cached-before-resume.keys'), 'utf8').split('\n').filter(Boolean));
const now = []; for (const l of fs.readFileSync(path.join(ROOT, '.cache', 'endgame-king', 'top.jsonl'), 'utf8').split('\n')) { const m = /^\{"key":"([^"]+)"/.exec(l); if (m && !before.has(m[1])) now.push(m[1]); }
const pick = now.sort((a, b) => hash32(seed + '|' + a) - hash32(seed + '|' + b)).slice(0, n);
process.stderr.write(`new games ${now.length}, picked ${pick.length} (seed ${seed})\n`);
console.log(pick.join('\n'));
