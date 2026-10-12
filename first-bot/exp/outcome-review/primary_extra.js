'use strict';
// Census second pass of the primary simulator, independently contrasted with the
// official-update reconstruction. Fills late pieces, all-life lineage supply and
// all missing exposure caches. One process, no writes to source caches.
const fs=require('fs'),cp=require('child_process');
const {load}=require('../../tools/replay.js'),ML=require('../../tools/mass_ledger.js');
const C='.cache/outcome-review';
const games=fs.readFileSync(C+'/primary.jsonl','utf8').trim().split('\n').map(JSON.parse);
const raw=new Map(fs.readFileSync(C+'/independent.jsonl','utf8').trim().split('\n').map(l=>{const x=JSON.parse(l);return[x.key,x];}));
const out=fs.openSync(C+'/primary-extra.jsonl','wx'),log=fs.openSync(C+'/resource-primary-extra.jsonl','wx');
const mismatches=[],causeDifferences=[];let last=0,done=0;
const totals={primary:{latePieces:0,lineSacAll:0,exposedTurns:0,eligibleTurns:0},independent:{latePieces:0,lineSacAll:0,exposedTurns:0,eligibleTurns:0}};
function guard(){if(Date.now()-last<20000)return;last=Date.now();const m=cp.execFileSync('/usr/bin/memory_pressure',[],{encoding:'utf8'}),memory=+(/System-wide memory free percentage:\s*(\d+)%/.exec(m)||[])[1],disk=+cp.execFileSync('/bin/df',['-g','/'],{encoding:'utf8'}).trim().split('\n').at(-1).trim().split(/\s+/)[3];fs.writeSync(log,JSON.stringify({at:new Date().toISOString(),memory,disk})+'\n');if(!Number.isFinite(memory)||memory<10||disk<20)throw Error('PAUSE resources');}
for(const g of games){guard();const R=load(g.file),info={map:g.map};if(g.map==='Prisoners Dilemma')info.variant=R.match.map.initialDragons.length===10?'PD10':'PD6';
 let seq=0,fin;const birth=new Map(),parent=new Map(),rows=[],eats=[],T={A:{latePieces:0,lineSacAll:0,exposedTurns:0,eligibleTurns:0,kingDeaths:[]},B:{latePieces:0,lineSacAll:0,exposedTurns:0,eligibleTurns:0,kingDeaths:[]}};
 for(const d of R.match.map.initialDragons)birth.set(d.id,-1);
 const m=ML.perGame(R,info,{
  turn(d,r,c){seq++;if(r<300||d.body.length<8)return;let nearest=Infinity;for(const x of c.drag.values())if(x.team!==d.team)nearest=Math.min(nearest,c.tdist(d.body[0],x.body[0]));rows.push([seq,d.id,nearest<=6?1:0]);},
  split(p,ch,e,r,c){seq++;birth.set(ch.id,seq);parent.set(ch.id,p.id);if(r>=250&&e.childBody.length<=3)T[ch.team].latePieces++;},
  eat(d,tile,o,r,c){seq++;if(o>=0&&c.deaths[o].team===d.team&&c.deaths[o].cause===0)eats.push([seq,d.id]);},
  death(d,rec,idx,other,r,c){seq++;if(rec.king)T[d.team].kingDeaths.push({id:d.id,r,len:rec.len,cause:ML.CAUSE[rec.cause],otherId:other?.id??null,otherLength:other?.body.length??null});},
  end(rounds,c){fin={A:c.kingOf('A')?.id??-1,B:c.kingOf('B')?.id??-1};}
 });
 for(const tm of['A','B']){const ids=[];for(let id=fin[tm];id>=0;id=parent.get(id)??-1)ids.push(id);ids.reverse();const windows=new Map(ids.map((id,i)=>[id,[birth.get(id),i+1<ids.length?birth.get(ids[i+1]):Infinity]]));
  for(const [s,id,near]of rows){const w=windows.get(id);if(w&&s>w[0]&&s<w[1]){T[tm].eligibleTurns++;T[tm].exposedTurns+=near;}}
  if(fin[tm]<0)T[tm].lineSacAll=null;else for(const[s,id]of eats){const w=windows.get(id);if(w&&s>w[0]&&s<w[1])T[tm].lineSacAll++;}
  const x=raw.get(g.key).teams[tm];
  const cmp=(f,p,v)=>{if(p!==v)mismatches.push({key:g.key,team:tm,field:f,primary:p,independent:v});};
  cmp('latePieces',T[tm].latePieces,x.births250);cmp('lineSacAll',T[tm].lineSacAll,x.lineSacAll);cmp('eligibleTurns',T[tm].eligibleTurns,x.exposureTurns);
  cmp('exposedTurns',T[tm].exposedTurns,Math.round((x.exposure||0)*x.exposureTurns));
  for(const kd of T[tm].kingDeaths){const rk=x.kd.find(z=>z.id===kd.id&&z.r===kd.r);if(!rk||rk.len!==kd.len)mismatches.push({key:g.key,team:tm,field:'kingDeath',primary:kd,independent:rk??null});else if(rk.cause!==kd.cause)causeDifferences.push({key:g.key,team:tm,id:kd.id,r:kd.r,primary:kd.cause,independent:rk.cause});}
  for(const k of['latePieces','lineSacAll','exposedTurns','eligibleTurns']){totals.primary[k]+=T[tm][k]||0;totals.independent[k]+=(k==='latePieces'?x.births250:k==='lineSacAll'?x.lineSacAll:k==='eligibleTurns'?x.exposureTurns:Math.round((x.exposure||0)*x.exposureTurns))||0;}
 }
 if(Object.values(m.chk).some(x=>x!==0))throw Error('Primary reconstruction checks '+g.key+' '+JSON.stringify(m.chk));
 fs.writeSync(out,JSON.stringify({key:g.key,teams:T,chk:m.chk})+'\n');done++;if(done%70===0)console.log('primary-extra '+done+'/'+games.length+' mismatches='+mismatches.length+' causeDifferences='+causeDifferences.length);
}
fs.closeSync(out);fs.closeSync(log);
fs.writeFileSync(C+'/extra-checks.json',JSON.stringify({totals,mismatchCount:mismatches.length,mismatches,causeDifferenceCount:causeDifferences.length,causeDifferences},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({totals,mismatchCount:mismatches.length,causeDifferenceCount:causeDifferences.length,first:mismatches.slice(0,5)}));
