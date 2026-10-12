# 구현 적용 확인

- 대상: `exp/mapid-b-px4` 60판
- 기준(사용자 규칙 2026-09-30): 승률이 아니라, 봇에 구현한 기능이 이 상대들에게 실제로 발동하고 의도대로 작동했는지를 본다.
- "의도대로"의 정의: 모이기=왕 3칸 안까지 가거나 희생까지 함 · 희생=떨군 진주 절반 이상을 우리 팀이 먹고 상대는 못 먹음 · 한입=2턴 안 분열하고 30라운드 뒤 가족 길이가 줄지 않음 · 탈출 분열=10라운드 뒤 몸이 살아 있음 · 정책 분열=새끼 30라운드 생존 · 탈출 질주·위협 피하기=10라운드 뒤 몸 생존 · 포털=3라운드 뒤 몸 생존 · 돌진=충돌 성사, 잡은 길이 ≥ 우리, 두 몸의 진주를 우리가 더 먹음 · 먹이 질주=진주 먹음.
- "몸"은 그 드래곤과 그 뒤 분열로 태어난 자손 전체다. 통로 고리처럼 몸을 새끼에게 넘기며 버티는 경우를 손실로 세지 않기 위해서다.
- stack2의 "의도대로": 조각 떼기=조각이 30라운드 살며 진주를 1개 이상 먹거나, 나중에 희생(feed·conv)으로 아군을 먹임 · 새 사망 진주 줍기=표적이 된 사망 진주(진주 하나가 한 건)를 우리 팀이 먹음(자연 진주로 오인했거나 이미 없던 표적은 판정에서 뺌).
- cand-mapid의 "의도대로": Schooltime b 초반 분열(bsp)=떼어 낸 조각(새 유닛)이 10라운드 뒤 살아 있음 · 지도·판본 인식=그 판에서 1개 이상의 프로세스가 판본까지 결정했고, 결정한 프로세스(마지막 표식 기준)가 모두 정답 지도·판본을 댐. 정답 판본은 로컬이면 지도 파일 이름, 온라인이면 기보의 자연 생성(한쪽 판본에서만 생성하는 칸)으로 정하고, 끝까지 가릴 수 없던 판은 뺀다. 지도별 줄의 이름 뒤 a·b·?가 정답 판본이다.

## 요약

| 기능 | 발동(판당) | 의도대로 | 
|---|---:|---:|
| 지도·판본 인식 (map=, cand-mapid; 판 단위) | 60 (1) | 100% | 
| Schooltime b 초반 분열 (split bsp, cand-mapid) | 73 (1.2) | 95% | 
| 큰 아군 곁 희생 (conv, stack1 M1) | 55 (0.9) | 98% | 
| 조각 떼기 (split frag, stack2 S1) | 46 (0.8) | 87% | 
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 543 (9.1) | 69% | 
| 왕에게 모이기 (g, 드래곤 단위) | 481 (8) | 85% | 
| 희생 먹이기 (feed) | 52 (0.9) | 92% | 
| 막다른 길 한입 (pocket-eat) | 1003 (16.7) | 99% | 
| 탈출 분열 (escape-split) | 2994 (49.9) | 99% | 
| 출구 없음 (no-exit) | 2883 (48.1) | – | 
| 정책 분열 (split) | 51 (0.9) | 67% | 
| 탈출 질주 3칸 (esc) | 46 (0.8) | 96% | 
| 위협 피하기 2칸 질주 | 461 (7.7) | 91% | 
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 992 (16.5) | 96% | 
| 돌진 (TRADE) | 11 (0.2) | 45% | 
| 먹이 질주 (2칸 이상, 먹은 것) | 48 (0.8) | 100% | 
| 기타 2칸 질주 | 2 (0) | – | 
| 마지막 돌진 (last-trade) | 23 (0.4) | – | 

- 건강: 턴 94247, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 4094턴 · 끝판(late) 2565턴 · 돌진 신뢰(T, 탈출 끔) 119턴, 그 직후 박혀 죽음 0

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 
|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 3% (25/910턴) | 
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 18.9칸 (3.6회), 진주 우리 94% · 상대 1% | 
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 0칸 (판당 0.00회) | 
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 29% (954/3242턴) | 
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.000회 (0건, 0칸) | 
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 3.8마리 (28판) | 
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 15회 | 
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 56% (우리 38%) | 
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 4.6 대 상대 16.8 (5.4회) · 박힌 교환의 우리 몫 16% (135회) | 
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 4.1개 | 

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 지도·판본 인식 (map=, cand-mapid; 판 단위)

- 이번: 판본을 기보로 가릴 수 있는 판 60/60 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 95%, 그중 정답 100% · 프로세스 3386: 표식 없음 4, 결정 3367 (정답 100%, 틀림 0), 가족만 15, 모름 0, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 91라운드
- 상대별: proxy4_elim 20회 100% · proxy4_king 20회 100% · proxy4_swarm 20회 100%
- 지도별: Autarky a 6회 100% · Default a 6회 100% · Devil b 6회 100% · Portals a 6회 100% · Prisoners Dilemma b 6회 100% · Queen Of Spades b 6회 100% · Schooltime b 6회 100% · Slithery Fight b 6회 100% · Trauma a 6회 100% · Trophy a 6회 100%
- 국면별: r0-99 60회 100%

## Schooltime b 초반 분열 (split bsp, cand-mapid)

