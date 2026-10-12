'use strict';
const fs=require('fs'),z=require('zlib'),{OUT,guard}=require('./setup'),path=require('path');
const P=require('./population.json'),get=(o,k)=>o[k]||(o[k]={games:0,heads50:0,N50:0,finalSum:0,splits:0,deathCauses:{},Acauses:{},small:{N:0,visibleEnemy:0,farKing:0,empiricalN:0,empiricalNear3:0},headContacts:0,mover:0,passive:0,activeBalance:{},activeLengthBalance:{},activeTaggedTrade:0,enemyBodyDeaths:0,allyBodyDeaths:0});
const inc=(o,k,n=1)=>o[k]=(o[k]||0)+n;const groups={};let n=0;
for(const t of P.tasks.filter(t=>t.custom)){
 if(n++%25===0)guard();
 const r=JSON.parse(z.gunzipSync(fs.readFileSync(path.join(OUT,'cache',t.key+'.json.gz')))),x=JSON.parse(z.gunzipSync(fs.readFileSync(path.join(OUT,'tactical-cache',t.key+'.json.gz'))));
 for(const tm of ['A','B']){
  const role=r.result.winner===tm?'winner':'loser',labels=['custom/'+role];
  if(t.us===tm)labels.push('ours/custom','ours/custom/'+role);if(t.under===tm)labels.push('under/custom','under/custom/'+role);
  for(const label of labels){
   const g=get(groups,label),p=r.profile[tm],s=p.small,emp=x.empiricalSmall[tm];g.games++;g.splits+=p.splits.length;g.finalSum+=r.result['team'+tm].longestDragon;
   if(p.curves['50']){g.heads50+=p.curves['50'].heads;g.N50++;}
   for(const k of ['N','visibleEnemy','farKing'])g.small[k]+=s[k]||0;for(const k of ['empiricalN','empiricalNear3'])g.small[k]+=emp[k]||0;
   for(const d of r.deaths.filter(d=>d.team===tm)){inc(g.deathCauses,d.reason);if(d.reason==='A')inc(g.Acauses,d.cause);if(d.reason==='O')g[d.otherTeam===tm?'allyBodyDeaths':'enemyBodyDeaths']++;}
   for(const e of x.records.filter(e=>e.reason==='H')){
    g.headContacts++;if(e.teamById[e.mover]!==tm){g.passive++;continue;}g.mover++;
    const a=e.lastDecisions[e.mover].at(-1),own=a.visibleAlly+1,enemy=a.visibleEnemy,balance=own<enemy?'lower':own===enemy?'equal':'higher';
    const enemyLen=e.lengths[e.passive],length=a.len<enemyLen?'shorter':a.len>enemyLen?'longer':'equal';inc(g.activeBalance,balance);inc(g.activeLengthBalance,length+'/'+balance);
    g.activeTaggedTrade+=+/\bTRADE\b/.test(a.tag);
   }
  }
 }
}
const out={at:new Date().toISOString(),N_customGames:n,groups,definition:'all custom-map games; active balance from the mover BEFORE its fatal action, own visible allies plus self vs visible enemy heads; winner/loser is actual game result; NoValidAction cause subtype comes from reconciled ledger'};
fs.writeFileSync(path.join(OUT,'custom-comparison.json'),JSON.stringify(out,null,2));console.log(JSON.stringify(out));
