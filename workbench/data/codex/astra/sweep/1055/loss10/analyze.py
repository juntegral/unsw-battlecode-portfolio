import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter,defaultdict
sys.path.insert(0,'tools')
import ladder_replay as lr
O=Path('data/codex/astra/sweep/1055/loss10')
for gid in (1504147,1504148,1504149):
 ledger=json.loads((O/f'{gid}-ledger.json').read_text());root=lr.replay.load(f'data/online/live-one1/b1504147/M{gid}.replay').root()
 W,H=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={};teams={};edges=[]
 for l in root.text(0).splitlines():
  q=l.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]='AB'[int(q[1])]
  elif q[0]=='EDGE':edges.append(tuple(map(int,q[1:4])))
 edges=lr.canonical_edges(W,H,edges); qs=ledger['queens'];qd=next((d for d in ledger['deaths'] if d['id']==qs['us']),None)
 attack=qd['actor'] if qd else -1;turns=[];pearls=set();rnd=-1;t=None;detail=[];counts=Counter();positions=defaultdict(set);eatid=Counter();moves=Counter();splits=[]
 def state():return {i:list(b) for i,b in bodies.items()}
 def flush():
  if t is None:return
  t['end']=list(bodies.get(t['id'],[]));t['Lend']=len(t['end']);turns.append(t)
 for idx,e in enumerate(root.pointer(3)):
  k=e.u16(0);p=e.pointer(0)
  if k==0:flush();t=None;rnd=p.i32(0)
  elif k==1:
   flush();i=p.i32(0);t=dict(r=rnd,id=i,side=teams[i],L=len(bodies[i]),start=list(bodies[i]),steps=[],eats=[],logs=[],dirs=[])
   if i==qs['us'] or (qd and rnd>=qd['round']-3 and i==attack):t.update(state=state(),pearls=list(pearls))
   if rnd<=100:positions[i].add(bodies[i][0])
  elif k==3:
   xy=lr.replay.point(p.pointer(0))
   if p.u32(0):pearls.add(xy)
   else:
    pearls.remove(xy);t['eats'].append(xy);eatid[t['id']]+=1
  elif k==4:
   a=p.pointer(0);t['action']=a.u16(0) if a else None
   if a and a.u16(0)==0:t['dirs']=list(a.pointer(0)) if a.pointer(0) else []
  elif k==6:t['logs'].append(p.text(0))
  elif k==9:
   i=p.i32(0);h=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i]
   if h!=b[0]:b.appendleft(h);t['steps'].append(h);moves[i]+=1
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   splits.append(dict(r=rnd,parent=p.i32(0),child=p.i32(4),before=t['L']))
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]='AB'[p.u16(8)]
  elif k==11:
   if p.i32(0)==qs['us']:detail.append(dict(deathstate=state(),pearls=list(pearls),actor=t))
   bodies.pop(p.i32(0))
 flush()
 qturn=[t for t in turns if t['id']==qs['us']]
 selected=qturn[-3:] if qd else [t for t in qturn if t['r'] in (0,25,100,200,300,400,499)]
 selected +=[t for t in turns if qd and t['id']==attack and t['r']>=qd['round']-2]
 def lead(s):return (s['queen_length'],s['longest'],s['total'])
 snapshots=ledger['snapshots'];lastnot=max((int(r) for r,s in snapshots.items() if lead(s['us'])>=lead(s['them'])),default=-1)
 bands={}
 for lo,hi in ((0,100),(101,200),(201,300),(301,400),(401,499)):
  bands[f'{lo}-{hi}']={s:dict(turns=sum(t['side']==s and lo<=t['r']<=hi for t in turns),eats=sum(len(t['eats']) for t in turns if t['side']==s and lo<=t['r']<=hi),zero=sum(not t['eats'] for t in turns if t['side']==s and lo<=t['r']<=hi)) for s in 'BA'}
 initial=[dict(id=i,side=teams[i],unique100=len(pos),pearls100=sum(len(t['eats']) for t in turns if t['id']==i and t['r']<=100),pearls=eatid[i],moves=moves[i]) for i,pos in positions.items() if i<10]
 output=dict(gid=gid,W=W,H=H,edges=list((e,*v) for e,v in edges.items()),selected=selected,death=detail,lastnot=lastnot,bands=bands,initial=initial,splits=splits,final_bodies=state(),qstats=dict(turns=len(qturn),unique=len(set(tuple(t['start'][0]) for t in qturn)),eats=sum(len(t['eats']) for t in qturn)))
 (O/f'{gid}-details.json').write_text(json.dumps(output))
 (O/f'{gid}-turns.json').write_text(json.dumps([{k:v for k,v in t.items() if k not in ('state','pearls')} for t in turns]))
 print(gid,'lastnot',lastnot,'bands',bands,'initial',initial,'qstats',output['qstats'])
 for t in selected:print('SELECT', {k:v for k,v in t.items() if k not in ('state','pearls')})
 print('queen split',[s for s in splits if s['parent']==qs['us']])
