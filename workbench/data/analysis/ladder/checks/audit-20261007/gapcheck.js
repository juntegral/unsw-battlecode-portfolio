// Do the local gap files describe the server's maps? Test every natural pearl birth against the local [lo,hi].
const fs=require('fs'),path=require('path');const {ctx}=require('./viewer2.js');
const RAW='~/01. Project/개인 프로젝트/unsw-swarm/data/online/ladder';
const GAPS=JSON.parse(fs.readFileSync(path.join(__dirname,'gaps.json')));
const [shard,of]=process.argv.slice(2).map(Number);
const res={};const key=c=>c.x+','+c.y;
for(const b of fs.readdirSync(RAW).filter(x=>/^\d+$/.test(x)).sort()){
  for(const f of fs.readdirSync(path.join(RAW,b)).filter(x=>/^game-\d+\.json$/.test(x)).sort()){
    const j=JSON.parse(fs.readFileSync(path.join(RAW,b,f)));
    if(j.id%of!==shard)continue;
    const R=ctx.parseReplay(fs.readFileSync(path.join(RAW,b,`M${j.id}.replay`)));
    const gaps=(GAPS[j.mapName]||{gaps:{}}).gaps;const local=!!GAPS[j.mapName];
    const m=res[j.mapName]=res[j.mapName]||{games:0,births:0,birthsOnZeroTile:0,tooSoon:0,overdue:0,overdueTiles:{},tested:0,fountainFreeTicks:0,fountainSpawns:0,perTile:{},firstBirth:{}};
    m.games++;
    const bodies=new Map();let i=0;
    for(const l of R.map.split('\n')){const q=l.trim().split(/\s+/);if(q[0]==='DRAGON'){const body=[];for(let k=0;k<+q[2];k++)body.push(q[3+2*k]+','+q[4+2*k]);bodies.set(i++,body);}}
    const pearls=new Set();const streak={},last={};let inTick=false,born=new Set(),occ=null,pearlAtTick=null,round=0,actor=null;
    const endTick=()=>{ if(!inTick)return; inTick=false;
      for(const t in gaps){const [lo,hi]=gaps[t];
        if(born.has(t)){ if(last[t]!==undefined&&round-last[t]<lo)m.tooSoon++; if(last[t]===undefined){(m.firstBirth[lo+'-'+hi]=m.firstBirth[lo+'-'+hi]||[]).push(round);} last[t]=round;streak[t]=0;
          if(hi===1)m.fountainSpawns++; }
        else if(!occ.has(t)&&!pearlAtTick.has(t)){ streak[t]=(streak[t]||0)+1; if(hi===1)m.fountainFreeTicks++;
          if(hi<=60){ if(streak[t]===hi+1){m.overdue++;m.overdueTiles[t]=(m.overdueTiles[t]||0)+1;} } }
        else streak[t]=0;
      }
      for(const t in gaps)if(gaps[t][1]<=60&&(!m.perTile[t]))m.perTile[t]=1;
    };
    for(const e of R.events){
      if(e.type==='roundStart'){endTick();round=e.round;actor=null;inTick=true;born=new Set();occ=new Set();for(const body of bodies.values())for(const c of body)occ.add(c);pearlAtTick=new Set(pearls);}
      else if(e.type==='turnStart'){endTick();actor=e.id;}
      else if(e.type==='tileChange'){const t=key(e.tile);
        if(e.hasPearl){pearls.add(t);if(inTick){born.add(t);m.births++;if(local&&!(t in gaps))m.birthsOnZeroTile++;}}
        else pearls.delete(t);}
      else if(e.type==='dragonUpdate'){const body=bodies.get(e.id),h=key(e.head),t=key(e.tail);if(body[0]!==h)body.unshift(h);while(body.length>1&&body[body.length-1]!==t)body.pop();}
      else if(e.type==='dragonSplit'){bodies.set(e.parentId,e.parentBody.map(key));bodies.set(e.childId,e.childBody.map(key));}
      else if(e.type==='dragonDeath'){bodies.delete(e.id);}
    }
    endTick();
  }
}
for(const k in res){res[k].testedTiles=Object.keys(res[k].perTile).length;delete res[k].perTile;}
fs.writeFileSync(path.join(__dirname,`gapcheck-${shard}.json`),JSON.stringify(res));
