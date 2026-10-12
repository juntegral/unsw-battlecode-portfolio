"""Tiny robust regressors, nested leave-layout/family-out selection, equal family weight."""
import json,math,statistics,collections,pathlib,datetime,random
from resource_guard import guard
O=pathlib.Path(__file__).resolve().parent
FEATURES=['area','initialHeads','initialMass','kelpDensity','spawnDensity','capacity','fountainShare','pocketShare','pocketCapacityShare','corridorDegree2Share','meanDegree','startDistance','isolated','centreSpawnShare','centreCapacityShare','edgeSpawnShare','middleAreaShare','openBoundaryShare','portalPairs','initialKing','homeCapacity','startVertexCut','corridorWidthMean','corridorWidthMedian']
RUNTIME=['area','initialHeads','kelpDensity','spawnDensity']
YMETRICS=['heads25','heads50','heads100','heads250','middle25','middle50','middle100','splitSpeed50','intakePerHR','pocketIntakeShare','pocketHRShare','sacOnset20','sacOnset50','sacClockHalfPeak','sacStep250','lineSacEat300','lineShare300','lineSacSourceShare300','kingGrowth300_500','kingSafeP10','finalKing']

def med(vals,ws):
 a=sorted(zip(vals,ws));target=sum(ws)/2;s=0
 for i,(v,w) in enumerate(a):
  s+=w
  if s>=target:return (v+a[i+1][0])/2 if s==target and i+1<len(a) else v
 return a[-1][0]
def weights(rows):
 c=collections.Counter(r['family'] for r in rows);return [1/c[r['family']] for r in rows]
def fit(rows,kind):
 w=weights(rows);y=[r['y'] for r in rows];base=med(y,w)
 if kind=='constant' or len(rows)<3:return {'kind':'constant','value':base}
 if kind.startswith('iso:'):
  _,f,sign=kind.split(':');sign=int(sign);pairs=sorted(zip([sign*r['x'][f] for r in rows],y,w));blocks=[]
  levels=collections.defaultdict(list)
  for x,v,a in pairs:levels[x].append((v,a))
  for x,values in sorted(levels.items()):
   ys=[v for v,a in values];ws=[a for v,a in values];blocks.append({'lo':x,'hi':x,'ys':ys,'ws':ws,'v':med(ys,ws)})
   while len(blocks)>1 and blocks[-2]['v']>blocks[-1]['v']:
    b=blocks.pop();a=blocks.pop();ys=a['ys']+b['ys'];ws=a['ws']+b['ws'];blocks.append({'lo':a['lo'],'hi':b['hi'],'ys':ys,'ws':ws,'v':med(ys,ws)})
  return {'kind':'isotonic','feature':f,'sign':sign,'blocks':[{k:b[k] for k in ['lo','hi','v']} for b in blocks]}
 # depth 1/2 median-leaf tree; >=3 layouts per leaf; 19 feature candidates all trained only on training layouts.
 depth=int(kind.split(':')[1]);feat=kind.split(':')[2].split(',')
 def grow(ids,level):
  yy=[y[i] for i in ids];ww=[w[i] for i in ids];v=med(yy,ww);loss=sum(ww[j]*abs(yy[j]-v) for j in range(len(ids)));best=None
  if level==0:return {'value':v}
  for f in feat:
   xs=sorted(set(rows[i]['x'][f] for i in ids))
   for a,b in zip(xs,xs[1:]):
    cut=(a+b)/2;left=[i for i in ids if rows[i]['x'][f]<=cut];right=[i for i in ids if rows[i]['x'][f]>cut]
    if min(len(left),len(right))<3:continue
    cost=0
    for js in [left,right]:
     vv=med([y[i] for i in js],[w[i] for i in js]);cost+=sum(w[i]*abs(y[i]-vv) for i in js)
    if best is None or cost<best[0]-1e-12:best=(cost,f,cut,left,right)
  if best is None or best[0]>=loss-1e-12:return {'value':v}
  _,f,cut,left,right=best;return {'feature':f,'cut':cut,'left':grow(left,level-1),'right':grow(right,level-1)}
 return {'kind':'tree','root':grow(list(range(len(rows))),depth)}
def predict(m,x):
 if m['kind']=='constant':return m['value']
 if m['kind']=='isotonic':
  z=m['sign']*x[m['feature']];bs=m['blocks']
  if z<=bs[0]['hi']:return bs[0]['v']
  for a,b in zip(bs,bs[1:]):
   if z<=b['hi']:
    if z<b['lo'] and b['lo']>a['hi']:return a['v']+(b['v']-a['v'])*(z-a['hi'])/(b['lo']-a['hi'])
    return b['v']
  return bs[-1]['v']
 n=m['root']
 while 'feature' in n:n=n['left'] if x[n['feature']]<=n['cut'] else n['right']
 return n['value']
