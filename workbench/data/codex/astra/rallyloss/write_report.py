import sys
sys.dont_write_bytecode=True
import json,csv
from pathlib import Path
from statistics import median
OUT=Path('data/codex/astra/rallyloss')
S=json.loads((OUT/'summary.json').read_text());A=json.loads((OUT/'audit.json').read_text())
G=list(map(json.loads,(OUT/'games.jsonl').read_text().splitlines()))
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])
def pct(a,b):return f'{a/b*100:.1f}%' if b else '—'
ledgerrows=[]
for label in ['one5-w1','one6-w1','one5-c1','one6-c1']:
    for s in ('0','1'):
        x=S[label]['sides'][s]['ledger'];ledgerrows.append([label,'우리' if s=='0' else 'WHQ' if '-w1' in label else 'Cache',*[x[k] for k in ['start','natural','mate_corpse','enemy_corpse','dead','paid','end','ours_eaten_enemy','residual']]])
ledger_table=table(['15판 합','진영','L350','자연 +','아군사체 +','적사체 +','사망 −','질주 −','끝','우리사체→적¹','잔차'],ledgerrows)
rallyrows=[]
for label in ['one5-w1','one6-w1','one5-c1','one6-c1']:
    c=S[label]['rally_inward'];rallyrows.append([label,c['n'],c['mass'],c['arrived'],c['advertised_arrived'],c['died_before_arrival'],c['ever_top'],c['end_transported'],pct(c['end_transported'],c['mass'])])
rally_table=table(['접근 대용²','개체','초기질량','전역최장≤3','알려진리더≤3','도착 전 사망','당시최장 섭취³','끝최장에 전달·잔존³','몫'],rallyrows)
foldrows=[]
for label in ['one5-w1','one6-w1','one5-c1','one6-c1']:
    x=A['sets'][label]['fold'];waits=[int(w) for w,n in x['wait'].items() for _ in range(n)];c=S[label]['fold'];foldrows.append([label,'WHQ' if '-w1' in label else 'Cache',x['n'],x['mass'],x['drop'],x['to_longest'],x['to_mates']-x['to_longest'],x['to_enemy'],x['uneaten'],median(waits),c['end_transported'],pct(c['end_transported'],x['mass'])])
fold_table=table(['상대 접기⁴','상대','희생','길이','드롭','사망시 최장 회수','다른 아군','적','미회수','회수 지연 중앙값','끝최장 잔존³','몫'],foldrows)
agerows=[]
for label in ['one6-w1','one6-c1']:
    for band in ['0-5','6-15','16-25']:
        x=A['sets'][label]['age'][band];agerows.append([label,band,x['n'],x['dead_leader'],x['bad_ratio'],x['wrong_top'],x['retained']])
