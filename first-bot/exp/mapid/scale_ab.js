#!/usr/bin/env node
// exp/mapid/scale_ab.js — a copy of tools/decisions_scale.js (2026-09-30) for the layout study (research/experiments/cand-mapid.md,
// part B): the map segment of Schooltime and Devil games carries the true pearl layout (exp/mapid/cache/feat.jsonl, natural
// spawns), and only those games are read. Everything else (rules, groups, outcomes, trees) is the original's.
// usage (repository root): node exp/mapid/scale_ab.js --jobs 3 --out exp/mapid/cache/scale-ab
// Large-scale decision learning by segment. Reads the decision dataset of tools/decisions.js (data/decisions) only:
// no games, no network. Top-vs-top rules R1-R8 of research/observations/top-decisions.md and new rule families (pearl
// targeting, portals, sonar, trapped / dead ends, early growth, sacrifices and king feeding) are measured in cells of
// map (Prisoners Dilemma split by start dragons) x phase x length class, per group (top teams, top winners, top losers,
// each of our online submissions, the top opponents of our online games) and per team. CART trees of each decision
// type (fitted on a sample of top games, with the map type, phase and start dragons among the features) add learned
// leaves with the same comparisons. Games stream through <= 4 worker threads; memory is bounded by the cell arrays.
//
// usage: node tools/decisions_scale.js [--top top-all] [--sets s1,s2,...] [--jobs 4] [--out data/decisions/scale]
//                                      [--tree-mod 8] [--tree-cap 300000] [--boot 400] [--index-rows N] [--alias a=b,..]
//                                      [--limit N]
//   --top       top-vs-top set (default top-all if present, else top-20260929a)
//   --sets      online sets (default: every data/decisions/<set> whose games have our side)
//   --tree-mod  trees are fitted on the top games whose key hash is 0 mod this (default 8: one in eight)
//   --tree-cap  rows per decision type kept for tree fitting (uniform reservoir, weights rescaled)
//   --index-rows only the games among the first N rows of data/top/index.jsonl (a dated corpus; the collector appends)
//   --alias     submissions counted as another one (default 12284=12142: merge2 uploaded again); 'none' = no alias
//   --limit     testing only: the first N usable top games
// Output: <out>.json (every number; input of tools/decisions_hyp.js) and <out>.md (Korean tables).
//
// Excluded: top games in which a team did not play: 0 pings and <= 3 splits in >= 100 rounds while that team pings in
// most games, for a team with >= 5 such games (the broken SSS bot of research/observations/top-timing.md), or no valid
// action on >= 20% of its turns.
// Groups: T = both teams of top games, TW / TL = winner / loser (draws in neither), O<sub> = our side of an online set
// by submission id, X = the top opponents of our online games (all sets pooled).
// Cells: rates are weighted turn rates (plain turns were sampled 1 in 8 with weight 8). "Per game" = per team-game.
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

const ROOT = path.resolve(__dirname, '..', '..'), DEC = path.join(ROOT, 'data', 'decisions');
const MAPS = ['Devil a', 'Devil b', 'Schooltime a', 'Schooltime b', 'other'];
const ELIM_MAPS = new Set(['Devil a', 'Devil b']); // as tools/decisions_lib.js (Devil); Schooltime is a round-500 map
const PHASES = ['r0-99', 'r100-249', 'r250-349', 'r350-449', 'r450+'];
const LENS = ['2', '3-4', '5-7', '8-11', '12-19', '20+'];
const NCELL = MAPS.length * PHASES.length * LENS.length;
const OUTS = ['net10', 'net30', 'al10', 'eat10', 'kc10', 'fk'];
const NO = OUTS.length, STRIDE = 5 + 2 * NO; // cell: w, n, a, d, n1, s1[NO], s0[NO]
const SUB_NAMES = { 10365: 'g4-r4 기준', 11939: 'px-king-v2', 11987: 'avoid6', 12042: 'portal1', 12096: 'px8', 12142: 'merge2 (bot/)', 12186: 'swarm8', 12238: 'px9d', 12284: 'merge2 반복' };
// the same bot uploaded again for a replicate set counts as one group (12284 = bot/ merge2 again, research/experiments/
// online-tests.md 09-30 09:35). --alias a=b,c=d replaces this map; --alias none keeps every submission apart.
const SUB_ALIAS_DEFAULT = { 12284: 12142 };
const LAYOUT = new Map();
for (const l of fs.readFileSync(path.join(__dirname, 'cache', 'feat.jsonl'), 'utf8').split('\n')) { if (!l.trim()) continue; const x = JSON.parse(l); LAYOUT.set(+x.gameId, x.layout); }
const layOf = g => LAYOUT.get(+String(g.key).split(':').pop());
const mapSegOf = g => (g.map === 'Schooltime' || g.map === 'Devil') && (layOf(g) === 'a' || layOf(g) === 'b') ? g.map + ' ' + layOf(g) : 'other';
const mix32 = x => { x ^= x >>> 16; x = Math.imul(x, 0x7feb352d); x ^= x >>> 15; x = Math.imul(x, 0x846ca68b); x ^= x >>> 16; return x >>> 0; };
const keyHash = k => mix32(parseInt(String(k).replace(/\D/g, '').slice(-9), 10) || 1);

// ---------------------------------------------------------------------------------------------------------------
// Row parsing: bytes of the gunzipped tsv straight into a Float64Array in canonical column order (no strings).
// String columns become codes: first char, or first*256+second for two chars ('' = 0).
const STR_COLS = new Set(['tm', 'fac', 'act', 'd1', 'fate', 'hitT', 'dwhy']);
const CH = s => s.length === 0 ? 0 : s.length === 1 ? s.charCodeAt(0) : s.charCodeAt(0) * 256 + s.charCodeAt(1);
const A_M = CH('M'), A_P = CH('P'), TM_A = CH('A');
const SK_FATES = new Set([CH('S'), CH('W'), CH('Aq'), CH('Ax')]);
const DEATH_CODES = { H: CH('H'), O: CH('O'), S: CH('S'), W: CH('W'), Ap: CH('Ap'), Aq: CH('Aq'), Ax: CH('Ax'), At: CH('At'), An: CH('An') };
const HT_A = CH('A');
function forEachRow(buf, COLS, onRow) {
  let i = buf.indexOf(10); if (i < 0) return 0;
  const header = buf.toString('utf8', 0, i).split('\t');
  const K = new Map(COLS.map((k, j) => [k, j]));
  const map = header.map(h => K.has(h) ? K.get(h) : -1), isStr = header.map(h => STR_COLS.has(h) ? 1 : 0), nc = header.length;
  const f = new Float64Array(COLS.length).fill(NaN);
  let col = 0, val = 0, neg = false, code = 0, len = 0, rows = 0;
  for (i = i + 1; i < buf.length; i++) {
    const b = buf[i];
    if (b === 9 || b === 10) {
      const m = map[col];
      if (m >= 0) f[m] = isStr[col] ? code : (neg ? -val : val);
      col++; val = 0; neg = false; code = 0; len = 0;
      if (b === 10) { if (col === nc) { onRow(f); rows++; } col = 0; }
      continue;
    }
    if (isStr[col]) { if (len < 2) code = code * 256 + b; len++; }
    else if (b === 45) neg = true; else val = val * 10 + (b - 48);
  }
  return rows;
}

// Named view of a parsed row (one reused object; fields are numbers).
function makeView(COLS) {
  const I = Object.fromEntries(COLS.map((k, j) => [k, j]));
  const z = {};
  const names = ['r', 'L', 'free', 'nbE', 'nbA', 'room', 'roomMax', 'tFree', 'eN', 'eNs', 'eNr', 'eNrs', 'eD0', 'eM0', 'eL', 'eAft', 'eFw', 'eLmin',
    'safe1', 'exp1', 'safe2', 'oppN', 'oppL', 'oppD', 'pN', 'pD0', 'pEd', 'pDang', 'aN', 'aD', 'aL', 'aMaxL', 'aDg', 'aLg', 'kD', 'eDg', 'U', 'TL', 'TT',
    'king', 'kRank', 'EU', 'EL', 'ptlN', 'ptlV', 'k', 'c', 'eD1', 'eM1', 'pD1', 'aDg1', 'endExp', 'roomAct', 'ate', 'ptlK', 'hitL', 'ram', 'al5',
    'al10', 'eat10', 'eatS10', 'F10', 'Fu10', 'kill10', 'feedS', 'feedE', 'feedK', 'cAl10', 'w', 'sN', 'sA', 'sE', 'rA', 'rE', 'pN3', 'sp5', 'spD', 'spD1',
    'F30', 'Fu30', 'kill30', 'kc10', 'act', 'fate', 'tm', 'hitT', 'dwhy', 'born', 'init'];
  const idx = names.map(k => I[k]);
  return {
    z,
    fill(f) {
      for (let j = 0; j < names.length; j++) z[names[j]] = f[idx[j]];
      z.move = z.act === A_M; z.mp = z.act === A_M || z.act === A_P; z.split = z.act === A_P; z.alive = z.fate === 0;
      z.sk = SK_FATES.has(z.fate) && z.free >= 1 ? 1 : 0;
      z.net10 = z.F10 - z.L + z.kill10; z.net30 = z.F30 - z.L + z.kill30;
      z.eDelta = z.eD0 <= 8 && z.eD1 <= 8 ? z.eD1 - z.eD0 : z.eM1 - z.eM0;
      const r = z.r, L = z.L;
      z.ph = r < 100 ? 0 : r < 250 ? 1 : r < 350 ? 2 : r < 450 ? 3 : 4;
      z.lc = L <= 2 ? 0 : L <= 4 ? 1 : L <= 7 ? 2 : L <= 11 ? 3 : L <= 19 ? 4 : 5;
      z.drop = Math.ceil(L / 2);
      z.fk = z.sk ? z.feedK : 0;
      return z;
    },
  };
}

