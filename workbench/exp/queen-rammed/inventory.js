'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'../..'),read=f=>JSON.parse(fs.readFileSync(path.join(ROOT,f))),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const evidence=read('exp/queen-rammed/build-identity.json'),qt=read('exp/q-analysis/tables.json');
const specs=[];
for(const base of ['exp/q2','exp/v16/q1','exp/q2box','exp/qsight','exp/q1c','exp/freecost'])for(const f of fs.readdirSync(path.join(ROOT,base)).filter(f=>/^spec.*\.json$/.test(f))){try{const s=read(base+'/'+f);if(Array.isArray(s))specs.push(...s.map(x=>({...x,spec:base+'/'+f})));}catch{}}
const dirs=new Set([...Object.keys(qt.games),...fs.readdirSync(path.join(ROOT,'exp/q2')).filter(f=>f.startsWith('cand4-')).map(f=>'exp/q2/'+f)]);
for(const p of ['q2box','qsight','q1c','freecost'])for(const f of ['off','on','b','c','self','id-off','id-base'])if(fs.existsSync(path.join(ROOT,`exp/${p}/${f}/rows.jsonl`)))dirs.add(`exp/${p}/${f}`);
const manifest=[],tasks=[],bad=[];
for(const dir of [...dirs].sort()){
 const rf=path.join(ROOT,dir,'rows.jsonl');if(!fs.existsSync(rf))continue;
 const latest=new Map(),lines=fs.readFileSync(rf,'utf8').split('\n').filter(Boolean);let rejected=0;
 for(const [i,l]of lines.entries()){let r;try{r=JSON.parse(l);}catch{bad.push({dir,line:i+1,reason:'invalid JSON'});continue;}if(r.exit!==0||r.G===undefined||r.error||r.botProblem){rejected++;bad.push({dir,line:i+1,key:r.key,reason:r.error||r.botProblem||r.exit});}else latest.set(r.key,{...r,sourceLine:i+1});}
 const lanes=specs.filter(s=>s.out===dir);const bot=lanes[0]?.bot||null;let ref=null;
 if(dir.startsWith('exp/q2box/'))ref=`exp/q2box/compiled/${path.basename(dir)==='id-base'?'base':path.basename(dir)==='id-off'?'off':path.basename(dir)}.wasm`;
 if(dir.startsWith('exp/freecost/'))ref=`exp/freecost/compiled/${path.basename(dir)==='id-base'?'base':path.basename(dir)==='id-off'?'off':path.basename(dir)}.wasm`;
 if(dir.startsWith('exp/q1c/'))ref=`exp/q1c/compiled/${path.basename(dir)==='id-base'?'base':path.basename(dir)==='id-off'?'off':path.basename(dir)==='self'?'on':path.basename(dir)}.wasm`;
 if(dir.startsWith('exp/qsight/'))ref=`exp/qsight/compiled/${path.basename(dir)==='id-base'?'base':path.basename(dir)==='id-off'?'off':path.basename(dir)}.wasm`;
 const build=ref&&evidence.references[ref];const role=build?.equalsCurrent?'main':'side';
 let reason=build?(build.equalsCurrent?'official WASM bytes equal current default':'official WASM bytes differ from current default'):'older Q2/Q1 lineage, before Q2BOX (and/or before current Q1/Q1B defaults)';
 const params=bot&&fs.existsSync(path.join(ROOT,bot,'params.hpp'))?Object.fromEntries([...fs.readFileSync(path.join(ROOT,bot,'params.hpp'),'utf8').matchAll(/constexpr bool\s+((?:Q1|Q2|FREECOST)[A-Z0-9_]*ON)\s*=\s*(true|false)/g)].map(m=>[m[1],m[2]==='true'])):null;
 let kept=0;
 for(const row of latest.values()){
  const file=dir+'/games/'+row.key.replace(/:/g,'_')+'/game.replay';if(!fs.existsSync(path.join(ROOT,file))){bad.push({dir,key:row.key,reason:'missing replay'});continue;}
  if(!['proxy4_king','bot-hunter'].includes(path.basename(row.opp))){bad.push({dir,key:row.key,reason:'nonrequested opponent (self probe)'});continue;}
  kept++;const lane=lanes.find(s=>s.opps.some(o=>path.basename(o)===path.basename(row.opp))&&s.seeds.includes(row.seed)&&s.sides.includes(row.side)&&(!s.only||s.only.includes(row.map)));
  const mapfile=lane?lane.maps+'/'+row.map+'.map':null;
  tasks.push({dir,key:row.key,file,row,role,buildSha256:build?.sha256||null,bot,mapfile,sourceSpec:lane?.spec||null,stratum:/flip/.test(row.map)?'id-flip':/^gen_/.test(row.map)?'generated':['arena','Colosseum','big_empty','default_small','stronghold'].includes(row.map)?'bundled':'online-or-sprint'});
 }
 manifest.push({dir,bot,role,reason,ref,buildSha256:build?.sha256||null,rawLines:lines.length,cleanKeys:latest.size,selected:kept,rejected,specs:[...new Set(lanes.map(x=>x.spec))],switches:params});
}
const out={frozenAt:new Date().toISOString(),currentBuild:evidence.current,selection:'last clean row per key; requested opponents only; no fresh games',manifest,tasks,bad};
fs.writeFileSync(path.join(__dirname,'inventory.json'),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({sets:manifest.length,mainSets:manifest.filter(x=>x.role==='main').map(x=>[x.dir,x.selected]),mainRows:tasks.filter(x=>x.role==='main').length,sideRows:tasks.filter(x=>x.role==='side').length,bad:bad.length},null,2));
