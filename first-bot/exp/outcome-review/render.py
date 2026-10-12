#!/usr/bin/env python3
"""Render the Korean census report after stages 1, 2 and 3 pass validation.
SUMMARY.txt is deliberately written only by finish.py after artifact checks.
"""
import collections,json,math,statistics as S
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];C=ROOT/'.cache/outcome-review';E=ROOT/'exp/outcome-review'
A=json.load(open(C/'analysis.json'));M=json.load(open(C/'manifest.json'));K=json.load(open(C/'recount-checks.json'))
G=[json.loads(x) for x in open(C/'games.jsonl') if x.strip()];D=[json.loads(x) for x in open(C/'deep.jsonl') if x.strip()]
bykey={r['key']:r for r in G}
assert not K['mismatchCount'];assert len(D)==len(A['selected']);assert all(not any(d['chk'].values()) for d in D)
def n(x,d=1):return '–' if x is None else f'{x:,.{d}f}'
def pct(x):return '–' if x is None else f'{100*x:.1f}%'
def ci(x,percent=False):return '–' if x[0] is None else f'{pct(x[0]) if percent else n(x[0])}–{pct(x[1]) if percent else n(x[1])}'
def summary(z):return f"{n(z['mean'])} [{ci(z['ci'])}]; {n(z['median'])} ({n(z['q1'])}–{n(z['q3'])}); N={z['n']}"
def mean(z):return f"{n(z['mean'])} [{ci(z['ci'])}], N={z['n']}"
L=[]
def add(x=''):L.append(x)
def table(headers,rows):
    add('');add('| '+' | '.join(headers)+' |');add('| '+' | '.join('---' for _ in headers)+' |')
    for row in rows:add('| '+' | '.join(str(x) for x in row)+' |')
    add('')
def outcome(z):return f"{z['W']}/{z['D']}/{z['L']}"
def final(z):return f"{n(z['ownFinal']['mean'])}/{n(z['enemyFinal']['mean'])}"
def distribution_table(waves,fields):
    for f,label in fields:
        add('### '+label)
        table(['웨이브','우리 평균 [95% CI]; 중앙 (IQR); N','같은 판 상대 평균 [95% CI]; 중앙 (IQR); N'],[(w,summary(A['distributions'][w][f]),summary(A['distributions'][w]['enemy'][f]) if f.startswith('our') else '비율 또는 우리 사건') for w in waves])

add('# 극상위 7팀 결과 검토와 우리 승리의 구조 (2026-10-01)')
add('')
add('- 작성: 로컬 전체 모집단 분석. 원본 파일 수정·네트워크·업로드·커밋·외부 쇼핑 사이트 접근·자격 증명 접근은 0건이다. 새 파일만 지정 경로에 썼다.')
add('- **[사실]**은 원자료 집계, **[해석]**은 연관의 해석이다. 목표 지표는 고정된 top-6 및 DEV 545 상대 전적이다. 레이팅·래더·저레이팅 스크림은 결과 지표에 넣지 않았다.')
add('- 순서: ① 전체 모집단 스크립트 ② 부류와 크기 ③ 사전에 고정한 규칙의 기보 읽기. 규칙은 `exp/outcome-review/METHOD.md`, 입력 스냅숏은 `.cache/outcome-review/manifest.json`이다.')
add('- 자원 실행 조건: '+str(M['resource']))
add('')
add('## 모집단과 정의')
pop=A['population']
table(['묶음','N','승/무/패','우리 전멸','설명'],[
 ['현재 웨이브 top-6',pop['top6']['n'],outcome(pop['top6']),pop['top6']['eliminated'],'14회 실행; 6상대 × 10지도'],
 ['현재 웨이브 DEV 545',pop['dev']['n'],outcome(pop['dev']),pop['dev']['eliminated'],'14회 실행; 1상대 × 10지도'],
 ['현재 웨이브 top-7',pop['waves']['n'],outcome(pop['waves']),pop['waves']['eliminated'],'merge2 3회, stack1–10, stack6 2회'],
 ['과거 9세트',pop['history']['n'],outcome(pop['history']),pop['history']['eliminated'],'요청한 9세트 전부'],
 ['우리 전체',pop['all']['n'],outcome(pop['all']),pop['all']['eliminated'],'서로 다른 게임 ID 전부']])
