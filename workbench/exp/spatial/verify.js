// Compare independently reconstructed spatial counts game by game, then sum per map/layout/class.
'use strict';
const fs=require('fs'),path=require('path'),S=require('./lib'),O=path.join(__dirname,'cache');
function compare(){const P=JSON.parse(fs.readFileSync(path.join(O,'population.json'),'utf8')),mine=[...new Map(S.readl(path.join(O,'games.jsonl')).map(r=>[r.key,r])).values()],other=new Map(S.readl(path.join(O,'recount.jsonl')).map(r=>[r.key,r])),byMap={},mismatches=[],unverified=[],checks={},ties=[];let n=0;
 const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 for(const a of mine){const b=other.get(a.key);if(!b){unverified.push(a.key);continue;}n++;checks.finalMismatch=(checks.finalMismatch||0)+b.finalMismatch;
  const diff=(field,x,y)=>{if(!eq(x,y))mismatches.push({key:a.key,field,primary:x,independent:y});};
  for(const z of ['rounds','winner','stall','roundsByPhase'])diff(z,a[z],b[z]);if(a.layout!==b.layout){if(b.layout==='?'&&a.layoutEvidence.ca===a.layoutEvidence.cb)ties.push({key:a.key,primary:a.layout,evidence:a.layoutEvidence});else diff('layout',a.layout,b.layout);}
  for(const t of ['A','B']){for(const z of ['app','hr','hrMid','cp','nat','natMid','death','deathMid','pocketDeath','splits','pings'])diff(t+'.'+z,a[t][z],b[t][z]);diff(t+'.sd',a[t].sd.map(p=>[p.n,p.pocket,p.present]),b[t].sd);if(a.layout===b.layout)for(const z of ['groupHold','groupStaff'])diff(t+'.'+z,a[t][z],b[t][z]);}
  if(a.layout===b.layout){diff('groupApp',a.groupApp,b.groupApp);diff('pocketFountains',a.pocketFountains,b.pocketFountains);if(a.tileCounts&&b.tileCounts)diff('tileCounts',a.tileCounts,b.tileCounts);}
  if(a.src==='top'&&a.stall.length||a.layout==='?')continue;const key=a.map+'/'+a.layout;const m=byMap[key]||(byMap[key]={N:0,classes:{}});m.N++;
  const labels=a.src==='top'?(a.winner?[[a.winner,'elite-winners'],[a.winner==='A'?'B':'A','elite-losers']]:[['A','elite-draws'],['B','elite-draws']]):[[a.us,(a.src==='local'?'local:':'ours:')+a.family]];
  for(const [t,label] of labels){const c=m.classes[label]||(m.classes[label]={N:0,primary:{natural:S.zero(),headRounds50_374:S.zero(),appearance:S.zero(),trap:S.zero()},independent:{natural:S.zero(),headRounds50_374:S.zero(),appearance:S.zero(),trap:S.zero()}});c.N++;for(const [name,r] of [['primary',a],['independent',b]])for(let i=0;i<6;i++){c[name].natural[i]+=S.sum(r[t].nat.map(p=>p[i]));c[name].headRounds50_374[i]+=r[t].hrMid[i];c[name].appearance[i]+=S.sum(r[t].app.map(p=>p[i]));c[name].trap[i]+=r[t].death[1][i];}}
 }
 const expected=P.tasks.filter(t=>t.src!=='top'||S.SELECT.has(t.map)).length,result={generatedAt:new Date().toISOString(),primaryGames:mine.length,independentGames:other.size,comparedGames:n,expectedSpatialGames:expected,unverified,checks,layoutTies:ties,mismatchCount:mismatches.length,mismatches,byMap};fs.writeFileSync(path.join(O,'verification.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({primaryGames:mine.length,independentGames:other.size,compared:n,expected,unverified:unverified.length,checks,ties:ties.length,mismatches:mismatches.length,first:mismatches.slice(0,4)}));return result;
}
if(require.main===module)compare();module.exports={compare};
