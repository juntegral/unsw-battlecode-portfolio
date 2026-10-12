'use strict';
const fs=require('fs'),path=require('path'),OUT=__dirname,ROOT=path.resolve(OUT,'../..');
const read=n=>JSON.parse(fs.readFileSync(path.join(OUT,n+'.json'))),T=read('tables'),P=read('population'),V=read('verification'),F=read('fountain-verification'),B=read('blocking-verification'),D=read('deep-selection');
const failures=[];let checks=0;function eq(a,b,label){checks++;if(a!==b)failures.push({label,actual:a,expected:b});}
eq(T.status,'complete','table completion');eq(T.population.completed,P.tasks.length,'frozen population coverage');eq(V.N,P.tasks.length,'independent coverage');eq(V.complete,true,'independent completion');
for(const [label,v]of [['all',V],['fountain',F],['blocking',B]]){eq(v.mismatches,0,label+' mismatch');for(const [k,a]of Object.entries(v.maps||{}))for(const [f,x]of Object.entries(a.primary))eq(x,a.independent[f],label+'/'+k+'/'+f);}
for(const [k,v]of Object.entries(V.checks))eq(v,0,'ledger/'+k);for(const [k,v]of Object.entries(T.checks))eq(v,0,'primary/'+k);eq(T.occupationCheck.N,P.tasks.length,'occupation coverage');eq(T.occupationCheck.intervalMismatch,0,'occupation interval');
const economic=['natural','fountain','ownDrop','enemyDrop','ownPocketDrop','deaths','deathLength','drops','recoveredOwn','recoveredEnemy','sprintCost','rawNet','recycledNet','headRounds'];
let episodeSum=0,gameSum=0,familySum=0;
for(const [mk,m]of Object.entries(T.maps)){
 gameSum+=Object.values(m.N).reduce((s,v)=>s+v,0);
 for(const [role,g]of Object.entries(m.groups)){
  const label=mk+'/'+role;episodeSum+=g.all.episodes;familySum+=g.family.episodes;
  for(const [a,b]of [['all','family'],['fountainPockets','fountainFamily']])for(const f of economic)eq(g[a][f],g[b][f],label+'/'+a+' family conservation '+f);
  for(const [cat,total]of [['protocol','all'],['kind','all'],['pocket','all'],['fountainProtocol','fountainPockets'],['familyProtocol','fountainFamily'],['familyNatural','fountainFamily'],['familyRelay','fountainFamily']])for(const f of ['episodes',...economic])eq(Object.values(g[cat]).reduce((s,a)=>s+a[f],0),g[total][f],label+'/'+cat+' partition '+f);
  eq(Object.values(g.deathReasons).reduce((s,a)=>s+a,0),g.all.deaths,label+' death cause coverage');eq(Object.values(g.fountainDeathReasons).reduce((s,a)=>s+a,0),g.fountainPockets.deaths,label+' fountain death cause coverage');
  for(const a of [g.all,g.fountainPockets,g.family,g.fountainFamily,...Object.values(g.familyProtocol)]){
   eq(a.rawNet,a.natural+a.ownDrop+a.enemyDrop-a.sprintCost-a.deathLength,label+' raw net identity');eq(a.recycledNet,a.rawNet+a.recoveredOwn-a.ownPocketDrop,label+' recovered net identity');eq(a.recoveredOwn+a.recoveredEnemy+a.unrecovered,a.drops,label+' drop balance');eq(a.occupiedPocketRounds<=a.headRounds,true,label+' unique occupation bounded');
  }
  const h=m.gameDistribution[role];eq(h.N,g.all.N,label+' histogram cohort');for(const name of ['natural','fountain','recycledNet','fountainNet','rounds'])eq(Object.values(h[name]).reduce((s,a)=>s+a,0),h.N,label+' histogram '+name);
  for(const [name,total]of [['natural',g.all.natural],['fountain',g.all.fountain],['recycledNet',g.all.recycledNet],['fountainNet',g.fountainPockets.recycledNet]])eq(Object.entries(h[name]).reduce((s,[k,a])=>s+Number(k)*a,0),total,label+' histogram weighted '+name);
 }
}
eq(gameSum,T.population.completed-T.population.rejectedStalledTop,'eligible games');eq(episodeSum,T.population.episodes,'physical episode totals');
for(const d of D.filter(v=>v.best&&v.best.eid!==undefined)){const n=d.map.replaceAll('/','-').replaceAll(' ','_')+'-'+d.role.replaceAll(':','-'),r=read('deep-'+n),g=T.maps[d.map].groups[d.role];eq(d.classN,g.familyProtocolNatural['splitEscape|'+d.naturalClass].episodes,n+' full class size');eq(d.candidateN<=d.classN,true,n+' candidate size');eq(r.best.episode.family.recycledNet,r.best.familyEpisodes.reduce((s,e)=>s+e.recycledNet,0),n+' deep family net');}
const report=fs.readFileSync(path.join(ROOT,'research/observations/pocket-harvest.md'),'utf8');let columns=null;
for(const line of report.split('\n')){if(line.startsWith('| ')){const n=line.split('|').length-2;if(columns===null)columns=n;else eq(n,columns,'report table columns: '+line.slice(0,90));}else columns=null;}
const images=[...report.matchAll(/!\[[^\]]*\]\(([^)]+)\)/g)].map(m=>m[1]);eq(images.length,3,'board picture count');for(const img of images)eq(fs.existsSync(path.resolve(ROOT,'research/observations',img)),true,'board exists '+img);
for(const m of report.matchAll(/\]\(([^)]+)\)/g)){const target=m[1];if(target.endsWith('SUMMARY.txt'))continue;eq(fs.existsSync(path.resolve(ROOT,'research/observations',target)),true,'report link '+target);}
const archive=read('archive');eq(archive.verified,true,'compressed cache verification');eq(archive.sha256,archive.decompressedSha256,'compressed cache hash');eq(fs.statSync(path.join(OUT,archive.file)).size,archive.compressedBytes,'compressed cache size');eq(fs.statSync(path.join(OUT,archive.source)).size,archive.sourceBytes,'source cache size');
const result={status:failures.length?'FAIL':'PASS',checks,N:P.tasks.length,eligibleGames:gameSum,physicalEpisodes:episodeSum,harvestFamilies:familySum,boardPictures:images.length,failures};fs.writeFileSync(path.join(OUT,'checks.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));if(failures.length)process.exitCode=1;
