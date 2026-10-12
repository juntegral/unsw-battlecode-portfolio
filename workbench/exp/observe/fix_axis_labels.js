'use strict';
const fs=require('fs'),path=require('path'),z=require('zlib'),readline=require('readline'),crypto=require('crypto'),cp=require('child_process'),L=require('./lib');
const O=__dirname,input=path.join(O,'games.jsonl.gz'),output=path.join(O,'games-axis.jsonl.gz');
function guard(){const d=cp.execFileSync('df',['-k',L.ROOT],{encoding:'utf8'}).trim().split('\n').pop().split(/\s+/),m=/System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure',['-Q'],{encoding:'utf8'}));return +d[3]/1048576>=21&&m&&+m[1]>=10;}
function localOrbits(row,a){
 const A=L.atlas(a.M,a.gap),N=A.N,calendar=new Map(),ex=new Int32Array(N).fill(-2147483647),states=new Map(),make=()=>({last:new Int16Array(N).fill(-9),old:new Int32Array(N).fill(-2147483647),orbits:new Set()}),teams={A:make(),B:make()};
 for(const[r,k,c]of a.trace.countdowns){if(!calendar.has(r))calendar.set(r,[]);calendar.get(r).push([k,Math.max(-1,r)+c]);}for(const[k,e]of calendar.get(-1)||[])ex[k]=e;
 function obs(C,k,r){if(C.last[k]===r-1&&C.old[k]===r&&ex[k]>r)C.orbits.add(r*N+Math.min(k,A.syms[A.trueSym](k)));C.last[k]=r;C.old[k]=ex[k];}
 function snap(r){const c=row.cp[r];for(const tm of 'AB')for(const q of Object.values(c.teams[tm].rates))q.orbitSamples=teams[tm].orbits.size;for(const p of c.processes)for(const q of Object.values(p.rates))q.orbitSamples=states.get(p.id).orbits.size;a.cp[r]=c;}
 let rr=-1;for(const[r,id,tm,k]of a.trace.turns){if(r!==rr){if(L.CPS.includes(rr))snap(rr);rr=r;if(r>200)break;for(const[v,e]of calendar.get(r)||[])ex[v]=e;}let C=states.get(id);if(!C){C=make();states.set(id,C);}for(const v of A.win[k])if(A.spawn[v]){obs(C,v,r);obs(teams[tm],v,r);}}
 if(L.CPS.includes(rr))snap(rr);for(const r of L.CPS)if(r>rr)snap(r);
}
(async()=>{
 if(fs.existsSync(output))throw Error('review existing axis output before re-run');let n=0,oldStatic=0,oldDynamic=0,newStatic=0,newDynamic=0;
 for await(const line of readline.createInterface({input:fs.createReadStream(input).pipe(z.createGunzip()),crlfDelay:Infinity})){
  while(!guard()){console.log('RESOURCE PAUSE');await new Promise(r=>setTimeout(r,30000));}const row=JSON.parse(line),f=path.join(O,'raw',crypto.createHash('sha256').update(row.key).digest('hex').slice(0,20)+'.json.gz'),a=JSON.parse(z.gunzipSync(fs.readFileSync(f))),bit={x:2,y:1,xy:4}[a.M.symmetry];oldStatic+=row.checks.staticFalseDecision;oldDynamic+=row.checks.dynamicFalseDecision;
  row.checks.staticFalseDecision=0;row.checks.dynamicFalseDecision=0;for(const c of Object.values(row.cp))for(const v of Object.values(c.teams)){if(L.one(v.mask)&&!(v.mask&bit))row.checks.staticFalseDecision++;if(v.dynamicMask!==null&&L.one(v.dynamicMask)&&!(v.dynamicMask&bit))row.checks.dynamicFalseDecision++;}
  if(row.src==='local')localOrbits(row,a);newStatic+=row.checks.staticFalseDecision;newDynamic+=row.checks.dynamicFalseDecision;
  const tmp=f+'.tmp';fs.writeFileSync(tmp,z.gzipSync(JSON.stringify(a),{level:6}));fs.renameSync(tmp,f);fs.appendFileSync(output,z.gzipSync(JSON.stringify(row)+'\n',{level:6}));if(++n%200===0)console.log('axis',n);
 }
 fs.renameSync(output,input);const report={at:new Date().toISOString(),games:n,issue:'map-file y means reflection about y axis, x-coordinate flip; x means x-axis/y-coordinate flip. Geometry/candidate numbering was correct; diagnostic truth bits and reset-orbit deduplication labels were inverted.',originalDiagnostic:{static:oldStatic,dynamic:oldDynamic},correctedDiagnostic:{static:newStatic,dynamic:newDynamic},scope:'no trajectories, observed windows, candidate masks, gap estimates or frontier guesses changed'};fs.writeFileSync(path.join(O,'axis-label-correction.json'),JSON.stringify(report,null,1));console.log('DONE',report);
})().catch(e=>{console.error(e);process.exitCode=1;});
