#!/usr/bin/env node
// Tables for research/observations/supply-chain.md from the aggregate (exp/supply-chain/aggregate.js).
// usage (repository root): node exp/supply-chain/report.js [--agg .cache/supply-chain/agg.json] [--out exp/supply-chain/report.md]
// Every rate is a ratio of sums over team-games; "per game" = per team-game in progress in that phase (the game had reached
// the phase's first round). Phases: p0 r0-99, p1 r100-249, p2 r250-349, p3 r350-449, p4 r450-499.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const AGG = JSON.parse(fs.readFileSync(path.resolve(ROOT, opt('agg', '.cache/supply-chain/agg.json')), 'utf8'));
const acc = AGG.acc;
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const ELIM = ['Devil', 'Trophy', 'Prisoners Dilemma', 'Prisoners Dilemma (10)', 'Queen Of Spades', 'Default'];
const KINDS = { r500: R500, elim: ELIM };
const GROUPS = ['TW', 'TL', 'T7W', 'X', 'g4r4', 'merge2', 'stack1', 'stack2', 'stack3', 'stack4', 'stack5', 'stack6', 'swarm8', 'px9d', 'px8', 'pxking', 'avoid6', 'portal1'];
const MAIN = ['TW', 'TL', 'X', 'merge2', 'stack1', 'stack2', 'stack3', 'stack4', 'stack5', 'stack6'].filter(g => acc[g]);
const OLD = ['g4r4', 'swarm8', 'px9d', 'px8', 'pxking', 'avoid6', 'portal1'].filter(g => acc[g]);
const PH = [[0, 10], [10, 25], [25, 35], [35, 45], [45, 50]];
const PHN = ['r0-99', 'r100-249', 'r250-349', 'r350-449', 'r450-499'];
const out = [];
const P = s => out.push(s);
const f1 = v => v === null || v === undefined || !isFinite(v) ? '–' : (Math.round(v * 10) / 10).toFixed(1);
const f2 = v => v === null || v === undefined || !isFinite(v) ? '–' : (Math.round(v * 100) / 100).toFixed(2);
const pc = (a, b) => b > 0 ? Math.round(100 * a / b) + '%' : '–';
const table = (head, rows) => { P('| ' + head.join(' | ') + ' |'); P('|' + head.map((_, i) => i === 0 ? '---' : '---:').join('|') + '|'); for (const r of rows) P('| ' + r.join(' | ') + ' |'); P(''); };

// merge nodes of a group over maps
function merged(group, maps) {
  const A = acc[group]; if (!A) return null;
  const m = { n: 0, nPh: [0, 0, 0, 0, 0], nBin: new Array(50).fill(0), win: 0, b: {}, ep: {}, tag: {}, tagD: {}, dr: {}, sp: {}, dt: {}, cp: {}, h: {}, pc: {}, ph: {} };
  const addArr = (o, k, a) => { const t = o[k] || (o[k] = new Array(a.length).fill(0)); for (let i = 0; i < a.length; i++) t[i] += a[i] || 0; };
  for (const mp of maps) {
    const x = A[mp]; if (!x) continue;
    m.n += x.n; m.win += x.win; for (let i = 0; i < 5; i++) m.nPh[i] += x.nPh[i]; for (let i = 0; i < 50; i++) m.nBin[i] += x.nBin[i];
    for (const s of ['b', 'ep', 'tag', 'tagD', 'dr', 'sp', 'dt', 'h', 'pc']) for (const [k, v] of Object.entries(x[s])) addArr(m[s], k, v);
    for (const [k, v] of Object.entries(x.cp)) { const c = m.cp[k] || (m.cp[k] = { s: new Array(50).fill(0), c: new Array(50).fill(0) }); for (let i = 0; i < 50; i++) { c.s[i] += v.s[i]; c.c[i] += v.c[i]; } }
    for (const [k, v] of Object.entries(x.ph)) { const t = m.ph[k] || (m.ph[k] = {}); for (const [h, a] of Object.entries(v)) addArr(t, h, a); }
  }
  return m.n ? m : null;
}
const bsum = (m, name, p0, p1) => { const a = m.b[name]; if (!a) return 0; let s = 0; for (let i = PH[p0][0]; i < PH[p1][1]; i++) s += a[i]; return s; };
const tsum = (m, name, p0, p1) => { const a = m.tag[name]; if (!a) return 0; let s = 0; for (let i = PH[p0][0]; i < PH[p1][1]; i++) s += a[i]; return s; };
const games = (m, p) => m.nPh[p];
const epv = (m, e, p0, p1, i) => { const a = m.ep[e]; if (!a) return 0; let s = 0; for (let p = p0; p <= p1; p++) s += a[p * 9 + i]; return s; };

