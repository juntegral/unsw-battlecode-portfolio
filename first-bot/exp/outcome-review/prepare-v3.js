'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ML = require('../../tools/mass_ledger.js');
const OUT = '.cache/outcome-review';
const allow = process.argv.includes('--allow-inherited-10');
function resourceCheck() {
  const mem = cp.execFileSync('/usr/bin/memory_pressure', [], {encoding:'utf8'});
  const free = +(/System-wide memory free percentage:\s*(\d+)%/.exec(mem)||[])[1];
  const disk = cp.execFileSync('/bin/df',['-g','/'],{encoding:'utf8'}).trim().split('\n').at(-1).trim().split(/\s+/);
  if (!Number.isFinite(free) || free < 10 || +disk[3] < 20) throw Error('PAUSE resource threshold: '+free+'% / '+disk[3]+' GiB');
  if (!allow) throw Error('Heavy work awaits explicit acceptance of inherited niceness 10');
  return {freeMemoryPercent:free,freeDiskGiB:+disk[3],niceInvocation:false,coordinatorReportedParentNiceness:10,observedChildNiceness:require('os').getPriority(),workers:1,authorization:'Coordinator approved continuation without invoking nice; 2026-10-01'};
}
const resource=resourceCheck();
fs.mkdirSync(OUT,{recursive:true});
const waves=[['W0.1','cand-merge2-online',0,'merge2'],['W0.2','cand-merge2-online-r2',0,'merge2'],['W0.3','cand-merge2-online-r3',0,'merge2']];
for(let i=1;i<=12;i++) {if(i===7)waves.push(['W7','cand-stack6-online-r2',7,'stack6']);else waves.push(['W'+i,'cand-stack'+(i<=6?i:i-1)+'-online',i,'stack'+(i<=6?i:i-1)]);}
const historical=['baseline-r1','baseline-r1b','baseline-r1c','cand-avoid6-online','cand-portal1-online','cand-swarm8-online','base-px8-online','base-px9d-online','px-king-v2-online'];
const defs=[...waves.map(a=>({wave:a[0],set:a[1],waveOrder:a[2],bot:a[3],era:'waves'})),...historical.map(s=>({wave:s,set:s,waveOrder:null,bot:s.startsWith('baseline-')?'g4-r4':s,era:'history'}))];
const allowed=new Set([306,70,20,801,264,46,545]);
const games=[],sets=[],absent=[],seen=new Set(),cacheCheck={},egCheck={};
const readl=f=>fs.existsSync(f)?fs.readFileSync(f,'utf8').split('\n').filter(Boolean).map(JSON.parse):[];
const sum=(xs)=>xs.reduce((a,b)=>a+b,0);
const flow=(t,k,start=0,end=50)=>sum(t.fl[ML.FI[k]].slice(start,end));
for (const d of defs) {
  const dir='data/online/'+d.set,idxfile=dir+'/index.json';
  if(!fs.existsSync(idxfile)){absent.push(d);continue;}
  const idx=JSON.parse(fs.readFileSync(idxfile,'utf8')), ms=readl('.cache/mass-ledger/online-'+d.set+'.jsonl'), es=readl('.cache/endgame-king/online-'+d.set+'.jsonl');
  const mm=new Map(ms.map(x=>[x.key,x])), em=new Map(es.map(x=>[x.key,x]));
  if(mm.size!==ms.length || em.size!==es.length)throw Error('Duplicate cache keys '+d.set);
  const gameRows=idx.games||idx;
  const counts={};
  for(const g of gameRows) {
    if(!allowed.has(g.opponentTeam))throw Error('Unexpected opponent '+JSON.stringify(g));
    if(seen.has(g.gameId))throw Error('Repeated game ID '+g.gameId);seen.add(g.gameId);
    const key=d.set+':'+g.gameId, e=em.get(key); let m=mm.get(key);
    if(!m){
      resourceCheck();
      const R=require('../../tools/replay.js').load(dir+'/M'+g.gameId+'.replay');
      const variant=g.mapName==='Prisoners Dilemma'?(R.match.map.initialDragons.length===10?'PD10':'PD6'):null;
      m={...ML.perGame(R,{map:g.mapName,variant}),variant};
      console.log('fresh mass reconstruction '+key);
    }
    const j=JSON.parse(fs.readFileSync(dir+'/game-'+g.gameId+'.json','utf8')),res=j.replay.result;
    const us=g.ourSide.toUpperCase(),en=us==='A'?'B':'A', a=m[us],b=m[en];
    const rr=res['team'+us],sr=res['team'+en];
    for(const [k,v] of Object.entries(m.chk))cacheCheck[k]=(cacheCheck[k]||0)+v;
    if(e)for(const[k,v]of Object.entries(e.chk2))egCheck[k]=(egCheck[k]||0)+v;
    if(a.st.king[50]!==rr.longestDragon||b.st.king[50]!==sr.longestDragon)throw Error('Final mismatch '+key);
    if(m.winner!==(res.winner||null) || ((g.winner||'').toUpperCase()||null)!==(res.winner||null))throw Error('Winner mismatch '+key);
    const winner=res.winner||null;
    const r={...d,key,id:g.gameId,opponent:g.opponentTeam,opponentName:j['team'+en+'Name'],map:g.mapName,family:ML.R500.includes(g.mapName)?'r500':'elim',ourSide:us,seed:g.seed,file:dir+'/M'+g.gameId+'.replay',requestedAt:g.requestedAt,completedAt:g.completedAt,submission:g.ourSubmission,
      outcome:winner===us?'W':winner===en?'L':'D',ourEliminated:rr.dragonCount===0,theirEliminated:sr.dragonCount===0,ourFinal:rr.longestDragon,theirFinal:sr.longestDragon,ourFinalUnits:rr.dragonCount,theirFinalUnits:sr.dragonCount,rounds:m.rounds,endReason:res.endReason,
      width:m.W,height:m.H,fountains:m.fountTiles,territory:m.terrTiles,variant:e?.variant||m.variant||null,endgameCached:!!e};
    for(const [name,t]of[['our',a],['their',b]]) {
      r[name+'Trajectory']=t.st;
      for(const t0 of[10,50,100,250,300,400]){
        r[name+'Heads'+t0]=m.rounds>t0?t.st.units[t0/10]:null;
        r[name+'King'+t0]=m.rounds>t0?t.st.king[t0/10]:null;
        r[name+'AbsorbedHeads'+t0]=t.st.units[t0/10];
      }
      r[name+'Natural']=flow(t,'eat_nat');r[name+'Natural100']=flow(t,'eat_nat',0,10);
      r[name+'Sacrifices']=flow(t,'dn_sac');r[name+'Sacrifices300']=flow(t,'dn_sac',0,30);
      r[name+'SacrificesLate']=flow(t,'dn_sac',30,50);
      r[name+'Lineage300']=t.lin?.cp?.['300']?.Lt??null;
      r[name+'LineSac300']=t.lin?.cp?.['300']?.eat[1]??null;
      r[name+'LineNatural300']=t.lin?.cp?.['300']?.eat[0]??null;
      r[name+'LineOwnOther300']=t.lin?.cp?.['300']?sum(t.lin.cp['300'].eat.slice(2,6)):null;
      r[name+'LineEnemy300']=t.lin?.cp?.['300']?sum(t.lin.cp['300'].eat.slice(6)):null;
      r[name+'LineSprint300']=t.lin?.cp?.['300']?.cost??null;
      r[name+'LineSplit300']=t.lin?.cp?.['300']?(t.lin.cp['300'].lossOff+t.lin.cp['300'].lossPath):null;
      r[name+'KingDeathsLate']=flow(t,'kd_n',30,50);
      r[name+'KingDeathLengthLate']=flow(t,'kd_len',30,50);
      const eg=e?.[name==='our'?us:en];
      r[name+'Exposure']=eg&&sum(eg.env.map(x=>x[0]))?sum(eg.env.map(x=>x[2]))/sum(eg.env.map(x=>x[0])):null;
      r[name+'ExposureTurns']=eg?sum(eg.env.map(x=>x[0])):null;
      r[name+'KingDeaths']=eg?.kd??null;
      r[name+'Faults']=flow(t,'dn_fault');
    }
    r.naturalRatio=r.theirNatural?r.ourNatural/r.theirNatural:null;
    r.naturalRatio100=r.theirNatural100?r.ourNatural100/r.theirNatural100:null;
    r.finalRatio=r.theirFinal?r.ourFinal/r.theirFinal:null;
    r.eliminationRound=r.ourEliminated?m.rounds-1:null;
    counts[r.map+'|'+r.opponent]=(counts[r.map+'|'+r.opponent]||0)+1;
    games.push(r);
  }
  if(gameRows.length!==70||Object.keys(counts).length!==70||Object.values(counts).some(x=>x!==1))throw Error('Incomplete wave '+d.set);
  sets.push({...d,n:gameRows.length,massN:ms.length,endgameN:es.length});
}
games.sort((a,b)=>a.id-b.id);
const manifest={createdAt:new Date().toISOString(),resource,sets,absent,n:games.length,uniqueGameIds:seen.size,cacheCheck,egCheck,excluded:['r1-online','r1-autoscrim','g1','g2'],allSeats:[...new Set(games.map(x=>x.ourSide))]};
fs.writeFileSync(OUT+'/manifest.json',JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
fs.writeFileSync(OUT+'/primary.jsonl',games.map(x=>JSON.stringify(x)).join('\n')+'\n',{flag:'wx'});
console.log(JSON.stringify({n:games.length,sets:sets.length,waves:sets.filter(x=>x.era==='waves').length,wins:games.filter(x=>x.outcome==='W').length,absent,cacheCheck,egCheck}));
