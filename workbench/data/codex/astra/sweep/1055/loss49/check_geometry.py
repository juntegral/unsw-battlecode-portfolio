import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
import ladder_replay as lr
from collections import defaultdict,deque
from pathlib import Path
OUT=Path(__file__).resolve().parent
for gid in (1512824,1513846,1513847):
 z=json.loads((OUT/f'{gid}-detail.json').read_text());t=z['queen_last3'][-1];sc=t['scene'];W,H=z['W'],z['H'];edges=lr.canonical_edges(W,H,sc['edges']);portals=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:portals[p].append(e)
 def dest(c,d):
  e=lr.edge_id(W,H,*c,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   e=next(v for v in portals[p] if v!=e);row,x=divmod(e,W+1);return ((x-(d==3))%W,(row//2-(d==0))%H)
  dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 def flood(h,occ=set()):
  ds={h:0};q=deque([h])
  while q:
   c=q.popleft()
   for d in range(4):
    n=dest(c,d)
    if n is not None and n not in ds and n not in occ:ds[n]=ds[c]+1;q.append(n)
  return ds
 print('GAME',gid)
 if gid==1513846:
  q=tuple(z['enemyq_positions']['215']);comp=flood(q);print('enemyqueen component size',len(comp),'own component',len(flood(tuple(t['body'][0]))),'enemy range',min(x for x,y in comp),max(x for x,y in comp),min(y for x,y in comp),max(y for x,y in comp))
 if gid==1512824:
  body=[tuple(c) for c in t['body']];pearl={tuple(c) for c in sc['pearls']};occ={tuple(c) for i,b in sc['bodies'].items() if i!='1' for c in b};enemies=[a for a in t['nearby'] if a['team']=='A'];paths=[]
  def walk(b,dirs,eaten):
   if dirs:
    blocked=occ|set(b[1:]);risks=[]
    for e in enemies:
     eb=[tuple(c) for c in e['body']];ds=flood(eb[0],blocked-set(eb));dist=ds.get(b[0],99999);risks.append((e['id'],dist))
    paths.append((dirs,b[0],risks))
   if len(dirs)>=2:return
   for d in range(4):
    n=dest(b[0],d)
    if n is None or n in occ or n in b:continue
    if len(dirs)>=1 and len(b)<=2:continue
    eat=n in pearl and n not in eaten;nb=[n]+b
    if not eat:nb.pop()
    if len(dirs)>=1:nb.pop()
    walk(nb,dirs+'NESW'[d],eaten|({n} if eat else set()))
  walk(body,'',set());print('paths',paths)
  print('stride conservative',[(ds,c,[(e['id'],flood(tuple(e['body'][0])).get(c),4) for e in enemies]) for ds,c,rs in paths])
