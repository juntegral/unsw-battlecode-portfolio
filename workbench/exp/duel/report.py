from verify import guard
"""Korean descriptive report; final SUMMARY is emitted only after verified full population."""
import json,pathlib,datetime,collections,statistics,gzip
O=pathlib.Path(__file__).resolve().parent
REPORT=O.parent.parent/'research/observations/duels.md'
def pct(n,d):return f'{100*n/d:.1f}%' if d else '—'
def avg(n,d):return f'{n/d:.2f}' if d else '—'
def table(header,rows):return ['|'+'|'.join(header)+'|','|'+'|'.join(['---']*len(header))+'|']+['|'+'|'.join(str(x) for x in row)+'|' for row in rows]
def main():
 guard()
 CC=json.loads((O/'custom-comparison.json').read_text());VC=json.loads((O/'verification-custom.json').read_text())
 if VC['mismatches']:raise RuntimeError('custom contact recount discrepancy')
 CAL=json.loads((O/'calibration.json').read_text());T=json.loads((O/'tables.json').read_text());V=json.loads((O/'verification.json').read_text());R=json.loads((O/'verification-raw.json').read_text());S=json.loads((O/'selection.json').read_text());C=json.loads((O/'classes.json').read_text())
 if T['verification'].get('nonzeroCheckGames') or any(v!=0 for v in T['verification']['checkSums'].values()):raise RuntimeError('reconstruction/indicator discrepancy needs resolution')
 if T['stage']!='full' or T['population']['unprocessedN'] or T['population']['errors'] or V['mismatches'] or R['missing'] or R['mismatchGames']:raise RuntimeError('full population and independent verification are required')
 early=json.loads(gzip.open(O/'tables-strict-first.json.gz','rt').read())
 G=T['groups'];P=T['population'];Z=lambda k:G.get(k,{'N_games':0,'N_episodes':0,'outcomes':{},'allContacts':{'N':0,'mover':0,'passive':0},'patterns':{},'features':{}})
 labels=['strict/winner','strict/loser','elite/winner','elite/loser','population/winner','population/loser','ours','ours/custom','under/known','under/known_autoscrim','under/custom','sprint_custom/winner','sprint_custom/loser']
 now=datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
 lines=['# 온라인 국소 결투: 상위권의 행동과 우리 실패', '',f'작성 {now}. W10. 네트워크·대전·업로드·커밋 없이 기존 온라인 기보 전수를 읽었다.','',
 '[사실] 원문 규칙은 [ALL.md](../../rules/ALL.md)·[death.md](../../rules/death.md), 항의 크기는 [terms.md](../../docs/arch/terms.md), kill path/TRADE는 [bot/plan.cpp](../../bot/plan.cpp)를 확인했다.', '',
 '[사실] 이 보고서는 온라인에서 관측한 행동의 기술 통계다. 로컬 흉내 상대의 승패를 채택 근거로 사용하지 않았다. 실제 변경은 구현하지 않았고 마지막 규칙의 적용 N은 모두 0이다.','',
 '## 먼저 읽을 관측','',
 '[사실] 상위 10팀 승자 정면접촉의 능동 이동은 309,628/534,426=57.9%, 우리 전체는 2,368/13,483=17.6%다. 그러나 우리 본선 7판은 93/108=86.1%로 방향이 뒤집힌다. 본선 사망594 중 켈프252·자기 몸79·아군 몸136이므로 이 집단을 따로 읽어야 한다.','',
 '[해석] 자료가 지지하는 다음 가설은 일괄 공격성 증가보다 다음 차례 도달 위험, 살아남는 몸 장벽, 분열 뒤 부모·새끼의 출구 보존이다. 감기·미끼는 아래 조작적 대리 지표이며 의도는 미확인이다. 마지막 규칙표의 수치는 구현할 시험 강도이고 예상 승률이 아니다.','',
 '## 1. 모집단과 세 단계 방법','',
 f"[사실] 첫 목록 시각 {early['population']['frozenAt']}, 최종 목록 고정 {P['frozenAt']}, 마지막 집계 {T['completedAt']}. 게임 id 중복 제거 후 목록 {P['inventoryN']:,}판, 분석 {P['analysedN']:,}판, 엄격 상위 10팀끼리 목록 {P['strictInventoryN']:,}판. 목록에서 기보가 없는 항목 {P['missingReplayN']}개는 제외하고 population.json에 남겼다. 에피소드 {P['episodeN']:,}개다. strict 조기 표는 {early['completedAt']}에 {early['population']['analysedN']:,}판을 저장했다. 추출이 끝난 뒤 최종 목록을 한 번 더 고정해 그때까지 도착한 기보를 반영했다.", '',
 f"[사실] 우리 W0–W12 및 v1-w1..3는 {P['oursInventoryN']}판. UnderTheC는 {P['underInventoryN']}판. 맞춤 지도 목록 N={P['customInventoryN']}이다. 맞춤 지도 여부는 기존 열 지도 이름 이외라는 조작적 구분으로, 본선이라는 서버 표식의 확인과는 구분한다.", '',
 f"[사실] stalled 추정으로 상위권 집계에서 제외한 게임 N={P['rejectedStallN']}. 기존 연구와 같은 ‘100라운드 이상, 한 팀의 sonar=0 및 분열≤3’ 규칙이다. 조용한 요새를 제외할 수 있는 휴리스틱이며, 원기보·에피소드는 삭제하지 않았다. 우리와 UnderTheC의 기준선에서는 이 제외를 적용하지 않았다.", '',
 '[사실] ① 전체 기보를 스크립트로 재구성하고 표를 먼저 저장했다. ② 에피소드 결과·머릿수·판면 조건의 분류와 크기를 확정했다. ③ 유형마다 그 특징의 평균에 가까운 서로 다른 게임 최대 세 개를 선택해 직전 세 결정을 읽고 eval/board.js로 그렸다. 상위권 깊은읽기는 strict 대전의 각 유형 안에서 고르며, 우리 사례는 전체 우리 온라인 집단에서 고른다. 극적인 사례를 임의로 고르지 않았다. classes.json과 selection.json에 N·선택 점수가 있다.','',
 f"[사실] 우리 시리즈별 경기 수: {dict(collections.Counter(t.get('set','collector') for t in json.loads((O/'population.json').read_text())['tasks'] if t.get('us')))}. 여러 제출 버전의 기록이므로 모든 실패를 현재 v1.7의 효과라고 해석하지 않는다.", '',
 '[사실] 조기 strict 표의 노출-교환 플래그와 제삼 몸 접촉의 isolated 제외 조건을 최종 재집계에서 고쳤다. 에피소드 진입·끝·결과 id는 바꾸지 않았고 전수 독립 재구성으로 확인했다. 조기 파일은 tables-strict-first.json.gz에 보존하고 tables-strict.json은 최종 정의로 갱신했다.', '',
 '[사실] strict는 수집 당시 rank A/B가 모두 1–10인 게임이다. elite는 해당 편의 수집 rank가 1–10인 게임이며, population은 요청한 data/top과 data/elite 전체 수집 기보의 편이며, 원 요청의 전체 상위권 자료에 해당한다. 실제 랭크 1–10 편만 보는 elite는 더 좁은 추가 집단이다. winner/loser는 결투 결과가 아니라 최종 경기 승패다. 반복 팀·시리즈·동일 게임의 두 편은 독립 표본이 아니므로 p값이나 인과 효과를 주장하지 않는다.','',
 '## 2. 정의와 관측 한계','',
 '[사실] 진입은 적대 두 머리의 지형 BFS 거리가 4 이하가 되는 라운드 시작 또는 action 종료/사망 직전 판면이다. 켈프·포털·경계 래핑을 반영하며 몸은 거리 계산에서 제외한다. 포털에서 방향성이 생길 수 있어 양방향 거리의 작은 값을 쓴다. 각 편의 id는 평생 고정이고 새끼는 더 높은 id를 받는다.','',
 '[사실] 제삼의 머리가 둘 중 하나와 BFS 5 이내면 third_party로 끝낸다. 진입 때부터 제삼자가 있는 경우도 즉시 종료하며, 같은 쌍은 라운드 시작에서 거리 4를 벗어나기 전 재진입하지 않는다. 거리 6 초과가 3라운드 지속하면 disengage, 경기 종료는 censored다. 원 정의의 사망 중 직접 죽임·맞교환에 해당하지 않는 경우는 other_death로 남겨 수치가 빠지지 않게 했다.','',
 '[사실] isolated는 검사한 모든 시작·action·분열 판면에서 제삼의 머리가 없고 제삼 몸 접촉도 없었던 사건이다. 질주 중간 통과만으로 스쳐 간 제삼자는 놓칠 수 있어 ‘전 시간 고립’보다 약한 관측 경계 정의다. local1v1은 진입 때 두 머리의 BFS8 이웃 합집합에서 팀 머릿수가 같다는 뜻이다. 지형 거리와 d8·공간은 전체 기보 연구 특징이다. 봇의 7×7 단일 창에서 그대로 알 수 있다고 가정하지 않는다.','',
 '[사실] kill은 파트너 몸으로 Hit Other Body, 또는 파트너와 거리 2 이내에서 Hit Wall/Self를 당하고 파트너가 그 fatal action을 살아남는 경우다. 벽/자기 사망은 파트너가 원인이라는 증명이 없으므로 reason별로 구분한다. trade는 파트너와 Head to Head 한 번이고 사망 둘을 한 사건으로 센다.','',
 '[사실] 여유 공간은 머리에서 지형 BFS5 이내의 빈칸 flood-fill이다. 현재의 모든 몸·자기 꼬리는 막힘으로 취급한다. 적 몸을 제거한 공간과 비교한 감기 후보는 정적 공간 감소이며, 꼬리 이동을 반영한 미래 탈출 증명이 아니다. 벽은 켈프이고 맵 바깥은 래핑한다. 길이 L의 진주 없는 브리프의 1무료걸음 가정에서 진주 없는 총 걸음 여력은 L−1, 추가 여력은 L−2다. 현행 규칙은 첫 ceil(L/4)걸음이 무료이며, 이때 총 여력은 L+ceil(L/4)−2, 추가 여력은 L+ceil(L/4)−3이다. 원기보와 맞는 재구성 모델을 적용했다. 0/1/2+ 여력 구간과 길이에 따른 대소관계는 두 공식에서 같다.','',
 f"[사실] 현재 rules/ALL.md의 무료 질주 규칙이 브리프 및 기존 mass_ledger.js의 1무료걸음 가정과 달랐다. 압축 캐시 검사값을 전수 감사한 N={CAL['N_audited']:,}판 중 {CAL['N_fixed']}판을 ceil(L/4) 모델로 재구성해 이동·분열·진주·최종 상태 검사와 독립 episode id 대조를 모두 통과시켰다. 영향을 받은 우리 기보 N=0, 본선 맞춤 지도 N=0, UnderTheC 아는 지도 N=53이다. 이 수정은 연구 디코더의 오류 수정이며 우리 봇의 성능 향상 수치가 아니다.", '',
 '[사실] 기존 도구 파일은 수정하지 않았다. exp/duel/ledger.js에 로컬 사본을 두고, 보정 경기의 eval/board.js 그림에만 ledger-preload.js를 적용했다. 다른 경기의 1무료걸음 모델이 기보와 맞는다는 사실만으로 실제 규칙이 1무료였다고 단정하지 않는다. 긴 조각의 복수 이동이 없으면 두 모델이 같은 기보를 만든다.', '',
 '## 3. 빈도: 전수 표','',
 '각 N은 해당 집단의 편-에피소드 수다. 같은 엄격 게임의 두 편에 맞교환이 각각 한 번 나타나므로 winner/loser 열을 합해 사건 수로 읽지 않는다. 죽임/피살은 episode의 결과이고 최종 승패와 다르다.','']
 rows=[]
 for k in labels:
  g=Z(k);o=g['outcomes'];rows.append([k,g['N_games'],g['N_episodes'],avg(g['N_episodes'],g['N_games']),o.get('kill',0),o.get('killed',0),o.get('trade',0),o.get('disengage',0),o.get('third_party',0),o.get('other_death',0),o.get('censored',0)])
 lines+=table(['집단','N 경기','N 에피소드','평균/경기','죽임','피살','교환','이탈','제삼자','그밖 사망','검열'],rows)
 for suffix,title in [('|local_equal_uncontested','진입 제삼자 없음 + 시작 d8 수 같음'),('|isolated','끝까지 제삼자 없는 isolated')]:
  lines+=['',f'### {title}',''];rr=[]
  for k in labels:
   g=Z(k+suffix);o=g['outcomes'];rr.append([k,g['N_episodes'],o.get('kill',0),o.get('killed',0),o.get('trade',0),o.get('disengage',0),o.get('third_party',0),o.get('other_death',0),o.get('censored',0)])
  lines+=table(['집단','N','죽임','피살','교환','이탈','제삼자','그밖 사망','검열'],rr)
 lines+=['','직접 몸 충돌(O)과 근접 벽(W)·자기 몸(S) 사망의 연관을 분리한다.','']
 lines+=table(['집단','죽임 O/W/S (N)','피살 O/W/S (N)'],[[k,Z(k).get('killReasons',{}),Z(k).get('killedReasons',{})] for k in labels])
 lines+=['','[해석] 승패 집단의 차이는 최종 승리와 함께 나타나는 행동의 차이다. 머릿수·위치·시간·길이가 다르므로 개별 결투 항을 바꿨을 때의 효과로 읽을 수 없다.','']
 for k in ['population/winner','population/loser','elite/winner','elite/loser','ours','ours/custom','under/known','under/known_autoscrim','under/custom','sprint_custom/winner','sprint_custom/loser']:
  g=Z(k);n=g['N_episodes'];third=g['outcomes'].get('third_party',0);iso=Z(k+'|isolated')['N_episodes'];lines.append(f"[사실] {k}: 제삼자 종료 {third:,}/{n:,}={pct(third,n)}, 고립 완료 {iso:,}/{n:,}={pct(iso,n)}. 따라서 고립 결투의 규칙만으로 군집 싸움 전체를 설명하지 않는다.")
 lines+=['','### 지도별·단계별','', 'N 에피소드; 단계는 진입 라운드다. 게임이 끝나 해당 단계에 도달하지 않은 판은 N 경기에서 제외한다. 지도×단계의 교차표와 추가 조건표는 tables.json에 있다.','']
 for dim in ['map','phase']:
  rr=[]
  for k in ['population/winner','population/loser','elite/winner','elite/loser','ours','ours/custom','under/known','under/known_autoscrim','under/custom','sprint_custom/winner','sprint_custom/loser']:
   for name,g in sorted(G.items()):
    if not name.startswith(k+'|'+dim+'=') or name.count('|')!=1:continue
    o=g['outcomes'];rr.append([k,name.split('=')[-1],g['N_games'],g['N_episodes'],o.get('kill',0),o.get('killed',0),o.get('trade',0),o.get('disengage',0),o.get('third_party',0)])
  lines+=table(['집단',dim,'N 경기','N','죽임','피살','교환','이탈','제삼자'],rr)+['']
 lines+=['## 4. 어떤 조건에서 끝나는가','',
 '[사실] action 종료 직전의 진입에는 fatal action이 포함된다. 그 순간의 길이·공간은 이미 해당 행동의 영향을 받았으므로 원인 변수로 읽을 수 없다. tables.json의 각 조건에 roundStartN/roundStartOutcomes를 따로 남겼고, 아래에 라운드 시작 진입만의 핵심 조건도 분리했다.', '',
 '[사실] 아래는 진입 제삼자가 없는 에피소드만의 시작 특징이다. N에 third_party·검열도 포함한다. 길이·공간·id는 서로 관련되므로 한 열의 차이를 해당 항의 인과 효과로 읽지 않는다. 길이×id, 공간×id 교차표도 tables.json에 있다.','']
 for field,title in [('lengthDifference','상대와 길이 차'),('sprintBudget','추가 질주 여력'),('sprintBudgetDifference','상대와 추가 질주 여력 차'),('space','자기 여유 공간 절대 크기'),('order','같은 라운드 실행 순서'),('spaceDifference','여유 공간 차: low <−4 / mid −4..4 / high >4'),('kelpDistance','켈프까지 거리'),('nearPearls','7×7의 진주 수'),('nearAllies','에피소드 밖 아군 머리 BFS8'),('visibleBalance','7×7의 자기 포함 아군/적 머리 수')]:
  lines+=['',f'### {title}',''];rr=[]
  for k in ['population/winner','population/loser','elite/winner','elite/loser','ours','ours/custom','under/known','under/known_autoscrim','under/custom','sprint_custom/winner','sprint_custom/loser']:
   for b,x in sorted(Z(k)['features'].get(field,{}).items()):
    o=x['outcomes'];rr.append([k,b,x['N'],o.get('kill',0),o.get('killed',0),o.get('trade',0),o.get('disengage',0),pct(o.get('kill',0),x['N'])])
  lines+=table(['집단','조건','N','죽임','피살','교환','이탈','죽임/N'],rr)
 lines+=['','### 라운드 시작에 이미 근접한 경우만의 조건','']
 for field in ['lengthDifference','order','spaceDifference']:
  rr=[]
  for k in ['population/winner','population/loser','elite/winner','elite/loser','ours','under/custom']:
   for b,x in sorted(Z(k)['features'].get(field,{}).items()):
    n=x.get('roundStartN',0);o=x.get('roundStartOutcomes',{});rr.append([k,field,b,n,o.get('kill',0),o.get('killed',0),o.get('trade',0),o.get('disengage',0)])
  lines+=table(['집단','특징','조건','N','죽임','피살','교환','이탈'],rr)+['']
 lines+=['','## 5. 죽이는 유형과 시도 뒤 결과','',
 '[사실] 한 드래곤의 질주 여러 걸음 사이에 다른 드래곤의 차례가 끼어들지 않는다. 나중 id는 이미 놓인 몸을 보고 판단한다. 따라서 단순히 직전 진행 칸을 가로막았다는 사실은 피할 수 없는 죽임을 뜻하지 않는다.', '',
 '[사실] 끊기 후보는 상대의 최근 진행 방향 다음 칸에 이번 이동으로 새 몸을 남긴 경우다. 사망 끊기는 실제 충돌한 몸 칸이 최근 2라운드 안에 만들어진 경우다. 그 몸을 만든 이동이 두 걸음 이상이면 질주 끊기다. kelp pin은 빈출구≤1, 켈프와 적 몸이 함께 막고 파트너가 거리≤2다. coil은 적 몸을 지우면 공간이 4칸 이상 늘고 현재 공간≤L+2이며 가까운 적 몸이≥3이다.','',
 '[사실] head_bait는 적이 유효한 최대 4걸음 경로로 닿을 수 있는 칸에 머리를 남긴 뒤의 교환 흔적이다. pearl_bait는 진주를 실제 먹은 이동에서 그런 노출이 있었던 흔적이다. 둘 모두 의도를 뜻하지 않는다. 도달 노출 대리 지표는 최대 4걸음만 보므로 더 긴 실제 질주에 대한 노출을 놓칠 수 있다. 직접 충돌 전수는 요청한 이동 길이 전체를 재구성한다. 시도 성공률은 그 조건을 보인 에피소드가 이후 kill/trade로 끝난 비율이지, 다른 수 대비 성공률이 아니다. 사망 유형은 겹치며 exclusive kill은 질주 끊기→끊기→벽 몰기→감기→진주 추격→기타 순서다.','']
 rr=[]
 for k in ['population/winner','population/loser','elite/winner','elite/loser','ours','ours/custom','under/known','under/known_autoscrim','under/custom','sprint_custom/winner','sprint_custom/loser']:
  g=Z(k);den=g['outcomes'].get('kill',0);terminal=sum(g['outcomes'].get(f,0) for f in ['kill','killed','trade'])
  for pat,x in g['patterns'].items():rr.append([k,pat,x['attemptEpisodes'],x['attemptEvents'],x['killAfterAttempt'],pct(x['killAfterAttempt'],x['attemptEpisodes']),x['tradeAfterAttempt'],pct(x['tradeAfterAttempt'],x['attemptEpisodes']),x['deathAfterAttempt'],x['fatalFlag'],f"{pct(x['fatalFlag'],terminal)} ({x['fatalFlag']}/{terminal})",x['killExclusive'],f"{pct(x['killExclusive'],den)} ({x['killExclusive']}/{den})"])
 lines+=table(['집단','유형','N 시도 ep','시도 사건','뒤 죽임','죽임/시도','뒤 교환','교환/시도','뒤 사망','종결 대리조건','kill·피살·교환 중 몫','배타 죽임','죽임 중 몫'],rr)
 lines+=['','### 전수 분류 뒤 깊게 읽은 사례','']
 for pat in ['cut_off','sprint_cut','wall_pin','coil','head_bait','pearl_bait']:
  key='elite/'+pat;cl=C['classes'].get(key,{'N':0});chosen=[x for x in S if x['class']==key]
  lines += ['',f"#### {pat}: 분류 N={cl['N']}, 선택 N={len(chosen)}",'']
  if not chosen:lines.append('[사실] 이 조작적 조건에 해당하는 사례가 없다. 해당 패턴의 의도나 성공률을 입증하지 못한다.');continue
  for x in chosen:
   e=x['episode'];lines.append(f"- [사실] 게임 **{e['gameId']}**, {e['map']}, **r{e['start']}–{e['end']}**, id {e['ids']}, 결과 {e['outcome']}. [직전 결정](../../exp/duel/reads/{x['slug']}.md), [전체 판면](../../exp/duel/boards/{x['slug']}.png), [7×7 판단 시야](../../exp/duel/boards/{x['slug']}-micro.png), [board.js 원문](../../exp/duel/boards/{x['slug']}.txt).")
   if x==chosen[0]:lines.append(f"![{pat}: 게임 {e['gameId']} 판단 시야](../../exp/duel/boards/{x['slug']}-micro.png)")
   vid=e['detail'].get('dead');dec=e['lastDecisions'].get(str(vid),[]) if vid is not None else []
   if not dec and e['outcome']=='trade':dec=e['lastDecisions'].get(str(e['ids'][0]),[])
   notes=[]
   for a in dec:notes.append(f"r{a['r']} #{a['id']} L{a['len']}: {''.join(a['action'].get('steps',[])) or a['action'].get('kind')} @{a['head']}→{a['after']}, 빈출구 {a.get('free')}, 시야 아군/적 {a.get('visibleAlly')}/{a.get('visibleEnemy')}, 섭취 {a.get('eaten')}")
   lines.append('  - [사실] '+(' → '.join(notes) if notes else '자기 차례 이전 사망이어서 마지막 결정이 없는 경우다.'))
 lines+=['','### 판면과 세 결정을 직접 읽은 해석','',f'[사실] 자동으로 직전 결정을 정리하고 그림을 만든 사례 N={len(S)}, 분류 N={len(C["classes"])}. 이 중 strict 유형별 대표 세 결정 N=18사례를 직접 비교하고, 전체/7×7 PNG N=12장을 육안 확인했다. 나머지 그림의 생성·연결은 파일 검사로 확인했다.','',
 '[사실] strict 대표 끊기 3/3은 Trauma 포털 협로였다(625779 r374–376, 613705 r474–476, 707261 r429–431). 피해자는 출구 1→1→0에서 같은 방향을 계속 선택했다. 625779의 실제 충돌 몸은 포털 반대편에 있어 머리 중심 7×7 그림만으로 보이지 않는다. 몸의 생성 시각을 기준으로 붙인 cut_off를 평지에서 머리가 눈앞을 가로지른 사건으로 읽으면 안 된다.', '',
 '[사실] 질주 끊기 대표 3/3에서는 피해자의 마지막 차례 출구가 0이었다. 649396 r403의 L15 적은 NNE로 장벽을 놓고, L3 피해자는 r403 E(출구2)→r404 S(1)→r405 E(0)로 몸에 부딪혔다. 691380은 r443 EE 이후 피해자가 W→W(진주1)→N(출구0)으로 들어갔다. 623954는 긴 조각이 split한 뒤 L2 부모가 진주를 먹으며 SE를 실행한 사례다. 질주 절단을 언제나 큰 길이 우세의 기술로 해석할 수 없다.', '',
 '[사실] 벽 몰기 대표 659225 r212–214에서는 피해자가 N으로 진주를 두 번 먹어 L4→5→6이 되었지만, 적의 r213 WWS 뒤 출구가 3→0이 되어 켈프에 충돌했다. 613705은 포털 몸 충돌과 겹치고, 701782는 벽 몰기 조건 뒤 정면교환으로 끝났다(대표 N=3). 유형 조건과 종결 원인은 구분해야 한다.', '',
 '[사실] 감기 대표 N=3 중 800834 r243과 669078 r256은 정면교환, 625497 r352는 켈프 사망이었다. 800834의 피해 편은 협로에서 W→S→W로 진주를 먹고, 상대는 N→E→N(출구0)으로 교환했다. 완전히 닫힌 원형 포위를 세 사례에서 입증한 것은 아니다. coil 대리 조건은 켈프와 몸이 함께 줄인 공간도 포착한다.', '',
 '[사실] head_bait 대표 N=3 모두 낮은 id가 2걸음으로 들어가 다음 차례가 아직 없는 높은 id를 죽였다(624225 r384 SE, 687878 r189 SE, 739890 r132 ES). 수동 편의 직전 빈출구는 2/1/2였다. pearl_bait 대표 N=3에서도 수동 편은 직전 두 차례 중 진주를 먹었고, 낮은 id가 SW/SS/WW 두 걸음으로 교환했다(628358 r419, 686415 r221, 706255 r96). 의도적 유인인지 정상 진주 추격 뒤 노출인지 기보만으로 구분되지 않는다.', '',
 '[해석] 직접 확인한 행동은 출구 감소, 몸 장벽의 유지, id 순서에 따른 다음 행동 기회의 차이다. ‘미끼를 설계했다’·‘코일을 계획했다’는 별도 의도 증거가 없다. 지도 독립 후보는 이 관측 가능한 상태를 조건으로 해야 한다. 포털 반대편의 미관측 몸을 구현이 안다고 가정하는 규칙은 제외한다.', '',
 '[사실] 맞춤 지도의 질주 끊기도 보인다: 806693 r254 WWW 뒤 피해자는 r255 N(출구0), 806976 r302 NN 뒤 r303 W(0), 806777 r440 ENEE 뒤 높은 id 피해자가 E(0)를 선택했다(대표 N=3). [세 결정과 그림 목록](../../exp/duel/selection.json)의 bracket_contacts/sprint_cut에 연결된다. 이 세 사례는 군집 포함 직접 충돌이며 고립 1:1로 바꿔 부르지 않는다.']
 TC=json.loads((O/'tactical-tables.json').read_text()) if (O/'tactical-tables.json').exists() else {'N_records':0,'groups':{}}
 if TC.get('missing') or TC.get('nonzeroChecks'):raise RuntimeError('tactical reconstruction requires investigation')
 lines+=['','### 군집을 포함한 직접 충돌 전수 (다른 분모)','',f"[사실] 직접 충돌/근접 사망 사건 N={TC['N_records']:,}. 고립 에피소드가 제삼자로 끝난 뒤의 싸움을 별도로 남겼다. O는 실제 상대 몸 id로 귀속한다. W/S는 적 머리 근처라는 연관만 뜻한다. head_bait는 직전 적 관측, pearl_bait는 최근 진주 섭취 흔적이라 에피소드 reach 기준보다 넓다. 두 대리 지표의 N을 합하지 않는다.",'']
 rr=[]
 for k in ['population/winner','population/loser','elite/winner','elite/loser','ours','ours/custom','under/known','under/known_autoscrim','under/custom','sprint_custom/winner','sprint_custom/loser']:
  x=TC['groups'].get(k,{})
  rr.append([k,x.get('N',0),x.get('headContacts',0),x.get('bodyKills',0),x.get('bodyDeaths',0),x.get('nearWallSelf',0),x.get('crowdedN',0)])
 lines+=table(['집단','N 사건','머리 교환','몸으로 죽임','적 몸에 피살','근접 벽/자기 사망','제삼 머리 근접'],rr)
 ownT=TC['groups'].get('ours',{})
 lines+=['',f"[사실] 우리 직접 피살의 유형 수: {ownT.get('ourDeathPatterns',{})}. 우리 실제 몸으로 죽임의 유형 수: {ownT.get('patterns',{})}. near_head/far_head는 상대 머리 거리≤4/초과의 중복 진단 열이다.",'']
 for pat in ['cut_off','sprint_cut','wall_pin','coil','head_bait','pearl_bait']:
  key='contacts/'+pat;cl=C['classes'].get(key,{'N':0});chosen=[x for x in S if x['class']==key]
  lines.append(f"[사실] 군집 포함 {pat}, 분류 N={cl['N']}, 선택 N={len(chosen)}: "+'; '.join(f"게임 {x['episode']['gameId']} r{x['episode']['end']} ([세 결정](../../exp/duel/reads/{x['slug']}.md), [판면](../../exp/duel/boards/{x['slug']}.png), [판단 시야](../../exp/duel/boards/{x['slug']}-micro.png))" for x in chosen)+'.')
 lines+=['','## 6. 우리 온라인 결투와 kill path','']
 rr=[]
 for k in ['population/winner','population/loser','elite/winner','elite/loser','ours','ours/custom','under/known','under/known_autoscrim','under/custom','sprint_custom/winner','sprint_custom/loser']:
  c=Z(k)['allContacts'];rr.append([k,c['N'],c['mover'],c['passive'],pct(c['mover'],c['N']),c.get('sprintMover',0),c.get('passivePriorFree2',0),c.get('passivePriorN',0)])
 lines+=table(['집단','N 정면접촉','들어감','들이받힘','들어감/N','질주 주체','수동 직전 출구≥2','N 직전 결정'],rr)
 lines+=['','[사실] Trophy만의 같은 분모 비교: '+ '; '.join(f"{k} 정면접촉 N={Z(k+'|map=Trophy')['allContacts']['N']}, 들어감 {Z(k+'|map=Trophy')['allContacts']['mover']}, 수동 {Z(k+'|map=Trophy')['allContacts']['passive']}" for k in ['elite/winner','elite/loser','ours'])+'.']
 o=Z('ours');lines+=['',f"[사실] 우리 자기 차례 N={o['N_turns']:,}; 3–4걸음 TRADE 선택 N={o.get('indicators',{}).get('kill_path_selected',{}).get('N',0)}, 전체 차례 중 {pct(o.get('indicators',{}).get('kill_path_selected',{}).get('N',0),o['N_turns'])}. 후보 생성/적격 차례의 분모는 알 수 없다.",f"[사실] 우리 에피소드 N={o['N_episodes']}, 죽임 N={o['outcomes'].get('kill',0)}, 피살 N={o['outcomes'].get('killed',0)}, 교환 N={o['outcomes'].get('trade',0)}. 정면접촉 전체와 isolated 결투의 분모는 다르다. cuts와 killer-body의 상대가 누구인지 직접 대조했다.",'']
 lines+=table(['선택 지시 태그','N 발동','적 머리 교환','그밖/불일치'],[[k,x['N'],x['headTrade'],x['failed']] for k,x in o.get('indicators',{}).items()])
 lines+=['','[사실] plan.cpp의 kill paths 분기는 3–4걸음으로 적 머리에 닿아 tradeValue를 받는 후보를 만든다. 몸으로 자르는 후보라는 뜻이 아니다. 선택되면 TRADE를 기록하고, 기보 이동 길이≥3으로 해당 분기를 식별했다. 1–2걸음 TRADE는 별도다. lntv는 지역 열세로 후보가 거부되었다는 흔적이며, 모든 생성 후보의 N은 기록되지 않는다. 성공은 적 머리 교환의 실행 여부이고 최종 경기 승리나 몸으로 죽임과 구별한다.','']
 for key in ['ours/killed','ours/kill','ours/trade_passive','ours/trade_mover','ours_contacts/killed','ours_contacts/kill','ours_contacts/trade_passive','ours_contacts/trade_mover']:
  cl=C['classes'].get(key,{'N':0});chosen=[x for x in S if x['class']==key];lines.append(f"[사실] {key}, 분류 N={cl['N']}, 선택 N={len(chosen)}: "+'; '.join(f"게임 {x['episode']['gameId']} r{x['episode']['end']} ([직전 세 결정](../../exp/duel/reads/{x['slug']}.md))" for x in chosen)+'.')
 lines+=['','### 우리에게 보인 실패와 본선의 차이','',
 '[사실] 우리 피살 대표에서 748854 r220 E로 진주1을 먹은 L2는 r221 E(출구1, 점수 −1113.0) 뒤 r222 no-exit(0)로 적 몸에 닿았다. 730074는 r423 W(출구1)→r424 escape-split4(0)→r425 L2 no-exit(0)였다. 687755는 r280 N→r281 escape-split5→r282 L2 no-exit로 켈프 사망했다. 분열로 길이를 줄인 사실이 빈출구를 만든다는 뜻은 아니다(서로 다른 게임 사례 N=3).', '',
 '[사실] 우리 실제 몸으로 죽임 대표 632326 r275–278에서는 W→S→E로 남긴 몸에 상대가 S로 충돌했다. 646192 r342–344에서도 S→S→W의 몸 장벽에 상대가 escape split 뒤 W로 부딪혔다. 선택 태그는 통상 이동 평가 문자열이었고 TRADE가 아니었다(사례 N=2). 따라서 실제 몸 죽임과 kill-path 지시를 같은 기제로 합하지 않는다.', '',
 '[사실] 본선 맞춤 지도 우리 N=7판에서는 적 정면접촉 108 중 능동 93(86.1%), 수동 15였다. 능동 93 중 최종 TRADE 태그 77(82.8%)이고, 자신이 짧은 경우 82/93이었다. 직전 자기 포함 가시 머릿수는 우세54/동수28/열세11이었다. 비교 집단 맞춤 지도 승자의 열세 진입은 1,633/15,648=10.4%, 우리는 11/93=11.8%다. 보이는 수 열세만으로 우리 교환을 설명할 차이는 크지 않다.', '',
 '[사실] 우리 본선 사망 N=594: 켈프252, 자기 몸79, 몸147, 정면116. 몸147은 적11/아군136이며, 정면116은 적 접촉108에 대응하는 우리 사망108과 아군 접촉 사망8이다. 직접 적 몸 죽임과 아군 몸 충돌을 분리했다. 고립 episode 죽임/피살은 각각 0으로, 실제 적 몸 피살11을 고립 결투 결과0과 혼동하지 않는다.', '',
 '[해석] 전체 온라인의 낮은 능동 비율을 본선에 그대로 옮겨 ‘더 자주 들이받자’고 권고할 근거가 없다. 본선 N=7은 작고 교환 뒤 승리의 인과 효과도 알 수 없다. 먼저 켈프·자기/아군 몸과 후속 출구를 진단하고, TRADE를 허용한 목적이 왕 성장·생존으로 이어지는지 기제로 확인하는 쪽이 이 자료에 맞는다.']
 lines+=['','## 7. UnderTheC: 자동 대전 기준선과 본선 맞춤 지도','',
 '[사실] 사용자 관찰은 본선의 처음 보는 지도 대응에 한정된다. under/known_autoscrim은 별도 전달된 30판의 아는 지도 기준선이다. under/known에는 수집기가 받은 아는 지도 대전도 합쳤다. under/custom은 본선의 맞춤 지도 대전이며 서로 합해 처음 보는 지도 능력을 주장하지 않는다.','']
 for k in ['under/known_autoscrim','under/known','under/custom','elite/winner','elite/loser','sprint_custom/winner','sprint_custom/loser']:
  p=T['profiles'].get(k);lines+=['',f'### {k}','']
  if not p:lines.append('N=0.');continue
  lines+=table(['r','N 도달 경기','평균 머리','평균 최장','평균 총길이'],[[r,c['N'],avg(c['heads'],c['N']),avg(c['longest'],c['N']),avg(c['total'],c['N'])] for r,c in sorted(p['curves'].items(),key=lambda x:int(x[0]))])
  if p['small'].get('empiricalN',0):lines+=['',f"[사실] 본선에서 관측한 빠른 자연 재생 칸의 부분집합: 자연 진주 섭취 뒤 재생 간격≤12를 두 번 이상 보고, 간격 중앙값≤12인 칸만 사용했다. 판 전체를 읽은 사후 정보이며 모든 샘의 정답 표가 아니다. 해당 칸이 식별된 경기 N={p['small'].get('empiricalGameN',0)}, 작은 조각 위치 N={p['small']['empiricalN']}, 거리≤3 N={p['small']['empiricalNear3']}, 8 초과를 9로 자른 평균 거리 {avg(p['small']['empiricalDistanceSum'],p['small']['empiricalN'])}. death drop은 자연 진주 origin과 구분해 제외했다."]
  n=sum(p['lengths'].values());small=p['small'];fn=p['finalLongest']['N'];lens={b:sum(v for l,v in p['lengths'].items() if (int(l)==2 if b=='2' else 3<=int(l)<=4 if b=='3-4' else 5<=int(l)<=7 if b=='5-7' else int(l)>=8)) for b in ['2','3-4','5-7','8+']};final=p['finalLongest']['values'];lines+=['',f"[사실] 길이 차례 분포 N={n:,}: {lens}. 분열 N={sum(p['splitPhases'].values()):,}, 시점 {p['splitPhases']}. 부모+새끼 형태 상위 6개 {sorted(p['splitShapes'].items(),key=lambda x:-x[1])[:6]}.",f"[사실] L≤4 조각의 5라운드마다 자기 turnStart 위치 N={small.get('N',0):,}: 왕 거리>5 {small.get('farKing',0)}, 적 머리가 7×7에 있음 {small.get('visibleEnemy',0)}, 샘 거리≤3 {small.get('nearFountain',0)}. 거리 평균은 8 초과를 9로 자른 값: 왕 {avg(small.get('kingDistanceSum',0),small.get('N',0))}, 적 {avg(small.get('enemyDistanceSum',0),small.get('N',0))}, 샘 {avg(small.get('fountainDistanceSum',0),small.get('N',0))}. 샘은 지도를 구분할 수 있는 판만 기존 지도 타일로 읽은 연구 정보다. custom 집단의 기존 표 기반 샘 값 0/거리9는 미관측 대체값이므로 실제 샘에서 멀다는 증거가 아니다. 위 경험적 재생 칸 통계와 구분한다.",f"[사실] 사망 원인 N={sum(p['deathCauses'].values()):,}: {p['deathCauses']}. 최종 최장 N={fn}, 평균 {avg(p['finalLongest']['sum'],fn)}, 중앙값 {statistics.median(final) if final else '—'}, 최종 생존 경기 N={sum(v>0 for v in final)}."]
 up=T['profiles'].get('under/known',{});ep=T['profiles'].get('elite/winner',{})
 if up and ep:
  lines+=['','### 기준선에서 다른 점 (지도 구성 통제 전)','']
  for r in ['25','50','100','250','350']:
   a=up['curves'].get(r);b=ep['curves'].get(r)
   if a and b:lines.append(f"[사실] r{r} 머릿수 UnderTheC {avg(a['heads'],a['N'])} (N={a['N']}) / 상위 승자 {avg(b['heads'],b['N'])} (N={b['N']}); 최장 {avg(a['longest'],a['N'])}/{avg(b['longest'],b['N'])}.")
  for label in ['farKing','visibleEnemy','nearFountain']:
   a=up['small'];b=ep['small'];lines.append(f"[사실] 작은 조각 {label}: UnderTheC {a.get(label,0)}/{a.get('N',0)}={pct(a.get(label,0),a.get('N',0))} / 상위 승자 {b.get(label,0)}/{b.get('N',0)}={pct(b.get(label,0),b.get('N',0))}.")
  lines+=['','[해석] 이 차이는 아는 지도 분포·상대 강도·승패 구성이 함께 다른 기준선이다. 처음 보는 지도를 분석하는 능력의 차이라고 해석하지 않는다.']
 lines+=['','### 본선에서 상위권과 다른 점: 승패를 나눠 비교','']
 rr=[]
 for k in ['custom/winner','custom/loser','ours/custom/winner','ours/custom/loser','under/custom/winner','under/custom/loser']:
  c=CC['groups'][k];rr.append([k,c['games'],f"{avg(c['heads50'],c['N50'])} (N={c['N50']})",avg(c['finalSum'],c['games']),avg(c['splits'],c['games']),c['headContacts'],c['mover'],c['enemyBodyDeaths'],c['allyBodyDeaths']])
 lines+=table(['집단','N 경기','r50 머리','최종 최장 평균','분열/경기','N 정면','능동','적 몸 피살','아군 몸 피살'],rr)
 lines+=['',
 '[사실] UnderTheC 본선 N=14판의 L≤4 위치 N=34,306: 왕 거리>5는 32,035(93.4%), 적 머리가 시야에 있음 3,948(11.5%), 경험적 빠른 자연 재생 칸 거리≤3은 6,728(19.6%). 맞춤 지도 승자 기준은 각각 1,120,642/1,183,784(94.7%), 199,863/1,183,784(16.9%), 186,750/1,179,071(15.8%). 왕에서 떨어져 있는 것만은 특이하지 않고, 적을 덜 보며 재생 칸에 더 자주 가까운 차이가 보인다. 같은 조각의 반복 관측이고 지도·승패 분포를 통제하지 않은 위치 통계다.', '',
 '[사실] UnderTheC 본선 사망 N=5,465: No Valid Action(A) 4,637(84.8%), 정면809, 몸18(적1/아군17), 켈프1, 자기 몸0. A의 로컬 ledger 조작적 세부는 trap 2,353/sac 2,284, fault 0/sprintDeath 0이다. trap은 유효 이웃 없음, sac은 유효 이웃은 있지만 행동이 없었음을 뜻한다. 의도적 정리·시간 초과·프로그램 오류 중 무엇인지는 이 태그만으로 확정하지 않는다. 질주 길이 부족 사망으로 세면 틀린다.', '',
 '[사실] UnderTheC 맞춤 지도 실제 적 몸 죽임 N=4, 고립 죽임 N=1(806958 r329 켈프 연관)이다. 806885 r349–351의 L2 id873은 E→E→E로 몸을 남겼고 적 id885는 S→W→N(출구0)으로 충돌했다. 다른 대표 806887 r160과 806959 r132는 상대가 출구0에서 split한 뒤 부모가 죽은 근접 사건이다. 실제 몸 죽임4와 근접 켈프/자기 사망 연관은 별도 분모다.', '',
 '[해석] UnderTheC는 이 본선에서 평지의 단독 절단을 많이 기록한 팀이라고 말하기 어렵다(N=4). 짧은 조각을 많이 만들고, 켈프·몸 충돌은 드물게 남기며, 왕과 떨어진 재생 칸 주변에 조각을 두고, 작은 조각의 교체가 많은 형태가 더 두드러진다. 정찰보다는 분산 수확·교환의 후보 해석도 맞지만, 통신/목표 의도가 보이지 않아 역할과 승리 기여는 미확인이다. 최종 승자만으로 비교하지 않도록 위 표를 승패별로 나눴으며 동일 상황의 대조 실험은 아니다.']
 for key in ['under_bracket/kill','under_bracket/trade_mover','under_bracket/trade_passive','under_bracket_contacts/kill','under_bracket_contacts/killed']:
  chosen=[x for x in S if x['class']==key];cl=C['classes'].get(key,{'N':0});lines.append(f"[사실] {key}, 분류 N={cl['N']}, 선택 N={len(chosen)}: "+'; '.join(f"게임 {x['episode']['gameId']} r{x['episode']['end']} ([세 결정](../../exp/duel/reads/{x['slug']}.md), [시야 그림](../../exp/duel/boards/{x['slug']}-micro.png))" for x in chosen)+'.')
 lines+=['','[해석] 왕에서 멀고 적을 자주 보는 조각은 정찰 역할의 후보 조건이다. 몸 위치만으로는 적 관측의 보고, 분열 목표, sonar 내용, 의도된 역할을 알 수 없다. 샘 접근과 먹이 경쟁도 같은 위치를 만들 수 있으므로 ‘관측자’라고 확정하지 않는다. 본선 맞춤 지도에서 같은 위치 조건이 나타나는지도 별도 N으로 비교한다. 움직임과 사망 흔적만으로 정찰의 효과를 확정하지 않는다.','',
 '## 8. 독립 재집계와 재현','',
 '[사실] 본선 능동접촉의 사전 시야 수 균형과 TRADE 태그도 별도 Python 스트림으로 재집계했다: 우리 정면접촉 주/독립 108/108, 능동 93/93; UnderTheC 정면 595/595, 능동 325/325. 8개 집단의 조건 셀 불일치 0이며 verification-custom.json에 두 수를 함께 남겼다.','',
 f"[사실] 에피소드 전수 재구성: 주 코드 {R['primaryN']:,}, 별도 dragonUpdate 코드 {R['independentN']:,}, 대조 게임 N={R['N_games']:,}, 불일치 게임 {R['mismatchGames']}. 집계 코드 독립 재계산: 주 표 {V['primaryEpisodeN']:,}, Python gzip 스트림 {V['independentEpisodeN']:,}, 불일치 {len(V['mismatches'])}.",'']
 lines+=table(['항목','주 코드','원사건 독립 코드'],[[k,T['verification']['primary'].get(k),T['verification']['independent'].get(k)] for k in ['deaths','headDeaths','enemyContacts','splits','indSelected','indSelectedTrade']])
 lines+=['',f"[사실] 직접 사망 상대 id의 원자료 독립 대조: 머리 교환 주/독립 {TC['verification']['headPrimary']:,}/{TC['verification']['headIndependent']:,}, 적 몸 피살 주/독립 {TC['verification']['bodyPrimary']:,}/{TC['verification']['bodyIndependent']:,}. 수뿐 아니라 각 게임의 (round, victim, killer)도 전부 대조했다."]
 if V.get('tactical'):lines+=['',f"[사실] 직접 충돌/근접 사망 집계도 독립 재계산했다: 주 코드 {V['tactical']['primaryN']:,} / Python {V['tactical']['independentN']:,}. 집단별 실제 몸으로 죽임·몸 피살·머리 교환·근접 벽/자기 사망은 verification.json에 두 수를 함께 남겼다."]
 lines+=['',f"[사실] 엔진 시뮬레이션·최종 상태·질량 검증 합: {T['verification']['checkSums']}. 직접 적 몸 충돌·머리 교환의 상대 id도 별도 dragonUpdate 코드로 매 경기 대조했다. 둘 다 같은 조작적 정의를 쓰므로 정의의 적절성을 검증한 것은 아니다. 재구성/집계 오류를 서로 다른 경로로 검사했다.",'',
 '[사실] 전체 목록 population.json, 표 tables.json, strict 조기 표 tables-strict.json, 에피소드 episodes.jsonl.gz, 원기보 대조 verification-raw.json, 독립 표 verification.json, 유형 classes.json, 판면 boards/에 있다. CPU 정책 효과·7×7 구현 가능성의 실제 적용 결과 N=0.','',
 '## 9. 일반 규칙 후보 — 모두 가설','',
 '[해석] 아래 N은 행동 근거의 기술 통계 분모이며, 규칙을 적용한 게임 N은 전부 0이다. 근접할 때만 현재 7×7과 자기 길이·id·이동 이력으로 발동한다. d8 전체 상태나 고정 지도 표를 구현 입력으로 요구하지 않는다. 적 길이는 현재 보이는 몸만으로 하한만 알 수 있으므로 길이 비교가 불확실하면 교환 보너스를 억제한다. id 순서는 한 라운드 동안 더 높은 id가 아직 움직이지 않았음을 이용하고, 다음 자기 차례까지는 낮은 id도 다음 라운드에서 한 번 움직인다는 것을 포함한다.','']
 ew=Z('elite/winner');oc=o['allContacts'];rules=[
 ['가설: 현행 무료 질주와 후속 몸을 맞추기',f"재구성 보정 N={CAL['N_fixed']}판; 영향받은 우리 온라인 N=0",'자기 시작 길이로 free=ceil(L/4)를 고정하고, 비용과 후속 꼬리 제거량을 max(0,steps−free)로 계산한다. 현재 제출 환경의 규칙을 확인한 뒤 후보를 생성한다.','무료 이동의 과도한 비용 평가와 잘못된 후속 몸 예측을 줄임. 실제 봇 적용 N=0.','SPRINT_COST=1.6 유지, 유료 걸음 수에만 곱함. L5의 2걸음은 기존보다 +1.6, L9의 3걸음 +3.2, L13의 4걸음 +4.8.'],

 ['가설: 첫걸음의 다음 차례 도달 위험',f"우리 정면접촉 N={oc['N']}, 수동 N={oc['passive']}; 상위 승자 접촉 N={ew['allContacts']['N']}",'보이는 적 머리의 합법적인 관측창 안의 경로와 질주 소모를 현재 몸으로 계산한다. 더 높은 id의 이번 라운드 행동과 낮은 id의 다음 라운드 행동을 구별한다. 안전한 다른 끝칸이 있으면 위험 칸을 낮춘다.','능동 머리 절단/질주 들이받힘을 줄임. 대안이 없는 경우는 별도 기록.','T1/T2 첫걸음만: 할인된 −4.8을 위험 조건에서 −24 정도로 복원(차 −19.2), 인접 −30 유지. DFS 전체에 반복하지 않음.'],
 ['가설: 끊기는 새 몸이 유지될 때만',f"상위 승자 끊기 시도 ep N={ew.get('patterns',{}).get('cut_off',{}).get('attemptEpisodes',0)}",'현재 보이는 상대의 마지막 출구/좁은 진로를 줄이고, 적 차례까지 그 몸이 꼬리로 사라지지 않으며 자기 후속 출구가 있는 경로만 컷 후보로 기록. 진행 방향 하나만 막는 보너스는 채택하지 않음.','한 턴의 몸 장벽이 실제 적 경로를 막는지 확인.','새 첫걸음 cut 후보 +3..+6 가설. 진주 +1, sprint −1.6/추가 걸음과 비교; T1·공간 사망 벌점은 유지.'],
 ['가설: 질주 끊기 비용과 탈출 관문',f"상위 승자 질주 끊기 시도 ep N={ew.get('patterns',{}).get('sprint_cut',{}).get('attemptEpisodes',0)}",'질주 후 최소 길이 2와 자기 몸 뒤 빈출구를 확인한다. 진주를 먹을 것이라는 가정 없이 먼저 비용을 지불할 수 있어야 한다.','적 몸 충돌 유도 뒤 자기 oversprint/갇힘을 억제.','SPRINT_COST=1.6 기본 유지; 안전 컷의 작은 보너스 +3..+6만, 공간 부족 AREA_TRAP≈−60 우회 금지.'],
 ['가설: 켈프·자기/아군 몸에서 출구 보존',"우리 본선 사망594: 켈프252/자기79/아군 몸136; escape-split 깊은읽기 N=3",'7×7 첫걸음 뒤 공간과 다음 출구를 계산하며 자기·아군 몸도 막힘으로 넣는다. split 후보는 부모와 새끼의 차례 순서별 출구를 확인한다. 관측 밖을 출구로 확정하지 않는다.','벽 몰기·감기 후보가 완성되기 전에 빠져나옴.','first-step 공간 1→2 회복에 +6..+12 가설. AREA_TRAP60/FILL3/DEADEND8의 적용 관계를 분리해 진단.'],
 ['가설: 보이는 수 균형으로 교환을 허용',f"상위 승자 trade ep N={ew['outcomes'].get('trade',0)}, 우리 trade N={o['outcomes'].get('trade',0)}",'긴 자기 왕을 보존하고, 보이는 수가 열세이면 같은 길이 교환을 억제한다. 짧은 조각·아군 지역 우세·명확한 적 길이의 경우에만 능동 교환을 시험한다.','왕의 손실을 억제하고 교환 허용 이유를 명확히 기록. 우리 본선은 이미 능동93/108이므로 일괄 공격성 증가 근거는 없음.','tradeValue W_KILL=4 기본; 같은 길이 우세 창에 +6..+12 terminal 가설. LNT veto와 왕 관문을 명시적으로 유지·시험.'],
 ['가설: 위험한 진주 추격을 사건으로 기억',f"상위 승자 pearl_bait 시도 ep N={ew.get('patterns',{}).get('pearl_bait',{}).get('attemptEpisodes',0)}",'먹은 뒤 적 도달 칸에 머리를 남기는 후보, 사망 진주 줄을 쫓으며 켈프 출구가 줄어드는 후보를 따로 표시한다. 머리 교환 가치·다음 출구를 같이 비교.','진주 추격 노출과 몸에 막힌 길의 반복 진입을 줄임.','확실한 진주 +1은 유지; 위험도는 첫걸음 T2/space로 −6..−24 조건부 가설. 진주 전체에 일괄 벌점 부여할 근거 없음.']]
 lines+=table(['규칙','근거 N','7×7+자기 상태 발동','예상 기제 효과 (미검증)','기존 항/크기 가설'],rules)
 REPORT.write_text('\n'.join(lines)+'\n')
 T['tactical']=TC;T['customComparison']=CC;T['verification']['customContactRecount']=VC
 T['status']='full population, independently reconstructed/recounted, classes and deep reads completed';T['verification']['rawEpisodeRecount']=R;T['verification']['tableRecount']={'primaryN':V['primaryEpisodeN'],'independentN':V['independentEpisodeN'],'mismatches':len(V['mismatches'])};T['reportAt']=now;(O/'tables.json').write_text(json.dumps(T,ensure_ascii=False,indent=2))
 # Required last artifact, exactly 12 lines.
 summary=[f'W10 결투 전수 연구 완료 {now}',f"전수 분석 {P['analysedN']}판 / 목록 {P['inventoryN']}판; 누락 기보 항목 {P['missingReplayN']}",f"엄격 상위10 대전 목록 {P['strictInventoryN']}판; stalled 제외 {P['rejectedStallN']}판",f"에피소드 주/독립 {R['primaryN']} / {R['independentN']}; 불일치 {R['mismatchGames']}",f"우리 온라인 {P['oursInventoryN']}판; UnderTheC {P['underInventoryN']}판; 맞춤지도 {P['customInventoryN']}판",f"우리 ep {o['N_episodes']}: kill {o['outcomes'].get('kill',0)}, killed {o['outcomes'].get('killed',0)}, trade {o['outcomes'].get('trade',0)}",f"우리 전체 정면 mover {oc['mover']}/{oc['N']}; 본선 mover93/108(86.1%): 일괄 공격성 증가 근거 없음",f"kill-path 선택 {o.get('indicators',{}).get('kill_path_selected',{}).get('N',0)}; 후보 미선택 N은 관측 불가",f"직접 충돌/근접 사망 {TC['N_records']}사건; 깊은읽기 {len(S)}사례",'본선 우리 사망594: 켈프252/자기몸79/아군몸136; UnderTheC 본선14판은 별도 분석','일반 규칙은 가설 7개, 실제 적용 N=0; mapdb/d8 전수 정보는 구현 입력으로 요구하지 않음','보고서 research/observations/duels.md; 표/기보/검증 exp/duel; 네트워크·대전·커밋 없음']
 assert len(summary)==12;(O/'SUMMARY.txt').write_text('\n'.join(summary)+'\n');print('REPORT',REPORT,'SUMMARY 12 lines')
if __name__=='__main__':main()
