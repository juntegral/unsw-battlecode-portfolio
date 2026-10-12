import sys,json,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
ROOT=Path.cwd(); OUT=ROOT/'data/codex/astra/sweep/1055/loss23'
sys.path.insert(0,str(ROOT/'tools'))
import ladder_replay as lr
spec=importlib.util.spec_from_file_location('counts',ROOT/'data/analysis/ladder/losses/counts/count_replays.py'); counts=importlib.util.module_from_spec(spec);spec.loader.exec_module(counts)
for gid in (1510790,1510791,1510793):
 p=ROOT/f'data/online/smoke/one13-c2-old/M{gid}.replay'; meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 base=lr.scan(p,meta,str(p.parent),set()); root=lr.replay.load(p).root()
 lines=root.text(0).splitlines(); w,h=map(int,lines[0].split()[1:3]); raw=[]; bodies={};teams={}
 for l in lines:
  q=l.split()
  if q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
  if q and q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
 geo=counts.Geometry(w,h,raw); queens=base['queens'];qu=queens['us'];qt=queens['them']; qdeath=next((d for d in base['deaths'] if d['id']==qu),None)
 rnd=-1;actor=None; pearls=set();turns=[];current=None;near=[];latepos={};qturns=[]
 tile=lambda p: lr.replay.point(p)[1]*w+lr.replay.point(p)[0]
 def xy(c):return [c%w,c//w]
 def snapshot():return {i:list(b) for i,b in bodies.items()}
 def close():
  if current is not None:
   current['end']=list(bodies.get(current['id'],[]));turns.append(current)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);a=ev.pointer(0)
  if k==0:close();current=None;rnd=a.i32(0);actor=None
  elif k==1:
   close();actor=a.i32(0); current=dict(round=rnd,id=actor,side=teams[actor],body=list(bodies[actor]),eaten=0,steps=[],split=None)
   if actor in (qu,qt) or (qdeath and qdeath['round']-4<=rnd<=qdeath['round']):current['state']=snapshot();current['pearls']=list(pearls)
   if qdeath and rnd>=qdeath['round'] and qu not in bodies and qt in bodies:
    ds=geo.distances(bodies[qt][0]);pairs=[(ds[b[0]],i) for i,b in bodies.items() if teams[i]==0]
    if pairs:
     dist,i=min(pairs);near.append(dict(round=rnd,actor=actor,id=i,distance=dist,own=xy(bodies[i][0]),queen=xy(bodies[qt][0])))
    if actor==qt:latepos[rnd]=xy(bodies[qt][0])
  elif k==3:
   c=tile(a.pointer(0))
   if a.u32(0):pearls.add(c)
   else:pearls.remove(c);current['eaten']+=1
  elif k==4:
   action=a.pointer(0); current['action_kind']=action.u16(0) if action else None;current['dirs']=list(action.pointer(0)) if action and action.u16(0)==0 and action.pointer(0) is not None else []
  elif k==9:
   i=a.i32(0);hd=tile(a.pointer(0));tail=tile(a.pointer(1));b=bodies[i]
   if b[0]!=hd:current['steps'].append(xy(hd));b.appendleft(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   parent,child=a.i32(0),a.i32(4);current['split']=[parent,child]
   for z,i in enumerate((parent,child)):bodies[i]=deque(tile(pt) for pt in a.pointer(z));teams[i]=a.u16(8)
  elif k==11:bodies.pop(a.i32(0))
 close()
 ownq=[t for t in turns if t['id']==qu]
 data=dict(gid=gid,map=meta['mapName'],bots=base['bots'],queens=queens,final=base['final'],end_reason=base['end_reason'],last_round=base['last_round'],qdeath=qdeath,their_qdeath=next((d for d in base['deaths'] if d['id']==qt),None),snapshots=base['snapshots'],q_eats=base['q_eats'],q_splits=base['q_splits'],deaths=base['deaths'],last_qturns=ownq[-3:],approach_min=min(near,key=lambda z:z['distance']) if near else None,approach_first=next((z for z in near if z['distance']<=5),None),approach_turns=sum(z['distance']<=5 and teams[z['actor']]==0 for z in near),queen_positions=latepos,teams=teams,w=w,h=h)
 (OUT/f'{gid}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));(OUT/f'{gid}-turns.json').write_text(json.dumps(turns,separators=(',',':')))
 print(json.dumps({k:data[k] for k in ('gid','map','bots','queens','final','end_reason','last_round','qdeath','their_qdeath','q_eats','q_splits','approach_min','approach_first')},ensure_ascii=False))
