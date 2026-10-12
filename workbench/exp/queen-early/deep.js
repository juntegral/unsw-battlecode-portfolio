#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process');const ROOT=path.resolve(__dirname,'../..');
const raw=require(path.join(ROOT,'legacy/exp/intake-gap/rawload')),ML=require(path.join(ROOT,'tools/mass_ledger'));
const T=JSON.parse(fs.readFileSync(path.join(__dirname,'tables.json'))),L=JSON.parse(fs.readFileSync(path.join(__dirname,'local.json')));
const specs=[
 {game:815244,side:'A',rounds:[300,450,499],focus:'surviving Stockfish queen'},
 {game:815352,rounds:[400,450,499],focus:'surviving Yueci queen'},
 {game:814547,rounds:[300,400,499],focus:'fandagong short loop'},
 {game:814627,rounds:[400,450,499],focus:'Tony S unescorted survivor'},
 {game:814623,rounds:[400,450,499],focus:'Tony S surviving Trauma queen'},
 {game:814625,rounds:[400,450,499],focus:'Tony S short Devil survivor'},
 {game:815034,rounds:[307,308,309,499],focus:'newborn paid three-step hit on L21 queen'},
 {game:814624,rounds:[337,338,339,340],focus:'paid two-step hit on Tony S L8 queen'},
 {game:814724,rounds:[113,116,117,118,222,223],focus:'period-four attacker loop; queen arrival; later trap'},
 {game:813921,rounds:[82,83,84],focus:'short equal-length sprint collision'},
 {game:815235,rounds:[35,36,37],focus:'queen-on-queen head collision'},
 {game:815035,rounds:[127,128,129],focus:'one-step hit on :3 L8 queen'},
];
const tie=T.games.filter(g=>g.rounds===500&&g.fate==='both_dead');const max=[...tie].sort((a,b)=>b.result['team'+b.winner].longestDragon-a.result['team'+a.winner].longestDragon)[0];
const med=[...tie].sort((a,b)=>Math.abs(a.result['team'+a.winner].longestDragon-46)-Math.abs(b.result['team'+b.winner].longestDragon-46))[0];
specs.push({game:max.gameId,rounds:[300,400,499],focus:'maximum tie-break longest dragon'},{game:med.gameId,rounds:[300,400,499],focus:'median tie-break longest dragon'});
const feed=L.games.find(g=>g.cohort==='exp/v16/q1/q1-sprint2'&&g.map==='australia'&&g.side==='B');if(feed)specs.push({local:feed.key,rounds:[300,350,400,413,414,415],focus:'queen feeding followed by allied body trap'});
const localHunter=L.games.filter(g=>g.cohort==='exp/q2/cand2d-hunter'&&g.queens[g.side].death?.category==='rammed').sort((a,b)=>b.queens[b.side].death.length-a.queens[a.side].death.length)[0];if(localHunter){const r=localHunter.queens[localHunter.side].death.round;specs.push({local:localHunter.key,rounds:[r-1,r,r+1],focus:'local queen-hunter contact'});}
const output=[];
for(const spec of specs){
 const s=fs.statfsSync(ROOT);if(s.bavail*s.bsize<21*1024**3)throw Error('PAUSE disk');
 const g=spec.local?L.games.find(g=>g.key===spec.local):T.games.find(g=>g.gameId===spec.game),R=raw.load(path.join(ROOT,g.file)),rounds=new Set(spec.rounds),snaps=[],events=[];
 let r=-1,cur=-1;const births=new Map();for(const e of R.events){if(e.type==='roundStart')r=e.round;if(e.type==='turnStart')cur=e.id;if(e.type==='dragonSplit')births.set(e.childId,{round:r,parent:e.parentId,childLength:e.childBody.length,parentLength:e.parentBody.length,childHead:e.childBody[0]});if(rounds.has(r)&&['dragonSplit','dragonDeath','dragonAction'].includes(e.type))events.push({round:r,currentTurn:cur,...e});}
 let lastR=-1;
 const snapshot=(r,c,stage)=>({round:r,stage,W:c.W,H:c.H,dragons:[...c.drag.values()].map(d=>({id:d.id,team:d.team,length:d.body.length,body:d.body.map(p=>({...p})),queen:d.id<=1})),pearls:[...c.pearls.keys()],initialHEdges:Array.from(R.match.map.initialHEdges),initialVEdges:Array.from(R.match.map.initialVEdges),portals:R.match.map.portals});
 ML.perGame(R,{map:g.map,rules:'123'}, {
  turn(d,r,c){if(rounds.has(r)&&lastR!==r){lastR=r;snaps.push(snapshot(r,c,'round start'));}if(rounds.has(r)&&Object.values(g.queens).some(q=>q.death?.round===r&&q.death.moverId===d.id&&q.death.role==='target'))snaps.push(snapshot(r,c,'before attacker #'+d.id));},
  end(n,c){if(rounds.has(499)&&g.rounds===500)snaps.push({round:500,W:c.W,H:c.H,dragons:[...c.drag.values()].map(d=>({id:d.id,team:d.team,length:d.body.length,body:d.body.map(p=>({...p})),queen:d.id<=1})),pearls:[...c.pearls.keys()],initialHEdges:Array.from(R.match.map.initialHEdges),initialVEdges:Array.from(R.match.map.initialVEdges),portals:R.match.map.portals});}
 });
 const name=spec.local?g.cohort.replaceAll('/','-')+'-'+g.localKey.replaceAll(':','-'):'game-'+g.gameId;
 const queens={};for(const tm of ['A','B']){const q=g.queens[tm];queens[tm]={id:q.id,death:q.death,endLength:q.endLength,attackerBirth:q.death?.other?births.get(q.death.other.id)||null:null,curve:q.curve};}
 const rec={name,focus:spec.focus,file:g.file,gameId:g.gameId||null,battleId:g.battleId||null,key:g.key||null,map:g.map,teamA:g.teamA,teamB:g.teamB,side:g.side||null,winner:g.winner,rounds:g.rounds,result:g.result,queens,snapshots:snaps,events};
 fs.writeFileSync(path.join(__dirname,name+'.json'),JSON.stringify(rec,null,2)+'\n');output.push({name,focus:spec.focus,file:g.file,gameId:g.gameId,key:g.key,rounds:spec.rounds,queens});console.log(name,snaps.length,'snapshots');
}
fs.writeFileSync(path.join(__dirname,'deep-selection.json'),JSON.stringify({createdAt:new Date().toISOString(),N:output.length,selection:'all distinct survivor mechanisms + paid hunts, loop accident, queen-on-queen, maximum and median tie-breaks, local feed/trap and hunter',games:output},null,2)+'\n');
