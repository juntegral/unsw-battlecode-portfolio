'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path');
const {makeLoader,viewerSource}=require('../../tools/top_features');
const {perGame}=require('../../tools/mass_ledger');
const load=makeLoader(viewerSource()),A=JSON.parse(fs.readFileSync(__dirname+'/analysis.json'));
const sum=(xs,k)=>xs.reduce((s,x)=>s+(Array.isArray(x[k])?x[k].length:x[k]||0),0);
const result={sets:{},regressions:[],keywise:[],reviews:[],selections:[],firstChanges:[],invalid:[]};
for(const [set,obj] of Object.entries(A.sets)) {
 const xs=Object.values(obj), totals={games:xs.length};
 for(const k of ['multi','completed','self','selfMulti','queenSelfMulti','rejected','oracleDrift','stepDrift','memoryDrift','missingTags','unknownInput','unseenPearls','predicted','oversprint'])totals[k]=sum(xs,k);
 totals.reasons={};totals.causes={};totals.checks={};
 for(const x of xs)for(const k of ['reasons','causes','checks'])for(const [c,v]of Object.entries(x[k]))totals[k][c]=(totals[k][c]||0)+v;
 totals.cpuMissing=xs.filter(x=>x.cpuMaxM===null).length;totals.cpuMaxM=Math.max(...xs.map(x=>x.cpuMaxM||0));
 totals.cpuAlarm=xs.filter(x=>x.cpuMaxM>=80).length;totals.cpuLimit=xs.filter(x=>x.cpuMaxM>=100).length;
 totals.queenDeaths=xs.filter(x=>x.death).length; result.sets[set]=totals;
}
result.depth={};for(const k of ['depthPairs','depthLower','depthSame','depthHigher'])result.depth[k]=sum(A.pairs,k);
fs.mkdirSync(__dirname+'/boards',{recursive:true});
function picture(c,us,center,label) {
 const W=c.W,H=c.H,grid=new Map(),legend=[];let i=0;
 for(const d of c.drag.values()) {const ch=d.team===us?String.fromCharCode(97+(i++%26)):'x';if(d.team===us)legend.push(ch+'=#'+d.id+' L'+d.body.length);d.body.forEach((t,j)=>grid.set(c.key(t.x,t.y),j?ch:ch.toUpperCase()));}
 for(const k of c.pearls.keys())if(!grid.has(k))grid.set(k,'*');
 const rows=[label+' around '+center.x+','+center.y+' x='+((center.x-4+W)%W)];
 for(let dy=-4;dy<=4;dy++){const y=(center.y+dy+H)%H;let s=String(y).padStart(3)+' ';for(let dx=-4;dx<=4;dx++)s+=grid.get(c.key((center.x+dx+W)%W,y))||'.';rows.push(s);}
 rows.push(legend.join(' '));return rows.join('\n');
}
const allActions=new Map();
for(const pair of A.pairs) {
 const key=pair.key,on=A.sets.on[key],off=A.sets.off[key],side=key.split(':').at(-2);
 const reasons=Object.entries(pair.reasons).filter(([k,v])=>k!=='S'&&v>0),causes=Object.entries(pair.causes).filter(([,v])=>v>0);
 const reg={key,reasons,causes,queenEarlier:pair.queenEarlier,queenDeathDelta:pair.queenDeathDelta};
 if(reasons.length||causes.length||pair.queenEarlier)result.regressions.push(reg);
 result.keywise.push({key,on:{multi:on.multi,completed:on.completed,self:on.self,selfMulti:on.selfMulti,queenSelfMulti:on.queenSelfMulti},off:{multi:off.multi,completed:off.completed,self:off.self,selfMulti:off.selfMulti,queenSelfMulti:off.queenSelfMulti},reasons:pair.reasons,causes:pair.causes});
 for(const set of ['on','off']) {
  const audit=A.sets[set][key],targets=new Map(),chosen=[];
  function target(id,round,why){const k=round+':'+id;if(!targets.has(k))targets.set(k,[]);targets.get(k).push(why);}
  for(const d of audit.deaths)if(d.reason==='S'||reasons.some(([r])=>d.reason===r)||causes.some(([r])=>d.cause===r)||(pair.queenEarlier&&d.id===audit.queen))target(d.id,d.round,'death:'+d.reason+'/'+d.cause);
  for(const d of audit.memoryDrift)target(d.id,d.round,'memoryDrift');
  for(const d of audit.missingTags)target(d.id,d.round,'missingTag');
  const R=load(path.resolve(__dirname,set,'games',key.replace(/:/g,'_'),'game.replay')),actions=new Map(),turns=new Map(),inds=new Map(),pictures=[];
  const categories=new Set();
  perGame(R,{map:'?',variant:'a',rules:'123'},{
   indicator(e){inds.set(e.id,e.text||'');},
   turn(d,r,c){if(d.team!==side)return;const k=r+':'+d.id;turns.set(d.id,{round:r,start:d.body.map(t=>c.key(t.x,t.y)),pearls:[...c.pearls.keys()],near:['N','E','S','W'].map(dir=>{const t=c.across(d.body[0].x,d.body[0].y,dir);return{dir,t,occupant:t?c.occ.get(c.key(t.x,t.y)):null};}),board:targets.has(k)?picture(c,side,d.body[0],set+' '+key+' r'+r+' turn #'+d.id):null});},
   action(d,e,r,c,before){if(d.team!==side)return;const k=r+':'+d.id,ind=inds.get(d.id)||'',steps=e.action?.kind==='move'?e.action.steps.length:0;
    const rec={id:d.id,round:r,action:e.action,indicator:ind,start:before.map(t=>c.key(t.x,t.y)),end:d.body.map(t=>c.key(t.x,t.y)),fate:d.fate,turn:turns.get(d.id)};actions.set(k,rec);
    if(e.tle||(!e.action))result.invalid.push({set,key,id:d.id,round:r,tle:e.tle,action:e.action});
    if(set==='on'&&steps>1&&!d.fate){const cats=[];if(before.length===8&&steps===3)cats.push('L8-paid-third');if(before.length===14&&steps===3)cats.push('L14-free-three');if(d.ateThisAct&&(/esc|[NESW]{2,}/.test(ind)))cats.push('pearl-multi');
     for(const cat of cats)if(!categories.has(cat)){categories.add(cat);chosen.push({...rec,category:cat});pictures.push(picture(c,side,d.body[0],set+' '+key+' r'+r+' after #'+d.id+' '+cat));}}
    if(targets.has(k)){pictures.push(rec.turn.board,picture(c,side,d.body[0],set+' '+key+' r'+r+' after action #'+d.id));result.reviews.push({set,key,why:targets.get(k),...rec});}
   },
   death(d,rec,idx,other,r,c){const k=r+':'+d.id;if(d.team!==side||!targets.has(k))return;const action=actions.get(k);pictures.push(picture(c,side,d.body[0],set+' '+key+' r'+r+' death #'+d.id));if(!action)result.reviews.push({set,key,why:targets.get(k),id:d.id,round:r,passive:true,other:other?{id:other.id,team:other.team,body:other.body}:null,body:d.body,turn:turns.get(d.id)});}
  });
  result.selections.push(...chosen.map(x=>({key,set,...x})));
  fs.writeFileSync(__dirname+'/boards/'+set+'-'+key.replace(/:/g,'_')+'.txt',pictures.filter(Boolean).join('\n\n')+'\n');
  allActions.set(set+':'+key,actions);
 }
 const oa=allActions.get('off:'+key),na=allActions.get('on:'+key);
 for(const [k,n]of na){const o=oa.get(k);if(o&&JSON.stringify(o.action)!==JSON.stringify(n.action)){result.firstChanges.push({key,off:o,on:n,sameStart:JSON.stringify(o.start)===JSON.stringify(n.start),samePearls:JSON.stringify(o.turn.pearls)===JSON.stringify(n.turn.pearls)});break;}}
 allActions.delete('off:'+key);allActions.delete('on:'+key);
}
fs.writeFileSync(__dirname+'/review.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({sets:result.sets,depth:result.depth,regressionKeys:result.regressions.length,reviews:result.reviews.length,selections:result.selections.length,firstChanges:result.firstChanges.length,invalid:result.invalid.length},null,2));
