# 구현 적용 확인

- 대상: `exp/mapid-a-px4` 60판
- 기준(사용자 규칙 2026-09-30): 승률이 아니라, 봇에 구현한 기능이 이 상대들에게 실제로 발동하고 의도대로 작동했는지를 본다.
- "의도대로"의 정의: 모이기=왕 3칸 안까지 가거나 희생까지 함 · 희생=떨군 진주 절반 이상을 우리 팀이 먹고 상대는 못 먹음 · 한입=2턴 안 분열하고 30라운드 뒤 가족 길이가 줄지 않음 · 탈출 분열=10라운드 뒤 몸이 살아 있음 · 정책 분열=새끼 30라운드 생존 · 탈출 질주·위협 피하기=10라운드 뒤 몸 생존 · 포털=3라운드 뒤 몸 생존 · 돌진=충돌 성사, 잡은 길이 ≥ 우리, 두 몸의 진주를 우리가 더 먹음 · 먹이 질주=진주 먹음.
- "몸"은 그 드래곤과 그 뒤 분열로 태어난 자손 전체다. 통로 고리처럼 몸을 새끼에게 넘기며 버티는 경우를 손실로 세지 않기 위해서다.
- stack2의 "의도대로": 조각 떼기=조각이 30라운드 살며 진주를 1개 이상 먹거나, 나중에 희생(feed·conv)으로 아군을 먹임 · 새 사망 진주 줍기=표적이 된 사망 진주(진주 하나가 한 건)를 우리 팀이 먹음(자연 진주로 오인했거나 이미 없던 표적은 판정에서 뺌).
- cand-mapid의 "의도대로": Schooltime b 초반 분열(bsp)=떼어 낸 조각(새 유닛)이 10라운드 뒤 살아 있음 · 지도·판본 인식=그 판에서 1개 이상의 프로세스가 판본까지 결정했고, 결정한 프로세스(마지막 표식 기준)가 모두 정답 지도·판본을 댐. 정답 판본은 로컬이면 지도 파일 이름, 온라인이면 기보의 자연 생성(한쪽 판본에서만 생성하는 칸)으로 정하고, 끝까지 가릴 수 없던 판은 뺀다. 지도별 줄의 이름 뒤 a·b·?가 정답 판본이다.

## 요약

| 기능 | 발동(판당) | 의도대로 | 
|---|---:|---:|
| 지도·판본 인식 (map=, cand-mapid; 판 단위) | 60 (1) | 100% | 
| 큰 아군 곁 희생 (conv, stack1 M1) | 66 (1.1) | 98% | 
| 조각 떼기 (split frag, stack2 S1) | 84 (1.4) | 77% | 
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 561 (9.4) | 74% | 
| 왕에게 모이기 (g, 드래곤 단위) | 390 (6.5) | 77% | 
| 희생 먹이기 (feed) | 56 (0.9) | 75% | 
| 막다른 길 한입 (pocket-eat) | 2 (0) | 0% | 
| 탈출 분열 (escape-split) | 3419 (57) | 99% | 
| 출구 없음 (no-exit) | 3309 (55.2) | – | 
| 정책 분열 (split) | 68 (1.1) | 65% | 
| 탈출 질주 3칸 (esc) | 76 (1.3) | 96% | 
| 위협 피하기 2칸 질주 | 483 (8.1) | 89% | 
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 856 (14.3) | 96% | 
| 돌진 (TRADE) | 16 (0.3) | 19% | 
| 먹이 질주 (2칸 이상, 먹은 것) | 83 (1.4) | 100% | 
| 기타 2칸 질주 | 3 (0.1) | – | 
| 마지막 돌진 (last-trade) | 7 (0.1) | – | 

- 건강: 턴 83711, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 4165턴 · 끝판(late) 2913턴 · 돌진 신뢰(T, 탈출 끔) 149턴, 그 직후 박혀 죽음 1

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 
|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 2% (11/703턴) | 
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 15.8칸 (3.5회), 진주 우리 92% · 상대 2% | 
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 1.1칸 (판당 0.03회) | 
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 21% (705/3284턴) | 
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.033회 (2건, 50칸) | 
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 4마리 (26판) | 
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 13.7회 | 
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 63% (우리 30%) | 
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 4.1 대 상대 14.9 (3.9회) · 박힌 교환의 우리 몫 23% (100회) | 
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 3.4개 | 

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 지도·판본 인식 (map=, cand-mapid; 판 단위)

- 이번: 판본을 기보로 가릴 수 있는 판 60/60 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 94%, 그중 정답 100% · 프로세스 3781: 표식 없음 1, 결정 3766 (정답 100%, 틀림 0), 가족만 14, 모름 0, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 82라운드
- 상대별: proxy4_elim 20회 100% · proxy4_king 20회 100% · proxy4_swarm 20회 100%
- 지도별: Autarky a 6회 100% · Default a 6회 100% · Devil a 6회 100% · Portals a 6회 100% · Prisoners Dilemma a 6회 100% · Queen Of Spades a 6회 100% · Schooltime a 6회 100% · Slithery Fight a 6회 100% · Trauma a 6회 100% · Trophy a 6회 100%
- 국면별: r0-99 60회 100%

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 91개 중 우리 팀 99% (지목한 아군 78%) · 상대 1% · 지목 아군 끝까지 생존 38% (그 뒤 죽은 원인: 갇힘 27, 희생 8, 아군 머리 1, 박힘(상대 돌진) 5) · 지목 아군의 몸(자손 포함)이 끝까지 삶 83% · 최종 왕 30% (최종 왕이 지목 아군의 자손 53%)
- 상대별: proxy4_elim 26회 100% · proxy4_king 26회 96% · proxy4_swarm 14회 100%
- 지도별: Autarky 10회 100% · Portals 13회 100% · Prisoners Dilemma 7회 100% · Queen Of Spades 1회 100% · Slithery Fight 34회 97% · Trauma 1회 100%
- 국면별: r250-349 32회 100% · r350-449 30회 97% · r450+ 4회 100%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_king · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_king:slithery_fight:B:1 · r350 · 드래곤 #693 L2: #760(L37)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 1; 지목 아군 r494 박힘(상대 돌진)에 사망

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 98% · 조각 30라운드 생존 68% · 30라운드 안 1개 이상 먹음 43% (살아서 먹음 31%) · 평생 먹은 진주 평균 2.7 · 나중에 아군을 먹임 65% (conv 38, feed 17, 분열 뒤 평균 58.5라운드) · 끝까지 생존 11% · 30라운드 안 죽은 원인: 희생 17, 갇힘 8, 박힘(상대 돌진) 2
- 상대별: proxy4_elim 30회 73% · proxy4_king 29회 79% · proxy4_swarm 25회 80%
- 지도별: Autarky 18회 94% · Default 1회 100% · Portals 6회 100% · Prisoners Dilemma 2회 50% · Slithery Fight 52회 73% · Trauma 5회 40%
- 국면별: r250-349 58회 86% · r350-449 26회 58%

