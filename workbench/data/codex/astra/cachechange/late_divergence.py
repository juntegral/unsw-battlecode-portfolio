import sys,json
sys.dont_write_bytecode=True
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,'tools')
from ladder_replay import replay
P=Path(__file__).parent
def events(g):
    r=replay.load(Path('data/online/smoke',g['src']+'-old',f'M{g["gid"]}.replay')).root()
    teams={};out=defaultdict(list);rnd=-1;actor=None
    for line in r.text(0).splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':teams[len(teams)]=int(q[1])
    for e in r.pointer(3):
        k=e.u16(0);p=e.pointer(0)
        if k==0:rnd=p.i32(0)
        elif k==1:actor=p.i32(0)
        elif k==4:
            a=p.pointer(0);out[rnd].append([teams[actor],actor,'action',a.u16(0),list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []])
        elif k==9:out[rnd].append([teams[p.i32(0)],p.i32(0),'update',replay.point(p.pointer(0)),replay.point(p.pointer(1))])
        elif k==10:
            teams[p.i32(4)]=p.u16(8)
            out[rnd].append([teams[actor],actor,'split',p.i32(4),[replay.point(c) for c in p.pointer(0)],[replay.point(c) for c in p.pointer(1)]])
        elif k==11:out[rnd].append([teams[p.i32(0)],p.i32(0),'death',p.u16(4)])
    return out
gs=[json.loads((P/f'{gid}.json').read_text()) for gid in [1484429,1493877]]
a,b=map(events,gs)
out={}
for s in [None,0,1]:
    for rnd in sorted(set(a)|set(b)):
        x=[e for e in a[rnd] if s is None or e[0]==s];y=[e for e in b[rnd] if s is None or e[0]==s]
        if x!=y:
            out[str(s)]={'r':rnd,'a':x,'b':y};break
(P/'late-divergence.json').write_text(json.dumps(out,indent=2))
print(out)
