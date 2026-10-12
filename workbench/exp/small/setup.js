'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process');
const S=require('../spatial/lib'),ROOT=S.ROOT,OUT=__dirname;
const readl=f=>fs.existsSync(f)?fs.readFileSync(f,'utf8').split('\n').filter(Boolean).map(JSON.parse):[];
function resource(){const s=cp.execFileSync('memory_pressure',['-Q'],{encoding:'utf8'}),m=/System-wide memory free percentage:\s*(\d+)%/.exec(s),d=fs.statfsSync(ROOT);return {at:cp.execFileSync('date',['+%Y-%m-%d %H:%M:%S %Z'],{encoding:'utf8'}).trim(),memoryFreePercent:m?+m[1]:null,diskFreeGiB:Number(d.bavail)*Number(d.bsize)/2**30};}
function guard(){const r=resource();if(r.memoryFreePercent===null||r.memoryFreePercent<10||r.diskFreeGiB<21)throw Error('RESOURCE PAUSE '+JSON.stringify(r));return r;}
function main(){
 const tasks=[],missing=[],seen=new Set(),known=new Set(Object.keys(S.MAPS));
 function add(t){if(seen.has(t.key))return;seen.add(t.key);if(fs.existsSync(t.file))tasks.push(t);else missing.push(t);}
 for(const set of ['v12-F-H','v12-S-H','v12-F-K','v12-S-K'])for(const r of readl(path.join(ROOT,'exp/gen',set,'rows.jsonl'))){if(!['arena','Colosseum','default_small','trophy'].includes(r.map))continue;add({...r,key:set+':'+r.key,src:'local',set,us:r.side,map:r.map==='trophy'?'Trophy':r.map,recognition:'off',file:path.join(ROOT,'exp/gen',set,'games',`${r.opp}_${r.map}_${r.side}_${r.seed}`,'game.replay')});}
 // Matched recognized v1.2 seed 1-2 reference, not opening/hold candidates.
 for(const [dir,set]of [['exp/v12','e-v12'],['exp/v14','v12-a2']])for(const r of readl(path.join(ROOT,dir,set,'rows.jsonl'))){if(r.map!=='trophy'||r.seed>2)continue;add({...r,key:'recognized:'+r.key,src:'local',set:'v12-recognized',us:r.side,map:'Trophy',recognition:'on',file:path.join(ROOT,dir,set,'games',`${r.opp}_${r.map}_${r.side}_${r.seed}`,'game.replay')});}
 const onlineSets=[...S.WAVE,'v1-w1','v1-w2','v1-w3'];
 for(const set of onlineSets){const p=path.join(ROOT,'data/online',set,'index.json');if(!fs.existsSync(p)){missing.push({set,reason:'index absent'});continue;}for(const r of JSON.parse(fs.readFileSync(p,'utf8')).games){if(r.mapName!=='Trophy')continue;add({...r,key:set+':'+r.gameId,src:'online',set,us:r.ourSide.toUpperCase(),map:r.mapName,file:path.join(ROOT,'data/online',set,'M'+r.gameId+'.replay')});}}
 const top=readl(path.join(ROOT,'data/top/index.jsonl')),elite=readl(path.join(ROOT,'data/elite/index.jsonl'));
 const topUnique=[...new Map(top.map(r=>[r.battleId+':'+r.gameId,r])).values()],eliteUnique=[...new Map(elite.map(r=>[r.battleId+':'+r.gameId,r])).values()];
 for(const r of topUnique.filter(r=>r.map==='Trophy'))add({...r,key:'top:'+r.battleId+':'+r.gameId,src:'top',file:path.join(ROOT,'data/top',String(r.battleId),r.gameId+'.replay.gz')});
 const unknown=eliteUnique.filter(r=>!known.has(r.map));
 for(const r of eliteUnique.filter(r=>r.map==='Trophy'||!known.has(r.map))){const overlap=topUnique.some(t=>t.gameId===r.gameId);if(overlap)continue;add({...r,key:'elite:'+r.battleId+':'+r.gameId,src:'elite',file:path.join(ROOT,'data/elite',String(r.battleId),r.gameId+'.replay.gz')});}
 const battleOnly=[];for(const dir of fs.readdirSync(path.join(ROOT,'data/elite'),{withFileTypes:true})){if(!dir.isDirectory())continue;const f=path.join(ROOT,'data/elite',dir.name,'battle.json');if(!fs.existsSync(f))continue;const b=JSON.parse(fs.readFileSync(f));for(const g of b.games||[]){if(eliteUnique.some(r=>r.gameId===g.id))continue;const r={battleId:+dir.name,gameId:g.id,map:g.mapName,winner:g.winner,teamA:b.teamAName,teamB:b.teamBName,rankA:b.ranks?.a?.rank??null,rankB:b.ranks?.b?.rank??null,at:b.at,metadataSource:'battle.json; index absent'};battleOnly.push(r);if((r.map==='Trophy'||!known.has(r.map))&&!topUnique.some(t=>t.gameId===g.id))add({...r,key:'elite:'+r.battleId+':'+r.gameId,src:'elite',file:path.join(ROOT,'data/elite',dir.name,g.id+'.replay.gz')});}}
 const p={frozenAt:resource().at,tasks,missing,onlineSets,top:{indexRows:top.length,uniqueGames:topUnique.length,trophy:topUnique.filter(r=>r.map==='Trophy').length},elite:{indexRows:elite.length,uniqueGames:eliteUnique.length,maps:Object.fromEntries([...new Set(eliteUnique.map(r=>r.map))].sort().map(m=>[m,eliteUnique.filter(r=>r.map===m).length])),unknownGames:unknown,battleOnlyGames:battleOnly},resources:guard()};
 // First deliverable: initial census before extraction, later filled by aggregate.js.
 fs.writeFileSync(path.join(OUT,'tables.json'),JSON.stringify({status:'census; extraction pending',createdAt:p.frozenAt,population:p,definitions:{round:'replay round (zero-based)',turnHook:'turnStart before action'}},null,2));
 fs.writeFileSync(path.join(OUT,'population.json'),JSON.stringify(p,null,2));
 console.log(JSON.stringify({tasks:tasks.length,sources:Object.fromEntries([...new Set(tasks.map(t=>t.src))].map(s=>[s,tasks.filter(t=>t.src===s).length])),top:p.top,elite:p.elite,missing:missing.length,resources:p.resources}));
}
module.exports={readl,guard,resource,ROOT,OUT};if(require.main===module)main();