absent=', '.join(x['wave']+' '+x['set'] for x in M['absent']) or '없음'
add(f'- [사실] 스냅숏 {M["createdAt"]}; 없는 요청 세트: {absent}. 표본 추출은 하지 않았다. 게임 중복 0건; 세트별 70개 지도×상대 셀을 모두 확인했다.')
add('- [사실] 모든 경기는 우리 A석이다. A/B 좌석 효과는 이 자료로 식별할 수 없다. “전멸형”은 지도 분류이며, 실제 종료 이유가 항상 전멸이라는 뜻은 아니다.')
add('- 500라운드형: Autarky, Portals, Schooltime, Slithery Fight, Trauma. 전멸형: Default, Devil, Prisoners Dilemma, Queen Of Spades, Trophy.')
add('- 최종 최장 = 리플레이 `result.team*.longestDragon`; 서버 `scoresA/B`는 사용하지 않는다. 우리/상대가 0마리이면 전멸이다. 무승부는 별도로 센다.')
add('- 머리 = 살아 있는 드래곤 수. r10/50/100/250은 해당 라운드 시작에 도달한 판의 분포다. 이미 끝난 판은 결측이며 도달 N을 명시한다. 원 기계 표에는 종료 상태를 고정한 값과 생존 몫도 있다.')
add('- 자연 진주 비율 = 우리 섭취/같은 판 상대 섭취. 상대 0인 판은 결측. 모델의 로그 비율만 양쪽 +1을 쓴다. 이 변환을 원 비율과 혼동하지 않는다.')
add('- 후기 조각 = r250–499에 분열로 태어난 길이 ≤3 새끼; 부모 stub 제외. 희생 = 턴 시작에 빈 이웃이 있는데 스스로 죽은 장부 sac. 의도적 먹이와 판단 실수는 이 정의만으로 구분되지 않는다.')
add('- 왕(현재 최장)과 최종 왕의 계보는 다르다. L300·왕에게 간 희생 진주는 최종 왕 계보 기준, 해당 계보가 살아 있고 r300에 도달한 N만 쓴다. 최종 왕 0은 전멸 판을 포함한다.')
add('- 노출 = r300–499 최종 왕 계보의 길이 ≥8 턴 중 적 머리가 토러스 맨해튼 6 이내인 몫. 해초·포털은 무시하므로 Portals 해석에 주의한다. 턴 0인 판은 결측.')
add('- Wilson 95% 구간은 승·무·패·전멸·최종 길이 우세 같은 이항 몫에 쓴다. 길이에 Wilson 구간을 붙이면 통계적으로 부적절하므로 평균 t 구간, 중앙값/IQR을 쓴다. 관측 모집단 값은 확정치이고, 구간은 같은 조건의 새 씨앗 경기 불확실성을 가정한다.')
add('')
add('## 1. 웨이브 결과 장부')
table(['웨이브','집단','N','승/무/패','승률 Wilson 95%','우리 전멸 [95%]','상대 전멸','끝 최장 우리/상대'],[(w,g,z['n'],outcome(z),f"{pct(z['W']/z['n'])} [{ci(z['winCI'],True)}]",f"{z['eliminated']} [{ci(z['elimCI'],True)}]",z['opponentEliminated'],final(z)) for w in A['waveNames'] for g,z in A['waveLedger'][w].items()])
add('[사실] 최종 길이와 우세 몫의 구간은 아래 표다. 전멸 판도 최종 길이 0으로 포함했다.')
table(['웨이브','집단','N','우리 끝 최장 평균 [95%]','상대 평균 [95%]','최종 길이 우세 수 [Wilson 95%]'],[(w,g,z['n'],mean(z['ownFinal']),mean(z['enemyFinal']),f"{z['dominance']} [{ci(z['dominanceCI'],True)}]") for w in A['waveNames'] for g,z in A['waveLedger'][w].items()])
add('### 지도별·상대별 합계')
table(['지도','집단','N','승/무/패','승률 [95%]','우리/상대 전멸','끝 최장 우리/상대'],[(m,g,z['n'],outcome(z),f"{pct(z['W']/z['n'])} [{ci(z['winCI'],True)}]",f"{z['eliminated']}/{z['opponentEliminated']}",final(z)) for m,a in A['byMap']['waves'].items() for g,z in a.items()])
table(['상대','N','승/무/패','승률 [95%]','우리/상대 전멸','끝 최장 우리/상대'],[(o,z['n'],outcome(z),f"{pct(z['W']/z['n'])} [{ci(z['winCI'],True)}]",f"{z['eliminated']}/{z['opponentEliminated']}",final(z)) for o,z in A['byOpponent']['waves'].items()])
add('### 과거 세트 (현재 추세와 분리)')
table(['세트','집단','N','승/무/패','승률 [95%]','우리 전멸','끝 최장 우리/상대'],[(s,g,z['n'],outcome(z),f"{pct(z['W']/z['n'])} [{ci(z['winCI'],True)}]",z['eliminated'],final(z)) for s,a in A['historySets'].items() for g,z in a.items()])

