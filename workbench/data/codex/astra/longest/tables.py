import json,csv,statistics as st
from pathlib import Path
from lineage import major_lineage
from derived import annotate
from collections import Counter,defaultdict
O=Path('data/codex/astra/longest')
G=[json.loads(x) for x in (O/'games.jsonl').read_text().splitlines()]
L=[json.loads(x) for x in (O/'local.jsonl').read_text().splitlines()]
C=json.loads((O/'census.json').read_text())
for g in G+L:annotate(g)
def med(a):return round(st.median(a),2) if a else None
def avg(a):return round(st.mean(a),2) if a else None
def snap(g,r):return g['snapshots'].get(str(r),g['snapshots'][str(g['last'])])
def stops(g,s,lo=350):return [d for d in g['deaths'] if d['side']==s and d['round']>=lo and d['cause']=='stop' and d['free']>0 and d['near_longer'] and not (d.get('action') or {}).get('timeout')]
def fedrams(g,s,lo):
 out=[]
 for d in g['deaths']:
  if d['side']!=s or d['cause']!='rammed' or d['round']<=lo:continue
  prior=[e for e in g['eats'] if e['id']==d['id'] and e['origin']=='own_drop' and e['stop'] and e['round']<=d['round']]
  anc=major_lineage(g.get('all_dragons',{}).get(str(d['id']),{}).get('lineage',[]))
  ancestral=[e for e in g['eats'] if e['origin']=='own_drop' and e['stop'] and any(e['id']==a['id'] and e['round']<=a['round'] for a in anc)]
  if prior or ancestral:out.append(dict(id=d['id'],r=d['round'],L=d['length'],fed=len(prior),ancestral_events=len(ancestral),last_feed=max(e['round'] for e in prior+ancestral),top=d['top']))
 return out

def measure(g):
 end=snap(g,g['last']);c=[x for x in g['cohort400'] if x['eligible']]
 return dict(gid=g['gid'],label=g['label'],map=g['map'],opp=g['opp'],result=g['result'],last=g['last'],end=end,phase=g['phase_nonqueen'],first_stop=[min((d['round'] for d in stops(g,s,151)),default=None) for s in (0,1)],stops=[len(stops(g,s)) for s in (0,1)],stop_rounds=[[d['round'] for d in stops(g,s)] for s in (0,1)],fold=[[snap(g,350)[s]['alive'],end[s]['alive']] for s in (0,1)],queen_first=[min((e['round'] for e in g['eats'] if e['id']==g['queens'][s] and e['origin']=='own_drop' and e['stop']),default=None) for s in (0,1)],distance400=med([x['distance'] for x in g['cohort400']]),distance_end_survivors400=med([x['distance'] for x in g['cohort400'] if x['death'] is None]),cohort=len(c),cohort_arrived=sum(x['arrived'] is not None or x['distance']<=3 for x in c),cohort_death_before_arrival=sum(x['death'] is not None and x['arrived'] is None and x['distance']>3 for x in c),cohort_stop=sum(x['stop'] is not None for x in c),cohort_survived=sum(x['death'] is None for x in c),fed_rams=[fedrams(g,s,350) for s in (0,1)])
M=[measure(g) for g in G]
(O/'metrics.json').write_text(json.dumps(M,ensure_ascii=False,indent=2))
summary=[]
for label in sorted(set(c['label'] for c in C)):
 rows=[m for m in M if m['label']==label];loss=[m for m in rows if m['result']=='loss'];allc=[c for c in C if c['label']==label]
 summary.append(dict(label=label,available=len(allc),longest=len(rows),wins=sum(m['result']=='win' for m in rows),losses=len(loss),gap_med=med([m['end'][1]['length']-m['end'][0]['length'] for m in loss]),unspent_med=med([m['end'][0]['alive'] for m in loss]),larger_total=sum(m['end'][0]['total']>m['end'][1]['total'] for m in loss)))
local=[]
for arm in ('mArl_vh','mAl4_vh'):
 gs=[g for g in L if g['label']==arm]
 local.append(dict(arm=arm,n=len(gs),alive_end=avg([snap(g,g['last'])[0]['alive'] for g in gs]),L400=avg([snap(g,400)[0]['length'] for g in gs]),Lend=avg([snap(g,g['last'])[0]['length'] for g in gs]),fed_body_rammed_games=sum(bool(fedrams(g,0,400)) for g in gs),longest20_rammed_games=sum(any(d['round']>400 and d['side']==0 and d['top'] and d['length']>=20 and d['cause']=='rammed' for d in g['deaths']) for g in gs),fed_rams=[dict(game=g['gid'],rams=fedrams(g,0,400)) for g in gs if fedrams(g,0,400)]))
