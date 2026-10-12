# QF3 여왕 기보 집계

`m5q3_vh`의 8개 지도·시드 × 양쪽 진영 = 16판. 모든 열은 같은 16판이며 상대는 `m3hunt`이다.

기존 표는 복사한 `qh_counts.py`·`qh_table.py`의 집계와 반올림을 그대로 사용했다. 거리 tiles는 토러스 맨해튼, steps는 몸을 무시한 열린 간선·포털 경로다. own3/own5는 여왕을 제외한 아군 머리다. e3/추격은 적 여왕을 제외한다. depth/home-rank는 4라운드마다, 나머지 구간 평균은 여왕 턴으로 가중한다. 조기 종료 판의 r100/r300 상태는 기존 스크립트대로 마지막 상태를 사용한다.

| measure | m3b7qk_vh | m5q3_vh | m5qh2_vh |
|---|---|---|---|
| games | 16 | 16 | 16 |
| depth r0-50 | 0.57 | 0.57 | 0.56 |
| home-rank r0-50 | 0.54 | 0.54 | 0.56 |
| own3 r0-50 | 0.59 | 0.59 | 0.61 |
| own5 r0-50 | 1.63 | 1.62 | 1.68 |
| alone5 % r0-50 | 29 | 29 | 27 |
| e3 per 100 turns r0-50 | 4.1 (33/809) | 4.0 (32/799) | 3.1 (25/808) |
| pearls per 100 turns r0-50 | 15.1 | 15.3 | 16.6 |
| tiles from start r0-50 | 9.5 | 9.5 | 9.0 |
| her length r0-50 | 3.7 | 3.7 | 3.7 |
| depth r51-100 | 0.50 | 0.51 | 0.46 |
| home-rank r51-100 | 0.60 | 0.67 | 0.64 |
| own3 r51-100 | 0.81 | 0.82 | 0.91 |
| own5 r51-100 | 2.49 | 2.55 | 2.81 |
| alone5 % r51-100 | 33 | 27 | 18 |
| e3 per 100 turns r51-100 | 11.5 (64/555) | 9.1 (50/552) | 13.1 (74/564) |
| pearls per 100 turns r51-100 | 5.6 | 4.9 | 5.9 |
| tiles from start r51-100 | 14.6 | 12.5 | 12.1 |
| her length r51-100 | 3.7 | 3.7 | 3.6 |
| depth r101-300 | 0.59 | 0.61 | 0.57 |
| home-rank r101-300 | 0.65 | 0.68 | 0.70 |
| own3 r101-300 | 1.00 | 0.82 | 1.21 |
| own5 r101-300 | 2.77 | 2.45 | 3.20 |
| alone5 % r101-300 | 13 | 14 | 11 |
| e3 per 100 turns r101-300 | 6.3 (27/428) | 8.3 (46/556) | 11.6 (68/584) |
| pearls per 100 turns r101-300 | 5.4 | 4.3 | 9.8 |
| tiles from start r101-300 | 14.0 | 13.7 | 11.1 |
| her length r101-300 | 4.5 | 5.3 | 5.4 |
| depth r301+ | - | - | 0.69 |
| home-rank r301+ | - | - | 0.89 |
| own3 r301+ | - | - | 0.23 |
| own5 r301+ | - | - | 0.88 |
| alone5 % r301+ | - | - | 41 |
| e3 per 100 turns r301+ | - | - | 0.0 (0/199) |
| pearls per 100 turns r301+ | - | - | 41.2 |
| tiles from start r301+ | - | - | 11.5 |
| her length r301+ | - | - | 61.6 |
| e3 per 100 turns all | 6.9 (124/1792) | 6.7 (128/1907) | 7.7 (167/2155) |
| chases a game | 2.19 (35) | 2.12 (34) | 2.44 (39) |
| chases starting with no mate within 5 % | 26 (9/35) | 15 (5/34) | 18 (7/39) |
| turns per chase | 3.5 | 3.8 | 4.3 |
| chases of 4+ turns % | 26 | 29 | 36 |
| chases with a mate ramming a pursuer | 5 | 5 | 6 |
| chases ending in her death | 9 | 9 | 8 |
| queen alive r100 | 7/16 | 9/16 | 9/16 |
| queen alive r150 | 4/16 | 4/16 | 5/16 |
| queen alive end | 0/16 | 0/16 | 1/16 |
| died: rammed | 14 | 14 | 13 |
| died: boxed | 0 | 0 | 0 |
| died: dead_end | 2 | 2 | 2 |
| died: into_head | 0 | 0 | 0 |
| pearls she eats a game | 11.0 | 10.8 | 19.1 |
| own dragons r100 | 46.7 | 46.7 | 47.6 |
| own total length r100 | 199.7 | 200.2 | 199.9 |
| own dragons r300 | 55.1 | 55.1 | 55.5 |
| own total length r300 | 251.6 | 251.2 | 259.2 |
| won | 11/16 | 11/16 | 12/16 |

