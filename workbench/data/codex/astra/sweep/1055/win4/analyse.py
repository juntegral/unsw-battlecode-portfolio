import sys
sys.dont_write_bytecode = True
import json
import ast
from pathlib import Path
from collections import deque, Counter

sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/local', 'data/analysis/ladder/dossier/work']
import ladder_replay as lr
import scoreboard as sb
geo_source = Path('data/analysis/ladder/dossier/work/tq2_scan.py')
geo_tree = ast.parse(geo_source.read_text())
geo_tree.body = [n for n in geo_tree.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'main')]
geo_env = {'__name__': 'imported_tq2_scan'}
exec(compile(geo_tree, str(geo_source), 'exec'), geo_env)
Geo = geo_env['Geo']

OUT = Path(__file__).resolve().parent
JOBS = [
 ('data/online/smoke/one13-c1-old',1506224),
 ('data/online/smoke/one13-c2-old',1510783),
 ('data/online/smoke/one13-c2-old',1510792),
 ('data/online/smoke/one13-c2-old',1510797),
 *[('data/online/live-one1/b1508916',i) for i in range(1508917,1508922)],
 ('data/online/live-one1/b1510461',1510461),
 ('data/online/live-one1/b1510461',1510462),
 ('data/online/live-one1/b1512747',1512748),
]

