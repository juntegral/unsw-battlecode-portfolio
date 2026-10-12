import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
from ladder_replay import replay
from count_local import Geo
from pathlib import Path
from collections import deque,Counter
OUT=Path(__file__).parent

def scan(gid):
 root=replay.load(Path(f'data/online/smoke/one12-c1-old/M{gid}.replay')).root()
 W,H=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={}; teams={}; raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque(int(q[4+2*k])*W+int(q[3+2*k]) for k in range(int(q[2]))); teams[i]=int(q[1])
  elif q and q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
 geo=Geo(W,H,raw); queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 rnd=-1; turn=None; turns=[]; pearls=set(); near=[]; died=False; deaths=[]; balls={}; rounds={}
 def xy(c): return [c%W,c//W]
 def ball(src):
  if src not in balls:
   ds={src:0}; qu=deque([src])
   while qu:
    c=qu.popleft()
    if ds[c]==5: continue
    for n in geo.adj[c]:
     if n not in ds: ds[n]=ds[c]+1; qu.append(n)
   balls[src]=ds
  return balls[src]
 def observe(idx):
  if died and queens[1] in bodies:
   qh=bodies[queens[1]][0]
   for i,b in bodies.items():
    if teams[i]==0 and ball(b[0]).get(qh,99)<=5:
     near.append([rnd,idx,i,ball(b[0])[qh],xy(b[0]),xy(qh)])
 def close():
  if turn is not None:
   turn['end']=list(bodies.get(turn['id'],[])); turns.append(turn)
 def snap(): return [[len(bodies.get(queens[s],())),max([len(b) for i,b in bodies.items() if teams[i]==s],default=0),sum(len(b) for i,b in bodies.items() if teams[i]==s),sum(teams[i]==s for i in bodies)] for s in (0,1)]
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0); p=ev.pointer(0)
  if k==0:
   close();turn=None
   if rnd>=0: rounds[rnd]=snap()
   rnd=p.i32(0)
  elif k==1:
   close(); i=p.i32(0)
   turn={'r':rnd,'event':idx,'id':i,'side':teams[i],'body':list(bodies[i]),'eat':0,'path':[],'action':None,'split':None}
   if i in queens:
    turn['all']={j:list(b) for j,b in bodies.items()};turn['pearls']=sorted(pearls)
  elif k==3:
   x,y=replay.point(p.pointer(0)); c=y*W+x
   if p.u32(0): pearls.add(c)
   else: pearls.remove(c);turn['eat']+=1
  elif k==4:
   a=p.pointer(0);turn['action']=a.u16(0) if a else None;turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==9:
   i=p.i32(0);x,y=replay.point(p.pointer(0));h=y*W+x;x,y=replay.point(p.pointer(1));t=y*W+x
   if bodies[i][0]!=h: bodies[i].appendleft(h);turn['path'].append(h)
   while len(bodies[i])>1 and bodies[i][-1]!=t: bodies[i].pop()
   assert bodies[i][-1]==t
  elif k==10:
   par,ch=p.i32(0),p.i32(4);turn['split']=[par,ch]
   for z,i in enumerate((par,ch)):
    bodies[i]=deque(replay.point(c)[1]*W+replay.point(c)[0] for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0); deaths.append({'r':rnd,'id':i,'reason':p.u16(4),'actor':turn['id'],'body':list(bodies[i]),'all':{j:list(b) for j,b in bodies.items()}});bodies.pop(i)
   if i==queens[0]:died=True
  if k in (1,9,10,11):observe(idx)
 close();rounds[rnd]=snap()
 d={'gid':gid,'W':W,'H':H,'queens':queens,'teams':teams,'turns':turns,'deaths':deaths,'near5':near,'rounds':rounds,'raw':raw}
 (OUT/f'{gid}-detail.json').write_text(json.dumps(d))
 print('GAME',gid,W,H,'Q',queens,'near5',len(near),'first',near[:1])
 qd=next(z for z in deaths if z['id']==queens[0]); ats=[t for t in turns if t['id']==qd['actor'] and t['r']==qd['r']]
 print('ATTACKER',ats)
 for t in [t for t in turns if t['id']==queens[0]][-5:]:
  small={k:v for k,v in t.items() if k not in ('all','pearls')};small['body']=list(map(xy,t['body']));small['path']=list(map(xy,t['path']));print('QUEEN',small)
  enemies=[(i,len(b),xy(b[0])) for i,b in t['all'].items() if teams[i]==1 and b[0] in geo.window(t['body'][0])];print('enemies',enemies)
  for di,(kind,n) in enumerate(geo.moves[t['body'][0]]):print('exit','NESW'[di],kind,xy(n),[(i,b.index(n)) for i,b in t['all'].items() if n in b])
 print('splits',[{k:v for k,v in t.items() if k not in ('all','pearls')} for t in turns if t['id']==queens[0] and t['split']])
 for lo,hi in [(0,50),(51,100),(101,150),(151,200),(201,300),(301,499)]:
  print('economy',lo,hi,[(len(ts:=[t for t in turns if t['side']==s and lo<=t['r']<=hi]),sum(t['eat'] for t in ts),sum(t['action']==1 for t in ts),len(set(t['body'][0] for t in ts))) for s in (0,1)])
 print('persistent total deficit',max([r for r,ss in rounds.items() if ss[0][2]>=ss[1][2]],default=-1)+1)
 print('persistent score deficit',max([r for r,ss in rounds.items() if tuple(ss[0][:3])>=tuple(ss[1][:3])],default=-1)+1)
for gid in (1501669,1501670,1501672):scan(gid)
