import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
O=Path('data/codex/astra/sweep/1055/loss36')
out={}
for gid in (1515658,1515660,1515661):
 g=json.loads((O/f'{gid}-ledger.json').read_text());t=json.loads((O/f'{gid}-trace.json').read_text());tt=t['turns']
 teams={x["id"]:x["team"] for x in tt};bands={}
 for lo,hi in ((0,100),(101,300),(301,399),(400,499),(433,499)):
  bands[f'{lo}-{hi}']=[dict(turns=sum(x['team']==s and lo<=x['r']<=hi for x in tt),eats=sum(x['eats'] for x in tt if x['team']==s and lo<=x['r']<=hi),splits=sum(teams[x['id']]==s and lo<=x['r']<=hi for x in t['splits'])) for s in (0,1)]
 out[gid]=dict(bands=bands)
 if gid==1515658:
  ours={385,748,763,783,806};theirs={274,805,813}
  out[gid]['lineage400_499']=[dict(eats=sum(x['eats'] for x in tt if x['id'] in ids and x['r']>=400),drops=sum(z['eat_round'] is not None and z['eat_round']>=400 and z['eater_id'] in ids for z in g['pearls'])) for ids in (ours,theirs)]
 if gid==1515661:
  out[gid]['ownmaxever']=max(x['L'] for x in tt if x['team']==0)
  out[gid]['r402']=g['snapshots']['402'];out[gid]['lastlong']=[x for x in tt if x['id']==309 and x['r']>=469]
 print(gid,out[gid])
(O/'metrics.json').write_text(json.dumps(out,indent=2))
