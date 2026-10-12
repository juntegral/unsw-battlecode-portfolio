# 구현 적용 확인

- 대상: `exp/stack11-a-px4` 60판 · 비교: `exp/stack10-a-px4` 60판
- 기준(사용자 규칙 2026-09-30): 승률이 아니라, 봇에 구현한 기능이 이 상대들에게 실제로 발동하고 의도대로 작동했는지를 본다.
- "의도대로"의 정의: 모이기=왕 3칸 안까지 가거나 희생까지 함 · 희생=떨군 진주 절반 이상을 우리 팀이 먹고 상대는 못 먹음 · 한입=2턴 안 분열하고 30라운드 뒤 가족 길이가 줄지 않음 · 탈출 분열=10라운드 뒤 몸이 살아 있음 · 정책 분열=새끼 30라운드 생존 · 탈출 질주·위협 피하기=10라운드 뒤 몸 생존 · 포털=3라운드 뒤 몸 생존 · 돌진=충돌 성사, 잡은 길이 ≥ 우리, 두 몸의 진주를 우리가 더 먹음 · 먹이 질주=진주 먹음.
- "몸"은 그 드래곤과 그 뒤 분열로 태어난 자손 전체다. 통로 고리처럼 몸을 새끼에게 넘기며 버티는 경우를 손실로 세지 않기 위해서다.
- stack2의 "의도대로": 조각 떼기=조각이 30라운드 살며 진주를 1개 이상 먹거나, 나중에 희생(feed·conv)으로 아군을 먹임 · 새 사망 진주 줍기=표적이 된 사망 진주(진주 하나가 한 건)를 우리 팀이 먹음(자연 진주로 오인했거나 이미 없던 표적은 판정에서 뺌).
- stack4의 "의도대로": tg=표식 턴 뒤 2라운드 안에 박히지 않음 · 몰렸을 때 분열=10라운드 뒤 몸이 살아 있음(보존율은 효과 줄) · px=그 턴에 우리 드래곤과 부딪혀 죽지 않음 · gx=그 드래곤의 몸(그 드래곤과 뒤에 태어난 자손)이 끝까지 삶(사용자 결정 17:16: 생존은 몸으로 판정, 드래곤 자체 생존은 참고).
- cand-mapid의 "의도대로": Schooltime b 초반 분열(bsp)=떼어 낸 조각(새 유닛)이 10라운드 뒤 살아 있음 · 지도·판본 인식=그 판에서 1개 이상의 프로세스가 판본까지 결정했고, 결정한 프로세스(마지막 표식 기준)가 모두 정답 지도·판본을 댐. 정답 판본은 로컬이면 지도 파일 이름, 온라인이면 기보의 자연 생성(한쪽 판본에서만 생성하는 칸)으로 정하고, 끝까지 가릴 수 없던 판은 뺀다. 지도별 줄의 이름 뒤 a·b·?가 정답 판본이다.
- stack5의 "의도대로": 덮기 분열=새끼가 30라운드 안에 자연 진주를 1개 이상 먹음(생존은 효과 줄) · 샘 지킴=목표 샘 3걸음 안에 든 뒤 30라운드 동안 그 무리(실제 샘, 목표에서 3걸음 안)에 생긴 자연 진주의 85% 이상을 우리가 먹음(도착하지 않았거나 진주가 생기지 않은 목표는 뺌) · 영토 덮기 끌림=20라운드 안에 우리 영토 자연 진주를 먹음. 게이트와 가설 수준 지표는 맨 뒤 stack5 절.
- stack7의 "의도대로": 수 바닥 분열(floor)=새끼가 30라운드 뒤 살아 있음 · 왕 길이 상한 분열(kcap)=새끼가 10라운드 뒤 살아 있음(부모 생존은 효과 줄). 판이 먼저 끝나면 생존으로 센다. 게이트, 저수 에피소드, 지도 가르기는 맨 뒤 stack7 절.
- stack9의 "의도대로": 늦은 재분열(lsplit)=새끼가 30라운드 안에 자연 진주를 1개 이상 먹음(떨군 진주의 우리 몫은 게이트 표) · 영토 덮기 끌림 창(cov 창)=표식이 연 30라운드 창 안에 그 드래곤이 우리 영토 자연 진주를 1개 이상 먹음. fc는 frag 줄에 포함된다. 게이트, 가설 수준 지표(공급 사슬 연구의 정의), 부작용은 맨 뒤 stack9 절.
- stack10의 "의도대로": 국지 수 우세 박음(lnt)=맞부딪힌 두 몸의 진주를 20라운드 안에 우리가 상대보다 많이 먹음(게이트는 합산 몫과 건당 net20) · 국지 수 열세 교환 거부(lntv)=10라운드 뒤 몸이 살아 있음(관찰) · 거부 예외(kint)=교환의 net20 > 0. 게이트, B3 빈도, 모든 교환, utab은 맨 뒤 stack10 절.
- stack11의 "의도대로": 더 긴 아군 곁 새 사망 진주 양보(ghd)=그 진주를 곁의 더 긴 아군(첫 표식 때 표식한 드래곤보다 길고 머리가 진주에서 맨해튼 2 안)이 먹음. gh·kx·lwk는 턴 단위 기록이라 "의도대로"를 매기지 않는다(설계 상황은 효과 줄). 게이트(가로채기, 노출, 끝판 창 대상 적중), 가설 수준 지표(끝판 왕 연구의 정의), 부작용은 맨 뒤 stack11 절.

## 요약

| 기능 | 발동(판당) | 의도대로 | 비교: 발동(판당) | 비교: 의도대로 |
|---|---:|---:|---:|---:|
| 모이기 물러서기 (gh, stack11; 턴 단위) | 2599 (43.3) | – | 0 (0) | – |
| 더 긴 아군 곁 새 사망 진주 양보 (ghd, stack11; 드래곤·진주 단위) | 386 (6.4) | 45% | 0 (0) | – |
| 왕 떼기 (kx, stack11; 턴 단위) | 616 (10.3) | – | 0 (0) | – |
| 끝판 창 왕 부류에게만 (lwk, stack11; 턴 단위) | 431 (7.2) | – | 0 (0) | – |
| 늦은 재분열 (lsplit, stack9) | 284 (4.7) | 25% | 288 (4.8) | 27% |
| 영토 덮기 끌림 30라운드 창 (cov 창, stack9; 드래곤·창 단위) | 3061 (51) | 29% | 3048 (50.8) | 29% |
| 국지 수 우세 박음 (lnt, stack10) | 168 (2.8) | 45% | 167 (2.8) | 43% |
| 국지 수 열세 교환 거부 (lntv, stack10) | 10 (0.2) | 80% | 12 (0.2) | 83% |
| 거부 예외: 상대 최장일 수 있음 (kint, stack10) | 9 (0.2) | 100% | 7 (0.1) | 100% |
| 몫을 긴 아군에게 넘기지 않음 (cl, stack8; 드래곤·진주 단위) | 10774 (179.6) | 68% | 10803 (180.1) | 67% |
| 수 바닥 분열 (split floor, stack7) | 25 (0.4) | 64% | 23 (0.4) | 70% |
| 왕 길이 상한 분열 (split kcap, stack7) | 1 (0) | 100% | 1 (0) | 100% |
| 지도·판본 인식 (map=, cand-mapid; 판 단위) | 60 (1) | 100% | 60 (1) | 100% |
| 덮기 분열 (csplit, stack5) | 1050 (17.5) | 38% | 1051 (17.5) | 38% |
| 샘 지킴 (F, stack5; 드래곤·샘 단위) | 1009 (16.8) | 90% | 1004 (16.7) | 90% |
| 영토 덮기 끌림 (cov, stack5) | 28184 (469.7) | 20% | 28095 (468.3) | 20% |
| 위협 모형 빈틈 (tg, stack4) | 11030 (183.8) | 98% | 11159 (186) | 98% |
| 모이기 시작 제한 (gx, stack4; 드래곤 단위) | 137 (2.3) | 97% | 60 (1) | 97% |
| 큰 아군 곁 희생 (conv, stack1 M1) | 222 (3.7) | 97% | 203 (3.4) | 100% |
| 조각 떼기 (split frag, stack2 S1) | 41 (0.7) | 34% | 46 (0.8) | 59% |
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 2781 (46.4) | 81% | 2847 (47.5) | 81% |
| 왕에게 모이기 (g, 드래곤 단위) | 1074 (17.9) | 76% | 1052 (17.5) | 80% |
| 희생 먹이기 (feed) | 176 (2.9) | 90% | 223 (3.7) | 88% |
| 막다른 길 한입 (pocket-eat) | 7 (0.1) | 71% | 6 (0.1) | 83% |
| 탈출 분열 (escape-split) | 4109 (68.5) | 98% | 4100 (68.3) | 97% |
| 출구 없음 (no-exit) | 4310 (71.8) | – | 4308 (71.8) | – |
| 정책 분열 (split) | 3 (0.1) | 100% | 3 (0.1) | 100% |
| 탈출 질주 3칸 (esc) | 72 (1.2) | 93% | 56 (0.9) | 93% |
| 위협 피하기 2칸 질주 | 585 (9.8) | 91% | 591 (9.9) | 91% |
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 2497 (41.6) | 93% | 2448 (40.8) | 93% |
| 돌진 (TRADE) | 213 (3.6) | 47% | 209 (3.5) | 42% |
| 먹이 질주 (2칸 이상, 먹은 것) | 175 (2.9) | 100% | 185 (3.1) | 100% |
| 기타 2칸 질주 | 55 (0.9) | – | 62 (1) | – |
| 마지막 돌진 (last-trade) | 17 (0.3) | – | 21 (0.4) | – |

- 건강: 턴 239329, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 비교 건강: 턴 236884, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 11782턴 · 끝판(late) 6430턴 · 돌진 신뢰(T, 탈출 끔) 0턴, 그 직후 박혀 죽음 0

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 비교 |
|---|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 7% (174/2591턴) | 7% (175/2557턴) |
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 36.9칸 (10.6회), 진주 우리 95% · 상대 1% | 45.3칸 (11.5회), 진주 우리 95% · 상대 2% |
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 2.7칸 (판당 0.07회) | 2.2칸 (판당 0.03회) |
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 23% (1008/4390턴) | 21% (846/4093턴) |
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.050회 (3건, 80칸) | 판당 0.100회 (6건, 146칸) |
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 9.4마리 (30판) | 9.1마리 (30판) |
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 19.2회 | 20.7회 |
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 58% (우리 37%) | 57% (우리 37%) |
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 9.7 대 상대 28 (9.6회) · 박힌 교환의 우리 몫 14% (174회) | 우리 8.6 대 상대 29.6 (9.9회) · 박힌 교환의 우리 몫 14% (178회) |
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 13.2개 | 11.2개 |

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 모이기 물러서기 (gh, stack11; 턴 단위)

- 이번: 턴 2599 · 설계 상황(팀 최장(기보, 이 드래곤 아님)이 맨해튼 6 안) 40% (기준 ≥95%) · 이 드래곤이 팀 최장 5% · 팀 최장까지 맨해튼 평균 9
- 상대별: proxy4_elim 715회 – · proxy4_king 833회 – · proxy4_swarm 1051회 –
- 지도별: Autarky 598회 – · Default 52회 – · Devil 14회 – · Portals 1125회 – · Prisoners Dilemma 111회 – · Queen Of Spades 27회 – · Schooltime 158회 – · Slithery Fight 460회 – · Trauma 54회 –
- 국면별: r250-349 142회 – · r350-449 1914회 – · r450+ 543회 –

## 더 긴 아군 곁 새 사망 진주 양보 (ghd, stack11; 드래곤·진주 단위)

- 이번: 진주 386개 (표식 턴 522) · 실제 사망 진주 100% (기준 ≥95%; 자연 0, 이미 없음 0) · 곁의 더 긴 아군이 먹음 45% (기준 ≥70%) · 우리 97% (표식한 드래곤 28%, 더 긴 우리 드래곤 52%, 최종 왕 계보 20%) · 상대 2% · 안 먹힘 0% · 곁의 더 긴 아군 수 평균 0.9
- 상대별: proxy4_elim 167회 42% · proxy4_king 101회 45% · proxy4_swarm 118회 50%
- 지도별: Autarky 100회 46% · Default 16회 38% · Devil 7회 43% · Portals 97회 52% · Prisoners Dilemma 46회 33% · Queen Of Spades 7회 43% · Schooltime 18회 33% · Slithery Fight 89회 46% · Trauma 6회 67%
- 국면별: r250-349 151회 40% · r350-449 220회 45% · r450+ 15회 87%

