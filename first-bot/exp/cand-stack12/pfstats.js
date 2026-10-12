// cand-stack12 pf (research/experiments/cand-stack12.md): per-game head-count, split-speed and intake numbers of the intake-gap study
// (research/observations/intake-gap.md sections 1-3, 6, 13), computed from one intake-gap record (exp/intake-gap/extract.js analyse() output
// or a line of .cache/intake-gap/*.jsonl) with the study's own team view (exp/intake-gap/aggregate.js teamView), and pooled the study's way.
// Used by exp/cand-stack12/baseline.js (online baselines from the cache) and tools/mech_check.js (the stack12 section, fresh replays).
'use strict';
const path = require('path');
const AG = require(path.join(__dirname, '..', 'intake-gap', 'aggregate.js'));

const NB = 50, NPH = 6;
const PHB = [[0, 5], [5, 10], [10, 25], [25, 35], [35, 45], [45, 50]];   // 10-round bins of each phase (aggregate.js)
const ORIGS = ['csplit', 'lsplit', 'floor', 'kcap', 'frag', 'bsplit', 'split', 'escsplit', 'escsplit2', 'unl']; // extract.js ORIGS
const ESC = new Set([ORIGS.indexOf('escsplit'), ORIGS.indexOf('escsplit2')]);
// the pf maps (bot pfMapOn) and the study's map kinds
const PF_MAPS = new Set(['Slithery Fight', 'Schooltime', 'Trauma', 'Default', 'Devil', 'Queen Of Spades', 'Trophy']);
const PF_500 = new Set(['Slithery Fight', 'Schooltime', 'Trauma']);
const PF_ELIM = new Set(['Default', 'Devil', 'Queen Of Spades', 'Trophy']);
const R500 = new Set(['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma']);
// the bot's pf target table (plan.cpp PF_TAB, capped at 64 - PF_HEADROOM = 56): top winners' mean r100 count per layout
const PF_TAB = { 'Slithery Fight': { f: 57, a: 60, b: 54 }, 'Schooltime': { f: 30, a: 44, b: 16 }, 'Trauma': { f: 18, a: 18, b: 18 }, 'Default': { f: 19, a: 19, b: 19 },
  'Devil': { f: 26, a: 29, b: 23 }, 'Queen Of Spades': { f: 13, a: 13, b: 12 }, 'Trophy': { f: 31, a: 31, b: 31 } };
const PF_CAP = 56;
const pfTargetOf = (map, layout) => { const r = PF_TAB[map]; if (!r) return null; return Math.min(PF_CAP, layout === 'a' ? r.a : layout === 'b' ? r.b : r.f); };

// one team-game: g = intake-gap record (needs map, kind, us or me), me = 0 (team A) / 1 (team B)
function gameStats(g, me) {
  const v = AG.teamView(g, me);
  const sumB = (arr, ph) => { let s = 0; for (let b = PHB[ph][0]; b < PHB[ph][1]; b++) s += arr[b] || 0; return s; };
  const l4 = t => [0, 1, 2].map(ph => v.hrLc[t][ph][2] + v.hrLc[t][ph][3] + v.hrLc[t][ph][4] + v.hrLc[t][ph][5]);
  const bNE = [0, 1, 2].map(ph => { if (!v.org) return null; let s = 0; for (let og = 0; og < ORIGS.length; og++) if (!ESC.has(og)) s += sumB(v.org.slice(og * NB, og * NB + NB), ph); return s; });
  const eatPh = t => [...Array(NPH)].map((_, ph) => v.eat[t][ph].reduce((s, a) => s + a[0] + a[1] + a[2], 0));
  const race = [...Array(NPH)].map((_, ph) => ({ NU: v.race[ph][0].reduce((s, x) => s + x, 0), NO: v.race[ph][2].reduce((s, x) => s + x, 0) }));
  const capMine = [0, 1, 2].map(r3 => v.att.reduce((s, ph) => s + ph[1][r3], 0)); // my territory's expected attempts by race (me nearer / tie / op nearer)
  const at = (arr, i) => arr && arr[i] !== undefined ? arr[i] : null;
  const endIdx = Math.min(50, Math.max(0, Math.floor(((g.rounds || 500) - 1) / 10) + 1));
  const oursElim = g.endReason === 'teamEliminated' && g.winner && g.winner !== (me ? 'B' : 'A') ? 1 : 0;
  return {
    map: g.map, kind: g.kind || (R500.has(g.map) ? 'r500' : 'elim'), variant: g.variant, rounds: g.rounds,
    units: [1, 5, 10, 25].map(i => at(v.units[0], i)), unitsO: [1, 5, 10, 25].map(i => at(v.units[1], i)),
    l4u: l4(0), l4o: l4(1), bNE, bU: [0, 1, 2].map(ph => v.birthPh[0][ph]), bO: [0, 1, 2].map(ph => v.birthPh[1][ph]),
    natU: [...Array(NPH)].map((_, ph) => v.nat[0][ph]), natO: [...Array(NPH)].map((_, ph) => v.nat[1][ph]),
    hrU: v.hr[0].slice(), hrO: v.hr[1].slice(), eatU: eatPh(0), eatO: eatPh(1), race, capMine,
    kingEnd: at(v.king[0], endIdx), kingEndO: at(v.king[1], endIdx), totalEnd: at(v.total[0], endIdx), elim: oursElim,
  };
}

