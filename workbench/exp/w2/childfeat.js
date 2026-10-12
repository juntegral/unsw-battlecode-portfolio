#!/usr/bin/env node
// W2 child-delay cost by mechanism (coordinator 15:15, user principle 14:37): which features our split children run in their first K own turns, per
// map, for two sets on the same keys (v1.6 vs v1.6.1). A held child runs DEFAULT F0 (label E=F) without the row's features. Features: the row's
// engine label (E=S swarm, E=W the W4 economy; Portals keeps E=F and is seen by " pt"), " pt" (Portals module), " sd" (swarm dispersal target),
// " hv" (pocket harvest), " ck" / " cp" / " cy" (CONV2), " sx" / " sr" (explosion / re-split). Also the children's turns in their first K
// turns, so the rates are per child-turn.
// usage: node exp/w2/childfeat.js <setA> <setB> [--k 10]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), ki = args.indexOf('--k'), K = ki >= 0 ? +args[ki + 1] : 10;
const sets = args.filter((a, i) => !a.startsWith('--') && (ki < 0 || i !== ki + 1));
const FEAT = { S: / E=S$/, W: / E=W$/, F: / E=F$/, pt: / pt(?= |$)/, sd: / sd/, hv: / hv/, cv2: / c[kpy][#=0-9]/, sx: / sx/, sr: / sr/ };
const res = {};
for (const set of sets) {
  const rows = fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => r.G !== undefined && !r.error);
  for (const r of rows) {
    const R = load(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'));
    const us = r.side, n0 = R.match.map.initialDragons.length;
    const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
    const seen = new Map();
    const A = ((res[r.map] = res[r.map] || {})[set] = res[r.map][set] || { kids: 0, turns: 0, feat: {} });
    for (const e of R.events) {
      if (e.type === 'dragonSplit') { team.set(e.childId, e.team); if (e.team === us) A.kids++; }
      else if (e.type === 'dragonIndicator' && team.get(e.id) === us && e.id >= n0) {
        const c = seen.get(e.id) || 0; if (c >= K) continue; seen.set(e.id, c + 1);
        A.turns++;
        for (const [k, re] of Object.entries(FEAT)) if (re.test(e.text || '')) A.feat[k] = (A.feat[k] || 0) + 1;
      }
    }
  }
}
const pc = (a, b) => b ? (100 * a / b).toFixed(1) : '-';
console.log(`children's first ${K} turns: share of child-turns with each feature (${sets.join(' vs ')})`);
console.log(`${'map'.padEnd(18)} ${Object.keys(FEAT).map(k => k.padStart(13)).join('')}`);
for (const [m, bySet] of Object.entries(res).sort()) {
  const cells = Object.keys(FEAT).map(k => sets.map(s => pc((bySet[s] || { feat: {} }).feat[k] || 0, (bySet[s] || {}).turns)).join('→').padStart(13));
  console.log(`${m.padEnd(18)} ${cells.join('')}   (child-turns ${sets.map(s => (bySet[s] || {}).turns || 0).join(' / ')})`);
}
