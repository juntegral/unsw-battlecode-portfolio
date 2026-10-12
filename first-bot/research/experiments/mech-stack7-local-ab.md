# 구현 적용 확인

- 대상: `exp/stack7-a-px4+exp/stack7-b-px4` 120판
- 기준(사용자 규칙 2026-09-30): 승률이 아니라, 봇에 구현한 기능이 이 상대들에게 실제로 발동하고 의도대로 작동했는지를 본다.
- "의도대로"의 정의: 모이기=왕 3칸 안까지 가거나 희생까지 함 · 희생=떨군 진주 절반 이상을 우리 팀이 먹고 상대는 못 먹음 · 한입=2턴 안 분열하고 30라운드 뒤 가족 길이가 줄지 않음 · 탈출 분열=10라운드 뒤 몸이 살아 있음 · 정책 분열=새끼 30라운드 생존 · 탈출 질주·위협 피하기=10라운드 뒤 몸 생존 · 포털=3라운드 뒤 몸 생존 · 돌진=충돌 성사, 잡은 길이 ≥ 우리, 두 몸의 진주를 우리가 더 먹음 · 먹이 질주=진주 먹음.
- "몸"은 그 드래곤과 그 뒤 분열로 태어난 자손 전체다. 통로 고리처럼 몸을 새끼에게 넘기며 버티는 경우를 손실로 세지 않기 위해서다.
- stack2의 "의도대로": 조각 떼기=조각이 30라운드 살며 진주를 1개 이상 먹거나, 나중에 희생(feed·conv)으로 아군을 먹임 · 새 사망 진주 줍기=표적이 된 사망 진주(진주 하나가 한 건)를 우리 팀이 먹음(자연 진주로 오인했거나 이미 없던 표적은 판정에서 뺌).
- stack4의 "의도대로": tg=표식 턴 뒤 2라운드 안에 박히지 않음 · 몰렸을 때 분열=10라운드 뒤 몸이 살아 있음(보존율은 효과 줄) · px=그 턴에 우리 드래곤과 부딪혀 죽지 않음 · gx=그 드래곤의 몸(그 드래곤과 뒤에 태어난 자손)이 끝까지 삶(사용자 결정 17:16: 생존은 몸으로 판정, 드래곤 자체 생존은 참고).
- cand-mapid의 "의도대로": Schooltime b 초반 분열(bsp)=떼어 낸 조각(새 유닛)이 10라운드 뒤 살아 있음 · 지도·판본 인식=그 판에서 1개 이상의 프로세스가 판본까지 결정했고, 결정한 프로세스(마지막 표식 기준)가 모두 정답 지도·판본을 댐. 정답 판본은 로컬이면 지도 파일 이름, 온라인이면 기보의 자연 생성(한쪽 판본에서만 생성하는 칸)으로 정하고, 끝까지 가릴 수 없던 판은 뺀다. 지도별 줄의 이름 뒤 a·b·?가 정답 판본이다.
- stack5의 "의도대로": 덮기 분열=새끼가 30라운드 안에 자연 진주를 1개 이상 먹음(생존은 효과 줄) · 샘 지킴=목표 샘 3걸음 안에 든 뒤 30라운드 동안 그 무리(실제 샘, 목표에서 3걸음 안)에 생긴 자연 진주의 85% 이상을 우리가 먹음(도착하지 않았거나 진주가 생기지 않은 목표는 뺌) · 영토 덮기 끌림=20라운드 안에 우리 영토 자연 진주를 먹음. 게이트와 가설 수준 지표는 맨 뒤 stack5 절.
- stack7의 "의도대로": 수 바닥 분열(floor)=새끼가 30라운드 뒤 살아 있음 · 왕 길이 상한 분열(kcap)=새끼가 10라운드 뒤 살아 있음(부모 생존은 효과 줄). 판이 먼저 끝나면 생존으로 센다. 게이트, 저수 에피소드, 지도 가르기는 맨 뒤 stack7 절.

## 요약

| 기능 | 발동(판당) | 의도대로 | 
|---|---:|---:|
| 수 바닥 분열 (split floor, stack7) | 72 (0.6) | 65% | 
| 왕 길이 상한 분열 (split kcap, stack7) | 12 (0.1) | 58% | 
| 지도·판본 인식 (map=, cand-mapid; 판 단위) | 120 (1) | 100% | 
| Schooltime b 초반 분열 (split bsp, cand-mapid) | 53 (0.4) | 94% | 
| 덮기 분열 (csplit, stack5) | 2045 (17) | 40% | 
| 샘 지킴 (F, stack5; 드래곤·샘 단위) | 4586 (38.2) | 94% | 
| 위협 모형 빈틈 (tg, stack4) | 25922 (216) | 98% | 
| 모이기 시작 제한 (gx, stack4; 드래곤 단위) | 139 (1.2) | 99% | 
| 큰 아군 곁 희생 (conv, stack1 M1) | 335 (2.8) | 99% | 
| 조각 떼기 (split frag, stack2 S1) | 43 (0.4) | 79% | 
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 4775 (39.8) | 80% | 
| 왕에게 모이기 (g, 드래곤 단위) | 1780 (14.8) | 83% | 
| 희생 먹이기 (feed) | 310 (2.6) | 88% | 
| 막다른 길 한입 (pocket-eat) | 1015 (8.5) | 99% | 
| 탈출 분열 (escape-split) | 8027 (66.9) | 98% | 
| 출구 없음 (no-exit) | 8279 (69) | – | 
| 정책 분열 (split) | 4 (0) | 75% | 
| 탈출 질주 3칸 (esc) | 145 (1.2) | 94% | 
| 위협 피하기 2칸 질주 | 1278 (10.7) | 93% | 
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 5428 (45.2) | 94% | 
| 돌진 (TRADE) | 83 (0.7) | 35% | 
| 먹이 질주 (2칸 이상, 먹은 것) | 322 (2.7) | 100% | 
| 기타 2칸 질주 | 169 (1.4) | – | 
| 마지막 돌진 (last-trade) | 66 (0.6) | – | 

- 건강: 턴 446183, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 18471턴 · 끝판(late) 9356턴 · 돌진 신뢰(T, 탈출 끔) 35턴, 그 직후 박혀 죽음 0

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 
|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 2% (87/5395턴) | 
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 38.4칸 (9.1회), 진주 우리 93% · 상대 2% | 
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 0.2칸 (판당 0.02회) | 
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 24% (2088/8616턴) | 
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.058회 (7건, 93칸) | 
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 6.2마리 (60판) | 
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 19.2회 | 
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 52% (우리 42%) | 
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 7.6 대 상대 24.3 (8.9회) · 박힌 교환의 우리 몫 21% (433회) | 
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 8.6개 | 

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 수 바닥 분열 (split floor, stack7)

- 이번: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 92% · 적 머리가 7×7 시야 안 39% · 부모 길이 평균 5.3 · 우리 수(표식) 평균 2.7 · 상대 수 평균 27.9 · 새끼 10라운드 생존 86% · 30라운드 65% · 부모 10라운드 생존 86% · 30라운드 67% · 새끼 30라운드 안 1개 이상 먹음 56% · 30라운드 뒤 가족 길이 변화 2.1 · 30라운드 안 새끼가 죽은 원인: 갇힘 10, 돌진 3, 박힘(상대 돌진) 4, 희생 8
- 상대별: proxy4_elim 27회 67% · proxy4_king 19회 68% · proxy4_swarm 26회 62%
- 지도별: Default 19회 68% · Devil 14회 64% · Queen Of Spades 13회 69% · Schooltime 14회 64% · Slithery Fight 3회 67% · Trauma 9회 56%
- 국면별: r0-99 4회 50% · r100-249 7회 71% · r250-349 26회 69% · r350-449 35회 63%

