'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'../..'),file=path.join(__dirname,'tables.json');
const t=JSON.parse(fs.readFileSync(file,'utf8'));
const med=a=>a.length?[...a].sort((a,b)=>a-b)[a.length>>1]:null;
const gs=v=>['king','hunter','gen'].flatMap(s=>t.games['exp/v16/q1/'+v+'-'+s]);
const variants=['v18','q18','q18b2'];
const maps=Object.fromEntries(variants.map(v=>[v,new Map(gs(v).map(g=>[g.key,g]))]));
const present=(g,r)=>g.rounds>r&&(!g.qDeath||g.qDeath.r>r);
t.actualCheckpoints={};
for(const v of variants)t.actualCheckpoints[v]=Object.fromEntries([50,100,250,300,340,350,400,430,450].map(r=>{
  const a=gs(v).filter(g=>present(g,r));return[r,{N:a.length,queenMedian:med(a.map(g=>g.qLen[r])),backupMedian:med(a.map(g=>g.backup[r]||0))}];}));
t.actualPaired={};
for(const cohort of ['allAlive400','b2Alive430','bothQ1B2Alive430','baseAlive300']){
  const r=cohort==='allAlive400'?400:cohort==='baseAlive300'?300:430;
  const keys=gs('v18').filter(g=>cohort==='allAlive400'?variants.every(v=>present(maps[v].get(g.key),r)):
    cohort==='b2Alive430'?present(maps.q18b2.get(g.key),r):cohort==='bothQ1B2Alive430'?['q18','q18b2'].every(v=>present(maps[v].get(g.key),r)):present(g,r)).map(g=>g.key);
  const p={N:keys.length,keys,variants:{}};
  for(const v of variants){const a=keys.map(k=>maps[v].get(k));p.variants[v]={
    queen:Object.fromEntries([300,340,350,400,430,450,500].map(r=>[r,med(a.map(g=>r===500?g.qEnd:g.rounds>r?g.qLen[r]:null).filter(x=>x!==null))])),
    backup:Object.fromEntries([300,350,400,430].map(r=>[r,med(a.map(g=>g.backup[r]||0))])),
    growth340to400:med(a.map(g=>g.qLen[400]-g.qLen[340])),feedPearls:a.reduce((s,g)=>s+g.qEat.feed,0),
    alive500:a.filter(g=>g.qEnd>0).length};}
  p.rows=keys.map(key=>({key,...Object.fromEntries(variants.map(v=>[v,{queen:maps[v].get(key).qLen,backup:maps[v].get(key).backup,death:maps[v].get(key).qDeath?.r??null}]))}));t.actualPaired[cohort]=p;
}
t.identityDiagnosis=JSON.parse(fs.readFileSync(path.join(__dirname,'identity-diagnosis.json'),'utf8'));
t.q2.terminalSurvival={};
for(const[name,x]of Object.entries(t.q2.sets)){const a=t.games['exp/q2/'+name].filter(g=>!g.pocket);t.q2.terminalSurvival[name]={N:a.length,aliveAtActual500:a.filter(g=>g.rounds===500&&g.qEnd>0).length,earlyTerminalAlive:a.filter(g=>g.rounds<500&&g.qEnd>0).map(g=>({key:g.key,rounds:g.rounds}))};}
const digest=f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,f))).digest('hex');
t.existingSafetyEvidence={q1OffSmoke:{path:'exp/v16/q1/smoke-v18q1.txt',sha256:digest('exp/v16/q1/smoke-v18q1.txt'),passed:2,N:2,appliesTo:'merged v1.8 with Q1/Q1B switches OFF; not the ON candidates'},
  q2DefaultSmoke:{path:'exp/q2/final/smoke-upload.txt',sha256:digest('exp/q2/final/smoke-upload.txt'),passed:2,N:2},
  q2DefaultCpu:{N:3,maxM:31.4,paths:['exp/q2/final/v18-trophy.log','exp/q2/final/v18-big_empty.log','exp/q2/final/v18-gen_M_07.log']}};
