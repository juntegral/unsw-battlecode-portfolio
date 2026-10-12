#!/usr/bin/env node
'use strict';
const L=require('./lib'),{fs,path,ROOT,EXISTING,read,mapFiles,metrics,hash}=L;
function census() {
 const seen=new Map();const maps=mapFiles(EXISTING).map(file=>{const m=read(file),sha=hash(m),duplicateOf=seen.get(sha)||null;if(!duplicateOf)seen.set(sha,file);return {file,name:m.name,sha256:sha,symlink:fs.lstatSync(path.resolve(ROOT,file)).isSymbolicLink(),duplicateOf,...metrics(m)};});
 const keys=['width','height','area','extremeAspect','kelpDensity','corridorDegree2Share','deadEnds','pocketTiles','portalPairCount','spawnShare','fountainShare','supply','centreSupplyShare','pocketSupplyShare','startDistance'];
 const envelope=Object.fromEntries(keys.map(k=>{const a=maps.filter(m=>!m.duplicateOf&&m[k]!==null).map(m=>m[k]);return[k,{min:Math.min(...a),max:Math.max(...a)}];}));
 return {createdAt:new Date().toISOString(),purpose:'기제 점검용 지도 전수조사. 승패 판정 없음.',definitions:{edges:'2*area toroidal canonical edges; opposite boundary aliases merged',corridorWidth:'min(horizontal open run, vertical open run), portals terminate runs; every tile counted',pocket:'complement of undirected 2-core, including isolated tiles (same as exp/spatial/lib.js)',supply:'sum(2/(minGap+maxGap)) over spawning tiles',centre:'0.4 <= dA/(dA+dB) < 0.6, BFS from ALL initial body segments, same as exp/spatial/lib.js',fountain:'meanGap <= 12',startDistance:'minimum head-to-head BFS, portals included',envelope:'coordinatewise min/max over unique maps; not a joint distribution or organiser forecast'},fileCount:maps.length,uniqueCount:seen.size,envelope,maps};
}
if(require.main===module){const out=path.join(ROOT,'exp/mapgen');fs.mkdirSync(out,{recursive:true});const c=census();fs.writeFileSync(path.join(out,'census.json'),JSON.stringify(c,null,2)+'\n');console.log(JSON.stringify({files:c.fileCount,unique:c.uniqueCount,envelope:c.envelope}));}
module.exports={census};
