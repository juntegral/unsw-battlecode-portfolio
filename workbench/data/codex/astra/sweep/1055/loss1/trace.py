import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
from ladder_replay import replay,edge_id
import ast,types
geo_module=types.ModuleType('tq2_def_readonly')
geo_ast=ast.parse(open('data/analysis/ladder/dossier/work/tq2_def.py').read())
geo_ast.body=[n for n in geo_ast.body if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='main')]
exec(compile(geo_ast,'tq2_def.py','exec'),geo_module.__dict__)
Geo=geo_module.Geo
from collections import deque,Counter
from pathlib import Path
OUT=Path('data/codex/astra/sweep/1055/loss1')
JOBS=[('data/online/live-one1/b1501017',1501019),('data/online/live-one1/b1501017',1501020),('data/online/smoke/one12-c1-old',1501665)]
for folder,gid in JOBS:
 base=json.loads((OUT/f'{gid}-base.json').read_text()); root=replay.load(Path(folder)/f'M{gid}.replay').root()
 lines=root.text(0).splitlines();w,h=map(int,lines[0].split()[1:3]);bodies={};teams={};edges=[]
 for line in lines:
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]='AB'[int(q[1])]
  elif q[0]=='EDGE':edges.append(tuple(map(int,q[1:4])))
 geo=Geo(w,h,edges);qu=base['queens']['us'];qe=base['queens']['them'];ours=base['ours'];present={};drops=0;turn=None;r=-1;turns=[];near=[];full={};rs={}
 def xy(c):return [c%w,c//w]
 def view(a,b):return min(abs(a%w-b%w),w-abs(a%w-b%w))<=3 and min(abs(a//w-b//w),h-abs(a//w-b//w))<=3
 def capture():return {'bodies':{i:list(b) for i,b in bodies.items()},'pearls':list(present),'teams':dict(teams)}
 def close():
  if turn is not None:
   turn['end']=list(bodies.get(turn['id'],[]));turns.append(turn)
 def snapshot():
  return {s:sorted([[i,len(b),xy(b[0])] for i,b in bodies.items() if teams[i]==s],key=lambda x:(-x[1],x[0])) for s in 'AB'}
 for idx,ev in enumerate(root.pointer(3)):
  k=replay.EVENT_NAMES[ev.u16(0)];p=ev.pointer(0)
  if k=='roundStart':
   close();turn=None
   if r>=0:rs[r]=snapshot()
   r=p.i32(0)
  elif k=='turnStart':
   close();i=p.i32(0);head=bodies[i][0]
   turn={'r':r,'event':idx,'id':i,'side':teams[i],'body':list(bodies[i]),'action':None,'steps':[],'eats':[],'split':None,'deaths':[],'logs':[]}
   if i==qu or (gid==1501019 and 267<=r<=273) or (gid==1501020 and 419<=r<=422) or (gid==1501665 and 209<=r<=214):
    full[idx]=capture()
    turn['near']=[[z,len(b),xy(b[0])] for z,b in bodies.items() if view(head,b[0])]
   if qu not in bodies and qe in bodies and teams[i]==ours:
    target=bodies[qe][0];dist=geo.ball(head).get(target,99)
    if dist<=5:near.append([r,i,len(bodies[i]),xy(head),xy(target),dist])
  elif k=='dragonAction':
   a=p.pointer(0);turn['action']={'kind':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else []}
  elif k=='tileChange':
   x,y=replay.point(p.pointer(0));c=y*w+x
   if p.u32(0):present[c]='drop' if drops else 'spawn';drops=max(0,drops-1)
   else:turn['eats'].append([xy(c),present.pop(c)])
  elif k=='dragonUpdate':
   i=p.i32(0);x,y=replay.point(p.pointer(0));head=y*w+x;x,y=replay.point(p.pointer(1));tail=y*w+x;b=bodies[i]
   if b[0]!=head:
    turn['steps'].append([i,xy(head)]);b.appendleft(head)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k=='dragonSplit':
   turn['split']=[p.i32(0),p.i32(4)]
   for z,i in enumerate(turn['split']):
    bodies[i]=deque(pt.i32(4)*w+pt.i32(0) for pt in p.pointer(z));teams[i]='AB'[p.u16(8)]
  elif k=='dragonDeath':
   i=p.i32(0);turn['deaths'].append([i,len(bodies[i]),p.u16(4)]);drops=(len(bodies[i])+1)//2;bodies.pop(i)
  elif 'log' in k.lower():
   turn['logs'].append([k,p.text(0)])
 close();rs[r]=snapshot()
 out={'w':w,'h':h,'turns':turns,'near_after':near,'full':full,'rounds':rs}
 (OUT/f'{gid}-trace.json').write_text(json.dumps(out))
 print(gid,'saved',len(turns),'near after',len(near),near[:3],flush=True)
