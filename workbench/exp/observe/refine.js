'use strict';
// Supplement: realistic rate-summary packets and sampled single-process geometry.
const fs=require('fs'),path=require('path'),z=require('zlib'),crypto=require('crypto'),cp=require('child_process'),L=require('./lib');
const O=__dirname,P=JSON.parse(fs.readFileSync(path.join(O,'population.json'))),OUT=path.join(O,'supplement.jsonl.gz');
function guard(){const d=cp.execFileSync('df',['-k',L.ROOT],{encoding:'utf8'}).trim().split('\n').pop().split(/\s+/),m=/System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure',['-Q'],{encoding:'utf8'}));return +d[3]/1048576>=21&&m&&+m[1]>=10;}
function run(t){
 const f=path.join(O,'raw',crypto.createHash('sha256').update(t.key).digest('hex').slice(0,20)+'.json.gz'),a=JSON.parse(z.gunzipSync(fs.readFileSync(f))),A=L.atlas(a.M,a.gap),N=A.N,local=t.src==='local',states=new Map(),splits=new Map(a.trace.splits.map(([r,p,c])=>[c,{r,p}])),contacts=new Map(),pcs=new Map(),sendTurns=new Set(a.trace.sonarTurns.map(([r,id])=>r+':'+id));
 for(const[r,s,id]of a.trace.contacts){const k=r+':'+s;if(!contacts.has(k))contacts.set(k,[]);contacts.get(k).push(id);}
 const countdowns=new Map();for(const[r,k,c]of a.trace.countdowns){if(!countdowns.has(r))countdowns.set(r,[]);countdowns.get(r).push([k,Math.max(r,-1)+c]);}
 const expiry=new Int32Array(N).fill(-2147483647);for(const[k,e]of countdowns.get(-1)||[])expiry[k]=e;
 const countState=from=>({n:from?from.n.slice():new Uint16Array(N),sum:from?from.sum.slice():new Uint32Array(N),last:from?from.last.slice():new Int16Array(N).fill(-9),ex:from?from.ex.slice():new Int32Array(N).fill(-2147483647),ln:from?from.ln.slice():new Uint16Array(N),mx:from?from.mx.slice():new Uint16Array(N),dynMask:from?from.dynMask:7,dynFirst:null});
 function observe(C,k,r){const e=expiry[k],old=C.ex[k];if(old>0&&e>old&&r-old>=0&&r-old<=60){C.ln[k]++;C.mx[k]=Math.max(C.mx[k],e-old);}if(C.last[k]===r-1&&old===r&&e>old){C.n[k]++;C.sum[k]+=e-r;}C.last[k]=r;C.ex[k]=e;for(let h=0;h<3;h++)if(C.dynMask&(1<<h)){const m=A.syms[h](k),ex=C.ex[m];if(C.last[m]>=0&&e!==ex&&(C.last[m]===r||Math.max(r,C.last[m])<Math.min(e,ex)))C.dynMask&=~(1<<h);}}
 const union={A:countState(),B:countState()},teamKnown={A:L.knowledge(A),B:L.knowledge(A)},teamFull={A:{mask:7,first:null},B:{mask:7,first:null}};
 const make=(id,tm)=>{const p=splits.get(id),s={id,team:tm,own:L.knowledge(A),inh:L.knowledge(A,p&&states.get(p.p)?.inh),C:countState(),I:countState(p&&states.get(p.p)?.I),rn:new Uint16Array(N),rs:new Uint32Array(N),rq:new Int16Array(N).fill(-1),inbox:[],list:[],eligible:new Uint8Array(N),sent:0,resend:0,fullOwn:7,fullInh:7,fullOwnFirst:null,fullInhFirst:null};states.set(id,s);return s;};
 const rate=(C,seen,mode,gate=4)=>{let tp=0,fp=0,classified=0,rel=0,rateN=0;for(let k=0;k<N;k++){const n=mode==='packet'?Math.max(C.C.n[k],C.rn[k]):C.n[k],su=mode==='packet'&&C.rn[k]>C.C.n[k]?C.rs[k]:mode==='packet'?C.C.sum[k]:C.sum[k];if(n<gate)continue;classified++;const mu=su/n,pred=mu<=12;tp+=+(pred&&A.fount[k]);fp+=+(pred&&!A.fount[k]);rel+=Math.abs((A.gap[k][0]+A.gap[k][1])/2/mu-1);rateN++;}return {tp,fp,fountainN:L.sum(A.fount),classified,rateN,rateRelativeAbsoluteSum:rel};};
 function snap(r){
  const c=a.cp[r],live=c.processes;const rates=[],geometry=[];
  if(local)for(const p of live){if(p.team!==t.us)continue;const s=states.get(p.id);if(!s)continue;const old={tp:0,fp:0,fountainN:L.sum(A.fount)};for(let k=0;k<N;k++){const pred=s.C.ln[k]>=2?s.C.mx[k]<=12:s.C.ln[k]===1&&s.C.mx[k]<=3;if(pred){old.tp+=A.fount[k];old.fp+=+!A.fount[k];}}rates.push({id:p.id,own:rate(s.C),inherited:rate(s.I),packet:rate(s,null,'packet'),legacy:old});}
  // Deterministic probability sample: one living process per eligible team at each round.
  const eligible=t.src==='top'?['A','B'].filter(tm=>(t['rank'+tm]??999)<=10):[t.us];
  for(const tm of eligible){const pp=live.filter(p=>p.team===tm).map(p=>({p,h:crypto.createHash('sha256').update('process:'+t.key+':'+r+':'+p.id).digest('hex')})).sort((x,y)=>x.h.localeCompare(y.h)).slice(0,1);
   for(const {p}of pp){const s=states.get(p.id);if(!s)continue;const v={id:p.id,team:tm,weight:live.filter(q=>q.team===tm).length/pp.length,own:{},inherited:{}};
    for(const [mode,K]of [['own',s.own],['inherited',s.inh]]){
     const mask=mode==='own'?s.fullOwn:s.fullInh,geom=L.geometryStats(A,{...K,mask},tm),h=L.which(mask),guess=h>=0?h:(mask&4?2:mask&1?0:1),root=a.M.initialDragons.find(d=>d.id===p.root),rootStart=root?[root.body[0].y*A.W+root.body[0].x]:[],nb=L.graph(A,K.seen,'literal'),fb=L.bins(nb,rootStart,rootStart.map(A.syms[guess]));let correct=0,n=0;for(const k of K.list){n++;correct+=+(fb[k]===A.bins[tm][k]);}
     v[mode]={geometry:geom,ownRootOnlyFrontier:{correct,N:n},conditionalAllSeeds:true};
    }geometry.push(v);
   }
  }
  let unionRates=null;
  if(local){const C=union[t.us],mask=c.teams[t.us].dynamicMask,h=L.which(mask),D={n:C.n.slice(),sum:C.sum.slice()};if(h>=0)for(let k=0;k<N;k++){const m=A.syms[h](k);if(C.n[m]>C.n[k]){D.n[k]=C.n[m];D.sum[k]=C.sum[m];}}unionRates={raw:rate(C),dynamicMirrored:rate(D)};}
  const fullSymmetry={teams:{},processes:[],trueMask:1<<A.trueSym},teamCertificates={};
  for(const tm of eligible){const K=teamKnown[tm],q=teamFull[tm],D=local?union[tm]:null,mask=D?D.dynMask:q.mask;fullSymmetry.teams[tm]={mask:q.mask,first:q.first,dynamicMask:D?D.dynMask:null,dynamicFirst:D?D.dynFirst:null,mirroredCoverage:L.sum(L.expanded(A,K,q.mask))/N,dynamicMirroredCoverage:D?L.sum(L.expanded(A,K,D.dynMask))/N:null};teamCertificates[tm]={raw:L.certificateStats(A,K),mirrored:L.certificateStats(A,{...K,mask},true)};}
  for(const p of live){if(!eligible.includes(p.team))continue;const s=states.get(p.id);if(s)fullSymmetry.processes.push({id:p.id,team:p.team,own:{mask:s.fullOwn,first:s.fullOwnFirst,mirroredCoverage:L.sum(L.expanded(A,s.own,s.fullOwn))/N},inherited:{mask:s.fullInh,first:s.fullInhFirst,mirroredCoverage:L.sum(L.expanded(A,s.inh,s.fullInh))/N},dynamic:local?{mask:s.C.dynMask,first:s.C.dynFirst,mirroredCoverage:L.sum(L.expanded(A,s.own,s.C.dynMask))/N}:null});}
  pcs[r]={rates,geometry,unionRates,fullSymmetry,teamCertificates};
 }
 let round=-1;
 for(const[r,id,tm,k]of a.trace.turns){
  if(r!==round){if(L.CPS.includes(round))snap(round);round=r;if(r>200)break;for(const[v,e]of countdowns.get(r)||[])expiry[v]=e;}
  let s=states.get(id);if(!s)s=make(id,tm);for(const[v,n,su,rr]of s.inbox)if(n>s.rn[v]||n===s.rn[v]&&rr>s.rq[v]){s.rn[v]=n;s.rs[v]=su;s.rq[v]=rr;}s.inbox=[];
  for(const v of A.win[k]){L.add(A,s.own,v,r);L.add(A,s.inh,v,r);L.add(A,teamKnown[tm],v,r);if(local&&A.spawn[v]){observe(s.C,v,r);observe(s.I,v,r);observe(union[tm],v,r);}}
  s.fullOwn=L.fullStaticMask(A,s.own);s.fullInh=L.fullStaticMask(A,s.inh);if(s.fullOwnFirst===null&&L.one(s.fullOwn))s.fullOwnFirst=r;if(s.fullInhFirst===null&&L.one(s.fullInh))s.fullInhFirst=r;
  teamFull[tm].mask=L.fullStaticMask(A,teamKnown[tm]);if(teamFull[tm].first===null&&L.one(teamFull[tm].mask))teamFull[tm].first=r;
  if(local){s.C.dynMask&=s.fullOwn;s.I.dynMask&=s.fullInh;union[tm].dynMask&=teamFull[tm].mask;for(const C of [s.C,s.I,union[tm]])if(C.dynFirst===null&&L.one(C.dynMask))C.dynFirst=r;}
  const recipients=contacts.get(r+':'+id)||[];
  if(local&&sendTurns.has(r+':'+id)){for(let v=0;v<N;v++)if(Math.max(s.C.n[v],s.rn[v])>0&&!s.eligible[v]){s.eligible[v]=1;s.list.push(v);}
   if(s.list.length){let v;if(s.sent<s.list.length)v=s.list[s.sent++];else v=s.list[s.resend++%s.list.length];const n=Math.max(s.C.n[v],s.rn[v]),su=s.rn[v]>s.C.n[v]?s.rs[v]:s.C.sum[v];for(const to of recipients){let rec=states.get(to);if(!rec){const meta=a.cp[200].processes.find(p=>p.id===to);rec=make(to,meta?meta.team:tm);}rec.inbox.push([v,n,su,r]);}}
  }
 }
 if(L.CPS.includes(round)&&!pcs[round])snap(round);for(const r of L.CPS)if(!pcs[r])snap(r);
 return {key:t.key,map:t.map,layout:a.task.layout||t.layout,src:t.src,set:t.set,area:N,cp:pcs};
}
(async()=>{
 const done=new Set();if(fs.existsSync(OUT))for(const l of z.gunzipSync(fs.readFileSync(OUT)).toString().trim().split('\n'))if(l)done.add(JSON.parse(l).key);
 let n=0;for(const t of P.tasks){if(done.has(t.key))continue;while(!guard()){console.log('RESOURCE PAUSE');await new Promise(r=>setTimeout(r,30000));}fs.appendFileSync(OUT,z.gzipSync(JSON.stringify(run(t))+'\n',{level:6}));if(++n%100===0)console.log('refine',n,'/'+P.tasks.length);}
})().catch(e=>{console.error(e);process.exitCode=1;});
