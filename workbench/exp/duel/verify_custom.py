"""Independent Python recount of custom-map active contacts from compressed stream."""
import json,gzip,collections,re
from verify import OUT,guard
guard()
C=json.loads((OUT/'custom-comparison.json').read_text());G=collections.defaultdict(lambda:collections.Counter());B=collections.defaultdict(collections.Counter);L=collections.defaultdict(collections.Counter)
for n,line in enumerate(gzip.open(OUT/'contacts.jsonl.gz','rt')):
 if n%100000==0:guard()
 e=json.loads(line)
 if not e['custom'] or e['reason']!='H':continue
 for team in ('A','B'):
  role='winner' if e['winner']==team else 'loser';labels=['custom/'+role]
  for field,base in [('us','ours'),('under','under')]:
   if e.get(field)==team:labels.extend([base+'/custom',base+'/custom/'+role])
  for label in labels:
   g=G[label];g['headContacts']+=1
   if e['teamById'][str(e['mover'])]!=team:g['passive']+=1;continue
   g['mover']+=1;a=e['lastDecisions'][str(e['mover'])][-1];d=a['visibleAlly']+1-a['visibleEnemy'];b='higher' if d>0 else 'lower' if d<0 else 'equal';B[label][b]+=1
   d=a['len']-e['lengths'][str(e['passive'])];l='longer' if d>0 else 'shorter' if d<0 else 'equal';L[label][l+'/'+b]+=1
   g['activeTaggedTrade']+=bool(re.search(r'\bTRADE\b',a['tag']))
checks={};m=[]
for k,v in G.items():
 independent=dict(v,activeBalance=dict(B[k]),activeLengthBalance=dict(L[k]));primary={f:C['groups'][k][f] for f in independent};checks[k]={'primary':primary,'independent':independent}
 if primary!=independent:m.append(k)
(OUT/'verification-custom.json').write_text(json.dumps({'groups':checks,'mismatches':m},ensure_ascii=False,indent=2))
print('CUSTOM RECOUNT groups',len(checks),'mismatches',m)
if m:raise SystemExit(1)
