import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['data/analysis/ladder/dossier/work','data/analysis/ladder/dossier/local','tools']
from o1_scan import scan
from ladder_replay import replay,canonical_edges,edge_id
from count_local import Geo
OUT=Path('data/codex/astra/sweep/0444/loss3')
for gid in (1488840,1488841):
 pth=Path(f'data/online/live-one1/b1488840/M{gid}.replay'); meta=json.loads(pth.with_name(f'game-{gid}.json').read_text())
 base=scan('loss3',pth,meta); (OUT/f'{gid}-ledger.json').write_text(json.dumps(base))
 root=replay.load(pth).root(); lines=root.text(0).splitlines(); W,H=map(int,lines[0].split()[1:]); bodies={}; teams={}; raw=[]
 for line in lines:
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque(replay.point(x) for x in [])
   bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 geo=Geo(W,H,raw); edges=canonical_edges(W,H,raw)
 queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 turns=[]; deaths=[]; snaps={}; pearls=set(); rnd=-1;t=None; close5=[]; distcache={}; closest=[]; rev=[[] for _ in range(W*H)]
 for c,ns in enumerate(geo.adj):
  for n in ns:rev[n].append(c)
 def snap():
  return [[len(bodies.get(queens[s],[])),max([len(b) for i,b in bodies.items() if teams[i]==s],default=0),sum(len(b) for i,b in bodies.items() if teams[i]==s),sum(teams[i]==s for i in bodies)] for s in (0,1)]
 def state():return {i:list(b) for i,b in bodies.items()}
 def near():
  if queens[0] in bodies or queens[1] not in bodies:return
  q=bodies[queens[1]][0]; qi=q[1]*W+q[0]
  if qi not in distcache:
   dd=[-1]*(W*H);dd[qi]=0;qq=deque([qi])
   while qq:
    c=qq.popleft()
    for n in rev[c]:
     if dd[n]<0:dd[n]=dd[c]+1;qq.append(n)
   distcache[qi]=dd
  dd=distcache[qi]
  for i,b in bodies.items():
   if teams[i]==0 and 0<=dd[b[0][1]*W+b[0][0]]:
    rec=[rnd,i,len(b),list(b[0]),list(q),dd[b[0][1]*W+b[0][0]]]
    if not closest or rec[-1]<closest[0][-1]:closest[:]=[rec]
    if rec[-1]<=5:close5.append(rec)
 for ix,e in enumerate(root.pointer(3)):
  k=e.u16(0); p=e.pointer(0)
  if k==0:
   if rnd>=0:snaps[rnd]=snap()
   rnd=p.i32(0)
  elif k==1:
   i=p.i32(0);t=dict(r=rnd,i=i,L=len(bodies[i]),head=list(bodies[i][0]),steps=[],eats=[],actions=[])
   if i in queens:t['bodies']=state();t['pearls']=list(pearls)
   turns.append(t);near()
  elif k==4:
   a=p.pointer(0);t['actions'].append(dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []))
  elif k==3:
   c=replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.discard(c);t['eats'].append(list(c))
  elif k==9:
   i=p.i32(0);hd,tl=replay.point(p.pointer(0)),replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);t['steps'].append(list(hd))
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
   near()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
   near()
  elif k==11:
   i=p.i32(0);deaths.append(dict(r=rnd,i=i,L=len(bodies[i]),reason=p.u16(4),actor=t['i'],body=list(bodies[i]),turn=t.copy()))
   bodies.pop(i);near()
 snaps[rnd]=snap()
 out=dict(gid=gid,W=W,H=H,queens=queens,teams=teams,bot=[root.text(1),root.text(2)],snaps=snaps,deaths=deaths,queen_turns=[t for t in turns if t['i'] in queens],close5=close5,closest=closest,turns=[{k:v for k,v in t.items() if k not in ('bodies','pearls')} for t in turns],final_bodies=state())
 (OUT/f'{gid}-detail.json').write_text(json.dumps(out))
 print(gid,'bot',out['bot'],'final Q/max/total/n',snaps[rnd],'queen deaths',[(d['r'],d['i'],d['L'],d['reason'],d['actor'],d['turn']['head'],d['turn']['steps'],d['turn']['actions']) for d in deaths if d['i'] in queens], 'near5',len(close5),close5[:3])
 print('last queen turns',[(t['r'],t['L'],t['head'],t['steps'],t['actions']) for t in out['queen_turns'] if t['i']==queens[0]][-5:])
