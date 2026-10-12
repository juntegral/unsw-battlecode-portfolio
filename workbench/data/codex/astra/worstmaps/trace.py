import analyze as a
from collections import Counter,deque
import json
rs=json.loads((a.OUT/'rows.json').read_text());out=[]
for r in rs:
 root=a.lr.agg.sb.load_replay(a.Path(r['path'])).root();w=r['features']['w'];h=r['features']['h'];own='AB'.index(r['own_side']);bodies={};teams={};raw=[];bearing={}
 for line in root.text(0).splitlines():
  q=line.split()
  if not q:continue
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(int(q[1])!=own)
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 bearing={c:(1,1 if c in r['features']['fast_cells'] else 10000) for c in r['features']['bearing_cells']}
 g=a.Geo(w,h,raw);queen=[min(i for i in bodies if teams[i]==s) for s in (0,1)];rnd=-1;actor=None;cur=None;present={};expected=0;born={};deaths={};splits=[];c=[Counter(),Counter()];moments=[];first_fast=[None,None];fast_eats=[[],[]]
 def close():
  global cur
  if cur is None:return
  s=cur['s'];c[s]['turns']+=1
  if cur['L']>=4:
   tag='queen4' if cur['queen'] else 'other4';c[s][tag]+=1;c[s][tag+'_split']+=cur['split']
   if not cur['split']:
    if cur['portal']:c[s][tag+'_nosplit_portal']+=1
    if cur['L']==4 and cur['queen'] and cur['food_before'] and rnd<=30:
     c[s]['queen4_aftermeal_nosplit']+=1
  if cur['portal'] and cur['L']==4 and not cur['queen'] and not cur['split'] and cur['r']<=50 and cur['exit']:
   moments.append(cur.copy())
  cur=None
 for ev in root.pointer(3):
  k=ev.u16(0)
  if k not in (0,1,3,9,10,11):continue
  p=ev.pointer(0);tile=lambda p:a.point(p)[1]*w+a.point(p)[0]
  if k==0:
   close();rnd=p.i32(0);actor=None
   if rnd>125:break
  elif k==1:
   close();actor=p.i32(0);s=teams[actor];b=bodies[actor];occ={c for bb in bodies.values() for c in bb}
   if rnd<=100:cur=dict(r=rnd,id=actor,s=s,L=len(b),queen=actor==queen[s],portal=any(k==2 for k,d in g.moves[b[-1]]),exit=any(k!=1 and d not in occ for k,d in g.moves[b[-1]]),split=0,food_before=born.get(('eat',actor),-99)>=rnd-3,head=[b[0]%w,b[0]//w],tail=[b[-1]%w,b[-1]//w])
  elif k==3:
   cell=tile(p.pointer(0))
   if p.u32(0):
    natural=expected==0;present[cell]=natural
    if expected:expected-=1
    if natural and cell not in bearing: c[0]['natural_off_config']+=1
   else:
    natural=present.pop(cell);s=teams[actor];born['eat',actor]=rnd
    if rnd<=100 and natural:
     c[s]['natural_eat']+=1
     if bearing.get(cell,(0,10000))[1]<=10:
      c[s]['fast_eat']+=1
      event=dict(r=rnd,id=actor,xy=[cell%w,cell//w]);fast_eats[s].append(event)
      if first_fast[s] is None:first_fast[s]=event
  elif k==9:
   i=p.i32(0);hd,tl=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
  elif k==10:
   pa,ch=p.i32(0),p.i32(4)
   if cur is not None:cur['split']=1
   splits.append(dict(r=rnd,id=ch,s=teams[pa],portal=any(k==2 for k,d in g.moves[bodies[pa][-1]])))
   for z,i in enumerate((pa,ch)):bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=int(p.u16(8)!=own)
  elif k==11:
   i=p.i32(0);expected=(len(bodies[i])+1)//2;deaths[i]=rnd;bodies.pop(i)
 for sp in splits:
  if sp['r']<=100 and sp['r']+25<=min(125,r['last']) and sp['portal']:
   s=sp['s'];c[s]['portal_birth']+=1;c[s]['portal_child_survive25']+=deaths.get(sp['id'],10000)>sp['r']+25
 out.append(dict(gid=r['gid'],map=r['map'],counts=c,first_fast=first_fast,fast_eats=fast_eats,moments=moments,splits=splits))
 print(r['gid'],flush=True)
(a.OUT/'trace.json').write_text(json.dumps(out,separators=(',',':')))
