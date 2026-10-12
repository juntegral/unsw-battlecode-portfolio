// duplicate targets: the share of our target-labelled turns (v1 " sd<d>@x,y", v0 " F<d>@x,y") whose target is also another of our dragons'
// target in the same round: exact tile, and within Manhattan 3 (one group). Per eval dir(s); swarm maps only by default (--all for every map).
const fs = require('fs'), path = require('path');
const { makeLoader, viewerSource } = require('../../tools/top_features.js');
const load = makeLoader(viewerSource());
const dirs = process.argv[2].split(','), all = process.argv.includes('--all');
const FORT = /^(autarky|portals|prisoners_dilemma)/;
const tot = { n: 0, exact: 0, group: 0, games: 0 };
for (const dir of dirs) {
  const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined);
  for (const r of rows) {
    if (!all && FORT.test(r.map)) continue;
    const f = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
    const R = load(f); tot.games++;
    const W = R.match.map.width, H = R.match.map.height;
    const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
    let round = -1, cur = [];
    const flush = () => {
      for (let i = 0; i < cur.length; i++) {
        tot.n++;
        let ex = 0, gr = 0;
        for (let j = 0; j < cur.length; j++) { if (i === j) continue; const dx = Math.abs(cur[i][0] - cur[j][0]), dy = Math.abs(cur[i][1] - cur[j][1]);
          const m = Math.min(dx, W - dx) + Math.min(dy, H - dy); if (m === 0) ex = 1; if (m <= 3) gr = 1; }
        tot.exact += ex; tot.group += gr;
      }
      cur = [];
    };
    for (const e of R.events) {
      if (e.type === 'roundStart') { flush(); round = e.round; }
      else if (e.type === 'dragonSplit') team.set(e.childId, e.team);
      else if (e.type === 'dragonIndicator' && team.get(e.id) === r.side) {
        const m = / (?:sd|F)\d+@(\d+),(\d+)/.exec(e.text || ''); if (m) cur.push([+m[1], +m[2]]);
      }
    }
    flush();
  }
}
console.log(`${process.argv[2]}: games ${tot.games}, target turns ${tot.n}, shared exact ${(100 * tot.exact / tot.n).toFixed(1)}%, shared within 3 ${(100 * tot.group / tot.n).toFixed(1)}%`);
