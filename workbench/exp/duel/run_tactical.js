'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib'),cp=require('child_process'),os=require('os'),{OUT,guard}=require('./setup');
if(process.argv[2]==='worker')process.on('message',t=>{
 try{
  const R=require('../spatial/lib').raw.load(t.file),x=require('./tactical').tactical(R,t);
  if(require('./calibrate').PHYSICS.some(k=>x.checks[k]!==0))throw Error('unreconciled tactical physics '+t.key);
  const f=path.join(OUT,'tactical-cache',t.key+'.json.gz'),tmp=f+'.tmp';fs.writeFileSync(tmp,zlib.gzipSync(JSON.stringify(x)));fs.renameSync(tmp,f);
  process.send({key:t.key,N:x.records.length});
 }catch(e){process.send({key:t.key,error:e.stack});}
});
else if(require.main===module)(async()=>{
 if(os.getPriority(0)<10)throw Error('nice >=10 required');guard();fs.mkdirSync(path.join(OUT,'tactical-cache'),{recursive:true});
 const P=JSON.parse(fs.readFileSync(path.join(OUT,'population.json'))),todo=P.tasks.filter(t=>!fs.existsSync(path.join(OUT,'tactical-cache',t.key+'.json.gz')));
 if(process.argv.includes('--custom-smoke')||process.argv.includes('--custom-all')){
  todo.sort((a,b)=>Number(b.custom)-Number(a.custom));
  if(process.argv.includes('--custom-smoke'))todo.splice(50);else{const k=todo.findIndex(t=>!t.custom);if(k>=0)todo.splice(k);}
 }
 const rawDone=()=>fs.existsSync(path.join(OUT,'raw-complete.flag'))&&fs.readFileSync(path.join(OUT,'raw-complete.flag'),'utf8')==='done';
 const adaptive=process.argv.includes('--adaptive'),base=process.argv.includes('--single')?1:adaptive&&rawDone()?3:2;
 let i=0,n=0,busy=0,stop=false,start=Date.now();if(!todo.length)return;
 fs.writeFileSync(path.join(OUT,'tactical.pid'),String(process.pid));
 await new Promise((resolve,reject)=>{
  const ws=[];
  function fail(e){if(stop)return;stop=true;ws.forEach(w=>w.kill());reject(e);}
  function next(w){
   if(stop)return;if(i===todo.length){if(!busy){stop=true;ws.forEach(w=>w.kill());resolve();}return;}
   try{if(n%10===0)fs.appendFileSync(path.join(OUT,'resources.jsonl'),JSON.stringify(guard())+'\n');}catch(e){fail(e);return;}
   busy++;w.send(todo[i++]);
  }
  function spawn(){
   const w=cp.fork(__filename,['worker'],{execArgv:['--max-old-space-size=1400'],stdio:['ignore','ignore','inherit','ipc']});ws.push(w);
   w.on('message',m=>{
    busy--;n++;if(m.error){fail(Error(m.error));return;}
    if(n%100===0)console.log('TACTICAL',n+'/'+todo.length,'sec',Math.round((Date.now()-start)/1000));
    if(adaptive&&ws.length<3&&rawDone()&&i<todo.length){console.log('RAW FINISHED; tactical pool expands to 3');spawn();}
    next(w);
   });
   w.on('error',fail);w.on('exit',(code,signal)=>{if(!stop)fail(Error('unexpected tactical worker exit '+code+' '+signal));});next(w);
  }
  for(let k=0;k<Math.min(base,todo.length);k++)spawn();
 });
 console.log('TACTICAL DONE',n);
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
