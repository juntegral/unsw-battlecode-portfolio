import sys,json,csv,statistics as st
sys.dont_write_bytecode=True
from collections import Counter
from pathlib import Path
from derived import candidate
O=Path('data/codex/astra/longest')
G=[json.loads(l) for l in (O/'games.jsonl').read_text().splitlines()]
L=[json.loads(l) for l in (O/'local.jsonl').read_text().splitlines()]
M=json.loads((O/'metrics.json').read_text())
rows=[]; transfers=[];groups=[]
for g in G:
 ds={d['id']:d for d in g['deaths']}; delivered=[]
 for e in g['eats']:
  d=ds.get(e['source'])
  if d and e['origin']=='own_drop' and candidate(d) and e['id'] in d['near_longer']:
   delivered.append(e)
   transfers.append(dict(gid=g['gid'],label=g['label'],side=e['side'],death_r=d['round'],source=d['id'],source_length=d['length'],cause=d['cause'],eat_r=e['round'],receiver=e['id']))
 co={c['id'] for c in g['cohort400'] if c['eligible']}
 row=dict(gid=g['gid'],label=g['label'],cohort_stop_recovered_by_top=sum(d['id'] in co and d['cause']=='stop' and any(i==d['top_id'] for r,i in d['eaters']) for d in ds.values()))
 for side in (0,1):
  d=[d for d in ds.values() if d['side']==side and d['round']>=350 and candidate(d)]
  row[str(side)]=dict(stop=len([x for x in d if x['cause']=='stop']),self=len([x for x in d if x['cause']=='own body']),self_recovered=len([x for x in d if x['cause']=='own body' and any(i in x['near_longer'] for r,i in x['eaters'])]),self_rounds=[x['round'] for x in d if x['cause']=='own body'],queen_first_own_drop=min((e['round'] for e in g['eats'] if e['id']==g['queens'][side] and e['origin']=='own_drop'),default=None),queen_first_feed_proxy=min((e['round'] for e in delivered if e['id']==g['queens'][side]),default=None))
 rows.append(row)
for name,pattern in [('WHQ','-w1'),('Cache','-c1'),('dev1 (보조)','-d1'),('ranked (보조)','-ranked')]:
 gs=[g for g in G if g['label'].endswith(pattern)]; ms=[m for m in M if m['label'].endswith(pattern)]; rs=[r for r in rows if r['label'].endswith(pattern)];loss=[m for m in ms if m['result']=='loss'];co=[c for g in gs for c in g['cohort400'] if c['eligible']];surv=[c for g in gs for c in g['cohort400'] if c['death'] is None]
 groups.append(dict(group=name,n=len(gs),wins=len(gs)-len(loss),losses=len(loss),gap=st.median([m['end'][1]['length']-m['end'][0]['length'] for m in loss]),unspent=st.median([m['end'][0]['alive'] for m in loss]),total_larger=sum(m['end'][0]['total']>m['end'][1]['total'] for m in loss),opponent_stop=sum(r['1']['stop'] for r in rs),opponent_self=sum(r['1']['self'] for r in rs),opponent_self_recovered=sum(r['1']['self_recovered'] for r in rs),fold_opponent=[round(st.mean(m['fold'][1][k] for m in ms),2) for k in (0,1)],cohort=len(co),arrived=sum(c['arrived'] is not None or c['distance']<=3 for c in co),before_arrival_death=sum(c['death'] is not None and c['arrived'] is None and c['distance']>3 for c in co),same_id_survivor_n=len(surv),same_id_survivor_far=sum(c['distance']>15 for c in surv),same_id_survivor_median=st.median([c['distance'] for c in surv]) if surv else None))
local=[]
for g in L:
 ds=[d for d in g['deaths'] if d['side']==0 and d['round']>400 and d['cause']=='rammed']
 fed=[d for d in ds if any(e['id']==d['id'] and e['origin']=='own_drop' and e['stop'] and e['round']<=d['round'] for e in g['eats'])]
 local.append(dict(game=g['gid'],arm=g['label'],L400=g['snapshots']['400'][0]['length'],Lend=g['snapshots'][str(g['last'])][0]['length'],alive=g['snapshots'][str(g['last'])][0]['alive'],direct_fed_rams=[{k:d[k] for k in ('id','round','length','top')} for d in fed]))
(O/'supplement.json').write_text(json.dumps(dict(groups=groups,games=rows,local=local),ensure_ascii=False,indent=2))
with (O/'transfers.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(transfers[0]),delimiter='\t');w.writeheader();w.writerows(transfers)
with (O/'cohort400.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['gid','id','length','leader400','distance400','eligible','arrival_round_leader','stop','death'])
 for g in G:
  for c in g['cohort400']:w.writerow([g['gid'],*[c[k] for k in ('id','length','leader','distance','eligible','arrived','stop','death')]])
def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+''.join('| '+' | '.join(str(c) for c in r)+' |\n' for r in rows)
t='[M] 추가 회수 검사: 자기 몸 충돌과 정지 모두 출구>0, 더 긴 아군 머리 거리≤3, timeout 아님. 회수는 당시 곁에 있던 그 긴 아군이 실제 드롭을 먹은 사건. [E] 고의 희생 여부는 미확정.\n\n'
t+=table(['판','상대 자기몸 충돌 후보','그 긴 아군 회수 후보','후보 라운드','여왕 첫 아군 드롭 우리/상대','여왕 첫 희생후보 회수 우리/상대'],[[r['gid'],r['1']['self'],r['1']['self_recovered'],r['1']['self_rounds'],[r[str(s)]['queen_first_own_drop'] for s in (0,1)],[r[str(s)]['queen_first_feed_proxy'] for s in (0,1)]] for r in rows])
t+='\n[M] r400 먹이 길이 후보 중 정지 사망 드롭을 사망 당시 전역 최장이 실제 회수한 개체 수. 역할 기억이나 의도를 복원한 값은 아니다.\n\n'
t+=table(['판','실제 최장 회수 후보'],[[r['gid'],r['cohort_stop_recovered_by_top']] for r in rows])
t+='\n[M] r400 이후 직접 정지 드롭을 먹었던 개체의 램: 분열 자손 추정 제외, 모든 길이.\n\n'
t+=table(['판','arm','r400→끝 최장','끝 생존','직접 먹은 용 램 id/r/L/top'],[[r['game'],r['arm'],f"{r['L400']}→{r['Lend']}",r['alive'],r['direct_fed_rams']] for r in local])
(O/'supplement.md').write_text(t)
print(json.dumps(groups,ensure_ascii=False,indent=2));print('local direct fed ram games',Counter(r['arm'] for r in local if r['direct_fed_rams']))
