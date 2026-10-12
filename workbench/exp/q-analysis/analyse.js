'use strict';
process.env.UNSW_RULES = '123';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '../..');
const { makeLoader, viewerSource } = require('../../tools/top_features');
const ML = require('../../tools/mass_ledger');
const load = makeLoader(viewerSource());
const CP = [50, 100, 250, 300, 340, 350, 400, 430, 450, 500];
const pocket = m => /autarky|dilemma|slithery/i.test(m);
const med = a => a.length ? [...a].sort((a,b) => a-b)[a.length >> 1] : null;
const sum = (a, f) => a.reduce((s,x) => s+f(x), 0);
const hist = a => a.reduce((o,x) => (o[x] = (o[x] || 0)+1, o), {});
const sha = x => crypto.createHash('sha256').update(x).digest('hex');
function inventory(dir) {
  const lines = fs.readFileSync(path.join(ROOT, dir, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean);
  const latest = new Map(), bad = [], counts = {}, invalid = [];
  lines.forEach((s,i) => {
    let r; try { r = JSON.parse(s); } catch(e) { invalid.push({line:i+1,error:e.message}); return; }
    counts[r.key] = (counts[r.key] || 0)+1;
    if (r.exit !== 0 || r.G === undefined || r.error || r.botProblem) bad.push({line:i+1,...r});
    else latest.set(r.key, {...r,sourceLine:i+1});
  });
  const rows = [...latest.values()].sort((a,b) => a.key.localeCompare(b.key));
  return {rows, audit:{dir,rawLines:lines.length,cleanKeys:rows.length,invalidLines:invalid,badRows:bad,
    repeatedKeys:Object.entries(counts).filter(([,n])=>n>1),missingReplays:[],selected:rows.map(r=>({key:r.key,line:r.sourceLine}))}};
}
function hashes(R) {
  const h = new Map(); let r = -1;
  for (const e of R.events) {
    if (e.type === 'roundStart') r = e.round;
    if (['dragonIndicator','dragonLog','debugDraw','engineLog'].includes(e.type)) continue;
    const o = Object.fromEntries(Object.entries(e).filter(([k]) => k !== 'instructions'));
    if (!h.has(r)) h.set(r,crypto.createHash('sha256'));
    h.get(r).update(JSON.stringify(o,(_,v)=>typeof v==='bigint'?String(v):v)+'\n');
  }
  return [...h].map(([r,x])=>[r,x.digest('hex')]);
}
function analyse(dir,row) {
  const file = path.join(dir,'games',row.key.replace(/:/g,'_'),'game.replay');
  const R = load(path.join(ROOT,file)), us = row.side;
  const Q = Math.min(...R.match.map.initialDragons.filter(d=>d.team===us).map(d=>d.id));
  const EQ = Math.min(...R.match.map.initialDragons.filter(d=>d.team!==us).map(d=>d.id));
  const g = {dir,file,key:row.key,map:row.map,side:us,seed:row.seed,opp:path.basename(row.opp),pocket:pocket(row.map),Q,EQ,
    qLen:{},backup:{},qDeath:null,enemyDeath:null,qEnd:0,endLongest:0,endTotal:0,won:row.won,
    feeds:[],feedDecisions:[],qEat:{feed:0,otherDeath:0,natural:0},crowd:[],tags:{},faults:[],cpu:[],hashes:hashes(R),
    result:R.result,replaySha256:sha(fs.readFileSync(path.join(ROOT,file)))};
  const last = new Map(), byDeath = new Map(); let lastSplit = null, lastRound = -1;
  function feed(e,r,c) {
    const m = /^feed #(\d+) d(\d+) L(\d+)(.*)$/.exec(e.text || ''); if(!m)return null;
    const d = c.drag.get(e.id); if(!d || d.team!==us)return null;
    const others = [...c.drag.values()].filter(o=>o.team===us&&o.id!==d.id).sort((a,b)=>b.body.length-a.body.length||a.id-b.id);
    const q = c.drag.get(Q);
    return {r,donor:e.id,head:{...d.body[0]},L:+m[3],d:+m[2],K:+m[1],toQueen:+m[1]===Q,
      queenAlive:!!q,kLongest:others[0]?.id===+m[1],qTag:/ Q(\s|$)/.test(m[4]),text:e.text,
      kind:/ cv2/.test(m[4])?'cv2':/ conv/.test(m[4])?'conv':'feed',slack:500-r-(+m[2]+ +m[3]),
      enemyWithin3:q?[...c.drag.values()].filter(o=>o.team!==us&&c.tdist(o.body[0],q.body[0])<=3).map(o=>o.id):[],
      drops:0,byQ:0,byOwn:0,byEnemy:0,byTarget:0,eats:[]};
  }
  const res = ML.perGame(R,{map:row.map,variant:'?',rules:'123'}, {
    turn(d,r,c) {
      if(r!==lastRound) {
        lastRound=r;
        if(CP.includes(r)) {
          g.qLen[r]=c.drag.get(Q)?.body.length || 0;
          g.backup[r]=Math.max(0,...[...c.drag.values()].filter(o=>o.team===us&&o.id!==Q).map(o=>o.body.length));
        }
      }
      if(d.id===Q&&r>=340&&r<=480&&r%10===0)g.crowd.push({r,n:[...c.drag.values()].filter(o=>o.team===us&&o.id!==Q&&c.tdist(o.body[0],d.body[0])<=2).length});
    },
    indicator(e,r,c) {
      last.set(e.id,{r,text:e.text||''});
      const d=c.drag.get(e.id); if(!d||d.team!==us)return;
      for(const tag of ['qs','qd','qk','qb','qw','qg','qp','g','gh'])if(new RegExp('(^| )'+tag+'[0-9]*( |$)').test(e.text||''))g.tags[tag]=(g.tags[tag]||0)+1;
      if(r>=300){const f=feed(e,r,c);if(f)g.feedDecisions.push(f);}
    },
    split(p,ch,e,r) {
      if(p.id===Q)lastSplit={r,kind:(last.get(Q)?.text.split(' ')[0]||'?').replace(/[0-9]+$/,'')};
    },
    death(d,rec,idx,other,r,c) {
      const li=last.get(d.id),recent=lastSplit&&r-lastSplit.r<=5;
      if(d.id===Q)g.qDeath={r,cause:ML.CAUSE[rec.cause],blk:rec.blk,allyBlock:d.allyBlock,enemyBlock:d.enemyBlock,
        L:d.body.length,head:{...d.body[0]},lastIndicator:li,split:recent?lastSplit:null,
        precursor:ML.CAUSE[rec.cause]+(recent?' after '+lastSplit.kind:d.body.length<=3?' while L<=3':' while L>=4'),
        other:other?{id:other.id,L:other.body.length,team:other.team}:null};
      if(d.id===EQ)g.enemyDeath={r,cause:ML.CAUSE[rec.cause],otherTeam:other?.team};
      if(rec.cause===6)g.faults.push({r,id:d.id,team:d.team});
      if(d.team!==us||r<300)return;
      const f=g.feedDecisions.findLast(x=>x.donor===d.id&&x.r===r);
      if(!f)return;
      f.drops=rec.drops;f.deathCause=ML.CAUSE[rec.cause];g.feeds.push(f);byDeath.set(idx,f);
    },
    eat(d,k,o,r,c) {
      if(d.id===Q&&r>=300)g.qEat[o<0?'natural':byDeath.has(o)?'feed':'otherDeath']++;
      const f=byDeath.get(o);if(!f)return;
      if(d.id===f.K)f.byTarget++;
      if(d.team!==us)f.byEnemy++;else if(d.id===Q)f.byQ++;else f.byOwn++;
      f.eats.push({r,id:d.id,x:k%c.W,y:Math.floor(k/c.W)});
    },
    end(n,c) {
      g.rounds=n;g.qEnd=c.drag.get(Q)?.body.length||0;
      for(const d of c.drag.values())if(d.team===us){g.endTotal+=d.body.length;g.endLongest=Math.max(g.endLongest,d.body.length);}
      for(const r of CP)if(g.qLen[r]===undefined)g.qLen[r]=g.qEnd;
      g.qLen[500]=g.qEnd;
    }
  });
  g.checks=res.chk;
  for(const s of row.cpu||[]) {
    const m=/team ([AB]) points per turn:.*max ([0-9.]+)M.*\((\d+) turns\)/.exec(s);
    if(m&&m[1]===us)g.cpu.push({maxM:+m[2],turns:+m[3],raw:s});
  }
  return g;
}
function aggregate(gs) {
  const F=gs.flatMap(g=>g.feeds), A=F.filter(f=>f.queenAlive), Q=A.filter(f=>f.toQueen), tag=F.filter(f=>f.qTag);
  const jit=tag.filter(f=>f.r>=430&&f.kind==='feed'), early=A.filter(f=>f.toQueen&&f.r<430);
  const drops = a=>({events:a.length,drops:sum(a,f=>f.drops),queen:sum(a,f=>f.byQ),ownOther:sum(a,f=>f.byOwn),enemy:sum(a,f=>f.byEnemy),target:sum(a,f=>f.byTarget),
    uneaten:sum(a,f=>f.drops-f.byQ-f.byOwn-f.byEnemy)});
  const crowds=gs.flatMap(g=>g.crowd.map(c=>c.n));
  const deaths=gs.filter(g=>g.qDeath), after=deaths.filter(g=>g.qDeath.r>=300);
  const alive=r=>gs.filter(g=>r===500?g.qEnd>0:!g.qDeath||g.qDeath.r>=r);
  const g430=alive(430);
  return {N:gs.length,alive:Object.fromEntries(CP.map(r=>[r,alive(r).length])),deaths:hist(deaths.map(g=>g.qDeath.cause)),
    precursors:hist(deaths.map(g=>g.qDeath.precursor)),deathRoundMedian:med(deaths.map(g=>g.qDeath.r)),
    rammedLge4:deaths.filter(g=>g.qDeath.cause==='rammed'&&g.qDeath.L>=4).length,
    rammedLge4WithoutRecentSplit:deaths.filter(g=>g.qDeath.cause==='rammed'&&g.qDeath.L>=4&&!g.qDeath.split).length,
    qLengthAlive:Object.fromEntries(CP.map(r=>[r,{median:med(alive(r).map(g=>g.qLen[r])),N:alive(r).length}])),
    qLengthAll:Object.fromEntries(CP.map(r=>[r,{median:med(gs.map(g=>g.qLen[r])),N:gs.length}])),
    feeds:{N:F.length,alive:A.length,toQueen:Q.length,lateNonQueenAlive:A.filter(f=>f.r>=430&&!f.toQueen).length,
      lateNonQueenDetails:gs.flatMap(g=>g.feeds.filter(f=>f.r>=430&&f.queenAlive&&!f.toQueen).map(f=>({key:g.key,...f}))),
      queenDrops:drops(Q),allDrops:drops(F),earlyQueen:early.length,earlyQueenNotLongest:early.filter(f=>!f.kLongest).length,
      qTagged:tag.length,qTaggedQueenDead:tag.filter(f=>!f.queenAlive).length,qTaggedWrongTarget:tag.filter(f=>!f.toQueen).length,
      jit:{...drops(jit),queenDead:jit.filter(f=>!f.queenAlive).length,slack:jit.length?[Math.min(...jit.map(f=>f.slack)),Math.max(...jit.map(f=>f.slack))]:null,
        enemyWithin3:jit.filter(f=>f.enemyWithin3.length).length},
      afterQueenDeath:F.filter(f=>!f.queenAlive).length,afterDeathToNonQueen:F.filter(f=>!f.queenAlive&&!f.toQueen).length,
      afterDeathGlobalLongest:F.filter(f=>!f.queenAlive&&f.kLongest).length},
    queenFeedDecisions:sum(gs,g=>g.feedDecisions.filter(f=>f.donor===g.Q).length),
    trapAllyAfter300:after.filter(g=>g.qDeath.cause==='trap'&&g.qDeath.blk==='a').length,
    trapAnyAllyAfter300:after.filter(g=>g.qDeath.cause==='trap'&&g.qDeath.allyBlock).length,
    trapAfter300N:after.filter(g=>g.qDeath.cause==='trap').length,
    crowd:{median:med(crowds),ge2:crowds.filter(n=>n>=2).length,N:crowds.length},
    backupAtQueen430:Object.fromEntries([300,350,400,430].map(r=>[r,{median:med(g430.map(g=>g.backup[r]||0)),N:g430.length}])),
    cpu:{gamesMeasured:gs.filter(g=>g.cpu.length).length,maxM:gs.some(g=>g.cpu.length)?Math.max(...gs.flatMap(g=>g.cpu.map(c=>c.maxM))):null,turns:sum(gs,g=>sum(g.cpu,c=>c.turns))},
    faults:gs.flatMap(g=>g.faults),checks:Object.fromEntries(Object.keys(gs[0]?.checks||{}).map(k=>[k,sum(gs,g=>g.checks[k])])),
    enemyQueensKilled:gs.filter(g=>g.enemyDeath?.otherTeam===g.side).length,tags:gs.reduce((o,g)=>{for(const[k,v]of Object.entries(g.tags))o[k]=(o[k]||0)+v;return o;},{}),
    qEat:gs.reduce((o,g)=>{for(const k of Object.keys(o))o[k]+=g.qEat[k];return o;},{feed:0,otherDeath:0,natural:0})};
}
function identity(a,b) {
  const bm=new Map(b.map(g=>[g.key,g]));const out=[];
  for(const g of a){const base=bm.get(g.key);if(!base)continue;const ah=new Map(g.hashes),bh=new Map(base.hashes);
    const rounds=[...new Set([...ah.keys(),...bh.keys()])].sort((a,b)=>a-b);
    const first=rounds.find(r=>ah.get(r)!==bh.get(r))??null;
    out.push({key:g.key,firstDifference:first,baseQueenDeath:base.qDeath?.r??null,same:first===null});
  }
  const early=out.filter(x=>x.baseQueenDeath!==null&&x.baseQueenDeath<280);
  return {N:out.length,same:out.filter(x=>x.same).length,before300:out.filter(x=>x.firstDifference!==null&&x.firstDifference<300),
    earlyQueenDeathN:early.length,earlyQueenDeathDifferences:early.filter(x=>!x.same),rows:out};
}
const groups={};const audit=[];
const dirs=[...['v18','q18','q18b2'].flatMap(v=>['king','hunter','gen'].map(s=>'exp/v16/q1/'+v+'-'+s)),
  'exp/v16/q1/q18off-id','exp/v16/q1/v18q1off-id',
  ...['cand4-king','cand6-king','cand4-hunter2','cand6-hunter2','cand4-hunter','cand6-hunter','v17-king','v17x-king','v17-hunter','cand-king','cand2-hunter','off5-king','off6-king'].map(s=>'exp/q2/'+s)];
for(const dir of dirs){const inv=inventory(dir);audit.push(inv.audit);const gs=[];
  for(const row of inv.rows){const f=path.join(ROOT,dir,'games',row.key.replace(/:/g,'_'),'game.replay');
    if(!fs.existsSync(f)){inv.audit.missingReplays.push(row.key);continue;}
    gs.push(analyse(dir,row));
  }
  groups[dir]=gs;console.log(dir,gs.length,'done');
}
const a={};for(const v of ['v18','q18','q18b2'])a[v]=['king','hunter','gen'].flatMap(s=>groups['exp/v16/q1/'+v+'-'+s]);
const q1={};for(const[v,gs]of Object.entries(a))q1[v]={all:aggregate(gs),strata:Object.fromEntries(['king','hunter','gen'].map(s=>[s,aggregate(groups['exp/v16/q1/'+v+'-'+s])]))};
const identities={q18_vs_v18:identity(a.q18,a.v18),q18b2_vs_v18:identity(a.q18b2,a.v18),off_vs_v18:identity(groups['exp/v16/q1/q18off-id'],a.v18),mergedOff_vs_v18:identity(groups['exp/v16/q1/v18q1off-id'],a.v18)};
const maps=Object.fromEntries(Object.entries(a).map(([v,gs])=>[v,new Map(gs.map(g=>[g.key,g]))]));
const paired={};
for(const cohort of ['queen400All','queen430All','baseQueen300']){
  const r=cohort==='queen400All'?400:cohort==='queen430All'?430:300;
  const keys=a.v18.filter(g=>cohort==='baseQueen300'?g.qLen[r]>0:['v18','q18','q18b2'].every(v=>maps[v].get(g.key)?.qLen[r]>0)).map(g=>g.key);
  paired[cohort]={N:keys.length,keys,variants:{}};
  for(const v of ['v18','q18','q18b2']){const gs=keys.map(k=>maps[v].get(k));paired[cohort].variants[v]={
    qLength:Object.fromEntries([300,340,350,400,430,450,500].map(r=>[r,med(gs.map(g=>g.qLen[r]))])),
    backup:Object.fromEntries([300,350,400,430].map(r=>[r,med(gs.map(g=>g.backup[r]||0))])),
    growth340to400:med(gs.map(g=>g.qLen[400]-g.qLen[340])),
    feedPearls:sum(gs,g=>g.qEat.feed),alive500:gs.filter(g=>g.qEnd>0).length};}
  paired[cohort].rows=keys.map(key=>({key,...Object.fromEntries(['v18','q18','q18b2'].map(v=>[v,{qLen:maps[v].get(key).qLen,backup:maps[v].get(key).backup,qFeedPearls:maps[v].get(key).qEat.feed}]))}));
}
const q2={sets:{},pooled:{},comparisons:{},pockets:[]};
for(const[dir,gs]of Object.entries(groups))if(dir.startsWith('exp/q2/'))q2.sets[path.basename(dir)]={all:aggregate(gs),nonPocket:aggregate(gs.filter(g=>!g.pocket)),pocket:aggregate(gs.filter(g=>g.pocket))};
for(const v of ['cand4','cand6']){
  const s1=groups['exp/q2/'+v+'-hunter'],s2=groups['exp/q2/'+v+'-hunter2'];
  const norm=g=>[g.opp,g.map,g.side].join(':');const k2=new Set(s2.map(norm));const k1=new Set(s1.map(norm));
  const gs=[...s1.filter(g=>k2.has(norm(g))),...s2.filter(g=>k1.has(norm(g)))];
  q2.pooled[v]={matchedMapSideKeys:k1.size,all:aggregate(gs),nonPocket:aggregate(gs.filter(g=>!g.pocket))};
}
for(const suffix of ['king','hunter','hunter2']){
  const s4=groups['exp/q2/cand4-'+suffix].filter(g=>!g.pocket),s6=new Map(groups['exp/q2/cand6-'+suffix].map(g=>[g.key,g]));
  q2.comparisons[suffix]={N:s4.length,bothAlive:0,onlyCand4Alive:0,onlyCand6Alive:0,bothDead:0,rows:[]};
  for(const g of s4){const h=s6.get(g.key);if(!h)continue;const k=g.qEnd>0?(h.qEnd>0?'bothAlive':'onlyCand4Alive'):(h.qEnd>0?'onlyCand6Alive':'bothDead');q2.comparisons[suffix][k]++;q2.comparisons[suffix].rows.push({key:g.key,cand4Death:g.qDeath,cand6Death:h.qDeath});}
}
const v17king=[...groups['exp/q2/v17-king'],...groups['exp/q2/v17x-king']];
const unique17=[...new Map(v17king.map(g=>[g.key,g])).values()];
identities.off5_vs_v17=identity(groups['exp/q2/off5-king'],unique17);
identities.off6_vs_v17=identity(groups['exp/q2/off6-king'],unique17);
for(const dir of ['exp/q2/cand4-king','exp/q2/cand6-king','exp/q2/cand4-hunter','exp/q2/cand6-hunter','exp/q2/cand4-hunter2','exp/q2/cand6-hunter2']){
  const ref=dir.endsWith('king')?unique17:groups['exp/q2/v17-hunter'];
  for(const g of groups[dir].filter(g=>g.pocket)){
    const baseline=ref.find(h=>h.map===g.map&&h.side===g.side&&h.seed===g.seed);
    const seed1ref=ref.find(h=>h.map===g.map&&h.side===g.side&&h.seed===1);
    const compact=g=>g?{key:g.key,seed:g.seed,queenDeath:g.qDeath?.r??null,queenEnd:g.qEnd,longest:g.endLongest,total:g.endTotal,won:g.won}:null;
    q2.pockets.push({set:path.basename(dir),candidate:compact(g),v17SameSeed:compact(baseline),v17Seed1Context:compact(seed1ref)});
  }
}
const sourceFiles=['versions/v1.8/VERSION.md','exp/v16/q1/Q1.md','exp/q2/bot-cand4/plan.cpp','exp/q2/bot-cand6/plan.cpp','tools/mass_ledger.js','tools/top_features.js'];
const out={metadata:{created:new Date().toISOString(),rules:'123',roundConvention:'Replay e.round, zero-based; r500=end. Queen alive at early terminal is carried to r500.',
  median:'upper middle (same as existing tools)',selection:'last clean row per key: exit=0, G present, no error or botProblem',
  identity:'all event fields except instructions, excluding dragonIndicator/dragonLog/debugDraw/engineLog; sonar included',
  sources:Object.fromEntries(sourceFiles.map(f=>[f,sha(fs.readFileSync(path.join(ROOT,f)))])),noGames:true,noNetwork:true},audit,q1,paired,q2,identities,
  games:Object.fromEntries(Object.entries(groups).map(([k,gs])=>[k,gs.map(({hashes,...g})=>g)]))};
fs.writeFileSync(path.join(__dirname,'tables.json'),JSON.stringify(out,null,2)+'\n');
console.log('tables written',path.join(__dirname,'tables.json'));
