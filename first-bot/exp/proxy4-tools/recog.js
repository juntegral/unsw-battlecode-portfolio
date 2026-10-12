#!/usr/bin/env node
'use strict';
// recog.js — checks the proxy4 map recognition (bots/proxy4_*, pxcore.cpp checkSdb) in local games. Each proxy4 dragon
// process writes one LOG line when it knows the map ("px4 map <name> r<round>"), when it is down to versions of one map
// ("px4 fam <name> n<k> r<round>", then later "px4 map ...") or when no table map fits ("px4 map none r<round>").
//
// usage (repository root):
//   node exp/proxy4-tools/recog.js run --label <L> --pairs a:b[,c:d] [--maps <file>,<file>|<dir>,...] [--seeds 1] [--jobs 2]
//       Plays every pair x map file x seed with tools/unswbc --sandbox, LOG lines kept (--no-draw --no-indicator), into
//       exp/<L>/games/<a>__<b>__<mapfile>__<seed>/game.replay. A bot is `bot`, a name under bots/, or a directory. At most
//       --jobs games at once (max 2); a game starts only while the machine runs fewer than 6 judge processes
//       (`ps -axo command | grep -c '[u]nswbc-clean.py run'`) and 20 GiB of disk are free.
//   node exp/proxy4-tools/recog.js report --label <L>[,<L2>] [--json <file>]
//       Per map file: dragon processes of proxy teams that logged, right / wrong / none, recognition delay after birth
//       (initial dragons are born at round 0, split children at their split round), processes that went through the
//       family state and how long it lasted. The right map of a file: <name>.map -> Name, *_b.map -> "Name b",
//       prisoners_dilemma_10 -> "Prisoners Dilemma 10".
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const argv = process.argv.slice(2), cmd = argv[0];
const opt = {}; for (let i = 1; i < argv.length; i++) if (argv[i].startsWith('--')) { const k = argv[i].slice(2); opt[k] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true; }
const dirOf = n => n === 'bot' ? path.join(ROOT, 'bot') : n.includes('/') ? path.resolve(ROOT, n) : path.join(ROOT, 'bots', n);
const nameOf = n => n.includes('/') ? path.basename(n) : n;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const judges = () => { try { return +cp.execSync("ps -axo command | grep -c '[u]nswbc-clean.py run' || true").toString().trim(); } catch { return 0; } };
const freeGiB = () => { const d = fs.statfsSync(ROOT); return d.bavail * d.bsize / 1024 ** 3; };
// the spawn-table name a map file should be recognised as (exp/proxy4-tools/genspawndb.js)
function expected(mapFile) {
  const key = path.basename(mapFile, '.map');
  if (key === 'prisoners_dilemma_10') return 'Prisoners_Dilemma_10';
  const txt = fs.readFileSync(mapFile, 'utf8'); const m = txt.match(/^MAP_NAME (.*)$/m);
  const base = (m ? m[1].trim() : key).replace(/ /g, '_');
  return /_b$/.test(key) ? base + '_b' : base;
}

async function run() {
  const label = opt.label; if (!label || !opt.pairs) { console.error('need --label and --pairs'); process.exit(2); }
  const out = path.join(ROOT, 'exp', label); fs.mkdirSync(path.join(out, 'games'), { recursive: true });
  const mapFiles = [];
  for (const m of String(opt.maps || 'maps/online-20260927,maps/variants').split(',')) {
    const p = path.resolve(ROOT, m);
    if (fs.statSync(p).isDirectory()) for (const f of fs.readdirSync(p).filter(x => x.endsWith('.map')).sort()) mapFiles.push(path.join(p, f));
    else mapFiles.push(p);
  }
  const seeds = String(opt.seeds || '1').split(',').map(Number), jobs = Math.min(2, +(opt.jobs || 2));
  const manifest = path.join(out, 'games.jsonl');
  const done = new Set(fs.existsSync(manifest) ? fs.readFileSync(manifest, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l).key) : []);
  const tasks = [];
  for (const pr of String(opt.pairs).split(',')) { const [a, b] = pr.split(':'); for (const mf of mapFiles) for (const sd of seeds) {
    const key = [nameOf(a), nameOf(b), path.basename(mf, '.map'), sd].join('__'); if (!done.has(key)) tasks.push({ key, a, b, mf, sd });
  } }
  console.log(`${label}: ${tasks.length} games`);
  let i = 0;
  const worker = async w => {
    await sleep(w * 1500);
    while (i < tasks.length) {
      for (;;) { if (freeGiB() < 20) { console.log('disk free < 20 GiB: stop'); return; } if (judges() < 6) break; await sleep(4000); }
      const t = tasks[i++]; const dir = path.join(out, 'games', t.key); fs.mkdirSync(dir, { recursive: true });
      const t0 = Date.now();
      const code = await new Promise(res => {
        const p = cp.spawn(path.join(ROOT, 'tools', 'unswbc'), ['run', t.mf, dirOf(t.a), dirOf(t.b), '--sandbox', '--seed', String(t.sd), '--no-draw', '--no-indicator', '-o', path.join(dir, 'game.replay')], { cwd: dir });
        let log = ''; p.stdout.on('data', d => log += d); p.stderr.on('data', d => log += d);
        p.on('close', c => { fs.writeFileSync(path.join(dir, 'run.log'), log); res(c); });
      });
      fs.appendFileSync(manifest, JSON.stringify({ key: t.key, a: nameOf(t.a), b: nameOf(t.b), map: path.relative(ROOT, t.mf), seed: t.sd, exit: code, secs: Math.round((Date.now() - t0) / 1000) }) + '\n');
      console.log(`  ${t.key} exit ${code} ${Math.round((Date.now() - t0) / 1000)}s`);
    }
  };
  await Promise.all(Array.from({ length: jobs }, (_, w) => worker(w)));
}

