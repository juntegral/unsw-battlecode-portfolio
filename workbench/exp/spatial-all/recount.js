// Independent event-driven recount. Shares only the validated binary decoder with lib.js.
// Bodies follow replay head/tail updates; intake follows tileChange under the current turnStart.
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process');
const ROOT=path.resolve(__dirname,'../..'),OUT=path.join(__dirname,'cache'),raw=require(path.join(ROOT,'legacy/exp/intake-gap/rawload.js'));
const SLUG={'Autarky':'autarky','Default':'default','Devil':'devil','Portals':'portals','Prisoners Dilemma':'prisoners_dilemma','Queen Of Spades':'queen_of_spades','Schooltime':'schooltime','Slithery Fight':'slithery_fight','Trauma':'trauma','Trophy':'trophy'};
const TARGET=new Set(['Devil','Queen Of Spades','Schooltime','Slithery Fight','Prisoners Dilemma']),TWO=new Set(['Devil','Queen Of Spades','Schooltime','Slithery Fight']);
const CAUSES=['sac','trap','rammed','ram','enemyBody','allyHead','fault','sprintDeath'],CPS=[25,50,100,250,375];
const zeros=n=>Array(n).fill(0),mat=(n,m)=>Array.from({length:n},()=>zeros(m)),ph=r=>r<100?0:r<250?1:r<375?2:3;
const geomCache=new Map(),gapCache=new Map();
function readGaps(map,lay){const key=map+'/'+lay;if(gapCache.has(key))return gapCache.get(key);const f=path.join(ROOT,lay==='b'||lay==='10'?'maps/variants':'maps/online-20260927',SLUG[map]+(lay==='b'?'_b':lay==='10'?'_10':'')+'.map'),lines=fs.readFileSync(f,'utf8').split('\n'),W=+lines[0].split(/\s+/)[1],g=[];for(const line of lines){const v=line.split(/\s+/);if(v[0]==='TILE')g[+v[2]*W+(+v[1])]=[+v[3],+v[4]];}gapCache.set(key,g);return g;}
function geo(M,map,lay){
 const key=JSON.stringify([map,lay,M.width,M.height,M.initialHEdges,M.initialVEdges,M.portals,M.initialDragons.map(d=>[d.team,d.body])]);if(geomCache.has(key))return geomCache.get(key);
 const W=M.width,H=M.height,N=W*H,xy=(x,y)=>((y%H+H)%H)*W+(x%W+W)%W,D=[[0,-1],[1,0],[0,1],[-1,0]],edgeKey=(x,y,s)=>{const z='NESW'.indexOf(s),a=xy(x,y),b=xy(x+D[z][0],y+D[z][1]);return (z%2===0?'h':'v')+Math.min(a,b)+':'+Math.max(a,b);},portals=new Map();
 for(const [a,b] of M.portals||[]){portals.set(edgeKey(a.x,a.y,a.side),b);portals.set(edgeKey(b.x,b.y,b.side),a);}
 const directions=Array.from({length:N},()=>zeros(4).map(()=>-1)),adj=Array.from({length:N},()=>new Set()),reverse=Array.from({length:N},()=>new Set());
 for(let y=0;y<H;y++)for(let x=0;x<W;x++)for(let z=0;z<4;z++){const p=portals.get(edgeKey(x,y,'NESW'[z]));let v;
  if(p){let px=p.x,py=p.y;if(p.side==='S')py=(py+1)%H;else if(p.side==='E')px=(px+1)%W;v=xy(px-(z===3?1:0),py-(z===0?1:0));}
  else{const he=(xx,yy)=>M.initialHEdges[yy*W+xx]===1,ve=(xx,yy)=>M.initialVEdges[yy*(W+1)+xx]===1;let wall;if(z===0)wall=he(x,y)||(y===0&&he(x,H));else if(z===2)wall=y===H-1?he(x,H)||he(x,0):he(x,y+1);else if(z===3)wall=ve(x,y)||(x===0&&ve(W,y));else wall=x===W-1?ve(W,y)||ve(0,y):ve(x+1,y);if(wall)continue;v=xy(x+D[z][0],y+D[z][1]);}
  const k=xy(x,y);directions[k][z]=v;adj[k].add(v);reverse[v].add(k);
 }
 const distance=(edges,seeds)=>{const a=Array(N).fill(Infinity),q=[];for(const k of seeds)if(a[k]!==0){a[k]=0;q.push(k);}for(let i=0;i<q.length;i++)for(const v of edges[q[i]])if(a[v]===Infinity){a[v]=a[q[i]]+1;q.push(v);}return a;};
 const dist={};for(const t of ['A','B'])dist[t]=distance(adj,M.initialDragons.filter(d=>d.team===t).flatMap(d=>d.body.map(p=>xy(p.x,p.y))));
 const bin={A:[],B:[]};for(let k=0;k<N;k++)for(const t of ['A','B']){const a=dist[t][k],b=dist[t==='A'?'B':'A'][k];bin[t][k]=a===Infinity&&b===Infinity?5:a===Infinity?4:b===Infinity?0:a+b===0?2:Math.min(4,Math.floor(5*a/(a+b)));}
 const edges=adj.map((v,k)=>new Set([...v,...reverse[k]])),inCore=new Set(Array.from({length:N},(_,i)=>i));let changed=true;while(changed){changed=false;const remove=[];for(const k of inCore){let n=0;for(const v of edges[k])n+=+inCore.has(v);if(n<=1)remove.push(k);}for(const k of remove){inCore.delete(k);changed=true;}}
 const pocket=Array.from({length:N},(_,i)=>!inCore.has(i)),fountains=[],gaps=lay==='?'?[]:readGaps(map,lay);for(let k=0;k<N;k++)if(gaps[k]&&gaps[k][1]>0&&gaps[k][0]+gaps[k][1]<=24)fountains.push(k);
 const groups=[],setKeys=new Set(),members=Array.from({length:N},()=>[]);for(const anchor of fountains){const ts=fountains.filter(v=>{const dx=Math.abs(anchor%W-v%W),dy=Math.abs(Math.floor(anchor/W)-Math.floor(v/W));return Math.min(dx,W-dx)+Math.min(dy,H-dy)<=3;}),idKey=ts.join(',');if(setKeys.has(idKey))continue;setKeys.add(idKey);const id=groups.length;for(const v of ts)members[v].push(id);groups.push({id,tiles:ts,distance:distance(reverse,ts)});}
 const near=Array.from({length:N},()=>[]);for(const group of groups)for(let k=0;k<N;k++)if(group.distance[k]<=3)near[k].push([group.id,group.distance[k]]);
 const g={W,H,N,xy,directions,adj,bin,pocket,fountains,groups,members,near};geomCache.set(key,g);return g;
}
function recount(R,task){
 const M=R.match.map,W=M.width,N=W*M.height,ix=p=>p.y*W+p.x;let lay=task.localLayout|| (task.map==='Prisoners Dilemma'?(M.initialDragons.length===10?'10':'6'):'a'),evidence=null;
 if(!task.localLayout&&TWO.has(task.map)){const a=readGaps(task.map,'a'),b=readGaps(task.map,'b');let ca=0,cb=0,block=false;for(const e of R.events){if(e.type==='dragonDeath'){block=true;continue;}if(e.type==='tileChange'&&e.hasPearl){if(!block){const k=ix(e.tile);ca+=+(!a[k]||a[k][1]===0);cb+=+(!b[k]||b[k][1]===0);}continue;}block=false;}lay=ca<cb?'a':cb<ca?'b':'?';evidence=[ca,cb];}
 // For tied spawn-support cases group checks are omitted; frontier/heads/intake are still independently verified.
 const g=geo(M,task.map,lay),T={};for(const t of ['A','B'])T[t]={app:mat(4,6),hr:mat(4,6),hrMid:zeros(6),cp:{},nat:mat(4,6),natMid:zeros(6),death:mat(8,6),deathMid:mat(8,6),pocketDeath:mat(8,6),groupHold:mat(4,g.groups.length),groupStaff:mat(4,g.groups.length),sd:mat(4,3),splits:0,pings:0};
 const team=new Map(),body=new Map(),occ=Array(N).fill(-1),pearl=Array(N).fill(0),presence=Array(N).fill(0),tileApp=Array(N).fill(0),tileAppPhase=mat(4,N),tileInitial=Array(N).fill(0),tileEat={A:Array(N).fill(0),B:Array(N).fill(0)},tileDeath={A:{},B:{}},groupApp=mat(4,g.groups.length),roundsByPhase=zeros(4);
 function put(id){for(const k of body.get(id))occ[k]=id;}function lift(id){for(const k of body.get(id))if(occ[k]===id)occ[k]=-1;}
 for(const d of M.initialDragons){team.set(d.id,d.team);body.set(d.id,d.body.map(ix));put(d.id);}function app(k,r){for(const t of ['A','B'])T[t].app[ph(r)][g.bin[t][k]]++;tileApp[k]++;tileAppPhase[ph(r)][k]++;for(const gi of g.members[k])groupApp[ph(r)][gi]++;}
 for(let k=0;k<N;k++)if(M.initialTiles[k]===2){pearl[k]=1;tileInitial[k]=1;app(k,0);}
 let round=-1,cur=-1,drop=false,first=false,steps=[],updates=0,free=0,tle=false,lastVictim=null,lenMismatch=0;
 for(const e of R.events){if(drop&&!(e.type==='tileChange'&&e.hasPearl))drop=false;
  if(e.type==='roundStart'){round=e.round;first=true;roundsByPhase[ph(round)]++;const hist={A:zeros(6),B:zeros(6)};for(const [id,b] of body){const t=team.get(id),z=g.bin[t][b[0]];T[t].hr[ph(round)][z]++;hist[t][z]++;if(round>=50&&round<375)T[t].hrMid[z]++;}if(CPS.includes(round))for(const t of ['A','B'])T[t].cp[round]=hist[t];}
  else if(e.type==='turnStart'){cur=e.id;steps=[];updates=0;tle=false;const b=body.get(cur);if(!b)throw Error('missing actor '+cur);free=g.directions[b[0]].filter(v=>v>=0&&occ[v]<0).length;
   if(first){first=false;for(let k=0;k<N;k++)if(pearl[k]===1)presence[k]++;const min={A:Array(g.groups.length).fill(Infinity),B:Array(g.groups.length).fill(Infinity)},staff={A:zeros(g.groups.length),B:zeros(g.groups.length)};for(const [id,b] of body)for(const [gi,d] of g.near[b[0]]){const t=team.get(id);min[t][gi]=Math.min(min[t][gi],d);staff[t][gi]++;}for(const t of ['A','B'])for(let i=0;i<g.groups.length;i++){T[t].groupHold[ph(round)][i]+=+(min[t][i]<=3&&min[t][i]<min[t==='A'?'B':'A'][i]);T[t].groupStaff[ph(round)][i]+=staff[t][i];}}
  }
  else if(e.type==='dragonAction'){steps=e.action&&e.action.kind==='move'?e.action.steps:[];tle=!!e.tle;}
  else if(e.type==='tileChange'){const k=ix(e.tile);if(e.hasPearl){pearl[k]=drop?2:1;if(!drop)app(k,Math.max(0,round));}else{const t=team.get(cur);if(!t)throw Error('eat without actor');if(pearl[k]===1){T[t].nat[ph(round)][g.bin[t][k]]++;tileEat[t][k]++;if(round>=50&&round<375)T[t].natMid[g.bin[t][k]]++;}if(!pearl[k])throw Error('eat absent pearl');pearl[k]=0;}}
  else if(e.type==='dragonUpdate'){if(round<0)continue;const id=e.id;lift(id);const b=body.get(id),h=ix(e.head),tail=ix(e.tail);if(b[0]!==h)b.unshift(h);while(b.length>1&&b[b.length-1]!==tail)b.pop();put(id);updates++;}
  else if(e.type==='dragonSplit'){const id=e.parentId;lift(id);body.set(id,e.parentBody.map(ix));put(id);team.set(e.childId,e.team);body.set(e.childId,e.childBody.map(ix));put(e.childId);T[e.team].splits++;}
  else if(e.type==='dragonDeath'){const id=e.id,b=body.get(id),t=team.get(id),k=b[0];let cause;
   if(id!==cur){cause=team.get(cur)===t?'allyHead':'rammed';lastVictim={id,team:t,round};}
   else if(e.reason==='H')cause=lastVictim&&lastVictim.round===round&&lastVictim.team===t?'allyHead':'ram';
   else if(e.reason==='O'){const z='NESW'.indexOf(steps[updates]),v=z<0?-1:g.directions[k][z],other=v>=0?occ[v]:-1;cause=other>=0&&team.get(other)===t?(free?'sac':'trap'):(free?'enemyBody':'trap');}
   else if(e.reason==='A'&&tle)cause='fault';else if(e.reason==='A'&&steps.length>updates&&updates>0&&b.length<=2)cause='sprintDeath';else cause=free?'sac':'trap';
   const ci=CAUSES.indexOf(cause),z=g.bin[t][k];T[t].death[ci][z]++;if(round>=50&&round<375)T[t].deathMid[ci][z]++;if(g.pocket[k])T[t].pocketDeath[ci][z]++;tileDeath[t][k]=(tileDeath[t][k]||0)+1;lift(id);body.delete(id);drop=true;
  }
  else if(e.type==='dragonIndicator'){const t=team.get(e.id),m=String(e.text||'').match(/ sd(\d+)@(\d+),(\d+)([ou])/);if(m&&t){const k=+m[3]*W+(+m[2]),v=T[t].sd[ph(round)];v[0]++;v[1]+=+g.pocket[k];v[2]+=+(pearl[k]===1);}}
 }
 let finalMismatch=0;for(const t of ['A','B']){const ds=[...body].filter(([id])=>team.get(id)===t).map(([id,b])=>b),r=R.result['team'+t];if(ds.length!==r.dragonCount||ds.reduce((s,b)=>s+b.length,0)!==r.totalLength||Math.max(0,...ds.map(b=>b.length))!==r.longestDragon)finalMismatch++;}
 for(const [id,n] of R.sonarBySender||[])if(team.has(id))T[team.get(id)].pings+=n;
 const rounds=round+1,stall=rounds>=100?['A','B'].filter(t=>!T[t].pings&&T[t].splits<=3):[],pocketFountains=g.fountains.filter(k=>g.pocket[k]).map(k=>({tile:k,app:tileApp[k],presentRounds:presence[k],eatA:tileEat.A[k],eatB:tileEat.B[k],deathA:tileDeath.A[k]||0,deathB:tileDeath.B[k]||0}));
 const gaps=lay==='?'?[]:readGaps(task.map,lay),tileCounts=[];for(let k=0;k<N;k++)if(tileApp[k]||gaps[k]&&gaps[k][1]>0)tileCounts.push([k,tileAppPhase.map(p=>p[k]),tileInitial[k],presence[k],tileEat.A[k],tileEat.B[k],tileDeath.A[k]||0,tileDeath.B[k]||0]);
 return {key:task.key,schemaVersion:2,tileCounts,layout:lay,layoutEvidence:evidence,rounds,winner:R.result.winner||null,stall,roundsByPhase,A:T.A,B:T.B,groupApp,pocketFountains,finalMismatch};
}
function resource(){const m=/System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure',['-Q'],{encoding:'utf8'})),d=cp.execFileSync('df',['-g',ROOT],{encoding:'utf8'}).trim().split('\n').pop().trim().split(/\s+/);return {memory:m?+m[1]:null,disk:+d[3]};}
if(require.main===module){const tasks=JSON.parse(fs.readFileSync(path.join(OUT,'population.json'),'utf8')).tasks.filter(t=>t.src!=='top'||TARGET.has(t.map)),file=path.join(OUT,'recount.jsonl'),done=new Set(fs.existsSync(file)?fs.readFileSync(file,'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r=>r.schemaVersion===2).map(r=>r.key):[]),start=Date.now();let n=0;for(const t of tasks){if(done.has(t.key))continue;if(n%100===0){const r=resource();if(r.memory===null||r.memory<10||r.disk<20){console.log('PAUSED',r);process.exit(75);}}try{const row=recount(raw.load(t.file),t);fs.appendFileSync(file,JSON.stringify(row)+'\n');}catch(e){fs.appendFileSync(path.join(OUT,'recount-errors.jsonl'),JSON.stringify({key:t.key,error:e.stack})+'\n');}n++;if(n%100===0)console.log('progress',n,'/',tasks.length-done.size,'sec',Math.round((Date.now()-start)/1000));}console.log('DONE',n,'seconds',(Date.now()-start)/1000);}
module.exports={recount,geo,readGaps};
