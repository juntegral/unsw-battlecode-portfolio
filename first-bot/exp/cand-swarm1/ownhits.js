#!/usr/bin/env node
// Collisions between our own dragons in an eval.js label: for each head-on with an ally (both ours) and each move into
// an ally's body, the mover's last indicator kind. usage: node exp/cand-swarm1/ownhits.js <label>
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
const loader = tf.makeLoader(tf.viewerSource());
const label = process.argv[2], dir = path.join(ROOT, 'exp', label);
const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined);
const kind = t => { if (!t) return 'none'; const w = t.split(' ')[0]; if (/^[NESW]+$/.test(w)) return t.includes('TRADE') ? 'trade' : (w.length > 1 ? 'sprint' : 'move'); return w.replace(/[-]?\d+$/, ''); };
const agg = { Hown: {}, Oown: {} }; let games = 0;
const add = (o, k) => { o[k] = (o[k] || 0) + 1; };
for (const r of rows) {
  const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
  const R = loader(file), M = R.match.map, side = r.side; games++;
  const team = new Map(), body = new Map();
  for (const d of M.initialDragons) { team.set(d.id, d.team); body.set(d.id, d.body.map(s => s.x + ',' + s.y)); }
  let cur = -1; const last = new Map(); let turnDeaths = [];
  const flush = () => {
    // head-on: two H deaths in the same turn, the mover is `cur`
    const H = turnDeaths.filter(d => d.reason === 'H');
    if (H.length >= 2 && team.get(cur) === side) { const other = H.find(d => d.id !== cur); if (other && team.get(other.id) === side) add(agg.Hown, kind(last.get(cur))); }
    for (const d of turnDeaths) if (d.reason === 'O' && d.id === cur && team.get(cur) === side && d.hitOwn) add(agg.Oown, kind(last.get(cur)));
    turnDeaths = [];
  };
  let lastHead = new Map();
  for (const e of R.events) {
    if (e.type === 'turnStart') { flush(); cur = e.id; }
    else if (e.type === 'dragonSplit') { team.set(e.childId, e.team); body.set(e.parentId, e.parentBody.map(s => s.x + ',' + s.y)); body.set(e.childId, e.childBody.map(s => s.x + ',' + s.y)); }
    else if (e.type === 'dragonIndicator') last.set(e.id, e.text);
    else if (e.type === 'dragonUpdate') {
      const b = body.get(e.id); if (!b) continue; const h = e.head.x + ',' + e.head.y, t = e.tail.x + ',' + e.tail.y;
      b.unshift(h); while (b.length > 1 && b[b.length - 1] !== t) b.pop();
    }
    else if (e.type === 'dragonAction' && e.id === cur && e.action && e.action.kind === 'move') { lastHead.set(cur, e.action); }
    else if (e.type === 'dragonDeath') {
      const d = { id: e.id, reason: e.reason };
      if (e.reason === 'O' && e.id === cur) {
        // which body was hit: the tile the head tried to enter is not recorded; approximate by any ally body adjacent to the head
        const b = body.get(cur); const h = b ? b[0] : null; let own = false;
        if (h) { const [x, y] = h.split(',').map(Number); const W = M.width, H2 = M.height; const nb = [[x, y - 1], [x + 1, y], [x, y + 1], [x - 1, y]].map(([a, c]) => ((a % W) + W) % W + ',' + ((c % H2) + H2) % H2);
          for (const [id, bb] of body) if (id !== cur && team.get(id) === side && bb.some(s => nb.includes(s))) own = true; }
        d.hitOwn = own;
      }
      turnDeaths.push(d); body.delete(e.id);
    }
  }
  flush();
}
const per = o => Object.entries(o).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${(v / games).toFixed(2)}`).join(', ');
console.log(`${label}: ${games} games`);
console.log('head-on with an ally, mover intent (per game):', per(agg.Hown));
console.log('into a body next to an ally (per game, approx):', per(agg.Oown));