- 이번: 분열 100% · 설계 상황(그 판이 실제로 Schooltime b) 100% · 조각 10라운드 생존 95% (기준 ≥85%; 상위권 b 92%) · 10라운드 안 1개 이상 먹음 11% (상위권 b 20%) · 부모 10라운드 생존 100% · 조각 30라운드 생존 93%, 30라운드 안 1개 이상 먹음 33% · 30라운드 뒤 가족 길이 변화 3.2 · 30라운드 안 조각이 죽은 원인: 희생 1, 갇힘 2, 박힘(상대 돌진) 2
- 상대별: proxy4_elim 31회 94% · proxy4_king 16회 94% · proxy4_swarm 26회 96%
- 지도별: Schooltime 73회 95%
- 국면별: r0-99 46회 100% · r100-249 27회 85%

실패 사례 (4건 중 4건, 기보 확인용):
- proxy4_swarm · Schooltime · 게임 exp/mapid-b-px4:proxy4_swarm:schooltime_b:B:2 · r130 · 드래곤 #12 L4: 조각 L2 → 조각 죽음 r132 희생, 상대 길이 3, 10·30라운드 안 먹은 진주 0·0
- proxy4_elim · Schooltime · 게임 exp/mapid-b-px4:proxy4_elim:schooltime_b:A:2 · r147 · 드래곤 #25 L4: 조각 L2 → 조각 죽음 r155 갇힘, 10·30라운드 안 먹은 진주 0·0
- proxy4_king · Schooltime · 게임 exp/mapid-b-px4:proxy4_king:schooltime_b:B:2 · r128 · 드래곤 #5 L4: 조각 L2 → 조각 죽음 r134 갇힘, 10·30라운드 안 먹은 진주 0·0
- proxy4_elim · Schooltime · 게임 exp/mapid-b-px4:proxy4_elim:schooltime_b:A:2 · r156 · 드래곤 #4 L4: 조각 L2 → 조각 죽음 r164 박힘(상대 돌진), 상대 길이 3, 10·30라운드 안 먹은 진주 0·0

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 83개 중 우리 팀 98% (지목한 아군 81%) · 상대 2% · 지목 아군 끝까지 생존 35% (그 뒤 죽은 원인: 희생 10, 갇힘 23, 아군 머리 2, 돌진 1) · 지목 아군의 몸(자손 포함)이 끝까지 삶 80% · 최종 왕 24% (최종 왕이 지목 아군의 자손 38%)
- 상대별: proxy4_elim 14회 100% · proxy4_king 22회 100% · proxy4_swarm 19회 95%
- 지도별: Autarky 7회 100% · Portals 34회 100% · Slithery Fight 7회 86% · Trauma 7회 100%
- 국면별: r250-349 21회 95% · r350-449 29회 100% · r450+ 5회 100%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r305 · 드래곤 #103 L3: #519(L11)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2; 지목 아군 r340 돌진에 사망

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 100% · 조각 30라운드 생존 57% · 30라운드 안 1개 이상 먹음 74% (살아서 먹음 48%) · 평생 먹은 진주 평균 3.9 · 나중에 아군을 먹임 70% (conv 18, feed 14, 분열 뒤 평균 37.7라운드) · 끝까지 생존 9% · 30라운드 안 죽은 원인: 희생 16, 갇힘 4
- 상대별: proxy4_elim 17회 88% · proxy4_king 18회 83% · proxy4_swarm 11회 91%
- 지도별: Autarky 20회 100% · Portals 12회 58% · Slithery Fight 10회 90% · Trauma 4회 100%
- 국면별: r250-349 25회 80% · r350-449 21회 95%

실패 사례 (6건 중 6건, 기보 확인용):
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r286 · 드래곤 #308 L14: 조각 L2 → 조각 죽음 r304 갇힘, 30라운드 안 먹은 진주 2
- proxy4_elim · Portals · 게임 exp/mapid-b-px4:proxy4_elim:portals:A:2 · r404 · 드래곤 #428 L17: 조각 L2 → 조각 죽음 r404 갇힘, 상대 길이 2, 30라운드 안 먹은 진주 0
- proxy4_king · Portals · 게임 exp/mapid-b-px4:proxy4_king:portals:B:2 · r269 · 드래곤 #312 L8: 조각 L2 → 조각 죽음 r282 갇힘, 상대 길이 13, 30라운드 안 먹은 진주 2
- proxy4_king · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_king:slithery_fight_b:B:2 · r285 · 드래곤 #508 L11: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Portals · 게임 exp/mapid-b-px4:proxy4_elim:portals:B:2 · r253 · 드래곤 #115 L17: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_king · Portals · 게임 exp/mapid-b-px4:proxy4_king:portals:B:2 · r323 · 드래곤 #330 L7: 조각 L2 → 조각 죽음 r332 갇힘, 상대 길이 16, 30라운드 안 먹은 진주 4

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 543개 (표식 턴 1231, 진주당 드래곤 1.1) · 질량 장부의 사망 진주 95% (자연 진주 0, 이미 없음 29) · 사망 진주 514개 중 우리가 먹음 69% · 상대 29% · 아무도 안 먹음 2% · 표적으로 삼은 드래곤이 먹음 60% · 우리가 먹기까지 평균 4.3라운드 · 상대 머리가 같거나 더 가까웠던 164개: 우리 28% 대 상대 70% · 박치기 진주 113개: 우리 57% 대 상대 42% · 우리 팀 사망 진주 70% · 사망 뒤 첫 표적까지 평균 1.7라운드
- 상대별: proxy4_elim 165회 70% · proxy4_king 177회 70% · proxy4_swarm 201회 68%
- 지도별: Autarky 48회 91% · Default 22회 32% · Devil 25회 52% · Portals 162회 97% · Prisoners Dilemma (10) 16회 47% · Queen Of Spades 22회 19% · Schooltime 72회 45% · Slithery Fight 130회 62% · Trauma 36회 72% · Trophy 10회 0%
- 국면별: r0-99 70회 41% · r100-249 160회 55% · r250-349 116회 74% · r350-449 167회 88% · r450+ 30회 79%