function report() {
  const { load } = require(path.join(ROOT, 'tools', 'replay.js'));
  const byMap = new Map();
  for (const label of String(opt.label).split(',')) {
    const manifest = path.join(ROOT, 'exp', label, 'games.jsonl');
    for (const g of fs.readFileSync(manifest, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l))) {
      const file = path.join(ROOT, 'exp', label, 'games', g.key, 'game.replay'); if (!fs.existsSync(file)) continue;
      const R = load(file), want = expected(path.join(ROOT, g.map));
      const teamName = { A: g.a, B: g.b };
      // birth round and team of every dragon; first "map" and first "fam" log of every dragon id
      const born = new Map(), team = new Map(), died = new Map(), first = new Map(), fam = new Map();
      let round = -1, rounds = 0;
      for (const e of R.events) {
        if (e.type === 'roundStart') { round = e.round; rounds = round + 1; continue; }
        if (e.type === 'dragonSplit') { born.set(e.childId, round); team.set(e.childId, e.team); team.set(e.parentId, e.team); }
        else if (e.type === 'dragonDeath') { if (!died.has(e.id)) died.set(e.id, round); }
        else if (e.type === 'dragonLog' && /^px4 /.test(e.text)) {
          const m = e.text.match(/^px4 (map|fam) (\S+)(?: n(\d+))? r(\d+)/); if (!m) continue;
          if (m[1] === 'map' && !first.has(e.id)) first.set(e.id, { name: m[2], r: +m[4] });
          if (m[1] === 'fam' && !fam.has(e.id)) fam.set(e.id, { name: m[2], r: +m[4] });
        } else if (e.type === 'dragonUpdate' && e.team && !team.has(e.id)) team.set(e.id, e.team);
      }
      const init = R.initialDragons || (R.map && R.map.dragons) || null;
      const key = path.basename(g.map, '.map');
      if (!byMap.has(key)) byMap.set(key, { want, games: 0, procs: 0, right: 0, wrong: [], none: 0, unknown: 0, delays: [], famN: 0, famDur: [], famOpen: 0, r0: 0, r0right: 0 });
      const S = byMap.get(key); S.games++;
      const ids = new Set([...first.keys(), ...fam.keys()]);
      for (const id of ids) {
        S.procs++;
        const b = born.has(id) ? born.get(id) : 0, f = first.get(id), fm = fam.get(id);
        if (b === 0 && !born.has(id)) { S.r0++; if (f && f.r === 0 && f.name === want) S.r0right++; }
        if (fm) { S.famN++; if (f) S.famDur.push(f.r - fm.r); else S.famOpen++; if (fm.name !== want.replace(/_b$|_10$/, '')) S.wrong.push(`${id}:fam ${fm.name}`); }
        if (!f) { S.unknown++; continue; }
        if (f.name === 'none') S.none++;
        else if (f.name === want) { S.right++; S.delays.push(f.r - b); }
        else S.wrong.push(`${id}:${f.name}@r${f.r}`);
      }
    }
  }
  const q = (a, p) => { if (!a.length) return '-'; const s = a.slice().sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
  const rows = [];
  console.log('| 지도 파일 | 기대 | 판 | 프로세스 | 맞음 | 틀림 | none | 모름(끝까지 가족) | r0 첫 드래곤: r0에 맞음 | 인식 지연 p50/p90/max | 가족 상태 거침 (기간 p50/max) |');
  console.log('|---|---|---:|---:|---:|---:|---:|---:|---|---|---|');
  for (const [key, S] of [...byMap].sort()) {
    rows.push({ map: key, ...S });
    console.log(`| ${key} | ${S.want} | ${S.games} | ${S.procs} | ${S.right} | ${S.wrong.length} | ${S.none} | ${S.unknown} | ${S.r0right}/${S.r0} | ${q(S.delays, 0.5)}/${q(S.delays, 0.9)}/${S.delays.length ? Math.max(...S.delays) : '-'} | ${S.famN} (${q(S.famDur, 0.5)}/${S.famDur.length ? Math.max(...S.famDur) : '-'}; 끝까지 ${S.famOpen}) |`);
    if (S.wrong.length) console.log('   wrong:', S.wrong.slice(0, 10).join(' '));
  }
  if (opt.json) fs.writeFileSync(path.resolve(ROOT, opt.json), JSON.stringify(rows, null, 1) + '\n');
}

if (cmd === 'run') run(); else if (cmd === 'report') report(); else { console.error('usage: recog.js run|report ...'); process.exit(2); }
