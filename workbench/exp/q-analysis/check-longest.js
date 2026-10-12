'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path');
const ROOT=path.resolve(__dirname,'../..');
const {makeLoader,viewerSource}=require('../../tools/top_features');
const ML=require('../../tools/mass_ledger'),load=makeLoader(viewerSource());
const file=path.join(__dirname,'tables.json'),t=JSON.parse(fs.readFileSync(file,'utf8'));
let games=0,events=0,global=0,other=0;
for(const s of ['king','hunter','gen'])for(const g of t.games['exp/v16/q1/q18b2-'+s]){
  if(!g.feeds.some(f=>f.r<430&&f.toQueen&&f.queenAlive))continue;
  games++;ML.perGame(load(path.join(ROOT,g.file)),{map:g.map,variant:'?',rules:'123'}, {death(d,rec,idx,o,r,c){
    const f=g.feeds.find(f=>f.donor===d.id&&f.r===r&&r<430&&f.toQueen&&f.queenAlive);if(!f)return;
    const q=c.drag.get(g.Q);f.queenLengthAtFeed=q?.body.length??null;
    const best=[...c.drag.values()].filter(x=>x.team===g.side).sort((a,b)=>b.body.length-a.body.length||a.id-b.id)[0];
    f.queenGlobalLongest=best?.id===g.Q;events++;global+=f.queenGlobalLongest?1:0;other+=f.kLongest?1:0;
  }});
}
t.earlyQueenGlobalLongest={games,events,globalLongest:global,longestExcludingDonor:other};
const criterion=t.criteria.find(c=>c.id==='Q1B.9.2.1-queen');criterion.value.longest=global;
fs.writeFileSync(file,JSON.stringify(t,null,2)+'\n');console.log(t.earlyQueenGlobalLongest);
