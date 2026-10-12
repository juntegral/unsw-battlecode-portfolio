import sys
sys.dont_write_bytecode=True
import json,csv
from pathlib import Path
from collections import Counter
from datetime import datetime
OUT=Path(__file__).resolve().parent
G=[json.loads(p.read_text()) for p in sorted(OUT.glob('g[0-9]*.json'))]
old=json.loads((OUT.parent/'smallmap/games.json').read_text())
lossids={g['gid'] for g in old if g['result']=='loss'}
groups={
 '원래 패배 54판':[g for g in G if g['gid'] in lossids],
 '원래 전체 73판':[g for g in G if g['original']],
 'WHQ one3–5':[g for g in G if g['label'].endswith('-w1')],
 'Cache one5-c1':[g for g in G if g['label']=='one5-c1'],
 'dev one3–5 (보조)':[g for g in G if g['label'].endswith('-d1')],
 '랭크 기타':[g for g in G if g['label']=='ranked'],
 'WHQ one5':[g for g in G if g['label']=='one5-w1'],
 'dev one5 (보조)':[g for g in G if g['label']=='one5-d1'],
}
def pct(n,d): return f'{100*n/d:.2f}%' if d else '—'
def closure(d):
 if d['at_split']['exits']==0: return '분열 시 이미 막힘'
 if d['at_death']['exits']>0: return '사망 시 빈 출구 있음'
 if not d['same_head']: return '움직인 뒤 다른 자리에서 막힘'
 return '나중 봉쇄:'+ '+'.join(sorted(set(d['original_exit_occupants_at_death'])))
def kind(d):
 if d['split_queen']: return '여왕 대기/안전/기타 분열 (분기 미확인)'
 child=d['sibling'] if d['role']=='parent' else d['at_split']
 if d['before']['exits']==0: return '비여왕 머리 봉쇄 탈출'
 if child['length']!=2: return '비여왕 큰 자식 탈출'
 if d['before']['length']>4: return '비여왕 일반 성장 (자식 크기로 식별)'
 return '비여왕 일반 성장/주머니 탈출 구별 불가'
def eligible(s):
 return not s['queen'] and s['before']['exits']>0
def clear_seen(s):
 return any(e['kind']=='free' and e['visible'] for e in s['children']['child']['edges'])

