import sys,json,importlib.util,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict,deque
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('weak',Path('data/codex/astra/weak/analyze.py'));w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
results=[]
for gid,bid in [(1516988,1516986),(1516990,1516986),(1516554,1516554)]:
 g=json.loads((OUT/f'{gid}.json').read_text());path=Path(f'data/online/live-one1/b{bid}/M{gid}.replay');root=w.replay.load(path).root();W,H=g['W'],g['H'];bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  p=line.split()
  if p[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(p[3+2*k]),int(p[4+2*k])) for k in range(int(p[2])));teams[i]=int(p[1])
  elif p[0]=='EDGE':raw.append(tuple(map(int,p[1:4])))
 geo=w.Geo(W,H,raw);rev=[[] for _ in geo.adj]
 for u,vs in enumerate(geo.adj):
  for v in vs:rev[v].append(u)
 cache={}
 def dt(c):
  a=c[1]*W+c[0]
  if a not in cache:
   ds={a:0};q=deque([a])
   while q:
    u=q.popleft()
    for v in rev[u]:
     if v not in ds:ds[v]=ds[u]+1;q.append(v)
   cache[a]=ds
  return cache[a]
 queen,enemy=g['base']['queens'];dead=False;r=-1;best=(99999,None);near=set();start=[sum(len(b) for i,b in bodies.items() if teams[i]==s) for s in [0,1]];eat=[0,0];lost=[0,0];paid=[0,0];actor=None;turn0=0;te=0;tl=0
 def close():
  global turn0,te,tl
  if actor is not None:
   s=teams[actor];end=sum(len(b) for i,b in bodies.items() if teams[i]==s);delta=turn0+te-tl-end;assert delta>=0;paid[s]+=delta
 def proximity(ix):
  global best
  if dead and enemy in bodies:
   eh=bodies[enemy][0];ds=dt(eh)
   for i,b in bodies.items():
    if teams[i]!=1:continue
    d=ds.get(b[0][1]*W+b[0][0],99999)
    if d<best[0]:best=(d,dict(r=r,event=ix,id=i,head=b[0],enemy=eh))
    if d<=5:near.add((r,i))
 for ix,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:close();actor=None;r=p.i32(0)
  elif k==1:
   close();actor=p.i32(0);turn0=sum(len(b) for i,b in bodies.items() if teams[i]==teams[actor]);te=0;tl=0
  elif k==3 and not p.u32(0):eat[teams[actor]]+=1;te+=1
  elif k==9:
   i=p.i32(0);h,t=w.replay.point(p.pointer(0)),w.replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=h:b.appendleft(h)
   while len(b)>1 and b[-1]!=t:b.pop()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(w.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);lost[teams[i]]+=len(bodies[i]);tl+=len(bodies[i]) if teams[i]==teams[actor] else 0;bodies.pop(i);dead|=i==queen
  if k in [0,9,10,11]:proximity(ix)
 close()
 final=[]
 for s in [0,1]:
  lens=[len(b) for i,b in bodies.items() if teams[i]==s];st=root.pointer(4).pointer(s);measured=[len(lens),max(lens,default=0),sum(lens),len(bodies.get(enemy if s==0 else queen,()))];assert measured==[st.i32(x) for x in [0,4,8,12]];assert start[s]+eat[s]-lost[s]-paid[s]==sum(lens);final.append(measured)
 result=dict(gid=gid,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),final_A_B=final,ledger=dict(start=start,eat=eat,dead=lost,paid=paid),min_post_distance=best,post_near_round_dragon_pairs=len(near),source_sha256=hashlib.sha256(Path('data/online/smoke/one14-bot/main.cpp').read_bytes()).hexdigest())
 results.append(result);print(result,flush=True)
(OUT/'verification.json').write_text(json.dumps(results,indent=2))
