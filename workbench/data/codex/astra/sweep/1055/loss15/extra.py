import sys,json,ast
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter,deque
p=Path(__file__).parent
ns={'__file__':str(p/'analyze.py')}; a=ast.parse((p/'analyze.py').read_text()); a.body=a.body[:-1];exec(compile(a,'analyze.py','exec'),ns)
replay=ns['replay'];Geo=ns['Geo']
out={}
for gid in range(1504018,1504021):
 root=replay.load(Path(f'data/online/live-one1/b1504016/M{gid}.replay')).root();lines=root.text(0).splitlines();w,h=map(int,lines[0].split()[1:3]);raw=[];teams={};heads={}
 for l in lines:
  s=l.split()
  if s[0]=='DRAGON':i=len(teams);teams[i]=int(s[1]);heads[i]=(int(s[3]),int(s[4]))
  elif s[0]=='EDGE':raw.append(tuple(map(int,s[1:])))
 geo=Geo(w,h,raw);r=0;actor=None;dirs=[];step=0;cross=Counter();moves=Counter();logs=[];selected=[];qt=Counter();own=1
 for ev in root.pointer(3):
  k=ev.u16(0)
  if k not in (0,1,4,9,10,11) and replay.EVENT_NAMES[k] != "dragonLog":continue
  v=ev.pointer(0)
  if k==0:r=v.i32(0)
  elif k==1:actor=v.i32(0);dirs=[];step=0
  elif k==4:
   action=v.pointer(0);dirs=list(action.pointer(0)) if action and action.u16(0)==0 and action.pointer(0) is not None else []
   if (gid==1504019 and actor in (0,1613,1651,1721,1894) and r>=427) or (gid==1504018 and actor==1 and r in (13,35,36,37)):
    selected.append(dict(r=r,id=actor,head=heads.get(actor),dirs=dirs,action=action.u16(0) if action else None))
   if r<=100:qt[f'{teams[actor]}-turns']+=1;qt[f'{teams[actor]}-split']+=int(action and action.u16(0)==1)
  elif k==9:
   i=v.i32(0);hd=replay.point(v.pointer(0));old=heads[i]
   if hd!=old:
    if i==actor and step<len(dirs):
     if r<=100:cross[str(teams[i])]+=geo.por[old[1]*w+old[0]][dirs[step]];moves[str(teams[i])]+=1
     step+=1
    heads[i]=hd
  elif k==10:
   for j,i in enumerate((v.i32(0),v.i32(4))):teams[i]=v.u16(8);heads[i]=replay.point(next(iter(v.pointer(j))))
  elif k==11:heads.pop(v.i32(0))
  elif replay.EVENT_NAMES[k]=="dragonLog":
   if v.i32(0) in (0,1) and (r>=425 or (gid==1504018 and r>=34) or (gid==1504020 and 130<=r<=135)):logs.append([r,v.i32(0),v.text(0)])
 out[gid]=dict(portals100=dict(cross),steps100=dict(moves),turns100=dict(qt),selected=selected,logs=logs)
 print(gid,dict(cross),dict(moves),dict(qt),flush=True)
(p/'extra.json').write_text(json.dumps(out))
