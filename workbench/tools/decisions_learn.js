#!/usr/bin/env node
// Learn top-team decision rules from the decision dataset (tools/decisions.js) and compare our bot's decisions in the
// same states. Interpretable models only: weighted conditional frequency tables and small CART trees fitted on the
// top-vs-top rows; the rows of our games are routed through the same tree leaves. Reads data/decisions only.
//
// usage: node tools/decisions_learn.js [--top top-20260929a] [--sets s1,s2,...] [--base <submission id>]
//                                      [--out data/decisions/report] [--cap 250000]
//   --top   top-vs-top set. Games with SSS are dropped (broken bot in 19 snapshot games; top-timing.md).
//   --sets  online sets (default: every data/decisions/<set> whose games have our side).
//   --base  our current bot's submission id (default: the submission of baseline-r1, else the most common one).
//           Other submissions are reported as candidates, one group per submission.
//   --cap   rows kept per decision type and group for tree fitting (uniform reservoir sample; weights kept;
//           default 150000, the pooled opponents X keep 40% of it).
// Output: <out>.json (every number in the report) and <out>.md (Korean: dataset, learned top rules per decision
//   type with supports and winners vs losers, our divergences per tree leaf, ranked divergences with impact).
//
// Groups: T = top-vs-top (both teams), TW / TL = winning / losing team of a top-vs-top game, O = our current bot in
// the online sets, X = the top opponents in the online sets (all sets pooled), C<sub> = our candidate submissions.
'use strict';
const fs = require('fs'), path = require('path');
const Lb = require('./decisions_lib.js');
const { Acc, fitTree, leafOf, leaves, pct, fx, fint, mdTable, wilson } = Lb;

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const TOPSET = opt('top', 'top-20260929a');
const OUT = path.resolve(Lb.ROOT, opt('out', path.join('data', 'decisions', 'report')));
const CAP = +opt('cap', 150000); // X (opponents of every online set) keeps CAP * 0.4
const allSets = fs.readdirSync(Lb.DEC).filter(s => fs.existsSync(path.join(Lb.DEC, s, 'games.jsonl')));
const SETS = opt('sets', null) ? opt('sets').split(',') : allSets.filter(s => s !== TOPSET && Lb.readJsonl(path.join(Lb.DEC, s, 'games.jsonl')).some(g => g.ourSide));
const subOf = new Map(); // set -> submission ids
for (const s of SETS) subOf.set(s, [...new Set(Lb.readJsonl(path.join(Lb.DEC, s, 'games.jsonl')).map(g => g.ourSubmission))]);
let BASE = opt('base', null);
if (BASE === null) {
  if (subOf.has('baseline-r1')) BASE = subOf.get('baseline-r1')[0];
  else { const c = {}; for (const v of subOf.values()) for (const x of v) c[x] = (c[x] || 0) + 1; BASE = Object.entries(c).sort((a, b) => b[1] - a[1])[0][0]; }
}
BASE = String(BASE);

// ---------------------------------------------------------------------------------------------------------------
// Row view: numbers for the fields the specs use.
const NUMF = ['r', 'id', 'L', 'born', 'free', 'nbE', 'room', 'roomMax', 'tFree', 'tE', 'eN', 'eNs', 'eNr', 'eNrs', 'eD0', 'eM0', 'eL',
  'eVis', 'eKn', 'eAft', 'eFw', 'eLmin', 'safe1', 'exp1', 'safe1a', 'exp1a', 'safe2', 'oppN', 'oppL', 'oppD', 'pN', 'pD0', 'pEd', 'pDang',
  'aN', 'aD', 'aL', 'aMaxL', 'aDg', 'aLg', 'kD', 'eDg', 'U', 'TL', 'TT', 'king', 'kRank', 'EU', 'EL', 'ptlN', 'ptlV', 'k', 'c', 'eD1', 'eM1',
  'pD1', 'aDg1', 'endExp', 'endExpA', 'roomAct', 'ate', 'ptlK', 'hitL', 'ram', 'al1', 'al5', 'al10', 'L1', 'L5', 'L10', 'eat5', 'eat10',
  'eatS10', 'dr', 'dbyL', 'F10', 'Fu10', 'kill10', 'feedS', 'feedE', 'feedK', 'cid', 'cAl10', 'cL10', 'w'];
const SELF_KILL = new Set(['S', 'W', 'Aq', 'Ax']);
function view(v, C) {
  const z = {};
  for (const f of NUMF) z[f] = +v[C[f]];
  z.act = v[C.act]; z.fate = v[C.fate]; z.dwhy = v[C.dwhy]; z.d1 = v[C.d1]; z.tm = v[C.tm];
  z.sk = SELF_KILL.has(z.fate) && z.free >= 1 ? 1 : 0;
  z.rammed1 = z.al1 === 0 && z.dwhy === 'V' ? 1 : 0;
  z.rammed5 = z.al5 === 0 && z.dwhy === 'V' ? 1 : 0;
  z.net10 = z.F10 - z.L + z.kill10;           // family length change over 10 rounds plus enemy length killed head-on
  z.move = z.act === 'M' ? 1 : 0;
  const dd = z.eD0 <= 8 && z.eD1 <= 8 ? z.eD1 - z.eD0 : z.eM1 - z.eM0;
  z.eDelta = dd;                              // focus enemy distance change (path, else Manhattan)
  z.thr = z.eNs === 0 ? -1 : z.exp1 === 0 && z.eNrs === 0 ? 0 : z.exp1 === 0 ? 1 : z.safe1 > 0 ? 2 : z.safe2 > 0 ? 3 : 4;
  return z;
}

