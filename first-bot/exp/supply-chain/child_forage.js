#!/usr/bin/env node
// Why do our split children not eat the spawns they are nearest to? Replays of our online sets (one process).
// For every piece (child born with length <= 3) of both sides, born r0-249, during its first 30 rounds:
//   claim = a natural spawn whose unique nearest head (static path over the map, bodies ignored, <= 12) is the piece.
//   Per claim: who ate it (the piece / its parent / another own piece / own mid / own big / the opponent / nobody within the
//   piece's window), the piece's moves while the claim was live (closer / same / farther by static path), and for our side
//   the piece's INDICATOR labels on those turns (F fountain goal, g gather goal, grab, tg/tgx threat gap, esc, TRADE, split
//   kinds, other).
//   allyNear: at some turn while the claim was live, another own head (seen, any length) was nearer to the spawn than the
//   piece (static path) — the situation where plan.cpp computeAttract() cuts the pearl's pull by CONTEST_ALLY_CLOSER.
// Per piece: turns with an F label in its first 30 rounds, whether it ate within 30 rounds, nearest own >= 8 at birth.
// usage (repository root): node exp/supply-chain/child_forage.js <set> [<set> ...] [--json out.json]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const X = require(path.join(ROOT, 'exp', 'territory-analysis', 'extract.js'));
const { parseInd } = require(path.join(ROOT, 'tools', 'mech_check.js'));
const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = tf.makeLoader(tf.viewerSource());
const argv = process.argv.slice(2);
const sets = argv.filter((a, i) => !a.startsWith('--') && argv[i - 1] !== '--json');
const R500 = new Set(['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma']);
const TAGCODE = { csplit: 'csplit', frag: 'frag', bsplit: 'bsp', split: 'split', escsplit: 'escape-split', escsplit2: 'esc-split', pocket: 'pocket' };
const agg = {}; // key side|kind|cls -> counters
const A = k => agg[k] || (agg[k] = { pieces: 0, ate30: 0, fTurns: 0, turns30: 0, piecesF: 0, ate30F: 0, piecesNoF: 0, ate30NoF: 0,
  nearBig: 0, ate30NearBig: 0, claims: 0, cSelf: 0, cParent: 0, cOwnPiece: 0, cOwnMid: 0, cOwnBig: 0, cEnemy: 0, cNone: 0,
  claimTurns: 0, closer: 0, same: 0, farther: 0, lab: {}, labNot: {}, allyNear: 0, allyNearSelf: 0, d0: [0, 0, 0, 0, 0], d0Self: [0, 0, 0, 0, 0],
  bigNearClaim: 0, bigNearClaimSelf: 0, fOnClaim: 0, fOnClaimSelf: 0, cases: [] });
const dBin = d => d <= 2 ? 0 : d <= 4 ? 1 : d <= 6 ? 2 : d <= 9 ? 3 : 4;

