const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('fs'), os = require('os'), path = require('path');
const cp = require('child_process');
const source = path.resolve(__dirname, '..');
function put(root, file, contents) { const target = path.join(root, file); fs.mkdirSync(path.dirname(target), { recursive: true }); fs.writeFileSync(target, contents); }
function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'arena-loop-test-'));
  for (const file of ['runtime.js', 'runner.js', 'run-job.js', 'check.js', 'wave-prompt.md', 'activate-after-wave.js']) put(root, 'loop/' + file, fs.readFileSync(path.join(source, file)));
  put(root, '.gitignore', 'lineages/*/waves/\nlineages/*/STOP\ncontrol/\ndata/\nbin/\n');
  put(root, 'lineages/g1/bot/bot.toml', 'name = "test"\n');
  put(root, 'lineages/g1/bot/main.cpp', 'baseline\n');
  put(root, 'lineages/g1/candidate/bot.toml', 'name = "test"\n');
  put(root, 'lineages/g1/candidate/main.cpp', 'candidate\n');
  put(root, 'lineages/g1/NOTES.md', 'ready: r1 — old baseline\n');
  put(root, 'maps/online-20260927/sample.map', 'fixture map\n');
  for (const opp of ['replay_rules_v8', 'archetype_swarm', 'archetype_hunter', 'h2']) put(root, 'bots/' + opp + '/bot.toml', 'name = "opponent"\n');
  // A synthetic evaluator; this suite never launches Claude, a real game, or a server request.
  put(root, 'lineages/_tools/eval.js', `
    const fs=require('fs'),path=require('path');
    const arg=k=>process.argv[process.argv.indexOf('--'+k)+1];
    const out=arg('out'), result=[];
    fs.mkdirSync(out,{recursive:true});
    for(const opp of arg('opps').split(',')) for(const mapFile of fs.readdirSync(arg('maps'))) for(const side of ['A','B']) for(const seed of arg('seeds').split(',').map(Number)) {
      const map=mapFile.replace(/\\.map$/,''),candidate=arg('label').endsWith('candidate');
      result.push({key:[opp,map,side,seed].join(':'),opp,map,side,seed,exit:0,G:candidate?2:1,alive:true,won:candidate});
    }
    fs.writeFileSync(path.join(out,'rows.jsonl'),result.map(JSON.stringify).join('\\n')+'\\n');
  `);
  for (const args of [['init', '-q'], ['config', 'user.name', 'Loop Test'], ['config', 'user.email', 'test@localhost'], ['add', '.'], ['commit', '-qm', 'fixture']]) cp.execFileSync('git', args, { cwd: root });
  return root;
}
const env = (root, extra = {}) => ({ ...process.env, UNSW_ARENA_DATA: path.join(root, 'data'), UNSW_MAX_WAVES: '1', PATH: path.join(root, 'bin') + path.delimiter + process.env.PATH, ...extra });
function node(root, code, extra = {}) { return cp.execFileSync(process.execPath, ['-e', code], { cwd: root, env: env(root, extra), encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }); }
function fakeClaude(root, body) { put(root, 'bin/claude', '#!' + process.execPath + '\n' + body + '\n'); fs.chmodSync(path.join(root, 'bin/claude'), 0o755); }
function run(root) { return cp.spawnSync(process.execPath, ['loop/runner.js', 'run', 'g1'], { cwd: root, env: env(root), encoding: 'utf8' }); }
const read = (root, file) => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));