def candidates(features):return ['constant']+['iso:'+f+':'+str(s) for f in features for s in [1,-1]]+['tree:1:'+','.join(features),'tree:2:'+','.join(features)]
def cv(rows,kind,unit):
 predictions=[]
 for group in sorted(set(r[unit] for r in rows)):
  train=[r for r in rows if r[unit]!=group];test=[r for r in rows if r[unit]==group]
  if not train:continue
  m=fit(train,kind)
  for r in test:predictions.append({'key':r['key'],'family':r['family'],'actual':r['y'],'predicted':predict(m,r['x']),'holdout':group})
 return predictions
def score(ps):
 if not ps:return {'N':0,'MAE':None}
 groups=collections.defaultdict(list)
 for p in ps:groups[p['family']].append(p)
 per={k:statistics.mean(abs(p['predicted']-p['actual']) for p in vs) for k,vs in groups.items()}
 return {'N':len(ps),'familyN':len(groups),'MAE':statistics.mean(per.values()),'RMSE':math.sqrt(statistics.mean(statistics.mean((p['predicted']-p['actual'])**2 for p in vs) for vs in groups.values())),'maxError':max(abs(p['predicted']-p['actual']) for p in ps),'perFamilyMAE':per}
def select(rows,ks):
 # Inner holdouts always drop every layout of one named map family.
 scores=[(score(cv(rows,k,'family'))['MAE'],i,k) for i,k in enumerate(ks)];scores=[a for a in scores if a[0] is not None];best=min(scores)
 base=scores[0][0]
 # Prefer the constant if the inner gain is less than 3%; a selection guard, not a significance test.
 return 'constant' if best[0]>=.97*base else best[2]
def nested(rows,ks,unit):
 ps=[]
 for group in sorted(set(r[unit] for r in rows)):
  train=[r for r in rows if r[unit]!=group];test=[r for r in rows if r[unit]==group];chosen=select(train,ks);m=fit(train,chosen)
  for r in test:ps.append({'key':r['key'],'family':r['family'],'holdout':group,'actual':r['y'],'predicted':predict(m,r['x']),'selected':chosen,'trainingKeys':[r['key'] for r in train],'model':m})
 return {'score':score(ps),'baseline':score(cv(rows,'constant',unit)),'predictions':ps}
def feature_value(f,k):
 v=f.get(k);return 999 if k=='startDistance' and v is None else float(v or 0)
def geometry_family(f):
 if f['isolated']:return 'isolated'
 if f['startDistance'] is not None and f['startDistance']>=40:return 'long-approach'
 if f['area']>=1500:return 'large-board'
 if f.get('initialKing',0)>=8 and f['area']<=1100:return 'seed-fortress'
 return 'compact-contact'
def rows_for(T,y,early=None):
 rows=[]
 for key,a in T['maps'].items():
  if key.endswith('/?') or 'winner' not in a['cohorts']:continue
  c=a['cohorts']['winner'];m=c['metrics'].get(y);v=c['pooled'].get(y,m.get('mean') if m else None)
  if v is None:continue
  x={k:feature_value(a['features'],k) for k in FEATURES}
  if early is not None:
   e=c['early'].get(str(early),{})
   for k,ek in [('kelpDensity','kelpDensityEstimate'),('spawnDensity','spawnDensityEstimate')]:
    if not e.get(ek,{}).get('N'):break
    x[k]=e[ek]['mean']
  rows.append({'key':key,'family':key.rsplit('/',1)[0],'geometryFamily':geometry_family(a['features']),'y':v,'N':m.get('N',c['N']) if m else c['N'],'x':x})
 return rows

