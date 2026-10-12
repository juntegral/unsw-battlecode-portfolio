import sys,ast,types,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,'tools'); import ladder_replay as lr
p=Path('data/analysis/ladder/dossier/work/tq2_scan.py'); t=ast.parse(p.read_text());t.body=t.body[:-1]; tq=types.ModuleType('tq');exec(compile(t,str(p),'exec'),tq.__dict__)
OUT=Path('data/codex/astra/sweep/1055/loss50')
JOBS=[(1512825,'data/online/live-one1/b1512823','B'),(1517686,'data/online/smoke/one14-c1-old','A'),(1517687,'data/online/smoke/one14-c1-old','A')]
for gid,folder,side in JOBS:
 qp=OUT/f'{gid}-queens.json'
 if not qp.exists(): continue
 q=json.loads(qp.read_text()); ledger=json.loads((OUT/f'{gid}-ledger.json').read_text()); qr=q['fate'][0]['r'] if q['fate'][0] else 500
 root=lr.replay.load(Path(folder)/f'M{gid}.replay').root();w,h=q['w'],q['h'];bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  a=line.split()
  if a[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(a[4+2*k])*w+int(a[3+2*k]) for k in range(int(a[2])));teams[i]=int('AB'[int(a[1])]!=side)
  elif a[0]=='EDGE':raw.append(tuple(map(int,a[1:4])))
 geo=tq.Geo(w,h,raw); pearls=set(); rnd=-1;actor=None;turn=None; turns=[]; boards=[]; logs=[]; after=[]; tally=[Counter(),Counter()];snap={}
 tile=lambda p:lr.replay.point(p)[1]*w+lr.replay.point(p)[0]
 def xy(c):return [c%w,c//w]
 def close():
  if turn is not None:
   turn['end']=xy(bodies[actor][0]) if actor in bodies else None;turn['end_length']=len(bodies.get(actor,())); turns.append(turn.copy())
 def snapshot():
  return [[len(bodies.get(q['queen'][s],())),max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),sum(len(b) for i,b in bodies.items() if teams[i]==s),sum(teams[i]==s for i in bodies),dict(tally[s])] for s in (0,1)]
 for ix,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close();turn=None;snap[rnd]=snapshot();rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);turn=dict(r=rnd,id=actor,side=teams[actor],head=xy(bodies[actor][0]),length=len(bodies[actor]),path=[],eat=0,action=None);tally[teams[actor]]['turns']+=1
   if actor==q['queen'][0] and qr-2<=rnd<=qr:
    hd=bodies[actor][0]; cx,cy=xy(hd); rows=[]; edge_rows=[]; occ={c:('Q' if i==actor and j==0 else 'q' if i==actor else 'A' if teams[i]==0 and j==0 else 'a' if teams[i]==0 else 'E' if j==0 else 'e') for i,b in bodies.items() for j,c in enumerate(b)}
    for dy in range(-3,4):
     rows.append(''.join(occ.get(((cy+dy)%h)*w+(cx+dx)%w,'*' if ((cy+dy)%h)*w+(cx+dx)%w in pearls else '.') for dx in range(-3,4)))
     edge_rows.append(' '.join(format(sum(1<<d for d,z in enumerate(geo.nxt[((cy+dy)%h)*w+(cx+dx)%w]) if z<0),'x') for dx in range(-3,4)))
    boards.append(dict(round=rnd,head=xy(hd),length=len(bodies[actor]),board=rows,walls_hex=edge_rows,near=[dict(id=i,side=teams[i],body=[xy(c) for c in b]) for i,b in bodies.items() if geo.ball(hd).get(b[0],99)<=8]))
   if rnd>qr and teams[actor]==0 and q['queen'][1] in bodies:
    dist=geo.ball(bodies[actor][0]).get(bodies[q['queen'][1]][0],99)
    if dist<=5:after.append(dict(round=rnd,id=actor,distance=dist))
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.discard(c);turn['eat']+=1;tally[teams[actor]]['eats']+=1
  elif k==4:
   a=p.pointer(0);typ=a.u16(0) if a else 2;turn['action']=typ
   turn['dirs']=list(a.pointer(0)) if a and typ==0 and a.pointer(0) is not None else []
   tally[teams[actor]][['move','split','none'][min(typ,2)]]+=1
  elif k==6 and actor==q['queen'][0] and qr-2<=rnd<=qr:logs.append([rnd,p.text(0)])
  elif k==9:
   i=p.i32(0);hd=tile(p.pointer(0));tl=tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:
    b.appendleft(hd)
    if i==actor:turn['path'].append(xy(hd))
   while len(b)>1 and b[-1]!=tl:b.pop()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=int('AB'[p.u16(8)]!=side)
  elif k==11:bodies.pop(p.i32(0))
 close();snap[rnd]=snapshot()
 losing=[r for r,ss in snap.items() if r>=0 and tuple(ss[0][:3])>=tuple(ss[1][:3])]
 out=dict(boards=boards,queen_logs=logs,after_close=after,snapshots=snap,permanent_score_deficit_from=max(losing)+1 if losing else 0,turns=turns,final_bodies={i:dict(side=teams[i],body=[xy(c) for c in b]) for i,b in bodies.items()})
 (OUT/f'{gid}-evidence.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
 print(gid,'permanent deficit',out['permanent_score_deficit_from'],'boards',boards,'logs',logs,flush=True)