const M = {}; for (const g of GROUPS) { M[g] = {}; for (const [k, maps] of Object.entries(KINDS)) M[g][k] = merged(g, maps); }
for (const g of GROUPS) M[g].all = merged(g, [...R500, ...ELIM]);

P(`# supply-chain report (generated ${new Date().toISOString()})`);
P(`- aggregate: ${AGG.at}; files ${JSON.stringify(AGG.counts)}`);
P(`- excluded top games: ${JSON.stringify(AGG.excluded)}; reconstruction checks summed: ${JSON.stringify(AGG.chkSum)}`);
P('');
P('## 0. Population (team-games; in progress per phase)');
{
  const rows = [];
  for (const g of GROUPS) for (const k of ['r500', 'elim']) { const m = M[g][k]; if (!m) continue; rows.push([g, k, m.n, m.nPh.join(' / '), pc(m.win, m.n)]); }
  table(['group', 'kind', 'team-games', 'in progress p0/p1/p2/p3/p4', 'won'], rows);
}

// ---------------------------------------------------------------------------------------------------------------
// Q1 conv
function convRows(k, e, phs) {
  const rows = [];
  for (const g of [...MAIN, ...OLD]) {
    const m = M[g][k]; if (!m) continue;
    for (const [p0, p1] of phs) {
      const n = games(m, p0);
      const turnsP = bsum(m, 'turnsP', p0, p1), st = bsum(m, e, p0, p1);
      const eps = epv(m, e, p0, p1, 0), fired = epv(m, e, p0, p1, 1), tagF = epv(m, e, p0, p1, 2), ok = epv(m, e, p0, p1, 6), okB = epv(m, e, p0, p1, 7);
      const left = epv(m, e, p0, p1, 3), died = epv(m, e, p0, p1, 4), end = epv(m, e, p0, p1, 5);
      const rr = bsum(m, e === 'cs' || e === 'csE' ? 'csR' : 'fsR', p0, p1), rounds = bsum(m, 'rounds', p0, p1);
      rows.push([g, p0 === p1 ? PHN[p0] : PHN[p0] + '…' + PHN[p1], n, f1(st / n), pc(st, turnsP), f1(eps / n), pc(rr, rounds), pc(fired, eps), g.startsWith('T') || g === 'X' ? '–' : pc(tagF, eps), pc(ok, fired), pc(okB, fired), f2(fired / n), f2(ok / n), pc(left, eps), pc(died, eps), pc(end, eps)]);
    }
  }
  return rows;
}
const HEAD_EP = ['group', 'phase', 'team-games', 'state turns/game', 'of piece turns', 'episodes/game', 'rounds with state', 'fired (sac)', 'our label', 'ok | fired', 'ok big | fired', 'fired/game', 'ok/game', 'left', 'died other', 'game end'];
for (const k of ['r500', 'elim']) {
  P(`## 1.1 conv state (cs), ${k}`);
  P('cs = piece 2-4 with an ally >= 8 (and >= L+4) in view within path 3, no enemy head in view. fired = sacrifice at a turn in the state; ok = >= half of its pearls to own team and none to the opponent; ok big = >= half to own dragons >= 8.');
  table(HEAD_EP, convRows(k, 'cs', [[2, 4], [2, 2], [3, 3], [4, 4], [0, 1]]));
  P(`### csE (the bot's other conditions too: r >= 300, units >= 3, not young, not a fresh stub), ${k}`);
  table(HEAD_EP, convRows(k, 'csE', [[2, 4]]));
  P(`### conv supply components, ${k} (per game, r250-499): piece turns, csGeo with enemy in view (csV), near miss (big ally within Manhattan 6 but not in path 3: csN)`);
  const rows = [];
  for (const g of [...MAIN, ...OLD]) { const m = M[g][k]; if (!m) continue; const n = games(m, 2); rows.push([g, n, f1(bsum(m, 'turnsP', 2, 4) / n), f1(bsum(m, 'cs', 2, 4) / n), f1(bsum(m, 'csV', 2, 4) / n), f1(bsum(m, 'csN', 2, 4) / n), f1(bsum(m, 'turnsB', 2, 4) / n), f1(bsum(m, 'sacP', 2, 4) / n), f1(bsum(m, 'sacCs', 2, 4) / n), pc(bsum(m, 'sacCs', 2, 4), bsum(m, 'sacP', 2, 4))]); }
  table(['group', 'team-games', 'piece turns', 'cs turns', 'csV turns', 'csN turns', 'big turns', 'piece sacs', 'sacs in cs', 'share of piece sacs in cs'], rows);
}
// our labels vs the state
{
  P('## 1.2 our labels against the replay state (all maps)');
  const rows = [];
  for (const g of ['merge2', 'stack1', 'stack2', 'stack3', 'stack4', 'stack5', 'stack6', 'g4r4']) {
    const m = M[g].all; if (!m) continue;
    const T = (k) => tsum(m, k, 0, 4);
    rows.push([g, m.n, T('conv'), pc(T('convCs'), T('conv')), pc(T('convCsE'), T('conv')), T('convOutLen'), T('convOutGeo'), T('feed'), pc(T('feedFs'), T('feed')), pc(T('feedFsK'), T('feed')), T('g'), pc(T('gGs'), T('g')), T('grabT'), T('grabNat'), T('grabGone'), T('F')]);
  }
  table(['bot', 'games', 'conv labels', 'in cs', 'in csE', 'out: L>4', 'out: geometry', 'feed labels', 'in fs', 'in fsK', 'g turns', 'in gs', 'grab label turns', 'grab: natural', 'grab: gone', 'F turns'], rows);
  P('### labelled deaths: [n, in state, drops, own, own big, opponent, target ate >= 1, ok] summed over phases');
  const rows2 = [];
  for (const g of ['merge2', 'stack1', 'stack2', 'stack3', 'stack4', 'stack5', 'stack6', 'g4r4']) {
    const m = M[g].all; if (!m) continue;
    for (const kind of ['conv', 'feed']) {
      const s = [0, 0, 0, 0, 0, 0, 0, 0]; for (let p = 0; p < 5; p++) { const a = m.tagD[kind + 'Death|' + p]; if (a) for (let i = 0; i < 8; i++) s[i] += a[i]; }
      if (!s[0]) continue;
      rows2.push([g, kind, s[0], pc(s[1], s[0]), s[2], pc(s[3], s[2]), pc(s[4], s[2]), pc(s[5], s[2]), pc(s[6], s[0]), pc(s[7], s[0])]);
    }
  }
  table(['bot', 'label', 'deaths', 'in state', 'pearls', 'own', 'own big', 'opponent', 'target ate', 'ok'], rows2);
}

