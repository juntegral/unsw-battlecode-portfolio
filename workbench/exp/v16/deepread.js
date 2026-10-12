#!/usr/bin/env node
// v1.6 deep read: one local game's conversion phase (r >= --from, default 250) for our team, as text. Read-only replay reconstruction
// (tools/mass_ledger.js perGame, the same simulation the conversion study used).
//   every --every rounds (default 10): our dragons by length (top --top, default 6): #id L<len> @x,y and the label of its last turn
//   every death of ours from --from: round, id, length, cause, the label of its turn, and who ate its drops (#id L<len> r<round>, E = enemy)
//   every split of a dragon of ours of length >= 8 (parent / child lengths)
// usage: node exp/v16/deepread.js <game.replay> <side A|B> [--from 250] [--every 10] [--top 6] [--labels]   (--labels: every labelled turn of the top dragon)
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const raw = require(path.join(ROOT, 'legacy', 'exp', 'intake-gap', 'rawload.js'));
const args = process.argv.slice(2), get = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const file = args[0], us = args[1];
const FROM = +get('--from', 250), EVERY = +get('--every', 10), TOP = +get('--top', 6), LABELS = args.includes('--labels');
const MAPS = { autarky: 'Autarky', default: 'Default', devil: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma', queen_of_spades: 'Queen Of Spades',
  schooltime: 'Schooltime', slithery_fight: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const R = raw.load(file);
const slug = (/games\/proxy4_\w+?_([a-z_]+?)(?:_b)?_[AB]_\d+/.exec(file) || [])[1];
const map = MAPS[slug] || 'Slithery Fight';
const label = new Map(), deathLabel = [], lines = [];
const xy = (p) => p.x + ',' + p.y;
const out = (s) => lines.push(s);
let lastSnap = -1;
const hooks = {
  turn(d, r, c) {
    if (r >= FROM && r !== lastSnap && r % EVERY === 0) {
      lastSnap = r;
      const a = [...c.drag.values()].filter(x => x.team === us).sort((x, y) => y.body.length - x.body.length || x.id - y.id);
      const en = [...c.drag.values()].filter(x => x.team !== us).sort((x, y) => y.body.length - x.body.length);
      out(`r${r} units ${a.length} mass ${a.reduce((s, x) => s + x.body.length, 0)} | ` + a.slice(0, TOP).map(x => `#${x.id} L${x.body.length} @${xy(x.body[0])} [${(label.get(x.id) || '').slice(0, 48)}]`).join('  ') +
        `  || enemy top L${en[0] ? en[0].body.length : 0}`);
    }
  },
  indicator(e, r, c) {
    label.set(e.id, e.text || '');
    if (LABELS && r >= FROM) { const d = c.drag.get(e.id); if (d && d.team === us && d.body.length >= 8) out(`  r${r} #${e.id} L${d.body.length} @${xy(d.body[0])}: ${e.text}`); }
  },
  split(p, ch, e, r) { if (p.team === us && r >= FROM && (p.body.length + ch.body.length) >= 8) out(`  r${r} split #${p.id} -> L${p.body.length} + child #${ch.id} L${ch.body.length} [${(label.get(p.id) || '').slice(0, 60)}]`); },
  death(d, rec, idx, other, r, c) {
    if (d.team !== us || r < FROM) return;
    deathLabel[idx] = { r, id: d.id, len: rec.len, cause: ML.CAUSE[rec.cause], king: rec.king, head: xy(d.body[0]), lab: (label.get(d.id) || '').slice(0, 70), eats: [] };
  },
  eat(d, k, o, r, c) { if (o >= 0 && deathLabel[o]) deathLabel[o].eats.push(`${d.team === us ? '' : 'E'}#${d.id} L${d.body.length} r${r}`); },
};
ML.perGame(R, { map, variant: 'a' }, hooks);
for (const x of deathLabel) if (x) lines.push(`  r${x.r} DEATH #${x.id} L${x.len} ${x.cause}${x.king ? ' KING' : ''} @${x.head} [${x.lab}] -> ${x.eats.join(', ') || '-'}`);
// order: snapshots and events by round (the death lines carry r first)
const rk = s => { const m = /r(\d+)/.exec(s); return m ? +m[1] : 0; };
lines.sort((a, b) => rk(a) - rk(b) || (a.startsWith('r') ? -1 : 1));
console.log(`${path.relative(ROOT, file)} side ${us} rounds ${R.result ? R.result.endReason : ''} result ${JSON.stringify(R.result && { winner: R.result.winner, A: R.result.teamA.longestDragon, B: R.result.teamB.longestDragon })}`);
console.log(lines.join('\n'));
