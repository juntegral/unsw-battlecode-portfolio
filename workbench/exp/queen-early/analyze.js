#!/usr/bin/env node
'use strict';
// Offline, one process. Writes only queen-early. No matches or network.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'../..'),OUT=__dirname;
const raw=require(path.join(ROOT,'legacy/exp/intake-gap/rawload'));
const ML=require(path.join(ROOT,'tools/mass_ledger'));
const CP=[0,25,50,100,150,200,250,300,350,400,450,499];
const geomCache=new Map();
const readl=f=>fs.readFileSync(f,'utf8').split('\n').filter(Boolean).map(JSON.parse);
function disk(){const s=fs.statfsSync(ROOT);if(s.bavail*s.bsize<21*1024**3)throw Error('PAUSE: disk free below 21 GiB');return s.bavail*s.bsize;}
function geometry(M,c){
 const sha=crypto.createHash('sha256').update(JSON.stringify([M.width,M.height,M.initialHEdges,M.initialVEdges,M.portals])).digest('hex');
 if(geomCache.has(sha))return geomCache.get(sha);
 const N=c.W*c.H,nb=Array.from({length:N},()=>[]),rev=Array.from({length:N},()=>[]);
 for(let k=0;k<N;k++)for(const d of 'NESW'){const p=c.across(k%c.W,k/c.W|0,d);if(p){const n=c.key(p.x,p.y);nb[k].push(n);rev[n].push(k);}}
 const G={sha,N,W:c.W,H:c.H,nb,rev,to:new Map(),seen:new Int32Array(N),queue:new Int32Array(N),epoch:0};geomCache.set(sha,G);return G;
}
function distTo(G,k){if(G.to.has(k))return G.to.get(k);const a=new Int16Array(G.N).fill(-1),q=new Int32Array(G.N);let end=1;q[0]=k;a[k]=0;for(let i=0;i<end;i++)for(const n of G.rev[q[i]])if(a[n]<0){a[n]=a[q[i]]+1;q[end++]=n;}G.to.set(k,a);return a;}
function reach(G,c,d,target,budget){
 // Conservative path test: all current body tiles stay blocked; target head alone is permitted.
 const start=c.key(d.body[0].x,d.body[0].y);if(distTo(G,target)[start]<0||distTo(G,target)[start]>budget)return null;
 const seen=G.seen,epoch=++G.epoch,q=G.queue,depth=new Int16Array(G.N);let end=1;q[0]=start;seen[start]=epoch;depth[start]=0;
 for(let i=0;i<end;i++){const k=q[i];if(depth[k]>=budget)continue;for(const n of G.nb[k]){if(n===target)return depth[k]+1;if(seen[n]===epoch||c.occ.has(n))continue;seen[n]=epoch;depth[n]=depth[k]+1;q[end++]=n;}}return null;
}
function room(G,c,d){const k=c.key(d.body[0].x,d.body[0].y),seen=G.seen,epoch=++G.epoch,q=G.queue;let end=1;q[0]=k;seen[k]=epoch;for(let i=0;i<end;i++)for(const n of G.nb[q[i]])if(seen[n]!==epoch&&!c.occ.has(n)){seen[n]=epoch;q[end++]=n;}return end;}
function neighbours(c,d){const h=d.body[0],out=[];for(const dir of 'NESW'){const p=c.across(h.x,h.y,dir),id=p&&c.occ.get(c.key(p.x,p.y)),o=id===undefined?null:c.drag.get(id);out.push({dir,tile:p,kind:!p?'wall':id===undefined?'free':id===d.id?'self':o.team===d.team?'ally':'enemy',id:id??null,head:!!o&&o.body[0].x===p.x&&o.body[0].y===p.y});}return out;}
function lenbin(L){return L<=4?'2-4':L<=8?'5-8':L<=12?'9-12':L<=20?'13-20':'21+';}
function newQueen(id,team){return {id,team,death:null,endLength:0,maxLength:0,curve:{},turns:[],splits:[],eats:{natural:0,ownDeath:0,enemyDeath:0,labelledFeed:0},nearEnemyTurns:0,freeReachTurns:0,enemyTurnOpportunities:0,enemyFreeReach:0,exposureRounds:[],exposureExamples:[],lastDanger:null,feeds:[]};}
function extract(R,task,rules){
 const M=R.match.map,qi={};for(const d of M.initialDragons)if(d.id<=1)qi[d.team]=d.id;
 const q={A:newQueen(qi.A,'A'),B:newQueen(qi.B,'B')},actions={A:{},B:{}},history=new Map(),indicators=new Map(),feedsByDeath=new Map(),rawDeaths=new Map();
 let cur=-1,round=-1;for(const e of R.events){if(e.type==='roundStart')round=e.round;if(e.type==='turnStart')cur=e.id;if(e.type==='dragonDeath')rawDeaths.set(e.id,{reason:e.reason,round,moverId:cur});}
 let G,lastSnap=-1,currentTurn=-1;const firstLong={A:null,B:null};
 const checkpoints={};
 const res=ML.perGame(R,{map:task.map,variant:task.map==='Prisoners Dilemma'?(M.initialDragons.length===10?'PD10':'PD6'):'?',rules}, {
  turn(d,r,c){
   currentTurn=d.id;if(!G)G=geometry(M,c);
   if(CP.includes(r)&&lastSnap!==r){lastSnap=r;checkpoints[r]={};for(const tm of ['A','B']){const z=c.drag.get(qi[tm]);checkpoints[r][tm]=z?{length:z.body.length,head:{...z.body[0]},room:room(G,c,z),neighbours:neighbours(c,z)}:null;q[tm].curve[r]=z?z.body.length:0;}}
   if(d.body.length>=9&&!firstLong[d.team])firstLong[d.team]={round:r,id:d.id,length:d.body.length,queen:d.id===qi[d.team]};
   if(d.id===qi[d.team]){
    const z=q[d.team],h=d.body[0],to=distTo(G,c.key(h.x,h.y));let nearest=Infinity,tor=Infinity,ally=0,threat=0,nearestId=null;
    for(const o of c.drag.values())if(o.id!==d.id){if(o.team===d.team){if(c.tdist(h,o.body[0])<=3)ally++;}else{const dd=to[c.key(o.body[0].x,o.body[0].y)];if(dd>=0&&dd<nearest){nearest=dd;nearestId=o.id;}tor=Math.min(tor,c.tdist(h,o.body[0]));if(reach(G,c,o,c.key(h.x,h.y),rules==='123'?Math.ceil(o.body.length/4):1)!==null)threat++;}}
    z.maxLength=Math.max(z.maxLength,d.body.length);z.nearEnemyTurns+=+(nearest<=3);z.freeReachTurns+=+(threat>0);
    z.turns.push([r,d.body.length,h.x,h.y,Number.isFinite(nearest)?nearest:null,Number.isFinite(tor)?tor:null,ally,threat,d.free,nearestId]);
   }
   const enemyTm=d.team==='A'?'B':'A',queen=c.drag.get(qi[enemyTm]);
   if(queen){const z=q[enemyTm];z.enemyTurnOpportunities++;const k=c.key(queen.body[0].x,queen.body[0].y),budget=rules==='123'?Math.ceil(d.body.length/4):1,steps=reach(G,c,d,k,budget);
    if(steps!==null){z.enemyFreeReach++;if(z.exposureRounds.at(-1)!==r)z.exposureRounds.push(r);const sample={round:r,attacker:d.id,length:d.body.length,freeSteps:budget,distance:steps,head:{...d.body[0]},queenHead:{...queen.body[0]}};z.lastDanger=sample;if(z.exposureExamples.length<12)z.exposureExamples.push(sample);}
   }
  },
  indicator(e,r,c){indicators.set(e.id,{round:r,text:e.text||''});},
  action(d,e,r,c,b){
   const a=e.action,L=b.length,z=actions[d.team],bin=lenbin(L),phase=r<100?'early':r<300?'middle':'late',isQ=d.id===qi[d.team];
   const k=[bin,phase,isQ?'queen':'other'].join('/');if(!z[k])z[k]={turns:0,moves:0,splits:0,requested:{},executedSteps:0,paidSteps:0,freeBudgetSum:0,withinFree:0,multiWithinFree:0};const v=z[k];v.turns++;
   if(a&&a.kind==='move'){const steps=a.steps.length,free=rules==='123'?Math.ceil(L/4):1;v.moves++;v.requested[steps]=(v.requested[steps]||0)+1;v.executedSteps+=d.expect.length;v.paidSteps+=Math.max(0,d.expect.length-free);v.freeBudgetSum+=free;v.withinFree+=+(steps<=free);v.multiWithinFree+=+(steps>=2&&steps<=free);}else if(a&&a.kind==='split')v.splits++;
   const hh=history.get(d.id)||[];hh.push({round:r,length:L,head:{...b[0]},action:a,fate:d.fate,indicator:indicators.get(d.id)?.round===r?indicators.get(d.id).text:null});if(hh.length>12)hh.shift();history.set(d.id,hh);
  },
  split(parent,child,e,r,c){if(parent.id===qi[parent.team])q[parent.team].splits.push({round:r,before:e.parentBody.length+e.childBody.length,kept:e.parentBody.length,child:e.childBody.length,childId:child.id});},
  eat(d,k,origin,r,c){if(d.id===qi[d.team]){const z=q[d.team],cat=origin<0?'natural':c.deaths[origin].team===d.team?'ownDeath':'enemyDeath';z.eats[cat]++;if(feedsByDeath.has(origin))z.eats.labelledFeed++;}const f=feedsByDeath.get(origin);if(f){if(d.id===qi[f.team])f.byQueen++;else if(d.team===f.team)f.byOwn++;else f.byEnemy++;}},
  death(d,rec,idx,other,r,c){
   const ev=rawDeaths.get(d.id),lab=indicators.get(d.id),m=lab&&lab.round===r&&/^feed #(\d+) d(\d+) L(\d+)(.*)$/.exec(lab.text);
   if(m){const f={team:d.team,round:r,id:d.id,target:+m[1],toQueen:+m[1]===qi[d.team],queenAlive:c.drag.has(qi[d.team]),drops:rec.drops,byQueen:0,byOwn:0,byEnemy:0,label:lab.text};q[d.team].feeds.push(f);feedsByDeath.set(idx,f);}
   if(d.id!==qi[d.team])return;const z=q[d.team];const mover=ev.moverId===d.id;
   z.death={...ev,length:d.body.length,head:{...d.body[0]},role:mover?'mover':'target',category:ML.CAUSE[rec.cause],freeAtTurnStart:d.free,neighbours:neighbours(c,d),other:other?{id:other.id,team:other.team,length:other.body.length,head:{...other.body[0]},queen:other.id===qi[other.team]}:null,fate:mover?d.fate:c.drag.get(ev.moverId)?.fate,ownHistory:structuredClone(history.get(d.id)||[]),otherHistory:structuredClone(other?history.get(other.id)||[]:[]),lastDanger:z.lastDanger};
  },
  end(n,c){for(const tm of ['A','B']){const d=c.drag.get(qi[tm]);q[tm].endLength=d?d.body.length:0;q[tm].curve.end=q[tm].endLength;q[tm].endHead=d?{...d.body[0]}:null;q[tm].endRoom=d?room(G,c,d):null;}}
 });
 for(const tm of ['A','B']){
  const z=q[tm];z.aliveEnd=z.death===null;z.aliveAt500=res.rounds===500&&z.aliveEnd;
  const late=z.turns.filter(x=>x[0]>=300),unique=new Set(late.map(x=>x[2]+','+x[3]));z.lateMotion={turns:late.length,uniqueHeadTiles:unique.size,repeatFraction:late.length?1-unique.size/late.length:null};
  z.geometry=G?G.sha:null;
 }
 const w=res.winner,l=w==='A'?'B':'A';const fate=w?(!q[w].death&&!q[l].death?'both_alive':!q[w].death?'winner_only':!q[l].death?'loser_only':'both_dead'):'draw';
 return {...task,queenIds:qi,rounds:res.rounds,winner:w,endReason:res.endReason,result:R.result,fate,queens:q,actions,firstLong,checkpoints,checks:res.chk,geometry:G?G.sha:null};
}
function localTasks(){
 const tasks=[],inventory=[];
 for(const base of ['exp/q2','exp/v16/q1'])for(const dir of fs.readdirSync(path.join(ROOT,base),{withFileTypes:true}).filter(d=>d.isDirectory()).map(d=>d.name).sort()){
  const folder=base+'/'+dir,rf=path.join(ROOT,folder,'rows.jsonl');if(!fs.existsSync(rf))continue;
  const rows=readl(rf),latest=new Map(rows.map(x=>[x.key,x]));let clean=0,missing=0,excluded=0;
  for(const row of latest.values()){if(row.exit!==0||row.error||row.botProblem){excluded++;continue;}const file=folder+'/games/'+row.key.replace(/:/g,'_')+'/game.replay';if(!fs.existsSync(path.join(ROOT,file))){missing++;continue;}clean++;tasks.push({...row,key:folder+':'+row.key,localKey:row.key,cohort:folder,file,teamA:row.side==='A'?dir:path.basename(row.opp),teamB:row.side==='B'?dir:path.basename(row.opp)});}
  inventory.push({cohort:folder,rows:rows.length,uniqueKeys:latest.size,clean,missing,excluded});
 }
 return {tasks,inventory};
}
const mode=process.argv[2]||'elite';disk();
if(mode==='elite'){
 const T=JSON.parse(fs.readFileSync(path.join(OUT,'tables.json'))),games=[];
 for(const [i,t] of T.games.entries()){disk();try{const R=raw.load(path.join(ROOT,t.file));games.push(extract(R,{battleId:t.battleId,gameId:t.gameId,file:t.file,map:t.map,at:t.at,teamA:t.teamA,teamB:t.teamB,indexWinner:t.winner,rankA:t.rankA,rankB:t.rankB},'123'));}catch(e){games.push({...t,error:String(e.stack)});}if((i+1)%20===0)console.log('elite',i+1,'/',T.N);}
 T.status='1.2.3 reconstruction complete; independent verification pending';T.extractedAt=new Date().toISOString();T.games=games;fs.writeFileSync(path.join(OUT,'tables.json'),JSON.stringify(T,null,2)+'\n');console.log('elite complete',games.length);
}else if(mode==='local'){
 const {tasks,inventory}=localTasks(),games=[];for(const [i,t]of tasks.entries()){disk();try{games.push(extract(raw.load(path.join(ROOT,t.file)),t,'123'));}catch(e){games.push({...t,error:String(e.stack)});}if((i+1)%25===0)console.log('local',i+1,'/',tasks.length);}
 fs.writeFileSync(path.join(OUT,'local.json'),JSON.stringify({createdAt:new Date().toISOString(),inventory,games},null,2)+'\n');console.log('local complete',games.length);
}else if(mode==='old'){
 const T=JSON.parse(fs.readFileSync(path.join(OUT,'tables.json'))),names=new Set(T.games.flatMap(g=>[g.teamA,g.teamB]));
 const oldCutoff='2026-10-01T09:00:00Z';
 const rows=readl(path.join(ROOT,'data/elite/index.jsonl')).filter(x=>Date.parse(x.at)<Date.parse(oldCutoff)).sort((a,b)=>Date.parse(b.at)-Date.parse(a.at));
 // Up to 3 last old games per team/map. Union avoids counting a replay twice.
 const keys=new Set(),counts=new Map(),tasks=[];
 for(const r of rows){let take=false;for(const tm of ['A','B']){const name=r['team'+tm],k=name+'/'+r.map,n=counts.get(k)||0;if(names.has(name)&&n<3){counts.set(k,n+1);take=true;}}const k=r.battleId+':'+r.gameId;if(take&&!keys.has(k)){keys.add(k);tasks.push({...r,key:k,file:`data/elite/${r.battleId}/${r.gameId}.replay.gz`});}}
 const games=[];for(const [i,t]of tasks.entries()){disk();try{games.push(extract(raw.load(path.join(ROOT,t.file)),t,'110'));}catch(e){games.push({...t,error:String(e.stack)});}if((i+1)%25===0)console.log('old',i+1,'/',tasks.length);}
 fs.writeFileSync(path.join(OUT,'old.json'),JSON.stringify({createdAt:new Date().toISOString(),cutoff:oldCutoff,selection:'last up to 3 games per new-cohort team/map, before 09:00Z; union of keys. Earlier provisional 11:08Z comparator contained 180/610 old-cost reconstruction failures, earliest 09:31:54Z, and was discarded.',games},null,2)+'\n');console.log('old complete',games.length);
}
