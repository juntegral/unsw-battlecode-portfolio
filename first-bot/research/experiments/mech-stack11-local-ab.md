# 구현 적용 확인

- 대상: `exp/stack11-a-px4+exp/stack11-b-px4-ks+exp/stack11-b-px4-elim` 120판 · 비교: `exp/stack10-a-px4+exp/stack10-b-px4` 120판
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
| 모이기 물러서기 (gh, stack11; 턴 단위) | 4783 (39.9) | – | 0 (0) | – |
| 더 긴 아군 곁 새 사망 진주 양보 (ghd, stack11; 드래곤·진주 단위) | 783 (6.5) | 44% | 0 (0) | – |
| 왕 떼기 (kx, stack11; 턴 단위) | 977 (8.1) | – | 0 (0) | – |
| 끝판 창 왕 부류에게만 (lwk, stack11; 턴 단위) | 941 (7.8) | – | 0 (0) | – |
| 늦은 재분열 (lsplit, stack9) | 577 (4.8) | 29% | 583 (4.9) | 32% |
| 영토 덮기 끌림 30라운드 창 (cov 창, stack9; 드래곤·창 단위) | 6244 (52) | 29% | 6280 (52.3) | 29% |
| 국지 수 우세 박음 (lnt, stack10) | 317 (2.6) | 44% | 316 (2.6) | 45% |
| 국지 수 열세 교환 거부 (lntv, stack10) | 24 (0.2) | 92% | 29 (0.2) | 90% |
| 거부 예외: 상대 최장일 수 있음 (kint, stack10) | 10 (0.1) | 100% | 9 (0.1) | 89% |
| 몫을 긴 아군에게 넘기지 않음 (cl, stack8; 드래곤·진주 단위) | 19203 (160) | 67% | 19345 (161.2) | 66% |
| 수 바닥 분열 (split floor, stack7) | 42 (0.4) | 57% | 42 (0.4) | 62% |
| 왕 길이 상한 분열 (split kcap, stack7) | 2 (0) | 100% | 2 (0) | 100% |
| 지도·판본 인식 (map=, cand-mapid; 판 단위) | 120 (1) | 100% | 120 (1) | 100% |
| Schooltime b 초반 분열 (split bsp, cand-mapid) | 59 (0.5) | 95% | 59 (0.5) | 95% |
| 덮기 분열 (csplit, stack5) | 1875 (15.6) | 38% | 1870 (15.6) | 38% |
| 샘 지킴 (F, stack5; 드래곤·샘 단위) | 2096 (17.5) | 88% | 2093 (17.4) | 88% |
| 영토 덮기 끌림 (cov, stack5) | 59433 (495.3) | 20% | 60148 (501.2) | 20% |
| 위협 모형 빈틈 (tg, stack4) | 22744 (189.5) | 98% | 23097 (192.5) | 98% |
| 모이기 시작 제한 (gx, stack4; 드래곤 단위) | 255 (2.1) | 97% | 134 (1.1) | 94% |
| 큰 아군 곁 희생 (conv, stack1 M1) | 440 (3.7) | 98% | 396 (3.3) | 98% |
| 조각 떼기 (split frag, stack2 S1) | 77 (0.6) | 38% | 88 (0.7) | 63% |
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 5245 (43.7) | 81% | 5397 (45) | 81% |
| 왕에게 모이기 (g, 드래곤 단위) | 1978 (16.5) | 77% | 1955 (16.3) | 80% |
| 희생 먹이기 (feed) | 322 (2.7) | 88% | 443 (3.7) | 87% |
| 막다른 길 한입 (pocket-eat) | 1016 (8.5) | 99% | 1014 (8.5) | 99% |
| 탈출 분열 (escape-split) | 7865 (65.5) | 98% | 7820 (65.2) | 97% |
| 출구 없음 (no-exit) | 8186 (68.2) | – | 8151 (67.9) | – |
| 정책 분열 (split) | 3 (0) | 100% | 3 (0) | 100% |
| 탈출 질주 3칸 (esc) | 132 (1.1) | 91% | 123 (1) | 91% |
| 위협 피하기 2칸 질주 | 1147 (9.6) | 93% | 1166 (9.7) | 93% |
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 5260 (43.8) | 94% | 5327 (44.4) | 94% |
| 돌진 (TRADE) | 379 (3.2) | 47% | 380 (3.2) | 46% |
| 먹이 질주 (2칸 이상, 먹은 것) | 328 (2.7) | 100% | 352 (2.9) | 100% |
| 기타 2칸 질주 | 123 (1) | – | 134 (1.1) | – |
| 마지막 돌진 (last-trade) | 40 (0.3) | – | 45 (0.4) | – |

- 건강: 턴 466356, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 비교 건강: 턴 464774, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 22806턴 · 끝판(late) 12197턴 · 돌진 신뢰(T, 탈출 끔) 61턴, 그 직후 박혀 죽음 0

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 비교 |
|---|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 7% (331/4833턴) | 7% (333/4857턴) |
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 39.1칸 (10.9회), 진주 우리 95% · 상대 1% | 47.7칸 (12.1회), 진주 우리 94% · 상대 3% |
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 2칸 (판당 0.07회) | 1.5칸 (판당 0.03회) |
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 24% (1915/8039턴) | 23% (1751/7684턴) |
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.025회 (3건, 80칸) | 판당 0.058회 (7건, 168칸) |
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 9마리 (59판) | 9.4마리 (59판) |
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 19.3회 | 20.2회 |
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 53% (우리 42%) | 53% (우리 42%) |
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 9.7 대 상대 23.9 (9.3회) · 박힌 교환의 우리 몫 18% (348회) | 우리 9.1 대 상대 24.2 (9.5회) · 박힌 교환의 우리 몫 17% (350회) |
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 10.2개 | 9개 |

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 모이기 물러서기 (gh, stack11; 턴 단위)

- 이번: 턴 4783 · 설계 상황(팀 최장(기보, 이 드래곤 아님)이 맨해튼 6 안) 40% (기준 ≥95%) · 이 드래곤이 팀 최장 4% · 팀 최장까지 맨해튼 평균 9.3
- 상대별: proxy4_elim 1525회 – · proxy4_king 1614회 – · proxy4_swarm 1644회 –
- 지도별: Autarky 1097회 – · Default 77회 – · Devil 25회 – · Portals 2004회 – · Prisoners Dilemma 111회 – · Prisoners Dilemma (10) 16회 – · Queen Of Spades 61회 – · Schooltime 158회 – · Slithery Fight 1029회 – · Trauma 205회 –
- 국면별: r250-349 234회 – · r350-449 3432회 – · r450+ 1117회 –

## 더 긴 아군 곁 새 사망 진주 양보 (ghd, stack11; 드래곤·진주 단위)

- 이번: 진주 783개 (표식 턴 1067) · 실제 사망 진주 100% (기준 ≥95%; 자연 1, 이미 없음 0) · 곁의 더 긴 아군이 먹음 44% (기준 ≥70%) · 우리 96% (표식한 드래곤 28%, 더 긴 우리 드래곤 50%, 최종 왕 계보 19%) · 상대 3% · 안 먹힘 1% · 곁의 더 긴 아군 수 평균 0.9
- 상대별: proxy4_elim 305회 41% · proxy4_king 268회 43% · proxy4_swarm 210회 49%
- 지도별: Autarky 230회 45% · Default 22회 29% · Devil 7회 43% · Portals 198회 49% · Prisoners Dilemma 46회 33% · Queen Of Spades 14회 36% · Schooltime 20회 40% · Slithery Fight 208회 42% · Trauma 38회 45%
- 국면별: r250-349 321회 38% · r350-449 412회 44% · r450+ 50회 72%

