#!/usr/bin/env node
// v1.6 local report: the conversion metrics of versions/v1.6/VERSION.md §3.2 for local sets (exp/v16/runq.js layout), one build against another on
// the same keys, plus CONV2's mechanism diagnostics.
// usage: node exp/v16/conv_report.js --sets <name>=<dir>[,<dir>] --sets <name>=<dir>[,<dir>] [--out report.md] [--prune] [--only-cache]
//   A dir may end in ?<regex> (only its keys matching it) or !<regex> (its keys not matching it), e.g. exp/gen/v12-S-H!stronghold,exp/gen/id-v13-S-H?stronghold
//   The first set is the treatment, the second the baseline (paired by key: opp:map:side:seed). Per-game results are cached in <dir>/conv16.jsonl
//   (delete it to recompute). --prune deletes a game's replay once its row is cached. --only-cache: no replay is read (cached rows only).
// Sources per game (unchanged research code, read-only):
//   exp/conversion/extract.js analyse (Codex): lineSacEat300 = sacrifice pearls of our team eaten by the active final line in r300-499 (drops made from
//     r250 included); the king curve r250-500 (the active final line's length); kingDeaths = deaths from r250 of our team's longest when it is >= 8;
//     sacrifice deaths from r250 with their drops' destinations (line / other ally / enemy / none); moments (heads, mass, other L >= 8 mass).
//   our own pass (tools/mass_ledger.js perGame): the label of each death's turn (a feed is "feed #<id> ..."; kind cv2 / sf / conv / late) and whether
//     the declared id is the active final line at the death (exp/conversion/targets.js's method: line = the final longest back through its parents,
//     a child takes the line from its birth); the CONV2 tags " ck#<id>" / " ck=" against our longest at that turn and the active final line, " cp",
//     " cy", " sq#"; K switches per dragon after r400.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const args = process.argv.slice(2);
const sets = []; for (let i = 0; i < args.length; i++) if (args[i] === '--sets') { const [n, d] = args[i + 1].split('='); sets.push({ name: n, dirs: d.split(',') }); }
const get = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const OUT = get('--out', null), PRUNE = args.includes('--prune'), ONLY_CACHE = args.includes('--only-cache');
const CACHE_DIR = get('--cache-dir', null);   // write the per-game cache here (<dir>/<set dir name>.conv16.jsonl) instead of inside the set (a set outside our write scope)
const MAPS = { slithery_fight: ['Slithery Fight', 'a'], slithery_fight_b: ['Slithery Fight', 'b'], schooltime: ['Schooltime', 'a'], schooltime_b: ['Schooltime', 'b'],
  trauma: ['Trauma', 'a'], default: ['Default', 'a'], autarky: ['Autarky', 'a'], devil: ['Devil', 'a'], devil_b: ['Devil', 'b'], trophy: ['Trophy', 'a'],
  queen_of_spades: ['Queen Of Spades', 'a'], queen_of_spades_b: ['Queen Of Spades', 'b'], portals: ['Portals', 'a'], prisoners_dilemma: ['Prisoners Dilemma', '6'],
  // held-out bundled maps (no spawn table: layout '?' keeps exp/spatial's geometry from reading a map file by name)
  arena: ['arena', '?'], big_empty: ['big_empty', '?'], Colosseum: ['Colosseum', '?'], default_small: ['default_small', '?'], stronghold: ['stronghold', '?'] };

