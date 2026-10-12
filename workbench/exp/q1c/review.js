'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),{makeLoader,viewerSource}=require('../../tools/top_features'),ML=require('../../tools/mass_ledger');
const load=makeLoader(viewerSource()),spec=require('./spec.json'),out={differences:[],games:[]};
const selected={
 'proxy4_king:trauma_flip:A:1':[298,300,338,340,350,398,400,430],
 'proxy4_king:trauma:B:1':[298,300,338,340,350,398,400,430],
 'proxy4_king:big_empty:B:1':[298,300,338,340,350,398,400,430],
 'proxy4_king:gen_L_03:A:1':[240,241,242,243,244],
 'bot-hunter:gen_L_03:A:1':[352,353,354,355,356,369,370,371,372,373],
 'bot-hunter:gen_L_03:B:1':[412,413,414,415,416],
 'bot-hunter:stronghold:B:1':[348,350,358,360,428,430,480,494,495,496,497,498],
 'bot-hunter:stronghold:A:1':[298,299,300,301,302,398,400,430],
 'bot-hunter:trauma_flip:B:1':[366,367,368,369,370,371,372,404,405,406,407,408],
 'bot-hunter:trauma:B:1':[336,337,338,339,340],
 'bot:gen_L_03:B:1':[398,399,400,401,402,470,480,490],
 'bot:big_empty:A:1':[303,304,305,306,307,470,480,490]
};
function read(s,k){
 const R=load(`exp/q1c/${s}/games/${k.replace(/:/g,'_')}/game.replay`),us=k.split(':')[2],Q=Math.min(...R.match.map.initialDragons.filter(d=>d.team===us).map(d=>d.id)),acts=[];
 let r=-1;for(const e of R.events){if(e.type==='roundStart')r=e.round;if(e.type==='dragonAction')acts.push({r,id:e.id,action:e.action});}
 if(selected[k]){
  const g={set:s,key:k,queen:Q,snapshots:[],turns:[],feeds:[],deaths:[],checks:null};const seen=new Set(),rounds=new Set(selected[k]),inds=new Map(),byDeath=new Map();
  g.checks=ML.perGame(R,{rules:'123'},{
   turn(d,r,c){if(rounds.has(r)&&!seen.has(r)){seen.add(r);g.snapshots.push({r,dragons:[...c.drag.values()].map(o=>({id:o.id,team:o.team,body:o.body}))});}},
   indicator(e,r,c){const d=c.drag.get(e.id);if(!d||d.team!==us)return;inds.set(d.id,{r,text:e.text});if(rounds.has(r)){
    const bk=/ qbk(-?\d+),(-?\d+)/.exec(e.text||'');
    g.turns.push({r,id:d.id,body:d.body,text:e.text,goal:bk?+bk[1]:null,visibleAllies:[...c.drag.values()].filter(o=>o.team===us&&o.id!==d.id&&o.body.some(t=>c.cheb(d.body[0],t)<=3)).map(o=>({id:o.id,L:o.body.length,head:o.body[0],headVisible:c.cheb(d.body[0],o.body[0])<=3}))});
   }},
   action(d,e,r,c,before){if(d.team===us&&rounds.has(r)){const t=g.turns.findLast(t=>t.r===r&&t.id===d.id);if(t){t.action=e.action;t.after=d.body;t.fate=d.fate;}}},
   death(d,rec,i,o,r,c){if(d.id===Q)g.deaths.push({r,body:d.body,record:rec});const ind=inds.get(d.id),m=ind?.r===r&&/^feed #(\d+)/.exec(ind.text||'');if(d.team===us&&m){const f={r,id:d.id,target:+m[1],drops:rec.drops,byTarget:0,byQueen:0,byOwn:0,byEnemy:0,text:ind.text,body:d.body};g.feeds.push(f);byDeath.set(i,f);}},
   eat(d,k,o,r,c){const f=byDeath.get(o);if(!f)return;if(d.id===f.target)f.byTarget++;if(d.id===Q)f.byQueen++;if(d.team===us)f.byOwn++;else f.byEnemy++;}
  }).chk;out.games.push(g);
 }
 return acts;
}
function diff(a,b){let i=0;for(;i<Math.min(a.length,b.length);i++)if(JSON.stringify(a[i])!==JSON.stringify(b[i]))return {index:i,off:a[i],on:b[i]};return a.length===b.length?null:{index:i,off:a[i],on:b[i]};}
const keys=new Set();for(const l of spec.filter(l=>l.out==='exp/q1c/off'))for(const m of l.only)for(const opp of l.opps)for(const side of l.sides)keys.add(`${opp.split('/').pop()}:${m}:${side}:1`);
for(const k of keys){const acts={};for(const s of ['off','b','c','on'])acts[s]=read(s,k);for(const[l,r]of[['off','b'],['off','c'],['b','on']])out.differences.push({key:k,comparison:`${l}/${r}`,first:diff(acts[l],acts[r])});}
for(const l of spec.filter(l=>l.out==='exp/q1c/self'))for(const m of l.only)for(const side of l.sides)read('self',`bot:${m}:${side}:1`);
fs.writeFileSync('exp/q1c/review.json',JSON.stringify(out,null,2)+'\n');
console.log('review games',out.games.length,'comparisons',out.differences.length);
