"""Independently recount optional rounded 56/64 head-budget errors from held-out predictions."""
import json,pathlib,collections,statistics,math
O=pathlib.Path(__file__).resolve().parent;T=json.load(open(O/'tables.json'));audit=[]
for target,f in T['fits'].items():
 if not target.startswith('heads'):continue
 for label,out in [('full',f)]+list(f['runtimeEarly'].items()):
  for variant in ['leaveFamilyOut','leaveGeometryFamilyOut']:
   for limit in [56,64]:
    errors=collections.defaultdict(list);sq=collections.defaultdict(list);n=0
    for p in out[variant]['predictions']:
     h=T['maps'][p['key']]['features']['initialHeads'];pred=min(limit,max(h,round(p['predicted'])));errors[p['family']].append(abs(pred-p['actual']));sq[p['family']].append((pred-p['actual'])**2);n+=1
    score={'N':n,'familyN':len(errors),'MAE':statistics.mean(map(statistics.mean,errors.values())),'RMSE':math.sqrt(statistics.mean(map(statistics.mean,sq.values()))),'perFamilyMAE':{k:statistics.mean(v) for k,v in errors.items()}}
    out.setdefault('roundedCapValidation',{}).setdefault(str(limit),{})[variant]=score
    if limit==56 and variant=='leaveFamilyOut':audit.append({'target':target,'input':label,'primaryMAE':out['integer56CapValidation']['MAE'],'recountMAE':score['MAE'],'match':abs(score['MAE']-out['integer56CapValidation']['MAE'])<1e-9})
T['capInterpretation']='Rule default and init UNIT_LIMIT is 64; optional 56 cap is a conservative budget experiment, not a rules limit. Runtime prototype reads observed unitLimit; unseen values have N=0 validation.'
json.dump(T,open(O/'tables.json','w'),ensure_ascii=False,indent=1,allow_nan=False)
json.dump({'N':len(audit),'mismatchN':sum(not a['match'] for a in audit),'counts':audit},open(O/'cap-verification.json','w'),indent=1)
print('CAP VERIFY',len(audit),'mismatch',sum(not a['match'] for a in audit))
