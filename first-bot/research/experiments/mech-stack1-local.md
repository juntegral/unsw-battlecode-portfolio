# 로컬 확인: cand-stack1 대 흉내 상대 v4 (a판, 60판)

- 대상: `exp/stack1-a-px4` 60판 · 비교: `exp/merge2-a-old4` 80판
- 기준(사용자 규칙 2026-09-30): 승률이 아니라, 봇에 구현한 기능이 이 상대들에게 실제로 발동하고 의도대로 작동했는지를 본다.
- "의도대로"의 정의: 모이기=왕 3칸 안까지 가거나 희생까지 함 · 희생=떨군 진주 절반 이상을 우리 팀이 먹고 상대는 못 먹음 · 한입=2턴 안 분열하고 30라운드 뒤 가족 길이가 줄지 않음 · 탈출 분열=10라운드 뒤 몸이 살아 있음 · 정책 분열=새끼 30라운드 생존 · 탈출 질주·위협 피하기=10라운드 뒤 몸 생존 · 포털=3라운드 뒤 몸 생존 · 돌진=충돌 성사, 잡은 길이 ≥ 우리, 두 몸의 진주를 우리가 더 먹음 · 먹이 질주=진주 먹음.
- "몸"은 그 드래곤과 그 뒤 분열로 태어난 자손 전체다. 통로 고리처럼 몸을 새끼에게 넘기며 버티는 경우를 손실로 세지 않기 위해서다.

## 요약

| 기능 | 발동(판당) | 의도대로 | 비교: 발동(판당) | 비교: 의도대로 |
|---|---:|---:|---:|---:|
| 큰 아군 곁 희생 (conv, stack1 M1) | 41 (0.7) | 100% | 0 (0) | – |
| 왕에게 모이기 (g, 드래곤 단위) | 277 (4.6) | 75% | 1828 (22.9) | 79% |
| 희생 먹이기 (feed) | 33 (0.6) | 70% | 415 (5.2) | 73% |
| 막다른 길 한입 (pocket-eat) | 0 (0) | – | 62 (0.8) | 47% |
| 탈출 분열 (escape-split) | 3345 (55.8) | 99% | 6323 (79) | 97% |
| 출구 없음 (no-exit) | 3236 (53.9) | – | 5550 (69.4) | – |
| 정책 분열 (split) | 82 (1.4) | 66% | 89 (1.1) | 73% |
| 탈출 질주 3칸 (esc) | 68 (1.1) | 90% | 299 (3.7) | 96% |
| 위협 피하기 2칸 질주 | 455 (7.6) | 87% | 977 (12.2) | 95% |
| 포털 통과 (전체; PORTAL?=미탐색 출구) | 907 (15.1) | 95% | 2224 (27.8) | 97% |
| 돌진 (TRADE) | 22 (0.4) | 36% | 68 (0.9) | 40% |
| 먹이 질주 (2칸 이상, 먹은 것) | 70 (1.2) | 100% | 424 (5.3) | 100% |
| 기타 2칸 질주 | 3 (0.1) | – | 36 (0.5) | – |
| 마지막 돌진 (last-trade) | 6 (0.1) | – | 24 (0.3) | – |

- 건강: 턴 78257, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 비교 건강: 턴 204478, 표식 누락 0, degraded 0, 시간 초과 사망 0, 한 턴 최대 명령 수 0.0M(한도 100M), 80M 넘은 턴 0, 탐색 깊이 5 미만 0%
- 표식 턴 수: 왕에게 모이기(g) 3082턴 · 끝판(late) 2475턴 · 돌진 신뢰(T, 탈출 끔) 0턴, 그 직후 박혀 죽음 0 · 후반 왕 보호(ks) 1457턴

## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)

| 지표 | 상위권 승자 | 이번 | 비교 |
|---|---|---|---|
| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | 4% (22/628턴) | 14% (48/341턴) |
| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | 12.8칸 (2회), 진주 우리 86% · 상대 7% | 57.6칸 (5.4회), 진주 우리 75% · 상대 6% |
| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | 1칸 (판당 0.03회) | 2.4칸 (판당 0.03회) |

