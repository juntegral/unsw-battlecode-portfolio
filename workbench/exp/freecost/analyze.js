#!/usr/bin/env node
'use strict';
process.env.UNSW_RULES = '123';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process');
const ROOT=path.resolve(__dirname,'../..'),TASK=__dirname;
const {makeLoader,viewerSource}=require(path.join(ROOT,'tools/top_features.js'));
const {perGame}=require(path.join(ROOT,'tools/mass_ledger.js'));
const load=makeLoader(viewerSource()),spec=JSON.parse(fs.readFileSync(path.join(TASK,'spec.json')));
const skip=new Set(['dragonIndicator','dragonLog','debugDraw','engineLog']);
function fingerprint(R) {
 const h=crypto.createHash('sha256');
 for(const e of R.events) {
  if(skip.has(e.type))continue;
  const o={};for(const [k,v]of Object.entries(e))if(k!=='instructions')o[k]=typeof v==='bigint'?String(v):v;
  h.update(JSON.stringify(o));
 }
 return h.digest('hex');
}
function hashBody(body,W) {let h=2166136261;for(const t of body)h=Math.imul(h^(t.y*W+t.x),16777619)>>>0;return h;}
function audit(R,row,on) {
 const queen=Math.min(...R.match.map.initialDragons.filter(d=>d.team===row.side).map(d=>d.id));
 const out={queen,hash:fingerprint(R),turnsL5:0,freeMulti:0,completedFreeMulti:0,death:null,deaths:[],self:0,wall:0,oversprint:0,invalidAction:0,blindUnverified:0,
  bands:{},moves:[],predicted:0,missingTags:0,knownBodyDrift:[],uncertainBodyDrift:[],unknownBodies:0,oracleDrift:[],checks:{},cpu:row.cpu||[]};
 const indicators=new Map(),starts=new Map(),requests=[],expected=[];
 const ledger=perGame(R,{map:'?',variant:'a',rules:'123'},{
  indicator(e){indicators.set(e.id,e.text||'');},
  turn(d,round,c){
   if(d.team!==row.side)return;
   if(d.body.length>=5)out.turnsL5++;
   const band=d.body.length<=4?'2-4':d.body.length<=8?'5-8':d.body.length<=12?'9-12':'13+';
   const b=out.bands[band]||(out.bands[band]={turns:0,freeMulti:0});b.turns++;
   starts.set(d.id,{band,pearls:new Set(c.pearls.keys())});
  },
  action(d,e,round,c,before){
   if(d.team!==row.side||!e.action||e.action.kind!=='move')return;
   const steps=e.action.steps.length,L=before.length,gratis=Math.ceil(L/4),paid=Math.max(0,steps-gratis),st=starts.get(d.id);
   const freeMulti=L>=5&&steps>1&&steps<=gratis;
   if(freeMulti){out.freeMulti++;out.bands[st.band].freeMulti++;if(!d.fate)out.completedFreeMulti++;}
   const ind=indicators.get(d.id)||'',tag=/\bfc(\d+),(\d+),(\d+),(\d+),(\d+)/.exec(ind);
   if(freeMulti||tag)out.moves.push({id:d.id,round,L,steps,gratis,paid,action:e.action.steps.join(''),head:before[0],fate:d.fate,indicator:ind});
   if(d.fate){if(d.fate.why==='sprint')out.oversprint++;return;}
   let h=before[0];const tiles=[],eats=[];
   for(const dir of e.action.steps){h=c.across(h.x,h.y,dir);if(!h)throw Error('survived blocked move');tiles.push(h);eats.push(st.pearls.has(c.key(h.x,h.y))?1:0);}
   requests.push([L,steps,...before.map(t=>c.key(t.x,t.y)),...tiles.map(t=>c.key(t.x,t.y)),...eats].join(' '));
   expected.push({id:d.id,round,body:d.body.map(t=>c.key(t.x,t.y)),paid});
   if(on){
    if(!tag){if(/PORTAL\?/.test(ind))out.blindUnverified++;else out.missingTags++;return;}
    out.predicted++;
    const vals=tag.slice(1).map(Number),unknown=vals[3];
    if(unknown>0){out.unknownBodies++;return;}
    const drift=vals[0]!==gratis||vals[1]!==paid||vals[2]!==d.body.length||vals[4]!==hashBody(d.body,c.W);
    if(drift){
     const rec={id:d.id,round,L,steps,reported:vals,actual:[gratis,paid,d.body.length,0,hashBody(d.body,c.W)],head:before[0],indicator:ind};
     (tiles.every(t=>c.cheb(t,before[0])<=3)?out.knownBodyDrift:out.uncertainBodyDrift).push(rec);
    }
   }
  },
  death(d,rec,idx,other,round){if(d.team!==row.side)return;
   const x={id:d.id,round,reason:rec.reason,head:d.body[0],L:d.body.length,indicator:indicators.get(d.id)||''};
   // The raw death reason is recorded below; ledger causes group wall and self together.
   out.deaths.push(x);if(d.id===queen)out.death=x;
  }
 });
 // Attach raw reasons in event order; hooks retain the useful before-death body state.
 const raw=R.events.filter(e=>e.type==='dragonDeath');
 for(const d of out.deaths){const e=raw.find(e=>e.id===d.id);d.reason=e?e.reason:null;if(d.reason==='S')out.self++;if(d.reason==='W')out.wall++;}
 out.invalidAction=R.events.filter(e=>e.type==='dragonDeath'&&out.deaths.some(d=>d.id===e.id)&&e.reason==='A').length;
 out.checks=ledger.chk;
 if(requests.length){
  const r=cp.spawnSync(path.join(TASK,'fixtures-on'),['--predict'],{input:requests.join('\n')+'\n',encoding:'utf8',maxBuffer:128*1024*1024});
  if(r.status!==0)throw Error('production predictor failed: '+r.stderr);
  const got=r.stdout.trim().split('\n');if(got.length!==expected.length)throw Error('predictor response count');
  for(let i=0;i<got.length;i++){
   const [paid,len,...body]=got[i].trim().split(/\s+/).map(Number),want=expected[i];
   if(paid!==want.paid||len!==want.body.length||JSON.stringify(body)!==JSON.stringify(want.body))out.oracleDrift.push({...want,got:body,gotPaid:paid});
  }
 }
 const cpuLine=out.cpu.find(l=>l.startsWith('team '+row.side+' points per turn:'));
 const max=cpuLine&&/max\s+([\d.]+)M/.exec(cpuLine);out.cpuMaxM=max?+max[1]:null;
 return out;
}
const report={expectedGames:0,sets:{},missing:[],historyErrors:[],pairs:[],identity:[]};
const clean=r=>r.G!==undefined&&r.exit===0&&!r.error&&!r.botProblem;
for(const dir of new Set(spec.map(s=>s.out))){
 const name=path.basename(dir),file=path.join(ROOT,dir,'rows.jsonl'),rows=new Map(),expected=new Set();report.sets[name]={};
 if(fs.existsSync(file))for(const l of fs.readFileSync(file,'utf8').split('\n').filter(Boolean)){
  const r=JSON.parse(l);if(clean(r))rows.set(r.key,r);else report.historyErrors.push({set:name,row:r});
 }
 for(const s of spec.filter(s=>s.out===dir))for(const opp of s.opps)for(const map of s.only)for(const side of s.sides)for(const seed of s.seeds)expected.add([path.basename(opp),map,side,seed].join(':'));
 report.expectedGames+=expected.size;
 for(const key of expected){
  const r=rows.get(key),f=path.join(ROOT,dir,'games',key.replace(/:/g,'_'),'game.replay');
  if(!r||!fs.existsSync(f)){report.missing.push({set:name,key});continue;}
  report.sets[name][key]=audit(load(f),r,name==='on');
 }
}
for(const [key,on]of Object.entries(report.sets.on||{})){
 const off=report.sets.off[key];if(!off)continue;
 report.pairs.push({key,freeMultiDelta:on.freeMulti-off.freeMulti,rateOn:on.turnsL5?on.freeMulti/on.turnsL5:null,rateOff:off.turnsL5?off.freeMulti/off.turnsL5:null,
  selfDelta:on.self-off.self,wallDelta:on.wall-off.wall,queenDeathDelta:Number(!!on.death)-Number(!!off.death),queenEarlier:!!on.death&&(!off.death||on.death.round<off.death.round)});
}
for(const [key,off]of Object.entries(report.sets['id-off']||{})){
 const base=report.sets['id-base'][key];report.identity.push({key,same:!!base&&off.hash===base.hash});
}
fs.writeFileSync(path.join(TASK,'analysis.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({expectedGames:report.expectedGames,missing:report.missing.length,historyErrors:report.historyErrors.length,
 pairs:report.pairs.length,identity:report.identity,regressions:report.pairs.filter(p=>p.selfDelta>0||p.wallDelta>0||p.queenDeathDelta>0||p.queenEarlier)},null,2));
if(report.missing.length)process.exitCode=2;
