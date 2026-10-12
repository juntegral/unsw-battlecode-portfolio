import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT.parent/'evade'),str(OUT.parents[3]/'analysis/ladder/dossier/work')]
import analyze as a
sys.path.insert(0,str(a.ROOT/'data/analysis/ladder/dossier/work'))
import o1_scan
rows=json.loads((OUT/'table-rows.json').read_text());checks=[]
for label in ('one5-w1','one5-c1','one7-w1','one7-c1'):
 for p,m in a.label_report.inventory(label,'old')['jobs']:
  out=o1_scan.scan(label,p,m)
  rr=[r for r in rows if r['gid']==m['id']]
  expected=Counter((d[0],d[2]) for d in out['deaths'] if d[4]=='rammed' and d[1]==0 and not d[6] and d[0]<=200)
  actual=Counter((r['round'],r['victim_impact_length']) for r in rr)
  assert expected==actual,(m['id'],expected-actual,actual-expected)
  g=a.Geo(a.lr.replay.load(p).root().text(0));n=0
  for row in rr:
   if row['last_event'] is not None:
    assert row['round']-row['last_round']==int(row['attacker']<row['victim'])
   for op in row['safe']:
    bs={i:tuple(tuple(c) for c in b) for i,s,b in row['start_bodies']};body=bs[row['victim']];ps=set(map(tuple,row['start_pearls']));others={c for i,b in bs.items() if i!=row['victim'] for c in b}
    for d in op['path']:
     nxt=g.moves[body[0]][d];assert nxt is not None and nxt not in body and nxt not in others
     body=(nxt,)+body if nxt in ps else (nxt,)+body[:-1];ps.discard(nxt)
    assert body==tuple(map(tuple,op['body']));assert a.good_room(g,body,others)
    assert not a.hits(g,bs,row['attacker'],row['victim'],body,ps,extra_budget=True)
    n+=1
  checks.append(dict(label=label,gid=m['id'],bot=out['bot'],independent_counts=True,witnesses=n,rammed_full=sum(d[4]=='rammed' and d[1]==0 and not d[6] for d in out['deaths']),replay_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
  print(label,m['id'],len(rr),n,flush=True)
(OUT/'verification.json').write_text(json.dumps(checks,indent=2))
