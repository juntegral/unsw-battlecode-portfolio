import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from collections import deque,Counter,defaultdict
sys.path[:0]=['tools','data/analysis/ladder/dossier/local','data/analysis/ladder/dossier']
import scoreboard as sb
import ladder_replay as lr
from count_dossier import Geo
OUT=Path(__file__).resolve().parent
JOBS=[(1516202,1516202),(1516204,1516202),(1516205,1516202),(1516987,1516986),(1516989,1516986),(1516555,1516554),(1516556,1516554),(1516557,1516554)]
MASK=(1<<64)-1; CHECK=255<<55; TAG=3<<53
rot=lambda x,b:((x<<b)|(x>>(64-b)))&MASK
def prf(key,m):
 v0=key[0]^0x736f6d6570736575;v1=key[1]^0x646f72616e646f6d;v2=key[0]^0x6c7967656e657261;v3=key[1]^0x7465646279746573
 def rounds(n):
  nonlocal v0,v1,v2,v3
  for _ in range(n):
   v0=(v0+v1)&MASK;v1=rot(v1,13)^v0;v0=rot(v0,32);v2=(v2+v3)&MASK;v3=rot(v3,16)^v2;v0=(v0+v3)&MASK;v3=rot(v3,21)^v0;v2=(v2+v1)&MASK;v1=rot(v1,17)^v2;v2=rot(v2,32)
 v3^=m;rounds(2);v0^=m;tail=8<<56;v3^=tail;rounds(2);v0^=tail;v2^=255;rounds(4);return v0^v1^v2^v3
assert prf((0x0706050403020100,0x0f0e0d0c0b0a0908),0x0706050403020100)==0x93f5f5799a932462
secret=0xE1DE70530C48DE42
rootkey=(secret,rot(secret,29)^0xa5a5a5a5a5a5a5a5)
def open_wire(key,wire):
 check=(wire&CHECK)>>55;plain=(wire&~CHECK)^ (prf(key,CHECK|check)&~(CHECK|TAG)&MASK)
 return plain if prf(key,plain&~CHECK)&255==check else None

