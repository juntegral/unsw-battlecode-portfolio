Against the normal bot, she mostly loops on her own side, a short distance from spawn: the median is 6 tiles (middle 50%: 6–11).
2.0% are within 4 tiles; 68.7% at 5–8, 5.8% at 9–12, and 23.5% at 13+.
15.5% are closer to their queen's spawn than ours; centre distances below give the map scale, not proof she is at the centre.
Loop sites are less crowded in these pooled decisions: an enemy head is in view in 8.3% versus 27.0% of switch-off length-2–3 decisions; mean heads within 6: 0.26 versus 0.6; weakhold is the exception for the within-6 mean (0.33 versus 0.31).
Normal set: 16 games per arm, 1283 switch-on lap steps versus 1635 switch-off short decisions; this is descriptive, not a matched-site or causal comparison.

Methods: only our queen, decisions at rounds <300. Distances are wrapped Manhattan distances, exactly as in the existing check; map centre is ((width−1)/2, (height−1)/2). Quartiles use linear interpolation. Distance and pressure are measured immediately before each action; “lap” classifies that action. “On the loop” classifies a decision immediately after a qualifying lap, using the existing length/home gates. Enemy pressure uses current true replay head positions, not remembered ghosts. The 7×7 head-presence box is visible; the Manhattan-6 count includes heads she cannot see. Geometry, spawn distances, and lap reconstruction also use replay truth.

Hunter set skipped: no final DONE line at start (last line: `2026-10-07 00:16:33 KST  map 12/17 australia: switch off 2/4, switch on 1/4 (108 s)`). No partial hunter counts are used.

Normal set — 1. Lap-step distance

| Map | Switch | Games | Lap decisions | Q25 / median / Q75 | ≤4 / 5–8 / 9–12 / 13+ |
|---|---|---:|---:|---|---|
| australia | off | 4 | 25 | 9 / 13 / 27 | 0.0% / 24.0% / 20.0% / 56.0% |
| australia | on | 4 | 486 | 6 / 6 / 7 | 0.0% / 81.7% / 2.7% / 15.6% |
| default | off | 4 | 3 | 14.5 / 15 / 16 | 0.0% / 0.0% / 0.0% / 100.0% |
| default | on | 4 | 130 | 11 / 16 / 22 | 0.0% / 4.6% / 26.9% / 68.5% |
| queen_of_spades | off | 4 | 5 | 20 / 21 / 22 | 0.0% / 0.0% / 0.0% / 100.0% |
| queen_of_spades | on | 4 | 341 | 6 / 7 / 20 | 0.0% / 53.4% / 7.6% / 39.0% |
| weakhold | off | 4 | 38 | 9 / 10 / 11 | 0.0% / 15.8% / 63.2% / 21.1% |
| weakhold | on | 4 | 326 | 5 / 6 / 7 | 8.0% / 90.8% / 0.3% / 0.9% |
| TOTAL | off | 16 | 71 | 9 / 11 / 21 | 0.0% / 16.9% / 40.8% / 42.3% |
| TOTAL | on | 16 | 1283 | 6 / 6 / 11 | 2.0% / 68.7% / 5.8% / 23.5% |

2. All length-2–3 decisions

| Map | Switch | Games | Short decisions | Q25 / median / Q75 | ≤4 / 5–8 / 9–12 / 13+ |
|---|---|---:|---:|---|---|
| australia | off | 4 | 400 | 8 / 16 / 27 | 5.5% / 21.0% / 16.0% / 57.5% |
| australia | on | 4 | 743 | 6 / 6 / 10 | 7.0% / 62.7% / 9.7% / 20.6% |
| default | off | 4 | 352 | 13 / 16 / 19.25 | 5.1% / 6.2% / 10.5% / 78.1% |
| default | on | 4 | 381 | 10 / 15 / 20 | 6.0% / 11.0% / 19.7% / 63.3% |
| queen_of_spades | off | 4 | 496 | 10 / 15 / 21 | 6.7% / 13.1% / 21.2% / 59.1% |
| queen_of_spades | on | 4 | 604 | 6 / 11 / 20 | 5.5% / 39.4% / 11.9% / 43.2% |
| weakhold | off | 4 | 387 | 8 / 11 / 17 | 6.2% / 23.5% / 32.3% / 38.0% |
| weakhold | on | 4 | 592 | 5 / 6 / 7 | 20.6% / 62.8% / 7.3% / 9.3% |
| TOTAL | off | 16 | 1635 | 9 / 14 / 20 | 5.9% / 16.0% / 20.2% / 57.8% |
| TOTAL | on | 16 | 2320 | 6 / 7 / 15 | 9.9% / 48.2% / 11.3% / 30.6% |

3. Map scale and lap steps on their side (strictly closer to enemy spawn)

