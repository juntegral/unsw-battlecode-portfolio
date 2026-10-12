# 구현 적용 확인

- 대상: `exp/stack9l340-b-px4` 60판 · 비교: `exp/stack8-b-px4` 60판
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
| 늦은 재분열 (lsplit, stack9) | 253 (4.2) | 30% | 0 (0) | – |
| 영토 덮기 끌림 30라운드 창 (cov 창, stack9; 드래곤·창 단위) | 3254 (54.2) | 27% | 0 (0) | – |
| 몫이 있어 F 끌림 멈춤 (Fp, stack8; 드래곤·진주 단위) | 685 (11.4) | 35% | 738 (12.3) | 33% |
| 몫을 긴 아군에게 넘기지 않음 (cl, stack8; 드래곤·진주 단위) | 8218 (137) | 67% | 7403 (123.4) | 68% |
| 몫을 한 걸음 가까운 적에게 넘기지 않음 (ce, stack8; 드래곤·진주 단위) | 873 (14.6) | 52% | 828 (13.8) | 52% |
| 아군을 친 탐침 뒤 포털 (px2, stack8) | 0 (0) | – | 402 (6.7) | 36% |
| 수 바닥 분열 (split floor, stack7) | 16 (0.3) | 63% | 35 (0.6) | 60% |
| 왕 길이 상한 분열 (split kcap, stack7) | 4 (0.1) | 100% | 1 (0) | 100% |
| 지도·판본 인식 (map=, cand-mapid; 판 단위) | 60 (1) | 100% | 60 (1) | 100% |
| Schooltime b 초반 분열 (split bsp, cand-mapid) | 53 (0.9) | 98% | 56 (0.9) | 96% |
| 덮기 분열 (csplit, stack5) | 834 (13.9) | 39% | 822 (13.7) | 40% |
| 샘 지킴 (F, stack5; 드래곤·샘 단위) | 1009 (16.8) | 88% | 1039 (17.3) | 85% |
| 영토 덮기 끌림 (cov, stack5) | 32218 (537) | 20% | 0 (0) | – |
| 위협 모형 빈틈 (tg, stack4) | 13423 (223.7) | 98% | 11743 (195.7) | 98% |
| 모이기 시작 제한 (gx, stack4; 드래곤 단위) | 82 (1.4) | 98% | 89 (1.5) | 97% |
| 큰 아군 곁 희생 (conv, stack1 M1) | 186 (3.1) | 98% | 123 (2.1) | 98% |
| 조각 떼기 (split frag, stack2 S1) | 33 (0.6) | 52% | 10 (0.2) | 70% |
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 2379 (39.7) | 83% | 1924 (32.1) | 82% |
| 왕에게 모이기 (g, 드래곤 단위) | 979 (16.3) | 86% | 847 (14.1) | 83% |
| 희생 먹이기 (feed) | 220 (3.7) | 90% | 148 (2.5) | 85% |
| 막다른 길 한입 (pocket-eat) | 1010 (16.8) | 99% | 1011 (16.9) | 99% |
| 탈출 분열 (escape-split) | 3755 (62.6) | 98% | 3758 (62.6) | 98% |
| 출구 없음 (no-exit) | 3923 (65.4) | – | 3839 (64) | – |
| 정책 분열 (split) | 0 (0) | – | 2 (0) | 100% |
| 탈출 질주 3칸 (esc) | 74 (1.2) | 96% | 80 (1.3) | 93% |
| 위협 피하기 2칸 질주 | 584 (9.7) | 93% | 585 (9.8) | 93% |
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 2790 (46.5) | 94% | 2676 (44.6) | 94% |
| 돌진 (TRADE) | 29 (0.5) | 21% | 29 (0.5) | 14% |
| 먹이 질주 (2칸 이상, 먹은 것) | 155 (2.6) | 100% | 128 (2.1) | 100% |
| 기타 2칸 질주 | 71 (1.2) | – | 62 (1) | – |
| 마지막 돌진 (last-trade) | 41 (0.7) | – | 32 (0.5) | – |

- 건강: 턴 227554, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 비교 건강: 턴 205265, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 9480턴 · 끝판(late) 4805턴 · 돌진 신뢰(T, 탈출 끔) 42턴, 그 직후 박혀 죽음 0

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 비교 |
|---|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 2% (45/2636턴) | 2% (35/2225턴) |
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 50.5칸 (12.7회), 진주 우리 93% · 상대 1% | 35.5칸 (7.8회), 진주 우리 92% · 상대 3% |
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 2칸 (판당 0.10회) | 0칸 (판당 0.00회) |
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 23% (920/3941턴) | 26% (1160/4423턴) |
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.067회 (4건, 49칸) | 판당 0.083회 (5건, 84칸) |
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 8.8마리 (30판) | 5.6마리 (30판) |
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 21.1회 | 19.8회 |
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 49% (우리 46%) | 49% (우리 45%) |
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 5.9 대 상대 18.9 (7회) · 박힌 교환의 우리 몫 22% (179회) | 우리 4.6 대 상대 18.8 (6.1회) · 박힌 교환의 우리 몫 20% (156회) |
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 5.1개 | 4개 |

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 늦은 재분열 (lsplit, stack9)

- 이번: 분열 100% · 설계 상황(r250–429, 부모 길이 4–6, 우리 수 < 목표; 기보) 100% (기준 ≥95%) · 새끼 30라운드 안 자연 진주 ≥1 30% (기준 ≥38%) · 죽은 새끼 233마리의 떨군 진주 443개 중 우리 78% (기준 ≥85%) · ≥8 29% · 상대 14% · 새끼 10·30라운드 생존 85% · 67% · 부모 길이 평균 4.4 · r340 뒤 0회
- 상대별: proxy4_elim 75회 31% · proxy4_king 87회 26% · proxy4_swarm 91회 34%
- 지도별: Autarky 65회 40% · Default 48회 29% · Devil 3회 67% · Portals 16회 25% · Queen Of Spades 23회 22% · Schooltime 8회 25% · Slithery Fight 29회 24% · Trauma 61회 28%
- 국면별: r250-349 253회 30%

