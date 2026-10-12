"""Partial score reconstruction, not bot execution; timers and sonar unavailable."""
import sys
sys.dont_write_bytecode=True
sys.path[:0]=['data/codex/astra/approach']
from scan import Board,edge_id,STEP
from collections import deque,Counter
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent

def focus(gid,actor,rounds):
 B=Board(f'data/online/live-one1/b1477038/M{gid}.replay');seen=set();known=set();food=set();results=[]
 for ev in B.root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0);B.update(k,p)
  if k!=1 or B.actor!=actor:continue
  h=B.bodies[actor][0];window={c for c in B.adj if B.view(h,c)}
  seen|=window;known|={edge_id(B.W,B.H,*c,d) for c in window for d in range(4)};food-=window;food|=window&B.pearls
  if B.rnd not in rounds:continue
  body=tuple(B.bodies[actor]);L=len(body);free={c:L-z+1 for z,c in enumerate(body)}
  blocked={c for i,b in B.bodies.items() if i!=actor for c in b if c in window}
  heads=[(i,b[0]) for i,b in B.bodies.items() if i!=actor and b[0] in window]
  def step(c,d):
   e=edge_id(B.W,B.H,*c,d)
   if e not in known:
    dx,dy=STEP[d];return ((c[0]+dx)%B.W,(c[1]+dy)%B.H)
   kind,pid=B.edges.get(e,(0,-1))
   if kind==1:return None
   if kind==2 and not all(ee in known for ee,v in B.edges.items() if v==(2,pid)):return None
   return B.adj[c][d]
  def race(hs):
   ds={c:0 for c in hs};q=deque(hs)
   while q:
    c=q.popleft()
    for d in range(4):
     n=step(c,d)
     if n is not None and n not in ds and n not in blocked and n not in free:ds[n]=ds[c]+1;q.append(n)
   return ds
  ally=race([c for i,c in heads if B.teams[i]==B.teams[actor]])
  enemy=race([c for i,c in heads if B.teams[i]!=B.teams[actor]])
  opts=[]
  for d in range(4):
   dest=step(h,d)
   if dest is None or dest in blocked or dest in free:opts.append(dict(d=d,dest=dest,rejected=True));continue
   ds={dest:1};eaten={dest:int(dest in food)};q=deque([dest]);dp=None;pearls=0;ns=nu=os=ou=0
   while q:
    c=q.popleft();t=ds[c];theirs=enemy.get(c,10**9);al=ally.get(c,10**9)
    share=(1 if t<theirs else .5 if t==theirs else 0) if al>=t else 0
    if c in seen:ns+=1;os+=share
    else:nu+=1;ou+=share
    contest=L<=4 and t<=theirs+1 and al>=t
    if dp is None and c in food and (share==1 or contest):dp=t
    if c in food and share>0:pearls+=1
    for z in range(4):
     n=step(c,z)
     if n is None or n in ds or n in blocked or t+1-eaten[c]<free.get(n,0):continue
     ds[n]=t+1;eaten[n]=eaten[c]+int(n in food);q.append(n)
   pocket={dest};q=deque([dest]);doors=[];psz=None
   while q:
    c=q.popleft()
    for z in range(4):
     e=edge_id(B.W,B.H,*c,z)
     if e not in known:psz=48;break
     kind,pid=B.edges.get(e,(0,-1))
     if kind==2:
      n=step(c,z);dx,dy=STEP[z];across=((c[0]+dx)%B.W,(c[1]+dy)%B.H)
      if n is not None:doors.append((across,n))
     if kind!=0:continue
     n=step(c,z)
     if n not in pocket:pocket.add(n);q.append(n)
     if len(pocket)>=48:psz=48;break
    if psz is not None:break
   if psz is None:psz=48 if any(a in pocket and b not in pocket for a,b in doors) else len(pocket)
   room=ns+.5*nu;tail=body[-1] in ds;cramped=400*max(0,3*L+8-room)+5000*max(0,L+2-room)+(0 if tail else 600)
   penalty=1000*max(0,L+int(dest in food)-psz//2) if psz<48 else 0
   opts.append(dict(d=d,dest=dest,room=room,tail=tail,cramped=cramped,pocket=psz,pocket_penalty=penalty,dp=dp,pearl_target=0 if dp is None else max(0,2*(260-40*dp)),eat_bonus=300 if dest in food and not penalty else 0,pearls=pearls,territory_min=.5*ou,territory_max=.5*ou+os,space=1.5*room))
  results.append(dict(game=gid,r=B.rnd,id=actor,body=body,seen=len(seen),heads=heads,food=sorted(food),options=opts))
 return results
if __name__=='__main__':
 rows=focus(1477042,6,[17,20,21,61])+focus(1477048,2,[16,17])
 (OUT/'partial-scores.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
