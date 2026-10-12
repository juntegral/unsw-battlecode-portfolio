"""Check two independent census passes and every recorded escape witness."""
import sys,json
sys.dont_write_bytecode=True
from scan import OUT,Board,RUNS
from collections import Counter

checks=[]
for af in sorted(OUT.glob('anytwo-*.json')):
    data=json.loads(af.read_text());sf=OUT/('scan-'+af.name[len('anytwo-'):])
    reference=json.loads(sf.read_text())
    key=lambda r:(r['r'],r['i'],r['cls'],r['mate'],tuple(map(tuple,r['targets'])))
    a=Counter(key(r) for r in data['rows'] if not r['adjacent'])
    b=Counter(key(r) for r in reference['rows'] if r['d']==2)
    assert a==b,(af,a-b,b-a)
    checks.append(dict(game=data['meta']['game'],label=data['meta']['label'],eligible=len(data['rows']),nearest_d2=sum(a.values())))

T=json.loads((OUT/'traps.json').read_text());boards={};witnesses=0
for r in T['rows']:
    if r['status']!='safe':continue
    game=r['game']
    if game not in boards:boards[game]=Board(RUNS/'m9etr1'/game/'game.replay')
    B=boards[game];s=r['snapshot'];body=(tuple(r['target']),)+tuple(map(tuple,r['body']))
    occ={tuple(c) for i,b in s['bodies'].items() if int(i)!=r['i'] for c in b}
    food=set(map(tuple,s['pearls']))-{tuple(r['target'])}
    path=r['frozen']['path'];assert len(path)==len(body)+2
    for d in path:
        n=B.adj[body[0]][d];assert n is not None and n not in occ and n not in body
        body=(n,)+body if n in food else (n,)+body[:-1]
        food.discard(n)
    witnesses+=1

result=dict(census_games=len(checks),census_eligible=sum(c['eligible'] for c in checks),
            trace_cases=sum(x['matched'] for x in T['inventory']),safe_witnesses_verified=witnesses,games=checks)
(OUT/'verification.json').write_text(json.dumps(result,indent=2))
print({k:v for k,v in result.items() if k!='games'})
