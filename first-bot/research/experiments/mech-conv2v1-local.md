# 구현 적용 확인: cand-conv2 로컬 (흉내 상대 v4, a판 60판)

> 이 보고서는 v1(끌림 켬, 적 거리 3·4) 60판이다. 만들 때 폴더가 `exp/conv2-a-px4`였고, 뒤에 `exp/conv2v1-a-px4`로 옮겼다(게임 키의 폴더 이름은 옛 이름 그대로다). v2는 `mech-conv2-local.md`다.

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
| 두 번째 단계 먹이기 (k2, conv2) | 10 (0.2) | 40% | 0 (0) | – |
| 왕 후보 쪽 끌림 (k2 표식, conv2; 드래곤 단위) | 613 (10.2) | 6% | 0 (0) | – |
| 후보 아닌 아군 희생 보류 (kch, conv2; 드래곤 단위) | 202 (3.4) | 85% | 0 (0) | – |
| 덮기 분열 (csplit, stack5) | 1091 (18.2) | 40% | 1091 (18.2) | 40% |
| 샘 지킴 (F, stack5; 드래곤·샘 단위) | 2807 (46.8) | 96% | 2819 (47) | 96% |
| 위협 모형 빈틈 (tg, stack4) | 12511 (208.5) | 98% | 12464 (207.7) | 98% |
| 모이기 시작 제한 (gx, stack4; 드래곤 단위) | 171 (2.9) | 58% | 68 (1.1) | 62% |
| 큰 아군 곁 희생 (conv, stack1 M1) | 79 (1.3) | 99% | 173 (2.9) | 97% |
| 조각 떼기 (split frag, stack2 S1) | 25 (0.4) | 68% | 31 (0.5) | 84% |
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 2388 (39.8) | 80% | 2360 (39.3) | 80% |
| 왕에게 모이기 (g, 드래곤 단위) | 1165 (19.4) | 76% | 831 (13.9) | 83% |
| 희생 먹이기 (feed) | 129 (2.2) | 91% | 161 (2.7) | 90% |
| 막다른 길 한입 (pocket-eat) | 6 (0.1) | 67% | 8 (0.1) | 50% |
| 탈출 분열 (escape-split) | 4198 (70) | 98% | 4185 (69.8) | 99% |
| 출구 없음 (no-exit) | 4355 (72.6) | – | 4311 (71.9) | – |
| 정책 분열 (split) | 7 (0.1) | 43% | 5 (0.1) | 20% |
| 탈출 질주 3칸 (esc) | 72 (1.2) | 97% | 72 (1.2) | 94% |
| 위협 피하기 2칸 질주 | 677 (11.3) | 94% | 669 (11.2) | 94% |
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 2642 (44) | 94% | 2463 (41.1) | 94% |
| 돌진 (TRADE) | 47 (0.8) | 11% | 51 (0.9) | 27% |
| 먹이 질주 (2칸 이상, 먹은 것) | 173 (2.9) | 100% | 174 (2.9) | 100% |
| 기타 2칸 질주 | 79 (1.3) | – | 86 (1.4) | – |
| 마지막 돌진 (last-trade) | 31 (0.5) | – | 32 (0.5) | – |

- 건강: 턴 231310, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 비교 건강: 턴 222732, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 12852턴 · 끝판(late) 6549턴 · 돌진 신뢰(T, 탈출 끔) 35턴, 그 직후 박혀 죽음 0

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 비교 |
|---|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 2% (47/2693턴) | 2% (45/2686턴) |
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 23.1칸 (5회), 진주 우리 93% · 상대 1% | 36칸 (8.8회), 진주 우리 94% · 상대 1% |
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 0.4칸 (판당 0.03회) | 0.3칸 (판당 0.03회) |
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 23% (1035/4454턴) | 23% (1028/4498턴) |
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.100회 (6건, 90칸) | 판당 0.100회 (6건, 76칸) |
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 7.7마리 (30판) | 6.1마리 (30판) |
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 22회 | 19.4회 |
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 55% (우리 38%) | 56% (우리 37%) |
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 6.7 대 상대 27.9 (9.7회) · 박힌 교환의 우리 몫 20% (231회) | 우리 8.2 대 상대 28.4 (10회) · 박힌 교환의 우리 몫 19% (236회) |
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 8.1개 | 9.2개 |

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 두 번째 단계 먹이기 (k2, conv2)

- 이번: 실행 100% · 설계 상황(지목 아군이 그 순간 팀 최장) 90% · 떨군 진주 44개 중 최종 왕 계보 23% · 우리 팀 43% · 상대 52% · 지목 아군이 그 순간 계보 70% · 최종 왕 60% · 먹인 길이 평균 8.2
- 상대별: proxy4_elim 3회 33% · proxy4_king 2회 50% · proxy4_swarm 5회 40%
- 지도별: Autarky 1회 0% · Devil 1회 0% · Prisoners Dilemma 4회 0% · Queen Of Spades 1회 100% · Trauma 3회 100%
- 국면별: r350-449 7회 14% · r450+ 3회 100%

실패 사례 (6건 중 6건, 기보 확인용):
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:A:1 · r431 · 드래곤 #382 L10: #164(L22)에게 두 번째 단계 희생 → 진주 5개 중 최종 왕 계보 0, 우리 0, 상대 5; 지목 아군 r466 갇힘에 사망
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:B:1 · r404 · 드래곤 #352 L5: #194(L8)에게 두 번째 단계 희생 → 진주 3개 중 최종 왕 계보 0, 우리 3, 상대 0; 지목 아군이 팀 최장 아님; 지목 아군 r419 갇힘에 사망
- proxy4_swarm · Devil · 게임 exp/conv2-a-px4:proxy4_swarm:devil:B:1 · r428 · 드래곤 #491 L12: #97(L16)에게 두 번째 단계 희생 → 진주 6개 중 최종 왕 계보 0, 우리 6, 상대 0
- proxy4_swarm · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_swarm:prisoners_dilemma:B:1 · r425 · 드래곤 #397 L10: #134(L19)에게 두 번째 단계 희생 → 진주 5개 중 최종 왕 계보 0, 우리 0, 상대 5
- proxy4_elim · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_elim:prisoners_dilemma:A:1 · r410 · 드래곤 #302 L11: #146(L21)에게 두 번째 단계 희생 → 진주 6개 중 최종 왕 계보 0, 우리 0, 상대 6
- proxy4_elim · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_elim:prisoners_dilemma:B:1 · r424 · 드래곤 #330 L11: #96(L20)에게 두 번째 단계 희생 → 진주 6개 중 최종 왕 계보 0, 우리 0, 상대 6; 지목 아군 r479 박힘(상대 돌진)에 사망

## 왕 후보 쪽 끌림 (k2 표식, conv2; 드래곤 단위)

- 이번: 드래곤 613 (표식 턴 5955, 시작 길이 평균 11.2) · 표식 희생으로 끝남 6% (k2 6, feed 28, conv 2; 계보가 먹은 진주 52) · 스스로 최종 왕 계보 7% · 끝까지 생존 15%
- 상대별: proxy4_elim 173회 9% · proxy4_king 216회 4% · proxy4_swarm 224회 5%
- 지도별: Autarky 268회 3% · Default 2회 50% · Devil 10회 20% · Portals 190회 6% · Prisoners Dilemma 65회 8% · Queen Of Spades 8회 25% · Schooltime 22회 9% · Slithery Fight 39회 8% · Trauma 9회 22%
- 국면별: r350-449 432회 7% · r450+ 181회 3%

