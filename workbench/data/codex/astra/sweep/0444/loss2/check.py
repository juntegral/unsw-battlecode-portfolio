import sys,json,ast,types
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,'tools');from ladder_replay import replay
p=Path('data/analysis/ladder/dossier/work/tq2_near.py');tree=ast.parse(p.read_text());tree.body=[n for n in tree.body if not isinstance(n,ast.Expr)];m=types.ModuleType('geo');exec(compile(tree,str(p),'exec'),m.__dict__)
O=Path('data/codex/astra/sweep/0444/loss2');out={}
for gid in (1488848,1488849):
 j=json.loads((O/f'{gid}-trace.json').read_text());base=json.loads((O/f'{gid}-base.json').read_text());w,h=j['w'],j['h'];geo=m.Geo(w,h,[tuple(map(int,l.split()[1:4])) for l in base['text'].splitlines() if l.startswith('EDGE ')])
 xy=lambda c:[c%w,c//w]
 def distance(a,b):
  Q=deque([a]);seen={a:0}
  while Q:
   v=Q.popleft()
   if v==b:return seen[v]
   for z in geo.nxt[v]:
    if z>=0 and z not in seen:seen[z]=seen[v]+1;Q.append(z)
  return 99999
 qr=next(d['round'] for d in base['deaths'] if d['id']==j['queens'][0]);eh=None;close=[];own_context={};qpos=[];nearown=[]
 for t in j['turns']:
  i=t['id'];r=t['r']
  if i==j['queens'][1]:eh=t['end'][0] if t['end'] else None
  if i==j['queens'][1] and r>qr:qpos.append(xy(t['body'][0]))
  if t['side']==0 and r>qr and eh is not None:
   d=distance(t['body'][0],eh);close.append([d,r,i,xy(t['body'][0]),xy(eh),len(t['body'])])
   if d<=5:nearown.append(close[-1])
 out[str(gid)]=dict(min_after=min(close) if close else None,queen_region=[min(c[0] for c in qpos),max(c[0] for c in qpos),min(c[1] for c in qpos),max(c[1] for c in qpos)],near_own_turns=nearown)
 if gid==1488848:
  for q in j['lastq']:
   pos=q['body'][0];att=q['context'].get('15');out[str(gid)][f"r{q['r']}_exits"]=[(xy(c),distance(att[0],c),c in q['body']) for c in geo.nxt[pos] if c>=0]
  out[str(gid)]['starvation']={}
  for i in (0,2):
   turns=[t for t in j['turns'] if t['id']==i and (i==0 or 34<=t['r']<=72)]
   adjacent=[t['r'] for t in turns if any(c in t['pearls'] for c in geo.nxt[t['body'][0]] if c>=0)]
   out[str(gid)]['starvation'][i]=dict(turns=len(turns),eats=sum(t['eat'] for t in turns),adjacent_pearl_rounds=adjacent)
  out[str(gid)]['permanent_deficit']={key:1+max(int(r) for r,s in base['snapshots'].items() if s['us'][key]>=s['them'][key]) for key in ('total','pearls','alive')}
 else:
  out[str(gid)]['attacker_direct_sightings']=[t['r'] for t in j['turns'] if t['id']==j['queens'][0] and '787' in t.get('context',{})]
  q=j['lastq'][-1];hd=q['body'][0];win={((hd//w+dy)%h)*w+(hd%w+dx)%w for dy in range(-3,4) for dx in range(-3,4)};occ=set(q['body']);frontier=[]
  for c in geo.nxt[hd]:
   if c<0 or c in occ:continue
   queue=deque([c]);seen={c:0}
   while queue:
    v=queue.popleft()
    if v not in win:
     frontier.append(dict(candidate=xy(c),distance=seen[v],first_unseen=xy(v)));break
    for z in geo.nxt[v]:
     if z>=0 and z not in seen and z not in occ:seen[z]=seen[v]+1;queue.append(z)
  out[str(gid)]['last_turn_frontier']=frontier
 # Draw 7x7 cells with wall and portal edges.
 diagrams=[]
 for t in j['lastq']:
  c=t['body'][0];x,y=xy(c);occ={z:(int(i),n) for i,b in t['context'].items() for n,z in enumerate(b)};ps=set(t['pearls']);a=[]
  for dy in range(-3,4):
   north='';row=''
   for dx in range(-3,4):
    z=((y+dy)%h)*w+(x+dx)%w
    north+='+'+('-' if geo.nxt[z][0]<0 else 'P' if geo.por[z][0] else ' ')
    v='*' if z in ps else '.'
    if z in occ:
     i,n=occ[z];v=('Q' if i==t['id'] else 'A' if j['teams'][str(i)]==0 else 'E') if n==0 else ('q' if i==t['id'] else 'a' if j['teams'][str(i)]==0 else 'e')
    row+=('|' if geo.nxt[z][3]<0 else 'P' if geo.por[z][3] else ' ')+v
   a.append(north+'+');a.append(row+('|' if geo.nxt[z][1]<0 else 'P' if geo.por[z][1] else ' '))
  south=''
  for dx in range(-3,4):
   z=((y+3)%h)*w+(x+dx)%w;south+='+'+('-' if geo.nxt[z][2]<0 else 'P' if geo.por[z][2] else ' ')
  a.append(south+'+');diagrams.append(a)
 (O/f'{gid}-diagram.txt').write_text('\n'.join('   '.join(d[row] for d in diagrams) for row in range(15)))
(O/'checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
