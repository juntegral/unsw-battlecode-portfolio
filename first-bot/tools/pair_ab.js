#!/usr/bin/env node
// Variant-weighted paired screen (maps/server-b/README.md): runs are `<prefix>-a-<set>` (tools/eval.js, seed 1 on
// maps/online-20260927 = the server's layout a) and `<prefix>-b-<set>` (seed 2 on maps/server-b = layout b of Devil, Queen
// Of Spades, Schooltime, Slithery Fight and 10-dragon Prisoners Dilemma, plus the five one-layout maps). Sets: px4 =
// proxy4_swarm,proxy4_elim,proxy4_king; old4 = replay_rules_v8,archetype_swarm,archetype_hunter,h2.
//
// usage (repository root):
//   node tools/pair_ab.js --cand <prefix> --base <prefix> [--sets px4,old4] [--bot <dir>] [--par 2] [--json <file>]
//       Pairs cand and base games by key (opp:map:side:seed) inside the a runs and inside the b runs and prints mean
//       differences cand - base of G, win and survival with 95% paired t intervals: all, per set, the two-layout maps
//       on a and on b, the one-layout maps, per map (a and b pooled) and, for the five two-layout maps, a and b apart.
//       The "all" line also has the map-cluster bootstrap interval of dG (as tools/eval.js --baseline).
//       --bot <dir>: first plays the cand runs that are missing (tools/eval.js --jobs 2; an eval starts only while the
//       machine runs at most 4 judge processes, so the total stays at 6 or fewer; at most --par evals at once).
//   node tools/pair_ab.js --base <prefix> [--sets px4,old4]
//       One bot alone: G, win and survival per map and layout (95%: t interval for G floored at 0, Wilson for shares),
//       and the a -> b change of G per two-layout map (unpaired, normal interval). That change also carries the seed
//       (a is seed 1, b seed 2); for the layout alone pair the same seeds: exp/proxy4-tools/ab_matched.js.
// Layout of a row: b if it comes from a b run and its map file is a second layout (_b, _10), else a.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..');
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const SETS = { px4: 'proxy4_swarm,proxy4_elim,proxy4_king', old4: 'replay_rules_v8,archetype_swarm,archetype_hunter,h2' };
const RUNS = { a: { maps: 'maps/online-20260927', seed: 1 }, b: { maps: 'maps/server-b', seed: 2 } };
const cand = arg('cand'), base = arg('base'), sets = arg('sets', 'px4,old4').split(',');
if (!base) { console.error('need --base <prefix> (and --cand <prefix> for a paired screen)'); process.exit(2); }
const label = (p, v, s) => `${p}-${v}-${s}`;
const readRows = L => { const f = path.join(ROOT, 'exp', L, 'rows.jsonl'); if (!fs.existsSync(f)) return null; const seen = new Set(), out = [];
  for (const l of fs.readFileSync(f, 'utf8').split('\n')) { if (!l.trim()) continue; let r; try { r = JSON.parse(l); } catch { continue; } if (r.G === undefined || seen.has(r.key)) continue; seen.add(r.key); out.push(r); } return out; };
const baseMap = m => m.replace(/_b$|_10$/, ''), layoutOf = (v, m) => v === 'b' && /_b$|_10$/.test(m) ? 'b' : 'a';
const TWO = new Set(['devil', 'queen_of_spades', 'schooltime', 'slithery_fight', 'prisoners_dilemma']);

