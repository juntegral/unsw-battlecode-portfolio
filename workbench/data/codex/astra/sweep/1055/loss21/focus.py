import sys
sys.dont_write_bytecode = True
import json
from collections import deque
from pathlib import Path
sys.path.insert(0,'data/analysis/ladder/dossier/local')
import scoreboard as sb
OUT=Path(__file__).resolve().parent

for gid in (1510785,1510786):
    root=sb.load_replay(Path(f'data/online/smoke/one13-c2-old/M{gid}.replay')).root()
    bodies={};teams={};pearls=set();records=[];rnd=-1;actor=None
    for line in root.text(0).splitlines():
        p=line.split()
        if p and p[0]=='DRAGON':
            i=len(bodies);bodies[i]=deque((int(p[3+2*k]),int(p[4+2*k])) for k in range(int(p[2])));teams[i]=int(p[1])
    q=min(i for i in bodies if teams[i]==0)
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:rnd=p.i32(0)
        elif k==1:
            actor=p.i32(0)
            select=(actor==q and (265<=rnd<=285 if gid==1510785 else 290<=rnd<=314)) or (gid==1510786 and actor in (967,926) and 470<=rnd<=475) or (gid==1510785 and actor==1036 and rnd==485)
            if select:records.append({'round':rnd,'event':idx,'actor':actor,'bodies':{str(i):list(b) for i,b in bodies.items()},'teams':teams.copy(),'pearls':list(pearls)})
        elif k==3:
            c=sb.replay_format.point(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:pearls.remove(c)
        elif k==9:
            b=bodies[p.i32(0)];hd=sb.replay_format.point(p.pointer(0));tail=sb.replay_format.point(p.pointer(1))
            if b[0]!=hd:b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):
                bodies[i]=deque(sb.replay_format.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
        elif k==11:bodies.pop(p.i32(0))
    (OUT/f'{gid}-focus.json').write_text(json.dumps(records))
    print(gid,len(records),flush=True)
