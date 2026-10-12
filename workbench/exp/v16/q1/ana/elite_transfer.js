// scratch: new-rule elite games: from r300, where do the drops of a team's own deaths go (its queen, its longest other dragon at the eat,
// another of its dragons, the enemy, nobody)? Deaths beside a longer ally (Manhattan <= 3, label-free feed proxy) separately. UNSW_RULES=123.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = '~/01. Project/개인 프로젝트/unsw-swarm';
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const ML = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const rows = fs.readFileSync(path.join(ROOT, 'data/elite/index.jsonl'), 'utf8').trim().split('\n').map(JSON.parse).filter(r => r.at >= '2026-10-01T11:08');
const T0 = 300, tot = { all: z(), beside: z() }; let games = 0, reach = 0, qAlive300 = 0;
function z() { return { deaths: 0, drops: 0, queen: 0, longest: 0, other: 0, enemy: 0 }; }
const qGrow = [];
for (const r of rows) {
  const f = path.join(ROOT, 'data/elite', String(r.battleId), r.gameId + '.replay.gz');
  if (!fs.existsSync(f)) continue;
  let R; try { R = load(f); } catch (e) { continue; }
  games++;
  const qOf = {}; for (const d of R.match.map.initialDragons) if (qOf[d.team] === undefined || d.id < qOf[d.team]) qOf[d.team] = d.id;
  const recs = new Map(); let reached = false; const q300 = {}, qEnd = {};
  try {
    ML.perGame(R, { map: r.map, variant: '?', rules: '123' }, {
      turn(d, rr, c) { if (rr >= T0 && !reached) { reached = true; for (const t of ['A', 'B']) { const q = c.drag.get(qOf[t]); q300[t] = q ? q.body.length : 0; } } },
      death(d, rec, idx, other, rr, c) {
        if (rr < T0) return;
        let beside = false; for (const o of c.drag.values()) if (o.team === d.team && o !== d && o.body.length > d.body.length && c.tdist(o.body[0], d.body[0]) <= 3) beside = true;
        recs.set(idx, { team: d.team, beside });
        for (const k of beside ? ['all', 'beside'] : ['all']) { tot[k].deaths++; tot[k].drops += rec.drops; }
      },
      eat(d, tile, idx, rr, c) {
        const x = recs.get(idx); if (!x) return;
        let cls;
        if (d.team !== x.team) cls = 'enemy';
        else if (d.id === qOf[x.team]) cls = 'queen';
        else { let best = null; for (const o of c.drag.values()) if (o.team === x.team && o.id !== qOf[x.team] && (!best || o.body.length > best.body.length)) best = o; cls = best && best.id === d.id ? 'longest' : 'other'; }
        for (const k of x.beside ? ['all', 'beside'] : ['all']) tot[k][cls]++;
      },
      end(n, c) { for (const t of ['A', 'B']) { const q = c.drag.get(qOf[t]); qEnd[t] = q ? q.body.length : 0; } },
    });
  } catch (e) { continue; }
  if (reached) { reach++; for (const t of ['A', 'B']) if (q300[t] > 0) { qAlive300++; qGrow.push(`${q300[t]}->${qEnd[t]}`); } }
}
const pc = (a, b) => b ? (100 * a / b).toFixed(0) + '%' : '-';
console.log(`games ${games}, reaching r${T0} ${reach}; queens alive at r${T0} ${qAlive300} (length r${T0}->end: ${qGrow.join(' ')})`);
for (const k of ['all', 'beside']) { const t = tot[k]; console.log(`${k === 'all' ? 'own deaths from r300' : '  beside a longer ally (<= 3)'}: ${t.deaths} deaths, ${t.drops} drops; eaten by the team's queen ${t.queen} (${pc(t.queen, t.drops)}), its longest other dragon ${t.longest} (${pc(t.longest, t.drops)}), another of its dragons ${t.other} (${pc(t.other, t.drops)}), the enemy ${t.enemy} (${pc(t.enemy, t.drops)})`); }
