#!/usr/bin/env node
// Endgame king study: how the final king grows in r300-500 and whether our "gather to the king" helps.
// Written for research/observations/endgame-king.md (2026-09-30). Replays only; no games, no network.
//
// usage (repository root):
//   node exp/endgame-king/extract.js top [--jobs 3] [--limit N] [--keys <file>]   every game of data/top/index.jsonl (both map kinds)
//   node exp/endgame-king/extract.js online <set> [<set> ...] [--jobs 3]
//   Output: one JSON line per game in .cache/endgame-king/<top|online-<set>>.jsonl. Games already there are skipped.
//
// Reconstruction: tools/mass_ledger.js perGame() with hooks (its checks must stay 0). Own checks (chk2, all expected 0):
//   spawn  natural pearls found by this pre-scan (initial + spawned) != the ledger's natStart + natSpawned
//   pair   a natural eat that cannot be paired with a spawn on its tile
//   lin    this file's line decomposition: L_t (t = 300, 350, 400, 450) != the ledger's lin.cp[t].Lt, or final != ledger final
//   dec    L300 + sum(gains) - sum(costs) - sum(split losses) != final (per team, games that reached r300)
// Definitions (per team):
//   King (at a moment) = the team's longest living dragon (ties -> lowest id; mass ledger). Taken at the first turn of each round.
//   Final king = the longest at the end; line = the final king followed back through its parents. Line member i owns the
//     window from its birth to the split that created member i+1 (mass ledger convention): final = L_t + line eats - sprint
//     cost - bodies split off the line (lossOff) - the parent's remaining body when the line moves into the child (lossPath).
//   Bins: pre = r < 300, then 50-round bins b0 300-349, b1 350-399, b2 400-449, b3 450-499.
//   dec[bin] = [nat, ownSac, ownOther, enemy, sprint, lossOff, lossPath]: pearls eaten by the line by origin (own death drops
//     split by the ledger cause: sac vs every other cause), sprint segments paid, split losses.
//   env[bin] (line member's own turns, r >= 300) = [turns, eD<=3, eD<=6, sum min(eD,30), natural pearls on the board within
//     Manhattan 5 of its head (sum), turns in own territory, turns as the team's longest, enemy heads within 6 (sum),
//     own heads within 6 (sum)]. eD = torus Manhattan distance from its head to the nearest enemy head.
//   nk[phase][dcls] (r >= 340, non-king dragons of length >= 4 at their turn start; phase 340-399 / 400-449 / 450-499;
//     dcls = torus Manhattan to the current king's head <= 3, 4-8, 9-16, 17+) = [turns, natural eaten, drops eaten,
//     turns with a previous turn in the previous round, of those closer to the king than before].
//   coh (r340 cohort): every non-king dragon of length >= 4 alive at the first turn of r340:
//     [id, L0, dK0, end, massToLine, natAfter, finalLen(family alive), near spawns, eaten by itself, by own others, by enemy,
//      gather turns (ours), fed (ours: 1 feed, 2 conv), x0, y0, maxLen after, rank0]
//     end: 0 on the line (it is the final king or an ancestor), 1 family alive off the line, 2 died by sacrifice (its own
//     death; family), 3 died another cause, 4 family died later (after a split).
//     near spawns = natural spawns within Manhattan 5 of its r340 head in r340-379 (what it would forage if it stayed).
//   sac: every own sacrifice (ledger cause sac) from r300 by a non-final-king dragon, aggregated by bin|dLine class|len class:
//     [n, len, drops, toLine, offLonger, offOther, enemy, none, cameFar, famAliveOff, famToLine] where dLine = torus Manhattan
//     from the feeder's head to the line member's head at the death; cameFar = the feeder was > 8 from the line member 20
//     rounds earlier and is <= 3 now; offLonger = own eater longer than the feeder before eating, off the line.
//   lineSac[bin] = [sac pearls to the line, of which feeder <= 3 at death, of which came from > 8 twenty rounds before,
//     feeder length sum, from non-king feeders of length >= 8]
//   kd: deaths of own dragons of length >= 8 from r300: [r, len, cause, wasLongest, killerLen, onLineBefore(1 = line member)]
//   Ours (task.us): labels. gath = gathering episodes (every dragon with a move label token g<d>):
//     [id, r0, L0, d0, x0, y0, dKing0, rLast, gTurns, steps, natG, dropG, natPre, turnsPre, dMin, end, endR, drops, toLine,
//      toOwn, toEnemy, isLine, famAlive, becameLongest, nearSpawn, nearOwn, nearEnemy, nearSelf, fedKind, natAfterG,
//      dropAfterG, turnsAfterG, lineAt0IsKing, targetIsLine]
//     end: 1 fed (labelled feed/conv death), 2 other sacrifice, 3 died another cause, 4 alive at the end, 5 alive and on the line
//     nearSpawn = natural spawns within Manhattan 5 of its head at r0 during [r0, r0+40); near* = their eaters.
//   tags on line-member turns from r300: bin -> {tag: turns}; conv/feed records.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..'), TOP = path.join(ROOT, 'data', 'top'), ONLINE = path.join(ROOT, 'data', 'online');
const CACHE = path.join(ROOT, '.cache', 'endgame-king');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js')), FI = ML.FI;
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const ELIM = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default'];
const kindOf = m => ELIM.includes(m) ? 'elim' : R500.includes(m) ? 'r500' : 'other';
const binOf = r => r < 300 ? 0 : 1 + Math.min(3, Math.floor((r - 300) / 50)); // 0 pre, 1..4 = b0..b3
const dcls = d => d <= 3 ? 0 : d <= 8 ? 1 : d <= 16 ? 2 : 3;
const lcls = L => L <= 4 ? 0 : L <= 7 ? 1 : 2;
const phase3 = r => r < 400 ? 0 : r < 450 ? 1 : 2;

