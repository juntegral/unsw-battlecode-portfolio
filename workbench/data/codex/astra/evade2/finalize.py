import json,hashlib,subprocess
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent
s=json.loads((OUT/'summary.json').read_text());rows=json.loads((OUT/'ram-audit.json').read_text());cs=json.loads((OUT/'cohorts.json').read_text())
assert all(z['games']==15 for z in s['labels'].values())
assert sum(z['rams'] for l,z in s['labels'].items() if l.startswith('one7'))==1319
assert all(sum(z['classes'].values())==z['rams'] for z in s['labels'].values())
assert all(sum(z['free_window']['outcomes'].values())==z['free_window']['n'] for z in s['labels'].values())
assert sum(r.get('turn_change_compatible',False) for r in rows if r['label'].startswith('one7'))==49
assert sum(r.get('added_plus',False) for r in rows if r['label'].startswith('one7'))==134
estimate={}
for early in (False,True):
 total=0
 for opponent in ('w1','c1'):
  b=[t for t in cs if t['label']=='one5-'+opponent and t['free_window'] and (not early or t['round']<=200)]
  n=[t for t in cs if t['label']=='one7-'+opponent and t['free_window'] and (not early or t['round']<=200)]
  total+=len(n)*sum(t['chosen_danger'] for t in b)/len(b)-sum(t['chosen_danger'] for t in n)
 denom=sum(z['turns200' if early else 'turns'] for l,z in s['labels'].items() if l.startswith('one7'))
 estimate['r0-200' if early else 'full']=dict(estimated_changed_turns=total,our_turns=denom,percent=100*total/denom)
wordcount=len(' '.join(l for l in (OUT/'report.md').read_text().splitlines() if not l.startswith('|')).split());assert wordcount<450
stamp=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],text=True).strip()
result=dict(completed=stamp,non_table_words=wordcount,estimate=estimate,one7_compatible_survived_own_move=sum(t['change_compatible'] for t in cs if t['label'].startswith('one7')),files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'report.md',OUT/'methods.md',OUT/'ram-audit.csv',OUT/'cohorts.csv')})
(OUT/'completion.json').write_text(json.dumps(result,indent=2))
(OUT/'DECISIONS.md').write_text(f'''# evade2 분석 판정\n\n- 실제 시계: {stamp} (`date` 확인).\n- [M/E] 원래 one5 회피가능329건 중 현행 검문 기하36건; one7의 같은 초기 표본은0건. 코드가 상정한 무료 위험 선택을 줄인 흔적은 있으나, 변경량 대리추정은 전체 턴의 약0.10%다.\n- [E/C] 판정: SHORT_EVADE 유지하며 보이는 적의 검사 도달을 지불 가능한 한 걸음만 확장하는 카드1장. 실제 구현·업로드는 하지 않았다.\n- [M/E] one7 비여왕 피격1,319건 전수 분류. 추가 도달 후보134건(초기54)은 살아날 수 확정치가 아니다. 로그·점수 부재로 실제 발동 수를 확정하지 않았다.\n- [M] 보고서: report.md, 세부 한계·재현: methods.md. 독립60판 사건/진주 보존 대조 및863개 안전 경로 확인.\n- [M] 이 분석 폴더만 작성했다. 네트워크·대전·봇 실행/변경·공용 문서 수정·커밋 없음.\n''')
print(json.dumps(result,indent=2))
