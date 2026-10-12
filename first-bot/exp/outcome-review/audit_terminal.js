'use strict';
// Census of every official terminal outcome; raw reconstruction of the entire tie class.
const fs=require('fs'),cp=require('child_process');
const {load}=require('../../tools/replay.js'),ML=require('../../tools/mass_ledger.js');
const C='.cache/outcome-review';
const G=fs.readFileSync(C+'/games.jsonl','utf8').trim().split('\n').map(JSON.parse);
const ties=[],checks=[],counts={W:0,D:0,L:0},errors=[];
function guard(){
 const m=+(/System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('/usr/bin/memory_pressure',[],{encoding:'utf8'}))||[])[1];
 const d=+cp.execFileSync('/bin/df',['-g','/'],{encoding:'utf8'}).trim().split('\n').at(-1).trim().split(/\s+/)[3];
 if(!Number.isFinite(m)||m<10||d<20)throw Error('PAUSE resource threshold');
}
guard();
for(const g of G){
 const j=JSON.parse(fs.readFileSync('data/online/'+g.set+'/game-'+g.id+'.json','utf8'));
 const r=j.replay.result,a=r.teamA,b=r.teamB;
 let expected;
 if(a.dragonCount===0||b.dragonCount===0)expected=a.dragonCount===b.dragonCount?null:a.dragonCount?'A':'B';
 else if(a.longestDragon!==b.longestDragon)expected=a.longestDragon>b.longestDragon?'A':'B';
 else expected=a.totalLength===b.totalLength?null:a.totalLength>b.totalLength?'A':'B';
 if(expected!==(r.winner||null))errors.push({key:g.key,expected,actual:r.winner});
 counts[g.outcome]++;
 if(a.longestDragon===b.longestDragon)ties.push({key:g.key,file:g.file,map:g.map,opponent:g.opponent,era:g.era,wave:g.wave,outcome:g.outcome,longest:a.longestDragon,totalA:a.totalLength,totalB:b.totalLength,headsA:a.dragonCount,headsB:b.dragonCount});
}
for(const g of ties){
 guard();const R=load(g.file);let terminal;
 const info={map:g.map};if(g.map==='Prisoners Dilemma')info.variant=R.match.map.initialDragons.length===10?'PD10':'PD6';
 const m=ML.perGame(R,info,{end(rounds,c){terminal={};for(const t of ['A','B']){const ds=[...c.drag.values()].filter(x=>x.team===t);terminal[t]={longest:Math.max(0,...ds.map(x=>x.body.length)),total:ds.reduce((s,x)=>s+x.body.length,0),heads:ds.length};}}});
 const equal=terminal.A.longest===g.longest&&terminal.B.longest===g.longest&&terminal.A.total===g.totalA&&terminal.B.total===g.totalB&&terminal.A.heads===g.headsA&&terminal.B.heads===g.headsB;
 checks.push({key:g.key,terminal,equal,chk:m.chk});
 console.log('tie census '+g.key+' totals '+g.totalA+'/'+g.totalB+' reconstructed '+terminal.A.total+'/'+terminal.B.total+' '+equal);
}
fs.writeFileSync(C+'/terminal-audit.json',JSON.stringify({gameN:G.length,counts,ruleMismatchCount:errors.length,errors,tieN:ties.length,ties,rawTieN:checks.length,rawTieMismatches:checks.filter(x=>!x.equal).length,checks},null,2)+'\n',{flag:'wx'});
