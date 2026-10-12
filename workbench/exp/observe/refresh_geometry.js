'use strict';
const fs=require('fs'),path=require('path'),z=require('zlib'),readline=require('readline'),crypto=require('crypto'),cp=require('child_process'),L=require('./lib');
const O=__dirname,input=path.join(O,'games.jsonl.gz'),output=path.join(O,'games-refreshed.jsonl.gz');
function guard(){const d=cp.execFileSync('df',['-k',L.ROOT],{encoding:'utf8'}).trim().split('\n').pop().split(/\s+/),m=/System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure',['-Q'],{encoding:'utf8'}));return +d[3]/1048576>=21&&m&&+m[1]>=10;}
(async()=>{
 if(fs.existsSync(output))throw Error('review existing refresh output before re-run');let n=0;
 for await(const line of readline.createInterface({input:fs.createReadStream(input).pipe(z.createGunzip()),crlfDelay:Infinity})){
  while(!guard()){console.log('RESOURCE PAUSE');await new Promise(r=>setTimeout(r,30000));}
  const row=JSON.parse(line),f=path.join(O,'raw',crypto.createHash('sha256').update(row.key).digest('hex').slice(0,20)+'.json.gz'),a=JSON.parse(z.gunzipSync(fs.readFileSync(f))),A=L.atlas(a.M,a.gap);
  for(const [r,c]of Object.entries(row.cp))for(const t of 'AB'){
   const v=c.teams[t],seen=Uint8Array.from(Buffer.from(v.seenMask,'base64')),K={seen,list:Array.from(seen,(v,k)=>v?k:-1).filter(k=>k>=0),mask:v.mask};v.geometry=L.geometryStats(A,K,t);
   if(v.dynamicMask!==null){const D={...K,mask:v.dynamicMask};v.dynamicGeometry=L.geometryStats(A,D,t).mirrored;v.dynamicSpawnMirrored=L.sum(Array.from(L.expanded(A,D),(q,k)=>q*A.spawn[k]));v.dynamicFountainMirrored=L.sum(Array.from(L.expanded(A,D),(q,k)=>q*A.fount[k]));}
   a.cp[r].teams[t]=v;
  }
  fs.writeFileSync(f,z.gzipSync(JSON.stringify(a),{level:6}));fs.appendFileSync(output,z.gzipSync(JSON.stringify(row)+'\n',{level:6}));if(++n%100===0)console.log('refresh',n);
 }
 fs.renameSync(output,input);console.log('DONE refresh',n);
})().catch(e=>{console.error(e);process.exitCode=1;});
