'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path');
const {makeLoader,viewerSource}=require('../../tools/top_features');
const {perGame}=require('../../tools/mass_ledger');
const load=makeLoader(viewerSource()),A=require('./analysis.json'),F=require('./firstdiv.json');
const out={decisions:[],situations:[],auditTargets:[],checks:[],rawA:[]};
const chosen=new Set();
const dirs='NESW';
function oracle(d,c,a){
 let b=d.body.map(p=>c.key(p.x,p.y)),pearls=new Set(c.pearls.keys()),free=Math.ceil(b.length/4),states=[];
 if(a?.kind!=='move')return {survived:null,reason:'non-move',body:b};
 for(let i=0;i<a.steps.length;i++){
  if(i>=free&&b.length<=2)return {survived:false,reason:'A',step:i+1,body:b,states};
  const p=c.across(b[0]%c.W,Math.floor(b[0]/c.W),a.steps[i]);
  if(!p)return {survived:false,reason:'W',step:i+1,body:b,states};
  const t=c.key(p.x,p.y),other=c.occ.get(t);
  if(b.includes(t))return {survived:false,reason:'S',step:i+1,body:b,states};
  if(other!==undefined&&other!==d.id)return {survived:false,reason:c.drag.get(other)?.body[0]?.x===p.x&&c.drag.get(other)?.body[0]?.y===p.y?'H':'O',step:i+1,other,body:b,states};
  b.unshift(t);if(!pearls.has(t))b.pop();pearls.delete(t);if(i>=free)b.pop();states.push([...b]);
 }
 return {survived:true,body:b,states};
}
for(const arm of ['on','off'])for(const [key,rec]of Object.entries(A.sets[arm])){
 const file=`exp/bodymem2/${arm}/games/${key.replaceAll(':','_')}/game.replay`,R=load(file),side=key.split(':')[2],fork=F.rows.find(r=>r.key===key),inds=new Map(),targets=new Set();
 for(const field of ['startBodyDrift','endBodyDrift'])for(const v of rec[field])targets.add(v.id);
 if(fork.status==='matched')fork.changed.forEach(v=>targets.add(v.id));
 const ledger=perGame(R,{rules:'123',map:'?'},{
  indicator(e){inds.set(e.id,e.text||'');},
  turn(d,r,c){
   if(d.team!==side)return;
   if(fork.status==='matched'&&r===fork.R){const x=fork.changed.find(x=>x.id===d.id);if(x)out.decisions.push({key,history:arm,R:r,id:d.id,body:d.body.map(p=>c.key(p.x,p.y)),pearls:[...c.pearls.keys()],on:x.on,off:x.off,onOracle:oracle(d,c,x.on.action),offOracle:oracle(d,c,x.off.action),classification:x.classification,fates:x.fates});}
  },
  action(d,e,r,c,before){
   if(d.team!==side||e.action?.kind!=='move'||e.action.steps.length<2||d.fate)return;
   const ind=inds.get(d.id)||'',free=Math.ceil(before.length/4),tag=/bodyx(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)/.exec(ind),group=key.includes('gen_')?'generated':['arena','big_empty','Colosseum','default_small','stronghold'].includes(key.split(':')[1])?'bundled':['around_unsw','australia','stripes'].includes(key.split(':')[1])?'sprint':'online';
   const kinds=[];if(before.length===8&&e.action.steps.length===2&&d.body.length===8)kinds.push('L8-free2');if(before.length===14&&e.action.steps.length===3&&d.body.length===14)kinds.push('L14-free3');if(e.action.steps.length>free)kinds.push('paid');if(tag&&+tag[7]>0)kinds.push('unseen');kinds.push('representative-'+group);
   for(const kind of kinds){const mark=arm+':'+kind+':'+group;if(!chosen.has(mark)){chosen.add(mark);targets.add(d.id);out.situations.push({key,arm,kind,round:r,id:d.id,action:e.action,indicator:ind,start:before.map(p=>c.key(p.x,p.y)),end:d.body.map(p=>c.key(p.x,p.y)),W:c.W,H:c.H});}}
  }
 });
 out.checks.push({key,arm,checks:ledger.chk});
 for(const d of rec.deaths.filter(d=>d.reason==='A'))out.rawA.push({key,arm,...d});
 if(targets.size)out.auditTargets.push({key,arm,file,side,ids:[...targets].sort((a,b)=>a-b)});
}
fs.writeFileSync(path.join(__dirname,'review-analysis.json'),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({decisions:out.decisions.length,situations:out.situations.length,auditTargets:out.auditTargets.length,rawA:out.rawA.length}));
