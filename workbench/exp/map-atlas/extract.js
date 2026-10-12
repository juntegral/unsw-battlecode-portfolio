// Offline atlas. Two workers maximum; all writes confined to exp/map-atlas/cache.
// Independent reconstruction: replay head/tail updates, not mass_ledger movement simulation.
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'../..'), OUT=path.join(__dirname,'cache');
const raw=require(path.join(ROOT,'legacy/exp/intake-gap/rawload.js'));
const {parseInd}=require(path.join(ROOT,'tools/mech_check.js'));
const MAPS={'Autarky':'autarky','Default':'default','Devil':'devil','Portals':'portals','Prisoners Dilemma':'prisoners_dilemma','Queen Of Spades':'queen_of_spades','Schooltime':'schooltime','Slithery Fight':'slithery_fight','Trauma':'trauma','Trophy':'trophy'};
const BMAPS=new Set(['Devil','Queen Of Spades','Schooltime','Slithery Fight']);
const WAVE=['cand-merge2-online','cand-merge2-online-r2','cand-merge2-online-r3',...Array.from({length:6},(_,i)=>`cand-stack${i+1}-online`),'cand-stack6-online-r2',...Array.from({length:5},(_,i)=>`cand-stack${i+7}-online`)];
const EARLY=['baseline-r1','baseline-r1b','baseline-r1c','cand-avoid6-online','cand-portal1-online','cand-swarm8-online','base-px8-online','base-px9d-online','px-king-v2-online'];
const CHECKPOINTS=[0,10,25,50,100,150,250,300,350,400,450,500],PH=[0,50,100,250,350,450,500];
const phase=r=>r<50?0:r<100?1:r<250?2:r<350?3:r<450?4:5;
const readl=f=>fs.readFileSync(f,'utf8').split('\n').filter(Boolean).map(JSON.parse);
const gaps=new Map(), graphCache=new Map();
let assignments={};try {const a=JSON.parse(fs.readFileSync(path.join(ROOT,'data/pearl_layout/variants.json'),'utf8'));for(const c of Object.values(a.cats))Object.assign(assignments,c.assign||{});}catch{}
function gapFile(map,lay){return path.join(ROOT,lay==='b'||lay==='10'?'maps/variants':'maps/online-20260927',lay==='10'?'prisoners_dilemma_10.map':MAPS[map]+(lay==='b'?'_b':'')+'.map');}
function gapOf(map,lay){const f=gapFile(map,lay);if(!gaps.has(f)){const lines=fs.readFileSync(f,'utf8').split('\n'),[w,h]=lines[0].split(' ').slice(1).map(Number),g=new Array(w*h).fill(null);for(const l of lines)if(l.startsWith('TILE ')){const[x,y,a,b]=l.split(/\s+/).slice(1).map(Number);g[y*w+x]=[a,b];}gaps.set(f,{w,h,g});}return gaps.get(f);}
function identify(R,map,gameId){
 if(map==='Prisoners Dilemma')return {layout:R.match.map.initialDragons.length===10?'10':'6',evidence:'initial dragons'};
 if(!BMAPS.has(map))return {layout:'a',evidence:'single'};
 const ga=gapOf(map,'a'),gb=gapOf(map,'b'),w=R.match.map.width;let ca=0,cb=0,drop=false;
 for(const e of R.events){if(e.type==='dragonDeath'){drop=true;continue;}if(e.type==='tileChange'&&e.hasPearl){if(!drop){const k=e.tile.y*w+e.tile.x;if(!ga.g[k]||!ga.g[k][1])ca++;if(!gb.g[k]||!gb.g[k][1])cb++;}continue;}drop=false;}
 const assigned=assignments['g'+gameId],best=ca<cb?'a':cb<ca?'b':assigned==='a'||assigned==='b'?assigned:'?';
 return {layout:best,evidence:ca===cb?'assignment/ambiguous':'spawn support',ca,cb,assigned:assigned||null,disagreement:ca!==cb&&assigned&&assigned!==best?1:0};
}
function graph(M){
 const W=M.width,H=M.height,N=W*H,sha=crypto.createHash('sha1').update(JSON.stringify([W,H,M.initialHEdges,M.initialVEdges,M.portals])).digest('hex');
 if(graphCache.has(sha))return graphCache.get(sha);
 const wx=x=>(x+W)%W,wy=y=>(y+H)%H,nb=new Int32Array(N*4).fill(-1),port=new Map(),dxy=[[0,-1],[1,0],[0,1],[-1,0]];
 const canon=e=>e.side==='S'?{x:e.x,y:wy(e.y+1),side:'N'}:e.side==='E'?{x:wx(e.x+1),y:e.y,side:'W'}:e;
 for(const pair of M.portals||[]){const a=canon(pair[0]),b=canon(pair[1]);port.set(`${a.x},${a.y},${a.side}`,b);port.set(`${b.x},${b.y},${b.side}`,a);}
 let kelp=0,portalEdges=0;
 for(let k=0;k<N;k++){const x=k%W,y=k/W|0;
  for(let d=0;d<4;d++){const horizontal=d===0||d===2,ex=d===1?wx(x+1):x,ey=d===2?wy(y+1):y,ek=`${ex},${ey},${horizontal?'N':'W'}`,p=port.get(ek);
   const wall=horizontal?(M.initialHEdges[ey*W+ex]===1||(ey===0&&M.initialHEdges[H*W+ex]===1)):(M.initialVEdges[ey*(W+1)+ex]===1||(ex===0&&M.initialVEdges[ey*(W+1)+W]===1));
   if(d===0||d===3){kelp+=+wall;portalEdges+=+!!p;}
   if(p){let px=p.x,py=p.y;if(d===0)py=wy(py-1);if(d===3)px=wx(px-1);nb[k*4+d]=py*W+px;}else if(!wall)nb[k*4+d]=wy(y+dxy[d][1])*W+wx(x+dxy[d][0]);
  }
 }
 const G={W,H,N,nb,sha,kelp,portalEdges};graphCache.set(sha,G);return G;
}
function bfs(G,seeds){const out=new Int16Array(G.N).fill(999),q=new Int32Array(G.N);let tail=0;for(const k of seeds)if(out[k]!==0){out[k]=0;q[tail++]=k;}for(let i=0;i<tail;i++){const k=q[i];for(let d=0;d<4;d++){const n=G.nb[k*4+d];if(n>=0&&out[n]===999){out[n]=out[k]+1;q[tail++]=n;}}}return out;}
function reconstruct(R,task){
 const M=R.match.map,G=graph(M),{W,H,N}=G,lay=identify(R,task.map,task.gameId),gtag=lay.layout==='6'?'a':lay.layout;
 const gap=gtag==='?'?null:gapOf(task.map,gtag).g;
 const da=bfs(G,M.initialDragons.filter(x=>x.team==='A').flatMap(x=>x.body.map(p=>p.y*W+p.x))),db=bfs(G,M.initialDragons.filter(x=>x.team==='B').flatMap(x=>x.body.map(p=>p.y*W+p.x)));
 const terr=new Int8Array(N),cap=[0,0,0],tiles=[0,0,0],fountains=[0,0,0];for(let k=0;k<N;k++){terr[k]=da[k]<db[k]?1:db[k]<da[k]?2:0;tiles[terr[k]]++;const g=gap&&gap[k];if(g&&g[1]){cap[terr[k]]+=2/(g[0]+g[1]);if((g[0]+g[1])/2<=12)fountains[terr[k]]++;}}
 const drag=new Map(),all=new Map(),occ=new Int32Array(N).fill(-1),pearls=new Int32Array(N).fill(-2),deaths=[],cpSeq={};
 let cur=-1,round=-1,seq=0,drop=-1,spawned=0;
 const T={};for(const t of ['A','B'])T[t]={cp:{},phase:PH.slice(0,6).map(()=>({rounds:0,headRounds:0,eligibleHR:0,eligibleTurns:0,splits:0,birthsSmall:0,births22:0,nat:0,sacN:0,sacLen:0,sacDrops:0,raidHR:0})),exposure:[[0,0,0,0],[0,0,0,0]],sac:[],kd:[],mech:{},turns:0,pings:0,splits:0};
 const key=p=>p.y*W+p.x,dist=(a,b)=>{const dx=Math.abs(a%W-b%W),dy=Math.abs((a/W|0)-(b/W|0));return Math.min(dx,W-dx)+Math.min(dy,H-dy);};
 const clear=d=>{for(const k of d.body)if(occ[k]===d.id)occ[k]=-1;};const put=d=>{for(const k of d.body)occ[k]=d.id;};
 const newD=(id,team,body,parent=-1)=>{const d={id,team,body:body.map(key),parent,born:round<0?0:round,bornSeq:seq,eats:[],splits:[],lens:{},label:null,free:0,steps:[],upds:0,death:null};drag.set(id,d);all.set(id,d);put(d);return d;};
 for(const d of M.initialDragons)newD(d.id,d.team,d.body);
 for(let k=0;k<N;k++)if(M.initialTiles[k]===2)pearls[k]=-1;
 const king=t=>{let k=null;for(const d of drag.values())if(d.team===t&&(!k||d.body.length>k.body.length||d.body.length===k.body.length&&d.id<k.id))k=d;return k;};
 const nearestEnemy=d=>{let v=999;for(const o of drag.values())if(o.team!==d.team)v=Math.min(v,dist(d.body[0],o.body[0]));return v;};
 const snapshot=r=>{
  cpSeq[r]=seq;for(const d of drag.values())d.lens[r]=d.body.length;
  for(const t of ['A','B']){const ds=[...drag.values()].filter(x=>x.team===t),k=king(t),a=bfs(G,ds.map(d=>d.body[0])),b=bfs(G,[...drag.values()].filter(x=>x.team!==t).map(d=>d.body[0]));let winCap=0,enemyCap=0,ownCap=0;
   for(let j=0;j<N;j++){const q=gap&&gap[j],c=q&&q[1]?2/(q[0]+q[1]):0;if(terr[j]===(t==='A'?1:2)){ownCap+=c;if(a[j]<b[j])winCap+=c;if(a[j]>b[j])enemyCap+=c;}}
   T[t].cp[r]={heads:ds.length,king:k?k.body.length:0,total:ds.reduce((s,d)=>s+d.body.length,0),pieces:ds.filter(d=>d.body.length<=4).length,vor:ownCap?winCap/ownCap:null,enemyNear:ownCap?enemyCap/ownCap:null,raid:ds.filter(d=>terr[d.body[0]]===(t==='A'?2:1)).length,kdist:k?nearestEnemy(k):null};
  }
 };
 snapshot(0);
 let firstTurn=true;
 const mechOf=(t,name)=>T[t].mech[name]||(T[t].mech[name]={n:0,applied:0,nat:0,records:[]});
 for(const e of R.events){seq++;if(drop>=0&&!(e.type==='tileChange'&&e.hasPearl))drop=-1;
  if(e.type==='roundStart'){round=e.round;firstTurn=true;if(CHECKPOINTS.includes(round)&&round!==0)snapshot(round);
   for(const t of ['A','B']){const ds=[...drag.values()].filter(x=>x.team===t),p=T[t].phase[phase(round)];p.rounds++;p.headRounds+=ds.length;p.eligibleHR+=ds.filter(d=>d.body.length>=4).length;p.raidHR+=ds.filter(d=>terr[d.body[0]]===(t==='A'?2:1)).length;}
  }else if(e.type==='turnStart'){cur=e.id;const d=drag.get(cur);if(!d)throw Error('turn for missing dragon');d.free=0;for(let z=0;z<4;z++){const v=G.nb[d.body[0]*4+z];if(v>=0&&occ[v]<0)d.free++;}d.label=null;d.tags=[];d.steps=[];d.upds=0;T[d.team].turns++;if(d.body.length>=4)T[d.team].phase[phase(round)].eligibleTurns++;
   if(firstTurn){firstTurn=false;if(round>=300)for(const t of ['A','B']){const k=king(t);if(k&&k.body.length>=8){const v=nearestEnemy(k),a=T[t].exposure[round<400?0:1];a[0]++;a[1]+=+(v<=3);a[2]+=+(v<=6);a[3]+=Math.min(v,30);}}}
  }else if(e.type==='dragonIndicator'){const d=drag.get(e.id);if(!d)continue;const p=parseInd(e.text);d.label=p;let tags=[];if(p.kind==='move'){if(p.fg)tags.push('F');if(p.f2)tags.push('F2');if(p.cl)tags.push('cl');if(p.cov)tags.push('cov');if(p.goalDist!==null&&/^g/.test(p.goal||''))tags.push('g');if(p.grab)tags.push('grab');if(p.tg)tags.push('tg');if(p.esc)tags.push('esc');if(p.lntv!==undefined)tags.push('lnt veto');}else if(['csplit','lsplit','frag','conv','feed','escsplit','escsplit2','noexit','floor','kcap','bsplit','pf'].includes(p.kind))tags.push(p.kind==='bsplit'?'bsp':p.kind==='escsplit'?'escape-split':p.kind==='escsplit2'?'esc-split':p.kind==='noexit'?'no-exit':p.kind);
   d.tags=tags;for(const tag of tags){const v=mechOf(d.team,tag);v.n++;if(v.records.length<10000)v.records.push([d.id,round,seq]);}
  }else if(e.type==='dragonAction'){const d=drag.get(e.id);if(!d)continue;d.steps=e.action&&e.action.kind==='move'?e.action.steps:[];d.action=e.action;d.tle=!!e.tle;
   for(const tag of d.tags||[])if(['F','F2','cl','cov','g','grab','tg','esc','lnt veto'].includes(tag)&&e.action&&e.action.kind==='move')mechOf(d.team,tag).applied++;
  }else if(e.type==='tileChange'){const k=key(e.tile);if(e.hasPearl){pearls[k]=drop>=0?drop:-1;if(drop<0)spawned++;}else{const d=drag.get(cur);if(!d)throw Error('eat for missing dragon');const origin=pearls[k];if(origin===-2)throw Error('unpaired pearl');d.eats.push([seq,round,origin]);if(origin===-1)T[d.team].phase[phase(round)].nat++;for(const tag of d.tags||[])if(origin===-1)mechOf(d.team,tag).nat++;pearls[k]=-2;}}
  else if(e.type==='dragonUpdate'){const d=drag.get(e.id);if(!d)throw Error('update for missing dragon');clear(d);const h=key(e.head),tail=key(e.tail),old=d.body[0],step=d.steps[d.upds],dx=step==='E'?1:step==='W'?-1:0,dy=step==='S'?1:step==='N'?-1:0,ordinary=((old/W|0)+dy+H)%H*W+(old%W+dx+W)%W;if(step&&h!==ordinary){const v=mechOf(d.team,'portal');v.n++;v.applied++;v.records.push([d.id,round,seq]);}if(d.body[0]!==h)d.body.unshift(h);while(d.body.length>1&&d.body[d.body.length-1]!==tail)d.body.pop();if(d.body.length<2)throw Error('short reconstructed body');d.upds++;put(d);}
  else if(e.type==='dragonSplit'){const d=drag.get(e.parentId);if(!d)throw Error('split for missing dragon');clear(d);d.body=e.parentBody.map(key);put(d);const ch=newD(e.childId,e.team,e.childBody,d.id);d.splits.push([seq,round,ch.id]);T[d.team].splits++;const p=T[d.team].phase[phase(round)];p.splits++;p.birthsSmall+=+(ch.body.length<=3);p.births22+=+(ch.body.length===2&&d.body.length===2);for(const tag of d.tags||[])if(['csplit','lsplit','frag','floor','kcap','bsp','pf','escape-split','esc-split','no-exit'].includes(tag)){mechOf(d.team,tag).applied++;ch.origin=tag;}}
  else if(e.type==='dragonDeath'){const d=drag.get(e.id);if(!d)throw Error('death for missing dragon');const actor=drag.get(cur),mover=cur===d.id;let other=null,cause='other';
   if(!mover){other=actor;cause=actor&&actor.team===d.team?'allyHead':'rammed';}
   else if(e.reason==='H'){const prev=deaths[deaths.length-1];other=prev&&prev.r===round?all.get(prev.id):null;cause=other&&other.team===d.team?'allyHead':'ram';}
   else if(e.reason==='O'){const z='NESW'.indexOf(d.steps[d.upds]),v=z<0?-1:G.nb[d.body[0]*4+z];other=v>=0?all.get(occ[v]):null;cause=other&&other.team===d.team?(d.free?'sac':'trap'):(d.free?'enemyBody':'trap');}
   else if(e.reason==='A'&&d.tle)cause='fault';
   else if(e.reason==='A'&&d.steps.length>d.upds&&d.upds>0&&d.body.length<=2)cause='sprintDeath';
   else cause=d.free?'sac':'trap';
   const k=king(d.team),rec={id:d.id,team:d.team,r:round,len:d.body.length,cause,seq,king:k===d&&d.body.length>=8,killer:other?other.body.length:0,toOwn:0,toEnemy:0,toLine:0,nearKing:999};
   if(rec.king)T[d.team].kd.push([round,rec.len,cause,rec.killer,mover?1:0]);
   if(cause==='sac'){let near=999,nearBig=999;for(const o of drag.values())if(o.team===d.team&&o.id!==d.id){near=Math.min(near,dist(d.body[0],o.body[0]));if(o.body.length>rec.len)nearBig=Math.min(nearBig,dist(d.body[0],o.body[0]));}rec.near=near;rec.nearBig=nearBig;const p=T[d.team].phase[phase(round)];p.sacN++;p.sacLen+=rec.len;p.sacDrops+=Math.ceil(rec.len/2);T[d.team].sac.push(deaths.length);}
   for(const tag of d.tags||[])if(['conv','feed','no-exit'].includes(tag))mechOf(d.team,tag).applied+=+(cause==='sac'||cause==='trap');
   d.death=rec;deaths.push(rec);drop=deaths.length-1;clear(d);drag.delete(d.id);
  }
 }
 const rounds=round+1;snapshot(500);const chk={final:0,dropBalance:0};
 for(const t of ['A','B']){const end=R.result['team'+t],k=king(t),s=T[t].cp[500];if(s.heads!==end.dragonCount||s.king!==end.longestDragon||s.total!==end.totalLength)chk.final++;
  const line=[];for(let d=k;d;d=d.parent>=0?all.get(d.parent):null)line.push(d);line.reverse();const lineSet=new Map();for(let i=0;i<line.length;i++)lineSet.set(line[i].id,[line[i].bornSeq,i+1<line.length?line[i+1].bornSeq:Infinity]);
  const le=PH.slice(0,6).map(()=>[0,0,0,0]),lateEat=[0,0,0,0];
  for(const d of all.values())if(d.team===t)for(const e of d.eats){const [es,r,origin]=e,ls=lineSet.get(d.id),isLine=ls&&es>ls[0]&&es<ls[1];if(origin>=0){const v=deaths[origin];v[v.team===t?'toOwn':'toEnemy']++;if(isLine&&v.team===t)v.toLine++;}if(isLine){const cat=origin<0?0:deaths[origin].team!==t?3:deaths[origin].cause==='sac'?1:2;le[phase(r)][cat]++;if(r>=300)lateEat[cat]++;}}
  const lens={};for(const r of [300,350,400,450])if(rounds>r){let d=null;for(const x of line)if(x.bornSeq<(cpSeq[r]||0))d=x;lens[r]=d&&d.lens[r]!==undefined?d.lens[r]:null;}
  T[t].line={king:s.king,lens,eat:le,lateEat};T[t].pings=M.initialDragons.filter(d=>d.team===t).reduce((s,d)=>s+(R.sonarBySender.get(d.id)||0),0);for(const d of all.values())if(d.team===t&&d.parent>=0)T[t].pings+=R.sonarBySender.get(d.id)||0;
  T[t].sac=T[t].sac.map(i=>{const d=deaths[i];return[d.r,d.len,d.toOwn,d.toEnemy,d.toLine,d.near,d.nearBig];});
  for(const v of Object.values(T[t].mech)){let s3=0,s30=0;for(const [id,r] of v.records){const d=all.get(id);if(d&&(!d.death||d.death.r>=Math.min(r+3,rounds-1)))s3++;if(d&&(!d.death||d.death.r>=Math.min(r+30,rounds-1)))s30++;}v.alive3=s3;v.alive30=s30;delete v.records;}
 }
 const stall=rounds>=100?['A','B'].filter(t=>T[t].pings===0&&T[t].splits<=3):[];
 const init=M.initialDragons.map(d=>({id:d.id,team:d.team,len:d.body.length,head:d.body[0],body:d.body}));
 const geoFile=path.join(OUT,`geometry-${MAPS[task.map]}-${lay.layout}.json`);if(!fs.existsSync(geoFile)&&lay.layout!=='?')fs.writeFileSync(geoFile,JSON.stringify({map:task.map,layout:lay.layout,M,graphSha:G.sha,cap,tiles,fountains}));
 return {...task,file:undefined,rounds,endReason:R.result.endReason,winner:R.result.winner||null,layout:lay.layout,layoutEvidence:lay,stall,chk,spawned,init: init.map(d=>({id:d.id,team:d.team,len:d.len,head:d.head})),A:T.A,B:T.B};
}
function resource(){const mem=cp.execFileSync('memory_pressure',[],{encoding:'utf8'}),disk=cp.execFileSync('df',['-g','/'],{encoding:'utf8'}),m=/System-wide memory free percentage:\s*(\d+)%/.exec(mem),d=disk.trim().split('\n').pop().trim().split(/\s+/);return{memory:m?+m[1]:null,disk:+d[3]};}
function tasks(){const out=readl(path.join(OUT,'top-index.jsonl')).map(r=>({...r,key:r.battleId+':'+r.gameId,src:'top',us:null,file:path.join(ROOT,'data/top',String(r.battleId),r.gameId+'.replay.gz')}));
 for(const set of [...WAVE,...EARLY]){const f=path.join(ROOT,'data/online',set,'index.json');if(!fs.existsSync(f))throw Error('missing set '+set);for(const r of JSON.parse(fs.readFileSync(f,'utf8')).games)out.push({...r,key:set+':'+r.gameId,map:r.mapName,src:'online',set,wave:WAVE.includes(set)?WAVE.indexOf(set):null,us:r.ourSide,oppId:r.opponentTeam,file:path.join(ROOT,'data/online',set,'M'+r.gameId+'.replay')});}if(fs.existsSync(path.join(OUT,'local-tasks.jsonl')))out.push(...readl(path.join(OUT,'local-tasks.jsonl')));return out;}