각 arm 집계 판수: m3b7qk_vh 16/16, m5q3_vh 16/16, m5qh2_vh 16/16.
누락: m4qf_vh/ladder_australia_1-seed2-side0: replay 없음, result 없음; m4qf_vh/ladder_australia_1-seed2-side1: replay 없음, result 없음; m4qf_vh/ladder_islands_1-seed2-side0: replay 없음, result 없음; m4qf_vh/ladder_islands_1-seed2-side1: replay 없음, result 없음; m4qf_vh/sqheld_blobs_large_90030-seed2-side0: replay 없음, result 없음; m4qf_vh/sqheld_blobs_large_90030-seed2-side1: replay 없음, result 없음; m4qf_vh/sqheld_portalrooms_large_90006-seed2-side0: replay 없음, result 없음; m4qf_vh/sqheld_portalrooms_large_90006-seed2-side1: replay 없음, result 없음; m4qf_vh/sqheld_portals_medium_90007-seed2-side0: replay 없음, result 없음; m4qf_vh/sqheld_portals_medium_90007-seed2-side1: replay 없음, result 없음.
미완료 또는 집계 실패: 없음.
`m4qf_vh`는 대상 중 기보·결과가 있는 판이 6/16판이므로 열에서 제외했고 집계하지 않았다.

첫 갈림은 복사한 `qh_div.py`의 순서대로 이동·분열·죽음 사건을 비교한 원시 라운드다.

- ladder_around_unsw_1-seed1-side0 first differs in round 248
- ladder_around_unsw_1-seed1-side1 first differs in round 46
- ladder_australia_1-seed2-side0 first differs in round 74
- ladder_australia_1-seed2-side1 first differs in round 113
- ladder_islands_1-seed2-side0 first differs in round 48
- ladder_islands_1-seed2-side1 identical
- ladder_tower_defense_1-seed1-side0 identical
- ladder_tower_defense_1-seed1-side1 identical
- sqheld_blobs_large_90030-seed2-side0 identical
- sqheld_blobs_large_90030-seed2-side1 identical
- sqheld_islands_medium_90038-seed1-side0 first differs in round 35
- sqheld_islands_medium_90038-seed1-side1 identical
- sqheld_portalrooms_large_90006-seed2-side0 identical
- sqheld_portalrooms_large_90006-seed2-side1 identical
- sqheld_portals_medium_90007-seed2-side0 identical
- sqheld_portals_medium_90007-seed2-side1 identical

판별 결과 (`result.txt` 원문):

