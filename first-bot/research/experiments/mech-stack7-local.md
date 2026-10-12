# 구현 적용 확인

- 대상: `exp/stack7-a-px4` 60판 · 비교: `exp/stack5-a-px4` 60판
- 기준(사용자 규칙 2026-09-30): 승률이 아니라, 봇에 구현한 기능이 이 상대들에게 실제로 발동하고 의도대로 작동했는지를 본다.
- "의도대로"의 정의: 모이기=왕 3칸 안까지 가거나 희생까지 함 · 희생=떨군 진주 절반 이상을 우리 팀이 먹고 상대는 못 먹음 · 한입=2턴 안 분열하고 30라운드 뒤 가족 길이가 줄지 않음 · 탈출 분열=10라운드 뒤 몸이 살아 있음 · 정책 분열=새끼 30라운드 생존 · 탈출 질주·위협 피하기=10라운드 뒤 몸 생존 · 포털=3라운드 뒤 몸 생존 · 돌진=충돌 성사, 잡은 길이 ≥ 우리, 두 몸의 진주를 우리가 더 먹음 · 먹이 질주=진주 먹음.
- "몸"은 그 드래곤과 그 뒤 분열로 태어난 자손 전체다. 통로 고리처럼 몸을 새끼에게 넘기며 버티는 경우를 손실로 세지 않기 위해서다.
- stack2의 "의도대로": 조각 떼기=조각이 30라운드 살며 진주를 1개 이상 먹거나, 나중에 희생(feed·conv)으로 아군을 먹임 · 새 사망 진주 줍기=표적이 된 사망 진주(진주 하나가 한 건)를 우리 팀이 먹음(자연 진주로 오인했거나 이미 없던 표적은 판정에서 뺌).
- stack4의 "의도대로": tg=표식 턴 뒤 2라운드 안에 박히지 않음 · 몰렸을 때 분열=10라운드 뒤 몸이 살아 있음(보존율은 효과 줄) · px=그 턴에 우리 드래곤과 부딪혀 죽지 않음 · gx=그 드래곤의 몸(그 드래곤과 뒤에 태어난 자손)이 끝까지 삶(사용자 결정 17:16: 생존은 몸으로 판정, 드래곤 자체 생존은 참고).
- cand-mapid의 "의도대로": Schooltime b 초반 분열(bsp)=떼어 낸 조각(새 유닛)이 10라운드 뒤 살아 있음 · 지도·판본 인식=그 판에서 1개 이상의 프로세스가 판본까지 결정했고, 결정한 프로세스(마지막 표식 기준)가 모두 정답 지도·판본을 댐. 정답 판본은 로컬이면 지도 파일 이름, 온라인이면 기보의 자연 생성(한쪽 판본에서만 생성하는 칸)으로 정하고, 끝까지 가릴 수 없던 판은 뺀다. 지도별 줄의 이름 뒤 a·b·?가 정답 판본이다.
- stack5의 "의도대로": 덮기 분열=새끼가 30라운드 안에 자연 진주를 1개 이상 먹음(생존은 효과 줄) · 샘 지킴=목표 샘 3걸음 안에 든 뒤 30라운드 동안 그 무리(실제 샘, 목표에서 3걸음 안)에 생긴 자연 진주의 85% 이상을 우리가 먹음(도착하지 않았거나 진주가 생기지 않은 목표는 뺌) · 영토 덮기 끌림=20라운드 안에 우리 영토 자연 진주를 먹음. 게이트와 가설 수준 지표는 맨 뒤 stack5 절.
- stack7의 "의도대로": 수 바닥 분열(floor)=새끼가 30라운드 뒤 살아 있음 · 왕 길이 상한 분열(kcap)=새끼가 10라운드 뒤 살아 있음(부모 생존은 효과 줄). 판이 먼저 끝나면 생존으로 센다. 게이트, 저수 에피소드, 지도 가르기는 맨 뒤 stack7 절.

## 요약

| 기능 | 발동(판당) | 의도대로 | 비교: 발동(판당) | 비교: 의도대로 |
|---|---:|---:|---:|---:|
| 수 바닥 분열 (split floor, stack7) | 49 (0.8) | 61% | 0 (0) | – |
| 왕 길이 상한 분열 (split kcap, stack7) | 8 (0.1) | 50% | 0 (0) | – |
| 지도·판본 인식 (map=, cand-mapid; 판 단위) | 60 (1) | 100% | 0 (0) | – |
| 덮기 분열 (csplit, stack5) | 1101 (18.4) | 40% | 1091 (18.2) | 40% |
| 샘 지킴 (F, stack5; 드래곤·샘 단위) | 2812 (46.9) | 96% | 2819 (47) | 96% |
| 위협 모형 빈틈 (tg, stack4) | 12497 (208.3) | 98% | 12464 (207.7) | 98% |
| 모이기 시작 제한 (gx, stack4; 드래곤 단위) | 60 (1) | 100% | 68 (1.1) | 100% |
| 큰 아군 곁 희생 (conv, stack1 M1) | 177 (3) | 98% | 173 (2.9) | 97% |
| 조각 떼기 (split frag, stack2 S1) | 24 (0.4) | 83% | 31 (0.5) | 84% |
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 2435 (40.6) | 81% | 2360 (39.3) | 80% |
| 왕에게 모이기 (g, 드래곤 단위) | 839 (14) | 85% | 831 (13.9) | 83% |
| 희생 먹이기 (feed) | 166 (2.8) | 90% | 161 (2.7) | 90% |
| 막다른 길 한입 (pocket-eat) | 8 (0.1) | 50% | 8 (0.1) | 50% |
| 탈출 분열 (escape-split) | 4193 (69.9) | 98% | 4185 (69.8) | 99% |
| 출구 없음 (no-exit) | 4347 (72.5) | – | 4311 (71.9) | – |
| 정책 분열 (split) | 2 (0) | 50% | 5 (0.1) | 20% |
| 탈출 질주 3칸 (esc) | 67 (1.1) | 96% | 72 (1.2) | 94% |
| 위협 피하기 2칸 질주 | 632 (10.5) | 93% | 669 (11.2) | 94% |
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 2489 (41.5) | 94% | 2463 (41.1) | 94% |
| 돌진 (TRADE) | 51 (0.9) | 31% | 51 (0.9) | 27% |
| 먹이 질주 (2칸 이상, 먹은 것) | 179 (3) | 100% | 174 (2.9) | 100% |
| 기타 2칸 질주 | 87 (1.5) | – | 86 (1.4) | – |
| 마지막 돌진 (last-trade) | 31 (0.5) | – | 32 (0.5) | – |

- 건강: 턴 223787, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 비교 건강: 턴 222732, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 9531턴 · 끝판(late) 4648턴 · 돌진 신뢰(T, 탈출 끔) 3턴, 그 직후 박혀 죽음 0

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 비교 |
|---|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 1% (41/2753턴) | 2% (45/2686턴) |
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 36.3칸 (9회), 진주 우리 95% · 상대 1% | 36칸 (8.8회), 진주 우리 94% · 상대 1% |
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 0.3칸 (판당 0.03회) | 0.3칸 (판당 0.03회) |
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 23% (1046/4455턴) | 23% (1028/4498턴) |
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.083회 (5건, 68칸) | 판당 0.100회 (6건, 76칸) |
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 6마리 (30판) | 6.1마리 (30판) |
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 19.4회 | 19.4회 |
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 56% (우리 38%) | 56% (우리 37%) |
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 9.1 대 상대 29.3 (10.2회) · 박힌 교환의 우리 몫 21% (243회) | 우리 8.2 대 상대 28.4 (10회) · 박힌 교환의 우리 몫 19% (236회) |
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 9.9개 | 9.2개 |

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 수 바닥 분열 (split floor, stack7)

- 이번: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 90% · 적 머리가 7×7 시야 안 37% · 부모 길이 평균 5.5 · 우리 수(표식) 평균 2.7 · 상대 수 평균 28.7 · 새끼 10라운드 생존 82% · 30라운드 61% · 부모 10라운드 생존 84% · 30라운드 63% · 새끼 30라운드 안 1개 이상 먹음 57% · 30라운드 뒤 가족 길이 변화 1.6 · 30라운드 안 새끼가 죽은 원인: 갇힘 8, 돌진 3, 박힘(상대 돌진) 3, 희생 5
- 상대별: proxy4_elim 16회 63% · proxy4_king 15회 67% · proxy4_swarm 18회 56%
- 지도별: Default 12회 58% · Devil 8회 50% · Queen Of Spades 10회 60% · Schooltime 12회 67% · Slithery Fight 2회 100% · Trauma 5회 60%
- 국면별: r0-99 3회 33% · r100-249 4회 75% · r250-349 18회 56% · r350-449 24회 67%

