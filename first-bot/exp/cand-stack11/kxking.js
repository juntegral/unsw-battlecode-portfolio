#!/usr/bin/env node
// cand-stack11 local diagnosis: at every " kx" turn, is the labelled dragon our longest (replay)? If not, where is the longer ally:
// in the 7x7 view now (Chebyshev <= 3: the bot saw it, so its length estimate was short), seen in view within the last 20 rounds, or
// not seen for 20+ rounds (then only sonar news could tell). Also the length gap. usage: node exp/cand-stack11/kxking.js <eval dir> [...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const MAPNAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma', queen_of_spades: 'Queen Of Spades', schooltime: 'Schooltime', slithery_fight: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const tot = { kx: 0, longest: 0, inView: 0, seen20: 0, unseen20: 0, gap: [], lenMe: [], lenK: [], byMap: {} };
for (const dirArg of process.argv.slice(2)) {
  const dir = path.resolve(dirArg);
  for (const l of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean)) {
    const row = JSON.parse(l), [opp, map, side, seed] = row.key.split(':');
    const f = path.join(dir, 'games', `${opp}_${map}_${side}_${seed}`, 'game.replay'); if (!fs.existsSync(f)) continue;
    const mapName = MAPNAME[map.replace(/_(b|10)$/, '')] || map, us = side;
    const R = load(f);
    const lastSeen = new Map(); // "a:b" -> last round dragon a had b's head within Chebyshev 3
    let W = 0, H = 0;
    const cheb = (p, q) => { const dx = Math.abs(p.x - q.x), dy = Math.abs(p.y - q.y); return Math.max(Math.min(dx, W - dx), Math.min(dy, H - dy)); };
    const tdist = (p, q) => { const dx = Math.abs(p.x - q.x), dy = Math.abs(p.y - q.y); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
    const hooks = {
      turn(d, r, c) {
        W = c.W; H = c.H;
        if (d.team !== us) return;
        for (const o of c.drag.values()) if (o.team === us && o.id !== d.id && cheb(o.body[0], d.body[0]) <= 3) lastSeen.set(d.id + ':' + o.id, r);
      },
      indicator(e, r, c) {
        const d = c.drag.get(e.id); if (!d || d.team !== us) return;
        const h = (e.text || '').split('|')[0]; if (!/(^|\s)kx\d+(\s|$)/.test(h)) return;
        tot.kx++; const m = tot.byMap[mapName] || (tot.byMap[mapName] = { kx: 0, notLongest: 0 }); m.kx++;
        let k = null; for (const o of c.drag.values()) if (o.team === us && o.id !== d.id && o.body.length > d.body.length && (!k || o.body.length > k.body.length)) k = o;
        if (!k) { tot.longest++; return; }
        m.notLongest++;
        tot.gap.push(k.body.length - d.body.length); tot.lenMe.push(d.body.length); tot.lenK.push(k.body.length);
        // any longer ally in view now / seen within 20 rounds
        let inView = 0, seen20 = 0;
        for (const o of c.drag.values()) {
          if (o.team !== us || o.id === d.id || o.body.length <= d.body.length) continue;
          if (cheb(o.body[0], d.body[0]) <= 3) inView = 1;
          const ls = lastSeen.get(d.id + ':' + o.id); if (ls !== undefined && r - ls <= 20) seen20 = 1;
        }
        if (inView) tot.inView++; else if (seen20) tot.seen20++; else tot.unseen20++;
      },
    };
    perGame(R, { map: mapName }, hooks);
  }
}
const med = a => { if (!a.length) return '-'; const s = a.slice().sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
console.log(`kx turns ${tot.kx}: our longest ${tot.longest} (${Math.round(100 * tot.longest / tot.kx)}%); not longest ${tot.kx - tot.longest}: longer ally in view now ${tot.inView}, seen in view within 20 rounds ${tot.seen20}, not seen for 20+ rounds ${tot.unseen20}`);
console.log(`not-longest turns: our length median ${med(tot.lenMe)}, the longest's median ${med(tot.lenK)}, gap median ${med(tot.gap)}`);
for (const [m, o] of Object.entries(tot.byMap)) console.log(`  ${m}: kx ${o.kx}, not longest ${o.notLongest} (${Math.round(100 * o.notLongest / o.kx)}%)`);