def one(gid,bid):
 path=Path(f'data/online/live-one1/b{bid}/M{gid}.replay');meta=json.loads(path.with_name(f'game-{gid}.json').read_text())
 loaded=sb.load_replay(path);root=loaded.root();orig=lr.replay.load;lr.replay.load=lambda _:loaded
 try: base=lr.scan(path,meta,str(path.parent),set())
 finally: lr.replay.load=orig
 assert root.text(2)=='21497' and base['ours']=='B' and base['winner']=='B'
 lines=root.text(0).splitlines();w,h=map(int,lines[0].split()[1:3]);bodies={};teams={};raw=[]
 for line in lines:
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 geo=Geo(w,h,raw);queens={s:min(i for i in teams if teams[i]==s) for s in (0,1)}
 keydata=(w<<40)|(h<<16)|1;key=(prf(rootkey,keydata),prf(rootkey,keydata|1<<63))
 def point(p):
  x,y=lr.replay.point(p);return y*w+x
 def xy(c):return [c%w,c//w]
 def visible(a,b):return geo.visible(a,b)
 def short(t):return {k:t[k] for k in ('round','id','length','head','end_head','steps','eaten','action','dirs','queen','units','enemyq','adj_enemies','end_adj','pearl_neighbors','pearl_taken','alive_end')}
 turns=[];splits=[];sonar=[];rnd=-1;actor=None;turn=None;pearls=set();counts=Counter();samehead=Counter();lastheads={}
 def adjacent_enemies(head):return [{'id':i,'length':len(b),'head':xy(b[0])} for i,b in bodies.items() if teams[i]==0 and any(k!=1 and d==head for k,d in geo.moves[b[0]])]
 def close():
  nonlocal turn
  if turn is None:return
  i=turn['id'];turn['alive_end']=i in bodies;turn['end_head']=xy(bodies[i][0]) if i in bodies else None
  turn['end_adj']=adjacent_enemies(bodies[i][0]) if i in bodies and turn['queen'] else []
  if teams[i]==1:
   counts['turns']+=1;counts['stops']+=turn['steps']==0 and turn['action']==0;counts['missed_adjacent']+=bool(turn['pearl_neighbors']) and not turn['pearl_taken'] and turn['action']==0
   if turn['queen']:
    counts['queen_turns']+=1;counts['queen_L'+('4plus' if turn['length']>=4 else str(turn['length']))]+=1
    counts['queen_end_adj']+=bool(turn['end_adj'])
   turns.append(short(turn))
  turn=None
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:close();rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);b=bodies[actor];hd=b[0]
   occ={c for bb in bodies.values() for c in bb};ns=[d for kind,d in geo.moves[hd] if kind!=1 and d in pearls and d not in occ]
   turn=dict(round=rnd,id=actor,length=len(b),head=xy(hd),end_head=None,steps=0,eaten=0,action=None,dirs=[],queen=actor==queens[teams[actor]],units=sum(teams[i]==teams[actor] for i in bodies),enemyq=len(bodies.get(queens[1-teams[actor]],())),adj_enemies=adjacent_enemies(hd) if teams[actor]==1 and actor==queens[1] else [],end_adj=[],pearl_neighbors=[xy(c) for c in ns],pearl_taken=False,alive_end=True)
  elif k==3:
   c=point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:
    pearls.remove(c)
    if turn:turn['eaten']+=1;turn['pearl_taken']|=xy(c) in turn['pearl_neighbors']
  elif k==4:
   a=p.pointer(0);turn['action']=a.u16(0);turn['dirs']=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==9:
   i=p.i32(0);hd=point(p.pointer(0));tl=point(p.pointer(1));b=bodies[i]
   if b[0]!=hd:
    old=b[0];b.appendleft(hd)
    if i==actor:
     d=turn['dirs'][turn['steps']] if turn['steps']<len(turn['dirs']) else None
     if d is not None and geo.moves[old][d][0]==2 and teams[i]==1:counts['portal_steps']+=1;sonar.append(dict(type='portal',round=rnd,id=i,length=len(b)-1,from_=xy(old),to=xy(hd)))
     turn['steps']+=1
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   parent=p.i32(0);child=p.i32(4);before=list(bodies[parent]);tail=before[-1]
   rec=dict(round=rnd,id=parent,child=child,length=len(before),units=sum(teams[i]==teams[parent] for i in bodies),queen=parent==queens[teams[parent]],tail_portal=any(k==2 for k,d in geo.moves[tail]))
   for z,i in enumerate((parent,child)):bodies[i]=deque(point(c) for c in p.pointer(z));teams[i]=p.u16(8)
   rec['keep']=len(bodies[parent]);rec['child_length']=len(bodies[child])
   if teams[parent]==1:splits.append(rec)
  elif k==11:bodies.pop(p.i32(0))
  elif k==12 and actor is not None and teams[actor]==1:
   plain=open_wire(key,p.u64(16))
   if plain is not None and plain>>63 and (plain>>38)&0x7fff==0x5b:
    landing=point(p.pointer(1));recipient=next((i for i,b in bodies.items() if landing in b),None)
    sonar.append(dict(type='far_head',round=rnd,id=actor,when=(plain>>28)&0x1ff,head=xy(plain&0x3fff),parts=((plain>>14)&0x3fff)+1,landing=xy(landing),recipient=recipient,queen_hit=recipient==queens[1],hitkind=p.u16(24)))
 close()
 snapshots=base['snapshots']
 def score(s):return (int(s['alive']>0),s['queen_length'],s['longest'],s['total'])
 rr=sorted(snapshots);good=[score(snapshots[r]['us'])>score(snapshots[r]['them']) for r in rr];start=len(rr)-1
 while start>0 and good[start-1]:start-=1
 assert good[-1]
 lead=rr[start]
 queen_deaths=[d for d in base['deaths'] if d['id'] in queens.values()]
 rams=[c for c in base['collisions'] if c['cross_team'] and any(d['actor']==d['id'] and d['side']=='us' for d in base['deaths'] if d['death'] in c['deaths'])]
 result=dict(gid=gid,map=meta['mapName'],opponent=meta['teamAName'],bot=21497,replay=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),last_round=base['last_round'],end_reason=base['end_reason'],final=base['final'],ahead_for_good=lead,queens=queens,queen_deaths=queen_deaths,counts=dict(counts),splits=splits,sonar=sonar,eats=base['eats'],deaths=base['deaths'],collisions=base['collisions'],checkpoints={str(r):snapshots[r] for r in rr if r in [0,10,50,100,150,200,250,300,350,400,450,499,500,lead]},queen_adj=[t for t in turns if t['queen'] and t['end_adj']],misses=[t for t in turns if t['pearl_neighbors'] and not t['pearl_taken'] and t['action']==0],stops=[t for t in turns if t['steps']==0 and t['action']==0],queen_turns=[t for t in turns if t['queen']])
 (OUT/f'{gid}.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
 (OUT/f'{gid}-turns.jsonl').write_text(''.join(json.dumps(t,separators=(',',':'))+'\n' for t in turns))
 print(json.dumps({k:result[k] for k in ['gid','map','last_round','end_reason','final','ahead_for_good','queen_deaths','counts']},ensure_ascii=False),flush=True)
 return result
if __name__=='__main__':
 rows=[one(*j) for j in JOBS]
 (OUT/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':'))+'\n')
