# Escort counts

## Step 2 checks

The copied drafts were read against the brief line by line. No changes were needed. Byte identity with both source drafts: True. All arms below were scanned from replay files; draft JSONL caches were not used.

`python3 dn_tab.py m3b7qk_vh m5es_vh` and `python3 esc_tab.py m3b7qk_vh m5es_vh`: PASS. All 25 shared printed rows have identical values on 8 common games. Both commands were run under `nice -n 10`.

| Arm | Games | Mate moved | Enemy moved | Chases; turns each; lasting 4+ | Sum of new length-by-target cells |
|---|---|---|---|---|---|
| m3b7qk_vh | 8 | 19 | 2 | 24; 3.5; 9 | 19 |
| m5es_vh | 8 | 61 | 18 | 31; 2.3; 7 | 61 |

Length-by-target sum equals the mate-moved count: PASS for both check arms. All original record fields also match the trusted ESC records for 16 arm-game records.

Distances: tiles are torus Manhattan distance; steps are breadth-first over open edges and portals (`Geo.adj`), ignoring bodies, capped at 8 (99 beyond that or with our queen dead). `L0`, enemy head distance, and start tiles are measured at the start of the mover’s turn. `moved` counts event-kind-9 head tile changes by the actor up to the collision. Length lost uses length at death. Chase definitions and existing table rows are unchanged.

The jobs emitted the permitted warning `nice: setpriority: Operation not permitted`.

## Input counts

| Arm | Scanned completed games |
|---|---|
| m3b7qk_vh | 128 |
| m4qd_vh | 58 |
| m5dn_vh | 8 |

New-arm wait: All 8 result files present; nice: setpriority: Operation not permitted; m5dn_vh 8.

Expected new-arm games missing from the three-arm intersection: none.

## Table A

| measure | m3b7qk_vh | m4qd_vh |
|---|---|---|
| games; won | 58; 37 | 58; 32 |
| queen turns | 4260 | 4294 |
| own heads within 3 tiles r0-50 / r51-100 / r101-300 | 0.59 / 0.91 / 0.40 | 0.60 / 0.93 / 0.39 |
| own heads within 5 tiles r0-50 / r51-100 / r101-300 | 1.65 / 2.74 / 1.38 | 1.65 / 2.84 / 1.32 |
| own heads of 4 or less within 5 tiles, same bands | 1.62 / 2.48 / 1.02 | 1.62 / 2.52 / 0.94 |
| queen turns to r300 with 1+ / 2+ mates of 4 or less within 5 tiles (%) | 65 / 36 | 64 / 36 |
| stays of a short mate within 5 tiles: number; turns each; lasting 10+ turns | 1511; 4.1; 127 | 1533; 4.1; 133 |
| enemy head within 3 steps per 100 queen turns: r0-50 / r51-100 / r101-300 / all (turns) | 5.5 / 7.2 / 4.9 / 5.1 (219) | 5.0 / 6.7 / 6.9 / 5.3 (226) |
| close chases; turns each; lasting 4+ | 80; 2.7; 17 | 70; 3.2; 20 |
| chases that start with no mate within 5 tiles | 25 of 80 (31%) | 28 of 70 (40%) |
| chases in which a mate and a pursuer meet head-on (mate moved) | 12 (10) of 80 | 15 (12) of 70 |
| chases that end in her being rammed | 20 | 19 |
| head-ons mate v enemy within 5 tiles of her: mate moved / enemy moved | 42 / 17 | 61 / 18 |
| those head-ons: length we lost / they lost; mate moved at length 2 / 3 / 4 / 5+ | 169 / 178; 20 / 14 / 5 / 3 | 253 / 226; 14 / 32 / 10 / 5 |
| mate moved, rammer L0 2: target was a pursuer / target only in the radius | 5 / 15 | 3 / 11 |
| mate moved, rammer L0 3: target was a pursuer / target only in the radius | 1 / 15 | 7 / 22 |
| mate moved, rammer L0 4: target was a pursuer / target only in the radius | 0 / 5 | 2 / 9 |
| mate moved, rammer L0 5+: target was a pursuer / target only in the radius | 0 / 1 | 1 / 6 |
| enemy moved (count) | 17 | 18 |
| paid hunt sprints by a 5+: count; segments paid | 0; 0 | 6; 11 |
| length lost by us / by them in those pairs | 169 / 178 | 253 / 226 |
| pursuers rammed by a mate | 6 | 13 |
| mates dead on their own move (kelp, body, no action) within 5 tiles of her, to r300: all; 4 long or less | 104; 101 | 125; 120 |
| queen alive at the end of r100 / r150 / game | 10 / 7 / 2 | 9 / 7 / 2 |
| rounds the queen lived, mean (alive at the end = last round) | 73 | 73 |
| queen deaths: rammed / boxed in / ran into a head | 39 / 14 / 3 | 41 / 12 / 3 |
| boxed-in deaths with a mate body on a neighbour tile of hers | 11 of 14 | 10 of 12 |
| queen turns with a mate body on a neighbour tile, per 100; with 0 or 1 free tile, per 100 | 8.9; 32.1 | 9.1; 32.0 |
| own dragons at r100 / r300 | 39.3 / 42.3 | 38.3 / 41.4 |
| own total length at r100 / r300 | 193.3 / 219.9 | 189.3 / 215.2 |
| enemy dragons at r100 / r300 | 35.0 / 35.0 | 35.9 / 36.1 |
| pearls eaten a game: all; r0-50 / r51-100 / r101-300 | 2742.8; 161.0 / 281.3 / 1173.9 | 2701.2; 160.2 / 277.8 / 1163.0 |
| queen length at the end (dead = 0) | 0.1 | 0.1 |

