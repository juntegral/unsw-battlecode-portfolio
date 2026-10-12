import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
ROOT=Path.cwd(); OUT=ROOT/'data/codex/astra/sweep/1055/loss7'
sys.path.insert(0,str(ROOT/'tools')); import ladder_replay as lr
sys.path.insert(0,str(ROOT/'data/analysis/ladder/dossier/local')); from count_local import Geo

def scan(gid):
 pth=ROOT/f'data/online/smoke/one12-p1-old/M{gid}.replay'; meta=json.loads(pth.with_name(f'game-{gid}.json').read_text())
 base=lr.scan(pth,meta,'one12-p1-old',set()); root=lr.replay.load(pth).root()
 bodies={};teams={};edges=[];pearls=set()
 for line in root.text(0).splitlines():
  q=line.split()
  if not q:continue
  if q[0]=='MAP':w,h=map(int,q[1:3])
  elif q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':edges.append(tuple(map(int,q[1:4])))
 uq=base['queens']['us'];eq=base['queens']['them']
 geo=Geo(w,h,edges); turns=[];splits=[];r=-1;cur=None;actor=None;post=[]
 tile=lambda p:p[1]*w+p[0]
 xy=lambda c:[c%w,c//w]
 def near(src):
  ds={src:0};queue=deque([src])
  while queue:
   c=queue.popleft()
   if ds[c]==5:continue
   for d in geo.adj[c]:
    if d not in ds:ds[d]=ds[c]+1;queue.append(d)
  return ds
 def board(src):
  rows=[];loc=[]
  for dy in range(-3,4):
   row=''
   for dx in range(-3,4):
    c=((src//w+dy)%h)*w+(src%w+dx)%w;v='*' if c in pearls else '.'
    for i,b in bodies.items():
     if c in b:v=('Q' if i==uq else 'K' if i==eq else 'A' if teams[i]==0 else 'B') if c==b[0] else ('a' if teams[i]==0 else 'b')
    row+=v
   rows.append(row)
  for i,b in bodies.items():
   dx=min(abs(b[0]%w-src%w),w-abs(b[0]%w-src%w));dy=min(abs(b[0]//w-src//w),h-abs(b[0]//w-src//w))
   if dx<=3 and dy<=3:loc.append([i,len(b),xy(b[0])])
  return rows,loc
 def finish():
  if cur is not None:
   cur['end']=xy(bodies[actor][0]) if actor in bodies else None;cur['endlen']=len(bodies.get(actor,()))
 for ei,ev in enumerate(root.pointer(3)):
  k=lr.replay.EVENT_NAMES[ev.u16(0)];p=ev.pointer(0)
  if k=='roundStart':finish();cur=None;r=p.i32(0)
  elif k=='turnStart':
   finish();actor=p.i32(0);src=bodies[actor][0]
   cur=dict(r=r,id=actor,L=len(bodies[actor]),head=xy(src),units=sum(teams[i]==teams[actor] for i in bodies),steps=[],eats=0,action=None)
   if actor in (0,1) or r<20:
    cur['board'],cur['near']=board(src)
    cur['body']=[xy(c) for c in bodies[actor]]
    cur['exits']=[[d,kind,xy(t),[[i,list(b).index(t)] for i,b in bodies.items() if t in b]] for d,(kind,t) in enumerate(geo.moves[src])]
   turns.append(cur)
   if uq not in bodies and eq in bodies:
    ds=near(src);dist=ds.get(bodies[eq][0],99)
    if teams[actor]==0 and dist<=5:post.append(dict(r=r,id=actor,L=len(bodies[actor]),head=xy(src),queen=xy(bodies[eq][0]),d=dist))
  elif k=='dragonAction':
   a=p.pointer(0);cur['action']=dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [])
  elif k=='tileChange':
   c=tile(lr.replay.point(p.pointer(0)))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);cur['eats']+=1
  elif k=='dragonUpdate':
   i=p.i32(0);hd=tile(lr.replay.point(p.pointer(0)));tl=tile(lr.replay.point(p.pointer(1)));b=bodies[i]
   if hd!=b[0]:b.appendleft(hd);cur['steps'].append(xy(hd))
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k=='dragonSplit':
   parent,child=p.i32(0),p.i32(4);before=len(bodies[parent])
   for z,i in enumerate((parent,child)):bodies[i]=deque(tile(lr.replay.point(c)) for c in p.pointer(z));teams[i]=p.u16(8)
   splits.append(dict(r=r,parent=parent,child=child,before=before,after=len(bodies[parent]),units=cur['units']))
  elif k=='dragonDeath':
   i=p.i32(0)
   if i in (0,1):
    cur['deathboard'],cur['deathnear']=board(bodies[i][0]);cur['deathbody']=[xy(c) for c in bodies[i]]
   bodies.pop(i)
 finish()
 base.pop('text');base.pop('pearls');base.pop('natural');base.pop('intervals');base.pop('eaten_rounds')
 out=dict(base=base,turns=turns,splits=splits,post=post,dimensions=[w,h],finalbodies={i:[xy(c) for c in b] for i,b in bodies.items()},teams=teams)
 (OUT/f'{gid}.json').write_text(json.dumps(out,ensure_ascii=False))
 qd=[d for d in base['deaths'] if d['id'] in (0,1)]
 print(json.dumps(dict(gid=gid,bots=base['bots'],final=base['final'],last=base['last_round'],qd=qd,splits=[s for s in splits if s['parent'] in (0,1)],postn=len(post),postfirst=post[:3]),ensure_ascii=False))
 for d in qd:
  for t in [t for t in turns if t['id']==d['id'] and t['r']<=d['round']][-3:]:print('QTURN',json.dumps(t))
 return out
if __name__=='__main__':
 for gid in (1503506,1503508,1503509):scan(gid)
