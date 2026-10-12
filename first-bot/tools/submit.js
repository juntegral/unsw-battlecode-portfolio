#!/usr/bin/env node
// Upload a bot as our active submission, or re-activate an earlier one. Nothing happens without --confirm.
// usage: node tools/submit.js upload <botdir> --name <label> --desc "<what changed>" [--confirm] [--force]
//        node tools/submit.js activate <submissionId> [--confirm] [--force]
//        node tools/submit.js active
// upload: smoke-tests the bot (2 local games), refuses while any of our battles is live or pending (a swap would change
// which bot plays them; --force skips this), runs the official `unswbc submit` with the key in the child's environment
// only, waits until the new submission is active, downloads the server zip and compares file hashes with <botdir>.
// Every upload/activation is logged to data/online/REMOTE-LOG.md and data/online/submissions.jsonl.
// The key is never printed or written: $UNSWBC_KEY, else the first bc_... token in ~/Downloads/api.txt.
const fs = require('fs'), path = require('path'), os = require('os'), cp = require('child_process'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..'), ONLINE = path.join(ROOT, 'data', 'online');
const BASE = 'https://game.battlecode.au/api/v1';
const argv = process.argv.slice(2), cmd = argv[0];
const flag = k => argv.includes('--' + k), opt = (k, d) => { const i = argv.indexOf('--' + k); return i > 0 ? argv[i + 1] : d; };
const CONFIRM = flag('confirm'), FORCE = flag('force');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const redact = s => String(s).replace(/bc_[A-Za-z0-9_-]+/g, 'bc_[REDACTED]');

function key() {
  const env = (process.env.UNSWBC_KEY || '').trim(); if (env) return env;
  const t = fs.readFileSync(process.env.UNSW_KEY_FILE || path.join(os.homedir(), 'Downloads', 'api.txt'), 'utf8');
  const k = (t.match(/bc_[A-Za-z0-9_-]+/) || [])[0]; if (!k) throw Error('API key not found'); return k;
}
async function api(method, p, body) {
  for (let i = 0; i < 3; i++) {
    const r = await fetch(BASE + p, { method, headers: { Authorization: 'Bearer ' + key(), ...(body ? { 'Content-Type': 'application/json' } : {}) }, body: body ? JSON.stringify(body) : undefined });
    if (r.status === 429) { await sleep(1000 * (+r.headers.get('retry-after') || 30)); continue; }
    const text = await r.text(); let json = null; try { json = JSON.parse(text); } catch {}
    if (!r.ok) throw Error(`${method} ${p} -> ${r.status} ${redact(text).slice(0, 200)}`);
    return json;
  }
  throw Error(`${method} ${p}: rate limited`);
}
const activeSub = async () => (await api('GET', '/submissions')).find(s => s.status === 'active') || null;
const logRemote = (what, target, purpose) => fs.appendFileSync(path.join(ONLINE, 'REMOTE-LOG.md'), `| ${new Date().toISOString().slice(0, 16)} | ${what} | ${target} | ${purpose} | 0 |\n`);
const logSub = rec => fs.appendFileSync(path.join(ONLINE, 'submissions.jsonl'), JSON.stringify({ at: new Date().toISOString(), ...rec }) + '\n');

// Our battles that are not finished: outcome live, or any pending game in results.
async function liveBattles() {
  const list = await api('GET', '/battles?limit=30');
  return (list || []).filter(b => !['win', 'loss', 'draw'].includes(b.outcome) || (b.results || []).includes('pending'));
}

function files(dir) {
  const out = {};
  const walk = (d, rel) => {
    for (const f of fs.readdirSync(d)) {
      if (['.unswbc-build', 'build', '.DS_Store', '__pycache__', '__MACOSX'].includes(f)) continue;
      const p = path.join(d, f), r = rel ? rel + '/' + f : f;
      if (fs.statSync(p).isDirectory()) walk(p, r); else out[r] = crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
    }
  };
  walk(dir, ''); return out;
}

function smoke(dir) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'smoke-')); const bad = [];
  for (const m of ['portals.map', 'slithery_fight.map']) {
    const r = cp.spawnSync(path.join(__dirname, 'unswbc'), ['run', path.join(ROOT, 'maps/online-20260927', m), dir, path.join(ROOT, 'bots/archetype_swarm'), '--sandbox', '--seed', '1', '--no-logs', '--no-draw', '-o', path.join(tmp, m + '.replay')], { cwd: tmp, encoding: 'utf8', timeout: 900000 });
    const o = (r.stdout || '') + (r.stderr || '');
    if (r.status !== 0 || !/wins|draw/i.test(o) || /no reply|timed out|Traceback|exceeded/i.test(o)) bad.push(`${m}: ${(o.split('\n').find(l => /no reply|timed out|Traceback|exceeded|error/i.test(l)) || 'exit ' + r.status).slice(0, 160)}`);
  }
  fs.rmSync(tmp, { recursive: true, force: true });
  return bad;
}

