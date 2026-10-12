#!/usr/bin/env node
// Operator-only, read-only view of the two active clean lineages.
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const WORKSPACES = '~/orca/workspaces/unsw-arena';
const CONTROL = path.join(path.dirname(ROOT), 'unsw-arena-clean-control');
const NAMES = ['g4', 'g5'];

const exists = file => fs.existsSync(file);
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
function alive(pid) {
  if (!Number.isInteger(pid) || pid <= 0) return false;
  try { process.kill(pid, 0); return true; }
  catch (error) { return error.code === 'EPERM'; }
}
function rows(file) {
  if (!exists(file)) return { done: 0, updated: null };
  const content = fs.readFileSync(file, 'utf8');
  // Count only newline-terminated rows; an evaluator may be appending one now.
  const completeLines = content.split('\n').slice(0, -1);
  return { done: completeLines.filter(Boolean).length, updated: fs.statSync(file).mtime.toISOString() };
}
function activeJobs(name, root) {
  const directory = path.join(CONTROL, 'jobs');
  if (!exists(directory)) return [];
  return fs.readdirSync(directory).filter(file => file.endsWith('.json')).flatMap(file => {
    const job = read(path.join(directory, file));
    return job.lineage === name && job.root?.normalize('NFD') === root.normalize('NFD') &&
      ['queued', 'running'].includes(job.status) ? [{ status: job.status, pid: job.pid, childPid: job.childPid,
        alive: alive(job.pid) || alive(job.childPid) }] : [];
  });
}
function confirmation(dir, wave) {
  const checks = path.join(dir, 'checks');
  if (!exists(checks)) return null;
  const plans = fs.readdirSync(checks).filter(name => name.startsWith(wave + '-')).flatMap(name => {
    const folder = path.join(checks, name), file = path.join(folder, 'plan.json');
    return exists(file) ? [{ folder, plan: read(file) }] : [];
  }).filter(x => x.plan.wave === wave).sort((a, b) => b.plan.at.localeCompare(a.plan.at));
  if (!plans.length) return null;
  const { folder, plan } = plans[0];
  return { id: path.basename(folder), expected: plan.expected,
    baseline: rows(path.join(folder, 'baseline-results/rows.jsonl')),
    candidate: rows(path.join(folder, 'candidate-results/rows.jsonl')),
    report: exists(path.join(folder, 'report.json')) ? read(path.join(folder, 'report.json')).status : null };
}
function lineage(name) {
  const root = path.join(WORKSPACES, name), dir = path.join(root, 'lineages', name);
  if (!exists(dir)) return { name, state: 'missing' };
  const ownerFile = path.join(CONTROL, 'locks', 'runner-' + name, 'owner.json');
  const owner = exists(ownerFile) ? read(ownerFile) : null;
  const running = owner && (alive(owner.pid) || alive(owner.childPid));
  const activeFile = path.join(dir, 'waves/active.json');
  const lastFile = path.join(dir, 'waves/last.json');
  const active = exists(activeFile) ? read(activeFile) : null;
  const jobs = activeJobs(name, root);
  const stop = exists(path.join(dir, 'STOP'));
  const state = stop ? 'stopping' : running ? jobs.some(j => j.status === 'queued') ? 'queued' : 'running' :
    owner ? 'stale-lock' : 'stopped';
  return { name, root, state, wave: active?.id || null, started: active?.started || null,
    last: exists(lastFile) ? read(lastFile) : null, jobs,
    confirmation: active ? confirmation(dir, active.id) : null };
}
function snapshot() {
  const stat = fs.statfsSync(ROOT);
  return { at: new Date().toISOString(), diskFreeGiB: Math.round(stat.bavail * stat.bsize / 2 ** 30),
    lineages: NAMES.map(lineage) };
}
function print(data) {
  console.log(`disk free ${data.diskFreeGiB} GiB`);
  for (const item of data.lineages) {
    let detail = '';
    if (item.confirmation) {
      const c = item.confirmation;
      detail = ` | check ${c.id}: baseline ${c.baseline.done}/${c.expected}, candidate ${c.candidate.done}/${c.expected}`;
      if (c.report) detail += `, report ${c.report}`;
    }
    console.log(`${item.name} ${item.wave || '-'} ${item.state}${detail}`);
  }
}
if (require.main === module) {
  try { const result = snapshot(); if (process.argv.includes('--json')) console.log(JSON.stringify(result, null, 2)); else print(result); }
  catch (error) { console.error(error.stack); process.exitCode = 1; }
}
module.exports = { snapshot };
