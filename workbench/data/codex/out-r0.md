# Round-0 split 단독 집계

`m4bq_vb`: baseline/live; `m5r0_vb`: baseline + SPLIT_ROUND0; `m5og_vb`: SPLIT_ROUND0 + QS_KEEP_ROUND 40 + QS_KEEP_CLEAR 6; `m5op_vb`: guard 없이 HEADING_TIE를 더한 pack. 상대는 plain main이다.

원본 `op_scan.py`·`op_tab.py`를 변경 없이 실행했다. 숫자는 기보에서 읽었다. 시점은 라운드 종료이며, 일찍 끝난 판은 최종 상태를 이후 시점에도 유지한다. 평균·조건부 분모는 원본 집계 정의를 따른다.

| count | m4bq_vb | m5r0_vb | m5og_vb | m5op_vb |
|---|---|---|---|---|
| queen first split round, mean (median; games she never split) | 9.1 (10.0; 0) | 8.9 (10.0; 0) | 7.0 (5.5; 0) | 6.1 (5.5; 0) |
| starter first split round, mean over starters (never) | 12.8 (0 of 32) | 12.4 (0 of 32) | 10.0 (1 of 32) | 11.0 (1 of 32) |
| starters of 4+ that split in round 0 / such starters | 2 / 14 | 12 / 14 | 14 / 14 | 14 / 14 |
| own dragons at r10, r20, r40, r60, r100, r300 | 3.1, 6.0, 19.2, 29.1, 34.7, 44.1 | 3.6, 7.0, 20.4, 29.6, 35.3, 45.3 | 3.7, 7.1, 21.1, 28.0, 32.3, 45.1 | 3.8, 7.8, 22.5, 31.0, 34.1, 44.6 |
| total length at r20, r40, r100, r300 | 16.1, 49.4, 152.1, 198.9 | 18.6, 52.0, 146.2, 193.4 | 18.2, 56.1, 141.4, 185.6 | 19.4, 56.8, 142.0, 188.1 |
| pearls eaten at r20, r40, r100, r300 | 11.7, 62.4, 325.8, 1335.2 | 13.8, 68.1, 323.1, 1331.6 | 13.8, 70.3, 304.2, 1324.5 | 15.0, 75.1, 336.3, 1330.7 |
| portal maps (14 games): any starter line through a portal by r10, r20 | 4, 6 | 4, 8 | 4, 9 | 4, 6 |
| portal maps (14 games): a non-queen starter line through a portal by r10, r20 | 3, 3 | 3, 5 | 3, 5 | 3, 3 |
| queen length at r40, r100, r150 (dead = 0) | 2.8, 1.8, 1.1 | 3.1, 2.1, 1.5 | 2.6, 1.3, 1.1 | 1.9, 1.6, 1.9 |
| queen alive at r40, r100, r150 (games) | 13, 8, 5 | 14, 10, 7 | 14, 6, 5 | 12, 7, 6 |
| queen turns at 4+ in r0-40 a game; split on them | 17.6; 48 of 281 | 16.1; 50 of 257 | 7.2; 53 of 116 | 4.3; 57 of 69 |
| queen dead by r40: games (round, length, cause) | 3 (36,4,rammed-by-enemy) (38,2,wall) (25,3,rammed-by-enemy) | 2 (38,2,wall) (25,3,rammed-by-enemy) | 2 (31,2,rammed-by-enemy) (29,2,rammed-by-enemy) | 4 (39,2,rammed-by-enemy) (26,2,rammed-by-enemy) (37,3,rammed-by-enemy) (36,2,rammed-by-enemy) |
| queen turns r0-40 at length 2 with an enemy head within 4 (games with any) | 3 (3) | 3 (3) | 6 (4) | 49 (8) |
| own deaths in r0-5; children born r0-1 dead within 10 rounds | 4; 6 | 2; 2 | 2; 2 | 2; 2 |
| own deaths by r40 a game | 6.9 | 8.0 | 7.1 | 8.9 |

표에 사용한 공통 16판(8지도 × seed 1 × 양편): m4bq_vb 16판, m5r0_vb 16판, m5og_vb 16판, m5op_vb 16판; 총 64개 기보. 공통 집합의 누락·실패 없음. 기보 완료 여부, result.txt의 winner·rounds, 최종 여왕 길이가 일치하며 result.json에 봇 오류가 없다. 스캔된 전체 기보는 arm 순서대로 64·16·16·16개이며, baseline의 공통 집합 밖 48판은 표에서 제외했다.

