'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {makeLoader,viewerSource}=require('../../tools/top_features'),{perGame}=require('../../tools/mass_ledger');
const load=makeLoader(viewerSource()),T=__dirname,A=JSON.parse(fs.readFileSync(path.join(T,'analysis.json')));
const out={arms:{},examples:{},identity:{},causal:{judgeVerified:0,forkVerified:0,scope:'native diagnostics only; no judge-clock/Planner snapshot/RNG fork runner provided'},keyErrors:[]};
const hash=b=>{let h=2166136261;for(const t of b)h=Math.imul(h^t,16777619)>>>0;return h;};
for(const arm of ['on','off']){
 const a=out.arms[arm]={games:0,turns:0,actions:0,multi:0,completed:0,predictedAll:0,predictedComplete:0,missingAll:0,missingComplete:0,startDriftAll:0,startDriftComplete:0,unknownAll:0,unknownComplete:0,unseenAll:0,unseenComplete:0,unknownSlots:0,missing:[],initialPartial:0,initialLong:[],bodymemRejected:0,errors:[],sonar:{direct:0,exact:0,under:0,over:0,headMismatch:0,fullySeenMismatch:0,mismatches:[]},splits:0,examples:{}};
 for(const [key,row]of Object.entries(A.sets[arm])) {
  a.games++;const dir=key.replace(/:/g,'_'),file=path.join(T,arm,'games',dir,'game.replay'),R=load(file),M=R.match.map,W=M.width;
  const side=key.split(':')[2],inds=new Map(),starts=new Map(),states=new Map(),first=new Set();
  let round=-1;for(const e of R.events){if(e.type==='roundStart')round=e.round;if(/error|timeout|no.?reply|problem/i.test(e.type))a.errors.push({key,round,event:e});}
  const remember=(kind,rec)=>{if(!a.examples[kind])a.examples[kind]=rec;if(arm==='on'&&!out.examples[kind])out.examples[kind]=rec;};
  const ledger=perGame(R,{map:key.split(':')[1],rules:'123'}, {
   indicator(e){inds.set(e.id,e.text||'');},
   turn(d,r,c){if(d.team!==side)return;a.turns++;const h=d.body[0],partial=d.body.filter(p=>c.cheb(h,p)>3).length;
    if(!first.has(d.id)){first.add(d.id);if(partial){a.initialPartial++;a.initialLong.push({key,id:d.id,round:r,L:d.body.length,hidden:partial});}}
    starts.set(d.id,{pearls:new Set(c.pearls.keys()),head:h,partial});
   },
   action(d,e,r,c,before){if(d.team!==side)return;a.actions++;const ind=inds.get(d.id)||'',st=starts.get(d.id),body=before.map(p=>c.key(p.x,p.y));
    const dirs=e.action?.kind==='move'?e.action.steps:[],steps=dirs.length,free=Math.ceil(before.length/4),tiles=[],eats=[],seen=[],used=new Set();let h=before[0];
    for(const dir of dirs){h=c.across(h.x,h.y,dir);if(!h)break;const t=c.key(h.x,h.y);tiles.push(t);eats.push(+(st.pearls.has(t)&&!used.has(t)));seen.push(c.cheb(st.head,h)<=3);used.add(t);}
    const end=d.fate?null:d.body.map(p=>c.key(p.x,p.y));
    const rec={arm,key,file:path.relative(process.cwd(),file),round:r,id:d.id,L:before.length,dirs:dirs.join(''),free,paid:Math.max(0,steps-free),start:body,end,tiles,eats,seen,indicator:ind};
    states.set(r+':'+d.id,{body:end,fullySeen:seen.every(Boolean),rec});
    const rej=/\bbodymemr(\d+)/.exec(ind);if(rej)a.bodymemRejected+=+rej[1];
    if(steps>1){a.multi++;if(!d.fate)a.completed++;
     const tag=/\bbodyx(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)/.exec(ind);
     if(!tag){a.missingAll++;if(!d.fate)a.missingComplete++;a.missing.push({...rec,fate:d.fate});}
     else {const v=tag.slice(1).map(Number);a.predictedAll++;if(!d.fate)a.predictedComplete++;
      if(v[4]!==hash(body)){a.startDriftAll++;if(!d.fate)a.startDriftComplete++;}
      if(v[3]){a.unknownAll++;if(!d.fate)a.unknownComplete++;}a.unknownSlots+=v[3];
      if(v[6]){a.unseenAll++;if(!d.fate)a.unseenComplete++;}
     }
    }
    if(end){
     if(before.length===8&&steps===2&&!eats.some(Boolean))remember('L8-free2',rec);
     if(before.length===14&&steps===3&&!eats.some(Boolean))remember('L14-free3',rec);
     if(steps>free&&eats.slice(free).some(Boolean))remember('paid-pearl',rec);
     if(seen.some(v=>!v)&&eats.some((v,i)=>v&&!seen[i]))remember('unseen-growth',rec);
     const kinds={bundled:['arena','big_empty','Colosseum','default_small','stronghold'],generated:['gen_'],online:['default','schooltime','trophy','portals','slithery_fight','autarky','prisoners_dilemma'],sprint:['around_unsw','australia','stripes']};
     if(steps>1&&steps<=free){for(const [kind,maps]of Object.entries(kinds))if(maps.some(m=>key.split(':')[1]===m||m==='gen_'&&key.split(':')[1].startsWith(m)))remember(kind+'-free',rec);}
    }
   },
   split(p,ch,e,r,c){if(p.team!==side)return;a.splits++;const body=p.body.map(t=>c.key(t.x,t.y));states.set(r+':'+p.id,{body,fullySeen:true});remember('split',{arm,key,round:r,id:p.id,parent:body,child:ch.body.map(t=>c.key(t.x,t.y))});}
  });
  if(Object.values(ledger.chk).some(v=>v))out.keyErrors.push({arm,key,checks:ledger.chk});
  round=-1;const counted=new Set();
  for(const e of R.events){if(e.type==='roundStart')round=e.round;if(e.type!=='sonarPing')continue;
   const k=round+':'+e.senderId;if(counted.has(k))continue;counted.add(k);
   const v=BigInt(e.value64)^0x9E3779B97F4A7C15n;if(Number(v>>58n)!==0x33)continue;
   const id=Number(v>>47n&2047n),rr=Number(v>>40n&127n),x=Number(v>>34n&63n),y=Number(v>>28n&63n),len=Number(v>>21n&127n),team=Number(v>>8n&1n);
   if(id!==e.senderId||rr!==(round&127)||team!==+(side==='B'))continue;
   const s=states.get(k);if(!s?.body)continue;
   const actual=Math.min(s.body.length,127),delta=len-actual,t=y*W+x;a.sonar.direct++;
   if(delta===0)a.sonar.exact++;if(delta<0)a.sonar.under++;if(delta>0)a.sonar.over++;
   if(t!==s.body[0])a.sonar.headMismatch++;
   if(delta||t!==s.body[0]){if(s.fullySeen)a.sonar.fullySeenMismatch++;a.sonar.mismatches.push({key,id,round,len,actual,head:t,actualHead:s.body[0],fullySeen:s.fullySeen,rec:s.rec});}
  }
 }
}
for(const arm of ['base','off','on']){const buf=fs.readFileSync(path.join(T,'compiled',arm+'.wasm'));out.identity[arm]={bytes:buf.length,sha256:crypto.createHash('sha256').update(buf).digest('hex')};}
out.identity.bytesEqual=fs.readFileSync(path.join(T,'compiled/base.wasm')).equals(fs.readFileSync(path.join(T,'compiled/off.wasm')));
fs.writeFileSync(path.join(T,'review.json'),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(Object.fromEntries(Object.entries(out.arms).map(([k,v])=>[k,{...v,initialLong:v.initialLong.length,sonar:{...v.sonar,mismatches:v.sonar.mismatches.length},examples:Object.keys(v.examples)}])),null,2));
