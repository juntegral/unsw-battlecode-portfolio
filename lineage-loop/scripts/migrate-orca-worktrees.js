#!/usr/bin/env node
// One-time, additive migration of paused g3/g4 into child worktrees of this Git repo.
// The original repositories are deliberately left untouched until separate verification.
const fs = require('fs');
const path = require('path');
const cp = require('child_process');
const crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..');
const PARENT = path.dirname(ROOT);
const WORKSPACES = '~/orca/workspaces/unsw-arena';
const { profile } = require('./clean-lineages');

const read = file => fs.readFileSync(file, 'utf8');
const write = (file, body) => fs.writeFileSync(file, body);
const json = file => JSON.parse(read(file));
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const git = (dir, args) => cp.execFileSync('git', args, { cwd: dir, encoding: 'utf8' }).trim();
const mustReplace = (body, before, after, label) => {
  if (!body.includes(before)) throw Error('Missing patch anchor: ' + label);
  return body.replace(before, after);
};
function walk(dir, visit) {
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    const file = path.join(dir, item.name);
    if (item.isSymbolicLink()) continue;
    if (item.isDirectory()) {
      if (item.name !== 'games' && item.name !== '.git') walk(file, visit);
    } else if (item.isFile()) visit(file);
  }
}
function verifyPause(name, root) {
  const dir = path.join(root, 'lineages', name), paused = json(path.join(dir, 'PAUSED.json'));
  const rt = require(path.join(root, 'loop/runtime.js'));
  if (!fs.existsSync(path.join(dir, 'STOP')) || paused.botHash !== rt.digest(path.join(dir, 'bot')))
    throw Error(name + ' STOP or bot hash changed');
  for (const row of paused.evaluations) {
    if (hash(path.join(dir, row.path)) !== row.sha256) throw Error(name + ' raw row hash changed: ' + row.path);
  }
  return { botHash: paused.botHash, rows: paused.evaluations.length, wave: paused.wave };
}
function relocateJson(dir, oldRoot, newRoot) {
  let count = 0;
  walk(dir, file => {
    if (!file.endsWith('.json')) return;
    const body = read(file);
    if (!body.includes(oldRoot)) return;
    JSON.parse(body);
    const changed = body.replaceAll(oldRoot, newRoot);
    JSON.parse(changed);
    write(file, changed);
    count++;
  });
  return count;
}
function patchRunner(root, oldRoot) {
  const file = path.join(root, 'loop/runner.js');
  let body = read(file).replaceAll(oldRoot, root);
  const original = `function finish(name, outcome, reason, evidence) {
  if (!['adopt', 'reject', 'incomplete'].includes(outcome) || !reason) throw Error('usage: finish <lineage> adopt|reject|incomplete <reason> [report.json]');`;
  const replacement = `function requestFinish(name, outcome, reason, evidence) {
  if (!['adopt', 'reject', 'incomplete'].includes(outcome) || !reason) throw Error('usage: finish <lineage> adopt|reject|incomplete <reason> [report.json]');
  const active = rt.wave(name), dir = rt.lineage(name), current = path.join(dir, 'CURRENT.md');
  if (fs.existsSync(path.join(active.work, 'finish.json')) || fs.existsSync(path.join(active.work, 'finish-request.json'))) throw Error('this wave already has a final decision');
  if (!fs.existsSync(current) || fs.statSync(current).mtimeMs < Date.parse(active.started)) throw Error('update CURRENT.md before finishing');
  if (rt.jobs(name).length) throw Error('wait for registered evaluations before finishing');
  if (outcome === 'adopt') {
    validateReport(name, active, path.resolve(evidence || ''));
    if (rt.ready(dir) <= active.ready) throw Error('append a new ready: rN to NOTES.md');
  } else if (!baselineIntact(name, active)) throw Error('keep the previous best in bot/ for reject or incomplete');
  const request = { wave: active.id, outcome, reason, evidence: evidence ? path.resolve(evidence) : null, at: new Date().toISOString() };
  rt.write(path.join(active.work, 'finish-request.json'), request);
  console.log(JSON.stringify(request));
  return request;
}
function finish(name, outcome, reason, evidence, trustedActive) {
  if (!['adopt', 'reject', 'incomplete'].includes(outcome) || !reason) throw Error('usage: finish <lineage> adopt|reject|incomplete <reason> [report.json]');`;
  body = mustReplace(body, original, replacement, 'finish request');
  body = mustReplace(body,
    `function finish(name, outcome, reason, evidence, trustedActive) {
  if (!['adopt', 'reject', 'incomplete'].includes(outcome) || !reason) throw Error('usage: finish <lineage> adopt|reject|incomplete <reason> [report.json]');
  const active = rt.wave(name), dir = rt.lineage(name), current = path.join(dir, 'CURRENT.md');`,
    `function finish(name, outcome, reason, evidence, trustedActive) {
  if (!['adopt', 'reject', 'incomplete'].includes(outcome) || !reason) throw Error('usage: finish <lineage> adopt|reject|incomplete <reason> [report.json]');
  const active = trustedActive || rt.wave(name), dir = rt.lineage(name), current = path.join(dir, 'CURRENT.md');`,
    'trusted active state');
  const oldGuard = `
  // Refuse an accidental launch outside the mandatory OS sandbox.
  try {
    const fd=fs.openSync(${JSON.stringify(path.join(PARENT, 'unsw-arena-archive/legacy-20260928/README.md'))},'r'); fs.closeSync(fd);
    throw Error('Use .isolation/launch.sh: legacy archive is readable outside the sandbox');
  } catch(e) { if(!['EACCES','EPERM'].includes(e.code)) throw e; }
`;
  const newGuard = `
  // Only the launcher runs this trusted supervisor; research children are sandboxed.
  if (process.env.UNSW_OPERATOR_LAUNCH !== '1') throw Error('Start through .isolation/launch.sh');
  if (!fs.existsSync(path.join(rt.ROOT, '.git'))) throw Error('Missing Git worktree pointer');
`;
  body = mustReplace(body, oldGuard, newGuard, 'supervisor guard');
  body = mustReplace(body,
    `const result = await rt.command('claude', ['-p', prompt,`,
    `const { UNSW_OPERATOR_LAUNCH, ...agentEnv } = process.env;
          const result = await rt.command('/usr/bin/sandbox-exec', ['-f', path.join(rt.ROOT, '.isolation/profile.sb'), 'claude', '-p', prompt,`,
    'sandboxed Claude invocation');
  body = mustReplace(body,
    `env: { ...process.env, UNSW_WAVE_ID: active.id, UNSW_LINEAGE: name },`,
    `env: { ...agentEnv, UNSW_WAVE_ID: active.id, UNSW_LINEAGE: name },`,
    'child environment');
  body = mustReplace(body,
    `const finishFile = path.join(active.work, 'finish.json');`,
    `const finishFile = path.join(active.work, 'finish.json');
        const requestFile = path.join(active.work, 'finish-request.json');`,
    'finish bridge path');
  body = mustReplace(body,
    `!fs.existsSync(finishFile) && unchanged)`,
    `!fs.existsSync(requestFile) && unchanged)`,
    'fallback guard');
  body = mustReplace(body,
    `if (!execution.code && !execution.refused && fs.existsSync(finishFile)) {
          record = rt.read(finishFile);`,
    `if (!execution.code && !execution.refused && fs.existsSync(requestFile)) {
          const request = rt.read(requestFile);
          if (request.wave !== active.id) throw Error('stale finish request');
          record = finish(name, request.outcome, request.reason, request.evidence, active);`,
    'trusted finalization');
  body = mustReplace(body,
    `if (action === 'finish') return finish(...args);`,
    `if (action === 'finish') return requestFinish(...args);`,
    'CLI finish request');
  body = mustReplace(body,
    `module.exports = { begin, finish, validateReport, publish, run };`,
    `module.exports = { begin, requestFinish, validateReport, publish, run };`,
    'module export');
  write(file, body);
  cp.execFileSync(process.execPath, ['--check', file], { stdio: 'inherit' });
}
function patchProfile(root, name) {
  profile(root, name);
  const file = path.join(root, '.isolation/profile.sb');
  let body = read(file);
  const former = `(deny file-read* file-write* (subpath ${JSON.stringify(WORKSPACES)}))`;
  const own = JSON.stringify(root);
  // Node needs metadata of parent directories for realpath/module loading.
  const parent = `(deny file-read-data file-write* (require-all (subpath ${JSON.stringify(WORKSPACES)}) (require-not (subpath ${own}))))`;
  body = mustReplace(body, former, parent, 'worktree filesystem guard');
  body += `(deny file-read* file-write* (subpath ${JSON.stringify(path.join(root, '.git'))}))\n`;
  write(file, body);
}
function patchLauncher(root, name, oldRoot) {
  const file = path.join(root, '.isolation/launch.sh');
  let body = read(file).replaceAll(oldRoot, root);
  body = mustReplace(body, `exec /usr/bin/caffeinate -i /usr/bin/sandbox-exec -f .isolation/profile.sb`,
    `export UNSW_OPERATOR_LAUNCH=1\nexec /usr/bin/caffeinate -i`, 'trusted supervisor launch');
  write(file, body);
  fs.chmodSync(file, 0o755);
}
function patchDocs(root, name) {
  const brief = path.join(root, 'lineages/BRIEF.md');
  let body = read(brief);
  body = body.replace('이 저장소는 새 Git 이력으로 시작하며 다른 계통·과거 아카이브·외부 작업 폴더는 OS에서 접근 차단된다.',
    '이 계통은 공통 Git 저장소의 부모 없는 별도 브랜치에서 시작한다. 연구 프로세스는 공용 Git 이력·다른 계통·과거 아카이브를 OS에서 읽을 수 없다.');
  body += '\n- 워크트리는 Orca의 unsw-arena 하위에 표시된다. 연구 실행은 이 폴더의 `.isolation/launch.sh`로만 시작한다.\n';
  write(brief, body);
  write(path.join(root, 'README.md'), `# ${name} 연구 워크트리\n\nunsw-arena의 하위 Git 워크트리. 부모 없는 별도 브랜치에서 현재 계통의 코드와 보존한 실험 자료를 이어간다. Orca의 트리 표시는 탐색용이며, 실제 연구는 이 폴더의 .isolation/launch.sh로 실행한다. 연구 프로세스는 공용 Git 이력·다른 계통·아카이브를 읽지 못한다.\n\n중지: touch lineages/${name}/STOP. 현재 웨이브와 등록된 평가 후 종료한다.\n`);
  const resume = path.join(root, 'lineages', name, 'RESUME.md');
  fs.appendFileSync(resume, '\n## 하위 워크트리 이관\n- 이전 독립 저장소의 파일과 원자료를 체크섬 확인 후 이 워크트리로 옮겼다. STOP은 유지한다.\n- 기존 중단 웨이브의 원자료를 그대로 사용한다. 새 runner는 다음 웨이브 ID를 열어 이전 미완료 작업을 이어간다. 시드·조건을 다시 추첨하지 않는다.\n');
  fs.appendFileSync(path.join(root, 'loop/wave-prompt.md'), '\n공용 Git 이력이나 다른 워크트리를 조사하지 않는다. 자신의 RESUME.md와 PAUSED.json의 중단 작업·기존 원자료를 먼저 확인하고, 누락된 조건만 이어간다.\n');
}
function repairRunner(root, name) {
  const file = path.join(root, 'loop/runner.js');
  let body = read(file);
  body = mustReplace(body,
    `function finish(name, outcome, reason, evidence) {
  if (!['adopt', 'reject', 'incomplete'].includes(outcome) || !reason) throw Error('usage: finish <lineage> adopt|reject|incomplete <reason> [report.json]');
  const active = rt.wave(name), dir = rt.lineage(name), current = path.join(dir, 'CURRENT.md');`,
    `function finish(name, outcome, reason, evidence, trustedActive) {
  if (!['adopt', 'reject', 'incomplete'].includes(outcome) || !reason) throw Error('usage: finish <lineage> adopt|reject|incomplete <reason> [report.json]');
  const active = trustedActive || rt.wave(name), dir = rt.lineage(name), current = path.join(dir, 'CURRENT.md');`,
    'trusted active state repair');
  body = mustReplace(body,
    `record = finish(name, request.outcome, request.reason, request.evidence);`,
    `record = finish(name, request.outcome, request.reason, request.evidence, active);`,
    'trusted finish call repair');
  write(file, body);
  cp.execFileSync(process.execPath, ['--check', file]);
  git(root, ['add', '--', 'loop/runner.js']);
  git(root, ['commit', '-m', name + ': pass active wave to trusted finish bridge']);
  console.log(JSON.stringify({name,commit:git(root,['rev-parse','HEAD'])}));
}
function prepare(name) {
  if (!['g3', 'g4'].includes(name)) throw Error('name must be g3 or g4');
  const oldRoot = path.join(PARENT, 'unsw-arena-' + name), root = path.join(WORKSPACES, name);
  if (!fs.existsSync(oldRoot) || !fs.existsSync(root)) throw Error('source or destination missing');
  if (git(oldRoot, ['status', '--porcelain'])) throw Error('source repository is not clean');
  if (git(root, ['branch', '--show-current']) !== 'lineage-' + name + '-clean') throw Error('wrong destination branch');
  if (!git(root, ['status', '--short', '--branch']).startsWith('## No commits yet on lineage-' + name + '-clean'))
    throw Error('destination branch already committed');
  const source = verifyPause(name, oldRoot), copied = verifyPause(name, root);
  if (JSON.stringify(source) !== JSON.stringify(copied)) throw Error('checkpoint mismatch before migration');
  const work = path.join(root, 'lineages', name);
  const changed = relocateJson(work, oldRoot, root) + relocateJson(path.join(root, '.arena-data/releases'), oldRoot, root);
  const wrapper = path.join(root, 'lineages/_tools/unswbc');
  write(wrapper, mustReplace(read(wrapper), oldRoot, root, 'UNSWBC wrapper'));
  patchRunner(root, oldRoot);
  patchProfile(root, name);
  patchLauncher(root, name, oldRoot);
  patchDocs(root, name);
  const logs = path.join(work, 'logs');
  if (fs.existsSync(logs) || fs.existsSync(path.join(root, '.git', 'objects'))) throw Error('unexpected logs or nested Git directory');
  fs.symlinkSync(path.join(root, '.arena-data/logs', name), logs);
  const after = verifyPause(name, root);
  if (JSON.stringify(source) !== JSON.stringify(after)) throw Error('checkpoint mismatch after migration');
  cp.execFileSync(process.execPath, ['--check', path.join(root, 'loop/runtime.js')]);
  cp.execFileSync(process.execPath, ['--check', path.join(root, 'loop/check.js')]);
  git(root, ['add', '-A']);
  git(root, ['commit', '-m', name + ': resume clean lineage in Orca child worktree']);
  const count = git(root, ['rev-list', '--count', 'HEAD']);
  if (count !== '1') throw Error('new branch is not an orphan history');
  const result = {name, root, branch:'lineage-' + name + '-clean', commit:git(root, ['rev-parse', 'HEAD']), relocatedJson:changed, ...after};
  console.log(JSON.stringify(result, null, 2));
  return result;
}
if (require.main === module) {
  try {
    if (process.argv[2] === 'repair-profile') {
      const name = process.argv[3], root = path.join(WORKSPACES, name);
      if (!['g3', 'g4'].includes(name)) throw Error('name must be g3 or g4');
      patchProfile(root, name);
      git(root, ['add', '--', '.isolation/profile.sb']);
      git(root, ['commit', '-m', name + ': allow parent metadata for sandboxed tools']);
      console.log(JSON.stringify({ name, commit: git(root, ['rev-parse', 'HEAD']) }));
    } else if (process.argv[2] === 'repair-runner') {
      const name=process.argv[3];
      if (!['g3','g4'].includes(name)) throw Error('name must be g3 or g4');
      repairRunner(path.join(WORKSPACES,name),name);
    } else prepare(process.argv[2]);
  } catch (error) { console.error(error.stack); process.exitCode = 1; }
}
module.exports = { prepare, verifyPause };
