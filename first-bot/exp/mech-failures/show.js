#!/usr/bin/env node
// ASCII view of one online game around a dragon, for opening the failure cases of mech-merge2-failures.md quickly.
// usage (repository root):
//   node exp/mech-failures/show.js <set> <gameId> <dragonId> <round>[,<round>...] [--r 6] [--after]
//     prints the board around the dragon's head at the start of each round (--after: after the dragon's own turn), and
//     the last action / indicator of every head in the window.
// Legend: @ our head, o our body, X their head, x their body, * pearl, . empty. Between cells: | kelp, : portal (vertical
// edges); under cells: - kelp, = portal (horizontal edges). "Our" = team 583 in that game.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const DIRS = ['N', 'E', 'S', 'W'];

function main() {
  const argv = process.argv.slice(2);
  const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
  const pos = argv.filter((a, i) => !a.startsWith('--') && argv[i - 1] !== '--r');
  const [set, gameId, dragonId, roundsArg] = pos;
  if (!roundsArg) { console.error('usage: show.js <set> <gameId> <dragonId> <r1,r2,...> [--r 6] [--after]'); process.exit(2); }
  const idx = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'online', set, 'index.json'), 'utf8'));
  const row = (idx.games || idx).find(g => String(g.gameId) === String(gameId));
  const us = String(row.ourSide).toUpperCase();
  const R = makeLoader(viewerSource())(path.join(ROOT, 'data', 'online', set, 'M' + gameId + '.replay'));
  const want = new Set(roundsArg.split(',').map(Number)), rad = +opt('--r', 6), after = argv.includes('--after'), did = +dragonId;
  const lastAct = new Map(), ind = new Map(); let lastR = -1, shown = new Set();
  const info = { map: row.mapName }; if (row.mapName === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
  function draw(c, r, when) {
    const d = c.drag.get(did) || null;
    const center = d ? d.body[0] : (lastAct.get(did) || {}).head;
    if (!center) { console.log(`r${r}: #${did} not alive`); return; }
    const W = c.W, H = c.H, K = (x, y) => y * W + x;
    const cell = new Map();
    for (const o of c.drag.values()) o.body.forEach((s, i) => cell.set(K(s.x, s.y), { o, head: i === 0 }));
    const lines = [], heads = [];
    for (let dy = -rad; dy <= rad; dy++) {
      let l1 = '', l2 = '';
      for (let dx = -rad; dx <= rad; dx++) {
        const x = ((center.x + dx) % W + W) % W, y = ((center.y + dy) % H + H) % H, k = K(x, y);
        const q = cell.get(k); let ch = c.pearls.has(k) ? '*' : '.';
        if (q) { const mine = q.o.team === us; ch = q.head ? (mine ? '@' : 'X') : (mine ? 'o' : 'x'); if (q.head) heads.push(q.o); }
        const e = c.across(x, y, 'E'), ep = e && (e.x !== (x + 1) % W || e.y !== y);
        const s = c.across(x, y, 'S'), sp = s && (s.y !== (y + 1) % H || s.x !== x);
        l1 += ch + (!e ? '|' : ep ? ':' : ' ');
        l2 += (!s ? '-' : sp ? '=' : ' ') + ' ';
      }
      lines.push(l1, l2);
    }
    console.log(`\n=== ${set} ${gameId} ${row.mapName} r${r} ${when}: #${did} ${d ? `L${d.body.length} head (${center.x},${center.y})` : 'dead'}  [@ ours, X theirs]`);
    console.log(lines.join('\n'));
    const hs = [...new Set(heads)].sort((a, b) => a.id - b.id);
    for (const o of hs) {
      const a = lastAct.get(o.id) || {};
      console.log(`  ${o.team === us ? 'ours ' : 'THEIR'} #${o.id} L${o.body.length} head (${o.body[0].x},${o.body[0].y}) born r${o.born}${o.parent >= 0 ? ' of #' + o.parent : ''} | last action r${a.r ?? '-'}: ${a.txt || '-'}${ind.has(o.id) && ind.get(o.id).r >= r - 1 ? ` | "${ind.get(o.id).text}"` : ''}`);
    }
  }
  const hooks = {
    turn(d, r, c) {
      if (r !== lastR) { lastR = r; if (!after && want.has(r) && !shown.has(r)) { shown.add(r); draw(c, r, 'round start'); } }
    },
    indicator(e, r) { ind.set(e.id, { r, text: e.text }); },
    action(d, e, r, c, before) {
      const a = e.action || {};
      lastAct.set(d.id, { r, head: d.body[0], txt: a.kind === 'move' ? `move ${a.steps.join('')}${d.portalSteps ? ' (portal)' : ''}${d.ateThisAct ? ' ate' + d.ateThisAct : ''}${d.fate ? ' DIED ' + d.fate.reason : ''} ${before[0].x},${before[0].y}->${d.body[0].x},${d.body[0].y}` : a.kind === 'split' ? `split child ${a.childSegmentCount}` : String(a.kind) });
      if (after && d.id === did && want.has(r)) draw(c, r, 'after its turn');
    },
    death(d, rec, idx, other, r, c) {
      const CA = ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'];
      if (d.id === did || (other && other.id === did)) console.log(`  [death r${r}] #${d.id} (${d.team === us ? 'ours' : 'THEIR'}) L${rec.len} ${CA[rec.cause]}${other ? ` with #${other.id} (${other.team === us ? 'ours' : 'THEIR'}) L${other.body.length}` : ''}`);
    },
  };
  perGame(R, info, hooks);
}
main();
