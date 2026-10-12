// Clean lineage construction. Called only by the operator transition script.
const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'..'), PARENT=path.dirname(ROOT);
const CONTROL=path.join(PARENT,'unsw-arena-clean-control');
const ARCHIVE=path.join(PARENT,'unsw-arena-archive','legacy-20260928');
const TOOLKIT='~/01. Project/개인 프로젝트/UNSW/.unswbc-110';
const PACKAGES='~/01. Project/개인 프로젝트/UNSW/.venv-ppo/lib/python3.13/site-packages';
const PYTHON='~/.aside/runtime/bin/python3';
const OPPONENTS=['replay_rules_v8','archetype_swarm','archetype_hunter','h2'];
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const write=(f,s)=>{fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,s);};
const git=(root,args)=>cp.execFileSync('git',args,{cwd:root,encoding:'utf8'}).trim();
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const rt=root=>require(path.join(root,'loop/runtime.js'));

function archiveLegacy(items){
  fs.mkdirSync(ARCHIVE,{recursive:true});
  const result=[];
  for(const item of items){
    const destination=path.join(ARCHIVE,item.name);
    if(!fs.existsSync(destination)){
      fs.mkdirSync(destination);
      fs.cpSync(path.join(item.root,'lineages',item.name),path.join(destination,'lineage'),{recursive:true,dereference:true});
      for(const f of ['CLAUDE.md','lineages/BRIEF.md','lineages/LOOP.md','lineages/GROWTH.md'])
        fs.copyFileSync(path.join(item.root,f),path.join(destination,path.basename(f)));
      git(item.root,['bundle','create',path.join(destination,'history.bundle'),git(item.root,['branch','--show-current'])]);
      const files=rt(item.root).hashes(path.join(item.root,'lineages',item.name,'bot'));
      for(const [f,h]of Object.entries(files))if(hash(path.join(destination,'lineage/bot',f))!==h)throw Error('Archive bot mismatch');
      write(path.join(destination,'ARCHIVE.json'),JSON.stringify({...item,archivedAt:new Date().toISOString(),files},null,2)+'\n');
    }
    result.push({name:item.name,path:destination});
  }
  write(path.join(ARCHIVE,'README.md'),'# Legacy archive\n\nThis archive is outside the clean research repositories. The clean agents are denied file access to this directory, the former worktrees, and the former Git history. The history bundles and lineage copies preserve prior work.\n');
  return result;
}

function verifyArchives(items){
  const summaries=[];
  for(const item of items){
    const destination=path.join(ARCHIVE,item.name),copy=path.join(destination,'lineage');
    const links=[];
    function materialize(dir){
      for(const name of fs.readdirSync(dir)){
        const file=path.join(dir,name),stat=fs.lstatSync(file);
        if(stat.isSymbolicLink()){
          const target=fs.readlinkSync(file),source=fs.realpathSync(file),staging=file+'.materialized-'+crypto.randomUUID();
          fs.cpSync(source,staging,{recursive:true,dereference:true,preserveTimestamps:true});
          links.push({path:path.relative(copy,file),formerTarget:target});
          write(path.join(destination,'materialized-links.json'),JSON.stringify(links,null,2)+'\n');
          if(!fs.lstatSync(file).isSymbolicLink())throw Error('Archive link changed during materialization');
          fs.unlinkSync(file);fs.renameSync(staging,file);
          if(fs.statSync(file).isDirectory())materialize(file);
        }else if(stat.isDirectory())materialize(file);
      }
    }
    materialize(copy);
    function inventory(dir){
      const result={};
      function visit(base,rel,ancestors){
        const real=fs.realpathSync(base);
        if(ancestors.has(real))throw Error('Archive source contains a link cycle');
        const next=new Set([...ancestors,real]);
        for(const name of fs.readdirSync(base).sort()){
          const p=path.join(base,name),key=path.join(rel,name),s=fs.statSync(p);
          if(s.isDirectory())visit(p,key,next);
          else if(s.isFile())result[key]={bytes:s.size,sha256:hash(p)};
        }
      }
      visit(dir,'',new Set());return result;
    }
    const original=inventory(path.join(item.root,'lineages',item.name)),archived=inventory(copy);
    const mismatches=[...new Set([...Object.keys(original),...Object.keys(archived)])].filter(k=>JSON.stringify(original[k])!==JSON.stringify(archived[k]));
    if(mismatches.length)throw Error('Archive differs from stopped source: '+JSON.stringify(mismatches.slice(0,10)));
    const bundle=cp.spawnSync('git',['bundle','verify',path.join(destination,'history.bundle')],{cwd:ROOT,encoding:'utf8'});
    if(bundle.status!==0)throw Error('Archive Git bundle failed verification');
    const summary={name:item.name,at:new Date().toISOString(),files:Object.keys(archived).length,
      bytes:Object.values(archived).reduce((s,x)=>s+x.bytes,0),mismatches:0,symlinksRemaining:0,completeGitHistory:true};
    write(path.join(destination,'INTEGRITY.json'),JSON.stringify({...summary,sha256:archived},null,2)+'\n');
    summaries.push(summary);console.log(JSON.stringify(summary));
  }
  return summaries;
}

