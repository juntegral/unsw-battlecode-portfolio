Hunter wall: 19/28 forced (67.9%); 19/28 before r50 (both arms).
Hunter self: 10/16 forced (62.5%); 10/16 before r50 (both arms).
Normal wall: 0/2 forced (0.0%); 0/2 before r50 (both arms).
Normal self: 1/1 forced (100.0%); 0/1 before r50 (both arms).
queen endings (5 off/6 on games): on is already shorter at r100. early: our pearls 24→13, splits 13→11. late: our pearls 165→113, splits 3→0. Final surviving queens 4→4. At r100, alive 5/5 off and 6/6 on. The early deficit accompanies less eating, with fewer splits; all queens are alive at r100, so death does not explain that first deficit. Later, on has lost 2/6 queens by r350 versus 0/5 off, and also eats less after r300; both reduce its late mean.
all trauma (4 off/4 on games): on is already shorter at r100. early: our pearls 21→0, splits 12→4. late: our pearls 97→95, splits 0→0. Final surviving queens 3→4. At r100, alive 4/4 off and 4/4 on. The early deficit accompanies less eating, with fewer splits; all queens are alive at r100, so death does not explain that first deficit. On loses no queen here; its r300-on pearls are nearly equal, and neither arm splits then, so late paid movement/damage or timing remains unallocated.

Counted 168 games and 146 queen deaths; 2026-10-07T00:48:53+09:00.
Safety, room, pressure and distance use replay true state, including what she cannot see. Safety is at the start of the fatal action; for an enemy-caused death this is the enemy action start, not a new queen decision. Reach is full_reach(real length), through the check margins walker (walls/portals, other bodies block, her body is an endpoint); distance <= reach is risky. Her tail is excluded as in the check; other tails stay blocked.
Room counts the starting head and caps at 30, with static bodies and her tail excluded. -5/-10 use that round’s queen action start, or roundStart if no queen action; room 0 and pressure 0 use the state immediately before the death event. Missing negative rounds are excluded from medians. Shrinking room does not by itself prove she walked into a pocket.
r100–450 lengths are roundStart, as in the check; r500 is terminal after actions (these replays label their 500 rounds 0–499). Dead queens count as zero. Early = replay r0–299, late = replay r300–499. Pearls/splits concern original ids 0/1, not descendants. Lap uses the check definition (first three loop steps excluded).

### hunter, base: 68 games, 59 deaths

| cause | deaths | forced | only risky | had a safe move |
| --- | --- | --- | --- | --- |
| wall | 16 | 11 | 0 | 5 |
| self | 7 | 5 | 0 | 2 |
| body | 1 | 1 | 0 | 0 |
| headon | 33 | 0 | 7 | 26 |
| none | 2 | 0 | 0 | 2 |

| cause | deaths | <50 | 50–99 | 100–199 | 200–299 | 300+ |
| --- | --- | --- | --- | --- | --- | --- |
| wall | 16 | 10 | 3 | 3 | 0 | 0 |
| self | 7 | 5 | 1 | 1 | 0 | 0 |
| body | 1 | 0 | 0 | 0 | 0 | 1 |
| headon | 33 | 10 | 10 | 10 | 0 | 3 |
| none | 2 | 0 | 0 | 0 | 0 | 2 |

| cause | deaths | room -10 | room -5 | room 0 |
| --- | --- | --- | --- | --- |
| wall | 16 | 30 (n=8) | 19 (n=14) | 1 (n=16) |
| self | 7 | 24 (n=3) | 5 (n=5) | 1 (n=7) |
| body | 1 | 30 (n=1) | 30 (n=1) | 1 (n=1) |
| headon | 33 | 30 (n=33) | 30 (n=33) | 30 (n=33) |
| none | 2 | 29.5 (n=2) | 30 (n=2) | 30 (n=2) |

| cause | deaths | multi-step | single-step | no move | lap in prior 4 rounds |
| --- | --- | --- | --- | --- | --- |
| wall | 16 | 0 | 16 | 0 | 0 |
| self | 7 | 0 | 7 | 0 | 0 |

### hunter, candidate: 68 games, 56 deaths

| cause | deaths | forced | only risky | had a safe move |
| --- | --- | --- | --- | --- |
| wall | 12 | 8 | 0 | 4 |
| self | 9 | 5 | 0 | 4 |
| body | 2 | 2 | 0 | 0 |
| headon | 31 | 1 | 11 | 19 |
| none | 2 | 0 | 0 | 2 |