summary={}; rates=[]; details=[]; pearls=[]; splitrows=[]
for name,gs in groups.items():
 a=dict(games=len(gs),sides={})
 for side in ('us','them'):
  ds=[d for g in gs for d in g['deaths'] if d['side']==side]
  sp=[s for g in gs for s in g['splits'] if s['side']==side]
  turns=sum(g['turns'][side] for g in gs)
  post=[d for d in ds if 'split_event' in d]
  boxed=[d for d in post if d['postsplit_boxed_proxy']]
  counts=Counter(d['category'] for d in ds)
  x=dict(turns=turns,splits=len(sp),deaths=len(ds),causes=dict(counts),post=len(post),boxed=len(boxed),
         affected_splits=len({(d['gid'],d['split_event']) for d in post}),
         boundary_splits=sum(s['round']==150 or s['round']==g['last_round'] for g in gs for s in g['splits'] if s['side']==side))
  a['sides'][side]=x
  for cause,n in counts.items(): rates.append(dict(group=name,side=side,cause=cause,count=n,turns=turns,per100=100*n/turns))
 for label,ds in [('all_post',[d for g in gs for d in g['deaths'] if d['side']=='us' and 'split_event' in d]),
                  ('boxed',[d for g in gs for d in g['deaths'] if d['side']=='us' and d['postsplit_boxed_proxy']])]:
  ids={d['death'] for d in ds}; ps=[p for g in gs for p in g['pearls'] if p['death'] in ids]
  childids={d['death']:d['split_child'] for d in ds}
  a[label]=dict(n=len(ds),roles=dict(Counter(d['role'] for d in ds)),lengths=dict(Counter(d['length'] for d in ds)),
      closure=dict(Counter(closure(d) for d in ds)),kind=dict(Counter(kind(d) for d in ds)),
      already_closed_visible=sum(d['at_split']['exits']==0 and all(e['visible'] for e in d['at_split']['edges']) for d in ds),
      body=sum(d['length'] for d in ds),drops=len(ps),recovered5=dict(Counter(p['eater'] if p['eater'] in ('us','them') and p['wait'] is not None and p['wait']<=5 else 'pending' for p in ps)),
      recovered_end=dict(Counter(p['eater'] for p in ps)),child_eaten=sum(p['eater_id']==childids[p['death']] for p in ps),
      own5_child=sum(p['eater_id']==childids[p['death']] and p['wait']<=5 for p in ps),
      queen_eaten=sum(p['eater']=='us' and p['eater_id'] in (0,1) for p in ps),
      censored5=sum(d['round']+5>g['last_round'] for g in gs for d in g['deaths'] if d['death'] in ids))
 sp=[s for g in gs for s in g['splits'] if s['side']=='us' and eligible(s)]
 filters={
  '눈앞에서 자식 봉쇄 확정': [s for s in sp if s['children']['child']['exits']==0 and all(e['visible'] for e in s['children']['child']['edges'])],
  '자식 출구 0 (전지적)': [s for s in sp if s['children']['child']['exits']==0],
  '관측된 빈 자식 출구 없으면 보류':[s for s in sp if not clear_seen(s)],
 }
 a['filters']={}
 for title,ss in filters.items():
  keys={(s['gid'],s['event']) for s in ss}
  ds=[d for g in gs for d in g['deaths'] if d['side']=='us' and (d['gid'],d.get('split_event')) in keys]
  a['filters'][title]=dict(delayed_splits=len(ss),near_deaths=len(ds),boxed_deaths=sum(d['postsplit_boxed_proxy'] for d in ds),
          child_deaths=sum(d['role']=='child' for d in ds),split_without_child_death=len(keys-{(d['gid'],d['split_event']) for d in ds if d['role']=='child'}))
 summary[name]=a

for g in G:
 for d in g['deaths']:
  if d['side']!='us' or 'split_event' not in d: continue
  row={k:d[k] for k in ('gid','round','id','length','category','split_round','split_parent','split_child','role','split_queen','postsplit_boxed_proxy')}
  row.update(label=g['label'],closure=closure(d),kind=kind(d),split_length=d['before']['length'],parent_exits=d['before']['exits'],
      birth_exits=d['at_split']['exits'],death_exits=d['at_death']['exits'],all_blockers_visible=all(e['visible'] for e in d['at_split']['edges']))
  details.append(row)
  pearls.extend(p for p in g['pearls'] if p['death']==d['death'])
 for s in g['splits']:
  splitrows.append(dict(gid=g['gid'],label=g['label'],side=s['side'],round=s['round'],parent=s['parent'],child=s['child'],queen=s['queen'],
       length=s['before']['length'],parent_exits=s['before']['exits'],child_length=s['children']['child']['length'],child_exits=s['children']['child']['exits'],
       clear_seen=clear_seen(s)))
for fn,rows in [('rates.csv',rates),('deaths.csv',details),('drops.csv',pearls),('splits.csv',splitrows)]:
 with (OUT/fn).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for row in rows for k in row)));w.writeheader();w.writerows(rows)
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
for a in summary.values():
 for k in ('all_post','boxed'):
  assert sum(a[k]['recovered5'].values())==sum(a[k]['recovered_end'].values())==a[k]['drops']
  assert sum(a[k]['roles'].values())==sum(a[k]['closure'].values())==sum(a[k]['kind'].values())==a[k]['n']

