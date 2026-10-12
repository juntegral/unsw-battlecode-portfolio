#!/usr/bin/env python3
"""Render all eight questions to a new draft; publishing and marker are separate."""
import collections,json,math,re,statistics as S,subprocess
from pathlib import Path
from case_notes import NOTES
R=Path(__file__).resolve().parents[2];C=R/'.cache/outcome-review';E=R/'exp/outcome-review'
def read(p):return json.load(open(C/p))
A=read('analysis.json');M=read('manifest.json');X=read('extensions.json');F=read('final-supplement.json')
K=read('recount-checks-v2.json');EX=read('extra-checks.json');CC=read('corrected-cause-checks.json');CA=read('class-audit.json');TA=read('terminal-audit.json')
G=list(map(json.loads,open(C/'games.jsonl')));D=list(map(json.loads,open(C/'deep.jsonl')));SEL=read('selection-v2.json')
models={**A['models'],**read('models-elite.json'),**read('models-extra.json')}
assert M['n']==len(G)==1680 and len(D)==len(SEL['games'])==41
assert set(NOTES)=={d['key'] for d in D}
assert not any([K['mismatchCount'],EX['mismatchCount'],CC['correctedMismatchCount'],CA['mismatchCount'],TA['rawTieMismatches'],TA['ruleMismatchCount']])
assert all(not any(d['chk'].values()) for d in D)
mem=subprocess.check_output(['/usr/bin/memory_pressure'],text=True)
assert int(re.search(r'System-wide memory free percentage:\s*(\d+)%',mem)[1])>=10
assert int(subprocess.check_output(['/bin/df','-g','/'],text=True).splitlines()[-1].split()[3])>=20
def n(x,d=1):return '–' if x is None else f'{x:,.{d}f}'
def pct(x):return '–' if x is None else f'{100*x:.1f}%'
def ci(x,pc=False):return '–' if x[0] is None else (' ～ '.join(pct(v) if pc else n(v) for v in x))
def tcrit(df):
 t=[0,12.706,4.303,3.182,2.776,2.571,2.447,2.365,2.306,2.262,2.228,2.201,2.179,2.160,2.145,2.131,2.120,2.110,2.101,2.093,2.086,2.080,2.074,2.069,2.064,2.060,2.056,2.052,2.048,2.045,2.042]
 return t[df] if df<=30 else 1.95996398454+(1.95996398454**3+1.95996398454)/(4*df)
def dist(xs):
 a=sorted(x for x in xs if x is not None and math.isfinite(x));nn=len(a)
 if not nn:return {'n':0,'mean':None,'ci':[None,None],'median':None,'q1':None,'q3':None}
 def q(p):
  x=(nn-1)*p;i=int(x);return a[i]+(a[min(i+1,nn-1)]-a[i])*(x-i)
 m=S.mean(a);h=tcrit(nn-1)*S.stdev(a)/math.sqrt(nn) if nn>1 else None
 return {'n':nn,'mean':m,'ci':[m-h,m+h] if h is not None else [None,None],'median':q(.5),'q1':q(.25),'q3':q(.75)}
def wilson(k,nn):
 if not nn:return [None,None]
 z=1.95996398454;p=k/nn;dv=1+z*z/nn;c=(p+z*z/(2*nn))/dv;h=z*math.sqrt(p*(1-p)/nn+z*z/(4*nn*nn))/dv
 return [max(0,c-h),min(1,c+h)]
def mean(z):return f"{n(z['mean'])} [{ci(z['ci'])}]; N={z['n']}"
def distribution(z):return mean(z)+f"; 중앙 {n(z['median'])} ({n(z['q1'])} ～ {n(z['q3'])})"
def wl(z):return f"{z['W']}/{z['D']}/{z['L']}"
def rate(k,nn):return f"{k}/{nn}, {pct(k/nn) if nn else '–'} [{ci(wilson(k,nn),True)}]"
def fin(z):return f"{n(z['ownFinal']['mean'])} [{ci(z['ownFinal']['ci'])}] / {n(z['enemyFinal']['mean'])} [{ci(z['enemyFinal']['ci'])}]"
def ledger(rr):
 co=collections.Counter(g['outcome'] for g in rr);nn=len(rr)
 return {'n':nn,**{k:co[k] for k in ['W','D','L']},'eliminated':sum(g['ourEliminated'] for g in rr),'opponentEliminated':sum(g['theirEliminated'] for g in rr),'dominance':sum(g['ourFinal']>g['theirFinal'] for g in rr),'ownFinal':dist(g['ourFinal'] for g in rr),'enemyFinal':dist(g['theirFinal'] for g in rr)}
def fmt_counts(d):return ', '.join(f'{k}: {v}' for k,v in d.items()) or '없음'
P=A['population'];B={g['key']:g for g in G};waves=[g for g in G if g['era']=='waves']
LABELS={'ourHeads10':'r10 머리','ourHeads50':'r50 머리','ourHeads100':'r100 머리','ourHeads250':'r250 머리','naturalRatio':'자연 진주 섭취 비율','ourFinal':'끝 최장','ourLineage300':'최종 왕 계보 L300','ourSacrifices':'경기 전체 희생 횟수','ourLineSac300':'r300 뒤 왕 계보 희생 진주','ourLineSacAll':'전체 생애 왕 계보 희생 진주','ourLatePieces':'r250 뒤 길이 ≤3 조각 출생','ourExposure':'r300 뒤 왕 계보 적 머리 노출','eliminationRound':'우리 전멸 라운드'}
L=[]
def add(s=''):L.append(s)
def table(headers,rows):
 add();add('| '+' | '.join(headers)+' |');add('| '+' | '.join('---' for h in headers)+' |')
 for row in rows:add('| '+' | '.join(str(v).replace('\n',' ') for v in row)+' |')
 add()
def outcome_table(rows,headers):
 table(headers+['N','승/무/패','승률 [Wilson 95%]','우리/상대 전멸','끝 최장 평균 [t 95%], 우리/상대','최장 우세 [Wilson 95%]'],[list(pre)+[z['n'],wl(z),rate(z['W'],z['n']),f"{z['eliminated']}/{z['opponentEliminated']}",fin(z),rate(z['dominance'],z['n'])] for pre,z in rows])
