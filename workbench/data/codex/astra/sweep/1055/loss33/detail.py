import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from collections import deque
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from spawn import read
from count_local import Geo
OUT=Path(__file__).resolve().parent
details=[]
for gid in (1512565,1512566,1512568):
 d=json.loads((OUT/f'{gid}.json').read_text());w,h=d['w'],d['h'];root=read(Path(f'data/online/smoke/one13-p2-old/M{gid}.replay'))
 teams={};raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':teams[len(teams)]=int(q[1])
  if q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 for ev in root.pointer(3):
  if ev.u16(0)==10:teams[ev.pointer(0).i32(4)]=ev.pointer(0).u16(8)
 g=Geo(w,h,raw);xy=lambda c:[c%w,c//w];cell=lambda p:p[1]*w+p[0]
 rows=[]
 for t in [t for t in d['turns'] if t['id']==d['queens'][0]][-5:]:
  head=cell(t['head']);win=g.window(head);occupied={cell(c) for b in t['bodies'].values() for c in b};ps={cell(c) for c in t['pearls']}
  hits={}
  for i,b in t['bodies'].items():
   if teams[int(i)]==0 or cell(b[0]) not in win:continue
   L=len(b);start=cell(b[0]);free=(L+3)//4;queue=deque([(start,(),0)]);seen=set()
   while queue:
    c,path,eaten=queue.popleft();steps=len(path)
    if steps>=4 or (steps>=free and L+eaten-max(0,steps-free)<=2):continue
    for kind,n in g.moves[c]:
     if kind==1 or n not in win or n in occupied or n==start or n in path:continue
     key=(n,steps+1,eaten+int(n in ps))
     if key in seen:continue
     seen.add(key);hits.setdefault(n,[]).append([int(i),[xy(z) for z in (start,)+path+(n,)]])
     queue.append((n,path+(n,),key[2]))
  opts=[]
  for dr,(kind,n) in zip('NESW',g.moves[head]):
   opts.append(dict(dir=dr,kind=kind,xy=xy(n),occupied=n in occupied,attackers=hits.get(n,[])))
  row=dict(r=t['r'],head=t['head'],L=t['L'],ours=sum(teams[int(i)]==0 for i in t['bodies']),options=opts)
  rows.append(row)
  print(gid,t['r'],[(o['dir'],o['kind'],o['occupied'],[(x[0],len(x[1])-1) for x in o['attackers']]) for o in opts])
 details.append(dict(gid=gid,bot_id=int(root.text(1)),rows=rows))
(OUT/'detail.json').write_text(json.dumps(details,indent=2))
