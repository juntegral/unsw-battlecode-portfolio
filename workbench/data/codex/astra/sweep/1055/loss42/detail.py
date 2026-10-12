import sys,json,ast
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
import ladder_replay as lr
sys.path.insert(0,"data/analysis/ladder/dossier/local")
import scoreboard
lr.replay.load=scoreboard.load_replay
from pathlib import Path
from collections import deque,defaultdict,Counter
OUT=Path('data/codex/astra/sweep/1055/loss42');FOLDER=Path('data/online/live-one1/b1514288')
a=ast.parse(Path('data/analysis/ladder/dossier/work/tq2_scan.py').read_text());ns=dict(canonical_edges=lr.canonical_edges,edge_id=lr.edge_id,defaultdict=defaultdict,deque=deque,STEP=((0,-1),(1,0),(0,1),(-1,0)),CAP=8)
exec(compile(ast.Module(body=[n for n in a.body if isinstance(n,ast.ClassDef) and n.name=='Geo'],type_ignores=[]),'tq2_scan.py','exec'),ns);Geo=ns['Geo']
for gid in (1514288,1514290,1514291):
 s=json.loads((OUT/f'{gid}-base.json').read_text());root=lr.replay.load(FOLDER/f'M{gid}.replay').root();w,h=map(int,s['text'].splitlines()[0].split()[1:3]);b={};team={};raw=[];pearls=set()
 for line in s['text'].splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(b);b[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));team[i]='AB'[int(q[1])]
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
  elif q[0]=='TILE' and int(q[3])==1:pearls.add((int(q[1]),int(q[2])))
 geo=Geo(w,h,raw);oq=s['queens']['us'];eq=s['queens']['them'];rnd=-1;actor=None;t={"steps":[],"eats":0};turns=[];qt=[];close=[];eqpos=[];splits=[];nearmin=999
 def cell(p):return p[1]*w+p[0]
 def board(p):
  occ={c:('Q' if i==oq and k==0 else 'K' if i==eq and k==0 else 'A' if team[i]=='B' and k==0 else 'E' if k==0 else 'q' if i==oq else 'a' if team[i]=='B' else 'e') for i,bb in b.items() for k,c in enumerate(bb)}
  rows=[]
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    xy=((p[0]+dx)%w,(p[1]+dy)%h);mask=sum(1<<d for d in range(4) if geo.nxt[cell(xy)][d]<0);row.append(occ.get(xy,'*' if xy in pearls else '.')+format(mask,'x'))
   rows.append(' '.join(row))
  return rows
 def monitor(ix):
  global nearmin
  if oq not in b and eq in b:
   ec=cell(b[eq][0]);eqpos.append((rnd,*b[eq][0]));best=None
   for i,bb in b.items():
    if team[i]!='B':continue
    d=geo.ball(cell(bb[0])).get(ec,999)
    if d<nearmin:nearmin=d
    if d<=5 and best is None:best={'round':rnd,'event':ix,'id':i,'distance':d,'head':bb[0],'enemy_queen':b[eq][0]}
   if best and (not close or close[-1]['round']!=rnd):close.append(best)
 for ix,ev in enumerate(root.pointer(3)):
  kind=ev.u16(0);p=ev.pointer(0)
  if kind==0:rnd=p.i32(0)
  elif kind==1:
   actor=p.i32(0);t={'round':rnd,'id':actor,'length':len(b[actor]),'head':b[actor][0],'steps':[],'eats':0};turns.append(t)
   if actor==oq or actor in {1514288:{718,737,722,112},1514290:{783,744,587},1514291:{26}}[gid]:
    t['board']=board(b[actor][0]);t['near']=[(i,len(bb),bb[0]) for i,bb in b.items() if i!=actor and geo.ball(cell(b[actor][0])).get(cell(bb[0]),999)<=8];t['body']=list(b[actor]);
   if actor==oq:qt.append(t)
   monitor(ix)
  elif kind==4:
   ac=p.pointer(0);t['actiontype']=ac.u16(0) if ac else None;t['dirs']=list(ac.pointer(0)) if ac and ac.u16(0)==0 and ac.pointer(0) is not None else []
  elif kind==3:
   xy=lr.replay.point(p.pointer(0))
   if p.u32(0):pearls.add(xy)
   else:pearls.discard(xy);t['eats']+=1
  elif kind==9:
   i=p.i32(0);hd=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));bb=b[i]
   if bb[0]!=hd:bb.appendleft(hd);t['steps'].append(hd)
   while len(bb)>1 and bb[-1]!=tail:bb.pop()
   assert bb[-1]==tail
   t['endlength']=len(bb);monitor(ix)
  elif kind==10:
   parent,child=p.i32(0),p.i32(4);splits.append({'round':rnd,'parent':parent,'child':child,'before':len(b[parent])})
   for z,i in enumerate((parent,child)):b[i]=deque(lr.replay.point(x) for x in p.pointer(z));team[i]='AB'[p.u16(8)]
   t['split']=[parent,child,len(b[parent]),len(b[child])]
  elif kind==11:
   i=p.i32(0)
   if i==oq:
    t['queen_death']=True;t['at_death_board']=board(b[i][0]);t['queen_body']=list(b[i])
   b.pop(i);monitor(ix)
 summary={'gid':gid,'last_queen_turns':qt[-3:],'queen_death_turns':[t for t in turns if t.get('queen_death')],'near_after':close,'nearest_after_capped8':nearmin,'enemy_queen_positions':list(dict.fromkeys(eqpos)),'queen_splits':[x for x in splits if x['parent']==oq],'queen_turns':qt,'turns':turns}
 (OUT/f'{gid}-detail.json').write_text(json.dumps(summary))
 print(gid,'last',qt[-3:],'death turns',summary['queen_death_turns'],'afternear',close[:2],len(close),'min',nearmin,flush=True)
