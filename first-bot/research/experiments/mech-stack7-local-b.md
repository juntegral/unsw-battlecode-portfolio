# 구현 적용 확인

- 대상: `exp/stack7-b-px4` 60판
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
| 수 바닥 분열 (split floor, stack7) | 23 (0.4) | 74% | 
| 왕 길이 상한 분열 (split kcap, stack7) | 4 (0.1) | 75% | 
| 지도·판본 인식 (map=, cand-mapid; 판 단위) | 60 (1) | 100% | 
| Schooltime b 초반 분열 (split bsp, cand-mapid) | 53 (0.9) | 94% | 
| 덮기 분열 (csplit, stack5) | 944 (15.7) | 39% | 
| 샘 지킴 (F, stack5; 드래곤·샘 단위) | 1774 (29.6) | 88% | 
| 위협 모형 빈틈 (tg, stack4) | 13425 (223.8) | 98% | 
| 모이기 시작 제한 (gx, stack4; 드래곤 단위) | 79 (1.3) | 99% | 
| 큰 아군 곁 희생 (conv, stack1 M1) | 158 (2.6) | 99% | 
| 조각 떼기 (split frag, stack2 S1) | 19 (0.3) | 74% | 
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 2340 (39) | 79% | 
| 왕에게 모이기 (g, 드래곤 단위) | 941 (15.7) | 80% | 
| 희생 먹이기 (feed) | 144 (2.4) | 86% | 
| 막다른 길 한입 (pocket-eat) | 1007 (16.8) | 99% | 
| 탈출 분열 (escape-split) | 3834 (63.9) | 97% | 
| 출구 없음 (no-exit) | 3932 (65.5) | – | 
| 정책 분열 (split) | 2 (0) | 100% | 
| 탈출 질주 3칸 (esc) | 78 (1.3) | 92% | 
| 위협 피하기 2칸 질주 | 646 (10.8) | 93% | 
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 2939 (49) | 94% | 
| 돌진 (TRADE) | 32 (0.5) | 41% | 
| 먹이 질주 (2칸 이상, 먹은 것) | 143 (2.4) | 100% | 
| 기타 2칸 질주 | 82 (1.4) | – | 
| 마지막 돌진 (last-trade) | 35 (0.6) | – | 

- 건강: 턴 222396, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 8940턴 · 끝판(late) 4708턴 · 돌진 신뢰(T, 탈출 끔) 32턴, 그 직후 박혀 죽음 0

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 
|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 2% (46/2642턴) | 
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 40.4칸 (9.2회), 진주 우리 92% · 상대 2% | 
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 0칸 (판당 0.00회) | 
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 25% (1042/4161턴) | 
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.033회 (2건, 25칸) | 
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 6.5마리 (30판) | 
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 18.9회 | 
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 47% (우리 47%) | 
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 6.1 대 상대 19.4 (7.5회) · 박힌 교환의 우리 몫 20% (190회) | 
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 7.4개 | 

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 수 바닥 분열 (split floor, stack7)

- 이번: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 96% · 적 머리가 7×7 시야 안 43% · 부모 길이 평균 5 · 우리 수(표식) 평균 2.7 · 상대 수 평균 26.3 · 새끼 10라운드 생존 96% · 30라운드 74% · 부모 10라운드 생존 91% · 30라운드 74% · 새끼 30라운드 안 1개 이상 먹음 52% · 30라운드 뒤 가족 길이 변화 3.3 · 30라운드 안 새끼가 죽은 원인: 희생 3, 갇힘 2, 박힘(상대 돌진) 1
- 상대별: proxy4_elim 11회 73% · proxy4_king 4회 75% · proxy4_swarm 8회 75%
- 지도별: Default 7회 86% · Devil 6회 83% · Queen Of Spades 3회 100% · Schooltime 2회 50% · Slithery Fight 1회 0% · Trauma 4회 50%
- 국면별: r0-99 1회 100% · r100-249 3회 67% · r250-349 8회 100% · r350-449 11회 55%

실패 사례 (6건 중 6건, 기보 확인용):
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:A:2 · r438 · 드래곤 #388 L4: 우리 3마리 · 상대 21마리 · 새끼 L2 → 새끼 죽음 r463 희생, 부모 10라운드 생존 · 표식 map=Slithery_Fight/b
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:A:2 · r165 · 드래곤 #46 L5: 우리 3마리 · 상대 14마리 · 새끼 L2 → 새끼 죽음 r171 갇힘, 부모 10라운드 생존 · 표식 map=Trauma/a
- proxy4_elim · Default · 게임 exp/stack7-b-px4:proxy4_elim:default:A:2 · r426 · 드래곤 #164 L7: 우리 3마리 · 상대 17마리 · 새끼 L2 → 새끼 죽음 r450 박힘(상대 돌진), 상대 길이 2, 부모 10라운드 생존 · 표식 map=Default/a
- proxy4_elim · Devil · 게임 exp/stack7-b-px4:proxy4_elim:devil_b:A:2 · r381 · 드래곤 #395 L4: 우리 3마리 · 상대 9마리 · 새끼 L2 → 새끼 죽음 r397 갇힘, 부모 10라운드 생존 · 표식 map=Devil/b
- proxy4_elim · Schooltime · 게임 exp/stack7-b-px4:proxy4_elim:schooltime_b:A:2 · r427 · 드래곤 #12 L4: 우리 3마리 · 상대 30마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r447 희생, 부모 10라운드 생존 · 표식 map=Schooltime/b
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:A:2 · r389 · 드래곤 #89 L5: 우리 2마리 · 상대 28마리 · 새끼 L2 → 새끼 죽음 r419 희생, 부모 10라운드 죽음 · 표식 map=Trauma/a

## 왕 길이 상한 분열 (split kcap, stack7)

- 이번: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 25% · 부모 길이 평균 8.8 · 우리 수(표식) 평균 4.8 · 상대 수 평균 18.8 · 새끼 10라운드 생존 75% · 30라운드 50% · 부모 10라운드 생존 75% · 30라운드 50% · 새끼 30라운드 안 1개 이상 먹음 50% · 30라운드 뒤 가족 길이 변화 5 · 30라운드 안 새끼가 죽은 원인: 박힘(상대 돌진) 1, 갇힘 1
- 상대별: proxy4_elim 1회 100% · proxy4_king 1회 100% · proxy4_swarm 2회 50%
- 지도별: Default 2회 100% · Queen Of Spades 1회 100% · Trauma 1회 0%
- 국면별: r0-99 1회 100% · r100-249 3회 67%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:A:2 · r164 · 드래곤 #46 L7: 우리 4마리 · 상대 15마리 · 새끼 L2 → 새끼 죽음 r164 갇힘, 상대 길이 3, 부모 10라운드 생존 · 표식 map=Trauma/a

## 지도·판본 인식 (map=, cand-mapid; 판 단위)

- 이번: 판본을 기보로 가릴 수 있는 판 60/60 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 95%, 그중 정답 100% · 프로세스 5101: 표식 없음 2, 결정 5081 (정답 100%, 틀림 0), 가족만 17, 모름 1, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 438라운드
- 상대별: proxy4_elim 20회 100% · proxy4_king 20회 100% · proxy4_swarm 20회 100%
- 지도별: Autarky a 6회 100% · Default a 6회 100% · Devil b 6회 100% · Portals a 6회 100% · Prisoners Dilemma b 6회 100% · Queen Of Spades b 6회 100% · Schooltime b 6회 100% · Slithery Fight b 6회 100% · Trauma a 6회 100% · Trophy a 6회 100%
- 국면별: r0-99 60회 100%

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

