import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0,'tools')
from ladder_replay import replay
P=Path(__file__).resolve().parent

def one(pair):
    key=pair['key'];g=json.loads((P/f'mJo5_vb--{key}.json').read_text());root=replay.load(g['path']).root();b={};s={};own=int(key[-1]);stop=pair['first']['round']
    for l in root.text(0).splitlines():
        q=l.split()
        if q and q[0]=='DRAGON':
            i=len(b);b[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));s[i]=int(int(q[1])!=own)
    queens=[min(i for i in b if s[i]==sd) for sd in (0,1)]
    for e in root.pointer(3):
        k=e.u16(0);p=e.pointer(0)
        if k==0 and p.i32(0)==stop:break
        if k==9:
            i=p.i32(0);h,tail=replay.point(p.pointer(0)),replay.point(p.pointer(1));bb=b[i]
            if bb[0]!=h:bb.appendleft(h)
            while len(bb)>1 and bb[-1]!=tail:bb.pop()
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):b[i]=deque(replay.point(c) for c in p.pointer(z));s[i]=int(p.u16(8)!=own)
        elif k==11:b.pop(p.i32(0))
    snaps=[]
    for sd in (0,1):
        lengths=[len(bb) for i,bb in b.items() if s[i]==sd]
        snaps.append([len(lengths),sum(lengths),max(lengths,default=0),len(b.get(queens[sd],()))])
    return key,dict(round=stop-1,snaps=snaps)

if __name__=='__main__':
    ps=[p for p in json.loads((P/'pairs.json').read_text()) if p['a']=='mJo5_vb' and p['b']=='mDone8' and p['result_a']=='win' and p['result_b']=='loss']
    with ProcessPoolExecutor(max_workers=2) as pool:out=dict(pool.map(one,ps))
    (P/'boundary-states.json').write_text(json.dumps(out,indent=2))
