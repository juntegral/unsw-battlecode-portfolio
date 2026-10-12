'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib'),os=require('os'),{OUT,guard,resource}=require('./setup');
const PHYSICS=['sim','splits','drops','eatTC','ledger','final','lineage','natBal','dropBal','unknownDeath'];
function header(file){return new Promise((resolve,reject)=>{
 const input=fs.createReadStream(file,{highWaterMark:8192}),gzip=zlib.createGunzip();let s='',done=false;
 const finish=(value,error)=>{if(done)return;done=true;input.destroy();gzip.destroy();error?reject(error):resolve(value);};
 input.on('error',e=>finish(null,e));gzip.on('error',e=>finish(null,e));
 gzip.on('data',b=>{s+=b.toString();const m=/"checks":(\{[^}]*\})/.exec(s);if(m)finish(JSON.parse(m[1]));});
 gzip.on('end',()=>finish(null,Error('missing cache checks '+file)));input.pipe(gzip);
});}
function atomic(file,x){const tmp=file+'.tmp';fs.writeFileSync(tmp,zlib.gzipSync(JSON.stringify(x)));fs.renameSync(tmp,file);}
async function main(){
 if(os.getPriority(0)<10)throw Error('nice >=10 required');guard();
 const P=JSON.parse(fs.readFileSync(path.join(OUT,'population.json'))),bad=[],modelsFile=path.join(OUT,'free-policies.json'),models=fs.existsSync(modelsFile)?JSON.parse(fs.readFileSync(modelsFile)):{};
 let n=0;for(const t of P.tasks){if(n++%100===0)guard();const f=path.join(OUT,'cache',t.key+'.json.gz');if(!fs.existsSync(f))continue;const c=await header(f);if(PHYSICS.some(k=>c[k]!==0))bad.push({t,before:c});if(n%1000===0)console.log('HEADER AUDIT',n+'/'+P.N,'bad',bad.length);}
 fs.writeFileSync(path.join(OUT,'calibration-before.json'),JSON.stringify({at:resource().at,N:P.N,bad},null,2));
 console.log('AUDIT COMPLETE',P.N,'bad',bad.length);
 const fixes=[];for(const {t,before}of bad){
  guard();const raw=require('../spatial/lib').raw,R=raw.load(t.file),task={...t,freePolicy:'quarter'},r=require('./lib').analyse(R,task);
  if(PHYSICS.some(k=>r.checks[k]!==0))throw Error('quarter model does not reconcile '+t.key+' '+JSON.stringify(r.checks));
  const I=require('./recount').recount(R,task),canonical=require('./verify_raw').canonical,a=r.episodes.map(canonical),b=I.map(canonical);
  if(JSON.stringify(a)!==JSON.stringify(b))throw Error('quarter episode reconstruction differs '+t.key);
  atomic(path.join(OUT,'cache',t.key+'.json.gz'),r);models[t.key]={policy:'quarter',before,after:r.checks,episodeN:r.episodes.length};
  fixes.push({game:t.key,before,after:r.checks,primaryN:a.length,independentN:b.length});console.log('FIXED',t.key,'episodes',a.length,'checks',r.checks);
 }
 const mt=modelsFile+'.tmp';fs.writeFileSync(mt,JSON.stringify(models,null,2));fs.renameSync(mt,modelsFile);
 const nowP=JSON.parse(fs.readFileSync(path.join(OUT,'population.json')));for(const t of nowP.tasks)t.freePolicy=models[t.key]?.policy||'one_fit';
 const pf=path.join(OUT,'population.json'),pt=pf+'.tmp';fs.writeFileSync(pt,JSON.stringify(nowP,null,2));fs.renameSync(pt,pf);
 fs.writeFileSync(path.join(OUT,'calibration.json'),JSON.stringify({at:resource().at,N_audited:P.N,N_fixed:fixes.length,fixes,method:'all cached physics checks audited; nonzero legacy-free-step games rebuilt with ceil(L/4), then all episode identities independently recounted'},null,2));
 fs.writeFileSync(path.join(OUT,'calibration.active'),'done');console.log('CALIBRATION DONE',fixes.length);
}
if(require.main===module)main().catch(e=>{console.error(e.stack);process.exitCode=1;});
module.exports={header,PHYSICS};
