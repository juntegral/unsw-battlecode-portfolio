'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process'),zlib=require('zlib'),readline=require('readline'),crypto=require('crypto');
const L=require('./lib'),O=__dirname;
function guard(){const m=/System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure',['-Q'],{encoding:'utf8'})),d=cp.execFileSync('df',['-k',L.ROOT],{encoding:'utf8'}).trim().split('\n').pop().split(/\s+/);return {memoryFreePct:m?+m[1]:0,diskGiB:+d[3]/1048576};}
function safe(){const v=guard();return v.memoryFreePct>=10&&v.diskGiB>=21;}
async function freeze(){
 const pf=path.join(O,'population.json');if(fs.existsSync(pf))return JSON.parse(fs.readFileSync(pf));
 const layouts=new Map(),gf=path.join(L.ROOT,'exp/general/games.jsonl.gz');
 for await(const line of readline.createInterface({input:fs.createReadStream(gf).pipe(zlib.createGunzip()),crlfDelay:Infinity})){const r=JSON.parse(line);if(r.src==='top')layouts.set(r.key,r.layout);}
 const top=L.S.readl(path.join(L.ROOT,'data/top/index.jsonl')),strata=new Map();let missingRank=0,missingLayout=0;
 for(const r of top){if(!['A','B'].some(t=>r['rank'+t]!=null&&r['rank'+t]<=10)){missingRank++;continue;}const layout=layouts.get(r.battleId+':'+r.gameId);if(!layout||layout==='?'){missingLayout++;continue;}
  const key=r.battleId+':'+r.gameId,st=r.map+'/'+layout;if(!strata.has(st))strata.set(st,[]);strata.get(st).push({...r,key,layout,src:'top',file:path.join(L.ROOT,'data/top',String(r.battleId),r.gameId+'.replay.gz'),hash:crypto.createHash('sha256').update('observe-20261001:'+key).digest('hex')});
 }
 const tasks=[],selection={};for(const[st,rs]of strata){rs.sort((a,b)=>a.hash.localeCompare(b.hash));const chosen=rs.slice(0,64);selection[st]={poolN:rs.length,sampleN:chosen.length};tasks.push(...chosen);}
 const EX=require('../spatial/extract');for(const set of [...L.S.WAVE,'v1-w1','v1-w2','v1-w3']){const dir=path.join(L.ROOT,'data/online',set);if(fs.existsSync(path.join(dir,'index.json')))tasks.push(...EX.onlineTasks(dir));}
 for(const set of ['v12-F-H','v12-F-K','v12-S-H','v12-S-K']){
  const dir=path.join(L.ROOT,'exp/gen',set,'games');for(const name of fs.readdirSync(dir)){const file=path.join(dir,name,'game.replay');if(!fs.existsSync(file))continue;const m=/^(proxy4_\w+?)_(.*?)_([AB])_(\d+)$/.exec(name);if(!m)throw Error('local name '+name);const slug=m[2],map=Object.keys(L.S.MAPS).find(k=>L.S.MAPS[k]===slug)||slug,mapFile=path.join(L.ROOT,set.endsWith('-K')?'maps/online-20260927':'maps/bundled',slug+'.map');tasks.push({key:set+':'+name,src:'local',set,map,layout:map==='Prisoners Dilemma'?'6':'a',mapFile,us:m[3],opp:m[1],seed:+m[4],file});}
 }
 tasks.sort((a,b)=>(a.src==='local'?0:a.src==='online'?1:2)-(b.src==='local'?0:b.src==='online'?1:2)||a.key.localeCompare(b.key));
 const p={frozenAt:new Date().toISOString(),method:'all four W1 sets + all 18 online sets + SHA256 sample 64 games per top-10 map/layout, both eligible sides; layouts from prior metadata, independently checked on extraction',selection,topPoolN:top.length,missingRank,missingLayout,resource:guard(),tasks,missing:tasks.filter(t=>!fs.existsSync(t.file)).map(t=>t.key)};
 fs.writeFileSync(pf,JSON.stringify(p,null,1));return p;
}
if(process.argv[2]==='worker'){
 const raw=require('./raw'),{analyse}=require('./analyse');process.on('message',t=>{try{const R=raw.load(t.file),v=analyse(R,{...t});fs.writeFileSync(path.join(O,'raw',crypto.createHash('sha256').update(t.key).digest('hex').slice(0,20)+'.json.gz'),zlib.gzipSync(JSON.stringify(v.audit),{level:6}));process.send({key:t.key,row:v.row});}catch(e){process.send({key:t.key,error:e.stack});}});
}else(async()=>{
 while(!safe()){console.log('RESOURCE PAUSE',guard());await new Promise(r=>setTimeout(r,30000));}
 fs.mkdirSync(path.join(O,'raw'),{recursive:true});const p=await freeze(),done=new Set(),file=path.join(O,'games.jsonl.gz');
 if(fs.existsSync(file))for await(const l of readline.createInterface({input:fs.createReadStream(file).pipe(zlib.createGunzip()),crlfDelay:Infinity}))if(l)done.add(JSON.parse(l).key);
 let todo=p.tasks.filter(t=>!done.has(t.key)&&fs.existsSync(t.file));if(process.argv[2]==='one')todo=todo.slice(0,1);
 console.log('START',new Date().toISOString(),'total',p.tasks.length,'todo',todo.length,guard());if(!todo.length)return;
 const workers=[],start=Date.now();let next=0,busy=0,n=0,stop=false,paused=false;
 function dispatch(w){if(stop)return;if(next===todo.length){if(!busy){stop=true;console.log('DONE',n,'seconds',(Date.now()-start)/1000);for(const x of workers)x.kill();}return;}
  if(!safe()){if(!paused){paused=true;console.log('RESOURCE PAUSE',guard());}setTimeout(()=>dispatch(w),30000);return;}if(paused){paused=false;console.log('RESOURCE RESUME',guard());}busy++;w.send(todo[next++]);
 }
 for(let i=0;i<Math.min(2,todo.length);i++){const w=cp.fork(__filename,['worker'],{execArgv:['--max-old-space-size=1100'],stdio:['ignore','ignore','inherit','ipc']});workers.push(w);w.on('message',m=>{busy--;n++;if(m.error)fs.appendFileSync(path.join(O,'errors.jsonl'),JSON.stringify(m)+'\n');else fs.appendFileSync(file,zlib.gzipSync(JSON.stringify(m.row)+'\n',{level:6}));if(n%25===0)console.log('progress',n+'/'+todo.length,'sec',Math.round((Date.now()-start)/1000),guard());dispatch(w);});w.on('exit',(c,s)=>{if(!stop&&n<todo.length){stop=true;console.error('worker exit',c,s);for(const x of workers)x.kill();process.exitCode=1;}});dispatch(w);}
})().catch(e=>{console.error(e);process.exitCode=1;});
module.exports={guard,freeze};