def main():
 resources=[guard()];T=json.load(open(O/'tables.json'));fits={}
 for y in YMETRICS:
  resources.append(guard())
  rows=rows_for(T,y)
  if len(rows)<8:continue
  ks=candidates(FEATURES);finalK=select(rows,ks)
  out={'NLayouts':len(rows),'NMapFamilies':len(set(r['family'] for r in rows)),'target':y,'mapLabels':[{k:r[k] for k in ['key','family','geometryFamily','y','N']} for r in rows],'featureSupport':{k:{'min':min(r['x'][k] for r in rows),'max':max(r['x'][k] for r in rows)} for k in FEATURES},'selection':'nested inner leave-family-out; 3% inner gain guard; median leaves; >=3 layouts/leaf; equal total weight per family','fittedKind':finalK,'model':fit(rows,finalK),'leaveLayoutOut':nested(rows,ks,'key'),'leaveFamilyOut':nested(rows,ks,'family'),'leaveGeometryFamilyOut':nested(rows,ks,'geometryFamily'),'perFeatureScreen':{}}
  for f in FEATURES:
   # Direction selected inside each outer fold for this single feature.
   one=['constant','iso:'+f+':1','iso:'+f+':-1'];out['perFeatureScreen'][f]={'leaveFamilyOut':nested(rows,one,'family')['score'],'model':fit(rows,select(rows,one))}
  out['runtimeEarly']={}
  for early in [10,30]:
   erows=rows_for(T,y,early);ek=candidates(RUNTIME);chosen=select(erows,ek);out['runtimeEarly'][str(early)]={'input':'observed allied union means; spawn identity uses visible countdown support oracle; delivery not guaranteed','fittedKind':chosen,'featureSupport':{k:{'min':min(r['x'][k] for r in erows),'max':max(r['x'][k] for r in erows)} for k in RUNTIME},'model':fit(erows,chosen),'leaveFamilyOut':nested(erows,ek,'family'),'leaveGeometryFamilyOut':nested(erows,ek,'geometryFamily')}
  if y.startswith('heads'):
   for e in out['runtimeEarly'].values():
    pp=[]
    for pred in e['leaveFamilyOut']['predictions']:
     f=T['maps'][pred['key']]['features'];pp.append({**pred,'predicted':min(56,max(f['initialHeads'],round(pred['predicted'])))})
    e['integer56CapValidation']=score(pp)
  a=out['leaveFamilyOut']['score'];b=out['leaveFamilyOut']['baseline'];out['partialRoleShift']={}
  for role in ['ours:W0-W12','ours:v1','elite-own']:
   ps=[]
   for pred in out['runtimeEarly']['30']['leaveFamilyOut']['predictions']:
    co=T['maps'][pred['key']]['cohorts'].get(role);row=next(r for r in rows if r['key']==pred['key']);xx=dict(row['x'])
    if not co or '30' not in co['early']:continue
    ee=co['early']['30'];good=True
    for f,ef in [('kelpDensity','kelpDensityEstimate'),('spawnDensity','spawnDensityEstimate')]:
     if not ee[ef]['N']:good=False;break
     xx[f]=ee[ef]['mean']
    if good:ps.append({**pred,'predicted':predict(pred['model'],xx),'inputN':ee['coverage']['N']})
   out['partialRoleShift'][role]={'score':score(ps),'predictions':ps,'caveat':'held-out terrain features estimated by different explorer policy; target remains held-out elite winner behavior'}
  if y.startswith('heads'):
   pp=[]
   for pred in out['leaveFamilyOut']['predictions']:
    f=T['maps'][pred['key']]['features'];pp.append({**pred,'predicted':min(56,max(f['initialHeads'],round(pred['predicted'])))})
   out['integer56CapValidation']=score(pp)
  out['relativeMAEGain']=1-a['MAE']/b['MAE'] if b['MAE'] else 0
  ga=out['leaveGeometryFamilyOut']['score']['MAE'];gb=out['leaveGeometryFamilyOut']['baseline']['MAE'];out['geometryRelativeMAEGain']=1-ga/gb if gb else 0;out['geometryFamiliesN']=len(set(r['geometryFamily'] for r in rows))
  rng=random.Random(583);pf=a['perFamilyMAE'];pb=b['perFamilyMAE'];families=sorted(pf);boot=[]
  for _ in range(2000):
   drawn=[rng.choice(families) for _ in families];bb=statistics.mean(pb[k] for k in drawn);boot.append(1-statistics.mean(pf[k] for k in drawn)/bb if bb else 0)
  boot.sort();out['relativeMAE95ByFamily']=[boot[50],boot[1949]];out['bootstrapCaveat']='descriptive sensitivity over 10 families; overlapping CV training folds; not a guaranteed unseen-map interval'
  out['observedMapRange']=[min(r['y'] for r in rows),max(r['y'] for r in rows)]
  out['transferStatus']='candidate' if out['relativeMAEGain']>=.1 and out['relativeMAE95ByFamily'][0]>0 and out['geometryRelativeMAEGain']>=.1 else 'fragile-gain' if out['relativeMAEGain']>=.1 else 'no-evidence-of-useful-feature-rule'
  fits[y]=out;print(y,'oracle',round(a['MAE'],4),'baseline',round(b['MAE'],4),'gain',round(out['relativeMAEGain'],3),'chosen',finalK,'r30',round(out['runtimeEarly']['30']['leaveFamilyOut']['score']['MAE'],4),flush=True)
 T['resourceChecksFit']=resources;T['fits']=fits;T['fitProtocol']={'predefinedFeatures':FEATURES,'runtimeFeatures':RUNTIME,'unit':'15 layouts; 10 named map families; neither N=20k independent maps','geometryFamilyRule':'isolated first; else start distance>=40; else area>=1500; else initialKing>=8 & area<=1100; else compact-contact. Fixed before fit, descriptive stress test.', 'oracleCaveat':'full-map gaps/start distances/2-core are diagnostic reference, not early runtime knowledge','selectionLeakage':'all choice inside outer holdout; per-feature screens exploratory; final all-map model for proposed engine only','NModelDeploymentTrials':0};T['status']='complete-fits';T['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();json.dump(T,open(O/'tables.json','w'),ensure_ascii=False,indent=1,allow_nan=False)
if __name__=='__main__':main()
