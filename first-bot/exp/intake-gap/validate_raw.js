#!/usr/bin/env node
// Checks exp/intake-gap/rawload.js against the official viewer conversion on a deterministic spread of replays:
// every decoded event (all kinds but sonar/logs/debug draws) must equal the official one, and sonar counts per sender too.
// usage: node exp/intake-gap/validate_raw.js [--top N] [--online N]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const RL = require('./rawload.js');
const argv = process.argv.slice(2), opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? +argv[i + 1] : d; };
const files = [];
const idx = fs.readFileSync(path.join(ROOT, 'data', 'top', 'index.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l));
const nt = opt('top', 12), step = Math.max(1, Math.floor(idx.length / nt));
for (let i = 0; i < idx.length && files.length < nt; i += step) files.push(path.join(ROOT, 'data', 'top', String(idx[i].battleId), idx[i].gameId + '.replay.gz'));
const no = opt('online', 8);
const sets = fs.readdirSync(path.join(ROOT, 'data', 'online')).filter(s => /^cand-stack|merge2/.test(s));
for (let i = 0; i < no; i++) { const s = sets[i % sets.length], d = path.join(ROOT, 'data', 'online', s); const f = fs.readdirSync(d).filter(x => x.endsWith('.replay')).sort()[i * 7 % 70]; if (f) files.push(path.join(d, f)); }
let bad = 0, ev = 0;
for (const f of files) { const r = RL.validate(f); ev += r.events; bad += r.bad; if (r.bad) console.log('MISMATCH', f, r.bad); }
console.log(`files ${files.length}, events ${ev}, mismatches ${bad}`);
