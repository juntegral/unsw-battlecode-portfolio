# Opening pack + guard 집계

A: plain main 상대, `m4bq_vb`(baseline/live) → `m5op_vb`(HEADING_TIE 포함 pack, guard 없음) → `m5og_vb`(SPLIT_ROUND0 + QS_KEEP_ROUND 40 + QS_KEEP_CLEAR 6).
B: queen hunter 상대, `m3b7qk_vh`(baseline) → `m5og_vh`.

집계는 원본 `op_scan.py`·`op_tab.py`를 그대로 복사해 실행했다. 숫자는 기보에서 읽었고, `result.txt`는 완료·승자·라운드 일치 확인에 사용했다. 시점은 원본 도구대로 라운드 종료 시점이며, 일찍 끝난 판은 최종 상태를 이후 시점에 유지한다. 평균과 조건부 분모도 원본 도구대로다.

## Table A

| count | m4bq_vb | m5op_vb | m5og_vb |
|---|---|---|---|
| queen first split round, mean (median; games she never split) | 9.1 (10.0; 0) | 6.1 (5.5; 0) | 7.0 (5.5; 0) |
| starter first split round, mean over starters (never) | 12.8 (0 of 32) | 11.0 (1 of 32) | 10.0 (1 of 32) |
| starters of 4+ that split in round 0 / such starters | 2 / 14 | 14 / 14 | 14 / 14 |
| own dragons at r10, r20, r40, r60, r100, r300 | 3.1, 6.0, 19.2, 29.1, 34.7, 44.1 | 3.8, 7.8, 22.5, 31.0, 34.1, 44.6 | 3.7, 7.1, 21.1, 28.0, 32.3, 45.1 |
| total length at r20, r40, r100, r300 | 16.1, 49.4, 152.1, 198.9 | 19.4, 56.8, 142.0, 188.1 | 18.2, 56.1, 141.4, 185.6 |
| pearls eaten at r20, r40, r100, r300 | 11.7, 62.4, 325.8, 1335.2 | 15.0, 75.1, 336.3, 1330.7 | 13.8, 70.3, 304.2, 1324.5 |
| portal maps (14 games): any starter line through a portal by r10, r20 | 4, 6 | 4, 6 | 4, 9 |
| portal maps (14 games): a non-queen starter line through a portal by r10, r20 | 3, 3 | 3, 3 | 3, 5 |
| queen length at r40, r100, r150 (dead = 0) | 2.8, 1.8, 1.1 | 1.9, 1.6, 1.9 | 2.6, 1.3, 1.1 |
| queen alive at r40, r100, r150 (games) | 13, 8, 5 | 12, 7, 6 | 14, 6, 5 |
| queen turns at 4+ in r0-40 a game; split on them | 17.6; 48 of 281 | 4.3; 57 of 69 | 7.2; 53 of 116 |
| queen dead by r40: games (round, length, cause) | 3 (36,4,rammed-by-enemy) (38,2,wall) (25,3,rammed-by-enemy) | 4 (39,2,rammed-by-enemy) (26,2,rammed-by-enemy) (37,3,rammed-by-enemy) (36,2,rammed-by-enemy) | 2 (31,2,rammed-by-enemy) (29,2,rammed-by-enemy) |
| queen turns r0-40 at length 2 with an enemy head within 4 (games with any) | 3 (3) | 49 (8) | 6 (4) |
| own deaths in r0-5; children born r0-1 dead within 10 rounds | 4; 6 | 2; 2 | 2; 2 |
| own deaths by r40 a game | 6.9 | 8.9 | 7.1 |

근거 판: 16개 지도·시드·진영 조합(8지도 × seed 1 × 양편); arm당 16판, 총 48개 기보. 누락·실패: 없음. 모든 `result.txt`의 winner와 rounds가 완료된 기보와 일치한다.

판별 승패(승 = 기보 winner가 해당 arm의 side와 같음):

