import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
import ladder_replay as lr
import ast,types
pmod=Path('data/analysis/ladder/dossier/work/tq2_near.py')
tree=ast.parse(pmod.read_text());tree.body=[n for n in tree.body if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='main')]
mod=types.ModuleType('geo_import');exec(compile(tree,str(pmod),'exec'),mod.__dict__);Geo=mod.Geo
OUT=Path('data/codex/astra/sweep/0509/loss1')
F=Path('data/online/smoke/one10-k1-old')
for gid in (1489836,1489844,1489845):
 pth=F/f'M{gid}.replay'; meta=json.loads((F/f'game-{gid}.json').read_text())
 base=lr.scan(pth,meta,str(F),set());base['intervals']={str(k):v for k,v in base['intervals'].items()}
 (OUT/f'{gid}-base.json').write_text(json.dumps(base,ensure_ascii=False))
 root=lr.replay.load(pth).root(); lines=root.text(0).splitlines(); w,h=map(int,lines[0].split()[1:3]); bodies={};teams={};raw=[];pearls=set()
 for line in lines:
  t=line.split()
  if t[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(t[4+2*k])*w+int(t[3+2*k]) for k in range(int(t[2])));teams[i]=int(t[1])
  elif t[0]=='EDGE':raw.append(tuple(map(int,t[1:4])))
  elif t[0]=='TILE' and int(t[3]):pearls.add(int(t[2])*w+int(t[1]))
 geo=Geo(w,h,raw); qs=[min(i for i in bodies if teams[i]==s) for s in (0,1)]; qturns=[];turns=[];r=-1;a=None;turn=None;near=[]
 def xy(c):return [c%w,c//w]
 def snap():return {i:list(b) for i,b in bodies.items()}
 def tile(z):x,y=lr.replay.point(z);return y*w+x
 for idx,e in enumerate(root.pointer(3)):
  k=e.u16(0);p=e.pointer(0)
  if k==0:r=p.i32(0)
  elif k==1:
   a=p.i32(0);turn=dict(r=r,id=a,L=len(bodies[a]),head=xy(bodies[a][0]),steps=[],actions=[],logs=[],eaten=[]);turns.append(turn)
   if (gid==1489844 and a in (568,599) and 319<=r<=322) or (gid==1489845 and a==974 and 213<=r<=216):
    turn['bodies']=snap();turn['pearls']=list(pearls)
   if a==qs[0]:
    turn['bodies']=snap();turn['pearls']=list(pearls);qturns.append(turn)
   if qs[0] not in bodies and qs[1] in bodies and teams[a]==0:
    dist=geo.ball(bodies[a][0]).get(bodies[qs[1]][0],999)
    if dist<=5:near.append(dict(r=r,id=a,L=len(bodies[a]),head=xy(bodies[a][0]),q=xy(bodies[qs[1]][0]),dist=dist))
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:
    pearls.discard(c)
    if turn is not None:turn['eaten'].append(xy(c))
  elif k==4:
   ac=p.pointer(0);turn['actions'].append(dict(kind=ac.u16(0),dirs=list(ac.pointer(0)) if ac.u16(0)==0 and ac.pointer(0) is not None else [],split=ac.i32(4)))
  elif k in (5,6):
   if turn is not None:turn['logs'].append(p.text(0))
  elif k==9:
   i=p.i32(0);hd,tl=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:
    b.appendleft(hd)
    if turn is not None:turn['steps'].append([i,xy(hd)])
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0)
   if i==qs[0]:
    turn['qdeath_state']=snap();turn['qdeath_pearls']=list(pearls)
   bodies.pop(i)
 qd=next(d for d in base['deaths'] if d['id']==qs[0]);dr=qd['round']
 recent=[t for t in turns if dr-4<=t['r']<=dr+1]
 results=dict(gid=gid,map=meta['mapName'],bots=base['bots'],size=[w,h],queens=qs,death=qd,final=base['final'],lastq=qturns[-3:],near=near,near_unique=len(set(t['id'] for t in near)),final_bodies={i:list(b) for i,b in bodies.items()},teams=teams,recent=recent)
 (OUT/f'{gid}-detail.json').write_text(json.dumps(results,ensure_ascii=False))
 (OUT/f'{gid}-turns.json').write_text(json.dumps(turns,ensure_ascii=False))
 print(json.dumps({k:v for k,v in results.items() if k not in ('lastq','recent','final_bodies','teams','near')},ensure_ascii=False))
 print('lastq',[(t['r'],t['L'],t['head'],t['actions'],t['steps']) for t in qturns[-3:]])
 print('near',len(near),near[:3])