add('# 극상위 7팀 결과 검토와 우리 승리의 구조 (2026-10-01)')
add()
add('- 작성: team 583의 로컬 전수 분석. 기존 파일 수정·네트워크·업로드·커밋·외부 사이트·자격 증명 접근은 0건이다. 새 파일만 지정한 출력 경로에 만들었다.')
add('- 목표: 매 웨이브의 고정 top-6 상대 결과와 DEV 545 결과를 따로 판단한다. 레이팅·래더·저레이팅 스크림은 승률 분모와 개선 지표에 넣지 않았다.')
add('- 표기: **[사실]**은 원자료와 스크립트 수치, **[해석]**은 추론이다. 별도 표시가 없으면 판당 팀 지표, 구간은 95%다.')
add('- 세 단계: ① 전체 모집단 계산과 독립 재계산 ② 부류와 크기 확정 ③ 읽기 전에 고정한 ID 규칙으로 기보 깊이 읽기. `METHOD.md`, `METHOD-APPENDIX.md`, `METHOD-CURRENT-CASES.md`를 순서대로 적용했다.')
add('- 실행: 조정자 승인에 따라 nice를 호출하지 않고 워커 1개로 진행했다. 조정자가 알린 부모 niceness는 10, 이번 실행 자식에서 관측한 값은 0이었다. 메모리 여유 10% 미만·루트 디스크 여유 20 GiB 미만이면 중단하는 감시를 유지했다. 관측값과 승인 조건의 차이를 숨기지 않았다.')
add('## 모집단·정의·핵심 답')
table(['묶음','N','승/무/패','우리/상대 전멸','승률 Wilson 95%'],[[name,z['n'],wl(z),f"{z['eliminated']}/{z['opponentEliminated']}",rate(z['W'],z['n'])] for name,z in [('현재 top-6',P['top6']),('현재 DEV 545',P['dev']),('현재 top-7',P['waves']),('과거 9세트',P['history']),('우리 전체',P['all'])]])
add(f"- [사실] 입력 스냅숏 {M['createdAt']}. 24세트·1,680개 서로 다른 게임 ID 전부다. W0–W12는 15회 실제 실행·1,050판이다(W0 3회, 나머지 각 1회). stack6은 W6/W7의 동일 봇 반복이다. W12 stack11도 70판 전부 포함했다. 없는 요청 세트: {', '.join(s['set'] for s in M['absent']) or '없음'}.")
add('- [사실] 각 세트의 7상대×10지도 셀은 정확히 한 판씩이다. 모두 우리 A석이므로 좌석 효과는 식별되지 않는다. 요청한 과거 9세트 630판을 역사 비교에 썼으며 `r1-online`, `r1-autoscrim`, `g1`, `g2`를 제외했다.')
table(['웨이브/역사','세트','봇','N'],[[s['wave'],s['set'],s['bot'],s['n']] for s in M['sets']])
table(['집단','상대 ID와 이름'],[['top-6','306 Cutlery; 70 cheji bt; 20 calc; 801 中国必须人能飞😡; 264 forgot to mention; 46 Sabotage-d'],['DEV','545 dev test 1 :P']])
add('- 500라운드형 = Autarky, Portals, Schooltime, Slithery Fight, Trauma. 전멸형 = Default, Devil, Prisoners Dilemma, Queen Of Spades, Trophy. 지도형과 실제 종료 이유는 다르다.')
add('- 결과 W/D/L은 공식 `result.winner`다. 첫 점수는 `result.team*.longestDragon`이다. 0마리 팀은 즉시 패배하며, 500라운드 최장 동률은 `totalLength`로 해소한다(로컬 `rules/structure.md`). 서버 `scoresA/B`는 총길이이므로 최장 지표로 쓰지 않았다. 전체 최장 동률 10판은 9패·1무, 전수 종료 규칙 불일치 0이다.')
add('- 머리 = 살아 있는 드래곤 수. r10/50/100/250은 해당 라운드 시작에 도달한 판만의 분포다. 끝난 판을 생존 머리 0으로 섞지 않았다. 도달 N·전멸률을 함께 제시하며, 종료 상태를 고정한 별도 궤적은 캐시에 남겼다.')
add('- 자연 섭취 비율 = 우리 자연 진주/동일 판 상대 자연 진주. 상대 0은 결측이다. 로그 모형만 양쪽 +1 보정 비율을 쓴다. 경기 비율의 평균과 합계 비율은 다른 수다.')
add('- 희생 = 턴 시작에 빈 이웃이 있는데 스스로 죽은 장부 `sac`. 의도적 먹이와 실수를 이 정의만으로 구분할 수 없다. 후기 조각 = r250–499의 분열 새끼 길이 ≤3; 부모 stub은 제외한다.')
add('- 현재 왕 = 현재 최장(동률은 작은 ID). 최종 왕 계보는 최종 왕의 부모·자식 경로를 시간순으로 잇되, 자식으로 넘긴 뒤 부모가 먹은 진주는 세지 않는다. L300은 그 최종 계보 조상의 r300 길이이며 현재 왕 길이와 다를 수 있다. 최종 왕 0은 전멸 판도 포함한다.')
add('- 왕 계보 희생 공급은 r300–499 및 전체 생애를 각각 센다. 적 머리 노출은 r300–499에 계보 길이 ≥8인 턴 중 토러스 맨해튼 6 안에 적 머리가 있는 몫이다. 해초·포털을 무시하고, 자격 턴 0인 판은 결측으로 둔다. r300 예측 감도 모형은 별도로 r200–299의 당시 현재 왕 노출만 쓴다.')
add('- Wilson은 승·무·패·전멸·최장 우세 같은 이항 비율에 쓴다. 연속 길이에 Wilson을 적용할 수 없어 평균 t 구간과 중앙값/IQR을 제시한다. 모집단 집계값 자체는 확정치다. 구간은 같은 구성의 새 씨앗 반복 불확실성을 가정하며, 단순 평균 구간은 경기 독립 가정, 회귀는 웨이브 군집 구간이다.')
add('[사실] 현재 top-6 승률은 81/900 = 9.0% [7.3% ～ 11.0%]이다. DEV는 28/150 = 18.7% [13.2% ～ 25.7%]다. 머리·섭취·희생 공급은 웨이브를 거치며 증가했고 전멸은 감소했지만, 최종 왕 길이와 top-6 승리 추세의 증가를 검출하지 못했다.')
add('[해석] 지금 자료에서 강한 승리 연관은 r300 현재 왕의 상대 대비 길이와 최종 계보의 후기 희생 공급이다. 머리·조각의 증가를 그 자체로 승리 개선이라 판단할 근거는 부족하다. 후기 지표의 연관은 종료 뒤 계보를 쓰므로 인과 효과가 아니다.')

