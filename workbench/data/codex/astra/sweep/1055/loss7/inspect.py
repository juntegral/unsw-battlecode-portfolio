import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque
sys.path.insert(0,str(Path(__file__).parent));from analyze import lr,Geo,OUT,ROOT
sys.path.insert(0,str(ROOT/'data/analysis/ladder/dossier/local'));from scoreboard import load_replay
for gid in (1503506,1503508,1503509):
 data=json.loads((OUT/f'{gid}.json').read_text());uq=data['base']['queens']['us'];eq=data['base']['queens']['them']
 root=load_replay(ROOT/f'data/online/smoke/one12-p1-old/M{gid}.replay').root();bodies={};teams={};edges=[];cache={};logs=[];contacts=[];locations=set();nearest=None;states={};r=-1
 for line in root.text(0).splitlines():
  q=line.split()
  if not q:continue
  if q[0]=='MAP':w,h=map(int,q[1:3])
  elif q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':edges.append(tuple(map(int,q[1:4])))
 geo=Geo(w,h,edges);rev=[[] for _ in geo.adj]
 for c,adj in enumerate(geo.adj):
  for d in adj:rev[d].append(c)
 def dists(target):
  if target not in cache:
   ds={target:0};queue=deque([target])
   while queue:
    c=queue.popleft()
    for d in rev[c]:
     if d not in ds:ds[d]=ds[c]+1;queue.append(d)
   cache[target]=ds
  return cache[target]
 tile=lambda p:p[1]*w+p[0]
 xy=lambda c:[c%w,c//w]
 for idx,ev in enumerate(root.pointer(3)):
  k=lr.replay.EVENT_NAMES[ev.u16(0)];p=ev.pointer(0)
  if k=='roundStart':r=p.i32(0)
  elif k=='turnStart':
   actor=p.i32(0)
   if actor==uq and ((gid==1503506 and r>=115) or (gid==1503508 and r>=340) or (gid==1503509 and r>=61)):
    states[r]={i:list(b) for i,b in bodies.items()}
  elif k=='dragonLog':
   if p.i32(0)==uq:logs.append([r,p.text(0)])
  elif k=='dragonUpdate':
   i=p.i32(0);hd=tile(lr.replay.point(p.pointer(0)));tl=tile(lr.replay.point(p.pointer(1)));b=bodies[i]
   if hd!=b[0]:b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
  elif k=='dragonSplit':
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(tile(lr.replay.point(c)) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k=='dragonDeath':bodies.pop(p.i32(0))
  if k in ('dragonUpdate','dragonSplit','dragonDeath') and uq not in bodies and eq in bodies:
   target=bodies[eq][0];locations.add(tuple(xy(target)));ds=dists(target)
   for i,b in bodies.items():
    if teams[i]!=0:continue
    dist=ds.get(b[0],999999)
    row=dict(r=r,event=idx,id=i,d=dist,head=xy(b[0]),queen=xy(target))
    if dist<=5:
     occ={c for bb in bodies.values() for c in bb};dd={b[0]:0};qq=deque([b[0]])
     while qq:
      cc=qq.popleft()
      if dd[cc]>=5:continue
      for nn in geo.adj[cc]:
       if nn not in dd and (nn not in occ or nn==target):dd[nn]=dd[cc]+1;qq.append(nn)
     row['body_clear_distance']=dd.get(target)
     dd={b[0]:0};qq=deque([b[0]])
     while qq:
      cc=qq.popleft()
      if dd[cc]>=5:continue
      for kind,nn in geo.moves[cc]:
       if kind==0 and nn not in dd and (nn not in occ or nn==target):dd[nn]=dd[cc]+1;qq.append(nn)
     row['ordinary_clear_distance']=dd.get(target)


    if nearest is None or dist<nearest['d']:nearest=row
    if dist<=5 and (not contacts or (r,i,dist,xy(b[0]),xy(target))!=(contacts[-1]['r'],contacts[-1]['id'],contacts[-1]['d'],contacts[-1]['head'],contacts[-1]['queen'])):contacts.append(row)
 # Exact 7x7-cell diagrams with kelp between cells.
 boards=[]
 for t in [t for t in data['turns'] if t['id']==uq][-3:]:
  src=t['head'][1]*w+t['head'][0];cs=[((src//w+dy)%h)*w+(src%w+dx)%w for dy in range(-3,4) for dx in range(-3,4)]
  arr=[list(' '*15) for _ in range(15)]
  for iy in range(7):
   for ix in range(7):
    c=cs[iy*7+ix];arr[2*iy+1][2*ix+1]=t['board'][iy][ix]
    for d,(kind,_) in enumerate(geo.moves[c]):
     if kind:
      ddy,ddx=[(-1,0),(0,1),(1,0),(0,-1)][d];arr[2*iy+1+ddy][2*ix+1+ddx]='-' if kind==1 and d%2==0 else '|' if kind==1 else 'O'
  boards.append(dict(r=t['r'],head=t['head'],board=[''.join(x) for x in arr]))
 out=dict(nearest=nearest,contacts=contacts,queen_locations=sorted(locations),logs=logs,states=states,boards=boards)
 (OUT/f'{gid}-inspection.json').write_text(json.dumps(out))
 print(gid,'nearest',nearest,'contacts',len(contacts),'queen_locations',sorted(locations) if not contacts else 'see json','logs',len(logs))
 for x in logs:
  if (gid==1503506 and x[0]>=74) or (gid==1503508 and (x[0] in (195,286,308) or x[0]>=340)) or (gid==1503509 and x[0]>=60):print(x)
