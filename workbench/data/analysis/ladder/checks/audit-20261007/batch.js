// node batch.js <shard> <of> : recount every ladder game in this shard, one JSON line each
const fs=require('fs'),path=require('path');const {recount}=require('./recount.js');
const RAW='~/01. Project/개인 프로젝트/unsw-swarm/data/online/ladder';
const [shard,of]=process.argv.slice(2).map(Number);
const out=fs.createWriteStream(path.join(__dirname,`recount-${shard}.jsonl`));
let n=0;
for(const b of fs.readdirSync(RAW).filter(x=>/^\d+$/.test(x)).sort()){
  for(const f of fs.readdirSync(path.join(RAW,b)).filter(x=>/^game-\d+\.json$/.test(x)).sort()){
    const j=JSON.parse(fs.readFileSync(path.join(RAW,b,f)));
    if(j.id%of!==shard)continue;
    const ours=j.teamAId===1119?'A':'B';
    let r;try{r=recount(path.join(RAW,b,`M${j.id}.replay`),ours);}catch(e){r={error:String(e.message)};}
    out.write(JSON.stringify({game:j.id,battle:Number(b),ours,...r})+'\n');n++;
  }
}
out.end(()=>console.log('shard',shard,'done',n));
