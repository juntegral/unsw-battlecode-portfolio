import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'));import ladder_replay as lr
sys.path.insert(0,str(ROOT/'data/analysis/ladder/dossier'));from count_dossier import Geo
GAMES=[(1504150,'data/online/live-one1/b1504147'),(1504151,'data/online/live-one1/b1504147'),(1504479,'data/online/smoke/one12-k1-old')]
for gid,folder in GAMES:
 root=lr.replay.load(ROOT/folder/f'M{gid}.replay').root(); w,h=map(int,root.text(0).splitlines()[0].split()[1:3]);bodies={};teams={};raw=[];pearls=set()
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 geo=Geo(w,h,raw);own=0 if gid==1504479 else 1;qu=min(i for i in teams if teams[i]==own);qe=min(i for i in teams if teams[i]!=own);turns=[];splits=[];rnd=-1;turn=None;close=[];qdead=False;minimum=None;roundends={}
 tile=lambda p:lr.replay.point(p)[1]*w+lr.replay.point(p)[0]
 xy=lambda c:[c%w,c//w]
 def board(c):
  occ={z:('Q' if i==qu and k==0 else 'q' if i==qu else 'K' if i==qe and k==0 else 'k' if i==qe else 'A' if teams[i]==own and k==0 else 'a' if teams[i]==own else 'E' if k==0 else 'e') for i,b in bodies.items() for k,z in enumerate(b)}
  lines=[];cx,cy=xy(c)
  for dy in range(-3,4):
   cs=[((cy+dy)%h)*w+(cx+dx)%w for dx in range(-3,4)]
   lines.append(''.join('+'+('-' if geo.moves[z][0][0]==1 else '~' if geo.moves[z][0][0]==2 else ' ') for z in cs)+'+')
   lines.append(''.join(('|' if geo.moves[z][3][0]==1 else '~' if geo.moves[z][3][0]==2 else ' ')+occ.get(z,'*' if z in pearls else '.') for z in cs)+('|' if geo.moves[cs[-1]][1][0]==1 else ' '))
  lines.append(''.join('+'+('-' if geo.moves[z][2][0]==1 else '~' if geo.moves[z][2][0]==2 else ' ') for z in cs)+'+')
  return '\n'.join(lines)
 def finish():
  if turn is not None:
   turn['end']=xy(bodies[turn['id']][0]) if turn['id'] in bodies else None
   turn['end_len']=len(bodies.get(turn['id'],()))
 def roundend():
  roundends[rnd]=[sorted([(i,len(b),xy(b[0])) for i,b in bodies.items() if teams[i]==s],key=lambda z:-z[1]) for s in [own,1-own]]
 def proximity(event):
  global minimum
  if not qdead or qe not in bodies:return
  c=bodies[qe][0];dist=geo.distances(c); options=[(dist[b[0]],i) for i,b in bodies.items() if teams[i]==own]
  if not options:return
  d,i=min(options)
  row=dict(round=rnd,event=event,id=i,d=int(d),head=xy(bodies[i][0]),queen=xy(c),queen_len=len(bodies[qe]))
  if minimum is None or d<minimum['d']:minimum=row
  if d<=5 and (not close or close[-1]['round']!=rnd):close.append(row)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   finish();roundend();rnd=p.i32(0);turn=None
  elif k==1:
   finish();i=p.i32(0);c=bodies[i][0]
   turn=dict(round=rnd,event=idx,id=i,side=teams[i],length=len(bodies[i]),head=xy(c),path=[],eats=0,units=sum(teams[j]==teams[i] for j in bodies))
   if i==qu:
    turn['board']=board(c);turn['near']=[dict(id=j,len=len(b),head=xy(b[0]),body=[xy(z) for z in b]) for j,b in bodies.items() if geo.visible(c,b[0]) or any(z in geo.window(c) for z in b)];turn['edges']=[(k,xy(z)) for k,z in geo.moves[c]]
   turns.append(turn)
  elif k==4:
   a=p.pointer(0)
   turn['action_kind']=a.u16(0) if a else None
   turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.discard(c);turn['eats']+=1
  elif k==9:
   i=p.i32(0);hd=tile(p.pointer(0));tail=tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);turn['path'].append(xy(hd))
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   a,ch=p.i32(0),p.i32(4);splits.append(dict(round=rnd,id=a,child=ch,before=len(bodies[a]),units=turn['units']))
   for z,i in enumerate((a,ch)):bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0)
   if i==qu:qdead=True
   bodies.pop(i)
  if k in (0,1,9,10,11):proximity(idx)
 finish();roundend()
 out=dict(gid=gid,w=w,h=h,turns=turns,splits=splits,close=close,minimum=minimum,roundends=roundends)
 (OUT/f'{gid}-detail.json').write_text(json.dumps(out))
 qt=[t for t in turns if t['id']==qu]
 print(gid,'lastqueen',[(t['round'],t['length'],t.get('dirs'),t['head'],t['end'],t['eats']) for t in qt[-3:]],'qsplit',[s for s in splits if s['id']==qu],'closest',minimum,'close rounds',len(close),flush=True)
 for t in qt[-3:]:print('r',t['round'],t['board'],sep='\n',flush=True)