function archiveSharedData(items){
  const data=path.join(PARENT,'unsw-arena-data'),results=[];
  for(const item of items){
    const destination=path.join(ARCHIVE,item.name,'shared-data'),files={};
    function copy(from,to,ancestors=new Set()){
      const real=fs.realpathSync(from),stat=fs.statSync(from);
      if(ancestors.has(real))throw Error('Shared archive source contains a link cycle');
      if(stat.isDirectory()){
        fs.mkdirSync(to,{recursive:true});
        for(const n of fs.readdirSync(from).sort())copy(path.join(from,n),path.join(to,n),new Set([...ancestors,real]));
      }else if(stat.isFile()){
        fs.mkdirSync(path.dirname(to),{recursive:true});
        if(!fs.existsSync(to))fs.copyFileSync(from,to);
        if(fs.lstatSync(to).isSymbolicLink())throw Error('Archive copy is still a symlink');
        const expected=hash(from),actual=hash(to);
        if(expected!==actual)throw Error('Shared archive file mismatch');
        files[path.relative(destination,to)]={bytes:stat.size,sha256:actual};
      }
    }
    for(const category of ['eval','releases']){
      const source=path.join(data,category);
      for(const n of fs.readdirSync(source).sort())if(n.startsWith(item.name+'-'))copy(path.join(source,n),path.join(destination,category,n));
    }
    const jobs=path.join(data,'control/jobs');
    for(const n of fs.readdirSync(jobs).filter(n=>n.endsWith('.json')).sort()){
      const f=path.join(jobs,n),j=read(f);
      if(j.lineage===item.name&&j.root?.normalize('NFD')===item.root.normalize('NFD'))copy(f,path.join(destination,'jobs',n));
    }
    const result={name:item.name,at:new Date().toISOString(),files:Object.keys(files).length,bytes:Object.values(files).reduce((s,x)=>s+x.bytes,0),mismatches:0};
    write(path.join(ARCHIVE,item.name,'SHARED-INTEGRITY.json'),JSON.stringify({...result,sha256:files},null,2)+'\n');
    results.push(result);console.log(JSON.stringify(result));
  }
  return results;
}

function opponents(){
  const dir=path.join(CONTROL,'operator-only/opponents');
  fs.mkdirSync(dir,{recursive:true});
  if(OPPONENTS.every(n=>fs.existsSync(path.join(dir,n,'main.wasm'))))return dir;
  const code=`import sys, pathlib, shutil, json, importlib.util\nsys.path[:0]=[${JSON.stringify(TOOLKIT)},${JSON.stringify(PACKAGES)}]\nfrom unswbc import clangtool\nroot=pathlib.Path(${JSON.stringify(ROOT)})\nout=pathlib.Path(${JSON.stringify(dir)})\nspec=importlib.util.spec_from_file_location('clean_inputs',root/'scripts/clean-unswbc.py')\nmodule=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)\nfor name in ${JSON.stringify(OPPONENTS)}:\n built=clangtool.build(module.freeze(root/'bots'/name,out.parent/'source-cache'))\n dest=out/name/'main.wasm'\n dest.parent.mkdir(parents=True,exist_ok=True)\n shutil.copyfile(built,dest)\n print(json.dumps({'opponent':name,'bytes':dest.stat().st_size}),flush=True)\n`;
  cp.execFileSync(PYTHON,['-c',code],{cwd:ROOT,stdio:'inherit',env:{...process.env,PYTHONPATH:TOOLKIT+':'+PACKAGES,XDG_CACHE_HOME:path.join(CONTROL,'operator-only/cache')}});
  return dir;
}

