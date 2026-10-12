'use strict';
const fs=require('fs'),path=require('path');
const {makeLoader,viewerSource}=require('../../tools/top_features');
const load=makeLoader(viewerSource()),ROOT=path.resolve(__dirname,'../..');
const t=JSON.parse(fs.readFileSync(path.join(__dirname,'tables.json'),'utf8'));
const skip=new Set(['dragonIndicator','dragonLog','debugDraw','engineLog']);
function flat(file){const R=load(path.join(ROOT,file)),out=[];let r=-1,cur=-1,ind=new Map();for(const e of R.events){if(e.type==='roundStart')r=e.round;if(e.type==='turnStart')cur=e.id;if(e.type==='dragonIndicator')ind.set(e.id,{r,text:e.text});if(skip.has(e.type))continue;const o=Object.fromEntries(Object.entries(e).filter(([k])=>k!=='instructions'));const id=e.id??e.senderId??cur;out.push({r,e:o,id,indicator:ind.get(id)});}return out;}
const key='proxy4_king:big_empty:A:1',base=t.games['exp/v16/q1/v18-king'].find(g=>g.key===key),a=flat(base.file),diagnoses=[];
for(const v of ['q18','q18b2']){const g=t.games['exp/v16/q1/'+v+'-king'].find(g=>g.key===key),b=flat(g.file);let i=0;const stringify=x=>JSON.stringify(x,(_,v)=>typeof v==='bigint'?v.toString():v);
  while(i<a.length&&i<b.length&&stringify(a[i].e)===stringify(b[i].e))i++;
  const pack=x=>x?{r:x.r,event:x.e,id:x.id,indicator:x.indicator}:null;
  diagnoses.push({variant:v,key,queenDeath:base.qDeath,firstDifferenceBase:pack(a[i]),firstDifferenceVariant:pack(b[i]),previousBase:pack(a[i-1]),previousVariant:pack(b[i-1])});
}
fs.writeFileSync(path.join(__dirname,'identity-diagnosis.json'),JSON.stringify(diagnoses,(_,v)=>typeof v==='bigint'?v.toString():v,2)+'\n');
console.log(JSON.stringify(diagnoses,(_,v)=>typeof v==='bigint'?v.toString():v));