실패 사례 (159건 중 10건, 기보 확인용):
- proxy4_swarm · Default · 게임 exp/mapid-b-px4:proxy4_swarm:default:A:2 · r124 · 드래곤 #6 L3: 진주 (20,20), 우리 머리 4칸 · 상대 머리 1칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_swarm · Devil · 게임 exp/mapid-b-px4:proxy4_swarm:devil_b:A:2 · r97 · 드래곤 #4 L7: 진주 (9,6), 우리 머리 4칸 · 상대 머리 3칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 3턴
- proxy4_swarm · Autarky · 게임 exp/mapid-b-px4:proxy4_swarm:autarky:A:2 · r97 · 드래곤 #6 L2: 진주 (27,3), 우리 머리 4칸 · 상대 머리 2칸, 박치기 1라운드 뒤 → 상대가 먹음 (1라운드 뒤), 표식 2턴
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/mapid-b-px4:proxy4_swarm:prisoners_dilemma_10:A:2 · r108 · 드래곤 #6 L2: 진주 (17,13), 우리 머리 1칸 · 상대 머리 3칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 1턴
- proxy4_swarm · Queen Of Spades · 게임 exp/mapid-b-px4:proxy4_swarm:queen_of_spades_b:A:2 · r72 · 드래곤 #0 L3: 진주 (4,0), 우리 머리 4칸 · 상대 머리 5칸, 우리 팀 사망 3라운드 뒤 → 상대가 먹음 (5라운드 뒤), 표식 1턴
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r480 · 드래곤 #437 L10: 진주 (11,0), 우리 머리 5칸 · 상대 머리 9칸, 우리 팀 사망 1라운드 뒤 → 아무도 안 먹음, 표식 4턴
- proxy4_swarm · Schooltime · 게임 exp/mapid-b-px4:proxy4_swarm:schooltime_b:A:2 · r327 · 드래곤 #7 L3: 진주 (12,23), 우리 머리 6칸 · 상대 머리 1칸, 상대 사망 2라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_swarm · Trauma · 게임 exp/mapid-b-px4:proxy4_swarm:trauma:B:2 · r244 · 드래곤 #1 L2: 진주 (22,4), 우리 머리 6칸 · 상대 머리 3칸, 상대 사망 3라운드 뒤 → 상대가 먹음 (10라운드 뒤), 표식 3턴
- proxy4_swarm · Trophy · 게임 exp/mapid-b-px4:proxy4_swarm:trophy:A:2 · r100 · 드래곤 #2 L10: 진주 (11,2), 우리 머리 3칸 · 상대 머리 4칸, 박치기 1라운드 뒤 → 아무도 안 먹음, 표식 4턴
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r4 · 드래곤 #23 L2: 진주 (33,5), 우리 머리 5칸 · 상대 머리 10칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (26라운드 뒤), 표식 1턴

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 481 (그중 통로 고리 세대 410, 판정에서 뺌) · 고리 밖 71: 처음 거리 평균 8.5 → 최소 4.3 · 3칸 안까지 감 49% · 희생까지 함 52% · 가는 길에 죽음 14% · 끝까지 생존 34%
- 상대별: proxy4_elim 119회 84% · proxy4_king 205회 81% · proxy4_swarm 157회 88%
- 지도별: Autarky 309회 95% · Portals 156회 85% · Schooltime 4회 75% · Slithery Fight 7회 60% · Trauma 5회 75%
- 국면별: r250-349 84회 97% · r350-449 322회 88% · r450+ 75회 57%

실패 사례 (19건 중 10건, 기보 확인용):
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r405 · 드래곤 #423 L11: 왕까지 거리 7 → 최소 7 (9턴), 가는 길에 죽음 r413 갇힘, 상대 길이 14
- proxy4_swarm · Schooltime · 게임 exp/mapid-b-px4:proxy4_swarm:schooltime_b:B:2 · r394 · 드래곤 #174 L31: 왕까지 거리 8 → 최소 8 (1턴)
- proxy4_swarm · Trauma · 게임 exp/mapid-b-px4:proxy4_swarm:trauma:A:2 · r417 · 드래곤 #251 L4: 왕까지 거리 13 → 최소 13 (3턴)
- proxy4_elim · Portals · 게임 exp/mapid-b-px4:proxy4_elim:portals:A:2 · r499 · 드래곤 #444 L29: 왕까지 거리 5 → 최소 5 (1턴)
- proxy4_elim · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_elim:slithery_fight_b:A:2 · r401 · 드래곤 #790 L7: 왕까지 거리 8 → 최소 8 (1턴), 가는 길에 죽음 r412 돌진, 상대 길이 19
- proxy4_king · Autarky · 게임 exp/mapid-b-px4:proxy4_king:autarky:B:2 · r498 · 드래곤 #486 L14: 왕까지 거리 15 → 최소 15 (1턴)
- proxy4_king · Portals · 게임 exp/mapid-b-px4:proxy4_king:portals:A:2 · r353 · 드래곤 #408 L4: 왕까지 거리 7 → 최소 6 (2턴), 가는 길에 죽음 r355 희생
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r444 · 드래곤 #437 L10: 왕까지 거리 7 → 최소 5 (56턴)
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r482 · 드래곤 #447 L16: 왕까지 거리 7 → 최소 5 (18턴)
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r483 · 드래곤 #448 L24: 왕까지 거리 7 → 최소 7 (1턴)

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 220개 중 우리 팀 92% (지목한 아군 64%) · 상대 1% · 지목 아군 끝까지 생존 67% (그 뒤 죽은 원인: 희생 3, 갇힘 14) · 지목 아군의 몸(자손 포함)이 끝까지 삶 94% · 최종 왕 50% (최종 왕이 지목 아군의 자손 69%)
- 상대별: proxy4_elim 18회 94% · proxy4_king 14회 100% · proxy4_swarm 20회 85%
- 지도별: Autarky 20회 95% · Portals 22회 95% · Schooltime 4회 75% · Slithery Fight 5회 80% · Trauma 1회 100%
- 국면별: r250-349 3회 100% · r350-449 33회 100% · r450+ 16회 75%

