import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as LR
from scoreboard import load_replay
from count_local import Geo
OUT=Path('data/codex/astra/sweep/1055/loss47'); SM=Path('data/online/smoke/one13-k2-old')
for gid in (1513836,1513839,1513840):
 root=load_replay(SM/f'M{gid}.replay').root();lines=root.text(0).splitlines();w,h=map(int,lines[0].split()[1:3]);bs={};teams={};raw=[]
 for l in lines:
  q=l.split()
  if q and q[0]=='DRAGON':
   i=len(bs);bs[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 geo=Geo(w,h,raw); qs=[min(i for i in bs if teams[i]==s) for s in (0,1)]
 rev=[[] for _ in geo.adj]
 for c,adj in enumerate(geo.adj):
  for t in adj:rev[t].append(c)
 distcache={}
 def distances(dst):
  if dst not in distcache:
   ds={dst:0};queue=deque([dst])
   while queue:
    c=queue.popleft()
    for t in rev[c]:
     if t not in ds:ds[t]=ds[c]+1;queue.append(t)
   distcache[dst]=ds
  return distcache[dst]
 def man(a,b):
  dx=abs(a%w-b%w);dy=abs(a//w-b//w);return min(dx,w-dx)+min(dy,h-dy)
 def frame():return dict(bodies={i:list(b) for i,b in bs.items()},pearls=list(pearls),teams=teams.copy(),round=rnd,event=idx)
 def close():
  if turn is not None:
   turn['end']=list(bs.get(turn['id'],()));turn['endL']=len(turn['end']);turn['team']=teams[turn['id']]
   turns.append(turn)
 rnd=-1;turn=None;actor=None;pearls={};turns=[];qframes=deque(maxlen=3);deadframes=[];deaths=[];splits=[];near=[];minimum=None;eqpos=Counter();qdead=False
 def check_near():
  global minimum
  if not qdead or qs[1] not in bs:return
  dst=bs[qs[1]][0];ds=distances(dst)
  for i,b in bs.items():
   if teams[i]:continue
   n=ds.get(b[0],99999);x=dict(round=rnd,event=idx,id=i,L=len(b),head=b[0],queen=dst,distance=n,manhattan=man(b[0],dst))
   if minimum is None or n<minimum['distance']:minimum=x
   if n<=5:near.append(x)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0)
  if k not in (0,1,3,4,9,10,11):continue
  p=ev.pointer(0)
  if k==0:
   close();turn=None;rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);turn=dict(round=rnd,event=idx,id=actor,start=list(bs[actor]),L=len(bs[actor]),eats=[],path=[],heads={i:[len(b),b[0]] for i,b in bs.items()})
   if actor==qs[0]:qframes.append(frame())
   if actor==qs[1] and qdead:eqpos[bs[actor][0]]+=1
   check_near()
  elif k==3:
   xy=LR.replay.point(p.pointer(0));c=xy[1]*w+xy[0]
   if p.u32(0):pearls[c]='spawn' if actor is None else 'drop'
   else:turn['eats'].append([c,pearls.pop(c)])
  elif k==4:
   a=p.pointer(0);turn['action']=a.u16(0) if a else None
   turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==9:
   i=p.i32(0);xy=LR.replay.point(p.pointer(0));hd=xy[1]*w+xy[0];xy=LR.replay.point(p.pointer(1));tl=xy[1]*w+xy[0];b=bs[i]
   if b[0]!=hd:b.appendleft(hd);turn['path'].append(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
   if (teams[i]==0 or i==qs[1]):check_near()
  elif k==10:
   par,ch=p.i32(0),p.i32(4)
   for z,i in enumerate((par,ch)):
    bs[i]=deque(LR.replay.point(t)[1]*w+LR.replay.point(t)[0] for t in p.pointer(z));teams[i]=p.u16(8)
   splits.append(dict(round=rnd,parent=par,child=ch,L=turn['L'],keep=len(bs[par]),give=len(bs[ch])))
   check_near()
  elif k==11:
   i=p.i32(0);deaths.append(dict(round=rnd,id=i,actor=actor,reason=p.u16(4),L=len(bs[i]),head=bs[i][0]))
   if i==qs[0]:deadframes=list(qframes)+[frame()];qdead=True
   bs.pop(i);check_near()
 close()
 for t in turns:
  if t['id'] not in qs and not (t['round']>=130 and t['id'] in (139,)):
   t.pop('heads',None)
 data=dict(gid=gid,w=w,h=h,qs=qs,turns=turns,qframes=deadframes,splits=splits,deaths=deaths,nearest_after=minimum,near5=near,eq_positions=dict(eqpos),raw_edges=raw)
 (OUT/f'{gid}-detail.json').write_text(json.dumps(data,separators=(',',':')))
 print(gid,'done turns',len(turns),'nearest',minimum,'near5 unique',len({(n['round'],n['id']) for n in near}),flush=True)