- 이번: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 99% · 적 머리가 시야에 있을 때 36% · 부모가 스스로 최장이라 믿음(k) 71% · 새끼 30라운드 안 자연 진주 ≥1 39% (500형 40% · 전멸형 38%; 기준 ≥45%) · 새끼 30라운드 생존 71% (500형 69% · 전멸형 73%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 87% · 새끼 30라운드 안 자연 진주 평균 0.9 · 30라운드 안 죽은 원인: 갇힘 198, 아군 머리 16, 박힘(상대 돌진) 50, 돌진 11, 적 몸통 1
- 상대별: proxy4_elim 368회 43% · proxy4_king 291회 37% · proxy4_swarm 285회 36%
- 지도별: Autarky 123회 38% · Default 178회 42% · Devil 60회 25% · Portals 79회 44% · Prisoners Dilemma (10) 19회 37% · Queen Of Spades 32회 19% · Schooltime 20회 30% · Slithery Fight 219회 37% · Trauma 136회 47% · Trophy 78회 46%
- 국면별: r0-99 436회 43% · r100-249 508회 36%

실패 사례 (574건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:B:2 · r1 · 드래곤 #1 L4: 새끼 L2, 적 머리 시야 안 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:A:2 · r50 · 드래곤 #10 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/stack7-b-px4:proxy4_king:devil_b:A:2 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/stack7-b-px4:proxy4_king:portals:A:2 · r5 · 드래곤 #4 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_king:prisoners_dilemma_10:B:2 · r168 · 드래곤 #3 L4: 새끼 L2, 적 머리 시야 안 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack7-b-px4:proxy4_king:queen_of_spades_b:A:2 · r37 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/stack7-b-px4:proxy4_king:schooltime_b:A:2 · r169 · 드래곤 #2 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/stack7-b-px4:proxy4_king:trauma:A:2 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:A:2 · r3 · 드래곤 #31 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trophy · 게임 exp/stack7-b-px4:proxy4_king:trophy:A:2 · r25 · 드래곤 #5 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0

## 샘 지킴 (F, stack5; 드래곤·샘 단위)

- 이번: 목표 1774개(표식 턴 21411) · 설계 상황 70% (실제 샘 99%, 우리 영토 84%, 처음에 다른 우리 머리 3걸음 안 없음 86%; 기준 ≥80%) · 3걸음 안 도착 37% · 도착 뒤 30라운드 그 무리 자연 진주 3565개 중 우리 91% · 상대 9% (합산 기준 ≥85%) · 처음 거리 평균 7.6
- 상대별: proxy4_elim 594회 82% · proxy4_king 543회 89% · proxy4_swarm 637회 91%
- 지도별: Autarky 233회 99% · Default 3회 – · Devil 163회 46% · Portals 727회 100% · Prisoners Dilemma (10) 97회 100% · Queen Of Spades 8회 – · Slithery Fight 440회 30% · Trauma 98회 88% · Trophy 5회 –
- 국면별: r0-99 622회 74% · r100-249 693회 93% · r250-349 459회 98%

실패 사례 (76건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:A:2 · r41 · 드래곤 #4 L2: 샘 (19,1) 처음 거리 13 → r70 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2
- proxy4_king · Devil · 게임 exp/stack7-b-px4:proxy4_king:devil_b:B:2 · r40 · 드래곤 #9 L2: 샘 (26,15) 처음 거리 13 → r51 도착, 30라운드 무리 진주 3개 중 우리 2 · 상대 1
- proxy4_king · Trauma · 게임 exp/stack7-b-px4:proxy4_king:trauma:A:2 · r196 · 드래곤 #2 L4: 샘 (11,14) 처음 거리 5 → r200 도착, 30라운드 무리 진주 3개 중 우리 0 · 상대 0
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:A:2 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_swarm · Devil · 게임 exp/stack7-b-px4:proxy4_swarm:devil_b:A:2 · r36 · 드래곤 #16 L2: 샘 (15,1) 처음 거리 6 → r42 도착, 30라운드 무리 진주 14개 중 우리 0 · 상대 14
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_elim · Devil · 게임 exp/stack7-b-px4:proxy4_elim:devil_b:A:2 · r35 · 드래곤 #4 L3: 샘 (14,7) 처음 거리 3 → r38 도착, 30라운드 무리 진주 6개 중 우리 0 · 상대 6
- proxy4_elim · Trauma · 게임 exp/stack7-b-px4:proxy4_elim:trauma:A:2 · r331 · 드래곤 #106 L5: 샘 (11,10) 처음 거리 2 → r331 도착, 30라운드 무리 진주 6개 중 우리 3 · 상대 0
- proxy4_elim · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_elim:slithery_fight_b:A:2 · r2 · 드래곤 #8 L2: 샘 (33,1) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r2 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:A:2 · r107 · 드래곤 #6 L2: 샘 (35,16) 처음 거리 7 (설계 밖: 실제 샘 1, 우리 영토 0, 다른 머리 0) → r110 도착, 30라운드 무리 진주 7개 중 우리 0 · 상대 7

## 위협 모형 빈틈 (tg, stack4)

- 이번: 피함(tg) 55% · 위협 칸으로 감(tgx) 6000턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 99% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 98%) · 길이별 L2-5 13141 · L6-9 174 · L10+ 110
- 상대별: proxy4_elim 4175회 98% · proxy4_king 4907회 99% · proxy4_swarm 4343회 98%
- 지도별: Autarky 779회 98% · Default 2243회 98% · Devil 1053회 97% · Portals 5회 100% · Prisoners Dilemma (10) 521회 99% · Queen Of Spades 1090회 99% · Schooltime 2253회 99% · Slithery Fight 3808회 99% · Trauma 259회 97% · Trophy 1414회 97%
- 국면별: r0-99 2339회 98% · r100-249 6144회 98% · r250-349 3439회 99% · r350-449 1263회 99% · r450+ 240회 98%

실패 사례 (228건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:B:2 · r54 · 드래곤 #12 L2: 위협 칸으로 감(tgx), 적 머리 경로 5칸 · 맨해튼 5칸(길이 3) → 박힘 r55 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:A:2 · r189 · 드래곤 #6 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r191 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Devil · 게임 exp/stack7-b-px4:proxy4_king:devil_b:A:2 · r92 · 드래곤 #35 L3: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r94 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_king:prisoners_dilemma_10:B:2 · r216 · 드래곤 #3 L3: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r217 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Queen Of Spades · 게임 exp/stack7-b-px4:proxy4_king:queen_of_spades_b:B:2 · r129 · 드래곤 #40 L3: 피함(tg), 적 머리 경로 2칸 · 맨해튼 2칸(길이 3) → 박힘 r130 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Schooltime · 게임 exp/stack7-b-px4:proxy4_king:schooltime_b:B:2 · r242 · 드래곤 #43 L2: 위협 칸으로 감(tgx), 적 머리 경로 5칸 · 맨해튼 5칸(길이 2) → 박힘 r243 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trauma · 게임 exp/stack7-b-px4:proxy4_king:trauma:A:2 · r246 · 드래곤 #25 L2: 피함(tg), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r248 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:A:2 · r44 · 드래곤 #10 L8: 피함(tg), 적 머리 경로 4칸 · 맨해튼 4칸(길이 2) → 박힘 r44 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trophy · 게임 exp/stack7-b-px4:proxy4_king:trophy:A:2 · r160 · 드래곤 #5 L2: 피함(tg), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r161 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack7-b-px4:proxy4_swarm:default:A:2 · r56 · 드래곤 #4 L2: 피함(tg), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r57 박힘(상대 돌진), 상대 길이 3

## 모이기 시작 제한 (gx, stack4; 드래곤 단위)

- 이번: 드래곤 79 (표식 턴 454) · 몸(자손 포함) 끝까지 99% (기준 ≥80%) · 드래곤 자체 끝까지 생존 57% (참고) · 뒤에 희생 먹이기(feed)로 끝남 3
- 상대별: proxy4_elim 20회 100% · proxy4_king 29회 97% · proxy4_swarm 30회 100%
- 지도별: Autarky 25회 100% · Devil 1회 100% · Portals 29회 100% · Prisoners Dilemma (10) 13회 100% · Schooltime 3회 100% · Slithery Fight 6회 83% · Trauma 2회 100%
- 국면별: r450+ 79회 99%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:B:2 · r490 · 드래곤 #221 L4: gx 1턴 (r490–r490) → 죽음 r492 희생

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 245개 중 우리 팀 99% (지목한 아군 65%) · 상대 0% · 지목 아군 끝까지 생존 32% (그 뒤 죽은 원인: 갇힘 71, 희생 27, 박힘(상대 돌진) 6, 적 몸통 1, 아군 머리 1, 돌진 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 70% · 최종 왕 28% (최종 왕이 지목 아군의 자손 47%)
- 상대별: proxy4_elim 66회 100% · proxy4_king 40회 100% · proxy4_swarm 52회 98%
- 지도별: Autarky 30회 100% · Default 1회 100% · Portals 63회 100% · Prisoners Dilemma (10) 4회 100% · Queen Of Spades 1회 100% · Schooltime 2회 100% · Slithery Fight 32회 100% · Trauma 25회 96%
- 국면별: r250-349 67회 99% · r350-449 84회 100% · r450+ 7회 100%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:B:2 · r328 · 드래곤 #246 L4: #225(L9)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1; 지목 아군 r334 돌진에 사망

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 89% · 조각 30라운드 생존 68% · 30라운드 안 1개 이상 먹음 63% (살아서 먹음 42%) · 평생 먹은 진주 평균 5.2 · 나중에 아군을 먹임 47% (conv 1, feed 8, 분열 뒤 평균 28.3라운드) · 끝까지 생존 26% · 30라운드 안 죽은 원인: 희생 5, 갇힘 1
- 상대별: proxy4_elim 8회 75% · proxy4_king 6회 83% · proxy4_swarm 5회 60%
- 지도별: Autarky 3회 100% · Default 2회 100% · Queen Of Spades 2회 100% · Slithery Fight 4회 75% · Trauma 8회 50%
- 국면별: r250-349 2회 100% · r350-449 17회 71%

실패 사례 (5건 중 5건, 기보 확인용):
- proxy4_king · Trauma · 게임 exp/stack7-b-px4:proxy4_king:trauma:B:2 · r360 · 드래곤 #182 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r352 · 드래곤 #33 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:B:2 · r397 · 드래곤 #289 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Trauma · 게임 exp/stack7-b-px4:proxy4_elim:trauma:A:2 · r396 · 드래곤 #203 L7: 조각 L2 → 조각 죽음 r402 갇힘, 30라운드 안 먹은 진주 0
- proxy4_elim · Trauma · 게임 exp/stack7-b-px4:proxy4_elim:trauma:B:2 · r352 · 드래곤 #157 L10: 조각 L2 → 30라운드 생존, 먹은 진주 0

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 2340개 (표식 턴 5741, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 1, 이미 없음 208) · 사망 진주 2131개 중 우리가 먹음 79% · 상대 20% · 아무도 안 먹음 1% · 표적으로 삼은 드래곤이 먹음 63% · 우리가 먹기까지 평균 3.7라운드 · 상대 머리가 같거나 더 가까웠던 690개: 우리 52% 대 상대 47% · 박치기 진주 336개: 우리 55% 대 상대 45% · 우리 팀 사망 진주 80% · 사망 뒤 첫 표적까지 평균 1.3라운드
- 상대별: proxy4_elim 856회 79% · proxy4_king 732회 80% · proxy4_swarm 752회 77%
- 지도별: Autarky 255회 100% · Default 259회 75% · Devil 121회 48% · Portals 673회 98% · Prisoners Dilemma (10) 55회 51% · Queen Of Spades 67회 40% · Schooltime 82회 55% · Slithery Fight 571회 68% · Trauma 181회 80% · Trophy 76회 36%
- 국면별: r0-99 259회 65% · r100-249 765회 75% · r250-349 674회 84% · r350-449 538회 86% · r450+ 104회 63%

실패 사례 (456건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:B:2 · r59 · 드래곤 #10 L2: 진주 (31,27), 우리 머리 6칸 · 상대 머리 2칸, 박치기 4라운드 뒤 → 상대가 먹음 (2라운드 뒤), 표식 1턴
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:B:2 · r38 · 드래곤 #3 L2: 진주 (33,17), 우리 머리 6칸 · 상대 머리 2칸, 상대 사망 4라운드 뒤 → 상대가 먹음 (2라운드 뒤), 표식 1턴
- proxy4_king · Devil · 게임 exp/stack7-b-px4:proxy4_king:devil_b:A:2 · r88 · 드래곤 #8 L3: 진주 (10,10), 우리 머리 5칸 · 상대 머리 3칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (2라운드 뒤), 표식 1턴
- proxy4_king · Portals · 게임 exp/stack7-b-px4:proxy4_king:portals:A:2 · r377 · 드래곤 #538 L5: 진주 (3,15), 우리 머리 4칸 · 상대 머리 13칸, 우리 팀 사망 4라운드 뒤 → 아무도 안 먹음, 표식 1턴
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_king:prisoners_dilemma_10:B:2 · r8 · 드래곤 #7 L2: 진주 (14,13), 우리 머리 2칸 · 상대 머리 3칸, 상대 사망 3라운드 뒤 → 상대가 먹음 (2라운드 뒤), 표식 1턴
- proxy4_king · Queen Of Spades · 게임 exp/stack7-b-px4:proxy4_king:queen_of_spades_b:A:2 · r331 · 드래곤 #5 L2: 진주 (8,33), 우리 머리 4칸 · 상대 머리 1칸, 상대 사망 4라운드 뒤 → 상대가 먹음 (1라운드 뒤), 표식 2턴
- proxy4_king · Schooltime · 게임 exp/stack7-b-px4:proxy4_king:schooltime_b:A:2 · r91 · 드래곤 #9 L3: 진주 (20,13), 우리 머리 3칸 · 상대 머리 5칸, 우리 팀 사망 0라운드 뒤 → 상대가 먹음 (73라운드 뒤), 표식 4턴
- proxy4_king · Trauma · 게임 exp/stack7-b-px4:proxy4_king:trauma:A:2 · r234 · 드래곤 #62 L3: 진주 (15,11), 우리 머리 5칸 · 상대 머리 3칸, 박치기 2라운드 뒤 → 상대가 먹음 (6라운드 뒤), 표식 3턴
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:A:2 · r4 · 드래곤 #25 L2: 진주 (33,5), 우리 머리 5칸 · 상대 머리 10칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (42라운드 뒤), 표식 1턴
- proxy4_king · Trophy · 게임 exp/stack7-b-px4:proxy4_king:trophy:A:2 · r91 · 드래곤 #8 L3: 진주 (5,23), 우리 머리 3칸 · 상대 머리 1칸, 우리 팀 사망 3라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 941 (그중 통로 고리 세대 743, 판정에서 뺌) · 고리 밖 198: 처음 거리 평균 10.6 → 최소 5.4 · 3칸 안까지 감 42% · 희생까지 함 55% · 가는 길에 죽음 20% · 끝까지 생존 25%
- 상대별: proxy4_elim 270회 78% · proxy4_king 339회 80% · proxy4_swarm 332회 83%
- 지도별: Autarky 367회 95% · Default 13회 73% · Devil 8회 67% · Portals 272회 86% · Prisoners Dilemma (10) 172회 100% · Queen Of Spades 11회 60% · Schooltime 6회 0% · Slithery Fight 54회 74% · Trauma 38회 69%
- 국면별: r250-349 194회 82% · r350-449 621회 83% · r450+ 126회 60%

실패 사례 (57건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:A:2 · r393 · 드래곤 #176 L5: 왕까지 거리 9 → 최소 8 (4턴), 가는 길에 죽음 r453 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:B:2 · r340 · 드래곤 #81 L5: 왕까지 거리 10 → 최소 6 (3턴)
- proxy4_king · Devil · 게임 exp/stack7-b-px4:proxy4_king:devil_b:B:2 · r483 · 드래곤 #448 L5: 왕까지 거리 4 → 최소 4 (4턴)
- proxy4_king · Portals · 게임 exp/stack7-b-px4:proxy4_king:portals:A:2 · r340 · 드래곤 #502 L4: 왕까지 거리 8 → 최소 6 (8턴), 가는 길에 죽음 r348 희생
- proxy4_king · Queen Of Spades · 게임 exp/stack7-b-px4:proxy4_king:queen_of_spades_b:B:2 · r340 · 드래곤 #61 L5: 왕까지 거리 12 → 최소 10 (3턴), 가는 길에 죽음 r342 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Schooltime · 게임 exp/stack7-b-px4:proxy4_king:schooltime_b:B:2 · r452 · 드래곤 #3 L7: 왕까지 거리 34 → 최소 34 (3턴)
- proxy4_king · Trauma · 게임 exp/stack7-b-px4:proxy4_king:trauma:A:2 · r351 · 드래곤 #12 L4: 왕까지 거리 24 → 최소 24 (1턴)
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:A:2 · r419 · 드래곤 #449 L4: 왕까지 거리 6 → 최소 4 (7턴)
- proxy4_swarm · Autarky · 게임 exp/stack7-b-px4:proxy4_swarm:autarky:B:2 · r340 · 드래곤 #167 L6: 왕까지 거리 7 → 최소 6 (7턴), 가는 길에 죽음 r346 아군 머리, 상대 길이 5
- proxy4_swarm · Portals · 게임 exp/stack7-b-px4:proxy4_swarm:portals:A:2 · r340 · 드래곤 #422 L9: 왕까지 거리 4 → 최소 4 (14턴), 가는 길에 죽음 r353 아군 머리, 상대 길이 3

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 469개 중 우리 팀 87% (지목한 아군 59%) · 상대 3% · 지목 아군 끝까지 생존 63% (그 뒤 죽은 원인: 박힘(상대 돌진) 2, 희생 20, 돌진 2, 갇힘 29) · 지목 아군의 몸(자손 포함)이 끝까지 삶 93% · 최종 왕 47% (최종 왕이 지목 아군의 자손 67%)
- 상대별: proxy4_elim 46회 91% · proxy4_king 51회 86% · proxy4_swarm 47회 81%
- 지도별: Autarky 52회 94% · Default 6회 83% · Devil 3회 67% · Portals 29회 86% · Prisoners Dilemma (10) 5회 60% · Queen Of Spades 5회 60% · Schooltime 4회 50% · Slithery Fight 25회 80% · Trauma 15회 100%
- 국면별: r250-349 18회 94% · r350-449 90회 93% · r450+ 36회 64%

실패 사례 (20건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:B:2 · r495 · 드래곤 #199 L7: #5(L13)에게 희생 → 진주 4개 중 우리 1, 지목 아군 1, 상대 0
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:A:2 · r340 · 드래곤 #139 L5: #62(L13)에게 희생 → 진주 3개 중 우리 1, 지목 아군 0, 상대 0
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r499 · 드래곤 #47 L2: #147(L2)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Portals · 게임 exp/stack7-b-px4:proxy4_king:portals:B:2 · r441 · 드래곤 #589 L10: #593(L19)에게 희생 → 진주 5개 중 우리 2, 지목 아군 2, 상대 0; 지목 아군 r462 갇힘에 사망
- proxy4_king · Queen Of Spades · 게임 exp/stack7-b-px4:proxy4_king:queen_of_spades_b:B:2 · r400 · 드래곤 #109 L5: #114(L9)에게 희생 → 진주 3개 중 우리 2, 지목 아군 2, 상대 1
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:B:2 · r443 · 드래곤 #469 L5: #431(L14)에게 희생 → 진주 3개 중 우리 1, 지목 아군 0, 상대 2; 지목 아군 r453 희생에 사망
- proxy4_swarm · Autarky · 게임 exp/stack7-b-px4:proxy4_swarm:autarky:A:2 · r499 · 드래곤 #463 L2: #485(L20)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_swarm:prisoners_dilemma_10:A:2 · r498 · 드래곤 #2 L2: #47(L2)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Portals · 게임 exp/stack7-b-px4:proxy4_swarm:portals:A:2 · r467 · 드래곤 #505 L5: #514(L13)에게 희생 → 진주 3개 중 우리 0, 지목 아군 0, 상대 0; 지목 아군 r489 희생에 사망
- proxy4_swarm · Schooltime · 게임 exp/stack7-b-px4:proxy4_swarm:schooltime_b:B:2 · r485 · 드래곤 #5 L2: #1(L4)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 1

## 막다른 길 한입 (pocket-eat)

- 이번: 한입 100% · 2턴 안 분열 99% · 30라운드 뒤 가족 길이 변화 0.1 (줄지 않음 100%)
- 상대별: proxy4_elim 335회 99% · proxy4_king 335회 99% · proxy4_swarm 337회 99%
- 지도별: Devil 1회 100% · Portals 3회 33% · Prisoners Dilemma (10) 1002회 99% · Trauma 1회 100%
- 국면별: r0-99 198회 100% · r100-249 300회 100% · r250-349 207회 99% · r350-449 199회 100% · r450+ 103회 94%

실패 사례 (8건 중 8건, 기보 확인용):
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_king:prisoners_dilemma_10:B:2 · r499 · 드래곤 #351 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_swarm:prisoners_dilemma_10:A:2 · r499 · 드래곤 #346 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_swarm · Portals · 게임 exp/stack7-b-px4:proxy4_swarm:portals:B:2 · r304 · 드래곤 #471 L8: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 4
- proxy4_elim · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_elim:prisoners_dilemma_10:A:2 · r499 · 드래곤 #310 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_elim · Portals · 게임 exp/stack7-b-px4:proxy4_elim:portals:A:2 · r287 · 드래곤 #438 L16: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 -16
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r499 · 드래곤 #368 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_swarm:prisoners_dilemma_10:B:2 · r499 · 드래곤 #380 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_elim · Prisoners Dilemma (10) · 게임 exp/stack7-b-px4:proxy4_elim:prisoners_dilemma_10:B:2 · r499 · 드래곤 #294 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 97% · 새끼 자체 10라운드 생존 24% · 30라운드 뒤 가족 길이 변화 8.1
- 상대별: proxy4_elim 1265회 97% · proxy4_king 1262회 98% · proxy4_swarm 1307회 98%
- 지도별: Autarky 1538회 100% · Default 29회 93% · Devil 37회 95% · Portals 948회 92% · Prisoners Dilemma (10) 997회 100% · Queen Of Spades 9회 100% · Schooltime 2회 100% · Slithery Fight 144회 92% · Trauma 129회 94% · Trophy 1회 100%
- 국면별: r0-99 652회 100% · r100-249 1170회 98% · r250-349 932회 95% · r350-449 768회 97% · r450+ 312회 98%

실패 사례 (98건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack7-b-px4:proxy4_king:portals:A:2 · r230 · 드래곤 #241 L5: 새끼 L3 → 새끼 죽음 r231 갇힘, 상대 길이 8, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_king · Trauma · 게임 exp/stack7-b-px4:proxy4_king:trauma:B:2 · r413 · 드래곤 #169 L4: 새끼 L2 → 새끼 죽음 r421 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Default · 게임 exp/stack7-b-px4:proxy4_swarm:default:A:2 · r196 · 드래곤 #73 L13: 새끼 L11 → 새끼 죽음 r198 박힘(상대 돌진), 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -13
- proxy4_swarm · Devil · 게임 exp/stack7-b-px4:proxy4_swarm:devil_b:A:2 · r96 · 드래곤 #47 L4: 새끼 L2 → 새끼 죽음 r104 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Portals · 게임 exp/stack7-b-px4:proxy4_swarm:portals:A:2 · r291 · 드래곤 #297 L15: 새끼 L13 → 새끼 죽음 r293 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -15
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r482 · 드래곤 #925 L5: 새끼 L3 → 새끼 죽음 r484 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:B:2 · r161 · 드래곤 #68 L7: 새끼 L5 → 새끼 죽음 r162 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7
- proxy4_elim · Default · 게임 exp/stack7-b-px4:proxy4_elim:default:B:2 · r356 · 드래곤 #138 L8: 새끼 L6 → 새끼 죽음 r365 박힘(상대 돌진), 상대 길이 4, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -8
- proxy4_elim · Portals · 게임 exp/stack7-b-px4:proxy4_elim:portals:A:2 · r182 · 드래곤 #218 L5: 새끼 L3 → 새끼 죽음 r187 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_elim · Trauma · 게임 exp/stack7-b-px4:proxy4_elim:trauma:A:2 · r452 · 드래곤 #251 L4: 새끼 L2 → 새끼 죽음 r452 돌진, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 87% · 그 밖(진짜로 갇힘) 507회
- 상대별: proxy4_elim 1328회 – · proxy4_king 1276회 – · proxy4_swarm 1328회 –
- 지도별: Autarky 1537회 – · Default 84회 – · Devil 39회 – · Portals 849회 – · Prisoners Dilemma (10) 1005회 – · Queen Of Spades 10회 – · Schooltime 16회 – · Slithery Fight 190회 – · Trauma 182회 – · Trophy 20회 –
- 국면별: r0-99 702회 – · r100-249 1294회 – · r250-349 913회 – · r350-449 715회 – · r450+ 308회 –

## 정책 분열 (split)

- 이번: 분열 100% · 새끼 30라운드 생존 100% · 30라운드 뒤 가족 길이 변화 7
- 상대별: proxy4_elim 1회 100% · proxy4_swarm 1회 100%
- 지도별: Default 2회 100%
- 국면별: r100-249 1회 100% · r350-449 1회 100%

## 탈출 질주 3칸 (esc)

- 이번: 질주 97% · 짧은 적 머리 4칸 안 72% · 몸 생존 5라운드 96% · 10라운드 95% (드래곤 자체 88%) · 10라운드 길이 변화 -2.9
- 상대별: proxy4_elim 22회 95% · proxy4_king 20회 80% · proxy4_swarm 36회 97%
- 지도별: Default 9회 67% · Devil 2회 100% · Queen Of Spades 11회 91% · Schooltime 5회 100% · Slithery Fight 45회 98% · Trauma 3회 67% · Trophy 3회 100%
- 국면별: r0-99 6회 100% · r100-249 14회 100% · r250-349 15회 87% · r350-449 19회 84% · r450+ 24회 96%

실패 사례 (6건 중 6건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:B:2 · r394 · 드래곤 #121 L7: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r394 적 몸통, 상대 길이 8
- proxy4_king · Queen Of Spades · 게임 exp/stack7-b-px4:proxy4_king:queen_of_spades_b:B:2 · r367 · 드래곤 #65 L6: 질주 3칸 (가장 가까운 짧은 적 머리 10칸) → 죽음 r375 희생
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:A:2 · r315 · 드래곤 #505 L16: 질주 3칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r319 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:A:2 · r374 · 드래곤 #122 L7: 질주 3칸 (가장 가까운 짧은 적 머리 2칸) → 죽음 r376 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Default · 게임 exp/stack7-b-px4:proxy4_elim:default:A:2 · r487 · 드래곤 #164 L7: 질주 2칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r489 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:A:2 · r282 · 드래곤 #115 L6: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r282 돌진, 상대 길이 2

## 위협 피하기 2칸 질주

- 이번: 질주 99% · 몸 10라운드 생존 94% (드래곤 자체 90%)
- 상대별: proxy4_elim 239회 94% · proxy4_king 189회 93% · proxy4_swarm 218회 92%
- 지도별: Autarky 17회 94% · Default 83회 88% · Devil 54회 98% · Prisoners Dilemma (10) 10회 100% · Queen Of Spades 88회 95% · Schooltime 89회 98% · Slithery Fight 232회 93% · Trauma 29회 86% · Trophy 44회 86%
- 국면별: r0-99 132회 93% · r100-249 205회 94% · r250-349 173회 92% · r350-449 124회 93% · r450+ 12회 100%

실패 사례 (44건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:B:2 · r332 · 드래곤 #87 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 4) → 죽음 r341 희생
- proxy4_king · Devil · 게임 exp/stack7-b-px4:proxy4_king:devil_b:A:2 · r86 · 드래곤 #54 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r92 갇힘, 상대 길이 6
- proxy4_king · Queen Of Spades · 게임 exp/stack7-b-px4:proxy4_king:queen_of_spades_b:B:2 · r401 · 드래곤 #28 L4: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 12) → 죽음 r411 희생
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:A:2 · r318 · 드래곤 #505 L14: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r319 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Trophy · 게임 exp/stack7-b-px4:proxy4_king:trophy:A:2 · r91 · 드래곤 #36 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 3) → 죽음 r97 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Autarky · 게임 exp/stack7-b-px4:proxy4_swarm:autarky:A:2 · r24 · 드래곤 #6 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r31 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack7-b-px4:proxy4_swarm:default:B:2 · r70 · 드래곤 #12 L3: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 3) → 죽음 r73 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Queen Of Spades · 게임 exp/stack7-b-px4:proxy4_swarm:queen_of_spades_b:A:2 · r423 · 드래곤 #49 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r433 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Schooltime · 게임 exp/stack7-b-px4:proxy4_swarm:schooltime_b:A:2 · r198 · 드래곤 #13 L3: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 3) → 죽음 r198 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:A:2 · r369 · 드래곤 #122 L8: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 3) → 죽음 r376 박힘(상대 돌진), 상대 길이 3

## 포털 통과 (전체; PORTAL?=미탐색 출구)

- 이번: 미탐색 출구 1190회(몸 3라운드 생존 93%) · 전체 몸 생존 3라운드 94% (드래곤 자체 79%) · 10라운드 88% · 10라운드 안 먹은 진주 0.9
- 상대별: proxy4_elim 1020회 94% · proxy4_king 1077회 94% · proxy4_swarm 842회 93%
- 지도별: Autarky 432회 94% · Default 738회 95% · Portals 1187회 92% · Prisoners Dilemma (10) 42회 100% · Queen Of Spades 31회 84% · Schooltime 70회 97% · Slithery Fight 168회 92% · Trauma 265회 97% · Trophy 6회 67%
- 국면별: r0-99 338회 97% · r100-249 1199회 94% · r250-349 895회 93% · r350-449 440회 91% · r450+ 67회 96%

실패 사례 (189건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:B:2 · r136 · 드래곤 #39 L3: 포털(미탐색 출구) → 죽음 r136 아군 머리, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:A:2 · r157 · 드래곤 #8 L11: 포털 → 죽음 r157 갇힘, 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Portals · 게임 exp/stack7-b-px4:proxy4_king:portals:A:2 · r168 · 드래곤 #153 L10: 포털 → 죽음 r169 갇힘, 상대 길이 15, 10라운드 안 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack7-b-px4:proxy4_king:queen_of_spades_b:B:2 · r145 · 드래곤 #39 L2: 포털 → 죽음 r146 박힘(상대 돌진), 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Trauma · 게임 exp/stack7-b-px4:proxy4_king:trauma:A:2 · r138 · 드래곤 #4 L3: 포털(미탐색 출구) → 죽음 r140 갇힘, 10라운드 안 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:B:2 · r64 · 드래곤 #16 L28: 포털 → 죽음 r64 아군 머리, 상대 길이 3, 10라운드 안 진주 0
- proxy4_swarm · Default · 게임 exp/stack7-b-px4:proxy4_swarm:default:A:2 · r236 · 드래곤 #51 L2: 포털 → 죽음 r236 박힘(상대 돌진), 상대 길이 3, 10라운드 안 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack7-b-px4:proxy4_swarm:autarky:A:2 · r149 · 드래곤 #94 L3: 포털 → 죽음 r151 갇힘, 10라운드 안 진주 0
- proxy4_swarm · Portals · 게임 exp/stack7-b-px4:proxy4_swarm:portals:A:2 · r124 · 드래곤 #6 L2: 포털(미탐색 출구) → 죽음 r125 갇힘, 10라운드 안 진주 0
- proxy4_swarm · Queen Of Spades · 게임 exp/stack7-b-px4:proxy4_swarm:queen_of_spades_b:B:2 · r237 · 드래곤 #6 L3: 포털(미탐색 출구) → 죽음 r239 박힘(상대 돌진), 상대 길이 3, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 13, 경로 19) · 잡은 길이 ≥ 우리 100% · 두 몸의 진주 우리 60 대 상대 111
- 상대별: proxy4_elim 11회 64% · proxy4_king 7회 14% · proxy4_swarm 14회 36%
- 지도별: Default 5회 40% · Devil 1회 0% · Queen Of Spades 3회 33% · Schooltime 5회 20% · Slithery Fight 15회 53% · Trauma 3회 33%
- 국면별: r0-99 3회 33% · r100-249 5회 80% · r250-349 13회 31% · r350-449 8회 25% · r450+ 3회 67%

실패 사례 (19건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:A:2 · r72 · 드래곤 #26 L2: 돌진 경로 1칸 → 상대 L3 잡음, 진주 우리 0 대 상대 3
- proxy4_king · Devil · 게임 exp/stack7-b-px4:proxy4_king:devil_b:A:2 · r421 · 드래곤 #399 L3: 돌진 경로 2칸 → 상대 L3 잡음, 진주 우리 1 대 상대 3
- proxy4_king · Schooltime · 게임 exp/stack7-b-px4:proxy4_king:schooltime_b:A:2 · r342 · 드래곤 #95 L2: 돌진 경로 2칸 → 상대 L8 잡음, 진주 우리 0 대 상대 6
- proxy4_king · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_king:slithery_fight_b:A:2 · r316 · 드래곤 #25 L4: 돌진 경로 1칸 → 상대 L8 잡음, 진주 우리 0 대 상대 6
- proxy4_swarm · Default · 게임 exp/stack7-b-px4:proxy4_swarm:default:B:2 · r279 · 드래곤 #112 L5: 돌진 경로 4칸 → 상대 L6 잡음, 진주 우리 0 대 상대 5
- proxy4_swarm · Queen Of Spades · 게임 exp/stack7-b-px4:proxy4_swarm:queen_of_spades_b:A:2 · r404 · 드래곤 #110 L4: 돌진 경로 3칸 → 상대 L13 잡음, 진주 우리 0 대 상대 9
- proxy4_swarm · Schooltime · 게임 exp/stack7-b-px4:proxy4_swarm:schooltime_b:A:2 · r449 · 드래곤 #7 L3: 돌진 경로 2칸 → 상대 L25 잡음, 진주 우리 2 대 상대 13
- proxy4_swarm · Slithery Fight · 게임 exp/stack7-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r226 · 드래곤 #445 L2: 돌진 경로 1칸 → 상대 L5 잡음, 진주 우리 0 대 상대 4
- proxy4_swarm · Trauma · 게임 exp/stack7-b-px4:proxy4_swarm:trauma:B:2 · r258 · 드래곤 #196 L4: 돌진 경로 2칸 → 상대 L5 잡음, 진주 우리 1 대 상대 4
- proxy4_elim · Default · 게임 exp/stack7-b-px4:proxy4_elim:default:B:2 · r270 · 드래곤 #143 L4: 돌진 경로 3칸 → 상대 L5 잡음, 진주 우리 1 대 상대 4

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 상대별: proxy4_elim 55회 100% · proxy4_king 47회 100% · proxy4_swarm 41회 100%
- 지도별: Autarky 8회 100% · Default 25회 100% · Devil 6회 100% · Portals 19회 100% · Prisoners Dilemma (10) 1회 100% · Queen Of Spades 13회 100% · Schooltime 11회 100% · Slithery Fight 47회 100% · Trauma 6회 100% · Trophy 7회 100%
- 국면별: r0-99 17회 100% · r100-249 49회 100% · r250-349 40회 100% · r350-449 29회 100% · r450+ 8회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 95%
- 상대별: proxy4_elim 40회 – · proxy4_king 20회 – · proxy4_swarm 22회 –
- 지도별: Autarky 4회 – · Default 6회 – · Devil 6회 – · Queen Of Spades 8회 – · Schooltime 9회 – · Slithery Fight 36회 – · Trauma 6회 – · Trophy 7회 –
- 국면별: r0-99 14회 – · r100-249 21회 – · r250-349 26회 – · r350-449 17회 – · r450+ 4회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 11회 – · proxy4_king 12회 – · proxy4_swarm 12회 –
- 지도별: Autarky 1회 – · Default 9회 – · Devil 12회 – · Schooltime 1회 – · Slithery Fight 5회 – · Trauma 5회 – · Trophy 2회 –
- 국면별: r0-99 6회 – · r100-249 18회 – · r250-349 4회 – · r350-449 6회 – · r450+ 1회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/stack7-b-px4` | 60 | 27 (0.45) | 59% | 0 (0.00) | 0 (0.00) | 7 | 19 | 1 | 1/2 (3.5) | 93 (1.55; 필사 22) | 13/40 (45.5) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.
- 이번 `exp/stack7-b-px4`: gx 표식 턴 454 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/stack7-b-px4` | 60 | 38199 | 0.9% (328) | 17.3% (6599) | 4161 | 1.2% (51) | 2.9% (121) | 25.0% (1042/4161) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/stack7-b-px4` | 전체 | 분열 | 8 (17%) | 10.6 | 101% | 106% | 4 | 0 |
| 이번 `exp/stack7-b-px4` | 전체 | 2칸 질주 | 18 (39%) | 9.7 | 82% | 77% | 6 | 5 |
| 이번 `exp/stack7-b-px4` | 전체 | 3칸 질주 | 4 (9%) | 10.3 | 39% | 39% | 4 | 1 |
| 이번 `exp/stack7-b-px4` | 전체 | 한 걸음 | 16 (35%) | 9.9 | 41% | 40% | 14 | 7 |
| 이번 `exp/stack7-b-px4` | 4칸 이상 | 분열 | 4 (16%) | 12.8 | 110% | 124% | 2 | 0 |
| 이번 `exp/stack7-b-px4` | 4칸 이상 | 2칸 질주 | 10 (40%) | 9.8 | 91% | 86% | 3 | 3 |
| 이번 `exp/stack7-b-px4` | 4칸 이상 | 3칸 질주 | 1 (4%) | 13 | 31% | 46% | 1 | 0 |
| 이번 `exp/stack7-b-px4` | 4칸 이상 | 한 걸음 | 10 (40%) | 9.5 | 43% | 44% | 8 | 5 |

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (93건 중 10건):
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:B:2 · r136 · 드래곤 #39 L3: v2.4 PORTAL? → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:B:2 · r175 · 드래곤 #74 L3: v6.5 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:A:2 · r64 · 드래곤 #11 L3: v-1.1 → 갇힘, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/stack7-b-px4:proxy4_king:default:A:2 · r198 · 드래곤 #40 L2: v7 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:A:2 · r157 · 드래곤 #8 L11: v-9.5 → 갇힘, 막은 우리 드래곤 L3
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:A:2 · r164 · 드래곤 #79 L3: v7.3 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:A:2 · r225 · 드래곤 #176 L3: v7.9 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:A:2 · r286 · 드래곤 #274 L3: v6.6 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:A:2 · r330 · 드래곤 #250 L5: v8.8 → 아군 머리, 막은 우리 드래곤 L4
- proxy4_king · Autarky · 게임 exp/stack7-b-px4:proxy4_king:autarky:B:2 · r119 · 드래곤 #61 L3: v8.2 → 아군 머리, 막은 우리 드래곤 L2

## 지도·판본 인식 상세 (cand-mapid)

이번 (60판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 6 | 100% | 100% | 36/36 (36) | 1700 | 1700 (0) | 0 | 0 | 0 | 0 |
| Default a | 6 | 100% | 100% | 24/24 (24) | 244 | 243 (0) | 0 | 0 | 0 | 0 |
| Devil b | 6 | 100% | 100% | 18/18 (18) | 121 | 121 (0) | 0 | 0 | 0 | 17 |
| Portals a | 6 | 100% | 100% | 18/18 (18) | 1045 | 1044 (0) | 0 | 1 | 0 | 1 |
| Prisoners Dilemma b | 6 | 100% | 100% | 18/30 (18) | 1046 | 1041 (0) | 5 | 0 | 0 | 438 |
| Queen Of Spades b | 6 | 100% | 100% | 12/12 (12) | 59 | 57 (0) | 2 | 0 | 0 | 86 |
| Schooltime b | 6 | 100% | 100% | 36/36 (36) | 95 | 95 (0) | 0 | 0 | 0 | 7 |
| Slithery Fight b | 6 | 100% | 100% | 48/48 (48) | 410 | 400 (0) | 10 | 0 | 0 | 49 |
| Trauma a | 6 | 100% | 100% | 12/12 (12) | 290 | 290 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 6 | 100% | 100% | 12/12 (12) | 91 | 90 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 60/60, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

### Schooltime 판의 경제 (bsp의 가설 수준 지표, 정답 판본별)

| 묶음 | 판본 | 판 | 드래곤 수 r50 | r100 | r0–99 자연 진주 먹음 | 전멸당함 | 끝 최장(전멸 0) | 판당 bsp 분열 |
|---|---|---:|---|---|---|---:|---|---:|
| 이번 | b | 6 | 8 [7, 8] | 9 [9, 11] | 12 [10, 15] | 0% | 12 [7, 13] | 8.8 |

- 기준값(`research/experiments/cand-mapid.md`, 웨이브 전에 적음): b에서 드래곤 수 r50 중앙 ≥ 6, r0–99 자연 진주 중앙 ≥ 14. 우리 merge2 계열 b 29판은 3 · 9, 떼 계열(swarm8·px) b 14판은 6 · 14, 상위권 b 승자는 8 · 32다. a는 bsp가 켜지지 않는 대조군이다.

## stack5: 영토 덮기 (csplit · F · cov) 게이트와 가설 수준 지표

- 기준값은 `research/experiments/cand-stack5.md`(웨이브 전)에서, 상위권 승자(TW) 값과 merge2 값은 `research/observations/top-territory.md`에서 왔다. 정의는 영토 연구의 `exp/territory-analysis/extract.js`와 같다(영토 = 시작 몸에서 더 가까운 팀의 칸, 샘 = 그 판 판본 파일의 평균 간격 ≤12, 보로노이 = 용량 1/평균 간격 가중, 거리 = 지도 위 이동 거리, 몸은 무시).

### 게이트 (기능 적용)

| 지표 | 기준 | 이번 |
|---|---|---|
| csplit 발동: 500라운드형 지도 r0–249 판당 | ≥20 | 19.2 (전체 944회) |
| csplit 설계 상황: 부모가 팀 최장(≥8)이 아님 | ≥90% | 99% |
| csplit 새끼가 30라운드 안에 자연 진주 ≥1개 | ≥45% (TW 47% · 45%) | 39% (944마리) |
| csplit 새끼 30라운드 생존 | ≥30% (TW 34% · 51%) | 71% |
| F 목표(드래곤·샘) 수, 3걸음 안 도착 | – | 1774, 도착 37% |
| F 설계 상황: 실제 우리 영토 샘, 처음 표식 때 다른 우리 머리 3걸음 안 없음 | ≥80% | 70% |
| F 도착 뒤 30라운드 그 무리 자연 진주의 우리 몫(합산) | ≥85% (TW 자기 샘 90%) | 91% (상대 9%, 3565개) |
| F 같은 몫의 지도 평균(지도마다 합산, 같은 무게, Portals 제외) | ≥85% | 77% (Autarky 99%, Devil 48%, Prisoners Dilemma (10) 100%, Trauma 93%, Slithery Fight 47%) |

### 가설 수준 지표 (관찰; 500라운드형 / 전멸형)

| 지표 | 기준 | 상위권 승자 | merge2 | 이번 |
|---|---|---|---|---|
| r100 우리 드래곤 수(r100까지 간 판) | ≥15 / ≥10 | 30 / 21 | 4 / 3 | 11.3 / 6.9 |
| r100 우리 영토 보로노이 몫(용량 가중, 판 평균) | ≥80% | 89% / 81% | 66% / 32% | 74% / 29% |
| r100 샘 지킴: 우리 영토 샘 중 우리 머리 3걸음 안(판 평균) | ≥50% | 61% / 55% | 22% / – | 38% / 34% |
| 우리 영토 자연 진주(r0부터 생성)를 상대가 먹은 몫(합산) | ≤25% | 11% / 16% | 56% / 55% | 47% / 65% |
| 우리 영토 샘 진주를 상대가 먹은 몫(합산) | ≤15% | 7% / 6% | 50% / 33% | 43% / 54% |

- 판 수(500라운드형 / 전멸형): 이번 30 / 30. 판본 파일을 못 찾은 판: 이번 0.

### 부작용: 우리 드래곤의 죽음 (판당; 전체 / r250 전)

| 원인 | 이번 |
|---|---|
| 갇힘(빈 이웃 없음; 통로 고리의 남은 조각 포함) | 66.6 / 33.6 |
| 적 머리에 박힘 | 7.6 / 5.2 |
| 우리 드래곤끼리 머리 충돌(둘 다 죽음, 둘 다 셈) | 1.9 / 1.2 |

- 막힘에서 아군 머리를 피해 죽은 턴(no-exit s): 이번 107

### 지도별 (이번)

| 지도 | 판 | csplit 판당 | 새끼 먹음 ≥1 | 새끼 30R 생존 | F 목표 · 도착 · 무리 진주 우리 몫 | r100 드래곤 | 보로노이 | 샘 지킴 | 상대가 먹은 영토 진주 | 상대가 먹은 샘 진주 |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| Autarky | 6 | 20.5 | 38% | 93% | 233 · 87% · 99% | 11.5 | 96% | 86% | 8% | 8% |
| Default | 6 | 29.7 | 42% | 62% | 3 · 33% · – | 9.2 | 33% | – | 71% | – |
| Devil | 6 | 10 | 25% | 77% | 163 · 23% · 48% | 7.2 | 33% | 18% | 85% | 87% |
| Portals | 6 | 13.2 | 44% | 62% | 727 · 32% · 100% | 11.3 | 100% | 41% | 0% | 0% |
| Prisoners Dilemma (10) | 6 | 3.2 | 37% | 95% | 97 · 62% · 100% | 3.8 | 46% | 50% | 23% | 0% |
| Queen Of Spades | 6 | 5.3 | 19% | 97% | 8 · 0% · – | 3.8 | 9% | – | 80% | – |
| Schooltime | 6 | 3.3 | 30% | 85% | 0 · – · – | 9 | 48% | – | 76% | – |
| Slithery Fight | 6 | 36.5 | 37% | 72% | 440 · 22% · 47% | 17.5 | 33% | 12% | 75% | 80% |
| Trauma | 6 | 22.7 | 47% | 47% | 98 · 28% · 93% | 7.2 | 96% | 14% | 53% | 0% |
| Trophy | 6 | 13 | 46% | 78% | 5 · 60% · – | 10.3 | 23% | – | 63% | – |

## stack7: 수 바닥 분열(floor)과 왕 길이 상한(kcap) 게이트, 저수 에피소드, 가설 수준 지표, 지도 가르기

- 기준값은 `research/experiments/cand-stack7.md`(웨이브 전)에서, 상위권·우리 값은 `research/observations/our-eliminations.md`(2.6절, 1.3절, 2.2절)에서 왔다. 저수 에피소드와 부류의 정의는 전멸 연구(`exp/eliminations/top.js` I, `lib.js` classOf)와 같다: r50부터 5라운드 간격으로 처음 우리 수 1–3·상대 ≥8인 라운드 r(라운드 첫 턴의 수; r+20이 판 안이고 우리 전멸 전), 그 뒤 [r, r+20) 분열, 20라운드 뒤 4마리 이상이면 회복, 50라운드 안 전멸. 연구의 분열 수는 10라운드 칸 두 개의 전체 분열(탈출 분열 포함)이고, 여기서는 [r, r+20)을 그대로 센다.

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 |
|---|---|---|---|
| floor | 발동(판당; floor 지도 판) | – | 23 (0.5; 42판) |
| floor | 1. 설계 상황: 발동 때 상대 ≥8마리 | ≥90% | 96% |
| floor | 저수 에피소드가 있는 floor 지도 판 · 그 20라운드 안 floor 발동이 있었던 판 | (관찰) | 30 · 17% |
| floor | 2. 즉시 효과 A: 에피소드 20라운드 비탈출 분열(판당; floor 지도) | ≥2.0 (상위 LX·LS 2.0, 우리 0.5) | 0.3 (floor 0.2, kcap 0, csplit 0.1; 탈출 포함 전체 0.4) |
| floor | 3. 즉시 효과 B: 에피소드 20라운드 뒤 4마리 이상(floor 지도) | ≥23% (상위 LX 23%, LS 26%, 우리 5%) | 20% (6/30) |
| floor | 4. 즉시 효과 C: floor 새끼 30라운드 생존 | ≥34% (상위 패자 제 영토 새끼 34%, 승자 51%) | 74% (23마리) |
| kcap | 발동(판당; kcap 지도 판) | – | 4 (0.1; 36판) |
| kcap | 1. 설계 상황: 부모가 그 순간 팀 최장이고 r250 전 | ≥90% | 100% |
| kcap | 2. 즉시 효과: 새끼 10라운드 생존 | ≥74% (상위권 길이 4 분열 74.2%) | 75% (4마리) |
| kcap | 2. 즉시 효과: 부모 10라운드 생존 | ≥55% (상위권 54.5%) | 75% |

### 저수 에피소드 (floor 지도 / 모든 지도; 판정은 floor 지도)

| 묶음 | 지도 | 판 | 에피소드 있음 | 처음 라운드(중앙) | 그때 우리 수 · 상대 수 | 그때 총길이 · 최장 | 20라운드 비탈출 분열 | floor · kcap | 탈출 포함 전체 | 20라운드 뒤 4마리 이상 | 50라운드 안 전멸 |
|---|---|---:|---:|---:|---|---|---:|---|---:|---:|---:|
| 이번 | floor 지도 | 42 | 71% | 292.5 | 2.9 · 28.4 | 13.4 · 7.6 | 0.3 | 0.2 · 0 | 0.4 | 20% | 10% |
| 이번 | floor 지도 중 전멸형 | 24 | 88% | 170 | 2.9 · 29.5 | 8 · 3.6 | 0.3 | 0.2 · 0 | 0.4 | 24% | 14% |
| 이번 | floor 지도 중 500형 | 18 | 50% | 435 | 3 · 25.9 | 26.1 · 17.1 | 0.1 | 0.1 · 0 | 0.3 | 11% | 0% |
| 이번 | 끄는 지도(Autarky·PD·Portals) | 18 | 50% | 220 | 3 · 15.8 | 27.4 · 17.6 | 0.3 | 0 · 0 | 8.3 | 44% | 0% |
| 이번 | 모든 지도 | 60 | 65% | 275 | 2.9 · 25.5 | 16.7 · 9.9 | 0.3 | 0.1 · 0 | 2.2 | 26% | 8% |

- 상위권 기준(전멸 연구 2.6절, 전멸형): LX 72%가 그런 때를 겪고(처음 r105) 20라운드에 2.0번 나누며 23%가 회복, 42%가 50라운드 안 전멸. LS 69%, 2.0번, 26%, 0%. 우리 g4 LX 95%(r50), 0.5번, 5%, 15%.

### 가설 수준 지표 (관찰)

| 기능 | 지표 | 기준 | 상위권 · 이전 우리 | 이번 |
|---|---|---|---|---|
| floor | r100 우리 드래곤 수(전멸형; 전멸은 0) — 전멸형 5지도 / PD 뺀 4지도 | ≥5.5 | 상위 LX 5.5, 우리 g4 LX 2.5 | 6.9 / 7.6 |
| floor | 전멸률(전멸형) | ≤66% | swarm8 66%, merge2 78% | 23% (7/30) / 29% (7/24) |
| floor | 전멸 라운드 중앙(전멸형) | ≥r235 | swarm8 235, merge2 150, stack1–3 163 | 201 / 201 |
| kcap | 우리 전멸 중 E2(왕 사냥) 비율(모든 지도) | ≤8% | 상위 LX 6%, 우리 16% | 0% (E1 0 · E2 0 · E3m 6 · E3l 1) |
| kcap | r50 우리 최장 평균(전멸형; 전멸은 0) — 5지도 / 4지도 | ≤4.5 | 상위 LS 3.8, 우리 g4 LX 6.8 | 5.7 / 3.8 |
| kcap | 전멸한 판의 길이 ≥8 죽음(판당; 모든 지도) | ≤0.4 | 우리 0.75 | 0.3 (7판) |

### 지도 가르기 (map= 표식으로 확인)

- floor는 Trophy, Queen Of Spades, Devil, Default, Schooltime, Trauma, Slithery Fight에서만, kcap은 그중 Slithery Fight를 뺀 여섯에서만 켠다. 봇은 프로세스마다 자기 창으로 지도 가족을 인식하고(`map=` 표식), 인식 전·`none`이면 끈다. "표식이 켜는 가족이 아닌 발동"은 발동한 프로세스의 마지막 `map=` 표식이 그 기능을 켜는 가족을 대지 않은 발동이다(0이어야 한다). "인식한 프로세스"는 마지막 표식이 그 판의 참 지도 가족을 댄 프로세스다.

| 묶음 | 지도(정답 판본) | 판 | floor 발동 | kcap 발동 | 표식이 켜는 가족이 아닌 발동 | 인식한 프로세스 |
|---|---|---:|---:|---:|---:|---:|
| 이번 | Autarky (끔) | 6 | 0 | 0 | 0 | 100% (1700/1700) |
| 이번 | Default | 6 | 7 | 2 | 0 | 100% (243/244) |
| 이번 | Devil b | 6 | 6 | 0 | 0 | 100% (121/121) |
| 이번 | Portals (끔) | 6 | 0 | 0 | 0 | 100% (1044/1045) |
| 이번 | Prisoners Dilemma (10) (끔) | 6 | 0 | 0 | 0 | 100% (1046/1046) |
| 이번 | Queen Of Spades b | 6 | 3 | 1 | 0 | 100% (59/59) |
| 이번 | Schooltime b | 6 | 2 | 0 | 0 | 100% (95/95) |
| 이번 | Slithery Fight b (kcap 끔) | 6 | 1 | 0 | 0 | 100% (410/410) |
| 이번 | Trauma | 6 | 4 | 1 | 0 | 100% (290/290) |
| 이번 | Trophy | 6 | 0 | 0 | 0 | 99% (90/91) |