function auditSeedBuild(){
  const out=path.join(PARENT,'unsw-arena-seed/lineages/seed0/checks/w000001-b87f9a4e');
  const code=`import sys, pathlib, json, os, hashlib, importlib.util\nsys.path[:0]=[${JSON.stringify(TOOLKIT)},${JSON.stringify(PACKAGES)}]\nfrom unswbc import clangtool\nspec=importlib.util.spec_from_file_location('clean_inputs',${JSON.stringify(path.join(ROOT,'scripts/clean-unswbc.py'))})\nmodule=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)\nout=pathlib.Path(${JSON.stringify(out)})\noperator=pathlib.Path(${JSON.stringify(path.join(CONTROL,'operator-only'))})\noriginal_cache=os.environ.get('XDG_CACHE_HOME')\nresults=[]\nfor name in ['candidate',*['opponents/'+x for x in ${JSON.stringify(OPPONENTS)}]]:\n if original_cache is None: os.environ.pop('XDG_CACHE_HOME',None)\n else: os.environ['XDG_CACHE_HOME']=original_cache\n legacy=clangtool.build(out/name)\n a=hashlib.sha256(legacy.read_bytes()).hexdigest()\n os.environ['XDG_CACHE_HOME']=str(operator/'cache')\n fresh=clangtool.build(module.freeze(out/name,operator/'source-cache'))\n b=hashlib.sha256(fresh.read_bytes()).hexdigest()\n results.append({'input':name,'existingWasmHash':a,'freshWasmHash':b,'same':a==b})\n print(json.dumps(results[-1]),flush=True)\n(out/'compiler-audit.json').write_text(json.dumps({'allEqual':all(r['same'] for r in results),'inputs':results},indent=2)+'\\n')\nif not all(r['same'] for r in results):sys.exit(1)\n`;
  cp.execFileSync(PYTHON,['-c',code],{cwd:ROOT,stdio:'inherit',env:{...process.env,PYTHONPATH:TOOLKIT+':'+PACKAGES}});
  return read(path.join(out,'compiler-audit.json'));
}

function profile(root,name){
  // Apply to the entire runner process tree, including file tools and Bash.
  // Only neutral toolkit installations and the clean coordination directory are
  // readable under the project parent; no former repository is an exception.
  const forms=p=>[...new Set([p.normalize('NFD'),p.normalize('NFC')])];
  const sub=p=>forms(p).map(v=>`(subpath ${JSON.stringify(v)})`);
  const no=p=>sub(p).map(s=>`(require-not ${s})`).join('\n    ');
  const allow=[root,CONTROL,TOOLKIT,PACKAGES];
  const denied=[ARCHIVE,path.join(CONTROL,'operator-only'),'~/orca/workspaces/unsw-arena',
    '~/.claude/projects','~/.claude/history.jsonl',
    '~/.claude/plugins','~/.claude/plans','~/.claude/todos',
    '~/.codex/sessions','~/.codex/archived_sessions','~/.codex/memories',
    '/private/tmp/claude-501','~/.cache/unswbc','~/Downloads/api.txt'];
  let text='(version 1)\n(allow default)\n';
  // Parent-directory metadata is needed for realpath/module loading. Contents
  // remain denied; explicit legacy directories are denied even metadata below.
  for(const parent of forms(PARENT))text+=`(deny file-read-data file-write*\n  (require-all (subpath ${JSON.stringify(parent)})\n    ${allow.map(no).join('\n    ')}))\n`;
  for(const p of denied)for(const s of sub(p))text+=`(deny file-read* file-write* ${s})\n`;
  for(const p of [TOOLKIT,PACKAGES])for(const s of sub(p))text+=`(deny file-write* ${s})\n`;
  for(const rel of ['.isolation','loop','rules','bots','lineages/_tools','CLAUDE.md','AGENTS.md','lineages/BRIEF.md','lineages/LOOP.md','lineages/GROWTH.md'])
    for(const s of sub(path.join(root,rel)))text+=`(deny file-write* ${s})\n`;
  write(path.join(root,'.isolation/profile.sb'),text);
  const settings={autoMemoryEnabled:false,enableAllProjectMcpServers:false};
  write(path.join(root,'.isolation/settings.json'),JSON.stringify(settings,null,2)+'\n');
  write(path.join(root,'.isolation/mcp.json'),'{"mcpServers":{}}\n');
}

