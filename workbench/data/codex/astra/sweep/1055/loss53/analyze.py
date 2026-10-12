import sys,json
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools')); import ladder_replay as lr
sys.path.insert(0,str(ROOT/'data/analysis/ladder/losses/counts')); from count_replays import Geometry
GAMES=[(1516203,1516202),(1516206,1516202),(1516986,1516986)]
for gid,bid in GAMES:
 p=ROOT/f'data/online/live-one1/b{bid}/M{gid}.replay'; meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 base=lr.scan(p,meta,str(bid),set()); OUT.joinpath(f'{gid}-base.json').write_text(json.dumps({k:v for k,v in base.items() if k != 'intervals'},ensure_ascii=False,separators=(',',':'))); print('BASE',gid,base['queens'],base['final'],[d for d in base['deaths'] if d['id'] in (0,1)],flush=True); root=lr.replay.load(p).root()
 W,H=map(int,base['text'].splitlines()[0].split()[1:3]); bodies={}; teams={}; edges=[]
 for l in base['text'].splitlines():
  q=l.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]='AB'[int(q[1])]
  if q[0]=='EDGE': edges.append(tuple(map(int,q[1:4])))
 geo=Geometry(W,H,edges); turns=[]; pearls=set(); rnd=0; actor=None; cur=None; close=[]
 OURQ=base['queens']['us']; ENQ=base['queens']['them']
 qdead=False; nearrounds=set(); mind=99999; closest=None
 def board(center):
  x,y=center; rows=[]
  occ={c:('Q' if i==OURQ else 'K' if i==ENQ else 'A' if teams[i]=='B' else 'E') if k==0 else ('q' if i==OURQ else 'k' if i==ENQ else 'a' if teams[i]=='B' else 'e') for i,b in bodies.items() for k,c in enumerate(b)}
  for dy in range(-3,4):
   row='';wall=''
   for dx in range(-3,4):
    xx,yy=(x+dx)%W,(y+dy)%H;c=(xx,yy); z=yy*W+xx
    row+=occ.get(c,'*' if c in pearls else '.')
    wall+='|' if geo.moves[z][1][0]==1 else ':' if geo.moves[z][1][0]==2 else ' '
   rows.append(''.join(a+b for a,b in zip(row,wall))[:-1])
   if dy<3: rows.append(' '.join('-' if geo.moves[((y+dy)%H)*W+(x+dx)%W][2][0]==1 else ':' if geo.moves[((y+dy)%H)*W+(x+dx)%W][2][0]==2 else ' ' for dx in range(-3,4)))
  return '\n'.join(rows)
 def near(idx):
  global mind,closest
  if not qdead or ENQ not in bodies:return
  dst=geo.distances(bodies[ENQ][0][1]*W+bodies[ENQ][0][0]);opts=[(dst[b[0][1]*W+b[0][0]],i,b[0]) for i,b in bodies.items() if teams[i]=='B']
  if not opts:return
  d,i,h=min(opts)
  if d<mind:mind=d;closest=dict(round=rnd,event=idx,id=i,head=h,queen=bodies[ENQ][0],distance=d)
  if d<=5:nearrounds.add(rnd)
 for idx,e in enumerate(root.pointer(3)):
  k=lr.replay.EVENT_NAMES[e.u16(0)];p=e.pointer(0)
  if k in ('turnStart','roundStart'):
   if cur:cur['end']={str(i):list(b) for i,b in bodies.items()} if actor==OURQ else {};turns.append(cur);cur=None
   if k=='roundStart':rnd=p.i32(0);actor=None
   else:
    actor=p.i32(0);cur=dict(round=rnd,event=idx,id=actor,body=list(bodies[actor]),heads={str(i):[len(b),b[0]] for i,b in bodies.items()} if actor==OURQ else {},board=board(bodies[actor][0]) if actor==OURQ else None,eats=0,updates=[],splits=[],deaths=[])
  elif k=='dragonAction':
   a=p.pointer(0);cur['action']=a.u16(0) if a else None;cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k=='tileChange':
   c=lr.replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);cur['eats']+=1
  elif k=='dragonUpdate':
   i=p.i32(0);h=lr.replay.point(p.pointer(0));t=lr.replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=h:b.appendleft(h)
   while len(b)>1 and b[-1]!=t:b.pop()
   assert b[-1]==t
   if cur:cur['updates'].append([i,list(b)])
  elif k=='dragonSplit':
   cur['splits'].append([p.i32(0),p.i32(4)])
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]='AB'[p.u16(8)]
  elif k=='dragonDeath':
   i=p.i32(0);cur['deaths'].append(i);bodies.pop(i)
   if i==OURQ:qdead=True
  if k in ('dragonUpdate','dragonSplit','dragonDeath','roundStart'):near(idx)
 if cur:cur['end']={str(i):list(b) for i,b in bodies.items()} if actor==OURQ else {};turns.append(cur)
 # Store modest complete evidence, full bodies only for last queen turns and nearby turns.
 qdeath=next((d for d in base['deaths'] if d['id']==OURQ),None)
 qt=[t for t in turns if t['id']==OURQ]; interesting=[t for t in turns if qdeath and abs(t['round']-qdeath['round'])<=2]
 summary={k:base[k] for k in ('gid','map','bots','final','end_reason','winner','last_round','queens','q_eats','q_splits','eats','anomalies')}
 summary.update(queen_deaths=[d for d in base['deaths'] if d['id'] in (0,1)],last_queen_turns=qt[-3:],near_after=dict(minimum=mind,closest=closest,rounds=len(nearrounds),first=min(nearrounds) if nearrounds else None),checkpoints={r:base['snapshots'].get(r) for r in (0,10,20,50,100,150,200,250,300,350,400,450,499,500)})
 OUT.joinpath(f'{gid}.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
 OUT.joinpath(f'{gid}-turns.json').write_text(json.dumps(turns,separators=(',',':')))
 OUT.joinpath(f'{gid}-base.json').write_text(json.dumps({k:v for k,v in base.items() if k not in ('intervals',)},ensure_ascii=False,separators=(',',':')))
 print(json.dumps({k:v for k,v in summary.items() if k not in ('last_queen_turns','checkpoints')},ensure_ascii=False))
 print('QUEEN LAST',[(t['round'],len(t['body']),t['body'][0],t.get('dirs'),t['splits'],t['deaths']) for t in qt[-3:]])
