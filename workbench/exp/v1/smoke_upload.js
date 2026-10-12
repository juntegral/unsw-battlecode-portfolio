// The local part of tools/submit.js upload (its smoke(): 2 sandbox games vs archetype_swarm, seed 1, portals and slithery_fight; pass = exit 0,
// "wins|draw" in the output, no "no reply|timed out|Traceback|exceeded"), without any network step, and the file list the upload hashes.
const fs = require('fs'), path = require('path'), os = require('os'), cp = require('child_process'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..', '..'), dir = path.resolve(process.argv[2] || 'versions/v1/bot');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'smoke-')); const bad = [];
for (const m of ['portals.map', 'slithery_fight.map']) {
  const r = cp.spawnSync(path.join(ROOT, 'tools', 'unswbc'), ['run', path.join(ROOT, 'maps/online-20260927', m), dir, path.join(ROOT, 'bots/archetype_swarm'), '--sandbox', '--seed', '1', '--no-logs', '--no-draw', '-o', path.join(tmp, m + '.replay')], { cwd: tmp, encoding: 'utf8', timeout: 900000 });
  const o = (r.stdout || '') + (r.stderr || '');
  const ok = !(r.status !== 0 || !/wins|draw/i.test(o) || /no reply|timed out|Traceback|exceeded/i.test(o));
  console.log(`${m}: ${ok ? 'ok' : 'FAIL'} (${(o.split('\n').find(l => /wins|draw/i.test(l)) || 'exit ' + r.status).trim().slice(0, 120)})`);
  if (!ok) bad.push(m);
}
fs.rmSync(tmp, { recursive: true, force: true });
const files = [];
const walk = (d, rel) => { for (const f of fs.readdirSync(d)) { if (['.unswbc-build', 'build', '.DS_Store', '__pycache__', '__MACOSX'].includes(f)) continue; const p = path.join(d, f), r = rel ? rel + '/' + f : f; if (fs.statSync(p).isDirectory()) walk(p, r); else files.push(r + ' ' + crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex').slice(0, 12)); } };
walk(dir, '');
console.log(`smoke test: ${2 - bad.length}/2 games finished cleanly`);
console.log('files the upload hashes: ' + files.join(', '));
process.exit(bad.length ? 1 : 0);
