#!/usr/bin/env node
// Failure study of our bot's mechanisms against the elite teams (replays only; no games, no network).
// Written for research/observations/mech-merge2-failures.md (2026-09-30).
//
// One reconstruction pass per game: the tools/mass_ledger.js step simulation with timeline hooks; for our online games
// also tools/mech_check.js analyse() (mechanism records from our INDICATOR labels), merged into the same pass.
// Per game it writes one JSON line:
//   mech  (online only) every firing of esc / sprintEsc / feed / gather / portal / trade / split with its context and
//         what happened after (who killed the body, from where, which pearls went where),
//   rams  every head-on death of a dragon of length >= 6 (either side) and every one of ours, with what the victim could
//         know at its last decision (killer position, visible segments, occupied tiles, the victim's own label),
//   agg   population counters per side ('us'/'them' online, 'A'/'B' for top games): long-dragon exposure, responses when
//         cornered, head-on pearl flows by collector distance, sacrifices, split children, portal crossings.
//
// usage (repository root):
//   node exp/mech-failures/collect.js online <set>[+<set>...] --out <file.jsonl> [--jobs 4]
//   node exp/mech-failures/collect.js top --out <file.jsonl> [--jobs 4] [--limit N]
//     Games already in --out are skipped (resumable). The report is exp/mech-failures/report.js.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..'), ONLINE = path.join(ROOT, 'data', 'online'), TOP = path.join(ROOT, 'data', 'top');
const DIRS = ['N', 'E', 'S', 'W'];
const R500 = new Set(['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma']);

