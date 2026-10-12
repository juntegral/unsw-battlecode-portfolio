#!/usr/bin/env node
'use strict';
// Independent reconstruction: trust replay head/tail updates, never simulate movement costs.
const fs=require('fs'),path=require('path');const ROOT=path.resolve(__dirname,'../..');
const raw=require(path.join(ROOT,'legacy/exp/intake-gap/rawload'));
const lenbin=L=>L<=4?'2-4':L<=8?'5-8':L<=12?'9-12':L<=20?'13-20':'21+';
function geom(M){const W=M.width,H=M.height,wx=x=>(x+W)%W,wy=y=>(y+H)%H,port=new Map(),nb=new Int32Array(W*H*4).fill(-1);
 const canon=e=>e.side==='S'?{x:e.x,y:wy(e.y+1),side:'N'}:e.side==='E'?{x:wx(e.x+1),y:e.y,side:'W'}:e;
 for(const p of M.portals||[]){const a=canon(p[0]),b=canon(p[1]);port.set(`${a.x},${a.y},${a.side}`,b);port.set(`${b.x},${b.y},${b.side}`,a);}
 for(let k=0;k<W*H;k++){const x=k%W,y=k/W|0;for(let z=0;z<4;z++){const horizontal=z===0||z===2,ex=z===1?wx(x+1):x,ey=z===2?wy(y+1):y,p=port.get(`${ex},${ey},${horizontal?'N':'W'}`);
 const wall=horizontal?(M.initialHEdges[ey*W+ex]===1||(ey===0&&M.initialHEdges[H*W+ex]===1)):(M.initialVEdges[ey*(W+1)+ex]===1||(ex===0&&M.initialVEdges[ey*(W+1)+W]===1));
 if(p)nb[k*4+z]=(z===0?wy(p.y-1):p.y)*W+(z===3?wx(p.x-1):p.x);else if(!wall)nb[k*4+z]=wy(y+[ -1,0,1,0][z])*W+wx(x+[0,1,0,-1][z]);}}
 return {W,H,nb};}
