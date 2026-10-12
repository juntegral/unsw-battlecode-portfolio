'use strict';
// Supplement current-format tests with real known-map replays before gap redaction.
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),C=require('../../tools/replay2map'),L=require('../../tools/mapgen/lib');
const refs=new Map(L.mapFiles(['maps/online-20260927']).map(f=>{const m=L.read(f);return[m.name,{file:f,m}];}));
const selected=new Map([...refs.keys()].map(k=>[k,[]])),seen=new Set();
for(const root of ['data/online/g1','data/online/g2']) {
  const dir=path.join(L.ROOT,root);if(!fs.existsSync(dir))continue;
  for(const set of fs.readdirSync(dir).sort()) {
    const sub=path.join(dir,set);if(!fs.statSync(sub).isDirectory())continue;
    for(const f of fs.readdirSync(sub).filter(f=>/^game-\d+\.json$/.test(f)).sort()) {
      const g=JSON.parse(fs.readFileSync(path.join(sub,f)));
      if(!g.completedAt||g.completedAt>='2026-09-27T11:00:00.000Z'||seen.has(g.id))continue;
      seen.add(g.id);const file=path.join(sub,`M${g.id}.replay`);if(!fs.existsSync(file))continue;
      const {m}=C.fromReplay(file,{events:false}),rows=selected.get(m.name);
      if(!rows||rows.length>=2||m.tiles.every(g=>g[1]===0))continue;
      const ref=refs.get(m.name),fields=C.compare(m,ref.m);
      assert(fields.geometryExact,file+' geometry');assert(fields.tiles.equal,file+' true gap fields');
      rows.push({gameId:g.id,battleId:g.battleId??null,seriesId:g.seriesId,replayFile:path.relative(L.ROOT,file),reference:ref.file,
        layout:'a',gapFieldsRedacted:false,fields});
    }
  }
}
const rows=[...selected].map(([name,replays])=>({name,replays}));
assert(rows.every(r=>r.replays.length===2),'two unredacted replays for every known name');
const file=path.join(__dirname,'validation.json'),v=JSON.parse(fs.readFileSync(file));
v.unredactedKnown={at:new Date().toISOString(),names:rows.length,replays:rows.reduce((n,r)=>n+r.replays.length,0),
  exactIncludingGaps:true,rows,note:'Only a layouts existed in these pre-redaction samples; b-layout intervals remain inferred reference data.'};
v.counts.unredactedKnownReplays=v.unredactedKnown.replays;
v.counts.totalKnownReplays=v.counts.knownReplays+v.unredactedKnown.replays;
fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');
console.log(JSON.stringify({names:rows.length,unredactedReplays:v.unredactedKnown.replays,allGapFieldsExact:true}));
