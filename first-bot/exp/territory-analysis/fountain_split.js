const S=require('./summarise.js');
(async()=>{ const {TG}=await S.load({top:'top-all'});
const pc=(a,b)=>b?(100*a/b).toFixed(0)+'%':'-';
for (const kind of ['r500','elim']) for (const g of ['TW','TL','merge2','X-merge2']) {
  const xs=TG.filter(x=>x.grp===g&&x.kind===kind); if(!xs.length) continue;
  const out=[];
  for (const f of [1,0]) { const byD=S.DB.map((_,i)=>[0,1,2,3].map(j=>xs.reduce((s,x)=>s+x.s.byDF[f][i][j],0))); const tot=byD.reduce((s,a)=>s+a[0],0);
    const far=byD[0][0]+byD[1][0], near=byD[5][0]+byD[6][0]; const en=byD.reduce((s,a)=>s+a[2],0);
    out.push(`${f?'샘':'샘 밖'}: n ${tot} · 적 3+ 가까움 ${pc(far,tot)}(상대 ${pc(byD[0][2]+byD[1][2],far)}) · 우리 3+ 가까움 ${pc(near,tot)}(상대 ${pc(byD[5][2]+byD[6][2],near)}) · 상대가 먹음 ${pc(en,tot)}`); }
  // by phase x fount: enemy share
  const ph=S.PHN.map((_,p)=>{ const a=[0,1].map(f=>[0,1,2,3].map(j=>xs.reduce((s,x)=>s+x.s.byPF[p][f][j],0))); return `${S.PHN[p]} 샘 ${pc(a[1][2],a[1][0])} / 밖 ${pc(a[0][2],a[0][0])}`; });
  console.log(kind,g,xs.length,'|',out.join(' | ')); console.log('   ',ph.join(' ; '));
}})();