Games behind Table A: 58 common games.

### Small-map games behind Table A

| Game | Cells | Baseline winner | Radius-5 winner | Baseline own dragons r100 | Radius-5 own dragons r100 | Baseline queen death round | Radius-5 queen death round |
|---|---|---|---|---|---|---|---|
| ladder_portals_1-seed1-side0 | 512 | m3b7qk_vh | m4qd_vh | 18 | 18 | 31 | 31 |
| ladder_portals_1-seed1-side1 | 512 | m3b7qk_vh | m3hunt | 15 | 21 | 78 | 82 |
| sqheld_blobs_small_90027-seed1-side0 | 300 | m3b7qk_vh | m4qd_vh | 18 | 18 | 6 | 6 |
| sqheld_blobs_small_90027-seed1-side1 | 300 | m3hunt | m3hunt | 0 | 0 | 6 | 7 |
| sqheld_blobs_small_90028-seed1-side0 | 399 | m3b7qk_vh | m4qd_vh | 20 | 46 | 6 | 6 |
| sqheld_blobs_small_90028-seed1-side1 | 399 | m3b7qk_vh | m4qd_vh | 50 | 36 | 6 | 6 |
| sqheld_islands_small_90042-seed1-side0 | 285 | draw | draw | 0 | 0 | 12 | 12 |
| sqheld_islands_small_90042-seed1-side1 | 285 | draw | draw | 0 | 0 | 13 | 13 |
| sqheld_open_small_90012-seed1-side0 | 414 | m3b7qk_vh | m3hunt | 35 | 18 | 106 | 96 |
| sqheld_open_small_90012-seed1-side1 | 414 | m3b7qk_vh | m4qd_vh | 51 | 24 | 24 | 24 |
| sqheld_open_small_90015-seed1-side0 | 320 | m3b7qk_vh | m4qd_vh | 12 | 12 | 6 | 6 |
| sqheld_open_small_90015-seed1-side1 | 320 | m3hunt | m3hunt | 0 | 0 | 6 | 6 |
| sqheld_open_small_90018-seed1-side0 | 224 | m3hunt | m3hunt | 0 | 0 | 10 | 10 |
| sqheld_open_small_90018-seed1-side1 | 224 | draw | draw | 0 | 0 | 6 | 6 |
| sqheld_portalrooms_small_90021-seed1-side0 | 300 | draw | draw | 0 | 0 | 3 | 3 |
| sqheld_portalrooms_small_90021-seed1-side1 | 300 | draw | draw | 0 | 0 | 4 | 4 |
| sqheld_portalrooms_small_90022-seed1-side0 | 170 | draw | draw | 0 | 0 | 5 | 5 |
| sqheld_portalrooms_small_90022-seed1-side1 | 170 | m3b7qk_vh | m4qd_vh | 5 | 2 | 70 | 48 |
| sqheld_portals_small_90029-seed1-side0 | 264 | m3b7qk_vh | m4qd_vh | 15 | 15 | 7 | 7 |
| sqheld_portals_small_90029-seed1-side1 | 264 | m3b7qk_vh | m4qd_vh | 20 | 20 | 27 | 27 |

## Table B — cells<=700

