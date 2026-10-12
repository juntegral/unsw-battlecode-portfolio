// v1.1 diagnostic: head share by frontier bin for BOTH teams (each from its own side) at r25/50/100, per map, and our sd target bins. usage: node exp/v11/oppbins.js <evalDir>[,<evalDir>]
const fs = require('fs'), path = require('path');
const ROOT = process.cwd();
const { geometry } = require(path.join(ROOT, 'exp', 'spatial', 'lib.js'));
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const load = makeLoader(viewerSource());
const dirs = process.argv[2].split(',');
const agg = {};
for (const dir of dirs) {
  const rows = fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.G !== undefined);
  for (const r of rows) {
    const file = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
    const R = load(file), M = R.match.map, W = M.width, g = geometry(M, 'x', '?');
    const us = r.side, them = us === 'A' ? 'B' : 'A';
    const team = new Map(M.initialDragons.map(d => [d.id, d.team]));
    const pos = new Map(); for (const d of M.initialDragons) pos.set(d.id, d.body[0]);
    const A = agg[r.map] || (agg[r.map] = { us: {}, them: {}, tg: [0, 0, 0, 0, 0] });
    let round = -1;
    const snap = rr => { for (const [id, p] of pos) { const t = team.get(id), side = t === us ? 'us' : 'them'; const b = g.bin[t][p.y * W + p.x]; const h = A[side][rr] || (A[side][rr] = [0, 0, 0, 0, 0, 0]); h[b]++; } };
    for (const e of R.events) {
      if (e.type === 'roundStart') { round = e.round; if ([25, 50, 100].includes(round)) snap(round); }
      else if (e.type === 'dragonSplit') { team.set(e.childId, e.team); }
      else if (e.type === 'dragonUpdate') { if (e.head) pos.set(e.id, e.head); }
      else if (e.type === 'dragonDeath') pos.delete(e.id);
      else if (e.type === 'dragonIndicator' && team.get(e.id) === us) { const m = / f([0-4])/.exec(e.text || ''); if (m && / sd\d+@/.test(e.text)) A.tg[+m[1]]++; }
    }
  }
}
const pc = h => { const t = h.slice(0, 5).reduce((a, b) => a + b, 0); return t ? h.slice(0, 5).map(v => Math.round(100 * v / t)).join('·') + ` (${t})` : '–'; };
for (const [m, A] of Object.entries(agg)) console.log(m.padEnd(18), 'us', [25, 50, 100].map(r => pc(A.us[r] || [])).join(' | '), ' THEM', [25, 50, 100].map(r => pc(A.them[r] || [])).join(' | '), ' sd-target bins', pc(A.tg.concat([0])));
