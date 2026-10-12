import sys,json
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
ROOT=Path.cwd(); OUT=ROOT/'data/codex/astra/sweep/0544/loss2'
sys.path.insert(0,str(ROOT/'data/analysis/ladder/dossier/local'))
from replay_format import load,point
from count_local import Geo

def scan(gid):
 root=load(ROOT/f'data/online/smoke/one8-c2-old/M{gid}.replay').root()
 bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if not q:continue
  if q[0]=='MAP':w,h=map(int,q[1:3])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
  elif q[0]=='DRAGON':
   i=len(bodies);teams[i]=int(q[1]);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
 geo=Geo(w,h,raw); queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 def xy(c):return [c%w,c//w]
 def snap():return [dict(units=sum(teams[i]==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),longest=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),queen=len(bodies.get(queens[s],[]))) for s in (0,1)]
 balls={}
 def ball(src):
  if src in balls:return balls[src]
  d={src:0};q=[src]
  for c in q:
   if d[c]>=5:continue
   for n in geo.adj[c]:
    if n not in d:d[n]=d[c]+1;q.append(n)
  balls[src]=d
  return d
 tile=lambda p:point(p)[1]*w+point(p)[0]
 turns=[];deaths=[];splits=[];snaps={};pearls=set();origins={};rnd=-1;cur=None;actor=None;near=[];qdead=False;firstnear=None;eqpos=[]
 def close():
  if cur is not None:cur['end']=list(bodies.get(actor,[]));cur['stateEnd']=snap()
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close()
   if rnd>=0:snaps[rnd]=snap()
   rnd=p.i32(0);actor=None;cur=None
  elif k==1:
   close();actor=p.i32(0)
   cur=dict(r=rnd,id=actor,L=len(bodies[actor]),body=list(bodies[actor]),steps=[],eats=[],eatOrigins=[],action=None,indicator='',state=snap())
   if actor in queens:cur['bodies']={i:list(b) for i,b in bodies.items()};cur['pearls']=list(pearls)
   if qdead and queens[1] in bodies and teams[actor]==0:
    eh=bodies[queens[1]][0];dist=ball(bodies[actor][0]).get(eh,99)
    if dist<=5:
     rec=dict(r=rnd,id=actor,L=len(bodies[actor]),distance=dist,head=xy(bodies[actor][0]),queen=xy(eh))
     near.append(rec);cur['nearQueen']=rec
   if actor==queens[1]:eqpos.append([rnd,xy(bodies[actor][0]),len(bodies[actor])])
   turns.append(cur)
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):pearls.add(c);origins[c]="natural" if actor is None else "drop"
   else:
    pearls.discard(c)
    if cur:cur['eats'].append(c);cur['eatOrigins'].append(origins.pop(c,'unknown'))
  elif k==7:
   if cur:cur['indicator']=p.text(0)
  elif k==6:
   if cur:cur.setdefault('logs',[]).append(p.text(0))
  elif k==4:
   a=p.pointer(0)
   if cur:cur['action']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else ('kind'+str(a.u16(0)) if a else None)
  elif k==9:
   i=p.i32(0);hd=tile(p.pointer(0));tail=tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:
    if cur:cur['steps'].append([b[0],hd])
    b.appendleft(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
   if qdead and queens[1] in bodies:
    eh=bodies[queens[1]][0]
    for j in ([z for z in bodies if teams[z]==0] if i==queens[1] else [i] if teams[i]==0 else []):
     dist=ball(bodies[j][0]).get(eh,99)
     if dist<=5:near.append(dict(r=rnd,id=j,L=len(bodies[j]),distance=dist,head=xy(bodies[j][0]),queen=xy(eh),event=idx))
  elif k==10:
   parent,child=p.i32(0),p.i32(4)
   rec=dict(r=rnd,parent=parent,child=child,before=len(bodies[parent]))
   for z,i in enumerate((parent,child)):bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
   rec.update(keep=len(bodies[parent]),give=len(bodies[child]));splits.append(rec)
   if qdead and queens[1] in bodies:
    eh=bodies[queens[1]][0]
    for j in (parent,child):
     if teams[j]!=0:continue
     dist=ball(bodies[j][0]).get(eh,99)
     if dist<=5:near.append(dict(r=rnd,id=j,L=len(bodies[j]),distance=dist,head=xy(bodies[j][0]),queen=xy(eh),event=idx))
  elif k==11:
   i=p.i32(0);reason=p.u16(4)
   rec=dict(r=rnd,id=i,side=teams[i],L=len(bodies[i]),body=list(bodies[i]),reason=reason,actor=actor,actorTurn=cur.copy(),state=snap())
   if i in queens:rec['bodies']={i:list(b) for i,b in bodies.items()}
   deaths.append(rec);bodies.pop(i)
   if i==queens[0]:
    qdead=True
    if queens[1] in bodies:
     eh=bodies[queens[1]][0]
     for j in bodies:
      if teams[j]!=0:continue
      dist=ball(bodies[j][0]).get(eh,99)
      if dist<=5:near.append(dict(r=rnd,id=j,L=len(bodies[j]),distance=dist,head=xy(bodies[j][0]),queen=xy(eh),event=idx))
 close();snaps[rnd]=snap()
 res=root.pointer(4);expected=[dict(zip(('units','longest','total','queen'),[res.pointer(s).i32(o) for o in (0,4,8,12)])) for s in (0,1)]
 assert snap()==expected,(snap(),expected)
 qturns=[t for t in turns if t['id']==queens[0]]
 data=dict(botA=root.text(1),botB=root.text(2),gid=gid,w=w,h=h,queens=queens,final=expected,lastRound=rnd,endedBy=res.u16(2),deaths=deaths,splits=splits,turns=turns,snaps=snaps,near=near,eqpos=eqpos,teams=teams)
 (OUT/f'{gid}.json').write_text(json.dumps(data,separators=(',',':')))
 summary={k:data[k] for k in ('gid','w','h','queens','final','lastRound','endedBy')};summary['queenDeaths']=[{k:v for k,v in d.items() if k not in ('bodies','actorTurn')} for d in deaths if d['id'] in queens];summary['lastQueenTurns']=[{k:v for k,v in t.items() if k not in ('bodies','pearls')} for t in qturns[-3:]];summary['nearCount']=len(near);summary['nearFirst']=near[:5];summary['checkpoints']={r:snaps[min(r,rnd)] for r in (0,50,100,200,300,400,499)}
 print(json.dumps(summary,ensure_ascii=False))
for gid in (1493881,1493882,1493883):scan(gid)