function analyseGame(file, row) {
  const E = require(path.join(ROOT, 'exp', 'conversion', 'extract.js'));
  const S = require(path.join(ROOT, 'exp', 'spatial', 'lib.js'));
  const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const [mapName, layout] = MAPS[row.map];
  const us = row.side, R = S.raw.load(file);
  const g = E.analyse(R, { key: row.key, src: 'local', map: mapName, us, localLayout: layout, file });
  const x = g[us];
  // our own pass: labels, tags, lineage windows
  let idx = 0;
  const label = new Map(), births = new Map(), parent = new Map(), ckSeen = [], deathsL = [], lastCk = new Map(), switches = new Map(), eatenBy = new Map();
  const tags = { ck: 0, ckSelf: 0, ckLongest: 0, cp: 0, cy: 0, sq: 0, sfOnRow: 0, moves: 0 };
  let final = null;
  for (const d0 of R.match.map.initialDragons) { births.set(d0.id, -1); parent.set(d0.id, -1); }
  const hooks = {
    turn() { idx++; },
    indicator(e, r, c) {
      idx++; label.set(e.id, e.text || '');
      const d = c.drag.get(e.id); if (!d || d.team !== us) return;
      const t = e.text || '';
      if (r >= 250) {
        tags.moves++;
        const m = / ck(#(\d+)|=)/.exec(t);
        if (m) {
          const k = m[1] === '=' ? e.id : +m[2];
          tags.ck++; if (m[1] === '=') tags.ckSelf++;
          let best = null; for (const o of c.drag.values()) if (o.team === us && (!best || o.body.length > best.body.length || (o.body.length === best.body.length && o.id < best.id))) best = o;
          if (best && best.id === k) tags.ckLongest++;
          ckSeen.push([idx, k]);
          if (r >= 400) { const p = lastCk.get(e.id); if (p !== undefined && p !== k) switches.set(e.id, (switches.get(e.id) || 0) + 1); }
          lastCk.set(e.id, k);
        }
        if (/ cp\d+/.test(t)) tags.cp++;
        if (/ cy\d+/.test(t)) tags.cy++;
        if (/ sq#\d+/.test(t)) tags.sq++;
        if (/ conv sf#\d+| sf#\d+ a\d+ late/.test(t)) tags.sfOnRow++;
      }
    },
    split(p, ch) { idx++; births.set(ch.id, idx); parent.set(ch.id, p.id); },
    death(d, rec, i, other, r) {
      idx++;
      if (d.team !== us || r < 250 || ML.CAUSE[rec.cause] !== 'sac') return;
      deathsL.push({ idx, r, id: d.id, len: rec.len, label: label.get(d.id) || '', ml: i });
    },
    eat(d, k, o) { if (o >= 0) { let a = eatenBy.get(o); if (!a) eatenBy.set(o, a = []); a.push(d.team === us ? d.id : -1); } },
    end(n, c) { const a = [...c.drag.values()].filter(d => d.team === us).sort((a, b) => b.body.length - a.body.length || a.id - b.id); final = a.length ? a[0].id : null; },
  };
  ML.perGame(R, { map: mapName, variant: layout }, hooks);
  const line = []; for (let id = final; id !== null && id !== undefined && id >= 0; id = parent.get(id)) line.push(id);
  line.reverse();
  const windows = line.map((id, j) => ({ id, from: births.get(id), to: j + 1 < line.length ? births.get(line[j + 1]) : Infinity }));
  const activeAt = i => { const w = windows.find(w => w.from < i && i < w.to); return w ? w.id : null; };
  let ckLine = 0; for (const [i, k] of ckSeen) if (activeAt(i) === k) ckLine++;
  // feeds: the labelled sacrifices from r250, matched to the extractor's sacrifice deaths (same team, id, round) for their drops
  const sacs = g.deaths.filter(d => d.team === us && d.cause === 0);
  const feeds = [];
  for (const d of deathsL) {
    const m = /^feed #(\d+) d(\d+) L(\d+)(.*)$/.exec(d.label); if (!m) continue;
    const rest = m[4], kind = / cv2/.test(rest) ? 'cv2' : / late/.test(rest) ? 'late' : / conv sf#/.test(rest) ? 'sf' : / conv/.test(rest) ? 'conv' : 'feed';
    const s = sacs.find(q => q.id === d.id && q.r === d.r);
    const eaters = eatenBy.get(d.ml) || [];
    const rl = (/ (?:k|a)(\d+)/.exec(rest) || [])[1];
    feeds.push({ r: d.r, id: d.id, len: d.len, target: +m[1], dist: +m[2], kind, merge: / m$/.test(rest) || / m /.test(rest), onLine: activeAt(d.idx) === +m[1], rl: rl ? +rl : null,
      toTarget: eaters.filter(e => e === +m[1]).length, toOtherOwn: eaters.filter(e => e >= 0 && e !== +m[1]).length,
      drops: s ? s.drops.length : null, toLine: s ? s.toLine : null, toAlly: s ? s.toAlly : null, toEnemy: s ? s.toEnemy : null, none: s ? s.none : null });
  }
  const sum = (a, f) => a.reduce((t, v) => t + f(v), 0);
  const s300 = sacs.filter(d => d.r >= 300);
  const eats300 = x.eats.filter(e => e.r >= 300);
  return {
    key: row.key, map: mapName + '/' + layout, opp: row.opp, side: us, seed: row.seed, rounds: g.rounds, won: row.won ? 1 : 0, G: row.G,
    elim: row.endReason === 'teamEliminated' && !row.alive ? 1 : 0, checks: g.checks,
    curve: x.curve, moments: x.moments,
    lineSacEat300: eats300.filter(e => e.origin >= 0 && e.originTeam === us && e.cause === 0).length,
    lineNat300: eats300.filter(e => e.origin < 0).length,
    sac250: { n: sacs.length, drops: sum(sacs, d => d.drops.length), line: sum(sacs, d => d.toLine), ally: sum(sacs, d => d.toAlly), enemy: sum(sacs, d => d.toEnemy), none: sum(sacs, d => d.none) },
    sac300: { n: s300.length, drops: sum(s300, d => d.drops.length), line: sum(s300, d => d.toLine), ally: sum(s300, d => d.toAlly), enemy: sum(s300, d => d.toEnemy), none: sum(s300, d => d.none) },
    kingDeaths: x.kingDeaths.map(d => [d.r, d.cause, d.len]),
    feeds, tags, ckLine, kSwitches400: [...switches.values()].reduce((a, b) => a + b, 0), kSwitchDragons: switches.size,
  };
}

function loadSet(s) {
  const out = [];
  for (const spec of s.dirs) {
    const fm = /^([^?!]+)([?!])(.+)$/.exec(spec), d = fm ? fm[1] : spec, keyOk = fm ? (k => new RegExp(fm[3]).test(k) === (fm[2] === '?')) : (() => true);
    const dir = path.resolve(ROOT, d), rowsFile = path.join(dir, 'rows.jsonl');
    const cacheFile = CACHE_DIR ? path.join(path.resolve(ROOT, CACHE_DIR), path.basename(dir) + '.conv16.jsonl') : path.join(dir, 'conv16.jsonl');
    if (CACHE_DIR) fs.mkdirSync(path.resolve(ROOT, CACHE_DIR), { recursive: true });
    if (!fs.existsSync(rowsFile)) { console.error('no rows', dir); continue; }
    const rows = new Map(); for (const l of fs.readFileSync(rowsFile, 'utf8').split('\n').filter(Boolean)) { const r = JSON.parse(l); if (r.G !== undefined && !r.error && !r.botProblem) rows.set(r.key, r); }
    const cache = new Map(); if (fs.existsSync(cacheFile)) for (const l of fs.readFileSync(cacheFile, 'utf8').split('\n').filter(Boolean)) { const r = JSON.parse(l); cache.set(r.key, r); }
    for (const [key, row] of rows) {
      if (!MAPS[row.map] || !keyOk(key)) continue;
      let a = cache.get(key);
      const file = path.join(dir, 'games', key.replace(/:/g, '_'), 'game.replay');
      if (!a && !ONLY_CACHE && fs.existsSync(file)) {
        try { a = analyseGame(file, row); fs.appendFileSync(cacheFile, JSON.stringify(a) + '\n'); cache.set(key, a); }
        catch (e) { console.error('analyse failed', key, e.stack.split('\n').slice(0, 3).join(' | ')); continue; }
      }
      if (!a) continue;
      if (PRUNE && fs.existsSync(file)) fs.rmSync(file);
      out.push(a);
    }
  }
  return out;
}

const mean = a => a.length ? a.reduce((s, v) => s + v, 0) / a.length : NaN;
const f1 = v => Number.isFinite(v) ? v.toFixed(1) : '–', f0 = v => Number.isFinite(v) ? v.toFixed(0) : '–', pc = (a, b) => b ? (100 * a / b).toFixed(0) + '%' : '–';
// exact two-sided sign test on the nonzero paired differences
function signP(pos, neg) {
  const n = pos + neg; if (!n) return 1; const k = Math.min(pos, neg); let p = 0, c = 1;
  for (let i = 0; i <= n; i++) { if (i <= k) p += c; c = c * (n - i) / (i + 1); }
  return Math.min(1, 2 * p / Math.pow(2, n));
}
function summary(games) {
  const fe = games.flatMap(g => g.feeds);
  const s3 = games.map(g => g.sac300), kd = games.flatMap(g => g.kingDeaths);
  const cv = r => mean(games.map(g => g.curve[r]).filter(v => v !== null && v !== undefined));
  const mo = (r, k) => mean(games.map(g => g.moments[r] ? g.moments[r][k] : null).filter(v => v !== null && v !== undefined));
  return {
    N: games.length, wins: games.reduce((s, g) => s + g.won, 0), elim: games.reduce((s, g) => s + g.elim, 0), G: mean(games.map(g => g.G)),
    curve: [300, 350, 400, 450, 500].map(cv), lineSac: mean(games.map(g => g.lineSacEat300)), lineNat: mean(games.map(g => g.lineNat300)),
    feeds: fe.length / games.length, feedsLabelled: fe.length, onLine: fe.filter(f => f.onLine).length,
    drops300: s3.reduce((s, v) => s + v.drops, 0), line300: s3.reduce((s, v) => s + v.line, 0), ally300: s3.reduce((s, v) => s + v.ally, 0),
    enemy300: s3.reduce((s, v) => s + v.enemy, 0), none300: s3.reduce((s, v) => s + v.none, 0),
    kdNonSac: kd.filter(d => d[1] !== 0).length, kdSac: kd.filter(d => d[1] === 0).length,
    heads: [250, 350, 450].map(r => mo(r, 'heads')), mass: [250, 350, 450].map(r => mo(r, 'mass')), big450: mo(450, 'otherBigMass'),
    kinds: fe.reduce((o, f) => (o[f.kind] = (o[f.kind] || 0) + 1, o), {}),
  };
}

const T = sets.map(s => ({ name: s.name, games: loadSet(s) }));
if (T.length < 1) { console.error('usage: --sets name=dir[,dir] [--sets name=dir]'); process.exit(2); }
const L = [];
const say = s => L.push(s);
say(`# v1.6 conversion report (${new Date().toISOString().slice(0, 16)}Z)`);
say('');
say('Sets: ' + T.map(t => `${t.name} = ${sets.find(s => s.name === t.name).dirs.join(', ')} (${t.games.length} games)`).join('; '));
say('');
const mapsAll = [...new Set(T.flatMap(t => t.games.map(g => g.map)))].sort();
const groups = [...mapsAll.map(m => [m, g => g.map === m]), ['all', () => true]];
// paired keys
const keyed = T.map(t => new Map(t.games.map(g => [g.key + '|' + g.map, g])));
const both = T.length > 1 ? [...keyed[0].keys()].filter(k => keyed[1].has(k)) : [...keyed[0].keys()];
say(`Paired keys: ${both.length}` + (T.length > 1 ? ` (first set ${keyed[0].size}, second ${keyed[1].size})` : ''));
say('');
say('## Outcome and conversion (per game; paired keys only)');
say('');
say('| map | set | N | wins | elim | final longest | king r300/350/400/450/500 | r300-499 king sac pearls | king natural r300+ | feeds/game | declared target = final line | r300+ sac drops: line/ally/enemy/none | king deaths non-sac / sac | heads r250/350/450 | mass r250/350/450 | other L>=8 mass r450 |');
say('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|');
for (const [gname, pred] of groups) for (let i = 0; i < T.length; i++) {
  const games = both.filter(k => pred(keyed[i].get(k))).map(k => keyed[i].get(k)); if (!games.length) continue;
  const s = summary(games);
  say(`| ${gname} | ${T[i].name} | ${s.N} | ${s.wins} | ${s.elim} | ${f1(s.G)} | ${s.curve.map(f1).join(' / ')} | ${f1(s.lineSac)} | ${f1(s.lineNat)} | ${f1(s.feeds)} | ${s.onLine}/${s.feedsLabelled} (${pc(s.onLine, s.feedsLabelled)}) | ${pc(s.line300, s.drops300)} / ${pc(s.ally300, s.drops300)} / ${pc(s.enemy300, s.drops300)} / ${pc(s.none300, s.drops300)} (${s.drops300}) | ${s.kdNonSac} / ${s.kdSac} | ${s.heads.map(f0).join(' / ')} | ${s.mass.map(f0).join(' / ')} | ${f1(s.big450)} |`);
}
if (T.length > 1) {
  say('');
  say(`## Paired differences (${T[0].name} − ${T[1].name}): mean, then + / 0 / − pairs and the two-sided sign test p`);
  say('');
  say('| map | pairs | r300-499 king sac pearls | final longest | king r400 | king r500 | wins | eliminations |');
  say('|---|---|---|---|---|---|---|---|');
  for (const [gname, pred] of groups) {
    const ks = both.filter(k => pred(keyed[0].get(k))); if (!ks.length) continue;
    const cell = f => { const d = ks.map(k => f(keyed[0].get(k)) - f(keyed[1].get(k))).filter(Number.isFinite); const p = d.filter(v => v > 0).length, n = d.filter(v => v < 0).length;
      return `${d.length ? (mean(d) >= 0 ? '+' : '') + mean(d).toFixed(1) : '–'} (${p}/${d.length - p - n}/${n}, p ${signP(p, n).toFixed(3)})`; };
    const sumOf = f => ks.reduce((s, k) => s + f(keyed[0].get(k)), 0) + ' vs ' + ks.reduce((s, k) => s + f(keyed[1].get(k)), 0);
    say(`| ${gname} | ${ks.length} | ${cell(g => g.lineSacEat300)} | ${cell(g => g.G)} | ${cell(g => g.curve[400] ?? NaN)} | ${cell(g => g.curve[500] ?? NaN)} | ${sumOf(g => g.won)} | ${sumOf(g => g.elim)} |`);
  }
}
say('');
say('## CONV2 mechanism (the tags of each set; r >= 250, our moves)');
say('');
say('| map | set | feeds by kind | cv2 feeds: piece / mid / big (merge) | cv2 feeds r250-349 / 350-399 / 400-499 | cv2 on final line | feed drops eaten by the declared target / another of ours / all | sf labels on the row after r250 | ck turns: = longest / = final line / self | K switches after r400 (dragons) | cp turns | cy turns | sq turns | moves |');
say('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|');
for (const [gname, pred] of groups) for (let i = 0; i < T.length; i++) {
  const games = both.filter(k => pred(keyed[i].get(k))).map(k => keyed[i].get(k)); if (!games.length) continue;
  const fe = games.flatMap(g => g.feeds), cv = fe.filter(f => f.kind === 'cv2');
  const t = games.reduce((o, g) => { for (const [k, v] of Object.entries(g.tags)) o[k] = (o[k] || 0) + v; return o; }, {});
  const kinds = fe.reduce((o, f) => (o[f.kind] = (o[f.kind] || 0) + 1, o), {});
  const ckLine = games.reduce((s, g) => s + g.ckLine, 0);
  say(`| ${gname} | ${T[i].name} | ${Object.entries(kinds).map(([k, v]) => k + ' ' + v).join(', ') || '–'} | ${cv.filter(f => f.len <= 4).length} / ${cv.filter(f => f.len >= 5 && f.len <= 7).length} / ${cv.filter(f => f.len >= 8).length} | ${cv.filter(f => f.r < 350).length} / ${cv.filter(f => f.r >= 350 && f.r < 400).length} / ${cv.filter(f => f.r >= 400).length} | ${cv.filter(f => f.onLine).length}/${cv.length} | ${fe.reduce((s, f) => s + (f.toTarget || 0), 0)} / ${fe.reduce((s, f) => s + (f.toOtherOwn || 0), 0)} / ${fe.reduce((s, f) => s + (f.drops || 0), 0)} | ${t.sfOnRow || 0} | ${pc(t.ckLongest || 0, t.ck)} / ${pc(ckLine, t.ck)} / ${t.ckSelf || 0} (${t.ck || 0}) | ${games.reduce((s, g) => s + g.kSwitches400, 0)} (${games.reduce((s, g) => s + g.kSwitchDragons, 0)}) | ${t.cp || 0} | ${t.cy || 0} | ${t.sq || 0} | ${t.moves || 0} |`);
}
say('');
say('## Feeds by the recipient length the donor saw (r >= 250; all labelled feeds): N, on the final line, drops eaten by the declared target / all drops');
say('');
say('| map | set | recipient < 8 | 8-15 | >= 16 |');
say('|---|---|---|---|---|');
for (const [gname, pred] of groups) for (let i = 0; i < T.length; i++) {
  const games = both.filter(k => pred(keyed[i].get(k))).map(k => keyed[i].get(k)); if (!games.length) continue;
  const fe = games.flatMap(g => g.feeds).filter(f => f.rl !== null && f.rl !== undefined);
  const cell = a => `${a.length}: ${pc(a.filter(f => f.onLine).length, a.length)} line, ${a.reduce((s, f) => s + (f.toTarget || 0), 0)}/${a.reduce((s, f) => s + (f.drops || 0), 0)}`;
  say(`| ${gname} | ${T[i].name} | ${cell(fe.filter(f => f.rl < 8))} | ${cell(fe.filter(f => f.rl >= 8 && f.rl < 16))} | ${cell(fe.filter(f => f.rl >= 16))} |`);
}
say('');
say('Definitions: versions/v1.6/VERSION.md §3.2. "declared target = final line": labelled feeds (`feed #<id>`) from r250 whose id is the active final line at the death. "king deaths": deaths from r250 of our longest at that moment when it is >= 8 (the extractor\'s kingDeaths), non-sacrifice causes vs sacrifice. Replay checks (sim, splits, drops, lineage) summed over the games: ' +
  JSON.stringify(T.map(t => t.games.reduce((o, g) => { for (const [k, v] of Object.entries(g.checks || {})) o[k] = (o[k] || 0) + v; return o; }, {}))));
const text = L.join('\n') + '\n';
if (OUT) fs.writeFileSync(path.resolve(ROOT, OUT), text);
process.stdout.write(text);
