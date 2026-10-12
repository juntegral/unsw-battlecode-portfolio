import sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict
import json,csv
O=Path(__file__).resolve().parent
games=[json.loads(p.read_text()) for p in sorted(O.glob('game-*.json'))]
rows=[r for g in games for r in g['rows']]
with (O/'spread.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
def aggregate(rs):
    def rat(a,b):
        den=sum(r[b] for r in rs)
        return sum(r[a] for r in rs)/den if den else None
    return dict(n=len(rs),coverage=rat('owned','bearing'),tie=rat('tie','bearing'),distance=rat('distance_sum','reachable'),
        unreachable=1-rat('reachable','bearing'),density=rat('heads','visible_bearing'),barren=rat('no_bearing4','heads'),
        crowd=rat('crowded2','heads'),heads=sum(r['heads'] for r in rs)/len(rs),
        pearls=sum(r['natural_eaten'] for r in rs)/len(rs),
        pairs_per_visible=rat('local_head_tile_pairs','visible_bearing'))
groups=defaultdict(list)
for r in rows: groups[r['label'],r['kind'],r['r'],r['side']].append(r)
A={k:aggregate(v) for k,v in groups.items()}
def fmt(x,p=1):return 'NA' if x is None else f'{x:.{p}f}'
def pair(a,b,k,m=1,p=1):return fmt(None if a[k] is None else a[k]*m,p)+'/'+fmt(None if b[k] is None else b[k]*m,p)
lines=['[M] 전수 집계. 우리/상대; 점유·고립·혼잡·도달불가는 %, 거리는 도달 가능한 칸만, H/V는 시야 합집합의 먹이칸당 머릿수.','']
for label in sorted({g['label'] for g in games}):
    for kind in ('all','natural'):
        lines+= [f'## {label}: {kind}','', '| r | 점유 | 평균 거리 | 도달불가 | H/V | 4걸음 먹이칸 없음 | 2걸음 동료 있음 | 머리/판 | 자연진주/판 |','|---|---|---|---|---|---|---|---|---|']
        for r in range(0,151,10):
            a,b=(A[label,kind,r,s] for s in (0,1))
            lines+=['| '+str(r)+' | '+' | '.join(pair(a,b,k,m,p) for k,m,p in [('coverage',100,1),('distance',1,2),('unreachable',100,1),('density',1,3),('barren',100,1),('crowd',100,1),('heads',1,1),('pearls',1,1)])+' |']
        lines+=['']
(O/'tables.md').write_text('\n'.join(lines))
(O/'summary.json').write_text(json.dumps([dict(label=k[0],kind=k[1],r=k[2],side=k[3],**v) for k,v in A.items()],indent=2))
out=[]
for g in games:
    rs={(r['r'],r['side']):r for r in g['rows'] if r['kind']=='natural'}
    a,b=rs[100,0],rs[100,1]
    out.append(dict(label=g['label'],gid=g['gid'],map=g['map'],gap=(b['owned']-a['owned'])/a['bearing'],heads=[a['heads'],b['heads']],
        pearls=[a['natural_eaten'],b['natural_eaten']],crowd=[a['crowded2'],b['crowded2']],barren=[a['no_bearing4'],b['no_bearing4']]))
(O/'worst.json').write_text(json.dumps(sorted(out,key=lambda x:-x['gap']),indent=2))
print(json.dumps(sorted(out,key=lambda x:-x['gap'])[:12],indent=2))
