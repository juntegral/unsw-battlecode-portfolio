'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'../..'),S=require('../spatial/lib');
const CPS=[0,5,10,20,25,30,50,100,200],DX=[0,1,0,-1],DY=[-1,0,1,0],BIT=[1,2,4],GATES=[1,2,4,8];
const sum=a=>a.reduce((s,v)=>s+v,0),one=m=>m===1||m===2||m===4,which=m=>m===1?0:m===2?1:m===4?2:-1;
function gaps(task,M){
 let file=task.mapFile;
 if(!file){const slug=S.MAPS[task.map];file=path.join(ROOT,task.layout==='b'||task.layout==='10'?'maps/server-b':'maps/online-20260927',slug+(task.layout==='b'?'_b':task.layout==='10'?'_10':'')+'.map');}
 const lines=fs.readFileSync(file,'utf8').split('\n'),a=Array.from({length:M.width*M.height},()=>[0,0]);
 for(const l of lines)if(l.startsWith('TILE ')){const[x,y,mn,mx]=l.split(/\s+/).slice(1).map(Number);a[y*M.width+x]=[mn,mx];}
 return {a,file:path.relative(ROOT,file)};
}
function atlas(M,gap){
 const W=M.width,H=M.height,N=W*H,wrap=(x,y)=>((y%H+H)%H)*W+(x%W+W)%W,step=(k,d)=>wrap(k%W+DX[d],(k/W|0)+DY[d]);
 const eid=(k,d)=>d===0?k:d===1?N+step(k,1):d===2?step(k,2):N+k;
 const kind=new Uint8Array(2*N),partner=new Int32Array(2*N).fill(-1),pairId=new Int16Array(2*N).fill(-1);
 for(let k=0;k<N;k++){const x=k%W,y=k/W|0;kind[k]=+(M.initialHEdges[k]===1||y===0&&M.initialHEdges[N+x]===1);kind[N+k]=+(M.initialVEdges[y*(W+1)+x]===1||x===0&&M.initialVEdges[y*(W+1)+W]===1);}
 const canon=p=>eid(wrap(p.x,p.y),'NESW'.indexOf(p.side));
 for(let i=0;i<M.portals.length;i++){const[a,b]=M.portals[i].map(canon);kind[a]=kind[b]=2;partner[a]=b;partner[b]=a;pairId[a]=pairId[b]=i;}
 const syms=[k=>(k/W|0)*W+W-1-k%W,k=>(H-1-(k/W|0))*W+k%W,k=>(H-1-(k/W|0))*W+W-1-k%W],md=[[0,3,2,1],[2,1,0,3],[2,3,0,1]],edgeSym=syms.map((f,h)=>{const a=new Int32Array(2*N);for(let k=0;k<N;k++)for(const d of [0,3])a[eid(k,d)]=eid(f(k),md[h][d]);return a;});
 const win=Array.from({length:N},(_,k)=>{const a=[];for(let dy=-3;dy<=3;dy++)for(let dx=-3;dx<=3;dx++)a.push(wrap(k%W+dx,(k/W|0)+dy));return a;});
 const spawn=gap.map(g=>+(g[1]>0)),fount=gap.map(g=>+(g[1]>0&&(g[0]+g[1])/2<=12)),starts={};for(const t of 'AB')starts[t]=M.initialDragons.filter(d=>d.team===t).map(d=>d.body[0].y*W+d.body[0].x);
 const bodies={};for(const t of 'AB')bodies[t]=M.initialDragons.filter(d=>d.team===t).flatMap(d=>d.body.map(p=>p.y*W+p.x));
 const A={W,H,N,wrap,step,eid,kind,partner,pairId,syms,md,edgeSym,win,spawn,fount,gap,starts,bodies,portalEdges:Array.from(kind,(v,k)=>v===2?k:-1).filter(k=>k>=0),trueSym:{x:1,y:0,xy:2}[M.symmetry]};
 A.trueGraph=graph(A,new Uint8Array(N).fill(1),'open');A.core=core(A.trueGraph);A.bins={};A.bodyBins={};for(const t of 'AB'){A.bins[t]=bins(A.trueGraph,starts[t],starts[t==='A'?'B':'A']);A.bodyBins[t]=bins(A.trueGraph,bodies[t],bodies[t==='A'?'B':'A']);}
 A.truthMask=7;for(let h=0;h<3;h++)for(let k=0;k<N;k++)if(spawn[k]!==spawn[syms[h](k)]||[0,1,2,3].some(d=>kind[eid(k,d)]!==kind[eid(syms[h](k),md[h][d])])){A.truthMask&=~BIT[h];break;}
 return A;
}
function edgeMask(A,seen){const out=new Uint8Array(2*A.N);for(let k=0;k<A.N;k++)if(seen[k])for(let d=0;d<4;d++)out[A.eid(k,d)]=1;return out;}
function graph(A,seen,mode,resolved=null){
 const {N,kind,partner}=A,known=edgeMask(A,seen),nb=Array.from({length:N},()=>[]);let unresolved=0;
 for(let k=0;k<N;k++)for(let d=0;d<4;d++){
  const e=A.eid(k,d);let v=-1;
  if(!known[e]){if(mode==='open'||mode==='literal')v=A.step(k,d);}
  else if(kind[e]===0)v=A.step(k,d);
  else if(kind[e]===2){const p=partner[e];if(p>=0&&known[p]&&(!resolved||resolved[e])){const t=p%N;v=d===0?A.step(t,0):d===3?A.step(t,3):t;}else{unresolved++;if(mode==='literal')v=A.step(k,d);else if(mode==='open'){
    // Possible destinations are unknown edges of the same orientation (or unresolved synthetic portal ends).
    // A fully inspected ordinary/kelp edge cannot secretly be the missing portal end.
    const offset=d%2===0?0:N,possible=new Set(nb[k]);
    for(let j=offset;j<offset+N;j++)if(!known[j]||kind[j]===2&&resolved&&!resolved[j]){
     const t=j%N,v=d===0?A.step(t,0):d===3?A.step(t,3):t;if(v!==k)possible.add(v);
    }
    nb[k]=Array.from(possible);
   }}}
  if(v>=0&&!nb[k].includes(v))nb[k].push(v);
 }
 nb.unresolvedPortals=unresolved;return nb;
}
function bfs(nb,seeds){const ds=new Int32Array(nb.length).fill(-1),q=[];for(const k of seeds)if(ds[k]<0){ds[k]=0;q.push(k);}for(let i=0;i<q.length;i++)for(const v of nb[q[i]])if(ds[v]<0){ds[v]=ds[q[i]]+1;q.push(v);}return ds;}
function bins(nb,ours,theirs){const a=bfs(nb,ours),b=bfs(nb,theirs);return Array.from(a,(v,k)=>v<0&&b[k]<0?5:v<0?4:b[k]<0?0:Math.min(4,Math.floor(5*(v+b[k]===0?.5:v/(v+b[k])))));}
function core(nb){const und=nb.map(a=>new Set(a));for(let k=0;k<nb.length;k++)for(const v of nb[k])und[v].add(k);const live=new Uint8Array(nb.length).fill(1),deg=und.map(a=>a.size),q=[];for(let k=0;k<deg.length;k++)if(deg[k]<=1)q.push(k);for(let i=0;i<q.length;i++){const k=q[i];if(!live[k])continue;live[k]=0;for(const v of und[k])if(live[v]&&--deg[v]<=1)q.push(v);}return live;}
function knowledge(A,from){return {seen:from?from.seen.slice():new Uint8Array(A.N),edges:from?from.edges.slice():new Uint8Array(2*A.N),list:from?from.list.slice():[],mask:from?from.mask:7,first:null,sentCursor:0,resendCursor:0};}
function add(A,K,k,r){
 if(K.seen[k])return false; // Static edges/support were already fully ingested for this tile.
 const fresh=!K.seen[k];if(fresh){K.seen[k]=1;K.list.push(k);}for(let d=0;d<4;d++)K.edges[A.eid(k,d)]=1;
 for(let h=0;h<3;h++)if(K.mask&BIT[h]){
  const m=A.syms[h](k);if(K.seen[m]&&A.spawn[k]!==A.spawn[m]){K.mask&=~BIT[h];continue;}
  for(let d=0;d<4;d++){const e=A.eid(k,d),me=A.edgeSym[h][e];if(K.edges[me]&&A.kind[e]!==A.kind[me]){K.mask&=~BIT[h];break;}
   // Portal identifiers are not assumed to survive mirroring or fit a one-tile patch.
  }
 }
 if(K.first===null&&one(K.mask))K.first=r;
 return fresh;
}
function expanded(A,K,mask=K.mask){const v=K.seen.slice(),h=which(mask);if(h>=0)for(const k of K.list)v[A.syms[h](k)]=1;return v;}
function rateStats(A,K,seen,gate){
 let tp=0,fp=0,fn=0,classified=0,spawnSeen=0,knownFount=0,rateN=0,relativeSum=0,relativeSq=0,trueSeenRate=0,estimatedRate=0,resetSamples=0;
 for(let k=0;k<A.N;k++)if(seen[k]&&A.spawn[k]){spawnSeen++;knownFount+=A.fount[k];const mu=(A.gap[k][0]+A.gap[k][1])/2;trueSeenRate+=1/mu;const n=K.samples[k];resetSamples+=n;
  if(n>=gate){classified++;const mean=K.sums[k]/n,pred=mean<=12;tp+=+(pred&&A.fount[k]);fp+=+(pred&&!A.fount[k]);const rel=(1/mean)/(1/mu)-1;rateN++;relativeSum+=Math.abs(rel);relativeSq+=rel*rel;estimatedRate+=1/mean;}
 }
 const orbitSamples=new Set((K.events||[]).map(([r,k])=>r*A.N+Math.min(k,A.syms[A.trueSym](k)))).size;
 fn=sum(A.fount)-tp;return {gate,tp,fp,fn,classified,spawnSeen,fountainSeen:knownFount,resetSamples,orbitSamples,rateN,rateRelativeAbsoluteSum:relativeSum,rateRelativeSquaredSum:relativeSq,trueSeenRate,estimatedRate};
}
function countdownState(N){return {expiry:new Int32Array(N).fill(-2147483647),last:new Int16Array(N).fill(-9),samples:new Uint16Array(N),sums:new Uint32Array(N),max:new Uint16Array(N),mask:7,first:null,events:[]};}
function observeCountdown(A,C,K,k,r,expiry){
 const old=C.expiry[k];if(C.last[k]===r-1&&old===r&&expiry>old){const g=expiry-r;C.samples[k]++;C.sums[k]+=g;C.max[k]=Math.max(C.max[k],g);C.events.push([r,k,g]);}
 C.last[k]=r;C.expiry[k]=expiry;
 C.mask&=K.mask;
 for(let h=0;h<3;h++)if(C.mask&BIT[h]){const m=A.syms[h](k);if(C.last[m]<0)continue;const ex=C.expiry[m];if(expiry!==ex&&(C.last[m]===r||Math.max(r,C.last[m])<Math.min(expiry,ex)))C.mask&=~BIT[h];}
 if(C.first===null&&one(C.mask))C.first=r;
}
function geometryStats(A,K,t){
 const out={};for(const [label,seen]of [['raw',K.seen],['mirrored',expanded(A,K)]]){
  const physical=edgeMask(A,K.seen),resolved=new Uint8Array(2*A.N);for(let e=0;e<resolved.length;e++)if(A.kind[e]===2&&physical[e]&&physical[A.partner[e]])resolved[e]=1;
  if(label==='mirrored'&&one(K.mask))for(let e=0;e<resolved.length;e++)if(resolved[e])resolved[A.edgeSym[which(K.mask)][e]]=1;
  const open=graph(A,seen,'open',resolved),wall=graph(A,seen,'wall',resolved),literal=graph(A,seen,'literal',resolved);
  const po=core(open),pw=core(wall),counts=c=>{let tp=0,fp=0;for(let k=0;k<A.N;k++)if(seen[k]&&!c[k]){tp+=+!A.core[k];fp+=+!!A.core[k];}return {tp,fp,fn:A.N-sum(A.core)-tp,predicted:tp+fp,evaluated:sum(seen)};};
  const h=which(K.mask),guess=h>=0?h:(K.mask&4?2:K.mask&1?0:1),enemy=A.starts[t].map(A.syms[guess]),fb=bins(literal,A.starts[t],enemy),oracle=bins(literal,A.starts[t],A.starts[t==='A'?'B':'A']),matrix=Array.from({length:6},()=>Array(6).fill(0));
  let correct=0,oracleCorrect=0,bodyCorrect=0,knownN=0,spawnN=0,spawnCorrect=0,fountainN=0,fountainCorrect=0,reachableN=0,reachableCorrect=0;
  for(let k=0;k<A.N;k++)if(seen[k]){knownN++;const good=+(fb[k]===A.bins[t][k]);correct+=good;oracleCorrect+=+(oracle[k]===A.bins[t][k]);bodyCorrect+=+(fb[k]===A.bodyBins[t][k]);matrix[A.bins[t][k]][fb[k]]++;spawnN+=A.spawn[k];spawnCorrect+=A.spawn[k]*good;fountainN+=A.fount[k];fountainCorrect+=A.fount[k]*good;reachableN+=+(A.bins[t][k]!==5);reachableCorrect+=+(A.bins[t][k]!==5)*good;}
  out[label]={optimistic:counts(po),certified:certifiedCounts(A,seen,open,po,resolved),pessimistic:counts(pw),literalOptimistic:counts(core(literal)),unresolvedPortalDirections:open.unresolvedPortals,frontier:{correct,oracleEnemyCorrect:oracleCorrect,bodyReferenceCorrect:bodyCorrect,N:knownN,spawnN,spawnCorrect,fountainN,fountainCorrect,reachableN,reachableCorrect,matrix,guessedSymmetry:guess,decided:h>=0,enemyStartCorrect:JSON.stringify(enemy.slice().sort((a,b)=>a-b))===JSON.stringify(A.starts[t==='A'?'B':'A'].slice().sort((a,b)=>a-b))}};
 }
 return out;
}
function fullStaticMask(A,K){let mask=K.mask;for(let h=0;h<3;h++)if(mask&(1<<h))for(const e of A.portalEdges)if(K.edges[e]){const me=A.edgeSym[h][e];if(A.kind[me]!==2||!K.edges[me]||!K.edges[A.partner[e]]||!K.edges[A.partner[me]])continue;if(A.edgeSym[h][A.partner[e]]!==A.partner[me]){mask&=~(1<<h);break;}}return mask;}
function certifiedCounts(A,seen,nb,co,resolved){
 const known=edgeMask(A,seen),und=nb.map(a=>new Set(a));for(let k=0;k<A.N;k++)for(const v of nb[k])und[v].add(k);const visited=new Uint8Array(A.N);let tp=0,fp=0;
 for(let k=0;k<A.N;k++)if(!co[k]&&!visited[k]){const q=[k];visited[k]=1;let closed=true;for(let i=0;i<q.length;i++){const u=q[i];for(let d=0;d<4;d++){const e=A.eid(u,d);if(!known[e]||A.kind[e]===2&&!resolved[e])closed=false;}for(const v of und[u])if(!co[v]&&!visited[v]){visited[v]=1;q.push(v);}}
  if(closed)for(const u of q)if(seen[u]){tp+=+!A.core[u];fp+=+!!A.core[u];}
 }
 return {tp,fp,fn:A.N-sum(A.core)-tp,predicted:tp+fp,evaluated:sum(seen)};
}
function certificateStats(A,K,mirror=false){const seen=mirror?expanded(A,K):K.seen,physical=edgeMask(A,K.seen),resolved=new Uint8Array(2*A.N);for(let e=0;e<2*A.N;e++)if(A.kind[e]===2&&physical[e]&&physical[A.partner[e]])resolved[e]=1;if(mirror&&one(K.mask))for(let e=0;e<2*A.N;e++)if(resolved[e])resolved[A.edgeSym[which(K.mask)][e]]=1;const nb=graph(A,seen,'open',resolved);return certifiedCounts(A,seen,nb,core(nb),resolved);}
function encodeSeen(a){return Buffer.from(a).toString('base64');}
module.exports={ROOT,S,CPS,GATES,sum,one,which,gaps,atlas,graph,bfs,bins,core,knowledge,add,expanded,countdownState,observeCountdown,rateStats,geometryStats,certificateStats,fullStaticMask,encodeSeen};