age_table=table(['조건 후보 전체','보고 나이','개체','대상 이미 사망','실제 길이비 불충족','전역최장 아님','전달·끝잔존³'],agerows)
main='''[M] 발견: 원거리 접근의 전달 몫은 낮고, 분열·사망한 리더의 낡은 보고를 따른다. WHQ의 가까운 희생은 대부분 아군이 회수한다.
[C/E] 판정·카드 하나: 집결을 **변경**—`RALLY_END_FRESH 25 → 5`; 5라운드 이내 리더 보고일 때만 막판 원거리 집결한다.
[E] 확신: 장부 높음, 잘못된 목표 추적 중간, 5의 최적성·온라인 개선 낮음.

[M] WHQ·Cache 각 one5/one6 15판, 총 60판. r350 뒤는 r351–종료다. 양편 120개 장부와 초기상태부터의 독립 재구성 120개 모두 잔차 0. 이른 종료는 종료 상태를 유지한다.

'''+ledger_table+'''

[M] 사망 원인별·판별 장부는 [tables.md](tables.md), [ledger.tsv](ledger.tsv)에 있다. ¹적이 먹은 사체는 별도 유출 표시이며 사망 차감에 다시 더하지 않는다.

'''+rally_table+'''

[M/E] ²음파로 확인한 리더, 정보 나이≤25, 길이비≥2, 거리>15, 먹이 라운드 이후이며 그 위치 쪽 이동이 있었던 개체다. **실제 집결 호출 수는 아니다**: one5에도 대용 개체가 있다. ³초기 질량의 보존 추적 모형; 자연 성장 제외, 분열·재섭취 포함. 끝 잔존은 실제 사체 전달된 질량만 센다.

'''+fold_table+'''

[M/E] ⁴r351 이후 비여왕·길이≤당시최장/2·최장≤3칸에서 정지/자기몸 사망한 조건부 표본이다. 이동 후보와 모집단이 달라 인과 비교는 아니다. WHQ 희생 거리 1/2/3칸은 one6 세트에서 36/54/101건; 189건 정지, 2건 자기몸이다. Cache는 121건 모두 자기몸이다.

'''+age_table+'''

[M] 장면: M1474983 #621은 r376 L24→L2+자식 #670 L22로 분열했지만 #9는 r401에 r376 보고를 따라간다. #75는 r410 최장 3칸 이내 도착, r411 정지, r419 적 #497이 회수한다. #127은 r424 정지→r428 당시 비최장 #603이 회수한다. WHQ #616(r371), #680(r397)은 1칸 옆 정지→다음 라운드 최장이 회수한다. [추가 장면](moments.md).

[M] 먹은 뒤 당시 최장 L≥10의 one6 사망은 WHQ전 2건: M1474983 r441 #670 L35, 공격자 L6·시작거리5·5걸음; M1474989 r425 #1 L25, L3·거리4·4걸음. 둘 다 빈 출구2. Cache전 r444(M1477040) #903 L13은 L2·거리1에 피격, 드롭7개 전부 적에게 간다. 분열 계보와 그 외 생존/재희생은 [fed_leaders.tsv](fed_leaders.tsv).

[C/E] 위치: one5/one6 `main.cpp:280`, 호출 `682–684`, 관문 `5575–5582`. `5597–5625`의 기존 희생·적4칸 검사는 유지한다. 기존 상수만 변경하며 [한 줄 패치](card.patch)와 native C++20 컴파일 통과 복사본을 준비했다. 5는 기존 `FEEDER_FRESH_ROUNDS`와 같은 보수적 후보다.

[E] 판정 표본은 온라인 60판. 확인은 WHQ·Cache 각각 15판의 계측 기보에서 먹이 라운드 뒤 **보고 나이>5인 집결 호출 0**, 사망한 목표 추적 감소, 전달·최장 계보 유지 여부다. 전달이 줄거나 유효한 리더 접근만 막으면 반증이다. 그 확인 30판은 실행하지 않았다.

[M/E] 미확인: 숨은 우선 경로/역할 때문에 모든 실제 집결 개체를 식별하지 못했다. 전역최장 거리에는 벽·포털을 반영하지 않았다. 양 버전 WHQ 시드는 15/15 다르고 여왕 변경도 동시 적용돼 승패 차이를 집결에 귀속하지 않는다. CPU/WASM·미지지도·패치 온라인 결과 미확인. 운영 소스·제출 변경 없음.
'''
(OUT/'report.md').write_text(main)
causekeys=['rammed','rams','wall','own body','mate body','foe body','mate head','stop']
fullrows=[]
for x in csv.DictReader((OUT/'ledger.tsv').open(),delimiter='\t'):
    fullrows.append([x['label'],x['gid'],x['map'],x['side'],x['last'],*[x[k] for k in ['start','natural','mate_corpse','enemy_corpse',*causekeys,'paid','ours_eaten_enemy','end','residual']]])
