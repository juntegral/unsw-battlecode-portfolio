#!/usr/bin/env node
// Full frozen population, local replay analysis only. Never invokes tools' CLIs.
// Usage: python3 exp/elite-counterplay/guard.py node --max-old-space-size=768 exp/elite-counterplay/extract.js online|reference
// Exactly one computation process. Pause between replays if memory <10% or disk <20 GB.
// Writes only .cache/elite-counterplay. Resume skips completed unique keys.
//
// Definitions fixed before extraction / case reading:
// phases 0..4: [0,100), [100,250), [250,350), [350,450), [450,500).
// King = current longest, ties lower ID; substantive king L>=8.
// Local a3/e3,a8/e8: torus Manhattan distance <=3/8 from death head;
// exclude victim AND directly involved other dragon. d3/d8 = a-e.
// Territory is starting-body Voronoi on static movement graph (kelp/portals/wrap).
// Natural includes initial pearls, excludes every death drop.
// Successful sprint raid = an enemy's >=2-step action ramming current king L>=8.
// Raid approach proxy = shorter enemy sprint, starts <=8 from king, ends closer
// and <=3 (Manhattan; does not establish intention). Recorded separately.
// Pressure = e3>=2 AND e3>a3, excluding the deciding dragon.
// Cause follows mass ledger, raw engine reason retained: sac is a behavioral
// proxy (free exit at own-turn start), not inferred intentional sacrifice.
// Online keeps ALL deaths and phases; top keeps ALL ledger summaries.
'use strict';
const fs=require('fs'), path=require('path'), cp=require('child_process');
const ROOT=path.resolve(__dirname,'../..'), CACHE=path.join(ROOT,'.cache/elite-counterplay');
const ML=require(path.join(ROOT,'tools/mass_ledger.js'));
const {load}=require(path.join(ROOT,'tools/replay.js'));
const {parseInd}=require(path.join(ROOT,'tools/mech_check.js'));
const {variantOf}=require(path.join(ROOT,'exp/territory-analysis/extract.js'));
const manifest=JSON.parse(fs.readFileSync(path.join(CACHE,'manifest.json'),'utf8'));
const phase=r=>r<100?0:r<250?1:r<350?2:r<450?3:4;
const sides=['A','B'], other=t=>t==='A'?'B':'A';
const checkpoints=new Set([0,30,50,100,200,250,300,340,350,400,450]);