실패 사례 (4건 중 4건, 기보 확인용):
- proxy4_swarm · Autarky · 게임 exp/mapid-b-px4:proxy4_swarm:autarky:B:2 · r457 · 드래곤 #388 L8: #11(L58)에게 희생 → 진주 4개 중 우리 1, 지목 아군 1, 상대 0
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r479 · 드래곤 #439 L5: #437(L10)에게 희생 → 진주 3개 중 우리 1, 지목 아군 1, 상대 0
- proxy4_swarm · Schooltime · 게임 exp/mapid-b-px4:proxy4_swarm:schooltime_b:B:2 · r489 · 드래곤 #32 L2: #7(L2)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 1
- proxy4_elim · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_elim:slithery_fight_b:A:2 · r486 · 드래곤 #592 L3: #843(L2)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1

## 막다른 길 한입 (pocket-eat)

- 이번: 한입 100% · 2턴 안 분열 99% · 30라운드 뒤 가족 길이 변화 0.1 (줄지 않음 100%)
- 상대별: proxy4_elim 334회 99% · proxy4_king 334회 99% · proxy4_swarm 335회 99%
- 지도별: Prisoners Dilemma (10) 1002회 99% · Trauma 1회 0%
- 국면별: r0-99 198회 100% · r100-249 300회 100% · r250-349 204회 100% · r350-449 199회 99% · r450+ 102회 94%

실패 사례 (7건 중 7건, 기보 확인용):
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/mapid-b-px4:proxy4_swarm:prisoners_dilemma_10:A:2 · r499 · 드래곤 #333 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_swarm · Trauma · 게임 exp/mapid-b-px4:proxy4_swarm:trauma:B:2 · r359 · 드래곤 #159 L12: 한입, 분열(새끼 L11), 30라운드 뒤 가족 길이 변화 -6
- proxy4_elim · Prisoners Dilemma (10) · 게임 exp/mapid-b-px4:proxy4_elim:prisoners_dilemma_10:A:2 · r499 · 드래곤 #332 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/mapid-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r499 · 드래곤 #355 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/mapid-b-px4:proxy4_swarm:prisoners_dilemma_10:B:2 · r499 · 드래곤 #376 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_elim · Prisoners Dilemma (10) · 게임 exp/mapid-b-px4:proxy4_elim:prisoners_dilemma_10:B:2 · r499 · 드래곤 #343 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/mapid-b-px4:proxy4_king:prisoners_dilemma_10:B:2 · r499 · 드래곤 #393 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 99% · 새끼 자체 10라운드 생존 13% · 30라운드 뒤 가족 길이 변화 10.1
- 상대별: proxy4_elim 953회 99% · proxy4_king 991회 99% · proxy4_swarm 1050회 99%
- 지도별: Autarky 1502회 100% · Default 9회 78% · Devil 19회 63% · Portals 344회 98% · Prisoners Dilemma (10) 997회 100% · Queen Of Spades 4회 75% · Schooltime 8회 88% · Slithery Fight 70회 97% · Trauma 40회 95% · Trophy 1회 100%
- 국면별: r0-99 590회 100% · r100-249 882회 99% · r250-349 619회 99% · r350-449 626회 99% · r450+ 277회 100%

