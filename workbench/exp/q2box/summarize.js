'use strict';
const fs=require('fs'),a=require('./analysis.json');
const flat=lane=>Object.values(a.sets[lane]);
const sealRows=lane=>flat(lane).flatMap(g=>g.seals.map(s=>({key:g.key,...s})));
const babies=lane=>flat(lane).flatMap(g=>g.newborns.map(n=>({key:g.key,...n})));
const qw=lane=>flat(lane).flatMap(g=>g.qwChildren.map(c=>({key:g.key,...c,first:g.newborns.find(n=>n.id===c.id)||null})));
const eligible=n=>n.length===2&&n.visible&&n.distance<=2&&n.outwardSingles.length>0;
const result={missing:a.missing,historyErrors:a.historyErrors,checks:Object.entries(a.sets).flatMap(([lane,gs])=>Object.values(gs).map(g=>({lane,key:g.key,checks:g.checks}))).filter(x=>Object.values(x.checks).some(v=>v!==0)),identity:a.identity,around:a.pairs.filter(p=>p.key.includes(':around_unsw:')),regressions:a.pairs.filter(p=>p.survivalRegression),pockets:a.pairs.filter(p=>/:(autarky|prisoners_dilemma|slithery_fight):/.test(p.key)),changed:a.pairs.filter(p=>!p.sameEvents),earlierDeaths:a.pairs.filter(p=>p.onDeath&&p.offDeath&&p.onDeath.round<p.offDeath.round),lanes:{}};
for(const lane of ['on','off']) {const b=babies(lane),q=qw(lane),s=sealRows(lane);result.lanes[lane]={games:flat(lane).length,seals:s,qbs:flat(lane).reduce((n,g)=>n+g.tags.qbs,0),qbe:flat(lane).reduce((n,g)=>n+g.tags.qbe,0),qwCount:q.length,qwMissing:q.filter(c=>!c.first),qwEligible:q.filter(c=>c.first&&eligible(c.first)),qwAll:q,qwEligibleSuccess:q.filter(c=>c.first&&eligible(c.first)&&c.first.action?.kind==='move'&&c.first.afterDistance>c.first.distance),nonqwQbe:b.filter(n=>!n.qw&&/\bqbe\d+/.test(n.indicator)),otherEligible:b.filter(n=>!n.qw&&eligible(n)),alive500:flat(lane).filter(g=>g.queenAlive500).length,cpuMax:Math.max(...flat(lane).flatMap(g=>(g.cpu||[]).filter(x=>x.startsWith('team '+g.side+' ')).map(x=>+x.match(/max ([\d.]+)M/)[1]))),cpuMissing:flat(lane).filter(g=>!(g.cpu||[]).some(x=>x.startsWith('team '+g.side+' '))).map(g=>g.key)};}
fs.writeFileSync('exp/q2box/summary.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({...result,lanes:Object.fromEntries(Object.entries(result.lanes).map(([k,v])=>[k,{...v,qwAll:undefined}]))},null,2));
