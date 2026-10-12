#!/usr/bin/env node
'use strict';
// Independent of mass_ledger hooks: count raw events by initial/split team IDs; inspect the real 64-bit sonar field.
const fs=require('fs'),path=require('path'),cp=require('child_process'),os=require('os');
const ROOT=path.resolve(__dirname,'../..'),{load}=require(path.join(ROOT,'tools/replay.js'));
const {parseInd}=require(path.join(ROOT,'tools/mech_check.js'));
const folders=[['cand-stack10-online',__dirname],['cand-stack11-online',path.join(__dirname,'w12')]];
function checkResources(){const m=/free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure',[],{encoding:'utf8'}));const d=cp.execFileSync('df',['-g','/'],{encoding:'utf8'}).trim().split('\n').at(-1).trim().split(/\s+/);if(!m||+m[1]<10||+d[3]<20)throw Error('PAUSE: resources below audit floor');}
const rows=[];
for(const [set,out]of folders){
 const ix=JSON.parse(fs.readFileSync(path.join(ROOT,'data/online',set,'index.json')));
 for(const [i,g]of ix.games.entries()){
  checkResources();const R=load(path.join(ROOT,'data/online',set,'M'+g.gameId+'.replay')),ids=new Map(R.match.map.initialDragons.map(d=>[d.id,d.team]));
  const ours=new Set([...ids].filter(([,t])=>t===g.ourSide).map(([id])=>id));
  const x={set,gameId:g.gameId,turns:0,indicators:0,actions:0,splits:0,kinds:{},goals:{},sonars:0,ownSonarsFromIdOver255:0,turnsFromIdOver255:0,firstOwnHighIdRound:null,
   ownHighIds:new Set(),maxOwnId:0,directMessages:0,directTruncatedId:0,directIdMismatchLow8:0,missingSonar64:0,priority:os.getPriority()};let r=-1;
  for(const e of R.events){
   if(e.type==='roundStart')r=e.round;
   if(e.type==='dragonSplit'){ids.set(e.childId,e.team);if(e.team===g.ourSide){ours.add(e.childId);x.splits++;}}
   if(e.type==='turnStart'&&ids.get(e.id)===g.ourSide){x.turns++;x.maxOwnId=Math.max(x.maxOwnId,e.id);if(e.id>255){x.turnsFromIdOver255++;x.ownHighIds.add(e.id);if(x.firstOwnHighIdRound===null)x.firstOwnHighIdRound=r;}}
   if(e.type==='dragonAction'&&ids.get(e.id)===g.ourSide)x.actions++;
   if(e.type==='dragonIndicator'&&ids.get(e.id)===g.ourSide){x.indicators++;const p=parseInd(e.text);x.kinds[p.kind]=(x.kinds[p.kind]||0)+1;const k=p.kind!=='move'?'early_action':p.fg?'F':p.goal||'none';x.goals[k]=(x.goals[k]||0)+1;}
   if(e.type==='sonarPing'&&ids.get(e.senderId)===g.ourSide){
    x.sonars++;if(e.senderId>255)x.ownSonarsFromIdOver255++;
    if(typeof e.value64!=='bigint'){x.missingSonar64++;continue;}
    const v=e.value64^0x9E3779B97F4A7C15n,magic=v>>58n;
    if(magic===0x2Dn){x.directMessages++;const id=Number((v>>50n)&255n);if(id!==(e.senderId&255))x.directIdMismatchLow8++;if(id!==e.senderId)x.directTruncatedId++;}
   }
  }
  x.ownHighIds=x.ownHighIds.size;
  const saved=JSON.parse(fs.readFileSync(path.join(out,`game-${g.gameId}.json`)));
  x.mismatch=[];for(const [key,a,b]of [['turns',x.turns,saved.turns],['indicators',x.indicators,saved.labelled],['actions',x.actions,saved.ledgerTurns],['splits',x.splits,Object.values(saved.splitActual).reduce((s,n)=>s+n,0)]])if(a!==b)x.mismatch.push({key,raw:a,reconstructed:b});
  for(const k of new Set([...Object.keys(saved.kinds),...Object.keys(x.kinds)]))if((saved.kinds[k]||0)!==(x.kinds[k]||0))x.mismatch.push({kind:k});
  for(const k of new Set([...Object.keys(saved.explicitGoals),...Object.keys(x.goals)]))if((saved.explicitGoals[k]||0)!==(x.goals[k]||0))x.mismatch.push({goal:k});
  // Correct a senderId naming mistake in our first pass; no source/input files are touched.
  saved.sonarFromIdOver255=x.ownSonarsFromIdOver255;
  fs.writeFileSync(path.join(out,`game-${g.gameId}.json`),JSON.stringify(saved,null,2)+'\n');
  rows.push(x);if(global.gc)global.gc();if((i+1)%10===0)console.log(`${set}: ${i+1}/${ix.games.length}, raw/reconstructed mismatches ${rows.reduce((s,v)=>s+v.mismatch.length,0)}`);
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,500);
 }
 // Refresh only the newly created per-game bundle with the checked sonar count.
 fs.writeFileSync(path.join(out,'per-game.jsonl'),ix.games.map(g=>JSON.stringify(JSON.parse(fs.readFileSync(path.join(out,`game-${g.gameId}.json`))))).join('\n')+'\n');
}
const sums=[];
for(const [set]of folders){const a=rows.filter(x=>x.set===set),s={set,games:a.length,mismatches:a.reduce((s,x)=>s+x.mismatch.length,0),gamesWithOwnIdOver255:a.filter(x=>x.ownHighIds).length,maxOwnId:Math.max(...a.map(x=>x.maxOwnId))};
 for(const k of ['turns','indicators','actions','splits','sonars','ownSonarsFromIdOver255','turnsFromIdOver255','directMessages','directTruncatedId','directIdMismatchLow8','missingSonar64','ownHighIds'])s[k]=a.reduce((s,x)=>s+x[k],0);
 sums.push(s);
}
fs.writeFileSync(path.join(__dirname,'raw-verification.json'),JSON.stringify({summary:sums,games:rows},null,2)+'\n');
console.log(JSON.stringify(sums,null,2));if(sums.some(x=>x.mismatches))process.exitCode=1;
