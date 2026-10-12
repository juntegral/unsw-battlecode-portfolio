"""Mark early predictions that fail both holdout improvements; provide conservative reference medians."""
import json,pathlib,collections,statistics
O=pathlib.Path(__file__).resolve().parent;T=json.load(open(O/'tables.json'))
def wm(rows):
 c=collections.Counter(r['family'] for r in rows);p=sorted((r['y'],1/c[r['family']]) for r in rows);total=sum(w for y,w in p);mass=0
 for i,(y,w) in enumerate(p):
  mass+=w
  if 2*mass>=total:return (y+p[i+1][0])/2 if 2*mass==total and i+1<len(p) else y
for y,f in T['fits'].items():
 f['baselineModel']={'kind':'constant','value':wm(f['mapLabels'])}
 for r,e in f['runtimeEarly'].items():
  e['relativeMAEGain']=1-e['leaveFamilyOut']['score']['MAE']/e['leaveFamilyOut']['baseline']['MAE'] if e['leaveFamilyOut']['baseline']['MAE'] else 0
  e['geometryRelativeMAEGain']=1-e['leaveGeometryFamilyOut']['score']['MAE']/e['leaveGeometryFamilyOut']['baseline']['MAE'] if e['leaveGeometryFamilyOut']['baseline']['MAE'] else 0
  e['earlyFeatureRuleEvidence']=e['relativeMAEGain']>=.1 and e['geometryRelativeMAEGain']>=.1
  e['proposalModel']=e['model'] if e['earlyFeatureRuleEvidence'] else f['baselineModel']
  e['proposalCaveat']='reference behavior only; gate requires >=10% MAE improvement for named-map and morphology holdout, not significance or score-effect proof'
  if y.startswith('heads'):
   actual={a['key']:a for a in f['mapLabels']};err=collections.defaultdict(list)
   for p in e['leaveFamilyOut']['predictions']:
    pred=min(64,max(T['maps'][p['key']]['features']['initialHeads'],round(wm([actual[k] for k in p['trainingKeys']]))));err[p['family']].append(abs(pred-p['actual']))
   e['roundedBaseline64MAE']=statistics.mean(map(statistics.mean,err.values()))
json.dump(T,open(O/'tables.json','w'),ensure_ascii=False,indent=1,allow_nan=False)
print('EARLY GATES',[(y,r) for y,f in T['fits'].items() for r,e in f['runtimeEarly'].items() if e['earlyFeatureRuleEvidence']])
