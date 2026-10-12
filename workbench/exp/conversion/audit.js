'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert'),E=require('./extract');
const p=JSON.parse(fs.readFileSync(path.join(__dirname,'population.json'))),t=JSON.parse(fs.readFileSync(path.join(__dirname,'tables.json'))),v=JSON.parse(fs.readFileSync(path.join(__dirname,'verification.json')));
assert.equal(t.coverage.processed,p.tasks.length);assert.equal(t.coverage.missing.length,0);assert.equal(v.N,p.tasks.length);assert(v.complete);assert.equal(v.mismatchN,0);assert.equal(v.checks.final,0);
for(const [key,g] of Object.entries(t.groups)){
 const a=v.groups[key];assert(a,key);assert.equal(a.N,g.N,key);for(const k of ['sacN','drops','toLine','toAlly','toEnemy','none','sac300N','drops300','line300','ally300','enemy300','none300'])assert.equal(g[k],a.independent[k],key+' '+k);assert.equal(g.final.sum,a.independent.final,key+' final');assert.equal(g.lineSacEat300.sum,a.independent.lineSacEat300,key+' sacEat');
 for(const [q,c]of Object.entries(g.curve)){const z=a.curve[q];if(!c.N){assert(!z||!z.N);continue;}assert.equal(c.N,z.N,key+' '+q+' N');assert.equal(c.sum,z.independent,key+' '+q);assert.equal(z.primary,z.independent,key+' '+q+' verification');}
}
let rawN=0,eventN=0,ancestorN=0;const unresolved=[];
for(const task of p.tasks){assert(fs.existsSync(E.filename(task)),task.key);rawN++;}
for(const map of ['Slithery Fight/a','Slithery Fight/b','Schooltime/a','Trauma/a','Autarky/a'])for(const role of ['eliteWinner','eliteLoser','ours:v1:top6']){const g=t.groups[map+'|'+role+'|r500'];eventN+=g.sacN;ancestorN+=g.feederGenealogy.ancestorN;assert.equal(g.feederGenealogy.ancestorN+g.feederGenealogy.offLineN,g.sacN);assert.equal(g.feederGenealogy.activeN,0);assert.equal(g.path.zeroSteps,g.path.splitActions);}
const audit={checkedAt:new Date().toISOString(),rawN,groupsN:Object.keys(t.groups).length,fullIndependentGames:v.N,independentMismatchN:v.mismatchN,selectedRoleSacEvents:eventN,selectedRoleAncestorSacEvents:ancestorN,allTablesMatchIndependent:true,resource:E.resource()};
t.verification={file:'verification.json',N:v.N,complete:v.complete,mismatchN:v.mismatchN,checks:v.checks,method:'independent raw head/tail and tileChange reconstruction; shared fast decoder and frozen layout assignment only'};
t.audit={file:'audit.json',checkedAt:audit.checkedAt,allTablesMatchIndependent:true};
t.definitions.feederGenealogy='ancestorN counts donor IDs in the split ancestry; activeN counts the active ancestral segment at death. An ancestor parent may feed after the final path took its child.';
t.definitions.relay+=' Same recipient ID only; split-descendant relays are not followed. secondLegLinePearls includes the whole subsequent packet, not identified original tokens.';
t.definitions.eventFiles='One gzip per game with all sacrifices from r250, true drop coordinates and recipient events; hash mapping in eventFiles. No uncompressed replay duplicates.';
fs.writeFileSync(path.join(__dirname,'tables.json'),JSON.stringify(t));fs.writeFileSync(path.join(__dirname,'audit.json'),JSON.stringify(audit,null,2));console.log(JSON.stringify(audit));