// ---------------------------------------------------------------------------------------------------------------
// Decision specs: population, binary label, tree features (observable to the bot, or shared by team sonar: marked
// with *), outcome values. Outcomes are means over rows (weighted).
const F = (name, fn) => [name, fn];
const OUTS = {
  net10: z => z.net10, rammed1: z => z.rammed1, dead5: z => 1 - z.al5, eat10: z => z.eat10, Fu10: z => z.Fu10,
  feedK: z => z.sk ? z.feedK : 0, feedS: z => z.sk ? z.feedS : 0,
};
const SPECS = [
  {
    id: 'a1', type: 'a', title: '긴 드래곤(L≥6), 더 짧은 적 머리가 한 걸음 칸이나 우리 머리에 닿음: 노출 칸에서 끝내는가',
    pop: z => z.L >= 6 && z.eNs >= 1 && z.move && z.fate === '' && (z.exp1 > 0 || z.eNrs > 0),
    label: z => z.endExp === 1 ? 1 : 0, yes: '노출 칸에서 끝냄', no: '도달 밖에서 끝냄',
    feats: [F('safe1', z => z.safe1), F('exp1', z => z.exp1), F('safe2', z => z.safe2), F('eD0', z => Math.min(z.eD0, 9)), F('eL', z => Math.min(z.eL, 12)),
      F('L', z => Math.min(z.L, 40)), F('eNrs', z => z.eNrs), F('room', z => z.room), F('r', z => z.r), F('U', z => Math.min(z.U, 64)), F('king*', z => z.king), F('eAft', z => z.eAft)],
  },
  {
    id: 'a2', type: 'a', title: '긴 드래곤(L≥6), 한 걸음은 모두 노출이고 질주 탈출이 있음: 질주하는가',
    pop: z => z.L >= 6 && z.eNs >= 1 && z.move && z.fate === '' && z.safe1 === 0 && z.exp1 > 0 && z.safe2 > 0,
    label: z => z.k >= 2 ? 1 : 0, yes: '질주', no: '한 걸음',
    feats: [F('safe2', z => z.safe2), F('eD0', z => Math.min(z.eD0, 9)), F('eL', z => Math.min(z.eL, 12)), F('L', z => Math.min(z.L, 40)), F('eNrs', z => z.eNrs),
      F('room', z => z.room), F('r', z => z.r), F('U', z => Math.min(z.U, 64)), F('king*', z => z.king)],
  },
  {
    id: 'a3', type: 'a', title: '긴 드래곤(L≥6), 더 짧은 적 머리가 3–6칸(아직 도달 밖): 다가가는가',
    pop: z => z.L >= 6 && z.eNs >= 1 && z.move && z.fate === '' && z.exp1 === 0 && z.eNrs === 0 && z.eD0 >= 3 && z.eD0 <= 6,
    label: z => z.eDelta < 0 ? 1 : 0, yes: '다가감', no: '유지·멀어짐',
    feats: [F('eD0', z => z.eD0), F('eL', z => Math.min(z.eL, 12)), F('L', z => Math.min(z.L, 40)), F('pD0', z => Math.min(z.pD0, 9)), F('room', z => z.room),
      F('r', z => z.r), F('U', z => Math.min(z.U, 64)), F('king*', z => z.king), F('eFw', z => z.eFw)],
  },
  {
    id: 'b1', type: 'b', title: '작은 조각(L≤4), 이번 턴에 적 머리를 박을 수 있음: 박는가',
    pop: z => z.L <= 4 && z.oppN >= 1 && (z.act === 'M' || z.act === 'P'),
    label: z => z.ram === 1 ? 1 : 0, yes: '박음', no: '안 박음',
    feats: [F('oppL-L', z => Math.max(-4, Math.min(z.oppL - z.L, 8))), F('oppD', z => z.oppD), F('L', z => z.L), F('U', z => Math.min(z.U, 64)), F('r', z => z.r),
      F('aN', z => Math.min(z.aN, 6)), F('eN', z => Math.min(z.eN, 6)), F('eAft', z => z.eAft), F('free', z => z.free)],
  },
  {
    id: 'b2', type: 'b', title: '작은 조각(L≤4), 적 머리가 보이지만 이번 턴에 박을 수 없음: 다가가는가',
    pop: z => z.L <= 4 && z.eN >= 1 && z.oppN === 0 && z.move && z.fate === '',
    label: z => z.eDelta < 0 ? 1 : 0, yes: '다가감', no: '유지·멀어짐',
    feats: [F('eD0', z => Math.min(z.eD0, 9)), F('eL-L', z => Math.max(-4, Math.min(z.eL - z.L, 8))), F('L', z => z.L), F('U', z => Math.min(z.U, 64)), F('r', z => z.r),
      F('aN', z => Math.min(z.aN, 6)), F('eNr', z => z.eNr), F('pD0', z => Math.min(z.pD0, 9))],
  },
  {
    id: 'c1', type: 'c', title: '분열할 수 있는 턴(L≥4): 분열하는가',
    pop: z => z.L >= 4 && z.U < 64 && (z.act === 'M' || z.act === 'P'),
    label: z => z.act === 'P' ? 1 : 0, yes: '분열', no: '이동',
    feats: [F('L', z => Math.min(z.L, 40)), F('r', z => z.r), F('U', z => Math.min(z.U, 64)), F('eN', z => Math.min(z.eN, 6)), F('eNr', z => z.eNr), F('room', z => z.room),
      F('tFree', z => z.tFree), F('free', z => z.free), F('aN', z => Math.min(z.aN, 6)), F('pN', z => Math.min(z.pN, 9)), F('king*', z => z.king)],
  },
  {
    id: 'c2', type: 'c', title: '분열할 때: 자식을 2칸으로 떼는가(아니면 몸 대부분을 넘기는 stub 등)',
    pop: z => z.act === 'P',
    label: z => z.c === 2 ? 1 : 0, yes: '자식 2', no: '그 밖',
    feats: [F('L', z => Math.min(z.L, 40)), F('r', z => z.r), F('free', z => z.free), F('room', z => z.room), F('eNr', z => z.eNr), F('U', z => Math.min(z.U, 64))],
  },
  {
    id: 'd1', type: 'd', title: '빈 이웃이 있는 턴: 스스로 죽는가(자기 몸·해초·SPLIT 1·행동 없음)',
    pop: z => z.free >= 1,
    label: z => z.sk, yes: '자해', no: '그 밖', cur: 'feedK',
    feats: [F('r', z => z.r), F('L', z => Math.min(z.L, 40)), F('U', z => Math.min(z.U, 64)), F('kRank*', z => Math.min(z.kRank, 64)), F('aDg*', z => Math.min(z.aDg, 30)),
      F('aLg*', z => Math.min(z.aLg, 40)), F('kD*', z => Math.min(z.kD, 40)), F('eN', z => Math.min(z.eN, 6)), F('aN', z => Math.min(z.aN, 6)), F('TL*', z => Math.min(z.TL, 60))],
  },
  {
    id: 'e1', type: 'e', title: '3걸음 안에 보이는 진주가 있음: 진주 쪽으로 가는가',
    pop: z => z.move && z.pD0 <= 3,
    label: z => z.pD1 < z.pD0 ? 1 : 0, yes: '진주 쪽', no: '다른 쪽',
    feats: [F('pD0', z => z.pD0), F('pDang', z => z.pDang), F('pEd-pD0', z => Math.max(-3, Math.min(z.pEd - z.pD0, 9))), F('L', z => Math.min(z.L, 40)), F('eNrs', z => z.eNrs),
      F('exp1', z => z.exp1), F('eN', z => Math.min(z.eN, 6)), F('r', z => z.r), F('U', z => Math.min(z.U, 64)), F('king*', z => z.king)],
  },
  {
    id: 'f1', type: 'f', title: '왕(팀 최장), 300라운드 이후: 가장 가까운 아군 쪽으로 가는가',
    pop: z => z.king === 1 && z.r >= 300 && z.move && z.fate === '' && z.aDg < 99,
    label: z => z.aDg1 < z.aDg ? 1 : 0, yes: '아군 쪽', no: '그 밖',
    feats: [F('aDg*', z => Math.min(z.aDg, 30)), F('aLg*', z => Math.min(z.aLg, 40)), F('L', z => Math.min(z.L, 60)), F('eN', z => Math.min(z.eN, 6)), F('r', z => z.r),
      F('U', z => Math.min(z.U, 64)), F('pD0', z => Math.min(z.pD0, 9))],
  },
  {
    id: 'g1', type: 'g', title: '머리 칸에 포털 변이 있음: 포털을 지나는가',
    pop: z => z.move && z.ptlN >= 1,
    label: z => z.ptlK >= 1 ? 1 : 0, yes: '포털 통과', no: '통과 안 함',
    feats: [F('ptlN', z => z.ptlN), F('L', z => Math.min(z.L, 40)), F('eN', z => Math.min(z.eN, 6)), F('pN', z => Math.min(z.pN, 9)), F('pD0', z => Math.min(z.pD0, 9)),
      F('free', z => z.free), F('room', z => z.room), F('r', z => z.r), F('U', z => Math.min(z.U, 64))],
  },
  {
    id: 'h1', type: 'h', title: '긴 드래곤(L≥6), 넓은 첫걸음(방 ≥ L+2)이 있음: 좁은 쪽으로 들어가는가',
    pop: z => z.L >= 6 && z.move && z.roomMax >= z.L + 2,
    label: z => z.roomAct < z.L + 2 ? 1 : 0, yes: '좁은 쪽', no: '넓은 쪽',
    feats: [F('L', z => Math.min(z.L, 40)), F('room', z => z.room), F('free', z => z.free), F('eN', z => Math.min(z.eN, 6)), F('pD0', z => Math.min(z.pD0, 9)), F('r', z => z.r)],
  },
];

