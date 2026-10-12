import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,'data/analysis/ladder/dossier/work')
from o1_scan import scan
sys.path.insert(0,'tools')
from ladder_replay import replay,edge_id,canonical_edges
OUT=Path('data/codex/astra/sweep/0559/loss4')
p=Path('data/online/smoke/one8-p1-old/M1494965.replay')
j=json.loads(p.with_name('game-1494965.json').read_text())
r=scan('one8-p1-old',p,j)
(OUT/'ledger.json').write_text(json.dumps(r))
print(json.dumps({k:v for k,v in r.items() if k in ('bot','how','ends','last','snaps')}))
root=replay.load(p).root(); W,H=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={};teams={};raw=[]
for line in root.text(0).splitlines():
 q=line.split()
 if q[0]=='DRAGON':
  i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
 elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
edges=canonical_edges(W,H,raw)
print('size',W,H,'teams',root.text(1),root.text(2))
qs=[min(i for i in teams if teams[i]==s) for s in (0,1)]
turns=[];deaths=[];pearls=set();rnd=-1;actor=None;turn=None;snaps={}
def snapshot():return [{'n':sum(teams[i]==s for i in bodies),'L':sum(len(b) for i,b in bodies.items() if teams[i]==s),'max':max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),'q':len(bodies.get(qs[s],[]))} for s in (0,1)]
for idx,ev in enumerate(root.pointer(3)):
 k=ev.u16(0);p0=ev.pointer(0)
 if k==0:
  if rnd>=0:snaps[rnd]=snapshot()
  rnd=p0.i32(0);actor=None
 elif k==1:
  actor=p0.i32(0);turn={'r':rnd,'i':actor,'event':idx,'b':{i:list(b) for i,b in bodies.items()},'pearls':list(pearls),'events':[]};turns.append(turn)
 elif k==3:
  xy=replay.point(p0.pointer(0))
  if p0.u32(0):pearls.add(xy)
  else:pearls.discard(xy)
  if actor is not None:turn['events'].append(['pearl',xy,p0.u32(0)])
 elif k==4:
  a=p0.pointer(0);turn['action']=[a.u16(0),list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else None]
 elif k==9:
  i=p0.i32(0);hd,tl=replay.point(p0.pointer(0)),replay.point(p0.pointer(1));b=bodies[i]
  if b[0]!=hd:b.appendleft(hd)
  while len(b)>1 and b[-1]!=tl:b.pop()
  assert b[-1]==tl
  if turn is not None:turn['events'].append(['move',i,hd,tl,len(b)])
 elif k==10:
  for z,i in enumerate((p0.i32(0),p0.i32(4))):bodies[i]=deque(replay.point(c) for c in p0.pointer(z));teams[i]=p0.u16(8)
  turn['events'].append(['split',p0.i32(0),p0.i32(4)])
 elif k==11:
  i=p0.i32(0);d={'r':rnd,'event':idx,'i':i,'actor':actor,'reason':p0.u16(4),'body':list(bodies[i])};deaths.append(d);turn['events'].append(['death',i,p0.u16(4)]);bodies.pop(i)
snaps[rnd]=snapshot()
qdeath=[d for d in deaths if d['i'] in qs];print('queen deaths',qdeath)
lastq=[t for t in turns if t['i']==qs[0]][-3:]
for t in lastq:
 print('QTURN',json.dumps({k:v for k,v in t.items() if k not in ('b','pearls')}))
for d in qdeath:
 for t in turns:
  if t['r']==d['r'] and t['i']==d['actor']:print('KILLER',json.dumps(t))
(OUT/'turns.json').write_text(json.dumps({'W':W,'H':H,'edges':raw,'teams':teams,'queens':qs,'deaths':deaths,'turns':turns,'snaps':snaps,'final':{i:list(b) for i,b in bodies.items()}}))
