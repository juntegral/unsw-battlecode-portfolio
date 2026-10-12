import sys
sys.dont_write_bytecode=True
import analyze as a
import json
from collections import deque
O=a.O;out=[]
for gid,r in [(1483344,65),(1485489,111),(1486054,109),(1493693,90),(1483011,181),(1485172,81)]:
 x=json.loads((O/f'g{gid}.json').read_text());root=a.lr.replay.load(a.R/x['path']).root();g=a.gm.Geo(root.text(0));bs={};teams={};seen=set();rnd=0
 for q in map(str.split,root.text(0).splitlines()):
  if q and q[0]=='DRAGON':i=len(bs);bs[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:rnd=p.i32(0)
  elif k==1 and p.i32(0)==x['queen']:
   h=bs[x['queen']][0];seen|={c for c in g.moves if g.visible(c,h)}
   if rnd==r:
    t=next(t for t in x['turns'] if t['r']==r);dest=g.moves[h][t['dirs'][0]];out.append(dict(gid=gid,r=r,L=len(bs[x['queen']]),head=h,dest=dest,seen=dest in seen,units=sum(teams[i]==x['own'] for i in bs)));break
  elif k==9:
   i=p.i32(0);h=a.lr.replay.point(p.pointer(0));tail=a.lr.replay.point(p.pointer(1));b=bs[i]
   if h!=b[0]:b.appendleft(h)
   while len(b)>1 and b[-1]!=tail:b.pop()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bs[i]=deque(a.lr.replay.point(v) for v in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:bs.pop(p.i32(0))
(O/'portal-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
