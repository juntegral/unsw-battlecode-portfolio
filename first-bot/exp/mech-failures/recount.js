'use strict';
// Independent recount for exp/mech-failures (a second method for the key numbers of mech-merge2-failures.md).
// It does not use tools/mass_ledger.js or tools/mech_check.js. Everything comes straight from the replay events:
//   bodies    from dragonUpdate head/tail (push the new head, drop tail segments until the reported tail), dragonSplit
//             bodies and the initial map; lengths are body lengths,
//   deaths    dragonDeath reason; a head-on victim is a dragon that dies with reason H while another dragon is moving,
//             and the mover (turnStart id) is its killer; the killer's steps = its dragonUpdate count in that action + 1,
//   pearls    drops = hasPearl tileChanges right after a death; eats = pearl-removing tileChanges during a turn (eater =
//             the dragon whose turn it is),
//   labels    own regexes on the dragonIndicator text.
// Definitions follow the primary analysis where possible; distances here are torus Manhattan (no kelp or portals).
// Called by collect.js on the same parsed replay: recount(R, task) -> one object per game.
const DIRS = { N: [0, -1], E: [1, 0], S: [0, 1], W: [-1, 0] };

function recount(R, task) {
  const online = task.mode === 'online', us = online ? task.us : null;
  const M = R.match.map, W = M.width, H = M.height;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H, key = (x, y) => y * W + x;
  const td = (a, b) => { const dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
  const cheb = (a, b) => { const dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); return Math.max(Math.min(dx, W - dx), Math.min(dy, H - dy)); };
  // portal edges: an edge is "N of (x,y)" or "W of (x,y)"
  const pedge = new Set();
  const canonEdge = e => e.side === 'S' ? `${e.x},${wy(e.y + 1)},N` : e.side === 'E' ? `${wx(e.x + 1)},${e.y},W` : `${e.x},${e.y},${e.side}`;
  for (const pr of M.portals || []) for (const e of pr) pedge.add(canonEdge(e));
  const stepEdge = (p, d) => d === 'N' ? `${p.x},${p.y},N` : d === 'S' ? `${p.x},${wy(p.y + 1)},N` : d === 'W' ? `${p.x},${p.y},W` : `${wx(p.x + 1)},${p.y},W`;

  const D = new Map(); // id -> {id, team, body:[{x,y}], born, parent, deathR, reason, killer, deathLen}
  for (const d0 of M.initialDragons) D.set(d0.id, { id: d0.id, team: d0.team, body: d0.body.map(s => ({ x: s.x, y: s.y })), born: 0, parent: -1, deathR: null });
  const alive = () => [...D.values()].filter(d => d.deathR === null);
  const pearls = new Map(); // tile -> origin death index (-1 natural)
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearls.set(i, -1);
  const deaths = []; // {id, team, r, reason, killer, len, eats:[team...], partner}
  const labels = new Map(); // 'id:r' -> text
  let round = -1, cur = -1, act = null, lastDeath = -1, dropMode = false;
  const acts = new Map(); // 'id:r' -> {steps, exec, eats, died, headB, preHeads (enemy heads at turn start), teamLens}
  const expo = {}; // side|maptype|phase -> {turns, e3, a3}
  const R500 = new Set(['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma']);
  const sideOf = tm => online ? (tm === us ? 'us' : 'them') : tm;
  const splitsOf = new Map(); // 'parent:r' -> child id
  const turnCtx = new Map(); // 'id:r' -> snapshot of heads at the dragon's turn start: [id, team, len, x, y, born]

  for (const e of R.events) {
    if (dropMode && !(e.type === 'tileChange' && e.hasPearl)) dropMode = false;
    switch (e.type) {
      case 'roundStart': round = e.round; break;
      case 'turnStart': {
        cur = e.id; const d = D.get(cur); if (!d || d.deathR !== null) { act = null; break; }
        act = { id: cur, r: round, steps: 0, exec: 0, eats: 0, died: false, headB: { ...d.body[0] }, fatalHead: { ...d.body[0] }, dirs: null, lenB: d.body.length };
        acts.set(cur + ':' + round, act);
        // heads at this turn start (for our dragons, and for the exposure count of long dragons)
        const L = d.body.length;
        if ((online && d.team === us) || L >= 6) {
          const snap = []; for (const o of D.values()) if (o.deathR === null && o !== d) snap.push([o.id, o.team, o.body.length, o.body[0].x, o.body[0].y, o.born]);
          turnCtx.set(cur + ':' + round, snap);
          if (L >= 6) {
            let e3 = 0, a3 = 0;
            for (const s of snap) { const t = td({ x: s[3], y: s[4] }, d.body[0]); if (s[1] !== d.team) { if (s[2] <= 4 && s[2] < L && t <= 3) e3 = 1; } else if (t <= 3) a3 = 1; }
            const k = sideOf(d.team) + '|' + (R500.has(task.map) ? 'r500' : 'elim') + '|' + (round < 250 ? 'r0-249' : 'r250+');
            const o = expo[k] || (expo[k] = { turns: 0, e3: 0, a3: 0 }); o.turns++; o.e3 += e3; o.a3 += a3;
          }
        }
        break;
      }
      case 'dragonIndicator': labels.set(e.id + ':' + round, e.text); break;
      case 'dragonAction': if (act && e.id === act.id && e.action && e.action.kind === 'move') { act.steps = e.action.steps.length; act.dirs = e.action.steps; } break;
      case 'dragonUpdate': {
        const d = D.get(e.id); if (!d || d.deathR !== null) break;
        if (act && e.id === act.id) { act.exec++; act.fatalHead = { x: e.head.x, y: e.head.y }; }
        const b = d.body;
        if (b[0].x !== e.head.x || b[0].y !== e.head.y) b.unshift({ x: e.head.x, y: e.head.y });
        while (b.length > 1 && (b[b.length - 1].x !== e.tail.x || b[b.length - 1].y !== e.tail.y)) b.pop();
        break;
      }
      case 'dragonSplit': {
        const p = D.get(e.parentId); if (!p) break;
        p.body = e.parentBody.map(s => ({ x: s.x, y: s.y }));
        D.set(e.childId, { id: e.childId, team: e.team, body: e.childBody.map(s => ({ x: s.x, y: s.y })), born: round, parent: e.parentId, deathR: null });
        splitsOf.set(e.parentId + ':' + round, e.childId);
        break;
      }
      case 'dragonDeath': {
        const d = D.get(e.id); if (!d || d.deathR !== null) break;
        const mover = e.id === cur;
        const z = { idx: deaths.length, id: d.id, team: d.team, r: round, reason: e.reason, len: d.body.length, killer: null, eats: [], mover };
        if (e.reason === 'H' && !mover) { const k = D.get(cur); if (k) z.killer = { id: k.id, team: k.team, lenB: act && act.id === k.id ? act.lenB : null, steps: act && act.id === k.id ? act.exec + 1 : null }; }
        if (mover && act) { act.died = true; act.deathReason = e.reason; }
        d.deathR = round; d.deathIdx = z.idx;
        deaths.push(z); lastDeath = z.idx; dropMode = true;
        break;
      }
      case 'tileChange': {
        const k = key(e.tile.x, e.tile.y);
        if (e.hasPearl) { pearls.set(k, dropMode ? lastDeath : -1); }
        else if (pearls.has(k)) {
          const o = pearls.get(k); pearls.delete(k);
          const eater = D.get(cur);
          if (act && eater && act.id === cur) act.eats++;
          if (o >= 0 && eater) deaths[o].eats.push(eater.team);
        }
        break;
      }
    }
  }
  const rounds = round + 1;
  const deathR = id => { const d = D.get(id); return d && d.deathR !== null ? d.deathR : 1e9; };
  const kids = new Map(); for (const d of D.values()) if (d.parent >= 0) { if (!kids.has(d.parent)) kids.set(d.parent, []); kids.get(d.parent).push(d.id); }
  const famAliveAt = (root, t) => { t = Math.min(t, rounds - 1); const st = [root]; while (st.length) { const id = st.pop(); const d = D.get(id); if (!d || d.born > t) continue; if (deathR(id) > t) return true; for (const c of kids.get(id) || []) st.push(c); } return false; };
  const out = { online, expo, heads: {}, selfNoHit: {}, children: {} };

  // ---- head-on victims: pearl flows of both bodies (partner = the mover's own death in the same turn)
  for (const z of deaths) {
    if (z.reason !== 'H' || z.mover || !z.killer || z.killer.team === z.team) continue; // enemy rams only
    const m = deaths.find(q => q.r === z.r && q.id === z.killer.id);
    const eats = z.eats.concat(m ? m.eats : []);
    const s = sideOf(z.team), o = out.heads[s] || (out.heads[s] = { n: 0, vEat: 0, kEat: 0, longVictim: 0 });
    o.n++; o.vEat += eats.filter(t => t === z.team).length; o.kEat += eats.filter(t => t !== z.team).length;
    if (z.len >= 6 && (z.killer.lenB || 99) <= 4) o.longVictim++;
  }
  // ---- self-inflicted deaths that hit no other dragon (reasons S, W, A), from round 250
  for (const z of deaths) {
    if (!['S', 'W', 'A'].includes(z.reason) || z.r < 250) continue;
    const s = sideOf(z.team), o = out.selfNoHit[s] || (out.selfNoHit[s] = { n: 0, drops: 0, own: 0, enemy: 0 });
    o.n++; o.drops += Math.ceil(z.len / 2); o.own += z.eats.filter(t => t === z.team).length; o.enemy += z.eats.filter(t => t !== z.team).length;
  }
  // ---- split children of length <= 3: dead within 30 rounds
  for (const d of D.values()) {
    if (d.parent < 0) continue;
    // length at birth is not kept after moves; use the split event record: children born <= 3 long
  }
  // (children need the birth length: recompute from dragonSplit events)
  for (const e of R.events) if (e.type === 'dragonSplit' && e.childBody.length <= 3) {
    const c = D.get(e.childId); if (!c) continue;
    const s = sideOf(e.team), o = out.children[s] || (out.children[s] = { n: 0, dead30: 0 });
    o.n++; if (deathR(e.childId) <= c.born + 30) o.dead30++;
  }

  if (online) {
    const M2 = { esc: { n: 0, ex: 0, fail: 0, cls: {} }, sprintEsc: { n: 0, ex: 0, fail: 0, cls: {} }, ramsLong: { n: 0, steps: {} }, feed: { n: 0, famEnd: 0 },
      trade: { n: 0, ex: 0, us: 0, them: 0 }, split: { n: 0, alive30: 0 }, portalStepDeaths: 0 };
    for (const [k, a] of acts) {
      const [idS] = k.split(':'); const id = +idS; const d = D.get(id); if (!d || d.team !== us) continue;
      const text = labels.get(id + ':' + a.r) || '';
      const mv = /^([NESW]+) v\S+ d\d+ L\d+(.*)$/.exec(text);
      // portal-step death: the fatal step crossed a portal edge
      if (a.died && a.dirs && a.exec < a.dirs.length && pedge.has(stepEdge(a.fatalHead, a.dirs[a.exec]))) M2.portalStepDeaths++;
      if (mv) {
        const tags = mv[2].split('|')[0];
        const isEsc = / esc\b/.test(tags), isTrade = / TRADE\b/.test(tags);
        let kind = null;
        if (isEsc) kind = 'esc';
        else if (!isTrade && mv[1].length >= 2 && a.eats === 0) {
          const snap = turnCtx.get(k) || []; let eD = 99; for (const s of snap) if (s[1] !== us) eD = Math.min(eD, td({ x: s[3], y: s[4] }, a.headB));
          if (eD <= 4) kind = 'sprintEsc';
        }
        if (kind) {
          const o = M2[kind]; o.n++;
          if (a.exec >= 2 && !a.died) {
            o.ex++;
            if (!famAliveAt(id, a.r + 10)) {
              o.fail++;
              const z = deaths.find(q => q.id === id);
              let c = 'family only';
              if (z && z.r <= a.r + 10) {
                const lt = labels.get(id + ':' + z.r) || '';
                if (/TRADE|last-trade/.test(lt)) c = 'our own TRADE';
                else if (z.reason === 'H' && !z.mover && z.killer) {
                  const snap = turnCtx.get(k) || [];
                  const kr = snap.find(s => s[0] === z.killer.id);
                  const kd = D.get(z.killer.id);
                  const shorter = snap.filter(s => s[1] !== us && s[2] < a.lenB).sort((p, q) => td({ x: p[3], y: p[4] }, a.headB) - td({ x: q[3], y: q[4] }, a.headB))[0];
                  if (kd && kd.born > a.r) c = 'rammed: child born after the escape';
                  else if (shorter && shorter[0] === z.killer.id) c = 'rammed: the head we escaped from';
                  else if (kr && cheb({ x: kr[3], y: kr[4] }, a.headB) <= 3) c = 'rammed: another head in view';
                  else c = 'rammed: a head outside the 7x7 view';
                } else c = 'other death ' + z.reason;
              }
              o.cls[c] = (o.cls[c] || 0) + 1;
            }
          }
        }
        if (isTrade) {
          M2.trade.n++;
          if (a.died && a.deathReason === 'H') {
            M2.trade.ex++;
            const z = deaths.find(q => q.id === id && q.r === a.r);
            const pv = deaths.filter(q => q.r === a.r && q.reason === 'H' && !q.mover && q.killer && q.killer.id === id);
            const eats = (z ? z.eats : []).concat(...pv.map(q => q.eats));
            M2.trade.us += eats.filter(t => t === us).length; M2.trade.them += eats.filter(t => t !== us).length;
          }
        }
      }
      let m;
      if ((m = /^feed #(\d+)/.exec(text)) && !/ conv/.test(text)) { M2.feed.n++; const t = +m[1]; const st = [t]; let aliveEnd = false; while (st.length) { const x = st.pop(); if (deathR(x) === 1e9) { aliveEnd = true; break; } for (const c of kids.get(x) || []) st.push(c); } if (aliveEnd) M2.feed.famEnd++; }
      if (/^split\d+ u\d+ L\d+/.test(text)) { const ch = splitsOf.get(id + ':' + a.r); if (ch !== undefined) { M2.split.n++; if (deathR(ch) > Math.min(a.r + 30, rounds - 1)) M2.split.alive30++; } }
    }
    for (const z of deaths) {
      if (z.team !== us || z.reason !== 'H' || z.mover || !z.killer || z.killer.team === us || z.len < 6) continue;
      M2.ramsLong.n++; const s = 'steps' + z.killer.steps; M2.ramsLong.steps[s] = (M2.ramsLong.steps[s] || 0) + 1;
    }
    out.mech = M2;
  }
  out.rounds = rounds;
  return out;
}
module.exports = { recount };