실패 사례 (212건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r328 · 드래곤 #200 L3: 진주 (51,7) 사망 진주, 곁의 더 긴 아군 0마리 → 표식한 드래곤이 먹음 (1라운드 뒤), 표식 1턴
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r347 · 드래곤 #129 L2: 진주 (16,20) 사망 진주, 곁의 더 긴 아군 0마리 → 다른 우리 드래곤이 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r364 · 드래곤 #530 L2: 진주 (4,8) 사망 진주, 곁의 더 긴 아군 1마리 → 표식한 드래곤이 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r354 · 드래곤 #170 L3: 진주 (9,6) 사망 진주, 곁의 더 긴 아군 1마리 → 표식한 드래곤이 먹음 (2라운드 뒤), 표식 2턴
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:A:1 · r347 · 드래곤 #170 L2: 진주 (40,21) 사망 진주, 곁의 더 긴 아군 0마리 → 다른 우리 드래곤이 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r335 · 드래곤 #249 L2: 진주 (13,12) 사망 진주, 곁의 더 긴 아군 0마리 → 상대가 먹음 (3라운드 뒤), 표식 1턴
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r396 · 드래곤 #231 L2: 진주 (3,1) 사망 진주, 곁의 더 긴 아군 1마리 → 표식한 드래곤이 먹음 (0라운드 뒤), 표식 1턴
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:A:1 · r327 · 드래곤 #239 L2: 진주 (4,6) 사망 진주, 곁의 더 긴 아군 1마리 → 다른 우리 드래곤이 먹음 (4라운드 뒤), 표식 2턴
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r300 · 드래곤 #112 L2: 진주 (2,6) 사망 진주, 곁의 더 긴 아군 0마리 → 다른 우리 드래곤이 먹음 (2라운드 뒤), 표식 1턴
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:A:1 · r458 · 드래곤 #57 L2: 진주 (8,7) 사망 진주, 곁의 더 긴 아군 1마리 → 다른 더 긴 우리 드래곤이 먹음 (2라운드 뒤), 표식 1턴

## 왕 떼기 (kx, stack11; 턴 단위)

- 이번: 턴 616 · 설계 상황(기보: 더 긴 우리 드래곤 없음, 적 머리 맨해튼 7 안) 58% (기준 ≥90%; 질량 장부의 왕 기준 52%) · kxm 72% · 움직인 뒤 가장 가까운 적 머리가 멀어짐 61% (kxm 턴 78%) · 표식 거리 1:5 2:30 3:82 4:193 5:124 6:116 7:66 · 10라운드 안 적 머리에 죽음 3% · 20라운드 안 갇혀 죽음 31% · 20라운드 안 탈출 분열 35% · KX 지도 밖 0턴
- 상대별: proxy4_elim 186회 – · proxy4_king 198회 – · proxy4_swarm 232회 –
- 지도별: Autarky 145회 – · Schooltime 279회 – · Slithery Fight 177회 – · Trauma 15회 –
- 국면별: r250-349 114회 – · r350-449 233회 – · r450+ 269회 –

## 끝판 창 왕 부류에게만 (lwk, stack11; 턴 단위)

- 이번: 턴 431 · 설계 상황(r430 뒤, 더 긴 우리 머리가 맨해튼 5 안) 98% (기준 모두) · r430 뒤 100% · 10라운드 뒤 몸 생존 94% · 끝까지 몸 생존 75%
- 상대별: proxy4_elim 69회 – · proxy4_king 132회 – · proxy4_swarm 230회 –
- 지도별: Autarky 88회 – · Devil 13회 – · Portals 174회 – · Queen Of Spades 14회 – · Schooltime 15회 – · Slithery Fight 116회 – · Trauma 11회 –
- 국면별: r350-449 111회 – · r450+ 320회 –

## 늦은 재분열 (lsplit, stack9)

- 이번: 분열 100% · 설계 상황(r250–339, 부모 길이 4–6, 우리 수 < 목표; 기보) 100% (기준 ≥95%) · 새끼 30라운드 안 자연 진주 ≥1 25% (기준 ≥38%) · 죽은 새끼 255마리의 떨군 진주 435개 중 우리 79% (기준 ≥85%) · ≥8 31% · 상대 15% · 새끼 10·30라운드 생존 89% · 74% · 부모 길이 평균 4.2 · r340 뒤 0회
- 비교: 분열 100% · 설계 상황(r250–339, 부모 길이 4–6, 우리 수 < 목표; 기보) 100% (기준 ≥95%) · 새끼 30라운드 안 자연 진주 ≥1 27% (기준 ≥38%) · 죽은 새끼 265마리의 떨군 진주 456개 중 우리 76% (기준 ≥85%) · ≥8 29% · 상대 18% · 새끼 10·30라운드 생존 91% · 74% · 부모 길이 평균 4.2 · r340 뒤 0회
- 상대별: proxy4_elim 99회 22% · proxy4_king 99회 24% · proxy4_swarm 86회 29%
- 지도별: Autarky 67회 30% · Default 46회 35% · Devil 2회 0% · Portals 14회 14% · Prisoners Dilemma 7회 0% · Queen Of Spades 14회 0% · Schooltime 46회 30% · Slithery Fight 51회 12% · Trauma 37회 35%
- 국면별: r250-349 284회 25%

실패 사례 (213건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r257 · 드래곤 #196 L4: 새끼 L2 · 우리 17/21마리 → 새끼 죽음 r429 희생(나이 172, 진주 2개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r258 · 드래곤 #96 L4: 새끼 L2 · 우리 10/22마리 → 새끼 죽음 r337 돌진(나이 79, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:B:1 · r312 · 드래곤 #309 L4: 새끼 L2 · 우리 5/11마리 → 새끼 죽음 r342 박힘(상대 돌진)(나이 30, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r280 · 드래곤 #420 L5: 새끼 L2 · 우리 10/11마리 → 새끼 죽음 r295 갇힘(나이 15, 진주 2개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r252 · 드래곤 #16 L4: 새끼 L2 · 우리 4/19마리 → 새끼 끝까지 생존, 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:B:1 · r322 · 드래곤 #165 L4: 새끼 L2 · 우리 10/11마리 → 새끼 죽음 r378 희생(나이 56, 진주 2개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:A:1 · r319 · 드래곤 #170 L4: 새끼 L2 · 우리 4/40마리 → 새끼 끝까지 생존, 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r287 · 드래곤 #282 L5: 새끼 L2 · 우리 15/37마리 → 새끼 죽음 r329 갇힘(나이 42, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r264 · 드래곤 #100 L4: 새끼 L2 · 우리 15/25마리 → 새끼 죽음 r315 갇힘(나이 51, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:A:1 · r268 · 드래곤 #249 L4: 새끼 L2 · 우리 17/21마리 → 새끼 죽음 r290 갇힘(나이 22, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0

## 영토 덮기 끌림 30라운드 창 (cov 창, stack9; 드래곤·창 단위)

- 이번: 창 3061개 (표식 턴 28184) · 창 30라운드 안 우리 영토 자연 진주 ≥1 29% (기준 ≥47%) · 창 안에 죽음 25% · 판 끝에 잘린 창 66 · 창을 연 표식 턴의 끝 칸이 기보 영토의 우리 쪽 87%
- 비교: 창 3048개 (표식 턴 28095) · 창 30라운드 안 우리 영토 자연 진주 ≥1 29% (기준 ≥47%) · 창 안에 죽음 26% · 판 끝에 잘린 창 61 · 창을 연 표식 턴의 끝 칸이 기보 영토의 우리 쪽 87%
- 상대별: proxy4_elim 1021회 29% · proxy4_king 1032회 30% · proxy4_swarm 1008회 28%
- 지도별: Autarky 362회 35% · Default 350회 14% · Devil 161회 40% · Portals 390회 44% · Prisoners Dilemma 105회 13% · Queen Of Spades 295회 20% · Schooltime 463회 34% · Slithery Fight 445회 30% · Trauma 421회 20% · Trophy 69회 30%
- 국면별: r0-99 785회 38% · r100-249 1042회 26% · r250-349 698회 21% · r350-449 428회 32% · r450+ 108회 20%

실패 사례 (2181건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r0 · 드래곤 #5 L3: 창 r0–r30, 표식 10턴 → 못 먹음
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r0 · 드래곤 #0 L4: 창 r0–r30, 표식 1턴 → 못 먹음
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r68 · 드래곤 #0 L2: 창 r68–r98, 표식 3턴 → 못 먹음
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r11 · 드래곤 #6 L2: 창 r11–r41, 표식 4턴 → 못 먹음
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r0 · 드래곤 #2 L3: 창 r0–r30, 표식 14턴 → 못 먹음
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r12 · 드래곤 #0 L3: 창 r12–r42, 표식 19턴 → 못 먹음
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:A:1 · r0 · 드래곤 #0 L4: 창 r0–r30, 표식 4턴 → 못 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r2 · 드래곤 #0 L2: 창 r2–r32, 표식 1턴 → 창 안에 죽음
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r74 · 드래곤 #9 L2: 창 r74–r104, 표식 31턴 → 못 먹음
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r0 · 드래곤 #0 L4: 창 r0–r30, 표식 12턴 → 못 먹음

## 국지 수 우세 박음 (lnt, stack10)

- 이번: 맞부딪힘 100% (168) · 설계 상황(기보 d3 ≥ +1이고 표적이 차례 시작에 바로 옆) 100% · 옛 규칙도 박았을 턴(o) 3% · 두 몸 진주 440개 중 20라운드 안 우리 48% · 상대 49% · 건당 net20 +0.46 · 적 길이 평균 2.7 · 우리 길이 평균 2.2
- 비교: 맞부딪힘 100% (167) · 설계 상황(기보 d3 ≥ +1이고 표적이 차례 시작에 바로 옆) 100% · 옛 규칙도 박았을 턴(o) 2% · 두 몸 진주 429개 중 20라운드 안 우리 44% · 상대 54% · 건당 net20 +0.17 · 적 길이 평균 2.6 · 우리 길이 평균 2.1
- 상대별: proxy4_elim 64회 48% · proxy4_king 48회 33% · proxy4_swarm 56회 50%
- 지도별: Autarky 5회 0% · Default 49회 51% · Devil 16회 44% · Queen Of Spades 21회 57% · Schooltime 31회 39% · Slithery Fight 35회 40% · Trauma 1회 0% · Trophy 10회 50%
- 국면별: r0-99 45회 38% · r100-249 72회 47% · r250-349 41회 44% · r350-449 9회 67% · r450+ 1회 0%

실패 사례 (93건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r46 · 드래곤 #3 L3: 표식 d3 1 · 기보 d3 1 · d8 -1 · 적 L2 → 진주 3개 중 20라운드 안 우리 0 · 상대 3, net20 -4
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r5 · 드래곤 #2 L2: 표식 d3 2 · 기보 d3 2 · d8 4 · 적 L2 → 진주 2개 중 20라운드 안 우리 0 · 상대 2, net20 -2
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r62 · 드래곤 #13 L3: 표식 d3 2 · 기보 d3 2 · d8 2 · 적 L3 → 진주 4개 중 20라운드 안 우리 2 · 상대 2, net20 0
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r202 · 드래곤 #4 L3: 표식 d3 1 · 기보 d3 1 · d8 -1 · 적 L2 → 진주 3개 중 20라운드 안 우리 0 · 상대 3, net20 -4
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:A:1 · r128 · 드래곤 #74 L2: 표식 d3 1 · 기보 d3 1 · d8 -4 · 적 L2 → 진주 2개 중 20라운드 안 우리 0 · 상대 2, net20 -2
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r100 · 드래곤 #157 L2: 표식 d3 2 · 기보 d3 2 · d8 1 · 적 L2 → 진주 2개 중 20라운드 안 우리 0 · 상대 2, net20 -2
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r76 · 드래곤 #2 L2: 표식 d3 1 · 기보 d3 1 · d8 -3 · 적 L3 → 진주 3개 중 20라운드 안 우리 0 · 상대 3, net20 -2
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:A:1 · r251 · 드래곤 #2 L2: 표식 d3 1 · 기보 d3 1 · d8 -5 · 적 L2 → 진주 2개 중 20라운드 안 우리 0 · 상대 2, net20 -2
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r5 · 드래곤 #2 L2: 표식 d3 3 · 기보 d3 3 · d8 4 · 적 L2 → 진주 2개 중 20라운드 안 우리 1 · 상대 1, net20 0
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:A:1 · r81 · 드래곤 #0 L2: 표식 d3 1 · 기보 d3 1 · d8 -1 · 적 L2 → 진주 2개 중 20라운드 안 우리 0 · 상대 2, net20 -2

## 국지 수 열세 교환 거부 (lntv, stack10)

- 이번: 거부 턴 10 · 설계 상황(기보 d3 ≤ −1) 100% · 표식 d3 = 기보 d3 100% · 10라운드 뒤 몸 생존 80% · 10라운드 안 박힘 20% · 우리 길이 평균 2.8
- 비교: 거부 턴 12 · 설계 상황(기보 d3 ≤ −1) 100% · 표식 d3 = 기보 d3 100% · 10라운드 뒤 몸 생존 83% · 10라운드 안 박힘 17% · 우리 길이 평균 3
- 상대별: proxy4_elim 2회 100% · proxy4_king 4회 50% · proxy4_swarm 4회 100%
- 지도별: Queen Of Spades 2회 100% · Schooltime 5회 80% · Slithery Fight 1회 0% · Trauma 2회 100%
- 국면별: r100-249 1회 100% · r250-349 5회 80% · r350-449 4회 75%

실패 사례 (2건 중 2건, 기보 확인용):
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r250 · 드래곤 #213 L2: 표식 d3 -2 (기보 -2) → 죽음 r250 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r357 · 드래곤 #231 L2: 표식 d3 -3 (기보 -3) → 죽음 r360 돌진, 상대 길이 12

## 거부 예외: 상대 최장일 수 있음 (kint, stack10)

- 이번: 맞부딪힘 100% (9) · 설계 상황(기보 d3 ≤ −1) 100% · 두 몸 진주 107개 중 20라운드 안 우리 12% · 상대 56% · 건당 net20 +10.44 · 적 길이 평균 19.2 · 우리 길이 평균 3.7
- 비교: 맞부딪힘 100% (7) · 설계 상황(기보 d3 ≤ −1) 100% · 두 몸 진주 79개 중 20라운드 안 우리 8% · 상대 54% · 건당 net20 +10.86 · 적 길이 평균 19 · 우리 길이 평균 2.9
- 상대별: proxy4_elim 3회 100% · proxy4_king 3회 100% · proxy4_swarm 3회 100%
- 지도별: Schooltime 7회 100% · Slithery Fight 1회 100% · Trauma 1회 100%
- 국면별: r250-349 2회 100% · r350-449 7회 100%

## 몫을 긴 아군에게 넘기지 않음 (cl, stack8; 드래곤·진주 단위)

- 이번: 진주 10774개 (표식 턴 26009; 표식 때 진주 있음 98%) · 설계 상황(자연 진주이고 우리 머리 가운데 표식한 조각만 가장 가까움) 37% · 그 드래곤이 먹음 68% (10라운드 안 67%) · 우리 팀 79% · 우리 긴 드래곤 7% · 상대 15%
- 비교: 진주 10803개 (표식 턴 25876; 표식 때 진주 있음 97%) · 설계 상황(자연 진주이고 우리 머리 가운데 표식한 조각만 가장 가까움) 37% · 그 드래곤이 먹음 67% (10라운드 안 66%) · 우리 팀 79% · 우리 긴 드래곤 7% · 상대 15%
- 상대별: proxy4_elim 3751회 68% · proxy4_king 3521회 68% · proxy4_swarm 3502회 67%
- 지도별: Autarky 2174회 94% · Default 742회 69% · Devil 423회 73% · Portals 1080회 61% · Prisoners Dilemma 1688회 97% · Queen Of Spades 757회 49% · Schooltime 1438회 46% · Slithery Fight 1568회 34% · Trauma 676회 55% · Trophy 228회 63%
- 국면별: r0-99 2728회 65% · r100-249 3442회 67% · r250-349 2118회 69% · r350-449 1914회 69% · r450+ 572회 76%

실패 사례 (3412건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r4 · 드래곤 #3 L3: 진주 (35,16) 우리 거리 5 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r4 · 드래곤 #12 L2: 진주 (10,29) 우리 거리 99 → 상대가 먹음
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r22 · 드래곤 #2 L2: 진주 (14,8) 우리 거리 6 → 상대가 먹음
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r10 · 드래곤 #6 L2: 진주 (15,1) 우리 거리 4 → 다른 우리 드래곤이 먹음
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r152 · 드래곤 #34 L3: 진주 (12,11) 우리 거리 5 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r16 · 드래곤 #2 L2: 진주 (6,33) 우리 거리 4 → 다른 우리 드래곤이 먹음
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:A:1 · r29 · 드래곤 #2 L2: 진주 (10,39) 우리 거리 99 → 상대가 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r1 · 드래곤 #12 L2: 진주 (21,1) 우리 거리 3 → 다른 우리 드래곤이 먹음
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r27 · 드래곤 #6 L3: 진주 (6,6) 우리 거리 99 → 상대가 먹음
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r33 · 드래곤 #4 L2: 진주 (11,10) 우리 거리 99 → 다른 우리 드래곤이 먹음

## 수 바닥 분열 (split floor, stack7)

- 이번: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 76% · 적 머리가 7×7 시야 안 44% · 부모 길이 평균 4.9 · 우리 수(표식) 평균 2.4 · 상대 수 평균 19.7 · 새끼 10라운드 생존 84% · 30라운드 64% · 부모 10라운드 생존 84% · 30라운드 68% · 새끼 30라운드 안 1개 이상 먹음 52% · 30라운드 뒤 가족 길이 변화 0.7 · 30라운드 안 새끼가 죽은 원인: 갇힘 4, 아군 머리 1, 박힘(상대 돌진) 2, 희생 2
- 비교: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 74% · 적 머리가 7×7 시야 안 43% · 부모 길이 평균 4.9 · 우리 수(표식) 평균 2.3 · 상대 수 평균 20.2 · 새끼 10라운드 생존 87% · 30라운드 70% · 부모 10라운드 생존 91% · 30라운드 70% · 새끼 30라운드 안 1개 이상 먹음 65% · 30라운드 뒤 가족 길이 변화 0.8 · 30라운드 안 새끼가 죽은 원인: 박힘(상대 돌진) 2, 갇힘 3, 희생 2
- 상대별: proxy4_elim 13회 69% · proxy4_king 6회 50% · proxy4_swarm 6회 67%
- 지도별: Default 3회 33% · Devil 15회 53% · Queen Of Spades 4회 100% · Schooltime 2회 100% · Trophy 1회 100%
- 국면별: r0-99 2회 100% · r100-249 3회 67% · r250-349 3회 67% · r350-449 17회 59%

실패 사례 (9건 중 9건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r427 · 드래곤 #129 L6: 우리 3마리 · 상대 19마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r429 갇힘, 부모 10라운드 생존 · 표식 map=Default/a
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r201 · 드래곤 #81 L4: 우리 3마리 · 상대 45마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r212 박힘(상대 돌진), 상대 길이 3, 부모 10라운드 생존 · 표식 map=Devil/a
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:A:1 · r388 · 드래곤 #82 L4: 우리 2마리 · 상대 6마리 · 새끼 L2 → 새끼 죽음 r392 갇힘, 상대 길이 6, 부모 10라운드 생존 (설계 밖: 상대 < 8마리) · 표식 map=Devil/a
- proxy4_elim · Devil · 게임 exp/stack11-a-px4:proxy4_elim:devil:A:1 · r304 · 드래곤 #167 L4: 우리 2마리 · 상대 51마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r308 박힘(상대 돌진), 상대 길이 3, 부모 10라운드 생존 · 표식 map=Devil/a
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r449 · 드래곤 #129 L5: 우리 3마리 · 상대 10마리 · 새끼 L2 → 새끼 죽음 r479 아군 머리, 상대 길이 14, 부모 10라운드 생존 · 표식 map=Default/a
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:A:1 · r433 · 드래곤 #82 L8: 우리 2마리 · 상대 4마리 · 새끼 L2 → 새끼 죽음 r457 희생, 부모 10라운드 죽음 (설계 밖: 상대 < 8마리) · 표식 map=Devil/a
- proxy4_elim · Devil · 게임 exp/stack11-a-px4:proxy4_elim:devil:B:1 · r374 · 드래곤 #486 L4: 우리 2마리 · 상대 9마리 · 새끼 L2 → 새끼 죽음 r385 희생, 부모 10라운드 생존 · 표식 map=Devil/a
- proxy4_elim · Devil · 게임 exp/stack11-a-px4:proxy4_elim:devil:B:1 · r418 · 드래곤 #502 L10: 우리 3마리 · 상대 3마리 · 새끼 L2 → 새끼 죽음 r419 갇힘, 부모 10라운드 생존 (설계 밖: 상대 < 8마리) · 표식 map=Devil/a
- proxy4_elim · Devil · 게임 exp/stack11-a-px4:proxy4_elim:devil:B:1 · r425 · 드래곤 #503 L5: 우리 3마리 · 상대 3마리 · 새끼 L2 → 새끼 죽음 r450 갇힘, 상대 길이 15, 부모 10라운드 생존 (설계 밖: 상대 < 8마리) · 표식 map=Devil/a

## 왕 길이 상한 분열 (split kcap, stack7)

- 이번: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 0% · 부모 길이 평균 7 · 우리 수(표식) 평균 3 · 상대 수 평균 5 · 새끼 10라운드 생존 100% · 30라운드 100% · 부모 10라운드 생존 100% · 30라운드 0% · 새끼 30라운드 안 1개 이상 먹음 100% · 30라운드 뒤 가족 길이 변화 -1 · 30라운드 안 새끼가 죽은 원인: 없음
- 비교: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 0% · 부모 길이 평균 7 · 우리 수(표식) 평균 3 · 상대 수 평균 5 · 새끼 10라운드 생존 100% · 30라운드 100% · 부모 10라운드 생존 100% · 30라운드 0% · 새끼 30라운드 안 1개 이상 먹음 100% · 30라운드 뒤 가족 길이 변화 -1 · 30라운드 안 새끼가 죽은 원인: 없음
- 상대별: proxy4_swarm 1회 100%
- 지도별: Trophy 1회 100%
- 국면별: r0-99 1회 100%

## 지도·판본 인식 (map=, cand-mapid; 판 단위)

- 이번: 판본을 기보로 가릴 수 있는 판 60/60 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 94%, 그중 정답 100% · 프로세스 5723: 표식 없음 3, 결정 5694 (정답 100%, 틀림 0), 가족만 25, 모름 1, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 177라운드
- 비교: 판본을 기보로 가릴 수 있는 판 60/60 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 94%, 그중 정답 100% · 프로세스 5722: 표식 없음 4, 결정 5694 (정답 100%, 틀림 0), 가족만 23, 모름 1, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 195라운드
- 상대별: proxy4_elim 20회 100% · proxy4_king 20회 100% · proxy4_swarm 20회 100%
- 지도별: Autarky a 6회 100% · Default a 6회 100% · Devil a 6회 100% · Portals a 6회 100% · Prisoners Dilemma a 6회 100% · Queen Of Spades a 6회 100% · Schooltime a 6회 100% · Slithery Fight a 6회 100% · Trauma a 6회 100% · Trophy a 6회 100%
- 국면별: r0-99 60회 100%

## 덮기 분열 (csplit, stack5)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 35% · 부모가 스스로 최장이라 믿음(k) 68% · 새끼 30라운드 안 자연 진주 ≥1 38% (500형 37% · 전멸형 39%; 기준 ≥45%) · 새끼 30라운드 생존 73% (500형 79% · 전멸형 65%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 80% · 새끼 30라운드 안 자연 진주 평균 0.7 · 30라운드 안 죽은 원인: 갇힘 176, 박힘(상대 돌진) 49, 돌진 46, 아군 머리 9
- 비교: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 36% · 부모가 스스로 최장이라 믿음(k) 69% · 새끼 30라운드 안 자연 진주 ≥1 38% (500형 37% · 전멸형 39%; 기준 ≥45%) · 새끼 30라운드 생존 74% (500형 79% · 전멸형 66%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 79% · 새끼 30라운드 안 자연 진주 평균 0.7 · 30라운드 안 죽은 원인: 박힘(상대 돌진) 48, 돌진 44, 갇힘 175, 아군 머리 9
- 상대별: proxy4_elim 371회 38% · proxy4_king 347회 37% · proxy4_swarm 332회 37%
- 지도별: Autarky 115회 35% · Default 166회 39% · Devil 78회 31% · Portals 77회 47% · Prisoners Dilemma 44회 45% · Queen Of Spades 97회 40% · Schooltime 153회 41% · Slithery Fight 184회 33% · Trauma 75회 29% · Trophy 61회 39%
- 국면별: r0-99 488회 42% · r100-249 562회 34%

실패 사례 (656건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r50 · 드래곤 #7 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r1 · 드래곤 #0 L4: 새끼 L2, 적 머리 시야 안 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r5 · 드래곤 #4 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r33 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r15 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r3 · 드래곤 #33 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r28 · 드래곤 #0 L5: 새끼 L2 → 새끼 죽음 r40 갇힘, 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0

## 샘 지킴 (F, stack5; 드래곤·샘 단위)

- 이번: 목표 1009개(표식 턴 10594) · 설계 상황 79% (실제 샘 100%, 우리 영토 100%, 처음에 다른 우리 머리 3걸음 안 없음 80%; 기준 ≥80%) · 3걸음 안 도착 58% · 도착 뒤 30라운드 그 무리 자연 진주 2400개 중 우리 91% · 상대 8% (합산 기준 ≥85%) · 처음 거리 평균 3.3
- 비교: 목표 1004개(표식 턴 10594) · 설계 상황 79% (실제 샘 100%, 우리 영토 100%, 처음에 다른 우리 머리 3걸음 안 없음 80%; 기준 ≥80%) · 3걸음 안 도착 58% · 도착 뒤 30라운드 그 무리 자연 진주 2408개 중 우리 91% · 상대 8% (합산 기준 ≥85%) · 처음 거리 평균 3.3
- 상대별: proxy4_elim 346회 95% · proxy4_king 357회 84% · proxy4_swarm 306회 91%
- 지도별: Autarky 20회 – · Devil 56회 81% · Portals 504회 100% · Prisoners Dilemma 58회 100% · Schooltime 10회 – · Slithery Fight 293회 51% · Trauma 68회 82%
- 국면별: r0-99 332회 82% · r100-249 427회 93% · r250-349 250회 97%

실패 사례 (46건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r23 · 드래곤 #2 L2: 샘 (14,8) 처음 거리 5 → r40 도착, 30라운드 무리 진주 6개 중 우리 0 · 상대 6
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r0 · 드래곤 #8 L5: 샘 (33,2) 처음 거리 0 → r0 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_swarm · Portals · 게임 exp/stack11-a-px4:proxy4_swarm:portals:B:1 · r306 · 드래곤 #398 L4: 샘 (4,7) 처음 거리 0 → r306 도착, 30라운드 무리 진주 7개 중 우리 5 · 상대 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_swarm:slithery_fight:A:1 · r0 · 드래곤 #8 L5: 샘 (33,2) 처음 거리 0 → r0 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_swarm · Trauma · 게임 exp/stack11-a-px4:proxy4_swarm:trauma:A:1 · r333 · 드래곤 #140 L3: 샘 (11,10) 처음 거리 3 → r333 도착, 30라운드 무리 진주 3개 중 우리 0 · 상대 0
- proxy4_elim · Devil · 게임 exp/stack11-a-px4:proxy4_elim:devil:B:1 · r51 · 드래곤 #1 L2: 샘 (20,0) 처음 거리 5 → r52 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2
- proxy4_elim · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_elim:slithery_fight:A:1 · r0 · 드래곤 #8 L5: 샘 (33,2) 처음 거리 0 → r0 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r103 · 드래곤 #0 L3: 샘 (8,0) 처음 거리 6 → r106 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r194 · 드래곤 #81 L2: 샘 (5,15) 처음 거리 6 → r196 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r9 · 드래곤 #26 L2: 샘 (30,1) 처음 거리 3 → r9 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2

## 영토 덮기 끌림 (cov, stack5)

- 이번: 턴 28184 · 20라운드 안 우리 영토 자연 진주 먹음 20%
- 비교: 턴 28095 · 20라운드 안 우리 영토 자연 진주 먹음 20%
- 상대별: proxy4_elim 9581회 20% · proxy4_king 9314회 21% · proxy4_swarm 9289회 19%
- 지도별: Autarky 2776회 29% · Default 3823회 12% · Devil 1615회 22% · Portals 1482회 34% · Prisoners Dilemma 1150회 7% · Queen Of Spades 3344회 15% · Schooltime 5227회 28% · Slithery Fight 3693회 22% · Trauma 4320회 11% · Trophy 754회 30%
- 국면별: r0-99 6984회 31% · r100-249 9655회 17% · r250-349 6119회 11% · r350-449 4416회 23% · r450+ 1010회 16%

실패 사례 (22496건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r0 · 드래곤 #5 L3
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r0 · 드래곤 #0 L4
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r19 · 드래곤 #2 L3
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r11 · 드래곤 #4 L4
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r0 · 드래곤 #2 L3
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r12 · 드래곤 #0 L3
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:A:1 · r0 · 드래곤 #0 L4
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r0 · 드래곤 #6 L2
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r24 · 드래곤 #6 L2
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r0 · 드래곤 #0 L4

## 위협 모형 빈틈 (tg, stack4)

- 이번: 피함(tg) 57% · 위협 칸으로 감(tgx) 4768턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 98% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 97%) · 길이별 L2-5 10823 · L6-9 103 · L10+ 104
- 비교: 피함(tg) 57% · 위협 칸으로 감(tgx) 4754턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 98% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 97%) · 길이별 L2-5 10946 · L6-9 126 · L10+ 87
- 상대별: proxy4_elim 3499회 98% · proxy4_king 3571회 98% · proxy4_swarm 3960회 98%
- 지도별: Autarky 632회 99% · Default 2149회 98% · Devil 842회 98% · Portals 6회 100% · Queen Of Spades 1483회 99% · Schooltime 3101회 98% · Slithery Fight 1866회 99% · Trauma 161회 94% · Trophy 790회 96%
- 국면별: r0-99 1912회 98% · r100-249 4979회 98% · r250-349 2715회 98% · r350-449 1204회 100% · r450+ 220회 97%

실패 사례 (205건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r170 · 드래곤 #7 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r171 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r11 · 드래곤 #13 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r13 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r41 · 드래곤 #2 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r43 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r211 · 드래곤 #64 L3: 피함(tg), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r213 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:A:1 · r126 · 드래곤 #8 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r128 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r309 · 드래곤 #428 L2: 피함(tg), 적 머리 경로 1칸 · 맨해튼 1칸(길이 2) → 박힘 r311 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r86 · 드래곤 #45 L2: 피함(tg), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r87 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r229 · 드래곤 #118 L2: 피함(tg), 적 머리 경로 4칸 · 맨해튼 4칸(길이 2) → 박힘 r231 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:B:1 · r474 · 드래곤 #3 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r476 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r188 · 드래곤 #66 L3: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r190 박힘(상대 돌진), 상대 길이 4

## 모이기 시작 제한 (gx, stack4; 드래곤 단위)

- 이번: 드래곤 137 (표식 턴 1014) · 몸(자손 포함) 끝까지 97% (기준 ≥80%) · 드래곤 자체 끝까지 생존 60% (참고) · 뒤에 희생 먹이기(feed)로 끝남 7
- 비교: 드래곤 60 (표식 턴 313) · 몸(자손 포함) 끝까지 97% (기준 ≥80%) · 드래곤 자체 끝까지 생존 62% (참고) · 뒤에 희생 먹이기(feed)로 끝남 3
- 상대별: proxy4_elim 28회 100% · proxy4_king 52회 96% · proxy4_swarm 57회 96%
- 지도별: Autarky 60회 100% · Default 6회 83% · Portals 29회 97% · Queen Of Spades 6회 67% · Schooltime 19회 100% · Slithery Fight 10회 100% · Trauma 7회 100%
- 국면별: r450+ 137회 97%

실패 사례 (4건 중 4건, 기보 확인용):
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:B:1 · r488 · 드래곤 #109 L8: gx 2턴 (r488–r489) → 죽음 r491 희생
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r491 · 드래곤 #76 L6: gx 4턴 (r491–r494) → 죽음 r495 희생
- proxy4_swarm · Portals · 게임 exp/stack11-a-px4:proxy4_swarm:portals:B:1 · r486 · 드래곤 #495 L6: gx 7턴 (r486–r492) → 죽음 r492 갇힘, 상대 길이 12
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:B:1 · r490 · 드래곤 #80 L4: gx 4턴 (r490–r493) → 죽음 r494 희생

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 336개 중 우리 팀 97% (지목한 아군 67%) · 상대 1% · 지목 아군 끝까지 생존 36% (그 뒤 죽은 원인: 갇힘 105, 희생 27, 돌진 5, 아군 머리 5) · 지목 아군의 몸(자손 포함)이 끝까지 삶 84% · 최종 왕 26% (최종 왕이 지목 아군의 자손 56%)
- 비교: 실행 100% · 떨군 진주 305개 중 우리 팀 99% (지목한 아군 69%) · 상대 0% · 지목 아군 끝까지 생존 44% (그 뒤 죽은 원인: 희생 28, 갇힘 77, 아군 머리 5, 돌진 1, 박힘(상대 돌진) 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 75% · 최종 왕 36% (최종 왕이 지목 아군의 자손 48%)
- 상대별: proxy4_elim 76회 96% · proxy4_king 65회 100% · proxy4_swarm 81회 96%
- 지도별: Autarky 49회 100% · Default 3회 67% · Devil 4회 100% · Portals 84회 99% · Prisoners Dilemma 2회 100% · Queen Of Spades 3회 100% · Schooltime 13회 85% · Slithery Fight 53회 96% · Trauma 11회 100%
- 국면별: r250-349 82회 100% · r350-449 106회 99% · r450+ 34회 85%

실패 사례 (6건 중 6건, 기보 확인용):
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:B:1 · r499 · 드래곤 #130 L2: #212(L11)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_swarm:slithery_fight:A:1 · r403 · 드래곤 #89 L3: #663(L40)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1; 지목 아군 r423 갇힘에 사망
- proxy4_elim · Portals · 게임 exp/stack11-a-px4:proxy4_elim:portals:A:1 · r497 · 드래곤 #586 L3: #563(L8)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_elim · Schooltime · 게임 exp/stack11-a-px4:proxy4_elim:schooltime:A:1 · r470 · 드래곤 #328 L4: #321(L11)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1; 지목 아군 r497 갇힘에 사망
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_swarm:slithery_fight:A:1 · r451 · 드래곤 #1208 L3: #1218(L31)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 1
- proxy4_elim · Schooltime · 게임 exp/stack11-a-px4:proxy4_elim:schooltime:A:1 · r490 · 드래곤 #403 L2: #430(L19)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 90% · 조각 30라운드 생존 44% · 30라운드 안 1개 이상 먹음 54% (살아서 먹음 17%) · 평생 먹은 진주 평균 4.9 · 나중에 아군을 먹임 24% (conv 8, feed 2, 분열 뒤 평균 31.8라운드) · 끝까지 생존 17% · 30라운드 안 죽은 원인: 갇힘 18, 희생 5
- 비교: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 89% · 조각 30라운드 생존 37% · 30라운드 안 1개 이상 먹음 63% (살아서 먹음 20%) · 평생 먹은 진주 평균 3.1 · 나중에 아군을 먹임 48% (conv 12, feed 10, 분열 뒤 평균 46.8라운드) · 끝까지 생존 0% · 30라운드 안 죽은 원인: 갇힘 18, 희생 10, 아군 머리 1
- 상대별: proxy4_elim 6회 17% · proxy4_king 16회 38% · proxy4_swarm 19회 37%
- 지도별: Portals 22회 32% · Schooltime 6회 50% · Slithery Fight 12회 33% · Trauma 1회 0%
- 국면별: r250-349 12회 25% · r350-449 29회 38%

실패 사례 (27건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r361 · 드래곤 #525 L12: 조각 L2 → 조각 죽음 r368 갇힘, 30라운드 안 먹은 진주 2
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r400 · 드래곤 #379 L11: 조각 L2 → 조각 죽음 r421 갇힘, 30라운드 안 먹은 진주 10
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:B:1 · r351 · 드래곤 #717 L8: 조각 L2 → 30라운드 생존, 먹은 진주 0 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_swarm · Portals · 게임 exp/stack11-a-px4:proxy4_swarm:portals:B:1 · r326 · 드래곤 #447 L9: 조각 L2 → 조각 죽음 r355 갇힘, 상대 길이 16, 30라운드 안 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_swarm:slithery_fight:A:1 · r315 · 드래곤 #734 L11: 조각 L2 → 조각 죽음 r336 갇힘, 30라운드 안 먹은 진주 5
- proxy4_elim · Portals · 게임 exp/stack11-a-px4:proxy4_elim:portals:A:1 · r391 · 드래곤 #545 L11: 조각 L2 → 조각 죽음 r399 갇힘, 30라운드 안 먹은 진주 1
- proxy4_elim · Schooltime · 게임 exp/stack11-a-px4:proxy4_elim:schooltime:A:1 · r341 · 드래곤 #147 L45: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_elim:slithery_fight:A:1 · r266 · 드래곤 #444 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Trauma · 게임 exp/stack11-a-px4:proxy4_elim:trauma:A:1 · r364 · 드래곤 #174 L7: 조각 L2 → 조각 죽음 r373 갇힘, 30라운드 안 먹은 진주 6 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r363 · 드래곤 #531 L10: 조각 L2 → 조각 죽음 r378 갇힘, 상대 길이 7, 30라운드 안 먹은 진주 0

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 2781개 (표식 턴 6901, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 1, 이미 없음 244) · 사망 진주 2536개 중 우리가 먹음 81% · 상대 17% · 아무도 안 먹음 1% · 표적으로 삼은 드래곤이 먹음 67% · 우리가 먹기까지 평균 3.3라운드 · 상대 머리가 같거나 더 가까웠던 788개: 우리 58% 대 상대 41% · 박치기 진주 546개: 우리 57% 대 상대 43% · 우리 팀 사망 진주 81% · 사망 뒤 첫 표적까지 평균 1.3라운드
- 비교: 표적 진주 2847개 (표식 턴 7305, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 0, 이미 없음 250) · 사망 진주 2597개 중 우리가 먹음 81% · 상대 17% · 아무도 안 먹음 1% · 표적으로 삼은 드래곤이 먹음 67% · 우리가 먹기까지 평균 3.5라운드 · 상대 머리가 같거나 더 가까웠던 811개: 우리 59% 대 상대 40% · 박치기 진주 537개: 우리 55% 대 상대 45% · 우리 팀 사망 진주 82% · 사망 뒤 첫 표적까지 평균 1.3라운드
- 상대별: proxy4_elim 1097회 83% · proxy4_king 827회 79% · proxy4_swarm 857회 80%
- 지도별: Autarky 330회 98% · Default 355회 79% · Devil 190회 58% · Portals 676회 98% · Prisoners Dilemma 117회 88% · Queen Of Spades 180회 60% · Schooltime 247회 61% · Slithery Fight 482회 77% · Trauma 105회 75% · Trophy 99회 64%
- 국면별: r0-99 308회 68% · r100-249 838회 79% · r250-349 675회 80% · r350-449 800회 88% · r450+ 160회 83%

실패 사례 (478건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r7 · 드래곤 #4 L2: 진주 (4,0), 우리 머리 6칸 · 상대 머리 4칸, 박치기 2라운드 뒤 → 상대가 먹음 (3라운드 뒤), 표식 4턴
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r67 · 드래곤 #4 L4: 진주 (10,11), 우리 머리 2칸 · 상대 머리 1칸, 박치기 1라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 3턴
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r477 · 드래곤 #576 L11: 진주 (11,5), 우리 머리 2칸 · 상대 머리 11칸, 우리 팀 사망 1라운드 뒤 → 아무도 안 먹음, 표식 1턴
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r206 · 드래곤 #170 L3: 진주 (15,11), 우리 머리 4칸 · 상대 머리 1칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r37 · 드래곤 #2 L2: 진주 (6,33), 우리 머리 3칸 · 상대 머리 7칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (49라운드 뒤), 표식 2턴
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:A:1 · r128 · 드래곤 #47 L2: 진주 (50,1), 우리 머리 3칸 · 상대 머리 4칸, 박치기 0라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 2턴
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r4 · 드래곤 #26 L2: 진주 (33,5), 우리 머리 5칸 · 상대 머리 10칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (58라운드 뒤), 표식 3턴
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r77 · 드래곤 #45 L2: 진주 (1,11), 우리 머리 5칸 · 상대 머리 2칸, 우리 팀 사망 0라운드 뒤 → 상대가 먹음 (8라운드 뒤), 표식 1턴
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r394 · 드래곤 #185 L3: 진주 (14,20), 우리 머리 4칸 · 상대 머리 3칸, 우리 팀 사망 0라운드 뒤 → 상대가 먹음 (5라운드 뒤), 표식 3턴
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:B:1 · r402 · 드래곤 #3 L3: 진주 (29,2), 우리 머리 5칸 · 상대 머리 3칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 2턴

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 1074 (그중 통로 고리 세대 801, 판정에서 뺌) · 고리 밖 273: 처음 거리 평균 9.6 → 최소 5.3 · 3칸 안까지 감 41% · 희생까지 함 44% · 가는 길에 죽음 23% · 끝까지 생존 33%
- 비교: 모이기 드래곤 1052 (그중 통로 고리 세대 779, 판정에서 뺌) · 고리 밖 273: 처음 거리 평균 10 → 최소 5.9 · 3칸 안까지 감 36% · 희생까지 함 58% · 가는 길에 죽음 21% · 끝까지 생존 21%
- 상대별: proxy4_elim 400회 76% · proxy4_king 351회 76% · proxy4_swarm 323회 77%
- 지도별: Autarky 435회 84% · Default 26회 64% · Devil 21회 47% · Portals 265회 86% · Prisoners Dilemma 187회 88% · Queen Of Spades 12회 67% · Schooltime 49회 50% · Slithery Fight 51회 70% · Trauma 28회 71%
- 국면별: r250-349 155회 93% · r350-449 773회 78% · r450+ 146회 49%

실패 사례 (93건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r428 · 드래곤 #281 L4: 왕까지 거리 5 → 최소 5 (1턴), 가는 길에 죽음 r429 희생
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r383 · 드래곤 #129 L4: 왕까지 거리 9 → 최소 6 (91턴), 가는 길에 죽음 r474 희생
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r386 · 드래곤 #81 L4: 왕까지 거리 13 → 최소 13 (1턴), 가는 길에 죽음 r413 돌진, 상대 길이 9
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r463 · 드래곤 #576 L11: 왕까지 거리 11 → 최소 7 (21턴)
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r350 · 드래곤 #174 L4: 왕까지 거리 8 → 최소 7 (21턴)
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:B:1 · r462 · 드래곤 #174 L11: 왕까지 거리 12 → 최소 7 (21턴)
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:A:1 · r383 · 드래곤 #284 L4: 왕까지 거리 6 → 최소 6 (2턴)
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r374 · 드래곤 #449 L4: 왕까지 거리 16 → 최소 4 (52턴), 가는 길에 죽음 r425 돌진, 상대 길이 26
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r351 · 드래곤 #248 L5: 왕까지 거리 6 → 최소 6 (1턴), 가는 길에 죽음 r417 아군 머리, 상대 길이 4
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:A:1 · r361 · 드래곤 #304 L4: 왕까지 거리 11 → 최소 10 (10턴), 가는 길에 죽음 r370 아군 머리, 상대 길이 2

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 474개 중 우리 팀 87% (지목한 아군 54%) · 상대 4% · 지목 아군 끝까지 생존 60% (그 뒤 죽은 원인: 희생 31, 갇힘 35, 돌진 2, 박힘(상대 돌진) 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 88% · 최종 왕 47% (최종 왕이 지목 아군의 자손 65%)
- 비교: 실행 100% · 떨군 진주 635개 중 우리 팀 87% (지목한 아군 56%) · 상대 7% · 지목 아군 끝까지 생존 61% (그 뒤 죽은 원인: 갇힘 39, 아군 머리 1, 희생 31, 박힘(상대 돌진) 13, 돌진 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 81% · 최종 왕 47% (최종 왕이 지목 아군의 자손 57%)
- 상대별: proxy4_elim 83회 90% · proxy4_king 54회 89% · proxy4_swarm 39회 90%
- 지도별: Autarky 47회 100% · Default 14회 79% · Devil 7회 86% · Portals 19회 89% · Prisoners Dilemma 34회 91% · Queen Of Spades 11회 55% · Schooltime 6회 100% · Slithery Fight 17회 100% · Trauma 21회 81%
- 국면별: r250-349 4회 100% · r350-449 131회 98% · r450+ 41회 63%

실패 사례 (18건 중 10건, 기보 확인용):
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r492 · 드래곤 #411 L11: #174(L22)에게 희생 → 진주 6개 중 우리 1, 지목 아군 1, 상대 2
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:B:1 · r467 · 드래곤 #55 L4: #109(L7)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2; 지목 아군 r491 희생에 사망
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:B:1 · r498 · 드래곤 #207 L3: #75(L12)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r392 · 드래곤 #147 L5: #4(L6)에게 희생 → 진주 3개 중 우리 2, 지목 아군 2, 상대 1
- proxy4_swarm · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_swarm:queen_of_spades:A:1 · r498 · 드래곤 #51 L3: #89(L6)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Trauma · 게임 exp/stack11-a-px4:proxy4_swarm:trauma:A:1 · r497 · 드래곤 #22 L5: #18(L16)에게 희생 → 진주 3개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_elim · Default · 게임 exp/stack11-a-px4:proxy4_elim:default:A:1 · r479 · 드래곤 #195 L4: #28(L2)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 1
- proxy4_elim · Devil · 게임 exp/stack11-a-px4:proxy4_elim:devil:B:1 · r497 · 드래곤 #522 L10: #527(L15)에게 희생 → 진주 5개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_elim · Portals · 게임 exp/stack11-a-px4:proxy4_elim:portals:A:1 · r436 · 드래곤 #569 L5: #565(L6)에게 희생 → 진주 3개 중 우리 0, 지목 아군 0, 상대 0; 지목 아군 r450 희생에 사망
- proxy4_elim · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_elim:prisoners_dilemma:B:1 · r486 · 드래곤 #363 L11: #173(L21)에게 희생 → 진주 6개 중 우리 2, 지목 아군 2, 상대 2; 지목 아군 r496 갇힘에 사망

## 막다른 길 한입 (pocket-eat)

- 이번: 한입 100% · 2턴 안 분열 86% · 30라운드 뒤 가족 길이 변화 7.4 (줄지 않음 86%)
- 비교: 한입 100% · 2턴 안 분열 83% · 30라운드 뒤 가족 길이 변화 7.5 (줄지 않음 83%)
- 상대별: proxy4_elim 4회 75% · proxy4_king 2회 50% · proxy4_swarm 1회 100%
- 지도별: Devil 1회 100% · Portals 5회 80% · Trauma 1회 0%
- 국면별: r0-99 4회 100% · r350-449 1회 100% · r450+ 2회 0%

실패 사례 (2건 중 2건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:B:1 · r452 · 드래곤 #653 L18: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 3
- proxy4_elim · Trauma · 게임 exp/stack11-a-px4:proxy4_elim:trauma:B:1 · r468 · 드래곤 #232 L7: 한입, 분열(새끼 L6), 30라운드 뒤 가족 길이 변화 -1

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 20% · 30라운드 뒤 가족 길이 변화 8.4
- 비교: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 97% · 새끼 자체 10라운드 생존 19% · 30라운드 뒤 가족 길이 변화 8.2
- 상대별: proxy4_elim 1432회 98% · proxy4_king 1339회 98% · proxy4_swarm 1338회 98%
- 지도별: Autarky 1536회 100% · Default 29회 86% · Devil 52회 85% · Portals 798회 94% · Prisoners Dilemma 1493회 99% · Queen Of Spades 18회 83% · Schooltime 34회 94% · Slithery Fight 90회 94% · Trauma 53회 92% · Trophy 6회 83%
- 국면별: r0-99 747회 99% · r100-249 1228회 98% · r250-349 872회 98% · r350-449 861회 98% · r450+ 401회 94%

실패 사례 (87건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r168 · 드래곤 #144 L7: 새끼 L5 → 새끼 죽음 r171 갇힘, 상대 길이 6, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r483 · 드래곤 #405 L12: 새끼 L10 → 새끼 죽음 r487 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -12
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r40 · 드래곤 #5 L4: 새끼 L2 → 새끼 죽음 r42 돌진, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r343 · 드래곤 #328 L6: 새끼 L4 → 새끼 죽음 r343 갇힘, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -6
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r392 · 드래곤 #38 L4: 새끼 L2 → 새끼 죽음 r394 갇힘, 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r183 · 드래곤 #60 L5: 새끼 L3 → 새끼 죽음 r190 박힘(상대 돌진), 상대 길이 4, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:A:1 · r49 · 드래곤 #29 L4: 새끼 L2 → 새끼 죽음 r53 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Portals · 게임 exp/stack11-a-px4:proxy4_swarm:portals:B:1 · r360 · 드래곤 #466 L6: 새끼 L4 → 새끼 죽음 r360 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -6
- proxy4_swarm · Schooltime · 게임 exp/stack11-a-px4:proxy4_swarm:schooltime:A:1 · r486 · 드래곤 #284 L4: 새끼 L2 → 새끼 죽음 r489 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_swarm:slithery_fight:A:1 · r252 · 드래곤 #476 L4: 새끼 L2 → 새끼 죽음 r254 갇힘, 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 86% · 그 밖(진짜로 갇힘) 595회
- 비교: 탈출 분열 뒤 남은 조각(고리의 일부) 86% · 그 밖(진짜로 갇힘) 598회
- 상대별: proxy4_elim 1487회 – · proxy4_king 1433회 – · proxy4_swarm 1390회 –
- 지도별: Autarky 1565회 – · Default 81회 – · Devil 55회 – · Portals 727회 – · Prisoners Dilemma 1510회 – · Queen Of Spades 44회 – · Schooltime 53회 – · Slithery Fight 162회 – · Trauma 87회 – · Trophy 26회 –
- 국면별: r0-99 790회 – · r100-249 1358회 – · r250-349 932회 – · r350-449 856회 – · r450+ 374회 –

## 정책 분열 (split)

- 이번: 분열 100% · 새끼 30라운드 생존 100% · 30라운드 뒤 가족 길이 변화 2
- 비교: 분열 100% · 새끼 30라운드 생존 100% · 30라운드 뒤 가족 길이 변화 3.3
- 상대별: proxy4_elim 1회 100% · proxy4_king 2회 100%
- 지도별: Default 1회 100% · Devil 1회 100% · Slithery Fight 1회 100%
- 국면별: r350-449 3회 100%

## 탈출 질주 3칸 (esc)

- 이번: 질주 99% · 짧은 적 머리 4칸 안 79% · 몸 생존 5라운드 97% · 10라운드 94% (드래곤 자체 89%) · 10라운드 길이 변화 -3.9
- 비교: 질주 100% · 짧은 적 머리 4칸 안 71% · 몸 생존 5라운드 96% · 10라운드 93% (드래곤 자체 91%) · 10라운드 길이 변화 -2.3
- 상대별: proxy4_elim 22회 82% · proxy4_king 24회 100% · proxy4_swarm 26회 96%
- 지도별: Autarky 1회 100% · Default 10회 100% · Prisoners Dilemma 2회 100% · Queen Of Spades 5회 80% · Schooltime 27회 89% · Slithery Fight 27회 96%
- 국면별: r0-99 5회 100% · r100-249 11회 91% · r250-349 2회 100% · r350-449 21회 86% · r450+ 33회 97%

실패 사례 (5건 중 5건, 기보 확인용):
- proxy4_swarm · Schooltime · 게임 exp/stack11-a-px4:proxy4_swarm:schooltime:A:1 · r456 · 드래곤 #224 L6: 질주 3칸 (가장 가까운 짧은 적 머리 5칸) → 죽음 r461 돌진, 상대 길이 33
- proxy4_elim · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_elim:queen_of_spades:B:1 · r196 · 드래곤 #57 L15: 질주 3칸 (가장 가까운 짧은 적 머리 2칸) → 죽음 r204 갇힘
- proxy4_elim · Schooltime · 게임 exp/stack11-a-px4:proxy4_elim:schooltime:A:1 · r427 · 드래곤 #400 L56: 질주 3칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r429 적 몸통, 상대 길이 17
- proxy4_elim · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_elim:slithery_fight:B:1 · r405 · 드래곤 #389 L12: 질주 3칸 (가장 가까운 짧은 적 머리 12칸) → 죽음 r410 갇힘, 상대 길이 9
- proxy4_elim · Schooltime · 게임 exp/stack11-a-px4:proxy4_elim:schooltime:A:1 · r429 · 드래곤 #400 L54: 질주 3칸 (가장 가까운 짧은 적 머리 2칸) → 죽음 r429 적 몸통, 상대 길이 17

## 위협 피하기 2칸 질주

- 이번: 질주 100% · 몸 10라운드 생존 92% (드래곤 자체 86%)
- 비교: 질주 100% · 몸 10라운드 생존 91% (드래곤 자체 86%)
- 상대별: proxy4_elim 196회 90% · proxy4_king 173회 92% · proxy4_swarm 216회 92%
- 지도별: Autarky 37회 92% · Default 91회 95% · Devil 50회 84% · Queen Of Spades 70회 90% · Schooltime 189회 91% · Slithery Fight 104회 93% · Trauma 22회 95% · Trophy 22회 91%
- 국면별: r0-99 117회 87% · r100-249 216회 94% · r250-349 98회 91% · r350-449 139회 91% · r450+ 15회 100%

실패 사례 (50건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r43 · 드래곤 #3 L5: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 3) → 죽음 r46 돌진, 상대 길이 2
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r218 · 드래곤 #53 L3: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 2) → 죽음 r219 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r101 · 드래곤 #26 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r110 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r360 · 드래곤 #313 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r366 돌진, 상대 길이 2
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r66 · 드래곤 #77 L4: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r73 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r85 · 드래곤 #45 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r87 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r409 · 드래곤 #172 L12: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 3) → 죽음 r416 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:B:1 · r95 · 드래곤 #74 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r96 돌진, 상대 길이 2
- proxy4_swarm · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_swarm:queen_of_spades:B:1 · r385 · 드래곤 #36 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r395 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Schooltime · 게임 exp/stack11-a-px4:proxy4_swarm:schooltime:A:1 · r146 · 드래곤 #12 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r152 갇힘, 상대 길이 3

## 포털 통과 (전체; PORTAL?=미탐색 출구)

- 이번: 미탐색 출구 1112회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 93% (드래곤 자체 77%) · 10라운드 88% · 10라운드 안 먹은 진주 0.9
- 비교: 미탐색 출구 1101회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 93% (드래곤 자체 77%) · 10라운드 87% · 10라운드 안 먹은 진주 0.9
- 상대별: proxy4_elim 812회 93% · proxy4_king 976회 94% · proxy4_swarm 709회 93%
- 지도별: Autarky 398회 96% · Default 339회 92% · Portals 1150회 92% · Prisoners Dilemma 76회 97% · Queen Of Spades 71회 86% · Schooltime 107회 94% · Slithery Fight 180회 93% · Trauma 176회 96%
- 국면별: r0-99 274회 95% · r100-249 917회 94% · r250-349 758회 94% · r350-449 448회 90% · r450+ 100회 91%

실패 사례 (169건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r166 · 드래곤 #125 L3: 포털 → 죽음 r168 갇힘, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r158 · 드래곤 #35 L3: 포털(미탐색 출구) → 죽음 r160 박힘(상대 돌진), 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r42 · 드래곤 #16 L2: 포털(미탐색 출구) → 죽음 r42 아군 머리, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r39 · 드래곤 #5 L4: 포털 → 죽음 r41 갇힘, 10라운드 안 진주 0
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r297 · 드래곤 #177 L4: 포털 → 죽음 r297 갇힘, 상대 길이 15, 10라운드 안 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r82 · 드래곤 #16 L24: 포털(미탐색 출구) → 죽음 r82 아군 머리, 상대 길이 4, 10라운드 안 진주 0
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r299 · 드래곤 #71 L3: 포털 → 죽음 r299 돌진, 상대 길이 3, 10라운드 안 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:A:1 · r238 · 드래곤 #181 L3: 포털 → 죽음 r238 아군 머리, 상대 길이 16, 10라운드 안 진주 0
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r148 · 드래곤 #33 L3: 포털(미탐색 출구) → 죽음 r149 박힘(상대 돌진), 상대 길이 3, 10라운드 안 진주 0
- proxy4_swarm · Portals · 게임 exp/stack11-a-px4:proxy4_swarm:portals:B:1 · r8 · 드래곤 #1 L3: 포털(미탐색 출구) → 죽음 r9 갇힘, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 176, 경로 37) · 잡은 길이 ≥ 우리 92% · 두 몸의 진주 우리 389 대 상대 467
- 비교: 충돌 성사 100% (인접 174, 경로 35) · 잡은 길이 ≥ 우리 92% · 두 몸의 진주 우리 312 대 상대 495
- 상대별: proxy4_elim 80회 44% · proxy4_king 60회 45% · proxy4_swarm 73회 52%
- 지도별: Autarky 5회 40% · Default 54회 54% · Devil 19회 53% · Queen Of Spades 25회 60% · Schooltime 51회 35% · Slithery Fight 44회 45% · Trauma 4회 25% · Trophy 11회 45%
- 국면별: r0-99 46회 43% · r100-249 75회 45% · r250-349 46회 46% · r350-449 40회 53% · r450+ 6회 67%

실패 사례 (113건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r46 · 드래곤 #3 L3: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 3
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r5 · 드래곤 #2 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r413 · 드래곤 #81 L7: 돌진 경로 4칸 → 상대 L9 잡음, 진주 우리 0 대 상대 8
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r202 · 드래곤 #4 L3: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 3
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:A:1 · r128 · 드래곤 #74 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r58 · 드래곤 #155 L2: 돌진 경로 2칸 → 상대 L3 잡음, 진주 우리 1 대 상대 3
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r76 · 드래곤 #2 L2: 돌진 경로 1칸 → 상대 L3 잡음, 진주 우리 0 대 상대 3
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:A:1 · r251 · 드래곤 #2 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r103 · 드래곤 #6 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:A:1 · r81 · 드래곤 #0 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 비교: 먹음 100%
- 상대별: proxy4_elim 63회 100% · proxy4_king 56회 100% · proxy4_swarm 56회 100%
- 지도별: Autarky 6회 100% · Default 27회 100% · Devil 13회 100% · Portals 29회 100% · Queen Of Spades 23회 100% · Schooltime 33회 100% · Slithery Fight 26회 100% · Trauma 5회 100% · Trophy 13회 100%
- 국면별: r0-99 29회 100% · r100-249 55회 100% · r250-349 29회 100% · r350-449 60회 100% · r450+ 2회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 91%
- 비교: 그 턴 사망 0% · 10라운드 생존 89%
- 상대별: proxy4_elim 20회 – · proxy4_king 22회 – · proxy4_swarm 13회 –
- 지도별: Autarky 2회 – · Default 4회 – · Devil 3회 – · Queen Of Spades 9회 – · Schooltime 25회 – · Slithery Fight 7회 – · Trauma 1회 – · Trophy 4회 –
- 국면별: r0-99 11회 – · r100-249 22회 – · r250-349 2회 – · r350-449 18회 – · r450+ 2회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 비교: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 5회 – · proxy4_king 7회 – · proxy4_swarm 5회 –
- 지도별: Default 1회 – · Devil 6회 – · Queen Of Spades 3회 – · Schooltime 2회 – · Slithery Fight 1회 – · Trauma 3회 – · Trophy 1회 –
- 국면별: r0-99 3회 – · r100-249 7회 – · r250-349 3회 – · r350-449 3회 – · r450+ 1회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/stack11-a-px4` | 60 | 17 (0.28) | 71% | 0 (0.00) | 0 (0.00) | 2 | 12 | 1 | 2/3 (7) | 95 (1.58; 필사 14) | 29/64 (101.5) |
| 비교 `exp/stack10-a-px4` | 60 | 20 (0.33) | 75% | 1 (0.02) | 0 (0.00) | 1 | 14 | 1 | 4/6 (14) | 99 (1.65; 필사 15) | 26/58 (91) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.
- 이번 `exp/stack11-a-px4`: gx 표식 턴 1014 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- 비교 `exp/stack10-a-px4`: gx 표식 턴 313 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/stack11-a-px4` | 60 | 38942 | 0.8% (307) | 16.0% (6226) | 4390 | 1.9% (82) | 4.0% (176) | 23.0% (1008/4390) |
| 비교 `exp/stack10-a-px4` | 60 | 36921 | 0.6% (223) | 16.4% (6047) | 4093 | 1.0% (40) | 2.8% (115) | 20.7% (846/4093) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/stack11-a-px4` | 전체 | 분열 | 5 (18%) | 10.2 | 45% | 59% | 4 | 2 |
| 이번 `exp/stack11-a-px4` | 전체 | 2칸 질주 | 5 (18%) | 14.6 | 110% | 141% | 2 | 1 |
| 이번 `exp/stack11-a-px4` | 전체 | 3칸 질주 | 6 (21%) | 17.8 | 155% | 151% | 0 | 0 |
| 이번 `exp/stack11-a-px4` | 전체 | 한 걸음 | 12 (43%) | 9.8 | 42% | 28% | 10 | 4 |
| 이번 `exp/stack11-a-px4` | 4칸 이상 | 분열 | 2 (18%) | 9.5 | 84% | 95% | 2 | 0 |
| 이번 `exp/stack11-a-px4` | 4칸 이상 | 2칸 질주 | 2 (18%) | 26 | 73% | 75% | 1 | 1 |
| 이번 `exp/stack11-a-px4` | 4칸 이상 | 3칸 질주 | 2 (18%) | 37.5 | 183% | 181% | 0 | 0 |
| 이번 `exp/stack11-a-px4` | 4칸 이상 | 한 걸음 | 5 (45%) | 9.6 | 48% | 27% | 5 | 2 |
| 비교 `exp/stack10-a-px4` | 전체 | 분열 | 3 (13%) | 10.3 | 84% | 106% | 1 | 0 |
| 비교 `exp/stack10-a-px4` | 전체 | 2칸 질주 | 3 (13%) | 17.7 | 83% | 74% | 1 | 0 |
| 비교 `exp/stack10-a-px4` | 전체 | 3칸 질주 | 2 (9%) | 10 | 100% | 95% | 0 | 0 |
| 비교 `exp/stack10-a-px4` | 전체 | 한 걸음 | 15 (65%) | 11.1 | 33% | 26% | 12 | 6 |
| 비교 `exp/stack10-a-px4` | 4칸 이상 | 분열 | 1 (13%) | 13 | 85% | 77% | 1 | 0 |
| 비교 `exp/stack10-a-px4` | 4칸 이상 | 2칸 질주 | 1 (13%) | 40 | 95% | 98% | 0 | 0 |
| 비교 `exp/stack10-a-px4` | 4칸 이상 | 한 걸음 | 6 (75%) | 12 | 25% | 14% | 6 | 4 |

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (95건 중 10건):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r253 · 드래곤 #75 L3: v7.9 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r276 · 드래곤 #65 L2: v8.1 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r328 · 드래곤 #198 L3: v9.8 PORTAL? → 아군 머리, 막은 우리 드래곤 L4
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:A:1 · r239 · 드래곤 #205 L3: v7.9 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:A:1 · r308 · 드래곤 #252 L3: v8.6 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:A:1 · r338 · 드래곤 #154 L2: v8.2 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:A:1 · r374 · 드래곤 #306 L3: v7.4 → 아군 머리, 막은 우리 드래곤 L4
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r248 · 드래곤 #58 L3: v7.4 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r250 · 드래곤 #89 L3: v6.9 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r351 · 드래곤 #171 L3: v2.6 PORTAL? → 아군 머리, 막은 우리 드래곤 L3

## 지도·판본 인식 상세 (cand-mapid)

이번 (60판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 6 | 100% | 100% | 36/36 (36) | 1754 | 1754 (0) | 0 | 0 | 0 | 0 |
| Default a | 6 | 100% | 100% | 24/24 (24) | 269 | 268 (0) | 0 | 0 | 0 | 0 |
| Devil a | 6 | 100% | 100% | 18/18 (18) | 166 | 164 (0) | 1 | 1 | 0 | 19 |
| Portals a | 6 | 100% | 100% | 18/18 (18) | 929 | 929 (0) | 0 | 0 | 0 | 1 |
| Prisoners Dilemma a | 6 | 100% | 100% | 6/18 (6) | 1562 | 1555 (0) | 7 | 0 | 0 | 177 |
| Queen Of Spades a | 6 | 100% | 100% | 12/12 (12) | 145 | 140 (0) | 4 | 0 | 0 | 29 |
| Schooltime a | 6 | 100% | 100% | 18/18 (18) | 259 | 259 (0) | 0 | 0 | 0 | 16 |
| Slithery Fight a | 6 | 100% | 100% | 48/48 (48) | 380 | 367 (0) | 13 | 0 | 0 | 56 |
| Trauma a | 6 | 100% | 100% | 12/12 (12) | 178 | 178 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 6 | 100% | 100% | 12/12 (12) | 81 | 80 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 60/60, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

비교 (60판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 6 | 100% | 100% | 36/36 (36) | 1749 | 1749 (0) | 0 | 0 | 0 | 0 |
| Default a | 6 | 100% | 100% | 24/24 (24) | 258 | 257 (0) | 0 | 0 | 0 | 0 |
| Devil a | 6 | 100% | 100% | 18/18 (18) | 164 | 162 (0) | 1 | 1 | 0 | 19 |
| Portals a | 6 | 100% | 100% | 18/18 (18) | 949 | 949 (0) | 0 | 0 | 0 | 1 |
| Prisoners Dilemma a | 6 | 100% | 100% | 6/18 (6) | 1534 | 1526 (0) | 8 | 0 | 0 | 195 |
| Queen Of Spades a | 6 | 100% | 100% | 12/12 (12) | 147 | 141 (0) | 5 | 0 | 0 | 29 |
| Schooltime a | 6 | 100% | 100% | 18/18 (18) | 287 | 286 (0) | 0 | 0 | 0 | 16 |
| Slithery Fight a | 6 | 100% | 100% | 48/48 (48) | 377 | 368 (0) | 9 | 0 | 0 | 48 |
| Trauma a | 6 | 100% | 100% | 12/12 (12) | 176 | 176 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 6 | 100% | 100% | 12/12 (12) | 81 | 80 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 60/60, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

### Schooltime 판의 경제 (bsp의 가설 수준 지표, 정답 판본별)

| 묶음 | 판본 | 판 | 드래곤 수 r50 | r100 | r0–99 자연 진주 먹음 | 전멸당함 | 끝 최장(전멸 0) | 판당 bsp 분열 |
|---|---|---:|---|---|---|---:|---|---:|
| 이번 | a | 6 | 9 [8, 10] | 15 [13, 16] | 30 [22, 48] | 0% | 29 [15, 34] | 0 |
| 비교 | a | 6 | 9 [8, 10] | 15 [13, 16] | 30 [22, 48] | 0% | 23 [9, 34] | 0 |

- 기준값(`research/experiments/cand-mapid.md`, 웨이브 전에 적음): b에서 드래곤 수 r50 중앙 ≥ 6, r0–99 자연 진주 중앙 ≥ 14. 우리 merge2 계열 b 29판은 3 · 9, 떼 계열(swarm8·px) b 14판은 6 · 14, 상위권 b 승자는 8 · 32다. a는 bsp가 켜지지 않는 대조군이다.

## stack5: 영토 덮기 (csplit · F · cov) 게이트와 가설 수준 지표

- 기준값은 `research/experiments/cand-stack5.md`(웨이브 전)에서, 상위권 승자(TW) 값과 merge2 값은 `research/observations/top-territory.md`에서 왔다. 정의는 영토 연구의 `exp/territory-analysis/extract.js`와 같다(영토 = 시작 몸에서 더 가까운 팀의 칸, 샘 = 그 판 판본 파일의 평균 간격 ≤12, 보로노이 = 용량 1/평균 간격 가중, 거리 = 지도 위 이동 거리, 몸은 무시).

### 게이트 (기능 적용)

| 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|
| csplit 발동: 500라운드형 지도 r0–249 판당 | ≥20 | 20.1 (전체 1050회) | 20.1 (전체 1051회) |
| csplit 설계 상황: 부모가 팀 최장(≥8)이 아님 | ≥90% | 100% | 100% |
| csplit 새끼가 30라운드 안에 자연 진주 ≥1개 | ≥45% (TW 47% · 45%) | 38% (1050마리) | 38% (1051마리) |
| csplit 새끼 30라운드 생존 | ≥30% (TW 34% · 51%) | 73% | 74% |
| F 목표(드래곤·샘) 수, 3걸음 안 도착 | – | 1009, 도착 58% | 1004, 도착 58% |
| F 설계 상황: 실제 우리 영토 샘, 처음 표식 때 다른 우리 머리 3걸음 안 없음 | ≥80% | 79% | 79% |
| F 도착 뒤 30라운드 그 무리 자연 진주의 우리 몫(합산) | ≥85% (TW 자기 샘 90%) | 91% (상대 8%, 2400개) | 91% (상대 8%, 2408개) |
| F 같은 몫의 지도 평균(지도마다 합산, 같은 무게, Portals 제외) | ≥85% | 84% (Devil 82%, Prisoners Dilemma 100%, Slithery Fight 61%, Trauma 94%) | 84% (Devil 82%, Prisoners Dilemma 100%, Trauma 94%, Slithery Fight 61%) |
| cov 턴, 20라운드 안 우리 영토 자연 진주 | – | 28184, 20% | 28095, 20% |

### 가설 수준 지표 (관찰; 500라운드형 / 전멸형)

| 지표 | 기준 | 상위권 승자 | merge2 | 이번 | 비교 |
|---|---|---|---|---|---|
| r100 우리 드래곤 수(r100까지 간 판) | ≥15 / ≥10 | 30 / 21 | 4 / 3 | 11.4 / 6 | 11.4 / 6 |
| r100 우리 영토 보로노이 몫(용량 가중, 판 평균) | ≥80% | 89% / 81% | 66% / 32% | 65% / 36% | 65% / 36% |
| r100 샘 지킴: 우리 영토 샘 중 우리 머리 3걸음 안(판 평균) | ≥50% | 61% / 55% | 22% / – | 27% / 61% | 27% / 61% |
| 우리 영토 자연 진주(r0부터 생성)를 상대가 먹은 몫(합산) | ≤25% | 11% / 16% | 56% / 55% | 58% / 58% | 57% / 58% |
| 우리 영토 샘 진주를 상대가 먹은 몫(합산) | ≤15% | 7% / 6% | 50% / 33% | 52% / 41% | 52% / 42% |

- 판 수(500라운드형 / 전멸형): 이번 30 / 30 · 비교 30 / 30. 판본 파일을 못 찾은 판: 이번 0 · 비교 0.

### 부작용: 우리 드래곤의 죽음 (판당; 전체 / r250 전)

| 원인 | 이번 | 비교 |
|---|---|---|
| 갇힘(빈 이웃 없음; 통로 고리의 남은 조각 포함) | 72.7 / 36 | 72.7 / 36 |
| 적 머리에 박힘 | 6.6 / 4.8 | 6.6 / 4.6 |
| 우리 드래곤끼리 머리 충돌(둘 다 죽음, 둘 다 셈) | 2.1 / 0.9 | 2.2 / 0.9 |

- 막힘에서 아군 머리를 피해 죽은 턴(no-exit s): 이번 115 · 비교 108

### 지도별 (이번)

| 지도 | 판 | csplit 판당 | 새끼 먹음 ≥1 | 새끼 30R 생존 | F 목표 · 도착 · 무리 진주 우리 몫 | r100 드래곤 | 보로노이 | 샘 지킴 | 상대가 먹은 영토 진주 | 상대가 먹은 샘 진주 |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| Autarky | 6 | 19.2 | 35% | 92% | 20 · 0% · – | 9.7 | 96% | 86% | 8% | 8% |
| Default | 6 | 27.7 | 39% | 58% | 0 · – · – | 10.3 | 25% | – | 78% | – |
| Devil | 6 | 13 | 31% | 69% | 56 · 46% · 82% | 6.7 | 29% | 22% | 82% | 84% |
| Portals | 6 | 12.8 | 47% | 56% | 504 · 76% · 100% | 10.8 | 100% | 35% | 0% | 0% |
| Prisoners Dilemma | 6 | 7.3 | 45% | 91% | 58 · 45% · 100% | 3.7 | 99% | 100% | 2% | 0% |
| Queen Of Spades | 6 | 16.2 | 40% | 67% | 0 · – · – | 3.8 | 12% | – | 72% | – |
| Schooltime | 6 | 25.5 | 41% | 86% | 10 · 0% · – | 14.5 | 15% | 0% | 80% | 88% |
| Slithery Fight | 6 | 30.7 | 33% | 80% | 293 · 43% · 61% | 16.8 | 23% | 2% | 81% | 86% |
| Trauma | 6 | 12.5 | 29% | 71% | 68 · 31% · 94% | 5.3 | 92% | 11% | 58% | 0% |
| Trophy | 6 | 10.2 | 39% | 56% | 0 · – · – | 5.5 | 18% | – | 71% | – |

## stack7: 수 바닥 분열(floor)과 왕 길이 상한(kcap) 게이트, 저수 에피소드, 가설 수준 지표, 지도 가르기

- 기준값은 `research/experiments/cand-stack7.md`(웨이브 전)에서, 상위권·우리 값은 `research/observations/our-eliminations.md`(2.6절, 1.3절, 2.2절)에서 왔다. 저수 에피소드와 부류의 정의는 전멸 연구(`exp/eliminations/top.js` I, `lib.js` classOf)와 같다: r50부터 5라운드 간격으로 처음 우리 수 1–3·상대 ≥8인 라운드 r(라운드 첫 턴의 수; r+20이 판 안이고 우리 전멸 전), 그 뒤 [r, r+20) 분열, 20라운드 뒤 4마리 이상이면 회복, 50라운드 안 전멸. 연구의 분열 수는 10라운드 칸 두 개의 전체 분열(탈출 분열 포함)이고, 여기서는 [r, r+20)을 그대로 센다.

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| floor | 발동(판당; floor 지도 판) | – | 25 (0.6; 42판) | 23 (0.5; 42판) |
| floor | 1. 설계 상황: 발동 때 상대 ≥8마리 | ≥90% | 76% | 74% |
| floor | 저수 에피소드가 있는 floor 지도 판 · 그 20라운드 안 floor 발동이 있었던 판 | (관찰) | 26 · 8% | 30 · 3% |
| floor | 2. 즉시 효과 A: 에피소드 20라운드 비탈출 분열(판당; floor 지도) | ≥2.0 (상위 LX·LS 2.0, 우리 0.5) | 0.2 (floor 0.1, kcap 0, csplit 0.2, lsplit 0; 탈출 포함 전체 0.3) | 0.2 (floor 0, kcap 0, csplit 0.1, lsplit 0; 탈출 포함 전체 0.2) |
| floor | 3. 즉시 효과 B: 에피소드 20라운드 뒤 4마리 이상(floor 지도) | ≥23% (상위 LX 23%, LS 26%, 우리 5%) | 8% (2/26) | 3% (1/30) |
| floor | 4. 즉시 효과 C: floor 새끼 30라운드 생존 | ≥34% (상위 패자 제 영토 새끼 34%, 승자 51%) | 64% (25마리) | 70% (23마리) |
| kcap | 발동(판당; kcap 지도 판) | – | 1 (0; 36판) | 1 (0; 36판) |
| kcap | 1. 설계 상황: 부모가 그 순간 팀 최장이고 r250 전 | ≥90% | 100% | 100% |
| kcap | 2. 즉시 효과: 새끼 10라운드 생존 | ≥74% (상위권 길이 4 분열 74.2%) | 100% (1마리) | 100% (1마리) |
| kcap | 2. 즉시 효과: 부모 10라운드 생존 | ≥55% (상위권 54.5%) | 100% | 100% |

### 저수 에피소드 (floor 지도 / 모든 지도; 판정은 floor 지도)

| 묶음 | 지도 | 판 | 에피소드 있음 | 처음 라운드(중앙) | 그때 우리 수 · 상대 수 | 그때 총길이 · 최장 | 20라운드 비탈출 분열 | floor · kcap | 탈출 포함 전체 | 20라운드 뒤 4마리 이상 | 50라운드 안 전멸 |
|---|---|---:|---:|---:|---|---|---:|---|---:|---:|---:|
| 이번 | floor 지도 | 42 | 62% | 172.5 | 2.9 · 29.4 | 12.6 · 7 | 0.2 | 0.1 · 0 | 0.3 | 8% | 12% |
| 이번 | floor 지도 중 전멸형 | 24 | 79% | 140 | 2.8 · 30.2 | 8.1 · 3.5 | 0.3 | 0.1 · 0 | 0.4 | 11% | 16% |
| 이번 | floor 지도 중 500형 | 18 | 39% | 430 | 3 · 27.4 | 24.9 · 16.4 | 0 | 0 · 0 | 0.1 | 0% | 0% |
| 이번 | 끄는 지도(Autarky·PD·Portals) | 18 | 44% | 405 | 2.9 · 17.5 | 28.9 · 15.3 | 0 | 0 · 0 | 10 | 0% | 0% |
| 이번 | 모든 지도 | 60 | 57% | 312.5 | 2.9 · 26.6 | 16.4 · 8.9 | 0.2 | 0.1 · 0 | 2.6 | 6% | 9% |
| 비교 | floor 지도 | 42 | 71% | 230 | 2.9 · 28.1 | 13.4 · 7 | 0.2 | 0 · 0 | 0.2 | 3% | 10% |
| 비교 | floor 지도 중 전멸형 | 24 | 88% | 160 | 2.9 · 29.4 | 8.3 · 3.7 | 0.2 | 0 · 0 | 0.3 | 5% | 14% |
| 비교 | floor 지도 중 500형 | 18 | 50% | 430 | 2.9 · 25 | 25.4 · 14.9 | 0 | 0 · 0 | 0 | 0% | 0% |
| 비교 | 끄는 지도(Autarky·PD·Portals) | 18 | 61% | 420 | 2.7 · 22.1 | 30.3 · 16.7 | 0 | 0 · 0 | 9.1 | 0% | 0% |
| 비교 | 모든 지도 | 60 | 68% | 380 | 2.8 · 26.5 | 18 · 9.6 | 0.1 | 0 · 0 | 2.6 | 2% | 7% |

- 상위권 기준(전멸 연구 2.6절, 전멸형): LX 72%가 그런 때를 겪고(처음 r105) 20라운드에 2.0번 나누며 23%가 회복, 42%가 50라운드 안 전멸. LS 69%, 2.0번, 26%, 0%. 우리 g4 LX 95%(r50), 0.5번, 5%, 15%.

### 가설 수준 지표 (관찰)

| 기능 | 지표 | 기준 | 상위권 · 이전 우리 | 이번 | 비교 |
|---|---|---|---|---|---|
| floor | r100 우리 드래곤 수(전멸형; 전멸은 0) — 전멸형 5지도 / PD 뺀 4지도 | ≥5.5 | 상위 LX 5.5, 우리 g4 LX 2.5 | 6 / 6.6 | 6 / 6.5 |
| floor | 전멸률(전멸형) | ≤66% | swarm8 66%, merge2 78% | 27% (8/30) / 33% (8/24) | 30% (9/30) / 33% (8/24) |
| floor | 전멸 라운드 중앙(전멸형) | ≥r235 | swarm8 235, merge2 150, stack1–3 163 | 170.5 / 170.5 | 177 / 170.5 |
| kcap | 우리 전멸 중 E2(왕 사냥) 비율(모든 지도) | ≤8% | 상위 LX 6%, 우리 16% | 0% (E1 0 · E2 0 · E3m 6 · E3l 2) | 11% (E1 0 · E2 1 · E3m 6 · E3l 2) |
| kcap | r50 우리 최장 평균(전멸형; 전멸은 0) — 5지도 / 4지도 | ≤4.5 | 상위 LS 3.8, 우리 g4 LX 6.8 | 4.8 / 3.2 | 4.8 / 3.2 |
| kcap | 전멸한 판의 길이 ≥8 죽음(판당; 모든 지도) | ≤0.4 | 우리 0.75 | 0 (8판) | 0.3 (9판) |

### 지도 가르기 (map= 표식으로 확인)

- floor는 Trophy, Queen Of Spades, Devil, Default, Schooltime, Trauma, Slithery Fight에서만, kcap은 그중 Slithery Fight를 뺀 여섯에서만 켠다. 봇은 프로세스마다 자기 창으로 지도 가족을 인식하고(`map=` 표식), 인식 전·`none`이면 끈다. "표식이 켜는 가족이 아닌 발동"은 발동한 프로세스의 마지막 `map=` 표식이 그 기능을 켜는 가족을 대지 않은 발동이다(0이어야 한다). "인식한 프로세스"는 마지막 표식이 그 판의 참 지도 가족을 댄 프로세스다.

| 묶음 | 지도(정답 판본) | 판 | floor 발동 | kcap 발동 | 표식이 켜는 가족이 아닌 발동 | 인식한 프로세스 |
|---|---|---:|---:|---:|---:|---:|
| 이번 | Autarky (끔) | 6 | 0 | 0 | 0 | 100% (1754/1754) |
| 이번 | Default | 6 | 3 | 0 | 0 | 100% (268/269) |
| 이번 | Devil a | 6 | 15 | 0 | 0 | 99% (165/166) |
| 이번 | Portals (끔) | 6 | 0 | 0 | 0 | 100% (929/929) |
| 이번 | Prisoners Dilemma (끔) | 6 | 0 | 0 | 0 | 100% (1562/1562) |
| 이번 | Queen Of Spades a | 6 | 4 | 0 | 0 | 99% (144/145) |
| 이번 | Schooltime a | 6 | 2 | 0 | 0 | 100% (259/259) |
| 이번 | Slithery Fight a (kcap 끔) | 6 | 0 | 0 | 0 | 100% (380/380) |
| 이번 | Trauma | 6 | 0 | 0 | 0 | 100% (178/178) |
| 이번 | Trophy | 6 | 1 | 1 | 0 | 99% (80/81) |
| 비교 | Autarky (끔) | 6 | 0 | 0 | 0 | 100% (1749/1749) |
| 비교 | Default | 6 | 1 | 0 | 0 | 100% (257/258) |
| 비교 | Devil a | 6 | 15 | 0 | 0 | 99% (163/164) |
| 비교 | Portals (끔) | 6 | 0 | 0 | 0 | 100% (949/949) |
| 비교 | Prisoners Dilemma (끔) | 6 | 0 | 0 | 0 | 100% (1534/1534) |
| 비교 | Queen Of Spades a | 6 | 4 | 0 | 0 | 99% (146/147) |
| 비교 | Schooltime a | 6 | 1 | 0 | 0 | 100% (286/287) |
| 비교 | Slithery Fight a (kcap 끔) | 6 | 1 | 0 | 0 | 100% (377/377) |
| 비교 | Trauma | 6 | 0 | 0 | 0 | 100% (176/176) |
| 비교 | Trophy | 6 | 1 | 1 | 0 | 99% (80/81) |

## stack8: 샘 목표 고르기(F2·F2p), 포털 출구의 아군(px2), 새끼의 몫(cl·ce)

- 기준값은 `research/experiments/cand-stack8.md`(로컬 확인 전, 18:20)에서 왔다. cl·ce의 기준값은 공급망 연구의 값(18:07)이다. F 목표(드래곤·샘 단위)와 포털 통과의 정의는 stack5 절과 "포털 통과" 절과 같다. Fp·cl·ce는 드래곤·진주 단위이고, 설계 상황은 처음 표식 때의 판이다.

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| F2 | 목표 수: F2 표식 / 모든 F(판당) | – | 1009 / 1009 (16.8) | 1004 / 1004 (16.7) |
| F2 | 1. 설계 상황: F2 표식 목표 (실제 샘 · 우리 영토 · 다른 머리 없음) | ≥90% | 79% (100% · 100% · 80%) | 79% (100% · 100% · 80%) |
| F2 | 1. 설계 상황: 모든 F 목표 | ≥80% | 79% | 79% |
| F2 | 2. 도착(3걸음 안): F2 표식 목표 / 모든 F | ≥80% | 58% / 58% | 58% / 58% |
| F2 | 3. 도착 뒤 30라운드 무리 자연 진주 우리 몫(F2 표식; 합산 · 지도 평균, Portals 제외) | ≥85% · ≥85% | 91% (2400개) · 84% | 91% (2408개) · 84% |
| F2 | 4. 겹친 추격: 다른 우리 드래곤의 같은 샘 목표와 겹침(F2 표식 / 모든 F) | ≤10% | 31% / 31% | 32% / 32% |
| F2p | Fp 진주 수(표식 턴) | – | 0 (0턴) | 0 (0턴) |
| F2p | 1. 설계 상황: 표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음 | ≥80% | – | – |
| F2p | 2. 즉시 효과: 그 드래곤이 10라운드 안에 먹음 · 상대가 먹음 | ≥48% · ≤5% | – · – | – · – |
| F2p | 끌어내기: F 표식 턴 가운데 유일하게 가장 가까운 자연 진주(7걸음 안, 무리 밖)에서 멀어진 턴 | ≤5% (관찰; W5+W6 15%) | 16% (후보가 있던 턴 28%; F 표식 턴 10594) | 16% (후보가 있던 턴 28%; F 표식 턴 10594) |
| px2 | 발동(px2 + px2x 턴, 판당) | – | 0 (0) | 0 (0) |
| px2 | 1. 설계 상황: 전 라운드 그 칸의 음파가 우리 드래곤에 멈춤 | ≥95% | – | – |
| px2 | 2. 즉시 효과 A: 건너지 않음(px2) | ≥80% | – | – |
| px2 | 3. 즉시 효과 B: 아군에 멈춘 탐침 뒤 아는 포털을 건너는 걸음에서 아군에 막혀 죽음(판당, v 무관) | ≤0.2 (W5–W7 0.69) | 0.90 (54건) | 0.90 (54건) |
| px2 | 보호: 포털 3라운드 몸 생존 | ≥95% | 93% | 93% |
| px2 | 보호: 건너는 걸음 아군 막힘 죽음(판당, 탐침·v 무관) | ≤0.75 (W5–W7 1.41) | 1.82 (109건) | 1.90 (114건) |
| cl | 진주 수(표식 턴) | – | 10774 (26009턴) | 10803 (25876턴) |
| cl | 설계 상황: 자연 진주, 우리 머리 가운데 표식한 조각만 가장 가까움 | ≥90% | 37% | 37% |
| cl | 즉시 효과: 조각이 먹음 · 우리 팀 · 우리 긴 드래곤 | ≥48% · ≥97% · ≤10% | 68% · 79% · 7% | 67% · 79% · 7% |
| ce | 진주 수(표식 턴) | – | 0 (0턴) | 0 (0턴) |
| ce | 설계 상황: 적 머리가 진주에서 우리 거리+1 안 | ≥80% | – | – |
| ce | 즉시 효과: 상대가 먹음 | ≤5% | – | – |
| ce | 보호: 표식 뒤 5라운드 안 박힘 | ≤19% | – | – |

- cl·ce의 가설 수준 지표(새끼 30라운드 먹음 ≥45%, 새끼 몫의 상대 몫 ≤3%/≤5%)는 공급망 스크립트 `exp/supply-chain/child_forage.js`로 잰다. 새끼 먹음은 stack5 절의 csplit 줄에도 있다.

### 포털 통과: 전 라운드 탐침(같은 칸, 같은 방향의 음파)별

| 묶음 | 출구 | 탐침 | 필사(v ≤ −20) | 통과 | 몸 3라운드 실패 | 건너는 걸음 아군 막힘 죽음 |
|---|---|---|---|---:|---:|---:|
| 이번 | 아는 포털 | clean | 아님 | 1003 | 4% | 30 |
| 이번 | 미탐색 | clean | 아님 | 848 | 3% | 11 |
| 이번 | 아는 포털 | ally | 아님 | 199 | 12% | 33 |
| 이번 | 미탐색 | clean | 필사 | 164 | 16% | 5 |
| 이번 | 아는 포털 | ally(머리) | 아님 | 76 | 22% | 21 |
| 이번 | 아는 포털 | none | 아님 | 61 | 15% | 0 |
| 이번 | 미탐색 | ally | 필사 | 41 | 10% | 2 |
| 이번 | 미탐색 | none | 필사 | 34 | 15% | 4 |
| 이번 | 아는 포털 | clean | 필사 | 26 | 12% | 0 |
| 이번 | 아는 포털 | enemy | 아님 | 13 | 23% | 0 |
| 이번 | 미탐색 | ally(머리) | 필사 | 11 | 27% | 3 |
| 이번 | 미탐색 | enemy | 필사 | 9 | 33% | 0 |
| 이번 | 아는 포털 | enemy(머리) | 아님 | 6 | 0% | 0 |
| 이번 | 미탐색 | enemy(머리) | 필사 | 4 | 25% | 0 |
| 이번 | 아는 포털 | ally | 필사 | 1 | 0% | 0 |
| 이번 | 미탐색 | none | 아님 | 1 | 0% | 0 |
| 비교 | 아는 포털 | clean | 아님 | 975 | 5% | 35 |
| 비교 | 미탐색 | clean | 아님 | 852 | 3% | 10 |
| 비교 | 아는 포털 | ally | 아님 | 207 | 11% | 32 |
| 비교 | 미탐색 | clean | 필사 | 149 | 15% | 4 |
| 비교 | 아는 포털 | ally(머리) | 아님 | 71 | 25% | 22 |
| 비교 | 아는 포털 | none | 아님 | 56 | 13% | 0 |
| 비교 | 미탐색 | ally | 필사 | 43 | 14% | 3 |
| 비교 | 미탐색 | none | 필사 | 31 | 16% | 5 |
| 비교 | 아는 포털 | clean | 필사 | 23 | 9% | 0 |
| 비교 | 미탐색 | ally(머리) | 필사 | 12 | 33% | 3 |
| 비교 | 아는 포털 | enemy | 아님 | 10 | 20% | 0 |
| 비교 | 미탐색 | enemy | 필사 | 7 | 43% | 0 |
| 비교 | 미탐색 | enemy(머리) | 필사 | 6 | 33% | 0 |
| 비교 | 아는 포털 | enemy(머리) | 아님 | 5 | 0% | 0 |
| 비교 | 미탐색 | none | 아님 | 1 | 0% | 0 |

## stack10: 국지 수 교환 문(lnt)과 판본별 머릿수 목표(utab)

- 기준값은 `research/experiments/cand-stack10.md`(21:12–21:14, 구현·로컬 확인 전)에서, 상위권·우리 값은 `research/observations/economy-principles.md`(4.1–4.3절, 7절)에서 왔다. 정의는 연구의 추출기(`exp/econ-principles/extract.js` O·C행)와 같다. d3 = 우리 드래곤의 차례 시작 머리에서 체비쇼프 3 안의 우리 머리 수 − 적 머리 수, d8 = 접촉 칸(표적 머리)에서 맨해튼 8 안의 같은 차이(두 드래곤 제외, 감싸기, 켈프·포털 무시). B3 기회 = 우리 길이 ≤4 드래곤의 차례 시작에 적 머리가 열린 변(포털 포함) 너머 바로 옆(둘 이상이면 가장 긴 것), 박음 = 그 머리로 한 걸음. 교환 = 우리 드래곤이 적 머리로 움직여 둘 다 죽음. 두 몸의 진주 = 두 사망 기록의 떨군 진주 합, net20 = (적 길이 − 우리 길이) + 20라운드 안 우리가 먹은 수 − 상대가 먹은 수.

### lnt 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| lnt | 박치기(맞부딪힘) 수 (판당) · 표식만 붙고 맞부딪히지 않음 | – | 168 (2.8) · 0 | 167 (2.8) · 0 |
| lnt | 1. 설계 상황: 기보 d3 ≥ +1이고 표적이 차례 시작에 바로 옆 | ≥95% | 100% | 100% |
| lnt | 2. 즉시 효과: 두 몸 진주 20R 우리 몫 / 상대 몫 · 건당 net20 (건) | ≥70% / ≤30% · ≥+1.5 | 48% / 49% · +0.46 (168) | 44% / 54% · +0.17 (167) |
| lnt | 3. 빈도: B3 기회 가운데 기보 d3 ≥ +1에서 박는 비율 | ≥50% (승자 65–73%, 우리 18세트 25–29%) | 92% (171/186) | 94% (170/180) |
| lnt | 3. 빈도: B3 기회 가운데 기보 d3 ≤ −1에서 박는 비율 | ≤20% (승자 14–16%) | 5% (23/505) | 6% (28/488) |
| lntv | 거부 턴 수 (판당) · 설계 상황(기보 d3 ≤ −1) · 표식 d3 = 기보 d3 | (관찰) | 10 (0.2) · 100% · 100% | 12 (0.2) · 100% · 100% |
| lntv | 거부 턴 뒤 10라운드 몸 생존 · 10라운드 안 박힘 | (관찰; 연구 4.2절: 박지 않은 기회 뒤 10라운드 사망 d3 ≤−2 우리 43%, 승자 50%) | 80% · 20% | 83% · 17% |
| kint | 예외 교환 수 · 두 몸 진주 20R 우리 몫 / 상대 몫 · 건당 net20 | (관찰; 승자의 상대 최장(≥8) 박기, d8 열세 net20 +9.47) | 9 · 12% / 56% · +10.44 (9) | 7 · 8% / 54% · +10.86 (7) |

### B3 기회: 기보 d3별 박는 비율과 그 박치기의 진주 (연구 4.2·4.3절 정의)

| 묶음 | d3 | 기회 | 박음 | 한 걸음 박치기(길이 ≤4, 차례 시작에 옆): 20R 우리 / 상대 · net20 (건) |
|---|---|---:|---:|---|
| 이번 | ≤−2 | 308 | 4% | 0% / 94% · -2.15 (13) |
| 이번 | −1 | 197 | 5% | 7% / 58% · +2.20 (10) |
| 이번 | 0 | 205 | 5% | 31% / 21% · +4.40 (10) |
| 이번 | +1 | 107 | 90% | 41% / 58% · -0.08 (96) |
| 이번 | ≥+2 | 79 | 95% | 56% / 39% · +1.13 (75) |
| 비교 | ≤−2 | 298 | 6% | 0% / 82% · -1.44 (18) |
| 비교 | −1 | 190 | 5% | 12% / 71% · -0.80 (10) |
| 비교 | 0 | 204 | 5% | 22% / 36% · +2.45 (11) |
| 비교 | +1 | 104 | 94% | 37% / 62% · -0.15 (98) |
| 비교 | ≥+2 | 76 | 95% | 53% / 41% · +0.58 (72) |

- 상위권 승자(연구 4.2·4.3절): 박는 비율 d3 ≤−2 14%, −1 16%, 0 29%, +1 65%, ≥+2 73%; 그 박치기의 20R 우리/상대 · net20은 ≤−2 24%/72% −0.76, −1 35%/60% +0.07, 0 52%/40% +1.21, +1 71%/25% +1.70, ≥+2 80%/15% +2.20. 우리 18세트: 12%, 13%, 16%, 25%, 29%; 9%/81% −1.63, 21%/69% −0.81, 36%/54% −0.01, 55%/38% +1.08, 70%/26% +2.32.

### 모든 교환 (우리가 박은 것; 가설 수준 지표, 관찰)

| 지표 | 기준 | 우리 18세트 · 상위권 승자 | 이번 | 비교 |
|---|---|---|---|---|
| 교환 수 (판당) · 그 가운데 lnt 표식 · kint 표식 | – | – | 241 (4) · 168 · 9 | 244 (4.1) · 167 · 7 |
| 두 몸 진주 20R 우리 몫 / 상대 몫 · 건당 net20 (건) | 우리 몫 ≥50% | 38% / 52% · 66% | 35% / 49% · +2.08 (241) | 30% / 54% · +1.46 (244) |
| 교환 가운데 d8 ≤ −3 비율 | ≤25% | 38% · 11% | 21% (50/241) | 22% (54/244) |
| 교환 가운데 d3 ≤ −1 비율 | (참고) | 36% · 8% | 12% | 13% |
| 판당 교환 net20의 합 (판) | ≥0 | – | +8.37 (60판) | +5.93 (60판) |

| 묶음 | d8 | 교환 | 20R 우리 / 상대 · net20 (건) |
|---|---|---:|---|
| 이번 | ≤−3 | 50 | 10% / 73% · -0.62 (50) |
| 이번 | −2 | 24 | 17% / 65% · +0.92 (24) |
| 이번 | −1 | 30 | 25% / 47% · +3.50 (30) |
| 이번 | 0 | 34 | 47% / 36% · +4.88 (34) |
| 이번 | +1 | 35 | 45% / 45% · +2.49 (35) |
| 이번 | +2 | 20 | 66% / 25% · +2.85 (20) |
| 이번 | ≥+3 | 48 | 52% / 38% · +2.00 (48) |
| 비교 | ≤−3 | 54 | 11% / 75% · -0.98 (54) |
| 비교 | −2 | 26 | 14% / 71% · +0.69 (26) |
| 비교 | −1 | 35 | 19% / 56% · +2.74 (35) |
| 비교 | 0 | 35 | 38% / 38% · +3.91 (35) |
| 비교 | +1 | 35 | 40% / 50% · +1.80 (35) |
| 비교 | +2 | 19 | 59% / 31% · +3.32 (19) |
| 비교 | ≥+3 | 40 | 52% / 42% · +0.80 (40) |

- 상위권 승자(연구 4.1절, 모든 교환): d8 ≤−3 41%/56% −0.12, 0 58%/34% +1.35, ≥+3 77%/17% +2.20. 우리 18세트: ≤−3 21%/70% −1.27, 0 37%/42% +1.15, ≥+3 72%/23% +2.76.

### utab 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| utab | csplit 발동 · 인식 뒤(발동한 프로세스의 마지막 map 표식이 판본을 댐) · tab 표식 | – | 1050 · 1047 · 0 | 1051 · 1048 · 0 |
| utab | 1. 설계 상황: 인식 뒤 csplit 가운데 tab | ≥95% | 0% | 0% |
| utab | 2. 즉시 효과: 목표가 1.5배 이상 오르는 판본 가운데 utab이 켜진 넷(Devil a·b, Slithery Fight a, Trophy a; W11부터 Portals는 넓이 목표)의 r100 우리 수 ÷ 표 r100 목표, 판 중앙값 (판) | ≥0.6 | 0.24 (18판) | 0.24 (18판) |
| utab | (사전 등록의 다섯 판본, Portals a 포함) r100 ÷ 표 r100 목표, 판 중앙값 (판) | – | 0.26 (24판) | 0.26 (24판) |
| utab | 3. tab csplit 새끼 30라운드 생존 | ≥30% | – (0마리) | – (0마리) |
| utab | (참고) 조금 오르는 판본(Slithery Fight b, Autarky a, Schooltime a): r100 ÷ 표 목표 중앙값 (판) | – | 0.38 (12판) | 0.38 (12판) |

### 판본별 r100 우리 드래곤 수 (utab 표 대비; 전멸은 0)

| 묶음 | 판본(정답) | 판 | 넓이 목표 | 표 r50 · r100 | r100 우리 수 중앙값 (평균) | ÷ 표 r100 (판 중앙값) | tab csplit (판당) |
|---|---|---:|---:|---|---|---:|---:|
| 이번 | Autarky/a | 6 | 21 | 17 · 23 | 9.5 (9.7) | 0.41 | 0 |
| 이번 | Default/a | 6 | 22 | 11 · 19 | 10 (10.3) | 0.53 | 0 |
| 이번 | Devil/a ↑ | 6 | 11 | 16 · 30 | 6.5 (6.7) | 0.22 | 0 |
| 이번 | Portals/a ↑ | 6 | 11 | 14 · 26 | 11 (10.8) | 0.42 | 0 |
| 이번 | Prisoners Dilemma/a | 6 | 11 | 9 · 13 | 4 (3.7) | 0.31 | 0 |
| 이번 | Queen Of Spades/a | 6 | 19 | 7 · 13 | 3.5 (3.8) | 0.27 | 0 |
| 이번 | Schooltime/a | 6 | 40 | 13 · 44 | 15 (14.5) | 0.34 | 0 |
| 이번 | Slithery Fight/a ↑ | 6 | 37 | 47 · 62 | 17 (16.8) | 0.27 | 0 |
| 이번 | Trauma/a ↓ | 6 | 25 | 7 · 16 | 5 (5.3) | 0.31 | 0 |
| 이번 | Trophy/a ↑ | 6 | 13 | 15 · 31 | 5 (5.5) | 0.16 | 0 |
| 비교 | Autarky/a | 6 | 21 | 17 · 23 | 9.5 (9.7) | 0.41 | 0 |
| 비교 | Default/a | 6 | 22 | 11 · 19 | 10 (10.2) | 0.53 | 0 |
| 비교 | Devil/a ↑ | 6 | 11 | 16 · 30 | 6.5 (6.7) | 0.22 | 0 |
| 비교 | Portals/a ↑ | 6 | 11 | 14 · 26 | 11 (10.8) | 0.42 | 0 |
| 비교 | Prisoners Dilemma/a | 6 | 11 | 9 · 13 | 4 (3.7) | 0.31 | 0 |
| 비교 | Queen Of Spades/a | 6 | 19 | 7 · 13 | 3.5 (3.8) | 0.27 | 0 |
| 비교 | Schooltime/a | 6 | 40 | 13 · 44 | 15 (14.5) | 0.34 | 0 |
| 비교 | Slithery Fight/a ↑ | 6 | 37 | 47 · 62 | 17 (16.8) | 0.27 | 0 |
| 비교 | Trauma/a ↓ | 6 | 25 | 7 · 16 | 5 (5.3) | 0.31 | 0 |
| 비교 | Trophy/a ↑ | 6 | 13 | 15 · 31 | 5 (5.5) | 0.16 | 0 |

- ↑ = 목표가 1.5배 이상 오르는 판본(게이트 2), ↓ = 2/3 이하로 내려가는 판본. 정답 판본은 로컬이면 지도 파일 이름, 온라인이면 기보의 자연 생성(`layoutTruth`; ?·x는 가릴 수 없던 판). stack6 r100(연구 7절): Autarky 10, Default 11, Devil a 6, Portals 12, PD10 4, PD a 4, QoS a 9, QoS b 5, Schooltime a 16, Schooltime b 8, Slithery a 31, Slithery b 11, Trauma 6, Trophy 9.

### utab 가설 수준 지표 (관찰; stack6(W6)과 비교)

| 지표 | 이번 | 비교 |
|---|---|---|
| 오르는 판본(utab이 켜진 넷: Devil a·b, Slithery Fight a, Trophy a): 우리 영토 자연 진주를 상대가 먹은 몫 | 81% (8482개, 18판) | 81% (8375개, 18판) |
| 오르는 판본(같은 넷): r0–199 우리가 먹은 자연 진주 (판당) | 43.7 | 43.7 |
| 내려가는 판본(QoS b, Schooltime b, Trauma a): r200 우리 최장(전멸은 0; 평균 · 중앙값) | 3.3 · 3 (6판) | 3.3 · 3 (6판) |
| 내려가는 판본: r100 우리 수 (평균) | 5.3 | 5.3 |

## stack9: 늦은 조각 풀 — 늦은 재분열(lsplit), frag 수 상한(fc), 영토 덮기 끌림(cov)

- 기준값은 `research/experiments/cand-stack9.md`(로컬 확인 결과를 보기 전, 21:04)에서, 상위권·우리 값은 `research/observations/supply-chain.md`(7절)에서 왔다. 가설 수준 지표는 그 연구의 코드(`exp/supply-chain/extract.js` analyse)를 같은 기보에 돌려 잰다. "판당"의 분모는 r250 뒤까지 간 우리 팀-경기다(500라운드형: Autarky, Portals, Schooltime, Slithery Fight, Trauma).

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| lsplit | 발동(모든 판당; 500라운드형 r250까지 간 판당) | – | 284 (4.7; 7.2) | 288 (4.8; 7.4) |
| lsplit | 1. 설계 상황: r250–339 · 부모 길이(분열 전) 4–6 · 우리 수(기보) < 목표 | ≥95% | 100% (100% · 100% · 100%; 표식의 수·목표 = 기보 100%) | 100% (100% · 100% · 100%; 표식의 수·목표 = 기보 100%) |
| lsplit | 2. 즉시 효과 A: 새끼가 30라운드 안에 자연 진주 ≥1 | ≥38% (승자의 늦은 2+2 새끼 38%) | 25% (284마리; 500형 26% · 전멸형 23%) | 27% (288마리; 500형 27% · 전멸형 26%) |
| lsplit | 3. 즉시 효과 B: 새끼가 죽을 때 떨군 진주의 우리 몫(합산) | ≥85% (승자 90%) | 79% (죽은 새끼 255마리, 진주 435개; ≥8 31% · 상대 15%) | 76% (죽은 새끼 265마리, 진주 456개; ≥8 29% · 상대 18%) |
| fc | 발동(판당) | – | 30 (0.5; frag 전체 41) | 40 (0.7; frag 전체 46) |
| fc | 1. 설계 상황: r250–420 · 부모가 팀 최장 아님 · 우리 수(기보) ≥ 옛 frag 상한 | ≥95% | 93% (100% · 93% · 100%) | 93% (100% · 93% · 100%) |
| fc | 2. 즉시 효과 A: 조각 제 몫(S1: 30라운드 살며 1개 이상 먹거나, 뒤에 희생 표식으로 아군을 먹임) | ≥50% | 27% (30마리) | 53% (40마리) |
| fc | 3. 즉시 효과 B: 조각이 죽을 때 떨군 진주 중 우리 ≥8이 먹은 몫(합산) | ≥20% (승자 부모 5–7 늦은 새끼 20%) | 31% (죽은 조각 27마리, 진주 42개; 우리 88% · 상대 0%) | 54% (죽은 조각 40마리, 진주 80개; 우리 86% · 상대 0%) |
| cov | 창 수(표식 턴; 판당 창) | – | 3061 (28184턴; 51) | 3048 (28095턴; 50.8) |
| cov | 게이트: 창 30라운드 안에 그 드래곤이 우리 영토 자연 진주 ≥1 | ≥47% (승자 자기 영토 태생 조각 47%) | 29% (창 안에 죽음 25%) | 29% (창 안에 죽음 26%) |
| cov | (관찰) 표식 턴의 끝 칸이 기보 영토의 우리 쪽: 창을 연 턴 / 모든 표식 턴 | – | 87% / 85% | 87% / 86% |
| cov | (참고) W5 정의: 표식 턴마다 20라운드 안에 우리 영토 자연 진주 | – | 20% | 20% |

### 가설 수준 지표 (관찰; 500라운드형 r250–499, r250 뒤까지 간 팀-경기당)

| 지표 | 기준 | 상위권 승자 · 패자 · stack5 · stack6 | 이번 | 비교 |
|---|---|---|---|---|
| lsplit: 조각 탄생(태어날 때 길이 ≤3; 모든 분열) | ≥50 | 156 · 135 · 8.7 · 7.1 | 12.6 (lsplit 7.2, frag 1.4, 탈출 분열 4, 그 밖 0.1) | 13.3 (lsplit 7.4, frag 1.5, 탈출 분열 4.3, 그 밖 0.1) |
| lsplit: conv 상태 에피소드 | ≥30 | 57.6 · 39.4 · 17.1 · 20.1 | 21.6 | 21.2 |
| lsplit · fc: conv형 진주(조각 → ≥8) | ≥12 (fc ≥9) | 22.9 · 14.8 · 6.5 · 5.4 | 6.5 | 7.1 |
| lsplit: 조각 → 조각 희생 진주 | ≥10 | 34.9 · 28.6 · 2.0 · 2.0 | 3.2 | 3.2 |
| fc: frag 새끼(r250–499) | ≥3 | (부모 5–7·8+ 36) · – · 0.4 · 0.9 | 1.4 | 1.5 |
| (관찰) r350 우리 조각 수(길이 ≤4; r350까지 간 판 평균) | – | 30.5 · – · 6.2 · – | 10.8 | 11 |
| (참고) 전멸형: 조각 탄생 · conv 상태 에피소드 · conv형 진주 · 조각 → 조각 | – | 68 · 17.3 · – · – | 4.6 · 1.1 · 0.7 · 2.2 | 4.4 · 1 · 1 · 2 |
| cov: r100 우리 영토에서 적이 더 가까운 몫(판 평균; 500형 / 전멸형) | ≤17% (500형) | 11% · 17% · 27% · 25% | 35% / 63% | 35% / 63% |
| cov: r100 자기 영토 보로노이(판 평균; 500형 / 전멸형) | ≥80% | 89% · 83% · 72% · 74% | 65% / 36% | 65% / 36% |
| cov: 우리 영토 자연 진주를 상대가 먹은 몫(합산; 500형 / 전멸형) | ≤25% | 11% / 16% (승자) | 58% / 58% | 57% / 58% |

- 판 수(r250 뒤까지 간 팀-경기; 500라운드형 / 전멸형): 이번 30 / 24 · 비교 30 / 24. 공급 사슬 재구성 점검이 0이 아닌 판: 이번 0 · 비교 0; 지표 계산 오류: 이번 0 · 비교 0.

### 부작용 (관찰; 판정에 쓰지 않음)

| 항목 | 이번 | 비교 |
|---|---|---|
| lsplit 새끼의 끝: 끝까지 삶 · 표식 희생(conv·feed) · 그 밖 희생 · 갇힘 · 박힘 · 아군 머리 · 그 밖 | 10% · 37% · 0% · 31% · 7% · 5% · 10% (284마리) | 8% · 36% · 0% · 31% · 7% · 6% · 12% (288마리) |
| 어린 조각 규칙(20라운드): lsplit 새끼가 20라운드 안에 끝남(갇힘 · 박힘 · 희생 · 그 밖) / 뒤에 conv·feed로 아군을 먹임(그때 나이 중앙) | 15% (29 · 4 · 0 · 10) / 37% (75) | 14% (29 · 2 · 0 · 9) / 36% (74) |
| lsplit 부모: 10라운드 생존 · 부모 몸(새끼 포함) 30라운드 뒤 길이 변화 평균 · 부모가 죽을 때 떨군 진주 우리 몫 | 86% · 3.5 · 70% (468개) | 85% · 3.5 · 73% (510개) |
| lsplit 모이기 창(r340 뒤) 발동 · 그 새끼 30라운드 안 자연 진주 ≥1 | 0 · – | 0 · – |
| 우리 드래곤의 죽음 r250 뒤(판당): 갇힘 · 적 머리에 박힘 · 우리끼리 머리 충돌(둘 다 셈) | 36.7 · 1.8 · 1.2 | 36.7 · 2 · 1.3 |
| 모이기(g) 드래곤(통로 고리 밖): 수 · 왕 3칸 안까지 감 · 희생까지 함 · 가는 길에 죽음 | 273 · 41% · 44% · 23% | 273 · 36% · 58% · 21% |
| 희생 먹이기(feed) · conv: 판당 발동, 떨군 진주 우리 몫 | feed 2.9, 87% · conv 3.7, 97% | feed 3.7, 87% · conv 3.4, 99% |
| 끝 왕 길이(500라운드형 끝까지 간 판) | 24.8 (30판) | 27.3 (30판) |

## stack11: 끝판 왕 — 모이기 물러서기(gh), 왕 떼기(kx), 끝판 창도 왕 부류에게(lwk)

- 기준값은 `research/experiments/cand-stack11.md`(23:04–23:06, 로컬 발동 수치를 보기 전)에서, 상위권·우리 값은 `research/observations/endgame-king.md`(1–5절, 7절)에서 왔다. gh 2, kx 2, lwk 2와 가설 수준 지표는 그 연구의 추출기(`exp/endgame-king/extract.js` analyse)를 같은 기보에 돌려 잰다. "500형 전부"는 500라운드형 모든 판, "500형 끝까지"는 500라운드까지 가고 최종 왕이 있는 판, "KX 지도"는 그 가운데 Schooltime·Slithery Fight·Trauma·Autarky다. 판당의 분모는 그 모집단의 우리 팀-경기다.

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| gh | 발동: gh 턴(판당) · ghd 진주 | – | 2599 (43.3) · 386 | 0 (0) · 0 |
| gh | 1. 설계 상황: gh 턴에 팀 최장(기보, 이 드래곤 아님)이 맨해튼 6 안 | ≥95% | 40% (이 드래곤이 팀 최장 132턴) | – (이 드래곤이 팀 최장 0턴) |
| gh | 1. 설계 상황: ghd 진주가 실제 사망 진주(표식 때 기보) | ≥95% | 100% (386개) | – (0개) |
| gh | 2. 즉시 효과 A: 가로채기 몫(r300 뒤 대상이 그때 계보인 표식 먹이의 진주를 계보 밖 우리 드래곤이 먹음; 500형 전부) | ≤20% (stack5–8 26–35%, merge2 20%) | 27% (97/362개, 먹이 173번) | 30% (118/396개, 먹이 169번) |
| gh | 3. 즉시 효과 B: ghd 진주를 곁의 더 긴 아군이 먹음 | ≥70% | 45% (386개; 우리 팀 97%, 상대 2%) | – (0개; 우리 팀 –, 상대 –) |
| kx | 발동: kx 턴(KX 지도 판당) | – | 616 (25.7; 발동한 판 21) | 0 (0; 발동한 판 0) |
| kx | 1. 설계 상황: kx 턴이 그 순간 팀 최장(기보: 더 긴 우리 드래곤 없음)이고 적 머리 맨해튼 7 안 | ≥90% | 58% (팀 최장 61% · 적 머리 7 안 92%; 질량 장부 왕 52%) | – (팀 최장 – · 적 머리 7 안 –; 질량 장부 왕 –) |
| kx | 2. 즉시 효과: KX 지도 계보 드래곤(길이 ≥8) r300–399 턴의 적 머리 6칸 안 몫(500형 끝까지) | ≤35% (stack5–7 52%, 승자 32%) | 41% (319/776턴, 24판) | 38% (252/661턴, 24판) |
| kx | 2. 즉시 효과: 같은 값 r400–499 | ≤22% (stack5–7 32%, 승자 21%) | 35% (665/1891턴, 24판) | 30% (582/1912턴, 24판) |
| lwk | 발동: lwk 턴(판당) | – | 431 (7.2) | 0 (0) |
| lwk | 1. 설계 상황: r430 뒤이고 더 긴 우리 머리가 맨해튼 5 안(기보) | 모두 | 98% (r430 뒤 100%) | – (r430 뒤 –) |
| lwk | 2. 즉시 효과: r430 뒤 feed의 대상이 그때 계보 · 떨군 진주 → 계보(500형 전부) | ≥55% · ≥45% (stack5–7 37% · 34%) | 52% (17/33) · 33% (29/87개) | 37% (28/76) · 38% (87/227개) |

### kx 2의 지도별 값 (계보 드래곤 길이 ≥8의 턴 가운데 적 머리 맨해튼 6 안; 500형 끝까지)

| 지도 | 구간 | 상위권 승자 (연구 T5b, r300–499) | 이번 | 비교 |
|---|---|---|---|---|
| Schooltime | r300–399 | 19% | 67% (110/164턴, 6판) | 24% (24/101턴, 6판) |
| Schooltime | r400–499 | 19% | 34% (163/475턴, 6판) | 33% (135/412턴, 6판) |
| Slithery Fight | r300–399 | 17% | 20% (65/333턴, 6판) | 21% (58/270턴, 6판) |
| Slithery Fight | r400–499 | 17% | 47% (213/449턴, 6판) | 10% (54/516턴, 6판) |
| Trauma | r300–399 | 17% | – | – |
| Trauma | r400–499 | 17% | 13% (48/363턴, 6판) | 12% (47/384턴, 6판) |
| Autarky | r300–399 | 22% | 52% (144/279턴, 6판) | 59% (170/290턴, 6판) |
| Autarky | r400–499 | 22% | 40% (241/604턴, 6판) | 58% (346/600턴, 6판) |
| Portals | r300–399 | 49% (참고: 벽 너머) | 50% (240/484턴, 6판) | 57% (288/508턴, 6판) |
| Portals | r400–499 | 49% (참고: 벽 너머) | 15% (91/589턴, 6판) | 21% (130/607턴, 6판) |

### 가설 수준 지표 (관찰; 연구 7절)

| 기능 | 지표 | 기준 | 상위권 승자 · stack5–7 (연구) | 이번 | 비교 |
|---|---|---|---|---|---|
| gh | 계보가 r300–499에 먹은 우리 희생 진주(판당; 500형 끝까지 / KX 지도) | ≥9.3 | 25.8 · 8.3 | 8.8 / 9.2 | 9.7 / 9.8 |
| gh | 모이기 창(r340–429) feed(판당; 500형 전부) · 발동 라운드 중앙 | ≥2.0 | – · 2.4 | 2.6 · 392 | 2.8 · 380 |
| gh | 길이 ≥8 우리 드래곤의 아군 머리 사망 r340–399(판당; r340까지 간 500형) | 늘지 않음 | – · 0.08 (r350–399) | 0.07 | 0.07 |
| gh | (참고) 뿌리 모이기 에피소드 가운데 가족의 마지막 죽음이 아군 머리(500형 전부) | – | – | 4% (10/244) | 7% (16/243) |
| gh | (부작용) 뿌리 모이기 에피소드 가족의 끝: 계보 / 계보 밖 삶 / 표식 먹이 / 다른 희생 / 다른 죽음(500형 전부) · 첫 g 표식에서 표식 먹이까지 라운드 중앙 | – | – · 11% / 21% / 47% / 0% / 21% | 14% / 30% / 36% / 0% / 21% (244) · 17 | 10% / 20% / 50% / 1% / 19% (243) · 16 |
| kx | r340 뒤 팀 최장(길이 ≥8)을 적 머리에 잃은 판(500형 끝까지 / KX 지도) | ≤7% | 5% · 13% (stack5–8) | 3% (1/30) / 4% (1/24) | 7% (2/30) / 8% (2/24) |
| kx | 계보의 우리 희생 진주 r300–499(판당; KX 지도) | ≥10 | 25.8 · 8.3 | 9.2 | 9.8 |
| kx | 표식 먹이(feed·conv, r300 뒤) 가운데 대상이 그때 계보인 몫(500형 전부 / KX 지도) | 유지 | – · 64% (feed r340–429) | 54% (320) / 67% (217) | 49% (347) / 60% (235) |
| kx | 왕 성장 r300→500(라운드당; 500형 끝까지 / KX 지도) | ≥0.12 | 0.18 · 0.09 | 0.08 / 0.08 | 0.10 / 0.10 |
| kx | 부작용: 계보의 자연 진주 r300–499(판당; KX 지도) | ≥11 | 11.7 · 12.4 | 9.8 | 10.5 |
| kx | 부작용: 계보의 분열 손실(떼어 냄 + 넘김) r300–499(판당; KX 지도) | 늘지 않음(≤5.9) | 6.6 · 5.9 | 5.5 | 2.3 |
| lwk | 계보의 r450–499 우리 희생 진주(판당; 500형 끝까지) | ≥2.6 | 6.4 · 2.1 | 1.7 | 2.6 |
| lwk | 끝에 계보 밖에서 산 길이 ≥8 드래곤의 끝 길이 합(판당; 500형 끝까지) | 늘지 않음 | – | 25 | 20.2 |

- 판 수(500형 전부 / 500형 끝까지 / KX 지도): 이번 30 / 30 / 24 · 비교 30 / 30 / 24. 추출기 재구성 점검이 0이 아닌 판: 이번 0 · 비교 0; 계산 오류: 이번 0 · 비교 0.

### 부작용 (관찰; 판정에 쓰지 않음)

| 항목 | 이번 | 비교 |
|---|---|---|
| kx 먹이 찾기: 계보 드래곤 턴당 5칸 안 자연 진주(r300–499; KX 지도) · 계보의 자연 진주(판당) | 1.31 · 9.8 | 1.51 · 10.5 |
| kx 가두기: r300 뒤 적이 계보 드래곤의 몸에 막혀 죽은 수(판당; 몸에 박음 + 몸 곁에 갇힘; KX 지도 / 500형 전부) · 계보가 먹은 적 사망 진주 r300–499(판당; KX 지도) | 0.2 / 0.2 · 3 | 0 / 0 · 2.1 |
| (참고) r300 뒤 적이 우리 몸에 막혀 죽은 수 전체(판당; 500형 전부): 박음 · 갇힘 | 0.1 · 0.5 | 0.2 · 0.6 |
| kx 막다른 곳·포털: 팀 최장(길이 ≥8)의 죽음 r300 뒤(판당; 500형 전부 / KX 지도): 적 머리 · 갇힘 · 아군 머리 · 희생 · 그 밖 | 0.03 · 0.07 · 0.10 · 0.00 · 0.00 / 0.04 · 0.00 · 0.04 · 0.00 · 0.00 | 0.07 · 0.07 · 0.07 · 0.03 · 0.00 / 0.08 · 0.04 · 0.04 · 0.04 · 0.00 |
| kx 포털: 그 순간 팀 최장(길이 ≥8)의 r300 뒤 포털 통과(판당; KX 지도) · 몸 3라운드 생존 · 드래곤 자체 3라운드 생존 · 넘는 걸음에서 죽음 | 1 (24) · 96% · 96% · 1 | 0.6 (14) · 86% · 86% · 2 |
| kx: 계보 드래곤 턴의 적 머리 3칸 안 몫 r300–499(KX 지도) | 9% | 9% |
| 길이 ≥8 우리 드래곤의 죽음 r300–499(판당; 500형 전부): 적 머리 · 아군 머리 · 갇힘 · 희생 | 0.10 · 0.17 · 0.80 · 0.33 | 0.10 · 0.23 · 0.43 · 0.80 |
| 표식 먹이 r300 뒤(판당; 500형 전부): conv · 모이기 창 feed · 끝판 창 feed | 7 · 2.6 · 1.1 | 6.3 · 2.8 · 2.5 |
| grab 표적 진주(판당) · 그중 우리가 먹음 | 46.4 · 81% | 47.5 · 81% |

