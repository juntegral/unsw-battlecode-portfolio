import json,pathlib,datetime,math,collections,statistics
O=pathlib.Path(__file__).resolve().parent;R=O.parents[1];T=json.load(open(O/'tables.json'));D=json.load(open(O/'deep-reads.json'));G=json.load(open(O/'geometry-verification.json'));F=json.load(open(O/'fit-verification.json'));I=json.load(open(O/'elite-inventory.json'));P=json.load(open(O/'population.json'));S=json.load(open(O/'scout.json'))
rows=[]
def add(x=''):rows.append(x)
def fmt(x,d=2):return '–' if x is None else f'{x:.{d}f}'
def pct(x):return '–' if x is None else f'{100*x:.1f}%'
def metric(c,k,field='mean'):return c['metrics'].get(k,{}).get(field)
def table(header,body):
 add('| '+' | '.join(header)+' |');add('| '+' | '.join(['---']*len(header))+' |')
 for row in body:add('| '+' | '.join(str(x) for x in row)+' |')
 add()
known=[(k,a) for k,a in sorted(T['maps'].items()) if not k.endswith('/?') and 'winner' in a['cohorts']]
def model_text(m):
 if m['kind']=='constant':return '상수 '+fmt(m['value'])
 if m['kind']=='isotonic':
  bs=m['blocks'];points=[(min(m['sign']*b['lo'],m['sign']*b['hi']),max(m['sign']*b['lo'],m['sign']*b['hi']),b['v']) for b in bs];points.sort();return m['feature']+' → '+', '.join(('['+fmt(lo,3)+','+fmt(hi,3)+']' if lo!=hi else fmt(lo,3))+':'+fmt(y,3) for lo,hi,y in points)+' (각 block 안 상수, block 사이 선형, 밖은 끝값; 정확값 JSON)'
 def tree(n):
  if 'value' in n:return fmt(n['value'],3)
  return '('+n['feature']+'≤'+fmt(n['cut'],3)+' ? '+tree(n['left'])+' : '+tree(n['right'])+')'
 return tree(m['root'])
counts=T['population']['counts'];top=counts['top'];stall=counts.get('topStalled',0);N=T['population']['processed'];winnerN=sum(a['cohorts']['winner']['N'] for k,a in known)
add('# 미지 지도에 옮길 수 있는 엘리트 원칙')
add()
add(f"[사실] 상위권 목록 동결 **{T['population']['frozenAt']}**, elite 갱신 **{T['population'].get('eliteRefreshedAt')}**. 고유 원자료 **N={N:,}판**, top **N={top:,}판**, 우리 **N={counts['online']:,}판**, top과 겹치지 않는 elite **N={counts['elite']:,}판**을 처리했다. top 멈춤 **N={stall:,}판**을 제외해 **N={top-stall:,}판**을 유지했다. 알려진 판본의 승자/패자 분석은 각각 **N={winnerN:,}팀-판**, **N=15판본·10지도 가족**이다. 미확정 판본과 무승부는 JSON에 별도로 남겼다. 지도가 통계적 일반화 단위이므로 2만 판을 2만 개 미지 지도 검증으로 읽지 않는다.")
add()
add('[해석] 가장 먼저 옮길 것은 지도 이름별 수치보다 **관측의 범위와 신뢰도를 붙이는 규칙**이다. 크기와 wrap은 즉시 알지만, 생성 잠재량·전체 2-core·완전한 고립·중앙 공급 몫은 대개 r30에 확정되지 않는다. 전체 지도 특징으로 설명되는 엘리트 행동과 초반에 실제로 실행할 수 있는 정책을 구분했다. 아래 수치 정책의 신규 봇 실행/승률 검증 **N=0**이다.')
add()
add('[해석] 전이 후보는 **중앙 공급 몫→r100 중앙 배치**, **포켓 공급 몫→포켓 자연 섭취/체류**다. 전자는 지도명 제외 MAE 0.0707, 기하군 제외 0.0745, 후자는 섭취 몫 MAE 0.0531/0.0542다(각 N=15판본·10지도·5기하군). 모두 전체 지도 기준값을 쓴 관계라 r10–30 자동 적용 근거는 아니다. r30 네 관측 특징의 heads100 오차 12.4883은 상수 10.2878보다 크고, middle100 오차 0.2199도 상수 0.2065보다 크다(각 N=15/10/5). 초반 head 정책을 생성 밀도 공식 하나로 고정할 근거는 얻지 못했다.')
add()
add('## 1. 전수 집계 → 크기가 있는 부류 → 선택 정독')
add()
add(f"[사실] 1단계: [extract.js](../../exp/general/extract.js)는 모든 고유 원자료 **N={N:,}판**을 질량 장부의 단계 이동으로 재구성했고, 수정한 [atlas_recount.js](../../exp/general/atlas_recount.js)는 기보 head/tail·분열 몸을 직접 따라갔다. r25/50/100/250의 머리·중앙·포켓, r0–49 분열 및 길이≥4 head-round, 자연 섭취, 희생 순서, 최종 왕의 활성 계보를 대조했다. [enrich.js](../../exp/general/enrich.js)는 희생 드롭의 최종 계보 배달과 포켓 자연 섭취, r300–499 매 5라운드의 왕 경로 거리를 따로 검산했다. `tables.json`은 최초 체크포인트부터 보고서보다 먼저 썼다.")
add()
add('[사실] 빠른 디코더는 sonar 이벤트를 이벤트 목록에서 빼고 `sonarBySender`에 별도로 보관한다. 원래 장부 ping 필드를 사용한 첫 배치의 멈춤 필터를 [repair_metadata.py](../../exp/general/repair_metadata.py)로 고쳤다. 초기/분열 ID로 발신자의 팀을 두 구현에서 별도로 복원했고, 수정된 ping 필드 N=42,713, 멈춤 판정 변경 N=265(우리/elite 포함), 멈춤 필터 독립 불일치 N=0이다. 수정 전후 키와 불일치 수를 [metadata-repair.json](../../exp/general/metadata-repair.json)에 남겼다. 행동 계수는 보존했으며 최종 표는 수정된 필터로 다시 계산했다.')
add()
add('[사실] 2단계의 배타적 기술 부류는 `r100 미도달` → `포켓 자연 섭취 몫≥20%` → `r100 중앙 머리 몫≥40%` → `분산` 순서다. 이는 의도·엔진 또는 승률 인과 분류가 아니다. 지도·승패·개별 웨이브·W0–W12 합산·v1 합산·상위 6팀 부분집합마다 부류 N과 전체 멤버 키를 먼저 저장했다. 합산 코호트는 개별 세트와 겹치므로 코호트 N을 모두 더하지 않는다.')
add()
classrows=[]
for k,a in known:
 c=a['cohorts']['winner'];q=c['classes'];classrows.append([k,c['N'],q.get('no-r100',0),q.get('pocket-harvest',0),q.get('middle-heavy',0),q.get('distributed',0)])
