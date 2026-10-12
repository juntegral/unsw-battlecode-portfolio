import sys,json
from pathlib import Path
from collections import deque,Counter,defaultdict
sys.dont_write_bytecode=True
sys.path.insert(0,'data/codex/astra/weak')
import analyze as prior
from ladder_replay import replay,edge_id,canonical_edges
OUT=Path(__file__).resolve().parent
for gid in (1492096,1492097,1492098):
 base=json.loads((OUT/f'{gid}.json').read_text());g=base['scan'];qd=next(d for d in g['deaths'] if d['id']==g['queens']['us']);q=g['queens']['us'];fq=g['queens']['them']
 root=replay.load(Path(f'data/online/smoke/one10-c1-old/M{gid}.replay')).root();lines=root.text(0).splitlines();w,h=map(int,lines[0].split()[1:3]);bodies={};teams={};raw=[];pearls=set()
 for l in lines:
  z=l.split()
  if z and z[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(z[3+2*k]),int(z[4+2*k])) for k in range(int(z[2])));teams[i]=int(z[1])
  elif z and z[0]=='EDGE':raw.append(tuple(map(int,z[1:4])))
 geo=prior.Geo(w,h,raw);edges=canonical_edges(w,h,raw)
 def vis(a,b):return min(abs(a[0]-b[0]),w-abs(a[0]-b[0]))<=3 and min(abs(a[1]-b[1]),h-abs(a[1]-b[1]))<=3
 def board(c):
  occ={xy:('Q' if i==q else 'K' if i==fq else 'A' if teams[i]==0 else 'B') if n==0 else ('a' if teams[i]==0 else 'b') for i,bb in bodies.items() for n,xy in enumerate(bb)}
  rows=[]
  for dy in range(-3,4):
   r=[]
   for dx in range(-3,4):
    xy=((c[0]+dx)%w,(c[1]+dy)%h);r.append(occ.get(xy,'*' if xy in pearls else '.'))
   rows.append(''.join(r))
  walls=[]
  for dy in range(-3,4):
   for dx in range(-3,4):
    xy=((c[0]+dx)%w,(c[1]+dy)%h)
    for d in (0,1,2,3):
     k,p=edges.get(edge_id(w,h,*xy,d),(0,-1))
     if k: walls.append([dx,dy,'NESW'[d],k,p])
  return dict(rows=rows,edges=walls,visible=[dict(id=i,team=teams[i],body=list(bb),visible_parts=sum(vis(c,z) for z in bb)) for i,bb in bodies.items() if any(vis(c,z) for z in bb)])
 turns=[];cur=None;r=-1;snaps={};qt=[];ats=[]
 def close():
  if cur is None:return
  i=cur['id'];cur['end']=list(bodies[i][0]) if i in bodies else None;cur['endL']=len(bodies.get(i,[]));turns.append(cur)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close();cur=None;r=p.i32(0)
  elif k==1:
   close();i=p.i32(0);bb=bodies[i];hh=bb[0];pv=[z for z in pearls if vis(hh,z)]
   cur=dict(r=r,event=idx,id=i,side=teams[i],L=len(bb),head=list(hh),pearl_view=len(pv),eats=0,moves=[],action=None,dirs=[])
   if (i==q and qd['round']-2<=r<=qd['round']) or (r==qd['round'] and i==qd['actor']) or (gid==1492097 and i==318 and r in (194,195)) or (gid==1492098 and i==95 and r in (178,179)):
    cur['board']=board(hh)
   if i==q and qd['round']-2<=r<=qd['round']:qt.append(cur)
   if r in (0,40,50,100,200,300,331,350,368,369,400,433,434,446,450,460,480,490,499) and r not in snaps:
    snaps[r]=[dict(id=i,side=teams[i],L=len(b),head=list(b[0])) for i,b in bodies.items()]
  elif k==3:
   xy=replay.point(p.pointer(0))
   if p.u32(0):pearls.add(xy)
   else:pearls.remove(xy);cur['eats']+=1
  elif k==4:
   a=p.pointer(0);cur['action']=a.u16(0) if a else None;cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else []
  elif k==9:
   i=p.i32(0);hd,tl=replay.point(p.pointer(0)),replay.point(p.pointer(1));bb=bodies[i]
   if hd!=bb[0]:bb.appendleft(hd);cur['moves'].append(list(hd))
   while len(bb)>1 and bb[-1]!=tl:bb.pop()
   assert bb[-1]==tl
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:bodies.pop(p.i32(0))
 close()
 out=dict(w=w,h=h,queen_turns=qt,turns=turns,snaps=snaps,final=[dict(id=i,side=teams[i],L=len(b),head=list(b[0])) for i,b in bodies.items()])
 (OUT/f'detail-{gid}.json').write_text(json.dumps(out))
 print(gid,'queen',[(t['r'],t['head'],t['dirs']) for t in qt],flush=True)
 for t in turns:
  if t.get('board') and t['id']!=q:print('attacker',t,flush=True)
 for lo,hi in ((0,50),(51,100),(101,200),(201,300),(301,400),(401,499)):
  print(lo,hi,[dict(turns=len(ts),eats=sum(t['eats'] for t in ts),split=sum(t['action']==1 for t in ts),no_eat_no_view=sum(t['eats']==0 and t['pearl_view']==0 and t['action']==0 for t in ts),no_eat_view=sum(t['eats']==0 and t['pearl_view']>0 and t['action']==0 for t in ts)) for s in (0,1) for ts in [[t for t in turns if t['side']==s and lo<=t['r']<=hi]]],flush=True)