실패 사례 (23건 중 10건, 기보 확인용):
- proxy4_swarm · Devil · 게임 exp/mapid-b-px4:proxy4_swarm:devil_b:A:2 · r114 · 드래곤 #2 L12: 새끼 L10 → 새끼 죽음 r116 아군 머리, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -12
- proxy4_swarm · Autarky · 게임 exp/mapid-b-px4:proxy4_swarm:autarky:B:2 · r312 · 드래곤 #274 L4: 새끼 L2 → 새끼 죽음 r321 갇힘, 상대 길이 30, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r303 · 드래곤 #328 L4: 새끼 L2 → 새끼 죽음 r305 갇힘, 상대 길이 12, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_elim · Default · 게임 exp/mapid-b-px4:proxy4_elim:default:A:2 · r171 · 드래곤 #64 L17: 새끼 L15 → 새끼 죽음 r172 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -17
- proxy4_elim · Devil · 게임 exp/mapid-b-px4:proxy4_elim:devil_b:A:2 · r124 · 드래곤 #64 L9: 새끼 L7 → 새끼 죽음 r130 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -9
- proxy4_elim · Queen Of Spades · 게임 exp/mapid-b-px4:proxy4_elim:queen_of_spades_b:A:2 · r275 · 드래곤 #0 L4: 새끼 L2 → 새끼 죽음 r275 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_elim · Portals · 게임 exp/mapid-b-px4:proxy4_elim:portals:B:2 · r411 · 드래곤 #394 L8: 새끼 L6 → 새끼 죽음 r421 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -8
- proxy4_elim · Schooltime · 게임 exp/mapid-b-px4:proxy4_elim:schooltime_b:B:2 · r305 · 드래곤 #125 L4: 새끼 L2 → 새끼 죽음 r308 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_elim · Trauma · 게임 exp/mapid-b-px4:proxy4_elim:trauma:B:2 · r247 · 드래곤 #85 L4: 새끼 L2 → 새끼 죽음 r250 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_elim · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_elim:slithery_fight_b:A:2 · r60 · 드래곤 #6 L9: 새끼 L7 → 새끼 죽음 r70 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -9

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 99% · 그 밖(진짜로 갇힘) 43회
- 상대별: proxy4_elim 926회 – · proxy4_king 957회 – · proxy4_swarm 1000회 –
- 지도별: Autarky 1494회 – · Default 4회 – · Devil 6회 – · Portals 285회 – · Prisoners Dilemma (10) 1000회 – · Queen Of Spades 4회 – · Schooltime 14회 – · Slithery Fight 53회 – · Trauma 22회 – · Trophy 1회 –
- 국면별: r0-99 581회 – · r100-249 848회 – · r250-349 596회 – · r350-449 586회 – · r450+ 272회 –

## 정책 분열 (split)

- 이번: 분열 100% · 새끼 30라운드 생존 67% · 30라운드 뒤 가족 길이 변화 1
- 상대별: proxy4_elim 13회 62% · proxy4_king 23회 74% · proxy4_swarm 15회 60%
- 지도별: Default 2회 50% · Devil 4회 100% · Portals 9회 22% · Queen Of Spades 9회 56% · Schooltime 3회 100% · Slithery Fight 13회 77% · Trauma 8회 75% · Trophy 3회 100%
- 국면별: r0-99 9회 67% · r100-249 21회 67% · r250-349 11회 55% · r350-449 10회 80%

실패 사례 (17건 중 10건, 기보 확인용):
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r94 · 드래곤 #10 L9: 새끼 L3 → 새끼 죽음 r106 갇힘, 30라운드 뒤 가족 길이 변화 3
- proxy4_swarm · Trauma · 게임 exp/mapid-b-px4:proxy4_swarm:trauma:B:2 · r419 · 드래곤 #203 L8: 새끼 L2 → 새끼 죽음 r441 돌진, 상대 길이 2, 30라운드 뒤 가족 길이 변화 2
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r305 · 드래곤 #519 L11: 새끼 L3 → 새끼 죽음 r305 돌진, 상대 길이 3, 30라운드 뒤 가족 길이 변화 -1
- proxy4_elim · Queen Of Spades · 게임 exp/mapid-b-px4:proxy4_elim:queen_of_spades_b:A:2 · r157 · 드래곤 #0 L6: 새끼 L2 → 새끼 죽음 r178 박힘(상대 돌진), 상대 길이 3, 30라운드 뒤 가족 길이 변화 -2
- proxy4_elim · Portals · 게임 exp/mapid-b-px4:proxy4_elim:portals:B:2 · r325 · 드래곤 #345 L9: 새끼 L3 → 새끼 죽음 r348 갇힘, 30라운드 뒤 가족 길이 변화 4
- proxy4_elim · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_elim:slithery_fight_b:B:2 · r316 · 드래곤 #438 L18: 새끼 L3 → 새끼 죽음 r316 희생, 30라운드 뒤 가족 길이 변화 -3
- proxy4_king · Default · 게임 exp/mapid-b-px4:proxy4_king:default:B:2 · r392 · 드래곤 #60 L5: 새끼 L2 → 새끼 죽음 r420 아군 머리, 상대 길이 6, 30라운드 뒤 가족 길이 변화 -5
- proxy4_king · Portals · 게임 exp/mapid-b-px4:proxy4_king:portals:A:2 · r124 · 드래곤 #6 L9: 새끼 L3 → 새끼 죽음 r136 갇힘, 30라운드 뒤 가족 길이 변화 -2
- proxy4_king · Queen Of Spades · 게임 exp/mapid-b-px4:proxy4_king:queen_of_spades_b:A:2 · r79 · 드래곤 #0 L5: 새끼 L2 → 새끼 죽음 r104 박힘(상대 돌진), 상대 길이 3, 30라운드 뒤 가족 길이 변화 0
- proxy4_king · Trauma · 게임 exp/mapid-b-px4:proxy4_king:trauma:B:2 · r275 · 드래곤 #88 L5: 새끼 L2 → 새끼 죽음 r276 아군 머리, 상대 길이 3, 30라운드 뒤 가족 길이 변화 -5

## 탈출 질주 3칸 (esc)

- 이번: 질주 98% · 짧은 적 머리 4칸 안 91% · 몸 생존 5라운드 100% · 10라운드 98% (드래곤 자체 96%) · 10라운드 길이 변화 -2.3
- 상대별: proxy4_elim 21회 90% · proxy4_king 11회 100% · proxy4_swarm 14회 100%
- 지도별: Default 3회 100% · Devil 3회 100% · Prisoners Dilemma (10) 1회 100% · Queen Of Spades 2회 100% · Schooltime 3회 100% · Slithery Fight 24회 96% · Trauma 3회 100% · Trophy 7회 86%
- 국면별: r0-99 12회 100% · r100-249 20회 95% · r250-349 11회 100% · r350-449 1회 0% · r450+ 2회 100%

