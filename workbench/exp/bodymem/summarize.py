import json,hashlib
from pathlib import Path
p=Path('exp/bodymem');a=json.loads((p/'analysis.json').read_text());v=json.loads((p/'review.json').read_text())
def bodyhash(body):
 h=2166136261
 for t in body:h=((h^(t&0xffffffff))*16777619)&0xffffffff
 return h
out={'sets':{},'sameHistory':{},'nativeProductionBodyCrosscheck':{},'context':{}}
for arm in ('on','off'):
 rows=list(a['sets'][arm].values());out['sets'][arm]={}
 for name in ('multi','completed','predicted','unknownInput','unseenPearls','oversprint','selfMulti','queenSelfMulti'):
  out['sets'][arm][name]=sum(r[name] for r in rows)
 for name in ('startBodyDrift','endBodyDrift','memoryDrift','missingTags','oracleDrift','stepDrift'):
  out['sets'][arm][name]=sum(len(r[name]) for r in rows)
 for name in ('reasons','causes'):out['sets'][arm][name]={k:sum(r[name].get(k,0) for r in rows) for k in set().union(*(r[name] for r in rows))}
 out['sets'][arm]['cpuMaxM']=max(r['cpuMaxM'] for r in rows)
for kind in ('memory','memory-strict'):
 ix=json.loads((p/(kind+'-index.json')).read_text())
 out['sameHistory'][kind]={}
 for source in ('on','off'):
  result={'turns':0,'missingCountdown':0,'ambiguousFacing':0,'worlds':{x:{k:0 for k in ('complete','completeDrift','startDrift','postDrift','unseenEndOnly')} for x in ('on','off')}}
  mismatch=[];checked=0;nativeMulti=0
  for x in ix:
   if x['arm']!=source:continue
   d=json.loads(Path(x['file']).read_text());result['turns']+=d['turns']
   for k in ('missingCountdown','ambiguousFacing'):result[k]+=d['uncertain'][k]
   for world in ('on','off'):
    for k in result['worlds'][world]:
     z=d['arms'][world][k];result['worlds'][world][k]+=z if isinstance(z,int) else len(z)
   if kind=='memory-strict':
    native={(r['round'],r['id']):r for r in d['arms'][source]['startDrift'] if not r['actual'].startswith('split') and len(r['actual'])>1 and r['postActual'] is not None}
    nativeMulti+=len(native)
    official={(r['round'],r['id']):r for r in a['sets'][source][x['key']]['startBodyDrift']}
    for key in set(native)|set(official):
     checked+=1
     if key not in native or key not in official or bodyhash(native[key]['reported'])!=official[key]['reported']:mismatch.append({'key':x['key'],'turn':key})
  out['sameHistory'][kind][source]=result
  if kind=='memory-strict':out['nativeProductionBodyCrosscheck'][source]={'nativeMultiDrift':nativeMulti,'checkedDriftTurns':checked,'mismatch':mismatch}
for direction in ('longer','shorter','same'):
 rows=[r for r in a['pairs'] if r['queenLifeDirection']==direction];d=[r['queenLifeOn']-r['queenLifeOff'] for r in rows]
 out['context'][direction]={'N':len(rows),'sumDelta':sum(d),'minDelta':min(d or [0]),'maxDelta':max(d or [0])}
out['context']['depth']={k:sum(r[k] for r in a['pairs']) for k in ('depthPairs','depthLower','depthSame','depthHigher')}
out['context']['newQueenDeaths']=sum(r['queenDeathDelta']>0 for r in a['pairs']);out['context']['rescuedQueenDeaths']=sum(r['queenDeathDelta']<0 for r in a['pairs'])
out['completeness']={'expected':a['expectedGames'],'missing':len(a['missing']),'historyErrors':len(a['historyErrors']),'pairs':len(a['pairs']),'identityPairs':len(a['identity']),'identityMatches':sum(x['same'] for x in a['identity'])}
(p/'summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
