#!/usr/bin/env node
// One online wave (the hourly online set) and its feedback, the mechanism application check.
//   1. wait for the hourly allowance (60 general games),
//   2. upload the bot and wait until it is active (tools/submit.js: smoke test, live-battle guard, server zip check),
//   3. request the 6 top teams x 10 maps + DEV team 545 x 10 maps against it,
//   4. wait for the games and download them to data/online/<set>,
//   5. write research/experiments/mech-<name>.md with tools/mech_check.js (--vs the previous wave, if given),
//   6. write research/experiments/triage-<name>.md with tools/wave_triage.js (replays to read first).
// The uploaded bot stays active (user rule 2026-09-30: only upload, never revert). Win rate is not reported
// (user rule 2026-09-30 10:10 KST: the feedback is whether each implemented mechanism applies against the elite).
//
// usage (repository root):
//   node tools/online_wave.js <botDir | active:<submissionId>> <name> "<description>" <set> [--vs <pool>] [--wait-min 180]
//     active:<id> skips the upload and plays the submission that is already active (a replicate wave).
'use strict';
const cp = require('child_process'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const argv = process.argv.slice(2);
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const pos = argv.filter((a, i) => !a.startsWith('--') && !['--vs', '--wait-min'].includes(argv[i - 1]));
const [bot, name, desc, set] = pos;
if (!bot || !name || !desc || !set) { console.error('usage: online_wave.js <botDir|active:<id>> <name> "<desc>" <set> [--vs <pool>]'); process.exit(2); }
const vs = opt('--vs', null), waitMin = +opt('--wait-min', 180);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const red = s => String(s).replace(/bc_[A-Za-z0-9_-]+/g, 'bc_[REDACTED]');
const node = (args, ok = false) => {
  try { return cp.execFileSync('node', args, { cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'], maxBuffer: 64 << 20 }).toString(); }
  catch (e) { if (ok) return (e.stdout || '').toString() + (e.stderr || '').toString(); throw e; }
};
const now = () => new Date().toISOString().slice(11, 19);

(async () => {
  // 1. allowance (a failed query prints -1 and is retried; the server sometimes answers 520)
  let left = -1;
  for (let i = 0; i < 70; i++) {
    let t = null; try { t = JSON.parse(node(['tools/online.js', 'tickets', '--json'])); } catch (e) { /* retry */ }
    left = t && t.normal ? t.normal.remaining : -1;
    console.log(now(), 'general tickets left', left);
    if (left >= 60) break;
    await sleep(60000);
  }
  if (left < 60) { console.log(now(), 'not enough tickets after waiting; stopping'); process.exit(1); }
  // 2. upload (or use the active submission)
  let active;
  if (bot.startsWith('active:')) active = bot.slice(7);
  else {
    // Our own unranked sets must not see a bot swap mid-set; hourly autoscrims (ranked) may, since their results are
    // not used. After 3 refusals the upload is forced if every live battle is ranked.
    const onlyAutoscrimsLive = () => {
      try {
        const a = JSON.parse(node(['tools/online.js', 'battles', '--limit', '30', '--json']));
        const live = a.filter(b => !['win', 'loss', 'draw'].includes(b.outcome) || (b.results || []).includes('pending'));
        return live.length > 0 && live.every(b => b.ranked);
      } catch (e) { return false; }
    };
    let up = '';
    for (let i = 0; i < 20; i++) {
      const force = i >= 3 && onlyAutoscrimsLive() ? ['--force'] : [];
      if (force.length) console.log(now(), 'only autoscrims are live: forcing the upload');
      up = red(node(['tools/submit.js', 'upload', bot, '--name', name, '--desc', desc, '--confirm', ...force], true));
      console.log(up.trim().split('\n').slice(-3).join('\n'));
      if (/active: \d+/.test(up) || /smoke test failed/.test(up)) break;
      await sleep(60000);
    }
    const m = up.match(/active: (\d+) /);
    if (!m) { console.log('upload failed; stopping'); process.exit(1); }
    active = m[1];
  }
  console.log(now(), 'wave bot is submission', active);
  // 3. request
  const ids = [];
  for (const teams of ['306,70,20,801,264,46', '545']) {
    const out = node(['tools/online.js', 'request', teams, '--maps', 'all', '--purpose', `${name} 웨이브`, '--expect-active', active, '--confirm'], true);
    for (const mm of out.matchAll(/ids ([0-9,]+)/g)) ids.push(+mm[1].split(',')[0]);
    console.log(out.split('\n').filter(l => /신청됨|거절|실패|error|refus/i.test(l)).join('\n'));
  }
  console.log(now(), 'series', ids.join(','));
  if (!ids.length) { console.log('no battles accepted; stopping'); process.exit(1); }
  // 4. wait and download
  for (let i = 0; i < waitMin; i++) {
    let tot = 0, comp = 0;
    for (const s of ids) {
      try { const j = JSON.parse(node(['tools/online.js', 'battle', String(s), '--json'])); const g = j.games || []; tot += g.length; comp += g.filter(q => (q.status === 'completed' || q.status === 'draw') && q.hasReplay).length; }   // a draw is finished too
      catch (e) { /* retry */ }
    }
    console.log(now(), 'completed', comp, '/', tot);
    if (tot >= ids.length * 10 && comp >= tot) break;
    await sleep(60000);
  }
  // download; a server error page (520) can cut it short, so retry until every replay is here (2026-10-01: bench-s11-1 got 23/70)
  const fsx = require('fs');
  const have = () => { try { return fsx.readdirSync(path.join(ROOT, 'data', 'online', set)).filter(f => /^M\d+\.replay$/.test(f)).length; } catch (e) { return 0; } };
  for (let t = 0; t < 4; t++) {
    console.log(red(node(['tools/online.js', 'download', ids.join(','), '--out', set, '--no-events', '--purpose', `${name} 웨이브 받기`], true)).split('\n').slice(-2).join('\n'));
    console.log(now(), 'replays', have(), '/', ids.length * 10);
    if (have() >= ids.length * 10) break;
    await sleep(60000);
  }
  // 5. mechanism application check
  const out = `research/experiments/mech-${name}.md`;
  console.log(node(['tools/mech_check.js', set, ...(vs ? ['--vs', vs] : []), '--out', out, '--title', `구현 적용 확인: ${name} (제출 ${active})`], true).trim());
  // 6. replay triage: the biggest losses and the upset wins, the replays to read first
  console.log(node(['tools/wave_triage.js', set, '--out', `research/experiments/triage-${name}.md`], true).trim());
  console.log(now(), 'wave done:', out);
})().catch(e => { console.error(red(e.message || e)); process.exit(1); });