add('## 1. 웨이브 결과 장부·반복 잡음·추세')
outcome_table([([w,g],z) for w in A['waveNames'] for g,z in A['waveLedger'][w].items()],['웨이브','집단'])
add('전멸의 구간은 다음 표다. 지도형·지도·상대의 모든 웨이브 셀은 부록 A–C에 있으며, 각 셀의 무·패·전멸 구간도 `analysis.json`에 보존했다.')
table(['웨이브','집단','우리 전멸 [Wilson 95%]','상대 전멸 [Wilson 95%]'],[[w,g,rate(z['eliminated'],z['n']),rate(z['opponentEliminated'],z['n'])] for w in A['waveNames'] for g,z in A['waveLedger'][w].items()])
add('### 지도형·지도·상대의 현재 합계')
outcome_table([([gr,fa],ledger([g for g in waves if (g['opponent']!=545)==(gr=='top6') and g['family']==fa])) for gr in ['top6','DEV'] for fa in ['r500','elim']],['집단','지도형'])
outcome_table([([m,gr],z) for m,gs in A['byMap']['waves'].items() for gr,z in gs.items()],['지도','집단'])
outcome_table([([op],z) for op,z in A['byOpponent']['waves'].items()],['상대'])
add('### 과거 세트 결과')
outcome_table([([s,gr],z) for s,gs in A['historySets'].items() for gr,z in gs.items()],['세트','집단'])
add('### 동일 봇 반복을 합친 잡음')
pw=A['power']
table(['봇','실제 실행','top-6 N','회별 승/60','합계 승률 [Wilson 95%]','회별 승수 SD'],[[b,', '.join(z['waves']),z['N'],', '.join(map(str,z['winCounts'])),rate(z['wins'],z['N']),n(z['winCountSD'],3)] for b,z in pw['replicates'].items()])
table(['봇','반복 쌍','지도×상대 셀 N','승리 여부가 달라진 셀'],[[b,' / '.join(q['pair']),q['n'],q['discordant']] for b,z in pw['replicates'].items() for q in z['discordantPairs']])
add(f"[사실] 반복 5회에서 Pearson 분산비 φ={n(pw['dispersion'],3)} [근사 χ² 95% {n(pw['dispersionCI'][0],3)} ～ {n(pw['dispersionCI'][1],3)}], 잔여 자유도 3이다. 독립 결과 전용 스크립트도 φ={n(CA['powerIndependentDispersion'],3)}이며 검출력 표 전체가 같다.")
table(['추세','후보/완전값 N','결과 변동 층 N/층','웨이브 군집 N','웨이브당 OR [군집 95%]','수렴'],[[name,f"{z['candidateN']}/{z['completeN']}",f"{z['informativeN']}/{z['strata']}",z['clusters'],f"{n(z['coefficients'][0]['OR'],3)} [{n(z['coefficients'][0]['ORCI'][0],3)} ～ {n(z['coefficients'][0]['ORCI'][1],3)}]",z['converged']] for name,z in [('top-6 승리',A['trend']['top6-logistic']),('top-6 전멸',A['trend']['elimination-logistic'])]])
add('[사실] 추세는 지도×상대×초기 머리 수별 절편을 보정한다. 승리 OR 0.993 [0.934 ～ 1.055]의 구간은 1을 포함하고, 전멸 OR 0.748 [0.674 ～ 0.830]은 감소 방향이다.')
add('[해석] 상대 코드·시각·씨앗·우리 코드가 같이 바뀌므로 웨이브는 무작위 처치가 아니다. 반복 5회로 작은 잡음을 정밀하게 추정할 수 없다. φ가 1보다 작아도 검출력에서 이항 분산 1을 하한으로 유지한다. 승리 증가를 검출하지 못했다는 결과가 모든 작은 개선을 배제하는 것은 아니다.')

add('## 2. 선행·후기 지표: 웨이브별 경기 분포와 움직임')
add('각 분포는 평균 [95% t 구간]; N; 중앙값 (25–75%)다. top-6와 DEV를 전부 분리했다. 머리와 L300·노출은 도달/계보 조건부 N, 전체 희생·자연 섭취·후기 출생·끝 최장은 종료가 빠른 판도 포함한다.')
for f,label in LABELS.items():
 add('### '+label)
 rows=[]
 for w in A['waveNames']:
  for gr in ['top6','DEV']:
   rr=[g for g in G if g['wave']==w and (g['opponent']!=545)==(gr=='top6')]
   z=A['distributions'][w]['byGroup'][gr][f]
   en=distribution(dist(g.get(f.replace('our','their')) for g in rr)) if f.startswith('our') else '우리/상대 비율' if f=='naturalRatio' else '우리 전멸 판만'
   rows.append([w,gr,distribution(z),en])
 table(['웨이브','집단','우리 분포','같은 판 상대 분포'],rows)
add('### 라운드 도달 N')
table(['웨이브','전체 N','r100','r250','r300','r400'],[[w,70,*[A['distributions'][w]['alive'][str(t)]['reached'] for t in [100,250,300,400]]] for w in A['waveNames']])
add('### 어느 지표가 움직였나')
table(['지표','15회 웨이브 평균의 기울기/웨이브 [95%]','경기값 N','BH q (13항)'],[[LABELS[f],f"{n(z['slopePerWave'],4)} [{n(z['slopeCI'][0],4)} ～ {n(z['slopeCI'][1],4)}]",z['gameN'],n(z['BHq'],6)] for f,z in X['featureWaveTrends'].items()])
add('[사실] r100 머리는 웨이브당 +0.619 [0.376 ～ 0.863], 후기 조각 +0.707 [0.522 ～ 0.891], 계보 희생(r300+) +0.471 [0.401 ～ 0.542]이다. 최종 왕 계보 L300은 −1.033 [−1.370 ～ −0.696]이다. 끝 최장 +0.016 [−0.109 ～ 0.141], 왕 노출 +0.00029 [−0.00324 ～ 0.00381]은 움직임을 검출하지 못했다.')
add('[해석] 초기 왕에 남긴 길이는 줄고 후기 공급은 늘었으나 최종 단일 왕 길이의 증가로 이어졌다고 확인할 수 없다. 전멸 판의 구성과 조건부 계보 N도 달라진다. OLS는 15회 실행의 평균을 같은 가중치로 회귀했고, W0의 세 번은 순서값 0을 공유한다. BH는 이 13개 탐색 비교만 조정한다.')
add('### 초기 merge2 210판과 최신 stack8–11 280판')
table(['지표','초기 평균 [95%], N','최신 평균 [95%], N','최신−초기 [95%]'],[[LABELS[f],mean(z['merge2']),mean(z['latestStack8to11']),f"{n(z['difference'])} [{ci(z['differenceCI'])}]"] for f,z in A['trend'].items() if f in LABELS and isinstance(z,dict) and 'merge2' in z])
add('[사실] 이 끝점 비교는 경기 단위 Welch 근사 구간이다. 지도×상대 구성은 같지만 무작위 버전 비교가 아니며, 조건부 지표의 N 차이를 유지했다.')