| Map | Size | Our side: spawn → centre / enemy | Off games / laps / their-side share | On games / laps / their-side share |
|---|---|---|---|---|
| australia | 64×64 | 0: (24, 19) → 20 / 40; 1: (39, 44) → 20 / 40 | 4 / 25 / 32.0% | 4 / 486 / 0.0% |
| default | 32×32 | 0: (0, 0) → 31 / 2; 1: (31, 31) → 31 / 2 | 4 / 3 / 0.0% | 4 / 130 / 23.8% |
| queen_of_spades | 25×35 | 0: (5, 11) → 13 / 23; 1: (19, 23) → 13 / 23 | 4 / 5 / 80.0% | 4 / 341 / 40.5% |
| weakhold | 40×15 | 0: (2, 3) → 21.5 / 12; 1: (37, 11) → 21.5 / 12 | 4 / 38 / 42.1% | 4 / 326 / 9.2% |
| TOTAL | — | — | 16 / 71 / 39.4% | 16 / 1283 / 15.5% |

4. Enemy pressure at decisions (true current heads)

| Map | Switch / sample | Games | Decisions | ≥1 head in 7×7 | Mean heads within Manhattan 6 |
|---|---|---:|---:|---:|---:|
| australia | off / laps | 4 | 25 | 20.0% | 0.4 |
| australia | on / laps | 4 | 486 | 3.5% | 0.09 |
| australia | off / all length 2–3 | 4 | 400 | 19.8% | 0.52 |
| default | off / laps | 4 | 3 | 66.7% | 1.33 |
| default | on / laps | 4 | 130 | 26.9% | 0.82 |
| default | off / all length 2–3 | 4 | 352 | 58.8% | 1.21 |
| queen_of_spades | off / laps | 4 | 5 | 40.0% | 0.8 |
| queen_of_spades | on / laps | 4 | 341 | 8.5% | 0.24 |
| queen_of_spades | off / all length 2–3 | 4 | 496 | 22.4% | 0.44 |
| weakhold | off / laps | 4 | 38 | 5.3% | 0.16 |
| weakhold | on / laps | 4 | 326 | 8.0% | 0.33 |
| weakhold | off / all length 2–3 | 4 | 387 | 11.6% | 0.31 |
| TOTAL | off / laps | 16 | 71 | 15.5% | 0.34 |
| TOTAL | on / laps | 16 | 1283 | 8.3% | 0.26 |
| TOTAL | off / all length 2–3 | 16 | 1635 | 27.0% | 0.6 |

5. Weakhold seed 13801, our side 0 (one game per arm; pre-action snapshots every 20 rounds)

| Switch | Round | Distance from spawn | Length | Lap action? | On the loop? | Enemy heads within 6 |
|---|---:|---:|---:|---|---|---:|
| on | 0 | 0 | 4 | no | no | 1 |
| on | 20 | 5 | 2 | yes | yes | 0 |
| on | 40 | 5 | 2 | yes | yes | 0 |
| on | 60 | 5 | 2 | yes | yes | 0 |
| on | 80 | 5 | 2 | yes | yes | 1 |
| on | 100 | 5 | 2 | yes | yes | 0 |
| on | 120 | 5 | 2 | yes | yes | 2 |
| on | 140 | 7 | 2 | yes | yes | 1 |
| on | 160 | 6 | 2 | no | no | 4 |
| on | 180 | 3 | 2 | no | no | 5 |
| on | 200 | 3 | 2 | yes | no | 0 |
| on | 220 | 3 | 2 | no | no | 2 |
| on | 240 | 3 | 2 | yes | no | 0 |
| on | 260 | 5 | 2 | no | no | 1 |
| on | 280 | 7 | 2 | no | yes | 1 |
| off | 0 | 0 | 4 | no | no | 1 |
| off | 20 | 12 | 2 | no | no | 0 |
| off | 40 | 10 | 2 | no | yes | 0 |
| off | 60 | 9 | 2 | no | no | 0 |
| off | 80 | 15 | 2 | no | no | 2 |

base: death round 97; missing pre-death decision marks []; candidate: death round 369; missing pre-death decision marks []. No snapshot after death or at round 300 is counted.

Check against existing check.json: switch-on lap total = 1283 (matches lap_steps_before_r300); on-the-loop decisions = 1255 (matches 1255). They are different event definitions: a lap step completes a lap; an on-the-loop decision follows one and requires a qualifying short queen and square entirely >4 from home. Counts can also differ at death, the final action, or r300. The check has 1302 all-round lap steps and 47 excluded following-lap decisions: 1302 − 47 = 1255; 19 lap steps occur at/after r300, giving 1283 before r300. Off lap/short/on-loop totals also match the reference. No missing measurement in the normal set; paths/maze routes and a categorical centre-region boundary were not requested or inferred.
