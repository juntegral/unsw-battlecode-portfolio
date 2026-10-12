"""Attach final audits and explicit interpretation limits; no replay mutation."""
import json,pathlib,datetime
O=pathlib.Path(__file__).resolve().parent
load=lambda name:json.load(open(O/name))
T=load('tables.json');F=load('fit-verification.json');G=load('geometry-verification.json');D=load('deep-reads.json');I=load('elite-inventory.json');M=load('metadata-repair.json')
assert not T['population']['missing'] and not T['verification']['enrichment']['missing']
assert not G['mismatch'] and not F['details']
T['verification'].update(geometry=G,fit=F,metadataRepair=M,roundedCaps=load('cap-verification.json'))
T['observability']=load('observability.json')
T['scoutReference']={'file':'scout.json','N':30,'interpretation':'static optimistic feasibility; bodies and splits omitted; sharing and unseen portal mates not guaranteed'}
T['deepReads']={'N':D['N'],'file':'deep-reads.json','selectionFile':'deep-selection.json','selection':'largest descriptive class per map-role, closest to cohort checkpoint means'}
T['sprintCheck']=I
T['behaviourRanges']={}
for y,f in T['fits'].items():T['behaviourRanges'][y]={'NLayouts':f['NLayouts'],'NMaps':f['NMapFamilies'],'range':f['observedMapRange'],'constantIsNotProofOfInvariance':True,'transferStatus':f['transferStatus']}
T['recommendations']={'NDeploymentGames':0,'runtimePrototype':'runtime_rules.py','modelUse':'diagnostic behavior targets, not optimized winning policy; runtime four-feature models; honor confidence and model support', 'headTarget':'round(model(area,initialHeads,observedKelpDensity,observedSpawnDensity)); clamp initialHeads..unitLimit; 64 is rules default; optional 56 is a conservative budget experiment only','demandBudget':'ceil(observed accessible successful appearance rate / target per-head intake); lower service estimate only, not total optimal heads','fortressCandidate':{'areaMax':1100,'initialKingMin':8,'certifiedCycleExtra':4,'requireProductivePocketOrGuard':True,'optimalClassificationN':0},'certifiedIsolationEnemyFrontierTarget':0,'exploration':{'scoutsPerStartingRegionMax':1,'updateRounds':[10,20,30],'respawnResetCandidateMin':4,'resetAccuracyValidationN':0},'conversion':{'checkRounds':[250,350,400],'reservationTTL':4,'firstDropAhead':[1,3],'largePacketBeforeRound':460,'after475FirstReceiptETA':[1,3],'protocolValidationN':0},'safety':{'candidateDistanceFloor':4,'openIngressTarget':[6,10],'routeCapacityExtra':4,'sprintSufficiency':False,'newPolicyN':0}}
T['status']='complete';T['missing']=[];T['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
json.dump(T,open(O/'tables.json','w'),ensure_ascii=False,indent=1,allow_nan=False)
print('FINAL TABLE',T['population']['processed'],'fits',len(T['fits']),'deep',D['N'])
