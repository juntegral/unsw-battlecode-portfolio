import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, Counter
from pathlib import Path
from functools import lru_cache

OUT = Path(__file__).resolve().parent
root = replay.load('data/online/live-one1/b1518019/M1518021.replay').root()
lines = root.text(0).splitlines()
W, H = map(int, lines[0].split()[1:3])
bodies, teams, raw = {}, {}, []
for line in lines:
    q = line.split()
    if q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque((int(q[3+2*k]), int(q[4+2*k])) for k in range(int(q[2])))
        teams[i] = int(q[1])
    elif q[0] == 'EDGE':
        raw.append(tuple(map(int, q[1:4])))
edges = canonical_edges(W,H,raw)
portals={}
for e,(k,p) in edges.items():
    if k==2:portals.setdefault(p,[]).append(e)
dirs = ((0,-1),(1,0),(0,1),(-1,0))
def dest(c,d):
    e=edge_id(W,H,*c,d); kind,pid=edges.get(e,(0,-1))
    if kind == 1:
        return None
    if kind == 2:
        partner=next(z for z in portals[pid] if z!=e)
        row,x=divmod(partner,W+1); y=row//2
        return ((x-(d==3))%W,(y-(d==0))%H)
    return ((c[0]+dirs[d][0])%W,(c[1]+dirs[d][1])%H)
def man(a,b):
    dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1])
    return min(dx,W-dx)+min(dy,H-dy)
@lru_cache(None)
def distances(c):
    dist={c:0}; queue=deque([c])
    while queue:
        x=queue.popleft()
        for d in range(4):
            y=dest(x,d)
            if y is not None and y not in dist:
                dist[y]=dist[x]+1; queue.append(y)
    return dist
def state():
    return {str(i):list(b) for i,b in bodies.items()}
pearls=set(); rnd=-1; actor=None; qt=None
turns=[]; near=[]; min_topo=None; min_man=None; qlocations=Counter(); qevents=[]
def check_near(idx):
    global min_topo,min_man
    if 1 in bodies or 0 not in bodies:return
    qh=bodies[0][0]; dist=distances(qh)
    for i,b in bodies.items():
        if teams[i]!=0:continue
        td=dist.get(b[0],9999); md=man(qh,b[0])
        r=dict(round=rnd,event=idx,id=i,head=b[0],queen=qh,topological=td,manhattan=md)
        if min_topo is None or td<min_topo['topological']:min_topo=r
        if min_man is None or md<min_man['manhattan']:min_man=r
        if td<=5:near.append(r)
for idx,ev in enumerate(root.pointer(3)):
    k=ev.u16(0); p=ev.pointer(0)
    if k==0:
        rnd=p.i32(0); actor=None
        if rnd>=420:qlocations[bodies[0][0]]+=1
    elif k==1:
        actor=p.i32(0)
        if actor in (0,1):
            qt=dict(round=rnd,id=actor,event=idx,body=list(bodies[actor]),units=sum(teams[i]==teams[actor] for i in bodies),actions=[],logs=[],updates=[],eats=[])
            if actor==1 and rnd>=410:qt.update(bodies=state(),pearls=list(pearls))
            turns.append(qt)
        else: qt=None
        check_near(idx)
    elif k==3:
        xy=replay.point(p.pointer(0))
        if p.u32(0):pearls.add(xy)
        else:
            pearls.remove(xy)
            if qt:qt['eats'].append(xy)
    elif k==4 and qt:
        a=p.pointer(0)
        qt['actions'].append(dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [],child=a.i32(4) if a.u16(0)==1 else None,tle=p.bit(32)))
    elif k==6 and qt:qt['logs'].append(p.text(0))
    elif k==9:
        i=p.i32(0); hd=replay.point(p.pointer(0)); tl=replay.point(p.pointer(1)); b=bodies[i]
        if b[0]!=hd:b.appendleft(hd)
        while len(b)>1 and b[-1]!=tl:b.pop()
        assert b[-1]==tl
        if qt:qt['updates'].append(list(b))
        check_near(idx)
    elif k==10:
        for z,i in enumerate((p.i32(0),p.i32(4))):
            bodies[i]=deque(replay.point(c) for c in p.pointer(z)); teams[i]=p.u16(8)
        check_near(idx)
    elif k==11:
        i=p.i32(0)
        if i in (0,1):qevents.append(dict(round=rnd,id=i,reason=p.u16(4),actor=actor,body=list(bodies[i])))
        bodies.pop(i)
        check_near(idx)
def board(t):
    cx,cy=t['body'][0]; bs={int(i):b for i,b in t['bodies'].items()}; ps=set(map(tuple,t['pearls']))
    rows=[]
    for dy in range(-3,4):
        north=''; cells=''
        for dx in range(-3,4):
            c=((cx+dx)%W,(cy+dy)%H)
            north+='+'+('--' if dest(c,0) is None else '  ')
            ch='*' if c in ps else '.'
            for i,b in bs.items():
                if list(c) in b or c in b:
                    ch=('Q' if i==1 else 'K' if i==0 else 'A' if teams[i]==0 else 'B') if tuple(b[0])==c else ('q' if i==1 else 'k' if i==0 else 'a' if teams[i]==0 else 'b')
            cells+=('|' if dest(c,3) is None else ' ')+ch+' '
        rows.extend([north+'+',cells+('|' if dest(((cx+3)%W,(cy+dy)%H),1) is None else ' ')])
    rows.append(''.join('+'+('--' if dest(((cx+dx)%W,(cy+3)%H),2) is None else '  ') for dx in range(-3,4))+'+')
    return '\n'.join(rows)
enemy_room=set(distances((2,1)))
incoming=[(x,y,d) for y in range(H) for x in range(W) if (x,y) not in enemy_room for d in range(4) if dest((x,y),d) in enemy_room]
out=dict(turns=turns,queen_deaths=qevents,postdeath_min_topological=min_topo,postdeath_min_manhattan=min_man,postdeath_near=near,queen_locations=[(k,v) for k,v in qlocations.items()],enemy_room=sorted(enemy_room),enemy_room_incoming=incoming)
(OUT/'moments.json').write_text(json.dumps(out,ensure_ascii=False))
with (OUT/'boards.txt').open('w') as f:
    for t in [t for t in turns if t['id']==1][-3:]:
        f.write(f"r{t['round']} center={t['body'][0]} body={t['body']} action={t['actions']}\n{board(t)}\n")
print('last queen turns')
for t in [t for t in turns if t['id']==1][-12:]:print({k:v for k,v in t.items() if k not in ('bodies','pearls')})
print('postdeath',min_topo,min_man,'near count',len(near),'queen locations',qlocations)
print('queen meals',[(t['round'],t['id'],t['eats']) for t in turns if t['eats']])
print((OUT/'boards.txt').read_text())
