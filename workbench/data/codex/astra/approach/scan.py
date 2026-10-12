"""Read-only replay audit. Run from repository root with python3 -B.

D2: nearest visible pearl is exactly two currently unoccupied steps away.
Enemy exclusion uses open-edge/portal graph distance <=4, ignoring bodies.
Direction uses FIRST successful step and frozen starting occupancy, with the
old head released. Multiple nearest pearls are treated as one target set.
"""
import sys, json, re
sys.dont_write_bytecode = True
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work']
from ladder_replay import replay, edge_id, canonical_edges
from o1_scan import STEP
from collections import deque, defaultdict, Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
RUNS = Path.home() / 'meow-redteam/solo/runs'

class Board:
    def __init__(self, path):
        self.root = replay.load(path).root()
        lines = self.root.text(0).splitlines()
        self.W, self.H = map(int, lines[0].split()[1:3])
        self.bodies, self.teams, raw = {}, {}, []
        for line in lines:
            q = line.split()
            if q and q[0] == 'DRAGON':
                i = len(self.bodies)
                self.bodies[i] = deque((int(q[3+2*k]), int(q[4+2*k])) for k in range(int(q[2])))
                self.teams[i] = int(q[1])
            elif q and q[0] == 'EDGE': raw.append(tuple(map(int,q[1:4])))
        self.edges = canonical_edges(self.W, self.H, raw)
        portals = defaultdict(list)
        for e,(kind,pid) in self.edges.items():
            if kind == 2: portals[pid].append(e)
        self.adj = {}
        for y in range(self.H):
            for x in range(self.W):
                ds = []
                for d,(dx,dy) in enumerate(STEP):
                    e = edge_id(self.W,self.H,x,y,d)
                    kind,pid = self.edges.get(e,(0,-1))
                    if kind == 1: n = None
                    elif kind == 2:
                        partner = next(z for z in portals[pid] if z != e)
                        row,px = divmod(partner,self.W+1)
                        n = ((px-(d==3))%self.W,(row//2-(d==0))%self.H)
                    else: n = ((x+dx)%self.W,(y+dy)%self.H)
                    ds.append(n)
                self.adj[x,y] = ds
        self.pearls = set()
        self.rnd = -1
        self.actor = None

    def view(self,h,c):
        return min((c[0]-h[0])%self.W,(h[0]-c[0])%self.W)<=3 and min((c[1]-h[1])%self.H,(h[1]-c[1])%self.H)<=3

    def flood(self,h,cap,occ=frozenset()):
        seen={h:0}; q=deque([h])
        while q:
            c=q.popleft()
            if seen[c]>=cap: continue
            for n in self.adj[c]:
                if n is not None and n not in seen and n not in occ:
                    seen[n]=seen[c]+1; q.append(n)
        return seen

    def update(self,k,p):
        if k==0: self.rnd=p.i32(0)
        elif k==1: self.actor=p.i32(0)
        elif k==3:
            c=replay.point(p.pointer(0))
            if p.u32(0): self.pearls.add(c)
            else: self.pearls.discard(c)
        elif k==9:
            b=self.bodies[p.i32(0)]
            h,t=replay.point(p.pointer(0)),replay.point(p.pointer(1))
            if b[0]!=h: b.appendleft(h)
            while len(b)>1 and b[-1]!=t: b.pop()
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):
                self.bodies[i]=deque(replay.point(c) for c in p.pointer(z)); self.teams[i]=p.u16(8)
        elif k==11: self.bodies.pop(p.i32(0))

    def snap(self):
        return dict(bodies={str(i):list(b) for i,b in self.bodies.items()}, teams=self.teams, pearls=list(self.pearls))

def inventory():
    out=[]
    for label in ('one4-w1','one4-d1','one5-w1','one5-c1','one5-d1'):
        folder=Path('data/online/smoke')/(label+'-old')
        for mp in sorted(folder.glob('game-*.json')):
            j=json.loads(mp.read_text()); path=folder/('M%d.replay'%j['id'])
            if path.exists(): out.append(dict(label=label,path=str(path),game=str(j['id']),own=0 if j['teamAId']==1119 else 1,map=j['mapName']))
    seen={j['game'] for j in out}
    for mp in sorted(Path('data/online/live-one1').glob('b*/game-*.json')):
        j=json.loads(mp.read_text())
        if str(j['id']) in seen or j.get('startedAt','')<'2026-10-08T15:10': continue
        path=mp.parent/('M%d.replay'%j['id'])
        if not path.exists(): continue
        own=0 if j['teamAId']==1119 else 1
        bot=replay.load(path).root().text(1+own)
        version={'20941':'one4-ranked','20980':'one5-ranked'}.get(bot)
        if version:
            out.append(dict(label=version,path=str(path),game=str(j['id']),own=own,map=j['mapName']))
            seen.add(str(j['id']))
    for folder in sorted((RUNS/'mDo5_vh').glob('*-seed*-side*')):
        if (folder/'result.txt').exists() and (folder/'game.replay').exists():
            out.append(dict(label='mDo5_vh',path=str(folder/'game.replay'),game=folder.name,own=int(folder.name[-1]),map=folder.name.rsplit('-seed',1)[0]))
    return out

def scan(job):
    B=Board(job['path']); own=job['own']; queen=min(i for i in B.bodies if B.teams[i]==own)
    C=Counter(); rows=[]; snapshots=[]; cur=None
    def close():
        nonlocal cur
        if cur is None: return
        if cur['split']: cls='split'
        elif cur['first'] is None: cls='died' if cur['died'] else 'no_step'
        else:
            ds=B.flood(cur['first'],3,cur['occ']-{cur['h']})
            dist=min(ds.get(t,99) for t in cur['targets'])
            cls='toward' if dist<cur['d'] else 'sideways' if dist==cur['d'] else 'away'
        row={k:v for k,v in cur.items() if k not in ('occ','snapshot')}
        row.update(cls=cls,**{k:job[k] for k in ('game','label','map')})
        rows.append(row)
        for window in ('all', 'early' if cur['r']<=100 else 'late'):
            C[(window,cur['d'],cur['mate'],cls)]+=1
        if (cur['d']==2 and cls=='away') or (cur['d']==1 and not cur['ate'] and not cur['split']):
            snapshots.append(dict(**row,snapshot=cur['snapshot']))
        cur=None
    for ev in B.root.pointer(3):
        k=ev.u16(0)
        if k not in (0,1,3,9,10,11): continue
        p=ev.pointer(0)
        if k in (0,1): close()
        if cur is not None:
            if k==9 and p.i32(0)==cur['i']:
                hd=replay.point(p.pointer(0))
                if cur['first'] is None and hd!=cur['h']: cur['first']=hd
            elif k==10 and p.i32(0)==cur['i']: cur['split']=True
            elif k==11 and p.i32(0)==cur['i']: cur['died']=True
            elif k==3 and not p.u32(0): cur['ate']=True
        B.update(k,p)
        if k!=1 or B.teams[B.actor]!=own or B.actor==queen: continue
        i=B.actor; body=B.bodies[i]; h=body[0]
        # Geometric reachability, not number of cost-free sprint moves.
        occ=set(c for b in B.bodies.values() for c in b)
        ds=B.flood(h,2,occ)
        P=[c for c in B.pearls if B.view(h,c) and c in ds]
        if not P: continue
        d=min(ds[c] for c in P)
        if d not in (1,2): continue
        nearby=B.flood(h,4)
        if any(B.teams[z]!=own and b[0] in nearby for z,b in B.bodies.items()): continue
        targets=sorted(c for c in P if ds[c]==d)
        cur=dict(i=i,r=B.rnd,L=len(body),h=h,d=d,targets=targets,occ=occ,
                 mate=any(z!=i and B.teams[z]==own and B.view(h,b[0]) for z,b in B.bodies.items()),
                 first=None,split=False,died=False,ate=False,snapshot=B.snap())
    close()
    meta=dict(**job,cells=B.W*B.H,bot=B.root.text(1+own),counts=[[a,b,c,d,n] for (a,b,c,d),n in sorted(C.items())])
    return meta,rows,snapshots

def main():
    jobs=inventory()
    (OUT/'inventory.json').write_text(json.dumps(jobs,indent=2))
    for job in jobs:
        target=OUT/('scan-'+job['label']+'-'+job['game']+'.json')
        if target.exists(): continue
        meta,rows,snapshots=scan(job)
        target.write_text(json.dumps(dict(meta=meta,rows=rows),separators=(',',':')))
        (OUT/('snap-'+job['label']+'-'+job['game']+'.json')).write_text(json.dumps(snapshots,separators=(',',':')))
        print(job['label'],job['game'],len(rows),len(snapshots),flush=True)

if __name__=='__main__': main()