| measure | m3b7qk_vh | m4qd_vh |
|---|---|---|
| games; won | 20; 11 | 20; 9 |
| queen turns | 445 | 417 |
| own heads within 3 tiles r0-50 / r51-100 / r101-300 | 0.43 / 1.56 / 4.67 | 0.47 / 1.81 / 0.00 |
| own heads within 5 tiles r0-50 / r51-100 / r101-300 | 1.09 / 4.78 / 10.50 | 1.17 / 4.86 / 0.00 |
| own heads of 4 or less within 5 tiles, same bands | 1.07 / 4.75 / 10.50 | 1.14 / 4.85 / 0.00 |
| queen turns to r300 with 1+ / 2+ mates of 4 or less within 5 tiles (%) | 61 / 38 | 60 / 37 |
| stays of a short mate within 5 tiles: number; turns each; lasting 10+ turns | 216; 4.1; 12 | 175; 4.4; 17 |
| enemy head within 3 steps per 100 queen turns: r0-50 / r51-100 / r101-300 / all (turns) | 5.3 / 4.1 / 0.0 / 4.9 (22) | 3.5 / 0.0 / 0.0 / 2.9 (12) |
| close chases; turns each; lasting 4+ | 10; 2.2; 2 | 7; 1.7; 0 |
| chases that start with no mate within 5 tiles | 1 of 10 (10%) | 1 of 7 (14%) |
| chases in which a mate and a pursuer meet head-on (mate moved) | 3 (3) of 10 | 2 (1) of 7 |
| chases that end in her being rammed | 2 | 3 |
| head-ons mate v enemy within 5 tiles of her: mate moved / enemy moved | 14 / 3 | 15 / 3 |
| those head-ons: length we lost / they lost; mate moved at length 2 / 3 / 4 / 5+ | 41 / 44; 9 / 5 / 0 / 0 | 51 / 46; 4 / 8 / 3 / 0 |
| mate moved, rammer L0 2: target was a pursuer / target only in the radius | 3 / 6 | 1 / 3 |
| mate moved, rammer L0 3: target was a pursuer / target only in the radius | 0 / 5 | 2 / 7 |
| mate moved, rammer L0 4: target was a pursuer / target only in the radius | 0 / 0 | 1 / 1 |
| mate moved, rammer L0 5+: target was a pursuer / target only in the radius | 0 / 0 | 0 / 0 |
| enemy moved (count) | 3 | 3 |
| paid hunt sprints by a 5+: count; segments paid | 0; 0 | 0; 0 |
| length lost by us / by them in those pairs | 41 / 44 | 51 / 46 |
| pursuers rammed by a mate | 3 | 4 |
| mates dead on their own move (kelp, body, no action) within 5 tiles of her, to r300: all; 4 long or less | 6; 6 | 6; 6 |
| queen alive at the end of r100 / r150 / game | 1 / 0 / 0 | 0 / 0 / 0 |
| rounds the queen lived, mean (alive at the end = last round) | 22 | 20 |
| queen deaths: rammed / boxed in / ran into a head | 15 / 3 / 2 | 17 / 2 / 1 |
| boxed-in deaths with a mate body on a neighbour tile of hers | 1 of 3 | 1 of 2 |
| queen turns with a mate body on a neighbour tile, per 100; with 0 or 1 free tile, per 100 | 9.7; 5.8 | 8.9; 7.2 |
| own dragons at r100 / r300 | 12.9 / 15.2 | 11.5 / 13.3 |
| own total length at r100 / r300 | 31.5 / 39.0 | 28.4 / 33.4 |
| enemy dragons at r100 / r300 | 6.0 / 5.3 | 6.5 / 7.0 |
| pearls eaten a game: all; r0-50 / r51-100 / r101-300 | 230.9; 36.1 / 46.0 / 104.2 | 269.4; 34.6 / 51.4 / 136.7 |
| queen length at the end (dead = 0) | 0.0 | 0.0 |

Games behind Table B: 20 common games.

## Table C — cells>700

| measure | m3b7qk_vh | m4qd_vh |
|---|---|---|
| games; won | 38; 26 | 38; 23 |
| queen turns | 3815 | 3877 |
| own heads within 3 tiles r0-50 / r51-100 / r101-300 | 0.62 / 0.81 / 0.38 | 0.62 / 0.83 / 0.39 |
| own heads within 5 tiles r0-50 / r51-100 / r101-300 | 1.76 / 2.44 / 1.33 | 1.75 / 2.61 / 1.32 |
| own heads of 4 or less within 5 tiles, same bands | 1.73 / 2.14 / 0.97 | 1.72 / 2.26 / 0.94 |
| queen turns to r300 with 1+ / 2+ mates of 4 or less within 5 tiles (%) | 65 / 35 | 65 / 36 |
| stays of a short mate within 5 tiles: number; turns each; lasting 10+ turns | 1295; 4.1; 115 | 1358; 4.0; 116 |
| enemy head within 3 steps per 100 queen turns: r0-50 / r51-100 / r101-300 / all (turns) | 5.5 / 7.7 / 4.9 / 5.2 (197) | 5.3 / 7.4 / 6.9 / 5.5 (214) |
| close chases; turns each; lasting 4+ | 70; 2.8; 15 | 63; 3.4; 20 |
| chases that start with no mate within 5 tiles | 24 of 70 (34%) | 27 of 63 (43%) |
| chases in which a mate and a pursuer meet head-on (mate moved) | 9 (7) of 70 | 13 (11) of 63 |
| chases that end in her being rammed | 18 | 16 |
| head-ons mate v enemy within 5 tiles of her: mate moved / enemy moved | 28 / 14 | 46 / 15 |
| those head-ons: length we lost / they lost; mate moved at length 2 / 3 / 4 / 5+ | 128 / 134; 11 / 9 / 5 / 3 | 202 / 180; 10 / 24 / 7 / 5 |
| mate moved, rammer L0 2: target was a pursuer / target only in the radius | 2 / 9 | 2 / 8 |
| mate moved, rammer L0 3: target was a pursuer / target only in the radius | 1 / 10 | 5 / 15 |
| mate moved, rammer L0 4: target was a pursuer / target only in the radius | 0 / 5 | 1 / 8 |
| mate moved, rammer L0 5+: target was a pursuer / target only in the radius | 0 / 1 | 1 / 6 |
| enemy moved (count) | 14 | 15 |
| paid hunt sprints by a 5+: count; segments paid | 0; 0 | 6; 11 |
| length lost by us / by them in those pairs | 128 / 134 | 202 / 180 |
| pursuers rammed by a mate | 3 | 9 |
| mates dead on their own move (kelp, body, no action) within 5 tiles of her, to r300: all; 4 long or less | 98; 95 | 119; 114 |
| queen alive at the end of r100 / r150 / game | 9 / 7 / 2 | 9 / 7 / 2 |
| rounds the queen lived, mean (alive at the end = last round) | 99 | 101 |
| queen deaths: rammed / boxed in / ran into a head | 24 / 11 / 1 | 24 / 10 / 2 |
| boxed-in deaths with a mate body on a neighbour tile of hers | 10 of 11 | 9 of 10 |
| queen turns with a mate body on a neighbour tile, per 100; with 0 or 1 free tile, per 100 | 8.8; 35.2 | 9.1; 34.7 |
| own dragons at r100 / r300 | 53.1 / 56.6 | 52.4 / 56.2 |
| own total length at r100 / r300 | 278.5 / 315.1 | 274.1 / 310.9 |
| enemy dragons at r100 / r300 | 50.3 / 50.6 | 51.4 / 51.4 |
| pearls eaten a game: all; r0-50 / r51-100 / r101-300 | 4064.8; 226.8 / 405.1 / 1736.9 | 3981.2; 226.2 / 397.0 / 1703.2 |
| queen length at the end (dead = 0) | 0.2 | 0.2 |

