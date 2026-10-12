"""Independent tabular refit/interpreter and macro error recount; does not import fit.py."""
import json,pathlib,collections,math,statistics,fractions
O=pathlib.Path(__file__).resolve().parent
T=json.load(open(O/'tables.json'))
def wmedian(pairs):
 pairs=sorted(pairs);mass=sum(w for y,w in pairs);z=fractions.Fraction(0)
 for i,(y,w) in enumerate(pairs):
  z+=w
  if 2*z>=mass:return (y+pairs[i+1][0])/2 if 2*z==mass and i+1<len(pairs) else y
 return pairs[-1][0]
def independent_refit(rows,kind):
 ct=collections.Counter(r['family'] for r in rows);ww={r['key']:fractions.Fraction(1,ct[r['family']]) for r in rows};median=lambda a:wmedian([(r['y'],ww[r['key']]) for r in a])
 if kind=='constant' or len(rows)<3:return {'kind':'constant','value':median(rows)}
 if kind.startswith('iso:'):
  _,feature,s=kind.split(':');s=int(s);levels=collections.defaultdict(list)
  for r in rows:levels[s*r['x'][feature]].append(r)
  blocks=[]
  for x,a in sorted(levels.items()):
   blocks.append({'lo':x,'hi':x,'v':median(a),'rows':a})
   while len(blocks)>=2 and blocks[-2]['v']>blocks[-1]['v']:
    v=blocks.pop();u=blocks.pop();a=u['rows']+v['rows'];blocks.append({'lo':u['lo'],'hi':v['hi'],'v':median(a),'rows':a})
  return {'kind':'isotonic','feature':feature,'sign':s,'blocks':[{k:v[k] for k in ['lo','hi','v']} for v in blocks]}
 _,depth,features=kind.split(':');depth=int(depth)
 def node(a,d):
  v=median(a);best=None;minimum=sum(float(ww[r['key']])*abs(r['y']-v) for r in a)
  for f in features.split(',') if d else []:
   vals=sorted({r['x'][f] for r in a})
   for i in range(len(vals)-1):
    cut=(vals[i]+vals[i+1])/2;l=[r for r in a if r['x'][f]<=cut];rr=[r for r in a if r['x'][f]>cut]
    if len(l)<3 or len(rr)<3:continue
    loss=0
    for b in [l,rr]:
     med=median(b);loss+=sum(float(ww[r['key']])*abs(r['y']-med) for r in b)
    if best is None or loss<best[0]-1e-12:best=(loss,f,cut,l,rr)
  if best is None or best[0]>=minimum-1e-12:return {'value':v}
  _,f,cut,l,rr=best;return {'feature':f,'cut':cut,'left':node(l,d-1),'right':node(rr,d-1)}
 return {'kind':'tree','root':node(rows,depth)}
def eval_model(m,x):
 kind=m['kind']
 if kind=='constant':return m['value']
 if kind=='tree':
  n=m['root']
  while 'value' not in n:n=n['right'] if x[n['feature']]>n['cut'] else n['left']
  return n['value']
 z=x[m['feature']]*m['sign'];blocks=m['blocks']
 for i,b in enumerate(blocks):
  if z<=b['hi']:
   if i and z<b['lo']:
    a=blocks[i-1];return a['v']+(b['v']-a['v'])*(z-a['hi'])/(b['lo']-a['hi'])
   return b['v']
 return blocks[-1]['v']
def xvalue(f,k):return 999. if k=='startDistance' and f.get(k) is None else float(f.get(k) or 0)
def datasets(fit,early=None):
 out=[]
 for label in fit['mapLabels']:
  a=T['maps'][label['key']];x={k:xvalue(a['features'],k) for k in T['fitProtocol']['predefinedFeatures']}
  if early:
   c=a['cohorts']['winner']['early'][early]
   for k,field in [('kelpDensity','kelpDensityEstimate'),('spawnDensity','spawnDensityEstimate')]:x[k]=c[field]['mean']
  out.append({**label,'x':x})
 return out
checks=collections.Counter();result={};details=[]
for name,fit in T['fits'].items():
 result[name]={}
 variants=[('leaveLayoutOut',fit['leaveLayoutOut'],None),('leaveFamilyOut',fit['leaveFamilyOut'],None),('leaveGeometryFamilyOut',fit['leaveGeometryFamilyOut'],None)]+[('r'+r,a['leaveFamilyOut'],r) for r,a in fit['runtimeEarly'].items()]+[('r'+r+'Geometry',a['leaveGeometryFamilyOut'],r) for r,a in fit['runtimeEarly'].items()]
 for unit,folds,early in variants:
  rows=datasets(fit,early);by={r['key']:r for r in rows};errors=collections.defaultdict(list);sq=collections.defaultdict(list);baseerrors=collections.defaultdict(list);n=0
  for p in folds['predictions']:
   checks['predictionN']+=1;n+=1;train=[by[k] for k in p['trainingKeys']];test=by[p['key']]
   leakage=any(r['family']==test['family'] for r in train) if unit!='leaveLayoutOut' else p['key'] in p['trainingKeys'];checks['leakage']+=int(leakage);checks['geometryLeakage']+=int('Geometry' in unit and any(r['geometryFamily']==test['geometryFamily'] for r in train))
   m=independent_refit(train,p['selected']);v=eval_model(m,test['x']);pv=eval_model(p['model'],test['x']);checks['savedModelMismatch']+=int(abs(pv-p['predicted'])>1e-9);checks['refitPredictionMismatch']+=int(abs(v-p['predicted'])>1e-8)
   if abs(v-p['predicted'])>1e-8:details.append({'target':name,'unit':unit,'key':p['key'],'selected':p['selected'],'primary':p['predicted'],'independent':v})
   errors[test['family']].append(abs(v-test['y']));sq[test['family']].append((v-test['y'])**2);b=eval_model(independent_refit(train,'constant'),test['x']);baseerrors[test['family']].append(abs(b-test['y']))
  mae=statistics.mean(statistics.mean(v) for v in errors.values());rmse=math.sqrt(statistics.mean(statistics.mean(v) for v in sq.values()));baseline=statistics.mean(statistics.mean(v) for v in baseerrors.values())
  checks['scoreN']+=1;checks['MAEMismatch']+=int(abs(mae-folds['score']['MAE'])>1e-8);checks['RMSEMismatch']+=int(abs(rmse-folds['score']['RMSE'])>1e-8);checks['baselineMismatch']+=int(abs(baseline-folds['baseline']['MAE'])>1e-8)
  result[name][unit]={'N':n,'familyN':len(errors),'primaryMAE':folds['score']['MAE'],'independentMAE':mae,'primaryRMSE':folds['score']['RMSE'],'independentRMSE':rmse,'primaryBaselineMAE':folds['baseline']['MAE'],'independentBaselineMAE':baseline}
json.dump({'checks':dict(checks),'fits':result,'details':details,'independence':'separate Fraction family weights, robust median refit and model interpreter; nested selected candidate IDs shared; inner selector not independently reselected'},open(O/'fit-verification.json','w'),ensure_ascii=False,indent=1)
print('FIT VERIFY',dict(checks),'details',len(details))
