import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque
sys.path.insert(0,'data/analysis/ladder/dossier/local')
import spawn
from replay_format import point
from count_local import Geo
OUT=Path(__file__).parent
out={}
for gid,qr,aid in ((1506219,241,518),(1506220,159,24),(1506221,173,66)):
 d=json.loads((OUT/f'{gid}.json').read_text());root=spawn.read(Path(f'data/online/smoke/one13-c1-old/M{gid}.replay'));w,h=d['w'],d['h'];b={};team={};raw=[]
 for line in root.text(0).splitlines():
  a=line.split()
  if a[0]=='DRAGON':i=len(b);team[i]=int(a[1]);b[i]=deque(int(a[4+2*k])*w+int(a[3+2*k]) for k in range(int(a[2])))
  elif a[0]=='EDGE':raw.append(tuple(map(int,a[1:4])))
 g=Geo(w,h,raw);r=-1;see=[];qsee=[];selected={};pearl=set();actor=None
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   r=p.i32(0)
   if r>qr:break
  elif k==1:
   actor=p.i32(0)
   if aid in b and team[actor]==0:
    vis=g.window(b[actor][0]);n=sum(c in vis for c in b[aid]);head=b[aid][0] in vis
    if n:see.append([r,actor,n,head])
    if actor==d['queens'][0] and n:qsee.append([r,n,head])
   if actor==d['queens'][0] and r==qr:
    selected=dict(bodies={i:list(v) for i,v in b.items()},pearls=list(pearl),neighbors=[(k,t,t in pearl) for k,t in g.moves[b[actor][0]]])
  elif k==3:
   xy=point(p.pointer(0));c=xy[1]*w+xy[0]
   if p.u32(0):pearl.add(c)
   else:pearl.remove(c)
  elif k==9:
   i=p.i32(0);xy=point(p.pointer(0));hd=xy[1]*w+xy[0];xy=point(p.pointer(1));tl=xy[1]*w+xy[0]
   if b[i][0]!=hd:b[i].appendleft(hd)
   while len(b[i])>1 and b[i][-1]!=tl:b[i].pop()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):b[i]=deque(point(pt)[1]*w+point(pt)[0] for pt in p.pointer(z));team[i]=p.u16(8)
  elif k==11:b.pop(p.i32(0))
 print(gid,'Queen attacker sightings',qsee,'mate last2', [x for x in see if x[0]>=qr-2]);print('neighbors',selected['neighbors'])
 turns=[t for t in d['turns'] if t['s']==0 and t['r']<=100]
 print('early no-eat move',sum(t['eat']==0 and t['action'][0]==0 for t in turns),'turns',len(turns),'dead',sum(x['s']==0 and x['r']<=100 for x in d['deaths']))
 out[gid]=dict(queen_sightings=qsee,last2=[x for x in see if x[0]>=qr-2],selected=selected)
(OUT/'details.json').write_text(json.dumps(out))
