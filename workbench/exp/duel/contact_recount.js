// Independent direct-contact identities from recorded head/tail updates, without move simulation.
'use strict';
const AR=require('../general/atlas_recount');
function contacts(R){
 const {W,N,nb}=AR.graph(R.match.map),ix=p=>p.y*W+p.x,body=new Map(),team=new Map(),occ=new Int32Array(N).fill(-1),heads=[],bodies=[];
 let r=-1,cur=-1,steps=[],updates=0;
 const lift=id=>{for(const k of body.get(id)||[])if(occ[k]===id)occ[k]=-1;},put=id=>{for(const k of body.get(id)||[])occ[k]=id;};
 for(const d of R.match.map.initialDragons){body.set(d.id,d.body.map(ix));team.set(d.id,d.team);put(d.id);}
 for(const e of R.events){
  if(e.type==='roundStart')r=e.round;
  else if(e.type==='turnStart'){cur=e.id;steps=[];updates=0;}
  else if(e.type==='dragonAction')steps=e.action?.kind==='move'?e.action.steps:[];
  else if(e.type==='dragonUpdate'&&r>=0){const b=body.get(e.id);if(!b)throw Error('raw contact: missing updated body');lift(e.id);const h=ix(e.head),tail=ix(e.tail);if(b[0]!==h)b.unshift(h);while(b.length>1&&b.at(-1)!==tail)b.pop();put(e.id);updates++;}
  else if(e.type==='dragonSplit'){lift(e.parentId);body.set(e.parentId,e.parentBody.map(ix));put(e.parentId);body.set(e.childId,e.childBody.map(ix));team.set(e.childId,e.team);put(e.childId);}
  else if(e.type==='dragonDeath'){
   const b=body.get(e.id);if(!b)throw Error('raw contact: missing dead body');
   if(e.reason==='H'&&e.id!==cur&&team.get(e.id)!==team.get(cur))heads.push([r,cur,e.id]);
   if(e.reason==='O'){const z='NESW'.indexOf(steps[updates]),v=z<0?-1:nb[b[0]*4+z],other=v<0?-1:occ[v];if(other>=0&&team.get(other)!==team.get(e.id))bodies.push([r,e.id,other]);}
   lift(e.id);body.delete(e.id);
  }
 }
 return {heads,bodies};
}
module.exports={contacts};