실패 사례 (440건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r328 · 드래곤 #200 L3: 진주 (51,7) 사망 진주, 곁의 더 긴 아군 0마리 → 표식한 드래곤이 먹음 (1라운드 뒤), 표식 1턴
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r347 · 드래곤 #129 L2: 진주 (16,20) 사망 진주, 곁의 더 긴 아군 0마리 → 다른 우리 드래곤이 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r364 · 드래곤 #530 L2: 진주 (4,8) 사망 진주, 곁의 더 긴 아군 1마리 → 표식한 드래곤이 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r354 · 드래곤 #170 L3: 진주 (9,6) 사망 진주, 곁의 더 긴 아군 1마리 → 표식한 드래곤이 먹음 (2라운드 뒤), 표식 2턴
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r344 · 드래곤 #163 L3: 진주 (55,18) 사망 진주, 곁의 더 긴 아군 0마리 → 다른 우리 드래곤이 먹음 (1라운드 뒤), 표식 1턴
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r335 · 드래곤 #249 L2: 진주 (13,12) 사망 진주, 곁의 더 긴 아군 0마리 → 상대가 먹음 (3라운드 뒤), 표식 1턴
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r396 · 드래곤 #231 L2: 진주 (3,1) 사망 진주, 곁의 더 긴 아군 1마리 → 표식한 드래곤이 먹음 (0라운드 뒤), 표식 1턴
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:A:1 · r327 · 드래곤 #239 L2: 진주 (4,6) 사망 진주, 곁의 더 긴 아군 1마리 → 다른 우리 드래곤이 먹음 (4라운드 뒤), 표식 2턴
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r300 · 드래곤 #112 L2: 진주 (2,6) 사망 진주, 곁의 더 긴 아군 0마리 → 다른 우리 드래곤이 먹음 (2라운드 뒤), 표식 1턴
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:A:1 · r458 · 드래곤 #57 L2: 진주 (8,7) 사망 진주, 곁의 더 긴 아군 1마리 → 다른 더 긴 우리 드래곤이 먹음 (2라운드 뒤), 표식 1턴

## 왕 떼기 (kx, stack11; 턴 단위)

- 이번: 턴 977 · 설계 상황(기보: 더 긴 우리 드래곤 없음, 적 머리 맨해튼 7 안) 65% (기준 ≥90%; 질량 장부의 왕 기준 60%) · kxm 73% · 움직인 뒤 가장 가까운 적 머리가 멀어짐 61% (kxm 턴 78%) · 표식 거리 1:6 2:38 3:113 4:306 5:225 6:193 7:96 · 10라운드 안 적 머리에 죽음 3% · 20라운드 안 몸(이 턴부터 태어난 자손 포함) 잃음 4% · 20라운드 안 탈출 분열 39% · KX 지도 밖 0턴
- 상대별: proxy4_elim 301회 – · proxy4_king 343회 – · proxy4_swarm 333회 –
- 지도별: Autarky 266회 – · Schooltime 306회 – · Slithery Fight 347회 – · Trauma 58회 –
- 국면별: r250-349 231회 – · r350-449 383회 – · r450+ 363회 –

## 끝판 창 왕 부류에게만 (lwk, stack11; 턴 단위)

- 이번: 턴 941 · 설계 상황(r430 뒤, 더 긴 우리 머리가 맨해튼 5 안) 97% (기준 모두) · r430 뒤 100% · 10라운드 뒤 몸 생존 91% · 끝까지 몸 생존 73%
- 상대별: proxy4_elim 203회 – · proxy4_king 318회 – · proxy4_swarm 420회 –
- 지도별: Autarky 133회 – · Devil 13회 – · Portals 371회 – · Prisoners Dilemma (10) 1회 – · Queen Of Spades 14회 – · Schooltime 15회 – · Slithery Fight 308회 – · Trauma 86회 –
- 국면별: r350-449 265회 – · r450+ 676회 –

## 늦은 재분열 (lsplit, stack9)

- 이번: 분열 100% · 설계 상황(r250–339, 부모 길이 4–6, 우리 수 < 목표; 기보) 100% (기준 ≥95%) · 새끼 30라운드 안 자연 진주 ≥1 29% (기준 ≥38%) · 죽은 새끼 524마리의 떨군 진주 881개 중 우리 79% (기준 ≥85%) · ≥8 28% · 상대 15% · 새끼 10·30라운드 생존 86% · 69% · 부모 길이 평균 4.3 · r340 뒤 0회
- 비교: 분열 100% · 설계 상황(r250–339, 부모 길이 4–6, 우리 수 < 목표; 기보) 100% (기준 ≥95%) · 새끼 30라운드 안 자연 진주 ≥1 32% (기준 ≥38%) · 죽은 새끼 544마리의 떨군 진주 954개 중 우리 76% (기준 ≥85%) · ≥8 29% · 상대 16% · 새끼 10·30라운드 생존 89% · 71% · 부모 길이 평균 4.3 · r340 뒤 0회
- 상대별: proxy4_elim 215회 32% · proxy4_king 188회 27% · proxy4_swarm 174회 28%
- 지도별: Autarky 122회 32% · Default 84회 37% · Devil 2회 0% · Portals 32회 9% · Prisoners Dilemma 7회 0% · Queen Of Spades 39회 31% · Schooltime 53회 26% · Slithery Fight 139회 25% · Trauma 99회 34%
- 국면별: r250-349 577회 29%

실패 사례 (409건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r257 · 드래곤 #196 L4: 새끼 L2 · 우리 17/21마리 → 새끼 죽음 r429 희생(나이 172, 진주 2개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r258 · 드래곤 #96 L4: 새끼 L2 · 우리 10/22마리 → 새끼 죽음 r337 돌진(나이 79, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:B:1 · r312 · 드래곤 #309 L4: 새끼 L2 · 우리 5/11마리 → 새끼 죽음 r342 박힘(상대 돌진)(나이 30, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r280 · 드래곤 #420 L5: 새끼 L2 · 우리 10/11마리 → 새끼 죽음 r295 갇힘(나이 15, 진주 2개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:B:1 · r322 · 드래곤 #165 L4: 새끼 L2 · 우리 10/11마리 → 새끼 죽음 r378 희생(나이 56, 진주 2개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r252 · 드래곤 #16 L4: 새끼 L2 · 우리 4/19마리 → 새끼 끝까지 생존, 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r283 · 드래곤 #15 L4: 새끼 L2 · 우리 7/40마리 → 새끼 죽음 r288 박힘(상대 돌진)(나이 5, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r287 · 드래곤 #282 L5: 새끼 L2 · 우리 15/37마리 → 새끼 죽음 r329 갇힘(나이 42, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r264 · 드래곤 #100 L4: 새끼 L2 · 우리 15/25마리 → 새끼 죽음 r315 갇힘(나이 51, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:A:1 · r268 · 드래곤 #249 L4: 새끼 L2 · 우리 17/21마리 → 새끼 죽음 r290 갇힘(나이 22, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0

## 영토 덮기 끌림 30라운드 창 (cov 창, stack9; 드래곤·창 단위)

- 이번: 창 6244개 (표식 턴 59433) · 창 30라운드 안 우리 영토 자연 진주 ≥1 29% (기준 ≥47%) · 창 안에 죽음 25% · 판 끝에 잘린 창 134 · 창을 연 표식 턴의 끝 칸이 기보 영토의 우리 쪽 90%
- 비교: 창 6280개 (표식 턴 60148) · 창 30라운드 안 우리 영토 자연 진주 ≥1 29% (기준 ≥47%) · 창 안에 죽음 26% · 판 끝에 잘린 창 128 · 창을 연 표식 턴의 끝 칸이 기보 영토의 우리 쪽 90%
- 상대별: proxy4_elim 2133회 29% · proxy4_king 2057회 31% · proxy4_swarm 2054회 28%
- 지도별: Autarky 714회 34% · Default 686회 19% · Devil 339회 34% · Portals 766회 45% · Prisoners Dilemma 105회 13% · Prisoners Dilemma (10) 128회 4% · Queen Of Spades 577회 23% · Schooltime 914회 27% · Slithery Fight 947회 36% · Trauma 893회 21% · Trophy 175회 43%
- 국면별: r0-99 1629회 38% · r100-249 2222회 25% · r250-349 1354회 25% · r350-449 823회 33% · r450+ 216회 21%

실패 사례 (4420건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r0 · 드래곤 #0 L4: 창 r0–r30, 표식 1턴 → 못 먹음
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r0 · 드래곤 #5 L3: 창 r0–r30, 표식 10턴 → 못 먹음
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r68 · 드래곤 #0 L2: 창 r68–r98, 표식 3턴 → 못 먹음
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r11 · 드래곤 #6 L2: 창 r11–r41, 표식 4턴 → 못 먹음
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r0 · 드래곤 #2 L3: 창 r0–r30, 표식 14턴 → 못 먹음
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r12 · 드래곤 #0 L3: 창 r12–r42, 표식 19턴 → 못 먹음
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r0 · 드래곤 #1 L4: 창 r0–r30, 표식 6턴 → 못 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r2 · 드래곤 #0 L2: 창 r2–r32, 표식 1턴 → 창 안에 죽음
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r0 · 드래곤 #0 L4: 창 r0–r30, 표식 12턴 → 못 먹음
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r74 · 드래곤 #9 L2: 창 r74–r104, 표식 31턴 → 못 먹음

## 국지 수 우세 박음 (lnt, stack10)

- 이번: 맞부딪힘 100% (317) · 설계 상황(기보 d3 ≥ +1이고 표적이 차례 시작에 바로 옆) 100% · 옛 규칙도 박았을 턴(o) 3% · 두 몸 진주 844개 중 20라운드 안 우리 48% · 상대 49% · 건당 net20 +0.50 · 적 길이 평균 2.7 · 우리 길이 평균 2.2
- 비교: 맞부딪힘 100% (316) · 설계 상황(기보 d3 ≥ +1이고 표적이 차례 시작에 바로 옆) 100% · 옛 규칙도 박았을 턴(o) 2% · 두 몸 진주 821개 중 20라운드 안 우리 47% · 상대 51% · 건당 net20 +0.28 · 적 길이 평균 2.6 · 우리 길이 평균 2.2
- 상대별: proxy4_elim 107회 39% · proxy4_king 106회 40% · proxy4_swarm 104회 52%
- 지도별: Autarky 6회 0% · Default 72회 51% · Devil 29회 34% · Prisoners Dilemma (10) 2회 0% · Queen Of Spades 29회 52% · Schooltime 43회 37% · Slithery Fight 93회 48% · Trauma 10회 30% · Trophy 33회 36%
- 국면별: r0-99 84회 38% · r100-249 133회 43% · r250-349 78회 47% · r350-449 19회 58% · r450+ 3회 33%

실패 사례 (179건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r5 · 드래곤 #2 L2: 표식 d3 2 · 기보 d3 2 · d8 4 · 적 L2 → 진주 2개 중 20라운드 안 우리 0 · 상대 2, net20 -2
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r46 · 드래곤 #3 L3: 표식 d3 1 · 기보 d3 1 · d8 -1 · 적 L2 → 진주 3개 중 20라운드 안 우리 0 · 상대 3, net20 -4
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r62 · 드래곤 #13 L3: 표식 d3 2 · 기보 d3 2 · d8 2 · 적 L3 → 진주 4개 중 20라운드 안 우리 2 · 상대 2, net20 0
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r202 · 드래곤 #4 L3: 표식 d3 1 · 기보 d3 1 · d8 -1 · 적 L2 → 진주 3개 중 20라운드 안 우리 0 · 상대 3, net20 -4
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r140 · 드래곤 #58 L2: 표식 d3 2 · 기보 d3 2 · d8 0 · 적 L2 → 진주 2개 중 20라운드 안 우리 0 · 상대 2, net20 -2
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r100 · 드래곤 #157 L2: 표식 d3 2 · 기보 d3 2 · d8 1 · 적 L2 → 진주 2개 중 20라운드 안 우리 0 · 상대 2, net20 -2
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r76 · 드래곤 #2 L2: 표식 d3 1 · 기보 d3 1 · d8 -3 · 적 L3 → 진주 3개 중 20라운드 안 우리 0 · 상대 3, net20 -2
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:A:1 · r251 · 드래곤 #2 L2: 표식 d3 1 · 기보 d3 1 · d8 -5 · 적 L2 → 진주 2개 중 20라운드 안 우리 0 · 상대 2, net20 -2
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r5 · 드래곤 #2 L2: 표식 d3 3 · 기보 d3 3 · d8 4 · 적 L2 → 진주 2개 중 20라운드 안 우리 1 · 상대 1, net20 0
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:B:1 · r59 · 드래곤 #43 L2: 표식 d3 1 · 기보 d3 1 · d8 -6 · 적 L2 → 진주 2개 중 20라운드 안 우리 0 · 상대 2, net20 -2

## 국지 수 열세 교환 거부 (lntv, stack10)

- 이번: 거부 턴 24 · 설계 상황(기보 d3 ≤ −1) 100% · 표식 d3 = 기보 d3 100% · 10라운드 뒤 몸 생존 92% · 10라운드 안 박힘 21% · 우리 길이 평균 3
- 비교: 거부 턴 29 · 설계 상황(기보 d3 ≤ −1) 100% · 표식 d3 = 기보 d3 100% · 10라운드 뒤 몸 생존 90% · 10라운드 안 박힘 21% · 우리 길이 평균 2.9
- 상대별: proxy4_elim 4회 100% · proxy4_king 5회 60% · proxy4_swarm 15회 100%
- 지도별: Default 1회 100% · Queen Of Spades 3회 100% · Schooltime 10회 90% · Slithery Fight 5회 80% · Trauma 4회 100% · Trophy 1회 100%
- 국면별: r100-249 3회 100% · r250-349 13회 92% · r350-449 8회 88%

실패 사례 (2건 중 2건, 기보 확인용):
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r250 · 드래곤 #213 L2: 표식 d3 -2 (기보 -2) → 죽음 r250 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r357 · 드래곤 #231 L2: 표식 d3 -3 (기보 -3) → 죽음 r360 돌진, 상대 길이 12

## 거부 예외: 상대 최장일 수 있음 (kint, stack10)

- 이번: 맞부딪힘 100% (10) · 설계 상황(기보 d3 ≤ −1) 100% · 두 몸 진주 119개 중 20라운드 안 우리 11% · 상대 57% · 건당 net20 +10.30 · 적 길이 평균 19.3 · 우리 길이 평균 3.6
- 비교: 맞부딪힘 100% (9) · 설계 상황(기보 d3 ≤ −1) 100% · 두 몸 진주 91개 중 20라운드 안 우리 11% · 상대 54% · 건당 net20 +9.33 · 적 길이 평균 16.6 · 우리 길이 평균 3.1
- 상대별: proxy4_elim 3회 100% · proxy4_king 4회 100% · proxy4_swarm 3회 100%
- 지도별: Schooltime 7회 100% · Slithery Fight 2회 100% · Trauma 1회 100%
- 국면별: r250-349 2회 100% · r350-449 8회 100%

## 몫을 긴 아군에게 넘기지 않음 (cl, stack8; 드래곤·진주 단위)

- 이번: 진주 19203개 (표식 턴 47848; 표식 때 진주 있음 97%) · 설계 상황(자연 진주이고 우리 머리 가운데 표식한 조각만 가장 가까움) 39% · 그 드래곤이 먹음 67% (10라운드 안 66%) · 우리 팀 80% · 우리 긴 드래곤 7% · 상대 14%
- 비교: 진주 19345개 (표식 턴 47728; 표식 때 진주 있음 97%) · 설계 상황(자연 진주이고 우리 머리 가운데 표식한 조각만 가장 가까움) 39% · 그 드래곤이 먹음 66% (10라운드 안 65%) · 우리 팀 79% · 우리 긴 드래곤 7% · 상대 15%
- 상대별: proxy4_elim 6824회 66% · proxy4_king 6252회 66% · proxy4_swarm 6127회 67%
- 지도별: Autarky 4373회 93% · Default 1321회 70% · Devil 698회 73% · Portals 2265회 61% · Prisoners Dilemma 1688회 97% · Prisoners Dilemma (10) 64회 36% · Queen Of Spades 1262회 54% · Schooltime 1795회 49% · Slithery Fight 3511회 36% · Trauma 1641회 59% · Trophy 585회 64%
- 국면별: r0-99 4833회 64% · r100-249 5980회 66% · r250-349 4168회 67% · r350-449 3272회 68% · r450+ 950회 75%

실패 사례 (6242건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r4 · 드래곤 #12 L2: 진주 (10,29) 우리 거리 99 → 상대가 먹음
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r4 · 드래곤 #3 L3: 진주 (35,16) 우리 거리 5 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r22 · 드래곤 #2 L2: 진주 (14,8) 우리 거리 6 → 상대가 먹음
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r10 · 드래곤 #6 L2: 진주 (15,1) 우리 거리 4 → 다른 우리 드래곤이 먹음
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r152 · 드래곤 #34 L3: 진주 (12,11) 우리 거리 5 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r16 · 드래곤 #2 L2: 진주 (6,33) 우리 거리 4 → 다른 우리 드래곤이 먹음
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r35 · 드래곤 #8 L2: 진주 (51,12) 우리 거리 4 → 상대가 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r1 · 드래곤 #12 L2: 진주 (21,1) 우리 거리 3 → 다른 우리 드래곤이 먹음
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r33 · 드래곤 #4 L2: 진주 (11,10) 우리 거리 99 → 다른 우리 드래곤이 먹음
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r27 · 드래곤 #6 L3: 진주 (6,6) 우리 거리 99 → 상대가 먹음

## 수 바닥 분열 (split floor, stack7)

- 이번: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 71% · 적 머리가 7×7 시야 안 40% · 부모 길이 평균 4.8 · 우리 수(표식) 평균 2.4 · 상대 수 평균 22 · 새끼 10라운드 생존 81% · 30라운드 57% · 부모 10라운드 생존 76% · 30라운드 62% · 새끼 30라운드 안 1개 이상 먹음 50% · 30라운드 뒤 가족 길이 변화 1 · 30라운드 안 새끼가 죽은 원인: 갇힘 9, 아군 머리 1, 박힘(상대 돌진) 3, 희생 2, 돌진 3
- 비교: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 71% · 적 머리가 7×7 시야 안 40% · 부모 길이 평균 4.7 · 우리 수(표식) 평균 2.3 · 상대 수 평균 23 · 새끼 10라운드 생존 83% · 30라운드 62% · 부모 10라운드 생존 81% · 30라운드 64% · 새끼 30라운드 안 1개 이상 먹음 57% · 30라운드 뒤 가족 길이 변화 1.2 · 30라운드 안 새끼가 죽은 원인: 박힘(상대 돌진) 3, 갇힘 8, 희생 2, 돌진 3
- 상대별: proxy4_elim 18회 61% · proxy4_king 14회 50% · proxy4_swarm 10회 60%
- 지도별: Default 5회 60% · Devil 29회 48% · Queen Of Spades 5회 80% · Schooltime 2회 100% · Trophy 1회 100%
- 국면별: r0-99 3회 67% · r100-249 7회 57% · r250-349 8회 50% · r350-449 24회 58%

실패 사례 (18건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r427 · 드래곤 #129 L6: 우리 3마리 · 상대 19마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r429 갇힘, 부모 10라운드 생존 · 표식 map=Default/a
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r201 · 드래곤 #81 L4: 우리 3마리 · 상대 45마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r212 박힘(상대 돌진), 상대 길이 3, 부모 10라운드 생존 · 표식 map=Devil/a
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:A:1 · r388 · 드래곤 #82 L4: 우리 2마리 · 상대 6마리 · 새끼 L2 → 새끼 죽음 r392 갇힘, 상대 길이 6, 부모 10라운드 생존 (설계 밖: 상대 < 8마리) · 표식 map=Devil/a
- proxy4_elim · Devil · 게임 exp/stack11-a-px4:proxy4_elim:devil:A:1 · r304 · 드래곤 #167 L4: 우리 2마리 · 상대 51마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r308 박힘(상대 돌진), 상대 길이 3, 부모 10라운드 생존 · 표식 map=Devil/a
- proxy4_elim · Queen Of Spades · 게임 exp/stack11-b-px4-elim:proxy4_elim:queen_of_spades_b:B:2 · r313 · 드래곤 #3 L4: 우리 3마리 · 상대 22마리 · 새끼 L2 → 새끼 죽음 r330 갇힘, 부모 10라운드 생존 · 표식 map=Queen_Of_Spades/b
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r449 · 드래곤 #129 L5: 우리 3마리 · 상대 10마리 · 새끼 L2 → 새끼 죽음 r479 아군 머리, 상대 길이 14, 부모 10라운드 생존 · 표식 map=Default/a
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:A:1 · r433 · 드래곤 #82 L8: 우리 2마리 · 상대 4마리 · 새끼 L2 → 새끼 죽음 r457 희생, 부모 10라운드 죽음 (설계 밖: 상대 < 8마리) · 표식 map=Devil/a
- proxy4_elim · Devil · 게임 exp/stack11-a-px4:proxy4_elim:devil:B:1 · r374 · 드래곤 #486 L4: 우리 2마리 · 상대 9마리 · 새끼 L2 → 새끼 죽음 r385 희생, 부모 10라운드 생존 · 표식 map=Devil/a
- proxy4_elim · Devil · 게임 exp/stack11-a-px4:proxy4_elim:devil:B:1 · r418 · 드래곤 #502 L10: 우리 3마리 · 상대 3마리 · 새끼 L2 → 새끼 죽음 r419 갇힘, 부모 10라운드 생존 (설계 밖: 상대 < 8마리) · 표식 map=Devil/a
- proxy4_elim · Devil · 게임 exp/stack11-a-px4:proxy4_elim:devil:B:1 · r425 · 드래곤 #503 L5: 우리 3마리 · 상대 3마리 · 새끼 L2 → 새끼 죽음 r450 갇힘, 상대 길이 15, 부모 10라운드 생존 (설계 밖: 상대 < 8마리) · 표식 map=Devil/a

## 왕 길이 상한 분열 (split kcap, stack7)

- 이번: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 50% · 부모 길이 평균 8 · 우리 수(표식) 평균 4 · 상대 수 평균 7 · 새끼 10라운드 생존 100% · 30라운드 100% · 부모 10라운드 생존 50% · 30라운드 0% · 새끼 30라운드 안 1개 이상 먹음 50% · 30라운드 뒤 가족 길이 변화 -1 · 30라운드 안 새끼가 죽은 원인: 없음
- 비교: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 50% · 부모 길이 평균 8 · 우리 수(표식) 평균 4 · 상대 수 평균 7 · 새끼 10라운드 생존 100% · 30라운드 100% · 부모 10라운드 생존 50% · 30라운드 0% · 새끼 30라운드 안 1개 이상 먹음 50% · 30라운드 뒤 가족 길이 변화 -1 · 30라운드 안 새끼가 죽은 원인: 없음
- 상대별: proxy4_king 1회 100% · proxy4_swarm 1회 100%
- 지도별: Queen Of Spades 1회 100% · Trophy 1회 100%
- 국면별: r0-99 1회 100% · r100-249 1회 100%

## 지도·판본 인식 (map=, cand-mapid; 판 단위)

- 이번: 판본을 기보로 가릴 수 있는 판 120/120 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 95%, 그중 정답 100% · 프로세스 10932: 표식 없음 9, 결정 10874 (정답 100%, 틀림 0), 가족만 48, 모름 1, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 305라운드
- 비교: 판본을 기보로 가릴 수 있는 판 120/120 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 95%, 그중 정답 100% · 프로세스 10899: 표식 없음 8, 결정 10849 (정답 100%, 틀림 0), 가족만 41, 모름 1, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 305라운드
- 상대별: proxy4_elim 40회 100% · proxy4_king 40회 100% · proxy4_swarm 40회 100%
- 지도별: Autarky a 12회 100% · Default a 12회 100% · Devil a 6회 100% · Devil b 6회 100% · Portals a 12회 100% · Prisoners Dilemma a 6회 100% · Prisoners Dilemma b 6회 100% · Queen Of Spades a 6회 100% · Queen Of Spades b 6회 100% · Schooltime a 6회 100% · Schooltime b 6회 100% · Slithery Fight a 6회 100% · Slithery Fight b 6회 100% · Trauma a 12회 100% · Trophy a 12회 100%
- 국면별: r0-99 120회 100%

## Schooltime b 초반 분열 (split bsp, cand-mapid)

- 이번: 분열 100% · 설계 상황(그 판이 실제로 Schooltime b) 100% · 조각 10라운드 생존 95% (기준 ≥85%; 상위권 b 92%) · 10라운드 안 1개 이상 먹음 14% (상위권 b 20%) · 부모 10라운드 생존 98% · 조각 30라운드 생존 95%, 30라운드 안 1개 이상 먹음 27% · 30라운드 뒤 가족 길이 변화 3.8 · 30라운드 안 조각이 죽은 원인: 갇힘 2, 돌진 1
- 비교: 분열 100% · 설계 상황(그 판이 실제로 Schooltime b) 100% · 조각 10라운드 생존 95% (기준 ≥85%; 상위권 b 92%) · 10라운드 안 1개 이상 먹음 14% (상위권 b 20%) · 부모 10라운드 생존 98% · 조각 30라운드 생존 95%, 30라운드 안 1개 이상 먹음 27% · 30라운드 뒤 가족 길이 변화 3.8 · 30라운드 안 조각이 죽은 원인: 갇힘 2, 돌진 1
- 상대별: proxy4_elim 25회 92% · proxy4_king 16회 94% · proxy4_swarm 18회 100%
- 지도별: Schooltime 59회 95%
- 국면별: r0-99 43회 98% · r100-249 16회 88%

실패 사례 (3건 중 3건, 기보 확인용):
- proxy4_king · Schooltime · 게임 exp/stack11-b-px4-ks:proxy4_king:schooltime_b:A:2 · r121 · 드래곤 #4 L4: 조각 L2 → 조각 죽음 r128 갇힘, 10·30라운드 안 먹은 진주 0·0
- proxy4_elim · Schooltime · 게임 exp/stack11-b-px4-elim:proxy4_elim:schooltime_b:A:2 · r124 · 드래곤 #10 L4: 조각 L2 → 조각 죽음 r128 갇힘, 10·30라운드 안 먹은 진주 0·0
- proxy4_elim · Schooltime · 게임 exp/stack11-b-px4-elim:proxy4_elim:schooltime_b:B:2 · r87 · 드래곤 #9 L4: 조각 L2 → 조각 죽음 r88 돌진, 상대 길이 2, 10·30라운드 안 먹은 진주 0·0

## 덮기 분열 (csplit, stack5)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 34% · 부모가 스스로 최장이라 믿음(k) 69% · 새끼 30라운드 안 자연 진주 ≥1 38% (500형 38% · 전멸형 38%; 기준 ≥45%) · 새끼 30라운드 생존 73% (500형 77% · 전멸형 67%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 85% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 박힘(상대 돌진) 87, 돌진 73, 갇힘 328, 아군 머리 26, 희생 1
- 비교: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 35% · 부모가 스스로 최장이라 믿음(k) 69% · 새끼 30라운드 안 자연 진주 ≥1 38% (500형 38% · 전멸형 38%; 기준 ≥45%) · 새끼 30라운드 생존 73% (500형 77% · 전멸형 68%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 84% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 박힘(상대 돌진) 86, 돌진 68, 갇힘 329, 아군 머리 25
- 상대별: proxy4_elim 676회 39% · proxy4_king 608회 37% · proxy4_swarm 591회 37%
- 지도별: Autarky 238회 37% · Default 297회 39% · Devil 136회 28% · Portals 149회 43% · Prisoners Dilemma 44회 45% · Prisoners Dilemma (10) 8회 0% · Queen Of Spades 139회 33% · Schooltime 163회 41% · Slithery Fight 347회 31% · Trauma 202회 44% · Trophy 152회 48%
- 국면별: r0-99 880회 40% · r100-249 995회 36%

실패 사례 (1166건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r1 · 드래곤 #0 L4: 새끼 L2, 적 머리 시야 안 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r50 · 드래곤 #7 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r5 · 드래곤 #4 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r33 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r15 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r34 · 드래곤 #8 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r3 · 드래곤 #33 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r28 · 드래곤 #0 L5: 새끼 L2 → 새끼 죽음 r40 갇힘, 30라운드 안 자연 진주 0

## 샘 지킴 (F, stack5; 드래곤·샘 단위)

- 이번: 목표 2096개(표식 턴 22613) · 설계 상황 82% (실제 샘 100%, 우리 영토 100%, 처음에 다른 우리 머리 3걸음 안 없음 82%; 기준 ≥80%) · 3걸음 안 도착 59% · 도착 뒤 30라운드 그 무리 자연 진주 4791개 중 우리 91% · 상대 8% (합산 기준 ≥85%) · 처음 거리 평균 3.3
- 비교: 목표 2093개(표식 턴 22617) · 설계 상황 82% (실제 샘 100%, 우리 영토 100%, 처음에 다른 우리 머리 3걸음 안 없음 82%; 기준 ≥80%) · 3걸음 안 도착 59% · 도착 뒤 30라운드 그 무리 자연 진주 4829개 중 우리 91% · 상대 8% (합산 기준 ≥85%) · 처음 거리 평균 3.3
- 상대별: proxy4_elim 698회 94% · proxy4_king 770회 85% · proxy4_swarm 628회 85%
- 지도별: Autarky 52회 0% · Devil 132회 56% · Portals 1065회 99% · Prisoners Dilemma 58회 100% · Prisoners Dilemma (10) 13회 100% · Schooltime 10회 – · Slithery Fight 628회 54% · Trauma 138회 84%
- 국면별: r0-99 716회 80% · r100-249 839회 93% · r250-349 541회 94%

실패 사례 (114건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r23 · 드래곤 #2 L2: 샘 (14,8) 처음 거리 5 → r40 도착, 30라운드 무리 진주 6개 중 우리 0 · 상대 6
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r0 · 드래곤 #8 L5: 샘 (33,2) 처음 거리 0 → r0 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_swarm · Portals · 게임 exp/stack11-a-px4:proxy4_swarm:portals:B:1 · r306 · 드래곤 #398 L4: 샘 (4,7) 처음 거리 0 → r306 도착, 30라운드 무리 진주 7개 중 우리 5 · 상대 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_swarm:slithery_fight:A:1 · r0 · 드래곤 #8 L5: 샘 (33,2) 처음 거리 0 → r0 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_swarm · Trauma · 게임 exp/stack11-a-px4:proxy4_swarm:trauma:A:1 · r333 · 드래곤 #140 L3: 샘 (11,10) 처음 거리 3 → r333 도착, 30라운드 무리 진주 3개 중 우리 0 · 상대 0
- proxy4_elim · Devil · 게임 exp/stack11-a-px4:proxy4_elim:devil:B:1 · r51 · 드래곤 #1 L2: 샘 (20,0) 처음 거리 5 → r52 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2
- proxy4_elim · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_elim:slithery_fight:A:1 · r0 · 드래곤 #8 L5: 샘 (33,2) 처음 거리 0 → r0 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_king · Autarky · 게임 exp/stack11-b-px4-ks:proxy4_king:autarky:A:2 · r130 · 드래곤 #2 L2: 샘 (19,1) 처음 거리 6 → r196 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_king · Trauma · 게임 exp/stack11-b-px4-ks:proxy4_king:trauma:A:2 · r265 · 드래곤 #116 L3: 샘 (11,12) 처음 거리 4 → r267 도착, 30라운드 무리 진주 6개 중 우리 4 · 상대 2
- proxy4_swarm · Autarky · 게임 exp/stack11-b-px4-ks:proxy4_swarm:autarky:A:2 · r117 · 드래곤 #6 L2: 샘 (19,1) 처음 거리 4 → r117 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1

## 영토 덮기 끌림 (cov, stack5)

- 이번: 턴 59433 · 20라운드 안 우리 영토 자연 진주 먹음 20%
- 비교: 턴 60148 · 20라운드 안 우리 영토 자연 진주 먹음 20%
- 상대별: proxy4_elim 20431회 20% · proxy4_king 19389회 21% · proxy4_swarm 19613회 19%
- 지도별: Autarky 5310회 29% · Default 7703회 13% · Devil 3604회 19% · Portals 2923회 37% · Prisoners Dilemma 1150회 7% · Prisoners Dilemma (10) 1819회 2% · Queen Of Spades 7101회 16% · Schooltime 11948회 21% · Slithery Fight 8042회 27% · Trauma 8109회 13% · Trophy 1724회 37%
- 국면별: r0-99 15006회 30% · r100-249 21602회 15% · r250-349 12414회 14% · r350-449 8360회 23% · r450+ 2051회 19%

실패 사례 (47527건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r0 · 드래곤 #0 L4
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r0 · 드래곤 #5 L3
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r19 · 드래곤 #2 L3
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r11 · 드래곤 #4 L4
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r0 · 드래곤 #2 L3
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r12 · 드래곤 #0 L3
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r0 · 드래곤 #1 L4
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r0 · 드래곤 #6 L2
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r0 · 드래곤 #0 L4
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r24 · 드래곤 #6 L2

## 위협 모형 빈틈 (tg, stack4)

- 이번: 피함(tg) 57% · 위협 칸으로 감(tgx) 9852턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 98% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 98%) · 길이별 L2-5 22322 · L6-9 212 · L10+ 210
- 비교: 피함(tg) 57% · 위협 칸으로 감(tgx) 9899턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 98% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 98%) · 길이별 L2-5 22657 · L6-9 229 · L10+ 211
- 상대별: proxy4_elim 7306회 98% · proxy4_king 7246회 98% · proxy4_swarm 8192회 99%
- 지도별: Autarky 1326회 99% · Default 4053회 98% · Devil 1671회 98% · Portals 12회 100% · Prisoners Dilemma (10) 702회 99% · Queen Of Spades 2693회 99% · Schooltime 5108회 99% · Slithery Fight 4696회 99% · Trauma 590회 97% · Trophy 1893회 96%
- 국면별: r0-99 4105회 98% · r100-249 10314회 98% · r250-349 5505회 98% · r350-449 2360회 99% · r450+ 460회 98%

실패 사례 (396건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r11 · 드래곤 #13 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r13 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r170 · 드래곤 #7 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r171 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r41 · 드래곤 #2 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r43 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r211 · 드래곤 #64 L3: 피함(tg), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r213 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r91 · 드래곤 #5 L3: 피함(tg), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r92 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r309 · 드래곤 #428 L2: 피함(tg), 적 머리 경로 1칸 · 맨해튼 1칸(길이 2) → 박힘 r311 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r229 · 드래곤 #118 L2: 피함(tg), 적 머리 경로 4칸 · 맨해튼 4칸(길이 2) → 박힘 r231 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r86 · 드래곤 #45 L2: 피함(tg), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r87 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r188 · 드래곤 #66 L3: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r190 박힘(상대 돌진), 상대 길이 4
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:B:1 · r474 · 드래곤 #3 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r476 박힘(상대 돌진), 상대 길이 3

## 모이기 시작 제한 (gx, stack4; 드래곤 단위)

- 이번: 드래곤 255 (표식 턴 1927) · 몸(자손 포함) 끝까지 97% (기준 ≥80%) · 드래곤 자체 끝까지 생존 62% (참고) · 뒤에 희생 먹이기(feed)로 끝남 9
- 비교: 드래곤 134 (표식 턴 795) · 몸(자손 포함) 끝까지 94% (기준 ≥80%) · 드래곤 자체 끝까지 생존 60% (참고) · 뒤에 희생 먹이기(feed)로 끝남 7
- 상대별: proxy4_elim 55회 98% · proxy4_king 101회 97% · proxy4_swarm 99회 96%
- 지도별: Autarky 93회 100% · Default 6회 83% · Portals 65회 97% · Prisoners Dilemma (10) 11회 100% · Queen Of Spades 6회 67% · Schooltime 20회 100% · Slithery Fight 42회 95% · Trauma 12회 92%
- 국면별: r450+ 255회 97%

실패 사례 (8건 중 8건, 기보 확인용):
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:B:1 · r488 · 드래곤 #109 L8: gx 2턴 (r488–r489) → 죽음 r491 희생
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r491 · 드래곤 #76 L6: gx 4턴 (r491–r494) → 죽음 r495 희생
- proxy4_swarm · Portals · 게임 exp/stack11-a-px4:proxy4_swarm:portals:B:1 · r486 · 드래곤 #495 L6: gx 7턴 (r486–r492) → 죽음 r492 갇힘, 상대 길이 12
- proxy4_king · Slithery Fight · 게임 exp/stack11-b-px4-ks:proxy4_king:slithery_fight_b:A:2 · r480 · 드래곤 #599 L4: gx 8턴 (r480–r489) → 죽음 r490 희생
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-b-px4-ks:proxy4_swarm:slithery_fight_b:A:2 · r479 · 드래곤 #914 L4: gx 1턴 (r479–r479) → 죽음 r480 희생
- proxy4_elim · Trauma · 게임 exp/stack11-b-px4-elim:proxy4_elim:trauma:B:2 · r497 · 드래곤 #195 L4: gx 1턴 (r497–r497) → 죽음 r498 희생
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:B:1 · r490 · 드래곤 #80 L4: gx 4턴 (r490–r493) → 죽음 r494 희생
- proxy4_swarm · Portals · 게임 exp/stack11-b-px4-ks:proxy4_swarm:portals:A:2 · r491 · 드래곤 #494 L4: gx 2턴 (r491–r492) → 죽음 r493 희생

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 686개 중 우리 팀 97% (지목한 아군 64%) · 상대 1% · 지목 아군 끝까지 생존 43% (그 뒤 죽은 원인: 갇힘 185, 희생 51, 돌진 5, 아군 머리 9, 박힘(상대 돌진) 3) · 지목 아군의 몸(자손 포함)이 끝까지 삶 83% · 최종 왕 28% (최종 왕이 지목 아군의 자손 58%)
- 비교: 실행 100% · 떨군 진주 610개 중 우리 팀 99% (지목한 아군 64%) · 상대 1% · 지목 아군 끝까지 생존 44% (그 뒤 죽은 원인: 희생 50, 갇힘 156, 아군 머리 9, 돌진 1, 박힘(상대 돌진) 7) · 지목 아군의 몸(자손 포함)이 끝까지 삶 76% · 최종 왕 34% (최종 왕이 지목 아군의 자손 51%)
- 상대별: proxy4_elim 157회 96% · proxy4_king 145회 99% · proxy4_swarm 138회 98%
- 지도별: Autarky 118회 99% · Default 4회 50% · Devil 5회 80% · Portals 156회 99% · Prisoners Dilemma 2회 100% · Prisoners Dilemma (10) 1회 100% · Queen Of Spades 7회 100% · Schooltime 15회 87% · Slithery Fight 104회 97% · Trauma 28회 96%
- 국면별: r250-349 150회 99% · r350-449 225회 99% · r450+ 65회 89%

실패 사례 (11건 중 10건, 기보 확인용):
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:B:1 · r499 · 드래곤 #130 L2: #212(L11)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_swarm:slithery_fight:A:1 · r403 · 드래곤 #89 L3: #663(L40)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1; 지목 아군 r423 갇힘에 사망
- proxy4_elim · Portals · 게임 exp/stack11-a-px4:proxy4_elim:portals:A:1 · r497 · 드래곤 #586 L3: #563(L8)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_elim · Schooltime · 게임 exp/stack11-a-px4:proxy4_elim:schooltime:A:1 · r470 · 드래곤 #328 L4: #321(L11)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1; 지목 아군 r497 갇힘에 사망
- proxy4_king · Devil · 게임 exp/stack11-b-px4-ks:proxy4_king:devil_b:A:2 · r484 · 드래곤 #418 L4: #417(L9)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2; 지목 아군 r496 박힘(상대 돌진)에 사망
- proxy4_king · Slithery Fight · 게임 exp/stack11-b-px4-ks:proxy4_king:slithery_fight_b:B:2 · r302 · 드래곤 #11 L3: #581(L18)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1
- proxy4_elim · Autarky · 게임 exp/stack11-b-px4-elim:proxy4_elim:autarky:A:2 · r368 · 드래곤 #247 L3: #195(L10)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_elim · Default · 게임 exp/stack11-b-px4-elim:proxy4_elim:default:B:2 · r439 · 드래곤 #78 L3: #121(L8)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2
- proxy4_elim · Trauma · 게임 exp/stack11-b-px4-elim:proxy4_elim:trauma:B:2 · r498 · 드래곤 #195 L4: #245(L11)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_swarm:slithery_fight:A:1 · r451 · 드래곤 #1208 L3: #1218(L31)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 1

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 87% · 조각 30라운드 생존 44% · 30라운드 안 1개 이상 먹음 56% (살아서 먹음 18%) · 평생 먹은 진주 평균 4.2 · 나중에 아군을 먹임 26% (conv 13, feed 7, 분열 뒤 평균 33.3라운드) · 끝까지 생존 13% · 30라운드 안 죽은 원인: 갇힘 32, 희생 9, 아군 머리 1, 돌진 1
- 비교: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 84% · 조각 30라운드 생존 41% · 30라운드 안 1개 이상 먹음 63% (살아서 먹음 23%) · 평생 먹은 진주 평균 3.2 · 나중에 아군을 먹임 50% (conv 25, feed 19, 분열 뒤 평균 44.9라운드) · 끝까지 생존 2% · 30라운드 안 죽은 원인: 갇힘 30, 희생 20, 아군 머리 2
- 상대별: proxy4_elim 19회 26% · proxy4_king 29회 45% · proxy4_swarm 29회 38%
- 지도별: Autarky 3회 100% · Portals 41회 32% · Queen Of Spades 2회 50% · Schooltime 6회 50% · Slithery Fight 20회 40% · Trauma 5회 20%
- 국면별: r250-349 19회 21% · r350-449 58회 43%

실패 사례 (48건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r361 · 드래곤 #525 L12: 조각 L2 → 조각 죽음 r368 갇힘, 30라운드 안 먹은 진주 2
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r400 · 드래곤 #379 L11: 조각 L2 → 조각 죽음 r421 갇힘, 30라운드 안 먹은 진주 10
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:B:1 · r351 · 드래곤 #717 L8: 조각 L2 → 30라운드 생존, 먹은 진주 0 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_swarm · Portals · 게임 exp/stack11-a-px4:proxy4_swarm:portals:B:1 · r326 · 드래곤 #447 L9: 조각 L2 → 조각 죽음 r355 갇힘, 상대 길이 16, 30라운드 안 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_swarm:slithery_fight:A:1 · r315 · 드래곤 #734 L11: 조각 L2 → 조각 죽음 r336 갇힘, 30라운드 안 먹은 진주 5
- proxy4_elim · Portals · 게임 exp/stack11-a-px4:proxy4_elim:portals:A:1 · r391 · 드래곤 #545 L11: 조각 L2 → 조각 죽음 r399 갇힘, 30라운드 안 먹은 진주 1
- proxy4_elim · Schooltime · 게임 exp/stack11-a-px4:proxy4_elim:schooltime:A:1 · r341 · 드래곤 #147 L45: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_elim:slithery_fight:A:1 · r266 · 드래곤 #444 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Trauma · 게임 exp/stack11-a-px4:proxy4_elim:trauma:A:1 · r364 · 드래곤 #174 L7: 조각 L2 → 조각 죽음 r373 갇힘, 30라운드 안 먹은 진주 6 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_swarm · Trauma · 게임 exp/stack11-b-px4-ks:proxy4_swarm:trauma:A:2 · r337 · 드래곤 #209 L8: 조각 L2 → 조각 죽음 r346 갇힘, 30라운드 안 먹은 진주 6 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 5245개 (표식 턴 12898, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 2, 이미 없음 468) · 사망 진주 4775개 중 우리가 먹음 81% · 상대 17% · 아무도 안 먹음 2% · 표적으로 삼은 드래곤이 먹음 67% · 우리가 먹기까지 평균 3.6라운드 · 상대 머리가 같거나 더 가까웠던 1402개: 우리 57% 대 상대 43% · 박치기 진주 1008개: 우리 58% 대 상대 42% · 우리 팀 사망 진주 82% · 사망 뒤 첫 표적까지 평균 1.3라운드
- 비교: 표적 진주 5397개 (표식 턴 13711, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 0, 이미 없음 479) · 사망 진주 4918개 중 우리가 먹음 81% · 상대 17% · 아무도 안 먹음 1% · 표적으로 삼은 드래곤이 먹음 67% · 우리가 먹기까지 평균 3.4라운드 · 상대 머리가 같거나 더 가까웠던 1439개: 우리 56% 대 상대 43% · 박치기 진주 1010개: 우리 57% 대 상대 43% · 우리 팀 사망 진주 83% · 사망 뒤 첫 표적까지 평균 1.3라운드
- 상대별: proxy4_elim 2002회 83% · proxy4_king 1689회 80% · proxy4_swarm 1554회 81%
- 지도별: Autarky 653회 98% · Default 562회 77% · Devil 301회 55% · Portals 1380회 98% · Prisoners Dilemma 117회 88% · Prisoners Dilemma (10) 39회 35% · Queen Of Spades 298회 58% · Schooltime 302회 59% · Slithery Fight 1036회 77% · Trauma 313회 80% · Trophy 244회 63%
- 국면별: r0-99 594회 66% · r100-249 1479회 77% · r250-349 1384회 84% · r350-449 1461회 90% · r450+ 327회 81%

실패 사례 (886건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r7 · 드래곤 #4 L2: 진주 (4,0), 우리 머리 6칸 · 상대 머리 4칸, 박치기 2라운드 뒤 → 상대가 먹음 (3라운드 뒤), 표식 4턴
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r67 · 드래곤 #4 L4: 진주 (10,11), 우리 머리 2칸 · 상대 머리 1칸, 박치기 1라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 3턴
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r477 · 드래곤 #576 L11: 진주 (11,5), 우리 머리 2칸 · 상대 머리 11칸, 우리 팀 사망 1라운드 뒤 → 아무도 안 먹음, 표식 1턴
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r206 · 드래곤 #170 L3: 진주 (15,11), 우리 머리 4칸 · 상대 머리 1칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r37 · 드래곤 #2 L2: 진주 (6,33), 우리 머리 3칸 · 상대 머리 7칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (49라운드 뒤), 표식 2턴
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r102 · 드래곤 #8 L2: 진주 (58,11), 우리 머리 3칸 · 상대 머리 7칸, 우리 팀 사망 2라운드 뒤 → 상대가 먹음 (137라운드 뒤), 표식 3턴
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r4 · 드래곤 #26 L2: 진주 (33,5), 우리 머리 5칸 · 상대 머리 10칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (58라운드 뒤), 표식 3턴
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r394 · 드래곤 #185 L3: 진주 (14,20), 우리 머리 4칸 · 상대 머리 3칸, 우리 팀 사망 0라운드 뒤 → 상대가 먹음 (5라운드 뒤), 표식 3턴
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r77 · 드래곤 #45 L2: 진주 (1,11), 우리 머리 5칸 · 상대 머리 2칸, 우리 팀 사망 0라운드 뒤 → 상대가 먹음 (8라운드 뒤), 표식 1턴
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r5 · 드래곤 #12 L2: 진주 (4,0), 우리 머리 2칸 · 상대 머리 5칸, 박치기 0라운드 뒤 → 상대가 먹음 (5라운드 뒤), 표식 2턴

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 1978 (그중 통로 고리 세대 1462, 판정에서 뺌) · 고리 밖 516: 처음 거리 평균 10.2 → 최소 5.1 · 3칸 안까지 감 43% · 희생까지 함 42% · 가는 길에 죽음 26% · 끝까지 생존 32%
- 비교: 모이기 드래곤 1955 (그중 통로 고리 세대 1429, 판정에서 뺌) · 고리 밖 526: 처음 거리 평균 10.3 → 최소 5.7 · 3칸 안까지 감 36% · 희생까지 함 58% · 가는 길에 죽음 21% · 끝까지 생존 21%
- 상대별: proxy4_elim 731회 78% · proxy4_king 669회 77% · proxy4_swarm 578회 76%
- 지도별: Autarky 788회 83% · Default 37회 69% · Devil 33회 60% · Portals 551회 82% · Prisoners Dilemma 187회 88% · Prisoners Dilemma (10) 75회 80% · Queen Of Spades 35회 73% · Schooltime 50회 49% · Slithery Fight 139회 76% · Trauma 83회 72%
- 국면별: r250-349 297회 85% · r350-449 1389회 80% · r450+ 292회 58%

실패 사례 (171건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r428 · 드래곤 #281 L4: 왕까지 거리 5 → 최소 5 (1턴), 가는 길에 죽음 r429 희생
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:B:1 · r383 · 드래곤 #129 L4: 왕까지 거리 9 → 최소 6 (91턴), 가는 길에 죽음 r474 희생
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r386 · 드래곤 #81 L4: 왕까지 거리 13 → 최소 13 (1턴), 가는 길에 죽음 r413 돌진, 상대 길이 9
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r463 · 드래곤 #576 L11: 왕까지 거리 11 → 최소 7 (21턴)
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r350 · 드래곤 #174 L4: 왕까지 거리 8 → 최소 7 (21턴)
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:B:1 · r462 · 드래곤 #174 L11: 왕까지 거리 12 → 최소 7 (21턴)
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r347 · 드래곤 #306 L4: 왕까지 거리 19 → 최소 17 (3턴), 가는 길에 죽음 r386 희생
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r374 · 드래곤 #449 L4: 왕까지 거리 16 → 최소 4 (52턴), 가는 길에 죽음 r425 돌진, 상대 길이 26
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r351 · 드래곤 #248 L5: 왕까지 거리 6 → 최소 6 (1턴), 가는 길에 죽음 r417 아군 머리, 상대 길이 4
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:A:1 · r361 · 드래곤 #304 L4: 왕까지 거리 11 → 최소 10 (10턴), 가는 길에 죽음 r370 아군 머리, 상대 길이 2

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 875개 중 우리 팀 88% (지목한 아군 54%) · 상대 4% · 지목 아군 끝까지 생존 64% (그 뒤 죽은 원인: 희생 44, 갇힘 57, 돌진 4, 박힘(상대 돌진) 5, 아군 머리 5) · 지목 아군의 몸(자손 포함)이 끝까지 삶 87% · 최종 왕 51% (최종 왕이 지목 아군의 자손 64%)
- 비교: 실행 100% · 떨군 진주 1218개 중 우리 팀 87% (지목한 아군 55%) · 상대 7% · 지목 아군 끝까지 생존 62% (그 뒤 죽은 원인: 갇힘 80, 아군 머리 3, 희생 63, 박힘(상대 돌진) 20, 돌진 4) · 지목 아군의 몸(자손 포함)이 끝까지 삶 82% · 최종 왕 46% (최종 왕이 지목 아군의 자손 59%)
- 상대별: proxy4_elim 146회 90% · proxy4_king 96회 85% · proxy4_swarm 80회 86%
- 지도별: Autarky 95회 98% · Default 20회 75% · Devil 13회 69% · Portals 35회 86% · Prisoners Dilemma 34회 91% · Queen Of Spades 24회 63% · Schooltime 9회 89% · Slithery Fight 45회 89% · Trauma 47회 89%
- 국면별: r250-349 16회 100% · r350-449 224회 96% · r450+ 82회 65%

실패 사례 (39건 중 10건, 기보 확인용):
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

- 이번: 한입 100% · 2턴 안 분열 99% · 30라운드 뒤 가족 길이 변화 0.1 (줄지 않음 100%)
- 비교: 한입 100% · 2턴 안 분열 99% · 30라운드 뒤 가족 길이 변화 0.1 (줄지 않음 100%)
- 상대별: proxy4_elim 342회 98% · proxy4_king 338회 99% · proxy4_swarm 336회 99%
- 지도별: Devil 1회 100% · Portals 11회 55% · Prisoners Dilemma (10) 1002회 99% · Trauma 2회 0%
- 국면별: r0-99 204회 100% · r100-249 300회 100% · r250-349 205회 100% · r350-449 203회 98% · r450+ 104회 92%

실패 사례 (13건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:B:1 · r452 · 드래곤 #653 L18: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 3
- proxy4_elim · Trauma · 게임 exp/stack11-a-px4:proxy4_elim:trauma:B:1 · r468 · 드래곤 #232 L7: 한입, 분열(새끼 L6), 30라운드 뒤 가족 길이 변화 -1
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack11-b-px4-ks:proxy4_king:prisoners_dilemma_10:A:2 · r499 · 드래곤 #363 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/stack11-b-px4-ks:proxy4_swarm:prisoners_dilemma_10:B:2 · r499 · 드래곤 #342 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_elim · Prisoners Dilemma (10) · 게임 exp/stack11-b-px4-elim:proxy4_elim:prisoners_dilemma_10:A:2 · r499 · 드래곤 #308 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_elim · Portals · 게임 exp/stack11-b-px4-elim:proxy4_elim:portals:A:2 · r360 · 드래곤 #565 L8: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 3
- proxy4_king · Portals · 게임 exp/stack11-b-px4-ks:proxy4_king:portals:A:2 · r281 · 드래곤 #427 L4: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 -4
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack11-b-px4-ks:proxy4_king:prisoners_dilemma_10:B:2 · r499 · 드래곤 #330 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_king · Portals · 게임 exp/stack11-b-px4-ks:proxy4_king:portals:B:2 · r356 · 드래곤 #547 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 6
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/stack11-b-px4-ks:proxy4_swarm:prisoners_dilemma_10:A:2 · r499 · 드래곤 #368 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 21% · 30라운드 뒤 가족 길이 변화 8.4
- 비교: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 97% · 새끼 자체 10라운드 생존 22% · 30라운드 뒤 가족 길이 변화 8.3
- 상대별: proxy4_elim 2721회 98% · proxy4_king 2619회 97% · proxy4_swarm 2525회 98%
- 지도별: Autarky 3064회 100% · Default 45회 87% · Devil 85회 89% · Portals 1700회 94% · Prisoners Dilemma 1493회 99% · Prisoners Dilemma (10) 1000회 100% · Queen Of Spades 30회 83% · Schooltime 35회 94% · Slithery Fight 216회 94% · Trauma 176회 87% · Trophy 21회 71%
- 국면별: r0-99 1402회 99% · r100-249 2330회 98% · r250-349 1730회 97% · r350-449 1645회 97% · r450+ 758회 95%

실패 사례 (191건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r168 · 드래곤 #144 L7: 새끼 L5 → 새끼 죽음 r171 갇힘, 상대 길이 6, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7
- proxy4_king · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_king:prisoners_dilemma:A:1 · r483 · 드래곤 #405 L12: 새끼 L10 → 새끼 죽음 r487 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -12
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r40 · 드래곤 #5 L4: 새끼 L2 → 새끼 죽음 r42 돌진, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r343 · 드래곤 #328 L6: 새끼 L4 → 새끼 죽음 r343 갇힘, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -6
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r392 · 드래곤 #38 L4: 새끼 L2 → 새끼 죽음 r394 갇힘, 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r183 · 드래곤 #60 L5: 새끼 L3 → 새끼 죽음 r190 박힘(상대 돌진), 상대 길이 4, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:B:1 · r113 · 드래곤 #109 L4: 새끼 L2 → 새끼 죽음 r119 갇힘, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Portals · 게임 exp/stack11-a-px4:proxy4_swarm:portals:B:1 · r360 · 드래곤 #466 L6: 새끼 L4 → 새끼 죽음 r360 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -6
- proxy4_swarm · Schooltime · 게임 exp/stack11-a-px4:proxy4_swarm:schooltime:A:1 · r486 · 드래곤 #284 L4: 새끼 L2 → 새끼 죽음 r489 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_swarm:slithery_fight:A:1 · r252 · 드래곤 #476 L4: 새끼 L2 → 새끼 죽음 r254 갇힘, 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 86% · 그 밖(진짜로 갇힘) 1119회
- 비교: 탈출 분열 뒤 남은 조각(고리의 일부) 86% · 그 밖(진짜로 갇힘) 1129회
- 상대별: proxy4_elim 2831회 – · proxy4_king 2743회 – · proxy4_swarm 2612회 –
- 지도별: Autarky 3110회 – · Default 142회 – · Devil 89회 – · Portals 1553회 – · Prisoners Dilemma 1510회 – · Prisoners Dilemma (10) 1003회 – · Queen Of Spades 62회 – · Schooltime 61회 – · Slithery Fight 317회 – · Trauma 279회 – · Trophy 60회 –
- 국면별: r0-99 1469회 – · r100-249 2553회 – · r250-349 1850회 – · r350-449 1609회 – · r450+ 705회 –

## 정책 분열 (split)

- 이번: 분열 100% · 새끼 30라운드 생존 100% · 30라운드 뒤 가족 길이 변화 2
- 비교: 분열 100% · 새끼 30라운드 생존 100% · 30라운드 뒤 가족 길이 변화 3.3
- 상대별: proxy4_elim 1회 100% · proxy4_king 2회 100%
- 지도별: Default 1회 100% · Devil 1회 100% · Slithery Fight 1회 100%
- 국면별: r350-449 3회 100%

## 탈출 질주 3칸 (esc)

- 이번: 질주 98% · 짧은 적 머리 4칸 안 83% · 몸 생존 5라운드 96% · 10라운드 92% (드래곤 자체 85%) · 10라운드 길이 변화 -4.2
- 비교: 질주 99% · 짧은 적 머리 4칸 안 79% · 몸 생존 5라운드 95% · 10라운드 92% (드래곤 자체 85%) · 10라운드 길이 변화 -3.5
- 상대별: proxy4_elim 36회 81% · proxy4_king 42회 98% · proxy4_swarm 54회 93%
- 지도별: Autarky 1회 100% · Default 15회 87% · Devil 3회 100% · Prisoners Dilemma 2회 100% · Queen Of Spades 10회 90% · Schooltime 33회 91% · Slithery Fight 64회 91% · Trophy 4회 100%
- 국면별: r0-99 12회 100% · r100-249 25회 84% · r250-349 13회 100% · r350-449 28회 86% · r450+ 54회 93%

실패 사례 (12건 중 10건, 기보 확인용):
- proxy4_swarm · Schooltime · 게임 exp/stack11-a-px4:proxy4_swarm:schooltime:A:1 · r456 · 드래곤 #224 L6: 질주 3칸 (가장 가까운 짧은 적 머리 5칸) → 죽음 r461 돌진, 상대 길이 33
- proxy4_elim · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_elim:queen_of_spades:B:1 · r196 · 드래곤 #57 L15: 질주 3칸 (가장 가까운 짧은 적 머리 2칸) → 죽음 r204 갇힘
- proxy4_elim · Schooltime · 게임 exp/stack11-a-px4:proxy4_elim:schooltime:A:1 · r427 · 드래곤 #400 L56: 질주 3칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r429 적 몸통, 상대 길이 17
- proxy4_elim · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_elim:slithery_fight:B:1 · r405 · 드래곤 #389 L12: 질주 3칸 (가장 가까운 짧은 적 머리 12칸) → 죽음 r410 갇힘, 상대 길이 9
- proxy4_king · Slithery Fight · 게임 exp/stack11-b-px4-ks:proxy4_king:slithery_fight_b:A:2 · r238 · 드래곤 #513 L27: 질주 3칸 (가장 가까운 짧은 적 머리 2칸) → 죽음 r241 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack11-b-px4-ks:proxy4_swarm:default:A:2 · r495 · 드래곤 #150 L6: 질주 2칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r495 돌진, 상대 길이 3
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-b-px4-ks:proxy4_swarm:slithery_fight_b:A:2 · r470 · 드래곤 #914 L8: 질주 3칸 (가장 가까운 짧은 적 머리 16칸) → 죽음 r480 희생
- proxy4_elim · Default · 게임 exp/stack11-b-px4-elim:proxy4_elim:default:B:2 · r222 · 드래곤 #83 L8: 질주 3칸 (가장 가까운 짧은 적 머리 2칸) → 죽음 r230 박힘(상대 돌진), 상대 길이 4
- proxy4_elim · Schooltime · 게임 exp/stack11-a-px4:proxy4_elim:schooltime:A:1 · r429 · 드래곤 #400 L54: 질주 3칸 (가장 가까운 짧은 적 머리 2칸) → 죽음 r429 적 몸통, 상대 길이 17
- proxy4_swarm · Slithery Fight · 게임 exp/stack11-b-px4-ks:proxy4_swarm:slithery_fight_b:A:2 · r471 · 드래곤 #914 L6: 질주 3칸 (가장 가까운 짧은 적 머리 20칸) → 죽음 r480 희생

## 위협 피하기 2칸 질주

- 이번: 질주 100% · 몸 10라운드 생존 94% (드래곤 자체 89%)
- 비교: 질주 100% · 몸 10라운드 생존 93% (드래곤 자체 89%)
- 상대별: proxy4_elim 383회 91% · proxy4_king 349회 94% · proxy4_swarm 415회 94%
- 지도별: Autarky 55회 95% · Default 173회 94% · Devil 90회 88% · Prisoners Dilemma (10) 8회 100% · Queen Of Spades 155회 94% · Schooltime 249회 93% · Slithery Fight 288회 94% · Trauma 41회 98% · Trophy 88회 89%
- 국면별: r0-99 245회 93% · r100-249 413회 93% · r250-349 214회 94% · r350-449 245회 93% · r450+ 30회 100%

실패 사례 (78건 중 10건, 기보 확인용):
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

- 이번: 미탐색 출구 2264회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 94% (드래곤 자체 78%) · 10라운드 88% · 10라운드 안 먹은 진주 0.9
- 비교: 미탐색 출구 2298회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 94% (드래곤 자체 78%) · 10라운드 89% · 10라운드 안 먹은 진주 0.9
- 상대별: proxy4_elim 1931회 93% · proxy4_king 1943회 94% · proxy4_swarm 1386회 93%
- 지도별: Autarky 838회 95% · Default 869회 94% · Portals 2349회 93% · Prisoners Dilemma 76회 97% · Prisoners Dilemma (10) 39회 100% · Queen Of Spades 116회 78% · Schooltime 198회 94% · Slithery Fight 370회 95% · Trauma 401회 95% · Trophy 4회 100%
- 국면별: r0-99 632회 96% · r100-249 1981회 95% · r250-349 1595회 93% · r350-449 866회 91% · r450+ 186회 88%

실패 사례 (341건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r158 · 드래곤 #35 L3: 포털(미탐색 출구) → 죽음 r160 박힘(상대 돌진), 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r166 · 드래곤 #125 L3: 포털 → 죽음 r168 갇힘, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Portals · 게임 exp/stack11-a-px4:proxy4_king:portals:A:1 · r42 · 드래곤 #16 L2: 포털(미탐색 출구) → 죽음 r42 아군 머리, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r39 · 드래곤 #5 L4: 포털 → 죽음 r41 갇힘, 10라운드 안 진주 0
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r297 · 드래곤 #177 L4: 포털 → 죽음 r297 갇힘, 상대 길이 15, 10라운드 안 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r82 · 드래곤 #16 L24: 포털(미탐색 출구) → 죽음 r82 아군 머리, 상대 길이 4, 10라운드 안 진주 0
- proxy4_king · Trauma · 게임 exp/stack11-a-px4:proxy4_king:trauma:A:1 · r299 · 드래곤 #71 L3: 포털 → 죽음 r299 돌진, 상대 길이 3, 10라운드 안 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:A:1 · r238 · 드래곤 #181 L3: 포털 → 죽음 r238 아군 머리, 상대 길이 16, 10라운드 안 진주 0
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r148 · 드래곤 #33 L3: 포털(미탐색 출구) → 죽음 r149 박힘(상대 돌진), 상대 길이 3, 10라운드 안 진주 0
- proxy4_swarm · Prisoners Dilemma · 게임 exp/stack11-a-px4:proxy4_swarm:prisoners_dilemma:A:1 · r30 · 드래곤 #4 L3: 포털 → 죽음 r30 아군 머리, 상대 길이 3, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 327, 경로 52) · 잡은 길이 ≥ 우리 91% · 두 몸의 진주 우리 639 대 상대 755
- 비교: 충돌 성사 100% (인접 326, 경로 54) · 잡은 길이 ≥ 우리 91% · 두 몸의 진주 우리 590 대 상대 766
- 상대별: proxy4_elim 129회 43% · proxy4_king 121회 49% · proxy4_swarm 129회 51%
- 지도별: Autarky 6회 33% · Default 78회 54% · Devil 33회 42% · Prisoners Dilemma (10) 2회 0% · Queen Of Spades 38회 55% · Schooltime 64회 34% · Slithery Fight 109회 52% · Trauma 15회 53% · Trophy 34회 41%
- 국면별: r0-99 85회 41% · r100-249 137회 45% · r250-349 85회 53% · r350-449 61회 52% · r450+ 11회 64%

실패 사례 (199건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack11-a-px4:proxy4_king:default:A:1 · r5 · 드래곤 #2 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_king · Autarky · 게임 exp/stack11-a-px4:proxy4_king:autarky:B:1 · r46 · 드래곤 #3 L3: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 3
- proxy4_king · Devil · 게임 exp/stack11-a-px4:proxy4_king:devil:A:1 · r413 · 드래곤 #81 L7: 돌진 경로 4칸 → 상대 L9 잡음, 진주 우리 0 대 상대 8
- proxy4_king · Queen Of Spades · 게임 exp/stack11-a-px4:proxy4_king:queen_of_spades:A:1 · r202 · 드래곤 #4 L3: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 3
- proxy4_king · Schooltime · 게임 exp/stack11-a-px4:proxy4_king:schooltime:B:1 · r140 · 드래곤 #58 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_king · Slithery Fight · 게임 exp/stack11-a-px4:proxy4_king:slithery_fight:A:1 · r58 · 드래곤 #155 L2: 돌진 경로 2칸 → 상대 L3 잡음, 진주 우리 1 대 상대 3
- proxy4_king · Trophy · 게임 exp/stack11-a-px4:proxy4_king:trophy:A:1 · r76 · 드래곤 #2 L2: 돌진 경로 1칸 → 상대 L3 잡음, 진주 우리 0 대 상대 3
- proxy4_swarm · Autarky · 게임 exp/stack11-a-px4:proxy4_swarm:autarky:A:1 · r251 · 드래곤 #2 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_swarm · Default · 게임 exp/stack11-a-px4:proxy4_swarm:default:A:1 · r103 · 드래곤 #6 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_swarm · Devil · 게임 exp/stack11-a-px4:proxy4_swarm:devil:B:1 · r59 · 드래곤 #43 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 비교: 먹음 100%
- 상대별: proxy4_elim 125회 100% · proxy4_king 110회 100% · proxy4_swarm 93회 100%
- 지도별: Autarky 10회 100% · Default 42회 100% · Devil 23회 100% · Portals 66회 100% · Prisoners Dilemma (10) 2회 100% · Queen Of Spades 36회 100% · Schooltime 38회 100% · Slithery Fight 74회 100% · Trauma 12회 100% · Trophy 25회 100%
- 국면별: r0-99 45회 100% · r100-249 93회 100% · r250-349 75회 100% · r350-449 110회 100% · r450+ 5회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 86%
- 비교: 그 턴 사망 0% · 10라운드 생존 85%
- 상대별: proxy4_elim 45회 – · proxy4_king 42회 – · proxy4_swarm 36회 –
- 지도별: Autarky 7회 – · Default 10회 – · Devil 8회 – · Portals 1회 – · Queen Of Spades 16회 – · Schooltime 31회 – · Slithery Fight 36회 – · Trauma 5회 – · Trophy 9회 –
- 국면별: r0-99 24회 – · r100-249 44회 – · r250-349 17회 – · r350-449 33회 – · r450+ 5회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 비교: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 14회 – · proxy4_king 14회 – · proxy4_swarm 12회 –
- 지도별: Default 2회 – · Devil 17회 – · Queen Of Spades 8회 – · Schooltime 3회 – · Slithery Fight 2회 – · Trauma 6회 – · Trophy 2회 –
- 국면별: r0-99 5회 – · r100-249 14회 – · r250-349 16회 – · r350-449 3회 – · r450+ 2회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/stack11-a-px4+exp/stack11-b-px4-ks+exp/stack11-b-px4-elim` | 120 | 31 (0.26) | 71% | 0 (0.00) | 0 (0.00) | 4 | 23 | 1 | 2/3 (3.5) | 194 (1.62; 필사 30) | 54/134 (94.5) |
| · exp/stack11-a-px4 | 60 | 17 (0.28) | 71% | 0 (0.00) | 0 (0.00) | 2 | 12 | 1 | 2/3 (7) | 95 (1.58; 필사 14) | 29/64 (101.5) |
| · exp/stack11-b-px4-ks | 40 | 4 (0.10) | 100% | 0 (0.00) | 0 (0.00) | 0 | 4 | 0 | 0/0 (0) | 64 (1.60; 필사 12) | 19/44 (99.8) |
| · exp/stack11-b-px4-elim | 20 | 10 (0.50) | 60% | 0 (0.00) | 0 (0.00) | 2 | 7 | 0 | 0/0 (0) | 35 (1.75; 필사 4) | 6/26 (63) |
| 비교 `exp/stack10-a-px4+exp/stack10-b-px4` | 120 | 38 (0.32) | 68% | 1 (0.01) | 0 (0.00) | 3 | 29 | 2 | 4/7 (7) | 192 (1.60; 필사 32) | 48/111 (84) |
| · exp/stack10-a-px4 | 60 | 20 (0.33) | 75% | 1 (0.02) | 0 (0.00) | 1 | 14 | 1 | 4/6 (14) | 99 (1.65; 필사 15) | 26/58 (91) |
| · exp/stack10-b-px4 | 60 | 18 (0.30) | 61% | 0 (0.00) | 0 (0.00) | 2 | 15 | 1 | 0/1 (0) | 93 (1.55; 필사 17) | 22/53 (77) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.
- 이번 `exp/stack11-a-px4+exp/stack11-b-px4-ks+exp/stack11-b-px4-elim`: gx 표식 턴 1927 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- · exp/stack11-a-px4: gx 표식 턴 1014 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- · exp/stack11-b-px4-ks: gx 표식 턴 654 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- · exp/stack11-b-px4-elim: gx 표식 턴 259 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- 비교 `exp/stack10-a-px4+exp/stack10-b-px4`: gx 표식 턴 795 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- · exp/stack10-a-px4: gx 표식 턴 313 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- · exp/stack10-b-px4: gx 표식 턴 482 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/stack11-a-px4+exp/stack11-b-px4-ks+exp/stack11-b-px4-elim` | 120 | 74112 | 0.7% (497) | 16.8% (12429) | 8039 | 1.8% (145) | 3.9% (317) | 23.8% (1915/8039) |
| · exp/stack11-a-px4 | 60 | 38942 | 0.8% (307) | 16.0% (6226) | 4390 | 1.9% (82) | 4.0% (176) | 23.0% (1008/4390) |
| · exp/stack11-b-px4-ks | 40 | 22459 | 0.6% (140) | 18.8% (4231) | 2469 | 1.7% (43) | 4.3% (106) | 28.2% (697/2469) |
| · exp/stack11-b-px4-elim | 20 | 12711 | 0.4% (50) | 15.5% (1972) | 1180 | 1.7% (20) | 3.0% (35) | 17.8% (210/1180) |
| 비교 `exp/stack10-a-px4+exp/stack10-b-px4` | 120 | 71469 | 0.6% (426) | 16.9% (12086) | 7684 | 1.3% (97) | 3.3% (252) | 22.8% (1751/7684) |
| · exp/stack10-a-px4 | 60 | 36921 | 0.6% (223) | 16.4% (6047) | 4093 | 1.0% (40) | 2.8% (115) | 20.7% (846/4093) |
| · exp/stack10-b-px4 | 60 | 34548 | 0.6% (203) | 17.5% (6039) | 3591 | 1.6% (57) | 3.8% (137) | 25.2% (905/3591) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/stack11-a-px4+exp/stack11-b-px4-ks+exp/stack11-b-px4-elim` | 전체 | 분열 | 13 (23%) | 11.8 | 77% | 76% | 8 | 2 |
| 이번 `exp/stack11-a-px4+exp/stack11-b-px4-ks+exp/stack11-b-px4-elim` | 전체 | 2칸 질주 | 14 (25%) | 12.8 | 106% | 111% | 6 | 1 |
| 이번 `exp/stack11-a-px4+exp/stack11-b-px4-ks+exp/stack11-b-px4-elim` | 전체 | 3칸 질주 | 10 (18%) | 15.8 | 115% | 112% | 1 | 1 |
| 이번 `exp/stack11-a-px4+exp/stack11-b-px4-ks+exp/stack11-b-px4-elim` | 전체 | 한 걸음 | 19 (34%) | 10.5 | 32% | 25% | 16 | 9 |
| 이번 `exp/stack11-a-px4+exp/stack11-b-px4-ks+exp/stack11-b-px4-elim` | 4칸 이상 | 분열 | 7 (29%) | 13 | 85% | 88% | 5 | 0 |
| 이번 `exp/stack11-a-px4+exp/stack11-b-px4-ks+exp/stack11-b-px4-elim` | 4칸 이상 | 2칸 질주 | 7 (29%) | 14.3 | 97% | 92% | 4 | 1 |
| 이번 `exp/stack11-a-px4+exp/stack11-b-px4-ks+exp/stack11-b-px4-elim` | 4칸 이상 | 3칸 질주 | 2 (8%) | 37.5 | 183% | 181% | 0 | 0 |
| 이번 `exp/stack11-a-px4+exp/stack11-b-px4-ks+exp/stack11-b-px4-elim` | 4칸 이상 | 한 걸음 | 8 (33%) | 10.4 | 35% | 25% | 7 | 4 |
| · exp/stack11-a-px4 | 전체 | 분열 | 5 (18%) | 10.2 | 45% | 59% | 4 | 2 |
| · exp/stack11-a-px4 | 전체 | 2칸 질주 | 5 (18%) | 14.6 | 110% | 141% | 2 | 1 |
| · exp/stack11-a-px4 | 전체 | 3칸 질주 | 6 (21%) | 17.8 | 155% | 151% | 0 | 0 |
| · exp/stack11-a-px4 | 전체 | 한 걸음 | 12 (43%) | 9.8 | 42% | 28% | 10 | 4 |
| · exp/stack11-a-px4 | 4칸 이상 | 분열 | 2 (18%) | 9.5 | 84% | 95% | 2 | 0 |
| · exp/stack11-a-px4 | 4칸 이상 | 2칸 질주 | 2 (18%) | 26 | 73% | 75% | 1 | 1 |
| · exp/stack11-a-px4 | 4칸 이상 | 3칸 질주 | 2 (18%) | 37.5 | 183% | 181% | 0 | 0 |
| · exp/stack11-a-px4 | 4칸 이상 | 한 걸음 | 5 (45%) | 9.6 | 48% | 27% | 5 | 2 |
| · exp/stack11-b-px4-ks | 전체 | 분열 | 4 (25%) | 10 | 103% | 75% | 2 | 0 |
| · exp/stack11-b-px4-ks | 전체 | 2칸 질주 | 6 (38%) | 12.7 | 91% | 72% | 1 | 0 |
| · exp/stack11-b-px4-ks | 전체 | 3칸 질주 | 3 (19%) | 15 | 29% | 24% | 1 | 1 |
| · exp/stack11-b-px4-ks | 전체 | 한 걸음 | 3 (19%) | 6.7 | 30% | 40% | 2 | 2 |
| · exp/stack11-b-px4-ks | 4칸 이상 | 분열 | 2 (29%) | 10.5 | 90% | 67% | 1 | 0 |
| · exp/stack11-b-px4-ks | 4칸 이상 | 2칸 질주 | 3 (43%) | 10 | 97% | 73% | 1 | 0 |
| · exp/stack11-b-px4-ks | 4칸 이상 | 한 걸음 | 2 (29%) | 6 | 50% | 67% | 1 | 1 |
| · exp/stack11-b-px4-elim | 전체 | 분열 | 4 (33%) | 15.8 | 86% | 90% | 2 | 0 |
| · exp/stack11-b-px4-elim | 전체 | 2칸 질주 | 3 (25%) | 10 | 133% | 137% | 3 | 0 |
| · exp/stack11-b-px4-elim | 전체 | 3칸 질주 | 1 (8%) | 6 | 50% | 67% | 0 | 0 |
| · exp/stack11-b-px4-elim | 전체 | 한 걸음 | 4 (33%) | 15.5 | 13% | 15% | 4 | 3 |
| · exp/stack11-b-px4-elim | 4칸 이상 | 분열 | 3 (50%) | 17 | 82% | 94% | 2 | 0 |
| · exp/stack11-b-px4-elim | 4칸 이상 | 2칸 질주 | 2 (33%) | 9 | 167% | 172% | 2 | 0 |
| · exp/stack11-b-px4-elim | 4칸 이상 | 한 걸음 | 1 (17%) | 23 | 0% | 0% | 1 | 1 |
| 비교 `exp/stack10-a-px4+exp/stack10-b-px4` | 전체 | 분열 | 8 (15%) | 11.8 | 95% | 85% | 3 | 0 |
| 비교 `exp/stack10-a-px4+exp/stack10-b-px4` | 전체 | 2칸 질주 | 14 (26%) | 12.2 | 93% | 81% | 5 | 0 |
| 비교 `exp/stack10-a-px4+exp/stack10-b-px4` | 전체 | 3칸 질주 | 7 (13%) | 12.1 | 65% | 66% | 1 | 1 |
| 비교 `exp/stack10-a-px4+exp/stack10-b-px4` | 전체 | 한 걸음 | 25 (46%) | 12 | 25% | 21% | 21 | 14 |
| 비교 `exp/stack10-a-px4+exp/stack10-b-px4` | 4칸 이상 | 분열 | 5 (20%) | 13.6 | 94% | 79% | 2 | 0 |
| 비교 `exp/stack10-a-px4+exp/stack10-b-px4` | 4칸 이상 | 2칸 질주 | 6 (24%) | 14.5 | 107% | 91% | 3 | 0 |
| 비교 `exp/stack10-a-px4+exp/stack10-b-px4` | 4칸 이상 | 3칸 질주 | 2 (8%) | 10 | 110% | 130% | 0 | 0 |
| 비교 `exp/stack10-a-px4+exp/stack10-b-px4` | 4칸 이상 | 한 걸음 | 12 (48%) | 13.3 | 19% | 14% | 11 | 9 |
| · exp/stack10-a-px4 | 전체 | 분열 | 3 (13%) | 10.3 | 84% | 106% | 1 | 0 |
| · exp/stack10-a-px4 | 전체 | 2칸 질주 | 3 (13%) | 17.7 | 83% | 74% | 1 | 0 |
| · exp/stack10-a-px4 | 전체 | 3칸 질주 | 2 (9%) | 10 | 100% | 95% | 0 | 0 |
| · exp/stack10-a-px4 | 전체 | 한 걸음 | 15 (65%) | 11.1 | 33% | 26% | 12 | 6 |
| · exp/stack10-a-px4 | 4칸 이상 | 분열 | 1 (13%) | 13 | 85% | 77% | 1 | 0 |
| · exp/stack10-a-px4 | 4칸 이상 | 2칸 질주 | 1 (13%) | 40 | 95% | 98% | 0 | 0 |
| · exp/stack10-a-px4 | 4칸 이상 | 한 걸음 | 6 (75%) | 12 | 25% | 14% | 6 | 4 |
| · exp/stack10-b-px4 | 전체 | 분열 | 5 (16%) | 12.6 | 100% | 75% | 2 | 0 |
| · exp/stack10-b-px4 | 전체 | 2칸 질주 | 11 (35%) | 10.7 | 97% | 84% | 4 | 0 |
| · exp/stack10-b-px4 | 전체 | 3칸 질주 | 5 (16%) | 13 | 54% | 57% | 1 | 1 |
| · exp/stack10-b-px4 | 전체 | 한 걸음 | 10 (32%) | 13.4 | 15% | 16% | 9 | 8 |
| · exp/stack10-b-px4 | 4칸 이상 | 분열 | 4 (24%) | 13.8 | 96% | 80% | 1 | 0 |
| · exp/stack10-b-px4 | 4칸 이상 | 2칸 질주 | 5 (29%) | 9.4 | 117% | 85% | 3 | 0 |
| · exp/stack10-b-px4 | 4칸 이상 | 3칸 질주 | 2 (12%) | 10 | 110% | 130% | 0 | 0 |
| · exp/stack10-b-px4 | 4칸 이상 | 한 걸음 | 6 (35%) | 14.5 | 14% | 14% | 5 | 5 |

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (194건 중 10건):
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

이번 (120판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 12 | 100% | 100% | 72/72 (72) | 3499 | 3499 (0) | 0 | 0 | 0 | 0 |
| Default a | 12 | 100% | 100% | 48/48 (48) | 480 | 479 (0) | 0 | 0 | 0 | 0 |
| Devil a | 6 | 100% | 100% | 18/18 (18) | 166 | 164 (0) | 1 | 1 | 0 | 19 |
| Devil b | 6 | 100% | 100% | 18/18 (18) | 123 | 122 (0) | 0 | 0 | 0 | 17 |
| Portals a | 12 | 100% | 100% | 36/36 (36) | 1958 | 1958 (0) | 0 | 0 | 0 | 1 |
| Prisoners Dilemma a | 6 | 100% | 100% | 6/18 (6) | 1562 | 1555 (0) | 7 | 0 | 0 | 177 |
| Prisoners Dilemma b | 6 | 100% | 100% | 18/30 (18) | 1038 | 1034 (0) | 4 | 0 | 0 | 305 |
| Queen Of Spades a | 6 | 100% | 100% | 12/12 (12) | 145 | 140 (0) | 4 | 0 | 0 | 29 |
| Queen Of Spades b | 6 | 100% | 100% | 12/12 (12) | 95 | 91 (0) | 2 | 0 | 0 | 71 |
| Schooltime a | 6 | 100% | 100% | 18/18 (18) | 259 | 259 (0) | 0 | 0 | 0 | 16 |
| Schooltime b | 6 | 100% | 100% | 36/36 (36) | 95 | 95 (0) | 0 | 0 | 0 | 7 |
| Slithery Fight a | 6 | 100% | 100% | 48/48 (48) | 380 | 367 (0) | 13 | 0 | 0 | 56 |
| Slithery Fight b | 6 | 100% | 100% | 48/48 (48) | 427 | 409 (0) | 17 | 0 | 0 | 27 |
| Trauma a | 12 | 100% | 100% | 24/24 (24) | 506 | 505 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 12 | 100% | 100% | 24/24 (24) | 199 | 197 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 120/120, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

비교 (120판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 12 | 100% | 100% | 72/72 (72) | 3498 | 3498 (0) | 0 | 0 | 0 | 0 |
| Default a | 12 | 100% | 100% | 48/48 (48) | 463 | 462 (0) | 0 | 0 | 0 | 0 |
| Devil a | 6 | 100% | 100% | 18/18 (18) | 164 | 162 (0) | 1 | 1 | 0 | 19 |
| Devil b | 6 | 100% | 100% | 18/18 (18) | 123 | 122 (0) | 0 | 0 | 0 | 17 |
| Portals a | 12 | 100% | 100% | 36/36 (36) | 1959 | 1959 (0) | 0 | 0 | 0 | 1 |
| Prisoners Dilemma a | 6 | 100% | 100% | 6/18 (6) | 1534 | 1526 (0) | 8 | 0 | 0 | 195 |
| Prisoners Dilemma b | 6 | 100% | 100% | 18/30 (18) | 1038 | 1034 (0) | 4 | 0 | 0 | 305 |
| Queen Of Spades a | 6 | 100% | 100% | 12/12 (12) | 147 | 141 (0) | 5 | 0 | 0 | 29 |
| Queen Of Spades b | 6 | 100% | 100% | 12/12 (12) | 101 | 99 (0) | 1 | 0 | 0 | 71 |
| Schooltime a | 6 | 100% | 100% | 18/18 (18) | 287 | 286 (0) | 0 | 0 | 0 | 16 |
| Schooltime b | 6 | 100% | 100% | 36/36 (36) | 95 | 95 (0) | 0 | 0 | 0 | 7 |
| Slithery Fight a | 6 | 100% | 100% | 48/48 (48) | 377 | 368 (0) | 9 | 0 | 0 | 48 |
| Slithery Fight b | 6 | 100% | 100% | 48/48 (48) | 420 | 406 (0) | 13 | 0 | 0 | 32 |
| Trauma a | 12 | 100% | 100% | 24/24 (24) | 500 | 500 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 12 | 100% | 100% | 24/24 (24) | 193 | 191 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 120/120, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

### Schooltime 판의 경제 (bsp의 가설 수준 지표, 정답 판본별)

| 묶음 | 판본 | 판 | 드래곤 수 r50 | r100 | r0–99 자연 진주 먹음 | 전멸당함 | 끝 최장(전멸 0) | 판당 bsp 분열 |
|---|---|---:|---|---|---|---:|---|---:|
| 이번 | a | 6 | 9 [8, 10] | 15 [13, 16] | 30 [22, 48] | 0% | 29 [15, 34] | 0 |
| 이번 | b | 6 | 8 [7, 8] | 11 [8, 11] | 12 [7, 17] | 17% | 10 [5, 12] | 9.8 |
| 비교 | a | 6 | 9 [8, 10] | 15 [13, 16] | 30 [22, 48] | 0% | 23 [9, 34] | 0 |
| 비교 | b | 6 | 8 [7, 8] | 11 [8, 11] | 12 [7, 17] | 17% | 12 [5, 13] | 9.8 |

- 기준값(`research/experiments/cand-mapid.md`, 웨이브 전에 적음): b에서 드래곤 수 r50 중앙 ≥ 6, r0–99 자연 진주 중앙 ≥ 14. 우리 merge2 계열 b 29판은 3 · 9, 떼 계열(swarm8·px) b 14판은 6 · 14, 상위권 b 승자는 8 · 32다. a는 bsp가 켜지지 않는 대조군이다.

## stack5: 영토 덮기 (csplit · F · cov) 게이트와 가설 수준 지표

- 기준값은 `research/experiments/cand-stack5.md`(웨이브 전)에서, 상위권 승자(TW) 값과 merge2 값은 `research/observations/top-territory.md`에서 왔다. 정의는 영토 연구의 `exp/territory-analysis/extract.js`와 같다(영토 = 시작 몸에서 더 가까운 팀의 칸, 샘 = 그 판 판본 파일의 평균 간격 ≤12, 보로노이 = 용량 1/평균 간격 가중, 거리 = 지도 위 이동 거리, 몸은 무시).

### 게이트 (기능 적용)

| 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|
| csplit 발동: 500라운드형 지도 r0–249 판당 | ≥20 | 18.3 (전체 1875회) | 18.3 (전체 1870회) |
| csplit 설계 상황: 부모가 팀 최장(≥8)이 아님 | ≥90% | 100% | 100% |
| csplit 새끼가 30라운드 안에 자연 진주 ≥1개 | ≥45% (TW 47% · 45%) | 38% (1875마리) | 38% (1870마리) |
| csplit 새끼 30라운드 생존 | ≥30% (TW 34% · 51%) | 73% | 73% |
| F 목표(드래곤·샘) 수, 3걸음 안 도착 | – | 2096, 도착 59% | 2093, 도착 59% |
| F 설계 상황: 실제 우리 영토 샘, 처음 표식 때 다른 우리 머리 3걸음 안 없음 | ≥80% | 82% | 82% |
| F 도착 뒤 30라운드 그 무리 자연 진주의 우리 몫(합산) | ≥85% (TW 자기 샘 90%) | 91% (상대 8%, 4791개) | 91% (상대 8%, 4829개) |
| F 같은 몫의 지도 평균(지도마다 합산, 같은 무게, Portals 제외) | ≥85% | 71% (Devil 67%, Prisoners Dilemma 100%, Slithery Fight 65%, Trauma 95%, Autarky 0%, Prisoners Dilemma (10) 100%) | 71% (Devil 67%, Prisoners Dilemma 100%, Slithery Fight 66%, Trauma 95%, Autarky 0%, Prisoners Dilemma (10) 100%) |
| cov 턴, 20라운드 안 우리 영토 자연 진주 | – | 59433, 20% | 60148, 20% |

### 가설 수준 지표 (관찰; 500라운드형 / 전멸형)

| 지표 | 기준 | 상위권 승자 | merge2 | 이번 | 비교 |
|---|---|---|---|---|---|
| r100 우리 드래곤 수(r100까지 간 판) | ≥15 / ≥10 | 30 / 21 | 4 / 3 | 11.1 / 6.1 | 11.1 / 6.1 |
| r100 우리 영토 보로노이 몫(용량 가중, 판 평균) | ≥80% | 89% / 81% | 66% / 32% | 71% / 32% | 71% / 32% |
| r100 샘 지킴: 우리 영토 샘 중 우리 머리 3걸음 안(판 평균) | ≥50% | 61% / 55% | 22% / – | 29% / 46% | 29% / 46% |
| 우리 영토 자연 진주(r0부터 생성)를 상대가 먹은 몫(합산) | ≤25% | 11% / 16% | 56% / 55% | 53% / 61% | 53% / 61% |
| 우리 영토 샘 진주를 상대가 먹은 몫(합산) | ≤15% | 7% / 6% | 50% / 33% | 48% / 47% | 48% / 47% |

- 판 수(500라운드형 / 전멸형): 이번 60 / 60 · 비교 60 / 60. 판본 파일을 못 찾은 판: 이번 0 · 비교 0.

### 부작용: 우리 드래곤의 죽음 (판당; 전체 / r250 전)

| 원인 | 이번 | 비교 |
|---|---|---|
| 갇힘(빈 이웃 없음; 통로 고리의 남은 조각 포함) | 69.1 / 33.8 | 68.8 / 33.8 |
| 적 머리에 박힘 | 6.7 / 4.4 | 6.6 / 4.3 |
| 우리 드래곤끼리 머리 충돌(둘 다 죽음, 둘 다 셈) | 2.1 / 0.9 | 2.1 / 0.9 |

- 막힘에서 아군 머리를 피해 죽은 턴(no-exit s): 이번 231 · 비교 227

### 지도별 (이번)

| 지도 | 판 | csplit 판당 | 새끼 먹음 ≥1 | 새끼 30R 생존 | F 목표 · 도착 · 무리 진주 우리 몫 | r100 드래곤 | 보로노이 | 샘 지킴 | 상대가 먹은 영토 진주 | 상대가 먹은 샘 진주 |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| Autarky | 12 | 19.8 | 37% | 94% | 52 · 8% · 0% | 11.3 | 96% | 86% | 8% | 8% |
| Default | 12 | 24.8 | 39% | 60% | 0 · – · – | 9.1 | 26% | – | 77% | – |
| Devil | 12 | 11.3 | 28% | 70% | 132 · 48% · 67% | 6.4 | 25% | 16% | 83% | 86% |
| Portals | 12 | 12.4 | 43% | 57% | 1065 · 78% · 100% | 11.3 | 100% | 35% | 0% | 0% |
| Prisoners Dilemma (10) | 6 | 1.3 | 0% | 63% | 13 · 8% · 100% | 3.8 | 47% | 50% | 24% | 0% |
| Prisoners Dilemma | 6 | 7.3 | 45% | 91% | 58 · 45% · 100% | 3.7 | 99% | 100% | 2% | 0% |
| Queen Of Spades | 12 | 11.6 | 33% | 74% | 0 · – · – | 4 | 10% | – | 75% | – |
| Schooltime | 12 | 13.6 | 41% | 86% | 10 · 0% · – | 12 | 37% | 0% | 79% | 88% |
| Slithery Fight | 12 | 28.9 | 31% | 79% | 628 · 43% · 65% | 14.6 | 27% | 3% | 78% | 83% |
| Trauma | 12 | 16.8 | 44% | 59% | 138 · 28% · 95% | 6.3 | 94% | 8% | 55% | 0% |
| Trophy | 12 | 12.7 | 48% | 64% | 0 · – · – | 7.3 | 24% | – | 62% | – |

## stack7: 수 바닥 분열(floor)과 왕 길이 상한(kcap) 게이트, 저수 에피소드, 가설 수준 지표, 지도 가르기

- 기준값은 `research/experiments/cand-stack7.md`(웨이브 전)에서, 상위권·우리 값은 `research/observations/our-eliminations.md`(2.6절, 1.3절, 2.2절)에서 왔다. 저수 에피소드와 부류의 정의는 전멸 연구(`exp/eliminations/top.js` I, `lib.js` classOf)와 같다: r50부터 5라운드 간격으로 처음 우리 수 1–3·상대 ≥8인 라운드 r(라운드 첫 턴의 수; r+20이 판 안이고 우리 전멸 전), 그 뒤 [r, r+20) 분열, 20라운드 뒤 4마리 이상이면 회복, 50라운드 안 전멸. 연구의 분열 수는 10라운드 칸 두 개의 전체 분열(탈출 분열 포함)이고, 여기서는 [r, r+20)을 그대로 센다.

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| floor | 발동(판당; floor 지도 판) | – | 42 (0.5; 84판) | 42 (0.5; 84판) |
| floor | 1. 설계 상황: 발동 때 상대 ≥8마리 | ≥90% | 71% | 71% |
| floor | 저수 에피소드가 있는 floor 지도 판 · 그 20라운드 안 floor 발동이 있었던 판 | (관찰) | 56 · 5% | 60 · 3% |
| floor | 2. 즉시 효과 A: 에피소드 20라운드 비탈출 분열(판당; floor 지도) | ≥2.0 (상위 LX·LS 2.0, 우리 0.5) | 0.2 (floor 0.1, kcap 0, csplit 0.1, lsplit 0; 탈출 포함 전체 0.2) | 0.2 (floor 0, kcap 0, csplit 0.1, lsplit 0; 탈출 포함 전체 0.2) |
| floor | 3. 즉시 효과 B: 에피소드 20라운드 뒤 4마리 이상(floor 지도) | ≥23% (상위 LX 23%, LS 26%, 우리 5%) | 9% (5/56) | 7% (4/60) |
| floor | 4. 즉시 효과 C: floor 새끼 30라운드 생존 | ≥34% (상위 패자 제 영토 새끼 34%, 승자 51%) | 57% (42마리) | 62% (42마리) |
| kcap | 발동(판당; kcap 지도 판) | – | 2 (0; 72판) | 2 (0; 72판) |
| kcap | 1. 설계 상황: 부모가 그 순간 팀 최장이고 r250 전 | ≥90% | 100% | 100% |
| kcap | 2. 즉시 효과: 새끼 10라운드 생존 | ≥74% (상위권 길이 4 분열 74.2%) | 100% (2마리) | 100% (2마리) |
| kcap | 2. 즉시 효과: 부모 10라운드 생존 | ≥55% (상위권 54.5%) | 50% | 50% |

### 저수 에피소드 (floor 지도 / 모든 지도; 판정은 floor 지도)

| 묶음 | 지도 | 판 | 에피소드 있음 | 처음 라운드(중앙) | 그때 우리 수 · 상대 수 | 그때 총길이 · 최장 | 20라운드 비탈출 분열 | floor · kcap | 탈출 포함 전체 | 20라운드 뒤 4마리 이상 | 50라운드 안 전멸 |
|---|---|---:|---:|---:|---|---|---:|---|---:|---:|---:|
| 이번 | floor 지도 | 84 | 67% | 165 | 2.9 · 30.7 | 10.2 · 5.1 | 0.2 | 0.1 · 0 | 0.2 | 9% | 14% |
| 이번 | floor 지도 중 전멸형 | 48 | 90% | 140 | 2.9 · 30 | 7.7 · 3.2 | 0.2 | 0.1 · 0 | 0.3 | 12% | 16% |
| 이번 | floor 지도 중 500형 | 36 | 36% | 430 | 3 · 33 | 18.5 · 11.4 | 0 | 0 · 0 | 0.1 | 0% | 8% |
| 이번 | 끄는 지도(Autarky·PD·Portals) | 36 | 47% | 390 | 2.9 · 18.9 | 28.1 · 16.4 | 0.2 | 0 · 0 | 9.2 | 24% | 0% |
| 이번 | 모든 지도 | 120 | 61% | 175 | 2.9 · 28 | 14.4 · 7.7 | 0.2 | 0 · 0 | 2.3 | 12% | 11% |
| 비교 | floor 지도 | 84 | 71% | 167.5 | 2.9 · 30 | 11 · 5.4 | 0.2 | 0 · 0 | 0.2 | 7% | 13% |
| 비교 | floor 지도 중 전멸형 | 48 | 92% | 142.5 | 2.9 · 29.9 | 7.4 · 3 | 0.2 | 0 · 0 | 0.3 | 9% | 16% |
| 비교 | floor 지도 중 500형 | 36 | 44% | 432.5 | 2.9 · 30.2 | 21.1 · 11.7 | 0 | 0 · 0 | 0 | 0% | 6% |
| 비교 | 끄는 지도(Autarky·PD·Portals) | 36 | 58% | 410 | 2.8 · 18 | 30.9 · 18.6 | 0.2 | 0 · 0 | 8.9 | 19% | 0% |
| 비교 | 모든 지도 | 120 | 68% | 225 | 2.9 · 26.8 | 16.2 · 8.8 | 0.2 | 0 · 0 | 2.5 | 10% | 10% |

- 상위권 기준(전멸 연구 2.6절, 전멸형): LX 72%가 그런 때를 겪고(처음 r105) 20라운드에 2.0번 나누며 23%가 회복, 42%가 50라운드 안 전멸. LS 69%, 2.0번, 26%, 0%. 우리 g4 LX 95%(r50), 0.5번, 5%, 15%.

### 가설 수준 지표 (관찰)

| 기능 | 지표 | 기준 | 상위권 · 이전 우리 | 이번 | 비교 |
|---|---|---|---|---|---|
| floor | r100 우리 드래곤 수(전멸형; 전멸은 0) — 전멸형 5지도 / PD 뺀 4지도 | ≥5.5 | 상위 LX 5.5, 우리 g4 LX 2.5 | 6.1 / 6.7 | 6.1 / 6.6 |
| floor | 전멸률(전멸형) | ≤66% | swarm8 66%, merge2 78% | 32% (19/60) / 40% (19/48) | 35% (21/60) / 42% (20/48) |
| floor | 전멸 라운드 중앙(전멸형) | ≥r235 | swarm8 235, merge2 150, stack1–3 163 | 195 / 195 | 209 / 202 |
| kcap | 우리 전멸 중 E2(왕 사냥) 비율(모든 지도) | ≤8% | 상위 LX 6%, 우리 16% | 5% (E1 0 · E2 1 · E3m 12 · E3l 7) | 9% (E1 0 · E2 2 · E3m 12 · E3l 8) |
| kcap | r50 우리 최장 평균(전멸형; 전멸은 0) — 5지도 / 4지도 | ≤4.5 | 상위 LS 3.8, 우리 g4 LX 6.8 | 5.3 / 3.6 | 5.3 / 3.6 |
| kcap | 전멸한 판의 길이 ≥8 죽음(판당; 모든 지도) | ≤0.4 | 우리 0.75 | 0.2 (20판) | 0.3 (22판) |

### 지도 가르기 (map= 표식으로 확인)

- floor는 Trophy, Queen Of Spades, Devil, Default, Schooltime, Trauma, Slithery Fight에서만, kcap은 그중 Slithery Fight를 뺀 여섯에서만 켠다. 봇은 프로세스마다 자기 창으로 지도 가족을 인식하고(`map=` 표식), 인식 전·`none`이면 끈다. "표식이 켜는 가족이 아닌 발동"은 발동한 프로세스의 마지막 `map=` 표식이 그 기능을 켜는 가족을 대지 않은 발동이다(0이어야 한다). "인식한 프로세스"는 마지막 표식이 그 판의 참 지도 가족을 댄 프로세스다.

| 묶음 | 지도(정답 판본) | 판 | floor 발동 | kcap 발동 | 표식이 켜는 가족이 아닌 발동 | 인식한 프로세스 |
|---|---|---:|---:|---:|---:|---:|
| 이번 | Autarky (끔) | 12 | 0 | 0 | 0 | 100% (3499/3499) |
| 이번 | Default | 12 | 5 | 0 | 0 | 100% (479/480) |
| 이번 | Devil a | 6 | 15 | 0 | 0 | 99% (165/166) |
| 이번 | Devil b | 6 | 14 | 0 | 0 | 99% (122/123) |
| 이번 | Portals (끔) | 12 | 0 | 0 | 0 | 100% (1958/1958) |
| 이번 | Prisoners Dilemma (10) (끔) | 6 | 0 | 0 | 0 | 100% (1038/1038) |
| 이번 | Prisoners Dilemma (끔) | 6 | 0 | 0 | 0 | 100% (1562/1562) |
| 이번 | Queen Of Spades a | 6 | 4 | 0 | 0 | 99% (144/145) |
| 이번 | Queen Of Spades b | 6 | 1 | 1 | 0 | 98% (93/95) |
| 이번 | Schooltime a | 6 | 2 | 0 | 0 | 100% (259/259) |
| 이번 | Schooltime b | 6 | 0 | 0 | 0 | 100% (95/95) |
| 이번 | Slithery Fight a (kcap 끔) | 6 | 0 | 0 | 0 | 100% (380/380) |
| 이번 | Slithery Fight b (kcap 끔) | 6 | 0 | 0 | 0 | 100% (426/427) |
| 이번 | Trauma | 12 | 0 | 0 | 0 | 100% (505/506) |
| 이번 | Trophy | 12 | 1 | 1 | 0 | 99% (197/199) |
| 비교 | Autarky (끔) | 12 | 0 | 0 | 0 | 100% (3498/3498) |
| 비교 | Default | 12 | 5 | 0 | 0 | 100% (462/463) |
| 비교 | Devil a | 6 | 15 | 0 | 0 | 99% (163/164) |
| 비교 | Devil b | 6 | 14 | 0 | 0 | 99% (122/123) |
| 비교 | Portals (끔) | 12 | 0 | 0 | 0 | 100% (1959/1959) |
| 비교 | Prisoners Dilemma (10) (끔) | 6 | 0 | 0 | 0 | 100% (1038/1038) |
| 비교 | Prisoners Dilemma (끔) | 6 | 0 | 0 | 0 | 100% (1534/1534) |
| 비교 | Queen Of Spades a | 6 | 4 | 0 | 0 | 99% (146/147) |
| 비교 | Queen Of Spades b | 6 | 1 | 1 | 0 | 99% (100/101) |
| 비교 | Schooltime a | 6 | 1 | 0 | 0 | 100% (286/287) |
| 비교 | Schooltime b | 6 | 0 | 0 | 0 | 100% (95/95) |
| 비교 | Slithery Fight a (kcap 끔) | 6 | 1 | 0 | 0 | 100% (377/377) |
| 비교 | Slithery Fight b (kcap 끔) | 6 | 0 | 0 | 0 | 100% (419/420) |
| 비교 | Trauma | 12 | 0 | 0 | 0 | 100% (500/500) |
| 비교 | Trophy | 12 | 1 | 1 | 0 | 99% (191/193) |

## stack8: 샘 목표 고르기(F2·F2p), 포털 출구의 아군(px2), 새끼의 몫(cl·ce)

- 기준값은 `research/experiments/cand-stack8.md`(로컬 확인 전, 18:20)에서 왔다. cl·ce의 기준값은 공급망 연구의 값(18:07)이다. F 목표(드래곤·샘 단위)와 포털 통과의 정의는 stack5 절과 "포털 통과" 절과 같다. Fp·cl·ce는 드래곤·진주 단위이고, 설계 상황은 처음 표식 때의 판이다.

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| F2 | 목표 수: F2 표식 / 모든 F(판당) | – | 2096 / 2096 (17.5) | 2093 / 2093 (17.4) |
| F2 | 1. 설계 상황: F2 표식 목표 (실제 샘 · 우리 영토 · 다른 머리 없음) | ≥90% | 82% (100% · 100% · 82%) | 82% (100% · 100% · 82%) |
| F2 | 1. 설계 상황: 모든 F 목표 | ≥80% | 82% | 82% |
| F2 | 2. 도착(3걸음 안): F2 표식 목표 / 모든 F | ≥80% | 59% / 59% | 59% / 59% |
| F2 | 3. 도착 뒤 30라운드 무리 자연 진주 우리 몫(F2 표식; 합산 · 지도 평균, Portals 제외) | ≥85% · ≥85% | 91% (4791개) · 71% | 91% (4829개) · 71% |
| F2 | 4. 겹친 추격: 다른 우리 드래곤의 같은 샘 목표와 겹침(F2 표식 / 모든 F) | ≤10% | 30% / 30% | 30% / 30% |
| F2p | Fp 진주 수(표식 턴) | – | 0 (0턴) | 0 (0턴) |
| F2p | 1. 설계 상황: 표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음 | ≥80% | – | – |
| F2p | 2. 즉시 효과: 그 드래곤이 10라운드 안에 먹음 · 상대가 먹음 | ≥48% · ≤5% | – · – | – · – |
| F2p | 끌어내기: F 표식 턴 가운데 유일하게 가장 가까운 자연 진주(7걸음 안, 무리 밖)에서 멀어진 턴 | ≤5% (관찰; W5+W6 15%) | 15% (후보가 있던 턴 28%; F 표식 턴 22613) | 15% (후보가 있던 턴 28%; F 표식 턴 22617) |
| px2 | 발동(px2 + px2x 턴, 판당) | – | 0 (0) | 0 (0) |
| px2 | 1. 설계 상황: 전 라운드 그 칸의 음파가 우리 드래곤에 멈춤 | ≥95% | – | – |
| px2 | 2. 즉시 효과 A: 건너지 않음(px2) | ≥80% | – | – |
| px2 | 3. 즉시 효과 B: 아군에 멈춘 탐침 뒤 아는 포털을 건너는 걸음에서 아군에 막혀 죽음(판당, v 무관) | ≤0.2 (W5–W7 0.69) | 0.92 (110건) | 0.88 (105건) |
| px2 | 보호: 포털 3라운드 몸 생존 | ≥95% | 94% | 94% |
| px2 | 보호: 건너는 걸음 아군 막힘 죽음(판당, 탐침·v 무관) | ≤0.75 (W5–W7 1.41) | 1.87 (224건) | 1.87 (224건) |
| cl | 진주 수(표식 턴) | – | 19203 (47848턴) | 19345 (47728턴) |
| cl | 설계 상황: 자연 진주, 우리 머리 가운데 표식한 조각만 가장 가까움 | ≥90% | 39% | 39% |
| cl | 즉시 효과: 조각이 먹음 · 우리 팀 · 우리 긴 드래곤 | ≥48% · ≥97% · ≤10% | 67% · 80% · 7% | 66% · 79% · 7% |
| ce | 진주 수(표식 턴) | – | 0 (0턴) | 0 (0턴) |
| ce | 설계 상황: 적 머리가 진주에서 우리 거리+1 안 | ≥80% | – | – |
| ce | 즉시 효과: 상대가 먹음 | ≤5% | – | – |
| ce | 보호: 표식 뒤 5라운드 안 박힘 | ≤19% | – | – |

- cl·ce의 가설 수준 지표(새끼 30라운드 먹음 ≥45%, 새끼 몫의 상대 몫 ≤3%/≤5%)는 공급망 스크립트 `exp/supply-chain/child_forage.js`로 잰다. 새끼 먹음은 stack5 절의 csplit 줄에도 있다.

### 포털 통과: 전 라운드 탐침(같은 칸, 같은 방향의 음파)별

| 묶음 | 출구 | 탐침 | 필사(v ≤ −20) | 통과 | 몸 3라운드 실패 | 건너는 걸음 아군 막힘 죽음 |
|---|---|---|---|---:|---:|---:|
| 이번 | 아는 포털 | clean | 아님 | 2163 | 4% | 60 |
| 이번 | 미탐색 | clean | 아님 | 1727 | 3% | 24 |
| 이번 | 아는 포털 | ally | 아님 | 416 | 11% | 69 |
| 이번 | 미탐색 | clean | 필사 | 323 | 16% | 8 |
| 이번 | 아는 포털 | none | 아님 | 156 | 12% | 0 |
| 이번 | 아는 포털 | ally(머리) | 아님 | 153 | 20% | 41 |
| 이번 | 미탐색 | none | 필사 | 80 | 15% | 8 |
| 이번 | 미탐색 | ally | 필사 | 80 | 8% | 5 |
| 이번 | 아는 포털 | clean | 필사 | 45 | 9% | 0 |
| 이번 | 아는 포털 | enemy | 아님 | 35 | 17% | 0 |
| 이번 | 미탐색 | ally(머리) | 필사 | 33 | 24% | 9 |
| 이번 | 아는 포털 | enemy(머리) | 아님 | 23 | 17% | 0 |
| 이번 | 미탐색 | enemy | 필사 | 11 | 27% | 0 |
| 이번 | 미탐색 | enemy(머리) | 필사 | 9 | 11% | 0 |
| 이번 | 아는 포털 | ally | 필사 | 4 | 25% | 0 |
| 이번 | 미탐색 | none | 아님 | 1 | 0% | 0 |
| 이번 | 아는 포털 | enemy | 필사 | 1 | 0% | 0 |
| 비교 | 아는 포털 | clean | 아님 | 2193 | 5% | 63 |
| 비교 | 미탐색 | clean | 아님 | 1755 | 3% | 24 |
| 비교 | 아는 포털 | ally | 아님 | 427 | 11% | 67 |
| 비교 | 미탐색 | clean | 필사 | 319 | 15% | 8 |
| 비교 | 아는 포털 | none | 아님 | 161 | 10% | 0 |
| 비교 | 아는 포털 | ally(머리) | 아님 | 146 | 20% | 38 |
| 비교 | 미탐색 | ally | 필사 | 84 | 8% | 5 |
| 비교 | 미탐색 | none | 필사 | 83 | 18% | 11 |
| 비교 | 아는 포털 | clean | 필사 | 41 | 7% | 0 |
| 비교 | 아는 포털 | enemy | 아님 | 36 | 14% | 0 |
| 비교 | 미탐색 | ally(머리) | 필사 | 34 | 24% | 8 |
| 비교 | 아는 포털 | enemy(머리) | 아님 | 23 | 17% | 0 |
| 비교 | 미탐색 | enemy(머리) | 필사 | 11 | 18% | 0 |
| 비교 | 미탐색 | enemy | 필사 | 11 | 36% | 0 |
| 비교 | 아는 포털 | ally | 필사 | 2 | 0% | 0 |
| 비교 | 미탐색 | none | 아님 | 1 | 0% | 0 |

## stack10: 국지 수 교환 문(lnt)과 판본별 머릿수 목표(utab)

- 기준값은 `research/experiments/cand-stack10.md`(21:12–21:14, 구현·로컬 확인 전)에서, 상위권·우리 값은 `research/observations/economy-principles.md`(4.1–4.3절, 7절)에서 왔다. 정의는 연구의 추출기(`exp/econ-principles/extract.js` O·C행)와 같다. d3 = 우리 드래곤의 차례 시작 머리에서 체비쇼프 3 안의 우리 머리 수 − 적 머리 수, d8 = 접촉 칸(표적 머리)에서 맨해튼 8 안의 같은 차이(두 드래곤 제외, 감싸기, 켈프·포털 무시). B3 기회 = 우리 길이 ≤4 드래곤의 차례 시작에 적 머리가 열린 변(포털 포함) 너머 바로 옆(둘 이상이면 가장 긴 것), 박음 = 그 머리로 한 걸음. 교환 = 우리 드래곤이 적 머리로 움직여 둘 다 죽음. 두 몸의 진주 = 두 사망 기록의 떨군 진주 합, net20 = (적 길이 − 우리 길이) + 20라운드 안 우리가 먹은 수 − 상대가 먹은 수.

### lnt 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| lnt | 박치기(맞부딪힘) 수 (판당) · 표식만 붙고 맞부딪히지 않음 | – | 317 (2.6) · 0 | 316 (2.6) · 0 |
| lnt | 1. 설계 상황: 기보 d3 ≥ +1이고 표적이 차례 시작에 바로 옆 | ≥95% | 100% | 100% |
| lnt | 2. 즉시 효과: 두 몸 진주 20R 우리 몫 / 상대 몫 · 건당 net20 (건) | ≥70% / ≤30% · ≥+1.5 | 48% / 49% · +0.50 (317) | 47% / 51% · +0.28 (316) |
| lnt | 3. 빈도: B3 기회 가운데 기보 d3 ≥ +1에서 박는 비율 | ≥50% (승자 65–73%, 우리 18세트 25–29%) | 89% (323/361) | 90% (322/356) |
| lnt | 3. 빈도: B3 기회 가운데 기보 d3 ≤ −1에서 박는 비율 | ≤20% (승자 14–16%) | 4% (43/1009) | 5% (48/999) |
| lntv | 거부 턴 수 (판당) · 설계 상황(기보 d3 ≤ −1) · 표식 d3 = 기보 d3 | (관찰) | 24 (0.2) · 100% · 100% | 29 (0.2) · 100% · 100% |
| lntv | 거부 턴 뒤 10라운드 몸 생존 · 10라운드 안 박힘 | (관찰; 연구 4.2절: 박지 않은 기회 뒤 10라운드 사망 d3 ≤−2 우리 43%, 승자 50%) | 92% · 21% | 90% · 21% |
| kint | 예외 교환 수 · 두 몸 진주 20R 우리 몫 / 상대 몫 · 건당 net20 | (관찰; 승자의 상대 최장(≥8) 박기, d8 열세 net20 +9.47) | 10 · 11% / 57% · +10.30 (10) | 9 · 11% / 54% · +9.33 (9) |

### B3 기회: 기보 d3별 박는 비율과 그 박치기의 진주 (연구 4.2·4.3절 정의)

| 묶음 | d3 | 기회 | 박음 | 한 걸음 박치기(길이 ≤4, 차례 시작에 옆): 20R 우리 / 상대 · net20 (건) |
|---|---|---:|---:|---|
| 이번 | ≤−2 | 601 | 4% | 1% / 92% · -2.08 (24) |
| 이번 | −1 | 408 | 5% | 8% / 63% · +1.05 (20) |
| 이번 | 0 | 457 | 4% | 25% / 39% · +1.70 (20) |
| 이번 | +1 | 210 | 87% | 38% / 60% · -0.21 (183) |
| 이번 | ≥+2 | 151 | 93% | 57% / 36% · +1.41 (140) |
| 비교 | ≤−2 | 595 | 5% | 1% / 84% · -1.66 (29) |
| 비교 | −1 | 404 | 5% | 12% / 69% · -0.80 (20) |
| 비교 | 0 | 465 | 5% | 18% / 43% · +1.74 (23) |
| 비교 | +1 | 212 | 90% | 38% / 60% · -0.14 (190) |
| 비교 | ≥+2 | 144 | 92% | 57% / 37% · +0.86 (132) |

- 상위권 승자(연구 4.2·4.3절): 박는 비율 d3 ≤−2 14%, −1 16%, 0 29%, +1 65%, ≥+2 73%; 그 박치기의 20R 우리/상대 · net20은 ≤−2 24%/72% −0.76, −1 35%/60% +0.07, 0 52%/40% +1.21, +1 71%/25% +1.70, ≥+2 80%/15% +2.20. 우리 18세트: 12%, 13%, 16%, 25%, 29%; 9%/81% −1.63, 21%/69% −0.81, 36%/54% −0.01, 55%/38% +1.08, 70%/26% +2.32.

### 모든 교환 (우리가 박은 것; 가설 수준 지표, 관찰)

| 지표 | 기준 | 우리 18세트 · 상위권 승자 | 이번 | 비교 |
|---|---|---|---|---|
| 교환 수 (판당) · 그 가운데 lnt 표식 · kint 표식 | – | – | 440 (3.7) · 317 · 10 | 449 (3.7) · 316 · 9 |
| 두 몸 진주 20R 우리 몫 / 상대 몫 · 건당 net20 (건) | 우리 몫 ≥50% | 38% / 52% · 66% | 37% / 50% · +1.54 (440) | 35% / 52% · +1.23 (449) |
| 교환 가운데 d8 ≤ −3 비율 | ≤25% | 38% · 11% | 23% (102/440) | 24% (106/449) |
| 교환 가운데 d3 ≤ −1 비율 | (참고) | 36% · 8% | 11% | 12% |
| 판당 교환 net20의 합 (판) | ≥0 | – | +5.64 (120판) | +4.59 (120판) |

| 묶음 | d8 | 교환 | 20R 우리 / 상대 · net20 (건) |
|---|---|---:|---|
| 이번 | ≤−3 | 102 | 12% / 75% · -0.75 (102) |
| 이번 | −2 | 38 | 17% / 66% · +0.24 (38) |
| 이번 | −1 | 51 | 29% / 45% · +2.61 (51) |
| 이번 | 0 | 52 | 45% / 40% · +3.17 (52) |
| 이번 | +1 | 66 | 41% / 50% · +1.73 (66) |
| 이번 | +2 | 32 | 66% / 27% · +2.44 (32) |
| 이번 | ≥+3 | 99 | 59% / 35% · +2.58 (99) |
| 비교 | ≤−3 | 106 | 11% / 76% · -1.00 (106) |
| 비교 | −2 | 40 | 20% / 65% · +0.82 (40) |
| 비교 | −1 | 58 | 27% / 52% · +1.84 (58) |
| 비교 | 0 | 58 | 35% / 40% · +2.84 (58) |
| 비교 | +1 | 65 | 42% / 52% · +1.42 (65) |
| 비교 | +2 | 29 | 63% / 30% · +2.52 (29) |
| 비교 | ≥+3 | 93 | 63% / 33% · +2.01 (93) |

- 상위권 승자(연구 4.1절, 모든 교환): d8 ≤−3 41%/56% −0.12, 0 58%/34% +1.35, ≥+3 77%/17% +2.20. 우리 18세트: ≤−3 21%/70% −1.27, 0 37%/42% +1.15, ≥+3 72%/23% +2.76.

### utab 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| utab | csplit 발동 · 인식 뒤(발동한 프로세스의 마지막 map 표식이 판본을 댐) · tab 표식 | – | 1875 · 1867 · 0 | 1870 · 1862 · 0 |
| utab | 1. 설계 상황: 인식 뒤 csplit 가운데 tab | ≥95% | 0% | 0% |
| utab | 2. 즉시 효과: 목표가 1.5배 이상 오르는 판본 가운데 utab이 켜진 넷(Devil a·b, Slithery Fight a, Trophy a; W11부터 Portals는 넓이 목표)의 r100 우리 수 ÷ 표 r100 목표, 판 중앙값 (판) | ≥0.6 | 0.25 (30판) | 0.25 (30판) |
| utab | (사전 등록의 다섯 판본, Portals a 포함) r100 ÷ 표 r100 목표, 판 중앙값 (판) | – | 0.29 (42판) | 0.29 (42판) |
| utab | 3. tab csplit 새끼 30라운드 생존 | ≥30% | – (0마리) | – (0마리) |
| utab | (참고) 조금 오르는 판본(Slithery Fight b, Autarky a, Schooltime a): r100 ÷ 표 목표 중앙값 (판) | – | 0.38 (24판) | 0.38 (24판) |

### 판본별 r100 우리 드래곤 수 (utab 표 대비; 전멸은 0)

| 묶음 | 판본(정답) | 판 | 넓이 목표 | 표 r50 · r100 | r100 우리 수 중앙값 (평균) | ÷ 표 r100 (판 중앙값) | tab csplit (판당) |
|---|---|---:|---:|---|---|---:|---:|
| 이번 | Autarky/a | 12 | 21 | 17 · 23 | 11 (11.3) | 0.48 | 0 |
| 이번 | Default/a | 12 | 22 | 11 · 19 | 8.5 (9.1) | 0.45 | 0 |
| 이번 | Devil/a ↑ | 6 | 11 | 16 · 30 | 6.5 (6.7) | 0.22 | 0 |
| 이번 | Devil/b ↑ | 6 | 11 | 12 · 24 | 6.5 (6.2) | 0.27 | 0 |
| 이번 | Portals/a ↑ | 12 | 11 | 14 · 26 | 11 (11.3) | 0.42 | 0 |
| 이번 | Prisoners Dilemma/a | 6 | 11 | 9 · 13 | 4 (3.7) | 0.31 | 0 |
| 이번 | Prisoners Dilemma/b | 6 | 11 | 9 · 15 | 4 (3.8) | 0.27 | 0 |
| 이번 | Queen Of Spades/a | 6 | 19 | 7 · 13 | 3.5 (3.8) | 0.27 | 0 |
| 이번 | Queen Of Spades/b ↓ | 6 | 19 | 7 · 12 | 4 (4.2) | 0.33 | 0 |
| 이번 | Schooltime/a | 6 | 40 | 13 · 44 | 15 (14.5) | 0.34 | 0 |
| 이번 | Schooltime/b ↓ | 6 | 40 | 8 · 16 | 10.5 (9.5) | 0.66 | 0 |
| 이번 | Slithery Fight/a ↑ | 6 | 37 | 47 · 62 | 17 (16.8) | 0.27 | 0 |
| 이번 | Slithery Fight/b | 6 | 37 | 43 · 55 | 11.5 (12.3) | 0.21 | 0 |
| 이번 | Trauma/a ↓ | 12 | 25 | 7 · 16 | 6 (6.3) | 0.38 | 0 |
| 이번 | Trophy/a ↑ | 12 | 13 | 15 · 31 | 7.5 (7.3) | 0.24 | 0 |
| 비교 | Autarky/a | 12 | 21 | 17 · 23 | 11 (11.3) | 0.48 | 0 |
| 비교 | Default/a | 12 | 22 | 11 · 19 | 8.5 (9) | 0.45 | 0 |
| 비교 | Devil/a ↑ | 6 | 11 | 16 · 30 | 6.5 (6.7) | 0.22 | 0 |
| 비교 | Devil/b ↑ | 6 | 11 | 12 · 24 | 6.5 (6.2) | 0.27 | 0 |
| 비교 | Portals/a ↑ | 12 | 11 | 14 · 26 | 11 (11.3) | 0.42 | 0 |
| 비교 | Prisoners Dilemma/a | 6 | 11 | 9 · 13 | 4 (3.7) | 0.31 | 0 |
| 비교 | Prisoners Dilemma/b | 6 | 11 | 9 · 15 | 4 (3.8) | 0.27 | 0 |
| 비교 | Queen Of Spades/a | 6 | 19 | 7 · 13 | 3.5 (3.8) | 0.27 | 0 |
| 비교 | Queen Of Spades/b ↓ | 6 | 19 | 7 · 12 | 4 (4.2) | 0.33 | 0 |
| 비교 | Schooltime/a | 6 | 40 | 13 · 44 | 15 (14.5) | 0.34 | 0 |
| 비교 | Schooltime/b ↓ | 6 | 40 | 8 · 16 | 10.5 (9.5) | 0.66 | 0 |
| 비교 | Slithery Fight/a ↑ | 6 | 37 | 47 · 62 | 17 (16.8) | 0.27 | 0 |
| 비교 | Slithery Fight/b | 6 | 37 | 43 · 55 | 11.5 (12.3) | 0.21 | 0 |
| 비교 | Trauma/a ↓ | 12 | 25 | 7 · 16 | 6 (6.3) | 0.38 | 0 |
| 비교 | Trophy/a ↑ | 12 | 13 | 15 · 31 | 7.5 (7.2) | 0.24 | 0 |

- ↑ = 목표가 1.5배 이상 오르는 판본(게이트 2), ↓ = 2/3 이하로 내려가는 판본. 정답 판본은 로컬이면 지도 파일 이름, 온라인이면 기보의 자연 생성(`layoutTruth`; ?·x는 가릴 수 없던 판). stack6 r100(연구 7절): Autarky 10, Default 11, Devil a 6, Portals 12, PD10 4, PD a 4, QoS a 9, QoS b 5, Schooltime a 16, Schooltime b 8, Slithery a 31, Slithery b 11, Trauma 6, Trophy 9.

### utab 가설 수준 지표 (관찰; stack6(W6)과 비교)

| 지표 | 이번 | 비교 |
|---|---|---|
| 오르는 판본(utab이 켜진 넷: Devil a·b, Slithery Fight a, Trophy a): 우리 영토 자연 진주를 상대가 먹은 몫 | 81% (10814개, 30판) | 81% (10702개, 30판) |
| 오르는 판본(같은 넷): r0–199 우리가 먹은 자연 진주 (판당) | 39.5 | 39.3 |
| 내려가는 판본(QoS b, Schooltime b, Trauma a): r200 우리 최장(전멸은 0; 평균 · 중앙값) | 3.6 · 3 (24판) | 3.6 · 3 (24판) |
| 내려가는 판본: r100 우리 수 (평균) | 6.5 | 6.5 |

## stack9: 늦은 조각 풀 — 늦은 재분열(lsplit), frag 수 상한(fc), 영토 덮기 끌림(cov)

- 기준값은 `research/experiments/cand-stack9.md`(로컬 확인 결과를 보기 전, 21:04)에서, 상위권·우리 값은 `research/observations/supply-chain.md`(7절)에서 왔다. 가설 수준 지표는 그 연구의 코드(`exp/supply-chain/extract.js` analyse)를 같은 기보에 돌려 잰다. "판당"의 분모는 r250 뒤까지 간 우리 팀-경기다(500라운드형: Autarky, Portals, Schooltime, Slithery Fight, Trauma).

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| lsplit | 발동(모든 판당; 500라운드형 r250까지 간 판당) | – | 577 (4.8; 7.4) | 583 (4.9; 7.7) |
| lsplit | 1. 설계 상황: r250–339 · 부모 길이(분열 전) 4–6 · 우리 수(기보) < 목표 | ≥95% | 100% (100% · 100% · 100%; 표식의 수·목표 = 기보 100%) | 100% (100% · 100% · 100%; 표식의 수·목표 = 기보 100%) |
| lsplit | 2. 즉시 효과 A: 새끼가 30라운드 안에 자연 진주 ≥1 | ≥38% (승자의 늦은 2+2 새끼 38%) | 29% (577마리; 500형 28% · 전멸형 33%) | 32% (583마리; 500형 32% · 전멸형 34%) |
| lsplit | 3. 즉시 효과 B: 새끼가 죽을 때 떨군 진주의 우리 몫(합산) | ≥85% (승자 90%) | 79% (죽은 새끼 524마리, 진주 881개; ≥8 28% · 상대 15%) | 76% (죽은 새끼 544마리, 진주 954개; ≥8 29% · 상대 16%) |
| fc | 발동(판당) | – | 61 (0.5; frag 전체 77) | 80 (0.7; frag 전체 88) |
| fc | 1. 설계 상황: r250–420 · 부모가 팀 최장 아님 · 우리 수(기보) ≥ 옛 frag 상한 | ≥95% | 87% (100% · 87% · 100%) | 85% (100% · 85% · 100%) |
| fc | 2. 즉시 효과 A: 조각 제 몫(S1: 30라운드 살며 1개 이상 먹거나, 뒤에 희생 표식으로 아군을 먹임) | ≥50% | 33% (61마리) | 59% (80마리) |
| fc | 3. 즉시 효과 B: 조각이 죽을 때 떨군 진주 중 우리 ≥8이 먹은 몫(합산) | ≥20% (승자 부모 5–7 늦은 새끼 20%) | 32% (죽은 조각 55마리, 진주 96개; 우리 78% · 상대 6%) | 52% (죽은 조각 78마리, 진주 145개; 우리 88% · 상대 0%) |
| cov | 창 수(표식 턴; 판당 창) | – | 6244 (59433턴; 52) | 6280 (60148턴; 52.3) |
| cov | 게이트: 창 30라운드 안에 그 드래곤이 우리 영토 자연 진주 ≥1 | ≥47% (승자 자기 영토 태생 조각 47%) | 29% (창 안에 죽음 25%) | 29% (창 안에 죽음 26%) |
| cov | (관찰) 표식 턴의 끝 칸이 기보 영토의 우리 쪽: 창을 연 턴 / 모든 표식 턴 | – | 90% / 88% | 90% / 88% |
| cov | (참고) W5 정의: 표식 턴마다 20라운드 안에 우리 영토 자연 진주 | – | 20% | 20% |

### 가설 수준 지표 (관찰; 500라운드형 r250–499, r250 뒤까지 간 팀-경기당)

| 지표 | 기준 | 상위권 승자 · 패자 · stack5 · stack6 | 이번 | 비교 |
|---|---|---|---|---|
| lsplit: 조각 탄생(태어날 때 길이 ≤3; 모든 분열) | ≥50 | 156 · 135 · 8.7 · 7.1 | 13.4 (lsplit 7.4, frag 1.3, 탈출 분열 4.7, 그 밖 0.1) | 14 (lsplit 7.7, frag 1.4, 탈출 분열 4.9, 그 밖 0.1) |
| lsplit: conv 상태 에피소드 | ≥30 | 57.6 · 39.4 · 17.1 · 20.1 | 21.9 | 20.4 |
| lsplit · fc: conv형 진주(조각 → ≥8) | ≥12 (fc ≥9) | 22.9 · 14.8 · 6.5 · 5.4 | 6.7 | 6.7 |
| lsplit: 조각 → 조각 희생 진주 | ≥10 | 34.9 · 28.6 · 2.0 · 2.0 | 3.2 | 3.8 |
| fc: frag 새끼(r250–499) | ≥3 | (부모 5–7·8+ 36) · – · 0.4 · 0.9 | 1.3 | 1.4 |
| (관찰) r350 우리 조각 수(길이 ≤4; r350까지 간 판 평균) | – | 30.5 · – · 6.2 · – | 10.9 | 11.1 |
| (참고) 전멸형: 조각 탄생 · conv 상태 에피소드 · conv형 진주 · 조각 → 조각 | – | 68 · 17.3 · – · – | 4.1 · 0.8 · 0.5 · 1.3 | 4.1 · 0.8 · 0.8 · 1.3 |
| cov: r100 우리 영토에서 적이 더 가까운 몫(판 평균; 500형 / 전멸형) | ≤17% (500형) | 11% · 17% · 27% · 25% | 29% / 67% | 29% / 67% |
| cov: r100 자기 영토 보로노이(판 평균; 500형 / 전멸형) | ≥80% | 89% · 83% · 72% · 74% | 71% / 32% | 71% / 32% |
| cov: 우리 영토 자연 진주를 상대가 먹은 몫(합산; 500형 / 전멸형) | ≤25% | 11% / 16% (승자) | 53% / 61% | 53% / 61% |

- 판 수(r250 뒤까지 간 팀-경기; 500라운드형 / 전멸형): 이번 60 / 48 · 비교 60 / 48. 공급 사슬 재구성 점검이 0이 아닌 판: 이번 0 · 비교 0; 지표 계산 오류: 이번 0 · 비교 0.

### 부작용 (관찰; 판정에 쓰지 않음)

| 항목 | 이번 | 비교 |
|---|---|---|
| lsplit 새끼의 끝: 끝까지 삶 · 표식 희생(conv·feed) · 그 밖 희생 · 갇힘 · 박힘 · 아군 머리 · 그 밖 | 9% · 36% · 0% · 34% · 9% · 5% · 8% (577마리) | 7% · 36% · 0% · 34% · 9% · 5% · 10% (583마리) |
| 어린 조각 규칙(20라운드): lsplit 새끼가 20라운드 안에 끝남(갇힘 · 박힘 · 희생 · 그 밖) / 뒤에 conv·feed로 아군을 먹임(그때 나이 중앙) | 19% (78 · 13 · 2 · 19) / 36% (73) | 17% (68 · 11 · 2 · 19) / 36% (85) |
| lsplit 부모: 10라운드 생존 · 부모 몸(새끼 포함) 30라운드 뒤 길이 변화 평균 · 부모가 죽을 때 떨군 진주 우리 몫 | 88% · 3.7 · 73% (921개) | 86% · 3.9 · 73% (1023개) |
| lsplit 모이기 창(r340 뒤) 발동 · 그 새끼 30라운드 안 자연 진주 ≥1 | 0 · – | 0 · – |
| 우리 드래곤의 죽음 r250 뒤(판당): 갇힘 · 적 머리에 박힘 · 우리끼리 머리 충돌(둘 다 셈) | 35.4 · 2.3 · 1.2 | 35.1 · 2.3 · 1.2 |
| 모이기(g) 드래곤(통로 고리 밖): 수 · 왕 3칸 안까지 감 · 희생까지 함 · 가는 길에 죽음 | 516 · 43% · 42% · 26% | 526 · 36% · 58% · 21% |
| 희생 먹이기(feed) · conv: 판당 발동, 떨군 진주 우리 몫 | feed 2.7, 88% · conv 3.7, 97% | feed 3.7, 87% · conv 3.3, 99% |
| 끝 왕 길이(500라운드형 끝까지 간 판) | 23.7 (59판) | 25.3 (59판) |

## stack11: 끝판 왕 — 모이기 물러서기(gh), 왕 떼기(kx), 끝판 창도 왕 부류에게(lwk)

- 기준값은 `research/experiments/cand-stack11.md`(23:04–23:06, 로컬 발동 수치를 보기 전)에서, 상위권·우리 값은 `research/observations/endgame-king.md`(1–5절, 7절)에서 왔다. gh 2, kx 2, lwk 2와 가설 수준 지표는 그 연구의 추출기(`exp/endgame-king/extract.js` analyse)를 같은 기보에 돌려 잰다. "500형 전부"는 500라운드형 모든 판, "500형 끝까지"는 500라운드까지 가고 최종 왕이 있는 판, "KX 지도"는 그 가운데 Schooltime·Slithery Fight·Trauma·Autarky다. 판당의 분모는 그 모집단의 우리 팀-경기다.

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| gh | 발동: gh 턴(판당) · ghd 진주 | – | 4783 (39.9) · 783 | 0 (0) · 0 |
| gh | 1. 설계 상황: gh 턴에 팀 최장(기보, 이 드래곤 아님)이 맨해튼 6 안 | ≥95% | 40% (이 드래곤이 팀 최장 213턴) | – (이 드래곤이 팀 최장 0턴) |
| gh | 1. 설계 상황: ghd 진주가 실제 사망 진주(표식 때 기보) | ≥95% | 100% (783개) | – (0개) |
| gh | 2. 즉시 효과 A: 가로채기 몫(r300 뒤 대상이 그때 계보인 표식 먹이의 진주를 계보 밖 우리 드래곤이 먹음; 500형 전부) | ≤20% (stack5–8 26–35%, merge2 20%) | 31% (248/790개, 먹이 380번) | 33% (283/867개, 먹이 377번) |
| gh | 3. 즉시 효과 B: ghd 진주를 곁의 더 긴 아군이 먹음 | ≥70% | 44% (782개; 우리 팀 96%, 상대 3%) | – (0개; 우리 팀 –, 상대 –) |
| kx | 발동: kx 턴(KX 지도 판당) | – | 977 (20.4; 발동한 판 37) | 0 (0; 발동한 판 0) |
| kx | 1. 설계 상황: kx 턴이 그 순간 팀 최장(기보: 더 긴 우리 드래곤 없음)이고 적 머리 맨해튼 7 안 | ≥90% | 65% (팀 최장 69% · 적 머리 7 안 93%; 질량 장부 왕 60%) | – (팀 최장 – · 적 머리 7 안 –; 질량 장부 왕 –) |
| kx | 2. 즉시 효과: KX 지도 계보 드래곤(길이 ≥8) r300–399 턴의 적 머리 6칸 안 몫(500형 끝까지) | ≤35% (stack5–7 52%, 승자 32%) | 39% (604/1530턴, 47판) | 44% (584/1324턴, 47판) |
| kx | 2. 즉시 효과: 같은 값 r400–499 | ≤22% (stack5–7 32%, 승자 21%) | 31% (1098/3599턴, 47판) | 30% (1101/3636턴, 47판) |
| lwk | 발동: lwk 턴(판당) | – | 941 (7.8) | 0 (0) |
| lwk | 1. 설계 상황: r430 뒤이고 더 긴 우리 머리가 맨해튼 5 안(기보) | 모두 | 97% (r430 뒤 100%) | – (r430 뒤 –) |
| lwk | 2. 즉시 효과: r430 뒤 feed의 대상이 그때 계보 · 떨군 진주 → 계보(500형 전부) | ≥55% · ≥45% (stack5–7 37% · 34%) | 53% (39/74) · 40% (81/205개) | 41% (72/177) · 38% (192/512개) |

### kx 2의 지도별 값 (계보 드래곤 길이 ≥8의 턴 가운데 적 머리 맨해튼 6 안; 500형 끝까지)

| 지도 | 구간 | 상위권 승자 (연구 T5b, r300–499) | 이번 | 비교 |
|---|---|---|---|---|
| Schooltime | r300–399 | 19% | 67% (110/164턴, 11판) | 24% (24/101턴, 11판) |
| Schooltime | r400–499 | 19% | 32% (213/673턴, 11판) | 32% (204/642턴, 11판) |
| Slithery Fight | r300–399 | 17% | 22% (135/613턴, 12판) | 25% (115/462턴, 12판) |
| Slithery Fight | r400–499 | 17% | 40% (385/960턴, 12판) | 29% (301/1036턴, 12판) |
| Trauma | r300–399 | 17% | 33% (9/27턴, 12판) | 43% (6/14턴, 12판) |
| Trauma | r400–499 | 17% | 9% (71/759턴, 12판) | 12% (89/756턴, 12판) |
| Autarky | r300–399 | 22% | 48% (350/726턴, 12판) | 59% (439/747턴, 12판) |
| Autarky | r400–499 | 22% | 36% (429/1207턴, 12판) | 42% (507/1202턴, 12판) |
| Portals | r300–399 | 49% (참고: 벽 너머) | 52% (491/940턴, 12판) | 57% (576/1018턴, 12판) |
| Portals | r400–499 | 49% (참고: 벽 너머) | 16% (180/1093턴, 12판) | 22% (260/1208턴, 12판) |

### 가설 수준 지표 (관찰; 연구 7절)

| 기능 | 지표 | 기준 | 상위권 승자 · stack5–7 (연구) | 이번 | 비교 |
|---|---|---|---|---|---|
| gh | 계보가 r300–499에 먹은 우리 희생 진주(판당; 500형 끝까지 / KX 지도) | ≥9.3 | 25.8 · 8.3 | 8.8 / 9.5 | 9.8 / 9.4 |
| gh | 모이기 창(r340–429) feed(판당; 500형 전부) · 발동 라운드 중앙 | ≥2.0 | – · 2.4 | 2.6 · 378 | 2.9 · 376 |
| gh | 길이 ≥8 우리 드래곤의 아군 머리 사망 r340–399(판당; r340까지 간 500형) | 늘지 않음 | – · 0.08 (r350–399) | 0.05 | 0.12 |
| gh | (참고) 뿌리 모이기 에피소드 가운데 가족의 마지막 죽음이 아군 머리(500형 전부) | – | – | 4% (19/496) | 4% (20/488) |
| gh | (부작용) 뿌리 모이기 에피소드 가족의 끝: 계보 / 계보 밖 삶 / 표식 먹이 / 다른 희생 / 다른 죽음(500형 전부) · 첫 g 표식에서 표식 먹이까지 라운드 중앙 | – | – · 11% / 21% / 47% / 0% / 21% | 13% / 28% / 39% / 0% / 19% (496) · 16 | 12% / 19% / 51% / 1% / 17% (488) · 16 |
| kx | r340 뒤 팀 최장(길이 ≥8)을 적 머리에 잃은 판(500형 끝까지 / KX 지도) | ≤7% | 5% · 13% (stack5–8) | 3% (2/59) / 4% (2/47) | 5% (3/59) / 6% (3/47) |
| kx | 계보의 우리 희생 진주 r300–499(판당; KX 지도) | ≥10 | 25.8 · 8.3 | 9.5 | 9.4 |
| kx | 표식 먹이(feed·conv, r300 뒤) 가운데 대상이 그때 계보인 몫(500형 전부 / KX 지도) | 유지 | – · 64% (feed r340–429) | 58% (652) / 72% (461) | 52% (725) / 61% (504) |
| kx | 왕 성장 r300→500(라운드당; 500형 끝까지 / KX 지도) | ≥0.12 | 0.18 · 0.09 | 0.08 / 0.09 | 0.09 / 0.10 |
| kx | 부작용: 계보의 자연 진주 r300–499(판당; KX 지도) | ≥11 | 11.7 · 12.4 | 10.3 | 10.1 |
| kx | 부작용: 계보의 분열 손실(떼어 냄 + 넘김) r300–499(판당; KX 지도) | 늘지 않음(≤5.9) | 6.6 · 5.9 | 4.1 | 2.5 |
| lwk | 계보의 r450–499 우리 희생 진주(판당; 500형 끝까지) | ≥2.6 | 6.4 · 2.1 | 2 | 2.8 |
| lwk | 끝에 계보 밖에서 산 길이 ≥8 드래곤의 끝 길이 합(판당; 500형 끝까지) | 늘지 않음 | – | 21.8 | 18.8 |

- 판 수(500형 전부 / 500형 끝까지 / KX 지도): 이번 60 / 59 / 47 · 비교 60 / 59 / 47. 추출기 재구성 점검이 0이 아닌 판: 이번 0 · 비교 0; 계산 오류: 이번 0 · 비교 0.

### 부작용 (관찰; 판정에 쓰지 않음)

| 항목 | 이번 | 비교 |
|---|---|---|
| kx 먹이 찾기: 계보 드래곤 턴당 5칸 안 자연 진주(r300–499; KX 지도) · 계보의 자연 진주(판당) | 1.25 · 10.3 | 1.47 · 10.1 |
| kx 가두기: r300 뒤 적이 계보 드래곤의 몸에 막혀 죽은 수(판당; 몸에 박음 + 몸 곁에 갇힘; KX 지도 / 500형 전부) · 계보가 먹은 적 사망 진주 r300–499(판당; KX 지도) | 0.2 / 0.2 · 1.8 | 0.1 / 0.1 · 1.6 |
| (참고) r300 뒤 적이 우리 몸에 막혀 죽은 수 전체(판당; 500형 전부): 박음 · 갇힘 | 0.1 · 0.4 | 0.1 · 0.4 |
| kx 막다른 곳·포털: 팀 최장(길이 ≥8)의 죽음 r300 뒤(판당; 500형 전부 / KX 지도): 적 머리 · 갇힘 · 아군 머리 · 희생 · 그 밖 | 0.03 · 0.13 · 0.12 · 0.02 · 0.00 / 0.04 · 0.02 · 0.02 · 0.02 · 0.00 | 0.05 · 0.10 · 0.08 · 0.05 · 0.00 / 0.06 · 0.04 · 0.04 · 0.06 · 0.00 |
| kx 포털: 그 순간 팀 최장(길이 ≥8)의 r300 뒤 포털 통과(판당; KX 지도) · 몸 3라운드 생존 · 드래곤 자체 3라운드 생존 · 넘는 걸음에서 죽음 | 0.7 (32) · 94% · 94% · 2 | 0.6 (28) · 86% · 86% · 4 |
| kx: 계보 드래곤 턴의 적 머리 3칸 안 몫 r300–499(KX 지도) | 7% | 9% |
| 길이 ≥8 우리 드래곤의 죽음 r300–499(판당; 500형 전부): 적 머리 · 아군 머리 · 갇힘 · 희생 | 0.08 · 0.22 · 0.75 · 0.40 | 0.08 · 0.28 · 0.52 · 0.78 |
| 표식 먹이 r300 뒤(판당; 500형 전부): conv · 모이기 창 feed · 끝판 창 feed | 7 · 2.6 · 1.2 | 6.2 · 2.9 · 3 |
| grab 표적 진주(판당) · 그중 우리가 먹음 | 43.7 · 81% | 45 · 81% |

