#!/usr/bin/env node
// v1.1 diagnostic: how sd targets are held. Per our dragon, consecutive turns with an " sd<d>@x,y" tag form target spells (same x,y); a spell
// ends when the target changes or the tag stops. Reached = the goal distance fell to <= FG_HOLD (2) during the spell. Also the spells by the
// target's frontier bin (" f<b>", v1.1 only) and their length in turns. usage: node exp/v11/sdflip.js <evalDir>[,<evalDir>] [--label x]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const dirs = process.argv[2].split(','), label = (() => { const i = process.argv.indexOf('--label'); return i > 0 ? process.argv[i + 1] : dirs.join('+'); })();
const agg = { spells: 0, reached: 0, turns: 0, startD: 0, byBin: {}, early: { spells: 0, reached: 0, turns: 0 } };
for (const dir of dirs) {
  const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined);
  for (const r of rows) {
    const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
    const R = load(file), team = new Map(R.match.map.initialDragons.map(d => [d.id, d.team]));
    let round = -1; const cur = new Map();
    const close = (id) => { const s = cur.get(id); if (!s) return; cur.delete(id);
      agg.spells++; agg.turns += s.n; agg.startD += s.d0; if (s.min <= 2) agg.reached++;
      const b = agg.byBin[s.b] || (agg.byBin[s.b] = { spells: 0, reached: 0, turns: 0, d0: 0 }); b.spells++; b.turns += s.n; b.d0 += s.d0; if (s.min <= 2) b.reached++;
      if (s.r0 < 100) { agg.early.spells++; agg.early.turns += s.n; if (s.min <= 2) agg.early.reached++; } };
    for (const e of R.events) {
      if (e.type === 'roundStart') round = e.round;
      else if (e.type === 'dragonSplit') team.set(e.childId, e.team);
      else if (e.type === 'dragonDeath') close(e.id);
      else if (e.type === 'dragonIndicator' && team.get(e.id) === r.side) {
        const m = / sd(\d+)@(\d+),(\d+)[ou](?: f(\d))?/.exec(e.text || '');
        if (!m) { close(e.id); continue; }
        const k = m[2] + ',' + m[3], d = +m[1], s = cur.get(e.id);
        if (s && s.k === k) { s.n++; s.min = Math.min(s.min, d); continue; }
        close(e.id); cur.set(e.id, { k, n: 1, d0: d, min: d, b: m[4] === undefined ? '-' : m[4], r0: round });
      }
    }
    for (const id of [...cur.keys()]) close(id);
  }
}
const pc = (a, n) => n ? (100 * a / n).toFixed(0) + '%' : '–';
console.log(`${label}: target spells ${agg.spells}, reached (goal distance <= 2) ${pc(agg.reached, agg.spells)}, mean spell ${(agg.turns / agg.spells).toFixed(1)} turns, mean start distance ${(agg.startD / agg.spells).toFixed(1)}; before r100: ${agg.early.spells} spells, reached ${pc(agg.early.reached, agg.early.spells)}, mean ${(agg.early.turns / agg.early.spells).toFixed(1)} turns`);
for (const [b, x] of Object.entries(agg.byBin).sort()) console.log(`  bin ${b}: spells ${x.spells}, reached ${pc(x.reached, x.spells)}, mean spell ${(x.turns / x.spells).toFixed(1)} turns, start distance ${(x.d0 / x.spells).toFixed(1)}`);
