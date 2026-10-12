#!/usr/bin/env node
// Q1 mechanism check (exp/v16/q1/Q1.md §5): per game, our queen (side A: id 0, side B: id 1): her death round, her length at r300 / 350 / 400 /
// 450 / 500, the pearls she ate from r300 by origin (our feeds, other deaths, natural); every labelled feed of ours from r300 ("feed #<K> ..."):
// whether K was the queen, whether the queen was alive then, the round (late window r >= 430), and who ate its drops (the queen, another of ours,
// the enemy). usage: node exp/v16/q1/qmech.js <dir> [<dir> ...] [--list] [--out file.md]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const ML = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), LIST = args.includes('--list'), oi = args.indexOf('--out'), OUT = oi >= 0 ? args[oi + 1] : null;
const dirs = args.filter((a, i) => !a.startsWith('--') && args[i - 1] !== '--out');
const CP = [100, 250, 300, 350, 400, 450];
function analyse(file, row) {
  const R = load(file), us = row.side;
  let Q = null; for (const d of R.match.map.initialDragons) if (d.team === us && (Q === null || d.id < Q)) Q = d.id;   // our queen: our lowest starting id (online sides do not fix it)
  const last = new Map(), feeds = [], byDeath = new Map(), qLen = {}, qEat = { feed: 0, otherDeath: 0, natural: 0 }, bLen = {}, crowd = [];
  let qDeath = null, qEnd = 0, qCause = '';
  ML.perGame(R, { map: row.map, variant: '?' }, {
    turn(d, r, c) {
      if (d.id === Q && CP.concat([430]).includes(r) && qLen[r] === undefined) qLen[r] = d.body.length;
      if (d.id === Q && r >= 340 && r <= 480 && r % 10 === 0) {   // Q1b: our other heads within Manhattan 2 of the queen's head
        let n = 0; for (const o of c.drag.values()) if (o.team === us && o.id !== Q && c.tdist(o.body[0], d.body[0]) <= 2) n++;
        crowd.push(n);
      }
      if ([300, 350, 400, 430].includes(r) && bLen[r] === undefined) {   // Q1b: the backup, our longest dragon other than the queen
        let b = 0; for (const o of c.drag.values()) if (o.team === us && o.id !== Q) b = Math.max(b, o.body.length);
        bLen[r] = b;
      }
    },
    indicator(e, r, c) { const d = c.drag.get(e.id); if (d && d.team === us) last.set(e.id, [r, e.text || '']); },
    death(d, rec, i, o, r, c) {
      if (d.id === Q && qDeath === null) { qDeath = r; qCause = ML.CAUSE[rec.cause] + (rec.blk && rec.blk !== '-' ? '/' + rec.blk : ''); }
      if (d.team !== us || r < 300) return;
      const t = last.get(d.id); if (!t || t[0] !== r) return;
      const m = /^feed #(\d+) d(\d+) L(\d+)(.*)$/.exec(t[1]); if (!m) return;
      let best = null; for (const o of c.drag.values()) if (o.team === us && o.id !== d.id && (!best || o.body.length > best.body.length || (o.body.length === best.body.length && o.id < best.id))) best = o;
      const f = { r, L: +m[3], d: +m[2], K: +m[1], toQueen: +m[1] === Q, queenAlive: c.drag.has(Q), kLongest: !!(best && best.id === +m[1]), qTag: / Q(\s|$)/.test(m[4]),
        kind: / cv2/.test(m[4]) ? 'cv2' : / conv/.test(m[4]) ? 'conv' : 'feed', drops: rec.drops, byQ: 0, byOwn: 0, byEnemy: 0 };
      f.slack = 500 - r - (f.d + f.L);
      feeds.push(f); byDeath.set(i, f);
    },
    eat(d, k, o, r, c) {
      if (d.id === Q && r >= 300) { if (o >= 0) { if (byDeath.has(o)) qEat.feed++; else qEat.otherDeath++; } else qEat.natural++; }
      const f = byDeath.get(o); if (!f) return;
      if (d.team !== us) f.byEnemy++; else if (d.id === Q) f.byQ++; else f.byOwn++;
    },
    end(n, c) { const q = c.drag.get(Q); qEnd = q ? q.body.length : 0; },
  });
  for (const r of CP) if (qLen[r] === undefined) qLen[r] = 0;
  qLen[500] = qEnd;
  return { key: row.key, map: row.map, won: row.won, qDeath, qCause, qLen, qEat, feeds, bLen, crowd };
}
const games = [];
for (const d of dirs) {
  const dir = path.resolve(ROOT, d);
  for (const l of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean)) {
    const row = JSON.parse(l); if (row.error) continue;
    const f = path.join(dir, 'games', row.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
    try { games.push(analyse(f, row)); } catch (e) { console.error('fail', row.key, String(e).slice(0, 100)); }
  }
}
const pc = (a, b) => b ? (100 * a / b).toFixed(0) + '%' : '–';
const med = a => { if (!a.length) return '–'; const s = [...a].sort((x, y) => x - y); return String(s[Math.floor(s.length / 2)]); };
const out = [`# Q1 mechanism check (${new Date().toISOString().slice(0, 16)}Z): ${games.length} games from ${dirs.join(', ')}`, ''];
const g300 = games.filter(g => g.qDeath === null || g.qDeath > 300), g400 = games.filter(g => g.qDeath === null || g.qDeath > 400);
const F = games.flatMap(g => g.feeds), Fa = F.filter(f => f.queenAlive);
out.push(`- games ${games.length}; our queen alive at r300 ${g300.length}, at r400 ${g400.length}, at r500 ${games.filter(g => g.qDeath === null).length}`);
out.push(`- labelled feeds from r300: ${F.length} (conv ${F.filter(f => f.kind === 'conv').length}, feed ${F.filter(f => f.kind === 'feed').length}, cv2 ${F.filter(f => f.kind === 'cv2').length}); while the queen was alive ${Fa.length}, of which to the queen ${Fa.filter(f => f.toQueen).length} (${pc(Fa.filter(f => f.toQueen).length, Fa.length)})`);
const late = Fa.filter(f => f.r >= 430 && !f.toQueen);
out.push(`- late feeds (r >= 430) to a non-queen while the queen was alive: ${late.length}`);
const Fq = Fa.filter(f => f.toQueen), dq = Fq.reduce((s, f) => s + f.drops, 0);
out.push(`- drops of feeds to the queen: ${dq}; eaten by the queen ${Fq.reduce((s, f) => s + f.byQ, 0)} (${pc(Fq.reduce((s, f) => s + f.byQ, 0), dq)}), another of ours ${Fq.reduce((s, f) => s + f.byOwn, 0)}, the enemy ${Fq.reduce((s, f) => s + f.byEnemy, 0)}`);
const Fo = Fa.filter(f => !f.toQueen), dO = Fo.reduce((s, f) => s + f.drops, 0);
out.push(`- drops of feeds to others while the queen was alive: ${dO}; eaten by their target or another of ours ${Fo.reduce((s, f) => s + f.byOwn + f.byQ, 0)}`);
const dc = {}; for (const g of games) if (g.qDeath !== null && g.qDeath > 300) dc[g.qCause] = (dc[g.qCause] || 0) + 1;
out.push(`- queen deaths after r300 by cause (trap/a = an ally body blocked a side, /e enemy body, /s self or kelp): ${Object.entries(dc).map(([k, v]) => k + ' ' + v).join(', ') || 'none'}`);
out.push(`- queen length (games with the queen alive at the round): ${[100, 250, 300, 350, 400, 450, 500].map(r => `r${r} ${med(games.filter(g => r === 500 ? g.qDeath === null : (g.qDeath === null || g.qDeath > r)).map(g => g.qLen[r]))}`).join(', ')}`);
out.push(`- the queen's pearls from r300 (games with the queen alive at r300): from our feeds ${g300.reduce((s, g) => s + g.qEat.feed, 0)}, other deaths ${g300.reduce((s, g) => s + g.qEat.otherDeath, 0)}, natural ${g300.reduce((s, g) => s + g.qEat.natural, 0)}`);
// Q1b criteria
const early = Fa.filter(f => f.toQueen && f.r < 430);
out.push(`- Q1b: feeds to the queen before r430 ${early.length}, of which she was our longest then ${early.filter(f => f.kLongest).length}`);
const g430 = games.filter(g => g.qDeath === null || g.qDeath > 430);
out.push(`- Q1b: backup (our longest non-queen) in games with the queen alive at r430: r300/350/400/430 medians ${[300, 350, 400, 430].map(r => med(g430.map(g => g.bLen[r] || 0))).join('/')} (n${g430.length})`);
const qtag = F.filter(f => f.qTag), qtagLate = qtag.filter(f => f.r >= 430 && f.kind === 'feed');
out.push(`- Q1b: " Q" feeds ${qtag.length} (while the queen was alive ${qtag.filter(f => f.queenAlive).length}); late merges (feed, r430+) ${qtagLate.length}, slack ${qtagLate.length ? Math.min(...qtagLate.map(f => f.slack)) + '-' + Math.max(...qtagLate.map(f => f.slack)) : '-'}, drops eaten by the queen ${qtagLate.reduce((s, f) => s + f.byQ, 0)}/${qtagLate.reduce((s, f) => s + f.drops, 0)}; all " Q" drops eaten by her ${qtag.reduce((s, f) => s + f.byQ, 0)}/${qtag.reduce((s, f) => s + f.drops, 0)}`);
const crowd = games.flatMap(g => g.crowd);
out.push(`- Q1b: our other heads within 2 of the queen's head (every 10th round r340-480): median ${med(crowd)}, share of samples with >= 2: ${pc(crowd.filter(x => x >= 2).length, crowd.length)} (n${crowd.length})`);
if (LIST) {
  out.push('', '| game | queen death | queen L r100/250/300/350/400/450/500 | queen pearls from r300: feeds / other deaths / natural | feeds from r300 (r L→K, q = queen, x = queen dead) |', '|---|---|---|---|---|');
  for (const g of games) out.push(`| ${g.key} | ${g.qDeath === null ? 'alive' : 'r' + g.qDeath + ' ' + g.qCause} | ${[100, 250, 300, 350, 400, 450, 500].map(r => g.qLen[r]).join('/')} | ${g.qEat.feed} / ${g.qEat.otherDeath} / ${g.qEat.natural} | ${g.feeds.map(f => `r${f.r} L${f.L}→#${f.K}${f.toQueen ? 'q' : ''}${f.queenAlive ? '' : 'x'} ${f.kind} ${f.byQ}/${f.drops}`).join('; ')} |`);
}
const text = out.join('\n') + '\n';
if (OUT) fs.writeFileSync(path.resolve(ROOT, OUT), text); else process.stdout.write(text);