// ---------------------------------------------------------------------------------------------------------------
// Rule catalog. kind 'bin': rate = weighted share of the population doing act (outcomes compared yes / no);
// 'val': rate = sum(w*act) / sum(w*den) (den default 1). cur = outcome used for the impact of a binary rule.
const B = (id, fam, name, pop, act, cur = 'net10') => ({ id, fam, name, kind: 'bin', pop, act: z => (act(z) ? 1 : 0), cur });
const V = (id, fam, name, pop, act, den = null) => ({ id, fam, name, kind: 'val', pop, act, den });
const RULES = [
  // splits and early growth
  B('R1', 'split', '길이 4 조각이 2+2로 분열', z => z.L === 4 && z.mp, z => z.split),
  B('R2', 'split', '길이 5–9, 방 ≥6, r≤166: 분열', z => z.L >= 5 && z.L <= 9 && z.room >= 6 && z.r <= 166 && z.mp, z => z.split),
  B('C3', 'split', '길이 ≥10, 방 ≥6: 분열', z => z.L >= 10 && z.room >= 6 && z.mp, z => z.split),
  B('E1', 'split', 'r<50, 길이 ≥4: 분열(초반 성장)', z => z.r < 50 && z.L >= 4 && z.mp, z => z.split),
  B('C4', 'split', '분열할 때 자식이 2칸', z => z.split, z => z.c === 2),
  B('C5', 'split', '길이 ≥6이 분열할 때 부모가 ≤3칸만 남김(stub)', z => z.split && z.L >= 6, z => z.L - z.c <= 3),
  B('D3', 'trap', '길이 ≥8, 좁은 방(1–5): 분열(통로 고리)', z => z.L >= 8 && z.room >= 1 && z.room <= 5 && z.mp, z => z.split),
  // long-dragon safety
  B('R5', 'safety', '길이 ≥6, 안전한 한 걸음과 노출 한 걸음이 함께 있음: 노출 칸에서 끝냄', z => z.L >= 6 && z.eNs >= 1 && z.move && z.alive && z.safe1 >= 1 && z.exp1 >= 1, z => z.endExp === 1),
  B('R8', 'safety', '길이 ≥6, 한 걸음은 모두 노출, 질주 탈출 있음: 질주', z => z.L >= 6 && z.eNs >= 1 && z.move && z.alive && z.safe1 === 0 && z.exp1 > 0 && z.safe2 > 0, z => z.k >= 2),
  B('A3', 'safety', '길이 ≥6, 더 짧은 적 머리가 3–6칸(도달 밖): 다가감', z => z.L >= 6 && z.eNs >= 1 && z.move && z.alive && z.exp1 === 0 && z.eNrs === 0 && z.eD0 >= 3 && z.eD0 <= 6, z => z.eDelta < 0),
  // small fragments and fights
  B('R4', 'fight', '길이 ≤3, 아군 보임, 같거나 긴 적 머리를 박을 수 있음(적 ≤2): 박음', z => z.L <= 3 && z.oppN >= 1 && z.aN >= 1 && z.oppL >= z.L && z.eN <= 2 && z.mp, z => z.ram === 1),
  B('B1a', 'fight', '길이 ≤4, 아군 없음, 더 긴 적 머리를 박을 수 있음: 박음', z => z.L <= 4 && z.oppN >= 1 && z.aN === 0 && z.oppL > z.L && z.mp, z => z.ram === 1),
  B('B1b', 'fight', '길이 ≤4, 박을 수 있는 적이 모두 더 짧음: 박음', z => z.L <= 4 && z.oppN >= 1 && z.oppL < z.L && z.mp, z => z.ram === 1),
  B('B3', 'fight', '길이 ≤4, 적 머리가 바로 옆: 한 걸음으로 박음', z => z.L <= 4 && z.nbE >= 1 && z.mp, z => z.ram === 1 && z.k === 1),
  B('R7', 'fight', '길이 ≤4, 적 머리 3–8칸(박을 수 없음): 다가감', z => z.L <= 4 && z.eN >= 1 && z.oppN === 0 && z.move && z.alive && z.eD0 >= 3 && z.eD0 <= 8, z => z.eD1 < z.eD0),
  // sacrifices and the king
  B('R3', 'king', '길이 ≥8 아군이 3칸 안, r≥350, 빈 이웃 있음: 자해', z => z.free >= 1 && z.aLg >= 8 && z.aDg <= 3 && z.r >= 350, z => z.sk, 'fk'),
  B('K1', 'king', 'r≥250, 4칸 이상 긴 아군 머리가 3칸 안, 적 없음: 자해', z => z.free >= 1 && z.king === 0 && z.r >= 250 && z.aLg >= z.L + 4 && z.aDg <= 3 && z.eN === 0, z => z.sk, 'fk'),
  B('K5', 'king', '빈 이웃이 있는 턴: 자해', z => z.free >= 1, z => z.sk, 'fk'),
  V('K2', 'king', '희생 진주 중 20라운드 안에 우리 왕이 먹은 몫', z => z.sk === 1, z => z.feedK, z => z.drop),
  V('K2s', 'king', '희생 진주 중 우리 팀이 먹은 몫', z => z.sk === 1, z => z.feedS, z => z.drop),
  V('K2e', 'king', '희생 진주 중 적이 먹은 몫', z => z.sk === 1, z => z.feedE, z => z.drop),
  V('K6', 'king', '희생 때 가장 가까운 아군 머리까지 거리(맨해튼)', z => z.sk === 1 && z.aDg < 99, z => z.aDg),
  V('K7', 'king', '희생 때 가장 가까운 아군 길이', z => z.sk === 1 && z.aLg > 0, z => z.aLg),
  V('K8', 'king', '희생 때 왕까지 거리(맨해튼)', z => z.sk === 1 && z.kD < 99, z => z.kD),
  B('K3', 'king', '왕, r≥300: 가장 가까운 아군 쪽으로 감', z => z.king === 1 && z.r >= 300 && z.move && z.alive && z.aDg < 99, z => z.aDg1 < z.aDg),
  V('K4', 'king', '왕(r≥250)의 다음 10라운드 먹이', z => z.king === 1 && z.r >= 250, z => z.eat10),
  V('K4s', 'king', '왕(r≥250)의 다음 10라운드 먹이 중 희생 진주', z => z.king === 1 && z.r >= 250, z => z.eatS10),
  // pearls
  B('P1', 'pearl', '3걸음 안에 진주: 진주 쪽으로 감', z => z.move && z.pD0 <= 3, z => z.pD1 < z.pD0),
  B('P2', 'pearl', '3걸음 안의 진주에 적이 같거나 더 가까움: 그래도 감', z => z.move && z.pD0 <= 3 && z.pEd <= z.pD0, z => z.pD1 < z.pD0),
  B('P3', 'pearl', '3걸음 안의 진주가 적 도달 안: 그래도 감', z => z.move && z.pD0 <= 3 && z.pDang === 1, z => z.pD1 < z.pD0),
  B('P4', 'pearl', '진주가 2걸음, 적이 2걸음 안, 길이 ≥3: 질주로 이번 턴에 먹음', z => z.move && z.pD0 === 2 && z.pEd <= 2 && z.L >= 3, z => z.k >= 2 && z.ate >= 1),
  B('P5', 'pearl', '시야에 진주 없음, 5라운드 안에 생길 칸이 4걸음 안: 그 칸 쪽으로 감', z => z.move && z.alive && z.pN === 0 && z.spD <= 4, z => z.spD1 < z.spD),
  V('P6', 'pearl', '이동 턴당 먹은 진주', z => z.move, z => z.ate),
  V('P7', 'pearl', '길이 ≥3 이동 턴의 질주 비율', z => z.move && z.L >= 3, z => (z.k >= 2 ? 1 : 0)),
  // portals
  B('R6', 'portal', '머리 칸에 포털 변, 4칸 안에 진주 없음, 빈 이웃 ≥2: 포털 통과', z => z.move && z.ptlN >= 1 && z.pD0 >= 5 && z.free >= 2, z => z.ptlK >= 1),
  B('G2', 'portal', '머리 칸에 포털 변, 더 짧은 적의 도달 안: 포털로 빠짐', z => z.move && z.ptlN >= 1 && z.eNrs >= 1, z => z.ptlK >= 1, 'al10'),
  B('G3', 'portal', '머리 칸에 포털 변, 진주가 2걸음 안: 포털 통과', z => z.move && z.ptlN >= 1 && z.pD0 <= 2, z => z.ptlK >= 1),
  B('G4', 'portal', '머리 칸에 포털 변: 포털 통과', z => z.move && z.ptlN >= 1, z => z.ptlK >= 1),
  V('G5', 'portal', '이동 턴당 포털 통과', z => z.move, z => z.ptlK),
  // trapped / dead ends
  B('D1', 'trap', '빈 이웃 없음, 옆에 적 머리: 박음', z => z.free === 0 && z.nbE >= 1 && z.mp, z => z.ram === 1, 'kc10'),
  B('D1b', 'trap', '빈 이웃 없음, 길이 ≥4: 분열', z => z.free === 0 && z.L >= 4, z => z.split, 'al10'),
  B('D2', 'trap', '막다른 곳(모든 첫걸음의 방 < 길이), 길이 ≥4: 분열', z => z.free >= 1 && z.roomMax < z.L && z.L >= 4 && z.mp, z => z.split),
  B('D2b', 'trap', '막다른 곳, 길이 ≥3: 질주', z => z.free >= 1 && z.roomMax < z.L && z.L >= 3 && z.move, z => z.k >= 2),
  B('D2c', 'trap', '막다른 곳: 자해', z => z.free >= 1 && z.roomMax < z.L, z => z.sk, 'fk'),
  // sonar
  V('S1', 'sonar', '턴당 핑 수', z => true, z => z.sN),
  B('S2', 'sonar', '핑을 하나 이상 보냄', z => true, z => z.sN >= 1),
  B('S3', 'sonar', '네 방향 모두 보냄', z => true, z => z.sN === 4),
  V('S4', 'sonar', '핑 하나가 다른 아군에 닿는 비율', z => z.sN >= 1, z => z.sA, z => z.sN),
  V('S5', 'sonar', '핑 하나가 적에 닿는 비율', z => z.sN >= 1, z => z.sE, z => z.sN),
  V('S6', 'sonar', '턴당 받은 아군 메시지', z => true, z => z.rA),
  B('S7', 'sonar', '아군 메시지를 하나 이상 받음', z => true, z => z.rA >= 1),
];
const RI = Object.fromEntries(RULES.map((R, i) => [R.id, i]));

