import sys,json,importlib.util
from pathlib import Path
from collections import deque
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

w=module('weak_analysis','data/codex/astra/weak/analyze.py')
p=Path('data/online/live-one1/b1479873/M1479875.replay');meta=json.loads(p.with_name('game-1479875.json').read_text())
x=w.extra(p,meta);root=w.replay.load(p).root();x['bot_text']=[root.text(1),root.text(2)]
(OUT/'target.json').write_text(json.dumps(x))
sys.path.insert(0,'data/codex/astra/deathcell')
import scan
x=scan.census(p,meta,root,{0});d=next(d for d in x['deaths'] if d['queen'] and d['side']==0)
(OUT/'queen-detail.json').write_text(json.dumps(d))
pc=module('pocket_check','data/codex/build/pocket/replay_check.py');g=scan.Geo(root.text(0))
(OUT/'card-target.json').write_text(json.dumps(pc.evaluate(g,d['entry']['context'],d['entry'],True)))
rows=json.loads((OUT/'moments.json').read_text());c=next(c for c in rows if c['id']==8 and c['r']==113)
bodies={int(i):tuple(map(tuple,bb)) for i,bb in c['bodies'].items()};pearls=set(map(tuple,c['pearls']))
def dest(h,z):return None if g.kind(h,z)==1 else g.dest(h,z)
def simulate(body,path):
    eaten=set()
    for z in path:
        n=dest(body[0],z);assert n is not None and n not in body
        eat=n in pearls-eaten;body=(n,)+(body if eat else body[:-1]);eaten.add(n)
    return body

def qpaths(mate):
    occupied={v for i,bb in bodies.items() if i not in (0,8) for v in bb}|set(mate)
    queue=deque([(bodies[0],(),frozenset())]);done=[]
    while queue:
        bb,path,eaten=queue.popleft()
        if len(path)==2:done.append(path);continue
        for z in range(4):
            n=dest(bb[0],z)
            if n is None or n in bb or n in occupied:continue
            eat=n in pearls-eaten;nb=(n,)+(bb if eat else bb[:-1]);queue.append((nb,path+(z,),eaten|{n}))
    return done
r=dict(before=qpaths(bodies[8]),actual_E_N=qpaths(simulate(bodies[8],[1,0])),alternative_N=qpaths(simulate(bodies[8],[0])),note='Frozen other dragons; queen two successive one-step turns. Local feasibility, not a replay rerun.')
assert r['before']==[(3,0)] and r['actual_E_N']==[] and r['alternative_N']==[(3,0)]
(OUT/'queen-unpin-proof.json').write_text(json.dumps(r,indent=2))
print('Target terminal state, queen census, pocket condition and unpin geometry checked.')