| cause | deaths | <50 | 50–99 | 100–199 | 200–299 | 300+ |
| --- | --- | --- | --- | --- | --- | --- |
| wall | 12 | 9 | 0 | 1 | 2 | 0 |
| self | 9 | 5 | 0 | 3 | 1 | 0 |
| body | 2 | 0 | 0 | 0 | 1 | 1 |
| headon | 31 | 4 | 13 | 7 | 2 | 5 |
| none | 2 | 0 | 0 | 0 | 0 | 2 |

| cause | deaths | room -10 | room -5 | room 0 |
| --- | --- | --- | --- | --- |
| wall | 12 | 30 (n=4) | 4 (n=10) | 1 (n=12) |
| self | 9 | 30 (n=5) | 30 (n=7) | 1 (n=9) |
| body | 2 | 16.5 (n=2) | 19.5 (n=2) | 1 (n=2) |
| headon | 31 | 30 (n=31) | 30 (n=31) | 30 (n=31) |
| none | 2 | 29.5 (n=2) | 30 (n=2) | 30 (n=2) |

| cause | deaths | multi-step | single-step | no move | lap in prior 4 rounds |
| --- | --- | --- | --- | --- | --- |
| wall | 12 | 0 | 12 | 0 | 1 |
| self | 9 | 0 | 9 | 0 | 1 |

### normal, base: 16 games, 16 deaths

| cause | deaths | forced | only risky | had a safe move |
| --- | --- | --- | --- | --- |
| wall | 2 | 0 | 0 | 2 |
| self | 0 | 0 | 0 | 0 |
| body | 0 | 0 | 0 | 0 |
| headon | 14 | 0 | 0 | 14 |
| none | 0 | 0 | 0 | 0 |

| cause | deaths | <50 | 50–99 | 100–199 | 200–299 | 300+ |
| --- | --- | --- | --- | --- | --- | --- |
| wall | 2 | 0 | 1 | 1 | 0 | 0 |
| self | 0 | 0 | 0 | 0 | 0 | 0 |
| body | 0 | 0 | 0 | 0 | 0 | 0 |
| headon | 14 | 1 | 4 | 9 | 0 | 0 |
| none | 0 | 0 | 0 | 0 | 0 | 0 |

| cause | deaths | room -10 | room -5 | room 0 |
| --- | --- | --- | --- | --- |
| wall | 2 | 30 (n=2) | 30 (n=2) | 19 (n=2) |
| self | 0 | — (n=0) | — (n=0) | — (n=0) |
| body | 0 | — (n=0) | — (n=0) | — (n=0) |
| headon | 14 | 30 (n=14) | 30 (n=14) | 30 (n=14) |
| none | 0 | — (n=0) | — (n=0) | — (n=0) |

| cause | deaths | multi-step | single-step | no move | lap in prior 4 rounds |
| --- | --- | --- | --- | --- | --- |
| wall | 2 | 0 | 2 | 0 | 0 |
| self | 0 | 0 | 0 | 0 | 0 |

### normal, candidate: 16 games, 15 deaths

| cause | deaths | forced | only risky | had a safe move |
| --- | --- | --- | --- | --- |
| wall | 0 | 0 | 0 | 0 |
| self | 1 | 1 | 0 | 0 |
| body | 0 | 0 | 0 | 0 |
| headon | 14 | 0 | 2 | 12 |
| none | 0 | 0 | 0 | 0 |

| cause | deaths | <50 | 50–99 | 100–199 | 200–299 | 300+ |
| --- | --- | --- | --- | --- | --- | --- |
| wall | 0 | 0 | 0 | 0 | 0 | 0 |
| self | 1 | 0 | 0 | 0 | 1 | 0 |
| body | 0 | 0 | 0 | 0 | 0 | 0 |
| headon | 14 | 3 | 2 | 6 | 2 | 1 |
| none | 0 | 0 | 0 | 0 | 0 | 0 |

| cause | deaths | room -10 | room -5 | room 0 |
| --- | --- | --- | --- | --- |
| wall | 0 | — (n=0) | — (n=0) | — (n=0) |
| self | 1 | 29 (n=1) | 11 (n=1) | 1 (n=1) |
| body | 0 | — (n=0) | — (n=0) | — (n=0) |
| headon | 14 | 30 (n=14) | 30 (n=14) | 30 (n=14) |
| none | 0 | — (n=0) | — (n=0) | — (n=0) |

| cause | deaths | multi-step | single-step | no move | lap in prior 4 rounds |
| --- | --- | --- | --- | --- | --- |
| wall | 0 | 0 | 0 | 0 | 0 |
| self | 1 | 0 | 1 | 0 | 0 |

### Examples (up to five each)

