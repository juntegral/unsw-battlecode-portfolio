import sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
import json
ROOT=Path.cwd(); OUT=ROOT/'data/codex/astra/sweep/0436/loss1'
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'data/analysis/ladder/dossier/local')]
import ladder_replay as lr
import replay_format as rf
from count_local import Geo
IDS=[1487473,1487474,1487478,1487479,1487486]
for gid in IDS:
 p=ROOT/f'data/online/smoke/one9-k1-old/M{gid}.replay'; meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 base=lr.scan(p,meta,'one9-k1-old',set())
 root=rf.load(p).root(); w,h=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  z=line.split()
  if z and z[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque(int(z[4+2*k])*w+int(z[3+2*k]) for k in range(int(z[2])));teams[i]=int(z[1])
  elif z and z[0]=='EDGE':raw.append(tuple(map(int,z[1:4])))
 geo=Geo(w,h,raw); qs=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 qdeath=next((d for d in base['deaths'] if d['id']==qs[0]),None); attacker=qdeath['actor'] if qdeath else None
 rnd=-1;actor=None;pearls=set();qt=[];turn=None;attacks=[];near=[];minnear=None;after_turns=0;nearids=set();qpositions=Counter();trace=[]
 cache={}
 def dist(src):
  if src not in cache:
   ds={src:0}; queue=deque([src])
   while queue:
    a=queue.popleft()
    for b in geo.adj[a]:
     if b not in ds:ds[b]=ds[a]+1;queue.append(b)
   cache[src]=ds
  return cache[src]
 def xy(c):return [c%w,c//w]
 def state():return {str(i):[len(b),xy(b[0])] for i,b in bodies.items()}
 def frame():
  hd=bodies[qs[0]][0]; win=geo.window(hd);oc={c:('Q' if i==qs[0] and k==0 else 'q' if i==qs[0] else 'X' if i==attacker and k==0 else 'x' if i==attacker else 'A' if teams[i]==0 and k==0 else 'a' if teams[i]==0 else 'B' if k==0 else 'b') for i,b in bodies.items() for k,c in enumerate(b)}
  lines=[]
  for dy in range(-3,4):
   north='';middle=''
   for dx in range(-3,4):
    c=((hd//w+dy)%h)*w+(hd%w+dx)%w
    north+='+'+({0:' ',1:'-',2:'@'}[geo.moves[c][0][0]])
    middle+=({0:' ',1:'|',2:'@'}[geo.moves[c][3][0]])+oc.get(c,'*' if c in pearls else '.')
   lines+=[north+'+',middle+({0:' ',1:'|',2:'@'}[geo.moves[c][1][0]])]
  lines+=[''.join('+'+{0:' ',1:'-',2:'@'}[geo.moves[((hd//w+3)%h)*w+(hd%w+dx)%w][2][0]] for dx in range(-3,4))+'+']
  return dict(round=rnd,event=idx,head=xy(hd),length=len(bodies[qs[0]]),body=[xy(c) for c in bodies[qs[0]]],board=lines,visible={str(i):dict(length=len(b),head=xy(b[0]),head_visible=b[0] in win,parts=sum(c in win for c in b),edge=any(c in win and (min(abs(c%w-hd%w),w-abs(c%w-hd%w))==3 or min(abs(c//w-hd//w),h-abs(c//w-hd//w))==3) for c in b)) for i,b in bodies.items() if any(c in win for c in b)},path=[],eats=[])
 def check_near():
  global minnear
  if qdeath and idx>qdeath['event'] and qs[1] in bodies:
   dest=bodies[qs[1]][0]; qpositions[dest]+=1
   for i,b in bodies.items():
    if teams[i]!=0:continue
    distance=dist(b[0]).get(dest,9999)
    if minnear is None or distance<minnear['distance']:minnear=dict(round=rnd,event=idx,id=i,length=len(b),head=xy(b[0]),enemy_head=xy(dest),distance=distance)
    if distance<=5:
     nearids.add(i)
     if len(near)<5:near.append(dict(round=rnd,event=idx,id=i,length=len(b),head=xy(b[0]),enemy_head=xy(dest),distance=distance))
 for idx,e in enumerate(root.pointer(3)):
  k=e.u16(0); pp=e.pointer(0);tile=lambda ptr:(lambda t:t[1]*w+t[0])(rf.point(ptr))
  if k==0:rnd=pp.i32(0);actor=None
  elif k==1:
   actor=pp.i32(0);turn=None
   if actor==qs[0]:turn=frame();qt.append(turn)
   if actor==attacker and actor!=qs[0] and qdeath and qdeath['round']-3<=rnd<=qdeath['round']:
    attacks.append(dict(round=rnd,id=actor,length=len(bodies[actor]),head=xy(bodies[actor][0]),state=state(),path=[],eats=[]));turn=attacks[-1]
   check_near()
  elif k==4:
   a=pp.pointer(0)
   if turn is not None:turn['action_kind']=a.u16(0) if a else None;turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==3:
   c=tile(pp.pointer(0))
   if pp.u32(0):pearls.add(c)
   else:
    pearls.remove(c)
    if turn is not None:turn['eats'].append(xy(c))
  elif k==9:
   i=pp.i32(0);hd=tile(pp.pointer(0));tail=tile(pp.pointer(1));b=bodies[i]
   if b[0]!=hd:
    b.appendleft(hd)
    if turn is not None:turn['path'].append(xy(hd))
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
   check_near()
  elif k==10:
   for z,i in enumerate((pp.i32(0),pp.i32(4))):bodies[i]=deque(tile(t) for t in pp.pointer(z));teams[i]=pp.u16(8)
   check_near()
  elif k==11:
   bodies.pop(pp.i32(0));check_near()
 snaps=base['snapshots']; losing=[r for r,st in snaps.items() if tuple(st['us'][k] for k in ('queen_length','longest','total'))>=tuple(st['them'][k] for k in ('queen_length','longest','total'))]
 out={k:base[k] for k in ('gid','map','bots','queens','final','last_round','end_reason','winner','q_eats','q_splits','eats','anomalies')}
 out.update(size=[w,h],queen_death=qdeath,their_queen_death=next((d for d in base['deaths'] if d['id']==qs[1]),None),last_nonlosing=max(losing,default=-1),last_queen_turns=qt[-3:],queen_turns=qt,attacker_turns=attacks,postdeath_near=near,postdeath_min=minnear,postdeath_near_ids=len(nearids),their_queen_positions=[(xy(c),n) for c,n in qpositions.most_common(8)],checkpoints={str(r):snaps[r] for r in [0,50,100,150,200,250,300,350,400,450,499] if r in snaps},long_deaths=[d for d in base['deaths'] if d['side']=='us' and d['length']>=10])
 (OUT/f'{gid}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 print(json.dumps({k:v for k,v in out.items() if k not in ('last_queen_turns','attacker_turns','checkpoints','long_deaths','queen_death','their_queen_death')}))
 print('QDEATH',qdeath,'THEIRS',out['their_queen_death']); print('QT',qt[-3:]);print('ATTACK',attacks)
