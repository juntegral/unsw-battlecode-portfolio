#!/usr/bin/env node
'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'../..'),spec=JSON.parse(fs.readFileSync(path.join(__dirname,'spec.json')));
const {decode}=require('./decode'),{makeLoader,viewerSource}=require('../../tools/top_features'),ML=require('../../tools/mass_ledger');
const load=makeLoader(viewerSource());
function fingerprint(R){const h=crypto.createHash('sha256');for(const e of R.events){if(['dragonIndicator','dragonLog','debugDraw','engineLog'].includes(e.type))continue;const o={};for(const[k,v]of Object.entries(e))if(k!=='instructions')o[k]=typeof v==='bigint'?String(v):v;h.update(JSON.stringify(o));}return h.digest('hex');}
function audit(R,row,on){
 const initial=R.match.map.initialDragons,us=row.side,Q=Math.min(...initial.filter(d=>d.team===us).map(d=>d.id));
 const a={key:row.key,queen:Q,hash:fingerprint(R),cpu:row.cpu||[],death:null,signals:[],receipts:[],queenTurns:[],errors:[]};
 const pending=new Map(),inputs=new Map(),pings=new Map();let round=-1,id=-1;
 for(const e of R.events){
  if(e.type==='roundStart')round=e.round;
  if(e.type==='turnStart'){id=e.id;inputs.set(`${round}:${id}`,pending.get(id)||[]);pending.delete(id);}
  if(e.type==='sonarPing'){
   const p={r:round,sender:e.senderId,hit:e.hitId,value:String(e.value64)},k=`${round}:${id}`;
   if(!pings.has(k))pings.set(k,[]);pings.get(k).push(p);
   if(e.hitId!==undefined){if(!pending.has(e.hitId))pending.set(e.hitId,[]);pending.get(e.hitId).push(p);}
  }
 }
 let memory=[],snap=null,turn=null;const observer=new Map();
 const result=ML.perGame(R,{map:row.map,rules:'123'}, {
  turn(d,r,c){
   if(d.team!==us)return;
   const enemies=[...c.drag.values()].filter(o=>o.team!==us).map(o=>({id:o.id,L:o.body.length,t:o.body[0].y*c.W+o.body[0].x,visible:c.cheb(d.body[0],o.body[0])<=3}));
   observer.set(d.id,{r,head:d.body[0],enemies});
   if(d.id!==Q)return;
   snap={r,L:d.body.length,head:{...d.body[0]},enemies};
   if(!on)return;
   let received=0,accepted=0;
   for(const p of inputs.get(`${r}:${Q}`)||[]){
    const s=decode(p.value,r,us,c.W,c.H);if(!s)continue;
    const source=c.drag.get(s.sender),target=c.drag.get(s.enemy);
    if(source&&source.team!==us||target&&target.team===us)continue;
    received++;memory=memory.filter(h=>r-h.round<=3);
    const i=memory.findIndex(h=>h.enemy===s.enemy);let adopted=false;
    if(i>=0){if(s.round>memory[i].round){memory[i]=s;adopted=true;}}
    else if(memory.length<16){memory.push(s);adopted=true;}
    else {let oldest=0;for(let j=1;j<memory.length;j++)if(memory[j].round<memory[oldest].round||memory[j].round===memory[oldest].round&&memory[j].enemy<memory[oldest].enemy)oldest=j;
     if(s.round>memory[oldest].round){memory[oldest]=s;adopted=true;}}
    if(adopted)accepted++;
    a.receipts.push({...s,receiveRound:r,sendRound:p.r,delay:r-p.r,adopted});
   }
   memory=memory.filter(h=>r-h.round<=3);
   turn={r,received,accepted,expected:memory.map(h=>({...h})),head:snap.head,L:snap.L};
  },
  indicator(e,r,c){
   const d=c.drag.get(e.id);if(!d||d.team!==us||!on)return;
   const text=e.text||'',tx=/ qst(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)/.exec(text);
   if(tx){
    const expected={enemy:+tx[1],round:+tx[2],t:+tx[3],len:+tx[4]},state=observer.get(e.id),seen=state?.enemies.find(h=>h.id===expected.enemy);
    const rays=(pings.get(`${r}:${e.id}`)||[]),reports=rays.map(p=>({...p,msg:decode(p.value,r,us,c.W,c.H)})).filter(p=>p.msg);
    const signal={r,id:e.id,...expected,ray:+tx[5],queenTile:+tx[6],actualLength:seen?.L,visible:seen?.visible,rays:rays.length,reports};
    a.signals.push(signal);
    if(!seen?.visible||seen.t!==expected.t||expected.round!==r)a.errors.push({r,id:e.id,kind:'report not current visible head',signal});
    // A dead sender emits no rays; preserve it as a failed opportunity.
    if(rays.length&& (reports.length!==1||rays.length!==4||reports.some(p=>Object.keys(expected).some(k=>p.msg[k]!==expected[k])||p.msg.sender!==e.id)))a.errors.push({r,id:e.id,kind:'emitted report fields/ray count',signal});
   }
   if(e.id!==Q)return;
   if(!turn||turn.r!==r){a.errors.push({r,kind:'missing queen turn'});return;}
   const ns=/ qsn(\d+),(\d+)/.exec(text),sp=/ qsp([\d.]+),([\d.]+)/.exec(text);
   const got=[...text.matchAll(/ qsr(\d+),(\d+),(\d+),(\d+),(\d+)/g)].map(m=>({enemy:+m[1],round:+m[2],t:+m[3],len:+m[4],sender:+m[5]}));
   const order=arr=>arr.map(h=>[h.sender,h.enemy,h.round,h.t,h.len]).sort((a,b)=>a[1]-b[1]);
   if(!ns||+ns[1]!==turn.received||+ns[2]!==turn.accepted||JSON.stringify(order(got))!==JSON.stringify(order(turn.expected)))a.errors.push({r,kind:'cache/latency/TTL reconstruction',expected:turn,got,ns});
   a.queenTurns.push({...turn,reports:got,p1:sp?+sp[1]:null,p2:sp?+sp[2]:null,indicator:text});
  },
  death(d,rec,i,other,r){
   if(d.id!==Q)return;
   const rammer=snap&&other?snap.enemies.find(h=>h.id===other.id):null;
   a.death={r,cause:ML.CAUSE[rec.cause],block:rec.blk,L:d.body.length,lastQueenTurn:snap?.r,rammer,other:other?{id:other.id,L:other.body.length}:null,
    outsideHunter:ML.CAUSE[rec.cause]==='rammed'&&!!rammer&&rammer.L>=9&&!rammer.visible};
  }
 });
 a.checks=result.chk;return a;
}
const sets={},missing=[],historyErrors=[];let expectedGames=0;
for(const out of new Set(spec.map(s=>s.out))){
 const name=path.basename(out),lanes=spec.filter(s=>s.out===out),rows=new Map(),file=path.join(ROOT,out,'rows.jsonl');sets[name]={};
 if(fs.existsSync(file))for(const l of fs.readFileSync(file,'utf8').split('\n').filter(Boolean)){const r=JSON.parse(l);if(r.exit===0&&r.G!==undefined&&!r.error&&!r.botProblem)rows.set(r.key,r);else historyErrors.push({out,row:r});}
 for(const lane of lanes){const maps=fs.readdirSync(path.join(ROOT,lane.maps)).filter(f=>f.endsWith('.map')&&(!lane.only||lane.only.includes(f.slice(0,-4))));
  for(const opp of lane.opps)for(const map of maps)for(const side of lane.sides)for(const seed of lane.seeds){
   expectedGames++;const key=[path.basename(opp),map.slice(0,-4),side,seed].join(':'),replay=path.join(ROOT,out,'games',key.replace(/:/g,'_'),'game.replay'),row=rows.get(key);
   if(!row||!fs.existsSync(replay)){missing.push({out,key});continue;}
   sets[name][key]=audit(load(replay),row,name==='on');
  }
 }
}
const identity=[];for(const[key,a]of Object.entries(sets['id-base']||{})){const b=sets['id-off']?.[key];identity.push({key,same:!!b&&a.hash===b.hash});}
const pairs=[];for(const[key,a]of Object.entries(sets.off||{})){const b=sets.on?.[key];if(!b)continue;pairs.push({key,off:a.death,on:b.death,newDeath:!a.death&&!!b.death,earlierDeath:!!b.death&&(!a.death||b.death.r<a.death.r)});}
const summary={expectedGames,loadedGames:Object.values(sets).reduce((n,s)=>n+Object.keys(s).length,0),missing:missing.length,historyErrors:historyErrors.length,identityKeys:identity.length,identitySame:identity.filter(i=>i.same).length,pairs:pairs.length};
for(const name of ['off','on']){const games=Object.values(sets[name]||{});summary[name]={games:games.length,queenDeaths:games.filter(g=>g.death).length,outsideHunter:games.filter(g=>g.death?.outsideHunter).length,causes:{},signals:games.reduce((n,g)=>n+g.signals.length,0),receipts:games.reduce((n,g)=>n+g.receipts.length,0),accepted:games.reduce((n,g)=>n+g.receipts.filter(s=>s.adopted).length,0),maxLatency:Math.max(-1,...games.flatMap(g=>g.receipts.map(s=>s.delay))),errors:games.reduce((n,g)=>n+g.errors.length,0)};
 for(const g of games)if(g.death)summary[name].causes[g.death.cause]=(summary[name].causes[g.death.cause]||0)+1;
}
fs.writeFileSync(path.join(__dirname,'analysis.json'),JSON.stringify({summary,sets,identity,pairs,missing,historyErrors},null,2)+'\n');
console.log(JSON.stringify(summary,null,2));
