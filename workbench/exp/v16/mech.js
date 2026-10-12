#!/usr/bin/env node
// v1.6g/h mechanism check (AGENTS.md 4.7: local games check that a mechanism fires where intended and does what it should; no outcome numbers).
// Per labelled feed of ours (the dying dragon's indicator "feed #<K> d<D> L<L> ..."): its kind (cv2 / sf / late / conv / feed), whether the declared
// K was our longest at that moment, how many of our dragons declared the same K that round (CONV2's " ck#<id>" / " ck=" tags), where its drops fell
// (Manhattan distance of each drop tile, body[0], body[2], ..., to K's head at the death) and who ate them (K, another of ours, the enemy, nobody).
// Merges (" m") also get their time slack at the death: 500 - r - (path distance + length). Tags counted per our turn: ck, cp, cy, sq and the v1.6h
// tags given with --tags. v1.6h: just-in-time merges (" jit": slack, K's eating delays), far pulls (" cp<d>" with d > 24: the change of d over the next
// 10 rounds), the spread gate (" sg": the first gated turn of each dragon, its Manhattan distance to our longest then).
// usage: node exp/v16/mech.js <dir>[?|!regex] ... [--from 250] [--tags sg] [--list] [--out file.md]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const ML = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const MAPS = { slithery_fight: ['Slithery Fight', 'a'], slithery_fight_b: ['Slithery Fight', 'b'], schooltime: ['Schooltime', 'a'], schooltime_b: ['Schooltime', 'b'],
  trauma: ['Trauma', 'a'], default: ['Default', 'a'], autarky: ['Autarky', 'a'], devil: ['Devil', 'a'], devil_b: ['Devil', 'b'], trophy: ['Trophy', 'a'],
  queen_of_spades: ['Queen Of Spades', 'a'], queen_of_spades_b: ['Queen Of Spades', 'b'], portals: ['Portals', 'a'], prisoners_dilemma: ['Prisoners Dilemma', '6'],
  arena: ['arena', '?'], big_empty: ['big_empty', '?'], Colosseum: ['Colosseum', '?'], default_small: ['default_small', '?'], stronghold: ['stronghold', '?'] };
const args = process.argv.slice(2), get = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const FROM = +get('--from', 250), LIST = args.includes('--list'), OUT = get('--out', null);
const TAGS = ['ck', 'cp', 'cy', 'sq', ...(get('--tags', '') ? get('--tags', '').split(',') : [])];
const dirs = []; for (let i = 0; i < args.length; i++) { if (args[i].startsWith('--')) { if (!['--list'].includes(args[i])) i++; continue; } dirs.push(args[i]); }