// ---------------------------------------------------------------------------------------------------------------
// Load
const groupsOf = (g, z) => {
  if (!g.ourSide) {
    const out = ['T'];
    if (g.winner === 'A' || g.winner === 'B') out.push(z.tm === g.winner ? 'TW' : 'TL');
    return out;
  }
  if (z.tm !== g.ourSide) return ['X'];
  return [String(g.ourSubmission) === BASE ? 'O' : 'C' + g.ourSubmission];
};
const gameCount = {}, teamGames = {}, setsOfGroup = {};
const tables = new Acc();         // spec|group -> label sums and outcomes; spec|group|label
const samples = {};               // spec -> group -> {rows:[[feat..., label, w, outcomes...]], seen}
const extra = new Acc();          // descriptive tables (deaths, king, self-kill placement, child size, ...)
let rng = 12345; const rand = () => { rng = (Math.imul(rng, 1103515245) + 12345) >>> 0; return rng / 4294967296; };
function sampleAdd(spec, grp, rec) {
  const S = (samples[spec.id] || (samples[spec.id] = {}));
  const s = S[grp] || (S[grp] = { rows: [], seen: 0 });
  s.seen++;
  const cap = grp === 'X' ? Math.floor(CAP * 0.4) : CAP;
  if (s.rows.length < cap) s.rows.push(rec);
  else { const j = Math.floor(rand() * s.seen); if (j < cap) s.rows[j] = rec; }
}
function loadSet(set, isTop) {
  for (const { g, C, rows } of Lb.gamesOf(set)) {
    if (isTop && (Lb.EXCLUDE_TEAMS.has(g.teamName.A) || Lb.EXCLUDE_TEAMS.has(g.teamName.B))) continue;
    const elim = Lb.ELIM_MAPS.has(g.map) ? 1 : 0;
    // game and team-game counts per group
    const gs = new Set();
    for (const tm of ['A', 'B']) for (const gr of groupsOf(g, { tm })) { teamGames[gr] = (teamGames[gr] || 0) + 1; gs.add(gr); }
    for (const gr of gs) { gameCount[gr] = (gameCount[gr] || 0) + 1; (setsOfGroup[gr] || (setsOfGroup[gr] = new Set())).add(set); }
    for (const tm of ['A', 'B']) for (const gr of groupsOf(g, { tm })) {
      const fin = g.final[tm], won = g.winner === tm ? 1 : 0, gone = fin[0] === 0 ? 1 : 0;
      extra.add(`game|${gr}|${elim ? 'E' : 'R'}`, 1, { won, gone, goneR: gone ? g.rounds : NaN, longest: fin[1], units: fin[0] });
      extra.add(`gamemap|${gr}|${g.map}`, 1, {});
    }
    const lastOf = new Map(); for (const v of rows) lastOf.set(v[C.id], v);
    const uAt = { A: {}, B: {} }; // team units at rounds 10, 25, 50, 100 (0 when the team is gone)
    for (const v of rows) { const r = +v[C.r]; if (r === 10 || r === 25 || r === 50 || r === 100) uAt[v[C.tm]][r] = Math.max(uAt[v[C.tm]][r] || 0, +v[C.U]); }
    for (const tm of ['A', 'B']) for (const gr of groupsOf(g, { tm })) for (const r of [10, 25, 50, 100]) if (g.rounds > r || (uAt[tm][r] || 0) === 0) extra.add(`unitsAt|${gr}|${elim ? 'E' : 'R'}|${r}`, 1, { U: uAt[tm][r] || 0 });
    for (const v of rows) {
      const z = view(v, C); z.elim = elim;
      const grs = groupsOf(g, z), w = z.w;
      for (const spec of SPECS) {
        if (!spec.pop(z)) continue;
        const y = spec.label(z);
        const feats = spec.feats.map(f => f[1](z));
        const outs = {}; for (const k in OUTS) outs[k] = OUTS[k](z);
        for (const gr of grs) {
          tables.add(`${spec.id}|${gr}`, w, { y });
          tables.add(`${spec.id}|${gr}|${y}`, w, outs);
          if (gr !== 'TW' && gr !== 'TL') sampleAdd(spec, gr, { x: feats, y, w, o: outs, win: grs.includes('TW') ? 1 : grs.includes('TL') ? 0 : -1 });
        }
      }
      // descriptive: deaths (last row of a dragon that died, exact rows only), king by phase, sacrifices, splits
      for (const gr of grs) {
        extra.add(`turns|${gr}`, w, { L: z.L });
        if (lastOf.get(v[C.id]) === v && z.dr >= 0 && w === 1) {
          const lb = z.L >= 6 ? 'L6+' : 'L<=5';
          extra.add(`death|${gr}|${lb}|${z.dwhy}`, 1, { L: z.L });
          if (z.dwhy === 'V') {
            const st = z.eN === 0 ? 'unseen' : z.eNrs > 0 ? 'inReach' : z.safe1 === 0 && z.exp1 > 0 ? 'allExp' : z.exp1 > 0 ? 'someExp' : 'noExp';
            extra.add(`deathV|${gr}|${lb}|${st}`, 1, { L: z.L, endExp: z.endExp === 1 ? 1 : 0, split: z.act === 'P' ? 1 : 0 });
          }
        }
        if (z.king === 1 && z.r >= 200) {
          const ph = Math.floor(z.r / 50) * 50;
          extra.add(`king|${gr}|${ph}`, w, { L: z.L, U: z.U, aDg: z.aDg, aN: z.aN, eDg: z.eDg, eat10: z.eat10, eatS10: z.eatS10, danger: z.eNrs > 0 ? 1 : 0, exp: z.endExp === 1 ? 1 : 0, sprint: z.move && z.k >= 2 ? 1 : 0 });
        }
        if (z.king === 0 && z.r >= 200) extra.add(`nonking|${gr}|${Math.floor(z.r / 50) * 50}`, w, { kD: z.kD, L: z.L });
        if (z.sk) {
          const ph = z.r < 250 ? 'r0-249' : z.r < 350 ? 'r250-349' : z.r < 450 ? 'r350-449' : 'r450+';
          extra.add(`sk|${gr}|${ph}`, w, { L: z.L, U: z.U, aDg: z.aDg, aLg: z.aLg, kD: z.kD, aN: z.aN, eN: z.eN, drop: Math.ceil(z.L / 2), feedS: z.feedS, feedK: z.feedK, feedE: z.feedE, kRank: z.kRank, king: z.king });
          extra.add(`skhow|${gr}|${z.fate}${z.fate === 'S' && z.d1 === 'B' ? 'B' : ''}`, w, {});
        }
        if (z.act === 'P' || ((z.act === 'M') && z.L >= 4)) {
          const lb = z.L === 4 ? '4' : z.L === 5 ? '5' : z.L <= 7 ? '6-7' : z.L <= 11 ? '8-11' : '12+';
          const ph = z.r < 100 ? 'r0-99' : z.r < 250 ? 'r100-249' : z.r < 400 ? 'r250-399' : 'r400+';
          extra.add(`split|${gr}|${lb}|${ph}`, w, { split: z.act === 'P' ? 1 : 0 });
          extra.add(`split|${gr}|${lb}`, w, { split: z.act === 'P' ? 1 : 0 });
          extra.add(`splitE|${gr}|${lb}|${z.eN > 0 ? 1 : 0}`, w, { split: z.act === 'P' ? 1 : 0 });
          const ub = z.U <= 2 ? 'U1-2' : z.U <= 5 ? 'U3-5' : z.U <= 15 ? 'U6-15' : z.U <= 31 ? 'U16-31' : 'U32+';
          extra.add(`splitU|${gr}|${lb}|${ub}`, w, { split: z.act === 'P' ? 1 : 0 });
          if (z.act === 'P') {
            const kind = z.c === 2 ? 'c2' : z.L - z.c <= 3 && z.c >= 4 ? 'stub' : 'mid';
            extra.add(`child|${gr}|${lb}|${kind}`, w, { cAl10: z.cAl10, net10: z.net10, Fu10: z.Fu10 });
            extra.add(`child|${gr}|${lb}`, w, {});
          }
        }
        if (z.move && z.k >= 2) extra.add(`sprint|${gr}|${z.eN > 0 ? 'e' : 'n'}`, w, {});
        if ((z.act === 'M' || z.act === 'P') && z.L >= 8 && z.room >= 1 && z.room <= 5) { extra.add(`loopmap|${gr}|${g.map}`, w, { split: z.act === 'P' ? 1 : 0 }); extra.add(`loopcorr|${gr}|${g.map === 'Autarky' || g.map === 'Prisoners Dilemma' ? 'corr' : 'other'}`, w, { split: z.act === 'P' ? 1 : 0, net10: z.net10 }); }
        if (z.nbE >= 1) { const lg = z.L <= 4 ? 'small' : z.L <= 9 ? 'mid' : 'big'; extra.add(`adj|${gr}|${lg}`, w, { ram: z.ram === 1 && z.k === 1 ? 1 : 0 }); }
        if (z.act === 'P') extra.add(`splitkind|${gr}|${z.L === 4 && z.c === 2 ? '4to2+2' : 'other'}`, w, {});
        if (z.sk) extra.add(`skr|${gr}|${Math.min(499, z.r)}`, w, {});
        if (z.move && z.pD0 <= 3) {
          const sz = z.L <= 4 ? 's' : z.L <= 9 ? 'm' : 'l', dz = z.pDang === 1 ? 'dang' : z.pEd <= z.pD0 ? 'contest' : 'free';
          extra.add(`pearlDz|${gr}|${sz}|${dz}`, w, { tow: z.pD1 < z.pD0 ? 1 : 0, rammed1: z.rammed1, net10: z.net10 });
        }
        if (z.move) extra.add(`moves|${gr}|${z.eN > 0 ? 'e' : 'n'}`, w, {});
        if (z.ate > 0) extra.add(`eat|${gr}`, w * z.ate, {});
        { const lb = z.L <= 2 ? '2' : z.L <= 4 ? '3-4' : z.L <= 9 ? '5-9' : z.L <= 19 ? '10-19' : '20+'; extra.add(`eatL|${gr}|${lb}`, w, { ate: z.ate, eat10: z.eat10 }); }
        if (z.move && z.ptlK > 0) extra.add(`portal|${gr}`, w * z.ptlK, {});
      }
    }
  }
}
const t0 = Date.now();
loadSet(TOPSET, true);
for (const s of SETS) loadSet(s, false);
const GROUPS = Object.keys(gameCount).sort((a, b) => { const o = ['T', 'TW', 'TL', 'O', 'X']; return (o.indexOf(a) < 0 ? 9 : o.indexOf(a)) - (o.indexOf(b) < 0 ? 9 : o.indexOf(b)) || a.localeCompare(b); });
console.error(`loaded in ${((Date.now() - t0) / 1000).toFixed(0)}s; games ${JSON.stringify(gameCount)}`);