실패 사례 (19건 중 10건, 기보 확인용):
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:A:1 · r279 · 드래곤 #202 L10: 조각 L2 → 조각 죽음 r284 갇힘, 상대 길이 26, 30라운드 안 먹은 진주 0
- proxy4_swarm · Trauma · 게임 exp/mapid-a-px4:proxy4_swarm:trauma:B:1 · r394 · 드래곤 #157 L8: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Prisoners Dilemma · 게임 exp/mapid-a-px4:proxy4_elim:prisoners_dilemma:A:1 · r345 · 드래곤 #224 L23: 조각 L2 → 조각 죽음 r349 갇힘, 상대 길이 21, 30라운드 안 먹은 진주 1 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_elim · Trauma · 게임 exp/mapid-a-px4:proxy4_elim:trauma:A:1 · r386 · 드래곤 #96 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_king · Autarky · 게임 exp/mapid-a-px4:proxy4_king:autarky:B:1 · r327 · 드래곤 #260 L7: 조각 L2 → 조각 죽음 r332 갇힘, 상대 길이 16, 30라운드 안 먹은 진주 0
- proxy4_elim · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_elim:slithery_fight:B:1 · r290 · 드래곤 #557 L7: 조각 L2 → 조각 죽음 r311 갇힘, 30라운드 안 먹은 진주 1
- proxy4_king · Trauma · 게임 exp/mapid-a-px4:proxy4_king:trauma:A:1 · r356 · 드래곤 #135 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_king · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_king:slithery_fight:A:1 · r262 · 드래곤 #581 L18: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:A:1 · r330 · 드래곤 #550 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:A:1 · r401 · 드래곤 #594 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 561개 (표식 턴 1362, 진주당 드래곤 1.1) · 질량 장부의 사망 진주 95% (자연 진주 0, 이미 없음 28) · 사망 진주 533개 중 우리가 먹음 74% · 상대 23% · 아무도 안 먹음 2% · 표적으로 삼은 드래곤이 먹음 65% · 우리가 먹기까지 평균 4.6라운드 · 상대 머리가 같거나 더 가까웠던 169개: 우리 43% 대 상대 54% · 박치기 진주 103개: 우리 66% 대 상대 34% · 우리 팀 사망 진주 76% · 사망 뒤 첫 표적까지 평균 1.6라운드
- 상대별: proxy4_elim 174회 78% · proxy4_king 213회 74% · proxy4_swarm 174회 72%
- 지도별: Autarky 54회 94% · Default 26회 52% · Devil 24회 50% · Portals 81회 94% · Prisoners Dilemma 32회 90% · Queen Of Spades 42회 74% · Schooltime 23회 48% · Slithery Fight 248회 71% · Trauma 23회 55% · Trophy 8회 50%
- 국면별: r0-99 90회 64% · r100-249 158회 65% · r250-349 127회 81% · r350-449 145회 88% · r450+ 41회 66%

