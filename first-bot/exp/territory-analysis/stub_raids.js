const S=require('./summarise.js');
const EI=S.EI, path=require('path');
const agg={};
const kindOf=m=>S.ELIM.includes(m)?'elim':'r500';
const inactive=T=>T.splits<=3&&T.sonar===0;
(async()=>{
 const files=[[path.join(S.CACHE,'top-all.jsonl.gz'),'top']]; for(const s of Object.keys(S.SETS)) files.push([path.join(S.CACHE,'online-'+s+'.jsonl.gz'),'online']);
 for (const [f,src] of files) await S.forEachGame(f, g=>{
  if (src==='top'&&(inactive(g.A)||inactive(g.B)||g.A.faults>=3||g.B.faults>=3||!g.winner)) return;
  const us=src==='online'?(g.us==='A'?0:1):-1, bot=src==='online'?S.SETS[g.set]:null;
  const grp=ti=>src==='top'?(((ti===0?'A':'B')===g.winner)?'TW':'TL'):(ti===us?bot:'X-'+bot);
  for (const e of g.E) { if (e[EI.dmax]<3) continue; if (!(e[EI.exit]===1 && !S.contactKill(e) && e[EI.killer]!==1)) continue; // self-loss excluding ally collisions
    const k=grp(e[EI.ti])+'|'+kindOf(g.map); const a=agg[k]||(agg[k]={n:0,stub:0,nat:0,natStub:0,L1le2:0,trap:0,sac:0});
    a.n++; a.nat+=e[EI.nat]; const stub=e[EI.L1]<=2&&e[EI.Lmax]>=4; if(stub){a.stub++;a.natStub+=e[EI.nat];} if(e[EI.L1]<=2)a.L1le2++; if(e[EI.cause]===1)a.trap++; if(e[EI.cause]===0)a.sac++; }
 });
 const pc=(a,b)=>b?(100*a/b).toFixed(0)+'%':'-';
 for (const [k,a] of Object.entries(agg).sort()) if (/^(TW|TL|X-merge2|merge2)\|/.test(k)) console.log(k.padEnd(16),'selfloss',a.n,'died at L2 after reaching L>=4 (split)',pc(a.stub,a.n),'of their natural take',pc(a.natStub,a.nat),'| died at L<=2',pc(a.L1le2,a.n),'trap',pc(a.trap,a.n),'sac',pc(a.sac,a.n));
})();
