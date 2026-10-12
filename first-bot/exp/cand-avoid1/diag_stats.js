#!/usr/bin/env node
// diag_stats.js — the bot's own state at the fatal decision, from the logged rerun of the baseline (diag-base) against
// archetype_hunter: attacker length the bot believed vs true, and the 2-step escape gate in the "sprint only" class.
// usage: node exp/cand-avoid1/diag_stats.js <ram_audit output of exp/cand-avoid1-diag>
const fs = require('fs');
function parseDiag(s) {
  if (!s) return null;
  const [left, right = ''] = s.split(' | ');
  const cands = [];
  for (const t of left.split(' ').slice(1)) {
    const m = /^([NESW]+)([!?]?):(-?[\d.]+)\/(-?[\d.]+)\/(-?[\d.]+)\/t(-?\d+),(-?\d+)\/e(\d+)$/.exec(t);
    if (m) cands.push({ dirs: m[1], flag: m[2], v: +m[3], base: +m[4], safety: +m[5], thF: +m[6], thL: +m[7] });
  }
  const gate = {}, enemies = [];
  for (const t of right.split(' ').filter(Boolean)) {
    let m;
    if ((m = /^E(\d+):(\d+)\/(\d+)\/(\d+)\/c(\d+)$/.exec(t))) enemies.push({ id: +m[1], est: +m[2], min: +m[3], vis: +m[4], cheb: +m[5] });
    else if ((m = /^([NESW]):(.*)$/.exec(t))) gate[m[1]] = m[2].match(/[NESW][-tpe]|x/g) || [];
  }
  return { cands, gate, enemies };
}
const r = JSON.parse(fs.readFileSync(process.argv[2]));
const C = r.cases, withLog = [];
for (const c of C) { const h = (c.hist || []).find(x => x.round === c.decRound); const D = h && parseDiag(h.log); if (D) withLog.push([c, D]); }
const est = {}; let over = 0, exact = 0, under = 0, notVis = 0;
for (const [c, D] of withLog) { const a = D.enemies.find(e => e.id === c.attId); if (!a) { notVis++; continue; } const k = a.est + '/' + c.attLen; est[k] = (est[k] || 0) + 1; if (a.est > c.attLen) over++; else if (a.est < c.attLen) under++; else exact++; }
console.log(`cases ${C.length}, with a log line at the fatal decision ${withLog.length}`);
console.log(`attacker length believed/true: exact ${exact}, over ${over}, under ${under}, not in the enemy list ${notVis}; pairs ${JSON.stringify(est)}`);
const so = withLog.filter(([c]) => c.cls === 'sprintOnly');
let has2 = 0, gateOpen = 0, gateClosedByThreat = 0, chosenSprint = 0;
for (const [c, D] of so) {
  if (D.cands.some(x => x.dirs.length === 2 && !x.flag)) has2++;
  const codes = Object.values(D.gate).flat();
  if (codes.some(x => x.endsWith('e'))) gateOpen++; else if (codes.some(x => x.endsWith('t'))) gateClosedByThreat++;
  if (c.act && c.act.length >= 2) chosenSprint++;
}
console.log(`sprintOnly with log ${so.length}: a 2-step candidate existed ${has2}; gate open for some second step ${gateOpen} (candidate then needs a free tile); every second step blocked by threat ${gateClosedByThreat}; we sprinted ${chosenSprint}`);
const ch = withLog.map(([c, D]) => D.cands.find(x => x.dirs === c.act)).filter(Boolean);
console.log(`chosen candidate's threat on its last tile > 0: ${ch.filter(x => x.thL > 0).length}/${ch.length}`);