상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).

## 큰 아군 곁 희생 (conv, stack1 M1)

- 이번: 실행 100% · 떨군 진주 60개 중 우리 팀 100% (지목한 아군 83%) · 상대 0% · 지목 아군 끝까지 생존 49% (그 뒤 죽은 원인: 갇힘 11, 박힘(상대 돌진) 7, 희생 3) · 최종 왕 22%
- 상대별: proxy4_elim 20회 100% · proxy4_king 10회 100% · proxy4_swarm 11회 100%
- 지도별: Autarky 1회 100% · Default 1회 100% · Portals 9회 100% · Prisoners Dilemma 7회 100% · Schooltime 1회 100% · Slithery Fight 21회 100% · Trauma 1회 100%
- 국면별: r250-349 24회 100% · r350-449 15회 100% · r450+ 2회 100%

## 왕에게 모이기 (g, 드래곤 단위)

- 이번: 모이기 드래곤 277 (그중 통로 고리 세대 222, 판정에서 뺌) · 고리 밖 55: 처음 거리 평균 8.4 → 최소 4.4 · 3칸 안까지 감 55% · 희생까지 함 36% · 가는 길에 죽음 18% · 끝까지 생존 45%
- 비교: 모이기 드래곤 1828 (그중 통로 고리 세대 1406, 판정에서 뺌) · 고리 밖 422: 처음 거리 평균 12.2 → 최소 7 · 3칸 안까지 감 28% · 희생까지 함 56% · 가는 길에 죽음 11% · 끝까지 생존 33%
- 상대별: proxy4_elim 69회 76% · proxy4_king 147회 71% · proxy4_swarm 61회 78%
- 지도별: Autarky 121회 100% · Portals 42회 67% · Prisoners Dilemma 74회 88% · Queen Of Spades 3회 0% · Slithery Fight 31회 89% · Trauma 6회 20%
- 국면별: r250-349 86회 89% · r350-449 184회 69% · r450+ 7회 20%

