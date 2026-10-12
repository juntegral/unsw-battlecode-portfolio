import json
from pathlib import Path
from collections import Counter
O=Path('data/codex/astra/sweep/1055/loss2');summary=[]
for gid in [1501666,1501667,1501668]:
 a=json.loads((O/f'{gid}-trace.json').read_text());b=json.loads((O/f'{gid}-ledger.json').read_text());cs=json.loads((O/f'{gid}-counts.json').read_text())
 par={s['child']:s for s in a['splits']};final=a['snaps']['499'];res={'gid':gid,'queens':a['queens'],'final':final,'lineages':[],'metrics':[]}
 for side in [0,1]:
  i=final[side][4][0][0];chain=[i];cut=[]
  while i in par:
   sp=par[i];cut.append([sp['r'],sp['id'],i,sp['before']]);i=sp['id'];chain.append(i)
  print(gid,'side',side,'chain',list(reversed(cut)))
  def anc(r):
   i=chain[0]
   while i in par and par[i]['r']>r:i=par[i]['id']
   return i
  lineage=[]
  for lo,hi in [(0,100),(301,350),(351,400),(401,450),(451,499)]:
   ts=[t for t in a['turns'] if t['side']==side and lo<=t['r']<=hi and t['id']==anc(t['r'])];ids={t['id'] for t in ts};drop=sum(p['eater_id']==anc(p['eat_round']) and lo<=p['eat_round']<=hi for p in b['pearls'] if p['eater_id'] is not None and p['eater']==['us','them'][side]);lineage.append([lo,hi,len(ts),sum(len(t['eat']) for t in ts),drop,ids and sorted(ids)])
  print('LINEAGE EATS',lineage)
  res['lineages'].append(dict(chain=list(reversed(cut)),eats=lineage))
 for lo,hi in [(301,350),(351,400),(401,450),(451,499)]:
  row=[]
  for side in [0,1]:
   ts=[t for t in a['turns'] if t['side']==side and lo<=t['r']<=hi];row.append(dict(turns=len(ts),eaten=sum(len(t['eat']) for t in ts),suicides=sum(t['action']=='suicide' for t in ts),splits=sum(t['action']=='split' for t in ts)))
  res['metrics'].append([lo,hi,row])
 both=max(d['r'] for d in a['deaths'] if d['id'] in a['queens']);post=[int(r) for r,s in a['snaps'].items() if int(r)>=both and s[0][2]>=s[1][2]];res['lasting_longest_deficit']=max(post)+1 if post else both
 print('TURN',res['lasting_longest_deficit'])
 summary.append(res)
(O/'summary.json').write_text(json.dumps(summary))
