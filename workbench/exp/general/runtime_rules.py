"""Reviewable unknown-map target prototype. No bot files are changed; effects untested."""
import pathlib,json,math
O=pathlib.Path(__file__).resolve().parent

def predict(model,features):
 if model['kind']=='constant':return model['value']
 if model['kind']=='tree':
  n=model['root']
  while 'value' not in n:n=n['left'] if features[n['feature']]<=n['cut'] else n['right']
  return n['value']
 z=model['sign']*features[model['feature']];b=model['blocks']
 for i,v in enumerate(b):
  if z<=v['hi']:
   if i and z<v['lo']:
    a=b[i-1];return a['v']+(v['v']-a['v'])*(z-a['hi'])/(v['lo']-a['hi'])
   return v['v']
 return b[-1]['v']
def unknown_targets(observed,confidence):
 """observed supplies area, initialHeads, measured kelp/spawn density; confidence is caller knowledge."""
 t=json.load(open(O/'tables.json'));out={'targets':{},'warnings':[],'deploymentTrialsN':0}
 required=['area','initialHeads','kelpDensity','spawnDensity']
 if 'unitLimit' not in observed:raise ValueError('Need runtime init unitLimit to clamp heads on an unseen map')
 early='10' if observed.get('round',30)<=10 else '30'
 out['inputCalibrationRound']=int(early)
 if any(k not in observed for k in required):raise ValueError('Need the four explicitly observed runtime inputs, no hidden-gap fallback')
 for metric in ['heads25','heads50','heads100','heads250','middle100','splitSpeed50']:
  f=t['fits'][metric];m=f['runtimeEarly'][early]['proposalModel'];v=predict(m,observed)
  if metric.startswith('heads'):v=min(observed['unitLimit'],max(observed['initialHeads'],round(v)))
  if metric.startswith('middle'):v=min(1,max(0,v))
  out['targets'][metric]={'value':v,'conditionalOnReachingRound':metric.startswith('heads'),'usesFeatureRule':f['runtimeEarly'][early]['earlyFeatureRuleEvidence'],'familyMAE':f['runtimeEarly'][early]['leaveFamilyOut']['score']['MAE'] if f['runtimeEarly'][early]['earlyFeatureRuleEvidence'] else f['runtimeEarly'][early]['leaveFamilyOut']['baseline']['MAE'],'familyN':f['runtimeEarly'][early]['leaveFamilyOut']['score']['familyN'],'geometryHoldoutMAE':f['runtimeEarly'][early]['leaveGeometryFamilyOut']['score']['MAE'] if f['runtimeEarly'][early]['earlyFeatureRuleEvidence'] else f['runtimeEarly'][early]['leaveGeometryFamilyOut']['baseline']['MAE']}
 if not confidence.get('frontierMetricDefined'):out['warnings'].append('middle share requires verified starting-body distance geometry; reference target is not an allocation command')
 if confidence.get('certifiedIsolation'):
  out['plan']='isolated economy + conversion';out['targets']['middle100']['value']=0;out['enemyFrontierHeads']=0
 elif observed['area']<=1100 and confidence.get('initialKingLength',0)>=8 and confidence.get('knownCycleTiles',0)>=confidence.get('initialKingLength',0)+4 and confidence.get('productivePocketGuardConfirmed'):
  out['plan']='fortress candidate; preserve seed king and keep producers'
 else:out['plan']='swarm survey and production; reconsider as confidence improves'
 if not confidence.get('alliedSharingConfirmed'):out['warnings'].append('Early fitted inputs were allied-vision union means: use local confidence, not assumed global knowledge')
 if not confidence.get('resetRateReliable'):out['warnings'].append('Successful spawn count is a lower bound, not hidden potential rate; do not cap demand from this alone')
 for k in required:
  bounds=t['fits']['heads100']['runtimeEarly'][early]['featureSupport'][k]
  if observed[k]<bounds['min'] or observed[k]>bounds['max']:out['warnings'].append(k+' outside early-input feature support; map-family CV does not guarantee extrapolation')
 out['warnings'].append('These targets predict observed elite behavior; new engine score/win effect N=0')
 return out
if __name__=='__main__':
 import sys
 x=json.load(sys.stdin);print(json.dumps(unknown_targets(x['observed'],x.get('confidence',{})),ensure_ascii=False,indent=1))
