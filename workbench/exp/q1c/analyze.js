#!/usr/bin/env node
'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'../..'),spec=JSON.parse(fs.readFileSync(path.join(__dirname,'spec.json')));
const {makeLoader,viewerSource}=require('../../tools/top_features'),ML=require('../../tools/mass_ledger');
const load=makeLoader(viewerSource());
function decode(value,r,team,W,H){
 const v=BigInt(value)^0x9E3779B97F4A7C15n,get=(s,m)=>Number((v>>BigInt(s))&BigInt(m)),magic=get(58,63),relay=magic===13;
 if(magic!==51&&!relay)return null;
 const id=get(47,2047),rnd=get(40,127),x=get(34,63),y=get(28,63),len=get(21,127),hx=get(15,63),hy=get(9,63),tm=get(8,1),chk=get(0,255);
 const want=(id*131+rnd*7+x*17+y*31+len*3+hx*5+hy*13+tm*101+(relay?108:90))&255;
 const newer=!relay&&(chk&127)===((want^64)&127),age=((r&127)-rnd)&127;
 if((chk!==want&&!newer)||tm!==(team==='B'?1:0)||x>=W||y>=H||len<2||age>=64||age>(relay?60:3))return null;
 return{id,round:r-age,relay,bit:newer&&!!(chk&128),newer,x,y,len,hx,hy};
}
function fingerprint(R){const h=crypto.createHash('sha256');for(const e of R.events){if(['dragonIndicator','dragonLog','debugDraw','engineLog'].includes(e.type))continue;const o={};for(const[k,v]of Object.entries(e))if(k!=='instructions')o[k]=typeof v==='bigint'?String(v):v;h.update(JSON.stringify(o));}return h.digest('hex');}
function audit(R,row,sight){
 const us=row.side,initial=R.match.map.initialDragons,Q=Math.min(...initial.filter(d=>d.team===us).map(d=>d.id)),EQ=Math.min(...initial.filter(d=>d.team!==us).map(d=>d.id));
 const a={key:row.key,queen:Q,enemyQueen:EQ,hash:fingerprint(R),cpu:row.cpu||[],qDeath:null,backup:{},crowd:[],traps:[],feeds:[],sightTurns:[],signalTurns:[],propagation:[],errors:[],gather:[]};
 const pending=new Map(),inputs=new Map(),pings=new Map();let r=-1,turnId=-1;
 for(const e of R.events){if(e.type==='roundStart')r=e.round;
  if(e.type==='turnStart'){turnId=e.id;inputs.set(`${r}:${e.id}`,pending.get(e.id)||[]);pending.delete(e.id);}
  if(e.type==='sonarPing'){const ping={sender:e.senderId,hit:e.hitId,r,value:String(e.value64)};const k=`${r}:${turnId}`;if(!pings.has(k))pings.set(k,[]);pings.get(k).push(ping);
   if(e.hitId!==undefined){if(!pending.has(e.hitId))pending.set(e.hitId,[]);pending.get(e.hitId).push(ping);}}
 }
 const memories=new Map(),states=new Map(),lastInd=new Map();
 const result=ML.perGame(R,{map:'?',rules:'123'}, {
  turn(d,r,c){if(d.team!==us)return;
   const q=c.drag.get(Q),eq=c.drag.get(EQ);
   if([350,400,430].includes(r)&&a.backup[r]===undefined)a.backup[r]=Math.max(0,...[...c.drag.values()].filter(o=>o.team===us&&o.id!==Q).map(o=>o.body.length));
   if(d.id===Q&&r>=340&&r<=480&&r%10===0)a.crowd.push({r,n:[...c.drag.values()].filter(o=>o.team===us&&o.id!==Q&&c.tdist(o.body[0],d.body[0])<=2).length});
   if(!sight)return;
   const m=memories.get(d.id)||{seen:-1000,heard:-1000};
   const visible=!!eq&&eq.body.some(t=>c.cheb(d.body[0],t)<=3);if(visible)m.seen=r;
   const adopted=[];
   for(const ping of inputs.get(`${r}:${d.id}`)||[]){const msg=decode(ping.value,r,us,c.W,c.H);
    if(!msg||msg.relay||msg.id===(d.id&2047)||!msg.bit||msg.round<=Math.max(m.seen,m.heard))continue;
    m.heard=msg.round;adopted.push({...ping,infoRound:msg.round,delay:r-ping.r});
   }
   memories.set(d.id,m);states.set(d.id,{r,id:d.id,seen:m.seen,heard:m.heard,belief:r-Math.max(m.seen,m.heard)<=50,direct:r-m.seen<=50,truth:!!eq,visible,adopted});
  },
  indicator(e,r,c){const d=c.drag.get(e.id);if(!d||d.team!==us)return;const text=e.text||'';lastInd.set(e.id,{r,text});
   const bk=/ qbk(-?\d+),(-?\d+)/.exec(text);if(bk)a.gather.push({r,id:e.id,target:+bk[1],keepTile:+bk[2]});
   if(sight){const s=states.get(e.id),tag=/ qc([01]),(-?\d+),(-?\d+),([01])/.exec(text);
    if(!s||!tag){a.errors.push({r,id:e.id,error:'missing qc'});return;}
    const observed={belief:!!+tag[1],seen:+tag[2],heard:+tag[3],direct:!!+tag[4]};
    if(Object.keys(observed).some(k=>observed[k]!==s[k]))a.errors.push({r,id:e.id,error:'belief reconstruction',expected:s,observed});
    a.sightTurns.push({...s,...observed});
    for(const hit of s.adopted)a.propagation.push({receiver:e.id,r,...hit,set:observed.belief&&observed.heard===s.heard});
    const sent=pings.get(`${r}:${e.id}`)||[];
    for(const ping of sent){const msg=decode(ping.value,r,us,c.W,c.H);if(!msg)continue;
      const t={r,id:e.id,truth:s.truth,bit:msg.bit,relay:msg.relay,direct:s.direct,hit:ping.hit};a.signalTurns.push(t);
      if(msg.bit!==(!msg.relay&&s.direct))a.errors.push({...t,error:'sender bit'});
    }
   }
   const f=/^feed #(\d+) d(\d+) L(\d+)(.*)/.exec(text);if(f){const s=states.get(e.id);a.feeds.push({r,id:e.id,target:+f[1],toQueen:+f[1]===Q,d:+f[2],L:+f[3],slack:500-r-(+f[2]+ +f[3]),kind:/cv2/.test(f[4])?'cv2':/sf#/.test(f[4])?'sf':/conv/.test(f[4])?'conv':'FE',belief:s?.belief,enemyAlive:c.drag.has(EQ),queenAlive:c.drag.has(Q)});}
  },
  death(d,rec,i,o,r){if(d.id!==Q)return;a.qDeath={r,cause:ML.CAUSE[rec.cause],block:rec.blk};if(r>=300&&ML.CAUSE[rec.cause]==='trap'&&rec.blk==='a')a.traps.push({r,...a.qDeath,indicator:lastInd.get(d.id)});}
 });
 a.checks=result.chk;
 const T=a.sightTurns,S=a.signalTurns;const n=(arr,f)=>arr.filter(f).length;
 a.beliefMetrics={turns:T.length,correct:n(T,t=>t.belief===t.truth),truePositive:n(T,t=>t.belief&&t.truth),falsePositive:n(T,t=>t.belief&&!t.truth),falseNegative:n(T,t=>!t.belief&&t.truth),trueNegative:n(T,t=>!t.belief&&!t.truth)};
 a.signalMetrics={rays:S.length,correct:n(S,t=>t.bit===t.truth),truePositive:n(S,t=>t.bit&&t.truth),falsePositive:n(S,t=>t.bit&&!t.truth),falseNegative:n(S,t=>!t.bit&&t.truth)};
 a.mergeViolations=a.feeds.filter(f=>sight&&f.toQueen&&!f.belief);
 return a;
}
const sets={},missing=[],historyErrors=[];
for(const out of new Set(spec.map(s=>s.out))){const name=path.basename(out),lanes=spec.filter(s=>s.out===out),rowfile=path.join(ROOT,out,'rows.jsonl'),rows=new Map();sets[name]={};
 if(fs.existsSync(rowfile))for(const l of fs.readFileSync(rowfile,'utf8').split('\n').filter(Boolean)){const r=JSON.parse(l);if(r.G!==undefined&&r.exit===0&&!r.error&&!r.botProblem)rows.set(r.key,r);else historyErrors.push({out,row:r});}
 for(const s of lanes)for(const opp of s.opps)for(const map of s.only)for(const side of s.sides)for(const seed of s.seeds){const key=[path.basename(opp),map,side,seed].join(':'),file=path.join(ROOT,out,'games',key.replace(/:/g,'_'),'game.replay'),row=rows.get(key);
  if(!row||!fs.existsSync(file)){missing.push({out,key});continue;}sets[name][key]=audit(load(file),row,['c','on','self'].includes(name));}
}
const pairs=[];for(const[l,r]of[['off','b'],['off','c'],['b','on']])for(const[key,a]of Object.entries(sets[l]||{})){const b=sets[r]?.[key];if(!b)continue;pairs.push({key,comparison:`${l}/${r}`,bothQueenAlive430:[a,b].every(g=>!g.qDeath||g.qDeath.r>=430),backupDelta:Object.fromEntries([350,400,430].map(r=>[r,a.backup[r]===undefined||b.backup[r]===undefined?null:b.backup[r]-a.backup[r]])),trapDelta:b.traps.length-a.traps.length,crowd:[a.crowd,b.crowd],sameEvents:a.hash===b.hash});}
const identity=Object.entries(sets['id-off']||{}).map(([key,a])=>({key,same:sets['id-base']?.[key]?.hash===a.hash}));
const output={sets,pairs,identity,missing,historyErrors};fs.writeFileSync(path.join(__dirname,'analysis.json'),JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify({games:Object.fromEntries(Object.entries(sets).map(([k,v])=>[k,Object.keys(v).length])),missing:missing.length,identity},null,2));
if(missing.length)process.exitCode=1;