실패 사례 (136건 중 10건, 기보 확인용):
- proxy4_swarm · Default · 게임 exp/mapid-a-px4:proxy4_swarm:default:A:1 · r178 · 드래곤 #4 L2: 진주 (7,24), 우리 머리 6칸 · 상대 머리 4칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (3라운드 뒤), 표식 2턴
- proxy4_swarm · Autarky · 게임 exp/mapid-a-px4:proxy4_swarm:autarky:B:1 · r346 · 드래곤 #9 L34: 진주 (47,3), 우리 머리 2칸 · 상대 머리 8칸, 우리 팀 사망 6라운드 뒤 → 아무도 안 먹음, 표식 1턴
- proxy4_swarm · Devil · 게임 exp/mapid-a-px4:proxy4_swarm:devil:B:1 · r180 · 드래곤 #48 L2: 진주 (23,6), 우리 머리 4칸 · 상대 머리 1칸, 상대 사망 1라운드 뒤 → 아무도 안 먹음, 표식 1턴
- proxy4_swarm · Queen Of Spades · 게임 exp/mapid-a-px4:proxy4_swarm:queen_of_spades:A:1 · r47 · 드래곤 #8 L3: 진주 (11,33), 우리 머리 6칸 · 상대 머리 1칸, 우리 팀 사망 4라운드 뒤 → 상대가 먹음 (192라운드 뒤), 표식 2턴
- proxy4_swarm · Prisoners Dilemma · 게임 exp/mapid-a-px4:proxy4_swarm:prisoners_dilemma:B:1 · r217 · 드래곤 #186 L2: 진주 (16,7), 우리 머리 3칸 · 상대 머리 2칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (1라운드 뒤), 표식 1턴
- proxy4_swarm · Trauma · 게임 exp/mapid-a-px4:proxy4_swarm:trauma:A:1 · r143 · 드래곤 #0 L4: 진주 (18,16), 우리 머리 2칸 · 상대 머리 1칸, 상대 사망 3라운드 뒤 → 상대가 먹음 (33라운드 뒤), 표식 3턴
- proxy4_swarm · Schooltime · 게임 exp/mapid-a-px4:proxy4_swarm:schooltime:B:1 · r406 · 드래곤 #5 L6: 진주 (38,16), 우리 머리 6칸 · 상대 머리 2칸, 상대 사망 3라운드 뒤 → 상대가 먹음 (6라운드 뒤), 표식 1턴
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:A:1 · r4 · 드래곤 #23 L2: 진주 (33,5), 우리 머리 5칸 · 상대 머리 10칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (84라운드 뒤), 표식 1턴
- proxy4_elim · Devil · 게임 exp/mapid-a-px4:proxy4_elim:devil:A:1 · r152 · 드래곤 #2 L8: 진주 (8,12), 우리 머리 4칸 · 상대 머리 1칸, 상대 사망 3라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_elim · Autarky · 게임 exp/mapid-a-px4:proxy4_elim:autarky:A:1 · r70 · 드래곤 #4 L2: 진주 (31,16), 우리 머리 3칸 · 상대 머리 3칸, 박치기 1라운드 뒤 → 상대가 먹음 (3라운드 뒤), 표식 2턴

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 390 (그중 통로 고리 세대 304, 판정에서 뺌) · 고리 밖 86: 처음 거리 평균 11.6 → 최소 5.7 · 3칸 안까지 감 43% · 희생까지 함 44% · 가는 길에 죽음 10% · 끝까지 생존 45%
- 상대별: proxy4_elim 142회 75% · proxy4_king 183회 76% · proxy4_swarm 65회 81%
- 지도별: Autarky 162회 81% · Devil 2회 – · Portals 84회 79% · Prisoners Dilemma 76회 90% · Queen Of Spades 3회 0% · Slithery Fight 50회 77% · Trauma 13회 57%
- 국면별: r250-349 90회 92% · r350-449 233회 82% · r450+ 67회 53%

