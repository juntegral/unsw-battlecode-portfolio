'use strict';
const fs=require('fs'),z=require('zlib'),rl=require('readline'),L=require('./lib');
(async()=>{const out={N:0,byEvidence:{},bothUnsupported:[]};for await(const s of rl.createInterface({input:fs.createReadStream('exp/opening/games.jsonl.gz').pipe(z.createGunzip()),crlfDelay:Infinity})){if(!s)continue;const r=JSON.parse(s);if(r.src!=='local')continue;out.N++;const a=r.layoutEvidence;out.byEvidence[a.evidence]=(out.byEvidence[a.evidence]||0)+1;if(a.ca>0&&a.cb>0)out.bothUnsupported.push({key:r.key,map:r.map,layout:r.layout,ca:a.ca,cb:a.cb});}console.log(JSON.stringify(out));})();