Games behind Table C: 38 common games.

## Table D

| measure | m3b7qk_vh | m4qd_vh | m5dn_vh |
|---|---|---|---|
| games; won | 8; 7 | 8; 5 | 8; 7 |
| queen turns | 659 | 770 | 670 |
| own heads within 3 tiles r0-50 / r51-100 / r101-300 | 0.60 / 1.31 / 0.54 | 0.61 / 1.33 / 0.39 | 0.58 / 0.85 / 0.40 |
| own heads within 5 tiles r0-50 / r51-100 / r101-300 | 1.78 / 4.09 / 1.88 | 1.87 / 4.12 / 1.54 | 1.77 / 3.04 / 1.38 |
| own heads of 4 or less within 5 tiles, same bands | 1.78 / 3.84 / 1.55 | 1.86 / 3.74 / 1.18 | 1.77 / 2.69 / 0.96 |
| queen turns to r300 with 1+ / 2+ mates of 4 or less within 5 tiles (%) | 76 / 47 | 76 / 47 | 73 / 42 |
| stays of a short mate within 5 tiles: number; turns each; lasting 10+ turns | 370; 4.0; 26 | 398; 3.8; 30 | 315; 3.6; 17 |
| enemy head within 3 steps per 100 queen turns: r0-50 / r51-100 / r101-300 / all (turns) | 9.3 / 5.6 / 23.5 / 11.7 (77) | 6.2 / 4.3 / 14.7 / 7.7 (59) | 11.3 / 7.3 / 23.4 / 14.0 (94) |
| close chases; turns each; lasting 4+ | 20; 3.9; 8 | 15; 3.9; 7 | 27; 3.5; 7 |
| chases that start with no mate within 5 tiles | 2 of 20 (10%) | 4 of 15 (27%) | 5 of 27 (19%) |
| chases in which a mate and a pursuer meet head-on (mate moved) | 6 (6) of 20 | 6 (6) of 15 | 7 (6) of 27 |
| chases that end in her being rammed | 6 | 3 | 7 |
| head-ons mate v enemy within 5 tiles of her: mate moved / enemy moved | 18 / 3 | 26 / 6 | 16 / 3 |
| those head-ons: length we lost / they lost; mate moved at length 2 / 3 / 4 / 5+ | 58 / 60; 11 / 5 / 1 / 1 | 103 / 80; 9 / 13 / 2 / 2 | 49 / 58; 10 / 6 / 0 / 0 |
| mate moved, rammer L0 2: target was a pursuer / target only in the radius | 3 / 8 | 2 / 7 | 1 / 9 |
| mate moved, rammer L0 3: target was a pursuer / target only in the radius | 1 / 5 | 2 / 10 | 3 / 3 |
| mate moved, rammer L0 4: target was a pursuer / target only in the radius | 0 / 1 | 2 / 1 | 0 / 0 |
| mate moved, rammer L0 5+: target was a pursuer / target only in the radius | 0 / 0 | 0 / 2 | 0 / 0 |
| enemy moved (count) | 3 | 6 | 3 |
| paid hunt sprints by a 5+: count; segments paid | 0; 0 | 1; 2 | 0; 0 |
| length lost by us / by them in those pairs | 58 / 60 | 103 / 80 | 49 / 58 |
| pursuers rammed by a mate | 4 | 6 | 4 |
| mates dead on their own move (kelp, body, no action) within 5 tiles of her, to r300: all; 4 long or less | 21; 20 | 42; 40 | 23; 22 |
| queen alive at the end of r100 / r150 / game | 3 / 1 / 0 | 2 / 1 / 0 | 2 / 1 / 0 |
| rounds the queen lived, mean (alive at the end = last round) | 81 | 95 | 83 |
| queen deaths: rammed / boxed in / ran into a head | 7 / 1 / 0 | 7 / 1 / 0 | 8 / 0 / 0 |
| boxed-in deaths with a mate body on a neighbour tile of hers | 1 of 1 | 1 of 1 | 0 of 0 |
| queen turns with a mate body on a neighbour tile, per 100; with 0 or 1 free tile, per 100 | 10.9; 7.6 | 10.9; 10.6 | 9.0; 9.7 |
| own dragons at r100 / r300 | 49.4 / 57.9 | 42.4 / 49.2 | 49.9 / 57.0 |
| own total length at r100 / r300 | 165.9 / 171.8 | 137.5 / 148.4 | 163.4 / 172.6 |
| enemy dragons at r100 / r300 | 38.6 / 37.1 | 44.8 / 44.6 | 40.0 / 39.2 |
| pearls eaten a game: all; r0-50 / r51-100 / r101-300 | 2610.2; 160.2 / 282.1 / 1129.2 | 2542.8; 154.0 / 250.2 / 1145.1 | 2628.9; 154.2 / 288.9 / 1239.9 |
| queen length at the end (dead = 0) | 0.0 | 0.0 | 0.0 |