add('## 3. 어떤 경기 특징이 극상위권 승리와 연관되는가')
add('[사실] 단순 로지스틱 모형은 지도×상대×초기 머리 수 층마다 별도 절편을 프로파일한다. Prisoners Dilemma의 초기 3/5머리 판본을 구분한다. 한 층의 결과가 전승/전패면 유한 절편이 없고 기울기에 정보가 없으므로 결과 변동 층만 회귀에 정보를 준다. 그 판들을 결과 장부에서는 빼지 않았다. 무승부 1판은 이항 회귀에서 제외하고, 결측 N은 모형 표에 드러낸다.')
add('[사실] 회귀 구간은 세트/웨이브 군집 sandwich 분산과 군집 자유도 t 값이다. 현재 모형 군집 15개(df14), 과거 포함 모형 24개(df23)다. 앞 모델은 r100까지, 랜드마크는 r300 도달 판의 r300까지 지표만 쓴다. 후기 모형의 최종 계보 지표는 종료 뒤에야 알 수 있다. 홀드아웃 성능이나 인과 효과로 검증한 모형은 아니다.')
major=['early-waves-top6','early-waves-top7','early-all-top7','landmark300-top6','landmark300-top7','landmark300-exposure','late-retrospective-top6','late-retrospective-top7','layout-interaction','layout-kelp-interaction']
table(['모형','후보/완전값 N','무 제외','결과 변동 층 N/층','군집 N','수렴/제약'],[[name,f"{z['candidateN']}/{z['completeN']}",z['drawExcluded'],f"{z['informativeN']}/{z['strata']}",z.get('clusters','–'),z.get('converged',z.get('error'))] for name in major for z in [models[name]]])
table(['모형','지표','OR [군집 95%]'],[[name,q['feature'],f"{n(q['OR'],3)} [{n(q['ORCI'][0],3)} ～ {n(q['ORCI'][1],3)}]"] for name in major for q in models[name].get('coefficients',[])])
add('로그 머리/섭취/희생/조각 OR는 양쪽 +1 보정 비율의 e배당이다. currentKingDifference300·lineageDifference300은 상대 대비 +5길이, lineSacDifference는 +10진주, exposureDifference는 상대 대비 +20%p다. kelp 상호작용은 해초 edge 비율 +10%p당 머리 로그비의 OR 배수다.')
add('[사실] top-6 랜드마크의 r300 현재 왕 +5길이 OR는 2.292 [1.504 ～ 3.491], 정보 N276이다. top-6 후기 다변량 모형에서 계보 희생 격차 +10개 OR는 6.462 [2.720 ～ 15.353], 정보 N263이다. 이 모형의 후기 조각 로그비 OR는 0.276 [0.110 ～ 0.694]로 음의 연관이며, 머리·자연·총 희생·노출의 구간은 넓다.')
add('[해석] 여러 머리 시점은 서로 상관되어 초기 다변량 계수가 불안정하다. 후기 희생 공급은 최종 왕의 정체와 생존을 조건으로 하므로 강한 연관이 있어도 처치 효과로 바꾸면 안 된다. 후기 출생이 많은 판에서 덜 이겼다는 결과는 분열을 줄이면 이긴다는 결론도 아니다. 분열이 생존·영토·공급·왕 유지와 함께 변한다.')
add('### 같은 정의의 단변수 보정 연관: top-6와 DEV 포함을 나란히')
top7={z['feature']:z for z in X['leverScaledOR']}
lever_labels={'headLogRatio100':'r100 머리 (+1 비율) 2배','fullLogNaturalRatio':'전체 자연 섭취 (+1 비율) 2배','currentKingDifference300':'r300 현재 왕 상대 대비 +5길이','lineSacDifference':'최종 계보 후기 희생 상대 대비 +10개','birthLogRatio':'후기 조각 (+1 비율) 2배','exposureDifference':'최종 계보 상대 대비 노출 −20%p'}
table(['지표','top-6 OR [95%]; 정보/완전값 N','top-7 OR [95%]; 정보/완전값 N'],[[lever_labels[z['feature']],f"{n(z['OR'],3)} [{n(z['CI'][0],3)} ～ {n(z['CI'][1],3)}]; {z['N']}/{z['completeN']}",f"{n(top7[z['feature']]['OR'],3)} [{n(top7[z['feature']]['CI'][0],3)} ～ {n(top7[z['feature']]['CI'][1],3)}]; {top7[z['feature']]['N']}/{top7[z['feature']]['completeN']}"] for z in F['eliteScaledOR']])
add('[사실] top-6 자연 섭취의 단변수 OR 1.605 [0.781 ～ 3.299]는 1을 포함한다. DEV 포함 top-7의 2.076 [1.121 ～ 3.846]만 보고 elite top-6에서 확정된 효과라고 말하지 않는다. 모든 단변수의 원 e배 계수와 N은 부록 D에 있다.')
add('### 원 지표별 전수 구간 표')
for f in A['stratified']:
 if f.endswith('-map-opponent'):continue
 table([LABELS[f]+' 구간 [하한,상한)','모집단','N','승/무/패','승률 [Wilson 95%]'],[[str(z['range']).replace('None','∞'),z['population'],z['n'],wl(z),rate(z['W'],z['n'])] for z in A['stratified'][f] if z['population'] in ['waves-top6','waves-top7']])
add('[사실] 최종 길이·전멸 라운드 표는 결과 설명용이며 예측 공변량에서 제외했다. 모든 비어 있지 않은 지도×상대×지표 구간 셀을 `analysis.json`의 `stratified.*-map-opponent`에 남겼다. 부록 E는 왕 계보 희생의 그 층별 표 전부다.')
add('### 지도 배치와 식별 한계')
table(['지도','배치 (폭×높이; 해초 edge/전체; 포털쌍; 초기 A/B 머리)','현재 N','승/무/패'],[[m,'; '.join(f"{q['width']}×{q['height']}; {q['kelpEdges']}/{q['edgeCount']}; {q['portalPairs']}; {q['initialHeadsA']}/{q['initialHeadsB']}" for q in z['layouts']),z['waves']['n'],wl(z['waves'])] for m,z in A['mapLayout'].items()])
add('[사실] 지도 배치의 주효과는 지도 고정 절편과 공선이다. 사전 포털 유무×머리 상호작용은 결과 변동이 있는 현재 지도에 모두 포털이 있어 머리 변수와 같아지므로 특이 행렬로 추정 불가였다. 탐색적 해초 밀도×머리 상호작용은 OR 2.064 [0.838 ～ 5.085], 정보 N356, 수렴했으나 구간이 1을 포함한다.')
add('[해석] 지도별 승률 차이는 크지만 독립적인 지도 배치 효과나 특정 배치가 경제 증대의 효과를 강화한다는 증거로 분리하지 못했다. 실패한 포털 모형도 삭제하지 않았다.')

add('## 4. 우리 승리 163판의 해부와 동일 지도·상대 패배')
add('[사실] 전수 승리 부류의 우선순위는 상대 전멸 → r300 뒤 현재 최장 길이 ≥8 사망 → 나머지 최종 길이 경주다. 왕이 바뀌거나 회복해도 사망 사건이 있으면 두 번째 부류다. 의도·회피 가능성·사망의 인과 기여를 부류 이름에 넣지 않았다.')
winrows=[]
for k,z in A['classes'].items():
 if not k.startswith('win:'):continue
 key=k[4:];q=F['classShare']['win:all']['classes'][key];q2=F['classShare']['win:waves']['classes'].get(key,{'n':0,'shareCI':wilson(0,109)})
 winrows.append([key,z['n'],rate(z['n'],163),f"{z['wavesN']}/{z['historyN']}",rate(q2['n'],109),fmt_counts(z['mapCounts']),fmt_counts(z['opponentCounts']),z['sameCellsLossN']])