실패 사례 (25건 중 10건, 기보 확인용):
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

- 이번: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 50% · 부모 길이 평균 8.3 · 우리 수(표식) 평균 4.3 · 상대 수 평균 14.4 · 새끼 10라운드 생존 58% · 30라운드 42% · 부모 10라운드 생존 58% · 30라운드 33% · 새끼 30라운드 안 1개 이상 먹음 58% · 30라운드 뒤 가족 길이 변화 2.5 · 30라운드 안 새끼가 죽은 원인: 박힘(상대 돌진) 3, 아군 머리 1, 갇힘 3
- 상대별: proxy4_elim 7회 43% · proxy4_king 1회 100% · proxy4_swarm 4회 75%
- 지도별: Default 4회 100% · Queen Of Spades 4회 25% · Trauma 2회 0% · Trophy 2회 100%
- 국면별: r0-99 4회 75% · r100-249 8회 50%

실패 사례 (5건 중 5건, 기보 확인용):
- proxy4_elim · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_elim:queen_of_spades:A:1 · r91 · 드래곤 #21 L8: 우리 4마리 · 상대 9마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r98 아군 머리, 상대 길이 5, 부모 10라운드 죽음 · 표식 map=Queen_Of_Spades/a
- proxy4_elim · Trauma · 게임 exp/stack7-a-px4:proxy4_elim:trauma:B:1 · r145 · 드래곤 #27 L8: 우리 5마리 · 상대 10마리 · 새끼 L2 → 새끼 죽음 r155 갇힘, 부모 10라운드 생존 · 표식 map=Trauma/a
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:A:2 · r164 · 드래곤 #46 L7: 우리 4마리 · 상대 15마리 · 새끼 L2 → 새끼 죽음 r164 갇힘, 상대 길이 3, 부모 10라운드 생존 · 표식 map=Trauma/a
- proxy4_elim · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_elim:queen_of_spades:A:1 · r108 · 드래곤 #35 L8: 우리 4마리 · 상대 9마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r109 박힘(상대 돌진), 상대 길이 2, 부모 10라운드 생존 · 표식 map=Queen_Of_Spades/a
- proxy4_elim · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_elim:queen_of_spades:A:1 · r120 · 드래곤 #35 L7: 우리 4마리 · 상대 11마리 · 새끼 L2 → 새끼 죽음 r121 갇힘, 부모 10라운드 죽음 · 표식 map=Queen_Of_Spades/a

## 지도·판본 인식 (map=, cand-mapid; 판 단위)

- 이번: 판본을 기보로 가릴 수 있는 판 120/120 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 95%, 그중 정답 100% · 프로세스 10688: 표식 없음 5, 결정 10651 (정답 100%, 틀림 0), 가족만 31, 모름 1, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 438라운드
- 상대별: proxy4_elim 40회 100% · proxy4_king 40회 100% · proxy4_swarm 40회 100%
- 지도별: Autarky a 12회 100% · Default a 12회 100% · Devil a 6회 100% · Devil b 6회 100% · Portals a 12회 100% · Prisoners Dilemma a 6회 100% · Prisoners Dilemma b 6회 100% · Queen Of Spades a 6회 100% · Queen Of Spades b 6회 100% · Schooltime a 6회 100% · Schooltime b 6회 100% · Slithery Fight a 6회 100% · Slithery Fight b 6회 100% · Trauma a 12회 100% · Trophy a 12회 100%
- 국면별: r0-99 120회 100%

## Schooltime b 초반 분열 (split bsp, cand-mapid)

- 이번: 분열 100% · 설계 상황(그 판이 실제로 Schooltime b) 100% · 조각 10라운드 생존 94% (기준 ≥85%; 상위권 b 92%) · 10라운드 안 1개 이상 먹음 19% (상위권 b 20%) · 부모 10라운드 생존 94% · 조각 30라운드 생존 91%, 30라운드 안 1개 이상 먹음 32% · 30라운드 뒤 가족 길이 변화 2.3 · 30라운드 안 조각이 죽은 원인: 갇힘 4, 박힘(상대 돌진) 1
- 상대별: proxy4_elim 24회 88% · proxy4_king 12회 100% · proxy4_swarm 17회 100%
- 지도별: Schooltime 53회 94%
- 국면별: r0-99 38회 97% · r100-249 15회 87%

실패 사례 (3건 중 3건, 기보 확인용):
- proxy4_elim · Schooltime · 게임 exp/stack7-b-px4:proxy4_elim:schooltime_b:A:2 · r47 · 드래곤 #8 L4: 조각 L2 → 조각 죽음 r55 박힘(상대 돌진), 상대 길이 2, 10·30라운드 안 먹은 진주 0·0
- proxy4_elim · Schooltime · 게임 exp/stack7-b-px4:proxy4_elim:schooltime_b:A:2 · r149 · 드래곤 #8 L9: 조각 L2 → 조각 죽음 r156 갇힘, 10·30라운드 안 먹은 진주 1·1
- proxy4_elim · Schooltime · 게임 exp/stack7-b-px4:proxy4_elim:schooltime_b:A:2 · r150 · 드래곤 #8 L7: 조각 L2 → 조각 죽음 r159 갇힘, 상대 길이 4, 10·30라운드 안 먹은 진주 1·1

## 덮기 분열 (csplit, stack5)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 35% · 부모가 스스로 최장이라 믿음(k) 66% · 새끼 30라운드 안 자연 진주 ≥1 40% (500형 40% · 전멸형 39%; 기준 ≥45%) · 새끼 30라운드 생존 73% (500형 73% · 전멸형 72%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 86% · 새끼 30라운드 안 자연 진주 평균 0.9 · 30라운드 안 죽은 원인: 갇힘 397, 아군 머리 35, 박힘(상대 돌진) 104, 희생 2, 돌진 23, 적 몸통 1
- 상대별: proxy4_elim 750회 42% · proxy4_king 685회 39% · proxy4_swarm 610회 37%
- 지도별: Autarky 221회 43% · Default 325회 38% · Devil 132회 29% · Portals 158회 49% · Prisoners Dilemma 49회 47% · Prisoners Dilemma (10) 19회 37% · Queen Of Spades 103회 41% · Schooltime 181회 46% · Slithery Fight 506회 32% · Trauma 230회 43% · Trophy 121회 46%
- 국면별: r0-99 943회 42% · r100-249 1102회 37%

실패 사례 (1237건 중 10건, 기보 확인용):
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

- 이번: 목표 4586개(표식 턴 43869) · 설계 상황 76% (실제 샘 99%, 우리 영토 88%, 처음에 다른 우리 머리 3걸음 안 없음 89%; 기준 ≥80%) · 3걸음 안 도착 51% · 도착 뒤 30라운드 그 무리 자연 진주 15283개 중 우리 96% · 상대 3% (합산 기준 ≥85%) · 처음 거리 평균 5.8
- 상대별: proxy4_elim 1605회 93% · proxy4_king 1527회 95% · proxy4_swarm 1454회 95%
- 지도별: Autarky 592회 100% · Default 3회 – · Devil 314회 50% · Portals 1393회 99% · Prisoners Dilemma 1051회 100% · Prisoners Dilemma (10) 97회 100% · Queen Of Spades 21회 – · Schooltime 11회 – · Slithery Fight 922회 30% · Trauma 167회 86% · Trophy 15회 –
- 국면별: r0-99 1456회 85% · r100-249 1879회 98% · r250-349 1251회 98%

