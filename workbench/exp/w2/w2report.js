#!/usr/bin/env node
// W2 report (versions/v1.6.1/VERSION.md §4): two local sets on the same keys (exp/v14/runq14.js layout), base (v1.6) and new (v1.6.1).
//   identity  per key: strict fingerprint (tools/fingerprint.js: every event but indicators) and behaviour fingerprint (also without the sonar
//             values, which v1.6.1 changes for undecided senders); and whether the recognition timing of every process is the same (the
//             round of each of our processes' first decided " map=<Name>/<a|b|?>" tag, and the set of processes);
//   timing    per map: start processes (id below the map's dragon count) decided on their first turn; children decided on their first turn,
//             delay in own turns (median, p90, max) of the later ones, never decided; per set;
//   misrecognition  on maps outside the table (held-out): processes with a decided tag, and our turns with E=S;
//   tags      v1.6.1's " mg=" " ms" " mn" " mc";
//   outcome   wins, eliminated, final longest ours (row G) per map and pooled, paired higher / lower / equal and a two-sided sign test.
// Per-replay results are cached in exp/w2/cache (keyed by the replay's size and mtime).
// usage: node exp/w2/w2report.js --base exp/w2/v16-K --new exp/w2/v161-K [--keys <regex>] [--ids]
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const BASE = opt('--base'), NEW = opt('--new'), KEYS = new RegExp(opt('--keys', '.')), SHOW_IDS = args.includes('--ids');
const CACHE = path.join(__dirname, 'cache'); fs.mkdirSync(CACHE, { recursive: true });
const HELDOUT = new Set(['arena', 'big_empty', 'Colosseum', 'default_small', 'stronghold']);
let load = null;
function rows(dir) {
  const f = path.join(ROOT, dir, 'rows.jsonl'), m = new Map();
  if (!fs.existsSync(f)) return m;
  for (const l of fs.readFileSync(f, 'utf8').split('\n')) { if (!l.trim()) continue; const r = JSON.parse(l); if (r.G !== undefined && r.exit === 0 && !r.error && !r.botProblem) m.set(r.key, r); }
  return m;
}
function analyse(dir, row) {
  const file = path.join(ROOT, dir, 'games', row.key.replace(/:/g, '_'), 'game.replay');
  const st = fs.statSync(file), ck = path.join(CACHE, `${path.basename(dir)}__${row.key.replace(/:/g, '_')}.json`);
  if (fs.existsSync(ck)) { const c = JSON.parse(fs.readFileSync(ck, 'utf8')); if (c.size === st.size && c.mtime === st.mtimeMs) return c; }
  if (!load) load = makeLoader(viewerSource());
  const R = load(file), us = row.side;
  const hs = crypto.createHash('sha256'), hb = crypto.createHash('sha256');
  const n0 = R.match.map.initialDragons.length;
  const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
  const P = new Map();   // id -> {first round, turns, dec: own-turn index of the first decided tag, decRound}
  const tags = { mg: 0, ms: 0, mn: 0, mc: 0 }, eng = { F: 0, S: 0, W: 0 };
  let round = -1;
  for (const e of R.events) {
    if (e.type !== 'dragonIndicator' && e.type !== 'dragonLog' && e.type !== 'debugDraw' && e.type !== 'engineLog') {
      const o = {}, b = {};
      for (const [k, v] of Object.entries(e)) {
        if (k === 'instructions') continue;
        const vv = typeof v === 'bigint' ? String(v) : v;
        o[k] = vv;
        if (!(e.type === 'sonarPing' && (k === 'value' || k === 'value64'))) b[k] = vv;
      }
      hs.update(JSON.stringify(o)); hb.update(JSON.stringify(b));
    }
    if (e.type === 'roundStart') round = e.round;
    else if (e.type === 'dragonSplit') team.set(e.childId, e.team);
    else if (e.type === 'turnStart' && team.get(e.id) === us) {
      const p = P.get(e.id) || { first: round, turns: 0, dec: null, decRound: null, firstTag: null };
      p.turns++; P.set(e.id, p);
    } else if (e.type === 'dragonIndicator' && team.get(e.id) === us) {
      const t = e.text || '', p = P.get(e.id);
      const m = / E=([A-Z])$/.exec(t); if (m && eng[m[1]] !== undefined) eng[m[1]]++;
      for (const x of t.matchAll(/(?:^| )(mg=\S+|ms\d+|mn|mc)(?= |$)/g)) tags[x[1].slice(0, 2)]++;
      const mm = /(?:^| )map=(\S+)/.exec(t);
      if (mm && p) {
        if (p.firstTag === null) p.firstTag = mm[1];
        if (p.dec === null && mm[1] !== 'none' && mm[1] !== '?') { p.dec = p.turns - 1; p.decRound = round; p.decMap = mm[1]; }
      }
    }
  }
  const procs = [...P.entries()].map(([id, p]) => ({ id, start: id < n0, first: p.first, turns: p.turns, dec: p.dec, decRound: p.decRound, decMap: p.decMap || null, firstTag: p.firstTag }));
  const c = { size: st.size, mtime: st.mtimeMs, strict: hs.digest('hex').slice(0, 16), behav: hb.digest('hex').slice(0, 16), procs, tags, eng };
  fs.writeFileSync(ck, JSON.stringify(c));
  return c;
}
const rb = rows(BASE), rn = rows(NEW);
const keys = [...rb.keys()].filter(k => rn.has(k) && KEYS.test(k)).sort();
const mapOf = k => k.split(':')[1];
const per = {}, pool = { n: 0, wb: 0, wn: 0, eb: 0, en: 0, gb: 0, gn: 0, hi: 0, lo: 0, eq: 0 };
const idRows = [];
const timing = {};   // set -> map -> stats
const mis = {};      // map -> {procs, turnsS}
const tagTot = {};
function tstat(set, map, c) {
  const T = ((timing[set] = timing[set] || {})[map] = timing[set][map] || { start: 0, start0: 0, kids: 0, kid0: 0, delays: [], never: 0, neverAlive: [] });
  for (const p of c.procs) {
    if (p.start) { T.start++; if (p.dec === 0) T.start0++; continue; }
    T.kids++;
    if (p.dec === 0) T.kid0++; else if (p.dec !== null) T.delays.push(p.dec); else { T.never++; T.neverAlive.push(p.turns); }
  }
}
for (const k of keys) {
  const m = mapOf(k), b = rb.get(k), n = rn.get(k);
  const cb = analyse(BASE, b), cn = analyse(NEW, n);
  const P = per[m] = per[m] || { n: 0, wb: 0, wn: 0, eb: 0, en: 0, gb: 0, gn: 0, hi: 0, lo: 0, eq: 0 };
  for (const Q of [P, pool]) {
    Q.n++; Q.wb += b.won ? 1 : 0; Q.wn += n.won ? 1 : 0; Q.eb += b.alive ? 0 : 1; Q.en += n.alive ? 0 : 1; Q.gb += b.G; Q.gn += n.G;
    if (n.G > b.G) Q.hi++; else if (n.G < b.G) Q.lo++; else Q.eq++;
  }
  // timing equality: every process id with the same first decided round, and the same set of processes
  const db = new Map(cb.procs.map(p => [p.id, p.decRound])), dn = new Map(cn.procs.map(p => [p.id, p.decRound]));
  let same = db.size === dn.size, firstDiff = null;
  for (const [id, r] of db) if (!dn.has(id) || dn.get(id) !== r) { same = false; if (firstDiff === null || id < firstDiff.id) firstDiff = { id, base: r, new: dn.has(id) ? dn.get(id) : 'absent' }; }
  idRows.push({ k, timingSame: same, strict: cb.strict === cn.strict, behav: cb.behav === cn.behav, firstDiff, wb: b.won, wn: n.won, gb: b.G, gn: n.G, eb: !b.alive, en: !n.alive });
  tstat('base', m, cb); tstat('new', m, cn);
  if (HELDOUT.has(m)) {
    for (const [set, c] of [['base', cb], ['new', cn]]) {
      const M = ((mis[set] = mis[set] || {})[m] = mis[set][m] || { games: 0, gamesMis: 0, procs: 0, turnsS: 0, maps: {} });
      M.games++; const bad = c.procs.filter(p => p.dec !== null); if (bad.length) M.gamesMis++;
      M.procs += bad.length; M.turnsS += c.eng.S; for (const p of bad) M.maps[p.decMap] = (M.maps[p.decMap] || 0) + 1;
    }
  }
  for (const [t, v] of Object.entries(cn.tags)) { const T = (tagTot[m] = tagTot[m] || { mg: 0, ms: 0, mn: 0, mc: 0 }); T[t] += v; }
}
function signP(hi, lo) { const n = hi + lo; if (!n) return 1; const k = Math.min(hi, lo); let p = 0; let c = 1; for (let i = 0; i <= n; i++) { if (i > 0) c = c * (n - i + 1) / i; if (i <= k) p += c; } return Math.min(1, 2 * p / Math.pow(2, n)); }
const f1 = x => x.toFixed(1);
console.log(`W2 report: base ${BASE} vs new ${NEW}, ${keys.length} paired keys${opt('--keys') ? ' matching ' + opt('--keys') : ''}`);
console.log('\n== outcome (new vs base): wins, eliminated, final longest mean, paired final longest higher/lower/equal, sign p');
for (const [m, P] of Object.entries(per).concat([['POOLED', pool]])) console.log(`${m.padEnd(18)} n ${String(P.n).padStart(3)}  wins ${P.wn} vs ${P.wb}  elim ${P.en} vs ${P.eb}  final ${f1(P.gn / P.n)} vs ${f1(P.gb / P.n)}  ${P.hi}/${P.lo}/${P.eq}  p ${signP(P.hi, P.lo).toFixed(3)}`);
console.log('\n== recognition timing per map (own turns): start decided on 1st turn; children decided on 1st turn / later (median p90 max) / never');
const q = (a, p) => { if (!a.length) return '-'; const s = a.slice().sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
for (const m of Object.keys(per)) for (const set of ['base', 'new']) {
  const T = timing[set][m];
  console.log(`${(set === 'base' ? m : '').padEnd(18)} ${set.padEnd(4)} start ${T.start0}/${T.start}  children ${T.kids}: 1st turn ${T.kid0} (${(100 * T.kid0 / Math.max(1, T.kids)).toFixed(0)}%)  later ${T.delays.length} (median ${q(T.delays, .5)} p90 ${q(T.delays, .9)} max ${T.delays.length ? Math.max(...T.delays) : '-'})  never ${T.never}${T.never ? ` (lived median ${q(T.neverAlive, .5)} turns)` : ''}  <=3 turns ${(100 * (T.kid0 + T.delays.filter(x => x <= 3).length) / Math.max(1, T.kids)).toFixed(0)}%`);
}
if (Object.keys(mis).length) {
  console.log('\n== misrecognition on held-out maps: games with any decided tag / games, processes, our E=S turns');
  for (const set of ['base', 'new']) for (const [m, M] of Object.entries(mis[set] || {})) console.log(`${set.padEnd(4)} ${m.padEnd(14)} ${M.gamesMis}/${M.games}  processes ${M.procs} ${JSON.stringify(M.maps)}  E=S turns ${M.turnsS}`);
}
console.log('\n== v1.6.1 tags (new set): mg (gate held a decision), ms (start check dropped), mn (none from a message), mc (decided on a confirmation)');
for (const [m, T] of Object.entries(tagTot)) console.log(`${m.padEnd(18)} mg ${T.mg}  ms ${T.ms}  mn ${T.mn}  mc ${T.mc}`);
const ts = idRows.filter(r => r.timingSame);
console.log(`\n== identity: timing unchanged in ${ts.length}/${idRows.length} games; of those strict identical ${ts.filter(r => r.strict).length}, behaviour identical ${ts.filter(r => r.behav).length}`);
console.log(`   timing changed in ${idRows.length - ts.length} games: strict identical ${idRows.filter(r => !r.timingSame && r.strict).length}, behaviour identical ${idRows.filter(r => !r.timingSame && r.behav).length}`);
const ch = idRows.filter(r => !r.timingSame);
if (ch.length) {
  let wB = 0, wN = 0, eB = 0, eN = 0, hi = 0, lo = 0, eq = 0, gB = 0, gN = 0;
  for (const r of ch) { wB += r.wb; wN += r.wn; eB += r.eb; eN += r.en; gB += r.gb; gN += r.gn; if (r.gn > r.gb) hi++; else if (r.gn < r.gb) lo++; else eq++; }
  console.log(`   outcome in the timing-changed games (new vs base): wins ${wN} vs ${wB}, elim ${eN} vs ${eB}, final ${f1(gN / ch.length)} vs ${f1(gB / ch.length)}, ${hi}/${lo}/${eq}, p ${signP(hi, lo).toFixed(3)}`);
}
for (const r of idRows) if (SHOW_IDS || (r.timingSame && !r.behav)) console.log(`   ${r.k.padEnd(40)} timing ${r.timingSame ? 'same' : 'CHANGED ' + JSON.stringify(r.firstDiff)} strict ${r.strict ? '=' : '≠'} behaviour ${r.behav ? '=' : '≠'}  G ${r.gb} -> ${r.gn}${r.wb !== r.wn ? (r.wn ? ' (new wins)' : ' (new loses)') : ''}`);
