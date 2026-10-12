'use strict';
// Independent reconstruction: official updates rather than simulated action bodies.
// Does not import mass_ledger.js or any earlier research extractor.
const fs=require('fs'),cp=require('child_process');
const {load}=require('../../tools/replay.js');
const dir='.cache/outcome-review';
if(!process.argv.includes('--allow-inherited-10'))throw Error('Awaiting resource exception');
const games=fs.readFileSync(dir+'/primary.jsonl','utf8').trim().split('\n').map(JSON.parse);
const out=fs.openSync(dir+'/independent.jsonl','wx'), log=fs.openSync(dir+'/resource-recount.jsonl','wx');
let last=0;
function guard(){
  if(Date.now()-last<20000)return;last=Date.now();
  const mem=cp.execFileSync('/usr/bin/memory_pressure',[],{encoding:'utf8'});
  const pct=+(/System-wide memory free percentage:\s*(\d+)%/.exec(mem)||[])[1];
  const disk=+cp.execFileSync('/bin/df',['-g','/'],{encoding:'utf8'}).trim().split('\n').at(-1).trim().split(/\s+/)[3];
  fs.writeSync(log,JSON.stringify({at:new Date().toISOString(),memory:pct,disk})+'\n');
  if(!Number.isFinite(pct)||pct<10||disk<20)throw Error('PAUSE resources '+pct+'% '+disk+' GiB');
}
function reconstruct(R,g){
 const M=R.match.map,W=M.width,H=M.height,wx=x=>(x+W)%W,wy=y=>(y+H)%H,key=(x,y)=>y*W+x;
 const canon=e=>e.side==='S'?{x:e.x,y:wy(e.y+1),side:'N'}:e.side==='E'?{x:wx(e.x+1),y:e.y,side:'W'}:{...e};
 const portal=new Map();for(const pr of M.portals||[]){if(pr.length!==2)continue;const[a,b]=pr.map(canon);portal.set(a.x+','+a.y+','+a.side,b);portal.set(b.x+','+b.y+','+b.side,a);}
 function across(h,d){const x=h.x,y=h.y;let ek,wall;
  if(d==='N'){ek=x+','+y+',N';wall=M.initialHEdges[y*W+x]===1||(y===0&&M.initialHEdges[H*W+x]===1);}
  else if(d==='S'){ek=x+','+wy(y+1)+',N';wall=M.initialHEdges[wy(y+1)*W+x]===1||(wy(y+1)===0&&M.initialHEdges[H*W+x]===1);}
  else if(d==='W'){ek=x+','+y+',W';wall=M.initialVEdges[y*(W+1)+x]===1||(x===0&&M.initialVEdges[y*(W+1)+W]===1);}
  else {ek=wx(x+1)+','+y+',W';wall=M.initialVEdges[y*(W+1)+wx(x+1)]===1||(wx(x+1)===0&&M.initialVEdges[y*(W+1)+W]===1);}
  const p=portal.get(ek);if(p){if(d==='N')return{x:p.x,y:wy(p.y-1)};if(d==='S')return{x:p.x,y:p.y};if(d==='W')return{x:wx(p.x-1),y:p.y};return{x:p.x,y:p.y};}
  if(wall)return null;return{x:wx(x+(d==='E'?1:d==='W'?-1:0)),y:wy(y+(d==='S'?1:d==='N'?-1:0))};
 }
 const D=new Map(),alive=new Map(),occ=new Map(),pearls=new Map(),deaths=[];
 const put=d=>{for(const s of d.body)occ.set(key(s.x,s.y),d.id);},clear=d=>{for(const s of d.body)if(occ.get(key(s.x,s.y))===d.id)occ.delete(key(s.x,s.y));};
 function born(id,team,body,parent,seq,r){const d={id,team,body:body.map(s=>({...s})),parent,born:seq,bornRound:r,eats:[],env:[],costs:[],splits:[],checkpoint:{},free:0,action:null,updates:0,tle:false};D.set(id,d);alive.set(id,d);put(d);return d;}
 for(const d of M.initialDragons)born(d.id,d.team,d.body,-1,-1,0);
 for(let k=0;k<M.initialTiles.length;k++)if(M.initialTiles[k]===2)pearls.set(k,{origin:0,death:-1});
 const T={A:{nat:0,nat100:0,sac:0,sac300:0,births250:0,births300:0,kd:[],turnExposure200:[0,0]},B:{nat:0,nat100:0,sac:0,sac300:0,births250:0,births300:0,kd:[],turnExposure200:[0,0]}};
 const checkpoints={},roundSeq={},sum=x=>x.reduce((a,b)=>a+b,0);
 const king=tm=>{let k=null;for(const d of alive.values())if(d.team===tm&&(!k||d.body.length>k.body.length||(d.body.length===k.body.length&&d.id<k.id)))k=d;return k;};
 const man=(a,b)=>{const x=Math.abs(a.x-b.x),y=Math.abs(a.y-b.y);return Math.min(x,W-x)+Math.min(y,H-y);};
 let seq=0,r=-1,cur=-1,dropping=null;
 for(const e of R.events){seq++;if(dropping&&!(e.type==='tileChange'&&e.hasPearl))dropping=null;
  if(e.type==='roundStart'){r=e.round;roundSeq[r]=seq;
   if([10,50,100,250,300,400].includes(r)){const s={};for(const tm of ['A','B']){const ds=[...alive.values()].filter(x=>x.team===tm);s[tm]={heads:ds.length,king:king(tm)?.body.length||0,total:sum(ds.map(x=>x.body.length))};}checkpoints[r]=s;}
   if([300,400].includes(r))for(const d of alive.values())d.checkpoint[r]=d.body.length;
  }else if(e.type==='turnStart'){cur=e.id;const d=alive.get(cur);if(!d)continue;
   d.free=0;for(const dir of ['N','E','S','W']){const n=across(d.body[0],dir);if(n&&!occ.has(key(n.x,n.y)))d.free++;}
   d.action=null;d.updates=0;d.tle=false;
   if(r>=200&&d.body.length>=8){let n=99,e6=0;for(const o of alive.values())if(o.team!==d.team){const q=man(d.body[0],o.body[0]);n=Math.min(n,q);if(q<=6)e6++;}
    if(r>=300)d.env.push([seq,r,n<=6?1:0,e6]);
    if(r<300&&king(d.team)?.id===d.id){T[d.team].turnExposure200[0]++;T[d.team].turnExposure200[1]+=n<=6?1:0;}
   }
  }else if(e.type==='dragonAction'){const d=alive.get(e.id);if(d){d.action=e.action;d.tle=!!e.tle;d.updates=0;}}
  else if(e.type==='dragonUpdate'){const d=alive.get(e.id);if(!d||r<0)continue;clear(d);const b=d.body.map(x=>({...x}));
   if(b[0].x!==e.head.x||b[0].y!==e.head.y)b.unshift({...e.head});
   while(b.length>1&&(b.at(-1).x!==e.tail.x||b.at(-1).y!==e.tail.y))b.pop();
   d.body=b;d.updates++;put(d);
  }else if(e.type==='tileChange'){const k=key(e.tile.x,e.tile.y);
   if(e.hasPearl){pearls.set(k,dropping?{origin:dropping.cause==='sac'?1:2,team:dropping.team,death:dropping.idx}:{origin:0,death:-1});}
   else {const p=pearls.get(k);pearls.delete(k);const d=alive.get(cur);if(p&&d){const ori=p.origin===0?0:p.team===d.team?p.origin:3;d.eats.push([seq,r,ori]);if(ori===0){T[d.team].nat++;if(r<100)T[d.team].nat100++;}}}
  }else if(e.type==='dragonSplit'){const p=alive.get(e.parentId);if(!p)continue;
   p.splits.push([seq,r,e.childId,e.childBody.length,e.parentBody.length]);clear(p);p.body=e.parentBody.map(x=>({...x}));put(p);born(e.childId,e.team,e.childBody,p.id,seq,r);
   if(e.childBody.length<=3&&r>=250)T[e.team].births250++;if(e.childBody.length<=3&&r>=300)T[e.team].births300++;
  }else if(e.type==='dragonDeath'){const d=alive.get(e.id);if(!d)continue;const isK=king(d.team)?.id===d.id&&d.body.length>=8;
   let cause='other',hit=null;
   if(cur!==d.id){cause='rammed';hit=alive.get(cur)||null;}
   else if(e.reason==='H'){cause='ram';}
   else if(e.reason==='A'&&d.tle)cause='fault';
   else if(e.reason==='A'&&d.action?.kind==='move'&&d.action.steps.length>=2)cause='sprintDeath';
   else if(e.reason==='W'||e.reason==='S'||e.reason==='A')cause=d.free>0?'sac':'trap';
   else if(e.reason==='O'){
    const dir=d.action?.steps?.[d.updates],n=dir?across(d.body[0],dir):null;hit=n?D.get(occ.get(key(n.x,n.y))):null;
    if(hit?.team===d.team)cause=d.free>0?'sac':'trap';else cause=d.free>0?'enemyBody':'trap';
   }
   const rec={id:d.id,r,seq,team:d.team,cause,reason:e.reason,len:d.body.length,king:isK,free:d.free,hitId:hit?.id??null,hitLength:hit?.body.length??null,idx:deaths.length};
   deaths.push(rec);if(cause==='sac'){T[d.team].sac++;if(r<300)T[d.team].sac300++;}
   if(isK)T[d.team].kd.push(rec);
   clear(d);alive.delete(d.id);d.died=seq;dropping=rec;
  }
 }
 const result={};
 for(const tm of ['A','B']){
  const k=king(tm),o={...T[tm],final:k?.body.length||0,finalId:k?.id??-1,finalUnits:[...alive.values()].filter(x=>x.team===tm).length,lineSacAll:null,lineSac300:null,lineage300:null,lineNatural300:null,lineOther300:null,lineEnemy300:null,lineSprint300:null,lineSplit300:null,exposure:null,exposureTurns:0};
  if(k){const line=[];for(let d=k;d;d=d.parent<0?null:D.get(d.parent))line.push(d);line.reverse();o.lineIds=line.map(d=>d.id);let env=[0,0],sacAll=0,gain=[0,0,0,0],split=0;
   for(let i=0;i<line.length;i++){const d=line[i],from=d.born,to=i+1<line.length?line[i+1].born:Infinity;
    for(const x of d.env)if(x[0]>from&&x[0]<to){env[0]++;env[1]+=x[2];}
    for(const x of d.eats)if(x[0]>from&&x[0]<to){if(x[2]===1)sacAll++;if(x[1]>=300)gain[x[2]]++;}
    for(const x of d.splits)if(x[0]>from&&x[0]<=to&&x[1]>=300)split+=(i+1<line.length&&x[2]===line[i+1].id)?x[4]:x[3];
    if(d.checkpoint[300]!==undefined)o.lineage300=d.checkpoint[300];
   }
   o.lineSacAll=sacAll;o.exposureTurns=env[0];o.exposure=env[0]?env[1]/env[0]:null;
   if(o.lineage300!==null){o.lineNatural300=gain[0];o.lineSac300=gain[1];o.lineOther300=gain[2];o.lineEnemy300=gain[3];o.lineSplit300=split;
    // The identity independently derives sprint spending from the official body lengths.
    o.lineSprint300=o.lineage300+sum(gain)-split-o.final;
   }
  }
  result[tm]=o;
 }
 const edges=[...M.initialHEdges,...M.initialVEdges],layout={width:W,height:H,area:W*H,kelpEdges:edges.filter(x=>x===1).length,edgeCount:edges.length,portalPairs:(M.portals||[]).length,initialHeadsA:M.initialDragons.filter(x=>x.team==='A').length,initialHeadsB:M.initialDragons.filter(x=>x.team==='B').length};
 return {key:g.key,id:g.id,checkpoints,rounds:r+1,teams:result,layout,deaths:deaths.filter(x=>x.king||x.cause==='fault')};
}
const mismatch=[],sums={primary:{n:0,w:0,d:0,l:0,eliminated:0,ownFinal:0,enemyFinal:0,ownNatural:0,enemyNatural:0,ownSac:0,enemySac:0},independent:{n:0,w:0,d:0,l:0,eliminated:0,ownFinal:0,enemyFinal:0,ownNatural:0,enemyNatural:0,ownSac:0,enemySac:0}};
let done=0;
for(const g of games){guard();const R=load(g.file),raw=reconstruct(R,g),us=g.ourSide,en=us==='A'?'B':'A',a=raw.teams[us],b=raw.teams[en];
 const compare=(field,p,v)=>{if(p!==v&&!(p===null&&v===undefined)&&!(typeof p==='number'&&typeof v==='number'&&Math.abs(p-v)<1e-9))mismatch.push({key:g.key,field,primary:p,independent:v});};
 compare('rounds',g.rounds,raw.rounds);
 for(const [prefix,t]of[['our',a],['their',b]]){
  compare(prefix+'Final',g[prefix+'Final'],t.final);compare(prefix+'FinalUnits',g[prefix+'FinalUnits'],t.finalUnits);
  compare(prefix+'ResultFinal',R.result['team'+(prefix==='our'?us:en)].longestDragon,t.final);
  for(const c of[10,50,100,250,300,400]){compare(prefix+'Heads'+c,g[prefix+'Heads'+c],raw.checkpoints[c]?.[prefix==='our'?us:en]?.heads??null);compare(prefix+'King'+c,g[prefix+'King'+c],raw.checkpoints[c]?.[prefix==='our'?us:en]?.king??null);}
  compare(prefix+'Natural',g[prefix+'Natural'],t.nat);compare(prefix+'Natural100',g[prefix+'Natural100'],t.nat100);
  compare(prefix+'Sacrifices',g[prefix+'Sacrifices'],t.sac);compare(prefix+'Sacrifices300',g[prefix+'Sacrifices300'],t.sac300);
  for(const [p,q]of[['Lineage300','lineage300'],['LineSac300','lineSac300'],['LineNatural300','lineNatural300'],['LineOwnOther300','lineOther300'],['LineEnemy300','lineEnemy300'],['LineSprint300','lineSprint300'],['LineSplit300','lineSplit300']])compare(prefix+p,g[prefix+p],t[q]);
  if(g.endgameCached){compare(prefix+'Exposure',g[prefix+'Exposure'],t.exposure);compare(prefix+'ExposureTurns',g[prefix+'ExposureTurns'],t.exposureTurns);}
 }
 const winner=R.result.winner||null, oc=winner===us?'w':winner===en?'l':'d';
 for(const kind of ['primary','independent']){const z=sums[kind];z.n++;z[kind==='primary'?g.outcome.toLowerCase():oc]++;z.eliminated+=kind==='primary'?g.ourEliminated:a.finalUnits===0;z.ownFinal+=kind==='primary'?g.ourFinal:a.final;z.enemyFinal+=kind==='primary'?g.theirFinal:b.final;z.ownNatural+=kind==='primary'?g.ourNatural:a.nat;z.enemyNatural+=kind==='primary'?g.theirNatural:b.nat;z.ownSac+=kind==='primary'?g.ourSacrifices:a.sac;z.enemySac+=kind==='primary'?g.theirSacrifices:b.sac;}
 fs.writeSync(out,JSON.stringify(raw)+'\n');done++;if(done%70===0)console.log('recount '+done+'/'+games.length+' mismatches='+mismatch.length);
}
fs.closeSync(out);fs.closeSync(log);
fs.writeFileSync(dir+'/recount-checks.json',JSON.stringify({sums,mismatchCount:mismatch.length,mismatches:mismatch},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({sums,mismatchCount:mismatch.length,first:mismatch.slice(0,6)}));
