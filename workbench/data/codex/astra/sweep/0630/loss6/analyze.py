import sys,json,importlib.util,hashlib
from pathlib import Path
from collections import deque
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
sys.path.insert(0,'tools');import ladder_replay as lr
spec=importlib.util.spec_from_file_location('cr','data/analysis/ladder/losses/counts/count_replays.py');cr=importlib.util.module_from_spec(spec);spec.loader.exec_module(cr)
for gid,bid in ((1497389,1497386),(1497390,1497386),(1496711,1496711)):
 folder=Path(f'data/online/live-one1/b{bid}');path=folder/f'M{gid}.replay';meta=json.loads((folder/f'game-{gid}.json').read_text())
 base=lr.scan(path,meta,str(folder),set());base.pop('intervals');(OUT/f'{gid}-base.json').write_text(json.dumps(base))
 root=lr.replay.load(path).root();w,h=map(int,root.text(0).splitlines()[0].split()[1:3]);bodies={};teams={};edges=[];own=int(meta['teamAId']!=1119)
 for line in root.text(0).splitlines():
  a=line.split()
  if a[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(a[4+2*k])*w+int(a[3+2*k]) for k in range(int(a[2])));teams[i]=int(a[1])
  elif a[0]=='EDGE':edges.append(tuple(map(int,a[1:4])))
 geo=cr.Geometry(w,h,edges);qu=base['queens']['us'];qt=base['queens']['them'];pearls=set();turns=[];queen=[];near=[];near_turns=[];rnd=-1;actor=None;turn=None;detail=[];qpositions={}
 qd=next((d for d in base['deaths'] if d['id']==qu),None);focus=set(range(qd['round']-3,qd['round']+1)) if qd else set()
 def close():
  if turn is not None:turn['end']=list(bodies.get(actor,()));turns.append(turn)
 def nearcheck(idx,k):
  if qu not in bodies and qt in bodies:
   hd=bodies[qt][0];qpositions[rnd]=hd;dist=geo.distances(hd);pairs=[(dist[b[0]],i,b[0]) for i,b in bodies.items() if teams[i]==own]
   if pairs:
    dd,i,p=min(pairs)
    if not near or dd<near[-1]['distance']:near.append(dict(round=rnd,event=idx,distance=dd,id=i,head=p,queen=hd))
   if k==1 and teams[actor]==own and dist[bodies[actor][0]]<=5:near_turns.append(dict(round=rnd,id=actor,distance=dist[bodies[actor][0]],head=bodies[actor][0],queen=hd,length=len(bodies[actor])))
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:close();turn=None;rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);turn=dict(round=rnd,event=idx,id=actor,side=teams[actor],start=list(bodies[actor]),eats=0,steps=[],action=None,splits=[],deaths=[])
   if actor==qu or (rnd in focus):turn['bodies']={i:list(b) for i,b in bodies.items()};turn['pearls']=list(pearls)
   if actor==qu:queen.append(turn)
   if rnd in focus:detail.append(turn)
  elif k==3:
   pt=lr.replay.point(p.pointer(0));c=pt[1]*w+pt[0]
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eats']+=1
  elif k==4:
   a=p.pointer(0);turn['action']=dict(type=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [])
  elif k==9:
   i=p.i32(0);hd=lr.replay.point(p.pointer(0));tl=lr.replay.point(p.pointer(1));hd=hd[1]*w+hd[0];tl=tl[1]*w+tl[0];b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);turn['steps'].append([i,hd])
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   turn['splits'].append([p.i32(0),p.i32(4)])
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(lr.replay.point(c)[1]*w+lr.replay.point(c)[0] for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:turn['deaths'].append([p.i32(0),p.u16(4)]);bodies.pop(p.i32(0))
  if k in (1,9,10,11):nearcheck(idx,k)
 close()
 out=dict(w=w,h=h,own=own,teams=teams,queen=queen[-3:],attacker=detail,near=near,near_turns=near_turns,enemy_positions=qpositions,final={i:list(b) for i,b in bodies.items()},turns=[{k:v for k,v in t.items() if k not in ('bodies','pearls')} for t in turns],sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 (OUT/f'{gid}-detail.json').write_text(json.dumps(out))
 print(gid,'bots',base['bots'],'q',base['queens'],'final',base['final'],'qdeath',qd,'near',near,'near_turn_n',len(near_turns),'anomalies',base['anomalies'])
 for t in queen[-3:]:print('QTURN',{k:v for k,v in t.items() if k not in ('bodies','pearls')})