lines=['[M] 생성 '+datetime.now().astimezone().isoformat(),'',
 '[M] r0–150 포함. 각 칸은 우리 / 상대. 사망률 분모는 실제 dragon turn; 분열당 사망은 부모·자식 사망 사건 수라 분열 실패 확률과 다르다.',
 '', '| 집단 | 판 | 용 턴 | 분열 | 사망/100턴 | 분열 직후 사망/100분열 | 봉쇄·비머리사망/100분열 | 사망 동반 분열/100분열 |',
 '|---|---:|---|---|---|---|---|---|']
for name,a in summary.items():
 u,t=a['sides']['us'],a['sides']['them']
 def pair(key):return f"{u[key]} / {t[key]}"
 def rat(key,den):return f"{100*u[key]/u[den]:.2f} / {100*t[key]/t[den]:.2f}"
 lines.append(f"| {name} | {a['games']} | {pair('turns')} | {pair('splits')} | {rat('deaths','turns')} | {rat('post','splits')} | {rat('boxed','splits')} | {rat('affected_splits','splits')} |")
lines+=['','[M] 사인별 건수(100턴당). 같은 원자료·같은 경기 양편 비교.','',
 '| 집단 | 편 | 벽 | 피격 | 선제 충돌 | 자기 몸 | 아군 몸 | 적 몸 | 아군 머리 | 무행동 | 불법 분열 |','|---|---|---|---|---|---|---|---|---|---|---|']
for name,a in summary.items():
 for side,x in a['sides'].items():
  cs=[]
  for c in ('wall','rammed','rams','self','mate_body','enemy_body','mate_head','no action','illegal split'):
   n=x['causes'].get(c,0);cs.append(f"{n} ({100*n/x['turns']:.3f})")
  lines.append('| '+name+' | '+side+' | '+' | '.join(cs)+' |')
for name in ('원래 패배 54판','원래 전체 73판','Cache one5-c1'):
 a=summary[name];lines+=['',f'[M] {name}: 우리 분열 직후 사망의 구성.','', '| 항목 | 모든 사인 | 봉쇄·비머리사망 |','|---|---|---|']
 for field in ('roles','lengths','closure','kind'):
  vals=set(a['all_post'][field])|set(a['boxed'][field])
  for v in sorted(vals,key=str):
   cs=[f"{a[k][field].get(v,0)} ({pct(a[k][field].get(v,0),a[k]['n'])})" for k in ('all_post','boxed')]
   lines.append(f'| {field}: {v} | '+ ' | '.join(cs)+' |')
lines+=['','[M] 사망 몸의 고유 진주 회수. 종료까지는 각 경기 끝까지. 5라운드 미완료 수는 summary.json.','',
 '| 집단/범위 | 사망 길이 | 낙하 진주 | 5라운드 우리/적/미회수 | 종료까지 우리/적/미회수 | 자식 직접 회수(종료까지) |','|---|---:|---:|---|---|---:|']
for name in ('원래 패배 54판','원래 전체 73판','Cache one5-c1'):
 for label in ('all_post','boxed'):
  x=summary[name][label];r=x['recovered5'];e=x['recovered_end']
  lines.append(f"| {name}/{label} | {x['body']} | {x['drops']} | {r.get('us',0)}/{r.get('them',0)}/{r.get('pending',0)} | {e.get('us',0)}/{e.get('them',0)}/{e.get('nobody',0)} | {x['child_eaten']} |")
lines+=['','[M] 가상 보류 필터의 범위. 모두 비여왕·부모 빈 출구≥1에 한정. 대체 행동/실제 지연 턴/생존 개선을 계산한 표가 아니다.','',
 '| 집단 | 필터 | 보류 분열 | 연결된 사망 | 자식 사망 | 자식이 즉사하지 않은 분열 |','|---|---|---:|---:|---:|---:|']
for name in ('원래 패배 54판','원래 전체 73판','Cache one5-c1'):
 for title,x in summary[name]['filters'].items():
  lines.append(f"| {name} | {title} | {x['delayed_splits']} | {x['near_deaths']} | {x['child_deaths']} | {x['split_without_child_death']} |")
(OUT/'tables.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
