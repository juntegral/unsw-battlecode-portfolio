'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path'),cp=require('child_process');
const ROOT=path.resolve(__dirname,'../..'),out={scope:'Native same-observation diagnostics; recorded past moves forced; no judge clock or RNG restoration.',rows:[]};
function run(cmd,args,options={}){const r=cp.spawnSync(cmd,args,{cwd:ROOT,encoding:'utf8',maxBuffer:128*1024**2,...options});if(r.status!==0)throw Error(cmd+' '+r.stderr);return r.stdout;}
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
for(const name of ['bodymem','bodyx','freecost','qsight']){
 const data=JSON.parse(fs.readFileSync(path.join(__dirname,name+'.json')));
 for(const row of data.rows.filter(r=>r.status==='matched'&&([1,3,10].some(k=>r.classification[k]==='harm')||[10,50].some(k=>r.queen.classification[k]==='harm')))){
  const review={name,key:row.key,R:row.R,id:row.id,production:{on:row.actions.on.text,off:row.actions.off.text},histories:{}};
  const dir=path.join(__dirname,'native',name,row.key.replace(/:/g,'_'));fs.mkdirSync(dir,{recursive:true});
  for(const history of ['on','off']){
   const prefix=path.join(dir,history);
   run(process.execPath,[path.join(__dirname,'native-input.js'),row.files[history],row.side,prefix,String(row.id),String(row.R)]);
   const meta=JSON.parse(fs.readFileSync(prefix+'.meta.json')),input=fs.readFileSync(prefix+'.input','utf8'),models={};
   for(const arm of ['on','off']){
    const text=run(path.join(__dirname,'native-'+name+'-'+arm),[],{input});fs.writeFileSync(prefix+'.'+arm+'.jsonl',text);
    const rs=text.trim().split('\n').filter(Boolean).map(JSON.parse);if(rs.length!==meta.snapshots.length)throw Error('native count');
    const r=rs.find(x=>x.round===row.R&&x.id===row.id);if(!r)throw Error('missing target');
    const ownProduction=review.production[history],normalized=ownProduction.startsWith('SPLIT:')?'split'+ownProduction.slice(6):ownProduction;
    models[arm]={...r,reproduced:r.choice===normalized,pastTurns:rs.length-1,pastReproduced:rs.slice(0,-1).filter((x,i)=>x.choice===meta.snapshots[i].actual).length};
   }
   const beliefs={};for(const arm of ['on','off'])for(const b of models[arm].beliefs){if(!beliefs[b.id])beliefs[b.id]={};beliefs[b.id][arm]=b;}
   review.histories[history]={uncertain:meta.uncertain,actualBody:meta.snapshots.find(x=>x.round===row.R&&x.id===row.id).body,models,
    ownBodyDifference:!eq(models.on.body,models.off.body),beliefDifferences:Object.values(beliefs).filter(b=>!eq(b.on,b.off)),choiceDifference:models.on.choice!==models.off.choice};
  }
  const n=review.histories.on.models.on,f=review.histories.off.models.off;
  const beliefs={};for(const [arm,m]of [['on',n],['off',f]])for(const b of m.beliefs){if(!beliefs[b.id])beliefs[b.id]={};beliefs[b.id][arm]=b;}
  review.actualArmMemory={ownBodyDifference:!eq(n.body,f.body),beliefDifferences:Object.values(beliefs).filter(b=>!eq(b.on,b.off))};
  out.rows.push(review);console.log(name,row.key,Object.fromEntries(Object.entries(review.histories).map(([k,v])=>[k,{on:v.models.on.choice,off:v.models.off.choice,ownBodyDifference:v.ownBodyDifference,beliefDifferences:v.beliefDifferences.length}])));
 }
}
fs.writeFileSync(path.join(__dirname,'native-review.json'),JSON.stringify(out,null,2)+'\n');