실패 사례 (136건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack7-a-px4:proxy4_king:devil:B:1 · r40 · 드래곤 #10 L2: 샘 (23,0) 처음 거리 9 → r58 도착, 30라운드 무리 진주 4개 중 우리 2 · 상대 2
- proxy4_king · Trauma · 게임 exp/stack7-a-px4:proxy4_king:trauma:B:1 · r318 · 드래곤 #6 L3: 샘 (36,13) 처음 거리 4 → r318 도착, 30라운드 무리 진주 3개 중 우리 0 · 상대 3
- proxy4_king · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_king:slithery_fight:A:1 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_swarm · Devil · 게임 exp/stack7-a-px4:proxy4_swarm:devil:B:1 · r78 · 드래곤 #1 L2: 샘 (26,0) 처음 거리 13 → r129 도착, 30라운드 무리 진주 7개 중 우리 5 · 상대 2
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_swarm:slithery_fight:A:1 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_elim · Devil · 게임 exp/stack7-a-px4:proxy4_elim:devil:B:1 · r47 · 드래곤 #3 L2: 샘 (26,15) 처음 거리 10 → r67 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2
- proxy4_elim · Portals · 게임 exp/stack7-a-px4:proxy4_elim:portals:A:1 · r321 · 드래곤 #442 L6: 샘 (15,1) 처음 거리 4 → r321 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 0
- proxy4_elim · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_elim:slithery_fight:A:1 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:A:2 · r41 · 드래곤 #4 L2: 샘 (19,1) 처음 거리 13 → r70 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2
- proxy4_elim · Trauma · 게임 exp/stack7-b-px4:proxy4_elim:trauma:A:2 · r331 · 드래곤 #106 L5: 샘 (11,10) 처음 거리 2 → r331 도착, 30라운드 무리 진주 6개 중 우리 3 · 상대 0

## 위협 모형 빈틈 (tg, stack4)

- 이번: 피함(tg) 56% · 위협 칸으로 감(tgx) 11528턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 99% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 97%) · 길이별 L2-5 25378 · L6-9 274 · L10+ 270
- 상대별: proxy4_elim 8637회 98% · proxy4_king 9024회 98% · proxy4_swarm 8261회 98%
- 지도별: Autarky 1503회 98% · Default 4744회 98% · Devil 2202회 98% · Portals 7회 100% · Prisoners Dilemma 23회 100% · Prisoners Dilemma (10) 521회 99% · Queen Of Spades 2196회 99% · Schooltime 5167회 98% · Slithery Fight 6779회 98% · Trauma 433회 96% · Trophy 2347회 97%
- 국면별: r0-99 4877회 99% · r100-249 12499회 98% · r250-349 5877회 98% · r350-449 2244회 99% · r450+ 425회 98%

실패 사례 (474건 중 10건, 기보 확인용):
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

- 이번: 드래곤 139 (표식 턴 787) · 몸(자손 포함) 끝까지 99% (기준 ≥80%) · 드래곤 자체 끝까지 생존 60% (참고) · 뒤에 희생 먹이기(feed)로 끝남 5
- 상대별: proxy4_elim 38회 100% · proxy4_king 47회 98% · proxy4_swarm 54회 100%
- 지도별: Autarky 38회 100% · Default 2회 100% · Devil 1회 100% · Portals 60회 100% · Prisoners Dilemma (10) 13회 100% · Schooltime 11회 100% · Slithery Fight 10회 90% · Trauma 4회 100%
- 국면별: r450+ 139회 99%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:B:2 · r490 · 드래곤 #221 L4: gx 1턴 (r490–r490) → 죽음 r492 희생

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 513개 중 우리 팀 98% (지목한 아군 66%) · 상대 1% · 지목 아군 끝까지 생존 38% (그 뒤 죽은 원인: 희생 41, 갇힘 149, 돌진 4, 아군 머리 3, 박힘(상대 돌진) 9, 적 몸통 1) · 지목 아군의 몸(자손 포함)이 끝까지 삶 76% · 최종 왕 32% (최종 왕이 지목 아군의 자손 48%)
- 상대별: proxy4_elim 138회 98% · proxy4_king 83회 100% · proxy4_swarm 114회 98%
- 지도별: Autarky 52회 100% · Default 4회 100% · Devil 2회 100% · Portals 125회 99% · Prisoners Dilemma 2회 100% · Prisoners Dilemma (10) 4회 100% · Queen Of Spades 9회 89% · Schooltime 7회 100% · Slithery Fight 87회 98% · Trauma 43회 98%
- 국면별: r250-349 147회 99% · r350-449 166회 99% · r450+ 22회 91%

실패 사례 (5건 중 5건, 기보 확인용):
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_swarm:slithery_fight:A:1 · r442 · 드래곤 #843 L2: #742(L39)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 1
- proxy4_elim · Portals · 게임 exp/stack7-a-px4:proxy4_elim:portals:A:1 · r479 · 드래곤 #551 L2: #535(L16)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_elim · Queen Of Spades · 게임 exp/stack7-a-px4:proxy4_elim:queen_of_spades:B:1 · r422 · 드래곤 #72 L3: #51(L8)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2; 지목 아군 r439 희생에 사망
- proxy4_elim · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_elim:slithery_fight:B:1 · r456 · 드래곤 #31 L4: #452(L10)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:B:2 · r328 · 드래곤 #246 L4: #225(L9)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1; 지목 아군 r334 돌진에 사망

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 91% · 조각 30라운드 생존 67% · 30라운드 안 1개 이상 먹음 58% (살아서 먹음 40%) · 평생 먹은 진주 평균 3.8 · 나중에 아군을 먹임 60% (conv 11, feed 15, 분열 뒤 평균 43.4라운드) · 끝까지 생존 14% · 30라운드 안 죽은 원인: 희생 11, 갇힘 3
- 상대별: proxy4_elim 19회 84% · proxy4_king 10회 60% · proxy4_swarm 14회 86%
- 지도별: Autarky 8회 100% · Default 4회 75% · Queen Of Spades 2회 100% · Schooltime 1회 0% · Slithery Fight 16회 81% · Trauma 12회 67%
- 국면별: r250-349 7회 100% · r350-449 36회 75%

