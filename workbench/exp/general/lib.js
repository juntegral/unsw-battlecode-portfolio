'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const S=require('../spatial/lib'),IG=require('../spatial/recount'),AR=require('./atlas_recount');
const ROOT=path.resolve(__dirname,'../..'),CPS=[0,10,20,25,30,50,100,250,300,350,400,450],EARLY=[0,10,20,30,50];
const zero=n=>Array(n).fill(0),sum=a=>a.reduce((s,v)=>s+v,0),ix=(p,W)=>p.y*W+p.x;
const symFns=(W,H)=>[k=>(k/W|0)*W+W-1-k%W,k=>(H-1-(k/W|0))*W+k%W,k=>(H-1-(k/W|0))*W+W-1-k%W];
function staticFeatures(M,map,lay,g){
 const W=M.width,H=M.height,N=W*H,G=AR.graph(M),spawn=g.gap.flatMap((v,k)=>v&&v[1]>0?[k]:[]),fnt=g.fountains,reachable=zero(N).map((_,k)=>g.d.A[k]>=0||g.d.B[k]>=0),mid=k=>g.bin.A[k]===2;
 const hs=t=>M.initialDragons.filter(d=>d.team===t).map(d=>ix(d.body[0],W)),ds=g.bfs(g.nb,hs('A')),pathAB=Math.min(...hs('B').map(k=>ds[k]<0?Infinity:ds[k]));
 let boundaryOpen=0;for(let x=0;x<W;x++)boundaryOpen+=+(G.nb[x*4]>=0);for(let y=0;y<H;y++)boundaryOpen+=+(G.nb[(y*W)*4+3]>=0);
 const out={map,layout:lay,W,H,area:N,wrap:true,openBoundaryShare:boundaryOpen/(W+H),initialHeads:M.initialDragons.filter(d=>d.team==='A').length,initialMass:M.initialDragons.filter(d=>d.team==='A').reduce((s,d)=>s+d.body.length,0),passableTileShare:sum(reachable.map(Number))/N,mobileTileShare:g.nb.filter(a=>a.length>0).length/N,kelpDensity:G.kelp/(2*N),portalPairs:M.portals.length,spawnTiles:spawn.length,spawnDensity:spawn.length/N,spawnPositions:spawn.map(k=>[k%W,k/W|0]),capacity:sum(spawn.map(k=>2/sum(g.gap[k]))),fountainShare:spawn.length?fnt.length/spawn.length:0,fountainTiles:fnt.length,pocketTiles:g.core.reduce((s,v)=>s+!v,0),pocketShare:g.core.reduce((s,v)=>s+!v,0)/N,pocketCount:g.pockets.length,corridorDegree2Share:g.nb.filter(a=>a.length===2).length/N,meanDegree:sum(g.nb.map(a=>a.length))/N,startDistance:Number.isFinite(pathAB)?pathAB:null,isolated:!Number.isFinite(pathAB),middleAreaShare:g.bin.A.filter(b=>b===2).length/N,centreSpawnShare:spawn.length?spawn.filter(mid).length/spawn.length:0,centreCapacityShare:sum(spawn.map(k=>mid(k)?2/sum(g.gap[k]):0))/sum(spawn.map(k=>2/sum(g.gap[k]))),edgeSpawnShare:spawn.length?spawn.filter(k=>Math.min(k%W,W-1-k%W,k/W|0,H-1-(k/W|0))<3).length/spawn.length:0,pocketCapacityShare:sum(spawn.map(k=>!g.core[k]?2/sum(g.gap[k]):0))/sum(spawn.map(k=>2/sum(g.gap[k]))),source:'full-map reference; gaps never runtime inputs'};
 return out;
}
function analyse(R,t){
 const lay=S.identify(R,t).layout,g=S.geometry(R.match.map,t.map,lay),W=g.W,N=g.N,H=g.H,features=staticFeatures(R.match.map,t.map,lay,g),windows=Array.from({length:N},(_,k)=>{const a=[];for(let dy=-3;dy<=3;dy++)for(let dx=-3;dx<=3;dx++)a.push(((k/W|0)+dy+H)%H*W+(k%W+dx+W)%W);return a;}),sym=symFns(W,H);
 const T={};for(const tm of ['A','B'])T[tm]={cp:{},headRounds:0,eligibleHR50:0,split50:0,natural:0,pocketNatural:0,pocketHR:0,sac:[],safety:[],early:{},pings:0};
 const seen={A:new Set(),B:new Set()},individual=new Map(),earlySeen={A:zero(N),B:zero(N)},earlyHits={A:zero(N),B:zero(N)},naturalByRound=Array.from({length:51},()=>[]);
 let rr=-1,drop=false;for(const e of R.events){if(drop&&!(e.type==='tileChange'&&e.hasPearl))drop=false;if(e.type==='roundStart')rr=e.round;if(rr>50)break;if(e.type==='dragonDeath')drop=true;if(e.type==='tileChange'&&e.hasPearl&&!drop&&rr>=0)naturalByRound[rr].push(ix(e.tile,W));}
 let last=-1;const hooks={turn(d,r,ctx){
 if(r<=50){let ss=individual.get(d.id);if(!ss){ss=new Set();individual.set(d.id,ss);}for(const k of windows[ix(d.body[0],W)]){seen[d.team].add(k);ss.add(k);}}
 if(r===last)return;last=r;
 for(const tm of ['A','B']){const ds=[...ctx.drag.values()].filter(d=>d.team===tm),v=T[tm];v.headRounds+=ds.length;v.pocketHR+=ds.filter(d=>!g.core[ix(d.body[0],W)]).length;if(r<50)v.eligibleHR50+=ds.filter(d=>d.body.length>=4).length;
 if(CPS.includes(r)){const king=ds.slice().sort((a,b)=>b.body.length-a.body.length||a.id-b.id)[0];v.cp[r]={heads:ds.length,mid:ds.filter(d=>g.bin[tm][ix(d.body[0],W)]===2).length,pocket:ds.filter(d=>!g.core[ix(d.body[0],W)]).length,king:king?king.body.length:0,total:sum(ds.map(d=>d.body.length))};if(r>=300&&king&&king.body.length>=8){const o=tm==='A'?'B':'A',dist=g.bfs(g.nb,[ix(king.body[0],W)]),dmin=Math.min(...[...ctx.drag.values()].filter(d=>d.team===o).map(d=>dist[ix(d.body[0],W)]<0?999:dist[ix(d.body[0],W)]));v.safety.push([r,Math.min(dmin,999)]);}}
 if(r<=50){const mask=new Set(ds.flatMap(d=>windows[ix(d.body[0],W)]));for(const k of mask)earlySeen[tm][k]++;for(const k of naturalByRound[r])if(mask.has(k))earlyHits[tm][k]++;
 if(EARLY.includes(r)){
 // A round checkpoint includes all allied pre-turn windows; union is an upper bound on sonar sharing.
 for(const k of mask)seen[tm].add(k);const ss=seen[tm],spawn=g.gap.flatMap((v,k)=>v&&v[1]>0&&ss.has(k)?[k]:[]),cand=sym.filter(f=>{for(const k of ss)if(ss.has(f(k))&&Boolean(g.gap[k]&&g.gap[k][1])!==Boolean(g.gap[f(k)]&&g.gap[f(k)][1]))return false;return true;});
 const expanded=new Set(ss);if(cand.length===1)for(const k of ss)expanded.add(cand[0](k));const symSpawn=g.gap.flatMap((v,k)=>v&&v[1]>0&&expanded.has(k)?[k]:[]),edgeN=2*ss.size,kelp=sum([...ss].map(k=>{const x=k%W,y=k/W|0,M=R.match.map;return +(M.initialHEdges[y*W+x]===1||y===0&&M.initialHEdges[H*W+x]===1)+ +(M.initialVEdges[y*(W+1)+x]===1||x===0&&M.initialVEdges[y*(W+1)+W]===1);}));
 const exposure=sum(spawn.map(k=>earlySeen[tm][k])),hits=sum(spawn.map(k=>earlyHits[tm][k]));v.early[r]={seenTiles:ss.size,coverage:ss.size/N,symmetryCandidates:cand.length,symmetryExpandedCoverage:expanded.size/N,spawnSeen:spawn.length,spawnSeenShare:features.spawnTiles?spawn.length/features.spawnTiles:null,spawnSymmetrySeen:symSpawn.length,spawnDensityEstimate:spawn.length/ss.size,kelpDensityEstimate:kelp/edgeN,capacitySeenOracle:sum(spawn.map(k=>2/sum(g.gap[k]))),capacitySeenShare:features.capacity?sum(spawn.map(k=>2/sum(g.gap[k])))/features.capacity:null,capacityExtrapolatedOracle:N/ss.size*sum(spawn.map(k=>2/sum(g.gap[k]))),successfulSpawnHits:hits,spawnerVisibleRounds:exposure,successfulRatePerVisibleSpawner:exposure?hits/exposure:null,capacitySuccessfulProxy:exposure?N*spawn.length/ss.size*hits/exposure:null,individualCoverageMax:Math.max(0,...ds.map(d=>(individual.get(d.id)||new Set()).size/N)),individualCoverageMean:ds.length?sum(ds.map(d=>(individual.get(d.id)||new Set()).size/N))/ds.length:null};
 }
 }
 }
 },split(p,ch,e,r){if(r<50)T[p.team].split50++;},eat(d,k,o,r){if(o<0){T[d.team].natural++;T[d.team].pocketNatural+=+!g.core[k];}},death(d,rec){if(rec.cause===0)T[d.team].sac.push([rec.r,rec.len]);}};
 const sonarTeam=new Map(R.match.map.initialDragons.map(d=>[d.id,d.team])),sonarPings={A:0,B:0};for(const e of R.events)if(e.type==='dragonSplit')sonarTeam.set(e.childId,e.team);for(const [id,n]of R.sonarBySender||[])sonarPings[sonarTeam.get(id)]+=n;const L=S.ML.perGame(R,{map:t.map,variant:lay==='10'?'PD10':lay},hooks),A=AR.reconstruct(R,t);
 const check={...L.chk};for(const tm of ['A','B']){const v=T[tm],a=A[tm];v.pings=sonarPings[tm];v.lin=L[tm].lin;v.final={king:L[tm].st.king[50],heads:L[tm].st.units[50]};v.sacBins=zero(50);for(const [r]of v.sac)v.sacBins[Math.min(49,r/10|0)]++;
 const comp={pings:+(v.pings!==a.pings),checkpoint:0,splits50:+(v.split50!==a.phase[0].splits),eligibleHR50:+(v.eligibleHR50!==a.phase[0].eligibleHR),natural:+(v.natural!==sum(a.phase.map(p=>p.nat))),sac:+(JSON.stringify(v.sac)!==JSON.stringify(a.sac.map(s=>s.slice(0,2)))),line:0};for(const [r,c]of Object.entries(v.cp))if(a.cp[r])for(const field of ['heads','mid','pocket','king','total'])comp.checkpoint+=+(c[field]!==a.cp[r][field]);if(v.lin&&v.lin.cp[300]){const e=v.lin.cp[300].eat;comp.line+=+(e[S.ML.ORIG.indexOf('oSac')]!==a.line.lateEat[1]);comp.line+=+(v.lin.cp[300].Lt!==a.line.lens[300]);}
 v.independent={pings:a.pings,cp:a.cp,split50:a.phase[0].splits,eligibleHR50:a.phase[0].eligibleHR,natural:sum(a.phase.map(p=>p.nat)),sac:a.sac.map(s=>s.slice(0,2)),line300:a.line.lens[300],lineSacEat300:a.line.lateEat[1]};v.compare=comp;
 }
 const stalled=L.rounds>=100?['A','B'].filter(tm=>T[tm].pings===0&&L[tm].splits<=3):[];
 return {...t,file:undefined,layout:lay,featuresKey:t.map+'/'+lay,features,rounds:L.rounds,winner:R.result.winner||null,endReason:R.result.endReason,stall:stalled,check,A:T.A,B:T.B};
}
module.exports={analyse,ROOT,S,IG,AR,staticFeatures};