// ---------------------------------------------------------------------------------------------------------------
// Q1 feed / gather
for (const k of ['r500', 'elim']) {
  P(`## 1.3 feed state, ${k}`);
  P('fs = r >= 250, not the team longest, a longer ally in view within path 5, no enemy head within Manhattan 4, units >= 3. fsK = the king within path 5. fsG = units >= 4, length >= 4.');
  table(HEAD_EP, convRows(k, 'fs', [[2, 4], [2, 2], [3, 3], [4, 4]]));
  P(`### fsK, ${k}`); table(HEAD_EP, convRows(k, 'fsK', [[2, 4], [3, 3], [4, 4]]));
  P(`### fsG, ${k}`); table(HEAD_EP, convRows(k, 'fsG', [[2, 4], [3, 3], [4, 4]]));
  P(`## 1.4 gather state (r >= 340, not the king, length >= 4, units >= 4), ${k}`);
  const rows = [];
  for (const g of [...MAIN, ...OLD]) {
    const m = M[g][k]; if (!m) continue; const n = games(m, 3);
    const gs = bsum(m, 'gs', 3, 4), d = [0, 1, 2, 3, 4].map(i => bsum(m, 'gsK' + i, 3, 4));
    rows.push([g, n, f1(gs / n), ...d.map(v => pc(v, gs)), pc(bsum(m, 'gsApp', 3, 4), bsum(m, 'gsPrev', 3, 4)), f1(bsum(m, 'turnsM', 3, 4) / n), f1(bsum(m, 'turnsB', 3, 4) / n)]);
  }
  table(['group', 'team-games (p3)', 'gs turns/game', 'to king <=3', '4-5', '6-8', '9-15', '16+', 'approached', 'mid turns/game', 'big turns/game'], rows);
}