- ladder_schooltime_1-seed1-side0: m4bq_vb 승; m5op_vb 승; m5og_vb 승
- ladder_schooltime_1-seed1-side1: m4bq_vb 승; m5op_vb 승; m5og_vb 승
- ladder_stripes_1-seed1-side0: m4bq_vb 승; m5op_vb 승; m5og_vb 승
- ladder_stripes_1-seed1-side1: m4bq_vb 승; m5op_vb 승; m5og_vb 승
- ladder_tower_defense_1-seed1-side0: m4bq_vb 승; m5op_vb 승; m5og_vb 승
- ladder_tower_defense_1-seed1-side1: m4bq_vb 승; m5op_vb 승; m5og_vb 승
- sqheld_portalrooms_large_90013-seed1-side0: m4bq_vb 패; m5op_vb 승; m5og_vb 패
- sqheld_portalrooms_large_90013-seed1-side1: m4bq_vb 패; m5op_vb 승; m5og_vb 패
- sqheld_portals_large_90010-seed1-side0: m4bq_vb 승; m5op_vb 승; m5og_vb 패
- sqheld_portals_large_90010-seed1-side1: m4bq_vb 패; m5op_vb 패; m5og_vb 승
- sqheld_portals_medium_90007-seed1-side0: m4bq_vb 승; m5op_vb 승; m5og_vb 승
- sqheld_portals_medium_90007-seed1-side1: m4bq_vb 패; m5op_vb 승; m5og_vb 승
- sqheld_portals_medium_90020-seed1-side0: m4bq_vb 승; m5op_vb 패; m5og_vb 승
- sqheld_portals_medium_90020-seed1-side1: m4bq_vb 패; m5op_vb 승; m5og_vb 승
- sqheld_portals_small_90029-seed1-side0: m4bq_vb 승; m5op_vb 승; m5og_vb 승
- sqheld_portals_small_90029-seed1-side1: m4bq_vb 패; m5op_vb 승; m5og_vb 패

## Table B

| count | m3b7qk_vh | m5og_vh |
|---|---|---|
| queen first split round, mean (median; games she never split) | 4.3 (2.5; 0) | 2.2 (0.0; 0) |
| starter first split round, mean over starters (never) | 3.9 (0 of 26) | 2.7 (0 of 26) |
| starters of 4+ that split in round 0 / such starters | 2 / 14 | 14 / 14 |
| own dragons at r10, r20, r40, r60, r100, r300 | 5.5, 10.8, 27.8, 39.7, 45.2, 51.2 | 6.3, 12.7, 29.7, 38.4, 40.7, 50.0 |
| total length at r20, r40, r100, r300 | 29.5, 72.2, 208.8, 258.2 | 32.4, 78.4, 175.1, 235.9 |
| pearls eaten at r20, r40, r100, r300 | 30.7, 124.5, 516.9, 1996.8 | 34.0, 128.2, 461.7, 1858.8 |
| portal maps (10 games): any starter line through a portal by r10, r20 | 2, 3 | 2, 6 |
| portal maps (10 games): a non-queen starter line through a portal by r10, r20 | 2, 2 | 2, 4 |
| queen length at r40, r100, r150 (dead = 0) | 1.6, 1.2, 0.5 | 2.2, 0.8, 0.5 |
| queen alive at r40, r100, r150 (games) | 6, 4, 2 | 9, 3, 2 |
| queen turns at 4+ in r0-40 a game; split on them | 16.6; 55 of 199 | 6.8; 51 of 81 |
| queen dead by r40: games (round, length, cause) | 6 (33,3,rammed-by-enemy) (31,4,rammed-by-enemy) (38,2,wall) (34,5,rammed-by-enemy) (7,3,rammed-by-enemy) (27,4,rammed-by-enemy) | 3 (19,3,rammed-by-enemy) (23,3,rammed-by-enemy) (7,3,rammed-by-enemy) |
| queen turns r0-40 at length 2 with an enemy head within 4 (games with any) | 3 (2) | 1 (1) |
| own deaths in r0-5; children born r0-1 dead within 10 rounds | 4; 6 | 2; 2 |
| own deaths by r40 a game | 20.6 | 19.8 |