실패 사례 (9건 중 9건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-a-px4:proxy4_king:default:A:1 · r369 · 드래곤 #151 L9: 조각 L2 → 30라운드 생존, 먹은 진주 0 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_king · Schooltime · 게임 exp/stack7-a-px4:proxy4_king:schooltime:A:1 · r413 · 드래곤 #265 L9: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_king:slithery_fight:B:1 · r403 · 드래곤 #951 L14: 조각 L2 → 조각 죽음 r411 갇힘, 상대 길이 5, 30라운드 안 먹은 진주 4
- proxy4_elim · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_elim:slithery_fight:B:1 · r409 · 드래곤 #36 L10: 조각 L2 → 조각 죽음 r416 갇힘, 상대 길이 8, 30라운드 안 먹은 진주 0
- proxy4_king · Trauma · 게임 exp/stack7-b-px4:proxy4_king:trauma:B:2 · r360 · 드래곤 #182 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r352 · 드래곤 #33 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:B:2 · r397 · 드래곤 #289 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Trauma · 게임 exp/stack7-b-px4:proxy4_elim:trauma:A:2 · r396 · 드래곤 #203 L7: 조각 L2 → 조각 죽음 r402 갇힘, 30라운드 안 먹은 진주 0
- proxy4_elim · Trauma · 게임 exp/stack7-b-px4:proxy4_elim:trauma:B:2 · r352 · 드래곤 #157 L10: 조각 L2 → 30라운드 생존, 먹은 진주 0

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 4775개 (표식 턴 11806, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 2, 이미 없음 418) · 사망 진주 4355개 중 우리가 먹음 80% · 상대 19% · 아무도 안 먹음 1% · 표적으로 삼은 드래곤이 먹음 64% · 우리가 먹기까지 평균 3.7라운드 · 상대 머리가 같거나 더 가까웠던 1444개: 우리 54% 대 상대 45% · 박치기 진주 754개: 우리 55% 대 상대 45% · 우리 팀 사망 진주 80% · 사망 뒤 첫 표적까지 평균 1.3라운드
- 상대별: proxy4_elim 1741회 79% · proxy4_king 1546회 81% · proxy4_swarm 1488회 78%
- 지도별: Autarky 478회 99% · Default 517회 75% · Devil 311회 59% · Portals 1183회 98% · Prisoners Dilemma 112회 91% · Prisoners Dilemma (10) 55회 51% · Queen Of Spades 208회 57% · Schooltime 307회 63% · Slithery Fight 1202회 71% · Trauma 269회 82% · Trophy 133회 45%
- 국면별: r0-99 567회 69% · r100-249 1610회 75% · r250-349 1313회 83% · r350-449 1072회 88% · r450+ 213회 74%

실패 사례 (889건 중 10건, 기보 확인용):
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

- 이번: 모이기 드래곤 1780 (그중 통로 고리 세대 1372, 판정에서 뺌) · 고리 밖 408: 처음 거리 평균 10.3 → 최소 5.3 · 3칸 안까지 감 42% · 희생까지 함 55% · 가는 길에 죽음 22% · 끝까지 생존 23%
- 상대별: proxy4_elim 558회 84% · proxy4_king 552회 81% · proxy4_swarm 670회 83%
- 지도별: Autarky 617회 95% · Default 32회 82% · Devil 34회 78% · Portals 552회 88% · Prisoners Dilemma 135회 86% · Prisoners Dilemma (10) 172회 100% · Queen Of Spades 24회 68% · Schooltime 35회 32% · Slithery Fight 99회 76% · Trauma 80회 68%
- 국면별: r250-349 381회 85% · r350-449 1192회 83% · r450+ 207회 74%

실패 사례 (110건 중 10건, 기보 확인용):
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

- 이번: 실행 100% · 떨군 진주 991개 중 우리 팀 88% (지목한 아군 60%) · 상대 4% · 지목 아군 끝까지 생존 65% (그 뒤 죽은 원인: 갇힘 57, 희생 41, 아군 머리 2, 박힘(상대 돌진) 7, 돌진 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 90% · 최종 왕 49% (최종 왕이 지목 아군의 자손 66%)
- 상대별: proxy4_elim 116회 91% · proxy4_king 101회 89% · proxy4_swarm 93회 83%
- 지도별: Autarky 86회 94% · Default 16회 88% · Devil 14회 79% · Portals 65회 91% · Prisoners Dilemma 27회 93% · Prisoners Dilemma (10) 5회 60% · Queen Of Spades 15회 53% · Schooltime 9회 78% · Slithery Fight 42회 81% · Trauma 31회 100%
- 국면별: r250-349 35회 91% · r350-449 194회 95% · r450+ 81회 70%

실패 사례 (37건 중 10건, 기보 확인용):
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

- 이번: 한입 100% · 2턴 안 분열 99% · 30라운드 뒤 가족 길이 변화 0.1 (줄지 않음 100%)
- 상대별: proxy4_elim 338회 99% · proxy4_king 336회 99% · proxy4_swarm 341회 98%
- 지도별: Devil 2회 50% · Portals 9회 56% · Prisoners Dilemma (10) 1002회 99% · Trauma 2회 50%
- 국면별: r0-99 203회 100% · r100-249 301회 100% · r250-349 207회 99% · r350-449 201회 99% · r450+ 103회 94%

실패 사례 (12건 중 10건, 기보 확인용):
- proxy4_swarm · Devil · 게임 exp/stack7-a-px4:proxy4_swarm:devil:A:1 · r60 · 드래곤 #38 L4: 한입, 분열(새끼 L3), 30라운드 뒤 가족 길이 변화 -2
- proxy4_swarm · Portals · 게임 exp/stack7-a-px4:proxy4_swarm:portals:A:1 · r131 · 드래곤 #122 L6: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 4
- proxy4_elim · Trauma · 게임 exp/stack7-a-px4:proxy4_elim:trauma:B:1 · r401 · 드래곤 #187 L7: 한입, 분열(새끼 L6), 30라운드 뒤 가족 길이 변화 -7
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_king:prisoners_dilemma_10:B:2 · r499 · 드래곤 #351 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_swarm:prisoners_dilemma_10:A:2 · r499 · 드래곤 #346 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_elim · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_elim:prisoners_dilemma_10:A:2 · r499 · 드래곤 #310 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_elim · Portals · 게임 exp/stack7-b-px4:proxy4_elim:portals:A:2 · r287 · 드래곤 #438 L16: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 -16
- proxy4_swarm · Portals · 게임 exp/stack7-a-px4:proxy4_swarm:portals:B:1 · r418 · 드래곤 #548 L13: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 4
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r499 · 드래곤 #368 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_swarm:prisoners_dilemma_10:B:2 · r499 · 드래곤 #380 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 22% · 30라운드 뒤 가족 길이 변화 8.2
- 상대별: proxy4_elim 2721회 98% · proxy4_king 2626회 98% · proxy4_swarm 2680회 98%
- 지도별: Autarky 3078회 100% · Default 67회 96% · Devil 109회 90% · Portals 1758회 94% · Prisoners Dilemma 1440회 99% · Prisoners Dilemma (10) 997회 100% · Queen Of Spades 39회 100% · Schooltime 57회 93% · Slithery Fight 275회 94% · Trauma 202회 93% · Trophy 5회 100%
- 국면별: r0-99 1442회 100% · r100-249 2389회 98% · r250-349 1882회 97% · r350-449 1618회 97% · r450+ 696회 98%

실패 사례 (164건 중 10건, 기보 확인용):
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

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 87% · 그 밖(진짜로 갇힘) 1058회
- 상대별: proxy4_elim 2822회 – · proxy4_king 2746회 – · proxy4_swarm 2711회 –
- 지도별: Autarky 3094회 – · Default 154회 – · Devil 106회 – · Portals 1568회 – · Prisoners Dilemma 1457회 – · Prisoners Dilemma (10) 1005회 – · Queen Of Spades 58회 – · Schooltime 87회 – · Slithery Fight 431회 – · Trauma 288회 – · Trophy 31회 –
- 국면별: r0-99 1526회 – · r100-249 2708회 – · r250-349 1864회 – · r350-449 1519회 – · r450+ 662회 –

## 정책 분열 (split)

- 이번: 분열 100% · 새끼 30라운드 생존 75% · 30라운드 뒤 가족 길이 변화 3.3
- 상대별: proxy4_elim 1회 100% · proxy4_swarm 3회 67%
- 지도별: Default 3회 67% · Queen Of Spades 1회 100%
- 국면별: r100-249 1회 100% · r350-449 3회 67%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_swarm · Default · 게임 exp/stack7-a-px4:proxy4_swarm:default:B:1 · r362 · 드래곤 #144 L5: 새끼 L2 → 새끼 죽음 r388 박힘(상대 돌진), 상대 길이 3, 30라운드 뒤 가족 길이 변화 -3

## 탈출 질주 3칸 (esc)

- 이번: 질주 98% · 짧은 적 머리 4칸 안 72% · 몸 생존 5라운드 96% · 10라운드 96% (드래곤 자체 90%) · 10라운드 길이 변화 -3.3
- 상대별: proxy4_elim 42회 95% · proxy4_king 50회 92% · proxy4_swarm 53회 94%
- 지도별: Default 15회 80% · Devil 8회 100% · Prisoners Dilemma 1회 100% · Queen Of Spades 17회 94% · Schooltime 22회 100% · Slithery Fight 73회 95% · Trauma 6회 83% · Trophy 3회 100%
- 국면별: r0-99 7회 100% · r100-249 28회 93% · r250-349 26회 92% · r350-449 37회 92% · r450+ 47회 96%

실패 사례 (9건 중 9건, 기보 확인용):
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_swarm:slithery_fight:A:1 · r456 · 드래곤 #183 L7: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r459 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_elim:slithery_fight:A:1 · r219 · 드래곤 #569 L8: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r220 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:A:2 · r282 · 드래곤 #115 L6: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r282 돌진, 상대 길이 2
- proxy4_king · Queen Of Spades · 게임 exp/stack7-b-px4:proxy4_king:queen_of_spades_b:B:2 · r367 · 드래곤 #65 L6: 질주 3칸 (가장 가까운 짧은 적 머리 10칸) → 죽음 r375 희생
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:A:2 · r315 · 드래곤 #505 L16: 질주 3칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r319 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:A:2 · r374 · 드래곤 #122 L7: 질주 3칸 (가장 가까운 짧은 적 머리 2칸) → 죽음 r376 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Default · 게임 exp/stack7-b-px4:proxy4_elim:default:A:2 · r487 · 드래곤 #164 L7: 질주 2칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r489 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-a-px4:proxy4_swarm:slithery_fight:B:1 · r228 · 드래곤 #16 L23: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r228 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:B:2 · r394 · 드래곤 #121 L7: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r394 적 몸통, 상대 길이 8

## 위협 피하기 2칸 질주

- 이번: 질주 99% · 몸 10라운드 생존 94% (드래곤 자체 90%)
- 상대별: proxy4_elim 465회 92% · proxy4_king 392회 93% · proxy4_swarm 421회 94%
- 지도별: Autarky 53회 98% · Default 183회 89% · Devil 105회 96% · Prisoners Dilemma 3회 100% · Prisoners Dilemma (10) 10회 100% · Queen Of Spades 158회 95% · Schooltime 261회 93% · Slithery Fight 393회 93% · Trauma 42회 90% · Trophy 70회 90%
- 국면별: r0-99 282회 95% · r100-249 446회 93% · r250-349 307회 91% · r350-449 217회 94% · r450+ 26회 92%

실패 사례 (88건 중 10건, 기보 확인용):
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

- 이번: 미탐색 출구 2212회(몸 3라운드 생존 93%) · 전체 몸 생존 3라운드 94% (드래곤 자체 79%) · 10라운드 88% · 10라운드 안 먹은 진주 0.9
- 상대별: proxy4_elim 1754회 94% · proxy4_king 2070회 94% · proxy4_swarm 1604회 92%
- 지도별: Autarky 795회 94% · Default 1306회 95% · Portals 2136회 93% · Prisoners Dilemma 70회 97% · Prisoners Dilemma (10) 42회 100% · Queen Of Spades 120회 79% · Schooltime 192회 91% · Slithery Fight 327회 94% · Trauma 434회 97% · Trophy 6회 67%
- 국면별: r0-99 632회 96% · r100-249 2199회 94% · r250-349 1636회 93% · r350-449 827회 91% · r450+ 134회 98%

실패 사례 (347건 중 10건, 기보 확인용):
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

- 이번: 충돌 성사 100% (인접 27, 경로 56) · 잡은 길이 ≥ 우리 99% · 두 몸의 진주 우리 202 대 상대 381
- 상대별: proxy4_elim 24회 50% · proxy4_king 17회 29% · proxy4_swarm 42회 29%
- 지도별: Autarky 1회 0% · Default 7회 29% · Devil 7회 57% · Queen Of Spades 7회 43% · Schooltime 24회 13% · Slithery Fight 33회 48% · Trauma 4회 25%
- 국면별: r0-99 4회 25% · r100-249 17회 35% · r250-349 27회 15% · r350-449 27회 44% · r450+ 8회 75%

실패 사례 (54건 중 10건, 기보 확인용):
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
- 상대별: proxy4_elim 119회 100% · proxy4_king 113회 100% · proxy4_swarm 90회 100%
- 지도별: Autarky 12회 100% · Default 51회 100% · Devil 21회 100% · Portals 39회 100% · Prisoners Dilemma (10) 1회 100% · Queen Of Spades 31회 100% · Schooltime 41회 100% · Slithery Fight 98회 100% · Trauma 10회 100% · Trophy 18회 100%
- 국면별: r0-99 52회 100% · r100-249 109회 100% · r250-349 75회 100% · r350-449 70회 100% · r450+ 16회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 92%
- 상대별: proxy4_elim 72회 – · proxy4_king 48회 – · proxy4_swarm 49회 –
- 지도별: Autarky 5회 – · Default 13회 – · Devil 15회 – · Queen Of Spades 26회 – · Schooltime 30회 – · Slithery Fight 63회 – · Trauma 8회 – · Trophy 9회 –
- 국면별: r0-99 27회 – · r100-249 54회 – · r250-349 40회 – · r350-449 37회 – · r450+ 11회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 15회 – · proxy4_king 29회 – · proxy4_swarm 22회 –
- 지도별: Autarky 1회 – · Default 10회 – · Devil 20회 – · Queen Of Spades 3회 – · Schooltime 5회 – · Slithery Fight 17회 – · Trauma 8회 – · Trophy 2회 –
- 국면별: r0-99 11회 – · r100-249 39회 – · r250-349 6회 – · r350-449 9회 – · r450+ 1회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/stack7-a-px4+exp/stack7-b-px4` | 120 | 53 (0.44) | 47% | 0 (0.00) | 0 (0.00) | 16 | 35 | 1 | 3/7 (5.3) | 177 (1.48; 필사 43) | 29/91 (50.8) |
| · exp/stack7-a-px4 | 60 | 26 (0.43) | 35% | 0 (0.00) | 0 (0.00) | 9 | 16 | 0 | 2/5 (7) | 84 (1.40; 필사 21) | 16/51 (56) |
| · exp/stack7-b-px4 | 60 | 27 (0.45) | 59% | 0 (0.00) | 0 (0.00) | 7 | 19 | 1 | 1/2 (3.5) | 93 (1.55; 필사 22) | 13/40 (45.5) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.
- 이번 `exp/stack7-a-px4+exp/stack7-b-px4`: gx 표식 턴 787 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- · exp/stack7-a-px4: gx 표식 턴 333 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- · exp/stack7-b-px4: gx 표식 턴 454 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/stack7-a-px4+exp/stack7-b-px4` | 120 | 78827 | 0.8% (605) | 15.9% (12564) | 8616 | 1.3% (108) | 3.0% (260) | 24.2% (2088/8616) |
| · exp/stack7-a-px4 | 60 | 40628 | 0.7% (277) | 14.7% (5965) | 4455 | 1.3% (57) | 3.1% (139) | 23.5% (1046/4455) |
| · exp/stack7-b-px4 | 60 | 38199 | 0.9% (328) | 17.3% (6599) | 4161 | 1.2% (51) | 2.9% (121) | 25.0% (1042/4161) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/stack7-a-px4+exp/stack7-b-px4` | 전체 | 분열 | 17 (17%) | 10.6 | 135% | 154% | 11 | 0 |
| 이번 `exp/stack7-a-px4+exp/stack7-b-px4` | 전체 | 2칸 질주 | 32 (32%) | 11.8 | 89% | 78% | 11 | 5 |
| 이번 `exp/stack7-a-px4+exp/stack7-b-px4` | 전체 | 3칸 질주 | 15 (15%) | 13.7 | 79% | 79% | 5 | 1 |
| 이번 `exp/stack7-a-px4+exp/stack7-b-px4` | 전체 | 한 걸음 | 36 (36%) | 10.2 | 49% | 51% | 28 | 17 |
| 이번 `exp/stack7-a-px4+exp/stack7-b-px4` | 4칸 이상 | 분열 | 12 (21%) | 11.5 | 149% | 172% | 8 | 0 |
| 이번 `exp/stack7-a-px4+exp/stack7-b-px4` | 4칸 이상 | 2칸 질주 | 18 (32%) | 13.3 | 91% | 81% | 5 | 3 |
| 이번 `exp/stack7-a-px4+exp/stack7-b-px4` | 4칸 이상 | 3칸 질주 | 9 (16%) | 14.8 | 87% | 91% | 2 | 0 |
| 이번 `exp/stack7-a-px4+exp/stack7-b-px4` | 4칸 이상 | 한 걸음 | 17 (30%) | 10.5 | 44% | 42% | 13 | 9 |
| · exp/stack7-a-px4 | 전체 | 분열 | 9 (17%) | 10.6 | 165% | 198% | 7 | 0 |
| · exp/stack7-a-px4 | 전체 | 2칸 질주 | 14 (26%) | 14.4 | 95% | 80% | 5 | 0 |
| · exp/stack7-a-px4 | 전체 | 3칸 질주 | 11 (20%) | 14.9 | 88% | 89% | 1 | 0 |
| · exp/stack7-a-px4 | 전체 | 한 걸음 | 20 (37%) | 10.5 | 56% | 59% | 14 | 10 |
| · exp/stack7-a-px4 | 4칸 이상 | 분열 | 8 (26%) | 10.9 | 172% | 200% | 6 | 0 |
| · exp/stack7-a-px4 | 4칸 이상 | 2칸 질주 | 8 (26%) | 17.6 | 91% | 78% | 2 | 0 |
| · exp/stack7-a-px4 | 4칸 이상 | 3칸 질주 | 8 (26%) | 15 | 93% | 96% | 1 | 0 |
| · exp/stack7-a-px4 | 4칸 이상 | 한 걸음 | 7 (23%) | 11.9 | 46% | 39% | 5 | 4 |
| · exp/stack7-b-px4 | 전체 | 분열 | 8 (17%) | 10.6 | 101% | 106% | 4 | 0 |
| · exp/stack7-b-px4 | 전체 | 2칸 질주 | 18 (39%) | 9.7 | 82% | 77% | 6 | 5 |
| · exp/stack7-b-px4 | 전체 | 3칸 질주 | 4 (9%) | 10.3 | 39% | 39% | 4 | 1 |
| · exp/stack7-b-px4 | 전체 | 한 걸음 | 16 (35%) | 9.9 | 41% | 40% | 14 | 7 |
| · exp/stack7-b-px4 | 4칸 이상 | 분열 | 4 (16%) | 12.8 | 110% | 124% | 2 | 0 |
| · exp/stack7-b-px4 | 4칸 이상 | 2칸 질주 | 10 (40%) | 9.8 | 91% | 86% | 3 | 3 |
| · exp/stack7-b-px4 | 4칸 이상 | 3칸 질주 | 1 (4%) | 13 | 31% | 46% | 1 | 0 |
| · exp/stack7-b-px4 | 4칸 이상 | 한 걸음 | 10 (40%) | 9.5 | 43% | 44% | 8 | 5 |

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (177건 중 10건):
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

이번 (120판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 12 | 100% | 100% | 72/72 (72) | 3379 | 3379 (0) | 0 | 0 | 0 | 0 |
| Default a | 12 | 100% | 100% | 48/48 (48) | 470 | 468 (0) | 0 | 0 | 0 | 0 |
| Devil a | 6 | 100% | 100% | 18/18 (18) | 170 | 170 (0) | 0 | 0 | 0 | 19 |
| Devil b | 6 | 100% | 100% | 18/18 (18) | 121 | 121 (0) | 0 | 0 | 0 | 17 |
| Portals a | 12 | 100% | 100% | 36/36 (36) | 1952 | 1951 (0) | 0 | 1 | 0 | 1 |
| Prisoners Dilemma a | 6 | 100% | 100% | 6/18 (6) | 1507 | 1502 (0) | 5 | 0 | 0 | 162 |
| Prisoners Dilemma b | 6 | 100% | 100% | 18/30 (18) | 1046 | 1041 (0) | 5 | 0 | 0 | 438 |
| Queen Of Spades a | 6 | 100% | 100% | 12/12 (12) | 127 | 126 (0) | 1 | 0 | 0 | 45 |
| Queen Of Spades b | 6 | 100% | 100% | 12/12 (12) | 59 | 57 (0) | 2 | 0 | 0 | 86 |
| Schooltime a | 6 | 100% | 100% | 18/18 (18) | 247 | 245 (0) | 0 | 0 | 0 | 11 |
| Schooltime b | 6 | 100% | 100% | 36/36 (36) | 95 | 95 (0) | 0 | 0 | 0 | 7 |
| Slithery Fight a | 6 | 100% | 100% | 48/48 (48) | 474 | 466 (0) | 8 | 0 | 0 | 42 |
| Slithery Fight b | 6 | 100% | 100% | 48/48 (48) | 410 | 400 (0) | 10 | 0 | 0 | 49 |
| Trauma a | 12 | 100% | 100% | 24/24 (24) | 479 | 479 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 12 | 100% | 100% | 24/24 (24) | 152 | 151 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 120/120, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

### Schooltime 판의 경제 (bsp의 가설 수준 지표, 정답 판본별)

| 묶음 | 판본 | 판 | 드래곤 수 r50 | r100 | r0–99 자연 진주 먹음 | 전멸당함 | 끝 최장(전멸 0) | 판당 bsp 분열 |
|---|---|---:|---|---|---|---:|---|---:|
| 이번 | a | 6 | 9 [8, 9] | 18 [13, 18] | 34 [20, 35] | 0% | 34 [12, 35] | 0 |
| 이번 | b | 6 | 8 [7, 8] | 9 [9, 11] | 12 [10, 15] | 0% | 12 [7, 13] | 8.8 |

- 기준값(`research/experiments/cand-mapid.md`, 웨이브 전에 적음): b에서 드래곤 수 r50 중앙 ≥ 6, r0–99 자연 진주 중앙 ≥ 14. 우리 merge2 계열 b 29판은 3 · 9, 떼 계열(swarm8·px) b 14판은 6 · 14, 상위권 b 승자는 8 · 32다. a는 bsp가 켜지지 않는 대조군이다.

## stack5: 영토 덮기 (csplit · F · cov) 게이트와 가설 수준 지표

- 기준값은 `research/experiments/cand-stack5.md`(웨이브 전)에서, 상위권 승자(TW) 값과 merge2 값은 `research/observations/top-territory.md`에서 왔다. 정의는 영토 연구의 `exp/territory-analysis/extract.js`와 같다(영토 = 시작 몸에서 더 가까운 팀의 칸, 샘 = 그 판 판본 파일의 평균 간격 ≤12, 보로노이 = 용량 1/평균 간격 가중, 거리 = 지도 위 이동 거리, 몸은 무시).

### 게이트 (기능 적용)

| 지표 | 기준 | 이번 |
|---|---|---|
| csplit 발동: 500라운드형 지도 r0–249 판당 | ≥20 | 21.6 (전체 2045회) |
| csplit 설계 상황: 부모가 팀 최장(≥8)이 아님 | ≥90% | 100% |
| csplit 새끼가 30라운드 안에 자연 진주 ≥1개 | ≥45% (TW 47% · 45%) | 40% (2045마리) |
| csplit 새끼 30라운드 생존 | ≥30% (TW 34% · 51%) | 73% |
| F 목표(드래곤·샘) 수, 3걸음 안 도착 | – | 4586, 도착 51% |
| F 설계 상황: 실제 우리 영토 샘, 처음 표식 때 다른 우리 머리 3걸음 안 없음 | ≥80% | 76% |
| F 도착 뒤 30라운드 그 무리 자연 진주의 우리 몫(합산) | ≥85% (TW 자기 샘 90%) | 96% (상대 3%, 15283개) |
| F 같은 몫의 지도 평균(지도마다 합산, 같은 무게, Portals 제외) | ≥85% | 83% (Autarky 100%, Devil 59%, Prisoners Dilemma 100%, Trauma 92%, Slithery Fight 46%, Prisoners Dilemma (10) 100%) |

### 가설 수준 지표 (관찰; 500라운드형 / 전멸형)

| 지표 | 기준 | 상위권 승자 | merge2 | 이번 |
|---|---|---|---|---|
| r100 우리 드래곤 수(r100까지 간 판) | ≥15 / ≥10 | 30 / 21 | 4 / 3 | 12.2 / 6.6 |
| r100 우리 영토 보로노이 몫(용량 가중, 판 평균) | ≥80% | 89% / 81% | 66% / 32% | 71% / 35% |
| r100 샘 지킴: 우리 영토 샘 중 우리 머리 3걸음 안(판 평균) | ≥50% | 61% / 55% | 22% / – | 31% / 48% |
| 우리 영토 자연 진주(r0부터 생성)를 상대가 먹은 몫(합산) | ≤25% | 11% / 16% | 56% / 55% | 52% / 61% |
| 우리 영토 샘 진주를 상대가 먹은 몫(합산) | ≤15% | 7% / 6% | 50% / 33% | 46% / 48% |

- 판 수(500라운드형 / 전멸형): 이번 60 / 60. 판본 파일을 못 찾은 판: 이번 0.

### 부작용: 우리 드래곤의 죽음 (판당; 전체 / r250 전)

| 원인 | 이번 |
|---|---|
| 갇힘(빈 이웃 없음; 통로 고리의 남은 조각 포함) | 69.9 / 35.6 |
| 적 머리에 박힘 | 7.9 / 5.5 |
| 우리 드래곤끼리 머리 충돌(둘 다 죽음, 둘 다 셈) | 1.9 / 1.1 |

- 막힘에서 아군 머리를 피해 죽은 턴(no-exit s): 이번 221

### 지도별 (이번)

| 지도 | 판 | csplit 판당 | 새끼 먹음 ≥1 | 새끼 30R 생존 | F 목표 · 도착 · 무리 진주 우리 몫 | r100 드래곤 | 보로노이 | 샘 지킴 | 상대가 먹은 영토 진주 | 상대가 먹은 샘 진주 |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| Autarky | 12 | 18.4 | 43% | 89% | 592 · 90% · 100% | 10.6 | 96% | 86% | 8% | 8% |
| Default | 12 | 27.1 | 38% | 62% | 3 · 33% · – | 10 | 35% | – | 71% | – |
| Devil | 12 | 11 | 29% | 75% | 314 · 18% · 59% | 7.9 | 31% | 21% | 83% | 85% |
| Portals | 12 | 13.2 | 49% | 59% | 1393 · 35% · 100% | 11.3 | 100% | 38% | 0% | 0% |
| Prisoners Dilemma (10) | 6 | 3.2 | 37% | 95% | 97 · 62% · 100% | 3.8 | 46% | 50% | 23% | 0% |
| Prisoners Dilemma | 6 | 8.2 | 47% | 94% | 1051 · 89% · 100% | 3.7 | 99% | 100% | 3% | 1% |
| Queen Of Spades | 12 | 8.6 | 41% | 81% | 21 · 19% · – | 3.5 | 15% | – | 78% | – |
| Schooltime | 12 | 15.1 | 46% | 86% | 11 · 0% · – | 12.6 | 37% | 0% | 80% | 0% |
| Slithery Fight | 12 | 42.2 | 32% | 74% | 922 · 22% · 46% | 20.3 | 30% | 9% | 76% | 81% |
| Trauma | 12 | 19.2 | 43% | 54% | 167 · 25% · 92% | 6.1 | 94% | 7% | 55% | 1% |
| Trophy | 12 | 10.1 | 46% | 76% | 15 · 47% · – | 8 | 19% | – | 69% | – |

## stack7: 수 바닥 분열(floor)과 왕 길이 상한(kcap) 게이트, 저수 에피소드, 가설 수준 지표, 지도 가르기

- 기준값은 `research/experiments/cand-stack7.md`(웨이브 전)에서, 상위권·우리 값은 `research/observations/our-eliminations.md`(2.6절, 1.3절, 2.2절)에서 왔다. 저수 에피소드와 부류의 정의는 전멸 연구(`exp/eliminations/top.js` I, `lib.js` classOf)와 같다: r50부터 5라운드 간격으로 처음 우리 수 1–3·상대 ≥8인 라운드 r(라운드 첫 턴의 수; r+20이 판 안이고 우리 전멸 전), 그 뒤 [r, r+20) 분열, 20라운드 뒤 4마리 이상이면 회복, 50라운드 안 전멸. 연구의 분열 수는 10라운드 칸 두 개의 전체 분열(탈출 분열 포함)이고, 여기서는 [r, r+20)을 그대로 센다.

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 |
|---|---|---|---|
| floor | 발동(판당; floor 지도 판) | – | 72 (0.9; 84판) |
| floor | 1. 설계 상황: 발동 때 상대 ≥8마리 | ≥90% | 92% |
| floor | 저수 에피소드가 있는 floor 지도 판 · 그 20라운드 안 floor 발동이 있었던 판 | (관찰) | 62 · 23% |
| floor | 2. 즉시 효과 A: 에피소드 20라운드 비탈출 분열(판당; floor 지도) | ≥2.0 (상위 LX·LS 2.0, 우리 0.5) | 0.3 (floor 0.3, kcap 0, csplit 0; 탈출 포함 전체 0.6) |
| floor | 3. 즉시 효과 B: 에피소드 20라운드 뒤 4마리 이상(floor 지도) | ≥23% (상위 LX 23%, LS 26%, 우리 5%) | 23% (14/62) |
| floor | 4. 즉시 효과 C: floor 새끼 30라운드 생존 | ≥34% (상위 패자 제 영토 새끼 34%, 승자 51%) | 65% (72마리) |
| kcap | 발동(판당; kcap 지도 판) | – | 12 (0.2; 72판) |
| kcap | 1. 설계 상황: 부모가 그 순간 팀 최장이고 r250 전 | ≥90% | 100% |
| kcap | 2. 즉시 효과: 새끼 10라운드 생존 | ≥74% (상위권 길이 4 분열 74.2%) | 58% (12마리) |
| kcap | 2. 즉시 효과: 부모 10라운드 생존 | ≥55% (상위권 54.5%) | 58% |

### 저수 에피소드 (floor 지도 / 모든 지도; 판정은 floor 지도)

| 묶음 | 지도 | 판 | 에피소드 있음 | 처음 라운드(중앙) | 그때 우리 수 · 상대 수 | 그때 총길이 · 최장 | 20라운드 비탈출 분열 | floor · kcap | 탈출 포함 전체 | 20라운드 뒤 4마리 이상 | 50라운드 안 전멸 |
|---|---|---:|---:|---:|---|---|---:|---|---:|---:|---:|
| 이번 | floor 지도 | 84 | 74% | 322.5 | 2.9 · 29.7 | 13.5 · 7.4 | 0.3 | 0.3 · 0 | 0.6 | 23% | 10% |
| 이번 | floor 지도 중 전멸형 | 48 | 83% | 170 | 2.9 · 29.4 | 8.2 · 3.8 | 0.3 | 0.2 · 0 | 0.4 | 20% | 15% |
| 이번 | floor 지도 중 500형 | 36 | 61% | 415 | 3 · 30.2 | 23 · 13.9 | 0.4 | 0.4 · 0 | 0.9 | 27% | 0% |
| 이번 | 끄는 지도(Autarky·PD·Portals) | 36 | 56% | 367.5 | 2.9 · 20.1 | 29.2 · 17.2 | 0.2 | 0 · 0 | 8.8 | 20% | 0% |
| 이번 | 모든 지도 | 120 | 68% | 342.5 | 2.9 · 27.3 | 17.3 · 9.8 | 0.3 | 0.2 · 0 | 2.6 | 22% | 7% |

- 상위권 기준(전멸 연구 2.6절, 전멸형): LX 72%가 그런 때를 겪고(처음 r105) 20라운드에 2.0번 나누며 23%가 회복, 42%가 50라운드 안 전멸. LS 69%, 2.0번, 26%, 0%. 우리 g4 LX 95%(r50), 0.5번, 5%, 15%.

### 가설 수준 지표 (관찰)

| 기능 | 지표 | 기준 | 상위권 · 이전 우리 | 이번 |
|---|---|---|---|---|
| floor | r100 우리 드래곤 수(전멸형; 전멸은 0) — 전멸형 5지도 / PD 뺀 4지도 | ≥5.5 | 상위 LX 5.5, 우리 g4 LX 2.5 | 6.6 / 7.4 |
| floor | 전멸률(전멸형) | ≤66% | swarm8 66%, merge2 78% | 25% (15/60) / 31% (15/48) |
| floor | 전멸 라운드 중앙(전멸형) | ≥r235 | swarm8 235, merge2 150, stack1–3 163 | 181 / 181 |
| kcap | 우리 전멸 중 E2(왕 사냥) 비율(모든 지도) | ≤8% | 상위 LX 6%, 우리 16% | 0% (E1 0 · E2 0 · E3m 13 · E3l 2) |
| kcap | r50 우리 최장 평균(전멸형; 전멸은 0) — 5지도 / 4지도 | ≤4.5 | 상위 LS 3.8, 우리 g4 LX 6.8 | 5.2 / 3.5 |
| kcap | 전멸한 판의 길이 ≥8 죽음(판당; 모든 지도) | ≤0.4 | 우리 0.75 | 0.1 (15판) |

### 지도 가르기 (map= 표식으로 확인)

- floor는 Trophy, Queen Of Spades, Devil, Default, Schooltime, Trauma, Slithery Fight에서만, kcap은 그중 Slithery Fight를 뺀 여섯에서만 켠다. 봇은 프로세스마다 자기 창으로 지도 가족을 인식하고(`map=` 표식), 인식 전·`none`이면 끈다. "표식이 켜는 가족이 아닌 발동"은 발동한 프로세스의 마지막 `map=` 표식이 그 기능을 켜는 가족을 대지 않은 발동이다(0이어야 한다). "인식한 프로세스"는 마지막 표식이 그 판의 참 지도 가족을 댄 프로세스다.

| 묶음 | 지도(정답 판본) | 판 | floor 발동 | kcap 발동 | 표식이 켜는 가족이 아닌 발동 | 인식한 프로세스 |
|---|---|---:|---:|---:|---:|---:|
| 이번 | Autarky (끔) | 12 | 0 | 0 | 0 | 100% (3379/3379) |
| 이번 | Default | 12 | 19 | 4 | 0 | 100% (468/470) |
| 이번 | Devil a | 6 | 8 | 0 | 0 | 100% (170/170) |
| 이번 | Devil b | 6 | 6 | 0 | 0 | 100% (121/121) |
| 이번 | Portals (끔) | 12 | 0 | 0 | 0 | 100% (1951/1952) |
| 이번 | Prisoners Dilemma (10) (끔) | 6 | 0 | 0 | 0 | 100% (1046/1046) |
| 이번 | Prisoners Dilemma (끔) | 6 | 0 | 0 | 0 | 100% (1507/1507) |
| 이번 | Queen Of Spades a | 6 | 10 | 3 | 0 | 100% (127/127) |
| 이번 | Queen Of Spades b | 6 | 3 | 1 | 0 | 100% (59/59) |
| 이번 | Schooltime a | 6 | 12 | 0 | 0 | 99% (245/247) |
| 이번 | Schooltime b | 6 | 2 | 0 | 0 | 100% (95/95) |
| 이번 | Slithery Fight a (kcap 끔) | 6 | 2 | 0 | 0 | 100% (474/474) |
| 이번 | Slithery Fight b (kcap 끔) | 6 | 1 | 0 | 0 | 100% (410/410) |
| 이번 | Trauma | 12 | 9 | 2 | 0 | 100% (479/479) |
| 이번 | Trophy | 12 | 0 | 2 | 0 | 99% (151/152) |