Games behind Table D: 8 common games.

## Table E — sqheld_open_small_90012

| measure | m3b7qk_vh | m4qd_vh | m5dn_vh |
|---|---|---|---|
| games; won | 2; 2 | 2; 1 | 2; 2 |
| queen turns | 132 | 122 | 73 |
| own heads within 3 tiles r0-50 / r51-100 / r101-300 | 1.09 / 2.58 / 4.67 | 1.09 / 2.35 / 0.00 | 0.89 / 0.00 / 0.00 |
| own heads within 5 tiles r0-50 / r51-100 / r101-300 | 2.80 / 7.18 / 10.50 | 3.01 / 6.17 / 0.00 | 2.42 / 0.00 / 0.00 |
| own heads of 4 or less within 5 tiles, same bands | 2.80 / 7.18 / 10.50 | 3.01 / 6.17 / 0.00 | 2.42 / 0.00 / 0.00 |
| queen turns to r300 with 1+ / 2+ mates of 4 or less within 5 tiles (%) | 91 / 79 | 90 / 78 | 84 / 62 |
| stays of a short mate within 5 tiles: number; turns each; lasting 10+ turns | 137; 4.6; 10 | 104; 4.9; 15 | 39; 4.5; 2 |
| enemy head within 3 steps per 100 queen turns: r0-50 / r51-100 / r101-300 / all (turns) | 10.5 / 8.0 / 0.0 / 9.1 (12) | 3.9 / 0.0 / 0.0 / 2.5 (3) | 13.7 / 0.0 / 0.0 / 13.7 (10) |
| close chases; turns each; lasting 4+ | 4; 3.0; 2 | 2; 1.5; 0 | 3; 3.3; 1 |
| chases that start with no mate within 5 tiles | 0 of 4 (0%) | 0 of 2 (0%) | 0 of 3 (0%) |
| chases in which a mate and a pursuer meet head-on (mate moved) | 2 (2) of 4 | 1 (1) of 2 | 2 (2) of 3 |
| chases that end in her being rammed | 1 | 1 | 2 |
| head-ons mate v enemy within 5 tiles of her: mate moved / enemy moved | 11 / 1 | 11 / 1 | 5 / 0 |
| those head-ons: length we lost / they lost; mate moved at length 2 / 3 / 4 / 5+ | 28 / 31; 8 / 3 / 0 / 0 | 34 / 29; 3 / 6 / 2 / 0 | 13 / 12; 2 / 3 / 0 / 0 |
| mate moved, rammer L0 2: target was a pursuer / target only in the radius | 2 / 6 | 0 / 3 | 0 / 2 |
| mate moved, rammer L0 3: target was a pursuer / target only in the radius | 0 / 3 | 1 / 5 | 2 / 1 |
| mate moved, rammer L0 4: target was a pursuer / target only in the radius | 0 / 0 | 1 / 1 | 0 / 0 |
| mate moved, rammer L0 5+: target was a pursuer / target only in the radius | 0 / 0 | 0 / 0 | 0 / 0 |
| enemy moved (count) | 1 | 1 | 0 |
| paid hunt sprints by a 5+: count; segments paid | 0; 0 | 0; 0 | 0; 0 |
| length lost by us / by them in those pairs | 28 / 31 | 34 / 29 | 13 / 12 |
| pursuers rammed by a mate | 2 | 2 | 2 |
| mates dead on their own move (kelp, body, no action) within 5 tiles of her, to r300: all; 4 long or less | 2; 2 | 3; 3 | 0; 0 |
| queen alive at the end of r100 / r150 / game | 1 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| rounds the queen lived, mean (alive at the end = last round) | 65 | 60 | 36 |
| queen deaths: rammed / boxed in / ran into a head | 1 / 1 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| boxed-in deaths with a mate body on a neighbour tile of hers | 1 of 1 | 0 of 0 | 0 of 0 |
| queen turns with a mate body on a neighbour tile, per 100; with 0 or 1 free tile, per 100 | 30.3; 6.1 | 24.6; 9.0 | 17.8; 1.4 |
| own dragons at r100 / r300 | 43.0 / 60.5 | 21.0 / 27.5 | 26.0 / 58.0 |
| own total length at r100 / r300 | 99.5 / 162.0 | 50.5 / 71.5 | 64.0 / 162.5 |
| enemy dragons at r100 / r300 | 15.0 / 0.0 | 29.5 / 29.5 | 19.5 / 0.0 |
| pearls eaten a game: all; r0-50 / r51-100 / r101-300 | 505.5; 80.0 / 193.5 / 232.0 | 766.0; 78.0 / 163.0 / 525.0 | 823.0; 78.5 / 179.5 / 565.0 |
| queen length at the end (dead = 0) | 0.0 | 0.0 | 0.0 |

Games behind Table E: 2 common games.

## New-arm comparison per game

