'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process'),assert=require('assert/strict');
const ROOT=path.resolve(__dirname,'../..'),file=path.join(__dirname,'tables.json'),t=JSON.parse(fs.readFileSync(file,'utf8'));
const checks=[],ok=(name,fn)=>{fn();checks.push(name);};
ok('Q1 474 clean rows, spec11 176, no missing replays',()=>{
  assert.equal(Object.entries(t.games).filter(([d])=>/\/(v18|q18|q18b2)-(king|hunter|gen)$/.test(d)).reduce((s,[d,g])=>s+g.length,0),474);
  assert.equal(['cand4-king','cand6-king','cand4-hunter2','cand6-hunter2'].reduce((s,k)=>s+t.games['exp/q2/'+k].length,0),176);
  assert(t.audit.every(a=>a.missingReplays.length===0));
});
ok('all retained row results match replay results and reconstruction',()=>{
  for(const a of t.audit){const rows=fs.readFileSync(path.join(ROOT,a.dir,'rows.jsonl'),'utf8').split('\n').filter(Boolean).map(JSON.parse);
    for(const g of t.games[a.dir]){const idx=a.selected.find(x=>x.key===g.key).line-1,r=rows[idx],res=g.result['team'+g.side];
      assert.equal(r.exit,0);assert(!r.error&&!r.botProblem);assert.equal(r.G,res.dragonCount?res.longestDragon:0);
      assert.equal(r.total,res.totalLength);assert.equal(r.units,res.dragonCount);assert.equal(r.won,g.result.winner===g.side);
      assert(Object.values(g.checks).every(n=>n===0));
    }
  }
});
ok('all replay and source SHA256 unchanged',()=>{
  const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,f))).digest('hex');
  for(const a of Object.values(t.games))for(const g of a)assert.equal(sha(g.file),g.replaySha256);
  for(const[f,hash]of Object.entries(t.metadata.sources))assert.equal(sha(f),hash);
});
ok('Q1 existing qmech feed/drop/trap/crowd values agree exactly',()=>{
  for(const v of ['v18','q18','q18b2']){const text=fs.readFileSync(path.join(__dirname,'verify-qmech-'+v+'.md'),'utf8'),a=t.q1[v].all;
    const m=/labelled feeds from r300: (\d+).*while the queen was alive (\d+), of which to the queen (\d+)/.exec(text);
    assert.deepEqual(m.slice(1).map(Number),[a.feeds.N,a.feeds.alive,a.feeds.toQueen]);
    const d=/drops of feeds to the queen: (\d+); eaten by the queen (\d+).*another of ours (\d+), the enemy (\d+)/.exec(text);
    assert.deepEqual(d.slice(1).map(Number),[a.feeds.queenDrops.drops,a.feeds.queenDrops.queen,a.feeds.queenDrops.ownOther,a.feeds.queenDrops.enemy]);
    const n=/late feeds \(r >= 430\).*: (\d+)/.exec(text);assert.equal(+n[1],a.feeds.lateNonQueenAlive);
    assert.equal(+( /trap\/a (\d+)/.exec(text)?.[1]||0),a.trapAllyAfter300);
    const crowd=/median (\d+), share of samples with >= 2: .* \(n(\d+)\)/.exec(text);
    assert.equal(+crowd[1],a.crowd.median);assert.equal(+crowd[2],a.crowd.N);
  }
});
ok('Q2 existing queenstat survival/death median and queendeath all classes agree',()=>{
  const text=fs.readFileSync(path.join(__dirname,'verify-queenstat.txt'),'utf8');
  for(const block of text.split('== ').filter(Boolean)){const name=/exp\/q2\/([^:]+):/.exec(block)[1],a=t.q2.sets[name].nonPocket;
    const m=/our queen:\s+alive at the end (\d+)\/(\d+);.*median round (\d+)/.exec(block);
    assert.deepEqual(m.slice(1).map(Number),[a.alive[500],a.N,a.deathRoundMedian]);
  }
  for(const line of fs.readFileSync(path.join(__dirname,'verify-queendeath.txt'),'utf8').trim().split('\n')){
    const i=line.indexOf(': '),name=line.slice(0,i),p=Object.fromEntries(line.slice(i+2).split(', ').map(s=>{const m=/^(.*) (\d+)$/.exec(s);return[m[1],+m[2]];}));
    assert.deepEqual(p,t.q2.sets[name].nonPocket.precursors);
  }
});
ok('freshness phases, all realized feeds, drop conservation, no queen feed',()=>{
  for(const v of ['v18','q18','q18b2'])for(const s of ['king','hunter','gen'])for(const g of t.games['exp/v16/q1/'+v+'-'+s]){
    assert.equal(g.feedDecisionCount,g.feeds.length);assert.equal(g.unrealizedFeedDecisions.length,0);
    for(const f of g.feeds){assert(f.freshness);assert.equal(f.drops,Math.ceil(f.L/2));assert(f.byQ+f.byOwn+f.byEnemy<=f.drops);assert.notEqual(f.donor,g.Q);}
  }
  assert.equal(t.freshness.aggregates.q18.freshAlive,380);assert.equal(t.freshness.aggregates.q18.freshToQueen,380);
  assert.equal(t.freshness.phaseSummary.q18b2.activeFreshN,59);assert.equal(t.freshness.phaseSummary.q18b2.activeFreshToQueen,59);
  assert.equal(t.freshness.aggregates.q18.lateFreshNonQueen.length,0);assert.equal(t.freshness.aggregates.q18b2.lateFreshNonQueen.length,0);
  assert.equal(t.freshness.reconstructionErrors.length,0);
});
ok('matched actual growth and pooled keys have correct eligibility',()=>{
  const map=v=>new Map(['king','hunter','gen'].flatMap(s=>t.games['exp/v16/q1/'+v+'-'+s]).map(g=>[g.key,g]));
  for(const v of ['v18','q18','q18b2'])for(const k of t.actualPaired.allAlive400.keys){const g=map(v).get(k);assert(g.rounds>400&&(!g.qDeath||g.qDeath.r>400));}
  for(const v of ['cand4','cand6']){
    const a=t.games['exp/q2/'+v+'-hunter'],b=t.games['exp/q2/'+v+'-hunter2'],norm=g=>[g.opp,g.map,g.side].join(':');
    assert.deepEqual(a.map(norm).sort(),b.map(norm).sort());assert.equal(t.q2.pooled[v].nonPocket.N,76);assert.equal(t.q2.pooled[v].nonPocket.alive[500],18);
  }
});
ok('pocket seed1 results match v17 for cand6 and current default, seed2 comparison absent',()=>{
  let same=0,defaultSame=0;
  for(const r of t.q2.pockets.filter(r=>['cand6-king','cand6-hunter'].includes(r.set))){const a=r.candidate,b=r.v17SameSeed;
    for(const k of ['queenDeath','queenEnd','longest','total','won'])assert.equal(a[k],b[k]);same++;
    const g=t.games['exp/v16/q1/v18-'+r.set.split('-')[1]].find(g=>g.key===a.key);assert.equal(g.qDeath.r,b.queenDeath);assert.equal(g.endLongest,b.longest);assert.equal(g.endTotal,b.total);assert.equal(g.won,b.won);defaultSame++;
  }
  assert.equal(same,12);assert.equal(defaultSame,12);
  assert(t.q2.pockets.filter(r=>r.set.endsWith('hunter2')).every(r=>r.v17SameSeed===null));
});
ok('existing fingerprint tool confirms all10 Q1 OFF comparisons without running games',()=>{
  const refs=['king','hunter','gen'].flatMap(s=>t.games['exp/v16/q1/v18-'+s]);
  const pairs=['q18off-id','v18q1off-id'].flatMap(s=>t.games['exp/v16/q1/'+s]).map(g=>[g,refs.find(h=>h.key===g.key)]);
  const files=pairs.flatMap(p=>p.map(g=>g.file));
  const raw=cp.execFileSync(process.execPath,['tools/fingerprint.js',...files],{cwd:ROOT,env:{...process.env,UNSW_RULES:'123'},maxBuffer:2**22}).toString();
  fs.writeFileSync(path.join(__dirname,'verify-fingerprint.txt'),raw);
  const lines=raw.trim().split('\n');assert.equal(lines.length,20);
  for(let i=0;i<lines.length;i+=2)assert.equal(lines[i].split(' ')[0],lines[i+1].split(' ')[0]);
});
ok('report three pictures exist and PNG snapshots are complete',()=>{
  const report=fs.readFileSync(path.join(ROOT,'versions/v1.8/ANALYSIS-1002.md'),'utf8'),imgs=[...report.matchAll(/!\[[^\]]*\]\(([^)]+)\)/g)];assert.equal(imgs.length,3);
  for(const m of imgs){const f=path.resolve(ROOT,'versions/v1.8',m[1]),b=fs.readFileSync(f);assert.equal(b.subarray(0,8).toString('hex'),'89504e470d0a1a0a');}
  for(const b of JSON.parse(fs.readFileSync(path.join(__dirname,'boards/manifest.json'),'utf8')))assert.deepEqual(b.rounds,b.actualSnapshots);
});
ok('registered failures are not hidden or rounded into pass',()=>{
  assert.equal(t.criteria.find(c=>c.id==='Q1B.9.2.2-drops').status,'FAIL');assert(116/238<0.5);
  assert.equal(t.criteria.filter(c=>c.id==='Q1.5.6-dead'&&c.status==='FAIL').length,2);
  assert.equal(t.earlyQueenGlobalLongest.globalLongest,190);assert.equal(t.earlyQueenGlobalLongest.events,261);
  assert.equal(t.criteria.find(c=>c.id==='Q1B.9.2.1-backup').status,'FAIL');
});
const result={createdLocal:cp.execFileSync('date',['+%Y-%m-%d %H:%M:%S %Z']).toString().trim(),passed:checks.length,checks,failed:0};
fs.writeFileSync(path.join(__dirname,'qa.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