실패 사례 (2건 중 2건, 기보 확인용):
- proxy4_elim · Trophy · 게임 exp/mapid-b-px4:proxy4_elim:trophy:A:2 · r107 · 드래곤 #2 L6: 질주 3칸 (가장 가까운 짧은 적 머리 2칸) → 죽음 r107 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_elim:slithery_fight_b:A:2 · r404 · 드래곤 #790 L7: 질주 3칸 (가장 가까운 짧은 적 머리 5칸) → 죽음 r412 돌진, 상대 길이 19

## 위협 피하기 2칸 질주

- 이번: 질주 98% · 몸 10라운드 생존 92% (드래곤 자체 88%)
- 상대별: proxy4_elim 148회 92% · proxy4_king 145회 88% · proxy4_swarm 168회 92%
- 지도별: Autarky 26회 100% · Default 61회 89% · Devil 28회 86% · Prisoners Dilemma (10) 19회 95% · Queen Of Spades 23회 87% · Schooltime 103회 95% · Slithery Fight 149회 91% · Trauma 22회 100% · Trophy 30회 70%
- 국면별: r0-99 138회 90% · r100-249 199회 89% · r250-349 80회 93% · r350-449 39회 95% · r450+ 5회 100%

실패 사례 (43건 중 10건, 기보 확인용):
- proxy4_swarm · Default · 게임 exp/mapid-b-px4:proxy4_swarm:default:A:2 · r121 · 드래곤 #40 L10: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r130 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Devil · 게임 exp/mapid-b-px4:proxy4_swarm:devil_b:A:2 · r107 · 드래곤 #60 L5: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 3) → 죽음 r117 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Queen Of Spades · 게임 exp/mapid-b-px4:proxy4_swarm:queen_of_spades_b:A:2 · r61 · 드래곤 #2 L10: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r69 아군 머리, 상대 길이 2
- proxy4_swarm · Trophy · 게임 exp/mapid-b-px4:proxy4_swarm:trophy:A:2 · r99 · 드래곤 #0 L5: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r99 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r91 · 드래곤 #30 L13: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 2) → 죽음 r100 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Devil · 게임 exp/mapid-b-px4:proxy4_elim:devil_b:A:2 · r129 · 드래곤 #83 L7: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 3) → 죽음 r130 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Queen Of Spades · 게임 exp/mapid-b-px4:proxy4_elim:queen_of_spades_b:B:2 · r431 · 드래곤 #75 L3: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 2) → 죽음 r434 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Schooltime · 게임 exp/mapid-b-px4:proxy4_elim:schooltime_b:A:2 · r282 · 드래곤 #30 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 3) → 죽음 r291 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Trophy · 게임 exp/mapid-b-px4:proxy4_elim:trophy:A:2 · r99 · 드래곤 #0 L4: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r107 박힘(상대 돌진), 상대 길이 2
- proxy4_elim · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_elim:slithery_fight_b:A:2 · r58 · 드래곤 #10 L4: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r59 박힘(상대 돌진), 상대 길이 3

## 포털 통과 (전체; PORTAL?=미탐색 출구)

- 이번: 미탐색 출구 459회(몸 3라운드 생존 98%) · 전체 몸 생존 3라운드 96% (드래곤 자체 79%) · 10라운드 94% · 10라운드 안 먹은 진주 1
- 상대별: proxy4_elim 325회 97% · proxy4_king 271회 96% · proxy4_swarm 396회 96%
- 지도별: Autarky 62회 98% · Default 119회 92% · Portals 545회 98% · Prisoners Dilemma (10) 35회 100% · Queen Of Spades 18회 67% · Schooltime 75회 95% · Slithery Fight 69회 99% · Trauma 69회 96%
- 국면별: r0-99 239회 100% · r100-249 348회 95% · r250-349 227회 95% · r350-449 155회 95% · r450+ 23회 100%

