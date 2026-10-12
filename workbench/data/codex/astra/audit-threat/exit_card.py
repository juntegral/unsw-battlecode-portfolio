import sys
sys.dont_write_bytecode=True
import audit as a
import json
from collections import deque
O=a.OUT

def scan(j,death):
 root=a.sb.load_replay(a.ROOT/j['path']).root();g=a.geo_mod.Geo(root.text(0));bs={};ts={};rnd=0;current=None;out=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bs);bs[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));ts[i]=int(q[1])
 own=0 if j['meta']['teamAId']==1119 else 1;queen=min(i for i in bs if ts[i]==own)
 def exits(skip=None):
  if queen not in bs:return []
  occ={c for i,b in bs.items() if i!=skip for c in b}
  return [n for n in g.moves[bs[queen][0]] if n is not None and n not in occ]
 def finish():
  nonlocal current
  if current is not None and current['before'] and not exits() and queen in bs:
   current['after']=exits();current['if_remove_mate']=exits(current['id']);current['body_end']=list(bs.get(current['id'],()))
   out.append(current)
  current=None
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k in (0,1):finish()
  if k==0:rnd=p.i32(0)
  elif k==1:
   i=p.i32(0)
   if ts[i]==own and i!=queen and queen in bs and death['r']-2<=rnd<=death['r']:
    h=bs[i][0];qh=bs[queen][0];visible=g.visible(qh,h)
    legal=[d for d,n in enumerate(g.moves[h]) if n is not None and not any(n in b for b in bs.values())]
    walls=[d for d,n in enumerate(g.moves[h]) if n is None]
    current=dict(gid=j['gid'],v=j['version'],r=rnd,id=i,queen=queen,queen_head=qh,body=list(bs[i]),before=exits(),queen_visible=visible,walls=walls,legal_one_steps=legal,can_split=len(bs[i])>=4,action=None,dirs=[])
  elif k==4 and current:
   act=p.pointer(0);current['action']=act.u16(0) if act else None;current['dirs']=list(act.pointer(0)) if act and act.u16(0)==0 and act.pointer(0) else []
  elif k==9:
   i=p.i32(0);h=a.lr.replay.point(p.pointer(0));t=a.lr.replay.point(p.pointer(1));b=bs[i]
   if h!=b[0]:b.appendleft(h)
   while len(b)>1 and b[-1]!=t:b.pop()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bs[i]=deque(a.lr.replay.point(c) for c in p.pointer(z));ts[i]=p.u16(8)
  elif k==11:bs.pop(p.i32(0))
 finish();return out
inv=json.loads((O/'inventory.json').read_text());out=[]
for j in inv['games']:
 if j['version'] not in (9,10):continue
 gm=json.loads((O/f'g{j["gid"]}.json').read_text());dd=next((d for d in gm['deaths'] if d['q']),None)
 if dd and dd['reason'] in (0,1,2):out.extend(scan(j,dd))
(O/'exit-card-witnesses.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
for x in out:print(x,flush=True)
