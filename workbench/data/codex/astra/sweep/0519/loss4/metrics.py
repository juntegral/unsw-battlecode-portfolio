import json,hashlib
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent
rows=[]
for gid in (1492096,1492097,1492098):
 a=json.loads((OUT/f'{gid}.json').read_text());d=json.loads((OUT/f'detail-{gid}.json').read_text());g=a['scan'];ts=d['turns'];queen=g['queens']['us'];streak=Counter();candidate=[]
 for t in ts:
  if t['side']!=0:continue
  if t['id']!=queen and t['L']<=4 and t['pearl_view']==0 and streak[t['id']]>=12:candidate.append((t['r'],t['id']))
  streak[t['id']]=0 if t['eats'] else streak[t['id']]+1
 rows.append(dict(gid=gid,final=g['final'],turn=a['detail']['decisive_retrospective'],last=g['last_round'],mass_behind_since=1+max((int(r) for r,v in g['snapshots'].items() if v['us']['total']>=v['them']['total']),default=-1),candidate_no_meal12_no_view_short_nonqueen=len(candidate),candidate_first=candidate[:3],candidate_round0_50=sum(r<=50 for r,i in candidate),first_eat=[next(((t['r'],t['id']) for t in ts if t['side']==s and t['eats']),None) for s in (0,1)]))
(OUT/'metrics.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
print('source sha256',hashlib.sha256(Path('data/online/smoke/one10-bot/main.cpp').read_bytes()).hexdigest())