test('reject ends cleanly, does not export, and wave IDs survive restart', () => {
  const root = fixture();
  fakeClaude(root, `const fs=require('fs'); fs.writeFileSync('lineages/g1/CURRENT.md','No adoption.'); require(process.cwd()+'/loop/runner').finish('g1','reject','no gain');`);
  assert.equal(run(root).status, 0);
  assert.equal(read(root, 'lineages/g1/waves/last.json').outcome, 'reject');
  assert.equal(fs.existsSync(path.join(root, 'data/releases/g1-r1')), false);
  assert.equal(run(root).status, 0);
  assert.equal(read(root, 'lineages/g1/waves/active.json').id, 'w000002');
});
test('STOP does not launch a new context', () => {
  const root = fixture(); put(root, 'lineages/g1/STOP', '');
  fakeClaude(root, 'throw Error("must not run")');
  assert.equal(run(root).status, 0);
  assert.equal(fs.existsSync(path.join(root, 'lineages/g1/waves/active.json')), false);
});
test('exit zero without finish and nonzero with ready never export', () => {
  for (const code of [0, 1]) {
    const root = fixture();
    fakeClaude(root, `require('fs').appendFileSync('lineages/g1/NOTES.md','ready: r2 — not confirmed\\n'); process.exit(${code});`);
    assert.equal(run(root).status, 0);
    assert.equal(read(root, 'lineages/g1/waves/last.json').outcome, 'incomplete');
    assert.equal(fs.existsSync(path.join(root, 'data/releases')), false);
  }
});
test('unconfirmed bot mutation stops this run and blocks the next without deleting files', () => {
  const root = fixture();
  fakeClaude(root, `require('fs').writeFileSync('lineages/g1/bot/main.cpp','unconfirmed');`);
  assert.equal(run(root).status, 1);
  assert.match(run(root).stderr, /unconfirmed/);
  assert.equal(fs.readFileSync(path.join(root, 'lineages/g1/bot/main.cpp'), 'utf8'), 'unconfirmed');
  assert.equal(read(root, 'lineages/g1/waves/counter.json').n, 1);
});
test('a crash before result.json cannot silently replace the baseline on restart', () => {
  const root = fixture();
  node(root, `require('./loop/runner').begin('g1'); require('fs').writeFileSync('lineages/g1/bot/main.cpp','unfinished');`);
  fakeClaude(root, 'throw Error("must not run")');
  assert.match(run(root).stderr, /unconfirmed/);
  assert.equal(read(root, 'lineages/g1/waves/counter.json').n, 1);
});
test('confirmation freezes inputs, draws paired seeds once, and commits exact adoption', () => {
  const root = fixture();
  node(root, `
    (async()=>{
      const fs=require('fs'),path=require('path'),assert=require('assert/strict');
      const runner=require('./loop/runner'),rt=require('./loop/runtime'),check=require('./loop/check');
      const active=runner.begin('g1'); process.env.UNSW_WAVE_ID=active.id;
      await check.check('g1','lineages/g1/candidate');
      const dir=path.join(rt.lineage('g1'),'checks',fs.readdirSync('lineages/g1/checks')[0]), report=path.join(dir,'report.json');
      assert.equal(rt.read(report).status,'valid'); assert.equal(rt.read(report).expected,16);
      const seeds=rt.read(report).seeds; assert.equal(new Set(seeds).size,2); assert(seeds.every(s=>s>=100000));
      await check.check('g1','lineages/g1/candidate');
      assert.equal(fs.readdirSync('lineages/g1/checks').length,1);
      assert.throws(()=>runner.validateReport('g1',active,report),/not the confirmed candidate/);
      fs.copyFileSync('lineages/g1/candidate/main.cpp','lineages/g1/bot/main.cpp');
      fs.appendFileSync('lineages/g1/NOTES.md','ready: r2 — confirmed fixture\\n');
      fs.writeFileSync('lineages/g1/CURRENT.md','r2, synthetic evidence.');
      const result=runner.finish('g1','adopt','fixture improvement',report);
      assert.throws(()=>runner.finish('g1','adopt','duplicate',report),/already has a final/);
      assert.equal(result.version,2); assert.equal(result.commit.length,40);
      assert.equal(runner.publish('g1',active,result),'g1-r2');
      assert.equal(runner.publish('g1',active,result),'g1-r2');
      assert.equal(rt.digest(path.join(rt.DATA,'releases/g1-r2')),result.candidateHash);
      fs.appendFileSync(path.join(dir,'candidate/main.cpp'),'changed');
      assert.throws(()=>runner.publish('g1',active,result),/frozen input changed/);
    })().catch(e=>{console.error(e);process.exitCode=1});
  `);
  assert.match(cp.execFileSync('git', ['log', '-1', '--format=%s'], { cwd: root, encoding: 'utf8' }), /^g1 r2:/);
});
test('duplicate, failed, missing, and mismatched match evidence is rejected', () => {
  const root = fixture();
  node(root, `
    const fs=require('fs'),assert=require('assert/strict'),{rows,compare,verifyConditions}=require('./loop/check');
    const row={key:'o:m:A:100001',opp:'o',map:'m',side:'A',seed:100001,exit:0,G:1,won:true,alive:true};
    const write=items=>fs.writeFileSync('rows.jsonl',items.map(JSON.stringify).join('\\n')+'\\n');
    for(const items of [[row,row],[{...row,exit:1}],[{...row,error:'missing replay'}],[{...row,botProblem:'timed out'}],[]]) {
      write(items); assert.throws(()=>rows('rows.jsonl',1));
    }
    write([row]); const r=rows('rows.jsonl',1);
    assert.throws(()=>compare(new Map([['other',row]]),r),/unpaired/);
    assert.throws(()=>verifyConditions(r,{maps:['m.map'],seeds:[100001],opponentHashes:{o:'hash'},expected:2}),/conditions/);
  `);
});
test('shared queue serializes batches and duplicate runner is refused', async () => {
  const root = fixture();
  node(root, `const r=require('./loop/runner');r.begin('g1');`);
  put(root, 'data/control/locks/local-evaluation/owner.json', JSON.stringify({ pid: 999999, token: 'dead-owner' }));
  const code = `
    const rt=require('./loop/runtime');
    rt.job('g1',async()=>{const fs=require('fs'); fs.appendFileSync('order.log','start '+process.pid+'\\n');await rt.sleep(250);fs.appendFileSync('order.log','end '+process.pid+'\\n');}).catch(e=>{console.error(e);process.exitCode=1});
  `;
  const spawn = script => new Promise((resolve, reject) => {
    const p = cp.spawn(process.execPath, ['-e', script], { cwd: root, env: env(root, { UNSW_WAVE_ID: 'w000001' }) });
    let err='';p.stderr.on('data',d=>err+=d);p.on('error',reject);p.on('exit',c=>c?reject(Error(err)):resolve());
  });
  await Promise.all([spawn(code), spawn(code)]);
  assert.deepEqual(fs.readFileSync(path.join(root, 'order.log'), 'utf8').trim().split('\n').map(l=>l.split(' ')[0]), ['start','end','start','end']);
  node(root, `(async()=>{ const rt=require('./loop/runtime'),assert=require('assert/strict'); const l=await rt.lock('runner-g1',{wait:false}); await assert.rejects(()=>rt.lock('runner-g1',{wait:false}),/another runner/);l.release(); })().catch(e=>{console.error(e);process.exitCode=1});`);
});
test('finish cannot race an active registered job', () => {
  const root = fixture();
  node(root, `
    const rt=require('./loop/runtime'),runner=require('./loop/runner'),assert=require('assert/strict');
    const a=runner.begin('g1');process.env.UNSW_WAVE_ID=a.id;
    rt.fs.writeFileSync('lineages/g1/CURRENT.md','waiting');
    rt.write(rt.path.join(rt.DATA,'control/jobs/test.json'),{root:rt.ROOT,lineage:'g1',status:'running',pid:process.pid});
    assert.throws(()=>runner.finish('g1','reject','not yet'),/wait for registered/);
  `);
});
test('boundary deployment applies only frozen common files and preserves bot and user edits', () => {
  const root = fixture();
  node(root, `
    const fs=require('fs'),path=require('path'),cp=require('child_process'),assert=require('assert/strict');
    const h=require('./loop/activate-after-wave');
    const stop=path.resolve('lineages/g1/STOP'),token='owned transition\\n';fs.writeFileSync(stop,token);
    const stat=fs.statSync(stop),dir=path.resolve('data/handoff');fs.mkdirSync(dir,{recursive:true});
    const original=cp.execFileSync('/usr/bin/which',['apply_patch'],{encoding:'utf8'}).trim();
    const applyPatch=path.join(dir,'apply_patch');fs.symlinkSync(fs.realpathSync(original),applyPatch);
    fs.writeFileSync('operator.md','before\\n');fs.writeFileSync('unrelated-user.txt','preserve me');
    const plan={root:process.cwd(),stop,token,stopIno:stat.ino,stopMtime:stat.mtimeMs,applyPatch,revision:'testrevision',
      files:[{path:'operator.md',before:h.hash('operator.md'),content:'after\\n'},{path:'new-common.md',before:null,content:'new\\n'}]};
    assert(h.ownsStop(plan));const commit=h.deploy(plan);assert.equal(commit.length,40);
    assert.equal(fs.readFileSync('operator.md','utf8'),'after\\n');assert.equal(fs.readFileSync('new-common.md','utf8'),'new\\n');
    assert.equal(fs.readFileSync('lineages/g1/bot/main.cpp','utf8'),'baseline\\n');assert.equal(fs.readFileSync('unrelated-user.txt','utf8'),'preserve me');
    assert.throws(()=>h.deploy(plan),/changed since scheduling/);
    fs.utimesSync(stop,new Date(),new Date(stat.mtimeMs+1000));assert.equal(h.ownsStop(plan),false);
    assert.throws(()=>h.deploy(plan),/STOP changed/);
  `);
});
test('boundary detector sees a remaining evaluation in the target worktree', async () => {
  const root = fixture();
  const child = cp.spawn(process.execPath, ['-e', 'setTimeout(()=>{},10000)', 'eval.js'], { cwd: root, stdio: 'ignore' });
  await new Promise((resolve, reject) => { child.once('spawn', resolve); child.once('error', reject); });
  try { node(root, `const h=require('./loop/activate-after-wave');require('assert/strict')(h.busy(process.cwd()).includes(${child.pid}));`); }
  finally { child.kill('SIGTERM'); await new Promise(resolve => child.once('exit', resolve)); }
});