// ---------------------------------------------------------------------------------------------------------------
// Trees: fit on T samples, route every group's samples, aggregate per leaf.
const RESULTS = {};
for (const spec of SPECS) {
  const S = samples[spec.id] || {};
  const T = S.T;
  const res = { id: spec.id, type: spec.type, title: spec.title, yes: spec.yes, no: spec.no, overall: {}, leaves: [] };
  for (const gr of GROUPS) {
    const e = tables.get(`${spec.id}|${gr}`);
    if (!e.n) continue;
    const y1 = tables.get(`${spec.id}|${gr}|1`), y0 = tables.get(`${spec.id}|${gr}|0`);
    const o = {};
    for (const k in OUTS) { o[k + '|1'] = tables.mean(`${spec.id}|${gr}|1`, k); o[k + '|0'] = tables.mean(`${spec.id}|${gr}|0`, k); }
    res.overall[gr] = { n: e.n, w: e.w, p: e.s.y / e.w, n1: y1.n, n0: y0.n, perGame: e.w / teamGames[gr], out: o };
  }
  if (T && T.rows.length >= 400) {
    const names = spec.feats.map(f => f[0]);
    const X = T.rows.map(r => r.x), y = T.rows.map(r => r.y), w = T.rows.map(r => r.w);
    const minN = Math.max(60, Math.floor(T.rows.length / 150));
    const tree = fitTree(X, y, w, 2, names, { maxDepth: 4, minLeafN: minN, minLeafW: minN, minGain: 0.004 });
    const lv = leaves(tree);
    const byNode = new Map(lv.map((l, i) => [l.node.id, i]));
    const agg = lv.map(() => ({}));
    for (const gr of Object.keys(S)) for (const r of S[gr].rows) {
      const li = byNode.get(leafOf(tree, r.x).id), a = agg[li];
      const keys = gr === 'T' ? ['T', r.win === 1 ? 'TW' : r.win === 0 ? 'TL' : null] : [gr];
      for (const k of keys) {
        if (!k) continue;
        const e = a[k] || (a[k] = { n: 0, w: 0, wy: 0, o1: {}, o0: {}, n1: 0, n0: 0 });
        e.n++; e.w += r.w; e.wy += r.w * r.y;
        const oo = r.y ? e.o1 : e.o0; if (r.y) e.n1++; else e.n0++;
        for (const kk in r.o) { oo[kk] = (oo[kk] || 0) + r.w * r.o[kk]; oo[kk + '#'] = (oo[kk + '#'] || 0) + r.w; }
      }
    }
    // scale sample weights to all rows of the group (reservoir keeps a uniform subset)
    for (const gr of Object.keys(S)) {
      const s = S[gr], scale = s.seen / s.rows.length;
      for (const a of agg) for (const k of gr === 'T' ? ['T', 'TW', 'TL'] : [gr]) if (a[k] && !a[k].scaled) { a[k].w *= scale; a[k].wy *= scale; a[k].scaled = true; for (const oo of [a[k].o1, a[k].o0]) for (const kk in oo) oo[kk] *= scale; }
    }
    res.tree = { names, sampleT: T.rows.length, seenT: T.seen, minLeafN: minN };
    res.leaves = lv.map((l, i) => {
      const a = agg[i], o = {};
      for (const gr in a) {
        const e = a[gr];
        const m = (oo, k) => oo[k + '#'] ? oo[k] / oo[k + '#'] : NaN;
        o[gr] = { n: e.n, w: e.w, p: e.w ? e.wy / e.w : NaN, n1: e.n1, n0: e.n0, perGame: e.w / teamGames[gr],
          out: Object.fromEntries(Object.keys(OUTS).flatMap(k => [[k + '|1', m(e.o1, k)], [k + '|0', m(e.o0, k)]])) };
      }
      return { text: l.text, g: o };
    });
  }
  RESULTS[spec.id] = res;
}

