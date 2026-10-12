import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict,deque
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
from ladder_replay import edge_id,canonical_edges
from scoreboard import load_replay
P=Path(__file__).parent
for gid,folder in [(1503514,'data/online/smoke/one12-p1-old'),(1503515,'data/online/smoke/one12-p1-old'),(1503326,'data/online/live-one1/b1503326')]:
 r=json.loads((P/f'{gid}-detail.json').read_text());w,h=r['size'];q,eq=r['queens'];teams=r['teams'];root=load_replay(Path(folder)/f'M{gid}.replay').root()
 raw=[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')];edges=canonical_edges(w,h,raw); portals=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:portals[p].append(e)
 def dest(c,d):
  e=edge_id(w,h,*c,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   other=next(z for z in portals[p] if z!=e);row,x=divmod(other,w+1);y=row//2
   return ((x-(d==3))%w,(y-(d==0))%h)
  dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d];return ((c[0]+dx)%w,(c[1]+dy)%h)
 print('\nGAME',gid)
 boards=[]
 for t in r['queen_turns'][-6:]:
  hd=tuple(t['body'][0]);world=t['world'];occ={tuple(c):(int(i),k) for i,b in world.items() for k,c in enumerate(b)}
  print('r',t['r'],'head',hd,'length',len(t['body']),'directions',t['dirs'],'steps',t['steps'])
  print('exits', [('NESW'[d],dest(hd,d),occ.get(dest(hd,d))) for d in range(4)])
  if t in r['queen_turns'][-3:]:
   grid=[];legend=[]
   for dy in range(-3,4):
    row=[]
    for dx in range(-3,4):
     c=((hd[0]+dx)%w,(hd[1]+dy)%h);ch='*' if list(c) in t['pearls'] else '.'
     if c in occ:
      i,k=occ[c];ch=('Q' if i==q else 'M' if teams[str(i)]==teams[str(q)] else 'E') if k==0 else ('q' if i==q else 'm' if teams[str(i)]==teams[str(q)] else 'e')
     suffix=''.join('NESW'[d] if edges.get(edge_id(w,h,*c,d),(0,-1))[0]==1 else 'nesw'[d] if edges.get(edge_id(w,h,*c,d),(0,-1))[0]==2 else '' for d in range(4))
     row.append(ch+suffix)
     if c in occ:legend.append((c,*occ[c]))
    grid.append(row)
   print('\n'.join(' '.join(f'{v:6}' for v in row) for row in grid));print('occupants',legend)
   boards.append(dict(round=t['r'],head=hd,grid=grid,action=t['dirs'],occupants=legend))
 d=next(d for d in r['deaths'] if d['id']==q);a=d['attack'];hd=tuple(d['body'][0]);target=dest(hd,a['dirs'][len(a['steps'])]) if a['dirs'] else None
 print('death target',target,'occupants',[(i,b.index(list(target))) for i,b in d['world'].items() if target is not None and list(target) in b])
 # Static topology is directed; ignore bodies and include every true portal.
 seen={hd};queue=deque([hd])
 while queue:
  c=queue.popleft()
  for di in range(4):
   n=dest(c,di)
   if n is not None and n not in seen:seen.add(n);queue.append(n)
 epos=tuple(d['world'][str(eq)][0]) if str(eq) in d['world'] else None
 print('queen-death component',len(seen),'enemy q',epos,'reachable',epos in seen)
 print('queen positions after death bounding', [(min(z[0][i] for z in r['enemy_queen_positions']),max(z[0][i] for z in r['enemy_queen_positions'])) for i in range(2)])
 (P/f'{gid}-boards.json').write_text(json.dumps(boards))
