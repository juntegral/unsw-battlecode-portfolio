import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from spawn import read
from replay_format import point
from count_local import Geo
OUT=Path(__file__).parent

def scan(gid):
 root=read(Path(f'data/online/smoke/one10-c1-old/M{gid}.replay'))
 bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if not q:continue
  if q[0]=='MAP':w,h=map(int,q[1:3])
  if q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
  if q[0]=='DRAGON':
   i=len(bodies);teams[i]=int(q[1]);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
 g=Geo(w,h,raw);qs=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 tile=lambda p:point(p)[1]*w+point(p)[0]
 xy=lambda c:[c%w,c//w]
 rnd=-1;actor=None;cur=None;present=set();qturns=[[],[]];turns=[];deaths=[];snaps={};near=[];splits=[];eats=Counter();nat=Counter()
 def state():return [dict(queen=len(bodies.get(qs[s],())),alive=sum(teams[i]==s for i in bodies),longest=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),eats=eats[s],natural=nat[s]) for s in (0,1)]
 def context():return {i:list(b) for i,b in bodies.items()}
 def close():
  if cur is not None:
   cur['end']=list(bodies.get(actor,()));turns.append(cur)
   if actor in qs:qturns[qs.index(actor)].append(cur)
 def distances(src):
  seen={src:0};todo=deque([src])
  while todo:
   c=todo.popleft()
   if seen[c]>=5:continue
   for t in g.adj[c]:
    if t not in seen:seen[t]=seen[c]+1;todo.append(t)
  return seen
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close();cur=None
   if rnd>=0:snaps[rnd]=state()
   rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);cur=dict(r=rnd,i=actor,start=list(bodies[actor]),steps=[],eat=[],event=idx)
   if actor in qs or (gid==1492093 and actor==548 and 244<=rnd<=247) or (gid==1492094 and ((actor==86 and 123<=rnd<=125) or (actor in (900,957) and 465<=rnd<=479))):cur.update(bodies=context(),pearls=sorted(present))
   if qs[0] not in bodies and qs[1] in bodies and teams[actor]==0:
    d=distances(bodies[actor][0]).get(bodies[qs[1]][0],999)
    if d<=5:cur.update(bodies=context(),pearls=sorted(present))
    if d<=5:near.append(dict(r=rnd,i=actor,L=len(bodies[actor]),d=d,head=xy(bodies[actor][0]),queen=xy(bodies[qs[1]][0]),visible=bodies[qs[1]][0] in g.window(bodies[actor][0])))
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):present.add(c)
   else:
    present.remove(c);eats[teams[actor]]+=1;nat[teams[actor]]+=int(origin[c]);cur['eat'].append(c)
   if p.u32(0):origin[c]=actor is None
  elif k==4:
   a=p.pointer(0);cur['action']=a.u16(0) if a else None
   cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else []
  elif k==9:
   i=p.i32(0);hd=tile(p.pointer(0));tl=tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);cur['steps'].append(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   parent,child=p.i32(0),p.i32(4);splits.append(dict(r=rnd,parent=parent,child=child))
   for z,i in enumerate((parent,child)):bodies[i]=deque(tile(x) for x in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);d=dict(r=rnd,i=i,reason=p.u16(4),actor=actor,body=list(bodies[i]),turn=dict(cur),s=teams[i])
   if i in qs:d['bodies']=context()
   deaths.append(d);bodies.pop(i)
 close();snaps[rnd]=state()
 result=root.pointer(4);final=[]
 for s in (0,1):
  p=result.pointer(s);f=dict(zip(('alive','longest','total','queen'),[p.i32(x) for x in (0,4,8,12)]));final.append(f)
  assert all(snaps[rnd][s][k]==v for k,v in f.items())
 out=dict(game=gid,bot=root.text(1),w=w,h=h,final=final,queens=qs,qdeath=[next((d for d in deaths if d['i']==q),None) for q in qs],snaps=snaps,qturns=qturns,near=near,splits=splits,deaths=deaths,turns=turns,final_bodies=context(),teams=teams,raw=raw)
 (OUT/f'{gid}.json').write_text(json.dumps(out,separators=(',',':')))
 print(gid,'bot',out['bot'],'final',final,'qdeath',[(d['r'],d['reason'],d['actor'],len(d['body'])) if d else None for d in out['qdeath']],'near',len(near),'first',near[:2])
origin={}
for gid in (1492093,1492094,1492095):scan(gid)
