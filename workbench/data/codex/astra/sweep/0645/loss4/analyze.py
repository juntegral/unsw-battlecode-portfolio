import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
ROOT=Path.cwd(); OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'tools')); import ladder_replay as lr
sys.path.insert(0,str(ROOT/'data/analysis/ladder/dossier/local')); from count_local import Geo
from scoreboard import load_replay
for gid in (1498748,1498749,1498751):
 p=ROOT/f'data/online/smoke/one11-p1-old/M{gid}.replay'; meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 base=lr.scan(p,meta,'one11-p1-old',set()); base.pop('intervals'); base.pop('natural'); base.pop('pearls'); base.pop('text')
 root=load_replay(p).root(); w,h=map(int,root.text(0).splitlines()[0].split()[1:3]); b={}; tm={}; edges=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(b); tm[i]=int(q[1]); b[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
  if q and q[0]=='EDGE':edges.append(tuple(map(int,q[1:4])))
 g=Geo(w,h,edges); qs=[min(i for i in b if tm[i]==s) for s in (0,1)]; rnd=-1; actor=None; pearls=set(); turns=[]; cur=None; queen_hist=[]; close=[]; mind=None; qdead=False; eat=Counter(); split=[]; logs=[]; distcache={}
 def pt(p):
  x,y=lr.replay.point(p);return y*w+x
 def snap():return {i:dict(L=len(v),head=[v[0]%w,v[0]//w]) for i,v in b.items()}
 def ds(target):
  if target not in distcache:
   # Reverse edges give directed movement distance to target, including portals.
   rev=[[] for _ in range(w*h)]
   for a,ns in enumerate(g.adj):
    for z in ns:rev[z].append(a)
   d={target:0};q=deque([target])
   while q:
    a=q.popleft()
    for z in rev[a]:
     if z not in d:d[z]=d[a]+1;q.append(z)
   distcache[target]=d
  return distcache[target]
 def check():
  global mind
  if not qdead or qs[1] not in b:return
  d=ds(b[qs[1]][0]);cand=[(d.get(v[0],99999),i) for i,v in b.items() if tm[i]==0]
  if not cand:return
  gap,i=min(cand); row=dict(r=rnd,id=i,gap=gap,head=[b[i][0]%w,b[i][0]//w],queen=[b[qs[1]][0]%w,b[qs[1]][0]//w])
  if mind is None or gap<mind['gap']:mind=row
  if gap<=5 and (not close or (rnd,i)!= (close[-1]['r'],close[-1]['id'])):close.append(row)
 for ei,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);v=ev.pointer(0)
  if k==0:rnd=v.i32(0)
  elif k==1:
   actor=v.i32(0);cur=dict(r=rnd,id=actor,L=len(b[actor]),head=[b[actor][0]%w,b[actor][0]//w],eats=0);turns.append(cur)
   if actor==qs[0]:
    occupied={c for body in b.values() for c in body}; cur['adjacent_pearls']=[z for k,z in g.moves[b[actor][0]] if k!=1 and z in pearls and z not in occupied]; cur['view_pearls']=len(pearls & g.window(b[actor][0])); qh=dict(cur);qh['bodies']={i:list(z) for i,z in b.items()};qh['pearls']=list(pearls);queen_hist.append(qh)
  elif k==3:
   c=pt(v.pointer(0))
   if v.u32(0):pearls.add(c)
   else:
    pearls.discard(c);eat[actor]+=1;cur['eats']+=1
    if actor==qs[0]:queen_hist[-1]['eats']+=1
  elif k==6:logs.append(dict(r=rnd,id=v.i32(0),text=v.text(0)))
  elif k==4:
   a=v.pointer(0); action=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else ('split' if a and a.u16(0)==1 else 'none');cur['action']=action
   if actor==qs[0]:queen_hist[-1]['action']=action
  elif k==9:
   i=v.i32(0);hd=pt(v.pointer(0));tl=pt(v.pointer(1));z=b[i]
   if z[0]!=hd:z.appendleft(hd)
   while len(z)>1 and z[-1]!=tl:z.pop()
   assert z[-1]==tl
  elif k==10:
   ids=[v.i32(0),v.i32(4)];split.append(dict(r=rnd,ids=ids,before=len(b[ids[0]])))
   for j,i in enumerate(ids):b[i]=deque(pt(c) for c in v.pointer(j));tm[i]=v.u16(8)
  elif k==11:
   i=v.i32(0)
   if i==qs[0]:qdead=True
   b.pop(i)
  if k in (1,9,10,11):check()
 out=dict(base=base,w=w,h=h,queens=qs,final=snap(),queen_last3=queen_hist[-3:],queen_turns=[{k:v for k,v in z.items() if k not in ('bodies','pearls')} for z in queen_hist],nearest=mind,close=close,turns=turns,eat=dict(eat),splits=split,logs=logs,teams=tm)
 (OUT/f'{gid}.json').write_text(json.dumps(out,ensure_ascii=False))
 print(gid,'bots',base['bots'],'final',base['final'],'qdeath',[d for d in base['deaths'] if d['id'] in qs],'near',mind,'close',len(close))
