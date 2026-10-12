import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,'data/analysis/ladder/dossier/local')
import spawn
from replay_format import point
from count_local import Geo
OUT=Path('data/codex/astra/sweep/1055/loss19')
for gid in (1506219,1506220,1506221):
 root=spawn.read(Path(f'data/online/smoke/one13-c1-old/M{gid}.replay'))
 bodies={};teams={};edges=[];w,h=map(int,root.text(0).splitlines()[0].split()[1:])
 for line in root.text(0).splitlines():
  a=line.split()
  if a[0]=='DRAGON':
   i=len(bodies);teams[i]=int(a[1]);bodies[i]=deque(int(a[4+2*k])*w+int(a[3+2*k]) for k in range(int(a[2])))
  elif a[0]=='EDGE':edges.append(tuple(map(int,a[1:4])))
 geo=Geo(w,h,edges);queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 xy=lambda c:[c%w,c//w]
 def distances(src,limit=5):
  dist={src:0};q=deque([src])
  while q:
   c=q.popleft()
   if dist[c]==limit:continue
   for t in geo.adj[c]:
    if t not in dist:dist[t]=dist[c]+1;q.append(t)
  return dist
 cache={}
 def near():
  if queens[0] in bodies or queens[1] not in bodies:return
  t=bodies[queens[1]][0]
  if t not in cache:cache[t]=distances(t)
  # reverse distance checked below using source search for asymmetric portals
  for i,b in bodies.items():
   if teams[i]==0 and cache[t].get(b[0],99)<=5:
    d=distances(b[0]).get(t,99)
    if d<=5:approach.append([rnd,i,d,xy(b[0]),xy(t)])
 def state():
  return [dict(n=sum(teams[i]==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),long=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),q=len(bodies.get(queens[s],[])),leaders=sorted([[i,len(b),xy(b[0])] for i,b in bodies.items() if teams[i]==s],key=lambda a:-a[1])[:4]) for s in (0,1)]
 def board(hd):
  occ={c:('Q' if i==queens[0] and j==0 else 'K' if i==queens[1] and j==0 else 'A' if teams[i]==0 and j==0 else 'B' if teams[i]==1 and j==0 else 'a' if teams[i]==0 else 'b') for i,b in bodies.items() for j,c in enumerate(b)}
  # cells with outgoing N/E/S/W wall bits recorded separately to preserve exact 7x7 cells.
  rows=[];walls=[]
  for dy in range(-3,4):
   row=[];wall=[]
   for dx in range(-3,4):
    c=((hd//w+dy)%h)*w+(hd%w+dx)%w
    row.append(occ.get(c,'*' if c in pearls else '.'));wall.append(format(sum(1<<d for d,(k,t) in enumerate(geo.moves[c]) if k==1),'x'))
   rows.append(''.join(row));walls.append(''.join(wall))
  return dict(cells=rows,walls=walls,nearby=[[i,len(b),xy(b[0])] for i,b in bodies.items() if b[0] in geo.window(hd)])
 rnd=-1;actor=None;turn=None;pearls=set();turns=[];deaths=[];splits=[];snaps={};approach=[];eats=[0,0];qturns=[]
 for ix,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   if rnd>=0:snaps[rnd]=state()
   rnd=p.i32(0);actor=None
  elif k==1:
   actor=p.i32(0);b=bodies[actor]
   turn=dict(r=rnd,id=actor,s=teams[actor],L=len(b),head=xy(b[0]),body=list(map(xy,b)),moves=[],eat=0,action=None)
   if actor==queens[0]:turn['board']=board(b[0]);qturns.append(turn)
   turns.append(turn);near()
  elif k==3:
   c=point(p.pointer(0));c=c[1]*w+c[0]
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);eats[teams[actor]]+=1;turn['eat']+=1
  elif k==4:
   a=p.pointer(0);turn['action']=[a.u16(0),list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else []]
  elif k==9:
   i=p.i32(0);h0=point(p.pointer(0));t0=point(p.pointer(1));hd=h0[1]*w+h0[0];tail=t0[1]*w+t0[0];b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);turn['moves'].append(xy(hd))
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   i,j=p.i32(0),p.i32(4);splits.append([rnd,i,j,len(bodies[i])])
   for z,di in enumerate((i,j)):bodies[di]=deque(point(pt)[1]*w+point(pt)[0] for pt in p.pointer(z));teams[di]=p.u16(8)
  elif k==11:
   i=p.i32(0);deaths.append(dict(r=rnd,id=i,s=teams[i],L=len(bodies[i]),head=xy(bodies[i][0]),reason=p.u16(4),actor=actor,actor_turn=turn.copy(),board=board(bodies[i][0]) if i in queens else None));bodies.pop(i)
 snaps[rnd]=state()
 st=root.pointer(4)
 for s in (0,1):
  result=st.pointer(s);assert [snaps[rnd][s][a] for a in ('n','long','total','q')]==[result.i32(o) for o in (0,4,8,12)]
 final=snaps[rnd];last_nonloss=max((r for r,ss in snaps.items() if tuple(ss[0][a] for a in ('q','long','total'))>=tuple(ss[1][a] for a in ('q','long','total'))),default=-1)
 data=dict(gid=gid,bot=root.text(1),w=w,h=h,queens=queens,final=final,snaps=snaps,deaths=deaths,splits=splits,qturns=qturns,approach=approach,turns=turns,eats=eats,last_nonloss=last_nonloss,end_reason=st.u16(2))
 (OUT/f'{gid}.json').write_text(json.dumps(data))
 print(gid,'bot',data['bot'],'queens',queens,'final',final,'last_nonloss',last_nonloss,'end_reason',data['end_reason'],'eats',eats)
 print('Qdeath',[{k:v for k,v in d.items() if k not in ('board','actor_turn')} for d in deaths if d['id'] in queens]);print('approach',len(approach),approach[:3]);print('last Q turns',[(t['r'],t['L'],t['head'],t['action'],t['moves']) for t in qturns[-3:]])