근거 판: 12개 지도·시드·진영 조합(6지도 × seed 1 × 양편); arm당 12판, 총 24개 기보. 누락·실패: 없음. 모든 `result.txt`의 winner와 rounds가 완료된 기보와 일치한다.

판별 승패(승 = 기보 winner가 해당 arm의 side와 같음):

- ladder_schooltime_1-seed1-side0: m3b7qk_vh 승; m5og_vh 승
- ladder_schooltime_1-seed1-side1: m3b7qk_vh 승; m5og_vh 승
- sqheld_open_medium_90017-seed1-side0: m3b7qk_vh 승; m5og_vh 승
- sqheld_open_medium_90017-seed1-side1: m3b7qk_vh 승; m5og_vh 패
- sqheld_portalrooms_large_90013-seed1-side0: m3b7qk_vh 패; m5og_vh 패
- sqheld_portalrooms_large_90013-seed1-side1: m3b7qk_vh 승; m5og_vh 승
- sqheld_portals_large_90010-seed1-side0: m3b7qk_vh 승; m5og_vh 패
- sqheld_portals_large_90010-seed1-side1: m3b7qk_vh 패; m5og_vh 승
- sqheld_portals_medium_90020-seed1-side0: m3b7qk_vh 승; m5og_vh 패
- sqheld_portals_medium_90020-seed1-side1: m3b7qk_vh 승; m5og_vh 패
- sqheld_portals_small_90029-seed1-side0: m3b7qk_vh 승; m5og_vh 승
- sqheld_portals_small_90029-seed1-side1: m3b7qk_vh 승; m5og_vh 패

여왕 사망 전수(각 arm의 우리 여왕; 전체 라운드):

`rammed`는 다른 머리의 차례에 head 충돌로 사망, `ran into a head`는 여왕 자신의 차례에 head 충돌로 사망이다. `boxed in`은 wall/own/body 충돌을 묶은 표기이며 원시 원인을 함께 적었다(다른 선택지가 없었다는 판정은 하지 않았다). 마지막 분열의 거리는 분열 이벤트 직후 여왕 머리와 당시 살아 있는 적 머리의 최소 toroidal Manhattan 거리이며, ≤6을 “예”로 센다. 분열이 없으면 해당 없음이다.

