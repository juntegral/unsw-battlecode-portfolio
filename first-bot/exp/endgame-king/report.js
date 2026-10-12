#!/usr/bin/env node
// Tables for research/observations/endgame-king.md from .cache/endgame-king/*.jsonl (exp/endgame-king/extract.js).
// usage: node exp/endgame-king/report.js [--out exp/endgame-king/report.md] [--json exp/endgame-king/numbers.json]
// Population rules: top-vs-top games with a winner; a game is left out when a team stopped (splits <= 3 and sonar 0) or the
// game had >= 3 timeout deaths (the mass-analysis rule). Ours: every game of the listed online sets (both sides; the elite side
// is group X). Groups of our sets below (SETGRP).
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'endgame-king');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const SETGRP = {
  'cand-stack1-online': 'stack1-4', 'cand-stack2-online': 'stack1-4', 'cand-stack3-online': 'stack1-4', 'cand-stack4-online': 'stack1-4',
  'cand-stack5-online': 'stack5', 'cand-stack6-online': 'stack6', 'cand-stack6-online-r2': 'stack6', 'cand-stack7-online': 'stack7', 'cand-stack8-online': 'stack8',
  'cand-merge2-online': 'merge2', 'cand-merge2-online-r2': 'merge2', 'cand-merge2-online-r3': 'merge2',
  'cand-swarm8-online': 'swarm8', 'cand-avoid6-online': 'avoid6', 'cand-portal1-online': 'portal1',
  'baseline-r1': 'g4r4', 'baseline-r1b': 'g4r4', 'baseline-r1c': 'g4r4',
  'base-px8-online': 'px', 'base-px9d-online': 'px', 'px-king-v2-online': 'px',
};
const OURS = ['g4r4', 'merge2', 'swarm8', 'avoid6', 'portal1', 'stack1-4', 'stack5', 'stack6', 'stack7', 'stack8', 'px'];
const GRPS = ['W', 'L', 'X', ...OURS, 'S58']; // S58 = stack5-8 pooled (csplit era)
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];

