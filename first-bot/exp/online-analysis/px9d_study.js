#!/usr/bin/env node
'use strict';
// px9d_study.js — replay study of base-px9d (px8 + corridor fortress + conditional late exit, submission 12238) against
// the other online test sets (2026-09-30 online analysis, research/experiments/online-analysis-px9d.md).
// Reads replays only: no network, no games.
//
// usage (repository root):
//   node exp/online-analysis/px9d_study.js [--sets base-px9d-online,base-px8-online,...] [--jobs 3] [--out file.jsonl]
//
// Per game it runs two passes on the same replay:
//   1. analyse() of exp/online-analysis/px8_study.js (unchanged): 10-round timeline of both sides, deaths by cause and
//      window, our king's intake from r300 by source, sacrifice fates, pressure at the king. px bots get the px memory
//      model: px9d and px8 as 'px8' (px9d = px8 + fortress; the sonar format is the same), px-king as 'px1', others off.
//   2. fort() below, a step simulation with tools/baseline_study.js buildGeo (same stepping as px8_study analyse, checked
//      against every dragonUpdate, the final result and the mass identity), for both teams:
//      - start lineage: the team's longest start dragon (lowest id on a tie); at each of its splits it follows the longer
//        piece (the child on a tie). "In the corridor" = head within 1 tile of the straight start line. Dragons that were
//        ever the lineage, and pieces split off it, are "lineage kin" (the fortress stubs).
//      - corridor fountains (Autarky, Prisoners Dilemma): tiles with max spawn gap <= 5 within one tile of the team's start
//        line, from maps/online-20260927/<map>.map (server replays hide pearlRespawn; as study.js). Spawns there are
//        counted from the replay, so the 10-dragon Prisoners Dilemma (other layout) is counted by its real spawns.
//      - snapshots every 10 rounds (state at the start of the round; index 50 = end): units, total length, longest,
//        lineage length and whether it is in the corridor, the longest dragon that is not the lineage ("outside king"),
//        units and total of the dragons that are not lineage kin ("swarm"), dragons >= 8, the second longest.
//      - every pearl eaten: eater side, source (natural on own fountain / on the other team's fountain / elsewhere,
//        corpse of own team / of the other team), eater class (lineage, longest of its team, outside king), 50-round
//        window.
//      - every death: side, round, length, cause (px8_study classes), lineage / kin flags, pearls it dropped and who ate
//        them (side, and whether the eater was that side's longest), and who killed it.
//      - our team size every round r330-420 (the late-exit test of px9d needs 22 dragons), fortress indicators of px9d
//        ('fort ...', 'escape-split... fort', 'peel-split... fort') and the old bot's 'escape-split' indicators.
// Output: one JSON line per game. Checks (expected 0): sim vs dragonUpdate, final state vs result, mass identity,
// pearl bookkeeping.
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const TF = require(path.join(ROOT, 'tools', 'top_features.js'));
const BS = require(path.join(ROOT, 'tools', 'baseline_study.js'));
const PX8 = require(path.join(__dirname, 'px8_study.js'));
const CHILD = process.argv.includes('--px9d-child');
const OWN_TEAM = 583;
const DIRS = 'NESW';
const ELIM_MAPS = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default'];
const MAP_FILE = { Autarky: 'autarky.map', 'Prisoners Dilemma': 'prisoners_dilemma.map' };
const DEFAULT_SETS = ['baseline-r1', 'baseline-r1b', 'baseline-r1c', 'px-king-v2-online', 'base-px8-online', 'base-px9d-online', 'cand-merge2-online'];
const NWIN = 10, WINLEN = 50;
const win = r => Math.max(0, Math.min(NWIN - 1, Math.floor(r / WINLEN)));
const variantOf = s => /px-king|base-px1/.test(s) ? 'px1' : /base-px8|base-px9|px8|px9/.test(s) ? 'px8' : 'other';
const SRC = ['natF', 'natX', 'natE', 'corOwn', 'corOpp'];

