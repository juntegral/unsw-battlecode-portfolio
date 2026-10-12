import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from collections import deque
sys.path.insert(0,str(Path.cwd()/'data/analysis/ladder/dossier/local'))
from count_local import Geo
OUT=Path(__file__).resolve().parent

def setup(gid,rnd,actor):
    data=json.loads((OUT/f'{gid}-detail.json').read_text())
    base=json.loads((OUT/f'{gid}-base.json').read_text())
    t=next(t for t in data['turns'] if t['id']==actor and t['round']==rnd)
    raw=[tuple(map(int,line.split()[1:4])) for line in base['text'].splitlines() if line.startswith('EDGE ')]
    g=Geo(data['w'],data['h'],raw)
    bs={int(i):tuple(b) for i,b in t['all_bodies'].items()}
    x,y=t['board']['center'];pe=set()
    for dy,row in enumerate(t['board']['rows']):
        for dx,ch in enumerate(row):
            if ch=='*':pe.add(((y+dy-3)%data['h'])*data['w']+(x+dx-3)%data['w'])
    return data,t,g,bs,pe

def step(g,b,occupied,pe,d,paid):
    k,n=g.moves[b[0]][d]
    if k==1 or n in occupied or n in b or (paid and len(b)<=2): return None
    eat=n in pe; bb=(n,)+b
    if not eat:bb=bb[:-1]
    if paid:bb=bb[:-1]
    return bb,pe-{n}

data,t,g,bs,pe=setup(1496849,75,1)
q=bs[1];occupied={c for i,b in bs.items() if i!=1 for c in b};before=q;route=[]
for j,d in enumerate([0,1,2]):
    nxt=step(g,q,occupied,pe,d,j>=1);assert nxt is not None
    q,pe=nxt;route.append(dict(head=[q[0]%g.w,q[0]//g.w],length=len(q)))
assert len(q)==2
enemy_reaches=[]
new_bs=dict(bs);new_bs[1]=q
for i,b in bs.items():
    if data['teams'][str(i)]!=1 or b[0] not in g.window(before[0]):continue
    occ={c for z,bb in new_bs.items() if z!=i for c in bb}-{q[0]}
    queue=deque([(b,frozenset(pe),0)]); seen=set();hit=False
    while queue:
        body,food,n=queue.popleft()
        if body[0]==q[0]:hit=True;break
        if n>=8:continue
        for direction in range(4):
            result=step(g,body,occ,food,direction,n>=(len(b)+3)//4)
            if result:
                bb,pp=result; key=(bb,frozenset(pp),n+1)
                if key not in seen:seen.add(key);queue.append(key)
    if hit:enemy_reaches.append(i)
print('Stripes NES',route,'enemy heads reaching endpoint under frozen other bodies',enemy_reaches)
assert not enemy_reaches

data,t,g,bs,pe=setup(1496848,111,8)
q=bs[0]; occ={c for i,b in bs.items() if i!=8 for c in b}
out=[]
for d in range(4):
    n=step(g,bs[8],occ,pe,d,False)
    if not n:continue
    body,food=n;after=dict(bs);after[8]=body
    occupied={c for i,b in after.items() if i!=0 for c in b}
    paths=[]
    for qd in range(4):
        m=step(g,q,occupied,food,qd,False)
        if not m:continue
        qb,pf=m
        onward=sum(step(g,qb,occupied,pf,dd,False) is not None for dd in range(4))
        paths.append(dict(first=[qb[0]%g.w,qb[0]//g.w],onward=onward))
    out.append(dict(mate_direction='NESW'[d],queen_paths=paths))
print('Maze mate alternatives',out)
(OUT/'path-checks.json').write_text(json.dumps(dict(stripes=dict(route=route,frozen_enemy_reachers=enemy_reaches),maze=out),indent=2))
