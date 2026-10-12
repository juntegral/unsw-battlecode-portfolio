#!/usr/bin/env node
// Independent FULL online recount. Shares only the official parser with extract.js.
// Does NOT import mass_ledger, mech_check, territory code or the primary extractor.
// Rebuilds bodies from official dragonUpdate head/tail and dragonSplit full bodies;
// natural pearl provenance from raw tileChange sequences; territories from an
// independently written directed tile graph. Checks every final body's count,
// longest and total against the replay result, and every online game against
// primary extraction. Five key metrics: our eliminations, our natural intake,
// opponent natural intake on our starting territory, king ram victims (L>=8),
// and the sprint subset of those victims. Also recounts wins and final lengths.
// Usage: guard.py node --max-old-space-size=768 exp/elite-counterplay/recount.js
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process');
const ROOT=path.resolve(__dirname,'../..'),C=path.join(ROOT,'.cache/elite-counterplay');
const {load}=require(path.join(ROOT,'tools/replay.js'));
const M=JSON.parse(fs.readFileSync(path.join(C,'manifest.json'),'utf8'));
function guard(){
 const m=/System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure',{encoding:'utf8'}));
 const d=+cp.execFileSync('df',['-g','/'],{encoding:'utf8'}).trim().split('\n').pop().trim().split(/\s+/)[3];
 if(!m||+m[1]<10||d<20)process.exit(75);
}
function territory(map){
 const w=map.width,h=map.height,n=w*h,wrap=(x,k)=>(x+k)%k;
 const edge=e=>e.side==='S'?[e.x,wrap(e.y+1,h),'N']:e.side==='E'?[wrap(e.x+1,w),e.y,'W']:[e.x,e.y,e.side];
 const portal=new Map();
 for(const pair of map.portals||[]){const a=edge(pair[0]),b=edge(pair[1]);portal.set(a.join(':'),b);portal.set(b.join(':'),a);}
 const graph=Array.from({length:n},()=>[]);
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){
  for(const dir of ['N','E','S','W']){
   const ex=dir==='E'?wrap(x+1,w):x,ey=dir==='S'?wrap(y+1,h):y;
   const axis=dir==='N'||dir==='S'?'N':'W';
   const p=portal.get([ex,ey,axis].join(':'));
   let nx,ny;
   if(p){nx=p[0];ny=p[1];if(dir==='N')ny=wrap(ny-1,h);if(dir==='W')nx=wrap(nx-1,w);}
   else{
    const blocked=axis==='N'?(map.initialHEdges[ey*w+ex]===1||ey===0&&map.initialHEdges[h*w+ex]===1):
      (map.initialVEdges[ey*(w+1)+ex]===1||ex===0&&map.initialVEdges[ey*(w+1)+w]===1);
    if(blocked)continue;
    nx=wrap(x+(dir==='E'?1:dir==='W'?-1:0),w);ny=wrap(y+(dir==='S'?1:dir==='N'?-1:0),h);
   }
   graph[y*w+x].push(ny*w+nx);
  }
 }
 const dist=team=>{
  const a=Array(n).fill(Infinity),queue=[];
  for(const d of map.initialDragons)if(d.team===team)for(const b of d.body){const k=b.y*w+b.x;if(a[k]===0)continue;a[k]=0;queue.push(k);}
  for(let i=0;i<queue.length;i++){const k=queue[i];for(const v of graph[k])if(!Number.isFinite(a[v])){a[v]=a[k]+1;queue.push(v);}}
  return a;
 };
 const a=dist('A'),b=dist('B');return a.map((v,i)=>v<b[i]?'A':b[i]<v?'B':null);
}
function recount(R,task){
 const map=R.match.map,w=map.width,terr=territory(map),drag=new Map(),team=new Map();
 for(const d of map.initialDragons){drag.set(d.id,{team:d.team,body:d.body.map(b=>({...b}))});team.set(d.id,d.team);}
 const pearl=new Map();for(let i=0;i<map.initialTiles.length;i++)if(map.initialTiles[i]===2)pearl.set(i,'natural');
 const eat={A:{nat:0,onA:0,onB:0},B:{nat:0,onA:0,onB:0}},lastDeath={A:null,B:null},pings={A:0,B:0},splits={A:0,B:0};
 let r=-1,current=-1,dropping=false,steps=new Map(),kingRams={A:0,B:0},kingSprint={A:0,B:0};
 const history=new Map([...drag].map(([id,d])=>[id,{team:d.team,born:0,died:null,parent:null,children:[]}]));
 const pressure=[];let currentPressure=null;
 const md=(a,b)=>{const x=Math.abs(a.x-b.x),y=Math.abs(a.y-b.y);return Math.min(x,w-x)+Math.min(y,map.height-y);};
 const cd=(a,b)=>{const x=Math.abs(a.x-b.x),y=Math.abs(a.y-b.y);return Math.max(Math.min(x,w-x),Math.min(y,map.height-y));};
 const kingside=d=>{for(const [id,o]of drag)if(o.team===d.team&&(o.body.length>d.body.length||o.body.length===d.body.length&&id<d.id))return false;return true;};
 for(const e of R.events){
  if(dropping&&!(e.type==='tileChange'&&e.hasPearl))dropping=false;
  if(e.type==='roundStart')r=e.round;
  else if(e.type==='turnStart'){
   current=e.id;currentPressure=null;
   const d=drag.get(current);
   if(d&&d.team===task.us&&task.era==='primary'){
    const es=[...drag.values()].filter(o=>o.team!==d.team).map(o=>({...o.body[0]}));
    const allies=[...drag].filter(([id,o])=>id!==current&&o.team===d.team).map(([id,o])=>({...o.body[0]}));
    const ev3=es.filter(h=>cd(h,d.body[0])<=3).length,av3=allies.filter(h=>cd(h,d.body[0])<=3).length;
    if(ev3>=2&&ev3>av3){
     currentPressure={id:current,r,len:d.body.length,e3:ev3,a3:av3,ed:Math.min(...es.map(h=>md(h,d.body[0]))),
       head:{...d.body[0]},end:{...d.body[0]},enemies:es,kind:null,steps:0,tag:''};pressure.push(currentPressure);
    }
   }
  }
  else if(e.type==='dragonIndicator'){if(currentPressure&&e.id===currentPressure.id)currentPressure.tag=e.text;}
  else if(e.type==='dragonAction'){
   steps.set(e.id,e.action?.kind==='move'?e.action.steps.length:0);
   if(currentPressure&&e.id===currentPressure.id){currentPressure.kind=e.action?.kind||null;currentPressure.steps=steps.get(e.id);}
  }
  else if(e.type==='sonarPing'){const t=team.get(e.senderId);if(t)pings[t]++;}
  else if(e.type==='tileChange'){
   const k=e.tile.y*w+e.tile.x;
   if(e.hasPearl)pearl.set(k,dropping?'death':'natural');
   else{
    if(pearl.get(k)==='natural'){
     const d=drag.get(current);if(!d)throw Error(`Natural eat without live eater ${task.key}`);
     eat[d.team].nat++;if(terr[k]==='A')eat[d.team].onA++;if(terr[k]==='B')eat[d.team].onB++;
    }
    pearl.delete(k);
   }
  }else if(e.type==='dragonUpdate'){
   const d=drag.get(e.id);if(!d)throw Error('Update of unknown dragon');
   const b=d.body;
   if(b[0].x!==e.head.x||b[0].y!==e.head.y)b.unshift({...e.head});
   while(b.length&&(b[b.length-1].x!==e.tail.x||b[b.length-1].y!==e.tail.y))b.pop();
   if(!b.length)throw Error(`Tail not found ${task.key} r${r} id${e.id}`);
   if(currentPressure&&e.id===currentPressure.id)currentPressure.end={...e.head};
  }else if(e.type==='dragonSplit'){
   const d=drag.get(e.parentId);d.body=e.parentBody.map(b=>({...b}));
   drag.set(e.childId,{team:e.team,body:e.childBody.map(b=>({...b}))});team.set(e.childId,e.team);splits[e.team]++;
   history.set(e.childId,{team:e.team,born:r,died:null,parent:e.parentId,children:[]});history.get(e.parentId).children.push(e.childId);
  }else if(e.type==='dragonDeath'){
   const d=drag.get(e.id);if(!d)throw Error('Death of unknown dragon');d.id=e.id;
   if(e.reason==='H'&&e.id!==current&&team.get(current)!==d.team&&d.body.length>=8&&kingside(d)){
    kingRams[d.team]++;if((steps.get(current)||0)>=2)kingSprint[d.team]++;
   }
   lastDeath[d.team]=r;drag.delete(e.id);dropping=true;history.get(e.id).died=r;
  }
 }
 const out={key:task.key,era:task.era,oppId:task.oppId,gameId:task.gameId,us:task.us,rounds:r+1,winner:R.result.winner||null};
 for(const t of ['A','B']){
  const ds=[...drag.values()].filter(d=>d.team===t),lens=ds.map(d=>d.body.length),res=R.result['team'+t];
  const state={units:ds.length,longest:Math.max(0,...lens),total:lens.reduce((a,b)=>a+b,0)};
  if(state.units!==res.dragonCount||state.longest!==res.longestDragon||state.total!==res.totalLength)throw Error(`Independent body mismatch ${task.key} ${t} ${JSON.stringify(state)} ${JSON.stringify(res)}`);
  out[t]={...state,...eat[t],elim:ds.length?null:lastDeath[t],kingRams:kingRams[t],kingSprint:kingSprint[t],pings:pings[t],splits:splits[t]};
 }
 const aliveFamily=(id,t)=>{const d=history.get(id);if(d.born>t)return false;if(d.died===null||d.died>t)return true;return d.children.some(child=>aliveFamily(child,t));};
 const behavior={retreat:{n:0,alive10:0},stay:{n:0,alive10:0},approach:{n:0,alive10:0},split:{n:0,alive10:0},other:{n:0,alive10:0}};
 for(const p of pressure){
  const endd=Math.min(...p.enemies.map(h=>md(h,p.end)));
  const kind=p.kind==='split'?'split':p.kind!=='move'?'other':endd>p.ed?'retreat':endd<p.ed?'approach':'stay';
  const a=behavior[kind];a.n++;if(aliveFamily(p.id,Math.min(r,p.r+10)))a.alive10++;
 }
 out.pressureBehavior=behavior;
 return out;
}
async function main(){
 const file=path.join(C,'recount.jsonl'),done=new Set();
 if(fs.existsSync(file))for(const l of fs.readFileSync(file,'utf8').split('\n'))if(l.trim())done.add(JSON.parse(l).key);
 const tasks=M.tasks.filter(t=>t.src==='online'&&!done.has(t.key)),fd=fs.openSync(file,'a'),start=Date.now();guard();
 for(let i=0;i<tasks.length;i++){
  if(i%25===0)guard();const t=tasks[i],res=recount(load(path.join(ROOT,t.file)),t);fs.writeSync(fd,JSON.stringify(res)+'\n');
  if((i+1)%25===0||i+1===tasks.length)console.log(`recount ${i+1}/${tasks.length}, ${Math.round((Date.now()-start)/1000)}s`);
  await new Promise(resolve=>setTimeout(resolve,50));
 }fs.closeSync(fd);
}
if(require.main===module)main().catch(e=>{console.error(e.stack);process.exitCode=1;});
module.exports={recount};
