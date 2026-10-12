import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter,defaultdict,deque
sys.path.insert(0,'data/analysis/ladder/dossier/work')
from o1_scan import replay,edge_id,canonical_edges,STEP
OUT=Path(__file__).resolve().parent
LABELS=('one8-c2','one10-c1','one8-p1')

def scan(label,mp):
 j=json.loads(mp.read_text());root=replay.load(mp.with_name('M%d.replay'%j['id'])).root()
 lines=root.text(0).splitlines();W,H=map(int,lines[0].split()[1:3]);own=int(j['teamAId']!=1119)
 bodies={};teams={};raw=[]
 for line in lines:
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 edges=canonical_edges(W,H,raw);ports=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:ports[p].append(e)
 def side(i):return int(teams[i]!=own)
 queens=[min(i for i in bodies if side(i)==s) for s in (0,1)]
 starters=set(bodies)
 def dest(c,d):
  e=edge_id(W,H,*c,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   pair=[v for v in ports[p] if v!=e];assert len(pair)==1
   row,x=divmod(pair[0],W+1);y=row//2
   return ((x-(d==3))%W,(y-(d==0))%H)
  dx,dy=STEP[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 adj={ (x,y):list(set(v for d in range(4) if (v:=dest((x,y),d)) is not None)) for x in range(W) for y in range(H)}
 def bfs(src,limit=99999,blocked=frozenset()):
  ds={p:0 for p in src};queue=deque(ds)
  while queue:
   c=queue.popleft()
   if ds[c]>=limit:continue
   for n in adj[c]:
    if n not in ds and n not in blocked:ds[n]=ds[c]+1;queue.append(n)
  return ds
 def gap(a,b):
  dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,W-dx)+min(dy,H-dy)
 def visible(a,b):return min(abs(a[0]-b[0]),W-abs(a[0]-b[0]))<=3 and min(abs(a[1]-b[1]),H-abs(a[1]-b[1]))<=3
 pearls={};expected=deque();rnd=-1;actor=None;cur=None;snaps={};turns=[];deaths=[];splits=[];eats=[];lastturn={};initial=[sum(side(i)==s for i in bodies) for s in (0,1)];initialL=[sum(len(b) for i,b in bodies.items() if side(i)==s) for s in (0,1)]
 def snapshot():
  ds=[bfs([b[0] for i,b in bodies.items() if side(i)==s]) for s in (0,1)]
  bearing=list(pearls);share=[0,0];tie=0;unreach=0
  for c in bearing:
   a,b=ds[0].get(c,99999),ds[1].get(c,99999)
   if min(a,b)==99999:unreach+=1
   elif a==b:tie+=1
   else:share[int(b<a)]+=1
  return {'heads':[sum(side(i)==s for i in bodies) for s in (0,1)],'length':[sum(len(b) for i,b in bodies.items() if side(i)==s) for s in (0,1)],'near3':[sum(side(i)==s and any(c in pearls for c in bfs([b[0]],3)) for i,b in bodies.items()) for s in (0,1)],'bearing':len(bearing),'nearest':share,'tied':tie,'unreachable':unreach}
 def close():
  nonlocal cur
  if cur is None:return
  i=cur['id'];cur['end']=list(bodies[i][0]) if i in bodies else None;cur['endL']=len(bodies.get(i,()))
  # Team mass conservation gives sprint cost even when this actor dies.
  cur['paid']=cur['mass0']+sum(cur['eats'].values())-cur['deadmass']-sum(len(b) for z,b in bodies.items() if side(z)==cur['side'])
  assert cur['paid']>=0,(j['id'],rnd,cur)
  del cur['mass0'];del cur['deadmass']
  if cur['L']>=4 and not cur['split']:
   # Observable sufficient conditions only: hidden planner gates remain unresolved.
   if cur['queen'] and cur['L']==4 and cur['heads']>=(6 if label=='one10-c1' else 2):cur['gate']='QS_KEEP_LEN eligible (ring/early-return precedence unknown)'
   elif cur['tail_spans']:cur['gate']='child_spans_portal geometry (precedence unknown)'
   elif cur['tail_exits']==0:cur['gate']='child_has_exit geometry (memory/precedence unknown)'
   elif cur['tail_room']<4:cur['gate']='CHILD_MIN_ROOM geometry (memory/precedence unknown)'
   elif cur['tail_portal']:cur['gate']='portal-adjacent (exception/precedence unknown)'
   else:cur['gate']='unresolved internal gate or earlier action'
  else:cur['gate']='split' if cur['split'] else 'L<4'
  turns.append(cur);lastturn[i]=cur;cur=None
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close()
   if rnd>=0:snaps[rnd]=snapshot() if rnd%10==0 or rnd==99 else {'heads':[sum(side(i)==s for i in bodies) for s in (0,1)],'length':[sum(len(b) for i,b in bodies.items() if side(i)==s) for s in (0,1)]}
   rnd=p.i32(0);actor=None
   if rnd>100:break
  elif k==1:
   close();actor=p.i32(0);b=bodies[actor];h=b[0];tail=b[-1];s=side(actor);occ={c for bb in bodies.values() for c in bb}
   cur={'r':rnd,'id':actor,'side':s,'L':len(b),'h':list(h),'tail':list(tail),'queen':actor==queens[s],'starter':actor in starters,'heads':sum(side(z)==s for z in bodies),'eats':{'natural':0,'corpse':0},'split':0,'dirs':[],'moves':[],'logs':[],'dead':False,'mass0':sum(len(bb) for z,bb in bodies.items() if side(z)==s),'deadmass':0,'free_exits':sum(c not in occ for c in adj[h]),'near_heads':[[z,side(z),len(bb),list(bb[0])] for z,bb in bodies.items() if z!=actor and visible(h,bb[0])],'tail_exits':sum(c not in occ for c in adj[tail]),'tail_room':min(20,len(bfs([tail],8,occ-{tail}))-1),'tail_spans':len(b)>=2 and gap(b[-1],b[-2])!=1,'tail_portal':any(edges.get(edge_id(W,H,*tail,d),(0,-1))[0]==2 for d in range(4)),'tail_visible':visible(h,tail)}
   if rnd<=20 or len(b)>=4:
    dist=bfs([h],10,occ-{h});cur['pearls']=[[list(c),o,dist.get(c,99)] for c,o in pearls.items() if visible(h,c)]
    cur['body']=list(b)
  elif k==4 and cur is not None:
   a=p.pointer(0);cur['action']=a.u16(0) if a else None;cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else [];cur['requested_child']=a.i32(4) if a and a.u16(0)==1 else None
  elif k==6 and cur is not None:cur['logs'].append(p.text(0))
  elif k==3:
   c=replay.point(p.pointer(0))
   if p.u32(0):
    assert c not in pearls
    if expected:assert expected.popleft()==c;pearls[c]='corpse'
    else:assert actor is None;pearls[c]='natural'
   else:
    o=pearls.pop(c);cur['eats'][o]+=1;eats.append({'r':rnd,'side':side(actor),'id':actor,'origin':o,'xy':c})
  elif k==9:
   i=p.i32(0);h,t=replay.point(p.pointer(0)),replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=h:
    b.appendleft(h)
    if cur and i==actor:cur['moves'].append(list(h))
   while len(b)>1 and b[-1]!=t:b.pop()
   assert b[-1]==t
  elif k==10:
   parent,child=p.i32(0),p.i32(4);L=len(bodies[parent]);cur['split']=1
   for z,i in enumerate((parent,child)):bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
   splits.append({'r':rnd,'side':side(parent),'id':parent,'child':child,'L':L,'parts':[len(bodies[parent]),len(bodies[child])]})
  elif k==11:
   i=p.i32(0);reason=p.u16(4);b=bodies[i];s=side(i);h=b[0];used=len(cur['moves']) if cur else 0
   target=dest(h,cur['dirs'][used]) if i==actor and cur and used<len(cur['dirs']) else None
   hit=[z for z,bb in bodies.items() if z!=i and target in bb] if target else []
   cause={0:'wall',1:'own body',2:'body',3:'rammed' if i!=actor else 'rams',4:'other'}[reason]
   if reason==4 and cur.get('action')==1 and cur.get('requested_child')==1:cause='illegal split'
   if reason==2 and hit:cause='mate body' if side(hit[0])==s else 'foe body'
   if reason==3 and i!=actor and side(actor)==s:cause='mate head'
   if reason==3 and i==actor and deaths and deaths[-1]['actor']==i and deaths[-1]['side']==s:cause='mate head'
   d={'r':rnd,'id':i,'side':s,'cause':cause,'L':len(b),'h':list(h),'body':list(b),'actor':actor,'attackerL':cur['L'] if cur else None,'target':target,'hit':hit,'free_exits':sum(c not in {c for bb in bodies.values() for c in bb} for c in adj[h]),'lastturn':lastturn.get(i) if i!=actor else dict(cur)}
   deaths.append(d)
   if cur and s==cur['side']:cur['deadmass']+=len(b)
   if i==actor:cur['dead']=True
   assert not expected;expected.extend(c for n,c in enumerate(b) if n%2==0);del bodies[i]
 else:
  close();snaps[rnd]=snapshot()
 assert not expected
 for r,snap in snaps.items():
  for s in (0,1):
   assert snap['heads'][s]==initial[s]+sum(x['side']==s and x['r']<=r for x in splits)-sum(x['side']==s and x['r']<=r for x in deaths)
   assert snap['length'][s]==initialL[s]+sum(x['side']==s and x['r']<=r for x in eats)-sum(x['L'] for x in deaths if x['side']==s and x['r']<=r)-sum(x['paid'] for x in turns if x['side']==s and x['r']<=r)
 return {'gid':j['id'],'label':label,'map':j['mapName'],'bots':[root.text(1),root.text(2)],'ours':own,'initial':initial,'initialL':initialL,'size':[W,H],'snaps':snaps,'turns':turns,'eats':eats,'splits':splits,'deaths':deaths}

if __name__=='__main__':
 seen=set()
 for label in LABELS:
  for mp in sorted(Path('data/online/smoke',label+'-old').glob('game-*.json')):
   gid=json.loads(mp.read_text())['id'];assert gid not in seen;seen.add(gid)
   out=OUT/f'{gid}.json'
   if not out.exists():
    row=scan(label,mp);out.write_text(json.dumps(row,separators=(',',':')))
   print(label,gid,flush=True)
 print('done',len(seen))