function clientArgs(root){
  return ['--safe-mode','--no-session-persistence','--strict-mcp-config','--mcp-config',path.join(root,'.isolation/mcp.json'),
    '--no-chrome','--disable-slash-commands','--setting-sources','project','--settings',path.join(root,'.isolation/settings.json'),
    '--tools','Bash,Read,Edit,Write,Glob,Grep,TaskStop,Workflow'];
}

function provision(item,baseline){
  const {name,root}=item;
  if(fs.existsSync(root))throw Error('Clean repository already exists: '+root);
  fs.mkdirSync(root,{recursive:true});
  for(const dir of ['rules','maps','loop'])fs.cpSync(path.join(ROOT,dir),path.join(root,dir),{recursive:true,dereference:true});
  for(const f of ['AGENTS.md','CLAUDE.md','.gitignore','lineages/BRIEF.md','lineages/LOOP.md','lineages/GROWTH.md']){
    fs.mkdirSync(path.dirname(path.join(root,f)),{recursive:true});fs.copyFileSync(path.join(ROOT,f),path.join(root,f));
  }
  for(const f of ['unswbc','eval.js','viewer.js','export_replay.js']){
    fs.mkdirSync(path.join(root,'lineages/_tools'),{recursive:true});fs.copyFileSync(path.join(ROOT,'lineages/_tools',f),path.join(root,'lineages/_tools',f));
  }
  fs.copyFileSync(path.join(ROOT,'scripts/clean-unswbc.py'),path.join(root,'lineages/_tools/unswbc-clean.py'));
  write(path.join(root,'lineages/_tools/unswbc'),`#!/bin/bash\nset -e\nexport PYTHONPATH=${JSON.stringify(TOOLKIT+':'+PACKAGES)} UNSWBC_NO_VSCODE=1 NO_COLOR=1\nexec ${JSON.stringify(PYTHON)} ${JSON.stringify(path.join(root,'lineages/_tools/unswbc-clean.py'))} "$@"\n`);
  fs.chmodSync(path.join(root,'lineages/_tools/unswbc'),0o755);
  let claude=fs.readFileSync(path.join(root,'CLAUDE.md'),'utf8');
  claude=claude.replace('| `lineages/_eval`, `_releases`, `<이름>/logs` | 공유 데이터 폴더로 가는 링크(벤치마크 결과, 배포 스냅숏, 온라인 기록) |',
    '| `.arena-data/`, `lineages/<이름>/checks/` | 이 저장소만의 평가 결과·배포 스냅숏·로그 |');
  write(path.join(root,'CLAUDE.md'),claude);
  // No symlinks to legacy data. Only fresh job/lock coordination is shared.
  let runtime=fs.readFileSync(path.join(root,'loop/runtime.js'),'utf8');
  runtime=runtime.replace("const DATA = process.env.UNSW_ARENA_DATA || '~/01. Project/개인 프로젝트/unsw-arena-data';",
    "const DATA = process.env.UNSW_ARENA_DATA || path.join(ROOT, '.arena-data');\nconst CONTROL = process.env.UNSW_ARENA_CONTROL || path.join(DATA, 'control');");
  runtime=runtime.replace("path.join(DATA, 'control', 'locks', name)","path.join(CONTROL, 'locks', name)");
  runtime=runtime.replace("path.join(DATA, 'control', 'jobs')","path.join(CONTROL, 'jobs')");
  runtime=runtime.replace("name.endsWith('.wasm')","(name.endsWith('.wasm') && name !== 'main.wasm')");
  if(runtime.includes("path.join(DATA, 'control',")||runtime.includes('/unsw-arena-data'))throw Error('Clean runtime still refers to legacy control/data');
  write(path.join(root,'loop/runtime.js'),runtime);
  const bootArgs=clientArgs(root);
  let runner=fs.readFileSync(path.join(root,'loop/runner.js'),'utf8');
  runner=runner.replace("['-p', prompt, '--model', which,",`['-p', prompt, ...${JSON.stringify(bootArgs)}, '--model', which,`);
  const guard=`\n  // Refuse an accidental launch outside the mandatory OS sandbox.\n  try {\n    const fd=fs.openSync(${JSON.stringify(path.join(ARCHIVE,'README.md'))},'r'); fs.closeSync(fd);\n    throw Error('Use .isolation/launch.sh: legacy archive is readable outside the sandbox');\n  } catch(e) { if(!['EACCES','EPERM'].includes(e.code)) throw e; }\n`;
  runner=runner.replace("  const dir = rt.lineage(name), waves = path.join(dir, 'waves');\n  fs.mkdirSync(waves, { recursive: true });",
    guard+"  const dir = rt.lineage(name), waves = path.join(dir, 'waves');\n  fs.mkdirSync(waves, { recursive: true });");
  if(!runner.includes('--safe-mode')||!runner.includes('mandatory OS sandbox'))throw Error('Clean runner isolation setup failed');
  write(path.join(root,'loop/runner.js'),runner);
  fs.appendFileSync(path.join(root,'loop/wave-prompt.md'),'\n평가는 끝날 때까지 Bash 호출에서 기다린다. 평가를 백그라운드로 돌리지 않는다. run-job.js/check.js를 실행하는 Bash의 timeout은 21600000(6시간)으로 지정한다. 큐 대기도 이 시간에 포함된다. 등록된 평가가 남아 있으면 최종 응답을 보내지 않는다.\n');
  const binaries=opponents();
  for(const opp of OPPONENTS)fs.cpSync(path.join(binaries,opp),path.join(root,'bots',opp),{recursive:true});
  const dir=path.join(root,'lineages',name);fs.mkdirSync(dir,{recursive:true});
  const initialHash=rt(ROOT).snapshot(path.join(path.dirname(baseline.last.report),'candidate'),path.join(dir,'bot'));
  if(initialHash!==baseline.botHash)throw Error('Clean seed differs from confirmed mold');
  const initialFiles=rt(ROOT).hashes(path.join(dir,'bot'));
  write(path.join(dir,'ORIGIN.json'),JSON.stringify({kind:'common-initial-seed',sha256:initialHash,files:initialFiles,verifiedExecution:true,independentImprovement:false},null,2)+'\n');
  write(path.join(dir,'NOTES.md'),`# ${name} NOTES\n\n## 공통 초기 코드\n운영자가 실행 검증한 동일한 거푸집 코드를 받아 시작한다. 이전 계통의 코드·이력·제안·성적·대화는 전달받지 않았다. 초기 코드 식별자는 ORIGIN.json에 있다.\n\nready: r1 — 전달받은 초기 코드. 이 계통의 개선이나 독립 성능 검증으로 세지 않는다.\n`);
  write(path.join(dir,'CURRENT.md'),`# ${name} CURRENT\n\n- 현재 bot/: r1, 운영자가 제공한 공통 초기 코드. ORIGIN.json의 파일 해시와 일치.\n- 진행 중 실험: 없음. 이전 실험의 가설·추천·성적은 전달받지 않았다.\n- 규칙서와 자기 코드를 읽고 스스로 관찰·가설·탐색을 시작한다. 후보는 별도 디렉터리에서 구현하고 채택할 후보는 LOOP.md의 새 조건 비교로 확인한다.\n- 종료 전 CURRENT.md를 갱신하고 finish adopt/reject/incomplete로 판단을 기록한다. 채택을 강제하지 않는다.\n`);
  let brief=fs.readFileSync(path.join(root,'lineages/BRIEF.md'),'utf8');
  brief=brief.replace('로컬 상대(블랙박스로 실행만, 소스는 읽지 말 것):','로컬 상대(실행 전용 main.wasm만 제공; 분석·역공학하지 말 것):');
  brief+='\n## 독립 실행 공간\n- 이 저장소는 새 Git 이력으로 시작하며 다른 계통·과거 아카이브·외부 작업 폴더는 OS에서 접근 차단된다. 로컬 상대는 공식 도구로 컴파일한 실행 바이너리만 제공한다.\n- 공통 도구와 규칙은 읽기 전용이다. 연구 파일은 자기 lineages 폴더에서만 변경한다.\n- 평가 결과·배포 스냅숏·로그는 이 저장소의 .arena-data에만 보관한다. 두 계통은 전략 자료 없이 실행 큐의 잠금·작업 상태만 공유한다.\n- 세션은 과거 대화·자동 메모리·전역 플러그인·MCP·외부 CLAUDE.md를 불러오지 않는다. CLAUDE.md는 이 저장소의 파일을 직접 읽는다.\n';
  write(path.join(root,'lineages/BRIEF.md'),brief);
  write(path.join(root,'README.md'),`# ${name} 독립 연구 공간\n\n동일한 초기 코드에서 독립적으로 발전시키는 계통. 규칙·작업 순서는 CLAUDE.md를 따른다. 다른 계통의 파일·Git 이력·대화·메모리를 공유하지 않는다.\n\n중지: touch lineages/${name}/STOP. 현재 웨이브와 등록된 평가 후 종료한다. 실행은 운영자의 격리 실행기를 통해 시작한다.\n`);
  fs.appendFileSync(path.join(root,'.gitignore'),'\n.arena-data/\n.isolation/probe-old\n');
  profile(root,name);
  const sh=s=>"'"+s.replaceAll("'","'\\''")+"'";
  const launchEnv=launchConfig(root).env;
  for(const rel of ['.arena-data/cache','.arena-data/tmp'])fs.mkdirSync(path.join(root,rel),{recursive:true});
  write(path.join(root,'.isolation/launch.sh'),`#!/bin/bash\nset -e\ncd ${sh(root)}\n${Object.entries(launchEnv).map(([k,v])=>'export '+k+'='+sh(v)).join('\n')}\nexec /usr/bin/caffeinate -i /usr/bin/sandbox-exec -f .isolation/profile.sb ${sh(process.execPath)} loop/runner.js run ${name}\n`);
  fs.chmodSync(path.join(root,'.isolation/launch.sh'),0o755);
  git(root,['init','-b','main']);
  git(root,['add','--','AGENTS.md','CLAUDE.md','README.md','.gitignore','.isolation','rules','maps','loop','bots','lineages']);
  git(root,['commit','-m',name+': clean initial seed and isolated research tools']);
  if(git(root,['rev-list','--count','HEAD'])!=='1'||git(root,['remote'])||fs.existsSync(path.join(root,'.git/objects/info/alternates')))
    throw Error('Repository is not independently initialized');
  return {...item,branch:'main',initialHash,initialCommit:git(root,['rev-parse','HEAD']),independentRepository:true};
}