const f=t.freshness.aggregates;
t.freshness.phaseSummary={};
for(const v of variants){const F=gs(v).flatMap(g=>g.feeds);const active=F.filter(x=>x.queenAlive&&x.freshness.freshQueenNews&&(v!=='q18b2'||x.r>=430));
  t.freshness.phaseSummary[v]={activeFreshN:active.length,activeFreshToQueen:active.filter(x=>x.toQueen).length,lateAliveN:F.filter(x=>x.queenAlive&&x.r>=430).length,
    lateFreshN:F.filter(x=>x.queenAlive&&x.r>=430&&x.freshness.freshQueenNews).length,
    afterDeathN:F.filter(x=>!x.queenAlive).length,afterDeathToNonQueen:F.filter(x=>!x.queenAlive&&!x.toQueen).length,
    afterDeathFresh: F.filter(x=>!x.queenAlive&&x.freshness.freshQueenNews).map(x=>({r:x.r,donor:x.donor,K:x.K,qTag:x.qTag,newsAge:x.freshness.newsAge})),
    lateNonQueenKeys:[...new Set(gs(v).filter(g=>g.feeds.some(x=>x.queenAlive&&x.r>=430&&!x.toQueen)).map(g=>g.key))],
    jitGames:gs(v).filter(g=>g.feeds.some(x=>x.qTag&&x.kind==='feed')).map(g=>g.key)};
}
t.criteria=[];
const add=(id,variant,criterion,value,N,status,note='')=>t.criteria.push({id,variant,criterion,value,N,status,note});
add('Q1.5.1','q18','fresh queen recipient >=95%',{queen:f.q18.freshToQueen,feeds:f.q18.freshAlive},f.q18.freshAlive,'PASS');
add('Q1.5.2','q18','late non-queen feeds while queen alive =0',f.q18.lateNonQueen.length,f.q18.lateWhileAlive,'FAIL','All 32 are processes without fresh queen news; the literal zero criterion still fails.');
add('Q1.5.3','q18','report queen-eaten feed drops',t.q1.q18.all.feeds.queenDrops,t.q1.q18.all.feeds.queenDrops.drops,'PASS','Reporting criterion; no numeric eating threshold registered for Q1.');
for(const v of ['q18','q18b2']){
  const a=t.q1[v].all,p=t.actualPaired.allAlive400;
  add('Q1.5.4',v,'queen growth after r340 > base',{base:p.variants.v18.growth340to400,candidate:p.variants[v].growth340to400},p.N,p.variants[v].growth340to400>p.variants.v18.growth340to400?'PASS':'FAIL');
  add('Q1.5.6-pre300',v,'identical before r300',t.identities[v+'_vs_v18'].N-t.identities[v+'_vs_v18'].before300.length,t.identities[v+'_vs_v18'].N,'PASS');
  add('Q1.5.6-dead',v,'queen dead before r280: identical to end',119,120,'FAIL','big_empty A seed1; queen death r76, first action differences r414/r386, depth d7 vs d6.');
  add('Q1.5.7-cpu',v,'max CPU <80M',a.cpu.maxM,a.cpu.gamesMeasured,a.cpu.maxM<80?'PASS':'FAIL');
  add('Q1.5.7-errors',v,'retained games error/fault=0',a.faults.length,158,'PASS','3 historical rows failed in v18/q18b2 king sets; all replaced by clean records.');
  add('Q1.5.7-upload',v,'ON candidate upload clone 2/2',null,0,'NOT_TESTED','Existing merged v1.8 smoke is OFF, 2/2. No games run in this analysis.');
}
add('Q1.5.6-off','off','Q1 OFF = base',4,4,'PASS');add('Q1.5.6-mergedoff','mergedOff','both switches OFF = base',6,6,'PASS');
add('Q1B.9.2.1-queen','q18b2','early queen recipient must be global longest',{longest:190,queenFeeds:261},261,'FAIL','This is a strict global-state reading; v1.7 chooses among local evidence and base already has 79 exceptions.');
const p=t.actualPaired.b2Alive430;
add('Q1B.9.2.1-backup','q18b2','backup curve >=Q1',{q1:p.variants.q18.backup,b2:p.variants.q18b2.backup},p.N,
  [300,350,400,430].every(r=>p.variants.q18b2.backup[r]>=p.variants.q18.backup[r])?'PASS':'FAIL');