// Decision types for trees (as tools/decisions_learn.js, plus spawn approach and dead ends). Features observable to the
// bot (* = shared by sonar); every tree may also split on the map type (elim), phase (ph) and the map's start dragons.
const F = (name, fn) => [name, fn];
const SEG_FEATS = [F('elim', z => z.elim), F('ph', z => z.ph), F('init', z => z.initN)];
const SPECS = [
  { id: 'a1', title: '긴 드래곤(L≥6), 더 짧은 적 머리가 한 걸음 칸이나 우리 머리에 닿음: 노출 칸에서 끝내는가', yes: '노출 칸에서 끝냄', no: '도달 밖', cur: 'net10',
    pop: z => z.L >= 6 && z.eNs >= 1 && z.move && z.alive && (z.exp1 > 0 || z.eNrs > 0), label: z => (z.endExp === 1 ? 1 : 0),
    feats: [F('safe1', z => z.safe1), F('exp1', z => z.exp1), F('safe2', z => z.safe2), F('eD0', z => Math.min(z.eD0, 9)), F('eL', z => Math.min(z.eL, 12)),
      F('L', z => Math.min(z.L, 40)), F('eNrs', z => z.eNrs), F('room', z => z.room), F('U', z => Math.min(z.U, 64)), F('king*', z => z.king), F('eAft', z => z.eAft)] },
  { id: 'a2', title: '긴 드래곤(L≥6), 한 걸음은 모두 노출, 질주 탈출 있음: 질주하는가', yes: '질주', no: '한 걸음', cur: 'net10',
    pop: z => z.L >= 6 && z.eNs >= 1 && z.move && z.alive && z.safe1 === 0 && z.exp1 > 0 && z.safe2 > 0, label: z => (z.k >= 2 ? 1 : 0),
    feats: [F('safe2', z => z.safe2), F('eD0', z => Math.min(z.eD0, 9)), F('eL', z => Math.min(z.eL, 12)), F('L', z => Math.min(z.L, 40)), F('eNrs', z => z.eNrs),
      F('room', z => z.room), F('U', z => Math.min(z.U, 64)), F('king*', z => z.king)] },
  { id: 'b1', title: '작은 조각(L≤4), 이번 턴에 적 머리를 박을 수 있음: 박는가', yes: '박음', no: '안 박음', cur: 'net10',
    pop: z => z.L <= 4 && z.oppN >= 1 && z.mp, label: z => (z.ram === 1 ? 1 : 0),
    feats: [F('oppL-L', z => Math.max(-4, Math.min(z.oppL - z.L, 8))), F('oppD', z => z.oppD), F('L', z => z.L), F('U', z => Math.min(z.U, 64)),
      F('aN', z => Math.min(z.aN, 6)), F('eN', z => Math.min(z.eN, 6)), F('eAft', z => z.eAft), F('free', z => z.free)] },
  { id: 'b2', title: '작은 조각(L≤4), 적 머리가 보이지만 박을 수 없음: 다가가는가', yes: '다가감', no: '유지·멀어짐', cur: 'net10',
    pop: z => z.L <= 4 && z.eN >= 1 && z.oppN === 0 && z.move && z.alive, label: z => (z.eDelta < 0 ? 1 : 0),
    feats: [F('eD0', z => Math.min(z.eD0, 9)), F('eL-L', z => Math.max(-4, Math.min(z.eL - z.L, 8))), F('L', z => z.L), F('U', z => Math.min(z.U, 64)),
      F('aN', z => Math.min(z.aN, 6)), F('eNr', z => z.eNr), F('pD0', z => Math.min(z.pD0, 9))] },
  { id: 'c1', title: '분열할 수 있는 턴(L≥4): 분열하는가', yes: '분열', no: '이동', cur: 'net10',
    pop: z => z.L >= 4 && z.U < 64 && z.mp, label: z => (z.split ? 1 : 0),
    feats: [F('L', z => Math.min(z.L, 40)), F('U', z => Math.min(z.U, 64)), F('eN', z => Math.min(z.eN, 6)), F('eNr', z => z.eNr), F('room', z => z.room),
      F('tFree', z => z.tFree), F('free', z => z.free), F('aN', z => Math.min(z.aN, 6)), F('pN', z => Math.min(z.pN, 9)), F('king*', z => z.king), F('r', z => z.r)] },
  { id: 'd1', title: '빈 이웃이 있는 턴: 스스로 죽는가', yes: '자해', no: '그 밖', cur: 'fk',
    pop: z => z.free >= 1, label: z => z.sk,
    feats: [F('r', z => z.r), F('L', z => Math.min(z.L, 40)), F('U', z => Math.min(z.U, 64)), F('kRank*', z => Math.min(z.kRank, 64)), F('aDg*', z => Math.min(z.aDg, 30)),
      F('aLg*', z => Math.min(z.aLg, 40)), F('kD*', z => Math.min(z.kD, 40)), F('eN', z => Math.min(z.eN, 6)), F('aN', z => Math.min(z.aN, 6)), F('TL*', z => Math.min(z.TL, 60))] },
  { id: 'e1', title: '3걸음 안에 진주: 진주 쪽으로 가는가', yes: '진주 쪽', no: '다른 쪽', cur: 'net10',
    pop: z => z.move && z.pD0 <= 3, label: z => (z.pD1 < z.pD0 ? 1 : 0),
    feats: [F('pD0', z => z.pD0), F('pDang', z => z.pDang), F('pEd-pD0', z => Math.max(-3, Math.min(z.pEd - z.pD0, 9))), F('L', z => Math.min(z.L, 40)), F('eNrs', z => z.eNrs),
      F('exp1', z => z.exp1), F('eN', z => Math.min(z.eN, 6)), F('U', z => Math.min(z.U, 64)), F('pN3', z => Math.min(z.pN3, 6))] },
  { id: 'f1', title: '왕, r≥300: 가장 가까운 아군 쪽으로 가는가', yes: '아군 쪽', no: '그 밖', cur: 'net10',
    pop: z => z.king === 1 && z.r >= 300 && z.move && z.alive && z.aDg < 99, label: z => (z.aDg1 < z.aDg ? 1 : 0),
    feats: [F('aDg*', z => Math.min(z.aDg, 30)), F('aLg*', z => Math.min(z.aLg, 40)), F('L', z => Math.min(z.L, 60)), F('eN', z => Math.min(z.eN, 6)),
      F('U', z => Math.min(z.U, 64)), F('pD0', z => Math.min(z.pD0, 9))] },
  { id: 'g1', title: '머리 칸에 포털 변: 포털을 지나는가', yes: '포털 통과', no: '통과 안 함', cur: 'net10',
    pop: z => z.move && z.ptlN >= 1, label: z => (z.ptlK >= 1 ? 1 : 0),
    feats: [F('ptlN', z => z.ptlN), F('L', z => Math.min(z.L, 40)), F('eN', z => Math.min(z.eN, 6)), F('eNrs', z => z.eNrs), F('pN', z => Math.min(z.pN, 9)),
      F('pD0', z => Math.min(z.pD0, 9)), F('free', z => z.free), F('room', z => z.room), F('U', z => Math.min(z.U, 64))] },
  { id: 'p5', title: '시야에 진주 없음, 5라운드 안에 생길 칸이 보임: 그 칸 쪽으로 가는가', yes: '생길 칸 쪽', no: '그 밖', cur: 'net10',
    pop: z => z.move && z.alive && z.pN === 0 && z.spD <= 8, label: z => (z.spD1 < z.spD ? 1 : 0),
    feats: [F('spD', z => z.spD), F('sp5', z => Math.min(z.sp5, 6)), F('L', z => Math.min(z.L, 40)), F('eN', z => Math.min(z.eN, 6)), F('U', z => Math.min(z.U, 64)), F('room', z => z.room)] },
  { id: 't1', title: '막다른 곳(모든 첫걸음의 방 < 길이 + 2), 길이 ≥4: 분열하는가', yes: '분열', no: '그 밖', cur: 'net10',
    pop: z => z.free >= 1 && z.roomMax < z.L + 2 && z.L >= 4 && z.mp, label: z => (z.split ? 1 : 0),
    feats: [F('L', z => Math.min(z.L, 40)), F('roomMax', z => z.roomMax), F('room', z => z.room), F('tFree', z => z.tFree), F('eN', z => Math.min(z.eN, 6)),
      F('U', z => Math.min(z.U, 64)), F('free', z => z.free), F('pN', z => Math.min(z.pN, 9))] },
];
for (const s of SPECS) s.allFeats = s.feats.concat(SEG_FEATS);

