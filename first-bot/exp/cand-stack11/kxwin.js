#!/usr/bin/env node
// cand-stack11 local diagnosis: which "am I the king" window would match the replay at the " kx" turns? Belief model (vision only; the bot
// also hears sonar news, so real beliefs are at least this informed): an own dragon counts as "believed longer" when it was in our 7x7 view
// (its head within Chebyshev 3) within W rounds and was longer than us then; dead ones stay believed (World::dragons never forgets).
// pigeonhole (longerAllyKnown): believed B allies within W, U = our units now; at least B - (U - 1) of them are dead, so "not king" only when
// the believed longer ones outnumber that. Reported per W: false king (not our longest, yet no believed longer ally) and missed king (our
// longest, yet a believed longer ally). usage: node exp/cand-stack11/kxwin.js <eval dir> [...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const MAPNAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma', queen_of_spades: 'Queen Of Spades', schooltime: 'Schooltime', slithery_fight: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const WS = [20, 40, 60, 100, 500];
const acc = {}; for (const w of WS) for (const p of [0, 1]) acc[w + (p ? 'p' : '')] = { fk: 0, mk: 0 };
let nL = 0, nN = 0;
for (const dirArg of process.argv.slice(2)) {
  const dir = path.resolve(dirArg);
  for (const l of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean)) {
    const row = JSON.parse(l), [opp, map, side, seed] = row.key.split(':');
    const f = path.join(dir, 'games', `${opp}_${map}_${side}_${seed}`, 'game.replay'); if (!fs.existsSync(f)) continue;
    const mapName = MAPNAME[map.replace(/_(b|10)$/, '')] || map, us = side;
    const R = load(f);
    const seen = new Map(); // d.id -> Map(o.id -> [round, length then])
    let W = 0, H = 0;
    const cheb = (p, q) => { const dx = Math.abs(p.x - q.x), dy = Math.abs(p.y - q.y); return Math.max(Math.min(dx, W - dx), Math.min(dy, H - dy)); };
    const hooks = {
      turn(d, r, c) {
        W = c.W; H = c.H;
        if (d.team !== us) return;
        let m = seen.get(d.id); if (!m) seen.set(d.id, m = new Map());
        for (const o of c.drag.values()) if (o.team === us && o.id !== d.id && cheb(o.body[0], d.body[0]) <= 3) m.set(o.id, [r, o.body.length]);
      },
      indicator(e, r, c) {
        const d = c.drag.get(e.id); if (!d || d.team !== us) return;
        const h = (e.text || '').split('|')[0]; if (!/(^|\s)kx\d+(\s|$)/.test(h)) return;
        let longest = 1, U = 0; for (const o of c.drag.values()) if (o.team === us) { U++; if (o.id !== d.id && o.body.length > d.body.length) longest = 0; }
        if (longest) nL++; else nN++;
        const m = seen.get(d.id) || new Map();
        for (const w of WS) {
          let B = 0, Lg = 0;
          for (const [, [rr, len]] of m) { if (r - rr > w) continue; B++; if (len > d.body.length) Lg++; }
          for (const p of [0, 1]) {
            const notKing = p ? Lg > Math.max(0, B - (U - 1)) : Lg > 0;
            const a = acc[w + (p ? 'p' : '')];
            if (!longest && !notKing) a.fk++;
            if (longest && notKing) a.mk++;
          }
        }
      },
    };
    perGame(R, { map: mapName }, hooks);
  }
}
console.log(`kx turns: our longest ${nL}, not our longest ${nN}`);
for (const w of WS) for (const p of [0, 1]) { const a = acc[w + (p ? 'p' : '')]; console.log(`W=${String(w).padStart(3)}${p ? ' +pigeonhole' : '             '}: false king ${a.fk}/${nN} (${Math.round(100 * a.fk / Math.max(1, nN))}%) · missed king ${a.mk}/${nL} (${Math.round(100 * a.mk / Math.max(1, nL))}%) · kx turns kept that are our longest ${nL - a.mk}, share ${Math.round(100 * (nL - a.mk) / Math.max(1, nL - a.mk + a.fk))}%`); }
