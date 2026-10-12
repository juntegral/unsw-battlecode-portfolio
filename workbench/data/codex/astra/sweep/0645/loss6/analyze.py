import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
from ladder_replay import replay,canonical_edges,edge_id
from collections import deque,Counter
from pathlib import Path
OUT=Path(__file__).parent

def scan(gid):
 root=replay.load(Path('data/online/live-one1/b1498842')/f'M{gid}.replay').root()
 lines=root.text(0).splitlines();w,h=map(int,lines[0].split()[1:3]);bodies={};teams={};raw=[]
 for line in lines:
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 queen=min(i for i in bodies if teams[i]==1);edges=canonical_edges(w,h,raw);pearls=set();turns=[];snaps={};rnd=-1;turn=None;queen_pre={};death_states=[]
 def state():return {i:list(b) for i,b in bodies.items()}
 def stats():
  return [{'n':sum(teams[i]==s for i in bodies),'total':sum(len(b) for i,b in bodies.items() if teams[i]==s),'long':max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),'q':len(bodies.get(min(i for i in teams if teams[i]==s),[]))} for s in (0,1)]
 def close():
  if turn is not None:
   turn['end']=list(bodies.get(turn['id'],[]));turns.append(turn)
 def board(i):
  head=bodies[i][0];rows=[]
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    c=((head[0]+dx)%w,(head[1]+dy)%h);ch='o' if c in pearls else '.'
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
   if rnd>=0:snaps[rnd]=stats()
   rnd=p.i32(0)
  elif k==1:
   close();i=p.i32(0);turn={'r':rnd,'event':idx,'id':i,'side':teams[i],'body':list(bodies[i]),'eat':[],'moves':[],'split':None,'deaths':[]}
   if i==queen:
    queen_pre[rnd]={'bodies':state(),'board':board(i),'pearls':list(pearls)}
  elif k==3:
   c=replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eat'].append(c)
  elif k==4:
   a=p.pointer(0);turn['action']=a.u16(0) if a else None
   turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
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
   i=p.i32(0);turn['deaths'].append([i,p.u16(4),len(bodies[i])]);
   if i==queen:death_states.append({'r':rnd,'actor':turn['id'],'bodies':state(),'pearls':list(pearls)})
   del bodies[i]
 close();snaps[rnd]=stats()
 out={'gid':gid,'queen':queen,'size':[w,h],'teams':teams,'snaps':snaps,'turns':turns,'queen_pre':queen_pre,'queen_death':death_states,'final_bodies':state()}
 (OUT/f'{gid}-trace.json').write_text(json.dumps(out,separators=(',',':')))
 # Leading score at end-of-round, ignoring elimination override until end.
 def score(s):return (s['q'],s['long'],s['total'])
 last_not_losing=max((r for r,s in snaps.items() if score(s[1])>=score(s[0])),default=-1)
 print(gid,'last_not_losing',last_not_losing,'snap',snaps.get(last_not_losing),'next',snaps.get(last_not_losing+1),'final',state())
 for d in death_states:
  r=d['r'];a=d['actor'];print('DEATH',d)
  for t in turns:
   if t['id'] in (queen,a) and r-3<=t['r']<=r:print(t)
 for side in (1,0):
  for lo,hi in [(0,74),(75,149),(150,299),(300,499)]:
   ts=[t for t in turns if t['side']==side and lo<=t['r']<=hi]
   print('window',side,lo,hi, 'turns',len(ts),'eats',sum(len(t['eat']) for t in ts),'splits',sum(t['split'] is not None for t in ts),'noeat',sum(not t['eat'] for t in ts))
 if gid==1498845:
  qs=[t for t in turns if t['id']==queen]
  print('queen eats',[t for t in qs if t['eat']]);print('queen distinct head',Counter(tuple(t['body'][0]) for t in qs))
  print('school final ordinary', [t for t in turns if t['id']==152 and t['r']>=290])
for gid in (1498844,1498845,1498846):scan(gid)