| Game | Arm | Winner | Rounds (result.txt) | Own dragons r100 | Own dragons r300 | Queen death round; kind; reason |
|---|---|---|---|---|---|---|
| ladder_islands_1-seed1-side0 | m3b7qk_vh | m3b7qk_vh | 500 | 60 | 59 | 237; rammed; reason 3 |
| ladder_islands_1-seed1-side0 | m4qd_vh | m4qd_vh | 500 | 60 | 57 | 352; rammed; reason 3 |
| ladder_islands_1-seed1-side0 | m5dn_vh | m5dn_vh | 500 | 60 | 58 | 282; rammed; reason 3 |
| ladder_islands_1-seed1-side1 | m3b7qk_vh | m3b7qk_vh | 500 | 50 | 56 | 62; rammed; reason 3 |
| ladder_islands_1-seed1-side1 | m4qd_vh | m4qd_vh | 500 | 50 | 56 | 57; rammed; reason 3 |
| ladder_islands_1-seed1-side1 | m5dn_vh | m5dn_vh | 500 | 50 | 56 | 57; rammed; reason 3 |
| sqheld_open_small_90012-seed1-side0 | m3b7qk_vh | m3b7qk_vh | 191 | 35 | 62 | 106; boxed; reason 2 |
| sqheld_open_small_90012-seed1-side0 | m4qd_vh | m3hunt | 200 | 18 | 0 | 96; rammed; reason 3 |
| sqheld_open_small_90012-seed1-side0 | m5dn_vh | m5dn_vh | 175 | 28 | 61 | 47; rammed; reason 3 |
| sqheld_open_small_90012-seed1-side1 | m3b7qk_vh | m3b7qk_vh | 111 | 51 | 59 | 24; rammed; reason 3 |
| sqheld_open_small_90012-seed1-side1 | m4qd_vh | m4qd_vh | 255 | 24 | 55 | 24; rammed; reason 3 |
| sqheld_open_small_90012-seed1-side1 | m5dn_vh | m5dn_vh | 255 | 24 | 55 | 24; rammed; reason 3 |
| sqheld_portals_medium_90007-seed1-side0 | m3b7qk_vh | m3b7qk_vh | 500 | 21 | 58 | 37; rammed; reason 3 |
| sqheld_portals_medium_90007-seed1-side0 | m4qd_vh | m4qd_vh | 500 | 36 | 54 | 58; rammed; reason 3 |
| sqheld_portals_medium_90007-seed1-side0 | m5dn_vh | m5dn_vh | 500 | 57 | 55 | 67; rammed; reason 3 |
| sqheld_portals_medium_90007-seed1-side1 | m3b7qk_vh | m3hunt | 500 | 59 | 56 | 41; rammed; reason 3 |
| sqheld_portals_medium_90007-seed1-side1 | m4qd_vh | m3hunt | 500 | 60 | 58 | 41; rammed; reason 3 |
| sqheld_portals_medium_90007-seed1-side1 | m5dn_vh | m3hunt | 500 | 60 | 58 | 41; rammed; reason 3 |
| sqheld_portals_medium_90020-seed1-side0 | m3b7qk_vh | m3b7qk_vh | 500 | 59 | 58 | 34; rammed; reason 3 |
| sqheld_portals_medium_90020-seed1-side0 | m4qd_vh | m4qd_vh | 500 | 30 | 54 | 30; rammed; reason 3 |
| sqheld_portals_medium_90020-seed1-side0 | m5dn_vh | m5dn_vh | 500 | 60 | 58 | 34; rammed; reason 3 |
| sqheld_portals_medium_90020-seed1-side1 | m3b7qk_vh | m3b7qk_vh | 500 | 60 | 55 | 110; rammed; reason 3 |
| sqheld_portals_medium_90020-seed1-side1 | m4qd_vh | m3hunt | 500 | 61 | 60 | 104; boxed; reason 2 |
| sqheld_portals_medium_90020-seed1-side1 | m5dn_vh | m5dn_vh | 500 | 60 | 55 | 110; rammed; reason 3 |

Round checkpoints follow the trusted scanner: if the game ended before a checkpoint, its final snapshot is used.

## List 1 — every mate-moved head-on within 5 tiles in m5dn_vh

Tiles in this list are at the start of the mover’s turn. Enemy length is at death; the enemy is stationary on a mate move. Every listed mate is not our queen; enemy queens are included if present. The mark uses the requested comparison: enemy length < mate `L0`.

