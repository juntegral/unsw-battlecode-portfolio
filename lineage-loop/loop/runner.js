#!/usr/bin/env node
// Wave lifecycle, independent of bot design and numerical promotion criteria.
const rt = require('./runtime');
const { fs, path } = rt;
function baselineIntact(name, active) {
  const bot = path.join(rt.lineage(name), 'bot');
  return active.baselineHash ? fs.existsSync(bot) && rt.digest(bot) === active.baselineHash : !fs.existsSync(path.join(bot, 'bot.toml'));
}

function begin(name) {
  const dir = rt.lineage(name), waves = path.join(dir, 'waves');
  fs.mkdirSync(waves, { recursive: true });
  const countFile = path.join(waves, 'counter.json');
  const log = path.join(waves, 'index.log');
  const oldStarts = fs.existsSync(log) ? (fs.readFileSync(log, 'utf8').match(/wave \S+ start/g) || []).length : 0;
  const n = Math.max(fs.existsSync(countFile) ? rt.read(countFile).n : 0, oldStarts) + 1;
  rt.write(countFile, { n });
  const id = 'w' + String(n).padStart(6, '0'), work = path.join(waves, id);
  fs.mkdirSync(work);
  const bot = path.join(dir, 'bot'), baseline = path.join(work, 'baseline');
  const baselineHash = fs.existsSync(path.join(bot, 'bot.toml')) ? rt.snapshot(bot, baseline) : null;
  const state = { schema: 1, id, name, root: rt.ROOT, work, baseline, baselineHash,
    ready: rt.ready(dir), started: new Date().toISOString() };
  rt.write(path.join(work, 'start.json'), state);
  rt.write(path.join(waves, 'active.json'), state);
  return state;
}
function validateReport(name, active, file) {
  if (!file || !rt.inside(path.join(rt.lineage(name), 'checks'), file)) throw Error('confirmation report must be inside your lineage checks/');
  const report = rt.read(file), plan = rt.read(path.join(path.dirname(file), 'plan.json'));
  if (report.status !== 'valid' || report.lineage !== name || report.baselineHash !== active.baselineHash || report.dir !== path.dirname(file)) throw Error('report does not confirm this baseline');
  for (const key of Object.keys(plan)) if (JSON.stringify(plan[key]) !== JSON.stringify(report[key])) throw Error('report differs from frozen plan: ' + key);
  const { rows, compare, verifyConditions } = require('./check');
  const cand = rows(path.join(report.dir, 'candidate-results/rows.jsonl'), plan.expected);
  const base = plan.baselineHash && rows(path.join(report.dir, 'baseline-results/rows.jsonl'), plan.expected);
  verifyConditions(cand, plan);
  if (base) verifyConditions(base, plan);
  if (JSON.stringify(compare(base, cand)) !== JSON.stringify(report.result)) throw Error('report summary differs from raw results');
  for (const [dir, hash] of [['candidate', plan.candidateHash], ['baseline', plan.baselineHash], ['maps', plan.mapHash],
    ...Object.entries(plan.opponentHashes).map(([opp, hash]) => ['opponents/' + opp, hash])]) {
    if (hash && rt.digest(path.join(report.dir, dir)) !== hash) throw Error('frozen input changed: ' + dir);
  }
  if (rt.digest(path.join(rt.lineage(name), 'bot')) !== plan.candidateHash) throw Error('bot/ is not the confirmed candidate');
  return report;
}
function finish(name, outcome, reason, evidence) {
  if (!['adopt', 'reject', 'incomplete'].includes(outcome) || !reason) throw Error('usage: finish <lineage> adopt|reject|incomplete <reason> [report.json]');
  const active = rt.wave(name), dir = rt.lineage(name), current = path.join(dir, 'CURRENT.md');
  if (fs.existsSync(path.join(active.work, 'finish.json'))) throw Error('this wave already has a final decision');
  if (!fs.existsSync(current) || fs.statSync(current).mtimeMs < Date.parse(active.started)) throw Error('update CURRENT.md before finishing');
  if (rt.jobs(name).length) throw Error('wait for registered evaluations before finishing');
  const result = { wave: active.id, outcome, reason, at: new Date().toISOString() };
  if (outcome === 'adopt') {
    const report = validateReport(name, active, path.resolve(evidence || ''));
    const version = rt.ready(dir);
    if (version <= active.ready) throw Error('append a new ready: rN to NOTES.md');
    const paths = ['bot', 'NOTES.md', 'CURRENT.md'].map(p => 'lineages/' + name + '/' + p);
    rt.git(['add', '-A', '--', ...paths]);
    if (rt.git(['diff', '--cached', '--name-only', '--', ...paths])) rt.git(['commit', '-m', name + ' r' + version + ': ' + reason, '--', ...paths]);
    Object.assign(result, { version, report: path.resolve(evidence), candidateHash: report.candidateHash, commit: rt.git(['rev-parse', 'HEAD']) });
  } else if (!baselineIntact(name, active)) {
    throw Error('keep the previous best in bot/ for reject or incomplete; working changes belong in a candidate directory');
  }
  rt.write(path.join(active.work, 'finish.json'), result);
  console.log(JSON.stringify(result));
  return result;
}
function publish(name, active, result) {
  const report = validateReport(name, active, result.report);
  if (rt.ready(rt.lineage(name)) !== result.version || report.candidateHash !== result.candidateHash) throw Error('adopted version changed after finish');
  const label = name + '-r' + result.version, destination = path.join(rt.DATA, 'releases', label);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  if (fs.existsSync(destination)) {
    if (rt.digest(destination) !== result.candidateHash) throw Error('release name already has different contents: ' + label);
  } else {
    const staging = path.join(path.dirname(destination), '.' + label + '-' + rt.crypto.randomUUID());
    if (rt.snapshot(path.join(report.dir, 'candidate'), staging) !== result.candidateHash) throw Error('snapshot changed during export');
    // The external daemon only sees a complete release directory.
    fs.renameSync(staging, destination);
  }
  rt.write(destination + '.sha256.json', { snapshot_at: new Date().toISOString(), from: report.dir,
    commit: result.commit, files: rt.hashes(destination) });
  return label;
}
async function run(name, model = process.env.UNSW_MODEL || 'claude-opus-5-5', fallback = process.env.UNSW_FALLBACK_MODEL || 'claude-fable-5') {
  const dir = rt.lineage(name), waves = path.join(dir, 'waves');
  fs.mkdirSync(waves, { recursive: true });
  const held = await rt.lock('runner-' + name, { wait: false });
  let stopping = false, child, completed = 0;
  const stop = signal => { stopping = true; child?.kill(signal); };
  const int = () => stop('SIGINT'), term = () => stop('SIGTERM');
  process.on('SIGINT', int); process.on('SIGTERM', term);
  const stopped = () => stopping || fs.existsSync(path.join(dir, 'STOP'));
  const log = message => { const line = new Date().toLocaleString('sv-SE') + ' ' + message; console.log(line); fs.appendFileSync(path.join(waves, 'index.log'), line + '\n'); };
  try {
    const lastFile = path.join(waves, 'last.json'), activeFile = path.join(waves, 'active.json');
    if (fs.existsSync(activeFile)) {
      const last = fs.existsSync(lastFile) ? rt.read(lastFile) : {}, previous = rt.read(activeFile);
      if (!(last.wave === previous.id && last.outcome === 'adopt') && !baselineIntact(name, previous)) {
        throw Error('previous wave left an unconfirmed bot/ change; inspect ' + previous.work + ' before restarting');
      }
    }
    fs.mkdirSync(path.join(rt.DATA, 'logs', name, 'online'), { recursive: true });
    if (!fs.existsSync(path.join(dir, 'logs'))) fs.symlinkSync(path.join(rt.DATA, 'logs', name), path.join(dir, 'logs'));
    await rt.drain(name);
    while (!stopped()) {
      const disk = fs.statfsSync(rt.ROOT);
      if (disk.bavail * disk.bsize < 20 * 1024 ** 3) { log('disk free < 20 GiB; waiting'); await rt.sleep(30000); continue; }
      const active = begin(name);
      let prompt = fs.readFileSync(path.join(rt.ROOT, 'loop/wave-prompt.md'), 'utf8').replaceAll('{{LINEAGE}}', name);
      const lastFile = path.join(waves, 'last.json');
      prompt += '\nWave ID: ' + active.id + '.\n';
      if (fs.existsSync(lastFile)) prompt += 'Previous runner outcome: ' + JSON.stringify(rt.read(lastFile)) + '\n';
      const invoke = async (which, suffix) => {
        const file = path.join(waves, active.id + suffix + '.jsonl'), fd = fs.openSync(file, 'w');
        try {
          const result = await rt.command('claude', ['-p', prompt, '--model', which, '--dangerously-skip-permissions', '--output-format', 'stream-json', '--verbose'], {
            env: { ...process.env, UNSW_WAVE_ID: active.id, UNSW_LINEAGE: name }, stdio: ['ignore', fd, fd],
            onSpawn(p) { child = p; held.child(p.pid); }
          });
          return { ...result, refused: /"stop_reason"\s*:\s*"refusal"/.test(fs.readFileSync(file, 'utf8')) };
        } finally { fs.closeSync(fd); child = undefined; held.child(null); }
      };
      log('wave ' + active.id + ' start');
      let execution, record;
      try {
        execution = await invoke(model, '');
        await rt.drain(name);
        const finishFile = path.join(active.work, 'finish.json');
        // Do not repeat a completed decision or an interrupted wave with a mutated baseline.
        const unchanged = baselineIntact(name, active);
        if ((execution.code || execution.refused) && !stopped() && !fs.existsSync(finishFile) && unchanged) {
          log('wave ' + active.id + ' fallback ' + fallback);
          execution = await invoke(fallback, '-fallback');
          await rt.drain(name);
        }
        if (!execution.code && !execution.refused && fs.existsSync(finishFile)) {
          record = rt.read(finishFile);
          if (record.wave !== active.id) throw Error('stale finish record');
          if (record.outcome === 'adopt') log('exported ' + publish(name, active, record));
        } else record = { outcome: 'incomplete', reason: 'no successful explicit finish; nothing exported' };
      } catch (e) { record = { outcome: 'incomplete', reason: String(e) }; }
      // Never let an orphaned registered job race the next wave.
      await rt.drain(name);
      const last = { wave: active.id, ...record, exit: execution?.code ?? 1, at: new Date().toISOString() };
      rt.write(path.join(active.work, 'result.json'), last); rt.write(lastFile, last);
      log('wave ' + active.id + ' exit ' + last.exit + ' (' + last.outcome + ')');
      rt.commit(name, name + ' wave ' + active.id + ': ' + last.outcome);
      if (record.outcome !== 'adopt' && !baselineIntact(name, active)) {
        throw Error('unconfirmed bot/ change preserved for review; runner stopped without resetting files');
      }
      completed++;
      if (process.env.UNSW_MAX_WAVES && completed >= +process.env.UNSW_MAX_WAVES) break;
      if (!stopped()) await rt.sleep(last.exit ? 60000 : 5000);
    }
    if (stopped()) log('STOP: current wave and registered evaluations finished');
  } finally { held.release(); process.off('SIGINT', int); process.off('SIGTERM', term); }
}
if (require.main === module) {
  const [action, ...args] = process.argv.slice(2);
  Promise.resolve().then(() => {
    if (action === 'run') return run(...args);
    if (action === 'finish') return finish(...args);
    throw Error('usage: runner.js run|finish <lineage> ...');
  }).catch(e => { console.error(e.message); process.exitCode = 1; });
}
module.exports = { begin, finish, validateReport, publish, run };