실패 사례 (19건 중 4건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack1-a-px4:proxy4_king:portals:B:1 · r360 · 드래곤 #339 L10: 왕까지 거리 7 → 최소 7 (23턴)
- proxy4_king · Queen Of Spades · 게임 exp/stack1-a-px4:proxy4_king:queen_of_spades:B:1 · r474 · 드래곤 #176 L23: 왕까지 거리 10 → 최소 9 (18턴)
- proxy4_king · Trauma · 게임 exp/stack1-a-px4:proxy4_king:trauma:A:1 · r385 · 드래곤 #209 L5: 왕까지 거리 4 → 최소 4 (1턴)
- proxy4_swarm · Portals · 게임 exp/stack1-a-px4:proxy4_swarm:portals:A:1 · r438 · 드래곤 #403 L24: 왕까지 거리 19 → 최소 10 (43턴)

## 희생 먹이기 (feed)

- 이번: 실행 100% · 떨군 진주 175개 중 우리 팀 73% (지목한 아군 61%) · 상대 12% · 지목 아군 끝까지 생존 79% (그 뒤 죽은 원인: 박힘(상대 돌진) 3, 갇힘 1, 희생 2, 돌진 1) · 최종 왕 61%
- 비교: 실행 100% · 떨군 진주 2163개 중 우리 팀 75% (지목한 아군 50%) · 상대 7% · 지목 아군 끝까지 생존 45% (그 뒤 죽은 원인: 희생 78, 갇힘 130, 아군 머리 9, 돌진 7, 박힘(상대 돌진) 4) · 최종 왕 19%
- 상대별: proxy4_elim 16회 88% · proxy4_king 8회 25% · proxy4_swarm 9회 78%
- 지도별: Autarky 7회 86% · Default 1회 0% · Portals 5회 80% · Prisoners Dilemma 4회 50% · Queen Of Spades 1회 0% · Slithery Fight 13회 69% · Trauma 2회 100%
- 국면별: r250-349 2회 100% · r350-449 14회 86% · r450+ 17회 53%

실패 사례 (10건 중 4건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack1-a-px4:proxy4_king:portals:B:1 · r499 · 드래곤 #385 L9: #65(L32)에게 희생 → 진주 5개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Default · 게임 exp/stack1-a-px4:proxy4_king:default:B:1 · r481 · 드래곤 #3 L20: #95(L3)에게 희생 → 진주 10개 중 우리 0, 지목 아군 0, 상대 0
- proxy4_king · Prisoners Dilemma · 게임 exp/stack1-a-px4:proxy4_king:prisoners_dilemma:B:1 · r441 · 드래곤 #399 L10: #278(L13)에게 희생 → 진주 5개 중 우리 3, 지목 아군 1, 상대 2; 지목 아군 r448 박힘(상대 돌진)에 사망
- proxy4_king · Queen Of Spades · 게임 exp/stack1-a-px4:proxy4_king:queen_of_spades:B:1 · r499 · 드래곤 #172 L9: #176(L25)에게 희생 → 진주 5개 중 우리 0, 지목 아군 0, 상대 0

## 탈출 분열 (escape-split)

- 이번: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 99% · 새끼 자체 10라운드 생존 10% · 30라운드 뒤 가족 길이 변화 9.8
- 비교: 분열 100% · 몸(가족)이 10라운드 뒤 살아 있음 97% · 새끼 자체 10라운드 생존 30% · 30라운드 뒤 가족 길이 변화 7.4
- 상대별: proxy4_elim 1124회 99% · proxy4_king 1103회 99% · proxy4_swarm 1118회 99%
- 지도별: Autarky 1486회 100% · Default 27회 100% · Devil 18회 78% · Portals 143회 94% · Prisoners Dilemma 1474회 99% · Queen Of Spades 25회 92% · Schooltime 12회 92% · Slithery Fight 136회 99% · Trauma 18회 94% · Trophy 6회 50%
- 국면별: r0-99 727회 100% · r100-249 1021회 99% · r250-349 674회 99% · r350-449 653회 99% · r450+ 270회 96%

실패 사례 (35건 중 4건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack1-a-px4:proxy4_king:devil:B:1 · r43 · 드래곤 #21 L5: 새끼 L3 → 새끼 죽음 r45 갇힘, 상대 길이 3, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -5
- proxy4_king · Portals · 게임 exp/stack1-a-px4:proxy4_king:portals:A:1 · r185 · 드래곤 #104 L15: 새끼 L13 → 새끼 죽음 r193 아군 머리, 상대 길이 19, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -15
- proxy4_king · Queen Of Spades · 게임 exp/stack1-a-px4:proxy4_king:queen_of_spades:A:1 · r149 · 드래곤 #27 L4: 새끼 L2 → 새끼 죽음 r157 박힘(상대 돌진), 상대 길이 4, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -4
- proxy4_king · Prisoners Dilemma · 게임 exp/stack1-a-px4:proxy4_king:prisoners_dilemma:B:1 · r433 · 드래곤 #389 L12: 새끼 L10 → 새끼 죽음 r437 갇힘, 10라운드 뒤 가족 전멸, 30라운드 뒤 가족 길이 변화 -12

## 출구 없음 (no-exit)

- 이번: 탈출 분열 뒤 남은 조각(고리의 일부) 99% · 그 밖(진짜로 갇힘) 40회
- 비교: 탈출 분열 뒤 남은 조각(고리의 일부) 93% · 그 밖(진짜로 갇힘) 363회
- 상대별: proxy4_elim 1085회 – · proxy4_king 1062회 – · proxy4_swarm 1089회 –
- 지도별: Autarky 1480회 – · Default 19회 – · Devil 7회 – · Portals 137회 – · Prisoners Dilemma 1465회 – · Queen Of Spades 23회 – · Schooltime 8회 – · Slithery Fight 87회 – · Trauma 9회 – · Trophy 1회 –
- 국면별: r0-99 695회 – · r100-249 984회 – · r250-349 656회 – · r350-449 634회 – · r450+ 267회 –

## 정책 분열 (split)

- 이번: 분열 100% · 새끼 30라운드 생존 66% · 30라운드 뒤 가족 길이 변화 2
- 비교: 분열 100% · 새끼 30라운드 생존 73% · 30라운드 뒤 가족 길이 변화 8
- 상대별: proxy4_elim 35회 57% · proxy4_king 23회 65% · proxy4_swarm 24회 79%
- 지도별: Autarky 3회 33% · Default 4회 50% · Devil 2회 100% · Portals 16회 50% · Queen Of Spades 11회 55% · Schooltime 17회 82% · Slithery Fight 20회 70% · Trauma 6회 83% · Trophy 3회 67%
- 국면별: r0-99 14회 43% · r100-249 32회 81% · r250-349 31회 58% · r350-449 5회 80%

실패 사례 (28건 중 4건, 기보 확인용):
- proxy4_king · Portals · 게임 exp/stack1-a-px4:proxy4_king:portals:B:1 · r297 · 드래곤 #31 L10: 새끼 L3 → 새끼 죽음 r309 갇힘, 상대 길이 4, 30라운드 뒤 가족 길이 변화 7
- proxy4_king · Queen Of Spades · 게임 exp/stack1-a-px4:proxy4_king:queen_of_spades:A:1 · r34 · 드래곤 #2 L9: 새끼 L2 → 새끼 죽음 r42 갇힘, 상대 길이 9, 30라운드 뒤 가족 길이 변화 4
- proxy4_king · Slithery Fight · 게임 exp/stack1-a-px4:proxy4_king:slithery_fight:A:1 · r93 · 드래곤 #33 L20: 새끼 L3 → 새끼 죽음 r120 갇힘, 30라운드 뒤 가족 길이 변화 3
- proxy4_swarm · Portals · 게임 exp/stack1-a-px4:proxy4_swarm:portals:A:1 · r321 · 드래곤 #342 L24: 새끼 L3 → 새끼 죽음 r332 갇힘, 30라운드 뒤 가족 길이 변화 15

## 탈출 질주 3칸 (esc)

- 이번: 질주 96% · 짧은 적 머리 4칸 안 90% · 몸 생존 5라운드 97% · 10라운드 94% (드래곤 자체 91%) · 10라운드 길이 변화 -3.5
- 비교: 질주 100% · 짧은 적 머리 4칸 안 89% · 몸 생존 5라운드 98% · 10라운드 96% (드래곤 자체 91%) · 10라운드 길이 변화 -4.4
- 상대별: proxy4_elim 14회 93% · proxy4_king 31회 87% · proxy4_swarm 23회 91%
- 지도별: Autarky 1회 100% · Default 5회 60% · Devil 7회 100% · Queen Of Spades 5회 80% · Schooltime 21회 95% · Slithery Fight 24회 88% · Trophy 5회 100%
- 국면별: r0-99 12회 100% · r100-249 27회 89% · r250-349 12회 83% · r350-449 12회 83% · r450+ 5회 100%

실패 사례 (7건 중 4건, 기보 확인용):
- proxy4_king · Default · 게임 exp/stack1-a-px4:proxy4_king:default:A:1 · r423 · 드래곤 #61 L6: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r423 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Slithery Fight · 게임 exp/stack1-a-px4:proxy4_king:slithery_fight:A:1 · r107 · 드래곤 #12 L6: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r112 박힘(상대 돌진), 상대 길이 2
- proxy4_swarm · Default · 게임 exp/stack1-a-px4:proxy4_swarm:default:B:1 · r291 · 드래곤 #1 L6: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r291 박힘(상대 돌진), 상대 길이 3
- proxy4_swarm · Queen Of Spades · 게임 exp/stack1-a-px4:proxy4_swarm:queen_of_spades:B:1 · r207 · 드래곤 #1 L8: 질주 3칸 (가장 가까운 짧은 적 머리 3칸) → 죽음 r217 박힘(상대 돌진), 상대 길이 2

## 위협 피하기 2칸 질주

- 이번: 질주 98% · 몸 10라운드 생존 88% (드래곤 자체 85%)
- 비교: 질주 100% · 몸 10라운드 생존 95% (드래곤 자체 91%)
- 상대별: proxy4_elim 114회 87% · proxy4_king 177회 88% · proxy4_swarm 164회 85%
- 지도별: Autarky 29회 97% · Default 77회 90% · Devil 29회 86% · Prisoners Dilemma 1회 100% · Queen Of Spades 37회 95% · Schooltime 94회 88% · Slithery Fight 128회 86% · Trauma 18회 89% · Trophy 42회 64%
- 국면별: r0-99 151회 85% · r100-249 190회 85% · r250-349 62회 90% · r350-449 43회 88% · r450+ 9회 100%

실패 사례 (61건 중 4건, 기보 확인용):
- proxy4_king · Devil · 게임 exp/stack1-a-px4:proxy4_king:devil:A:1 · r48 · 드래곤 #0 L5: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r54 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Default · 게임 exp/stack1-a-px4:proxy4_king:default:B:1 · r59 · 드래곤 #7 L3: 2칸 질주 (가장 가까운 적 머리 2칸, 길이 2) → 죽음 r65 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Schooltime · 게임 exp/stack1-a-px4:proxy4_king:schooltime:A:1 · r142 · 드래곤 #2 L7: 2칸 질주 (가장 가까운 적 머리 4칸, 길이 3) → 죽음 r144 박힘(상대 돌진), 상대 길이 3
- proxy4_king · Trauma · 게임 exp/stack1-a-px4:proxy4_king:trauma:B:1 · r231 · 드래곤 #1 L3: 2칸 질주 (가장 가까운 적 머리 3칸, 길이 3) → 죽음 r231 박힘(상대 돌진), 상대 길이 3

## 포털 통과 (전체; PORTAL?=미탐색 출구)

- 이번: 미탐색 출구 367회(몸 3라운드 생존 97%) · 전체 몸 생존 3라운드 95% (드래곤 자체 84%) · 10라운드 91% · 10라운드 안 먹은 진주 1.1
- 비교: 미탐색 출구 767회(몸 3라운드 생존 96%) · 전체 몸 생존 3라운드 97% (드래곤 자체 87%) · 10라운드 95% · 10라운드 안 먹은 진주 1.4
- 상대별: proxy4_elim 293회 96% · proxy4_king 270회 95% · proxy4_swarm 344회 94%
- 지도별: Autarky 66회 97% · Default 171회 95% · Portals 314회 96% · Prisoners Dilemma 46회 98% · Queen Of Spades 50회 80% · Schooltime 37회 92% · Slithery Fight 169회 97% · Trauma 53회 94% · Trophy 1회 100%
- 국면별: r0-99 231회 96% · r100-249 334회 93% · r250-349 218회 96% · r350-449 107회 95% · r450+ 17회 100%

실패 사례 (45건 중 4건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack1-a-px4:proxy4_king:autarky:A:1 · r312 · 드래곤 #10 L30: 포털 → 죽음 r312 희생, 상대 길이 26, 10라운드 안 진주 0
- proxy4_king · Portals · 게임 exp/stack1-a-px4:proxy4_king:portals:B:1 · r8 · 드래곤 #1 L3: 포털(미탐색 출구) → 죽음 r9 갇힘, 10라운드 안 진주 0
- proxy4_king · Queen Of Spades · 게임 exp/stack1-a-px4:proxy4_king:queen_of_spades:A:1 · r29 · 드래곤 #0 L3: 포털(미탐색 출구) → 죽음 r30 갇힘, 10라운드 안 진주 0
- proxy4_king · Schooltime · 게임 exp/stack1-a-px4:proxy4_king:schooltime:B:1 · r406 · 드래곤 #255 L5: 포털 → 죽음 r407 박힘(상대 돌진), 상대 길이 3, 10라운드 안 진주 0

## 돌진 (TRADE)

- 이번: 충돌 성사 100% (인접 18, 경로 4) · 잡은 길이 ≥ 우리 95% · 두 몸의 진주 우리 24 대 상대 59 · 새 작은 조각 박치기(ram4) 11회, 성사 11: 곁에 아군 있음 11회(진주 우리 8 대 17), 없음 0회(0 대 0)
- 비교: 충돌 성사 100% (인접 27, 경로 41) · 잡은 길이 ≥ 우리 97% · 두 몸의 진주 우리 177 대 상대 309
- 상대별: proxy4_elim 5회 60% · proxy4_king 9회 22% · proxy4_swarm 8회 38%
- 지도별: Autarky 2회 50% · Default 1회 0% · Devil 3회 67% · Schooltime 3회 33% · Slithery Fight 8회 38% · Trauma 3회 0% · Trophy 2회 50%
- 국면별: r0-99 10회 40% · r100-249 3회 33% · r250-349 5회 40% · r350-449 3회 0% · r450+ 1회 100%

실패 사례 (14건 중 4건, 기보 확인용):
- proxy4_king · Autarky · 게임 exp/stack1-a-px4:proxy4_king:autarky:B:1 · r76 · 드래곤 #7 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2
- proxy4_king · Schooltime · 게임 exp/stack1-a-px4:proxy4_king:schooltime:A:1 · r289 · 드래곤 #31 L2: 돌진 경로 1칸 → 상대 L13 잡음, 진주 우리 0 대 상대 8
- proxy4_king · Trauma · 게임 exp/stack1-a-px4:proxy4_king:trauma:A:1 · r386 · 드래곤 #151 L3: 돌진 경로 1칸 → 상대 L8 잡음, 진주 우리 0 대 상대 6
- proxy4_swarm · Default · 게임 exp/stack1-a-px4:proxy4_swarm:default:A:1 · r8 · 드래곤 #0 L2: 돌진 경로 1칸 → 상대 L2 잡음, 진주 우리 0 대 상대 2

## 먹이 질주 (2칸 이상, 먹은 것)

- 이번: 먹음 100%
- 비교: 먹음 100%
- 상대별: proxy4_elim 25회 100% · proxy4_king 21회 100% · proxy4_swarm 24회 100%
- 지도별: Autarky 1회 100% · Default 8회 100% · Devil 2회 100% · Portals 5회 100% · Prisoners Dilemma 5회 100% · Queen Of Spades 9회 100% · Schooltime 20회 100% · Slithery Fight 19회 100% · Trophy 1회 100%
- 국면별: r0-99 18회 100% · r100-249 31회 100% · r250-349 6회 100% · r350-449 11회 100% · r450+ 4회 100%

## 기타 2칸 질주

- 이번: 그 턴 사망 0% · 10라운드 생존 100%
- 비교: 그 턴 사망 0% · 10라운드 생존 94%
- 상대별: proxy4_swarm 3회 –
- 지도별: Slithery Fight 3회 –
- 국면별: r0-99 1회 – · r100-249 1회 – · r450+ 1회 –

## 마지막 돌진 (last-trade)

- 이번: 그 턴 사망 100% · 10라운드 생존 0%
- 비교: 그 턴 사망 100% · 10라운드 생존 0%
- 상대별: proxy4_elim 3회 – · proxy4_king 1회 – · proxy4_swarm 2회 –
- 지도별: Autarky 1회 – · Devil 1회 – · Schooltime 2회 – · Slithery Fight 1회 – · Trauma 1회 –
- 국면별: r100-249 4회 – · r250-349 2회 –

