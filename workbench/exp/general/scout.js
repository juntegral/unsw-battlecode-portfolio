'use strict';
// Static movement feasibility of a vision-gain survey; no local games, no hidden gaps used for path selection.
const fs=require('fs'),path=require('path'),S=require('../spatial/lib'),AR=require('./atlas_recount');
const OUT=__dirname,ROOT=path.resolve(OUT,'../..'),base=JSON.parse(fs.readFileSync(path.join(ROOT,'exp/map-atlas/cache/geometry.json'))),files=fs.readdirSync(path.join(ROOT,'exp/map-atlas/cache')).filter(f=>/^geometry-.*\.json$/.test(f));
const zero=n=>Array(n).fill(0),sum=a=>a.reduce((s,v)=>s+v,0);
function survey(M,map,lay,tm){const g=S.geometry(M,map,lay),W=g.W,H=g.H,N=g.N,ix=p=>p.y*W+p.x,windows=Array.from({length:N},(_,k)=>{const a=[];for(let dy=-3;dy<=3;dy++)for(let dx=-3;dx<=3;dx++)a.push(((k/W|0)+dy+H)%H*W+(k%W+dx+W)%W);return a;}),pos=M.initialDragons.filter(d=>d.team===tm).map(d=>ix(d.body[0])),seen=new Set(),visits=zero(N),spawn=g.gap.flatMap((v,k)=>v&&v[1]>0?[k]:[]),out={};
 const G=AR.graph(M);for(let r=0;r<=50;r++){
  for(const k of pos)for(const v of windows[k])seen.add(v);
  if([0,10,20,30,50].includes(r)){
   const known=new Set(seen),optimistic=Array.from({length:N},()=>[]),pess=Array.from({length:N},()=>[]);let degreeKnown=0,kelp=0;
   for(const k of known){const vs=g.nb[k];degreeKnown+=vs.length;kelp+=4-vs.length;for(const v of vs)if(known.has(v))pess[k].push(v);}
   // Entire outgoing edge of a seen tile is visible; unknown cells are never closed by default.
   for(let k=0;k<N;k++)if(known.has(k))optimistic[k]=g.nb[k].slice();else for(const [dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]])optimistic[k].push(((k/W|0)+dy+H)%H*W+(k%W+dx+W)%W);
   const seeds=pos,enemyStarts=M.initialDragons.filter(d=>d.team!==tm).map(d=>ix(d.body[0]));const Dg=g.bfs(optimistic,seeds),Dp=g.bfs(pess,seeds),lo=Math.min(...enemyStarts.map(k=>Dg[k]<0?Infinity:Dg[k])),hi=Math.min(...enemyStarts.map(k=>Dp[k]<0?Infinity:Dp[k]));
   const core=new Set(known),degree=new Map([...known].map(k=>[k,pess[k].length])),q=[...known].filter(k=>degree.get(k)<=1);while(q.length){const k=q.pop();if(!core.delete(k))continue;for(const v of pess[k])if(core.has(v)){degree.set(v,degree.get(v)-1);if(degree.get(v)<=1)q.push(v);}}
   // A removed observed component is certified a true pocket only if every outgoing neighbour is observed and its mouth touches a seen cycle.
   const used=new Set(),certified=[];for(const k of known)if(!core.has(k)&&!used.has(k)){const comp=[k],mouth=new Set();used.add(k);let closed=true;for(let i=0;i<comp.length;i++)for(const v of g.nb[comp[i]])if(!known.has(v))closed=false;else if(core.has(v))mouth.add(v);else if(!used.has(v)){used.add(v);comp.push(v);}if(closed&&mouth.size===1)certified.push(comp);}
   const ownReach=g.bfs(g.nb,seeds),component=Array.from({length:N},(_,k)=>k).filter(k=>ownReach[k]>=0),closed=component.every(k=>seen.has(k)),matesSeen=(M.portals||[]).every(pair=>pair.every(e=>{const k=e.y%H*W+e.x%W;return !component.includes(k)||seen.has(k)&&seen.has(((e.y+H+(e.side==='N'?-1:e.side==='S'?1:0))%H)*W+(e.x+W+(e.side==='W'?-1:e.side==='E'?1:0))%W);}));out[r]={isolationCertifiableWithKnownMates:closed&&matesSeen&&enemyStarts.every(k=>ownReach[k]<0),oracleOptimisticNoRoute:!Number.isFinite(lo),seenTiles:seen.size,coverage:seen.size/N,spawnSeen:spawn.filter(k=>seen.has(k)).length,spawnSeenShare:spawn.filter(k=>seen.has(k)).length/spawn.length,meanDegreeEstimate:degreeKnown/known.size,kelpDensityEstimate:kelp/(4*known.size),certifiedPocketTiles:sum(certified.map(a=>a.length)),certifiedPocketCount:certified.length,knownCycleTiles:core.size,startDistanceLowerBound:Number.isFinite(lo)?lo:null,startDistanceUpperBound:Number.isFinite(hi)?hi:null,note:'distance uses known initial enemy head positions: symmetry/starter-sonar prerequisite; scout movement ignores bodies'};
  }
  // Local movement choices reward newly visible cells, discourage revisits; portal endpoint must already be observed.
  for(let i=0;i<pos.length;i++){const k=pos[i],x=k%W,y=k/W|0;let best=null;for(let d=0;d<4;d++){const v=G.nb[k*4+d];if(v<0)continue;const ordinary=((y+[-1,0,1,0][d]+H)%H)*W+(x+[0,1,0,-1][d]+W)%W;if(v!==ordinary&&!seen.has(v))continue;const gain=windows[v].filter(z=>!seen.has(z)).length,score=10*gain-visits[v]-.01*d;if(!best||score>best.score)best={v,score};}if(best){pos[i]=best.v;visits[best.v]++;for(const v of windows[best.v])seen.add(v);}}
 }
 return out;}
const result={status:'static feasibility upper bound, 15 layouts x 2 seats; one scout per starting head, body collision and split production omitted',maps:{}};
for(const fn of files){const v=JSON.parse(fs.readFileSync(path.join(ROOT,'exp/map-atlas/cache',fn))),M=v.M;for(const k of ['initialHEdges','initialVEdges','initialTiles'])if(!Array.isArray(M[k]))M[k]=Object.values(M[k]);const f=v.map+'/'+v.layout;if(result.maps[f])continue;result.maps[f]={A:survey(M,v.map,v.layout,'A'),B:survey(M,v.map,v.layout,'B')};}
fs.writeFileSync(path.join(OUT,'scout.json'),JSON.stringify(result,null,1));console.log('SURVEY',Object.keys(result.maps).length);
