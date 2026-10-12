# 구현 적용 확인

- 대상: `exp/stack9-a-px4+exp/stack9-b-px4` 120판 · 비교: `exp/stack8-a-px4+exp/stack8-b-px4` 120판
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
| 늦은 재분열 (lsplit, stack9) | 1298 (10.8) | 33% | 0 (0) | – |
| 영토 덮기 끌림 30라운드 창 (cov 창, stack9; 드래곤·창 단위) | 6918 (57.7) | 27% | 0 (0) | – |
| 몫이 있어 F 끌림 멈춤 (Fp, stack8; 드래곤·진주 단위) | 1332 (11.1) | 34% | 1406 (11.7) | 35% |
| 몫을 긴 아군에게 넘기지 않음 (cl, stack8; 드래곤·진주 단위) | 22010 (183.4) | 65% | 17951 (149.6) | 67% |
| 몫을 한 걸음 가까운 적에게 넘기지 않음 (ce, stack8; 드래곤·진주 단위) | 2225 (18.5) | 52% | 1895 (15.8) | 49% |
| 아군을 친 탐침 뒤 포털 (px2, stack8) | 0 (0) | – | 838 (7) | 38% |
| 수 바닥 분열 (split floor, stack7) | 20 (0.2) | 55% | 58 (0.5) | 71% |
| 왕 길이 상한 분열 (split kcap, stack7) | 5 (0) | 100% | 2 (0) | 100% |
| 지도·판본 인식 (map=, cand-mapid; 판 단위) | 120 (1) | 100% | 120 (1) | 100% |
| Schooltime b 초반 분열 (split bsp, cand-mapid) | 53 (0.4) | 98% | 56 (0.5) | 96% |
| 덮기 분열 (csplit, stack5) | 1904 (15.9) | 40% | 1881 (15.7) | 39% |
| 샘 지킴 (F, stack5; 드래곤·샘 단위) | 2075 (17.3) | 88% | 2043 (17) | 86% |
| 영토 덮기 끌림 (cov, stack5) | 63738 (531.2) | 20% | 0 (0) | – |
| 위협 모형 빈틈 (tg, stack4) | 28711 (239.3) | 98% | 24617 (205.1) | 98% |
| 모이기 시작 제한 (gx, stack4; 드래곤 단위) | 294 (2.5) | 91% | 171 (1.4) | 96% |
| 큰 아군 곁 희생 (conv, stack1 M1) | 606 (5.1) | 99% | 290 (2.4) | 96% |
| 조각 떼기 (split frag, stack2 S1) | 60 (0.5) | 58% | 32 (0.3) | 69% |
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 6065 (50.5) | 82% | 4377 (36.5) | 81% |
| 왕에게 모이기 (g, 드래곤 단위) | 2382 (19.9) | 71% | 1833 (15.3) | 80% |
| 희생 먹이기 (feed) | 558 (4.7) | 82% | 327 (2.7) | 83% |
| 막다른 길 한입 (pocket-eat) | 1018 (8.5) | 99% | 1028 (8.6) | 98% |
| 탈출 분열 (escape-split) | 7956 (66.3) | 98% | 7935 (66.1) | 98% |
| 출구 없음 (no-exit) | 8557 (71.3) | – | 8073 (67.3) | – |
| 정책 분열 (split) | 0 (0) | – | 4 (0) | 100% |
| 탈출 질주 3칸 (esc) | 130 (1.1) | 98% | 178 (1.5) | 93% |
| 위협 피하기 2칸 질주 | 1244 (10.4) | 94% | 1272 (10.6) | 94% |
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 5591 (46.6) | 94% | 5320 (44.3) | 94% |
| 돌진 (TRADE) | 94 (0.8) | 35% | 96 (0.8) | 35% |
| 먹이 질주 (2칸 이상, 먹은 것) | 324 (2.7) | 100% | 319 (2.7) | 100% |
| 기타 2칸 질주 | 133 (1.1) | – | 146 (1.2) | – |
| 마지막 돌진 (last-trade) | 83 (0.7) | – | 70 (0.6) | – |

- 건강: 턴 532913, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 비교 건강: 턴 437071, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 16687턴 · 끝판(late) 18543턴 · 돌진 신뢰(T, 탈출 끔) 7턴, 그 직후 박혀 죽음 0

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 비교 |
|---|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 2% (115/5996턴) | 2% (91/4963턴) |
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 53.6칸 (16.9회), 진주 우리 90% · 상대 2% | 36.5칸 (8.4회), 진주 우리 91% · 상대 3% |
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 0.6칸 (판당 0.03회) | 0칸 (판당 0.00회) |
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 25% (1761/7023턴) | 27% (2364/8801턴) |
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.025회 (3건, 27칸) | 판당 0.050회 (6건, 100칸) |
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 13.5마리 (60판) | 6.2마리 (60판) |
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 28.6회 | 19.9회 |
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 52% (우리 42%) | 52% (우리 41%) |
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 9 대 상대 24.2 (8.8회) · 박힌 교환의 우리 몫 22% (422회) | 우리 8.5 대 상대 23.6 (7.8회) · 박힌 교환의 우리 몫 20% (366회) |
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 10.4개 | 8.4개 |

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 늦은 재분열 (lsplit, stack9)

- 이번: 분열 100% · 설계 상황(r250–429, 부모 길이 4–6, 우리 수 < 목표; 기보) 100% (기준 ≥95%) · 새끼 30라운드 안 자연 진주 ≥1 33% (기준 ≥38%) · 죽은 새끼 1125마리의 떨군 진주 1856개 중 우리 79% (기준 ≥85%) · ≥8 24% · 상대 10% · 새끼 10·30라운드 생존 88% · 71% · 부모 길이 평균 4.3 · r340 뒤 773회
- 상대별: proxy4_elim 393회 35% · proxy4_king 522회 34% · proxy4_swarm 383회 31%
- 지도별: Autarky 339회 34% · Default 192회 34% · Devil 47회 64% · Portals 72회 24% · Prisoners Dilemma 37회 32% · Queen Of Spades 69회 22% · Schooltime 165회 45% · Slithery Fight 179회 27% · Trauma 198회 28%
- 국면별: r250-349 589회 30% · r350-449 709회 36%