// ---------------------------------------------------------------------------------------------------------------
// Q1 grab: death drops by the team that sees them
function drSum(m, filt) { const s = new Array(11).fill(0); for (const [k, v] of Object.entries(m.dr)) { const [ph, orig, cg, w6, view, cont] = k.split('|').map(Number); if (!filt(ph, orig, cg, w6, view, cont)) continue; for (let i = 0; i < 11; i++) s[i] += v[i]; } return s; }
for (const k of ['r500', 'elim']) {
  P(`## 1.5 grab: death drops within 6 steps of the team's heads in their first 6 rounds, ${k}`);
  P('columns: drops within 6 per game; of them eaten by the team / by the opponent / nobody; eaten by own piece / mid / big; mean delay (rounds) to our eat; for our bots the share our grab labels targeted and the share of targeted eaten by us.');
  for (const [pname, pf] of [['all phases', () => true], ['r0-249', ph => ph <= 1], ['r250-499', ph => ph >= 2]]) {
    P(`### ${pname}`);
    const rows = [];
    for (const g of [...MAIN, ...OLD]) {
      const m = M[g][k]; if (!m) continue; const n = pname === 'r250-499' ? games(m, 2) : m.n;
      for (const [oname, of] of [['own deaths', o => o === 0], ['enemy deaths', o => o === 1]]) {
        const s = drSum(m, (ph, o, cg, w6) => pf(ph) && of(o) && w6 === 1), a = drSum(m, (ph, o) => pf(ph) && of(o));
        const v = drSum(m, (ph, o, cg, w6, view) => pf(ph) && of(o) && w6 === 1 && view === 1), c = drSum(m, (ph, o, cg, w6, view, cont) => pf(ph) && of(o) && w6 === 1 && cont === 1);
        rows.push([g, oname, f1(a[0] / n), f1(s[0] / n), pc(s[1], s[0]), pc(s[2], s[0]), pc(s[3], s[0]), pc(s[4], s[1]), pc(s[5], s[1]), pc(s[6], s[1]), f1(s[7] / Math.max(1, s[1])), pc(v[0], s[0]), pc(v[1], v[0]), pc(c[0], s[0]), pc(c[1], c[0]), g.startsWith('T') || g === 'X' ? '–' : pc(s[8], s[0]), g.startsWith('T') || g === 'X' ? '–' : pc(s[9], s[8])]);
      }
    }
    table(['group', 'origin', 'all drops/game', 'within 6/game', 'eaten own', 'opponent', 'nobody', 'by piece', 'by mid', 'by big', 'delay', 'in view', 'own | view', 'contested', 'own | contested', 'grab labelled', 'own | labelled'], rows);
  }
  P(`### drops within 6 by cause of the death (r250-499), ${k}`);
  const rows = [];
  for (const g of MAIN) {
    const m = M[g][k]; if (!m) continue; const n = games(m, 2);
    for (const [cn, ci] of [['sac', 0], ['trap', 1], ['head-on', 2], ['other', 3]]) for (const [on, oi] of [['own', 0], ['enemy', 1]]) {
      const s = drSum(m, (ph, o, cg, w6) => ph >= 2 && o === oi && cg === ci && w6 === 1); if (!s[0]) continue;
      rows.push([g, on + ' ' + cn, f1(s[0] / n), pc(s[1], s[0]), pc(s[2], s[0]), pc(s[6], s[1])]);
    }
  }
  table(['group', 'death', 'within 6/game', 'eaten own', 'opponent', 'own by big'], rows);
}

// ---------------------------------------------------------------------------------------------------------------
// elite link: deaths of pieces and who eats their drops
function dtSum(m, filt) { const s = new Array(9).fill(0); for (const [k, v] of Object.entries(m.dt)) { const [ph, cause, lc, near, mech] = k.split('|'); if (!filt(+ph, +cause, +lc, near, mech || 'o')) continue; for (let i = 0; i < 9; i++) s[i] += v[i]; } return s; }
for (const k of ['r500', 'elim']) {
  P(`## 1.6 deaths of pieces (<= 4) and where their pearls go, ${k} (per game by phase group)`);
  P('near = the nearest living own head within Manhattan 3 at the death: 0 none, S shorter than 8, B >= 8. columns: deaths/game, length/game, pearls/game, eaten own / own piece / own mid / own big / opponent (shares of pearls).');
  for (const [pname, p0, p1] of [['r0-249', 0, 1], ['r250-499', 2, 4]]) {
    P(`### ${pname}`);
    const rows = [];
    for (const g of MAIN) {
      const m = M[g][k]; if (!m) continue; const n = games(m, p0);
      for (const [cn, ci] of [['sac', 0], ['trap', 1], ['rammed', 2], ['ram', 3], ['allyHead', 5]]) for (const near of ['0', 'S', 'B']) for (const [mn, mf] of [['', mh => mh !== 's'], [' stub', mh => mh === 's']]) {
        const s = dtSum(m, (ph, c, lc, nr, mh) => ph >= p0 && ph <= p1 && c === ci && lc === 0 && nr === near && mf(mh)); if (!s[0]) continue;
        rows.push([g, cn + '|' + near + mn, f2(s[0] / n), f1(s[1] / n), f1(s[2] / n), pc(s[3], s[2]), pc(s[4], s[2]), pc(s[5], s[2]), pc(s[6], s[2]), pc(s[7], s[2])]);
      }
    }
    table(['group', 'cause|near', 'deaths/game', 'length/game', 'pearls/game', 'own', 'own piece', 'own mid', 'own big', 'opponent'], rows);
  }
}