table(['지도/판본','승자 N','r100 미도달 N','포켓 수확 N','중앙 집중 N','분산 N'],classrows)
add(f"[사실] 3단계는 판본별 가장 큰 부류에서 체크포인트 평균에 가장 가까운 승자, W12, v1-w3를 정독했다(**N={D['N']}팀-판 읽기**). 모든 후보 부류 크기와 선택 거리는 [deep-selection.json](../../exp/general/deep-selection.json), 실제 ID·분열·이동·섭취·드롭 및 라운드는 [deep-reads.json](../../exp/general/deep-reads.json)과 압축 `deep-*.json.gz`에 있다. 유리한 점수의 최대 사례를 고르지 않았다.")
add()
add('## 2. 특징의 기준값과 r10–30 관측 가능성')
add()
add('[사실] Vision 규칙 입력 N=1: 머리 주변 **wrap된 7×7**만 본다. kelp가 타일 시야를 가리지 않으며 **portal 너머를 보지 못한다**. sonar의 차단/수신은 별도다. 지도 대칭은 세 후보로 유지하고, 보인 적이 없다는 이유로 고립을 확정하지 않는다.')
add()
add('[사실] 규칙의 kelp는 **칸이 아닌 간선**이다. 아래 통과율은 시작 몸에서 A/B 중 하나라도 도달하는 칸/전체, 이동 가능율은 적어도 한 이웃이 있는 칸/전체로 별도 저장했다. 중간은 시작 **몸 전체**로부터 정적 최단 경로 거리 비율 f∈[.4,.6)이며 화면의 x/y 중앙이 아니다. 폭은 칸에서 가로·세로로 일반 간선만 따라가 kelp/portal에서 끊은 직선 span 중 작은 값의 중앙값이다. `startVertexCut`은 시작 몸 사이 독립 경로 수로 폭과 다르다. 각 기준값은 **N=1지도 파일/판본**, 독립 대조는 **N=15판본**이다.')
add()
geo=[]
for k,a in known:
 f=a['features'];geo.append([k,f"{f['W']}×{f['H']}",pct(f['passableTileShare']),pct(f['kelpDensity']),f['spawnTiles'],fmt(f['capacity']),pct(f['fountainShare']),f"{f['pocketCount']} / {f['pocketTiles']}",fmt(f.get('corridorWidthMedian'),0),f['startDistance'] if f['startDistance'] is not None else '연결 없음',f.get('startVertexCut'),pct(f['centreSpawnShare'])+'/'+pct(f['centreCapacityShare']),pct(f['edgeSpawnShare'])])
table(['지도/판본 (각 N=1)','크기','통과율','kelp/간선','생성 칸','잠재량/round','샘/생성칸','포켓 수/칸','폭 중앙','시작 머리 거리','경로 cut','중앙 칸/공급 몫','좌표 가장자리 칸 몫'],geo)
add('[사실] 샘 정의는 숨겨진 gap 평균≤12, 생성 잠재량은 Σ 1/meanGap이다. 이는 **지도 파일 기준값**이다. 봇 입력에 min/max는 없고, 현재 countdown과 -1(생성하지 않음)만 보인다. 성공한 생성은 몸/진주 점유로 억제되며 잠재량보다 작다. 전체 생성 좌표는 `maps.*.features.spawnPositions`, r10/20/30에 보인 좌표별 빈도·N은 `cohorts.*.seenSpawnPositions`에 있다. 알려지지 않은 판본의 생성 특징은 0 대신 null이다.')
add()
obs=[]
for k,a in known:
 c=a['cohorts']['winner'];f=a['features'];e10=c['early'].get('10',{});e30=c['early'].get('30',{});q=S['maps'][k]['A']['30'];rate=e30.get('capacitySuccessfulProxy',{}).get('mean')
 obs.append([k,e10['coverage']['N'],pct(e10['coverage']['mean']),e30['coverage']['N'],pct(e30['coverage']['mean']),pct(e30['individualCoverageMax']['mean']),pct(e30['spawnSeenShare']['mean']),fmt(e30['spawnDensityEstimate']['mean']-f['spawnDensity'],3),fmt(e30['kelpDensityEstimate']['mean']-f['kelpDensity'],3),fmt(rate/f['capacity'] if rate is not None and f['capacity'] else None),pct(q['coverage'])])