실패 사례 (866건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:B:1 · r262 · 드래곤 #196 L4: 새끼 L2 · 우리 20/21마리 → 새끼 죽음 r277 갇힘(나이 15, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r255 · 드래곤 #91 L4: 새끼 L2 · 우리 18/22마리 → 새끼 죽음 r323 돌진(나이 68, 진주 2개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r370 · 드래곤 #560 L6: 새끼 L2 · 우리 10/11마리 → 새끼 죽음 r385 갇힘(나이 15, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9-a-px4:proxy4_king:prisoners_dilemma:A:1 · r329 · 드래곤 #149 L4: 새끼 L2 · 우리 10/11마리 → 새끼 죽음 r482 희생(나이 153, 진주 2개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r250 · 드래곤 #64 L4: 새끼 L2 · 우리 9/19마리 → 새끼 죽음 r433 갇힘(나이 183, 진주 2개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r255 · 드래곤 #21 L4: 새끼 L2 · 우리 9/40마리 → 새끼 죽음 r346 박힘(상대 돌진)(나이 91, 진주 1개 중 우리 0), 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r250 · 드래곤 #327 L4: 새끼 L2 · 우리 22/37마리 → 새끼 죽음 r455 희생(나이 205, 진주 2개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r264 · 드래곤 #100 L4: 새끼 L2 · 우리 15/25마리 → 새끼 죽음 r315 갇힘(나이 51, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack9-a-px4:proxy4_swarm:autarky:A:1 · r279 · 드래곤 #280 L4: 새끼 L2 · 우리 16/21마리 → 새끼 끝까지 생존, 30라운드 안 자연 진주 0
- proxy4_swarm · Default · 게임 exp/stack9-a-px4:proxy4_swarm:default:A:1 · r263 · 드래곤 #12 L4: 새끼 L2 · 우리 8/22마리 → 새끼 끝까지 생존, 30라운드 안 자연 진주 0

## 영토 덮기 끌림 30라운드 창 (cov 창, stack9; 드래곤·창 단위)

- 이번: 창 6918개 (표식 턴 63738) · 창 30라운드 안 우리 영토 자연 진주 ≥1 27% (기준 ≥47%) · 창 안에 죽음 26% · 판 끝에 잘린 창 242 · 창을 연 표식 턴의 끝 칸이 기보 영토의 우리 쪽 89%
- 상대별: proxy4_elim 2283회 28% · proxy4_king 2426회 27% · proxy4_swarm 2209회 27%
- 지도별: Autarky 789회 35% · Default 874회 16% · Devil 348회 32% · Portals 816회 43% · Prisoners Dilemma 104회 12% · Prisoners Dilemma (10) 133회 3% · Queen Of Spades 624회 19% · Schooltime 1058회 27% · Slithery Fight 1010회 34% · Trauma 976회 19% · Trophy 186회 37%
- 국면별: r0-99 1637회 37% · r100-249 2291회 23% · r250-349 1385회 23% · r350-449 1199회 29% · r450+ 406회 23%

실패 사례 (5023건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:B:1 · r0 · 드래곤 #5 L3: 창 r0–r30, 표식 10턴 → 못 먹음
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r0 · 드래곤 #0 L4: 창 r0–r30, 표식 6턴 → 못 먹음
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:A:1 · r68 · 드래곤 #0 L2: 창 r68–r98, 표식 3턴 → 못 먹음
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r11 · 드래곤 #6 L2: 창 r11–r41, 표식 4턴 → 못 먹음
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9-a-px4:proxy4_king:prisoners_dilemma:A:1 · r0 · 드래곤 #2 L3: 창 r0–r30, 표식 14턴 → 못 먹음
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r12 · 드래곤 #0 L3: 창 r12–r42, 표식 19턴 → 못 먹음
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r0 · 드래곤 #0 L4: 창 r0–r30, 표식 4턴 → 못 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r2 · 드래곤 #0 L2: 창 r2–r32, 표식 1턴 → 창 안에 죽음
- proxy4_king · Trophy · 게임 exp/stack9-a-px4:proxy4_king:trophy:A:1 · r74 · 드래곤 #9 L2: 창 r74–r104, 표식 31턴 → 못 먹음
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r0 · 드래곤 #0 L4: 창 r0–r30, 표식 12턴 → 못 먹음

## 몫이 있어 F 끌림 멈춤 (Fp, stack8; 드래곤·진주 단위)

- 이번: 진주 1332개 (표식 턴 4421; 표식 때 진주 있음 97%) · 설계 상황(표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음) 71% · 그 드래곤이 먹음 35% (10라운드 안 34%) · 우리 팀 71% · 우리 긴 드래곤 16% · 상대 22%
- 비교: 진주 1406개 (표식 턴 4526; 표식 때 진주 있음 97%) · 설계 상황(표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음) 70% · 그 드래곤이 먹음 36% (10라운드 안 35%) · 우리 팀 72% · 우리 긴 드래곤 17% · 상대 22%
- 상대별: proxy4_elim 418회 32% · proxy4_king 458회 33% · proxy4_swarm 456회 38%
- 지도별: Autarky 1회 100% · Devil 42회 32% · Portals 880회 42% · Prisoners Dilemma 21회 71% · Prisoners Dilemma (10) 2회 0% · Schooltime 3회 0% · Slithery Fight 372회 16% · Trauma 11회 18%
- 국면별: r0-99 484회 33% · r100-249 461회 32% · r250-349 387회 39%

실패 사례 (850건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:A:1 · r41 · 드래곤 #9 L4: 진주 (7,13) 우리 거리 12 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r17 · 드래곤 #6 L2: 진주 (13,6) 우리 거리 99 → 상대가 먹음
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9-a-px4:proxy4_king:prisoners_dilemma:A:1 · r150 · 드래곤 #34 L3: 진주 (12,11) 우리 거리 3 → 다른 우리 드래곤이 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r0 · 드래곤 #8 L5: 진주 (31,5) 우리 거리 5 → 다른 우리 드래곤이 먹음
- proxy4_swarm · Devil · 게임 exp/stack9-a-px4:proxy4_swarm:devil:A:1 · r41 · 드래곤 #9 L4: 진주 (7,13) 우리 거리 12 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_swarm · Portals · 게임 exp/stack9-a-px4:proxy4_swarm:portals:A:1 · r17 · 드래곤 #6 L2: 진주 (13,6) 우리 거리 99 → 상대가 먹음
- proxy4_swarm · Schooltime · 게임 exp/stack9-a-px4:proxy4_swarm:schooltime:A:1 · r147 · 드래곤 #19 L3: 진주 (23,39) 우리 거리 99 → 아무도 안 먹음
- proxy4_swarm · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_swarm:slithery_fight:B:1 · r0 · 드래곤 #9 L5: 진주 (31,21) 우리 거리 5 → 다른 우리 드래곤이 먹음
- proxy4_elim · Devil · 게임 exp/stack9-a-px4:proxy4_elim:devil:A:1 · r131 · 드래곤 #72 L2: 진주 (9,0) 우리 거리 99 → 상대가 먹음
- proxy4_elim · Portals · 게임 exp/stack9-a-px4:proxy4_elim:portals:A:1 · r21 · 드래곤 #2 L7: 진주 (27,5) 우리 거리 5 (설계 밖) → 다른 우리 드래곤이 먹음

## 몫을 긴 아군에게 넘기지 않음 (cl, stack8; 드래곤·진주 단위)

- 이번: 진주 22010개 (표식 턴 53286; 표식 때 진주 있음 97%) · 설계 상황(자연 진주이고 우리 머리 가운데 표식한 조각만 가장 가까움) 40% · 그 드래곤이 먹음 65% (10라운드 안 64%) · 우리 팀 78% · 우리 긴 드래곤 7% · 상대 15%
- 비교: 진주 17951개 (표식 턴 42455; 표식 때 진주 있음 97%) · 설계 상황(자연 진주이고 우리 머리 가운데 표식한 조각만 가장 가까움) 39% · 그 드래곤이 먹음 67% (10라운드 안 66%) · 우리 팀 79% · 우리 긴 드래곤 6% · 상대 16%
- 상대별: proxy4_elim 7102회 65% · proxy4_king 7900회 65% · proxy4_swarm 7008회 65%
- 지도별: Autarky 4765회 91% · Default 1847회 68% · Devil 970회 70% · Portals 2375회 62% · Prisoners Dilemma 1738회 95% · Prisoners Dilemma (10) 55회 30% · Queen Of Spades 1490회 52% · Schooltime 2453회 49% · Slithery Fight 3951회 38% · Trauma 1913회 58% · Trophy 453회 61%
- 국면별: r0-99 4981회 64% · r100-249 6213회 66% · r250-349 4060회 66% · r350-449 5022회 64% · r450+ 1734회 65%

실패 사례 (7484건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:B:1 · r4 · 드래곤 #3 L3: 진주 (35,16) 우리 거리 5 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r4 · 드래곤 #12 L2: 진주 (10,29) 우리 거리 99 → 상대가 먹음
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:A:1 · r22 · 드래곤 #2 L2: 진주 (14,8) 우리 거리 6 → 상대가 먹음
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r10 · 드래곤 #6 L2: 진주 (15,1) 우리 거리 4 → 다른 우리 드래곤이 먹음
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9-a-px4:proxy4_king:prisoners_dilemma:A:1 · r152 · 드래곤 #34 L3: 진주 (12,11) 우리 거리 5 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r16 · 드래곤 #2 L2: 진주 (6,33) 우리 거리 4 → 다른 우리 드래곤이 먹음
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r29 · 드래곤 #2 L2: 진주 (10,39) 우리 거리 99 → 상대가 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r1 · 드래곤 #12 L2: 진주 (21,1) 우리 거리 3 → 다른 우리 드래곤이 먹음
- proxy4_king · Trophy · 게임 exp/stack9-a-px4:proxy4_king:trophy:A:1 · r27 · 드래곤 #6 L3: 진주 (6,6) 우리 거리 99 → 상대가 먹음
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r33 · 드래곤 #4 L2: 진주 (11,10) 우리 거리 99 → 다른 우리 드래곤이 먹음

## 몫을 한 걸음 가까운 적에게 넘기지 않음 (ce, stack8; 드래곤·진주 단위)

- 이번: 진주 2225개 (표식 턴 3556; 표식 때 진주 있음 97%) · 설계 상황(적 머리가 진주에서 우리 거리+1 안) 81% · 그 드래곤이 먹음 26% (10라운드 안 24%) · 우리 팀 38% · 우리 긴 드래곤 5% · 상대 48% · 5라운드 안 박힘 7%
- 비교: 진주 1895개 (표식 턴 2959; 표식 때 진주 있음 96%) · 설계 상황(적 머리가 진주에서 우리 거리+1 안) 83% · 그 드래곤이 먹음 28% (10라운드 안 26%) · 우리 팀 39% · 우리 긴 드래곤 5% · 상대 51% · 5라운드 안 박힘 6%
- 상대별: proxy4_elim 723회 56% · proxy4_king 802회 53% · proxy4_swarm 700회 47%
- 지도별: Autarky 32회 71% · Default 255회 51% · Devil 116회 49% · Portals 92회 96% · Prisoners Dilemma 23회 94% · Prisoners Dilemma (10) 18회 29% · Queen Of Spades 226회 49% · Schooltime 473회 46% · Slithery Fight 775회 54% · Trauma 126회 47% · Trophy 89회 32%
- 국면별: r0-99 373회 37% · r100-249 692회 46% · r250-349 434회 52% · r350-449 531회 65% · r450+ 195회 63%

실패 사례 (1033건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:B:1 · r184 · 드래곤 #7 L2: 진주 (18,16) 우리 거리 4 → 상대가 먹음
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r211 · 드래곤 #48 L2: 진주 (22,7) 우리 거리 3 (설계 밖) → 상대가 먹음
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:A:1 · r22 · 드래곤 #2 L2: 진주 (14,8) 우리 거리 6 → 상대가 먹음
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r178 · 드래곤 #181 L4: 진주 (12,7) 우리 거리 99 (설계 밖) → 상대가 먹음
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r99 · 드래곤 #2 L2: 진주 (6,33) 우리 거리 4 → 상대가 먹음
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r40 · 드래곤 #10 L3: 진주 (14,3) 우리 거리 4 (설계 밖) → 상대가 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r28 · 드래곤 #47 L2: 진주 (37,26) 우리 거리 99 (설계 밖) → 상대가 먹음
- proxy4_king · Trophy · 게임 exp/stack9-a-px4:proxy4_king:trophy:A:1 · r63 · 드래곤 #14 L2: 진주 (14,17) 우리 거리 6 → 상대가 먹음
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r180 · 드래곤 #16 L2: 진주 (19,12) 우리 거리 5 → 상대가 먹음
- proxy4_swarm · Autarky · 게임 exp/stack9-a-px4:proxy4_swarm:autarky:A:1 · r322 · 드래곤 #2 L2: 진주 (35,1) 우리 거리 6 → 상대가 먹음

## 수 바닥 분열 (split floor, stack7)

- 이번: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 95% · 적 머리가 7×7 시야 안 35% · 부모 길이 평균 4.4 · 우리 수(표식) 평균 2.4 · 상대 수 평균 29.1 · 새끼 10라운드 생존 80% · 30라운드 55% · 부모 10라운드 생존 75% · 30라운드 70% · 새끼 30라운드 안 1개 이상 먹음 25% · 30라운드 뒤 가족 길이 변화 0.8 · 30라운드 안 새끼가 죽은 원인: 박힘(상대 돌진) 5, 갇힘 1, 희생 1, 돌진 2
- 비교: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 84% · 적 머리가 7×7 시야 안 29% · 부모 길이 평균 5.1 · 우리 수(표식) 평균 2.7 · 상대 수 평균 23.7 · 새끼 10라운드 생존 83% · 30라운드 71% · 부모 10라운드 생존 84% · 30라운드 69% · 새끼 30라운드 안 1개 이상 먹음 53% · 30라운드 뒤 가족 길이 변화 3.2 · 30라운드 안 새끼가 죽은 원인: 박힘(상대 돌진) 3, 돌진 2, 갇힘 9, 희생 3
- 상대별: proxy4_elim 11회 45% · proxy4_king 3회 33% · proxy4_swarm 6회 83%
- 지도별: Devil 14회 50% · Queen Of Spades 4회 75% · Schooltime 2회 50%
- 국면별: r0-99 2회 50% · r100-249 3회 33% · r250-349 9회 67% · r350-449 6회 50%

실패 사례 (9건 중 9건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:A:1 · r201 · 드래곤 #81 L4: 우리 3마리 · 상대 45마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r212 박힘(상대 돌진), 상대 길이 3, 부모 10라운드 생존 · 표식 map=Devil/a
- proxy4_elim · Devil · 게임 exp/stack9-a-px4:proxy4_elim:devil:A:1 · r219 · 드래곤 #166 L4: 우리 3마리 · 상대 43마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r223 박힘(상대 돌진), 상대 길이 3, 부모 10라운드 죽음 · 표식 map=Devil/a
- proxy4_elim · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_elim:queen_of_spades:A:1 · r314 · 드래곤 #95 L4: 우리 2마리 · 상대 18마리 · 새끼 L2 → 새끼 죽음 r317 박힘(상대 돌진), 상대 길이 3, 부모 10라운드 생존 · 표식 map=Queen_Of_Spades/a
- proxy4_elim · Schooltime · 게임 exp/stack9-a-px4:proxy4_elim:schooltime:B:1 · r279 · 드래곤 #191 L4: 우리 3마리 · 상대 63마리 · 새끼 L2 → 새끼 죽음 r292 박힘(상대 돌진), 상대 길이 3, 부모 10라운드 죽음 · 표식 map=Schooltime/a
- proxy4_swarm · Devil · 게임 exp/stack9-b-px4:proxy4_swarm:devil_b:B:2 · r444 · 드래곤 #449 L4: 우리 2마리 · 상대 15마리 · 새끼 L2 → 새끼 죽음 r461 박힘(상대 돌진), 상대 길이 4, 부모 10라운드 생존 · 표식 map=Devil/b
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:B:1 · r439 · 드래곤 #555 L4: 우리 3마리 · 상대 7마리 · 새끼 L2 → 새끼 죽음 r439 갇힘, 상대 길이 2, 부모 10라운드 생존 (설계 밖: 상대 < 8마리) · 표식 map=Devil/a
- proxy4_elim · Devil · 게임 exp/stack9-a-px4:proxy4_elim:devil:B:1 · r374 · 드래곤 #486 L4: 우리 2마리 · 상대 9마리 · 새끼 L2 → 새끼 죽음 r386 희생, 부모 10라운드 생존 · 표식 map=Devil/a
- proxy4_elim · Devil · 게임 exp/stack9-b-px4:proxy4_elim:devil_b:B:2 · r99 · 드래곤 #7 L4: 우리 3마리 · 상대 31마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r101 돌진, 상대 길이 3, 부모 10라운드 생존 · 표식 map=Devil/b
- proxy4_elim · Devil · 게임 exp/stack9-b-px4:proxy4_elim:devil_b:B:2 · r295 · 드래곤 #7 L4: 우리 1마리 · 상대 45마리 · 새끼 L2 → 새끼 죽음 r315 돌진, 상대 길이 7, 부모 10라운드 죽음 · 표식 map=Devil/b

## 왕 길이 상한 분열 (split kcap, stack7)

- 이번: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 80% · 부모 길이 평균 11 · 우리 수(표식) 평균 4.6 · 상대 수 평균 20.2 · 새끼 10라운드 생존 100% · 30라운드 60% · 부모 10라운드 생존 20% · 30라운드 0% · 새끼 30라운드 안 1개 이상 먹음 80% · 30라운드 뒤 가족 길이 변화 -1.8 · 30라운드 안 새끼가 죽은 원인: 갇힘 1, 박힘(상대 돌진) 1
- 비교: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 50% · 부모 길이 평균 8 · 우리 수(표식) 평균 4 · 상대 수 평균 7 · 새끼 10라운드 생존 100% · 30라운드 50% · 부모 10라운드 생존 50% · 30라운드 0% · 새끼 30라운드 안 1개 이상 먹음 50% · 30라운드 뒤 가족 길이 변화 -1 · 30라운드 안 새끼가 죽은 원인: 박힘(상대 돌진) 1
- 상대별: proxy4_elim 1회 100% · proxy4_king 1회 100% · proxy4_swarm 3회 100%
- 지도별: Default 2회 100% · Queen Of Spades 2회 100% · Trophy 1회 100%
- 국면별: r0-99 1회 100% · r100-249 4회 100%

## 지도·판본 인식 (map=, cand-mapid; 판 단위)

- 이번: 판본을 기보로 가릴 수 있는 판 120/120 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 95%, 그중 정답 100% · 프로세스 11728: 표식 없음 7, 결정 11689 (정답 100%, 틀림 0), 가족만 32, 모름 0, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 305라운드
- 비교: 판본을 기보로 가릴 수 있는 판 120/120 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 95%, 그중 정답 100% · 프로세스 10400: 표식 없음 6, 결정 10366 (정답 100%, 틀림 0), 가족만 28, 모름 0, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 267라운드
- 상대별: proxy4_elim 40회 100% · proxy4_king 40회 100% · proxy4_swarm 40회 100%
- 지도별: Autarky a 12회 100% · Default a 12회 100% · Devil a 6회 100% · Devil b 6회 100% · Portals a 12회 100% · Prisoners Dilemma a 6회 100% · Prisoners Dilemma b 6회 100% · Queen Of Spades a 6회 100% · Queen Of Spades b 6회 100% · Schooltime a 6회 100% · Schooltime b 6회 100% · Slithery Fight a 6회 100% · Slithery Fight b 6회 100% · Trauma a 12회 100% · Trophy a 12회 100%
- 국면별: r0-99 120회 100%

## Schooltime b 초반 분열 (split bsp, cand-mapid)

- 이번: 분열 100% · 설계 상황(그 판이 실제로 Schooltime b) 100% · 조각 10라운드 생존 98% (기준 ≥85%; 상위권 b 92%) · 10라운드 안 1개 이상 먹음 17% (상위권 b 20%) · 부모 10라운드 생존 100% · 조각 30라운드 생존 98%, 30라운드 안 1개 이상 먹음 32% · 30라운드 뒤 가족 길이 변화 4.7 · 30라운드 안 조각이 죽은 원인: 갇힘 1
- 비교: 분열 100% · 설계 상황(그 판이 실제로 Schooltime b) 100% · 조각 10라운드 생존 96% (기준 ≥85%; 상위권 b 92%) · 10라운드 안 1개 이상 먹음 11% (상위권 b 20%) · 부모 10라운드 생존 100% · 조각 30라운드 생존 95%, 30라운드 안 1개 이상 먹음 23% · 30라운드 뒤 가족 길이 변화 3.3 · 30라운드 안 조각이 죽은 원인: 박힘(상대 돌진) 1, 갇힘 2
- 상대별: proxy4_elim 19회 95% · proxy4_king 16회 100% · proxy4_swarm 18회 100%
- 지도별: Schooltime 53회 98%
- 국면별: r0-99 40회 100% · r100-249 13회 92%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_elim · Schooltime · 게임 exp/stack9-b-px4:proxy4_elim:schooltime_b:B:2 · r103 · 드래곤 #18 L4: 조각 L2 → 조각 죽음 r106 갇힘, 10·30라운드 안 먹은 진주 0·0

## 덮기 분열 (csplit, stack5)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 36% · 부모가 스스로 최장이라 믿음(k) 69% · 새끼 30라운드 안 자연 진주 ≥1 40% (500형 40% · 전멸형 39%; 기준 ≥45%) · 새끼 30라운드 생존 74% (500형 76% · 전멸형 73%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 84% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 갇힘 366, 박힘(상대 돌진) 78, 아군 머리 20, 돌진 21, 적 몸통 1
- 비교: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 34% · 부모가 스스로 최장이라 믿음(k) 67% · 새끼 30라운드 안 자연 진주 ≥1 39% (500형 38% · 전멸형 41%; 기준 ≥45%) · 새끼 30라운드 생존 77% (500형 78% · 전멸형 76%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 87% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 갇힘 305, 아군 머리 27, 박힘(상대 돌진) 85, 돌진 16, 희생 1
- 상대별: proxy4_elim 642회 40% · proxy4_king 683회 39% · proxy4_swarm 579회 39%
- 지도별: Autarky 233회 41% · Default 334회 41% · Devil 134회 25% · Portals 160회 45% · Prisoners Dilemma 44회 48% · Prisoners Dilemma (10) 7회 0% · Queen Of Spades 135회 36% · Schooltime 162회 43% · Slithery Fight 383회 34% · Trauma 202회 44% · Trophy 110회 51%
- 국면별: r0-99 875회 44% · r100-249 1029회 36%

실패 사례 (1151건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:B:1 · r50 · 드래곤 #7 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r1 · 드래곤 #0 L4: 새끼 L2, 적 머리 시야 안 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r5 · 드래곤 #4 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9-a-px4:proxy4_king:prisoners_dilemma:A:1 · r33 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r15 · 드래곤 #2 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r3 · 드래곤 #33 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trophy · 게임 exp/stack9-a-px4:proxy4_king:trophy:A:1 · r28 · 드래곤 #0 L5: 새끼 L2 → 새끼 죽음 r40 갇힘, 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0

## 샘 지킴 (F, stack5; 드래곤·샘 단위)

- 이번: 목표 2075개(표식 턴 21918) · 설계 상황 82% (실제 샘 100%, 우리 영토 100%, 처음에 다른 우리 머리 3걸음 안 없음 82%; 기준 ≥80%) · 3걸음 안 도착 59% · 도착 뒤 30라운드 그 무리 자연 진주 4782개 중 우리 91% · 상대 8% (합산 기준 ≥85%) · 처음 거리 평균 3.2
- 비교: 목표 2043개(표식 턴 21830) · 설계 상황 82% (실제 샘 100%, 우리 영토 100%, 처음에 다른 우리 머리 3걸음 안 없음 83%; 기준 ≥80%) · 3걸음 안 도착 60% · 도착 뒤 30라운드 그 무리 자연 진주 4711개 중 우리 90% · 상대 9% (합산 기준 ≥85%) · 처음 거리 평균 3.2
- 상대별: proxy4_elim 665회 90% · proxy4_king 716회 88% · proxy4_swarm 694회 86%
- 지도별: Autarky 47회 0% · Devil 138회 51% · Portals 1086회 99% · Prisoners Dilemma 61회 97% · Prisoners Dilemma (10) 13회 100% · Schooltime 16회 – · Slithery Fight 569회 54% · Trauma 145회 91%
- 국면별: r0-99 705회 79% · r100-249 833회 93% · r250-349 537회 94%

실패 사례 (119건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:A:1 · r23 · 드래곤 #2 L2: 샘 (14,8) 처음 거리 5 → r40 도착, 30라운드 무리 진주 6개 중 우리 0 · 상대 6
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r265 · 드래곤 #365 L11: 샘 (19,8) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r265 도착, 30라운드 무리 진주 4개 중 우리 2 · 상대 0
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r0 · 드래곤 #8 L5: 샘 (33,2) 처음 거리 0 → r0 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_swarm · Autarky · 게임 exp/stack9-a-px4:proxy4_swarm:autarky:B:1 · r93 · 드래곤 #67 L2: 샘 (34,16) 처음 거리 6 → r145 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_swarm · Devil · 게임 exp/stack9-a-px4:proxy4_swarm:devil:A:1 · r41 · 드래곤 #9 L4: 샘 (8,15) 처음 거리 0 → r41 도착, 30라운드 무리 진주 7개 중 우리 5 · 상대 2
- proxy4_swarm · Portals · 게임 exp/stack9-a-px4:proxy4_swarm:portals:A:1 · r317 · 드래곤 #436 L15: 샘 (27,0) 처음 거리 0 → r317 도착, 30라운드 무리 진주 5개 중 우리 2 · 상대 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_swarm:slithery_fight:B:1 · r0 · 드래곤 #9 L5: 샘 (29,24) 처음 거리 0 → r0 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_elim · Devil · 게임 exp/stack9-a-px4:proxy4_elim:devil:A:1 · r47 · 드래곤 #9 L2: 샘 (8,15) 처음 거리 4 → r47 도착, 30라운드 무리 진주 6개 중 우리 4 · 상대 2
- proxy4_elim · Portals · 게임 exp/stack9-a-px4:proxy4_elim:portals:A:1 · r324 · 드래곤 #453 L6: 샘 (19,0) 처음 거리 0 → r324 도착, 30라운드 무리 진주 4개 중 우리 0 · 상대 0
- proxy4_elim · Prisoners Dilemma · 게임 exp/stack9-a-px4:proxy4_elim:prisoners_dilemma:B:1 · r338 · 드래곤 #241 L11: 샘 (17,2) 처음 거리 0 → r338 도착, 30라운드 무리 진주 5개 중 우리 4 · 상대 0

## 영토 덮기 끌림 (cov, stack5)

- 이번: 턴 63738 · 20라운드 안 우리 영토 자연 진주 먹음 20%
- 상대별: proxy4_elim 21113회 20% · proxy4_king 22452회 20% · proxy4_swarm 20173회 19%
- 지도별: Autarky 5791회 29% · Default 9028회 12% · Devil 2861회 22% · Portals 3038회 37% · Prisoners Dilemma 1274회 8% · Prisoners Dilemma (10) 1989회 2% · Queen Of Spades 7508회 13% · Schooltime 13080회 23% · Slithery Fight 9141회 27% · Trauma 8195회 13% · Trophy 1833회 30%
- 국면별: r0-99 14716회 30% · r100-249 21690회 16% · r250-349 12653회 13% · r350-449 10053회 22% · r450+ 4626회 20%

실패 사례 (51061건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:B:1 · r0 · 드래곤 #5 L3
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r0 · 드래곤 #0 L4
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:A:1 · r19 · 드래곤 #2 L3
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r11 · 드래곤 #4 L4
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9-a-px4:proxy4_king:prisoners_dilemma:A:1 · r0 · 드래곤 #2 L3
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r12 · 드래곤 #0 L3
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r0 · 드래곤 #0 L4
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r0 · 드래곤 #6 L2
- proxy4_king · Trophy · 게임 exp/stack9-a-px4:proxy4_king:trophy:A:1 · r24 · 드래곤 #6 L2
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r0 · 드래곤 #0 L4

## 위협 모형 빈틈 (tg, stack4)

- 이번: 피함(tg) 56% · 위협 칸으로 감(tgx) 12590턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 98% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 98%) · 길이별 L2-5 28293 · L6-9 181 · L10+ 237
- 비교: 피함(tg) 57% · 위협 칸으로 감(tgx) 10538턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 98% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 98%) · 길이별 L2-5 24014 · L6-9 294 · L10+ 309
- 상대별: proxy4_elim 9153회 98% · proxy4_king 10112회 99% · proxy4_swarm 9446회 98%
- 지도별: Autarky 1281회 98% · Default 6447회 99% · Devil 2170회 98% · Portals 14회 100% · Prisoners Dilemma 40회 98% · Prisoners Dilemma (10) 769회 99% · Queen Of Spades 2922회 99% · Schooltime 6199회 99% · Slithery Fight 6204회 99% · Trauma 607회 98% · Trophy 2058회 97%
- 국면별: r0-99 4627회 98% · r100-249 11829회 98% · r250-349 6458회 98% · r350-449 4554회 99% · r450+ 1243회 99%

실패 사례 (461건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:B:1 · r84 · 드래곤 #3 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r84 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r203 · 드래곤 #51 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 3) → 박힘 r204 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:A:1 · r41 · 드래곤 #2 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r43 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r315 · 드래곤 #32 L2: 피함(tg), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r315 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r126 · 드래곤 #8 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r128 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r168 · 드래곤 #281 L2: 피함(tg), 적 머리 경로 5칸 · 맨해튼 4칸(길이 2) → 박힘 r170 박힘(상대 돌진), 상대 길이 5
- proxy4_king · Trophy · 게임 exp/stack9-a-px4:proxy4_king:trophy:A:1 · r112 · 드래곤 #14 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r114 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r229 · 드래곤 #118 L2: 피함(tg), 적 머리 경로 4칸 · 맨해튼 4칸(길이 2) → 박힘 r231 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Autarky · 게임 exp/stack9-a-px4:proxy4_swarm:autarky:B:1 · r190 · 드래곤 #67 L2: 피함(tg), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r192 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack9-a-px4:proxy4_swarm:default:A:1 · r179 · 드래곤 #2 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 3) → 박힘 r181 박힘(상대 돌진), 상대 길이 3

## 모이기 시작 제한 (gx, stack4; 드래곤 단위)

- 이번: 드래곤 294 (표식 턴 1899) · 몸(자손 포함) 끝까지 91% (기준 ≥80%) · 드래곤 자체 끝까지 생존 60% (참고) · 뒤에 희생 먹이기(feed)로 끝남 28
- 비교: 드래곤 171 (표식 턴 940) · 몸(자손 포함) 끝까지 96% (기준 ≥80%) · 드래곤 자체 끝까지 생존 49% (참고) · 뒤에 희생 먹이기(feed)로 끝남 11
- 상대별: proxy4_elim 90회 90% · proxy4_king 112회 88% · proxy4_swarm 92회 97%
- 지도별: Autarky 87회 98% · Default 25회 80% · Devil 15회 80% · Portals 49회 94% · Prisoners Dilemma 4회 100% · Prisoners Dilemma (10) 13회 100% · Queen Of Spades 10회 80% · Schooltime 41회 93% · Slithery Fight 29회 90% · Trauma 21회 81%
- 국면별: r450+ 294회 91%

실패 사례 (25건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r490 · 드래곤 #189 L4: gx 2턴 (r490–r491) → 죽음 r492 희생
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r488 · 드래곤 #657 L5: gx 3턴 (r488–r490) → 죽음 r491 희생
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r458 · 드래곤 #390 L4: gx 1턴 (r458–r458) → 죽음 r459 희생
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r490 · 드래곤 #255 L5: gx 1턴 (r490–r490) → 죽음 r493 희생
- proxy4_swarm · Trauma · 게임 exp/stack9-a-px4:proxy4_swarm:trauma:B:1 · r486 · 드래곤 #238 L4: gx 1턴 (r486–r486) → 죽음 r493 희생
- proxy4_king · Autarky · 게임 exp/stack9-b-px4:proxy4_king:autarky:B:2 · r489 · 드래곤 #409 L7: gx 9턴 (r489–r497) → 죽음 r498 희생
- proxy4_king · Queen Of Spades · 게임 exp/stack9-b-px4:proxy4_king:queen_of_spades_b:B:2 · r481 · 드래곤 #157 L4: gx 7턴 (r481–r487) → 죽음 r488 희생
- proxy4_swarm · Default · 게임 exp/stack9-b-px4:proxy4_swarm:default:B:2 · r486 · 드래곤 #243 L4: gx 3턴 (r486–r488) → 죽음 r490 희생
- proxy4_swarm · Slithery Fight · 게임 exp/stack9-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r481 · 드래곤 #906 L4: gx 1턴 (r481–r481) → 죽음 r482 희생
- proxy4_elim · Autarky · 게임 exp/stack9-b-px4:proxy4_elim:autarky:A:2 · r490 · 드래곤 #344 L4: gx 1턴 (r490–r490) → 죽음 r491 희생

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 914개 중 우리 팀 98% (지목한 아군 58%) · 상대 1% · 지목 아군 끝까지 생존 53% (그 뒤 죽은 원인: 돌진 4, 갇힘 161, 희생 108, 박힘(상대 돌진) 1, 아군 머리 11) · 지목 아군의 몸(자손 포함)이 끝까지 삶 88% · 최종 왕 43% (최종 왕이 지목 아군의 자손 65%)
- 비교: 실행 100% · 떨군 진주 451개 중 우리 팀 96% (지목한 아군 64%) · 상대 3% · 지목 아군 끝까지 생존 33% (그 뒤 죽은 원인: 희생 56, 갇힘 117, 아군 머리 4, 박힘(상대 돌진) 13, 돌진 3) · 지목 아군의 몸(자손 포함)이 끝까지 삶 80% · 최종 왕 29% (최종 왕이 지목 아군의 자손 53%)
- 상대별: proxy4_elim 194회 98% · proxy4_king 250회 99% · proxy4_swarm 162회 98%
- 지도별: Autarky 238회 100% · Default 9회 78% · Devil 5회 100% · Portals 200회 100% · Prisoners Dilemma 11회 100% · Queen Of Spades 7회 100% · Schooltime 11회 100% · Slithery Fight 114회 97% · Trauma 11회 82%
- 국면별: r250-349 164회 99% · r350-449 358회 99% · r450+ 84회 94%

실패 사례 (9건 중 9건, 기보 확인용):
- proxy4_swarm · Portals · 게임 exp/stack9-a-px4:proxy4_swarm:portals:A:1 · r475 · 드래곤 #547 L2: #545(L20)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_swarm:slithery_fight:B:1 · r309 · 드래곤 #309 L2: #25(L23)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 1
- proxy4_elim · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_elim:slithery_fight:B:1 · r463 · 드래곤 #645 L2: #1010(L31)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 1
- proxy4_king · Autarky · 게임 exp/stack9-b-px4:proxy4_king:autarky:A:2 · r474 · 드래곤 #485 L4: #457(L41)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Slithery Fight · 게임 exp/stack9-b-px4:proxy4_king:slithery_fight_b:A:2 · r335 · 드래곤 #478 L4: #648(L8)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1; 지목 아군 r365 갇힘에 사망
- proxy4_swarm · Trauma · 게임 exp/stack9-b-px4:proxy4_swarm:trauma:A:2 · r449 · 드래곤 #263 L2: #243(L8)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 1; 지목 아군 r480 갇힘에 사망
- proxy4_elim · Default · 게임 exp/stack9-b-px4:proxy4_elim:default:B:2 · r448 · 드래곤 #106 L3: #200(L9)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1
- proxy4_swarm · Trauma · 게임 exp/stack9-b-px4:proxy4_swarm:trauma:A:2 · r454 · 드래곤 #283 L2: #243(L8)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0; 지목 아군 r480 갇힘에 사망
- proxy4_elim · Default · 게임 exp/stack9-b-px4:proxy4_elim:default:B:2 · r479 · 드래곤 #181 L3: #200(L14)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 88% · 조각 30라운드 생존 42% · 30라운드 안 1개 이상 먹음 70% (살아서 먹음 27%) · 평생 먹은 진주 평균 2.7 · 나중에 아군을 먹임 47% (conv 24, feed 4, 분열 뒤 평균 45.1라운드) · 끝까지 생존 0% · 30라운드 안 죽은 원인: 갇힘 21, 희생 12, 돌진 1, 아군 머리 1
- 비교: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 100% · 조각 30라운드 생존 56% · 30라운드 안 1개 이상 먹음 63% (살아서 먹음 38%) · 평생 먹은 진주 평균 4 · 나중에 아군을 먹임 47% (conv 5, feed 10, 분열 뒤 평균 32.2라운드) · 끝까지 생존 25% · 30라운드 안 죽은 원인: 희생 9, 돌진 1, 갇힘 4
- 상대별: proxy4_elim 20회 60% · proxy4_king 21회 57% · proxy4_swarm 19회 58%
- 지도별: Autarky 1회 100% · Portals 37회 59% · Queen Of Spades 3회 67% · Slithery Fight 18회 56% · Trauma 1회 0%
- 국면별: r250-349 28회 57% · r350-449 32회 59%

실패 사례 (25건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r255 · 드래곤 #370 L9: 조각 L2 → 조각 죽음 r275 갇힘, 30라운드 안 먹은 진주 1
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r419 · 드래곤 #104 L8: 조각 L2 → 조각 죽음 r424 갇힘, 30라운드 안 먹은 진주 1
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:B:1 · r267 · 드래곤 #565 L8: 조각 L2 → 조각 죽음 r290 갇힘, 30라운드 안 먹은 진주 0
- proxy4_swarm · Portals · 게임 exp/stack9-a-px4:proxy4_swarm:portals:B:1 · r360 · 드래곤 #482 L7: 조각 L2 → 조각 죽음 r363 갇힘, 상대 길이 16, 30라운드 안 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_swarm:slithery_fight:B:1 · r344 · 드래곤 #156 L11: 조각 L2 → 조각 죽음 r349 갇힘, 상대 길이 29, 30라운드 안 먹은 진주 1
- proxy4_elim · Portals · 게임 exp/stack9-a-px4:proxy4_elim:portals:B:1 · r346 · 드래곤 #466 L9: 조각 L2 → 조각 죽음 r368 갇힘, 30라운드 안 먹은 진주 1
- proxy4_elim · Trauma · 게임 exp/stack9-a-px4:proxy4_elim:trauma:A:1 · r364 · 드래곤 #176 L7: 조각 L2 → 조각 죽음 r373 갇힘, 30라운드 안 먹은 진주 6 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_elim · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_elim:slithery_fight:B:1 · r284 · 드래곤 #535 L9: 조각 L2 → 조각 죽음 r310 갇힘, 30라운드 안 먹은 진주 7
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:B:1 · r350 · 드래곤 #561 L9: 조각 L2 → 조각 죽음 r350 갇힘, 30라운드 안 먹은 진주 0
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:B:1 · r355 · 드래곤 #559 L8: 조각 L2 → 조각 죽음 r367 갇힘, 30라운드 안 먹은 진주 6

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 6065개 (표식 턴 15285, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 91% (자연 진주 2, 이미 없음 525) · 사망 진주 5538개 중 우리가 먹음 82% · 상대 17% · 아무도 안 먹음 2% · 표적으로 삼은 드래곤이 먹음 67% · 우리가 먹기까지 평균 3라운드 · 상대 머리가 같거나 더 가까웠던 1585개: 우리 53% 대 상대 45% · 박치기 진주 876개: 우리 55% 대 상대 45% · 우리 팀 사망 진주 82% · 사망 뒤 첫 표적까지 평균 1.2라운드
- 비교: 표적 진주 4377개 (표식 턴 10828, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 92% (자연 진주 3, 이미 없음 366) · 사망 진주 4008개 중 우리가 먹음 81% · 상대 18% · 아무도 안 먹음 1% · 표적으로 삼은 드래곤이 먹음 68% · 우리가 먹기까지 평균 3.4라운드 · 상대 머리가 같거나 더 가까웠던 1237개: 우리 54% 대 상대 45% · 박치기 진주 665개: 우리 53% 대 상대 47% · 우리 팀 사망 진주 82% · 사망 뒤 첫 표적까지 평균 1.3라운드
- 상대별: proxy4_elim 1963회 82% · proxy4_king 2329회 82% · proxy4_swarm 1773회 81%
- 지도별: Autarky 901회 99% · Default 818회 74% · Devil 392회 60% · Portals 1408회 98% · Prisoners Dilemma 176회 83% · Prisoners Dilemma (10) 34회 32% · Queen Of Spades 304회 57% · Schooltime 446회 62% · Slithery Fight 1086회 77% · Trauma 364회 82% · Trophy 136회 52%
- 국면별: r0-99 519회 68% · r100-249 1407회 76% · r250-349 1460회 84% · r350-449 1897회 87% · r450+ 782회 82%

실패 사례 (1023건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r140 · 드래곤 #32 L2: 진주 (24,8), 우리 머리 5칸 · 상대 머리 4칸, 우리 팀 사망 0라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 3턴
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:A:1 · r67 · 드래곤 #4 L4: 진주 (10,11), 우리 머리 2칸 · 상대 머리 1칸, 박치기 1라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 3턴
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r177 · 드래곤 #181 L4: 진주 (18,11), 우리 머리 7칸 · 상대 머리 1칸, 상대 사망 4라운드 뒤 → 상대가 먹음 (1라운드 뒤), 표식 2턴
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9-a-px4:proxy4_king:prisoners_dilemma:A:1 · r363 · 드래곤 #291 L4: 진주 (16,11), 우리 머리 6칸 · 상대 머리 1칸, 상대 사망 2라운드 뒤 → 상대가 먹음 (1라운드 뒤), 표식 1턴
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r57 · 드래곤 #2 L3: 진주 (8,33), 우리 머리 4칸 · 상대 머리 3칸, 박치기 1라운드 뒤 → 상대가 먹음 (6라운드 뒤), 표식 1턴
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r128 · 드래곤 #47 L2: 진주 (50,1), 우리 머리 3칸 · 상대 머리 4칸, 박치기 0라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 3턴
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r4 · 드래곤 #26 L2: 진주 (33,5), 우리 머리 5칸 · 상대 머리 10칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (140라운드 뒤), 표식 3턴
- proxy4_king · Trophy · 게임 exp/stack9-a-px4:proxy4_king:trophy:A:1 · r77 · 드래곤 #45 L2: 진주 (1,11), 우리 머리 5칸 · 상대 머리 2칸, 우리 팀 사망 0라운드 뒤 → 상대가 먹음 (8라운드 뒤), 표식 1턴
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r485 · 드래곤 #295 L2: 진주 (3,17), 우리 머리 4칸 · 상대 머리 9칸, 우리 팀 사망 0라운드 뒤 → 아무도 안 먹음, 표식 1턴
- proxy4_swarm · Default · 게임 exp/stack9-a-px4:proxy4_swarm:default:A:1 · r180 · 드래곤 #33 L2: 진주 (2,30), 우리 머리 4칸 · 상대 머리 2칸, 박치기 0라운드 뒤 → 상대가 먹음 (2라운드 뒤), 표식 3턴

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 2382 (그중 통로 고리 세대 1841, 판정에서 뺌) · 고리 밖 541: 처음 거리 평균 10.2 → 최소 6.5 · 3칸 안까지 감 28% · 희생까지 함 42% · 가는 길에 죽음 30% · 끝까지 생존 28%
- 비교: 모이기 드래곤 1833 (그중 통로 고리 세대 1384, 판정에서 뺌) · 고리 밖 449: 처음 거리 평균 10.6 → 최소 5.8 · 3칸 안까지 감 37% · 희생까지 함 51% · 가는 길에 죽음 24% · 끝까지 생존 25%
- 상대별: proxy4_elim 752회 70% · proxy4_king 899회 70% · proxy4_swarm 731회 72%
- 지도별: Autarky 965회 63% · Default 37회 78% · Devil 69회 82% · Portals 630회 84% · Prisoners Dilemma 334회 76% · Prisoners Dilemma (10) 105회 0% · Queen Of Spades 15회 43% · Schooltime 77회 61% · Slithery Fight 88회 50% · Trauma 62회 46%
- 국면별: r250-349 269회 72% · r350-449 1601회 72% · r450+ 512회 67%

실패 사례 (229건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:B:1 · r349 · 드래곤 #336 L4: 왕까지 거리 6 → 최소 6 (1턴), 가는 길에 죽음 r353 희생
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r432 · 드래곤 #202 L4: 왕까지 거리 17 → 최소 9 (13턴)
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:A:1 · r469 · 드래곤 #635 L9: 왕까지 거리 6 → 최소 6 (1턴)
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r341 · 드래곤 #537 L4: 왕까지 거리 11 → 최소 11 (2턴), 가는 길에 죽음 r343 희생
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9-a-px4:proxy4_king:prisoners_dilemma:A:1 · r340 · 드래곤 #34 L4: 왕까지 거리 14 → 최소 6 (16턴), 가는 길에 죽음 r364 갇힘
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r387 · 드래곤 #104 L4: 왕까지 거리 4 → 최소 4 (75턴)
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r367 · 드래곤 #237 L4: 왕까지 거리 24 → 최소 14 (77턴)
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r379 · 드래곤 #446 L4: 왕까지 거리 7 → 최소 4 (29턴), 가는 길에 죽음 r411 아군 머리, 상대 길이 2
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r351 · 드래곤 #249 L5: 왕까지 거리 6 → 최소 6 (1턴), 가는 길에 죽음 r369 갇힘
- proxy4_swarm · Autarky · 게임 exp/stack9-a-px4:proxy4_swarm:autarky:A:1 · r383 · 드래곤 #323 L4: 왕까지 거리 11 → 최소 4 (30턴), 가는 길에 죽음 r485 갇힘

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 1194개 중 우리 팀 82% (지목한 아군 49%) · 상대 5% · 지목 아군 끝까지 생존 63% (그 뒤 죽은 원인: 희생 128, 갇힘 62, 박힘(상대 돌진) 9, 돌진 6, 아군 머리 3) · 지목 아군의 몸(자손 포함)이 끝까지 삶 78% · 최종 왕 27% (최종 왕이 지목 아군의 자손 34%)
- 비교: 실행 100% · 떨군 진주 987개 중 우리 팀 86% (지목한 아군 58%) · 상대 6% · 지목 아군 끝까지 생존 65% (그 뒤 죽은 원인: 희생 56, 돌진 6, 아군 머리 3, 갇힘 37, 박힘(상대 돌진) 12) · 지목 아군의 몸(자손 포함)이 끝까지 삶 86% · 최종 왕 50% (최종 왕이 지목 아군의 자손 60%)
- 상대별: proxy4_elim 191회 82% · proxy4_king 190회 82% · proxy4_swarm 177회 82%
- 지도별: Autarky 125회 98% · Default 26회 77% · Devil 37회 81% · Portals 74회 92% · Prisoners Dilemma 31회 94% · Queen Of Spades 18회 72% · Schooltime 56회 73% · Slithery Fight 74회 66% · Trauma 117회 74%
- 국면별: r250-349 13회 92% · r350-449 149회 92% · r450+ 396회 78%

실패 사례 (99건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:B:1 · r478 · 드래곤 #486 L6: #11(L38)에게 희생 → 진주 3개 중 우리 1, 지목 아군 1, 상대 0
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r492 · 드래곤 #189 L5: #211(L9)에게 희생 → 진주 3개 중 우리 1, 지목 아군 1, 상대 0
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:B:1 · r489 · 드래곤 #638 L5: #649(L23)에게 희생 → 진주 3개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9-a-px4:proxy4_king:prisoners_dilemma:A:1 · r487 · 드래곤 #331 L5: #149(L12)에게 희생 → 진주 3개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r486 · 드래곤 #130 L2: #156(L3)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r440 · 드래곤 #413 L4: #21(L6)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 1
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r476 · 드래곤 #927 L4: #684(L31)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r486 · 드래곤 #6 L3: #150(L2)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0; 지목 아군 r487 희생에 사망
- proxy4_swarm · Devil · 게임 exp/stack9-a-px4:proxy4_swarm:devil:B:1 · r435 · 드래곤 #478 L4: #505(L5)에게 희생 → 진주 2개 중 우리 1, 지목 아군 0, 상대 1
- proxy4_swarm · Portals · 게임 exp/stack9-a-px4:proxy4_swarm:portals:B:1 · r436 · 드래곤 #528 L6: #536(L21)에게 희생 → 진주 3개 중 우리 1, 지목 아군 0, 상대 0; 지목 아군 r465 희생에 사망

## 막다른 길 한입 (pocket-eat)

- 이번: 한입 100% · 2턴 안 분열 99% · 30라운드 뒤 가족 길이 변화 0.2 (줄지 않음 100%)
- 비교: 한입 100% · 2턴 안 분열 98% · 30라운드 뒤 가족 길이 변화 0.1 (줄지 않음 99%)
- 상대별: proxy4_elim 341회 99% · proxy4_king 340회 98% · proxy4_swarm 337회 99%
- 지도별: Devil 3회 33% · Portals 13회 62% · Prisoners Dilemma (10) 1002회 99%
- 국면별: r0-99 204회 100% · r100-249 303회 99% · r250-349 208회 99% · r350-449 200회 100% · r450+ 103회 94%

실패 사례 (13건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:B:1 · r235 · 드래곤 #368 L4: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 5
- proxy4_swarm · Devil · 게임 exp/stack9-a-px4:proxy4_swarm:devil:B:1 · r125 · 드래곤 #91 L4: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 3
- proxy4_elim · Portals · 게임 exp/stack9-a-px4:proxy4_elim:portals:A:1 · r270 · 드래곤 #370 L18: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 5
- proxy4_king · Devil · 게임 exp/stack9-b-px4:proxy4_king:devil_b:B:2 · r338 · 드래곤 #320 L4: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 0
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack9-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r499 · 드래곤 #363 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/stack9-b-px4:proxy4_swarm:prisoners_dilemma_10:B:2 · r499 · 드래곤 #342 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_elim · Prisoners Dilemma (10) · 게임 exp/stack9-b-px4:proxy4_elim:prisoners_dilemma_10:A:2 · r499 · 드래곤 #308 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_elim · Portals · 게임 exp/stack9-a-px4:proxy4_elim:portals:B:1 · r201 · 드래곤 #248 L10: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 2
- proxy4_king · Portals · 게임 exp/stack9-b-px4:proxy4_king:portals:A:2 · r360 · 드래곤 #521 L13: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 4
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack9-b-px4:proxy4_king:prisoners_dilemma_10:B:2 · r499 · 드래곤 #355 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 21% · 30라운드 뒤 가족 길이 변화 8.4
- 비교: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 21% · 30라운드 뒤 가족 길이 변화 8.2
- 상대별: proxy4_elim 2579회 98% · proxy4_king 2704회 98% · proxy4_swarm 2673회 99%
- 지도별: Autarky 3045회 100% · Default 62회 92% · Devil 138회 87% · Portals 1796회 95% · Prisoners Dilemma 1445회 100% · Prisoners Dilemma (10) 996회 100% · Queen Of Spades 50회 88% · Schooltime 36회 97% · Slithery Fight 186회 97% · Trauma 194회 91% · Trophy 8회 100%
- 국면별: r0-99 1417회 100% · r100-249 2298회 98% · r250-349 1825회 97% · r350-449 1679회 98% · r450+ 737회 98%

실패 사례 (156건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r230 · 드래곤 #101 L5: 새끼 L3 → 새끼 죽음 r235 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:B:1 · r106 · 드래곤 #93 L4: 새끼 L2 → 새끼 죽음 r111 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r273 · 드래곤 #405 L11: 새끼 L9 → 새끼 죽음 r279 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -11
- proxy4_king · Prisoners Dilemma · 게임 exp/stack9-a-px4:proxy4_king:prisoners_dilemma:A:1 · r473 · 드래곤 #291 L4: 새끼 L2 → 새끼 죽음 r473 갇힘, 상대 길이 7, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Devil · 게임 exp/stack9-a-px4:proxy4_swarm:devil:A:1 · r49 · 드래곤 #29 L4: 새끼 L2 → 새끼 죽음 r53 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Portals · 게임 exp/stack9-a-px4:proxy4_swarm:portals:A:1 · r88 · 드래곤 #31 L4: 새끼 L2 → 새끼 죽음 r92 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Schooltime · 게임 exp/stack9-a-px4:proxy4_swarm:schooltime:A:1 · r479 · 드래곤 #324 L6: 새끼 L4 → 새끼 죽음 r486 희생, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -6
- proxy4_swarm · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_swarm:slithery_fight:B:1 · r161 · 드래곤 #16 L30: 새끼 L28 → 새끼 죽음 r164 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -30
- proxy4_swarm · Trauma · 게임 exp/stack9-a-px4:proxy4_swarm:trauma:B:1 · r248 · 드래곤 #125 L7: 새끼 L5 → 새끼 죽음 r249 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7
- proxy4_elim · Autarky · 게임 exp/stack9-a-px4:proxy4_elim:autarky:B:1 · r414 · 드래곤 #363 L4: 새끼 L2 → 새끼 죽음 r418 아군 머리, 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 84% · 그 밖(진짜로 갇힘) 1404회
- 비교: 탈출 분열 뒤 남은 조각(고리의 일부) 88% · 그 밖(진짜로 갇힘) 938회
- 상대별: proxy4_elim 2777회 – · proxy4_king 2948회 – · proxy4_swarm 2832회 –
- 지도별: Autarky 3154회 – · Default 253회 – · Devil 130회 – · Portals 1636회 – · Prisoners Dilemma 1476회 – · Prisoners Dilemma (10) 1000회 – · Queen Of Spades 85회 – · Schooltime 78회 – · Slithery Fight 376회 – · Trauma 334회 – · Trophy 35회 –
- 국면별: r0-99 1504회 – · r100-249 2599회 – · r250-349 1963회 – · r350-449 1780회 – · r450+ 711회 –

## 탈출 질주 3칸 (esc)

- 이번: 질주 100% · 짧은 적 머리 4칸 안 84% · 몸 생존 5라운드 98% · 10라운드 98% (드래곤 자체 88%) · 10라운드 길이 변화 -3.2
- 비교: 질주 100% · 짧은 적 머리 4칸 안 84% · 몸 생존 5라운드 97% · 10라운드 93% (드래곤 자체 86%) · 10라운드 길이 변화 -3.7
- 상대별: proxy4_elim 38회 95% · proxy4_king 53회 100% · proxy4_swarm 39회 97%
- 지도별: Default 22회 100% · Devil 9회 89% · Queen Of Spades 11회 91% · Schooltime 25회 100% · Slithery Fight 55회 98% · Trauma 4회 100% · Trophy 4회 100%
- 국면별: r0-99 13회 100% · r100-249 20회 95% · r250-349 20회 100% · r350-449 11회 100% · r450+ 66회 97%

실패 사례 (3건 중 3건, 기보 확인용):
- proxy4_swarm · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_swarm:queen_of_spades:A:1 · r475 · 드래곤 #89 L6: 질주 2칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r476 박힘(상대 돌진), 상대 길이 4
- proxy4_elim · Devil · 게임 exp/stack9-b-px4:proxy4_elim:devil_b:A:2 · r491 · 드래곤 #477 L7: 질주 3칸 (가장 가까운 짧은 적 머리 2칸) → 죽음 r492 희생
- proxy4_elim · Slithery Fight · 게임 exp/stack9-b-px4:proxy4_elim:slithery_fight_b:B:2 · r167 · 드래곤 #397 L6: 질주 3칸 (가장 가까운 짧은 적 머리 1칸) → 죽음 r168 박힘(상대 돌진), 상대 길이 3

## 위협 피하기 2칸 질주

- 이번: 질주 100% · 몸 10라운드 생존 94% (드래곤 자체 89%)
- 비교: 질주 100% · 몸 10라운드 생존 94% (드래곤 자체 90%)
- 상대별: proxy4_elim 427회 94% · proxy4_king 452회 94% · proxy4_swarm 365회 94%
- 지도별: Autarky 53회 96% · Default 224회 92% · Devil 99회 88% · Portals 2회 100% · Prisoners Dilemma 3회 100% · Prisoners Dilemma (10) 6회 100% · Queen Of Spades 158회 95% · Schooltime 277회 95% · Slithery Fight 317회 95% · Trauma 33회 94% · Trophy 72회 92%
- 국면별: r0-99 255회 95% · r100-249 432회 93% · r250-349 249회 93% · r350-449 234회 95% · r450+ 74회 96%

실패 사례 (78건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:A:1 · r28 · 드래곤 #2 L4: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r38 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r95 · 드래곤 #29 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 3) → 죽음 r102 갇힘
- proxy4_king · Devil · 게임 exp/stack9-a-px4:proxy4_king:devil:A:1 · r101 · 드래곤 #26 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r110 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:B:1 · r221 · 드래곤 #80 L4: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r222 갇힘
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r210 · 드래곤 #128 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 7) → 죽음 r213 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r222 · 드래곤 #302 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 5) → 죽음 r225 갇힘, 상대 길이 2
- proxy4_king · Trophy · 게임 exp/stack9-a-px4:proxy4_king:trophy:A:1 · r93 · 드래곤 #45 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r96 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r378 · 드래곤 #38 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r388 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Default · 게임 exp/stack9-a-px4:proxy4_swarm:default:A:1 · r322 · 드래곤 #18 L3: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 3) → 죽음 r322 아군 머리, 상대 길이 2
- proxy4_swarm · Devil · 게임 exp/stack9-a-px4:proxy4_swarm:devil:A:1 · r65 · 드래곤 #9 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r71 박힘(상대 돌진), 상대 길이 2

## 포털 통과 (전체; PORTAL?=미탐색 출구)

- 이번: 미탐색 출구 2348회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 94% (드래곤 자체 79%) · 10라운드 90% · 10라운드 안 먹은 진주 0.8
- 비교: 미탐색 출구 2209회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 94% (드래곤 자체 80%) · 10라운드 89% · 10라운드 안 먹은 진주 0.9
- 상대별: proxy4_elim 1647회 93% · proxy4_king 2205회 95% · proxy4_swarm 1739회 94%
- 지도별: Autarky 956회 95% · Default 1182회 94% · Portals 2250회 94% · Prisoners Dilemma 72회 99% · Prisoners Dilemma (10) 39회 100% · Queen Of Spades 128회 78% · Schooltime 193회 93% · Slithery Fight 326회 93% · Trauma 440회 95% · Trophy 5회 80%
- 국면별: r0-99 673회 95% · r100-249 2001회 95% · r250-349 1690회 94% · r350-449 1017회 93% · r450+ 210회 88%

실패 사례 (332건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:B:1 · r277 · 드래곤 #297 L2: 포털 → 죽음 r280 갇힘, 10라운드 안 진주 1
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r126 · 드래곤 #37 L3: 포털(미탐색 출구) → 죽음 r129 박힘(상대 돌진), 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Portals · 게임 exp/stack9-a-px4:proxy4_king:portals:A:1 · r42 · 드래곤 #16 L2: 포털(미탐색 출구) → 죽음 r42 아군 머리, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r50 · 드래곤 #12 L2: 포털 → 죽음 r53 갇힘, 10라운드 안 진주 0
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r287 · 드래곤 #7 L3: 포털(미탐색 출구) → 죽음 r287 돌진, 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r278 · 드래곤 #591 L3: 포털(미탐색 출구) → 죽음 r278 갇힘, 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Trauma · 게임 exp/stack9-a-px4:proxy4_king:trauma:A:1 · r299 · 드래곤 #71 L3: 포털 → 죽음 r299 돌진, 상대 길이 3, 10라운드 안 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack9-a-px4:proxy4_swarm:autarky:A:1 · r238 · 드래곤 #181 L3: 포털 → 죽음 r238 아군 머리, 상대 길이 16, 10라운드 안 진주 0
- proxy4_swarm · Default · 게임 exp/stack9-a-px4:proxy4_swarm:default:A:1 · r203 · 드래곤 #56 L3: 포털(미탐색 출구) → 죽음 r205 갇힘, 상대 길이 14, 10라운드 안 진주 0
- proxy4_swarm · Portals · 게임 exp/stack9-a-px4:proxy4_swarm:portals:A:1 · r42 · 드래곤 #17 L2: 포털(미탐색 출구) → 죽음 r42 아군 머리, 상대 길이 2, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 44, 경로 50) · 잡은 길이 ≥ 우리 100% · 두 몸의 진주 우리 267 대 상대 450
- 비교: 충돌 성사 100% (인접 39, 경로 57) · 잡은 길이 ≥ 우리 98% · 두 몸의 진주 우리 262 대 상대 478
- 상대별: proxy4_elim 16회 38% · proxy4_king 43회 35% · proxy4_swarm 35회 34%
- 지도별: Default 5회 60% · Devil 10회 50% · Prisoners Dilemma 1회 100% · Queen Of Spades 12회 17% · Schooltime 25회 16% · Slithery Fight 37회 43% · Trauma 4회 50%
- 국면별: r0-99 4회 0% · r100-249 10회 30% · r250-349 24회 25% · r350-449 37회 41% · r450+ 19회 47%

실패 사례 (61건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r306 · 드래곤 #18 L2: 돌진 경로 1칸 → 상대 L10 잡음, 진주 우리 0 대 상대 6
- proxy4_king · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_king:queen_of_spades:A:1 · r310 · 드래곤 #4 L3: 돌진 경로 2칸 → 상대 L7 잡음, 진주 우리 1 대 상대 5
- proxy4_king · Schooltime · 게임 exp/stack9-a-px4:proxy4_king:schooltime:A:1 · r379 · 드래곤 #346 L3: 돌진 경로 2칸 → 상대 L21 잡음, 진주 우리 0 대 상대 13
- proxy4_king · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_king:slithery_fight:A:1 · r94 · 드래곤 #12 L2: 돌진 경로 1칸 → 상대 L5 잡음, 진주 우리 0 대 상대 4
- proxy4_swarm · Devil · 게임 exp/stack9-a-px4:proxy4_swarm:devil:B:1 · r335 · 드래곤 #140 L2: 돌진 경로 1칸 → 상대 L14 잡음, 진주 우리 0 대 상대 8
- proxy4_swarm · Schooltime · 게임 exp/stack9-a-px4:proxy4_swarm:schooltime:A:1 · r332 · 드래곤 #181 L2: 돌진 경로 1칸 → 상대 L6 잡음, 진주 우리 0 대 상대 4
- proxy4_swarm · Slithery Fight · 게임 exp/stack9-a-px4:proxy4_swarm:slithery_fight:B:1 · r155 · 드래곤 #63 L3: 돌진 경로 1칸 → 상대 L8 잡음, 진주 우리 0 대 상대 6
- proxy4_swarm · Trauma · 게임 exp/stack9-a-px4:proxy4_swarm:trauma:B:1 · r348 · 드래곤 #1 L2: 돌진 경로 1칸 → 상대 L7 잡음, 진주 우리 0 대 상대 5
- proxy4_elim · Queen Of Spades · 게임 exp/stack9-a-px4:proxy4_elim:queen_of_spades:A:1 · r131 · 드래곤 #32 L2: 돌진 경로 1칸 → 상대 L5 잡음, 진주 우리 0 대 상대 4
- proxy4_elim · Schooltime · 게임 exp/stack9-a-px4:proxy4_elim:schooltime:B:1 · r363 · 드래곤 #122 L4: 돌진 경로 2칸 → 상대 L21 잡음, 진주 우리 0 대 상대 13

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 비교: 먹음 100%
- 상대별: proxy4_elim 97회 100% · proxy4_king 115회 100% · proxy4_swarm 112회 100%
- 지도별: Autarky 13회 100% · Default 45회 100% · Devil 20회 100% · Portals 48회 100% · Prisoners Dilemma 3회 100% · Queen Of Spades 31회 100% · Schooltime 45회 100% · Slithery Fight 84회 100% · Trauma 12회 100% · Trophy 23회 100%
- 국면별: r0-99 49회 100% · r100-249 93회 100% · r250-349 64회 100% · r350-449 99회 100% · r450+ 19회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 1% · 10라운드 생존 95%
- 비교: 그 턴 사망 0% · 10라운드 생존 92%
- 상대별: proxy4_elim 37회 – · proxy4_king 51회 – · proxy4_swarm 45회 –
- 지도별: Autarky 6회 – · Default 10회 – · Devil 10회 – · Queen Of Spades 17회 – · Schooltime 27회 – · Slithery Fight 55회 – · Trauma 4회 – · Trophy 4회 –
- 국면별: r0-99 27회 – · r100-249 47회 – · r250-349 22회 – · r350-449 29회 – · r450+ 8회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 비교: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 18회 – · proxy4_king 30회 – · proxy4_swarm 35회 –
- 지도별: Default 24회 – · Devil 24회 – · Queen Of Spades 4회 – · Schooltime 10회 – · Slithery Fight 9회 – · Trauma 9회 – · Trophy 3회 –
- 국면별: r0-99 10회 – · r100-249 43회 – · r250-349 11회 – · r350-449 11회 – · r450+ 8회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/stack9-a-px4+exp/stack9-b-px4` | 120 | 39 (0.33) | 49% | 0 (0.00) | 0 (0.00) | 9 | 27 | 2 | 1/3 (1.8) | 182 (1.52; 필사 44) | 40/163 (70) |
| · exp/stack9-a-px4 | 60 | 17 (0.28) | 53% | 0 (0.00) | 0 (0.00) | 3 | 12 | 1 | 1/2 (3.5) | 90 (1.50; 필사 27) | 21/94 (73.5) |
| · exp/stack9-b-px4 | 60 | 22 (0.37) | 45% | 0 (0.00) | 0 (0.00) | 6 | 15 | 1 | 0/1 (0) | 92 (1.53; 필사 17) | 19/69 (66.5) |
| 비교 `exp/stack8-a-px4+exp/stack8-b-px4` | 120 | 57 (0.47) | 54% | 0 (0.00) | 0 (0.00) | 8 | 48 | 1 | 2/6 (3.5) | 82 (0.68; 필사 137) | 37/108 (64.8) |
| · exp/stack8-a-px4 | 60 | 29 (0.48) | 45% | 0 (0.00) | 0 (0.00) | 4 | 25 | 0 | 0/1 (0) | 46 (0.77; 필사 65) | 23/65 (80.5) |
| · exp/stack8-b-px4 | 60 | 28 (0.47) | 64% | 0 (0.00) | 0 (0.00) | 4 | 23 | 1 | 2/5 (7) | 36 (0.60; 필사 72) | 14/43 (49) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.
- 이번 `exp/stack9-a-px4+exp/stack9-b-px4`: gx 표식 턴 1899 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- · exp/stack9-a-px4: gx 표식 턴 878 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- · exp/stack9-b-px4: gx 표식 턴 1021 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- 비교 `exp/stack8-a-px4+exp/stack8-b-px4`: gx 표식 턴 940 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- · exp/stack8-a-px4: gx 표식 턴 462 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- · exp/stack8-b-px4: gx 표식 턴 478 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/stack9-a-px4+exp/stack9-b-px4` | 120 | 68017 | 0.6% (381) | 18.0% (12218) | 7023 | 1.2% (81) | 2.4% (172) | 25.1% (1761/7023) |
| · exp/stack9-a-px4 | 60 | 34905 | 0.7% (241) | 16.8% (5854) | 3765 | 1.2% (47) | 2.8% (106) | 24.2% (913/3765) |
| · exp/stack9-b-px4 | 60 | 33112 | 0.4% (140) | 19.2% (6364) | 3258 | 1.0% (34) | 2.0% (66) | 26.0% (848/3258) |
| 비교 `exp/stack8-a-px4+exp/stack8-b-px4` | 120 | 80480 | 0.9% (709) | 16.8% (13541) | 8801 | 2.0% (175) | 4.5% (398) | 26.9% (2364/8801) |
| · exp/stack8-a-px4 | 60 | 41480 | 1.0% (413) | 15.9% (6613) | 4378 | 2.7% (117) | 6.1% (269) | 27.5% (1204/4378) |
| · exp/stack8-b-px4 | 60 | 39000 | 0.8% (296) | 17.8% (6928) | 4423 | 1.3% (58) | 2.9% (129) | 26.2% (1160/4423) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/stack9-a-px4+exp/stack9-b-px4` | 전체 | 분열 | 10 (17%) | 10.6 | 108% | 131% | 9 | 1 |
| 이번 `exp/stack9-a-px4+exp/stack9-b-px4` | 전체 | 2칸 질주 | 13 (22%) | 12.2 | 103% | 102% | 4 | 0 |
| 이번 `exp/stack9-a-px4+exp/stack9-b-px4` | 전체 | 3칸 질주 | 12 (20%) | 9.5 | 80% | 66% | 3 | 2 |
| 이번 `exp/stack9-a-px4+exp/stack9-b-px4` | 전체 | 한 걸음 | 24 (41%) | 12.4 | 95% | 99% | 18 | 10 |
| 이번 `exp/stack9-a-px4+exp/stack9-b-px4` | 4칸 이상 | 분열 | 6 (25%) | 11 | 124% | 164% | 6 | 0 |
| 이번 `exp/stack9-a-px4+exp/stack9-b-px4` | 4칸 이상 | 2칸 질주 | 7 (29%) | 16 | 79% | 81% | 2 | 0 |
| 이번 `exp/stack9-a-px4+exp/stack9-b-px4` | 4칸 이상 | 3칸 질주 | 5 (21%) | 9.2 | 115% | 89% | 1 | 0 |
| 이번 `exp/stack9-a-px4+exp/stack9-b-px4` | 4칸 이상 | 한 걸음 | 6 (25%) | 13.8 | 210% | 218% | 4 | 2 |
| · exp/stack9-a-px4 | 전체 | 분열 | 5 (16%) | 13.6 | 129% | 149% | 5 | 0 |
| · exp/stack9-a-px4 | 전체 | 2칸 질주 | 8 (26%) | 14.3 | 89% | 85% | 1 | 0 |
| · exp/stack9-a-px4 | 전체 | 3칸 질주 | 6 (19%) | 10.7 | 105% | 91% | 0 | 0 |
| · exp/stack9-a-px4 | 전체 | 한 걸음 | 12 (39%) | 13.9 | 142% | 147% | 9 | 3 |
| · exp/stack9-a-px4 | 4칸 이상 | 분열 | 4 (24%) | 13 | 138% | 175% | 4 | 0 |
| · exp/stack9-a-px4 | 4칸 이상 | 2칸 질주 | 6 (35%) | 17 | 85% | 89% | 1 | 0 |
| · exp/stack9-a-px4 | 4칸 이상 | 3칸 질주 | 3 (18%) | 9 | 152% | 122% | 0 | 0 |
| · exp/stack9-a-px4 | 4칸 이상 | 한 걸음 | 4 (24%) | 13 | 335% | 348% | 2 | 0 |
| · exp/stack9-b-px4 | 전체 | 분열 | 5 (18%) | 7.6 | 68% | 100% | 4 | 1 |
| · exp/stack9-b-px4 | 전체 | 2칸 질주 | 5 (18%) | 9 | 138% | 144% | 3 | 0 |
| · exp/stack9-b-px4 | 전체 | 3칸 질주 | 6 (21%) | 8.3 | 48% | 34% | 3 | 2 |
| · exp/stack9-b-px4 | 전체 | 한 걸음 | 12 (43%) | 10.9 | 36% | 38% | 9 | 7 |
| · exp/stack9-b-px4 | 4칸 이상 | 분열 | 2 (29%) | 7 | 71% | 121% | 2 | 0 |
| · exp/stack9-b-px4 | 4칸 이상 | 2칸 질주 | 1 (14%) | 10 | 20% | 0% | 1 | 0 |
| · exp/stack9-b-px4 | 4칸 이상 | 3칸 질주 | 2 (29%) | 9.5 | 63% | 42% | 1 | 0 |
| · exp/stack9-b-px4 | 4칸 이상 | 한 걸음 | 2 (29%) | 15.5 | 0% | 0% | 2 | 2 |
| 비교 `exp/stack8-a-px4+exp/stack8-b-px4` | 전체 | 분열 | 14 (12%) | 12.4 | 113% | 119% | 9 | 1 |
| 비교 `exp/stack8-a-px4+exp/stack8-b-px4` | 전체 | 2칸 질주 | 24 (21%) | 10.8 | 98% | 89% | 6 | 1 |
| 비교 `exp/stack8-a-px4+exp/stack8-b-px4` | 전체 | 3칸 질주 | 22 (19%) | 9.8 | 99% | 88% | 4 | 2 |
| 비교 `exp/stack8-a-px4+exp/stack8-b-px4` | 전체 | 한 걸음 | 54 (47%) | 12.3 | 40% | 38% | 37 | 29 |
| 비교 `exp/stack8-a-px4+exp/stack8-b-px4` | 4칸 이상 | 분열 | 10 (17%) | 11.6 | 125% | 136% | 8 | 1 |
| 비교 `exp/stack8-a-px4+exp/stack8-b-px4` | 4칸 이상 | 2칸 질주 | 12 (21%) | 12.5 | 93% | 72% | 5 | 1 |
| 비교 `exp/stack8-a-px4+exp/stack8-b-px4` | 4칸 이상 | 3칸 질주 | 11 (19%) | 12.9 | 88% | 75% | 2 | 1 |
| 비교 `exp/stack8-a-px4+exp/stack8-b-px4` | 4칸 이상 | 한 걸음 | 25 (43%) | 13.3 | 44% | 44% | 18 | 12 |
| · exp/stack8-a-px4 | 전체 | 분열 | 8 (14%) | 8.5 | 124% | 144% | 5 | 1 |
| · exp/stack8-a-px4 | 전체 | 2칸 질주 | 6 (11%) | 8.7 | 135% | 117% | 1 | 0 |
| · exp/stack8-a-px4 | 전체 | 3칸 질주 | 13 (23%) | 9.3 | 104% | 91% | 3 | 2 |
| · exp/stack8-a-px4 | 전체 | 한 걸음 | 30 (53%) | 10.2 | 38% | 31% | 20 | 18 |
| · exp/stack8-a-px4 | 4칸 이상 | 분열 | 7 (24%) | 8.7 | 125% | 148% | 5 | 1 |
| · exp/stack8-a-px4 | 4칸 이상 | 2칸 질주 | 4 (14%) | 10 | 138% | 100% | 1 | 0 |
| · exp/stack8-a-px4 | 4칸 이상 | 3칸 질주 | 6 (21%) | 12.8 | 99% | 81% | 1 | 1 |
| · exp/stack8-a-px4 | 4칸 이상 | 한 걸음 | 12 (41%) | 11.3 | 60% | 53% | 7 | 5 |
| · exp/stack8-b-px4 | 전체 | 분열 | 6 (11%) | 17.7 | 107% | 103% | 4 | 0 |
| · exp/stack8-b-px4 | 전체 | 2칸 질주 | 18 (32%) | 11.4 | 89% | 82% | 5 | 1 |
| · exp/stack8-b-px4 | 전체 | 3칸 질주 | 9 (16%) | 10.6 | 92% | 83% | 1 | 0 |
| · exp/stack8-b-px4 | 전체 | 한 걸음 | 24 (42%) | 15 | 42% | 44% | 17 | 11 |
| · exp/stack8-b-px4 | 4칸 이상 | 분열 | 3 (10%) | 18.3 | 125% | 124% | 3 | 0 |
| · exp/stack8-b-px4 | 4칸 이상 | 2칸 질주 | 8 (28%) | 13.8 | 76% | 62% | 4 | 1 |
| · exp/stack8-b-px4 | 4칸 이상 | 3칸 질주 | 5 (17%) | 13 | 75% | 69% | 1 | 0 |
| · exp/stack8-b-px4 | 4칸 이상 | 한 걸음 | 13 (45%) | 15.2 | 34% | 38% | 11 | 7 |

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (182건 중 10건):
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:B:1 · r284 · 드래곤 #228 L3: v9.3 PORTAL? → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:A:1 · r239 · 드래곤 #205 L3: v7.9 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:A:1 · r308 · 드래곤 #252 L3: v8.6 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9-a-px4:proxy4_king:autarky:A:1 · r378 · 드래곤 #209 L3: v-0.9 → 희생, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r140 · 드래곤 #2 L3: v9.4 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r250 · 드래곤 #108 L3: v5.7 PORTAL? → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r316 · 드래곤 #147 L3: v3.1 PORTAL? → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:A:1 · r378 · 드래곤 #157 L3: v8.2 → 아군 머리, 막은 우리 드래곤 L5
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:B:1 · r153 · 드래곤 #24 L3: v7.6 PORTAL? → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Default · 게임 exp/stack9-a-px4:proxy4_king:default:B:1 · r193 · 드래곤 #30 L4: v-11.4 → 아군 머리, 막은 우리 드래곤 L2

## 지도·판본 인식 상세 (cand-mapid)

이번 (120판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 12 | 100% | 100% | 72/72 (72) | 3690 | 3690 (0) | 0 | 0 | 0 | 0 |
| Default a | 12 | 100% | 100% | 48/48 (48) | 638 | 638 (0) | 0 | 0 | 0 | 0 |
| Devil a | 6 | 100% | 100% | 18/18 (18) | 198 | 198 (0) | 0 | 0 | 0 | 19 |
| Devil b | 6 | 100% | 100% | 18/18 (18) | 171 | 168 (0) | 2 | 0 | 0 | 17 |
| Portals a | 12 | 100% | 100% | 36/36 (36) | 2101 | 2100 (0) | 0 | 0 | 0 | 2 |
| Prisoners Dilemma a | 6 | 100% | 100% | 6/18 (6) | 1544 | 1535 (0) | 9 | 0 | 0 | 177 |
| Prisoners Dilemma b | 6 | 100% | 100% | 18/30 (18) | 1033 | 1029 (0) | 4 | 0 | 0 | 305 |
| Queen Of Spades a | 6 | 100% | 100% | 12/12 (12) | 164 | 162 (0) | 1 | 0 | 0 | 55 |
| Queen Of Spades b | 6 | 100% | 100% | 12/12 (12) | 123 | 122 (0) | 1 | 0 | 0 | 71 |
| Schooltime a | 6 | 100% | 100% | 18/18 (18) | 322 | 321 (0) | 0 | 0 | 0 | 16 |
| Schooltime b | 6 | 100% | 100% | 36/36 (36) | 132 | 132 (0) | 0 | 0 | 0 | 12 |
| Slithery Fight a | 6 | 100% | 100% | 48/48 (48) | 505 | 497 (0) | 8 | 0 | 0 | 36 |
| Slithery Fight b | 6 | 100% | 100% | 48/48 (48) | 345 | 336 (0) | 7 | 0 | 0 | 34 |
| Trauma a | 12 | 100% | 100% | 24/24 (24) | 619 | 619 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 12 | 100% | 100% | 24/24 (24) | 143 | 142 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 120/120, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

비교 (120판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 12 | 100% | 100% | 72/72 (72) | 3384 | 3384 (0) | 0 | 0 | 0 | 0 |
| Default a | 12 | 100% | 100% | 48/48 (48) | 414 | 414 (0) | 0 | 0 | 0 | 0 |
| Devil a | 6 | 100% | 100% | 18/18 (18) | 154 | 153 (0) | 0 | 0 | 0 | 19 |
| Devil b | 6 | 100% | 100% | 18/18 (18) | 133 | 133 (0) | 0 | 0 | 0 | 17 |
| Portals a | 12 | 100% | 100% | 36/36 (36) | 1986 | 1986 (0) | 0 | 0 | 0 | 2 |
| Prisoners Dilemma a | 6 | 100% | 100% | 6/18 (6) | 1506 | 1498 (0) | 8 | 0 | 0 | 177 |
| Prisoners Dilemma b | 6 | 100% | 100% | 18/30 (18) | 1034 | 1031 (0) | 3 | 0 | 0 | 267 |
| Queen Of Spades a | 6 | 100% | 100% | 12/12 (12) | 153 | 148 (0) | 4 | 0 | 0 | 49 |
| Queen Of Spades b | 6 | 100% | 100% | 12/12 (12) | 75 | 75 (0) | 0 | 0 | 0 | 71 |
| Schooltime a | 6 | 100% | 100% | 18/18 (18) | 225 | 225 (0) | 0 | 0 | 0 | 12 |
| Schooltime b | 6 | 100% | 100% | 36/36 (36) | 101 | 101 (0) | 0 | 0 | 0 | 7 |
| Slithery Fight a | 6 | 100% | 100% | 48/48 (48) | 370 | 364 (0) | 6 | 0 | 0 | 19 |
| Slithery Fight b | 6 | 100% | 100% | 48/48 (48) | 281 | 273 (0) | 7 | 0 | 0 | 19 |
| Trauma a | 12 | 100% | 100% | 24/24 (24) | 425 | 425 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 12 | 100% | 100% | 24/24 (24) | 159 | 156 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 120/120, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

### Schooltime 판의 경제 (bsp의 가설 수준 지표, 정답 판본별)

| 묶음 | 판본 | 판 | 드래곤 수 r50 | r100 | r0–99 자연 진주 먹음 | 전멸당함 | 끝 최장(전멸 0) | 판당 bsp 분열 |
|---|---|---:|---|---|---|---:|---|---:|
| 이번 | a | 6 | 9 [8, 9] | 16 [13, 16] | 33 [22, 48] | 0% | 22 [19, 36] | 0 |
| 이번 | b | 6 | 8 [7, 8] | 11 [8, 12] | 13 [7, 17] | 0% | 11 [6, 12] | 8.8 |
| 비교 | a | 6 | 9 [8, 9] | 17 [13, 18] | 33 [20, 35] | 0% | 23 [16, 26] | 0 |
| 비교 | b | 6 | 8 [7, 8] | 11 [8, 11] | 14 [10, 15] | 0% | 13 [6, 14] | 9.3 |

- 기준값(`research/experiments/cand-mapid.md`, 웨이브 전에 적음): b에서 드래곤 수 r50 중앙 ≥ 6, r0–99 자연 진주 중앙 ≥ 14. 우리 merge2 계열 b 29판은 3 · 9, 떼 계열(swarm8·px) b 14판은 6 · 14, 상위권 b 승자는 8 · 32다. a는 bsp가 켜지지 않는 대조군이다.

## stack5: 영토 덮기 (csplit · F · cov) 게이트와 가설 수준 지표

- 기준값은 `research/experiments/cand-stack5.md`(웨이브 전)에서, 상위권 승자(TW) 값과 merge2 값은 `research/observations/top-territory.md`에서 왔다. 정의는 영토 연구의 `exp/territory-analysis/extract.js`와 같다(영토 = 시작 몸에서 더 가까운 팀의 칸, 샘 = 그 판 판본 파일의 평균 간격 ≤12, 보로노이 = 용량 1/평균 간격 가중, 거리 = 지도 위 이동 거리, 몸은 무시).

### 게이트 (기능 적용)

| 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|
| csplit 발동: 500라운드형 지도 r0–249 판당 | ≥20 | 19 (전체 1904회) | 19 (전체 1881회) |
| csplit 설계 상황: 부모가 팀 최장(≥8)이 아님 | ≥90% | 100% | 100% |
| csplit 새끼가 30라운드 안에 자연 진주 ≥1개 | ≥45% (TW 47% · 45%) | 40% (1904마리) | 39% (1881마리) |
| csplit 새끼 30라운드 생존 | ≥30% (TW 34% · 51%) | 74% | 77% |
| F 목표(드래곤·샘) 수, 3걸음 안 도착 | – | 2075, 도착 59% | 2043, 도착 60% |
| F 설계 상황: 실제 우리 영토 샘, 처음 표식 때 다른 우리 머리 3걸음 안 없음 | ≥80% | 82% | 82% |
| F 도착 뒤 30라운드 그 무리 자연 진주의 우리 몫(합산) | ≥85% (TW 자기 샘 90%) | 91% (상대 8%, 4782개) | 90% (상대 9%, 4711개) |
| F 같은 몫의 지도 평균(지도마다 합산, 같은 무게, Portals 제외) | ≥85% | 71% (Devil 63%, Prisoners Dilemma 100%, Slithery Fight 64%, Trauma 97%, Autarky 0%, Prisoners Dilemma (10) 100%) | 73% (Autarky 53%, Devil 57%, Prisoners Dilemma 100%, Slithery Fight 61%, Trauma 94%) |
| cov 턴, 20라운드 안 우리 영토 자연 진주 | – | 63738, 20% | 0, – |

### 가설 수준 지표 (관찰; 500라운드형 / 전멸형)

| 지표 | 기준 | 상위권 승자 | merge2 | 이번 | 비교 |
|---|---|---|---|---|---|
| r100 우리 드래곤 수(r100까지 간 판) | ≥15 / ≥10 | 30 / 21 | 4 / 3 | 11.1 / 6.7 | 11 / 7.1 |
| r100 우리 영토 보로노이 몫(용량 가중, 판 평균) | ≥80% | 89% / 81% | 66% / 32% | 70% / 33% | 71% / 34% |
| r100 샘 지킴: 우리 영토 샘 중 우리 머리 3걸음 안(판 평균) | ≥50% | 61% / 55% | 22% / – | 28% / 48% | 28% / 43% |
| 우리 영토 자연 진주(r0부터 생성)를 상대가 먹은 몫(합산) | ≤25% | 11% / 16% | 56% / 55% | 52% / 61% | 52% / 60% |
| 우리 영토 샘 진주를 상대가 먹은 몫(합산) | ≤15% | 7% / 6% | 50% / 33% | 48% / 47% | 47% / 46% |

- 판 수(500라운드형 / 전멸형): 이번 60 / 60 · 비교 60 / 60. 판본 파일을 못 찾은 판: 이번 0 · 비교 0.

### 부작용: 우리 드래곤의 죽음 (판당; 전체 / r250 전)

| 원인 | 이번 | 비교 |
|---|---|---|
| 갇힘(빈 이웃 없음; 통로 고리의 남은 조각 포함) | 72.2 / 34.4 | 68.2 / 33.8 |
| 적 머리에 박힘 | 7.9 / 4.9 | 7.1 / 5 |
| 우리 드래곤끼리 머리 충돌(둘 다 죽음, 둘 다 셈) | 2.2 / 0.8 | 2 / 1 |

- 막힘에서 아군 머리를 피해 죽은 턴(no-exit s): 이번 293 · 비교 188

### 지도별 (이번)

| 지도 | 판 | csplit 판당 | 새끼 먹음 ≥1 | 새끼 30R 생존 | F 목표 · 도착 · 무리 진주 우리 몫 | r100 드래곤 | 보로노이 | 샘 지킴 | 상대가 먹은 영토 진주 | 상대가 먹은 샘 진주 |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| Autarky | 12 | 19.4 | 41% | 93% | 47 · 13% · 0% | 11.4 | 96% | 86% | 9% | 9% |
| Default | 12 | 27.8 | 41% | 66% | 0 · – · – | 11.4 | 27% | – | 73% | – |
| Devil | 12 | 11.2 | 25% | 75% | 138 · 49% · 63% | 7.4 | 26% | 20% | 81% | 83% |
| Portals | 12 | 13.3 | 45% | 58% | 1086 · 77% · 99% | 11.3 | 100% | 28% | 0% | 0% |
| Prisoners Dilemma (10) | 6 | 1.2 | 0% | 71% | 13 · 8% · 100% | 3.8 | 47% | 50% | 25% | 0% |
| Prisoners Dilemma | 6 | 7.3 | 48% | 91% | 61 · 48% · 100% | 3.7 | 99% | 100% | 4% | 2% |
| Queen Of Spades | 12 | 11.3 | 36% | 79% | 0 · – · – | 4.5 | 19% | – | 76% | – |
| Schooltime | 12 | 13.5 | 43% | 87% | 16 · 0% · – | 12.2 | 34% | 0% | 76% | 70% |
| Slithery Fight | 12 | 31.9 | 34% | 76% | 569 · 41% · 64% | 14.3 | 25% | 4% | 78% | 85% |
| Trauma | 12 | 16.8 | 44% | 61% | 145 · 29% · 97% | 6.3 | 94% | 8% | 54% | 1% |
| Trophy | 12 | 9.2 | 51% | 76% | 0 · – · – | 6.6 | 18% | – | 69% | – |

## stack7: 수 바닥 분열(floor)과 왕 길이 상한(kcap) 게이트, 저수 에피소드, 가설 수준 지표, 지도 가르기

- 기준값은 `research/experiments/cand-stack7.md`(웨이브 전)에서, 상위권·우리 값은 `research/observations/our-eliminations.md`(2.6절, 1.3절, 2.2절)에서 왔다. 저수 에피소드와 부류의 정의는 전멸 연구(`exp/eliminations/top.js` I, `lib.js` classOf)와 같다: r50부터 5라운드 간격으로 처음 우리 수 1–3·상대 ≥8인 라운드 r(라운드 첫 턴의 수; r+20이 판 안이고 우리 전멸 전), 그 뒤 [r, r+20) 분열, 20라운드 뒤 4마리 이상이면 회복, 50라운드 안 전멸. 연구의 분열 수는 10라운드 칸 두 개의 전체 분열(탈출 분열 포함)이고, 여기서는 [r, r+20)을 그대로 센다.

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| floor | 발동(판당; floor 지도 판) | – | 20 (0.2; 84판) | 58 (0.7; 84판) |
| floor | 1. 설계 상황: 발동 때 상대 ≥8마리 | ≥90% | 95% | 84% |
| floor | 저수 에피소드가 있는 floor 지도 판 · 그 20라운드 안 floor 발동이 있었던 판 | (관찰) | 41 · 5% | 67 · 19% |
| floor | 2. 즉시 효과 A: 에피소드 20라운드 비탈출 분열(판당; floor 지도) | ≥2.0 (상위 LX·LS 2.0, 우리 0.5) | 0.2 (floor 0, kcap 0, csplit 0.1, lsplit 0.1; 탈출 포함 전체 0.2) | 0.3 (floor 0.2, kcap 0, csplit 0.1; 탈출 포함 전체 0.5) |
| floor | 3. 즉시 효과 B: 에피소드 20라운드 뒤 4마리 이상(floor 지도) | ≥23% (상위 LX 23%, LS 26%, 우리 5%) | 7% (3/41) | 16% (11/67) |
| floor | 4. 즉시 효과 C: floor 새끼 30라운드 생존 | ≥34% (상위 패자 제 영토 새끼 34%, 승자 51%) | 55% (20마리) | 71% (58마리) |
| kcap | 발동(판당; kcap 지도 판) | – | 5 (0.1; 72판) | 2 (0; 72판) |
| kcap | 1. 설계 상황: 부모가 그 순간 팀 최장이고 r250 전 | ≥90% | 100% | 100% |
| kcap | 2. 즉시 효과: 새끼 10라운드 생존 | ≥74% (상위권 길이 4 분열 74.2%) | 100% (5마리) | 100% (2마리) |
| kcap | 2. 즉시 효과: 부모 10라운드 생존 | ≥55% (상위권 54.5%) | 20% | 50% |

### 저수 에피소드 (floor 지도 / 모든 지도; 판정은 floor 지도)

| 묶음 | 지도 | 판 | 에피소드 있음 | 처음 라운드(중앙) | 그때 우리 수 · 상대 수 | 그때 총길이 · 최장 | 20라운드 비탈출 분열 | floor · kcap | 탈출 포함 전체 | 20라운드 뒤 4마리 이상 | 50라운드 안 전멸 |
|---|---|---:|---:|---:|---|---|---:|---|---:|---:|---:|
| 이번 | floor 지도 | 84 | 49% | 160 | 3 · 35.8 | 8 · 3.6 | 0.2 | 0 · 0 | 0.2 | 7% | 17% |
| 이번 | floor 지도 중 전멸형 | 48 | 73% | 150 | 2.9 · 33.2 | 6.4 · 2.4 | 0.2 | 0.1 · 0 | 0.2 | 9% | 20% |
| 이번 | floor 지도 중 500형 | 36 | 17% | 317.5 | 3 · 51.3 | 17 · 10.7 | 0.2 | 0 · 0 | 0.2 | 0% | 0% |
| 이번 | 끄는 지도(Autarky·PD·Portals) | 36 | 25% | 75 | 2.9 · 14.1 | 26.2 · 17.9 | 0.3 | 0 · 0 | 8.3 | 33% | 0% |
| 이번 | 모든 지도 | 120 | 42% | 157.5 | 2.9 · 31.9 | 11.2 · 6.2 | 0.2 | 0 · 0 | 1.7 | 12% | 14% |
| 비교 | floor 지도 | 84 | 80% | 280 | 2.9 · 32.9 | 11.7 · 6.4 | 0.3 | 0.2 · 0 | 0.5 | 16% | 12% |
| 비교 | floor 지도 중 전멸형 | 48 | 90% | 170 | 2.9 · 34.4 | 8.1 · 3.8 | 0.3 | 0.2 · 0 | 0.4 | 12% | 19% |
| 비교 | floor 지도 중 500형 | 36 | 67% | 427.5 | 3 · 30.3 | 18.2 · 11 | 0.3 | 0.3 · 0 | 0.6 | 25% | 0% |
| 비교 | 끄는 지도(Autarky·PD·Portals) | 36 | 47% | 365 | 2.9 · 21.4 | 29.4 · 17.4 | 0.3 | 0 · 0 | 9.2 | 24% | 0% |
| 비교 | 모든 지도 | 120 | 70% | 312.5 | 2.9 · 30.6 | 15.3 · 8.6 | 0.3 | 0.2 · 0 | 2.3 | 18% | 10% |

- 상위권 기준(전멸 연구 2.6절, 전멸형): LX 72%가 그런 때를 겪고(처음 r105) 20라운드에 2.0번 나누며 23%가 회복, 42%가 50라운드 안 전멸. LS 69%, 2.0번, 26%, 0%. 우리 g4 LX 95%(r50), 0.5번, 5%, 15%.

### 가설 수준 지표 (관찰)

| 기능 | 지표 | 기준 | 상위권 · 이전 우리 | 이번 | 비교 |
|---|---|---|---|---|---|
| floor | r100 우리 드래곤 수(전멸형; 전멸은 0) — 전멸형 5지도 / PD 뺀 4지도 | ≥5.5 | 상위 LX 5.5, 우리 g4 LX 2.5 | 6.7 / 7.5 | 7.1 / 7.9 |
| floor | 전멸률(전멸형) | ≤66% | swarm8 66%, merge2 78% | 30% (18/60) / 38% (18/48) | 28% (17/60) / 35% (17/48) |
| floor | 전멸 라운드 중앙(전멸형) | ≥r235 | swarm8 235, merge2 150, stack1–3 163 | 198.5 / 198.5 | 208 / 208 |
| kcap | 우리 전멸 중 E2(왕 사냥) 비율(모든 지도) | ≤8% | 상위 LX 6%, 우리 16% | 6% (E1 0 · E2 1 · E3m 13 · E3l 4) | 0% (E1 0 · E2 0 · E3m 14 · E3l 3) |
| kcap | r50 우리 최장 평균(전멸형; 전멸은 0) — 5지도 / 4지도 | ≤4.5 | 상위 LS 3.8, 우리 g4 LX 6.8 | 5.2 / 3.5 | 5.2 / 3.5 |
| kcap | 전멸한 판의 길이 ≥8 죽음(판당; 모든 지도) | ≤0.4 | 우리 0.75 | 0.3 (18판) | 0.1 (17판) |

### 지도 가르기 (map= 표식으로 확인)

- floor는 Trophy, Queen Of Spades, Devil, Default, Schooltime, Trauma, Slithery Fight에서만, kcap은 그중 Slithery Fight를 뺀 여섯에서만 켠다. 봇은 프로세스마다 자기 창으로 지도 가족을 인식하고(`map=` 표식), 인식 전·`none`이면 끈다. "표식이 켜는 가족이 아닌 발동"은 발동한 프로세스의 마지막 `map=` 표식이 그 기능을 켜는 가족을 대지 않은 발동이다(0이어야 한다). "인식한 프로세스"는 마지막 표식이 그 판의 참 지도 가족을 댄 프로세스다.

| 묶음 | 지도(정답 판본) | 판 | floor 발동 | kcap 발동 | 표식이 켜는 가족이 아닌 발동 | 인식한 프로세스 |
|---|---|---:|---:|---:|---:|---:|
| 이번 | Autarky (끔) | 12 | 0 | 0 | 0 | 100% (3690/3690) |
| 이번 | Default | 12 | 0 | 2 | 0 | 100% (638/638) |
| 이번 | Devil a | 6 | 6 | 0 | 0 | 100% (198/198) |
| 이번 | Devil b | 6 | 8 | 0 | 0 | 99% (170/171) |
| 이번 | Portals (끔) | 12 | 0 | 0 | 0 | 100% (2100/2101) |
| 이번 | Prisoners Dilemma (10) (끔) | 6 | 0 | 0 | 0 | 100% (1033/1033) |
| 이번 | Prisoners Dilemma (끔) | 6 | 0 | 0 | 0 | 100% (1544/1544) |
| 이번 | Queen Of Spades a | 6 | 2 | 0 | 0 | 99% (163/164) |
| 이번 | Queen Of Spades b | 6 | 2 | 2 | 0 | 100% (123/123) |
| 이번 | Schooltime a | 6 | 2 | 0 | 0 | 100% (321/322) |
| 이번 | Schooltime b | 6 | 0 | 0 | 0 | 100% (132/132) |
| 이번 | Slithery Fight a (kcap 끔) | 6 | 0 | 0 | 0 | 100% (505/505) |
| 이번 | Slithery Fight b (kcap 끔) | 6 | 0 | 0 | 0 | 99% (343/345) |
| 이번 | Trauma | 12 | 0 | 0 | 0 | 100% (619/619) |
| 이번 | Trophy | 12 | 0 | 1 | 0 | 99% (142/143) |
| 비교 | Autarky (끔) | 12 | 0 | 0 | 0 | 100% (3384/3384) |
| 비교 | Default | 12 | 7 | 0 | 0 | 100% (414/414) |
| 비교 | Devil a | 6 | 7 | 0 | 0 | 99% (153/154) |
| 비교 | Devil b | 6 | 10 | 0 | 0 | 100% (133/133) |
| 비교 | Portals (끔) | 12 | 0 | 0 | 0 | 100% (1986/1986) |
| 비교 | Prisoners Dilemma (10) (끔) | 6 | 0 | 0 | 0 | 100% (1034/1034) |
| 비교 | Prisoners Dilemma (끔) | 6 | 0 | 0 | 0 | 100% (1506/1506) |
| 비교 | Queen Of Spades a | 6 | 5 | 0 | 0 | 99% (152/153) |
| 비교 | Queen Of Spades b | 6 | 8 | 1 | 0 | 100% (75/75) |
| 비교 | Schooltime a | 6 | 9 | 0 | 0 | 100% (225/225) |
| 비교 | Schooltime b | 6 | 2 | 0 | 0 | 100% (101/101) |
| 비교 | Slithery Fight a (kcap 끔) | 6 | 1 | 0 | 0 | 100% (370/370) |
| 비교 | Slithery Fight b (kcap 끔) | 6 | 4 | 0 | 0 | 100% (280/281) |
| 비교 | Trauma | 12 | 4 | 0 | 0 | 100% (425/425) |
| 비교 | Trophy | 12 | 1 | 1 | 0 | 98% (156/159) |

## stack8: 샘 목표 고르기(F2·F2p), 포털 출구의 아군(px2), 새끼의 몫(cl·ce)

- 기준값은 `research/experiments/cand-stack8.md`(로컬 확인 전, 18:20)에서 왔다. cl·ce의 기준값은 공급망 연구의 값(18:07)이다. F 목표(드래곤·샘 단위)와 포털 통과의 정의는 stack5 절과 "포털 통과" 절과 같다. Fp·cl·ce는 드래곤·진주 단위이고, 설계 상황은 처음 표식 때의 판이다.

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| F2 | 목표 수: F2 표식 / 모든 F(판당) | – | 2075 / 2075 (17.3) | 2043 / 2043 (17) |
| F2 | 1. 설계 상황: F2 표식 목표 (실제 샘 · 우리 영토 · 다른 머리 없음) | ≥90% | 82% (100% · 100% · 82%) | 82% (100% · 100% · 83%) |
| F2 | 1. 설계 상황: 모든 F 목표 | ≥80% | 82% | 82% |
| F2 | 2. 도착(3걸음 안): F2 표식 목표 / 모든 F | ≥80% | 59% / 59% | 60% / 60% |
| F2 | 3. 도착 뒤 30라운드 무리 자연 진주 우리 몫(F2 표식; 합산 · 지도 평균, Portals 제외) | ≥85% · ≥85% | 91% (4782개) · 71% | 90% (4711개) · 73% |
| F2 | 4. 겹친 추격: 다른 우리 드래곤의 같은 샘 목표와 겹침(F2 표식 / 모든 F) | ≤10% | 29% / 29% | 29% / 29% |
| F2p | Fp 진주 수(표식 턴) | – | 1332 (4421턴) | 1406 (4526턴) |
| F2p | 1. 설계 상황: 표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음 | ≥80% | 71% | 70% |
| F2p | 2. 즉시 효과: 그 드래곤이 10라운드 안에 먹음 · 상대가 먹음 | ≥48% · ≤5% | 34% · 22% | 35% · 22% |
| F2p | 끌어내기: F 표식 턴 가운데 유일하게 가장 가까운 자연 진주(7걸음 안, 무리 밖)에서 멀어진 턴 | ≤5% (관찰; W5+W6 15%) | 16% (후보가 있던 턴 29%; F 표식 턴 21918) | 15% (후보가 있던 턴 29%; F 표식 턴 21830) |
| px2 | 발동(px2 + px2x 턴, 판당) | – | 0 (0) | 838 (7) |
| px2 | 1. 설계 상황: 전 라운드 그 칸의 음파가 우리 드래곤에 멈춤 | ≥95% | – | 100% |
| px2 | 2. 즉시 효과 A: 건너지 않음(px2) | ≥80% | – | 38% |
| px2 | 3. 즉시 효과 B: 아군에 멈춘 탐침 뒤 아는 포털을 건너는 걸음에서 아군에 막혀 죽음(판당, v 무관) | ≤0.2 (W5–W7 0.69) | 0.77 (92건) | 0.85 (102건) |
| px2 | 보호: 포털 3라운드 몸 생존 | ≥95% | 94% | 94% |
| px2 | 보호: 건너는 걸음 아군 막힘 죽음(판당, 탐침·v 무관) | ≤0.75 (W5–W7 1.41) | 1.88 (226건) | 1.82 (219건) |
| cl | 진주 수(표식 턴) | – | 22010 (53286턴) | 17951 (42455턴) |
| cl | 설계 상황: 자연 진주, 우리 머리 가운데 표식한 조각만 가장 가까움 | ≥90% | 40% | 39% |
| cl | 즉시 효과: 조각이 먹음 · 우리 팀 · 우리 긴 드래곤 | ≥48% · ≥97% · ≤10% | 65% · 78% · 7% | 67% · 79% · 6% |
| ce | 진주 수(표식 턴) | – | 2225 (3556턴) | 1895 (2959턴) |
| ce | 설계 상황: 적 머리가 진주에서 우리 거리+1 안 | ≥80% | 81% | 83% |
| ce | 즉시 효과: 상대가 먹음 | ≤5% | 48% | 51% |
| ce | 보호: 표식 뒤 5라운드 안 박힘 | ≤19% | 7% | 6% |

- cl·ce의 가설 수준 지표(새끼 30라운드 먹음 ≥45%, 새끼 몫의 상대 몫 ≤3%/≤5%)는 공급망 스크립트 `exp/supply-chain/child_forage.js`로 잰다. 새끼 먹음은 stack5 절의 csplit 줄에도 있다.

### 포털 통과: 전 라운드 탐침(같은 칸, 같은 방향의 음파)별

| 묶음 | 출구 | 탐침 | 필사(v ≤ −20) | 통과 | 몸 3라운드 실패 | 건너는 걸음 아군 막힘 죽음 |
|---|---|---|---|---:|---:|---:|
| 이번 | 아는 포털 | clean | 아님 | 2338 | 4% | 61 |
| 이번 | 미탐색 | clean | 아님 | 1795 | 3% | 27 |
| 이번 | 아는 포털 | ally | 아님 | 423 | 9% | 57 |
| 이번 | 미탐색 | clean | 필사 | 312 | 15% | 7 |
| 이번 | 아는 포털 | none | 아님 | 220 | 8% | 2 |
| 이번 | 아는 포털 | ally(머리) | 아님 | 135 | 16% | 35 |
| 이번 | 미탐색 | ally | 필사 | 88 | 13% | 10 |
| 이번 | 미탐색 | none | 필사 | 84 | 13% | 7 |
| 이번 | 아는 포털 | clean | 필사 | 63 | 11% | 4 |
| 이번 | 미탐색 | ally(머리) | 필사 | 45 | 33% | 16 |
| 이번 | 아는 포털 | enemy | 아님 | 33 | 12% | 0 |
| 이번 | 아는 포털 | enemy(머리) | 아님 | 27 | 7% | 0 |
| 이번 | 미탐색 | enemy(머리) | 필사 | 12 | 25% | 0 |
| 이번 | 미탐색 | enemy | 필사 | 12 | 8% | 0 |
| 이번 | 아는 포털 | none | 필사 | 2 | 0% | 0 |
| 이번 | 아는 포털 | ally | 필사 | 2 | 0% | 0 |
| 비교 | 아는 포털 | clean | 아님 | 2198 | 4% | 54 |
| 비교 | 미탐색 | clean | 아님 | 1722 | 3% | 26 |
| 비교 | 아는 포털 | ally | 필사 | 387 | 11% | 65 |
| 비교 | 미탐색 | clean | 필사 | 279 | 11% | 5 |
| 비교 | 아는 포털 | none | 아님 | 224 | 4% | 0 |
| 비교 | 아는 포털 | ally(머리) | 필사 | 113 | 21% | 35 |
| 비교 | 미탐색 | none | 필사 | 79 | 16% | 11 |
| 비교 | 미탐색 | ally | 필사 | 71 | 23% | 10 |
| 비교 | 아는 포털 | clean | 필사 | 64 | 14% | 4 |
| 비교 | 아는 포털 | ally | 아님 | 49 | 4% | 2 |
| 비교 | 아는 포털 | enemy | 아님 | 40 | 15% | 0 |
| 비교 | 미탐색 | ally(머리) | 필사 | 27 | 22% | 7 |
| 비교 | 아는 포털 | enemy(머리) | 아님 | 26 | 12% | 0 |
| 비교 | 미탐색 | enemy | 필사 | 22 | 27% | 0 |
| 비교 | 미탐색 | enemy(머리) | 필사 | 9 | 33% | 0 |
| 비교 | 아는 포털 | ally(머리) | 아님 | 6 | 0% | 0 |
| 비교 | 아는 포털 | none | 필사 | 3 | 33% | 0 |
| 비교 | 아는 포털 | enemy | 필사 | 1 | 0% | 0 |

## stack9: 늦은 조각 풀 — 늦은 재분열(lsplit), frag 수 상한(fc), 영토 덮기 끌림(cov)

- 기준값은 `research/experiments/cand-stack9.md`(로컬 확인 결과를 보기 전, 21:04)에서, 상위권·우리 값은 `research/observations/supply-chain.md`(7절)에서 왔다. 가설 수준 지표는 그 연구의 코드(`exp/supply-chain/extract.js` analyse)를 같은 기보에 돌려 잰다. "판당"의 분모는 r250 뒤까지 간 우리 팀-경기다(500라운드형: Autarky, Portals, Schooltime, Slithery Fight, Trauma).

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| lsplit | 발동(모든 판당; 500라운드형 r250까지 간 판당) | – | 1298 (10.8; 15.9) | 0 (0; 0) |
| lsplit | 1. 설계 상황: r250–429 · 부모 길이(분열 전) 4–6 · 우리 수(기보) < 목표 | ≥95% | 100% (100% · 100% · 100%; 표식의 수·목표 = 기보 100%) | – (– · – · –; 표식의 수·목표 = 기보 –) |
| lsplit | 2. 즉시 효과 A: 새끼가 30라운드 안에 자연 진주 ≥1 | ≥38% (승자의 늦은 2+2 새끼 38%) | 33% (1298마리; 500형 33% · 전멸형 35%) | – (0마리; 500형 – · 전멸형 –) |
| lsplit | 3. 즉시 효과 B: 새끼가 죽을 때 떨군 진주의 우리 몫(합산) | ≥85% (승자 90%) | 79% (죽은 새끼 1125마리, 진주 1856개; ≥8 24% · 상대 10%) | – (죽은 새끼 0마리, 진주 0개; ≥8 – · 상대 –) |
| fc | 발동(판당) | – | 56 (0.5; frag 전체 60) | 0 (0; frag 전체 32) |
| fc | 1. 설계 상황: r250–420 · 부모가 팀 최장 아님 · 우리 수(기보) ≥ 옛 frag 상한 | ≥95% | 88% (100% · 88% · 100%) | – (– · – · –) |
| fc | 2. 즉시 효과 A: 조각 제 몫(S1: 30라운드 살며 1개 이상 먹거나, 뒤에 희생 표식으로 아군을 먹임) | ≥50% | 59% (56마리) | – (0마리) |
| fc | 3. 즉시 효과 B: 조각이 죽을 때 떨군 진주 중 우리 ≥8이 먹은 몫(합산) | ≥20% (승자 부모 5–7 늦은 새끼 20%) | 45% (죽은 조각 56마리, 진주 96개; 우리 90% · 상대 9%) | – (죽은 조각 0마리, 진주 0개; 우리 – · 상대 –) |
| cov | 창 수(표식 턴; 판당 창) | – | 6918 (63738턴; 57.7) | 0 (0턴; 0) |
| cov | 게이트: 창 30라운드 안에 그 드래곤이 우리 영토 자연 진주 ≥1 | ≥47% (승자 자기 영토 태생 조각 47%) | 27% (창 안에 죽음 26%) | – (창 안에 죽음 –) |
| cov | (관찰) 표식 턴의 끝 칸이 기보 영토의 우리 쪽: 창을 연 턴 / 모든 표식 턴 | – | 89% / 87% | – / – |
| cov | (참고) W5 정의: 표식 턴마다 20라운드 안에 우리 영토 자연 진주 | – | 20% | – |

### 가설 수준 지표 (관찰; 500라운드형 r250–499, r250 뒤까지 간 팀-경기당)

| 지표 | 기준 | 상위권 승자 · 패자 · stack5 · stack6 | 이번 | 비교 |
|---|---|---|---|---|
| lsplit: 조각 탄생(태어날 때 길이 ≤3; 모든 분열) | ≥50 | 156 · 135 · 8.7 · 7.1 | 21.1 (lsplit 15.9, frag 1, 탈출 분열 4.3, 그 밖 0) | 4.9 (lsplit 0, frag 0.4, 탈출 분열 4.2, 그 밖 0.3) |
| lsplit: conv 상태 에피소드 | ≥30 | 57.6 · 39.4 · 17.1 · 20.1 | 25.9 | 14.9 |
| lsplit · fc: conv형 진주(조각 → ≥8) | ≥12 (fc ≥9) | 22.9 · 14.8 · 6.5 · 5.4 | 8.7 | 5 |
| lsplit: 조각 → 조각 희생 진주 | ≥10 | 34.9 · 28.6 · 2.0 · 2.0 | 6.3 | 1.4 |
| fc: frag 새끼(r250–499) | ≥3 | (부모 5–7·8+ 36) · – · 0.4 · 0.9 | 1 | 0.4 |
| (관찰) r350 우리 조각 수(길이 ≤4; r350까지 간 판 평균) | – | 30.5 · – · 6.2 · – | 11.3 | 4.8 |
| (참고) 전멸형: 조각 탄생 · conv 상태 에피소드 · conv형 진주 · 조각 → 조각 | – | 68 · 17.3 · – · – | 9 · 2 · 0.9 · 1.9 | 1.9 · 1.5 · 0.7 · 1 |
| cov: r100 우리 영토에서 적이 더 가까운 몫(판 평균; 500형 / 전멸형) | ≤17% (500형) | 11% · 17% · 27% · 25% | 30% / 66% | 28% / 64% |
| cov: r100 자기 영토 보로노이(판 평균; 500형 / 전멸형) | ≥80% | 89% · 83% · 72% · 74% | 70% / 33% | 71% / 34% |
| cov: 우리 영토 자연 진주를 상대가 먹은 몫(합산; 500형 / 전멸형) | ≤25% | 11% / 16% (승자) | 52% / 61% | 52% / 60% |

- 판 수(r250 뒤까지 간 팀-경기; 500라운드형 / 전멸형): 이번 60 / 48 · 비교 60 / 48. 공급 사슬 재구성 점검이 0이 아닌 판: 이번 0 · 비교 0; 지표 계산 오류: 이번 0 · 비교 0.

### 부작용 (관찰; 판정에 쓰지 않음)

| 항목 | 이번 | 비교 |
|---|---|---|
| lsplit 새끼의 끝: 끝까지 삶 · 표식 희생(conv·feed) · 그 밖 희생 · 갇힘 · 박힘 · 아군 머리 · 그 밖 | 13% · 43% · 0% · 28% · 7% · 4% · 4% (1298마리) | – |
| 어린 조각 규칙(20라운드): lsplit 새끼가 20라운드 안에 끝남(갇힘 · 박힘 · 희생 · 그 밖) / 뒤에 conv·feed로 아군을 먹임(그때 나이 중앙) | 18% (157 · 27 · 18 · 28) / 43% (66) | – |
| lsplit 부모: 10라운드 생존 · 부모 몸(새끼 포함) 30라운드 뒤 길이 변화 평균 · 부모가 죽을 때 떨군 진주 우리 몫 | 86% · 3.7 · 76% (1890개) | – |
| lsplit 모이기 창(r340 뒤) 발동 · 그 새끼 30라운드 안 자연 진주 ≥1 | 773 · 35% | 0 · – |
| 우리 드래곤의 죽음 r250 뒤(판당): 갇힘 · 적 머리에 박힘 · 우리끼리 머리 충돌(둘 다 셈) | 37.7 · 3 · 1.4 | 34.4 · 2.2 · 1.1 |
| 모이기(g) 드래곤(통로 고리 밖): 수 · 왕 3칸 안까지 감 · 희생까지 함 · 가는 길에 죽음 | 541 · 28% · 42% · 30% | 449 · 37% · 51% · 24% |
| 희생 먹이기(feed) · conv: 판당 발동, 떨군 진주 우리 몫 | feed 4.7, 82% · conv 5.1, 98% | feed 2.7, 86% · conv 2.4, 96% |
| 끝 왕 길이(500라운드형 끝까지 간 판) | 22.5 (60판) | 24.2 (60판) |

