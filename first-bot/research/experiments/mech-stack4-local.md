# 구현 적용 확인

- 대상: `exp/stack4-a-px4` 60판 · 비교: `exp/stack3-a-px4` 60판
- 기준(사용자 규칙 2026-09-30): 승률이 아니라, 봇에 구현한 기능이 이 상대들에게 실제로 발동하고 의도대로 작동했는지를 본다.
- "의도대로"의 정의: 모이기=왕 3칸 안까지 가거나 희생까지 함 · 희생=떨군 진주 절반 이상을 우리 팀이 먹고 상대는 못 먹음 · 한입=2턴 안 분열하고 30라운드 뒤 가족 길이가 줄지 않음 · 탈출 분열=10라운드 뒤 몸이 살아 있음 · 정책 분열=새끼 30라운드 생존 · 탈출 질주·위협 피하기=10라운드 뒤 몸 생존 · 포털=3라운드 뒤 몸 생존 · 돌진=충돌 성사, 잡은 길이 ≥ 우리, 두 몸의 진주를 우리가 더 먹음 · 먹이 질주=진주 먹음.
- "몸"은 그 드래곤과 그 뒤 분열로 태어난 자손 전체다. 통로 고리처럼 몸을 새끼에게 넘기며 버티는 경우를 손실로 세지 않기 위해서다.
- stack2의 "의도대로": 조각 떼기=조각이 30라운드 살며 진주를 1개 이상 먹거나, 나중에 희생(feed·conv)으로 아군을 먹임 · 새 사망 진주 줍기=표적이 된 사망 진주(진주 하나가 한 건)를 우리 팀이 먹음(자연 진주로 오인했거나 이미 없던 표적은 판정에서 뺌).
- stack4의 "의도대로": tg=표식 턴 뒤 2라운드 안에 박히지 않음 · 몰렸을 때 분열=10라운드 뒤 몸이 살아 있음(보존율은 효과 줄) · px=그 턴에 우리 드래곤과 부딪혀 죽지 않음 · gx=그 드래곤이 끝까지 삶.

## 요약

| 기능 | 발동(판당) | 의도대로 | 비교: 발동(판당) | 비교: 의도대로 |
|---|---:|---:|---:|---:|
| 위협 모형 빈틈 (tg, stack4) | 3675 (61.3) | 98% | 0 (0) | – |
| 몰렸을 때 분열 (esc-split, stack4) | 26 (0.4) | 100% | 0 (0) | – |
| 포털 출구 혼잡 피하기 (px, stack4) | 113 (1.9) | 91% | 0 (0) | – |
| 모이기 시작 제한 (gx, stack4; 드래곤 단위) | 41 (0.7) | 63% | 0 (0) | – |
| 큰 아군 곁 희생 (conv, stack1 M1) | 99 (1.7) | 99% | 66 (1.1) | 98% |
| 조각 떼기 (split frag, stack2 S1) | 69 (1.2) | 80% | 84 (1.4) | 76% |
| 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위) | 733 (12.2) | 81% | 552 (9.2) | 75% |
| 왕에게 모이기 (g, 드래곤 단위) | 422 (7) | 77% | 385 (6.4) | 78% |
| 희생 먹이기 (feed) | 62 (1) | 85% | 54 (0.9) | 80% |
| 막다른 길 한입 (pocket-eat) | 1 (0) | 0% | 0 (0) | – |
| 탈출 분열 (escape-split) | 3507 (58.5) | 98% | 3398 (56.6) | 99% |
| 출구 없음 (no-exit) | 3354 (55.9) | – | 3290 (54.8) | – |
| 정책 분열 (split) | 64 (1.1) | 72% | 69 (1.2) | 65% |
| 탈출 질주 3칸 (esc) | 96 (1.6) | 94% | 73 (1.2) | 96% |
| 위협 피하기 2칸 질주 | 417 (7) | 95% | 479 (8) | 89% |
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 1030 (17.2) | 96% | 854 (14.2) | 96% |
| 돌진 (TRADE) | 21 (0.4) | 48% | 16 (0.3) | 25% |
| 먹이 질주 (2칸 이상, 먹은 것) | 88 (1.5) | 100% | 82 (1.4) | 100% |
| 기타 2칸 질주 | 53 (0.9) | – | 6 (0.1) | – |
| 마지막 돌진 (last-trade) | 11 (0.2) | – | 7 (0.1) | – |

- 건강: 턴 88178, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 비교 건강: 턴 83584, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 4392턴 · 끝판(late) 3395턴 · 돌진 신뢰(T, 탈출 끔) 1턴, 그 직후 박혀 죽음 0

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 비교 |
|---|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 3% (22/716턴) | 2% (11/692턴) |
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 19.9칸 (4.7회), 진주 우리 93% · 상대 2% | 15.2칸 (3.5회), 진주 우리 94% · 상대 2% |
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 0칸 (판당 0.00회) | 1.1칸 (판당 0.03회) |
| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | 20% (716/3593턴) | 19% (624/3229턴) |
| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | 판당 0.017회 (1건, 24칸) | 판당 0.033회 (2건, 50칸) |
| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | 4.2마리 (28판) | 4마리 (26판) |
| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | 15.6회 | 13.8회 |
| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | 62% (우리 31%) | 63% (우리 30%) |
| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | 우리 5.9 대 상대 11 (4회) · 박힌 교환의 우리 몫 28% (94회) | 우리 4.1 대 상대 14.9 (3.9회) · 박힌 교환의 우리 몫 23% (100회) |
| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | 5.5개 | 3.5개 |

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).
H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.

## 위협 모형 빈틈 (tg, stack4)

- 이번: 피함(tg) 63% · 위협 칸으로 감(tgx) 1355턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) 99% · 2라운드 안 박히지 않음 98% (tg 99%, tgx 97%) · 길이별 L2-5 3184 · L6-9 272 · L10+ 219
- 상대별: proxy4_elim 1099회 98% · proxy4_king 1217회 98% · proxy4_swarm 1359회 99%
- 지도별: Autarky 592회 97% · Default 685회 98% · Devil 224회 99% · Portals 1회 100% · Prisoners Dilemma 4회 100% · Queen Of Spades 428회 99% · Schooltime 579회 98% · Slithery Fight 802회 98% · Trauma 49회 96% · Trophy 311회 98%
- 국면별: r0-99 1097회 99% · r100-249 1501회 97% · r250-349 685회 98% · r350-449 296회 99% · r450+ 96회 100%