add('## 2. 반복 웨이브 잡음과 추세')
power=A['power']
table(['같은 봇','top-6 N','각 회 승수/60','합계 승수','승률 Wilson 95%','회별 승수 표준편차'],[(b,z['N'],', '.join(map(str,z['winCounts'])),z['wins'],ci(z['winCI'],True),n(z['winCountSD'],2)) for b,z in power['replicates'].items()])
add(f"[사실] 같은 봇 반복의 Pearson 분산비 φ={n(power['dispersion'],3)}, 95% 구간 {ci(power['dispersionCI'])}, 잔여 자유도 {power['residualDF']}다. 반복이 5회뿐이라 분산의 상한은 매우 불확실하다. 검출력 계산은 이항 분산 1을 하한으로 유지한다.")
for label,key in [('top-6 승리','top6-logistic'),('top-6 전멸','elimination-logistic')]:
 z=A['trend'][key]
 if z.get('coefficients'):
  q=z['coefficients'][0];add(f"[사실] 지도×상대 고정 절편, 웨이브당 {label} OR={n(q['OR'],3)} [{n(q['ORCI'][0],3)}–{n(q['ORCI'][1],3)}], 후보 N={z['candidateN']}, 분석 가능 N={z['completeN']}, 결과 변동 층 N={z['informativeN']}, 웨이브 군집 {z['clusters']}, 수렴={z['converged']}.")
 else:add('[사실] 추세 모형 식별 불가: '+str(z))
add('[해석] 웨이브는 무작위 처치가 아니다. 상대 코드 변경, 씨앗, 시각과 우리 코드가 함께 바뀐다. 승리 추세의 구간이 1을 포함하면 “개선 없음”이 증명된 것이 아니라 이 자료에서 검출되지 않은 것이다.')
add('### 초기 merge2와 최신 stack8–10의 지표 변화')
table(['지표','초기 평균 [95%], N','최신 평균 [95%], N','최신−초기 [95%]'],[(f,mean(z['merge2']),mean(z['latestStack8to10']),f"{n(z['difference'])} [{ci(z['differenceCI'])}]") for f,z in A['trend'].items() if f in A['distributions'][A['waveNames'][0]] and isinstance(z,dict) and 'merge2' in z])
add('[사실] 이 변화 구간은 전체 경기의 Welch 근사 구간이며 탐색적 비교다. 지도·상대 균형은 같지만 계보·노출·전멸 라운드의 N은 조건부 모집단이므로 변화에 생존 구성도 반영된다. 복수 비교 확증 판정으로 쓰지 않는다.')

add('## 3. 경기별 선행·후기 지표 분포')
add('각 칸은 평균 [95% t 구간]; 중앙 (25–75%); N이다. top-6/DEV 분리 분포도 `analysis.json`의 `distributions.*.byGroup`에 전부 있다.')
distribution_table(A['waveNames'],[(f,f) for f in ['ourHeads10','ourHeads50','ourHeads100','ourHeads250','naturalRatio','ourFinal','ourLineage300','ourSacrifices','ourLineSac300','ourLineSacAll','ourLatePieces','ourExposure','eliminationRound']])
add('### 라운드 도달과 생존 구성')
table(['웨이브','전체 N','r100 도달 N','r250 도달 N','r300 도달 N','r400 도달 N'],[(w,len([r for r in G if r['wave']==w]),*[A['distributions'][w]['alive'][str(t)]['reached'] for t in [100,250,300,400]]) for w in A['waveNames']])

