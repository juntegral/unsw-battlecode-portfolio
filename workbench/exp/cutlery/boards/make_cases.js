'use strict';
const fs=require('fs'),path=require('path'),z=require('zlib'),cp=require('child_process'),ROOT=path.resolve(__dirname,'../../..'),raw=require(ROOT+'/legacy/exp/intake-gap/rawload');
const P=JSON.parse(z.gunzipSync(fs.readFileSync(ROOT+'/exp/cutlery/population.json.gz'))),tasks=new Map(P.tasks.map(t=>[t.key,t]));
const cases=[
 ['reproduction-cutlery','592400','B','25,50,100','재생산·초반 질량 분산','Trophy cohort map-mean nearest candidate'],
 ['reproduction-ours','677083','A','25,50,100','재생산·초반 질량 분산','Trophy cohort map-mean nearest candidate'],
 ['combat-cutlery','689737','A','50,72,100','능동 교환','Trophy equal|ahead ram rate closest to cohort mean'],
 ['combat-ours','748855','A','50,100,185','능동 교환','Trophy equal|ahead ram rate closest to cohort mean'],
 ['cohesion-cutlery','756247','B','25,50,100','아군 간격','Trophy capped-distance closest to cohort mean; exact headcount control refutes simple pull'],
 ['cohesion-ours','650966','A','25,50,100','아군 간격','Trophy capped-distance closest to cohort mean; exact headcount control refutes simple pull'],
 ['scout-cutlery','752457','A','50,100,250','정찰 배치','Trophy L2-3 near-enemy fraction closest to cohort mean'],
 ['scout-ours','724088','A','50,100,250','정찰 배치','Trophy L2-3 near-enemy fraction closest to cohort mean'],
 ['king-cutlery','687911','A','50,100,250','왕 주변','Trophy enemy heads within8 closest to cohort mean'],
 ['king-ours','724133','A','50,100,250','왕 주변','Trophy enemy heads within8 closest to cohort mean'],
 ['intake-cutlery','661410','B','50,100,250','섭취','Trophy per-move intake closest to cohort mean'],
 ['intake-ours','666204','A','50,100,250','섭취','Trophy per-move intake closest to cohort mean'],
 ['custom-score-loss','806806','A','100,250,450,499','custom surviving score loss','closest class centroid N9'],
 ['custom-extinction','806972','A','50,100,150,190','custom extinction100-249','closest class centroid N4'],
 ['custom-success','806579','A','50,100,250,499','custom victory','first series Stripes win; illustrative only'],
];
const LC=JSON.parse(fs.readFileSync(ROOT+'/exp/cutlery/audit/loss-classes.json'));
for(const cat of ['surviving_score_loss','extinct_before100','extinct_100_249','extinct_250plus']){
 const g=LC.groups['top/'+cat],r=g.representatives[0],t=tasks.get(r.game),tm=['A','B'].find(s=>t.labels[s].includes('Cutlery'));cases.push(['loss-'+cat,r.game,tm,cat==='extinct_before100'?'25,50,65':cat==='extinct_100_249'?'25,50,100,150':cat==='extinct_250plus'?'50,100,250,350':'50,100,250,499','loss/'+cat,'closest multivariate class centroid; classN='+g.N]);
}
let index=[];
for(const [slug,id,tm,rounds,family,selection]of cases){
 const t=tasks.get(id);if(!t)throw Error('missing '+id);const R=raw.load(t.file);fs.writeFileSync(__dirname+'/'+slug+'-map.json',JSON.stringify(R.match.map));
 const r=cp.spawnSync(process.execPath,[ROOT+'/eval/board.js',t.file,t.map,t.variant||'a',tm,rounds],{encoding:'utf8',maxBuffer:20*1024*1024,env:{...process.env,UNSW_RULES:t.rules==='123'?'123':'110'}});if(r.status)throw Error(r.stderr);fs.writeFileSync(__dirname+'/'+slug+'.txt',r.stdout);
 const d=cp.spawnSync('python3',[__dirname+'/render.py',slug],{encoding:'utf8'});if(d.status)throw Error(d.stderr);
 index.push({slug,game:id,map:t.map,team:tm,rounds:rounds.split(',').map(Number),rules:t.rules,custom:t.custom,winner:R.result.winner,family,selection,png:slug+'.png',ascii:slug+'.txt',producer:'node eval/board.js',physicsScope:'Replay reconstruction only; no games played',visuallyInspected:false});console.log(slug);
}
fs.writeFileSync(__dirname+'/index.json',JSON.stringify({definitions:{snapshots:'eval/board.js takes first dragon turnStart of chosen round; not necessarily exact roundStart. Full board retrospective, invisible information is not an inferred bot observation.',selection:'Means/centroids chosen before pictures; medoids from preliminary broadened known-cohort summaries, retained as illustrations after source-primary reweighting. Custom success hand-selected explicitly illustrative; no representative claim.'},N:index.length,boards:index},null,2));
