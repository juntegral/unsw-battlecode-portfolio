'use strict';
// Second independent, lightweight metadata census: directory game files, no index.
const fs=require('fs');
const first=JSON.parse(fs.readFileSync('.cache/outcome-review/metadata-ledger.json','utf8'));
const sets=[['W0.1','cand-merge2-online'],['W0.2','cand-merge2-online-r2'],['W0.3','cand-merge2-online-r3']];
for(let i=1;i<=12;i++)sets.push(['W'+i,i===7?'cand-stack6-online-r2':'cand-stack'+(i<=6?i:i-1)+'-online']);
const h=['baseline-r1','baseline-r1b','baseline-r1c','cand-avoid6-online','cand-portal1-online','cand-swarm8-online','base-px8-online','base-px9d-online','px-king-v2-online'];
for(const s of h)sets.push([s,s]);
const result={},mismatch=[],seen=new Set();
for(const [w,s]of sets){const dir='data/online/'+s;if(!fs.existsSync(dir))continue;
 const a={top6:{N:0,W:0,D:0,L:0,ourEliminated:0,theirEliminated:0,ourFinalSum:0,theirFinalSum:0},DEV:{N:0,W:0,D:0,L:0,ourEliminated:0,theirEliminated:0,ourFinalSum:0,theirFinalSum:0}};
 const files=fs.readdirSync(dir).filter(x=>/^game-\d+\.json$/.test(x));
 for(const file of files){const j=JSON.parse(fs.readFileSync(dir+'/'+file,'utf8'));const side=j.teamAId===583?'A':j.teamBId===583?'B':null;if(!side)throw Error('Not our game '+file);
  if(seen.has(j.id))throw Error('Duplicate ID '+j.id);seen.add(j.id);
  const en=side==='A'?'B':'A',opp=j['team'+en+'Id'];if(![306,70,20,801,264,46,545].includes(opp))throw Error('Unexpected opponent');
  const r=j.replay.result,z=a[opp===545?'DEV':'top6'],o=(j.winner||'').toUpperCase();z.N++;z[o===side?'W':o===en?'L':'D']++;
  z.ourEliminated+=r['team'+side].dragonCount===0;z.theirEliminated+=r['team'+en].dragonCount===0;z.ourFinalSum+=r['team'+side].longestDragon;z.theirFinalSum+=r['team'+en].longestDragon;
 }
 result[w]=a;
 for(const g of['top6','DEV']){const b=first.cells[w][g];for(const k of['N','ourEliminated','theirEliminated','ourFinalSum','theirFinalSum'])if(a[g][k]!==b[k])mismatch.push({wave:w,group:g,k,first:b[k],second:a[g][k]});for(const k of['W','D','L'])if(a[g][k]!==+(b.index[k]||0))mismatch.push({wave:w,group:g,k,first:b.index[k]||0,second:a[g][k]});}
}
fs.writeFileSync('.cache/outcome-review/metadata-audit.json',JSON.stringify({N:seen.size,mismatchCount:mismatch.length,mismatches:mismatch,waves:result},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({firstN:first.N,independentN:seen.size,mismatchCount:mismatch.length}));
