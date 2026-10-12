import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'data/analysis/ladder/dossier/local')]
import ladder_replay as lr
import scoreboard as sb
from count_local import Geo

def scan(gid):
 path=ROOT/f'data/online/smoke/one11-p1-old/M{gid}.replay'
 meta=json.loads(path.with_name(f'game-{gid}.json').read_text())
 root=sb.load_replay(path).root()
 lr.replay.load=lambda _:type('Loaded',(),{'root':lambda _:root})()
 base=lr.scan(path,meta,path.parent.name,set())
 bodies,teams,edges={},{},[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='MAP':w,h=map(int,q[1:3])
  if q[0]=='EDGE':edges.append(tuple(map(int,q[1:4])))
  if q[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2]))); teams[i]=int(q[1])
 geo=Geo(w,h,edges); queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 tile=lambda p: p.i32(4)*w+p.i32(0)
 xy=lambda c:[c%w,c//w]
 present=set(); turns=[]; qt=[]; history=[]; checkpoints={}; distances={}; contacts=[]
 rnd=-1; actor=None; t=None
 def dist(src):
  if src not in distances:
   ds={src:0}; q=deque([src])
   while q:
    c=q.popleft()
    if ds[c]>=5:continue
    for z in geo.adj[c]:
     if z not in ds:ds[z]=ds[c]+1;q.append(z)
   distances[src]=ds
  return distances[src]
 def contact(event):
  if queens[0] not in bodies and queens[1] in bodies:
   qh=bodies[queens[1]][0]; ds=dist(qh)
   near=[(i,ds[b[0]],xy(b[0])) for i,b in bodies.items() if teams[i]==0 and b[0] in ds]
   if near:contacts.append(dict(round=rnd,event=event,queen=xy(qh),ours=near))
 def close():
  if t is not None:
   t['end']=list(bodies.get(actor,())); t['end_length']=len(t['end'])
 def board(hd):
  chars={c:'.' for c in range(w*h)}
  for c in present:chars[c]='*'
  for i,b in bodies.items():
   for c in b:chars[c]='q' if i==queens[0] else 'a' if teams[i]==0 else 'b'
   chars[b[0]]='Q' if i==queens[0] else 'K' if i==queens[1] else 'A' if teams[i]==0 else 'B'
  rows=[]
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    c=((hd//w+dy)%h)*w+(hd%w+dx)%w
    row.append(chars[c])
   rows.append(''.join(row))
  ed=[]
  for c in geo.window(hd):
   for d,(k,z) in enumerate(geo.moves[c]):
    if k: ed.append([xy(c),'NESW'[d],k,xy(z)])
  return rows,ed
 def snap():return [[i,len(b),xy(b[0])] for i,b in bodies.items()]
 for ix,ev in enumerate(root.pointer(3)):
  k=ev.u16(0); p=ev.pointer(0)
  if k==0:
   close();t=None
   if rnd>=0:checkpoints[rnd]=snap()
   rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0)
   t=dict(round=rnd,event=ix,id=actor,side=teams[actor],length=len(bodies[actor]),head=xy(bodies[actor][0]),body=list(bodies[actor]),eat=0,steps=[],action=None)
   turns.append(t)
   if actor==queens[0] or (gid==1498743 and actor in [892,1093,1059,1026] and rnd>=450) or (gid==1498746 and actor==8 and 37<=rnd<=100) or (gid==1498745 and actor==171 and rnd>=350):
    t['board'],t['edges']=board(bodies[actor][0]);t['all']={i:list(b) for i,b in bodies.items()};t['pearls']=list(present)
   if actor==queens[0]:qt.append(t)
   contact(ix)
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):present.add(c)
   else:present.remove(c);t['eat']+=1
  elif k==4:
   a=p.pointer(0);t['action']=a.u16(0);t['dirs']=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else [];t['childSize']=a.i32(4) if a.u16(0)==1 else None
  elif k==9:
   i=p.i32(0);hd=tile(p.pointer(0));tail=tile(p.pointer(1));b=bodies[i]
   if hd!=b[0]:
    if i==actor:t['steps'].append(xy(hd))
    b.appendleft(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
   contact(ix)
  elif k==10:
   parent,child=p.i32(0),p.i32(4)
   history.append(dict(round=rnd,event=ix,kind='split',id=parent,child=child,before=len(bodies[parent])))
   for z,i in enumerate((parent,child)):bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
   history[-1].update(parent_length=len(bodies[parent]),child_length=len(bodies[child]))
   contact(ix)
  elif k==11:
   i=p.i32(0)
   history.append(dict(round=rnd,event=ix,kind='death',id=i,length=len(bodies[i]),reason=p.u16(4),actor=actor,head=xy(bodies[i][0])))
   bodies.pop(i);contact(ix)
 close();checkpoints[rnd]=snap()
 for s in (0,1):
  actual=[sum(teams[i]==s for i in bodies),max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),sum(len(b) for i,b in bodies.items() if teams[i]==s),len(bodies.get(queens[s],()))]
  assert actual==[root.pointer(4).pointer(s).i32(o) for o in (0,4,8,12)]
 out=dict(gid=gid,w=w,h=h,queens=queens,teams=teams,final=base['final'],eats=base['eats'],snapshots=base['snapshots'],deaths=base['deaths'],history=history,turns=turns,queen_turns=qt,contacts=contacts,checkpoints=checkpoints,anomalies=base['anomalies'])
 (OUT/f'{gid}.json').write_text(json.dumps(out,separators=(',',':')))
 print(gid,'final',base['final'],'eats',base['eats'],'anomalies',base['anomalies'])
 print('queens',queens,'deaths',[d for d in history if d['kind']=='death' and d['id'] in queens])
 print('largest deaths',sorted([d for d in history if d['kind']=='death' and teams[d['id']]==0],key=lambda d:-d['length'])[:12])
 print('contacts',len(contacts),contacts[:2])
for g in [1498743,1498745,1498746]:scan(g)
