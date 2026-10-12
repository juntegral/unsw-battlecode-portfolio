import json,pathlib,collections
O=pathlib.Path(__file__).resolve().parent;T=json.load(open(O/'tables.json'));I=json.load(open(O/'key-independent.json'));out={};errors=[]
for o in T['ourGames']:
 a={k:0 for k in ['rammedN','priorN','priorFree2plus','priorLen2','fatalStep2plus','trapN','trapAllyBody','trapAllyHead','trapAnyAlly','trapEnemyBody']};a['trapReasons']=collections.Counter()
 contacts=[c for c in o['headons'] if c['victimTeam']==o['us']];a['rammedN']=len(contacts);a['fatalStep2plus']=sum(c['collisionStep']>=2 for c in contacts);prior=[c['victimLastTurn'] for c in contacts if c['victimLastTurn']];a['priorN']=len(prior);a['priorFree2plus']=sum(p['free']>=2 for p in prior);a['priorLen2']=sum(p['len']==2 for p in prior)
 ds=[d for d in o['deaths'] if d['cause']=='trap'];a['trapN']=len(ds)
 for d in ds:
  b=d['start']['blocked'];a['trapAllyBody']+=b['allyBody']>0;a['trapAllyHead']+=b['allyHead']>0;a['trapAnyAlly']+=b['allyBody']+b['allyHead']>0;a['trapEnemyBody']+=b['enemyBody']>0;a['trapReasons'][d.get('reason') or 'A']+=1
 if a!=I['perGame'][o['key']]:errors.append({'key':o['key'],'primary':a,'independent':I['perGame'][o['key']]})
 keys=['allOwn',o['src']+'/'+o['set']]
 if o['src']=='local' and o['map']!='Trophy':keys+=['local/bundled','local/'+o['map']]
 for k in keys:
  g=out.setdefault(k,{'N':0,**{f:0 for f in a if f!='trapReasons'},'trapReasons':collections.Counter()});g['N']+=1
  for f,v in a.items():
   if f=='trapReasons':g[f].update(v)
   else:g[f]+=v
for k,g in out.items():
 if g!=I['groups'][k]:errors.append({'group':k,'primary':g,'independent':I['groups'][k]})
json.dump({'N':len(T['ourGames']),'primaryGroups':out,'independentGroups':I['groups'],'mismatchN':len(errors),'mismatches':errors,'method':'fresh independent replay-update reconstruction in Node, primary table aggregation separately in Python; per game and pooled'},open(O/'key-verification.json','w'),ensure_ascii=False,indent=2)
print('KEY COMPARE',len(T['ourGames']),len(out),'mismatch',len(errors));print(errors[:2])
if errors:raise SystemExit(1)
