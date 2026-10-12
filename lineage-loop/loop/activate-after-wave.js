#!/usr/bin/env node
// Operator-only deployment. Leave a running legacy wave untouched, then apply one frozen common revision.
const rt = require('./runtime'), cp = require('child_process');
const { fs, path } = rt;
const FILES = ['AGENTS.md', 'CLAUDE.md', 'README.md', 'lineages/BRIEF.md', 'lineages/LOOP.md', 'lineages/GROWTH.md',
  'lineages/_tools/eval.js', 'scripts/status.sh', 'loop/run-lineage.sh', 'loop/wave-prompt.md',
  'loop/runtime.js', 'loop/run-job.js', 'loop/check.js', 'loop/runner.js', 'loop/activate-after-wave.js', 'loop/test/runtime.test.js'];
const hash = file => fs.existsSync(file) ? rt.crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex') : null;
function identity(pid) {
  try { return cp.execFileSync('/bin/ps', ['-p', String(pid), '-o', 'lstart=', '-o', 'command='], { encoding: 'utf8' }).trim(); }
  catch { return ''; }
}
function ownsStop(plan) {
  try { const s = fs.statSync(plan.stop); return s.ino === plan.stopIno && s.mtimeMs === plan.stopMtime && fs.readFileSync(plan.stop, 'utf8') === plan.token; }
  catch { return false; }
}
function busy(root) {
  const rows = cp.execFileSync('/bin/ps', ['-axo', 'pid=,command='], { encoding: 'utf8' }).split('\n')
    .map(line => line.trim().match(/^(\d+)\s+(.+)$/)).filter(Boolean)
    .map(m => ({ pid: +m[1], command: m[2] }))
    .filter(p => p.pid !== process.pid && /(?:claude|unswbc|g2eval\.py|batch\.sh|match\.sh|eval\.js|runner\.js run|run-job\.js|check\.js)/.test(p.command));
  const pids = new Set(rows.filter(p => p.command.includes(root + '/')).map(p => p.pid));
  if (rows.length) {
    const result = cp.spawnSync('/usr/sbin/lsof', ['-a', '-p', rows.map(p => p.pid).join(','), '-d', 'cwd', '-Fn'], { encoding: 'utf8' });
    if (result.error || ![0, 1].includes(result.status)) throw Error('cannot inspect remaining evaluation processes');
    let pid;
    for (const line of result.stdout.split('\n')) {
      if (line.startsWith('p')) pid = +line.slice(1);
      if (line.startsWith('n') && (line.slice(1) === root || line.slice(1).startsWith(root + '/'))) pids.add(pid);
    }
  }
  return [...pids];
}
function deploy(plan) {
  if (!ownsStop(plan)) throw Error('STOP changed; automatic transition cancelled');
  for (const f of plan.files) if (hash(path.join(plan.root, f.path)) !== f.before) throw Error('common file changed since scheduling: ' + f.path);
  let patch = '*** Begin Patch\n';
  for (const f of plan.files) {
    const target = path.join(plan.root, f.path);
    if (hash(target) === rt.crypto.createHash('sha256').update(f.content).digest('hex')) continue;
    const lines = text => text.replace(/\n$/, '').split('\n');
    if (f.before === null) patch += '*** Add File: ' + target + '\n' + lines(f.content).map(l => '+' + l).join('\n') + '\n';
    else patch += '*** Update File: ' + target + '\n@@\n' + lines(fs.readFileSync(target, 'utf8')).map(l => '-' + l).join('\n') + '\n' + lines(f.content).map(l => '+' + l).join('\n') + '\n';
  }
  patch += '*** End Patch\n';
  cp.execFileSync(plan.applyPatch, [], { input: patch, cwd: plan.root, encoding: 'utf8' });
  for (const f of plan.files) if (hash(path.join(plan.root, f.path)) !== rt.crypto.createHash('sha256').update(f.content).digest('hex')) throw Error('deployed content mismatch: ' + f.path);
  const git = args => cp.execFileSync('git', args, { cwd: plan.root, encoding: 'utf8' }).trim();
  const files = plan.files.map(f => f.path);
  git(['add', '--', ...files]);
  if (git(['diff', '--cached', '--name-only', '--', ...files])) git(['commit', '-m', 'loop: activate isolated wave lifecycle from ' + plan.revision.slice(0, 8), '--', ...files]);
  return git(['rev-parse', 'HEAD']);
}
function schedule(root, name, pid, revision) {
  root = fs.realpathSync(root); rt.lineage(name);
  const owner = identity(pid);
  if (!owner.includes('loop/run-lineage.sh ' + name)) throw Error('PID is not the requested legacy lineage loop');
  const cwd = cp.execFileSync('/usr/sbin/lsof', ['-a', '-p', String(pid), '-d', 'cwd', '-Fn'], { encoding: 'utf8' });
  if (!cwd.split('\n').includes('n' + root)) throw Error('legacy loop PID belongs to another worktree');
  const git = args => cp.execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim();
  if (git(['status', '--porcelain', '--', ...FILES])) throw Error('common files have local changes; will not overwrite them');
  revision = rt.git(['rev-parse', revision + '^{commit}']);
  const dir = path.join(rt.DATA, 'control', 'handoffs', name + '-' + rt.crypto.randomUUID());
  fs.mkdirSync(dir, { recursive: true });
  // Preserve the installed apply_patch entry point beyond the current Codex session's temporary PATH.
  const patchTool = cp.execFileSync('/usr/bin/which', ['apply_patch'], { encoding: 'utf8' }).trim();
  const applyPatch = path.join(dir, 'apply_patch'); fs.symlinkSync(fs.realpathSync(patchTool), applyPatch);
  const files = FILES.map(file => ({ path: file, before: hash(path.join(root, file)), content: cp.execFileSync('git', ['show', revision + ':' + file], { cwd: rt.ROOT, encoding: 'utf8' }) }));
  const stop = path.join(root, 'lineages', name, 'STOP'), token = 'automatic structural transition ' + rt.crypto.randomUUID() + '\n';
  fs.writeFileSync(stop, token, { flag: 'wx' });
  const stat = fs.statSync(stop), file = path.join(dir, 'plan.json');
  const plan = { root, name, pid: +pid, owner, revision, files, applyPatch, stop, token, stopIno: stat.ino, stopMtime: stat.mtimeMs,
    dir, status: 'waiting-for-wave', scheduled: new Date().toISOString() };
  rt.write(file, plan);
  const fd = fs.openSync(path.join(dir, 'watcher.log'), 'a');
  const child = cp.spawn('/usr/bin/caffeinate', ['-i', process.execPath, __filename, 'watch', file], { detached: true, stdio: ['ignore', fd, fd], cwd: rt.ROOT });
  child.unref(); fs.closeSync(fd);
  rt.write(file, { ...plan, watcherPid: child.pid });
  console.log(JSON.stringify({ name, status: plan.status, plan: file, watcherPid: child.pid }));
  return file;
}
async function watch(file) {
  let plan = rt.read(file);
  const update = (status, extra = {}) => { plan = { ...plan, ...extra, status, updated: new Date().toISOString() }; rt.write(file, plan); console.log(plan.updated, status, extra); };
  try {
    while (identity(plan.pid) === plan.owner) {
      if (!ownsStop(plan)) { update('cancelled-stop-changed'); return; }
      await rt.sleep(10000);
    }
    update('waiting-for-local-jobs');
    // Two quiet observations prevent a just-finished batch from handing over to its next child unnoticed.
    let quiet = 0;
    while (quiet < 2) {
      if (!ownsStop(plan)) { update('cancelled-stop-changed'); return; }
      const pids = busy(plan.root);
      quiet = pids.length ? 0 : quiet + 1;
      if (pids.length) update('waiting-for-local-jobs', { pendingPids: pids });
      if (quiet < 2) await rt.sleep(10000);
    }
    update('deploying', { pendingPids: [] });
    const commit = deploy(plan);
    if (!ownsStop(plan)) { update('deployed-but-stop-changed', { commit }); return; }
    fs.unlinkSync(plan.stop); // Only our exact, unchanged marker; never a user-created STOP.
    const log = path.join(plan.root, 'lineages', plan.name, 'waves', 'runner.log'), fd = fs.openSync(log, 'a');
    const child = cp.spawn('/usr/bin/caffeinate', ['-i', process.execPath, path.join(plan.root, 'loop/runner.js'), 'run', plan.name],
      { cwd: plan.root, detached: true, stdio: ['ignore', fd, fd] });
    await new Promise((resolve, reject) => { child.once('spawn', resolve); child.once('error', reject); });
    child.unref(); fs.closeSync(fd);
    await rt.sleep(1000);
    if (!rt.alive(child.pid)) throw Error('new runner exited during startup; inspect ' + log);
    update('started', { commit, runnerPid: child.pid, runnerLog: log });
  } catch (e) { update('failed', { error: String(e) }); process.exitCode = 1; }
}
if (require.main === module) {
  const [action, ...args] = process.argv.slice(2);
  Promise.resolve().then(() => {
    if (action === 'schedule') return schedule(...args);
    if (action === 'watch') return watch(...args);
    throw Error('usage: activate-after-wave.js schedule <worktree> <lineage> <legacy PID> <revision>');
  }).catch(e => { console.error(e.message); process.exitCode = 1; });
}
module.exports = { FILES, hash, ownsStop, deploy, identity, busy };
