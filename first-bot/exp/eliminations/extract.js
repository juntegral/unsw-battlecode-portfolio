#!/usr/bin/env node
// How teams get eliminated, and what surviving losers do differently. Replays only: no games, no network.
// Written for research/observations/our-eliminations.md (2026-09-30).
//
// usage (repository root):
//   node exp/eliminations/extract.js keys [--out exp/eliminations/top-<stamp>.keys]
//       Snapshot of data/top: every unique battle:game with a replay file (the fixed top population of this study).
//   node exp/eliminations/extract.js top --keys <file> [--jobs 4] [--limit N]
//   node exp/eliminations/extract.js online <set> [<set> ...] [--jobs 4]
//   node exp/eliminations/extract.js one <online set> <gameId>        prints one game's record (debug)
//   Cache: exp/eliminations/cache/top.jsonl.gz and cache/online-<set>.jsonl.gz, one gzip member (one JSON line) per game.
//   Games already in a cache file are skipped.
//
// Reconstruction: tools/mass_ledger.js perGame() with hooks (moves, sprints, portals, splits, deaths by cause; its checks
// are kept in the record and must stay 0). Definitions (fixed before any result was looked at):
//   View      = Chebyshev distance <= 3 on the torus (a dragon's 7x7 window).
//   eV / aV   = enemy / other ally heads in the view of a dragon at the start of its turn.
//   Swarm turn = a turn of a dragon with eV >= 2 and eV > aV (outnumbered by enemy heads in its own view).
//     Response: split | ram (its move ended in a head-on with an enemy head) | sprint (2+ steps) | step | none.
//     Away: the smallest Chebyshev distance from our head to those enemy heads (their positions at our turn start) grew (+1),
//     shrank (-1) or stayed (0). Outcome: the dragon alive 10 rounds later (a10); the dragon or a descendant born after the
//     turn alive 10 rounds later (f10).
//   Death context = the dying dragon's last turn start (for a ram victim that is its last decision): eV, aV, nearest enemy
//     head (torus Manhattan). Swarm death = eV >= 2 at that moment.
//   Killer steps (ks): steps the mover actually made in the move that killed (rammed: the enemy's move; ram: ours).
//   Death classes of the ledger (cause index): 0 sac, 1 trap, 2 rammed, 3 ram, 4 enemyBody, 5 allyHead, 6 fault, 7 sprintDeath.
//   Death mech (the ledger's): 1 stub (split within 2 rounds keeping <= 3 segments: an escape-split loop's stub), 2 newborn, 0 other.
//   Death rows: [r, len, cause, ks, eV, aV, king, killerLen, killerAge, ownUnits, enemyUnits, blk, eMin, portalSteps, mech].
//   King = the team's longest living dragon at that moment (ties -> lowest id), as in the ledger.
//   Series: units / total length / longest at the first turn of each round (online: every round; top: every 5 rounds), and
//     the final state. Elimination round = round of the team's last death when it ends with 0 dragons.
//   Position (every 10 rounds, first turn of the round): heads in own / neutral / enemy territory (the ledger's static
//     split), mean nearest-ally and nearest-enemy head distance (torus Manhattan, capped at 30), heads with an ally / an
//     enemy head within 3, heads on corridor tiles (at most 2 open edges; kelp and portals as in the ledger).
//   Pearl layout: tools/mech_check.js layoutTruth (natural spawns on tiles that never spawn in the other layout; PD by start
//     dragons) and exp/territory-analysis variantOf (variants.json, else spawn counts) side by side.
//   Our labels (online, our team only): INDICATOR text of each turn tokenised (see tokens()); counts per 10-round bin, and
//     the dying dragon's last label.
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), cp = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const TOP = path.join(ROOT, 'data', 'top'), ONLINE = path.join(ROOT, 'data', 'online');
const CACHE = path.join(__dirname, 'cache');
const TEAMS = ['A', 'B'];
const PH = [0, 30, 50, 100, 200, 300, 400, 501]; // phases for aggregated deaths / splits
const phaseIdx = r => { for (let i = PH.length - 2; i >= 0; i--) if (r >= PH[i]) return i; return 0; };
const lcOf = L => L <= 2 ? 0 : L <= 4 ? 1 : L <= 7 ? 2 : L <= 14 ? 3 : 4; // 2 | 3-4 | 5-7 | 8-14 | 15+

