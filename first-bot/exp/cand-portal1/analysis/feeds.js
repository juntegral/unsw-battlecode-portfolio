// late consolidation: count our "feed" deaths, pearls they drop, and how many of those pearls our team eats (and the longest)
const path = require('path'), fs = require('fs');
const HR = '~/01. Project/개인 프로젝트/unsw-heuristic';
const { load } = require(path.join(HR, 'tools/replay.js'));
const [dir, mapf] = process.argv.slice(2);
let feeds = 0, drops = 0, eatenUs = 0, games = 0, feedLen = 0;
for (const g of fs.readdirSync(dir + '/games')) {
  if (!g.includes(mapf)) continue;
  const US = /_A_\d$/.test(g) ? 'A' : 'B';
  const R = load(dir + '/games/' + g + '/game.replay'); games++;
  const team = new Map(), len = new Map(); for (const d of R.match.map.initialDragons) { team.set(d.id, d.team); len.set(d.id, d.body.length); }
  const lastInd = new Map(); let cur = -1, phase = 'tick', pendingFeed = null; const feedTiles = new Set();
  for (const e of R.events) {
    if (e.type === 'roundStart') phase = 'tick';
    if (e.type === 'turnStart') { phase = 'turn'; cur = e.id; pendingFeed = null; }
    if (e.type === 'dragonSplit') { team.set(e.childId, e.team); len.set(e.childId, e.childBody.length); len.set(e.parentId, e.parentBody.length); }
    if (e.type === 'dragonIndicator') lastInd.set(e.id, e.text || '');
    if (e.type === 'dragonDeath' && team.get(e.id) === US && /^feed/.test(lastInd.get(e.id) || '')) { feeds++; pendingFeed = e.id; }
    if (e.type === 'tileChange') {
      const t = e.tile.x + ',' + e.tile.y;
      if (e.hasPearl && phase === 'turn' && pendingFeed !== null) { drops++; feedTiles.add(t); }
      else if (!e.hasPearl && phase === 'turn' && feedTiles.has(t)) { feedTiles.delete(t); if (team.get(cur) === US) eatenUs++; }
      else if (e.hasPearl) feedTiles.delete(t);
    }
  }
}
console.log({ games, feedsPerGame: (feeds / games).toFixed(2), dropsPerGame: (drops / games).toFixed(1), eatenByUsShare: (eatenUs / Math.max(1, drops)).toFixed(3) });