def analyse(folder, gid):
 path = Path(folder)/f'M{gid}.replay'
 meta = json.loads(path.with_name(f'game-{gid}.json').read_text())
 msg = sb.load_replay(path)
 root = msg.root()
 old = lr.replay.load
 lr.replay.load = lambda _: msg
 try:
  base = lr.scan(path, meta, folder, set())
 finally:
  lr.replay.load = old
 own = 0 if meta['teamAId']==1119 else 1
 assert root.text(own+1)=='21377', (gid, root.text(own+1))
 assert base['winner']=='AB'[own]
 w,h = map(int,root.text(0).splitlines()[0].split()[1:3])
 bodies,teams,raw = {},{},[]
 for line in root.text(0).splitlines():
  p = line.split()
  if p and p[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque(int(p[4+2*k])*w+int(p[3+2*k]) for k in range(int(p[2])))
   teams[i]=int(p[1])
  elif p and p[0]=='EDGE': raw.append(tuple(map(int,p[1:4])))
 geo=Geo(w,h,raw)
 queens=[base['queens'][s] for s in ('us','them')]
 def ours(i): return teams[i]==own
 def tile(p):
  x,y=lr.replay.point(p);return y*w+x
 def man(a,b):
  dx,dy=abs(a%w-b%w),abs(a//w-b//w)
  return min(dx,w-dx)+min(dy,h-dy)
 def view(a,b):
  dx,dy=abs(a%w-b%w),abs(a//w-b//w)
  return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
 def simple_reach(src, target, occ, limit):
  seen={src};q=deque([(src,0)])
  while q:
   c,d=q.popleft()
   if d==limit:continue
   for n in geo.nxt[c]:
    if n<0:continue
    if n==target:return d+1
    if n not in seen and n not in occ:
     seen.add(n);q.append((n,d+1))
  return None
 rnd,actor,turn=-1,None,None
 present={};turns=[];logs=[];pings=[];ec=Counter();splits=[]
 def close():
  nonlocal turn
  if turn is None:return
  i=turn['id'];survive=i in bodies
  turn['end_length']=len(bodies.get(i,()))
  turn['end']=bodies[i][0] if survive else None
  turn['steps']=len(turn['path'])
  if ours(i) and i==queens[0] and survive:
   qh=bodies[i][0]
   turn['one_step_ram']=[z for z,b in bodies.items() if not ours(z) and qh in geo.nxt[b[0]]]
   turn['mate_head_dist_end']=min((man(qh,b[0]) for z,b in bodies.items() if ours(z) and z!=i),default=None)
  turns.append(turn);turn=None
 for eidx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);ec[k]+=1;p=ev.pointer(0)
  if k==0:
   close();rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0)
   b=bodies[actor];hd=b[0]
   occ={c for bb in bodies.values() for c in bb}
   safe_pearl=[];adj_pearl=[];portal=[]
   for d,n in enumerate(geo.nxt[hd]):
    if n<0:continue
    if geo.por[hd][d]: portal.append([d,n])
    if n in present and n not in occ:
     adj_pearl.append(n)
     if not any(simple_reach(bb[0],n,occ,(len(bb)+3)//4+1) for z,bb in bodies.items() if ours(z)!=ours(actor)):
      safe_pearl.append(n)
   turn=dict(round=rnd,event=eidx,id=actor,ours=ours(actor),queen=actor==queens[0],length=len(b),head=hd,
    units=sum(ours(z)==ours(actor) for z in bodies),mate_dist=min((man(hd,bb[0]) for z,bb in bodies.items() if z!=actor and ours(z)==ours(actor)),default=None),
    eq_length=len(bodies.get(queens[1],())),path=[],eaten=[],action=None,dirs=[],adj_pearl=adj_pearl,safe_pearl=safe_pearl,portal=portal,
    visible_enemies=[dict(id=z,head=bb[0],length=len(bb)) for z,bb in bodies.items() if ours(z)!=ours(actor) and view(hd,bb[0])],
    enemy_dist=min((geo.ball(hd).get(bb[0],99) for z,bb in bodies.items() if ours(z)!=ours(actor)),default=99))
   if ours(actor) and actor==queens[0]:
    turn['body']=list(b)
    turn['open']=[n for n in geo.nxt[hd] if n>=0 and n not in occ]
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):present[c]=rnd
   else:
    present.pop(c);turn['eaten'].append(c)
  elif k==4:
   a=p.pointer(0)
   turn['action']=a.u16(0) if a else None
   turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
   if a and a.u16(0)==1:turn['child_size']=a.i32(4)
   turn['tle']=p.bit(32)
  elif k==6: logs.append(dict(round=rnd,id=p.i32(0),text=p.text(0),ours=ours(p.i32(0))))
  elif k==9:
   i=p.i32(0);hd,tail=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:
    if actor==i:turn['path'].append([b[0],hd])
    b.appendleft(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   parent,child=p.i32(0),p.i32(4)
   rec=dict(round=rnd,id=parent,child=child,length=len(bodies[parent]),ours=ours(parent),queen=parent==queens[0])
   for z,i in enumerate((parent,child)):
    bodies[i]=deque(tile(q) for q in p.pointer(z));teams[i]=p.u16(8)
   rec.update(parent_length=len(bodies[parent]),child_length=len(bodies[child]),head=bodies[parent][0],child_head=bodies[child][0])
   splits.append(rec)
  elif k==11:
   i=p.i32(0)
   if turn is not None and actor==i:turn['death_reason']=p.u16(4)
   bodies.pop(i)
  elif k==12:
   pings.append(dict(round=rnd,id=p.i32(0),ours=ours(p.i32(0)),message=p.u64(16),direction=p.u16(4),
    hit=p.i32(12) if p.u16(6) else None,origin=lr.replay.point(p.pointer(0)),end=lr.replay.point(p.pointer(1))))
 close()
 def score(s):return (s['alive']>0,s['queen_length'],s['longest'],s['total'])
 snaps=base['snapshots']
 bad=[r for r,s in snaps.items() if score(s['us'])<=score(s['them'])]
 ahead=min(r for r in snaps if r>max(bad,default=-1))
 final=base['final']
 for z,t in enumerate('AB'):
  ls=[len(b) for i,b in bodies.items() if teams[i]==z];st=root.pointer(4).pointer(z)
  assert (len(ls),max(ls,default=0),sum(ls))==(st.i32(0),st.i32(4),st.i32(8))
 qdeath=[d for d in base['deaths'] if d['id']==queens[0]]
 eqdeath=[d for d in base['deaths'] if d['id']==queens[1]]
 qturns=[t for t in turns if t['ours'] and t['queen']]
 qvuln=[t for t in qturns if t.get('one_step_ram')]
 queen_deficits=[dict(round=r,us=s['us']['queen_length'],them=s['them']['queen_length']) for r,s in snaps.items() if s['us']['queen_length'] and s['them']['queen_length'] and s['us']['queen_length']<s['them']['queen_length']]
 collapses=[dict(round=r,previous=r0,before=snaps[r0]['us']['alive'],after=s['us']['alive']) for r,s in snaps.items() for r0 in [max(0,r-10)] if r0 in snaps and snaps[r0]['us']['alive']>=4 and 2*s['us']['alive']<=snaps[r0]['us']['alive']]
 return dict(gid=gid,map=meta['mapName'],side='AB'[own],replay=str(path),bot=21377,last_round=base['last_round'],winner=base['winner'],end_reason=base['end_reason'],
 final=final,ahead=ahead,ahead_state=snaps[ahead],qdeath=qdeath,eqdeath=eqdeath,queen_deficits=queen_deficits,
 q_one_step=qvuln,count_halved=collapses,events=dict(ec),logs=logs,turns=turns,pings=pings,splits=splits,
 snapshots=snaps,deaths=base['deaths'],eats=base['eats'],q_eats=base['q_eats'],anomalies=base['anomalies'])

if __name__=='__main__':
 for folder,gid in JOBS:
  result=analyse(folder,gid)
  (OUT/f'{gid}.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
  print(json.dumps({k:result[k] for k in ('gid','map','side','last_round','final','ahead','qdeath','eqdeath','events','eats')},ensure_ascii=False),flush=True)