// ---- statistics ----
const mean = a => a.reduce((s, x) => s + x, 0) / a.length;
function tq(nu) { const z = 1.959964; if (nu < 1) return NaN; if (nu === 1) return 12.706; if (nu === 2) return 4.303; return z + (z ** 3 + z) / (4 * nu) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * nu * nu); }
function ci(a) { const n = a.length, m = mean(a); if (n < 2) return [m, NaN, NaN]; const sd = Math.sqrt(a.reduce((s, x) => s + (x - m) ** 2, 0) / (n - 1)), h = tq(n - 1) * sd / Math.sqrt(n); return [m, m - h, m + h]; }
function clusterBoot(pairs) { // map-cluster bootstrap of mean dG (tools/eval.js)
  const maps = [...new Set(pairs.map(p => p.map))].map(m => pairs.filter(p => p.map === m));
  let s = 20260927; const rnd = () => (s = (Math.imul(s, 1103515245) + 12345) >>> 0) / 4294967296, reps = [];
  for (let k = 0; k < 4000; k++) { const pick = maps.map(() => maps[Math.floor(rnd() * maps.length)]).flat(); reps.push(mean(pick.map(p => p.dG))); }
  reps.sort((x, y) => x - y); return [reps[Math.floor(0.025 * reps.length)], reps[Math.floor(0.975 * reps.length)]];
}
const f = (x, d = 2) => Number.isFinite(x) ? (x >= 0 ? '+' : '') + x.toFixed(d) : '-';
const fmt = ([m, lo, hi], d = 2) => `${f(m, d)} [${f(lo, d)}, ${f(hi, d)}]`;
const pct = ([m, lo, hi]) => `${f(100 * m, 0)} [${f(100 * lo, 0)}, ${f(100 * hi, 0)}]`;

// ---- optional: play the missing cand runs ----
const judges = () => { try { return +cp.execSync("ps -axo command | grep -c '[u]nswbc-clean.py run' || true").toString().trim(); } catch { return 0; } };
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function playMissing(bot) {
  const todo = [];
  for (const s of sets) for (const v of ['a', 'b']) { const rows = readRows(label(cand, v, s)), need = SETS[s].split(',').length * 10 * 2; if (!rows || rows.length < need) todo.push({ s, v }); }
  const par = +arg('par', 2), live = new Set();
  for (const t of todo) {
    for (;;) { if (live.size < par && judges() <= 4) break; await sleep(5000); }
    const L = label(cand, t.v, t.s), args = ['tools/eval.js', '--bot', bot, '--label', L, '--maps', RUNS[t.v].maps, '--seeds', String(RUNS[t.v].seed), '--opps', SETS[t.s], '--jobs', '2'];
    console.error(`start ${L} (judges running: ${judges()})`);
    const p = new Promise(res => { const c = cp.spawn('node', args, { cwd: ROOT, stdio: ['ignore', 'inherit', 'inherit'] }); c.on('close', res); });
    live.add(p); p.then(() => live.delete(p));
    await sleep(8000); // let the eval start its games before the next machine check
  }
  await Promise.all([...live]);
}

