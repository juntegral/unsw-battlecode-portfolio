// Reconcile the completed full-file independent recount with a canonical game census.
// No key statistic changes: byte-identical copies belong to two historical set labels.
'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib'),crypto=require('crypto'),assert=require('assert');
const E=require('./extract'),RE=require('./verify'),RAW=require('../../legacy/exp/intake-gap/rawload');
const read=n=>JSON.parse(fs.readFileSync(path.join(__dirname,n))),P=read('population.json'),T=read('tables.json'),V=read('verification.json');
assert(V.complete);assert.equal(V.mismatchN,0);assert.equal(V.checks.final,0);assert.equal(V.N,P.inputRows,'full-file recount must cover every input row');assert.equal(P.inputRows-P.tasks.length,P.duplicateAliases.length);
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),aliasChecks=[];
for(const t of P.tasks.filter(t=>t.aliases?.length)){
 for(const a of t.aliases){assert.equal(hash(t.file),hash(a.file));assert.equal(hash(t.file),a.sourceSha256);}
 const r=JSON.parse(zlib.gunzipSync(fs.readFileSync(E.filename(t)))),v=RE.recount(RAW.load(t.file),t,r.layout);assert.equal(v.checkFinal,0);
 for(const tm of ['A','B']){const x=r[tm],y=v[tm],deaths=r.deaths.filter(d=>d.team===tm&&d.cause===0);assert.equal(x.final?.len||0,y.final);assert.deepEqual(x.curve,y.curve);assert.equal(deaths.length,y.sacN);assert.equal(deaths.reduce((s,d)=>s+d.toLine,0),y.toLine);assert.equal(deaths.reduce((s,d)=>s+d.drops.length,0),y.drops);assert.equal(x.eats.filter(e=>e.r>=300&&e.originTeam===tm&&e.cause===0).length,y.lineSacEat300);}
 aliasChecks.push({gameId:t.gameId,primary:t.key,aliases:t.aliases.map(a=>a.key),independentRecountMatched:true,sourceSha256:hash(t.file)});
}
assert.equal(Object.keys(T.groups).length,Object.keys(V.groups).length);
for(const [key,g]of Object.entries(T.groups)){const v=V.groups[key];assert(v,key);assert.equal(g.N,v.N,key);for(const k of ['sacN','drops','toLine','toAlly','toEnemy','none','sac300N','drops300','line300','ally300','enemy300','none300'])assert.equal(g[k],v.independent[k],key+' '+k);assert.equal(g.final.sum,v.independent.final,key);assert.equal(g.lineSacEat300.sum,v.independent.lineSacEat300,key);for(const [q,c]of Object.entries(g.curve))if(c.N){assert.equal(c.N,v.curve[q].N,key);assert.equal(c.sum,v.curve[q].independent,key);}}
V.recountedInputFiles=V.N;V.N=P.tasks.length;V.expected=P.tasks.length;V.uniqueGames=P.tasks.length;V.populationCopies=require('./population_aliases').counts(P.tasks);V.canonicalReconciliation={checkedAt:new Date().toISOString(),inputFilesRecounted:V.recountedInputFiles,uniqueGames:V.N,duplicateCopies:P.duplicateAliases.length,aliasChecks,allGroupStatisticsUnchanged:true,method:'Full independent input-file recount completed first; collapse only byte-identical repeated games. Both affected unique games independently recounted again. All group sums and curves match the original independent result; each historical set membership retained.'};
fs.writeFileSync(path.join(__dirname,'verification.json'),JSON.stringify(V,null,2));console.log(JSON.stringify({N:V.N,recountedInputFiles:V.recountedInputFiles,aliasRechecks:aliasChecks.length,groups:Object.keys(T.groups).length,mismatchN:V.mismatchN}));
