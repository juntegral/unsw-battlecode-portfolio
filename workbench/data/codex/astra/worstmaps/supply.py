import analyze as a
from collections import Counter,defaultdict
from statistics import median
import json,hashlib
rs=json.loads((a.OUT/'rows.json').read_text());groups={}
for r in rs:
 root=a.lr.agg.sb.load_replay(a.Path(r['path'])).root();w=r['features']['w'];h=r['features']['h']
 raw=[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')]
 sig=hashlib.sha256(json.dumps(a.Geo(w,h,raw).moves).encode()).hexdigest()[:16]
 d=groups.setdefault(sig,dict(map=r['map'],games=[],births=Counter(),gaps=defaultdict(list),total=0));d['games'].append(r['gid']);rnd=-1;actor=None;removed={}
 for ev in root.pointer(3):
  k=ev.u16(0)
  if k not in (0,1,3):continue
  p=ev.pointer(0)
  if k==0:rnd=p.i32(0);actor=None
  elif k==1:actor=p.i32(0)
  else:
   x,y=a.point(p.pointer(0));cell=y*w+x
   if p.u32(0):
    if actor is None:
     d['births'][cell]+=1;d['total']+=1
     if cell in removed:d['gaps'][cell].append(rnd-removed.pop(cell))
   else:removed[cell]=rnd
for d in groups.values():
 d['fast']=[c for c,gs in d['gaps'].items() if len(gs)>=5 and median(gs)<=12]
 gs=[x for g in d['gaps'].values() for x in g]
 d['gap_summary']=[len(gs),min(gs),median(gs),max(gs)] if gs else []
 d['fast_births']=sum(d['births'][c] for c in d['fast'])
(a.OUT/'supply.json').write_text(json.dumps(groups,separators=(',',':')))
print([(d['map'],len(d['games']),len(d['births']),len(d['fast']),d['gap_summary']) for d in groups.values()])
