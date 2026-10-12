// Shared local runtime. No server access and no bot-specific policy.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const { spawn, execFileSync } = require('child_process');
const ROOT = path.resolve(__dirname, '..');
const DATA = process.env.UNSW_ARENA_DATA || '~/01. Project/개인 프로젝트/unsw-arena-data';
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const alive = pid => { if (!Number.isInteger(Number(pid)) || Number(pid) <= 0) return false; try { process.kill(Number(pid), 0); return true; } catch (e) { return e.code === 'EPERM'; } };
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
function write(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = file + '.' + process.pid + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(value, null, 2) + '\n');
  fs.renameSync(tmp, file);
}
function lineage(name) {
  if (!/^[a-z][a-z0-9_-]*$/.test(name || '')) throw Error('invalid lineage');
  return path.join(ROOT, 'lineages', name);
}
function wave(name) {
  const state = read(path.join(lineage(name), 'waves', 'active.json'));
  if (!process.env.UNSW_WAVE_ID || state.id !== process.env.UNSW_WAVE_ID) {
    throw Error('run this command from the managed wave; UNSW_WAVE_ID must match active.json');
  }
  return state;
}
const excluded = name => ['.git', '.unswbc-build', 'build', 'replays', '__pycache__', '.DS_Store'].includes(name) || name.endsWith('.wasm');
function files(dir, prefix = '') {
  const out = [];
  for (const name of fs.readdirSync(path.join(dir, prefix)).sort()) {
    if (excluded(name)) continue;
    const rel = path.join(prefix, name), stat = fs.lstatSync(path.join(dir, rel));
    if (stat.isSymbolicLink()) throw Error('snapshot contains a symlink: ' + rel);
    if (stat.isDirectory()) out.push(...files(dir, rel));
    else if (stat.isFile()) out.push(rel);
  }
  return out;
}
function hashes(dir) {
  return Object.fromEntries(files(dir).map(f => [f, crypto.createHash('sha256').update(fs.readFileSync(path.join(dir, f))).digest('hex')]));
}
const digest = dir => crypto.createHash('sha256').update(JSON.stringify(hashes(dir))).digest('hex');
function snapshot(from, to) {
  if (fs.existsSync(to)) throw Error('snapshot already exists: ' + to);
  fs.mkdirSync(to, { recursive: true });
  for (const file of files(from)) {
    fs.mkdirSync(path.dirname(path.join(to, file)), { recursive: true });
    fs.copyFileSync(path.join(from, file), path.join(to, file));
  }
  return digest(to);
}
function inside(parent, target) {
  const rel = path.relative(fs.realpathSync(parent), fs.realpathSync(target));
  return rel === '' || (!rel.startsWith('..' + path.sep) && rel !== '..' && !path.isAbsolute(rel));
}
function ready(dir) {
  const file = path.join(dir, 'NOTES.md');
  if (!fs.existsSync(file)) return 0;
  return Math.max(0, ...[...fs.readFileSync(file, 'utf8').matchAll(/^\s*[-*]?\s*ready:\s*r(\d+)/gmi)].map(m => +m[1]));
}
async function lock(name, { wait = true, stopped = () => false } = {}) {
  const dir = path.join(DATA, 'control', 'locks', name), ownerFile = path.join(dir, 'owner.json');
  fs.mkdirSync(path.dirname(dir), { recursive: true });
  const token = crypto.randomUUID();
  while (true) {
    if (stopped()) throw Error('stopped while waiting for ' + name);
    try {
      fs.mkdirSync(dir);
      write(ownerFile, { pid: process.pid, token, at: new Date().toISOString(), root: ROOT });
      return {
        child(pid) { const o = read(ownerFile); if (o.token === token) write(ownerFile, { ...o, childPid: pid }); },
        release() { try { if (read(ownerFile).token === token) { fs.unlinkSync(ownerFile); fs.rmdirSync(dir); } } catch (e) { if (e.code !== 'ENOENT') throw e; } }
      };
    } catch (e) {
      if (e.code !== 'EEXIST') throw e;
      try {
        const owner = read(ownerFile);
        if (!alive(owner.pid) && !(owner.childPid && alive(owner.childPid))) {
          // Serialize stale cleanup so two waiters cannot delete a newly acquired lock.
          const reaping = dir + '.reaping';
          let acquired = false;
          try {
            fs.mkdirSync(reaping); acquired = true;
            const latest = read(ownerFile);
            if (latest.token === owner.token && !alive(latest.pid) && !(latest.childPid && alive(latest.childPid))) {
              fs.unlinkSync(ownerFile); fs.rmdirSync(dir);
            }
          } catch (cleanup) { if (!['EEXIST', 'ENOENT'].includes(cleanup.code)) throw cleanup; }
          finally { if (acquired) fs.rmdirSync(reaping); }
          if (!fs.existsSync(dir)) continue;
        }
      } catch (err) {
        if (!['ENOENT', 'ENOTEMPTY'].includes(err.code)) throw err;
        // A process can die between mkdir and owner.json. Only reclaim an old, empty directory.
        try { if (Date.now() - fs.statSync(dir).mtimeMs > 10000 && !fs.readdirSync(dir).length) fs.rmdirSync(dir); }
        catch (gone) { if (!['ENOENT', 'ENOTEMPTY'].includes(gone.code)) throw gone; }
      }
      if (!wait) throw Error('another runner owns ' + name);
      await sleep(1000);
    }
  }
}
function command(cmd, args, opts = {}) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { cwd: ROOT, stdio: 'inherit', ...opts });
    opts.onSpawn?.(p);
    p.once('error', reject);
    p.once('exit', (code, signal) => resolve({ code: code ?? 128, signal }));
  });
}
const jobDir = () => path.join(DATA, 'control', 'jobs');
function jobs(name) {
  if (!fs.existsSync(jobDir())) return [];
  return fs.readdirSync(jobDir()).filter(f => f.endsWith('.json')).map(f => read(path.join(jobDir(), f)))
    .filter(j => j.root === ROOT && j.lineage === name && ['queued', 'running'].includes(j.status));
}
async function drain(name) {
  while (true) {
    const pending = jobs(name);
    if (!pending.length) return;
    for (const j of pending) {
      if (!alive(j.pid) && !(j.childPid && alive(j.childPid))) write(j.file, { ...j, status: 'interrupted' });
    }
    if (jobs(name).length) { console.log('waiting for registered local evaluation jobs'); await sleep(5000); }
  }
}
async function job(name, work) {
  const state = wave(name), id = crypto.randomUUID(), file = path.join(jobDir(), id + '.json');
  const entry = { id, file, pid: process.pid, root: ROOT, lineage: name, wave: state.id, status: 'queued' };
  write(file, entry);
  let held;
  try {
    // One evaluation batch across all managed lineages; each batch has at most two games.
    held = await lock('local-evaluation');
    const disk = fs.statfsSync(ROOT);
    if (disk.bavail * disk.bsize < 20 * 1024 ** 3) throw Error('disk free < 20 GiB; evaluation not started');
    write(file, { ...entry, status: 'running' });
    const result = await work(p => {
      held.child(p.pid);
      write(file, { ...entry, childPid: p.pid, status: 'running' });
    });
    if (result?.code) throw Error('evaluation command exited ' + result.code);
    write(file, { ...entry, status: 'finished', at: new Date().toISOString() });
    return result;
  } catch (e) {
    write(file, { ...entry, status: 'failed', error: String(e) }); throw e;
  } finally { held?.release(); }
}
function git(args) { return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8' }).trim(); }
function commit(name, message) {
  git(['add', '-A', '--', 'lineages/' + name]);
  if (git(['diff', '--cached', '--name-only', '--', 'lineages/' + name])) git(['commit', '-m', message, '--', 'lineages/' + name]);
}
module.exports = { fs, path, crypto, ROOT, DATA, sleep, alive, read, write, lineage, wave, hashes, digest, snapshot, inside, ready, lock, command, jobs, drain, job, git, commit };