// ---------------------------------------------------------------------------------------------------------------
// Q2 pieces
const CLS = { 1: 'csplit', 2: 'frag', 3: 'bsp', 4: 'split', 5: 'escape-split', 6: 'esc-split', 7: 'pocket', 9: 'unlabelled', 10: 'parent 4', 11: 'parent 5-7', 12: 'parent 8+', all: 'all' };
const ENDN = ['alive', 'sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprint'];
const hmed = (h, edges) => { if (!h) return '–'; const n = h.reduce((a, b) => a + b, 0); let c = 0; for (let i = 0; i < h.length; i++) { c += h[i]; if (c * 2 >= n) return edges[i]; } return '–'; };
const LIFE_E = ['0', '1-4', '5-9', '10-19', '20-49', '50-99', '100-199', '200+'];
function pieceRow(g, k, key, n) {
  const m = M[g][k]; if (!m) return null; const v = m.pc[key]; if (!v || !v[0]) return null; const h = m.ph[key] || {};
  const N = v[0];
  return [g, CLS[key.split('|')[1]] || key, N, f1(N / n), f1(v[1] / N), hmed(h.life, LIFE_E), f1(v[2] / N), f2(v[3] / N), pc(v[4], N), pc(v[5], N), pc(v[14], v[13]), pc(v[15], v[13]),
    ...[0, 1, 2, 3, 4, 6].map(e => pc(v[16 + e], N)), pc(v[28], v[27]), pc(v[29], v[27]), pc(v[30], v[27]), f2(v[34] / N), f2(v[35] / N), f2(v[36] / N), pc(v[37], v[36])];
}
const HEAD_P = ['group', 'class', 'pieces', 'per game', 'life mean', 'life median', 'steps', 'natural eaten', 'ate <=30r', 'alive +30', 'own terr turns', 'enemy terr turns', 'end alive', 'sac', 'trap', 'rammed', 'ram', 'allyHead', 'drops own', 'drops own big', 'drops opp', 'net', 'new mass', 'claimed spawns <=30r', 'claimed eaten'];
for (const k of ['r500', 'elim']) {
  P(`## 2.1 life ledger of pieces (children <= 3 at birth), ${k}`);
  P('net = (own-eaten death pearls, or final length if alive) + mass split off to children - birth length. new mass = natural + enemy-drop pearls eaten - sprint cost - (length at death - own-eaten death pearls).');
  for (const ph of ['all', '0', '1', '2', '3']) {
    P(`### born ${ph === 'all' ? 'any round' : PHN[+ph]}`);
    const rows = [];
    for (const g of [...MAIN, ...OLD]) { const m = M[g][k]; if (!m) continue; const r = pieceRow(g, k, ph + '|all', ph === 'all' ? m.n : games(m, +ph)); if (r) rows.push(r); }
    table(HEAD_P, rows);
  }
  P(`### by class (born r0-249 / r250-499), ${k}`);
  const rows = [];
  for (const g of [...MAIN, ...OLD]) {
    const m = M[g][k]; if (!m) continue;
    const cls = g.startsWith('T') || g === 'X' ? [10, 11, 12] : [1, 2, 3, 4, 5, 6, 9];
    for (const c of cls) for (const phs of [['0', '1'], ['2', '3', '4']]) {
      // sum the phase keys
      const v = new Array(64).fill(0); const hl = new Array(8).fill(0); let any = 0;
      for (const p of phs) { const a = m.pc[p + '|' + c]; if (a) { any = 1; for (let i = 0; i < 64; i++) v[i] += a[i]; const h = (m.ph[p + '|' + c] || {}).life; if (h) for (let i = 0; i < 8; i++) hl[i] += h[i]; } }
      if (!any || !v[0]) continue; const N = v[0];
      rows.push([g, CLS[c] + (phs[0] === '0' ? ' <r250' : ' r250+'), N, f1(N / m.n), f1(v[1] / N), hmed(hl, LIFE_E), f2(v[3] / N), pc(v[4], N), pc(v[5], N), ...[0, 1, 2, 3].map(e => pc(v[16 + e], N)), pc(v[28], v[27]), pc(v[29], v[27]), f2(v[34] / N), f2(v[35] / N), f2(v[36] / N), pc(v[37], v[36])]);
    }
  }
  table(['group', 'class', 'pieces', 'per game', 'life mean', 'life median', 'natural eaten', 'ate <=30r', 'alive +30', 'end alive', 'sac', 'trap', 'rammed', 'drops own', 'drops own big', 'net', 'new mass', 'claimed <=30r', 'claimed eaten'], rows);
}

