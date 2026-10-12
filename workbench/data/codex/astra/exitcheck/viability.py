import sys
sys.dont_write_bytecode=True
import analyze as a
import json
O=a.O
out=[]
for f in sorted(O.glob('case*.json')):
 x=json.loads(f.read_text())
 if x['death']['reason']==3 or any(c['strict_certain'] for c in x['closures']):continue
 raw=json.loads((O/f'g{x["gid"]}.json').read_text());root=a.lr.replay.load(a.R/raw['path']).root();g=a.gm.Geo(root.text(0));hits=[]
 for t in x['turns']:
  if t['L'] not in (2,3) or not t['dirs'] or not t['endbody']:continue
  head=tuple(t['body'][0]);initial=tuple(map(tuple,t['body']));known={c for c in g.moves if g.visible(c,head)};pearls=frozenset(map(tuple,t['snapshot']['pearls']));other={tuple(c) for i,b in t['snapshot']['bodies'].items() if int(i)!=t['id'] for c in b}
  def step(body,eaten,d,paid=False,first=False):
   n=g.moves[body[0]][d]
   if n is None or n in body or (first and n in other) or (paid and len(body)<=2):return None
   if n not in known:return 'unknown'
   eat=n in pearls and n not in eaten;nb=(n,)+body if eat else (n,)+body[:-1]
   if paid:nb=nb[:-1]
   return nb,eaten|{n} if eat else eaten
  def viable(state,stack,depth=0):
   if state=='unknown':return True
   body,eaten=state
   if len(body)>=4 or depth>=35:return True
   key=(body,eaten)
   if key in stack:return True
   return any(ns is not None and viable(ns,stack|{key},depth+1) for d in range(4) if (ns:=step(body,eaten,d)) is not None)
  state=(initial,frozenset());valid=True
  for z,d in enumerate(t['dirs']):
   state=step(*state,d,paid=z>=((t['L']+3)//4),first=True) if state!='unknown' else 'unknown'
   if state is None:valid=False;break
  if not valid or viable(state,set()):continue
  alts=[]
  for d in range(4):
   st=step(initial,frozenset(),d,first=True)
   if st is not None and g.edges.get(a.lr.edge_id(g.w,g.h,*initial[0],d),(0,-1))[0]==0 and viable(st,set()):alts.append('NESW'[d])
  if alts:hits.append(dict(r=t['r'],L=t['L'],head=head,original=''.join('NESW'[d] for d in t['dirs']),alternatives=alts))
 out.append(dict(gid=x['gid'],hits=hits))
 print(x['gid'],hits,flush=True)
(O/'viability.json').write_text(json.dumps(out,indent=2))
