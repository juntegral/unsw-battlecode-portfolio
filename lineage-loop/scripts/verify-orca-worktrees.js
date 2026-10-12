#!/usr/bin/env node
// Read-only verification of the copied pause checkpoint and frozen confirmations.
const fs = require('fs');
const path = require('path');
const cp = require('child_process');
const crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..');
const PARENT = path.dirname(ROOT);
const WORKSPACES = '~/orca/workspaces/unsw-arena';
const sha256 = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const git = (cwd, args) => cp.execFileSync('git', args, { cwd, encoding:'utf8' }).trim();
function verify(name, compareSource = true) {
  const target = path.join(WORKSPACES, name), source = path.join(PARENT, 'unsw-arena-' + name);
  const dir = path.join(target, 'lineages', name), checkpoint = read(path.join(dir, 'PAUSED.json'));
  const rt = require(path.join(target, 'loop/runtime.js'));
  const check = require(path.join(target, 'loop/check.js'));
  if (!fs.existsSync(path.join(dir, 'STOP'))) throw Error(name + ': missing STOP');
  if (rt.digest(path.join(dir, 'bot')) !== checkpoint.botHash) throw Error(name + ': bot hash mismatch');
  for (const row of checkpoint.evaluations) {
    const file = path.join(dir, row.path);
    if (sha256(file) !== row.sha256) throw Error(name + ': row hash mismatch ' + row.path);
    if (compareSource && fs.existsSync(source) && sha256(file) !== sha256(path.join(source, 'lineages', name, row.path)))
      throw Error(name + ': source row mismatch ' + row.path);
  }
  const active = read(path.join(dir, 'waves/active.json'));
  if (active.root !== target || active.work !== path.join(dir, 'waves', checkpoint.wave) ||
      active.baselineHash !== checkpoint.botHash || read(path.join(dir, 'waves/last.json')).outcome !== 'incomplete')
    throw Error(name + ': wave relocation changed the pause');
  const reports = [];
  for (const sub of fs.readdirSync(path.join(dir, 'checks'))) {
    const base = path.join(dir, 'checks', sub), planFile = path.join(base, 'plan.json'), reportFile = path.join(base, 'report.json');
    if (!fs.existsSync(planFile) || !fs.existsSync(reportFile)) continue;
    const plan = read(planFile), report = read(reportFile);
    if (plan.dir !== base || report.dir !== base) throw Error(name + ': stale confirmation path ' + sub);
    for (const key of Object.keys(plan)) {
      if (JSON.stringify(plan[key]) !== JSON.stringify(report[key])) throw Error(name + ': plan/report mismatch ' + sub + '/' + key);
    }
    if (report.status === 'valid') {
      const candidate = check.rows(path.join(base, 'candidate-results/rows.jsonl'), plan.expected);
      const baseline = plan.baselineHash && check.rows(path.join(base, 'baseline-results/rows.jsonl'), plan.expected);
      check.verifyConditions(candidate, plan);
      if (baseline) check.verifyConditions(baseline, plan);
      if (JSON.stringify(check.compare(baseline, candidate)) !== JSON.stringify(report.result))
        throw Error(name + ': report differs from raw results ' + sub);
      for (const [rel, expected] of [['candidate',plan.candidateHash],['baseline',plan.baselineHash],['maps',plan.mapHash],
        ...Object.entries(plan.opponentHashes).map(([opp,hash]) => ['opponents/' + opp,hash])]) {
        if (expected && rt.digest(path.join(base, rel)) !== expected) throw Error(name + ': frozen input changed ' + sub + '/' + rel);
      }
    }
    reports.push({id:sub,status:report.status});
  }
  const common = git(target, ['rev-parse', '--git-common-dir']);
  if (path.resolve(target, common) !== path.join(ROOT, '.git')) throw Error(name + ': not same Git repository');
  const initial = git(target, ['rev-list', '--max-parents=0', 'HEAD']);
  if (initial.split('\n').length !== 1 || !initial) throw Error(name + ': branch does not have one independent root');
  if (git(target, ['status', '--porcelain'])) throw Error(name + ': worktree is not clean');
  return {name,target,branch:git(target,['branch','--show-current']),head:git(target,['rev-parse','HEAD']),
    rootCommit:initial,botHash:checkpoint.botHash,rows:checkpoint.evaluations.length,reports};
}
if (require.main === module) {
  try { console.log(JSON.stringify(['g3','g4'].map(name => verify(name)), null, 2)); }
  catch (error) { console.error(error.stack); process.exitCode = 1; }
}
module.exports = { verify };
