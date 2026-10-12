// paired per key on v1.8 5db1c0f (labels: v17 = the v1.8 base, q1 = +Q1, q1b = +Q1b2): our queen at r300/430/500, the backup (our longest non-queen) at r430, and at the end our longest
// living dragon (tiebreak 2) and total length; plus the queen's own feeds (sacrifices). UNSW_RULES=123.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = '~/01. Project/개인 프로젝트/unsw-swarm';
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const ML = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const SETS = {
  v17: ['exp/v16/q1/v18-king', 'exp/v16/q1/v18-hunter', 'exp/v16/q1/v18-gen'],
  q1: ['exp/v16/q1/q18-king', 'exp/v16/q1/q18-hunter', 'exp/v16/q1/q18-gen'],
  q1b: ['exp/v16/q1/q18b2-king', 'exp/v16/q1/q18b2-hunter', 'exp/v16/q1/q18b2-gen'],
};
const res = {};
for (const [v, dirs] of Object.entries(SETS)) for (const d of dirs) for (const l of fs.readFileSync(path.join(ROOT, d, 'rows.jsonl'), 'utf8').trim().split('\n')) {
  const row = JSON.parse(l), f = path.join(ROOT, d, 'games', row.key.replace(/:/g, '_'), 'game.replay');
  if (!fs.existsSync(f)) continue;
  const R = load(f), us = row.side;
  let Q = null; for (const x of R.match.map.initialDragons) if (x.team === us && (Q === null || x.id < Q)) Q = x.id;
  const g = { q300: null, q430: null, b430: null, endQ: 0, endLongest: 0, endTotal: 0, sac: 0, won: row.won };
  ML.perGame(R, { map: row.map, variant: '?', rules: '123' }, {
    turn(dd, r, c) {
      if (r === 300 && g.q300 === null) { const q = c.drag.get(Q); g.q300 = q ? q.body.length : 0; }
      if (r === 430 && g.q430 === null) { const q = c.drag.get(Q); g.q430 = q ? q.body.length : 0; let b = 0; for (const o of c.drag.values()) if (o.team === us && o.id !== Q) b = Math.max(b, o.body.length); g.b430 = b; }
    },
    indicator(e, r, c) { if (e.id === Q && /^feed #/.test(e.text || e.indicator || '')) g.sac++; },
    end(n, c) { const q = c.drag.get(Q); g.endQ = q ? q.body.length : 0; for (const o of c.drag.values()) if (o.team === us) { g.endLongest = Math.max(g.endLongest, o.body.length); g.endTotal += o.body.length; } },
  });
  (res[row.key] = res[row.key] || {})[v] = g;
}
const keys = Object.keys(res).filter(k => res[k].v17 && res[k].q1 && res[k].q1b && res[k].v17.q300 > 0);
console.log(`keys with our queen alive at r300 in v1.7 (the same in all, identity): ${keys.length}`);
console.log('key | v1.7 queen r430/end, longest end | Q1 ... | Q1b ... (b = backup at r430)');
for (const k of keys) {
  const s = v => { const g = res[k][v]; return `q ${g.q430}/${g.endQ} b ${g.b430} long ${g.endLongest} tot ${g.endTotal}${g.sac ? ' SAC' + g.sac : ''}`; };
  console.log(`${k.padEnd(40)} | ${s('v17')} | ${s('q1')} | ${s('q1b')}`);
}
const sum = (v, fn) => keys.reduce((a, k) => a + fn(res[k][v]), 0);
for (const v of ['v17', 'q1', 'q1b']) console.log(`${v}: queen alive at end ${sum(v, g => g.endQ > 0 ? 1 : 0)}/${keys.length}; queen dead at end -> our longest living (tiebreak 2) total ${sum(v, g => g.endQ > 0 ? 0 : g.endLongest)} over ${sum(v, g => g.endQ > 0 ? 0 : 1)} games; the queen's own feeds ${sum(v, g => g.sac)}`);