table(['지도/판본','r10 N','아군 합집합 r10','r30 N','아군 합집합 r30','최대 개체 누적 r30','생성칸 발견 몫 r30','생성 밀도 bias','kelp bias','성공생성 proxy/잠재량','정찰 계획 r30 (각 N=1좌석)'],obs)
add('[사실] 위 합집합은 실제 머리 경로의 7×7 시야를 합친 **완전 공유 상한**이다. 개체 누적 시야는 분열 부모의 메모리를 새 자식에게 자동 상속하지 않았다. sonar는 첫 kelp/몸에서 멈추고 발신자·팀 식별 정보를 주지 않는다. 같은 방향 두 메시지는 마지막 것만 나가며 죽는 턴에는 발신하지 않는다. 표의 시야가 모든 개체의 실제 지식이라는 검증 **N=0**이다. r0 개체 시야 크기는 각 머리 49칸이며, 테이블의 개체 누적 hook 평균 r0는 첫 행동자 편향이 있어 신뢰도 판정에는 r10 이후만 썼다.')
add()
add('[사실] 리플레이에는 countdown 이벤트가 없어 **실제 countdown reset 추정의 오차 검증 N=0**이다. 대신 보이는 생성 칸의 노출 라운드와 성공한 자연 출현을 세었다. 잠재율 oracle을 보인 칸에 대입한 외삽도 JSON에 별도 표시했고 조기 실행 모형에는 넣지 않았다. 대칭 판별의 현재 전수 시야 audit은 **생성 support의 모순만** 이용했다. 그 대칭 확장은 생성 support용이며 간선·portal 구조까지 확정한 결과가 아니다.')
add()
table(['특징','봇이 추정 가능한 시기','신뢰 조건/미확정 처리'],[
 ['크기·wrap·초기 own heads','r0, 규칙/입력 N=1','정확. 자식/재시작 init은 게임 r0가 아니다'],
 ['전체 시작 질량·왕 씨앗','자기 길이 r0; 아군 합 r0–10 조건부','모든 시작 루트의 행동 전 길이 보고 필요. 완전 공유 실행 검증 N=0'],
 ['통과율·kelp·국지 폭','국지 r0; 지도 외삽 r10–30','좌표/간선 중복 제거; 전수 위 시야 N과 bias; 탐색 경로 편향'],
 ['생성 칸·좌표','시야 안 r0; 전체는 탐색 후','countdown≥0 정확; 미관측 총수는 하한; 검증 N은 위 표'],
 ['생성률·샘 몫','빠른 칸 r10–30, 느린 칸 더 늦게','연속 countdown reset과 노출. 제안 ≥4 reset; 이 gate의 정밀도 검증 N=0'],
 ['포켓 수·2-core','완전히 본 작은 pocket r10–30; 전체 더 늦게','모든 간선·단일 입구·알려진 cycle을 확인. 미탐색 frontier를 막다른 길로 분류하지 않음'],
 ['시작 거리·고립','r10–30 조건부, 또는 전체 survey 뒤','대칭/시작 몸·portal 짝 필요. 미관측 portal을 닫아 거리 하한/고립을 증명하지 않음'],
 ['중앙 칸/공급 몫','r10–30 조건부; 공급률 신뢰는 더 늦게','정적 경로 거리 구간과 생성률 둘 다 필요. 알 수 없는 칸은 중앙에서 제외하지 않고 unknown'],
 ['좌표 가장자리 몫','본 생성칸에서 r0 이후','wrap이 있으므로 가장자리=안전한 본진이라고 해석하지 않음']])
add('[해석] 한 번 본 작은 countdown으로 샘을 분류하거나, 성공한 출현 수를 잠재 재생성률로 써서 head 목표를 줄이면 수요를 크게 낮춰 잡을 수 있다. 대칭 칸은 countdown을 공유하므로 독립 reset 표본 수를 두 배로 세지 않는다. 현재 자료가 지지하는 것은 생성 **위치**와 공급 **속도**를 따로 측정하는 절차다. 새로운 reset 추정기를 검증했다고 주장하지 않는다(N=0).')
add()
add('## 3. 승자/패자 행동 곡선과 공급·전환')
add()
beh=[]
for k,a in known:
 w=a['cohorts']['winner'];l=a['cohorts']['loser']
 hs=[]
 for r in [25,50,100,250]:hs.append(fmt(metric(w,'heads'+str(r)),1)+'/'+fmt(metric(l,'heads'+str(r)),1)+f" (N={w['metrics']['heads'+str(r)]['N']})")
 beh.append([k,w['N'],*hs,fmt(w['pooled']['splitSpeed50'])+'/'+fmt(l['pooled']['splitSpeed50']),' / '.join(pct(w['pooled']['middle'+str(rr)])+'/'+pct(l['pooled']['middle'+str(rr)]) for rr in [25,50,100]),fmt(w['pooled']['intakePerHR'],3)+'/'+fmt(l['pooled']['intakePerHR'],3)])
table(['지도/판본','승/패 각각 N','heads r25 승/패','r50 승/패','r100 승/패','r250 승/패','분열/eligible HR r0–49 승/패','중간 r25,50,100 각각 승/패','자연 섭취/HR 승/패'],beh)
add('[사실] 분열 분모는 길이≥4 머리-라운드다. 섭취 분모는 해당 판이 실제 진행한 모든 head-round이며, 원수와 분모는 JSON에 있다. 중앙 비율은 합산 중앙 머리/합산 머리다. r250 머리는 그 라운드에 도달한 판의 조건부 수치이며 짧은 전멸형의 전수 목표가 아니다. 승자·패자 차의 게임별 대응 평균·N·분포는 `pairedWinnerMinusLoser`에 있다.')
add()
conv=[]
for k,a in known:
 w=a['cohorts']['winner'];l=a['cohorts']['loser'];s=w.get('safety',{})
 conv.append([k,w['N'],str(w['pooled']['sacClockHalfPeak'])+'/'+str(l['pooled']['sacClockHalfPeak']),fmt(metric(w,'sacOnset20'),0)+'/'+fmt(metric(l,'sacOnset20'),0)+', '+fmt(metric(w,'sacOnset50'),0)+'/'+fmt(metric(l,'sacOnset50'),0)+f" (N={w['metrics']['sacOnset20']['N']}/{l['metrics']['sacOnset20']['N']})",fmt(w['pooled']['sacRate240'],3)+'→'+fmt(w['pooled']['sacRate250'],3)+' / '+fmt(l['pooled']['sacRate240'],3)+'→'+fmt(l['pooled']['sacRate250'],3),pct(w['pooled']['pocketIntakeShare'])+'/'+pct(l['pooled']['pocketIntakeShare'])+', '+pct(w['pooled']['pocketHRShare'])+'/'+pct(l['pooled']['pocketHRShare']),w['conversion']['N500'],pct(w['pooled']['lineShare300'])+'/'+pct(l['pooled']['lineShare300']),fmt(metric(w,'kingGrowth300_500'),3)+'/'+fmt(metric(l,'kingGrowth300_500'),3),str(s.get('p10Reachable'))+'/'+str(l.get('safety',{}).get('p10Reachable')),pct(s.get('le3'))+'/'+pct(l.get('safety',{}).get('le3')),str(s.get('sampleRoundsN'))+'/'+str(l.get('safety',{}).get('sampleRoundsN'))])
