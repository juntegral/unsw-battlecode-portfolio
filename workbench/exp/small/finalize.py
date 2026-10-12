"""Validate all deliverables, fill final table metadata, write 12-line summary last."""
import json,pathlib,re,datetime,shutil,subprocess,collections
O=pathlib.Path(__file__).resolve().parent;ROOT=O.parents[1]
T=json.load(open(O/'tables.json'));V=json.load(open(O/'verification.json'));S=json.load(open(O/'support.json'));DQ=json.load(open(O/'decoder-qa.json'));P=json.load(open(O/'population.json'));R=ROOT/'research/observations/small-maps.md';report=R.read_text();index=(O/'INDEX.md').read_text()
KV=json.load(open(O/'key-verification.json'))
errors=[]
if V['mismatchN']:errors.append('independent group mismatch')
if KV['mismatchN']:errors.append('independent mechanism mismatch')
if any(T['verification']['ledgerCheckSums'].values()) or any(T['verification']['independentMismatchSums'].values()):errors.append('reconstruction check')
if any(x['bad'] for x in DQ['checks']):errors.append('decoder check')
if T['population']['analysedN']!=len(P['tasks']):errors.append('population incomplete')
if T['verification']['primaryTotals']!=T['verification']['independentTotals']:errors.append('total mismatch')
conservation=0;seen=set()
for line in open(O/'rows.jsonl'):
 row=json.loads(line)
 if row.get('schemaVersion')!=2 or row['key'] in seen:continue
 seen.add(row['key'])
 for tm in ['A','B']:
  expected=sum(x['team']==tm for x in row['initial'])+row[tm]['splits']-row[tm]['deaths']
  conservation+=expected!=row[tm]['final']['dragonCount']
if conservation:errors.append('birth/death conservation')
last20=0
for o in T['ourGames']:
 if len(o['last20'])!=20 or [x['r'] for x in o['last20']]!=list(range(o['rounds']-20,o['rounds'])):last20+=1
 if len(o['deaths'])!=sum(o['deathCauses'].values()):errors.append('own death sum '+o['key'])
if last20:errors.append('last20 mismatch')
linkN=0
for file,content in [(R,report),(O/'INDEX.md',index)]:
 for link in re.findall(r'\]\(([^)]+)\)',content):
  if '://' in link or link.startswith('#'):continue
  linkN+=1
  if not (file.parent/link).resolve().exists():errors.append('broken link '+link)
tables=0;badCells=0;expected=None
for line in report.splitlines():
 if line.startswith('|'):
  n=len(line.split('|'))-2
  if expected is None:expected=n;tables+=1
  elif n!=expected:badCells+=1
 else:expected=None
if badCells:errors.append('markdown table cells')
mem=subprocess.check_output(['memory_pressure','-Q'],text=True);freepct=int(mem.split('System-wide memory free percentage:')[1].split('%')[0]);disk=shutil.disk_usage(O).free/2**30;clock=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],text=True).strip()
if freepct<10 or disk<21:raise RuntimeError('RESOURCE PAUSE')
rules=[]
rulehead=False
for line in report.splitlines():
 if line.startswith('|우선|가설·threshold|'):rulehead=True;continue
 if rulehead and line.startswith('|---'):continue
 if rulehead and line.startswith('|'):
  a=line[1:-1].split('|');rules.append({'priority':a[0],'thresholdHypothesis':a[1],'observationalSupportWithN':a[2],'expectedEffectAndFalsifier':a[3],'implementationTrialsN':0})
 elif rulehead:break
if len(rules)!=6:errors.append('rule table incomplete')
qa={'at':clock,'populationN':T['population']['analysedN'],'ourTimelinesN':len(T['ourGames']),'deepReadN':len(json.load(open(O/'deep-selection.json'))),'boardsN':len(json.load(open(O/'boards.json'))),'allContactN':S['totals'],'birthDeathTeamsN':2*len(seen),'conservationMismatchN':conservation,'last20MismatchN':last20,'localLinksN':linkN,'reportTablesN':tables,'markdownCellMismatchN':badCells,'ruleN':len(rules),'memoryFreePercent':freepct,'diskFreeGiB':disk,'errors':errors}
(O/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
if errors:raise RuntimeError(errors)
T['status']='complete: full population, classes, deep reads, independent recount, hypotheses (untested)'
T['verification']['keyMechanismRecount']={'ourGamesN':KV['N'],'groupsN':len(KV['primaryGroups']),'mismatchN':KV['mismatchN'],'file':'exp/small/key-verification.json'}
T['finalizedAt']=clock;T['hypotheses']=rules;T['verification']['independentCohortRecount']={'groupsN':len(V['groups']),'fieldsN':len(V['comparedFields']),'mismatchN':V['mismatchN'],'file':'exp/small/verification.json'};T['definitions']['last20']='both teams state/deaths/splits plus our actions only; enemyActionN counts their actions; all actions in raw';T['definitions']['quantiles']='sorted empirical floor((N-1)*p), median p=.5; maxHeads at round starts';T['qa']=qa
(O/'tables.json').write_text(json.dumps(T,ensure_ascii=False,separators=(',',':'))+'\n')
summary=[
 f'완료 {clock}; 기존 기보 N=2,129, 우리 타임라인 N=194, 판면 그림 N=3.',
 '독립 재집계: 사망 252,971/252,971, 분열 346,965/346,965, 머리 접촉 99,839/99,839; 불일치 0.',
 '번들 소형지도 F 24/24·S 24/24 전멸; Trophy 인식 OFF F 8/8·S 8/8 전멸.',
 '인식 ON Trophy 기보는 4/4 전멸만 직접 재구성; seed 2 네 판은 기보 없음.',
 '번들 사망 N=442: head-on 334, trap 108; 들이받힘 rammed 311.',
 '들이받힌 조각의 직전 판단 N=307 중 빈 출구 ≥2가 226; 구석에 몰림만으로 설명 불가.',
 'default_small trap 94/94에 아군 조각 인접(몸 57/94·머리 68/94, 중복); 적 몸은 3/94.',
 'Trophy top 1,906판 중 정체 15 제외 N=1,891; 양쪽 순위 1–10인 엄격 표본 N=466.',
 '승자 분열 211,628/222,806(95.0%)가 L4→2+2; 일괄적인 분열 지연·길이 하한 인상 근거 부족.',
 'r50–99 교환 사망은 양쪽 22,458개씩; 분열−사망은 승자 +31,036, 패자 +2,578.',
 '가설: area≤625에서 안전한 재생산·다음 id 위협 회피·조건부 L3 보존·지역 trade gate·드롭 회수; 적용 N=0.',
 '미지 지도 기보 N=0; 보고서 research/observations/small-maps.md; 네트워크·업로드·새 경기·커밋 N=0.'
]
assert len(summary)==12
# This is deliberately the final write of the workflow.
(O/'SUMMARY.txt').write_text('\n'.join(summary)+'\n')
print(json.dumps(qa,ensure_ascii=False));print('SUMMARY 12 lines; written last')
