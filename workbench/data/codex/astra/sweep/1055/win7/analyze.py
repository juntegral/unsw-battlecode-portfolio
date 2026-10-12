import sys
sys.dont_write_bytecode = True
import json, ast, types
from pathlib import Path
from collections import deque, Counter
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/local', 'data/analysis/ladder/dossier/work']
import ladder_replay as lr
import scoreboard as sb
geo_path = Path('data/analysis/ladder/dossier/work/tq2_near.py')
geo_tree = ast.parse(geo_path.read_text())
geo_tree.body = [n for n in geo_tree.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'main')]
geo_module = types.ModuleType('win7_shared_geo')
exec(compile(geo_tree, str(geo_path), 'exec'), geo_module.__dict__)
Geo = geo_module.Geo

OUT = Path(__file__).resolve().parent
PATHS = [
 'data/online/smoke/one13-q1-old/M1515671.replay',
 *[f'data/online/live-one1/b1506911/M{g}.replay' for g in (1506912,1506913,1506914)],
 'data/online/live-one1/b1506148/M1506148.replay',
 'data/online/live-one1/b1511406/M1511408.replay',
 'data/online/live-one1/b1514288/M1514289.replay',
 *[f'data/online/live-one1/b1515123/M{g}.replay' for g in (1515124,1515127)],
 *[f'data/online/smoke/one13-k1-old/M{g}.replay' for g in (1509098,1509099,1509101)],
]

