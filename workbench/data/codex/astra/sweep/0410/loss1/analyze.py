import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
import ladder_replay as lr
import ast,types
geo_source=Path('data/analysis/ladder/dossier/work/tq2_chase.py')
geo_ast=ast.parse(geo_source.read_text())
geo_ast.body=[n for n in geo_ast.body if not isinstance(n,ast.Expr)]
geo_module=types.ModuleType('tq2_chase_readonly')
exec(compile(geo_ast,str(geo_source),'exec'),geo_module.__dict__)
Geo=geo_module.Geo
OUT=Path(__file__).resolve().parent
GAMES=[(1486051,1486052),(1486051,1486053),(1486051,1486054),(1483995,1483997),(1483995,1483998)]

def run(bid,gid):
 p=Path(f'data/online/live-one1/b{bid}/M{gid}.replay');meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 base=lr.scan(p,meta,'ranked',set());root=lr.replay.load(p).root();text=root.text(0);w,h=map(int,text.splitlines()[0].split()[1:]);bodies={};teams={};raw=[]
 for line in text.splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 geo=Geo(w,h,raw);queens=[min(i for i in bodies if teams[i]==s) for s in [0,1]];rnd=-1;actor=None;turns=[];current=None;pearls=set();snaps={};close=[];qdead=False;nearest=None;enemy_q_positions=[];full_dist={}
 def xy(c):return [c%w,c//w]
 def tile(p):x,y=lr.replay.point(p);return y*w+x
 def snapshot():
  return [dict(q=len(bodies.get(queens[s],[])),n=sum(teams[i]==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),longest=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),leaders=sorted([(i,len(b),xy(b[0])) for i,b in bodies.items() if teams[i]==s],key=lambda v:-v[1])[:4]) for s in [0,1]]
 def check_near(event):
  nonlocal nearest
  if not qdead or queens[1] not in bodies:return
  qh=bodies[queens[1]][0]
  if not enemy_q_positions or enemy_q_positions[-1][1]!=xy(qh):enemy_q_positions.append([rnd,xy(qh)])
  if qh not in full_dist:
   rev=[[] for _ in geo.nxt]
   for src,ns in enumerate(geo.nxt):
    for dest in ns:
     if dest>=0:rev[dest].append(src)
   d={qh:0};queue=deque([qh])
   while queue:
    c=queue.popleft()
    for z in rev[c]:
     if z not in d:d[z]=d[c]+1;queue.append(z)
   full_dist[qh]=d
  for i,b in bodies.items():
   if teams[i]==0:
    dist=full_dist[qh].get(b[0],999)
    rec=[rnd,event,i,len(b),dist,xy(b[0]),xy(qh)]
    if nearest is None or dist<nearest[4]:nearest=rec
    if dist<=5:close.append([rnd,event,i,len(b),dist,xy(b[0]),xy(qh)])
 def board(center):
  occ={c:('Q' if i==queens[0] and z==0 else 'K' if i==queens[1] and z==0 else 'A' if teams[i]==0 and z==0 else 'B' if z==0 else 'a' if teams[i]==0 else 'b') for i,b in bodies.items() for z,c in enumerate(b)}
  grid=[];edges=[];legend={}
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    c=((center//w+dy)%h)*w+(center%w+dx)%w;row.append(occ.get(c,'*' if c in pearls else '.'))
    for d in range(4):
     if geo.nxt[c][d]<0 or geo.por[c][d]:edges.append([dx,dy,'NESW'[d],'#' if geo.nxt[c][d]<0 else 'P'])
   grid.append(''.join(row))
  for i,b in bodies.items():
   dx=(b[0]%w-center%w+w//2)%w-w//2;dy=(b[0]//w-center//w+h//2)%h-h//2
   if abs(dx)<=3 and abs(dy)<=3:legend[i]=[dx,dy,len(b)]
  return dict(center=xy(center),grid=grid,edges=edges,heads=legend)
 for index,ev in enumerate(root.pointer(3)):
  kind=ev.u16(0);v=ev.pointer(0)
  if kind==0:
   if rnd>=0:snaps[rnd]=snapshot()
   rnd=v.i32(0);actor=None
  elif kind==1:
   actor=v.i32(0);b=bodies[actor];current=dict(round=rnd,id=actor,side=teams[actor],L=len(b),start=xy(b[0]),event=index,eats=0,steps=[],action=None)
   if actor==queens[0]:current.update(board=board(b[0]),bodies={i:list(bb) for i,bb in bodies.items()},pearls=list(pearls))
   turns.append(current);check_near(index)
  elif kind==3:
   c=tile(v.pointer(0))
   if v.u32(0):pearls.add(c)
   else:pearls.discard(c);current['eats']+=1
  elif kind==4:
   a=v.pointer(0);current['action']={'kind':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []}
  elif kind==9:
   i=v.i32(0);hd,tail=tile(v.pointer(0)),tile(v.pointer(1));b=bodies[i]
   if b[0]!=hd:
    assert geo.nxt[b[0]][current['action']['dirs'][len(current['steps'])]]==hd,(gid,rnd,actor,b[0],hd)
    b.appendleft(hd);current['steps'].append(xy(hd))
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
   if current is not None:current['endL']=len(b)
   check_near(index)
  elif kind==10:
   for z,i in enumerate([v.i32(0),v.i32(4)]):bodies[i]=deque(tile(pt) for pt in v.pointer(z));teams[i]=v.u16(8)
   current['split']=[v.i32(0),v.i32(4),len(bodies[v.i32(0)]),len(bodies[v.i32(4)])];check_near(index)
  elif kind==11:
   i=v.i32(0)
   if i==queens[0]:qdead=True
   del bodies[i];check_near(index)
 snaps[rnd]=snapshot()
 qturns=[t for t in turns if t['id']==queens[0]]
 qdeaths=[d for d in base['deaths'] if d['id'] in queens]
 decision='wiped' if snaps[rnd][0]['n']==0 else 'queen' if snaps[rnd][0]['q']!=snaps[rnd][1]['q'] else 'longest' if snaps[rnd][0]['longest']!=snaps[rnd][1]['longest'] else 'total'
 def ahead(st):return tuple(st[1][k] for k in ['q','longest','total'])>tuple(st[0][k] for k in ['q','longest','total'])
 permanent=max([r for r,st in snaps.items() if not ahead(st)],default=-1)+1
 out=dict(gid=gid,map=meta['mapName'],bot=base['bots'],queens=queens,dim=[w,h],final=snaps[rnd],end=rnd,decision=decision,permanent=permanent,qdeaths=qdeaths,nearest=nearest,enemy_q_positions=enemy_q_positions,close_count=len(close),close_first=close[:8],close_last=close[-3:],checkpoints={r:snaps[r] for r in [0,25,50,75,100,150,200,250,300,350,400,450,499] if r in snaps},queen_turns=qturns[-3:],q_eats=base['q_eats'],q_splits=base['q_splits'],eats=base['eats'])
 (OUT/f'{gid}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 (OUT/f'{gid}-turns.json').write_text(json.dumps(turns,separators=(',',':')))
 (OUT/f'{gid}-deaths.json').write_text(json.dumps(base['deaths'],separators=(',',':')))
 (OUT/f'{gid}-snapshots.json').write_text(json.dumps(snaps,separators=(',',':')))
 print(json.dumps({k:v for k,v in out.items() if k not in ['checkpoints','queen_turns','enemy_q_positions']},ensure_ascii=False))
if __name__=='__main__':
 for bid,gid in GAMES:run(bid,gid)