wall, had a safe move: hunter/base_autarky_v0_3000_1.replay r9; hunter/base_autarky_v0_3001_1.replay r9; hunter/base_devil_v0_3001_1.replay r35; hunter/base_maze_3000_1.replay r174; hunter/base_weakhold_3000_1.replay r93

self, had a safe move: hunter/base_autarky_v0_3000_0.replay r9; hunter/base_autarky_v0_3001_0.replay r9; hunter/candidate_autarky_v0_3000_0.replay r9; hunter/candidate_autarky_v0_3001_0.replay r9; hunter/candidate_islands_3000_1.replay r113

wall, forced: hunter/base_maze_3000_0.replay r84; hunter/base_maze_3001_0.replay r92; hunter/base_maze_3001_1.replay r112; hunter/base_portals_v0_3000_0.replay r13; hunter/base_portals_v0_3001_0.replay r121

### Part B: lengths and events

queen endings, base: 5 games. Means include dead queens as 0.

| round | games | our mean length | their mean length | ours alive | theirs alive |
| --- | --- | --- | --- | --- | --- |
| 100 | 5 | 2.40 | 2.60 | 5 | 5 |
| 200 | 5 | 2.60 | 2.20 | 5 | 4 |
| 250 | 5 | 2.60 | 2.40 | 5 | 4 |
| 300 | 5 | 3.20 | 3.20 | 5 | 4 |
| 350 | 5 | 9.20 | 11.40 | 5 | 4 |
| 400 | 5 | 20.40 | 19.60 | 5 | 4 |
| 450 | 5 | 29.60 | 23.40 | 4 | 4 |
| 500 | 5 | 34.60 | 27.40 | 4 | 4 |

| period | games | our pearls | their pearls | our splits | their splits | our lap/decisions |
| --- | --- | --- | --- | --- | --- | --- |
| r0–299 | 5 | 24 | 27 | 13 | 14 | 65/1500 (4.3%) |
| r300–500 | 5 | 165 | 123 | 3 | 1 | 33/922 (3.6%) |

queen endings, candidate: 6 games. Means include dead queens as 0.

| round | games | our mean length | their mean length | ours alive | theirs alive |
| --- | --- | --- | --- | --- | --- |
| 100 | 6 | 2.00 | 2.83 | 6 | 6 |
| 200 | 6 | 2.17 | 3.00 | 6 | 6 |
| 250 | 6 | 2.33 | 4.17 | 6 | 6 |
| 300 | 6 | 2.00 | 5.33 | 5 | 6 |
| 350 | 6 | 4.33 | 18.50 | 4 | 6 |
| 400 | 6 | 7.50 | 30.17 | 4 | 6 |
| 450 | 6 | 11.83 | 40.33 | 4 | 6 |
| 500 | 6 | 17.17 | 48.33 | 4 | 6 |

| period | games | our pearls | their pearls | our splits | their splits | our lap/decisions |
| --- | --- | --- | --- | --- | --- | --- |
| r0–299 | 6 | 13 | 46 | 11 | 19 | 1491/1777 (83.9%) |
| r300–500 | 6 | 113 | 276 | 0 | 9 | 21/831 (2.5%) |

all trauma, base: 4 games. Means include dead queens as 0.

| round | games | our mean length | their mean length | ours alive | theirs alive |
| --- | --- | --- | --- | --- | --- |
| 100 | 4 | 2.50 | 2.50 | 4 | 4 |
| 200 | 4 | 2.75 | 2.75 | 4 | 4 |
| 250 | 4 | 2.75 | 3.00 | 4 | 4 |
| 300 | 4 | 3.25 | 4.00 | 4 | 4 |
| 350 | 4 | 7.50 | 14.25 | 4 | 4 |
| 400 | 4 | 15.25 | 24.50 | 4 | 4 |
| 450 | 4 | 22.75 | 29.25 | 3 | 4 |
| 500 | 4 | 27.00 | 34.25 | 3 | 4 |

| period | games | our pearls | their pearls | our splits | their splits | our lap/decisions |
| --- | --- | --- | --- | --- | --- | --- |
| r0–299 | 4 | 21 | 26 | 12 | 13 | 60/1200 (5.0%) |
| r300–500 | 4 | 97 | 123 | 0 | 1 | 33/722 (4.6%) |

all trauma, candidate: 4 games. Means include dead queens as 0.

