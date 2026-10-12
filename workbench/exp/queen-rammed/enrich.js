'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path');const ROOT=path.resolve(__dirname,'../..');
const {makeLoader,viewerSource}=require('../../tools/top_features'),ML=require('../../tools/mass_ledger');const load=makeLoader(viewerSource());
const snap=(c,r)=>({round:r,W:c.W,H:c.H,dragons:[...c.drag.values()].map(d=>({id:d.id,team:d.team,body:d.body.map(p=>({...p})),born:d.born,parent:d.parent})),pearls:[...c.pearls.keys()]});
const files=fs.readdirSync(path.join(__dirname,'raw')).filter(f=>f.endsWith('.json')).sort();let n=0;
for(const f of files){const p=path.join(__dirname,'raw',f),o=JSON.parse(fs.readFileSync(p)),g=o.game,d=g.death;if(!d)continue;const R=load(path.join(ROOT,g.file));
 ML.perGame(R,{map:g.map,rules:'123'},{
  turn(x,r,c){if(d.other&&x.id===d.other.id&&r===d.round)d.killerTurnState=snap(c,r);},
  action(x,e,r,c){if(x.id===g.queenId&&r===d.lastQueenTurn?.round&&e.action?.kind==='move')d.afterQueenAction=snap(c,r);},
  split(x,ch,e,r,c){if(x.id===g.queenId&&r===d.lastQueenTurn?.round)d.afterQueenAction=snap(c,r);}
 });fs.writeFileSync(p,JSON.stringify(o)+'\n');if(++n%20===0)console.log('enrich',n);}
console.log('enriched deaths',n);