판별 결과(승 = 기보 winner가 해당 arm의 side와 같음):

- ladder_schooltime_1-seed1-side0: m4bq_vb 승; m5r0_vb 승; m5og_vb 승; m5op_vb 승
- ladder_schooltime_1-seed1-side1: m4bq_vb 승; m5r0_vb 승; m5og_vb 승; m5op_vb 승
- ladder_stripes_1-seed1-side0: m4bq_vb 승; m5r0_vb 승; m5og_vb 승; m5op_vb 승
- ladder_stripes_1-seed1-side1: m4bq_vb 승; m5r0_vb 승; m5og_vb 승; m5op_vb 승
- ladder_tower_defense_1-seed1-side0: m4bq_vb 승; m5r0_vb 승; m5og_vb 승; m5op_vb 승
- ladder_tower_defense_1-seed1-side1: m4bq_vb 승; m5r0_vb 승; m5og_vb 승; m5op_vb 승
- sqheld_portalrooms_large_90013-seed1-side0: m4bq_vb 패; m5r0_vb 승; m5og_vb 패; m5op_vb 승
- sqheld_portalrooms_large_90013-seed1-side1: m4bq_vb 패; m5r0_vb 승; m5og_vb 패; m5op_vb 승
- sqheld_portals_large_90010-seed1-side0: m4bq_vb 승; m5r0_vb 승; m5og_vb 패; m5op_vb 승
- sqheld_portals_large_90010-seed1-side1: m4bq_vb 패; m5r0_vb 패; m5og_vb 승; m5op_vb 패
- sqheld_portals_medium_90007-seed1-side0: m4bq_vb 승; m5r0_vb 승; m5og_vb 승; m5op_vb 승
- sqheld_portals_medium_90007-seed1-side1: m4bq_vb 패; m5r0_vb 패; m5og_vb 승; m5op_vb 승
- sqheld_portals_medium_90020-seed1-side0: m4bq_vb 승; m5r0_vb 승; m5og_vb 승; m5op_vb 패
- sqheld_portals_medium_90020-seed1-side1: m4bq_vb 패; m5r0_vb 패; m5og_vb 승; m5op_vb 승
- sqheld_portals_small_90029-seed1-side0: m4bq_vb 승; m5r0_vb 승; m5og_vb 승; m5op_vb 승
- sqheld_portals_small_90029-seed1-side1: m4bq_vb 패; m5r0_vb 승; m5og_vb 패; m5op_vb 승

## 4줄 요약

baseline → SPLIT_ROUND0 단독에서 길이 4+ 시작 드래곤의 r0 분열은 2/14 → 12/14, 시작 드래곤 첫 분열 평균은 12.8 → 12.4, r0–5 사망·초기 새끼 10라운드 내 사망은 4·6 → 2·2이며, guard/HEADING_TIE arm은 각각 14/14·14/14와 2·2·2·2다.
머릿수·총 길이·누적 섭취·r40까지 사망 평균은 SPLIT_ROUND0 단독부터 달라졌다: baseline/단독/guard/HEADING_TIE의 r20 값은 머릿수 6.0/7.0/7.1/7.8, 총 길이 16.1/18.6/18.2/19.4, 섭취 11.7/13.8/13.8/15.0이고, r40까지 사망 평균은 6.9/8.0/7.1/8.9다.
포털 r20 통과 판은 baseline/단독/guard/HEADING_TIE에서 전체 시작 계보 6/8/9/6·비여왕 계보 3/5/5/3으로 단독부터 달라지고, r10은 각각 4/4/4/4·3/3/3/3이다; 길이 2·적 머리 4칸 이내 여왕 차례는 baseline과 단독이 3회(3판)로 같으며 guard에서 6회(4판), HEADING_TIE에서 49회(8판)로 달라진다.
여왕 첫 분열·길이·생존·4+ 차례 분열·r40까지 사망도 단독부터 달라졌다: baseline/단독/guard/HEADING_TIE에서 첫 분열 평균 9.1/8.9/7.0/6.1, r40 길이 2.8/3.1/2.6/1.9, r40·r100·r150 생존 13·8·5/14·10·7/14·6·5/12·7·6, 4+ 차례 분열 48/281·50/257·53/116·57/69, r40까지 사망 3/2/2/4판이다.
