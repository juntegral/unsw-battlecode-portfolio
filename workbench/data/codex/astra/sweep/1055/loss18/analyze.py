import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as lr
from spawn import read
from count_local import Geo
OUT=Path(__file__).parent

def run(gid):
 p=Path(f'data/online/smoke/one13-c1-old/M{gid}.replay'); j=json.loads(p.with_name(f'game-{gid}.json').read_text())
 base=json.loads((OUT/f'{gid}-base.json').read_text()) if (OUT/f'{gid}-base.json').exists() else lr.scan(p,j,'one13-c1-old',set());base.pop('intervals',None)
 (OUT/f'{gid}-base.json').write_text(json.dumps(base))
 print(gid,{k:base[k] for k in ('bots','queens','final','last_round','end_reason','q_eats','q_splits')},flush=True)
 print('queen deaths',[d for d in base['deaths'] if d['id'] in base['queens'].values()],flush=True)
 root=read(p);w,h=map(int,root.text(0).splitlines()[0].split()[1:3]);bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 oq,tq=base['queens']['us'],base['queens']['them'];g=Geo(w,h,raw);tile=lambda p:lr.replay.point(p)[1]*w+lr.replay.point(p)[0]
 rnd=-1;actor=None;cur=None;turns=[];present=set();near=[];cached={};snapshots={};deaths=[]
 def ball(c):
  if c not in cached:
   d={c:0};queue=deque([c])
   while queue:
    s=queue.popleft()
    if d[s]>=5:continue
    for t in g.adj[s]:
     if t not in d:d[t]=d[s]+1;queue.append(t)
   cached[c]=d
  return cached[c]
 def close():
  if cur is not None:
   cur['end']=list(bodies.get(actor,[]));turns.append(cur)
 def observe(ev):
  if oq not in bodies and tq in bodies:
   for i,b in bodies.items():
    if teams[i]==0:
     dist=ball(b[0]).get(bodies[tq][0],99)
     if dist<=5:near.append([rnd,ev,i,dist,b[0],bodies[tq][0]])
 for ix,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close();cur=None;actor=None;rnd=p.i32(0)
  elif k==1:
   close();actor=p.i32(0);cur={'r':rnd,'id':actor,'body':list(bodies[actor]),'eats':0,'moves':[],'splits':[],'event':ix}
   if actor in (0,1):cur['all']={i:list(b) for i,b in bodies.items()};cur['pearls']=sorted(present)
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):present.add(c)
   else:present.remove(c);cur['eats']+=1
  elif k==4:
   a=p.pointer(0);cur['action_kind']=a.u16(0) if a else None;cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==9:
   i=p.i32(0);hd,tl=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);cur['moves'].append(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
   observe(ix)
  elif k==10:
   par,ch=p.i32(0),p.i32(4)
   for z,i in enumerate((par,ch)):bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
   cur['splits'].append([par,ch,len(bodies[par]),len(bodies[ch])]);observe(ix)
  elif k==11:
   i=p.i32(0);deaths.append({'r':rnd,'id':i,'actor':actor,'body':list(bodies[i]),'all':{i:list(b) for i,b in bodies.items()},'pearls':sorted(present),'reason':p.u16(4),'event':ix});bodies.pop(i);observe(ix)
 close()
 out={'w':w,'h':h,'teams':teams,'turns':turns,'near':near,'deaths':deaths,'final_bodies':{i:list(b) for i,b in bodies.items()}}
 (OUT/f'{gid}-detail.json').write_text(json.dumps(out))
 print('last queen turns',[(t['r'],t['body'],t['end'],t['dirs'],t['eats'],t['splits']) for t in turns if t['id']==oq][-8:],flush=True)
 print('near',len(near),near[:3],flush=True)
 print('checkpoints',[(r,base['snapshots'].get(r)) for r in (0,50,100,200,300,400,499)],flush=True)
for gid in (1506216,1506217,1506218):run(gid)