const mean = xs => { const a = xs.filter(x => x !== null && x !== undefined); return a.length ? a.reduce((s, x) => s + x, 0) / a.length : null; };
// pooled numbers of a list of gameStats (the study's conventions: counts are per-game means, rates pooled ratios, view B per phase on
// pooled head-rounds and eats, the race share per team-game)
function pool(S) {
  const n = S.length;
  if (!n) return { n: 0 };
  const sum = f => S.reduce((s, x) => s + (f(x) || 0), 0);
  const speed = ph => { const b = sum(x => x.bNE[ph]), h = sum(x => x.l4u[ph]); return h ? b / h : null; };
  const speedO = ph => { const b = sum(x => x.bO[ph]), h = sum(x => x.l4o[ph]); return h ? b / h : null; };
  const speed99 = (() => { const b = sum(x => x.bNE[0] + x.bNE[1]), h = sum(x => x.l4u[0] + x.l4u[1]); return h ? b / h : null; })();
  const speed99O = (() => { const b = sum(x => x.bO[0] + x.bO[1]), h = sum(x => x.l4o[0] + x.l4o[1]); return h ? b / h : null; })();
  // view B heads term per phase: (H_O - H_U) (r_U + r_O) / 2 per team-game, on pooled head-rounds and natural eats
  const vb = [...Array(NPH)].map((_, ph) => {
    const HU = sum(x => x.hrU[ph]), HO = sum(x => x.hrO[ph]), IU = sum(x => x.eatU[ph]), IO = sum(x => x.eatO[ph]);
    const rU = HU ? IU / HU : 0, rO = HO ? IO / HO : 0;
    return { heads: (HO - HU) * (rU + rO) / 2 / n, rate: (HO + HU) / 2 * (rO - rU) / n, gap: (IO - IU) / n };
  });
  const cap = [0, 1, 2].map(r => sum(x => x.capMine[r]));
  return {
    n,
    units: [0, 1, 2, 3].map(i => mean(S.map(x => x.units[i]))), unitsO: [0, 1, 2, 3].map(i => mean(S.map(x => x.unitsO[i]))),
    speed: [speed(0), speed(1), speed(2)], speedO: [speedO(0), speedO(1), speedO(2)], speed99, speed99O,
    births99: mean(S.map(x => x.bNE[0] + x.bNE[1])), l4hr99: mean(S.map(x => x.l4u[0] + x.l4u[1])),
    nat99: mean(S.map(x => x.natU[0] + x.natU[1])), nat99O: mean(S.map(x => x.natO[0] + x.natO[1])),
    natPh: [...Array(NPH)].map((_, ph) => mean(S.map(x => x.natU[ph]))), natPhO: [...Array(NPH)].map((_, ph) => mean(S.map(x => x.natO[ph]))),
    nat: mean(S.map(x => x.natU.reduce((s, y) => s + y, 0))), natO: mean(S.map(x => x.natO.reduce((s, y) => s + y, 0))),
    heads249: vb[0].heads + vb[1].heads + vb[2].heads, headsAll: vb.reduce((s, r) => s + r.heads, 0), rateAll: vb.reduce((s, r) => s + r.rate, 0),
    race249: sum(x => x.race[0].NO - x.race[0].NU + x.race[1].NO - x.race[1].NU + x.race[2].NO - x.race[2].NU) / n,
    terrNear: cap[0] + cap[1] + cap[2] > 0 ? cap[2] / (cap[0] + cap[1] + cap[2]) : null,
    kingEnd: mean(S.map(x => x.kingEnd)), kingEndO: mean(S.map(x => x.kingEndO)), totalEnd: mean(S.map(x => x.totalEnd)),
    elim: mean(S.map(x => x.elim)),
  };
}

module.exports = { gameStats, pool, pfTargetOf, PF_MAPS, PF_500, PF_ELIM, R500, PF_TAB, PF_CAP };