| Game | Round | Mate id | Mate L0 | Mate start tile | Enemy id | Enemy length | Enemy start tile | qsteps | qtiles | Our queen start tile | Baseline mark |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ladder_islands_1-seed1-side0 | 119 | 167 | 2 | (51,8) | 139 | 2 | (51,9) | 6 | 4 | (51,5) |  |
| ladder_islands_1-seed1-side0 | 161 | 64 | 2 | (0,24) | 81 | 2 | (0,23) | 4 | 4 | (55,26) |  |
| ladder_islands_1-seed1-side0 | 241 | 307 | 3 | (0,0) | 317 | 3 | (55,39) | 6 | 6 | (0,4) |  |
| sqheld_open_small_90012-seed1-side0 | 33 | 3 | 3 | (15,7) | 8 | 3 | (14,7) | 4 | 4 | (16,9) |  |
| sqheld_open_small_90012-seed1-side0 | 40 | 19 | 3 | (12,9) | 23 | 2 | (12,11) | 3 | 3 | (14,10) | **baseline disallows: enemy shorter** |
| sqheld_open_small_90012-seed1-side0 | 43 | 42 | 2 | (12,8) | 6 | 3 | (12,9) | 4 | 4 | (14,7) |  |
| sqheld_open_small_90012-seed1-side0 | 45 | 31 | 2 | (15,5) | 34 | 2 | (14,5) | 4 | 4 | (12,7) |  |
| sqheld_open_small_90012-seed1-side1 | 23 | 3 | 3 | (6,6) | 2 | 2 | (7,7) | 2 | 2 | (7,5) | **baseline disallows: enemy shorter** |
| sqheld_portals_medium_90007-seed1-side0 | 34 | 35 | 3 | (30,3) | 36 | 2 | (32,3) | 3 | 3 | (31,1) | **baseline disallows: enemy shorter** |
| sqheld_portals_medium_90007-seed1-side0 | 44 | 101 | 2 | (32,23) | 51 | 3 | (31,23) | 6 | 6 | (35,1) |  |
| sqheld_portals_medium_90007-seed1-side0 | 45 | 84 | 2 | (33,3) | 74 | 4 | (32,3) | 6 | 6 | (36,1) |  |
| sqheld_portals_medium_90007-seed1-side0 | 49 | 70 | 2 | (39,1) | 17 | 2 | (38,1) | 4 | 4 | (1,0) |  |
| sqheld_portals_medium_90007-seed1-side0 | 51 | 31 | 2 | (4,22) | 33 | 4 | (5,22) | 4 | 4 | (2,23) |  |
| sqheld_portals_medium_90007-seed1-side0 | 57 | 131 | 2 | (0,23) | 18 | 5 | (1,23) | 3 | 3 | (1,20) |  |
| sqheld_portals_medium_90020-seed1-side0 | 34 | 77 | 2 | (24,16) | 70 | 4 | (24,15) | 5 | 5 | (22,18) |  |
| sqheld_portals_medium_90020-seed1-side1 | 104 | 260 | 3 | (29,8) | 307 | 5 | (30,7) | 6 | 6 | (27,10) |  |

Listed head-ons: 16.

## List 2 — every queen chase in m5dn_vh

Pursuer ids and lengths are listed at every queen turn of the chase. An ending is queen rammed if her rammed death follows the final chased queen turn. Otherwise, pursuer rammed by a mate requires a mate-moved pair involving a pursuer present on the final chased turn, after that turn and before her next turn, within the trusted association window (through the following round). Remaining ended chases are labelled pursuer left.