// ---------------------------------------------------------------------------------------------------------------
// Q3 formation
const DIST_E = ['<=3', '4-5', '6-8', '9-12', '13-20', '21+', 'none'], NND_E = ['1', '2', '3', '4-5', '6-8', '9+', 'none'], N5_E = ['0', '1', '2', '3-4', '5-8', '9+'], PC_E = ['0', '1', '2', '3-4', '5+'];
const CELL_E = ['<0.5', '0.5-1', '1-2', '2-4', '4-8', '8-16', '16+'];
for (const k of ['r500', 'elim']) {
  P(`## 3.1 per-turn formation histograms of pieces (<= 4), ${k}`);
  for (const [name, edges, title] of [['pBig', DIST_E, 'Manhattan to the nearest own head >= 8'], ['pNnd', NND_E, 'Manhattan to the nearest other own head'], ['pN5', N5_E, 'own heads within Manhattan 5']]) {
    P(`### ${title}`);
    const rows = [];
    for (const g of MAIN) { const m = M[g][k]; if (!m) continue; const h = m.h[name]; if (!h) continue; const nb = edges.length;
      for (let p = 0; p < 5; p++) { const s = h.slice(p * nb, p * nb + nb), n = s.reduce((a, b) => a + b, 0); if (!n) continue; rows.push([g, PHN[p], n, ...s.map(v => pc(v, n))]); } }
    table(['group', 'phase', 'piece turns', ...edges], rows);
  }
  P(`### big allies (>= 8): own pieces within Manhattan 5, ${k}`);
  { const rows = []; for (const g of MAIN) { const m = M[g][k]; if (!m) continue; const h = m.h.bPc5; if (!h) continue; for (let p = 0; p < 5; p++) { const s = h.slice(p * 5, p * 5 + 5), n = s.reduce((a, b) => a + b, 0); if (!n) continue; rows.push([g, PHN[p], n, ...s.map(v => pc(v, n))]); } } table(['group', 'phase', 'big turns', ...PC_E], rows); }
  P(`## 3.2 checkpoints (first turn of the round; means over team-games in progress), ${k}`);
  P('vor = own-territory spawn capacity where our nearest head (static path) is nearer than theirs (tie 1/2); unc = own capacity with no head of either team within 6; ecl = own capacity where their head is nearer; svc = capacity-weighted mean distance from own capacity to our nearest head (cap 30); cellP = mean expected spawns per 30 rounds in a piece\'s Voronoi cell (all heads).');
  { const rows = [];
    for (const g of MAIN) { const m = M[g][k]; if (!m) continue;
      for (const r of [50, 100, 150, 200, 250, 300, 350, 400]) { const i = r / 10, cv = nm => m.cp[nm] && m.cp[nm].c[i] ? m.cp[nm].s[i] / m.cp[nm].c[i] : null;
        const pieces = cv('pieces'), cellP = m.cp.cellP && m.cp.cellP.c[i] ? m.cp.cellP.s[i] / 10 / Math.max(1, m.cp.pieces.s[i]) : null;
        rows.push([g, 'r' + r, m.cp.units ? m.cp.units.c[i] : 0, f1(cv('units')), f1(pieces), f1(cv('bigs')), pc(cv('vor'), 1000), pc(cv('unc'), 1000), pc(cv('ecl'), 1000), f1(cv('svc') / 100), f2(cellP)]); } }
    table(['group', 'round', 'team-games', 'units', 'pieces', 'bigs', 'vor', 'unc', 'ecl', 'svc', 'cellP (spawns/30r per piece)'], rows); }
  P(`### Voronoi cell of pieces (expected spawns per 30 rounds), share of piece-checkpoints, ${k}`);
  { const rows = []; for (const g of MAIN) { const m = M[g][k]; if (!m) continue; const h = m.h.cell0; if (!h) continue; for (let p = 0; p < 5; p++) { const s = h.slice(p * 7, p * 7 + 7), n = s.reduce((a, b) => a + b, 0); if (!n) continue; rows.push([g, PHN[p], n, ...s.map(v => pc(v, n))]); } } table(['group', 'phase', 'piece checkpoints', ...CELL_E], rows); }
  P(`## 3.3 which pieces eat within 30 rounds (born r0-249), ${k}`);
  for (const [name, edges, title] of [['n30_nnd', NND_E, 'nearest other own head at birth'], ['n30_n5', N5_E, 'own heads within 5 at birth'], ['n30_claim', ['0', '1', '2', '3-5', '6+'], 'spawns it was the unique nearest head of within 30 rounds'], ['n30_bt', ['own', 'neutral', 'enemy'], 'birth territory'], ['n30_big', DIST_E, 'nearest own >= 8 at birth'], ['n30_view', ['no', 'yes'], 'enemy head in view at birth']]) {
    P(`### by ${title}: pieces (share) / ate within 30 rounds`);
    const rows = [];
    for (const g of MAIN) { const m = M[g][k]; if (!m) continue; const nb = edges.length, c = new Array(nb * 2).fill(0);
      for (const p of ['0', '1']) { const h = (m.ph[p + '|all'] || {})[name]; if (h) for (let i = 0; i < nb * 2; i++) c[i] += h[i]; }
      const tot = c.reduce((a, b) => a + b, 0); if (!tot) continue;
      rows.push([g, tot, ...edges.map((_, i) => `${pc(c[2 * i] + c[2 * i + 1], tot)} / ${pc(c[2 * i + 1], c[2 * i] + c[2 * i + 1])}`)]); }
    table(['group', 'pieces', ...edges], rows);
  }
  P(`## 3.4 forage and return: pieces that ended by sacrifice (born any round), nearest own >= 8 over their life, ${k}`);
  for (const [name, title] of [['fedBirth', 'at birth'], ['fedMax', 'max over life'], ['fed10', '10 turns before the end'], ['fedLast', 'at the last turn']]) {
    const rows = []; for (const g of MAIN) { const m = M[g][k]; if (!m) continue; const h = (m.ph['all|all'] || {})[name]; if (!h) continue; const n = h.reduce((a, b) => a + b, 0); rows.push([g, n, ...h.map(v => pc(v, n))]); }
    P(`### ${title}`); table(['group', 'fed pieces', ...DIST_E], rows);
  }
  { const rows = []; for (const g of MAIN) { const m = M[g][k]; if (!m) continue; const h = (m.ph['all|all'] || {}).fedLife; if (!h) continue; const n = h.reduce((a, b) => a + b, 0); rows.push([g, n, ...h.map(v => pc(v, n))]); } P('### life of fed pieces'); table(['group', 'fed pieces', ...LIFE_E], rows); }
  { const rows = []; for (const g of MAIN) { const m = M[g][k]; if (!m) continue; const h = (m.ph['all|all'] || {}).trapLast; if (!h) continue; const n = h.reduce((a, b) => a + b, 0); rows.push([g, n, ...h.map(v => pc(v, n))]); } P('### trapped pieces: nearest own >= 8 at the last turn'); table(['group', 'trapped pieces', ...DIST_E], rows); }
}