function fountainTiles(mapName, M) {
  const f = MAP_FILE[mapName]; if (!f) return null;
  const W = M.width;
  const gaps = fs.readFileSync(path.join(ROOT, 'maps/online-20260927', f), 'utf8').split('\n').filter(l => l.startsWith('TILE ')).map(l => l.trim().split(/\s+/).slice(1).map(Number));
  const out = {};
  for (const t of ['A', 'B']) {
    const d = M.initialDragons.filter(x => x.team === t).sort((a, b) => b.body.length - a.body.length || a.id - b.id)[0];
    out[t] = new Set();
    if (!d || !d.body.every(s => s.x === d.body[0].x)) continue;
    for (const [x, y, , mx] of gaps) if (mx >= 1 && mx <= 5 && Math.abs(x - d.body[0].x) <= 1) out[t].add(y * W + x);
  }
  return out;
}

function fort(R, g) {
  const M = R.match.map, { W, H, N, nb } = BS.buildGeo(M);
  const US = g.ourSide, THEM = US === 'A' ? 'B' : 'A';
  const SIDE = t => t === US ? 'us' : 'them';
  const tileOf = s => s.y * W + s.x;
  const drag = new Map(), occ = new Int32Array(N).fill(-1);
  const pearl = new Int32Array(N).fill(-1);            // -1 none, -2 natural (initial or spawned), >= 0 index into deaths[]
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearl[i] = -2;
  const setOcc = d => { for (const t of d.body) occ[t] = d.id; };
  const clrOcc = d => { for (const t of d.body) if (occ[t] === d.id) occ[t] = -1; };
  const mk = (id, team, body, born, parent) => { const d = { id, team, body, born, parent, kin: false, expect: [], fate: null, free: -1 }; drag.set(id, d); setOcc(d); return d; };
  for (const d0 of M.initialDragons) mk(d0.id, d0.team, d0.body.map(tileOf), 0, -1);
  const F = fountainTiles(g.map, M);

  // lineage per team
  const LIN = {};
  for (const t of ['A', 'B']) {
    const s0 = M.initialDragons.filter(d => d.team === t).sort((a, b) => b.body.length - a.body.length || a.id - b.id)[0];
    const vertical = s0.body.every(s => s.x === s0.body[0].x), horizontal = s0.body.every(s => s.y === s0.body[0].y);
    LIN[t] = { cur: s0.id, startLen: s0.body.length, vertical, horizontal, lx: s0.body[0].x, ly: s0.body[0].y,
      exitRound: null, inRounds: 0, death: null, splits: 0, maxLen: s0.body.length };
    drag.get(s0.id).kin = true;
  }
  const lineOff = (t, tile) => {
    const L = LIN[t], x = tile % W, y = (tile / W) | 0;
    if (L.vertical) { const d = Math.abs(x - L.lx); return Math.min(d, W - d); }
    if (L.horizontal) { const d = Math.abs(y - L.ly); return Math.min(d, H - d); }
    return 99;
  };
  const linDrag = t => { const L = LIN[t]; return L.death ? null : drag.get(L.cur) || null; };
  const linIn = t => { const d = linDrag(t); return d && lineOff(t, d.body[0]) <= 1; };
  const longestOther = (team, id) => { let m = 0; for (const o of drag.values()) if (o.team === team && o.id !== id && o.body.length > m) m = o.body.length; return m; };
  // outside king: longest dragon that is not the lineage dragon while the lineage holds the corridor (fountain maps only)
  const outsideKingLen = team => { const ld = F && linIn(team) ? linDrag(team) : null; let m = 0; for (const o of drag.values()) if (o.team === team && o !== ld && o.body.length > m) m = o.body.length; return m; };

  // ---- outputs ----
  const snaps = { us: [], them: [] };
  const snap = () => {
    for (const t of [US, THEM]) {
      const ld = linDrag(t), inC = !!(ld && lineOff(t, ld.body[0]) <= 1);
      let u = 0, tot = 0, lng = 0, sec = 0, n8 = 0, ok = 0, su = 0, st = 0;
      for (const o of drag.values()) {
        if (o.team !== t) continue;
        const L = o.body.length; u++; tot += L;
        if (L > lng) { sec = lng; lng = L; } else if (L > sec) sec = L;
        if (L >= 8) n8++;
        if (!(F && inC && o === ld) && L > ok) ok = L;
        if (!o.kin) { su++; st += L; }
      }
      snaps[SIDE(t)].push([u, tot, lng, ld ? ld.body.length : 0, inC ? 1 : 0, ok, su, st, n8, sec]);
    }
  };
  const Z = () => new Array(NWIN).fill(0);
  const zsrc = () => ({ natF: 0, natX: 0, natE: 0, corOwn: 0, corOpp: 0 });
  const eat = { us: zsrc(), them: zsrc() }, eatW = { us: {}, them: {} };
  for (const s of ['us', 'them']) for (const k of SRC) eatW[s][k] = Z();
  const eatLin = { us: zsrc(), them: zsrc() }, eatKing = { us: zsrc(), them: zsrc() }, eatKing300 = { us: zsrc(), them: zsrc() }, eatKing350 = { us: zsrc(), them: zsrc() };
  const eatOK = { us: zsrc(), them: zsrc() }, eatOK300 = { us: zsrc(), them: zsrc() };
  const kingEatW = { us: Z(), them: Z() }, okEatW = { us: Z(), them: Z() };
  const fnt = F ? { us: { spawns: 0 }, them: { spawns: 0 } } : null;
  const deaths = [];
  const ind = { fort: 0, fortSplit: 0, peel: 0, peelRounds: [], escSplit: 0, fortNonLin: 0, fortRounds: [] };
  const units330 = { max: 0, first22: null, at: {} };
  const chk = { updates: 0, deaths: 0, final: 1, mass: 1, pearl: 0 };
  let round = -1, cur = -1, dropCtx = -1, indText = '';
  const mass = { us: { init: 0, eaten: 0, paid: 0, died: 0 }, them: { init: 0, eaten: 0, paid: 0, died: 0 } };
  for (const o of drag.values()) mass[SIDE(o.team)].init += o.body.length;
  const freeCount = d => { const h = d.body[0]; let f = 0; for (let k = 0; k < 4; k++) { const u = nb[h * 4 + k]; if (u >= 0 && occ[u] === -1) f++; } return f; };

  const onEat = (d, k, lenBefore) => {
    const src0 = pearl[k]; pearl[k] = -1;
    const side = SIDE(d.team), w = win(round);
    let src;
    if (src0 === -2) src = F && F[d.team].has(k) ? 'natF' : F && F[d.team === 'A' ? 'B' : 'A'].has(k) ? 'natX' : 'natE';
    else { const D = deaths[src0]; src = D.side === side ? 'corOwn' : 'corOpp'; }
    mass[side].eaten++;
    if (round < 0) return;
    eat[side][src]++; eatW[side][src][w]++;
    const isLin = !LIN[d.team].death && LIN[d.team].cur === d.id;
    const isLongest = lenBefore >= longestOther(d.team, d.id);
    const ld = F && linIn(d.team) ? linDrag(d.team) : null;
    let isOK = false;
    if (d !== ld) { let m = 0; for (const o of drag.values()) if (o.team === d.team && o !== ld && o.id !== d.id && o.body.length > m) m = o.body.length; isOK = lenBefore >= m; }
    if (isLin) eatLin[side][src]++;
    if (isLongest) { eatKing[side][src]++; kingEatW[side][w]++; if (round >= 300) eatKing300[side][src]++; if (round >= 350) eatKing350[side][src]++; }
    if (isOK) { eatOK[side][src]++; okEatW[side][w]++; if (round >= 300) eatOK300[side][src]++; }
    if (src0 >= 0) { const D = deaths[src0]; D.eaten[side === 'us' ? 0 : 1]++; if (isLongest) D.eatenK[side === 'us' ? 0 : 1]++; if (isOK) D.eatenOK[side === 'us' ? 0 : 1]++; }
  };

  for (const e of R.events) {
    if (dropCtx >= 0 && !(e.type === 'tileChange' && e.hasPearl)) dropCtx = -1;
    switch (e.type) {
      case 'roundStart': {
        round = e.round;
        if (round % 10 === 0) snap();
        for (const t of ['A', 'B']) if (linIn(t)) LIN[t].inRounds++;
        if (round >= 330 && round <= 420) {
          let u = 0; for (const o of drag.values()) if (o.team === US) u++;
          if (u > units330.max) units330.max = u;
          if (u >= 22 && units330.first22 === null) units330.first22 = round;
          if (round % 30 === 0) units330.at[round] = u;
        }
        break;
      }
      case 'turnStart': { cur = e.id; indText = ''; const d = drag.get(cur); if (d) { d.expect = []; d.fate = null; d.free = freeCount(d); } break; }
      case 'dragonIndicator': {
        const d = drag.get(e.id); if (!d || d.team !== US || round < 0) break;
        const t = e.text || ''; indText = t;
        const isLin = !LIN[US].death && LIN[US].cur === d.id;
        if (/ fort /.test(t) || t.startsWith('fort ')) {
          ind.fort++; if (!isLin) ind.fortNonLin++;
          if (t.startsWith('peel-split')) { ind.peel++; ind.peelRounds.push(round); }
          else if (t.startsWith('escape-split')) ind.fortSplit++;
          if (ind.fortRounds.length < 6 && (!F || !isLin)) ind.fortRounds.push(round);
        } else if (t.startsWith('escape-split')) ind.escSplit++;
        break;
      }
      case 'tileChange': {
        const k = tileOf(e.tile);
        if (e.hasPearl) {
          if (dropCtx >= 0) { pearl[k] = dropCtx; deaths[dropCtx].dropped++; }
          else { pearl[k] = -2; if (round >= 0 && fnt) { if (F[US].has(k)) fnt.us.spawns++; if (F[THEM].has(k)) fnt.them.spawns++; } }
        } else if (pearl[k] !== -1) { chk.pearl++; pearl[k] = -1; }
        break;
      }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action;
        if (!a || a.kind !== 'move') break;
        clrOcc(d);
        const body = d.body.slice(); let fate = null;
        for (let i = 0; i < a.steps.length; i++) {
          if (i > 0 && body.length <= 2) { fate = { reason: 'A', step: i, why: 'sprint' }; break; }
          const h = body[0], nx = nb[h * 4 + DIRS.indexOf(a.steps[i])];
          if (nx < 0) { fate = { reason: 'W', step: i }; break; }
          if (body.includes(nx)) { fate = { reason: 'S', step: i }; break; }
          const o = occ[nx];
          if (o !== -1) { const od = drag.get(o); fate = { reason: od.body[0] === nx ? 'H' : 'O', step: i, hit: o, hitTeam: od.team, hitLen: od.body.length }; break; }
          const lenBefore = body.length;
          body.unshift(nx);
          if (pearl[nx] !== -1) onEat(d, nx, lenBefore); else body.pop();
          if (i > 0) { body.pop(); mass[SIDE(d.team)].paid++; }
          d.expect.push({ h: body[0], t: body[body.length - 1] });
        }
        d.fate = fate; d.body = body; setOcc(d);
        const L = LIN[d.team];
        if (!L.death && L.cur === d.id) {
          if (body.length > L.maxLen) L.maxLen = body.length;
          if (L.exitRound === null && lineOff(d.team, body[0]) >= 2) L.exitRound = round;
        }
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id); if (!d || round < 0) break;
        const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        const eh = tileOf(e.head), et = tileOf(e.tail);
        if (x.h !== eh || x.t !== et) {
          chk.updates++;
          clrOcc(d); const b = d.body.slice(); if (b[0] !== eh) b.unshift(eh);
          while (b.length > 1 && b[b.length - 1] !== et) b.pop();
          d.body = b; d.expect = []; setOcc(d);
        }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        clrOcc(p); p.body = e.parentBody.map(tileOf); setOcc(p);
        const c = mk(e.childId, e.team, e.childBody.map(tileOf), round, p.id);
        const L = LIN[p.team];
        if (!L.death && L.cur === p.id) {
          L.splits++; c.kin = true;
          if (c.body.length >= p.body.length) L.cur = c.id;
          const ld = drag.get(L.cur);
          if (L.exitRound === null && lineOff(p.team, ld.body[0]) >= 2) L.exitRound = round;
        }
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        const side = SIDE(d.team), mover = cur === d.id, len = d.body.length;
        let c, m = null;
        if (mover) {
          const f = d.fate;
          if (e.reason === 'H') c = f && f.hitTeam !== d.team ? 'ram' : 'allyHead';
          else if (e.reason === 'O') c = f && f.hitTeam !== d.team ? 'enemyBody' : (d.free === 0 ? 'trapped' : 'volAlly');
          else if (e.reason === 'A' && f && f.why === 'sprint') c = 'sprintCost';
          else if (d.free === 0) c = 'trapped';
          else c = f && f.step > 0 ? 'sprintWS' : 'vol';
          if (e.reason === 'A') { if (f && f.reason !== 'A') chk.deaths++; }
          else if (!f || f.reason !== e.reason) chk.deaths++;
        } else {
          m = drag.get(cur);
          c = e.reason === 'H' && m && m.team !== d.team ? 'rammed' : e.reason === 'H' && m ? 'allyHead' : 'other';
          if (e.reason !== 'H' || !m || !m.fate || m.fate.hit !== d.id) chk.deaths++;
        }
        const L = LIN[d.team], isLin = !L.death && L.cur === d.id;
        const wasLongest = len >= longestOther(d.team, d.id);
        const byEnemy = c === 'ram' || c === 'rammed' || c === 'enemyBody';
        deaths.push({ side, r: round, len, c, lin: isLin ? 1 : 0, kin: d.kin ? 1 : 0, longest: wasLongest ? 1 : 0, born: d.born, byEnemy: byEnemy ? 1 : 0,
          byLen: m && m.team !== d.team ? m.body.length : 0, dropped: 0, eaten: [0, 0], eatenK: [0, 0], eatenOK: [0, 0] });
        mass[side].died += len;
        if (isLin) L.death = { r: round, c, len };
        clrOcc(d); drag.delete(e.id);
        dropCtx = deaths.length - 1;
        break;
      }
      default: break;
    }
  }
  const rounds = round + 1;
  while (snaps.us.length < 50) snap();
  snap();
  const res = R.result, rU = res['team' + US], rT = res['team' + THEM];
  const fU = snaps.us[50], fT = snaps.them[50];
  if (fU[0] !== rU.dragonCount || fU[1] !== rU.totalLength || fU[2] !== rU.longestDragon || fT[0] !== rT.dragonCount || fT[1] !== rT.totalLength || fT[2] !== rT.longestDragon) chk.final = 0;
  for (const s of ['us', 'them']) { const x = mass[s]; if (x.init + x.eaten - x.paid - x.died !== (s === 'us' ? fU[1] : fT[1])) chk.mass = 0; }
  const lin = {};
  for (const t of [US, THEM]) {
    const L = LIN[t], d = linDrag(t);
    lin[SIDE(t)] = { startLen: L.startLen, straight: L.vertical || L.horizontal, exitRound: L.exitRound, inRounds: L.inRounds, death: L.death, splits: L.splits, maxLen: L.maxLen, final: d ? d.body.length : 0, finalIn: linIn(t) ? 1 : 0 };
  }
  return { rounds, snaps, eat, eatW, eatLin, eatKing, eatKing300, eatKing350, eatOK, eatOK300, kingEatW, okEatW, fnt, deaths, ind, units330, lin, chk };
}