실패 사례 (38건 중 10건, 기보 확인용):
- proxy4_swarm · Default · 게임 exp/mapid-b-px4:proxy4_swarm:default:B:2 · r104 · 드래곤 #7 L8: 포털 → 죽음 r104 돌진, 상대 길이 2, 10라운드 안 진주 0
- proxy4_swarm · Queen Of Spades · 게임 exp/mapid-b-px4:proxy4_swarm:queen_of_spades_b:A:2 · r166 · 드래곤 #0 L3: 포털 → 죽음 r168 박힘(상대 돌진), 상대 길이 2, 10라운드 안 진주 1
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r247 · 드래곤 #272 L17: 포털(미탐색 출구) → 죽음 r247 갇힘, 상대 길이 2, 10라운드 안 진주 0
- proxy4_swarm · Schooltime · 게임 exp/mapid-b-px4:proxy4_swarm:schooltime_b:A:2 · r173 · 드래곤 #15 L3: 포털(미탐색 출구) → 죽음 r173 돌진, 상대 길이 2, 10라운드 안 진주 0
- proxy4_swarm · Trauma · 게임 exp/mapid-b-px4:proxy4_swarm:trauma:B:2 · r376 · 드래곤 #88 L6: 포털 → 죽음 r376 갇힘, 상대 길이 9, 10라운드 안 진주 0
- proxy4_elim · Default · 게임 exp/mapid-b-px4:proxy4_elim:default:A:2 · r134 · 드래곤 #4 L2: 포털 → 죽음 r134 돌진, 상대 길이 2, 10라운드 안 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_swarm:slithery_fight_b:B:2 · r101 · 드래곤 #23 L12: 포털 → 죽음 r102 갇힘, 상대 길이 13, 10라운드 안 진주 0
- proxy4_elim · Portals · 게임 exp/mapid-b-px4:proxy4_elim:portals:A:2 · r416 · 드래곤 #414 L14: 포털 → 죽음 r416 갇힘, 상대 길이 15, 10라운드 안 진주 0
- proxy4_elim · Queen Of Spades · 게임 exp/mapid-b-px4:proxy4_elim:queen_of_spades_b:A:2 · r43 · 드래곤 #2 L9: 포털 → 죽음 r43 돌진, 상대 길이 3, 10라운드 안 진주 0
- proxy4_elim · Schooltime · 게임 exp/mapid-b-px4:proxy4_elim:schooltime_b:B:2 · r333 · 드래곤 #17 L2: 포털 → 죽음 r333 돌진, 상대 길이 3, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 2, 경로 9) · 잡은 길이 ≥ 우리 100% · 두 몸의 진주 우리 41 대 상대 55
- 상대별: proxy4_elim 1회 0% · proxy4_king 5회 40% · proxy4_swarm 5회 60%
- 지도별: Devil 1회 0% · Queen Of Spades 1회 0% · Schooltime 2회 50% · Slithery Fight 6회 50% · Trauma 1회 100%
- 국면별: r100-249 1회 100% · r250-349 4회 0% · r350-449 5회 60% · r450+ 1회 100%