table(['지도/판본','승/패 각각 N','희생 half-peak 승/패','onset20,50 각각 승/패','r240대→r250대 희생/팀-round','포켓 자연,HR 몫 각각 승/패','500완주 N','왕 배달 line share 승/패','계보 성장/round r300–500 승/패','왕 거리 p10 승/패','거리≤3 몫 승/패','왕 표본-round N 승/패'],conv)
add('[사실] `clock`은 r200 이후 10라운드 희생률의 최고치 절반에 처음 닿은 bin이고, onset20/50은 각 판의 r200 이후 희생 이벤트 누적 20/50% 라운드다. 이는 첫 희생과 다르다. line share는 r300–499에 생성된 희생 드롭 중 최종 왕의 **활성** 계보가 끝까지 직접 먹은 몫이다. r300 이후 왕이 먹은 희생 진주는 더 일찍 생성된 드롭도 포함해 다른 계수다. 성장률은 마지막 왕의 r300 활성 조상 길이에서 최종 길이까지이며 왕 ID가 고정되어 있었다는 뜻이 아니다.')
add()
add('[해석] 포켓의 유무와 섭취 강도는 지도 기하에 조건부다. 섭취만으로 이익을 확정하지 않는다. 기존 [pocket-harvest](pocket-harvest.md)의 샘 포켓은 PD10에서 순질량 −73/835 승자 게임, Trauma에서 +216,526/1,869 승자 게임이었다(각 원래 N; 현재 동결과 다른 모집단). 짧은 진입→역방향 자식 반출→드롭 재회수가 관측되지만, 모든 포켓을 동일한 자동 수익기로 다루면 안 된다. 기존 [conversion-protocol](conversion-protocol.md)의 local relay와 최종 왕 급식을 구분하는 해석을 유지한다. 새 전환 프로토콜 실행 N=0.')
add()
add('## 4. 무엇이 불변이고 무엇이 특징에 따라 바뀌는가')
add()
split=[a['cohorts']['winner']['pooled']['splitSpeed50'] for k,a in known];growth=[metric(a['cohorts']['winner'],'kingGrowth300_500') for k,a in known if metric(a['cohorts']['winner'],'kingGrowth300_500') is not None]
add(f"[사실] 승자 분열 속도의 범위는 **{min(split):.3f}–{max(split):.3f} / eligible HR (N=15판본)**이다. 이 범위 내 적극적 분열은 공통이지만 같은 0.65 상수라고 할 수 없다. 500완주 승자의 왕 계보 성장 평균은 **{min(growth):.3f}–{max(growth):.3f}/round (N={len(growth)}판본; 게임 N은 위 표)**다. 양의 후반 성장은 공통이지만 크기가 크게 다르며 최종 승패로 표본을 고른 결과도 포함한다.")
add()
add('[해석] 상수 모형이 검증에서 이겼다는 이유만으로 행동이 지도 불변이라고 부르지 않는다. 관측 지도 간 범위가 크고 단순 특징이 예측하지 못하면 **미설명 지도 차이**다. 높은 머리 수 자체를 같은 시각에 모든 지도에 강제하거나, r250을 모든 head의 일괄 희생 시계로 쓰는 규칙은 별도로 검증해야 한다(N=0). 왕의 실제 급식 경로·ID·사망까지 연결해야 하며 머리가 많다는 조건만으로 전환 성공을 뜻하지 않는다.')
add()
add('## 5. 지도/가족 제외 검증')
add()
add('[사실] 주 검증 leave-one-map-out은 **N=10지도명**의 모든 판본을 함께 빼며, 보조 leave-one-layout-out은 **N=15물리 판본**을 한 개씩 뺐다. 더 엄격한 leave-one-family-out은 결과 fitting 전에 고정한 **N=5기하군**(고립, 시작거리≥40, 면적≥1500, 초기왕≥8·면적≤1100, 나머지 접촉형)을 통째로 뺐다. 기하군은 위 순서로 배정했고 map 이름을 특징으로 넣지 않았다. JSON의 `leaveFamilyOut`은 지도명 제외, `leaveGeometryFamilyOut`은 기하군 제외다. 안쪽 모형 선택은 지도명 전체를 뺐으며 고정 상수, 특징 하나의 단조 관계, 깊이≤2·잎≥3판본의 작은 tree를 비교했다. 잎/단조 block은 중앙값이고 가족의 총 가중치를 같게 했다. 내부 MAE 개선<3%면 상수를 택했다. 부호·특징·tree 선택을 held-out 지도에서 정하지 않았다. bootstrap은 목표별 최대 N=10가족 오차의 민감도이며 CV 학습집합이 겹치므로 미래 지도 보장 구간이 아니다.')
add()
fitrows=[]
for y,f in T['fits'].items():
 a=f['leaveLayoutOut']['score'];b=f['leaveFamilyOut']['score'];base=f['leaveFamilyOut']['baseline'];e=f['runtimeEarly']['30']['leaveFamilyOut']['score'];g=f['leaveGeometryFamilyOut'];eg=f['runtimeEarly']['30']['leaveGeometryFamilyOut']['score'];ci=f['relativeMAE95ByFamily'];fitrows.append([y,f['NLayouts'],f['NMapFamilies'],fmt(a['MAE'],4),fmt(b['MAE'],4),fmt(base['MAE'],4),pct(f['relativeMAEGain']),pct(ci[0])+'~'+pct(ci[1]),fmt(e['MAE'],4),fmt(g['score']['MAE'],4),pct(f['geometryRelativeMAEGain']),fmt(eg['MAE'],4),f['transferStatus']])
