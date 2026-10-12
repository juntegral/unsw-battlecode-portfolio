import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
ROOT=Path.cwd(); OUT=ROOT/'data/codex/astra/sweep/0645/loss5'
sys.path.insert(0,str(ROOT/'tools'))
import ladder_replay as lr
sys.path.insert(0,str(ROOT/'data/analysis/ladder/dossier'))
from count_dossier import Geo
GAMES=[(1498363,1498363),(1498842,1498842),(1498842,1498843)]
def scan(folder,gid):
 p=ROOT/f'data/online/live-one1/b{folder}/M{gid}.replay';meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 base=lr.scan(p,meta,'loss5',set());root=lr.replay.load(p).root();w,h=map(int,base['text'].splitlines()[0].split()[1:3]);bs={};teams={};edges=[]
 for line in base['text'].splitlines():
  a=line.split()
  if a[0]=='DRAGON':
   i=len(bs);bs[i]=deque((int(a[3+2*k]),int(a[4+2*k])) for k in range(int(a[2])));teams[i]=int(a[1])
  elif a[0]=='EDGE':edges.append(tuple(map(int,a[1:4])))
 geo=Geo(w,h,edges);q=base['queens']['us'];eq=base['queens']['them'];rnd=-1;actor=None;pearls=set();turn=None;turns=[];qviews=[];near=[];dists={};minnear=None;finals={};split=[]
 def tile(c):return c[1]*w+c[0]
 def man(a,b):
  dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]);return min(dx,w-dx)+min(dy,h-dy)
 def view(c,d):return min(abs(c[0]-d[0]),w-abs(c[0]-d[0]))<=3 and min(abs(c[1]-d[1]),h-abs(c[1]-d[1]))<=3
 def board(c):
  cells={z:('Q' if i==q else 'K' if i==eq else 'A' if teams[i]==1 else 'E') if k==0 else ('q' if i==q else 'k' if i==eq else 'a' if teams[i]==1 else 'e') for i,b in bs.items() for k,z in enumerate(b)}
  return [''.join(cells.get(((c[0]+dx)%w,(c[1]+dy)%h),'*' if ((c[0]+dx)%w,(c[1]+dy)%h) in pearls else '.') for dx in range(-3,4)) for dy in range(-3,4)]
 def close():
  if turn is not None:
   turn['end']=list(bs.get(actor,()));turns.append(turn)
 for idx,ev in enumerate(root.pointer(3)):
  kind=ev.u16(0);p=ev.pointer(0)
  if kind==0:close();turn=None;rnd=p.i32(0);actor=None
  elif kind==1:
   close();actor=p.i32(0);turn=dict(round=rnd,event=idx,id=actor,team=teams[actor],body=list(bs[actor]),eats=0,steps=[],action=None)
   if actor==q:
    v=dict(round=rnd,event=idx,head=bs[q][0],body=list(bs[q]),board=board(bs[q][0]),visible={i:list(b) for i,b in bs.items() if any(view(bs[q][0],c) for c in b)},pearls=[c for c in pearls if view(bs[q][0],c)],exits=[(k,d%w,d//w) for k,d in geo.moves[tile(bs[q][0])]])
    qviews.append(v)
   if q not in bs and eq in bs and teams[actor]==1:
    c=tile(bs[actor][0]);target=tile(bs[eq][0]);
    if c not in dists:dists[c]=geo.bfs([c])
    dist=int(dists[c][target]);row=dict(round=rnd,event=idx,id=actor,length=len(bs[actor]),head=bs[actor][0],queen=bs[eq][0],distance=dist,manhattan=man(bs[actor][0],bs[eq][0]),visible=view(bs[actor][0],bs[eq][0]))
    if minnear is None or dist<minnear['distance']:minnear=row
    if dist<=5:
     row['view_pearls']=[z for z in pearls if view(bs[actor][0],z)]
     near.append(row)
  elif kind==3:
   c=lr.replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eats']+=1
  elif kind==4:
   a=p.pointer(0);turn['action']=dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else [])
  elif kind==9:
   i=p.i32(0);hd=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bs[i]
   if b[0]!=hd:
    if turn is not None and i==actor:turn['steps'].append(hd)
    b.appendleft(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif kind==10:
   parent,child=p.i32(0),p.i32(4);split.append(dict(round=rnd,parent=parent,child=child))
   for z,i in enumerate((parent,child)):bs[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif kind==11:bs.pop(p.i32(0))
 close()
 base.pop('text');base.pop('intervals');base.pop('natural');base.pop('pearls');base['turns']=turns;base['qviews']=qviews;base['near5']=near;base['minnear']=minnear;base['splits']=split;base['final_bodies']={i:list(b) for i,b in bs.items()};base['teams']=teams;base['size']=[w,h]
 (OUT/f'{gid}.json').write_text(json.dumps(base,ensure_ascii=False))
 print(gid,'bots',base['bots'],'final',base['final'],'last',rnd,'queen deaths',[d for d in base['deaths'] if d['id'] in (q,eq)],'near5',len(near),'minnear',minnear)
 print('snaps',[(r,s) for r,s in base['snapshots'].items() if r in (0,25,50,100,150,200,300,400,499)])
 print('last queen', [t for t in turns if t['id']==q][-3:])
for a,b in GAMES:scan(a,b)
