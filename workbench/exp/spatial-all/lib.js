// Spatial occupancy study. Read-only replay reconstruction; caches live under exp/spatial.
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'../..');
const ML=require(path.join(ROOT,'tools/mass_ledger.js'));
const raw=require(path.join(ROOT,'legacy/exp/intake-gap/rawload.js'));
const MAPS={'Autarky':'autarky','Default':'default','Devil':'devil','Portals':'portals','Prisoners Dilemma':'prisoners_dilemma','Queen Of Spades':'queen_of_spades','Schooltime':'schooltime','Slithery Fight':'slithery_fight','Trauma':'trauma','Trophy':'trophy'};
const SELECT=new Set(['Devil','Queen Of Spades','Schooltime','Slithery Fight','Prisoners Dilemma','Default','Trauma','Trophy','Autarky','Portals']); // exp/spatial-all (coordinator 04:30): all ten maps
const TWO=new Set(['Devil','Queen Of Spades','Schooltime','Slithery Fight']);
const WAVE=['cand-merge2-online','cand-merge2-online-r2','cand-merge2-online-r3',...Array.from({length:6},(_,i)=>`cand-stack${i+1}-online`),'cand-stack6-online-r2',...Array.from({length:5},(_,i)=>`cand-stack${i+7}-online`)];
const EARLY=['baseline-r1','baseline-r1b','baseline-r1c','cand-avoid6-online','cand-portal1-online','cand-swarm8-online','base-px8-online','base-px9d-online','px-king-v2-online'];
const CPS=[25,50,100,250,375],PHASES=[[0,99],[100,249],[250,374],[375,499]],BINS=[[0,.2],[.2,.4],[.4,.6],[.6,.8],[.8,1]];
const zero=(n=6)=>Array(n).fill(0),matrix=(n=4,m=6)=>Array.from({length:n},()=>zero(m));
const phase=r=>r<100?0:r<250?1:r<375?2:3;
const sum=a=>a.reduce((s,v)=>s+v,0),readl=f=>fs.existsSync(f)?fs.readFileSync(f,'utf8').split('\n').filter(Boolean).map(JSON.parse):[];
let assign=null;
function gaps(map,lay){const slug=MAPS[map],f=path.join(ROOT,lay==='b'||lay==='10'?'maps/variants':'maps/online-20260927',slug+(lay==='b'?'_b':lay==='10'?'_10':'')+'.map');const lines=fs.readFileSync(f,'utf8').split('\n'),[W,H]=lines[0].split(/\s+/).slice(1).map(Number),a=Array(W*H).fill(null);for(const l of lines)if(l.startsWith('TILE ')){const[x,y,mn,mx]=l.split(/\s+/).slice(1).map(Number);a[y*W+x]=[mn,mx];}return a;}
const gapCache=new Map();
function getGaps(m,l){const k=m+'/'+l;if(!gapCache.has(k))gapCache.set(k,gaps(m,l));return gapCache.get(k);}
function identify(R,task){
 if(task.localLayout)return {layout:task.localLayout,evidence:'local directory/map table'};
 if(task.map==='Prisoners Dilemma')return {layout:R.match.map.initialDragons.length===10?'10':'6',evidence:'initial dragon count (both teams)'};
 if(!TWO.has(task.map))return {layout:'a',evidence:'single layout'};
 const ga=getGaps(task.map,'a'),gb=getGaps(task.map,'b'),W=R.match.map.width;let ca=0,cb=0,drop=false;
 for(const e of R.events){if(e.type==='dragonDeath'){drop=true;continue;}if(e.type==='tileChange'&&e.hasPearl){if(!drop){const k=e.tile.y*W+e.tile.x;ca+=+(!ga[k]||ga[k][1]===0);cb+=+(!gb[k]||gb[k][1]===0);}continue;}drop=false;}
 if(assign===null){assign={};const f=path.join(ROOT,'data/pearl_layout/variants.json');if(fs.existsSync(f))for(const c of Object.values(JSON.parse(fs.readFileSync(f,'utf8')).cats))Object.assign(assign,c.assign||{});}
 const a=assign['g'+task.gameId],layout=ca<cb?'a':cb<ca?'b':a==='a'||a==='b'?a:'?';
 return {layout,ca,cb,evidence:ca!==cb?'natural spawn support':layout==='?'?'ambiguous':'inherited assignment on support tie'};
}
const geoCache=new Map();
function geometry(M,map,layout){
 const signature=crypto.createHash('sha256').update(JSON.stringify([map,layout,M.width,M.height,M.initialHEdges,M.initialVEdges,M.portals,M.initialDragons.map(d=>[d.team,d.body])])).digest('hex');
 if(geoCache.has(signature))return geoCache.get(signature);
 const W=M.width,H=M.height,N=W*H,wx=x=>(x%W+W)%W,wy=y=>(y%H+H)%H,nb=Array.from({length:N},()=>[]),rev=Array.from({length:N},()=>[]),ports=new Map();
 const canonical=e=>e.side==='S'?{x:e.x,y:wy(e.y+1),side:'N'}:e.side==='E'?{x:wx(e.x+1),y:e.y,side:'W'}:e;
 for(const pair of M.portals||[]){const[a,b]=pair.map(canonical);ports.set(`${a.x},${a.y},${a.side}`,b);ports.set(`${b.x},${b.y},${b.side}`,a);}
 for(let k=0;k<N;k++){const x=k%W,y=k/W|0;for(let d=0;d<4;d++){const hor=d%2===0,ex=d===1?wx(x+1):x,ey=d===2?wy(y+1):y,p=ports.get(`${ex},${ey},${hor?'N':'W'}`),wall=hor?(M.initialHEdges[ey*W+ex]===1||ey===0&&M.initialHEdges[H*W+ex]===1):(M.initialVEdges[ey*(W+1)+ex]===1||ex===0&&M.initialVEdges[ey*(W+1)+W]===1);let v=-1;if(p)v=(d===0?wy(p.y-1):p.y)*W+(d===3?wx(p.x-1):p.x);else if(!wall)v=wy(y+[ -1,0,1,0 ][d])*W+wx(x+[0,1,0,-1][d]);if(v>=0&&!nb[k].includes(v)){nb[k].push(v);rev[v].push(k);}}}
 const bfs=(adj,seeds)=>{const ds=new Int16Array(N).fill(-1),q=new Int32Array(N);let n=0;for(const k of seeds)if(ds[k]<0){ds[k]=0;q[n++]=k;}for(let i=0;i<n;i++)for(const v of adj[q[i]])if(ds[v]<0){ds[v]=ds[q[i]]+1;q[n++]=v;}return ds;};
 const d={};for(const t of ['A','B'])d[t]=bfs(nb,M.initialDragons.filter(x=>x.team===t).flatMap(x=>x.body.map(p=>p.y*W+p.x)));
 const f={A:[],B:[]},bin={A:[],B:[]};
 for(const t of ['A','B']){const o=t==='A'?'B':'A';for(let k=0;k<N;k++){const a=d[t][k],b=d[o][k];let q=a<0&&b<0?null:a<0?1:b<0?0:a+b===0?.5:a/(a+b);f[t].push(q);bin[t].push(q===null?5:Math.min(4,Math.floor(q*5)));}}
 // 2-core uses distinct neighbours in the undirected passable graph, including portals.
 const und=nb.map((a,k)=>[...new Set([...a,...rev[k]])]),core=new Uint8Array(N).fill(1),degree=und.map(a=>a.length),q=[];
 for(let k=0;k<N;k++)if(degree[k]<=1)q.push(k);while(q.length){const k=q.pop();if(!core[k])continue;core[k]=0;for(const v of und[k])if(core[v]&&--degree[v]<=1)q.push(v);}
 const pockets=[],component=new Int32Array(N).fill(-1),mouths=[];
 for(let k=0;k<N;k++)if(!core[k]&&component[k]<0){const tiles=[k],mouth=new Set(),id=pockets.length;component[k]=id;for(let i=0;i<tiles.length;i++)for(const v of und[tiles[i]])if(core[v])mouth.add(v);else if(component[v]<0){component[v]=id;tiles.push(v);}const m=[...mouth];mouths.push(...m);pockets.push({id,tiles,mouth:m});}
 const mouthDist=bfs(rev,[...new Set(mouths)]),nearestPocket=new Int16Array(N).fill(-1);for(const p of pockets){if(!p.mouth.length)continue;const ds=bfs(rev,p.mouth);for(let k=0;k<N;k++)if(ds[k]>=0&&ds[k]<=4&&ds[k]===mouthDist[k]&&nearestPocket[k]<0)nearestPocket[k]=p.id;}const gap=layout==='?'?Array(N).fill(null):getGaps(map,layout),fountains=[];
 for(let k=0;k<N;k++)if(gap[k]&&gap[k][1]>0&&(gap[k][0]+gap[k][1])/2<=12)fountains.push(k);
 const man=(a,b)=>{const dx=Math.abs(a%W-b%W),dy=Math.abs((a/W|0)-(b/W|0));return Math.min(dx,W-dx)+Math.min(dy,H-dy);};
 // Fountain groups: unique anchor-centred radius-3 fountain sets (overlap is intentional).
 const groups=[],tileGroups=Array.from({length:N},()=>[]),nearByTile=Array.from({length:N},()=>[]),seenGroups=new Set();
 for(const k of fountains){const tiles=fountains.filter(v=>man(k,v)<=3),setKey=tiles.join(',');if(seenGroups.has(setKey))continue;seenGroups.add(setKey);const id=groups.length,ds=bfs(rev,tiles),capacity=sum(tiles.map(v=>2/(gap[v][0]+gap[v][1])));for(let v=0;v<N;v++)if(ds[v]>=0&&ds[v]<=3)nearByTile[v].push([id,ds[v]]);for(const v of tiles)tileGroups[v].push(id);groups.push({id,anchor:k,tiles,capacity,pocketTiles:tiles.filter(v=>!core[v]),fA:sum(tiles.map(v=>(f.A[v]===null?.5:f.A[v])*2/(gap[v][0]+gap[v][1])))/capacity,dist:ds});}
 const out={signature,W,H,N,nb,rev,bfs,d,f,bin,core,pockets,component,mouthDist,nearestPocket,gap,fountains,groups,tileGroups,nearByTile,man};geoCache.set(signature,out);return out;
}
function geometryJSON(g,map,layout){return {signature:g.signature,map,layout,W:g.W,H:g.H,pocketTiles:g.core.reduce((s,v)=>s+!v,0),unreachableBoth:g.bin.A.filter(v=>v===5).length,spawnTiles:g.gap.flatMap((v,k)=>v&&v[1]>0?[{tile:k,xy:[k%g.W,k/g.W|0],gap:v,meanGap:(v[0]+v[1])/2,pocket:!g.core[k],fA:g.f.A[k]}]:[]),pockets:g.pockets.map(p=>({...p,tiles:p.tiles.map(k=>[k%g.W,k/g.W|0]),mouth:p.mouth.map(k=>[k%g.W,k/g.W|0])})),fountains:g.fountains.map(k=>({tile:k,xy:[k%g.W,k/g.W|0],gap:g.gap[k],pocket:!g.core[k],component:g.component[k],fA:g.f.A[k],fBinA:g.bin.A[k]})),groups:g.groups.map(x=>({id:x.id,anchor:[x.anchor%g.W,x.anchor/g.W|0],anchorPocket:!g.core[x.anchor],anchorFA:g.f.A[x.anchor],tiles:x.tiles,xy:x.tiles.map(k=>[k%g.W,k/g.W|0]),capacity:x.capacity,pocket:x.pocketTiles.length===x.tiles.length,mixedPocket:x.pocketTiles.length>0&&x.pocketTiles.length<x.tiles.length,pocketTiles:x.pocketTiles,fA:x.fA,fBinA:Math.min(4,Math.floor(x.fA*5)),fRangeA:[Math.min(...x.tiles.map(k=>g.f.A[k]??.5)),Math.max(...x.tiles.map(k=>g.f.A[k]??.5))]}))};}
function simpleMeta(R,task){const teams=new Map(R.match.map.initialDragons.map(d=>[d.id,d.team])),pings={A:0,B:0},splits={A:0,B:0};let rounds=0;for(const e of R.events){if(e.type==='roundStart')rounds=e.round+1;if(e.type==='dragonSplit'){teams.set(e.childId,e.team);splits[e.team]++;}}for(const [id,n] of R.sonarBySender||[])pings[teams.get(id)]+=n;return {...task,file:undefined,rounds,winner:R.result.winner||null,stall:rounds>=100?['A','B'].filter(t=>pings[t]===0&&splits[t]<=3):[],pings,splits};}
function teamBlank(g){return {app:matrix(),hr:matrix(),hrMid:zero(),turnHR:matrix(),cp:{},nat:matrix(),natMid:zero(),death:ML.CAUSE.map(()=>zero()),deathMid:ML.CAUSE.map(()=>zero()),pocketDeath:ML.CAUSE.map(()=>zero()),mouthHR:matrix(),parkedMouthHR:matrix(),groupHold:matrix(4,g.groups.length),groupStaff:matrix(4,g.groups.length),sd:PHASES.map(()=>({n:0,pocket:0,present:0,distance:zero(7),sumDistance:0,own:0,uncovered:0})),targets:{},splits:0,pings:0,xHeads:zero(7),xAppearance:zero(7),xNatHook:0,pocketNat:0};}
function analyse(R,task,deep=false){
 const lay=identify(R,task),g=geometry(R.match.map,task.map,lay.layout),{W,H,N}=g,T={A:teamBlank(g),B:teamBlank(g)},roundsByPhase=zero(4),groupApp=matrix(4,g.groups.length),tilePresence=new Uint16Array(N),tileApp=new Uint32Array(N),tileAppPhase=matrix(4,N),tileInitial=new Uint8Array(N),tileEat={A:new Uint32Array(N),B:new Uint32Array(N)},tileDeath={A:{},B:{}},deepRows=[];
 const recordAppearance=(k,r)=>{for(const t of ['A','B'])T[t].app[phase(r)][g.bin[t][k]]++;tileApp[k]++;tileAppPhase[phase(r)][k]++;for(const gi of g.tileGroups[k])groupApp[phase(r)][gi]++;};
 for(let k=0;k<N;k++)if(R.match.map.initialTiles[k]===2){tileInitial[k]=1;recordAppearance(k,0);}
 let drop=false,r=-1;for(const e of R.events){if(e.type==='roundStart')r=e.round;if(e.type==='dragonDeath'){drop=true;continue;}if(e.type==='tileChange'&&e.hasPearl){if(!drop)recordAppearance(e.tile.y*W+e.tile.x,Math.max(0,r));continue;}drop=false;}
 let lastR=-1,prevNatural=new Set(),prevTeam=null,hookEats={A:0,B:0},parkStreak=new Map();
 const hooks={
  turn(d,round,ctx){
   // Compatibility with the brief: disappearing pearls belong to the PREVIOUS hook's actor.
   const now=new Set();for(const [k,v] of ctx.pearls)if(v<0)now.add(k);for(const k of prevNatural)if(!now.has(k)&&prevTeam)hookEats[prevTeam]++;if(round<375)for(const k of now)if(!prevNatural.has(k))for(const t of ['A','B'])T[t].xAppearance[Math.min(6,Math.floor(7*(k%W)/W))]++;prevNatural=now;prevTeam=d.team;
   T[d.team].turnHR[phase(round)][g.bin[d.team][ctx.key(d.body[0].x,d.body[0].y)]]++;
   if(round===lastR)return;lastR=round;roundsByPhase[phase(round)]++;
   const nearest={A:new Int8Array(g.groups.length).fill(99),B:new Int8Array(g.groups.length).fill(99)},staff={A:zero(g.groups.length),B:zero(g.groups.length)},hist={A:zero(),B:zero()};
   for(const a of ctx.drag.values()){const k=ctx.key(a.body[0].x,a.body[0].y),t=a.team,b=g.bin[t][k];T[t].hr[phase(round)][b]++;hist[t][b]++;if(round>=50&&round<375)T[t].hrMid[b]++;if(g.mouthDist[k]>=0&&g.mouthDist[k]<=4)T[t].mouthHR[phase(round)][b]++;if(g.nearestPocket[k]>=0){let st=parkStreak.get(a.id);if(!st||st.lastRound!==round-1||st.pocket!==g.nearestPocket[k])st={pocket:g.nearestPocket[k],lastRound:round,n:0,samples:[]};st.n++;st.lastRound=round;if(st.n<=10)st.samples.push([phase(round),b]);if(st.n===10)for(const [pp,bb] of st.samples)T[t].parkedMouthHR[pp][bb]++;else if(st.n>10)T[t].parkedMouthHR[phase(round)][b]++;parkStreak.set(a.id,st);}else parkStreak.delete(a.id);if(round>=50&&round<375&&round%5===0)T[t].xHeads[Math.min(6,Math.floor(7*(k%W)/W))]++;for(const [gi,dist] of g.nearByTile[k]){nearest[t][gi]=Math.min(nearest[t][gi],dist);staff[t][gi]++;}}
   for(const t of ['A','B']){if(CPS.includes(round))T[t].cp[round]=hist[t];const o=t==='A'?'B':'A';for(let i=0;i<g.groups.length;i++){T[t].groupHold[phase(round)][i]+=+(nearest[t][i]<=3&&nearest[t][i]<nearest[o][i]);T[t].groupStaff[phase(round)][i]+=staff[t][i];}}
   for(const k of now)tilePresence[k]++;
   if(deep&&(round%25===0||CPS.includes(round)))deepRows.push({round,A:hist.A,B:hist.B,groups:g.groups.map((v,i)=>({id:i,A:staff.A[i],B:staff.B[i],held:nearest.A[i]<=3&&nearest.A[i]<nearest.B[i]?'A':nearest.B[i]<=3&&nearest.B[i]<nearest.A[i]?'B':null})),pocketPresent:g.fountains.filter(k=>!g.core[k]&&now.has(k)).map(k=>[k%W,k/W|0])});
  },
  eat(d,k,origin,round){if(origin<0){const t=d.team;T[t].nat[phase(round)][g.bin[t][k]]++;if(round>=50&&round<375)T[t].natMid[g.bin[t][k]]++;tileEat[t][k]++;T[t].pocketNat+=+!g.core[k];}},
  death(d,rec,idx,other,round,ctx){const k=ctx.key(d.body[0].x,d.body[0].y),t=d.team,b=g.bin[t][k];T[t].death[rec.cause][b]++;if(round>=50&&round<375)T[t].deathMid[rec.cause][b]++;if(!g.core[k])T[t].pocketDeath[rec.cause][b]++;tileDeath[t][k]=(tileDeath[t][k]||0)+1;if(deep)deepRows.push({death:true,round,team:t,id:d.id,xy:[k%W,k/W|0],f:g.f[t][k],cause:ML.CAUSE[rec.cause],pocket:!g.core[k],len:rec.len});},
  split(p){T[p.team].splits++;},
  indicator(e,round,ctx){const d=ctx.drag.get(e.dragonId??e.id);if(!d)return;const m=String(e.text||'').match(/ sd(\d+)@(\d+),(\d+)([ou])/);if(!m)return;const k=+m[3]*W+(+m[2]);if(k<0||k>=N)throw Error('sd out of range');const v=T[d.team].sd[phase(round)],di=+m[1],j=di<4?di:di<8?4:di<16?5:6;v.n++;v.pocket+=+!g.core[k];v.present+=+(ctx.pearls.get(k)===-1);v.distance[j]++;v.sumDistance+=di;v.own+=+(m[4]==='o');v.uncovered+=+(m[4]==='u');const a=T[d.team].targets[k]||(T[d.team].targets[k]={n:0,present:0,sumDistance:0,pocket:!g.core[k],f:g.f[d.team][k],xy:[k%W,k/W|0]});a.n++;a.present+=+(ctx.pearls.get(k)===-1);a.sumDistance+=di;},
  end(rounds,ctx){const now=new Set();for(const [k,v] of ctx.pearls)if(v<0)now.add(k);for(const k of prevNatural)if(!now.has(k)&&prevTeam)hookEats[prevTeam]++;}
 };
 const L=ML.perGame(R,{map:task.map,variant:lay.layout==='10'?'PD10':lay.layout},hooks);
 const ledgerNatural={},checks={...L.chk,hookEat:0,appearance:0,death:0};
 for(const t of ['A','B']){ledgerNatural[t]=sum(L[t].fl[ML.FI.eat_nat]);checks.hookEat+=+(sum(T[t].nat.flat())!==ledgerNatural[t]);checks.death+=+(sum(T[t].death.flat())!==sum(ML.CAUSE.map(c=>sum(L[t].fl[ML.FI['dn_'+c]]))));T[t].xNatHook=hookEats[t];for(const [k,v] of Object.entries(T[t].targets))v.presenceRounds=tilePresence[+k];}
 const initial=sum(Array.from({length:N},(_,k)=>+(R.match.map.initialTiles[k]===2)));checks.appearance=+(sum(T.A.app.flat())-initial!==sum(L.gf.slice(0,3).flat()));
 const teams=new Map([...R.match.map.initialDragons.map(d=>[d.id,d.team]),...R.events.filter(e=>e.type==='dragonSplit').map(e=>[e.childId,e.team])]);for(const [id,n] of R.sonarBySender||[])if(teams.has(id))T[teams.get(id)].pings+=n;
 const rounds=L.rounds,stall=rounds>=100?['A','B'].filter(t=>T[t].pings===0&&T[t].splits<=3):[];
 const pocketFountains=g.fountains.filter(k=>!g.core[k]).map(k=>({tile:k,app:tileApp[k],presentRounds:tilePresence[k],eatA:tileEat.A[k],eatB:tileEat.B[k],deathA:tileDeath.A[k]||0,deathB:tileDeath.B[k]||0}));
 const tileCounts=[];for(let k=0;k<N;k++)if(tileApp[k]||g.gap[k]&&g.gap[k][1]>0)tileCounts.push([k,tileAppPhase.map(p=>p[k]),tileInitial[k],tilePresence[k],tileEat.A[k],tileEat.B[k],tileDeath.A[k]||0,tileDeath.B[k]||0]);
 return {...task,schemaVersion:2,tileCounts,file:undefined,layout:lay.layout,layoutEvidence:lay,geometry:g.signature,rounds,winner:R.result.winner||null,endReason:R.result.endReason,stall,roundsByPhase,groupApp,pocketFountains,A:T.A,B:T.B,ledgerNatural,checks,hookDifference:{A:hookEats.A-ledgerNatural.A,B:hookEats.B-ledgerNatural.B},result:R.result,deepRows:deep?deepRows:undefined};
}
module.exports={ROOT,ML,raw,MAPS,SELECT,TWO,WAVE,EARLY,CPS,PHASES,BINS,zero,matrix,phase,sum,readl,identify,geometry,geometryJSON,simpleMeta,analyse};
