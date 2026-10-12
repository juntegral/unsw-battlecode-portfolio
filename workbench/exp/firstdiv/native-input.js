#!/usr/bin/env node
'use strict';
process.env.UNSW_RULES = '123';
const fs=require('fs'),path=require('path'),cp=require('child_process');
const {makeLoader,viewerSource}=require('../../tools/top_features');
const {perGame}=require('../../tools/mass_ledger');
const load=makeLoader(viewerSource()),[file,side,prefix,ids,lastRound]=process.argv.slice(2);
if(!file||!side||!prefix)throw Error('usage: node exp/bodymem/replay.js REPLAY A|B OUT_PREFIX [id,id,...]');
const wanted=ids?new Set(ids.split(',').map(Number)):null,R=load(file),M=R.match.map,W=M.width,H=M.height;
const wrap=(v,n)=>(v%n+n)%n,dirs='NESW',actions=new Map(),inds=new Map(),sonars=new Map();
let r=-1;for(const e of R.events){if(e.type==='roundStart')r=e.round;if(e.type==='dragonAction')actions.set(`${r}:${e.id}`,e.action);if(e.type==='dragonIndicator')inds.set(`${r}:${e.id}`,e.text);if(e.type==='sonarPing'){const k=`${r}:${e.senderId}`;if(!sonars.has(k))sonars.set(k,[]);sonars.get(k).push(e);}}
const portal=new Map();for(const[pid,ends]of(M.portals||[]).entries())for(const e of ends){let{x,y}=e,s=e.side;if(s==='S'){y=wrap(y+1,H);s='N';}if(s==='E'){x=wrap(x+1,W);s='W';}portal.set(`${x},${y},${s}`,M.portalLabels?.[pid]??pid);}
function edge(x,y,s){x=wrap(x,W);y=wrap(y,H);const pid=portal.get(`${x},${y},${s}`),kelp=s==='N'?(M.initialHEdges[y*W+x]===1||(y===0&&M.initialHEdges[H*W+x]===1)):(M.initialVEdges[y*(W+1)+x]===1||(x===0&&M.initialVEdges[y*(W+1)+W]===1));return pid??(kelp?-2:-1);}
let pos=0,rr=-1;const facing=new Map(M.initialDragons.map(d=>[d.id,d.facing])),pending=new Map(),echo=new Map(),countdown=new Map();
function advance(id,round){while(pos<R.events.length){const e=R.events[pos++];if(e.type==='roundStart')rr=e.round;if(e.type==='pearlCountdown')countdown.set(e.tile.y*W+e.tile.x,{r:rr,v:e.countdown});if(e.type==='dragonUpdate')facing.set(e.id,e.facing);if(e.type==='dragonSplit')facing.set(e.childId,e.childFacing);if(e.type==='sonarPing'){if(e.hitId!==undefined){if(!pending.has(e.hitId))pending.set(e.hitId,[]);pending.get(e.hitId).push(String(e.value64));}if(!echo.has(e.senderId))echo.set(e.senderId,[]);echo.get(e.senderId).push(e);}if(e.type==='turnStart'&&e.id===id&&rr===round)break;}}

const lines=[`${W} ${H} ${M.unitLimit||64} ${side}`],snapshots=[],uncertain={missingCountdown:0,ambiguousFacing:0};
const ledger=perGame(R,{map:'?',rules:'123'},{turn(d,round,c){
 advance(d.id,round);const msgs=pending.get(d.id)||[],echoes=echo.get(d.id)||[];pending.delete(d.id);echo.delete(d.id);
 if(d.team!==side||wanted&&!wanted.has(d.id)||round>Number(lastRound))return;
 const action=actions.get(`${round}:${d.id}`)||{},move=action.kind==='move'?action.steps.join(''):'-',split=action.kind==='split'?action.childSegmentCount:0;
 const values=[d.id,round,d.body.length,dirs.indexOf(facing.get(d.id)||'N'),[...c.drag.values()].filter(o=>o.team===side).length,msgs.length,...msgs];
 values.push(...['kelp','ally','allyHead','enemy','enemyHead'].map(kind=>echoes.filter(e=>e.hitKind===kind).length));
 const center=d.body[0];for(let dy=-3;dy<=3;dy++)for(let dx=-3;dx<=3;dx++){const x=wrap(center.x+dx,W),y=wrap(center.y+dy,H),k=y*W+x,v=countdown.get(k);if(!v)uncertain.missingCountdown++;values.push(x,y,+c.pearls.has(k),v?Math.max(-1,v.v-(round-v.r)):-1);}
 const parts=[];for(const o of c.drag.values())o.body.forEach((p,i)=>{if(c.cheb(center,p)>3)return;let dir=facing.get(o.id)||'N';if(i){const prev=o.body[i-1],options=[...dirs].filter(dir=>{const t=c.across(p.x,p.y,dir);return t&&t.x===prev.x&&t.y===prev.y;});if(options.length!==1)uncertain.ambiguousFacing++;dir=options[0]||dir;}parts.push([o.team,o.id,p.x,p.y,dirs.indexOf(dir),+(i===0)]);});values.push(parts.length,...parts.flat());
 for(let y=-3;y<=4;y++)for(let x=-3;x<=3;x++)values.push(edge(center.x+x,center.y+y,'N'));
 for(let y=-3;y<=3;y++)for(let x=-3;x<=4;x++)values.push(edge(center.x+x,center.y+y,'W'));
 const rays=sonars.get(`${round}:${d.id}`)||[],lastDir=rays.length===1?dirs.indexOf(rays[0].direction):-2,lastFrom=rays.length===1?rays[0].origin.y*W+rays[0].origin.x:-1;
 values.push(move||'-',split,lastDir,lastFrom);lines.push(values.join(' '));
 snapshots.push({round,id:d.id,actual:split?'split'+split:move,indicator:inds.get(`${round}:${d.id}`)||'',body:d.body.map(p=>c.key(p.x,p.y))});
}});
fs.mkdirSync(path.dirname(prefix),{recursive:true});fs.writeFileSync(prefix+'.input',lines.join('\n')+'\n');
fs.writeFileSync(prefix+'.meta.json',JSON.stringify({file,side,checks:ledger.chk,uncertain,snapshots},null,2)+'\n');
