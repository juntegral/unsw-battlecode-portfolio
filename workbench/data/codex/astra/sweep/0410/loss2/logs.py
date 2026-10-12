import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from scoreboard import load_replay
OUT=Path(__file__).resolve().parent
specs={1485657:('data/online/live-one1/b1485657',{0:(358,362),533:(400,460),595:(453,499)}),1485169:('data/online/smoke/one8-k1-old',{1:(387,393),371:(409,417),387:(400,499)}),1485170:('data/online/smoke/one8-k1-old',{0:(69,73),9:(72,73),100:(73,73),640:(260,262),518:(400,499)}),1485174:('data/online/smoke/one8-k1-old',{0:(193,196),414:(193,196)}),1485180:('data/online/smoke/one8-k1-old',{0:(0,499)})}
for gid,(folder,ids) in specs.items():
 root=load_replay(Path(folder)/f'M{gid}.replay').root();r=-1;out=[]
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:r=p.i32(0)
  if k not in (6,10):continue
  i=p.i32(0)
  if i not in ids or not ids[i][0]<=r<=ids[i][1]:continue
  if k==6:out.append(dict(r=r,id=i,event=idx,log=p.text(0)))
  else:out.append(dict(r=r,id=i,event=idx,split=[p.i32(0),p.i32(4)]))
 (OUT/f'{gid}-logs.json').write_text(json.dumps(out))
 print(gid,len(out))
 print(out if gid!=1485180 and gid!=1485657 and gid!=1485170 else out[:8])