// ---------------------------------------------------------------------------------------------------------------
// Worker: one pass over a shard of games.
//  mode 'A' (tree sample): reservoir of [features, label, w, win] per spec.
//  mode 'B' (full): rule cells, team cells, per team-game clusters, tree leaf cells, deaths.
function runShard(wd) {
  const { COLS, games, groups, mode, trees, cap, seed } = wd;
  const V_ = makeView(COLS), z = V_.z;
  const G = groups.length, gi = Object.fromEntries(groups.map((g, i) => [g, i]));
  let rng = seed >>> 0 || 1; const rand = () => { rng = (Math.imul(rng, 1103515245) + 12345) >>> 0; return rng / 4294967296; };
  const out = { rows: 0, games: 0 };
  // ---- mode A
  if (mode === 'A') {
    const res = SPECS.map(() => ({ rows: [], seen: 0 }));
    for (const g of games) {
      const buf = zlib.gunzipSync(fs.readFileSync(g.file));
      z.elim = g.elim; z.initN = g.initDragons || 0;
      out.rows += forEachRow(buf, COLS, f => {
        V_.fill(f);
        const win = g.winner === 'A' || g.winner === 'B' ? (((z.tm === TM_A) ? 'A' : 'B') === g.winner ? 1 : 0) : -1;
        for (let s = 0; s < SPECS.length; s++) {
          const sp = SPECS[s];
          if (!sp.pop(z)) continue;
          const R = res[s]; R.seen++;
          const rec = [sp.allFeats.map(q => q[1](z)), sp.label(z), z.w, win];
          if (R.rows.length < cap) R.rows.push(rec); else { const j = Math.floor(rand() * R.seen); if (j < cap) R.rows[j] = rec; }
        }
      });
      out.games++;
    }
    out.samples = res;
    return out;
  }
  // ---- mode B
  const NR = RULES.length;
  const cells = RULES.map(() => new Float64Array(G * NCELL * STRIDE));
  const teamCells = {};   // `${grp}|${team}` -> Float64Array(NR*4): w, n, a, d
  const clusters = [];    // per team-game: {grp, map, win, team, v: [d, a] x NR}
  const deaths = {};      // `${grp}|${map}|${lc}|${cause}` -> [count, lenSum]
  const trNodes = trees.map(t => t.nodes);
  const leafCells = trees.map(t => new Float64Array(t.nLeaves * G * MAPS.length * STRIDE));
  const leafTeam = trees.map(() => ({})); // team -> Float64Array(nLeaves*3): w, a, n (T rows only)
  const outV = new Float64Array(NO);
  const addCell = (arr, base, w, a, d, yes, bin) => {
    arr[base] += w; arr[base + 1]++; arr[base + 2] += w * a; arr[base + 3] += w * d; if (a > 0) arr[base + 4]++;
    if (bin) { const o = base + 5 + (yes ? 0 : NO); for (let k = 0; k < NO; k++) { const v = outV[k]; if (v === v) arr[o + k] += w * v; } }
  };
  for (const g of games) {
    const buf = zlib.gunzipSync(fs.readFileSync(g.file));
    const mi = MAPS.indexOf(g.mapSeg);
    z.elim = g.elim; z.initN = g.initDragons || 0;
    // groups of each team of this game
    const tg = {};
    for (const tm of ['A', 'B']) {
      const list = [];
      if (g.top) {
        list.push('T');
        if (g.winner === tm) list.push('TW'); else if (g.winner === 'A' || g.winner === 'B') list.push('TL');
      } else list.push(tm === g.ourSide ? 'O' + g.ourSubmission : 'X');
      tg[tm] = list.filter(x => x in gi).map(x => gi[x]);
    }
    const cl = { A: new Float64Array(NR * 2), B: new Float64Array(NR * 2) };
    const tcA = {}, tcB = {};
    for (const tm of ['A', 'B']) {
      const team = g.teamName[tm] || '?';
      for (const gg of tg[tm]) { const k = groups[gg] + '|' + team; if (!teamCells[k]) teamCells[k] = new Float64Array(NR * 4); (tm === 'A' ? tcA : tcB)[gg] = teamCells[k]; }
    }
    const lt = trees.map((t, s) => { const o = {}; if (!g.top) return o; for (const tm of ['A', 'B']) { const team = g.teamName[tm] || '?'; o[tm] = leafTeam[s][team] || (leafTeam[s][team] = new Float64Array(t.nLeaves * 3)); } return o; });
    out.rows += forEachRow(buf, COLS, f => {
      V_.fill(f);
      const tm = z.tm === TM_A ? 'A' : 'B', grs = tg[tm], w = z.w;
      if (!grs.length) return;
      const cell = (mi * PHASES.length + z.ph) * LENS.length + z.lc;
      outV[0] = z.net10; outV[1] = z.net30; outV[2] = z.al10; outV[3] = z.eat10; outV[4] = z.kc10; outV[5] = z.fk;
      const clv = cl[tm], tcs = tm === 'A' ? tcA : tcB;
      for (let ri = 0; ri < NR; ri++) {
        const R = RULES[ri];
        if (!R.pop(z)) continue;
        const a = R.act(z), d = R.den ? R.den(z) : 1;
        if (!(a === a) || !(d === d)) continue;
        const bin = R.kind === 'bin';
        const arr = cells[ri];
        for (const gg of grs) {
          addCell(arr, (gg * NCELL + cell) * STRIDE, w, a, d, a > 0, bin);
          const t = tcs[gg]; if (t) { const o = ri * 4; t[o] += w; t[o + 1]++; t[o + 2] += w * a; t[o + 3] += w * d; }
        }
        clv[ri * 2] += w * d; clv[ri * 2 + 1] += w * a;
      }
      // tree leaves
      for (let s = 0; s < SPECS.length; s++) {
        const sp = SPECS[s];
        if (!trNodes[s] || !sp.pop(z)) continue;
        let n = trNodes[s][0];
        while (n.f >= 0) n = trNodes[s][sp.allFeats[n.f][1](z) <= n.t ? n.l : n.r];
        const y = sp.label(z), li = n.leaf, arr = leafCells[s];
        for (const gg of grs) addCell(arr, ((li * G + gg) * MAPS.length + mi) * STRIDE, w, y, 1, y > 0, true);
        const tt = lt[s][tm]; if (tt) { tt[li * 3] += w; tt[li * 3 + 1] += w * y; tt[li * 3 + 2]++; }
      }
      // deaths: own-action deaths on this row; a head-on also kills the dragon hit (victim team from hitT)
      if (z.fate !== 0 && z.w === 1) {
        let cause = 'other';
        for (const [k, v] of Object.entries(DEATH_CODES)) if (v === z.fate) cause = k;
        if (cause === 'S' || cause === 'W' || cause === 'Aq' || cause === 'Ax') cause = z.free >= 1 ? 'sk-' + cause : 'trap-' + cause;
        for (const gg of grs) { const k = groups[gg] + '|' + mi + '|' + z.lc + '|' + cause; const e = deaths[k] || (deaths[k] = [0, 0]); e[0]++; e[1] += z.L; }
        if (cause === 'H' && z.hitL > 0) {
          const vt = z.hitT === HT_A ? tm : (tm === 'A' ? 'B' : 'A');
          const vl = z.hitL, vlc = vl <= 2 ? 0 : vl <= 4 ? 1 : vl <= 7 ? 2 : vl <= 11 ? 3 : vl <= 19 ? 4 : 5;
          for (const gg of tg[vt]) { const k = groups[gg] + '|' + mi + '|' + vlc + '|' + (z.hitT === HT_A ? 'V-ally' : 'V'); const e = deaths[k] || (deaths[k] = [0, 0]); e[0]++; e[1] += vl; }
        }
      }
    });
    for (const tm of ['A', 'B']) for (const gg of tg[tm]) clusters.push({ grp: groups[gg], map: mi, win: g.winner === tm ? 1 : (g.winner === 'A' || g.winner === 'B') ? 0 : -1, team: g.teamName[tm] || '?', v: cl[tm] });
    out.games++;
  }
  Object.assign(out, { cells, teamCells, clusters, deaths, leafCells, leafTeam });
  return out;
}
if (!isMainThread) {
  const res = runShard(workerData);
  parentPort.postMessage(res);
}

// ---------------------------------------------------------------------------------------------------------------
// Main
if (isMainThread && require.main === module) main().catch(e => { console.error(e); process.exit(1); });
module.exports = { RULES, SPECS, MAPS, PHASES, LENS, OUTS, STRIDE, NCELL, SUB_NAMES };

function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  const out = []; for (const l of fs.readFileSync(file, 'utf8').split('\n')) { if (!l.trim()) continue; try { out.push(JSON.parse(l)); } catch { /* partial */ } }
  return out;
}
function runWorkers(shards, common) {
  return Promise.all(shards.map((games, i) => new Promise((resolve, reject) => {
    const w = new Worker(__filename, { workerData: { ...common, games, seed: 7919 * (i + 1) }, resourceLimits: { maxOldGenerationSizeMb: 4096 } });
    w.on('message', resolve); w.on('error', reject);
    w.on('exit', c => { if (c) reject(Error('worker exit ' + c)); });
  })));
}
// shards of similar row counts: sort games by rows (desc) and deal them to the lightest shard
function shardsOf(games, k) {
  const s = Array.from({ length: k }, () => ({ load: 0, games: [] }));
  for (const g of games.slice().sort((a, b) => b.rows - a.rows)) { let m = s[0]; for (const x of s) if (x.load < m.load) m = x; m.games.push(g); m.load += g.rows; }
  return s.map(x => x.games).filter(x => x.length);
}

// weighted CART (same algorithm as tools/decisions_lib.js fitTree), returned as a flat node list for the workers
function fitTreeFlat(X, y, w, names, opts) {
  const Lb = require('../../tools/decisions_lib.js');
  const tree = Lb.fitTree(X, y, w, 2, names, opts);
  const nodes = []; let nLeaves = 0; const leafInfo = [];
  (function walk(n, conds) {
    const id = nodes.length; nodes.push(null);
    if (!n.split) { nodes[id] = { f: -1, leaf: nLeaves }; leafInfo.push({ conds, n: n.n, w: n.w, p: n.cnt[1] / Math.max(n.w, 1e-9) }); nLeaves++; return id; }
    const node = { f: n.split.f, t: n.split.t, l: -1, r: -1, leaf: -1 };
    nodes[id] = node;
    node.l = walk(n.left, conds.concat([{ name: n.split.name, op: '<=', v: n.split.lo }]));
    node.r = walk(n.right, conds.concat([{ name: n.split.name, op: '>=', v: n.split.hi }]));
    return id;
  })(tree.root, []);
  for (const l of leafInfo) {
    const r = new Map();
    for (const c of l.conds) { const e = r.get(c.name) || { lo: -Infinity, hi: Infinity }; if (c.op === '<=') e.hi = Math.min(e.hi, c.v); else e.lo = Math.max(e.lo, c.v); r.set(c.name, e); }
    l.text = [...r.entries()].map(([k, e]) => e.lo === -Infinity ? `${k}≤${e.hi}` : e.hi === Infinity ? `${k}≥${e.lo}` : e.lo === e.hi ? `${k}=${e.lo}` : `${k} ${e.lo}–${e.hi}`).join(', ') || '(전체)';
    delete l.conds;
  }
  return { nodes, nLeaves, leaves: leafInfo };
}

