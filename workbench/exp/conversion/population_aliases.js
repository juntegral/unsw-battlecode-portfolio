// A replay can appear in both an autoscrim index and the historical online index.
// Count one game globally, retain all set memberships, and verify source bytes agree.
'use strict';
const fs=require('fs'),crypto=require('crypto'),assert=require('assert');
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
function canonicalize(tasks){
 const byId=new Map(),out=[];
 for(const original of tasks){const t={...original,aliases:[...(original.aliases||[])]},id=t.gameId===undefined?'key:'+t.key:'game:'+t.gameId;
  if(!byId.has(id)){byId.set(id,t);out.push(t);continue;}
  const primary=byId.get(id);for(const k of ['src','map','us','oppId'])assert.equal(t[k],primary[k],'conflicting alias '+t.key+' '+k);
  const sha=hash(primary.file);assert.equal(hash(t.file),sha,'nonidentical source replay alias '+t.key);
  const alias={...t,sourceSha256:sha};delete alias.aliases;if(!primary.aliases.some(a=>a.key===alias.key))primary.aliases.push(alias);
 }
 return out;
}
function counts(tasks){return {uniqueGames:tasks.length,inputRows:tasks.reduce((s,t)=>s+1+(t.aliases?.length||0),0),duplicateAliases:tasks.flatMap(t=>(t.aliases||[]).map(a=>({gameId:t.gameId,primary:t.key,alias:a.key,sourceSha256:a.sourceSha256}))) };}
module.exports={canonicalize,counts};
