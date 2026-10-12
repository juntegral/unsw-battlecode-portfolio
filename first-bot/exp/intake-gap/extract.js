#!/usr/bin/env node
// Natural-pearl intake gap: where do the pearls we do not eat go? Replays only (no games, no network).
// Written for research/observations/intake-gap.md (2026-09-30, coordinator question 22:10 "is it still the economy?").
//
// usage (repository root):
//   node exp/intake-gap/extract.js online <set> [<set> ...] [--jobs 3]
//   node exp/intake-gap/extract.js top [--keys <file>|all] [--jobs 3] [--limit N]
//   One JSON line per game in .cache/intake-gap/<online-<set>|top>.jsonl. Games already there are skipped.
//
// Reconstruction: tools/mass_ledger.js perGame() with hooks (its chk must stay 0); map geometry, territory and pearl
// layout (a / b / PD10) from exp/territory-analysis/extract.js (geometry, variantOf, fileOf, gapsOfFile).
// Loader: exp/intake-gap/rawload.js decodes the events straight from the Cap'n Proto bytes (5-6x faster than the official per-event
// conversion; validated event by event by exp/intake-gap/validate_raw.js); the official parser still builds the root (map, result).
// Sonar / debug / log events are counted and skipped (not used here). The ledger's `sonar` count is therefore 0; sonar pings per
// team are counted here.
//
// Definitions (per round = at the round's first turn, i.e. after the round's spawns and before any move):
//   dist_t(k): static path distance from tile k to the nearest living head of team t (kelp, portals, wrap; bodies ignored),
//     multi-source BFS; unreachable / no heads = INF (999).
//   race of tile k (from team A's side): dB - dA; class 0..8 = <=-6, -5..-3, -2..-1, 0, 1..2, 3..5, >=6, (both INF = 8).
//     race3 = A nearer / tie / B nearer.
//   Natural pearl: on the map at the start, or spawned at a round start (ledger origin -1). Its row: round of appearance
//     (initial pearls: 0, flag init), race class at appearance, tile territory (0 neutral, 1 A, 2 B), fountain (mean gap <= 12),
//     vision (a head of the team within Chebyshev 3), nearest-head length of each team, fate (eaten by A / B / uneaten at end),
//     delay (rounds from appearance to eaten).
//   Spawn attempts (expected): each round, capacity 1/mean gap of every spawnable tile, by race3 and territory (CAPR).
//   Blocked attempts:
//     body (expected): capacity of spawnable tiles under a body of team t at the round start (random countdown phase).
//     natural pearl (expected, renewal): a natural pearl spawned at r0 and removed in round r1 blocks N(r1 - r0) attempts, the
//       renewal count of the tile's uniform gap [min, max] (the countdown restarts at its own spawn). Initial pearls: capacity x
//       rounds present (phase unknown).
//     drop pearl (expected): capacity of spawnable tiles under a death drop at the round start (random phase).
//     mirror (observed lower bound): symmetric tiles share one countdown; a natural spawn on k whose mirror m (spawnable, m != k)
//       did not spawn that round means m's attempt was blocked by what occupied m (A body, B body, natural pearl, drop, none=check).
//   Head-rounds: living heads at each round's first turn, by length class (2, 3, 4, 5-7, 8-14, 15+), by the head's territory
//     (own / neutral / enemy of its team) and by the static distance to the nearest natural pearl on the board (0-3, 4-6, 7-10, 11+).
//   Natural eats: by eater team, eater length before the move (class), pearl territory relative to the eater, 10-round bin.
//   Our labels (online games, our side): the turn's INDICATOR kind (tools/mech_check.js grammar): turns and natural eats per kind.
//   Child origin (our side): a child's split label kind (csplit, lsplit, floor, kcap, frag, bsplit, split, escsplit, escsplit2);
//     natural eats of the child itself.
// Independent recount (recount(), same parsed replay, no ledger / no step simulation / own kelp-portal-wrap graph): bodies from
// dragonUpdate head/tail + dragonSplit bodies; natural pearls from the tileChange order; per team natural eats by phase, head-rounds
// by phase, race3 x fate counts by phase, expected body blocking per team, mirror-observed blocks by blocker. Compared per game (chkR).
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process'), zlib = require('zlib'), vm = require('vm');

const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const X = require(path.join(ROOT, 'exp', 'territory-analysis', 'extract.js'));
const TOP = path.join(ROOT, 'data', 'top'), ONLINE = path.join(ROOT, 'data', 'online'), CACHE = path.join(ROOT, '.cache', 'intake-gap');
const INF = 999, NB = 50;
const PH = r => r < 50 ? 0 : r < 100 ? 1 : r < 250 ? 2 : r < 350 ? 3 : r < 450 ? 4 : 5; // 6 phases: r0-49, 50-99, 100-249, 250-349, 350-449, 450+
const NPH = 6;
const LC = L => L <= 2 ? 0 : L === 3 ? 1 : L === 4 ? 2 : L <= 7 ? 3 : L <= 14 ? 4 : 5; // 2,3,4,5-7,8-14,15+
const LCS = L => L <= 4 ? 0 : L <= 7 ? 1 : 2;                                           // <=4, 5-7, >=8
const RC = (dA, dB) => { if (dA >= INF && dB >= INF) return 8; const x = dB - dA; return x <= -6 ? 0 : x <= -3 ? 1 : x <= -1 ? 2 : x === 0 ? 3 : x <= 2 ? 4 : x <= 5 ? 5 : 6; };
const R3 = (dA, dB) => dA < dB ? 0 : dA === dB ? 1 : 2; // A nearer / tie / B nearer
const DNP = d => d < 0 || d >= INF ? 3 : d <= 3 ? 0 : d <= 6 ? 1 : d <= 10 ? 2 : 3;
const KINDS = ['plain', 'g', 'F', 'cov', 'cl', 'grab', 'esc', 'noexit', 'escsplit', 'feed', 'split', 'trade', 'lsplit', 'csplit', 'other'];
const KI = Object.fromEntries(KINDS.map((k, i) => [k, i]));
const ORIGS = ['csplit', 'lsplit', 'floor', 'kcap', 'frag', 'bsplit', 'split', 'escsplit', 'escsplit2', 'unl'];
const OI = Object.fromEntries(ORIGS.map((k, i) => [k, i]));

