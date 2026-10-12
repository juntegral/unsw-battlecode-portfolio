import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/losses/counts']
from ladder_replay import replay
from count_replays import Geometry
from collections import deque
from pathlib import Path
O=Path('data/codex/astra/sweep/0539/loss1'); D=Path('data/online/live-one1/b1493690')
for gid in [1493690,1493693,1493694]:
 root=replay.load(D/f'M{gid}.replay').root(); txt=root.text(0); W,H=map(int,txt.splitlines()[0].split()[1:3]); bs={}; teams={}; raw=[]
 for ln in txt.splitlines():
  q=ln.split()
  if q and q[0]=='DRAGON':
   i=len(bs);bs[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2]))); teams[i]=int(q[1])
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 g=Geometry(W,H,raw); qu=min(i for i in bs if teams[i]==1); qe=min(i for i in bs if teams[i]==0)
 turns=[]; qt=[]; near=[]; deaths=[]; pearls=set(); snapshots={}; r=-1;t=None
 def state():return {i:[teams[i],len(b),list(b[0])] for i,b in bs.items()}
 def finalturn():
  if t is not None:t['end']=list(bs[t['id']]) if t['id'] in bs else []
 def board():
  x,y=bs[qu][0];occ={c:('Q' if i==qu and k==0 else 'q' if i==qu else 'A' if teams[i]==1 and k==0 else 'a' if teams[i]==1 else 'E' if k==0 else 'e') for i,b in bs.items() for k,c in enumerate(b)}
  return [''.join(occ.get(((x+dx)%W,(y+dy)%H),'*' if ((x+dx)%W,(y+dy)%H) in pearls else '.') for dx in range(-3,4)) for dy in range(-3,4)]
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0); p=ev.pointer(0)
  if k==0:
   finalturn();t=None
   if r>=0:snapshots[r]=state()
   r=p.i32(0)
  elif k==1:
   finalturn(); i=p.i32(0);t=dict(r=r,id=i,L=len(bs[i]),head=list(bs[i][0]),steps=[],eats=[],act=None); turns.append(t)
   if (gid==1493693 and i==982 and r==480) or (gid==1493694 and i==843 and r==466):
    t['pearls_now']=list(pearls);t['state_now']=state()
   if i==qu:
    t.update(board=board(),state=state(),bodies={z:list(b) for z,b in bs.items()},edges=[(c,g.moves[c[1]*W+c[0]]) for c in bs[i]]);qt.append(t)
   if qu not in bs and qe in bs and teams[i]==1:
    dd=g.distances(bs[qe][0][1]*W+bs[qe][0][0])[bs[i][0][1]*W+bs[i][0][0]]
    if dd<=5:near.append(dict(r=r,id=i,L=len(bs[i]),head=list(bs[i][0]),q=list(bs[qe][0]),d=dd))
  elif k==4:
   a=p.pointer(0); t['act']=dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else [])
  elif k==3:
   c=replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:
    pearls.remove(c)
    if t:t['eats'].append(c)
  elif k==9:
   i=p.i32(0);hd=replay.point(p.pointer(0));tl=replay.point(p.pointer(1));b=bs[i]
   if b[0]!=hd:
    b.appendleft(hd)
    if t:t['steps'].append(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   t['split']=[p.i32(0),p.i32(4),len(bs[p.i32(0)]),[len(p.pointer(z)) for z in (0,1)]]
   for z,i in enumerate((p.i32(0),p.i32(4))):bs[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);deaths.append(dict(r=r,id=i,actor=t['id'],reason=p.u16(4),state=state(),body=list(bs[i])));bs.pop(i)
 finalturn();snapshots[r]=state()
 o=dict(W=W,H=H,qu=qu,qe=qe,qt=qt[-3:],turns=turns,near=near,deaths=deaths,snapshots=snapshots)
 (O/f'{gid}-moments.json').write_text(json.dumps(o))
 print('\nGAME',gid,'size',W,H,'near',len(near),near[:3])
 for q in qt[-3:]:print('Q',q['r'],q['head'],q['L'],'act',q['act'],'steps',q['steps'],'end',q['end'],'\n'+'\n'.join(q['board']))
 for d in deaths:
  if d['id']==qu:
   print('DEATH',d)
   print('ATTACK TURNS',[t for t in turns if t['id']==d['actor'] and d['r']-2<=t['r']<=d['r'] and t['id']!=qu])