// ---------------------------------------------------------------------------------------------------------------
// Divergences. Per spec and leaf: our rate vs the top rate, weighted by how often we are in the leaf, times the
// outcome difference between doing the action and not doing it in that leaf.
//   impact = (our leaf turns per team-game) x (P_top - P_ours) x (outcome|yes - outcome|no)
// The outcome difference comes from the top-vs-top rows of the leaf (dT): there both actions are common, while in our
// games the rarer action is usually taken in special situations (e.g. our few splits in open space are escape splits).
// Our own difference (dO) is shown as a check when both actions have >= 30 of our rows in the leaf.
// Currency: net10 (family length change over 10 rounds + enemy length killed head-on) unless the spec names another
// one (sacrifices: feedK = pearls the own king eats from the drop within 20 rounds, a G proxy).
// Leaves are then pooled into rules: per spec, "do it more (like top)" = leaves where P_top > P_ours, and "do it less".
const MIN_GAP = 0.02;
function divergences(ourGroup) {
  const leavesOut = [], rules = new Map();
  for (const spec of SPECS) {
    const cur = spec.cur || 'net10';
    const res = RESULTS[spec.id];
    for (const [i, lf] of res.leaves.entries()) {
      const O = lf.g[ourGroup], T = lf.g.T;
      if (!O || !T || O.n < 30 || T.n < 30) continue;
      const gap = T.p - O.p;
      if (Math.abs(gap) < MIN_GAP) continue;
      const dT = (T.out[cur + '|1'] || 0) - (T.out[cur + '|0'] || 0);
      const dO = O.n1 >= 30 && O.n0 >= 30 ? O.out[cur + '|1'] - O.out[cur + '|0'] : NaN;
      const impT = Number.isFinite(dT) ? O.perGame * gap * dT : NaN;
      const impO = Number.isFinite(dO) ? O.perGame * gap * dO : NaN;
      const rec = { spec: spec.id, leaf: i, text: lf.text, yes: spec.yes, cur, pT: T.p, pO: O.p, pTW: lf.g.TW ? lf.g.TW.p : NaN, pTL: lf.g.TL ? lf.g.TL.p : NaN,
        nT: T.n, nO: O.n, perGame: O.perGame, dT, dO, impT, impO };
      leavesOut.push(rec);
      const key = spec.id + (gap > 0 ? '+' : '-');
      const r = rules.get(key) || { key, spec: spec.id, title: spec.title, yes: spec.yes, dir: gap > 0 ? 'more' : 'less', cur, perGame: 0, impT: 0, impO: 0, impOn: 0, leaves: [] };
      r.perGame += O.perGame; if (Number.isFinite(impT)) r.impT += impT; if (Number.isFinite(impO)) { r.impO += impO; r.impOn++; }
      r.leaves.push(i);
      rules.set(key, r);
    }
  }
  leavesOut.sort((a, b) => Math.abs(b.impT) - Math.abs(a.impT));
  const rl = [...rules.values()].sort((a, b) => Math.abs(b.impT) - Math.abs(a.impT));
  return { leaves: leavesOut, rules: rl };
}
const DIV = { O: divergences('O') };
for (const gr of GROUPS) if (gr.startsWith('C')) DIV[gr] = divergences(gr);