table(['행동 (MAE 원 단위)','판본 N','지도명 N','판본 제외 MAE','지도명 제외 MAE','상수 baseline','MAE 개선','가족 bootstrap 95%','r30 지도 제외 MAE','기하군 제외 MAE (N≤5군)','기하군 개선','r30 기하군 제외 MAE','판정'],fitrows)
add('[사실] r10/r30 실행 모형의 입력은 정확한 area·초기 heads와 시야로 외삽한 kelp/spawn 밀도뿐이다. 공급 gap, 전체 포켓 비중, 전체 경로 거리, 중앙 공급 몫은 주지 않았다. 각각의 별도 모형/검증이 JSON에 있으며, 관측 입력은 winner 탐색 경로의 아군 시야 합집합 평균이므로 낙관적이다. W0–W12/v1의 다른 탐색 경로를 held-out 지도 입력으로 바꾼 `partialRoleShift`도 계산했다. 지도의 행동 목표 예측과 실제 봇의 승률 효과는 다르다(새 엔진 실험 N=0).')
add()
role=[]
for y in ['heads100','middle100','splitSpeed50','sacClockHalfPeak','pocketIntakeShare','lineShare300']:
 if y not in T['fits']:continue
 f=T['fits'][y];rr=f['partialRoleShift'];role.append([y,f['runtimeEarly']['30']['leaveFamilyOut']['score']['familyN'],fmt(f['runtimeEarly']['30']['leaveFamilyOut']['score']['MAE'],4),fmt(rr['ours:W0-W12']['score']['MAE'],4),rr['ours:W0-W12']['score'].get('familyN'),fmt(rr['ours:v1']['score']['MAE'],4),rr['ours:v1']['score'].get('familyN')])
table(['목표','가족 N','winner 시야 r30 MAE','W0–W12 시야 MAE','가족 N','v1 시야 MAE','가족 N'],role)
add('[해석] JSON의 per-feature screen은 탐색용이다. 최종 모형의 정직한 검증값은 nested 결과다. 판본 제외에서 좋고 지도명 제외에서 나빠지는 관계는 쌍둥이 판본으로 인한 기억 효과를 의심해야 한다. 지도명·기하군 제외 검증 모두 좋아도 전체 지도만 사용할 수 있으면 조기 적용 규칙으로 승격하지 않았다.')
add()
add('## 6. 미지 지도 엔진에 주는 수치 규칙')
add()
add('[해석] 다음은 구현 후보이며 신규 봇/미지 지도 경기 **N=0**이다. 관측 예측의 수치·검증 점수는 함께 적고, 아직 알 수 없는 특징을 지도 이름/숨겨진 gap으로 대체하지 않는다. 모든 개체는 자기 기억과 최근 sonar만 사용하며 공유율을 상태에 붙인다.')
add()
for y in ['heads25','heads50','heads100','heads250','middle100']:
 if y not in T['fits']:continue
 f=T['fits'][y];e=f['runtimeEarly']['30'];add(f"- {y}: r30 관측 모형 **{model_text(e['model'])}**. 가족 제외 MAE **{fmt(e['leaveFamilyOut']['score']['MAE'],3)}, N={e['leaveFamilyOut']['score']['familyN']}가족**. 머리 출력은 정수로 반올림하고 [초기 heads,입력 UNIT_LIMIT]에 제한한다. 기본 제한 64와 보수적 예산 56은 JSON에서 별도로 오차를 검산했다. r25 목표를 r30에 처음 알아서 소급 달성한다고 해석하지 않으며 r0–10 입력 모형/관측 갱신으로 시작한다.")
add()
add('[해석] 위 r30 fitted 모형을 그대로 배포하지 않는다. 지도명·기하군 제외 MAE가 상수보다 각각 ≥10% 좋아질 때만 특징 규칙의 후보로 두는 gate를 추가했다(신규 정책 N=0). heads25/50/100/250는 이 gate를 모두 통과하지 못했다. 임시 **관측 행동 기준**은 가족 동일 가중 중앙값이며 최적 목표가 아니다:')
add()
baselines=[]
for y in ['heads25','heads50','heads100','heads250']:
 f=T['fits'][y];e=f['runtimeEarly']['30'];baselines.append([y,fmt(f['baselineModel']['value'],2),round(f['baselineModel']['value']),fmt(e['leaveFamilyOut']['baseline']['MAE'],3),fmt(e['roundedBaseline64MAE'],3),f['NLayouts'],f['NMapFamilies']])