table(['승리 부류','전체 N','전체 승리 중 [95%]','현재/과거 N','현재 승리 중 [95%]','지도별 N','상대별 N','같은 셀 패배 N'],winrows)
add('[사실] 현재 top-7 승리 109판 중 Autarky 51판(46.8%), Portals 21, Prisoners Dilemma 28, Slithery Fight 3, Queen Of Spades 2, Trauma 4다. 상대 전멸 승리 1판은 과거 Devil·306의 628109이며 현재 1,050판에는 없다. 과거 포함 Autarky 승리는 78/163이다.')
for k,z in A['classes'].items():
 if not k.startswith('win:'):continue
 add('### '+k)
 table(['지표','승리 평균 [95%], N','같은 지도·상대 패배 평균 [95%], N','승리−해당 셀 패배 평균 [95%], N'],[[LABELS[f],mean(z['indicators'][f]),mean(z['sameCellsLossIndicators'][f]),mean(z['matchedWinMinusLoss'][f])] for f in ['ourHeads10','ourHeads50','ourHeads100','ourHeads250','naturalRatio','ourFinal','ourLineage300','ourSacrifices','ourLineSac300','ourLatePieces','ourExposure']])
add('[사실] 마지막 열은 각 승리에서 같은 지도×상대 패배들의 평균을 빼고, 승리 판들의 차이를 평균했다. 과거·현재를 함께 쓴 기술 비교이며 같은 패배가 여러 승리의 기준으로 재사용된다. 이 t 구간은 반복 대조의 의존성이나 상대 버전 변화까지 보정한 인과 구간이 아니다.')
add('### 관측 가능한 상대 실패 신호')
siglabels={'late-king-loss':'r300 뒤 왕≥8 사망','king-sac':'왕≥8 빈 이웃 자해','king-trapped':'왕≥8 막힘 사망','king-ally-head':'왕≥8 아군 머리 충돌','king-enemy-head':'왕≥8 적 머리 충돌','timeout':'상대 시간 초과 사망'}
table(['시대','집단','결과','신호 (왕 신호는 경기 전체)','경기 N','신호 경기 N [Wilson 95%]'],[[z['era'],z['group'],z['outcome'],siglabels[z['signal']],z['n'],rate(z['count'],z['n'])] for z in F['opponentSignals']])
add('[해석] 머리 충돌·막힘·시간 초과는 보이는 사건이다. 빈 이웃이 있는 자해도 의도적 먹이가 될 수 있다. 다른 차례에서 드래곤이 움직이므로 빈 이웃은 안전한 반사실 선택의 증명도 아니다. 왕 소실 뒤 진주 회수와 후계 왕 회복을 함께 읽는다. “상대 실수 때문에만 이겼다”는 비율은 이 자료로 식별하지 않았다.')

add('## 5. 근소 패배와 r300/r400 선두 뒤 패배')
add('[사실] 근소 패배 = 결과 L, 상대 최장 >0, 우리 최장/상대 최장 ≥0.8. 전체 98판, 현재 66·과거 32판이다. 현재 양쪽 최장이 양수인 패배 474판 중 66판(13.9%, Wilson 11.1% ～ 17.3%)이다. 최장 동률 패배도 포함한다.')
add('양쪽 최종 계보의 r300 상태가 있으면 다음 항등식으로 격차를 분해한다: 상대 끝 − 우리 끝 = (상대−우리 L300) + (상대−우리 자연/희생/기타 아군/적 사망 섭취) + (우리−상대 질주/분열 감소). 가장 큰 양수 항을 부류로 삼고 동률은 L300→자연→희생→기타 아군→적 사망→질주→분열 순서다. 부류는 회계이며 이 항을 제거하는 행동의 효과가 아니다.')
table(['근소 패배 부류','전체 N','현재/과거 N','근소 패배 98판 중 [95%]','현재 66판 중 [95%]','지도별 N','상대별 N'],[[k[5:],z['n'],f"{z['wavesN']}/{z['historyN']}",rate(z['n'],98),rate(z['wavesN'],66),fmt_counts(z['mapCounts']),fmt_counts(z['opponentCounts'])] for k,z in A['classes'].items() if k.startswith('near:')])
add('### 근소 패배의 평균 최종 격차를 정확히 나누기')
terms={'initial-lineage':'L300','natural-intake':'자연 섭취','sacrifice-to-line':'아군 희생 공급','other-own-drops':'기타 아군 사망 공급','enemy-drops':'적 사망 공급','sprint-loss':'질주 감소','split-loss':'분열 감소'}
table(['격차 항 (양수면 상대 유리)','현재 근소 패배 평균 [95%], N','과거 평균 [95%], N'],[[label,mean(X['nearMissAccounting']['waves']['terms'][f]),mean(X['nearMissAccounting']['history']['terms'][f])] for f,label in terms.items()]+[['최종 격차',mean(X['nearMissAccounting']['waves']['gap']),mean(X['nearMissAccounting']['history']['gap'])]])
add('[사실] 현재 근소 패배에서는 L300 −7.9·자연 −5.9의 우리 우위에 상대 희생 공급 +18.4가 맞서며, 다른 항을 합하면 최종 격차 +4.3이다. 희생 최대 항인 49/66판과 평균 차는 서로 다른 집계다.')
add('### 최장 동률 10판: 전수 총길이 확인')
table(['게임','지도','상대','최장 우리/상대','총길이 우리/상대','끝 머리 우리/상대','공식 결과'],[[z['key'],z['map'],z['opponent'],f"{z['longest']}/{z['longest']}",f"{z['totalA']}/{z['totalB']}",f"{z['headsA']}/{z['headsB']}",z['outcome']] for z in TA['ties']])
add('[사실] 10판 모두 원 리플레이 종료 몸을 전수 재구성해 총길이까지 일치했다. 동률 패배는 길이 격차 0에 대한 항 분류를 유지하되, 승패를 직접 가른 총길이 규칙을 별도로 표시했다. 현재 동률 7판 중 6패·1무, 과거 동률 3판은 모두 패배다.')
add('### 현재 왕의 선두를 잃은 판')
leadrows=[]
for era in ['waves','history','all']:
 for t in [300,400]:
  rr=[g for g in G if (era=='all' or g['era']==era) and g.get('led'+str(t))];zz=collections.Counter(g['outcome'] for g in rr)
  leadrows.append([era,t,len(rr),f"{zz['W']}/{zz['D']}/{zz['L']}",rate(zz['L'],len(rr))])