// ---------------------------------------------------------------------------------------------------------------
// Report
const J = { meta: { top: TOPSET, sets: SETS, base: BASE, groups: GROUPS, gameCount, teamGames, setsOfGroup: Object.fromEntries(Object.entries(setsOfGroup).map(([k, v]) => [k, [...v]])), cap: CAP, created: new Date().toISOString() },
  results: RESULTS, divergences: DIV, extra: extra.toJSON() };
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT + '.json', JSON.stringify(J, (k, v) => typeof v === 'number' && !Number.isFinite(v) ? null : v));

const gname = gr => ({ T: '상위끼리', TW: '상위 승자', TL: '상위 패자', O: `우리(${BASE})`, X: '우리 경기의 상위 상대' }[gr] || `후보 ${gr.slice(1)}`);
const P = (e, d = 1) => e && e.w ? (100 * e.p).toFixed(d) + '%' : '–';
const md = [];
md.push(`# 결정 단위 비교 보고서 (자동 생성)`);
md.push('');
md.push(`- 생성: ${J.meta.created}. 명령: \`node tools/decisions_learn.js\`. 자료: \`data/decisions/\`(\`tools/decisions.js\`).`);
md.push(`- 상위끼리: \`${TOPSET}\` ${gameCount.T}판(SSS가 낀 판 제외). 온라인 세트: ${SETS.map(s => `\`${s}\``).join(', ')}. 우리 기준 제출: ${BASE}.`);
md.push(`- 집단: ${GROUPS.map(g => `${gname(g)} ${gameCount[g]}판`).join(', ')}.`);
md.push(`- 비율은 가중치(표본 턴 ×${8})를 반영한 턴 비율이다. n은 실제 행 수다. "판당"은 팀·경기당이다.`);
md.push('');
md.push('## 결정 유형별 전체 비율');
const hdr = ['결정', '예', ...GROUPS.map(gname)];
md.push(mdTable(hdr, SPECS.map(s => { const r = RESULTS[s.id]; return [`${s.id} ${s.title}`, s.yes, ...GROUPS.map(gr => r.overall[gr] ? `${P(r.overall[gr])} (n ${fint(r.overall[gr].n)}, 판당 ${fx(r.overall[gr].perGame, 1)})` : '–')]; })));
md.push('');
md.push('- 결과(net10 = 10라운드 뒤 가족 길이 − 지금 길이 + 머리로 죽인 적 길이), 예/아니오별 평균:');
md.push(mdTable(['결정', ...GROUPS.slice(0, 5).map(gname)], SPECS.map(s => { const r = RESULTS[s.id]; return [s.id, ...GROUPS.slice(0, 5).map(gr => r.overall[gr] ? `${fx(r.overall[gr].out['net10|1'])} / ${fx(r.overall[gr].out['net10|0'])}` : '–')]; })));
md.push('');
for (const spec of SPECS) {
  const r = RESULTS[spec.id], cur = spec.cur || 'net10';
  md.push(`## ${spec.id}. ${spec.title}`);
  if (!r.tree) { md.push('- 상위 표본이 적어 나무를 만들지 않았다.'); md.push(''); continue; }
  md.push(`- 나무: 상위끼리 표본 ${fint(r.tree.sampleT)}행(전체 ${fint(r.tree.seenT)}행), 깊이 ≤ 4, 잎 최소 ${r.tree.minLeafN}행. 특징: ${r.tree.names.join(', ')} (*는 음파로 팀이 공유해야 아는 값).`);
  const rows = r.leaves.map((l, i) => {
    const T = l.g.T, O = l.g.O, TW = l.g.TW, TL = l.g.TL, X = l.g.X;
    const ci = O && O.n ? wilson(O.p, O.n) : null;
    return [String(i), l.text, T ? fint(T.n) : '0', P(T), P(TW), P(TL), O ? fint(O.n) : '0', O ? `${P(O)}${ci ? ` [${Math.max(0, 100 * ci[0]).toFixed(0)}–${Math.min(100, 100 * ci[1]).toFixed(0)}]` : ''}` : '–',
      O ? fx(O.perGame, 2) : '–', X ? P(X) : '–', T ? `${fx(T.out[cur + '|1'])}/${fx(T.out[cur + '|0'])}` : '–', O ? `${fx(O.out[cur + '|1'])}/${fx(O.out[cur + '|0'])}` : '–'];
  });
  md.push(mdTable(['잎', '조건', '상위 n', `상위 ${spec.yes}`, '승자', '패자', '우리 n', `우리 ${spec.yes}`, '우리 판당', '상대(우리 경기)', `${cur} 상위 예/아니오`, `${cur} 우리 예/아니오`], rows));
  md.push('');
}
md.push('## 규칙 단위 차이 (영향 추정 순)');
md.push('- 영향(판당) = 우리 판당 그 잎 턴 수 × (상위 비율 − 우리 비율) × (예 − 아니오의 결과 차이)를 잎마다 더한 값이다. 결과 차이는 상위끼리 행에서 잰다(dT). 괄호 안은 우리 행에서 잰 값(dO, 두 행동 모두 30행 이상인 잎만)이다.');
md.push('- 결과 단위: net10 = 10라운드 뒤 가족 길이 − 지금 길이 + 머리로 죽인 적 길이(칸). feedK = 떨어진 진주 중 20라운드 안에 우리 왕이 먹은 수(G 대리값). 모두 상관에서 나온 추정이다.');
const dirKo = r => r.dir === 'more' ? `더 자주 ${r.yes}` : `덜 ${r.yes}`;
md.push(mdTable(['순위', '결정', '상위처럼', '해당 잎', '우리 판당 턴', '영향 dT', '(영향 dO)', '단위'], DIV.O.rules.slice(0, 16).map((r, i) => [String(i + 1), `${r.spec} ${r.title}`, dirKo(r), r.leaves.join(','), fx(r.perGame, 1), fx(r.impT, 2), r.impOn ? fx(r.impO, 2) : '–', r.cur])));
md.push('');
md.push('## 잎 단위 차이 (|영향 dT| 순, 상위 20)');
md.push(mdTable(['순위', '결정', '잎', '조건', '상위', '승자/패자', '우리', '우리 판당', 'dT', 'dO', '영향 dT', '영향 dO'], DIV.O.leaves.slice(0, 20).map((d, i) => [String(i + 1), `${d.spec} ${d.yes}`, String(d.leaf), d.text, pct(d.pT, 1, 1), `${pct(d.pTW, 1, 0)}/${pct(d.pTL, 1, 0)}`, pct(d.pO, 1, 1), fx(d.perGame, 2), fx(d.dT), fx(d.dO), fx(d.impT, 2), fx(d.impO, 2)])));
md.push('');
for (const gr of GROUPS.filter(g => g.startsWith('C'))) {
  md.push(`### 후보 ${gr.slice(1)} (${[...setsOfGroup[gr]].join(', ')}): 규칙 단위 차이`);
  md.push(mdTable(['순위', '결정', '상위처럼', '후보 판당 턴', '영향 dT', '단위'], DIV[gr].rules.slice(0, 10).map((r, i) => [String(i + 1), `${r.spec}`, dirKo(r), fx(r.perGame, 1), fx(r.impT, 2), r.cur])));
  md.push('');
}
// descriptive tables
md.push('## 설명 표');
md.push('### 사망 원인 (팀·경기당, 마지막 행 기준)');
const causes = ['V', 'H', 'O', 'S', 'W', 'Aq', 'Ax', 'Ap', 'At', 'An'];
md.push(mdTable(['집단', '길이', ...causes], GROUPS.flatMap(gr => ['L6+', 'L<=5'].map(lb => [gname(gr), lb, ...causes.map(c => { const e = extra.get(`death|${gr}|${lb}|${c}`); return e.n ? fx(e.n / teamGames[gr], 2) : '–'; })]))));
md.push('- V = 적·아군 머리가 들어와 박힘, H = 우리가 머리로 박음, O = 남의 몸, S = 자기 몸, W = 해초, Aq = 불법 분열(SPLIT 1 등), Ax = 행동 없음(자해), Ap = 질주 비용 부족, At = 시간 초과, An = 행동 없음(그 밖).');
md.push('');
md.push('### 박혀 죽은 L≥6 드래곤의 마지막 결정 때 상태 (팀·경기당)');
const sts = ['unseen', 'noExp', 'someExp', 'allExp', 'inReach'];
md.push(mdTable(['집단', ...sts, '그중 노출 칸에서 끝냄'], GROUPS.map(gr => { let tot = 0, ex = 0; const cells = sts.map(st => { const e = extra.get(`deathV|${gr}|L6+|${st}`); tot += e.n; ex += e.s.endExp || 0; return e.n ? fx(e.n / teamGames[gr], 3) : '–'; }); return [gname(gr), ...cells, tot ? pct(ex, tot) : '–']; })));
md.push('- unseen: 적 머리가 시야에 없음. noExp: 짧은 적이 보이나 어느 한 걸음도 도달 안. someExp: 안전한 한 걸음 있음. allExp: 한 걸음 모두 노출. inReach: 이미 우리 머리가 도달 안.');
md.push('');
md.push('### 왕(팀 최장) 50라운드 창별 평균');
const kf = ['L', 'U', 'aDg', 'aN', 'eDg', 'eat10', 'eatS10', 'danger', 'sprint'];
md.push(mdTable(['창', '집단', 'n', ...kf, '비왕 kD'], [200, 250, 300, 350, 400, 450].flatMap(ph => GROUPS.filter(g => extra.get(`king|${g}|${ph}`).n).map(gr => [String(ph), gname(gr), fint(extra.get(`king|${gr}|${ph}`).n), ...kf.map(k => fx(extra.mean(`king|${gr}|${ph}`, k), 2)), fx(extra.mean(`nonking|${gr}|${ph}`, 'kD'), 1)]))));
md.push('- aDg: 가장 가까운 아군 머리까지 맨해튼 거리. eDg: 가장 가까운 적 머리. eat10: 다음 10라운드에 먹은 진주. eatS10: 그중 아군 사망으로 떨어진 진주. danger: 짧은 적이 우리 머리에 닿는 턴 비율. 비왕 kD: 왕이 아닌 드래곤과 왕 머리의 거리.');
md.push('');
md.push('### 자해 (빈 이웃이 있는데 자기 몸·해초·SPLIT 1·행동 없음) 창별 평균');
const sf = ['L', 'U', 'kRank', 'aDg', 'aLg', 'kD', 'aN', 'eN', 'drop', 'feedS', 'feedK', 'feedE'];
md.push(mdTable(['창', '집단', '판당', ...sf], ['r0-249', 'r250-349', 'r350-449', 'r450+'].flatMap(ph => GROUPS.filter(g => extra.get(`sk|${g}|${ph}`).n).map(gr => [ph, gname(gr), fx(extra.get(`sk|${gr}|${ph}`).w / teamGames[gr], 2), ...sf.map(k => fx(extra.mean(`sk|${gr}|${ph}`, k), 2))]))));
md.push('- drop: 떨어진 진주 수. feedS/feedK/feedE: 20라운드 안에 우리 팀/우리 왕/적이 먹은 수.');
md.push('');
md.push('### 분열 확률(턴당 %)과 자식 길이');
const lbs = ['4', '5', '6-7', '8-11', '12+'], phs = ['r0-99', 'r100-249', 'r250-399', 'r400+'];
md.push(mdTable(['길이', '집단', '전체', ...phs, '자식 2', 'stub(부모 ≤3)', '중간'], lbs.flatMap(lb => GROUPS.filter(g => extra.get(`split|${g}|${lb}`).n).map(gr => {
  const tot = extra.get(`child|${gr}|${lb}`).w;
  return [lb, gname(gr), fx(100 * extra.mean(`split|${gr}|${lb}`, 'split'), 2), ...phs.map(ph => fx(100 * extra.mean(`split|${gr}|${lb}|${ph}`, 'split'), 1)),
    ...['c2', 'stub', 'mid'].map(k => { const e = extra.get(`child|${gr}|${lb}|${k}`); return e.w ? `${pct(e.w, tot, 0)} (자식 10R 생존 ${fx(extra.mean(`child|${gr}|${lb}|${k}`, 'cAl10'), 2)})` : '–'; })];
}))));
md.push('');
md.push('### 분열 확률(턴당 %): 적 머리가 보일 때와 아닐 때, 팀 수별');
md.push(mdTable(['길이', '집단', '적 없음', '적 보임', 'U1-2', 'U3-5', 'U6-15', 'U16-31', 'U32+'], ['4', '5', '6-7', '8-11', '12+'].flatMap(lb => GROUPS.filter(g => extra.get(`split|${g}|${lb}`).n).map(gr => [lb, gname(gr),
  ...[0, 1].map(e => fx(100 * extra.mean(`splitE|${gr}|${lb}|${e}`, 'split'), 1)), ...['U1-2', 'U3-5', 'U6-15', 'U16-31', 'U32+'].map(u => { const e = extra.get(`splitU|${gr}|${lb}|${u}`); return e.n >= 30 ? fx(100 * extra.mean(`splitU|${gr}|${lb}|${u}`, 'split'), 1) : '–'; })]))));