실패 사례 (19건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack7-a-px4:proxy4_king:devil:B:1 · r388 · 드래곤 #543 L4: 우리 3마리 · 상대 15마리 · 새끼 L2 → 새끼 죽음 r391 갇힘, 상대 길이 13, 부모 10라운드 생존 · 표식 map=Devil/a
- proxy4_king · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_king:queen_of_spades:A:1 · r67 · 드래곤 #2 L4: 우리 3마리 · 상대 7마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r69 돌진, 상대 길이 2, 부모 10라운드 생존 (설계 밖: 상대 < 8마리) · 표식 map=Queen_Of_Spades/a
- proxy4_king · Schooltime · 게임 exp/stack7-a-px4:proxy4_king:schooltime:A:1 · r325 · 드래곤 #220 L9: 우리 3마리 · 상대 64마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r328 갇힘, 부모 10라운드 죽음 · 표식 map=Schooltime/a
- proxy4_swarm · Default · 게임 exp/stack7-a-px4:proxy4_swarm:default:B:1 · r299 · 드래곤 #14 L4: 우리 3마리 · 상대 35마리 · 새끼 L2 → 새끼 죽음 r310 갇힘, 상대 길이 4, 부모 10라운드 생존 · 표식 map=Default/a
- proxy4_swarm · Devil · 게임 exp/stack7-a-px4:proxy4_swarm:devil:B:1 · r446 · 드래곤 #527 L5: 우리 3마리 · 상대 13마리 · 새끼 L2 → 새끼 죽음 r454 희생, 부모 10라운드 생존 · 표식 map=Devil/a
- proxy4_swarm · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_swarm:queen_of_spades:A:1 · r43 · 드래곤 #10 L5: 우리 3마리 · 상대 5마리 · 새끼 L2 → 새끼 죽음 r44 갇힘, 부모 10라운드 죽음 (설계 밖: 상대 < 8마리) · 표식 map=Queen_Of_Spades/a
- proxy4_swarm · Trauma · 게임 exp/stack7-a-px4:proxy4_swarm:trauma:A:1 · r425 · 드래곤 #5 L4: 우리 3마리 · 상대 8마리 · 새끼 L2 → 새끼 죽음 r437 갇힘, 부모 10라운드 생존 · 표식 map=Trauma/a
- proxy4_elim · Default · 게임 exp/stack7-a-px4:proxy4_elim:default:A:1 · r269 · 드래곤 #103 L5: 우리 3마리 · 상대 34마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r281 박힘(상대 돌진), 상대 길이 2, 부모 10라운드 생존 · 표식 map=Default/a
- proxy4_elim · Devil · 게임 exp/stack7-a-px4:proxy4_elim:devil:A:1 · r441 · 드래곤 #435 L4: 우리 3마리 · 상대 5마리 · 새끼 L2 → 새끼 죽음 r464 희생, 부모 10라운드 생존 (설계 밖: 상대 < 8마리) · 표식 map=Devil/a
- proxy4_elim · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_elim:queen_of_spades:B:1 · r439 · 드래곤 #114 L4: 우리 3마리 · 상대 5마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r466 희생, 부모 10라운드 생존 (설계 밖: 상대 < 8마리) · 표식 map=Queen_Of_Spades/a

## 왕 길이 상한 분열 (split kcap, stack7)

- 이번: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 63% · 부모 길이 평균 8 · 우리 수(표식) 평균 4.1 · 상대 수 평균 12.3 · 새끼 10라운드 생존 50% · 30라운드 38% · 부모 10라운드 생존 50% · 30라운드 25% · 새끼 30라운드 안 1개 이상 먹음 63% · 30라운드 뒤 가족 길이 변화 1.3 · 30라운드 안 새끼가 죽은 원인: 박힘(상대 돌진) 2, 아군 머리 1, 갇힘 2
- 상대별: proxy4_elim 6회 33% · proxy4_swarm 2회 100%
- 지도별: Default 2회 100% · Queen Of Spades 3회 0% · Trauma 1회 0% · Trophy 2회 100%
- 국면별: r0-99 3회 67% · r100-249 5회 40%

실패 사례 (4건 중 4건, 기보 확인용):
- proxy4_elim · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_elim:queen_of_spades:A:1 · r91 · 드래곤 #21 L8: 우리 4마리 · 상대 9마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r98 아군 머리, 상대 길이 5, 부모 10라운드 죽음 · 표식 map=Queen_Of_Spades/a
- proxy4_elim · Trauma · 게임 exp/stack7-a-px4:proxy4_elim:trauma:B:1 · r145 · 드래곤 #27 L8: 우리 5마리 · 상대 10마리 · 새끼 L2 → 새끼 죽음 r155 갇힘, 부모 10라운드 생존 · 표식 map=Trauma/a
- proxy4_elim · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_elim:queen_of_spades:A:1 · r108 · 드래곤 #35 L8: 우리 4마리 · 상대 9마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r109 박힘(상대 돌진), 상대 길이 2, 부모 10라운드 생존 · 표식 map=Queen_Of_Spades/a
- proxy4_elim · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_elim:queen_of_spades:A:1 · r120 · 드래곤 #35 L7: 우리 4마리 · 상대 11마리 · 새끼 L2 → 새끼 죽음 r121 갇힘, 부모 10라운드 죽음 · 표식 map=Queen_Of_Spades/a

## 지도·판본 인식 (map=, cand-mapid; 판 단위)

- 이번: 판본을 기보로 가릴 수 있는 판 60/60 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 94%, 그중 정답 100% · 프로세스 5587: 표식 없음 3, 결정 5570 (정답 100%, 틀림 0), 가족만 14, 모름 0, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 162라운드
- 상대별: proxy4_elim 20회 100% · proxy4_king 20회 100% · proxy4_swarm 20회 100%
- 지도별: Autarky a 6회 100% · Default a 6회 100% · Devil a 6회 100% · Portals a 6회 100% · Prisoners Dilemma a 6회 100% · Queen Of Spades a 6회 100% · Schooltime a 6회 100% · Slithery Fight a 6회 100% · Trauma a 6회 100% · Trophy a 6회 100%
- 국면별: r0-99 60회 100%

## 덮기 분열 (csplit, stack5)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 34% · 부모가 스스로 최장이라 믿음(k) 62% · 새끼 30라운드 안 자연 진주 ≥1 40% (500형 40% · 전멸형 40%; 기준 ≥45%) · 새끼 30라운드 생존 74% (500형 75% · 전멸형 72%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 86% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 갇힘 199, 아군 머리 19, 박힘(상대 돌진) 54, 희생 2, 돌진 12
- 비교: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 33% · 부모가 스스로 최장이라 믿음(k) 63% · 새끼 30라운드 안 자연 진주 ≥1 40% (500형 40% · 전멸형 41%; 기준 ≥45%) · 새끼 30라운드 생존 75% (500형 75% · 전멸형 74%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 84% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 갇힘 191, 아군 머리 19, 박힘(상대 돌진) 50, 희생 2, 돌진 12
- 상대별: proxy4_elim 382회 42% · proxy4_king 394회 41% · proxy4_swarm 325회 37%
- 지도별: Autarky 98회 48% · Default 147회 34% · Devil 72회 32% · Portals 79회 54% · Prisoners Dilemma 49회 47% · Queen Of Spades 71회 51% · Schooltime 161회 48% · Slithery Fight 287회 29% · Trauma 94회 36% · Trophy 43회 47%
- 국면별: r0-99 507회 42% · r100-249 594회 38%

실패 사례 (663건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:A:1 · r1 · 드래곤 #0 L4: 새끼 L2, 적 머리 시야 안 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Autarky · 게임 exp/stack7-a-px4:proxy4_king:autarky:B:1 · r81 · 드래곤 #9 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/stack7-a-px4:proxy4_king:devil:A:1 · r1 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/stack7-a-px4:proxy4_king:portals:A:1 · r5 · 드래곤 #4 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack7-a-px4:proxy4_king:prisoners_dilemma:A:1 · r33 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_king:queen_of_spades:A:1 · r15 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/stack7-a-px4:proxy4_king:schooltime:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/stack7-a-px4:proxy4_king:trauma:B:1 · r1 · 드래곤 #1 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_king:slithery_fight:A:1 · r3 · 드래곤 #33 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trophy · 게임 exp/stack7-a-px4:proxy4_king:trophy:B:1 · r42 · 드래곤 #12 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0

## 샘 지킴 (F, stack5; 드래곤·샘 단위)

- 이번: 목표 2812개(표식 턴 22458) · 설계 상황 79% (실제 샘 99%, 우리 영토 90%, 처음에 다른 우리 머리 3걸음 안 없음 90%; 기준 ≥80%) · 3걸음 안 도착 59% · 도착 뒤 30라운드 그 무리 자연 진주 11718개 중 우리 98% · 상대 2% (합산 기준 ≥85%) · 처음 거리 평균 4.8
- 비교: 목표 2819개(표식 턴 22512) · 설계 상황 79% (실제 샘 98%, 우리 영토 90%, 처음에 다른 우리 머리 3걸음 안 없음 90%; 기준 ≥80%) · 3걸음 안 도착 59% · 도착 뒤 30라운드 그 무리 자연 진주 11724개 중 우리 98% · 상대 2% (합산 기준 ≥85%) · 처음 거리 평균 4.8
- 상대별: proxy4_elim 1011회 96% · proxy4_king 984회 96% · proxy4_swarm 817회 96%
- 지도별: Autarky 359회 100% · Devil 151회 58% · Portals 666회 99% · Prisoners Dilemma 1051회 100% · Queen Of Spades 13회 – · Schooltime 11회 – · Slithery Fight 482회 31% · Trauma 69회 85% · Trophy 10회 –
- 국면별: r0-99 834회 90% · r100-249 1186회 99% · r250-349 792회 99%

실패 사례 (60건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack7-a-px4:proxy4_king:devil:B:1 · r40 · 드래곤 #10 L2: 샘 (23,0) 처음 거리 9 → r58 도착, 30라운드 무리 진주 4개 중 우리 2 · 상대 2
- proxy4_king · Trauma · 게임 exp/stack7-a-px4:proxy4_king:trauma:B:1 · r318 · 드래곤 #6 L3: 샘 (36,13) 처음 거리 4 → r318 도착, 30라운드 무리 진주 3개 중 우리 0 · 상대 3
- proxy4_king · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_king:slithery_fight:A:1 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_swarm · Devil · 게임 exp/stack7-a-px4:proxy4_swarm:devil:B:1 · r78 · 드래곤 #1 L2: 샘 (26,0) 처음 거리 13 → r129 도착, 30라운드 무리 진주 7개 중 우리 5 · 상대 2
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_swarm:slithery_fight:A:1 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_elim · Devil · 게임 exp/stack7-a-px4:proxy4_elim:devil:B:1 · r47 · 드래곤 #3 L2: 샘 (26,15) 처음 거리 10 → r67 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2
- proxy4_elim · Portals · 게임 exp/stack7-a-px4:proxy4_elim:portals:A:1 · r321 · 드래곤 #442 L6: 샘 (15,1) 처음 거리 4 → r321 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 0
- proxy4_elim · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_elim:slithery_fight:A:1 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_king · Devil · 게임 exp/stack7-a-px4:proxy4_king:devil:B:1 · r74 · 드래곤 #11 L2: 샘 (26,15) 처음 거리 12 → r200 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2
- proxy4_king · Trauma · 게임 exp/stack7-a-px4:proxy4_king:trauma:B:1 · r327 · 드래곤 #6 L2: 샘 (36,10) 처음 거리 1 → r327 도착, 30라운드 무리 진주 3개 중 우리 0 · 상대 3

## 위협 모형 빈틈 (tg, stack4)

- 이번: 피함(tg) 56% · 위협 칸으로 감(tgx) 5528턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 99% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 97%) · 길이별 L2-5 12237 · L6-9 100 · L10+ 160
- 비교: 피함(tg) 56% · 위협 칸으로 감(tgx) 5433턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 99% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 97%) · 길이별 L2-5 12140 · L6-9 119 · L10+ 205
- 상대별: proxy4_elim 4462회 98% · proxy4_king 4117회 98% · proxy4_swarm 3918회 98%
- 지도별: Autarky 724회 98% · Default 2501회 98% · Devil 1149회 98% · Portals 2회 100% · Prisoners Dilemma 23회 100% · Queen Of Spades 1106회 99% · Schooltime 2914회 98% · Slithery Fight 2971회 98% · Trauma 174회 96% · Trophy 933회 97%
- 국면별: r0-99 2538회 99% · r100-249 6355회 98% · r250-349 2438회 98% · r350-449 981회 99% · r450+ 185회 97%

실패 사례 (246건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:A:1 · r108 · 드래곤 #12 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r109 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Autarky · 게임 exp/stack7-a-px4:proxy4_king:autarky:B:1 · r207 · 드래곤 #5 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r209 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Devil · 게임 exp/stack7-a-px4:proxy4_king:devil:A:1 · r177 · 드래곤 #99 L2: 피함(tg), 적 머리 경로 4칸 · 맨해튼 4칸(길이 2) → 박힘 r178 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_king:queen_of_spades:A:1 · r394 · 드래곤 #54 L3: 피함(tg), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r395 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Schooltime · 게임 exp/stack7-a-px4:proxy4_king:schooltime:A:1 · r146 · 드래곤 #13 L2: 피함(tg), 적 머리 경로 2칸 · 맨해튼 2칸(길이 3) → 박힘 r148 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_king:slithery_fight:A:1 · r35 · 드래곤 #12 L5: 피함(tg), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r35 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Trophy · 게임 exp/stack7-a-px4:proxy4_king:trophy:B:1 · r111 · 드래곤 #1 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r112 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trauma · 게임 exp/stack7-a-px4:proxy4_king:trauma:A:1 · r202 · 드래곤 #16 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r204 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Autarky · 게임 exp/stack7-a-px4:proxy4_swarm:autarky:A:1 · r45 · 드래곤 #4 L2: 피함(tg), 적 머리 경로 5칸 · 맨해튼 5칸(길이 2) → 박힘 r47 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack7-a-px4:proxy4_swarm:default:B:1 · r275 · 드래곤 #65 L5: 위협 칸으로 감(tgx), 적 머리 경로 1칸 · 맨해튼 1칸(길이 3) → 박힘 r275 박힘(상대 돌진), 상대 길이 3

## 모이기 시작 제한 (gx, stack4; 드래곤 단위)

- 이번: 드래곤 60 (표식 턴 333) · 몸(자손 포함) 끝까지 100% (기준 ≥80%) · 드래곤 자체 끝까지 생존 65% (참고) · 뒤에 희생 먹이기(feed)로 끝남 2
- 비교: 드래곤 68 (표식 턴 438) · 몸(자손 포함) 끝까지 100% (기준 ≥80%) · 드래곤 자체 끝까지 생존 62% (참고) · 뒤에 희생 먹이기(feed)로 끝남 6
- 상대별: proxy4_elim 18회 100% · proxy4_king 18회 100% · proxy4_swarm 24회 100%
- 지도별: Autarky 13회 100% · Default 2회 100% · Portals 31회 100% · Schooltime 8회 100% · Slithery Fight 4회 100% · Trauma 2회 100%
- 국면별: r450+ 60회 100%

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 268개 중 우리 팀 97% (지목한 아군 67%) · 상대 1% · 지목 아군 끝까지 생존 44% (그 뒤 죽은 원인: 희생 14, 갇힘 78, 돌진 2, 아군 머리 2, 박힘(상대 돌진) 3) · 지목 아군의 몸(자손 포함)이 끝까지 삶 81% · 최종 왕 35% (최종 왕이 지목 아군의 자손 49%)
- 비교: 실행 100% · 떨군 진주 263개 중 우리 팀 98% (지목한 아군 68%) · 상대 2% · 지목 아군 끝까지 생존 45% (그 뒤 죽은 원인: 희생 12, 갇힘 79, 박힘(상대 돌진) 1, 돌진 2, 아군 머리 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 82% · 최종 왕 34% (최종 왕이 지목 아군의 자손 50%)
- 상대별: proxy4_elim 72회 96% · proxy4_king 43회 100% · proxy4_swarm 62회 98%
- 지도별: Autarky 22회 100% · Default 3회 100% · Devil 2회 100% · Portals 62회 98% · Prisoners Dilemma 2회 100% · Queen Of Spades 8회 88% · Schooltime 5회 100% · Slithery Fight 55회 96% · Trauma 18회 100%
- 국면별: r250-349 80회 100% · r350-449 82회 98% · r450+ 15회 87%

실패 사례 (4건 중 4건, 기보 확인용):
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_swarm:slithery_fight:A:1 · r442 · 드래곤 #843 L2: #742(L39)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 1
- proxy4_elim · Portals · 게임 exp/stack7-a-px4:proxy4_elim:portals:A:1 · r479 · 드래곤 #551 L2: #535(L16)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_elim · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_elim:queen_of_spades:B:1 · r422 · 드래곤 #72 L3: #51(L8)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2; 지목 아군 r439 희생에 사망
- proxy4_elim · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_elim:slithery_fight:B:1 · r456 · 드래곤 #31 L4: #452(L10)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 92% · 조각 30라운드 생존 67% · 30라운드 안 1개 이상 먹음 54% (살아서 먹음 38%) · 평생 먹은 진주 평균 2.8 · 나중에 아군을 먹임 71% (conv 10, feed 7, 분열 뒤 평균 51.4라운드) · 끝까지 생존 4% · 30라운드 안 죽은 원인: 희생 6, 갇힘 2
- 비교: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 87% · 조각 30라운드 생존 61% · 30라운드 안 1개 이상 먹음 65% (살아서 먹음 42%) · 평생 먹은 진주 평균 2.7 · 나중에 아군을 먹임 61% (conv 10, feed 9, 분열 뒤 평균 47.6라운드) · 끝까지 생존 6% · 30라운드 안 죽은 원인: 갇힘 4, 희생 8
- 상대별: proxy4_elim 11회 91% · proxy4_king 4회 25% · proxy4_swarm 9회 100%
- 지도별: Autarky 5회 100% · Default 2회 50% · Schooltime 1회 0% · Slithery Fight 12회 83% · Trauma 4회 100%
- 국면별: r250-349 5회 100% · r350-449 19회 79%

실패 사례 (4건 중 4건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:A:1 · r369 · 드래곤 #151 L9: 조각 L2 → 30라운드 생존, 먹은 진주 0 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_king · Schooltime · 게임 exp/stack7-a-px4:proxy4_king:schooltime:A:1 · r413 · 드래곤 #265 L9: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_king:slithery_fight:B:1 · r403 · 드래곤 #951 L14: 조각 L2 → 조각 죽음 r411 갇힘, 상대 길이 5, 30라운드 안 먹은 진주 4
- proxy4_elim · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_elim:slithery_fight:B:1 · r409 · 드래곤 #36 L10: 조각 L2 → 조각 죽음 r416 갇힘, 상대 길이 8, 30라운드 안 먹은 진주 0

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 2435개 (표식 턴 6065, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 1, 이미 없음 210) · 사망 진주 2224개 중 우리가 먹음 81% · 상대 18% · 아무도 안 먹음 1% · 표적으로 삼은 드래곤이 먹음 65% · 우리가 먹기까지 평균 3.7라운드 · 상대 머리가 같거나 더 가까웠던 754개: 우리 55% 대 상대 44% · 박치기 진주 418개: 우리 55% 대 상대 45% · 우리 팀 사망 진주 81% · 사망 뒤 첫 표적까지 평균 1.3라운드
- 비교: 표적 진주 2360개 (표식 턴 5857, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 0, 이미 없음 203) · 사망 진주 2157개 중 우리가 먹음 80% · 상대 19% · 아무도 안 먹음 1% · 표적으로 삼은 드래곤이 먹음 65% · 우리가 먹기까지 평균 3.7라운드 · 상대 머리가 같거나 더 가까웠던 704개: 우리 53% 대 상대 46% · 박치기 진주 378개: 우리 52% 대 상대 48% · 우리 팀 사망 진주 81% · 사망 뒤 첫 표적까지 평균 1.4라운드
- 상대별: proxy4_elim 885회 80% · proxy4_king 814회 82% · proxy4_swarm 736회 79%
- 지도별: Autarky 223회 99% · Default 258회 76% · Devil 190회 67% · Portals 510회 98% · Prisoners Dilemma 112회 91% · Queen Of Spades 141회 65% · Schooltime 225회 66% · Slithery Fight 631회 73% · Trauma 88회 85% · Trophy 57회 56%
- 국면별: r0-99 308회 72% · r100-249 845회 76% · r250-349 639회 82% · r350-449 534회 90% · r450+ 109회 84%

실패 사례 (433건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:A:1 · r212 · 드래곤 #92 L3: 진주 (14,16), 우리 머리 2칸 · 상대 머리 3칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 2턴
- proxy4_king · Autarky · 게임 exp/stack7-a-px4:proxy4_king:autarky:B:1 · r364 · 드래곤 #3 L2: 진주 (31,8), 우리 머리 3칸 · 상대 머리 2칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (1라운드 뒤), 표식 1턴
- proxy4_king · Devil · 게임 exp/stack7-a-px4:proxy4_king:devil:A:1 · r72 · 드래곤 #10 L3: 진주 (9,6), 우리 머리 3칸 · 상대 머리 3칸, 박치기 1라운드 뒤 → 상대가 먹음 (5라운드 뒤), 표식 3턴
- proxy4_king · Portals · 게임 exp/stack7-a-px4:proxy4_king:portals:A:1 · r154 · 드래곤 #114 L3: 진주 (12,14), 우리 머리 4칸 · 상대 머리 1칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (1라운드 뒤), 표식 1턴
- proxy4_king · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_king:queen_of_spades:A:1 · r57 · 드래곤 #2 L3: 진주 (8,33), 우리 머리 4칸 · 상대 머리 3칸, 박치기 1라운드 뒤 → 상대가 먹음 (6라운드 뒤), 표식 1턴
- proxy4_king · Prisoners Dilemma · 게임 exp/stack7-a-px4:proxy4_king:prisoners_dilemma:B:1 · r284 · 드래곤 #194 L2: 진주 (16,13), 우리 머리 4칸 · 상대 머리 1칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Schooltime · 게임 exp/stack7-a-px4:proxy4_king:schooltime:A:1 · r147 · 드래곤 #10 L2: 진주 (2,7), 우리 머리 4칸 · 상대 머리 1칸, 박치기 1라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_king:slithery_fight:A:1 · r4 · 드래곤 #26 L2: 진주 (33,5), 우리 머리 5칸 · 상대 머리 10칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (26라운드 뒤), 표식 3턴
- proxy4_king · Trophy · 게임 exp/stack7-a-px4:proxy4_king:trophy:B:1 · r132 · 드래곤 #12 L2: 진주 (12,22), 우리 머리 6칸 · 상대 머리 1칸, 박치기 1라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Trauma · 게임 exp/stack7-a-px4:proxy4_king:trauma:A:1 · r204 · 드래곤 #16 L2: 진주 (21,9), 우리 머리 4칸 · 상대 머리 2칸, 상대 사망 3라운드 뒤 → 아무도 안 먹음, 표식 1턴

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 839 (그중 통로 고리 세대 629, 판정에서 뺌) · 고리 밖 210: 처음 거리 평균 9.9 → 최소 5.2 · 3칸 안까지 감 41% · 희생까지 함 55% · 가는 길에 죽음 24% · 끝까지 생존 21%
- 비교: 모이기 드래곤 831 (그중 통로 고리 세대 626, 판정에서 뺌) · 고리 밖 205: 처음 거리 평균 9.6 → 최소 5.1 · 3칸 안까지 감 41% · 희생까지 함 52% · 가는 길에 죽음 24% · 끝까지 생존 24%
- 상대별: proxy4_elim 288회 88% · proxy4_king 213회 82% · proxy4_swarm 338회 83%
- 지도별: Autarky 250회 96% · Default 19회 88% · Devil 26회 81% · Portals 280회 91% · Prisoners Dilemma 135회 86% · Queen Of Spades 13회 75% · Schooltime 29회 46% · Slithery Fight 45회 77% · Trauma 42회 67%
- 국면별: r250-349 187회 88% · r350-449 571회 83% · r450+ 81회 83%

실패 사례 (53건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack7-a-px4:proxy4_king:devil:B:1 · r439 · 드래곤 #580 L4: 왕까지 거리 5 → 최소 5 (2턴), 가는 길에 죽음 r444 갇힘
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:B:1 · r435 · 드래곤 #64 L4: 왕까지 거리 5 → 최소 5 (1턴)
- proxy4_king · Portals · 게임 exp/stack7-a-px4:proxy4_king:portals:A:1 · r478 · 드래곤 #608 L24: 왕까지 거리 12 → 최소 10 (5턴)
- proxy4_king · Schooltime · 게임 exp/stack7-a-px4:proxy4_king:schooltime:A:1 · r414 · 드래곤 #265 L7: 왕까지 거리 25 → 최소 18 (14턴)
- proxy4_king · Trauma · 게임 exp/stack7-a-px4:proxy4_king:trauma:B:1 · r340 · 드래곤 #172 L6: 왕까지 거리 21 → 최소 5 (26턴), 가는 길에 죽음 r365 갇힘, 상대 길이 9
- proxy4_swarm · Autarky · 게임 exp/stack7-a-px4:proxy4_swarm:autarky:A:1 · r422 · 드래곤 #446 L4: 왕까지 거리 5 → 최소 5 (1턴), 가는 길에 죽음 r423 희생
- proxy4_king · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_king:slithery_fight:B:1 · r340 · 드래곤 #592 L4: 왕까지 거리 14 → 최소 5 (32턴), 가는 길에 죽음 r372 희생
- proxy4_swarm · Portals · 게임 exp/stack7-a-px4:proxy4_swarm:portals:A:1 · r340 · 드래곤 #457 L4: 왕까지 거리 7 → 최소 5 (16턴), 가는 길에 죽음 r356 희생
- proxy4_swarm · Devil · 게임 exp/stack7-a-px4:proxy4_swarm:devil:B:1 · r399 · 드래곤 #496 L4: 왕까지 거리 6 → 최소 4 (7턴), 가는 길에 죽음 r405 돌진, 상대 길이 27
- proxy4_swarm · Prisoners Dilemma · 게임 exp/stack7-a-px4:proxy4_swarm:prisoners_dilemma:B:1 · r340 · 드래곤 #134 L6: 왕까지 거리 15 → 최소 12 (4턴), 가는 길에 죽음 r378 박힘(상대 돌진), 상대 길이 3

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 522개 중 우리 팀 88% (지목한 아군 60%) · 상대 5% · 지목 아군 끝까지 생존 66% (그 뒤 죽은 원인: 갇힘 28, 희생 21, 아군 머리 2, 박힘(상대 돌진) 5) · 지목 아군의 몸(자손 포함)이 끝까지 삶 88% · 최종 왕 50% (최종 왕이 지목 아군의 자손 66%)
- 비교: 실행 100% · 떨군 진주 509개 중 우리 팀 88% (지목한 아군 60%) · 상대 5% · 지목 아군 끝까지 생존 68% (그 뒤 죽은 원인: 갇힘 26, 희생 17, 아군 머리 2, 돌진 1, 박힘(상대 돌진) 5) · 지목 아군의 몸(자손 포함)이 끝까지 삶 89% · 최종 왕 47% (최종 왕이 지목 아군의 자손 58%)
- 상대별: proxy4_elim 70회 91% · proxy4_king 50회 92% · proxy4_swarm 46회 85%
- 지도별: Autarky 34회 94% · Default 10회 90% · Devil 11회 82% · Portals 36회 94% · Prisoners Dilemma 27회 93% · Queen Of Spades 10회 50% · Schooltime 5회 100% · Slithery Fight 17회 82% · Trauma 16회 100%
- 국면별: r250-349 17회 88% · r350-449 104회 96% · r450+ 45회 76%

실패 사례 (17건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack7-a-px4:proxy4_king:autarky:A:1 · r343 · 드래곤 #87 L10: #8(L20)에게 희생 → 진주 5개 중 우리 2, 지목 아군 2, 상대 0
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:B:1 · r353 · 드래곤 #144 L6: #117(L10)에게 희생 → 진주 3개 중 우리 0, 지목 아군 0, 상대 3
- proxy4_king · Prisoners Dilemma · 게임 exp/stack7-a-px4:proxy4_king:prisoners_dilemma:B:1 · r485 · 드래곤 #445 L10: #131(L18)에게 희생 → 진주 5개 중 우리 0, 지목 아군 0, 상대 5
- proxy4_king · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_king:queen_of_spades:B:1 · r342 · 드래곤 #34 L4: #92(L5)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1; 지목 아군 r459 희생에 사망
- proxy4_swarm · Autarky · 게임 exp/stack7-a-px4:proxy4_swarm:autarky:B:1 · r415 · 드래곤 #436 L6: #444(L7)에게 희생 → 진주 3개 중 우리 1, 지목 아군 1, 상대 0
- proxy4_swarm · Portals · 게임 exp/stack7-a-px4:proxy4_swarm:portals:A:1 · r488 · 드래곤 #519 L5: #586(L22)에게 희생 → 진주 3개 중 우리 1, 지목 아군 1, 상대 0
- proxy4_swarm · Devil · 게임 exp/stack7-a-px4:proxy4_swarm:devil:B:1 · r492 · 드래곤 #544 L2: #540(L16)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Prisoners Dilemma · 게임 exp/stack7-a-px4:proxy4_swarm:prisoners_dilemma:B:1 · r375 · 드래곤 #345 L10: #134(L11)에게 희생 → 진주 5개 중 우리 0, 지목 아군 0, 상대 5; 지목 아군 r378 박힘(상대 돌진)에 사망
- proxy4_swarm · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_swarm:queen_of_spades:B:1 · r493 · 드래곤 #182 L7: #83(L13)에게 희생 → 진주 4개 중 우리 0, 지목 아군 0, 상대 1
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_swarm:slithery_fight:A:1 · r442 · 드래곤 #378 L4: #742(L39)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2

## 막다른 길 한입 (pocket-eat)

- 이번: 한입 100% · 2턴 안 분열 75% · 30라운드 뒤 가족 길이 변화 3.4 (줄지 않음 75%)
- 비교: 한입 100% · 2턴 안 분열 75% · 30라운드 뒤 가족 길이 변화 4 (줄지 않음 75%)
- 상대별: proxy4_elim 3회 67% · proxy4_king 1회 100% · proxy4_swarm 4회 25%
- 지도별: Devil 1회 0% · Portals 6회 67% · Trauma 1회 0%
- 국면별: r0-99 5회 80% · r100-249 1회 0% · r350-449 2회 0%

실패 사례 (4건 중 4건, 기보 확인용):
- proxy4_swarm · Devil · 게임 exp/stack7-a-px4:proxy4_swarm:devil:A:1 · r60 · 드래곤 #38 L4: 한입, 분열(새끼 L3), 30라운드 뒤 가족 길이 변화 -2
- proxy4_swarm · Portals · 게임 exp/stack7-a-px4:proxy4_swarm:portals:A:1 · r131 · 드래곤 #122 L6: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 4
- proxy4_elim · Trauma · 게임 exp/stack7-a-px4:proxy4_elim:trauma:B:1 · r401 · 드래곤 #187 L7: 한입, 분열(새끼 L6), 30라운드 뒤 가족 길이 변화 -7
- proxy4_swarm · Portals · 게임 exp/stack7-a-px4:proxy4_swarm:portals:B:1 · r418 · 드래곤 #548 L13: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 4

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 20% · 30라운드 뒤 가족 길이 변화 8.2
- 비교: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 99% · 새끼 자체 10라운드 생존 20% · 30라운드 뒤 가족 길이 변화 8.1
- 상대별: proxy4_elim 1456회 99% · proxy4_king 1364회 98% · proxy4_swarm 1373회 98%
- 지도별: Autarky 1540회 100% · Default 38회 97% · Devil 72회 88% · Portals 810회 97% · Prisoners Dilemma 1440회 99% · Queen Of Spades 30회 100% · Schooltime 55회 93% · Slithery Fight 131회 97% · Trauma 73회 90% · Trophy 4회 100%
- 국면별: r0-99 790회 99% · r100-249 1219회 99% · r250-349 950회 99% · r350-449 850회 97% · r450+ 384회 98%

실패 사례 (66건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack7-a-px4:proxy4_king:devil:B:1 · r436 · 드래곤 #543 L8: 새끼 L6 → 새끼 죽음 r441 갇힘, 상대 길이 7, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -8
- proxy4_king · Portals · 게임 exp/stack7-a-px4:proxy4_king:portals:A:1 · r146 · 드래곤 #144 L5: 새끼 L3 → 새끼 죽음 r147 갇힘, 상대 길이 7, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_king · Prisoners Dilemma · 게임 exp/stack7-a-px4:proxy4_king:prisoners_dilemma:B:1 · r477 · 드래곤 #435 L12: 새끼 L10 → 새끼 죽음 r481 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -12
- proxy4_king · Schooltime · 게임 exp/stack7-a-px4:proxy4_king:schooltime:A:1 · r305 · 드래곤 #230 L4: 새끼 L2 → 새끼 죽음 r307 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Autarky · 게임 exp/stack7-a-px4:proxy4_swarm:autarky:A:1 · r354 · 드래곤 #248 L5: 새끼 L3 → 새끼 죽음 r359 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_swarm · Default · 게임 exp/stack7-a-px4:proxy4_swarm:default:A:1 · r342 · 드래곤 #114 L5: 새끼 L3 → 새끼 죽음 r342 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_swarm · Devil · 게임 exp/stack7-a-px4:proxy4_swarm:devil:A:1 · r92 · 드래곤 #81 L5: 새끼 L3 → 새끼 죽음 r97 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_swarm · Portals · 게임 exp/stack7-a-px4:proxy4_swarm:portals:A:1 · r283 · 드래곤 #370 L8: 새끼 L6 → 새끼 죽음 r284 아군 머리, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -8
- proxy4_swarm · Prisoners Dilemma · 게임 exp/stack7-a-px4:proxy4_swarm:prisoners_dilemma:B:1 · r367 · 드래곤 #335 L12: 새끼 L10 → 새끼 죽음 r371 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -12
- proxy4_swarm · Schooltime · 게임 exp/stack7-a-px4:proxy4_swarm:schooltime:A:1 · r392 · 드래곤 #363 L7: 새끼 L5 → 새끼 죽음 r402 적 몸통, 상대 길이 17, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 87% · 그 밖(진짜로 갇힘) 551회
- 비교: 탈출 분열 뒤 남은 조각(고리의 일부) 88% · 그 밖(진짜로 갇힘) 537회
- 상대별: proxy4_elim 1494회 – · proxy4_king 1470회 – · proxy4_swarm 1383회 –
- 지도별: Autarky 1557회 – · Default 70회 – · Devil 67회 – · Portals 719회 – · Prisoners Dilemma 1457회 – · Queen Of Spades 48회 – · Schooltime 71회 – · Slithery Fight 241회 – · Trauma 106회 – · Trophy 11회 –
- 국면별: r0-99 824회 – · r100-249 1414회 – · r250-349 951회 – · r350-449 804회 – · r450+ 354회 –

## 정책 분열 (split)

- 이번: 분열 100% · 새끼 30라운드 생존 50% · 30라운드 뒤 가족 길이 변화 -0.5
- 비교: 분열 100% · 새끼 30라운드 생존 20% · 30라운드 뒤 가족 길이 변화 -6.4
- 상대별: proxy4_swarm 2회 50%
- 지도별: Default 1회 0% · Queen Of Spades 1회 100%
- 국면별: r350-449 2회 50%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_swarm · Default · 게임 exp/stack7-a-px4:proxy4_swarm:default:B:1 · r362 · 드래곤 #144 L5: 새끼 L2 → 새끼 죽음 r388 박힘(상대 돌진), 상대 길이 3, 30라운드 뒤 가족 길이 변화 -3

## 탈출 질주 3칸 (esc)

- 이번: 질주 99% · 짧은 적 머리 4칸 안 73% · 몸 생존 5라운드 97% · 10라운드 97% (드래곤 자체 92%) · 10라운드 길이 변화 -3.7
- 비교: 질주 99% · 짧은 적 머리 4칸 안 69% · 몸 생존 5라운드 96% · 10라운드 96% (드래곤 자체 92%) · 10라운드 길이 변화 -3.4
- 상대별: proxy4_elim 20회 95% · proxy4_king 30회 100% · proxy4_swarm 17회 88%
- 지도별: Default 6회 100% · Devil 6회 100% · Prisoners Dilemma 1회 100% · Queen Of Spades 6회 100% · Schooltime 17회 100% · Slithery Fight 28회 89% · Trauma 3회 100%
- 국면별: r0-99 1회 100% · r100-249 14회 86% · r250-349 11회 100% · r350-449 18회 100% · r450+ 23회 96%

실패 사례 (3건 중 3건, 기보 확인용):
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_swarm:slithery_fight:A:1 · r456 · 드래곤 #183 L7: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r459 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_elim:slithery_fight:A:1 · r219 · 드래곤 #569 L8: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r220 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_swarm:slithery_fight:B:1 · r228 · 드래곤 #16 L23: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r228 박힘(상대 돌진), 상대 길이 3

## 위협 피하기 2칸 질주

- 이번: 질주 100% · 몸 10라운드 생존 93% (드래곤 자체 89%)
- 비교: 질주 99% · 몸 10라운드 생존 94% (드래곤 자체 90%)
- 상대별: proxy4_elim 226회 91% · proxy4_king 203회 94% · proxy4_swarm 203회 95%
- 지도별: Autarky 36회 100% · Default 100회 90% · Devil 51회 94% · Prisoners Dilemma 3회 100% · Queen Of Spades 70회 94% · Schooltime 172회 91% · Slithery Fight 161회 93% · Trauma 13회 100% · Trophy 26회 96%
- 국면별: r0-99 150회 96% · r100-249 241회 93% · r250-349 134회 90% · r350-449 93회 96% · r450+ 14회 86%

실패 사례 (44건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:A:1 · r197 · 드래곤 #0 L2: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 2) → 죽음 r197 질주 불가
- proxy4_king · Devil · 게임 exp/stack7-a-px4:proxy4_king:devil:B:1 · r94 · 드래곤 #23 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r102 돌진, 상대 길이 2
- proxy4_king · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_king:queen_of_spades:A:1 · r394 · 드래곤 #54 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r395 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Schooltime · 게임 exp/stack7-a-px4:proxy4_king:schooltime:A:1 · r231 · 드래곤 #34 L3: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 4) → 죽음 r235 박힘(상대 돌진), 상대 길이 4
- proxy4_king · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_king:slithery_fight:A:1 · r123 · 드래곤 #182 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r132 갇힘, 상대 길이 4
- proxy4_swarm · Default · 게임 exp/stack7-a-px4:proxy4_swarm:default:B:1 · r233 · 드래곤 #87 L3: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 5) → 죽음 r235 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Schooltime · 게임 exp/stack7-a-px4:proxy4_swarm:schooltime:A:1 · r222 · 드래곤 #119 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r226 돌진, 상대 길이 26
- proxy4_swarm · Trophy · 게임 exp/stack7-a-px4:proxy4_swarm:trophy:A:1 · r91 · 드래곤 #48 L3: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 2) → 죽음 r99 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_swarm:slithery_fight:A:1 · r457 · 드래곤 #183 L5: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 3) → 죽음 r459 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Devil · 게임 exp/stack7-a-px4:proxy4_elim:devil:B:1 · r107 · 드래곤 #58 L3: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 2) → 죽음 r114 박힘(상대 돌진), 상대 길이 2

## 포털 통과 (전체; PORTAL?=미탐색 출구)

- 이번: 미탐색 출구 1022회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 94% (드래곤 자체 79%) · 10라운드 89% · 10라운드 안 먹은 진주 0.9
- 비교: 미탐색 출구 1005회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 94% (드래곤 자체 79%) · 10라운드 89% · 10라운드 안 먹은 진주 0.9
- 상대별: proxy4_elim 734회 94% · proxy4_king 993회 95% · proxy4_swarm 762회 92%
- 지도별: Autarky 363회 94% · Default 568회 96% · Portals 949회 93% · Prisoners Dilemma 70회 97% · Queen Of Spades 89회 78% · Schooltime 122회 88% · Slithery Fight 159회 95% · Trauma 169회 96%
- 국면별: r0-99 294회 94% · r100-249 1000회 95% · r250-349 741회 93% · r350-449 387회 91% · r450+ 67회 100%

실패 사례 (158건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:A:1 · r185 · 드래곤 #35 L3: 포털 → 죽음 r185 갇힘, 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Autarky · 게임 exp/stack7-a-px4:proxy4_king:autarky:B:1 · r285 · 드래곤 #209 L3: 포털 → 죽음 r286 갇힘, 10라운드 안 진주 0
- proxy4_king · Portals · 게임 exp/stack7-a-px4:proxy4_king:portals:A:1 · r66 · 드래곤 #23 L6: 포털 → 죽음 r66 갇힘, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack7-a-px4:proxy4_king:prisoners_dilemma:A:1 · r267 · 드래곤 #151 L3: 포털(미탐색 출구) → 죽음 r267 아군 머리, 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_king:queen_of_spades:A:1 · r50 · 드래곤 #12 L2: 포털 → 죽음 r53 갇힘, 10라운드 안 진주 0
- proxy4_king · Schooltime · 게임 exp/stack7-a-px4:proxy4_king:schooltime:B:1 · r219 · 드래곤 #42 L2: 포털(미탐색 출구) → 죽음 r219 박힘(상대 돌진), 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Trauma · 게임 exp/stack7-a-px4:proxy4_king:trauma:B:1 · r365 · 드래곤 #172 L6: 포털 → 죽음 r365 갇힘, 상대 길이 9, 10라운드 안 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack7-a-px4:proxy4_swarm:autarky:A:1 · r264 · 드래곤 #253 L2: 포털 → 죽음 r265 갇힘, 10라운드 안 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_king:slithery_fight:B:1 · r183 · 드래곤 #384 L3: 포털(미탐색 출구) → 죽음 r183 아군 머리, 상대 길이 6, 10라운드 안 진주 0
- proxy4_swarm · Default · 게임 exp/stack7-a-px4:proxy4_swarm:default:B:1 · r205 · 드래곤 #57 L2: 포털 → 죽음 r208 갇힘, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 14, 경로 37) · 잡은 길이 ≥ 우리 98% · 두 몸의 진주 우리 142 대 상대 270
- 비교: 충돌 성사 100% (인접 18, 경로 33) · 잡은 길이 ≥ 우리 98% · 두 몸의 진주 우리 121 대 상대 271
- 상대별: proxy4_elim 13회 38% · proxy4_king 10회 40% · proxy4_swarm 28회 25%
- 지도별: Autarky 1회 0% · Default 2회 0% · Devil 6회 67% · Queen Of Spades 4회 50% · Schooltime 19회 11% · Slithery Fight 18회 44% · Trauma 1회 0%
- 국면별: r0-99 1회 0% · r100-249 12회 17% · r250-349 14회 0% · r350-449 19회 53% · r450+ 5회 80%

실패 사례 (35건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack7-a-px4:proxy4_king:autarky:B:1 · r376 · 드래곤 #3 L4: 돌진 경로 3칸 → 상대 L11 잡음, 진주 우리 0 대 상대 8
- proxy4_king · Schooltime · 게임 exp/stack7-a-px4:proxy4_king:schooltime:A:1 · r192 · 드래곤 #102 L5: 돌진 경로 3칸 → 상대 L13 잡음, 진주 우리 0 대 상대 10
- proxy4_king · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_king:slithery_fight:A:1 · r272 · 드래곤 #307 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_king · Trauma · 게임 exp/stack7-a-px4:proxy4_king:trauma:A:1 · r297 · 드래곤 #116 L4: 돌진 경로 3칸 → 상대 L6 잡음, 진주 우리 0 대 상대 5
- proxy4_swarm · Default · 게임 exp/stack7-a-px4:proxy4_swarm:default:A:1 · r128 · 드래곤 #37 L2: 돌진 경로 1칸 → 상대 L3 잡음, 진주 우리 0 대 상대 3
- proxy4_swarm · Devil · 게임 exp/stack7-a-px4:proxy4_swarm:devil:A:1 · r358 · 드래곤 #9 L4: 돌진 경로 2칸 → 상대 L14 잡음, 진주 우리 2 대 상대 7
- proxy4_swarm · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_swarm:queen_of_spades:A:1 · r388 · 드래곤 #64 L2: 돌진 경로 2칸 → 상대 L7 잡음, 진주 우리 0 대 상대 5
- proxy4_swarm · Schooltime · 게임 exp/stack7-a-px4:proxy4_swarm:schooltime:B:1 · r288 · 드래곤 #5 L5: 돌진 경로 4칸 → 상대 L7 잡음, 진주 우리 0 대 상대 6
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_swarm:slithery_fight:A:1 · r279 · 드래곤 #30 L3: 돌진 경로 1칸 → 상대 L6 잡음, 진주 우리 0 대 상대 5
- proxy4_elim · Default · 게임 exp/stack7-a-px4:proxy4_elim:default:A:1 · r427 · 드래곤 #150 L2: 돌진 경로 2칸 → 상대 L28 잡음, 진주 우리 0 대 상대 16

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 비교: 먹음 100%
- 상대별: proxy4_elim 64회 100% · proxy4_king 66회 100% · proxy4_swarm 49회 100%
- 지도별: Autarky 4회 100% · Default 26회 100% · Devil 15회 100% · Portals 20회 100% · Queen Of Spades 18회 100% · Schooltime 30회 100% · Slithery Fight 51회 100% · Trauma 4회 100% · Trophy 11회 100%
- 국면별: r0-99 35회 100% · r100-249 60회 100% · r250-349 35회 100% · r350-449 41회 100% · r450+ 8회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 89%
- 비교: 그 턴 사망 0% · 10라운드 생존 87%
- 상대별: proxy4_elim 32회 – · proxy4_king 28회 – · proxy4_swarm 27회 –
- 지도별: Autarky 1회 – · Default 7회 – · Devil 9회 – · Queen Of Spades 18회 – · Schooltime 21회 – · Slithery Fight 27회 – · Trauma 2회 – · Trophy 2회 –
- 국면별: r0-99 13회 – · r100-249 33회 – · r250-349 14회 – · r350-449 20회 – · r450+ 7회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 비교: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 4회 – · proxy4_king 17회 – · proxy4_swarm 10회 –
- 지도별: Default 1회 – · Devil 8회 – · Queen Of Spades 3회 – · Schooltime 4회 – · Slithery Fight 12회 – · Trauma 3회 –
- 국면별: r0-99 5회 – · r100-249 21회 – · r250-349 2회 – · r350-449 3회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/stack7-a-px4` | 60 | 26 (0.43) | 35% | 0 (0.00) | 0 (0.00) | 9 | 16 | 0 | 2/5 (7) | 84 (1.40; 필사 21) | 16/51 (56) |
| 비교 `exp/stack5-a-px4` | 60 | 29 (0.48) | 38% | 0 (0.00) | 0 (0.00) | 10 | 18 | 0 | 3/6 (10.5) | 81 (1.35; 필사 20) | 14/50 (49) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.
- 이번 `exp/stack7-a-px4`: gx 표식 턴 333 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- 비교 `exp/stack5-a-px4`: gx 표식 턴 438 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/stack7-a-px4` | 60 | 40628 | 0.7% (277) | 14.7% (5965) | 4455 | 1.3% (57) | 3.1% (139) | 23.5% (1046/4455) |
| 비교 `exp/stack5-a-px4` | 60 | 41158 | 0.7% (283) | 14.3% (5873) | 4498 | 1.1% (50) | 3.6% (161) | 22.9% (1028/4498) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/stack7-a-px4` | 전체 | 분열 | 9 (17%) | 10.6 | 165% | 198% | 7 | 0 |
| 이번 `exp/stack7-a-px4` | 전체 | 2칸 질주 | 14 (26%) | 14.4 | 95% | 80% | 5 | 0 |
| 이번 `exp/stack7-a-px4` | 전체 | 3칸 질주 | 11 (20%) | 14.9 | 88% | 89% | 1 | 0 |
| 이번 `exp/stack7-a-px4` | 전체 | 한 걸음 | 20 (37%) | 10.5 | 56% | 59% | 14 | 10 |
| 이번 `exp/stack7-a-px4` | 4칸 이상 | 분열 | 8 (26%) | 10.9 | 172% | 200% | 6 | 0 |
| 이번 `exp/stack7-a-px4` | 4칸 이상 | 2칸 질주 | 8 (26%) | 17.6 | 91% | 78% | 2 | 0 |
| 이번 `exp/stack7-a-px4` | 4칸 이상 | 3칸 질주 | 8 (26%) | 15 | 93% | 96% | 1 | 0 |
| 이번 `exp/stack7-a-px4` | 4칸 이상 | 한 걸음 | 7 (23%) | 11.9 | 46% | 39% | 5 | 4 |
| 비교 `exp/stack5-a-px4` | 전체 | 분열 | 9 (20%) | 13 | 145% | 167% | 6 | 0 |
| 비교 `exp/stack5-a-px4` | 전체 | 2칸 질주 | 11 (25%) | 17.1 | 91% | 69% | 4 | 0 |
| 비교 `exp/stack5-a-px4` | 전체 | 3칸 질주 | 7 (16%) | 18.4 | 91% | 93% | 1 | 0 |
| 비교 `exp/stack5-a-px4` | 전체 | 한 걸음 | 17 (39%) | 11.2 | 43% | 51% | 12 | 9 |
| 비교 `exp/stack5-a-px4` | 4칸 이상 | 분열 | 9 (30%) | 13 | 145% | 167% | 6 | 0 |
| 비교 `exp/stack5-a-px4` | 4칸 이상 | 2칸 질주 | 9 (30%) | 17 | 90% | 69% | 3 | 0 |
| 비교 `exp/stack5-a-px4` | 4칸 이상 | 3칸 질주 | 5 (17%) | 18.6 | 96% | 98% | 1 | 0 |
| 비교 `exp/stack5-a-px4` | 4칸 이상 | 한 걸음 | 7 (23%) | 11.7 | 45% | 55% | 6 | 4 |

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (84건 중 10건):
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:A:1 · r109 · 드래곤 #2 L2: v7.1 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:A:1 · r185 · 드래곤 #35 L3: vnull → 갇힘, 막은 우리 드래곤 L3
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:A:1 · r221 · 드래곤 #75 L3: v1.6 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:A:1 · r230 · 드래곤 #41 L2: v7.3 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack7-a-px4:proxy4_king:autarky:B:1 · r319 · 드래곤 #65 L7: v7.7 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Autarky · 게임 exp/stack7-a-px4:proxy4_king:autarky:A:1 · r265 · 드래곤 #136 L3: v8.8 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Autarky · 게임 exp/stack7-a-px4:proxy4_king:autarky:A:1 · r324 · 드래곤 #186 L8: v7.8 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:B:1 · r156 · 드래곤 #39 L5: v7.6 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:B:1 · r168 · 드래곤 #35 L3: v7.9 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:B:1 · r228 · 드래곤 #55 L3: v7.6 → 아군 머리, 막은 우리 드래곤 L4

## 지도·판본 인식 상세 (cand-mapid)

이번 (60판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 6 | 100% | 100% | 36/36 (36) | 1679 | 1679 (0) | 0 | 0 | 0 | 0 |
| Default a | 6 | 100% | 100% | 24/24 (24) | 226 | 225 (0) | 0 | 0 | 0 | 0 |
| Devil a | 6 | 100% | 100% | 18/18 (18) | 170 | 170 (0) | 0 | 0 | 0 | 19 |
| Portals a | 6 | 100% | 100% | 18/18 (18) | 907 | 907 (0) | 0 | 0 | 0 | 1 |
| Prisoners Dilemma a | 6 | 100% | 100% | 6/18 (6) | 1507 | 1502 (0) | 5 | 0 | 0 | 162 |
| Queen Of Spades a | 6 | 100% | 100% | 12/12 (12) | 127 | 126 (0) | 1 | 0 | 0 | 45 |
| Schooltime a | 6 | 100% | 100% | 18/18 (18) | 247 | 245 (0) | 0 | 0 | 0 | 11 |
| Slithery Fight a | 6 | 100% | 100% | 48/48 (48) | 474 | 466 (0) | 8 | 0 | 0 | 42 |
| Trauma a | 6 | 100% | 100% | 12/12 (12) | 189 | 189 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 6 | 100% | 100% | 12/12 (12) | 61 | 61 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 60/60, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

### Schooltime 판의 경제 (bsp의 가설 수준 지표, 정답 판본별)

| 묶음 | 판본 | 판 | 드래곤 수 r50 | r100 | r0–99 자연 진주 먹음 | 전멸당함 | 끝 최장(전멸 0) | 판당 bsp 분열 |
|---|---|---:|---|---|---|---:|---|---:|
| 이번 | a | 6 | 9 [8, 9] | 18 [13, 18] | 34 [20, 35] | 0% | 34 [12, 35] | 0 |
| 비교 | a | 6 | 9 [8, 9] | 18 [13, 18] | 34 [20, 35] | 0% | 22 [9, 25] | 0 |

- 기준값(`research/experiments/cand-mapid.md`, 웨이브 전에 적음): b에서 드래곤 수 r50 중앙 ≥ 6, r0–99 자연 진주 중앙 ≥ 14. 우리 merge2 계열 b 29판은 3 · 9, 떼 계열(swarm8·px) b 14판은 6 · 14, 상위권 b 승자는 8 · 32다. a는 bsp가 켜지지 않는 대조군이다.

## stack5: 영토 덮기 (csplit · F · cov) 게이트와 가설 수준 지표

- 기준값은 `research/experiments/cand-stack5.md`(웨이브 전)에서, 상위권 승자(TW) 값과 merge2 값은 `research/observations/top-territory.md`에서 왔다. 정의는 영토 연구의 `exp/territory-analysis/extract.js`와 같다(영토 = 시작 몸에서 더 가까운 팀의 칸, 샘 = 그 판 판본 파일의 평균 간격 ≤12, 보로노이 = 용량 1/평균 간격 가중, 거리 = 지도 위 이동 거리, 몸은 무시).

### 게이트 (기능 적용)

| 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|
| csplit 발동: 500라운드형 지도 r0–249 판당 | ≥20 | 24 (전체 1101회) | 23.7 (전체 1091회) |
| csplit 설계 상황: 부모가 팀 최장(≥8)이 아님 | ≥90% | 100% | 100% |
| csplit 새끼가 30라운드 안에 자연 진주 ≥1개 | ≥45% (TW 47% · 45%) | 40% (1101마리) | 40% (1091마리) |
| csplit 새끼 30라운드 생존 | ≥30% (TW 34% · 51%) | 74% | 75% |
| F 목표(드래곤·샘) 수, 3걸음 안 도착 | – | 2812, 도착 59% | 2819, 도착 59% |
| F 설계 상황: 실제 우리 영토 샘, 처음 표식 때 다른 우리 머리 3걸음 안 없음 | ≥80% | 79% | 79% |
| F 도착 뒤 30라운드 그 무리 자연 진주의 우리 몫(합산) | ≥85% (TW 자기 샘 90%) | 98% (상대 2%, 11718개) | 98% (상대 2%, 11724개) |
| F 같은 몫의 지도 평균(지도마다 합산, 같은 무게, Portals 제외) | ≥85% | 83% (Autarky 100%, Devil 78%, Prisoners Dilemma 100%, Trauma 92%, Slithery Fight 46%) | 83% (Autarky 100%, Devil 78%, Prisoners Dilemma 100%, Trauma 90%, Slithery Fight 46%) |

### 가설 수준 지표 (관찰; 500라운드형 / 전멸형)

| 지표 | 기준 | 상위권 승자 | merge2 | 이번 | 비교 |
|---|---|---|---|---|---|
| r100 우리 드래곤 수(r100까지 간 판) | ≥15 / ≥10 | 30 / 21 | 4 / 3 | 13.1 / 6.4 | 13.1 / 6.2 |
| r100 우리 영토 보로노이 몫(용량 가중, 판 평균) | ≥80% | 89% / 81% | 66% / 32% | 68% / 40% | 68% / 40% |
| r100 샘 지킴: 우리 영토 샘 중 우리 머리 3걸음 안(판 평균) | ≥50% | 61% / 55% | 22% / – | 26% / 62% | 26% / 62% |
| 우리 영토 자연 진주(r0부터 생성)를 상대가 먹은 몫(합산) | ≤25% | 11% / 16% | 56% / 55% | 56% / 57% | 56% / 57% |
| 우리 영토 샘 진주를 상대가 먹은 몫(합산) | ≤15% | 7% / 6% | 50% / 33% | 48% / 42% | 49% / 41% |

- 판 수(500라운드형 / 전멸형): 이번 30 / 30 · 비교 30 / 30. 판본 파일을 못 찾은 판: 이번 0 · 비교 0.

### 부작용: 우리 드래곤의 죽음 (판당; 전체 / r250 전)

| 원인 | 이번 | 비교 |
|---|---|---|
| 갇힘(빈 이웃 없음; 통로 고리의 남은 조각 포함) | 73.2 / 37.6 | 72.6 / 37.3 |
| 적 머리에 박힘 | 8.1 / 5.8 | 7.9 / 5.6 |
| 우리 드래곤끼리 머리 충돌(둘 다 죽음, 둘 다 셈) | 1.8 / 0.9 | 1.8 / 0.9 |

- 막힘에서 아군 머리를 피해 죽은 턴(no-exit s): 이번 114 · 비교 108

### 지도별 (이번)

| 지도 | 판 | csplit 판당 | 새끼 먹음 ≥1 | 새끼 30R 생존 | F 목표 · 도착 · 무리 진주 우리 몫 | r100 드래곤 | 보로노이 | 샘 지킴 | 상대가 먹은 영토 진주 | 상대가 먹은 샘 진주 |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| Autarky | 6 | 16.3 | 48% | 85% | 359 · 92% · 100% | 9.7 | 96% | 86% | 8% | 8% |
| Default | 6 | 24.5 | 34% | 63% | 0 · – · – | 10.8 | 38% | – | 70% | – |
| Devil | 6 | 12 | 32% | 74% | 151 · 13% · 78% | 8.7 | 29% | 24% | 82% | 83% |
| Portals | 6 | 13.2 | 54% | 56% | 666 · 38% · 99% | 11.3 | 100% | 36% | 0% | 0% |
| Prisoners Dilemma | 6 | 8.2 | 47% | 94% | 1051 · 89% · 100% | 3.7 | 99% | 100% | 3% | 1% |
| Queen Of Spades | 6 | 11.8 | 51% | 73% | 13 · 31% · – | 3.2 | 22% | – | 75% | – |
| Schooltime | 6 | 26.8 | 48% | 86% | 11 · 0% · – | 16.2 | 26% | 0% | 81% | 0% |
| Slithery Fight | 6 | 47.8 | 29% | 75% | 482 · 22% · 46% | 23.2 | 28% | 7% | 77% | 83% |
| Trauma | 6 | 15.7 | 36% | 64% | 69 · 20% · 92% | 5 | 93% | 0% | 58% | 2% |
| Trophy | 6 | 7.2 | 47% | 72% | 10 · 40% · – | 5.7 | 14% | – | 76% | – |

## stack7: 수 바닥 분열(floor)과 왕 길이 상한(kcap) 게이트, 저수 에피소드, 가설 수준 지표, 지도 가르기

- 기준값은 `research/experiments/cand-stack7.md`(웨이브 전)에서, 상위권·우리 값은 `research/observations/our-eliminations.md`(2.6절, 1.3절, 2.2절)에서 왔다. 저수 에피소드와 부류의 정의는 전멸 연구(`exp/eliminations/top.js` I, `lib.js` classOf)와 같다: r50부터 5라운드 간격으로 처음 우리 수 1–3·상대 ≥8인 라운드 r(라운드 첫 턴의 수; r+20이 판 안이고 우리 전멸 전), 그 뒤 [r, r+20) 분열, 20라운드 뒤 4마리 이상이면 회복, 50라운드 안 전멸. 연구의 분열 수는 10라운드 칸 두 개의 전체 분열(탈출 분열 포함)이고, 여기서는 [r, r+20)을 그대로 센다.

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| floor | 발동(판당; floor 지도 판) | – | 49 (1.2; 42판) | 0 (0; 42판) |
| floor | 1. 설계 상황: 발동 때 상대 ≥8마리 | ≥90% | 90% | – |
| floor | 저수 에피소드가 있는 floor 지도 판 · 그 20라운드 안 floor 발동이 있었던 판 | (관찰) | 32 · 28% | 34 · 0% |
| floor | 2. 즉시 효과 A: 에피소드 20라운드 비탈출 분열(판당; floor 지도) | ≥2.0 (상위 LX·LS 2.0, 우리 0.5) | 0.4 (floor 0.4, kcap 0, csplit 0; 탈출 포함 전체 0.7) | 0.1 (floor 0, kcap 0, csplit 0; 탈출 포함 전체 0.2) |
| floor | 3. 즉시 효과 B: 에피소드 20라운드 뒤 4마리 이상(floor 지도) | ≥23% (상위 LX 23%, LS 26%, 우리 5%) | 25% (8/32) | 9% (3/34) |
| floor | 4. 즉시 효과 C: floor 새끼 30라운드 생존 | ≥34% (상위 패자 제 영토 새끼 34%, 승자 51%) | 61% (49마리) | – (0마리) |
| kcap | 발동(판당; kcap 지도 판) | – | 8 (0.2; 36판) | 0 (0; 36판) |
| kcap | 1. 설계 상황: 부모가 그 순간 팀 최장이고 r250 전 | ≥90% | 100% | – |
| kcap | 2. 즉시 효과: 새끼 10라운드 생존 | ≥74% (상위권 길이 4 분열 74.2%) | 50% (8마리) | – (0마리) |
| kcap | 2. 즉시 효과: 부모 10라운드 생존 | ≥55% (상위권 54.5%) | 50% | – |

### 저수 에피소드 (floor 지도 / 모든 지도; 판정은 floor 지도)

| 묶음 | 지도 | 판 | 에피소드 있음 | 처음 라운드(중앙) | 그때 우리 수 · 상대 수 | 그때 총길이 · 최장 | 20라운드 비탈출 분열 | floor · kcap | 탈출 포함 전체 | 20라운드 뒤 4마리 이상 | 50라운드 안 전멸 |
|---|---|---:|---:|---:|---|---|---:|---|---:|---:|---:|
| 이번 | floor 지도 | 42 | 76% | 337.5 | 2.9 · 30.8 | 13.5 · 7.2 | 0.4 | 0.4 · 0 | 0.7 | 25% | 9% |
| 이번 | floor 지도 중 전멸형 | 24 | 79% | 160 | 2.8 · 29.2 | 8.5 · 4.1 | 0.3 | 0.3 · 0 | 0.4 | 16% | 16% |
| 이번 | floor 지도 중 500형 | 18 | 72% | 400 | 3 · 33.2 | 20.8 · 11.7 | 0.5 | 0.5 · 0 | 1.2 | 38% | 0% |
| 이번 | 끄는 지도(Autarky·PD·Portals) | 18 | 61% | 380 | 2.8 · 23.6 | 30.5 · 16.9 | 0 | 0 · 0 | 9.1 | 0% | 0% |
| 이번 | 모든 지도 | 60 | 72% | 360 | 2.9 · 29 | 17.8 · 9.7 | 0.3 | 0.3 · 0 | 2.9 | 19% | 7% |
| 비교 | floor 지도 | 42 | 81% | 302.5 | 2.9 · 30 | 13.4 · 7.2 | 0.1 | 0 · 0 | 0.2 | 9% | 9% |
| 비교 | floor 지도 중 전멸형 | 24 | 88% | 150 | 2.9 · 28 | 8.8 · 4.3 | 0.1 | 0 · 0 | 0.3 | 14% | 14% |
| 비교 | floor 지도 중 500형 | 18 | 72% | 400 | 3 · 33.3 | 20.7 · 11.9 | 0 | 0 · 0 | 0 | 0% | 0% |
| 비교 | 끄는 지도(Autarky·PD·Portals) | 18 | 61% | 380 | 2.8 · 23.6 | 30.5 · 16.9 | 0 | 0 · 0 | 9.1 | 0% | 0% |
| 비교 | 모든 지도 | 60 | 75% | 360 | 2.9 · 28.4 | 17.6 · 9.6 | 0 | 0 · 0 | 2.4 | 7% | 7% |

- 상위권 기준(전멸 연구 2.6절, 전멸형): LX 72%가 그런 때를 겪고(처음 r105) 20라운드에 2.0번 나누며 23%가 회복, 42%가 50라운드 안 전멸. LS 69%, 2.0번, 26%, 0%. 우리 g4 LX 95%(r50), 0.5번, 5%, 15%.

### 가설 수준 지표 (관찰)

| 기능 | 지표 | 기준 | 상위권 · 이전 우리 | 이번 | 비교 |
|---|---|---|---|---|---|
| floor | r100 우리 드래곤 수(전멸형; 전멸은 0) — 전멸형 5지도 / PD 뺀 4지도 | ≥5.5 | 상위 LX 5.5, 우리 g4 LX 2.5 | 6.4 / 7.1 | 6.2 / 6.9 |
| floor | 전멸률(전멸형) | ≤66% | swarm8 66%, merge2 78% | 27% (8/30) / 33% (8/24) | 33% (10/30) / 42% (10/24) |
| floor | 전멸 라운드 중앙(전멸형) | ≥r235 | swarm8 235, merge2 150, stack1–3 163 | 162.5 / 162.5 | 176.5 / 176.5 |
| kcap | 우리 전멸 중 E2(왕 사냥) 비율(모든 지도) | ≤8% | 상위 LX 6%, 우리 16% | 0% (E1 0 · E2 0 · E3m 7 · E3l 1) | 30% (E1 0 · E2 3 · E3m 6 · E3l 1) |
| kcap | r50 우리 최장 평균(전멸형; 전멸은 0) — 5지도 / 4지도 | ≤4.5 | 상위 LS 3.8, 우리 g4 LX 6.8 | 4.8 / 3.2 | 5.2 / 3.8 |
| kcap | 전멸한 판의 길이 ≥8 죽음(판당; 모든 지도) | ≤0.4 | 우리 0.75 | 0 (8판) | 0.7 (10판) |

### 지도 가르기 (map= 표식으로 확인)

- floor는 Trophy, Queen Of Spades, Devil, Default, Schooltime, Trauma, Slithery Fight에서만, kcap은 그중 Slithery Fight를 뺀 여섯에서만 켠다. 봇은 프로세스마다 자기 창으로 지도 가족을 인식하고(`map=` 표식), 인식 전·`none`이면 끈다. "표식이 켜는 가족이 아닌 발동"은 발동한 프로세스의 마지막 `map=` 표식이 그 기능을 켜는 가족을 대지 않은 발동이다(0이어야 한다). "인식한 프로세스"는 마지막 표식이 그 판의 참 지도 가족을 댄 프로세스다.

| 묶음 | 지도(정답 판본) | 판 | floor 발동 | kcap 발동 | 표식이 켜는 가족이 아닌 발동 | 인식한 프로세스 |
|---|---|---:|---:|---:|---:|---:|
| 이번 | Autarky (끔) | 6 | 0 | 0 | 0 | 100% (1679/1679) |
| 이번 | Default | 6 | 12 | 2 | 0 | 100% (225/226) |
| 이번 | Devil a | 6 | 8 | 0 | 0 | 100% (170/170) |
| 이번 | Portals (끔) | 6 | 0 | 0 | 0 | 100% (907/907) |
| 이번 | Prisoners Dilemma (끔) | 6 | 0 | 0 | 0 | 100% (1507/1507) |
| 이번 | Queen Of Spades a | 6 | 10 | 3 | 0 | 100% (127/127) |
| 이번 | Schooltime a | 6 | 12 | 0 | 0 | 99% (245/247) |
| 이번 | Slithery Fight a (kcap 끔) | 6 | 2 | 0 | 0 | 100% (474/474) |
| 이번 | Trauma | 6 | 5 | 1 | 0 | 100% (189/189) |
| 이번 | Trophy | 6 | 0 | 2 | 0 | 100% (61/61) |
| 비교 | Autarky (끔) | 6 | 0 | 0 | 0 | 표식 없음 |
| 비교 | Default | 6 | 0 | 0 | 0 | 표식 없음 |
| 비교 | Devil a | 6 | 0 | 0 | 0 | 표식 없음 |
| 비교 | Portals (끔) | 6 | 0 | 0 | 0 | 표식 없음 |
| 비교 | Prisoners Dilemma (끔) | 6 | 0 | 0 | 0 | 표식 없음 |
| 비교 | Queen Of Spades a | 6 | 0 | 0 | 0 | 표식 없음 |
| 비교 | Schooltime a | 6 | 0 | 0 | 0 | 표식 없음 |
| 비교 | Slithery Fight a (kcap 끔) | 6 | 0 | 0 | 0 | 표식 없음 |
| 비교 | Trauma | 6 | 0 | 0 | 0 | 표식 없음 |
| 비교 | Trophy | 6 | 0 | 0 | 0 | 표식 없음 |

