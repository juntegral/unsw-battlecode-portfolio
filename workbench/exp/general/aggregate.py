"""Stream the complete frozen population; preserve denominators and independent raw sums."""
import json,gzip,math,statistics,collections,datetime,pathlib,sys
O=pathlib.Path(__file__).resolve().parent
METRICS=['heads25','heads50','heads100','heads250','middle25','middle50','middle100','splitSpeed50','intakePerHR','pocketIntakeShare','pocketHRShare','sacOnset20','sacOnset50','lineSacEat300','lineSacSourceShare300','kingGrowth300_500','kingSafeP10','finalKing']
def stats(v):
 v=sorted(x for x in v if x is not None and math.isfinite(x));n=len(v)
 if not n:return {'N':0,'mean':None,'median':None}
 s=sum(v);sd=statistics.stdev(v) if n>1 else 0
 return {'N':n,'sum':s,'mean':s/n,'median':statistics.median(v),'p10':v[int(.1*(n-1))],'p90':v[int(.9*(n-1))],'sd':sd,'naive95':[s/n-1.96*sd/math.sqrt(n),s/n+1.96*sd/math.sqrt(n)]}
def vals(r,t):
 v=r[t];out={}
 for c in [25,50,100,250]:
  x=v['cp'].get(str(c));out['heads'+str(c)]=x['heads'] if x else None
  if c!=250:out['middle'+str(c)]=x['mid']/x['heads'] if x and x['heads'] else None
 out['splitSpeed50']=v['split50']/v['eligibleHR50'] if v['eligibleHR50'] else None
 out['intakePerHR']=v['natural']/v['headRounds'] if v['headRounds'] else None
 out['pocketIntakeShare']=v['pocketNatural']/v['natural'] if v['natural'] else None
 out['pocketHRShare']=v['pocketHR']/v['headRounds'] if v['headRounds'] else None
 sac=[x[0] for x in v['sac'] if x[0]>=200]
 for p in [20,50]:out['sacOnset'+str(p)]=sac[max(0,math.ceil(len(sac)*p/100)-1)] if sac else None
 lin=v.get('lin');c=lin['cp'].get('300') if lin else None
 full=r['rounds']==500
 out['lineSacEat300']=c['eat'][1] if full and c else None
 out['lineSacSourceShare300']=c['eat'][1]/sum(c['eat']) if full and c and sum(c['eat']) else None
 out['kingGrowth300_500']=(lin['len']-c['Lt'])/200 if full and c else None
 ds=sorted(x[1] for x in v['safety'] if x[1]<999);out['kingSafeP10']=ds[int(.1*(len(ds)-1))] if ds else None
 out['finalKing']=v['final']['king'];return out