| round | games | our mean length | their mean length | ours alive | theirs alive |
| --- | --- | --- | --- | --- | --- |
| 100 | 4 | 2.00 | 2.75 | 4 | 4 |
| 200 | 4 | 2.00 | 3.00 | 4 | 4 |
| 250 | 4 | 2.00 | 4.00 | 4 | 4 |
| 300 | 4 | 2.00 | 4.25 | 4 | 4 |
| 350 | 4 | 6.50 | 14.75 | 4 | 4 |
| 400 | 4 | 11.25 | 26.00 | 4 | 4 |
| 450 | 4 | 17.75 | 33.50 | 4 | 4 |
| 500 | 4 | 25.75 | 40.50 | 4 | 4 |

| period | games | our pearls | their pearls | our splits | their splits | our lap/decisions |
| --- | --- | --- | --- | --- | --- | --- |
| r0–299 | 4 | 0 | 27 | 4 | 13 | 1150/1200 (95.8%) |
| r300–500 | 4 | 95 | 159 | 0 | 7 | 21/800 (2.6%) |

paired union of queen endings, base: 7 games. Means include dead queens as 0.

| round | games | our mean length | their mean length | ours alive | theirs alive |
| --- | --- | --- | --- | --- | --- |
| 100 | 7 | 2.00 | 2.57 | 6 | 7 |
| 200 | 7 | 1.86 | 1.57 | 5 | 4 |
| 250 | 7 | 1.86 | 1.71 | 5 | 4 |
| 300 | 7 | 2.29 | 2.29 | 5 | 4 |
| 350 | 7 | 6.57 | 8.14 | 5 | 4 |
| 400 | 7 | 14.57 | 14.00 | 5 | 4 |
| 450 | 7 | 21.14 | 16.71 | 4 | 4 |
| 500 | 7 | 24.71 | 19.57 | 4 | 4 |

| period | games | our pearls | their pearls | our splits | their splits | our lap/decisions |
| --- | --- | --- | --- | --- | --- | --- |
| r0–299 | 7 | 51 | 32 | 28 | 17 | 91/1749 (5.2%) |
| r300–500 | 7 | 165 | 123 | 3 | 1 | 33/922 (3.6%) |

paired union of queen endings, candidate: 7 games. Means include dead queens as 0.

| round | games | our mean length | their mean length | ours alive | theirs alive |
| --- | --- | --- | --- | --- | --- |
| 100 | 7 | 1.71 | 2.43 | 6 | 6 |
| 200 | 7 | 1.86 | 2.57 | 6 | 6 |
| 250 | 7 | 2.00 | 3.57 | 6 | 6 |
| 300 | 6 | 2.00 | 5.33 | 5 | 6 |
| 350 | 6 | 4.33 | 18.50 | 4 | 6 |
| 400 | 6 | 7.50 | 30.17 | 4 | 6 |
| 450 | 6 | 11.83 | 40.33 | 4 | 6 |
| 500 | 6 | 17.17 | 48.33 | 4 | 6 |

| period | games | our pearls | their pearls | our splits | their splits | our lap/decisions |
| --- | --- | --- | --- | --- | --- | --- |
| r0–299 | 7 | 13 | 48 | 12 | 21 | 1495/1818 (82.2%) |
| r300–500 | 7 | 113 | 276 | 0 | 9 | 21/831 (2.5%) |

### Timing interpretation

queen endings (5 off/6 on games): on is already shorter at r100. early: our pearls 24→13, splits 13→11. late: our pearls 165→113, splits 3→0. Final surviving queens 4→4. At r100, alive 5/5 off and 6/6 on. The early deficit accompanies less eating, with fewer splits; all queens are alive at r100, so death does not explain that first deficit. Later, on has lost 2/6 queens by r350 versus 0/5 off, and also eats less after r300; both reduce its late mean.

all trauma (4 off/4 on games): on is already shorter at r100. early: our pearls 21→0, splits 12→4. late: our pearls 97→95, splits 0→0. Final surviving queens 3→4. At r100, alive 4/4 off and 4/4 on. The early deficit accompanies less eating, with fewer splits; all queens are alive at r100, so death does not explain that first deficit. On loses no queen here; its r300-on pearls are nearly equal, and neither arm splits then, so late paid movement/damage or timing remains unallocated.

paired union of queen endings (7 off/7 on games): on is already shorter at r100. early: our pearls 51→13, splits 28→12. late: our pearls 165→113, splits 3→0. Final surviving queens 4→4. At r100, alive 6/7 off and 6/7 on.

Queen-ending groups select different games in each arm; the paired union additionally compares the same map/seed/side games, including the other arm even if its ending differs.
Could not measure: exact internal bot view/reasons, future survival after a safe alternative, dynamic multi-step escape, causal attribution of length loss to food/splits alone (paid steps and incoming damage also change length). Room is static. Fatal step count is requested steps, including unexecuted ones; free/paid allocation at the fatal step is not inferred. No new games were run.