// ---------------------------------------------------------------------------------------------------------------
// Pearl layout: the same rule as tools/mech_check.js layoutTruth (copied; that function is not exported)
const LAYOUT_FILES = { 'Devil': ['devil', 'devil_b'], 'Queen Of Spades': ['queen_of_spades', 'queen_of_spades_b'], 'Schooltime': ['schooltime', 'schooltime_b'],
  'Slithery Fight': ['slithery_fight', 'slithery_fight_b'], 'Prisoners Dilemma': ['prisoners_dilemma', 'prisoners_dilemma_10'] };
const layoutTables = new Map();
function spawnTable(file) {
  if (!layoutTables.has(file)) {
    const L = fs.readFileSync(file, 'utf8').split('\n'), m = /^MAP (\d+) (\d+)/.exec(L[0]), W = +m[1], on = new Uint8Array(W * +m[2]);
    for (const l of L) if (l.startsWith('TILE ')) { const [x, y, , mx] = l.trim().split(/\s+/).slice(1).map(Number); on[y * W + x] = mx > 0 ? 1 : 0; }
    layoutTables.set(file, on);
  }
  return layoutTables.get(file);
}
function layoutTruth(R, mapName) {
  const M = R.match.map, f = LAYOUT_FILES[mapName];
  if (!f) return 'a';
  if (mapName === 'Prisoners Dilemma') return M.initialDragons.length === 10 ? 'b' : 'a';
  const a = spawnTable(path.join(ROOT, 'maps', 'online-20260927', f[0] + '.map')), b = spawnTable(path.join(ROOT, 'maps', 'variants', f[1] + '.map'));
  if (a.length !== M.width * M.height) return '?';
  let evA = 0, evB = 0, rs = false;
  for (const e of R.events) {
    if (e.type === 'roundStart') rs = true; else if (e.type === 'turnStart') rs = false;
    else if (rs && e.type === 'tileChange' && e.hasPearl) { const k = e.tile.y * M.width + e.tile.x; if (a[k] && !b[k]) evA++; else if (b[k] && !a[k]) evB++; }
  }
  return evA && !evB ? 'a' : evB && !evA ? 'b' : evA && evB ? 'x' : '?';
}