// ---- report ----
function load(prefix) {
  const out = [];
  for (const s of sets) for (const v of ['a', 'b']) { const rows = readRows(label(prefix, v, s)); if (!rows) { console.error(`missing run exp/${label(prefix, v, s)}`); continue; }
    for (const r of rows) out.push({ ...r, set: s, run: v, bmap: baseMap(r.map), layout: layoutOf(v, r.map) }); }
  return out;
}
const groups = rows => {
  const g = [['all', () => true]];
  if (sets.length > 1) for (const s of sets) g.push([`set ${s}`, r => r.set === s]);
  g.push(['two-layout maps, a (seed 1)', r => TWO.has(r.bmap) && r.layout === 'a'], ['two-layout maps, b (seed 2)', r => r.layout === 'b'], ['one-layout maps (seeds 1, 2)', r => !TWO.has(r.bmap)]);
  for (const m of [...new Set(rows.map(r => r.bmap))].sort()) { g.push([`${m}`, r => r.bmap === m]); if (TWO.has(m)) g.push([`${m} a`, r => r.bmap === m && r.layout === 'a'], [`${m} b`, r => r.bmap === m && r.layout === 'b']); }
  return g;
};
function paired() {
  const C = load(cand), B = load(base), bk = new Map(B.map(r => [`${r.set}|${r.run}|${r.key}`, r]));
  const pairs = [];
  for (const r of C) { const b = bk.get(`${r.set}|${r.run}|${r.key}`); if (!b) continue; pairs.push({ ...r, map: r.bmap, dG: r.G - b.G, dW: +r.won - +b.won, dA: +r.alive - +b.alive, cG: r.G, bG: b.G }); }
  console.log(`# pair_ab: ${cand} - ${base}, sets ${sets.join(',')}, ${pairs.length} pairs (cand rows ${C.length}, base rows ${B.length})`);
  console.log('| group | n | dG [95%] | d win %p [95%] | d alive %p [95%] | G cand / base |');
  console.log('|---|---:|---|---|---|---|');
  const out = [];
  for (const [name, fn] of groups(pairs)) {
    const P = pairs.filter(fn); if (!P.length) continue;
    const row = { group: name, n: P.length, dG: ci(P.map(p => p.dG)), dWin: ci(P.map(p => p.dW)), dAlive: ci(P.map(p => p.dA)), G: [mean(P.map(p => p.cG)), mean(P.map(p => p.bG))] };
    if (name === 'all') row.dGcluster = clusterBoot(P);
    out.push(row);
    console.log(`| ${name} | ${row.n} | ${fmt(row.dG)}${row.dGcluster ? ` (map-cluster [${f(row.dGcluster[0])}, ${f(row.dGcluster[1])}])` : ''} | ${pct(row.dWin)} | ${pct(row.dAlive)} | ${row.G[0].toFixed(1)} / ${row.G[1].toFixed(1)} |`);
  }
  return out;
}
function wilson(k, n) { const z = 1.959964, p = k / n, d = 1 + z * z / n, c = (p + z * z / (2 * n)) / d, h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return [p, Math.max(0, c - h), Math.min(1, c + h)]; }
function single() {
  const B = load(base);
  // G: t interval with the lower end floored at 0 (G >= 0); win and alive: Wilson intervals
  const st = P => { const g = ci(P.map(r => r.G)); return { n: P.length, G: [g[0], Math.max(0, g[1]), g[2]], win: wilson(P.filter(r => r.won).length, P.length), alive: wilson(P.filter(r => r.alive).length, P.length) }; };
  console.log(`# pair_ab: ${base} alone, sets ${sets.join(',')}, ${B.length} games`);
  console.log('| group | n | G [95%] | win % [95%] | alive % [95%] |');
  console.log('|---|---:|---|---|---|');
  const out = [], v1 = ([m, lo, hi], k = 1, d = 1) => `${(k * m).toFixed(d)} [${(k * lo).toFixed(d)}, ${(k * hi).toFixed(d)}]`;
  for (const [name, fn] of groups(B)) { const P = B.filter(fn); if (!P.length) continue; const s = st(P); out.push({ group: name, ...s });
    console.log(`| ${name} | ${s.n} | ${v1(s.G)} | ${v1(s.win, 100, 0)} | ${v1(s.alive, 100, 0)} |`); }
  // a -> b per two-layout map (b minus a, unpaired: different seed and layout; Welch-style normal interval)
  console.log('\n| map | n a / b | G a / b | G b - a [95%] | win % a / b | alive % a / b |');
  console.log('|---|---|---|---|---|---|');
  for (const m of [...TWO].sort()) {
    const A = B.filter(r => r.bmap === m && r.layout === 'a'), Bb = B.filter(r => r.bmap === m && r.layout === 'b'); if (!A.length || !Bb.length) continue;
    const va = ci(A.map(r => r.G)), vb = ci(Bb.map(r => r.G)), sa = (va[2] - va[0]) / tq(A.length - 1), sb = (vb[2] - vb[0]) / tq(Bb.length - 1), d = vb[0] - va[0], h = 1.96 * Math.sqrt(sa * sa + sb * sb);
    out.push({ group: `${m} b-a`, dG: [d, d - h, d + h] });
    console.log(`| ${m} | ${A.length} / ${Bb.length} | ${va[0].toFixed(1)} / ${vb[0].toFixed(1)} | ${fmt([d, d - h, d + h], 1)} | ${(100 * mean(A.map(r => +r.won))).toFixed(0)} / ${(100 * mean(Bb.map(r => +r.won))).toFixed(0)} | ${(100 * mean(A.map(r => +r.alive))).toFixed(0)} / ${(100 * mean(Bb.map(r => +r.alive))).toFixed(0)} |`);
  }
  return out;
}
(async () => {
  if (arg('bot')) { if (!cand) { console.error('--bot needs --cand'); process.exit(2); } await playMissing(path.resolve(arg('bot'))); }
  const out = cand ? paired() : single();
  if (arg('json')) fs.writeFileSync(path.resolve(arg('json')), JSON.stringify(out, null, 1) + '\n');
})();