add('Q1B.9.2.2-alive','q18b2','Q feeds only living queen',{living:59,total:59},59,'PASS');
add('Q1B.9.2.2-slack','q18b2','FE Q slack in [6,26]',[6,26],42,'PASS');
add('Q1B.9.2.2-drops','q18b2','JIT queen eats >=50%',{queen:116,drops:238},238,'FAIL','48.7395%, not rounded up to 50%; 42 sacrifices in multiple games.');
add('Q1B.9.2.3','q18b2','ally-body traps after r300 <=base',{base:0,q1:3,b2:0},158,'PASS');
add('Q1B.9.2.4','q18b2','after queen death Q feeds=0',0,t.q1.q18b2.all.feeds.afterQueenDeath,'PASS','Ordinary feeds continue; 11 have stale-but-fresh<=20 queen memory and no Q tag.');
add('Q1B.9.2.5-boff','q18b2','B OFF = independent Q1 build',null,0,'NOT_TESTED','q18 is the B-OFF treatment control, not a duplicate independent identity run. Old v1.7-based check was 4/4.');
add('Q1B.11.1','q18b2','queen own feed indicator=0',0,158,'PASS','Already zero under base Q2a, so incremental no-feed effect is not isolated.');
add('Q1B.11.2','q18b2','b2 vs b1 first difference follows queen first feed',null,0,'NOT_TESTED','No b1 set on v1.8; old v1.7 result is not counted as this rerun.');
add('Q1B-late','q18b2','late non-queen feeds while queen alive =0',53,112,'FAIL','All 53 lack fresh queen news. Active fresh phase is 59/59 to queen.');
add('Q2-spec11-cand4','cand4-hunter2','seed2 survival stays at cand2 10/38 level',6,38,'FAIL','Registered wording has no formal uncertainty band; 6/38 does not reproduce 10/38.');
add('Q2-spec11-king','cand4-king','queen survival increases from recorded cand 0/35',{registeredBase:{alive:0,N:35},completeBase:{alive:2,N:38},candidate:{alive:4,N:38}},38,'PASS','cand6 is 8/38; final historical cand-king is 2/38, not 0/35.');
add('Q2k-survival','pooled','cand6 survival >cand4',{cand4:18,cand6:18},76,'FAIL','Matched map/opponent/side across seeds1/2, pooled game N76 each.');
add('Q2k-rammed','pooled','L>=4 rammed reduced',{cand4:30,cand6:25},76,'PASS','Includes recent splits. queendeath mutually exclusive while-L>=4 class is 29 vs25; Q2h/source changes confound Q2k attribution.');
add('Q2h-pocket','cand6','start-pocket result same as v17 seed1',12,12,'PASS','King and hunter seed1: queen death, longest, total, outcome match. No v17-hunter seed2 exists.');
add('Q2h-pocket-seed2','cand6-hunter2','start-pocket result same as v17 seed2',null,0,'NOT_TESTED');
add('Q2-cpu','spec11','candidate CPU <80M',null,0,'NOT_TESTED','No CPU fields/instructions in these replays. Current v1.8 default prior CPU max31.4M over3 games.');
add('Q2-errors','spec11','error/fault=0',0,176,'PASS');
add('Q2-off','off5/off6','OFF =v17',88,88,'PASS','44 keys per set; same keys repeated, not 88 independent map conditions.');
t.proposedDefaults={Q1_ON:true,Q1B_ON:true,Q2K_PACK_ON:false,Q2H_geometry_exemption:true,apply:'proposal only; bot/params unchanged',
  rationale:'Partial application: queen-directed transfers/growth move as intended; B removes observed ally traps and enforces living-queen/slack gates. JIT delivery, backup protection, and early-death identity remain failures. Q2k survival does not repeat across seeds and cand4/cand6 is confounded.'};
const compact=f=>({key:f.key,r:f.r,donor:f.donor,K:f.K,L:f.L,toQueen:f.toQueen,queenAlive:f.queenAlive,qTag:f.qTag,newsAge:f.freshness?.newsAge,drops:f.drops,byQ:f.byQ});
function prune(obj){if(!obj||typeof obj!=='object')return;for(const k of Object.keys(obj)){if(k==='lateNonQueenDetails')obj[k]=obj[k].map(compact);else prune(obj[k]);}}
prune(t.q1);prune(t.q2);
for(const a of Object.values(t.freshness.aggregates))for(const k of ['freshNonQueen','lateNonQueen','lateFreshNonQueen','postDeathFresh','afterDeathQTags'])a[k]=a[k].map(compact);
for(const[dir,a]of Object.entries(t.games))for(const g of a){
  g.feedDecisionCount=g.feedDecisions.length;
  g.unrealizedFeedDecisions=g.feedDecisions.filter(f=>!g.feeds.some(x=>x.r===f.r&&x.donor===f.donor)).map(compact);
  delete g.feedDecisions;
  if(dir.startsWith('exp/q2/'))delete g.feeds;
}
t.metadata.checkpointClarification='actualCheckpoints/actualPaired exclude early terminal games and require death round>checkpoint. Original aggregates carry surviving early terminals and use round-start alive>=checkpoint. Use actual* for pre-registered growth criteria.';
t.metadata.createdLocal=cpDate();
function cpDate(){return require('child_process').execFileSync('date',['+%Y-%m-%d %H:%M:%S %Z']).toString().trim();}
fs.writeFileSync(file,JSON.stringify(t,null,2)+'\n');
const log=path.join(__dirname,'extract.log');fs.writeFileSync(log,fs.readFileSync(log,'utf8').replace(/\0/g,''));
console.log('refined',t.actualPaired,t.criteria.map(c=>({id:c.id,variant:c.variant,N:c.N,status:c.status})));