// ---------------------------------------------------------------------------------------------------------------
// Our INDICATOR labels (bot/plan.cpp decide(), exp/cand-stack4/bot/plan.cpp): one base kind + modifiers
function tokens(s) {
  if (!s) return ['none'];
  let m;
  if ((m = /^feed #(\d+) d(\d+) L(\d+)( conv)?/.exec(s))) return [m[4] ? 'conv' : 'feed'];
  if (/^pocket-eat/.test(s)) return ['pocket'];
  if (/^escape-split/.test(s)) return ['escsplit'];
  if (/^esc-split/.test(s)) return ['escsplit2'];
  if (/^csplit/.test(s)) return ['csplit'];
  if (/^split/.test(s)) return [/ frag(?:\s|$)/.test(s) ? 'frag' : / bsp(?:\s|$)/.test(s) ? 'bsplit' : 'split'];
  if (s.startsWith('last-trade')) return ['lasttrade'];
  if (s.startsWith('no-exit')) return ['noexit'];
  if (s.startsWith('degraded')) return ['degraded'];
  if ((m = /^([NESW]+) v(\S+) d(\d+) L(\d+)(.*)$/.exec(s))) {
    const out = ['move', m[1].length >= 2 ? 'multi' : 'single'];
    const v = +m[2]; if (v <= -200) out.push('doom'); else if (v < 0) out.push('vneg');
    for (const t of m[5].split('|')[0].trim().split(/\s+/).filter(Boolean)) {
      if (/^[Kg]\d+$/.test(t)) out.push(t[0]);
      else if (/^grab@/.test(t)) out.push('grab');
      else if (/^F\d+@/.test(t)) out.push('F');
      else if (t.startsWith('map=')) out.push('map');
      else if (['TRADE', 'PORTAL?', 'late', 'esc', 'T', 'ram4', 'ram4o', 'c1', 'c0', 'ks', 'ks2', 'tg', 'tgx', 'px', 'pxx', 'gx', 'sx', 'cov'].includes(t)) out.push(t);
      else out.push('x:' + t.slice(0, 12));
    }
    return out;
  }
  return ['other:' + s.split(/\s+/)[0].replace(/[#\d]+$/, '').slice(0, 16)];
}

// ---------------------------------------------------------------------------------------------------------------
// One game
function analyse(R, task, perGame) {
  const M = R.match.map, nInit = M.initialDragons.length;
  const info = { map: task.map };
  if (task.map === 'Prisoners Dilemma') info.variant = nInit === 10 ? 'PD10' : 'PD6';
  const online = task.src === 'online', us = task.us || null;
  const STEP = online ? 1 : 5;
  let geo = null; // static tile degree (open edges), computed on the first turn
  const T = {};
  for (const tm of TEAMS) T[tm] = {
    ser: { u: [], t: [], k: [] }, pos: [], spl: new Array(50).fill(0), splC: new Array(50).fill(0), splV: new Array(PH.length - 1).fill(0),
    dth: {}, last: [], sw: {}, turns: [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], swT: [0, 0, 0, 0, 0],
    faults: 0, elim: -1, firstDeath: -1, kd: [],
  };
  const ctxNow = new Map();   // dragon id -> context at its last turn start
  const swEp = [];            // swarm-turn episodes {tm, id, r, lc, resp, away}
  const pending = new Map();  // dragon id -> swarm episode of this turn (response filled in by the action hook)
  const deathR = new Map(), bornR = new Map(), parentOf = new Map(), kids = new Map();
  const deathsFull = [];      // online: every death of ours (objects)
  const oppDeaths = [];       // online: every death of the opponent [r, len, cause, ks, eV, aV, king, klen, kage, u, eu]
  const lab = online ? Array.from({ length: 51 }, () => ({})) : null; // our label tokens per 10-round bin
  const lastLbl = new Map();  // our dragon id -> { r, text }
  const lblRing = new Map();  // our dragon id -> last 4 [r, text]
  const ourDrg = online ? new Map() : null;
  let snapR = -1;
  const labelCount = online ? { turns: 0, labelled: 0 } : null;

  const snapshot = (r, c) => {
    for (const tm of TEAMS) {
      let u = 0, t = 0, k = 0;
      for (const o of c.drag.values()) if (o.team === tm) { u++; t += o.body.length; if (o.body.length > k) k = o.body.length; }
      const i = r / STEP; T[tm].ser.u[i] = u; T[tm].ser.t[i] = t; T[tm].ser.k[i] = k;
    }
  };
  const posSnap = (r, c) => {
    const heads = { A: [], B: [] };
    for (const o of c.drag.values()) heads[o.team].push(o.body[0]);
    for (const tm of TEAMS) {
      const own = tm === 'A' ? 1 : 2, H = heads[tm], E = heads[tm === 'A' ? 'B' : 'A'];
      let nOwn = 0, nNeu = 0, nEn = 0, sA = 0, a3 = 0, sE = 0, e3 = 0, cor = 0;
      for (let i = 0; i < H.length; i++) {
        const h = H[i], k = c.key(h.x, h.y), tt = c.terr[k];
        if (tt === 0) nNeu++; else if (tt === own) nOwn++; else nEn++;
        if (geo[k] <= 2) cor++;
        let da = 30; for (let j = 0; j < H.length; j++) if (j !== i) { const x = c.tdist(h, H[j]); if (x < da) da = x; }
        let de = 30; for (const g of E) { const x = c.tdist(h, g); if (x < de) de = x; }
        sA += da; sE += de; if (da <= 3) a3++; if (de <= 3) e3++;
      }
      T[tm].pos.push([r, H.length, nOwn, nNeu, nEn, H.length ? Math.round(10 * sA / H.length) : -1, a3, H.length ? Math.round(10 * sE / H.length) : -1, e3, cor]);
    }
  };

  const hooks = {
    turn(d, r, c) {
      if (!geo) {
        geo = new Uint8Array(c.W * c.H);
        for (let y = 0; y < c.H; y++) for (let x = 0; x < c.W; x++) { let n = 0; for (const s of ['N', 'E', 'S', 'W']) if (c.across(x, y, s)) n++; geo[y * c.W + x] = n; }
      }
      if (r !== snapR) {
        snapR = r;
        if (r % STEP === 0) snapshot(r, c);
        if (r % 10 === 0) posSnap(r, c);
      }
      if (!bornR.has(d.id)) { bornR.set(d.id, d.born); parentOf.set(d.id, d.parent); }
      // context: heads in view
      let eV = 0, aV = 0, eMin = 99; const eh = [];
      for (const o of c.drag.values()) {
        if (o === d) continue;
        const ch = c.cheb(o.body[0], d.body[0]);
        if (o.team !== d.team) { if (ch <= 3) { eV++; eh.push(o.body[0]); } const md = c.tdist(o.body[0], d.body[0]); if (md < eMin) eMin = md; }
        else if (ch <= 3) aV++;
      }
      const L = d.body.length, lc = lcOf(L), tm = T[d.team];
      tm.turns[lc][Math.min(eV, 4)]++;
      ctxNow.set(d.id, { r, eV, aV, eMin, L });
      if (eV >= 2 && eV > aV) {
        tm.swT[lc]++;
        const ep = { tm: d.team, id: d.id, r, lc, resp: 'none', away: 0, eh, h0: { x: d.body[0].x, y: d.body[0].y } };
        pending.set(d.id, ep); swEp.push(ep);
      } else pending.delete(d.id);
      if (online && d.team === us) {
        labelCount.turns++;
        if (!ourDrg.has(d.id)) ourDrg.set(d.id, { id: d.id, born: d.born, parent: d.parent, bornLen: L, maxLen: L, death: null, cause: null });
        const q = ourDrg.get(d.id); if (L > q.maxLen) q.maxLen = L;
      }
    },
    indicator(e, r, c) {
      if (!online) return;
      const d = c.drag.get(e.id); if (!d || d.team !== us) return;
      labelCount.labelled++;
      lastLbl.set(e.id, { r, text: e.text });
      { let q = lblRing.get(e.id); if (!q) lblRing.set(e.id, q = []); q.push([r, (e.text || '').slice(0, 48)]); if (q.length > 4) q.shift(); }
      const b = lab[Math.min(50, Math.floor(r / 10))];
      for (const t of tokens(e.text)) b[t] = (b[t] || 0) + 1;
    },
    action(d, e, r, c, before) {
      const ep = pending.get(d.id);
      if (!ep || ep.r !== r) return;
      pending.delete(d.id);
      const a = e.action || {};
      if (a.kind === 'split') ep.resp = 'split';
      else if (a.kind === 'move') {
        const f = d.fate;
        if (f && f.reason === 'H' && f.hitTeam !== d.team) ep.resp = 'ram';
        else ep.resp = d.steps >= 2 ? 'sprint' : 'step';
        const h1 = f ? null : d.body[0];
        if (h1) {
          let m0 = 99, m1 = 99;
          for (const g of ep.eh) { m0 = Math.min(m0, c.cheb(g, ep.h0)); m1 = Math.min(m1, c.cheb(g, h1)); }
          ep.away = m1 > m0 ? 1 : m1 < m0 ? -1 : 0;
        }
      } else ep.resp = 'none';
    },
    split(p, ch, e, r, c) {
      const tm = T[p.team], b = Math.min(49, Math.floor(r / 10));
      tm.spl[b]++; tm.splC[b] += ch.body.length;
      const cx = ctxNow.get(p.id); if (cx && cx.r === r && cx.eV > 0) tm.splV[phaseIdx(r)]++;
      bornR.set(ch.id, r); parentOf.set(ch.id, p.id);
      if (!kids.has(p.id)) kids.set(p.id, []); kids.get(p.id).push(ch.id);
    },
    death(d, rec, idx, other, r, c) {
      deathR.set(d.id, r);
      const tm = T[d.team];
      if (tm.firstDeath < 0) tm.firstDeath = r;
      if (rec.cause === 6) tm.faults++;
      const cx = ctxNow.get(d.id) || { r: -1, eV: 0, aV: 0, eMin: 99 };
      let u = 0, eu = 0; for (const o of c.drag.values()) { if (o.team === d.team) u++; else eu++; }
      let ks = 0, klen = 0, kage = -1, kid = -1;
      if (other) {
        kid = other.id; klen = other.body.length; kage = r - other.born;
        if (rec.cause === 2) ks = other.fate ? other.fate.step + 1 : other.steps;
      }
      if (rec.cause === 3) ks = d.fate ? d.fate.step + 1 : d.steps;
      const king = c.isKingNow(d) ? 1 : 0;
      const sw = cx.eV >= 2 ? 1 : 0;
      // mech (the ledger's rec.mech): 1 stub = it split within the last 2 rounds and kept <= 3 segments (an escape-split loop's
      // stub left in its dead end, or the front half of a 2+2 split); 2 newborn = born by a split within the last 2 rounds; 0 other
      const mech = rec.mech === 'stub' ? 1 : rec.mech === 'newborn' ? 2 : 0;
      const key = phaseIdx(r) + '|' + rec.cause + '|' + lcOf(rec.len) + '|' + sw + '|' + mech;
      const a = tm.dth[key] || (tm.dth[key] = [0, 0]); a[0]++; a[1] += rec.len;
      const row = [r, rec.len, rec.cause, ks, cx.eV, cx.aV, king, klen, kage, u, eu, rec.blk, cx.eMin, d.portalSteps || 0, mech];
      tm.last.push(row); if (tm.last.length > 6) tm.last.shift();
      if (rec.len >= 8) tm.kd.push(row); // every death of length >= 8 (row[6] = was the team's longest)
      if (online && d.team !== us) oppDeaths.push([...row.slice(0, 11), mech]);
      if (online && d.team === us) {
        const lb = lastLbl.get(d.id);
        const full = { r, tm: d.team, id: d.id, len: rec.len, cause: rec.cause, ks, eV: cx.eV, aV: cx.aV, eMin: cx.eMin, ctxR: cx.r, king, klen, kage, kid,
          u, eu, blk: rec.blk, near: rec.near, kdist: rec.kdist, born: d.born, parent: d.parent, portal: d.portalSteps || 0, drops: rec.drops, mech };
        full.lbl = lb ? lb.text.slice(0, 80) : null; full.lblR = lb ? lb.r : -1; full.lbls = lblRing.get(d.id) || [];
        deathsFull.push(full);
        if (ourDrg.has(d.id)) { const q = ourDrg.get(d.id); q.death = r; q.cause = rec.cause; }
      }
    },
    end(n, c) {
      for (const tm of TEAMS) {
        let u = 0, t = 0, k = 0;
        for (const o of c.drag.values()) if (o.team === tm) { u++; t += o.body.length; if (o.body.length > k) k = o.body.length; }
        T[tm].end = { u, t, k };
      }
    },
  };
  const g = perGame(R, info, hooks);
  const rounds = g.rounds;
  // elimination round = last death of a team ending with no dragons
  const lastDeath = { A: -1, B: -1 };
  for (const tm of TEAMS) for (const row of T[tm].last) if (row[0] > lastDeath[tm]) lastDeath[tm] = row[0];
  for (const tm of TEAMS) T[tm].elim = T[tm].end.u === 0 ? lastDeath[tm] : -1;
  // swarm outcomes
  const alive = (id, t) => { const dr = deathR.has(id) ? deathR.get(id) : Infinity; return dr > t; };
  const famAlive = (id, r0, t) => {
    const st = [id];
    while (st.length) {
      const x = st.pop(); const b = bornR.has(x) ? bornR.get(x) : 0;
      if (x !== id && (b < r0 || b > t)) continue;
      if (alive(x, t)) return true;
      for (const k of kids.get(x) || []) st.push(k);
    }
    return false;
  };
  for (const ep of swEp) {
    const t = ep.r + 10;
    const a10 = alive(ep.id, t) ? 1 : 0, f10 = a10 || famAlive(ep.id, ep.r, t) ? 1 : 0;
    const k = ep.lc + '|' + ep.resp + '|' + ep.away;
    const acc = T[ep.tm].sw[k] || (T[ep.tm].sw[k] = [0, 0, 0]); acc[0]++; acc[1] += a10; acc[2] += f10;
  }
  const out = {
    key: task.key, src: task.src, set: task.set || null, gameId: task.gameId, map: task.map, variant: info.variant || null, nInit, unitLimit: M.unitLimit,
    lay: layoutTruth(R, task.map), teamA: task.teamA, teamB: task.teamB, us, opp: task.opp || null, oppId: task.oppId || null,
    eloA: task.eloA || null, eloB: task.eloB || null, ranked: task.ranked || false, at: task.at || null,
    winner: R.result.winner || null, endReason: R.result.endReason, rounds, step: STEP, chk: g.chk,
    health: { A: { splits: g.A.splits, sonar: g.A.sonar }, B: { splits: g.B.splits, sonar: g.B.sonar } },
    ml: { A: { fl: pickFl(g.A.fl, online), lin: g.A.lin ? { len: g.A.lin.len, gen: g.A.lin.gen, born: g.A.lin.born } : null }, B: { fl: pickFl(g.B.fl, online), lin: g.B.lin ? { len: g.B.lin.len, gen: g.B.lin.gen, born: g.B.lin.born } : null } },
    T,
  };
  try { const X5 = require(path.join(ROOT, 'exp', 'territory-analysis', 'extract.js')); const v = X5.variantOf(task.map, task.gameId, R, nInit); out.lay2 = v.tag; out.lay2how = v.how; } catch (err) { out.lay2 = null; }
  if (online) { out.deaths = deathsFull; out.oppDeaths = oppDeaths; out.lab = lab; out.labelCount = labelCount; out.ourDrg = [...ourDrg.values()]; }
  return out;
}
// a few ledger flows per 10-round bin (eat by origin, sprints, splits): kept for the win study
const { FI } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
function pickFl(fl, perBin) {
  const o = {};
  const byPhase = a => { const s = new Array(PH.length - 1).fill(0); for (let b = 0; b < a.length; b++) s[phaseIdx(b * 10)] += a[b]; return s; };
  for (const k of ['eat_nat', 'nat_own', 'nat_enemy', 'nat_neutral', 'nat_fOwn', 'nat_fEnemy', 'eat_oSac', 'eat_oTrap', 'eat_oRammed', 'eat_oRam', 'eat_oOther',
    'eat_eSac', 'eat_eTrap', 'eat_eRammed', 'eat_eRam', 'eat_eOther', 'spr_n', 'spr_ram', 'spr_eat', 'spr_esc', 'spr_other', 'split_n', 'bk_n', 'bk_len', 'kd_n', 'kd_len'])
    o[k] = perBin ? fl[FI[k]] : byPhase(fl[FI[k]]);
  return o;
}

// ---------------------------------------------------------------------------------------------------------------
// Tasks
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];
function topRows() {
  const seen = new Set(), out = [];
  for (const r of readJsonl(path.join(TOP, 'index.jsonl'))) {
    const k = r.battleId + ':' + r.gameId; if (seen.has(k)) continue; seen.add(k);
    if (!fs.existsSync(path.join(TOP, String(r.battleId), r.gameId + '.replay.gz'))) continue;
    out.push(r);
  }
  return out;
}
function topTasks(keysFile) {
  const byKey = new Map(topRows().map(r => [r.battleId + ':' + r.gameId, r]));
  const keys = fs.readFileSync(path.resolve(ROOT, keysFile), 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  const out = [];
  for (const k of keys) {
    const r = byKey.get(k); if (!r) continue;
    out.push({ key: k, file: path.join(TOP, String(r.battleId), r.gameId + '.replay.gz'), src: 'top', map: r.map, gameId: r.gameId, battleId: r.battleId,
      teamA: r.teamA, teamB: r.teamB, eloA: r.eloA, eloB: r.eloB, ranked: !!r.ranked, at: r.at });
  }
  return out;
}
function teamNames() { try { return Object.fromEntries(JSON.parse(fs.readFileSync(path.join(TOP, 'leaderboard.json'), 'utf8')).map(t => [t.id, t.name])); } catch { return {}; } }
function onlineTasks(set) {
  const dir = path.join(ONLINE, set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8')), names = teamNames();
  const out = [];
  for (const g of idx.games || idx) {
    const f = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
    const us = String(g.ourSide).toUpperCase(), opp = names[g.opponentTeam] || String(g.opponentTeam);
    out.push({ key: set + ':' + g.gameId, file: f, src: 'online', set, map: g.mapName, gameId: g.gameId, us, opp, oppId: g.opponentTeam,
      teamA: us === 'A' ? 'US' : opp, teamB: us === 'B' ? 'US' : opp, sub: g.ourSubmission, at: g.completedAt });
  }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------
// Workers
function workerMain() {
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const load = makeLoader(viewerSource());
  process.on('message', task => {
    try { process.send({ key: task.key, line: JSON.stringify(analyse(load(task.file), task, perGame)) }); }
    catch (err) { process.send({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 5).join(' | ') }); }
  });
}
function cachedKeys(file) {
  const done = new Set();
  if (!fs.existsSync(file)) return done;
  const txt = zlib.gunzipSync(fs.readFileSync(file)).toString('utf8');
  for (const l of txt.split('\n')) { const m = /^\{"key":"([^"]+)"/.exec(l); if (m) done.add(m[1]); }
  return done;
}
async function extract(tasks, cacheFile, jobs, limit) {
  fs.mkdirSync(path.dirname(cacheFile), { recursive: true });
  const done = cachedKeys(cacheFile);
  const todo = tasks.filter(t => !done.has(t.key)).slice(0, limit);
  console.log(`${path.relative(ROOT, cacheFile)}: ${tasks.length} games, cached ${done.size}, to do ${todo.length} (jobs ${jobs})`);
  if (!todo.length) return;
  const fd = fs.openSync(cacheFile, 'a'), t0 = Date.now(), errors = [];
  let n = 0;
  await new Promise((resolve, reject) => {
    const queue = todo.slice(); let live = Math.min(jobs, queue.length);
    for (let i = 0, k = live; i < k; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced', execArgv: ['--max-old-space-size=3072'] });
      let finished = false;
      const next = () => { const t = queue.shift(); if (!t) { finished = true; w.kill(); if (--live === 0) resolve(); return; } w.send(t); };
      w.on('message', m => {
        if (m.error) { errors.push(m.key + ' ' + m.error); console.error('error', m.key, m.error); }
        else fs.writeSync(fd, zlib.gzipSync(m.line + '\n'));
        n++;
        if (n % 100 === 0) console.log(`  ${n}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
        next();
      });
      w.on('error', reject);
      w.on('exit', code => { if (!finished) reject(Error('worker exited unexpectedly with code ' + code)); });
      next();
    }
  });
  fs.closeSync(fd);
  console.log(`done ${n} in ${((Date.now() - t0) / 1000).toFixed(0)}s, errors ${errors.length}`);
}
function readCache(file) {
  if (!fs.existsSync(file)) return [];
  return zlib.gunzipSync(fs.readFileSync(file)).toString('utf8').split('\n').filter(l => l.trim()).map(l => JSON.parse(l));
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const jobs = Math.max(1, Math.min(6, +opt('jobs', 4))), limit = +opt('limit', Infinity);
  const cmd = argv[0];
  if (cmd === 'keys') {
    const rows = topRows(), stamp = new Date().toISOString().replace(/[-:]/g, '').slice(0, 13);
    const out = path.resolve(ROOT, opt('out', `exp/eliminations/top-${stamp}.keys`));
    fs.writeFileSync(out, rows.map(r => r.battleId + ':' + r.gameId).join('\n') + '\n');
    console.log(`${rows.length} top games -> ${path.relative(ROOT, out)}`);
    return;
  }
  if (cmd === 'top') return extract(topTasks(opt('keys')), path.join(CACHE, 'top.jsonl.gz'), jobs, limit);
  if (cmd === 'online') {
    const sets = []; for (let i = 1; i < argv.length; i++) { if (argv[i].startsWith('--')) { i++; continue; } sets.push(argv[i]); }
    for (const s of sets) await extract(onlineTasks(s), path.join(CACHE, 'online-' + s + '.jsonl.gz'), jobs, limit);
    return;
  }
  if (cmd === 'one') {
    const t = onlineTasks(argv[1]).find(x => String(x.gameId) === String(argv[2]));
    const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
    const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
    const rec = analyse(makeLoader(viewerSource())(t.file), t, perGame);
    console.log(JSON.stringify(rec).slice(0, +opt('chars', 4000)));
    return;
  }
  console.error('usage: see the header of exp/eliminations/extract.js'); process.exit(2);
}
module.exports = { analyse, tokens, readCache, CACHE, PH, lcOf, phaseIdx, onlineTasks, topTasks, layoutTruth };
if (require.main === module) main().catch(err => { console.error(err); process.exit(1); });
