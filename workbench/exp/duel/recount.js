// Independent episode reconstruction from replay dragonUpdate head/tail, not mass_ledger moves.
'use strict';const AR=require('../general/atlas_recount');
function recount(R,t){const G=AR.graph(R.match.map),{W,H,N,nb}=G,ix=p=>p.y*W+p.x,dsCache=new Map(),body=new Map(),team=new Map(),occ=new Int32Array(N).fill(-1),active=new Map(),cool=new Set(),eps=[],rawReasons=new Map(R.events.filter(e=>e.type==='dragonDeath').map(e=>[e.id,e.reason]));let r=-1,cur=-1,steps=[],updates=0,pending=false,first=true;
 function distances(k){if(dsCache.has(k))return dsCache.get(k);const d=new Uint8Array(N).fill(99),q=[k];d[k]=0;for(let i=0;i<q.length;i++){const u=q[i];if(d[u]>=8)continue;for(let z=0;z<4;z++){const v=nb[u*4+z];if(v>=0&&d[v]===99){d[v]=d[u]+1;q.push(v);}}}dsCache.set(k,d);return d;}
 const dist=(a,b)=>Math.min(distances(a)[b],distances(b)[a]),key=(a,b)=>a<b?a+':'+b:b+':'+a;
 const lift=id=>{for(const k of body.get(id)||[])if(occ[k]===id)occ[k]=-1;},put=id=>{for(const k of body.get(id)||[])occ[k]=id;};for(const d of R.match.map.initialDragons){body.set(d.id,d.body.map(ix));team.set(d.id,d.team);put(d.id);}
 const third=ep=>{const a=body.get(ep.a),b=body.get(ep.b);return !!a&&!!b&&[...body].some(([id,x])=>id!==ep.a&&id!==ep.b&&(dist(a[0],x[0])<=5||dist(b[0],x[0])<=5));};
 function end(ep,outcome,detail){eps.push({id:t.key+':'+key(ep.a,ep.b)+':'+ep.start,outcome,end:r,...detail});active.delete(key(ep.a,ep.b));cool.add(key(ep.a,ep.b));}
 function discover(only){const actor=body.has(only)?team.get(only):null,as=[...body.keys()].filter(id=>team.get(id)==='A'&&(actor!=='A'||id===only)),bs=[...body.keys()].filter(id=>team.get(id)==='B'&&(actor!=='B'||id===only));for(const a of as)for(const b of bs){const k=key(a,b);if(active.has(k)||cool.has(k)||dist(body.get(a)[0],body.get(b)[0])>4)continue;const ep={a,b,start:r,separated:0};active.set(k,ep);if(third(ep))end(ep,'third_party',{});}}
 function checkThird(){for(const ep of [...active.values()])if(third(ep))end(ep,'third_party',{});}
 function flush(){if(!pending)return;pending=false;discover(cur);checkThird();}
 function snapshot(){for(const k of [...cool]){const [a,b]=k.split(':').map(Number);if(!body.has(a)||!body.has(b)||dist(body.get(a)[0],body.get(b)[0])>4)cool.delete(k);}for(const ep of [...active.values()]){if(!body.has(ep.a)||!body.has(ep.b)){end(ep,'other_death',{});continue;}ep.separated=dist(body.get(ep.a)[0],body.get(ep.b)[0])>6?ep.separated+1:0;if(third(ep))end(ep,'third_party',{});else if(ep.separated>=3)end(ep,'disengage',{});}discover();}
 for(const e of R.events){if(e.type==='roundStart'){flush();r=e.round;first=true;}else if(e.type==='turnStart'){flush();cur=e.id;steps=[];updates=0;if(first){first=false;snapshot();}}
  else if(e.type==='dragonAction'){steps=e.action?.kind==='move'?e.action.steps:[];pending=true;}
  else if(e.type==='dragonUpdate'&&r>=0){const b=body.get(e.id);if(!b)throw Error('independent missing update body');lift(e.id);const h=ix(e.head),tail=ix(e.tail);if(b[0]!==h)b.unshift(h);while(b.length>1&&b.at(-1)!==tail)b.pop();put(e.id);updates++;}
  else if(e.type==='dragonSplit'){flush();lift(e.parentId);body.set(e.parentId,e.parentBody.map(ix));put(e.parentId);body.set(e.childId,e.childBody.map(ix));team.set(e.childId,e.team);put(e.childId);checkThird();}
  else if(e.type==='dragonDeath'){flush();const b=body.get(e.id);if(!b)throw Error('independent missing dead body');let other=null;if(e.reason==='H'){if(e.id!==cur)other=cur;else{const z=DIR.indexOf(steps[updates]),v=z<0?-1:nb[b[0]*4+z];other=v>=0&&occ[v]>=0?occ[v]:null;/* passive victim has already gone: recover from its death event */if(other===null)other=lastHeadVictim;}}
   else if(e.reason==='O'){const z=DIR.indexOf(steps[updates]),v=z<0?-1:nb[b[0]*4+z];other=v>=0&&occ[v]>=0?occ[v]:null;}
   for(const ep of [...active.values()])if(ep.a===e.id||ep.b===e.id){const oid=ep.a===e.id?ep.b:ep.a,p=body.get(oid);if(!p)end(ep,'other_death',{});else if(e.reason==='H'&&other===oid)end(ep,'trade',{mover:cur});else if(e.reason==='O'&&other===oid||['W','S'].includes(e.reason)&&dist(b[0],p[0])<=2)end(ep,'kill',{killer:oid,dead:e.id});else end(ep,other!==null&&other!==oid?'third_party':'other_death',{});}
   if(e.reason==='H'&&e.id!==cur)lastHeadVictim=e.id;lift(e.id);body.delete(e.id);
  }
 }
 flush();for(const ep of [...active.values()])end(ep,'censored',{});return eps;
}
const DIR='NESW';let lastHeadVictim=null;
module.exports={recount};
