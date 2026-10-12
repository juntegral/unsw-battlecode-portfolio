"""Correct ping metadata from decoder's sonarBySender; behavioral raw counts remain untouched."""
import gzip,json,pathlib,collections,hashlib
O=pathlib.Path(__file__).resolve().parent
fix={}
for l in gzip.open(O/'conversion.jsonl.gz','rt'):
 r=json.loads(l);fix[r['key']]={'stall':r['stall'],'A':r['A']['pings'],'B':r['B']['pings'],'AI':r['A']['independent']['pings'],'BI':r['B']['independent']['pings']}
c=collections.Counter();details=[]
with gzip.open(O/'games-corrected.jsonl.gz','wt',compresslevel=6) as out:
 for l in gzip.open(O/'games.jsonl.gz','rt'):
  r=json.loads(l);x=fix[r['key']];c['N']+=1
  if r['stall']!=x['stall']:c['stallChanged']+=1;details.append({'key':r['key'],'old':r['stall'],'new':x['stall']})
  primaryStall=[t for t in r['stall'] if x[t]==0];c['stallMismatch']+=int(primaryStall!=x['stall']);r['stall']=primaryStall;r['stallIndependent']=x['stall']
  for tm in 'AB':
   c['pingFieldsChanged']+=int(r[tm]['pings']!=x[tm]);r[tm]['pings']=x[tm];r[tm]['independent']['pings']=x[tm+'I'];r[tm]['compare']['pings']=int(x[tm]!=x[tm+'I'])
  out.write(json.dumps(r,separators=(',',':'),ensure_ascii=False)+'\n')
(O/'games-corrected.jsonl.gz').replace(O/'games.jsonl.gz')
json.dump({'counts':dict(c),'changedStallKeys':details,'reason':'fast decoder strips sonarPing events; sonarBySender is authoritative; both separately assigned sender teams reconstructed from initial+split IDs','allBehaviorRowsPreserved':True},open(O/'metadata-repair.json','w'),ensure_ascii=False,indent=1)
print('METADATA REPAIR',dict(c))
