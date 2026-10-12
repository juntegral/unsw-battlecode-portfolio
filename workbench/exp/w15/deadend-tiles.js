// Concentration of our dead-end-terminus wall deaths per tile, and the round of the first vs later deaths there.
'use strict';
const fs=require('fs'),path=require('path');
const ROOT='~/01. Project/개인 프로젝트/unsw-swarm';
const L=require(path.join(ROOT,'tools/mapgen/lib.js'));
const {makeLoader,viewerSource}=require(path.join(ROOT,'tools/top_features.js'));
const load=makeLoader(viewerSource()), G=path.join(ROOT,'exp/mapgen/games');
const only=process.argv.slice(2);
let all=0,repeat=0,games=0;
for(const dir of fs.readdirSync(G).sort()){
  const m1=/^(gen_[A-Z]_\d+)_([AB])_1$/.exec(dir); if(!m1||(only.length&&!only.some(o=>dir.startsWith(o))))continue;
  const [,map,side]=m1, f=path.join(G,dir,'game.replay'); if(!fs.existsSync(f))continue;
  const m=L.parse(fs.readFileSync(path.join(ROOT,'maps/generated',map+'.map'),'utf8')), nb=L.graph(m), core=L.coreOf(nb);
  const R=load(f), team=new Map(), head=new Map(), born=new Map(); let round=0; const tiles=new Map();
  for(const d of R.match.map.initialDragons){team.set(d.id,d.team);head.set(d.id,d.body[0]);born.set(d.id,0);}
  for(const e of R.events){
    if(e.type==='roundStart')round=e.round;
    else if(e.type==='dragonSplit'){team.set(e.childId,e.team);born.set(e.childId,round);}
    else if(e.type==='dragonUpdate'&&e.head)head.set(e.id,e.head);
    else if(e.type==='dragonDeath'&&e.reason==='W'&&team.get(e.id)===side){
      const h=head.get(e.id); if(!h)continue; const k=h.y*m.W+h.x; if(core[k]||nb[k].length!==1)continue;
      const t=tiles.get(k)||{n:0,rounds:[],ages:[]}; t.n++; t.rounds.push(round); t.ages.push(round-(born.get(e.id)||0)); tiles.set(k,t);
    }
  }
  const tot=[...tiles.values()].reduce((s,t)=>s+t.n,0); if(!tot)continue; games++; all+=tot;
  const rep=[...tiles.values()].reduce((s,t)=>s+Math.max(0,t.n-1),0); repeat+=rep;
  const top=[...tiles.entries()].sort((a,b)=>b[1].n-a[1].n).slice(0,3).map(([k,t])=>`(${k%m.W},${Math.floor(k/m.W)})x${t.n} r${t.rounds[0]}-${t.rounds[t.rounds.length-1]} medAge${t.ages.sort((a,b)=>a-b)[t.ages.length>>1]}`);
  console.log(dir,'deadEndWallDeaths',tot,'tiles',tiles.size,'repeats',rep,'top',top.join(' '));
}
console.log('TOTAL games',games,'deaths',all,'repeat deaths at an already-used terminus',repeat);
