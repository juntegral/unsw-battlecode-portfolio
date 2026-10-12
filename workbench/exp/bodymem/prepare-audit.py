from pathlib import Path
p=Path('exp/bodymem')
s=(p/'replay-world.cpp').read_text().replace('#include "engine.hpp"\n#include "policy.hpp"\n#include "plan.hpp"','#include "world.hpp"')
s=s.replace('std::unique_ptr<Planner> p; PolicySelector policy; ','')
s=s.replace(' ptr->p = std::make_unique<Planner>(ptr->w);','')
a=s.index('        const auto& row = st.policy.get(w);')
b=s.index('        std::vector<int> path;',a)
s=s[:a]+s[b:]
a=s.index('        std::cout << ",\\\"choice\\\":')
s=s[:a]+'        std::cout << "}\\n";\n    }\n}\n'
(p/'memory-world.cpp').write_text(s)
s=(p/'replay.js').read_text()
s=s.replace('let mapGraph=null;', 'const known=new Map(), active=new Map();')
a=s.index(' if(!mapGraph)')
b=s.index('\n}});',a)
s=s[:a]+''' const old=known.get(d.id)||new Set(), observed=new Set(d.body.filter(p=>c.cheb(center,p)<=3).map(p=>c.key(p.x,p.y)));
 const body=d.body.map(p=>c.key(p.x,p.y)), unresolved=body.filter(t=>!old.has(t)&&!observed.has(t));
 known.set(d.id,new Set([...old,...observed]));
 const rec={round,id:d.id,actual:split?'split'+split:move,indicator:inds.get(`${round}:${d.id}`)||'',body,unresolved,post:null};
 snapshots.push(rec); active.set(d.id,rec);
},action(d,e,round,c,before){
 if(d.team!==side||!active.has(d.id))return;
 const rec=active.get(d.id), k=known.get(d.id)||new Set();
 if(e.action?.kind==='move') {let h=before[0];for(const dir of e.action.steps){h=c.across(h.x,h.y,dir);if(!h)break;k.add(c.key(h.x,h.y));}}
 rec.post=d.fate?null:d.body.map(p=>c.key(p.x,p.y));known.set(d.id,new Set((rec.post||[]).filter(t=>k.has(t))));
},split(parent,child,e,round,c){
 const rec=active.get(parent.id);if(parent.team!==side||!rec)return;
 rec.post=parent.body.map(p=>c.key(p.x,p.y)); const k=known.get(parent.id)||new Set();known.set(parent.id,new Set(rec.post.filter(t=>k.has(t))));
}''' + s[b:].replace('\n}});','\n});',1)
a=s.index('function oracle(')
s=s[:a]+'''const result={file,side,checks:ledger.chk,uncertain,turns:snapshots.length,arms:{},scope:'World arrays only; recorded actions forced, no Planner or causal safety claim'};
for(const arm of ['on','off']) {
 const p=cp.spawnSync(path.join(__dirname,'memory-world-'+arm),[],{input:lines.join('\\n')+'\\n',encoding:'utf8',maxBuffer:256*1024**2});
 if(p.status!==0)throw Error(arm+': '+p.stderr);
 const rows=p.stdout.trim().split('\\n').filter(Boolean).map(JSON.parse);if(rows.length!==snapshots.length)throw Error('row count');
 const out={turns:rows.length,complete:0,completeDrift:[],startDrift:[],postDrift:[],unseenEndOnly:[],samples:[]};
 for(let i=0;i<rows.length;i++) {
  const v=rows[i],s=snapshots[i],drift=JSON.stringify(v.body)!==JSON.stringify(s.body),post=s.post&&JSON.stringify(v.post)!==JSON.stringify(s.post);
  const rec={round:s.round,id:s.id,actual:s.actual,body:s.body,reported:v.body,unresolved:s.unresolved,postActual:s.post,postReported:v.post,indicator:s.indicator};
  if(!s.unresolved.length){out.complete++;if(drift)out.completeDrift.push(rec);}
  if(drift)out.startDrift.push(rec);
  if(post)out.postDrift.push(rec);
  if(post&&!drift)out.unseenEndOnly.push(rec);
  if(s.actual.length>1&&s.actual[0]!=='s'&&out.samples.length<8)out.samples.push(rec);
 }
 result.arms[arm]=out;
}
fs.writeFileSync(prefix+'.json',JSON.stringify(result,null,2)+'\\n');
console.log(JSON.stringify({file,turns:result.turns,uncertain,arms:Object.fromEntries(Object.entries(result.arms).map(([k,v])=>[k,{complete:v.complete,completeDrift:v.completeDrift.length,startDrift:v.startDrift.length,postDrift:v.postDrift.length}]))}));
'''
s=s.replace("fs.writeFileSync(prefix+'.input',lines.join('\\n')+'\\n');",'')
(p/'memory-trace.js').write_text(s)
