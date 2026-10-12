#!/usr/bin/env node
// Who is our longest dragon at r300 and r500 on one map: a start dragon (born r0) or a child, and whether it is the
// long start dragon's escape loop (length <= 16 and head in the start corridor is not checked; we report length).
// usage: node exp/cand-swarm1/kingorigin.js <map> <label> [<label> ...]
'use strict';
const path = require('path'), fs = require('fs');
const ROOT = path.resolve(__dirname, '..', '..');
const tf = require(path.join(ROOT, 'tools', 'top_features.js')); const loader = tf.makeLoader(tf.viewerSource());
const map = process.argv[2];
for (const label of process.argv.slice(3)) {
  const dir = path.join(ROOT, 'exp', label);
  const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined && r.map === map);
  const out = { 300: { start: 0, child: 0, len: [] }, 500: { start: 0, child: 0, len: [] } };
  for (const r of rows) {
    const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
    const R = loader(file), M = R.match.map, side = r.side;
    const team = new Map(), len = new Map(), born = new Map();
    for (const d of M.initialDragons) { team.set(d.id, d.team); len.set(d.id, d.body.length); born.set(d.id, 0); }
    let round = 0, cur = -1;
    const snap = rr => { let best = -1, bl = 0; for (const [id, l] of len) if (team.get(id) === side && l > bl) { bl = l; best = id; } if (best < 0) return; out[rr][born.get(best) === 0 ? 'start' : 'child']++; out[rr].len.push(bl); };
    for (const e of R.events) {
      if (e.type === 'roundStart') { if (e.round === 300) snap(300); round = e.round; }
      else if (e.type === 'turnStart') cur = e.id;
      else if (e.type === 'dragonSplit') { team.set(e.childId, e.team); len.set(e.parentId, e.parentBody.length); len.set(e.childId, e.childBody.length); born.set(e.childId, round); }
      else if (e.type === 'tileChange' && !e.hasPearl && cur >= 0 && len.has(cur)) len.set(cur, len.get(cur) + 1);
      else if (e.type === 'dragonAction' && e.action && e.action.kind === 'move' && e.action.directions && e.action.directions.length > 1) len.set(e.id, len.get(e.id) - (e.action.directions.length - 1));
      else if (e.type === 'dragonDeath') len.delete(e.id);
    }
    if (round >= 499) snap(500);
  }
  const med = a => { const s = a.slice().sort((x, y) => x - y); return s.length ? s[Math.floor((s.length - 1) / 2)] : '-'; };
  console.log(`${label} ${map}: r300 longest is a start dragon in ${out[300].start}/${out[300].start + out[300].child} games (median length ${med(out[300].len)}); r500 ${out[500].start}/${out[500].start + out[500].child} (median ${med(out[500].len)})`);
}
