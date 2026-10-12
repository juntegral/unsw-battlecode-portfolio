'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),{makeLoader,viewerSource}=require('../../tools/top_features.js'),{perGame}=require('../../tools/mass_ledger.js');
const load=makeLoader(viewerSource()),a=require('./analysis.json');
const regress=new Set(a.pairs.filter(x=>x.selfDelta>0||x.wallDelta>0||x.queenDeathDelta>0||x.queenEarlier).map(x=>x.key));
const out={drifts:[],deaths:[],predictorN:0,scalarMismatch:{free:0,paid:0,length:0,hash:0},deathClasses:{},completeVisibleDrifts:0};
function picture(c,body,center){const grid=new Map();for(const q of c.drag.values())for(let i=0;i<q.body.length;i++)grid.set(c.key(q.body[i].x,q.body[i].y),q.id+':'+i);for(let i=0;i<body.length;i++)grid.set(c.key(body[i].x,body[i].y),'self:'+i);const rows=[];for(let dy=-3;dy<=3;dy++){let r=[];for(let dx=-3;dx<=3;dx++){const x=(center.x+dx+c.W)%c.W,y=(center.y+dy+c.H)%c.H,k=c.key(x,y);r.push(grid.get(k)|| (c.pearls.has(k)?'*':'.'));}rows.push(r);}return rows;}
for(const [set,rows]of Object.entries(a.sets))for(const [key,row]of Object.entries(rows)){
 const driftMap=new Map([...row.knownBodyDrift,...row.uncertainBodyDrift].map(x=>[`${x.round}:${x.id}`,x]));
 const selectedDeaths=new Set((regress.has(key)&&['on','off'].includes(set)?row.deaths.filter(d=>['S','W'].includes(d.reason)||d.id===row.queen):[]).map(x=>`${x.round}:${x.id}`));
 if(set!=='on'&&!selectedDeaths.size&&set!=='off'&&!set.startsWith('id-'))continue;
 const R=load(`exp/freecost/${set}/games/${key.replace(/:/g,'_')}/game.replay`),starts=new Map(),pending=new Map(),births=new Map(),afterDeath=[];
 const rawDeath=new Map(R.events.filter(e=>e.type==='dragonDeath').map(e=>[e.id,e.reason]));
 perGame(R,{map:'?',variant:'a',rules:'123'},{
  turn(d,r,c){for(const p of afterDeath.splice(0))p.nextTurnPicture={round:r,id:d.id,grid:picture(c,[],p.before[0])};if(d.team!==key.split(':')[2])return;const t=`${r}:${d.id}`;if(driftMap.has(t)||selectedDeaths.has(t))starts.set(d.id,{body:d.body.slice(),pearls:new Set(c.pearls.keys()),picture:picture(c,d.body,d.body[0])});},
  split(p,ch,e,r){births.set(ch.id,{round:r,parent:p.id,body:ch.body.slice()});},
  action(d,e,r,c,before){if(d.team!==key.split(':')[2]||e.action?.kind!=='move')return;if(!d.fate)out.predictorN++;
   const t=`${r}:${d.id}`,drift=driftMap.get(t),st=starts.get(d.id);if(!drift&&!selectedDeaths.has(t))return;
   const path=[];let head=before[0];for(const dir of e.action.steps){const next=c.across(head.x,head.y,dir);path.push({dir,from:head,to:next,pearl:next?st.pearls.has(c.key(next.x,next.y)):false});if(!next)break;head=next;}
   const rec={set,key,id:d.id,round:r,action:e.action,indicator:drift?.indicator||row.deaths.find(x=>x.id===d.id)?.indicator,before,after:d.body.slice(),path,fate:d.fate,birth:births.get(d.id),beforePicture:st.picture,afterPicture:picture(c,d.body,before[0])};
   if(drift){rec.drift=drift;rec.allStartBodyVisible=before.every(x=>c.cheb(x,before[0])<=3);if(rec.allStartBodyVisible)out.completeVisibleDrifts++;for(const [i,k]of ['free','paid','length','unused','hash'].entries())if(i!==3&&drift.reported[i]!==drift.actual[i])out.scalarMismatch[k]++;out.drifts.push(rec);}
   if(selectedDeaths.has(t))pending.set(d.id,rec);
  },
  death(d,rec,idx,other,r,c){if(!selectedDeaths.has(`${r}:${d.id}`))return;const reason=rawDeath.get(d.id),p=pending.get(d.id)||{set,key,id:d.id,round:r,before:d.body.slice(),beforePicture:picture(c,d.body,d.body[0])};p.reason=reason;p.ledger=rec;p.killer=other?{id:other.id,team:other.team,body:other.body.slice()}:null;afterDeath.push(p);const ind=p.indicator||row.deaths.find(x=>x.id===d.id)?.indicator||'';p.classification=/\bfeed\b|\bsf#/.test(ind)?'intentional-feed':/no-exit/.test(ind)?'no-exit':d.fate?.reason==='S'?'self-path':d.fate?.reason==='W'?'wall-path':reason==='H'?'head-contact':'other';const cls=`${set}:${p.classification}`;out.deathClasses[cls]=(out.deathClasses[cls]||0)+1;out.deaths.push(p);},
 });
}
fs.writeFileSync('exp/freecost/audit.json',JSON.stringify(out)+'\n');
console.log(JSON.stringify({drifts:out.drifts.length,deaths:out.deaths.length,predictorN:out.predictorN,scalarMismatch:out.scalarMismatch,completeVisibleDrifts:out.completeVisibleDrifts,deathClasses:out.deathClasses}));
