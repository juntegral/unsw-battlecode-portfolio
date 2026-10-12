import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as lr,scoreboard
from collections import deque,defaultdict,Counter
from pathlib import Path
O=Path('data/codex/astra/sweep/1055/loss36'); S=Path('data/online/smoke/one13-q1-old')
for gid in (1515658,1515660,1515661):
 root=scoreboard.load_replay(S/f'M{gid}.replay').root(); G=json.loads((O/f'{gid}-ledger.json').read_text()); q=G['queens']; qd=next(d['round'] for d in G['deaths'] if d['id']==q['us'])
 W,H=map(int,root.text(0).splitlines()[0].split()[1:3]); B={};T={};raw=[]
 for l in root.text(0).splitlines():
  a=l.split()
  if a[0]=='DRAGON':
   i=len(B); B[i]=deque((int(a[3+2*k]),int(a[4+2*k])) for k in range(int(a[2]))); T[i]=int(a[1])
  if a[0]=='EDGE':raw.append(tuple(map(int,a[1:4])))
 E=lr.canonical_edges(W,H,raw);P=defaultdict(list)
 for e,(k,p) in E.items():
  if k==2:P[p].append(e)
 def dest(c,d):
  e=lr.edge_id(W,H,*c,d);k,p=E.get(e,(0,-1))
  if k==1:return None
  if k==2:
   a=next(z for z in P[p] if z!=e); row,x=divmod(a,W+1); return ((x-(d==3))%W,(row//2-(d==0))%H)
  dx,dy=lr.base.STEP[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 adj={(x,y):[t for d in range(4) if (t:=dest((x,y),d)) is not None] for y in range(H) for x in range(W)}
 rev=defaultdict(list)
 for a,ns in adj.items():
  for b in ns:rev[b].append(a)
 cache={}
 def distances(c):
  if c not in cache:
   ds={c:0}; todo=deque([c])
   while todo:
    a=todo.popleft()
    for b in rev[a]:
     if b not in ds:ds[b]=ds[a]+1;todo.append(b)
   cache[c]=ds
  return cache[c]
 def view(i):
  h=B[i][0];occ={p:(j,k) for j,b in B.items() for k,p in enumerate(b)};rows=[];ids={}
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    p=((h[0]+dx)%W,(h[1]+dy)%H);v=occ.get(p);ch='*' if p in pearls else '.'
    if v:
     j,k=v;ids[j]=dict(team=T[j],length=len(B[j]),head=B[j][0],body=list(B[j]));ch=('Q' if j==i else 'A' if T[j]==0 else 'E') if k==0 else ('q' if j==i else 'a' if T[j]==0 else 'e')
    mask=''.join('NESW'[d] for d in range(4) if E.get(lr.edge_id(W,H,*p,d),(0,-1))[0]==1)
    ports=''.join('NESW'[d] for d in range(4) if E.get(lr.edge_id(W,H,*p,d),(0,-1))[0]==2)
    row.append([ch,mask,ports])
   rows.append(row)
  return dict(center=h,cells=rows,visible=ids)
 rnd=-1;actor=None;cur=None;turns=[];queenturns=[];pearls=set();near=[];splits=[];deathframes=[]
 def close():
  if cur is not None:
   cur['end']=dict(length=len(B.get(actor,())),head=B[actor][0] if actor in B else None)
   turns.append(cur)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:close();cur=None;rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);cur=dict(r=rnd,id=actor,team=T[actor],L=len(B[actor]),head=B[actor][0],path=[],eats=0)
   if actor==q['us']:
    cur['view']=view(actor);cur['allheads']={j:[T[j],len(b),b[0]] for j,b in B.items()};queenturns.append(cur)
   if q['us'] not in B and q['them'] in B:
    ds=distances(B[q['them']][0]);friends=[(ds.get(b[0],9999),j,b[0]) for j,b in B.items() if T[j]==0]
    if friends:
     n=min(friends)
     near.append([rnd,*n,B[q['them']][0]])
  elif k==4:
   a=p.pointer(0);cur['act']=a.u16(0) if a else None;cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==3:
   c=lr.replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.discard(c);cur['eats']+=1
  elif k==9:
   i=p.i32(0);h=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=B[i]
   if h!=b[0]:b.appendleft(h);cur['path'].append(h)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   i,ch=p.i32(0),p.i32(4);sp=dict(r=rnd,id=i,child=ch,before=len(B[i]))
   for z,j in enumerate((i,ch)):B[j]=deque(lr.replay.point(c) for c in p.pointer(z));T[j]=p.u16(8)
   sp.update(after=len(B[i]),childlen=len(B[ch]));splits.append(sp)
  elif k==11:
   i=p.i32(0)
   if i==q['us'] or (T[i]==0 and len(B[i])>=8):deathframes.append(dict(r=rnd,id=i,actor=actor,view=view(i),turn=cur.copy()))
   B.pop(i)
 close()
 final={i:[T[i],len(b),b[0]] for i,b in B.items()}
 out=dict(W=W,H=H,queen_turns=queenturns,turns=turns,near=near,splits=splits,deathframes=deathframes,final=final)
 (O/f'{gid}-trace.json').write_text(json.dumps(out))
 snaps=G['snapshots']; last_not_loss=max(int(r) for r,v in snaps.items() if (v['us']['queen_length'],v['us']['longest'],v['us']['total']) >= (v['them']['queen_length'],v['them']['longest'],v['them']['total']))
 print(gid,'last not loss',last_not_loss,'lastqueen',json.dumps(queenturns[-3:]),'nearfirst',next((n for n in near if n[1]<=5),None),'nearmin',min(near,key=lambda n:n[1]) if near else None,'final',final,flush=True)
 print('LONGDEATHS',[(d['round'],d['id'],d['length'],d['cause'],d['actor']) for d in G['deaths'] if d['side']=='us' and d['length']>=8],flush=True)