// ---------------------------------------------------------------------------------------------------------------
// natural spawns race (context: foraging supply)
function spSum(m, filt) { const s = [0, 0, 0, 0]; for (const [k, v] of Object.entries(m.sp)) { const [ph, terr, race, cls] = k.split('|').map(Number); if (!filt(ph, terr, race, cls)) continue; for (let i = 0; i < 4; i++) s[i] += v[i]; } return s; }
for (const k of ['r500', 'elim']) {
  P(`## 3.5 natural spawns: who is nearest and who eats (per game), ${k}`);
  const rows = [];
  for (const g of MAIN) { const m = M[g][k]; if (!m) continue;
    for (const [pname, p0, p1] of [['r0-99', 0, 0], ['r100-249', 1, 1], ['r250-499', 2, 4]]) { const n = games(m, p0);
      const all = spSum(m, ph => ph >= p0 && ph <= p1), own = spSum(m, (ph, t) => ph >= p0 && ph <= p1 && t === 0);
      const race = [0, 1, 2, 3].map(r => spSum(m, (ph, t, rc) => ph >= p0 && ph <= p1 && t === 0 && rc === r));
      const byP = spSum(m, (ph, t, rc, cls) => ph >= p0 && ph <= p1 && cls === 0), byM = spSum(m, (ph, t, rc, cls) => ph >= p0 && ph <= p1 && cls === 1), byB = spSum(m, (ph, t, rc, cls) => ph >= p0 && ph <= p1 && cls === 2);
      rows.push([g, pname, f1(all[0] / n), f1(all[1] / n), f1(own[0] / n), pc(own[1], own[0]), pc(own[2], own[0]), ...race.map(r => pc(r[0], own[0])), pc(byP[0], all[0]), pc(byP[3], byP[0]), pc(byM[0], all[0]), pc(byM[3], byM[0]), pc(byB[0], all[0]), pc(byB[3], byB[0])]); } }
  table(['group', 'phase', 'spawns/game', 'eaten by us/game', 'own-terr spawns/game', 'own-terr eaten us', 'own-terr eaten them', 'own-terr: we nearer', 'tie', 'they nearer', 'none <=12', 'our piece unique nearest', '… it ate', 'our mid nearest', '… it ate', 'our big nearest', '… it ate'], rows);
}