| Game | First round | Last round | Turns | Pursuer ids and lengths | Mates within 5 tiles at first turn | How it ended |
|---|---|---|---|---|---|---|
| ladder_islands_1-seed1-side0 | 137 | 141 | 5 | r137: #81 L2; r138: #81 L2; r139: #81 L2; r140: #81 L2; r141: #81 L2 | none | pursuer left |
| ladder_islands_1-seed1-side0 | 147 | 148 | 2 | r147: #81 L2; r148: #81 L2 | #9 L3 (7,22) (5 tiles) | pursuer left |
| ladder_islands_1-seed1-side0 | 153 | 164 | 12 | r153: #38 L2; r154: #38 L2; r155: #38 L2; r156: #38 L2, #156 L2; r157: #156 L2; r158: #156 L2; r159: #156 L2; r160: #81 L2; r161: #81 L2, #156 L2; r162: #156 L2; r163: #156 L2; r164: #156 L2 | #64 L2 (1,27) (5 tiles) | pursuer left |
| ladder_islands_1-seed1-side0 | 185 | 186 | 2 | r185: #156 L2; r186: #156 L2 | #118 L2 (48,35) (4 tiles) | pursuer left |
| ladder_islands_1-seed1-side0 | 189 | 196 | 8 | r189: #156 L2; r190: #156 L2; r191: #156 L2; r192: #156 L2; r193: #156 L2; r194: #156 L2; r195: #156 L2; r196: #156 L2 | #118 L2 (46,37) (5 tiles), #272 L2 (40,34) (4 tiles) | pursuer left |
| ladder_islands_1-seed1-side0 | 261 | 262 | 2 | r261: #15 L2; r262: #131 L2 | #375 L18 (10,5) (4 tiles) | pursuer left |
| ladder_islands_1-seed1-side0 | 265 | 265 | 1 | r265: #304 L2 | #375 L2 (7,6) (4 tiles), #386 L2 (3,3) (5 tiles) | pursuer left |
| ladder_islands_1-seed1-side0 | 280 | 282 | 3 | r280: #371 L3; r281: #371 L3; r282: #371 L4 | none | queen rammed |
| ladder_islands_1-seed1-side1 | 45 | 50 | 6 | r45: #42 L2; r46: #42 L2; r47: #42 L2; r48: #42 L2; r49: #42 L2; r50: #42 L2 | none | pursuer left |
| ladder_islands_1-seed1-side1 | 57 | 57 | 1 | r57: #63 L3 | none | queen rammed |
| sqheld_open_small_90012-seed1-side0 | 24 | 24 | 1 | r24: #8 L3 | #3 L3 (16,7) (2 tiles), #9 L2 (15,2) (4 tiles), #17 L2 (17,4) (2 tiles) | pursuer left |
| sqheld_open_small_90012-seed1-side0 | 41 | 47 | 7 | r41: #29 L4; r42: #29 L4; r43: #29 L4; r44: #29 L4, #34 L2; r45: #29 L4, #34 L2; r46: #7 L2, #29 L4; r47: #29 L5 | #9 L2 (18,11) (5 tiles), #15 L2 (16,8) (4 tiles) | queen rammed |
| sqheld_open_small_90012-seed1-side1 | 23 | 24 | 2 | r23: #2 L2, #8 L3; r24: #6 L2, #8 L3 | #3 L3 (6,6) (2 tiles), #9 L4 (7,2) (3 tiles), #11 L2 (4,3) (5 tiles) | queen rammed |
| sqheld_portals_medium_90007-seed1-side0 | 19 | 19 | 1 | r19: #8 L3 | #4 L3 (36,17) (4 tiles), #11 L3 (38,18) (5 tiles) | pursuer left |
| sqheld_portals_medium_90007-seed1-side0 | 24 | 24 | 1 | r24: #8 L3 | #4 L3 (37,20) (5 tiles) | pursuer left |
| sqheld_portals_medium_90007-seed1-side0 | 26 | 26 | 1 | r26: #8 L3 | #31 L2 (36,22) (4 tiles) | pursuer left |
| sqheld_portals_medium_90007-seed1-side0 | 28 | 34 | 7 | r28: #8 L3; r29: #8 L3; r30: #8 L3; r31: #36 L2; r32: #36 L2; r33: #36 L2; r34: #36 L2 | #31 L2 (38,22) (4 tiles), #32 L2 (35,21) (4 tiles) | pursuer rammed by a mate: r34 mate #35 / pursuer #36 |
| sqheld_portals_medium_90007-seed1-side0 | 36 | 38 | 3 | r36: #51 L3; r37: #51 L4; r38: #51 L4 | none | pursuer left |
| sqheld_portals_medium_90007-seed1-side0 | 41 | 43 | 3 | r41: #74 L3; r42: #74 L3; r43: #74 L4 | #44 L3 (31,22) (3 tiles), #84 L2 (35,1) (4 tiles) | pursuer left |
| sqheld_portals_medium_90007-seed1-side0 | 48 | 48 | 1 | r48: #17 L2 | #70 L2 (39,0) (2 tiles), #100 L3 (38,21) (4 tiles), #119 L2 (35,0) (4 tiles) | pursuer left |
| sqheld_portals_medium_90007-seed1-side0 | 56 | 57 | 2 | r56: #18 L4; r57: #18 L4 | #60 L3 (1,18) (4 tiles), #126 L2 (4,21) (2 tiles), #131 L2 (0,22) (3 tiles) | pursuer rammed by a mate: r57 mate #131 / pursuer #18 |
| sqheld_portals_medium_90007-seed1-side0 | 61 | 62 | 2 | r61: #145 L2; r62: #145 L2 | #4 L2 (39,18) (1 tiles), #11 L2 (2,16) (4 tiles), #115 L2 (39,14) (5 tiles), #139 L2 (1,22) (5 tiles), #140 L2 (38,20) (4 tiles), #144 L3 (37,16) (5 tiles), #147 L2 (39,22) (5 tiles), #151 L2 (39,16) (3 tiles) | pursuer left |
| sqheld_portals_medium_90007-seed1-side1 | 39 | 41 | 3 | r39: #47 L3; r40: #47 L3; r41: #47 L4 | #21 L4 (17,17) (4 tiles), #71 L3 (14,20) (4 tiles), #78 L2 (12,17) (3 tiles) | queen rammed |
| sqheld_portals_medium_90020-seed1-side0 | 24 | 26 | 3 | r24: #25 L3, #37 L2; r25: #37 L2; r26: #37 L2 | #6 L2 (23,17) (2 tiles), #28 L4 (20,14) (4 tiles), #30 L3 (19,16) (3 tiles), #38 L2 (22,12) (4 tiles) | pursuer left |
| sqheld_portals_medium_90020-seed1-side0 | 34 | 34 | 1 | r34: #79 L5 | #62 L2 (22,12) (5 tiles), #65 L2 (22,14) (3 tiles), #77 L2 (24,16) (3 tiles), #82 L3 (20,14) (5 tiles), #85 L3 (18,18) (5 tiles), #95 L2 (20,16) (3 tiles) | queen rammed |
| sqheld_portals_medium_90020-seed1-side1 | 96 | 96 | 1 | r96: #331 L2 | #286 L5 (26,13) (5 tiles), #292 L5 (27,7) (2 tiles), #319 L4 (25,12) (5 tiles) | pursuer left |
| sqheld_portals_medium_90020-seed1-side1 | 98 | 110 | 13 | r98: #288 L3; r99: #288 L3; r100: #288 L4; r101: #288 L4; r102: #288 L4; r103: #288 L4; r104: #288 L4; r105: #305 L3; r106: #305 L3; r107: #305 L3; r108: #305 L3; r109: #305 L3; r110: #305 L3, #354 L3 | #292 L5 (25,5) (2 tiles), #319 L4 (24,11) (5 tiles) | queen rammed |

Listed chases: 27.

DONE 2026-10-08 19:34:07 KST