for (const set of sets) {
  const dir = path.join(ROOT, 'data', 'online', set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  for (const gm of idx.games) {
    const f = path.join(dir, 'M' + gm.gameId + '.replay'); if (!fs.existsSync(f)) continue;
    const R = load(f), G = X.geometry(R), W = G.W, H = G.H, N = G.N, us = String(gm.ourSide).toUpperCase(), kind = R500.has(gm.mapName) ? 'r500' : 'elim';
    const info = { map: gm.mapName }; if (gm.mapName === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
    const pc = new Map(), claims = [], shadows = [], lastInd = new Map(), known = new Set();
    if (R.match.map.initialTiles) R.match.map.initialTiles.forEach((v, i) => { if (v === 2) known.add(i); });
    const K = p => p.y * W + p.x;
    const man = (a, b) => { let dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); dx = Math.min(dx, W - dx); dy = Math.min(dy, H - dy); return dx + dy; };
    const D = new Int16Array(N), Q = new Int32Array(N);
    const bfs = (src, maxD) => { D.fill(-1); let qh = 0, qt = 0; Q[qt++] = src; D[src] = 0; while (qh < qt) { const t = Q[qh++]; if (D[t] >= maxD) continue; for (let j = 0; j < 4; j++) { const u = G.nb[t * 4 + j]; if (u < 0 || D[u] >= 0) continue; D[u] = D[t] + 1; Q[qt++] = u; } } };
    let lastR = -1, ctxRef = null;
    const hooks = {
      split(p, ch, e, r, c) {
        if (ch.body.length > 3 || r >= 250) return;
        let cls = 'top';
        if (p.team === us) { const li = lastInd.get(p.id); const t = li && li.r === r ? parseInd(li.text) : null; cls = t ? (TAGCODE[t.kind] || 'other') : 'unlabelled'; }
        let dBig = 99; for (const o of c.drag.values()) if (o.team === ch.team && o !== ch && o.body.length >= 8) dBig = Math.min(dBig, man(o.body[0], ch.body[0]));
        pc.set(ch.id, { id: ch.id, team: ch.team, parent: p.id, born: r, cls, ate30: 0, fTurns: 0, turns: 0, nearBig: dBig <= 5 ? 1 : 0, key: set + ':' + gm.gameId });
      },
      turn(d, r, c) {
        ctxRef = c;
        if (r !== lastR) {
          lastR = r;
          for (const [k, o] of c.pearls) {
            if (o !== -1 || known.has(k)) continue; known.add(k);
            // unique nearest head (static path <= 12)
            bfs(k, 12); let best = 99, who = []; for (const x of c.drag.values()) { const dd = D[K(x.body[0])]; if (dd < 0) continue; if (dd < best) { best = dd; who = [x]; } else if (dd === best) who.push(x); }
            if (who.length === 1 && who[0].body.length <= 4) {                 // shadowed: a sibling piece is the unique nearest head
              let eBest = 99; for (const x of c.drag.values()) if (x.team !== who[0].team) { const dd = D[K(x.body[0])]; if (dd >= 0 && dd < eBest) eBest = dd; }
              for (const x of c.drag.values()) {
                if (x === who[0] || x.team !== who[0].team) continue; const q2 = pc.get(x.id); if (!q2 || r > q2.born + 30) continue;
                const dd = D[K(x.body[0])]; if (dd < 0 || dd > 4 || dd > eBest) continue;
                shadows.push({ q: q2, k, r, d0: dd, prevD: dd, eaten: null, first: null, sib: who[0].id });
              }
            }
            if (who.length !== 1) continue;
            const q = pc.get(who[0].id); if (!q || r > q.born + 30) continue;
            let bigNear = 0; for (const x of c.drag.values()) if (x.team === q.team && x.body.length >= 8 && x !== who[0]) { const dd = D[K(x.body[0])]; if (dd >= 0 && dd <= best + 3) bigNear = 1; }
            claims.push({ q, k, r, d0: best, prevD: best, eaten: null, turns: 0, closer: 0, same: 0, farther: 0, lab: {}, allyNear: 0, bigNear, fOn: 0 });
          }
        }
        const q = pc.get(d.id); if (!q || r > q.born + 30) return;
        q.turns++;
        const sh = shadows.filter(x => x.q === q && !x.eaten && x.first === null);
        if (sh.length) { bfs(K(d.body[0]), 8); for (const x of sh) { const dd = D[x.k] < 0 ? 99 : D[x.k]; x.pending = dd; } q.pendingSh = sh; }
        const live = claims.filter(x => x.q === q && !x.eaten && r > x.r - 1);
        if (!live.length) return;
        bfs(K(d.body[0]), 16);
        for (const x of live) {
          const dd = D[x.k] < 0 ? 99 : D[x.k];
          x.turns++; if (dd < x.prevD) x.closer++; else if (dd === x.prevD) x.same++; else x.farther++; x.prevD = dd;
        }
        // another own head nearer to the claim than the piece (static path)
        for (const x of live) {
          bfs(x.k, 14); const mine = D[K(d.body[0])] < 0 ? 99 : D[K(d.body[0])];
          for (const o of c.drag.values()) { if (o.team !== d.team || o === d) continue; const dd = D[K(o.body[0])]; if (dd >= 0 && dd < mine) { x.allyNear = 1; break; } }
        }
        q.pendingLive = live;
      },
      indicator(e, r, c) {
        const d = c.drag.get(e.id); if (!d) return;
        if (d.team === us) lastInd.set(e.id, { r, text: e.text || '' });
        const q = pc.get(e.id); if (!q || q.team !== us || r > q.born + 30) return;
        const t = parseInd(e.text || '');
        let lab = t.kind;
        if (t.kind === 'move') { const s = []; if (t.fg) s.push('F'); if (t.goal) s.push('g'); if (t.grab) s.push('grab'); if (t.tg) s.push(t.tg); if (t.esc) s.push('esc'); if (t.trade) s.push('TRADE'); lab = s.length ? s.join('+') : 'move'; }
        if (t.kind === 'move' && t.fg) q.fTurns++;
        for (const x of (q.pendingLive || [])) { x.lab[lab] = (x.lab[lab] || 0) + 1; if (t.kind === 'move' && t.fg) x.fOn = 1; }
        q.pendingLive = null;
      },
      action(d, e, r, c) {
        const q = pc.get(d.id); if (!q || !q.pendingSh) return;
        bfs(K(d.body[0]), 8);
        for (const x of q.pendingSh) { const dd = D[x.k] < 0 ? 99 : D[x.k]; if (x.first === null) x.first = dd < x.pending ? 'closer' : dd === x.pending ? 'same' : 'farther'; }
        q.pendingSh = null;
      },
      eat(d, k, o, r, c) {
        if (o >= 0) return;
        known.delete(k);                                   // a later spawn on this tile is a new one
        const q = pc.get(d.id); if (q && r <= q.born + 30) q.ate30++;
        for (const x of shadows) if (x.k === k && !x.eaten && r >= x.r) x.eaten = d.id === x.q.id ? 'self' : d.team !== x.q.team ? 'enemy' : d.id === x.sib ? 'sibling' : d.body.length <= 4 ? 'ownPiece' : 'ownLonger';
        for (const x of claims) if (x.k === k && !x.eaten && r >= x.r) {
          const own = d.team === x.q.team;
          x.eaten = d.id === x.q.id ? 'self' : !own ? 'enemy' : d.id === x.q.parent ? 'parent' : d.body.length <= 4 ? 'ownPiece' : d.body.length <= 7 ? 'ownMid' : 'ownBig';
          x.eatR = r;
        }
      },
    };
    ML.perGame(R, info, hooks);
    for (const q of pc.values()) {
      const side = q.team === us ? 'ours' : 'X', a = A(side + '|' + kind + '|' + q.cls), b = A(side + '|all|' + q.cls);
      for (const z of [a, b]) {
        z.pieces++; if (q.ate30) z.ate30++; z.fTurns += q.fTurns; z.turns30 += q.turns;
        if (q.fTurns > 0) { z.piecesF++; if (q.ate30) z.ate30F++; } else { z.piecesNoF++; if (q.ate30) z.ate30NoF++; }
        if (q.nearBig) { z.nearBig++; if (q.ate30) z.ate30NearBig++; }
      }
    }
    for (const x of shadows) {
      const side = x.q.team === us ? 'ours' : 'X';
      for (const z of [A(side + '|' + kind + '|' + x.q.cls), A(side + '|all|' + x.q.cls)]) {
        z.sh = z.sh || { n: 0, closer: 0, same: 0, farther: 0, none: 0, self: 0, sibling: 0, ownPiece: 0, ownLonger: 0, enemy: 0, uneaten: 0, d: [0, 0, 0, 0, 0] };
        z.sh.n++; z.sh[x.first || 'none']++; z.sh[x.eaten || 'uneaten']++; z.sh.d[x.d0]++;
      }
    }
    for (const x of claims) {
      const side = x.q.team === us ? 'ours' : 'X';
      for (const z of [A(side + '|' + kind + '|' + x.q.cls), A(side + '|all|' + x.q.cls)]) {
        z.claims++;
        const e = x.eaten && x.eatR <= x.q.born + 30 ? x.eaten : x.eaten ? x.eaten : 'none';
        z['c' + { self: 'Self', parent: 'Parent', ownPiece: 'OwnPiece', ownMid: 'OwnMid', ownBig: 'OwnBig', enemy: 'Enemy', none: 'None' }[e]]++;
        z.claimTurns += x.turns; z.closer += x.closer; z.same += x.same; z.farther += x.farther;
        z.d0[dBin(x.d0)]++; if (e === 'self') z.d0Self[dBin(x.d0)]++;
        if (x.allyNear) { z.allyNear++; if (e === 'self') z.allyNearSelf++; }
        if (x.bigNear) { z.bigNearClaim++; if (e === 'self') z.bigNearClaimSelf++; }
        if (x.fOn) { z.fOnClaim++; if (e === 'self') z.fOnClaimSelf++; }
        const L = e === 'self' ? z.lab : z.labNot; for (const [l, n] of Object.entries(x.lab)) L[l] = (L[l] || 0) + n;
        if (e !== 'self' && z.cases.length < 400) z.cases.push({ key: x.q.key, id: x.q.id, born: x.q.born, spawnR: x.r, tile: [x.k % W, (x.k / W) | 0], d0: x.d0, eaten: e, eatR: x.eatR || null, closer: x.closer, farther: x.farther, same: x.same, lab: x.lab, allyNear: x.allyNear });
      }
    }
  }
}
const pct = (a, b) => b ? Math.round(100 * a / b) + '%' : '–';
const lines = [];
for (const [k, z] of Object.entries(agg).sort()) {
  if (!k.includes('|all|') || z.pieces < 20) continue;
  lines.push(`${k}: pieces ${z.pieces}, ate within 30 ${pct(z.ate30, z.pieces)}; with F turns ${z.piecesF} (${pct(z.ate30F, z.piecesF)} ate) / no F ${z.piecesNoF} (${pct(z.ate30NoF, z.piecesNoF)} ate); F share of first-30 turns ${pct(z.fTurns, z.turns30)}; born within 5 of own >=8: ${z.nearBig} (${pct(z.ate30NearBig, z.nearBig)} ate)`);
  lines.push(`  claims ${z.claims}: self ${pct(z.cSelf, z.claims)}, parent ${pct(z.cParent, z.claims)}, own piece ${pct(z.cOwnPiece, z.claims)}, own mid ${pct(z.cOwnMid, z.claims)}, own big ${pct(z.cOwnBig, z.claims)}, enemy ${pct(z.cEnemy, z.claims)}, nobody ${pct(z.cNone, z.claims)}`);
  lines.push(`  moves while a claim was live (piece-turns ${z.claimTurns}): closer ${pct(z.closer, z.claimTurns)}, same ${pct(z.same, z.claimTurns)}, farther ${pct(z.farther, z.claimTurns)}`);
  lines.push(`  claim distance at spawn <=2/3-4/5-6/7-9/10+: ${z.d0.join('/')}; eaten by self ${z.d0.map((n, i) => pct(z.d0Self[i], n)).join('/')}`);
  lines.push(`  an own head became nearer to the claim: ${pct(z.allyNear, z.claims)} (self ate ${pct(z.allyNearSelf, z.allyNear)}; others ${pct(z.cSelf - z.allyNearSelf, z.claims - z.allyNear)}); own >=8 within +3 of the claim at spawn: ${pct(z.bigNearClaim, z.claims)} (self ate ${pct(z.bigNearClaimSelf, z.bigNearClaim)}); F label on a claim turn: ${pct(z.fOnClaim, z.claims)} (self ate ${pct(z.fOnClaimSelf, z.fOnClaim)})`);
  if (z.sh) lines.push(`  shadowed spawns (a sibling piece uniquely nearest, this piece within 4 and not farther than any enemy head): ${z.sh.n} (${(z.sh.n / z.pieces).toFixed(2)} per piece); first move closer ${pct(z.sh.closer, z.sh.n)} / same ${pct(z.sh.same, z.sh.n)} / farther ${pct(z.sh.farther, z.sh.n)} / no turn ${pct(z.sh.none, z.sh.n)}; eaten by this piece ${pct(z.sh.self, z.sh.n)}, the sibling ${pct(z.sh.sibling, z.sh.n)}, another own piece ${pct(z.sh.ownPiece, z.sh.n)}, own longer ${pct(z.sh.ownLonger, z.sh.n)}, enemy ${pct(z.sh.enemy, z.sh.n)}, nobody ${pct(z.sh.uneaten, z.sh.n)}`);
  const top = o => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([l, n]) => `${l} ${n}`).join(', ');
  if (Object.keys(z.lab).length) { lines.push(`  labels on claim turns, claims the piece ate: ${top(z.lab)}`); lines.push(`  labels on claim turns, claims it did not eat: ${top(z.labNot)}`); }
}
console.log(lines.join('\n'));
const jo = argv.indexOf('--json'); if (jo >= 0) fs.writeFileSync(path.resolve(ROOT, argv[jo + 1]), JSON.stringify(agg));
