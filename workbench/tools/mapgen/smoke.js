#!/usr/bin/env node
// Sequential official-runner queue. No result strength or winner fields are extracted.
'use strict';
const L=require('./lib'),{fs,path,ROOT,read,hash}=L,cp=require('child_process'),{validate}=require('./validate');
const OUT=path.join(ROOT,'exp/mapgen'),ROWS=path.join(OUT,'smoke.jsonl');
function resources() {
 const p=cp.spawnSync('pgrep',['-f','unswbc-clean.py run'],{encoding:'utf8'});
 const free=fs.statfsSync(ROOT),freeBytes=free.bavail*free.bsize;
 if(p.error||![0,1].includes(p.status)||p.stderr.trim())return {ok:false,reason:'process_count_unavailable',detail:String(p.error||p.stderr||'pgrep exit '+p.status).trim(),freeBytes};
 const running=p.stdout.trim()?p.stdout.trim().split('\n').length:0;
 return {ok:running<6&&freeBytes>=21*1024**3,reason:running>=6?'machine_game_cap':freeBytes<21*1024**3?'disk_below_21_GiB':null,running,freeBytes};
}
function parseCpu(log) {
 const out={A:null,B:null};for(const m of log.matchAll(/team ([AB]) points per turn:[^\n]*? max ([\d,.]+M?)\s+\((\d+) turns\)/g)){const s=m[2],v=parseFloat(s.replace(/,/g,''))*(s.endsWith('M')?1e6:1);out[m[1]]={maxPoints:v,reported:s,precisionPoints:s.endsWith('M')?100000:1,turns:+m[3]};}return out;
}
function analyseReplay(file,side,log='') {
 const {makeLoader,viewerSource}=require(path.join(ROOT,'tools/top_features.js')),R=makeLoader(viewerSource())(file);
 const teams=new Map(R.match.map.initialDragons.map(d=>[d.id,d.team])),recognition={A:{},B:{}},engines={A:{},B:{}},timeouts=[];let round=-1;
 for(const e of R.events){if(e.type==='roundStart')round=e.round;if(e.type==='dragonSplit')teams.set(e.childId,e.team);const id=e.id??e.dragonId,t=teams.get(id);
  if(e.type==='dragonIndicator') {if(!recognition[t])continue;const text=e.text||'';for(const x of text.matchAll(/(?:^| )map=([^ ]+)/g)){const name=x[1];if(!recognition[t][name])recognition[t][name]={turns:0,firstRound:round,firstDragon:id};recognition[t][name].turns++;}const m=/ E=([A-Z])$/.exec(text);if(m)engines[t][m[1]]=(engines[t][m[1]]||0)+1;}
  if(e.type==='dragonAction'&&e.tle)timeouts.push({round,id,team:t});
 }
 const known=Object.keys(recognition[side]).filter(k=>!['?','none','Unknown'].includes(k));
 const ourErrors=log.split('\n').filter(line=>line.includes(`(team ${side})`)&&/no reply|timed out|timeout|exceeded|error|failed|trap|unreachable|fuel|closed|exit|ran out|limit|stopped/i.test(line)&&!line.includes('died:'));
 const ourTimeouts=[...timeouts.filter(x=>x.team===side),...ourErrors.filter(line=>/time|fuel|points/i.test(line)).map(line=>({source:'runner',line}))];
 const defects=/map:\s*(\d+) defects? found and corrected/.exec(log);
 return {mapLoaded:!!R.match.map,finished:!!R.result,rounds:round+1,mapDefects:defects?+defects[1]:0,ourErrors,ourTimeouts,recognition,engines,misrecognition:known,maxCpuPerTurn:parseCpu(log),ourMaxCpuPerTurn:parseCpu(log)[side]};
}
function tasks(manifest,only=null) {return manifest.maps.filter(m=>!only||only.has(m.name)).flatMap(m=>(m.family==='X'?['A','B']:['A']).map(side=>({gameId:`mapgen:${m.name}:${side}:1`,map:m.name,mapFile:m.file,mapSha256:m.sha256,family:m.family,side,seed:1})));}
const readRows=()=>fs.existsSync(ROWS)?fs.readFileSync(ROWS,'utf8').split('\n').filter(Boolean).map(JSON.parse):[];
const append=row=>fs.appendFileSync(ROWS,JSON.stringify(row)+'\n');
async function smoke(only=null) {
 fs.mkdirSync(OUT,{recursive:true});const manifest=JSON.parse(fs.readFileSync(path.join(ROOT,'maps/generated/manifest.json'),'utf8')),all=tasks(manifest,only),rows=readRows();
 const attempted=new Set(rows.filter(r=>r.attempted&&all.some(t=>t.gameId===r.gameId&&t.mapSha256===r.mapSha256)).map(r=>r.gameId)),todo=all.filter(t=>!attempted.has(t.gameId));
 if(!todo.length){console.log(JSON.stringify({status:'already_attempted',tasks:0}));return;}
 const guard=resources();fs.writeFileSync(path.join(OUT,'resource-check.json'),JSON.stringify({at:new Date().toISOString(),...guard},null,2)+'\n');
 if(!guard.ok&&guard.reason==='process_count_unavailable'){for(const t of todo)append({...t,at:new Date().toISOString(),attempted:false,status:'blocked',mapLoaded:null,finished:null,ourErrors:null,ourTimeouts:null,ourMaxCpuPerTurn:null,recognition:null,reason:guard.reason,detail:guard.detail});console.log(JSON.stringify({status:'blocked',tasks:todo.length,reason:guard.reason,detail:guard.detail}));return;}
 const lock=path.join(OUT,'smoke.lock');let fd;try{fd=fs.openSync(lock,'wx');fs.writeSync(fd,JSON.stringify({pid:process.pid,at:new Date().toISOString()}));}catch(e){throw Error('smoke.lock exists; inspect owner before removing: '+lock);}
 try {for(const t of todo) {
  const validation=validate(read(t.mapFile),{connected:true}),onlyFrozenException=t.family==='X'&&validation.errors.every(x=>x.startsWith('generated map disconnected'));
  if(!validation.valid&&!onlyFrozenException){append({...t,at:new Date().toISOString(),attempted:false,status:'static_invalid',validation});continue;}
  if(hash(read(t.mapFile))!==t.mapSha256)throw Error('map changed since manifest: '+t.map);
  let g=resources();while(!g.ok&&g.reason!=='process_count_unavailable'){console.log(JSON.stringify({status:'waiting',gameId:t.gameId,...g}));await new Promise(r=>setTimeout(r,15000));g=resources();}
  if(!g.ok){append({...t,at:new Date().toISOString(),attempted:false,status:'blocked',reason:g.reason,detail:g.detail});break;}
  const dir=path.join(OUT,'games',t.map+'_'+t.side+'_1');fs.mkdirSync(dir,{recursive:true});
  const us=path.join(ROOT,'versions/v1.6/bot'),opp=path.join(ROOT,'bots/proxy4_king'),a=t.side==='A'?us:opp,b=t.side==='A'?opp:us;
  const args=['-n','10',path.join(ROOT,'tools/unswbc'),'run',path.join(ROOT,t.mapFile),a,b,'--sandbox','--seed','1','--no-logs','--no-draw','-o',path.join(dir,'game.replay')];
  const startedAt=new Date().toISOString(),logFile=path.join(dir,'runner.log'),output=fs.createWriteStream(logFile);
  let spawnError=null;const exit=await new Promise(resolve=>{const p=cp.spawn('nice',args,{cwd:dir,env:{...process.env,XDG_CACHE_HOME:path.join(OUT,'cache')}});p.stdout.pipe(output,{end:false});p.stderr.pipe(output,{end:false});p.on('error',e=>spawnError=String(e));p.on('close',code=>output.end(()=>resolve(code)));});
  const log=fs.readFileSync(logFile,'utf8'),row={...t,at:new Date().toISOString(),startedAt,attempted:true,status:exit===0?'completed':'runner_error',exit,launchResources:g,staticValid:validation.valid,replay:path.relative(ROOT,path.join(dir,'game.replay')),runnerLog:path.relative(ROOT,logFile),mapLoaded:null,finished:null,ourErrors:null,ourTimeouts:null,ourMaxCpuPerTurn:null,recognition:null};
  if(spawnError)row.error=spawnError;try{Object.assign(row,analyseReplay(path.join(dir,'game.replay'),t.side,log));}catch(e){row.error=String(e.message);if(exit===0)row.status='replay_error';}
  const globalFaults=log.split('\n').filter(x=>/error:|Traceback|no reply|timed out|exceeded/i.test(x));if(globalFaults.length)row.runnerFaults=globalFaults.slice(0,25);
  append(row);console.log(JSON.stringify({gameId:t.gameId,mapLoaded:row.mapLoaded,finished:row.finished,ourErrors:row.ourErrors?.length??null,ourTimeouts:row.ourTimeouts?.length??null,misrecognition:row.misrecognition,ourMaxCpuPerTurn:row.ourMaxCpuPerTurn}));
 }}finally{fs.closeSync(fd);fs.unlinkSync(lock);}
}
if(require.main===module){const args=process.argv.slice(2),i=args.indexOf('--only'),only=i>=0?new Set(args[i+1].split(',')):null;smoke(only).then(()=>require('./report').report()).catch(e=>{console.error(e.message);process.exitCode=1;});}
module.exports={resources,parseCpu,analyseReplay,tasks,readRows,smoke};
