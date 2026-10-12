'use strict';
const L=require('./lib');
function analyse(R,task){
 if(task.src!=='local')task.layout=L.S.identify(R,task).layout;
 if(task.layout==='?')throw Error('ambiguous layout '+task.key);
 const {a:gap,file:mapFile}=L.gaps(task,R.match.map),A=L.atlas(R.match.map,gap),N=A.N;
 const exact=R.events.some(e=>e.type==='pearlCountdown'),expiry=new Int32Array(N).fill(-2147483647),team={},states=new Map(),lifetimes=[],cp={},trace={turns:[],splits:[],contacts:[],countdowns:[]};
 const chk={sonarHit:0,sonarTeam:0,staticFalseDecision:0,dynamicFalseDecision:0,zeroCandidates:0,gapMismatch:0},sonar={A:{sent:0,delivered:0,self:0,enemy:0,lost:0},B:{sent:0,delivered:0,self:0,enemy:0,lost:0}};
 if(exact)for(let k=0;k<N;k++){const g=R.match.map.pearlRespawn[k];if(g&&(g.minRounds!==gap[k][0]||g.maxRounds!==gap[k][1]))chk.gapMismatch++;}
 for(const t of 'AB')team[t]={K:L.knowledge(A),C:L.countdownState(N)};
 const newState=(d,parent)=>{
  const s={id:d.id,team:d.team,born:d.born||0,root:parent?parent.root:d.id,own:L.knowledge(A),inherited:L.knowledge(A,parent&&parent.inherited),patch:L.knowledge(A),C:L.countdownState(N),summaryMask:7,summaryFirst:null,inbox:[],packet:null,turnSeq:0,packetSeq:-1};
  if(parent&&L.one(s.inherited.mask))s.inherited.first=d.born;
  states.set(s.id,s);return s;
 };
 for(const d of R.match.map.initialDragons)newState(d,null);
 const maskCount=m=>+(!!(m&1))+(!!(m&2))+(!!(m&4));
 const modelStats=(K,mask=K.mask)=>({seen:K.list.length,coverage:K.list.length/N,mirroredSeen:L.sum(L.expanded(A,K,mask)),mask,candidates:maskCount(mask)});
 function checkpoint(r,ctx,censored=false){
  const out={censored,teams:{},processes:[]};
  for(const t of 'AB'){
   const {K,C}=team[t],v={...modelStats(K),dynamicMask:exact?C.mask:null,dynamicFirst:exact?C.first:null,first:K.first,spawnSeen:L.sum(K.list.map(k=>A.spawn[k])),fountainSeen:L.sum(K.list.map(k=>A.fount[k])),spawnMirrored:L.sum(Array.from(L.expanded(A,K),(v,k)=>v*A.spawn[k])),fountainMirrored:L.sum(Array.from(L.expanded(A,K),(v,k)=>v*A.fount[k])),seenMask:L.encodeSeen(K.seen),geometry:L.geometryStats(A,K,t),rates:exact?Object.fromEntries(L.GATES.map(g=>[g,L.rateStats(A,C,K.seen,g)])):null};
   if(exact){v.dynamicMirroredSeen=L.sum(L.expanded(A,K,C.mask));v.oldFountain={tp:0,fp:0};for(const k of K.list){const pred=C.samples[k]>=2?C.max[k]<=12:C.samples[k]===1&&C.max[k]<=3;if(pred){v.oldFountain.tp+=A.fount[k];v.oldFountain.fp+=+!A.fount[k];}}}
   out.teams[t]=v;
  }
  if(ctx&&!censored)for(const d of ctx.drag.values()){
   const s=states.get(d.id);if(!s)continue;
   const v={id:s.id,team:s.team,born:s.born,root:s.root,age:r-s.born,own:modelStats(s.own),inherited:modelStats(s.inherited),patch:modelStats(s.patch),summary:modelStats(s.own,s.summaryMask)};
   if(exact){v.dynamic=modelStats(s.own,s.C.mask);v.rates=Object.fromEntries([2,4].map(g=>[g,L.rateStats(A,s.C,s.own.seen,g)]));}
   out.processes.push(v);
  }
  cp[r]=out;
 }
 let round=-1,ctxRef=null,maxRound=-1;
 const hooks={turn(d,r,ctx){ctxRef=ctx;let s=states.get(d.id);if(!s)s=newState(d,null);s.turnSeq++;
  for(const q of s.inbox){if(q.tile!==null)L.add(A,s.patch,q.tile,r);s.summaryMask&=q.mask;}s.inbox=[];
  const k=d.body[0].y*A.W+d.body[0].x;trace.turns.push([r,d.id,d.team,k]);
  for(const v of A.win[k]){
   L.add(A,s.own,v,r);L.add(A,s.inherited,v,r);L.add(A,s.patch,v,r);L.add(A,team[d.team].K,v,r);
   if(exact&&A.spawn[v]&&expiry[v]!==-2147483647){L.observeCountdown(A,s.C,s.own,v,r,expiry[v]);L.observeCountdown(A,team[d.team].C,team[d.team].K,v,r,expiry[v]);}
  }
  if(exact){s.C.mask&=s.own.mask;team[d.team].C.mask&=team[d.team].K.mask;if(s.C.first===null&&L.one(s.C.mask))s.C.first=r;if(team[d.team].C.first===null&&L.one(team[d.team].C.mask))team[d.team].C.first=r;}
  s.summaryMask&=s.own.mask;if(s.summaryFirst===null&&L.one(s.summaryMask))s.summaryFirst=r;
 },split(p,ch,e,r){const ps=states.get(p.id);newState(ch,ps);trace.splits.push([r,p.id,ch.id]);},death(d,rec){const s=states.get(d.id);if(s){lifetimes.push({id:s.id,team:s.team,born:s.born,death:rec.r,ownFirst:s.own.first,inheritedFirst:s.inherited.first,patchFirst:s.patch.first,summaryFirst:s.summaryFirst,dynamicFirst:exact?s.C.first:null,ownMask:s.own.mask});states.delete(s.id);}},end(r,ctx){ctxRef=ctx;}};
 const original=R.events;
 function* events(){for(const e of original){
  if(e.type==='roundStart'){if(L.CPS.includes(round))checkpoint(round,ctxRef);round=e.round;maxRound=Math.max(maxRound,round);}
  if(e.type==='pearlCountdown'){const k=e.tile.y*A.W+e.tile.x;expiry[k]=Math.max(-1,round)+e.countdown;trace.countdowns.push([round,k,e.countdown]);}
  if(e.type==='sonarPing'){
   const s=states.get(e.senderId),d=ctxRef&&ctxRef.drag.get(e.senderId);if(s){const st=sonar[s.team];st.sent++;
    if(s.packetSeq!==s.turnSeq){const K=s.patch;let tile=null;if(K.list.length){if(K.sentCursor<K.list.length)tile=K.list[K.sentCursor++];else tile=K.list[(K.resendCursor++)%K.list.length];}s.packet={tile,mask:s.summaryMask};s.packetSeq=s.turnSeq;}
    let hit=e.hitId;if(hit===undefined&&e.end&&ctxRef)hit=ctxRef.occ.get(e.end.y*A.W+e.end.x);
    const receiver=states.get(hit),live=ctxRef&&ctxRef.drag.get(hit),hk=e.hitKind;
    if(!d||!receiver||!live||hk==='empty'||hk==='kelp'){st.lost++;}
    else if(receiver.team!==s.team){st.enemy++;if(hk&&hk!=='enemy'&&hk!=='enemyHead')chk.sonarTeam++;}
    else if(hit===s.id){st.self++;}
    else{
     st.delivered++;if(hk&&hk!=='ally'&&hk!=='allyHead')chk.sonarTeam++;
     if(e.end&&ctxRef.occ.get(e.end.y*A.W+e.end.x)!==hit)chk.sonarHit++;
     receiver.inbox.push(s.packet);trace.contacts.push([round,s.id,hit,s.packet.tile,s.packet.mask]);
    }
   }
  }
  yield e;
 }}
 R.events=events();const ledger=L.S.ML.perGame(R,{map:task.map,variant:task.layout==='10'?'PD10':task.layout},hooks);R.events=original;
 if(L.CPS.includes(round)&&!cp[round])checkpoint(round,ctxRef);
 for(const r of L.CPS)if(!cp[r])checkpoint(r,ctxRef,true);
 for(const s of states.values())lifetimes.push({id:s.id,team:s.team,born:s.born,death:null,censoredAt:maxRound,ownFirst:s.own.first,inheritedFirst:s.inherited.first,patchFirst:s.patch.first,summaryFirst:s.summaryFirst,dynamicFirst:exact?s.C.first:null,ownMask:s.own.mask});
 const trueBit={x:2,y:1,xy:4}[R.match.map.symmetry];
 for(const c of Object.values(cp))for(const v of Object.values(c.teams)){if(v.mask===0)chk.zeroCandidates++;if(L.one(v.mask)&&!(v.mask&trueBit))chk.staticFalseDecision++;if(exact&&L.one(v.dynamicMask)&&!(v.dynamicMask&trueBit))chk.dynamicFalseDecision++;}
 const eligible=task.src==='top'?['A','B'].filter(t=>(task['rank'+t]??999)<=10):[task.us];
 return {row:{...task,file:undefined,mapFile,area:N,W:A.W,H:A.H,layout:task.layout,truth:{spawnTiles:L.sum(A.spawn),fountainTiles:L.sum(A.fount),pocketTiles:N-L.sum(A.core),symmetry:R.match.map.symmetry,staticSymmetries:A.truthMask,portalPairs:R.match.map.portals.length,capacity:L.sum(gap.map(g=>g[1]>0?2/(g[0]+g[1]):0))},eligible,exactCountdowns:exact,rounds:maxRound+1,winner:R.result.winner,checks:{...ledger.chk,...chk},sonar,cp,lifetimes},audit:{key:task.key,task,M:R.match.map,gap,trace,cp,checks:ledger.chk}};
}
module.exports={analyse};