md.push('');
md.push('### 자해 방식 (판당)');
const hows = ['SB', 'S', 'W', 'Aq', 'Ax'];
md.push(mdTable(['집단', '자기 목으로(SB)', '자기 몸 그 밖(S)', '해초(W)', 'SPLIT 1 등(Aq)', '행동 없음(Ax)'], GROUPS.map(gr => [gname(gr), ...hows.map(h => { const e = extra.get(`skhow|${gr}|${h}`); return e.w ? fx(e.w / teamGames[gr], 2) : '–'; })])));
md.push('');
md.push('### 길이별 먹이 (턴당 먹은 진주, 다음 10라운드 먹이)');
const elb = ['2', '3-4', '5-9', '10-19', '20+'];
md.push(mdTable(['집단', ...elb.map(l => 'L' + l)], GROUPS.map(gr => [gname(gr), ...elb.map(l => { const k = `eatL|${gr}|${l}`; const e = extra.get(k); return e.n ? `${fx(extra.mean(k, 'ate'), 3)} / ${fx(extra.mean(k, 'eat10'), 2)} (턴 ${fint(e.w / teamGames[gr])})` : '–'; })])));
md.push('- 칸: 턴당 먹은 진주 / 다음 10라운드에 먹은 진주 (그 길이 턴의 판당 수).');
md.push('');
md.push('### 경기 결과 (팀·경기 단위)');
md.push(mdTable(['집단', '지도', '팀·경기', '승', '전멸', '전멸 라운드 평균', '끝 최장 평균', '끝 수 평균'], GROUPS.flatMap(gr => ['E', 'R'].map(m => { const k = `game|${gr}|${m}`; const e = extra.get(k); return e.n ? [gname(gr), m === 'E' ? '전멸형' : '500형', String(e.n), pct(e.s.won, e.n, 0), pct(e.s.gone, e.n, 0), fx(extra.mean(k, 'goneR'), 0), fx(extra.mean(k, 'longest'), 1), fx(extra.mean(k, 'units'), 1)] : null; }).filter(Boolean))));
md.push('');
md.push('### 알려진 수치와 대조 (상위끼리, 표본 가중)');
{
  const gr = 'T';
  const adj = ['small', 'mid', 'big'].map(k => { const e = extra.get(`adj|${gr}|${k}`); return `${k === 'small' ? '≤4' : k === 'mid' ? '5–9' : '≥10'}: ${fint(e.w)}턴 중 ${pct(e.s.ram, e.w)}`; }).join(', ');
  const sk = extra.get(`split|${gr}|4`); const s22 = extra.get(`splitkind|${gr}|4to2+2`).w, sAll = s22 + extra.get(`splitkind|${gr}|other`).w;
  let tot = 0; const hist = []; for (let r = 0; r < 500; r++) { const e = extra.get(`skr|${gr}|${r}`); hist.push(e.w); tot += e.w; }
  let acc = 0, med = -1; for (let r = 0; r < 500 && med < 0; r++) { acc += hist[r]; if (acc >= tot / 2) med = r; }
  md.push(`- 적 머리가 바로 옆일 때 한 걸음으로 박는 비율: ${adj}. (top-fragments.md: 36.2%, 7.0%, 6.5%)`);
  md.push(`- 분열 중 4 → 2+2: ${pct(s22, sAll)}. (top-summary: 68%)`);
  md.push(`- 빈 이웃이 있는데 스스로 죽음: 팀·경기당 ${fx(tot / teamGames[gr], 1)}회, 라운드 중앙값 ${med}. (top-summary: 30.9회, 365–392)`);
  void sk;
}
md.push('');
md.push('### 좁은 방(1–5칸)의 길이 ≥8 드래곤: 지도별 분열 (통로 요새 확인)');
const mapsSeen = [...new Set([...extra.m.keys()].filter(k => k.startsWith('loopmap|')).map(k => k.split('|')[2]))].sort();
md.push(mdTable(['지도', ...['T', 'O'].map(g => gname(g) + ' 판당 턴 / 분열')], mapsSeen.map(mp => [mp, ...['T', 'O'].map(gr => { const k = `loopmap|${gr}|${mp}`; const e = extra.get(k); return e.n ? `${fx(e.w / Math.max(1, extra.get(`gamemap|${gr}|${mp}`).n), 1)} / ${fx(100 * extra.mean(k, 'split'), 1)}%` : '–'; })])));
md.push('- 판당 턴은 그 지도의 팀·경기당 턴 수다.');
md.push(mdTable(['묶음', ...GROUPS.slice(0, 5).map(gname)], ['corr', 'other'].map(c => [c === 'corr' ? 'Autarky+PD' : '나머지 8개', ...GROUPS.slice(0, 5).map(gr => { const k = `loopcorr|${gr}|${c}`; const e = extra.get(k); return e.n ? `턴 ${fint(e.w / teamGames[gr])}, 분열 ${fx(100 * extra.mean(k, 'split'), 1)}%, net10 ${fx(extra.mean(k, 'net10'))}` : '–'; })])));
md.push('');
md.push('### 팀 드래곤 수 (팀·경기 평균, 끝난 팀은 0)');
md.push(mdTable(['집단', '지도', 'r10', 'r25', 'r50', 'r100'], GROUPS.flatMap(gr => ['E', 'R'].map(m => [gname(gr), m === 'E' ? '전멸형' : '500형', ...[10, 25, 50, 100].map(r => fx(extra.mean(`unitsAt|${gr}|${m}|${r}`, 'U'), 1))]))));
md.push('');
md.push('### 진주 쪽으로 가는 비율: 진주가 적 도달 안(dang), 적이 같거나 더 가까움(contest), 그 밖(free)');
md.push(mdTable(['길이', '진주', ...GROUPS.slice(0, 5).map(gname)], ['s', 'm', 'l'].flatMap(sz => ['free', 'contest', 'dang'].map(dz => [sz === 's' ? '≤4' : sz === 'm' ? '5–9' : '≥10', dz, ...GROUPS.slice(0, 5).map(gr => { const k = `pearlDz|${gr}|${sz}|${dz}`; const e = extra.get(k); return e.n >= 30 ? `${fx(100 * extra.mean(k, 'tow'), 1)}% (n ${fint(e.n)})` : '–'; })]))));
md.push('');
md.push('### 판당 총량');
md.push(mdTable(['집단', '드래곤 턴', '평균 길이', '먹은 진주', '포털 통과', '질주율(적 보임)', '질주율(적 없음)'], GROUPS.map(gr => [gname(gr), fint(extra.get(`turns|${gr}`).w / teamGames[gr]), fx(extra.mean(`turns|${gr}`, 'L'), 2), fx(extra.get(`eat|${gr}`).w / teamGames[gr], 1), fx(extra.get(`portal|${gr}`).w / teamGames[gr], 1),
  pct(extra.get(`sprint|${gr}|e`).w, extra.get(`moves|${gr}|e`).w, 2), pct(extra.get(`sprint|${gr}|n`).w, extra.get(`moves|${gr}|n`).w, 2)])));
md.push('');
fs.writeFileSync(OUT + '.md', md.join('\n') + '\n');
console.error(`wrote ${path.relative(Lb.ROOT, OUT)}.json and .md in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
