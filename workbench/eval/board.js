// eval/board.js: ASCII board pictures for expected-vs-actual checks (docs/arch/README.md). Inspect one replay: snapshots of the board at chosen rounds plus a timeline of our economy and conversion.
// usage: node eval/board.js <replay> <mapName> <variant a|b> <ourTeam A|B> [rounds comma list]
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const [file, mapName, variant, us, roundsArg] = process.argv.slice(2);
const them = us === 'A' ? 'B' : 'A';
const SNAP = new Set((roundsArg || '10,40,100,200,300,380,450,499').split(',').map(Number));
const R = makeLoader(viewerSource())(file);
const out = [];
const tl = [];            // timeline rows every 25 rounds
const sdTargets = new Map(); // round -> [{x,y}]
const tags = { sx: 0, sr: 0, sd: 0, sf: 0, sq: 0, sc: 0, sk: 0, esc: 0, split: 0 };
const sfEvents = [];      // local feeds: round, from len, to id
let lastSnap = -1;
function snapshot(round, ctx) {
  const { W, H, drag, pearls } = ctx;
  const g = Array.from({ length: H }, () => Array(W).fill(' '));
  for (const [k, v] of pearls) { const x = k % W, y = (k / W) | 0; g[y][x] = v === -1 ? 'o' : '%'; }
  const ours = [], theirs = [];
  for (const d of drag.values()) {
    const L = d.body.length;
    for (let i = 1; i < L; i++) { const s = d.body[i]; g[s.y][s.x] = d.team === us ? '.' : 'x'; }
    const h = d.body[0];
    g[h.y][h.x] = d.team === us ? (L >= 10 ? '#' : String(Math.min(L, 9))) : (L >= 10 ? 'K' : 'X');
    (d.team === us ? ours : theirs).push(L);
  }
  for (const t of sdTargets.get(round) || []) if (g[t.y] && g[t.y][t.x] === ' ') g[t.y][t.x] = '*';
  ours.sort((a, b) => b - a); theirs.sort((a, b) => b - a);
  out.push(`--- r${round}: ours ${ours.length} dragons [${ours.slice(0, 12).join(' ')}${ours.length > 12 ? ' …' : ''}] total ${ours.reduce((a, b) => a + b, 0)} | theirs ${theirs.length} [${theirs.slice(0, 8).join(' ')}${theirs.length > 8 ? ' …' : ''}] total ${theirs.reduce((a, b) => a + b, 0)}`);
  out.push('+' + '-'.repeat(W) + '+');
  for (const row of g) out.push('|' + row.join('') + '|');
  out.push('+' + '-'.repeat(W) + '+');
}
const res = perGame(R, { map: mapName, variant }, {
  turn(d, round, ctx) {
    if (SNAP.has(round) && round !== lastSnap) { lastSnap = round; snapshot(round, ctx); }
    if (round % 25 === 0 && (!tl.length || tl[tl.length - 1].r !== round)) {
      const o = [...ctx.drag.values()].filter(q => q.team === us).map(q => q.body.length);
      const t = [...ctx.drag.values()].filter(q => q.team === them).map(q => q.body.length);
      tl.push({ r: round, ou: o.length, ol: Math.max(0, ...o), ot: o.reduce((a, b) => a + b, 0), tu: t.length, tlong: Math.max(0, ...t), tt: t.reduce((a, b) => a + b, 0) });
    }
  },
  indicator(e, round, ctx) {
    const s = String(e.text || '');
    const d = ctx.drag.get(e.dragonId ?? e.id);
    if (d && d.team !== us) return;
    for (const k of Object.keys(tags)) if (new RegExp(`(^|\\s)${k}([@#\\d]|\\b)`).test(s)) tags[k]++;
    const m = s.match(/ sd@(\d+),(\d+)/); if (m) { const a = sdTargets.get(round) || []; a.push({ x: +m[1], y: +m[2] }); sdTargets.set(round, a); }
    const f = s.match(/ sf#(\d+)/); if (f) sfEvents.push({ r: round, from: d ? d.body.length : '?', to: +f[1] });
  },
});
console.log(`game ${path.basename(path.dirname(file))} map ${mapName}/${variant} us=${us} result ${JSON.stringify(R.result && { winner: R.result.winner, rounds: R.result.rounds, end: R.result.endReason })}`);
console.log('tags(our turns):', JSON.stringify(tags));
console.log('timeline r | our units / longest / total | their units / longest / total');
for (const x of tl) console.log(`  r${String(x.r).padStart(3)} | ${String(x.ou).padStart(3)} / ${String(x.ol).padStart(3)} / ${String(x.ot).padStart(4)} | ${String(x.tu).padStart(3)} / ${String(x.tlong).padStart(3)} / ${String(x.tt).padStart(4)}`);
console.log(`local feeds (sf) ${sfEvents.length}: first 12 → ${sfEvents.slice(0, 12).map(e => `r${e.r} L${e.from}→#${e.to}`).join(', ')}`);
console.log(out.join('\n'));
