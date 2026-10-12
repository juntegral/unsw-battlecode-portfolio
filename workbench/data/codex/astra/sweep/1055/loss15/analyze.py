import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
from ladder_replay import replay,edge_id
import ast, types
geo_path=Path("data/analysis/ladder/dossier/work/tq2_chase.py")
geo_ast=ast.parse(geo_path.read_text())
geo_ast.body=[n for n in geo_ast.body if not isinstance(n,ast.Expr) or not isinstance(n.value,ast.Call)]
geo_module=types.ModuleType("geo_reader")
exec(compile(geo_ast,str(geo_path),"exec"),geo_module.__dict__)
Geo=geo_module.Geo
OUT=Path(__file__).parent

def run(gid):
 base=json.loads((OUT/f'{gid}-base.json').read_text()); qs=base['queens']; q=qs['us']; eq=qs['them']
 root=replay.load(Path(f'data/online/live-one1/b1504016/M{gid}.replay')).root()
 lines=root.text(0).splitlines(); w,h=map(int,lines[0].split()[1:3]); bodies={};teams={};raw=[]
 for line in lines:
  a=line.split()
  if a[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque((int(a[3+2*k]),int(a[4+2*k])) for k in range(int(a[2])));teams[i]=int(a[1])
  elif a[0]=='EDGE':raw.append(tuple(map(int,a[1:])))
 geo=Geo(w,h,raw); own=teams[q]; pearls=set();turns=[]; qt=[];deaths=[];qchanges=[];splits=[];near=[];r=0;cur=None;expected=0;origins={};eats=Counter();snaps=[]
 def cell(p):return p[1]*w+p[0]
 def board(hd):
  occ={p:('Q' if i==q and j==0 else 'q' if i==q else 'K' if i==eq and j==0 else 'k' if i==eq else 'B' if teams[i]==own and j==0 else 'b' if teams[i]==own else 'A' if j==0 else 'a') for i,b in bodies.items() for j,p in enumerate(b)}
  rows=[]
  for dy in range(-3,4):
   y=(hd[1]+dy)%h; row=''
   for dx in range(-3,4):
    x=(hd[0]+dx)%w
    row+=occ.get((x,y),'*' if (x,y) in pearls else '.')
   rows.append(row)
  edges=[]
  for dy in range(-3,4):
   for dx in range(-3,4):
    x,y=(hd[0]+dx)%w,(hd[1]+dy)%h
    vals=['NESW'[d]+('P' if geo.por[cell((x,y))][d] else '#') for d in range(4) if geo.nxt[cell((x,y))][d]<0 or geo.por[cell((x,y))][d]]
    if vals: edges.append([dx,dy,','.join(vals)])
  return dict(rows=rows,edges=edges)
 def close():
  if cur is not None:
   cur['end']=list(bodies.get(cur['id'],[]));turns.append(cur)
   if cur['id']==q: qt.append(cur)
 def check_near(idx):
  if q in bodies or eq not in bodies:return
  for i,b in bodies.items():
   if teams[i]==own:
    d=geo.ball(cell(b[0])).get(cell(bodies[eq][0]),99)
    if d<=5 and (not near or near[-1]['r']!=r):
     near.append(dict(r=r,id=i,dist=d,head=b[0],enemy=bodies[eq][0],event=idx));break
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close();cur=None;r=p.i32(0)
   if r%25==0:
    snaps.append(dict(r=r,heads={i:list(b) for i,b in bodies.items()},eats=dict(eats)))
  elif k==1:
   close();i=p.i32(0);cur=dict(r=r,id=i,L=len(bodies[i]),head=bodies[i][0],dirs=[],steps=[],eats=0)
   if i==q:
    cur['board']=board(bodies[q][0]);cur['context']={i:list(b) for i,b in bodies.items()};cur['pearls']=list(pearls)
   check_near(idx)
  elif k==4:
   a=p.pointer(0);cur['action']=a.u16(0) if a else None;cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==3:
   c=replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c);origins[c]='drop' if expected else 'natural';expected=max(0,expected-1)
   else:
    pearls.remove(c);cur['eats']+=1;eats[f'{teams[cur["id"]]}-{origins.pop(c)}']+=1
  elif k==9:
   i=p.i32(0);hd=replay.point(p.pointer(0));tl=replay.point(p.pointer(1));b=bodies[i];old=len(b)
   if b[0]!=hd:b.appendleft(hd);cur['steps'].append(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   if i==q and old!=len(b):qchanges.append(dict(r=r,old=old,new=len(b),head=hd))
   check_near(idx)
  elif k==10:
   a,b=p.i32(0),p.i32(4);L=len(bodies[a])
   for j,i in enumerate((a,b)):bodies[i]=deque(replay.point(c) for c in p.pointer(j));teams[i]=p.u16(8)
   splits.append(dict(r=r,id=a,child=b,L=L,keep=len(bodies[a]),head=bodies[a][0]))
  elif k==11:
   i=p.i32(0);expected=(len(bodies[i])+1)//2
   if i==q:
    deaths.append(dict(r=r,id=i,actor=cur['id'],actor_turn=cur.copy(),last3=(qt+([cur] if cur['id']==q else []))[-3:],context={i:list(b) for i,b in bodies.items()},board=board(bodies[i][0])))
   bodies.pop(i)
 close()
 a=dict(gid=gid,w=w,h=h,queens=qs,deaths=deaths,qchanges=qchanges,qsplits=[s for s in splits if s['id']==q],near=near,snaps=snaps,turns=[t for t in turns if t['id']==q or t['r']>=400],splits=[s for s in splits if s['r']>=400])
 (OUT/f'{gid}-detail.json').write_text(json.dumps(a))
 print(gid,'qdeath',[(d['r'],d['actor'],d['actor_turn']) for d in deaths],flush=True)
 print('qsplits',a['qsplits'],'qchanges late',[c for c in qchanges if c['r']>=380],'near',near[:3],len(near),flush=True)
 for d in deaths:
  for t in d['last3']:
   print('QTURN',t['r'],t['L'],t['head'],t['dirs'],t['steps'], 'end',t.get('end'));print('\n'.join(t['board']['rows']));print('edges',t['board']['edges'])
for gid in range(1504018,1504021):run(gid)