function readJsonl(f) { const out = []; if (!fs.existsSync(f)) return out; for (const l of fs.readFileSync(f, 'utf8').split('\n')) { if (!l.trim()) continue; try { out.push(JSON.parse(l)); } catch { } } return out; }
function loadAll() {
  const teams = []; const games = { top: 0, topKept: 0, online: {} }; const chkSum = {}, chk2Sum = {};
  const addChk = g => { for (const [k, v] of Object.entries(g.chk || {})) chkSum[k] = (chkSum[k] || 0) + v; for (const [k, v] of Object.entries(g.chk2 || {})) chk2Sum[k] = (chk2Sum[k] || 0) + v; };
  const files = fs.readdirSync(CACHE).filter(f => f.endsWith('.jsonl'));
  for (const f of files) {
    const isTop = f.startsWith('top');
    for (const g of readJsonl(path.join(CACHE, f))) {
      addChk(g);
      if (isTop) {
        games.top++;
        if (!g.winner) continue;
        const stopped = ['A', 'B'].some(t => g[t].splits <= 3 && g[t].sonar === 0);
        if (stopped || g.A.faults + g.B.faults >= 3) continue;
        games.topKept++;
        for (const t of ['A', 'B']) teams.push({ grp: t === g.winner ? 'W' : 'L', g, t, won: t === g.winner });
      } else {
        const grp = SETGRP[g.set]; if (!grp) continue;
        games.online[g.set] = (games.online[g.set] || 0) + 1;
        const them = g.us === 'A' ? 'B' : 'A';
        teams.push({ grp, g, t: g.us, won: g.winner === g.us, ours: true });
        if (/^stack[5-8]$/.test(grp)) teams.push({ grp: 'S58', g, t: g.us, won: g.winner === g.us, ours: true, pooled: true });
        teams.push({ grp: 'X', g, t: them, won: g.winner === them, opp: g.opp });
      }
    }
  }
  return { teams, games, chkSum, chk2Sum };
}
const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN;
const median = a => { if (!a.length) return NaN; const b = a.slice().sort((x, y) => x - y); return b[Math.floor(b.length / 2)]; };
const f1 = x => Number.isFinite(x) ? x.toFixed(1) : '–', f2 = x => Number.isFinite(x) ? x.toFixed(2) : '–';
const pct = (a, b) => b ? Math.round(100 * a / b) + '%' : '–';
const md = (head, rows) => ['| ' + head.join(' | ') + ' |', '|' + head.map((h, i) => i === 0 ? '---' : '---:').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');

function main() {
  const { teams, games, chkSum, chk2Sum } = loadAll();
  const out = [], J = {};
  out.push('# endgame-king report (generated ' + new Date().toISOString() + ')');
  out.push(`top games read ${games.top}, kept ${games.topKept}; online ${JSON.stringify(games.online)}`);
  out.push('ledger checks ' + JSON.stringify(chkSum) + '; own checks ' + JSON.stringify(chk2Sum));
  J.games = games; J.chk = chkSum; J.chk2 = chk2Sum;
  const R = x => x.g.res || x.g[x.t];
  const sel = (grp, f) => teams.filter(x => x.grp === grp && f(x));
  const r500full = x => x.g.kind === 'r500' && x.g.rounds === 500 && x.g[x.t].kid >= 0;
  // ------------------------------------------------------------------ Q1: sources of the final king's length per 50-round bin
  const SRC = ['nat', 'oSac', 'oOther', 'enemy', 'sprint', 'lossOff', 'lossPath'];
  const q1 = (grp, f) => {
    const T = sel(grp, f); if (!T.length) return null;
    const bins = [0, 1, 2, 3, 4].map(b => SRC.map((_, i) => mean(T.map(x => x.g[x.t].dec[b][i]))));
    const L300 = mean(T.map(x => x.g[x.t].Lt[300]).filter(v => v !== undefined));
    const fin = mean(T.map(x => x.g[x.t].king));
    return { n: T.length, bins, L300, fin, win: mean(T.map(x => x.won ? 1 : 0)) };
  };
  out.push('\n## Q1. Final king line: gains by source per 50-round bin (500-round maps, games to r500; per team-game)');
  const q1rows = []; J.q1 = {};
  for (const grp of GRPS) {
    const q = q1(grp, r500full); if (!q) continue; J.q1[grp] = q;
    const netB = b => q.bins[b][0] + q.bins[b][1] + q.bins[b][2] + q.bins[b][3] - q.bins[b][4] - q.bins[b][5] - q.bins[b][6];
    for (let b = 1; b <= 4; b++) q1rows.push([grp, q.n, ['r300', 'r350', 'r400', 'r450'][b - 1], ...q.bins[b].map(f1), f1(netB(b))]);
    q1rows.push([grp, q.n, 'sum 300-499', ...SRC.map((_, i) => f1(q.bins.slice(1).reduce((s, v) => s + v[i], 0))), f1([1, 2, 3, 4].reduce((s, b) => s + netB(b), 0))]);
    q1rows.push([grp, q.n, 'L300 → final (win%)', f1(q.L300), f1(q.fin), pct(Math.round(q.win * q.n), q.n), '', '', '', '', '']);
  }
  out.push(md(['group', 'team-games', 'bin', 'nat', 'own sac', 'own other', 'enemy', '− sprint', '− split off', '− split path', 'net'], q1rows));
  // per map (W vs ours pooled S58 and merge2)
  out.push('\n### Q1 per map (sum r300-499; L300; final)');
  const q1m = []; J.q1map = {};
  for (const m of R500) for (const grp of ['W', 'L', 'X', 'merge2', 'stack1-4', 'S58']) {
    const q = q1(grp, x => r500full(x) && x.g.map === m); if (!q) continue;
    const s = i => q.bins.slice(1).reduce((a, v) => a + v[i], 0);
    J.q1map[m + '|' + grp] = q;
    q1m.push([m, grp, q.n, f1(q.L300), f1(s(0)), f1(s(1)), f1(s(2)), f1(s(3)), f1(-s(4)), f1(-s(5) - s(6)), f1(q.fin), pct(Math.round(q.win * q.n), q.n)]);
  }
  out.push(md(['map', 'group', 'n', 'L300', 'nat', 'own sac', 'own other', 'enemy', 'sprint', 'split', 'final', 'win'], q1m));
  // elimination maps: winners' final line in games that lasted past r300
  out.push('\n### Q1 elimination maps (Devil, Trophy, PD, QoS, Default): the final king line, games that lasted past r300');
  const q1e = []; J.q1elim = {};
  for (const grp of GRPS) for (const end of ['r500', 'elim']) {
    const f = x => x.g.kind === 'elim' && x.g.rounds > 300 && x.g[x.t].kid >= 0 && (end === 'r500' ? x.g.rounds === 500 : x.g.rounds < 500);
    const T = sel(grp, f); if (T.length < 3) continue;
    const bins = [1, 2, 3, 4].map(b => { const U = T.filter(x => x.g.rounds > 250 + 50 * b); return { n: U.length, v: SRC.map((_, i) => mean(U.map(x => x.g[x.t].dec[b][i]))) }; });
    J.q1elim[grp + '|' + end] = { n: T.length, bins, L300: mean(T.map(x => x.g[x.t].Lt[300]).filter(v => v !== undefined)), fin: mean(T.map(x => x.g[x.t].king)) };
    for (let b = 0; b < 4; b++) if (bins[b].n) q1e.push([grp, end, ['r300', 'r350', 'r400', 'r450'][b], bins[b].n, ...bins[b].v.map(f1)]);
    q1e.push([grp, end, 'L300 → final', T.length, f1(J.q1elim[grp + '|' + end].L300), f1(J.q1elim[grp + '|' + end].fin), '', '', '', '', '']);
  }
  out.push(md(['group', 'ending', 'bin', 'team-games', 'nat', 'own sac', 'own other', 'enemy', 'sprint', 'split off', 'split path'], q1e));
  // ------------------------------------------------------------------ Q2: growth vs start
  out.push('\n## Q2. Final king line length at r300/350/400/450/500 and growth per round (500-round maps, games to r500)');
  const q2 = []; J.q2 = {};
  for (const grp of GRPS) {
    const T = sel(grp, x => r500full(x) && x.g[x.t].Lt[300] !== undefined); if (!T.length) continue;
    const L = t => mean(T.map(x => t === 500 ? x.g[x.t].king : x.g[x.t].Lt[t]));
    const top300 = mean(T.map(x => x.g[x.t].st.king[0]));
    const g = [300, 350, 400, 450].map(t => (L(t + 50) - L(t)) / 50);
    J.q2[grp] = { n: T.length, L: [300, 350, 400, 450, 500].map(L), top300, g };
    q2.push([grp, T.length, f1(top300), ...[300, 350, 400, 450, 500].map(t => f1(L(t))), ...g.map(f2), f2((L(500) - L(300)) / 200)]);
  }
  out.push(md(['group', 'n', 'team longest r300', 'line L300', 'L350', 'L400', 'L450', 'final', 'g300', 'g350', 'g400', 'g450', 'g300-500'], q2));
  out.push('\n### Q2 by L300 class: growth per round r300→500 (n)');
  const cls = [[0, 10], [11, 20], [21, 30], [31, 999]];
  const q2c = []; J.q2c = {};
  for (const grp of GRPS) {
    const T = sel(grp, x => r500full(x) && x.g[x.t].Lt[300] !== undefined); if (!T.length) continue;
    const row = [grp];
    for (const [a, b] of cls) { const U = T.filter(x => x.g[x.t].Lt[300] >= a && x.g[x.t].Lt[300] <= b); const v = mean(U.map(x => (x.g[x.t].king - x.g[x.t].Lt[300]) / 200)); row.push(U.length ? `${f2(v)} (${U.length})` : '–'); J.q2c[grp + '|' + a] = { n: U.length, g: v, fin: mean(U.map(x => x.g[x.t].king)), win: mean(U.map(x => x.won ? 1 : 0)) }; }
    q2c.push(row);
  }
  out.push(md(['group', 'L300 ≤10', '11–20', '21–30', '31+'], q2c));
  // ------------------------------------------------------------------ Q3: gathering (ours) and the elite's non-king dragons
  out.push('\n## Q3. Gathering episodes (our labelled sets; a dragon with a move label g<d>)');
  const gRows = []; J.q3 = {};
  const ENDS = ['', 'fed', 'other sac', 'died', 'alive off line', 'alive on line'];
  for (const grp of OURS.concat(['S58'])) for (const kind of ['r500', 'elim']) {
    const T = sel(grp, x => x.g.kind === kind && x.g[x.t].gath); if (!T.length) continue;
    const E = []; for (const x of T) for (const q of x.g[x.t].gath) E.push(q);
    if (!E.length) continue;
    const n = E.length, games = T.length;
    const by = k => E.filter(q => q[15] === k).length;
    const gT = E.reduce((s, q) => s + q[8], 0), natG = E.reduce((s, q) => s + q[10], 0), dropG = E.reduce((s, q) => s + q[11], 0);
    const tPre = E.reduce((s, q) => s + q[13], 0), natPre = E.reduce((s, q) => s + q[12], 0);
    const fed = E.filter(q => q[15] === 1), fedDrops = fed.reduce((s, q) => s + q[17], 0), fedLine = fed.reduce((s, q) => s + q[18], 0), fedOwn = fed.reduce((s, q) => s + q[19], 0), fedEn = fed.reduce((s, q) => s + q[20], 0);
    const reached = E.filter(q => q[14] <= 5).length;
    const nS = E.reduce((s, q) => s + q[24], 0), nOwn = E.reduce((s, q) => s + q[25], 0), nEn = E.reduce((s, q) => s + q[26], 0), nSelf = E.reduce((s, q) => s + q[27], 0);
    const o = { games, n, perGame: n / games, L0: mean(E.map(q => q[2])), d0: median(E.map(q => q[3])), dKing0: median(E.map(q => q[6])), gTurns: gT / n, steps: E.reduce((s, q) => s + q[9], 0) / n,
      natPerG: natG / gT, dropPerG: dropG / gT, natPerPre: natPre / tPre, ends: [1, 2, 3, 4, 5].map(by), fedDrops, fedLine, fedOwn, fedEn, reached,
      nearSpawn: nS, nearSelf: nSelf, nearOwn: nOwn, nearEnemy: nEn, becameLongest: E.filter(q => q[23]).length, L4: E.filter(q => q[2] >= 4).length,
      big: E.filter(q => q[2] >= 8).length, bigEnds: [1, 2, 3, 4, 5].map(k => E.filter(q => q[2] >= 8 && q[15] === k).length) };
    J.q3[grp + '|' + kind] = o;
    gRows.push([grp, kind, games, n, f1(o.perGame), f1(o.L0), o.d0, o.dKing0, f1(o.gTurns), f1(o.steps), f2(o.natPerPre), f2(o.natPerG), f2(o.dropPerG), pct(reached, n),
      ...[1, 2, 3, 4, 5].map(k => pct(by(k), n)), pct(fedLine, fedDrops), pct(fedOwn, fedDrops), pct(nEn, nS), pct(nSelf, nS)]);
  }
  out.push(md(['group', 'maps', 'games', 'episodes', '/game', 'L0', 'd0 med', 'dKing0 med', 'g turns', 'steps', 'nat/turn before', 'nat/turn g', 'drop/turn g', 'reached ≤5',
    'fed', 'other sac', 'died', 'alive off', 'alive line', 'fed drops→line', 'fed drops→own other', 'spawns near start→enemy', '→itself'], gRows));
  // root episodes (not a child split off a gathering parent) with the family's fate
  out.push('\n### Q3b root gathering episodes (a dragon whose parent was not already gathering when it was born): family fate (the dragon and its later children)');
  const FATE = ['line', 'alive off', 'fed (labelled)', 'other sac', 'died other'];
  const fateOf = q => q[42] ? 0 : q[22] ? 1 : q[44] ? 2 : q[43] === 0 ? 3 : 4;
  const g2 = []; J.q3b = {};
  for (const grp of OURS.concat(['S58'])) for (const kind of ['r500', 'elim']) {
    const T = sel(grp, x => x.g.kind === kind && x.g[x.t].gath); if (!T.length) continue;
    const E = []; for (const x of T) for (const q of x.g[x.t].gath) if (!q[40]) E.push(q);
    if (!E.length) continue;
    const n = E.length, fc = [0, 1, 2, 3, 4].map(k => E.filter(q => fateOf(q) === k).length);
    const famDrops = E.reduce((s, q) => s + q[46], 0), famToLine = E.reduce((s, q) => s + q[34], 0);
    const mass0 = E.reduce((s, q) => s + q[2], 0);
    const aliveLen = E.filter(q => fateOf(q) === 1).reduce((s, q) => s + q[35], 0);
    const kingIsLine = E.filter(q => q[32]).length;
    const nB = E.reduce((s, q) => s + q[36], 0), eB = E.reduce((s, q) => s + q[39], 0), nA = E.reduce((s, q) => s + q[24], 0), eA = E.reduce((s, q) => s + q[26], 0);
    const sB = E.reduce((s, q) => s + q[37], 0), sA = E.reduce((s, q) => s + q[27], 0);
    const o = { games: T.length, n, fc, famDrops, famToLine, mass0, aliveLen, kingIsLine, nB, eB, nA, eA, sB, sA, stub: E.filter(q => q[41]).length,
      natG: E.reduce((s, q) => s + q[10], 0), gT: E.reduce((s, q) => s + q[8], 0), natPre: E.reduce((s, q) => s + q[12], 0), tPre: E.reduce((s, q) => s + q[13], 0),
      steps: E.reduce((s, q) => s + q[9], 0), dKing0: median(E.map(q => q[6])), L0: mean(E.map(q => q[2])), r0: median(E.map(q => q[1])), reached: E.filter(q => q[14] <= 5).length };
    J.q3b[grp + '|' + kind] = o;
    g2.push([grp, kind, T.length, n, f1(n / T.length), f1(o.L0), o.r0, o.dKing0, f1(o.steps / n), f2(o.natPre / o.tPre), f2(o.natG / o.gT), pct(o.reached, n), ...fc.map(v => pct(v, n)), pct(famToLine, famDrops), f1(mass0 / T.length), f1(famToLine / T.length), f1(aliveLen / T.length), pct(kingIsLine, n), `${pct(eB, nB)} → ${pct(eA, nA)}`, `${pct(sB, nB)} → ${pct(sA, nA)}`]);
  }
  out.push(md(['group', 'maps', 'games', 'root episodes', '/game', 'L0', 'r0 med', 'dKing0 med', 'steps', 'nat/turn 20r before', 'nat/turn g', 'reached ≤5', ...FATE, 'family drops → line', 'L0 sum/game', 'to line/game', 'alive-off length/game', 'king at r0 = line member', 'spawns ≤5 of start → enemy: 40r before → 40r after', '→ itself: before → after'], g2));
  // per map for the csplit era + stack8
  out.push('\n### Q3b per map (500-round maps, S58 and stack8 and merge2+stack1-4)');
  const g3 = [];
  for (const m of R500) for (const grp of ['merge2', 'stack1-4', 'S58', 'stack8']) {
    const T = sel(grp, x => x.g.map === m && x.g[x.t].gath); if (!T.length) continue;
    const E = []; for (const x of T) for (const q of x.g[x.t].gath) if (!q[40]) E.push(q);
    if (!E.length) continue;
    const n = E.length, fc = [0, 1, 2, 3, 4].map(k => E.filter(q => fateOf(q) === k).length);
    const famDrops = E.reduce((s, q) => s + q[46], 0), famToLine = E.reduce((s, q) => s + q[34], 0);
    const nB = E.reduce((s, q) => s + q[36], 0), eB = E.reduce((s, q) => s + q[39], 0), nA = E.reduce((s, q) => s + q[24], 0), eA = E.reduce((s, q) => s + q[26], 0);
    J['q3map|' + m + '|' + grp] = { n, fc, famDrops, famToLine, nB, eB, nA, eA, games: T.length, kingIsLine: E.filter(q => q[32]).length };
    g3.push([m, grp, T.length, n, ...fc.map(v => pct(v, n)), pct(famToLine, famDrops), pct(E.filter(q => q[32]).length, n), `${pct(eB, nB)} → ${pct(eA, nA)}`, f1(E.reduce((s, q) => s + q[26] - q[39], 0) / T.length)]);
  }
  out.push(md(['map', 'group', 'games', 'root episodes', ...FATE, 'family drops → line', 'king at r0 = line member', 'spawns near start → enemy before → after', 'extra enemy eats near starts/game (after − before)'], g3));
  // cohort before/after (every group): spawns near the r340 head, r300-339 vs r340-379
  out.push('\n### Q3c what the r340 cohort leaves behind: natural spawns within Manhattan 5 of the r340 head, eaten by the enemy / by itself, r300–339 → r340–379 (500-round maps, games to r500)');
  const g4 = []; J.q3c = {};
  for (const grp of GRPS) for (const gf of ['all', 'g', 'noG']) {
    if (gf !== 'all' && !OURS.concat(['S58']).includes(grp)) continue;
    const T = sel(grp, r500full); if (!T.length) continue;
    const C = []; for (const x of T) for (const c of x.g[x.t].coh) if (gf === 'all' || (gf === 'g' ? c[11] > 0 : c[11] === 0)) C.push(c);
    if (!C.length) continue;
    const S = i => C.reduce((s, c) => s + c[i], 0);
    J.q3c[grp + '|' + gf] = { n: C.length, games: T.length, nB: S(17), sB: S(18), oB: S(19), eB: S(20), nA: S(7), sA: S(8), oA: S(9), eA: S(10) };
    g4.push([grp, gf, T.length, C.length, f1(S(17) / C.length), f1(S(7) / C.length), `${pct(S(20), S(17))} → ${pct(S(10), S(7))}`, `${pct(S(18), S(17))} → ${pct(S(8), S(7))}`, `${pct(S(19), S(17))} → ${pct(S(9), S(7))}`, f1((S(10) - S(20)) / T.length)]);
  }
  out.push(md(['group', 'who', 'games', 'cohort', 'spawns before/dragon', 'after/dragon', '→ enemy', '→ itself', '→ own other', 'extra enemy eats/game'], g4));
  // non-king dragons (L >= 4), r340+, by distance to the king
  out.push('\n### Q3 non-king dragons (L ≥ 4) from r340: turns share and natural pearls per turn by distance to the king (500-round maps, all games)');
  const nkRows = []; J.nk = {};
  for (const grp of GRPS) {
    const T = sel(grp, x => x.g.kind === 'r500'); if (!T.length) continue;
    const a = new Array(60).fill(0); for (const x of T) { const v = x.g[x.t].nk; for (let i = 0; i < 60; i++) a[i] += v[i]; }
    const row = [grp, T.length];
    let tot = 0; for (let p = 0; p < 3; p++) for (let c = 0; c < 4; c++) tot += a[(p * 4 + c) * 5];
    for (let c = 0; c < 4; c++) { let t = 0, n = 0, dr = 0; for (let p = 0; p < 3; p++) { const b = (p * 4 + c) * 5; t += a[b]; n += a[b + 1]; dr += a[b + 2]; } row.push(`${pct(t, tot)} · ${f2(n / t)} · ${f2(dr / t)}`); }
    let pv = 0, ap = 0; for (let i = 0; i < 12; i++) { pv += a[i * 5 + 3]; ap += a[i * 5 + 4]; }
    row.push(f1(tot / T.length), pct(ap, pv));
    J.nk[grp] = a; nkRows.push(row);
  }
  out.push(md(['group', 'team-games', '≤3 (turns · nat/turn · drop/turn)', '4–8', '9–16', '17+', 'turns/game', 'closer than last turn'], nkRows));
  // r340 cohort: ends, mass to line, what it would forage
  out.push('\n### Q3/Q4 r340 cohort (non-king L ≥ 4 at the first turn of r340; 500-round maps, games to r500)');
  const cRows = []; J.coh = {};
  for (const grp of GRPS) for (const gf of ['all', 'g', 'noG']) {
    if (gf !== 'all' && !OURS.concat(['S58']).includes(grp)) continue;
    const T = sel(grp, r500full); if (!T.length) continue;
    const C = []; for (const x of T) for (const c of x.g[x.t].coh) if (gf === 'all' || (gf === 'g' ? c[11] > 0 : c[11] === 0)) C.push(c);
    if (!C.length) continue;
    const by = k => C.filter(c => c[3] === k).length;
    const nS = C.reduce((s, c) => s + c[7], 0), eS = C.reduce((s, c) => s + c[8], 0), eO = C.reduce((s, c) => s + c[9], 0), eE = C.reduce((s, c) => s + c[10], 0);
    const o = { games: T.length, n: C.length, L0: mean(C.map(c => c[1])), far: C.filter(c => c[2] > 16).length, ends: [0, 1, 2, 3, 4].map(by), massToLine: C.reduce((s, c) => s + c[4], 0) / T.length,
      natAfter: mean(C.map(c => c[5])), nS, eS, eO, eE, mass: C.reduce((s, c) => s + c[1], 0) / T.length };
    J.coh[grp + '|' + gf] = o;
    cRows.push([grp, gf, T.length, f1(C.length / T.length), f1(o.L0), pct(o.far, C.length), ...[0, 1, 2, 3, 4].map(k => pct(by(k), C.length)), f1(o.massToLine), f1(o.natAfter), f1(nS / C.length), pct(eS, nS), pct(eO, nS), pct(eE, nS)]);
  }
  out.push(md(['group', 'who', 'games', 'cohort/game', 'L0', 'dK0 > 16', 'on line', 'family alive off', 'sacrificed', 'died other', 'family died later', 'drops to line/game', 'nat eaten after r340',
    'spawns ≤5 of r340 head (r340–379)', '→itself', '→own other', '→enemy'], cRows));
  // ------------------------------------------------------------------ Q4: sacrifices and the line
  out.push('\n## Q4. Sacrifices from r300 by distance to the line member at death (500-round maps, games to r500; per team-game)');
  const sRows = []; J.sac = {};
  for (const grp of GRPS) {
    const T = sel(grp, r500full); if (!T.length) continue;
    for (const dc of [0, 1, 2, 3]) {
      const a = new Array(11).fill(0);
      for (const x of T) for (const [k, v] of Object.entries(x.g[x.t].sac)) { const p = k.split('|'); if (+p[1] !== dc) continue; for (let i = 0; i < 11; i++) a[i] += v[i]; }
      J.sac[grp + '|' + dc] = a;
      sRows.push([grp, T.length, ['≤3', '4–8', '9–16', '17+'][dc], f1(a[0] / T.length), f1(a[2] / T.length), pct(a[3], a[2]), pct(a[4], a[2]), pct(a[5], a[2]), pct(a[6], a[2]), pct(a[7], a[2]), pct(a[8], a[0]), pct(a[9], a[4] + a[5]), pct(a[10], a[4] + a[5])]);
    }
  }
  out.push(md(['group', 'n', 'dLine', 'sacrifices/game', 'pearls/game', '→line', '→off-line longer', '→off-line other', '→enemy', 'uneaten', 'came from >8 (20 r before)', 'off-line eater family alive at end', '…died, gave to line'], sRows));
  out.push('\n### Q4 sacrifice pearls eaten by the line per bin (per team-game): total · feeder ≤3 at death · feeder came from >8 · from feeders L ≥ 8');
  const lRows = []; J.lineSac = {};
  for (const grp of GRPS) {
    const T = sel(grp, r500full); if (!T.length) continue;
    const a = [0, 1, 2, 3].map(b => [0, 1, 2, 3, 4].map(i => T.reduce((s, x) => s + x.g[x.t].lineSac[b][i], 0) / T.length));
    J.lineSac[grp] = a;
    lRows.push([grp, T.length, ...a.map(v => `${f1(v[0])} · ${pct(v[1], v[0])} · ${pct(v[2], v[0])} · ${pct(v[4], v[0])}`)]);
  }
  out.push(md(['group', 'n', 'r300', 'r350', 'r400', 'r450'], lRows));
  out.push('\n### Q4 who is the line member (500-round maps, games to r500): team longest at t (%), first round it was the team longest (median), r340 cohort member on the line');
  const kRows = []; J.lr = {};
  for (const grp of GRPS) {
    const T = sel(grp, r500full); if (!T.length) continue;
    const row = [grp, T.length];
    for (const t of [300, 350, 400, 450]) { const U = T.filter(x => x.g[x.t].lr && x.g[x.t].lr[t]); const k = U.filter(x => x.g[x.t].lr[t][1] === x.g[x.t].lr[t][2]).length; row.push(pct(k, U.length)); J.lr[grp + '|' + t] = [k, U.length]; }
    const first = T.map(x => x.g[x.t].lr && x.g[x.t].lr[450] ? x.g[x.t].lr[450][3] : 0).filter(v => v > 0);
    const fromCoh = T.filter(x => x.g[x.t].coh.some(c => c[3] === 0)).length;
    row.push(median(first), pct(first.filter(v => v > 400).length, first.length), pct(fromCoh, T.length));
    J.lr[grp + '|coh'] = [fromCoh, T.length];
    kRows.push(row);
  }
  out.push(md(['group', 'n', 'r300', 'r350', 'r400', 'r450', 'first longest (median round)', 'first longest after r400', 'final king from the r340 non-king cohort'], kRows));
  // the final king from the cohort: its r340 length and distance, and its gains
  out.push('\n### Q4 games whose final king line came from the r340 non-king cohort vs from the r340 king (500-round maps, to r500)');
  const fRows = []; J.fromCoh = {};
  for (const grp of GRPS) for (const which of ['cohort', 'king340']) {
    const T = sel(grp, x => r500full(x) && (which === 'cohort' ? x.g[x.t].coh.some(c => c[3] === 0) : !x.g[x.t].coh.some(c => c[3] === 0))); if (T.length < 3) continue;
    const s = i => mean(T.map(x => [1, 2, 3, 4].reduce((a, b) => a + x.g[x.t].dec[b][i], 0)));
    const C = T.map(x => x.g[x.t].coh.find(c => c[3] === 0)).filter(Boolean);
    J.fromCoh[grp + '|' + which] = { n: T.length, fin: mean(T.map(x => x.g[x.t].king)), L300: mean(T.map(x => x.g[x.t].Lt[300])), nat: s(0), sac: s(1), oth: s(2), en: s(3), win: mean(T.map(x => x.won ? 1 : 0)) };
    fRows.push([grp, which, T.length, pct(T.filter(x => x.won).length, T.length), C.length ? f1(mean(C.map(c => c[1]))) : '–', C.length ? median(C.map(c => c[2])) : '–', C.length ? median(C.map(c => c[16])) : '–', f1(mean(T.map(x => x.g[x.t].Lt[300]))), f1(s(0)), f1(s(1)), f1(s(2)), f1(s(3)), f1(mean(T.map(x => x.g[x.t].king)))]);
  }
  out.push(md(['group', 'final king from', 'n', 'win', 'its L at r340', 'its dK at r340 (med)', 'its rank at r340 (med)', 'line L300', 'nat r300+', 'own sac r300+', 'own other', 'enemy', 'final'], fRows));
  // ------------------------------------------------------------------ Q5: the king's surroundings, deaths, tags
  out.push('\n## Q5. The line member\'s own turns from r300 (500-round maps, games to r500): enemy exposure, foraging field, company');
  const eRows = []; J.env = {};
  for (const grp of GRPS) {
    const T = sel(grp, r500full); if (!T.length) continue;
    for (let b = 0; b < 4; b++) {
      const a = new Array(9).fill(0); for (const x of T) for (let i = 0; i < 9; i++) a[i] += x.g[x.t].env[b][i];
      J.env[grp + '|' + b] = a;
      eRows.push([grp, T.length, ['r300', 'r350', 'r400', 'r450'][b], f1(a[0] / T.length), pct(a[1], a[0]), pct(a[2], a[0]), f1(a[3] / a[0]), f2(a[4] / a[0]), pct(a[5], a[0]), pct(a[6], a[0]), f2(a[7] / a[0]), f2(a[8] / a[0])]);
    }
  }
  out.push(md(['group', 'n', 'bin', 'turns/game', 'enemy head ≤3', '≤6', 'mean eD (cap 30)', 'natural pearls ≤5', 'own territory', 'team longest', 'enemy heads ≤6', 'own heads ≤6'], eRows));
  out.push('\n### Q5 deaths of own dragons L ≥ 8 that were the team longest, from r300 (per team-game; all 500-round games that reached the bin)');
  const dRows = []; J.kd = {};
  for (const grp of GRPS) {
    const T = sel(grp, x => x.g.kind === 'r500'); if (!T.length) continue;
    const row = [grp, T.length];
    for (let b = 0; b < 4; b++) {
      const lo = 300 + 50 * b, hi = lo + 50, U = T.filter(x => x.g.rounds > lo);
      const K = []; for (const x of U) for (const k of x.g[x.t].kd) if (k[0] >= lo && k[0] < hi && k[3]) K.push(k);
      const byC = c => K.filter(k => k[2] === c).length;
      J.kd[grp + '|' + b] = { n: U.length, k: K.length, len: K.reduce((s, k) => s + k[1], 0), causes: [0, 1, 2, 3, 4, 5].map(byC) };
      row.push(`${f2(K.length / U.length)} · L${f1(mean(K.map(k => k[1])))} · ram'd ${byC(2)} ram ${byC(3)} trap ${byC(1)} sac ${byC(0)}`);
    }
    dRows.push(row);
  }
  out.push(md(['group', 'team-games', 'r300', 'r350', 'r400', 'r450'], dRows));
  out.push('\n### Q5 our labels on the line member\'s turns (per 100 turns)');
  const tRows = []; J.tags = {};
  for (const grp of OURS.concat(['S58'])) {
    const T = sel(grp, r500full); if (!T.length) continue;
    const agg = [{}, {}, {}, {}];
    for (const x of T) { const lt = x.g[x.t].lineTags; if (!lt) continue; for (let b = 0; b < 4; b++) for (const [k, v] of Object.entries(lt[b])) agg[b][k] = (agg[b][k] || 0) + v; }
    J.tags[grp] = agg;
    tRows.push([grp, T.length, ...agg.map(a => { const n = a._n || 0; return ['tg', 'tgx', 'grab', 'g', 'TRADE', 'F', 'esc'].map(k => `${k} ${f1(100 * (a[k] || 0) / (n || 1))}`).join(', ') + ` (n ${n})`; })]);
  }
  out.push(md(['group', 'n', 'r300', 'r350', 'r400', 'r450'], tRows));
  const outFile = path.resolve(ROOT, opt('out', 'exp/endgame-king/report.md'));
  fs.writeFileSync(outFile, out.join('\n') + '\n');
  fs.writeFileSync(path.resolve(ROOT, opt('json', 'exp/endgame-king/numbers.json')), JSON.stringify(J));
  console.log('wrote', path.relative(ROOT, outFile), 'teams', teams.length);
}
main();
