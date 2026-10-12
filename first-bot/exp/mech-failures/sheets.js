#!/usr/bin/env node
// Stage 3 of mech-merge2-failures.md: compact case sheets for the replays selected by report.js (--select file).
// usage (repository root): node exp/mech-failures/sheets.js <select.json> [--pattern <prefix>] [--frames extreme|all|none]
// Each game is loaded once. For every selected case it prints, round by round, the subject dragon (its length, head, our
// label), the dragon that killed it or the partner of the event, the enemy heads within 5, and the events (splits,
// deaths with cause, portal crossings); the extreme case of each class also gets a 7x7 board at the decisive moment.
// Board legend: @ our head, o our body, X their head, x their body, * pearl, | kelp or : portal on a vertical edge,
// - kelp or = portal on a horizontal edge.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const { makeFastLoader } = require(path.join(__dirname, 'collect.js'));
const CA = ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'];
const argv = process.argv.slice(2);
const opt = n => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : null; };
const sel = JSON.parse(fs.readFileSync(argv[0], 'utf8')).filter(x => !opt('--pattern') || x.pattern.startsWith(opt('--pattern')));
const frames = opt('--frames') || 'extreme';
const load = makeFastLoader();
const byGame = new Map(); for (const x of sel) { const k = x.set + ':' + x.game; if (!byGame.has(k)) byGame.set(k, []); byGame.get(k).push(x); }
const out = [];
for (const [k, cases] of byGame) {
  const [set, gameS] = k.split(':'); const game = +gameS;
  const idx = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'online', set, 'index.json'), 'utf8'));
  const row = (idx.games || idx).find(g => g.gameId === game), us = String(row.ourSide).toUpperCase();
  const R = load(path.join(ROOT, 'data', 'online', set, 'M' + game + '.replay'));
  const info = { map: row.mapName }; if (row.mapName === 'Prisoners Dilemma') info.variant = R.match.map.initialDragons.length === 10 ? 'PD10' : 'PD6';
  // subject per case
  for (const x of cases) {
    x.subject = x.id; let m;
    if (x.pattern.startsWith('2') && (m = /feeds #(\d+)/.exec(x.note))) x.subject = +m[1];
    if (x.pattern.startsWith('6') && (m = /child #(\d+)/.exec(x.note))) x.subject = +m[1];
  }
  const snaps = new Map(), labels = new Map(), deaths = new Map(), splits = [], portals = [], eatsOf = new Map(), boards = new Map();
  let lastR = -1, W = 0, H = 0;
  const want = new Set(); for (const x of cases) for (let r = Math.max(0, x.r - 3); r <= x.r + 12; r++) want.add(r);
  const wantBoard = new Map(); // round -> [case]
  const hooks = {
    turn(d, r, c) {
      W = c.W; H = c.H;
      if (r !== lastR) {
        lastR = r;
        const a = []; for (const o of c.drag.values()) a.push([o.id, o.team, o.body.length, o.body[0].x, o.body[0].y, o.born]);
        snaps.set(r, a);
        for (const x of cases) if (x.boardR === r && !boards.has(x)) boards.set(x, board(c, x));
      }
    },
    indicator(e, r) { labels.set(e.id + ':' + r, e.text); },
    action(d, e, r, c) { if (d.portalSteps) portals.push([r, d.id, d.team, d.body.length, d.fate ? d.fate.reason : null]); },
    split(p, ch, e, r) { splits.push([r, p.id, ch.id, p.team, p.body.length, ch.body.length]); },
    death(d, rec, idx, other, r, c) { deaths.set(d.id, { r, cause: rec.cause, len: rec.len, other: other ? [other.id, other.team, other.body.length, other.steps || 0, other.portalSteps || 0] : null, idx }); },
    eat(d, tile, o, r) { if (o >= 0) { if (!eatsOf.has(o)) eatsOf.set(o, []); eatsOf.get(o).push([r, d.id, d.team, d.body.length]); } },
  };
  // decisive round per case (for the board): death round of the subject if known later; first pass without boards
  perGame(R, info, hooks);
  const dist = (a, b) => { const dx = Math.abs(a[3] - b[3]), dy = Math.abs(a[4] - b[4]); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
  for (const x of cases) {
    const z = deaths.get(x.subject);
    const isEsc = x.pattern.startsWith('1 ');
    let r0 = x.r - 2, r1 = z ? z.r : x.r + 10;
    if (isEsc) r1 = Math.min(r1, x.r + 10);
    if (x.pattern.startsWith('1b')) r0 = Math.max(0, r1 - 5);
    if (x.pattern.startsWith('2') || x.pattern.startsWith('6')) r0 = z ? Math.max(x.r, z.r - 5) : x.r;
    if (x.pattern.startsWith('3')) { r0 = x.r - 1; r1 = z && z.r <= x.r + 70 ? z.r : Math.min(x.r + 6, 499); }
    if (x.pattern.startsWith('4')) r1 = Math.min(r1, x.r + 3);
    if (x.pattern.startsWith('5')) r1 = x.r + 1;
    x.window = [r0, r1]; x.boardR = z ? z.r : Math.min(x.r + 1, 499);
    if (x.pattern.startsWith('3') && !(z && z.r <= x.r + 70)) x.boardR = x.r;
  }
  // second pass for the boards and the long windows (feed / split / gather need rounds outside the first pass's want set)
  lastR = -1; snaps.clear();
  const need = new Set(); for (const x of cases) for (let r = x.window[0]; r <= x.window[1]; r++) need.add(r);
  const hooks2 = { ...hooks, turn(d, r, c) { if (r !== lastR) { lastR = r; if (need.has(r)) { const a = []; for (const o of c.drag.values()) a.push([o.id, o.team, o.body.length, o.body[0].x, o.body[0].y, o.born]); snaps.set(r, a); }
    for (const x of cases) if (x.boardR === r && !boards.has(x) && (frames === 'all' || (frames === 'extreme' && x.role === 'extreme'))) boards.set(x, board(c, x)); } } };
  labels.clear(); deaths.clear(); splits.length = 0; portals.length = 0; eatsOf.clear();
  perGame(load(path.join(ROOT, 'data', 'online', set, 'M' + game + '.replay')), info, hooks2);
  function board(c, x) {
    const d = c.drag.get(x.subject); if (!d) return null;
    const K = (xx, yy) => yy * c.W + xx, cell = new Map();
    for (const o of c.drag.values()) o.body.forEach((s, i) => cell.set(K(s.x, s.y), { o, head: i === 0 }));
    const cx = d.body[0].x, cy = d.body[0].y, lines = [];
    for (let dy = -3; dy <= 3; dy++) {
      let l1 = '', l2 = '';
      for (let dx = -3; dx <= 3; dx++) {
        const xx = ((cx + dx) % c.W + c.W) % c.W, yy = ((cy + dy) % c.H + c.H) % c.H, kk = K(xx, yy), q = cell.get(kk);
        let ch = c.pearls.has(kk) ? '*' : '.'; if (q) { const mine = q.o.team === us; ch = q.head ? (mine ? '@' : 'X') : (mine ? 'o' : 'x'); }
        const e = c.across(xx, yy, 'E'), ep = e && (e.x !== (xx + 1) % c.W || e.y !== yy), s = c.across(xx, yy, 'S'), sp = s && (s.y !== (yy + 1) % c.H || s.x !== xx);
        l1 += ch + (!e ? '|' : ep ? ':' : ' '); l2 += (!s ? '-' : sp ? '=' : ' ') + ' ';
      }
      lines.push('    ' + l1, '    ' + l2);
    }
    return lines.join('\n');
  }
  for (const x of cases) {
    const z = deaths.get(x.subject), other = z && z.other ? z.other[0] : null;
    out.push(`\n### ${x.pattern} | ${x.cls} | ${x.role}`);
    out.push(`${set} ${game} ${row.mapName} vs ${x.opp} (we are ${us}), r${x.r} #${x.id}${x.subject !== x.id ? ` (subject #${x.subject})` : ''}: ${x.note}`);
    for (let r = x.window[0]; r <= x.window[1]; r++) {
      const s = snaps.get(r); if (!s) continue;
      const me = s.find(q => q[0] === x.subject); if (!me) { out.push(`  r${r}: #${x.subject} not alive`); continue; }
      const ot = other !== null ? s.find(q => q[0] === other) : null;
      const en = s.filter(q => q[1] !== me[1] && q[0] !== other && dist(q, me) <= 5).sort((a, b) => dist(a, me) - dist(b, me)).slice(0, 6).map(q => `L${q[2]}@${dist(q, me)}`).join(' ');
      const al = s.filter(q => q[1] === me[1] && q[0] !== me[0] && dist(q, me) <= 3).map(q => `L${q[2]}@${dist(q, me)}`).join(' ');
      const lab = labels.get(x.subject + ':' + r) || '';
      const ev = [...splits.filter(q => q[0] === r && (q[1] === x.subject || q[1] === other)).map(q => `split #${q[1]}->#${q[2]} (${q[4]}+${q[5]})`),
        ...portals.filter(q => q[0] === r && (q[1] === x.subject || q[1] === other)).map(q => `#${q[1]} portal${q[4] ? ' DIED ' + q[4] : ''}`)].join('; ');
      out.push(`  r${r}: L${me[2]} (${me[3]},${me[4]}) "${lab.split('|')[0].trim()}"` + (ot ? ` | #${other} L${ot[2]} (${ot[3]},${ot[4]}) d${dist(ot, me)}` : '') + (en ? ` | enemy<=5: ${en}` : '') + (al ? ` | ally<=3: ${al}` : '') + (ev ? ` | ${ev}` : ''));
    }
    if (z) {
      const E = eatsOf.get(z.idx) || [];
      out.push(`  death r${z.r}: ${CA[z.cause]} L${z.len}` + (z.other ? ` with #${z.other[0]} (${z.other[1] === us ? 'ours' : 'THEIRS'}) L${z.other[2]}, its move ${z.other[3]} steps${z.other[4] ? ', through a portal' : ''}` : '') + `; drops eaten: us ${E.filter(e => e[2] === us).length}, them ${E.filter(e => e[2] !== us).length}`);
    }
    if (boards.get(x)) out.push(`  board at the start of r${x.boardR} around #${x.subject}:\n` + boards.get(x));
  }
}
console.log(out.join('\n'));