def scan(path):
 path = Path(path)
 meta = json.loads(path.with_name('game-'+path.stem[1:]+'.json').read_text())
 root = sb.load_replay(path).root()
 print(meta['id'],'decoded',flush=True)
 original = lr.replay.load
 lr.replay.load = lambda _: type('Loaded', (), {'root': lambda _: root})()
 try: base = lr.scan(path, meta, path.parent.name, set())
 finally: lr.replay.load = original
 print(meta['id'],'base verified',flush=True)
 assert root.text(1 if base['ours']=='A' else 2) == '21377'
 assert base['winner'] == base['ours']
 lines = root.text(0).splitlines()
 w,h = map(int,lines[0].split()[1:3])
 raw = [tuple(map(int,l.split()[1:4])) for l in lines if l.startswith('EDGE ')]
 geo = Geo(w,h,raw)
 bodies, teams = {}, {}
 for line in lines:
  q = line.split()
  if q[0]=='DRAGON':
   i=len(bodies); teams[i]='AB'[int(q[1])]
   bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
 ours=base['ours']; queen=base['queens']['us']; foe=base['queens']['them']
 rnd=0; actor=None; turn=None; pearls=set(); turns=[]; qstates=[]; counts=Counter()
 histories={}; visited={}; units=Counter()
 squares=[tuple(((c//w+dy)%h)*w+(c%w+dx)%w for dx in range(-3,4) for dy in range(-3,4)) for c in range(w*h)]
 tile=lambda p: lr.replay.point(p)[1]*w+lr.replay.point(p)[0]
 xy=lambda c: [c%w,c//w]
 def visible(a,b):
  dx=abs(a%w-b%w); dy=abs(a//w-b//w)
  return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
 def close():
  nonlocal turn
  if turn is None: return
  i=turn['id']; live=i in bodies
  turn['end_length']=len(bodies.get(i,()))
  turn['end_head']=xy(bodies[i][0]) if live else None
  turn['died']=not live
  turn['stay']=live and not turn['moves'] and not turn['split']
  if teams[i]==ours:
   turns.append(turn)
   if i==queen:
    qstates.append(turn)
   if turn['stay']: counts['stay']+=1
  turn=None
 def qdanger():
  if queen not in bodies:return
  c=bodies[queen][0]
  heads=[(j,b[0],len(b)) for j,b in bodies.items() if teams[j]!=ours]
  near=[(j,L) for j,z,L in heads if c in geo.nxt[z]]
  if near:
   counts['q_one_step_samples']+=1
   qadj.append(dict(round=rnd,actor=actor,queen=xy(c),length=len(bodies[queen]),enemies=near))
 qadj=[]
 for idx,e in enumerate(root.pointer(3)):
  k=e.u16(0); p=e.pointer(0)
  if k==0:
   close();rnd=p.i32(0);actor=None
   if rnd%100==0:print(meta['id'],'round',rnd,flush=True)
  elif k==1:
   close();actor=p.i32(0)
   if actor==queen:qdanger()
   c=bodies[actor][0];L=len(bodies[actor]);own=teams[actor]==ours
   if own:visited.setdefault(actor,set()).update(squares[c])
   occ={z for b in bodies.values() for z in b} if own else set()
   adj=[(d,z) for d,z in enumerate(geo.nxt[c]) if z>=0 and z not in occ] if own else []
   adj_pearl=[xy(z) for d,z in adj if z in pearls]
   unseen_portals=[d for d,z in adj if geo.por[c][d] and z not in visited.get(actor,set())]
   ball=geo.ball(c) if own else {}
   enemies=[dict(id=j,length=len(b),head=xy(b[0]),distance=ball.get(b[0],99),visible=visible(c,b[0])) for j,b in bodies.items() if teams[j]!=teams[actor]] if own else []
   turn=dict(round=rnd,event=idx,id=actor,length=L,head=xy(c),action=None,dirs=[],moves=[],split=None,eats=0,adj_pearls=adj_pearl,unseen_portals=unseen_portals,ordinary_open=any(not geo.por[c][d] for d,z in adj),enemies=enemies,units=sum(teams[j]==teams[actor] for j in bodies) if own else 0,foe_q=len(bodies.get(foe,())),mate_near=sum(j!=actor and teams[j]==teams[actor] and visible(c,b[0]) for j,b in bodies.items()) if actor==queen else 0)
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:
    pearls.remove(c)
    if turn is not None:turn['eats']+=1
  elif k==4:
   a=p.pointer(0)
   turn['action']=a.u16(0) if a else None
   turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
   usage=p.pointer(1)
   turn['cpu']=usage.u64(0) if usage else 0
   turn['timeout']=p.bit(32)
  elif k==9:
   i=p.i32(0);c=tile(p.pointer(0));tail=tile(p.pointer(1));b=bodies[i]
   if b[0]!=c:
    b.appendleft(c)
    if turn is not None and i==actor:turn['moves'].append(xy(c))
   while len(b)>1 and b[-1]!=tail:b.pop()
   if i==queen:qdanger()
  elif k==10:
   parent,child=p.i32(0),p.i32(4)
   turn['split']=dict(parent_before=len(bodies[parent]),child=child,child_length=len(p.pointer(1)))
   for z,i in enumerate((parent,child)):
    bodies[i]=deque(tile(t) for t in p.pointer(z));teams[i]='AB'[p.u16(8)]
  elif k==11:bodies.pop(p.i32(0))
 close()
 def score(s):return (s['queen_length'],s['longest'],s['total'])
 lead={r:(score(ss['us'])>score(ss['them']) if ss['us']['alive'] and ss['them']['alive'] else bool(ss['us']['alive'])) for r,ss in base['snapshots'].items()}
 behind=[r for r,v in lead.items() if not v]
 permanent=min((r for r,v in lead.items() if v and (not behind or r>max(behind))),default=None)
 qdeaths=[d for d in base['deaths'] if d['id'] in (queen,foe)]
 qlengths=Counter(t['length'] for t in qstates)
 keeper=[t for t in qstates if t['length'] in (3,4) and t['units']>=2 and t['action']==0]
 portal=[t for t in turns if t['id']!=queen and t['length']<4 and t['unseen_portals'] and t['ordinary_open'] and t['action']==0 and t['moves'] and t['dirs'] and t['dirs'][0] not in t['unseen_portals']]
 misses=[t for t in turns if t['adj_pearls'] and t['action']==0 and t['eats']==0 and not t['died']]
 adjacent_eats=[t for t in turns if t['adj_pearls'] and t['eats']>0]
 bigescape=[t for t in turns if t['id']!=queen and t['length']>=8 and 2<=len(t['moves'])<=min(6,(t['length']+3)//4) and not t['died'] and any(x['distance']<=3 for x in t['enemies'])]
 base.update(permanent_lead=permanent,queen_lengths=dict(qlengths),queen_deaths=qdeaths,qadj=qadj,
             turns=turns,keeper=keeper,portal=portal,misses=misses,adjacent_eats=adjacent_eats,bigescape=bigescape,
             max_cpu=max(t.get('cpu',0) for t in turns),timeouts=sum(t.get('timeout',False) for t in turns))
 return base

if __name__=='__main__':
 with (OUT/'measured.jsonl').open('w') as f:
  for path in PATHS:
   v=scan(path);f.write(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n');f.flush()
   print(v['gid'],v['map'],'lead',v['permanent_lead'],'final',v['final'],'qdeath',[(d['id'],d['round'],d['cause'],d['actor']) for d in v['queen_deaths']], 'adj',len(v['qadj']), 'portal',len(v['portal']), 'big',len(v['bigescape']),flush=True)
