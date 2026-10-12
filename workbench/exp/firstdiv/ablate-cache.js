'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process'),data=require('./native-review.json'),out=[];
const run=(arm,args,input)=>{const p=cp.spawnSync(path.join(__dirname,'native-bodymem-'+arm),args,{input,encoding:'utf8',maxBuffer:128*1024**2});if(p.status!==0)throw Error(p.stderr);return p.stdout;};
for(const r of data.rows.filter(r=>r.name==='bodymem')){
 const record={key:r.key,R:r.R,id:r.id,histories:{}};
 for(const [history,h]of Object.entries(r.histories)){
  const dir=path.join(__dirname,'native','bodymem',r.key.replace(/:/g,'_')),prefix=path.join(dir,history),input=fs.readFileSync(prefix+'.input','utf8'),args=[String(r.R),String(r.id)];
  const target=text=>text.trim().split('\n').map(JSON.parse).find(x=>x.round===r.R&&x.id===r.id);
  const models={};for(const arm of ['on','off']){const text=run(arm,args,input);fs.writeFileSync(prefix+'.cache.'+arm+'.jsonl',text);models[arm]=target(text);}
  fs.writeFileSync(prefix+'.override.tsv.cache.tsv',[models.off.cache.fresh.join(' '),...models.off.cache.tiles.map(x=>x.join(' '))].join('\n')+'\n');
  const text=run('on',[...args,prefix+'.override.tsv'],input);fs.writeFileSync(prefix+'.memory-cache-override.jsonl',text);const result=target(text);
  const changedTiles=models.on.cache.tiles.map((a,i)=>({tile:i,on:a,off:models.off.cache.tiles[i]})).filter(x=>JSON.stringify(x.on)!==JSON.stringify(x.off));
  record.histories[history]={before:models.on.choice,off:models.off.choice,after:result.choice,flippedToOff:result.choice===models.off.choice,ownBodyUnchanged:JSON.stringify(result.body)===JSON.stringify(models.on.body),changedTiles,freshBefore:models.on.cache.fresh,freshOff:models.off.cache.fresh,indicator:result.indicator};
 }
 out.push(record);console.log(r.key,record.histories.on.before+' -> '+record.histories.on.after,record.histories.off.before+' -> '+record.histories.off.after);
}
fs.writeFileSync(path.join(__dirname,'memory-cache-ablation.json'),JSON.stringify({scope:'Native belief/occupancy/fresh-ally cache intervention only; same ON code, forced past actions and observations; no production judge-clock fork.',rows:out},null,2)+'\n');