loss=[m for m in M if m['result']=='loss']
agg=dict(online_games=len(C),longest_games=len(G),losses=len(loss),wins=len(G)-len(loss),loss_gap=med([m['end'][1]['length']-m['end'][0]['length'] for m in loss]),loss_unspent=med([m['end'][0]['alive'] for m in loss]),loss_larger_total=sum(m['end'][0]['total']>m['end'][1]['total'] for m in loss),fed_ram_games=sum(bool(m['fed_rams'][0]) for m in M),cohort=sum(m['cohort'] for m in M),arrived=sum(m['cohort_arrived'] for m in M),death_before_arrival=sum(m['cohort_death_before_arrival'] for m in M),cohort_survived=sum(m['cohort_survived'] for m in M),logs=sum(len(g['logs']) for g in G))
(O/'summary.json').write_text(json.dumps(dict(aggregate=agg,online=summary,local=local),ensure_ascii=False,indent=2))
with (O/'checkpoints.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['gid','label','round','side','id','length','role','natural','own_drop','foe_drop','stop_drop','feed_proxy_pearls','alive','total','death'])
 for g in G:
  for r,ss in g['snapshots'].items():
   for s,x in enumerate(ss):w.writerow([g['gid'],g['label'],r,s,*[x[k] for k in ('id','length','role','natural','own_drop','foe_drop','stop_drop','feed_proxy_pearls','alive','total')],g['leaders'][str(x['id'])]['death'] if x['id'] is not None else None])
with (O/'leaders.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['gid','label','side','id','born','start','parent','natural','own_drop','foe_drop','stop_drop','feed_sources','splits','death','lineage'])
 for g in G:
  for x in g['leaders'].values():w.writerow([g['gid'],g['label'],*[x[k] for k in ('side','id','born','start','parent','natural','own_drop','foe_drop','stop_drop','feed_sources','splits','death','lineage')]])
def table(head,rows):return '| '+' | '.join(head)+' |\n| '+' | '.join(['---']*len(head))+' |\n'+''.join('| '+' | '.join(str(v) for v in row)+' |\n' for row in rows)
text='[M] 온라인 최장 승부 전수표. 모든 수치는 기보를 다시 읽었다. 0=우리, 1=상대. 라운드는 기보의 0부터 시작하는 roundStart 값, end는 마지막 실제 라운드다.\n\n'
text+='[M] 분류 Q=여왕, F=출구가 있는 더 짧은 아군의 정지/자기몸 충돌 때 거리≤3이었고 그 드롭을 직접 회수한 비여왕, O=그 외(먹임이 없었다는 뜻은 아님). [E] F*=분열 때마다 절반 이상 몸을 물려받은 주 계보의 조상에게 F의 회수 이력이 있는 개체(물려받은 드롭 질량 자체는 미확정). F는 전략적 리더 선출이나 고의 희생을 확정하지 않는다. fed/ordinary는 이 관측 분류다. 동률 최장은 최소 id를 대표로 골랐다. 자연/아군/적 드롭은 출생 후 누적 섭취이며 현재 길이와 다르다(분열·유료 이동). 새끼의 출생 길이는 상속분이다.\n\n'
text+='[M] 정지 희생 후보 = 움직일 빈 출구가 있고, 더 긴 아군 머리가 토러스 맨해튼 거리 3 이내인 stop 사망(타임아웃 제외). [E] 고의 먹이기의 관측 대리값이며 상대 의도는 확정하지 않는다. [M] 거리에는 벽·포털·몸을 반영하지 않는다.\n\n'
text+=table(['세트','완료','최장 판','승','패','패배 격차 중앙값','패배 잔존 중앙값','총길이 우세 패배'],[[s[k] for k in ('label','available','longest','wins','losses','gap_med','unspent_med','larger_total')] for s in summary])
text+='\n[M] 전 판의 최장 변화(id:길이:분류). 세부 섭취와 사망은 checkpoints.tsv 및 leaders.tsv에 있다.\n\n'
rounds=list(range(200,500,25))
rows=[]
for g in G:
 for s in (0,1):
  cells=[]
  for r in rounds:
   x=g['snapshots'].get(str(r),[None,None])[s];cells.append(f"{x['id']}:{x['length']}:{dict(queen='Q',fed='F',ordinary='O',**{'inherited-fed':'F*'})[x['role']]}" if x else '—')
  x=snap(g,g['last'])[s];cells.append(f"{x['id']}:{x['length']}:{dict(queen='Q',fed='F',ordinary='O',**{'inherited-fed':'F*'})[x['role']]}")
  rows.append([g['gid'],g['label'],g['result'],'우리' if s==0 else '상대',*cells,x['total']])
text+=table(['판','세트','결과','편',*[str(r) for r in rounds],'end','최종 총길이'],rows)
text+='\n[M] 표에 나타난 개체별 평생 섭취·인접 희생·사망. 인접 희생은 그 개체가 더 길고 거리≤3일 때의 stop 사망 후보다. 회수와 별개이며 중복 귀속 가능하다.\n\n'
text+=table(['판','편:id','출생 길이','자연/아군/적 드롭','아군 정지 드롭','곁 정지 희생 r:id','사망','상속 계보'],[[g['gid'],f"{x['side']}:{x['id']}",x['start'],f"{x['natural']}/{x['own_drop']}/{x['foe_drop']}",x['stop_drop'],','.join(f"{d['round']}:{d['id']}" for d in g['deaths'] if d['cause']=='stop' and d['free']>0 and x['id'] in d['near_longer']) or '없음',x['death'] or '생존',x.get('lineage',[])] for g in G for x in g['leaders'].values()])
text+='\n[M] 마지막 150라운드(r350부터)의 정지 후보 수·라운드, r350→end 머릿수, 여왕 첫 아군 정지 드롭 섭취(전 경기), 우리 r400 후보 추적. [C/E] phase는 실제 개체의 queen_game/선출 기억을 복원한 값이 아니라 기본 r400 및 수≥56 cap 규칙으로 재구성한 최초 전역 조건이다.\n\n'
text+=table(['판','phase/첫 우리 정지','우리/상대 정지','우리/상대 접기','여왕 첫 먹임 우리/상대','r400 거리 중앙값 전체/끝 생존','후보/도착/도착 전 사망/끝 생존'],[[m['gid'],f"{m['phase']}/{m['first_stop'][0]}",m['stops'],m['fold'],m['queen_first'],f"{m['distance400']}/{m['distance_end_survivors400']}",f"{m['cohort']}/{m['cohort_arrived']}/{m['cohort_death_before_arrival']}/{m['cohort_survived']}"] for m in M])
text+='\n[M] 후보는 r400에서 비여왕·최장 이외·길이≤당시 최장/2인 개체다. 도착은 r400 이미 거리≤3 또는 이후 살아 있는 당시 전역 최장(목표 변경 허용)에 조건을 유지하며 거리≤3이 된 경우다. [E] 실제 먹이기 역할·경로를 뜻하지 않으며 도착 전 사망은 이동 실패의 상한 대리값이다.\n\n'
text+=table(['판','우리 정지 후보 라운드','상대 정지 후보 라운드'],[[m['gid'],','.join(map(str,m['stop_rounds'][0])) or '없음',','.join(map(str,m['stop_rounds'][1])) or '없음'] for m in M])
text+='\n[M] 로컬: 동일 지도·시드·편의 완료 판. fed-ram은 아군 정지 드롭을 이미 먹은 몸 또는 그 자손의 수동 정면충돌이며(자손에게 전달된 진주량은 미확정), 최장 여부나 L20 문턱과 별개다.\n\n'
text+=table(['arm','n','끝 잔존 평균','r400 최장 평균','끝 최장 평균','r400 뒤 먹인 몸 램 판','r400 뒤 L20+ 최장 램 판'],[[a[k] for k in ('arm','n','alive_end','L400','Lend','fed_body_rammed_games','longest20_rammed_games')] for a in local])
text+=table(['판','arm','r400→끝 잔존','r400→끝 최장','먹인 몸 램 r/id/L/회수량','끝 총길이 우리/상대'],[[g['gid'],g['label'],f"{snap(g,400)[0]['alive']}→{snap(g,g['last'])[0]['alive']}",f"{snap(g,400)[0]['length']}→{snap(g,g['last'])[0]['length']}",fedrams(g,0,400),f"{snap(g,g['last'])[0]['total']}/{snap(g,g['last'])[1]['total']}"] for g in L])
(O/'tables.md').write_text(text)
print(json.dumps(dict(aggregate=agg,online=summary,local=local),ensure_ascii=False,indent=2))
