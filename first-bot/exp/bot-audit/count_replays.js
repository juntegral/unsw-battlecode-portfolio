#!/usr/bin/env node
'use strict';
// Offline, one replay at a time; no games/network. Uses the repository's grammar and checked reconstruction.
const fs = require('fs'), path = require('path'), zlib = require('zlib'), cp = require('child_process'), os = require('os');
const ROOT = path.resolve(__dirname, '../..'), OUT = path.join(__dirname, process.argv[3] || '');
if (!OUT.startsWith(__dirname + path.sep) && OUT !== __dirname) throw Error('Output must stay under exp/bot-audit');
fs.mkdirSync(OUT, { recursive: true });
const { load } = require(path.join(ROOT, 'tools/replay.js'));
const { parseInd } = require(path.join(ROOT, 'tools/mech_check.js'));
const { perGame, FI } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const SET = process.argv[2] || 'cand-stack10-online';
const DIR = path.join(ROOT, 'data/online', SET);
const PHASE = r => r < 100 ? 'r0-99' : r < 250 ? 'r100-249' : r < 300 ? 'r250-299' : r < 340 ? 'r300-339' : r < 430 ? 'r340-429' : r < 450 ? 'r430-449' : r < 470 ? 'r450-469' : r < 495 ? 'r470-494' : 'r495-499';
const LEN = n => n <= 2 ? '2' : n <= 4 ? '3-4' : n <= 6 ? '5-6' : n === 7 ? '7' : '8+';
const SPLITS = new Set(['split','frag','bsplit','csplit','kcap','floor','lsplit','escsplit','escsplit2']);
const KNOWN_TAGS = ['feed','conv','pocket','escsplit','escsplit2','split','frag','bsplit','csplit','kcap','floor','lsplit','fc','noexit','noexit_spare','lasttrade','degraded','TRADE','PORTAL?','late','esc','T','g','K','F','F2','Fp','cov','grab','cl','ce','tg','tgx','gx','sx','px','pxx','px2','px2x','ks','ks2','ram4','ram4o','lnt','lntv','kint','tab','gh','ghd','kx','kxm','lwk','map'];
const inc = (o,k,n=1) => o[k]=(o[k]||0)+n;
function resourceCheck() {
  const mem = cp.execFileSync('memory_pressure', [], {encoding:'utf8'});
  const disk = cp.execFileSync('df', ['-g','/'], {encoding:'utf8'});
  const m = /System-wide memory free percentage:\s*(\d+)%/.exec(mem);
  const d = disk.trim().split('\n').at(-1).trim().split(/\s+/);
  if (!m || !Number.isFinite(+d[3])) throw Error('Resource readings unavailable; pause.');
  const x = {freeMemoryPct:+m[1],freeDiskGB:+d[3]};
  if (x.freeMemoryPct<10 || x.freeDiskGB<20) throw Error('PAUSE: '+JSON.stringify(x));
  return x;
}
function tagsOf(p,text) {
  const t=[];
  if (p.kind!=='move' && p.kind!=='none') t.push(p.kind);
  if (p.kind==='move') {
    for (const [f,k] of [['trade','TRADE'],['blind','PORTAL?'],['late','late'],['esc','esc'],['trust','T'],['fg','F'],['f2','F2'],['fp','Fp'],['cov','cov'],['grab','grab'],['cl','cl'],['ce','ce'],['gx','gx'],['sx','sx'],['ks','ks'],['ks2','ks2'],['kint','kint'],['gh','gh'],['ghd','ghd'],['kxm','kxm'],['lwk','lwk']]) if(p[f]) t.push(k);
    if(p.goal)t.push(p.goal); if(p.tg)t.push(p.tg); if(p.px)t.push(p.px); if(p.px2)t.push(p.px2);
    if(p.ram4)t.push(p.ram4==='new'?'ram4':'ram4o');
    if(p.lnt)t.push('lnt'); if(p.lntv!==undefined)t.push('lntv'); if(p.kx!==undefined)t.push('kx');
  }
  if(p.fc)t.push('fc'); if(p.tab)t.push('tab');
  if(/^no-exit s(?:\s|$)/.test(text))t.push('noexit_spare');
  if(/(?:^|\s)map=/.test(text))t.push('map');
  return t;
}
function one(row) {
  const file=path.join(DIR,'M'+row.gameId+'.replay'), before=resourceCheck();
  const R=load(file), us=String(row.ourSide).toUpperCase();
  const G={gameId:row.gameId,map:row.mapName,opp:row.opponentTeam,us,submission:row.ourSubmission,winner:R.result.winner||null,
    rounds:0,turns:0,labelled:0,move:0,tags:{},kinds:{},explicitGoals:{},goalModifiers:{},splits:{},splitActual:{},
    phases:{},lengths:{},cooccurrence:{},labelActionMismatch:0,duplicates:0,missingLabels:0,unexpected:[],
    gateChecks:{},maxDragonId:0,sonarFromIdOver255:0,resources:before,priority:os.getPriority()};
  const latest=new Map(), contexts=new Map(), rows=[], gate=(k,ok)=>{const x=G.gateChecks[k]||(G.gateChecks[k]={n:0,pass:0});x.n++;x.pass+=!!ok;};
  function turn(d,r,c) {
    G.maxDragonId=Math.max(G.maxDragonId,d.id); if(d.team!==us)return;
    G.turns++; G.rounds=Math.max(G.rounds,r+1);
    const units=[...c.drag.values()].filter(x=>x.team===us).length, enemyUnits=c.drag.size-units;
    const visible=[...c.drag.values()].filter(x=>x!==d&&c.cheb(x.body[0],d.body[0])<=3);
    const nearEnemy=visible.filter(x=>x.team!==us).length, nearAlly=visible.length-nearEnemy;
    const cx={r,L:d.body.length,u:units,eu:enemyUnits,king:c.isKingNow(d),nearEnemy,d3:nearAlly-nearEnemy};
    contexts.set(d.id,cx); latest.delete(d.id);
    const ph=PHASE(r), lc=LEN(cx.L); (G.phases[ph]||(G.phases[ph]={turns:0,tags:{},goals:{},splits:{}})).turns++;
    (G.lengths[lc]||(G.lengths[lc]={turns:0,tags:{}})).turns++;
  }
  function indicator(e,r,c) {
    const d=c.drag.get(e.id); if(!d||d.team!==us)return;
    if(latest.has(d.id))G.duplicates++;
    const cx=contexts.get(d.id); if(!cx||cx.r!==r)throw Error('Indicator without current context');
    G.labelled++; const p=parseInd(e.text), tags=tagsOf(p,e.text), ph=G.phases[PHASE(r)],lc=G.lengths[LEN(cx.L)];
    inc(G.kinds,p.kind); tags.forEach(k=>{inc(G.tags,k);inc(ph.tags,k);inc(lc.tags,k);});
    if(p.kind==='other'||p.extra?.length)G.unexpected.push({id:e.id,r,text:e.text,parsed:p});
    const eg=p.kind!=='move'?'early_action':p.fg?'F':p.goal||'none'; inc(G.explicitGoals,eg); inc(ph.goals,eg);
    if(p.kind==='move'){G.move++; const mods=tags.filter(k=>['g','K','F','F2','cov','grab','cl','ce','gh','ghd','kx'].includes(k));
      for(const k of mods)inc(G.goalModifiers,k);
      for(let i=0;i<mods.length;i++)for(let j=i+1;j<mods.length;j++)inc(G.cooccurrence,[mods[i],mods[j]].sort().join('+'));
    }
    if(SPLITS.has(p.kind)){inc(G.splits,p.kind);inc(ph.splits,p.kind);gate(p.kind+'_unit_limit',cx.u<64);}
    const target=Math.min(40,Math.max(8,Math.floor(c.W*c.H/45)));
    if(p.kind==='csplit'){gate('csplit_clock',r>=1&&r<250);gate('csplit_length',cx.L>=4);gate('csplit_actual_units',cx.u<target);gate('csplit_not_true_long_king',!(cx.L>=8&&cx.king));}
    if(p.kind==='lsplit'){gate('lsplit_clock',r>=250&&r<340);gate('lsplit_length',cx.L>=4&&cx.L<=6);gate('lsplit_actual_units',cx.u<target);}
    if(p.kind==='frag'){gate('frag_clock',r>=250&&r<=420);gate('frag_not_true_king',!cx.king);gate('frag_enemy_not_in_view',cx.nearEnemy===0);}
    if(p.kind==='floor')gate('floor_opponent_8plus',cx.eu>=8);
    if(p.kind==='kcap')gate('kcap_true_king',cx.king);
    if(p.lnt){gate('lnt_actual_d3_excluding_victim',cx.d3+1===p.lnt.d3);gate('lnt_d3_1plus',p.lnt.d3>=1);}
    latest.set(d.id,{p,text:e.text,cx,tags});
    rows.push([row.gameId,e.id,r,cx.L,cx.u,cx.eu,cx.king?1:0,cx.nearEnemy,cx.d3,p.kind,eg,tags.join(','),e.text.replace(/[\t\r\n]/g,' ')].join('\t'));
  }
  function action(d,e,r,c,body) {
    if(d.team!==us)return; const x=latest.get(d.id);
    if(!x){G.missingLabels++;return;}
    const p=x.p, a=e.action; const split=SPLITS.has(p.kind);
    if(split && a?.kind!=='split')G.labelActionMismatch++;
    if(p.kind==='move'&&(a?.kind!=='move'||a.steps.join('')!==p.dirs))G.labelActionMismatch++;
  }
  function split(p,ch,e,r,c){if(p.team===us)inc(G.splitActual,latest.get(p.id)?.p.kind||'unlabelled');}
  const ledger=perGame(R,{map:row.mapName,variant:row.mapName==='Prisoners Dilemma'&&R.match.map.initialDragons.length===10?'PD10':undefined},{turn,indicator,action,split});
  G.checks=ledger.chk; G.result=R.result;G.endReason=ledger.endReason;
  G.ledgerTurns=ledger[us].fl[FI.turns].reduce((s,v)=>s+v,0);
  G.finalKing=ledger[us].lin;
  G.maxInstr=0;G.faults=0;G.over80M=0;G.depths={};
  let ownIds=new Set(R.match.map.initialDragons.filter(d=>d.team===us).map(d=>d.id));
  for(const e of R.events){
    if(e.type==='dragonSplit'&&e.team===us)ownIds.add(e.childId);
    if(e.type==='dragonAction'&&ownIds.has(e.id)){G.maxInstr=Math.max(G.maxInstr,e.instructions?.count||0);G.over80M+=+(e.instructions?.count>8e7);G.faults+=!!(e.tle||e.instructions?.exceeded);}
    if(e.type==='sonarPing'&&e.senderId>255&&ownIds.has(e.senderId))G.sonarFromIdOver255++;
    if(e.type==='dragonIndicator'&&ownIds.has(e.id)){const p=parseInd(e.text);if(p.kind==='move')inc(G.depths,String(p.depth));}
  }
  fs.writeFileSync(path.join(OUT,`game-${row.gameId}.json`),JSON.stringify(G,null,2)+'\n');
  fs.appendFileSync(path.join(OUT,'turn-tags.tsv.gz'),zlib.gzipSync(rows.join('\n')+'\n'));
  return G;
}
function main(){
  const index=JSON.parse(fs.readFileSync(path.join(DIR,'index.json'))), games=[];
  const turnFile=path.join(OUT,'turn-tags.tsv.gz'); if(fs.existsSync(turnFile))throw Error('Counts already exist. Refuse to overwrite turn evidence.');
  fs.writeFileSync(turnFile,zlib.gzipSync('gameId\tdragonId\tround\tlength\townUnits\tenemyUnits\ttrueKing\tenemyHeadsInView\td3_all_enemies\tkind\texplicitGoal\ttags\tindicator\n'));
  for(const row of index.games){
    if(!fs.existsSync(path.join(DIR,'M'+row.gameId+'.replay')))throw Error('Missing replay '+row.gameId);
    games.push(one(row)); if(global.gc)global.gc();
    console.log(`${games.length}/${index.games.length} M${row.gameId}: ${games.at(-1).turns} turns, checks ${JSON.stringify(games.at(-1).checks)}`);
    // Cooperative one-second pause after each replay; no parallel workers or games.
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,1000);
  }
  const S={set:SET,games:games.length,turns:0,labelled:0,move:0,wins:0,draws:0,tags:{},kinds:{},splits:{},splitActual:{},explicitGoals:{},goalModifiers:{},cooccurrence:{},gateChecks:{},checks:{},depths:{},phases:{},lengths:{},missingLabels:0,duplicates:0,labelActionMismatch:0,unexpected:[],maxInstr:0,faults:0,over80M:0,priorityValues:[],resourceMin:{freeMemoryPct:100,freeDiskGB:Infinity},maxDragonId:0};
  const merge=(a,b)=>{for(const [k,v]of Object.entries(b))inc(a,k,v);};
  for(const g of games){
    ['turns','labelled','move','missingLabels','duplicates','labelActionMismatch','faults','over80M'].forEach(k=>S[k]+=g[k]);
    for(const k of ['tags','kinds','splits','splitActual','explicitGoals','goalModifiers','cooccurrence','checks','depths'])merge(S[k],g[k]);
    for(const [k,v] of Object.entries(g.gateChecks)){const x=S.gateChecks[k]||(S.gateChecks[k]={n:0,pass:0});x.n+=v.n;x.pass+=v.pass;}
    for(const [k,v]of Object.entries(g.phases)){const x=S.phases[k]||(S.phases[k]={turns:0,tags:{},goals:{},splits:{}});x.turns+=v.turns;merge(x.tags,v.tags);merge(x.goals,v.goals);merge(x.splits,v.splits);}
    for(const [k,v]of Object.entries(g.lengths)){const x=S.lengths[k]||(S.lengths[k]={turns:0,tags:{}});x.turns+=v.turns;merge(x.tags,v.tags);}
    S.wins+=g.winner===g.us;S.draws+=!g.winner;S.maxInstr=Math.max(S.maxInstr,g.maxInstr);S.unexpected.push(...g.unexpected);
    S.maxDragonId=Math.max(S.maxDragonId,g.maxDragonId);for(const k of Object.keys(S.resourceMin))S.resourceMin[k]=Math.min(S.resourceMin[k],g.resources[k]);
  }
  S.priorityValues=[...new Set(games.map(g=>g.priority))];
  S.submissions=[...new Set(games.map(g=>g.submission))]; S.nonEscapeSplits=Object.entries(S.splits).filter(([k])=>!k.startsWith('esc')).reduce((s,[,n])=>s+n,0);
  const pergame=KNOWN_TAGS.map(k=>{const arr=games.map(g=>g.tags[k]||0).sort((a,b)=>a-b),n=arr.reduce((s,v)=>s+v,0);return{tag:k,n,perGame:n/games.length,gamesWithTag:arr.filter(v=>v>0).length,median:(arr[34]+arr[35])/2,min:arr[0],max:arr.at(-1),turnShare:n/S.turns,moveShare:n/S.move};});
  S.tagSummary=pergame;
  fs.writeFileSync(path.join(OUT,'counts.json'),JSON.stringify(S,null,2)+'\n');
  fs.writeFileSync(path.join(OUT,'per-game.jsonl'),games.map(g=>JSON.stringify(g)).join('\n')+'\n');
  fs.writeFileSync(path.join(OUT,'tag-summary.tsv'),'tag\tcount\tper_game\tgames_with_tag\tmedian\tmin\tmax\tall_turn_share\tmove_share\n'+pergame.map(x=>[x.tag,x.n,x.perGame,x.gamesWithTag,x.median,x.min,x.max,x.turnShare,x.moveShare].join('\t')).join('\n')+'\n');
  fs.writeFileSync(path.join(OUT,'per-game-tags.tsv'),'gameId\tmap\topp\tus\tturns\t'+KNOWN_TAGS.join('\t')+'\n'+games.map(g=>[g.gameId,g.map,g.opp,g.us,g.turns,...KNOWN_TAGS.map(k=>g.tags[k]||0)].join('\t')).join('\n')+'\n');
  console.log(JSON.stringify({games:S.games,turns:S.turns,move:S.move,wins:S.wins,draws:S.draws,checks:S.checks,explicitGoals:S.explicitGoals,splits:S.splits,tags:S.tags,unknown:S.unexpected.length},null,2));
}
main();