table(['시대','선두 시점','선두 N','뒤 승/무/패','선두 뒤 패배 [Wilson 95%]'],leadrows)
table(['선두 뒤 패배 부류','전체 N','현재/과거 N','전체 436판 중 [95%]','현재 293판 중 [95%]','지도별 N','상대별 N'],[[k[5:],z['n'],f"{z['wavesN']}/{z['historyN']}",rate(z['n'],436),rate(z['wavesN'],293),fmt_counts(z['mapCounts']),fmt_counts(z['opponentCounts'])] for k,z in A['classes'].items() if k.startswith('lead:')])
add('[사실] 선두 뒤 패배는 처음 선두인 체크포인트 뒤 우리 현재 왕≥8 사망이 있으면 우선 분류하고, 다음은 상대 최종 계보의 후기 희생 공급 우위, 나머지는 other-growth다. 현재 r300 선두 391판에서 286패, r400 선두 199판에서 102패다. 두 시점 선두 패배의 합집합은 293판이며, 근소 패배와 겹치는 것은 56판이다. 전체에서는 선두 뒤 패배 436판 중 근소 패배 83판이 겹친다. N을 더하지 않는다.')
add('[해석] r300 왕 선두가 많은데도 승리가 적은 것은 선두 왕과 최종 왕이 다르거나, 왕을 잃거나, 적의 후기 공급이 더 빠른 세 경로를 구분해야 함을 보인다. 희생 공급을 최대 항으로 분류했다고 그 공급만 막으면 이긴다고 주장하지 않는다.')

add('## 6. 사전에 고정한 41개 리플레이 깊이 읽기')
add('[사실] 먼저 모든 승리/근소 패배/선두 뒤 패배 부류에서 게임 ID가 가장 작은 2판(부류 크기가 1이면 1판)을 선택했다. 선택 승리마다 같은 지도·상대의 최저 ID 패배를 같은 시대 우선으로 추가해 25판을 고정했다. 이 규칙은 과거에 편중되므로 읽기 전에 W12 각 비어 있지 않은 부류의 최저 ID 2판과 각 추가 승리의 가장 최근 이전 웨이브 같은 셀 패배를 더했다. 중복 제거 후 41판이다. `selection-v2.json`을 고정한 뒤에만 전부 깊이 읽었고, 읽은 뒤 선택은 바꾸지 않았다.')
add('[사실] 사례 수는 incidence 추정 분모가 아니다. 모든 부류의 크기는 전수에서 나온다. 아래 라운드는 0부터 시작하며 우리 A/상대 B다. 몸을 넘기는 분열은 ID 변경과 함께 계보에 남겼다. `deep.jsonl`에 전체 선택 판의 체크포인트·계보·소실·섭취·분열 포인터를 보존했다.')
table(['게임','지도','상대','결과','선택 이유'],[[d['key'],d['map'],d['opponent'],d['outcome'],', '.join(d['selection'])] for d in D])
for d in D:
 g=B[d['key']];add('### '+d['key']+' · '+d['map']+' · '+str(d['opponent'])+' · '+d['outcome'])
 add('[사실] 리플레이 `'+g['file']+'`. 부류 '+', '.join(f'{k}={g[k]}' for k in ['winClass','nearClass','leadClass'] if k in g)+'.')
 cp={q['r']:q for q in d['checkpoints']}
 table(['라운드','머리 A/B','현재 왕 A/B (ID, 길이)'],[[t,f"{cp[t]['A']['heads']}/{cp[t]['B']['heads']}",f"#{cp[t]['A']['kid']} L{cp[t]['A']['king']} / #{cp[t]['B']['kid']} L{cp[t]['B']['king']}"] for t in [0,50,100,250,300,400,450,490] if t in cp])
 def ancestor(tm):
  aa=[z['id'] for z in d['lines'][tm] if z['born']<300]
  return aa[-1] if aa else None
 add(f"1. [사실] 최종 왕 A #{d['final']['A']['kid']} L{d['final']['A']['len']}, B #{d['final']['B']['kid']} L{d['final']['B']['len']}. r300 최종 계보 조상 A #{ancestor('A')} L{g['ourLineage300']}, B #{ancestor('B')} L{g['theirLineage300']}. 종료 r{d['rounds']-1}.")
 relevant=[q for q in d['significantDeaths'] if q['isKing'] and q['r']>=300]
 if not relevant:relevant=[q for q in d['significantDeaths'] if q['isKing'] and q['r']>=250]
 relevant=sorted(relevant,key=lambda q:(-q['len'],q['r'],q['id']))[:2]
 if g['theirEliminated'] or g['ourEliminated']:
  tm='B' if g['theirEliminated'] else 'A'
  finaldeath=[q for q in d['significantDeaths'] if q['team']==tm and q['r']>=d['rounds']-3]
  if finaldeath:
   q=max(finaldeath,key=lambda q:(q['r'],q['id']))
   if q not in relevant:relevant.append(q)
 if relevant:
  for q in sorted(relevant,key=lambda q:(q['r'],q['id'])):
   t=q['turn'];eat=collections.Counter(z['team'] for z in q['eaters']);pos=t.get('head',{});free=[x['dir'] for x in t.get('free',[])]
   add(f"2. [사실] r{q['r']} {q['team']} #{q['id']} L{q['len']} 소실({q['cause']}), 접촉 #{q['otherId']} L{q['otherLength']}. 관측 마지막 차례 r{t.get('r')}, 머리 ({pos.get('x')},{pos.get('y')}), 행동 {t.get('action')}, 빈 이웃 {free}. 진주 {q['drops']}개 중 자기 팀 {eat[q['team']]}·적 {sum(eat.values())-eat[q['team']]}개 회수. 회수 포인터: "+(', '.join(f"#{z['id']}@r{z['r']}" for z in q['eaters'][:10]) or '없음')+'.')
 else:add('2. [사실] 위 표시 규칙에 해당하는 후기 길이 ≥8 왕 소실은 없다. 공급과 계보에 남긴 길이를 아래에서 비교한다.')
 add(f"3. [사실] r300 뒤 최종 계보 A/B: 자연 {g['ourLineNatural300']}/{g['theirLineNatural300']}, 희생 {g['ourLineSac300']}/{g['theirLineSac300']}, 기타 아군 사망 {g['ourLineOwnOther300']}/{g['theirLineOwnOther300']}, 적 사망 {g['ourLineEnemy300']}/{g['theirLineEnemy300']}, 질주 감소 {g['ourLineSprint300']}/{g['theirLineSprint300']}, 분열 감소 {g['ourLineSplit300']}/{g['theirLineSplit300']}.")
 for tm in ['A','B']:
  ev=[q for q in d['events'] if q['type']=='eat' and q['team']==tm and q['origin']=='own-sac' and q['r']>=300][:3]
  if ev:add('4. [사실] '+tm+' 계보의 첫 후기 희생 진주 섭취: '+', '.join(f"#{q['id']}@r{q['r']} ({q['tile']['x']},{q['tile']['y']})" for q in ev)+'.')
 facts,interp=NOTES[d['key']];add('5. [사실] '+facts);add('[해석] '+interp)
 if g.get('gapTerms'):add('[사실] 최종 격차 항: '+fmt_counts(g['gapTerms'])+f"; 합 {sum(g['gapTerms'].values())}, 공식 길이 차 {g['theirFinal']-g['ourFinal']}.")
 if g['ourFinal']==g['theirFinal']:
  tie=next(q for q in TA['ties'] if q['key']==g['key']);add(f"[사실] 최장 동률의 종료 판단: 총길이 {tie['totalA']}/{tie['totalB']}, 결과 {tie['outcome']}.")