table(['head 행동 기준','중앙값','반올림 기준','지도 제외 상수 MAE','[H0,64] 반올림 상수 MAE','판본 N','지도 N'],baselines)
add('[해석] [runtime_rules.py](../../exp/general/runtime_rules.py)는 검토용으로 이 gate·입력 UNIT_LIMIT·구간 밖 경고를 구현한다. r10과 r30 모형을 시점에 따라 선택하며 알려지지 않은 지도명/숨겨진 gap을 받지 않는다. 기준 7/13/23/38은 시작 heads보다 낮으면 시작값으로 올리고 입력 제한으로 자른다. r250 기준은 살아서 r250에 도달한 판의 조건부 표본이므로 전멸형 지도에 전원 38마리를 강제하지 않는다. 새로운 봇에서 실행한 N=0이다.')
add()
add('[해석] head 목표는 검증 gate를 거친 **진단 기준**으로 사용한다. 생산적인 자연 섭취/빈 생성 칸이 늘고 안전한 분리 경로가 있으면 목표까지 분열하고, 전선 head 소모·병목 중복 서비스가 커지면 낮춘다. 재생성률만 안다고 전체 head 수를 확정하지 않는다. `ceil(관측 접근 가능 생성율/목표 머리당 섭취율)`은 서비스 수요를 점검하는 예산식으로만 사용한다. 성공 출현으로 잰 율은 하한이고 min/max를 모르는 새 지도에서 이 식의 최적성·승률 검증은 N=0이다.')
add()
add('[해석] 요새 후보는 **r10–30에** area≤1,100, 시작 왕 길이≥8, 길이+4 이상을 수용하는 알려진 cycle, 보호할 생산 pocket/guard 경로를 함께 확인했을 때 우선 검토한다. 이 숫자는 기존 Autarky/PD의 장점을 옮기는 출발 gate이며 최적 엔진 분류 검증 N=0이다. 큰 지도·분산 공급 또는 이 증거가 없으면 떼 탐색/생산을 기본으로 둔다. 시작 왕을 남긴 채 다른 생산 조각을 늘리고 상태가 바뀌면 지역 relay를 붙인다. gap 하나만 보고 일찍 요새로 고정하지 않는다. **고립이 완전히 증명된 경우**에는 전진/적 접촉 head 목표를 0으로 두고 생산+전환을 운용하되 Portals 이름은 조회하지 않는다.')
add()
add('[해석] 전체 중앙 공급 몫을 신뢰할 수 있을 때만 최종 표의 oracle 관계를 목표로 검토한다. 그 전에는 알려진 생산 구역에 도착시간·중복 예약으로 head를 배치하고 미관측 구역은 정찰한다. r30에 모든 머리를 중앙으로 보내는 규칙은 두지 않는다. 생산적 pocket은 수확자를 남기며 확인된 길이 2–3의 진입과 reverse child 반출을 시도할 수 있지만 순질량을 기록한다. 단일 packet의 회수 거리/마감 ETA와 왕 ID 예약을 별도 관리한다(정책 실험 N=0).')
add()
add('[해석] 희생은 한 시각에 전원 전환하지 않는다. r250은 작은 local relay를 검토하는 **최초 점검 시각**, r350은 안전한 왕 후보 점검, r400은 급식 ID 안정화 점검으로 둔다. 받는 쪽의 회수 경로·최근 위치가 없으면 수확을 계속한다. 후보 TTL 4라운드, 첫 드롭 waypoint는 왕 경로의 1–3칸 앞, 큰 패킷은 r460 이전 출하, r475 이후는 1–3턴 첫 회수 가능한 작은 패킷만 허용한다. 이 수치는 기존 conversion 관측에서 가져온 설계 후보로 새 unknown-map 실행 N=0이다. 특히 후반 소수 왕을 elect하는 시계와 r250 지역 재활용을 분리한다.')
add()
add('[해석] 왕 안전은 가능한 경로 거리 하한 4칸, 열린 ingress에서 목표 6–10칸을 검증 출발점으로 삼는다. 이는 sprint를 막는 충분조건이 아니다. 시야 밖 적이 없다고 가정하지 말고 최근 guard/sonar와 보호된 순환 경로를 우선한다. 긴 왕의 공간은 현재 몸+예상 성장+4 이상을 수용하게 계획한다. 도달 불가능한 적은 거리 31 같은 유한 안전 값과 합치지 않는다(새 safety gate 효과 N=0).')
add()
add('## 7. 첫 10–20라운드의 측정 행동')
add()
add('[해석] 실행 순서 후보(신규 시험 N=0):')
add()
add('1. r0에 W/H, unit limit, own count, root ID/초기 길이를 저장한다. 현재 49칸에서 spawner 여부·좌표·kelp/portal ID를 중복 없는 지도로 기록한다. 세 대칭 가설을 유지한다. 초기 자기 긴 몸의 시야 밖 tail을 아는 것으로 가정하지 않는다.')
add('2. r0–5에 수확 동선과 겹치지 않는 짧은 head를 시작 지역마다 최대 1개 정찰자로 배정한다. 알려진 합법 이동 중 새 7×7 칸 수를 우선하고 재방문을 벌점으로 준다. 분열 자식은 새 메모리·새 시야로 탐색하며 부모와 역할/초기 요약을 생존 중 나눠 보낸다. blind portal 조사는 짧은 정찰자에게만 검토하고 긴 왕은 확인된 출구를 쓴다.')
add('3. r5–10에 아직 공유되지 않은 생성 칸·입구·portal 짝을 우선 교환한다. 좌표 bit 수는 W/H에서 계산하며 알려진 63×40 한도를 미지 지도의 최대 크기로 가정하지 않는다. 메시지에 타입·라운드·full ID를 넣고 직접 시야/handshake로 발신자를 확인한다. 같은 방향 메시지 덮어쓰기와 다음 턴 수신 순서를 반영한다.')
add('4. r10–20에는 대표 빠른 생성 칸을 연속으로 보며 reset 횟수와 노출 시간, body/pearl 점유를 따로 기록한다. 느린 칸은 미확정으로 둔다. 동일 대칭 orbit의 draw를 중복 표본으로 세지 않는다. 전체 간선과 입구가 확인된 pocket만 인증하고 단순 탐색 frontier를 포켓으로 세지 않는다.')
add('5. r20–30에 지도 면적 커버율·원래 root 보고율·생성 칸 발견 하한·포켓 인증 수·대칭 후보 수를 갱신한다. 고립/공급률/중앙 판정이 불확실하면 그 값에 의존하는 전원 이동·일괄 희생을 보류하고 지역 생산을 계속한다. 정찰자의 실제 head 비용과 자연 섭취 손실도 판정에 포함한다.')
add()
add('[사실] [scout.json](../../exp/general/scout.json)은 시작 head당 한 정찰자가 시야 이득으로 움직이는 기하적 가능성을 **N=15판본×2좌석=30경로 집합**에서 계산했다. 몸 충돌·분열 비용을 무시한 상한이고, 시작 enemy 몸/portal 짝 가정이 필요해 봇의 실제 고립 증명으로 읽지 않는다. 위 표의 작은 지도와 큰 지도의 r30 커버율 차이는 초기 전체 feature 확정에 걸리는 시간이 지도 크기/연결에 의존함을 보여 준다. 실제 exploration 성능 검증 N=0이다.')
add()
add('## 8. 게임 ID와 라운드 정독')
add()
for v in D['reads']:
 if v['role']!='winner':continue
 task=next(t for t in P['tasks'] if t['key']==v['best']['key']);file=pathlib.Path(task['file']);rel=pathlib.Path('../..')/file.relative_to(R);cp=v['cp'];parts=[]
 for rr in ['25','50','100','250','300','450','499']:
  if rr in cp:parts.append('r'+rr+f" H{cp[rr]['heads']}/M{cp[rr]['middle']}/K{cp[rr]['king']}")
 splits=v['firstSplits'];early='; '.join(f"r{x['r']} #{x['parent']}→#{x['child']} {x['parentLen']}+{x['childLen']}" for x in splits)
 packets=v['packets'];packet=''
 if packets:
  q=packets[0];packet=f" r{q['r']} #{q['id']} L{q['len']} {q['cause']} 드롭{q['drops']}, 최종 활성 계보 직접 섭취 N={len(q['lineEaters'])}."
 add(f"[사실] **{v['mapLayout']}**, [{v['best']['key']} {v['best']['team']}]({rel.as_posix()}): 선택 **N=1**, 부류 **{v['class']} N={v['classN']} / 코호트 N={v['cohortN']}**, 실제 라운드 N={v['rounds']}. {'; '.join(parts)}. 초기 분열: {early or 'r0–49 관측 없음'}. 끝 왕 L{v['kingFinal']}.{packet}")
 add()
