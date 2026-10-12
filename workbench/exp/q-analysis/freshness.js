'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path');
const ROOT=path.resolve(__dirname,'../..');
const {makeLoader,viewerSource}=require('../../tools/top_features');
const ML=require('../../tools/mass_ledger');
const load=makeLoader(viewerSource());
const t=JSON.parse(fs.readFileSync(path.join(__dirname,'tables.json'),'utf8'));
function decode(value,r,us,W,H){
  const v=BigInt(value)^0x9E3779B97F4A7C15n,magic=Number(v>>58n),relay=magic===13;
  if(magic!==51&&!relay)return null;
  const get=(shift,mask)=>Number((v>>BigInt(shift))&BigInt(mask));
  const id=get(47,2047),rnd=get(40,127),x=get(34,63),y=get(28,63),L=get(21,127),hx=get(15,63),hy=get(9,63),team=get(8,1),chk=get(0,255);
  const want=(id*131+rnd*7+x*17+y*31+L*3+hx*5+hy*13+team*101+(relay?108:90))&255;
  const age=((r&127)-rnd)&127;
  if(chk!==want||team!==(us==='B'?1:0)||x>=W||y>=H||L<2||age>(relay?60:3))return null;
  return{id,r:r-age,relay,x,y,L};
}
const agg={},errors=[];
for(const v of ['v18','q18','q18b2']){
  const games=['king','hunter','gen'].flatMap(s=>t.games['exp/v16/q1/'+v+'-'+s]);
  for(const g of games){
    const R=load(path.join(ROOT,g.file)),pending=new Map(),inputs=new Map();let round=-1;
    for(const e of R.events){if(e.type==='roundStart')round=e.round;
      if(e.type==='sonarPing'&&e.hitId!==undefined){if(!pending.has(e.hitId))pending.set(e.hitId,[]);pending.get(e.hitId).push(e.value64);}
      if(e.type==='turnStart'){inputs.set(e.id+':'+round,pending.get(e.id)||[]);pending.delete(e.id);}}
    const news=new Map(),states=new Map();
    const res=ML.perGame(R,{map:g.map,variant:'?',rules:'123'},{turn(d,r,c){
      if(d.team!==g.side)return;
      if(!news.has(d.id))news.set(d.id,{lastSeen:-999,headSeen:-999,knownHead:false});
      const n=news.get(d.id),q=c.drag.get(g.Q);let visibleHead=false,visiblePart=false;
      if(q){visibleHead=c.cheb(d.body[0],q.body[0])<=3;visiblePart=q.body.some(b=>c.cheb(d.body[0],b)<=3);
        if(visiblePart)n.lastSeen=r;if(visibleHead){n.headSeen=r;n.knownHead=true;}}
      const messages=[];
      for(const val of inputs.get(d.id+':'+r)||[]){const m=decode(val,r,g.side,c.W,c.H);if(!m||m.id!==g.Q||m.id===d.id)continue;messages.push(m);
        if(m.r>=n.headSeen){n.headSeen=m.r;n.lastSeen=Math.max(n.lastSeen,m.r);n.knownHead=true;}}
      states.set(d.id,{newsAge:r-Math.max(n.headSeen,n.lastSeen),knownHead:n.knownHead,freshQueenNews:n.knownHead&&r-Math.max(n.headSeen,n.lastSeen)<=20,
        visibleHead,visiblePart,messages,queenAlive:!!q});
    },indicator(e,r,c){
      if(r<300||!/^feed #/.test(e.text||''))return;
      const f=g.feedDecisions.find(x=>x.donor===e.id&&x.r===r);if(!f)return;
      const s=states.get(e.id);f.freshness=s?{...s}:null;
      const death=g.feeds.find(x=>x.donor===e.id&&x.r===r);if(death)death.freshness=f.freshness;
    }});
    if(Object.values(res.chk).some(n=>n!==0))errors.push({key:g.key,dir:g.dir,checks:res.chk});
  }
  const F=games.flatMap(g=>g.feeds.map(f=>({key:g.key,...f}))),fresh=F.filter(f=>f.queenAlive&&f.freshness?.freshQueenNews),late=F.filter(f=>f.queenAlive&&f.r>=430);
  agg[v]={N:games.length,feeds:F.length,whileAlive:F.filter(f=>f.queenAlive).length,freshAlive:fresh.length,freshToQueen:fresh.filter(f=>f.toQueen).length,
    freshNonQueen:fresh.filter(f=>!f.toQueen),lateWhileAlive:late.length,lateNonQueen:late.filter(f=>!f.toQueen),
    lateFreshNonQueen:late.filter(f=>f.freshness?.freshQueenNews&&!f.toQueen),
    postDeathFresh:F.filter(f=>!f.queenAlive&&f.freshness?.freshQueenNews),
    afterDeathQTags:F.filter(f=>!f.queenAlive&&f.qTag),missingFreshness:F.filter(f=>!f.freshness).length,
    earlyFreshToQueen:F.filter(f=>f.r<430&&f.queenAlive&&f.freshness?.freshQueenNews&&f.toQueen).length};
  console.log(v,'freshness done',JSON.stringify({freshAlive:agg[v].freshAlive,freshToQueen:agg[v].freshToQueen,lateNonQueen:agg[v].lateNonQueen.length,lateFreshNonQueen:agg[v].lateFreshNonQueen.length}));
}
t.freshness={method:'Track queen part/head visibility in toroidal 7x7 at each donor turn; consume sonarPing hitId messages at recipient next turn; decode MSG2 checksum, team, age; known head and max(lastSeen,headSeen) age<=20. Child memory starts empty.',aggregates:agg,reconstructionErrors:errors};
fs.writeFileSync(path.join(__dirname,'tables.json'),JSON.stringify(t,null,2)+'\n');
