#!/usr/bin/env node
// Stage 3 (close reading): one online game told round by round from the replay (mass-ledger reconstruction + our labels).
// usage: node exp/eliminations/film.js <set> <gameId> [--from R] [--to R] [--dragons] [--all-deaths]
//   Prints: per 10 rounds our / their units, total, longest, heads by territory, deaths by mode; our dragons that mattered
//   (reached length 5 or lived 30 rounds) with their label kinds; every non-stub death of ours in the window with the killer and
//   its last labels; the opponent's deaths caused by us in the window.
// Board views of one moment: node exp/mech-failures/show.js <set> <gameId> <dragonId> <round>
'use strict';
const fs = require('fs'), path = require('path');
const L = require('./lib.js');
const X = require('./extract.js');
const { makeLoader, viewerSource } = require(path.join(L.ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(L.ROOT, 'tools', 'mass_ledger.js'));

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const [set, gameId] = argv.filter((a, i) => !a.startsWith('--') && !['--from', '--to'].includes(argv[i - 1]));
const task = X.onlineTasks(set).find(t => String(t.gameId) === String(gameId));
if (!task) { console.error('no such game'); process.exit(2); }
const R = makeLoader(viewerSource())(task.file);
const rec = X.analyse(R, task, perGame);
const us = rec.us, them = us === 'A' ? 'B' : 'A';
const g = Object.assign(rec, { U: rec.T[us], E: rec.T[them] });
const elim = g.U.elim;
const from = +opt('from', elim >= 0 ? Math.max(0, elim - 60) : 0), to = +opt('to', elim >= 0 ? elim : g.rounds);
const cls = elim >= 0 ? L.classOf(elim, g.U.kd) : '-';
console.log(`# ${set} ${gameId}  ${L.mapLay(g)}  vs ${task.opp}  bot ${L.BOT[set]}  winner ${g.winner === us ? 'US' : 'THEM'} (${g.endReason}, ${g.rounds} rounds)  our elim r${elim}  class ${cls}`);
console.log(`final: us u${g.U.end.u} t${g.U.end.t} k${g.U.end.k} | them u${g.E.end.u} t${g.E.end.t} k${g.E.end.k} ; lineage us ${JSON.stringify(g.ml[us].lin)} them ${JSON.stringify(g.ml[them].lin)}`);

// per 10 rounds
const rowOf = d => [d.r, d.len, d.cause, d.ks, d.eV, d.aV, d.king, d.klen, d.kage, d.u, d.eu, d.blk, d.eMin, d.portal, d.mech];
const MODES = ['sprintRam', 'stepRam', 'ourRam', 'trapE', 'trapSelf', 'enemyBody', 'sac', 'allyHead', 'stub'];
const ab = { sprintRam: 'sR', stepRam: 'R1', ourRam: 'oR', trapE: 'tE', trapSelf: 'tS', enemyBody: 'eB', sac: 'sac', allyHead: 'aH', stub: 'stub' };
console.log('\n r   | us u  t  k | them u  t  k | our heads own/neu/en | their heads in ours | our deaths (mode:n)            | their deaths by us');
for (let r = 0; r < g.rounds; r += 10) {
  const p = g.U.pos.find(x => x[0] === r) || [], q = g.E.pos.find(x => x[0] === r) || [];
  const D = g.deaths.filter(d => d.r >= r && d.r < r + 10), cnt = {};
  for (const d of D) { const m = ab[L.modeOf(rowOf(d))] || '?'; cnt[m] = (cnt[m] || 0) + 1; }
  const O = g.oppDeaths.filter(d => d[0] >= r && d[0] < r + 10 && (d[2] === 2 || d[2] === 3 || d[2] === 4)).length;
  console.log(`${String(r).padStart(4)} | ${String(L.at(g, us, r, 'u')).padStart(4)} ${String(L.at(g, us, r, 't')).padStart(3)} ${String(L.at(g, us, r, 'k')).padStart(2)} | ${String(L.at(g, them, r, 'u')).padStart(6)} ${String(L.at(g, them, r, 't')).padStart(3)} ${String(L.at(g, them, r, 'k')).padStart(2)} | ${(p.length ? `${p[2]}/${p[3]}/${p[4]}` : '-').padStart(20)} | ${String(q.length ? q[4] : '-').padStart(19)} | ${Object.entries(cnt).map(([k, v]) => k + ':' + v).join(' ').padEnd(30)} | ${O}`);
}

// our dragons that mattered, with label kinds (re-read the replay for per-dragon labels)
if (argv.includes('--dragons')) {
  const labs = new Map(), lens = new Map();
  perGame(R, { map: task.map, variant: task.map === 'Prisoners Dilemma' ? (R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6') : undefined }, {
    indicator(e, r, c) { const d = c.drag.get(e.id); if (!d || d.team !== us) return; let m = labs.get(e.id); if (!m) labs.set(e.id, m = {}); for (const t of X.tokens(e.text)) m[t] = (m[t] || 0) + 1; },
    turn(d, r) { if (d.team !== us) return; const x = lens.get(d.id) || { max: 0, first: r, last: r }; x.max = Math.max(x.max, d.body.length); x.last = r; lens.set(d.id, x); },
  });
  console.log('\nour dragons (max length >= 5 or lived >= 30 rounds): id born parent bornLen maxLen death cause | label kinds');
  for (const d of g.ourDrg) {
    const x = lens.get(d.id) || { max: d.maxLen }; const life = (d.death === null ? g.rounds : d.death) - d.born;
    if (x.max < 5 && life < 30) continue;
    const m = labs.get(d.id) || {};
    const top = Object.entries(m).filter(([k]) => !['single', 'move'].includes(k)).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([k, v]) => k + ':' + v).join(' ');
    console.log(`  #${d.id} born r${d.born} parent ${d.parent} L${d.bornLen} max ${x.max} ${d.death === null ? 'alive' : 'died r' + d.death + ' ' + L.CAUSE[d.cause]} | moves ${m.move || 0} ${top}`);
  }
}

// our deaths in the window
console.log(`\nour deaths r${from}-${to} (stubs ${argv.includes('--all-deaths') ? 'shown' : 'hidden'}): r id len mode | killer len steps age | eV aV eMin | our units / theirs | last labels`);
for (const d of g.deaths.filter(d => d.r >= from && d.r <= to)) {
  const m = L.modeOf(rowOf(d)); if (m === 'stub' && !argv.includes('--all-deaths')) continue;
  console.log(`  r${d.r} #${d.id} L${d.len} ${L.MODE_KO[m]}${d.king ? ' (왕)' : ''} | ${d.kid >= 0 ? `#${d.kid} L${d.klen} ${d.ks}걸음 나이${d.kage}` : '-'} | eV${d.eV} aV${d.aV} e${d.eMin} | ${d.u}/${d.eu} | ${(d.lbls || []).map(x => 'r' + x[0] + ' ' + x[1]).join(' ; ')}`);
}
const kdE = g.E.kd.filter(d => d[0] >= from && d[0] <= to);
if (kdE.length) console.log(`their L>=8 deaths in the window: ${kdE.map(d => `r${d[0]} L${d[1]} ${L.MODE_KO[L.modeOf(d)]}${d[6] ? ' (왕)' : ''}`).join(' ; ')}`);
// label kinds per 50 rounds
console.log('\nour label kinds per 50 rounds:');
for (let b = 0; b < 10; b++) {
  const c = {}; for (let i = b * 5; i < b * 5 + 5; i++) for (const [k, v] of Object.entries(g.lab[i] || {})) c[k] = (c[k] || 0) + v;
  const s = Object.entries(c).filter(([k]) => !['move', 'single'].includes(k)).sort((a, b2) => b2[1] - a[1]).map(([k, v]) => k + ':' + v).join(' ');
  if (c.move || s) console.log(`  r${b * 50}-${b * 50 + 49}: moves ${c.move || 0} ${s}`);
}
