import sys
sys.dont_write_bytecode=True
import audit as a
import json,gzip
from collections import deque
from pathlib import Path
O=a.OUT

def witness(job,targets):
 root=a.sb.load_replay(a.ROOT/job['path']).root();g=a.geo_mod.Geo(root.text(0));bodies={};teams={};present=set();rnd=0;out=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
 own=0 if job['meta']['teamAId']==1119 else 1;qid=min(i for i in bodies if teams[i]==own)
 def inspect():
  b=list(bodies[qid]);win={((b[0][0]+dx)%g.w,(b[0][1]+dy)%g.h) for dx in range(-3,4) for dy in range(-3,4)}
  occ={c:i for i,bb in bodies.items() for c in bb};ops=[]
  for d,n in enumerate(g.moves[b[0]]):
   if n is None:ops.append(dict(d=d,wall=True));continue
   o=dict(d=d,dest=n,occupant=occ.get(n),pearl=n in present,portal=g.edges.get(a.lr.edge_id(g.w,g.h,*b[0],d),(0,-1))[0]==2)
   if n not in occ:
    nb=[n]+b if n in present else [n]+b[:-1]
    blocked={c for i,bb in bodies.items() if i!=qid for c in bb}|set(nb[1:]);room={n};queue=deque([n])
    while queue:
     c=queue.popleft()
     for p in g.adj[c]:
      if p not in room and p not in blocked and p in win:room.add(p);queue.append(p)
    o.update(next_open=[nn for nn in g.adj[n] if nn not in blocked],visible_room=len(room),room=sorted(room))
   ops.append(o)
  return dict(r=rnd,body=b,options=ops,near=[dict(id=i,team=teams[i],body=list(bb)) for i,bb in bodies.items() if any(c in win for c in bb)],pearls=sorted(present&win))
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:rnd=p.i32(0)
  elif k==1 and p.i32(0)==qid and rnd in targets:out.append(inspect())
  elif k==3:
   c=a.lr.replay.point(p.pointer(0))
   if p.u32(0):present.add(c)
   else:present.remove(c)
  elif k==9:
   i=p.i32(0);h=a.lr.replay.point(p.pointer(0));t=a.lr.replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=h:b.appendleft(h)
   while len(b)>1 and b[-1]!=t:b.pop()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(a.lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:bodies.pop(p.i32(0))
 return out

def main():
 inv=json.loads((O/'inventory.json').read_text());out=[]
 for j in inv['games']:
  if j['version'] not in (9,10) or not (O/f'g{j["gid"]}.json').exists():continue
  gm=json.loads((O/f'g{j["gid"]}.json').read_text());dd=next((d for d in gm['deaths'] if d['q']),None)
  if not dd:continue
  rounds=set(range(max(0,dd['r']-6),dd['r']+1));ws=witness(j,rounds);out.append(dict(gid=j['gid'],v=j['version'],map=gm['map'],death=dd,witnesses=ws))
 (O/'queen-witnesses.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 for x in out:
  print(x['gid'],x['map'],x['death']['r'],x['death'].get('reach_class'))
  for w in x['witnesses'][-3:]:print(w['r'],w['body'],[{k:v for k,v in p.items() if k!='room'} for p in w['options']])
if __name__=='__main__':main()