if(require.main===module&&process.argv[2]==='worker'){process.on('message',task=>{try{const R=raw.load(task.file),v=reconstruct(R,task);process.send({key:task.key,row:v});}catch(e){process.send({key:task.key,error:String(e.stack)});}});}
else if(require.main===module){
 if(process.argv[2]==='one'){const t=tasks().find(x=>x.key===process.argv[3])||tasks()[0],start=Date.now(),v=reconstruct(raw.load(t.file),t);console.log(JSON.stringify({ms:Date.now()-start,v}));}
 else{const outfile=path.join(OUT,'raw.jsonl'),done=new Set(fs.existsSync(outfile)?readl(outfile).map(x=>x.key):[]),todo=tasks().filter(t=>!done.has(t.key));fs.writeFileSync(path.join(OUT,'tasks.jsonl'),tasks().map(x=>JSON.stringify(x)).join('\n')+'\n');let i=0,n=0,busy=0,paused=false;const workers=[],start=Date.now();
  function dispatch(w){if(paused)return;if(i>=todo.length){if(busy===0){for(const x of workers)x.kill();console.log('DONE',done.size+n,'elapsed_s',(Date.now()-start)/1000);}return;}if(n%100===0){const r=resource();if(r.memory===null||r.memory<10||r.disk<20){paused=true;console.log('PAUSED',JSON.stringify(r));for(const x of workers)x.kill();process.exitCode=75;return;}}const t=todo[i++];busy++;w.send(t);}
  console.log('population',todo.length,'already',done.size,'resource',resource());
  for(let z=0;z<2;z++){const w=cp.fork(__filename,['worker'],{execArgv:['--max-old-space-size=900'],stdio:['ignore','ignore','inherit','ipc']});workers.push(w);w.on('message',m=>{busy--;n++;if(m.error)fs.appendFileSync(path.join(OUT,'errors.jsonl'),JSON.stringify(m)+'\n');else fs.appendFileSync(outfile,JSON.stringify(m.row)+'\n');if(n%100===0)console.log('progress',n+'/'+todo.length,'seconds',Math.round((Date.now()-start)/1000));dispatch(w);});w.on('exit',(c,s)=>{if(i<todo.length&&!paused)console.log('worker exit',c,s);});dispatch(w);}
 }
}
module.exports={reconstruct,graph,bfs,gapOf,identify,resource,WAVE,EARLY};