add('[해석] 반복해서 보이는 승리는 큰 초기 계보·자연 공급·희생 공급·계보 유지의 여러 조합이다. 724071은 r400에 뒤졌다가 살아 있는 다른 왕이 커져 이겼고, 724083은 끝 직전 상대 왕 소실 뒤 승리했다. 반대로 677088·609361은 상대 왕을 잃게 해도 후계 왕이나 동률 해소 때문에 졌다. 왕 손실 자체를 승리의 충분조건으로 볼 수 없다.')

add('## 7. +3·+5·+10 top-6 승/60의 검출력')
add('[사실] 현재 top-6 기준 p0=0.09. 목표 p1은 0.14, 0.17333, 0.25667이다. 양측 α=0.05, 독립적인 기존/신규 두 팔을 같은 크기로 평가하는 두 비율 정규 근사를 썼다. 각 팔에 고정 지도×상대 구성을 유지하고 새 씨앗 평가를 가정한다. DEV 10판은 N에 포함하지 않는다.')
table(['추가 승/60','검출력','분산 가정','팔당 top-6 경기 N','두 팔 총 N','팔당 완전 웨이브','총 웨이브','완전 웨이브의 총 top-6 N'],[[z['plusWinsPer60'],pct(z['power']),z['noise'],z['gamesPerArm'],z['totalGames'],z['wavesPerArm'],z['totalWaves'],z['totalWaves']*60] for z in pw['table'] if z['noise']!='binomial-floor'])
add('[사실] 측정 분산의 하한 1을 유지한 80% 검출력은 팔당 638/258/80판, 두 팔 총 1,276/516/160판이다. 60판 웨이브로 올리면 팔당 11/5/2회, 총 22/10/4회이며 실제 평가하는 top-6 판은 1,320/600/240판이다. 각 실행에 DEV도 포함하면 전체 실행 판 수는 웨이브 수×70이다.')
add('[해석] 반복 잔여 자유도 3의 넓은 분산 상한(φ=8.951)을 적용한 행은 불확실성의 감도 분석이다. 기본 설계 약속이 아니다. 한두 웨이브 승수가 오르내리는 것으로 +3승을 판단하기 어렵다. 기존 900판을 고정 기준으로 재사용하거나 짝지은 씨앗 설계를 쓰면 필요한 신규 N이 달라지므로 이 표와 섞지 않는다. 정규 근사이며 정확한 지도별 검출력을 검증한 모의실험은 아니다.')

add('## 8. 결론: elite 승리에 연결된 지렛대와 최신 위치')
add('[사실] W12는 top-6 6승·0무·54패/60 [승률 Wilson 4.7% ～ 20.1%], 우리 전멸 24/60이다. DEV는 3승·0무·7패/10이다. 전체 현재 top-6는 81/900 [7.3% ～ 11.0%], 최종 최장 평균 14.1 [12.9 ～ 15.3] 대 29.2 [27.6 ～ 30.8]이다. 전멸 감소의 추세와 승리 증가의 추세를 구분해야 한다.')
latest=[g for g in G if g['wave']=='W12' and g['opponent']!=545 and g['family']=='r500']
add('### W12 top-6의 500라운드형 30판: 현재 경제와 왕')
fields=['ourHeads10','ourHeads50','ourHeads100','ourHeads250','ourNatural','ourKing300','ourFinal','ourSacrifices','ourLineSac300','ourLatePieces','ourExposure']
extraLabels={'ourNatural':'경기 전체 자연 진주','ourKing300':'r300 당시 현재 왕'}
table(['지표','우리 평균 [95%], N','동일 판 상대 평균 [95%], N'],[[LABELS.get(f,extraLabels.get(f,f)),mean(dist(g[f] for g in latest)),mean(dist(g[f.replace('our','their')] for g in latest))] for f in fields])
add(f"[사실] 이 30판에는 전멸 3판을 최종 길이 0으로 포함한다. 자연 진주 합계 비율은 {n(F['latestNaturalRatioOfTotals']*100,1)}%, 경기별 비율 평균은 {mean(X['latestPosition']['top6-r500']['indicators']['naturalRatio'])}다. 상대 0 결측·도달 N·노출 자격 N을 각각 유지했다.")
add('### 양쪽 최종 왕 계보가 r300에 있는 동일한 27판')
pair=F['latestPairedFlows'];flowlabels={'Lineage300':'L300','LineNatural300':'+ 자연','LineSac300':'+ 아군 희생','LineOwnOther300':'+ 기타 아군 사망','LineEnemy300':'+ 적 사망','LineSprint300':'− 질주','LineSplit300':'− 분열','Final':'= 끝 왕'}
table(['흐름','우리 평균 [95%], N','상대 평균 [95%], N','상대−우리 평균 [95%], N (비용은 부호 반대)'],[[flowlabels[f],mean(z['ours']),mean(z['theirs']),mean(z['enemyMinusOurs'])] for f,z in pair.items()])
add('[사실] 동일 27판의 끝 왕 격차는 19.6 [9.3 ～ 30.0], 희생 공급 격차는 20.1 [12.4 ～ 27.7]이다. 우리 L300과 자연 섭취가 평균적으로 조금 앞서도 이 공급 차를 덮지 못했다. 질주·분열은 계보 비용이므로 마지막 열의 음수 차가 상대에게 유리하다. 희생 항이 최종 격차의 102%인 것은 다른 항들이 상쇄하기 때문이지 설명력 R²가 아니다.')
table(['지렛대','top-6 단변수 보정 OR [95%], 정보 N','최신 30판의 실제 위치','판단'],[[lever_labels[z['feature']],f"{n(z['OR'],3)} [{n(z['CI'][0],3)} ～ {n(z['CI'][1],3)}], N={z['N']}",pos,interpret] for z,pos,interpret in zip(F['eliteScaledOR'],['r100 머리 12.6 / 33.1','자연 진주 227.3 / 733.9','r300 현재 왕 12.4 / 13.2','같은 27판 희생 공급 10.3 / 30.3','후기 조각 18.3 / 121.3','조건부 노출 46.8% / 17.2%'],['머리는 증가했으나 승리 연관의 구간은 넓다','규모 격차는 크지만 elite 안의 단변수 승리 연관은 불확실','양의 연관; 최종 왕의 초기 계보와 구분한다','양의 후기 연관이 크고 최신 공급 차도 크다','관측 승리 연관은 음수; 조각 출생만 늘리는 근거가 아니다','보호 방향은 맞지만 구간이 1을 조금 포함한다'])])
add('[해석] 우선 확인할 방향은 늘어난 머리와 질량을 최종 단일 왕에게 넣는 전환이다. 왕 계보 희생 공급, r300 이후 왕의 계보 유지, 적·아군 머리 접촉 뒤의 회복을 함께 측정할 필요가 있다. 큰 왕의 반복 몸 넘김이 섭취를 상쇄한 724073은 전환 손실을 검사할 구체적인 사례다. 현재 자료는 이 행동들을 바꾸면 몇 승이 늘어나는지 계산하지 못한다.')
add('[해석] 머리·자연 섭취의 구조 격차는 `intake-gap.md`, 후기 공급은 `supply-chain.md`, 왕 전환은 `endgame-king.md`의 진단과 연결된다. 다만 그 문서들의 다른 시점·모집단 수치를 이번 elite 승리 효과로 대체하지 않았다. `conversion-chain.md`, `economy-principles.md`, `our-eliminations.md`, `top-territory.md`도 배경이다. 우리 판의 직접 결과는 개선 후보를 검증하는 최종 지표로 남는다.')
add('### 전수 top-vs-top 참고 캐시: 별도 맥락')
table(['지도형','캐시 전체 N','500 종료 승자/패자 N','끝 왕 승자/패자 평균 [95%], N','r100 머리 승자/패자 평균 [95%], N','후기 희생 공급 승자/패자 평균 [95%], N'],[[k,z['n'],f"{z['winFinal']['n']}/{z['loseFinal']['n']}",mean(z['winFinal'])+' / '+mean(z['loseFinal']),mean(z['winHeads100'])+' / '+mean(z['loseHeads100']),mean(z['winLineSac'])+' / '+mean(z['loseLineSac'])] for k,z in A['topVsTop'].items()])
add('[사실] 지정된 `top-sample.jsonl`의 14,998행을 모두 읽었고 비활성·timeout 판도 제거하지 않았다. 지도형 N은 전체, 지표는 그중 500라운드 종료 판만이다. 왕 계보 없는 패자 1판의 희생은 결측으로 남겼다. 이 캐시는 우리 상대 승률·추세·검출력 분모에 넣지 않는다.')

