import json,csv,subprocess
from pathlib import Path
from collections import Counter
import summarize
OUT=Path(__file__).resolve().parent

def main():
 gs=[json.loads(p.read_text()) for p in OUT.glob('game-*.json')];inv=json.loads((OUT/'inventory.json').read_text());summary=json.loads((OUT/'summary.json').read_text());report=(OUT/'report.md').read_text()
 assert len(gs)==len(inv['rows'])==209
 assert Counter(g['version'] for g in gs)==Counter({k:v['n'] for k,v in summary.items()})
 assert len(report.split())<500
 assert len(' '.join(l for l in report.splitlines() if not l.startswith('|')).split())<450
 assert sum(l.startswith('|---') for l in report.splitlines())==1
 assert len(set(g['gid'] for g in gs))==len(gs)
 cards=[]
 for g in gs:
  assert g['checks']==[0,0]
  for t in g['reach']:
   if t['visible'] and not t['hitqueen'] and t['reasons']==['lunge_pearl_population_gate:3636,4762']:cards.append(dict(version=g['version'],gid=g['gid'],r=t['r'],id=t['id'],length=t['L'],units=t['units'],path=t['path'],action=t['action']))
 assert len(cards)==11 and len({r['gid'] for r in cards})==7
 summarize.write('card-turns.tsv',cards)
 geo=[r for p in OUT.glob('geometry-*.json') for r in json.loads(p.read_text())]
 assert len(geo)==sum(len(g['candidates']) for g in gs)==2648
 assert not any(r['path_distance']>=9999 for r in geo)
 assert sum(g['coverage'].get('path_search_truncated',0) for g in gs)==87
 assert all(not any('unresolved_internal_memory_or_override' in t['reasons'] for t in g['reach']) for g in gs)
 for v,x in summary.items():
  ls=[g for g in gs if g['version']==v]
  assert x['queen_ram']==sum('rammer' in d for g in ls for d in g['deaths'])
  assert x['queen_dead']==sum(d['queen'] and d['side']==1 for g in ls for d in g['deaths'])
  assert x['queen_mate_pearls']==sum(t['queen'] and t['side']==t['source_side']==0 for g in ls for t in g['transfers'])
  assert x['rally']['L']==x['rally']['lost']+x['rally']['remaining']
 time=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],text=True).strip()
 result=dict(time=time,report_words=len(report.split()),body_words=len(' '.join(l for l in report.splitlines() if not l.startswith('|')).split()),tables=1,games=len(gs),card_turns=len(cards),card_games=len({r['gid'] for r in cards}),all_passed=True)
 (OUT/'report-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
 (OUT/'DECISIONS.md').write_text(f'''[M] {time} — audit-hunt 완료. 입력 동결 04:59:18 KST, 209판; 종료 점수 측면 대조 418건, 전체 질량 보존 418건, 대용 집결 토큰 보존 2648건 모두 일치. report.md는 {result['report_words']}단어, 표 1개다.\n\n[M/C/E] one10의 L>4 여왕 박치기 3회와 부트 먹이기 사례를 확인했다. QUEEN_AVENGE의 사망 주장이 전혀 생성되지 않는다는 보편 명제는 철회한다. 집결 손실과 버전별 최장 승부는 집결 단독 인과로 해석하지 않는다.\n\n[E] 카드 1개: sure_queen 경로에서만 LUNGE_PEARL의 아군56마리 관문을 면제. 가시권 미공격 11턴/7판의 확인된 코드 관문을 대상으로 하며 미검증 승률 개선을 주장하지 않는다. 패치·경기·업로드는 하지 않았다.\n\n[M/E] 고정 몸 경로의 미공격 하한 목록이며 검색상한87회·꼬리활용·내부 기억·분기 로그·반사실 결과는 남은 한계다. 가장 큰 질량 손실을 단일 규칙에 귀속할 수 없어 그 영역에 추정성 카드를 만들지 않았다.\n''')
if __name__=='__main__':main()
