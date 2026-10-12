import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as lr
from count_local import Geo
OUT=Path(__file__).resolve().parent
for gid in (1498740,1498741,1498742):
 root=lr.replay.load(f'data/online/smoke/one11-p1-old/M{gid}.replay').root()
 scan=json.loads((OUT/f'{gid}-scan.json').read_text());qs=scan['queens'];q=qs['us'];eq=qs['them']
 w,h=map(int,root.text(0).splitlines()[0].split()[1:3]);bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  a=line.split()
  if a[0]=='DRAGON':
   i=len(bodies);teams[i]=int(a[1]);bodies[i]=deque(int(a[4+2*k])*w+int(a[3+2*k]) for k in range(int(a[2])))
  elif a[0]=='EDGE':raw.append(tuple(map(int,a[1:4])))
 geo=Geo(w,h,raw);own=teams[q];pearls=set();cur=None;turns=[];rnd=-1;cache={};near=[];closest=None;dead=False;births={};final={}
 xy=lambda c:[c%w,c//w]
 tile=lambda p:lr.replay.point(p)[1]*w+lr.replay.point(p)[0]
 def dist(src):
  if src not in cache:
   ds={src:0};queue=deque([src])
   while queue:
    c=queue.popleft()
    for t in geo.adj[c]:
     if t not in ds:ds[t]=ds[c]+1;queue.append(t)
   cache[src]=ds
  return cache[src]
 def board(src):
  chars={c:('*' if c in pearls else '.') for c in geo.window(src)};heads=[]
  for i,b in bodies.items():
   for k,c in enumerate(b):
    if c in chars:chars[c]=('Q' if i==q else 'K' if i==eq else 'A' if teams[i]==own else 'B') if k==0 else ('a' if teams[i]==own else 'b')
   if b[0] in chars:heads.append([i,len(b),xy(b[0])])
  x,y=xy(src)
  rows=[''.join(chars[((y+dy)%h)*w+(x+dx)%w] for dx in range(-3,4)) for dy in range(-3,4)]
  edges=[' '.join(''.join('nesw'[d] if k==2 else 'NESW'[d] for d,(k,t) in enumerate(geo.moves[((y+dy)%h)*w+(x+dx)%w]) if k) or '-' for dx in range(-3,4)) for dy in range(-3,4)]
  return dict(center=xy(src),rows=rows,edges=edges,heads=heads)
 def close():
  if cur is not None:
   cur['end']=list(bodies.get(cur['id'],[]));turns.append(cur)
 for ei,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:close();cur=None;rnd=p.i32(0)
  elif k==1:
   close();i=p.i32(0)
   cur=dict(r=rnd,id=i,side=teams[i],body=list(bodies[i]),steps=[],eats=0,deaths=[],split=None)
   if i in (q,eq) or (gid==1498740 and i==666 and rnd in (379,381)) or (gid==1498740 and 260<=rnd<=264) or (gid==1498741 and 125<=rnd<=128) or (gid==1498742 and 102<=rnd<=105):
    cur['board']=board(bodies[i][0]);cur['all']={j:list(b) for j,b in bodies.items()};cur['pearls']=list(pearls)
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);cur['eats']+=1
  elif k==4:
   a=p.pointer(0);cur['act']=a.u16(0) if a else None;cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==9:
   i=p.i32(0);hd=tile(p.pointer(0));tail=tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);cur['steps'].append(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   ids=[p.i32(0),p.i32(4)];cur['split']=ids;births[ids[1]]=[rnd,ids[0]]
   for z,i in enumerate(ids):bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);cur['deaths'].append([i,p.u16(4),list(bodies[i])]);bodies.pop(i)
   if i==q:dead=True
  if dead and eq in bodies and k in (1,9,10,11):
   dest=bodies[eq][0]
   for i,b in bodies.items():
    if teams[i]!=own:continue
    d=dist(b[0]).get(dest,99999);v=dict(r=rnd,event=ei,id=i,d=d,head=xy(b[0]),queen=xy(dest))
    if closest is None or d<closest['d']:closest=v
    if k==1 and cur['id']==i and d<=5:near.append(v)
 close()
 final={i:list(b) for i,b in bodies.items()}
 result=dict(gid=gid,w=w,h=h,own=own,q=q,eq=eq,turns=turns,births=births,teams=teams,near=near,closest=closest,final=final)
 (OUT/f'{gid}-detail.json').write_text(json.dumps(result,separators=(',',':')))
 print('\nGAME',gid,w,h,'closest',closest,'near turns',len(near),'first',near[:2])
 for t in [t for t in turns if t['id']==q][-3:]+[t for t in turns if any(d[0]==q for d in t['deaths'])]:
  print('TURN',t['r'],t['id'],'body',[xy(c) for c in t['body']],'dirs',t['dirs'],'steps',[xy(c) for c in t['steps']],'deaths',t['deaths'],'board',t.get('board'))
 print('final leaders',sorted([(i,teams[i],len(b)) for i,b in bodies.items()],key=lambda x:-x[2])[:8])
