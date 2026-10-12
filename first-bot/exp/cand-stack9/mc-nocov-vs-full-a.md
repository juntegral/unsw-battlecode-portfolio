# 구현 적용 확인

- 대상: `exp/stack9nocov-a-px4` 60판 · 비교: `exp/stack9-a-px4` 60판
- 기준(사용자 규칙 2026-09-30): 승률이 아니라, 봇에 구현한 기능이 이 상대들에게 실제로 발동하고 의도대로 작동했는지를 본다.
- "의도대로"의 정의: 모이기=왕 3칸 안까지 가거나 희생까지 함 · 희생=떨군 진주 절반 이상을 우리 팀이 먹고 상대는 못 먹음 · 한입=2턴 안 분열하고 30라운드 뒤 가족 길이가 줄지 않음 · 탈출 분열=10라운드 뒤 몸이 살아 있음 · 정책 분열=새끼 30라운드 생존 · 탈출 질주·위협 피하기=10라운드 뒤 몸 생존 · 포털=3라운드 뒤 몸 생존 · 돌진=충돌 성사, 잡은 길이 ≥ 우리, 두 몸의 진주를 우리가 더 먹음 · 먹이 질주=진주 먹음.
- "몸"은 그 드래곤과 그 뒤 분열로 태어난 자손 전체다. 통로 고리처럼 몸을 새끼에게 넘기며 버티는 경우를 손실로 세지 않기 위해서다.
- stack2의 "의도대로": 조각 떼기=조각이 30라운드 살며 진주를 1개 이상 먹거나, 나중에 희생(feed·conv)으로 아군을 먹임 · 새 사망 진주 줍기=표적이 된 사망 진주(진주 하나가 한 건)를 우리 팀이 먹음(자연 진주로 오인했거나 이미 없던 표적은 판정에서 뺌).
- stack4의 "의도대로": tg=표식 턴 뒤 2라운드 안에 박히지 않음 · 몰렸을 때 분열=10라운드 뒤 몸이 살아 있음(보존율은 효과 줄) · px=그 턴에 우리 드래곤과 부딪혀 죽지 않음 · gx=그 드래곤의 몸(그 드래곤과 뒤에 태어난 자손)이 끝까지 삶(사용자 결정 17:16: 생존은 몸으로 판정, 드래곤 자체 생존은 참고).
- cand-mapid의 "의도대로": Schooltime b 초반 분열(bsp)=떼어 낸 조각(새 유닛)이 10라운드 뒤 살아 있음 · 지도·판본 인식=그 판에서 1개 이상의 프로세스가 판본까지 결정했고, 결정한 프로세스(마지막 표식 기준)가 모두 정답 지도·판본을 댐. 정답 판본은 로컬이면 지도 파일 이름, 온라인이면 기보의 자연 생성(한쪽 판본에서만 생성하는 칸)으로 정하고, 끝까지 가릴 수 없던 판은 뺀다. 지도별 줄의 이름 뒤 a·b·?가 정답 판본이다.
- stack5의 "의도대로": 덮기 분열=새끼가 30라운드 안에 자연 진주를 1개 이상 먹음(생존은 효과 줄) · 샘 지킴=목표 샘 3걸음 안에 든 뒤 30라운드 동안 그 무리(실제 샘, 목표에서 3걸음 안)에 생긴 자연 진주의 85% 이상을 우리가 먹음(도착하지 않았거나 진주가 생기지 않은 목표는 뺌) · 영토 덮기 끌림=20라운드 안에 우리 영토 자연 진주를 먹음. 게이트와 가설 수준 지표는 맨 뒤 stack5 절.
- stack7의 "의도대로": 수 바닥 분열(floor)=새끼가 30라운드 뒤 살아 있음 · 왕 길이 상한 분열(kcap)=새끼가 10라운드 뒤 살아 있음(부모 생존은 효과 줄). 판이 먼저 끝나면 생존으로 센다. 게이트, 저수 에피소드, 지도 가르기는 맨 뒤 stack7 절.
- stack9의 "의도대로": 늦은 재분열(lsplit)=새끼가 30라운드 안에 자연 진주를 1개 이상 먹음(떨군 진주의 우리 몫은 게이트 표) · 영토 덮기 끌림 창(cov 창)=표식이 연 30라운드 창 안에 그 드래곤이 우리 영토 자연 진주를 1개 이상 먹음. fc는 frag 줄에 포함된다. 게이트, 가설 수준 지표(공급 사슬 연구의 정의), 부작용은 맨 뒤 stack9 절.

## 요약

| 기능 | 발동(판당) | 의도대로 | 비교: 발동(판당) | 비교: 의도대로 |
|---|---:|---:|---:|---:|
| 늦은 재분열 (lsplit, stack9) | 769 (12.8) | 35% | 706 (11.8) | 34% |
| 영토 덮기 끌림 30라운드 창 (cov 창, stack9; 드래곤·창 단위) | 0 (0) | – | 3406 (56.8) | 28% |
| 몫이 있어 F 끌림 멈춤 (Fp, stack8; 드래곤·진주 단위) | 627 (10.5) | 35% | 647 (10.8) | 34% |
| 몫을 긴 아군에게 넘기지 않음 (cl, stack8; 드래곤·진주 단위) | 13097 (218.3) | 65% | 12665 (211.1) | 65% |
| 몫을 한 걸음 가까운 적에게 넘기지 않음 (ce, stack8; 드래곤·진주 단위) | 1370 (22.8) | 51% | 1214 (20.2) | 51% |
| 수 바닥 분열 (split floor, stack7) | 7 (0.1) | 71% | 10 (0.2) | 40% |
| 왕 길이 상한 분열 (split kcap, stack7) | 1 (0) | 100% | 1 (0) | 100% |
| 지도·판본 인식 (map=, cand-mapid; 판 단위) | 60 (1) | 100% | 60 (1) | 100% |
| 덮기 분열 (csplit, stack5) | 1073 (17.9) | 38% | 1070 (17.8) | 40% |
| 샘 지킴 (F, stack5; 드래곤·샘 단위) | 1018 (17) | 87% | 1066 (17.8) | 88% |
| 영토 덮기 끌림 (cov, stack5) | 0 (0) | – | 29775 (496.3) | 20% |
| 위협 모형 빈틈 (tg, stack4) | 14616 (243.6) | 98% | 14320 (238.7) | 98% |
| 모이기 시작 제한 (gx, stack4; 드래곤 단위) | 220 (3.7) | 91% | 135 (2.3) | 93% |
| 큰 아군 곁 희생 (conv, stack1 M1) | 279 (4.7) | 98% | 331 (5.5) | 99% |
| 조각 떼기 (split frag, stack2 S1) | 29 (0.5) | 55% | 35 (0.6) | 54% |
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 3225 (53.8) | 82% | 3297 (55) | 81% |
| 왕에게 모이기 (g, 드래곤 단위) | 1357 (22.6) | 72% | 1327 (22.1) | 69% |
| 희생 먹이기 (feed) | 317 (5.3) | 79% | 303 (5.1) | 82% |
| 막다른 길 한입 (pocket-eat) | 9 (0.2) | 56% | 9 (0.2) | 56% |
| 탈출 분열 (escape-split) | 4235 (70.6) | 98% | 4202 (70) | 98% |
| 출구 없음 (no-exit) | 4640 (77.3) | – | 4552 (75.9) | – |
| 탈출 질주 3칸 (esc) | 69 (1.2) | 91% | 73 (1.2) | 99% |
| 위협 피하기 2칸 질주 | 667 (11.1) | 94% | 662 (11) | 94% |
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 3037 (50.6) | 94% | 2731 (45.5) | 94% |
| 돌진 (TRADE) | 73 (1.2) | 42% | 59 (1) | 36% |
| 먹이 질주 (2칸 이상, 먹은 것) | 213 (3.6) | 100% | 186 (3.1) | 100% |
| 기타 2칸 질주 | 73 (1.2) | – | 77 (1.3) | – |
| 마지막 돌진 (last-trade) | 38 (0.6) | – | 36 (0.6) | – |

- 건강: 턴 285989, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 비교 건강: 턴 279784, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 8822턴 · 끝판(late) 10379턴 · 돌진 신뢰(T, 탈출 끔) 3턴, 그 직후 박혀 죽음 0

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 비교 |
|---|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 2% (68/3396턴) | 2% (56/3181턴) |
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 53.5칸 (16.2회), 진주 우리 86% · 상대 3% | 57.2칸 (18.1회), 진주 우리 90% · 상대 3% |
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 1.6칸 (판당 0.07회) | 0.3칸 (판당 0.03회) |
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 31% (1204/3926턴) | 24% (913/3765턴) |
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.117회 (7건, 105칸) | 판당 0.033회 (2건, 18칸) |
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 14.5마리 (30판) | 14.3마리 (30판) |
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 28.5회 | 29.8회 |
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 56% (우리 38%) | 56% (우리 38%) |
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 9.9 대 상대 31.5 (10.1회) · 박힌 교환의 우리 몫 17% (234회) | 우리 10.7 대 상대 28.4 (9.8회) · 박힌 교환의 우리 몫 23% (226회) |
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 14.5개 | 14.8개 |

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 늦은 재분열 (lsplit, stack9)

- 이번: 분열 100% · 설계 상황(r250–429, 부모 길이 4–6, 우리 수 < 목표; 기보) 100% (기준 ≥95%) · 새끼 30라운드 안 자연 진주 ≥1 35% (기준 ≥38%) · 죽은 새끼 668마리의 떨군 진주 1103개 중 우리 78% (기준 ≥85%) · ≥8 21% · 상대 11% · 새끼 10·30라운드 생존 86% · 69% · 부모 길이 평균 4.3 · r340 뒤 455회
- 비교: 분열 100% · 설계 상황(r250–429, 부모 길이 4–6, 우리 수 < 목표; 기보) 100% (기준 ≥95%) · 새끼 30라운드 안 자연 진주 ≥1 34% (기준 ≥38%) · 죽은 새끼 613마리의 떨군 진주 1017개 중 우리 81% (기준 ≥85%) · ≥8 27% · 상대 10% · 새끼 10·30라운드 생존 87% · 70% · 부모 길이 평균 4.3 · r340 뒤 434회
- 상대별: proxy4_elim 238회 34% · proxy4_king 290회 38% · proxy4_swarm 241회 31%
- 지도별: Autarky 169회 30% · Default 158회 37% · Devil 22회 64% · Portals 39회 21% · Prisoners Dilemma 36회 22% · Queen Of Spades 55회 36% · Schooltime 142회 50% · Slithery Fight 64회 19% · Trauma 84회 29%
- 국면별: r250-349 361회 28% · r350-449 408회 41%