실패 사례 (68건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack4-a-px4:proxy4_king:default:A:1 · r109 · 드래곤 #6 L14: 위협 칸으로 감(tgx), 적 머리 경로 5칸 · 맨해튼 3칸(길이 3) → 박힘 r110 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Devil · 게임 exp/stack4-a-px4:proxy4_king:devil:B:1 · r50 · 드래곤 #15 L2: 피함(tg), 적 머리 경로 5칸 · 맨해튼 3칸(길이 2) → 박힘 r52 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Autarky · 게임 exp/stack4-a-px4:proxy4_king:autarky:B:1 · r158 · 드래곤 #7 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r160 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trauma · 게임 exp/stack4-a-px4:proxy4_king:trauma:B:1 · r158 · 드래곤 #1 L4: 피함(tg), 적 머리 경로 2칸 · 맨해튼 2칸(길이 2) → 박힘 r158 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Schooltime · 게임 exp/stack4-a-px4:proxy4_king:schooltime:B:1 · r142 · 드래곤 #3 L5: 피함(tg), 적 머리 경로 5칸 · 맨해튼 5칸(길이 2) → 박힘 r144 박힘(상대 돌진), 상대 길이 4
- proxy4_king · Trophy · 게임 exp/stack4-a-px4:proxy4_king:trophy:A:1 · r129 · 드래곤 #0 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 2) → 박힘 r131 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:A:1 · r59 · 드래곤 #12 L10: 위협 칸으로 감(tgx), 적 머리 경로 5칸 · 맨해튼 3칸(길이 3) → 박힘 r60 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack4-a-px4:proxy4_swarm:default:A:1 · r125 · 드래곤 #4 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r127 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Autarky · 게임 exp/stack4-a-px4:proxy4_swarm:autarky:B:1 · r370 · 드래곤 #3 L2: 위협 칸으로 감(tgx), 적 머리 경로 3칸 · 맨해튼 3칸(길이 3) → 박힘 r371 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Devil · 게임 exp/stack4-a-px4:proxy4_swarm:devil:B:1 · r121 · 드래곤 #96 L3: 피함(tg), 적 머리 경로 5칸 · 맨해튼 4칸(길이 2) → 박힘 r123 박힘(상대 돌진), 상대 길이 4

## 몰렸을 때 분열 (esc-split, stack4)

- 이번: 분열 100% · 설계 상황(몰림: 한 걸음이 모두 짧은 적 머리 사정 안) 88% · 꼬리가 적 머리에서 4칸 이상 62% · 몸 길이 보존 +10 92% · +30 89% (기준 ≥85%) · 10라운드 안 몸 잃음 0% (기준 ≤10%) · 새끼 10라운드 생존 92%
- 상대별: proxy4_elim 6회 100% · proxy4_king 12회 100% · proxy4_swarm 8회 100%
- 지도별: Default 3회 100% · Devil 2회 100% · Queen Of Spades 2회 100% · Schooltime 2회 100% · Slithery Fight 12회 100% · Trauma 5회 100%
- 국면별: r0-99 1회 100% · r100-249 10회 100% · r250-349 9회 100% · r350-449 5회 100% · r450+ 1회 100%

## 포털 출구 혼잡 피하기 (px, stack4)

- 이번: 피함(px) 16% · 붐비는 출구로 넘음(pxx) 95턴 · 그 턴 우리 드래곤과 충돌 사망 10 (px 0, pxx 10) · 몸 3라운드 생존 92% (보호 지표인 포털 통과 판당·통과 뒤 3라운드 몸 생존은 "포털 통과" 행, 넘는 걸음 죽음은 stack4 가설 지표 절)
- 상대별: proxy4_elim 48회 94% · proxy4_king 35회 86% · proxy4_swarm 30회 93%
- 지도별: Autarky 8회 100% · Default 11회 91% · Portals 46회 93% · Prisoners Dilemma 3회 100% · Queen Of Spades 1회 100% · Slithery Fight 42회 90% · Trauma 2회 0%
- 국면별: r0-99 15회 100% · r100-249 44회 89% · r250-349 31회 90% · r350-449 16회 94% · r450+ 7회 86%

실패 사례 (10건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack4-a-px4:proxy4_king:portals:A:1 · r259 · 드래곤 #265 L9: 붐비는 출구로 넘음(pxx) → 그 턴 사망 r259 갇힘, 상대 길이 15
- proxy4_king · Trauma · 게임 exp/stack4-a-px4:proxy4_king:trauma:B:1 · r128 · 드래곤 #12 L7: 붐비는 출구로 넘음(pxx) → 그 턴 사망 r128 갇힘, 상대 길이 4
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:A:1 · r264 · 드래곤 #460 L3: 붐비는 출구로 넘음(pxx) → 그 턴 사망 r264 갇힘, 상대 길이 22
- proxy4_swarm · Default · 게임 exp/stack4-a-px4:proxy4_swarm:default:B:1 · r129 · 드래곤 #32 L2: 붐비는 출구로 넘음(pxx) → 그 턴 사망 r129 희생, 상대 길이 13
- proxy4_swarm · Trauma · 게임 exp/stack4-a-px4:proxy4_swarm:trauma:B:1 · r128 · 드래곤 #12 L7: 붐비는 출구로 넘음(pxx) → 그 턴 사망 r128 갇힘, 상대 길이 4
- proxy4_elim · Portals · 게임 exp/stack4-a-px4:proxy4_elim:portals:A:1 · r454 · 드래곤 #461 L9: 붐비는 출구로 넘음(pxx) → 그 턴 사망 r454 갇힘, 상대 길이 17
- proxy4_elim · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_elim:slithery_fight:B:1 · r138 · 드래곤 #283 L10: 붐비는 출구로 넘음(pxx) → 그 턴 사망 r138 갇힘, 상대 길이 18
- proxy4_king · Portals · 게임 exp/stack4-a-px4:proxy4_king:portals:A:1 · r413 · 드래곤 #432 L9: 붐비는 출구로 넘음(pxx) → 그 턴 사망 r413 갇힘, 상대 길이 21
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:A:1 · r271 · 드래곤 #321 L9: 붐비는 출구로 넘음(pxx) → 그 턴 사망 r271 갇힘, 상대 길이 22
- proxy4_elim · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_elim:slithery_fight:B:1 · r162 · 드래곤 #7 L9: 붐비는 출구로 넘음(pxx) → 그 턴 사망 r162 갇힘, 상대 길이 18

## 모이기 시작 제한 (gx, stack4; 드래곤 단위)

- 이번: 드래곤 41 (표식 턴 218) · 끝까지 생존 63% (기준 ≥80%) · 몸(자손 포함) 끝까지 98% · 뒤에 희생 먹이기(feed)로 끝남 2
- 상대별: proxy4_elim 7회 100% · proxy4_king 12회 92% · proxy4_swarm 22회 36%
- 지도별: Autarky 13회 23% · Default 5회 100% · Portals 10회 80% · Queen Of Spades 2회 50% · Schooltime 3회 67% · Slithery Fight 8회 88%
- 국면별: r450+ 41회 63%

실패 사례 (15건 중 10건, 기보 확인용):
- proxy4_king · Queen Of Spades · 게임 exp/stack4-a-px4:proxy4_king:queen_of_spades:A:1 · r494 · 드래곤 #144 L4: gx 2턴 (r494–r495) → 죽음 r498 희생
- proxy4_swarm · Autarky · 게임 exp/stack4-a-px4:proxy4_swarm:autarky:B:1 · r477 · 드래곤 #496 L15: gx 1턴 (r477–r477) → 죽음 r480 갇힘
- proxy4_swarm · Portals · 게임 exp/stack4-a-px4:proxy4_swarm:portals:A:1 · r484 · 드래곤 #480 L20: gx 2턴 (r484–r485) → 죽음 r490 갇힘
- proxy4_swarm · Schooltime · 게임 exp/stack4-a-px4:proxy4_swarm:schooltime:A:1 · r481 · 드래곤 #201 L6: gx 12턴 (r481–r492) → 죽음 r495 갇힘, 상대 길이 34
- proxy4_swarm · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_swarm:slithery_fight:A:1 · r494 · 드래곤 #1057 L11: gx 2턴 (r494–r495) → 죽음 r499 돌진, 상대 길이 31
- proxy4_swarm · Autarky · 게임 exp/stack4-a-px4:proxy4_swarm:autarky:B:1 · r479 · 드래곤 #498 L15: gx 1턴 (r479–r479) → 죽음 r482 갇힘
- proxy4_swarm · Autarky · 게임 exp/stack4-a-px4:proxy4_swarm:autarky:B:1 · r480 · 드래곤 #499 L14: gx 2턴 (r480–r481) → 죽음 r484 갇힘
- proxy4_swarm · Autarky · 게임 exp/stack4-a-px4:proxy4_swarm:autarky:B:1 · r482 · 드래곤 #501 L14: gx 2턴 (r482–r483) → 죽음 r486 갇힘
- proxy4_swarm · Autarky · 게임 exp/stack4-a-px4:proxy4_swarm:autarky:B:1 · r484 · 드래곤 #503 L14: gx 2턴 (r484–r485) → 죽음 r488 갇힘
- proxy4_swarm · Autarky · 게임 exp/stack4-a-px4:proxy4_swarm:autarky:B:1 · r486 · 드래곤 #504 L14: gx 2턴 (r486–r487) → 죽음 r490 갇힘

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 149개 중 우리 팀 97% (지목한 아군 71%) · 상대 1% · 지목 아군 끝까지 생존 39% (그 뒤 죽은 원인: 희생 19, 박힘(상대 돌진) 4, 갇힘 35, 돌진 1, 아군 머리 1) · 지목 아군의 몸(자손 포함)이 끝까지 삶 80% · 최종 왕 18% (최종 왕이 지목 아군의 자손 42%)
- 비교: 실행 100% · 떨군 진주 92개 중 우리 팀 99% (지목한 아군 78%) · 상대 1% · 지목 아군 끝까지 생존 42% (그 뒤 죽은 원인: 갇힘 27, 박힘(상대 돌진) 5, 희생 5, 아군 머리 1) · 지목 아군의 몸(자손 포함)이 끝까지 삶 89% · 최종 왕 30% (최종 왕이 지목 아군의 자손 53%)
- 상대별: proxy4_elim 42회 98% · proxy4_king 27회 100% · proxy4_swarm 30회 100%
- 지도별: Autarky 11회 100% · Default 3회 100% · Portals 23회 100% · Prisoners Dilemma 3회 100% · Queen Of Spades 1회 100% · Schooltime 12회 100% · Slithery Fight 41회 98% · Trauma 5회 100%
- 국면별: r250-349 47회 98% · r350-449 46회 100% · r450+ 6회 100%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_elim · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_elim:slithery_fight:A:1 · r316 · 드래곤 #667 L3: #27(L8)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 2; 지목 아군 r367 희생에 사망

## 조각 떼기 (split frag, stack2 S1)

- 이번: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 96% · 조각 30라운드 생존 65% · 30라운드 안 1개 이상 먹음 55% (살아서 먹음 35%) · 평생 먹은 진주 평균 4.1 · 나중에 아군을 먹임 64% (conv 30, feed 14, 분열 뒤 평균 46.2라운드) · 끝까지 생존 12% · 30라운드 안 죽은 원인: 희생 16, 돌진 1, 갇힘 7
- 비교: 분열 100% · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) 98% · 조각 30라운드 생존 68% · 30라운드 안 1개 이상 먹음 43% (살아서 먹음 31%) · 평생 먹은 진주 평균 2.8 · 나중에 아군을 먹임 64% (conv 38, feed 16, 분열 뒤 평균 55.2라운드) · 끝까지 생존 12% · 30라운드 안 죽은 원인: 희생 17, 갇힘 8, 박힘(상대 돌진) 2
- 상대별: proxy4_elim 24회 71% · proxy4_king 25회 80% · proxy4_swarm 20회 90%
- 지도별: Autarky 20회 100% · Default 1회 0% · Portals 6회 67% · Prisoners Dilemma 3회 67% · Schooltime 4회 75% · Slithery Fight 28회 71% · Trauma 7회 86%
- 국면별: r250-349 45회 84% · r350-449 24회 71%

실패 사례 (14건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack4-a-px4:proxy4_king:portals:B:1 · r373 · 드래곤 #392 L8: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack4-a-px4:proxy4_king:prisoners_dilemma:B:1 · r356 · 드래곤 #215 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:B:1 · r261 · 드래곤 #321 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_swarm · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_swarm:slithery_fight:A:1 · r361 · 드래곤 #10 L12: 조각 L2 → 조각 죽음 r374 갇힘, 상대 길이 12, 30라운드 안 먹은 진주 0
- proxy4_elim · Default · 게임 exp/stack4-a-px4:proxy4_elim:default:B:1 · r329 · 드래곤 #106 L8: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Portals · 게임 exp/stack4-a-px4:proxy4_elim:portals:B:1 · r366 · 드래곤 #372 L7: 조각 L2 → 조각 죽음 r384 갇힘, 30라운드 안 먹은 진주 2
- proxy4_elim · Trauma · 게임 exp/stack4-a-px4:proxy4_elim:trauma:B:1 · r323 · 드래곤 #97 L7: 조각 L2 → 30라운드 생존, 먹은 진주 0
- proxy4_elim · Schooltime · 게임 exp/stack4-a-px4:proxy4_elim:schooltime:B:1 · r303 · 드래곤 #240 L7: 조각 L2 → 조각 죽음 r317 갇힘, 상대 길이 41, 30라운드 안 먹은 진주 0
- proxy4_elim · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_elim:slithery_fight:A:1 · r250 · 드래곤 #496 L18: 조각 L2 → 조각 죽음 r253 갇힘, 상대 길이 24, 30라운드 안 먹은 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:B:1 · r341 · 드래곤 #438 L8: 조각 L2 → 조각 죽음 r356 돌진, 상대 길이 10, 30라운드 안 먹은 진주 2

## 새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)

- 이번: 표적 진주 733개 (표식 턴 1724, 진주당 드래곤 1.2) · 질량 장부의 사망 진주 95% (자연 진주 2, 이미 없음 31) · 사망 진주 700개 중 우리가 먹음 81% · 상대 17% · 아무도 안 먹음 2% · 표적으로 삼은 드래곤이 먹음 67% · 우리가 먹기까지 평균 4.5라운드 · 상대 머리가 같거나 더 가까웠던 188개: 우리 51% 대 상대 48% · 박치기 진주 118개: 우리 71% 대 상대 28% · 우리 팀 사망 진주 82% · 사망 뒤 첫 표적까지 평균 1.7라운드
- 비교: 표적 진주 552개 (표식 턴 1351, 진주당 드래곤 1.1) · 질량 장부의 사망 진주 95% (자연 진주 0, 이미 없음 27) · 사망 진주 525개 중 우리가 먹음 75% · 상대 23% · 아무도 안 먹음 2% · 표적으로 삼은 드래곤이 먹음 65% · 우리가 먹기까지 평균 4.7라운드 · 상대 머리가 같거나 더 가까웠던 168개: 우리 43% 대 상대 54% · 박치기 진주 104개: 우리 66% 대 상대 34% · 우리 팀 사망 진주 76% · 사망 뒤 첫 표적까지 평균 1.6라운드
- 상대별: proxy4_elim 313회 88% · proxy4_king 233회 75% · proxy4_swarm 187회 78%
- 지도별: Autarky 69회 94% · Default 36회 65% · Devil 23회 52% · Portals 158회 97% · Prisoners Dilemma 30회 79% · Queen Of Spades 48회 49% · Schooltime 113회 90% · Slithery Fight 222회 76% · Trauma 21회 75% · Trophy 13회 60%
- 국면별: r0-99 118회 61% · r100-249 119회 66% · r250-349 204회 88% · r350-449 237회 96% · r450+ 55회 70%

실패 사례 (132건 중 10건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack4-a-px4:proxy4_king:devil:B:1 · r36 · 드래곤 #15 L2: 진주 (18,3), 우리 머리 3칸 · 상대 머리 3칸, 박치기 0라운드 뒤 → 상대가 먹음 (4라운드 뒤), 표식 3턴
- proxy4_king · Default · 게임 exp/stack4-a-px4:proxy4_king:default:B:1 · r203 · 드래곤 #31 L3: 진주 (25,24), 우리 머리 6칸 · 상대 머리 3칸, 상대 사망 2라운드 뒤 → 상대가 먹음 (2라운드 뒤), 표식 2턴
- proxy4_king · Autarky · 게임 exp/stack4-a-px4:proxy4_king:autarky:A:1 · r175 · 드래곤 #4 L2: 진주 (35,15), 우리 머리 3칸 · 상대 머리 1칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Prisoners Dilemma · 게임 exp/stack4-a-px4:proxy4_king:prisoners_dilemma:B:1 · r386 · 드래곤 #3 L22: 진주 (17,9), 우리 머리 4칸 · 상대 머리 2칸, 우리 팀 사망 2라운드 뒤 → 상대가 먹음 (1라운드 뒤), 표식 1턴
- proxy4_king · Queen Of Spades · 게임 exp/stack4-a-px4:proxy4_king:queen_of_spades:A:1 · r86 · 드래곤 #16 L3: 진주 (3,3), 우리 머리 4칸 · 상대 머리 9칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (9라운드 뒤), 표식 4턴
- proxy4_king · Portals · 게임 exp/stack4-a-px4:proxy4_king:portals:A:1 · r146 · 드래곤 #104 L10: 진주 (12,7), 우리 머리 2칸 · 상대 머리 4칸, 상대 사망 1라운드 뒤 → 상대가 먹음 (2라운드 뒤), 표식 1턴
- proxy4_king · Trauma · 게임 exp/stack4-a-px4:proxy4_king:trauma:B:1 · r141 · 드래곤 #1 L4: 진주 (29,7), 우리 머리 6칸 · 상대 머리 1칸, 상대 사망 2라운드 뒤 → 상대가 먹음 (0라운드 뒤), 표식 1턴
- proxy4_king · Schooltime · 게임 exp/stack4-a-px4:proxy4_king:schooltime:B:1 · r145 · 드래곤 #1 L3: 진주 (1,2), 우리 머리 2칸 · 상대 머리 1칸, 박치기 1라운드 뒤 → 상대가 먹음 (6라운드 뒤), 표식 2턴
- proxy4_king · Trophy · 게임 exp/stack4-a-px4:proxy4_king:trophy:A:1 · r91 · 드래곤 #0 L3: 진주 (10,14), 우리 머리 4칸 · 상대 머리 1칸, 박치기 2라운드 뒤 → 상대가 먹음 (2라운드 뒤), 표식 1턴
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:A:1 · r4 · 드래곤 #26 L2: 진주 (33,5), 우리 머리 5칸 · 상대 머리 10칸, 우리 팀 사망 1라운드 뒤 → 상대가 먹음 (38라운드 뒤), 표식 3턴

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 422 (그중 통로 고리 세대 330, 판정에서 뺌) · 고리 밖 92: 처음 거리 평균 10 → 최소 6.1 · 3칸 안까지 감 38% · 희생까지 함 41% · 가는 길에 죽음 24% · 끝까지 생존 35%
- 비교: 모이기 드래곤 385 (그중 통로 고리 세대 301, 판정에서 뺌) · 고리 밖 84: 처음 거리 평균 11.6 → 최소 5.7 · 3칸 안까지 감 44% · 희생까지 함 43% · 가는 길에 죽음 11% · 끝까지 생존 46%
- 상대별: proxy4_elim 124회 80% · proxy4_king 111회 68% · proxy4_swarm 187회 82%
- 지도별: Autarky 193회 95% · Default 4회 67% · Portals 104회 88% · Prisoners Dilemma 34회 100% · Queen Of Spades 4회 33% · Schooltime 22회 74% · Slithery Fight 57회 56% · Trauma 4회 67%
- 국면별: r250-349 107회 83% · r350-449 272회 78% · r450+ 43회 60%

실패 사례 (38건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack4-a-px4:proxy4_king:portals:B:1 · r440 · 드래곤 #398 L4: 왕까지 거리 20 → 최소 19 (2턴)
- proxy4_king · Queen Of Spades · 게임 exp/stack4-a-px4:proxy4_king:queen_of_spades:A:1 · r412 · 드래곤 #16 L4: 왕까지 거리 20 → 최소 7 (33턴), 가는 길에 죽음 r458 희생
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:A:1 · r340 · 드래곤 #625 L4: 왕까지 거리 11 → 최소 7 (16턴), 가는 길에 죽음 r356 희생
- proxy4_swarm · Autarky · 게임 exp/stack4-a-px4:proxy4_swarm:autarky:B:1 · r394 · 드래곤 #417 L30: 왕까지 거리 10 → 최소 10 (8턴)
- proxy4_swarm · Portals · 게임 exp/stack4-a-px4:proxy4_swarm:portals:B:1 · r428 · 드래곤 #403 L8: 왕까지 거리 11 → 최소 9 (3턴)
- proxy4_swarm · Schooltime · 게임 exp/stack4-a-px4:proxy4_swarm:schooltime:A:1 · r412 · 드래곤 #358 L13: 왕까지 거리 6 → 최소 6 (2턴)
- proxy4_swarm · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_swarm:slithery_fight:A:1 · r369 · 드래곤 #821 L17: 왕까지 거리 10 → 최소 10 (4턴)
- proxy4_swarm · Trauma · 게임 exp/stack4-a-px4:proxy4_swarm:trauma:B:1 · r355 · 드래곤 #135 L5: 왕까지 거리 12 → 최소 11 (20턴), 가는 길에 죽음 r433 돌진, 상대 길이 3
- proxy4_elim · Default · 게임 exp/stack4-a-px4:proxy4_elim:default:B:1 · r476 · 드래곤 #159 L20: 왕까지 거리 13 → 최소 13 (3턴)
- proxy4_elim · Portals · 게임 exp/stack4-a-px4:proxy4_elim:portals:A:1 · r340 · 드래곤 #389 L20: 왕까지 거리 9 → 최소 9 (2턴), 가는 길에 죽음 r347 아군 머리, 상대 길이 6

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 229개 중 우리 팀 85% (지목한 아군 59%) · 상대 7% · 지목 아군 끝까지 생존 69% (그 뒤 죽은 원인: 돌진 1, 박힘(상대 돌진) 3, 갇힘 12, 희생 3) · 지목 아군의 몸(자손 포함)이 끝까지 삶 95% · 최종 왕 48% (최종 왕이 지목 아군의 자손 71%)
- 비교: 실행 100% · 떨군 진주 197개 중 우리 팀 88% (지목한 아군 70%) · 상대 3% · 지목 아군 끝까지 생존 70% (그 뒤 죽은 원인: 희생 8, 박힘(상대 돌진) 2, 갇힘 6) · 지목 아군의 몸(자손 포함)이 끝까지 삶 94% · 최종 왕 54% (최종 왕이 지목 아군의 자손 76%)
- 상대별: proxy4_elim 27회 93% · proxy4_king 20회 75% · proxy4_swarm 15회 87%
- 지도별: Autarky 18회 100% · Default 2회 100% · Portals 15회 87% · Prisoners Dilemma 8회 63% · Queen Of Spades 2회 50% · Schooltime 8회 88% · Slithery Fight 7회 71% · Trauma 2회 100%
- 국면별: r250-349 7회 100% · r350-449 34회 94% · r450+ 21회 67%

실패 사례 (9건 중 9건, 기보 확인용):
- proxy4_king · Prisoners Dilemma · 게임 exp/stack4-a-px4:proxy4_king:prisoners_dilemma:A:1 · r476 · 드래곤 #407 L11: #2(L30)에게 희생 → 진주 6개 중 우리 1, 지목 아군 1, 상대 4; 지목 아군 r489 돌진에 사망
- proxy4_king · Queen Of Spades · 게임 exp/stack4-a-px4:proxy4_king:queen_of_spades:A:1 · r498 · 드래곤 #144 L5: #150(L6)에게 희생 → 진주 3개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:A:1 · r462 · 드래곤 #810 L5: #848(L26)에게 희생 → 진주 3개 중 우리 1, 지목 아군 1, 상대 2
- proxy4_swarm · Portals · 게임 exp/stack4-a-px4:proxy4_swarm:portals:A:1 · r433 · 드래곤 #484 L5: #485(L12)에게 희생 → 진주 3개 중 우리 1, 지목 아군 1, 상대 0; 지목 아군 r485 갇힘에 사망
- proxy4_elim · Prisoners Dilemma · 게임 exp/stack4-a-px4:proxy4_elim:prisoners_dilemma:B:1 · r491 · 드래곤 #368 L10: #273(L27)에게 희생 → 진주 5개 중 우리 1, 지목 아군 1, 상대 2
- proxy4_elim · Schooltime · 게임 exp/stack4-a-px4:proxy4_elim:schooltime:B:1 · r485 · 드래곤 #457 L4: #461(L31)에게 희생 → 진주 2개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack4-a-px4:proxy4_king:prisoners_dilemma:B:1 · r384 · 드래곤 #334 L11: #3(L23)에게 희생 → 진주 6개 중 우리 0, 지목 아군 0, 상대 6; 지목 아군 r450 박힘(상대 돌진)에 사망
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:A:1 · r480 · 드래곤 #856 L5: #864(L20)에게 희생 → 진주 3개 중 우리 1, 지목 아군 0, 상대 2
- proxy4_swarm · Portals · 게임 exp/stack4-a-px4:proxy4_swarm:portals:A:1 · r493 · 드래곤 #498 L7: #501(L21)에게 희생 → 진주 4개 중 우리 0, 지목 아군 0, 상대 0

## 막다른 길 한입 (pocket-eat)

- 이번: 한입 100% · 2턴 안 분열 100% · 30라운드 뒤 가족 길이 변화 -1 (줄지 않음 0%)
- 상대별: proxy4_swarm 1회 0%
- 지도별: Trauma 1회 0%
- 국면별: r450+ 1회 0%

실패 사례 (1건 중 1건, 기보 확인용):
- proxy4_swarm · Trauma · 게임 exp/stack4-a-px4:proxy4_swarm:trauma:B:1 · r473 · 드래곤 #305 L9: 한입, 분열(새끼 L8), 30라운드 뒤 가족 길이 변화 -1

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 98% · 새끼 자체 10라운드 생존 12% · 30라운드 뒤 가족 길이 변화 9.2
- 비교: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 99% · 새끼 자체 10라운드 생존 11% · 30라운드 뒤 가족 길이 변화 9.7
- 상대별: proxy4_elim 1241회 98% · proxy4_king 1086회 98% · proxy4_swarm 1180회 99%
- 지도별: Autarky 1504회 100% · Default 27회 100% · Devil 21회 71% · Portals 268회 92% · Prisoners Dilemma 1435회 99% · Queen Of Spades 11회 100% · Schooltime 76회 88% · Slithery Fight 142회 96% · Trauma 16회 100% · Trophy 7회 71%
- 국면별: r0-99 728회 99% · r100-249 1025회 99% · r250-349 724회 98% · r350-449 713회 98% · r450+ 317회 96%

실패 사례 (59건 중 10건, 기보 확인용):
- proxy4_king · Prisoners Dilemma · 게임 exp/stack4-a-px4:proxy4_king:prisoners_dilemma:A:1 · r467 · 드래곤 #397 L12: 새끼 L10 → 새끼 죽음 r471 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -12
- proxy4_king · Portals · 게임 exp/stack4-a-px4:proxy4_king:portals:A:1 · r236 · 드래곤 #173 L13: 새끼 L11 → 새끼 죽음 r239 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -13
- proxy4_king · Schooltime · 게임 exp/stack4-a-px4:proxy4_king:schooltime:A:1 · r230 · 드래곤 #173 L10: 새끼 L8 → 새끼 죽음 r236 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -10
- proxy4_king · Trophy · 게임 exp/stack4-a-px4:proxy4_king:trophy:A:1 · r81 · 드래곤 #2 L8: 새끼 L6 → 새끼 죽음 r89 박힘(상대 돌진), 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -8
- proxy4_swarm · Devil · 게임 exp/stack4-a-px4:proxy4_swarm:devil:B:1 · r66 · 드래곤 #3 L7: 새끼 L5 → 새끼 죽음 r76 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:B:1 · r129 · 드래곤 #105 L7: 새끼 L5 → 새끼 죽음 r135 박힘(상대 돌진), 상대 길이 2, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -7
- proxy4_swarm · Portals · 게임 exp/stack4-a-px4:proxy4_swarm:portals:B:1 · r329 · 드래곤 #29 L6: 새끼 L4 → 새끼 죽음 r332 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -6
- proxy4_swarm · Trophy · 게임 exp/stack4-a-px4:proxy4_swarm:trophy:B:1 · r78 · 드래곤 #42 L4: 새끼 L2 → 새끼 죽음 r80 박힘(상대 돌진), 상대 길이 4, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_swarm · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_swarm:slithery_fight:A:1 · r87 · 드래곤 #215 L6: 새끼 L4 → 새끼 죽음 r89 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -6
- proxy4_elim · Devil · 게임 exp/stack4-a-px4:proxy4_elim:devil:B:1 · r95 · 드래곤 #22 L4: 새끼 L2 → 새끼 죽음 r97 박힘(상대 돌진), 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 97% · 그 밖(진짜로 갇힘) 84회
- 비교: 탈출 분열 뒤 남은 조각(고리의 일부) 99% · 그 밖(진짜로 갇힘) 48회
- 상대별: proxy4_elim 1178회 – · proxy4_king 1044회 – · proxy4_swarm 1132회 –
- 지도별: Autarky 1497회 – · Default 10회 – · Devil 11회 – · Portals 234회 – · Prisoners Dilemma 1432회 – · Queen Of Spades 8회 – · Schooltime 45회 – · Slithery Fight 107회 – · Trauma 9회 – · Trophy 1회 –
- 국면별: r0-99 700회 – · r100-249 985회 – · r250-349 694회 – · r350-449 681회 – · r450+ 294회 –

## 정책 분열 (split)

- 이번: 분열 100% · 새끼 30라운드 생존 72% · 30라운드 뒤 가족 길이 변화 1.7
- 비교: 분열 100% · 새끼 30라운드 생존 65% · 30라운드 뒤 가족 길이 변화 0.9
- 상대별: proxy4_elim 26회 77% · proxy4_king 20회 60% · proxy4_swarm 18회 78%
- 지도별: Default 5회 80% · Devil 2회 50% · Portals 9회 56% · Prisoners Dilemma 2회 100% · Queen Of Spades 11회 73% · Schooltime 14회 86% · Slithery Fight 15회 53% · Trauma 5회 100% · Trophy 1회 100%
- 국면별: r0-99 14회 64% · r100-249 16회 100% · r250-349 28회 54% · r350-449 6회 100%

실패 사례 (18건 중 10건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack4-a-px4:proxy4_king:portals:B:1 · r297 · 드래곤 #31 L10: 새끼 L3 → 새끼 죽음 r300 갇힘, 상대 길이 2, 30라운드 뒤 가족 길이 변화 -1
- proxy4_king · Queen Of Spades · 게임 exp/stack4-a-px4:proxy4_king:queen_of_spades:A:1 · r34 · 드래곤 #2 L9: 새끼 L2 → 새끼 죽음 r42 갇힘, 상대 길이 9, 30라운드 뒤 가족 길이 변화 1
- proxy4_king · Schooltime · 게임 exp/stack4-a-px4:proxy4_king:schooltime:A:1 · r263 · 드래곤 #170 L8: 새끼 L3 → 새끼 죽음 r274 박힘(상대 돌진), 상대 길이 4, 30라운드 뒤 가족 길이 변화 -5
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:A:1 · r278 · 드래곤 #524 L25: 새끼 L3 → 새끼 죽음 r303 희생, 30라운드 뒤 가족 길이 변화 -2
- proxy4_swarm · Default · 게임 exp/stack4-a-px4:proxy4_swarm:default:B:1 · r257 · 드래곤 #12 L5: 새끼 L2 → 새끼 죽음 r257 박힘(상대 돌진), 상대 길이 3, 30라운드 뒤 가족 길이 변화 -5
- proxy4_swarm · Queen Of Spades · 게임 exp/stack4-a-px4:proxy4_swarm:queen_of_spades:A:1 · r34 · 드래곤 #2 L9: 새끼 L2 → 새끼 죽음 r43 갇힘, 30라운드 뒤 가족 길이 변화 2
- proxy4_swarm · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_swarm:slithery_fight:A:1 · r318 · 드래곤 #10 L18: 새끼 L3 → 새끼 죽음 r318 희생, 30라운드 뒤 가족 길이 변화 13
- proxy4_elim · Queen Of Spades · 게임 exp/stack4-a-px4:proxy4_elim:queen_of_spades:A:1 · r48 · 드래곤 #2 L10: 새끼 L2 → 새끼 죽음 r53 아군 머리, 상대 길이 7, 30라운드 뒤 가족 길이 변화 0
- proxy4_elim · Devil · 게임 exp/stack4-a-px4:proxy4_elim:devil:A:1 · r77 · 드래곤 #4 L8: 새끼 L3 → 새끼 죽음 r91 아군 머리, 상대 길이 2, 30라운드 뒤 가족 길이 변화 -8
- proxy4_elim · Portals · 게임 exp/stack4-a-px4:proxy4_elim:portals:B:1 · r293 · 드래곤 #324 L8: 새끼 L3 → 새끼 죽음 r313 갇힘, 30라운드 뒤 가족 길이 변화 5

## 탈출 질주 3칸 (esc)

- 이번: 질주 100% · 짧은 적 머리 4칸 안 91% · 몸 생존 5라운드 97% · 10라운드 94% (드래곤 자체 90%) · 10라운드 길이 변화 -2.9
- 비교: 질주 99% · 짧은 적 머리 4칸 안 85% · 몸 생존 5라운드 99% · 10라운드 97% (드래곤 자체 97%) · 10라운드 길이 변화 -2.4
- 상대별: proxy4_elim 21회 95% · proxy4_king 42회 90% · proxy4_swarm 33회 97%
- 지도별: Default 8회 88% · Devil 11회 91% · Prisoners Dilemma 1회 0% · Queen Of Spades 16회 100% · Schooltime 18회 89% · Slithery Fight 38회 97% · Trophy 4회 100%
- 국면별: r0-99 24회 92% · r100-249 34회 97% · r250-349 15회 87% · r350-449 13회 92% · r450+ 10회 100%

실패 사례 (6건 중 6건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack4-a-px4:proxy4_king:devil:B:1 · r58 · 드래곤 #3 L6: 질주 3칸 (가장 가까운 짧은 적 머리 1칸) → 죽음 r68 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Prisoners Dilemma · 게임 exp/stack4-a-px4:proxy4_king:prisoners_dilemma:B:1 · r442 · 드래곤 #3 L26: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r450 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Schooltime · 게임 exp/stack4-a-px4:proxy4_king:schooltime:B:1 · r201 · 드래곤 #5 L6: 질주 3칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r204 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack4-a-px4:proxy4_swarm:default:B:1 · r267 · 드래곤 #12 L6: 질주 3칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r275 박힘(상대 돌진), 상대 길이 3
- proxy4_elim · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_elim:slithery_fight:B:1 · r322 · 드래곤 #555 L6: 질주 3칸 (가장 가까운 짧은 적 머리 2칸) → 죽음 r327 희생
- proxy4_king · Schooltime · 게임 exp/stack4-a-px4:proxy4_king:schooltime:A:1 · r89 · 드래곤 #0 L8: 질주 3칸 (가장 가까운 짧은 적 머리 4칸) → 죽음 r92 박힘(상대 돌진), 상대 길이 3

## 위협 피하기 2칸 질주

- 이번: 질주 100% · 몸 10라운드 생존 95% (드래곤 자체 93%)
- 비교: 질주 99% · 몸 10라운드 생존 91% (드래곤 자체 88%)
- 상대별: proxy4_elim 116회 95% · proxy4_king 157회 94% · proxy4_swarm 144회 95%
- 지도별: Autarky 44회 98% · Default 63회 94% · Devil 25회 92% · Prisoners Dilemma 1회 100% · Queen Of Spades 45회 98% · Schooltime 74회 96% · Slithery Fight 117회 95% · Trauma 10회 80% · Trophy 38회 92%
- 국면별: r0-99 160회 94% · r100-249 154회 96% · r250-349 56회 95% · r350-449 42회 98% · r450+ 5회 60%

실패 사례 (22건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack4-a-px4:proxy4_king:default:B:1 · r8 · 드래곤 #5 L4: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r11 돌진, 상대 길이 2
- proxy4_king · Autarky · 게임 exp/stack4-a-px4:proxy4_king:autarky:B:1 · r52 · 드래곤 #3 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r60 갇힘
- proxy4_king · Schooltime · 게임 exp/stack4-a-px4:proxy4_king:schooltime:B:1 · r195 · 드래곤 #133 L5: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r201 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trophy · 게임 exp/stack4-a-px4:proxy4_king:trophy:A:1 · r82 · 드래곤 #30 L6: 2칸 질주 (가장 가까운 적 머리 1칸, 길이 2) → 죽음 r89 박힘(상대 돌진), 상대 길이 2
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:A:1 · r110 · 드래곤 #34 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 3) → 죽음 r118 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Default · 게임 exp/stack4-a-px4:proxy4_swarm:default:B:1 · r272 · 드래곤 #12 L4: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r275 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Devil · 게임 exp/stack4-a-px4:proxy4_swarm:devil:A:1 · r57 · 드래곤 #0 L5: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r66 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Queen Of Spades · 게임 exp/stack4-a-px4:proxy4_swarm:queen_of_spades:A:1 · r80 · 드래곤 #2 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 3) → 죽음 r80 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Trauma · 게임 exp/stack4-a-px4:proxy4_swarm:trauma:A:1 · r204 · 드래곤 #0 L4: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r212 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Trophy · 게임 exp/stack4-a-px4:proxy4_swarm:trophy:B:1 · r72 · 드래곤 #42 L6: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 2) → 죽음 r79 박힘(상대 돌진), 상대 길이 2

## 포털 통과 (전체; PORTAL?=미탐색 출구)

- 이번: 미탐색 출구 414회(몸 3라운드 생존 96%) · 전체 몸 생존 3라운드 96% (드래곤 자체 84%) · 10라운드 93% · 10라운드 안 먹은 진주 1
- 비교: 미탐색 출구 370회(몸 3라운드 생존 96%) · 전체 몸 생존 3라운드 96% (드래곤 자체 83%) · 10라운드 93% · 10라운드 안 먹은 진주 1.1
- 상대별: proxy4_elim 391회 95% · proxy4_king 290회 96% · proxy4_swarm 349회 97%
- 지도별: Autarky 108회 99% · Default 203회 95% · Portals 393회 96% · Prisoners Dilemma 49회 100% · Queen Of Spades 36회 86% · Schooltime 34회 100% · Slithery Fight 126회 96% · Trauma 80회 96% · Trophy 1회 0%
- 국면별: r0-99 252회 97% · r100-249 343회 96% · r250-349 233회 97% · r350-449 155회 94% · r450+ 47회 96%

실패 사례 (41건 중 10건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack4-a-px4:proxy4_king:default:A:1 · r135 · 드래곤 #0 L18: 포털 → 죽음 r135 돌진, 상대 길이 2, 10라운드 안 진주 0
- proxy4_king · Autarky · 게임 exp/stack4-a-px4:proxy4_king:autarky:B:1 · r321 · 드래곤 #245 L3: 포털 → 죽음 r323 희생, 10라운드 안 진주 0
- proxy4_king · Portals · 게임 exp/stack4-a-px4:proxy4_king:portals:B:1 · r8 · 드래곤 #1 L3: 포털(미탐색 출구) → 죽음 r9 갇힘, 10라운드 안 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack4-a-px4:proxy4_king:queen_of_spades:A:1 · r29 · 드래곤 #0 L3: 포털(미탐색 출구) → 죽음 r30 갇힘, 10라운드 안 진주 0
- proxy4_king · Trauma · 게임 exp/stack4-a-px4:proxy4_king:trauma:B:1 · r128 · 드래곤 #12 L7: 포털 → 죽음 r128 갇힘, 상대 길이 4, 10라운드 안 진주 0
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:A:1 · r271 · 드래곤 #321 L9: 포털 → 죽음 r271 갇힘, 상대 길이 22, 10라운드 안 진주 0
- proxy4_swarm · Default · 게임 exp/stack4-a-px4:proxy4_swarm:default:A:1 · r421 · 드래곤 #77 L2: 포털 → 죽음 r423 갇힘, 10라운드 안 진주 0
- proxy4_swarm · Portals · 게임 exp/stack4-a-px4:proxy4_swarm:portals:B:1 · r8 · 드래곤 #1 L3: 포털(미탐색 출구) → 죽음 r9 갇힘, 10라운드 안 진주 0
- proxy4_swarm · Queen Of Spades · 게임 exp/stack4-a-px4:proxy4_swarm:queen_of_spades:A:1 · r29 · 드래곤 #0 L3: 포털(미탐색 출구) → 죽음 r30 갇힘, 10라운드 안 진주 0
- proxy4_swarm · Trauma · 게임 exp/stack4-a-px4:proxy4_swarm:trauma:B:1 · r128 · 드래곤 #12 L7: 포털 → 죽음 r128 갇힘, 상대 길이 4, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 12, 경로 9) · 잡은 길이 ≥ 우리 95% · 두 몸의 진주 우리 69 대 상대 63
- 비교: 충돌 성사 100% (인접 6, 경로 10) · 잡은 길이 ≥ 우리 94% · 두 몸의 진주 우리 26 대 상대 83
- 상대별: proxy4_elim 3회 33% · proxy4_king 10회 70% · proxy4_swarm 8회 25%
- 지도별: Default 1회 0% · Devil 1회 0% · Queen Of Spades 1회 100% · Schooltime 5회 80% · Slithery Fight 12회 42% · Trauma 1회 0%
- 국면별: r0-99 1회 0% · r100-249 5회 0% · r250-349 5회 80% · r350-449 7회 57% · r450+ 3회 67%

실패 사례 (11건 중 10건, 기보 확인용):
- proxy4_king · Schooltime · 게임 exp/stack4-a-px4:proxy4_king:schooltime:A:1 · r242 · 드래곤 #187 L4: 돌진 경로 1칸 → 상대 L8 잡음, 진주 우리 2 대 상대 4
- proxy4_swarm · Devil · 게임 exp/stack4-a-px4:proxy4_swarm:devil:B:1 · r118 · 드래곤 #101 L2: 돌진 경로 2칸 → 상대 L3 잡음, 진주 우리 1 대 상대 2
- proxy4_swarm · Default · 게임 exp/stack4-a-px4:proxy4_swarm:default:B:1 · r201 · 드래곤 #5 L2: 돌진 경로 1칸 → 상대 L3 잡음, 진주 우리 0 대 상대 3
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:B:1 · r356 · 드래곤 #687 L4: 돌진 경로 3칸 → 상대 L10 잡음, 진주 우리 3 대 상대 4
- proxy4_swarm · Trauma · 게임 exp/stack4-a-px4:proxy4_swarm:trauma:A:1 · r270 · 드래곤 #12 L2: 돌진 경로 1칸 → 상대 L3 잡음, 진주 우리 0 대 상대 3
- proxy4_swarm · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_swarm:slithery_fight:A:1 · r93 · 드래곤 #143 L4: 돌진 경로 2칸 → 상대 L3 잡음, 진주 우리 0 대 상대 4
- proxy4_elim · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_elim:slithery_fight:A:1 · r235 · 드래곤 #527 L2: 돌진 경로 1칸 → 상대 L6 잡음, 진주 우리 0 대 상대 4
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:B:1 · r357 · 드래곤 #701 L3: 돌진 경로 2칸 → 상대 L16 잡음, 진주 우리 0 대 상대 10
- proxy4_swarm · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_swarm:slithery_fight:A:1 · r120 · 드래곤 #6 L2: 돌진 경로 1칸 → 상대 L5 잡음, 진주 우리 0 대 상대 4
- proxy4_swarm · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_swarm:slithery_fight:A:1 · r476 · 드래곤 #433 L2: 돌진 경로 1칸 → 상대 L18 잡음, 진주 우리 4 대 상대 5

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 비교: 먹음 100%
- 상대별: proxy4_elim 24회 100% · proxy4_king 42회 100% · proxy4_swarm 22회 100%
- 지도별: Autarky 4회 100% · Default 10회 100% · Devil 4회 100% · Portals 6회 100% · Queen Of Spades 8회 100% · Schooltime 29회 100% · Slithery Fight 22회 100% · Trauma 1회 100% · Trophy 4회 100%
- 국면별: r0-99 20회 100% · r100-249 22회 100% · r250-349 13회 100% · r350-449 25회 100% · r450+ 8회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 91%
- 비교: 그 턴 사망 0% · 10라운드 생존 83%
- 상대별: proxy4_elim 18회 – · proxy4_king 22회 – · proxy4_swarm 13회 –
- 지도별: Default 7회 – · Devil 5회 – · Queen Of Spades 9회 – · Schooltime 12회 – · Slithery Fight 19회 – · Trophy 1회 –
- 국면별: r0-99 17회 – · r100-249 18회 – · r250-349 11회 – · r350-449 6회 – · r450+ 1회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 비교: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 1회 – · proxy4_king 5회 – · proxy4_swarm 5회 –
- 지도별: Autarky 1회 – · Default 2회 – · Prisoners Dilemma 1회 – · Schooltime 2회 – · Trauma 5회 –
- 국면별: r0-99 1회 – · r100-249 2회 – · r250-349 4회 – · r350-449 2회 – · r450+ 2회 –

## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.

| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |
|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |
| 이번 `exp/stack4-a-px4` | 60 | 35 (0.58) | 54% | 0 (0.00) | 0 (0.00) | 4 | 27 | 2 | 0/1 (0) | 19 (0.32; 필사 2) | 7/22 (24.5) |
| 비교 `exp/stack3-a-px4` | 60 | 51 (0.85) | 57% | 5 (0.08) | 0 (0.00) | 6 | 30 | 9 | 1/2 (3.5) | 15 (0.25; 필사 1) | 3/9 (10.5) |

- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.
- 이번 `exp/stack4-a-px4`: gx 표식 턴 218 · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 0

### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)

사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.

| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 이번 `exp/stack4-a-px4` | 60 | 42832 | 0.9% (373) | 12.0% (5156) | 3593 | 1.4% (49) | 3.3% (120) | 19.9% (716/3593) |
| 비교 `exp/stack3-a-px4` | 60 | 41862 | 1.1% (458) | 11.5% (4824) | 3229 | 1.7% (54) | 4.6% (149) | 19.3% (624/3229) |

### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율

| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |
| 이번 `exp/stack4-a-px4` | 전체 | 분열 | 31 (37%) | 13.5 | 89% | 80% | 18 | 1 |
| 이번 `exp/stack4-a-px4` | 전체 | 2칸 질주 | 13 (16%) | 10.6 | 84% | 76% | 1 | 1 |
| 이번 `exp/stack4-a-px4` | 전체 | 3칸 질주 | 7 (8%) | 9.9 | 114% | 91% | 1 | 0 |
| 이번 `exp/stack4-a-px4` | 전체 | 한 걸음 | 32 (39%) | 12.4 | 35% | 28% | 23 | 20 |
| 이번 `exp/stack4-a-px4` | 4칸 이상 | 분열 | 18 (51%) | 14.3 | 96% | 90% | 9 | 0 |
| 이번 `exp/stack4-a-px4` | 4칸 이상 | 2칸 질주 | 2 (6%) | 24 | 104% | 102% | 0 | 0 |
| 이번 `exp/stack4-a-px4` | 4칸 이상 | 3칸 질주 | 3 (9%) | 10 | 173% | 183% | 0 | 0 |
| 이번 `exp/stack4-a-px4` | 4칸 이상 | 한 걸음 | 12 (34%) | 17.1 | 38% | 36% | 9 | 8 |
| 비교 `exp/stack3-a-px4` | 전체 | 분열 | 14 (12%) | 12.9 | 84% | 62% | 8 | 2 |
| 비교 `exp/stack3-a-px4` | 전체 | 2칸 질주 | 43 (36%) | 10.5 | 82% | 66% | 11 | 9 |
| 비교 `exp/stack3-a-px4` | 전체 | 3칸 질주 | 26 (22%) | 9.1 | 79% | 80% | 2 | 2 |
| 비교 `exp/stack3-a-px4` | 전체 | 한 걸음 | 36 (30%) | 12.2 | 37% | 23% | 23 | 21 |
| 비교 `exp/stack3-a-px4` | 4칸 이상 | 분열 | 9 (16%) | 12.7 | 95% | 98% | 4 | 0 |
| 비교 `exp/stack3-a-px4` | 4칸 이상 | 2칸 질주 | 21 (36%) | 12.1 | 94% | 74% | 6 | 4 |
| 비교 `exp/stack3-a-px4` | 4칸 이상 | 3칸 질주 | 8 (14%) | 8.3 | 64% | 59% | 2 | 2 |
| 비교 `exp/stack3-a-px4` | 4칸 이상 | 한 걸음 | 20 (34%) | 13.6 | 33% | 23% | 13 | 13 |

넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (19건 중 10건):
- proxy4_king · Default · 게임 exp/stack4-a-px4:proxy4_king:default:A:1 · r154 · 드래곤 #12 L3: v10 PORTAL? → 아군 머리, 막은 우리 드래곤 L4
- proxy4_king · Portals · 게임 exp/stack4-a-px4:proxy4_king:portals:A:1 · r240 · 드래곤 #173 L2: v-10.5 → 아군 머리, 막은 우리 드래곤 L9
- proxy4_king · Portals · 게임 exp/stack4-a-px4:proxy4_king:portals:A:1 · r259 · 드래곤 #265 L9: v-6.3 → 갇힘, 막은 우리 드래곤 L15
- proxy4_king · Portals · 게임 exp/stack4-a-px4:proxy4_king:portals:A:1 · r413 · 드래곤 #432 L9: v-7.1 → 갇힘, 막은 우리 드래곤 L21
- proxy4_king · Trauma · 게임 exp/stack4-a-px4:proxy4_king:trauma:B:1 · r128 · 드래곤 #12 L7: v-11.2 → 갇힘, 막은 우리 드래곤 L4
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:A:1 · r264 · 드래곤 #460 L3: v-8.4 → 갇힘, 막은 우리 드래곤 L22
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:A:1 · r271 · 드래곤 #321 L9: v-9.2 → 갇힘, 막은 우리 드래곤 L22
- proxy4_swarm · Default · 게임 exp/stack4-a-px4:proxy4_swarm:default:B:1 · r129 · 드래곤 #32 L2: v-15 → 희생, 막은 우리 드래곤 L13
- proxy4_swarm · Default · 게임 exp/stack4-a-px4:proxy4_swarm:default:B:1 · r186 · 드래곤 #47 L2: v4 → 아군 머리, 막은 우리 드래곤 L2
- proxy4_king · Slithery Fight · 게임 exp/stack4-a-px4:proxy4_king:slithery_fight:B:1 · r330 · 드래곤 #321 L10: v-9.5 → 갇힘, 막은 우리 드래곤 L2

