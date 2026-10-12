import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from collections import Counter,defaultdict,deque
from datetime import datetime
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parent/'evade'))
import analyze as a
sys.path.insert(0,str(a.ROOT.parent/'battlecode/work'))
import card_42_check as codec
LABELS=('one5-w1','one5-c1','one7-w1','one7-c1')

def analyze(path,meta,label):
 base=a.lr.scan(path,meta,label,set());root=a.lr.replay.load(path).root();g=a.Geo(root.text(0));W,H=g.w,g.h
 bodies={};teams={};occup={};own=0 if meta['teamAId']==1119 else 1
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies);bodies[i]=tuple((int(q[3+2*z]),int(q[4+2*z])) for z in range(int(q[2])));teams[i]=int(q[1])
   for c in bodies[i]:occup[c]=i
 known=defaultdict(set);lengths=defaultdict(dict);hist=[];last={};turn=None;r=-1;pearls=set();eats=defaultdict(list)
 windows={};edgesby={};pairs=defaultdict(set);attackstats={};actor=None;actor_event=None
 for e,(k,pid) in g.edges.items():
  if k==2:pairs[pid].add(e)
 key=codec.make_key(W,H,2 if own==0 else 1);streams={};decoded={}
 def window(h):
  if h not in windows:windows[h]={( (h[0]+dx)%W,(h[1]+dy)%H) for dx in range(-3,4) for dy in range(-3,4)}
  return windows[h]
 def viewedges(h):
  if h not in edgesby:edgesby[h]={a.lr.edge_id(W,H,*c,d) for c in window(h) for d in range(4)}
  return edgesby[h]
 def make_turn(idx,i):
  b=bodies[i];h=b[0];L=len(b);view=window(h);vis=Counter(occup[c] for c in view if c in occup)
  friends=[j for j in vis if teams[j]==own and j!=i and bodies[j][0] in view]
  enemies=[j for j in vis if teams[j]!=own and bodies[j][0] in view]
  memory=lengths[i]
  for j,n in vis.items():memory[j]=max(memory.get(j,0),n)
  seen=known[i];seen.update(viewedges(h))
  count=sum(t==own for j,t in teams.items() if j in bodies)
  t=dict(event=idx,id=i,round=r,L=L,head=h,heads=[len(friends)+1,len(enemies)],units=count,kind=None,dirs=[],ate=0,used=0,leader=None,
    enemies=[dict(id=j,head=bodies[j][0],length=len(bodies[j]),parts=vis[j],memory=memory[j]) for j in enemies],friend_ids=friends,
    queen_visible=base['queens']['us'] in friends,free_danger=[],free_reached=[],plus_danger=[],plus_reached=[],choices=[],endbody=None)
  if i<=1:return t
  # Leader exclusion can be proved false before the growth phase or while board_short suppresses it.
  aggressive=W*H<=1200
  feeding=r>400 or (r>350 and count>=56)
  t['leader_possible']=r>(300 if aggressive else 150) and not (not aggressive and not feeding and count<56 and L<10)
  if not t['leader_possible']:t['leader']=False
  if not enemies or L>8:return t
  blocked={c for c in view if c in occup}|set(b)
  def step(c,d):
   e=a.lr.edge_id(W,H,*c,d)
   if e in seen:
    k,pid=g.edges.get(e,(0,-1))
    if k==1:return None
    if k==2:return g.moves[c][d] if pairs[pid]<=seen else None
   dx,dy=a.STEP[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
  def bfs(origins,depth):
   dist={p:0 for p in origins};q=deque(origins)
   while q:
    c=q.popleft();nstep=dist[c]+1
    if nstep>depth:continue
    for d in range(4):
     n=step(c,d)
     if n is None or n in blocked or n in dist:continue
     dist[n]=nstep;q.append(n)
   return dist
  maxdepth=max((memory[j]+3)//4+1 for j in enemies)
  allies=bfs([bodies[j][0] for j in friends],maxdepth)
  reach={};plus={};danger=set();dangerplus=set()
  for j in enemies:
   free=(memory[j]+3)//4;ds=bfs([bodies[j][0]],free+1)
   reach[j]={c:d for c,d in ds.items() if 0<d<=free};plus[j]={c:d for c,d in ds.items() if 0<d<=free+(memory[j]>=3)}
   danger.update(c for c,d in reach[j].items() if allies.get(c,999999)>=d)
   dangerplus.update(c for c,d in plus[j].items() if allies.get(c,999999)>=d)
  reached=set().union(*(set(z) for z in reach.values()));reachedplus=set().union(*(set(z) for z in plus.values()))
  t['free_danger']=list(danger);t['free_reached']=list(reached);t['plus_danger']=list(dangerplus);t['plus_reached']=list(reachedplus)
  t['enemy_reach']={str(j):list(z) for j,z in reach.items()};t['enemy_plus']={str(j):list(z) for j,z in plus.items()}
  # One-step alternatives: true immediate legality, visible room/cycle certificate. Scores remain unobserved.
  other={c for j,bb in bodies.items() if j!=i for c in bb}
  for d in range(4):
   n=step(h,d)
   if n is None or n in blocked:continue
   if n!=g.moves[h][d] or n in other:continue
   nb=(n,)+b if n in pearls else (n,)+b[:-1]
   good=a.good_room(g,nb,other,view)
   t['choices'].append(dict(dir=d,dest=n,room=good,free=n in reached,danger=n in danger,plus=n in reachedplus,plusdanger=n in dangerplus,pearl=n in pearls))
  return t
 def finish():
  nonlocal turn
  if turn is None:return
  t=turn;i=t['id'];t['endbody']=bodies.get(i,());t['endpoint']=t['endbody'][0] if t['endbody'] else None
  # A successful intentional head-ram cannot subsequently be a passive victim, but matters to turn cohorts.
  p=t['head'];enemyheads={tuple(e['head']) for e in t['enemies']};t['attack_path']=False
  for d in t['dirs']:
   p=g.moves[p][d]
   if p is None:break
   if p in enemyheads:t['attack_path']=True
  t['stop']=t['kind']==0 and not t['dirs']
  t['eligible']=i>1 and t['L']<=4 and t['heads'][0]<=t['heads'][1] and t['leader'] is False and t['kind']==0 and bool(t['dirs']) and not t['attack_path']
  t['possible_eligible']=i>1 and t['L']<=4 and t['heads'][0]<=t['heads'][1] and t['leader'] is not True and t['kind']==0 and bool(t['dirs']) and not t['attack_path']
  t['free_window']=t['eligible'] and any(c['danger'] for c in t['choices']) and any(c['room'] and not c['free'] for c in t['choices'])
  t['plus_window']=t['eligible'] and any(c['plusdanger'] for c in t['choices']) and any(c['room'] and not c['plus'] for c in t['choices'])
  t['chosen_free']=t['endpoint'] in t['free_reached'];t['chosen_danger']=t['endpoint'] in t['free_danger'];t['chosen_plus']=t['endpoint'] in t['plus_reached']
  t['change_compatible']=t['free_window'] and t['endpoint'] is not None and not t['chosen_free']
  hist.append(t);last[i]=t;turn=None
 events=list(root.pointer(3))
 for idx,ev in enumerate(events):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:finish();r=p.i32(0)
  elif k==1:
   finish();i=p.i32(0);actor=i;actor_event=idx;attackstats[idx]=dict(length=len(bodies[i]),used=0)
   if teams[i]==own:turn=make_turn(idx,i)
  elif k==4:
   if turn is not None:
    act=p.pointer(0);turn['kind']=act.u16(0) if act else None
    turn['dirs']=list(act.pointer(0)) if act and act.u16(0)==0 and act.pointer(0) is not None else []
  elif k==3:
   c=a.lr.replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:
    pearls.remove(c)
    if turn is not None:turn['ate']+=1;eats[turn['id']].append((r,idx))
  elif k==9:
   i=p.i32(0);hd=a.lr.replay.point(p.pointer(0));tl=a.lr.replay.point(p.pointer(1));old=bodies[i];bb=deque(old)
   if hd!=bb[0]:
    if i==actor:attackstats[actor_event]['used']+=1
    bb.appendleft(hd)
    if turn is not None and turn['id']==i:turn['used']+=1
   while len(bb)>1 and bb[-1]!=tl:bb.pop()
   assert bb[-1]==tl
   for c in old:occup.pop(c,None)
   bodies[i]=tuple(bb)
   for c in bb:occup[c]=i
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):
    for c in bodies.get(i,()):occup.pop(c,None)
    bodies[i]=tuple(a.lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
    for c in bodies[i]:occup[c]=i
  elif k==11:
   i=p.i32(0)
   for c in bodies.pop(i):occup.pop(c,None)
  elif k==12 and turn is not None:
   if p.i32(0)!=turn['id']:continue
   wire=p.u64(16)
   if wire not in decoded:decoded[wire]=codec.unseal(key,wire,streams)
   plain=decoded[wire]
   if plain is not None and plain>>63==0:
    leader_id=(plain&0xFFFF)&0x7FFF
    if turn.get('leader_possible'):turn['leader']=leader_id==turn['id']
 finish()
 deathby={d['id']:d for d in base['deaths']};by_event={t['event']:t for t in hist}
 for t in hist:
  d=deathby.get(t['id']);t['dead5']=d is not None and d['event']>t['event'] and d['round']<=t['round']+5
  t['censored5']=not t['dead5'] and base['last_round']<t['round']+5
  t['ate5']=sum(t['round']<rr<=t['round']+5 for rr,ix in eats[t['id']])
  t['outcome']='dead' if t['dead5'] else 'censored' if t['censored5'] else 'alive_ate' if t['ate5'] else 'alive_no_food'
 audit=[];history=defaultdict(list)
 for t in hist:history[t['id']].append(t)
 deaths={d['death']:d for d in base['deaths']}
 for c in base['collisions']:
  if not c['cross_team']:continue
  v=deaths[c['deaths'][0]];att=deaths[c['deaths'][1]]
  if v['side']!='us' or v['id']==base['queens']['us']:continue
  ts=[t for t in history[v['id']] if t['event']<v['event']];t=ts[-1] if ts else None
  rec=dict(gid=meta['id'],label=label,map=meta['mapName'],round=c['round'],victim=v['id'],attacker=att['id'],death=v['death'],impact_length=v['length'],turn=t)
  # Attacking steps = successful updates before ram + the fatal head collision step.
  rec['attack_steps']=attackstats[c['turn_start']]['used']+1
  rec['attacker_start_length']=attackstats[c['turn_start']]['length']
  rec['paid_attack']=rec['attack_steps']>(rec['attacker_start_length']+3)//4
  if t:
   actual=next((e for e in t['enemies'] if e['id']==att['id']),None);rec['visible_attacker']=actual is not None
   rec['attacker_memory']=actual['memory'] if actual else None
   rec['attacker_free_reaches']=t['endpoint'] in t.get('enemy_reach',{}).get(str(att['id']),[])
   rec['attacker_plus_reaches']=t['endpoint'] in t.get('enemy_plus',{}).get(str(att['id']),[])
   if t['L']>4:reason='length>4'
   elif t['leader'] is True:reason='leader'
   elif t['kind']==1:reason='exempt_split'
   elif t['kind']!=0 or not t['dirs']:reason='exempt_stop'
   elif t['attack_path']:reason='exempt_attack_path'
   elif t['heads'][0]>t['heads'][1]:reason='ahead_in_heads'
   elif t['leader'] is None:reason='leader_unresolved'
   elif not actual:reason='attacker_not_visible'
   elif not rec['attacker_free_reaches']:reason='attacker_outside_free_reach'
   elif not t['chosen_danger']:reason='ally_closer_exception'
   elif not any(x['room'] and not x['free'] for x in t['choices']):reason='no_certified_safe_alternative'
   else:reason='would_veto_unresolved_scores_or_override'
  else:reason='no_prior_turn'
  rec['class']=reason;audit.append(rec)
 return dict(label=label,gid=meta['id'],map=meta['mapName'],bots=base['bots'],last_round=base['last_round'],anomalies=base['anomalies'],turns=hist,rams=audit)

if __name__=='__main__':
 for label in LABELS:
  inv=a.label_report.inventory(label,'old')
  for path,meta in inv['jobs']:
   cache=OUT/f'scan-{meta["id"]}.json'
   if cache.exists():continue
   result=analyze(path,meta,label)
   cache.write_text(json.dumps(result,separators=(',',':')))
   print(label,meta['id'],'turns',len(result['turns']),'rams',len(result['rams']),dict(Counter(x['class'] for x in result['rams'])),flush=True)