실패 사례 (6건 중 6건, 기보 확인용):
- proxy4_swarm · Schooltime · 게임 exp/mapid-b-px4:proxy4_swarm:schooltime_b:A:2 · r338 · 드래곤 #137 L4: 돌진 경로 2칸 → 상대 L7 잡음, 진주 우리 0 대 상대 6
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r340 · 드래곤 #519 L6: 돌진 경로 3칸 → 상대 L14 잡음, 진주 우리 1 대 상대 9
- proxy4_elim · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_elim:slithery_fight_b:A:2 · r412 · 드래곤 #790 L5: 돌진 경로 3칸 → 상대 L19 잡음, 진주 우리 2 대 상대 9
- proxy4_king · Devil · 게임 exp/mapid-b-px4:proxy4_king:devil_b:B:2 · r315 · 드래곤 #197 L4: 돌진 경로 3칸 → 상대 L5 잡음, 진주 우리 0 대 상대 5
- proxy4_king · Queen Of Spades · 게임 exp/mapid-b-px4:proxy4_king:queen_of_spades_b:B:2 · r366 · 드래곤 #3 L5: 돌진 경로 4칸 → 상대 L8 잡음, 진주 우리 0 대 상대 6
- proxy4_king · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_king:slithery_fight_b:A:2 · r294 · 드래곤 #212 L4: 돌진 경로 2칸 → 상대 L15 잡음, 진주 우리 0 대 상대 10

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 상대별: proxy4_elim 15회 100% · proxy4_king 16회 100% · proxy4_swarm 17회 100%
- 지도별: Autarky 6회 100% · Default 3회 100% · Devil 2회 100% · Portals 9회 100% · Prisoners Dilemma (10) 1회 100% · Queen Of Spades 2회 100% · Schooltime 7회 100% · Slithery Fight 13회 100% · Trauma 5회 100%
- 국면별: r0-99 6회 100% · r100-249 15회 100% · r250-349 15회 100% · r350-449 12회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 50%
- 상대별: proxy4_swarm 2회 –
- 지도별: Slithery Fight 1회 – · Trauma 1회 –
- 국면별: r350-449 2회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 1회 – · proxy4_king 12회 – · proxy4_swarm 10회 –
- 지도별: Autarky 2회 – · Devil 7회 – · Schooltime 3회 – · Slithery Fight 6회 – · Trauma 5회 –
- 국면별: r100-249 13회 – · r250-349 6회 – · r350-449 4회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/mapid-b-px4` | 60 | 41 (0.68) | 76% | 4 (0.07) | 0 (0.00) | 2 | 27 | 7 | 0/0 (0) | 19 (0.32; 필사 4) | 4/10 (14) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/mapid-b-px4` | 60 | 36937 | 0.8% (299) | 14.5% (5368) | 3242 | 1.3% (41) | 2.5% (82) | 29.4% (954/3242) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/mapid-b-px4` | 전체 | 분열 | 13 (14%) | 13.8 | 71% | 50% | 6 | 2 |
| 이번 `exp/mapid-b-px4` | 전체 | 2칸 질주 | 36 (38%) | 12 | 70% | 60% | 11 | 9 |
| 이번 `exp/mapid-b-px4` | 전체 | 3칸 질주 | 24 (26%) | 8.2 | 77% | 50% | 2 | 1 |
| 이번 `exp/mapid-b-px4` | 전체 | 한 걸음 | 21 (22%) | 10.8 | 33% | 28% | 17 | 13 |
| 이번 `exp/mapid-b-px4` | 4칸 이상 | 분열 | 4 (12%) | 10 | 98% | 80% | 1 | 0 |
| 이번 `exp/mapid-b-px4` | 4칸 이상 | 2칸 질주 | 15 (44%) | 10.9 | 79% | 60% | 4 | 2 |
| 이번 `exp/mapid-b-px4` | 4칸 이상 | 3칸 질주 | 6 (18%) | 8.5 | 78% | 75% | 0 | 0 |
| 이번 `exp/mapid-b-px4` | 4칸 이상 | 한 걸음 | 9 (26%) | 12.8 | 63% | 55% | 6 | 2 |

사각 박힘 (4건 중 4건, 기보 확인용):
- proxy4_swarm · Trophy · 게임 exp/mapid-b-px4:proxy4_swarm:trophy:B:2 · r161 · 드래곤 #1 L24: 결정 "WN v3.7 d7 L25" → 가해자 #12 L3 2걸음 (path through a tile occupied at the decision)
- proxy4_elim · Devil · 게임 exp/mapid-b-px4:proxy4_elim:devil_b:B:2 · r139 · 드래곤 #1 L8: 결정 "WW v2.7 d7 L9" → 가해자 #37 L3 2걸음 (path through a tile occupied at the decision)
- proxy4_elim · Slithery Fight · 게임 exp/mapid-b-px4:proxy4_elim:slithery_fight_b:B:2 · r279 · 드래곤 #15 L28: 결정 "WS v3.7 d7 L29" → 가해자 #357 L3 2걸음 (path through a tile occupied at the decision)
- proxy4_king · Schooltime · 게임 exp/mapid-b-px4:proxy4_king:schooltime_b:A:2 · r214 · 드래곤 #17 L6: 결정 "WW v4.2 d7 L7" → 가해자 #49 L3 1걸음 (path through a tile occupied at the decision)

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (19건 중 10건):
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r150 · 드래곤 #37 L7: v-8.6 → 갇힘, 막은 우리 드래곤 L14
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r240 · 드래곤 #110 L3: v-0.1 → 갇힘, 막은 우리 드래곤 L12
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:A:2 · r413 · 드래곤 #423 L15: v1.2 → 갇힘, 막은 우리 드래곤 L14
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:B:2 · r271 · 드래곤 #360 L14: v0.9 → 갇힘, 막은 우리 드래곤 L13
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:B:2 · r319 · 드래곤 #377 L14: v-8.2 → 갇힘, 막은 우리 드래곤 L3
- proxy4_swarm · Portals · 게임 exp/mapid-b-px4:proxy4_swarm:portals:B:2 · r469 · 드래곤 #547 L3: v0.5 → 갇힘, 막은 우리 드래곤 L12
- proxy4_swarm · Trauma · 게임 exp/mapid-b-px4:proxy4_swarm:trauma:B:2 · r376 · 드래곤 #88 L6: v-3.1 → 갇힘, 막은 우리 드래곤 L9
- proxy4_elim · Portals · 게임 exp/mapid-b-px4:proxy4_elim:portals:A:2 · r416 · 드래곤 #414 L14: v-1.3 → 갇힘, 막은 우리 드래곤 L15
- proxy4_elim · Portals · 게임 exp/mapid-b-px4:proxy4_elim:portals:A:2 · r478 · 드래곤 #439 L3: v2.7 → 갇힘, 막은 우리 드래곤 L30
- proxy4_elim · Portals · 게임 exp/mapid-b-px4:proxy4_elim:portals:A:2 · r498 · 드래곤 #443 L3: v4 → 갇힘, 막은 우리 드래곤 L29

## 지도·판본 인식 상세 (cand-mapid)

이번 (60판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 6 | 100% | 100% | 36/36 (36) | 1558 | 1558 (0) | 0 | 0 | 0 | 0 |
| Default a | 6 | 100% | 100% | 24/24 (24) | 35 | 35 (0) | 0 | 0 | 0 | 0 |
| Devil b | 6 | 100% | 100% | 18/18 (18) | 41 | 37 (0) | 3 | 0 | 0 | 4 |
| Portals a | 6 | 100% | 100% | 18/18 (18) | 383 | 383 (0) | 0 | 0 | 0 | 0 |
| Prisoners Dilemma b | 6 | 100% | 100% | 18/30 (18) | 1027 | 1023 (0) | 4 | 0 | 0 | 91 |
| Queen Of Spades b | 6 | 100% | 100% | 12/12 (12) | 25 | 21 (0) | 2 | 0 | 0 | 24 |
| Schooltime b | 6 | 100% | 100% | 36/36 (36) | 102 | 102 (0) | 0 | 0 | 0 | 9 |
| Slithery Fight b | 6 | 100% | 100% | 48/48 (48) | 135 | 129 (0) | 6 | 0 | 0 | 14 |
| Trauma a | 6 | 100% | 100% | 12/12 (12) | 64 | 63 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 6 | 100% | 100% | 12/12 (12) | 16 | 16 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 60/60, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

### Schooltime 판의 경제 (bsp의 가설 수준 지표, 정답 판본별)

| 묶음 | 판본 | 판 | 드래곤 수 r50 | r100 | r0–99 자연 진주 먹음 | 전멸당함 | 끝 최장(전멸 0) | 판당 bsp 분열 |
|---|---|---:|---|---|---|---:|---|---:|
| 이번 | b | 6 | 8 [7, 8] | 12 [7, 12] | 15 [7, 18] | 0% | 12 [9, 12] | 12.2 |

- 기준값(`research/experiments/cand-mapid.md`, 웨이브 전에 적음): b에서 드래곤 수 r50 중앙 ≥ 6, r0–99 자연 진주 중앙 ≥ 14. 우리 merge2 계열 b 29판은 3 · 9, 떼 계열(swarm8·px) b 14판은 6 · 14, 상위권 b 승자는 8 · 32다. a는 bsp가 켜지지 않는 대조군이다.

