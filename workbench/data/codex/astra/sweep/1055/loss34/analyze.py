import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
import ladder_replay as lr
import o1_scan
from pathlib import Path
from collections import deque,Counter,defaultdict
OUT=Path(__file__).resolve().parent
PATHS=['data/online/smoke/one13-p2-old/M1512569.replay','data/online/smoke/one13-p2-old/M1512570.replay','data/online/live-one1/b1513119/M1513119.replay']
for path in PATHS:
 pth=Path(path);gid=int(pth.stem[1:]);meta=json.loads(pth.with_name(f'game-{gid}.json').read_text())
 base=lr.scan(pth,meta,'loss34',set()); ledger=o1_scan.scan('loss34',pth,meta)
 root=lr.replay.load(pth).root();W,H=map(int,root.text(0).splitlines()[0].split()[1:3]);own='AB'.index(base['ours']);bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  v=line.split()
  if v[0]=='DRAGON':
   i=len(bodies);teams[i]=int(v[1]);bodies[i]=deque((int(v[3+2*k]),int(v[4+2*k])) for k in range(int(v[2])))
  if v[0]=='EDGE':raw.append(tuple(map(int,v[1:4])))
 edges=lr.canonical_edges(W,H,raw);ports=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:ports[p].append(e)
 def dest(c,d):
  e=lr.edge_id(W,H,*c,d);kind,pid=edges.get(e,(0,-1))
  if kind==1:return None
  if kind==2:
   other=next(t for t in ports[pid] if t!=e);row,x=divmod(other,W+1);return ((x-(d==3))%W,(row//2-(d==0))%H)
  dx,dy=lr.base.STEP[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 reverse=defaultdict(list)
 for y in range(H):
  for x in range(W):
   for d in range(4):
    t=dest((x,y),d)
    if t is not None:reverse[t].append((x,y))
 distances={}
 def dist(target):
  if target not in distances:
   ds={target:0};q=deque([target])
   while q:
    c=q.popleft()
    for t in reverse[c]:
     if t not in ds:ds[t]=ds[c]+1;q.append(t)
   distances[target]=ds
  return distances[target]
 qid=base['queens']['us'];eq=base['queens']['them'];pearls=set();rnd=-1;actor=None;turn=None;turns=[];qturns=[];near=[];mind=None;deathscene=[]
 def finish():
  if turn is not None:
   turn['end']=list(bodies[actor][0]) if actor in bodies else None;turn['endlen']=len(bodies.get(actor,[]));turns.append(turn)
 def capture():return {str(i):{'team':teams[i],'body':list(b)} for i,b in bodies.items()}
 def proximity(idx):
  global mind
  if qid in bodies or eq not in bodies:return
  ds=dist(bodies[eq][0]);hits=[(ds.get(b[0],9999),i,b[0]) for i,b in bodies.items() if teams[i]==own]
  if not hits:return
  d,i,h=min(hits);item={'r':rnd,'event':idx,'id':i,'head':h,'enemyq':bodies[eq][0],'distance':d}
  if mind is None or d<mind['distance']:mind=item
  if d<=5 and (not near or near[-1]['r']!=rnd):near.append(item)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:finish();turn=None;rnd=p.i32(0);actor=None
  elif k==1:
   finish();actor=p.i32(0);turn={'r':rnd,'event':idx,'id':actor,'side':teams[actor],'head':list(bodies[actor][0]),'length':len(bodies[actor]),'eats':0,'steps':[],'logs':[],'actions':[]}
   if actor==qid:
    turn['bodies']=capture();turn['pearls']=list(pearls);qturns.append(turn)
  elif k==3:
   c=lr.replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eats']+=1
  elif k==4:
   a=p.pointer(0);turn['actions'].append({'kind':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [],'raw':a.i32(4)})
  elif k==6:
   if turn is not None:turn['logs'].append(p.text(0))
  elif k==9:
   i=p.i32(0);hd=lr.replay.point(p.pointer(0));tl=lr.replay.point(p.pointer(1));b=bodies[i]
   if hd!=b[0]:
    if i==actor:turn['steps'].append([list(b[0]),list(hd)])
    b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
   turn['split']=[p.i32(0),p.i32(4)]
  elif k==11:
   i=p.i32(0)
   if i in (qid,eq):deathscene.append({'r':rnd,'id':i,'actor':actor,'bodies':capture(),'turn':dict(turn)})
   bodies.pop(i)
  if k in (1,9,10,11):proximity(idx)
 finish()
 result={'base':{k:v for k,v in base.items() if k not in ('intervals','text')},'ledger':ledger,'near':near,'mindistance':mind,'queen_turns':qturns,'queen_deathscene':deathscene,'turns':turns,'edges':raw,'size':[W,H],'final_bodies':capture()}
 (OUT/f'{gid}.json').write_text(json.dumps(result,ensure_ascii=False))
 print(gid,'bots',base['bots'],'queens',base['queens'],'final',base['final'],'last_round',base['last_round'],'reason',base['end_reason'])
 print('queen deaths',[(d['id'],d['round'],d['cause'],d['actor'],d['length'],d['destination'],d['hit']) for d in base['deaths'] if d['id'] in (qid,eq)])
 print('near',near[:3],len(near),'min',mind)
 print('last qturns', [{k:v for k,v in t.items() if k not in ('bodies','pearls')} for t in qturns[-3:]])
 print('checkpoints',[(r,base['snapshots'].get(r)) for r in [0,25,50,100,150,200,300,400,499]])