add('## 독립 검산과 재현')
table(['핵심 수','1차 캐시·게임 JSON','독립 공식 업데이트 재구성'],[[k,K['sums']['primary'][k],K['sums']['independent'][k]] for k in K['sums']['primary']])
table(['두 팀 합계','별도 질량 시뮬레이터 전수','독립 공식 업데이트 전수'],[[k,EX['totals']['primary'][k],EX['totals']['independent'][k]] for k in EX['totals']['primary']])
table(['전수 부류','1차','독립 재구성으로 재분류'],[[k,v,CA['independentClasses'][k]] for k,v in CA['primaryClasses'].items()])
table(['추가 점검','1차','독립'],[['전체 종료 판',TA['gameN'],F['terminalIndependentN']],['최장 동률 판',TA['tieN'],F['independentTieN']],['반복 분산 φ',n(CA['powerPrimaryDispersion'],6),n(CA['powerIndependentDispersion'],6)]])
add(f"[사실] 1,680판 전부를 독립 스크립트로 다시 셌다. 머리 체크포인트·끝 최장·자연·희생·계보 L300와 흐름·노출의 경기별 숫자 불일치 {K['mismatchCount']}건, 후기 조각/전체 계보 희생/노출 분자·분모 불일치 {EX['mismatchCount']}건, 부류 불일치 {CA['mismatchCount']}건이다. 41개 깊이 읽기 판의 질량 점검도 전부 0이다. 기존 질량 점검 {M['cacheCheck']}, 기존 계보 점검 {M['egCheck']}.")
add('[사실] 최초 독립 사망 분류에서 아군 머리 접촉을 적 머리 접촉으로 분류한 202건을 찾았다(allyHead→ram 99, →rammed 103). 그 의미를 수정한 새 스크립트로 전 모집단을 다시 실행했다. 현재 왕 사망 사건 2,284개의 원인도 최종 불일치 0이다. 최초 오류 캐시를 덮어쓰지 않고 함께 남겼다.')
add('[사실] 기존 질량 장부가 빠진 stack5 677098은 새 장부로 추출했다. 기존 왕 계보 캐시가 없는 stack5 1판·W12 70판의 노출은 전수 원 리플레이의 두 구현으로 보완했다. 캐시 존재 여부 때문에 경기를 제외하지 않았다.')
add('스크립트와 캐시는 `exp/outcome-review/`, `.cache/outcome-review/`에 있다. 실행 순서와 최종 사용 판본은 `exp/outcome-review/RUN-final.md`에 적었다. 쓰기는 `x`/`wx`로 새 경로를 만들며 기존 산출물을 덮어쓰지 않는다. 재실행은 새 하위 출력 경로를 사용하는 새 스크립트 판본으로 해야 한다. `SUMMARY.txt`는 최종 보고서·수치·사례 점검 후 마지막에만 쓴다.')

add('## 부록 A. 웨이브 × 지도형 (top-6/DEV)')
outcome_table([([w,gr,fa],z) for w,grs in A['waveFamily'].items() for gr,fams in grs.items() for fa,z in fams.items()],['웨이브','집단','지도형'])
add('## 부록 B. 웨이브 × 지도 (top-6/DEV)')
outcome_table([([w,m,gr],z) for w,maps in A['waveMap'].items() for m,grs in maps.items() for gr,z in grs.items()],['웨이브','지도','집단'])
add('## 부록 C. 웨이브 × 상대')
outcome_table([([w,op],z) for w,ops in A['waveOpponent'].items() for op,z in ops.items()],['웨이브','상대'])
add('[사실] DEV의 웨이브×지도 셀은 N=1이다. 승률에는 Wilson을 쓰되 길이 평균의 분산 구간은 추정할 수 없어 –로 두었다. 무·패·우리/상대 전멸의 모든 95% 구간은 기계 표 각 셀에 남겼다.')
add('## 부록 D. 모든 단변수 보정 모형')
table(['모형','후보/완전값 N','정보 N/층','군집 N','변수','원 척도 OR [95%]'],[[name,f"{z['candidateN']}/{z['completeN']}",f"{z['informativeN']}/{z['strata']}",z['clusters'],q['feature'],f"{n(q['OR'],3)} [{n(q['ORCI'][0],3)} ～ {n(q['ORCI'][1],3)}]"] for name,z in models.items() if name.startswith(('single-adjusted:','elite-single:')) for q in z.get('coefficients',[])])
add('## 부록 E. 지도 × 상대 × 왕 계보 희생 공급의 전수 층별 표')
table(['지도','상대','r300+ 왕 계보 희생 구간','N','승/무/패','승률 Wilson 95%'],[[z['map'],z['opponent'],str(z['range']).replace('None','∞'),z['n'],wl(z),rate(z['W'],z['n'])] for z in A['stratified']['ourLineSac300-map-opponent']])
text='\n'.join(L)+'\n'
with open(C/'report-draft-final.md','x',encoding='utf-8') as f:f.write(text)
print('Rendered new draft:',len(text.splitlines()),'lines;',len(text.encode()),'bytes; 41 cases, all eight questions.')