function guard(){
 const mem=cp.execFileSync('memory_pressure',{encoding:'utf8'}),df=cp.execFileSync('df',['-g','/'],{encoding:'utf8'});
 const m=/System-wide memory free percentage:\s*(\d+)%/.exec(mem), disk=+df.trim().split('\n').pop().trim().split(/\s+/)[3];
 if(!m)throw Error('Cannot read memory_pressure');
 if(+m[1]<10||disk<20){console.error(`RESOURCE PAUSE memory ${m[1]}% disk ${disk} GB`);process.exit(75);}
 return {free:+m[1],disk};
}
function analyse(R, task){
 const meta={...task}; delete meta.file;
 const variant=variantOf(task.map,task.gameId,R,R.match.map.initialDragons.length);
 const info={map:task.map,variant:task.map==='Prisoners Dilemma'?(R.match.map.initialDragons.length===10?'PD10':'PD6'):variant.tag};
 const rawReasons=new Map(R.events.filter(e=>e.type==='dragonDeath').map(e=>[e.id,e.reason]));
 const online=task.src==='online', deaths=[],raids=[],snaps={},tags={A:{},B:{}};
 const stats={};
 for(const t of sides)stats[t]={intake:Array.from({length:5},()=>({nat:[0,0,0],drop:[0,0,0]})),
   pressure:Array.from({length:5},()=>({turns:0,under:0,a3:0,e3:0,a8:0,e8:0})),
   kingExposure:Array.from({length:5},()=>({turns:0,enemy3:0,enemy8:0,under:0})),
   tagTurns:{},tagPressure:{},splits:[]};
 let lastRound=-1;
 const getLocal=(d,c,ex)=>{
  const a=[0,0,0,0];
  for(const o of c.drag.values()){
   if(o.id===d.id||o.id===ex)continue;
   const dst=c.tdist(o.body[0],d.body[0]),off=o.team===d.team?0:1;
   if(dst<=3)a[off]++;if(dst<=8)a[2+off]++;
  }return a;
 };
 const coarse=(reason,rec,d,o)=>rec.cause===2?'rammed':rec.cause===1?'trapped':
   reason==='S'||reason==='O'&&o&&o.team===d.team||rec.cause===5?'own_collision':
   rec.cause===0?'sacrifice':ML.CAUSE[rec.cause];
 const hooks=online?{
  turn(d,r,c){
   if(r!==lastRound){
    lastRound=r;
    if(checkpoints.has(r))snaps[r]=Object.fromEntries(sides.map(t=>{const ds=[...c.drag.values()].filter(x=>x.team===t);return[t,{units:ds.length,total:ds.reduce((n,x)=>n+x.body.length,0),king:c.kingOf(t)?.body.length||0}];}));
   }
   const lc=getLocal(d,c,-1),p=stats[d.team].pressure[phase(r)];
   p.turns++;p.a3+=lc[0];p.e3+=lc[1];p.a8+=lc[2];p.e8+=lc[3];
   const under=lc[1]>=2&&lc[1]>lc[0];if(under)p.under++;
   d.ecpTurn={r,h:{...d.body[0]},len:d.body.length,lc,under:!!under};
   if(c.isKingNow(d)&&d.body.length>=8){const k=stats[d.team].kingExposure[phase(r)];k.turns++;if(lc[1])k.enemy3++;if(lc[3])k.enemy8++;if(under)k.under++;}
  },
  indicator(e,r,c){
   const d=c.drag.get(e.id);if(!d)return;
   const ind=parseInd(e.text),tokens=[ind.kind];
   if(ind.trade)tokens.push('TRADE');if(ind.esc)tokens.push('esc');if(ind.fg)tokens.push('F');
   for(const k of ['tg','gx','cl','ce','cov','fp','f2','px2','ks','ks2','goal','lnt'])if(ind[k])tokens.push(k==='goal'?ind.goal:typeof ind[k]==='string'?ind[k]:k);
   tags[d.team][d.id]={r,text:e.text,tokens};
   for(const t of tokens){stats[d.team].tagTurns[t]=(stats[d.team].tagTurns[t]||0)+1;if(d.ecpTurn?.under)stats[d.team].tagPressure[t]=(stats[d.team].tagPressure[t]||0)+1;}
  },
  eat(d,k,origin,r,c){
   const mine=d.team==='A'?1:2,rel=c.terr[k]===mine?0:c.terr[k]===0?1:2;
   stats[d.team].intake[phase(r)][origin<0?'nat':'drop'][rel]++;
  },
  action(d,e,r,c,before){
   if(e.action?.kind!=='move'||e.action.steps.length<2)return;
   const k=c.kingOf(other(d.team));if(!k||k.body.length<8)return;
   const start=c.tdist(before[0],k.body[0]),end=c.tdist(d.body[0],k.body[0]);
   const hit=d.fate?.reason==='H'&&d.fate.hit===k.id;
   const approach=before.length<k.body.length&&start<=8&&end<=3&&end<start;
   if(hit||approach)raids.push({r,team:d.team,id:d.id,len:before.length,kingId:k.id,kingLen:k.body.length,
     start,end,steps:e.action.steps.join(''),hit:!!hit,approach:!!approach,from:before[0],to:d.body[0]});
  },
  split(p,ch,e,r,c){stats[p.team].splits.push({r,id:p.id,child:ch.id,parentLen:p.body.length,childLen:ch.body.length,tag:tags[p.team][p.id]?.text||''});},
  death(d,rec,idx,o,r,c){
   const reason=rawReasons.get(d.id),lc=getLocal(d,c,o?.id??-1),lab=tags[d.team][d.id];
   deaths.push({idx,id:d.id,team:d.team,r,phase:phase(r),len:d.body.length,cause:ML.CAUSE[rec.cause],coarse:coarse(reason,rec,d,o),reason,
    king:c.isKingNow(d)&&d.body.length>=8,kingAny:c.isKingNow(d),killerId:o?.id??null,killerTeam:o?.team??null,
    killerLen:o?.body.length??null,killerSteps:rec.cause===2?o?.steps||0:0,free:d.free,
    a3:lc[0],e3:lc[1],a8:lc[2],e8:lc[3],d3:lc[0]-lc[1],d8:lc[2]-lc[3],head:{...d.body[0]},
    enemyBlock:d.enemyBlock,allyBlock:d.allyBlock,turn:d.ecpTurn||null,tag:lab?.text||'',tagRound:lab?.r??null,
    born:d.born,parent:d.parent,stub:rec.mech,rec});
  },
  end(r,c){
   snaps.final=Object.fromEntries(sides.map(t=>{const ds=[...c.drag.values()].filter(x=>x.team===t);return[t,{units:ds.length,total:ds.reduce((n,x)=>n+x.body.length,0),king:c.kingOf(t)?.body.length||0}];}));
  }
 }:null;
 const ledger=ML.perGame(R,info,hooks);
 if(Object.values(ledger.chk).some(n=>n!==0))throw Error(`Reconstruction mismatch ${task.key}: ${JSON.stringify(ledger.chk)}`);
 const result={...meta,seed:R.seed,variant:variant.tag,variantHow:variant.how,...ledger};
 if(online){
  for(const t of sides){
   stats[t].elimination=snaps.final[t].units===0?Math.max(...deaths.filter(x=>x.team===t).map(x=>x.r)):null;
   const et=stats[t].elimination;
   if(et!==null&&et!==ledger.rounds-1)throw Error('Elimination round mismatch');
  }
  result.extra={deaths,raids,snaps,stats};
 }
 return result;
}
async function main(){
 const mode=process.argv[2];if(!['online','reference'].includes(mode))throw Error('Expected online or reference');
 const shardAt=process.argv.indexOf('--shard'),shard=shardAt>=0?process.argv[shardAt+1].split('/').map(Number):null;
 if(shard&&(mode!=='reference'||shard.length!==2||shard[1]!==2||![0,1].includes(shard[0])))throw Error('Only reference shards 0/2 or 1/2');
 const output=path.join(CACHE,shard?`reference-shard-${shard[0]}.jsonl`:mode+'.jsonl'),done=new Set();
 for(const name of shard?['reference.jsonl',`reference-shard-${shard[0]}.jsonl`]:[mode+'.jsonl']){
  const f=path.join(CACHE,name);if(fs.existsSync(f))for(const l of fs.readFileSync(f,'utf8').split('\n'))if(l.trim())done.add(JSON.parse(l).key);
 }
 const tasks=manifest.tasks.filter(t=>(mode==='online'?t.src==='online':t.src==='top')).filter((t,i)=>(!shard||i%shard[1]===shard[0])&&!done.has(t.key));
 console.log(JSON.stringify({mode,total:tasks.length,cached:done.size,guard:guard()}));
 const fd=fs.openSync(output,'a'),start=Date.now();
 for(let i=0;i<tasks.length;i++){
  // Check at every game boundary. Flush each complete JSON line so resuming is safe.
  if(i%25===0)guard();
  const t=tasks[i],R=load(path.join(ROOT,t.file)),result=analyse(R,t);
  fs.writeSync(fd,JSON.stringify(result)+'\n');
  if((i+1)%25===0||i+1===tasks.length)console.log(`${mode} ${i+1}/${tasks.length}, ${Math.round((Date.now()-start)/1000)}s, ${t.key}`);
  // Yield to other local games; no parallel worker pool.
  await new Promise(resolve=>setTimeout(resolve,50));
 }
 fs.closeSync(fd);
}
if(require.main===module)main().catch(e=>{console.error(e.stack);process.exitCode=1;});
module.exports={analyse};
