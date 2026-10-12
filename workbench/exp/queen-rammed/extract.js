'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'../..'),OUT=__dirname;
const {makeLoader,viewerSource}=require('../../tools/top_features'),ML=require('../../tools/mass_ledger');
const load=makeLoader(viewerSource()),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const inv=JSON.parse(fs.readFileSync(path.join(OUT,'inventory.json'))),seen=new Map(),games=[],checks={},errors=[];
fs.mkdirSync(path.join(OUT,'raw'),{recursive:true});
function fingerprint(R){const h=crypto.createHash('sha256');for(const e of R.events){if(['dragonIndicator','dragonLog','debugDraw','engineLog'].includes(e.type))continue;const o={};for(const[k,v]of Object.entries(e))if(k!=='instructions')o[k]=typeof v==='bigint'?String(v):v;h.update(JSON.stringify(o));}return h.digest('hex');}
function snapshot(c,r){return {round:r,W:c.W,H:c.H,dragons:[...c.drag.values()].map(d=>({id:d.id,team:d.team,body:d.body.map(p=>({...p})),born:d.born,parent:d.parent})),pearls:[...c.pearls.keys()]};}
function extract(R,t,id){
 const M=R.match.map,Q=Math.min(...M.initialDragons.filter(d=>d.team===t.row.side).map(d=>d.id)),rawDeath=new Map();let round=-1,cur=-1;
 for(const e of R.events){if(e.type==='roundStart')round=e.round;if(e.type==='turnStart')cur=e.id;if(e.type==='dragonDeath')rawDeath.set(e.id,{round,reason:e.reason,mover:cur});}
 const out={id,dir:t.dir,key:t.key,file:t.file,side:t.row.side,map:t.row.map,seed:t.row.seed,opponent:path.basename(t.row.opp),role:t.role,stratum:t.stratum,queenId:Q,death:null,rounds:null,queenAliveEnd:false,aliases:[{dir:t.dir,key:t.key,file:t.file,sourceLine:t.row.sourceLine}]};
 let last=null,previous=null,currentAction=null;const history=new Map(),turnStates=new Map(),ind=new Map(),qHistory=[];
 const res=ML.perGame(R,{map:t.row.map,rules:'123'}, {
  turn(d,r,c){
   turnStates.set(d.id,{round:r,L:d.body.length,body:d.body.map(p=>({...p})),born:d.born,parent:d.parent});
   if(d.id===Q&&t.role==='main'){previous=last;last=snapshot(c,r);qHistory.push({round:r,body:d.body.map(p=>({...p}))});if(qHistory.length>7)qHistory.shift();}
  },
  indicator(e,r){ind.set(e.id,{round:r,text:e.text||''});},
  action(d,e,r,c,b){const a={round:r,id:d.id,startLength:b.length,startBody:b.map(p=>({...p})),action:e.action,executed:d.expect?.length||0,endBody:d.body.map(p=>({...p})),fate:d.fate,indicator:ind.get(d.id)?.text||null};history.set(d.id,a);currentAction=a;},
  death(d,rec,idx,other,r,c){if(d.id!==Q)return;
   out.death={round:r,cause:ML.CAUSE[rec.cause],reason:rawDeath.get(Q)?.reason,length:d.body.length,head:{...d.body[0]},body:d.body.map(p=>({...p})),lastIndicator:ind.get(Q),blocking:rec.blk,mover:rawDeath.get(Q)?.mover,other:other?{id:other.id,team:other.team,L:d.body.length===0?null:other.body.length,born:other.born,parent:other.parent}:null,queenAction:history.get(Q)||null,killerAction:other?history.get(other.id)||null:killerActionFallback(c),killerTurn:other?turnStates.get(other.id)||null:null};
   if(t.role==='main'){out.death.lastQueenTurn=last;out.death.previousQueenTurn=previous;out.death.atDeath=snapshot(c,r);out.death.queenHistory=qHistory;}
  },
  end(n,c){out.rounds=n;out.queenAliveEnd=c.drag.has(Q);out.queenEndLength=c.drag.get(Q)?.body.length||0;}
 });
 function killerActionFallback(c){return out.death?.mover===Q?null:currentAction;}
 out.checks=res.chk;out.result=res.result;return out;
}
const tasks=inv.tasks.sort((a,b)=>(a.role==='main'?0:1)-(b.role==='main'?0:1)||a.dir.localeCompare(b.dir)||a.key.localeCompare(b.key));
for(const [i,t]of tasks.entries()){
 try{
  const R=load(path.join(ROOT,t.file)),hash=fingerprint(R),mapHash=sha(JSON.stringify(R.match.map)),dedup=t.role+'|'+t.row.side+'|'+t.key+'|'+mapHash+'|'+hash;
  if(seen.has(dedup)){const g=seen.get(dedup);g.aliases.push({dir:t.dir,key:t.key,file:t.file,sourceLine:t.row.sourceLine});continue;}
  const id='g'+String(games.length+1).padStart(4,'0'),g=extract(R,t,id);g.fingerprint=hash;g.mapHash=mapHash;g.replaySha256=sha(fs.readFileSync(path.join(ROOT,t.file)));
  if(t.role==='main'){
   const file='raw/'+id+'.json';fs.writeFileSync(path.join(OUT,file),JSON.stringify({game:g,map:R.match.map})+'\n');g.raw=file;
   if(g.death)for(const k of ['lastQueenTurn','previousQueenTurn','atDeath','queenHistory'])delete g.death[k];
  }
  seen.set(dedup,g);games.push(g);for(const[k,v]of Object.entries(g.checks))if(v)checks[k]=(checks[k]||0)+v;
 }catch(e){errors.push({dir:t.dir,key:t.key,error:String(e.stack)});}
 if((i+1)%50===0){console.log(i+1+'/'+tasks.length+' unique '+games.length+' errors '+errors.length);fs.writeFileSync(path.join(OUT,'extract-progress.json'),JSON.stringify({processed:i+1,total:tasks.length,unique:games.length,errors}));}
}
const out={metadata:{frozenAt:inv.frozenAt,finishedAt:new Date().toISOString(),rules:'123',dedup:'same role + side + scenario key + initial map hash + physical events fingerprint (sonar included; instructions and debug excluded)'},inventory:inv.manifest,rejected:inv.bad,games,checks,errors};
fs.writeFileSync(path.join(OUT,'extracted.json'),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({main:games.filter(g=>g.role==='main').length,side:games.filter(g=>g.role==='side').length,checks,errors:errors.length}));
