import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
from ladder_replay import replay
from pathlib import Path
D=Path('data/analysis/ladder/dossier');W=D/'work'
def scan(row):
 root=replay.load(Path(row['replay'])).root();heads={};teams={};w,h=row['width'],row['height'];mine=row['side'];queen=row['queen']['id']
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':i=len(heads);heads[i]=(int(q[3]),int(q[4]));teams[i]='AB'[int(q[1])]
 def dist(a,b):
  dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,w-dx)+min(dy,h-dy)
 def snap():
  if queen not in heads:return None
  q=heads[queen];enemy=[z for i,z in heads.items() if teams[i]!=mine];friends=[z for i,z in heads.items() if i!=queen and teams[i]==mine]
  if not enemy:return None
  ne=min(dist(q,z) for z in enemy);closest=[z for z in enemy if dist(q,z)==ne]
  return int(any(dist(f,e)<ne for f in friends for e in closest))
 rnd=0;out={'0':snap()}
 for ev in root.pointer(3):
  k=ev.u16(0)
  if k not in (0,9,10,11):continue
  p=ev.pointer(0)
  if k==0:
   nxt=p.i32(0)
   if nxt>rnd and rnd in (10,20,30,40,60,80,100,150):out[str(rnd)]=snap()
   rnd=nxt
   if rnd>150:break
  elif k==9:heads[p.i32(0)]=replay.point(p.pointer(0))
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):heads[i]=replay.point(next(iter(p.pointer(z))));teams[i]='AB'[p.u16(8)]
  elif k==11:heads.pop(p.i32(0))
 else:
  if rnd in (10,20,30,40,60,80,100,150):out[str(rnd)]=snap()
 return out
shard=int(sys.argv[1]);nsh=3;rows=[]
for who,f in [('O','per-game.jsonl'),('R','target/per-game-top1.jsonl')]:
 for line in (D/f).open():
  r=json.loads(line)
  if r['relation']=='us':rows.append((who,r))
with (W/f'qp_screen_{shard}.jsonl').open('w') as f:
 for n,(who,r) in enumerate(rows):
  if n%nsh!=shard:continue
  f.write(json.dumps({'who':who,'game':r['game'],'screen':scan(r)})+'\n');f.flush()
print('done',shard)
