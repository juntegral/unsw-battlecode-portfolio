import sys,json,ast,types
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
import ladder_replay as lr
pmod=Path('data/analysis/ladder/dossier/work/tq2_near.py');tree=ast.parse(pmod.read_text());tree.body=[n for n in tree.body if not(isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='main')];mod=types.ModuleType('geo');exec(compile(tree,str(pmod),'exec'),mod.__dict__)
P=Path('data/codex/astra/sweep/0509/loss1');F=Path('data/online/smoke/one10-k1-old');boards=[]
for gid in [1489836,1489844,1489845]:
 d=json.loads((P/f'{gid}-detail.json').read_text());root=lr.replay.load(F/f'M{gid}.replay').root();w,h=d['size'];raw=[tuple(map(int,t.split()[1:4])) for t in root.text(0).splitlines() if t.startswith('EDGE ')];g=mod.Geo(w,h,raw);qs=d['queens'];teams={int(i):s for i,s in d['teams'].items()}
 print('\nGAME',gid)
 for t in d['lastq']:
  cells={c:('Q' if int(i)==qs[0] and j==0 else 'q' if int(i)==qs[0] else 'A' if teams[int(i)]==0 and j==0 else 'a' if teams[int(i)]==0 else 'E' if j==0 else 'e') for i,b in t['bodies'].items() for j,c in enumerate(b)};cx,cy=t['head'];render=[]
  for dy in range(-3,4):
   y=(cy+dy)%h;upper='';row=''
   for dx in range(-3,4):
    x=(cx+dx)%w;c=y*w+x
    north=g.edges.get(lr.edge_id(w,h,x,y,0),(0,-1))[0];west=g.edges.get(lr.edge_id(w,h,x,y,3),(0,-1))[0]
    upper+='+'+('-' if north==1 else 'O' if north==2 else ' ')
    row+=('|' if west==1 else 'O' if west==2 else ' ')+cells.get(c,'*' if c in t['pearls'] else '.')
   east=g.edges.get(lr.edge_id(w,h,(cx+3)%w,y,1),(0,-1))[0];render.extend([upper+'+',row+('|' if east==1 else 'O' if east==2 else ' ')])
  y=(cy+3)%h;render.append(''.join('+'+('-' if g.edges.get(lr.edge_id(w,h,(cx+dx)%w,y,2),(0,-1))[0]==1 else 'O' if g.edges.get(lr.edge_id(w,h,(cx+dx)%w,y,2),(0,-1))[0]==2 else ' ') for dx in range(-3,4))+'+')
  boards.append(dict(gid=gid,r=t['r'],head=t['head'],board='\n'.join(render)))
  hd=cy*w+cx
  print('r',t['r'],'adj',[(z,g.edges.get(lr.edge_id(w,h,cx,cy,k),(0,-1)), None if z<0 else [z%w,z//w],cells.get(z,'.')) for k,z in enumerate(g.nxt[hd])])
 rev=[[] for _ in g.nxt]
 for c,ns in enumerate(g.nxt):
  for z in ns:
   if z>=0:rev[z].append(c)
 cache={}
 def distances(dst):
  if dst not in cache:
   ds={dst:0};q=deque([dst])
   while q:
    c=q.popleft()
    for z in rev[c]:
     if z not in ds:ds[z]=ds[c]+1;q.append(z)
   cache[dst]=ds
  return cache[dst]
 heads={};r=-1;dead=False;minimum=99999;witness=None;nearstates=0;qpositions=set();nearids=set();ranged=[]
 for line in root.text(0).splitlines():
  t=line.split()
  if t[0]=='DRAGON':heads[len(heads)]=int(t[4])*w+int(t[3])
 def tile(z):x,y=lr.replay.point(z);return y*w+x
 for e in root.pointer(3):
  k=e.u16(0);p=e.pointer(0)
  if k==0:r=p.i32(0)
  elif k==9:heads[p.i32(0)]=tile(p.pointer(0))
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):heads[i]=tile(next(iter(p.pointer(z))))
  elif k==11:
   i=p.i32(0);heads.pop(i);dead=dead or i==qs[0]
  else:continue
  if not dead or qs[1] not in heads:continue
  qh=heads[qs[1]];qpositions.add(qh);ds=distances(qh)
  for i,hd in heads.items():
   if teams[i]!=0:continue
   dist=ds.get(hd,99999)
   if dist<minimum:minimum=dist;witness=[r,i,[hd%w,hd//w],[qh%w,qh//w]]
   if dist<=5:nearstates+=1;nearids.add(i)
 result=dict(min_distance=None if minimum==99999 else minimum,witness=witness,near_event_states=nearstates,near_ids=sorted(nearids),enemy_queen_positions=[[c%w,c//w] for c in sorted(qpositions)],enemy_queen_reachable_cells=sorted(set(len(distances(c)) for c in qpositions)))
 (P/f'{gid}-distance.json').write_text(json.dumps(result));print(result)
(P/'boards.json').write_text(json.dumps(boards))
