#!/usr/bin/env node
// Conversion chain study (backlog #20): where does sacrificed mass go, and does it reach the final king?
// Written for research/observations/conversion-chain.md (2026-09-30). Replays only; no games, no network.
//
// usage (repository root):
//   node exp/conv-chain/chain.js extract top [--jobs 4] [--limit N]      500-round maps of data/top (every game in index.jsonl)
//   node exp/conv-chain/chain.js extract online <set> [<set> ...] [--jobs 4]
//   node exp/conv-chain/chain.js extract local <exp folder> [--jobs 4]   local eval folder (rows.jsonl + games/)
//     One JSON line per game in .cache/conv-chain/<name>.jsonl (top.jsonl, online-<set>.jsonl, local-<label>.jsonl);
//     games already there are skipped.
//
// Reconstruction: tools/mass_ledger.js perGame with hooks (every pearl's source death and eater, splits, deaths by cause).
// Definitions (per team):
//   Final king = the team's longest dragon at the end (ties: lowest id, as the ledger). Line = the final king followed back
//     through its parents. Line member i owns the window from its birth to the split that created member i+1 (the final king:
//     to the end). A pearl eaten by a line member inside its window is "to the line" (the ledger's lineage convention:
//     final = L_t + line eats - sprint cost - bodies split off the line).
//   Drop classes of an own-team death's pearls (one class per pearl):
//     K0 eaten by the final king itself · KA eaten by an ancestor inside its window · E eaten by the enemy · U never eaten
//     other own eaters by the fate of their family after the eating (the eater and every descendant born later: a split hands
//     mass to the child): M some member alive at the end (not the line) · S2K all died and >= 1 of their drops was eaten by the
//     line · S all died, none to the line, the last death a sacrifice · X all died, none to the line, the last another cause.
//     suffix s / m: eater length before the eating move < 8 / >= 8.
//   eff = K0 + KA + sum over pearls eaten off the line of (family drops eaten by the line / family mass), family mass = death
//     lengths + end lengths (one mass unit becomes that much line mass; one level only).
//   Sacrifice = ledger cause 'sac' (self-inflicted with a free neighbour). Our labelled conversions: "feed #<id> d<d> L<l>[ conv]"
//     (feed, conv), gathering = move label token g<d> (a non-king heading for the king it knows).
//   King choice snapshots at the first turn of rounds 300, 350, 400, 450: every own dragon with length, head, eD (torus
//     Manhattan to the nearest enemy head), aM8 (length of other own dragons whose head is within 8), cen (length-weighted mean
//     distance to the other own heads), fr (free tiles within 4 steps, bodies block), own (head in own territory), eM8 (enemy
//     length whose head is within 8).
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..'), TOP = path.join(ROOT, 'data', 'top'), ONLINE = path.join(ROOT, 'data', 'online');
const CACHE = path.join(ROOT, '.cache', 'conv-chain');
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const ELIM = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default'];
const MAPNAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma',
  queen_of_spades: 'Queen Of Spades', schooltime: 'Schooltime', slithery_fight: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const kindOf = m => ELIM.includes(m) ? 'elim' : R500.includes(m) ? 'r500' : 'other';
const CPS = [300, 350, 400, 450];
const CLS = ['K0', 'KA', 'E', 'U', 'Ms', 'Mm', 'S2Ks', 'S2Km', 'Ss', 'Sm', 'Xs', 'Xm'];
const CI = Object.fromEntries(CLS.map((k, i) => [k, i]));
const lenClass = L => L <= 2 ? '2' : L === 3 ? '3' : L === 4 ? '4' : L <= 7 ? '5-7' : L <= 14 ? '8-14' : '15+';
const phase = r => r < 250 ? 'p0' : r < 300 ? 'p250' : 'p' + Math.floor(r / 25) * 25; // 25-round bins from r300
const DIRS = ['N', 'E', 'S', 'W'];

