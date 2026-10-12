#!/usr/bin/env node
'use strict';
const L=require('./lib'),{fs,path,ROOT,EXISTING,read,mapFiles,mirrorTile,mirrorEdge,edgeBetween,graph,components,hash}=L;
function validate(m,{connected=false}={}) {
 const errors=[],warnings=[],N=m.W*m.H,eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 if(!m.symmetry)errors.push('declared symmetry required for this test bed');
 if(m.symmetry) {
  for(let k=0;k<N;k++)if(!eq(m.tiles[k],m.tiles[mirrorTile(m,k)])){errors.push(`tile symmetry at ${k}`);break;}
  for(let k=0;k<2*N;k++)if(m.edges[k][0]!==m.edges[mirrorEdge(m,k)][0]){errors.push(`edge symmetry at ${k}`);break;}
  for(const d of m.dragons)if(!m.dragons.some(b=>b.team===1-d.team&&eq(b.body,d.body.map(k=>mirrorTile(m,k)))))errors.push('dragon symmetry');
 }
 const pairs=new Map();m.edges.forEach(([t,id],e)=>{if(t===2){if(!pairs.has(id))pairs.set(id,[]);pairs.get(id).push(e);}});
 for(const[id,es]of pairs) {
  if(es.length!==2){errors.push(`portal ${id}: ${es.length} endpoints`);continue;}
  if((es[0]<N)!==(es[1]<N))errors.push(`portal ${id}: orientation`);
  if(m.symmetry){const ss=es.map(e=>mirrorEdge(m,e));if((ss[0]===es[0])!==(ss[1]===es[1]))errors.push(`portal ${id}: one endpoint on symmetry axis`);const ids=ss.map(e=>m.edges[e][1]);if(ids[0]!==ids[1])errors.push(`portal ${id}: mirror pairing`);}
 }
 const occupied=new Set();for(const d of m.dragons){for(let i=0;i<d.body.length;i++){const k=d.body[i];if(occupied.has(k))errors.push(`dragon overlap at ${k}`);occupied.add(k);if(i&&edgeBetween(m,d.body[i-1],k)<0)errors.push('nonadjacent dragon segments');}}
 for(const t of [0,1])if(!m.dragons.some(d=>d.team===t))errors.push('missing team');
 const nb=graph(m),comp=components(nb),starts=m.dragons.map(d=>comp.c[d.body[0]]),teamsConnected=new Set(starts).size===1;
 if(connected&&comp.sizes.length!==1)errors.push(`generated map disconnected: ${comp.sizes.length} components`);
 if(!connected&&comp.sizes.length!==1)warnings.push(`existing topology: ${comp.sizes.length} components; connectivity is not a format constraint`);
 return {file:m.file||null,sha256:hash(m),valid:errors.length===0,errors:[...new Set(errors)],warnings,connectivity:{allTiles:comp.sizes.length===1,allStarts:teamsConnected,components:comp.sizes.sort((a,b)=>b-a)}};
}
function run(files,connected) {return files.map(file=>{try{return validate(read(file),{connected});}catch(e){return{file,valid:false,errors:[String(e.message)],warnings:[]};}});}
if(require.main===module) {
 const a=process.argv.slice(2),existing=a.includes('--existing'),inputs=a.filter(x=>!x.startsWith('--'));
 const rows=run(mapFiles(inputs.length?inputs:existing?EXISTING:['maps/generated']),!existing);
 const out=path.join(ROOT,'exp/mapgen');fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,existing?'validation-existing.json':'validation-generated.json'),JSON.stringify({at:new Date().toISOString(),mode:existing?'existing-format-symmetry-connectivity-audit':'generated-strict-connectivity',rows},null,2)+'\n');
 console.log(JSON.stringify({maps:rows.length,valid:rows.filter(r=>r.valid).length,failures:rows.filter(r=>!r.valid),connectivityWarnings:rows.filter(r=>r.warnings.length).map(r=>({file:r.file,...r.connectivity}))}));if(rows.some(r=>!r.valid))process.exitCode=1;
}
module.exports={validate,run};
