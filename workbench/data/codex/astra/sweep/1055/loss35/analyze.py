import sys,json
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
from ladder_replay import replay,edge_id,canonical_edges
OUT=Path(__file__).parent
BASE=Path('data/online/live-one1/b1513119')
def analyze(gid):
 root=replay.load(BASE/f'M{gid}.replay').root()
 ledger=json.loads((OUT/f'{gid}-ledger.json').read_text())
 W,H=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  if q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 edges=canonical_edges(W,H,raw);queen=ledger['queens']['us'];qd=next(d for d in ledger['deaths'] if d['id']==queen);killer=qd['actor']
 pearls=set();rnd=-1;turn=None;qt=[];kt=[];splits=[];eats=[];visits={};crossings=[]
 def context(focal=None):
  focal=queen if focal is None else focal
  h=bodies[focal][0];occ={c:('Q' if i==queen and k==0 else 'q' if i==queen else 'H' if teams[i]==1 and k==0 else 'b' if teams[i]==1 else 'X' if k==0 else 'x') for i,b in bodies.items() for k,c in enumerate(b)}
  rows=[];walls=[];near=[]
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    c=((h[0]+dx)%W,(h[1]+dy)%H);row.append(occ.get(c,'*' if c in pearls else '.'))
    kinds=[edges.get(edge_id(W,H,*c,d),(0,-1))[0] for d in range(4)]
    if any(kinds):walls.append([dx,dy,''.join('NESW'[d] for d,v in enumerate(kinds) if v==1),''.join('NESW'[d] for d,v in enumerate(kinds) if v==2)])
   rows.append(''.join(row))
  for i,b in bodies.items():
   dx=min(abs(b[0][0]-h[0]),W-abs(b[0][0]-h[0]));dy=min(abs(b[0][1]-h[1]),H-abs(b[0][1]-h[1]))
   if max(dx,dy)<=6:near.append([i,teams[i],len(b),list(b[0]),list(b)])
  return dict(head=list(h),body=list(bodies[focal]),board=rows,edges=walls,near=near)
 def finish():
  if turn is not None:turn['end']=list(bodies.get(turn['id'],[]))
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:finish();turn=None;rnd=p.i32(0)
  elif k==1:
   finish();i=p.i32(0);turn=dict(r=rnd,id=i,start=list(bodies[i]),dirs=[],updates=[],eats=[])
   visits.setdefault(i,set()).add(bodies[i][0])
   if i==queen:turn['view']=context();qt.append(turn)
   if i==killer or (gid==1513123 and rnd>=450) or (gid==1513120 and rnd<=100 and teams[i]==1):kt.append(turn)
   if gid==1513123 and i==1234 and rnd>=458:turn['view']=context(i)
  elif k==4:
   a=p.pointer(0);turn['kind']=a.u16(0) if a else None;turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==3:
   c=replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.discard(c);turn['eats'].append(c);eats.append([rnd,turn['id'],teams[turn['id']],c])
  elif k==9:
   i=p.i32(0);h=replay.point(p.pointer(0));tail=replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=h:
    old=b[0];dx=min(abs(h[0]-old[0]),W-abs(h[0]-old[0]));dy=min(abs(h[1]-old[1]),H-abs(h[1]-old[1]))
    if dx+dy>1:crossings.append([rnd,i,teams[i],old,h])
    b.appendleft(h)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
   if turn:turn['updates'].append([i,list(b)])
  elif k==10:
   i=p.i32(0);child=p.i32(4)
   splits.append([rnd,i,child,len(bodies[i]),[replay.point(c) for c in p.pointer(0)],[replay.point(c) for c in p.pointer(1)]])
   for z,n in enumerate((i,child)):bodies[n]=deque(replay.point(c) for c in p.pointer(z));teams[n]=p.u16(8)
  elif k==11:
   i=p.i32(0)
   if i==queen:turn['queen_death_view']=context()
   bodies.pop(i)
 finish()
 def score(s):return (int(s['alive']>0),s['queen_length'],s['longest'],s['total'])
 snaps=ledger['snapshots'];nonloss=[int(r) for r,s in snaps.items() if score(s['us'])>=score(s['them'])];last_nonloss=max(nonloss,default=-1)
 out=dict(gid=gid,size=[W,H],queen=queen,killer=killer,last_nonloss=last_nonloss,permanent_score_deficit=last_nonloss+1,queen_last_turns=qt[-3:],killer_turns=[t for t in kt if t['id']==killer and t['r']>=qd['round']-3],all_splits=splits,queen_splits=[s for s in splits if s[1]==queen],queen_turns=qt,late_turns=kt,crossings=crossings,visits={i:len(v) for i,v in visits.items()},eats=eats,final_bodies={i:list(b) for i,b in bodies.items()},teams=teams)
 (OUT/f'{gid}-detail.json').write_text(json.dumps(out))
 print(gid,'permanent score deficit',last_nonloss+1,'last q turns',[(t['r'],t['start'],t['dirs'],t['end']) for t in qt[-3:]],'killer',[(t['r'],t['start'],t['dirs'],t['end']) for t in out['killer_turns']],flush=True)
for gid in [1513120,1513121,1513123]:analyze(gid)