function parseLabel(s) {
  if (!s) return null;
  let m;
  if ((m = /^feed #(\d+) d(\d+) L(\d+)( conv)?/.exec(s))) return { k: m[4] ? 'conv' : 'feed', target: +m[1], dist: +m[2] };
  if ((m = /^feed #(\d+) d(\d+) L(\d+) (\S+)/.exec(s))) return { k: 'feed-' + m[4], target: +m[1], dist: +m[2] };
  const g = /\sg(\d+)(?=\s|\||$)/.exec(s);
  const kk = /\sK(\d+)(?=\s|\||$)/.exec(s);
  const tags = [];
  for (const t of (s.split('|')[0] || '').split(/\s+/)) if (/^(kc\d*|kc[a-z]*|kl\d*|kq\d*|k2\S*|kx\S*)$/.test(t)) tags.push(t);
  return { k: 'move', g: g ? +g[1] : null, K: kk ? +kk[1] : null, tags };
}

// ---------------------------------------------------------------------------------------------------------------
function analyse(R, task, perGame) {
  const nInit = R.match.map.initialDragons.length;
  const info = { map: task.map };
  if (task.map === 'Prisoners Dilemma') info.variant = nInit === 10 ? 'PD10' : 'PD6';
  let ev = 0;
  const bornEv = new Map();              // dragon id -> hook counter at birth (initial dragons: -1)
  for (const d0 of R.match.map.initialDragons) bornEv.set(d0.id, -1);
  const eats = [];                       // [deathIdx, eaterId, eaterTeam, ev, round, lenBefore, kingNow]
  const deathOf = new Map();             // dragon id -> { idx, r, cause, len, team, ev, nearIds }
  const dinfo = [];                      // death idx -> { id, team, r, cause, len, drops, ev, nearIds }
  const labels = new Map();              // our dragon id -> label text of this turn
  const pend = new Map();                // our dragon id -> labelled conversion made this action
  const convs = [];                      // our feed/conv records
  const gath = new Map();                // our gathering episodes by dragon id
  const tagTurns = {};                   // our extra move tags (new mechanisms) -> turns
  const snaps = {};                      // cp -> { ev, team -> [dragon rows] }
  let cpi = 0, finalIds = null;
  const us = task.us || null;
  const hooks = {
    turn(d, r, c) {
      ev++;
      while (cpi < CPS.length && r >= CPS[cpi]) {
        const t = CPS[cpi++];
        if (r !== t) continue;          // the game ended before, or a round without turns
        const rows = { A: [], B: [] };
        for (const x of c.drag.values()) {
          const h = x.body[0];
          let eD = 99, eM8 = 0, aM8 = 0, wS = 0, wN = 0;
          for (const o of c.drag.values()) {
            if (o === x) continue;
            const dd = c.tdist(o.body[0], h);
            if (o.team !== x.team) { if (dd < eD) eD = dd; if (dd <= 8) eM8 += o.body.length; }
            else { if (dd <= 8) aM8 += o.body.length; wS += dd * o.body.length; wN += o.body.length; }
          }
          // free tiles within 4 steps (bodies block)
          const seen = new Set([c.key(h.x, h.y)]); let fr = 0, front = [h];
          for (let s = 0; s < 4 && front.length; s++) {
            const nx = [];
            for (const p of front) for (const dir of DIRS) {
              const u = c.across(p.x, p.y, dir); if (!u) continue; const k = c.key(u.x, u.y);
              if (seen.has(k) || c.occ.has(k)) continue; seen.add(k); fr++; nx.push(u);
            }
            front = nx;
          }
          const own = c.terr[c.key(h.x, h.y)] === (x.team === 'A' ? 1 : 2) ? 1 : 0;
          rows[x.team].push([x.id, x.body.length, eD, aM8, wN ? +(wS / wN).toFixed(1) : -1, fr, own, eM8, h.x, h.y]);
        }
        snaps[t] = { ev, rows };
      }
    },
    indicator(e, r, c) { if (!us) return; const d = c.drag.get(e.id); if (d && d.team === us) labels.set(e.id, e.text || ''); },
    action(d, e, r, c, before) {
      ev++;
      if (!us || d.team !== us) return;
      const text = labels.get(d.id); labels.delete(d.id);
      const t = parseLabel(text);
      if (!t) return;
      if (t.k === 'move') {
        if (t.g !== null) { let q = gath.get(d.id); if (!q) gath.set(d.id, q = { id: d.id, r0: r, ev0: ev, L0: before.length, d0: t.g, dMin: t.g, r1: r, turns: 0 }); q.dMin = Math.min(q.dMin, t.g); q.r1 = r; q.turns++; }
        for (const x of t.tags) tagTurns[x] = (tagTurns[x] || 0) + 1;
        return;
      }
      const rec = { k: t.k, r, id: d.id, L: before.length, target: t.target, dist: t.dist, idx: -1, text };
      // the target's state now (it may be out of our knowledge; the replay knows)
      const T = c.drag.get(t.target);
      rec.tLen = T ? T.body.length : 0;
      let rank = 1, longest = 0; for (const o of c.drag.values()) if (o.team === d.team && o !== d) { longest = Math.max(longest, o.body.length); if (T && o !== T && (o.body.length > T.body.length || (o.body.length === T.body.length && o.id < T.id))) rank++; }
      rec.tRank = T ? rank : 0; rec.teamLongest = longest;
      rec.tDist = T ? c.tdist(T.body[0], d.body[0]) : 99;
      rec.ev = ev;
      pend.set(d.id, rec); convs.push(rec);
    },
    eat(d, tile, o, r, c) {
      ev++;
      if (o < 0) return;
      eats.push([o, d.id, d.team, ev, r, d.body.length, c.isKingNow(d) ? 1 : 0]);
    },
    split(p, ch, e, r, c) { ev++; bornEv.set(ch.id, ev); },
    death(d, rec, idx, other, r, c) {
      ev++;
      const near = [];
      for (const o of c.drag.values()) if (o !== d && o.team === d.team && c.tdist(o.body[0], d.body[0]) <= 3) near.push(o.id);
      const x = { id: d.id, team: d.team, r, cause: rec.cause, len: rec.len, drops: rec.drops, ev, near };
      dinfo[idx] = x; deathOf.set(d.id, idx);
      const p = pend.get(d.id); if (p && p.r === r) p.idx = idx;
      pend.delete(d.id);
    },
    end(rounds, c) {
      finalIds = { A: new Map(), B: new Map() };
      for (const d of c.drag.values()) finalIds[d.team].set(d.id, d.body.length);
    },
  };
  const g = perGame(R, info, hooks);
  const parent = new Map();
  for (const d0 of R.match.map.initialDragons) parent.set(d0.id, -1);
  for (const e of R.events) if (e.type === 'dragonSplit') parent.set(e.childId, e.parentId);
  const kids = new Map(); for (const [c0, p0] of parent) if (p0 >= 0) { if (!kids.has(p0)) kids.set(p0, []); kids.get(p0).push(c0); }
  const out = { key: task.key, src: task.src, set: task.set || null, map: task.map, kind: kindOf(task.map), variant: info.variant || null,
    us, opp: task.opp || null, winner: g.winner ? String(g.winner).toUpperCase() : null, rounds: g.rounds, endReason: g.endReason, chk: g.chk,
    teamA: task.teamA || null, teamB: task.teamB || null, eloA: task.eloA || null, eloB: task.eloB || null };
  for (const tm of ['A', 'B']) {
    if (us && tm !== us && task.src !== 'top') { /* keep both sides: the opponent side is an elite reference */ }
    // final king and its line
    let kid = -1, kl = 0; for (const [id, L] of finalIds[tm]) if (L > kl || (L === kl && id < kid)) { kid = id; kl = L; }
    const line = []; for (let x = kid; x !== undefined && x !== -1; x = parent.get(x)) line.push(x);
    line.reverse();
    const win = new Map(); // line id -> [from, to)
    for (let i = 0; i < line.length; i++) win.set(line[i], [bornEv.get(line[i]), i + 1 < line.length ? bornEv.get(line[i + 1]) : Infinity]);
    const onLine = (id, e) => { const w = win.get(id); return w ? e > w[0] && e < w[1] : false; };
    const lineAt = e => { for (const id of line) if (onLine(id, e)) return id; return -1; };
    // per death: drops to the line
    const toLine = new Map();
    for (const q of eats) if (q[2] === tm && dinfo[q[0]] && dinfo[q[0]].team === tm && onLine(q[1], q[3])) toLine.set(q[0], (toLine.get(q[0]) || 0) + 1);
    // family of X after hook counter e: X and every descendant born after e (a split hands mass to the child; the corridor
    // loop and the elite's split u-turn keep a body alive through generations). Fate of that mass: any member alive at the end,
    // the members' death drops eaten by the line, the members' mass (death lengths + end lengths).
    const toLineAny = new Map();
    for (const q of eats) if (q[2] === tm && onLine(q[1], q[3])) toLineAny.set(q[0], (toLineAny.get(q[0]) || 0) + 1);
    const famMemo = new Map();
    const family = (id, e) => {
      const mk = id + ':' + e; if (famMemo.has(mk)) return famMemo.get(mk);
      const r = { alive: 0, aliveLen: 0, toLine: 0, mass: 0, lastCause: -1, lastR: -1, n: 0, line: 0 };
      const st = [id];
      while (st.length) {
        const x = st.pop(); r.n++;
        if (win.has(x) && x !== id) r.line = 1;
        if (finalIds[tm].has(x)) { r.alive = 1; r.aliveLen += finalIds[tm].get(x); r.mass += finalIds[tm].get(x); }
        const di = deathOf.get(x);
        if (di !== undefined) { const dz = dinfo[di]; r.mass += dz.len; r.toLine += toLineAny.get(di) || 0; if (dz.r > r.lastR) { r.lastR = dz.r; r.lastCause = dz.cause; } }
        for (const c of kids.get(x) || []) if (bornEv.get(c) > e) st.push(c);
      }
      famMemo.set(mk, r); return r;
    };
    const fateCls = (id, e, len) => { // an own eater not on the line at e
      const s = len >= 8 ? 'm' : 's', f = family(id, e);
      if (f.alive) return 'M' + s;
      if (f.toLine > 0) return 'S2K' + s;
      return (f.lastCause === 0 ? 'S' : 'X') + s;
    };
    const eatsBy = new Map(); for (const q of eats) { let a = eatsBy.get(q[0]); if (!a) eatsBy.set(q[0], a = []); a.push(q); }
    const classify = idx => { // -> { c: counts[CLS], eff, kNow }
      const x = dinfo[idx], c = new Array(CLS.length).fill(0); let eff = 0, kNow = 0, n = 0;
      for (const q of eatsBy.get(idx) || []) {
        n++;
        if (q[2] !== tm) { c[CI.E]++; continue; }
        if (q[6]) kNow++;
        if (onLine(q[1], q[3])) { c[q[1] === kid ? CI.K0 : CI.KA]++; eff += 1; continue; }
        c[CI[fateCls(q[1], q[3], q[5])]]++;
        const f = family(q[1], q[3]); if (f.mass > 0) eff += f.toLine / f.mass;
      }
      c[CI.U] += Math.max(0, x.drops - n);
      return { c, eff, kNow };
    };
    const isFam = (id, e, y) => { const st = [id]; while (st.length) { const x = st.pop(); if (x === y) return true; for (const c of kids.get(x) || []) if (bornEv.get(c) > e) st.push(c); } return false; };
    const famTag = (id, e) => { // 'line' | 'alive' | 'dead:<cause>' for the family of id after e, with its drops to the line
      if (onLine(id, e)) return { t: 'line', toLine: 0 };
      const f = family(id, e);
      return { t: f.alive ? 'alive' : 'dead:' + f.lastCause, toLine: f.toLine, mass: f.mass, aliveLen: f.aliveLen };
    };
    // 1) own-team deaths from r250 by cause (sac separately), phase and length class: drop classes
    const agg = {};
    const add = (key, x, cl) => { const a = agg[key] || (agg[key] = [0, 0, 0, 0, 0, 0, ...new Array(CLS.length).fill(0)]); a[0]++; a[1] += x.len; a[2] += x.drops; a[3] += cl.eff; a[4] += cl.kNow; a[5] += x.near.some(id => lineAt(x.ev) === id) ? 1 : 0; for (let i = 0; i < CLS.length; i++) a[6 + i] += cl.c[i]; };
    const causeName = ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'];
    for (let i = 0; i < dinfo.length; i++) {
      const x = dinfo[i]; if (!x || x.team !== tm || x.r < 250) continue;
      if (x.id === kid) continue;
      const cl = classify(i);
      add([causeName[x.cause] === 'sac' ? 'sac' : 'other', phase(x.r), lenClass(x.len)].join('|'), x, cl);
    }
    // 2) the line: sacrifice pearls eaten by the line from r350 by the sacrificer's length class; its eater at the time
    const lineSac = {};
    for (const q of eats) {
      if (q[2] !== tm || q[4] < 350 || !onLine(q[1], q[3])) continue;
      const x = dinfo[q[0]]; if (!x) continue;
      const k = (x.team !== tm ? 'enemy' : causeName[x.cause] === 'sac' ? 'sac' : 'own-other') + '|' + (x.team === tm ? lenClass(x.len) : '-');
      lineSac[k] = (lineSac[k] || 0) + 1;
    }
    // 3) king choice snapshots: rows with the line member marked, and every row's fate
    const kc = {};
    for (const t of CPS) {
      const s = snaps[t]; if (!s) continue;
      const anc = lineAt(s.ev);
      kc[t] = s.rows[tm].map(r => {
        const di = deathOf.get(r[0]); const x = di !== undefined ? dinfo[di] : null;
        const f = famTag(r[0], s.ev);
        return [...r, r[0] === anc ? 1 : 0, finalIds[tm].has(r[0]) ? finalIds[tm].get(r[0]) : 0, x ? x.cause : -1, x ? x.r : -1, f.t, f.toLine || 0, f.aliveLen || 0];
      });
    }
    // 4) ours: labelled conversions and gathering episodes
    let convOut = null, gathOut = null;
    if (us === tm) {
      convOut = convs.map(v => {
        const o = { k: v.k, r: v.r, id: v.id, L: v.L, target: v.target, dist: v.dist, tLen: v.tLen, tRank: v.tRank, teamLongest: v.teamLongest, tDist: v.tDist, died: v.idx >= 0 ? 1 : 0 };
        o.tOnLine = onLine(v.target, v.ev) ? 1 : 0; o.tFinalKing = v.target === kid ? 1 : 0;
        o.tLineLater = line.includes(v.target) ? 1 : 0; // the target is an ancestor (or the king) at some time
        const di = deathOf.get(v.target); const tx = di !== undefined ? dinfo[di] : null;
        o.tFate = finalIds[tm].has(v.target) ? (v.target === kid ? 'king' : 'alive:' + finalIds[tm].get(v.target)) : tx ? 'died:' + tx.cause + '@' + tx.r + ':' + tx.len : 'gone';
        o.lineAt = lineAt(v.ev);
        { const f = famTag(v.target, v.ev); o.tFam = f.t; o.tFamToLine = f.toLine; o.tFamMass = f.mass || 0; }
        if (v.idx >= 0) { const cl = classify(v.idx); o.c = cl.c; o.eff = +cl.eff.toFixed(3); o.drops = dinfo[v.idx].drops; o.eatT = (eatsBy.get(v.idx) || []).filter(q => q[1] === v.target).length; }
        // the target's own later fate as a feeder: its death drops eaten by the line
        if (tx) { o.tDrops = tx.drops; o.tToLine = toLine.get(di) || 0; o.tCause = tx.cause; }
        return o;
      });
      gathOut = [...gath.values()].map(q => {
        const di = deathOf.get(q.id); const x = di !== undefined ? dinfo[di] : null;
        const fedLbl = convs.find(v => v.id === q.id && v.idx >= 0);
        const o = { id: q.id, r0: q.r0, r1: q.r1, L0: q.L0, d0: q.d0, dMin: q.dMin, turns: q.turns, onLine: line.includes(q.id) ? 1 : 0, final: finalIds[tm].has(q.id) ? finalIds[tm].get(q.id) : 0, isKing: q.id === kid ? 1 : 0 };
        if (x) { o.cause = x.cause; o.dr = x.r; o.len = x.len; o.fed = fedLbl ? fedLbl.k : null; const cl = classify(di); o.c = cl.c; o.eff = +cl.eff.toFixed(3); o.drops = x.drops; }
        { const f = famTag(q.id, q.ev0); o.fam = f.t; o.famToLine = f.toLine; o.famMass = f.mass || 0; o.famAliveLen = f.aliveLen || 0; }
        { const fd = convs.filter(v => v.idx >= 0 && v.r >= q.r0 && family(q.id, q.ev0) && isFam(q.id, q.ev0, v.id)); o.famFed = fd.length; }
        return o;
      });
    }
    out[tm] = { king: kl, kid, gen: line.length - 1, agg, lineSac, kc, conv: convOut, gath: gathOut, tags: us === tm ? tagTurns : undefined };
  }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------
function readJsonl(f) { return fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : []; }
function teamNames() { try { return Object.fromEntries(JSON.parse(fs.readFileSync(path.join(TOP, 'leaderboard.json'), 'utf8')).map(t => [t.id, t.name])); } catch { return {}; } }
function topTasks() {
  const seen = new Set(), out = [];
  for (const r of readJsonl(path.join(TOP, 'index.jsonl'))) {
    const k = r.battleId + ':' + r.gameId; if (seen.has(k)) continue; seen.add(k);
    if (!R500.includes(r.map)) continue;
    const f = path.join(TOP, String(r.battleId), r.gameId + '.replay.gz'); if (!fs.existsSync(f)) continue;
    out.push({ key: k, file: f, src: 'top', map: r.map, teamA: r.teamA, teamB: r.teamB, eloA: r.eloA, eloB: r.eloB, us: null });
  }
  return out;
}
function onlineTasks(set) {
  const dir = path.join(ONLINE, set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8')), names = teamNames(), out = [];
  for (const g of idx.games || idx) {
    if (g.ourWin === null || g.ourWin === undefined) continue;
    const f = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
    out.push({ key: set + ':' + g.gameId, file: f, set, src: 'online', map: g.mapName, opp: names[g.opponentTeam] || String(g.opponentTeam), us: String(g.ourSide).toUpperCase() });
  }
  return out;
}
function localTasks(dir) {
  const abs = path.resolve(ROOT, dir), out = [];
  for (const l of fs.readFileSync(path.join(abs, 'rows.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue;
    const row = JSON.parse(l), [opp, map, side, seed] = row.key.split(':');
    const f = path.join(abs, 'games', `${opp}_${map}_${side}_${seed}`, 'game.replay'); if (!fs.existsSync(f)) continue;
    out.push({ key: path.basename(abs) + ':' + row.key, file: f, set: path.basename(abs), src: 'local', map: MAPNAME[map.replace(/_(b|10)$/, '')] || map, opp, us: side });
  }
  return out;
}
function workerMain() {
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const load = makeLoader(viewerSource());
  process.on('message', task => {
    try { process.send({ key: task.key, line: JSON.stringify(analyse(load(task.file), task, perGame)) }); }
    catch (err) { process.send({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | ') }); }
  });
}
async function extract(tasks, file, jobs, limit) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const done = new Set(readJsonl(file).map(x => x.key));
  const todo = tasks.filter(t => !done.has(t.key)).slice(0, limit);
  console.log(`${path.relative(ROOT, file)}: ${tasks.length} games, cached ${done.size}, to do ${todo.length} (jobs ${jobs})`);
  if (!todo.length) return;
  const fd = fs.openSync(file, 'a'), t0 = Date.now(); let n = 0, errors = 0;
  await new Promise(resolve => {
    const q = todo.slice(); let live = Math.min(jobs, q.length);
    for (let i = 0, k = live; i < k; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced', execArgv: ['--max-old-space-size=3072'] });
      const next = () => { const t = q.shift(); if (!t) { w.kill(); if (--live === 0) resolve(); return; } w.send(t); };
      w.on('message', m => { if (m.error) { errors++; console.error('error', m.key, m.error); } else fs.writeSync(fd, m.line + '\n'); n++; if (n % 100 === 0) console.log(`  ${n}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`); next(); });
      next();
    }
  });
  fs.closeSync(fd);
  console.log(`done ${n} in ${((Date.now() - t0) / 1000).toFixed(0)}s, errors ${errors}`);
}
async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const jobs = Math.max(1, +opt('jobs', 4)), limit = +opt('limit', Infinity);
  const pos = []; for (let i = 0; i < argv.length; i++) { if (argv[i].startsWith('--')) { i++; continue; } pos.push(argv[i]); }
  if (pos[0] !== 'extract') { console.error('usage: see the header'); process.exit(2); }
  if (pos[1] === 'top') { // --reverse --name top2: a second process from the other end (the report reads every top*.jsonl, deduped)
    // games already in any top*.jsonl are skipped (a second file may hold a part of them)
    const done = new Set(); if (fs.existsSync(CACHE)) for (const f of fs.readdirSync(CACHE).filter(f => /^top.*\.jsonl$/.test(f))) for (const x of readJsonl(path.join(CACHE, f))) done.add(x.key);
    let T = topTasks().filter(t => !done.has(t.key)); if (argv.includes('--reverse')) T = T.reverse();
    return extract(T, path.join(CACHE, opt('name', 'top') + '.jsonl'), jobs, limit);
  }
  if (pos[1] === 'online') { for (const s of pos.slice(2)) await extract(onlineTasks(s), path.join(CACHE, 'online-' + s + '.jsonl'), jobs, limit); return; }
  if (pos[1] === 'local') { for (const s of pos.slice(2)) await extract(localTasks(s), path.join(CACHE, 'local-' + path.basename(s) + '.jsonl'), jobs, limit); return; }
  console.error('usage: see the header'); process.exit(2);
}
module.exports = { analyse, CLS, CI, CPS, parseLabel, lenClass };
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
