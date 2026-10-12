import json,pathlib,datetime,collections
O=pathlib.Path(__file__).resolve().parent;R=O.parents[1];p=json.load(open(O/'population.json'));existing={str(t['battleId'])+':'+str(t['gameId']):t for t in p['tasks'] if t['src'] in ['top','elite']};aliases={};new=[]
for l in open(R/'data/elite/index.jsonl'):
 if not l.strip():continue
 r=json.loads(l);base=str(r['battleId'])+':'+str(r['gameId'])
 if base in existing:key=existing[base]['key']
 else:
  key='elite:'+base;t={**r,'key':key,'src':'elite','file':str(R/'data/elite'/str(r['battleId'])/(str(r['gameId'])+'.replay.gz'))};new.append(t);existing[base]=t
 aliases[key]=r
p['tasks']+=new;p['eliteAliases']=aliases;p['eliteRefreshedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();p['eliteRefreshAdded']=len(new);p['missing']=[t['key'] for t in p['tasks'] if not pathlib.Path(t['file']).exists()];json.dump(p,open(O/'population.json','w'),ensure_ascii=False,indent=1)
print('REFRESH ELITE','index',len(aliases),'new',len(new),'missing',len(p['missing']))