function teamNames() { try { return Object.fromEntries(JSON.parse(fs.readFileSync(path.join(TOP, 'leaderboard.json'), 'utf8')).map(t => [t.id, t.name])); } catch { return {}; } }
function onlineTasks(pool) {
  const names = teamNames(), out = [];
  for (const part of pool.split('+')) {
    const dir = path.join(ONLINE, part), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
    for (const g of idx.games || idx) {
      if (g.ourWin === null || g.ourWin === undefined) continue;
      const f = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
      out.push({ mode: 'online', key: part + ':' + g.gameId, file: f, set: part, src: 'online', map: g.mapName, opp: names[g.opponentTeam] || String(g.opponentTeam),
        oppId: g.opponentTeam, us: String(g.ourSide).toUpperCase(), gameId: g.gameId, ourWin: g.ourWin });
    }
  }
  return out;
}
function topTasks() {
  const seen = new Set(), out = [];
  for (const l of fs.readFileSync(path.join(TOP, 'index.jsonl'), 'utf8').split('\n')) {
    if (!l.trim()) continue; let r; try { r = JSON.parse(l); } catch { continue; }
    const k = r.battleId + ':' + r.gameId; if (seen.has(k)) continue; seen.add(k);
    const f = path.join(TOP, String(r.battleId), r.gameId + '.replay.gz'); if (!fs.existsSync(f)) continue;
    out.push({ mode: 'top', key: 'top:' + k, file: f, set: 'top', src: 'top', map: r.map, opp: null, us: 'A', gameId: k, teamA: r.teamA, teamB: r.teamB, winner: r.winner || null });
  }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------
// One game.
function study(R, task) {
  const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const online = task.mode === 'online';
  const us = task.us, them = us === 'A' ? 'B' : 'A';
  const sideOf = tm => online ? (tm === us ? 'us' : 'them') : tm;
  const G = {
    snaps: new Map(), lastTurn: new Map(), ind: new Map(), acts: new Map(), portalActs: [], dropEaten: new Map(),
    splits: [], splitOf: new Map(), deaths: [], deathOf: new Map(), expo: [], longStats: {}, rounds: 0, final: [], all: null,
  };
  let W = 0, H = 0, N = 0, NB = null, PORT = null, stamp = null, dist = null, queue = null, cur = 0, lastR = -1;
  const kx = k => k % W, ky = k => (k / W) | 0;
  const tdk = (a, b) => { const dx = Math.abs(kx(a) - kx(b)), dy = Math.abs(ky(a) - ky(b)); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
  const chk = (a, b) => { const dx = Math.abs(kx(a) - kx(b)), dy = Math.abs(ky(a) - ky(b)); return Math.max(Math.min(dx, W - dx), Math.min(dy, H - dy)); };
  const K = p => p.y * W + p.x;
  function initGeo(c) {
    W = c.W; H = c.H; N = W * H;
    NB = new Int32Array(N * 4).fill(-1); PORT = new Uint8Array(N * 4);
    for (let k = 0; k < N; k++) for (let d = 0; d < 4; d++) {
      const x = kx(k), y = ky(k), nx = c.across(x, y, DIRS[d]);
      if (!nx) continue;
      NB[k * 4 + d] = nx.y * W + nx.x;
      const px = ((x + [0, 1, 0, -1][d]) % W + W) % W, py = ((y + [-1, 0, 1, 0][d]) % H + H) % H;
      if (nx.x !== px || nx.y !== py) PORT[k * 4 + d] = 1;
    }
    stamp = new Int32Array(N); dist = new Int32Array(N); queue = new Int32Array(N);
    G.terr = c.terr;
  }
  // BFS from sources over tiles for which pass(k) is true (sources always pass); visit(k, d, blocked) returns true to stop.
  function bfs(srcs, maxD, pass, visit) {
    cur++; let qh = 0, qt = 0;
    for (const s of srcs) { if (s < 0 || stamp[s] === cur) continue; stamp[s] = cur; dist[s] = 0; queue[qt++] = s; }
    while (qh < qt) {
      const k = queue[qh++], d = dist[k];
      if (visit && visit(k, d, false)) return;
      if (d >= maxD) continue;
      for (let i = 0; i < 4; i++) {
        const u = NB[k * 4 + i]; if (u < 0 || stamp[u] === cur) continue;
        stamp[u] = cur; dist[u] = d + 1;
        if (!pass(u)) { if (visit && visit(u, d + 1, true)) return; continue; } // blocked tiles are reported, not expanded
        queue[qt++] = u;
      }
    }
  }
  const nbString = (c, d) => {
    const h = K(d.body[0]); let s = '';
    for (let i = 0; i < 4; i++) {
      const u = NB[h * 4 + i]; if (u < 0) { s += 'K'; continue; }
      const o = c.occ.get(u); if (o === undefined) { s += '.'; continue; }
      const od = c.drag.get(o); if (!od) { s += '?'; continue; }
      const head = K(od.body[0]) === u;
      s += od === d ? 'S' : od.team === d.team ? (head ? 'a' : 'A') : (head ? 'e' : 'E');
    }
    return s;
  };
  const areaFrom = (c, k, cap) => { let n = 0; bfs([k], 60, u => !c.occ.has(u), (u, d, blocked) => { if (blocked) return false; n++; return n >= cap; }); return n; };
  function nearestHeads(c, tiles, skip, maxD) {
    const out = { A: null, B: null };
    bfs(tiles, maxD, u => { const o = c.occ.get(u); return o === undefined || skip.has(o); }, (u, d, blocked) => {
      if (!blocked) return false;
      const o = c.occ.get(u); if (o === undefined || skip.has(o)) return false;
      const od = c.drag.get(o); if (!od || K(od.body[0]) !== u) return false;
      if (!out[od.team]) out[od.team] = { id: od.id, d, len: od.body.length };
      return out.A && out.B;
    });
    return out;
  }
  function snapshot(c, r) { const a = []; for (const d of c.drag.values()) a.push({ id: d.id, team: d.team, body: Int32Array.from(d.body.map(K)) }); G.snaps.set(r, a); }

  // a long dragon X with shorter enemy heads (<=4) near: which of its single steps land inside an enemy sprint reach (len-1)
  function exposure(c, X, r) {
    const LX = X.body.length, hx = K(X.body[0]);
    const thr = [];
    for (const Y of c.drag.values()) {
      if (Y.team === X.team) continue;
      const LY = Y.body.length; if (LY > 4 || LY >= LX) continue;
      if (tdk(K(Y.body[0]), hx) <= 5) thr.push(Y);
    }
    if (!thr.length) return;
    const singles = [];
    for (let i = 0; i < 4; i++) { const u = NB[hx * 4 + i]; if (u >= 0 && !c.occ.has(u)) singles.push(u); }
    const margin = new Map(singles.map(u => [u, 99]));
    let minTd = 99; const ids = [];
    for (const Y of thr) {
      const reach = Y.body.length - 1, hy = K(Y.body[0]);
      minTd = Math.min(minTd, tdk(hy, hx)); ids.push(Y.id);
      bfs([hy], 5, u => !c.occ.has(u), (u, d, blocked) => { if (!blocked && margin.has(u)) margin.set(u, Math.min(margin.get(u), d - reach)); return false; });
    }
    const thrd = singles.filter(u => margin.get(u) <= 0).length;
    const tail = K(X.body[LX - 1]); let tailE = 99;
    for (const Y of c.drag.values()) if (Y.team !== X.team) tailE = Math.min(tailE, tdk(K(Y.body[0]), tail));
    G.expo.push({ r, id: X.id, team: X.team, L: LX, minTd, singles: singles.length, thrd, all: singles.length > 0 && thrd === singles.length, ids, tailE, resp: null });
  }
  function longStat(c, X, r) {
    const hx = K(X.body[0]), LX = X.body.length;
    const key = X.team + '|' + (R500.has(task.map) ? 'r500' : 'elim') + '|' + (r < 250 ? 'r0-249' : 'r250+');
    const o = G.longStats[key] || (G.longStats[key] = { turns: 0, e3: 0, e5: 0, a3any: 0 });
    let e3 = 0, e5 = 0, a3 = 0;
    for (const Y of c.drag.values()) {
      if (Y === X) continue;
      const td = tdk(K(Y.body[0]), hx);
      if (Y.team !== X.team) { if (Y.body.length <= 4 && Y.body.length < LX) { if (td <= 3) e3++; if (td <= 5) e5++; } }
      else if (td <= 3) a3++;
    }
    o.turns++; if (e3) o.e3++; if (e5) o.e5++; if (a3) o.a3any++;
  }

  const hooks = {
    turn(d, r, c) {
      if (!NB) initGeo(c);
      if (r !== lastR) { snapshot(c, r); lastR = r; }
      G.lastTurn.set(d.id, { r, nb: nbString(c, d), len: d.body.length });
      if (d.body.length >= 6) { exposure(c, d, r); longStat(c, d, r); }
    },
    indicator(e, r, c) { if (!online) return; const d = c.drag.get(e.id); if (d && d.team === us) G.ind.set(e.id + ':' + r, e.text); },
    action(d, e, r, c, before) {
      const a = e.action || {};
      const rec = { r, id: d.id, team: d.team, kind: a.kind || null, steps: d.steps, portal: d.portalSteps || 0, ate: d.ateThisAct, lenB: before.length, lenA: d.body.length,
        hB: K(before[0]), hA: K(d.body[0]), tB: K(before[before.length - 1]), fate: d.fate ? d.fate.reason : null };
      if (a.kind === 'split') rec.split = a.childSegmentCount;
      if (a.kind === 'move') {
        let h = before[0]; const tiles = [], exits = [];
        const n = d.fate ? d.fate.step : a.steps.length;
        for (let i = 0; i < n; i++) {
          const di = DIRS.indexOf(a.steps[i]), k = K(h), u = NB[k * 4 + di]; if (u < 0) break;
          tiles.push(u); if (PORT[k * 4 + di]) exits.push(u); h = { x: kx(u), y: ky(u) };
        }
        rec.tiles = tiles; rec.exits = exits;
      }
      const ours = online && d.team === us;
      if (ours || rec.portal || before.length >= 5) {
        const near = [];
        for (const o of c.drag.values()) {
          if (o === d) continue;
          const oh = K(o.body[0]), td = tdk(oh, rec.hB);
          if (td <= 8) { let vis = 0, tailVis = 0; o.body.forEach((sg, i) => { if (chk(K(sg), rec.hB) <= 3) { vis++; if (i === o.body.length - 1) tailVis = 1; } });
            near.push([o.id, o.team, o.body.length, oh, td, chk(oh, rec.hB), o.born, vis, tailVis]); }
        }
        rec.near = near;
        let tailE = 99; for (const o of c.drag.values()) if (o.team !== d.team) tailE = Math.min(tailE, tdk(K(o.body[0]), rec.tB));
        rec.tailE = tailE;
        // occupied tiles around the head at this decision (before the move), incl. our own body as it stood
        const occ = []; const hx = kx(rec.hB), hy = ky(rec.hB);
        for (let dy = -6; dy <= 6; dy++) for (let dx = -6; dx <= 6; dx++) { const k = (((hy + dy) % H + H) % H) * W + (((hx + dx) % W + W) % W); if (c.occ.has(k) && c.occ.get(k) !== d.id) occ.push(k); }
        for (const sg of before) occ.push(K(sg));
        rec.occ = occ;
        if (rec.steps >= 2 || rec.portal || rec.kind === 'split') {
          rec.area = rec.kind === 'move' && !d.fate ? areaFrom(c, rec.hA, 40) : null;
          if (rec.portal && rec.exits.length) {
            const ex = rec.exits[rec.exits.length - 1]; let eE = 99, eEL = 0, eA = 99;
            for (const o of c.drag.values()) { if (o === d) continue; const td = tdk(K(o.body[0]), ex); if (o.team !== d.team) { if (td < eE) { eE = td; eEL = o.body.length; } } else eA = Math.min(eA, td); }
            rec.exitE = eE; rec.exitEL = eEL; rec.exitA = eA;
          }
        }
      }
      if (rec.portal) G.portalActs.push(rec);
      G.acts.set(d.id + ':' + r, rec);
      const ex = G.expo.length ? G.expo[G.expo.length - 1] : null;
      if (ex && ex.id === d.id && ex.r === r && !ex.resp) ex.resp = { kind: rec.kind, steps: rec.steps, died: !!d.fate };
    },
    eat(d, k, o, r, c) {
      if (o >= 0) { let a = G.dropEaten.get(o); if (!a) G.dropEaten.set(o, a = []); a.push([d.id, d.team, r, d.body.length, c.isKingNow(d) ? 1 : 0]); }
    },
    split(p, ch, e, r, c) {
      let eH = 99; const chH = K(ch.body[0]);
      for (const o of c.drag.values()) if (o.team !== p.team) eH = Math.min(eH, tdk(K(o.body[0]), chH));
      const s = { r, parent: p.id, child: ch.id, team: p.team, pLen: p.body.length, cLen: ch.body.length, cHead: chH, eHead: eH, terr: c.terr[chH] };
      G.splits.push(s); G.splitOf.set(p.id + ':' + r, s);
    },
    death(d, rec, idx, other, r, c) {
      const body = d.body.map(K), drops = []; for (let i = 0; i < body.length; i += 2) drops.push(body[i]);
      const kE = c.kingOf(d.team === 'A' ? 'B' : 'A');
      const skip = new Set([d.id]); if (other && rec.cause >= 2 && rec.cause <= 3) skip.add(other.id);
      const col = nearestHeads(c, drops, skip, 14);
      const x = { idx, r, id: d.id, team: d.team, cause: rec.cause, len: rec.len, drops: rec.drops, head: body[0], rec, get pair() { return this.rec.pair; },
        king: rec.king, born: d.born, parent: d.parent, turn: G.lastTurn.get(d.id) || null, text: G.ind.get(d.id + ':' + r) || null, terr: c.terr[body[0]],
        killer: other ? { id: other.id, team: other.team, len: other.body.length, steps: other.steps || 0, portal: other.portalSteps || 0, born: other.born, isKing: kE === other ? 1 : 0 } : null,
        colOwn: col[d.team], colEnemy: col[d.team === 'A' ? 'B' : 'A'] };
      G.deaths.push(x); G.deathOf.set(d.id, x);
    },
    end(n, c) { G.rounds = n; G.final = [...c.drag.values()].map(x => ({ id: x.id, team: x.team, len: x.body.length })); G.all = c.all; },
  };
  const merge = (a, b) => { const h = {}; for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) h[k] = (...args) => { if (a[k]) a[k](...args); if (b[k]) b[k](...args); }; return h; };
  let res;
  if (online) {
    const { analyse } = require(path.join(ROOT, 'tools', 'mech_check.js'));
    res = analyse(R, task, (R2, info, h) => perGame(R2, info, merge(h, hooks)));
  } else {
    const info = { map: task.map }; if (task.map === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
    const g = perGame(R, info, hooks);
    res = { map: info.variant === 'PD10' ? 'Prisoners Dilemma (10)' : task.map, recs: [], chk: g.chk };
  }
  return derive(G, res, task, { us, them, sideOf, tdk, NB, PORT, W, H });
}

// ---------------------------------------------------------------------------------------------------------------
function derive(G, res, task, X) {
  const { us, them, sideOf, tdk } = X;
  const online = task.mode === 'online';
  const INF = 1e9, rounds = G.rounds;
  const life = new Map(); for (const [id, d] of G.all) life.set(id, { id, team: d.team, born: d.born, parent: d.parent });
  const kids = new Map(); for (const L of life.values()) if (L.parent >= 0) { if (!kids.has(L.parent)) kids.set(L.parent, []); kids.get(L.parent).push(L.id); }
  const deathR = id => { const z = G.deathOf.get(id); return z ? z.r : INF; };
  const aliveAt = (id, t) => { const L = life.get(id); return !!L && L.born <= t && deathR(id) > t; };
  const family = (root, t) => { const out = []; const st = [root]; while (st.length) { const id = st.pop(); const L = life.get(id); if (!L || L.born > t) continue; out.push(id); for (const k of kids.get(id) || []) st.push(k); } return out; };
  const famAlive = (root, t) => family(root, Math.min(t, rounds - 1)).some(id => aliveAt(id, Math.min(t, rounds - 1)));
  const finalIds = new Set(G.final.map(f => f.id)), finalLen = new Map(G.final.map(f => [f.id, f.len]));
  const famAliveEnd = root => family(root, INF).some(id => finalIds.has(id));
  const famLenAt = (root, t) => { if (t >= rounds) return family(root, INF).reduce((s, id) => s + (finalLen.get(id) || 0), 0);
    const snap = G.snaps.get(t) || []; const m = new Map(snap.map(e => [e.id, e.body.length])); return family(root, t).reduce((s, id) => s + (m.get(id) || 0), 0); };
  const finalKing = team => { let k = null; for (const f of G.final) if (f.team === team && (!k || f.len > k.len || (f.len === k.len && f.id < k.id))) k = f; return k; };
  const ancestors = id => { const a = []; for (let x = life.get(id); x; x = x.parent >= 0 ? life.get(x.parent) : null) a.push(x.id); return a; };
  const lineOf = { A: new Set(finalKing('A') ? ancestors(finalKing('A').id) : []), B: new Set(finalKing('B') ? ancestors(finalKing('B').id) : []) };
  const snapAt = r => { let s = G.snaps.get(r); while (!s && r > 0) s = G.snaps.get(--r); return s || []; };
  const headAt = (id, r) => { const s = snapAt(r).find(e => e.id === id); return s ? { h: s.body[0], len: s.body.length } : null; };
  const unitsAt = (team, r) => snapAt(r).filter(e => e.team === team).length;
  const kingAt = (team, r, exclude) => { let k = null; for (const e of snapAt(r)) if (e.team === team && e.id !== exclude && (!k || e.body.length > k.body.length || (e.body.length === k.body.length && e.id < k.id))) k = e; return k; };
  const label = (id, r) => G.ind.get(id + ':' + r) || null;
  const dz = z => z ? { r: z.r, cause: z.cause, len: z.len, killer: z.killer, nb: z.turn ? z.turn.nb : null, text: z.text, terr: z.terr, colOwn: z.colOwn, colEnemy: z.colEnemy } : null;
  const eatenBy = idx => G.dropEaten.get(idx) || [];
  const meta = { key: task.key, game: task.gameId, set: task.set, mode: task.mode, map: res.map, opp: task.opp, us: online ? us : null, rounds, ourWin: task.ourWin, teamA: task.teamA, teamB: task.teamB, chk: res.chk };
  const out = { meta, mech: null, rams: [], agg: {} };
  const recs = res.recs || [];
  const trace = (a, b, r0, r1) => { const t = []; for (let r = r0; r <= r1; r++) { const x = headAt(a, r), y = headAt(b, r); t.push(x && y ? tdk(x.h, y.h) : null); } return t; };

  if (online) {
    const M = { esc: [], feed: [], gather: [], portal: [], trade: [], split: [] };
    // ---- escape sprints (esc) and 2-step threat sprints (sprintEsc)
    for (const x of recs) {
      if (x.k !== 'esc' && x.k !== 'sprintEsc') continue;
      const act = G.acts.get(x.id + ':' + x.r) || {};
      const own = G.deathOf.get(x.id);
      const fam = family(x.id, x.r + 10).filter(id => id !== x.id);
      const o = { k: x.k, r: x.r, id: x.id, L: x.L, steps: x.steps, ok: x.ok, ex: x.ex, alive10: x.alive10, self10: x.self10,
        tailE: act.tailE, area: act.area, text: label(x.id, x.r), fam10L: famLenAt(x.id, x.r + 10), fam30L: famLenAt(x.id, x.r + 30),
        near: (act.near || []).filter(n => n[1] !== us).map(n => ({ id: n[0], len: n[2], td: n[4], cheb: n[5] })),
        death: own && own.r <= x.r + 10 ? dz(own) : null, famDeaths: fam.map(id => G.deathOf.get(id)).filter(z => z && z.r <= x.r + 10).length };
      if (o.death && o.death.killer) {
        const kid = o.death.killer.id, n = (act.near || []).find(q => q[0] === kid);
        o.killerAtEsc = n ? { td: n[4], cheb: n[5], len: n[2] } : null;
        o.killerBorn = (life.get(kid) || {}).born;
        o.killerHist = trace(x.id, kid, Math.max(0, x.r - 5), x.r);
        o.trace = trace(x.id, kid, x.r, o.death.r);
        const ka = G.acts.get(kid + ':' + o.death.r) || {}; o.killerLenB = ka.lenB;
        const k0 = headAt(kid, x.r + 1); o.killerLenAfterEsc = k0 ? k0.len : null;
      }
      o.ourPortal = 0; for (let r = x.r + 1; r <= Math.min(x.r + 10, rounds); r++) { const a = G.acts.get(x.id + ':' + r); if (a && a.portal) o.ourPortal++; }
      M.esc.push(o);
    }
    // ---- feed
    for (const x of recs) {
      if (x.k !== 'feed') continue;
      const t = x.target, tz = G.deathOf.get(t), kAt = kingAt(us, x.r, x.id);
      let tLoop = 0, tFeeds = 0; const tFam = family(t, INF);
      for (const id of tFam) for (let r = x.r; r < rounds; r++) { const s = label(id, r); if (!s) continue; if (s.startsWith('escape-split')) tLoop++; else if (s.startsWith('feed')) tFeeds++; }
      const fa = G.acts.get(x.id + ':' + x.r);
      const o = { r: x.r, id: x.id, L: x.L, target: t, tLen: x.tLen, dist: x.dist, drops: x.drops, eatOwn: x.eatOwn, eatT: x.eatT, eatEnemy: x.eatEnemy, ok: x.ok,
        tAliveEnd: x.tAliveEnd, tFamEnd: famAliveEnd(t) ? 1 : 0, tIsFinalLine: lineOf[us].has(t) ? 1 : 0, tDeath: tz ? dz(tz) : null, tLoop, tFeeds,
        kingIsTarget: kAt && kAt.id === t ? 1 : 0, kingFamEnd: kAt && famAliveEnd(kAt.id) ? 1 : 0, kingIsFinalLine: kAt && lineOf[us].has(kAt.id) ? 1 : 0,
        kingDistFromFeeder: fa && kAt ? tdk(fa.hB, kAt.body[0]) : null };
      if (tz && tz.killer) { const ek = kingAt(them, tz.r); o.tKillerIsEnemyKing = ek && ek.id === tz.killer.id ? 1 : 0; }
      M.feed.push(o);
    }
    // ---- gathering (g label)
    for (const x of recs) {
      if (x.k !== 'gather') continue;
      const r0 = x.r, r1 = x.r + x.turns - 1;
      let next = null;
      for (let r = r1 + 1; r <= Math.min(rounds - 1, r1 + 3); r++) { const s = label(x.id, r); if (s) { next = s; break; } }
      const z = G.deathOf.get(x.id), gk = kingAt(us, r0 + 1, x.id), a0 = G.acts.get(x.id + ':' + r0), me0 = a0 ? { h: a0.hB } : headAt(x.id, r0 + 1);
      const k1 = kingAt(us, r1 + 1, -1);
      const o = { r0, r1, id: x.id, L: x.L, d0: x.d0, dMin: x.dMin, turns: x.turns, fed: x.fed, loop: x.loop, aliveEnd: x.aliveEnd, ok: x.ok,
        death: z && !x.fed && !x.loop ? dz(z) : null, next: next ? next.split('|')[0].trim() : null,
        unitsAfter: unitsAt(us, Math.min(rounds - 1, r1 + 1)), lenAfter: (headAt(x.id, Math.min(rounds - 1, r1 + 1)) || {}).len || null,
        becameKing: k1 && k1.id === x.id ? 1 : 0, goalDiedR: gk && deathR(gk.id) < INF ? deathR(gk.id) : null,
        path: gk && me0 ? staticPath(X, G, me0.h, gk.body[0], us) : null, rounds };
      M.gather.push(o);
    }
    // ---- portal crossings (ours)
    for (const x of recs) {
      if (x.k !== 'portal') continue;
      const act = G.acts.get(x.id + ':' + x.r) || {}, z = G.deathOf.get(x.id);
      M.portal.push({ r: x.r, id: x.id, L: x.L, blind: x.blind, alive3: x.alive3, alive10: x.alive10, self3: x.self3, steps: act.steps, fate: act.fate,
        onStep: act.portal > (act.exits || []).length ? 1 : 0, exitE: act.exitE, exitA: act.exitA, area: act.area, text: label(x.id, x.r), death: z && z.r <= x.r + 10 ? dz(z) : null });
    }
    // ---- trades
    for (const x of recs) {
      if (x.k !== 'trade') continue;
      const z = G.deathOf.get(x.id);
      const o = { r: x.r, id: x.id, L: x.L, path: x.path, ex: x.ex, killed: x.killed, pUs: x.pUs, pThem: x.pThem, text: label(x.id, x.r) };
      if (x.ex && z) {
        const pz = z.pair >= 0 ? G.deaths.find(q => q.idx === z.pair) : null;
        o.our = { colOwn: z.colOwn, colEnemy: z.colEnemy };
        if (pz) o.their = { id: pz.id, len: pz.len, colOwn: pz.colOwn, colEnemy: pz.colEnemy };
      }
      M.trade.push(o);
    }
    // ---- policy split children
    for (const x of recs) {
      if (x.k !== 'split' || !x.ex) continue;
      const s = G.splitOf.get(x.id + ':' + x.r); if (!s) continue;
      const cz = G.deathOf.get(s.child);
      const o = { r: x.r, id: x.id, L: x.L, child: s.child, cLen: s.cLen, eHead: s.eHead, units: x.units, terrBirth: s.terr === (us === 'A' ? 1 : 2) ? 'own' : s.terr === 0 ? 'neutral' : 'enemy',
        alive30: x.childAlive30, childFam30: famAlive(s.child, x.r + 30) ? 1 : 0, childFamLen30: famLenAt(s.child, x.r + 30), death: cz ? dz(cz) : null, deathAge: cz ? cz.r - x.r : null };
      if (cz) {
        o.terrDeath = cz.terr === (us === 'A' ? 1 : 2) ? 'own' : cz.terr === 0 ? 'neutral' : 'enemy';
        const ph = headAt(x.id, cz.r); o.parentDist = ph ? tdk(ph.h, cz.head) : null;
        if (cz.killer) { const kl = life.get(cz.killer.id); o.killerAge = kl ? cz.r - kl.born : null; }
        o.eatenOwn = eatenBy(cz.idx).map(e => e[1] === us ? 'us' : 'them');
        if (cz.pair >= 0) { const pz = G.deaths.find(q => q.idx === cz.pair); if (pz) o.pairEaten = eatenBy(pz.idx).map(e => e[1] === us ? 'us' : 'them'); }
        o.portalBefore = 0; o.blindBefore = 0; o.lastCross = null;
        for (let r = x.r; r <= cz.r; r++) { const a = G.acts.get(s.child + ':' + r); if (a && a.portal) { o.portalBefore++; o.lastCross = r; const t = label(s.child, r); if (t && t.includes('PORTAL?')) o.blindBefore++; } }
      }
      M.split.push(o);
    }
    out.mech = M;
  }

  // ---- rams: head-on deaths of dragons of length >= 6 (either side) and all of ours: what the victim could know
  for (const z of G.deaths) {
    if (z.cause !== 2 || !z.killer) continue;
    const mine = online && z.team === us;
    if (!mine && z.len < 6) continue;
    const ka = G.acts.get(z.killer.id + ':' + z.r) || {};
    const ourR = z.id < z.killer.id ? z.r : z.r - 1, oa = G.acts.get(z.id + ':' + ourR) || {};
    const n = (oa.near || []).find(q => q[0] === z.killer.id);
    // shadowing: rounds in the 10 before the strike with the killer's head within 5 of the victim's; the killer's growth
    let shadow = 0, kLen10 = null; for (let t = Math.max(0, z.r - 10); t < z.r; t++) { const a = headAt(z.id, t), b = headAt(z.killer.id, t); if (a && b && tdk(a.h, b.h) <= 5) shadow++; if (b && kLen10 === null) kLen10 = b.len; }
    const rec = { side: sideOf(z.team), r: z.r, id: z.id, killerId: z.killer.id, len: z.len, king: z.king, born: z.born, text: mine ? label(z.id, ourR) : null, shadow, killerLen10: kLen10,
      killerLenB: ka.lenB, killerSteps: z.killer.steps, killerAte: ka.ate, killerPortal: ka.portal, killerBorn: z.killer.born,
      atDecision: n ? { td: n[4], cheb: n[5], vis: n[7], tailVis: n[8], len: n[2] } : null, hasDecision: oa.hB !== undefined ? 1 : 0,
      distToNewHead: ka.hB !== undefined && oa.hA !== undefined ? tdk(ka.hB, oa.hA) : null };
    if (oa.occ && ka.tiles) { const occ = new Set(oa.occ); rec.pathThroughOcc = ka.tiles.filter(t => occ.has(t)).length; rec.newHeadWasOcc = oa.hA !== undefined && occ.has(oa.hA) ? 1 : 0; }
    if (rec.distToNewHead !== null && oa.near) rec.masked = oa.near.some(q => q[1] !== z.team && q[0] !== z.killer.id && tdk(q[3], oa.hA) < rec.distToNewHead && q[2] - 1 < tdk(q[3], oa.hA)) ? 1 : 0;
    const pz = z.pair >= 0 ? G.deaths.find(q => q.idx === z.pair) : null;
    const E = eatenBy(z.idx).concat(pz ? eatenBy(pz.idx) : []);
    rec.eatVictimTeam = E.filter(e => e[1] === z.team).length; rec.eatKillerTeam = E.filter(e => e[1] !== z.team).length;
    rec.colVictimTeam = z.colOwn ? z.colOwn.d : null; rec.colKillerTeam = z.colEnemy ? z.colEnemy.d : null;
    out.rams.push(rec);
  }

  // ---- population counters per side
  const A = side => out.agg[side] || (out.agg[side] = { longTurns: {}, cornered: {}, corneredTail4: {}, headon: { n: 0, spr: 0, col: {} }, longVictim: { n: 0, lenLost: 0, kEat: 0, vEat: 0 },
    sac: {}, children: { n: 0, dead30: 0, causes: {} }, portal: {}, rammedLong: { n: 0 } });
  const hist = (o, k, v) => { const b = v === null || v === undefined ? 'x' : Math.min(v, 30); o[k] = o[k] || {}; o[k][b] = (o[k][b] || 0) + 1; };
  const inc = (o, k, v = 1) => { o[k] = (o[k] || 0) + v; };
  for (const [k, v] of Object.entries(G.longStats)) { const [team, mt, ph] = k.split('|'); const o = A(sideOf(team)).longTurns; const q = o[mt + '|' + ph] || (o[mt + '|' + ph] = { turns: 0, e3: 0, e5: 0, a3any: 0 }); for (const f of Object.keys(q)) q[f] += v[f]; }
  for (const e of G.expo) {
    if (!e.all) continue;
    const r = e.resp, k = !r ? 'none' : r.kind === 'split' ? 'split' : r.steps >= 3 ? 'sprint3' : r.steps === 2 ? 'sprint2' : 'single';
    const z = G.deathOf.get(e.id);
    for (const bucket of e.tailE >= 4 ? ['cornered', 'corneredTail4'] : ['cornered']) {
      const o = A(sideOf(e.team))[bucket]; const q = o[k] || (o[k] = { n: 0, L: 0, f10: 0, f30: 0, d10: 0, fd10: 0 });
      q.n++; q.L += e.L; q.f10 += famLenAt(e.id, e.r + 10); q.f30 += famLenAt(e.id, e.r + 30); if (z && z.r <= e.r + 10) q.d10++; if (!famAlive(e.id, e.r + 10)) q.fd10++;
    }
  }
  for (const z of G.deaths) {
    const S = A(sideOf(z.team)), E = eatenBy(z.idx);
    const own = E.filter(e => e[1] === z.team), en = E.filter(e => e[1] !== z.team);
    if (!z.killer && z.r >= 250) { // self-inflicted without hitting another dragon (reasons S, W, A): for the recount
      const q = S.selfNoHit || (S.selfNoHit = { n: 0, drops: 0, own: 0, enemy: 0 }); q.n++; q.drops += z.drops; q.own += own.length; q.enemy += en.length;
    }
    if (z.cause === 0) {
      const ph = z.r < 250 ? 'r0-249' : 'r250+';
      const s = S.sac[ph] || (S.sac[ph] = { n: 0, len: 0, drops: 0, own: 0, enemy: 0, withE: 0, eAlive: 0, eLine: 0, v23: 0, v47: 0, v8: 0 });
      s.n++; s.len += z.len; s.drops += z.drops; s.own += own.length; s.enemy += en.length;
      if (z.len <= 3) s.v23++; else if (z.len <= 7) s.v47++; else s.v8++;
      hist(s, 'colD', z.colOwn ? z.colOwn.d : null); hist(s, 'colL', z.colOwn ? z.colOwn.len : null);
      const ids = [...new Set(own.map(e => e[0]))];
      if (ids.length) { s.withE++; if (ids.some(id => famAliveEnd(id))) s.eAlive++; if (ids.some(id => lineOf[z.team].has(id))) s.eLine++; }
    }
    if (z.cause === 2 && z.pair >= 0) {
      const m = G.deaths.find(q => q.idx === z.pair); if (!m) continue;
      const Em = eatenBy(m.idx);
      const vEat = E.filter(e => e[1] === z.team).length + Em.filter(e => e[1] === z.team).length, kEat = E.filter(e => e[1] !== z.team).length + Em.filter(e => e[1] !== z.team).length;
      const dv = z.colOwn ? z.colOwn.d : 99, dm = z.colEnemy ? z.colEnemy.d : 99;
      const ck = dm === 99 && dv === 99 ? 'none' : dm <= dv ? 'killerNearer' : 'victimNearer';
      S.headon.n++; if (z.killer && z.killer.steps >= 2) S.headon.spr++;
      const q = S.headon.col[ck] || (S.headon.col[ck] = { n: 0, kEat: 0, vEat: 0, drops: 0 }); q.n++; q.kEat += kEat; q.vEat += vEat; q.drops += z.drops + m.drops;
      if (z.len >= 6 && m.len <= 4) { S.longVictim.n++; S.longVictim.lenLost += z.len; S.longVictim.kEat += kEat; S.longVictim.vEat += vEat; hist(S.longVictim, 'colK', dm === 99 ? null : dm); hist(S.longVictim, 'colV', dv === 99 ? null : dv); }
    }
  }
  for (const s of G.splits) {
    if (s.cLen > 3) continue;
    const c = A(sideOf(s.team)).children, cz = G.deathOf.get(s.child);
    c.n++; if (cz && cz.r <= s.r + 30) { c.dead30++; inc(c.causes, String(cz.cause)); }
  }
  for (const a of G.portalActs) {
    const z = G.deathOf.get(a.id), lc = a.lenB <= 3 ? 'L2-3' : a.lenB <= 7 ? 'L4-7' : 'L8+';
    const o = A(sideOf(a.team)).portal; const q = o[lc] || (o[lc] = { n: 0, self3: 0, onStep: 0, onStepOwn: 0, onStepEnemy: 0, body3: 0 });
    q.n++; if (!(z && z.r <= a.r + 3)) q.self3++; if (famAlive(a.id, a.r + 3)) q.body3++;
    if (a.portal > (a.exits || []).length && (a.fate === 'O' || a.fate === 'H')) { q.onStep++; if (z && z.killer) { if (z.killer.team === a.team) q.onStepOwn++; else q.onStepEnemy++; } }
  }
  return out;
}

// shortest path on the static map (kelp and portals; bodies ignored): length, portal crossings, share in enemy territory
function staticPath(X, G, a, b, us) {
  const { NB, PORT, W, H } = X; const N = W * H;
  const par = new Int32Array(N).fill(-1), pd = new Int8Array(N).fill(-1), dist = new Int32Array(N).fill(-1), q = [a]; dist[a] = 0;
  for (let i = 0; i < q.length; i++) { const k = q[i]; if (k === b) break; for (let d = 0; d < 4; d++) { const u = NB[k * 4 + d]; if (u < 0 || dist[u] >= 0) continue; dist[u] = dist[k] + 1; par[u] = k; pd[u] = d; q.push(u); } }
  if (dist[b] < 0) return { len: null };
  let portals = 0, enemy = 0, n = 0; const ourT = us === 'A' ? 1 : 2;
  for (let k = b; k !== a; k = par[k]) { const p = par[k]; if (PORT[p * 4 + pd[k]]) portals++; n++; if (G.terr[k] && G.terr[k] !== ourT) enemy++; }
  return { len: dist[b], portals, enemyFrac: n ? enemy / n : 0 };
}

// ---------------------------------------------------------------------------------------------------------------
// The loader of tools/top_features.js, minus the event kinds this study never reads (sonar pings, pearl countdowns, logs,
// debug draws): the same parse, 1.2-2.5x faster on top games. Checked equal on the mass-ledger output (dt, fl, chk).
function makeFastLoader() {
  const vm = require('vm'), zlib = require('zlib');
  const { viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const src = viewerSource(), cut = src.indexOf('var Af=B(');
  if (cut < 0) throw Error('unexpected replay-viewer build');
  const code = src.slice(0, cut).replace('if(n.formatVersion>1)', 'if(n.formatVersion>2)') + 'globalThis.__tf={Df:Df,bf:bf,Of:Of};})();';
  const ctx = { TextEncoder, TextDecoder }; vm.runInNewContext(code, ctx, { timeout: 5000 });
  const { Df, bf, Of } = ctx.__tf;
  const SKIP = new Set(['sonarPing', 'pearlCountdown', 'engineLog', 'dragonLog', 'debugDraw']);
  const skip = new Set(), keep = new Set();
  return function load(file) {
    const raw = fs.readFileSync(file);
    const root = Df(file.endsWith('.gz') ? zlib.gunzipSync(raw) : raw);
    const list = root.events, n = list.length, events = [];
    for (let i = 0; i < n; i++) {
      const ev = list.get(i), w = ev.which();
      if (skip.has(w)) continue;
      const o = bf(ev);
      if (!keep.has(w)) { if (SKIP.has(o.type)) { skip.add(w); continue; } keep.add(w); }
      events.push(o);
    }
    const R = Of(root, events); R.formatVersion = root.formatVersion; return R;
  };
}
function workerMain() {
  const load = makeFastLoader();
  const { recount } = require(path.join(__dirname, 'recount.js'));
  process.on('message', task => {
    try { const R = load(task.file); const o = study(R, task); o.recount = recount(R, task); process.send({ ok: true, key: task.key, line: JSON.stringify(o) }); }
    catch (err) { process.send({ ok: false, key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 5).join(' | ') }); }
  });
}
async function runAll(tasks, jobs, outFile) {
  const fd = fs.openSync(outFile, 'a'), q = tasks.slice(), errors = [], t0 = Date.now(); let done = 0;
  await Promise.all(Array.from({ length: Math.min(jobs, q.length) }, () => new Promise(resolve => {
    const w = cp.fork(__filename, ['--worker'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'], execArgv: ['--max-old-space-size=3072'] });
    const next = () => { const t = q.shift(); if (!t) { w.kill(); resolve(); return; } w.send(t); };
    w.on('message', m => {
      if (m.ok) fs.writeSync(fd, m.line + '\n'); else { errors.push(m); console.error('error', m.key, m.error); }
      if (++done % 200 === 0) console.log(`  ${done}/${tasks.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
      next();
    });
    w.on('exit', code => { if (q.length) console.error('worker exited', code); });
    next();
  })));
  fs.closeSync(fd);
  return errors;
}
async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
  const mode = argv[0], outFile = opt('--out') && path.resolve(opt('--out'));
  if (!outFile || !['online', 'top'].includes(mode)) { console.error('usage: collect.js online <set+set> --out f.jsonl [--jobs 4] | collect.js top --out f.jsonl [--jobs 4] [--limit N]'); process.exit(2); }
  let tasks = mode === 'online' ? onlineTasks(argv[1]) : topTasks();
  const done = new Set();
  if (fs.existsSync(outFile)) for (const l of fs.readFileSync(outFile, 'utf8').split('\n')) { const m = /"key":"([^"]+)"/.exec(l); if (m) done.add(m[1]); }
  tasks = tasks.filter(t => !done.has(t.key));
  if (opt('--limit')) tasks = tasks.slice(0, +opt('--limit'));
  const jobs = Math.min(4, +opt('--jobs', 4));
  console.log(`${mode}: ${tasks.length} games to do (${done.size} already in ${path.basename(outFile)}), jobs ${jobs}`);
  const t0 = Date.now();
  const errors = await runAll(tasks, jobs, outFile);
  console.log(`done in ${((Date.now() - t0) / 1000).toFixed(0)}s, errors ${errors.length}`);
}
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
module.exports = { study, makeFastLoader };
