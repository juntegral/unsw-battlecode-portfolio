#!/usr/bin/env python3
"""Full class trajectories, separate elite feature trends, independent top-cache sums."""
import ast,collections,json,math,re,statistics as S,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'.cache/outcome-review';A=json.load(open(C/'analysis.json'))
source=ast.parse((R/'exp/outcome-review/extend_analysis.py').read_text())
names={'dist','tcrit','wilson','cf','ibeta','pvalue'}
exec(compile(ast.Module(body=[z for z in source.body if isinstance(z,ast.FunctionDef) and z.name in names],type_ignores=[]),'descriptive-functions','exec'),globals())
last=0
def guard():
 global last
 if time.monotonic()-last<10:return
 last=time.monotonic();m=subprocess.check_output(['/usr/bin/memory_pressure'],text=True)
 assert int(re.search(r'System-wide memory free percentage:\s*(\d+)%',m)[1])>=10,'PAUSE memory'
 assert int(subprocess.check_output(['/bin/df','-g','/'],text=True).splitlines()[-1].split()[3])>=20,'PAUSE disk'
guard();G=list(map(json.loads,open(C/'games.jsonl')))
featureTrends={}
features=list(json.load(open(C/'extensions.json'))['featureWaveTrends'])
for group in ['top6','DEV']:
 trends={}
 for f in features:
  pts=[]
  for w in A['waveNames']:
   rr=[g for g in G if g['wave']==w and (g['opponent']!=545)==(group=='top6') and g[f] is not None]
   if rr:pts.append((rr[0]['waveOrder'],S.mean(g[f] for g in rr),len(rr)))
  nn=len(pts);xm=S.mean(x for x,y,n in pts);ym=S.mean(y for x,y,n in pts);xx=sum((x-xm)**2 for x,y,n in pts)
  b=sum((x-xm)*(y-ym) for x,y,n in pts)/xx;a=ym-b*xm
  se=math.sqrt(sum((y-a-b*x)**2 for x,y,n in pts)/(nn-2)/xx);h=tcrit(nn-2)*se
  trends[f]={'waveN':nn,'gameN':sum(n for x,y,n in pts),'slope':b,'ci':[b-h,b+h],'p':pvalue(b/se,nn-2) if se else 1}
 ordered=sorted(trends,key=lambda f:trends[f]['p']);q=1
 for i in range(len(ordered),0,-1):
  f=ordered[i-1];q=min(q,trends[f]['p']*len(ordered)/i);trends[f]['BHq']=q
 featureTrends[group]=trends
curves={}
for era in ['all','waves']:
 curves[era]={}
 for cl in ['length-race','opponent-late-king-loss','opponent-elimination']:
  rr=[g for g in G if g.get('winClass')==cl and (era=='all' or g['era']==era)]
  cells={(g['map'],g['opponent']) for g in rr}
  control=[g for g in G if g['outcome']=='L' and (g['map'],g['opponent']) in cells and (era=='all' or g['era']==era)]
  metrics={}
  for t in [10,50,100,250,300,400]:
   metrics[str(t)]={f:dist(g.get(f+str(t)) for g in rr) for f in ['ourHeads','theirHeads','ourKing','theirKing']}
   metrics[str(t)]['controlOurHeads']=dist(g.get('ourHeads'+str(t)) for g in control)
   metrics[str(t)]['controlOurKing']=dist(g.get('ourKing'+str(t)) for g in control)
  curves[era][cl]={'n':len(rr),'controlN':len(control),'checkpoints':metrics}
# Read every top-cache row independently, sum rather than reusing analysis arrays.
acc=collections.defaultdict(lambda:{'n':0,'metrics':collections.defaultdict(lambda:[0,0])})
for line in open(R/'.cache/mass-ledger/top-sample.jsonl'):
 guard()
 if not line.strip():continue
 g=json.loads(line);z=acc[g['kind']];z['n']+=1
 if g['rounds']!=500 or g['winner'] not in ('A','B'):continue
 for prefix,side in [('win',g['winner']),('lose','B' if g['winner']=='A' else 'A')]:
  vals={'Final':g[side]['st']['king'][-1],'Heads100':g[side]['st']['units'][10]}
  cp=(g[side].get('lin') or {}).get('cp',{}).get('300')
  if cp:vals['LineSac']=cp['eat'][1]
  for metric,v in vals.items():z['metrics'][prefix+metric][0]+=1;z['metrics'][prefix+metric][1]+=v
topAudit={};errors=[]
for kind,z in acc.items():
 first=A['topVsTop'][kind]
 if z['n']!=first['n']:errors.append(kind+':N')
 topAudit[kind]={'primaryN':first['n'],'independentN':z['n'],'metrics':{}}
 for metric,(nn,ss) in z['metrics'].items():
  primary=first[metric];mm=ss/nn
  if nn!=primary['n'] or abs(mm-primary['mean'])>1e-9:errors.append(kind+':'+metric)
  topAudit[kind]['metrics'][metric]={'primaryN':primary['n'],'independentN':nn,'primaryMean':primary['mean'],'independentMean':mm}
assert not errors
out={'featureTrendsByGroup':featureTrends,'winClassTrajectories':curves,'topCacheIndependent':topAudit,'topCacheMismatchCount':len(errors)}
with open(C/'review-extra.json','x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'topCache':{k: {'primaryN':z['primaryN'],'independentN':z['independentN']} for k,z in topAudit.items()},'groupTrends':{gr:{f:z for f,z in d.items() if f in ['ourHeads100','ourFinal','ourLineSac300','ourExposure']} for gr,d in featureTrends.items()}},ensure_ascii=False))
