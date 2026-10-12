#!/usr/bin/env node
// cand-stack11 local safety: does kx push the king into dead ends? King-like turns = our dragon of length >= 8 with no longer own dragon,
// r >= 300, on a KX map (Schooltime, Slithery Fight, Trauma, Autarky), an enemy head within torus Manhattan 7 at its turn start (the kx
// situation from the replay; tag-independent, so stack10 compares). Per such turn: within 20 rounds the dragon made an escape split (the
// ledger's stub split: the parent keeps <= 3, the child gets >= 4), and its body (the dragon and descendants born later) was lost; its
// body's trapped deaths. One record per turn; also per dragon-episode (first such turn of a dragon). Split by the kx tag on that turn.
// usage: node exp/cand-stack11/deadend.js <eval dir>[+<eval dir>] [...]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const MAPNAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma', queen_of_spades: 'Queen Of Spades', schooltime: 'Schooltime', slithery_fight: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const KX = new Set(['Schooltime', 'Slithery Fight', 'Trauma', 'Autarky']);
for (const pool of process.argv.slice(2)) {
  const T = { all: { n: 0, esc: 0, lost: 0, trapLost: 0 }, kx: { n: 0, esc: 0, lost: 0, trapLost: 0 }, nokx: { n: 0, esc: 0, lost: 0, trapLost: 0 }, byMap: {}, games: 0, epi: { n: 0, esc: 0, lost: 0 } };
  for (const dirArg of pool.split('+')) {
    const dir = path.resolve(dirArg);
    for (const l of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean)) {
      const row = JSON.parse(l), [opp, map, side, seed] = row.key.split(':');
      const mapName = MAPNAME[map.replace(/_(b|10)$/, '')] || map; if (!KX.has(mapName)) continue;
      const f = path.join(dir, 'games', `${opp}_${map}_${side}_${seed}`, 'game.replay'); if (!fs.existsSync(f)) continue;
      const us = side, R = load(f); T.games++;
      let W = 0, H = 0; const td = (p, q) => { const dx = Math.abs(p.x - q.x), dy = Math.abs(p.y - q.y); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
      const turns = [], lab = new Map(), kids = new Map(), death = new Map(), stubSplit = new Map(); let rounds = 500;
      const hooks = {
        turn(d, r, c) {
          W = c.W; H = c.H;
          if (d.team !== us || r < 300 || d.body.length < 8) return;
          let longest = true, eD = 99; for (const o of c.drag.values()) { if (o.id === d.id) continue; if (o.team === us) { if (o.body.length > d.body.length) longest = false; } else eD = Math.min(eD, td(o.body[0], d.body[0])); }
          if (longest && eD <= 7) turns.push({ id: d.id, r });
        },
        indicator(e, r, c) { const d = c.drag.get(e.id); if (d && d.team === us) lab.set(e.id + ':' + r, /(^|\s)kx\d+(\s|$)/.test((e.text || '').split('|')[0])); },
        split(p, ch, e, r) { if (p.team !== us) return; if (!kids.has(p.id)) kids.set(p.id, []); kids.get(p.id).push([ch.id, r]); if (e.parentBody.length <= 3 && e.childBody.length >= 4) { if (!stubSplit.has(p.id)) stubSplit.set(p.id, []); stubSplit.get(p.id).push(r); } },
        death(d, rec, idx, other, r) { if (d.team === us) death.set(d.id, [r, rec.cause]); },
        end(n) { rounds = n; },
      };
      perGame(R, { map: mapName }, hooks);
      // body alive at t: the dragon or a descendant born by t is alive at t
      const alive = (id, t, born0) => { const st = [id]; while (st.length) { const x = st.pop(); const dz = death.get(x); if (!dz || dz[0] > t) return true; for (const [c, br] of kids.get(x) || []) if (br <= t && br >= born0) st.push(c); } return false; };
      const lastCause = (id, t, born0) => { let best = null; const st = [id]; while (st.length) { const x = st.pop(); const dz = death.get(x); if (dz && dz[0] <= t && (!best || dz[0] >= best[0])) best = dz; for (const [c, br] of kids.get(x) || []) if (br <= t && br >= born0) st.push(c); } return best ? best[1] : null; };
      const seenEp = new Set();
      for (const q of turns) {
        const t = Math.min(q.r + 20, rounds - 1), kxT = lab.get(q.id + ':' + q.r) === true;
        const esc = (stubSplit.get(q.id) || []).some(r => r > q.r && r <= q.r + 20) ? 1 : 0;
        const lost = alive(q.id, t, q.r) ? 0 : 1, trap = lost && lastCause(q.id, t, q.r) === 1 ? 1 : 0;
        for (const k of ['all', kxT ? 'kx' : 'nokx']) { T[k].n++; T[k].esc += esc; T[k].lost += lost; T[k].trapLost += trap; }
        const m = T.byMap[mapName] || (T.byMap[mapName] = { n: 0, esc: 0, lost: 0 }); m.n++; m.esc += esc; m.lost += lost;
        if (!seenEp.has(q.id)) { seenEp.add(q.id); T.epi.n++; T.epi.esc += esc; T.epi.lost += lost; }
      }
    }
  }
  const p = (a, b) => b ? Math.round(100 * a / b) + '%' : '-';
  console.log(`${pool}: KX-map games ${T.games}; king-like turns ${T.all.n}: escape split within 20 ${p(T.all.esc, T.all.n)} · body lost within 20 ${p(T.all.lost, T.all.n)} (trapped last ${p(T.all.trapLost, T.all.n)})`);
  console.log(`   kx-tagged ${T.kx.n}: esc ${p(T.kx.esc, T.kx.n)} · lost ${p(T.kx.lost, T.kx.n)} · untagged ${T.nokx.n}: esc ${p(T.nokx.esc, T.nokx.n)} · lost ${p(T.nokx.lost, T.nokx.n)}; first turn of each dragon ${T.epi.n}: esc ${p(T.epi.esc, T.epi.n)} · lost ${p(T.epi.lost, T.epi.n)}`);
  console.log('   by map: ' + Object.entries(T.byMap).map(([m, o]) => `${m} ${o.n} esc ${p(o.esc, o.n)} lost ${p(o.lost, o.n)}`).join(' | '));
}