async function upload() {
  const dir = path.resolve(argv[1] || ''), name = opt('name'), desc = opt('desc', '');
  if (!argv[1] || !fs.existsSync(path.join(dir, 'bot.toml')) || !name) { console.error('usage: submit.js upload <botdir> --name <label> --desc "..." [--confirm]'); process.exit(2); }
  const before = await activeSub();
  console.log(`active now: ${before ? before.id + ' ' + before.name : 'none'}`);
  const bad = smoke(dir);
  if (bad.length) { console.error('smoke test failed:\n  ' + bad.join('\n  ')); process.exit(1); }
  console.log('smoke test: 2/2 games finished cleanly');
  const live = await liveBattles();
  if (live.length && !FORCE) { console.error(`refusing: ${live.length} of our battles are live or pending (${live.map(b => b.id).join(',')}); retry later or --force`); process.exit(3); }
  if (!CONFIRM) { console.log(`plan: upload ${dir} as "${name}" (${desc}). Add --confirm to do it.`); return; }
  const r = cp.spawnSync(path.join(__dirname, 'unswbc'), ['submit', dir, '-n', name, '-d', desc], { cwd: ROOT, encoding: 'utf8', timeout: 300000, env: { ...process.env, UNSWBC_KEY: key() } });
  console.log(redact(((r.stdout || '') + (r.stderr || '')).trim().split('\n').slice(-3).join('\n')));
  if (r.status !== 0) { logRemote('업로드 실패', name, desc); process.exit(1); }
  let a = null;
  for (let i = 0; i < 30; i++) { await sleep(10000); a = await activeSub(); if (a && a.name === name) break; }
  if (!a || a.name !== name) { logRemote('업로드(활성화 확인 실패)', name, desc); console.error(`uploaded but not active after 5 min (active: ${a && a.name})`); process.exit(1); }
  // Compare the server's copy with ours.
  const res = await fetch(`${BASE}/submissions/${a.id}/download`, { headers: { Authorization: 'Bearer ' + key() } });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'subzip-')), zip = path.join(tmp, 'bot.zip');
  fs.writeFileSync(zip, Buffer.from(await res.arrayBuffer())); cp.spawnSync('unzip', ['-oq', zip, '-d', path.join(tmp, 'x')]);
  const want = files(dir), got = fs.existsSync(path.join(tmp, 'x')) ? files(path.join(tmp, 'x')) : {};
  const match = Object.entries(want).every(([f, h]) => got[f] === h);
  fs.rmSync(tmp, { recursive: true, force: true });
  logRemote('업로드', `${name} → 제출 ${a.id}`, desc); logSub({ action: 'upload', id: a.id, name, dir: path.relative(ROOT, dir), desc, serverZipMatch: match, previous: before && before.id });
  console.log(`active: ${a.id} ${a.name}; server zip ${match ? 'matches' : 'DOES NOT match'} ${path.relative(ROOT, dir)}`);
  if (!match) process.exitCode = 1;
}

async function activate() {
  const id = +argv[1]; if (!id) { console.error('usage: submit.js activate <submissionId> [--confirm]'); process.exit(2); }
  const subs = await api('GET', '/submissions'), s = subs.find(x => x.id === id), before = subs.find(x => x.status === 'active');
  if (!s) { console.error(`no submission ${id}`); process.exit(2); }
  console.log(`active now: ${before ? before.id + ' ' + before.name : 'none'}; target: ${s.id} ${s.name}`);
  if (before && before.id === id) { console.log('already active'); return; }
  const live = await liveBattles();
  if (live.length && !FORCE) { console.error(`refusing: ${live.length} of our battles are live or pending (${live.map(b => b.id).join(',')}); retry later or --force`); process.exit(3); }
  if (!CONFIRM) { console.log('plan only. Add --confirm to activate.'); return; }
  await api('POST', `/submissions/${id}/activate`);
  let a = null; for (let i = 0; i < 12; i++) { await sleep(5000); a = await activeSub(); if (a && a.id === id) break; }
  if (!a || a.id !== id) { console.error(`activation not visible after 60 s (active: ${a && a.id})`); process.exit(1); }
  logRemote('활성화', `제출 ${id} (${s.name})`, opt('purpose', '기준 봇 복귀 또는 시험 봇 전환')); logSub({ action: 'activate', id, name: s.name, previous: before && before.id });
  console.log(`active: ${a.id} ${a.name}`);
}

(async () => {
  if (cmd === 'upload') await upload();
  else if (cmd === 'activate') await activate();
  else if (cmd === 'active') { const a = await activeSub(); console.log(a ? `${a.id} ${a.name} (${a.uploadedAt})` : 'none'); }
  else { console.error('usage: submit.js upload|activate|active ...'); process.exit(2); }
})().catch(e => { console.error(redact(e.message || e)); process.exit(1); });
