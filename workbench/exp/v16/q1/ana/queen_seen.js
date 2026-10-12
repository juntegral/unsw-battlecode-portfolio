// scratch: at r430, is each team's ENEMY queen alive, and when did any of the team's heads last have her head in its 7x7 view (Chebyshev <= 3,
// torus)? Elite new-rule games, or our local run dirs (rows.jsonl + games/<key>/game.replay). UNSW_RULES=123 for 1.2.3 free steps.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = '~/01. Project/개인 프로젝트/unsw-swarm';
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const ML = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const T = 430, args = process.argv.slice(2);
const files = [];
if (args[0] === 'elite') {
  const rows = fs.readFileSync(path.join(ROOT, 'data/elite/index.jsonl'), 'utf8').trim().split('\n').map(JSON.parse).filter(r => r.at >= '2026-10-01T11:08');
  for (const r of rows) files.push({ f: path.join(ROOT, 'data/elite', String(r.battleId), r.gameId + '.replay.gz'), map: r.map, teams: ['A', 'B'] });
} else for (const d of args) for (const l of fs.readFileSync(path.join(d, 'rows.jsonl'), 'utf8').trim().split('\n')) {
  const row = JSON.parse(l); files.push({ f: path.join(d, 'games', row.key.replace(/:/g, '_'), 'game.replay'), map: row.map, teams: [row.side] });
}
const out = { alive: [], dead: 0, deadSeenLate: 0 };
for (const g of files) {
  if (!fs.existsSync(g.f)) continue;
  let R; try { R = load(g.f); } catch (e) { continue; }
  const init = R.match.map.initialDragons, qOf = {};
  for (const d of init) if (qOf[d.team] === undefined || d.id < qOf[d.team]) qOf[d.team] = d.id;
  const last = { A: -1, B: -1 }, aliveAt = {};
  try {
    ML.perGame(R, { map: g.map, variant: '?', rules: '123' }, {
      turn(d, r, c) {
        if (r > T) return;
        for (const t of ['A', 'B']) {
          const eq = c.drag.get(qOf[t === 'A' ? 'B' : 'A']); if (!eq) continue;
          if (d.team === t && c.cheb(d.body[0], eq.body[0]) <= 3) last[t] = r;
        }
        if (r === T) for (const t of ['A', 'B']) aliveAt[t] = c.drag.has(qOf[t]);
      },
    });
  } catch (e) { continue; }
  for (const t of g.teams) {
    const e = t === 'A' ? 'B' : 'A';
    if (aliveAt[e] === undefined) continue;   // the game ended before r430
    if (aliveAt[e]) out.alive.push(last[t] < 0 ? 'never' : T - last[t]); else { out.dead++; if (last[t] >= T - 50) out.deadSeenLate++; }
  }
}
const a = out.alive, seen50 = a.filter(x => x !== 'never' && x <= 50).length;
console.log(`team views at r${T}: enemy queen alive ${a.length} (seen within the last 50 rounds ${seen50}; rounds since last seen: ${a.map(String).sort().join(',')}), dead ${out.dead} (of which seen within the last 50 rounds before r${T} ${out.deadSeenLate})`);