실패 사례 (176건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r251 · 드래곤 #106 L4: 새끼 L2 · 우리 10/22마리 → 새끼 죽음 r304 갇힘(나이 53, 진주 1개 중 우리 0), 30라운드 안 자연 진주 0
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:A:2 · r250 · 드래곤 #164 L4: 새끼 L2 · 우리 19/21마리 → 새끼 죽음 r268 갇힘(나이 18, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:B:2 · r307 · 드래곤 #38 L4: 새끼 L2 · 우리 5/11마리 → 새끼 죽음 r308 박힘(상대 돌진)(나이 1, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r304 · 드래곤 #353 L4: 새끼 L2 · 우리 10/11마리 → 새끼 죽음 r378 갇힘(나이 74, 진주 2개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_king:queen_of_spades_b:B:2 · r268 · 드래곤 #102 L4: 새끼 L2 · 우리 9/19마리 → 새끼 죽음 r350 박힘(상대 돌진)(나이 82, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_king:schooltime_b:B:2 · r307 · 드래곤 #3 L4: 새끼 L2 · 우리 6/40마리 → 새끼 죽음 r386 돌진(나이 79, 진주 2개 중 우리 0), 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/stack9l340-b-px4:proxy4_king:trauma:A:2 · r256 · 드래곤 #16 L4: 새끼 L2 · 우리 8/25마리 → 새끼 죽음 r456 희생(나이 200, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r253 · 드래곤 #122 L4: 새끼 L2 · 우리 17/37마리 → 새끼 죽음 r495 희생(나이 242, 진주 5개 중 우리 2), 30라운드 안 자연 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack9l340-b-px4:proxy4_swarm:autarky:A:2 · r257 · 드래곤 #159 L4: 새끼 L2 · 우리 20/21마리 → 새끼 끝까지 생존, 30라운드 안 자연 진주 0
- proxy4_swarm · Default · 게임 exp/stack9l340-b-px4:proxy4_swarm:default:B:2 · r250 · 드래곤 #117 L4: 새끼 L2 · 우리 14/22마리 → 새끼 죽음 r289 갇힘(나이 39, 진주 1개 중 우리 1), 30라운드 안 자연 진주 0

## 영토 덮기 끌림 30라운드 창 (cov 창, stack9; 드래곤·창 단위)

- 이번: 창 3254개 (표식 턴 32218) · 창 30라운드 안 우리 영토 자연 진주 ≥1 27% (기준 ≥47%) · 창 안에 죽음 25% · 판 끝에 잘린 창 60 · 창을 연 표식 턴의 끝 칸이 기보 영토의 우리 쪽 92%
- 상대별: proxy4_elim 1107회 28% · proxy4_king 1062회 26% · proxy4_swarm 1085회 27%
- 지도별: Autarky 382회 33% · Default 332회 17% · Devil 188회 31% · Portals 399회 45% · Prisoners Dilemma (10) 133회 3% · Queen Of Spades 280회 19% · Schooltime 479회 18% · Slithery Fight 491회 34% · Trauma 455회 21% · Trophy 115회 42%
- 국면별: r0-99 825회 37% · r100-249 1205회 21% · r250-349 683회 23% · r350-449 443회 30% · r450+ 98회 22%

실패 사례 (2374건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r0 · 드래곤 #0 L4: 창 r0–r30, 표식 1턴 → 못 먹음
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:A:2 · r0 · 드래곤 #6 L3: 창 r0–r30, 표식 13턴 → 못 먹음
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r17 · 드래곤 #0 L2: 창 r17–r47, 표식 6턴 → 못 먹음
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r15 · 드래곤 #6 L2: 창 r15–r45, 표식 18턴 → 못 먹음
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r0 · 드래곤 #2 L3: 창 r0–r30, 표식 16턴 → 못 먹음
- proxy4_king · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_king:queen_of_spades_b:B:2 · r0 · 드래곤 #3 L3: 창 r0–r30, 표식 31턴 → 못 먹음
- proxy4_king · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_king:schooltime_b:A:2 · r9 · 드래곤 #2 L2: 창 r9–r39, 표식 14턴 → 못 먹음
- proxy4_king · Trauma · 게임 exp/stack9l340-b-px4:proxy4_king:trauma:A:2 · r0 · 드래곤 #2 L4: 창 r0–r30, 표식 5턴 → 못 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r0 · 드래곤 #6 L2: 창 r0–r30, 표식 23턴 → 못 먹음
- proxy4_king · Trophy · 게임 exp/stack9l340-b-px4:proxy4_king:trophy:A:2 · r34 · 드래곤 #8 L2: 창 r34–r64, 표식 9턴 → 못 먹음

## 몫이 있어 F 끌림 멈춤 (Fp, stack8; 드래곤·진주 단위)

- 이번: 진주 685개 (표식 턴 2347; 표식 때 진주 있음 96%) · 설계 상황(표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음) 72% · 그 드래곤이 먹음 36% (10라운드 안 35%) · 우리 팀 73% · 우리 긴 드래곤 15% · 상대 20%
- 비교: 진주 738개 (표식 턴 2445; 표식 때 진주 있음 97%) · 설계 상황(표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음) 69% · 그 드래곤이 먹음 34% (10라운드 안 33%) · 우리 팀 70% · 우리 긴 드래곤 16% · 상대 23%
- 상대별: proxy4_elim 207회 29% · proxy4_king 237회 36% · proxy4_swarm 241회 38%
- 지도별: Autarky 1회 100% · Devil 25회 30% · Portals 474회 42% · Prisoners Dilemma (10) 2회 0% · Slithery Fight 181회 17% · Trauma 2회 0%
- 국면별: r0-99 251회 33% · r100-249 229회 30% · r250-349 205회 42%

실패 사례 (430건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r58 · 드래곤 #4 L2: 진주 (15,15) 우리 거리 6 (설계 밖) → 상대가 먹음
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r17 · 드래곤 #6 L2: 진주 (13,6) 우리 거리 99 → 상대가 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r0 · 드래곤 #8 L5: 진주 (31,5) 우리 거리 5 → 다른 우리 드래곤이 먹음
- proxy4_swarm · Devil · 게임 exp/stack9l340-b-px4:proxy4_swarm:devil_b:A:2 · r28 · 드래곤 #4 L2: 진주 (14,7) 우리 거리 4 → 상대가 먹음
- proxy4_swarm · Portals · 게임 exp/stack9l340-b-px4:proxy4_swarm:portals:A:2 · r17 · 드래곤 #6 L2: 진주 (13,6) 우리 거리 99 → 상대가 먹음
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_swarm:prisoners_dilemma_10:B:2 · r145 · 드래곤 #5 L3: 진주 (16,6) 우리 거리 4 (설계 밖) → 상대가 먹음
- proxy4_swarm · Trauma · 게임 exp/stack9l340-b-px4:proxy4_swarm:trauma:A:2 · r78 · 드래곤 #0 L3: 진주 (14,18) 우리 거리 6 → 상대가 먹음
- proxy4_swarm · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r0 · 드래곤 #8 L5: 진주 (31,5) 우리 거리 5 → 다른 우리 드래곤이 먹음
- proxy4_elim · Devil · 게임 exp/stack9l340-b-px4:proxy4_elim:devil_b:A:2 · r35 · 드래곤 #4 L3: 진주 (14,8) 우리 거리 3 → 상대가 먹음
- proxy4_elim · Portals · 게임 exp/stack9l340-b-px4:proxy4_elim:portals:A:2 · r21 · 드래곤 #7 L2: 진주 (13,6) 우리 거리 99 → 상대가 먹음

## 몫을 긴 아군에게 넘기지 않음 (cl, stack8; 드래곤·진주 단위)

- 이번: 진주 8218개 (표식 턴 20588; 표식 때 진주 있음 97%) · 설계 상황(자연 진주이고 우리 머리 가운데 표식한 조각만 가장 가까움) 42% · 그 드래곤이 먹음 67% (10라운드 안 66%) · 우리 팀 79% · 우리 긴 드래곤 7% · 상대 15%
- 비교: 진주 7403개 (표식 턴 18424; 표식 때 진주 있음 97%) · 설계 상황(자연 진주이고 우리 머리 가운데 표식한 조각만 가장 가까움) 42% · 그 드래곤이 먹음 68% (10라운드 안 67%) · 우리 팀 80% · 우리 긴 드래곤 7% · 상대 16%
- 상대별: proxy4_elim 2787회 65% · proxy4_king 2530회 69% · proxy4_swarm 2901회 67%
- 지도별: Autarky 2257회 92% · Default 672회 70% · Devil 308회 80% · Portals 1138회 67% · Prisoners Dilemma (10) 55회 30% · Queen Of Spades 529회 56% · Schooltime 437회 62% · Slithery Fight 1607회 38% · Trauma 938회 60% · Trophy 277회 64%
- 국면별: r0-99 2095회 64% · r100-249 2516회 67% · r250-349 1808회 66% · r350-449 1414회 69% · r450+ 385회 83%

실패 사례 (2636건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r23 · 드래곤 #2 L2: 진주 (4,10) 우리 거리 6 (설계 밖) → 다른 우리 드래곤이 먹음
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:A:2 · r23 · 드래곤 #10 L4: 진주 (53,12) 우리 거리 99 → 상대가 먹음
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r24 · 드래곤 #4 L2: 진주 (14,7) 우리 거리 6 → 상대가 먹음
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r10 · 드래곤 #0 L3: 진주 (4,11) 우리 거리 99 → 아무도 안 먹음
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r9 · 드래곤 #6 L2: 진주 (17,13) 우리 거리 6 (설계 밖) → 상대가 먹음
- proxy4_king · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_king:queen_of_spades_b:B:2 · r101 · 드래곤 #3 L2: 진주 (3,2) 우리 거리 6 (설계 밖) → 상대가 먹음
- proxy4_king · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_king:schooltime_b:A:2 · r32 · 드래곤 #0 L2: 진주 (8,12) 우리 거리 6 → 상대가 먹음
- proxy4_king · Trauma · 게임 exp/stack9l340-b-px4:proxy4_king:trauma:A:2 · r66 · 드래곤 #0 L2: 진주 (11,10) 우리 거리 99 → 다른 우리 드래곤이 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r0 · 드래곤 #12 L2: 진주 (21,1) 우리 거리 4 → 다른 우리 드래곤이 먹음
- proxy4_king · Trophy · 게임 exp/stack9l340-b-px4:proxy4_king:trophy:A:2 · r3 · 드래곤 #2 L3: 진주 (7,2) 우리 거리 5 (설계 밖) → 다른 우리 드래곤이 먹음

## 몫을 한 걸음 가까운 적에게 넘기지 않음 (ce, stack8; 드래곤·진주 단위)

- 이번: 진주 873개 (표식 턴 1387; 표식 때 진주 있음 97%) · 설계 상황(적 머리가 진주에서 우리 거리+1 안) 82% · 그 드래곤이 먹음 27% (10라운드 안 24%) · 우리 팀 38% · 우리 긴 드래곤 4% · 상대 48% · 5라운드 안 박힘 7%
- 비교: 진주 828개 (표식 턴 1252; 표식 때 진주 있음 96%) · 설계 상황(적 머리가 진주에서 우리 거리+1 안) 81% · 그 드래곤이 먹음 29% (10라운드 안 26%) · 우리 팀 41% · 우리 긴 드래곤 6% · 상대 48% · 5라운드 안 박힘 5%
- 상대별: proxy4_elim 302회 59% · proxy4_king 260회 48% · proxy4_swarm 311회 49%
- 지도별: Autarky 17회 82% · Default 97회 49% · Devil 41회 43% · Portals 47회 98% · Prisoners Dilemma (10) 18회 29% · Queen Of Spades 96회 51% · Schooltime 83회 45% · Slithery Fight 357회 54% · Trauma 64회 40% · Trophy 53회 37%
- 국면별: r0-99 162회 37% · r100-249 293회 50% · r250-349 229회 58% · r350-449 158회 57% · r450+ 31회 74%

실패 사례 (409건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r79 · 드래곤 #14 L2: 진주 (10,12) 우리 거리 3 → 상대가 먹음
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r27 · 드래곤 #4 L2: 진주 (16,1) 우리 거리 5 → 상대가 먹음
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r9 · 드래곤 #6 L2: 진주 (17,13) 우리 거리 6 → 상대가 먹음
- proxy4_king · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_king:queen_of_spades_b:B:2 · r125 · 드래곤 #40 L2: 진주 (15,1) 우리 거리 3 → 상대가 먹음
- proxy4_king · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_king:schooltime_b:A:2 · r40 · 드래곤 #2 L2: 진주 (14,5) 우리 거리 5 → 상대가 먹음
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r29 · 드래곤 #12 L2: 진주 (26,1) 우리 거리 4 → 상대가 먹음
- proxy4_king · Trophy · 게임 exp/stack9l340-b-px4:proxy4_king:trophy:A:2 · r58 · 드래곤 #5 L3: 진주 (4,2) 우리 거리 3 → 상대가 먹음
- proxy4_swarm · Default · 게임 exp/stack9l340-b-px4:proxy4_swarm:default:A:2 · r85 · 드래곤 #20 L2: 진주 (16,7) 우리 거리 6 → 상대가 먹음
- proxy4_swarm · Devil · 게임 exp/stack9l340-b-px4:proxy4_swarm:devil_b:A:2 · r40 · 드래곤 #8 L2: 진주 (12,10) 우리 거리 5 → 상대가 먹음
- proxy4_swarm · Autarky · 게임 exp/stack9l340-b-px4:proxy4_swarm:autarky:B:2 · r56 · 드래곤 #7 L2: 진주 (26,13) 우리 거리 2 → 상대가 먹음

## 수 바닥 분열 (split floor, stack7)

- 이번: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 81% · 적 머리가 7×7 시야 안 38% · 부모 길이 평균 4.7 · 우리 수(표식) 평균 2.4 · 상대 수 평균 19.1 · 새끼 10라운드 생존 94% · 30라운드 63% · 부모 10라운드 생존 75% · 30라운드 50% · 새끼 30라운드 안 1개 이상 먹음 44% · 30라운드 뒤 가족 길이 변화 -0.5 · 30라운드 안 새끼가 죽은 원인: 희생 1, 갇힘 1, 돌진 4
- 비교: 분열 100% · 설계 상황(발동 때 상대 ≥8마리) 86% · 적 머리가 7×7 시야 안 26% · 부모 길이 평균 5.4 · 우리 수(표식) 평균 2.7 · 상대 수 평균 21.5 · 새끼 10라운드 생존 77% · 30라운드 60% · 부모 10라운드 생존 86% · 30라운드 66% · 새끼 30라운드 안 1개 이상 먹음 46% · 30라운드 뒤 가족 길이 변화 1.3 · 30라운드 안 새끼가 죽은 원인: 희생 3, 갇힘 8, 돌진 1, 박힘(상대 돌진) 2
- 상대별: proxy4_elim 7회 57% · proxy4_king 4회 50% · proxy4_swarm 5회 80%
- 지도별: Devil 14회 57% · Queen Of Spades 2회 100%
- 국면별: r0-99 1회 0% · r100-249 1회 100% · r250-349 5회 80% · r350-449 8회 50% · r450+ 1회 100%

실패 사례 (6건 중 6건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r422 · 드래곤 #35 L4: 우리 3마리 · 상대 6마리 · 새끼 L2 → 새끼 죽음 r442 희생, 부모 10라운드 생존 (설계 밖: 상대 < 8마리) · 표식 map=Devil/b
- proxy4_swarm · Devil · 게임 exp/stack9l340-b-px4:proxy4_swarm:devil_b:B:2 · r431 · 드래곤 #437 L4: 우리 2마리 · 상대 16마리 · 새끼 L2 → 새끼 죽음 r443 돌진, 상대 길이 5, 부모 10라운드 생존 · 표식 map=Devil/b
- proxy4_elim · Devil · 게임 exp/stack9l340-b-px4:proxy4_elim:devil_b:A:2 · r402 · 드래곤 #426 L4: 우리 3마리 · 상대 8마리 · 새끼 L2 → 새끼 죽음 r419 돌진, 상대 길이 23, 부모 10라운드 생존 · 표식 map=Devil/b
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:B:2 · r400 · 드래곤 #407 L4: 우리 3마리 · 상대 13마리 · 새끼 L2 → 새끼 죽음 r411 갇힘, 상대 길이 6, 부모 10라운드 죽음 · 표식 map=Devil/b
- proxy4_elim · Devil · 게임 exp/stack9l340-b-px4:proxy4_elim:devil_b:B:2 · r99 · 드래곤 #7 L4: 우리 3마리 · 상대 31마리 · 적 머리 시야 안 · 새끼 L2 → 새끼 죽음 r101 돌진, 상대 길이 3, 부모 10라운드 생존 · 표식 map=Devil/b
- proxy4_elim · Devil · 게임 exp/stack9l340-b-px4:proxy4_elim:devil_b:B:2 · r295 · 드래곤 #7 L4: 우리 1마리 · 상대 45마리 · 새끼 L2 → 새끼 죽음 r315 돌진, 상대 길이 7, 부모 10라운드 죽음 · 표식 map=Devil/b

## 왕 길이 상한 분열 (split kcap, stack7)

- 이번: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 100% · 부모 길이 평균 12 · 우리 수(표식) 평균 5 · 상대 수 평균 24 · 새끼 10라운드 생존 100% · 30라운드 50% · 부모 10라운드 생존 0% · 30라운드 0% · 새끼 30라운드 안 1개 이상 먹음 75% · 30라운드 뒤 가족 길이 변화 -2.5 · 30라운드 안 새끼가 죽은 원인: 갇힘 1, 박힘(상대 돌진) 1
- 비교: 분열 100% · 설계 상황(부모가 그 순간 팀 최장, r250 전) 100% · 적 머리가 7×7 시야 안 100% · 부모 길이 평균 9 · 우리 수(표식) 평균 5 · 상대 수 평균 9 · 새끼 10라운드 생존 100% · 30라운드 0% · 부모 10라운드 생존 0% · 30라운드 0% · 새끼 30라운드 안 1개 이상 먹음 0% · 30라운드 뒤 가족 길이 변화 -3 · 30라운드 안 새끼가 죽은 원인: 박힘(상대 돌진) 1
- 상대별: proxy4_elim 1회 100% · proxy4_king 1회 100% · proxy4_swarm 2회 100%
- 지도별: Default 2회 100% · Queen Of Spades 2회 100%
- 국면별: r100-249 4회 100%

## 지도·판본 인식 (map=, cand-mapid; 판 단위)

- 이번: 판본을 기보로 가릴 수 있는 판 60/60 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 95%, 그중 정답 100% · 프로세스 5170: 표식 없음 3, 결정 5154 (정답 100%, 틀림 0), 가족만 13, 모름 0, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 305라운드
- 비교: 판본을 기보로 가릴 수 있는 판 60/60 · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) 100% (기준 ≥95%) · 첫 결정이 정답 100% · 시작 드래곤 0라운드 결정 95%, 그중 정답 100% · 프로세스 4906: 표식 없음 4, 결정 4892 (정답 100%, 틀림 0), 가족만 10, 모름 0, none 0 · 태어나서 결정까지 p50 0 / p90 0 / 최대 267라운드
- 상대별: proxy4_elim 20회 100% · proxy4_king 20회 100% · proxy4_swarm 20회 100%
- 지도별: Autarky a 6회 100% · Default a 6회 100% · Devil b 6회 100% · Portals a 6회 100% · Prisoners Dilemma b 6회 100% · Queen Of Spades b 6회 100% · Schooltime b 6회 100% · Slithery Fight b 6회 100% · Trauma a 6회 100% · Trophy a 6회 100%
- 국면별: r0-99 60회 100%

## Schooltime b 초반 분열 (split bsp, cand-mapid)

- 이번: 분열 100% · 설계 상황(그 판이 실제로 Schooltime b) 100% · 조각 10라운드 생존 98% (기준 ≥85%; 상위권 b 92%) · 10라운드 안 1개 이상 먹음 17% (상위권 b 20%) · 부모 10라운드 생존 100% · 조각 30라운드 생존 98%, 30라운드 안 1개 이상 먹음 32% · 30라운드 뒤 가족 길이 변화 4.7 · 30라운드 안 조각이 죽은 원인: 갇힘 1
- 비교: 분열 100% · 설계 상황(그 판이 실제로 Schooltime b) 100% · 조각 10라운드 생존 96% (기준 ≥85%; 상위권 b 92%) · 10라운드 안 1개 이상 먹음 11% (상위권 b 20%) · 부모 10라운드 생존 100% · 조각 30라운드 생존 95%, 30라운드 안 1개 이상 먹음 23% · 30라운드 뒤 가족 길이 변화 3.3 · 30라운드 안 조각이 죽은 원인: 박힘(상대 돌진) 1, 갇힘 2
- 상대별: proxy4_elim 19회 95% · proxy4_king 16회 100% · proxy4_swarm 18회 100%
- 지도별: Schooltime 53회 98%
- 국면별: r0-99 40회 100% · r100-249 13회 92%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_elim · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_elim:schooltime_b:B:2 · r103 · 드래곤 #18 L4: 조각 L2 → 조각 죽음 r106 갇힘, 10·30라운드 안 먹은 진주 0·0

## 덮기 분열 (csplit, stack5)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 35% · 부모가 스스로 최장이라 믿음(k) 71% · 새끼 30라운드 안 자연 진주 ≥1 39% (500형 42% · 전멸형 35%; 기준 ≥45%) · 새끼 30라운드 생존 73% (500형 73% · 전멸형 73%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 88% · 새끼 30라운드 안 자연 진주 평균 0.8 · 30라운드 안 죽은 원인: 갇힘 167, 돌진 12, 아군 머리 9, 박힘(상대 돌진) 37, 적 몸통 1
- 비교: 분열 100% · 설계 상황(부모가 팀 최장 ≥8이 아님) 100% · 적 머리가 시야에 있을 때 35% · 부모가 스스로 최장이라 믿음(k) 70% · 새끼 30라운드 안 자연 진주 ≥1 40% (500형 40% · 전멸형 41%; 기준 ≥45%) · 새끼 30라운드 생존 75% (500형 74% · 전멸형 75%; 기준 ≥30%) · 새끼가 우리 영토에서 태어남 90% · 새끼 30라운드 안 자연 진주 평균 0.9 · 30라운드 안 죽은 원인: 갇힘 145, 돌진 10, 박힘(상대 돌진) 43, 아군 머리 9, 희생 1
- 상대별: proxy4_elim 299회 39% · proxy4_king 259회 37% · proxy4_swarm 276회 39%
- 지도별: Autarky 122회 43% · Default 154회 36% · Devil 60회 22% · Portals 81회 41% · Prisoners Dilemma (10) 7회 0% · Queen Of Spades 41회 17% · Schooltime 28회 21% · Slithery Fight 143회 35% · Trauma 127회 53% · Trophy 71회 56%
- 국면별: r0-99 383회 42% · r100-249 451회 36%

실패 사례 (510건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r1 · 드래곤 #0 L4: 새끼 L2, 적 머리 시야 안 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:A:2 · r73 · 드래곤 #61 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r9 · 드래곤 #4 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r50 · 드래곤 #2 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_king:queen_of_spades_b:B:2 · r38 · 드래곤 #3 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_king:schooltime_b:A:2 · r178 · 드래곤 #9 L6: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trauma · 게임 exp/stack9l340-b-px4:proxy4_king:trauma:A:2 · r1 · 드래곤 #0 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r3 · 드래곤 #31 L5: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0
- proxy4_king · Trophy · 게임 exp/stack9l340-b-px4:proxy4_king:trophy:A:2 · r25 · 드래곤 #5 L4: 새끼 L2 → 30라운드 생존, 30라운드 안 자연 진주 0

## 샘 지킴 (F, stack5; 드래곤·샘 단위)

- 이번: 목표 1009개(표식 턴 11006) · 설계 상황 83% (실제 샘 100%, 우리 영토 100%, 처음에 다른 우리 머리 3걸음 안 없음 83%; 기준 ≥80%) · 3걸음 안 도착 60% · 도착 뒤 30라운드 그 무리 자연 진주 2242개 중 우리 90% · 상대 9% (합산 기준 ≥85%) · 처음 거리 평균 3.2
- 비교: 목표 1039개(표식 턴 11370) · 설계 상황 83% (실제 샘 100%, 우리 영토 100%, 처음에 다른 우리 머리 3걸음 안 없음 83%; 기준 ≥80%) · 3걸음 안 도착 60% · 도착 뒤 30라운드 그 무리 자연 진주 2300개 중 우리 89% · 상대 9% (합산 기준 ≥85%) · 처음 거리 평균 3.2
- 상대별: proxy4_elim 322회 92% · proxy4_king 349회 87% · proxy4_swarm 338회 84%
- 지도별: Autarky 29회 0% · Devil 77회 54% · Portals 563회 99% · Prisoners Dilemma (10) 13회 100% · Slithery Fight 251회 49% · Trauma 76회 83%
- 국면별: r0-99 372회 79% · r100-249 376회 94% · r250-349 261회 94%

실패 사례 (62건 중 10건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:A:2 · r130 · 드래곤 #2 L2: 샘 (19,1) 처음 거리 6 → r196 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r41 · 드래곤 #4 L2: 샘 (14,8) 처음 거리 5 → r60 도착, 30라운드 무리 진주 7개 중 우리 0 · 상대 7
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:B:2 · r280 · 드래곤 #342 L3: 샘 (4,14) 처음 거리 0 (설계 밖: 실제 샘 1, 우리 영토 1, 다른 머리 1) → r280 도착, 30라운드 무리 진주 4개 중 우리 0 · 상대 0
- proxy4_king · Trauma · 게임 exp/stack9l340-b-px4:proxy4_king:trauma:A:2 · r265 · 드래곤 #116 L3: 샘 (11,12) 처음 거리 4 → r267 도착, 30라운드 무리 진주 6개 중 우리 4 · 상대 2
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r0 · 드래곤 #8 L5: 샘 (33,2) 처음 거리 0 → r0 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_swarm · Devil · 게임 exp/stack9l340-b-px4:proxy4_swarm:devil_b:A:2 · r43 · 드래곤 #10 L2: 샘 (8,15) 처음 거리 2 → r43 도착, 30라운드 무리 진주 4개 중 우리 2 · 상대 2
- proxy4_swarm · Autarky · 게임 exp/stack9l340-b-px4:proxy4_swarm:autarky:A:2 · r36 · 드래곤 #2 L4: 샘 (19,1) 처음 거리 6 → r162 도착, 30라운드 무리 진주 2개 중 우리 0 · 상대 2
- proxy4_swarm · Portals · 게임 exp/stack9l340-b-px4:proxy4_swarm:portals:A:2 · r300 · 드래곤 #351 L3: 샘 (27,0) 처음 거리 0 → r300 도착, 30라운드 무리 진주 4개 중 우리 0 · 상대 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r0 · 드래곤 #8 L5: 샘 (33,2) 처음 거리 0 → r0 도착, 30라운드 무리 진주 1개 중 우리 0 · 상대 1
- proxy4_elim · Autarky · 게임 exp/stack9l340-b-px4:proxy4_elim:autarky:B:2 · r110 · 드래곤 #3 L2: 샘 (34,16) 처음 거리 6 → r178 도착, 30라운드 무리 진주 3개 중 우리 0 · 상대 3

## 영토 덮기 끌림 (cov, stack5)

- 이번: 턴 32218 · 20라운드 안 우리 영토 자연 진주 먹음 20%
- 상대별: proxy4_elim 11237회 22% · proxy4_king 10836회 19% · proxy4_swarm 10145회 19%
- 지도별: Autarky 2769회 28% · Default 3725회 13% · Devil 1608회 23% · Portals 1420회 44% · Prisoners Dilemma (10) 1989회 2% · Queen Of Spades 3957회 15% · Schooltime 6777회 17% · Slithery Fight 4872회 28% · Trauma 4027회 16% · Trophy 1074회 34%
- 국면별: r0-99 7627회 30% · r100-249 11976회 14% · r250-349 6669회 15% · r350-449 4613회 26% · r450+ 1333회 21%

실패 사례 (25780건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r0 · 드래곤 #0 L4
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:A:2 · r0 · 드래곤 #6 L3
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r13 · 드래곤 #8 L2
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r0 · 드래곤 #0 L3
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r0 · 드래곤 #2 L3
- proxy4_king · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_king:queen_of_spades_b:B:2 · r0 · 드래곤 #3 L3
- proxy4_king · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_king:schooltime_b:A:2 · r9 · 드래곤 #2 L2
- proxy4_king · Trauma · 게임 exp/stack9l340-b-px4:proxy4_king:trauma:A:2 · r0 · 드래곤 #0 L4
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r0 · 드래곤 #6 L2
- proxy4_king · Trophy · 게임 exp/stack9l340-b-px4:proxy4_king:trophy:A:2 · r8 · 드래곤 #0 L2

## 위협 모형 빈틈 (tg, stack4)

- 이번: 피함(tg) 56% · 위협 칸으로 감(tgx) 5973턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 99% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 98%) · 길이별 L2-5 13171 · L6-9 132 · L10+ 120
- 비교: 피함(tg) 57% · 위협 칸으로 감(tgx) 5104턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 99% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 97%) · 길이별 L2-5 11460 · L6-9 141 · L10+ 142
- 상대별: proxy4_elim 4553회 98% · proxy4_king 4581회 99% · proxy4_swarm 4289회 98%
- 지도별: Autarky 745회 99% · Default 2410회 98% · Devil 1050회 98% · Portals 8회 100% · Prisoners Dilemma (10) 769회 99% · Queen Of Spades 1367회 99% · Schooltime 2359회 99% · Slithery Fight 3191회 99% · Trauma 313회 98% · Trophy 1211회 96%
- 국면별: r0-99 2314회 98% · r100-249 5926회 98% · r250-349 3347회 98% · r350-449 1622회 99% · r450+ 214회 99%

실패 사례 (229건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r85 · 드래곤 #13 L2: 위협 칸으로 감(tgx), 적 머리 경로 1칸 · 맨해튼 1칸(길이 2) → 박힘 r87 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:A:2 · r121 · 드래곤 #4 L2: 피함(tg), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r123 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_king:prisoners_dilemma_10:B:2 · r164 · 드래곤 #7 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r166 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_king:queen_of_spades_b:B:2 · r129 · 드래곤 #40 L3: 피함(tg), 적 머리 경로 2칸 · 맨해튼 2칸(길이 3) → 박힘 r130 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_king:schooltime_b:A:2 · r157 · 드래곤 #2 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r159 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r56 · 드래곤 #12 L2: 피함(tg), 적 머리 경로 5칸 · 맨해튼 4칸(길이 4) → 박힘 r58 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trophy · 게임 exp/stack9l340-b-px4:proxy4_king:trophy:A:2 · r101 · 드래곤 #0 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r102 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack9l340-b-px4:proxy4_swarm:default:A:2 · r175 · 드래곤 #65 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r177 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Devil · 게임 exp/stack9l340-b-px4:proxy4_swarm:devil_b:A:2 · r45 · 드래곤 #4 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r47 박힘(상대 돌진), 상대 길이 4
- proxy4_swarm · Autarky · 게임 exp/stack9l340-b-px4:proxy4_swarm:autarky:A:2 · r145 · 드래곤 #6 L2: 위협 칸으로 감(tgx), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r146 박힘(상대 돌진), 상대 길이 2

## 모이기 시작 제한 (gx, stack4; 드래곤 단위)

- 이번: 드래곤 82 (표식 턴 534) · 몸(자손 포함) 끝까지 98% (기준 ≥80%) · 드래곤 자체 끝까지 생존 55% (참고) · 뒤에 희생 먹이기(feed)로 끝남 4
- 비교: 드래곤 89 (표식 턴 478) · 몸(자손 포함) 끝까지 97% (기준 ≥80%) · 드래곤 자체 끝까지 생존 43% (참고) · 뒤에 희생 먹이기(feed)로 끝남 7
- 상대별: proxy4_elim 20회 95% · proxy4_king 21회 100% · proxy4_swarm 41회 98%
- 지도별: Autarky 21회 95% · Default 2회 100% · Devil 5회 100% · Portals 28회 100% · Prisoners Dilemma (10) 13회 100% · Queen Of Spades 2회 50% · Slithery Fight 9회 100% · Trauma 2회 100%
- 국면별: r450+ 82회 98%

실패 사례 (2건 중 2건, 기보 확인용):
- proxy4_swarm · Autarky · 게임 exp/stack9l340-b-px4:proxy4_swarm:autarky:A:2 · r485 · 드래곤 #459 L12: gx 13턴 (r485–r497) → 죽음 r498 희생
- proxy4_elim · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_elim:queen_of_spades_b:A:2 · r479 · 드래곤 #125 L5: gx 9턴 (r479–r487) → 죽음 r491 갇힘, 상대 길이 15

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 290개 중 우리 팀 98% (지목한 아군 58%) · 상대 1% · 지목 아군 끝까지 생존 54% (그 뒤 죽은 원인: 갇힘 62, 아군 머리 8, 희생 14, 돌진 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 85% · 최종 왕 44% (최종 왕이 지목 아군의 자손 68%)
- 비교: 실행 100% · 떨군 진주 197개 중 우리 팀 98% (지목한 아군 64%) · 상대 2% · 지목 아군 끝까지 생존 33% (그 뒤 죽은 원인: 박힘(상대 돌진) 10, 희생 14, 갇힘 59) · 지목 아군의 몸(자손 포함)이 끝까지 삶 84% · 최종 왕 28% (최종 왕이 지목 아군의 자손 54%)
- 상대별: proxy4_elim 67회 99% · proxy4_king 54회 98% · proxy4_swarm 65회 97%
- 지도별: Autarky 63회 100% · Default 1회 100% · Portals 72회 97% · Schooltime 1회 100% · Slithery Fight 30회 93% · Trauma 19회 100%
- 국면별: r250-349 71회 99% · r350-449 98회 99% · r450+ 17회 88%

실패 사례 (4건 중 4건, 기보 확인용):
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r335 · 드래곤 #478 L4: #648(L8)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1; 지목 아군 r424 갇힘에 사망
- proxy4_swarm · Portals · 게임 exp/stack9l340-b-px4:proxy4_swarm:portals:B:2 · r482 · 드래곤 #569 L2: #607(L15)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_swarm:slithery_fight_b:B:2 · r382 · 드래곤 #894 L3: #562(L38)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1
- proxy4_elim · Portals · 게임 exp/stack9l340-b-px4:proxy4_elim:portals:A:2 · r485 · 드래곤 #554 L2: #575(L15)에게 희생 → 진주 1개 중 우리 0, 지목 아군 0, 상대 0

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 91% · 조각 30라운드 생존 42% · 30라운드 안 1개 이상 먹음 64% (살아서 먹음 27%) · 평생 먹은 진주 평균 2.7 · 나중에 아군을 먹임 36% (conv 8, feed 4, 분열 뒤 평균 33.4라운드) · 끝까지 생존 0% · 30라운드 안 죽은 원인: 희생 6, 갇힘 12, 아군 머리 1
- 비교: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 100% · 조각 30라운드 생존 80% · 30라운드 안 1개 이상 먹음 60% (살아서 먹음 60%) · 평생 먹은 진주 평균 4.8 · 나중에 아군을 먹임 40% (conv 1, feed 3, 분열 뒤 평균 45라운드) · 끝까지 생존 30% · 30라운드 안 죽은 원인: 갇힘 2
- 상대별: proxy4_elim 5회 0% · proxy4_king 13회 69% · proxy4_swarm 15회 53%
- 지도별: Autarky 6회 83% · Portals 22회 45% · Slithery Fight 5회 40%
- 국면별: r250-349 15회 60% · r350-449 18회 44%

실패 사례 (16건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r327 · 드래곤 #467 L9: 조각 L2 → 조각 죽음 r350 갇힘, 30라운드 안 먹은 진주 2
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r340 · 드래곤 #648 L8: 조각 L2 → 조각 죽음 r360 갇힘, 상대 길이 24, 30라운드 안 먹은 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack9l340-b-px4:proxy4_swarm:autarky:A:2 · r420 · 드래곤 #459 L7: 조각 L2 → 조각 죽음 r431 갇힘, 상대 길이 27, 30라운드 안 먹은 진주 1
- proxy4_swarm · Portals · 게임 exp/stack9l340-b-px4:proxy4_swarm:portals:A:2 · r277 · 드래곤 #330 L7: 조각 L2 → 조각 죽음 r302 갇힘, 30라운드 안 먹은 진주 1
- proxy4_swarm · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_swarm:slithery_fight_b:B:2 · r256 · 드래곤 #562 L32: 조각 L2 → 30라운드 생존, 먹은 진주 0 (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)
- proxy4_elim · Portals · 게임 exp/stack9l340-b-px4:proxy4_elim:portals:A:2 · r356 · 드래곤 #494 L7: 조각 L2 → 조각 죽음 r368 갇힘, 상대 길이 14, 30라운드 안 먹은 진주 0
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r374 · 드래곤 #515 L13: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:B:2 · r341 · 드래곤 #479 L7: 조각 L2 → 조각 죽음 r351 갇힘, 30라운드 안 먹은 진주 7
- proxy4_swarm · Portals · 게임 exp/stack9l340-b-px4:proxy4_swarm:portals:A:2 · r379 · 드래곤 #442 L15: 조각 L2 → 조각 죽음 r384 갇힘, 상대 길이 8, 30라운드 안 먹은 진주 0
- proxy4_swarm · Portals · 게임 exp/stack9l340-b-px4:proxy4_swarm:portals:A:2 · r393 · 드래곤 #466 L15: 조각 L2 → 조각 죽음 r413 갇힘, 30라운드 안 먹은 진주 1

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 2379개 (표식 턴 5900, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 92% (자연 진주 2, 이미 없음 183) · 사망 진주 2194개 중 우리가 먹음 83% · 상대 16% · 아무도 안 먹음 1% · 표적으로 삼은 드래곤이 먹음 68% · 우리가 먹기까지 평균 3.3라운드 · 상대 머리가 같거나 더 가까웠던 649개: 우리 57% 대 상대 42% · 박치기 진주 330개: 우리 52% 대 상대 48% · 우리 팀 사망 진주 83% · 사망 뒤 첫 표적까지 평균 1.3라운드
- 비교: 표적 진주 1924개 (표식 턴 4765, 진주당 드래곤 1.3) · 질량 장부의 사망 진주 92% (자연 진주 3, 이미 없음 148) · 사망 진주 1773개 중 우리가 먹음 82% · 상대 17% · 아무도 안 먹음 1% · 표적으로 삼은 드래곤이 먹음 68% · 우리가 먹기까지 평균 3.6라운드 · 상대 머리가 같거나 더 가까웠던 537개: 우리 54% 대 상대 46% · 박치기 진주 265개: 우리 50% 대 상대 50% · 우리 팀 사망 진주 84% · 사망 뒤 첫 표적까지 평균 1.4라운드
- 상대별: proxy4_elim 786회 82% · proxy4_king 806회 83% · proxy4_swarm 787회 83%
- 지도별: Autarky 354회 99% · Default 321회 77% · Devil 114회 56% · Portals 735회 99% · Prisoners Dilemma (10) 34회 32% · Queen Of Spades 100회 51% · Schooltime 71회 48% · Slithery Fight 349회 69% · Trauma 208회 89% · Trophy 93회 60%
- 국면별: r0-99 257회 68% · r100-249 617회 74% · r250-349 668회 86% · r350-449 709회 92% · r450+ 128회 83%

실패 사례 (377건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r74 · 드래곤 #0 L2: 진주 (16,2), 우리 머리 6칸 · 상대 머리 1칸, 박치기 4라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r72 · 드래곤 #0 L3: 진주 (12,13), 우리 머리 4칸 · 상대 머리 1칸, 박치기 5라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r351 · 드래곤 #448 L15: 진주 (27,5), 우리 머리 3칸 · 상대 머리 3칸, 우리 팀 사망 1라운드 뒤 → 아무도 안 먹음, 표식 2턴
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r456 · 드래곤 #6 L2: 진주 (17,5), 우리 머리 5칸 · 상대 머리 4칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (3라운드 뒤), 표식 1턴
- proxy4_king · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_king:queen_of_spades_b:B:2 · r112 · 드래곤 #3 L3: 진주 (18,1), 우리 머리 6칸 · 상대 머리 1칸, 상대 사망 3라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_king:schooltime_b:A:2 · r160 · 드래곤 #23 L2: 진주 (22,9), 우리 머리 4칸 · 상대 머리 2칸, 박치기 1라운드 뒤 → 상대가 먹음 (2라운드 뒤), 표식 2턴
- proxy4_king · Trauma · 게임 exp/stack9l340-b-px4:proxy4_king:trauma:A:2 · r225 · 드래곤 #25 L3: 진주 (15,4), 우리 머리 4칸 · 상대 머리 5칸, 우리 팀 사망 2라운드 뒤 → 아무도 안 먹음, 표식 5턴
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r4 · 드래곤 #25 L2: 진주 (33,5), 우리 머리 5칸 · 상대 머리 10칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (28라운드 뒤), 표식 1턴
- proxy4_king · Trophy · 게임 exp/stack9l340-b-px4:proxy4_king:trophy:A:2 · r103 · 드래곤 #2 L2: 진주 (14,23), 우리 머리 4칸 · 상대 머리 4칸, 박치기 1라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 2턴
- proxy4_swarm · Default · 게임 exp/stack9l340-b-px4:proxy4_swarm:default:A:2 · r14 · 드래곤 #2 L2: 진주 (2,30), 우리 머리 5칸 · 상대 머리 1칸, 박치기 3라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 979 (그중 통로 고리 세대 738, 판정에서 뺌) · 고리 밖 241: 처음 거리 평균 9.3 → 최소 4.8 · 3칸 안까지 감 37% · 희생까지 함 64% · 가는 길에 죽음 16% · 끝까지 생존 20%
- 비교: 모이기 드래곤 847 (그중 통로 고리 세대 654, 판정에서 뺌) · 고리 밖 193: 처음 거리 평균 10.4 → 최소 5.5 · 3칸 안까지 감 38% · 희생까지 함 55% · 가는 길에 죽음 22% · 끝까지 생존 22%
- 상대별: proxy4_elim 308회 86% · proxy4_king 308회 89% · proxy4_swarm 363회 83%
- 지도별: Autarky 380회 98% · Default 16회 57% · Devil 19회 50% · Portals 359회 90% · Prisoners Dilemma (10) 105회 0% · Queen Of Spades 12회 67% · Schooltime 4회 100% · Slithery Fight 40회 73% · Trauma 44회 82%
- 국면별: r250-349 135회 94% · r350-449 708회 89% · r450+ 136회 63%

실패 사례 (54건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r456 · 드래곤 #130 L4: 왕까지 거리 17 → 최소 15 (5턴)
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:B:2 · r412 · 드래곤 #470 L28: 왕까지 거리 11 → 최소 4 (21턴)
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r469 · 드래곤 #512 L4: 왕까지 거리 13 → 최소 6 (6턴)
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r415 · 드래곤 #567 L4: 왕까지 거리 5 → 최소 5 (4턴), 가는 길에 죽음 r419 갇힘, 상대 길이 12
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r479 · 드래곤 #6 L4: 왕까지 거리 15 → 최소 4 (8턴)
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r402 · 드래곤 #647 L4: 왕까지 거리 4 → 최소 4 (18턴), 가는 길에 죽음 r426 돌진, 상대 길이 9
- proxy4_king · Trauma · 게임 exp/stack9l340-b-px4:proxy4_king:trauma:B:2 · r388 · 드래곤 #275 L6: 왕까지 거리 7 → 최소 7 (3턴)
- proxy4_swarm · Devil · 게임 exp/stack9l340-b-px4:proxy4_swarm:devil_b:B:2 · r400 · 드래곤 #423 L6: 왕까지 거리 8 → 최소 8 (1턴), 가는 길에 죽음 r401 돌진, 상대 길이 25
- proxy4_swarm · Default · 게임 exp/stack9l340-b-px4:proxy4_swarm:default:B:2 · r358 · 드래곤 #180 L4: 왕까지 거리 5 → 최소 5 (1턴)
- proxy4_swarm · Portals · 게임 exp/stack9l340-b-px4:proxy4_swarm:portals:A:2 · r340 · 드래곤 #360 L10: 왕까지 거리 22 → 최소 4 (7턴), 가는 길에 죽음 r347 갇힘, 상대 길이 12

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 606개 중 우리 팀 88% (지목한 아군 56%) · 상대 3% · 지목 아군 끝까지 생존 66% (그 뒤 죽은 원인: 박힘(상대 돌진) 4, 갇힘 41, 아군 머리 6, 희생 24) · 지목 아군의 몸(자손 포함)이 끝까지 삶 87% · 최종 왕 54% (최종 왕이 지목 아군의 자손 66%)
- 비교: 실행 100% · 떨군 진주 448개 중 우리 팀 89% (지목한 아군 59%) · 상대 4% · 지목 아군 끝까지 생존 67% (그 뒤 죽은 원인: 희생 24, 갇힘 19, 박힘(상대 돌진) 4, 아군 머리 2) · 지목 아군의 몸(자손 포함)이 끝까지 삶 84% · 최종 왕 51% (최종 왕이 지목 아군의 자손 60%)
- 상대별: proxy4_elim 69회 94% · proxy4_king 72회 92% · proxy4_swarm 79회 85%
- 지도별: Autarky 74회 99% · Default 8회 50% · Devil 6회 83% · Portals 52회 96% · Queen Of Spades 8회 63% · Schooltime 7회 57% · Slithery Fight 23회 78% · Trauma 42회 93%
- 국면별: r250-349 9회 100% · r350-449 146회 95% · r450+ 65회 78%

실패 사례 (22건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r478 · 드래곤 #207 L13: #48(L18)에게 희생 → 진주 7개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r475 · 드래곤 #510 L4: #35(L7)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1
- proxy4_king · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_king:queen_of_spades_b:B:2 · r392 · 드래곤 #72 L4: #65(L5)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2
- proxy4_king · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_king:schooltime_b:B:2 · r444 · 드래곤 #36 L4: #8(L8)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1
- proxy4_king · Trauma · 게임 exp/stack9l340-b-px4:proxy4_king:trauma:A:2 · r376 · 드래곤 #4 L4: #185(L5)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r495 · 드래곤 #556 L10: #674(L38)에게 희생 → 진주 5개 중 우리 2, 지목 아군 2, 상대 0
- proxy4_swarm · Autarky · 게임 exp/stack9l340-b-px4:proxy4_swarm:autarky:A:2 · r498 · 드래곤 #459 L14: #271(L43)에게 희생 → 진주 7개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_swarm · Default · 게임 exp/stack9l340-b-px4:proxy4_swarm:default:B:2 · r395 · 드래곤 #22 L4: #180(L7)에게 희생 → 진주 2개 중 우리 1, 지목 아군 1, 상대 1
- proxy4_swarm · Portals · 게임 exp/stack9l340-b-px4:proxy4_swarm:portals:A:2 · r481 · 드래곤 #533 L5: #546(L6)에게 희생 → 진주 3개 중 우리 1, 지목 아군 1, 상대 0; 지목 아군 r487 희생에 사망
- proxy4_swarm · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_swarm:queen_of_spades_b:B:2 · r456 · 드래곤 #125 L4: #115(L8)에게 희생 → 진주 2개 중 우리 1, 지목 아군 0, 상대 1; 지목 아군 r457 갇힘에 사망

## 막다른 길 한입 (pocket-eat)

- 이번: 한입 100% · 2턴 안 분열 99% · 30라운드 뒤 가족 길이 변화 0.1 (줄지 않음 100%)
- 비교: 한입 100% · 2턴 안 분열 99% · 30라운드 뒤 가족 길이 변화 0.1 (줄지 않음 100%)
- 상대별: proxy4_elim 337회 99% · proxy4_king 338회 98% · proxy4_swarm 335회 99%
- 지도별: Devil 3회 0% · Portals 5회 60% · Prisoners Dilemma (10) 1002회 99%
- 국면별: r0-99 200회 100% · r100-249 300회 100% · r250-349 207회 99% · r350-449 199회 99% · r450+ 104회 92%

실패 사례 (11건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r465 · 드래곤 #509 L4: 한입, 분열(새끼 L3), 30라운드 뒤 가족 길이 변화 -4
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r360 · 드래곤 #521 L13: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 4
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_king:prisoners_dilemma_10:A:2 · r499 · 드래곤 #363 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_swarm:prisoners_dilemma_10:B:2 · r499 · 드래곤 #342 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_elim · Devil · 게임 exp/stack9l340-b-px4:proxy4_elim:devil_b:A:2 · r498 · 드래곤 #452 L18: 한입, 분열(새끼 L17), 30라운드 뒤 가족 길이 변화 -14
- proxy4_elim · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_elim:prisoners_dilemma_10:A:2 · r499 · 드래곤 #308 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:B:2 · r338 · 드래곤 #320 L4: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 2
- proxy4_king · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_king:prisoners_dilemma_10:B:2 · r499 · 드래곤 #355 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:B:2 · r333 · 드래곤 #478 L5: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 -5
- proxy4_swarm · Prisoners Dilemma (10) · 게임 exp/stack9l340-b-px4:proxy4_swarm:prisoners_dilemma_10:A:2 · r499 · 드래곤 #368 L12: 한입, 분열 없음, 30라운드 뒤 가족 길이 변화 1

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 22% · 30라운드 뒤 가족 길이 변화 8.3
- 비교: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 22% · 30라운드 뒤 가족 길이 변화 8.2
- 상대별: proxy4_elim 1239회 98% · proxy4_king 1232회 97% · proxy4_swarm 1284회 98%
- 지도별: Autarky 1529회 100% · Default 26회 88% · Devil 49회 90% · Portals 945회 95% · Prisoners Dilemma (10) 996회 100% · Queen Of Spades 12회 83% · Schooltime 3회 100% · Slithery Fight 78회 99% · Trauma 111회 88% · Trophy 6회 100%
- 국면별: r0-99 655회 100% · r100-249 1059회 98% · r250-349 878회 96% · r350-449 838회 98% · r450+ 325회 98%

실패 사례 (75건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r126 · 드래곤 #105 L4: 새끼 L2 → 새끼 죽음 r127 박힘(상대 돌진), 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:B:2 · r306 · 드래곤 #134 L4: 새끼 L2 → 새끼 죽음 r307 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r105 · 드래곤 #70 L9: 새끼 L7 → 새끼 죽음 r105 갇힘, 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -9
- proxy4_king · Trauma · 게임 exp/stack9l340-b-px4:proxy4_king:trauma:A:2 · r285 · 드래곤 #193 L7: 새끼 L5 → 새끼 죽음 r286 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r244 · 드래곤 #528 L8: 새끼 L6 → 새끼 죽음 r246 박힘(상대 돌진), 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -8
- proxy4_swarm · Autarky · 게임 exp/stack9l340-b-px4:proxy4_swarm:autarky:B:2 · r416 · 드래곤 #474 L4: 새끼 L2 → 새끼 죽음 r418 희생, 상대 길이 15, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Devil · 게임 exp/stack9l340-b-px4:proxy4_swarm:devil_b:B:2 · r399 · 드래곤 #411 L8: 새끼 L6 → 새끼 죽음 r401 돌진, 상대 길이 25, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -8
- proxy4_swarm · Default · 게임 exp/stack9l340-b-px4:proxy4_swarm:default:B:2 · r142 · 드래곤 #39 L4: 새끼 L2 → 새끼 죽음 r151 갇힘, 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Portals · 게임 exp/stack9l340-b-px4:proxy4_swarm:portals:A:2 · r252 · 드래곤 #263 L6: 새끼 L4 → 새끼 죽음 r252 갇힘, 상대 길이 10, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -6
- proxy4_swarm · Trauma · 게임 exp/stack9l340-b-px4:proxy4_swarm:trauma:A:2 · r230 · 드래곤 #103 L7: 새끼 L5 → 새끼 죽음 r231 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 86% · 그 밖(진짜로 갇힘) 537회
- 비교: 탈출 분열 뒤 남은 조각(고리의 일부) 89% · 그 밖(진짜로 갇힘) 433회
- 상대별: proxy4_elim 1308회 – · proxy4_king 1283회 – · proxy4_swarm 1332회 –
- 지도별: Autarky 1551회 – · Default 101회 – · Devil 50회 – · Portals 851회 – · Prisoners Dilemma (10) 1000회 – · Queen Of Spades 23회 – · Schooltime 13회 – · Slithery Fight 127회 – · Trauma 183회 – · Trophy 24회 –
- 국면별: r0-99 688회 – · r100-249 1191회 – · r250-349 942회 – · r350-449 785회 – · r450+ 317회 –

## 탈출 질주 3칸 (esc)

- 이번: 질주 100% · 짧은 적 머리 4칸 안 88% · 몸 생존 5라운드 97% · 10라운드 96% (드래곤 자체 85%) · 10라운드 길이 변화 -3.4
- 비교: 질주 100% · 짧은 적 머리 4칸 안 88% · 몸 생존 5라운드 99% · 10라운드 93% (드래곤 자체 85%) · 10라운드 길이 변화 -4
- 상대별: proxy4_elim 25회 92% · proxy4_king 27회 96% · proxy4_swarm 22회 100%
- 지도별: Default 11회 100% · Devil 9회 89% · Queen Of Spades 7회 100% · Schooltime 7회 100% · Slithery Fight 35회 94% · Trauma 1회 100% · Trophy 4회 100%
- 국면별: r0-99 8회 100% · r100-249 10회 90% · r250-349 11회 100% · r350-449 19회 100% · r450+ 26회 92%

실패 사례 (3건 중 3건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r474 · 드래곤 #510 L6: 질주 3칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r475 희생
- proxy4_elim · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_elim:slithery_fight_b:B:2 · r167 · 드래곤 #397 L6: 질주 3칸 (가장 가까운 짧은 적 머리 1칸) → 죽음 r168 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_elim:slithery_fight_b:B:2 · r470 · 드래곤 #351 L7: 질주 2칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r476 박힘(상대 돌진), 상대 길이 3

## 위협 피하기 2칸 질주

- 이번: 질주 100% · 몸 10라운드 생존 94% (드래곤 자체 88%)
- 비교: 질주 100% · 몸 10라운드 생존 93% (드래곤 자체 89%)
- 상대별: proxy4_elim 201회 94% · proxy4_king 190회 93% · proxy4_swarm 193회 94%
- 지도별: Autarky 18회 100% · Default 94회 89% · Devil 47회 91% · Portals 1회 100% · Prisoners Dilemma (10) 6회 100% · Queen Of Spades 83회 95% · Schooltime 83회 93% · Slithery Fight 188회 95% · Trauma 13회 92% · Trophy 51회 92%
- 국면별: r0-99 132회 96% · r100-249 186회 92% · r250-349 124회 92% · r350-449 128회 94% · r450+ 14회 93%

실패 사례 (38건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r344 · 드래곤 #152 L4: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 2) → 죽음 r346 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r420 · 드래곤 #484 L5: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 3) → 죽음 r422 희생
- proxy4_king · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_king:queen_of_spades_b:B:2 · r346 · 드래곤 #106 L3: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 3) → 죽음 r350 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r419 · 드래곤 #647 L4: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r426 돌진, 상대 길이 9
- proxy4_king · Trophy · 게임 exp/stack9l340-b-px4:proxy4_king:trophy:B:2 · r90 · 드래곤 #35 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r96 돌진, 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack9l340-b-px4:proxy4_swarm:default:A:2 · r12 · 드래곤 #6 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r22 갇힘, 상대 길이 2
- proxy4_swarm · Devil · 게임 exp/stack9l340-b-px4:proxy4_swarm:devil_b:A:2 · r47 · 드래곤 #8 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r51 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_swarm:queen_of_spades_b:A:2 · r297 · 드래곤 #103 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r302 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_swarm:schooltime_b:A:2 · r170 · 드래곤 #12 L8: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r171 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r264 · 드래곤 #457 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r271 박힘(상대 돌진), 상대 길이 4

## 포털 통과 (전체; PORTAL?=미탐색 출구)

- 이번: 미탐색 출구 1190회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 94% (드래곤 자체 79%) · 10라운드 90% · 10라운드 안 먹은 진주 0.9
- 비교: 미탐색 출구 1107회(몸 3라운드 생존 94%) · 전체 몸 생존 3라운드 94% (드래곤 자체 80%) · 10라운드 89% · 10라운드 안 먹은 진주 0.9
- 상대별: proxy4_elim 831회 93% · proxy4_king 983회 94% · proxy4_swarm 976회 95%
- 지도별: Autarky 478회 95% · Default 564회 95% · Portals 1183회 94% · Prisoners Dilemma (10) 39회 100% · Queen Of Spades 54회 70% · Schooltime 81회 95% · Slithery Fight 141회 95% · Trauma 246회 96% · Trophy 4회 75%
- 국면별: r0-99 376회 95% · r100-249 1021회 95% · r250-349 851회 94% · r350-449 458회 93% · r450+ 84회 92%

실패 사례 (164건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r82 · 드래곤 #14 L2: 포털 → 죽음 r82 돌진, 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:A:2 · r69 · 드래곤 #8 L9: 포털 → 죽음 r69 희생, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Portals · 게임 exp/stack9l340-b-px4:proxy4_king:portals:A:2 · r51 · 드래곤 #17 L3: 포털(미탐색 출구) → 죽음 r52 갇힘, 상대 길이 5, 10라운드 안 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_king:queen_of_spades_b:B:2 · r157 · 드래곤 #39 L2: 포털 → 죽음 r157 박힘(상대 돌진), 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_king:schooltime_b:B:2 · r385 · 드래곤 #128 L3: 포털(미탐색 출구) → 죽음 r386 돌진, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Trauma · 게임 exp/stack9l340-b-px4:proxy4_king:trauma:A:2 · r319 · 드래곤 #25 L3: 포털 → 죽음 r322 박힘(상대 돌진), 상대 길이 3, 10라운드 안 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r90 · 드래곤 #220 L6: 포털 → 죽음 r91 갇힘, 상대 길이 24, 10라운드 안 진주 0
- proxy4_swarm · Autarky · 게임 exp/stack9l340-b-px4:proxy4_swarm:autarky:A:2 · r69 · 드래곤 #8 L9: 포털 → 죽음 r69 희생, 상대 길이 2, 10라운드 안 진주 0
- proxy4_swarm · Default · 게임 exp/stack9l340-b-px4:proxy4_swarm:default:B:2 · r137 · 드래곤 #43 L2: 포털 → 죽음 r140 갇힘, 10라운드 안 진주 0
- proxy4_swarm · Portals · 게임 exp/stack9l340-b-px4:proxy4_swarm:portals:A:2 · r51 · 드래곤 #16 L3: 포털(미탐색 출구) → 죽음 r52 갇힘, 상대 길이 5, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 11, 경로 18) · 잡은 길이 ≥ 우리 100% · 두 몸의 진주 우리 56 대 상대 161
- 비교: 충돌 성사 100% (인접 12, 경로 17) · 잡은 길이 ≥ 우리 93% · 두 몸의 진주 우리 30 대 상대 154
- 상대별: proxy4_elim 5회 0% · proxy4_king 10회 30% · proxy4_swarm 14회 21%
- 지도별: Default 2회 50% · Devil 5회 0% · Queen Of Spades 6회 0% · Schooltime 3회 0% · Slithery Fight 12회 42% · Trauma 1회 0%
- 국면별: r0-99 1회 0% · r100-249 2회 50% · r250-349 6회 17% · r350-449 19회 21% · r450+ 1회 0%

실패 사례 (23건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r72 · 드래곤 #26 L2: 돌진 경로 1칸 → 상대 L3 잡음, 진주 우리 0 대 상대 3
- proxy4_king · Devil · 게임 exp/stack9l340-b-px4:proxy4_king:devil_b:A:2 · r478 · 드래곤 #502 L2: 돌진 경로 1칸 → 상대 L23 잡음, 진주 우리 5 대 상대 6
- proxy4_king · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_king:slithery_fight_b:A:2 · r276 · 드래곤 #122 L3: 돌진 경로 2칸 → 상대 L6 잡음, 진주 우리 1 대 상대 4
- proxy4_swarm · Devil · 게임 exp/stack9l340-b-px4:proxy4_swarm:devil_b:B:2 · r401 · 드래곤 #423 L6: 돌진 경로 3칸 → 상대 L25 잡음, 진주 우리 3 대 상대 13
- proxy4_swarm · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_swarm:queen_of_spades_b:B:2 · r297 · 드래곤 #1 L2: 돌진 경로 2칸 → 상대 L5 잡음, 진주 우리 0 대 상대 5
- proxy4_swarm · Schooltime · 게임 exp/stack9l340-b-px4:proxy4_swarm:schooltime_b:B:2 · r388 · 드래곤 #78 L3: 돌진 경로 2칸 → 상대 L8 잡음, 진주 우리 0 대 상대 6
- proxy4_swarm · Trauma · 게임 exp/stack9l340-b-px4:proxy4_swarm:trauma:A:2 · r426 · 드래곤 #216 L2: 돌진 경로 1칸 → 상대 L23 잡음, 진주 우리 4 대 상대 9
- proxy4_swarm · Slithery Fight · 게임 exp/stack9l340-b-px4:proxy4_swarm:slithery_fight_b:A:2 · r366 · 드래곤 #509 L2: 돌진 경로 2칸 → 상대 L11 잡음, 진주 우리 1 대 상대 7
- proxy4_elim · Devil · 게임 exp/stack9l340-b-px4:proxy4_elim:devil_b:A:2 · r419 · 드래곤 #441 L5: 돌진 경로 4칸 → 상대 L23 잡음, 진주 우리 6 대 상대 8
- proxy4_elim · Queen Of Spades · 게임 exp/stack9l340-b-px4:proxy4_elim:queen_of_spades_b:A:2 · r360 · 드래곤 #100 L4: 돌진 경로 2칸 → 상대 L5 잡음, 진주 우리 0 대 상대 5

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 비교: 먹음 100%
- 상대별: proxy4_elim 53회 100% · proxy4_king 46회 100% · proxy4_swarm 56회 100%
- 지도별: Autarky 8회 100% · Default 23회 100% · Devil 9회 100% · Portals 32회 100% · Queen Of Spades 23회 100% · Schooltime 6회 100% · Slithery Fight 33회 100% · Trauma 7회 100% · Trophy 14회 100%
- 국면별: r0-99 21회 100% · r100-249 42회 100% · r250-349 34회 100% · r350-449 50회 100% · r450+ 8회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 93%
- 비교: 그 턴 사망 0% · 10라운드 생존 92%
- 상대별: proxy4_elim 23회 – · proxy4_king 24회 – · proxy4_swarm 24회 –
- 지도별: Autarky 5회 – · Default 7회 – · Devil 2회 – · Queen Of Spades 14회 – · Schooltime 8회 – · Slithery Fight 31회 – · Trauma 2회 – · Trophy 2회 –
- 국면별: r0-99 11회 – · r100-249 21회 – · r250-349 14회 – · r350-449 22회 – · r450+ 3회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 비교: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 9회 – · proxy4_king 13회 – · proxy4_swarm 19회 –
- 지도별: Default 11회 – · Devil 13회 – · Queen Of Spades 1회 – · Schooltime 4회 – · Slithery Fight 5회 – · Trauma 4회 – · Trophy 3회 –
- 국면별: r0-99 6회 – · r100-249 23회 – · r250-349 9회 – · r350-449 3회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/stack9l340-b-px4` | 60 | 27 (0.45) | 52% | 0 (0.00) | 0 (0.00) | 6 | 20 | 1 | 1/4 (3.5) | 95 (1.58; 필사 16) | 18/38 (63) |
| 비교 `exp/stack8-b-px4` | 60 | 28 (0.47) | 64% | 0 (0.00) | 0 (0.00) | 4 | 23 | 1 | 2/5 (7) | 36 (0.60; 필사 72) | 14/43 (49) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.
- 이번 `exp/stack9l340-b-px4`: gx 표식 턴 534 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0
- 비교 `exp/stack8-b-px4`: gx 표식 턴 478 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/stack9l340-b-px4` | 60 | 35943 | 0.6% (209) | 18.2% (6525) | 3941 | 1.3% (51) | 2.4% (94) | 23.3% (920/3941) |
| 비교 `exp/stack8-b-px4` | 60 | 39000 | 0.8% (296) | 17.8% (6928) | 4423 | 1.3% (58) | 2.9% (129) | 26.2% (1160/4423) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/stack9l340-b-px4` | 전체 | 분열 | 4 (9%) | 14.5 | 102% | 95% | 1 | 0 |
| 이번 `exp/stack9l340-b-px4` | 전체 | 2칸 질주 | 7 (16%) | 10 | 126% | 120% | 3 | 0 |
| 이번 `exp/stack9l340-b-px4` | 전체 | 3칸 질주 | 9 (21%) | 10.1 | 69% | 51% | 2 | 1 |
| 이번 `exp/stack9l340-b-px4` | 전체 | 한 걸음 | 23 (53%) | 10.3 | 43% | 44% | 14 | 10 |
| 이번 `exp/stack9l340-b-px4` | 4칸 이상 | 분열 | 1 (6%) | 39 | 100% | 100% | 0 | 0 |
| 이번 `exp/stack9l340-b-px4` | 4칸 이상 | 2칸 질주 | 3 (18%) | 11.7 | 80% | 51% | 1 | 0 |
| 이번 `exp/stack9l340-b-px4` | 4칸 이상 | 3칸 질주 | 5 (29%) | 11.2 | 70% | 63% | 1 | 0 |
| 이번 `exp/stack9l340-b-px4` | 4칸 이상 | 한 걸음 | 8 (47%) | 11.8 | 40% | 35% | 4 | 3 |
| 비교 `exp/stack8-b-px4` | 전체 | 분열 | 6 (11%) | 17.7 | 107% | 103% | 4 | 0 |
| 비교 `exp/stack8-b-px4` | 전체 | 2칸 질주 | 18 (32%) | 11.4 | 89% | 82% | 5 | 1 |
| 비교 `exp/stack8-b-px4` | 전체 | 3칸 질주 | 9 (16%) | 10.6 | 92% | 83% | 1 | 0 |
| 비교 `exp/stack8-b-px4` | 전체 | 한 걸음 | 24 (42%) | 15 | 42% | 44% | 17 | 11 |
| 비교 `exp/stack8-b-px4` | 4칸 이상 | 분열 | 3 (10%) | 18.3 | 125% | 124% | 3 | 0 |
| 비교 `exp/stack8-b-px4` | 4칸 이상 | 2칸 질주 | 8 (28%) | 13.8 | 76% | 62% | 4 | 1 |
| 비교 `exp/stack8-b-px4` | 4칸 이상 | 3칸 질주 | 5 (17%) | 13 | 75% | 69% | 1 | 0 |
| 비교 `exp/stack8-b-px4` | 4칸 이상 | 한 걸음 | 13 (45%) | 15.2 | 34% | 38% | 11 | 7 |

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (95건 중 10건):
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r64 · 드래곤 #11 L3: v-1 → 갇힘, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r139 · 드래곤 #51 L3: v3 PORTAL? → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:A:2 · r278 · 드래곤 #62 L2: v-2.5 → 갇힘, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:A:2 · r69 · 드래곤 #8 L9: v-0.2 → 희생, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:A:2 · r250 · 드래곤 #136 L3: v8.4 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:A:2 · r315 · 드래곤 #61 L3: v8.2 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:A:2 · r338 · 드래곤 #112 L3: v9 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Autarky · 게임 exp/stack9l340-b-px4:proxy4_king:autarky:B:2 · r339 · 드래곤 #61 L2: v7.7 → 아군 머리, 막은 우리 드래곤 L3
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:B:2 · r174 · 드래곤 #29 L2: v7.2 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Default · 게임 exp/stack9l340-b-px4:proxy4_king:default:B:2 · r198 · 드래곤 #65 L15: v6.9 → 아군 머리, 막은 우리 드래곤 L2

## 지도·판본 인식 상세 (cand-mapid)

이번 (60판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 6 | 100% | 100% | 36/36 (36) | 1758 | 1758 (0) | 0 | 0 | 0 | 0 |
| Default a | 6 | 100% | 100% | 24/24 (24) | 254 | 254 (0) | 0 | 0 | 0 | 0 |
| Devil b | 6 | 100% | 100% | 18/18 (18) | 144 | 141 (0) | 2 | 0 | 0 | 17 |
| Portals a | 6 | 100% | 100% | 18/18 (18) | 1082 | 1082 (0) | 0 | 0 | 0 | 1 |
| Prisoners Dilemma b | 6 | 100% | 100% | 18/30 (18) | 1033 | 1029 (0) | 4 | 0 | 0 | 305 |
| Queen Of Spades b | 6 | 100% | 100% | 12/12 (12) | 92 | 92 (0) | 0 | 0 | 0 | 71 |
| Schooltime b | 6 | 100% | 100% | 36/36 (36) | 110 | 110 (0) | 0 | 0 | 0 | 7 |
| Slithery Fight b | 6 | 100% | 100% | 48/48 (48) | 297 | 289 (0) | 7 | 0 | 0 | 34 |
| Trauma a | 6 | 100% | 100% | 12/12 (12) | 311 | 311 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 6 | 100% | 100% | 12/12 (12) | 89 | 88 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 60/60, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

비교 (60판):

| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| Autarky a | 6 | 100% | 100% | 36/36 (36) | 1689 | 1689 (0) | 0 | 0 | 0 | 0 |
| Default a | 6 | 100% | 100% | 24/24 (24) | 203 | 203 (0) | 0 | 0 | 0 | 0 |
| Devil b | 6 | 100% | 100% | 18/18 (18) | 133 | 133 (0) | 0 | 0 | 0 | 17 |
| Portals a | 6 | 100% | 100% | 18/18 (18) | 1044 | 1044 (0) | 0 | 0 | 0 | 1 |
| Prisoners Dilemma b | 6 | 100% | 100% | 18/30 (18) | 1034 | 1031 (0) | 3 | 0 | 0 | 267 |
| Queen Of Spades b | 6 | 100% | 100% | 12/12 (12) | 75 | 75 (0) | 0 | 0 | 0 | 71 |
| Schooltime b | 6 | 100% | 100% | 36/36 (36) | 101 | 101 (0) | 0 | 0 | 0 | 7 |
| Slithery Fight b | 6 | 100% | 100% | 48/48 (48) | 281 | 273 (0) | 7 | 0 | 0 | 19 |
| Trauma a | 6 | 100% | 100% | 12/12 (12) | 250 | 250 (0) | 0 | 0 | 0 | 0 |
| Trophy a | 6 | 100% | 100% | 12/12 (12) | 96 | 93 (0) | 0 | 0 | 0 | 0 |

- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 60/60, 가릴 수 없음 0, 다름 0. 온라인 판은 자연 생성 방법만 쓴다.

### Schooltime 판의 경제 (bsp의 가설 수준 지표, 정답 판본별)

| 묶음 | 판본 | 판 | 드래곤 수 r50 | r100 | r0–99 자연 진주 먹음 | 전멸당함 | 끝 최장(전멸 0) | 판당 bsp 분열 |
|---|---|---:|---|---|---|---:|---|---:|
| 이번 | b | 6 | 8 [7, 8] | 11 [8, 12] | 13 [7, 17] | 0% | 14 [7, 14] | 8.8 |
| 비교 | b | 6 | 8 [7, 8] | 11 [8, 11] | 14 [10, 15] | 0% | 13 [6, 14] | 9.3 |

- 기준값(`research/experiments/cand-mapid.md`, 웨이브 전에 적음): b에서 드래곤 수 r50 중앙 ≥ 6, r0–99 자연 진주 중앙 ≥ 14. 우리 merge2 계열 b 29판은 3 · 9, 떼 계열(swarm8·px) b 14판은 6 · 14, 상위권 b 승자는 8 · 32다. a는 bsp가 켜지지 않는 대조군이다.

## stack5: 영토 덮기 (csplit · F · cov) 게이트와 가설 수준 지표

- 기준값은 `research/experiments/cand-stack5.md`(웨이브 전)에서, 상위권 승자(TW) 값과 merge2 값은 `research/observations/top-territory.md`에서 왔다. 정의는 영토 연구의 `exp/territory-analysis/extract.js`와 같다(영토 = 시작 몸에서 더 가까운 팀의 칸, 샘 = 그 판 판본 파일의 평균 간격 ≤12, 보로노이 = 용량 1/평균 간격 가중, 거리 = 지도 위 이동 거리, 몸은 무시).

### 게이트 (기능 적용)

| 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|
| csplit 발동: 500라운드형 지도 r0–249 판당 | ≥20 | 16.7 (전체 834회) | 16.7 (전체 822회) |
| csplit 설계 상황: 부모가 팀 최장(≥8)이 아님 | ≥90% | 100% | 100% |
| csplit 새끼가 30라운드 안에 자연 진주 ≥1개 | ≥45% (TW 47% · 45%) | 39% (834마리) | 40% (822마리) |
| csplit 새끼 30라운드 생존 | ≥30% (TW 34% · 51%) | 73% | 75% |
| F 목표(드래곤·샘) 수, 3걸음 안 도착 | – | 1009, 도착 60% | 1039, 도착 60% |
| F 설계 상황: 실제 우리 영토 샘, 처음 표식 때 다른 우리 머리 3걸음 안 없음 | ≥80% | 83% | 83% |
| F 도착 뒤 30라운드 그 무리 자연 진주의 우리 몫(합산) | ≥85% (TW 자기 샘 90%) | 90% (상대 9%, 2242개) | 89% (상대 9%, 2300개) |
| F 같은 몫의 지도 평균(지도마다 합산, 같은 무게, Portals 제외) | ≥85% | 64% (Autarky 0%, Devil 62%, Prisoners Dilemma (10) 100%, Trauma 94%, Slithery Fight 63%) | 54% (Autarky 0%, Devil 53%, Slithery Fight 68%, Trauma 94%) |
| cov 턴, 20라운드 안 우리 영토 자연 진주 | – | 32218, 20% | 0, – |

### 가설 수준 지표 (관찰; 500라운드형 / 전멸형)

| 지표 | 기준 | 상위권 승자 | merge2 | 이번 | 비교 |
|---|---|---|---|---|---|
| r100 우리 드래곤 수(r100까지 간 판) | ≥15 / ≥10 | 30 / 21 | 4 / 3 | 10.3 / 6.6 | 10.1 / 7 |
| r100 우리 영토 보로노이 몫(용량 가중, 판 평균) | ≥80% | 89% / 81% | 66% / 32% | 74% / 27% | 75% / 30% |
| r100 샘 지킴: 우리 영토 샘 중 우리 머리 3걸음 안(판 평균) | ≥50% | 61% / 55% | 22% / – | 32% / 34% | 32% / 28% |
| 우리 영토 자연 진주(r0부터 생성)를 상대가 먹은 몫(합산) | ≤25% | 11% / 16% | 56% / 55% | 49% / 65% | 49% / 65% |
| 우리 영토 샘 진주를 상대가 먹은 몫(합산) | ≤15% | 7% / 6% | 50% / 33% | 46% / 52% | 45% / 52% |

- 판 수(500라운드형 / 전멸형): 이번 30 / 30 · 비교 30 / 30. 판본 파일을 못 찾은 판: 이번 0 · 비교 0.

### 부작용: 우리 드래곤의 죽음 (판당; 전체 / r250 전)

| 원인 | 이번 | 비교 |
|---|---|---|
| 갇힘(빈 이웃 없음; 통로 고리의 남은 조각 포함) | 66.3 / 31.7 | 64.9 / 31.6 |
| 적 머리에 박힘 | 7.3 / 4.8 | 6.9 / 4.7 |
| 우리 드래곤끼리 머리 충돌(둘 다 죽음, 둘 다 셈) | 1.9 / 0.9 | 1.9 / 0.9 |

- 막힘에서 아군 머리를 피해 죽은 턴(no-exit s): 이번 108 · 비교 93

### 지도별 (이번)

| 지도 | 판 | csplit 판당 | 새끼 먹음 ≥1 | 새끼 30R 생존 | F 목표 · 도착 · 무리 진주 우리 몫 | r100 드래곤 | 보로노이 | 샘 지킴 | 상대가 먹은 영토 진주 | 상대가 먹은 샘 진주 |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| Autarky | 6 | 20.3 | 43% | 96% | 29 · 17% · 0% | 12.8 | 96% | 86% | 9% | 9% |
| Default | 6 | 25.7 | 36% | 66% | 0 · – · – | 9.5 | 27% | – | 75% | – |
| Devil | 6 | 10 | 22% | 77% | 77 · 51% · 62% | 7.5 | 26% | 18% | 82% | 85% |
| Portals | 6 | 13.5 | 41% | 59% | 563 · 77% · 99% | 11.7 | 100% | 31% | 0% | 0% |
| Prisoners Dilemma (10) | 6 | 1.2 | 0% | 71% | 13 · 8% · 100% | 3.8 | 47% | 50% | 25% | 0% |
| Queen Of Spades | 6 | 6.8 | 17% | 88% | 0 · – · – | 4.2 | 9% | – | 81% | – |
| Schooltime | 6 | 4.7 | 21% | 79% | 0 · – · – | 9.5 | 52% | – | 76% | – |
| Slithery Fight | 6 | 23.8 | 35% | 75% | 251 · 42% · 63% | 10.5 | 27% | 4% | 79% | 85% |
| Trauma | 6 | 21.2 | 53% | 56% | 76 · 28% · 94% | 7.2 | 96% | 6% | 50% | 2% |
| Trophy | 6 | 11.8 | 56% | 77% | 0 · – · – | 8.2 | 27% | – | 61% | – |

## stack7: 수 바닥 분열(floor)과 왕 길이 상한(kcap) 게이트, 저수 에피소드, 가설 수준 지표, 지도 가르기

- 기준값은 `research/experiments/cand-stack7.md`(웨이브 전)에서, 상위권·우리 값은 `research/observations/our-eliminations.md`(2.6절, 1.3절, 2.2절)에서 왔다. 저수 에피소드와 부류의 정의는 전멸 연구(`exp/eliminations/top.js` I, `lib.js` classOf)와 같다: r50부터 5라운드 간격으로 처음 우리 수 1–3·상대 ≥8인 라운드 r(라운드 첫 턴의 수; r+20이 판 안이고 우리 전멸 전), 그 뒤 [r, r+20) 분열, 20라운드 뒤 4마리 이상이면 회복, 50라운드 안 전멸. 연구의 분열 수는 10라운드 칸 두 개의 전체 분열(탈출 분열 포함)이고, 여기서는 [r, r+20)을 그대로 센다.

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| floor | 발동(판당; floor 지도 판) | – | 16 (0.4; 42판) | 35 (0.8; 42판) |
| floor | 1. 설계 상황: 발동 때 상대 ≥8마리 | ≥90% | 81% | 86% |
| floor | 저수 에피소드가 있는 floor 지도 판 · 그 20라운드 안 floor 발동이 있었던 판 | (관찰) | 30 · 0% | 36 · 17% |
| floor | 2. 즉시 효과 A: 에피소드 20라운드 비탈출 분열(판당; floor 지도) | ≥2.0 (상위 LX·LS 2.0, 우리 0.5) | 0.1 (floor 0, kcap 0, csplit 0.1, lsplit 0; 탈출 포함 전체 0.1) | 0.3 (floor 0.2, kcap 0, csplit 0.1; 탈출 포함 전체 0.5) |
| floor | 3. 즉시 효과 B: 에피소드 20라운드 뒤 4마리 이상(floor 지도) | ≥23% (상위 LX 23%, LS 26%, 우리 5%) | 10% (3/30) | 17% (6/36) |
| floor | 4. 즉시 효과 C: floor 새끼 30라운드 생존 | ≥34% (상위 패자 제 영토 새끼 34%, 승자 51%) | 63% (16마리) | 60% (35마리) |
| kcap | 발동(판당; kcap 지도 판) | – | 4 (0.1; 36판) | 1 (0; 36판) |
| kcap | 1. 설계 상황: 부모가 그 순간 팀 최장이고 r250 전 | ≥90% | 100% | 100% |
| kcap | 2. 즉시 효과: 새끼 10라운드 생존 | ≥74% (상위권 길이 4 분열 74.2%) | 100% (4마리) | 100% (1마리) |
| kcap | 2. 즉시 효과: 부모 10라운드 생존 | ≥55% (상위권 54.5%) | 0% | 0% |

### 저수 에피소드 (floor 지도 / 모든 지도; 판정은 floor 지도)

| 묶음 | 지도 | 판 | 에피소드 있음 | 처음 라운드(중앙) | 그때 우리 수 · 상대 수 | 그때 총길이 · 최장 | 20라운드 비탈출 분열 | floor · kcap | 탈출 포함 전체 | 20라운드 뒤 4마리 이상 | 50라운드 안 전멸 |
|---|---|---:|---:|---:|---|---|---:|---|---:|---:|---:|
| 이번 | floor 지도 | 42 | 71% | 235 | 3 · 32.8 | 11.8 · 5.9 | 0.1 | 0 · 0 | 0.1 | 10% | 10% |
| 이번 | floor 지도 중 전멸형 | 24 | 88% | 155 | 3 · 32.4 | 8.2 · 3.3 | 0.1 | 0 · 0 | 0.2 | 14% | 14% |
| 이번 | floor 지도 중 500형 | 18 | 50% | 455 | 3 · 33.9 | 20.2 · 11.8 | 0 | 0 · 0 | 0 | 0% | 0% |
| 이번 | 끄는 지도(Autarky·PD·Portals) | 18 | 56% | 207.5 | 3 · 16.8 | 31.7 · 20.5 | 0.3 | 0 · 0 | 8.5 | 30% | 0% |
| 이번 | 모든 지도 | 60 | 67% | 235 | 3 · 28.8 | 16.8 · 9.5 | 0.1 | 0 · 0 | 2.2 | 15% | 8% |
| 비교 | floor 지도 | 42 | 86% | 272.5 | 2.9 · 33.3 | 11 · 6.1 | 0.3 | 0.2 · 0 | 0.5 | 17% | 14% |
| 비교 | floor 지도 중 전멸형 | 24 | 100% | 175 | 2.9 · 33.8 | 8 · 3.8 | 0.4 | 0.2 · 0 | 0.5 | 17% | 21% |
| 비교 | floor 지도 중 500형 | 18 | 67% | 412.5 | 2.9 · 32.3 | 17.1 · 10.7 | 0.3 | 0.3 · 0 | 0.5 | 17% | 0% |
| 비교 | 끄는 지도(Autarky·PD·Portals) | 18 | 50% | 170 | 3 · 22.3 | 25.8 · 16 | 0.6 | 0 · 0 | 8.6 | 44% | 0% |
| 비교 | 모든 지도 | 60 | 75% | 240 | 2.9 · 31.1 | 14 · 8 | 0.4 | 0.2 · 0 | 2.1 | 22% | 11% |

- 상위권 기준(전멸 연구 2.6절, 전멸형): LX 72%가 그런 때를 겪고(처음 r105) 20라운드에 2.0번 나누며 23%가 회복, 42%가 50라운드 안 전멸. LS 69%, 2.0번, 26%, 0%. 우리 g4 LX 95%(r50), 0.5번, 5%, 15%.

### 가설 수준 지표 (관찰)

| 기능 | 지표 | 기준 | 상위권 · 이전 우리 | 이번 | 비교 |
|---|---|---|---|---|---|
| floor | r100 우리 드래곤 수(전멸형; 전멸은 0) — 전멸형 5지도 / PD 뺀 4지도 | ≥5.5 | 상위 LX 5.5, 우리 g4 LX 2.5 | 6.6 / 7.3 | 7 / 7.8 |
| floor | 전멸률(전멸형) | ≤66% | swarm8 66%, merge2 78% | 37% (11/30) / 46% (11/24) | 27% (8/30) / 33% (8/24) |
| floor | 전멸 라운드 중앙(전멸형) | ≥r235 | swarm8 235, merge2 150, stack1–3 163 | 208 / 208 | 216.5 / 216.5 |
| kcap | 우리 전멸 중 E2(왕 사냥) 비율(모든 지도) | ≤8% | 상위 LX 6%, 우리 16% | 8% (E1 0 · E2 1 · E3m 7 · E3l 4) | 0% (E1 0 · E2 0 · E3m 7 · E3l 1) |
| kcap | r50 우리 최장 평균(전멸형; 전멸은 0) — 5지도 / 4지도 | ≤4.5 | 상위 LS 3.8, 우리 g4 LX 6.8 | 5.7 / 3.9 | 5.6 / 3.8 |
| kcap | 전멸한 판의 길이 ≥8 죽음(판당; 모든 지도) | ≤0.4 | 우리 0.75 | 0.5 (12판) | 0.1 (8판) |

### 지도 가르기 (map= 표식으로 확인)

- floor는 Trophy, Queen Of Spades, Devil, Default, Schooltime, Trauma, Slithery Fight에서만, kcap은 그중 Slithery Fight를 뺀 여섯에서만 켠다. 봇은 프로세스마다 자기 창으로 지도 가족을 인식하고(`map=` 표식), 인식 전·`none`이면 끈다. "표식이 켜는 가족이 아닌 발동"은 발동한 프로세스의 마지막 `map=` 표식이 그 기능을 켜는 가족을 대지 않은 발동이다(0이어야 한다). "인식한 프로세스"는 마지막 표식이 그 판의 참 지도 가족을 댄 프로세스다.

| 묶음 | 지도(정답 판본) | 판 | floor 발동 | kcap 발동 | 표식이 켜는 가족이 아닌 발동 | 인식한 프로세스 |
|---|---|---:|---:|---:|---:|---:|
| 이번 | Autarky (끔) | 6 | 0 | 0 | 0 | 100% (1758/1758) |
| 이번 | Default | 6 | 0 | 2 | 0 | 100% (254/254) |
| 이번 | Devil b | 6 | 14 | 0 | 0 | 99% (143/144) |
| 이번 | Portals (끔) | 6 | 0 | 0 | 0 | 100% (1082/1082) |
| 이번 | Prisoners Dilemma (10) (끔) | 6 | 0 | 0 | 0 | 100% (1033/1033) |
| 이번 | Queen Of Spades b | 6 | 2 | 2 | 0 | 100% (92/92) |
| 이번 | Schooltime b | 6 | 0 | 0 | 0 | 100% (110/110) |
| 이번 | Slithery Fight b (kcap 끔) | 6 | 0 | 0 | 0 | 100% (296/297) |
| 이번 | Trauma | 6 | 0 | 0 | 0 | 100% (311/311) |
| 이번 | Trophy | 6 | 0 | 0 | 0 | 99% (88/89) |
| 비교 | Autarky (끔) | 6 | 0 | 0 | 0 | 100% (1689/1689) |
| 비교 | Default | 6 | 7 | 0 | 0 | 100% (203/203) |
| 비교 | Devil b | 6 | 10 | 0 | 0 | 100% (133/133) |
| 비교 | Portals (끔) | 6 | 0 | 0 | 0 | 100% (1044/1044) |
| 비교 | Prisoners Dilemma (10) (끔) | 6 | 0 | 0 | 0 | 100% (1034/1034) |
| 비교 | Queen Of Spades b | 6 | 8 | 1 | 0 | 100% (75/75) |
| 비교 | Schooltime b | 6 | 2 | 0 | 0 | 100% (101/101) |
| 비교 | Slithery Fight b (kcap 끔) | 6 | 4 | 0 | 0 | 100% (280/281) |
| 비교 | Trauma | 6 | 3 | 0 | 0 | 100% (250/250) |
| 비교 | Trophy | 6 | 1 | 0 | 0 | 97% (93/96) |

## stack8: 샘 목표 고르기(F2·F2p), 포털 출구의 아군(px2), 새끼의 몫(cl·ce)

- 기준값은 `research/experiments/cand-stack8.md`(로컬 확인 전, 18:20)에서 왔다. cl·ce의 기준값은 공급망 연구의 값(18:07)이다. F 목표(드래곤·샘 단위)와 포털 통과의 정의는 stack5 절과 "포털 통과" 절과 같다. Fp·cl·ce는 드래곤·진주 단위이고, 설계 상황은 처음 표식 때의 판이다.

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| F2 | 목표 수: F2 표식 / 모든 F(판당) | – | 1009 / 1009 (16.8) | 1039 / 1039 (17.3) |
| F2 | 1. 설계 상황: F2 표식 목표 (실제 샘 · 우리 영토 · 다른 머리 없음) | ≥90% | 83% (100% · 100% · 83%) | 83% (100% · 100% · 83%) |
| F2 | 1. 설계 상황: 모든 F 목표 | ≥80% | 83% | 83% |
| F2 | 2. 도착(3걸음 안): F2 표식 목표 / 모든 F | ≥80% | 60% / 60% | 60% / 60% |
| F2 | 3. 도착 뒤 30라운드 무리 자연 진주 우리 몫(F2 표식; 합산 · 지도 평균, Portals 제외) | ≥85% · ≥85% | 90% (2242개) · 64% | 89% (2300개) · 54% |
| F2 | 4. 겹친 추격: 다른 우리 드래곤의 같은 샘 목표와 겹침(F2 표식 / 모든 F) | ≤10% | 26% / 26% | 29% / 29% |
| F2p | Fp 진주 수(표식 턴) | – | 685 (2347턴) | 738 (2445턴) |
| F2p | 1. 설계 상황: 표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음 | ≥80% | 72% | 69% |
| F2p | 2. 즉시 효과: 그 드래곤이 10라운드 안에 먹음 · 상대가 먹음 | ≥48% · ≤5% | 35% · 20% | 33% · 23% |
| F2p | 끌어내기: F 표식 턴 가운데 유일하게 가장 가까운 자연 진주(7걸음 안, 무리 밖)에서 멀어진 턴 | ≤5% (관찰; W5+W6 15%) | 16% (후보가 있던 턴 29%; F 표식 턴 11006) | 16% (후보가 있던 턴 28%; F 표식 턴 11370) |
| px2 | 발동(px2 + px2x 턴, 판당) | – | 0 (0) | 402 (6.7) |
| px2 | 1. 설계 상황: 전 라운드 그 칸의 음파가 우리 드래곤에 멈춤 | ≥95% | – | 100% |
| px2 | 2. 즉시 효과 A: 건너지 않음(px2) | ≥80% | – | 36% |
| px2 | 3. 즉시 효과 B: 아군에 멈춘 탐침 뒤 아는 포털을 건너는 걸음에서 아군에 막혀 죽음(판당, v 무관) | ≤0.2 (W5–W7 0.69) | 0.97 (58건) | 0.93 (56건) |
| px2 | 보호: 포털 3라운드 몸 생존 | ≥95% | 94% | 94% |
| px2 | 보호: 건너는 걸음 아군 막힘 죽음(판당, 탐침·v 무관) | ≤0.75 (W5–W7 1.41) | 1.85 (111건) | 1.80 (108건) |
| cl | 진주 수(표식 턴) | – | 8218 (20588턴) | 7403 (18424턴) |
| cl | 설계 상황: 자연 진주, 우리 머리 가운데 표식한 조각만 가장 가까움 | ≥90% | 42% | 42% |
| cl | 즉시 효과: 조각이 먹음 · 우리 팀 · 우리 긴 드래곤 | ≥48% · ≥97% · ≤10% | 67% · 79% · 7% | 68% · 80% · 7% |
| ce | 진주 수(표식 턴) | – | 873 (1387턴) | 828 (1252턴) |
| ce | 설계 상황: 적 머리가 진주에서 우리 거리+1 안 | ≥80% | 82% | 81% |
| ce | 즉시 효과: 상대가 먹음 | ≤5% | 48% | 48% |
| ce | 보호: 표식 뒤 5라운드 안 박힘 | ≤19% | 7% | 5% |

- cl·ce의 가설 수준 지표(새끼 30라운드 먹음 ≥45%, 새끼 몫의 상대 몫 ≤3%/≤5%)는 공급망 스크립트 `exp/supply-chain/child_forage.js`로 잰다. 새끼 먹음은 stack5 절의 csplit 줄에도 있다.

### 포털 통과: 전 라운드 탐침(같은 칸, 같은 방향의 음파)별

| 묶음 | 출구 | 탐침 | 필사(v ≤ −20) | 통과 | 몸 3라운드 실패 | 건너는 걸음 아군 막힘 죽음 |
|---|---|---|---|---:|---:|---:|
| 이번 | 아는 포털 | clean | 아님 | 1145 | 4% | 21 |
| 이번 | 미탐색 | clean | 아님 | 919 | 3% | 16 |
| 이번 | 아는 포털 | ally | 아님 | 205 | 11% | 36 |
| 이번 | 미탐색 | clean | 필사 | 158 | 14% | 1 |
| 이번 | 아는 포털 | none | 아님 | 103 | 6% | 0 |
| 이번 | 아는 포털 | ally(머리) | 아님 | 73 | 18% | 22 |
| 이번 | 미탐색 | ally | 필사 | 44 | 11% | 2 |
| 이번 | 미탐색 | none | 필사 | 39 | 15% | 4 |
| 이번 | 아는 포털 | clean | 필사 | 36 | 8% | 1 |
| 이번 | 미탐색 | ally(머리) | 필사 | 21 | 33% | 8 |
| 이번 | 아는 포털 | enemy | 아님 | 19 | 16% | 0 |
| 이번 | 아는 포털 | enemy(머리) | 아님 | 17 | 0% | 0 |
| 이번 | 미탐색 | enemy(머리) | 필사 | 5 | 20% | 0 |
| 이번 | 미탐색 | enemy | 필사 | 4 | 25% | 0 |
| 이번 | 아는 포털 | none | 필사 | 1 | 0% | 0 |
| 이번 | 아는 포털 | ally | 필사 | 1 | 0% | 0 |
| 비교 | 아는 포털 | clean | 아님 | 1097 | 4% | 24 |
| 비교 | 미탐색 | clean | 아님 | 863 | 3% | 11 |
| 비교 | 아는 포털 | ally | 필사 | 179 | 13% | 30 |
| 비교 | 미탐색 | clean | 필사 | 140 | 13% | 2 |
| 비교 | 아는 포털 | none | 아님 | 126 | 4% | 0 |
| 비교 | 아는 포털 | ally(머리) | 필사 | 66 | 20% | 25 |
| 비교 | 미탐색 | none | 필사 | 39 | 18% | 6 |
| 비교 | 미탐색 | ally | 필사 | 35 | 26% | 3 |
| 비교 | 아는 포털 | clean | 필사 | 31 | 16% | 1 |
| 비교 | 아는 포털 | ally | 아님 | 30 | 0% | 1 |
| 비교 | 아는 포털 | enemy | 아님 | 21 | 10% | 0 |
| 비교 | 아는 포털 | enemy(머리) | 아님 | 15 | 0% | 0 |
| 비교 | 미탐색 | ally(머리) | 필사 | 14 | 29% | 5 |
| 비교 | 미탐색 | enemy | 필사 | 11 | 27% | 0 |
| 비교 | 미탐색 | enemy(머리) | 필사 | 5 | 20% | 0 |
| 비교 | 아는 포털 | none | 필사 | 2 | 50% | 0 |
| 비교 | 아는 포털 | ally(머리) | 아님 | 2 | 0% | 0 |

## stack9: 늦은 조각 풀 — 늦은 재분열(lsplit), frag 수 상한(fc), 영토 덮기 끌림(cov)

- 기준값은 `research/experiments/cand-stack9.md`(로컬 확인 결과를 보기 전, 21:04)에서, 상위권·우리 값은 `research/observations/supply-chain.md`(7절)에서 왔다. 가설 수준 지표는 그 연구의 코드(`exp/supply-chain/extract.js` analyse)를 같은 기보에 돌려 잰다. "판당"의 분모는 r250 뒤까지 간 우리 팀-경기다(500라운드형: Autarky, Portals, Schooltime, Slithery Fight, Trauma).

### 게이트 (기능 적용)

| 기능 | 지표 | 기준 | 이번 | 비교 |
|---|---|---|---|---|
| lsplit | 발동(모든 판당; 500라운드형 r250까지 간 판당) | – | 253 (4.2; 6) | 0 (0; 0) |
| lsplit | 1. 설계 상황: r250–429 · 부모 길이(분열 전) 4–6 · 우리 수(기보) < 목표 | ≥95% | 100% (100% · 100% · 100%; 표식의 수·목표 = 기보 100%) | – (– · – · –; 표식의 수·목표 = 기보 –) |
| lsplit | 2. 즉시 효과 A: 새끼가 30라운드 안에 자연 진주 ≥1 | ≥38% (승자의 늦은 2+2 새끼 38%) | 30% (253마리; 500형 31% · 전멸형 28%) | – (0마리; 500형 – · 전멸형 –) |
| lsplit | 3. 즉시 효과 B: 새끼가 죽을 때 떨군 진주의 우리 몫(합산) | ≥85% (승자 90%) | 78% (죽은 새끼 233마리, 진주 443개; ≥8 29% · 상대 14%) | – (죽은 새끼 0마리, 진주 0개; ≥8 – · 상대 –) |
| fc | 발동(판당) | – | 30 (0.5; frag 전체 33) | 0 (0; frag 전체 10) |
| fc | 1. 설계 상황: r250–420 · 부모가 팀 최장 아님 · 우리 수(기보) ≥ 옛 frag 상한 | ≥95% | 93% (100% · 93% · 100%) | – (– · – · –) |
| fc | 2. 즉시 효과 A: 조각 제 몫(S1: 30라운드 살며 1개 이상 먹거나, 뒤에 희생 표식으로 아군을 먹임) | ≥50% | 47% (30마리) | – (0마리) |
| fc | 3. 즉시 효과 B: 조각이 죽을 때 떨군 진주 중 우리 ≥8이 먹은 몫(합산) | ≥20% (승자 부모 5–7 늦은 새끼 20%) | 43% (죽은 조각 30마리, 진주 51개; 우리 90% · 상대 2%) | – (죽은 조각 0마리, 진주 0개; 우리 – · 상대 –) |
| cov | 창 수(표식 턴; 판당 창) | – | 3254 (32218턴; 54.2) | 0 (0턴; 0) |
| cov | 게이트: 창 30라운드 안에 그 드래곤이 우리 영토 자연 진주 ≥1 | ≥47% (승자 자기 영토 태생 조각 47%) | 27% (창 안에 죽음 25%) | – (창 안에 죽음 –) |
| cov | (관찰) 표식 턴의 끝 칸이 기보 영토의 우리 쪽: 창을 연 턴 / 모든 표식 턴 | – | 92% / 90% | – / – |
| cov | (참고) W5 정의: 표식 턴마다 20라운드 안에 우리 영토 자연 진주 | – | 20% | – |

### 가설 수준 지표 (관찰; 500라운드형 r250–499, r250 뒤까지 간 팀-경기당)

| 지표 | 기준 | 상위권 승자 · 패자 · stack5 · stack6 | 이번 | 비교 |
|---|---|---|---|---|
| lsplit: 조각 탄생(태어날 때 길이 ≤3; 모든 분열) | ≥50 | 156 · 135 · 8.7 · 7.1 | 10.8 (lsplit 6, frag 1.1, 탈출 분열 3.8, 그 밖 0) | 4.2 (lsplit 0, frag 0.2, 탈출 분열 3.7, 그 밖 0.3) |
| lsplit: conv 상태 에피소드 | ≥30 | 57.6 · 39.4 · 17.1 · 20.1 | 18.6 | 12.6 |
| lsplit · fc: conv형 진주(조각 → ≥8) | ≥12 (fc ≥9) | 22.9 · 14.8 · 6.5 · 5.4 | 5.8 | 4.4 |
| lsplit: 조각 → 조각 희생 진주 | ≥10 | 34.9 · 28.6 · 2.0 · 2.0 | 4.1 | 1.1 |
| fc: frag 새끼(r250–499) | ≥3 | (부모 5–7·8+ 36) · – · 0.4 · 0.9 | 1.1 | 0.2 |
| (관찰) r350 우리 조각 수(길이 ≤4; r350까지 간 판 평균) | – | 30.5 · – · 6.2 · – | 10.2 | 5 |
| (참고) 전멸형: 조각 탄생 · conv 상태 에피소드 · conv형 진주 · 조각 → 조각 | – | 68 · 17.3 · – · – | 4.5 · 0.3 · 0 · 0.7 | 1.9 · 1.3 · 0.6 · 0.7 |
| cov: r100 우리 영토에서 적이 더 가까운 몫(판 평균; 500형 / 전멸형) | ≤17% (500형) | 11% · 17% · 27% · 25% | 25% / 72% | 24% / 69% |
| cov: r100 자기 영토 보로노이(판 평균; 500형 / 전멸형) | ≥80% | 89% · 83% · 72% · 74% | 74% / 27% | 75% / 30% |
| cov: 우리 영토 자연 진주를 상대가 먹은 몫(합산; 500형 / 전멸형) | ≤25% | 11% / 16% (승자) | 49% / 65% | 49% / 65% |

- 판 수(r250 뒤까지 간 팀-경기; 500라운드형 / 전멸형): 이번 30 / 24 · 비교 30 / 24. 공급 사슬 재구성 점검이 0이 아닌 판: 이번 0 · 비교 0; 지표 계산 오류: 이번 0 · 비교 0.

### 부작용 (관찰; 판정에 쓰지 않음)

| 항목 | 이번 | 비교 |
|---|---|---|
| lsplit 새끼의 끝: 끝까지 삶 · 표식 희생(conv·feed) · 그 밖 희생 · 갇힘 · 박힘 · 아군 머리 · 그 밖 | 8% · 38% · 0% · 34% · 12% · 4% · 4% (253마리) | – |
| 어린 조각 규칙(20라운드): lsplit 새끼가 20라운드 안에 끝남(갇힘 · 박힘 · 희생 · 그 밖) / 뒤에 conv·feed로 아군을 먹임(그때 나이 중앙) | 22% (38 · 9 · 2 · 6) / 38% (95) | – |
| lsplit 부모: 10라운드 생존 · 부모 몸(새끼 포함) 30라운드 뒤 길이 변화 평균 · 부모가 죽을 때 떨군 진주 우리 몫 | 82% · 2.9 · 77% (401개) | – |
| lsplit 모이기 창(r340 뒤) 발동 · 그 새끼 30라운드 안 자연 진주 ≥1 | 0 · – | 0 · – |
| 우리 드래곤의 죽음 r250 뒤(판당): 갇힘 · 적 머리에 박힘 · 우리끼리 머리 충돌(둘 다 셈) | 34.7 · 2.5 · 1 | 33.3 · 2.2 · 1 |
| 모이기(g) 드래곤(통로 고리 밖): 수 · 왕 3칸 안까지 감 · 희생까지 함 · 가는 길에 죽음 | 241 · 37% · 64% · 16% | 193 · 38% · 55% · 22% |
| 희생 먹이기(feed) · conv: 판당 발동, 떨군 진주 우리 몫 | feed 3.7, 88% · conv 3.1, 98% | feed 2.5, 89% · conv 2.1, 98% |
| 끝 왕 길이(500라운드형 끝까지 간 판) | 25.4 (29판) | 23.4 (30판) |

