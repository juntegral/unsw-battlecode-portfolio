#!/usr/bin/env node
'use strict';
// fp_all.js — behaviour fingerprint (tools/fingerprint.js hashReplay: every event except indicators, logs, drawings and
// instruction counts) of two bots on all 15 map files (maps/online-20260927 + maps/variants), one opponent, one seed;
// plus the map tags (" map=...") of the candidate's replays against each file's true map and layout.
// usage (repository root):
//   node exp/mapid/fp_all.js --a exp/cand-stack2/bot --b exp/cand-mapid/bot --label <name> [--opp bots/proxy4_king] [--seed 1]
//        [--jobs 3] [--maps devil_b,schooltime_b]   (default: all 15 files)
// Replays: exp/mapid/fp/<label>/<a|b>_<mapfile>/game.replay (reused if present; the baseline side is keyed by its folder).
const fs = require('fs'), path = require('path'), cp = require('child_process'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..', '..');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const A = opt('a', 'exp/cand-stack2/bot'), B = opt('b', 'exp/cand-mapid/bot'), label = opt('label', 'fp'), opp = opt('opp', 'bots/proxy4_king');
const seed = +opt('seed', 1), jobs = Math.min(3, +opt('jobs', 3));
const FILES = [...fs.readdirSync(path.join(ROOT, 'maps', 'online-20260927')).filter(f => f.endsWith('.map')).sort().map(f => 'maps/online-20260927/' + f),
  ...fs.readdirSync(path.join(ROOT, 'maps', 'variants')).filter(f => f.endsWith('.map')).sort().map(f => 'maps/variants/' + f)]
  .filter(f => !opt('maps') || opt('maps').split(',').includes(path.basename(f, '.map')));
const OUT = path.join(__dirname, 'fp', label);
const slug = s => s.replace(/[^A-Za-z0-9]+/g, '-').replace(/^-|-$/g, '');
const judges = () => { try { return +cp.execSync("ps -axo command | grep -c '[u]nswbc-clean.py run' || true").toString().trim(); } catch { return 0; } };
const freeGiB = () => { const d = fs.statfsSync(ROOT); return d.bavail * d.bsize / 1024 ** 3; };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
let load = null;
const SKIP = new Set(['dragonIndicator', 'dragonLog', 'debugDraw', 'engineLog']);
function scan(file) {
  if (!load) load = makeLoader(viewerSource());
  const R = load(file), h = crypto.createHash('sha256');
  let n = 0, r = -1; const tags = [], born = new Map(); let firstDiffRound = null;
  for (const e of R.events) {
    if (e.type === 'roundStart') r = e.round;
    if (e.type === 'dragonSplit') born.set(e.childId, r);
    if (e.type === 'dragonIndicator') { const m = /(?:^|\s)map=(\S+)/.exec(e.text || ''); if (m) tags.push({ r, id: e.id, tag: m[1], born: born.has(e.id) ? born.get(e.id) : 0 }); }
    if (SKIP.has(e.type)) continue;
    const o = {}; for (const [k, v] of Object.entries(e)) { if (k === 'instructions') continue; o[k] = typeof v === 'bigint' ? String(v) : v; }
    h.update(JSON.stringify(o)); n++;
  }
  return { hash: h.digest('hex').slice(0, 16), events: n, rounds: r + 1, tags };
}
function truth(file) {
  const k = path.basename(file, '.map');
  const fam = { autarky: 'Autarky', default: 'Default', devil: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners_Dilemma', queen_of_spades: 'Queen_Of_Spades',
    schooltime: 'Schooltime', slithery_fight: 'Slithery_Fight', trauma: 'Trauma', trophy: 'Trophy' }[k.replace(/_(b|10)$/, '')];
  return fam + '/' + (/_(b|10)$/.test(k) ? 'b' : 'a');
}
function play(bot, map, dir) {
  const out = path.join(dir, 'game.replay');
  if (fs.existsSync(out)) return Promise.resolve(out);
  fs.mkdirSync(dir, { recursive: true });
  return new Promise((res, rej) => {
    const p = cp.spawn(path.join(ROOT, 'tools', 'unswbc'), ['run', path.join(ROOT, map), path.resolve(ROOT, bot), path.resolve(ROOT, opp), '--sandbox', '--seed', String(seed), '--no-logs', '--no-draw', '-o', out], { cwd: dir, stdio: ['ignore', 'pipe', 'pipe'] });
    let log = ''; p.stdout.on('data', d => log += d); p.stderr.on('data', d => log += d);
    p.on('close', code => { fs.writeFileSync(path.join(dir, 'run.log'), log); fs.existsSync(out) ? res(out) : rej(new Error(`no replay (${code}) ${dir}`)); });
  });
}
(async () => {
  const q = [];
  for (const m of FILES) {
    const k = path.basename(m, '.map');
    q.push({ m, side: 'a', bot: A, dir: path.join(OUT, `${slug(A)}_${k}_s${seed}`) }, { m, side: 'b', bot: B, dir: path.join(OUT, `${slug(B)}_${k}_s${seed}`) });
  }
  const res = new Map(); let i = 0;
  await Promise.all(Array.from({ length: jobs }, async () => {
    while (i < q.length) {
      const t = q[i++];
      if (!fs.existsSync(path.join(t.dir, 'game.replay'))) {
        while (judges() >= 6 || freeGiB() < 20) { if (freeGiB() < 20) { console.error('disk free < 20 GiB: stop'); process.exit(3); } await sleep(5000); }
      }
      try { res.set(t.m + t.side, scan(await play(t.bot, t.m, t.dir))); } catch (e) { console.error(String(e)); }
    }
  }));
  let same = 0, n = 0; const rows = [];
  console.log(`| map file | ${A} | ${B} | same | rounds | tags (processes) | right | family only | wrong / none |`);
  console.log('|---|---|---|---|---:|---:|---:|---:|---:|');
  const tot = { procs: 0, right: 0, fam: 0, wrong: 0, init0: 0, init0Right: 0 };
  for (const m of FILES) {
    const a = res.get(m + 'a'), b = res.get(m + 'b'); if (!a || !b) { console.log(`| ${path.basename(m)} | missing |`); continue; }
    n++; const eq = a.hash === b.hash; if (eq) same++;
    // per process: its last tag (the tag is written on the first turn and on every change)
    const last = new Map(), first = new Map();
    for (const t of b.tags) { last.set(t.id, t); if (!first.has(t.id)) first.set(t.id, t); }
    const want = truth(m); let right = 0, fam = 0, wrong = 0;
    for (const t of last.values()) { if (t.tag === want) right++; else if (t.tag === want.replace(/\/[ab]$/, '/?')) fam++; else wrong++; }
    for (const t of first.values()) if (t.born === 0 && t.r === 0) { tot.init0++; if (t.tag === want) tot.init0Right++; }
    tot.procs += last.size; tot.right += right; tot.fam += fam; tot.wrong += wrong;
    rows.push({ file: m, same: eq, hashA: a.hash, hashB: b.hash, rounds: b.rounds, procs: last.size, right, fam, wrong, want, wrongTags: [...last.values()].filter(t => t.tag !== want && t.tag !== want.replace(/\/[ab]$/, '/?')) });
    console.log(`| ${path.basename(m)} | ${a.hash} | ${b.hash} | ${eq ? 'yes' : '**no**'} | ${b.rounds} | ${last.size} | ${right} | ${fam} | ${wrong} |`);
  }
  console.log(`\n${same}/${n} identical. processes ${tot.procs}: right ${tot.right}, family only ${tot.fam}, wrong/none ${tot.wrong}; initial dragons right at round 0: ${tot.init0Right}/${tot.init0}`);
  for (const r of rows) for (const w of r.wrongTags) console.log(`  wrong: ${path.basename(r.file)} #${w.id} r${w.r} born r${w.born} ${w.tag} (want ${r.want})`);
  fs.writeFileSync(path.join(OUT, 'summary.json'), JSON.stringify({ A, B, opp, seed, same, n, tot, rows }, null, 1));
  process.exit(same === n ? 0 : 1);
})();
