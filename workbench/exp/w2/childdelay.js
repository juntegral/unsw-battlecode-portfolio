#!/usr/bin/env node
// W2 design data (before pre-registration): for every child of our team on known maps, how many of its turns pass until
//   (a) it receives a sonar ping from an ally (any of our pings that ends on the child's body; a ping cast before the child's
//       turn in the same round is read that turn, one cast after it the next round),
//   (b) its head has moved >= D tiles (torus Chebyshev) from its birth head, D = 7 (a second, disjoint 7x7 window) and 12,
// and when v1.x recognised the map in it now (the first " map=" tag of the child: decided at birth or later).
// usage: node exp/w2/childdelay.js <replay> ...   (our side from the path: _A_ or _B_ before the seed)
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const files = process.argv.slice(2);
const turnsTo = { msg: [], d7: [], d12: [], tagBirth: 0, tagLater: 0, tagNone: 0, n: 0, msgBirth: 0, diedNoMsg: 0 };
const perMap = {};
for (const f of files) {
  const us = /_B_\d+\//.test(f) ? 'B' : 'A';
  const mapName = (/_(autarky|default|devil|portals|prisoners_dilemma|queen_of_spades|schooltime|slithery_fight|trauma|trophy|stronghold|arena|big_empty|Colosseum|default_small)_[AB]_/.exec(f) || [])[1] || '?';
  const R = load(f);
  // interleave synthetic indicator events after each ping so the hook sees the live board
  const ev = [];
  for (const e of R.events) { ev.push(e); if (e.type === 'sonarPing') ev.push({ type: 'dragonIndicator', id: -1, text: '', ping: e }); }
  const R2 = Object.assign({}, R, { events: ev });
  const kids = new Map();   // id -> {born, bornHead, turns, msgTurn, d7Turn, d12Turn, tag}
  let curTurnId = -1;
  perGame(R2, { map: mapName, variant: 'a' }, {
    split(p, ch, e, round, ctx) { if (ch.team === us) kids.set(ch.id, { born: round, h0: { ...ch.body[0] }, turns: 0, msgTurn: null, pend: false, d7: null, d12: null, tag: null }); },
    turn(d, round, ctx) {
      curTurnId = d.id;
      const k = kids.get(d.id); if (!k) return;
      k.turns++;
      if (k.pend && k.msgTurn === null) k.msgTurn = k.turns - 1;   // read at this turn (0 = first turn)
      const h = d.body[0], dist = ctx.cheb(h, k.h0);
      if (dist >= 7 && k.d7 === null) k.d7 = k.turns - 1;
      if (dist >= 12 && k.d12 === null) k.d12 = k.turns - 1;
    },
    indicator(e, round, ctx) {
      if (e.ping) {
        const p = e.ping; if (!/ally/i.test(p.hitKind || '')) return;
        const s = ctx.drag.get(p.senderId); if (!s || s.team !== us) return;
        const o = ctx.occ.get(ctx.key(p.end.x, p.end.y)); if (o === undefined) return;
        const k = kids.get(o); if (!k || k.msgTurn !== null) return;
        k.pend = true;
        return;
      }
      const k = kids.get(e.id); if (!k || k.tag !== null) return;
      const m = / map=(\S+)/.exec(e.text || ''); if (m) k.tag = { at: k.turns - 1, v: m[1] };
    },
  });
  for (const [id, k] of kids) {
    if (k.turns === 0) continue;
    turnsTo.n++;
    const pm = perMap[mapName] = perMap[mapName] || { n: 0, msg: [], d7: [], tagBirth: 0 };
    pm.n++;
    if (k.msgTurn !== null) { turnsTo.msg.push(k.msgTurn); pm.msg.push(k.msgTurn); if (k.msgTurn === 0) turnsTo.msgBirth++; } else { turnsTo.diedNoMsg++; pm.msg.push(Infinity); turnsTo.msg.push(Infinity); }
    turnsTo.d7.push(k.d7 === null ? Infinity : k.d7); pm.d7.push(k.d7 === null ? Infinity : k.d7);
    turnsTo.d12.push(k.d12 === null ? Infinity : k.d12);
    if (k.tag && k.tag.at === 0 && !/none|\?/.test(k.tag.v)) { turnsTo.tagBirth++; pm.tagBirth++; } else if (k.tag && !/none/.test(k.tag.v)) turnsTo.tagLater++; else turnsTo.tagNone++;
  }
}
const q = (a, p) => { const s = a.slice().sort((x, y) => x - y); return s.length ? s[Math.min(s.length - 1, Math.floor(p * s.length))] : '-'; };
const share = (a, t) => (100 * a.filter(x => x <= t).length / Math.max(1, a.length)).toFixed(0) + '%';
console.log(`children ${turnsTo.n}; map tag at birth (decided) ${turnsTo.tagBirth}, later ${turnsTo.tagLater}, none/? ${turnsTo.tagNone}`);
console.log(`(a) first ally ping: at birth ${share(turnsTo.msg, 0)}, <=2 turns ${share(turnsTo.msg, 2)}, <=5 ${share(turnsTo.msg, 5)}, <=10 ${share(turnsTo.msg, 10)}; median ${q(turnsTo.msg, .5)}, p90 ${q(turnsTo.msg, .9)}; never ${turnsTo.diedNoMsg}`);
console.log(`(b) head >= 7 from birth: <=5 turns ${share(turnsTo.d7, 5)}, <=10 ${share(turnsTo.d7, 10)}, <=20 ${share(turnsTo.d7, 20)}; median ${q(turnsTo.d7, .5)}, p90 ${q(turnsTo.d7, .9)}`);
console.log(`(b) head >= 12 from birth: <=10 ${share(turnsTo.d12, 10)}, <=20 ${share(turnsTo.d12, 20)}; median ${q(turnsTo.d12, .5)}, p90 ${q(turnsTo.d12, .9)}`);
for (const [m, pm] of Object.entries(perMap)) console.log(`  ${m.padEnd(18)} children ${String(pm.n).padStart(5)}  tag at birth ${share(Array(pm.tagBirth).fill(0).concat(Array(pm.n - pm.tagBirth).fill(1)), 0)}  ping<=0 ${share(pm.msg, 0)} <=2 ${share(pm.msg, 2)} <=5 ${share(pm.msg, 5)} median ${q(pm.msg, .5)} | d7 median ${q(pm.d7, .5)} p90 ${q(pm.d7, .9)}`);