def main():
 table=json.load(open(O/'tables.json'));p=json.load(open(O/'population.json'));groups=collections.defaultdict(lambda:{'N':0,'metrics':collections.defaultdict(list),'raw':collections.Counter(),'independentRaw':collections.Counter(),'sacBins':[0]*50,'roundBins':[0]*50,'classes':collections.Counter(),'classKeys':collections.defaultdict(list),'classMetrics':collections.defaultdict(lambda:collections.defaultdict(list)),'early':collections.defaultdict(lambda:collections.defaultdict(list)),'keys':[]})
 features={};pop=collections.Counter();checks=collections.Counter();mism=collections.Counter();paired=collections.defaultdict(lambda:collections.defaultdict(list));seen=set();teamNames=collections.defaultdict(collections.Counter);battle=collections.defaultdict(set)
 for l in gzip.open(O/(sys.argv[1] if len(sys.argv)>1 else 'games.jsonl.gz'),'rt'):
  r=json.loads(l)
  if r['key'] in seen:raise ValueError('duplicate '+r['key'])
  seen.add(r['key']);pop[r['src']]+=1;checks.update(r['check']);fkey=r['featuresKey'];features.setdefault(fkey,r['features'])
  for t in 'AB':mism.update(r[t]['compare'])
  if r['src']=='top' and r['stall']:pop['topStalled']+=1;continue
  if r['src']=='elite' and r['stall']:pop['eliteStalled']+=1;continue
  if r['layout']=='?':pop[r['src']+'UnknownLayout']+=1
  win=r.get('winner');roles=[]
  if r['src']=='top':
   if win:roles=[(win,'winner'),('B' if win=='A' else 'A','loser')]
   else:roles=[('A','draw'),('B','draw')];pop['topDraw']+=1
  elif r['src']=='online':
   roles=[(r['us'],'ours:'+r['set'])];family='v1' if r['set'].startswith('v1-w') else 'W0-W12';roles.append((r['us'],'ours:'+family))
   if r.get('oppId')!=545:roles.append((r['us'],'ours:'+family+':top6'))
  else:pass
  elite=p.get('eliteAliases',{}).get(r['key'],r if r['src']=='elite' else None)
  if elite:
   for t in 'AB':
    rank=elite.get('rank'+t)
    if rank is not None and rank<=10:roles.append((t,'elite-own'))
  for tm in set(t for t,role in roles):teamNames[fkey][r.get('team'+tm,r.get('set',r['src']))]+=1
  battle[fkey].add(r.get('battleId',r['key']))
  if r['src']=='top' and win:
   w=vals(r,win);lo=vals(r,'B' if win=='A' else 'A')
   for k in METRICS:
    if w[k] is not None and lo[k] is not None:paired[fkey][k].append(w[k]-lo[k])
  for t,role in roles:
   v=r[t];a=groups[(fkey,role)];a['N']+=1;a['raw']['wins']+=int(win==t);a['raw']['draws']+=int(not win);a['raw']['eliminated']+=int(v['final']['heads']==0);a['raw']['N500']+=int(r['rounds']==500);a['keys'].append(r['key']+':'+t);vm=vals(r,t)
   for k,x in vm.items():a['metrics'][k].append(x)
   for k in ['natural','pocketNatural','headRounds','pocketHR','split50','eligibleHR50']:a['raw'][k]+=v[k]
   a['raw']['sacEvents']+=len(v['sac']);a['independentRaw']['natural']+=v['independent']['natural'];a['independentRaw']['split50']+=v['independent']['split50'];a['independentRaw']['eligibleHR50']+=v['independent']['eligibleHR50'];a['independentRaw']['sacEvents']+=len(v['independent']['sac'])
   if vm['lineSacEat300'] is not None:a['raw']['lineSacEat300']+=vm['lineSacEat300'];a['independentRaw']['lineSacEat300']+=v['independent']['lineSacEat300']
   for c in [25,50,100,250]:
    x=v['cp'].get(str(c));y=v['independent']['cp'].get(str(c))
    if x:
     a['raw']['heads'+str(c)]+=x['heads'];a['raw']['mid'+str(c)]+=x['mid'];a['raw']['pocket'+str(c)]+=x['pocket'];a['raw']['checkpointN'+str(c)]+=1
    if y and x:
     for k in ['heads','mid','pocket']:a['independentRaw'][k+str(c)]+=y[k]
   for b in range(50):a['sacBins'][b]+=v['sacBins'][b];a['roundBins'][b]+=min(10,max(0,r['rounds']-10*b))
   mid=vm['middle100'];pn=vm['pocketIntakeShare'];cl='no-r100' if mid is None else 'pocket-harvest' if pn is not None and pn>=.2 else 'middle-heavy' if mid>=.4 else 'distributed'
   a['classes'][cl]+=1;a['classKeys'][cl].append(r['key']+':'+t)
   for field,value in vm.items():a['classMetrics'][cl][field].append(value)
   for c,e in v['early'].items():
    for k,x in e.items():a['early'][c][k].append(x)

 out={}
 geometryVerification=json.load(open(O/'geometry-verification.json'))
 for k,f in features.items():
  if k.endswith('/?'):
   for field in ['spawnTiles','spawnDensity','capacity','fountainShare','fountainTiles','centreSpawnShare','centreCapacityShare','pocketCapacityShare','edgeSpawnShare']:f[field]=None
   f['spawnPositions']=[]
  if k in geometryVerification['maps']:
   f['startVertexCut']=geometryVerification['maps'][k]['startVertexCut'];f.update(geometryVerification['maps'][k]['extraFeatures'])
 for (fkey,role),a in groups.items():
  target=out.setdefault(fkey,{'features':features[fkey],'cohorts':{},'pairedWinnerMinusLoser':{},'teamAppearanceCounts':dict(teamNames[fkey]),'battleN':len(battle[fkey])})
  metrics={k:stats(a['metrics'][k]) for k in METRICS}
  raw=a['raw'];rates=[n/d if d else None for n,d in zip(a['sacBins'],a['roundBins'])];late=[x for x in rates[20:] if x is not None];clock=next((i*10 for i in range(20,50) if rates[i] is not None and rates[i]>=.5*max(late)),None) if late and max(late)>0 else None
  raw['sacBinsN']=sum(a['sacBins']);pooled={'splitSpeed50':raw['split50']/raw['eligibleHR50'] if raw['eligibleHR50'] else None,'intakePerHR':raw['natural']/raw['headRounds'] if raw['headRounds'] else None,'pocketIntakeShare':raw['pocketNatural']/raw['natural'] if raw['natural'] else None,'pocketHRShare':raw['pocketHR']/raw['headRounds'] if raw['headRounds'] else None,'sacClockHalfPeak':clock,'sacRate240':rates[24],'sacRate250':rates[25],'sacStep250':rates[25]-rates[24] if rates[24] is not None and rates[25] is not None else None}
  for c in [25,50,100]:pooled['middle'+str(c)]=raw['mid'+str(c)]/raw['heads'+str(c)] if raw['heads'+str(c)] else None
  target['cohorts'][role]={'N':a['N'],'metrics':metrics,'pooled':pooled,'raw':dict(raw),'independentRaw':dict(a['independentRaw']),'sacBins':{'events':a['sacBins'],'teamRounds':a['roundBins'],'rate':rates},'classes':dict(a['classes']),'classKeys':dict(a['classKeys']),'classBehaviour':{cl:{'N':a['classes'][cl],'metrics':{field:stats(v) for field,v in ms.items()}} for cl,ms in a['classMetrics'].items()},'keys':a['keys'],'early':{c:{k:stats(v) for k,v in e.items()} for c,e in a['early'].items()}}
 for k,m in paired.items():out[k]['pairedWinnerMinusLoser']={m:stats(v) for m,v in m.items()}
 table.update(status='complete-counts' if len(seen)==len(p['tasks']) else 'partial-counts',updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),population={'frozenAt':p['frozenAt'],'eliteRefreshedAt':p.get('eliteRefreshedAt'),'eliteIndexN':len(p.get('eliteAliases',{})),'requested':len(p['tasks']),'processed':len(seen),'counts':dict(pop),'missing':[t['key'] for t in p['tasks'] if t['key'] not in seen]},maps=out,definitions={'checkpoint':'round start, conditional on reaching round; terminated games not carried forward','middle':'static shortest distance from starting bodies f in [0.4,0.6); wrap+kelp+portals','splitSpeed50':'splits r0-49 / length>=4 head-rounds r0-49','sac':'self inflicted death with free neighbour; operational proxy not intention','lineSacSourceShare300':'own-sacrifice share of final lineage intake in r300-499 (differs from packet line delivery share)','kingGrowth300_500':'(final king length - active ancestral length r300)/200; 500-round games only','kingSafeP10':'per-game p10 of four checkpoints r300/350/400/450, reachable enemy heads only','classes':'r100 absent; else pocket natural>=20%; else middle100>=40%; else distributed; descriptive not causal','confidence':'naive game-level CI descriptive only; held-out map/family validation is generalization evidence'},verification={'games':len(seen),'primaryLedgerChecks':dict(checks),'independentPerGameMismatch':dict(mism),'keyCountsStored':'maps.*.cohorts.*.raw and independentRaw; same frozen replay keys, decoder and layout identity shared'},missing=['conversion packet line share and independent pocket/safety enrichment','fits and partial-input validation','deep reads','report'])
 json.dump(table,open(O/'tables.json','w'),ensure_ascii=False,indent=1,allow_nan=False)
 print('COUNT TABLE',len(seen),dict(pop),dict(mism))
if __name__=='__main__':main()
