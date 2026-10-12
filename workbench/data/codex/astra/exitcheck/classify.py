import sys
sys.dont_write_bytecode=True
import analyze as a
import json
from collections import deque,Counter
O=a.O

def evalrow(x):
 root=a.lr.replay.load(a.R/x['path']).root();g=a.gm.Geo(root.text(0));teams={};q=x['queen']
 for line in root.text(0).splitlines():
  t=line.split()
  if t and t[0]=='DRAGON':teams[len(teams)]=int(t[1])
 for ev in root.pointer(3):
  if ev.u16(0)==10:
   p=ev.pointer(0);teams[p.i32(4)]=p.u16(8)
 def ex(body,other):return [n for n in g.moves[body[0]] if n is not None and n not in body and n not in other]
 def alt(t):
  st=t['snapshot'];bs={int(i):list(map(tuple,b)) for i,b in st['bodies'].items()};body=list(map(tuple,t['body']));ps=set(map(tuple,st['pearls']));i=t['id'];other={c for k,b in bs.items() if k!=i for c in b};out=[]
  for d,n in enumerate(g.moves[body[0]]):
   if n is None:out.append(dict(d='NESW'[d],kind='wall'));continue
   if n in body:out.append(dict(d='NESW'[d],kind='self'));continue
   if n in other:
    who=next(k for k,b in bs.items() if k!=i and n in b);out.append(dict(d='NESW'[d],kind='head' if bs[who][0]==n else 'body',who=who));continue
   nb=[n]+body if n in ps else [n]+body[:-1]
   out.append(dict(d='NESW'[d],kind='move',body=nb,own_exits=ex(nb,other),queen_exits=[v for v in g.moves[tuple(st['head'])] if v is not None and v not in other and v not in nb],portal=g.edges.get(a.lr.edge_id(g.w,g.h,*body[0],d),(0,-1))[0]==2))
  return out
 def board(t):
  st=t['snapshot'];h=st['head'];bs={int(i):list(map(tuple,b)) for i,b in st['bodies'].items()};oc={c:(i,k) for i,b in bs.items() for k,c in enumerate(b)};ps=set(map(tuple,st['pearls']));grid=[[' ']*15 for _ in range(15)]
  for dy in range(7):
   for dx in range(7):
    c=((h[0]+dx-3)%g.w,(h[1]+dy-3)%g.h);ch='*' if c in ps else '.'
    if c in oc:
     i,k=oc[c];ch=('Q' if k==0 else 'q') if i==q else ('A' if k==0 else 'a') if teams[i]==x['own'] else ('E' if k==0 else 'e')
    grid[2*dy+1][2*dx+1]=ch
    for d,(yy,xx) in enumerate(((2*dy,2*dx+1),(2*dy+1,2*dx+2),(2*dy+2,2*dx+1),(2*dy+1,2*dx))):
     edge=g.edges.get(a.lr.edge_id(g.w,g.h,*c,d),(0,-1))[0]
     grid[yy][xx]='P' if edge==2 else ('-' if d%2==0 else '|') if edge==1 else ' '
  for y in range(0,15,2):
   for xx in range(0,15,2):grid[y][xx]='+'
  return '\n'.join(''.join(r) for r in grid)
 d=x['death'];closers=[]
 candidates=list(x['closures']);hf=O/f'history{x["gid"]}.json';hist=json.loads(hf.read_text()) if hf.exists() else x.get('history',[])
 for t in hist:
  if t['id']==q or t['team']!=x['own'] or not t.get('snapshot') or t['qh']!=d['snapshot']['head'] or t['endexits'] or not t['endbody'] or any(c['event']==t['event'] for c in candidates):continue
  st=t['snapshot'];other={tuple(z) for i,b in st['bodies'].items() if int(i)!=t['id'] for z in b}
  opened=[n for n in g.moves[tuple(t['qh'])] if n is not None and n not in other]
  if opened:candidates.append(dict(t,remove_exits=opened,already_boxed=True))
 for c in candidates:
  if 'snapshot' not in c:continue
  c=dict(c);c['alternatives']=alt(c);bs={int(i):list(map(tuple,b)) for i,b in c['snapshot']['bodies'].items()};qh=tuple(c['qh']);b=list(map(tuple,c['body']));visible_neighbors=all(n is None or g.visible(n,b[0]) for n in g.moves[qh]);portals=any(g.edges.get(a.lr.edge_id(g.w,g.h,*qh,z),(0,-1))[0]==2 for z in range(4));pathportal=False;h=b[0]
  for z in c['dirs']:
   if g.edges.get(a.lr.edge_id(g.w,g.h,*h,z),(0,-1))[0]==2:pathportal=True
   h=g.moves[h][z]
   if h is None:break
  near=c['distance']<=2 or any((min(abs(v[0]-qh[0]),g.w-abs(v[0]-qh[0]))+min(abs(v[1]-qh[1]),g.h-abs(v[1]-qh[1])))<=1 for v in c['path'])
  c['strict_gate']=c['team']==x['own'] and c['id']>1 and c['L'] in (2,3) and c['qvisible'] and near and not c['split'] and bool(c['dirs'])
  c['visible_neighbors']=visible_neighbors;c['queen_portal']=portals;c['pathportal']=pathportal
  c['strict_certain']=c['strict_gate'] and visible_neighbors and all(g.visible(tuple(v),b[0]) for v in c['path']) and all(g.visible(v,b[0]) for v in b)
  c['live_alternatives']=[z['d'] for z in c['alternatives'] if z['kind']=='move' and z['queen_exits']]
  closers.append(c)
 turns=[dict(t,alternatives=alt(t),board=board(t)) for t in x['turns']]
 return dict(gid=x['gid'],v=x['v'],map=x['map'],queen=q,own=x['own'],death={k:v for k,v in d.items() if k!='snapshot'},neighbors=d['snapshot']['neighbors'],turns=turns,closures=closers)
if __name__=='__main__':
 for p in sorted(O.glob('g*.json')):
  if not p.stem[1:].isdigit():continue
  x=json.loads(p.read_text());f=O/f'case{x["gid"]}.json'
  if not x['selected'] or x['v']==11 or f.exists():continue
  v=evalrow(x);f.write_text(json.dumps(v,ensure_ascii=False));print(x['gid'],flush=True)
