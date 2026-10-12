import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter,defaultdict
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as lr
from count_local import Geo
OUT=Path('data/codex/astra/sweep/1055/loss41'); BASE=Path('data/online/live-one1/b1511406')
for gid in [1511407,1511409,1511410]:
 root=lr.replay.load(BASE/f'M{gid}.replay').root();bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if not q:continue
  if q[0]=='MAP':w,h=map(int,q[1:3])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
  elif q[0]=='DRAGON':
   i=len(bodies);teams[i]=int(q[1]);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
 g=Geo(w,h,raw);queens={s:min(i for i in bodies if teams[i]==s) for s in (0,1)};us=queens[1];them=queens[0]
 pearls=set();rnd=-1;actor=None;turn=None;turns=[];qdeath=None;deathstates=[];distcache={};near=[];roundmin={};qpos={};deaths=[];splits=[]
 def state():return {'r':rnd,'actor':actor,'bodies':{i:list(b) for i,b in bodies.items()},'pearls':list(pearls)}
 def close():
  if turn is not None:
   turn['end']={i:[len(b),b[0]%w,b[0]//w] for i,b in bodies.items() if i in (us,them,turn['actor'])};turns.append(turn)
 def distance(src):
  if src not in distcache:
   ds={src:0};q=deque([src])
   while q:
    c=q.popleft()
    for dest in g.adj[c]:
     if dest not in ds:ds[dest]=ds[c]+1;q.append(dest)
   distcache[src]=ds
  return distcache[src]
 def proximity(event):
  if qdeath is None or them not in bodies:return
  target=bodies[them][0];qpos[rnd]=target;ds=distance(target)
  best=min(((ds.get(b[0],9999),i,b[0]) for i,b in bodies.items() if teams[i]==1),default=(9999,None,None))
  if rnd not in roundmin or best[0]<roundmin[rnd][0]:roundmin[rnd]=list(best)+[target,event]
  if best[0]<=5 and (not near or near[-1][0]!=rnd):near.append([rnd,*best,target,event])
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:close();turn=None;rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);turn={'r':rnd,'actor':actor,'start':state(),'moves':[],'eats':[],'deaths':[]}
  elif k==4:
   a=p.pointer(0);turn['action']=a.u16(0) if a else None;turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==3:
   xy=lr.replay.point(p.pointer(0));c=xy[1]*w+xy[0]
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eats'].append(c)
  elif k==9:
   i=p.i32(0);xy=lr.replay.point(p.pointer(0));hd=xy[1]*w+xy[0];xy=lr.replay.point(p.pointer(1));tl=xy[1]*w+xy[0];b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);turn['moves'].append([i,hd])
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   par,ch=p.i32(0),p.i32(4);splits.append([rnd,par,ch,len(bodies[par])])
   for z,i in enumerate((par,ch)):bodies[i]=deque(lr.replay.point(c)[1]*w+lr.replay.point(c)[0] for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);d={'r':rnd,'id':i,'reason':p.u16(4),'L':len(bodies[i]),'actor':actor,'head':bodies[i][0]};deaths.append(d);turn['deaths'].append(d)
   if i==us:qdeath=rnd;deathstates.append(state())
   bodies.pop(i)
  if k in (0,1,9,10,11):proximity(idx)
 close()
 qt=[t for t in turns if t['actor']==us];last=qt[-3:];attack=[t for t in turns if any(d['id']==us for d in t['deaths'])]
 # Keep full states only for queen and her attacker's nearby turns.
 attacker=attack[0]['actor'] if attack else None
 selected=[t for t in turns if t['actor']==us or (t['actor']==attacker and qdeath-5<=t['r']<=qdeath)]
 data={'gid':gid,'w':w,'h':h,'queens':queens,'teams':teams,'qdeath':qdeath,'last3':last,'attack':attack,'selected':selected,'near':near,'roundmin':roundmin,'qpos':qpos,'splits':splits,'deaths':deaths}
 (OUT/f'{gid}-detail.json').write_text(json.dumps(data))
 def board(t):
  bs={int(i):b for i,b in t['start']['bodies'].items()};center=bs[us][0];cx,cy=center%w,center//w;occ={c:(i,n) for i,b in bs.items() for n,c in enumerate(b)};ps=set(t['start']['pearls']);lines=[]
  for dy in range(-3,4):
   y=(cy+dy)%h;top='';row=''
   for dx in range(-3,4):
    x=(cx+dx)%w;c=y*w+x
    top+='+'+('─' if g.moves[c][0][0]==1 else 'P' if g.moves[c][0][0]==2 else ' ')
    ch='*' if c in ps else '.'
    if c in occ:
     i,n=occ[c];ch=('Q' if i==us else 'K' if i==them else 'F' if teams[i]==1 else 'E') if n==0 else ('q' if i==us else 'k' if i==them else 'f' if teams[i]==1 else 'e')
    row+=('│' if g.moves[c][3][0]==1 else 'P' if g.moves[c][3][0]==2 else ' ')+ch
   lines.extend([top+'+',row+('│' if g.moves[c][1][0]==1 else 'P' if g.moves[c][1][0]==2 else ' ')])
  bottom=''
  for dx in range(-3,4):
   c=((cy+3)%h)*w+(cx+dx)%w;bottom+='+'+('─' if g.moves[c][2][0]==1 else 'P' if g.moves[c][2][0]==2 else ' ')
  lines.append(bottom+'+');return lines
 boards=[board(t) for t in last]
 txt=' | '.join(f"r{t['r']} Q@{t['start']['bodies'][us][0]%w},{t['start']['bodies'][us][0]//w} L{len(t['start']['bodies'][us])} dirs={t.get('dirs')}" for t in last)+'\n'+'\n'.join('    '.join(row) for row in zip(*boards))
 (OUT/f'{gid}-boards.txt').write_text(txt+'\n')
 print(gid,'queen',us,'dies',qdeath,'attacker',attacker,'last',[(t['r'],t.get('dirs'),t['moves']) for t in last],'nearest',min(roundmin.values(),default=[]),'near rounds',len(near),flush=True)