add('[해석] 이 정독은 개막 뒤 실제 head가 어디에 남는지와 급식 드롭이 활성 계보로 연결되는지를 확인하는 사례다. 승자의 N=1 궤적을 전수 평균이나 승률 개선 효과로 바꾸지 않는다. W12/v1-w3 대응 사례의 같은 라운드·ID는 deep-reads와 압축 원수에 전부 남겼다.')
add()
add('## 9. 현재 elite와 진짜 미지 지도 확인')
add()
el=[]
for k,a in known:
 c=a['cohorts'].get('elite-own')
 if not c:continue
 w=a['cohorts']['winner'];el.append([k,c['N'],c['metrics']['heads100']['N'],fmt(metric(c,'heads100'),1),fmt(metric(w,'heads100'),1),fmt(c['pooled']['splitSpeed50']),pct(c['pooled']['pocketIntakeShare']),c['conversion']['N500'],pct(c['pooled']['lineShare300'])])
table(['지도/판본','현재 top10 자신의 팀-판 N','r100 N','heads100 elite-own','기존 승자 평균','분열/eligible HR','포켓 자연 몫','500완주 N','왕 line share'],el)
add('[사실] elite는 수집 당시 rank≤10인 쪽의 **자기 행동**만 별도 코호트로 보았다. top와 겹친 game은 alias로 연결해 한 번만 재구성했으며 코호트에는 포함했다. 상대의 세기가 다르므로 elite-own 승패율을 top-vs-top의 인과 검증으로 사용하지 않았다. 행별 N이 작아 패턴 확인용이며 nested fitting에는 섞지 않았다.')
add()
add(f"[사실] 최종 로컬 elite 인덱스 확인 **{I['checkedAt']}**, 목록 N={I['uniqueN']}고유 판, 알려진 10지도 밖 이름 **N={I['unknownN']}판**이다. 따라서 16:30 KST sprint의 진짜 미지 지도 검증 결과는 **N=0**이다. 이번 종료는 sprint 이전이다. 아래 부록을 이후 확인에 사용한다.")
add()
add('[해석] 부록 실행 계획은 [elite-inventory.json](../../exp/general/elite-inventory.json)에 저장했다. 새 이름이 생기면 모델을 **먼저 동결**하고 맵별 고유 game/battle/팀 N과 누락을 기록한다. 숨겨진 gap 기준값 없이 성공 생성 support 하한·실제 r0–30 관측 특징으로 먼저 예측한다. 전체 head/split/frontier/포켓/희생/계보를 두 재구성으로 대조한 뒤, 새 지도·각 팀의 MAE·편향·예측범위 포함률을 기존 가족 제외 점수와 비교한다. 상대 강도별 자기 행동을 분리하고 부류 N을 만든 후 대표 기보 r0–50·r250–499를 읽는다. 재학습은 이 사전 점수를 보존한 뒤 별도 실험으로 한다. unseen replay에는 감춰진 생성 범위가 없어 기존 map-file feature를 채워 넣지 않는다.')
add()
add('## 10. 독립 재계산, 한계, 재현')
add()
vr=[]
for k,a in known:
 for role in ['winner','loser']:
  c=a['cohorts'][role];x=c['raw'];z=c['independentRaw'];cc=c['conversion'];vr.append([k+' '+role,c['N'],f"{x['heads100']} / {z['heads100']} (N={x['checkpointN100']})",f"{x['split50']} / {z['split50']}",f"{x['natural']} / {z['natural']}",f"{x['sacEvents']} / {z['sacEvents']}",f"{cc['full'].get('linePacket300',0)} / {cc['independentFull'].get('linePacket300',0)}",f"{cc['all'].get('pocketNatural',0)} / {cc['independentAll'].get('pocketNatural',0)}"])