- m3b7qk_vh sqheld_open_medium_90017-seed1-side0: r72, 길이 3, boxed in (own; actor #0, team 0); 마지막 분열 r66, 적 머리 ≤6 아니오, 최소 거리 8.
- m5og_vh sqheld_open_medium_90017-seed1-side0: r89, 길이 3, rammed (head; actor #495, team 1); 마지막 분열 r17, 적 머리 ≤6 예, 최소 거리 3.
- m3b7qk_vh sqheld_open_medium_90017-seed1-side1: r61, 길이 3, boxed in (own; actor #1, team 1); 마지막 분열 r55, 적 머리 ≤6 예, 최소 거리 5.
- m5og_vh sqheld_open_medium_90017-seed1-side1: r19, 길이 3, rammed (head; actor #14, team 0); 마지막 분열 r17, 적 머리 ≤6 예, 최소 거리 3.
- m3b7qk_vh sqheld_portalrooms_large_90013-seed1-side0: r33, 길이 3, rammed (head; actor #26, team 1); 마지막 분열 r32, 적 머리 ≤6 예, 최소 거리 4.
- m5og_vh sqheld_portalrooms_large_90013-seed1-side0: r47, 길이 3, rammed (head; actor #76, team 1); 마지막 분열 r46, 적 머리 ≤6 예, 최소 거리 4.
- m3b7qk_vh sqheld_portalrooms_large_90013-seed1-side1: r31, 길이 4, rammed (head; actor #34, team 0); 마지막 분열 r30, 적 머리 ≤6 예, 최소 거리 5.
- m5og_vh sqheld_portalrooms_large_90013-seed1-side1: r41, 길이 2, rammed (head; actor #2, team 0); 마지막 분열 r36, 적 머리 ≤6 예, 최소 거리 2.
- m3b7qk_vh sqheld_portals_large_90010-seed1-side0: r149, 길이 3, boxed in (own; actor #0, team 0); 마지막 분열 r147, 적 머리 ≤6 예, 최소 거리 3.
- m5og_vh sqheld_portals_large_90010-seed1-side0: r98, 길이 3, rammed (head; actor #143, team 1); 마지막 분열 r42, 적 머리 ≤6 아니오, 최소 거리 20.
- m3b7qk_vh sqheld_portals_large_90010-seed1-side1: r38, 길이 2, boxed in (wall; actor #1, team 1); 마지막 분열 r37, 적 머리 ≤6 예, 최소 거리 6.
- m5og_vh sqheld_portals_large_90010-seed1-side1: r112, 길이 4, rammed (head; actor #178, team 0); 마지막 분열 r36, 적 머리 ≤6 아니오, 최소 거리 17.
- m3b7qk_vh sqheld_portals_medium_90020-seed1-side0: r34, 길이 5, rammed (head; actor #19, team 1); 마지막 분열 r32, 적 머리 ≤6 예, 최소 거리 6.
- m5og_vh sqheld_portals_medium_90020-seed1-side0: r57, 길이 4, rammed (head; actor #119, team 1); 마지막 분열 r51, 적 머리 ≤6 예, 최소 거리 6.
- m3b7qk_vh sqheld_portals_medium_90020-seed1-side1: r110, 길이 3, rammed (head; actor #305, team 0); 마지막 분열 r73, 적 머리 ≤6 아니오, 최소 거리 9.
- m5og_vh sqheld_portals_medium_90020-seed1-side1: r23, 길이 3, rammed (head; actor #8, team 0); 마지막 분열 r18, 적 머리 ≤6 예, 최소 거리 4.
- m3b7qk_vh sqheld_portals_small_90029-seed1-side0: r7, 길이 3, rammed (head; actor #1, team 1); 마지막 분열 r1, 적 머리 ≤6 아니오, 최소 거리 7.
- m5og_vh sqheld_portals_small_90029-seed1-side0: r7, 길이 3, rammed (head; actor #1, team 1); 마지막 분열 r0, 적 머리 ≤6 아니오, 최소 거리 9.
- m3b7qk_vh sqheld_portals_small_90029-seed1-side1: r27, 길이 4, rammed (head; actor #0, team 0); 마지막 분열 r19, 적 머리 ≤6 예, 최소 거리 6.
- m5og_vh sqheld_portals_small_90029-seed1-side1: r73, 길이 3, rammed (head; actor #18, team 0); 마지막 분열 r35, 적 머리 ≤6 아니오, 최소 거리 10.

## 5줄 요약

A에서 길이 4+ 시작 드래곤의 r0 분열은 baseline/pack/guard 순서로 2/14 → 14/14 → 14/14이며, r0–5 사망과 초기 새끼 10라운드 내 사망은 4·6 → 2·2 → 2·2다.
A의 r20 평균 머릿수는 6.0 → 7.8 → 7.1, 누적 섭취는 11.7 → 15.0 → 13.8이며, guard의 두 값 모두 baseline보다 크고 pack보다 작다.
A의 r40/r100/r150 여왕 생존 판은 13/8/5 → 12/7/6 → 14/6/5이며, 길이 2에서 적 머리 4칸 이내였던 r0–40 여왕 차례는 3 → 49 → 6이다.
B의 baseline → guard 여왕 생존 판은 r40 6 → 9, r100 4 → 3, r150 2 → 2이며, 전체 여왕 사망은 10 → 10건(원시 head 충돌 6 → 10, own/wall 충돌 4 → 0)이다.
포털 지도에서 r10 통과 판 수는 A의 모든 arm과 B의 양 arm에서 같고, r20 통과는 A의 전체 시작 계보 6 → 6 → 9·비여왕 계보 3 → 3 → 5, B는 각각 3 → 6·2 → 4다.