// ---------------------------------------------------------------------------------------------------------------
function listOnline(set) {
  const dir = path.join(ROOT, 'data', 'online', set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  const out = [];
  for (const g of idx.games || idx) {
    if (g.ourWin === null || g.ourWin === undefined) continue;
    const gj = JSON.parse(fs.readFileSync(path.join(dir, `game-${g.gameId}.json`), 'utf8'));
    const us = String(g.ourSide).toUpperCase(), them = us === 'A' ? 'B' : 'A';
    if (gj['team' + us + 'Id'] !== OWN_TEAM) throw Error(`${set} ${g.gameId}: side ${us} is not ${OWN_TEAM}`);
    const res = gj.replay.result;
    out.push({ src: 'online', set, id: String(g.gameId), file: path.join(dir, `M${g.gameId}.replay`), ourSide: us, map: g.mapName, opp: String(g.opponentTeam),
      oppName: gj['team' + them + 'Name'], win: g.ourWin ? 1 : 0, G: res['team' + us].dragonCount > 0 ? res['team' + us].longestDragon : 0,
      theirLongest: res['team' + them].longestDragon, total: res['team' + us].totalLength, theirTotal: res['team' + them].totalLength,
      survived: res['team' + us].dragonCount > 0 ? 1 : 0, endReason: res.endReason, variant: variantOf(set) });
  }
  return out;
}

async function runWorkers(tasks, jobs, onRec) {
  let next = 0, done = 0; const errors = [];
  await new Promise((resolve, reject) => {
    const nw = Math.min(jobs, tasks.length); let live = nw; if (!nw) return resolve();
    for (let k = 0; k < nw; k++) {
      const w = cp.fork(__filename, ['--px9d-child'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
      let finished = false;
      const feed = () => { if (next >= tasks.length) { finished = true; w.send('exit'); if (--live === 0) resolve(); return; } const i = next++; w.send({ i, task: tasks[i] }); };
      w.on('message', m => { if (m.error) errors.push(tasks[m.i].set + ' ' + tasks[m.i].id + ' ' + m.error); else onRec(m.rec); if (++done % 50 === 0) process.stderr.write(`${done}/${tasks.length} `); feed(); });
      w.on('error', reject);
      w.on('exit', code => { if (!finished) reject(Error('child exited with code ' + code)); });
      feed();
    }
  });
  process.stderr.write('\n');
  if (errors.length) { console.error(errors.join('\n')); throw Error(errors.length + ' games failed'); }
}

if (CHILD) {
  const load = TF.makeLoader(TF.viewerSource());
  process.on('message', m => {
    if (m === 'exit') { process.exit(0); return; }
    try {
      const R = load(m.task.file), t = m.task;
      const a = PX8.analyse(R, t);
      const x = fort(R, t);
      const nInit = R.match.map.initialDragons.length;
      const mapKey = t.map === 'Prisoners Dilemma' ? 'PD' + nInit : t.map;
      const px8 = { tl: a.tl, cause: a.cause, causeW: a.causeW, causeLen: a.causeLen, kingEat: a.kingEat, kingEatW: a.kingEatW, sacLate: a.sacLate, sac: a.sac,
        sacNear: a.sacNear, K: a.K, KD: a.KD, T1: a.T1, stubs: a.stubs, splitsW: a.splitsW, natW: a.natW, eatW: a.eatW, chk: a.chk };
      process.send({ i: m.i, rec: { ...t, file: undefined, mapKey, nInit, type: ELIM_MAPS.includes(t.map) ? 'elim' : 'r500', px8, x } });
    } catch (err) { process.send({ i: m.i, error: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | ') }); }
  });
}

async function main() {
  const argv = process.argv.slice(2);
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const sets = opt('sets', DEFAULT_SETS.join(',')).split(',').filter(Boolean);
  const jobs = Math.min(3, Math.max(1, +opt('jobs', 3)));
  const out = path.resolve(ROOT, opt('out', '.cache/online-analysis/px9d_study.jsonl'));
  const tasks = sets.flatMap(listOnline);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  process.stderr.write(`px9d_study: ${tasks.length} games (${sets.join(', ')}) with ${jobs} workers -> ${out}\n`);
  const t0 = Date.now(), recs = [];
  await runWorkers(tasks, jobs, r => recs.push(r));
  recs.sort((p, q) => sets.indexOf(p.set) - sets.indexOf(q.set) || p.id.localeCompare(q.id));
  fs.writeFileSync(out, recs.map(r => JSON.stringify(r)).join('\n') + '\n');
  const c = { games: recs.length, px8: { updates: 0, deaths: 0, splits: 0, finalBad: 0, massBad: 0 }, fort: { updates: 0, deaths: 0, pearl: 0, finalBad: 0, massBad: 0 } };
  for (const r of recs) {
    c.px8.updates += r.px8.chk.updates; c.px8.deaths += r.px8.chk.deaths; c.px8.splits += r.px8.chk.splits; if (!r.px8.chk.final) c.px8.finalBad++; if (!r.px8.chk.massOk) c.px8.massBad++;
    c.fort.updates += r.x.chk.updates; c.fort.deaths += r.x.chk.deaths; c.fort.pearl += r.x.chk.pearl; if (!r.x.chk.final) c.fort.finalBad++; if (!r.x.chk.mass) c.fort.massBad++;
  }
  console.log(JSON.stringify(c));
  process.stderr.write(`done in ${((Date.now() - t0) / 1000).toFixed(1)}s\n`);
}
if (!CHILD && require.main === module) main().catch(err => { console.error(err); process.exit(1); });
module.exports = { fort, fountainTiles };