// ---------------------------------------------------------------------------------------------------------------
// fast loader
function makeFastLoader() {
  const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
  const src = tf.viewerSource();
  const cut = src.indexOf('var Af=B(');
  if (cut < 0) throw Error('unexpected replay-viewer build');
  const code = src.slice(0, cut).replace('if(n.formatVersion>1)', 'if(n.formatVersion>2)') + 'globalThis.__tf={Df:Df,bf:bf,Of:Of,cu:$,of:of};})();';
  const ctx = { TextEncoder, TextDecoder };
  vm.runInNewContext(code, ctx, { timeout: 5000 });
  const { Df, bf, Of, of } = ctx.__tf;
  const SON = of.SONAR_PING, DBG = of.DEBUG_DRAW, DLOG = of.DRAGON_LOG, ELOG = of.ENGINE_LOG;
  if (SON === undefined || DBG === undefined) throw Error('event kind enum not found');
  return file => {
    const raw = fs.readFileSync(file);
    const root = Df(file.endsWith('.gz') ? zlib.gunzipSync(raw) : raw);
    const list = root.events, n = list.length, events = [], sonar = new Map();
    for (let i = 0; i < n; i++) {
      const ev = list.get(i), w = ev.which();
      if (w === SON) { const id = ev.sonarPing.senderId; sonar.set(id, (sonar.get(id) || 0) + 1); continue; }
      if (w === DBG || w === DLOG || w === ELOG) continue;
      events.push(bf(ev));
    }
    const R = Of(root, events);
    R.sonarBySender = sonar;
    return R;
  };
}

