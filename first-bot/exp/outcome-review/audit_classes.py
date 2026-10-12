#!/usr/bin/env python3
"""Independent class census using official-update reconstruction, not primary features."""
import collections,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'.cache/outcome-review'
A=json.load(open(C/'analysis.json'));M=json.load(open(C/'manifest.json'))
meta={x['set']:x for x in M['sets']};primary={g['key']:g for g in map(json.loads,open(C/'games.jsonl'))}
counts={z:collections.Counter() for z in ['all','waves','history']};mismatch=[]
terms=['initial-lineage','natural-intake','sacrifice-to-line','other-own-drops','enemy-drops','sprint-loss','split-loss']
for g in map(json.loads,open(C/'independent-v2.jsonl')):
 st=g['key'].split(':')[0];era=meta[st]['era']
 j=json.load(open(R/'data/online'/st/('game-'+str(g['id'])+'.json')))
 o='W' if j['replay']['result']['winner']=='A' else 'L' if j['replay']['result']['winner']=='B' else 'D'
 a,b=g['teams']['A'],g['teams']['B'];cl={}
 if o=='W':cl['winClass']='opponent-elimination' if b['finalUnits']==0 else 'opponent-late-king-loss' if any(d['r']>=300 for d in b['kd']) else 'length-race'
 if o=='L' and b['final']>0 and a['final']>=.8*b['final']:
  if a['lineage300'] is None or b['lineage300'] is None:cl['nearClass']='no-r300-decomposition'
  else:
   values=[b['lineage300']-a['lineage300'],b['lineNatural300']-a['lineNatural300'],b['lineSac300']-a['lineSac300'],b['lineOther300']-a['lineOther300'],b['lineEnemy300']-a['lineEnemy300'],a['lineSprint300']-b['lineSprint300'],a['lineSplit300']-b['lineSplit300']]
   assert sum(values)==b['final']-a['final']
   cl['nearClass']=terms[values.index(max(values))]
 leads=[t for t in [300,400] if str(t) in g['checkpoints'] and g['checkpoints'][str(t)]['A']['king']>g['checkpoints'][str(t)]['B']['king']]
 if o=='L' and leads:
  cl['leadClass']='our-late-king-loss' if any(d['r']>=min(leads) for d in a['kd']) else 'opponent-sacrifice-growth' if a['lineSac300'] is not None and b['lineSac300'] is not None and b['lineSac300']>a['lineSac300'] else 'other-growth'
 for name,prefix in [('winClass','win:'),('nearClass','near:'),('leadClass','lead:')]:
  if cl.get(name)!=primary[g['key']].get(name):mismatch.append({'key':g['key'],'field':name,'primary':primary[g['key']].get(name),'independent':cl.get(name)})
  if name in cl:
   for pop in ['all',era]:counts[pop][prefix+cl[name]]+=1
first={k:z['n'] for k,z in A['classes'].items()}
assert dict(counts['all'])==first and not mismatch
P=json.load(open(C/'metadata-power.json'));pw=A['power']
assert abs(P['dispersion']-pw['dispersion'])<1e-12
for z in pw['table']:
 z2=next(v for v in P['table'] if v['plusWinsPer60']==z['plusWinsPer60'] and v['power']==z['power'] and v['noise']==z['noise'])
 assert all(z[q]==z2[q] for q in ['gamesPerArm','totalGames','wavesPerArm','totalWaves'])
out={'gameN':len(primary),'primaryClasses':first,'independentClasses':dict(counts['all']),'byEra':{k:dict(v) for k,v in counts.items()},'mismatchCount':len(mismatch),'powerPrimaryDispersion':pw['dispersion'],'powerIndependentDispersion':P['dispersion'],'powerTableMismatches':0}
with open(C/'class-audit.json','x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(out,ensure_ascii=False))
