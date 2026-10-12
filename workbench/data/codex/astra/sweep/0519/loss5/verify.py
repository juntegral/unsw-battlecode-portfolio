import json,hashlib
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent
rows=[]
for g in (1492099,1492102,1492103):
 s=json.loads((P/f'{g}-summary.json').read_text());d=json.loads((P/f'{g}-turns.json').read_text());teams=d['teams'];ts=d['turns'];q=s['queens'][0]
 assert s['botA']=='21200'
 qt=[t for t in ts if t['i']==q];foeq=[t for t in ts if t['i']==s['queens'][1]]
 ram=Counter('active' if x['actor']==x['i'] else 'passive' for x in d['deaths'] if teams[str(x['i'])]==0 and x['reason']==3)
 persist={k:max((int(r) for r,st in s['snaps'].items() if st[0][k]>=st[1][k]),default=-1)+1 for k in ('q','long','total')}
 row=dict(game=g,final=s['final'],ram=dict(ram),persistent_deficit=persist,queen_eats=[sum(t['eat'] for t in qt),sum(t['eat'] for t in foeq)],queen_splits=[x for x in d['splits'] if x['parent']==q])
 if g==1492099:
  assert persist['long']==439
  assert [(x['r'],x['i'],x['L']) for x in d['deaths'] if teams[str(x['i'])]==0 and x['L']>=6]==[(360,176,8),(361,102,10)]
 if g==1492102:
  assert ram=={'passive':27,'active':8}
  row['r51_100']=[dict(turns=len(v:=[t for t in ts if 51<=t['r']<=100 and teams[str(t['i'])]==z]),eats=sum(t['eat'] for t in v)) for z in (0,1)]
  assert row['r51_100']==[dict(turns=172,eats=21),dict(turns=714,eats=76)]
 if g==1492103:
  late=[t for t in qt if t['r']>=389]
  row['queen_late']=dict(turns=len(late),eats=sum(t['eat'] for t in late),actions=dict(Counter(t['action'] for t in late)))
  assert row['queen_late']==dict(turns=111,eats=0,actions={0:111})
  row['r301_388_suicides']=sum(301<=t['r']<=388 and teams[str(t['i'])]==0 and t['action']==2 for t in ts)
  assert row['r301_388_suicides']==12
  assert row['queen_eats']==[33,49]
  assert sum(x['lens'][1] for x in row['queen_splits'])==10
  assert 4+33-10==27 and 4+49==53
 rows.append(row)
source=Path('data/online/smoke/one10-bot/main.cpp')
(P/'evidence.json').write_text(json.dumps(dict(source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),games=rows),indent=2))
report=(P/'report.md').read_text();assert len(' '.join(l for l in report.splitlines() if not l.startswith('|')).split())<600
assert report.count('<code>')==6
print('Verified: 3 bot ids, final-state reconstruction assertions (analyze.py), quoted counts, 6 queen boards, report length.')