// ---------------------------------------------------------------------------------------------------------------
// label kind of one INDICATOR text (tools/mech_check.js parseInd grammar, reduced to activity kinds)
function labelKind(s) {
  if (!s) return 'plain';
  if (/^feed #/.test(s)) return 'feed';
  if (/^pocket-eat/.test(s)) return 'other';
  if (/^escape-split/.test(s) || /^esc-split/.test(s)) return 'escsplit';
  if (/^csplit\d/.test(s)) return 'csplit';
  if (/^lsplit\d/.test(s)) return 'lsplit';
  if (/^split\d/.test(s)) return 'split';
  if (s.startsWith('no-exit')) return 'noexit';
  if (s.startsWith('last-trade') || s.startsWith('degraded')) return 'other';
  const m = /^([NESW]+) v(\S+) d(\d+) L(\d+)(.*)$/.exec(s);
  if (!m) return 'other';
  const toks = m[5].split('|')[0].trim().split(/\s+/).filter(Boolean);
  if (toks.includes('TRADE')) return 'trade';
  if (toks.includes('esc')) return 'esc';
  if (toks.some(t => /^F\d+@/.test(t))) return 'F';
  if (toks.some(t => /^[Kg]\d+$/.test(t))) return 'g';
  if (toks.some(t => /^grab@/.test(t))) return 'grab';
  if (toks.some(t => /^cl@/.test(t))) return 'cl';
  if (toks.includes('cov')) return 'cov';
  return 'plain';
}
function splitOrigin(s) {
  if (!s) return 'unl';
  if (/^csplit\d/.test(s)) return 'csplit';
  if (/^lsplit\d/.test(s)) return 'lsplit';
  if (/^escape-split/.test(s)) return 'escsplit';
  if (/^esc-split/.test(s)) return 'escsplit2';
  const m = /^split(\d+) u(\d+) L(\d+)(.*)$/.exec(s);
  if (m) { const t = m[4]; return / frag(\s|$)/.test(t) ? 'frag' : / bsp(\s|$)/.test(t) ? 'bsplit' : / kcap(\s|$)/.test(t) ? 'kcap' : / floor(\s|$)/.test(t) ? 'floor' : 'split'; }
  return 'unl';
}

// renewal count of a uniform gap [mn, mx]: m[t] = expected attempts in (0, t] after an attempt at 0
const renewCache = new Map();
function renewal(mn, mx) {
  const key = mn + ',' + mx;
  let m = renewCache.get(key);
  if (!m) {
    m = new Float64Array(502); const p = 1 / (mx - mn + 1);
    for (let t = 1; t <= 501; t++) { let s = 0; for (let j = mn; j <= mx && j <= t; j++) s += p * (1 + m[t - j]); m[t] = s; }
    renewCache.set(key, m);
  }
  return m;
}
function symOf(file) {
  try { const L = fs.readFileSync(file, 'utf8').split('\n', 4); for (const l of L) { const m = /^SYMMETRY (\S+)/.exec(l); if (m) return m[1]; } } catch { /* none */ }
  return null;
}

// ---------------------------------------------------------------------------------------------------------------
// main per-game analysis
function analyse(R, info) {
  const M = R.match.map, W = M.width, H = M.height, nInit = M.initialDragons.length;
  const linfo = { map: info.map }; if (info.map === 'Prisoners Dilemma') linfo.variant = nInit === 10 ? 'PD10' : 'PD6';
  const G = X.geometry(R), N = G.N, nb = G.nb, terr = G.terr;
  const V = X.variantOf(info.map, info.gameId, R, nInit);
  const lf = X.fileOf(info.map, V.tag), gg = lf && fs.existsSync(lf) ? X.gapsOfFile(lf) : null;
  const layoutOk = gg && gg.w === W && gg.h === H ? 1 : 0;
  const CAP = new Float64Array(N), MN = new Int16Array(N), MXG = new Int16Array(N), fount = new Uint8Array(N);
  const spawnList = [];
  if (layoutOk) for (let k = 0; k < N; k++) { const q = gg.g[k]; if (q && q[1] > 0) { const mg = Math.max(1, (q[0] + q[1]) / 2); CAP[k] = 1 / mg; MN[k] = Math.max(1, q[0]); MXG[k] = q[1]; if (mg <= 12) fount[k] = 1; spawnList.push(k); } }
  const sym = lf ? symOf(lf) : null;
  const MIR = new Int32Array(N).fill(-1); let symOk = 0;
  if (sym && layoutOk) {
    for (let k = 0; k < N; k++) { const x = k % W, y = (k / W) | 0; const mx = sym.includes('y') ? W - 1 - x : x, my = sym.includes('x') ? H - 1 - y : y; MIR[k] = my * W + mx; }
    let bad = 0; for (let k = 0; k < N; k++) { const a = gg.g[k], b = gg.g[MIR[k]]; if ((a ? a[1] : 0) !== (b ? b[1] : 0) || (a ? a[0] : 0) !== (b ? b[0] : 0)) bad++; }
    symOk = bad === 0 ? 1 : 0;
  }
  const TI = tm => tm === 'A' ? 0 : 1;
  const rel = (k, ti) => terr[k] === 0 ? 1 : terr[k] === ti + 1 ? 0 : 2; // 0 own, 1 neutral, 2 enemy
  const us = info.us ? TI(info.us) : -1;

  // accumulators
  const z = n => new Array(n).fill(0);
  const HR = [0, 1].map(() => [0, 1, 2, 3, 4, 5].map(() => z(NB)));
  const HRT = [0, 1].map(() => [0, 1, 2].map(() => z(NB)));
  const HRP = [0, 1].map(() => z(3 * 4 * NPH));             // [lcs][dnp][ph]
  const EAT = [0, 1].map(() => [0, 1, 2, 3, 4, 5].map(() => [0, 1, 2].map(() => z(NB))));
  const TURNS = [0, 1].map(() => z(NB)), STEPS = [0, 1].map(() => z(NB));
  const RACE = {};                                           // "ph|terr|f|cls|vis|fate|init" -> n
  const DEL = {};                                            // "ph|r3|fate" -> [n, sumDelay]
  const NEAR = {};                                           // "ph|r3|lcsA|lcsB|fate" -> n
  const CAPR = z(NB * 3 * 3);                                // [bin][terr][r3] expected attempts
  const CAPRF = z(NPH * 3 * 3);                              // fountains only [ph][terr][r3]
  const OB = z(2 * NPH * 3 * 3 * 2);                         // body blocking [team][ph][terr][r3][f]
  const PB = z(NPH * 3 * 3 * 3);                             // natural pearl blocking [ph][terr][r3 at spawn][fate]
  const DB = z(NPH * 3 * 3);                                 // drop blocking [ph][terr][r3]
  const PBR = z(NPH * 3 * 3);                                // natural pearl blocking by the round it happens [ph][terr][r3 now] (renewal density at the pearl's age)
  const STEAL = z(NPH * 3 * 2 * 3);                          // [ph][r3 at spawn][eater team 0 A 1 B][eater length class <=4, 5-7, >=8] natural eats
  const SBM = z(NPH * 5 * 3 * 3);                            // mirror observed [ph][blocker][terr][r3]
  const ACT = z(KINDS.length * NB), ACTE = z(KINDS.length * NB); // our turns / natural eats by label kind
  const ORG = z(ORIGS.length * NB), ORGE = z(ORIGS.length * NB), ORGHR = z(ORIGS.length * NB); // births, natural eats, head-rounds by origin
  const chkX = { mirNone: 0, spawnMismatch: 0, layout: layoutOk ? 0 : 1, sym: sym && !symOk ? 1 : 0, liveLeft: 0 };

  // per-round state
  const distT = [new Int16Array(N), new Int16Array(N)], lenT = [new Int16Array(N), new Int16Array(N)];
  const visT = [new Uint8Array(N), new Uint8Array(N)];
  const distP = new Int16Array(N);
  const Q = new Int32Array(N + 8);
  const heads = [[], []];
  const bfs = (srcs, d, L) => {
    d.fill(-1); let qh = 0, qt = 0;
    for (const s of srcs) if (d[s.k] < 0) { d[s.k] = 0; if (L) L[s.k] = s.len; Q[qt++] = s.k; }
    while (qh < qt) { const k = Q[qh++], dk = d[k]; for (let j = 0; j < 4; j++) { const u = nb[k * 4 + j]; if (u < 0 || d[u] >= 0) continue; d[u] = dk + 1; if (L) L[u] = L[k]; Q[qt++] = u; } }
  };
  const live = new Map(); // tile -> natural pearl record
  const label = new Map(), origin = new Map();
  let lastRound = -99, spawnsSeen = 0, curRound = -1;
  const dd = (ti, k) => distT[ti][k] < 0 ? INF : distT[ti][k];

  function finalize(p, fate, r1) { // fate 0 A, 1 B, 2 none
    const ph = PH(p.r0);
    const kk = ph + '|' + p.terr + '|' + p.f + '|' + p.cls + '|' + p.vis + '|' + fate + '|' + p.init;
    RACE[kk] = (RACE[kk] || 0) + 1;
    const r3 = p.cls === 8 ? 1 : p.cls <= 2 ? 2 : p.cls === 3 ? 1 : 0;
    if (fate < 2) { const k2 = ph + '|' + r3 + '|' + fate; const a = DEL[k2] || (DEL[k2] = [0, 0]); a[0]++; a[1] += r1 - p.r0; }
    const k3 = ph + '|' + r3 + '|' + p.lA + '|' + p.lB + '|' + fate; NEAR[k3] = (NEAR[k3] || 0) + 1;
    if (fate < 2) STEAL[((ph * 3 + r3) * 2 + fate) * 3 + p.eLcs]++;
    // blocked attempts while it sat on the tile
    let blk;
    if (p.init) blk = CAP[p.k] * r1;
    else blk = MXG[p.k] > 0 ? renewal(MN[p.k], MXG[p.k])[Math.max(0, Math.min(501, r1 - p.r0))] : 0;
    PB[((ph * 3 + p.terr) * 3 + r3) * 3 + fate] += blk;
  }

  function roundStart(round, ctx) {
    heads[0] = []; heads[1] = [];
    for (const d of ctx.drag.values()) { const h = d.body[0]; heads[TI(d.team)].push({ k: h.y * W + h.x, len: d.body.length, d }); }
    bfs(heads[0], distT[0], lenT[0]); bfs(heads[1], distT[1], lenT[1]);
    for (const ti of [0, 1]) { const v = visT[ti]; v.fill(0); for (const h of heads[ti]) { const hx = h.k % W, hy = (h.k / W) | 0; for (let dy = -3; dy <= 3; dy++) { const yy = G.wy(hy + dy) * W; for (let dx = -3; dx <= 3; dx++) v[yy + G.wx(hx + dx)] = 1; } } }
    const ph = PH(round), b = Math.min(NB - 1, Math.floor(round / 10));
    // natural pearls already on the board at this round start block this round's attempt on their tile:
    // expected = renewal density at the pearl's age (spawned pearls) or the capacity (initial pearls, unknown phase)
    for (const p of live.values()) {
      if (!(CAP[p.k] > 0)) continue;
      let u; if (p.init) u = CAP[p.k]; else { const m = renewal(MN[p.k], MXG[p.k]), a = round - p.r0; u = a >= 1 && a <= 501 ? m[a] - m[a - 1] : 0; }
      PBR[(ph * 3 + terr[p.k]) * 3 + R3(dd(0, p.k), dd(1, p.k))] += u;
    }
    // new natural pearls at this round start (initial pearls appear at round 0 with init = 1)
    const fresh = [];
    for (const [k, o] of ctx.pearls) {
      if (o !== -1 || live.has(k)) continue;
      const dA = dd(0, k), dB = dd(1, k);
      const p = { k, r0: round, terr: terr[k], f: fount[k], cls: RC(dA, dB), vis: visT[0][k] + 2 * visT[1][k], lA: dA < INF ? LCS(lenT[0][k]) : 3, lB: dB < INF ? LCS(lenT[1][k]) : 3, init: round === 0 && initialSet.has(k) ? 1 : 0 };
      live.set(k, p); fresh.push(k); if (!p.init) spawnsSeen++;
    }
    // mirror-observed blocks
    if (symOk && round > 0) {
      const set = new Set(fresh);
      for (const k of fresh) {
        const m = MIR[k]; if (m === k || set.has(m) || !(CAP[m] > 0)) continue;
        let bl = 4; const o = ctx.occ.get(m);
        if (o !== undefined) { const od = ctx.drag.get(o); bl = od ? TI(od.team) : 4; }
        else if (ctx.pearls.has(m)) bl = ctx.pearls.get(m) < 0 ? 2 : 3;
        if (bl === 4) chkX.mirNone++;
        SBM[((ph * 5 + bl) * 3 + terr[m]) * 3 + R3(dd(0, m), dd(1, m))]++;
      }
    }
    // expected attempts by race (capacity) and blocked by bodies / drops
    for (const k of spawnList) {
      const r3 = R3(dd(0, k), dd(1, k));
      CAPR[(b * 3 + terr[k]) * 3 + r3] += CAP[k];
      if (fount[k]) CAPRF[(ph * 3 + terr[k]) * 3 + r3] += CAP[k];
      const o = ctx.occ.get(k);
      if (o !== undefined) { const od = ctx.drag.get(o); if (od) OB[((((TI(od.team) * NPH + ph) * 3 + terr[k]) * 3 + r3) * 2) + fount[k]] += CAP[k]; }
      else if (ctx.pearls.has(k) && ctx.pearls.get(k) >= 0) DB[(ph * 3 + terr[k]) * 3 + r3] += CAP[k];
    }
    // head-rounds
    const pl = []; for (const [k, o] of ctx.pearls) if (o === -1) pl.push({ k, len: 0 });
    bfs(pl, distP, null);
    for (const ti of [0, 1]) for (const h of heads[ti]) {
      const lc = LC(h.len); HR[ti][lc][b]++; HRT[ti][rel(h.k, ti)][b]++;
      HRP[ti][(LCS(h.len) * 4 + DNP(distP[h.k])) * NPH + ph]++;
      if (ti === us) { const og = origin.get(h.d.id); if (og !== undefined) ORGHR[og * NB + b]++; }
    }
  }
  const initialSet = new Set(); if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) initialSet.add(i);

  const hooks = {
    turn(d, round, ctx) {
      if (round !== lastRound) { lastRound = round; curRound = round; roundStart(round, ctx); }
      label.set(d.id, null);
    },
    indicator(e, round, ctx) { label.set(e.id, e.text); },
    action(d, e, round, ctx) {
      const ti = TI(d.team), b = Math.min(NB - 1, Math.floor(round / 10));
      TURNS[ti][b]++; if (e.action && e.action.kind === 'move') STEPS[ti][b] += e.action.steps.length;
      if (ti === us) ACT[KI[labelKind(label.get(d.id))] * NB + b]++;
    },
    eat(d, k, o, round, ctx) {
      if (o >= 0) return;
      const ti = TI(d.team), b = Math.min(NB - 1, Math.floor(round / 10));
      EAT[ti][LC(d.body.length)][rel(k, ti)][b]++;
      if (ti === us) {
        ACTE[KI[labelKind(label.get(d.id))] * NB + b]++;
        const og = origin.get(d.id); if (og !== undefined) ORGE[og * NB + b]++;
      }
      const p = live.get(k);
      if (p) { live.delete(k); p.eLcs = LCS(d.body.length); finalize(p, ti, round); }
    },
    split(p, ch, e, round, ctx) {
      if (TI(p.team) !== us) return;
      const og = OI[splitOrigin(label.get(p.id))];
      origin.set(ch.id, og); ORG[og * NB + Math.min(NB - 1, Math.floor(round / 10))]++;
    },
    end(rounds, ctx) { for (const p of live.values()) { finalize(p, 2, rounds - 1); chkX.liveLeft++; } live.clear(); },
  };
  const g = ML.perGame(R, linfo, hooks);
  // natural spawns seen by this pass (r > 0 spawns + round-0 spawns that were not initial) vs the ledger's count
  if (spawnsSeen !== g.natSpawned) chkX.spawnMismatch = spawnsSeen - g.natSpawned;
  const sonar = [0, 0];
  const teamOf = new Map(); for (const d0 of M.initialDragons) teamOf.set(d0.id, TI(d0.team));
  for (const e of R.events) if (e.type === 'dragonSplit') teamOf.set(e.childId, TI(e.team));
  for (const [id, n] of R.sonarBySender || []) { const t = teamOf.get(id); if (t !== undefined) sonar[t] += n; }
  const team = tm => {
    const T = g[tm], fl = T.fl, F = c => fl[ML.FI[c]];
    const dropEat = z(NB); for (const o of ML.ORIG.slice(1)) { const a = F('eat_' + o); for (let i = 0; i < NB; i++) dropEat[i] += a[i]; }
    const spr = z(NB); for (const c of ['spr_ram', 'spr_eat', 'spr_esc', 'spr_other']) { const a = F(c); for (let i = 0; i < NB; i++) spr[i] += a[i]; }
    return { eatNat: F('eat_nat'), eatDrop: dropEat, spr, sprN: F('spr_n'), splitN: F('split_n'), faults: F('dn_fault').reduce((s, v) => s + v, 0),
      units: T.st.units, king: T.st.king, total: T.st.total, splits: T.splits };
  };
  // independent recount: every online game; top games whose key hash (FNV-1a) is divisible by 5 (time budget; the parse is shared)
  const fnv = s => { let x = 2166136261; for (let i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 16777619); } return x >>> 0; };
  const doRc = info.src !== 'top' || !info.key || fnv(info.key) % 5 === 0;
  const rc = doRc ? recount(R, info, { W, H, CAP, MIR, symOk, spawnList, terr }) : null;
  // compare the recount with the main pass (all expected 0)
  const chkR = doRc ? { nat: 0, hr: 0, race: 0, ob: 0, sbm: 0, capr: 0 } : null;
  if (doRc) {
  for (const ti of [0, 1]) {
    const tm = ti ? 'B' : 'A', ph = z(NPH);
    g[tm].fl[ML.FI.eat_nat].forEach((v, i) => { ph[PH(i * 10)] += v; });
    for (let p = 0; p < NPH; p++) if (ph[p] !== rc.nat[ti][p]) chkR.nat++;
    const hr = z(NPH); for (let lc = 0; lc < 6; lc++) HR[ti][lc].forEach((v, i) => { hr[PH(i * 10)] += v; });
    for (let p = 0; p < NPH; p++) if (hr[p] !== rc.hr[ti][p]) chkR.hr++;
  }
  { // race3 x fate by phase
    const mine = {}; for (const [k, n] of Object.entries(RACE)) { const [ph, , , cls, , fate] = k.split('|').map(Number); const r3 = cls === 8 ? 1 : cls <= 2 ? 2 : cls === 3 ? 1 : 0; const kk = ph + '|' + r3 + '|' + fate; mine[kk] = (mine[kk] || 0) + n; }
    const keys = new Set([...Object.keys(mine), ...Object.keys(rc.race)]);
    for (const kk of keys) if ((mine[kk] || 0) !== (rc.race[kk] || 0)) chkR.race++;
  }
  { // expected body blocking per team (sum) and mirror blocks by blocker
    const obT = [0, 0]; for (let t = 0; t < 2; t++) for (let i = 0; i < NPH * 3 * 3 * 2; i++) obT[t] += OB[t * NPH * 3 * 3 * 2 + i];
    for (let t = 0; t < 2; t++) if (Math.abs(obT[t] - rc.ob[t]) > 1e-6) chkR.ob++;
    const sb = z(5); for (let i = 0; i < SBM.length; i++) sb[Math.floor(i / 9) % 5] += SBM[i];
    for (let bl = 0; bl < 5; bl++) if (sb[bl] !== rc.sbm[bl]) chkR.sbm++;
    const cr = z(3); for (let i = 0; i < CAPR.length; i++) cr[i % 3] += CAPR[i];
    for (let r = 0; r < 3; r++) if (Math.abs(cr[r] - rc.capr[r]) > 1e-6) chkR.capr++;
  }
  }
  const r4 = a => a.map(x => Math.round(x * 1e4) / 1e4);
  return {
    rounds: g.rounds, endReason: g.endReason, winner: g.winner, W, H, variant: V.tag, vhow: V.how, sym: sym || null, symOk,
    natStart: g.natStart, natSpawned: g.natSpawned, chk: g.chk, chkX, chkR, sonar,
    capTerr: [0, 1, 2].map(t => { let s = 0; for (const k of spawnList) if (terr[k] === t) s += CAP[k]; return Math.round(s * 1e4) / 1e4; }),
    terrTiles: g.terrTiles,
    A: team('A'), B: team('B'),
    HR, HRT, HRP, EAT, TURNS, STEPS, RACE, DEL, NEAR, CAPR: r4(CAPR), CAPRF: r4(CAPRF), OB: r4(OB), PB: r4(PB), PBR: r4(PBR), DB: r4(DB), SBM, STEAL,
    ACT: us >= 0 ? ACT : null, ACTE: us >= 0 ? ACTE : null, ORG: us >= 0 ? ORG : null, ORGE: us >= 0 ? ORGE : null, ORGHR: us >= 0 ? ORGHR : null,
  };
}

