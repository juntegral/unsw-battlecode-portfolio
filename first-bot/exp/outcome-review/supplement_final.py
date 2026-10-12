#!/usr/bin/env python3
"""Final census supplements: independent terminal recount and paired latest economy."""
import collections,json,math,re,statistics as S,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'.cache/outcome-review'
mem=subprocess.check_output(['/usr/bin/memory_pressure'],text=True)
assert int(re.search(r'System-wide memory free percentage:\s*(\d+)%',mem)[1])>=10
assert int(subprocess.check_output(['/bin/df','-g','/'],text=True).splitlines()[-1].split()[3])>=20
A=json.load(open(C/'analysis.json'));M=json.load(open(C/'manifest.json'))
G=[json.loads(l) for l in open(C/'games.jsonl') if l.strip()]
E=json.load(open(C/'models-elite.json'))
def dist(xs):
 a=[x for x in xs if x is not None];nn=len(a)
 if not nn:return {'n':0,'mean':None,'ci':[None,None]}
 t=[0,12.706,4.303,3.182,2.776,2.571,2.447,2.365,2.306,2.262,2.228,2.201,2.179,2.160,2.145,2.131,2.120,2.110,2.101,2.093,2.086,2.080,2.074,2.069,2.064,2.060,2.056,2.052,2.048,2.045,2.042]
 tc=t[nn-1] if 1<nn<=31 else 1.96+(1.96**3+1.96)/(4*(nn-1)) if nn>31 else 0
 m=S.mean(a);h=tc*S.stdev(a)/math.sqrt(nn) if nn>1 else None
 return {'n':nn,'mean':m,'ci':[m-h,m+h] if h is not None else [None,None]}
def wilson(k,n):
 if not n:return [None,None]
 z=1.95996398454;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return [max(0,c-h),min(1,c+h)]
# Independent metadata traversal: do not obtain tie membership from the first audit.
ties=[];recount=collections.Counter();rule_errors=[]
for st in M['sets']:
 for p in sorted((R/'data/online'/st['set']).glob('game-*.json')):
  j=json.load(open(p))
  if j['teamAId']!=583 or j['teamBId'] not in [306,70,20,801,264,46,545]:continue
  a=j['replay']['result']['teamA'];b=j['replay']['result']['teamB'];winner=j['replay']['result']['winner']
  oc='W' if winner=='A' else 'L' if winner=='B' else 'D';recount[oc]+=1
  if a['dragonCount']==0 or b['dragonCount']==0:
   expect=None if a['dragonCount']==b['dragonCount'] else 'A' if a['dragonCount'] else 'B'
  else:
   av=(a['longestDragon'],a['totalLength']);bv=(b['longestDragon'],b['totalLength'])
   expect='A' if av>bv else 'B' if bv>av else None
  if expect!=winner:rule_errors.append(j['id'])
  if a['longestDragon']==b['longestDragon']:ties.append({'key':st['set']+':'+str(j['id']),'outcome':oc,'longest':a['longestDragon'],'totals':[a['totalLength'],b['totalLength']]})
T=json.load(open(C/'terminal-audit.json'))
assert sum(recount.values())==M['n']==1680 and not rule_errors
assert sorted(x['key'] for x in ties)==sorted(x['key'] for x in T['ties'])
assert dict(recount)==T['counts'] and not T['rawTieMismatches'] and not T['ruleMismatchCount']
latest=[g for g in G if g['wave']=='W12' and g['opponent']!=545 and g['family']=='r500']
paired=[g for g in latest if g['ourLineage300'] is not None and g['theirLineage300'] is not None]
flows=['Lineage300','LineNatural300','LineSac300','LineOwnOther300','LineEnemy300','LineSprint300','LineSplit300','Final']
paired_values={f:{'ours':dist(g['our'+f] for g in paired),'theirs':dist(g['their'+f] for g in paired),'enemyMinusOurs':dist(g['their'+f]-g['our'+f] for g in paired)} for f in flows}
scaled=[]
for f,s in [('headLogRatio100',math.log(2)),('fullLogNaturalRatio',math.log(2)),('currentKingDifference300',1),('lineSacDifference',1),('birthLogRatio',math.log(2)),('exposureDifference',-1)]:
 m=E['elite-single:'+f];q=m['coefficients'][0]
 scaled.append({'feature':f,'OR':math.exp(q['beta']*s),'CI':sorted(math.exp(z*s) for z in q['betaCI']),'N':m['informativeN'],'completeN':m['completeN'],'strata':m['strata']})
class_share={}
for prefix in ['win:','near:','lead:']:
 for era in ['waves','history','all']:
  rr=[g for g in G if era=='all' or g['era']==era]
  name={'win:':'winClass','near:':'nearClass','lead:':'leadClass'}[prefix]
  eligible=[g for g in rr if g.get(name)]
  counts=collections.Counter(g[name] for g in eligible)
  class_share[prefix+era]={'n':len(eligible),'classes':{k:{'n':nn,'shareCI':wilson(nn,len(eligible))} for k,nn in counts.items()}}
coverage={}
for era in ['waves','history','all']:
 rr=[g for g in G if era=='all' or g['era']==era]
 coverage[era]={'near':sum(bool(g.get('nearClass')) for g in rr),'lead':sum(bool(g.get('leadClass')) for g in rr),'nearAndLead':sum(bool(g.get('nearClass')) and bool(g.get('leadClass')) for g in rr)}
signals=[]
for era in ['waves','history']:
 for group in ['top6','DEV']:
  for oc in ['W','L']:
   rr=[g for g in G if g['era']==era and g['outcome']==oc and (g['opponent']!=545)==(group=='top6')]
   for label,fn in [('late-king-loss',lambda g:any(x['r']>=300 for x in g['theirRawKingDeaths'])),('king-sac',lambda g:any(x['cause']=='sac' for x in g['theirRawKingDeaths'])),('king-trapped',lambda g:any(x['cause']=='trap' for x in g['theirRawKingDeaths'])),('king-ally-head',lambda g:any(x['cause']=='allyHead' for x in g['theirRawKingDeaths'])),('king-enemy-head',lambda g:any(x['cause'] in ['ram','rammed'] for x in g['theirRawKingDeaths'])),('timeout',lambda g:g['theirFaults']>0)]:
    nn=sum(fn(g) for g in rr);signals.append({'era':era,'group':group,'outcome':oc,'signal':label,'n':len(rr),'count':nn,'ci':wilson(nn,len(rr))})
out={'terminalIndependentN':sum(recount.values()),'terminalIndependentCounts':dict(recount),'independentTieN':len(ties),'independentTies':ties,'independentRuleMismatchCount':len(rule_errors),'latestR500Top6N':len(latest),'latestNaturalRatioOfTotals':sum(g['ourNatural'] for g in latest)/sum(g['theirNatural'] for g in latest),'latestPairedN':len(paired),'latestPairedFlows':paired_values,'eliteScaledOR':scaled,'classShare':class_share,'nearLeadCoverage':coverage,'opponentSignals':signals}
with open(C/'final-supplement.json','x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'N':out['terminalIndependentN'],'tieN':len(ties),'latestPairedN':len(paired),'latestNaturalRatioOfTotals':out['latestNaturalRatioOfTotals'],'eliteScaledOR':scaled,'coverage':coverage},ensure_ascii=False))
