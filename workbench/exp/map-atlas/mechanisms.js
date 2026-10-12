// Reuse the inherited, documented application definitions, with caches redirected by our own runner.
// Imports are read-only; no inherited command-line entry point is executed.
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process');
const ROOT=path.resolve(__dirname,'../..'),OUT=path.join(__dirname,'cache');
const raw=require(path.join(ROOT,'legacy/exp/intake-gap/rawload.js'));
const MC=require(path.join(ROOT,'legacy/tools/mech_check.js'));
const ML=require(path.join(ROOT,'legacy/tools/mass_ledger.js'));
const {resource}=require('./extract.js');
const readl=f=>fs.readFileSync(f,'utf8').split('\n').filter(Boolean).map(JSON.parse);
if(process.argv[2]==='worker'){
 process.on('message',task=>{try{
  const R=raw.load(task.file),a=MC.analyse(R,{...task,layout:task.layout==='6'?'a':task.layout,opp:String(task.oppId||'proxy4_king')},ML.perGame),by={};
  for(const r of a.recs){const v=by[r.k]||(by[r.k]={n:0,ex:0,okN:0,ok:0,sitN:0,sit:0,nat30:0,alive30N:0,alive30:0,f2N:0,f2OkN:0,f2Ok:0});
   v.n++;v.ex+=+!!r.ex;if(r.ok!==null&&r.ok!==undefined){v.okN++;v.ok+=+!!r.ok;}if(r.sit!==null&&r.sit!==undefined){v.sitN++;v.sit+=+!!r.sit;}
   v.nat30+=r.nat30||0;if(r.childAlive30!==undefined){v.alive30N++;v.alive30+=r.childAlive30;}if(r.f2){v.f2N++;if(r.ok!==null&&r.ok!==undefined){v.f2OkN++;v.f2Ok+=+!!r.ok;}}
  }
  process.send({key:task.key,row:{key:task.key,src:task.src,set:task.set,map:task.map,layout:task.layout,us:task.us,by,checks:a.chk,t5:a.t5,health:a.health,s10:a.s10,c2:a.c2,s7:a.s7}});
 }catch(e){process.send({key:task.key,error:String(e.stack)});}});
}else{
 const rows=readl(path.join(OUT,'raw.jsonl')),byKey=new Map(rows.map(r=>[r.key,r])),tasks=readl(path.join(OUT,'tasks.jsonl')).filter(t=>t.src!=='top').map(t=>({...t,layout:byKey.get(t.key).layout}));
 const f=path.join(OUT,'mechanisms.jsonl'),done=new Set(fs.existsSync(f)?readl(f).map(r=>r.key):[]),todo=tasks.filter(t=>!done.has(t.key));let i=0,n=0,busy=0,paused=false;const workers=[],start=Date.now();console.log('tasks',todo.length);
 function dispatch(w){if(paused)return;if(i===todo.length){if(!busy){for(const x of workers)x.kill();console.log('DONE',n,'seconds',(Date.now()-start)/1000);}return;}if(n%50===0){const r=resource();if(r.memory===null||r.memory<10||r.disk<20){paused=true;for(const x of workers)x.kill();console.log('PAUSED',r);process.exitCode=75;return;}}busy++;w.send(todo[i++]);}
 for(let z=0;z<2;z++){const w=cp.fork(__filename,['worker'],{execArgv:['--max-old-space-size=900'],stdio:['ignore','ignore','inherit','ipc']});workers.push(w);w.on('message',m=>{busy--;n++;if(m.error)fs.appendFileSync(path.join(OUT,'mechanism-errors.jsonl'),JSON.stringify(m)+'\n');else fs.appendFileSync(f,JSON.stringify(m.row)+'\n');if(n%100===0)console.log('progress',n,'seconds',Math.round((Date.now()-start)/1000));dispatch(w);});dispatch(w);}
}
