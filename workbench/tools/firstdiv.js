#!/usr/bin/env node
'use strict';
process.env.UNSW_RULES = '123';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const {load} = require('./replay');
const {perGame} = require('./mass_ledger');
const CAUSES = ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'];
const HORIZONS = [1, 3, 10, 50];
const replacer = (_, x) => typeof x === 'bigint' ? x.toString() : x;
const stable = v => JSON.stringify(v, replacer);
const digest = v => crypto.createHash('sha256').update(stable(v)).digest('hex');
const same = (a, b) => stable(a) === stable(b);
const actionText = a => !a ? 'NO_ACTION' : a.kind === 'move' ? a.steps.join('') : a.kind === 'split' ? `SPLIT:${a.childSegmentCount}` : stable(a);
const tile = (p, W) => p.y * W + p.x;
function board(dragons, pearls, W, H) {
  return {W, H, dragons: [...dragons.values()].map(d => ({id:d.id, team:d.team, body:d.body.map(p => typeof p === 'number' ? p : tile(p, W))})).sort((a,b) => a.id-b.id), pearls:[...pearls.keys()].sort((a,b) => a-b)};
}
function inventory(dir) {
  const rows = new Map(), historyErrors = [], duplicates = [];
  const f = path.join(dir, 'rows.jsonl');
  for (const [i, line] of fs.readFileSync(f, 'utf8').split('\n').entries()) {
    if (!line.trim()) continue;
    const r = JSON.parse(line);
    if (r.exit !== 0 || r.error || r.botProblem || r.G === undefined) {historyErrors.push({line:i+1,row:r}); continue;}
    if (rows.has(r.key)) duplicates.push(r.key);
    rows.set(r.key, r);
  }
  return {rows, historyErrors, duplicates};
}
function replayFile(dir, key) {
  const f = path.join(dir, 'games', key.replace(/:/g, '_'), 'game.replay');
  if (fs.existsSync(f)) return f;
  if (fs.existsSync(f+'.gz')) return f+'.gz';
  throw Error('missing replay: '+f);
}
function actionLog(R, side) {
  const teams = new Map(R.match.map.initialDragons.map(d => [d.id,d.team]));
  const result = new Map(), indicators = new Map(); let r = -1, order = 0;
  for (const e of R.events) {
    if (e.type === 'roundStart') {r=e.round;order=0;}
    if (e.type === 'turnStart') indicators.delete(e.id);
    if (e.type === 'dragonSplit') teams.set(e.childId,e.team);
    if (e.type === 'dragonIndicator') indicators.set(e.id,e.text);
    if (e.type === 'dragonAction') {
      if (!side || teams.get(e.id) === side) result.set(`${r}:${e.id}`, {round:r,id:e.id,team:teams.get(e.id),order,action:e.action ?? null,text:actionText(e.action),indicator:indicators.get(e.id) ?? null,tle:!!e.tle});
      order++;
    }
  }
  return result;
}
function changes(on, off) {
  const out = [];
  for (const key of new Set([...on.keys(),...off.keys()])) {
    const a=on.get(key),b=off.get(key);
    if (!a || !b || !same(a.action,b.action) || a.tle!==b.tle) {
      const x=a||b;out.push({round:x.round,id:x.id,order:Math.min(a?.order ?? Infinity,b?.order ?? Infinity),on:a??null,off:b??null});
    }
  }
  return out.sort((a,b) => a.round-b.round || a.order-b.order || a.id-b.id);
}
const PREFIX_TYPES = new Set(['roundStart','turnStart','dragonAction','dragonUpdate','dragonSplit','dragonDeath','tileChange','pearlCountdown','sonarPing']);
function firstPrefixDifference(A, B, limit) {
  function* events(R) {let round=-1;for (const e of R.events) {if(e.type==='roundStart')round=e.round;if(round>limit)return;if(PREFIX_TYPES.has(e.type))yield {round,event:e};}}
  const a=events(A),b=events(B);
  for (;;) {const x=a.next(),y=b.next();if(x.done&&y.done)return null;
    if (x.done||y.done||!same(x.value,y.value)) return {on:x.value??null,off:y.value??null};}
}
function reconstruct(R, fork, ids) {
  const M=R.match.map,W=M.width,H=M.height;
  const drag=new Map(M.initialDragons.map(d=>[d.id,{id:d.id,team:d.team,body:d.body.map(p=>tile(p,W))}]));
  const pearls=new Set();for(let t=0;t<M.initialTiles.length;t++)if(M.initialTiles[t]===2)pearls.add(t);
  const turns=new Map(),deaths=new Map(),facing=new Map(M.initialDragons.map(d=>[d.id,d.facing]));
  let r=-1,start=null,rounds=0,startFacing=null,currentMover=null;
  for(const e of R.events) {
    if(e.type==='roundStart'){r=e.round;rounds=r+1;if(r===fork){start=board(drag,pearls,W,H);startFacing=[...facing].filter(([id])=>drag.has(id)).sort((a,b)=>a[0]-b[0]);}}
    if(e.type==='turnStart'&&r===fork&&ids.has(e.id))turns.set(e.id,{board:board(drag,pearls,W,H),facing:facing.get(e.id)});
    if(e.type==='turnStart')currentMover=e.id;
    if(e.type==='tileChange'){const t=tile(e.tile,W);if(e.hasPearl)pearls.add(t);else pearls.delete(t);}
    if(e.type==='dragonUpdate') {
      const d=drag.get(e.id);if(!d)throw Error('update of missing dragon '+e.id);
      const head=tile(e.head,W),tail=tile(e.tail,W);if(d.body[0]!==head)d.body.unshift(head);
      const i=d.body.lastIndexOf(tail);if(i<0)throw Error(`missing tail r${r} #${e.id}`);
      d.body.length=i+1;facing.set(e.id,e.facing);
    }
    if(e.type==='dragonSplit') {
      drag.get(e.parentId).body=e.parentBody.map(p=>tile(p,W));
      drag.set(e.childId,{id:e.childId,team:e.team,body:e.childBody.map(p=>tile(p,W))});facing.set(e.childId,e.childFacing);
    }
    if(e.type==='dragonDeath'){deaths.set(e.id,{round:r,reason:e.reason,mover:currentMover});drag.delete(e.id);}
  }
  return {start,startFacing,turns,deaths,rounds,final:board(drag,pearls,W,H)};
}
function detailed(R, fork, ids, raw) {
  const turns=new Map(),acts=new Map(),deaths=new Map();let validationTurns=0;
  const ledger=perGame(R,{map:'?',rules:'123'},{
    turn(d,r,c){if(r!==fork||!ids.has(d.id))return;
      const b=board(c.drag,c.pearls,c.W,c.H);validationTurns++;
      if(!same(b,raw.turns.get(d.id)?.board))throw Error(`raw/ledger board mismatch r${r} #${d.id}`);
      const h=d.body[0],near=['N','E','S','W'].map(dir=>{const p=c.across(h.x,h.y,dir);const occupant=p?c.occ.get(c.key(p.x,p.y)):undefined;return {dir,tile:p?tile(p,c.W):null,occupant:occupant??null,pearl:p?c.pearls.has(tile(p,c.W)):false};});
      turns.set(d.id,{hash:digest(b),body:d.body.map(p=>tile(p,c.W)),head:{...h},neighbors:near});
    },
    action(d,e,r,c,before){acts.set(d.id,{round:r,action:e.action??null});if(r!==fork||!ids.has(d.id))return;
      const t=turns.get(d.id);if(t){t.fate=d.fate?{...d.fate}:null;t.after=d.body.map(p=>tile(p,c.W));t.action=e.action??null;}
    },
    death(d,rec,idx,other,r,c){deaths.set(d.id,{round:r,reason:raw.deaths.get(d.id)?.reason??null,cause:CAUSES[rec.cause],mover:raw.deaths.get(d.id)?.mover??null,otherId:other?.id??null,otherTeam:other?.team??null,otherBody:other?.body.map(p=>tile(p,c.W))??null,otherAction:other?acts.get(other.id)??null:null,body:d.body.map(p=>tile(p,c.W)),ownAction:acts.get(d.id)??null});}
  });
  if(Object.values(ledger.chk).some(Boolean))throw Error('ledger checks: '+stable(ledger.chk));
  if(raw.rounds!==ledger.rounds)throw Error('round count mismatch');
  const end={A:raw.final.dragons.filter(d=>d.team==='A'),B:raw.final.dragons.filter(d=>d.team==='B')};
  for(const side of ['A','B']){const ds=end[side],res=R.result['team'+side];if(ds.length!==res.dragonCount||ds.reduce((s,d)=>s+d.body.length,0)!==res.totalLength||Math.max(0,...ds.map(d=>d.body.length))!==res.longestDragon)throw Error('raw final mismatch');}
  for(const [id,x]of raw.deaths)if(!same(x,{round:deaths.get(id)?.round,reason:deaths.get(id)?.reason,mover:deaths.get(id)?.mover}))throw Error('death mismatch');
  return {turns,deaths,checks:ledger.chk,validationTurns};
}
function fate(raw, detail, id, R) {
  const death=detail.deaths.get(id)??null,initial=raw.start?.dragons.some(d=>d.id===id)??false;
  const states={};
  for(const k of HORIZONS){const target=R+k;const dead=death&&death.round<target;
    states[k]={round:target,state:dead?'dead':target<=raw.rounds?'alive':'censored',alive:dead?false:target<=raw.rounds?true:null,death:dead?death:null,observedThrough:raw.rounds};}
  return {id,aliveAtFork:initial,death,states};
}
function classify(a,b,k) {
  const x=a.states[k].state,y=b.states[k].state;
  if(x==='censored'||y==='censored')return 'censored';
  return x==='dead'?(y==='alive'?'harm':'both'):(y==='dead'?'help':'neither');
}
function analyzePair(key, onFile, offFile, side) {
  const A=load(onFile),B=load(offFile),changesAll=changes(actionLog(A,side),actionLog(B,side)),first=changesAll[0];
  if(!first)return {key,status:'no_divergence',R:null,id:null,files:{on:onFile,off:offFile},prefixDifference:firstPrefixDifference(A,B,Infinity)};
  const R=first.round,changed=changesAll.filter(c=>c.round===R),ids=new Set(changed.map(c=>c.id));
  const queenIds=[A,B].map(replay=>Math.min(...replay.match.map.initialDragons.filter(d=>d.team===side).map(d=>d.id)));
  if(queenIds[0]!==queenIds[1]||!Number.isFinite(queenIds[0]))throw Error('queen ids differ or absent');
  const queenId=queenIds[0],ar=reconstruct(A,R,ids),br=reconstruct(B,R,ids),ad=detailed(A,R,ids,ar),bd=detailed(B,R,ids,br);
  const boardIdentical=same(ar.start,br.start),geometryIdentical=same(A.match.map,B.match.map),facingIdentical=same(ar.startFacing,br.startFacing);
  const firstActionDifferenceAll=changes(actionLog(A,null),actionLog(B,null))[0]??null;
  const record={key,side,R,id:first.id,status:boardIdentical&&geometryIdentical&&facingIdentical?'matched':'state_mismatch',files:{on:onFile,off:offFile},boardIdentical,geometryIdentical,facingIdentical,firstActionDifferenceAll,
    boardHashes:{on:digest(ar.start),off:digest(br.start)},board:ar.start,offBoard:boardIdentical?null:br.start,
    prefixDifference:firstPrefixDifference(A,B,R),checks:{on:ad.checks,off:bd.checks},validationTurns:ad.validationTurns+bd.validationTurns,rounds:{on:ar.rounds,off:br.rounds},changed:[]};
  for(const c of changed){const f={on:fate(ar,ad,c.id,R),off:fate(br,bd,c.id,R)};const at=ad.turns.get(c.id),bt=bd.turns.get(c.id);
    record.changed.push({...c,turnBoardIdentical:!!at&&!!bt&&at.hash===bt.hash,turn:{on:at??null,off:bt??null},fates:f,classification:Object.fromEntries([1,3,10].map(k=>[k,classify(f.on,f.off,k)]))});}
  const f={on:fate(ar,ad,queenId,R),off:fate(br,bd,queenId,R)};
  record.queen={id:queenId,fates:f,classification:Object.fromEntries([10,50].map(k=>[k,classify(f.on,f.off,k)]))};
  record.actions={on:first.on,off:first.off};record.fates=record.changed[0].fates;record.classification=record.changed[0].classification;
  record.firstTurnBoardIdentical=record.changed[0].turnBoardIdentical;
  return record;
}
function summarize(rows) {
  const result={keys:rows.length,status:{},tables:{changed:{},queen:{}},stateMismatches:[],errors:[],noDivergence:[],firstTurnMismatches:[],priorInfoDifferences:[]};
  for(const subject of ['changed','queen'])for(const k of subject==='changed'?[1,3,10]:[10,50])result.tables[subject][k]={harm:0,help:0,both:0,neither:0,censored:0};
  for(const row of rows){result.status[row.status]=(result.status[row.status]||0)+1;
    if(row.status==='error'){result.errors.push({key:row.key,error:row.error});continue;}
    if(row.status==='no_divergence'){result.noDivergence.push(row.key);continue;}
    if(row.status!=='matched'){result.stateMismatches.push(row.key);continue;}
    if(!row.firstTurnBoardIdentical)result.firstTurnMismatches.push(row.key);
    const p=row.prefixDifference;if(p&&(p.on?.round<row.R||p.off?.round<row.R))result.priorInfoDifferences.push({key:row.key,difference:p});
    for(const k of [1,3,10])result.tables.changed[k][row.classification[k]]++;
    for(const k of [10,50])result.tables.queen[k][row.queen.classification[k]]++;
  }
  result.queenDeadBeforeFork=rows.filter(r=>r.status==='matched'&&!r.queen.fates.on.aliveAtFork&&!r.queen.fates.off.aliveAtFork).length;
  return result;
}
function selfTest() {
  const raw={rounds:12,start:{dragons:[{id:0}]}},d={deaths:new Map([[0,{round:10,reason:'H'}]])},f=fate(raw,d,0,10);
  if(f.states[1].state!=='dead'||f.states[3].state!=='dead')throw Error('death boundary');
  const g=fate(raw,{deaths:new Map()},0,10);
  if(g.states[1].state!=='alive'||g.states[3].state!=='censored')throw Error('censor boundary');
  if(classify(f,g,1)!=='harm'||classify(g,f,1)!=='help'||classify(f,f,1)!=='both'||classify(g,g,1)!=='neither'||classify(f,g,3)!=='censored')throw Error('classifications');
  const a=new Map([['0:0',{round:0,id:0,order:0,action:{kind:'move',steps:['N']},tle:false}]]),b=new Map([['0:0',{round:0,id:0,order:0,action:{kind:'move',steps:['E']},tle:false}]]);
  if(changes(a,b).length!==1||changes(a,a).length||changes(a,new Map()).length!==1)throw Error('action diff');
  const observed=fate({...raw,rounds:20},{deaths:new Map([[0,{round:13,reason:'S'}]])},0,10);
  if(observed.states[3].state!=='alive'||observed.states[10].state!=='dead')throw Error('exclusive horizon');
  return {passed:true,checks:['death boundary','censor boundary','five fate classes','action equality/missing action','exclusive horizon']};
}
async function main() {
  const args=process.argv.slice(2);if(args[0]==='--self-test'){console.log(stable(selfTest()));return;}
  if(args.length<2||args.includes('--help')){console.log('usage: UNSW_RULES=123 node tools/firstdiv.js ON_DIR OFF_DIR [--out FILE] [--key KEY]\nNo games. Fate at R+k means start of round R+k (death rounds R..R+k-1).');return;}
  const opt=k=>{const i=args.indexOf(k);return i<0?null:args[i+1];};
  const onDir=path.resolve(args[0]),offDir=path.resolve(args[1]),on=inventory(onDir),off=inventory(offDir),wanted=opt('--key');
  const keys=[...new Set([...on.rows.keys(),...off.rows.keys()])].filter(k=>!wanted||k===wanted).sort(),rows=[];
  for(const key of keys){let row;try{
    if(!on.rows.has(key)||!off.rows.has(key))throw Error('missing on/off result row');
    const x=on.rows.get(key),y=off.rows.get(key);if(['side','map','opp','seed'].some(k=>x[k]!==y[k]))throw Error('row metadata differs');
    row=analyzePair(key,replayFile(onDir,key),replayFile(offDir,key),x.side);
  }catch(e){row={key,status:'error',error:String(e.stack||e)};}rows.push(row);process.stderr.write(`${rows.length}/${keys.length} ${key} ${row.status}${row.R===undefined||row.R===null?'':' R='+row.R}\n`);}
  if(wanted&&!keys.length)throw Error('key not found: '+wanted);
  const report={schemaVersion:1,rules:'123',createdAt:new Date().toISOString(),inputs:{on:onDir,off:offDir},definitions:{time:'start of R+k; death in R..R+k-1 inclusive',changedDragon:'first action difference in round/turn order; all changed dragons at R retained',queen:'lowest initial id for our team; prior deaths retained and counted separately',censored:'game ended alive before horizon; not counted as survivor',eligibility:'identical geometry and all dragon bodies/pearl tiles at start R; turn equality and earlier sonar differences reported separately',effect:'whole switch continuation after fork; later changed actions may mediate outcomes'},inventory:{on:{keys:on.rows.size,historyErrors:on.historyErrors,duplicates:on.duplicates},off:{keys:off.rows.size,historyErrors:off.historyErrors,duplicates:off.duplicates}},summary:summarize(rows),rows};
  const out=opt('--out');if(out){fs.mkdirSync(path.dirname(path.resolve(out)),{recursive:true});fs.writeFileSync(out,JSON.stringify(report,replacer,2)+'\n');console.log(JSON.stringify(report.summary,replacer,2));}else console.log(JSON.stringify(report,replacer,2));
}
if(require.main===module)main().catch(e=>{console.error(e.stack);process.exitCode=1;});
module.exports={analyzePair,summarize,classify,fate,changes,reconstruct,selfTest};
