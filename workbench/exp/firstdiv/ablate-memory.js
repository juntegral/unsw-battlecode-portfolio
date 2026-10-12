'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process'),data=require('./native-review.json'),out=[];
for(const r of data.rows.filter(r=>r.name==='bodymem')){
 const record={key:r.key,R:r.R,id:r.id,histories:{}};
 for(const [history,h]of Object.entries(r.histories)){
  const dir=path.join(__dirname,'native','bodymem',r.key.replace(/:/g,'_')),prefix=path.join(dir,history),file=prefix+'.override.tsv';
  const beliefs=h.models.off.beliefs;
  fs.writeFileSync(file,beliefs.map(b=>[b.id,b.head,b.length,b.minLength,+b.tailSeen,b.chain.length,...b.chain].join(' ')).join('\n')+'\n');
  const result=cp.spawnSync(path.join(__dirname,'native-bodymem-on'),[String(r.R),String(r.id),file],{input:fs.readFileSync(prefix+'.input','utf8'),encoding:'utf8',maxBuffer:128*1024**2});
  if(result.status!==0)throw Error(result.stderr);fs.writeFileSync(prefix+'.memory-override.jsonl',result.stdout);
  const target=result.stdout.trim().split('\n').map(JSON.parse).find(x=>x.round===r.R&&x.id===r.id);
  record.histories[history]={before:h.models.on.choice,off:h.models.off.choice,after:target.choice,flippedToOff:target.choice===h.models.off.choice,ownBodyUnchanged:JSON.stringify(target.body)===JSON.stringify(h.models.on.body),changedFields:'Dragon headT, estLen, minLen, tailSeen, chain replaced from OFF; same ON Planner and observed-input history; occupancy arrays retained',indicator:target.indicator};
 }
 out.push(record);console.log(r.key,record.histories.on.after,record.histories.off.after);
}
fs.writeFileSync(path.join(__dirname,'memory-ablation.json'),JSON.stringify({scope:'Native belief-field intervention only; not a production/judge fork',rows:out},null,2)+'\n');