실패 사례 (577건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r400 · 드래곤 #427 L14: 끌림 2턴 (r400–r401) → 죽음 r404 갇힘
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:B:1 · r416 · 드래곤 #554 L5: 끌림 1턴 (r416–r416) → 죽음 r442 박힘(상대 돌진), 상대 길이 4
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r400 · 드래곤 #392 L17: 끌림 16턴 (r400–r415) → 죽음 r427 갇힘
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:A:1 · r400 · 드래곤 #348 L11: 끌림 1턴 (r400–r400) → 죽음 r403 갇힘
- proxy4_king · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_king:queen_of_spades:B:1 · r453 · 드래곤 #193 L13: 끌림 1턴 (r453–r453) → 스스로 최종 왕 계보
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r405 · 드래곤 #6 L5: 끌림 27턴 (r405–r434) → 죽음 r437 갇힘
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:B:1 · r445 · 드래곤 #341 L12: 끌림 12턴 (r445–r456) → 스스로 최종 왕 계보
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:A:1 · r400 · 드래곤 #248 L5: 끌림 88턴 (r400–r487) → 끝까지 생존(계보 밖)
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:B:1 · r400 · 드래곤 #13 L7: 끌림 56턴 (r400–r485) → 끝까지 생존(계보 밖)
- proxy4_swarm · Devil · 게임 exp/conv2-a-px4:proxy4_swarm:devil:A:1 · r423 · 드래곤 #449 L5: 끌림 11턴 (r423–r455) → 죽음 r489 갇힘

## 후보 아닌 아군 희생 보류 (kch, conv2; 드래곤 단위)

- 이번: 드래곤 202 (표식 턴 1348) · 뒤에 후보에게 희생(kc) 16% · 몸(자손 포함) 끝까지 76% · 드래곤 자체 끝까지 43%
- 상대별: proxy4_elim 60회 82% · proxy4_king 63회 87% · proxy4_swarm 79회 86%
- 지도별: Autarky 14회 100% · Default 2회 50% · Devil 1회 100% · Portals 119회 81% · Queen Of Spades 1회 100% · Schooltime 4회 100% · Slithery Fight 61회 90%
- 국면별: r250-349 40회 73% · r350-449 80회 84% · r450+ 82회 93%

실패 사례 (30건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r304 · 드래곤 #126 L2: 보류 1턴 (r304–r304) → 죽음 r307 갇힘
- proxy4_swarm · Default · 게임 exp/conv2-a-px4:proxy4_swarm:default:A:1 · r352 · 드래곤 #119 L3: 보류 1턴 (r352–r352) → 죽음 r359 갇힘, 상대 길이 21
- proxy4_swarm · Portals · 게임 exp/conv2-a-px4:proxy4_swarm:portals:A:1 · r356 · 드래곤 #442 L4: 보류 4턴 (r356–r364) → 죽음 r370 갇힘
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:A:1 · r406 · 드래곤 #417 L2: 보류 1턴 (r406–r406) → 죽음 r407 갇힘, 상대 길이 27
- proxy4_elim · Portals · 게임 exp/conv2-a-px4:proxy4_elim:portals:A:1 · r322 · 드래곤 #349 L2: 보류 1턴 (r322–r322) → 죽음 r379 갇힘
- proxy4_elim · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_elim:slithery_fight:B:1 · r300 · 드래곤 #384 L2: 보류 12턴 (r300–r374) → 죽음 r375 갇힘
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r462 · 드래곤 #536 L2: 보류 2턴 (r462–r465) → 죽음 r466 갇힘
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r352 · 드래곤 #478 L2: 보류 4턴 (r352–r360) → 죽음 r362 갇힘, 상대 길이 9
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r445 · 드래곤 #596 L4: 보류 7턴 (r445–r451) → 죽음 r453 갇힘, 상대 길이 11
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:A:1 · r470 · 드래곤 #615 L3: 보류 2턴 (r470–r471) → 죽음 r486 갇힘, 상대 길이 2

## 덮기 분열 (csplit, stack5)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 33% · 부모가 스스로 최장이라 믿음(k) 63% · 새끼 30라운드 안 자연 진주 ≥1 40% (500형 40% · 전멸형 41%; 기준 ≥45%) · 새끼 30라운드 생존 75% (500형 75% · 전멸형 74%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 84% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 갇힘 191, 아군 머리 19, 박힘(상대 돌진) 50, 희생 2, 돌진 12
- 비교: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 33% · 부모가 스스로 최장이라 믿음(k) 63% · 새끼 30라운드 안 자연 진주 ≥1 40% (500형 40% · 전멸형 41%; 기준 ≥45%) · 새끼 30라운드 생존 75% (500형 75% · 전멸형 74%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 84% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 갇힘 191, 아군 머리 19, 박힘(상대 돌진) 50, 희생 2, 돌진 12
- 상대별: proxy4_elim 360회 41% · proxy4_king 398회 40% · proxy4_swarm 333회 39%
- 지도별: Autarky 98회 48% · Default 131회 33% · Devil 72회 32% · Portals 79회 54% · Prisoners Dilemma 49회 47% · Queen Of Spades 96회 50% · Schooltime 161회 48% · Slithery Fight 287회 29% · Trauma 87회 37% · Trophy 31회 58%
- 국면별: r0-99 500회 43% · r100-249 591회 38%

실패 사례 (652건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r1 · 드래곤 #0 L4: 새끼 L2, 적 머리 시야 안 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:A:1 · r1 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r81 · 드래곤 #9 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r5 · 드래곤 #5 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:A:1 · r33 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_king:queen_of_spades:A:1 · r15 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:B:1 · r1 · 드래곤 #5 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trophy · 게임 exp/conv2-a-px4:proxy4_king:trophy:B:1 · r42 · 드래곤 #12 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r3 · 드래곤 #33 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0

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
- proxy4_elim · Trauma · 게임 exp/conv2-a-px4:proxy4_elim:trauma:B:1 · r223 · 드래곤 #26 L2: 샘 (36,9) 처음 거리 0 → r223 도착, 30라운드 무리 진주 7개 중 우리 5 · 상대 0
- proxy4_elim · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_elim:slithery_fight:A:1 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:B:1 · r74 · 드래곤 #11 L2: 샘 (26,15) 처음 거리 12 → r200 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2

## 위협 모형 빈틈 (tg, stack4)

- 이번: 피함(tg) 56% · 위협 칸으로 감(tgx) 5461턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 99% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 97%) · 길이별 L2-5 12189 · L6-9 132 · L10+ 190
- 비교: 피함(tg) 56% · 위협 칸으로 감(tgx) 5433턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 99% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 97%) · 길이별 L2-5 12140 · L6-9 119 · L10+ 205
- 상대별: proxy4_elim 4516회 98% · proxy4_king 4185회 98% · proxy4_swarm 3810회 98%
- 지도별: Autarky 723회 97% · Default 2359회 98% · Devil 1087회 98% · Portals 2회 100% · Prisoners Dilemma 39회 95% · Queen Of Spades 1344회 98% · Schooltime 2956회 98% · Slithery Fight 3042회 98% · Trauma 172회 95% · Trophy 787회 97%
- 국면별: r0-99 2469회 99% · r100-249 6451회 98% · r250-349 2470회 98% · r350-449 933회 98% · r450+ 188회 98%

실패 사례 (255건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r108 · 드래곤 #12 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r109 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:A:1 · r177 · 드래곤 #99 L2: 피함(tg), 적 머리 경로 4칸 · 맨해튼 4칸(길이 2) → 박힘 r178 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r207 · 드래곤 #5 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r209 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:A:1 · r480 · 드래곤 #383 L21: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r481 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_king:queen_of_spades:A:1 · r187 · 드래곤 #31 L2: 피함(tg), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r187 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r202 · 드래곤 #16 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r204 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:B:1 · r107 · 드래곤 #15 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r108 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trophy · 게임 exp/conv2-a-px4:proxy4_king:trophy:B:1 · r111 · 드래곤 #1 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r112 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r35 · 드래곤 #12 L5: 피함(tg), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r35 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Default · 게임 exp/conv2-a-px4:proxy4_swarm:default:B:1 · r275 · 드래곤 #65 L5: 위협 칸으로 감(tgx), 적 머리 경로 1칸 · 맨해튼 1칸(길이 3) → 박힘 r275 박힘(상대 돌진), 상대 길이 3

## 모이기 시작 제한 (gx, stack4; 드래곤 단위)

- 이번: 드래곤 171 (표식 턴 1116) · 끝까지 생존 58% (기준 ≥80%) · 몸(자손 포함) 끝까지 98% · 뒤에 희생 먹이기(feed)로 끝남 2
- 비교: 드래곤 68 (표식 턴 438) · 끝까지 생존 62% (기준 ≥80%) · 몸(자손 포함) 끝까지 100% · 뒤에 희생 먹이기(feed)로 끝남 6
- 상대별: proxy4_elim 48회 52% · proxy4_king 57회 61% · proxy4_swarm 66회 59%
- 지도별: Autarky 70회 27% · Devil 3회 67% · Portals 59회 68% · Queen Of Spades 5회 100% · Schooltime 9회 89% · Slithery Fight 25회 100%
- 국면별: r450+ 171회 58%

실패 사례 (72건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r480 · 드래곤 #485 L14: gx 2턴 (r480–r481) → 죽음 r484 갇힘
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r481 · 드래곤 #544 L20: gx 1턴 (r481–r481) → 죽음 r483 갇힘
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:A:1 · r490 · 드래곤 #275 L4: gx 3턴 (r490–r492) → 죽음 r494 갇힘
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:A:1 · r480 · 드래곤 #529 L14: gx 2턴 (r480–r481) → 죽음 r484 갇힘
- proxy4_swarm · Devil · 게임 exp/conv2-a-px4:proxy4_swarm:devil:A:1 · r488 · 드래곤 #468 L10: gx 4턴 (r488–r492) → 죽음 r499 갇힘, 상대 길이 13
- proxy4_swarm · Portals · 게임 exp/conv2-a-px4:proxy4_swarm:portals:A:1 · r464 · 드래곤 #563 L4: gx 2턴 (r464–r465) → 죽음 r466 희생
- proxy4_elim · Autarky · 게임 exp/conv2-a-px4:proxy4_elim:autarky:A:1 · r480 · 드래곤 #385 L14: gx 1턴 (r480–r480) → 죽음 r484 갇힘
- proxy4_elim · Portals · 게임 exp/conv2-a-px4:proxy4_elim:portals:A:1 · r479 · 드래곤 #579 L14: gx 5턴 (r479–r483) → 죽음 r486 갇힘
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r483 · 드래곤 #486 L15: gx 1턴 (r483–r483) → 죽음 r486 갇힘
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r484 · 드래곤 #487 L14: gx 2턴 (r484–r485) → 죽음 r488 갇힘

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 124개 중 우리 팀 99% (지목한 아군 81%) · 상대 1% · 지목 아군 끝까지 생존 65% (그 뒤 죽은 원인: 희생 8, 갇힘 17, 박힘(상대 돌진) 2, 돌진 1) · 지목 아군의 몸(자손 포함)이 끝까지 삶 87% · 최종 왕 52% (최종 왕이 지목 아군의 자손 67%)
- 비교: 실행 100% · 떨군 진주 263개 중 우리 팀 98% (지목한 아군 68%) · 상대 2% · 지목 아군 끝까지 생존 45% (그 뒤 죽은 원인: 희생 12, 갇힘 79, 박힘(상대 돌진) 1, 돌진 2, 아군 머리 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 82% · 최종 왕 34% (최종 왕이 지목 아군의 자손 50%)
- 상대별: proxy4_elim 30회 97% · proxy4_king 24회 100% · proxy4_swarm 25회 100%
- 지도별: Autarky 17회 100% · Default 3회 100% · Devil 1회 100% · Portals 8회 100% · Prisoners Dilemma 4회 100% · Queen Of Spades 8회 88% · Slithery Fight 23회 100% · Trauma 15회 100%
- 국면별: r250-349 31회 100% · r350-449 38회 97% · r450+ 10회 100%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_elim · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_elim:queen_of_spades:A:1 · r370 · 드래곤 #53 L4: #127(L12)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 80% · 조각 30라운드 생존 88% · 30라운드 안 1개 이상 먹음 52% (살아서 먹음 48%) · 평생 먹은 진주 평균 3.8 · 나중에 아군을 먹임 32% (conv 3, feed 5, 분열 뒤 평균 81.3라운드) · 끝까지 생존 28% · 30라운드 안 죽은 원인: 희생 1, 갇힘 1, 돌진 1
- 비교: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 87% · 조각 30라운드 생존 61% · 30라운드 안 1개 이상 먹음 65% (살아서 먹음 42%) · 평생 먹은 진주 평균 2.7 · 나중에 아군을 먹임 61% (conv 10, feed 9, 분열 뒤 평균 47.6라운드) · 끝까지 생존 6% · 30라운드 안 죽은 원인: 갇힘 4, 희생 8
- 상대별: proxy4_elim 11회 82% · proxy4_king 5회 60% · proxy4_swarm 9회 56%
- 지도별: Autarky 3회 100% · Default 2회 50% · Portals 1회 0% · Schooltime 3회 100% · Slithery Fight 11회 45% · Trauma 5회 100%
- 국면별: r250-349 7회 86% · r350-449 18회 61%

실패 사례 (8건 중 8건, 기보 확인용):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r369 · 드래곤 #151 L9: 조각 L2 → 30라운드 생존, 먹은 진주 0 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r410 · 드래곤 #533 L12: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:A:1 · r418 · 드래곤 #922 L8: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_elim:slithery_fight:B:1 · r404 · 드래곤 #36 L11: 조각 L2 → 조각 죽음 r423 돌진, 상대 길이 3, 30라운드 안 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r308 · 드래곤 #11 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r364 · 드래곤 #507 L13: 조각 L2 → 조각 죽음 r379 갇힘, 상대 길이 17, 30라운드 안 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r380 · 드래곤 #507 L11: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_elim:slithery_fight:B:1 · r420 · 드래곤 #347 L8: 조각 L2 → 30라운드 생존, 먹은 진주 0

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 2388개 (표식 턴 6056, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 0, 이미 없음 211) · 사망 진주 2177개 중 우리가 먹음 80% · 상대 19% · 아무도 안 먹음 2% · 표적으로 삼은 드래곤이 먹음 66% · 우리가 먹기까지 평균 3.4라운드 · 상대 머리가 같거나 더 가까웠던 726개: 우리 53% 대 상대 46% · 박치기 진주 370개: 우리 51% 대 상대 49% · 우리 팀 사망 진주 81% · 사망 뒤 첫 표적까지 평균 1.3라운드
- 비교: 표적 진주 2360개 (표식 턴 5857, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 0, 이미 없음 203) · 사망 진주 2157개 중 우리가 먹음 80% · 상대 19% · 아무도 안 먹음 1% · 표적으로 삼은 드래곤이 먹음 65% · 우리가 먹기까지 평균 3.7라운드 · 상대 머리가 같거나 더 가까웠던 704개: 우리 53% 대 상대 46% · 박치기 진주 378개: 우리 52% 대 상대 48% · 우리 팀 사망 진주 81% · 사망 뒤 첫 표적까지 평균 1.4라운드
- 상대별: proxy4_elim 788회 80% · proxy4_king 873회 81% · proxy4_swarm 727회 79%
- 지도별: Autarky 238회 97% · Default 194회 74% · Devil 144회 62% · Portals 579회 97% · Prisoners Dilemma 131회 83% · Queen Of Spades 169회 62% · Schooltime 198회 59% · Slithery Fight 613회 73% · Trauma 91회 81% · Trophy 31회 54%
- 국면별: r0-99 281회 71% · r100-249 819회 75% · r250-349 560회 79% · r350-449 585회 89% · r450+ 143회 88%

실패 사례 (441건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r212 · 드래곤 #92 L3: 진주 (14,16), 우리 머리 2칸 · 상대 머리 3칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 2턴
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:A:1 · r72 · 드래곤 #10 L3: 진주 (9,6), 우리 머리 3칸 · 상대 머리 3칸, 박치기 1라운드 뒤 → 상대가 먹음 (5라운드 뒤), 표식 3턴
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r371 · 드래곤 #3 L2: 진주 (21,11), 우리 머리 3칸 · 상대 머리 3칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (5라운드 뒤), 표식 4턴
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r279 · 드래곤 #278 L14: 진주 (5,10), 우리 머리 4칸 · 상대 머리 1칸, 우리 팀 사망 0라운드 뒤 → 아무도 안 먹음, 표식 2턴
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:A:1 · r433 · 드래곤 #164 L22: 진주 (14,3), 우리 머리 3칸 · 상대 머리 2칸, 우리 팀 사망 2라운드 뒤 → 상대가 먹음 (19라운드 뒤), 표식 2턴
- proxy4_king · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_king:queen_of_spades:A:1 · r57 · 드래곤 #2 L3: 진주 (8,33), 우리 머리 4칸 · 상대 머리 3칸, 박치기 1라운드 뒤 → 상대가 먹음 (6라운드 뒤), 표식 1턴
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r204 · 드래곤 #16 L2: 진주 (21,9), 우리 머리 4칸 · 상대 머리 2칸, 상대 사망 3라운드 뒤 → 상대가 먹음 (284라운드 뒤), 표식 1턴
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:B:1 · r139 · 드래곤 #60 L2: 진주 (34,1), 우리 머리 5칸 · 상대 머리 3칸, 박치기 0라운드 뒤 → 상대가 먹음 (2라운드 뒤), 표식 2턴
- proxy4_king · Trophy · 게임 exp/conv2-a-px4:proxy4_king:trophy:B:1 · r132 · 드래곤 #12 L2: 진주 (12,22), 우리 머리 6칸 · 상대 머리 1칸, 박치기 1라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r4 · 드래곤 #26 L2: 진주 (33,5), 우리 머리 5칸 · 상대 머리 10칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (26라운드 뒤), 표식 3턴

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 1165 (그중 통로 고리 세대 936, 판정에서 뺌) · 고리 밖 229: 처음 거리 평균 10.3 → 최소 5.6 · 3칸 안까지 감 35% · 희생까지 함 38% · 가는 길에 죽음 29% · 끝까지 생존 34%
- 비교: 모이기 드래곤 831 (그중 통로 고리 세대 626, 판정에서 뺌) · 고리 밖 205: 처음 거리 평균 9.6 → 최소 5.1 · 3칸 안까지 감 41% · 희생까지 함 52% · 가는 길에 죽음 24% · 끝까지 생존 24%
- 상대별: proxy4_elim 359회 72% · proxy4_king 390회 80% · proxy4_swarm 416회 76%
- 지도별: Autarky 468회 91% · Default 15회 58% · Devil 14회 44% · Portals 350회 80% · Prisoners Dilemma 168회 83% · Queen Of Spades 14회 55% · Schooltime 34회 57% · Slithery Fight 66회 69% · Trauma 36회 54%
- 국면별: r250-349 217회 81% · r350-449 763회 78% · r450+ 185회 58%

실패 사례 (97건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r340 · 드래곤 #96 L6: 왕까지 거리 5 → 최소 5 (8턴)
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:B:1 · r416 · 드래곤 #554 L5: 왕까지 거리 6 → 최소 6 (1턴), 가는 길에 죽음 r442 박힘(상대 돌진), 상대 길이 4
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:B:1 · r435 · 드래곤 #64 L4: 왕까지 거리 5 → 최소 5 (1턴)
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r340 · 드래곤 #469 L10: 왕까지 거리 10 → 최소 6 (8턴), 가는 길에 죽음 r347 갇힘, 상대 길이 14
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:B:1 · r478 · 드래곤 #395 L9: 왕까지 거리 6 → 최소 6 (4턴)
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r376 · 드래곤 #148 L5: 왕까지 거리 17 → 최소 12 (73턴)
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:B:1 · r377 · 드래곤 #139 L4: 왕까지 거리 21 → 최소 11 (28턴), 가는 길에 죽음 r418 돌진, 상대 길이 13
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r341 · 드래곤 #287 L4: 왕까지 거리 14 → 최소 12 (25턴), 가는 길에 죽음 r456 돌진, 상대 길이 15
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:A:1 · r350 · 드래곤 #380 L7: 왕까지 거리 11 → 최소 5 (22턴), 가는 길에 죽음 r371 아군 머리, 상대 길이 3
- proxy4_swarm · Default · 게임 exp/conv2-a-px4:proxy4_swarm:default:A:1 · r354 · 드래곤 #128 L4: 왕까지 거리 17 → 최소 5 (7턴), 가는 길에 죽음 r361 희생

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 381개 중 우리 팀 90% (지목한 아군 59%) · 상대 4% · 지목 아군 끝까지 생존 66% (그 뒤 죽은 원인: 희생 9, 갇힘 29, 돌진 2, 박힘(상대 돌진) 4) · 지목 아군의 몸(자손 포함)이 끝까지 삶 90% · 최종 왕 53% (최종 왕이 지목 아군의 자손 69%)
- 비교: 실행 100% · 떨군 진주 509개 중 우리 팀 88% (지목한 아군 60%) · 상대 5% · 지목 아군 끝까지 생존 68% (그 뒤 죽은 원인: 갇힘 26, 희생 17, 아군 머리 2, 돌진 1, 박힘(상대 돌진) 5) · 지목 아군의 몸(자손 포함)이 끝까지 삶 89% · 최종 왕 47% (최종 왕이 지목 아군의 자손 58%)
- 상대별: proxy4_elim 44회 89% · proxy4_king 52회 90% · proxy4_swarm 33회 94%
- 지도별: Autarky 31회 94% · Default 7회 71% · Devil 6회 100% · Portals 24회 100% · Prisoners Dilemma 25회 96% · Queen Of Spades 7회 71% · Schooltime 5회 80% · Slithery Fight 15회 80% · Trauma 9회 89%
- 국면별: r250-349 16회 94% · r350-449 85회 93% · r450+ 28회 82%

실패 사례 (12건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r340 · 드래곤 #351 L5: #96(L6)에게 희생 → 진주 3개 중 우리 1, 지목 아군 0, 상대 0
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:B:1 · r353 · 드래곤 #144 L6: #117(L10)에게 희생 → 진주 3개 중 우리 0, 지목 아군 0, 상대 3; 지목 아군 r463 희생에 사망
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:B:1 · r432 · 드래곤 #382 L11: #187(L13)에게 희생 → 진주 6개 중 우리 2, 지목 아군 2, 상대 4; 지목 아군 r446 갇힘에 사망
- proxy4_swarm · Trauma · 게임 exp/conv2-a-px4:proxy4_swarm:trauma:B:1 · r372 · 드래곤 #3 L4: #132(L6)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2; 지목 아군 r379 박힘(상대 돌진)에 사망
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:A:1 · r490 · 드래곤 #976 L3: #183(L5)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_elim · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_elim:queen_of_spades:A:1 · r375 · 드래곤 #71 L4: #127(L12)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2
- proxy4_elim · Schooltime · 게임 exp/conv2-a-px4:proxy4_elim:schooltime:A:1 · r475 · 드래곤 #26 L18: #201(L24)에게 희생 → 진주 9개 중 우리 3, 지목 아군 3, 상대 2
- proxy4_elim · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_elim:slithery_fight:A:1 · r497 · 드래곤 #568 L2: #943(L7)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r363 · 드래곤 #352 L6: #96(L13)에게 희생 → 진주 3개 중 우리 1, 지목 아군 1, 상대 0
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:B:1 · r463 · 드래곤 #117 L4: #26(L7)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0

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

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 22% · 30라운드 뒤 가족 길이 변화 7.8
- 비교: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 99% · 새끼 자체 10라운드 생존 20% · 30라운드 뒤 가족 길이 변화 8.1
- 상대별: proxy4_elim 1381회 97% · proxy4_king 1355회 97% · proxy4_swarm 1462회 99%
- 지도별: Autarky 1554회 100% · Default 33회 100% · Devil 59회 90% · Portals 932회 95% · Prisoners Dilemma 1326회 98% · Queen Of Spades 44회 100% · Schooltime 36회 97% · Slithery Fight 146회 97% · Trauma 68회 88%
- 국면별: r0-99 785회 99% · r100-249 1218회 99% · r250-349 968회 99% · r350-449 906회 94% · r450+ 321회 99%

실패 사례 (93건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r352 · 드래곤 #320 L9: 새끼 L7 → 새끼 죽음 r359 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -9
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r300 · 드래곤 #126 L5: 새끼 L3 → 새끼 죽음 r304 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:A:1 · r423 · 드래곤 #372 L12: 새끼 L10 → 새끼 죽음 r427 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -12
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:B:1 · r319 · 드래곤 #242 L5: 새끼 L3 → 새끼 죽음 r321 갇힘, 상대 길이 16, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_swarm · Devil · 게임 exp/conv2-a-px4:proxy4_swarm:devil:A:1 · r92 · 드래곤 #81 L5: 새끼 L3 → 새끼 죽음 r97 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_swarm · Portals · 게임 exp/conv2-a-px4:proxy4_swarm:portals:A:1 · r283 · 드래곤 #370 L8: 새끼 L6 → 새끼 죽음 r284 아군 머리, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -8
- proxy4_swarm · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_swarm:prisoners_dilemma:B:1 · r417 · 드래곤 #389 L12: 새끼 L10 → 새끼 죽음 r421 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -12
- proxy4_swarm · Schooltime · 게임 exp/conv2-a-px4:proxy4_swarm:schooltime:A:1 · r392 · 드래곤 #363 L7: 새끼 L5 → 새끼 죽음 r402 적 몸통, 상대 길이 17, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7
- proxy4_swarm · Trauma · 게임 exp/conv2-a-px4:proxy4_swarm:trauma:B:1 · r350 · 드래곤 #212 L7: 새끼 L5 → 새끼 죽음 r350 갇힘, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r246 · 드래곤 #13 L4: 새끼 L2 → 새끼 죽음 r246 갇힘, 상대 길이 4, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 86% · 그 밖(진짜로 갇힘) 615회
- 비교: 탈출 분열 뒤 남은 조각(고리의 일부) 88% · 그 밖(진짜로 갇힘) 537회
- 상대별: proxy4_elim 1437회 – · proxy4_king 1429회 – · proxy4_swarm 1489회 –
- 지도별: Autarky 1572회 – · Default 57회 – · Devil 54회 – · Portals 847회 – · Prisoners Dilemma 1346회 – · Queen Of Spades 57회 – · Schooltime 54회 – · Slithery Fight 256회 – · Trauma 106회 – · Trophy 6회 –
- 국면별: r0-99 816회 – · r100-249 1405회 – · r250-349 963회 – · r350-449 876회 – · r450+ 295회 –

## 정책 분열 (split)

- 이번: 분열 100% · 새끼 30라운드 생존 43% · 30라운드 뒤 가족 길이 변화 -5.3
- 비교: 분열 100% · 새끼 30라운드 생존 20% · 30라운드 뒤 가족 길이 변화 -6.4
- 상대별: proxy4_elim 6회 33% · proxy4_king 1회 100%
- 지도별: Default 4회 0% · Prisoners Dilemma 2회 100% · Queen Of Spades 1회 100%
- 국면별: r350-449 7회 43%

실패 사례 (4건 중 4건, 기보 확인용):
- proxy4_elim · Default · 게임 exp/conv2-a-px4:proxy4_elim:default:A:1 · r408 · 드래곤 #9 L17: 새끼 L2 → 새끼 죽음 r410 갇힘, 30라운드 뒤 가족 길이 변화 1
- proxy4_elim · Default · 게임 exp/conv2-a-px4:proxy4_elim:default:A:1 · r428 · 드래곤 #9 L19: 새끼 L2 → 새끼 죽음 r431 갇힘, 상대 길이 17, 30라운드 뒤 가족 길이 변화 -1
- proxy4_elim · Default · 게임 exp/conv2-a-px4:proxy4_elim:default:A:1 · r435 · 드래곤 #9 L19: 새끼 L2 → 새끼 죽음 r435 돌진, 상대 길이 18, 30라운드 뒤 가족 길이 변화 -19
- proxy4_elim · Default · 게임 exp/conv2-a-px4:proxy4_elim:default:A:1 · r446 · 드래곤 #9 L18: 새끼 L2 → 새끼 죽음 r452 갇힘, 상대 길이 17, 30라운드 뒤 가족 길이 변화 -18

## 탈출 질주 3칸 (esc)

- 이번: 질주 99% · 짧은 적 머리 4칸 안 69% · 몸 생존 5라운드 99% · 10라운드 99% (드래곤 자체 93%) · 10라운드 길이 변화 -3.4
- 비교: 질주 99% · 짧은 적 머리 4칸 안 69% · 몸 생존 5라운드 96% · 10라운드 96% (드래곤 자체 92%) · 10라운드 길이 변화 -3.4
- 상대별: proxy4_elim 28회 96% · proxy4_king 29회 100% · proxy4_swarm 15회 93%
- 지도별: Default 6회 100% · Devil 5회 100% · Prisoners Dilemma 3회 100% · Queen Of Spades 10회 100% · Schooltime 18회 100% · Slithery Fight 27회 93% · Trauma 3회 100%
- 국면별: r0-99 1회 100% · r100-249 14회 86% · r250-349 8회 100% · r350-449 27회 100% · r450+ 22회 100%

실패 사례 (2건 중 2건, 기보 확인용):
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r228 · 드래곤 #16 L23: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r228 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_elim:slithery_fight:A:1 · r219 · 드래곤 #569 L8: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r220 박힘(상대 돌진), 상대 길이 3

## 위협 피하기 2칸 질주

- 이번: 질주 99% · 몸 10라운드 생존 95% (드래곤 자체 90%)
- 비교: 질주 99% · 몸 10라운드 생존 94% (드래곤 자체 90%)
- 상대별: proxy4_elim 224회 92% · proxy4_king 223회 95% · proxy4_swarm 230회 95%
- 지도별: Autarky 36회 100% · Default 85회 93% · Devil 53회 94% · Prisoners Dilemma 5회 100% · Queen Of Spades 101회 96% · Schooltime 179회 92% · Slithery Fight 173회 94% · Trauma 15회 100% · Trophy 30회 93%
- 국면별: r0-99 151회 97% · r100-249 253회 92% · r250-349 146회 94% · r350-449 111회 96% · r450+ 16회 88%

실패 사례 (40건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r197 · 드래곤 #0 L2: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 2) → 죽음 r197 질주 불가
- proxy4_king · Devil · 게임 exp/conv2-a-px4:proxy4_king:devil:B:1 · r94 · 드래곤 #23 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r102 돌진, 상대 길이 2
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:B:1 · r156 · 드래곤 #73 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r160 박힘(상대 돌진), 상대 길이 4
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r123 · 드래곤 #182 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r132 갇힘, 상대 길이 4
- proxy4_swarm · Default · 게임 exp/conv2-a-px4:proxy4_swarm:default:B:1 · r233 · 드래곤 #87 L3: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 5) → 죽음 r235 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_swarm:queen_of_spades:A:1 · r350 · 드래곤 #49 L5: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 3) → 죽음 r351 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Schooltime · 게임 exp/conv2-a-px4:proxy4_swarm:schooltime:A:1 · r222 · 드래곤 #119 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r226 돌진, 상대 길이 26
- proxy4_swarm · Trophy · 게임 exp/conv2-a-px4:proxy4_swarm:trophy:A:1 · r107 · 드래곤 #0 L9: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r111 박힘(상대 돌진), 상대 길이 4
- proxy4_elim · Default · 게임 exp/conv2-a-px4:proxy4_elim:default:A:1 · r1 · 드래곤 #6 L4: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r7 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:B:1 · r224 · 드래곤 #266 L4: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 3) → 죽음 r225 돌진, 상대 길이 8

## 포털 통과 (전체; PORTAL?=미탐색 출구)

- 이번: 미탐색 출구 1128회(몸 3라운드 생존 93%) · 전체 몸 생존 3라운드 94% (드래곤 자체 78%) · 10라운드 89% · 10라운드 안 먹은 진주 0.9
- 비교: 미탐색 출구 1005회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 94% (드래곤 자체 79%) · 10라운드 89% · 10라운드 안 먹은 진주 0.9
- 상대별: proxy4_elim 736회 93% · proxy4_king 1074회 94% · proxy4_swarm 832회 94%
- 지도별: Autarky 391회 95% · Default 529회 96% · Portals 1106회 92% · Prisoners Dilemma 68회 97% · Queen Of Spades 79회 87% · Schooltime 127회 91% · Slithery Fight 184회 95% · Trauma 157회 96% · Trophy 1회 100%
- 국면별: r0-99 285회 95% · r100-249 975회 95% · r250-349 792회 93% · r350-449 498회 92% · r450+ 92회 93%

실패 사례 (166건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/conv2-a-px4:proxy4_king:default:A:1 · r185 · 드래곤 #35 L3: 포털 → 죽음 r185 갇힘, 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Autarky · 게임 exp/conv2-a-px4:proxy4_king:autarky:B:1 · r285 · 드래곤 #209 L3: 포털 → 죽음 r286 갇힘, 10라운드 안 진주 0
- proxy4_king · Portals · 게임 exp/conv2-a-px4:proxy4_king:portals:B:1 · r8 · 드래곤 #1 L3: 포털(미탐색 출구) → 죽음 r9 갇힘, 10라운드 안 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/conv2-a-px4:proxy4_king:prisoners_dilemma:A:1 · r267 · 드래곤 #151 L3: 포털(미탐색 출구) → 죽음 r267 아군 머리, 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_king:queen_of_spades:A:1 · r50 · 드래곤 #12 L2: 포털 → 죽음 r53 갇힘, 10라운드 안 진주 0
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r274 · 드래곤 #50 L3: 포털 → 죽음 r276 박힘(상대 돌진), 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:B:1 · r219 · 드래곤 #42 L2: 포털(미탐색 출구) → 죽음 r219 박힘(상대 돌진), 상대 길이 3, 10라운드 안 진주 0
- proxy4_swarm · Default · 게임 exp/conv2-a-px4:proxy4_swarm:default:B:1 · r205 · 드래곤 #57 L2: 포털 → 죽음 r208 갇힘, 10라운드 안 진주 0
- proxy4_swarm · Autarky · 게임 exp/conv2-a-px4:proxy4_swarm:autarky:A:1 · r264 · 드래곤 #253 L2: 포털 → 죽음 r265 갇힘, 10라운드 안 진주 0
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:B:1 · r183 · 드래곤 #384 L3: 포털(미탐색 출구) → 죽음 r183 아군 머리, 상대 길이 6, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 20, 경로 27) · 잡은 길이 ≥ 우리 100% · 두 몸의 진주 우리 44 대 상대 277
- 비교: 충돌 성사 100% (인접 18, 경로 33) · 잡은 길이 ≥ 우리 98% · 두 몸의 진주 우리 121 대 상대 271
- 상대별: proxy4_elim 10회 10% · proxy4_king 10회 10% · proxy4_swarm 27회 11%
- 지도별: Default 2회 0% · Devil 3회 33% · Queen Of Spades 5회 0% · Schooltime 19회 5% · Slithery Fight 16회 19% · Trauma 2회 0%
- 국면별: r0-99 1회 0% · r100-249 12회 17% · r250-349 15회 0% · r350-449 16회 6% · r450+ 3회 67%

실패 사례 (42건 중 10건, 기보 확인용):
- proxy4_king · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_king:queen_of_spades:A:1 · r378 · 드래곤 #28 L4: 돌진 경로 3칸 → 상대 L11 잡음, 진주 우리 0 대 상대 8
- proxy4_king · Trauma · 게임 exp/conv2-a-px4:proxy4_king:trauma:A:1 · r297 · 드래곤 #116 L4: 돌진 경로 3칸 → 상대 L6 잡음, 진주 우리 0 대 상대 5
- proxy4_king · Schooltime · 게임 exp/conv2-a-px4:proxy4_king:schooltime:A:1 · r192 · 드래곤 #102 L5: 돌진 경로 3칸 → 상대 L13 잡음, 진주 우리 0 대 상대 10
- proxy4_king · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_king:slithery_fight:A:1 · r272 · 드래곤 #307 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_swarm · Default · 게임 exp/conv2-a-px4:proxy4_swarm:default:A:1 · r128 · 드래곤 #37 L2: 돌진 경로 1칸 → 상대 L3 잡음, 진주 우리 0 대 상대 3
- proxy4_swarm · Devil · 게임 exp/conv2-a-px4:proxy4_swarm:devil:A:1 · r358 · 드래곤 #9 L4: 돌진 경로 2칸 → 상대 L14 잡음, 진주 우리 2 대 상대 7
- proxy4_swarm · Queen Of Spades · 게임 exp/conv2-a-px4:proxy4_swarm:queen_of_spades:B:1 · r280 · 드래곤 #57 L3: 돌진 경로 2칸 → 상대 L5 잡음, 진주 우리 0 대 상대 5
- proxy4_swarm · Trauma · 게임 exp/conv2-a-px4:proxy4_swarm:trauma:A:1 · r405 · 드래곤 #217 L3: 돌진 경로 2칸 → 상대 L6 잡음, 진주 우리 1 대 상대 4
- proxy4_swarm · Schooltime · 게임 exp/conv2-a-px4:proxy4_swarm:schooltime:A:1 · r176 · 드래곤 #108 L3: 돌진 경로 2칸 → 상대 L5 잡음, 진주 우리 1 대 상대 4
- proxy4_swarm · Slithery Fight · 게임 exp/conv2-a-px4:proxy4_swarm:slithery_fight:A:1 · r279 · 드래곤 #30 L3: 돌진 경로 1칸 → 상대 L6 잡음, 진주 우리 0 대 상대 5

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 비교: 먹음 100%
- 상대별: proxy4_elim 60회 100% · proxy4_king 72회 100% · proxy4_swarm 41회 100%
- 지도별: Autarky 9회 100% · Default 16회 100% · Devil 9회 100% · Portals 23회 100% · Prisoners Dilemma 1회 100% · Queen Of Spades 16회 100% · Schooltime 35회 100% · Slithery Fight 49회 100% · Trauma 4회 100% · Trophy 11회 100%
- 국면별: r0-99 33회 100% · r100-249 60회 100% · r250-349 29회 100% · r350-449 39회 100% · r450+ 12회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 86%
- 비교: 그 턴 사망 0% · 10라운드 생존 87%
- 상대별: proxy4_elim 33회 – · proxy4_king 22회 – · proxy4_swarm 24회 –
- 지도별: Autarky 1회 – · Default 5회 – · Devil 5회 – · Queen Of Spades 17회 – · Schooltime 23회 – · Slithery Fight 25회 – · Trauma 2회 – · Trophy 1회 –
- 국면별: r0-99 13회 – · r100-249 31회 – · r250-349 16회 – · r350-449 17회 – · r450+ 2회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 비교: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 5회 – · proxy4_king 15회 – · proxy4_swarm 11회 –
- 지도별: Default 1회 – · Devil 8회 – · Queen Of Spades 4회 – · Schooltime 4회 – · Slithery Fight 12회 – · Trauma 2회 –
- 국면별: r0-99 4회 – · r100-249 21회 – · r250-349 3회 – · r350-449 3회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/conv2-a-px4` | 60 | 29 (0.48) | 52% | 0 (0.00) | 0 (0.00) | 9 | 20 | 0 | 2/6 (7) | 93 (1.55; 필사 24) | 31/66 (108.5) |
| 비교 `exp/stack5-a-px4` | 60 | 29 (0.48) | 38% | 0 (0.00) | 0 (0.00) | 10 | 18 | 0 | 3/6 (10.5) | 81 (1.35; 필사 20) | 14/50 (49) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.
- 이번 `exp/conv2-a-px4`: gx 표식 턴 1116 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- 비교 `exp/stack5-a-px4`: gx 표식 턴 438 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/conv2-a-px4` | 60 | 40986 | 0.8% (318) | 14.5% (5937) | 4454 | 1.8% (81) | 5.3% (238) | 23.2% (1035/4454) |
| 비교 `exp/stack5-a-px4` | 60 | 41158 | 0.7% (283) | 14.3% (5873) | 4498 | 1.1% (50) | 3.6% (161) | 22.9% (1028/4498) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/conv2-a-px4` | 전체 | 분열 | 7 (17%) | 16 | 130% | 146% | 3 | 0 |
| 이번 `exp/conv2-a-px4` | 전체 | 2칸 질주 | 9 (22%) | 17.7 | 90% | 58% | 4 | 0 |
| 이번 `exp/conv2-a-px4` | 전체 | 3칸 질주 | 7 (17%) | 14 | 88% | 95% | 1 | 0 |
| 이번 `exp/conv2-a-px4` | 전체 | 한 걸음 | 18 (44%) | 11.7 | 39% | 41% | 12 | 9 |
| 이번 `exp/conv2-a-px4` | 4칸 이상 | 분열 | 7 (29%) | 16 | 130% | 146% | 3 | 0 |
| 이번 `exp/conv2-a-px4` | 4칸 이상 | 2칸 질주 | 7 (29%) | 17.7 | 88% | 55% | 3 | 0 |
| 이번 `exp/conv2-a-px4` | 4칸 이상 | 3칸 질주 | 5 (21%) | 12.4 | 92% | 103% | 1 | 0 |
| 이번 `exp/conv2-a-px4` | 4칸 이상 | 한 걸음 | 5 (21%) | 14.4 | 42% | 38% | 4 | 3 |
| 비교 `exp/stack5-a-px4` | 전체 | 분열 | 9 (20%) | 13 | 145% | 167% | 6 | 0 |
| 비교 `exp/stack5-a-px4` | 전체 | 2칸 질주 | 11 (25%) | 17.1 | 91% | 69% | 4 | 0 |
| 비교 `exp/stack5-a-px4` | 전체 | 3칸 질주 | 7 (16%) | 18.4 | 91% | 93% | 1 | 0 |
| 비교 `exp/stack5-a-px4` | 전체 | 한 걸음 | 17 (39%) | 11.2 | 43% | 51% | 12 | 9 |
| 비교 `exp/stack5-a-px4` | 4칸 이상 | 분열 | 9 (30%) | 13 | 145% | 167% | 6 | 0 |
| 비교 `exp/stack5-a-px4` | 4칸 이상 | 2칸 질주 | 9 (30%) | 17 | 90% | 69% | 3 | 0 |
| 비교 `exp/stack5-a-px4` | 4칸 이상 | 3칸 질주 | 5 (17%) | 18.6 | 96% | 98% | 1 | 0 |
| 비교 `exp/stack5-a-px4` | 4칸 이상 | 한 걸음 | 7 (23%) | 11.7 | 45% | 55% | 6 | 4 |

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (93건 중 10건):
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
| 우리 영토 자연 진주(r0부터 생성)를 상대가 먹은 몫(합산) | ≤25% | 11% / 16% | 56% / 55% | 55% / 58% | 56% / 57% |
| 우리 영토 샘 진주를 상대가 먹은 몫(합산) | ≤15% | 7% / 6% | 50% / 33% | 48% / 43% | 49% / 41% |

- 판 수(500라운드형 / 전멸형): 이번 30 / 30 · 비교 30 / 30. 판본 파일을 못 찾은 판: 이번 0 · 비교 0.

### 부작용: 우리 드래곤의 죽음 (판당; 전체 / r250 전)

| 원인 | 이번 | 비교 |
|---|---|---|
| 갇힘(빈 이웃 없음; 통로 고리의 남은 조각 포함) | 73.5 / 37.3 | 72.6 / 37.3 |
| 적 머리에 박힘 | 7.8 / 5.6 | 7.9 / 5.6 |
| 우리 드래곤끼리 머리 충돌(둘 다 죽음, 둘 다 셈) | 2.1 / 0.9 | 1.8 / 0.9 |

- 막힘에서 아군 머리를 피해 죽은 턴(no-exit s): 이번 109 · 비교 108

### 지도별 (이번)

| 지도 | 판 | csplit 판당 | 새끼 먹음 ≥1 | 새끼 30R 생존 | F 목표 · 도착 · 무리 진주 우리 몫 | r100 드래곤 | 보로노이 | 샘 지킴 | 상대가 먹은 영토 진주 | 상대가 먹은 샘 진주 |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| Autarky | 6 | 16.3 | 48% | 85% | 361 · 92% · 100% | 9.7 | 96% | 86% | 9% | 8% |
| Default | 6 | 21.8 | 33% | 65% | 0 · – · – | 10.8 | 38% | – | 69% | – |
| Devil | 6 | 12 | 32% | 74% | 149 · 13% · 78% | 8.7 | 29% | 24% | 81% | 83% |
| Portals | 6 | 13.2 | 54% | 56% | 654 · 39% · 99% | 11.3 | 100% | 36% | 0% | 0% |
| Prisoners Dilemma | 6 | 8.2 | 47% | 94% | 1044 · 88% · 100% | 3.7 | 99% | 100% | 5% | 3% |
| Queen Of Spades | 6 | 16 | 50% | 74% | 19 · 26% · – | 3.7 | 25% | – | 72% | – |
| Schooltime | 6 | 26.8 | 48% | 86% | 11 · 0% · – | 16.2 | 26% | 0% | 82% | 61% |
| Slithery Fight | 6 | 47.8 | 29% | 75% | 485 · 21% · 47% | 23.2 | 28% | 7% | 76% | 82% |
| Trauma | 6 | 14.5 | 37% | 64% | 72 · 22% · 90% | 5 | 93% | 0% | 57% | 2% |
| Trophy | 6 | 5.2 | 58% | 81% | 12 · 42% · – | 4.3 | 9% | – | 78% | – |

## cand-conv2: 희생 질량이 최종 왕 계보로 가는가 (kc · k2) 게이트와 가설 수준 지표

- 기준값은 `research/experiments/cand-conv2.md`(온라인 전)에서, 상위권·우리 봇 값은 `research/observations/conversion-chain.md`에서 왔다. 최종 왕 계보 = 끝의 최장 드래곤을 부모 쪽으로 따라간 드래곤들이고, 계보 드래곤 i는 태어난 라운드부터 계보 드래곤 i+1이 태어난 라운드 전까지를 맡는다. "계보 몫" = 떨어진 진주 가운데 그 창 안의 계보 드래곤이 먹은 비율.

| 항목 | 이번 | 비교 |
|---|---|---|
| conv (kc 표식) | 79건 · 진주 124 → 계보 54% · 상대 1% · 지목이 그 순간 계보 62% · 지목이 그 순간 팀 최장 56% | 0건 · 진주 0 → 계보 – · 상대 – · 지목이 그 순간 계보 – · 지목이 그 순간 팀 최장 – |
| conv (kc 없음) | 0건 · 진주 0 → 계보 – · 상대 – · 지목이 그 순간 계보 – · 지목이 그 순간 팀 최장 – | 173건 · 진주 263 → 계보 37% · 상대 2% · 지목이 그 순간 계보 50% · 지목이 그 순간 팀 최장 43% |
| feed (kc 표식) | 129건 · 진주 381 → 계보 48% · 상대 4% · 지목이 그 순간 계보 66% · 지목이 그 순간 팀 최장 42% | 0건 · 진주 0 → 계보 – · 상대 – · 지목이 그 순간 계보 – · 지목이 그 순간 팀 최장 – |
| feed (kc 없음) | 0건 · 진주 0 → 계보 – · 상대 – · 지목이 그 순간 계보 – · 지목이 그 순간 팀 최장 – | 161건 · 진주 509 → 계보 46% · 상대 5% · 지목이 그 순간 계보 55% · 지목이 그 순간 팀 최장 39% |
| k2 | 10건 · 진주 44 → 계보 23% · 상대 52% · 지목이 그 순간 계보 70% · 지목이 그 순간 팀 최장 90% | 0건 · 진주 0 → 계보 – · 상대 – · 지목이 그 순간 계보 – · 지목이 그 순간 팀 최장 – |
| 500라운드형(500까지 간 판) 판 | 30 | 30 |
| k2 발동(판당, 500형 끝까지 간 판) | 4 (0.1) | 0 (0) |
| r300 뒤 우리 희생 진주의 계보 몫 (상위권 승자 21%) | 52% (197/380) | 41% (246/593) |
| r350 뒤 계보가 먹은 우리 희생 진주(판당; 상위권 승자 19.7, merge2 3.8) | 5.7 | 6.5 |
| r400 계보 밖 길이 ≥8 드래곤(판당) · 가족이 계보 밖에서 끝까지 삶 · 계보에 진주를 줌 | 1.3 · 82% (끝 길이 12.5) · 31% | 1.6 · 69% (끝 길이 16.8) · 42% |
| 끝 왕 길이(500형 끝까지 간 판, 판정에 쓰지 않음) | 24 | 26.7 |

