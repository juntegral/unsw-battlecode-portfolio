import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'data/analysis/ladder/dossier/local'))
from scoreboard import load_replay
from replay_format import point
from count_local import Geo

def scan(gid):
 pth=ROOT/f'data/online/smoke/one13-c2-old/M{gid}.replay';root=load_replay(pth).root()
 w,h=map(int,root.text(0).splitlines()[0].split()[1:3]); b={};tm={};edges=[]
 for line in root.text(0).splitlines():
  z=line.split()
  if z[0]=='DRAGON':
   i=len(b);tm[i]=int(z[1]);b[i]=deque(int(z[4+2*k])*w+int(z[3+2*k]) for k in range(int(z[2])))
  if z[0]=='EDGE':edges.append(tuple(map(int,z[1:4])))
 geo=Geo(w,h,edges); queens=[min(i for i in b if tm[i]==s) for s in (0,1)]
 rnd=-1; actor=None;cur=None;turns=[];deaths=[];splits=[];snaps={};pearls=set();eat=Counter();qt=[];post=[];cache={}
 def xy(c):return [c%w,c//w]
 def state():return [dict(n=sum(tm[i]==s for i in b),total=sum(len(bb) for i,bb in b.items() if tm[i]==s),longest=max((len(bb) for i,bb in b.items() if tm[i]==s),default=0),queen=len(b.get(queens[s],())),eaten=eat[s]) for s in (0,1)]
 def bfs(src):
  if src not in cache:
   ds={src:0};q=deque([src])
   while q:
    c=q.popleft()
    for d in geo.adj[c]:
     if d not in ds:ds[d]=ds[c]+1;q.append(d)
   cache[src]=ds
  return cache[src]
 def distcheck(idx):
  if queens[0] not in b and queens[1] in b:
   c=b[queens[1]][0];pairs=[(bfs(bb[0]).get(c,99999),i) for i,bb in b.items() if tm[i]==0]
   if pairs:
    d,i=min(pairs);post.append(dict(round=rnd,event=idx,d=d,id=i,our=xy(b[i][0]),enemy=xy(c)))
 def finish():
  if cur is not None:cur['end']=xy(b[actor][0]) if actor in b else None;cur['endL']=len(b.get(actor,()))
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   finish()
   if rnd>=0:snaps[rnd]=state()
   rnd=p.i32(0);actor=None;cur=None
  elif k==1:
   finish();actor=p.i32(0)
   cur=dict(round=rnd,event=idx,id=actor,side=tm[actor],L=len(b[actor]),head=xy(b[actor][0]),steps=[],eats=0,logs=[])
   turns.append(cur)
   if actor in queens:
    cur['bodies']={i:list(bb) for i,bb in b.items()};cur['pearls']=sorted(pearls);qt.append(cur)
  elif k==3:
   x,y=point(p.pointer(0));c=y*w+x
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);eat[tm[actor]]+=1;cur['eats']+=1
  elif k==4:
   a=p.pointer(0);cur['actionKind']=a.u16(0) if a else None
   cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==6:
   if cur is not None:cur['logs'].append(p.text(0))
  elif k==9:
   i=p.i32(0);x,y=point(p.pointer(0));hd=y*w+x;x,y=point(p.pointer(1));tail=y*w+x
   if b[i][0]!=hd:b[i].appendleft(hd);cur['steps'].append(xy(hd))
   while len(b[i])>1 and b[i][-1]!=tail:b[i].pop()
   assert b[i][-1]==tail
  elif k==10:
   parent,child=p.i32(0),p.i32(4)
   before=len(b[parent]);oldhead=xy(b[parent][0])
   for z,i in enumerate((parent,child)):
    b[i]=deque(point(c)[1]*w+point(c)[0] for c in p.pointer(z));tm[i]=p.u16(8)
   splits.append(dict(round=rnd,event=idx,parent=parent,child=child,before=before,keep=len(b[parent]),childL=len(b[child]),head=oldhead))
  elif k==11:
   i=p.i32(0);d=dict(round=rnd,event=idx,id=i,side=tm[i],reason=p.u16(4),actor=actor,L=len(b[i]),body=[xy(c) for c in b[i]],turn=cur.copy())
   d['bodies']={i:list(bb) for i,bb in b.items()};deaths.append(d);b.pop(i)
  if k in (1,9,10,11):distcheck(idx)
 finish();snaps[rnd]=state();final=state()
 for s in (0,1):
  st=root.pointer(4).pointer(s)
  assert [final[s][f] for f in ('n','longest','total','queen')]==[st.i32(o) for o in (0,4,8,12)]
 def lead(st):return tuple(st[0][k] for k in ('queen','longest','total'))<tuple(st[1][k] for k in ('queen','longest','total'))
 permanent=next((r for r in sorted(snaps) if all(lead(snaps[x]) for x in snaps if x>=r)),None)
 data=dict(gid=gid,w=w,h=h,queens=queens,final=final,end=rnd,endReason=root.pointer(4).u16(2),permanent=permanent,teams=tm,edges=edges,snaps=snaps,turns=turns,deaths=deaths,splits=splits,post=post,sha=hashlib.sha256(pth.read_bytes()).hexdigest())
 (OUT/f'{gid}.json').write_text(json.dumps(data,separators=(',',':')))
 print(json.dumps({k:data[k] for k in ('gid','w','h','queens','final','end','endReason','permanent')}))
 print('QDEATHS',json.dumps([{k:d[k] for k in ('round','id','reason','actor','L','body')} for d in deaths if d['id'] in queens]))
 print('POST',min(post,key=lambda x:x['d']) if post else None,'close events',sum(x['d']<=5 for x in post))
 print('QSPLITS',[s for s in splits if s['parent'] in queens][:20])
 print('CHECKPOINTS',{r:snaps[r] for r in (0,10,20,50,100,200,300,400,499) if r in snaps})
for gid in (1510787,1510788,1510789):scan(gid)
