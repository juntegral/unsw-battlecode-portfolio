import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,'tools')
import ladder_replay as lr
OUT=Path('data/codex/astra/sweep/0630/win1')
JOBS=[(1496853,'data/online/smoke/one11-c1-old'),(1496854,'data/online/smoke/one11-c1-old'),(1496855,'data/online/smoke/one11-c1-old'),(1496856,'data/online/smoke/one11-c1-old'),(1497631,'data/online/live-one1/b1497630'),(1497632,'data/online/live-one1/b1497630'),(1497634,'data/online/live-one1/b1497630'),(1497388,'data/online/live-one1/b1497386')]
STEP=((0,-1),(1,0),(0,1),(-1,0))
def scan(gid,folder):
 path=Path(folder)/f'M{gid}.replay';meta=json.loads((Path(folder)/f'game-{gid}.json').read_text())
 base=lr.scan(path,meta,folder,set());root=lr.replay.load(path).root();text=root.text(0)
 W,H=map(int,text.splitlines()[0].split()[1:3]);ours=base['ours'];queens=base['queens'];bodies={};teams={};raw=[]
 for line in text.splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]='AB'[int(q[1])]
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 edges=lr.canonical_edges(W,H,raw);portals={}
 for e,(k,p) in edges.items():
  if k==2:portals.setdefault(p,[]).append(e)
 def side(i):return 'us' if teams[i]==ours else 'them'
 def man(a,b):return min(abs(a[0]-b[0]),W-abs(a[0]-b[0]))+min(abs(a[1]-b[1]),H-abs(a[1]-b[1]))
 def visible(a,b):return min(abs(a[0]-b[0]),W-abs(a[0]-b[0]))<=3 and min(abs(a[1]-b[1]),H-abs(a[1]-b[1]))<=3
 def dest(c,d):
  e=lr.edge_id(W,H,*c,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   other=next(z for z in portals[p] if z!=e);r,x=divmod(other,W+1);return ((x-(d==3))%W,(r//2-(d==0))%H)
  dx,dy=STEP[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 def ball(c,n):
  seen={c:0};qu=deque([c])
  while qu:
   c=qu.popleft()
   if seen[c]==n:continue
   for d in range(4):
    z=dest(c,d)
    if z is not None and z not in seen:seen[z]=seen[c]+1;qu.append(z)
  return seen
 pearls={};rnd=0;actor=None;turn=None;turns=[];logs=[];qthreat=[];splits=[];cuts=[]
 def finish():
  nonlocal turn
  if turn is not None:
   turn['end_body']=list(bodies.get(turn['id'],()))
   if queens['us'] in bodies:
    occupied={c for b in bodies.values() for c in b}
    turn['queen_exits_after']=[dest(bodies[queens['us']][0],d) for d in range(4) if dest(bodies[queens['us']][0],d) is not None and dest(bodies[queens['us']][0],d) not in occupied]
   turns.append(turn);turn=None
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:finish();rnd=p.i32(0);actor=None
  elif k==1:
   finish();actor=p.i32(0);body=list(bodies[actor]);head=body[0];occ={c:i for i,b in bodies.items() for c in b}
   adj=[dest(head,d) for d in range(4)];free=[c for c in adj if c is not None and c not in occ]
   turn=dict(round=rnd,event=idx,id=actor,side=side(actor),body=body,length=len(body),head=head,count=sum(side(i)==side(actor) for i in bodies),free=free,adj=adj,pearl_adj=[c for c in free if c in pearls],eats=[],steps=[],deaths=[],dirs=[],split=None,qbody=list(bodies.get(queens['us'],())),eqbody=list(bodies.get(queens['them'],())),mate_heads=[(i,b[0]) for i,b in bodies.items() if side(i)==side(actor) and i!=actor and visible(head,b[0])],enemy_heads=[(i,b[0],len(b)) for i,b in bodies.items() if side(i)!=side(actor) and visible(head,b[0])])
   turn['visible_enemy_parts']=[dict(id=i,head=b[0],actual=len(b),visible=sum(visible(head,c) for c in b),edge=any(visible(head,c) and (min(abs(head[0]-c[0]),W-abs(head[0]-c[0]))==3 or min(abs(head[1]-c[1]),H-abs(head[1]-c[1]))==3) for c in b)) for i,b in bodies.items() if side(i)!=side(actor) and visible(head,b[0])]
   turn['head_portal_dirs']=[d for d in range(4) if edges.get(lr.edge_id(W,H,*head,d),(0,-1))[0]==2]
   turn['tail_portal']=any(edges.get(lr.edge_id(W,H,*body[-1],d),(0,-1))[0]==2 for d in range(4))
   if queens['us'] in bodies:
    turn['queen_exits_before']=[dest(bodies[queens['us']][0],d) for d in range(4) if dest(bodies[queens['us']][0],d) is not None and dest(bodies[queens['us']][0],d) not in occ]
   if side(actor)=='them' and queens['us'] in bodies:
    qh=bodies[queens['us']][0]
    if qh in adj:
     qthreat.append(dict(round=rnd,event=idx,enemy=actor,enemy_length=len(body),head=head,queen_head=qh,queen_length=len(bodies[queens['us']]),enemy_queen_length=len(bodies.get(queens['them'],())),our_count=sum(side(i)=='us' for i in bodies)))
  elif k==4:
   a=p.pointer(0);turn['action']=a.u16(0) if a else None
   turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k in (5,6):logs.append(dict(round=rnd,id=actor,kind=k,text=p.text(0)))
  elif k==3:
   c=lr.replay.point(p.pointer(0))
   if p.u32(0):pearls[c]=actor is not None
   else:
    origin=pearls.pop(c);turn['eats'].append(dict(cell=c,drop=origin))
  elif k==9:
   i=p.i32(0);hd=lr.replay.point(p.pointer(0));tl=lr.replay.point(p.pointer(1));b=bodies[i];old=list(b)
   if b[0]!=hd:b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   if i==actor and old[0]!=hd:turn['steps'].append(hd)
   if i!=actor and len(b)<len(old):cuts.append(dict(round=rnd,actor=actor,target=i,before=len(old),after=len(b)))
  elif k==10:
   par,child=p.i32(0),p.i32(4);turn['split']=child
   sp=dict(round=rnd,parent=par,child=child,side=side(par),count=turn['count'],before=turn['length'])
   for z,i in enumerate((par,child)):
    bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]='AB'[p.u16(8)]
   sp['after']=len(bodies[par]);sp['child_head']=bodies[child][0];sp['parent_head']=bodies[par][0];sp['portal_at_head']=any(edges.get(lr.edge_id(W,H,*bodies[par][0],d),(0,-1))[0]==2 for d in range(4));splits.append(sp)
   sp['tail_portal']=turn['tail_portal']
  elif k==11:
   i=p.i32(0);turn['deaths'].append(i);bodies.pop(i)
 finish()
 snapshots=base['snapshots']
 def key(st):return (int(st['alive']>0),st['queen_length'],st['longest'],st['total'])
 permanent=1+max((int(r) for r,st in snapshots.items() if key(st['us'])<=key(st['them'])),default=-1)
 qdeaths={s:next((d for d in base['deaths'] if d['id']==queens[s]),None) for s in ('us','them')}
 death_index={d['id']:d for d in base['deaths']}
 rams=[]
 for t in turns:
  if t['side']!='us':continue
  enemy_deaths=[death_index[i] for i in t['deaths'] if i in death_index and death_index[i]['side']=='them' and death_index[i]['reason']==3]
  for d in enemy_deaths:
   ram=dict(round=t['round'],actor=t['id'],length=t['length'],target=d['id'],target_length=d['length'],steps=len(t['steps'])+1,queen_target=d['id']==queens['them'],queen_dist=None,head=t['head'],victim_head=d['body'][0])
   if t['qbody']:ram['queen_dist']=ball(t['qbody'][0],3).get(d['body'][0],99)
   rams.append(ram)
 qturns=[t for t in turns if t['id']==queens['us']]
 ownturns=[t for t in turns if t['side']=='us']
 passed=[t for t in ownturns if t['pearl_adj'] and t['steps'] and t['steps'][0] not in t['pearl_adj'] and not t['deaths']]
 stopped=[t for t in ownturns if t['action']==2]
 herd=[t for t in qturns if t['count']>=12 and len(t['mate_heads'])<2 and t['mate_heads'] and t['steps'] and min(man(t['steps'][-1],c) for _,c in t['mate_heads'])<min(man(t['head'],c) for _,c in t['mate_heads']) and min(man(t['head'],c) for _,c in t['mate_heads'])>3]
 feed=[t for t in stopped if t['round']>400 and t['qbody'] and t['length'] in (2,3) and 2<=len(t['qbody'])<6 and man(t['head'],t['qbody'][0])<=3]
 bouts=[]
 for q in qthreat:
  t=next(t for t in turns if t['event']==q['event']);q['action']=t['dirs'];q['rammed']=queens['us'] in t['deaths'];q['end_head']=t['end_body'][0] if t['end_body'] else None
  bouts.append(q)
 out={k:base[k] for k in ('gid','map','ours','last_round','final','end_reason','eats','q_eats','q_splits','anomalies')}
 out.update(bot_ids={'us':root.text(1 if ours=='A' else 2),'them':root.text(2 if ours=='A' else 1)},permanent_lead=permanent,queen_deaths=qdeaths,snapshots=snapshots,rams=rams,queen_adjacent_enemy_turns=bouts,counts=dict(turns=len(ownturns),eat_first_compatible=sum(bool(t['steps']) and t['steps'][0] in t['pearl_adj'] for t in ownturns),passed_adjacent=len(passed),no_action=len(stopped),herd_compatible=len(herd),boot_feeding_compatible=len(feed),queen_threat_turns=len(bouts),queen_portals=sum(any(edges.get(lr.edge_id(W,H,*t['head'],d),(0,-1))[0]==2 for d in t['dirs'][:1]) for t in qturns),queen_turns_length3=sum(t['length']==3 for t in qturns),logs=len(logs)),examples={'passed':passed[:5],'herd':herd[:3],'feed':feed[:5],'stopped':stopped[:5]},splits=splits,cuts=cuts)
 out['queen_ids']=queens
 out['high_portal_ids']=sorted({pid for kind,pid in edges.values() if kind==2 and pid>=2*W*H})
 out['feed_drops']=[x for x in base['pearls'] if x['dragon'] in {t['id'] for t in feed}]
 out['queen_partial_enemy_turns']=[dict(round=t['round'],id=t['id'],enemies=t['visible_enemy_parts']) for t in qturns if any(e['edge'] and e['visible']<4 for e in t['visible_enemy_parts'])]
 (OUT/f'{gid}-turns.json').write_text(json.dumps(turns,separators=(',',':')))
 return out
allrows=[]
for gid,folder in JOBS:
 r=scan(gid,folder);allrows.append(r);print(gid,r['map'],r['final'],'lead',r['permanent_lead'],'qdeath',[(s,d['round'] if d else None,d['cause'] if d else None) for s,d in r['queen_deaths'].items()],r['counts'],flush=True)
(OUT/'measurements.json').write_text(json.dumps(allrows,ensure_ascii=False,separators=(',',':')))