function verifyIsolation(items){
  const checks=[];
  for(const item of items){
    const peer=items.find(x=>x.name!==item.name);
    const old=path.join(ROOT,'CLAUDE.md');
    const alias=path.join(item.root,'.isolation/probe-old');
    fs.symlinkSync(old,alias);
    const probe={allow:[path.join(item.root,'CLAUDE.md'),path.join(item.root,'lineages',item.name,'bot/bot.toml')],
      deny:[old,path.join(ARCHIVE,'README.md'),path.join(peer.root,'CLAUDE.md'),path.join(PARENT,'unsw-arena-seed/lineages/seed0/NOTES.md'),alias],
      protected:[path.join(item.root,'loop/runtime.js'),path.join(item.root,'.isolation/profile.sb')]};
    const code=`const fs=require('fs');require('./loop/runtime');const p=${JSON.stringify(probe)};let fail=[];for(const f of p.allow){try{fs.realpathSync(f);fs.readFileSync(f)}catch(e){fail.push({expected:'allow',f,code:e.code})}}for(const f of p.deny){try{fs.readFileSync(f);fail.push({expected:'deny',f})}catch(e){if(!['EACCES','EPERM'].includes(e.code))fail.push({expected:'deny',f,code:e.code})}}for(const f of p.protected){try{const fd=fs.openSync(f,'a');fs.closeSync(fd);fail.push({expected:'write-deny',f})}catch(e){if(!['EACCES','EPERM'].includes(e.code))fail.push({expected:'write-deny',f,code:e.code})}}console.log(JSON.stringify({name:${JSON.stringify(item.name)},passed:!fail.length,checks:p.allow.length+p.deny.length+p.protected.length,fail}));if(fail.length)process.exitCode=1;`;
    try{
      const output=cp.execFileSync('/usr/bin/sandbox-exec',['-f',path.join(item.root,'.isolation/profile.sb'),process.execPath,'-e',code],{cwd:item.root,encoding:'utf8'});
      checks.push(JSON.parse(output));
    }finally{fs.unlinkSync(alias);}
  }
  return checks;
}
function launchConfig(root){
  const childWorktree=root.startsWith('~/orca/workspaces/unsw-arena/');
  return {command:'/usr/bin/caffeinate',args:childWorktree?
      ['-i',process.execPath,path.join(root,'loop/runner.js')]:
      ['-i','/usr/bin/sandbox-exec','-f',path.join(root,'.isolation/profile.sb'),process.execPath,path.join(root,'loop/runner.js')],
    env:{UNSW_ARENA_DATA:path.join(root,'.arena-data'),UNSW_ARENA_CONTROL:CONTROL,
      ...(childWorktree?{UNSW_OPERATOR_LAUNCH:'1'}:{}),XDG_CACHE_HOME:path.join(root,'.arena-data/cache'),
      CLAUDE_CODE_TMPDIR:path.join(root,'.arena-data/tmp'),CLAUDE_CODE_DISABLE_BACKGROUND_TASKS:'1',
      BASH_DEFAULT_TIMEOUT_MS:'21600000',BASH_MAX_TIMEOUT_MS:'21600000'}};
}
function testIsolation(){
  const tmp=fs.mkdtempSync('/private/tmp/unsw-clean-isolation-');
  const items=['g3','g4'].map(name=>({name,root:path.join(tmp,name)}));
  for(const x of items){
    write(path.join(x.root,'CLAUDE.md'),'probe\n');
    write(path.join(x.root,'lineages',x.name,'bot/bot.toml'),'[project]\n');
    write(path.join(x.root,'loop/runtime.js'),'// probe\n');
    profile(x.root,x.name);
  }
  if(!fs.existsSync(path.join(ARCHIVE,'README.md')))write(path.join(ARCHIVE,'README.md'),'# Legacy archive\n');
  // A peer outside the real project parent needs an explicit deny for this fixture.
  for(const x of items){const peer=items.find(y=>y.name!==x.name);fs.appendFileSync(path.join(x.root,'.isolation/profile.sb'),`(deny file-read* file-write* (subpath ${JSON.stringify(peer.root)}))\n`);}
  return {directory:tmp,checks:verifyIsolation(items)};
}
function testClient(){
  const isolation=testIsolation(),root=path.join(isolation.directory,'g3');
  fs.mkdirSync(path.join(root,'.arena-data/tmp'),{recursive:true});
  const result=cp.spawnSync('/usr/bin/sandbox-exec',['-f',path.join(root,'.isolation/profile.sb'),'claude','-p',
    'Reply with READY only. Do not inspect files or use tools.',...clientArgs(root),'--model','claude-opus-5-5',
    '--dangerously-skip-permissions','--max-turns','1','--output-format','stream-json','--verbose'],
    {cwd:root,env:{...process.env,...launchConfig(root).env},encoding:'utf8',timeout:90000,maxBuffer:4<<20});
  write(path.join(root,'client-probe.jsonl'),result.stdout||'');
  const messages=(result.stdout||'').split('\n').filter(Boolean).flatMap(l=>{try{return [JSON.parse(l)];}catch{return [];}});
  const init=messages.find(x=>x.type==='system'&&x.subtype==='init');
  const final=messages.findLast(x=>x.type==='result');
  const unexpected=init&&(init.mcp_servers?.length||init.skills?.length||init.memory_paths?.auto||
    init.plugins?.some(p=>p.path!=='builtin'||!['agents-md','telemetry'].includes(p.name))||
    init.agents?.some(n=>!['claude','Explore','general-purpose','Plan'].includes(n)));
  const summary={directory:root,exit:result.status,isolated:!!init&&!unexpected,servers:init?.mcp_servers,skills:init?.skills,
    plugins:init?.plugins,agents:init?.agents,memoryPaths:init?.memory_paths,tools:init?.tools,
    result:final?.result,error:result.error?.message,stderr:result.stderr?.slice(-1500)};
  console.log(JSON.stringify(summary,null,2));
  if(result.status!==0||!summary.isolated||final?.is_error)throw Error('Clean Claude client preflight failed');
  return summary;
}
module.exports={CONTROL,ARCHIVE,archiveLegacy,verifyArchives,archiveSharedData,opponents,auditSeedBuild,profile,provision,verifyIsolation,launchConfig,testIsolation,testClient};
