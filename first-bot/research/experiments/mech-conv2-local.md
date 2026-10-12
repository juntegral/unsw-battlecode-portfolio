# 구현 적용 확인: cand-conv2 v2 로컬 (흉내 상대 v4, a판 60판)

- 대상: `exp/conv2-a-px4` 60판 · 비교: `exp/stack5-a-px4` 60판
- 기준(사용자 규칙 2026-09-30): 승률이 아니라, 봇에 구현한 기능이 이 상대들에게 실제로 발동하고 의도대로 작동했는지를 본다.
- "의도대로"의 정의: 모이기=왕 3칸 안까지 가거나 희생까지 함 · 희생=떨군 진주 절반 이상을 우리 팀이 먹고 상대는 못 먹음 · 한입=2턴 안 분열하고 30라운드 뒤 가족 길이가 줄지 않음 · 탈출 분열=10라운드 뒤 몸이 살아 있음 · 정책 분열=새끼 30라운드 생존 · 탈출 질주·위협 피하기=10라운드 뒤 몸 생존 · 포털=3라운드 뒤 몸 생존 · 돌진=충돌 성사, 잡은 길이 ≥ 우리, 두 몸의 진주를 우리가 더 먹음 · 먹이 질주=진주 먹음.
- "몸"은 그 드래곤과 그 뒤 분열로 태어난 자손 전체다. 통로 고리처럼 몸을 새끼에게 넘기며 버티는 경우를 손실로 세지 않기 위해서다.
- stack2의 "의도대로": 조각 떼기=조각이 30라운드 살며 진주를 1개 이상 먹거나, 나중에 희생(feed·conv)으로 아군을 먹임 · 새 사망 진주 줍기=표적이 된 사망 진주(진주 하나가 한 건)를 우리 팀이 먹음(자연 진주로 오인했거나 이미 없던 표적은 판정에서 뺌).
- stack4의 "의도대로": tg=표식 턴 뒤 2라운드 안에 박히지 않음 · 몰렸을 때 분열=10라운드 뒤 몸이 살아 있음(보존율은 효과 줄) · px=그 턴에 우리 드래곤과 부딪혀 죽지 않음 · gx=그 드래곤이 끝까지 삶.
- stack5의 "의도대로": 덮기 분열=새끼가 30라운드 안에 자연 진주를 1개 이상 먹음(생존은 효과 줄) · 샘 지킴=목표 샘 3걸음 안에 든 뒤 30라운드 동안 그 무리(실제 샘, 목표에서 3걸음 안)에 생긴 자연 진주의 85% 이상을 우리가 먹음(도착하지 않았거나 진주가 생기지 않은 목표는 뺌) · 영토 덮기 끌림=20라운드 안에 우리 영토 자연 진주를 먹음. 게이트와 가설 수준 지표는 맨 뒤 stack5 절.

## 요약

| 기능 | 발동(판당) | 의도대로 | 비교: 발동(판당) | 비교: 의도대로 |
|---|---:|---:|---:|---:|
| 두 번째 단계 먹이기 (k2, conv2) | 7 (0.1) | 57% | 0 (0) | – |
| 후보 아닌 아군 희생 보류 (kch, conv2; 드래곤 단위) | 195 (3.3) | 79% | 0 (0) | – |
| 덮기 분열 (csplit, stack5) | 1091 (18.2) | 40% | 1091 (18.2) | 40% |
| 샘 지킴 (F, stack5; 드래곤·샘 단위) | 2807 (46.8) | 96% | 2819 (47) | 96% |
| 위협 모형 빈틈 (tg, stack4) | 12504 (208.4) | 98% | 12464 (207.7) | 98% |
| 모이기 시작 제한 (gx, stack4; 드래곤 단위) | 133 (2.2) | 65% | 68 (1.1) | 62% |
| 큰 아군 곁 희생 (conv, stack1 M1) | 85 (1.4) | 96% | 173 (2.9) | 97% |
| 조각 떼기 (split frag, stack2 S1) | 26 (0.4) | 62% | 31 (0.5) | 84% |
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 2405 (40.1) | 80% | 2360 (39.3) | 80% |
| 왕에게 모이기 (g, 드래곤 단위) | 941 (15.7) | 77% | 831 (13.9) | 83% |
| 희생 먹이기 (feed) | 130 (2.2) | 88% | 161 (2.7) | 90% |
| 막다른 길 한입 (pocket-eat) | 6 (0.1) | 67% | 8 (0.1) | 50% |
| 탈출 분열 (escape-split) | 4292 (71.5) | 98% | 4185 (69.8) | 99% |
| 출구 없음 (no-exit) | 4446 (74.1) | – | 4311 (71.9) | – |
| 정책 분열 (split) | 5 (0.1) | 20% | 5 (0.1) | 20% |
| 탈출 질주 3칸 (esc) | 72 (1.2) | 94% | 72 (1.2) | 94% |
| 위협 피하기 2칸 질주 | 672 (11.2) | 94% | 669 (11.2) | 94% |
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 2648 (44.1) | 93% | 2463 (41.1) | 94% |
| 돌진 (TRADE) | 51 (0.9) | 14% | 51 (0.9) | 27% |
| 먹이 질주 (2칸 이상, 먹은 것) | 175 (2.9) | 100% | 174 (2.9) | 100% |
| 기타 2칸 질주 | 83 (1.4) | – | 86 (1.4) | – |
| 마지막 돌진 (last-trade) | 32 (0.5) | – | 32 (0.5) | – |

- 건강: 턴 231010, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 비교 건강: 턴 222732, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 12378턴 · 끝판(late) 6006턴 · 돌진 신뢰(T, 탈출 끔) 27턴, 그 직후 박혀 죽음 0

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 비교 |
|---|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 2% (47/2701턴) | 2% (45/2686턴) |
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 24.7칸 (5.3회), 진주 우리 90% · 상대 2% | 36칸 (8.8회), 진주 우리 94% · 상대 1% |
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 2칸 (판당 0.10회) | 0.3칸 (판당 0.03회) |
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 22% (966/4441턴) | 23% (1028/4498턴) |
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.117회 (7건, 110칸) | 판당 0.100회 (6건, 76칸) |
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 7.7마리 (30판) | 6.1마리 (30판) |
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 21.9회 | 19.4회 |
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 55% (우리 39%) | 56% (우리 37%) |
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 7.6 대 상대 28.7 (9.8회) · 박힌 교환의 우리 몫 20% (232회) | 우리 8.2 대 상대 28.4 (10회) · 박힌 교환의 우리 몫 19% (236회) |
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 9개 | 9.2개 |

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 두 번째 단계 먹이기 (k2, conv2)

- 이번: 실행 100% · 설계 상황(지목 아군이 그 순간 팀 최장) 86% · 떨군 진주 27개 중 최종 왕 계보 44% · 우리 팀 63% · 상대 7% · 지목 아군이 그 순간 계보 57% · 최종 왕 43% · 먹인 길이 평균 6.9
- 상대별: proxy4_elim 2회 50% · proxy4_swarm 5회 60%
- 지도별: Autarky 1회 100% · Devil 2회 0% · Prisoners Dilemma 1회 0% · Queen Of Spades 1회 100% · Trauma 2회 100%
- 국면별: r350-449 3회 67% · r450+ 4회 50%

실패 사례 (3건 중 3건, 기보 확인용):
- proxy4_swarm · Devil · 게임 exp/conv2-a-px4:proxy4_swarm:devil:A:1 · r452 · 드래곤 #449 L5: #456(L10)에게 두 번째 단계 희생 → 진주 3개 중 최종 왕 계보 1, 우리 1, 상대 0
- proxy4_elim · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_elim:prisoners_dilemma:B:1 · r466 · 드래곤 #366 L11: #96(L23)에게 두 번째 단계 희생 → 진주 6개 중 최종 왕 계보 0, 우리 0, 상대 1; 지목 아군 r469 박힘(상대 돌진)에 사망
- proxy4_swarm · Devil · 게임 exp/conv2-a-px4:proxy4_swarm:devil:B:1 · r428 · 드래곤 #491 L12: #97(L16)에게 두 번째 단계 희생 → 진주 6개 중 최종 왕 계보 1, 우리 6, 상대 0; 지목 아군 r448 갇힘에 사망

