'use strict';
// Stage 3 only: selection.json must already exist. No adaptive selection.
const fs=require('fs'),cp=require('child_process');
const {load}=require('../../tools/replay.js'),ML=require('../../tools/mass_ledger.js');
const base='.cache/outcome-review';
if(!process.argv.includes('--allow-inherited-10'))throw Error('Awaiting resource exception');
const selection=JSON.parse(fs.readFileSync(base+'/selection.json','utf8'));
const all=new Map(fs.readFileSync(base+'/games.jsonl','utf8').trim().split('\n').map(l=>{const r=JSON.parse(l);return[r.key,r];}));
const out=fs.openSync(base+'/deep.jsonl','wx'),sum=a=>a.reduce((s,x)=>s+x,0);
for(const sel of selection.games){
 const mem=cp.execFileSync('/usr/bin/memory_pressure',[],{encoding:'utf8'}),pct=+(/System-wide memory free percentage:\s*(\d+)%/.exec(mem)||[])[1];
 const disk=+cp.execFileSync('/bin/df',['-g','/'],{encoding:'utf8'}).trim().split('\n').at(-1).trim().split(/\s+/)[3];
 if(pct<10||disk<20)throw Error('PAUSE resource threshold');
 const g=all.get(sel.key),R=load(sel.file),us=g.ourSide,en=us==='A'?'B':'A';
 const info={map:g.map};if(g.map==='Prisoners Dilemma')info.variant=R.match.map.initialDragons.length===10?'PD10':'PD6';
 const checkpoints=[],turns=new Map(),labels=new Map(),events=[],parents=new Map(),born=new Map(),deaths=[];
 let round=-1,final={};
 const m=ML.perGame(R,info,{
  turn(d,r,c){
   if(round!==r){round=r;if(r%10===0){const row={r};for(const tm of[us,en]){const k=c.kingOf(tm),ds=[...c.drag.values()].filter(x=>x.team===tm);row[tm]={heads:ds.length,total:sum(ds.map(x=>x.body.length)),king:k?.body.length||0,kid:k?.id??-1,head:k?{...k.body[0]}:null};}checkpoints.push(row);}}
   const free=[];for(const dir of['N','E','S','W']){const n=c.across(d.body[0].x,d.body[0].y,dir);if(n&&!c.occ.has(c.key(n.x,n.y)))free.push({dir,...n});}
   turns.set(d.id,{r,len:d.body.length,head:{...d.body[0]},free,isKing:c.isKingNow(d),nearest:[...c.drag.values()].filter(x=>x.team!==d.team).map(x=>({id:x.id,len:x.body.length,d:c.tdist(d.body[0],x.body[0])})).sort((a,b)=>a.d-b.d||a.id-b.id).slice(0,2)});
  },
  indicator(e,r,c){labels.set(e.id,e.text||'');},
  action(d,e,r,c,before){const t=turns.get(d.id);if(t){t.action=e.action;t.label=labels.get(d.id)||null;}},
  eat(d,tile,origin,r,c){const rec=origin>=0?c.deaths[origin]:null;
   const ev={type:'eat',r,id:d.id,team:d.team,origin:rec?rec.team===d.team?(rec.cause===0?'own-sac':'own-other'):'enemy-drop':'natural',deathIndex:origin,tile:{x:tile%c.W,y:Math.floor(tile/c.W)}};events.push(ev);
   if(origin>=0){const x=deaths[origin];if(x){x.eaters.push({r,id:d.id,team:d.team});}}
  },
  split(p,ch,e,r,c){parents.set(ch.id,p.id);born.set(ch.id,r);events.push({type:'split',r,id:p.id,child:ch.id,team:p.team,parentKept:e.parentBody.length,childLength:e.childBody.length});},
  death(d,rec,idx,other,r,c){const t=turns.get(d.id)||{};const x={type:'death',r,id:d.id,team:d.team,cause:ML.CAUSE[rec.cause],len:rec.len,drops:rec.drops,isKing:rec.king,otherId:other?.id??null,otherLength:other?.body.length??null,turn:t,eaters:[]};deaths[idx]=x;events.push(x);},
  end(rounds,c){for(const tm of[us,en]){const k=c.kingOf(tm);final[tm]={kid:k?.id??-1,len:k?.body.length||0,heads:[...c.drag.values()].filter(x=>x.team===tm).length};}}
 });
 const lines={};for(const tm of[us,en]){let id=final[tm].kid;const ids=[];while(id>=0){ids.push(id);id=parents.get(id)??-1;}lines[tm]=ids.reverse().map(id=>({id,born:born.get(id)||0}));}
 const lineIds=new Set(Object.values(lines).flat().map(x=>x.id));
 const significantDeaths=deaths.filter(x=>x&&(x.isKing||x.turn.isKing&&x.len>=8||x.cause==='fault'||x.r>=g.rounds-3));
 const interesting=events.filter(x=>x.type==='eat'?lineIds.has(x.id)&&x.r>=250:x.type==='split'?lineIds.has(x.child)&&x.r>=250:significantDeaths.includes(x));
 const row={key:g.key,id:g.id,map:g.map,opponent:g.opponent,outcome:g.outcome,selection:sel.reasons,rounds:m.rounds,checkpoints,lines,final,significantDeaths,events:interesting,chk:m.chk};
 fs.writeSync(out,JSON.stringify(row)+'\n');console.log('deep-read '+g.key+' '+sel.reasons.join(', ')+' checks='+JSON.stringify(m.chk));
}
fs.closeSync(out);
