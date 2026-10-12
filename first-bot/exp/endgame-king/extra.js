#!/usr/bin/env node
// Extra tables for the endgame king study (same population rules as report.js): L>=8 deaths by cause (all own dragons of
// length >= 8 from r300, not only the team longest), the line member's enemy exposure per map, and in games whose final king
// came from the r340 non-king cohort, what happened to the r340 king.
// usage: node exp/endgame-king/extra.js [--out exp/endgame-king/extra.md]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'endgame-king');
const argv = process.argv.slice(2); const outF = argv.indexOf('--out') >= 0 ? argv[argv.indexOf('--out') + 1] : 'exp/endgame-king/extra.md';
const SETGRP = { 'cand-stack1-online': 'stack1-4', 'cand-stack2-online': 'stack1-4', 'cand-stack3-online': 'stack1-4', 'cand-stack4-online': 'stack1-4', 'cand-stack5-online': 'S58', 'cand-stack6-online': 'S58', 'cand-stack6-online-r2': 'S58', 'cand-stack7-online': 'S58', 'cand-stack8-online': 'S58', 'cand-merge2-online': 'merge2', 'cand-merge2-online-r2': 'merge2', 'cand-merge2-online-r3': 'merge2', 'baseline-r1': 'g4r4', 'baseline-r1b': 'g4r4', 'baseline-r1c': 'g4r4', 'cand-swarm8-online': 'other', 'cand-avoid6-online': 'other', 'cand-portal1-online': 'other', 'base-px8-online': 'px', 'base-px9d-online': 'px', 'px-king-v2-online': 'px' };
const R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'];
const teams = [];
for (const f of fs.readdirSync(CACHE).filter(f => f.endsWith('.jsonl'))) {
  const isTop = f.startsWith('top');
  for (const l of fs.readFileSync(path.join(CACHE, f), 'utf8').split('\n')) {
    if (!l.trim()) continue; const g = JSON.parse(l);
    if (isTop) { if (!g.winner) continue; if (['A', 'B'].some(t => g[t].splits <= 3 && g[t].sonar === 0) || g.A.faults + g.B.faults >= 3) continue; for (const t of ['A', 'B']) teams.push({ grp: t === g.winner ? 'W' : 'L', g, t }); }
    else { const grp = SETGRP[g.set]; if (!grp) continue; teams.push({ grp, g, t: g.us }); teams.push({ grp: 'X', g, t: g.us === 'A' ? 'B' : 'A' }); }
  }
}
const GR = ['W', 'L', 'X', 'g4r4', 'merge2', 'stack1-4', 'S58', 'px'];
const pct = (a, b) => b ? Math.round(100 * a / b) + '%' : '–', f2 = x => Number.isFinite(x) ? x.toFixed(2) : '–', f1 = x => Number.isFinite(x) ? x.toFixed(1) : '–';
const md = (h, rows) => ['| ' + h.join(' | ') + ' |', '|' + h.map((x, i) => i ? '---:' : '---').join('|') + '|', ...rows.map(r => '| ' + r.join(' | ') + ' |')].join('\n');
const out = ['# endgame-king extra tables (' + new Date().toISOString() + ')'];
// (a) L>=8 deaths by cause
out.push('\n## L ≥ 8 own deaths from r300 by cause (500-round maps, per team-game that reached the bin): n/game (length) — trap · rammed · ram · enemy body · ally head');
const rowsA = [];
for (const grp of GR) {
  const T = teams.filter(x => x.grp === grp && x.g.kind === 'r500'); if (!T.length) continue;
  const row = [grp, T.length];
  for (let b = 0; b < 4; b++) {
    const lo = 300 + 50 * b, U = T.filter(x => x.g.rounds > lo); const K = []; for (const x of U) for (const k of x.g[x.t].kd) if (k[0] >= lo && k[0] < lo + 50) K.push(k);
    const c = i => K.filter(k => k[2] === i).length;
    row.push(`${f2(K.length / U.length)} (L${f1(K.reduce((s, k) => s + k[1], 0) / Math.max(1, K.length))}) — ${c(1)}·${c(2)}·${c(3)}·${c(4)}·${c(5)} sac ${c(0)}`);
  }
  rowsA.push(row);
}
out.push(md(['group', 'team-games', 'r300', 'r350', 'r400', 'r450'], rowsA));
// (b) exposure per map
out.push('\n## Line member exposure per map (500-round maps, games to r500): enemy head ≤3 / ≤6 share of its turns, r300–399 and r400–499; natural pearls ≤5 per turn');
const rowsB = [];
for (const m of R500) for (const grp of ['W', 'L', 'X', 'merge2', 'stack1-4', 'S58']) {
  const T = teams.filter(x => x.grp === grp && x.g.map === m && x.g.kind === 'r500' && x.g.rounds === 500 && x.g[x.t].kid >= 0); if (!T.length) continue;
  const a = [0, 1, 2, 3].map(b => { const v = new Array(9).fill(0); for (const x of T) for (let i = 0; i < 9; i++) v[i] += x.g[x.t].env[b][i]; return v; });
  const s01 = i => a[0][i] + a[1][i], s23 = i => a[2][i] + a[3][i];
  rowsB.push([m, grp, T.length, `${pct(s01(1), s01(0))} / ${pct(s01(2), s01(0))}`, `${pct(s23(1), s23(0))} / ${pct(s23(2), s23(0))}`, f2((s01(4) + s23(4)) / (s01(0) + s23(0))), f1((s01(3) + s23(3)) / (s01(0) + s23(0)))]);
}
out.push(md(['map', 'group', 'team-games', 'r300–399 ≤3 / ≤6', 'r400–499 ≤3 / ≤6', 'pearls ≤5 per turn', 'mean eD'], rowsB));
// (c) when the final king came from the cohort: the r340 team longest's fate (from kd: a death of the team longest L>=8 from r340)
out.push('\n## Final king from the r340 non-king cohort: did a team-longest L ≥ 8 die from r340? (500-round maps, games to r500)');
const rowsC = [];
for (const grp of GR) {
  const T = teams.filter(x => x.grp === grp && x.g.kind === 'r500' && x.g.rounds === 500 && x.g[x.t].kid >= 0); if (!T.length) continue;
  for (const which of ['cohort', 'king340']) {
    const U = T.filter(x => (which === 'cohort') === x.g[x.t].coh.some(c => c[3] === 0)); if (!U.length) continue;
    const died = U.filter(x => x.g[x.t].kd.some(k => k[0] >= 340 && k[3])).length;
    const rammed = U.filter(x => x.g[x.t].kd.some(k => k[0] >= 340 && k[3] && (k[2] === 2 || k[2] === 3))).length;
    const ally = U.filter(x => x.g[x.t].kd.some(k => k[0] >= 340 && k[3] && k[2] === 5)).length;
    rowsC.push([grp, which, U.length, pct(died, U.length), pct(rammed, U.length), pct(ally, U.length)]);
  }
}
out.push(md(['group', 'final king from', 'games', 'a team-longest L≥8 died from r340', '… by an enemy head', '… by an ally head'], rowsC));
// (d) gathering root episodes whose family died by another cause: that cause, by map (S58 incl. stack8; merge2 + stack1-4)
out.push('\n## Root gathering episodes whose family died by another cause (not a sacrifice): last cause, by map (500-round maps)');
const CN = ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'];
const rowsD = [];
for (const grp of ['merge2', 'stack1-4', 'S58']) for (const m of R500) {
  const T = teams.filter(x => x.grp === grp && x.g.map === m && x.g[x.t].gath); if (!T.length) continue;
  const E = []; for (const x of T) for (const q of x.g[x.t].gath) if (!q[40]) E.push(q);
  const D = E.filter(q => !q[42] && !q[22] && !q[44] && q[43] !== 0);
  const c = {}; for (const q of D) c[CN[q[43]]] = (c[CN[q[43]]] || 0) + 1;
  const lost = D.reduce((s, q) => s + q[46], 0), toLine = D.reduce((s, q) => s + q[34], 0);
  rowsD.push([grp, m, T.length, E.length, D.length, pct(D.length, E.length), Object.entries(c).sort((a, b) => b[1] - a[1]).map(([k, v]) => k + ' ' + v).join(', '), f1(D.reduce((s, q) => s + q[2], 0) / T.length), pct(toLine, lost)]);
}
out.push(md(['group', 'map', 'games', 'root episodes', 'died other', 'share', 'last cause', 'their L0 per game', 'family drops → line'], rowsD));
// (e) labelled feed/conv events: target on the line, drops to the line, by map and by gathering flag
out.push('\n## Labelled sacrifices (feed / conv) from r300: target on the line at that moment, drops eaten by the line / by the target (500-round maps)');
const rowsE = [];
for (const grp of ['merge2', 'stack1-4', 'S58']) for (const m of R500.concat(['all'])) {
  const T = teams.filter(x => x.grp === grp && x.g.kind === 'r500' && (m === 'all' || x.g.map === m) && x.g[x.t].conv); if (!T.length) continue;
  for (const k of ['feed', 'conv']) {
    const C = []; for (const x of T) for (const v of x.g[x.t].conv) if (v[0] === k && v[6] && v[1] >= 300) C.push(v);
    if (!C.length) continue;
    const drops = C.reduce((s, v) => s + v[7], 0), line = C.reduce((s, v) => s + v[8], 0), tgt = C.reduce((s, v) => s + v[9], 0), en = C.reduce((s, v) => s + v[11], 0);
    const G = C.filter(v => v[13]);
    rowsE.push([grp, m, k, T.length, C.length, f2(C.length / T.length), pct(C.filter(v => v[12]).length, C.length), pct(line, drops), pct(tgt, drops), pct(en, drops), pct(G.length, C.length)]);
  }
}
out.push(md(['group', 'map', 'label', 'team-games', 'events', '/game', 'target on line', 'drops → line', 'drops → target', 'drops → enemy', 'by a gathering dragon'], rowsE));
// (f) exposure vs growth: the line member's share of r300-449 turns with an enemy head within Manhattan 6 (per team-game)
out.push('\n## Line exposure (share of the line member\'s r300–449 turns with an enemy head ≤ 6) and the king\'s growth (500-round maps, games to r500; Portals left out: Manhattan crosses its walls)');
const rowsF = [];
for (const grp of ['W', 'L', 'X', 'merge2', 'stack1-4', 'S58']) {
  const T = teams.filter(x => x.grp === grp && x.g.kind === 'r500' && x.g.map !== 'Portals' && x.g.rounds === 500 && x.g[x.t].kid >= 0 && x.g[x.t].Lt[300] !== undefined); if (!T.length) continue;
  const ex = x => { const e = x.g[x.t].env; const n = e[0][0] + e[1][0] + e[2][0], k = e[0][2] + e[1][2] + e[2][2]; return n ? k / n : null; };
  for (const [a, b] of [[0, 0.1], [0.1, 0.3], [0.3, 0.6], [0.6, 1.01]]) {
    const U = T.filter(x => { const v = ex(x); return v !== null && v >= a && v < b; }); if (!U.length) continue;
    const m = f => U.reduce((s, x) => s + f(x), 0) / U.length;
    const sac = x => [1, 2, 3, 4].reduce((s, bb) => s + x.g[x.t].dec[bb][1], 0), nat = x => [1, 2, 3, 4].reduce((s, bb) => s + x.g[x.t].dec[bb][0], 0);
    rowsF.push([grp, `${Math.round(a * 100)}–${Math.min(100, Math.round(b * 100))}%`, U.length, f1(m(x => x.g[x.t].Lt[300])), f1(m(nat)), f1(m(sac)), f1(m(x => x.g[x.t].king)), f2(m(x => (x.g[x.t].king - x.g[x.t].Lt[300]) / 200)), pct(U.filter(x => x.g.winner === x.t).length, U.length)]);
  }
}
out.push(md(['group', 'exposure', 'team-games', 'L300', 'nat r300+', 'own sac r300+', 'final', 'growth/round', 'win'], rowsF));
// (g) r340 cohort per map: family fates of gathered / not gathered (ours) and the elite side, last death by an enemy head
out.push('\n## r340 cohort per map (500-round maps, games to r500): family end and the share whose family\'s last death was by an enemy head (rammed / ram)');
const rowsG = [];
for (const grp of ['S58', 'stack1-4+merge2', 'X', 'W', 'L']) for (const m of R500) {
  const T = teams.filter(x => (grp === 'stack1-4+merge2' ? (x.grp === 'stack1-4' || x.grp === 'merge2') : x.grp === grp) && x.g.map === m && x.g.rounds === 500);
  for (const who of (grp === 'X' || grp === 'W' || grp === 'L') ? ['all'] : ['g', 'noG']) {
    const C = []; for (const x of T) for (const c of x.g[x.t].coh) if (who === 'all' || (who === 'g' ? c[11] > 0 : c[11] === 0)) C.push(c);
    if (!C.length) continue;
    const e2 = k => pct(C.filter(c => c[3] === k).length, C.length);
    const en = C.filter(c => (c[3] === 3 || c[3] === 4) && (c[21] === 2 || c[21] === 3)).length;
    rowsG.push([grp, m, who, C.length, e2(0), e2(1), e2(2), e2(3), e2(4), pct(en, C.length), f1(C.reduce((s, c) => s + c[1], 0) / C.length)]);
  }
}
out.push(md(['group', 'map', 'who', 'cohort', 'line', 'family alive', 'sacrificed', 'died other', 'family died after split', 'family last death by an enemy head', 'L0'], rowsG));
// (h) games in which the team lost its longest dragon (L >= 8, the longest at that moment) to an enemy head from r340
out.push('\n## Games in which the team longest (L ≥ 8) died by an enemy head (rammed / ram) from r340, and its length (500-round maps, games to r500)');
const rowsH = [];
for (const grp of ['W', 'L', 'X', 'g4r4', 'merge2', 'stack1-4', 'S58', 'px']) {
  const T = teams.filter(x => x.grp === grp && x.g.kind === 'r500' && x.g.rounds === 500 && x.g[x.t].kid >= 0); if (!T.length) continue;
  const hit = T.filter(x => x.g[x.t].kd.some(k => k[0] >= 340 && k[3] && (k[2] === 2 || k[2] === 3)));
  const L = []; for (const x of hit) for (const k of x.g[x.t].kd) if (k[0] >= 340 && k[3] && (k[2] === 2 || k[2] === 3)) L.push(k[1]);
  const ally = T.filter(x => x.g[x.t].kd.some(k => k[0] >= 340 && k[3] && k[2] === 5)).length;
  rowsH.push([grp, T.length, pct(hit.length, T.length), f1(L.reduce((a, b) => a + b, 0) / Math.max(1, L.length)), pct(ally, T.length), pct(hit.filter(x => x.g.winner === x.t).length, hit.length)]);
}
out.push(md(['group', 'team-games', 'lost the longest to an enemy head from r340', 'its length (mean)', 'lost the longest to an ally head', 'win in those games'], rowsH));
// (i) labelled feed events by 30-round bin: target on the line, drops to the line / the target (500-round maps, all games)
out.push('\n## Labelled feed by 30-round bin (500-round maps, all games): events per game, target on the line, drops to the line / to the target');
const rowsI = [];
const binI = r => r < 370 ? '340-369' : r < 400 ? '370-399' : r < 430 ? '400-429' : r < 460 ? '430-459' : '460-499';
for (const grp of ['S58', 'stack1-4', 'merge2']) {
  const T = teams.filter(x => x.grp === grp && x.g.kind === 'r500' && x.g[x.t].conv); if (!T.length) continue;
  const acc = {};
  for (const x of T) for (const v of x.g[x.t].conv) { if (v[0] !== 'feed' || !v[6] || v[1] < 340) continue; const b = binI(v[1]); const o = acc[b] || (acc[b] = [0, 0, 0, 0, 0]); o[0]++; o[1] += v[12]; o[2] += v[7]; o[3] += v[8]; o[4] += v[9]; }
  for (const b of Object.keys(acc).sort()) { const o = acc[b]; rowsI.push([grp, b, T.length, f2(o[0] / T.length), pct(o[1], o[0]), pct(o[3], o[2]), pct(o[4], o[2])]); }
}
out.push(md(['group', 'rounds', 'team-games', 'feeds/game', 'target on line', 'drops → line', 'drops → target'], rowsI));
fs.writeFileSync(path.resolve(ROOT, outF), out.join('\n') + '\n');
console.log(out.join('\n'));