## 후보 아닌 아군 희생 보류 (kch, conv2; 드래곤 단위)

- 이번: 드래곤 195 (표식 턴 1070) · 뒤에 후보에게 희생(kc) 20% · 몸(자손 포함) 끝까지 63% · 드래곤 자체 끝까지 32%
- 상대별: proxy4_elim 68회 75% · proxy4_king 44회 86% · proxy4_swarm 83회 78%
- 지도별: Autarky 22회 86% · Default 2회 50% · Devil 1회 100% · Portals 110회 77% · Queen Of Spades 1회 100% · Schooltime 4회 100% · Slithery Fight 55회 78%
- 국면별: r250-349 40회 65% · r350-449 90회 71% · r450+ 65회 98%

실패 사례 (41건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r352 · 드래곤 #478 L2: 보류 4턴 (r352–r360) → 죽음 r362 갇힘, 상대 길이 9
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:B:1 · r397 · 드래곤 #796 L4: 보류 1턴 (r397–r397) → 죽음 r410 갇힘, 상대 길이 2
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:B:1 · r422 · 드래곤 #352 L4: 보류 3턴 (r422–r432) → 죽음 r440 갇힘
- proxy4_swarm · Default · 게임 exp/conv2-a-px4:proxy4_swarm:default:A:1 · r352 · 드래곤 #119 L3: 보류 1턴 (r352–r352) → 죽음 r359 갇힘, 상대 길이 21
- proxy4_swarm · Portals · 게임 exp/conv2-a-px4:proxy4_swarm:portals:A:1 · r356 · 드래곤 #442 L4: 보류 4턴 (r356–r364) → 죽음 r370 갇힘
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:A:1 · r300 · 드래곤 #510 L3: 보류 16턴 (r300–r480) → 죽음 r484 갇힘, 상대 길이 6
- proxy4_elim · Portals · 게임 exp/conv2-a-px4:proxy4_elim:portals:B:1 · r305 · 드래곤 #319 L2: 보류 3턴 (r305–r364) → 죽음 r373 갇힘
- proxy4_elim · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_elim:slithery_fight:B:1 · r300 · 드래곤 #384 L2: 보류 12턴 (r300–r374) → 죽음 r375 갇힘
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r432 · 드래곤 #557 L9: 보류 6턴 (r432–r458) → 죽음 r466 갇힘, 상대 길이 11
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r439 · 드래곤 #592 L4: 보류 2턴 (r439–r440) → 죽음 r442 갇힘, 상대 길이 13

## 덮기 분열 (csplit, stack5)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 33% · 부모가 스스로 최장이라 믿음(k) 63% · 새끼 30라운드 안 자연 진주 ≥1 40% (500형 40% · 전멸형 41%; 기준 ≥45%) · 새끼 30라운드 생존 75% (500형 75% · 전멸형 74%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 84% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 갇힘 191, 아군 머리 19, 박힘(상대 돌진) 50, 희생 2, 돌진 12
- 비교: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 33% · 부모가 스스로 최장이라 믿음(k) 63% · 새끼 30라운드 안 자연 진주 ≥1 40% (500형 40% · 전멸형 41%; 기준 ≥45%) · 새끼 30라운드 생존 75% (500형 75% · 전멸형 74%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 84% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 갇힘 191, 아군 머리 19, 박힘(상대 돌진) 50, 희생 2, 돌진 12
- 상대별: proxy4_elim 360회 41% · proxy4_king 398회 40% · proxy4_swarm 333회 39%
- 지도별: Autarky 98회 48% · Default 131회 33% · Devil 72회 32% · Portals 79회 54% · Prisoners Dilemma 49회 47% · Queen Of Spades 96회 50% · Schooltime 161회 48% · Slithery Fight 287회 29% · Trauma 87회 37% · Trophy 31회 58%
- 국면별: r0-99 500회 43% · r100-249 591회 38%

실패 사례 (652건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r1 · 드래곤 #0 L4: 새끼 L2, 적 머리 시야 안 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r81 · 드래곤 #9 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:A:1 · r1 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r5 · 드래곤 #4 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:A:1 · r33 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_king:queen_of_spades:A:1 · r15 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r3 · 드래곤 #33 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trophy · 게임 exp/conv2-a-px4:proxy4_king:trophy:A:1 · r28 · 드래곤 #0 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0

## 샘 지킴 (F, stack5; 드래곤·샘 단위)

- 이번: 목표 2807개(표식 턴 22760) · 설계 상황 79% (실제 샘 98%, 우리 영토 90%, 처음에 다른 우리 머리 3걸음 안 없음 90%; 기준 ≥80%) · 3걸음 안 도착 59% · 도착 뒤 30라운드 그 무리 자연 진주 11631개 중 우리 98% · 상대 2% (합산 기준 ≥85%) · 처음 거리 평균 4.8
- 비교: 목표 2819개(표식 턴 22512) · 설계 상황 79% (실제 샘 98%, 우리 영토 90%, 처음에 다른 우리 머리 3걸음 안 없음 90%; 기준 ≥80%) · 3걸음 안 도착 59% · 도착 뒤 30라운드 그 무리 자연 진주 11724개 중 우리 98% · 상대 2% (합산 기준 ≥85%) · 처음 거리 평균 4.8
- 상대별: proxy4_elim 1005회 96% · proxy4_king 980회 96% · proxy4_swarm 822회 96%
- 지도별: Autarky 361회 100% · Devil 149회 58% · Portals 654회 98% · Prisoners Dilemma 1044회 100% · Queen Of Spades 19회 – · Schooltime 11회 – · Slithery Fight 485회 32% · Trauma 72회 80% · Trophy 12회 –
- 국면별: r0-99 836회 90% · r100-249 1186회 99% · r250-349 785회 99%

실패 사례 (61건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:B:1 · r40 · 드래곤 #10 L2: 샘 (23,0) 처음 거리 9 → r58 도착, 30라운드 무리 진주 4개 중 우리 2 · 상대 2
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r311 · 드래곤 #428 L2: 샘 (16,14) 처음 거리 4 → r311 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 0
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:B:1 · r318 · 드래곤 #6 L3: 샘 (36,13) 처음 거리 4 → r318 도착, 30라운드 무리 진주 3개 중 우리 0 · 상대 3
- proxy4_swarm · Devil · 게임 exp/conv2-a-px4:proxy4_swarm:devil:B:1 · r78 · 드래곤 #1 L2: 샘 (26,0) 처음 거리 13 → r129 도착, 30라운드 무리 진주 7개 중 우리 5 · 상대 2
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:A:1 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_elim · Devil · 게임 exp/conv2-a-px4:proxy4_elim:devil:B:1 · r47 · 드래곤 #3 L2: 샘 (26,15) 처음 거리 10 → r67 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2
- proxy4_elim · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_elim:slithery_fight:A:1 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_elim · Trauma · 게임 exp/conv2-a-px4:proxy4_elim:trauma:B:1 · r223 · 드래곤 #26 L2: 샘 (36,9) 처음 거리 0 → r223 도착, 30라운드 무리 진주 7개 중 우리 5 · 상대 0
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:B:1 · r74 · 드래곤 #11 L2: 샘 (26,15) 처음 거리 12 → r200 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2

## 위협 모형 빈틈 (tg, stack4)

- 이번: 피함(tg) 56% · 위협 칸으로 감(tgx) 5455턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 99% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 97%) · 길이별 L2-5 12195 · L6-9 125 · L10+ 184
- 비교: 피함(tg) 56% · 위협 칸으로 감(tgx) 5433턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 99% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 97%) · 길이별 L2-5 12140 · L6-9 119 · L10+ 205
- 상대별: proxy4_elim 4509회 98% · proxy4_king 4155회 98% · proxy4_swarm 3840회 98%
- 지도별: Autarky 723회 97% · Default 2362회 98% · Devil 1085회 98% · Portals 2회 100% · Prisoners Dilemma 11회 82% · Queen Of Spades 1361회 98% · Schooltime 2946회 98% · Slithery Fight 3054회 98% · Trauma 173회 95% · Trophy 787회 97%
- 국면별: r0-99 2469회 99% · r100-249 6451회 98% · r250-349 2470회 98% · r350-449 924회 98% · r450+ 190회 98%

실패 사례 (254건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r108 · 드래곤 #12 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r109 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r207 · 드래곤 #5 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r209 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:A:1 · r177 · 드래곤 #99 L2: 피함(tg), 적 머리 경로 4칸 · 맨해튼 4칸(길이 2) → 박힘 r178 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:B:1 · r464 · 드래곤 #385 L12: 위협 칸으로 감(tgx), 적 머리 경로 5칸 · 맨해튼 5칸(길이 2) → 박힘 r465 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_king:queen_of_spades:A:1 · r187 · 드래곤 #31 L2: 피함(tg), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r187 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:A:1 · r146 · 드래곤 #13 L2: 피함(tg), 적 머리 경로 2칸 · 맨해튼 2칸(길이 3) → 박힘 r148 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r202 · 드래곤 #16 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r204 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r35 · 드래곤 #12 L5: 피함(tg), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r35 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Trophy · 게임 exp/conv2-a-px4:proxy4_king:trophy:A:1 · r73 · 드래곤 #0 L2: 피함(tg), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r75 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:B:1 · r167 · 드래곤 #5 L2: 피함(tg), 적 머리 경로 5칸 · 맨해튼 5칸(길이 2) → 박힘 r169 박힘(상대 돌진), 상대 길이 3

## 모이기 시작 제한 (gx, stack4; 드래곤 단위)

- 이번: 드래곤 133 (표식 턴 1048) · 끝까지 생존 65% (기준 ≥80%) · 몸(자손 포함) 끝까지 97% · 뒤에 희생 먹이기(feed)로 끝남 4
- 비교: 드래곤 68 (표식 턴 438) · 끝까지 생존 62% (기준 ≥80%) · 몸(자손 포함) 끝까지 100% · 뒤에 희생 먹이기(feed)로 끝남 6
- 상대별: proxy4_elim 28회 79% · proxy4_king 28회 82% · proxy4_swarm 77회 53%
- 지도별: Autarky 35회 40% · Portals 66회 64% · Queen Of Spades 4회 100% · Schooltime 6회 83% · Slithery Fight 22회 95%
- 국면별: r450+ 133회 65%

실패 사례 (47건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r471 · 드래곤 #608 L7: gx 3턴 (r471–r473) → 죽음 r476 갇힘
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:B:1 · r480 · 드래곤 #495 L14: gx 2턴 (r480–r481) → 죽음 r484 갇힘
- proxy4_swarm · Portals · 게임 exp/conv2-a-px4:proxy4_swarm:portals:A:1 · r471 · 드래곤 #607 L14: gx 2턴 (r471–r472) → 죽음 r475 갇힘
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:A:1 · r482 · 드래곤 #510 L4: gx 3턴 (r482–r484) → 죽음 r484 갇힘, 상대 길이 6
- proxy4_elim · Portals · 게임 exp/conv2-a-px4:proxy4_elim:portals:B:1 · r483 · 드래곤 #567 L5: gx 8턴 (r483–r493) → 죽음 r496 갇힘, 상대 길이 16
- proxy4_elim · Schooltime · 게임 exp/conv2-a-px4:proxy4_elim:schooltime:A:1 · r494 · 드래곤 #441 L13: gx 1턴 (r494–r494) → 죽음 r498 희생
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r475 · 드래곤 #613 L8: gx 2턴 (r475–r481) → 죽음 r484 갇힘, 상대 길이 9
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r482 · 드래곤 #617 L6: gx 8턴 (r482–r489) → 죽음 r494 갇힘
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r487 · 드래곤 #615 L13: gx 4턴 (r487–r490) → 죽음 r493 갇힘, 상대 길이 16
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r481 · 드래곤 #548 L7: gx 2턴 (r481–r482) → 죽음 r484 갇힘

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 134개 중 우리 팀 97% (지목한 아군 75%) · 상대 1% · 지목 아군 끝까지 생존 54% (그 뒤 죽은 원인: 희생 10, 갇힘 25, 박힘(상대 돌진) 1, 돌진 1, 아군 머리 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 74% · 최종 왕 33% (최종 왕이 지목 아군의 자손 56%)
- 비교: 실행 100% · 떨군 진주 263개 중 우리 팀 98% (지목한 아군 68%) · 상대 2% · 지목 아군 끝까지 생존 45% (그 뒤 죽은 원인: 희생 12, 갇힘 79, 박힘(상대 돌진) 1, 돌진 2, 아군 머리 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 82% · 최종 왕 34% (최종 왕이 지목 아군의 자손 50%)
- 상대별: proxy4_elim 34회 97% · proxy4_king 27회 96% · proxy4_swarm 24회 96%
- 지도별: Autarky 19회 100% · Default 3회 100% · Devil 1회 100% · Portals 12회 100% · Prisoners Dilemma 6회 83% · Queen Of Spades 8회 88% · Schooltime 2회 100% · Slithery Fight 19회 95% · Trauma 15회 100%
- 국면별: r250-349 31회 100% · r350-449 45회 96% · r450+ 9회 89%

실패 사례 (3건 중 3건, 기보 확인용):
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:B:1 · r417 · 드래곤 #339 L3: #187(L8)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1; 지목 아군 r454 갇힘에 사망
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r493 · 드래곤 #809 L4: #530(L22)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_elim · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_elim:queen_of_spades:A:1 · r370 · 드래곤 #53 L4: #127(L12)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 77% · 조각 30라운드 생존 88% · 30라운드 안 1개 이상 먹음 54% (살아서 먹음 46%) · 평생 먹은 진주 평균 3.2 · 나중에 아군을 먹임 27% (conv 3, feed 4, 분열 뒤 평균 65.9라운드) · 끝까지 생존 38% · 30라운드 안 죽은 원인: 박힘(상대 돌진) 1, 갇힘 1, 희생 1
- 비교: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 87% · 조각 30라운드 생존 61% · 30라운드 안 1개 이상 먹음 65% (살아서 먹음 42%) · 평생 먹은 진주 평균 2.7 · 나중에 아군을 먹임 61% (conv 10, feed 9, 분열 뒤 평균 47.6라운드) · 끝까지 생존 6% · 30라운드 안 죽은 원인: 갇힘 4, 희생 8
- 상대별: proxy4_elim 11회 91% · proxy4_king 6회 50% · proxy4_swarm 9회 33%
- 지도별: Autarky 3회 100% · Default 2회 50% · Portals 1회 0% · Schooltime 4회 75% · Slithery Fight 11회 36% · Trauma 5회 100%
- 국면별: r250-349 7회 57% · r350-449 19회 63%

실패 사례 (10건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r369 · 드래곤 #151 L9: 조각 L2 → 30라운드 생존, 먹은 진주 0 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r410 · 드래곤 #533 L12: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:A:1 · r405 · 드래곤 #321 L7: 조각 L2 → 조각 죽음 r418 박힘(상대 돌진), 상대 길이 5, 30라운드 안 먹은 진주 2 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:A:1 · r416 · 드래곤 #922 L8: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_elim:slithery_fight:B:1 · r404 · 드래곤 #36 L11: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r308 · 드래곤 #11 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r318 · 드래곤 #681 L12: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r333 · 드래곤 #681 L11: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r364 · 드래곤 #507 L13: 조각 L2 → 조각 죽음 r379 갇힘, 상대 길이 17, 30라운드 안 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r380 · 드래곤 #507 L11: 조각 L2 → 30라운드 생존, 먹은 진주 0

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 2405개 (표식 턴 6080, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 0, 이미 없음 209) · 사망 진주 2196개 중 우리가 먹음 80% · 상대 18% · 아무도 안 먹음 2% · 표적으로 삼은 드래곤이 먹음 66% · 우리가 먹기까지 평균 3.5라운드 · 상대 머리가 같거나 더 가까웠던 715개: 우리 54% 대 상대 45% · 박치기 진주 378개: 우리 52% 대 상대 48% · 우리 팀 사망 진주 81% · 사망 뒤 첫 표적까지 평균 1.3라운드
- 비교: 표적 진주 2360개 (표식 턴 5857, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 0, 이미 없음 203) · 사망 진주 2157개 중 우리가 먹음 80% · 상대 19% · 아무도 안 먹음 1% · 표적으로 삼은 드래곤이 먹음 65% · 우리가 먹기까지 평균 3.7라운드 · 상대 머리가 같거나 더 가까웠던 704개: 우리 53% 대 상대 46% · 박치기 진주 378개: 우리 52% 대 상대 48% · 우리 팀 사망 진주 81% · 사망 뒤 첫 표적까지 평균 1.4라운드
- 상대별: proxy4_elim 808회 81% · proxy4_king 846회 81% · proxy4_swarm 751회 79%
- 지도별: Autarky 262회 95% · Default 194회 74% · Devil 145회 62% · Portals 580회 97% · Prisoners Dilemma 116회 90% · Queen Of Spades 175회 63% · Schooltime 200회 59% · Slithery Fight 612회 74% · Trauma 90회 81% · Trophy 31회 54%
- 국면별: r0-99 281회 71% · r100-249 819회 75% · r250-349 560회 79% · r350-449 604회 90% · r450+ 141회 87%

실패 사례 (436건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r212 · 드래곤 #92 L3: 진주 (14,16), 우리 머리 2칸 · 상대 머리 3칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 2턴
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r371 · 드래곤 #3 L2: 진주 (21,11), 우리 머리 3칸 · 상대 머리 3칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (5라운드 뒤), 표식 4턴
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:A:1 · r72 · 드래곤 #10 L3: 진주 (9,6), 우리 머리 3칸 · 상대 머리 3칸, 박치기 1라운드 뒤 → 상대가 먹음 (5라운드 뒤), 표식 3턴
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r154 · 드래곤 #114 L3: 진주 (12,14), 우리 머리 4칸 · 상대 머리 1칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (1라운드 뒤), 표식 1턴
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:B:1 · r284 · 드래곤 #194 L2: 진주 (16,13), 우리 머리 4칸 · 상대 머리 1칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_king:queen_of_spades:A:1 · r57 · 드래곤 #2 L3: 진주 (8,33), 우리 머리 4칸 · 상대 머리 3칸, 박치기 1라운드 뒤 → 상대가 먹음 (6라운드 뒤), 표식 1턴
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:A:1 · r147 · 드래곤 #10 L2: 진주 (2,7), 우리 머리 4칸 · 상대 머리 1칸, 박치기 1라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r204 · 드래곤 #16 L2: 진주 (21,9), 우리 머리 4칸 · 상대 머리 2칸, 상대 사망 3라운드 뒤 → 아무도 안 먹음, 표식 1턴
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r4 · 드래곤 #26 L2: 진주 (33,5), 우리 머리 5칸 · 상대 머리 10칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (26라운드 뒤), 표식 3턴
- proxy4_king · Trophy · 게임 exp/conv2-a-px4:proxy4_king:trophy:A:1 · r61 · 드래곤 #13 L2: 진주 (2,12), 우리 머리 4칸 · 상대 머리 3칸, 우리 팀 사망 2라운드 뒤 → 상대가 먹음 (3라운드 뒤), 표식 2턴

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 941 (그중 통로 고리 세대 712, 판정에서 뺌) · 고리 밖 229: 처음 거리 평균 10.9 → 최소 5.6 · 3칸 안까지 감 36% · 희생까지 함 38% · 가는 길에 죽음 30% · 끝까지 생존 31%
- 비교: 모이기 드래곤 831 (그중 통로 고리 세대 626, 판정에서 뺌) · 고리 밖 205: 처음 거리 평균 9.6 → 최소 5.1 · 3칸 안까지 감 41% · 희생까지 함 52% · 가는 길에 죽음 24% · 끝까지 생존 24%
- 상대별: proxy4_elim 278회 77% · proxy4_king 271회 79% · proxy4_swarm 392회 76%
- 지도별: Autarky 314회 88% · Default 14회 64% · Devil 8회 80% · Portals 346회 81% · Prisoners Dilemma 118회 81% · Queen Of Spades 14회 73% · Schooltime 29회 61% · Slithery Fight 65회 67% · Trauma 33회 57%
- 국면별: r250-349 217회 81% · r350-449 600회 79% · r450+ 124회 63%

실패 사례 (87건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r340 · 드래곤 #96 L6: 왕까지 거리 5 → 최소 5 (8턴)
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:B:1 · r435 · 드래곤 #64 L4: 왕까지 거리 5 → 최소 5 (1턴)
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r348 · 드래곤 #509 L9: 왕까지 거리 8 → 최소 4 (21턴), 가는 길에 죽음 r369 갇힘, 상대 길이 6
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:A:1 · r435 · 드래곤 #385 L20: 왕까지 거리 7 → 최소 7 (1턴)
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:A:1 · r412 · 드래곤 #10 L4: 왕까지 거리 30 → 최소 11 (67턴), 가는 길에 죽음 r478 희생, 상대 길이 18
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r376 · 드래곤 #148 L5: 왕까지 거리 17 → 최소 17 (20턴)
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r341 · 드래곤 #287 L4: 왕까지 거리 14 → 최소 12 (25턴), 가는 길에 죽음 r456 돌진, 상대 길이 15
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:B:1 · r373 · 드래곤 #233 L4: 왕까지 거리 14 → 최소 5 (41턴), 가는 길에 죽음 r414 희생
- proxy4_swarm · Default · 게임 exp/conv2-a-px4:proxy4_swarm:default:A:1 · r354 · 드래곤 #128 L4: 왕까지 거리 17 → 최소 5 (7턴), 가는 길에 죽음 r361 희생
- proxy4_swarm · Devil · 게임 exp/conv2-a-px4:proxy4_swarm:devil:B:1 · r405 · 드래곤 #491 L8: 왕까지 거리 7 → 최소 7 (1턴), 가는 길에 죽음 r428 희생

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 386개 중 우리 팀 85% (지목한 아군 57%) · 상대 6% · 지목 아군 끝까지 생존 68% (그 뒤 죽은 원인: 희생 14, 갇힘 20, 돌진 2, 박힘(상대 돌진) 4, 아군 머리 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 78% · 최종 왕 49% (최종 왕이 지목 아군의 자손 63%)
- 비교: 실행 100% · 떨군 진주 509개 중 우리 팀 88% (지목한 아군 60%) · 상대 5% · 지목 아군 끝까지 생존 68% (그 뒤 죽은 원인: 갇힘 26, 희생 17, 아군 머리 2, 돌진 1, 박힘(상대 돌진) 5) · 지목 아군의 몸(자손 포함)이 끝까지 삶 89% · 최종 왕 47% (최종 왕이 지목 아군의 자손 58%)
- 상대별: proxy4_elim 48회 85% · proxy4_king 47회 87% · proxy4_swarm 35회 91%
- 지도별: Autarky 33회 91% · Default 7회 71% · Devil 6회 100% · Portals 18회 100% · Prisoners Dilemma 23회 87% · Queen Of Spades 9회 78% · Schooltime 6회 67% · Slithery Fight 18회 83% · Trauma 10회 90%
- 국면별: r250-349 16회 94% · r350-449 79회 92% · r450+ 35회 74%

실패 사례 (16건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r340 · 드래곤 #351 L5: #96(L6)에게 희생 → 진주 3개 중 우리 1, 지목 아군 0, 상대 0
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:B:1 · r353 · 드래곤 #144 L6: #117(L10)에게 희생 → 진주 3개 중 우리 0, 지목 아군 0, 상대 3; 지목 아군 r463 희생에 사망
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:A:1 · r487 · 드래곤 #414 L10: #385(L24)에게 희생 → 진주 5개 중 우리 1, 지목 아군 1, 상대 2
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:A:1 · r498 · 드래곤 #551 L4: #527(L10)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:A:1 · r492 · 드래곤 #985 L5: #993(L13)에게 희생 → 진주 3개 중 우리 2, 지목 아군 1, 상대 1
- proxy4_swarm · Trauma · 게임 exp/conv2-a-px4:proxy4_swarm:trauma:B:1 · r372 · 드래곤 #3 L4: #132(L6)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2; 지목 아군 r379 박힘(상대 돌진)에 사망
- proxy4_elim · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_elim:prisoners_dilemma:A:1 · r478 · 드래곤 #353 L11: #146(L24)에게 희생 → 진주 6개 중 우리 0, 지목 아군 0, 상대 4
- proxy4_elim · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_elim:queen_of_spades:B:1 · r443 · 드래곤 #51 L4: #87(L25)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2
- proxy4_elim · Schooltime · 게임 exp/conv2-a-px4:proxy4_elim:schooltime:A:1 · r475 · 드래곤 #26 L18: #201(L24)에게 희생 → 진주 9개 중 우리 3, 지목 아군 3, 상대 2
- proxy4_elim · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_elim:slithery_fight:A:1 · r476 · 드래곤 #15 L4: #98(L5)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2

## 막다른 길 한입 (pocket-eat)

- 이번: 한입 100% · 2턴 안 분열 83% · 30라운드 뒤 가족 길이 변화 5 (줄지 않음 83%)
- 비교: 한입 100% · 2턴 안 분열 75% · 30라운드 뒤 가족 길이 변화 4 (줄지 않음 75%)
- 상대별: proxy4_elim 2회 100% · proxy4_king 1회 100% · proxy4_swarm 3회 33%
- 지도별: Devil 1회 0% · Portals 5회 80%
- 국면별: r0-99 5회 80% · r100-249 1회 0%

실패 사례 (2건 중 2건, 기보 확인용):
- proxy4_swarm · Devil · 게임 exp/conv2-a-px4:proxy4_swarm:devil:A:1 · r60 · 드래곤 #38 L4: 한입, 분열(새끼 L3), 30라운드 뒤 가족 길이 변화 -2
- proxy4_swarm · Portals · 게임 exp/conv2-a-px4:proxy4_swarm:portals:A:1 · r131 · 드래곤 #122 L6: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 4

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 22% · 30라운드 뒤 가족 길이 변화 8
- 비교: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 99% · 새끼 자체 10라운드 생존 20% · 30라운드 뒤 가족 길이 변화 8.1
- 상대별: proxy4_elim 1453회 98% · proxy4_king 1348회 98% · proxy4_swarm 1491회 99%
- 지도별: Autarky 1563회 100% · Default 33회 100% · Devil 58회 90% · Portals 918회 96% · Prisoners Dilemma 1440회 99% · Queen Of Spades 48회 100% · Schooltime 35회 97% · Slithery Fight 134회 96% · Trauma 63회 87%
- 국면별: r0-99 785회 99% · r100-249 1218회 99% · r250-349 968회 99% · r350-449 950회 97% · r450+ 371회 96%

실패 사례 (81건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r352 · 드래곤 #320 L9: 새끼 L7 → 새끼 죽음 r359 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -9
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r146 · 드래곤 #144 L5: 새끼 L3 → 새끼 죽음 r147 갇힘, 상대 길이 7, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:A:1 · r479 · 드래곤 #409 L12: 새끼 L10 → 새끼 죽음 r483 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -12
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:B:1 · r319 · 드래곤 #242 L5: 새끼 L3 → 새끼 죽음 r321 갇힘, 상대 길이 16, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_swarm · Devil · 게임 exp/conv2-a-px4:proxy4_swarm:devil:A:1 · r92 · 드래곤 #81 L5: 새끼 L3 → 새끼 죽음 r97 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_swarm · Portals · 게임 exp/conv2-a-px4:proxy4_swarm:portals:A:1 · r283 · 드래곤 #370 L8: 새끼 L6 → 새끼 죽음 r284 아군 머리, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -8
- proxy4_swarm · Schooltime · 게임 exp/conv2-a-px4:proxy4_swarm:schooltime:A:1 · r392 · 드래곤 #363 L7: 새끼 L5 → 새끼 죽음 r402 적 몸통, 상대 길이 17, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7
- proxy4_swarm · Trauma · 게임 exp/conv2-a-px4:proxy4_swarm:trauma:B:1 · r350 · 드래곤 #212 L7: 새끼 L5 → 새끼 죽음 r350 갇힘, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r246 · 드래곤 #13 L4: 새끼 L2 → 새끼 죽음 r246 갇힘, 상대 길이 4, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_elim · Autarky · 게임 exp/conv2-a-px4:proxy4_elim:autarky:B:1 · r348 · 드래곤 #195 L5: 새끼 L3 → 새끼 죽음 r352 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 86% · 그 밖(진짜로 갇힘) 609회
- 비교: 탈출 분열 뒤 남은 조각(고리의 일부) 88% · 그 밖(진짜로 갇힘) 537회
- 상대별: proxy4_elim 1501회 – · proxy4_king 1438회 – · proxy4_swarm 1507회 –
- 지도별: Autarky 1577회 – · Default 57회 – · Devil 52회 – · Portals 833회 – · Prisoners Dilemma 1461회 – · Queen Of Spades 57회 – · Schooltime 51회 – · Slithery Fight 252회 – · Trauma 100회 – · Trophy 6회 –
- 국면별: r0-99 816회 – · r100-249 1405회 – · r250-349 963회 – · r350-449 916회 – · r450+ 346회 –

## 정책 분열 (split)

- 이번: 분열 100% · 새끼 30라운드 생존 20% · 30라운드 뒤 가족 길이 변화 -6.4
- 비교: 분열 100% · 새끼 30라운드 생존 20% · 30라운드 뒤 가족 길이 변화 -6.4
- 상대별: proxy4_elim 4회 0% · proxy4_king 1회 100%
- 지도별: Default 4회 0% · Queen Of Spades 1회 100%
- 국면별: r350-449 5회 20%

실패 사례 (4건 중 4건, 기보 확인용):
- proxy4_elim · Default · 게임 exp/conv2-a-px4:proxy4_elim:default:A:1 · r408 · 드래곤 #9 L17: 새끼 L2 → 새끼 죽음 r410 갇힘, 30라운드 뒤 가족 길이 변화 1
- proxy4_elim · Default · 게임 exp/conv2-a-px4:proxy4_elim:default:A:1 · r428 · 드래곤 #9 L19: 새끼 L2 → 새끼 죽음 r431 갇힘, 상대 길이 17, 30라운드 뒤 가족 길이 변화 -1
- proxy4_elim · Default · 게임 exp/conv2-a-px4:proxy4_elim:default:A:1 · r435 · 드래곤 #9 L19: 새끼 L2 → 새끼 죽음 r435 돌진, 상대 길이 18, 30라운드 뒤 가족 길이 변화 -19
- proxy4_elim · Default · 게임 exp/conv2-a-px4:proxy4_elim:default:A:1 · r446 · 드래곤 #9 L18: 새끼 L2 → 새끼 죽음 r452 갇힘, 상대 길이 17, 30라운드 뒤 가족 길이 변화 -18

## 탈출 질주 3칸 (esc)

- 이번: 질주 99% · 짧은 적 머리 4칸 안 78% · 몸 생존 5라운드 97% · 10라운드 96% (드래곤 자체 93%) · 10라운드 길이 변화 -3.6
- 비교: 질주 99% · 짧은 적 머리 4칸 안 69% · 몸 생존 5라운드 96% · 10라운드 96% (드래곤 자체 92%) · 10라운드 길이 변화 -3.4
- 상대별: proxy4_elim 29회 90% · proxy4_king 28회 100% · proxy4_swarm 15회 93%
- 지도별: Default 7회 100% · Devil 3회 100% · Prisoners Dilemma 2회 50% · Queen Of Spades 14회 100% · Schooltime 13회 100% · Slithery Fight 30회 90% · Trauma 3회 100%
- 국면별: r0-99 1회 100% · r100-249 14회 86% · r250-349 8회 100% · r350-449 26회 96% · r450+ 23회 96%

실패 사례 (4건 중 4건, 기보 확인용):
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r228 · 드래곤 #16 L23: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r228 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_elim:prisoners_dilemma:B:1 · r467 · 드래곤 #96 L23: 질주 3칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r469 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_elim:slithery_fight:A:1 · r219 · 드래곤 #569 L8: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r220 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_elim:slithery_fight:B:1 · r435 · 드래곤 #516 L6: 질주 3칸 (가장 가까운 짧은 적 머리 6칸) → 죽음 r444 희생

## 위협 피하기 2칸 질주

- 이번: 질주 99% · 몸 10라운드 생존 95% (드래곤 자체 90%)
- 비교: 질주 99% · 몸 10라운드 생존 94% (드래곤 자체 90%)
- 상대별: proxy4_elim 224회 92% · proxy4_king 222회 95% · proxy4_swarm 226회 95%
- 지도별: Autarky 36회 100% · Default 87회 93% · Devil 53회 94% · Prisoners Dilemma 2회 100% · Queen Of Spades 103회 96% · Schooltime 177회 92% · Slithery Fight 168회 94% · Trauma 16회 100% · Trophy 30회 93%
- 국면별: r0-99 151회 97% · r100-249 253회 92% · r250-349 146회 94% · r350-449 106회 96% · r450+ 16회 88%

실패 사례 (40건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r197 · 드래곤 #0 L2: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 2) → 죽음 r197 질주 불가
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:B:1 · r94 · 드래곤 #23 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r102 돌진, 상대 길이 2
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:A:1 · r231 · 드래곤 #34 L3: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 4) → 죽음 r235 박힘(상대 돌진), 상대 길이 4
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r123 · 드래곤 #182 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r132 갇힘, 상대 길이 4
- proxy4_swarm · Default · 게임 exp/conv2-a-px4:proxy4_swarm:default:B:1 · r233 · 드래곤 #87 L3: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 5) → 죽음 r235 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_swarm:queen_of_spades:A:1 · r350 · 드래곤 #49 L5: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 3) → 죽음 r351 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Schooltime · 게임 exp/conv2-a-px4:proxy4_swarm:schooltime:A:1 · r222 · 드래곤 #119 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r226 돌진, 상대 길이 26
- proxy4_swarm · Trophy · 게임 exp/conv2-a-px4:proxy4_swarm:trophy:A:1 · r107 · 드래곤 #0 L9: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r111 박힘(상대 돌진), 상대 길이 4
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r224 · 드래곤 #266 L4: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 3) → 죽음 r225 돌진, 상대 길이 8
- proxy4_elim · Default · 게임 exp/conv2-a-px4:proxy4_elim:default:A:1 · r1 · 드래곤 #6 L4: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r7 박힘(상대 돌진), 상대 길이 2

## 포털 통과 (전체; PORTAL?=미탐색 출구)

- 이번: 미탐색 출구 1112회(몸 3라운드 생존 93%) · 전체 몸 생존 3라운드 93% (드래곤 자체 78%) · 10라운드 89% · 10라운드 안 먹은 진주 0.9
- 비교: 미탐색 출구 1005회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 94% (드래곤 자체 79%) · 10라운드 89% · 10라운드 안 먹은 진주 0.9
- 상대별: proxy4_elim 771회 93% · proxy4_king 1058회 94% · proxy4_swarm 819회 93%
- 지도별: Autarky 395회 94% · Default 532회 96% · Portals 1104회 91% · Prisoners Dilemma 68회 97% · Queen Of Spades 80회 88% · Schooltime 127회 90% · Slithery Fight 187회 95% · Trauma 154회 96% · Trophy 1회 100%
- 국면별: r0-99 285회 95% · r100-249 975회 95% · r250-349 792회 93% · r350-449 494회 90% · r450+ 102회 91%

실패 사례 (178건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r185 · 드래곤 #35 L3: 포털 → 죽음 r185 갇힘, 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r285 · 드래곤 #209 L3: 포털 → 죽음 r286 갇힘, 10라운드 안 진주 0
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r66 · 드래곤 #23 L6: 포털 → 죽음 r66 갇힘, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:A:1 · r267 · 드래곤 #151 L3: 포털(미탐색 출구) → 죽음 r267 아군 머리, 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_king:queen_of_spades:A:1 · r50 · 드래곤 #12 L2: 포털 → 죽음 r53 갇힘, 10라운드 안 진주 0
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:A:1 · r478 · 드래곤 #10 L19: 포털 → 죽음 r478 희생, 상대 길이 18, 10라운드 안 진주 0
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r274 · 드래곤 #50 L3: 포털 → 죽음 r276 박힘(상대 돌진), 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:B:1 · r183 · 드래곤 #384 L3: 포털(미탐색 출구) → 죽음 r183 아군 머리, 상대 길이 6, 10라운드 안 진주 0
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:B:1 · r104 · 드래곤 #85 L3: 포털 → 죽음 r104 아군 머리, 상대 길이 3, 10라운드 안 진주 0
- proxy4_swarm · Default · 게임 exp/conv2-a-px4:proxy4_swarm:default:B:1 · r205 · 드래곤 #57 L2: 포털 → 죽음 r208 갇힘, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 20, 경로 31) · 잡은 길이 ≥ 우리 100% · 두 몸의 진주 우리 70 대 상대 308
- 비교: 충돌 성사 100% (인접 18, 경로 33) · 잡은 길이 ≥ 우리 98% · 두 몸의 진주 우리 121 대 상대 271
- 상대별: proxy4_elim 10회 10% · proxy4_king 12회 8% · proxy4_swarm 29회 17%
- 지도별: Default 2회 0% · Devil 3회 33% · Prisoners Dilemma 1회 0% · Queen Of Spades 5회 0% · Schooltime 19회 5% · Slithery Fight 19회 26% · Trauma 2회 0%
- 국면별: r0-99 1회 0% · r100-249 12회 17% · r250-349 15회 0% · r350-449 18회 11% · r450+ 5회 60%

실패 사례 (44건 중 10건, 기보 확인용):
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:B:1 · r460 · 드래곤 #127 L4: 돌진 경로 2칸 → 상대 L20 잡음, 진주 우리 0 대 상대 6
- proxy4_king · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_king:queen_of_spades:A:1 · r378 · 드래곤 #28 L4: 돌진 경로 3칸 → 상대 L11 잡음, 진주 우리 0 대 상대 8
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:A:1 · r192 · 드래곤 #102 L5: 돌진 경로 3칸 → 상대 L13 잡음, 진주 우리 0 대 상대 10
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r297 · 드래곤 #116 L4: 돌진 경로 3칸 → 상대 L6 잡음, 진주 우리 0 대 상대 5
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r272 · 드래곤 #307 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_swarm · Default · 게임 exp/conv2-a-px4:proxy4_swarm:default:A:1 · r128 · 드래곤 #37 L2: 돌진 경로 1칸 → 상대 L3 잡음, 진주 우리 0 대 상대 3
- proxy4_swarm · Devil · 게임 exp/conv2-a-px4:proxy4_swarm:devil:A:1 · r358 · 드래곤 #9 L4: 돌진 경로 2칸 → 상대 L14 잡음, 진주 우리 2 대 상대 7
- proxy4_swarm · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_swarm:queen_of_spades:B:1 · r280 · 드래곤 #57 L3: 돌진 경로 2칸 → 상대 L5 잡음, 진주 우리 0 대 상대 5
- proxy4_swarm · Schooltime · 게임 exp/conv2-a-px4:proxy4_swarm:schooltime:A:1 · r176 · 드래곤 #108 L3: 돌진 경로 2칸 → 상대 L5 잡음, 진주 우리 1 대 상대 4
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:A:1 · r279 · 드래곤 #30 L3: 돌진 경로 1칸 → 상대 L6 잡음, 진주 우리 0 대 상대 5

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 비교: 먹음 100%
- 상대별: proxy4_elim 65회 100% · proxy4_king 71회 100% · proxy4_swarm 39회 100%
- 지도별: Autarky 9회 100% · Default 16회 100% · Devil 9회 100% · Portals 25회 100% · Prisoners Dilemma 1회 100% · Queen Of Spades 16회 100% · Schooltime 35회 100% · Slithery Fight 49회 100% · Trauma 4회 100% · Trophy 11회 100%
- 국면별: r0-99 33회 100% · r100-249 60회 100% · r250-349 29회 100% · r350-449 45회 100% · r450+ 8회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 87%
- 비교: 그 턴 사망 0% · 10라운드 생존 87%
- 상대별: proxy4_elim 34회 – · proxy4_king 23회 – · proxy4_swarm 26회 –
- 지도별: Autarky 1회 – · Default 5회 – · Devil 5회 – · Prisoners Dilemma 1회 – · Queen Of Spades 18회 – · Schooltime 23회 – · Slithery Fight 27회 – · Trauma 2회 – · Trophy 1회 –
- 국면별: r0-99 13회 – · r100-249 31회 – · r250-349 16회 – · r350-449 19회 – · r450+ 4회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 비교: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 5회 – · proxy4_king 15회 – · proxy4_swarm 12회 –
- 지도별: Default 1회 – · Devil 8회 – · Queen Of Spades 5회 – · Schooltime 4회 – · Slithery Fight 12회 – · Trauma 2회 –
- 국면별: r0-99 4회 – · r100-249 21회 – · r250-349 3회 – · r350-449 3회 – · r450+ 1회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/conv2-a-px4` | 60 | 30 (0.50) | 47% | 0 (0.00) | 0 (0.00) | 9 | 21 | 0 | 2/7 (7) | 100 (1.67; 필사 29) | 37/69 (129.5) |
| 비교 `exp/stack5-a-px4` | 60 | 29 (0.48) | 38% | 0 (0.00) | 0 (0.00) | 10 | 18 | 0 | 3/6 (10.5) | 81 (1.35; 필사 20) | 14/50 (49) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.
- 이번 `exp/conv2-a-px4`: gx 표식 턴 1048 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- 비교 `exp/stack5-a-px4`: gx 표식 턴 438 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/conv2-a-px4` | 60 | 41364 | 0.7% (276) | 14.6% (6049) | 4441 | 1.6% (71) | 4.5% (198) | 21.8% (966/4441) |
| 비교 `exp/stack5-a-px4` | 60 | 41158 | 0.7% (283) | 14.3% (5873) | 4498 | 1.1% (50) | 3.6% (161) | 22.9% (1028/4498) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/conv2-a-px4` | 전체 | 분열 | 7 (17%) | 16.6 | 128% | 159% | 3 | 0 |
| 이번 `exp/conv2-a-px4` | 전체 | 2칸 질주 | 10 (24%) | 17.4 | 90% | 61% | 4 | 0 |
| 이번 `exp/conv2-a-px4` | 전체 | 3칸 질주 | 8 (20%) | 13.3 | 86% | 97% | 1 | 0 |
| 이번 `exp/conv2-a-px4` | 전체 | 한 걸음 | 16 (39%) | 10.9 | 46% | 48% | 10 | 8 |
| 이번 `exp/conv2-a-px4` | 4칸 이상 | 분열 | 6 (24%) | 15 | 136% | 157% | 3 | 0 |
| 이번 `exp/conv2-a-px4` | 4칸 이상 | 2칸 질주 | 8 (32%) | 17.4 | 88% | 60% | 3 | 0 |
| 이번 `exp/conv2-a-px4` | 4칸 이상 | 3칸 질주 | 6 (24%) | 11.7 | 89% | 106% | 1 | 0 |
| 이번 `exp/conv2-a-px4` | 4칸 이상 | 한 걸음 | 5 (20%) | 12.4 | 48% | 44% | 4 | 3 |
| 비교 `exp/stack5-a-px4` | 전체 | 분열 | 9 (20%) | 13 | 145% | 167% | 6 | 0 |
| 비교 `exp/stack5-a-px4` | 전체 | 2칸 질주 | 11 (25%) | 17.1 | 91% | 69% | 4 | 0 |
| 비교 `exp/stack5-a-px4` | 전체 | 3칸 질주 | 7 (16%) | 18.4 | 91% | 93% | 1 | 0 |
| 비교 `exp/stack5-a-px4` | 전체 | 한 걸음 | 17 (39%) | 11.2 | 43% | 51% | 12 | 9 |
| 비교 `exp/stack5-a-px4` | 4칸 이상 | 분열 | 9 (30%) | 13 | 145% | 167% | 6 | 0 |
| 비교 `exp/stack5-a-px4` | 4칸 이상 | 2칸 질주 | 9 (30%) | 17 | 90% | 69% | 3 | 0 |
| 비교 `exp/stack5-a-px4` | 4칸 이상 | 3칸 질주 | 5 (17%) | 18.6 | 96% | 98% | 1 | 0 |
| 비교 `exp/stack5-a-px4` | 4칸 이상 | 한 걸음 | 7 (23%) | 11.7 | 45% | 55% | 6 | 4 |

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (100건 중 10건):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r109 · 드래곤 #2 L2: v7.1 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r185 · 드래곤 #35 L3: vnull → 갇힘, 막은 우리 드래곤 L3
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r221 · 드래곤 #75 L3: v1.6 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r230 · 드래곤 #41 L2: v7.3 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:A:1 · r265 · 드래곤 #136 L3: v8.8 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:B:1 · r156 · 드래곤 #39 L5: v7.6 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:B:1 · r168 · 드래곤 #35 L3: v7.9 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:B:1 · r228 · 드래곤 #55 L3: v7.6 → 아군 머리, 막은 우리 드래곤 L4
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:B:1 · r234 · 드래곤 #36 L2: v7 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:B:1 · r273 · 드래곤 #86 L3: v0.5 PORTAL? → 아군 머리, 막은 우리 드래곤 L4

## stack5: 영토 덮기 (csplit · F · cov) 게이트와 가설 수준 지표

- 기준값은 `research/experiments/cand-stack5.md`(웨이브 전)에서, 상위권 승자(TW) 값과 merge2 값은 `research/observations/top-territory.md`에서 왔다. 정의는 영토 연구의 `exp/territory-analysis/extract.js`와 같다(영토 = 시작 몸에서 더 가까운 팀의 칸, 샘 = 그 판 판본 파일의 평균 간격 ≤12, 보로노이 = 용량 1/평균 간격 가중, 거리 = 지도 위 이동 거리, 몸은 무시).

### 게이트 (기능 적용)

| 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|
| csplit 발동: 500라운드형 지도 r0–249 판당 | ≥20 | 23.7 (전체 1091회) | 23.7 (전체 1091회) |
| csplit 설계 상황: 부모가 팀 최장(≥8)이 아님 | ≥90% | 100% | 100% |
| csplit 새끼가 30라운드 안에 자연 진주 ≥1개 | ≥45% (TW 47% · 45%) | 40% (1091마리) | 40% (1091마리) |
| csplit 새끼 30라운드 생존 | ≥30% (TW 34% · 51%) | 75% | 75% |
| F 목표(드래곤·샘) 수, 3걸음 안 도착 | – | 2807, 도착 59% | 2819, 도착 59% |
| F 설계 상황: 실제 우리 영토 샘, 처음 표식 때 다른 우리 머리 3걸음 안 없음 | ≥80% | 79% | 79% |
| F 도착 뒤 30라운드 그 무리 자연 진주의 우리 몫(합산) | ≥85% (TW 자기 샘 90%) | 98% (상대 2%, 11631개) | 98% (상대 2%, 11724개) |
| F 같은 몫의 지도 평균(지도마다 합산, 같은 무게, Portals 제외) | ≥85% | 83% (Autarky 100%, Devil 78%, Prisoners Dilemma 100%, Trauma 90%, Slithery Fight 47%) | 83% (Autarky 100%, Devil 78%, Prisoners Dilemma 100%, Trauma 90%, Slithery Fight 46%) |

### 가설 수준 지표 (관찰; 500라운드형 / 전멸형)

| 지표 | 기준 | 상위권 승자 | merge2 | 이번 | 비교 |
|---|---|---|---|---|---|
| r100 우리 드래곤 수(r100까지 간 판) | ≥15 / ≥10 | 30 / 21 | 4 / 3 | 13.1 / 6.2 | 13.1 / 6.2 |
| r100 우리 영토 보로노이 몫(용량 가중, 판 평균) | ≥80% | 89% / 81% | 66% / 32% | 68% / 40% | 68% / 40% |
| r100 샘 지킴: 우리 영토 샘 중 우리 머리 3걸음 안(판 평균) | ≥50% | 61% / 55% | 22% / – | 26% / 62% | 26% / 62% |
| 우리 영토 자연 진주(r0부터 생성)를 상대가 먹은 몫(합산) | ≤25% | 11% / 16% | 56% / 55% | 55% / 56% | 56% / 57% |
| 우리 영토 샘 진주를 상대가 먹은 몫(합산) | ≤15% | 7% / 6% | 50% / 33% | 48% / 41% | 49% / 41% |

- 판 수(500라운드형 / 전멸형): 이번 30 / 30 · 비교 30 / 30. 판본 파일을 못 찾은 판: 이번 0 · 비교 0.

### 부작용: 우리 드래곤의 죽음 (판당; 전체 / r250 전)

| 원인 | 이번 | 비교 |
|---|---|---|
| 갇힘(빈 이웃 없음; 통로 고리의 남은 조각 포함) | 75.1 / 37.3 | 72.6 / 37.3 |
| 적 머리에 박힘 | 7.8 / 5.6 | 7.9 / 5.6 |
| 우리 드래곤끼리 머리 충돌(둘 다 죽음, 둘 다 셈) | 2.1 / 0.9 | 1.8 / 0.9 |

- 막힘에서 아군 머리를 피해 죽은 턴(no-exit s): 이번 112 · 비교 108

### 지도별 (이번)

| 지도 | 판 | csplit 판당 | 새끼 먹음 ≥1 | 새끼 30R 생존 | F 목표 · 도착 · 무리 진주 우리 몫 | r100 드래곤 | 보로노이 | 샘 지킴 | 상대가 먹은 영토 진주 | 상대가 먹은 샘 진주 |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| Autarky | 6 | 16.3 | 48% | 85% | 361 · 92% · 100% | 9.7 | 96% | 86% | 9% | 8% |
| Default | 6 | 21.8 | 33% | 65% | 0 · – · – | 10.8 | 38% | – | 70% | – |
| Devil | 6 | 12 | 32% | 74% | 149 · 13% · 78% | 8.7 | 29% | 24% | 81% | 83% |
| Portals | 6 | 13.2 | 54% | 56% | 654 · 39% · 99% | 11.3 | 100% | 36% | 0% | 0% |
| Prisoners Dilemma | 6 | 8.2 | 47% | 94% | 1044 · 88% · 100% | 3.7 | 99% | 100% | 2% | 0% |
| Queen Of Spades | 6 | 16 | 50% | 74% | 19 · 26% · – | 3.7 | 25% | – | 72% | – |
| Schooltime | 6 | 26.8 | 48% | 86% | 11 · 0% · – | 16.2 | 26% | 0% | 82% | 62% |
| Slithery Fight | 6 | 47.8 | 29% | 75% | 485 · 21% · 47% | 23.2 | 28% | 7% | 76% | 82% |
| Trauma | 6 | 14.5 | 37% | 64% | 72 · 22% · 90% | 5 | 93% | 0% | 57% | 2% |
| Trophy | 6 | 5.2 | 58% | 81% | 12 · 42% · – | 4.3 | 9% | – | 78% | – |

## cand-conv2: 희생 질량이 최종 왕 계보로 가는가 (kc · k2) 게이트와 가설 수준 지표

- 기준값은 `research/experiments/cand-conv2.md`(온라인 전)에서, 상위권·우리 봇 값은 `research/observations/conversion-chain.md`에서 왔다. 최종 왕 계보 = 끝의 최장 드래곤을 부모 쪽으로 따라간 드래곤들이고, 계보 드래곤 i는 태어난 라운드부터 계보 드래곤 i+1이 태어난 라운드 전까지를 맡는다. "계보 몫" = 떨어진 진주 가운데 그 창 안의 계보 드래곤이 먹은 비율.

| 항목 | 이번 | 비교 |
|---|---|---|
| conv (kc 표식) | 85건 · 진주 134 → 계보 43% · 상대 1% · 지목이 그 순간 계보 52% · 지목이 그 순간 팀 최장 52% | 0건 · 진주 0 → 계보 – · 상대 – · 지목이 그 순간 계보 – · 지목이 그 순간 팀 최장 – |
| conv (kc 없음) | 0건 · 진주 0 → 계보 – · 상대 – · 지목이 그 순간 계보 – · 지목이 그 순간 팀 최장 – | 173건 · 진주 263 → 계보 37% · 상대 2% · 지목이 그 순간 계보 50% · 지목이 그 순간 팀 최장 43% |
| feed (kc 표식) | 130건 · 진주 386 → 계보 43% · 상대 6% · 지목이 그 순간 계보 63% · 지목이 그 순간 팀 최장 44% | 0건 · 진주 0 → 계보 – · 상대 – · 지목이 그 순간 계보 – · 지목이 그 순간 팀 최장 – |
| feed (kc 없음) | 0건 · 진주 0 → 계보 – · 상대 – · 지목이 그 순간 계보 – · 지목이 그 순간 팀 최장 – | 161건 · 진주 509 → 계보 46% · 상대 5% · 지목이 그 순간 계보 55% · 지목이 그 순간 팀 최장 39% |
| k2 | 7건 · 진주 27 → 계보 44% · 상대 7% · 지목이 그 순간 계보 57% · 지목이 그 순간 팀 최장 86% | 0건 · 진주 0 → 계보 – · 상대 – · 지목이 그 순간 계보 – · 지목이 그 순간 팀 최장 – |
| 500라운드형(500까지 간 판) 판 | 30 | 30 |
| k2 발동(판당, 500형 끝까지 간 판) | 3 (0.1) | 0 (0) |
| r300 뒤 우리 희생 진주의 계보 몫 (상위권 승자 24%) | 47% (190/404) | 41% (246/593) |
| r350 뒤 계보가 먹은 우리 희생 진주(판당; 상위권 승자 21.4, merge2 3.8) | 5.5 | 6.5 |
| r400 계보 밖 길이 ≥8 드래곤(판당) · 가족이 계보 밖에서 끝까지 삶 · 계보에 진주를 줌 | 1.4 · 73% (끝 길이 14.3) · 32% | 1.6 · 69% (끝 길이 16.8) · 42% |
| 끝 왕 길이(500형 끝까지 간 판, 판정에 쓰지 않음) | 23 | 26.7 |

