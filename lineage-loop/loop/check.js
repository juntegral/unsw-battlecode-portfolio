#!/usr/bin/env node
// Confirmation is separated from exploration: freeze inputs, then draw fresh seeds.
const rt = require('./runtime');
const { fs, path } = rt;
const OPPONENTS = ['replay_rules_v8', 'archetype_swarm', 'archetype_hunter', 'h2'];

function rows(file, expected) {
  if (!fs.existsSync(file)) throw Error('missing evaluation results: ' + file);
  const all = fs.readFileSync(file, 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse);
  const unique = new Map(all.map(r => [r.key, r]));
  if (unique.size !== expected || all.length !== expected) throw Error('incomplete or duplicate confirmation rows');
  for (const r of all) {
    if (r.error || r.exit !== 0 || r.botProblem || !Number.isFinite(r.G) || typeof r.won !== 'boolean' || typeof r.alive !== 'boolean') {
      throw Error('failed match is not valid evidence: ' + r.key);
    }
  }
  return unique;
}
function verifyConditions(result, plan) {
  const expected = new Set();
  for (const opp of Object.keys(plan.opponentHashes)) for (const map of plan.maps) for (const side of ['A', 'B']) for (const seed of plan.seeds) {
    expected.add([opp, map.replace(/\.map$/, ''), side, seed].join(':'));
  }
  if (expected.size !== plan.expected || result.size !== expected.size) throw Error('conditions do not match the frozen plan');
  for (const [key, r] of result) {
    if (!expected.has(key) || key !== [r.opp, r.map, r.side, r.seed].join(':')) throw Error('unexpected condition: ' + key);
  }
}
function compare(base, candidate) {
  if (base && (base.size !== candidate.size || [...candidate.keys()].some(k => !base.has(k)))) throw Error('unpaired conditions');
  const group = list => {
    const n = list.length;
    const wins = list.filter(r => r.won).length;
    return { n, wins, survived: list.filter(r => r.alive).length, meanG: list.reduce((s, r) => s + r.G, 0) / n };
  };
  const cand = [...candidate.values()], old = base && [...base.values()];
  const breakdown = field => Object.fromEntries([...new Set(cand.map(r => r[field]))].sort().map(value => [value, {
    candidate: group(cand.filter(r => r[field] === value)), baseline: old && group(old.filter(r => r[field] === value))
  }]));
  return { candidate: group(cand), baseline: old && group(old), byMap: breakdown('map'), byOpponent: breakdown('opp'), bySide: breakdown('side') };
}
async function check(name, source) {
  const active = rt.wave(name), dir = rt.lineage(name), candidate = path.resolve(source || '');
  if (!rt.inside(dir, candidate) || candidate === path.join(dir, 'bot') || !fs.existsSync(path.join(candidate, 'bot.toml'))) {
    throw Error('candidate must be a separate bot project inside your lineage directory');
  }
  if (active.baselineHash && rt.digest(path.join(dir, 'bot')) !== active.baselineHash) throw Error('keep bot/ at the wave baseline until confirmation finishes');
  const fingerprint = rt.digest(candidate), checks = path.join(dir, 'checks');
  fs.mkdirSync(checks, { recursive: true });
  const previous = fs.readdirSync(checks).map(x => path.join(checks, x, 'plan.json')).filter(f => fs.existsSync(f))
    .map(rt.read).find(p => p.candidateHash === fingerprint && p.baselineHash === active.baselineHash);
  if (previous) {
    const report = path.join(previous.dir, 'report.json');
    if (fs.existsSync(report)) {
      console.log(report);
      if (rt.read(report).status !== 'valid') throw Error('previous confirmation is invalid; diagnose it, do not reroll seeds');
      return;
    }
    throw Error('this candidate already has an unfinished confirmation: ' + previous.dir + '; inspect it before requesting another');
  }
  const out = path.join(checks, active.id + '-' + rt.crypto.randomUUID().slice(0, 8));
  fs.mkdirSync(out);
  const candidateHash = rt.snapshot(candidate, path.join(out, 'candidate'));
  if (candidateHash !== fingerprint) throw Error('candidate changed while being frozen');
  if (active.baselineHash) {
    if (rt.snapshot(active.baseline, path.join(out, 'baseline')) !== active.baselineHash) throw Error('baseline changed');
  }
  const mapsSource = path.join(rt.ROOT, 'maps', 'online-20260927');
  rt.snapshot(mapsSource, path.join(out, 'maps'));
  const opponentHashes = {};
  for (const opp of OPPONENTS) opponentHashes[opp] = rt.snapshot(path.join(rt.ROOT, 'bots', opp), path.join(out, 'opponents', opp));
  // Sampling happens only after both source snapshots have been fixed.
  const seeds = new Set();
  while (seeds.size < 2) seeds.add(rt.crypto.randomInt(100000, 2147483647));
  const maps = fs.readdirSync(path.join(out, 'maps')).filter(f => f.endsWith('.map')).sort();
  const plan = { schema: 1, dir: out, wave: active.id, lineage: name, at: new Date().toISOString(),
    candidateHash, baselineHash: active.baselineHash, seeds: [...seeds], maps, opponentHashes,
    mapHash: rt.digest(path.join(out, 'maps')), expected: maps.length * seeds.size * OPPONENTS.length * 2 };
  rt.write(path.join(out, 'plan.json'), plan);
  let report;
  try {
    await rt.job(name, async onSpawn => {
      for (const which of active.baselineHash ? ['baseline', 'candidate'] : ['candidate']) {
        const result = await rt.command(process.execPath, [path.join(rt.ROOT, 'lineages/_tools/eval.js'),
          '--bot', path.join(out, which), '--label', name + '-' + active.id + '-' + which,
          '--out', path.join(out, which + '-results'), '--maps', path.join(out, 'maps'),
          '--opponent-root', path.join(out, 'opponents'), '--opps', OPPONENTS.join(','),
          '--seeds', plan.seeds.join(','), '--jobs', '2'], { onSpawn });
        if (result.code !== 0) throw Error(which + ' evaluator exited ' + result.code);
      }
    });
    const baseline = active.baselineHash && rows(path.join(out, 'baseline-results/rows.jsonl'), plan.expected);
    const candidateRows = rows(path.join(out, 'candidate-results/rows.jsonl'), plan.expected);
    verifyConditions(candidateRows, plan);
    if (baseline) verifyConditions(baseline, plan);
    if (rt.digest(path.join(out, 'candidate')) !== candidateHash || (active.baselineHash && rt.digest(path.join(out, 'baseline')) !== active.baselineHash)) throw Error('frozen bot sources changed');
    if (rt.digest(path.join(out, 'maps')) !== plan.mapHash || OPPONENTS.some(o => rt.digest(path.join(out, 'opponents', o)) !== opponentHashes[o])) throw Error('evaluation environment changed');
    report = { ...plan, status: 'valid', result: compare(baseline, candidateRows),
      scope: 'Listed maps and opponents, fresh seeds, both sides. This report is evidence, not an automatic promotion score.' };
  } catch (e) { report = { ...plan, status: 'invalid', error: String(e) }; }
  rt.write(path.join(out, 'report.json'), report);
  console.log(path.join(out, 'report.json'));
  if (report.status !== 'valid') throw Error(report.error);
}
if (require.main === module) check(...process.argv.slice(2)).catch(e => { console.error(e.message); process.exitCode = 1; });
module.exports = { rows, compare, verifyConditions, check };
