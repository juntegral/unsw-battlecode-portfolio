"""Second aggregation of independent replay-update evidence; no ML/group functions."""
import json,gzip,pathlib,collections,subprocess,shutil,datetime
O=pathlib.Path(__file__).resolve().parent
T=json.load(open(O/'tables.json'));P=json.load(open(O/'population.json'))
groups=collections.defaultdict(lambda:{'N':0,'eliminated':0,'splits':0,'deaths':0,'headons':0,'ram':0,'rammed':0,'deathCauses':collections.Counter(),'heads25':0,'heads100':0,'splitChild30N':0,'splitChild30Alive':0})
rawindex={}
for line in open(O/'rows.jsonl'):
 r=json.loads(line)
 if r.get('schemaVersion')==2:rawindex[r['key']]=r['raw']
for i,task in enumerate(P['tasks']):
 if i%100==0:
  m=subprocess.check_output(['memory_pressure','-Q'],text=True);pct=int(m.split('System-wide memory free percentage:')[1].split('%')[0]);free=shutil.disk_usage(O).free/2**30
  if pct<10 or free<21:raise RuntimeError('RESOURCE PAUSE')
 r=json.load(gzip.open(O/rawindex[task['key']]));I=r['independent'];deaths=I['deaths'];deathById={d['id']:d for d in deaths}
 if r['src'] in ['top','elite'] and (r['stall'] or not r['winner']):continue
 sides=[r['us']] if r.get('us') else ['A','B']
 for tm in sides:
  if r['src']=='local':
   engine='인식ON' if r['recognition']=='on' else ('F' if '-F-' in r['set'] else 'S');keys=['local/'+r['map']+'/'+engine,'local/'+r['set']]
   if r['recognition']=='off':keys+=['local/recognitionOff']
   if r['map']!='Trophy':keys+=['local/bundled/'+engine]
  elif r['src']=='online':keys=['online/'+r['set'],'online/v1' if r['set'].startswith('v1-w') else 'online/W0-W12']
  else:
   role='winner' if r['winner']==tm else 'loser';keys=[r['src']+'/'+role]
   ranks=[r.get('rankA'),r.get('rankB')]
   if r['src']=='top' and all(n is not None and 1<=n<=10 for n in ranks):keys+=['top/bothTop10/'+role]
   n=r.get('rankA' if tm=='A' else 'rankB')
   if r['src']=='elite' and n is not None and 1<=n<=10:keys+=['elite/rank10/'+role]
  ss=[s for s in I['splits'] if s['team']==tm];ds=[d for d in deaths if d['team']==tm];ct=[c for c in I['contacts'] if c['moverTeam']!=c['victimTeam']]
  extra={'splitL4':sum(s['kept']+s['childLen']==4 for s in ss),'split50to99':sum(50<=s['r']<100 for s in ss),'death50to99':sum(50<=d['r']<100 for d in ds),'headonDeath50to99':sum(50<=d['r']<100 and d['cause'] in ['ram','rammed'] for d in ds),'headonLengthBalance':sum((c['victimLen']-c['moverLen']) if c['moverTeam']==tm else (c['moverLen']-c['victimLen']) for c in ct)}
  own_dt=[v for k,v in r[tm]['ledger']['dt'].items() if k.split('|')[0] in ['ram','rammed']];other_dt=[v for k,v in r['B' if tm=='A' else 'A']['ledger']['dt'].items() if k.split('|')[0] in ['ram','rammed']]
  extra.update({'dropOwnDropped':sum(v[2] for v in own_dt),'dropOwnRecovered':sum(v[3] for v in own_dt),'dropOwnEnemyRecovered':sum(v[5] for v in own_dt),'dropEnemyRecovered':sum(v[5] for v in other_dt)})
  for k in keys:
   g=groups[k];g['N']+=1;g['eliminated']+=I['final'][tm]['heads']==0;g['splits']+=len(ss);g['deaths']+=len(ds);g['headons']+=len(ct);g['ram']+=sum(c['moverTeam']==tm for c in ct);g['rammed']+=sum(c['victimTeam']==tm for c in ct);g['deathCauses'].update(d['cause'] for d in ds)
   for field,value in extra.items():g[field]=g.get(field,0)+value
   for rd in [25,100]:
    c=next((x for x in I['curves'] if x['r']==rd),None);g['heads'+str(rd)]+=c[tm]['heads'] if c else I['final'][tm]['heads']
   for s in ss:
    if r['rounds']>s['r']+30:
     g['splitChild30N']+=1;g['splitChild30Alive']+=s['child'] not in deathById or deathById[s['child']]['r']>=s['r']+30
errors=[]
for k,g in groups.items():
 a=T['groups'][k]
 want={'N':a['N'],'eliminated':a['eliminated'],'splits':a['splitsDetailed']['N'],'deaths':a['deaths'],'headons':a['headons'],'ram':a['ram'],'rammed':a['rammed'],'deathCauses':a['deathCauses'],'heads25':round(a['curves']['25']['heads']['mean']*a['N']),'heads100':round(a['curves']['100']['heads']['mean']*a['N']),'splitChild30N':sum(b['alive30N'] for b in a['splitsDetailed']['beforeBins'].values()),'splitChild30Alive':sum(b['alive30'] for b in a['splitsDetailed']['beforeBins'].values())}
 want.update({'splitL4':a['splitsDetailed']['before'].get('4',0),'split50to99':a['phaseEvents'].get('50-99',{}).get('splits',0),'death50to99':a['phaseEvents'].get('50-99',{}).get('deaths',0),'headonDeath50to99':a['phaseEvents'].get('50-99',{}).get('headonDeaths',0),'headonLengthBalance':a['headonLengthBalance']})
 want.update({'dropOwnDropped':a['dropTrade']['ownDropped'],'dropOwnRecovered':a['dropTrade']['ownRecovered'],'dropOwnEnemyRecovered':a['dropTrade']['ownEnemyRecovered'],'dropEnemyRecovered':a['dropTrade']['enemyRecovered']})
 for f,v in want.items():
  if g[f]!=v:errors.append({'group':k,'field':f,'primary':v,'independent':g[f]})
json.dump({'at':datetime.datetime.now().astimezone().isoformat(),'method':'Python separately aggregates independent head/tail reconstruction for 17 fields; 4 drop fields use shared mass_ledger death (dt) instead of contact (ct) summaries; same frozen cohorts; no primary aggregation code','groups':groups,'comparedFields':list(want),'mismatchN':len(errors),'mismatches':errors},open(O/'verification.json','w'),ensure_ascii=False,indent=2)
print('INDEPENDENT GROUPS',len(groups),'mismatches',len(errors));print(errors[:5])
if errors:raise SystemExit(1)