실패 사례 (30건 중 10건, 기보 확인용):
- proxy4_swarm · Portals · 게임 exp/mapid-a-px4:proxy4_swarm:portals:B:1 · r428 · 드래곤 #403 L8: 왕까지 거리 11 → 최소 9 (3턴)
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:A:1 · r446 · 드래곤 #888 L4: 왕까지 거리 22 → 최소 21 (16턴)
- proxy4_swarm · Trauma · 게임 exp/mapid-a-px4:proxy4_swarm:trauma:B:1 · r479 · 드래곤 #221 L4: 왕까지 거리 19 → 최소 18 (2턴)
- proxy4_elim · Portals · 게임 exp/mapid-a-px4:proxy4_elim:portals:B:1 · r454 · 드래곤 #441 L11: 왕까지 거리 8 → 최소 4 (38턴)
- proxy4_elim · Prisoners Dilemma · 게임 exp/mapid-a-px4:proxy4_elim:prisoners_dilemma:A:1 · r344 · 드래곤 #224 L23: 왕까지 거리 6 → 최소 6 (6턴)
- proxy4_elim · Trauma · 게임 exp/mapid-a-px4:proxy4_elim:trauma:A:1 · r426 · 드래곤 #141 L4: 왕까지 거리 27 → 최소 5 (25턴)
- proxy4_king · Autarky · 게임 exp/mapid-a-px4:proxy4_king:autarky:B:1 · r390 · 드래곤 #365 L4: 왕까지 거리 20 → 최소 6 (6턴), 가는 길에 죽음 r396 희생
- proxy4_elim · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_elim:slithery_fight:B:1 · r356 · 드래곤 #295 L16: 왕까지 거리 21 → 최소 18 (56턴), 가는 길에 죽음 r420 돌진, 상대 길이 21
- proxy4_king · Portals · 게임 exp/mapid-a-px4:proxy4_king:portals:A:1 · r378 · 드래곤 #421 L4: 왕까지 거리 6 → 최소 5 (18턴), 가는 길에 죽음 r396 갇힘, 상대 길이 40
- proxy4_king · Queen Of Spades · 게임 exp/mapid-a-px4:proxy4_king:queen_of_spades:B:1 · r474 · 드래곤 #176 L23: 왕까지 거리 10 → 최소 9 (18턴)

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 209개 중 우리 팀 84% (지목한 아군 65%) · 상대 4% · 지목 아군 끝까지 생존 66% (그 뒤 죽은 원인: 갇힘 9, 희생 8, 박힘(상대 돌진) 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 93% · 최종 왕 52% (최종 왕이 지목 아군의 자손 77%)
- 상대별: proxy4_elim 21회 76% · proxy4_king 15회 87% · proxy4_swarm 20회 65%
- 지도별: Autarky 13회 100% · Default 1회 100% · Portals 13회 54% · Prisoners Dilemma 5회 60% · Queen Of Spades 1회 0% · Slithery Fight 19회 74% · Trauma 4회 100%
- 국면별: r250-349 11회 91% · r350-449 26회 92% · r450+ 19회 42%

실패 사례 (14건 중 10건, 기보 확인용):
- proxy4_swarm · Portals · 게임 exp/mapid-a-px4:proxy4_swarm:portals:A:1 · r486 · 드래곤 #399 L2: #403(L2)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0; 지목 아군 r494 희생에 사망
- proxy4_swarm · Prisoners Dilemma · 게임 exp/mapid-a-px4:proxy4_swarm:prisoners_dilemma:B:1 · r495 · 드래곤 #449 L10: #213(L29)에게 희생 → 진주 5개 중 우리 1, 지목 아군 1, 상대 1
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:A:1 · r431 · 드래곤 #594 L7: #851(L19)에게 희생 → 진주 4개 중 우리 2, 지목 아군 2, 상대 2; 지목 아군 r461 갇힘에 사망
- proxy4_elim · Portals · 게임 exp/mapid-a-px4:proxy4_elim:portals:B:1 · r497 · 드래곤 #445 L2: #437(L18)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0; 지목 아군 r498 희생에 사망
- proxy4_elim · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_elim:slithery_fight:A:1 · r493 · 드래곤 #1019 L6: #1036(L10)에게 희생 → 진주 3개 중 우리 1, 지목 아군 1, 상대 0
- proxy4_king · Prisoners Dilemma · 게임 exp/mapid-a-px4:proxy4_king:prisoners_dilemma:B:1 · r441 · 드래곤 #399 L10: #278(L13)에게 희생 → 진주 5개 중 우리 3, 지목 아군 1, 상대 2; 지목 아군 r448 박힘(상대 돌진)에 사망
- proxy4_king · Queen Of Spades · 게임 exp/mapid-a-px4:proxy4_king:queen_of_spades:B:1 · r499 · 드래곤 #172 L9: #176(L25)에게 희생 → 진주 5개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Portals · 게임 exp/mapid-a-px4:proxy4_swarm:portals:A:1 · r498 · 드래곤 #413 L2: #419(L29)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:A:1 · r474 · 드래곤 #347 L4: #947(L24)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:A:1 · r490 · 드래곤 #550 L8: #947(L25)에게 희생 → 진주 4개 중 우리 2, 지목 아군 2, 상대 1

## 막다른 길 한입 (pocket-eat)

- 이번: 한입 100% · 2턴 안 분열 100% · 30라운드 뒤 가족 길이 변화 -2.5 (줄지 않음 0%)
- 상대별: proxy4_elim 2회 0%
- 지도별: Devil 2회 0%
- 국면별: r350-449 1회 0% · r450+ 1회 0%

실패 사례 (2건 중 2건, 기보 확인용):
- proxy4_elim · Devil · 게임 exp/mapid-a-px4:proxy4_elim:devil:B:1 · r441 · 드래곤 #424 L8: 한입, 분열(새끼 L7), 30라운드 뒤 가족 길이 변화 -1
- proxy4_elim · Devil · 게임 exp/mapid-a-px4:proxy4_elim:devil:B:1 · r453 · 드래곤 #425 L9: 한입, 분열(새끼 L8), 30라운드 뒤 가족 길이 변화 -4

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 99% · 새끼 자체 10라운드 생존 11% · 30라운드 뒤 가족 길이 변화 9.7
- 상대별: proxy4_elim 1173회 99% · proxy4_king 1121회 99% · proxy4_swarm 1125회 99%
- 지도별: Autarky 1506회 100% · Default 9회 100% · Devil 30회 87% · Portals 189회 96% · Prisoners Dilemma 1483회 99% · Queen Of Spades 29회 97% · Schooltime 11회 91% · Slithery Fight 130회 98% · Trauma 26회 92% · Trophy 6회 50%
- 국면별: r0-99 733회 100% · r100-249 1010회 99% · r250-349 666회 99% · r350-449 687회 99% · r450+ 323회 98%

실패 사례 (30건 중 10건, 기보 확인용):
- proxy4_swarm · Devil · 게임 exp/mapid-a-px4:proxy4_swarm:devil:A:1 · r157 · 드래곤 #30 L4: 새끼 L2 → 새끼 죽음 r158 박힘(상대 돌진), 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Queen Of Spades · 게임 exp/mapid-a-px4:proxy4_swarm:queen_of_spades:A:1 · r146 · 드래곤 #37 L13: 새끼 L11 → 새끼 죽음 r148 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -13
- proxy4_swarm · Portals · 게임 exp/mapid-a-px4:proxy4_swarm:portals:B:1 · r329 · 드래곤 #29 L6: 새끼 L4 → 새끼 죽음 r332 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -6
- proxy4_swarm · Prisoners Dilemma · 게임 exp/mapid-a-px4:proxy4_swarm:prisoners_dilemma:B:1 · r487 · 드래곤 #438 L12: 새끼 L10 → 새끼 죽음 r491 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -12
- proxy4_swarm · Trophy · 게임 exp/mapid-a-px4:proxy4_swarm:trophy:A:1 · r78 · 드래곤 #26 L11: 새끼 L9 → 새끼 죽음 r79 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -11
- proxy4_elim · Portals · 게임 exp/mapid-a-px4:proxy4_elim:portals:B:1 · r197 · 드래곤 #203 L4: 새끼 L2 → 새끼 죽음 r206 갇힘, 상대 길이 7, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_elim · Devil · 게임 exp/mapid-a-px4:proxy4_elim:devil:B:1 · r275 · 드래곤 #313 L4: 새끼 L2 → 새끼 죽음 r281 박힘(상대 돌진), 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_elim · Schooltime · 게임 exp/mapid-a-px4:proxy4_elim:schooltime:B:1 · r169 · 드래곤 #1 L14: 새끼 L12 → 새끼 죽음 r171 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -14
- proxy4_elim · Trophy · 게임 exp/mapid-a-px4:proxy4_elim:trophy:B:1 · r102 · 드래곤 #3 L6: 새끼 L4 → 새끼 죽음 r110 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -6
- proxy4_elim · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_elim:slithery_fight:A:1 · r160 · 드래곤 #307 L24: 새끼 L22 → 새끼 죽음 r166 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -24

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 99% · 그 밖(진짜로 갇힘) 49회
- 상대별: proxy4_elim 1132회 – · proxy4_king 1078회 – · proxy4_swarm 1099회 –
- 지도별: Autarky 1497회 – · Default 3회 – · Devil 15회 – · Portals 168회 – · Prisoners Dilemma 1475회 – · Queen Of Spades 25회 – · Schooltime 9회 – · Slithery Fight 99회 – · Trauma 17회 – · Trophy 1회 –
- 국면별: r0-99 698회 – · r100-249 976회 – · r250-349 653회 – · r350-449 676회 – · r450+ 306회 –

## 정책 분열 (split)

- 이번: 분열 100% · 새끼 30라운드 생존 65% · 30라운드 뒤 가족 길이 변화 1
- 상대별: proxy4_elim 31회 61% · proxy4_king 21회 62% · proxy4_swarm 16회 75%
- 지도별: Default 3회 0% · Devil 3회 67% · Portals 16회 50% · Queen Of Spades 12회 50% · Schooltime 17회 88% · Slithery Fight 8회 100% · Trauma 5회 80% · Trophy 4회 25%
- 국면별: r0-99 14회 36% · r100-249 32회 72% · r250-349 16회 69% · r350-449 6회 83%

실패 사례 (24건 중 10건, 기보 확인용):
- proxy4_swarm · Default · 게임 exp/mapid-a-px4:proxy4_swarm:default:A:1 · r242 · 드래곤 #0 L33: 새끼 L2 → 새끼 죽음 r264 박힘(상대 돌진), 상대 길이 3, 30라운드 뒤 가족 길이 변화 -33
- proxy4_swarm · Queen Of Spades · 게임 exp/mapid-a-px4:proxy4_swarm:queen_of_spades:A:1 · r34 · 드래곤 #2 L9: 새끼 L2 → 새끼 죽음 r43 갇힘, 30라운드 뒤 가족 길이 변화 11
- proxy4_swarm · Portals · 게임 exp/mapid-a-px4:proxy4_swarm:portals:A:1 · r321 · 드래곤 #342 L24: 새끼 L3 → 새끼 죽음 r332 갇힘, 30라운드 뒤 가족 길이 변화 15
- proxy4_swarm · Trauma · 게임 exp/mapid-a-px4:proxy4_swarm:trauma:A:1 · r394 · 드래곤 #128 L7: 새끼 L2 → 새끼 죽음 r408 돌진, 상대 길이 4, 30라운드 뒤 가족 길이 변화 -4
- proxy4_elim · Default · 게임 exp/mapid-a-px4:proxy4_elim:default:B:1 · r124 · 드래곤 #3 L15: 새끼 L2 → 새끼 죽음 r132 갇힘, 상대 길이 11, 30라운드 뒤 가족 길이 변화 -1
- proxy4_elim · Portals · 게임 exp/mapid-a-px4:proxy4_elim:portals:B:1 · r190 · 드래곤 #180 L12: 새끼 L3 → 새끼 죽음 r198 갇힘, 30라운드 뒤 가족 길이 변화 3
- proxy4_elim · Queen Of Spades · 게임 exp/mapid-a-px4:proxy4_elim:queen_of_spades:A:1 · r39 · 드래곤 #2 L10: 새끼 L2 → 새끼 죽음 r42 아군 머리, 상대 길이 8, 30라운드 뒤 가족 길이 변화 -10
- proxy4_elim · Schooltime · 게임 exp/mapid-a-px4:proxy4_elim:schooltime:B:1 · r66 · 드래곤 #5 L13: 새끼 L3 → 새끼 죽음 r88 박힘(상대 돌진), 상대 길이 3, 30라운드 뒤 가족 길이 변화 -2
- proxy4_elim · Trophy · 게임 exp/mapid-a-px4:proxy4_elim:trophy:A:1 · r48 · 드래곤 #10 L9: 새끼 L3 → 새끼 죽음 r58 박힘(상대 돌진), 상대 길이 2, 30라운드 뒤 가족 길이 변화 -9
- proxy4_king · Devil · 게임 exp/mapid-a-px4:proxy4_king:devil:A:1 · r116 · 드래곤 #95 L6: 새끼 L2 → 새끼 죽음 r121 박힘(상대 돌진), 상대 길이 3, 30라운드 뒤 가족 길이 변화 -2

## 탈출 질주 3칸 (esc)

- 이번: 질주 99% · 짧은 적 머리 4칸 안 84% · 몸 생존 5라운드 99% · 10라운드 97% (드래곤 자체 97%) · 10라운드 길이 변화 -2.2
- 상대별: proxy4_elim 20회 95% · proxy4_king 30회 97% · proxy4_swarm 26회 96%
- 지도별: Autarky 1회 100% · Default 5회 100% · Devil 8회 100% · Prisoners Dilemma 1회 100% · Queen Of Spades 7회 86% · Schooltime 19회 100% · Slithery Fight 30회 93% · Trophy 5회 100%
- 국면별: r0-99 15회 93% · r100-249 27회 93% · r250-349 9회 100% · r350-449 11회 100% · r450+ 14회 100%

실패 사례 (3건 중 3건, 기보 확인용):
- proxy4_swarm · Queen Of Spades · 게임 exp/mapid-a-px4:proxy4_swarm:queen_of_spades:B:1 · r207 · 드래곤 #1 L8: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r217 박힘(상대 돌진), 상대 길이 2
- proxy4_elim · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_elim:slithery_fight:A:1 · r212 · 드래곤 #470 L6: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r212 아군 머리, 상대 길이 6
- proxy4_king · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_king:slithery_fight:A:1 · r89 · 드래곤 #216 L8: 질주 3칸 (가장 가까운 짧은 적 머리 2칸) → 죽음 r90 박힘(상대 돌진), 상대 길이 2

## 위협 피하기 2칸 질주

- 이번: 질주 99% · 몸 10라운드 생존 91% (드래곤 자체 88%)
- 상대별: proxy4_elim 113회 84% · proxy4_king 205회 91% · proxy4_swarm 165회 92%
- 지도별: Autarky 28회 100% · Default 75회 95% · Devil 31회 87% · Prisoners Dilemma 1회 100% · Queen Of Spades 37회 92% · Schooltime 98회 89% · Slithery Fight 160회 93% · Trauma 16회 88% · Trophy 37회 57%
- 국면별: r0-99 154회 86% · r100-249 188회 87% · r250-349 67회 97% · r350-449 61회 95% · r450+ 13회 100%

실패 사례 (51건 중 10건, 기보 확인용):
- proxy4_swarm · Devil · 게임 exp/mapid-a-px4:proxy4_swarm:devil:B:1 · r174 · 드래곤 #3 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 3) → 죽음 r176 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Queen Of Spades · 게임 exp/mapid-a-px4:proxy4_swarm:queen_of_spades:B:1 · r214 · 드래곤 #1 L6: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 3) → 죽음 r217 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Schooltime · 게임 exp/mapid-a-px4:proxy4_swarm:schooltime:A:1 · r133 · 드래곤 #4 L7: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 3) → 죽음 r133 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Trophy · 게임 exp/mapid-a-px4:proxy4_swarm:trophy:A:1 · r78 · 드래곤 #38 L9: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r79 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:A:1 · r236 · 드래곤 #451 L21: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 3) → 죽음 r236 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Default · 게임 exp/mapid-a-px4:proxy4_elim:default:B:1 · r67 · 드래곤 #1 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 3) → 죽음 r69 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Schooltime · 게임 exp/mapid-a-px4:proxy4_elim:schooltime:B:1 · r193 · 드래곤 #95 L4: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 3) → 죽음 r198 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Trauma · 게임 exp/mapid-a-px4:proxy4_elim:trauma:B:1 · r249 · 드래곤 #1 L4: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r250 돌진, 상대 길이 2
- proxy4_elim · Trophy · 게임 exp/mapid-a-px4:proxy4_elim:trophy:A:1 · r52 · 드래곤 #11 L5: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 3) → 죽음 r58 박힘(상대 돌진), 상대 길이 2
- proxy4_elim · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_elim:slithery_fight:A:1 · r204 · 드래곤 #470 L7: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r212 아군 머리, 상대 길이 6

## 포털 통과 (전체; PORTAL?=미탐색 출구)

- 이번: 미탐색 출구 372회(몸 3라운드 생존 97%) · 전체 몸 생존 3라운드 96% (드래곤 자체 83%) · 10라운드 93% · 10라운드 안 먹은 진주 1.1
- 상대별: proxy4_elim 315회 96% · proxy4_king 272회 97% · proxy4_swarm 269회 95%
- 지도별: Autarky 75회 99% · Default 92회 96% · Portals 359회 97% · Prisoners Dilemma 44회 98% · Queen Of Spades 49회 82% · Schooltime 43회 93% · Slithery Fight 141회 99% · Trauma 53회 94%
- 국면별: r0-99 231회 96% · r100-249 291회 94% · r250-349 186회 98% · r350-449 123회 98% · r450+ 25회 100%

실패 사례 (34건 중 10건, 기보 확인용):
- proxy4_swarm · Default · 게임 exp/mapid-a-px4:proxy4_swarm:default:A:1 · r270 · 드래곤 #89 L30: 포털(미탐색 출구) → 죽음 r271 박힘(상대 돌진), 상대 길이 3, 10라운드 안 진주 0
- proxy4_swarm · Autarky · 게임 exp/mapid-a-px4:proxy4_swarm:autarky:A:1 · r103 · 드래곤 #10 L9: 포털 → 죽음 r103 희생, 상대 길이 13, 10라운드 안 진주 0
- proxy4_swarm · Prisoners Dilemma · 게임 exp/mapid-a-px4:proxy4_swarm:prisoners_dilemma:A:1 · r30 · 드래곤 #4 L3: 포털 → 죽음 r30 아군 머리, 상대 길이 3, 10라운드 안 진주 0
- proxy4_swarm · Queen Of Spades · 게임 exp/mapid-a-px4:proxy4_swarm:queen_of_spades:A:1 · r29 · 드래곤 #0 L3: 포털(미탐색 출구) → 죽음 r30 갇힘, 10라운드 안 진주 0
- proxy4_swarm · Portals · 게임 exp/mapid-a-px4:proxy4_swarm:portals:B:1 · r8 · 드래곤 #1 L3: 포털(미탐색 출구) → 죽음 r9 갇힘, 10라운드 안 진주 0
- proxy4_swarm · Schooltime · 게임 exp/mapid-a-px4:proxy4_swarm:schooltime:B:1 · r153 · 드래곤 #3 L5: 포털 → 죽음 r153 갇힘, 상대 길이 2, 10라운드 안 진주 0
- proxy4_swarm · Trauma · 게임 exp/mapid-a-px4:proxy4_swarm:trauma:B:1 · r128 · 드래곤 #12 L7: 포털 → 죽음 r128 갇힘, 상대 길이 4, 10라운드 안 진주 0
- proxy4_elim · Default · 게임 exp/mapid-a-px4:proxy4_elim:default:A:1 · r120 · 드래곤 #0 L15: 포털 → 죽음 r123 박힘(상대 돌진), 상대 길이 2, 10라운드 안 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:B:1 · r245 · 드래곤 #454 L11: 포털 → 죽음 r245 갇힘, 상대 길이 2, 10라운드 안 진주 0
- proxy4_elim · Portals · 게임 exp/mapid-a-px4:proxy4_elim:portals:B:1 · r8 · 드래곤 #1 L3: 포털(미탐색 출구) → 죽음 r9 갇힘, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 6, 경로 10) · 잡은 길이 ≥ 우리 94% · 두 몸의 진주 우리 24 대 상대 90
- 상대별: proxy4_elim 5회 20% · proxy4_king 6회 0% · proxy4_swarm 5회 40%
- 지도별: Default 1회 0% · Devil 2회 50% · Schooltime 3회 0% · Slithery Fight 5회 20% · Trauma 4회 25% · Trophy 1회 0%
- 국면별: r0-99 3회 33% · r100-249 2회 0% · r250-349 4회 0% · r350-449 5회 20% · r450+ 2회 50%

실패 사례 (13건 중 10건, 기보 확인용):
- proxy4_swarm · Trauma · 게임 exp/mapid-a-px4:proxy4_swarm:trauma:A:1 · r256 · 드래곤 #74 L2: 돌진 경로 1칸 → 상대 L3 잡음, 진주 우리 0 대 상대 3
- proxy4_swarm · Trophy · 게임 exp/mapid-a-px4:proxy4_swarm:trophy:A:1 · r79 · 드래곤 #26 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:A:1 · r184 · 드래곤 #12 L4: 돌진 경로 3칸 → 상대 L3 잡음, 진주 우리 1 대 상대 3
- proxy4_elim · Devil · 게임 exp/mapid-a-px4:proxy4_elim:devil:B:1 · r458 · 드래곤 #421 L3: 돌진 경로 2칸 → 상대 L28 잡음, 진주 우리 6 대 상대 7
- proxy4_elim · Schooltime · 게임 exp/mapid-a-px4:proxy4_elim:schooltime:A:1 · r397 · 드래곤 #193 L7: 돌진 경로 4칸 → 상대 L25 잡음, 진주 우리 0 대 상대 16
- proxy4_elim · Trauma · 게임 exp/mapid-a-px4:proxy4_elim:trauma:A:1 · r343 · 드래곤 #102 L2: 돌진 경로 2칸 → 상대 L12 잡음, 진주 우리 0 대 상대 8
- proxy4_elim · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_elim:slithery_fight:B:1 · r420 · 드래곤 #295 L6: 돌진 경로 3칸 → 상대 L21 잡음, 진주 우리 0 대 상대 13
- proxy4_king · Default · 게임 exp/mapid-a-px4:proxy4_king:default:A:1 · r259 · 드래곤 #89 L2: 돌진 경로 2칸 → 상대 L3 잡음, 진주 우리 0 대 상대 4
- proxy4_king · Schooltime · 게임 exp/mapid-a-px4:proxy4_king:schooltime:A:1 · r289 · 드래곤 #31 L2: 돌진 경로 1칸 → 상대 L13 잡음, 진주 우리 0 대 상대 8
- proxy4_king · Trauma · 게임 exp/mapid-a-px4:proxy4_king:trauma:A:1 · r409 · 드래곤 #151 L2: 돌진 경로 1칸 → 상대 L8 잡음, 진주 우리 0 대 상대 5

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 상대별: proxy4_elim 30회 100% · proxy4_king 34회 100% · proxy4_swarm 19회 100%
- 지도별: Default 7회 100% · Devil 5회 100% · Portals 5회 100% · Prisoners Dilemma 4회 100% · Queen Of Spades 17회 100% · Schooltime 19회 100% · Slithery Fight 26회 100%
- 국면별: r0-99 15회 100% · r100-249 42회 100% · r250-349 7회 100% · r350-449 12회 100% · r450+ 7회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 100%
- 상대별: proxy4_swarm 3회 –
- 지도별: Slithery Fight 3회 –
- 국면별: r0-99 1회 – · r100-249 1회 – · r250-349 1회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 3회 – · proxy4_king 2회 – · proxy4_swarm 2회 –
- 지도별: Devil 1회 – · Schooltime 2회 – · Slithery Fight 2회 – · Trauma 2회 –
- 국면별: r100-249 4회 – · r250-349 2회 – · r350-449 1회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/mapid-a-px4` | 60 | 51 (0.85) | 57% | 5 (0.08) | 0 (0.00) | 6 | 30 | 9 | 1/2 (3.5) | 15 (0.25; 필사 1) | 3/9 (10.5) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/mapid-a-px4` | 60 | 41964 | 1.1% (469) | 11.6% (4858) | 3284 | 1.8% (60) | 5.1% (166) | 21.5% (705/3284) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/mapid-a-px4` | 전체 | 분열 | 14 (12%) | 12.9 | 84% | 62% | 8 | 2 |
| 이번 `exp/mapid-a-px4` | 전체 | 2칸 질주 | 43 (36%) | 10.5 | 82% | 66% | 11 | 9 |
| 이번 `exp/mapid-a-px4` | 전체 | 3칸 질주 | 25 (21%) | 9.1 | 79% | 79% | 2 | 2 |
| 이번 `exp/mapid-a-px4` | 전체 | 한 걸음 | 36 (31%) | 12.2 | 37% | 23% | 23 | 21 |
| 이번 `exp/mapid-a-px4` | 4칸 이상 | 분열 | 9 (16%) | 12.7 | 95% | 98% | 4 | 0 |
| 이번 `exp/mapid-a-px4` | 4칸 이상 | 2칸 질주 | 21 (37%) | 12.1 | 94% | 74% | 6 | 4 |
| 이번 `exp/mapid-a-px4` | 4칸 이상 | 3칸 질주 | 7 (12%) | 8.1 | 60% | 53% | 2 | 2 |
| 이번 `exp/mapid-a-px4` | 4칸 이상 | 한 걸음 | 20 (35%) | 13.6 | 33% | 23% | 13 | 13 |

사각 박힘 (5건 중 5건, 기보 확인용):
- proxy4_swarm · Trophy · 게임 exp/mapid-a-px4:proxy4_swarm:trophy:A:1 · r79 · 드래곤 #38 L8: 결정 "SE v3.9 d7 L9 map=Trophy/a" → 가해자 #37 L3 2걸음 (path through a tile occupied at the decision)
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:A:1 · r236 · 드래곤 #451 L20: 결정 "NN v3.3 d7 L21" → 가해자 #464 L3 2걸음 (path through a tile occupied at the decision)
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:B:1 · r117 · 드래곤 #13 L11: 결정 "S v6.8 d7 L11" → 가해자 #235 L4 2걸음 (path through a tile occupied at the decision)
- proxy4_elim · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_elim:slithery_fight:B:1 · r165 · 드래곤 #349 L8: 결정 "SW v2.8 d7 L9" → 가해자 #369 L4 2걸음 (path through a tile occupied at the decision)
- proxy4_king · Queen Of Spades · 게임 exp/mapid-a-px4:proxy4_king:queen_of_spades:A:1 · r247 · 드래곤 #35 L7: 결정 "N v6.3 d7 L7" → 가해자 #56 L3 2걸음 (path through a tile occupied at the decision)

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (15건 중 10건):
- proxy4_swarm · Autarky · 게임 exp/mapid-a-px4:proxy4_swarm:autarky:A:1 · r103 · 드래곤 #10 L9: v-1.5 → 희생, 막은 우리 드래곤 L13
- proxy4_swarm · Prisoners Dilemma · 게임 exp/mapid-a-px4:proxy4_swarm:prisoners_dilemma:A:1 · r30 · 드래곤 #4 L3: v6.4 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_swarm · Portals · 게임 exp/mapid-a-px4:proxy4_swarm:portals:A:1 · r158 · 드래곤 #78 L11: v8.5 PORTAL? → 아군 머리, 막은 우리 드래곤 L18
- proxy4_swarm · Portals · 게임 exp/mapid-a-px4:proxy4_swarm:portals:A:1 · r218 · 드래곤 #149 L15: v-8.3 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_swarm · Portals · 게임 exp/mapid-a-px4:proxy4_swarm:portals:A:1 · r421 · 드래곤 #397 L13: v-1.2 → 갇힘, 막은 우리 드래곤 L33
- proxy4_swarm · Trauma · 게임 exp/mapid-a-px4:proxy4_swarm:trauma:B:1 · r128 · 드래곤 #12 L7: v-3.3 → 갇힘, 막은 우리 드래곤 L4
- proxy4_swarm · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_swarm:slithery_fight:B:1 · r245 · 드래곤 #454 L11: v-9.2 → 갇힘, 막은 우리 드래곤 L2
- proxy4_elim · Queen Of Spades · 게임 exp/mapid-a-px4:proxy4_elim:queen_of_spades:A:1 · r42 · 드래곤 #7 L3: v0.1 PORTAL? → 아군 머리, 막은 우리 드래곤 L8
- proxy4_elim · Trauma · 게임 exp/mapid-a-px4:proxy4_elim:trauma:B:1 · r120 · 드래곤 #11 L7: v-11.5 → 갇힘, 막은 우리 드래곤 L4
- proxy4_elim · Slithery Fight · 게임 exp/mapid-a-px4:proxy4_elim:slithery_fight:B:1 · r454 · 드래곤 #31 L3: v-0.4 → 갇힘, 막은 우리 드래곤 L19

## 지도·판본 인식 상세 (cand-mapid)

이번 (60판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 6 | 100% | 100% | 36/36 (36) | 1560 | 1560 (0) | 0 | 0 | 0 | 0 |
| Default a | 6 | 100% | 100% | 24/24 (24) | 37 | 37 (0) | 0 | 0 | 0 | 0 |
| Devil a | 6 | 100% | 100% | 18/18 (18) | 51 | 51 (0) | 0 | 0 | 0 | 0 |
| Portals a | 6 | 100% | 100% | 18/18 (18) | 229 | 229 (0) | 0 | 0 | 0 | 0 |
| Prisoners Dilemma a | 6 | 100% | 100% | 6/18 (6) | 1503 | 1499 (0) | 4 | 0 | 0 | 82 |
| Queen Of Spades a | 6 | 100% | 100% | 12/12 (12) | 53 | 51 (0) | 2 | 0 | 0 | 19 |
| Schooltime a | 6 | 100% | 100% | 18/18 (18) | 46 | 46 (0) | 0 | 0 | 0 | 0 |
| Slithery Fight a | 6 | 100% | 100% | 48/48 (48) | 232 | 223 (0) | 8 | 0 | 0 | 13 |
| Trauma a | 6 | 100% | 100% | 12/12 (12) | 48 | 48 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 6 | 100% | 100% | 12/12 (12) | 22 | 22 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 60/60, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

### Schooltime 판의 경제 (bsp의 가설 수준 지표, 정답 판본별)

| 묶음 | 판본 | 판 | 드래곤 수 r50 | r100 | r0–99 자연 진주 먹음 | 전멸당함 | 끝 최장(전멸 0) | 판당 bsp 분열 |
|---|---|---:|---|---|---|---:|---|---:|
| 이번 | a | 6 | 3 [3, 3] | 3 [3, 3] | 18 [15, 28] | 33% | 12 [0, 14] | 0 |

- 기준값(`research/experiments/cand-mapid.md`, 웨이브 전에 적음): b에서 드래곤 수 r50 중앙 ≥ 6, r0–99 자연 진주 중앙 ≥ 14. 우리 merge2 계열 b 29판은 3 · 9, 떼 계열(swarm8·px) b 14판은 6 · 14, 상위권 b 승자는 8 · 32다. a는 bsp가 켜지지 않는 대조군이다.

