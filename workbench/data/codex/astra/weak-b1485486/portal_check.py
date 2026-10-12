import sys,json
sys.dont_write_bytecode=True
from collections import deque
import evidence as e
O=e.O;g=json.loads((O/'M1485489.json').read_text());d=g['detail'];root,edge,step=e.geo(g);w,H=d['w'],d['h'];known=set();checks=[]
for t in d['qt'][0]:
 x,y=t['body'][0]
 for dx in range(-3,4):
  for dy in range(-3,4):known.add(((x+dx)%w,(y+dy)%H))
 if t['r']>111:break
 if t['r']%2:continue
 q=deque([tuple(t['body'][0])]);seen=set(q);res=None
 while q and res is None:
  c=q.popleft()
  for k in range(4):
   dx,dy=((0,-1),(1,0),(0,1),(-1,0))[k];adj=((c[0]+dx)%w,(c[1]+dy)%H)
   if c not in known and adj not in known:res=-1;break
   if edge(c,k)[0]!=0:continue
   if adj in seen:continue
   if len(seen)>=w*H//2:res=-1;break
   seen.add(adj);q.append(adj)
 if res is None:res=len(seen)
 checks.append((t['r'],res))
print('home_region results',checks)
(O/'portal-check.json').write_text(json.dumps(checks))
