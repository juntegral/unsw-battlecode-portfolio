// Our vs proxy deaths on the generated-map smoke games: reason, and whether the head died off the 2-core (dead-end branch).
'use strict';
const fs=require('fs'),path=require('path');
const ROOT='~/01. Project/개인 프로젝트/unsw-swarm';
const L=require(path.join(ROOT,'tools/mapgen/lib.js'));
const {makeLoader,viewerSource}=require(path.join(ROOT,'tools/top_features.js'));
const load=makeLoader(viewerSource());
const G=path.join(ROOT,'exp/mapgen/games');
const tot={us:{},opp:{}},perMap={},ex={};
for(const dir of fs.readdirSync(G).sort()){
  const m1=/^(gen_[A-Z]_\d+)_([AB])_1$/.exec(dir); if(!m1)continue;
  const [,map,side]=m1, f=path.join(G,dir,'game.replay'); if(!fs.existsSync(f))continue;
  const m=L.parse(fs.readFileSync(path.join(ROOT,'maps/generated',map+'.map'),'utf8')), nb=L.graph(m), core=L.coreOf(nb);
  const R=load(f), team=new Map(), head=new Map(), ind=new Map();
  for(const d of R.match.map.initialDragons){team.set(d.id,d.team);head.set(d.id,d.body[0]);}
  const pm=perMap[map]||(perMap[map]={us:0,usOff:0,opp:0,oppOff:0,offFrac:core.filter(c=>!c).length/core.length});
  let round=0;
  for(const e of R.events){
    if(e.type==='roundStart')round=e.round;
    if(e.type==='dragonSplit'){team.set(e.childId,e.team);}
    else if(e.type==='dragonUpdate'&&e.head){head.set(e.id,e.head);}
    else if(e.type==='dragonIndicator'){ind.set(e.id||e.dragonId,e.text||'');}
    else if(e.type==='dragonDeath'){
      const who=team.get(e.id)===side?'us':'opp', h=head.get(e.id); const k=h?h.y*m.W+h.x:-1; const off=k>=0&&!core[k];
      const deg=k>=0?nb[k].length:-1, tag=ind.get(e.id)||''; const feed=/feed|sf|cv2|fd|sac|gift/i.test(tag);
      const key=e.reason+(off?'/off':'/core')+(deg===1?'/end':'')+(feed?'/feed':''); tot[who][key]=(tot[who][key]||0)+1;
      if(who==='us'&&e.reason==='W'&&!ex[key]){ex[key]=dir+' r'+round+' id'+e.id+' tag:'+tag.slice(0,60);} 
      if(who==='us'){pm.us++;if(off&&(e.reason==='W'||e.reason==='S'))pm.usOff++;}else{pm.opp++;if(off&&(e.reason==='W'||e.reason==='S'))pm.oppOff++;}
    }
  }
}
for(const w of ['us','opp']){console.log(w);for(const [k,v] of Object.entries(tot[w]).sort((a,b)=>b[1]-a[1]))console.log('  ',k,v);}
console.log(JSON.stringify(ex,null,1));
for(const [k,v] of Object.entries(perMap)) if(v.usOff||v.oppOff) console.log(k,'offCoreTiles='+(v.offFrac*100).toFixed(0)+'%','us W/S off-core '+v.usOff+'/'+v.us,'opp '+v.oppOff+'/'+v.opp);
