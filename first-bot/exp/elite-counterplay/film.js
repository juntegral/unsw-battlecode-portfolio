#!/usr/bin/env node
// Stage 3. Only the frozen selection from selection.json is deep-read.
// Two lowest-ID losses in each team's largest class + lowest-ID win; no-win
// teams explicitly keep that absence. One top example of the matching class's
// signature (lowest game ID, nonstalled win). No game selection by anecdotes.
// E1/E3/E4 -> swarm50, E2/K5 -> sprintKingRam, I6 -> homeRaid, C7/G8 -> kingFeed.
// Film preserves full actions for final king lineages, last three victims and
// killers, initial king, and most productive invading dragon; all deaths/splits
// and every 10-round team state are included. No inferred opponent intentions.
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process');
const ROOT=path.resolve(__dirname,'../..'),C=path.join(ROOT,'.cache/elite-counterplay');
const {load}=require(path.join(ROOT,'tools/replay.js')),ML=require(path.join(ROOT,'tools/mass_ledger.js'));
const man=JSON.parse(fs.readFileSync(path.join(C,'manifest.json'),'utf8'));
const selection=JSON.parse(fs.readFileSync(path.join(C,'selection.json'),'utf8'));
const agg=JSON.parse(fs.readFileSync(path.join(C,'aggregate.json'),'utf8'));
const ts=new Map(man.tasks.map(t=>[t.key,t]));
function guard(){
 const m=/System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure',{encoding:'utf8'}));
 const d=+cp.execFileSync('df',['-g','/'],{encoding:'utf8'}).trim().split('\n').pop().trim().split(/\s+/)[3];
 if(!m||+m[1]<10||d<20)process.exit(75);
}
function analyse(R,task){
 const actions=new Map(),labels=new Map(),deaths=[],splits=[],eats=[],snaps=[],byId=new Map(),enemyNat=new Map();
 const us=task.us||'A',sumTeam=(c,t)=>{const ds=[...c.drag.values()].filter(d=>d.team===t),k=c.kingOf(t);return{u:ds.length,total:ds.reduce((s,d)=>s+d.body.length,0),kingId:k?.id??null,kingLen:k?.body.length||0};};
 let lastRound=-1,final=null,line={};
 const hooks={
  turn(d,r,c){
   if(r!==lastRound){lastRound=r;if(r%10===0||[30,50,100,250,340,350,400,450,499].includes(r))snaps.push({r,A:sumTeam(c,'A'),B:sumTeam(c,'B')});}
   const head=d.body[0];let a3=0,e3=0,a8=0,e8=0;
   for(const o of c.drag.values()){if(o===d)continue;const dst=c.tdist(head,o.body[0]);if(o.team===d.team){if(dst<=3)a3++;if(dst<=8)a8++;}else{if(dst<=3)e3++;if(dst<=8)e8++;}}
   d.film={r,id:d.id,team:d.team,L:d.body.length,head:{...head},king:c.isKingNow(d),a3,e3,a8,e8,tag:''};
  },
  indicator(e,r,c){labels.set(e.id,e.text);const d=c.drag.get(e.id);if(d?.film)d.film.tag=e.text;},
  action(d,e,r,c,before){const a={...d.film,kind:e.action?.kind||null,steps:e.action?.steps?.join('')||'',end:{...d.body[0]},endLen:d.body.length,fate:d.fate};
    let list=actions.get(d.id);if(!list)actions.set(d.id,list=[]);list.push(a);},
  split(p,ch,e,r,c){splits.push({r,id:p.id,child:ch.id,team:p.team,L:p.body.length+ch.body.length,kept:p.body.length,childLen:ch.body.length,
    head:{...p.body[0]},childHead:{...ch.body[0]},tag:labels.get(p.id)||''});},
  eat(d,k,origin,r,c){const rec={r,id:d.id,team:d.team,x:k%c.W,y:(k/c.W)|0,origin,territory:c.terr[k],king:c.isKingNow(d)};eats.push(rec);
    if(origin<0&&c.terr[k]!==0&&c.terr[k]!== (d.team==='A'?1:2))enemyNat.set(d.id,(enemyNat.get(d.id)||0)+1);},
  death(d,rec,idx,o,r,c){deaths.push({r,id:d.id,team:d.team,L:d.body.length,king:c.isKingNow(d),head:{...d.body[0]},cause:ML.CAUSE[rec.cause],
    killer:o?.id??null,killerLen:o?.body.length??null,killerSteps:rec.cause===2?o?.steps||0:0,turn:d.film,tag:labels.get(d.id)||'',rec,idx});},
  end(r,c){
    final={r,A:sumTeam(c,'A'),B:sumTeam(c,'B')};
    for(const t of ['A','B']){let d=c.kingOf(t),a=[];while(d){a.push({id:d.id,born:d.born,L:d.body.length});d=d.parent>=0?c.all.get(d.parent):null;}line[t]=a.reverse();}
    for(const [id,d]of c.all)byId.set(id,{id,team:d.team,parent:d.parent,born:d.born,finalLen:d.body.length,alive:c.drag.has(id)});
  }
 };
 const g=ML.perGame(R,{map:task.map,variant:task.map==='Prisoners Dilemma'&&R.match.map.initialDragons.length===10?'PD10':null},hooks);
 if(Object.values(g.chk).some(x=>x!==0))throw Error('Film reconstruction mismatch');
 const victims=deaths.filter(d=>d.team===us),track=new Set();
 for(const d of victims.slice(-3)){track.add(d.id);if(d.killer!==null)track.add(d.killer);}
 for(const d of victims.filter(d=>d.king&&d.L>=8&&d.cause==='rammed').slice(0,1)){track.add(d.id);if(d.killer!==null)track.add(d.killer);}
 for(const t of ['A','B'])for(const d of line[t])track.add(d.id);
 const invading=[...enemyNat].sort((a,b)=>b[1]-a[1]||a[0]-b[0]).slice(0,2);for(const [id]of invading)track.add(id);
 const init=R.match.map.initialDragons.filter(d=>d.team===us).sort((a,b)=>b.body.length-a.body.length||a.id-b.id)[0];if(init)track.add(init.id);
 const trackActions=Object.fromEntries([...track].map(id=>[id,actions.get(id)||[]]));
 return {key:task.key,map:task.map,us:task.us,opponent:task.oppId,src:task.src,result:R.result,rounds:g.rounds,seed:R.seed,
   size:[R.match.map.width,R.match.map.height],snaps,final,line,invaders:invading,dragons:Object.fromEntries(byId),
   deaths,splits,eats,actions:trackActions,checks:g.chk};
}
async function main(){
 const wanted=new Map();
 for(const [id,s]of Object.entries(selection.teams)){
  for(const key of [...s.losses,...s.win])wanted.set(key,{team:+id,kind:s.win.includes(key)?'win':'loss',class:s.largestClass});
  const sig=['E1','E3','E4'].includes(s.largestClass)?'swarm50':['E2','K5'].includes(s.largestClass)?'sprintKingRam':s.largestClass==='I6'?'homeRaid':'kingFeed';
  const key=agg.reference[id].signatureExample[sig];if(key)wanted.set(key,{team:+id,kind:'reference',signature:sig});
 }
 fs.mkdirSync(path.join(C,'films'),{recursive:true});
 const output=[];
 for(const [key,purpose]of wanted){
  const task=ts.get(key);if(!task)throw Error(`Missing selected task ${key}`);guard();
  const filename=path.join(C,'films',key.replace(':','-')+'.json');
  if(!fs.existsSync(filename)){
   const data=analyse(load(path.join(ROOT,task.file)),task);
   fs.writeFileSync(filename,JSON.stringify({...data,purpose})+'\n');
  }
  output.push({key,...purpose,file:path.relative(ROOT,filename)});console.log(`film ${key} ${purpose.kind}`);
  await new Promise(resolve=>setTimeout(resolve,50));
 }
 fs.writeFileSync(path.join(C,'film-index.json'),JSON.stringify(output,null,2)+'\n');
}
if(require.main===module)main().catch(e=>{console.error(e.stack);process.exitCode=1;});