// ---------------------------------------------------------------------------------------------------------------
// Independent recount: no ledger, no step simulation, no territory-analysis geometry. Own graph from the map arrays,
// own body tracking (dragonUpdate head/tail, dragonSplit bodies, dragonDeath), own natural-pearl tracking from event order.
function recount(R, info, shared) {
  const M = R.match.map, W = M.width, H = M.height, N = W * H;
  const { CAP, MIR, symOk, spawnList } = shared; // pearl layout / capacity / mirror come from the map file (shared input, like the parser)
  // graph: an edge between (x,y) and its neighbour is kelp if the map marks it; portals pair edges (rules/kelp-and-portals.md)
  const hEdge = (x, y) => { // north edge of row y (y in 0..H), column x
    const yy = ((y % H) + H) % H; return M.initialHEdges[yy * W + x] === 1 || (yy === 0 && M.initialHEdges[H * W + x] === 1);
  };
  const vEdge = (x, y) => { const xx = ((x % W) + W) % W; return M.initialVEdges[y * (W + 1) + xx] === 1 || (xx === 0 && M.initialVEdges[y * (W + 1) + W] === 1); };
  const pmap = new Map();
  const norm = e => { // edge as the tile on its south / east side with side N / W
    if (e.side === 'N') return [e.x, e.y, 'N']; if (e.side === 'W') return [e.x, e.y, 'W'];
    if (e.side === 'S') return [e.x, (e.y + 1) % H, 'N']; return [(e.x + 1) % W, e.y, 'W'];
  };
  for (const pr of M.portals || []) { if (pr.length !== 2) continue; const a = norm(pr[0]), b = norm(pr[1]); pmap.set(a.join(','), b); pmap.set(b.join(','), a); }
  const adj = new Int32Array(N * 4).fill(-1);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const k = y * W + x;
    // N: edge (x, y, N); leaving north through a portal pair (px, py, N) arrives at (px, py - 1)... rule: entering from one side exits the other side of the partner
    const cand = [
      [[x, y, 'N'], () => hEdge(x, y), [x, (y - 1 + H) % H], (p) => [p[0], (p[1] - 1 + H) % H]],
      [[(x + 1) % W, y, 'W'], () => vEdge(x + 1, y), [(x + 1) % W, y], (p) => [p[0], p[1]]],
      [[x, (y + 1) % H, 'N'], () => hEdge(x, y + 1), [x, (y + 1) % H], (p) => [p[0], p[1]]],
      [[x, y, 'W'], () => vEdge(x, y), [(x - 1 + W) % W, y], (p) => [(p[0] - 1 + W) % W, p[1]]],
    ];
    for (let j = 0; j < 4; j++) {
      const [e, kelp, plain, via] = cand[j];
      const p = pmap.get(e.join(','));
      let t;
      if (p) t = via(p); else if (kelp()) t = null; else t = plain;
      if (t) adj[k * 4 + j] = t[1] * W + t[0];
    }
  }
  const Q = new Int32Array(N + 8);
  const bfsFrom = (srcs, d) => { d.fill(-1); let qh = 0, qt = 0; for (const s of srcs) if (d[s] < 0) { d[s] = 0; Q[qt++] = s; } while (qh < qt) { const k = Q[qh++]; for (let j = 0; j < 4; j++) { const u = adj[k * 4 + j]; if (u >= 0 && d[u] < 0) { d[u] = d[k] + 1; Q[qt++] = u; } } } };
  const dA = new Int32Array(N), dB = new Int32Array(N);
  const PHr = r => r < 50 ? 0 : r < 100 ? 1 : r < 250 ? 2 : r < 350 ? 3 : r < 450 ? 4 : 5;
  const dragons = new Map(); // id -> {team 0/1, body [[x,y]...]}
  for (const d0 of M.initialDragons) dragons.set(d0.id, { team: d0.team === 'A' ? 0 : 1, body: d0.body.map(s => [s.x, s.y]) });
  const pearl = new Map(); // tile -> {nat, r0, r3}
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearl.set(i, { nat: true, r0: 0, r3: -1 });
  const out = { nat: [new Array(6).fill(0), new Array(6).fill(0)], hr: [new Array(6).fill(0), new Array(6).fill(0)], race: {}, ob: [0, 0], sbm: [0, 0, 0, 0, 0], capr: [0, 0, 0] };
  let round = -1, inTurn = false, curTeam = -1, spawnedThisRound = [];
  const occAt = () => { const o = new Map(); for (const [id, d] of dragons) for (const s of d.body) o.set(s[1] * W + s[0], d.team); return o; };
  const flushRoundStart = () => { // at the first turn of the round: state after the round's spawns
    const hA = [], hB = [];
    for (const d of dragons.values()) (d.team ? hB : hA).push(d.body[0][1] * W + d.body[0][0]);
    bfsFrom(hA, dA); bfsFrom(hB, dB);
    const r3 = k => { const a = dA[k] < 0 ? 999 : dA[k], b = dB[k] < 0 ? 999 : dB[k]; return a < b ? 0 : a === b ? 1 : 2; };
    const ph = PHr(round);
    out.hr[0][ph] += hA.length; out.hr[1][ph] += hB.length;
    for (const [k, p] of pearl) if (p.nat && p.r3 < 0) p.r3 = r3(k);
    const occ = occAt();
    for (const k of spawnList) { out.capr[r3(k)] += CAP[k]; const t = occ.get(k); if (t !== undefined) out.ob[t] += CAP[k]; }
    if (symOk && round > 0) {
      const set = new Set(spawnedThisRound);
      for (const k of spawnedThisRound) {
        const m = MIR[k]; if (m === k || set.has(m) || !(CAP[m] > 0)) continue;
        const t = occ.get(m); let bl;
        if (t !== undefined) bl = t; else if (pearl.has(m)) bl = pearl.get(m).nat ? 2 : 3; else bl = 4;
        out.sbm[bl]++;
      }
    }
  };
  let firstTurnSeen = false;
  for (const e of R.events) {
    switch (e.type) {
      case 'roundStart': round = e.round; inTurn = false; firstTurnSeen = false; spawnedThisRound = []; break;
      case 'turnStart':
        if (!firstTurnSeen) { firstTurnSeen = true; flushRoundStart(); }
        inTurn = true; { const d = dragons.get(e.id); curTeam = d ? d.team : -1; } break;
      case 'tileChange': {
        const k = e.tile.y * W + e.tile.x;
        if (e.hasPearl) {
          if (!inTurn && round >= 0) { pearl.set(k, { nat: true, r0: round, r3: -1 }); spawnedThisRound.push(k); }
          else pearl.set(k, { nat: false });
        } else {
          const p = pearl.get(k); pearl.delete(k);
          if (p && p.nat && curTeam >= 0 && round >= 0) {
            out.nat[curTeam][PHr(round)]++;
            const kk = PHr(p.r0) + '|' + p.r3 + '|' + curTeam; out.race[kk] = (out.race[kk] || 0) + 1;
          }
        }
        break;
      }
      case 'dragonUpdate': {
        const d = dragons.get(e.id); if (!d) break;
        const b = d.body;
        if (b[0][0] !== e.head.x || b[0][1] !== e.head.y) b.unshift([e.head.x, e.head.y]);
        while (b.length > 1 && (b[b.length - 1][0] !== e.tail.x || b[b.length - 1][1] !== e.tail.y)) b.pop();
        break;
      }
      case 'dragonSplit': {
        const p = dragons.get(e.parentId); if (p) p.body = e.parentBody.map(s => [s.x, s.y]);
        dragons.set(e.childId, { team: e.team === 'A' ? 0 : 1, body: e.childBody.map(s => [s.x, s.y]) });
        break;
      }
      case 'dragonDeath': dragons.delete(e.id); break;
    }
  }
  const lastR = round;
  for (const [k, p] of pearl) if (p.nat) { const kk = PHr(p.r0) + '|' + (p.r3 < 0 ? 1 : p.r3) + '|2'; out.race[kk] = (out.race[kk] || 0) + 1; }
  return out;
}

