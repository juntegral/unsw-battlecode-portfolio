'use strict';process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path');const {makeLoader,viewerSource}=require('../../tools/top_features');const {perGame}=require('../../tools/mass_ledger');
const load=makeLoader(viewerSource()),A=JSON.parse(fs.readFileSync(__dirname+'/analysis.json')),V={sets:{},firstEvent:null};
for(const set of ['on','off']){const z={queenMulti:0,queenCompleted:0,updates:0,turns:0,unknownMap:0,unqualified:0,qualified:0};V.sets[set]=z;
for(const [key,a] of Object.entries(A.sets[set])){const side=key.split(':').at(-2),R=load(path.resolve(__dirname,set,'games',key.replace(/:/g,'_'),'game.replay')),inds=new Map(),bad=new Set(a.memoryDrift.map(d=>d.round+':'+d.id));
perGame(R,{map:'?',variant:'a',rules:'123'},{indicator(e){inds.set(e.id,e.text||'');},turn(d){if(d.team===side)z.turns++;},action(d,e,r){if(d.team!==side)return;const s=e.action?.kind==='move'?e.action.steps.length:0,ind=inds.get(d.id)||'';if(/map=(?!none\b)/.test(ind))z.unknownMap++;if(d.id===a.queen&&s>1){z.queenMulti++;if(!d.fate)z.queenCompleted++;}if(s>1&&!d.fate){z.updates+=s;if(set==='on'){const m=/\bbodyx(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)/.exec(ind);if(!m||+m[4]||+m[7]||bad.has(r+':'+d.id))z.unqualified++;else z.qualified++;}}}});
}}
fs.writeFileSync(__dirname+'/verification.json',JSON.stringify(V,null,2)+'\n');
const key='proxy4_king_default_small_A_1',skip=new Set(['dragonIndicator','dragonLog','debugDraw','engineLog']);
const events=set=>load(path.resolve(__dirname,set,'games',key,'game.replay')).events.filter(e=>!skip.has(e.type)).map(e=>Object.fromEntries(Object.entries(e).filter(([k])=>k!=='instructions').map(([k,v])=>[k,typeof v==='bigint'?String(v):v])));
const on=events('on'),off=events('off');let r=-1;
for(let i=0;i<Math.min(on.length,off.length);i++){if(on[i].type==='roundStart')r=on[i].round;if(JSON.stringify(on[i])!==JSON.stringify(off[i])){V.firstEvent={index:i,round:r,on:on[i],off:off[i]};break;}}
fs.writeFileSync(__dirname+'/verification.json',JSON.stringify(V,null,2)+'\n');console.log(JSON.stringify(V,null,2));
