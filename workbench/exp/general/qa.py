"""Final structural/resource audit. Raw metrics and fits were independently recounted."""
import json,gzip,pathlib,collections,re,hashlib,datetime
from resource_guard import guard
O=pathlib.Path(__file__).resolve().parent;R=O.parents[1]
load=lambda name:json.load(open(O/name))
T=load('tables.json');P=load('population.json');E=load('metadata-repair.json');F=load('fit-verification.json');G=load('geometry-verification.json');checks=collections.Counter();issues=[]
def check(name,ok,detail=None):
 checks[name]+=1
 if not ok:issues.append({'check':name,'detail':detail})
keys={t['key'] for t in P['tasks']}
for name in ['games.jsonl.gz','conversion.jsonl.gz']:
 seen=set();n=0
 for line in gzip.open(O/name,'rt'):
  r=json.loads(line);n+=1;seen.add(r['key'])
 check('rawKeys',seen==keys,{'file':name,'N':n,'uniqueN':len(seen),'expected':len(keys)})
 check('rawDuplicates',n==len(seen),name)
check('populationProcessed',T['population']['processed']==len(keys))
check('missing',not T['missing'] and not T['population']['missing'] and not T['verification']['enrichment']['missing'])
for label,counts in [('primary',T['verification']['primaryLedgerChecks']),('independent',T['verification']['independentPerGameMismatch']),('enrichPrimary',T['verification']['enrichment']['primaryChecks']),('enrichIndependent',T['verification']['enrichment']['independentMismatch'])]:
 for field,value in counts.items():check('recountZero',value==0,(label,field,value))
check('metadataStall',E['counts']['stallMismatch']==0,E)
check('geometry',not G['mismatch'])
check('roundedCaps',load('cap-verification.json')['mismatchN']==0)
check('prototypeSmoke',load('prototype-smoke.json')['passed'] and load('prototype-smoke.json')['NDeploymentGames']==0)
for field,value in F['checks'].items():
 if field not in ['predictionN','scoreN']:check('fitIndependentZero',value==0,(field,value))
for key,a in T['maps'].items():
 for role,c in a['cohorts'].items():
  check('classPartition',sum(c['classes'].values())==c['N'],(key,role))
  check('cohortKeys',len(c['keys'])==len(set(c['keys']))==c['N'],(key,role))
  check('classKeyPartition',set(c['keys'])=={k for v in c['classKeys'].values() for k in v},(key,role))
  for cl,v in c['classBehaviour'].items():check('classBehaviourN',v['N']==c['classes'][cl],(key,role,cl))
  for field,value in c['independentRaw'].items():check('cohortRawRecount',value==c['raw'][field],(key,role,field))
  x=c['conversion'];check('conversionN',x['N']==c['N'] and x['N500']==c['raw']['N500'],(key,role))
  for suffix in ['All','Full']:check('conversionCounts',x[suffix.lower()]==x['independent'+suffix],(key,role,suffix))
  check('pocketRecount',x['all'].get('pocketNatural',0)==c['raw']['pocketNatural'],(key,role))
  check('safetyRecount',c['safety']['histogram']==c['safety']['independentHistogram'],(key,role))
  check('safetyN',sum(c['safety']['histogram'].values())==c['safety']['sampleRoundsN'],(key,role))
report=R/'research/observations/general-principles.md';text=report.read_text()
check('reportExists',len(text)>5000 and '[사실]' in text and '[해석]' in text and 'N=' in text)
check('reportNoPlaceholder',not re.search(r'\bTODO\b|TBD|작성 예정',text))
for link in re.findall(r'\]\(([^)]+)\)',text):
 if not link.startswith(('http','#')):check('reportLocalLink',(report.parent/link).exists(),link)
resolvedErrors=[];unresolvedErrors=[]
for name in ['errors.jsonl','enrich-errors.jsonl']:
 if (O/name).exists():
  for line in (O/name).read_text().splitlines():
   r=json.loads(line);key=r.get('key');(resolvedErrors if key in keys else unresolvedErrors).append(r)
check('unresolvedErrors',not unresolvedErrors,unresolvedErrors)
# Retain only compressed geometry cache artifacts after all worker pipelines end.
for p in (O/'geometry').glob('*.json'):
 with gzip.open(str(p)+'.gz','wb',compresslevel=6) as out:out.write(p.read_bytes())
 p.unlink()
partial=O/'progress.jsonl.gz'
if partial.exists():partial.unlink()
resources=guard()
json.dump(resources,open(O/'resource-final.json','w'),indent=1)
result={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':dict(checks),'issues':issues,'resolvedHistoricalErrors':resolvedErrors,'unresolvedErrors':unresolvedErrors,'resource':resources,'sha256':{name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in [('tables.json',O/'tables.json'),('report',report)]}}
json.dump(result,open(O/'qa.json','w'),ensure_ascii=False,indent=1)
print('QA',dict(checks),'issues',len(issues))
if issues:raise SystemExit(1)
