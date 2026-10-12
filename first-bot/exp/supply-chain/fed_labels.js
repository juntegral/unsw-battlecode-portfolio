// usage (repository root): node exp/supply-chain/fed_labels.js — labels in the 10 turns before our pieces (<=4) sacrificed, stack5+stack6 online.
// labels of our pieces (<=4 at death) in the 10 turns before a sacrifice death; stack5+stack6 online (one process)
const path=require('path'), fs=require('fs'); const ROOT=process.cwd();
const ML=require(ROOT+'/tools/mass_ledger.js'); const {parseInd}=require(ROOT+'/tools/mech_check.js');
const tf=require(ROOT+'/tools/top_features.js'); const load=tf.makeLoader(tf.viewerSource());
const cnt={pieces:0, turns:0, lab:{}, deathLab:{}, withG:0, withF:0, bigMoved:0};
for (const set of ['cand-stack5-online','cand-stack6-online']) {
  const idx=JSON.parse(fs.readFileSync(path.join(ROOT,'data/online',set,'index.json'),'utf8'));
  for (const g of idx.games) { const f=path.join(ROOT,'data/online',set,'M'+g.gameId+'.replay'); if(!fs.existsSync(f)) continue;
    const R=load(f), us=String(g.ourSide).toUpperCase(); const info={map:g.mapName}; if(g.mapName==='Prisoners Dilemma') info.variant=R.match.map.initialDragons.length===10?'PD10':'PD6';
    const hist=new Map();
    ML.perGame(R, info, {
      indicator(e,r,c){ const d=c.drag.get(e.id); if(!d||d.team!==us) return; let h=hist.get(e.id); if(!h) hist.set(e.id,h=[]); const t=parseInd(e.text||''); let lab=t.kind; if(t.kind==='move'){ const s=[]; if(t.goal) s.push('g'); if(t.fg) s.push('F'); if(t.grab) s.push('grab'); lab=s.length?s.join('+'):'move'; } h.push([r,lab]); if(h.length>12) h.shift(); },
      death(d,rec,idx,o,r,c){ if(d.team!==us||rec.cause!==0||d.body.length>4) return; const h=(hist.get(d.id)||[]).filter(x=>x[0]>=r-10&&x[0]<r); cnt.pieces++; const last=(hist.get(d.id)||[]).find(x=>x[0]===r); const dl=last?last[1]:'none'; cnt.deathLab[dl]=(cnt.deathLab[dl]||0)+1;
        let hasG=0,hasF=0; for(const [rr,l] of h){ cnt.turns++; cnt.lab[l]=(cnt.lab[l]||0)+1; if(l.includes('g')&&l!=='grab') hasG=1; if(l.includes('F')) hasF=1; } cnt.withG+=hasG; cnt.withF+=hasF; }
    });
  }
}
console.log(JSON.stringify(cnt));
