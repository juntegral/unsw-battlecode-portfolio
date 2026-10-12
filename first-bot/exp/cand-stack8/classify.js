#!/usr/bin/env node
// exp/cand-stack8/classify.js <study.json>... — failure classes of F targets and portal crossings (cand-stack8 pre-study)
'use strict';
const fs = require('fs');
const games = [].concat(...process.argv.slice(2).filter(a => !a.startsWith('--')).map(f => JSON.parse(fs.readFileSync(f, 'utf8'))));
const pct = (a, b) => b ? (100 * a / b).toFixed(0) + '%' : '–';
const GATHER_START = 340;
const cnt = () => new Map(); const inc = (m, k, v = 1) => m.set(k, (m.get(k) || 0) + v);
const show = (title, m, tot) => { console.log(`\n${title} (N=${tot})`); for (const [k, v] of [...m.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${k.padEnd(60)} ${String(v).padStart(6)}  ${pct(v, tot)}`); };

// ---------------- F
const fAll = [], fCls = cnt(), fClsMap = new Map(), ex = [];
let nEp = 0, nSit = 0, nArr = 0;
for (const g of games) {
  const X = g.X, W = X.W;
  const ourT = g.us === 'A' ? 1 : 2;
  const tagsBy = new Map(); for (const [id, r, a, d] of X.ftags) { if (!tagsBy.has(id)) tagsBy.set(id, []); tagsBy.get(id).push([r, a, d]); }
  const fTargetsAt = new Map(); // r:a -> ids tagging it
  for (const [id, r, a] of X.ftags) { const k = r + ':' + a; if (!fTargetsAt.has(k)) fTargetsAt.set(k, new Set()); fTargetsAt.get(k).add(id); }
  for (const x of g.recs.filter(y => y.k === 'fguard')) {
    nEp++;
    const ff = X.fFirst[x.id + ':' + x.a] || {};
    const home = X.home[x.id] || [];
    const dz = X.deaths[x.id];
    let cls;
    if (!x.sit) {
      if (!x.fnt) cls = 'S1 not a true fountain';
      else if (!x.own) {
        const t = ff.terrA;
        const homeOwn = home[1] === ourT ? 'born in our territory' : home[1] === 0 ? 'born neutral' : 'born in enemy territory';
        cls = `S2 not our territory (${t === 0 ? 'neutral' : 'enemy'} tile; dragon ${homeOwn})`;
      } else {
        // another head of ours within 3 at the first tag: nearer / as near / farther than us (the bot's rule takes it if we are nearer)
        const o3 = (ff.others || []).filter(o => o[1] <= 3);
        const nearer = o3.some(o => o[1] < ff.mine), same = o3.some(o => o[1] === ff.mine);
        const alsoF = o3.some(o => { for (let dr = -3; dr <= 3; dr++) { const s = fTargetsAt.get((x.r + dr) + ':' + x.a); if (s && s.has(o[0])) return true; } return false; });
        const vis = o3.some(o => o[3]);
        cls = `S3 other head ≤3 (${nearer ? 'it is nearer' : same ? 'as near' : 'we are nearer'}${alsoF ? ', it F-tags the same fountain' : ''}${vis ? ', in our view' : ', out of view'})`;
      }
    } else if (!x.ex) {
      // designed situation, never arrived
      const tags = tagsBy.get(x.id) || [];
      const after = tags.filter(t => t[0] > x.r1);
      const nextT = after.length ? after[0] : null;
      const midSwitch = tags.some(t => t[0] > x.r && t[0] < x.r1 && t[1] !== x.a);
      if (dz && dz.r <= x.r1 + 2) cls = `N1 died on the way (${['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'][dz.cause]})`;
      else if (x.r1 >= g.rounds - 2) cls = 'N5 game ended while chasing';
      else if (nextT && nextT[1] !== x.a && nextT[0] <= x.r1 + 3) cls = midSwitch ? 'N2 swapped target (alternating)' : 'N2 swapped target';
      else {
        const r1 = x.r1 + 1;
        const u = X.units[r1], k = X.kingId[r1];
        const lbl = X.labels[x.id + ':' + r1] || '';
        if (r1 >= GATHER_START - 1) cls = 'N3 goal off: gathering (r>=340)';
        else if (u !== undefined && u < 3) cls = 'N3 goal off: < 3 units';
        else if (k && k[0] === x.id && k[1] >= 8) cls = 'N3 goal off: became king';
        else if (/^(split|csplit|escape|esc-split|feed|pocket)/.test(lbl)) cls = 'N4 other action next turn (' + lbl.split(/[\s0-9]/)[0] + ')';
        else if (/ g\d| K\d/.test(lbl)) cls = 'N3 goal off: gather goal';
        else if (nextT && nextT[1] === x.a) cls = 'N6 same target later (gap), never within 3';
        else cls = 'N3 goal off: other (guarded by an ally / beyond 20 / dropped)';
      }
      if (midSwitch && !/N2/.test(cls)) cls += ' [alternating]';
    } else { cls = 'OK arrived (designed situation)'; nArr++; }
    if (x.sit) nSit++;
    inc(fCls, cls);
    if (!fClsMap.has(x.map)) fClsMap.set(x.map, cnt()); inc(fClsMap.get(x.map), cls.slice(0, 2));
    fAll.push({ cls, map: x.map, game: g.game, set: g.set, r: x.r, id: x.id, L: x.L, a: [x.ax, x.ay], d0: x.d0, mine: ff.mine, others: ff.others, eNear: ff.enemyNear, r1: x.r1, turns: x.turns });
  }
}
console.log(`games ${games.length}; F episodes ${nEp}; designed ${nSit} (${pct(nSit, nEp)}); designed & arrived ${nArr} (${pct(nArr, nSit)} of designed)`);
show('F episode classes', fCls, nEp);
// top-level class by map
console.log('\nF classes by map (S1..S3 = outside the designed situation, N* = designed but never arrived, OK)');
const heads = ['S1', 'S2', 'S3', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'OK'];
console.log('  ' + 'map'.padEnd(26) + heads.map(h => h.padStart(6)).join('') + '     N');
for (const [m, c] of [...fClsMap.entries()].sort()) { const tot = [...c.values()].reduce((s, v) => s + v, 0); console.log('  ' + m.padEnd(26) + heads.map(h => String(c.get(h) || 0).padStart(6)).join('') + String(tot).padStart(6)); }
// never-arrived designed episodes: first distance and duration
const na = fAll.filter(x => /^N/.test(x.cls));
const byD = cnt(); for (const x of na) inc(byD, x.d0 <= 3 ? 'd0<=3' : x.d0 <= 6 ? 'd0 4-6' : x.d0 <= 10 ? 'd0 7-10' : 'd0 11+');
show('never arrived: first distance (bot label)', byD, na.length);
const byT = cnt(); for (const x of na) inc(byT, x.turns <= 1 ? '1 tagged turn' : x.turns <= 3 ? '2-3 turns' : x.turns <= 10 ? '4-10 turns' : '11+ turns');
show('never arrived: tagged turns', byT, na.length);
const byE = cnt(); for (const x of na) inc(byE, x.eNear <= 3 ? 'enemy head <=3 of target at first tag' : x.eNear <= 6 ? 'enemy head 4-6' : 'no enemy head within 6');
show('never arrived: enemy head near target at first tag', byE, na.length);
if (process.argv.includes('--cases')) { for (const c of [...new Set(fAll.map(x => x.cls))]) { console.log('\n# ' + c); for (const x of fAll.filter(y => y.cls === c).slice(0, 4)) console.log('  ', JSON.stringify(x)); } }

// ---------------- portal
const pCls = cnt(), pMap = new Map(); let nX = 0, nF = 0;
const pCases = [];
for (const g of games) {
  const X = g.X;
  const crossAt = new Map(); for (const c of X.cross) crossAt.set(c.id + ':' + c.r, c);
  for (const x of g.recs.filter(y => y.k === 'portal')) {
    nX++;
    if (x.alive3) continue;
    nF++;
    const c = crossAt.get(x.id + ':' + x.r) || {}, dz = X.deaths[x.id];
    let cls;
    const lbl = X.labels[x.id + ':' + x.r] || '';
    if (!dz) cls = 'Z no death record';
    else if (c.fate && dz.r === x.r && c.fate.step >= c.stepI) {
      // died on this move at or after the portal step
      const onExit = c.fate.step === c.stepI;
      const who = c.fate.hitTeam === 'us' ? 'own' : c.fate.hitTeam === 'them' ? 'enemy' : 'none';
      const what = c.fate.reason === 'H' ? 'head' : c.fate.reason === 'O' ? 'body' : c.fate.reason === 'S' ? 'own body (self)' : c.fate.reason === 'W' ? 'kelp' : 'sprint';
      cls = `C ${onExit ? 'exit tile' : 'after exit, same move'}: ${who} ${what}`;
    } else {
      const cause = ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'][dz.cause];
      const dt = dz.r - x.r;
      let why = cause;
      if (dz.cause === 2) why = `rammed by enemy (enemy head ${c.eH <= 2 ? '<=2' : c.eH <= 4 ? '3-4' : '5+'} of exit at crossing)`;
      if (dz.cause === 1) why = `trapped (room4 after crossing ${c.room4 <= 3 ? '<=3' : c.room4 <= 8 ? '4-8' : '9+'})`;
      if (dz.cause === 0) why = /^feed|conv/.test(X.labels[x.id + ':' + dz.r] || '') ? 'sac (feed/conv label)' : 'sac (other)';
      cls = `L later (+${dt <= 1 ? '0-1' : '2-3'}): ${why}`;
    }
    inc(pCls, cls);
    if (!pMap.has(x.map)) pMap.set(x.map, cnt()); inc(pMap.get(x.map), cls.split(':')[0]);
    pCases.push({ cls, map: x.map, game: g.game, r: x.r, id: x.id, L: x.L, blind: x.blind, v: x.v, c, dz, lbl });
  }
}
console.log(`\nportal crossings ${nX}; body dead within 3 rounds ${nF} (${pct(nF, nX)})`);
show('portal failure classes', pCls, nF);
console.log('\nportal failures by map');
for (const [m, c] of [...pMap.entries()].sort()) console.log('  ' + m.padEnd(26) + [...c.entries()].map(([k, v]) => `${k} ${v}`).join(' · '));
// own-blocked exit deaths: what the dragon could know (own head distance to exit at the crossing, blind label, probe)
const own = pCases.filter(x => /^C .*own/.test(x.cls));
const oc = cnt(); for (const x of own) inc(oc, `${x.blind ? 'PORTAL? (unexplored)' : 'known portal'}; own head ${x.c.oH <= 1 ? '<=1' : x.c.oH <= 3 ? '2-3' : '4+'} of exit; v ${x.v !== null && x.v <= -20 ? '<=-20 (desperate)' : '> -20'}`);
show('own-blocked crossing deaths: context', oc, own.length);
const enemyC = pCases.filter(x => /enemy/.test(x.cls));
const ec = cnt(); for (const x of enemyC) inc(ec, `${x.blind ? 'PORTAL?' : 'known'}; enemy head ${x.c.eH <= 2 ? '<=2' : x.c.eH <= 4 ? '3-4' : '5+'} of exit; L ${x.L <= 3 ? '<=3' : x.L <= 6 ? '4-6' : '7+'}; eL ${x.c.eHL >= x.L ? '>=ours' : '<ours'}`);
show('enemy-related failures: context', ec, enemyC.length);
if (process.argv.includes('--pcases')) for (const c of [...new Set(pCases.map(x => x.cls))]) { console.log('\n# ' + c); for (const x of pCases.filter(y => y.cls === c).slice(0, 5)) console.log('  ', JSON.stringify({ map: x.map, game: x.game, r: x.r, id: x.id, L: x.L, blind: x.blind, v: x.v, lbl: x.lbl, c: x.c, dz: x.dz })); }

// ---------------- F pull-away (coordinator 18:0x): an F-tagged move that raises our path distance to a natural pearl we are the unique
// nearest head to (within 7, outside the target group); the pearl's first eater after the move
{
  let nTurns = 0, nCandTurns = 0, nPull = 0; const fate = cnt(), byMap = new Map(), epPull = new Set(); let nEpAll = 0;
  for (const g of games) {
    const X = g.X; nEpAll += g.recs.filter(y => y.k === 'fguard').length;
    const eatsBy = new Map(); for (const [t, r, tm, id] of X.natEat) { if (!eatsBy.has(t)) eatsBy.set(t, []); eatsBy.get(t).push([r, tm, id]); }
    nTurns += X.ftags.length;
    const turnsWithCand = new Set(X.pull.map(p => p[0] + ':' + p[1])); nCandTurns += turnsWithCand.size;
    const pulledTurns = new Set();
    for (const [id, r, a, k, dm, d2, ate, mv] of X.pull) {
      if (ate || d2 <= dm) continue;
      pulledTurns.add(id + ':' + r); epPull.add(g.key + ':' + id + ':' + a);
      const ev = (eatsBy.get(k) || []).find(e => e[0] >= r);
      const who = !ev ? 'nobody (still there / game end)' : ev[1] === 2 ? 'enemy' : ev[2] === id ? 'this dragon later' : 'another of ours';
      inc(fate, who); if (!byMap.has(g.map)) byMap.set(g.map, [0, 0]); byMap.get(g.map)[0]++; if (who === 'enemy') byMap.get(g.map)[1]++;
    }
    nPull += pulledTurns.size;
  }
  console.log(`\nF pull-away: F-tagged turns ${nTurns}; with a uniquely-nearest natural pearl within 7 outside the group ${nCandTurns} (${pct(nCandTurns, nTurns)}); turns that moved away from one ${nPull} (${pct(nPull, nTurns)}); F episodes with >=1 such turn ${epPull.size} / ${nEpAll} (${pct(epPull.size, nEpAll)})`);
  const tot = [...fate.values()].reduce((s, v) => s + v, 0);
  show('pull-away pearls: first eater after the move', fate, tot);
  console.log('  by map (pull-away pearls · eaten by the enemy): ' + [...byMap.entries()].map(([m, v]) => `${m} ${v[0]}·${v[1]}`).join(' | '));
}
// ---------------- portal: probe status of the failures by class
{
  const pc = cnt(); const allP = cnt(); let n = 0;
  for (const g of games) for (const cr of g.X.cross) inc(allP, cr.probe && cr.probe.startsWith('dirty') ? 'dirty' : cr.probe || '?');
  show('all crossings: probe of the previous round (from that tile, that direction)', allP, [...allP.values()].reduce((s, v) => s + v, 0));
  for (const x of pCases) { n++; inc(pc, `${x.cls.slice(0, 40).padEnd(40)} | ${x.blind ? 'PORTAL?' : 'known'} | probe ${x.c.probe && x.c.probe.startsWith('dirty') ? 'dirty' : x.c.probe}`); }
  show('portal failures: class x exit kind x probe', pc, n);
}