// ---------------------------------------------------------------------------------------------------------------
// tasks, workers
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(l => l.trim()).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];
function topTasks(keysArg) {
  const seen = new Set(), idx = [];
  for (const r of readJsonl(path.join(TOP, 'index.jsonl'))) { const k = r.battleId + ':' + r.gameId; if (seen.has(k)) continue; seen.add(k); idx.push(r); }
  const byKey = new Map(idx.map(r => [r.battleId + ':' + r.gameId, r]));
  const keys = !keysArg || keysArg === 'all' ? [...byKey.keys()] : fs.readFileSync(path.resolve(ROOT, keysArg), 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  const out = [];
  for (const k of keys) {
    const r = byKey.get(k); if (!r) continue;
    const f = path.join(TOP, String(r.battleId), r.gameId + '.replay.gz'); if (!fs.existsSync(f)) continue;
    out.push({ key: k, file: f, info: { src: 'top', map: r.map, gameId: r.gameId, battleId: r.battleId, teamA: r.teamA, teamB: r.teamB, eloA: r.eloA, eloB: r.eloB,
      rankA: r.rankA, rankB: r.rankB, winnerIdx: r.winner ? String(r.winner).toUpperCase() : null, ranked: !!r.ranked, at: r.at, us: null } });
  }
  return out;
}
function onlineTasks(set) {
  const dir = path.join(ONLINE, set), idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
  let names = {};
  try { for (const t of JSON.parse(fs.readFileSync(path.join(TOP, 'leaderboard.json'), 'utf8'))) names[t.id] = t.name; } catch { /* optional */ }
  const out = [];
  for (const g of idx.games || idx) {
    const f = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
    const us = String(g.ourSide).toUpperCase(), opp = names[g.opponentTeam] || String(g.opponentTeam);
    out.push({ key: set + ':' + g.gameId, file: f, info: { src: 'online', set, map: g.mapName, gameId: g.gameId, teamA: us === 'A' ? set : opp, teamB: us === 'B' ? set : opp,
      oppId: g.opponentTeam, opp, winnerIdx: g.winner ? String(g.winner).toUpperCase() : null, at: g.completedAt, us, sub: g.ourSubmission } });
  }
  return out;
}
function workerMain() {
  // default: the raw Cap'n Proto event decoder (exp/intake-gap/rawload.js, checked event by event against the official conversion
  // by exp/intake-gap/validate_raw.js); INTAKE_OFFICIAL=1 uses the official per-event conversion (makeFastLoader)
  const load = process.env.INTAKE_OFFICIAL === '1' ? makeFastLoader() : require('./rawload.js').load;
  process.on('message', task => {
    try {
      const R = load(task.file);
      const res = analyse(R, { ...task.info, key: task.key });
      process.send({ key: task.key, line: JSON.stringify({ key: task.key, ...task.info, seed: R.seed, kind: ML.R500.includes(task.info.map) ? 'r500' : 'elim', ...res }) });
    } catch (err) { process.send({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 6).join(' | ') }); }
  });
}
async function extract(tasks, cacheFile, jobs, limit) {
  fs.mkdirSync(path.dirname(cacheFile), { recursive: true });
  const done = new Set();
  if (fs.existsSync(cacheFile)) for (const l of fs.readFileSync(cacheFile, 'utf8').split('\n')) { const m = /^\{"key":"([^"]+)"/.exec(l); if (m) done.add(m[1]); }
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
        else fs.writeSync(fd, m.line + '\n');
        n++;
        if (n % 50 === 0) console.log(`  ${n}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
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
async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const jobs = Math.max(1, Math.min(3, +opt('jobs', 3))), limit = +opt('limit', Infinity);
  if (argv[0] === 'top') { // hash order (FNV-1a of the key): any prefix of the run is a uniform sample of the population
    const h = s => { let x = 2166136261; for (let i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 16777619); } return x >>> 0; };
    let tasks = topTasks(opt('keys', 'all')).sort((a, b) => h(a.key) - h(b.key));
    const part = opt('part', null); // "i/n": the keys whose hash (another multiplier) mod n is i, cache top-p<i>.jsonl
    if (part) { const [i, n] = part.split('/').map(Number); const h2 = s => Math.imul(h(s), 2654435761) >>> 0; tasks = tasks.filter(t => h2(t.key) % n === i); return extract(tasks, path.join(CACHE, 'top-p' + i + '.jsonl'), jobs, limit); }
    return extract(tasks, path.join(CACHE, opt('name', 'top') + '.jsonl'), jobs, limit);
  }
  if (argv[0] === 'online') {
    const sets = []; for (let i = 1; i < argv.length; i++) { if (argv[i].startsWith('--')) { i++; continue; } sets.push(argv[i]); }
    for (const s of sets) await extract(onlineTasks(s), path.join(CACHE, 'online-' + s + '.jsonl'), jobs, limit);
    return;
  }
  if (argv[0] === 'one') { // debug: node extract.js one <file> <map> [us]
    const load = process.env.INTAKE_OFFICIAL === '1' ? makeFastLoader() : require('./rawload.js').load; const R = load(argv[1]);
    const res = analyse(R, { map: argv[2], us: argv[3] || null, gameId: null });
    console.log(JSON.stringify({ chk: res.chk, chkX: res.chkX, chkR: res.chkR, variant: res.variant, sym: res.sym, symOk: res.symOk, rounds: res.rounds }));
    return;
  }
  console.error('usage: see the header'); process.exit(2);
}
module.exports = { analyse, recount, makeFastLoader, labelKind, splitOrigin, renewal, PH, LC, LCS, RC, KINDS, ORIGS, NPH, NB };
if (require.main === module) main().catch(err => { console.error(err); process.exit(1); });