function direct(R,rules){
 const M=R.match.map,G=geom(M),key=p=>p.y*G.W+p.x,drag=new Map(),occ=new Map(),all=new Map(),qi={},q={},actions={A:{},B:{}},deaths=[];
 let r=-1,cur=-1,turnRec=null,exposures={A:0,B:0},opps={A:0,B:0};
 const clear=d=>{for(const k of d.body)if(occ.get(k)===d.id)occ.delete(k);},put=d=>{for(const k of d.body)occ.set(k,d.id);};
 const add=(id,team,body)=>{const d={id,team,body:body.map(key),steps:[],updates:0};drag.set(id,d);all.set(id,d);put(d);return d;};
 for(const d of M.initialDragons){add(d.id,d.team,d.body);if(d.id<=1){qi[d.team]=d.id;q[d.team]={id:d.id,death:null,turns:[],splits:[]};}}
 function reachable(d,target,budget){const seen=new Set([d.body[0]]),queue=[[d.body[0],0]];for(let i=0;i<queue.length;i++){const [k,depth]=queue[i];if(depth===budget)continue;for(let z=0;z<4;z++){const n=G.nb[k*4+z];if(n<0)continue;if(n===target)return true;if(!seen.has(n)&&!occ.has(n)){seen.add(n);queue.push([n,depth+1]);}}}return false;}
 function closeTurn(){if(turnRec){turnRec.v.executedSteps+=turnRec.d.updates;turnRec.v.paidSteps+=Math.max(0,turnRec.d.updates-turnRec.free);turnRec=null;}}
 for(const e of R.events){
  if(e.type==='roundStart')r=e.round;
  else if(e.type==='turnStart'){
   closeTurn();cur=e.id;const d=drag.get(cur);d.steps=[];d.updates=0;
   if(d.id===qi[d.team])q[d.team].turns.push([r,d.body.length,d.body[0]%G.W,d.body[0]/G.W|0]);
   const tm=d.team==='A'?'B':'A',z=drag.get(qi[tm]);if(z){opps[tm]++;exposures[tm]+=+reachable(d,z.body[0],rules==='123'?Math.ceil(d.body.length/4):1);}
  }else if(e.type==='dragonAction'){
   const d=drag.get(e.id),a=e.action,L=d.body.length,k=[lenbin(L),r<100?'early':r<300?'middle':'late',d.id===qi[d.team]?'queen':'other'].join('/'),z=actions[d.team];
   if(!z[k])z[k]={turns:0,moves:0,splits:0,requested:{},executedSteps:0,paidSteps:0,freeBudgetSum:0,withinFree:0,multiWithinFree:0};const v=z[k];v.turns++;
   if(a&&a.kind==='move'){d.steps=a.steps;const free=rules==='123'?Math.ceil(L/4):1;v.moves++;v.requested[d.steps.length]=(v.requested[d.steps.length]||0)+1;v.freeBudgetSum+=free;v.withinFree+=+(d.steps.length<=free);v.multiWithinFree+=+(d.steps.length>=2&&d.steps.length<=free);turnRec={v,d,free};}else if(a&&a.kind==='split')v.splits++;
  }else if(e.type==='dragonUpdate'){
   if(r<0)continue;const d=drag.get(e.id);clear(d);const h=key(e.head),tail=key(e.tail);if(d.body[0]!==h)d.body.unshift(h);while(d.body.length>1&&d.body.at(-1)!==tail)d.body.pop();d.updates++;put(d);
  }else if(e.type==='dragonSplit'){
   const d=drag.get(e.parentId);if(d.id===qi[d.team])q[d.team].splits.push({round:r,before:e.parentBody.length+e.childBody.length,kept:e.parentBody.length,child:e.childBody.length,childId:e.childId});clear(d);d.body=e.parentBody.map(key);put(d);add(e.childId,e.team,e.childBody);
  }else if(e.type==='dragonDeath'){
   const d=drag.get(e.id);let other=null;
   if(cur!==e.id)other=all.get(cur);
   else if(e.reason==='H'){const prev=deaths.at(-1);if(prev&&prev.r===r)other=all.get(prev.id);}
   else if(e.reason==='O'){const z='NESW'.indexOf(d.steps[d.updates]),k=z<0?-1:G.nb[d.body[0]*4+z];other=all.get(occ.get(k));}
   if(d.id===qi[d.team])q[d.team].death={round:r,reason:e.reason,moverId:cur,length:d.body.length,head:{x:d.body[0]%G.W,y:d.body[0]/G.W|0},otherId:other?other.id:null,otherTeam:other?other.team:null};
   deaths.push({id:d.id,r});clear(d);drag.delete(e.id);
  }
 }
 closeTurn();const final={};for(const tm of ['A','B']){const ds=[...drag.values()].filter(d=>d.team===tm);final[tm]={dragonCount:ds.length,longestDragon:Math.max(0,...ds.map(d=>d.body.length)),totalLength:ds.reduce((s,d)=>s+d.body.length,0)};const z=drag.get(qi[tm]);q[tm].endLength=z?z.body.length:0;}
 return {rounds:r+1,qi,q,final,actions,exposures,opps};
}
const mode=process.argv[2]||'elite',file=mode==='elite'?'tables.json':mode+'.json';const T=JSON.parse(fs.readFileSync(path.join(__dirname,file))),checks={games:0,queenTeam:0,fates:0,death:0,other:0,length:0,turns:0,splits:0,final:0,actions:0,reach:0,opportunities:0},diff=[],fates={},reasons={},deciders={},rawWrong={winnerAlive:0,loserAlive:0};
for(const [i,g]of T.games.entries()){
 const s=fs.statfsSync(ROOT);if(s.bavail*s.bsize<21*1024**3)throw Error('PAUSE disk');if(g.error)continue;
 const z=direct(raw.load(path.join(ROOT,g.file)),mode==='old'?'110':'123');checks.games++;
 const bad=(cat,detail)=>{checks[cat]++;if(diff.length<30)diff.push({game:g.gameId||g.key,cat,detail});};
 for(const tm of ['A','B']){const a=g.queens[tm],b=z.q[tm];if(a.id!==b.id)bad('queenTeam',tm);if(!!a.death!==!!b.death)bad('fates',tm);
  if(a.endLength!==b.endLength)bad('length',[tm,a.endLength,b.endLength]);
  if(JSON.stringify(a.turns.map(x=>x.slice(0,4)))!==JSON.stringify(b.turns))bad('turns',tm);
  if(JSON.stringify(a.splits)!==JSON.stringify(b.splits))bad('splits',tm);
  if(a.death&&b.death){for(const k of ['round','reason','moverId','length','head'])if(JSON.stringify(a.death[k])!==JSON.stringify(b.death[k]))bad('death',[tm,k,a.death[k],b.death[k]]);if((a.death.other?.id??null)!==b.death.otherId||(a.death.other?.team??null)!==b.death.otherTeam)bad('other',tm);reasons[b.death.reason]=(reasons[b.death.reason]||0)+1;}
  for(const k of ['dragonCount','longestDragon','totalLength'])if(z.final[tm][k]!==g.result['team'+tm][k])bad('final',[tm,k]);
  if(JSON.stringify(z.actions[tm])!==JSON.stringify(g.actions[tm]))bad('actions',tm);
  if(a.enemyFreeReach!==z.exposures[tm])bad('reach',tm);if(a.enemyTurnOpportunities!==z.opps[tm])bad('opportunities',tm);
 }
 const w=g.winner,l=w==='A'?'B':'A';const fate=w?(!z.q[w].death&&!z.q[l].death?'both_alive':!z.q[w].death?'winner_only':!z.q[l].death?'loser_only':'both_dead'):'draw';fates[fate]=(fates[fate]||0)+1;
 if(w){const assumed=w==='A'?0:1;rawWrong.winnerAlive+=+!Object.values(z.q).find(a=>a.id===assumed).death;rawWrong.loserAlive+=+!Object.values(z.q).find(a=>a.id===1-assumed).death;}
 let decider=null,computed=null;if(g.endReason==='teamEliminated'){decider='elimination';computed=z.final.A.dragonCount===0?(z.final.B.dragonCount===0?null:'B'):'A';}else{for(const k of mode==='old'?['longestDragon','totalLength']:['queen','longestDragon','totalLength']){const a=k==='queen'?z.q.A.endLength:z.final.A[k],b=k==='queen'?z.q.B.endLength:z.final.B[k];if(a!==b){decider=k;computed=a>b?'A':'B';break;}}if(!decider)decider='draw';}deciders[decider]=(deciders[decider]||0)+1;if(computed!==w)bad('final',['winner',computed,w,decider]);
 if((i+1)%50===0)console.log('verify',mode,i+1,'/',T.games.length);
}
const out={createdAt:new Date().toISOString(),method:'independent replay head/tail updates, splits, deaths; no move cost simulation; separate occupancy BFS',checks,diff,fates,reasons,deciders,rawWrong};fs.writeFileSync(path.join(__dirname,'verify-'+mode+'.json'),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
module.exports={direct,geom};
