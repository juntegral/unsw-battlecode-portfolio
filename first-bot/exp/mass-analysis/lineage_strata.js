#!/usr/bin/env node
// lineage_strata.js — final-king lineage sacrifice gain after r350 within strata of the lineage length at r350
// (r500 maps, games that reached r500; top sample + our online sets). Reads .cache/mass-ledger only.
// usage: node exp/mass-analysis/lineage_strata.js   (research/observations/top-mass-spending.md 3.2)

const ROOT=require('path').resolve(__dirname,'..','..');
const fs=require('fs');
const keys=new Set(fs.readFileSync(ROOT+'/exp/mass-analysis/sample-top1500.keys','utf8').split('\n').filter(Boolean));
const SETS={'baseline-r1':'g4r4','baseline-r1b':'g4r4','baseline-r1c':'g4r4','cand-merge2-online':'merge2','cand-swarm8-online':'swarm8','base-px9d-online':'px9d'};
const rows=[];
const read=f=>fs.readFileSync(f,'utf8').split('\n').filter(Boolean).map(l=>{try{return JSON.parse(l)}catch{return null}}).filter(Boolean);
for (const g of read(ROOT+'/.cache/mass-ledger/top-sample.jsonl')) { if(!keys.has(g.key)||g.kind!=='r500'||g.rounds!==500||!g.winner) continue; for (const s of ['A','B']) { const L=g[s].lin; if(!L||!L.cp[350]) continue; rows.push({grp: s===g.winner?'TW':'TL', Lt:L.cp[350].Lt, sac:L.cp[350].eat[1], units350: g[s].st.units[35], final:L.len}); } }
for (const [set,grp] of Object.entries(SETS)) for (const g of read(ROOT+'/.cache/mass-ledger/online-'+set+'.jsonl')) { if(g.kind!=='r500'||g.rounds!==500) continue; const L=g[g.us].lin; if(!L||!L.cp[350]) continue; rows.push({grp, Lt:L.cp[350].Lt, sac:L.cp[350].eat[1], units350: g[g.us].st.units[35], final:L.len}); }
const strata=[[0,8],[8,16],[16,24],[24,999]];
const out={};
for (const r of rows) { const si=strata.findIndex(([a,b])=>r.Lt>=a&&r.Lt<b); const k=r.grp+'|'+si; (out[k]=out[k]||[]).push(r); }
console.log('group | L350 stratum | n | mean lineage sac gain r350+ | mean units at r350 | mean final king');
for (const grp of ['TW','TL','g4r4','merge2','swarm8','px9d']) for (let si=0;si<strata.length;si++) { const a=out[grp+'|'+si]; if(!a) continue; const m=f=>(a.reduce((s,x)=>s+f(x),0)/a.length).toFixed(1); console.log(grp, '|', strata[si].join('–'), '|', a.length, '|', m(x=>x.sac), '|', m(x=>x.units350), '|', m(x=>x.final)); }