- ladder_around_unsw_1-seed1-side0 — m3b7qk_vh: winner=0 how=round_limit (longest dragon, 73 to 28) rounds=500 final_lengths=379,242
- ladder_around_unsw_1-seed1-side0 — m5q3_vh: winner=1 how=round_limit (longest dragon, 50 to 33) rounds=500 final_lengths=358,289
- ladder_around_unsw_1-seed1-side0 — m5qh2_vh: winner=0 how=round_limit (longer queen, 100 to 0) rounds=500 final_lengths=332,282
- ladder_around_unsw_1-seed1-side1 — m3b7qk_vh: winner=0 how=round_limit (longest dragon, 56 to 28) rounds=500 final_lengths=263,262
- ladder_around_unsw_1-seed1-side1 — m5q3_vh: winner=1 how=round_limit (longest dragon, 117 to 68) rounds=500 final_lengths=269,377
- ladder_around_unsw_1-seed1-side1 — m5qh2_vh: winner=1 how=round_limit (longest dragon, 83 to 33) rounds=500 final_lengths=236,367
- ladder_australia_1-seed2-side0 — m3b7qk_vh: winner=1 how=round_limit (longest dragon, 32 to 28) rounds=500 final_lengths=161,254
- ladder_australia_1-seed2-side0 — m5q3_vh: winner=1 how=round_limit (longest dragon, 47 to 45) rounds=500 final_lengths=230,259
- ladder_australia_1-seed2-side0 — m5qh2_vh: winner=1 how=round_limit (longest dragon, 28 to 27) rounds=500 final_lengths=230,190
- ladder_australia_1-seed2-side1 — m3b7qk_vh: winner=1 how=round_limit (longest dragon, 97 to 30) rounds=500 final_lengths=165,340
- ladder_australia_1-seed2-side1 — m5q3_vh: winner=1 how=round_limit (longest dragon, 35 to 13) rounds=500 final_lengths=189,243
- ladder_australia_1-seed2-side1 — m5qh2_vh: winner=1 how=round_limit (longest dragon, 46 to 18) rounds=500 final_lengths=275,230
- ladder_islands_1-seed2-side0 — m3b7qk_vh: winner=0 how=round_limit (longest dragon, 70 to 6) rounds=500 final_lengths=398,21
- ladder_islands_1-seed2-side0 — m5q3_vh: winner=0 how=round_limit (longest dragon, 60 to 12) rounds=500 final_lengths=388,45
- ladder_islands_1-seed2-side0 — m5qh2_vh: winner=0 how=round_limit (longest dragon, 90 to 19) rounds=500 final_lengths=362,19
- ladder_islands_1-seed2-side1 — m3b7qk_vh: winner=1 how=round_limit (longest dragon, 38 to 25) rounds=500 final_lengths=85,261
- ladder_islands_1-seed2-side1 — m5q3_vh: winner=1 how=round_limit (longest dragon, 38 to 25) rounds=500 final_lengths=85,261
- ladder_islands_1-seed2-side1 — m5qh2_vh: winner=1 how=round_limit (longest dragon, 22 to 8) rounds=500 final_lengths=55,236
- ladder_tower_defense_1-seed1-side0 — m3b7qk_vh: winner=0 how=round_limit (longest dragon, 24 to 4) rounds=500 final_lengths=110,6
- ladder_tower_defense_1-seed1-side0 — m5q3_vh: winner=0 how=round_limit (longest dragon, 24 to 4) rounds=500 final_lengths=110,6
- ladder_tower_defense_1-seed1-side0 — m5qh2_vh: winner=0 how=round_limit (longest dragon, 24 to 4) rounds=500 final_lengths=110,6
- ladder_tower_defense_1-seed1-side1 — m3b7qk_vh: winner=1 how=elimination (by elimination) rounds=236 final_lengths=0,112
- ladder_tower_defense_1-seed1-side1 — m5q3_vh: winner=1 how=elimination (by elimination) rounds=236 final_lengths=0,112
- ladder_tower_defense_1-seed1-side1 — m5qh2_vh: winner=1 how=elimination (by elimination) rounds=236 final_lengths=0,112
- sqheld_blobs_large_90030-seed2-side0 — m3b7qk_vh: winner=0 how=round_limit (longest dragon, 49 to 26) rounds=500 final_lengths=359,418
- sqheld_blobs_large_90030-seed2-side0 — m5q3_vh: winner=0 how=round_limit (longest dragon, 49 to 26) rounds=500 final_lengths=359,418
- sqheld_blobs_large_90030-seed2-side0 — m5qh2_vh: winner=1 how=round_limit (longest dragon, 58 to 32) rounds=500 final_lengths=460,467
- sqheld_blobs_large_90030-seed2-side1 — m3b7qk_vh: winner=0 how=round_limit (longest dragon, 51 to 49) rounds=500 final_lengths=528,486
- sqheld_blobs_large_90030-seed2-side1 — m5q3_vh: winner=0 how=round_limit (longest dragon, 51 to 49) rounds=500 final_lengths=528,486
- sqheld_blobs_large_90030-seed2-side1 — m5qh2_vh: winner=0 how=round_limit (longest dragon, 51 to 49) rounds=500 final_lengths=528,486
- sqheld_islands_medium_90038-seed1-side0 — m3b7qk_vh: winner=0 how=round_limit (longest dragon, 22 to 3) rounds=500 final_lengths=211,5
- sqheld_islands_medium_90038-seed1-side0 — m5q3_vh: winner=0 how=round_limit (longest dragon, 59 to 5) rounds=500 final_lengths=210,18
- sqheld_islands_medium_90038-seed1-side0 — m5qh2_vh: winner=0 how=round_limit (longest dragon, 63 to 4) rounds=500 final_lengths=221,4
- sqheld_islands_medium_90038-seed1-side1 — m3b7qk_vh: winner=0 how=round_limit (longest dragon, 80 to 5) rounds=500 final_lengths=169,21
- sqheld_islands_medium_90038-seed1-side1 — m5q3_vh: winner=0 how=round_limit (longest dragon, 80 to 5) rounds=500 final_lengths=169,21
- sqheld_islands_medium_90038-seed1-side1 — m5qh2_vh: winner=0 how=round_limit (longest dragon, 80 to 5) rounds=500 final_lengths=169,21
- sqheld_portalrooms_large_90006-seed2-side0 — m3b7qk_vh: winner=1 how=round_limit (longest dragon, 118 to 59) rounds=500 final_lengths=269,362
- sqheld_portalrooms_large_90006-seed2-side0 — m5q3_vh: winner=1 how=round_limit (longest dragon, 118 to 59) rounds=500 final_lengths=269,362
- sqheld_portalrooms_large_90006-seed2-side0 — m5qh2_vh: winner=0 how=round_limit (longest dragon, 96 to 22) rounds=500 final_lengths=415,303
- sqheld_portalrooms_large_90006-seed2-side1 — m3b7qk_vh: winner=1 how=round_limit (longest dragon, 54 to 29) rounds=500 final_lengths=342,304
- sqheld_portalrooms_large_90006-seed2-side1 — m5q3_vh: winner=1 how=round_limit (longest dragon, 54 to 29) rounds=500 final_lengths=342,304
- sqheld_portalrooms_large_90006-seed2-side1 — m5qh2_vh: winner=1 how=round_limit (longest dragon, 52 to 19) rounds=500 final_lengths=256,399
- sqheld_portals_medium_90007-seed2-side0 — m3b7qk_vh: winner=0 how=round_limit (longest dragon, 15 to 7) rounds=500 final_lengths=222,139
- sqheld_portals_medium_90007-seed2-side0 — m5q3_vh: winner=0 how=round_limit (longest dragon, 15 to 7) rounds=500 final_lengths=222,139
- sqheld_portals_medium_90007-seed2-side0 — m5qh2_vh: winner=0 how=round_limit (longest dragon, 15 to 7) rounds=500 final_lengths=222,139
- sqheld_portals_medium_90007-seed2-side1 — m3b7qk_vh: winner=1 how=round_limit (longest dragon, 21 to 5) rounds=500 final_lengths=150,199
- sqheld_portals_medium_90007-seed2-side1 — m5q3_vh: winner=1 how=round_limit (longest dragon, 21 to 5) rounds=500 final_lengths=150,199
- sqheld_portals_medium_90007-seed2-side1 — m5qh2_vh: winner=1 how=round_limit (longest dragon, 21 to 5) rounds=500 final_lengths=150,199

