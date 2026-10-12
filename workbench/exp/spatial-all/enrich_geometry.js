// Add all spawn tiles to the static tables, including maps with no <=12-gap fountains.
'use strict';
const fs=require('fs'),path=require('path'),S=require('./lib'),O=path.join(__dirname,'cache');
const P=JSON.parse(fs.readFileSync(path.join(O,'population.json'),'utf8')),tasks=new Map(P.tasks.map(t=>[t.key,t])),rows=[...new Map(S.readl(path.join(O,'games.jsonl')).map(r=>[r.key,r])).values()],seen=new Set();
for(const r of rows){if(seen.has(r.geometry))continue;seen.add(r.geometry);const t=tasks.get(r.key),R=S.raw.load(t.file),g=S.geometry(R.match.map,r.map,r.layout);fs.writeFileSync(path.join(O,'geometry-'+g.signature+'.json'),JSON.stringify(S.geometryJSON(g,r.map,r.layout)));}
console.log('enriched geometries',seen.size);
