#!/usr/bin/env node
// Read-only spatial diagnostic. No extraction/cache writes, network, or games are started.
// node eval/spatial_report.js <online set name/dir | local exp dir | games dir | one game dir>
// Core f-bins are team-relative; the seven x-bands below intentionally reproduce the original brief.
'use strict';
const fs=require('fs'),path=require('path');
const ROOT=path.resolve(__dirname,'..'),S=require(path.join(ROOT,'exp/spatial/lib.js'));
const {localTasks,onlineTasks,resource}=require(path.join(ROOT,'exp/spatial/extract.js'));
const sum=S.sum,zero=S.zero;
function tasksFor(arg){let dir=path.resolve(arg);if(!fs.existsSync(dir))dir=path.join(ROOT,'data/online',arg);if(!fs.existsSync(dir))throw Error('No such set or directory: '+arg);if(fs.existsSync(path.join(dir,'index.json')))return onlineTasks(dir);const sets=fs.readdirSync(dir,{withFileTypes:true}).filter(e=>e.isDirectory()&&e.name.endsWith('-px4'));if(sets.length)return sets.flatMap(e=>localTasks(path.join(dir,e.name,'games')));return localTasks(fs.existsSync(path.join(dir,'games'))?path.join(dir,'games'):dir);}
function pct(a){const n=sum(a);return a.map(v=>n?(100*v/n).toFixed(1):'NA').join(' / ');}
function report(tasks){const maps={},checks={},hookDiff=[];let n=0;
 for(const t of tasks){if(n++%20===0){const r=resource();if(r.memory===null||r.memory<10||r.diskGB<20)throw Error('PAUSED: resource limit '+JSON.stringify(r));}const row=S.analyse(S.raw.load(t.file),t),key=row.map+'/'+row.layout,us=row.us,them=us==='A'?'B':'A',o=row[us],e=row[them];for(const [k,v] of Object.entries(row.checks))checks[k]=(checks[k]||0)+v;if(row.hookDifference.A||row.hookDifference.B)hookDiff.push({key:row.key,...row.hookDifference});const m=maps[key]||(maps[key]={N:0,hr:zero(),app:zero(),hrTheir:zero(),intake:zero(),trap:zero(),pocketTrap:zero(),naturalUs:0,naturalThem:0,sd:0,sdPocket:0,sdPresent:0,sdDistances:zero(7),sdDistanceSum:0,phaseApp:S.matrix(),phaseHR:S.matrix(),xHeads:zero(7),xAppear:zero(7),xOwnTwoHeads:0,xOwnTwoAppear:0,hookUs:0,hookThem:0});m.N++;
  for(let i=0;i<6;i++){m.hr[i]+=o.hrMid[i];m.hrTheir[i]+=e.hrMid[i];m.app[i]+=sum(o.app.slice(0,3).map(p=>p[i]));m.intake[i]+=sum(o.nat.map(p=>p[i]));m.trap[i]+=o.death[1][i];m.pocketTrap[i]+=o.pocketDeath[1][i];}
  for(let p=0;p<4;p++)for(let i=0;i<6;i++){m.phaseApp[p][i]+=o.app[p][i];m.phaseHR[p][i]+=o.hr[p][i];}
  m.naturalUs+=row.ledgerNatural[us];m.naturalThem+=row.ledgerNatural[them];m.hookUs+=o.xNatHook;m.hookThem+=e.xNatHook;for(const p of o.sd){m.sd+=p.n;m.sdPocket+=p.pocket;m.sdPresent+=p.present;m.sdDistanceSum+=p.sumDistance;for(let i=0;i<7;i++)m.sdDistances[i]+=p.distance[i];}for(let i=0;i<7;i++){m.xHeads[i]+=o.xHeads[i];m.xAppear[i]+=o.xAppearance[i];}const own=us==='A'?[0,1]:[5,6];m.xOwnTwoHeads+=sum(own.map(i=>o.xHeads[i]));m.xOwnTwoAppear+=sum(own.map(i=>o.xAppearance[i]));
 }
 console.log('sets: '+[...new Set(tasks.map(t=>t.set))].join(', ')+'; games N='+tasks.length);
 console.log('f bins: [0,.2) / [.2,.4) / [.4,.6) / [.6,.8) / [.8,1]; final column = unreachable from both starts');
 for(const [name,m] of Object.entries(maps).sort()){console.log(`\n${name} N=${m.N}`);console.log(`  heads us r50-374 (%) [head-rounds N=${sum(m.hr)}]: ${pct(m.hr)}`);console.log(`  natural appearances r0-374 (%) [pearls N=${sum(m.app)}]: ${pct(m.app)}`);console.log(`  natural eaten us ${m.naturalUs} / them ${m.naturalThem}`);console.log(`  trap deaths by f-bin: ${m.trap.join(' / ')}; inside pockets: ${m.pocketTrap.join(' / ')}`);console.log(`  sd targets N=${m.sd}; to pockets ${m.sd?Math.round(100*m.sdPocket/m.sd):'NA'}% (${m.sdPocket}/${m.sd}); pearl present at decision ${m.sd?(100*m.sdPresent/m.sd).toFixed(1):'NA'}%; mean target distance ${m.sd?(m.sdDistanceSum/m.sd).toFixed(2):'NA'}`);console.log(`  sd target distances [0,1,2,3,4-7,8-15,16+]: ${m.sdDistances.join(' / ')}`);console.log(`  compatibility x-band heads r50-374 sampled each 5 rounds (%): ${pct(m.xHeads)}`);console.log(`  compatibility x-band appearances r<375 (%): ${pct(m.xAppear)}`);console.log(`  two home x-bands: heads ${sum(m.xHeads)?Math.round(100*m.xOwnTwoHeads/sum(m.xHeads)):'NA'}% / appearances ${sum(m.xAppear)?Math.round(100*m.xOwnTwoAppear/sum(m.xAppear)):'NA'}%; previous-hook set-difference recount ${m.hookUs}/${m.hookThem}`);
  for(let p=0;p<4;p++)console.log(`  r${S.PHASES[p].join('-')}: appearances ${pct(m.phaseApp[p])} (N=${sum(m.phaseApp[p])}); heads ${pct(m.phaseHR[p])} (HR=${sum(m.phaseHR[p])})`);
 }
 console.log('\nreconciliation (all expected zero): '+JSON.stringify(checks));console.log('previous-turn set-difference recount exceptions: '+hookDiff.length+(hookDiff.length?' '+JSON.stringify(hookDiff):''));if(Object.values(checks).some(v=>v!==0))process.exitCode=1;return {maps,checks,hookDiff};
}
if(require.main===module){if(process.argv.length!==3){console.error('usage: node eval/spatial_report.js <set dir or exp dir>');process.exitCode=2;}else try{const tasks=tasksFor(process.argv[2]);if(!tasks.length)throw Error('No replays found');report(tasks);}catch(e){console.error(e.stack);process.exitCode=1;}}
module.exports={tasksFor,report};