## 적 머리가 더 많은 턴의 이동

턴 시작의 토러스 7×7 시야(각 축 거리 ≤3)에서 적 머리 수 > 아군 머리 수인 여왕 턴만 센다. 아군에는 여왕 자신, 적에는 적 여왕을 포함한다. 가장 가까운 적·아군은 그 시야 안에서 토러스 맨해튼 거리로 고르고, 동률은 낮은 id로 정한다. 목표 머리의 위치는 턴 시작 위치에 고정한다. 턴 시작에서 마지막으로 기록된 이동 머리 위치까지의 순거리 변화를 센다(다중 걸음 포함). 이동 사건이 없는 턴은 거리 유지에 포함하며, 죽는 충돌 시도의 기록되지 않은 목적지는 추정하지 않는다. 아군에게 가까워짐은 적 거리의 세 분류와 중복될 수 있다.

| measure | m3b7qk_vh | m5q3_vh |
|---|---|---|
| 해당 턴 수 | 34 | 11 |
| 가장 가까운 적에게서 멀어짐 | 26 | 8 |
| 가장 가까운 적에게 가까워짐 | 6 | 1 |
| 가장 가까운 적과 거리 유지 | 2 | 2 |
| 가장 가까운 아군에게 가까워짐 (중복 집계) | 2 | 2 |
| 적에게서 멀어지며 아군에게 가까워짐 | 2 | 1 |
| 시야에 다른 아군 머리 있음 | 2 | 2 |
| 시야에 다른 아군 머리 없음 | 32 | 9 |
| 머리 이동 사건 없음 (거리 유지에 포함) | 2 | 1 |
| 머리 이동 사건 2개 이상 | 2 | 2 |
| 해당 턴에 여왕 죽음 | 0 | 0 |

## 5줄 요약

같은 16판 중 사건이 달라진 판은 6판, 동일한 판은 10판이다.  
여왕 생존 r100/r150/종료는 기준 7/16, 4/16, 0/16 → QF3 9/16, 4/16, 0/16이다.  
여왕 사망 rammed/boxed/dead_end/into_head는 기준 14/0/2/0 → QF3 14/0/2/0이다.  
추격 수는 기준 2.19 (35) → QF3 2.12 (34), 추격당 턴은 3.5 → 3.8, 판당 여왕 진주 섭취는 11.0 → 10.8이다.  
적 머리가 더 많은 턴은 기준 34 → QF3 11, 적에게서 멀어짐은 26 → 8, 아군에게 가까워짐은 2 → 2이다.