// per map key numbers (r250-499 conv / feed supply, drops, pieces)
P('## 4. per map (all phases unless noted)');
{
  const maps = [...R500, ...ELIM];
  const rows = [];
  for (const mp of maps) for (const g of ['TW', 'TL', 'X', 'merge2', 'stack4', 'stack5']) {
    const m = merged(g, [mp]); if (!m) continue; const n2 = m.nPh[2] || 1;
    const eps = epv(m, 'cs', 2, 4, 0), fired = epv(m, 'cs', 2, 4, 1), ok = epv(m, 'cs', 2, 4, 6);
    const feps = epv(m, 'fs', 2, 4, 0), ffired = epv(m, 'fs', 2, 4, 1);
    const w6 = drSum(m, (ph, o, cg, w) => w === 1), v = m.pc['all|all'] || new Array(64).fill(0);
    rows.push([mp, g, m.n, f1(bsum(m, 'cs', 2, 4) / n2), f1(eps / n2), pc(fired, eps), f2(fired / n2), f2(ok / n2), f1(bsum(m, 'fs', 2, 4) / n2), pc(ffired, feps), f1(w6[0] / m.n), pc(w6[1], w6[0]), f1(v[0] / m.n), pc(v[4], v[0]), pc(v[5], v[0]), f2(v[34] / Math.max(1, v[0]))]);
  }
  table(['map', 'group', 'team-games', 'cs turns/game (r250+)', 'cs episodes/game', 'fired', 'fired/game', 'ok/game', 'fs turns/game', 'fs fired', 'drops within 6/game', 'eaten own', 'pieces/game', 'ate <=30r', 'alive +30', 'net/piece'], rows);
}

// ---------------------------------------------------------------------------------------------------------------
// 5. material through each link (pearls per team-game) and the funnel decomposition
P('## 5. material through each link, pearls per team-game (phase groups by the round of the event; pieces by birth round)');
P('conv-like = pieces (<=4, not stubs) sacrificed with an own head >= 8 within Manhattan 3, pearls eaten by own dragons >= 8; piece->piece = pieces sacrificed with only shorter own heads near (S), pearls eaten by own; mid/big sac = sacrifices of dragons >= 5, pearls eaten by own >= 8; recycling = trapped pieces that are not stubs, pearls eaten by own; stub = a <=4 remnant of its own split within 2 rounds (U-turn / escape-split loop), any cause, pearls eaten by own; grab own / enemy = death drops within 6 of our heads eaten by us; forage = natural pearls eaten by pieces born in the phase group.');
for (const k of ['r500', 'elim']) {
  const rows = [];
  for (const g of [...MAIN, ...OLD]) {
    const m = M[g][k]; if (!m) continue;
    for (const [pname, p0, p1] of [['r0-249', 0, 1], ['r250-499', 2, 4]]) {
      const n = games(m, p0);
      const d = f => dtSum(m, (ph, c, lc, nr, mech) => ph >= p0 && ph <= p1 && f(c, lc, nr, mech));
      const convB = d((c, lc, nr, mech) => c === 0 && lc === 0 && nr === 'B' && mech !== 's'), p2p = d((c, lc, nr, mech) => c === 0 && lc === 0 && nr === 'S' && mech !== 's'), p0s = d((c, lc, nr, mech) => c === 0 && lc === 0 && nr === '0' && mech !== 's');
      const mbs = d((c, lc) => c === 0 && lc >= 1), trap = d((c, lc, nr, mech) => c === 1 && lc === 0 && mech !== 's'), stub = d((c, lc, nr, mech) => lc === 0 && mech === 's');
      const gOwn = drSum(m, (ph, o, cg, w6) => ph >= p0 && ph <= p1 && o === 0 && w6 === 1), gEn = drSum(m, (ph, o, cg, w6) => ph >= p0 && ph <= p1 && o === 1 && w6 === 1);
      let pv = new Array(64).fill(0); for (let p = p0; p <= p1; p++) { const a = m.pc[p + '|all']; if (a) for (let i = 0; i < 64; i++) pv[i] += a[i]; }
      rows.push([g, pname, n, f1(pv[0] / n), f1(pv[3] / n), f1(convB[6] / n), f1(p2p[3] / n), f1(p0s[3] / n), f1(mbs[6] / n), f1(trap[3] / n), f1(stub[3] / n), f1(gOwn[1] / n), f1(gEn[1] / n),
        f1(epv(m, 'cs', p0, p1, 0) / n), pc(epv(m, 'cs', p0, p1, 1), epv(m, 'cs', p0, p1, 0)), f2(epv(m, 'cs', p0, p1, 7) / n), f1(epv(m, 'fs', p0, p1, 0) / n), pc(epv(m, 'fs', p0, p1, 1), epv(m, 'fs', p0, p1, 0)), f2(epv(m, 'fs', p0, p1, 7) / n)]);
    }
  }
  P(`### ${k}`);
  table(['group', 'phase', 'team-games', 'pieces born', 'forage (natural by pieces)', 'conv-like to big', 'piece->piece', 'piece sac alone', 'mid/big sac to big', 'recycling (trap, not stub)', 'stub deaths (own eats)', 'grab own drops', 'grab enemy drops', 'cs episodes', 'cs fired', 'cs okBig/game', 'fs episodes', 'fs fired', 'fs okBig/game'], rows);
}

const outF = path.resolve(ROOT, opt('out', 'exp/supply-chain/report.md'));
fs.writeFileSync(outF, out.join('\n') + '\n');
console.error(`wrote ${path.relative(ROOT, outF)} (${out.length} lines)`);
