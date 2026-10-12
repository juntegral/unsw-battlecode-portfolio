import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter,deque
R=Path.cwd();P=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'data/analysis/ladder/dossier/local'))
import scoreboard as sb
for gid in (1504482,1504484,1504486):
 root=sb.load_replay(R/f'data/online/smoke/one12-k1-old/M{gid}.replay').root();r=0;out=[];cpu=[];logs=[];special=[];bodies={};teams={};w,h=map(int,root.text(0).splitlines()[0].split()[1:3])
 for l in root.text(0).splitlines():
  q=l.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(sb.replay_format.point(None) for _ in ())
   bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
 def visible(a,b):
  dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]);return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
 for idx,e in enumerate(root.pointer(3)):
  k=e.u16(0);p=e.pointer(0)
  if k==0:
   r=p.i32(0)
   if gid==1504486 and r>=465:special.append(dict(r=r,leaders=sorted([(len(b),i) for i,b in bodies.items()],reverse=True)[:8]))
  elif k==1:
   actor=p.i32(0)
   if gid==1504484 and 134<=r<=136 and teams[actor]==0:special.append(dict(r=r,id=actor,head=bodies[actor][0],attacker=bodies.get(45),sees45=45 in bodies and visible(bodies[actor][0],bodies[45][0])))
   if gid==1504486 and r==479 and actor==111:special.append(dict(r=r,id=actor,bodies={i:list(b) for i,b in bodies.items()}))
  elif k==4:
   u=p.pointer(1);a=p.pointer(0);row=dict(r=r,id=p.i32(0),tle=p.bit(32),points=u.u64(0) if u else 0,exhausted=u.bit(64) if u else False,action=a.u16(0) if a else None)
   if row['tle'] or row['exhausted'] or row['id']==0 or row['points']>=80000000:cpu.append(row)
  elif k in (5,6):
   if (gid==1504486 and r>=468 and r<=471) or (gid==1504482 and r==209) or (gid==1504484 and r==136):logs.append(dict(r=r,event=idx,k=k,text=p.text(0)))
  elif k==9:
   b=bodies[p.i32(0)];hd=sb.replay_format.point(p.pointer(0));tail=sb.replay_format.point(p.pointer(1))
   if b[0]!=hd:b.appendleft(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(sb.replay_format.point(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:bodies.pop(p.i32(0))
 (P/f'{gid}-extras.json').write_text(json.dumps(dict(cpu=cpu,logs=logs,special=special),default=list,indent=2))
 print(gid,'timeouts',[x for x in cpu if x['tle'] or x['exhausted']]);print('CPU last queen',[x for x in cpu if x['id']==0][-5:]);print('logs',logs[:8])
