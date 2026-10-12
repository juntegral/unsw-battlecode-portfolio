import json,gzip,collections,pathlib,datetime,statistics
from aggregate import stats
O=pathlib.Path(__file__).resolve().parent
T=json.load(open(O/'tables.json'));members=collections.defaultdict(list)
for f,a in T['maps'].items():
 for role,c in a['cohorts'].items():
  for key in c['keys']:members[key].append((f,role))
classmembers={}
classacc=collections.defaultdict(lambda:collections.defaultdict(list))
for f,a in T['maps'].items():
 for role,c in a['cohorts'].items():
  for cl,keys in c['classKeys'].items():
   for key in keys:classmembers[(f,role,key)]=cl
acc=collections.defaultdict(lambda:{'all':collections.Counter(),'full':collections.Counter(),'independentAll':collections.Counter(),'independentFull':collections.Counter(),'N':0,'N500':0,'hist':collections.Counter(),'independentHist':collections.Counter(),'metrics':collections.defaultdict(list),'deaths':[],'earlySpawn':collections.defaultdict(collections.Counter),'earlySpawnN':collections.Counter()})
checks=collections.Counter();compare=collections.Counter();n=0;keys=set();layoutEvidenceCounts=collections.Counter()
for l in gzip.open(O/'conversion.jsonl.gz','rt'):
 r=json.loads(l);n+=1;keys.add(r['key']);checks.update(r['check']);e=r.get('layoutEvidence',{});layoutEvidenceCounts['ambiguousRetained']+=int(r['layout']=='?');layoutEvidenceCounts['supportTie']+=int('ca' in e and e['ca']==e['cb'])
 for tm in 'AB':
  compare.update(r['compare'][tm]);key=r['key']+':'+tm
  if key not in members:continue
  for f,role in members[key]:
    a=acc[(f,role)];v=r[tm];a['N']+=1
    for rr,positions in v['earlySpawn'].items():a['earlySpawn'][rr].update(positions);a['earlySpawnN'][rr]+=1
    for k in ['sacDrops300','linePacket300','ownRecovery300','lineSacEat300','lineEat300','pocketNatural']:a['all'][k]+=v[k];a['independentAll'][k]+=v['independent'][k]
    for d,x in enumerate(v['safetyHist']):
     if x:a['hist'][d]+=x
    for d,x in enumerate(v['independent']['safetyHist']):
     if x:a['independentHist'][d]+=x
    a['deaths']+=v['safetyDeaths']
    distances=[i for i,count in enumerate(v['safetyHist']) if i!=999 for _ in range(count)]
    distanceP10=sorted(distances)[int(.1*(len(distances)-1))] if distances else None
    a['metrics']['kingSafeP10'].append(distanceP10)
    ca=classacc[(f,role,classmembers[(f,role,key)])];ca['kingSafeP10'].append(distanceP10)
    if r['rounds']==500:
     a['N500']+=1
     for k in ['sacDrops300','linePacket300','ownRecovery300','lineSacEat300','lineEat300']:a['full'][k]+=v[k];a['independentFull'][k]+=v['independent'][k]
     a['metrics']['lineShare300'].append(v['linePacket300']/v['sacDrops300'] if v['sacDrops300'] else None)
     a['metrics']['lineSacEat300'].append(v['lineSacEat300'])
     a['metrics']['lineSacSourceShare300'].append(v['lineSacEat300']/v['lineEat300'] if v['lineEat300'] else None)
     for field in ['lineShare300','lineSacEat300','lineSacSourceShare300']:ca[field].append(a['metrics'][field][-1])
def histq(hist,q):
 h={int(k):v for k,v in hist.items() if int(k)!=999};n=sum(h.values())
 if not n:return None
 cum=0
 for k,v in sorted(h.items()):
  cum+=v
  if cum>=q*n:return k
for (f,role),a in acc.items():
 c=T['maps'][f]['cohorts'][role];h=a['hist'];nh=sum(h.values());nr=nh-h[999];s=a['full']
 c['seenSpawnPositions']={r:{'N':a['earlySpawnN'][r],'tiles':[{'tile':k,'xy':[k%T['maps'][f]['features']['W'],k//T['maps'][f]['features']['W']],'seenN':v,'seenFraction':v/a['earlySpawnN'][r]} for k,v in sorted(pos.items())]} for r,pos in a['earlySpawn'].items()}
 c['conversion']={k:dict(a[k]) for k in ['all','full','independentAll','independentFull']};c['conversion'].update(N=a['N'],N500=a['N500'])
 if a['N']!=c['N']:raise ValueError('cohort missing '+f+role)
 for k,v in a['metrics'].items():c['metrics'][k]=stats(v)
 c['pooled']['lineShare300']=s['linePacket300']/s['sacDrops300'] if s['sacDrops300'] else None
 c['pooled']['lineSacSourceShare300']=s['lineSacEat300']/s['lineEat300'] if s['lineEat300'] else None
 c['pooled']['kingSafeP10']=histq(h,.1)
 c['safety']={'gameN':a['N'],'sampleRoundsN':nh,'sampling':'r300-499 every5 rounds, current longest length>=8','unreachableN':h[999],'reachableN':nr,'p10Reachable':histq(h,.1),'medianReachable':histq(h,.5),'le3':sum(v for k,v in h.items() if k<=3)/nh if nh else None,'le6':sum(v for k,v in h.items() if k<=6)/nh if nh else None,'histogram':dict(h),'independentHistogram':dict(a['independentHist']),'kingDeathN':len(a['deaths']),'deathDistance':stats([v[3] for v in a['deaths'] if v[3]!=999]),'killerLength':stats([v[4] for v in a['deaths'] if v[4]>0])}
 if c['raw']['pocketNatural']!=a['independentAll']['pocketNatural']:raise ValueError('pocket mismatch '+f+role)
for (f,role,cl),ms in classacc.items():
 for field,values in ms.items():T['maps'][f]['cohorts'][role]['classBehaviour'][cl]['metrics'][field]=stats(values)
T['verification']['enrichment']={'N':n,'keysN':len(keys),'layoutEvidenceCounts':dict(layoutEvidenceCounts),'primaryChecks':dict(checks),'independentMismatch':dict(compare),'missing':[t['key'] for t in json.load(open(O/'population.json'))['tasks'] if t['key'] not in keys]}
T['definitions']['lineShare300']='drops created by own operational sacrifices r300-499 consumed by active final lineage by end / all these drops; 500-round finishes only for fit'
T['definitions']['kingSafeP10']='pooled p10 shortest legal path to nearest enemy head; r300-499 every5 rounds, current longest>=8; unreachable excluded from quantile but retained in histogram/proportions'
T['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();T['missing']=['fits and partial-input validation','deep reads','report']
json.dump(T,open(O/'tables.json','w'),ensure_ascii=False,indent=1,allow_nan=False)
print('ENRICHED',n,dict(compare))
