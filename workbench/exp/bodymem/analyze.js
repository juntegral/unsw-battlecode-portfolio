#!/usr/bin/env node
'use strict';
process.env.UNSW_RULES = '123';
const fs = require('fs'), path = require('path'), crypto = require('crypto'), cp = require('child_process');
const TASK = __dirname, ROOT = path.resolve(TASK, '../..');
const {makeLoader, viewerSource} = require(path.join(ROOT, 'tools/top_features.js'));
const {perGame} = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource()), spec = JSON.parse(fs.readFileSync(path.join(TASK, 'spec.json')));
const causes = ['sac','trap','rammed','ram','enemyBody','allyHead','fault','sprintDeath'];
function fingerprint(R) {
  const h = crypto.createHash('sha256'), skip = new Set(['dragonIndicator','dragonLog','debugDraw','engineLog']);
  for (const e of R.events) {
    if (skip.has(e.type)) continue;
    const o = {}; for (const [k,v] of Object.entries(e)) if (k !== 'instructions') o[k] = typeof v === 'bigint' ? String(v) : v;
    h.update(JSON.stringify(o));
  }
  return h.digest('hex');
}
function bodyHash(body) { let h=2166136261; for (const t of body) h=Math.imul(h^t,16777619)>>>0; return h; }
function audit(R, row, on) {
  const queen = Math.min(...R.match.map.initialDragons.filter(d=>d.team===row.side).map(d=>d.id));
  const out = {queen, hash:fingerprint(R), multi:0, completed:0, selfMulti:0, queenSelfMulti:0,
    self:0, rejected:0, oracleDrift:[], stepDrift:[], startBodyDrift:[], endBodyDrift:[], memoryDrift:[], missingTags:[], unknownInput:0, unseenPearls:0,
    predicted:0, deaths:[], reasons:{}, causes:{}, death:null, oversprint:0, depth:{}, samples:[], cpu:row.cpu||[]};
  const indicators=new Map(), starts=new Map(), actions=new Map(), requests=[], expected=[], expectedUpdates=new Map();
  const ledger=perGame(R,{map:row.map||'?',variant:'a',rules:'123'},{
    indicator(e) { indicators.set(e.id,e.text||''); },
    turn(d,round,c) { if(d.team===row.side) starts.set(d.id,{pearls:new Set(c.pearls.keys())}); },
    action(d,e,round,c,before) {
      if(d.team!==row.side) return;
      const ind=indicators.get(d.id)||'', steps=e.action&&e.action.kind==='move'?e.action.steps.length:0;
      const rec={id:d.id,round,steps,action:e.action,indicator:ind,fate:d.fate,start:before.map(t=>c.key(t.x,t.y))};
      actions.set(d.id,rec);
      const dep=/\bd(\d+)\b/.exec(ind); if(dep)out.depth[round+':'+d.id]=+dep[1];
      const rej=/\bbodyxr(\d+)/.exec(ind); if(rej)out.rejected+=+rej[1];
      if(steps<2) return;
      out.multi++;
      if(d.fate) { if(d.fate.why==='sprint')out.oversprint++; return; }
      out.completed++;
      let head=before[0]; const tiles=[],eats=[],consumed=new Set(),st=starts.get(d.id);
      for(const dir of e.action.steps) {
        head=c.across(head.x,head.y,dir); if(!head)throw Error('completed blocked path');
        const t=c.key(head.x,head.y); tiles.push(t);eats.push(+(st.pearls.has(t)&&!consumed.has(t)));consumed.add(t);
      }
      requests.push([before.length,steps,c.W*c.H,...rec.start,...tiles,...eats,0,-1].join(' '));
      const end=d.body.map(t=>c.key(t.x,t.y));
      let oracle=[...rec.start]; const snapshots=[],free=Math.ceil(before.length/4);
      for(let i=0;i<steps;i++) { oracle.unshift(tiles[i]);if(!eats[i])oracle.pop();if(i>=free)oracle.pop();snapshots.push([...oracle]); }
      const want={id:d.id,round,body:end,states:snapshots}; expected.push(want);
      expectedUpdates.set(round+':'+d.id,want);
      const tag=/\bbodyx(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)/.exec(ind);
      if(on) {
        if(!tag)out.missingTags.push({id:d.id,round,indicator:ind});
        else {
          out.predicted++;
          const v=tag.slice(1).map(Number),actual=[free,Math.max(0,steps-free),end.length,0,bodyHash(rec.start),bodyHash(end),0];
          if(v[4]!==actual[4])out.startBodyDrift.push({id:d.id,round,reported:v[4],actual:actual[4]});
          if(v[2]!==actual[2]||v[5]!==actual[5])out.endBodyDrift.push({id:d.id,round,reported:v,actual});
          if(v[3])out.unknownInput++; if(v[6])out.unseenPearls++;
          if(v[0]!==actual[0]||v[1]!==actual[1]||v[2]!==actual[2]||v[4]!==actual[4]||v[5]!==actual[5])
            out.memoryDrift.push({id:d.id,round,reported:v,actual,inputMismatch:v[4]!==actual[4],start:rec.start,end,tiles,eats,indicator:ind});
        }
      }
      if(out.samples.length<8)out.samples.push({...rec,end,tiles,eats});
    },
    death(d,rec,idx,other,round) {
      if(d.team!==row.side)return;
      const a=actions.get(d.id), x={id:d.id,round,cause:causes[rec.cause],head:d.body[0],length:d.body.length,
        steps:a&&a.round===round?a.steps:0,action:a&&a.round===round?a.action:null,
        indicator:indicators.get(d.id)||'',fate:d.fate};
      out.deaths.push(x); if(d.id===queen)out.death=x;
    }
  });
  const rawDeaths=new Map(R.events.filter(e=>e.type==='dragonDeath').map(e=>[e.id,e.reason]));
  for(const d of out.deaths) {
    d.reason=rawDeaths.get(d.id);out.reasons[d.reason]=(out.reasons[d.reason]||0)+1;out.causes[d.cause]=(out.causes[d.cause]||0)+1;
    if(d.reason==='S') { out.self++;if(d.steps>1){out.selfMulti++;if(d.id===queen)out.queenSelfMulti++;} }
    d.intentionalFeed=/^(feed|sf|conv)/.test(d.indicator);d.noExit=/^(no-exit|last-trade)/.test(d.indicator);
  }
  out.checks=ledger.chk;
  out.lastRound=Math.max(...R.events.filter(e=>e.type==='roundStart').map(e=>e.round));
  out.queenLifetime=out.death?out.death.round:out.lastRound+1; out.queenCensored=!out.death;
  if(requests.length) {
    const r=cp.spawnSync(path.join(TASK,'transition-on'),[],{input:requests.join('\n')+'\n',encoding:'utf8',maxBuffer:256*1024**2});
    if(r.status!==0)throw Error('production transition failed: '+r.stderr);
    const lines=r.stdout.trim().split('\n').map(JSON.parse);if(lines.length!==expected.length)throw Error('predictor response count');
    for(let i=0;i<lines.length;i++) {
      const got=lines[i],want=expected[i];
      if(!got.legal||got.reason!=='-'||JSON.stringify(got.body)!==JSON.stringify(want.body)||JSON.stringify(got.states)!==JSON.stringify(want.states))
        out.oracleDrift.push({...want,got});
    }
  }
  let round=-1; const indices=new Map();
  for(const e of R.events) {
    if(e.type==='roundStart')round=e.round;
    if(e.type==='dragonAction')indices.set(round+':'+e.id,0);
    if(e.type!=='dragonUpdate')continue;
    const key=round+':'+e.id,want=expectedUpdates.get(key);if(!want)continue;
    const i=indices.get(key)||0,b=want.states[i];indices.set(key,i+1);
    if(!b||b[0]!==e.head.y*R.match.map.width+e.head.x||b[b.length-1]!==e.tail.y*R.match.map.width+e.tail.x)
      out.stepDrift.push({id:e.id,round,step:i,head:e.head,tail:e.tail,predicted:b});
  }
  for(const [key,want] of expectedUpdates)if(indices.get(key)!==want.states.length)out.stepDrift.push({key,missingUpdates:want.states.length-(indices.get(key)||0)});
  const cpu=out.cpu.find(l=>l.startsWith('team '+row.side+' points per turn:')),max=cpu&&/max\s+([\d.]+)M/.exec(cpu);
  out.cpuMaxM=max?+max[1]:null;
  return out;
}
if(process.argv.includes('--replay')) {
  const arg=k=>process.argv[process.argv.indexOf(k)+1],f=arg('--replay'),side=arg('--side');
  const r=audit(load(path.resolve(ROOT,f)),{side,cpu:[]},process.argv.includes('--on'));
  const out=arg('--out');if(out)fs.writeFileSync(path.resolve(ROOT,out),JSON.stringify(r,null,2)+'\n');
  console.log(JSON.stringify({multi:r.multi,completed:r.completed,checks:r.checks,oracleDrift:r.oracleDrift.length,stepDrift:r.stepDrift.length,memoryDrift:r.memoryDrift.length}));
  process.exit(r.oracleDrift.length||r.stepDrift.length?1:0);
}
const report={expectedGames:0,sets:{},missing:[],historyErrors:[],pairs:[],identity:[]};
const clean=r=>r.G!==undefined&&r.exit===0&&!r.error&&!r.botProblem;
for(const dir of new Set(spec.map(s=>s.out))) {
  const name=path.basename(dir),file=path.join(ROOT,dir,'rows.jsonl'),rows=new Map(),expected=new Set();report.sets[name]={};
  if(fs.existsSync(file))for(const l of fs.readFileSync(file,'utf8').split('\n').filter(Boolean)){
    const r=JSON.parse(l);if(clean(r))rows.set(r.key,r);else report.historyErrors.push({set:name,row:r});
  }
  for(const s of spec.filter(s=>s.out===dir))for(const opp of s.opps)for(const map of s.only)for(const side of s.sides)for(const seed of s.seeds)
    expected.add([path.basename(opp),map,side,seed].join(':'));
  report.expectedGames+=expected.size;
  for(const key of expected){
    const row=rows.get(key),f=path.join(ROOT,dir,'games',key.replace(/:/g,'_'),'game.replay');
    if(!row||!fs.existsSync(f)){report.missing.push({set:name,key});continue;}
    report.sets[name][key]=audit(load(f),row,true);
  }
}
for(const [key,on]of Object.entries(report.sets.on||{})) {
  const off=report.sets.off[key];if(!off)continue;
  const reasons={},causes={};for(const r of new Set([...Object.keys(on.reasons),...Object.keys(off.reasons)]))reasons[r]=(on.reasons[r]||0)-(off.reasons[r]||0);
  for(const c of new Set([...Object.keys(on.causes),...Object.keys(off.causes)]))causes[c]=(on.causes[c]||0)-(off.causes[c]||0);
  const depth=Object.keys(on.depth).filter(k=>off.depth[k]!==undefined).map(k=>on.depth[k]-off.depth[k]);
  report.pairs.push({key,reasonsOn:on.reasons,reasonsOff:off.reasons,causesOn:on.causes,causesOff:off.causes,queenCensoredOn:on.queenCensored,queenCensoredOff:off.queenCensored,queenLifeOn:on.queenLifetime,queenLifeOff:off.queenLifetime,queenLifeDirection:on.queenLifetime>off.queenLifetime?'longer':on.queenLifetime<off.queenLifetime?'shorter':'same',startDriftOn:on.startBodyDrift.length,startDriftOff:off.startBodyDrift.length,multiOn:on.multi,multiOff:off.multi,selfMultiDelta:on.selfMulti-off.selfMulti,queenSelfMultiDelta:on.queenSelfMulti-off.queenSelfMulti,
    reasons,causes,queenDeathDelta:Number(!!on.death)-Number(!!off.death),queenEarlier:!!on.death&&(!off.death||on.death.round<off.death.round),
    depthPairs:depth.length,depthLower:depth.filter(v=>v<0).length,depthSame:depth.filter(v=>v===0).length,depthHigher:depth.filter(v=>v>0).length});
}
for(const [key,off]of Object.entries(report.sets['id-off']||{})) {
  const base=report.sets['id-base'][key];report.identity.push({key,same:!!base&&off.hash===base.hash});
}
const columns=['key','multiOn','multiOff','startDriftOn','startDriftOff','queenLifeOn','queenLifeOff','queenLifeDirection','queenCensoredOn','queenCensoredOff','reasonsOn','reasonsOff','causesOn','causesOff'];
fs.writeFileSync(path.join(TASK,'keywise.tsv'),columns.join('\t')+'\n'+report.pairs.map(p=>columns.map(c=>typeof p[c]==='object'?JSON.stringify(p[c]):p[c]).join('\t')).join('\n')+'\n');
fs.writeFileSync(path.join(TASK,'analysis.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({expectedGames:report.expectedGames,missing:report.missing.length,historyErrors:report.historyErrors.length,pairs:report.pairs.length,identity:report.identity},null,2));
if(report.missing.length)process.exitCode=2;
