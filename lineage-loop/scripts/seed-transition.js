#!/usr/bin/env node
// Operator-authorized one-time migration: finish g1/g2, establish seed0,
// then start g3/g4 from the identical confirmed seed. No server requests.
const fs = require('fs');
const path = require('path');
const cp = require('child_process');
const ROOT = path.resolve(__dirname, '..');
const PARENT = path.dirname(ROOT);
const SEED = path.join(PARENT, 'unsw-arena-seed');
const DATA = '~/01. Project/개인 프로젝트/unsw-arena-data';
const OLD = [
  {name:'g1', root:'~/orca/workspaces/unsw-arena/taimen'},
  {name:'g2', root:'~/orca/workspaces/unsw-arena/prowfish'},
];
const NEW = ['g3', 'g4'].map(name => ({name, root:path.join('~/orca/workspaces/unsw-arena', name), branch:'lineage-' + name + '-clean'}));
const WORK = path.join(DATA, 'control', 'seed-transition-20260928');
const STATE = path.join(WORK, 'state.json');
const ONLINE = path.join(ROOT, 'lineages/seed0/checks/seed0-mold-20260928-040652');
const read = f => JSON.parse(fs.readFileSync(f, 'utf8'));
const exists = f => fs.existsSync(f);
const now = () => new Date().toISOString();
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const rt = root => require(path.join(root, 'loop/runtime.js'));
const runner = root => require(path.join(root, 'loop/runner.js'));
const live = pid => rt(ROOT).alive(pid);
function write(file, body) { fs.mkdirSync(path.dirname(file), {recursive:true}); fs.writeFileSync(file, body); }
function git(root, args) { return cp.execFileSync('git', args, {cwd:root, encoding:'utf8'}).trim(); }
function persist(state, stage, extra={}) {
  Object.assign(state, extra, {stage, updated:now()});
  rt(ROOT).write(STATE, state);
  console.log(JSON.stringify({at:now(), stage, ...extra}));
}
function owner(name) {
  const control=['g3','g4'].includes(name)?require('./clean-lineages').CONTROL:path.join(DATA,'control');
  const f = path.join(control, 'locks', 'runner-' + name, 'owner.json');
  return exists(f) ? read(f) : null;
}
function running(name) { const o=owner(name); return !!o && (live(o.pid) || (o.childPid && live(o.childPid))); }
function activeJobs(name, root) {
  const control=['g3','g4'].includes(name)?require('./clean-lineages').CONTROL:path.join(DATA,'control');
  const dir=path.join(control,'jobs');
  if(!exists(dir))return [];
  return fs.readdirSync(dir).filter(f=>f.endsWith('.json')).map(f=>read(path.join(dir,f)))
    .filter(j=>j.lineage===name&&j.root.normalize('NFD')===root.normalize('NFD')&&['running','queued'].includes(j.status)&&(live(j.pid)||(j.childPid&&live(j.childPid))));
}
function requireStopped(name, root) {
  if (running(name) || activeJobs(name, root).length) throw Error(name + ' is still running');
}
async function stopNow() {
  // Explicit user request: interrupt the legacy waves and their evaluations.
  // Preserve files; only terminate process trees recorded as belonging to g1/g2.
  const lines=cp.execFileSync('/bin/ps',['-axo','pid=,ppid=,command='],{encoding:'utf8'}).trim().split('\n');
  const processes=new Map(lines.map(line=>{
    const m=line.trim().match(/^(\d+)\s+(\d+)\s+(.*)$/);
    return m?[Number(m[1]),{pid:Number(m[1]),ppid:Number(m[2]),command:m[3]}]:null;
  }).filter(Boolean));
  const roots=new Set();
  for(const {name,root} of OLD){
    const o=owner(name);
    if(o && o.root===root && processes.get(o.pid)?.command.includes('runner.js run '+name)) roots.add(o.pid);
    for(const j of rt(root).jobs(name)){
      const p=processes.get(j.pid);
      if(p && /(?:run-job\.js|check\.js)/.test(p.command) && p.command.includes(name)) roots.add(j.pid);
    }
  }
  const targets=new Set(roots);
  let grew=true;
  while(grew){grew=false;for(const p of processes.values())if(targets.has(p.ppid)&&!targets.has(p.pid)){targets.add(p.pid);grew=true;}}
  if(targets.has(process.pid)) throw Error('Refusing to terminate the operator');
  const record={at:now(),reason:'User explicitly requested forced stop of legacy waves',processes:[...targets].map(pid=>processes.get(pid))};
  fs.mkdirSync(WORK,{recursive:true});rt(ROOT).write(path.join(WORK,'forced-stop.json'),record);
  for(const pid of [...targets].reverse()) try{process.kill(pid,'SIGTERM');}catch(e){if(e.code!=='ESRCH')throw e;}
  await pause(4000);
  for(const pid of [...targets].reverse()) if(live(pid)) try{process.kill(pid,'SIGKILL');}catch(e){if(e.code!=='ESRCH')throw e;}
  await pause(1500);
  for(const {name,root} of OLD){
    const r=rt(root),dir=path.join(root,'lineages',name),waves=path.join(dir,'waves');
    if(activeJobs(name,root).length||running(name)) throw Error('Legacy processes remain: '+name);
    await r.drain(name);
    const active=read(path.join(waves,'active.json'));
    const lastFile=path.join(waves,'last.json');
    const before=exists(lastFile)?read(lastFile):null;
    const completed=before?.wave===active.id && exists(path.join(active.work,'finish.json'));
    if(!completed){
      const result={wave:active.id,outcome:'incomplete',reason:'사용자 요청으로 기존 계통 강제 종료. 중단된 탐색·평가를 완료나 성능 개선으로 세지 않음.',exit:143,at:now()};
      if(before)r.write(path.join(active.work,'result-before-forced-stop.json'),before);
      r.write(path.join(active.work,'result.json'),result);r.write(lastFile,result);
      fs.appendFileSync(path.join(waves,'index.log'),now()+' operator forced stop; incomplete\n');
      const current=path.join(dir,'CURRENT.md');
      let body=exists(current)?fs.readFileSync(current,'utf8'):`# ${name} CURRENT\n\n- 현재 보존 버전: r${active.ready}, 웨이브 시작 기준선. 상세 이력 NOTES.md.\n`;
      const intact=active.baselineHash===r.digest(path.join(dir,'bot'));
      body+=`\n## 강제 종료 인계 (${now()})\n- 웨이브 ${active.id}: 사용자 요청으로 강제 종료, 미완료. 모든 파일과 원자료를 보존.\n- bot/가 웨이브 시작 코드와 ${intact?'일치':'불일치(미확인 변경 보존)'}함. 종료 후 후보를 승격하지 않음.\n- 진행 중 실험에 대한 앞선 설명은 중단 전 상태이며, 완료되지 않은 평가 결과로 채택하지 않는다.\n`;
      write(current,body);
    }
  }
  console.log(JSON.stringify({stopped:[...targets],record:path.join(WORK,'forced-stop.json')}));
}
async function pauseClean() {
  const state=read(STATE);
  if(state.stage!=='pause-requested')throw Error('Request clean-lineage STOP first');
  const table=()=>new Map(cp.execFileSync('/bin/ps',['-axo','pid=,ppid=,command='],{encoding:'utf8'}).trim().split('\n').flatMap(line=>{
    const m=line.trim().match(/^(\d+)\s+(\d+)\s+(.*)$/);
    return m?[[+m[1],{pid:+m[1],ppid:+m[2],command:m[3]}]]:[];
  }));
  const processes=table(),targets=new Set(),roots=new Set(),before=[];
  for(const item of NEW){
    if(!exists(path.join(item.root,'lineages',item.name,'STOP')))throw Error('Missing STOP: '+item.name);
    const o=owner(item.name),jobs=rt(item.root).jobs(item.name);
    if(o&&live(o.pid)){
      if(o.root.normalize('NFD')!==item.root.normalize('NFD')||!processes.get(o.pid)?.command.normalize('NFD').includes(path.join(item.root,'loop/runner.js').normalize('NFD')+' run '+item.name))throw Error('Unexpected runner owner: '+item.name);
      roots.add(o.pid);targets.add(o.pid);
    }
    for(const j of jobs)if(live(j.pid)){
      const command=processes.get(j.pid)?.command||'';
      if(!/(?:run-job\.js|check\.js)/.test(command)||!command.includes(item.name))throw Error('Unexpected evaluation owner');
      targets.add(j.pid);
    }
    before.push({...item,owner:o,jobs,active:read(path.join(item.root,'lineages',item.name,'waves/active.json'))});
  }
  let grew=true;
  while(grew){grew=false;for(const p of processes.values())if(targets.has(p.ppid)&&!targets.has(p.pid)){targets.add(p.pid);grew=true;}}
  if(targets.has(process.pid))throw Error('Operator appears in research process tree');
  rt(ROOT).write(path.join(WORK,'clean-pause-processes.json'),{at:now(),before,processes:[...targets].map(pid=>processes.get(pid))});
  const signal=(pid,sig)=>{try{process.kill(pid,sig);}catch(e){if(e.code!=='ESRCH')throw e;}};
  // Let the managed runners drain jobs, record incomplete work and commit it.
  for(const pid of roots)signal(pid,'SIGINT');
  for(const pid of targets)if(!roots.has(pid))signal(pid,'SIGTERM');
  await pause(3000);
  const after=table();
  for(const pid of targets)if(!roots.has(pid)&&live(pid)&&after.get(pid)?.command===processes.get(pid)?.command)signal(pid,'SIGKILL');
  for(let i=0;i<12&&[...targets].some(live);i++)await pause(2000);
  if([...targets].some(live))throw Error('Research processes remain; inspect before claiming stopped');
  const paused=[];
  for(const item of before){
    const r=rt(item.root),dir=path.join(item.root,'lineages',item.name);
    await r.drain(item.name);requireStopped(item.name,item.root);
    const active=read(path.join(dir,'waves/active.json')),last=read(path.join(dir,'waves/last.json'));
    if(active.id!==item.active.id||last.wave!==active.id)throw Error('Unexpected pause boundary: '+item.name);
    const botHash=r.digest(path.join(dir,'bot')),intact=botHash===active.baselineHash,evaluations=[];
    function walk(base){for(const e of fs.readdirSync(base,{withFileTypes:true})){
      if(e.isDirectory()&&!['games','waves','logs','bot','baseline','candidate','opponents','maps','.unswbc-build','build'].includes(e.name))walk(path.join(base,e.name));
      if(e.isFile()&&e.name==='rows.jsonl'){
        const f=path.join(base,e.name),data=fs.readFileSync(f),lines=data.toString().split('\n').filter(Boolean),rows=[];let malformed=0;
        for(const line of lines){try{rows.push(JSON.parse(line));}catch{malformed++;}}
        evaluations.push({path:path.relative(dir,f),rows:rows.length,errors:rows.filter(x=>x.error||x.botProblem||x.exit!==0).length,malformed,sha256:r.crypto.createHash('sha256').update(data).digest('hex')});
      }
    }}
    walk(dir);
    const checkpoint={at:now(),reason:'User requested resumable pause',wave:active.id,last,baselineIntact:intact,botHash,version:r.ready(dir),
      runnerStopped:true,evaluationJobsStopped:true,priorJobs:item.jobs,transcript:'waves/'+active.id+'.jsonl',evaluations};
    r.write(path.join(dir,'PAUSED.json'),checkpoint);
    const resume=`# ${item.name} 재개 기록\n\n- 사용자 요청으로 ${checkpoint.at}에 중지. STOP 유지. 중단 웨이브: ${active.id}, 실제 종료 ${last.exit}, 결과 ${last.outcome}.\n- bot/: r${checkpoint.version}, 시작 기준선과 ${intact?'동일':'다름 — 재시작 전에 확인 필요'}. SHA256 ${botHash}. 자동 되돌림·초기화 없음.\n- 이 웨이브의 진행 중 실험은 미완료이며 채택·개선으로 취급하지 않는다. 마지막 CURRENT.md의 '진행 중 없음'은 중단 웨이브 시작 전 상태일 수 있다.\n- 재개 시 NOTES.md의 최근 실험과 \`${checkpoint.transcript}\`의 마지막 작업부터 확인한다. 후보·분석 도구·원자료는 같은 폴더에 보존했다. 작업 목록과 결과 행 수·해시는 PAUSED.json에 있다.\n- 미완료 평가는 기존 코드·지도·상대·시드를 유지하고, 이미 완료한 결과를 보존한 채 누락된 조건만 이어간다. 실패 행이 있으면 원본을 보존해 별도로 조사하며 정상 결과로 세지 않는다. 확인 계획을 다시 추첨하지 않는다.\n- 모든 평가는 공통 큐를 사용한다. 재개는 STOP 해제 후 이 저장소의 .isolation/launch.sh로 실행하며, 기존 웨이브를 초기화하거나 덮어쓰지 않는다.\n`;
    write(path.join(dir,'RESUME.md'),resume);
    fs.appendFileSync(path.join(dir,'CURRENT.md'),`\n## 사용자 요청 일시 중지 (${checkpoint.at})\n- ${active.id} 중지, r${checkpoint.version} 보존. 재개 전 RESUME.md 및 PAUSED.json부터 확인한다.\n`);
    r.commit(item.name,item.name+': preserve work for user-requested pause');
    paused.push({name:item.name,root:item.root,wave:active.id,outcome:last.outcome,exit:last.exit,version:checkpoint.version,baselineIntact:intact,
      botHash,commit:git(item.root,['rev-parse','HEAD']),resume:path.join(dir,'RESUME.md'),checkpoint:path.join(dir,'PAUSED.json'),errorRows:evaluations.reduce((n,x)=>n+x.errors+x.malformed,0)});
  }
  persist(state,'paused',{pause:{...state.pause,completedAt:now(),lineages:paused}});report(state);
}
async function resumePaused() {
  const state=read(STATE);
  if(state.stage!=='paused'||!state.pause?.lineages||!state.migration?.worktrees)
    throw Error('Record and verify migrated worktrees before resuming');
  const prepared=[];
  for(const item of NEW){
    requireStopped(item.name,item.root);
    const dir=path.join(item.root,'lineages',item.name),stop=path.join(dir,'STOP');
    if(!exists(stop))throw Error('STOP missing before coordinated resume: '+item.name);
    const saved=state.pause.lineages.find(x=>x.name===item.name),checkpoint=read(path.join(dir,'PAUSED.json'));
    const active=read(path.join(dir,'waves/active.json')),last=read(path.join(dir,'waves/last.json'));
    const r=rt(item.root);
    if(!saved||!checkpoint.baselineIntact||checkpoint.botHash!==saved.botHash||
       r.digest(path.join(dir,'bot'))!==saved.botHash||active.baselineHash!==saved.botHash||
       active.id!==checkpoint.wave||last.wave!==checkpoint.wave||last.outcome!=='incomplete'||
       git(item.root,['rev-parse','HEAD'])!==state.migration.worktrees[item.name]?.head||r.jobs(item.name).length)
      throw Error('Paused code, wave or Git checkpoint changed: '+item.name);
    for(const row of checkpoint.evaluations){
      const file=path.join(dir,row.path),hash=r.crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
      if(hash!==row.sha256)throw Error('Paused result changed: '+item.name+'/'+row.path);
    }
    prepared.push({item,stop,priorWave:active.id});
  }
  for(const x of prepared)fs.unlinkSync(x.stop);
  const continuous={...state.continuous};
  try{
    for(const {item} of prepared){const launched=launch(item.root,item.name,null,true);continuous[item.name]={pid:launched.pid,log:launched.log};}
    persist(state,'resuming',{continuous,resume:{requestedAt:now(),from:prepared.map(x=>({name:x.item.name,wave:x.priorWave}))}});report(state);
    for(let i=0;i<45;i++){
      const all=prepared.every(({item,priorWave})=>{
        const f=path.join(item.root,'lineages',item.name,'waves/active.json');
        if(!running(item.name)||!exists(f)||read(f).id===priorWave)return false;
        const active=read(f),events=path.join(item.root,'lineages',item.name,'waves',active.id+'.jsonl');
        if(!exists(events))return false;
        const init=fs.readFileSync(events,'utf8').split('\n').filter(Boolean).flatMap(line=>{try{return[JSON.parse(line)];}catch{return[];}})
          .find(x=>x.type==='system'&&x.subtype==='init');
        if(!init)return false;
        if(init.cwd.normalize('NFD')!==item.root.normalize('NFD')||init.skills?.length||init.mcp_servers?.length||
           init.plugins?.some(p=>p.path!=='builtin'||!['agents-md','telemetry'].includes(p.name)))
          throw Error('New client is not isolated: '+item.name);
        return true;
      });
      if(all){persist(state,'continuous-running',{resume:{...state.resume,startedAt:now(),waves:prepared.map(({item})=>({name:item.name,wave:read(path.join(item.root,'lineages',item.name,'waves/active.json')).id}))}});report(state);return;}
      await pause(2000);
    }
    throw Error('Clean runners did not start isolated new waves');
  }catch(e){for(const x of prepared)if(!exists(x.stop))write(x.stop,now()+' resume requires review\n');
    persist(state,'needs-review',{error:String(e.stack||e)});report(state);throw e;}
}
function recordWorktreeMigration() {
  const state=read(STATE);
  if(state.stage!=='paused'||!state.pause?.lineages)throw Error('Expected verified paused state');
  const verify=require('./verify-orca-worktrees').verify, worktrees={};
  for(const item of NEW){
    requireStopped(item.name,item.root);
    const result=verify(item.name,false), saved=state.pause.lineages.find(x=>x.name===item.name);
    if(!saved||result.botHash!==saved.botHash)throw Error('Migrated bot does not match pause: '+item.name);
    worktrees[item.name]=result;
  }
  state.newLineages=state.newLineages.map(x=>{
    const moved=worktrees[x.name];
    return moved?{...x,root:moved.target,branch:moved.branch,independentRepository:false,worktree:true}:x;
  });
  persist(state,'paused',{migration:{recordedAt:now(),worktrees}});
  report(state);
}
function handoff() {
  const s=read(STATE);
  if(s.stage!=='seed-baseline-running') throw Error('Supervisor handoff requires the seed stage');
  for(const item of NEW) if(exists(item.root)) throw Error('New lineage already exists; inspect before handoff');
  const p=s.operatorPid;
  const command=cp.execFileSync('/bin/ps',['-p',String(p),'-o','command='],{encoding:'utf8'}).trim();
  if(!command.includes('seed-transition.js run')) throw Error('Unexpected supervisor process');
  persist(s,'handoff-awaiting-seed',{handoffReason:'User requires independently initialized clean repositories; seed subprocess continues unchanged.'});
  process.kill(p,'SIGTERM');
  report(s);
}
function status() {
  const s=exists(STATE)?read(STATE):{stage:'not-started'};
  const states=[...OLD, {name:'seed0',root:SEED}, ...NEW].map(({name,root})=>{
    const waves=path.join(root,'lineages',name,'waves');
    const o=owner(name), last=path.join(waves,'last.json'), active=path.join(waves,'active.json');
    const pending=exists(path.join(root,'loop/runtime.js'))?activeJobs(name,root):[];
    return {name,root,running:running(name),owner:o,last:exists(last)?read(last):null,
      active:exists(active)?read(active).id:null,stop:exists(path.join(root,'lineages',name,'STOP')),
      jobs:pending.map(({pid,childPid,status,wave})=>({pid,childPid,status,wave}))};
  });
  console.log(JSON.stringify({state:s,lineages:states},null,2));
}
function briefStatus(){
  const state=read(STATE),lineages=[];
  for(const item of NEW){
    const dir=path.join(item.root,'lineages',item.name),evaluations=[];
    function walk(base){
      if(!exists(base))return;
      for(const e of fs.readdirSync(base,{withFileTypes:true})){
        if(e.isDirectory()&&!['games','waves','logs','bot','baseline','candidate','opponents','maps'].includes(e.name))walk(path.join(base,e.name));
        if(e.isFile()&&e.name==='rows.jsonl'){
          const file=path.join(base,e.name),rows=fs.readFileSync(file,'utf8').split('\n').filter(Boolean).flatMap(l=>{try{return[JSON.parse(l)];}catch{return[];}});
          evaluations.push({path:path.relative(dir,file),n:rows.length,errors:rows.filter(r=>r.error||r.botProblem||r.exit!==0).length});
        }
      }
    }
    walk(dir);
    const f=path.join(dir,'waves/last.json');
    lineages.push({name:item.name,running:running(item.name),last:exists(f)?read(f):null,
      jobs:activeJobs(item.name,item.root).map(j=>j.status),evaluations});
  }
  console.log(JSON.stringify({at:now(),stage:state.stage,lineages},null,2));
}
function archiveOld(item) {
  const {name,root}=item;
  requireStopped(name,root);
  const dir=path.join(root,'lineages',name), waves=path.join(dir,'waves');
  const active=read(path.join(waves,'active.json'));
  const forced=path.join(WORK,'forced-stop.json');
  const previous=path.join(active.work,'result-before-forced-stop.json');
  if(exists(forced)&&exists(previous)&&!read(forced).processes.some(p=>p.command.includes('runner.js run '+name))){
    // A lineage already stopped before the forced termination must retain its
    // actual runner exit code and timestamp, not be described as signal-killed.
    const original=read(previous);
    rt(root).write(path.join(waves,'last.json'),original);
    rt(root).write(path.join(active.work,'result.json'),original);
    fs.appendFileSync(path.join(dir,'CURRENT.md'),'\n- 정정: 이 계통의 실행기는 강제 종료 명령 전에 이미 종료되어 있었다. 마지막 실제 실행 결과와 exit 코드는 waves/last.json에 그대로 복원했으며, 추가 실행을 막고 보존한 상태다.\n');
  }
  const last=read(path.join(waves,'last.json'));
  if(last.wave!==active.id) throw Error(name+' has no final record for its last wave');
  const current=path.join(dir,'CURRENT.md');
  if(!exists(current)) throw Error(name+' needs a CURRENT.md before archiving');
  const mark='<!-- seed-transition-20260928 -->';
  const tail=`\n${mark}\n- 운영 중지: ${now()}. 사용자 요청으로 현재 웨이브와 등록된 평가가 끝난 뒤 종료. 기존 봇·실험·커밋 보존. 새 연구는 공통 seed0 기준선에서 파생한 g3/g4에서 진행.\n`;
  for(const f of [current,path.join(dir,'NOTES.md')]) if(!fs.readFileSync(f,'utf8').includes(mark)) fs.appendFileSync(f,tail);
  git(root,['add','--','lineages/'+name+'/CURRENT.md','lineages/'+name+'/NOTES.md']);
  if(git(root,['diff','--cached','--name-only','--','lineages/'+name]))
    git(root,['commit','-m',name+': preserve final state before shared-seed transition','--','lineages/'+name+'/CURRENT.md','lineages/'+name+'/NOTES.md']);
  return {name,root,last,commit:git(root,['rev-parse','HEAD']),botHash:rt(root).digest(path.join(dir,'bot'))};
}
function prepareSeed() {
  requireStopped('seed0',SEED);
  const dir=path.join(SEED,'lineages/seed0');
  const m=read(path.join(ONLINE,'manifest.json'));
  const got=rt(SEED).hashes(path.join(dir,'candidate'));
  if(JSON.stringify(Object.entries(got).sort())!==JSON.stringify(Object.entries(m.files).sort()))
    throw Error('Seed candidate differs from uploaded mold; review source before proceeding');
  const onlineTarget=path.join(dir,'checks/server-20260928');
  if(!exists(onlineTarget)) fs.cpSync(ONLINE,onlineTarget,{recursive:true});
  const prior=path.join(dir,'PRE_BASELINE_CURRENT.md');
  if(!exists(prior)) fs.copyFileSync(path.join(dir,'CURRENT.md'),prior);
  const notes=path.join(dir,'NOTES.md'), mark='<!-- initial-confirmation-20260928 -->';
  if(!fs.readFileSync(notes,'utf8').includes(mark)) fs.appendFileSync(notes,
    `\n${mark}\n## 운영자 요청: 공통 거푸집 초기 확인\n후보는 서버 제출 #9109(v22)와 파일별 SHA256이 같다. 공식 서버에서 500라운드 1판 정상 완료, CPU 한도 초과 0회. 상세 근거 checks/server-20260928/REPORT.md. 이 온라인 결과는 로컬 초기 확인을 대체하지 않는다. 이번 웨이브는 후보를 그대로 고정해 초기 기준선을 확인한다. 성능 향상 주장이 아니며, 코드를 튜닝하지 않는다.\n`);
  write(path.join(dir,'CURRENT.md'),`# seed0 초기 기준선 확정\n\n- 현재 bot/: 없음. candidate/는 사용자 승인 거푸집이며 서버 #9109와 동일하다. 변경하지 않는다.\n- 이번 단일 웨이브의 작업: CLAUDE.md 순서로 규칙과 기록을 읽고, 필요하면 공통 큐로 공식 엔진 스모크를 실행한 뒤 node loop/check.js seed0 lineages/seed0/candidate 로 초기 160판 확인을 완료한다.\n- 새 가설 탐색이나 수치 튜닝을 시작하지 않는다. 실행·프로토콜 오류가 있으면 원인을 기록하고 bot/ 없이 incomplete로 끝내라. 같은 후보의 확인 시드를 다시 뽑지 않는다.\n- 확인이 valid이면 원자료와 지도·진영·상대별 결과를 검토한다. 초기 기준선이므로 승률 임계값이나 개선을 요구하지 않는다. 정상 실행되고 기준선으로 쓸 수 있으면 고정된 후보 그대로 bot/에 반영하고 NOTES.md에 ready: r1(초기 기준선, 성능 개선 아님)을 기록한다. LOOP.md의 finish adopt로 종료한다.\n- CURRENT.md에 초기 성적, 실제 오류 수, 미검증 가정, 근거 경로를 남긴다. 해당 상태를 운영자가 같은 코드에서 g3/g4를 파생하는 데 쓴다.\n- 온라인 실행 근거: checks/server-20260928/REPORT.md. 과거 상태: PRE_BASELINE_CURRENT.md.\n`);
}
function launch(root,name,maxWaves,detached=false) {
  requireStopped(name,root);
  const stop=path.join(root,'lineages',name,'STOP');
  if(exists(stop)) throw Error('STOP present: '+stop);
  const waves=path.join(root,'lineages',name,'waves');fs.mkdirSync(waves,{recursive:true});
  const log=path.join(waves,maxWaves?'initial-runner.log':'runner.log');
  const fd=fs.openSync(log,'a');
  const env={...process.env,UNSW_ARENA_DATA:DATA};
  delete env.UNSW_WAVE_ID; delete env.UNSW_LINEAGE; delete env.UNSW_MAX_WAVES;
  if(maxWaves) env.UNSW_MAX_WAVES=String(maxWaves);
  const config=['g3','g4'].includes(name)?require('./clean-lineages').launchConfig(root):
    {command:'/usr/bin/caffeinate',args:['-i',process.execPath,path.join(root,'loop/runner.js')],env:{}};
  Object.assign(env,config.env);
  const child=cp.spawn(config.command,[...config.args,'run',name],
    {cwd:root,env,detached:true,stdio:['ignore',fd,fd]});
  fs.closeSync(fd);
  const result=new Promise((resolve,reject)=>{child.once('error',reject);child.once('exit',(code,signal)=>resolve({code,signal}));});
  if(detached) child.unref();
  return {pid:child.pid,log,result};
}
function verifyWave(root,name,{seed=false}={}) {
  requireStopped(name,root);
  const r=rt(root), dir=path.join(root,'lineages',name), waves=path.join(dir,'waves');
  const last=read(path.join(waves,'last.json')), active=read(path.join(waves,'active.json'));
  const finish=read(path.join(active.work,'finish.json'));
  if(last.wave!==active.id || finish.wave!==active.id || last.exit!==0 || last.outcome!==finish.outcome)
    throw Error(name+' first wave did not end with a successful explicit finish');
  let evidence=null;
  if(last.outcome==='adopt') evidence=runner(root).validateReport(name,active,last.report);
  else if(active.baselineHash!==r.digest(path.join(dir,'bot'))) throw Error(name+' changed best without adoption');
  if(seed){
    if(last.outcome!=='adopt' || last.version!==1 || evidence.expected!==160 || evidence.baselineHash!==null)
      throw Error('Seed did not establish a valid 160-game initial baseline');
    if(r.digest(path.join(dir,'bot'))!==r.digest(path.join(dir,'candidate'))) throw Error('Seed code changed');
  }
  return {last,active,evidence,botHash:r.digest(path.join(dir,'bot')),commit:git(root,['rev-parse','HEAD'])};
}
function provision(item,baseline) { return require('./clean-lineages').provision(item,baseline); }
function report(state) {
  const file=path.join(ROOT,'lineages/seed0/TRANSITION.md');
  const body=['# 공통 거푸집 전환 — 2026-09-28','',`상태: ${state.stage}; 갱신: ${state.updated}`,'',
    '## 기존 계통','',...(state.archived||[]).map(x=>`- ${x.name}: 종료·보존. 마지막 ${x.last.wave} / ${x.last.outcome}, commit ${x.commit}. STOP 유지.`),'',
    ...(state.archives||[]).map(x=>`- 독립 아카이브 ${x.name}: ${x.path}`),'',
    '## 공통 기준선','',state.baseline?`- seed0 r1: ${state.baseline.botHash}; 근거 ${state.baseline.last.report}.`:'- 아직 확인 중.','',
    '## 새 계통','',...(state.newLineages||[]).map(x=>`- ${x.name}: ${x.root}; 초기 해시 ${x.initialHash}.`),'',
    ...(state.isolation||[]).map(x=>`- ${x.name} 최초 독립 저장소 격리 검사: ${x.passed?'통과':'실패'} (${x.checks}개).`),'',
    ...(Object.values(state.migration?.worktrees||{}).map(x=>`- ${x.name} Orca 하위 워크트리: ${x.target}, ${x.branch}, 이관 커밋 ${x.head}; 중단 시점 봇 ${x.botHash}, 평가 원자료 ${x.rows}개 해시 검증. 이전 독립 저장소 삭제.`)),'',
    '## 첫 웨이브','',...(state.newLineages||[]).map(({name:n})=>{const x=state.firstWaves?.[n];return x?`- ${n}: ${x.last.wave}, ${x.last.outcome}, exit ${x.last.exit}, commit ${x.commit}.${x.last.report?' 확인 근거: '+x.last.report+'.':''}`:`- ${n}: 첫 웨이브 종료·검증 대기.`;}),'',
    '## 연속 실행','',...Object.entries(state.continuous||{}).map(([n,x])=>`- ${n}: ${state.stage==='paused'?'중지됨 (이전 PID '+x.pid+')':'PID '+x.pid}, 로그 ${x.log}.`),'',
    ...(state.pause?.lineages||[]).map(x=>{
      const moved=state.migration?.worktrees?.[x.name];
      const resume=moved?path.join(moved.target,'lineages',x.name,'RESUME.md'):x.resume;
      return `- ${x.name} 지난 중단 기록: ${resume}; r${x.version}, ${x.wave} 미완료, 당시 commit ${x.commit}.`;
    }),
    ...(state.resume?.waves||[]).map(x=>`- ${x.name} 재개 웨이브: ${x.wave}.`),'',
    '각 계통은 자기 첫 웨이브의 검증이 끝나면 독립적으로 연속 실행을 시작한다. 결과·캐시·배포 사본은 각 저장소에만 저장하며, 기존 서버 제출 데몬과 연결하지 않았다.','',
    '중지는 해당 저장소에서 touch lineages/<이름>/STOP. 현재 웨이브와 등록된 평가가 끝난 뒤 종료한다.','',
    '격리·아카이브·초기 기준선의 검증 근거: CLEAN_START_VALIDATION.md.','',
    `운영 상태 파일: ${STATE}`,''];
  write(file,body.join('\n'));
}
async function afterBaseline(state,baseline){
  const clean=require('./clean-lineages');
  persist(state,'seed-baseline-verified',{baseline});report(state);
  const newLineages=NEW.map(x=>provision(x,baseline));
  if(newLineages.some(x=>x.initialHash!==baseline.botHash))throw Error('New lineages differ at start');
  const isolation=clean.verifyIsolation(newLineages);
  persist(state,'new-lineages-created',{newLineages,isolation});report(state);
  await startNewWaves(state,newLineages);
}
async function startNewWaves(state,newLineages){
  const firstRuns=newLineages.map(x=>({...x,...launch(x.root,x.name,1)}));
  persist(state,'first-waves-running',{firstRuns:firstRuns.map(({name,pid,log})=>({name,pid,log}))});report(state);
  const firstExits=await Promise.all(firstRuns.map(async x=>({name:x.name,...await x.result})));
  if(firstExits.some(x=>x.code!==0))throw Error('First-wave runner failed: '+JSON.stringify(firstExits));
  const firstWaves=Object.fromEntries(newLineages.map(x=>[x.name,verifyWave(x.root,x.name)]));
  persist(state,'first-waves-verified',{firstWaves});report(state);
  const continuous={};
  for(const x of newLineages){const p=launch(x.root,x.name,null,true);continuous[x.name]={pid:p.pid,log:p.log};}
  persist(state,'continuous-starting',{continuous});report(state);
  for(let i=0;i<30;i++){
    const started=newLineages.every(x=>{
      const f=path.join(x.root,'lineages',x.name,'waves/active.json');
      return running(x.name)&&exists(f)&&read(f).id!==firstWaves[x.name].last.wave;
    });
    if(started){persist(state,'continuous-running');report(state);return;}
    await pause(2000);
  }
  throw Error('Continuous runners did not start new waves within 60 seconds');
}
async function retryUnstartedWaves(){
  const state=read(STATE),clean=require('./clean-lineages');
  if(state.stage!=='needs-review'||!state.newLineages)throw Error('No unstarted clean lineages');
  for(const item of state.newLineages){
    requireStopped(item.name,item.root);
    if(exists(path.join(item.root,'lineages',item.name,'waves/active.json')))throw Error('Wave already began; inspect rather than reset it');
    if(rt(item.root).digest(path.join(item.root,'lineages',item.name,'bot'))!==state.baseline.botHash)throw Error('Initial bot changed');
    clean.profile(item.root,item.name);
    git(item.root,['add','--','.isolation/profile.sb']);
    if(git(item.root,['diff','--cached','--name-only']))git(item.root,['commit','-m',item.name+': permit ancestor metadata while denying external file contents']);
  }
  state.operatorPid=process.pid;delete state.error;
  state.isolation=clean.verifyIsolation(state.newLineages);
  try{await startNewWaves(state,state.newLineages);}
  catch(e){persist(state,'needs-review',{error:String(e.stack||e)});report(state);throw e;}
}
function handoffIndependent(){
  const state=read(STATE);
  if(state.stage!=='first-waves-running')throw Error('Expected first-wave supervision');
  const pid=state.operatorPid;
  if(pid===process.pid)throw Error('Refusing to signal the current operator');
  const command=cp.execFileSync('/bin/ps',['-p',String(pid),'-o','command='],{encoding:'utf8'}).trim();
  if(!command.includes('seed-transition.js retry-unstarted-waves'))throw Error('Unexpected supervisor process');
  const history=state.supervisorHistory||[];
  history.push({at:now(),pid,reason:'Continue each lineage immediately after its own verified first wave, without waiting for its peer.'});
  persist(state,'independent-first-wave-handoff',{supervisorHistory:history});report(state);
  // Research runners were spawned detached and remain untouched.
  process.kill(pid,'SIGTERM');
}
async function resumeIndependent(){
  const state=read(STATE);
  if(state.stage!=='independent-first-wave-handoff')throw Error('Expected independent supervisor handoff');
  if(live(state.operatorPid))throw Error('Previous supervisor is still alive');
  state.operatorPid=process.pid;state.firstWaves||={};state.continuous||={};
  persist(state,'first-waves-finishing-independently');report(state);
  try{
    while(true){
      for(const item of state.newLineages){
        if(state.firstWaves[item.name])continue;
        const first=state.firstRuns.find(x=>x.name===item.name);
        if(running(item.name)||live(first.pid)||activeJobs(item.name,item.root).length)continue;
        const checked=verifyWave(item.root,item.name);
        state.firstWaves[item.name]=checked;
        const run=launch(item.root,item.name,null,true);
        state.continuous[item.name]={pid:run.pid,log:run.log};
        persist(state,'first-waves-finishing-independently',{firstWaves:state.firstWaves,continuous:state.continuous});report(state);
      }
      if(state.newLineages.every(item=>state.firstWaves[item.name]))break;
      await pause(5000);
    }
    for(let i=0;i<30;i++){
      const started=state.newLineages.every(item=>running(item.name)&&read(path.join(item.root,'lineages',item.name,'waves/active.json')).id!==state.firstWaves[item.name].last.wave);
      if(started){persist(state,'continuous-running');report(state);return;}
      await pause(2000);
    }
    throw Error('A verified lineage did not enter continuous execution');
  }catch(e){persist(state,'needs-review',{error:String(e.stack||e)});report(state);throw e;}
}
async function resumeClean(){
  const state=read(STATE);
  if(state.stage!=='handoff-awaiting-seed')throw Error('Inspect transition state before resuming');
  state.operatorPid=process.pid;
  persist(state,'archiving-legacy-for-clean-start');report(state);
  try{
    const archives=require('./clean-lineages').archiveLegacy(state.archived);
    persist(state,'waiting-seed-for-clean-start',{archives});report(state);
    while(running('seed0')||live(state.seedRun.pid)||activeJobs('seed0',SEED).length)await pause(5000);
    const baseline=verifyWave(SEED,'seed0',{seed:true});
    await afterBaseline(state,baseline);
  }catch(e){persist(state,'needs-review',{error:String(e.stack||e)});report(state);throw e;}
}
async function recoverSeed(){
  const state=read(STATE);
  if(state.stage!=='needs-review')throw Error('Recovery requires an interrupted transition');
  requireStopped('seed0',SEED);
  const r=rt(SEED),active=read(path.join(SEED,'lineages/seed0/waves/active.json'));
  if(active.id!=='w000001'||active.baselineHash!==null)throw Error('Unexpected seed wave');
  const out=path.join(SEED,'lineages/seed0/checks/w000001-b87f9a4e'),plan=read(path.join(out,'plan.json'));
  if(exists(path.join(active.work,'finish.json')))throw Error('Seed already has a decision');
  const commands=cp.execFileSync('/bin/ps',['-axo','pid=,command='],{encoding:'utf8'}).normalize('NFD');
  if(commands.split('\n').some(s=>s.includes(out.normalize('NFD'))))throw Error('An evaluator may still own the frozen plan');
  function verifyInputs(){
    for(const [dir,hash]of [['candidate',plan.candidateHash],['maps',plan.mapHash],...Object.entries(plan.opponentHashes).map(([n,h])=>['opponents/'+n,h])])
      if(r.digest(path.join(out,dir))!==hash)throw Error('Frozen input changed: '+dir);
    if(r.digest(path.join(SEED,'lineages/seed0/candidate'))!==plan.candidateHash)throw Error('Original mold changed');
  }
  verifyInputs();
  const rowsFile=path.join(out,'candidate-results/rows.jsonl'),priorRows=fs.readFileSync(rowsFile);
  const prior=priorRows.toString().trim().split('\n').filter(Boolean).map(JSON.parse);
  if(prior.some(x=>x.error||x.exit!==0||x.botProblem))throw Error('Review failed rows before resuming');
  const recoveryFile=path.join(out,'operator-recovery.json');
  const history=exists(recoveryFile)?read(recoveryFile).attempts:[];
  const attempt={at:now(),rowsBefore:prior.length,seeds:plan.seeds,priorResult:read(path.join(active.work,'result.json')),
    reason:'Claude background tasks were killed after its waiting turn ended. Resume only missing games under the original frozen plan.'};
  history.push(attempt);r.write(recoveryFile,{attempts:history});
  state.operatorPid=process.pid;delete state.error;
  persist(state,'seed-baseline-recovering',{recovery:{plan:path.join(out,'plan.json'),rowsBefore:prior.length}});report(state);
  const held=await r.lock('runner-seed0',{wait:false});
  const awake=cp.spawn('/usr/bin/caffeinate',['-i','-w',String(process.pid)],{stdio:'ignore'});
  process.env.UNSW_WAVE_ID=active.id;process.env.UNSW_LINEAGE='seed0';
  try{
    await r.drain('seed0');
    await r.job('seed0',async onSpawn=>{
      const result=await r.command(process.execPath,[path.join(SEED,'lineages/_tools/eval.js'),
        '--bot',path.join(out,'candidate'),'--label','seed0-'+active.id+'-candidate',
        '--out',path.join(out,'candidate-results'),'--maps',path.join(out,'maps'),
        '--opponent-root',path.join(out,'opponents'),'--opps',Object.keys(plan.opponentHashes).join(','),
        '--seeds',plan.seeds.join(','),'--jobs','2','--force'],{onSpawn:p=>{onSpawn(p);held.child(p.pid);}});
      if(result.code!==0)throw Error('Resumed evaluator exited '+result.code);
    });
    verifyInputs();
    if(!fs.readFileSync(rowsFile).subarray(0,priorRows.length).equals(priorRows))throw Error('Existing raw rows changed during recovery');
    const check=require(path.join(SEED,'loop/check.js')),rows=check.rows(rowsFile,plan.expected);
    check.verifyConditions(rows,plan);
    const evidence={...plan,status:'valid',result:check.compare(null,rows),scope:'Initial execution baseline on the frozen maps, opponents, seeds and sides; no improvement claim.'};
    r.write(path.join(out,'report.json'),evidence);
    Object.assign(attempt,{finishedAt:now(),rowsAfter:rows.size,status:'completed'});r.write(recoveryFile,{attempts:history});
    persist(state,'seed-baseline-results-ready',{seedReport:path.join(out,'report.json')});report(state);
    console.log(JSON.stringify(evidence.result));
  }catch(e){persist(state,'needs-review',{error:String(e.stack||e)});report(state);throw e;}
  finally{held.release();awake.kill();delete process.env.UNSW_WAVE_ID;delete process.env.UNSW_LINEAGE;}
}
async function adoptRecoveredSeed(){
  const state=read(STATE);
  if(state.stage!=='seed-baseline-results-ready')throw Error('Review complete seed results first');
  requireStopped('seed0',SEED);
  const r=rt(SEED),dir=path.join(SEED,'lineages/seed0'),active=read(path.join(dir,'waves/active.json'));
  const evidence=read(state.seedReport),check=require(path.join(SEED,'loop/check.js'));
  const compilerAudit=read(path.join(evidence.dir,'compiler-audit.json'));
  if(!compilerAudit.allEqual||compilerAudit.inputs.length!==5)throw Error('Initial compiler audit is incomplete');
  const rows=check.rows(path.join(evidence.dir,'candidate-results/rows.jsonl'),160);check.verifyConditions(rows,evidence);
  if(evidence.status!=='valid'||JSON.stringify(check.compare(null,rows))!==JSON.stringify(evidence.result))throw Error('Invalid initial evidence');
  if(exists(path.join(dir,'bot')))throw Error('Initial bot already exists');
  const score=evidence.result.candidate;
  r.snapshot(path.join(evidence.dir,'candidate'),path.join(dir,'bot'));
  fs.appendFileSync(path.join(dir,'NOTES.md'),`\n## 초기 기준선 확인 완료 (${now()})\n160판, 승 ${score.wins}, 생존 ${score.survived}, 평균 G ${score.meanG}. 실행 오류·누락 0. 첫 실행은 66판 후 에이전트 백그라운드 작업 종료로 중단되었다. 원자료를 보존하고 같은 코드·시드·지도·상대에서 남은 94판을 운영자가 이어서 완료했다. checks/w000001-b87f9a4e/operator-recovery.json에 중단과 재개를 보존했다.\n\nready: r1 — 공통 거푸집 초기 실행 기준선. 성능 개선이 아니며, 지도·상대·시드 범위를 넘는 강도 주장을 하지 않는다. 근거 checks/w000001-b87f9a4e/report.json.\n`);
  write(path.join(dir,'CURRENT.md'),`# seed0 CURRENT\n\n- bot/: r1, 사용자 승인 거푸집과 동일. 초기 확인 160/160 정상 실행, ${score.wins}승, ${score.survived}판 생존, 평균 G ${score.meanG}.\n- 기준선 확인만 완료했으며 성능 개선을 주장하지 않는다. 검증 범위는 고정된 지도 10개·상대 4개·양 진영·시드 2개다.\n- 근거: checks/w000001-b87f9a4e/report.json 및 candidate-results/rows.jsonl. 최초 중단 기록은 operator-recovery.json에 보존했다.\n- 새 계통에는 초기 코드와 실행 검증 여부만 전달한다. 이 기록·성적·과거 가설은 전달하지 않는다.\n`);
  process.env.UNSW_WAVE_ID=active.id;
  const finish=runner(SEED).finish('seed0','adopt','160판 정상 실행을 확인한 공통 초기 기준선; 개선 주장 없음',state.seedReport);
  const prior=path.join(active.work,'result-before-operator-recovery.json');
  if(!exists(prior))fs.copyFileSync(path.join(active.work,'result.json'),prior);
  const result={...finish,exit:0,operatorRecovery:true,at:now()};
  r.write(path.join(active.work,'result.json'),result);r.write(path.join(dir,'waves/last.json'),result);
  fs.appendFileSync(path.join(dir,'waves/index.log'),now()+' operator completed original frozen confirmation and adopted initial baseline\n');
  runner(SEED).publish('seed0',active,result);r.commit('seed0','seed0: preserve interrupted run and completed initial confirmation');
  delete process.env.UNSW_WAVE_ID;
  state.operatorPid=process.pid;
  try{await afterBaseline(state,verifyWave(SEED,'seed0',{seed:true}));}
  catch(e){persist(state,'needs-review',{error:String(e.stack||e)});report(state);throw e;}
}
async function resumeProvision(){
  const state=read(STATE),clean=require('./clean-lineages');
  if(state.stage!=='needs-review'||!state.baseline||state.newLineages)throw Error('Not a prelaunch provisioning interruption');
  const preserved=[];
  for(const item of NEW){
    if(!exists(item.root))continue;
    requireStopped(item.name,item.root);
    if(exists(path.join(item.root,'.git'))||exists(path.join(item.root,'lineages',item.name)))throw Error('Inspect initialized lineage before resuming');
    const destination=path.join(clean.CONTROL,'operator-only','provision-interrupted-'+item.name+'-'+Date.now());
    fs.mkdirSync(path.dirname(destination),{recursive:true});fs.renameSync(item.root,destination);
    preserved.push({name:item.name,path:destination});
  }
  state.operatorPid=process.pid;state.provisioningRecovery=preserved;delete state.error;
  try{await afterBaseline(state,verifyWave(SEED,'seed0',{seed:true}));}
  catch(e){persist(state,'needs-review',{error:String(e.stack||e)});report(state);throw e;}
}
async function run() {
  if(exists(STATE)) throw Error('Transition already recorded; inspect status instead of starting twice');
  for(const {root,name} of OLD) if(!exists(path.join(root,'lineages',name,'STOP'))) throw Error('Schedule legacy STOP first');
  const state={created:now(),operatorPid:process.pid,legacy:OLD,newTargets:NEW};
  persist(state,'waiting-legacy');report(state);
  try {
    while(OLD.some(x=>running(x.name)||activeJobs(x.name,x.root).length)) await pause(5000);
    const archived=OLD.map(archiveOld);
    persist(state,'legacy-archived',{archived});report(state);
    prepareSeed();
    const seed=launch(SEED,'seed0',1);
    persist(state,'seed-baseline-running',{seedRun:{pid:seed.pid,log:seed.log}});report(state);
    const seedExit=await seed.result;
    if(seedExit.code!==0) throw Error('Seed runner exited '+JSON.stringify(seedExit));
    const baseline=verifyWave(SEED,'seed0',{seed:true});
    persist(state,'seed-baseline-verified',{baseline});report(state);
    persist(state,'archiving-legacy-for-clean-start',{archives:require('./clean-lineages').archiveLegacy(state.archived)});
    await afterBaseline(state,baseline);
  } catch(e) {persist(state,'needs-review',{error:String(e.stack||e)});report(state);throw e;}
}
if(require.main===module) Promise.resolve().then(()=>{
  const action=process.argv[2];
  if(action==='status') return status();
  if(action==='brief') return briefStatus();
  if(action==='verify-first'){
    const item=NEW.find(x=>x.name===process.argv[3]);
    if(!item)throw Error('Specify g3 or g4');
    const v=verifyWave(item.root,item.name);
    return console.log(JSON.stringify({name:item.name,wave:v.last.wave,outcome:v.last.outcome,exit:v.last.exit,version:v.last.version,
      sourceHash:v.botHash,commit:v.commit,candidate:v.evidence?.result.candidate,baseline:v.evidence?.result.baseline}));
  }
  if(action==='refresh-report') return report(read(STATE));
  if(action==='request-clean-stop') {
    const state=read(STATE), requestedAt=now();
    for(const item of NEW) write(path.join(item.root,'lineages',item.name,'STOP'),requestedAt+' user requested resumable pause\n');
    persist(state,'pause-requested',{pause:{requestedAt,reason:'User requested stopping g3/g4 with work preserved for later continuation.'}});
    return report(state);
  }
  if(action==='pause-clean') return pauseClean();
  if(action==='record-worktree-migration') return recordWorktreeMigration();
  if(action==='resume-paused') return resumePaused();
  if(action==='stop-now') return stopNow();
  if(action==='handoff') return handoff();
  if(action==='resume-clean') return resumeClean();
  if(action==='recover-seed') return recoverSeed();
  if(action==='adopt-recovered-seed') return adoptRecoveredSeed();
  if(action==='resume-provision') return resumeProvision();
  if(action==='retry-unstarted-waves') return retryUnstartedWaves();
  if(action==='handoff-independent') return handoffIndependent();
  if(action==='resume-independent') return resumeIndependent();
  if(action==='test-clean-isolation') return console.log(JSON.stringify(require('./clean-lineages').testIsolation(),null,2));
  if(action==='prepare-clean-tools') return console.log(require('./clean-lineages').opponents());
  if(action==='test-clean-client') return require('./clean-lineages').testClient();
  if(action==='audit-seed-build') return require('./clean-lineages').auditSeedBuild();
  if(action==='verify-archives') return require('./clean-lineages').verifyArchives(read(STATE).archived);
  if(action==='archive-shared-data') return require('./clean-lineages').archiveSharedData(read(STATE).archived);
  if(action==='run') return run();
  throw Error('usage: seed-transition.js status|stop-now|run');
}).catch(e=>{console.error(e.message);process.exitCode=1;});
