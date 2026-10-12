import sys,json,ast
from pathlib import Path
from collections import deque,Counter,defaultdict
sys.dont_write_bytecode=True
sys.path.insert(0,'data/analysis/ladder/dossier/local')
import scoreboard as sb
sys.path.insert(0,'tools')
from ladder_replay import edge_id,canonical_edges
# Reuse the existing geometry class without its command-line main.
src=Path('data/analysis/ladder/dossier/work/tq2_near.py').read_text(); tree=ast.parse(src)
env=dict(defaultdict=defaultdict,deque=deque,canonical_edges=canonical_edges,edge_id=edge_id,STEP=((0,-1),(1,0),(0,1),(-1,0)),CAP=8)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Geo'],type_ignores=[]),'tq2_near.Geo','exec'),env)
Geo=env['Geo']; OUT=Path(__file__).parent

def scan(gid):
 root=sb.load_replay(Path(f'data/online/smoke/one12-c1-old/M{gid}.replay')).root()
 lines=root.text(0).splitlines(); w,h=map(int,lines[0].split()[1:3]); bodies={};teams={};raw=[]
 for line in lines:
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 g=Geo(w,h,raw); qids=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 def snap():return {str(i):list(b) for i,b in bodies.items()}
 def state():return [dict(n=sum(teams[i]==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),longest=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),queen=len(bodies.get(qids[s],[])),top=sorted([(len(b),i) for i,b in bodies.items() if teams[i]==s],reverse=True)[:4]) for s in (0,1)]
 pearls=set();turns=[];deaths=[];splits=[];snaps={};qturns=[[],[]];close=[];r=-1;actor=None;t=None;qd=False
 def observe(idx):
  if not qd or qids[1] not in bodies:return
  tar=bodies[qids[1]][0]
  # Directed shortest paths from each friendly head, walls/portals included; bodies ignored.
  for i,b in bodies.items():
   if teams[i]==0:
    d=g.ball(b[0]).get(tar,99)
    if d<=5:close.append([r,idx,i,len(b),b[0],tar,d])
 def finish():
  nonlocal t
  if t is not None:
   t['end']=list(bodies.get(t['id'],[]));t['finalstate']=state() if t['id'] in qids else None
   turns.append(t);t=None
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   finish()
   if r>=0:snaps[r]=state()
   r=p.i32(0);actor=None
  elif k==1:
   finish();actor=p.i32(0);b=bodies[actor]
   t=dict(r=r,idx=idx,id=actor,side=teams[actor],body=list(b),eaten=[],moves=[],action=None,n=sum(teams[i]==teams[actor] for i in bodies))
   if actor in qids:
    t['board']=snap();t['pearls']=list(pearls);qturns[teams[actor]].append(t)
   if qd:observe(idx)
  elif k==3:
   c=sb.replay_format.point(p.pointer(0));cell=c[1]*w+c[0]
   if p.u32(0):pearls.add(cell)
   else:
    pearls.remove(cell)
    if t:t['eaten'].append(cell)
  elif k==4:
   a=p.pointer(0)
   if t:t['action']={'kind':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [],'data':a.i32(4)} if a else None
  elif k==9:
   i=p.i32(0);hd,tl=[sb.replay_format.point(p.pointer(z)) for z in (0,1)];hd=hd[1]*w+hd[0];tl=tl[1]*w+tl[0];b=bodies[i]
   if b[0]!=hd:
    if t:t['moves'].append([b[0],hd])
    b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
   observe(idx)
  elif k==10:
   par,ch=p.i32(0),p.i32(4);splits.append([r,par,ch,len(bodies[par]),sum(teams[i]==teams[par] for i in bodies)])
   for z,i in enumerate((par,ch)):
    bodies[i]=deque(pt.i32(4)*w+pt.i32(0) for pt in p.pointer(z));teams[i]=p.u16(8)
   observe(idx)
  elif k==11:
   i=p.i32(0);rec=dict(r=r,idx=idx,id=i,actor=actor,reason=p.u16(4),body=list(bodies[i]),action=t['action'],actorbody=t['body'],moves=list(t['moves']),eaten=list(t['eaten']))
   if i in qids:rec['board']=snap();rec['pearls']=list(pearls)
   deaths.append(rec);bodies.pop(i)
   if i==qids[0]:qd=True
   observe(idx)
 finish();snaps[r]=state()
 final=root.pointer(4)
 for s in (0,1):
  p=final.pointer(s);assert [p.i32(x) for x in (0,4,8,12)]==[snaps[r][s][x] for x in ('n','longest','total','queen')]
 out=dict(gid=gid,bot=[root.text(1),root.text(2)],w=w,h=h,queens=qids,teams=teams,edges=raw,turns=turns,qturns=qturns,deaths=deaths,splits=splits,snaps=snaps,close=close)
 (OUT/f'detail-{gid}.json').write_text(json.dumps(out,separators=(',',':')))
 print(gid,'qdeaths',[d for d in deaths if d['id'] in qids],'close count',len(close),'first',close[:1],flush=True)
for gid in (1501674,1501675,1501676):scan(gid)
