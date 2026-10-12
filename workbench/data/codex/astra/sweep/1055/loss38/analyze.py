import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
from ladder_replay import scan,replay,canonical_edges,edge_id
from collections import deque,Counter
from pathlib import Path
OUT=Path(__file__).parent
jobs=[(1515669,'data/online/smoke/one13-q1-old'),(1515670,'data/online/smoke/one13-q1-old'),(1506911,'data/online/live-one1/b1506911')]
for gid,folder in jobs:
 p=Path(folder);meta=json.loads((p/f'game-{gid}.json').read_text());path=p/f'M{gid}.replay'
 result=scan(path,meta,folder,set());(OUT/f'{gid}-scan.json').write_text(json.dumps({k:v for k,v in result.items() if k!='intervals'}))
 root=replay.load(path).root();lines=root.text(0).splitlines();w,h=map(int,lines[0].split()[1:3]);bodies={};teams={};raw=[]
 for line in lines:
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 edges=canonical_edges(w,h,raw);pearls=set();turns=[];rnd=-1;turn=None;queen_pre=[];qids=list(result['queens'].values());ours=0 if result['ours']=='A' else 1;distances=[];snaps={}
 def state():return {i:list(b) for i,b in bodies.items()}
 def close():
  if turn is not None:turn['end']=list(bodies.get(turn['id'],[]));turns.append(turn)
 def board(i):
  hx,hy=bodies[i][0];rows=[]
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    c=((hx+dx)%w,(hy+dy)%h);ch='o' if c in pearls else '.'
    for z,b in bodies.items():
     if c in b:ch=('Q' if z==i else 'M' if teams[z]==teams[i] else 'E') if c==b[0] else ('b' if z==i else 'm' if teams[z]==teams[i] else 'e')
    ed=''.join('NESW'[d] if edges.get(edge_id(w,h,*c,d),(0,0))[0]==1 else 'nesw'[d] if edges.get(edge_id(w,h,*c,d),(0,0))[0]==2 else '' for d in range(4))
    row.append(ch+ed)
   rows.append(row)
  return rows
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close();turn=None
   if rnd>=0:snaps[rnd]=state()
   rnd=p.i32(0)
  elif k==1:
   close();i=p.i32(0);turn={'r':rnd,'event':idx,'id':i,'side':teams[i],'body':list(bodies[i]),'eat':[],'moves':[],'split':None,'deaths':[]}
   if i in qids:queen_pre.append({'r':rnd,'id':i,'bodies':state(),'board':board(i),'pearls':list(pearls)})
   if qids[0] not in bodies and qids[1] in bodies and teams[i]==ours:
    a=bodies[i][0];b=bodies[qids[1]][0];d=min(abs(a[0]-b[0]),w-abs(a[0]-b[0]))+min(abs(a[1]-b[1]),h-abs(a[1]-b[1]));distances.append([rnd,i,d,a,b])
  elif k==3:
   c=replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eat'].append(c)
  elif k==4:
   a=p.pointer(0);turn['action']=a.u16(0) if a else None;turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==9:
   i=p.i32(0);head=replay.point(p.pointer(0));tail=replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=head:
    b.appendleft(head)
    if i==turn['id']:turn['moves'].append(head)
   while len(b)>1 and b[-1]!=tail:b.pop()
  elif k==10:
   a,c=p.i32(0),p.i32(4);turn['split']=[a,c]
   for z,i in enumerate((a,c)):bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);turn['deaths'].append([i,p.u16(4),len(bodies[i])]);del bodies[i]
 close();snaps[rnd]=state()
 out={'gid':gid,'queens':qids,'size':[w,h],'teams':teams,'turns':turns,'queen_pre':queen_pre,'distances':distances,'snaps':snaps}
 (OUT/f'{gid}-trace.json').write_text(json.dumps(out,separators=(',',':')))
 def score(s):return (s['queen_length'],s['longest'],s['total'])
 last=max((r for r,s in result['snapshots'].items() if score(s['us'])>=score(s['them'])),default=-1)
 print(gid,'bots',result['bots'],'winner',result['winner'],'end',result['end_reason'],'final',result['final'],'last_not_losing',last,'eats',result['eats'])
 for d in result['deaths']:
  if d['id'] in qids:
   print('QDEATH',d)
   for t in turns:
    if t['id'] in (d['id'],d['actor']) and d['round']-3<=t['r']<=d['round']:print('TURN',t)
 print('CLOSE', sorted(distances,key=lambda a:a[2])[:5])
 for r in (0,25,50,100,150,200,250,300,350,400,450,499):
  if r in result['snapshots']:print(r,result['snapshots'][r])