function parseLabel(s) {
  if (!s) return null;
  let m;
  if ((m = /^feed #(\d+) d(\d+) L(\d+)( conv)?/.exec(s))) return { k: m[4] ? 'conv' : 'feed', target: +m[1], dist: +m[2] };
  const head = (s.split('|')[0] || '');
  const g = /\sg(\d+)(?=\s|$)/.exec(head);
  const tags = [];
  for (const t of head.split(/\s+/)) if (/^(tg|tgx|gx|ks|ks2|grab@\S+|F\d+@\S+|TRADE|esc|late|K\d+)$/.test(t)) tags.push(t.replace(/@.*$/, '').replace(/^F\d+/, 'F').replace(/^K\d+/, 'K'));
  return { k: 'move', g: g ? +g[1] : null, tags };
}

function analyse(R, task, perGame) {
  const M = R.match.map, W = M.width, H = M.height;
  const nInit = M.initialDragons.length;
  const info = { map: task.map };
  if (task.map === 'Prisoners Dilemma') info.variant = nInit === 10 ? 'PD10' : 'PD6';
  const key = (x, y) => y * W + x;
  const tdist = (a, b) => { const dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
  const tdistXY = (ax, ay, bx, by) => { const dx = Math.abs(ax - bx), dy = Math.abs(ay - by); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
  const chk2 = { spawn: 0, pair: 0, lin: 0, dec: 0, surv: 0 };
  // ---- pre-scan: natural pearls (initial + spawned). A drop run = the consecutive pearl tileChanges right after a death
  // (the ledger's rule; its drop check is 0 on every game, so no spawn is absorbed into a run).
  const spawnT = new Map(); // tile -> [round, ...] in order (initial pearls: round -1)
  const pushS = (k, r) => { let a = spawnT.get(k); if (!a) spawnT.set(k, a = []); a.push(r); };
  let nSpawn = 0;
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) { pushS(i, -1); nSpawn++; }
  {
    let round = -1, dropping = false;
    for (const e of R.events) {
      if (dropping && !(e.type === 'tileChange' && e.hasPearl)) dropping = false;
      if (e.type === 'roundStart') round = e.round;
      else if (e.type === 'dragonDeath') dropping = true;
      else if (e.type === 'tileChange' && e.hasPearl && !dropping) { pushS(key(e.tile.x, e.tile.y), round); nSpawn++; }
    }
  }
  // ---- hooks
  let ev = 0, curRound = -1;
  const us = task.us || null;
  const bornEv = new Map(), parent = new Map(), bornR = new Map();
  for (const d0 of M.initialDragons) { bornEv.set(d0.id, -1); parent.set(d0.id, -1); bornR.set(d0.id, 0); }
  const eatsBy = new Map();   // dragon id -> [ev, round, cls(0 nat 1 ownSac 2 ownOther 3 enemy), deathIdx]
  const costsBy = new Map();  // dragon id -> [ev, round, paid]
  const splitsBy = new Map(); // dragon id -> [ev, round, childId, childLen, parentKept]
  const natEats = new Map();  // tile -> [[ev, round, team, id], ...]
  const dropEats = new Map(); // death idx -> [[eaterId, team, ev, lenBefore], ...]
  const dinfo = [];           // death idx -> {...}
  const deathOf = new Map();  // dragon id -> death idx
  const kingAt = { A: -1, B: -1 };
  const evAtRound = {};
  const pos = new Map();      // dragon id -> flat [round, x, y, ...] from r280 (first turn each round)
  const bigRows = [];         // [id, team, ev, r, eD, pearls5, own, isLongest, e6, a6]
  const nk = { A: new Array(3 * 4 * 5).fill(0), B: new Array(3 * 4 * 5).fill(0) };
  const nkState = new Map();  // id -> { r, dK, p, c }
  const coh = { A: [], B: [] }; let cohEv = -1;
  const lastLen = new Map();
  // ours
  const labels = new Map(), pendLbl = new Map();
  const gath = new Map();      // id -> episode
  const convs = [];
  const turnTags = [];         // [id, ev, r, tags(string)] for our dragons from r300 (line member filter at the end)
  const everLongestAfter = new Map(); // id -> first round it was the team longest at a round start from r300
  const finalAlive = new Map();       // id -> [team, length] at the end (ledger state)
  const pendEat = new Map();          // our dragon id -> [nat, drop] eaten during its current action
  const hooks = {
    turn(d, r, c) {
      ev++;
      if (r !== curRound) {
        curRound = r;
        evAtRound[r] = ev;
        for (const tm of ['A', 'B']) { let k = null; for (const x of c.drag.values()) if (x.team === tm && (!k || x.body.length > k.body.length || (x.body.length === k.body.length && x.id < k.id))) k = x; kingAt[tm] = k ? k.id : -1; if (k && r >= 300 && !everLongestAfter.has(k.id)) everLongestAfter.set(k.id, r); }
        if (r >= 340 && cohEv < 0) {
          cohEv = ev;
          for (const x of c.drag.values()) {
            if (x.id === kingAt[x.team] || x.body.length < 4) continue;
            const k = c.drag.get(kingAt[x.team]);
            let rank = 1; for (const o of c.drag.values()) if (o.team === x.team && o !== x && (o.body.length > x.body.length || (o.body.length === x.body.length && o.id < x.id))) rank++;
            coh[x.team].push({ id: x.id, L0: x.body.length, dK0: k ? tdist(k.body[0], x.body[0]) : 99, x0: x.body[0].x, y0: x.body[0].y, rank0: rank, r0: r });
          }
        }
      }
      const h = d.body[0], L = d.body.length;
      lastLen.set(d.id, L);
      if (r >= 280) { let a = pos.get(d.id); if (!a) pos.set(d.id, a = []); if (a.length === 0 || a[a.length - 3] !== r) a.push(r, h.x, h.y); }
      if (r >= 300 && L >= 8) {
        let eD = 99, e6 = 0, a6 = 0;
        for (const o of c.drag.values()) { if (o === d) continue; const dd = tdist(o.body[0], h); if (o.team !== d.team) { if (dd < eD) eD = dd; if (dd <= 6) e6++; } else if (dd <= 6) a6++; }
        let p5 = 0; for (const [k, o] of c.pearls) if (o < 0) { const px = k % W, py = (k / W) | 0; if (tdistXY(px, py, h.x, h.y) <= 5) p5++; }
        const own = c.terr[key(h.x, h.y)] === (d.team === 'A' ? 1 : 2) ? 1 : 0;
        bigRows.push([d.id, d.team, ev, r, eD, p5, own, kingAt[d.team] === d.id ? 1 : 0, e6, a6]);
      }
      if (r >= 340 && L >= 4 && kingAt[d.team] !== d.id) {
        let k = c.drag.get(kingAt[d.team]);
        if (k) {
          const dK = tdist(k.body[0], h), p = phase3(r), cl = dcls(dK), base = (p * 4 + cl) * 5, a = nk[d.team];
          a[base]++;
          const prev = nkState.get(d.id);
          if (prev && prev.r === r - 1) { a[base + 3]++; if (dK < prev.dK) a[base + 4]++; }
          nkState.set(d.id, { r, dK, base });
        } else nkState.delete(d.id);
      } else nkState.delete(d.id);
    },
    indicator(e, r, c) { if (!us) return; const d = c.drag.get(e.id); if (d && d.team === us) labels.set(e.id, e.text || ''); },
    action(d, e, r, c, before) {
      ev++;
      const a = e.action;
      if (a && a.kind === 'move') {
        const paid = before.length + d.ateThisAct - d.body.length;
        if (paid > 0) { let q = costsBy.get(d.id); if (!q) costsBy.set(d.id, q = []); q.push(ev, r, paid); }
      }
      if (!us || d.team !== us) return;
      const text = labels.get(d.id); labels.delete(d.id);
      const pe = pendEat.get(d.id) || [0, 0]; pendEat.delete(d.id);
      const t = parseLabel(text);
      if (!t) return;
      if (t.k === 'move') {
        if (r >= 300) turnTags.push([d.id, ev, r, t.tags.join(' ') + (t.g !== null ? ' g' : '')]);
        if (t.g !== null) {
          let q = gath.get(d.id);
          if (!q) {
            const k = c.drag.get(kingAt[d.team]);
            gath.set(d.id, q = { id: d.id, r0: r, ev0: ev, L0: before.length, d0: t.g, x0: before[0].x, y0: before[0].y, dKing0: k ? tdist(k.body[0], before[0]) : 99,
              rLast: r, gTurns: 0, steps: 0, natG: 0, dropG: 0, dMin: t.g, dKmin: 99, kingId0: kingAt[d.team] });
          }
          q.rLast = r; q.gTurns++; q.steps += d.steps || 0; q.dMin = Math.min(q.dMin, t.g); q.natG += pe[0]; q.dropG += pe[1];
          const k = c.drag.get(kingAt[d.team]); if (k && k.id !== d.id) q.dKmin = Math.min(q.dKmin, tdist(k.body[0], d.body[0]));
        }
        return;
      }
      const rec = { k: t.k, r, id: d.id, L: before.length, target: t.target, dist: t.dist, ev, idx: -1 };
      pendLbl.set(d.id, rec); convs.push(rec);
    },
    eat(d, tile, o, r, c) {
      ev++;
      let cls = 0;
      if (o >= 0) { const x = c.deaths[o]; cls = x.team === d.team ? (x.cause === 0 ? 1 : 2) : 3; let q = dropEats.get(o); if (!q) dropEats.set(o, q = []); q.push([d.id, d.team, ev, d.body.length]); }
      else { let q = natEats.get(tile); if (!q) natEats.set(tile, q = []); q.push([ev, r, d.team, d.id]); }
      let q = eatsBy.get(d.id); if (!q) eatsBy.set(d.id, q = []); q.push(ev, r, cls, o);
      const s = nkState.get(d.id);
      if (s && s.r === r) nk[d.team][s.base + (cls === 0 ? 1 : 2)]++;
      if (us && d.team === us) { const pe = pendEat.get(d.id) || [0, 0]; pe[cls === 0 ? 0 : 1]++; pendEat.set(d.id, pe); }
    },
    split(p, ch, e, r, c) {
      ev++; bornEv.set(ch.id, ev); parent.set(ch.id, p.id); bornR.set(ch.id, r);
      let q = splitsBy.get(p.id); if (!q) splitsBy.set(p.id, q = []); q.push(ev, r, ch.id, e.childBody.length, e.parentBody.length);
    },
    death(d, rec, idx, other, r, c) {
      ev++;
      let ko = null; for (const o of c.drag.values()) if (o !== d && o.team === d.team && (!ko || o.body.length > ko.body.length || (o.body.length === ko.body.length && o.id < ko.id))) ko = o;
      const x = { id: d.id, team: d.team, r, cause: rec.cause, len: rec.len, drops: rec.drops, ev, hx: d.body[0].x, hy: d.body[0].y,
        dK: ko ? tdist(ko.body[0], d.body[0]) : 99, wasLongest: rec.king ? 1 : (!ko || d.body.length > ko.body.length || (d.body.length === ko.body.length && d.id < ko.id)) ? 1 : 0,
        killerLen: other && other.team !== d.team ? other.body.length : 0, lbl: null };
      const p = pendLbl.get(d.id); if (p && p.r === r) { p.idx = idx; x.lbl = p.k; }
      pendLbl.delete(d.id);
      dinfo[idx] = x; deathOf.set(d.id, idx);
    },
    end(rounds, c) { for (const d of c.drag.values()) finalAlive.set(d.id, [d.team, d.body.length]); },
  };
  const g = perGame(R, info, hooks);
  if (nSpawn !== g.natStart + g.natSpawned) chk2.spawn++;
  // ---- natural spawn -> eater pairing
  const natEater = new Map(); // tile -> [[spawnRound, eatRound|null, team|null, id|null], ...]
  for (const [k, sp] of spawnT) {
    const es = natEats.get(k) || [];
    const out = []; let j = 0;
    for (let i = 0; i < sp.length; i++) {
      const next = i + 1 < sp.length ? sp[i + 1] : Infinity;
      if (j < es.length && es[j][1] >= sp[i] && es[j][1] <= next) { out.push([sp[i], es[j][1], es[j][2], es[j][3]]); j++; }
      else out.push([sp[i], null, null, null]);
    }
    if (j !== es.length) chk2.pair += es.length - j;
    natEater.set(k, out);
  }
  for (const k of natEats.keys()) if (!spawnT.has(k)) chk2.pair += natEats.get(k).length;
  const spawnsNear = (x0, y0, r0, r1) => { // natural spawns within Manhattan 5 of (x0, y0) in [r0, r1): eaters
    const out = [];
    for (let dy = -5; dy <= 5; dy++) for (let dx = -5 + Math.abs(dy); dx <= 5 - Math.abs(dy); dx++) {
      const x = ((x0 + dx) % W + W) % W, y = ((y0 + dy) % H + H) % H;
      if (tdistXY(x, y, x0, y0) !== Math.abs(dx) + Math.abs(dy)) continue; // wrapped twice on a small map
      const a = natEater.get(key(x, y)); if (!a) continue;
      for (const s of a) if (s[0] >= r0 && s[0] < r1) out.push(s);
    }
    return out;
  };
  const nearEaters = (x0, y0, r0, r1, tm, selfId) => { const sp = spawnsNear(x0, y0, r0, r1); let a = 0, b = 0, c = 0; for (const s of sp) { if (s[2] === null) continue; if (s[2] !== tm) c++; else if (s[3] === selfId) a++; else b++; } return [sp.length, a, b, c]; };
  // ---- final dragons (the ledger's end state) and an independent length check: birth + eats - costs - split-offs = end length
  const finalLen = { A: new Map(), B: new Map() };
  for (const [id, [tm, L]] of finalAlive) finalLen[tm].set(id, L);
  {
    const birthLen = new Map();
    for (const d0 of M.initialDragons) birthLen.set(d0.id, d0.body.length);
    for (const e of R.events) if (e.type === 'dragonSplit') birthLen.set(e.childId, e.childBody.length);
    for (const [id, [, Lend]] of finalAlive) {
      let L = birthLen.get(id) || 0;
      const ea = eatsBy.get(id); if (ea) L += ea.length / 4;
      const co = costsBy.get(id); if (co) for (let i = 0; i < co.length; i += 3) L -= co[i + 2];
      const sp = splitsBy.get(id); if (sp) for (let i = 0; i < sp.length; i += 5) L -= sp[i + 3];
      if (L !== Lend) chk2.surv++;
    }
  }
  const kids = new Map(); for (const [c0, p0] of parent) if (p0 >= 0) { if (!kids.has(p0)) kids.set(p0, []); kids.get(p0).push(c0); }
  const out = { key: task.key, src: task.src, set: task.set || null, map: task.map, kind: kindOf(task.map), variant: info.variant || null,
    us, opp: task.opp || null, winner: g.winner ? String(g.winner).toUpperCase() : null, rounds: g.rounds, endReason: g.endReason, chk: g.chk, chk2,
    teamA: task.teamA || null, teamB: task.teamB || null, eloA: task.eloA || null, eloB: task.eloB || null };
  for (const tm of ['A', 'B']) {
    const T = g[tm];
    const st = { king: T.st.king.slice(30), units: T.st.units.slice(30), total: T.st.total.slice(30), second: T.st.second.slice(30) };
    // final king (ledger: longest, ties lowest id) and the line
    let kid = -1, kl = 0; for (const [id, L] of finalLen[tm]) if (L > kl || (L === kl && id < kid)) { kid = id; kl = L; }
    if (kl !== T.st.king[50]) chk2.lin++;
    const line = []; for (let x = kid; x !== undefined && x !== -1; x = parent.get(x)) line.push(x);
    line.reverse();
    const win = new Map();
    for (let i = 0; i < line.length; i++) win.set(line[i], [bornEv.get(line[i]), i + 1 < line.length ? bornEv.get(line[i + 1]) : Infinity, i]);
    const onLine = (id, e) => { const w = win.get(id); return w ? e > w[0] && e < w[1] : false; };
    const lineAtEv = e => { for (const id of line) if (onLine(id, e)) return id; return -1; };
    // decomposition
    const dec = Array.from({ length: 5 }, () => new Array(7).fill(0));
    if (kid >= 0) {
      for (let i = 0; i < line.length; i++) {
        const id = line[i], [w0, w1] = win.get(id);
        const ea = eatsBy.get(id) || []; for (let q = 0; q < ea.length; q += 4) if (ea[q] > w0 && ea[q] < w1) dec[binOf(ea[q + 1])][ea[q + 2]]++;
        const co = costsBy.get(id) || []; for (let q = 0; q < co.length; q += 3) if (co[q] > w0 && co[q] < w1) dec[binOf(co[q + 1])][4] += co[q + 2];
        const sp = splitsBy.get(id) || [];
        for (let q = 0; q < sp.length; q += 5) {
          if (!(sp[q] > w0 && sp[q] <= w1)) continue;
          if (i + 1 < line.length && sp[q + 2] === line[i + 1]) dec[binOf(sp[q + 1])][6] += sp[q + 4]; else dec[binOf(sp[q + 1])][5] += sp[q + 3];
        }
      }
    }
    const net = b => dec[b][0] + dec[b][1] + dec[b][2] + dec[b][3] - dec[b][4] - dec[b][5] - dec[b][6];
    const Lt = {};
    if (kid >= 0) {
      let acc = kl; const cps = [450, 400, 350, 300];
      // L_t = final - net gains from t on; bins are 50 rounds from 300
      Lt[450] = kl - net(4); Lt[400] = Lt[450] - net(3); Lt[350] = Lt[400] - net(2); Lt[300] = Lt[350] - net(1);
      for (const t of cps) {
        const c = T.lin && T.lin.cp && T.lin.cp[t];
        if (c) { if (c.Lt !== Lt[t]) chk2.lin++; }
        else delete Lt[t];
      }
      void acc;
      if (T.lin && T.lin.len !== kl) chk2.lin++;
      // birth length of the root + all gains - all losses = final
      const d0 = M.initialDragons.find(x => x.id === line[0]);
      if (d0) { let s = d0.body.length; for (let b = 0; b < 5; b++) s += net(b); if (s !== kl) chk2.dec++; }
    }
    // line member at a round (its head position at that round's first turn)
    const posAt = (id, r) => { const a = pos.get(id); if (!a) return null; let best = null; for (let i = 0; i < a.length; i += 3) { if (a[i] <= r) best = [a[i + 1], a[i + 2], a[i]]; else break; } return best && r - best[2] <= 3 ? best : null; };
    const lineMemberAtRound = r => { const e = evAtRound[r]; return e === undefined ? -1 : lineAtEv(e + 0.5); };
    // env: line member's own turns
    const env = Array.from({ length: 4 }, () => new Array(9).fill(0));
    for (const row of bigRows) {
      if (row[1] !== tm || row[3] < 300 || !onLine(row[0], row[2])) continue;
      const b = binOf(row[3]) - 1, a = env[b];
      a[0]++; if (row[4] <= 3) a[1]++; if (row[4] <= 6) a[2]++; a[3] += Math.min(row[4], 30); a[4] += row[5]; a[5] += row[6]; a[6] += row[7]; a[7] += row[8]; a[8] += row[9];
    }
    // family helpers (id and every descendant born after e)
    const family = (id, e) => {
      const r = { alive: 0, aliveLen: 0, toLine: 0, mass: 0, lastCause: -1, lastR: -1, n: 0, onLine: 0, lastLbl: null, nLbl: 0, drops: 0 };
      const stck = [id];
      while (stck.length) {
        const x = stck.pop(); r.n++;
        if (win.has(x)) r.onLine = 1;
        if (finalLen[tm].has(x)) { r.alive = 1; r.aliveLen += finalLen[tm].get(x); r.mass += finalLen[tm].get(x); }
        const di = deathOf.get(x);
        if (di !== undefined) { const dz = dinfo[di]; r.mass += dz.len; r.drops += dz.drops; if (dz.lbl) r.nLbl++; for (const q of dropEats.get(di) || []) if (q[1] === tm && onLine(q[0], q[2])) r.toLine++; if (dz.r > r.lastR || (dz.r === r.lastR && dz.ev > r.lastEv)) { r.lastR = dz.r; r.lastEv = dz.ev; r.lastCause = dz.cause; r.lastLbl = dz.lbl; } }
        for (const c of kids.get(x) || []) if (bornEv.get(c) > e) stck.push(c);
      }
      return r;
    };
    // cohort r340
    const cohOut = [];
    for (const c of coh[tm]) {
      const f = family(c.id, cohEv);
      const di = deathOf.get(c.id), x = di !== undefined ? dinfo[di] : null;
      let end;
      if (win.has(c.id)) end = 0;
      else if (f.alive) end = 1;
      else if (x && x.cause === 0) end = 2;
      else if (x && x.cause !== 0 && (!splitsBy.get(c.id) || f.n === 1)) end = 3;
      else end = 4;
      let natAfter = 0; const ea = eatsBy.get(c.id) || []; for (let q = 0; q < ea.length; q += 4) if (ea[q + 1] >= c.r0 && ea[q + 2] === 0) natAfter++;
      let maxLen = c.L0; { let L = c.L0; for (let q = 0; q < ea.length; q += 4) if (ea[q + 1] >= c.r0) { L++; maxLen = Math.max(maxLen, L); } }
      const sp = spawnsNear(c.x0, c.y0, c.r0, c.r0 + 40);
      let eS = 0, eO = 0, eE = 0; for (const s of sp) { if (s[2] === null) continue; if (s[2] !== tm) eE++; else if (s[3] === c.id) eS++; else eO++; }
      const gq = gath.get(c.id);
      const fedK = x && x.lbl ? (x.lbl === 'conv' ? 2 : 1) : 0;
      const bw = nearEaters(c.x0, c.y0, c.r0 - 40, c.r0, tm, c.id);
      cohOut.push([c.id, c.L0, c.dK0, end, f.toLine, natAfter, f.aliveLen, sp.length, eS, eO, eE, gq ? gq.gTurns : 0, fedK, c.x0, c.y0, maxLen, c.rank0, ...bw, f.lastCause, f.lastLbl ? 1 : 0, f.drops]);
    }
    // sacrifices from r300 (own team), aggregated
    const sac = {};
    const lineSac = Array.from({ length: 4 }, () => new Array(5).fill(0));
    const kd = [];
    for (let i = 0; i < dinfo.length; i++) {
      const x = dinfo[i]; if (!x || x.team !== tm || x.r < 300) continue;
      if (x.len >= 8) kd.push([x.r, x.len, x.cause, x.wasLongest, x.killerLen, win.has(x.id) ? 1 : 0]);
      if (x.cause !== 0 || x.id === kid) continue;
      const lm = lineAtEv(x.ev);
      let dLine = 99, cameFar = 0;
      if (lm >= 0) {
        const lp = posAt(lm, x.r); if (lp) dLine = tdistXY(lp[0], lp[1], x.hx, x.hy);
        const fp20 = posAt(x.id, x.r - 20), lm20 = lineMemberAtRound(x.r - 20), lp20 = lm20 >= 0 ? posAt(lm20, x.r - 20) : null;
        if (fp20 && lp20 && tdistXY(fp20[0], fp20[1], lp20[0], lp20[1]) > 8 && dLine <= 3) cameFar = 1;
      }
      let toLine = 0, offLonger = 0, offOther = 0, enemy = 0, none = 0, famAliveOff = 0, famToLine = 0;
      const eaten = dropEats.get(i) || [];
      for (const q of eaten) {
        if (q[1] !== tm) { enemy++; continue; }
        if (onLine(q[0], q[2])) { toLine++; continue; }
        if (q[3] > x.len) offLonger++; else offOther++;
        const f = family(q[0], q[2]); if (f.alive) famAliveOff++; else if (f.toLine > 0) famToLine++;
      }
      none = Math.max(0, x.drops - eaten.length);
      const b = binOf(x.r) - 1;
      const k = b + '|' + dcls(dLine > 90 ? 99 : dLine) + '|' + lcls(x.len) + '|' + (x.lbl || '-');
      const a = sac[k] || (sac[k] = new Array(11).fill(0));
      a[0]++; a[1] += x.len; a[2] += x.drops; a[3] += toLine; a[4] += offLonger; a[5] += offOther; a[6] += enemy; a[7] += none; a[8] += cameFar; a[9] += famAliveOff; a[10] += famToLine;
      if (toLine) { const ls = lineSac[b]; ls[0] += toLine; if (dLine <= 3) ls[1] += toLine; if (cameFar) ls[2] += toLine; ls[3] += x.len * toLine; if (x.len >= 8) ls[4] += toLine; }
    }
    const faults = T.fl[FI.dn_fault].reduce((a, b) => a + b, 0);
    const kdl = T.fl[FI.kd_len], kdn = T.fl[FI.kd_n];
    const res = { king: kl, kid, gen: line.length - 1, st, Lt, dec, env, nk: nk[tm], coh: cohOut, sac, lineSac, kd, lin: T.lin ? { len: T.lin.len, gen: T.lin.gen, cp: T.lin.cp } : null,
      splits: T.splits, sonar: T.sonar, faults, kdLen: [0, 1, 2, 3, 4].map(b => b === 0 ? kdl.slice(0, 30).reduce((a, x) => a + x, 0) : kdl.slice(25 + 5 * b, 30 + 5 * b).reduce((a, x) => a + x, 0)),
      keat: ['keat_nat', 'keat_oSac', 'keat_eSac'].map(k => T.fl[FI[k]].slice(30)) };
    // line member at r300/350/400/450: its rank among the team (1 = longest) and length
    res.lr = {};
    for (const t of [300, 350, 400, 450]) {
      const e = evAtRound[t]; if (e === undefined || kid < 0) continue;
      const lm = lineAtEv(e + 0.5); if (lm < 0) continue;
      res.lr[t] = [lm, Lt[t] !== undefined ? Lt[t] : null, st.king[(t - 300) / 10], everLongestAfter.get(lm) || 0];
    }
    if (us === tm) {
      // gathering episodes
      res.gath = [...gath.values()].map(q => {
        const di = deathOf.get(q.id), x = di !== undefined ? dinfo[di] : null;
        let end = 4, endR = 500, drops = 0, toLine = 0, toOwn = 0, toEnemy = 0;
        if (x) {
          endR = x.r; drops = x.drops;
          end = x.lbl ? 1 : x.cause === 0 ? 2 : 3;
          for (const e of dropEats.get(di) || []) { if (e[1] !== tm) toEnemy++; else if (onLine(e[0], e[2])) toLine++; else toOwn++; }
        } else if (win.has(q.id)) end = 5;
        const f = family(q.id, q.ev0);
        let natPre = 0, turnsPre = 0, natAfterG = 0, dropAfterG = 0;
        const ea = eatsBy.get(q.id) || [];
        for (let i = 0; i < ea.length; i += 4) {
          if (ea[i + 1] >= q.r0 - 20 && ea[i + 1] < q.r0 && ea[i + 2] === 0) natPre++;
          if (ea[i + 1] > q.rLast) { if (ea[i + 2] === 0) natAfterG++; else dropAfterG++; }
        }
        { const a = pos.get(q.id) || []; for (let i = 0; i < a.length; i += 3) if (a[i] >= q.r0 - 20 && a[i] < q.r0) turnsPre++; }
        const turnsAfterG = Math.max(0, (x ? x.r : g.rounds - 1) - q.rLast);
        const sp = spawnsNear(q.x0, q.y0, q.r0, q.r0 + 40);
        let nOwn = 0, nEn = 0, nSelf = 0; for (const s of sp) { if (s[2] === null) continue; if (s[2] !== tm) nEn++; else if (s[3] === q.id) nSelf++; else nOwn++; }
        const lmAt0 = lineAtEv(q.ev0);
        const becameLongest = everLongestAfter.has(q.id) && everLongestAfter.get(q.id) > q.r0 ? 1 : 0;
        const lastConv = convs.filter(v => v.id === q.id && v.idx >= 0).pop();
        const targetIsLine = lastConv ? (onLine(lastConv.target, lastConv.ev) ? 1 : 0) : -1;
        const bw = nearEaters(q.x0, q.y0, q.r0 - 40, q.r0, tm, q.id);
        const par = parent.get(q.id), pg = par !== undefined && par >= 0 ? gath.get(par) : null;
        const parentGath = pg && bornEv.get(q.id) > pg.ev0 ? 1 : 0;
        const sp2 = splitsBy.get(q.id) || []; let stub = 0;
        if (x) for (let i = 0; i < sp2.length; i += 5) if (sp2[i + 1] >= x.r - 2 && sp2[i + 4] <= 3) stub = 1;
        let famOnLine = 0; { const st2 = [q.id]; while (st2.length) { const y = st2.pop(); if (win.has(y)) famOnLine = 1; for (const c2 of kids.get(y) || []) if (bornEv.get(c2) > q.ev0) st2.push(c2); } }
        return [q.id, q.r0, q.L0, q.d0, q.x0, q.y0, q.dKing0, q.rLast, q.gTurns, q.steps, q.natG, q.dropG, natPre, turnsPre, Math.min(q.dMin, q.dKmin), end, endR, drops, toLine, toOwn, toEnemy,
          win.has(q.id) ? 1 : 0, f.alive, becameLongest, sp.length, nOwn, nEn, nSelf, x && x.lbl ? x.lbl : null, natAfterG, dropAfterG, turnsAfterG, lmAt0 === q.kingId0 ? 1 : 0, targetIsLine, f.toLine, f.aliveLen,
          ...bw, parentGath, stub, famOnLine, f.lastCause, f.lastLbl, f.nLbl, f.drops, f.n, par === undefined ? -1 : par];
      });
      res.conv = convs.map(v => {
        const x = v.idx >= 0 ? dinfo[v.idx] : null;
        let toLine = 0, toTarget = 0, toOwn = 0, toEnemy = 0;
        if (x) for (const e of dropEats.get(v.idx) || []) { if (e[1] !== tm) toEnemy++; else if (onLine(e[0], e[2])) toLine++; else toOwn++; if (e[0] === v.target) toTarget++; }
        return [v.k, v.r, v.id, v.L, v.target, v.dist, x ? 1 : 0, x ? x.drops : 0, toLine, toTarget, toOwn, toEnemy, onLine(v.target, v.ev) ? 1 : 0, gath.has(v.id) ? 1 : 0];
      });
      const tagB = [{}, {}, {}, {}];
      for (const [id, e, r, s] of turnTags) { if (!onLine(id, e)) continue; const b = binOf(r) - 1; const o = tagB[b]; o._n = (o._n || 0) + 1; for (const t of s.split(' ')) if (t) o[t] = (o[t] || 0) + 1; }
      res.lineTags = tagB;
    }
    out[tm] = res;
  }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------
function readJsonl(f) { return fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : []; }
function doneKeys(f) { const s = new Set(); if (!fs.existsSync(f)) return s; for (const l of fs.readFileSync(f, 'utf8').split('\n')) { const m = /^\{"key":"([^"]+)"/.exec(l); if (m) s.add(m[1]); } return s; }
function teamNames() { try { return Object.fromEntries(JSON.parse(fs.readFileSync(path.join(TOP, 'leaderboard.json'), 'utf8')).map(t => [t.id, t.name])); } catch { return {}; } }
function topTasks(keysFile) {
  const seen = new Set(), out = [];
  const want = keysFile ? new Set(fs.readFileSync(path.resolve(ROOT, keysFile), 'utf8').split('\n').map(s => s.trim()).filter(Boolean)) : null;
  for (const r of readJsonl(path.join(TOP, 'index.jsonl'))) {
    const k = r.battleId + ':' + r.gameId; if (seen.has(k)) continue; seen.add(k);
    if (want && !want.has(k)) continue;
    const f = path.join(TOP, String(r.battleId), r.gameId + '.replay.gz'); if (!fs.existsSync(f)) continue;
    out.push({ key: k, file: f, src: 'top', map: r.map, teamA: r.teamA, teamB: r.teamB, eloA: r.eloA, eloB: r.eloB, us: null });
  }
  return out;
}
function onlineTasks(set) {
  const dir = path.join(ONLINE, set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8')), names = teamNames(), out = [];
  for (const g of idx.games || idx) {
    const f = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
    out.push({ key: set + ':' + g.gameId, file: f, set, src: 'online', map: g.mapName, opp: names[g.opponentTeam] || String(g.opponentTeam), oppId: g.opponentTeam, us: String(g.ourSide).toUpperCase() });
  }
  return out;
}
function workerMain() {
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const { perGame } = ML;
  const load = makeLoader(viewerSource());
  process.on('message', task => {
    try { process.send({ key: task.key, line: JSON.stringify(analyse(load(task.file), task, perGame)) }); }
    catch (err) { process.send({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | ') }); }
  });
}
async function extract(tasks, file, jobs, limit) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const done = doneKeys(file);
  const todo = tasks.filter(t => !done.has(t.key)).slice(0, limit);
  console.log(`${path.relative(ROOT, file)}: ${tasks.length} games, cached ${done.size}, to do ${todo.length} (jobs ${jobs})`);
  if (!todo.length) return;
  const fd = fs.openSync(file, 'a'), t0 = Date.now(); let n = 0, errors = 0;
  await new Promise(resolve => {
    const q = todo.slice(); let live = Math.min(jobs, q.length);
    for (let i = 0, k = live; i < k; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced', execArgv: ['--max-old-space-size=3072'] });
      const next = () => { const t = q.shift(); if (!t) { w.kill(); if (--live === 0) resolve(); return; } w.send(t); };
      w.on('message', m => { if (m.error) { errors++; console.error('error', m.key, m.error); } else fs.writeSync(fd, m.line + '\n'); n++; if (n % 200 === 0) console.log(`  ${n}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`); next(); });
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
  const jobs = Math.max(1, Math.min(3, +opt('jobs', 3))), limit = +opt('limit', Infinity);
  const pos = []; for (let i = 0; i < argv.length; i++) { if (argv[i].startsWith('--')) { i++; continue; } pos.push(argv[i]); }
  if (pos[0] === 'top') return extract(topTasks(opt('keys', null)), path.join(CACHE, opt('name', 'top') + '.jsonl'), jobs, limit);
  if (pos[0] === 'online') { for (const s of pos.slice(1)) await extract(onlineTasks(s), path.join(CACHE, 'online-' + s + '.jsonl'), jobs, limit); return; }
  console.error('usage: see the header'); process.exit(2);
}
module.exports = { analyse, parseLabel, readJsonl, binOf, dcls };
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
