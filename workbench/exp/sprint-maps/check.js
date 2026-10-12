'use strict';
// Independent graph comparison, replay conversion regressions, and artifact audit.
const assert=require('assert/strict'),fs=require('fs'),path=require('path'),vm=require('vm');
const ROOT=path.resolve(__dirname,'../..'),L=require('../../tools/mapgen/lib'),C=require('../../tools/replay2map');
const {graph:otherGraph}=require('../general/atlas_recount');
const src=require('../../tools/top_features').viewerSource(),ctx={TextEncoder,TextDecoder};
vm.runInNewContext(src.slice(0,src.indexOf('var Af=B('))+'globalThis.mapParser=La;})();',ctx,{timeout:5000});
const tests=[],test=(name,f)=>{f();tests.push({name,pass:true});};
const m=L.blank(12,10,'xy','regression');m.tiles[0]=[1,10];m.tiles[119]=[1,10];
m.edges[0]=[1,-1];m.edges[120+2]=[1,-1];m.edges[13]=[2,7];m.edges[25]=[2,7];
m.dragons=[{team:1,body:[26,25]},{team:0,body:[93,94]}];
test('official viewer map parser round-trip retains gap support, wrap edges, nonconsecutive portal id and dragon order',()=>{
  const text=L.serialize(m)+'END\n',M=ctx.mapParser.fromMapText(text);assert.deepEqual(JSON.parse(JSON.stringify(C.fromMap(M,text))),m);
  assert.equal(C.fromMap(M).edges[13][1],0); // pair-only lists cannot recover original id 7
});
test('south/east boundary aliases normalize to north/west without losing kelp',()=>{
  const text=L.serialize(m)+'END\n',M=ctx.mapParser.fromMapText(text);
  M.initialHEdges[0]=0;M.initialHEdges[120]=1;
  M.initialVEdges[0]=0;M.initialVEdges[12]=1;
  const rebuilt=C.fromMap(M);assert.deepEqual(rebuilt.edges[0],[1,-1]);assert.deepEqual(rebuilt.edges[120],[1,-1]);
});
const v=JSON.parse(fs.readFileSync(path.join(__dirname,'validation.json'))),c=JSON.parse(fs.readFileSync(path.join(__dirname,'census.json')));
if(v.unredactedKnown)test('twenty actual unredacted replays exactly match all ten known a-layout tile gaps and geometry',()=>{
  assert.equal(v.unredactedKnown.names,10);assert.equal(v.unredactedKnown.replays,20);
  for(const r of v.unredactedKnown.rows){assert.equal(r.replays.length,2);for(const e of r.replays){assert(e.fields.geometryExact);assert(e.fields.tiles.equal);assert(e.fields.name.equal);}}
});
test('all ten known names and all fifteen layouts have >=2 distinct replay games and exact geometry',()=>{
  assert.equal(v.counts.knownNames,10);assert.equal(v.counts.knownLayouts,15);
  for(const row of v.known){assert(new Set(row.replays.map(r=>r.gameId)).size>=2);for(const r of row.replays){assert(r.fields.geometryExact);assert(r.fields.edgeKinds.equal);assert(r.fields.portals.equal);assert(r.fields.dragonOrderAndBodies.equal);}}
});
test('224 sprint metadata games each included once; all seven map ids agree with brief',()=>{
  const games=v.sprint.flatMap(s=>s.games);assert.equal(games.length,224);assert.equal(new Set(games.map(g=>g.gameId)).size,224);
  assert.deepEqual(v.sprint.map(s=>s.mapId).sort((a,b)=>a-b),[28,29,30,31,32,33,34]);
  for(const s of v.sprint){assert(s.allGamesSameStructureUpToGlobalTeamSwap);assert(s.games.every(g=>g.redactedGaps&&g.countdownEvents===0));assert.equal(s.games.length,32);}
});
const graphs=[];
for(const s of v.sprint) {
  const map=L.read(s.file),M=ctx.mapParser.fromMapText(fs.readFileSync(path.join(ROOT,s.file),'utf8'));
  const direct=L.graph(map),other=otherGraph(M),bad=[];
  for(let k=0;k<direct.length;k++) {
    const ref=[...new Set([...other.nb.slice(k*4,k*4+4)].filter(x=>x>=0))].sort((a,b)=>a-b);
    if(JSON.stringify(ref)!==JSON.stringify(direct[k].slice().sort((a,b)=>a-b)))bad.push(k);
  }
  assert.equal(bad.length,0,s.name+' independent graph mismatch');graphs.push({name:s.name,tiles:direct.length,mismatches:bad.length});
  const r=c.sprint.find(r=>r.file===s.file);assert.equal(r.sha256,L.hash(map));
  assert.equal(Object.values(r.corridorWidthDistribution).reduce((a,b)=>a+b,0),r.area);
  assert.equal(Object.values(r.degreeDistribution).reduce((a,b)=>a+b,0),r.area);
  assert.equal(Object.values(r.deadEndChainLengthDistribution).reduce((a,b)=>a+b,0),r.deadEndChainCount);
  assert.equal(r.core2Tiles+r.pocketTiles,r.area);
  for(const chain of r.deadEndChains){assert.equal(chain.tiles.length,chain.length);assert(new Set(chain.tiles).size===chain.length);}
}
tests.push({name:'all seven graphs agree with independent directional portal-aware graph',pass:true});
tests.push({name:'all saved hashes and histogram/core/chain accounting match census',pass:true});
test('20 existing maps plus 35 generated maps and S/M/L/R/X family counts',()=>{
  assert.equal(c.existing.length,20);assert.equal(c.generated.length,35);
  assert.deepEqual(c.families.map(f=>[f.name,f.maps]),[['S',6],['M',8],['L',6],['R',2],['X',13]]);
});
// Preserve the per-replay geometry while replacing only the estimated tile field
// in the audit's pooled estimate comparisons.
const gapQA=v.known.map(row=>{
  const r=row.replays[0].estimatedFields.tiles,truth=L.read(row.file),est=row.gapFit.tiles;
  let absMin=0,absMax=0,spawnMismatch=0,fountainMismatch=0;
  for(let k=0;k<truth.tiles.length;k++){
    absMin+=Math.abs(truth.tiles[k][0]-est[k][0]);absMax+=Math.abs(truth.tiles[k][1]-est[k][1]);
    spawnMismatch+=(truth.tiles[k][1]>0)!==(est[k][1]>0);
    fountainMismatch+=(truth.tiles[k][1]>0&&(truth.tiles[k][0]+truth.tiles[k][1])/2<=12)!==(est[k][1]>0&&(est[k][0]+est[k][1])/2<=12);
  }
  return {name:row.name,layout:row.layout,games:row.gapFit.games,exactTileShare:1-r.mismatches/truth.tiles.length,
    minGapMAE:absMin/truth.tiles.length,maxGapMAE:absMax/truth.tiles.length,spawnClassificationErrors:spawnMismatch,fountainClassificationErrors:fountainMismatch};
});
const out={at:new Date().toISOString(),tests,graphs,gapEstimatorKnownMapQA:gapQA,allPassed:true};
fs.writeFileSync(path.join(__dirname,'checks.json'),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({tests:tests.length,graphChecks:graphs.length,allPassed:true,gapQA}));