full_table=table(['세트','M id','지도','진영','종료 r','L350','자연+','아군+','적+','피격−','자발램−','벽−','자기몸−','아군몸−','적몸−','아군머리−','무행동−','질주−','사체→적','끝','잔차'],fullrows)
tables='[M] 전수 60판 × 양편. 지도명은 사례 식별용이다. 규칙은 지도명·크기 표에 의존하지 않는다.\n\n'+ledger_table+'\n\n[M] 사망 원인 합은 사망 길이와 같다. 모든 잔차=0. corpse→enemy는 r351 뒤 죽은 해당 진영 드롭 중 종료 전 상대가 먹은 알이다. 자연/사체 섭취에는 r350 전에 생긴 진주도 포함한다. 이른 종료에서는 L350=종료 길이, 기간 섭취·사망·질주=0.\n\n'+full_table+'\n\n[M] r401–종료 장부는 [ledger400.tsv](ledger400.tsv). 개체 전수는 [tracked.tsv](tracked.tsv), 모든 전달은 [transfers.tsv](transfers.tsv), 정보의 실제 대상 검사는 [candidate_truth.tsv](candidate_truth.tsv), 상대 회수는 [fold.tsv](fold.tsv).\n'
(OUT/'tables.md').write_text(tables)
methods='''[M] 입력은 다운로드된 one5-w1/one6-w1/one5-c1/one6-c1 60개 packed Cap’n Proto 기보다. 네트워크·온라인 신청·로컬 경기 없이 기존 `o1_scan.scan`, `longest.analyze.detail`, `ladder_replay.replay`를 import했다. 소스는 읽기만 했다. `inventory.json`은 최종 입력 현황이다.

[M] 장부 = L(컷오프) + 자연 섭취 + 아군 사체 섭취 + 적 사체 섭취 − 모든 사망 길이 − 유료 이동 비용 = 종료 L. `o1_scan`의 턴별 보존식으로 유료 비용을 복원한다. rammed는 적이 움직여 접촉한 피해자, rams는 접촉을 시작한 우리 용이다. mate head와 enemy body도 별도 열이 있어 누락되지 않는다. stop은 엔진 reason4 전체이며 의도적 희생이라고 단정하지 않는다. 이동 대용의 stop에서 timeout 기록은 0건이다. `ledger.tsv`/`ledger400.tsv`에 각각 120행, `audit.tsv`에 초기상태부터의 별도 120식, 잔차는 모두 0이다.

[M/E] 실제 `rally_ready()` 호출 로그는 없다. 발신 음파의 SipHash 검사·암호를 원본 codec에 따라 복호화하고 원본 SipHash reference vector를 검증했다. 각 차례의 발신 리더 보고에서 id/길이/위치/원본 시각을 얻는다. 그 차례의 참상태 길이와 나이를 대조했다. 비여왕, 자신 아닌 리더, 길이비2, 거리>15, 팀 유닛>3, 막판 신선도≤25라는 확인 가능한 조건을 적용한다. queen_game 태그가 관측된 프로세스는 feed_round300, 그 밖은400으로 두었다. 숨은 조기 queen_game 전환은 누락될 수 있다. FEED_CAP_UNITS가 r351에 먹이를 시작해도 RALLY_END_FRESH는 feed_round 전에는 적용되지 않는다.

[M/E] 차례 종료 위치가 보고 위치에 더 가까워진 차례를 하나 이상 가진 개체를 inward 표본으로 삼았다. 원거리 후보는 최초 조건 충족 시점의 질량으로 추적한다. 실제 route_target과 escape/staffing/chase/ram의 우선순위, trader와 fallback 상태는 복원하지 않았으므로 인과적으로 rally라고 확정하지 않는다. 따라서 one5에도 대용 표본이 존재한다. 죽는 차례에서 음파가 없을 수 있으므로 first-step 실패는 이동 확정 표본에서 빠질 수 있다. `tracked.tsv`에는 이동 없는 조건 후보도 모두 남겼다.

[M/E] 도착은 살아 있는 같은 id가 당시 전역최장 머리의 토러스 맨해튼 거리≤3이 되는 것이다. 지도 벽·포털·적 차단은 반영하지 않는다. 따로 자신의 음파 리더 실제 머리에 도착한 수도 기록했다. 죽음은 원 id의 죽음이고, 추적 질량은 자손까지 계속 따른다. 도착 전 죽음을 집결이 유발했다고 단정하지 않는다. 사망하는 차례의 advertised_distance는 마지막 발신 보고 대상의 실제 위치에 대한 거리일 수 있고, 그 차례의 새 입력을 복원한 값은 아니다.

[E] 초기 질량은 토큰 보존 모형으로 센다. 한 걸음에서 먹지 않았으면 꼬리 토큰을 머리로 옮기고, 먹었으면 그 진주 토큰을 머리에 추가한다. 유료 이동에서 빠진 토큰은 소실, 분열은 좌표로 토큰을 두 몸에 배분, 사망은 원본 몸의 짝수 인덱스 토큰만 진주로 남긴다. 자연 진주는 새로운 토큰이다. 이는 엔진에 존재하지 않는 물질 식별자를 부여한 명시적 모형이며 성장으로 섞인 초기/새 질량 배분에 가정이 들어간다. 각각의 5,173개 추적 관측에서 초기질량=소실+몸/바닥에 잔존을 검증했다. 접기 관측은 같은 질량의 재희생이 중복 계수될 수 있고, 이동 대용은 최초 조건 시점 표본이므로 두 모집단을 순수 효율의 인과 비교로 쓰지 않는다.

[M/E] ever_top는 섭취 직전 그 팀 전역최장인 용이 먹은 초기 토큰의 누적 고유 수다. end_transported는 후보 선언 이후 한 번 이상 아군이 사체 진주로 회수하고, 종료 때 그 팀 최장의 몸에 들어 있는 초기 토큰 수다. 자손에게 전달된 것도 포함한다. 단순히 후보 자신이 자라 최장이 된 초기 질량은 end_transported에 포함하지 않는다. 모형상 전달·소실은 재섭취를 포함해 닫히지만 지형 경로와 실제 행동 의도는 알려주지 않는다.

[C] 원본 one5/one6 차이는 QUEEN_DEAD_ALL(main.cpp151)과 RALLY_END_FRESH(280) 두 상수다. 호출682–684는 기존 route_target이 없을 때만 쓴다. 관문5575–5582는 메시지 나이/길이비를 확인하지만 보고 대상의 생존·분열은 확인하지 않는다. `hear_sighting`1926–1930은 같은 id의 길이를 max로 유지한다. SONAR_STALE25(60), FEEDER_FRESH_ROUNDS5(62), FEEDER_DIE_DIST3(64), keep-off2(58), 죽기5597–5607, 이동거부5984–5986이다. 따라서 ‘옆1칸에서만 죽기’ 한 줄을 제안하면 keep-off2 때문에 보통 접근할 수 없으므로 이 보고는 그 카드를 제안하지 않는다.

[E] 카드의 정확한 제안은 RALLY_END_FRESH를5로 제한하는 것뿐이다. 실제 최장 선출 문제·이미 잘못된 1–5라운드 보고·기존 근거리 먹이기를 해결하지 않는다. 유효한 장거리 이송을 줄일 수 있다. 검증 기보에는 route 선택 순간 RALLY(round,id,target,report_age)를 남겨 호출 수를 직접 세어야 한다. 온라인 대전 실행은 이 분석의 권한 밖이며 다음 30판 수집은 조정자가 결정한다.

[M] 복사본 C++20 native 컴파일은 성공했다. 패치는 `card.patch`, 복사본은 `build-check/`이고 온라인 source/WASM과 CPU는 변경·검사하지 않았다. 셸 nice 요청은 sandbox의 setpriority 제한으로 실패해 로그에 남았다. 외부 상태 변경과 경기 실행은 없었다.
'''
(OUT/'methods.md').write_text(methods)
moments='''[M] 장부 장면 1: M1474983 Australia, r350 우리217/WHQ249→r400 173/258→r499 120/247. 우리 식217+120+157+29−400−3=120, WHQ249+280+335+71−669−19=247.

[M] 장부 장면 2: M1474996 Slithery Fight r350 우리247/WHQ267→r400 242/237→r499 152/301. 우리247+142+277+33−547=152, WHQ267+502+545+31−1042−2=301. 사망과 드롭 회수가 많아도 자연 섭취와 합산해야 총길이가 설명된다.

[M] 잘못된 목표 장면 1: M1474983 r376 #621 L24→부모L2+자식#670 L22. r393 부모가 다시 L4→L2로 분열한다. #9 r401 머리(49,55), 알려진 목표#621 (58,17), 길이24·나이25·거리35. 당시 전역최장#670 L22이며 #621을 따라간다는 것은 실제 최장을 따라간다는 뜻이 아니다. #9는 종료까지 같은 id로 생존하지만 그 초기질량3은 최장에게 전달되지 않는다.

[M] 잘못된 목표 장면 2: 같은 판 #712 r401 (2,35), 같은 r376 #621 보고·거리26. r402 (2,36)에서 적#614 L3에게 한 걸음·시작거리1로 들이받힘. 당시 전역최장까지40칸. 드롭 하나는 적#600이 r403, 다른 하나는 우리#23이 r405에 회수한다. [E] 이 이동의 실제 우선 경로가 집결이었다는 증거는 없다.

[M] 이송 장면 1: M1474983 #75 초기L2/r401 (37,20), 보고 목표까지23. r410 당시 최장#670과3칸, r411 (39,20)에서 stop; r419 적#497이 유일한 드롭 회수. 초기 토큰2 중 최장 전달0.

[M] 이송 장면 2: M1474983 #127 초기L2/r401 (9,1), 목표까지31. r424 (4,1) stop, 당시 최장#670까지50칸. r428 비최장#603이 회수. #603이 나중에 최장이 되어 초기질량1은 종료 때 그 몸에 남는다. ‘당시 최장 섭취’와 ‘끝 최장 잔존’은 다른 지표다.

[M] 이송 장면 3: M1474983 #527 초기L2/r401 (49,31), 목표까지23. r434 (0,39)에서 적#759가 L4·세 걸음·시작거리3으로 피격시킴. 당시 최장까지31칸, 도착 기록 없음. 드롭은 r435 적#771, r436 적#737이 회수한다.

[M] WHQ 전달 장면 1: M1474983 r371 #616 L2 (5,42), 최장#284과1칸 옆 stop; r372 #284 회수. 장면 2: 같은 판 r397 #680 L2 (43,43), 최장#501과1칸 옆 stop; r398 #501 회수. 장면 3: M1474996 r352 #1066 L2 (45,13), 최장여왕#1과3칸 옆 stop; r354 #1 회수. [E] 고의성은 상대 소스가 없으므로 확정하지 않는다.

[M] Cache 전달 장면 1: M1477039 r378 #612 L2 (51,16), 최장#556과3칸 떨어져 자기몸 사망; r380 #556 회수. 장면 2: 같은 판 r394 #152 L2 (44,19), #556과3칸, 자기몸 사망→r395 #556 회수. 반례: M1477040 r357 #248 L4 (51,36), 최장과3칸, 자기몸 사망 드롭2개는 r359/r361 모두 우리#244가 회수.

[M] 먹인 최장 피격 장면 1: M1474983 r441 #670 L35 (47,29), 아군 정지 드롭13알을 먹은 이력. 적L6가5칸 거리에서5걸음(유료2)으로 공격, 빈 출구2. 18개 드롭 중 아군10/적8. #603은 종료L29 생존.

[M] 먹인 최장 피격 장면 2: M1474989 r425 우리여왕#1 L25 (30,4), 정지 드롭18알을 먹은 이력. 적L3가4칸 거리에서4걸음(유료2)으로 공격, 빈 출구2. 13개 드롭 중 아군11/적2. 최종최장#342 L28은 먹인 계보 자손으로 남는다.

[M] 먹인 최장 피격 장면 3: M1477040 r444 #903 L13 (33,23), 정지 드롭8알을 먹은 이력. 적L2가1칸에서한 걸음으로 공격, 빈 출구2. 드롭7개 전부 적 회수, 아군0. 최종최장#1069 L18은 다른 먹인 계보 자손이다.
'''
(OUT/'moments.md').write_text(moments)
print('report words excluding tables:',len(' '.join(l for l in main.splitlines() if not l.startswith('|')).split()))