add('## 4. 어떤 경기 특징이 승리와 연관되는가')
add('[사실] 지도×상대의 서로 다른 절편을 둔 로지스틱 회귀다. 한 층에서 전승/전패면 절편이 무한대로 가므로 기울기에 정보가 없는 그 층을 프로파일 가능도에서 제외한다. 해당 N과 층 수를 보고하며, 원 결과 표에서는 한 판도 빼지 않는다. 구간은 세트(웨이브) 군집 점수의 sandwich 분산과 군집 자유도 t 값이다. 순수 예측 모델은 r100까지, 랜드마크 모델은 r300 도달 판의 r300까지 자료만 쓴다.')
table(['모형','후보 N','완전값 N','결과 변동 층 N/층','군집','수렴','변수'],[(name,z['candidateN'],z['completeN'],f"{z['informativeN']}/{z['strata']}",z.get('clusters','–'),z.get('converged',z.get('error','–')),', '.join(z['fields'])) for name,z in A['models'].items() if not name.startswith('single-adjusted:')])
add('로그 머리/섭취/희생/조각 비율의 OR는 +1 보정 비율의 e배당이다. 2배당 OR는 OR^ln(2)다. currentKingDifference300·lineageDifference300은 상대 대비 +5길이, lineSacDifference는 +10진주, exposureDifference는 상대 대비 +20%p다.')
table(['모형','변수','OR [군집 95%]'],[(name,q['feature'],f"{n(q['OR'],3)} [{n(q['ORCI'][0],3)}–{n(q['ORCI'][1],3)}]") for name,z in A['models'].items() for q in z.get('coefficients',[])])
add('[해석] 후기 모형은 승리를 미리 맞히는 모형이 아니다. 최종 왕 계보는 경기 종료 뒤에만 알 수 있고 전멸 결과에 따라 결측이 생긴다. 이 모형의 효과를 처치의 인과 효과나 새 봇의 기대 승수로 바꾸지 않는다. 최종 길이·전멸 라운드는 결과를 직접 인코딩하므로 설명 표에만 있다.')
add('### 원 지표의 층별 승률')
for f in ['ourHeads10','ourHeads50','ourHeads100','ourHeads250','naturalRatio','ourFinal','ourLineage300','ourSacrifices','ourLineSac300','ourLatePieces','ourExposure','eliminationRound']:
 table([f+' 구간','집단','N','승/무/패','승률 Wilson 95%'],[(str(z['range']),z['population'],z['n'],outcome(z),ci(z['winCI'],True)) for z in A['stratified'][f] if z['population'] in ['waves-top7','waves-top6']])
add('지도×상대×각 구간의 모든 비어 있지 않은 셀은 `analysis.json`의 `stratified.*-map-opponent`에 있다. 작은 셀의 넓은 구간을 유지했다.')
add('### 지도 배치')
table(['지도','배치 (폭×높이 / 해초 edge / 포털쌍 / 시작 A머리)','웨이브 N','승/무/패'],[(m,'; '.join(f"{z['width']}×{z['height']} / {z['kelpEdges']} / {z['portalPairs']} / {z['initialHeadsA']}" for z in a['layouts']),a['waves']['n'],outcome(a['waves'])) for m,a in A['mapLayout'].items()])
add('[사실] 배치의 주효과는 지도 고정 효과와 공선이므로 별도로 식별되지 않는다. 포털 유무×r100 머리 비율 상호작용만 감도 분석에서 추정했다. 특정 배치가 승리를 유발한다고 주장하지 않는다.')

add('## 5. 우리 승리의 해부: 전체 부류와 같은 셀의 패배')
add('우선순위: 상대 전멸 → 상대가 살아 있지만 r300 뒤 길이 ≥8인 현재 왕을 잃음 → 최종 길이 경주 승리. “왕 손실”은 후속 왕으로 회복했더라도 사건이 있으면 해당한다. “out-grown”에는 상대의 낮은 성장과 우리 전환이 함께 들어갈 수 있다.')
table(['부류','전체 N','현재/과거 N','지도별 N','상대별 N','같은 지도·상대 패배 N'],[(k,z['n'],f"{z['wavesN']}/{z['historyN']}",str(z['mapCounts']),str(z['opponentCounts']),z['sameCellsLossN']) for k,z in A['classes'].items() if k.startswith('win:')])
for k,z in A['classes'].items():
 if not k.startswith('win:'):continue
 add('### '+k)
 table(['지표','승리 평균 [95%], N','같은 셀 패배 평균 [95%], N','승리−각 셀 패배 평균 [95%], N'],[(f,mean(z['indicators'][f]),mean(z['sameCellsLossIndicators'][f]),mean(z['matchedWinMinusLoss'][f])) for f in ['ourHeads100','ourHeads250','naturalRatio','ourFinal','ourLineage300','ourSacrifices','ourLineSac300','ourLatePieces','ourExposure']])
add('### 관측 가능한 상대 실패 신호')
signal=[]
for era in ['waves','history']:
 for oc in ['W','L']:
  rr=[r for r in G if r['era']==era and r['outcome']==oc];nn=len(rr)
  for label,fun in [('왕≥8 빈 이웃 자해',lambda r:any(x['cause']=='sac' for x in r['theirRawKingDeaths'])),('왕≥8 적 머리 접촉',lambda r:any(x['cause'] in ['ram','rammed'] for x in r['theirRawKingDeaths'])),('상대 timeout',lambda r:r['theirFaults']>0)]:
   c=sum(fun(r) for r in rr);signal.append([era,oc,label,nn,c,ci(__import__('analyse').wilson(c,nn),True)])
# Avoid importing analyse.py's execution path; use a local Wilson expression below.