table(['지도/역할','팀-판 N','heads r100 1차/독립','split0–49 1차/독립','자연 1차/독립','희생 1차/독립','500완주 왕 드롭 1차/독립','포켓 자연 1차/독립'],vr)
add(f"[사실] 기하 대조 **N={G['N']}판본**, 불일치 **N={len(G['mismatch'])}**. 두 행동 구현의 checkpoint·분열·eligible HR·자연 섭취·희생·계보·ping 불일치 합은 **{T['verification']['independentPerGameMismatch']}**이고 원래 장부 보존 검사는 **{T['verification']['primaryLedgerChecks']}**이다. enrichment의 패킷·포켓·거리 histogram·ping 불일치는 **{T['verification']['enrichment']['independentMismatch']}**이다. 원자료 디코더와 판본 분류/배정표는 공유했으므로 이 부분의 독립성은 주장하지 않는다.")
add()
vf=[]
for y in ['heads25','heads50','heads100','heads250','middle100','splitSpeed50','pocketIntakeShare','sacClockHalfPeak','lineShare300','kingGrowth300_500','kingSafeP10']:
 if y not in F['fits']:continue
 
 for kind in ['leaveFamilyOut','leaveGeometryFamilyOut']:
  v=F['fits'][y][kind];vf.append([y+' '+kind,v['N'],v['familyN'],fmt(v['primaryMAE'],6),fmt(v['independentMAE'],6),fmt(v['primaryBaselineMAE'],6),fmt(v['independentBaselineMAE'],6)])
table(['목표','held-out 예측 N','가족 N','MAE 1차','MAE 독립','상수 MAE 1차','상수 MAE 독립'],vf)
add(f"[사실] [verify_fits.py](../../exp/general/verify_fits.py)는 별도 Fraction 가족 가중치·중앙값/단조/tree 구현으로 선택된 outer-fold 모형을 다시 맞추고, 예측과 MAE/RMSE/baseline을 다시 셌다. 대조 원수는 **{F['checks']}**다. 저장된 선택 모형 ID를 공유했으며 내부 selector 전체를 독립 재선정한 검증은 아니다. 합집합 시야/초기 탐색 입력의 불완전한 공유와 countdown reset 누락은 검증되지 않은 부분으로 남는다.")
add()
add('[사실] 재현 명령과 정의는 [README](../../exp/general/README.md), 동결 키는 [population.json](../../exp/general/population.json), 최종 원수/모형/검증은 [tables.json](../../exp/general/tables.json)에 있다. 추출/enrichment를 동시에 돌리지 않고 각각 최대 2 worker, free memory<10% 또는 disk<21GiB에서 새 배정을 멈췄다. 대형 캐시는 gzip이며 로컬 게임·네트워크·업로드·commit·상대 소스 열람 N=0이다. 새 쓰기는 `exp/general/**`와 이 보고서뿐이다.')
add()
add('[해석] 관측의 한계는 최종 승패 선택, 같은 battle/팀/버전 반복, 종료 길이의 조건부 표본, 정적 거리와 실제 sprint/몸 장애물 차이, 운영상 희생과 실제 의도의 차이다. 지도별 표본은 많아도 일반화 family는 N=10뿐이다. 새 엔진의 head target·탐색·요새 gate·예약 전환·왕 안전이 실제 점수에 미친 효과 및 sprint out-of-sample은 N=0이다. 좋은 oracle 관계를 초반 전역 지식으로 오인하지 않는다.')
add()
add('## 11. feature → rule → numbers → validation score')
add()
add('[해석] 아래 fitted 관계는 전수 학습값을 정확한 block 정의로 표시한 진단표다. `candidate`도 전체 지도 특징 조건이며 신규 실행 N=0; `no-evidence` 행은 정책 채택을 권하지 않는다. 임시 head 기준과 인증 gate는 별도 행이다.')
add()
final=[]
for y in ['heads25','heads50','heads100','heads250','middle100','splitSpeed50','pocketIntakeShare','sacClockHalfPeak','lineShare300','kingGrowth300_500','kingSafeP10']:
 if y not in T['fits']:continue
 f=T['fits'][y];m=f['model'];feat=m.get('feature','여러 특징' if m['kind']=='tree' else '설명되지 않은 지도 차이/상수');a=f['leaveFamilyOut']['score'];r=f['runtimeEarly']['30'];nums=model_text(m);final.append([feat,y,nums,f"LO layout {fmt(f['leaveLayoutOut']['score']['MAE'],3)} / map {fmt(a['MAE'],3)} / geometry {fmt(f['leaveGeometryFamilyOut']['score']['MAE'],3)}; r30 map {fmt(r['leaveFamilyOut']['score']['MAE'],3)}, geometry {fmt(r['leaveGeometryFamilyOut']['score']['MAE'],3)}; N={f['NLayouts']}판본/{a['familyN']}지도/{f['geometryFamiliesN']}기하군; {f['transferStatus']}"])
final += [['조기 특징 규칙 gate 실패 + 현재 UNIT_LIMIT','임시 head 행동 기준','r25/50/100/250 = 7/13/23/38, [H0,UNIT_LIMIT] 제한, r250 도달 조건','반올림 상수 지도 제외 MAE 4.035/7.341/10.456/8.841, N=15판본·10지도; 최적 목표/승률 N=0'],['area + 씨앗 왕 + 국지 cycle/pocket','요새 후보를 검토','area≤1100, 초기 왕≥8, cycle≥L+4; 완전 고립이면 적 전진 0','최적 엔진/승률 검증 N=0; 알려진 지도에서 유도한 설계 gate'],['현재 시야 + reset + 인증 입구','먼저 측정하고 unknown을 유지','정찰자 최대1/시작 지역, ≥4 reset 후보, TTL4; r10/20/30 갱신','기하 경로 N=30좌석, 실제 정책/생성률 정확도 N=0'],['현재 왕 + slot/경로 + 마감 ETA','지역 relay와 최종 급식을 분리','r250/350/400 점검; first drop1–3; 큰 패킷 r460 이전','기존 conversion 관측 N은 원 보고서; 신규 protocol N=0']]
table(['feature','rule','numbers (훈련 전수 모형/설계값)','validation score / N'],final)
(R/'research/observations/general-principles.md').write_text('\n'.join(rows)+'\n')
print('REPORT',len(rows),'lines',len('\n'.join(rows)),'chars')