function analyse(file, row) {
  const [mapName, layout] = MAPS[row.map] || [row.map, '?'];
  const us = row.side, R = load(file);
  const lastText = new Map(), ckBy = new Map(), feeds = [], byDeath = new Map(), tagN = Object.fromEntries(TAGS.map(t => [t, 0]));
  const cpBy = new Map(), sgFirst = [];
  let turns = 0;
  const longestOf = c => { let b = null; for (const o of c.drag.values()) if (o.team === us && (!b || o.body.length > b.body.length || (o.body.length === b.body.length && o.id < b.id))) b = o; return b; };
  ML.perGame(R, { map: mapName, variant: layout }, {
    indicator(e, r, c) {
      const d = c.drag.get(e.id); if (!d || d.team !== us) return;
      const t = e.text || ''; lastText.set(e.id, [r, t]);
      if (r < FROM) return;
      turns++;
      for (const g of TAGS) if (new RegExp(`(^|\\s)${g}([#=\\d@]|\\b)`).test(t)) tagN[g]++;
      const m = / ck(#(\d+)|=)/.exec(t);
      if (m) { let a = ckBy.get(r); if (!a) ckBy.set(r, a = new Map()); a.set(e.id, m[1] === '=' ? e.id : +m[2]); }
      const cp = / cp(\d+)/.exec(t);
      if (cp) { let a = cpBy.get(e.id); if (!a) cpBy.set(e.id, a = []); a.push([r, +cp[1]]); }
      if (/ sg(\s|$)/.test(t) && !sgFirst.some(q => q.id === e.id)) { const b = longestOf(c); sgFirst.push({ id: e.id, r, L: d.body.length, dist: b ? c.tdist(d.body[0], b.body[0]) : null, longest: !!(b && b.id === e.id) }); }
    },
    death(d, rec, i, other, r, c) {
      if (d.team !== us || r < FROM) return;
      const lt = lastText.get(d.id); if (!lt || lt[0] !== r) return;
      const m = /^feed #(\d+) d(\d+) L(\d+)(.*)$/.exec(lt[1]); if (!m) return;
      const rest = m[4], kind = / cv2/.test(rest) ? 'cv2' : / late/.test(rest) ? 'late' : / conv sf#/.test(rest) ? 'sf' : / conv/.test(rest) ? 'conv' : 'feed';
      const K = +m[1], k = c.drag.get(K), best = longestOf(c), L = d.body.length;
      const tiles = d.body.filter((_, j) => j % 2 === 0);
      const kBel = (/ (?:k|a)(\d+)/.exec(rest) || [])[1];
      const f = { r, id: d.id, L, kind, merge: / m(\s|$)/.test(rest), jit: / jit/.test(rest), kDelay: [], K, kL: k ? k.body.length : null, kBel: kBel ? +kBel : null, dist: +m[2], kLongest: !!(best && best.id === K),
        dropD: k ? tiles.map(s => c.tdist(s, k.body[0])) : [], drops: rec.drops, toK: 0, toOwn: 0, toEnemy: 0, slack: 500 - r - (+m[2] + L), text: lt[1] };
      feeds.push(f); byDeath.set(i, f);
    },
    eat(d, k, o, r) { const f = byDeath.get(o); if (!f) return; if (d.team !== us) f.toEnemy++; else if (d.id === f.K) { f.toK++; f.kDelay.push(r - f.r); } else f.toOwn++; },
  });
  for (const f of feeds) {
    const a = ckBy.get(f.r); let n = 0, same = 0;
    if (a) for (const [id, k] of a) { n++; if (k === f.K) same++; }
    f.agree = n ? same / n : null; f.declN = n;
  }
  // far pulls: a dragon's pull distance d > 24 at round r against its pull distance 8-12 rounds later (the nearest such turn)
  const farPull = [];
  for (const a of cpBy.values()) for (const [r, dd] of a) {
    if (dd <= 24) continue;
    const later = a.filter(([r2]) => r2 >= r + 8 && r2 <= r + 12);
    if (later.length) farPull.push(later[0][1] - dd);
  }
  return { key: row.key, map: mapName + '/' + layout, turns, tags: tagN, feeds, farPull, sgFirst };
}

const games = [];
for (const spec of dirs) {
  const fm = /^([^?!]+)([?!])(.+)$/.exec(spec), dir = path.resolve(ROOT, fm ? fm[1] : spec), ok = fm ? (k => new RegExp(fm[3]).test(k) === (fm[2] === '?')) : (() => true);
  const rowsFile = path.join(dir, 'rows.jsonl'); if (!fs.existsSync(rowsFile)) { console.error('no rows', dir); continue; }
  for (const l of fs.readFileSync(rowsFile, 'utf8').split('\n').filter(Boolean)) {
    const row = JSON.parse(l); if (!ok(row.key) || row.error) continue;
    const file = path.join(dir, 'games', row.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(file)) continue;
    try { games.push(analyse(file, row)); } catch (e) { console.error('fail', row.key, String(e).slice(0, 120)); }
  }
}
const out = [];
const pc = (a, b) => b ? (100 * a / b).toFixed(0) + '%' : '–';
const med = a => { if (!a.length) return '–'; const s = [...a].sort((x, y) => x - y); return String(s[Math.floor(s.length / 2)]); };
out.push(`# CONV2 mechanism check (${new Date().toISOString().slice(0, 16)}Z): ${games.length} games from ${dirs.join(', ')}; our turns and feeds from r${FROM}`);
out.push('');
out.push('| map | games | our turns | tags per 100 turns (' + TAGS.join(' / ') + ') | feeds by kind | declared K = our longest | median share of our declarations naming K | K shorter than the donor believed (and too short for the gate) | drops: to K / other own / enemy / none | median drop distance to K head | merges: n, median slack, drops to K | just-in-time merges: n, slack min-max, K longest, drops to K, median K eating delay | far pulls (d > 24): n, median change of d over 10 rounds | spread gate: dragons, median distance to our longest at the first gated turn, share >= 24 |');
out.push('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|');
const byMap = new Map(); for (const g of games) { if (!byMap.has(g.map)) byMap.set(g.map, []); byMap.get(g.map).push(g); }
for (const [m, gs] of [...byMap.entries(), ['all', games]]) {
  const fs_ = gs.flatMap(g => g.feeds), turns = gs.reduce((s, g) => s + g.turns, 0);
  const kinds = {}; for (const f of fs_) kinds[f.kind] = (kinds[f.kind] || 0) + 1;
  const drops = fs_.reduce((s, f) => s + f.drops, 0), toK = fs_.reduce((s, f) => s + f.toK, 0), toOwn = fs_.reduce((s, f) => s + f.toOwn, 0), toE = fs_.reduce((s, f) => s + f.toEnemy, 0);
  const merges = fs_.filter(f => f.merge);
  const short = fs_.filter(f => f.kL !== null && f.kBel !== null && f.kL < f.kBel), shortGate = short.filter(f => f.merge ? f.kL < f.L : f.kL < f.L + 2);
  const jits = fs_.filter(f => f.jit), fp = gs.flatMap(g => g.farPull), sg = gs.flatMap(g => g.sgFirst).filter(q => q.dist !== null);
  out.push(`| ${m} | ${gs.length} | ${turns} | ${TAGS.map(t => (100 * gs.reduce((s, g) => s + g.tags[t], 0) / Math.max(1, turns)).toFixed(1)).join(' / ')} | ${Object.entries(kinds).map(([k, n]) => k + ' ' + n).join(', ') || '–'} | ${pc(fs_.filter(f => f.kLongest).length, fs_.length)} | ${med(fs_.filter(f => f.agree !== null).map(f => Math.round(100 * f.agree)))}% | ${short.length} (${shortGate.length}) of ${fs_.length} | ${pc(toK, drops)} / ${pc(toOwn, drops)} / ${pc(toE, drops)} / ${pc(drops - toK - toOwn - toE, drops)} (${drops}) | ${med(fs_.flatMap(f => f.dropD))} | ${merges.length}, ${med(merges.map(f => f.slack))}, ${pc(merges.reduce((s, f) => s + f.toK, 0), merges.reduce((s, f) => s + f.drops, 0))} | ${jits.length}${jits.length ? `, ${Math.min(...jits.map(f => f.slack))}-${Math.max(...jits.map(f => f.slack))}, ${pc(jits.filter(f => f.kLongest).length, jits.length)}, ${pc(jits.reduce((s, f) => s + f.toK, 0), jits.reduce((s, f) => s + f.drops, 0))}, ${med(jits.flatMap(f => f.kDelay))}` : ''} | ${fp.length}${fp.length ? ', ' + med(fp) : ''} | ${sg.length}${sg.length ? `, ${med(sg.map(q => q.dist))}, ${pc(sg.filter(q => q.dist >= 24).length, sg.length)}` : ''} |`);
}
if (LIST) {
  out.push('', '## Feeds', '', '| game | r | donor | L | kind | K (L; believed) | K longest | declared same K | drop distances to K | to K / own / enemy of drops | slack | K eats within L + 5 rounds |', '|---|---|---|---|---|---|---|---|---|---|---|---|');
  for (const g of games) for (const f of g.feeds) out.push(`| ${g.key} | ${f.r} | #${f.id} | ${f.L} | ${f.kind}${f.merge ? ' m' : ''}${f.jit ? ' jit' : ''} | #${f.K} (${f.kL}; ${f.kBel ?? '–'}) | ${f.kLongest ? 'yes' : 'no'} | ${f.agree === null ? '–' : Math.round(100 * f.agree) + '% of ' + f.declN} | ${f.dropD.join(',')} | ${f.toK} / ${f.toOwn} / ${f.toEnemy} of ${f.drops} | ${f.slack} | ${f.kDelay.filter(x => x <= f.L + 5).length} of ${f.drops} |`);
}
const text = out.join('\n') + '\n';
if (OUT) fs.writeFileSync(path.resolve(ROOT, OUT), text); else process.stdout.write(text);