실패 사례 (502건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r251 · 드래곤 #251 L4: 새끼 L2 · 우리 18/21마리 → 새끼 죽음 r289 갇힘(나이 38, 진주 2개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:A:1 · r253 · 드래곤 #113 L4: 새끼 L2 · 우리 20/22마리 → 새끼 죽음 r278 갇힘(나이 25, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:A:1 · r412 · 드래곤 #422 L4: 새끼 L2 · 우리 7/11마리 → 새끼 죽음 r415 갇힘(나이 3, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:A:1 · r370 · 드래곤 #560 L6: 새끼 L2 · 우리 10/11마리 → 새끼 죽음 r385 갇힘(나이 15, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9nocov-a-px4:proxy4_king:prisoners_dilemma:A:1 · r269 · 드래곤 #34 L4: 새끼 L2 · 우리 10/11마리 → 새끼 죽음 r330 갇힘(나이 61, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_king:queen_of_spades:A:1 · r260 · 드래곤 #54 L4: 새끼 L2 · 우리 10/19마리 → 새끼 죽음 r276 박힘(상대 돌진)(나이 16, 진주 1개 중 우리 0), 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:A:1 · r265 · 드래곤 #199 L4: 새끼 L2 · 우리 5/40마리 → 새끼 죽음 r357 박힘(상대 돌진)(나이 92, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_king:trauma:A:1 · r264 · 드래곤 #100 L4: 새끼 L2 · 우리 15/25마리 → 새끼 죽음 r315 갇힘(나이 51, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:A:1 · r257 · 드래곤 #393 L4: 새끼 L2 · 우리 22/37마리 → 새끼 죽음 r488 희생(나이 231, 진주 1개 중 우리 0), 30라운드 안 자연 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_swarm:autarky:A:1 · r263 · 드래곤 #160 L4: 새끼 L2 · 우리 16/21마리 → 새끼 죽음 r274 갇힘(나이 11, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0

## 몫이 있어 F 끌림 멈춤 (Fp, stack8; 드래곤·진주 단위)

- 이번: 진주 627개 (표식 턴 1958; 표식 때 진주 있음 98%) · 설계 상황(표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음) 71% · 그 드래곤이 먹음 36% (10라운드 안 35%) · 우리 팀 72% · 우리 긴 드래곤 17% · 상대 22%
- 비교: 진주 647개 (표식 턴 2074; 표식 때 진주 있음 98%) · 설계 상황(표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음) 71% · 그 드래곤이 먹음 34% (10라운드 안 34%) · 우리 팀 70% · 우리 긴 드래곤 17% · 상대 22%
- 상대별: proxy4_elim 207회 36% · proxy4_king 221회 32% · proxy4_swarm 199회 38%
- 지도별: Devil 16회 29% · Portals 406회 41% · Prisoners Dilemma 24회 75% · Schooltime 2회 0% · Slithery Fight 170회 17% · Trauma 9회 22%
- 국면별: r0-99 232회 32% · r100-249 226회 37% · r250-349 169회 37%

실패 사례 (396건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:B:1 · r17 · 드래곤 #5 L3: 진주 (21,9) 우리 거리 4 → 다른 우리 드래곤이 먹음
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:A:1 · r17 · 드래곤 #6 L2: 진주 (13,6) 우리 거리 99 → 상대가 먹음
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9nocov-a-px4:proxy4_king:prisoners_dilemma:A:1 · r150 · 드래곤 #34 L3: 진주 (12,11) 우리 거리 3 → 다른 우리 드래곤이 먹음
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:B:1 · r133 · 드래곤 #32 L2: 진주 (36,39) 우리 거리 99 → 아무도 안 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:A:1 · r0 · 드래곤 #8 L5: 진주 (31,5) 우리 거리 5 → 다른 우리 드래곤이 먹음
- proxy4_swarm · Devil · 게임 exp/stack9nocov-a-px4:proxy4_swarm:devil:A:1 · r52 · 드래곤 #8 L2: 진주 (7,13) 우리 거리 3 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_swarm · Portals · 게임 exp/stack9nocov-a-px4:proxy4_swarm:portals:A:1 · r17 · 드래곤 #6 L2: 진주 (13,6) 우리 거리 99 → 상대가 먹음
- proxy4_swarm · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_swarm:schooltime:B:1 · r156 · 드래곤 #73 L2: 진주 (39,39) 우리 거리 99 → 다른 우리 드래곤이 먹음
- proxy4_swarm · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_swarm:slithery_fight:A:1 · r0 · 드래곤 #8 L5: 진주 (31,5) 우리 거리 5 → 다른 우리 드래곤이 먹음
- proxy4_elim · Portals · 게임 exp/stack9nocov-a-px4:proxy4_elim:portals:A:1 · r21 · 드래곤 #2 L7: 진주 (27,5) 우리 거리 5 (설계 밖) → 다른 우리 드래곤이 먹음

## 몫을 긴 아군에게 넘기지 않음 (cl, stack8; 드래곤·진주 단위)

- 이번: 진주 13097개 (표식 턴 30911; 표식 때 진주 있음 97%) · 설계 상황(자연 진주이고 우리 머리 가운데 표식한 조각만 가장 가까움) 38% · 그 드래곤이 먹음 65% (10라운드 안 65%) · 우리 팀 79% · 우리 긴 드래곤 7% · 상대 15%
- 비교: 진주 12665개 (표식 턴 29330; 표식 때 진주 있음 97%) · 설계 상황(자연 진주이고 우리 머리 가운데 표식한 조각만 가장 가까움) 38% · 그 드래곤이 먹음 65% (10라운드 안 64%) · 우리 팀 78% · 우리 긴 드래곤 7% · 상대 15%
- 상대별: proxy4_elim 4221회 66% · proxy4_king 4782회 65% · proxy4_swarm 4094회 65%
- 지도별: Autarky 2343회 92% · Default 1250회 66% · Devil 517회 71% · Portals 1211회 60% · Prisoners Dilemma 1781회 95% · Queen Of Spades 1077회 55% · Schooltime 2008회 47% · Slithery Fight 1938회 35% · Trauma 762회 56% · Trophy 210회 64%
- 국면별: r0-99 2880회 63% · r100-249 3678회 66% · r250-349 2398회 66% · r350-449 3017회 67% · r450+ 1124회 65%

실패 사례 (4404건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r4 · 드래곤 #3 L3: 진주 (35,16) 우리 거리 5 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:A:1 · r4 · 드래곤 #12 L2: 진주 (10,29) 우리 거리 99 → 상대가 먹음
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:B:1 · r15 · 드래곤 #5 L3: 진주 (16,10) 우리 거리 6 → 상대가 먹음
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:A:1 · r10 · 드래곤 #6 L2: 진주 (15,1) 우리 거리 4 → 다른 우리 드래곤이 먹음
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9nocov-a-px4:proxy4_king:prisoners_dilemma:A:1 · r152 · 드래곤 #34 L3: 진주 (12,11) 우리 거리 5 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_king · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_king:queen_of_spades:A:1 · r16 · 드래곤 #2 L2: 진주 (6,33) 우리 거리 4 → 다른 우리 드래곤이 먹음
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:A:1 · r29 · 드래곤 #2 L2: 진주 (10,39) 우리 거리 99 → 상대가 먹음
- proxy4_king · Trophy · 게임 exp/stack9nocov-a-px4:proxy4_king:trophy:A:1 · r29 · 드래곤 #2 L2: 진주 (1,19) 우리 거리 5 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_king · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_king:trauma:A:1 · r33 · 드래곤 #4 L2: 진주 (11,10) 우리 거리 99 → 다른 우리 드래곤이 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:A:1 · r1 · 드래곤 #12 L2: 진주 (21,1) 우리 거리 3 → 다른 우리 드래곤이 먹음

## 몫을 한 걸음 가까운 적에게 넘기지 않음 (ce, stack8; 드래곤·진주 단위)

- 이번: 진주 1370개 (표식 턴 2204; 표식 때 진주 있음 96%) · 설계 상황(적 머리가 진주에서 우리 거리+1 안) 85% · 그 드래곤이 먹음 26% (10라운드 안 25%) · 우리 팀 39% · 우리 긴 드래곤 6% · 상대 49% · 5라운드 안 박힘 7%
- 비교: 진주 1214개 (표식 턴 1941; 표식 때 진주 있음 96%) · 설계 상황(적 머리가 진주에서 우리 거리+1 안) 81% · 그 드래곤이 먹음 26% (10라운드 안 24%) · 우리 팀 38% · 우리 긴 드래곤 5% · 상대 49% · 5라운드 안 박힘 7%
- 상대별: proxy4_elim 389회 47% · proxy4_king 512회 56% · proxy4_swarm 469회 48%
- 지도별: Autarky 13회 42% · Default 169회 54% · Devil 62회 48% · Portals 48회 93% · Prisoners Dilemma 19회 80% · Queen Of Spades 159회 63% · Schooltime 404회 42% · Slithery Fight 403회 50% · Trauma 44회 39% · Trophy 49회 46%
- 국면별: r0-99 239회 36% · r100-249 417회 44% · r250-349 254회 51% · r350-449 344회 63% · r450+ 116회 68%

실패 사례 (649건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r91 · 드래곤 #7 L3: 진주 (19,1) 우리 거리 4 → 상대가 먹음
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:A:1 · r317 · 드래곤 #57 L2: 진주 (28,3) 우리 거리 6 → 상대가 먹음
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:B:1 · r21 · 드래곤 #5 L3: 진주 (16,5) 우리 거리 3 → 상대가 먹음
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:A:1 · r178 · 드래곤 #181 L4: 진주 (12,7) 우리 거리 99 (설계 밖) → 상대가 먹음
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9nocov-a-px4:proxy4_king:prisoners_dilemma:A:1 · r379 · 드래곤 #216 L2: 진주 (15,2) 우리 거리 6 → 상대가 먹음
- proxy4_king · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_king:queen_of_spades:A:1 · r164 · 드래곤 #14 L2: 진주 (4,4) 우리 거리 4 → 상대가 먹음
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:A:1 · r40 · 드래곤 #10 L3: 진주 (14,3) 우리 거리 4 (설계 밖) → 상대가 먹음
- proxy4_king · Trophy · 게임 exp/stack9nocov-a-px4:proxy4_king:trophy:A:1 · r70 · 드래곤 #11 L2: 진주 (3,15) 우리 거리 6 → 상대가 먹음
- proxy4_king · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_king:trauma:A:1 · r180 · 드래곤 #16 L2: 진주 (19,12) 우리 거리 5 → 상대가 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:A:1 · r28 · 드래곤 #47 L2: 진주 (37,26) 우리 거리 99 (설계 밖) → 상대가 먹음

## 수 바닥 분열 (split floor, stack7)

- 이번: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 86% · 적 머리가 7×7 시야 안 43% · 부모 길이 평균 4.4 · 우리 수(표식) 평균 2.7 · 상대 수 평균 32.3 · 새끼 10라운드 생존 86% · 30라운드 71% · 부모 10라운드 생존 71% · 30라운드 71% · 새끼 30라운드 안 1개 이상 먹음 43% · 30라운드 뒤 가족 길이 변화 2.7 · 30라운드 안 새끼가 죽은 원인: 박힘(상대 돌진) 1, 돌진 1
- 비교: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 90% · 적 머리가 7×7 시야 안 30% · 부모 길이 평균 4.1 · 우리 수(표식) 평균 2.6 · 상대 수 평균 32 · 새끼 10라운드 생존 70% · 30라운드 40% · 부모 10라운드 생존 80% · 30라운드 70% · 새끼 30라운드 안 1개 이상 먹음 30% · 30라운드 뒤 가족 길이 변화 2 · 30라운드 안 새끼가 죽은 원인: 박힘(상대 돌진) 4, 갇힘 1, 희생 1
- 상대별: proxy4_king 4회 50% · proxy4_swarm 3회 100%
- 지도별: Devil 5회 60% · Queen Of Spades 2회 100%
- 국면별: r0-99 1회 100% · r100-249 2회 0% · r250-349 3회 100% · r350-449 1회 100%

실패 사례 (2건 중 2건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:B:1 · r173 · 드래곤 #124 L5: 우리 3마리 · 상대 48마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r184 박힘(상대 돌진), 상대 길이 2, 부모 10라운드 죽음 · 표식 map=Devil/a
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:B:1 · r180 · 드래곤 #205 L5: 우리 3마리 · 상대 48마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r180 돌진, 상대 길이 3, 부모 10라운드 죽음 · 표식 map=Devil/a

## 왕 길이 상한 분열 (split kcap, stack7)

- 이번: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 0% · 부모 길이 평균 7 · 우리 수(표식) 평균 3 · 상대 수 평균 5 · 새끼 10라운드 생존 100% · 30라운드 100% · 부모 10라운드 생존 100% · 30라운드 0% · 새끼 30라운드 안 1개 이상 먹음 100% · 30라운드 뒤 가족 길이 변화 1 · 30라운드 안 새끼가 죽은 원인: 없음
- 비교: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 0% · 부모 길이 평균 7 · 우리 수(표식) 평균 3 · 상대 수 평균 5 · 새끼 10라운드 생존 100% · 30라운드 100% · 부모 10라운드 생존 100% · 30라운드 0% · 새끼 30라운드 안 1개 이상 먹음 100% · 30라운드 뒤 가족 길이 변화 1 · 30라운드 안 새끼가 죽은 원인: 없음
- 상대별: proxy4_swarm 1회 100%
- 지도별: Trophy 1회 100%
- 국면별: r0-99 1회 100%

## 지도·판본 인식 (map=, cand-mapid; 판 단위)

- 이번: 판본을 기보로 가릴 수 있는 판 60/60 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 94%, 그중 정답 100% · 프로세스 6324: 표식 없음 6, 결정 6298 (정답 100%, 틀림 0), 가족만 20, 모름 0, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 219라운드
- 비교: 판본을 기보로 가릴 수 있는 판 60/60 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 94%, 그중 정답 100% · 프로세스 6234: 표식 없음 3, 결정 6213 (정답 100%, 틀림 0), 가족만 18, 모름 0, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 177라운드
- 상대별: proxy4_elim 20회 100% · proxy4_king 20회 100% · proxy4_swarm 20회 100%
- 지도별: Autarky a 6회 100% · Default a 6회 100% · Devil a 6회 100% · Portals a 6회 100% · Prisoners Dilemma a 6회 100% · Queen Of Spades a 6회 100% · Schooltime a 6회 100% · Slithery Fight a 6회 100% · Trauma a 6회 100% · Trophy a 6회 100%
- 국면별: r0-99 60회 100%

## 덮기 분열 (csplit, stack5)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 33% · 부모가 스스로 최장이라 믿음(k) 64% · 새끼 30라운드 안 자연 진주 ≥1 38% (500형 37% · 전멸형 41%; 기준 ≥45%) · 새끼 30라운드 생존 78% (500형 80% · 전멸형 75%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 84% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 갇힘 171, 아군 머리 18, 박힘(상대 돌진) 42, 돌진 6
- 비교: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 36% · 부모가 스스로 최장이라 믿음(k) 67% · 새끼 30라운드 안 자연 진주 ≥1 40% (500형 39% · 전멸형 42%; 기준 ≥45%) · 새끼 30라운드 생존 76% (500형 78% · 전멸형 72%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 80% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 갇힘 199, 박힘(상대 돌진) 41, 아군 머리 11, 돌진 9
- 상대별: proxy4_elim 346회 40% · proxy4_king 416회 39% · proxy4_swarm 311회 35%
- 지도별: Autarky 116회 35% · Default 163회 38% · Devil 77회 30% · Portals 79회 49% · Prisoners Dilemma 48회 42% · Queen Of Spades 99회 47% · Schooltime 147회 40% · Slithery Fight 220회 33% · Trauma 75회 29% · Trophy 49회 51%
- 국면별: r0-99 487회 43% · r100-249 586회 34%

실패 사례 (663건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r50 · 드래곤 #7 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:A:1 · r1 · 드래곤 #0 L4: 새끼 L2, 적 머리 시야 안 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:B:1 · r1 · 드래곤 #1 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:A:1 · r5 · 드래곤 #4 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9nocov-a-px4:proxy4_king:prisoners_dilemma:A:1 · r33 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_king:queen_of_spades:A:1 · r15 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trophy · 게임 exp/stack9nocov-a-px4:proxy4_king:trophy:A:1 · r28 · 드래곤 #0 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_king:trauma:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:A:1 · r3 · 드래곤 #33 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0

## 샘 지킴 (F, stack5; 드래곤·샘 단위)

- 이번: 목표 1018개(표식 턴 10489) · 설계 상황 82% (실제 샘 100%, 우리 영토 100%, 처음에 다른 우리 머리 3걸음 안 없음 82%; 기준 ≥80%) · 3걸음 안 도착 58% · 도착 뒤 30라운드 그 무리 자연 진주 2459개 중 우리 90% · 상대 9% (합산 기준 ≥85%) · 처음 거리 평균 3.2
- 비교: 목표 1066개(표식 턴 10912) · 설계 상황 81% (실제 샘 100%, 우리 영토 100%, 처음에 다른 우리 머리 3걸음 안 없음 81%; 기준 ≥80%) · 3걸음 안 도착 58% · 도착 뒤 30라운드 그 무리 자연 진주 2540개 중 우리 91% · 상대 8% (합산 기준 ≥85%) · 처음 거리 평균 3.3
- 상대별: proxy4_elim 318회 89% · proxy4_king 350회 86% · proxy4_swarm 350회 85%
- 지도별: Autarky 13회 33% · Devil 62회 50% · Portals 523회 98% · Prisoners Dilemma 65회 100% · Schooltime 7회 – · Slithery Fight 277회 41% · Trauma 71회 88%
- 국면별: r0-99 338회 77% · r100-249 414회 94% · r250-349 266회 90%

실패 사례 (66건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r71 · 드래곤 #3 L2: 샘 (34,16) 처음 거리 6 → r77 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:B:1 · r16 · 드래곤 #5 L3: 샘 (17,8) 처음 거리 6 → r22 도착, 30라운드 무리 진주 4개 중 우리 0 · 상대 4
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:A:1 · r265 · 드래곤 #365 L11: 샘 (19,8) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r265 도착, 30라운드 무리 진주 4개 중 우리 2 · 상대 0
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:A:1 · r0 · 드래곤 #8 L5: 샘 (33,2) 처음 거리 0 → r0 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_swarm · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_swarm:autarky:A:1 · r78 · 드래곤 #2 L2: 샘 (19,1) 처음 거리 6 → r80 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_swarm · Devil · 게임 exp/stack9nocov-a-px4:proxy4_swarm:devil:A:1 · r23 · 드래곤 #2 L2: 샘 (14,8) 처음 거리 5 → r36 도착, 30라운드 무리 진주 4개 중 우리 0 · 상대 4
- proxy4_swarm · Portals · 게임 exp/stack9nocov-a-px4:proxy4_swarm:portals:A:1 · r317 · 드래곤 #436 L15: 샘 (27,0) 처음 거리 0 → r317 도착, 30라운드 무리 진주 5개 중 우리 2 · 상대 0
- proxy4_swarm · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_swarm:trauma:A:1 · r222 · 드래곤 #5 L3: 샘 (11,10) 처음 거리 6 → r224 도착, 30라운드 무리 진주 3개 중 우리 0 · 상대 3
- proxy4_swarm · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_swarm:slithery_fight:A:1 · r0 · 드래곤 #8 L5: 샘 (33,2) 처음 거리 0 → r0 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_elim · Devil · 게임 exp/stack9nocov-a-px4:proxy4_elim:devil:A:1 · r47 · 드래곤 #9 L2: 샘 (8,15) 처음 거리 4 → r47 도착, 30라운드 무리 진주 4개 중 우리 2 · 상대 2

## 위협 모형 빈틈 (tg, stack4)

- 이번: 피함(tg) 56% · 위협 칸으로 감(tgx) 6396턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 98% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 98%) · 길이별 L2-5 14406 · L6-9 98 · L10+ 112
- 비교: 피함(tg) 57% · 위협 칸으로 감(tgx) 6180턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 98% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 98%) · 길이별 L2-5 14084 · L6-9 95 · L10+ 141
- 상대별: proxy4_elim 4434회 98% · proxy4_king 4847회 99% · proxy4_swarm 5335회 98%
- 지도별: Autarky 427회 97% · Default 3352회 99% · Devil 1083회 98% · Portals 6회 100% · Prisoners Dilemma 2회 100% · Queen Of Spades 1563회 98% · Schooltime 4113회 98% · Slithery Fight 2874회 99% · Trauma 179회 96% · Trophy 1017회 96%
- 국면별: r0-99 2401회 99% · r100-249 6120회 98% · r250-349 3387회 98% · r350-449 2130회 99% · r450+ 578회 98%

실패 사례 (260건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r89 · 드래곤 #7 L3: 피함(tg), 적 머리 경로 4칸 · 맨해튼 4칸(길이 3) → 박힘 r91 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:A:1 · r74 · 드래곤 #13 L2: 위협 칸으로 감(tgx), 적 머리 경로 1칸 · 맨해튼 1칸(길이 3) → 박힘 r75 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:B:1 · r218 · 드래곤 #47 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r220 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_king:queen_of_spades:A:1 · r214 · 드래곤 #72 L3: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r216 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:A:1 · r188 · 드래곤 #13 L3: 피함(tg), 적 머리 경로 4칸 · 맨해튼 3칸(길이 2) → 박힘 r189 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trophy · 게임 exp/stack9nocov-a-px4:proxy4_king:trophy:A:1 · r75 · 드래곤 #0 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 4) → 박힘 r77 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_king:trauma:A:1 · r229 · 드래곤 #118 L2: 피함(tg), 적 머리 경로 4칸 · 맨해튼 4칸(길이 2) → 박힘 r231 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:A:1 · r231 · 드래곤 #468 L3: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r233 박힘(상대 돌진), 상대 길이 4
- proxy4_swarm · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_swarm:autarky:A:1 · r45 · 드래곤 #4 L2: 피함(tg), 적 머리 경로 5칸 · 맨해튼 5칸(길이 2) → 박힘 r47 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack9nocov-a-px4:proxy4_swarm:default:A:1 · r183 · 드래곤 #17 L2: 피함(tg), 적 머리 경로 3칸 · 맨해튼 2칸(길이 2) → 박힘 r184 박힘(상대 돌진), 상대 길이 2

## 모이기 시작 제한 (gx, stack4; 드래곤 단위)

- 이번: 드래곤 220 (표식 턴 1191) · 몸(자손 포함) 끝까지 91% (기준 ≥80%) · 드래곤 자체 끝까지 생존 50% (참고) · 뒤에 희생 먹이기(feed)로 끝남 24
- 비교: 드래곤 135 (표식 턴 878) · 몸(자손 포함) 끝까지 93% (기준 ≥80%) · 드래곤 자체 끝까지 생존 63% (참고) · 뒤에 희생 먹이기(feed)로 끝남 13
- 상대별: proxy4_elim 49회 90% · proxy4_king 103회 91% · proxy4_swarm 68회 91%
- 지도별: Autarky 65회 97% · Default 21회 81% · Devil 7회 100% · Portals 18회 83% · Prisoners Dilemma 41회 95% · Queen Of Spades 12회 75% · Schooltime 35회 97% · Slithery Fight 10회 90% · Trauma 11회 64%
- 국면별: r450+ 220회 91%

실패 사례 (20건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:A:1 · r481 · 드래곤 #211 L4: gx 10턴 (r481–r492) → 죽음 r493 희생
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:A:1 · r488 · 드래곤 #657 L5: gx 3턴 (r488–r490) → 죽음 r491 희생
- proxy4_king · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_king:queen_of_spades:B:1 · r479 · 드래곤 #154 L9: gx 14턴 (r479–r492) → 죽음 r493 희생
- proxy4_king · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_king:trauma:A:1 · r490 · 드래곤 #255 L5: gx 1턴 (r490–r490) → 죽음 r493 희생
- proxy4_swarm · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_swarm:autarky:A:1 · r487 · 드래곤 #413 L4: gx 3턴 (r487–r489) → 죽음 r490 희생
- proxy4_swarm · Default · 게임 exp/stack9nocov-a-px4:proxy4_swarm:default:A:1 · r485 · 드래곤 #208 L4: gx 1턴 (r485–r485) → 죽음 r493 희생
- proxy4_swarm · Prisoners Dilemma · 게임 exp/stack9nocov-a-px4:proxy4_swarm:prisoners_dilemma:B:1 · r478 · 드래곤 #335 L4: gx 1턴 (r478–r478) → 죽음 r479 희생
- proxy4_swarm · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_swarm:slithery_fight:A:1 · r480 · 드래곤 #1134 L4: gx 2턴 (r480–r481) → 죽음 r482 희생
- proxy4_swarm · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_swarm:trauma:B:1 · r486 · 드래곤 #238 L4: gx 1턴 (r486–r486) → 죽음 r493 희생
- proxy4_elim · Default · 게임 exp/stack9nocov-a-px4:proxy4_elim:default:B:1 · r489 · 드래곤 #207 L4: gx 4턴 (r489–r492) → 죽음 r493 희생

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 416개 중 우리 팀 98% (지목한 아군 62%) · 상대 1% · 지목 아군 끝까지 생존 42% (그 뒤 죽은 원인: 갇힘 103, 희생 50, 박힘(상대 돌진) 1, 아군 머리 1, 돌진 6) · 지목 아군의 몸(자손 포함)이 끝까지 삶 92% · 최종 왕 36% (최종 왕이 지목 아군의 자손 64%)
- 비교: 실행 100% · 떨군 진주 501개 중 우리 팀 99% (지목한 아군 59%) · 상대 0% · 지목 아군 끝까지 생존 49% (그 뒤 죽은 원인: 돌진 1, 갇힘 98, 희생 62, 박힘(상대 돌진) 1, 아군 머리 8) · 지목 아군의 몸(자손 포함)이 끝까지 삶 91% · 최종 왕 39% (최종 왕이 지목 아군의 자손 63%)
- 상대별: proxy4_elim 116회 97% · proxy4_king 86회 99% · proxy4_swarm 77회 99%
- 지도별: Autarky 66회 100% · Default 1회 100% · Devil 2회 100% · Portals 116회 99% · Prisoners Dilemma 14회 100% · Queen Of Spades 4회 100% · Schooltime 2회 100% · Slithery Fight 74회 95%
- 국면별: r250-349 91회 97% · r350-449 139회 100% · r450+ 49회 96%

실패 사례 (5건 중 5건, 기보 확인용):
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:B:1 · r337 · 드래곤 #328 L3: #214(L17)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1
- proxy4_swarm · Portals · 게임 exp/stack9nocov-a-px4:proxy4_swarm:portals:A:1 · r475 · 드래곤 #547 L2: #545(L20)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_elim · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_elim:slithery_fight:A:1 · r300 · 드래곤 #450 L3: #35(L16)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1; 지목 아군 r402 돌진에 사망
- proxy4_elim · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_elim:slithery_fight:A:1 · r310 · 드래곤 #547 L2: #35(L16)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 1; 지목 아군 r402 돌진에 사망
- proxy4_elim · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_elim:slithery_fight:B:1 · r490 · 드래곤 #862 L3: #605(L43)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 83% · 조각 30라운드 생존 34% · 30라운드 안 1개 이상 먹음 62% (살아서 먹음 17%) · 평생 먹은 진주 평균 2.7 · 나중에 아군을 먹임 48% (conv 12, feed 2, 분열 뒤 평균 38.8라운드) · 끝까지 생존 3% · 30라운드 안 죽은 원인: 갇힘 11, 희생 8
- 비교: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 89% · 조각 30라운드 생존 34% · 30라운드 안 1개 이상 먹음 77% (살아서 먹음 26%) · 평생 먹은 진주 평균 2.7 · 나중에 아군을 먹임 46% (conv 12, feed 4, 분열 뒤 평균 49라운드) · 끝까지 생존 0% · 30라운드 안 죽은 원인: 갇힘 14, 희생 7, 돌진 1, 아군 머리 1
- 상대별: proxy4_elim 16회 63% · proxy4_king 6회 33% · proxy4_swarm 7회 57%
- 지도별: Autarky 4회 50% · Default 1회 0% · Portals 18회 61% · Slithery Fight 5회 60% · Trauma 1회 0%
- 국면별: r250-349 11회 36% · r350-449 18회 67%

실패 사례 (13건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:A:1 · r255 · 드래곤 #370 L9: 조각 L2 → 조각 죽음 r275 갇힘, 30라운드 안 먹은 진주 1
- proxy4_swarm · Portals · 게임 exp/stack9nocov-a-px4:proxy4_swarm:portals:B:1 · r360 · 드래곤 #482 L7: 조각 L2 → 조각 죽음 r363 갇힘, 상대 길이 16, 30라운드 안 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_swarm:slithery_fight:A:1 · r265 · 드래곤 #479 L7: 조각 L2 → 조각 죽음 r286 갇힘, 상대 길이 2, 30라운드 안 먹은 진주 5
- proxy4_elim · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_elim:autarky:B:1 · r306 · 드래곤 #246 L17: 조각 L2 → 조각 죽음 r313 갇힘, 30라운드 안 먹은 진주 0 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_elim · Portals · 게임 exp/stack9nocov-a-px4:proxy4_elim:portals:B:1 · r346 · 드래곤 #466 L9: 조각 L2 → 조각 죽음 r368 갇힘, 30라운드 안 먹은 진주 1
- proxy4_elim · Default · 게임 exp/stack9nocov-a-px4:proxy4_elim:default:B:1 · r349 · 드래곤 #144 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_elim · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_elim:trauma:A:1 · r364 · 드래곤 #174 L7: 조각 L2 → 조각 죽음 r373 갇힘, 30라운드 안 먹은 진주 6 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_elim · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_elim:slithery_fight:B:1 · r283 · 드래곤 #605 L27: 조각 L2 → 조각 죽음 r286 갇힘, 상대 길이 25, 30라운드 안 먹은 진주 0 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:B:1 · r350 · 드래곤 #561 L9: 조각 L2 → 조각 죽음 r350 갇힘, 30라운드 안 먹은 진주 0
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:B:1 · r355 · 드래곤 #559 L8: 조각 L2 → 조각 죽음 r367 갇힘, 30라운드 안 먹은 진주 6

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 3225개 (표식 턴 8240, 진주당 드래곤 1.4) · 질량 장부의 사망 진주 91% (자연 진주 2, 이미 없음 281) · 사망 진주 2942개 중 우리가 먹음 82% · 상대 16% · 아무도 안 먹음 2% · 표적으로 삼은 드래곤이 먹음 67% · 우리가 먹기까지 평균 3.1라운드 · 상대 머리가 같거나 더 가까웠던 932개: 우리 57% 대 상대 41% · 박치기 진주 465개: 우리 55% 대 상대 44% · 우리 팀 사망 진주 80% · 사망 뒤 첫 표적까지 평균 1.2라운드
- 비교: 표적 진주 3297개 (표식 턴 8372, 진주당 드래곤 1.4) · 질량 장부의 사망 진주 91% (자연 진주 0, 이미 없음 290) · 사망 진주 3007개 중 우리가 먹음 81% · 상대 17% · 아무도 안 먹음 2% · 표적으로 삼은 드래곤이 먹음 68% · 우리가 먹기까지 평균 3라운드 · 상대 머리가 같거나 더 가까웠던 871개: 우리 53% 대 상대 45% · 박치기 진주 468개: 우리 55% 대 상대 45% · 우리 팀 사망 진주 81% · 사망 뒤 첫 표적까지 평균 1.2라운드
- 상대별: proxy4_elim 1036회 81% · proxy4_king 1215회 83% · proxy4_swarm 974회 80%
- 지도별: Autarky 454회 99% · Default 484회 79% · Devil 188회 57% · Portals 681회 98% · Prisoners Dilemma 189회 82% · Queen Of Spades 219회 65% · Schooltime 332회 66% · Slithery Fight 476회 76% · Trauma 132회 82% · Trophy 70회 44%
- 국면별: r0-99 242회 68% · r100-249 789회 76% · r250-349 802회 82% · r350-449 927회 89% · r450+ 465회 83%

실패 사례 (543건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:A:1 · r75 · 드래곤 #6 L2: 진주 (6,7), 우리 머리 5칸 · 상대 머리 4칸, 박치기 0라운드 뒤 → 상대가 먹음 (11라운드 뒤), 표식 2턴
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:B:1 · r57 · 드래곤 #1 L3: 진주 (18,6), 우리 머리 4칸 · 상대 머리 2칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 1턴
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:A:1 · r177 · 드래곤 #181 L4: 진주 (18,11), 우리 머리 7칸 · 상대 머리 1칸, 상대 사망 4라운드 뒤 → 상대가 먹음 (1라운드 뒤), 표식 2턴
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9nocov-a-px4:proxy4_king:prisoners_dilemma:A:1 · r218 · 드래곤 #149 L2: 진주 (15,7), 우리 머리 3칸 · 상대 머리 1칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_king:queen_of_spades:A:1 · r57 · 드래곤 #2 L3: 진주 (8,33), 우리 머리 4칸 · 상대 머리 3칸, 박치기 1라운드 뒤 → 상대가 먹음 (6라운드 뒤), 표식 1턴
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:A:1 · r108 · 드래곤 #0 L2: 진주 (4,10), 우리 머리 6칸 · 상대 머리 3칸, 박치기 3라운드 뒤 → 상대가 먹음 (5라운드 뒤), 표식 4턴
- proxy4_king · Trophy · 게임 exp/stack9nocov-a-px4:proxy4_king:trophy:A:1 · r61 · 드래곤 #13 L2: 진주 (2,12), 우리 머리 4칸 · 상대 머리 3칸, 우리 팀 사망 2라운드 뒤 → 상대가 먹음 (3라운드 뒤), 표식 2턴
- proxy4_king · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_king:trauma:A:1 · r485 · 드래곤 #295 L2: 진주 (3,17), 우리 머리 4칸 · 상대 머리 9칸, 우리 팀 사망 0라운드 뒤 → 아무도 안 먹음, 표식 1턴
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:A:1 · r4 · 드래곤 #26 L2: 진주 (33,5), 우리 머리 5칸 · 상대 머리 10칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (140라운드 뒤), 표식 3턴
- proxy4_swarm · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_swarm:autarky:A:1 · r48 · 드래곤 #2 L3: 진주 (20,4), 우리 머리 3칸 · 상대 머리 4칸, 박치기 1라운드 뒤 → 상대가 먹음 (10라운드 뒤), 표식 4턴

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 1357 (그중 통로 고리 세대 1060, 판정에서 뺌) · 고리 밖 297: 처음 거리 평균 9.4 → 최소 5.8 · 3칸 안까지 감 32% · 희생까지 함 46% · 가는 길에 죽음 24% · 끝까지 생존 30%
- 비교: 모이기 드래곤 1327 (그중 통로 고리 세대 1006, 판정에서 뺌) · 고리 밖 321: 처음 거리 평균 10.1 → 최소 6.4 · 3칸 안까지 감 28% · 희생까지 함 42% · 가는 길에 죽음 29% · 끝까지 생존 29%
- 상대별: proxy4_elim 452회 62% · proxy4_king 524회 76% · proxy4_swarm 381회 78%
- 지도별: Autarky 490회 80% · Default 32회 73% · Devil 28회 75% · Portals 292회 81% · Prisoners Dilemma 384회 70% · Queen Of Spades 15회 57% · Schooltime 60회 60% · Slithery Fight 34회 60% · Trauma 22회 35%
- 국면별: r250-349 135회 79% · r350-449 879회 74% · r450+ 343회 69%

실패 사례 (114건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r485 · 드래곤 #437 L4: 왕까지 거리 9 → 최소 9 (1턴)
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:A:1 · r460 · 드래곤 #200 L5: 왕까지 거리 20 → 최소 11 (17턴)
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:A:1 · r387 · 드래곤 #122 L4: 왕까지 거리 5 → 최소 4 (2턴), 가는 길에 죽음 r398 갇힘
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:A:1 · r341 · 드래곤 #537 L4: 왕까지 거리 11 → 최소 11 (2턴), 가는 길에 죽음 r343 희생
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9nocov-a-px4:proxy4_king:prisoners_dilemma:A:1 · r386 · 드래곤 #169 L4: 왕까지 거리 4 → 최소 4 (1턴), 가는 길에 죽음 r408 갇힘, 상대 길이 11
- proxy4_king · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_king:queen_of_spades:A:1 · r472 · 드래곤 #184 L4: 왕까지 거리 9 → 최소 7 (10턴), 가는 길에 죽음 r481 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:A:1 · r439 · 드래곤 #349 L4: 왕까지 거리 6 → 최소 6 (2턴), 가는 길에 죽음 r440 돌진, 상대 길이 29
- proxy4_king · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_king:trauma:A:1 · r351 · 드래곤 #249 L5: 왕까지 거리 6 → 최소 6 (1턴), 가는 길에 죽음 r369 갇힘
- proxy4_swarm · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_swarm:autarky:A:1 · r396 · 드래곤 #402 L4: 왕까지 거리 7 → 최소 6 (2턴), 가는 길에 죽음 r399 희생
- proxy4_swarm · Devil · 게임 exp/stack9nocov-a-px4:proxy4_swarm:devil:A:1 · r485 · 드래곤 #506 L5: 왕까지 거리 6 → 최소 5 (2턴)

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 704개 중 우리 팀 76% (지목한 아군 48%) · 상대 5% · 지목 아군 끝까지 생존 63% (그 뒤 죽은 원인: 희생 75, 갇힘 34, 돌진 3, 박힘(상대 돌진) 6) · 지목 아군의 몸(자손 포함)이 끝까지 삶 77% · 최종 왕 32% (최종 왕이 지목 아군의 자손 37%)
- 비교: 실행 100% · 떨군 진주 656개 중 우리 팀 82% (지목한 아군 51%) · 상대 6% · 지목 아군 끝까지 생존 63% (그 뒤 죽은 원인: 희생 68, 갇힘 35, 박힘(상대 돌진) 4, 돌진 3, 아군 머리 1) · 지목 아군의 몸(자손 포함)이 끝까지 삶 81% · 최종 왕 25% (최종 왕이 지목 아군의 자손 35%)
- 상대별: proxy4_elim 87회 79% · proxy4_king 130회 78% · proxy4_swarm 100회 80%
- 지도별: Autarky 65회 97% · Default 31회 61% · Devil 18회 78% · Portals 35회 89% · Prisoners Dilemma 30회 93% · Queen Of Spades 12회 58% · Schooltime 37회 68% · Slithery Fight 32회 66% · Trauma 57회 75%
- 국면별: r250-349 1회 100% · r350-449 64회 94% · r450+ 252회 75%

실패 사례 (66건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:A:1 · r478 · 드래곤 #57 L5: #189(L6)에게 희생 → 진주 3개 중 우리 1, 지목 아군 1, 상대 2
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:A:1 · r448 · 드래곤 #505 L4: #507(L7)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0; 지목 아군 r449 돌진에 사망
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:B:1 · r489 · 드래곤 #638 L5: #649(L23)에게 희생 → 진주 3개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9nocov-a-px4:proxy4_king:prisoners_dilemma:B:1 · r487 · 드래곤 #127 L3: #439(L6)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_king:queen_of_spades:A:1 · r489 · 드래곤 #161 L3: #196(L4)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:A:1 · r484 · 드래곤 #449 L6: #398(L8)에게 희생 → 진주 3개 중 우리 2, 지목 아군 2, 상대 1
- proxy4_king · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_king:trauma:A:1 · r486 · 드래곤 #6 L3: #150(L2)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0; 지목 아군 r487 희생에 사망
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:A:1 · r444 · 드래곤 #506 L5: #926(L12)에게 희생 → 진주 3개 중 우리 0, 지목 아군 0, 상대 3
- proxy4_swarm · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_swarm:autarky:A:1 · r495 · 드래곤 #321 L11: #427(L29)에게 희생 → 진주 6개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Default · 게임 exp/stack9nocov-a-px4:proxy4_swarm:default:A:1 · r487 · 드래곤 #118 L2: #160(L3)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0

## 막다른 길 한입 (pocket-eat)

- 이번: 한입 100% · 2턴 안 분열 56% · 30라운드 뒤 가족 길이 변화 6.3 (줄지 않음 89%)
- 비교: 한입 100% · 2턴 안 분열 56% · 30라운드 뒤 가족 길이 변화 6.8 (줄지 않음 100%)
- 상대별: proxy4_elim 4회 50% · proxy4_king 4회 50% · proxy4_swarm 1회 100%
- 지도별: Devil 1회 0% · Portals 8회 63%
- 국면별: r0-99 4회 100% · r100-249 3회 0% · r250-349 1회 0% · r350-449 1회 100%

실패 사례 (4건 중 4건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:B:1 · r165 · 드래곤 #124 L4: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 -1
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:B:1 · r235 · 드래곤 #368 L4: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 5
- proxy4_elim · Portals · 게임 exp/stack9nocov-a-px4:proxy4_elim:portals:A:1 · r270 · 드래곤 #370 L18: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 5
- proxy4_elim · Portals · 게임 exp/stack9nocov-a-px4:proxy4_elim:portals:B:1 · r201 · 드래곤 #248 L10: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 2

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 20% · 30라운드 뒤 가족 길이 변화 8.6
- 비교: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 20% · 30라운드 뒤 가족 길이 변화 8.5
- 상대별: proxy4_elim 1403회 98% · proxy4_king 1483회 98% · proxy4_swarm 1349회 99%
- 지도별: Autarky 1533회 100% · Default 49회 90% · Devil 48회 81% · Portals 871회 94% · Prisoners Dilemma 1508회 100% · Queen Of Spades 46회 91% · Schooltime 32회 88% · Slithery Fight 91회 97% · Trauma 56회 95% · Trophy 1회 0%
- 국면별: r0-99 751회 99% · r100-249 1223회 99% · r250-349 947회 98% · r350-449 905회 97% · r450+ 409회 96%

실패 사례 (83건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:A:1 · r401 · 드래곤 #197 L4: 새끼 L2 → 새끼 죽음 r408 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:B:1 · r187 · 드래곤 #220 L5: 새끼 L3 → 새끼 죽음 r191 박힘(상대 돌진), 상대 길이 4, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:A:1 · r273 · 드래곤 #405 L11: 새끼 L9 → 새끼 죽음 r279 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -11
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:A:1 · r480 · 드래곤 #365 L8: 새끼 L6 → 새끼 죽음 r484 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -8
- proxy4_king · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_king:trauma:B:1 · r484 · 드래곤 #1 L4: 새끼 L2 → 새끼 죽음 r487 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Devil · 게임 exp/stack9nocov-a-px4:proxy4_swarm:devil:A:1 · r107 · 드래곤 #88 L4: 새끼 L2 → 새끼 죽음 r109 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Default · 게임 exp/stack9nocov-a-px4:proxy4_swarm:default:B:1 · r314 · 드래곤 #97 L4: 새끼 L2 → 새끼 죽음 r316 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Portals · 게임 exp/stack9nocov-a-px4:proxy4_swarm:portals:A:1 · r88 · 드래곤 #31 L4: 새끼 L2 → 새끼 죽음 r92 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_swarm:queen_of_spades:A:1 · r330 · 드래곤 #100 L4: 새끼 L2 → 새끼 죽음 r339 박힘(상대 돌진), 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_swarm:schooltime:A:1 · r343 · 드래곤 #350 L4: 새끼 L2 → 새끼 죽음 r344 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 83% · 그 밖(진짜로 갇힘) 805회
- 비교: 탈출 분열 뒤 남은 조각(고리의 일부) 83% · 그 밖(진짜로 갇힘) 776회
- 상대별: proxy4_elim 1517회 – · proxy4_king 1665회 – · proxy4_swarm 1458회 –
- 지도별: Autarky 1632회 – · Default 165회 – · Devil 49회 – · Portals 788회 – · Prisoners Dilemma 1543회 – · Queen Of Spades 79회 – · Schooltime 77회 – · Slithery Fight 186회 – · Trauma 110회 – · Trophy 11회 –
- 국면별: r0-99 790회 – · r100-249 1377회 – · r250-349 1067회 – · r350-449 1002회 – · r450+ 404회 –

## 탈출 질주 3칸 (esc)

- 이번: 질주 99% · 짧은 적 머리 4칸 안 81% · 몸 생존 5라운드 94% · 10라운드 93% (드래곤 자체 81%) · 10라운드 길이 변화 -5
- 비교: 질주 100% · 짧은 적 머리 4칸 안 82% · 몸 생존 5라운드 99% · 10라운드 99% (드래곤 자체 93%) · 10라운드 길이 변화 -2.8
- 상대별: proxy4_elim 19회 95% · proxy4_king 29회 86% · proxy4_swarm 21회 95%
- 지도별: Default 5회 100% · Devil 6회 100% · Queen Of Spades 7회 86% · Schooltime 24회 96% · Slithery Fight 25회 84% · Trophy 2회 100%
- 국면별: r0-99 8회 100% · r100-249 16회 94% · r250-349 8회 100% · r350-449 3회 100% · r450+ 34회 85%

실패 사례 (6건 중 6건, 기보 확인용):
- proxy4_king · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_king:queen_of_spades:A:1 · r463 · 드래곤 #197 L10: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r467 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:B:1 · r461 · 드래곤 #433 L17: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r461 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:B:1 · r491 · 드래곤 #1066 L35: 질주 3칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r495 박힘(상대 돌진), 상대 길이 4
- proxy4_swarm · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_swarm:slithery_fight:B:1 · r131 · 드래곤 #16 L27: 질주 3칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r133 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_elim:slithery_fight:B:1 · r477 · 드래곤 #620 L6: 질주 2칸 (가장 가까운 짧은 적 머리 21칸) → 죽음 r487 희생
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:B:1 · r493 · 드래곤 #1066 L34: 질주 3칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r495 박힘(상대 돌진), 상대 길이 4

## 위협 피하기 2칸 질주

- 이번: 질주 100% · 몸 10라운드 생존 95% (드래곤 자체 90%)
- 비교: 질주 100% · 몸 10라운드 생존 94% (드래곤 자체 90%)
- 상대별: proxy4_elim 213회 92% · proxy4_king 215회 95% · proxy4_swarm 239회 95%
- 지도별: Autarky 34회 94% · Default 112회 96% · Devil 50회 90% · Portals 1회 100% · Queen Of Spades 81회 99% · Schooltime 208회 95% · Slithery Fight 118회 92% · Trauma 26회 92% · Trophy 37회 92%
- 국면별: r0-99 136회 93% · r100-249 221회 95% · r250-349 153회 93% · r350-449 130회 95% · r450+ 27회 96%

실패 사례 (38건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r305 · 드래곤 #3 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r310 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Devil · 게임 exp/stack9nocov-a-px4:proxy4_king:devil:B:1 · r57 · 드래곤 #9 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r62 갇힘, 상대 길이 4
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:B:1 · r318 · 드래곤 #93 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 3) → 죽음 r318 아군 머리, 상대 길이 3
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:B:1 · r245 · 드래곤 #180 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 4) → 죽음 r255 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Trophy · 게임 exp/stack9nocov-a-px4:proxy4_king:trophy:A:1 · r98 · 드래곤 #13 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r105 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_king:trauma:A:1 · r378 · 드래곤 #38 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r388 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:A:1 · r276 · 드래곤 #505 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r285 갇힘, 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack9nocov-a-px4:proxy4_swarm:default:A:1 · r299 · 드래곤 #91 L4: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r299 아군 머리, 상대 길이 5
- proxy4_swarm · Devil · 게임 exp/stack9nocov-a-px4:proxy4_swarm:devil:B:1 · r54 · 드래곤 #8 L4: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 2) → 죽음 r64 돌진, 상대 길이 2
- proxy4_swarm · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_swarm:schooltime:A:1 · r201 · 드래곤 #28 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r207 박힘(상대 돌진), 상대 길이 2

## 포털 통과 (전체; PORTAL?=미탐색 출구)

- 이번: 미탐색 출구 1191회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 94% (드래곤 자체 80%) · 10라운드 89% · 10라운드 안 먹은 진주 0.8
- 비교: 미탐색 출구 1155회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 94% (드래곤 자체 79%) · 10라운드 89% · 10라운드 안 먹은 진주 0.8
- 상대별: proxy4_elim 929회 93% · proxy4_king 1027회 95% · proxy4_swarm 1081회 95%
- 지도별: Autarky 452회 94% · Default 870회 95% · Portals 1089회 95% · Prisoners Dilemma 58회 98% · Queen Of Spades 124회 87% · Schooltime 106회 92% · Slithery Fight 148회 93% · Trauma 182회 96% · Trophy 8회 50%
- 국면별: r0-99 286회 95% · r100-249 1025회 96% · r250-349 952회 94% · r350-449 623회 94% · r450+ 151회 88%

실패 사례 (173건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r140 · 드래곤 #101 L3: 포털 → 죽음 r141 갇힘, 10라운드 안 진주 0
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:A:1 · r162 · 드래곤 #49 L3: 포털(미탐색 출구) → 죽음 r162 아군 머리, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Portals · 게임 exp/stack9nocov-a-px4:proxy4_king:portals:A:1 · r42 · 드래곤 #16 L2: 포털(미탐색 출구) → 죽음 r42 아군 머리, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_king:queen_of_spades:A:1 · r50 · 드래곤 #12 L2: 포털 → 죽음 r53 갇힘, 10라운드 안 진주 0
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:A:1 · r371 · 드래곤 #323 L3: 포털(미탐색 출구) → 죽음 r371 돌진, 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_king:trauma:A:1 · r299 · 드래곤 #71 L3: 포털 → 죽음 r299 돌진, 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:A:1 · r196 · 드래곤 #327 L7: 포털 → 죽음 r197 박힘(상대 돌진), 상대 길이 2, 10라운드 안 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_swarm:autarky:A:1 · r294 · 드래곤 #304 L4: 포털(미탐색 출구) → 죽음 r294 희생, 상대 길이 4, 10라운드 안 진주 0
- proxy4_swarm · Default · 게임 exp/stack9nocov-a-px4:proxy4_swarm:default:A:1 · r237 · 드래곤 #79 L3: 포털(미탐색 출구) → 죽음 r237 아군 머리, 상대 길이 2, 10라운드 안 진주 0
- proxy4_swarm · Prisoners Dilemma · 게임 exp/stack9nocov-a-px4:proxy4_swarm:prisoners_dilemma:A:1 · r30 · 드래곤 #4 L3: 포털 → 죽음 r30 아군 머리, 상대 길이 3, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 38, 경로 35) · 잡은 길이 ≥ 우리 100% · 두 몸의 진주 우리 263 대 상대 338
- 비교: 충돌 성사 100% (인접 26, 경로 33) · 잡은 길이 ≥ 우리 100% · 두 몸의 진주 우리 170 대 상대 277
- 상대별: proxy4_elim 21회 52% · proxy4_king 22회 36% · proxy4_swarm 30회 40%
- 지도별: Default 9회 44% · Devil 6회 83% · Queen Of Spades 8회 63% · Schooltime 28회 18% · Slithery Fight 18회 56% · Trauma 4회 50%
- 국면별: r0-99 3회 0% · r100-249 8회 38% · r250-349 13회 8% · r350-449 34회 47% · r450+ 15회 73%

실패 사례 (42건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9nocov-a-px4:proxy4_king:default:A:1 · r369 · 드래곤 #20 L2: 돌진 경로 1칸 → 상대 L7 잡음, 진주 우리 0 대 상대 5
- proxy4_king · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_king:queen_of_spades:A:1 · r231 · 드래곤 #49 L3: 돌진 경로 2칸 → 상대 L5 잡음, 진주 우리 0 대 상대 5
- proxy4_king · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_king:schooltime:A:1 · r192 · 드래곤 #10 L2: 돌진 경로 1칸 → 상대 L5 잡음, 진주 우리 1 대 상대 3
- proxy4_king · Slithery Fight · 게임 exp/stack9nocov-a-px4:proxy4_king:slithery_fight:A:1 · r94 · 드래곤 #12 L2: 돌진 경로 1칸 → 상대 L5 잡음, 진주 우리 0 대 상대 4
- proxy4_swarm · Devil · 게임 exp/stack9nocov-a-px4:proxy4_swarm:devil:B:1 · r408 · 드래곤 #78 L3: 돌진 경로 2칸 → 상대 L30 잡음, 진주 우리 7 대 상대 8
- proxy4_swarm · Default · 게임 exp/stack9nocov-a-px4:proxy4_swarm:default:B:1 · r265 · 드래곤 #69 L2: 돌진 경로 1칸 → 상대 L5 잡음, 진주 우리 0 대 상대 4
- proxy4_swarm · Queen Of Spades · 게임 exp/stack9nocov-a-px4:proxy4_swarm:queen_of_spades:A:1 · r356 · 드래곤 #82 L3: 돌진 경로 2칸 → 상대 L10 잡음, 진주 우리 3 대 상대 4
- proxy4_swarm · Schooltime · 게임 exp/stack9nocov-a-px4:proxy4_swarm:schooltime:A:1 · r312 · 드래곤 #320 L3: 돌진 경로 2칸 → 상대 L22 잡음, 진주 우리 6 대 상대 7
- proxy4_swarm · Trauma · 게임 exp/stack9nocov-a-px4:proxy4_swarm:trauma:B:1 · r348 · 드래곤 #1 L2: 돌진 경로 1칸 → 상대 L7 잡음, 진주 우리 0 대 상대 5
- proxy4_elim · Default · 게임 exp/stack9nocov-a-px4:proxy4_elim:default:B:1 · r321 · 드래곤 #131 L2: 돌진 경로 1칸 → 상대 L5 잡음, 진주 우리 0 대 상대 4

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 비교: 먹음 100%
- 상대별: proxy4_elim 73회 100% · proxy4_king 74회 100% · proxy4_swarm 66회 100%
- 지도별: Autarky 7회 100% · Default 27회 100% · Devil 16회 100% · Portals 24회 100% · Prisoners Dilemma 2회 100% · Queen Of Spades 27회 100% · Schooltime 58회 100% · Slithery Fight 36회 100% · Trauma 6회 100% · Trophy 10회 100%
- 국면별: r0-99 31회 100% · r100-249 58회 100% · r250-349 36회 100% · r350-449 67회 100% · r450+ 21회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 92%
- 비교: 그 턴 사망 1% · 10라운드 생존 97%
- 상대별: proxy4_elim 26회 – · proxy4_king 37회 – · proxy4_swarm 10회 –
- 지도별: Default 9회 – · Devil 3회 – · Queen Of Spades 9회 – · Schooltime 27회 – · Slithery Fight 20회 – · Trophy 5회 –
- 국면별: r0-99 15회 – · r100-249 26회 – · r250-349 8회 – · r350-449 20회 – · r450+ 4회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 비교: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 11회 – · proxy4_king 17회 – · proxy4_swarm 10회 –
- 지도별: Default 7회 – · Devil 12회 – · Queen Of Spades 4회 – · Schooltime 5회 – · Slithery Fight 7회 – · Trauma 2회 – · Trophy 1회 –
- 국면별: r0-99 3회 – · r100-249 18회 – · r250-349 8회 – · r350-449 9회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/stack9nocov-a-px4` | 60 | 30 (0.50) | 50% | 0 (0.00) | 0 (0.00) | 4 | 26 | 0 | 1/7 (3.5) | 95 (1.58; 필사 21) | 16/71 (56) |
| 비교 `exp/stack9-a-px4` | 60 | 17 (0.28) | 53% | 0 (0.00) | 0 (0.00) | 3 | 12 | 1 | 1/2 (3.5) | 90 (1.50; 필사 27) | 21/94 (73.5) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.
- 이번 `exp/stack9nocov-a-px4`: gx 표식 턴 1191 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- 비교 `exp/stack9-a-px4`: gx 표식 턴 878 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/stack9nocov-a-px4` | 60 | 34272 | 0.6% (202) | 17.0% (5842) | 3926 | 1.5% (59) | 3.6% (140) | 30.7% (1204/3926) |
| 비교 `exp/stack9-a-px4` | 60 | 34905 | 0.7% (241) | 16.8% (5854) | 3765 | 1.2% (47) | 2.8% (106) | 24.2% (913/3765) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/stack9nocov-a-px4` | 전체 | 분열 | 4 (10%) | 14.3 | 67% | 81% | 3 | 2 |
| 이번 `exp/stack9nocov-a-px4` | 전체 | 2칸 질주 | 6 (15%) | 13.2 | 132% | 111% | 1 | 0 |
| 이번 `exp/stack9nocov-a-px4` | 전체 | 3칸 질주 | 8 (20%) | 13.5 | 66% | 62% | 5 | 3 |
| 이번 `exp/stack9nocov-a-px4` | 전체 | 한 걸음 | 23 (56%) | 12.2 | 33% | 33% | 20 | 17 |
| 이번 `exp/stack9nocov-a-px4` | 4칸 이상 | 분열 | 2 (11%) | 10.5 | 171% | 210% | 2 | 1 |
| 이번 `exp/stack9nocov-a-px4` | 4칸 이상 | 2칸 질주 | 5 (28%) | 14.6 | 134% | 112% | 1 | 0 |
| 이번 `exp/stack9nocov-a-px4` | 4칸 이상 | 3칸 질주 | 6 (33%) | 16 | 52% | 56% | 5 | 3 |
| 이번 `exp/stack9nocov-a-px4` | 4칸 이상 | 한 걸음 | 5 (28%) | 13.6 | 41% | 41% | 4 | 3 |
| 비교 `exp/stack9-a-px4` | 전체 | 분열 | 5 (16%) | 13.6 | 129% | 149% | 5 | 0 |
| 비교 `exp/stack9-a-px4` | 전체 | 2칸 질주 | 8 (26%) | 14.3 | 89% | 85% | 1 | 0 |
| 비교 `exp/stack9-a-px4` | 전체 | 3칸 질주 | 6 (19%) | 10.7 | 105% | 91% | 0 | 0 |
| 비교 `exp/stack9-a-px4` | 전체 | 한 걸음 | 12 (39%) | 13.9 | 142% | 147% | 9 | 3 |
| 비교 `exp/stack9-a-px4` | 4칸 이상 | 분열 | 4 (24%) | 13 | 138% | 175% | 4 | 0 |
| 비교 `exp/stack9-a-px4` | 4칸 이상 | 2칸 질주 | 6 (35%) | 17 | 85% | 89% | 1 | 0 |
| 비교 `exp/stack9-a-px4` | 4칸 이상 | 3칸 질주 | 3 (18%) | 9 | 152% | 122% | 0 | 0 |
| 비교 `exp/stack9-a-px4` | 4칸 이상 | 한 걸음 | 4 (24%) | 13 | 335% | 348% | 2 | 0 |

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (95건 중 10건):
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r288 · 드래곤 #298 L2: v8.7 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r349 · 드래곤 #321 L3: v7.7 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r355 · 드래곤 #93 L3: v10.6 PORTAL? → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:B:1 · r416 · 드래곤 #407 L3: v8.3 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:A:1 · r243 · 드래곤 #203 L3: v7.2 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:A:1 · r273 · 드래곤 #140 L3: v9.6 PORTAL? → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:A:1 · r278 · 드래곤 #214 L2: v-0.6 → 희생, 막은 우리 드래곤 L5
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:A:1 · r288 · 드래곤 #174 L2: v6.1 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:A:1 · r307 · 드래곤 #255 L2: v7.6 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9nocov-a-px4:proxy4_king:autarky:A:1 · r331 · 드래곤 #315 L3: v6.9 → 아군 머리, 막은 우리 드래곤 L2

## 지도·판본 인식 상세 (cand-mapid)

이번 (60판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 6 | 100% | 100% | 36/36 (36) | 1858 | 1858 (0) | 0 | 0 | 0 | 0 |
| Default a | 6 | 100% | 100% | 24/24 (24) | 395 | 395 (0) | 0 | 0 | 0 | 0 |
| Devil a | 6 | 100% | 100% | 18/18 (18) | 170 | 169 (0) | 0 | 0 | 0 | 19 |
| Portals a | 6 | 100% | 100% | 18/18 (18) | 1025 | 1024 (0) | 0 | 0 | 0 | 2 |
| Prisoners Dilemma a | 6 | 100% | 100% | 6/18 (6) | 1610 | 1602 (0) | 8 | 0 | 0 | 219 |
| Queen Of Spades a | 6 | 100% | 100% | 12/12 (12) | 214 | 207 (0) | 5 | 0 | 0 | 49 |
| Schooltime a | 6 | 100% | 100% | 18/18 (18) | 339 | 337 (0) | 0 | 0 | 0 | 12 |
| Slithery Fight a | 6 | 100% | 100% | 48/48 (48) | 422 | 415 (0) | 7 | 0 | 0 | 65 |
| Trauma a | 6 | 100% | 100% | 12/12 (12) | 228 | 228 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 6 | 100% | 100% | 12/12 (12) | 63 | 63 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 60/60, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

비교 (60판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 6 | 100% | 100% | 36/36 (36) | 1835 | 1835 (0) | 0 | 0 | 0 | 0 |
| Default a | 6 | 100% | 100% | 24/24 (24) | 338 | 338 (0) | 0 | 0 | 0 | 0 |
| Devil a | 6 | 100% | 100% | 18/18 (18) | 198 | 198 (0) | 0 | 0 | 0 | 19 |
| Portals a | 6 | 100% | 100% | 18/18 (18) | 1025 | 1024 (0) | 0 | 0 | 0 | 2 |
| Prisoners Dilemma a | 6 | 100% | 100% | 6/18 (6) | 1544 | 1535 (0) | 9 | 0 | 0 | 177 |
| Queen Of Spades a | 6 | 100% | 100% | 12/12 (12) | 164 | 162 (0) | 1 | 0 | 0 | 55 |
| Schooltime a | 6 | 100% | 100% | 18/18 (18) | 322 | 321 (0) | 0 | 0 | 0 | 16 |
| Slithery Fight a | 6 | 100% | 100% | 48/48 (48) | 505 | 497 (0) | 8 | 0 | 0 | 36 |
| Trauma a | 6 | 100% | 100% | 12/12 (12) | 249 | 249 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 6 | 100% | 100% | 12/12 (12) | 54 | 54 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 60/60, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

### Schooltime 판의 경제 (bsp의 가설 수준 지표, 정답 판본별)

| 묶음 | 판본 | 판 | 드래곤 수 r50 | r100 | r0–99 자연 진주 먹음 | 전멸당함 | 끝 최장(전멸 0) | 판당 bsp 분열 |
|---|---|---:|---|---|---|---:|---|---:|
| 이번 | a | 6 | 9 [8, 9] | 17 [13, 18] | 33 [20, 35] | 0% | 22 [12, 31] | 0 |
| 비교 | a | 6 | 9 [8, 9] | 16 [13, 16] | 33 [22, 48] | 0% | 22 [19, 36] | 0 |

- 기준값(`research/experiments/cand-mapid.md`, 웨이브 전에 적음): b에서 드래곤 수 r50 중앙 ≥ 6, r0–99 자연 진주 중앙 ≥ 14. 우리 merge2 계열 b 29판은 3 · 9, 떼 계열(swarm8·px) b 14판은 6 · 14, 상위권 b 승자는 8 · 32다. a는 bsp가 켜지지 않는 대조군이다.

## stack5: 영토 덮기 (csplit · F · cov) 게이트와 가설 수준 지표

- 기준값은 `research/experiments/cand-stack5.md`(웨이브 전)에서, 상위권 승자(TW) 값과 merge2 값은 `research/observations/top-territory.md`에서 왔다. 정의는 영토 연구의 `exp/territory-analysis/extract.js`와 같다(영토 = 시작 몸에서 더 가까운 팀의 칸, 샘 = 그 판 판본 파일의 평균 간격 ≤12, 보로노이 = 용량 1/평균 간격 가중, 거리 = 지도 위 이동 거리, 몸은 무시).

### 게이트 (기능 적용)

| 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|
| csplit 발동: 500라운드형 지도 r0–249 판당 | ≥20 | 21.2 (전체 1073회) | 21.3 (전체 1070회) |
| csplit 설계 상황: 부모가 팀 최장(≥8)이 아님 | ≥90% | 100% | 100% |
| csplit 새끼가 30라운드 안에 자연 진주 ≥1개 | ≥45% (TW 47% · 45%) | 38% (1073마리) | 40% (1070마리) |
| csplit 새끼 30라운드 생존 | ≥30% (TW 34% · 51%) | 78% | 76% |
| F 목표(드래곤·샘) 수, 3걸음 안 도착 | – | 1018, 도착 58% | 1066, 도착 58% |
| F 설계 상황: 실제 우리 영토 샘, 처음 표식 때 다른 우리 머리 3걸음 안 없음 | ≥80% | 82% | 81% |
| F 도착 뒤 30라운드 그 무리 자연 진주의 우리 몫(합산) | ≥85% (TW 자기 샘 90%) | 90% (상대 9%, 2459개) | 91% (상대 8%, 2540개) |
| F 같은 몫의 지도 평균(지도마다 합산, 같은 무게, Portals 제외) | ≥85% | 77% (Autarky 73%, Devil 65%, Prisoners Dilemma 100%, Trauma 94%, Slithery Fight 53%) | 65% (Devil 63%, Prisoners Dilemma 100%, Slithery Fight 65%, Trauma 100%, Autarky 0%) |
| cov 턴, 20라운드 안 우리 영토 자연 진주 | – | 0, – | 29775, 20% |

### 가설 수준 지표 (관찰; 500라운드형 / 전멸형)

| 지표 | 기준 | 상위권 승자 | merge2 | 이번 | 비교 |
|---|---|---|---|---|---|
| r100 우리 드래곤 수(r100까지 간 판) | ≥15 / ≥10 | 30 / 21 | 4 / 3 | 11.9 / 7.1 | 11.8 / 6.8 |
| r100 우리 영토 보로노이 몫(용량 가중, 판 평균) | ≥80% | 89% / 81% | 66% / 32% | 67% / 39% | 65% / 38% |
| r100 샘 지킴: 우리 영토 샘 중 우리 머리 3걸음 안(판 평균) | ≥50% | 61% / 55% | 22% / – | 25% / 58% | 25% / 61% |
| 우리 영토 자연 진주(r0부터 생성)를 상대가 먹은 몫(합산) | ≤25% | 11% / 16% | 56% / 55% | 56% / 52% | 56% / 58% |
| 우리 영토 샘 진주를 상대가 먹은 몫(합산) | ≤15% | 7% / 6% | 50% / 33% | 50% / 38% | 51% / 43% |

- 판 수(500라운드형 / 전멸형): 이번 30 / 30 · 비교 30 / 30. 판본 파일을 못 찾은 판: 이번 0 · 비교 0.

### 부작용: 우리 드래곤의 죽음 (판당; 전체 / r250 전)

| 원인 | 이번 | 비교 |
|---|---|---|
| 갇힘(빈 이웃 없음; 통로 고리의 남은 조각 포함) | 78 / 36.2 | 76.6 / 37.2 |
| 적 머리에 박힘 | 8.4 / 5.3 | 8.1 / 5.1 |
| 우리 드래곤끼리 머리 충돌(둘 다 죽음, 둘 다 셈) | 2.5 / 1 | 2.5 / 0.8 |

- 막힘에서 아군 머리를 피해 죽은 턴(no-exit s): 이번 140 · 비교 160

### 지도별 (이번)

| 지도 | 판 | csplit 판당 | 새끼 먹음 ≥1 | 새끼 30R 생존 | F 목표 · 도착 · 무리 진주 우리 몫 | r100 드래곤 | 보로노이 | 샘 지킴 | 상대가 먹은 영토 진주 | 상대가 먹은 샘 진주 |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| Autarky | 6 | 19.3 | 35% | 92% | 13 · 23% · 73% | 10 | 96% | 86% | 9% | 8% |
| Default | 6 | 27.2 | 38% | 74% | 0 · – · – | 11.3 | 27% | – | 67% | – |
| Devil | 6 | 12.8 | 30% | 75% | 62 · 39% · 65% | 9.8 | 36% | 17% | 79% | 82% |
| Portals | 6 | 13.2 | 49% | 56% | 523 · 77% · 99% | 11 | 100% | 25% | 0% | 0% |
| Prisoners Dilemma | 6 | 8 | 42% | 88% | 65 · 45% · 100% | 3.7 | 99% | 100% | 2% | 0% |
| Queen Of Spades | 6 | 16.5 | 47% | 71% | 0 · – · – | 4.5 | 24% | – | 60% | – |
| Schooltime | 6 | 24.5 | 40% | 93% | 7 · 0% · – | 15.2 | 20% | 0% | 77% | 60% |
| Slithery Fight | 6 | 36.7 | 33% | 76% | 277 · 40% · 53% | 18 | 26% | 5% | 80% | 86% |
| Trauma | 6 | 12.5 | 29% | 71% | 71 · 28% · 94% | 5.3 | 92% | 11% | 59% | 2% |
| Trophy | 6 | 8.2 | 51% | 76% | 0 · – · – | 6.3 | 9% | – | 80% | – |

## stack7: 수 바닥 분열(floor)과 왕 길이 상한(kcap) 게이트, 저수 에피소드, 가설 수준 지표, 지도 가르기

- 기준값은 `research/experiments/cand-stack7.md`(웨이브 전)에서, 상위권·우리 값은 `research/observations/our-eliminations.md`(2.6절, 1.3절, 2.2절)에서 왔다. 저수 에피소드와 부류의 정의는 전멸 연구(`exp/eliminations/top.js` I, `lib.js` classOf)와 같다: r50부터 5라운드 간격으로 처음 우리 수 1–3·상대 ≥8인 라운드 r(라운드 첫 턴의 수; r+20이 판 안이고 우리 전멸 전), 그 뒤 [r, r+20) 분열, 20라운드 뒤 4마리 이상이면 회복, 50라운드 안 전멸. 연구의 분열 수는 10라운드 칸 두 개의 전체 분열(탈출 분열 포함)이고, 여기서는 [r, r+20)을 그대로 센다.

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| floor | 발동(판당; floor 지도 판) | – | 7 (0.2; 42판) | 10 (0.2; 42판) |
| floor | 1. 설계 상황: 발동 때 상대 ≥8마리 | ≥90% | 86% | 90% |
| floor | 저수 에피소드가 있는 floor 지도 판 · 그 20라운드 안 floor 발동이 있었던 판 | (관찰) | 16 · 6% | 20 · 10% |
| floor | 2. 즉시 효과 A: 에피소드 20라운드 비탈출 분열(판당; floor 지도) | ≥2.0 (상위 LX·LS 2.0, 우리 0.5) | 0.1 (floor 0.1, kcap 0, csplit 0, lsplit 0; 탈출 포함 전체 0.3) | 0.3 (floor 0.1, kcap 0, csplit 0.1, lsplit 0.2; 탈출 포함 전체 0.4) |
| floor | 3. 즉시 효과 B: 에피소드 20라운드 뒤 4마리 이상(floor 지도) | ≥23% (상위 LX 23%, LS 26%, 우리 5%) | 0% (0/16) | 5% (1/20) |
| floor | 4. 즉시 효과 C: floor 새끼 30라운드 생존 | ≥34% (상위 패자 제 영토 새끼 34%, 승자 51%) | 71% (7마리) | 40% (10마리) |
| kcap | 발동(판당; kcap 지도 판) | – | 1 (0; 36판) | 1 (0; 36판) |
| kcap | 1. 설계 상황: 부모가 그 순간 팀 최장이고 r250 전 | ≥90% | 100% | 100% |
| kcap | 2. 즉시 효과: 새끼 10라운드 생존 | ≥74% (상위권 길이 4 분열 74.2%) | 100% (1마리) | 100% (1마리) |
| kcap | 2. 즉시 효과: 부모 10라운드 생존 | ≥55% (상위권 54.5%) | 100% | 100% |

### 저수 에피소드 (floor 지도 / 모든 지도; 판정은 floor 지도)

| 묶음 | 지도 | 판 | 에피소드 있음 | 처음 라운드(중앙) | 그때 우리 수 · 상대 수 | 그때 총길이 · 최장 | 20라운드 비탈출 분열 | floor · kcap | 탈출 포함 전체 | 20라운드 뒤 4마리 이상 | 50라운드 안 전멸 |
|---|---|---:|---:|---:|---|---|---:|---|---:|---:|---:|
| 이번 | floor 지도 | 42 | 38% | 145 | 2.9 · 40.2 | 8.4 · 3.8 | 0.1 | 0.1 · 0 | 0.3 | 0% | 19% |
| 이번 | floor 지도 중 전멸형 | 24 | 58% | 127.5 | 2.9 · 38.7 | 6.6 · 2.6 | 0.1 | 0.1 · 0 | 0.3 | 0% | 21% |
| 이번 | floor 지도 중 500형 | 18 | 11% | 355 | 3 · 50.5 | 20.5 · 11.5 | 0 | 0 · 0 | 0 | 0% | 0% |
| 이번 | 끄는 지도(Autarky·PD·Portals) | 18 | 11% | 275 | 2.5 · 9 | 34 · 24 | 0 | 0 · 0 | 10 | 0% | 0% |
| 이번 | 모든 지도 | 60 | 30% | 145 | 2.9 · 36.7 | 11.2 · 6 | 0.1 | 0.1 · 0 | 1.3 | 0% | 17% |
| 비교 | floor 지도 | 42 | 48% | 162.5 | 3 · 33.4 | 9.6 · 5 | 0.3 | 0.1 · 0 | 0.4 | 5% | 20% |
| 비교 | floor 지도 중 전멸형 | 24 | 71% | 145 | 2.9 · 32.2 | 6.4 · 2.4 | 0.3 | 0.1 · 0 | 0.4 | 6% | 24% |
| 비교 | floor 지도 중 500형 | 18 | 17% | 455 | 3 · 40.3 | 28 · 19.3 | 0.3 | 0 · 0 | 0.3 | 0% | 0% |
| 비교 | 끄는 지도(Autarky·PD·Portals) | 18 | 11% | 272.5 | 2.5 · 12 | 36.5 · 25.5 | 0 | 0 · 0 | 10 | 0% | 0% |
| 비교 | 모든 지도 | 60 | 37% | 162.5 | 2.9 · 31.5 | 12 · 6.8 | 0.3 | 0.1 · 0 | 1.2 | 5% | 18% |

- 상위권 기준(전멸 연구 2.6절, 전멸형): LX 72%가 그런 때를 겪고(처음 r105) 20라운드에 2.0번 나누며 23%가 회복, 42%가 50라운드 안 전멸. LS 69%, 2.0번, 26%, 0%. 우리 g4 LX 95%(r50), 0.5번, 5%, 15%.

### 가설 수준 지표 (관찰)

| 기능 | 지표 | 기준 | 상위권 · 이전 우리 | 이번 | 비교 |
|---|---|---|---|---|---|
| floor | r100 우리 드래곤 수(전멸형; 전멸은 0) — 전멸형 5지도 / PD 뺀 4지도 | ≥5.5 | 상위 LX 5.5, 우리 g4 LX 2.5 | 7.1 / 8 | 6.8 / 7.6 |
| floor | 전멸률(전멸형) | ≤66% | swarm8 66%, merge2 78% | 27% (8/30) / 33% (8/24) | 23% (7/30) / 29% (7/24) |
| floor | 전멸 라운드 중앙(전멸형) | ≥r235 | swarm8 235, merge2 150, stack1–3 163 | 181.5 / 181.5 | 160 / 160 |
| kcap | 우리 전멸 중 E2(왕 사냥) 비율(모든 지도) | ≤8% | 상위 LX 6%, 우리 16% | 0% (E1 0 · E2 0 · E3m 7 · E3l 1) | 0% (E1 0 · E2 0 · E3m 6 · E3l 1) |
| kcap | r50 우리 최장 평균(전멸형; 전멸은 0) — 5지도 / 4지도 | ≤4.5 | 상위 LS 3.8, 우리 g4 LX 6.8 | 4.8 / 3.3 | 4.7 / 3.1 |
| kcap | 전멸한 판의 길이 ≥8 죽음(판당; 모든 지도) | ≤0.4 | 우리 0.75 | 0 (8판) | 0 (7판) |

### 지도 가르기 (map= 표식으로 확인)

- floor는 Trophy, Queen Of Spades, Devil, Default, Schooltime, Trauma, Slithery Fight에서만, kcap은 그중 Slithery Fight를 뺀 여섯에서만 켠다. 봇은 프로세스마다 자기 창으로 지도 가족을 인식하고(`map=` 표식), 인식 전·`none`이면 끈다. "표식이 켜는 가족이 아닌 발동"은 발동한 프로세스의 마지막 `map=` 표식이 그 기능을 켜는 가족을 대지 않은 발동이다(0이어야 한다). "인식한 프로세스"는 마지막 표식이 그 판의 참 지도 가족을 댄 프로세스다.

| 묶음 | 지도(정답 판본) | 판 | floor 발동 | kcap 발동 | 표식이 켜는 가족이 아닌 발동 | 인식한 프로세스 |
|---|---|---:|---:|---:|---:|---:|
| 이번 | Autarky (끔) | 6 | 0 | 0 | 0 | 100% (1858/1858) |
| 이번 | Default | 6 | 0 | 0 | 0 | 100% (395/395) |
| 이번 | Devil a | 6 | 5 | 0 | 0 | 99% (169/170) |
| 이번 | Portals (끔) | 6 | 0 | 0 | 0 | 100% (1024/1025) |
| 이번 | Prisoners Dilemma (끔) | 6 | 0 | 0 | 0 | 100% (1610/1610) |
| 이번 | Queen Of Spades a | 6 | 2 | 0 | 0 | 99% (212/214) |
| 이번 | Schooltime a | 6 | 0 | 0 | 0 | 99% (337/339) |
| 이번 | Slithery Fight a (kcap 끔) | 6 | 0 | 0 | 0 | 100% (422/422) |
| 이번 | Trauma | 6 | 0 | 0 | 0 | 100% (228/228) |
| 이번 | Trophy | 6 | 0 | 1 | 0 | 100% (63/63) |
| 비교 | Autarky (끔) | 6 | 0 | 0 | 0 | 100% (1835/1835) |
| 비교 | Default | 6 | 0 | 0 | 0 | 100% (338/338) |
| 비교 | Devil a | 6 | 6 | 0 | 0 | 100% (198/198) |
| 비교 | Portals (끔) | 6 | 0 | 0 | 0 | 100% (1024/1025) |
| 비교 | Prisoners Dilemma (끔) | 6 | 0 | 0 | 0 | 100% (1544/1544) |
| 비교 | Queen Of Spades a | 6 | 2 | 0 | 0 | 99% (163/164) |
| 비교 | Schooltime a | 6 | 2 | 0 | 0 | 100% (321/322) |
| 비교 | Slithery Fight a (kcap 끔) | 6 | 0 | 0 | 0 | 100% (505/505) |
| 비교 | Trauma | 6 | 0 | 0 | 0 | 100% (249/249) |
| 비교 | Trophy | 6 | 0 | 1 | 0 | 100% (54/54) |

## stack8: 샘 목표 고르기(F2·F2p), 포털 출구의 아군(px2), 새끼의 몫(cl·ce)

- 기준값은 `research/experiments/cand-stack8.md`(로컬 확인 전, 18:20)에서 왔다. cl·ce의 기준값은 공급망 연구의 값(18:07)이다. F 목표(드래곤·샘 단위)와 포털 통과의 정의는 stack5 절과 "포털 통과" 절과 같다. Fp·cl·ce는 드래곤·진주 단위이고, 설계 상황은 처음 표식 때의 판이다.

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| F2 | 목표 수: F2 표식 / 모든 F(판당) | – | 1018 / 1018 (17) | 1066 / 1066 (17.8) |
| F2 | 1. 설계 상황: F2 표식 목표 (실제 샘 · 우리 영토 · 다른 머리 없음) | ≥90% | 82% (100% · 100% · 82%) | 81% (100% · 100% · 81%) |
| F2 | 1. 설계 상황: 모든 F 목표 | ≥80% | 82% | 81% |
| F2 | 2. 도착(3걸음 안): F2 표식 목표 / 모든 F | ≥80% | 58% / 58% | 58% / 58% |
| F2 | 3. 도착 뒤 30라운드 무리 자연 진주 우리 몫(F2 표식; 합산 · 지도 평균, Portals 제외) | ≥85% · ≥85% | 90% (2459개) · 77% | 91% (2540개) · 65% |
| F2 | 4. 겹친 추격: 다른 우리 드래곤의 같은 샘 목표와 겹침(F2 표식 / 모든 F) | ≤10% | 30% / 30% | 31% / 31% |
| F2p | Fp 진주 수(표식 턴) | – | 627 (1958턴) | 647 (2074턴) |
| F2p | 1. 설계 상황: 표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음 | ≥80% | 71% | 71% |
| F2p | 2. 즉시 효과: 그 드래곤이 10라운드 안에 먹음 · 상대가 먹음 | ≥48% · ≤5% | 35% · 22% | 34% · 22% |
| F2p | 끌어내기: F 표식 턴 가운데 유일하게 가장 가까운 자연 진주(7걸음 안, 무리 밖)에서 멀어진 턴 | ≤5% (관찰; W5+W6 15%) | 15% (후보가 있던 턴 28%; F 표식 턴 10489) | 16% (후보가 있던 턴 29%; F 표식 턴 10912) |
| px2 | 발동(px2 + px2x 턴, 판당) | – | 0 (0) | 0 (0) |
| px2 | 1. 설계 상황: 전 라운드 그 칸의 음파가 우리 드래곤에 멈춤 | ≥95% | – | – |
| px2 | 2. 즉시 효과 A: 건너지 않음(px2) | ≥80% | – | – |
| px2 | 3. 즉시 효과 B: 아군에 멈춘 탐침 뒤 아는 포털을 건너는 걸음에서 아군에 막혀 죽음(판당, v 무관) | ≤0.2 (W5–W7 0.69) | 0.67 (40건) | 0.68 (41건) |
| px2 | 보호: 포털 3라운드 몸 생존 | ≥95% | 94% | 94% |
| px2 | 보호: 건너는 걸음 아군 막힘 죽음(판당, 탐침·v 무관) | ≤0.75 (W5–W7 1.41) | 1.93 (116건) | 1.95 (117건) |
| cl | 진주 수(표식 턴) | – | 13097 (30911턴) | 12665 (29330턴) |
| cl | 설계 상황: 자연 진주, 우리 머리 가운데 표식한 조각만 가장 가까움 | ≥90% | 38% | 38% |
| cl | 즉시 효과: 조각이 먹음 · 우리 팀 · 우리 긴 드래곤 | ≥48% · ≥97% · ≤10% | 65% · 79% · 7% | 65% · 78% · 7% |
| ce | 진주 수(표식 턴) | – | 1370 (2204턴) | 1214 (1941턴) |
| ce | 설계 상황: 적 머리가 진주에서 우리 거리+1 안 | ≥80% | 85% | 81% |
| ce | 즉시 효과: 상대가 먹음 | ≤5% | 49% | 49% |
| ce | 보호: 표식 뒤 5라운드 안 박힘 | ≤19% | 7% | 7% |

- cl·ce의 가설 수준 지표(새끼 30라운드 먹음 ≥45%, 새끼 몫의 상대 몫 ≤3%/≤5%)는 공급망 스크립트 `exp/supply-chain/child_forage.js`로 잰다. 새끼 먹음은 stack5 절의 csplit 줄에도 있다.

### 포털 통과: 전 라운드 탐침(같은 칸, 같은 방향의 음파)별

| 묶음 | 출구 | 탐침 | 필사(v ≤ −20) | 통과 | 몸 3라운드 실패 | 건너는 걸음 아군 막힘 죽음 |
|---|---|---|---|---:|---:|---:|
| 이번 | 아는 포털 | clean | 아님 | 1377 | 5% | 41 |
| 이번 | 미탐색 | clean | 아님 | 886 | 3% | 13 |
| 이번 | 아는 포털 | ally | 아님 | 224 | 9% | 29 |
| 이번 | 미탐색 | clean | 필사 | 177 | 12% | 4 |
| 이번 | 아는 포털 | none | 아님 | 131 | 6% | 0 |
| 이번 | 아는 포털 | ally(머리) | 아님 | 55 | 13% | 11 |
| 이번 | 미탐색 | none | 필사 | 50 | 12% | 4 |
| 이번 | 미탐색 | ally | 필사 | 41 | 7% | 4 |
| 이번 | 아는 포털 | clean | 필사 | 28 | 14% | 3 |
| 이번 | 아는 포털 | enemy | 아님 | 21 | 19% | 1 |
| 이번 | 미탐색 | ally(머리) | 필사 | 18 | 28% | 6 |
| 이번 | 미탐색 | enemy | 필사 | 16 | 31% | 0 |
| 이번 | 아는 포털 | enemy(머리) | 아님 | 6 | 0% | 0 |
| 이번 | 미탐색 | enemy(머리) | 필사 | 3 | 33% | 0 |
| 이번 | 아는 포털 | enemy(머리) | 필사 | 2 | 0% | 0 |
| 이번 | 아는 포털 | none | 필사 | 1 | 0% | 0 |
| 이번 | 아는 포털 | ally | 필사 | 1 | 0% | 0 |
| 비교 | 아는 포털 | clean | 아님 | 1138 | 5% | 36 |
| 비교 | 미탐색 | clean | 아님 | 882 | 3% | 11 |
| 비교 | 아는 포털 | ally | 아님 | 215 | 7% | 26 |
| 비교 | 미탐색 | clean | 필사 | 148 | 16% | 6 |
| 비교 | 아는 포털 | none | 아님 | 111 | 5% | 2 |
| 비교 | 아는 포털 | ally(머리) | 아님 | 61 | 20% | 15 |
| 비교 | 미탐색 | ally | 필사 | 44 | 14% | 7 |
| 비교 | 미탐색 | none | 필사 | 43 | 9% | 3 |
| 비교 | 아는 포털 | clean | 필사 | 28 | 14% | 3 |
| 비교 | 미탐색 | ally(머리) | 필사 | 24 | 38% | 8 |
| 비교 | 아는 포털 | enemy | 아님 | 13 | 15% | 0 |
| 비교 | 아는 포털 | enemy(머리) | 아님 | 9 | 11% | 0 |
| 비교 | 미탐색 | enemy(머리) | 필사 | 8 | 25% | 0 |
| 비교 | 미탐색 | enemy | 필사 | 6 | 0% | 0 |
| 비교 | 아는 포털 | none | 필사 | 1 | 0% | 0 |

## stack9: 늦은 조각 풀 — 늦은 재분열(lsplit), frag 수 상한(fc), 영토 덮기 끌림(cov)

- 기준값은 `research/experiments/cand-stack9.md`(로컬 확인 결과를 보기 전, 21:04)에서, 상위권·우리 값은 `research/observations/supply-chain.md`(7절)에서 왔다. 가설 수준 지표는 그 연구의 코드(`exp/supply-chain/extract.js` analyse)를 같은 기보에 돌려 잰다. "판당"의 분모는 r250 뒤까지 간 우리 팀-경기다(500라운드형: Autarky, Portals, Schooltime, Slithery Fight, Trauma).

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| lsplit | 발동(모든 판당; 500라운드형 r250까지 간 판당) | – | 769 (12.8; 16.6) | 706 (11.8; 17.7) |
| lsplit | 1. 설계 상황: r250–429 · 부모 길이(분열 전) 4–6 · 우리 수(기보) < 목표 | ≥95% | 100% (100% · 100% · 100%; 표식의 수·목표 = 기보 100%) | 100% (100% · 100% · 100%; 표식의 수·목표 = 기보 100%) |
| lsplit | 2. 즉시 효과 A: 새끼가 30라운드 안에 자연 진주 ≥1 | ≥38% (승자의 늦은 2+2 새끼 38%) | 35% (769마리; 500형 33% · 전멸형 37%) | 34% (706마리; 500형 33% · 전멸형 36%) |
| lsplit | 3. 즉시 효과 B: 새끼가 죽을 때 떨군 진주의 우리 몫(합산) | ≥85% (승자 90%) | 78% (죽은 새끼 668마리, 진주 1103개; ≥8 21% · 상대 11%) | 81% (죽은 새끼 613마리, 진주 1017개; ≥8 27% · 상대 10%) |
| fc | 발동(판당) | – | 29 (0.5; frag 전체 29) | 31 (0.5; frag 전체 35) |
| fc | 1. 설계 상황: r250–420 · 부모가 팀 최장 아님 · 우리 수(기보) ≥ 옛 frag 상한 | ≥95% | 83% (100% · 83% · 100%) | 87% (100% · 87% · 100%) |
| fc | 2. 즉시 효과 A: 조각 제 몫(S1: 30라운드 살며 1개 이상 먹거나, 뒤에 희생 표식으로 아군을 먹임) | ≥50% | 55% (29마리) | 55% (31마리) |
| fc | 3. 즉시 효과 B: 조각이 죽을 때 떨군 진주 중 우리 ≥8이 먹은 몫(합산) | ≥20% (승자 부모 5–7 늦은 새끼 20%) | 51% (죽은 조각 28마리, 진주 49개; 우리 100% · 상대 0%) | 45% (죽은 조각 31마리, 진주 56개; 우리 89% · 상대 11%) |
| cov | 창 수(표식 턴; 판당 창) | – | 0 (0턴; 0) | 3406 (29775턴; 56.8) |
| cov | 게이트: 창 30라운드 안에 그 드래곤이 우리 영토 자연 진주 ≥1 | ≥47% (승자 자기 영토 태생 조각 47%) | – (창 안에 죽음 –) | 28% (창 안에 죽음 26%) |
| cov | (관찰) 표식 턴의 끝 칸이 기보 영토의 우리 쪽: 창을 연 턴 / 모든 표식 턴 | – | – / – | 87% / 85% |
| cov | (참고) W5 정의: 표식 턴마다 20라운드 안에 우리 영토 자연 진주 | – | – | 20% |

### 가설 수준 지표 (관찰; 500라운드형 r250–499, r250 뒤까지 간 팀-경기당)

| 지표 | 기준 | 상위권 승자 · 패자 · stack5 · stack6 | 이번 | 비교 |
|---|---|---|---|---|
| lsplit: 조각 탄생(태어날 때 길이 ≤3; 모든 분열) | ≥50 | 156 · 135 · 8.7 · 7.1 | 22.1 (lsplit 16.6, frag 0.9, 탈출 분열 4.6, 그 밖 0) | 23.1 (lsplit 17.7, frag 1.1, 탈출 분열 4.3, 그 밖 0.1) |
| lsplit: conv 상태 에피소드 | ≥30 | 57.6 · 39.4 · 17.1 · 20.1 | 26.6 | 29 |
| lsplit · fc: conv형 진주(조각 → ≥8) | ≥12 (fc ≥9) | 22.9 · 14.8 · 6.5 · 5.4 | 8.5 | 9.7 |
| lsplit: 조각 → 조각 희생 진주 | ≥10 | 34.9 · 28.6 · 2.0 · 2.0 | 5.5 | 6.8 |
| fc: frag 새끼(r250–499) | ≥3 | (부모 5–7·8+ 36) · – · 0.4 · 0.9 | 0.9 | 1.1 |
| (관찰) r350 우리 조각 수(길이 ≤4; r350까지 간 판 평균) | – | 30.5 · – · 6.2 · – | 11.6 | 11.4 |
| (참고) 전멸형: 조각 탄생 · conv 상태 에피소드 · conv형 진주 · 조각 → 조각 | – | 68 · 17.3 · – · – | 13.8 · 2.6 · 1.2 · 2.8 | 9.5 · 3.1 · 1 · 2.5 |
| cov: r100 우리 영토에서 적이 더 가까운 몫(판 평균; 500형 / 전멸형) | ≤17% (500형) | 11% · 17% · 27% · 25% | 32% / 60% | 34% / 61% |
| cov: r100 자기 영토 보로노이(판 평균; 500형 / 전멸형) | ≥80% | 89% · 83% · 72% · 74% | 67% / 39% | 65% / 38% |
| cov: 우리 영토 자연 진주를 상대가 먹은 몫(합산; 500형 / 전멸형) | ≤25% | 11% / 16% (승자) | 56% / 52% | 56% / 58% |

- 판 수(r250 뒤까지 간 팀-경기; 500라운드형 / 전멸형): 이번 30 / 24 · 비교 30 / 24. 공급 사슬 재구성 점검이 0이 아닌 판: 이번 0 · 비교 0; 지표 계산 오류: 이번 0 · 비교 0.

### 부작용 (관찰; 판정에 쓰지 않음)

| 항목 | 이번 | 비교 |
|---|---|---|
| lsplit 새끼의 끝: 끝까지 삶 · 표식 희생(conv·feed) · 그 밖 희생 · 갇힘 · 박힘 · 아군 머리 · 그 밖 | 13% · 36% · 1% · 34% · 7% · 5% · 5% (769마리) | 13% · 43% · 0% · 28% · 6% · 5% · 4% (706마리) |
| 어린 조각 규칙(20라운드): lsplit 새끼가 20라운드 안에 끝남(갇힘 · 박힘 · 희생 · 그 밖) / 뒤에 conv·feed로 아군을 먹임(그때 나이 중앙) | 21% (117 · 16 · 9 · 18) / 36% (79) | 19% (91 · 15 · 8 · 18) / 43% (67) |
| lsplit 부모: 10라운드 생존 · 부모 몸(새끼 포함) 30라운드 뒤 길이 변화 평균 · 부모가 죽을 때 떨군 진주 우리 몫 | 85% · 3.1 · 71% (1138개) | 88% · 4.3 · 77% (1043개) |
| lsplit 모이기 창(r340 뒤) 발동 · 그 새끼 30라운드 안 자연 진주 ≥1 | 455 · 39% | 434 · 36% |
| 우리 드래곤의 죽음 r250 뒤(판당): 갇힘 · 적 머리에 박힘 · 우리끼리 머리 충돌(둘 다 셈) | 41.8 · 3.1 · 1.6 | 39.4 · 3 · 1.7 |
| 모이기(g) 드래곤(통로 고리 밖): 수 · 왕 3칸 안까지 감 · 희생까지 함 · 가는 길에 죽음 | 297 · 32% · 46% · 24% | 321 · 28% · 42% · 29% |
| 희생 먹이기(feed) · conv: 판당 발동, 떨군 진주 우리 몫 | feed 5.3, 76% · conv 4.7, 98% | feed 5.1, 82% · conv 5.5, 99% |
| 끝 왕 길이(500라운드형 끝까지 간 판) | 22.1 (30판) | 25.4 (30판) |