async function main() {
  const argv = process.argv.slice(2);
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const t0 = Date.now();
  const TOPSET = opt('top', fs.existsSync(path.join(DEC, 'top-all', 'games.jsonl')) ? 'top-all' : 'top-20260929a');
  const JOBS = Math.max(1, Math.min(4, +opt('jobs', 4)));
  const OUT = path.resolve(ROOT, opt('out', path.join('data', 'decisions', 'scale')));
  const TREE_MOD = +opt('tree-mod', 8), TREE_CAP = +opt('tree-cap', 300000), BOOT = +opt('boot', 400);
  const COLS = require('../../tools/decisions.js').COLS;
  const allSets = fs.readdirSync(DEC).filter(s => fs.existsSync(path.join(DEC, s, 'games.jsonl')));
  const SETS = opt('sets', null) ? opt('sets').split(',') : allSets.filter(s => s !== TOPSET && !s.startsWith('top-') && readJsonl(path.join(DEC, s, 'games.jsonl')).some(g => g.ourSide));

  // ---- game lists
  let topRaw = readJsonl(path.join(DEC, TOPSET, 'games.jsonl')).filter(g => mapSegOf(g) !== 'other');   // layout study: Schooltime and Devil only
  // --index-rows N: only games among the first N rows of data/top/index.jsonl (reproduces a dated corpus of top-all)
  const INDEX_ROWS = +opt('index-rows', 0);
  if (INDEX_ROWS > 0) {
    const keep = new Set(readJsonl(path.join(ROOT, 'data', 'top', 'index.jsonl')).slice(0, INDEX_ROWS).map(r => r.battleId + ':' + r.gameId));
    topRaw = topRaw.filter(g => keep.has(g.key));
  }
  const manifest = fs.existsSync(path.join(DEC, TOPSET, 'manifest.json')) ? JSON.parse(fs.readFileSync(path.join(DEC, TOPSET, 'manifest.json'), 'utf8')) : null;
  // inactive team-games (a broken bot): no pings and <= 3 splits over >= 100 rounds by a team that pings in most of its
  // games, or no valid action on >= 20% of its turns
  const pingGames = {};
  for (const g of topRaw) if (g.tc) for (const tm of ['A', 'B']) { const t = g.teamName[tm]; const e = pingGames[t] || (pingGames[t] = [0, 0]); e[0]++; if (g.tc[tm].pings > 0) e[1]++; }
  // the silent pattern counts only for a team that shows it in >= 5 games (a systematically broken submission such as SSS);
  // isolated cases are early losses of working bots (e.g. Queen Of Spades, before a late-pinging team starts)
  const silent = (g, tm) => { const t = g.tc[tm], pg = pingGames[g.teamName[tm]]; return g.rounds >= 100 && t.pings === 0 && t.splits <= 3 && pg && pg[1] / pg[0] >= 0.5; };
  const silentN = {}; for (const g of topRaw) if (g.tc) for (const tm of ['A', 'B']) if (silent(g, tm)) silentN[g.teamName[tm]] = (silentN[g.teamName[tm]] || 0) + 1;
  const inactive = (g, tm) => {
    if (!g.tc) return g.teamName[tm] === 'SSS';
    const t = g.tc[tm];
    if (t.turns > 0 && t.none / t.turns >= 0.2) return true;
    return silent(g, tm) && (silentN[g.teamName[tm]] || 0) >= 5;
  };
  const excluded = [], topGames = [];
  for (const g of topRaw) {
    const bad = ['A', 'B'].filter(tm => inactive(g, tm));
    if (bad.length) { excluded.push({ key: g.key, teams: bad.map(tm => g.teamName[tm]), map: g.map }); continue; }
    topGames.push(g);
  }
  const prep = (set, g, top) => ({ file: path.join(DEC, set, g.out), key: g.key, map: g.map, mapSeg: mapSegOf(g), elim: ELIM_MAPS.has(mapSegOf(g)) ? 1 : 0, initDragons: g.initDragons || 0,
    winner: g.winner, teamName: g.teamName, top, ourSide: g.ourSide || null, ourSubmission: g.ourSubmission || null, rows: g.rows || 1 });
  const LIMIT = +opt('limit', 0); // testing: first N usable top games only
  const TG = (LIMIT > 0 ? topGames.slice(0, LIMIT) : topGames).map(g => prep(TOPSET, g, true));
  const OG = [];
  const onlineMeta = [];
  const ALIAS = opt('alias', null) === null ? SUB_ALIAS_DEFAULT : opt('alias') === 'none' ? {} : Object.fromEntries(opt('alias').split(',').map(x => x.split('=')));
  for (const s of SETS) for (const g0 of readJsonl(path.join(DEC, s, 'games.jsonl'))) {
    if (!g0.ourSide || mapSegOf(g0) === 'other') continue;
    const g = ALIAS[g0.ourSubmission] ? { ...g0, ourSubmission: +ALIAS[g0.ourSubmission], ourSubmissionRaw: g0.ourSubmission } : g0;
    OG.push(prep(s, g, false)); onlineMeta.push({ set: s, g });
  }
  const subs = [...new Set(OG.map(g => String(g.ourSubmission)))].sort();
  const groups = ['T', 'TW', 'TL', ...subs.map(s => 'O' + s), 'X'];
  const setsOfSub = {}; for (const { set, g } of onlineMeta) (setsOfSub[g.ourSubmission] || (setsOfSub[g.ourSubmission] = new Set())).add(set);
  console.error(`top ${TOPSET}: ${topRaw.length} games, excluded ${excluded.length} (inactive team), used ${TG.length}; online ${SETS.length} sets, ${OG.length} games; groups ${groups.join(' ')}`);

  // ---- team-game counts per group x map (denominators of per-game rates) and game-level tables
  const tgCount = {}; const addTG = (gr, mi) => { const k = gr + '|' + mi; tgCount[k] = (tgCount[k] || 0) + 1; tgCount[gr + '|all'] = (tgCount[gr + '|all'] || 0) + 1; };
  const allMeta = [...topGames.map(g => ({ g, top: true })), ...onlineMeta.map(x => ({ g: x.g, top: false }))];
  const results = {}; // grp|map -> {n, won, gone, goneR, longest, units, G}
  const growth = {};  // grp|elim|r -> sums of units, total, longest (all team-games; gone = 0)
  const TLR = [10, 20, 30, 50, 75, 100, 150, 200, 250, 300, 350, 400, 450, 500];
  const teamStats = {}; // top team -> {games, wins, pings, turns, splits, pA, pE}
  for (const { g, top } of allMeta) {
    const ms = mapSegOf(g), mi = MAPS.indexOf(ms), el = ELIM_MAPS.has(ms) ? 'E' : 'R';
    for (const tm of ['A', 'B']) {
      const grs = top ? ['T', ...(g.winner === tm ? ['TW'] : (g.winner === 'A' || g.winner === 'B') ? ['TL'] : [])] : [tm === g.ourSide ? 'O' + g.ourSubmission : 'X'];
      const fin = g.final[tm], won = g.winner === tm ? 1 : 0, gone = fin[0] === 0 ? 1 : 0;
      for (const gr of grs) {
        addTG(gr, mi);
        for (const mk of [ms, el, 'all']) {
          const k = gr + '|' + mk; const e = results[k] || (results[k] = { n: 0, won: 0, gone: 0, goneR: 0, longest: 0, units: 0, total: 0 });
          e.n++; e.won += won; e.gone += gone; if (gone) e.goneR += g.rounds; e.longest += fin[1]; e.units += fin[0]; e.total += fin[2];
        }
        if (g.tl) for (const r of TLR) {
          const i = r / 10; if (!Number.isInteger(i)) continue;
          const s = g.tl[tm], u = s[i * 3], tot = s[i * 3 + 1], lg = s[i * 3 + 2];
          for (const mk of [el, ms]) { const k = gr + '|' + mk + '|' + r; const e = growth[k] || (growth[k] = { n: 0, u: 0, tot: 0, lg: 0, alive: 0 }); e.n++; e.u += u; e.tot += tot; e.lg += lg; e.alive += u > 0 ? 1 : 0; }
        }
        if (g.tl && TLR.includes(75)) { /* r75 is not on the 10-round grid: interpolate 70/80 */
          const s = g.tl[tm]; for (const mk of [el, ms]) { const k = gr + '|' + mk + '|75'; const e = growth[k] || (growth[k] = { n: 0, u: 0, tot: 0, lg: 0, alive: 0 });
            e.n++; e.u += (s[21] + s[24]) / 2; e.tot += (s[22] + s[25]) / 2; e.lg += (s[23] + s[26]) / 2; e.alive += (s[21] + s[24]) > 0 ? 1 : 0; }
        }
      }
      if (top && g.tc) {
        const t = g.teamName[tm], e = teamStats[t] || (teamStats[t] = { games: 0, wins: 0, pings: 0, turns: 0, splits: 0, pA: 0, pE: 0, maps: {} });
        e.games++; e.wins += won; e.pings += g.tc[tm].pings; e.turns += g.tc[tm].turns; e.splits += g.tc[tm].splits; e.pA += g.tc[tm].pA; e.pE += g.tc[tm].pE; e.maps[ms] = (e.maps[ms] || 0) + 1;
      }
    }
  }

  // ---- pass A: tree samples from one in TREE_MOD top games
  const sampleGames = TG.filter(g => keyHash(g.key) % TREE_MOD === 0);
  const tA = Date.now();
  const resA = await runWorkers(shardsOf(sampleGames, JOBS), { COLS, groups, mode: 'A', trees: [], cap: Math.ceil(TREE_CAP / JOBS) });
  const trees = [];
  for (let s = 0; s < SPECS.length; s++) {
    const rows = [], names = SPECS[s].allFeats.map(q => q[0]);
    let seen = 0;
    for (const r of resA) { const x = r.samples[s]; seen += x.seen; const scale = x.seen / Math.max(1, x.rows.length); for (const q of x.rows) rows.push([q[0], q[1], q[2] * scale, q[3]]); }
    if (rows.length < 2000) { trees.push({ id: SPECS[s].id, nodes: null, nLeaves: 0, leaves: [], sample: rows.length, seen }); continue; }
    const minN = Math.max(300, Math.floor(rows.length / 250));
    const T = fitTreeFlat(rows.map(r => r[0]), rows.map(r => r[1]), rows.map(r => r[2]), names, { maxDepth: 5, minLeafN: minN, minLeafW: minN, minGain: 0.003 });
    trees.push({ id: SPECS[s].id, ...T, sample: rows.length, seen, minLeafN: minN, names });
  }
  console.error(`pass A: ${sampleGames.length} games, ${resA.reduce((a, r) => a + r.rows, 0)} rows, ${((Date.now() - tA) / 1000).toFixed(0)}s; tree leaves ${trees.map(t => t.id + ':' + t.nLeaves).join(' ')}`);

  // ---- pass B: everything
  const tB = Date.now();
  const resB = await runWorkers(shardsOf([...TG, ...OG], JOBS), { COLS, groups, mode: 'B', trees: trees.map(t => ({ nodes: t.nodes, nLeaves: t.nLeaves })), cap: 0 });
  const NR = RULES.length, G = groups.length;
  const cells = RULES.map(() => new Float64Array(G * NCELL * STRIDE));
  const teamCells = {}, deaths = {}, clusters = [];
  const leafCells = trees.map(t => new Float64Array(t.nLeaves * G * MAPS.length * STRIDE));
  const leafTeam = trees.map(() => ({}));
  let rowsB = 0;
  for (const r of resB) {
    rowsB += r.rows;
    for (let i = 0; i < NR; i++) { const a = cells[i], b = r.cells[i]; for (let j = 0; j < a.length; j++) a[j] += b[j]; }
    for (const [k, v] of Object.entries(r.teamCells)) { const a = teamCells[k] || (teamCells[k] = new Float64Array(v.length)); for (let j = 0; j < v.length; j++) a[j] += v[j]; }
    for (const [k, v] of Object.entries(r.deaths)) { const a = deaths[k] || (deaths[k] = [0, 0]); a[0] += v[0]; a[1] += v[1]; }
    for (const c of r.clusters) clusters.push(c);
    for (let s = 0; s < trees.length; s++) {
      const a = leafCells[s], b = r.leafCells[s]; for (let j = 0; j < a.length; j++) a[j] += b[j];
      for (const [k, v] of Object.entries(r.leafTeam[s])) { const x = leafTeam[s][k] || (leafTeam[s][k] = new Float64Array(v.length)); for (let j = 0; j < v.length; j++) x[j] += v[j]; }
    }
  }
  console.error(`pass B: ${TG.length + OG.length} games, ${rowsB} rows, ${((Date.now() - tB) / 1000).toFixed(0)}s`);

  // ---------------------------------------------------------------------------------------------------------------
  // Summaries
  const gIdx = Object.fromEntries(groups.map((g, i) => [g, i]));
  // sum a rule's cells over a selection: sel(mi, ph, lc) -> bool
  function sumCells(ri, gr, sel) {
    const a = cells[ri], gg = gIdx[gr], s = new Float64Array(STRIDE);
    if (gg === undefined) return s;
    for (let mi = 0; mi < MAPS.length; mi++) for (let ph = 0; ph < PHASES.length; ph++) for (let lc = 0; lc < LENS.length; lc++) {
      if (sel && !sel(mi, ph, lc)) continue;
      const base = (gg * NCELL + (mi * PHASES.length + ph) * LENS.length + lc) * STRIDE;
      for (let j = 0; j < STRIDE; j++) s[j] += a[base + j];
    }
    return s;
  }
  const stat = (s, R, tgN) => {
    const o = { w: s[0], n: s[1], p: s[3] > 0 ? s[2] / s[3] : null, n1: s[4], perGame: tgN ? s[0] / tgN : null };
    if (R.kind === 'bin') {
      const w1 = s[2], w0 = s[0] - s[2];
      o.out1 = {}; o.out0 = {};
      OUTS.forEach((k, j) => { o.out1[k] = w1 > 0 ? s[5 + j] / w1 : null; o.out0[k] = w0 > 0 ? s[5 + NO + j] / w0 : null; });
      o.n0 = s[1] - s[4];
    }
    return o;
  };
  const tgOf = (gr, mi) => tgCount[gr + '|' + (mi === undefined ? 'all' : mi)] || 0;
  const tgSel = (gr, pred) => { let n = 0; for (let mi = 0; mi < MAPS.length; mi++) if (pred(mi)) n += tgOf(gr, mi); return n; };
  const ruleOut = {};
  for (let ri = 0; ri < NR; ri++) {
    const R = RULES[ri], o = { id: R.id, fam: R.fam, name: R.name, kind: R.kind, cur: R.cur || null, all: {}, map: {}, type: {}, phase: {}, len: {}, mapPhase: {} };
    for (const gr of groups) {
      o.all[gr] = stat(sumCells(ri, gr), R, tgOf(gr));
      o.map[gr] = MAPS.map((m, mi) => stat(sumCells(ri, gr, x => x === mi), R, tgOf(gr, mi)));
      o.type[gr] = ['E', 'R'].map(t => stat(sumCells(ri, gr, x => ELIM_MAPS.has(MAPS[x]) === (t === 'E')), R, tgSel(gr, x => ELIM_MAPS.has(MAPS[x]) === (t === 'E'))));
      o.phase[gr] = PHASES.map((p, ph) => stat(sumCells(ri, gr, (x, y) => y === ph), R, tgOf(gr)));
      o.len[gr] = LENS.map((l, lc) => stat(sumCells(ri, gr, (x, y, zz) => zz === lc), R, tgOf(gr)));
      o.mapPhase[gr] = ['E', 'R'].map(t => PHASES.map((p, ph) => stat(sumCells(ri, gr, (x, y) => y === ph && ELIM_MAPS.has(MAPS[x]) === (t === 'E')), R, tgSel(gr, x => ELIM_MAPS.has(MAPS[x]) === (t === 'E')))));
    }
    // teams (top): rate per team with >= 30 rows
    o.teams = {};
    for (const [k, v] of Object.entries(teamCells)) {
      const [gr, team] = [k.slice(0, k.indexOf('|')), k.slice(k.indexOf('|') + 1)];
      if (gr !== 'T' && gr !== 'X') continue;
      const j = ri * 4; if (v[j + 1] < 30) continue;
      (o.teams[gr] || (o.teams[gr] = {}))[team] = { p: v[j + 3] > 0 ? v[j + 2] / v[j + 3] : null, n: v[j + 1], w: v[j] };
    }
    ruleOut[R.id] = o;
  }
  // stratified impact: our group moved to the top winners' rate in each map x phase x length cell, times the outcome
  // difference (doing it - not) of the top rows. Thin cells fall back to the map x phase, the phase, then all cells:
  // the winners' rate needs >= 30 rows, the outcome difference >= 20 rows on both sides.
  //   impact per team-game = sum over cells (w_ours * pW - a_ours) * dT / team-games
  const PH = PHASES.length, LC = LENS.length, NM = MAPS.length;
  const cellOf = (gg, mi, ph, lc) => (gg * NCELL + (mi * PH + ph) * LC + lc) * STRIDE;
  const CURS = ['net10', 'net30', 'al10', 'eat10', 'kc10', 'fk'];
  const impacts = {};
  const OURS_G = groups.filter(g => g.startsWith('O'));
  for (let ri = 0; ri < NR; ri++) {
    const R = RULES[ri]; if (R.kind !== 'bin') continue;
    const A = cells[ri];
    const agg = gg => { // map x phase, phase and all aggregates of one group
      const mp = new Float64Array(NM * PH * STRIDE), p = new Float64Array(PH * STRIDE), all = new Float64Array(STRIDE);
      for (let mi = 0; mi < NM; mi++) for (let ph = 0; ph < PH; ph++) for (let lc = 0; lc < LC; lc++) {
        const b = cellOf(gg, mi, ph, lc);
        for (let j = 0; j < STRIDE; j++) { const v = A[b + j]; mp[(mi * PH + ph) * STRIDE + j] += v; p[ph * STRIDE + j] += v; all[j] += v; }
      }
      return { mp, p, all };
    };
    const aT = agg(gIdx.T), aW = agg(gIdx.TW);
    const dOf = (arr, off, j) => { const n1 = arr[off + 4], n0 = arr[off + 1] - arr[off + 4], w1 = arr[off + 2], w0 = arr[off] - arr[off + 2]; return (n1 >= 20 && n0 >= 20 && w1 > 0 && w0 > 0) ? arr[off + 5 + j] / w1 - arr[off + 5 + NO + j] / w0 : null; };
    const pOf = (arr, off) => arr[off + 1] >= 30 && arr[off] > 0 ? arr[off + 2] / arr[off] : null;
    impacts[R.id] = {};
    for (const gr of OURS_G) {
      const gg = gIdx[gr], tgN = tgOf(gr), res = {};
      for (const cur of CURS) {
        const j = OUTS.indexOf(cur);
        let imp = 0, turns = 0, gapW = 0, cov = 0; const byType = { E: 0, R: 0 }, byPhase = new Array(PH).fill(0), byMap = new Array(NM).fill(0);
        for (let mi = 0; mi < NM; mi++) for (let ph = 0; ph < PH; ph++) for (let lc = 0; lc < LC; lc++) {
          const bo = cellOf(gg, mi, ph, lc); const wO = A[bo]; if (!(wO > 0)) continue;
          turns += wO;
          let pW = pOf(A, cellOf(gIdx.TW, mi, ph, lc));
          if (pW === null) pW = pOf(aW.mp, (mi * PH + ph) * STRIDE);
          if (pW === null) pW = pOf(aW.p, ph * STRIDE);
          if (pW === null) pW = pOf(aW.all, 0);
          let dT = dOf(A, cellOf(gIdx.T, mi, ph, lc), j);
          if (dT === null) dT = dOf(aT.mp, (mi * PH + ph) * STRIDE, j);
          if (dT === null) dT = dOf(aT.p, ph * STRIDE, j);
          if (dT === null) dT = dOf(aT.all, 0, j);
          if (pW === null || dT === null) continue;
          cov += wO;
          const moved = wO * pW - A[bo + 2], x = moved * dT / tgN;
          imp += x; gapW += moved;
          byType[ELIM_MAPS.has(MAPS[mi]) ? 'E' : 'R'] += x; byPhase[ph] += x; byMap[mi] += x;
        }
        res[cur] = { impact: imp, turns: turns / tgN, gap: turns ? gapW / turns : null, coverage: turns ? cov / turns : null, byType, byPhase, byMap };
      }
      impacts[R.id][gr] = res;
    }
  }
  // game-clustered bootstrap: rate per group (T, TW, TL, O*, X) and the gap TW - O*
  let seed = 12345; const rnd = () => { seed = (Math.imul(seed, 1103515245) + 12345) >>> 0; return seed / 4294967296; };
  const byGrp = {}; for (const c of clusters) (byGrp[c.grp] || (byGrp[c.grp] = [])).push(c);
  const boot = {};
  for (let ri = 0; ri < NR; ri++) {
    const R = RULES[ri]; boot[R.id] = {};
    const draws = {};
    for (const gr of groups) {
      const L = byGrp[gr] || []; if (!L.length) continue;
      const d = new Float64Array(L.length), a = new Float64Array(L.length);
      L.forEach((c, i) => { d[i] = c.v[ri * 2]; a[i] = c.v[ri * 2 + 1]; });
      const ps = [];
      for (let b = 0; b < BOOT; b++) { let sd = 0, sa = 0; for (let i = 0; i < L.length; i++) { const j = (rnd() * L.length) | 0; sd += d[j]; sa += a[j]; } ps.push(sd > 0 ? sa / sd : NaN); }
      draws[gr] = ps;
      const q = ps.filter(Number.isFinite).sort((x, y) => x - y);
      boot[R.id][gr] = q.length ? [q[Math.floor(0.025 * q.length)], q[Math.floor(0.975 * q.length)]] : null;
    }
    for (const gr of groups.filter(g => g.startsWith('O'))) {
      if (!draws.TW || !draws[gr]) continue;
      const q = draws.TW.map((x, i) => x - draws[gr][i]).filter(Number.isFinite).sort((x, y) => x - y);
      boot[R.id]['TW-' + gr] = q.length ? [q[Math.floor(0.025 * q.length)], q[Math.floor(0.975 * q.length)]] : null;
    }
    if (draws.TW && draws.TL) { const q = draws.TW.map((x, i) => x - draws.TL[i]).filter(Number.isFinite).sort((x, y) => x - y); boot[R.id]['TW-TL'] = q.length ? [q[Math.floor(0.025 * q.length)], q[Math.floor(0.975 * q.length)]] : null; }
  }
  // tree leaves: per group totals and per map, winners vs losers, our groups, teams
  const treeOut = trees.map((t, s) => {
    if (!t.nodes) return { id: t.id, leaves: [], sample: t.sample };
    const sp = SPECS[s];
    const leaves = t.leaves.map((lf, li) => {
      const g = {};
      for (const gr of groups) {
        const tot = new Float64Array(STRIDE), byMap = [];
        for (let mi = 0; mi < MAPS.length; mi++) {
          const base = ((li * G + gIdx[gr]) * MAPS.length + mi) * STRIDE, x = leafCells[s].subarray(base, base + STRIDE);
          for (let j = 0; j < STRIDE; j++) tot[j] += x[j];
          byMap.push(x[1] >= 1 ? { w: x[0], n: x[1], p: x[3] > 0 ? x[2] / x[3] : null } : null);
        }
        const st = stat(tot, { kind: 'bin' }, tgOf(gr));
        st.byMap = byMap;
        g[gr] = st;
      }
      const teams = {};
      for (const [team, v] of Object.entries(leafTeam[s])) if (v[li * 3 + 2] >= 30) teams[team] = { p: v[li * 3 + 1] / v[li * 3], n: v[li * 3 + 2] };
      return { text: lf.text, g, teams };
    });
    return { id: t.id, title: sp.title, yes: sp.yes, no: sp.no, cur: sp.cur, sample: t.sample, seen: t.seen, minLeafN: t.minLeafN, names: t.names, leaves };
  });

  const J = {
    meta: { created: new Date().toISOString(), command: 'node tools/decisions_scale.js' + (argv.length ? ' ' + argv.join(' ') : ''), top: TOPSET, manifest, indexRows: INDEX_ROWS || null, alias: ALIAS,
      lastTopKey: topRaw.length ? topRaw[topRaw.length - 1].key : null, sets: SETS, subs, subNames: SUB_NAMES, setsOfSub: Object.fromEntries(Object.entries(setsOfSub).map(([k, v]) => [k, [...v]])),
      groups, maps: MAPS, phases: PHASES, lens: LENS, outs: OUTS, elimMaps: [...ELIM_MAPS], topGamesRaw: topRaw.length, topGamesUsed: TG.length, excluded,
      onlineGames: OG.length, rows: rowsB, treeSampleGames: sampleGames.length, tgCount, seconds: (Date.now() - t0) / 1000, jobs: JOBS },
    rules: ruleOut, impacts, boot, trees: treeOut, results, growth, growthRounds: TLR, teamStats, deaths,
  };
  fs.writeFileSync(OUT + '.json', JSON.stringify(J, (k, v) => (typeof v === 'number' && !Number.isFinite(v)) ? null : (v instanceof Float64Array ? Array.from(v) : v)));
  fs.writeFileSync(OUT + '.md', renderMd(J));
  console.error(`wrote ${path.relative(ROOT, OUT)}.json and .md in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}

// ---------------------------------------------------------------------------------------------------------------
// Markdown (Korean): every rule by group, segment and team; tree leaves; game-level tables.
function renderMd(J) {
  const { groups, subNames } = J.meta;
  const gname = g => ({ T: '상위', TW: '상위 승자', TL: '상위 패자', X: '우리 경기의 상위 상대' }[g] || (g.startsWith('O') ? `우리 ${subNames[g.slice(1)] || g.slice(1)}` : g));
  const pc = (p, d = 1) => (p === null || p === undefined || !Number.isFinite(p)) ? '–' : (100 * p).toFixed(d) + '%';
  const fx = (v, d = 2) => (v === null || v === undefined || !Number.isFinite(v)) ? '–' : v.toFixed(d);
  const fint = v => Number.isFinite(v) ? Math.round(v).toLocaleString('en-US') : '–';
  const tbl = (h, rows) => ['| ' + h.join(' | ') + ' |', '|' + h.map((_, i) => i === 0 ? '---' : '---:').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');
  const fmtRate = (st, R) => !st || st.p === null ? '–' : R.kind === 'bin' ? pc(st.p) : fx(st.p, 3);
  const OURS = groups.filter(g => g.startsWith('O'));
  const KEY = ['T', 'TW', 'TL', ...OURS, 'X'];
  const md = [];
  md.push('# 대규모 결정 규칙: 구간별 표 (자동 생성)', '');
  md.push(`- 생성: ${J.meta.created}. 명령: \`${J.meta.command || 'node tools/decisions_scale.js'}\`. 실행 ${fx(J.meta.seconds / 60, 1)}분, 작업자 ${J.meta.jobs}.`);
  const mf = J.meta.manifest;
  md.push(`- 상위끼리: \`${J.meta.top}\` ${J.meta.topGamesRaw}판(${J.meta.indexRows ? `index 첫 ${J.meta.indexRows}행` : mf ? `index ${mf.indexRows}행, ${mf.created} 기준` : 'index'}, 마지막 경기 ${J.meta.lastTopKey}). 봇이 멈춘 팀이 낀 ${J.meta.excluded.length}판을 빼고 ${J.meta.topGamesUsed}판을 쓴다. 나무 표본은 ${J.meta.treeSampleGames}판이다.`);
  md.push(`- 우리 온라인: ${J.meta.sets.map(s => '`' + s + '`').join(', ')} ${J.meta.onlineGames}판. 행 ${fint(J.meta.rows)}개.`);
  md.push(`- 집단(팀·경기 수): ${groups.map(g => `${gname(g)} ${J.meta.tgCount[g + '|all'] || 0}`).join(', ')}.`);
  md.push('- 비율은 표본 가중(평범한 턴 8분의 1)을 되살린 턴 비율이다. "판당"은 팀·경기당 그 상태의 턴 수다. 괄호는 경기 단위 붓스트랩 95% 구간이다.', '');
  md.push('## 1. 규칙 요약');
  md.push(tbl(['규칙', ...KEY.map(gname), '승자−패자'], Object.values(J.rules).map(o => {
    const R = o; return [`${o.id} ${o.name}`, ...KEY.map(g => { const s = o.all[g]; const b = J.boot[o.id] && J.boot[o.id][g]; return s && s.p !== null ? `${fmtRate(s, R)}${b && (g === 'T' || g === 'TW' || g === 'TL' || g.startsWith('O')) ? ` [${R.kind === 'bin' ? pc(b[0]) : fx(b[0], 3)}–${R.kind === 'bin' ? pc(b[1]) : fx(b[1], 3)}]` : ''}` : '–'; }),
      (() => { const a = o.all.TW, b = o.all.TL, c = J.boot[o.id]['TW-TL']; if (!a || !b || a.p === null || b.p === null) return '–'; const d = a.p - b.p; return R.kind === 'bin' ? `${(100 * d).toFixed(1)}%p${c ? ` [${(100 * c[0]).toFixed(1)}, ${(100 * c[1]).toFixed(1)}]` : ''}` : `${fx(d, 3)}`; })()];
  })));
  md.push('');
  md.push('### 1.0 규칙이 지도·국면에 따라 달라지는 폭 (상위끼리)');
  md.push('- 지도·국면별 상위 비율의 최소–최대(행 300개 이상), 승자−패자 차이를 지도 종류별로 적는다.');
  md.push(tbl(['규칙', '상위 전체', '지도 최소', '지도 최대', '국면 최소', '국면 최대', '승자−패자(전멸형)', '승자−패자(500형)'], Object.values(J.rules).map(o => {
    const R = o, ok = s => s && s.n >= 300 && s.p !== null;
    const mp = MAPS.map((m, i) => [m, o.map.T[i]]).filter(([, s]) => ok(s)).sort((a, b) => a[1].p - b[1].p);
    const ph = PHASES.map((p, i) => [p, o.phase.T[i]]).filter(([, s]) => ok(s)).sort((a, b) => a[1].p - b[1].p);
    const f = x => x ? `${fmtRate(x[1], R)} ${x[0]}` : '–';
    const wl = ti => { const a = o.type.TW[ti], b = o.type.TL[ti]; return ok(a) && ok(b) ? (R.kind === 'bin' ? `${(100 * (a.p - b.p)).toFixed(1)}%p` : fx(a.p - b.p, 3)) : '–'; };
    return [`${o.id}`, fmtRate(o.all.T, R), f(mp[0]), f(mp[mp.length - 1]), f(ph[0]), f(ph[ph.length - 1]), wl(0), wl(1)];
  })));
  md.push('');
  md.push('### 1.1 지원(행 수)과 판당 턴');
  md.push(tbl(['규칙', ...KEY.map(g => gname(g) + ' 행 / 판당')], Object.values(J.rules).map(o => [o.id, ...KEY.map(g => { const s = o.all[g]; return s ? `${fint(s.n)} / ${fx(s.perGame, 1)}` : '–'; })])));
  md.push('');
  md.push('### 1.2 결과 대조(상위끼리 행, 행동함 / 안 함)');
  md.push(tbl(['규칙', '단위', 'net10', 'net30', '10R 생존', '10R 먹이', '10R 처치 수', '왕 먹이(fk)'], Object.values(J.rules).filter(o => o.kind === 'bin').map(o => {
    const s = o.all.T; return [o.id, o.cur, ...OUTS.map(k => `${fx(s.out1[k])} / ${fx(s.out0[k])}`)];
  })));
  md.push('');
  md.push('## 2. 규칙별 구간');
  for (const o of Object.values(J.rules)) {
    const R = o;
    md.push(`### ${o.id} ${o.name}`);
    const segRow = (label, arr) => [label, ...['T', 'TW', 'TL', ...OURS.filter(g => g === 'O12142' || g === 'O12186' || g === 'O10365'), 'X'].map(g => { const s = arr[g]; return s && s.n >= 20 ? `${fmtRate(s, R)} (${fint(s.n)})` : '–'; })];
    const hdr = ['구간', ...['T', 'TW', 'TL', ...OURS.filter(g => g === 'O12142' || g === 'O12186' || g === 'O10365'), 'X'].map(gname)];
    const rows = [];
    MAPS.forEach((m, mi) => { const x = {}; for (const g of groups) x[g] = o.map[g][mi]; if (x.T && x.T.n >= 20) rows.push(segRow(m, x)); });
    PHASES.forEach((p, ph) => { const x = {}; for (const g of groups) x[g] = o.phase[g][ph]; if (x.T && x.T.n >= 20) rows.push(segRow(p, x)); });
    LENS.forEach((l, lc) => { const x = {}; for (const g of groups) x[g] = o.len[g][lc]; if (x.T && x.T.n >= 20) rows.push(segRow('L' + l, x)); });
    md.push(tbl(hdr, rows));
    if (o.kind === 'bin') {
      const dRow = (label, s) => s && s.out1 && s.n1 >= 20 && s.n0 >= 20 ? `${label} ${fx(s.out1[o.cur] - s.out0[o.cur])}` : null;
      const ds = [...MAPS.map((m, mi) => dRow(m, o.map.T[mi])), ...PHASES.map((p, ph) => dRow(p, o.phase.T[ph]))].filter(Boolean);
      md.push(`- 상위끼리의 결과 차이(${o.cur}, 행동함 − 안 함): ${ds.join(', ')}.`);
    }
    const tt = o.teams.T ? Object.entries(o.teams.T).filter(([, e]) => e.p !== null).sort((a, b) => a[1].p - b[1].p) : [];
    if (tt.length) md.push(`- 상위 팀별(행 30개 이상 ${tt.length}팀): 최소 ${fmtRate(tt[0][1], R)}(${tt[0][0]}), 중앙 ${fmtRate(tt[tt.length >> 1][1], R)}, 최대 ${fmtRate(tt[tt.length - 1][1], R)}(${tt[tt.length - 1][0]}).`);
    md.push('');
  }
  md.push('## 3. 층화 영향 추정 (우리 집단을 상위 승자 비율로 옮길 때, 팀·경기당)');
  md.push('- 영향 = Σ 칸(지도 × 국면 × 길이) 우리 판당 턴 × (승자 비율 − 우리 비율) × (상위끼리의 행동함 − 안 함 결과 차이). 상관에서 나온 1차 추정이다.');
  for (const gr of OURS) {
    md.push(`### ${gname(gr)}`);
    md.push(tbl(['규칙', '판당 턴', '승자와의 차이', 'net10', 'net30', 'al10', 'eat10', 'kc10', 'fk'], Object.entries(J.impacts).map(([id, x]) => { const e = x[gr]; if (!e) return null; return [id, fx(e.net10.turns, 1), e.net10.gap === null ? '–' : `${(100 * e.net10.gap).toFixed(1)}%p`, ...['net10', 'net30', 'al10', 'eat10', 'kc10', 'fk'].map(k => fx(e[k].impact, 2))]; }).filter(Boolean)));
    md.push('');
  }
  md.push('## 4. 나무 잎 (상위 표본으로 학습, 모든 집단을 같은 잎으로 보냄)');
  for (const t of J.trees) {
    md.push(`### ${t.id}. ${t.title || ''}`);
    if (!t.leaves.length) { md.push('- 표본이 적어 나무를 만들지 않았다.', ''); continue; }
    md.push(`- 표본 ${fint(t.sample)}행(전체 ${fint(t.seen)}행), 깊이 ≤5, 잎 최소 ${t.minLeafN}행. 특징: ${t.names.join(', ')}. elim = 전멸형 지도, ph = 국면 0–4, init = 지도 시작 드래곤 수.`);
    md.push(tbl(['잎', '조건', '상위 n', '상위', '승자', '패자', ...OURS.filter(g => g === 'O12142' || g === 'O12186').map(g => gname(g) + ' (n)'), `${t.cur} 상위 예/아니오`], t.leaves.map((l, i) => {
      const T = l.g.T; return [String(i), l.text, fint(T.n), pc(T.p), pc(l.g.TW.p), pc(l.g.TL.p), ...OURS.filter(g => g === 'O12142' || g === 'O12186').map(g => l.g[g] && l.g[g].n >= 1 ? `${pc(l.g[g].p)} (${fint(l.g[g].n)})` : '–'), `${fx(T.out1 && T.out1[t.cur])} / ${fx(T.out0 && T.out0[t.cur])}`];
    })));
    md.push('');
  }
  md.push('## 5. 경기 단위 표');
  md.push('### 5.1 결과 (팀·경기)');
  md.push(tbl(['집단', '지도', '팀·경기', '승', '전멸', '끝 최장', '끝 총길이', '끝 수'], groups.flatMap(g => [...MAPS, 'E', 'R', 'all'].map(m => { const e = J.results[g + '|' + m]; return e && e.n ? [gname(g), m, String(e.n), pc(e.won / e.n, 0), pc(e.gone / e.n, 0), fx(e.longest / e.n, 1), fx(e.total / e.n, 1), fx(e.units / e.n, 1)] : null; }).filter(Boolean))));
  md.push('');
  md.push('### 5.2 성장 곡선 (팀·경기 평균, 전멸은 0): 수 / 총길이 / 최장');
  for (const el of ['E', 'R']) {
    md.push(`#### ${el === 'E' ? '전멸형' : '500형'} 지도`);
    md.push(tbl(['집단', ...J.growthRounds.map(r => 'r' + r)], groups.map(g => [gname(g), ...J.growthRounds.map(r => { const e = J.growth[g + '|' + el + '|' + r]; return e && e.n ? `${fx(e.u / e.n, 1)} / ${fx(e.tot / e.n, 0)} / ${fx(e.lg / e.n, 1)}` : '–'; })])));
    md.push('');
  }
  md.push('### 5.3 사망 (팀·경기당): 원인별');
  const causes = ['V', 'V-ally', 'H', 'O', 'sk-S', 'sk-W', 'sk-Aq', 'sk-Ax', 'trap-S', 'trap-W', 'trap-Ax', 'trap-Aq', 'Ap', 'At', 'An'];
  md.push(tbl(['집단', '길이', ...causes], groups.flatMap(g => LENS.map((l, lc) => [gname(g), l, ...causes.map(c => { let n = 0; for (let mi = 0; mi < MAPS.length; mi++) { const e = J.deaths[g + '|' + mi + '|' + lc + '|' + c]; if (e) n += e[0]; } const tg = J.meta.tgCount[g + '|all']; return n && tg ? fx(n / tg, 2) : '–'; })]))));
  md.push('- V = 적 머리에 박힘(적이 박음), V-ally = 아군 머리에 박힘, H = 우리가 머리로 박음(같이 죽음), O = 남의 몸, sk-* = 빈 이웃이 있는데 자기 몸(S)·해초(W)·불법 분열(Aq)·행동 없음(Ax), trap-* = 빈 이웃 없이 같은 방식, Ap = 질주 비용 부족, At = 시간 초과, An = 그 밖의 무행동.');
  md.push('');
  md.push('### 5.4 상위 팀 (음파·분열·승률)');
  md.push(tbl(['팀', '판', '승률', '드래곤 턴당 핑', '핑당 아군', '핑당 적', '판당 분열'], Object.entries(J.teamStats).sort((a, b) => b[1].games - a[1].games).map(([t, e]) => [t, String(e.games), pc(e.wins / e.games, 0), fx(e.pings / Math.max(1, e.turns), 2), pc(e.pA / Math.max(1, e.pings)), pc(e.pE / Math.max(1, e.pings)), fx(e.splits / e.games, 0)])));
  md.push('');
  return md.join('\n') + '\n';
}
