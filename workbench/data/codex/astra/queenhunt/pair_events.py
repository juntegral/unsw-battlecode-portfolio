import sys
sys.dont_write_bytecode=True
import json
from itertools import zip_longest
from pathlib import Path
sys.path[:0]=['data/analysis/ladder/dossier/local']
from scoreboard import load_replay
from replay_format import point
OUT=Path(__file__).resolve().parent
RUNS=Path.home()/'meow-redteam/solo/runs'

def stream(path):
    root=load_replay(path).root();rnd=-1;actor=None
    for ev in root.pointer(3):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:rnd=p.i32(0);actor=None;payload=rnd
        elif k==1:actor=p.i32(0);payload=actor
        elif k==3:payload=(p.u32(0),point(p.pointer(0)))
        elif k==9:payload=(p.i32(0),point(p.pointer(0)),point(p.pointer(1)))
        elif k==10:payload=(p.i32(0),p.i32(4),p.u16(8),[[point(z) for z in p.pointer(i)] for i in (0,1)])
        elif k==11:payload=(p.i32(0),p.u16(4))
        else:continue
        yield (rnd,actor,k,payload)

rows=[]
for p in sorted((RUNS/'mDqh_vb').glob('*/game.replay')):
    q=RUNS/'mDl5_vb'/p.parent.name/'game.replay'
    if not q.exists():continue
    first=None;prior=[]
    for a,b in zip_longest(stream(p),stream(q)):
        if a!=b:first=dict(hunt=a,one5=b,preceding=prior[-6:]);break
        prior.append(a)
    rows.append(dict(game=p.parent.name,first_difference=first))
(OUT/'pair-first-difference.json').write_text(json.dumps(rows,indent=2))
for r in rows:print(r['game'],r['first_difference'])
