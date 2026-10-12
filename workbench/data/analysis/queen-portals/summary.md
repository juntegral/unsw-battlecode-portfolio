# Queen portal counts

Input: 2,343 ladder/top1 games and 45 live-bot games; 2388 unique games. Parsed portal-map games: 1947; queen-games: 3894. No network or game runs.

A queen-game is one team’s queen in one game; both teams are included. G = unique games, Q = queen-games, J = jumps. Ours = 1119 meow; top three = 306 Vibing++, 91 SSS, 264 forgot to mention; other = every remaining team. Each fraction states its sample size; the row’s G applies to each number in that row.

Detection reuses qh31b-analysis/count.py: a dragonUpdate head move longer than one normal step, with open-border wrapping on each axis, between cells touching different edges of the same portal label. No sonar-ping requirement. Updates are individual steps, so the threshold is one step, not a full action’s reach.

Distance = Manhattan cells, wrapping an axis only when its border has an open edge. Walls, bodies and portal shortcuts are ignored for distance. Enemy heads use full replay positions immediately before the landing update. “Not seen” means no enemy head within 15 cells, not actual bot visibility; 9+ means 9–15. Other-side means landing strictly nearer the enemy queen’s initial head than the own queen’s initial head.

Alive at round 100 means alive at the start of round 100; games ending earlier are excluded. Death windows include the jump round and the next 10 or 30 rounds. Repeated jumps may share a death. Queen-game death shares count a queen once if any selected jump meets the window.

| Source | Parsed portal games | Queen-games |
|---|---|---|
| ladder/top1 | G=1911 | Q=3822, G=1911 |
| qh31b-test-old | G=24 | Q=48, G=24 |
| qh31b-dev1-old | G=12 | Q=24, G=12 |

## Maps

Portals = paired labels (two edges each). Free cells were not separately counted: this format stores blocked edges, not blocked tiles.

| Map | Width × height | Cells | Portal pairs (edges) | Size group | Games |
|---|---|---|---|---|---|
| Around UNSW | 64 × 64 | 4096 | 4 (8) | over 2,400 | G=143 |
| Australia | 64 × 64 | 4096 | 4 (8) | over 2,400 | G=145 |
| Autarky | 54 × 18 | 972 | 8 (16) | 601–1,200 | G=120 |
| Default | 32 × 32 | 1024 | 12 (24) | 601–1,200 | G=144 |
| Islands | 56 × 40 | 2240 | 12 (24) | 1,201–2,400 | G=157 |
| Maze | 48 × 24 | 1152 | 16 (32) | 601–1,200 | G=132 |
| Portals | 32 × 16 | 512 | 20 (40) | up to 600 | G=147 |
| Prisoners Dilemma | 32 × 16 | 512 | 4 (8) | up to 600 | G=117 |
| Queen Of Spades | 25 × 35 | 875 | 2 (4) | 601–1,200 | G=118 |
| Schooltime | 60 × 40 | 2400 | 12 (24) | 1,201–2,400 | G=144 |
| Slithery Fight | 63 × 27 | 1701 | 2 (4) | 1,201–2,400 | G=144 |
| Stripes | 24 × 12 | 288 | 8 (16) | up to 600 | G=146 |
| Trauma | 48 × 24 | 1152 | 6 (12) | 601–1,200 | G=150 |
| Trophy | 25 × 25 | 625 | 1 (2) | 601–1,200 | G=140 |

- up to 600: Portals, Prisoners Dilemma, Stripes (G=410).
- 601–1,200: Autarky, Default, Maze, Queen Of Spades, Trauma, Trophy (G=804).
- 1,201–2,400: Islands, Schooltime, Slithery Fight (G=445).
- over 2,400: Around UNSW, Australia (G=288).

## 1. Queen jumps

| Size | Tag | Sample | At least one jump | Jumps per queen-game | First jump median round |
|---|---|---|---|---|---|
| up to 600 | ours | Q=113, G=113 | 100/113 (88.5%) | 2.363 (J=267, Q=113, G=113) | 4 (Q=100, G=100) |
| up to 600 | top three | Q=313, G=268 | 166/313 (53.0%) | 2.441 (J=764, Q=313, G=268) | 9 (Q=166, G=154) |
| up to 600 | other | Q=394, G=362 | 189/394 (48.0%) | 1.784 (J=703, Q=394, G=362) | 11 (Q=189, G=179) |
| 601–1,200 | ours | Q=254, G=254 | 10/254 (3.9%) | 0.067 (J=17, Q=254, G=254) | 100.5 (Q=10, G=10) |
| 601–1,200 | top three | Q=599, G=512 | 94/599 (15.7%) | 0.604 (J=362, Q=599, G=512) | 72.5 (Q=94, G=90) |
| 601–1,200 | other | Q=755, G=709 | 85/755 (11.3%) | 0.338 (J=255, Q=755, G=709) | 67 (Q=85, G=84) |
| 1,201–2,400 | ours | Q=152, G=152 | 1/152 (0.7%) | 0.007 (J=1, Q=152, G=152) | 66 (Q=1, G=1) |
| 1,201–2,400 | top three | Q=326, G=274 | 9/326 (2.8%) | 0.040 (J=13, Q=326, G=274) | 404 (Q=9, G=9) |
| 1,201–2,400 | other | Q=412, G=389 | 14/412 (3.4%) | 0.056 (J=23, Q=412, G=389) | 111.5 (Q=14, G=14) |
| over 2,400 | ours | Q=92, G=92 | 0/92 (0.0%) | 0.000 (J=0, Q=92, G=92) | not measured (Q=0, G=0) |
| over 2,400 | top three | Q=217, G=186 | 2/217 (0.9%) | 0.009 (J=2, Q=217, G=186) | 354.5 (Q=2, G=2) |
| over 2,400 | other | Q=267, G=254 | 14/267 (5.2%) | 0.064 (J=17, Q=267, G=254) | 61.5 (Q=14, G=14) |

## 2. Game endings

| Size | Tag | Queen | Sample | Elimination | Queen rule | Longest dragon | Total length | Draw | Unknown |
|---|---|---|---|---|---|---|---|---|---|
| up to 600 | ours | jumped | Q=100, G=100 | 51/100 (51.0%) | 18/100 (18.0%) | 31/100 (31.0%) | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| up to 600 | ours | never jumped | Q=13, G=13 | 13/13 (100.0%) | 0/13 (0.0%) | 0/13 (0.0%) | 0/13 (0.0%) | 0/13 (0.0%) | 0/13 (0.0%) |
| up to 600 | top three | jumped | Q=166, G=154 | 119/166 (71.7%) | 30/166 (18.1%) | 17/166 (10.2%) | 0/166 (0.0%) | 0/166 (0.0%) | 0/166 (0.0%) |
| up to 600 | top three | never jumped | Q=147, G=136 | 79/147 (53.7%) | 58/147 (39.5%) | 10/147 (6.8%) | 0/147 (0.0%) | 0/147 (0.0%) | 0/147 (0.0%) |
| up to 600 | other | jumped | Q=189, G=179 | 132/189 (69.8%) | 25/189 (13.2%) | 32/189 (16.9%) | 0/189 (0.0%) | 0/189 (0.0%) | 0/189 (0.0%) |
| up to 600 | other | never jumped | Q=205, G=198 | 108/205 (52.7%) | 69/205 (33.7%) | 28/205 (13.7%) | 0/205 (0.0%) | 0/205 (0.0%) | 0/205 (0.0%) |
| 601–1,200 | ours | jumped | Q=10, G=10 | 0/10 (0.0%) | 4/10 (40.0%) | 6/10 (60.0%) | 0/10 (0.0%) | 0/10 (0.0%) | 0/10 (0.0%) |
| 601–1,200 | ours | never jumped | Q=244, G=244 | 129/244 (52.9%) | 66/244 (27.0%) | 46/244 (18.9%) | 3/244 (1.2%) | 0/244 (0.0%) | 0/244 (0.0%) |
| 601–1,200 | top three | jumped | Q=94, G=90 | 46/94 (48.9%) | 17/94 (18.1%) | 30/94 (31.9%) | 1/94 (1.1%) | 0/94 (0.0%) | 0/94 (0.0%) |
| 601–1,200 | top three | never jumped | Q=505, G=443 | 275/505 (54.5%) | 173/505 (34.3%) | 56/505 (11.1%) | 1/505 (0.2%) | 0/505 (0.0%) | 0/505 (0.0%) |
| 601–1,200 | other | jumped | Q=85, G=84 | 43/85 (50.6%) | 13/85 (15.3%) | 28/85 (32.9%) | 1/85 (1.2%) | 0/85 (0.0%) | 0/85 (0.0%) |
| 601–1,200 | other | never jumped | Q=670, G=634 | 341/670 (50.9%) | 231/670 (34.5%) | 92/670 (13.7%) | 6/670 (0.9%) | 0/670 (0.0%) | 0/670 (0.0%) |
| 1,201–2,400 | ours | jumped | Q=1, G=1 | 0/1 (0.0%) | 0/1 (0.0%) | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| 1,201–2,400 | ours | never jumped | Q=151, G=151 | 20/151 (13.2%) | 33/151 (21.9%) | 97/151 (64.2%) | 1/151 (0.7%) | 0/151 (0.0%) | 0/151 (0.0%) |
| 1,201–2,400 | top three | jumped | Q=9, G=9 | 1/9 (11.1%) | 4/9 (44.4%) | 4/9 (44.4%) | 0/9 (0.0%) | 0/9 (0.0%) | 0/9 (0.0%) |
| 1,201–2,400 | top three | never jumped | Q=317, G=266 | 8/317 (2.5%) | 78/317 (24.6%) | 230/317 (72.6%) | 1/317 (0.3%) | 0/317 (0.0%) | 0/317 (0.0%) |
| 1,201–2,400 | other | jumped | Q=14, G=14 | 3/14 (21.4%) | 4/14 (28.6%) | 7/14 (50.0%) | 0/14 (0.0%) | 0/14 (0.0%) | 0/14 (0.0%) |
| 1,201–2,400 | other | never jumped | Q=398, G=376 | 26/398 (6.5%) | 101/398 (25.4%) | 267/398 (67.1%) | 4/398 (1.0%) | 0/398 (0.0%) | 0/398 (0.0%) |
| over 2,400 | ours | jumped | Q=0, G=0 | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) |
| over 2,400 | ours | never jumped | Q=92, G=92 | 2/92 (2.2%) | 32/92 (34.8%) | 57/92 (62.0%) | 1/92 (1.1%) | 0/92 (0.0%) | 0/92 (0.0%) |
| over 2,400 | top three | jumped | Q=2, G=2 | 0/2 (0.0%) | 1/2 (50.0%) | 1/2 (50.0%) | 0/2 (0.0%) | 0/2 (0.0%) | 0/2 (0.0%) |
| over 2,400 | top three | never jumped | Q=215, G=184 | 1/215 (0.5%) | 69/215 (32.1%) | 144/215 (67.0%) | 1/215 (0.5%) | 0/215 (0.0%) | 0/215 (0.0%) |
| over 2,400 | other | jumped | Q=14, G=14 | 2/14 (14.3%) | 3/14 (21.4%) | 9/14 (64.3%) | 0/14 (0.0%) | 0/14 (0.0%) | 0/14 (0.0%) |
| over 2,400 | other | never jumped | Q=253, G=243 | 1/253 (0.4%) | 89/253 (35.2%) | 161/253 (63.6%) | 2/253 (0.8%) | 0/253 (0.0%) | 0/253 (0.0%) |

## 3 and 4. Win rate and fate

### Win rate: any jump

| Size | Tag | Subset | Wins with any jump | Wins without any jump |
|---|---|---|---|---|
| up to 600 | ours | all | 42/100 (42.0%) (Q=100, G=100) | 0/13 (0.0%) (Q=13, G=13) |
| up to 600 | ours | alive r100 | 15/30 (50.0%) (Q=30, G=30) | 0/2 (0.0%) (Q=2, G=2) |
| up to 600 | top three | all | 110/166 (66.3%) (Q=166, G=154) | 85/147 (57.8%) (Q=147, G=136) |
| up to 600 | top three | alive r100 | 45/70 (64.3%) (Q=70, G=66) | 59/97 (60.8%) (Q=97, G=89) |
| up to 600 | other | all | 85/189 (45.0%) (Q=189, G=179) | 88/205 (42.9%) (Q=205, G=198) |
| up to 600 | other | alive r100 | 47/87 (54.0%) (Q=87, G=85) | 68/145 (46.9%) (Q=145, G=140) |
| 601–1,200 | ours | all | 4/10 (40.0%) (Q=10, G=10) | 126/244 (51.6%) (Q=244, G=244) |
| 601–1,200 | ours | alive r100 | 4/7 (57.1%) (Q=7, G=7) | 87/170 (51.2%) (Q=170, G=170) |
| 601–1,200 | top three | all | 63/94 (67.0%) (Q=94, G=90) | 299/505 (59.2%) (Q=505, G=443) |
| 601–1,200 | top three | alive r100 | 37/55 (67.3%) (Q=55, G=53) | 250/385 (64.9%) (Q=385, G=352) |
| 601–1,200 | other | all | 38/85 (44.7%) (Q=85, G=84) | 274/670 (40.9%) (Q=670, G=634) |
| 601–1,200 | other | alive r100 | 23/53 (43.4%) (Q=53, G=52) | 230/517 (44.5%) (Q=517, G=497) |
| 1,201–2,400 | ours | all | 0/1 (0.0%) (Q=1, G=1) | 31/151 (20.5%) (Q=151, G=151) |
| 1,201–2,400 | ours | alive r100 | 0/1 (0.0%) (Q=1, G=1) | 23/110 (20.9%) (Q=110, G=110) |
| 1,201–2,400 | top three | all | 7/9 (77.8%) (Q=9, G=9) | 202/317 (63.7%) (Q=317, G=266) |
| 1,201–2,400 | top three | alive r100 | 7/9 (77.8%) (Q=9, G=9) | 188/290 (64.8%) (Q=290, G=245) |
| 1,201–2,400 | other | all | 6/14 (42.9%) (Q=14, G=14) | 199/398 (50.0%) (Q=398, G=376) |
| 1,201–2,400 | other | alive r100 | 5/11 (45.5%) (Q=11, G=11) | 189/366 (51.6%) (Q=366, G=350) |
| over 2,400 | ours | all | 0/0 (not measured) (Q=0, G=0) | 16/92 (17.4%) (Q=92, G=92) |
| over 2,400 | ours | alive r100 | 0/0 (not measured) (Q=0, G=0) | 11/60 (18.3%) (Q=60, G=60) |
| over 2,400 | top three | all | 2/2 (100.0%) (Q=2, G=2) | 128/215 (59.5%) (Q=215, G=184) |
| over 2,400 | top three | alive r100 | 2/2 (100.0%) (Q=2, G=2) | 112/168 (66.7%) (Q=168, G=151) |
| over 2,400 | other | all | 9/14 (64.3%) (Q=14, G=14) | 133/253 (52.6%) (Q=253, G=243) |
| over 2,400 | other | alive r100 | 8/9 (88.9%) (Q=9, G=9) | 121/219 (55.3%) (Q=219, G=211) |

### Fate: any jump

| Size | Tag | any jump | Sample | Alive at end | Death within 10 (Q) | Death within 30 (Q) |
|---|---|---|---|---|---|---|
| up to 600 | ours | with | Q=100, G=100 | 9/100 (9.0%) | 63/100 (63.0%) | 77/100 (77.0%) |
| up to 600 | ours | without | Q=13, G=13 | 0/13 (0.0%) | not applicable | not applicable |
| up to 600 | top three | with | Q=166, G=154 | 51/166 (30.7%) | 53/166 (31.9%) | 78/166 (47.0%) |
| up to 600 | top three | without | Q=147, G=136 | 69/147 (46.9%) | not applicable | not applicable |
| up to 600 | other | with | Q=189, G=179 | 36/189 (19.0%) | 86/189 (45.5%) | 112/189 (59.3%) |
| up to 600 | other | without | Q=205, G=198 | 75/205 (36.6%) | not applicable | not applicable |
| 601–1,200 | ours | with | Q=10, G=10 | 0/10 (0.0%) | 7/10 (70.0%) | 8/10 (80.0%) |
| 601–1,200 | ours | without | Q=244, G=244 | 76/244 (31.1%) | not applicable | not applicable |
| 601–1,200 | top three | with | Q=94, G=90 | 15/94 (16.0%) | 42/94 (44.7%) | 66/94 (70.2%) |
| 601–1,200 | top three | without | Q=505, G=443 | 234/505 (46.3%) | not applicable | not applicable |
| 601–1,200 | other | with | Q=85, G=84 | 10/85 (11.8%) | 33/85 (38.8%) | 54/85 (63.5%) |
| 601–1,200 | other | without | Q=670, G=634 | 263/670 (39.3%) | not applicable | not applicable |
| 1,201–2,400 | ours | with | Q=1, G=1 | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| 1,201–2,400 | ours | without | Q=151, G=151 | 46/151 (30.5%) | not applicable | not applicable |
| 1,201–2,400 | top three | with | Q=9, G=9 | 5/9 (55.6%) | 1/9 (11.1%) | 1/9 (11.1%) |
| 1,201–2,400 | top three | without | Q=317, G=266 | 161/317 (50.8%) | not applicable | not applicable |
| 1,201–2,400 | other | with | Q=14, G=14 | 3/14 (21.4%) | 5/14 (35.7%) | 8/14 (57.1%) |
| 1,201–2,400 | other | without | Q=398, G=376 | 211/398 (53.0%) | not applicable | not applicable |
| over 2,400 | ours | with | Q=0, G=0 | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) |
| over 2,400 | ours | without | Q=92, G=92 | 0/92 (0.0%) | not applicable | not applicable |
| over 2,400 | top three | with | Q=2, G=2 | 1/2 (50.0%) | 0/2 (0.0%) | 0/2 (0.0%) |
| over 2,400 | top three | without | Q=215, G=184 | 48/215 (22.3%) | not applicable | not applicable |
| over 2,400 | other | with | Q=14, G=14 | 1/14 (7.1%) | 4/14 (28.6%) | 8/14 (57.1%) |
| over 2,400 | other | without | Q=253, G=243 | 49/253 (19.4%) | not applicable | not applicable |

The next two tables count jumps. A later death may follow multiple jumps. Causes are exclusive. Other includes enemy body, an active queen’s head-on, allied head-on, suicide/no action, and unresolved collisions.

| Size | Tag | Window rounds | All jumps | Followed by death | Rammed by enemy | Wall | Own body | Team body | Other | Game ended before full window, without death |
|---|---|---|---|---|---|---|---|---|---|---|
| up to 600 | ours | 10 | J=267, G=100 | 70/267 (26.2%) (death G=63) | 16/70 (22.9%) | 22/70 (31.4%) | 9/70 (12.9%) | 20/70 (28.6%) | 3/70 (4.3%) | 0/267 (0.0%) (G=0) |
| up to 600 | ours | 30 | J=267, G=100 | 113/267 (42.3%) (death G=77) | 31/113 (27.4%) | 32/113 (28.3%) | 18/113 (15.9%) | 20/113 (17.7%) | 12/113 (10.6%) | 2/267 (0.7%) (G=1) |
| up to 600 | top three | 10 | J=764, G=154 | 68/764 (8.9%) (death G=52) | 18/68 (26.5%) | 0/68 (0.0%) | 10/68 (14.7%) | 10/68 (14.7%) | 30/68 (44.1%) | 29/764 (3.8%) (G=20) |
| up to 600 | top three | 30 | J=764, G=154 | 178/764 (23.3%) (death G=77) | 95/178 (53.4%) | 0/178 (0.0%) | 13/178 (7.3%) | 10/178 (5.6%) | 60/178 (33.7%) | 67/764 (8.8%) (G=26) |
| up to 600 | other | 10 | J=703, G=179 | 97/703 (13.8%) (death G=85) | 17/97 (17.5%) | 27/97 (27.8%) | 34/97 (35.1%) | 4/97 (4.1%) | 15/97 (15.5%) | 23/703 (3.3%) (G=12) |
| up to 600 | other | 30 | J=703, G=179 | 223/703 (31.7%) (death G=109) | 79/223 (35.4%) | 48/223 (21.5%) | 50/223 (22.4%) | 5/223 (2.2%) | 41/223 (18.4%) | 49/703 (7.0%) (G=15) |
| 601–1,200 | ours | 10 | J=17, G=10 | 7/17 (41.2%) (death G=7) | 1/7 (14.3%) | 4/7 (57.1%) | 1/7 (14.3%) | 1/7 (14.3%) | 0/7 (0.0%) | 0/17 (0.0%) (G=0) |
| 601–1,200 | ours | 30 | J=17, G=10 | 11/17 (64.7%) (death G=8) | 1/11 (9.1%) | 4/11 (36.4%) | 1/11 (9.1%) | 1/11 (9.1%) | 4/11 (36.4%) | 0/17 (0.0%) (G=0) |
| 601–1,200 | top three | 10 | J=362, G=90 | 47/362 (13.0%) (death G=40) | 24/47 (51.1%) | 0/47 (0.0%) | 2/47 (4.3%) | 0/47 (0.0%) | 21/47 (44.7%) | 3/362 (0.8%) (G=3) |
| 601–1,200 | top three | 30 | J=362, G=90 | 110/362 (30.4%) (death G=63) | 56/110 (50.9%) | 0/110 (0.0%) | 4/110 (3.6%) | 0/110 (0.0%) | 50/110 (45.5%) | 8/362 (2.2%) (G=5) |
| 601–1,200 | other | 10 | J=255, G=84 | 38/255 (14.9%) (death G=33) | 17/38 (44.7%) | 3/38 (7.9%) | 7/38 (18.4%) | 4/38 (10.5%) | 7/38 (18.4%) | 1/255 (0.4%) (G=1) |
| 601–1,200 | other | 30 | J=255, G=84 | 80/255 (31.4%) (death G=54) | 33/80 (41.2%) | 13/80 (16.2%) | 13/80 (16.2%) | 11/80 (13.8%) | 10/80 (12.5%) | 3/255 (1.2%) (G=2) |
| 1,201–2,400 | ours | 10 | J=1, G=1 | 0/1 (0.0%) (death G=0) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/1 (0.0%) (G=0) |
| 1,201–2,400 | ours | 30 | J=1, G=1 | 0/1 (0.0%) (death G=0) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/1 (0.0%) (G=0) |
| 1,201–2,400 | top three | 10 | J=13, G=9 | 1/13 (7.7%) (death G=1) | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 4/13 (30.8%) (G=3) |
| 1,201–2,400 | top three | 30 | J=13, G=9 | 1/13 (7.7%) (death G=1) | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 5/13 (38.5%) (G=4) |
| 1,201–2,400 | other | 10 | J=23, G=14 | 5/23 (21.7%) (death G=5) | 1/5 (20.0%) | 0/5 (0.0%) | 1/5 (20.0%) | 2/5 (40.0%) | 1/5 (20.0%) | 0/23 (0.0%) (G=0) |
| 1,201–2,400 | other | 30 | J=23, G=14 | 12/23 (52.2%) (death G=8) | 5/12 (41.7%) | 0/12 (0.0%) | 2/12 (16.7%) | 4/12 (33.3%) | 1/12 (8.3%) | 0/23 (0.0%) (G=0) |
| over 2,400 | ours | 10 | J=0, G=0 | 0/0 (not measured) (death G=0) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) (G=0) |
| over 2,400 | ours | 30 | J=0, G=0 | 0/0 (not measured) (death G=0) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) (G=0) |
| over 2,400 | top three | 10 | J=2, G=2 | 0/2 (0.0%) (death G=0) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/2 (0.0%) (G=0) |
| over 2,400 | top three | 30 | J=2, G=2 | 0/2 (0.0%) (death G=0) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 1/2 (50.0%) (G=1) |
| over 2,400 | other | 10 | J=17, G=14 | 4/17 (23.5%) (death G=4) | 0/4 (0.0%) | 1/4 (25.0%) | 1/4 (25.0%) | 1/4 (25.0%) | 1/4 (25.0%) | 0/17 (0.0%) (G=0) |
| over 2,400 | other | 30 | J=17, G=14 | 8/17 (47.1%) (death G=8) | 0/8 (0.0%) | 1/8 (12.5%) | 3/8 (37.5%) | 2/8 (25.0%) | 2/8 (25.0%) | 0/17 (0.0%) (G=0) |

| Size | Tag | Landing distance | Share of jumps (J) | Death within 10 (J) | Death within 30 (J) |
|---|---|---|---|---|---|
| up to 600 | ours | 0–3 | 101/267 (37.8%) (G=60) | 43/101 (42.6%) (death G=41) | 58/101 (57.4%) (death G=48) |
| up to 600 | ours | 4–8 | 115/267 (43.1%) (G=78) | 25/115 (21.7%) (death G=25) | 49/115 (42.6%) (death G=41) |
| up to 600 | ours | 9+ | 34/267 (12.7%) (G=29) | 2/34 (5.9%) (death G=2) | 6/34 (17.6%) (death G=6) |
| up to 600 | ours | not seen | 17/267 (6.4%) (G=17) | 0/17 (0.0%) (death G=0) | 0/17 (0.0%) (death G=0) |
| up to 600 | top three | 0–3 | 214/764 (28.0%) (G=99) | 39/214 (18.2%) (death G=36) | 76/214 (35.5%) (death G=56) |
| up to 600 | top three | 4–8 | 382/764 (50.0%) (G=121) | 20/382 (5.2%) (death G=17) | 68/382 (17.8%) (death G=39) |
| up to 600 | top three | 9+ | 147/764 (19.2%) (G=66) | 5/147 (3.4%) (death G=4) | 26/147 (17.7%) (death G=19) |
| up to 600 | top three | not seen | 21/764 (2.7%) (G=15) | 4/21 (19.0%) (death G=2) | 8/21 (38.1%) (death G=6) |
| up to 600 | other | 0–3 | 231/703 (32.9%) (G=130) | 56/231 (24.2%) (death G=54) | 94/231 (40.7%) (death G=76) |
| up to 600 | other | 4–8 | 383/703 (54.5%) (G=129) | 30/383 (7.8%) (death G=27) | 103/383 (26.9%) (death G=60) |
| up to 600 | other | 9+ | 83/703 (11.8%) (G=54) | 9/83 (10.8%) (death G=9) | 24/83 (28.9%) (death G=21) |
| up to 600 | other | not seen | 6/703 (0.9%) (G=6) | 2/6 (33.3%) (death G=2) | 2/6 (33.3%) (death G=2) |
| 601–1,200 | ours | 0–3 | 2/17 (11.8%) (G=1) | 0/2 (0.0%) (death G=0) | 2/2 (100.0%) (death G=1) |
| 601–1,200 | ours | 4–8 | 9/17 (52.9%) (G=6) | 3/9 (33.3%) (death G=3) | 5/9 (55.6%) (death G=4) |
| 601–1,200 | ours | 9+ | 5/17 (29.4%) (G=5) | 4/5 (80.0%) (death G=4) | 4/5 (80.0%) (death G=4) |
| 601–1,200 | ours | not seen | 1/17 (5.9%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| 601–1,200 | top three | 0–3 | 54/362 (14.9%) (G=45) | 26/54 (48.1%) (death G=25) | 38/54 (70.4%) (death G=35) |
| 601–1,200 | top three | 4–8 | 181/362 (50.0%) (G=53) | 14/181 (7.7%) (death G=13) | 47/181 (26.0%) (death G=34) |
| 601–1,200 | top three | 9+ | 109/362 (30.1%) (G=47) | 4/109 (3.7%) (death G=4) | 20/109 (18.3%) (death G=13) |
| 601–1,200 | top three | not seen | 18/362 (5.0%) (G=17) | 3/18 (16.7%) (death G=3) | 5/18 (27.8%) (death G=5) |
| 601–1,200 | other | 0–3 | 64/255 (25.1%) (G=38) | 19/64 (29.7%) (death G=18) | 28/64 (43.8%) (death G=24) |
| 601–1,200 | other | 4–8 | 89/255 (34.9%) (G=48) | 10/89 (11.2%) (death G=10) | 29/89 (32.6%) (death G=23) |
| 601–1,200 | other | 9+ | 73/255 (28.6%) (G=37) | 8/73 (11.0%) (death G=6) | 18/73 (24.7%) (death G=16) |
| 601–1,200 | other | not seen | 29/255 (11.4%) (G=19) | 1/29 (3.4%) (death G=1) | 5/29 (17.2%) (death G=5) |
| 1,201–2,400 | ours | 0–3 | 0/1 (0.0%) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| 1,201–2,400 | ours | 4–8 | 1/1 (100.0%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| 1,201–2,400 | ours | 9+ | 0/1 (0.0%) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| 1,201–2,400 | ours | not seen | 0/1 (0.0%) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| 1,201–2,400 | top three | 0–3 | 4/13 (30.8%) (G=3) | 1/4 (25.0%) (death G=1) | 1/4 (25.0%) (death G=1) |
| 1,201–2,400 | top three | 4–8 | 4/13 (30.8%) (G=4) | 0/4 (0.0%) (death G=0) | 0/4 (0.0%) (death G=0) |
| 1,201–2,400 | top three | 9+ | 1/13 (7.7%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| 1,201–2,400 | top three | not seen | 4/13 (30.8%) (G=4) | 0/4 (0.0%) (death G=0) | 0/4 (0.0%) (death G=0) |
| 1,201–2,400 | other | 0–3 | 10/23 (43.5%) (G=7) | 3/10 (30.0%) (death G=3) | 7/10 (70.0%) (death G=5) |
| 1,201–2,400 | other | 4–8 | 8/23 (34.8%) (G=8) | 2/8 (25.0%) (death G=2) | 4/8 (50.0%) (death G=4) |
| 1,201–2,400 | other | 9+ | 4/23 (17.4%) (G=4) | 0/4 (0.0%) (death G=0) | 1/4 (25.0%) (death G=1) |
| 1,201–2,400 | other | not seen | 1/23 (4.3%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| over 2,400 | ours | 0–3 | 0/0 (not measured) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | ours | 4–8 | 0/0 (not measured) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | ours | 9+ | 0/0 (not measured) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | ours | not seen | 0/0 (not measured) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | top three | 0–3 | 1/2 (50.0%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| over 2,400 | top three | 4–8 | 1/2 (50.0%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| over 2,400 | top three | 9+ | 0/2 (0.0%) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | top three | not seen | 0/2 (0.0%) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | other | 0–3 | 3/17 (17.6%) (G=2) | 0/3 (0.0%) (death G=0) | 0/3 (0.0%) (death G=0) |
| over 2,400 | other | 4–8 | 5/17 (29.4%) (G=5) | 1/5 (20.0%) (death G=1) | 3/5 (60.0%) (death G=3) |
| over 2,400 | other | 9+ | 8/17 (47.1%) (G=7) | 2/8 (25.0%) (death G=2) | 4/8 (50.0%) (death G=4) |
| over 2,400 | other | not seen | 1/17 (5.9%) (G=1) | 1/1 (100.0%) (death G=1) | 1/1 (100.0%) (death G=1) |

## 5. Other-side jumps

| Size | Tag | Other-side share of jumps |
|---|---|---|
| up to 600 | ours | 133/267 (49.8%) (all G=100, other-side G=79) |
| up to 600 | top three | 148/764 (19.4%) (all G=154, other-side G=92) |
| up to 600 | other | 190/703 (27.0%) (all G=179, other-side G=107) |
| 601–1,200 | ours | 5/17 (29.4%) (all G=10, other-side G=3) |
| 601–1,200 | top three | 102/362 (28.2%) (all G=90, other-side G=53) |
| 601–1,200 | other | 96/255 (37.6%) (all G=84, other-side G=50) |
| 1,201–2,400 | ours | 0/1 (0.0%) (all G=1, other-side G=0) |
| 1,201–2,400 | top three | 7/13 (53.8%) (all G=9, other-side G=6) |
| 1,201–2,400 | other | 8/23 (34.8%) (all G=14, other-side G=7) |
| over 2,400 | ours | 0/0 (not measured) (all G=0, other-side G=0) |
| over 2,400 | top three | 2/2 (100.0%) (all G=2, other-side G=2) |
| over 2,400 | other | 12/17 (70.6%) (all G=14, other-side G=12) |

### Win rate: other-side jump

Comparison: queens with at least one other-side jump versus queens without an other-side jump (including queens that jumped only to their own side).

| Size | Tag | Subset | Wins with other-side jump | Wins without other-side jump |
|---|---|---|---|---|
| up to 600 | ours | all | 32/79 (40.5%) (Q=79, G=79) | 10/34 (29.4%) (Q=34, G=34) |
| up to 600 | ours | alive r100 | 13/28 (46.4%) (Q=28, G=28) | 2/4 (50.0%) (Q=4, G=4) |
| up to 600 | top three | all | 58/94 (61.7%) (Q=94, G=92) | 137/219 (62.6%) (Q=219, G=201) |
| up to 600 | top three | alive r100 | 33/53 (62.3%) (Q=53, G=51) | 71/114 (62.3%) (Q=114, G=105) |
| up to 600 | other | all | 56/107 (52.3%) (Q=107, G=107) | 117/287 (40.8%) (Q=287, G=274) |
| up to 600 | other | alive r100 | 31/60 (51.7%) (Q=60, G=60) | 84/172 (48.8%) (Q=172, G=167) |
| 601–1,200 | ours | all | 1/3 (33.3%) (Q=3, G=3) | 129/251 (51.4%) (Q=251, G=251) |
| 601–1,200 | ours | alive r100 | 1/3 (33.3%) (Q=3, G=3) | 90/174 (51.7%) (Q=174, G=174) |
| 601–1,200 | top three | all | 37/55 (67.3%) (Q=55, G=53) | 325/544 (59.7%) (Q=544, G=474) |
| 601–1,200 | top three | alive r100 | 26/41 (63.4%) (Q=41, G=40) | 261/399 (65.4%) (Q=399, G=365) |
| 601–1,200 | other | all | 20/51 (39.2%) (Q=51, G=50) | 292/704 (41.5%) (Q=704, G=666) |
| 601–1,200 | other | alive r100 | 15/34 (44.1%) (Q=34, G=33) | 238/536 (44.4%) (Q=536, G=515) |
| 1,201–2,400 | ours | all | 0/0 (not measured) (Q=0, G=0) | 31/152 (20.4%) (Q=152, G=152) |
| 1,201–2,400 | ours | alive r100 | 0/0 (not measured) (Q=0, G=0) | 23/111 (20.7%) (Q=111, G=111) |
| 1,201–2,400 | top three | all | 5/6 (83.3%) (Q=6, G=6) | 204/320 (63.8%) (Q=320, G=269) |
| 1,201–2,400 | top three | alive r100 | 5/6 (83.3%) (Q=6, G=6) | 190/293 (64.8%) (Q=293, G=248) |
| 1,201–2,400 | other | all | 1/7 (14.3%) (Q=7, G=7) | 204/405 (50.4%) (Q=405, G=382) |
| 1,201–2,400 | other | alive r100 | 1/5 (20.0%) (Q=5, G=5) | 193/372 (51.9%) (Q=372, G=355) |
| over 2,400 | ours | all | 0/0 (not measured) (Q=0, G=0) | 16/92 (17.4%) (Q=92, G=92) |
| over 2,400 | ours | alive r100 | 0/0 (not measured) (Q=0, G=0) | 11/60 (18.3%) (Q=60, G=60) |
| over 2,400 | top three | all | 2/2 (100.0%) (Q=2, G=2) | 128/215 (59.5%) (Q=215, G=184) |
| over 2,400 | top three | alive r100 | 2/2 (100.0%) (Q=2, G=2) | 112/168 (66.7%) (Q=168, G=151) |
| over 2,400 | other | all | 7/12 (58.3%) (Q=12, G=12) | 135/255 (52.9%) (Q=255, G=244) |
| over 2,400 | other | alive r100 | 6/7 (85.7%) (Q=7, G=7) | 123/221 (55.7%) (Q=221, G=212) |

### Fate: other-side jump

| Size | Tag | other-side jump | Sample | Alive at end | Death within 10 (Q) | Death within 30 (Q) |
|---|---|---|---|---|---|---|
| up to 600 | ours | with | Q=79, G=79 | 8/79 (10.1%) | 50/79 (63.3%) | 56/79 (70.9%) |
| up to 600 | ours | without | Q=34, G=34 | 1/34 (2.9%) | not applicable | not applicable |
| up to 600 | top three | with | Q=94, G=92 | 31/94 (33.0%) | 26/94 (27.7%) | 38/94 (40.4%) |
| up to 600 | top three | without | Q=219, G=201 | 89/219 (40.6%) | not applicable | not applicable |
| up to 600 | other | with | Q=107, G=107 | 20/107 (18.7%) | 63/107 (58.9%) | 75/107 (70.1%) |
| up to 600 | other | without | Q=287, G=274 | 91/287 (31.7%) | not applicable | not applicable |
| 601–1,200 | ours | with | Q=3, G=3 | 0/3 (0.0%) | 1/3 (33.3%) | 2/3 (66.7%) |
| 601–1,200 | ours | without | Q=251, G=251 | 76/251 (30.3%) | not applicable | not applicable |
| 601–1,200 | top three | with | Q=55, G=53 | 11/55 (20.0%) | 21/55 (38.2%) | 32/55 (58.2%) |
| 601–1,200 | top three | without | Q=544, G=474 | 238/544 (43.8%) | not applicable | not applicable |
| 601–1,200 | other | with | Q=51, G=50 | 5/51 (9.8%) | 21/51 (41.2%) | 32/51 (62.7%) |
| 601–1,200 | other | without | Q=704, G=666 | 268/704 (38.1%) | not applicable | not applicable |
| 1,201–2,400 | ours | with | Q=0, G=0 | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) |
| 1,201–2,400 | ours | without | Q=152, G=152 | 46/152 (30.3%) | not applicable | not applicable |
| 1,201–2,400 | top three | with | Q=6, G=6 | 3/6 (50.0%) | 1/6 (16.7%) | 1/6 (16.7%) |
| 1,201–2,400 | top three | without | Q=320, G=269 | 163/320 (50.9%) | not applicable | not applicable |
| 1,201–2,400 | other | with | Q=7, G=7 | 2/7 (28.6%) | 5/7 (71.4%) | 5/7 (71.4%) |
| 1,201–2,400 | other | without | Q=405, G=382 | 212/405 (52.3%) | not applicable | not applicable |
| over 2,400 | ours | with | Q=0, G=0 | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) |
| over 2,400 | ours | without | Q=92, G=92 | 0/92 (0.0%) | not applicable | not applicable |
| over 2,400 | top three | with | Q=2, G=2 | 1/2 (50.0%) | 0/2 (0.0%) | 0/2 (0.0%) |
| over 2,400 | top three | without | Q=215, G=184 | 48/215 (22.3%) | not applicable | not applicable |
| over 2,400 | other | with | Q=12, G=12 | 1/12 (8.3%) | 4/12 (33.3%) | 8/12 (66.7%) |
| over 2,400 | other | without | Q=255, G=244 | 49/255 (19.2%) | not applicable | not applicable |

The next two tables count jumps. A later death may follow multiple jumps. Causes are exclusive. Other includes enemy body, an active queen’s head-on, allied head-on, suicide/no action, and unresolved collisions.

| Size | Tag | Window rounds | All jumps | Followed by death | Rammed by enemy | Wall | Own body | Team body | Other | Game ended before full window, without death |
|---|---|---|---|---|---|---|---|---|---|---|
| up to 600 | ours | 10 | J=133, G=79 | 50/133 (37.6%) (death G=50) | 5/50 (10.0%) | 18/50 (36.0%) | 7/50 (14.0%) | 20/50 (40.0%) | 0/50 (0.0%) | 0/133 (0.0%) (G=0) |
| up to 600 | ours | 30 | J=133, G=79 | 64/133 (48.1%) (death G=56) | 8/64 (12.5%) | 21/64 (32.8%) | 12/64 (18.8%) | 20/64 (31.2%) | 3/64 (4.7%) | 1/133 (0.8%) (G=1) |
| up to 600 | top three | 10 | J=148, G=92 | 27/148 (18.2%) (death G=25) | 2/27 (7.4%) | 0/27 (0.0%) | 6/27 (22.2%) | 8/27 (29.6%) | 11/27 (40.7%) | 14/148 (9.5%) (G=12) |
| up to 600 | top three | 30 | J=148, G=92 | 40/148 (27.0%) (death G=37) | 14/40 (35.0%) | 0/40 (0.0%) | 6/40 (15.0%) | 8/40 (20.0%) | 12/40 (30.0%) | 22/148 (14.9%) (G=15) |
| up to 600 | other | 10 | J=190, G=107 | 64/190 (33.7%) (death G=63) | 2/64 (3.1%) | 20/64 (31.2%) | 30/64 (46.9%) | 1/64 (1.6%) | 11/64 (17.2%) | 8/190 (4.2%) (G=6) |
| up to 600 | other | 30 | J=190, G=107 | 91/190 (47.9%) (death G=75) | 12/91 (13.2%) | 23/91 (25.3%) | 33/91 (36.3%) | 1/91 (1.1%) | 22/91 (24.2%) | 17/190 (8.9%) (G=9) |
| 601–1,200 | ours | 10 | J=5, G=3 | 1/5 (20.0%) (death G=1) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 1/1 (100.0%) | 0/1 (0.0%) | 0/5 (0.0%) (G=0) |
| 601–1,200 | ours | 30 | J=5, G=3 | 2/5 (40.0%) (death G=2) | 0/2 (0.0%) | 0/2 (0.0%) | 0/2 (0.0%) | 1/2 (50.0%) | 1/2 (50.0%) | 0/5 (0.0%) (G=0) |
| 601–1,200 | top three | 10 | J=102, G=53 | 21/102 (20.6%) (death G=20) | 11/21 (52.4%) | 0/21 (0.0%) | 2/21 (9.5%) | 0/21 (0.0%) | 8/21 (38.1%) | 1/102 (1.0%) (G=1) |
| 601–1,200 | top three | 30 | J=102, G=53 | 36/102 (35.3%) (death G=30) | 20/36 (55.6%) | 0/36 (0.0%) | 4/36 (11.1%) | 0/36 (0.0%) | 12/36 (33.3%) | 3/102 (2.9%) (G=3) |
| 601–1,200 | other | 10 | J=96, G=50 | 21/96 (21.9%) (death G=21) | 9/21 (42.9%) | 2/21 (9.5%) | 5/21 (23.8%) | 1/21 (4.8%) | 4/21 (19.0%) | 1/96 (1.0%) (G=1) |
| 601–1,200 | other | 30 | J=96, G=50 | 40/96 (41.7%) (death G=32) | 19/40 (47.5%) | 7/40 (17.5%) | 7/40 (17.5%) | 2/40 (5.0%) | 5/40 (12.5%) | 1/96 (1.0%) (G=1) |
| 1,201–2,400 | ours | 10 | J=0, G=0 | 0/0 (not measured) (death G=0) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) (G=0) |
| 1,201–2,400 | ours | 30 | J=0, G=0 | 0/0 (not measured) (death G=0) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) (G=0) |
| 1,201–2,400 | top three | 10 | J=7, G=6 | 1/7 (14.3%) (death G=1) | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 3/7 (42.9%) (G=2) |
| 1,201–2,400 | top three | 30 | J=7, G=6 | 1/7 (14.3%) (death G=1) | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 3/7 (42.9%) (G=2) |
| 1,201–2,400 | other | 10 | J=8, G=7 | 5/8 (62.5%) (death G=5) | 1/5 (20.0%) | 0/5 (0.0%) | 1/5 (20.0%) | 2/5 (40.0%) | 1/5 (20.0%) | 0/8 (0.0%) (G=0) |
| 1,201–2,400 | other | 30 | J=8, G=7 | 6/8 (75.0%) (death G=5) | 1/6 (16.7%) | 0/6 (0.0%) | 1/6 (16.7%) | 3/6 (50.0%) | 1/6 (16.7%) | 0/8 (0.0%) (G=0) |
| over 2,400 | ours | 10 | J=0, G=0 | 0/0 (not measured) (death G=0) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) (G=0) |
| over 2,400 | ours | 30 | J=0, G=0 | 0/0 (not measured) (death G=0) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) (G=0) |
| over 2,400 | top three | 10 | J=2, G=2 | 0/2 (0.0%) (death G=0) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/2 (0.0%) (G=0) |
| over 2,400 | top three | 30 | J=2, G=2 | 0/2 (0.0%) (death G=0) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 0/0 (not measured) | 1/2 (50.0%) (G=1) |
| over 2,400 | other | 10 | J=12, G=12 | 4/12 (33.3%) (death G=4) | 0/4 (0.0%) | 1/4 (25.0%) | 1/4 (25.0%) | 1/4 (25.0%) | 1/4 (25.0%) | 0/12 (0.0%) (G=0) |
| over 2,400 | other | 30 | J=12, G=12 | 8/12 (66.7%) (death G=8) | 0/8 (0.0%) | 1/8 (12.5%) | 3/8 (37.5%) | 2/8 (25.0%) | 2/8 (25.0%) | 0/12 (0.0%) (G=0) |

| Size | Tag | Landing distance | Share of jumps (J) | Death within 10 (J) | Death within 30 (J) |
|---|---|---|---|---|---|
| up to 600 | ours | 0–3 | 65/133 (48.9%) (G=40) | 33/65 (50.8%) (death G=33) | 39/65 (60.0%) (death G=34) |
| up to 600 | ours | 4–8 | 65/133 (48.9%) (G=55) | 16/65 (24.6%) (death G=16) | 24/65 (36.9%) (death G=23) |
| up to 600 | ours | 9+ | 3/133 (2.3%) (G=3) | 1/3 (33.3%) (death G=1) | 1/3 (33.3%) (death G=1) |
| up to 600 | ours | not seen | 0/133 (0.0%) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| up to 600 | top three | 0–3 | 56/148 (37.8%) (G=44) | 23/56 (41.1%) (death G=22) | 27/56 (48.2%) (death G=26) |
| up to 600 | top three | 4–8 | 71/148 (48.0%) (G=50) | 4/71 (5.6%) (death G=4) | 13/71 (18.3%) (death G=13) |
| up to 600 | top three | 9+ | 20/148 (13.5%) (G=11) | 0/20 (0.0%) (death G=0) | 0/20 (0.0%) (death G=0) |
| up to 600 | top three | not seen | 1/148 (0.7%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| up to 600 | other | 0–3 | 97/190 (51.1%) (G=72) | 44/97 (45.4%) (death G=44) | 54/97 (55.7%) (death G=50) |
| up to 600 | other | 4–8 | 78/190 (41.1%) (G=54) | 15/78 (19.2%) (death G=15) | 31/78 (39.7%) (death G=27) |
| up to 600 | other | 9+ | 13/190 (6.8%) (G=12) | 3/13 (23.1%) (death G=3) | 4/13 (30.8%) (death G=4) |
| up to 600 | other | not seen | 2/190 (1.1%) (G=2) | 2/2 (100.0%) (death G=2) | 2/2 (100.0%) (death G=2) |
| 601–1,200 | ours | 0–3 | 1/5 (20.0%) (G=1) | 0/1 (0.0%) (death G=0) | 1/1 (100.0%) (death G=1) |
| 601–1,200 | ours | 4–8 | 3/5 (60.0%) (G=2) | 1/3 (33.3%) (death G=1) | 1/3 (33.3%) (death G=1) |
| 601–1,200 | ours | 9+ | 1/5 (20.0%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| 601–1,200 | ours | not seen | 0/5 (0.0%) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| 601–1,200 | top three | 0–3 | 23/102 (22.5%) (G=21) | 14/23 (60.9%) (death G=14) | 18/23 (78.3%) (death G=18) |
| 601–1,200 | top three | 4–8 | 53/102 (52.0%) (G=31) | 6/53 (11.3%) (death G=6) | 14/53 (26.4%) (death G=12) |
| 601–1,200 | top three | 9+ | 25/102 (24.5%) (G=17) | 1/25 (4.0%) (death G=1) | 4/25 (16.0%) (death G=3) |
| 601–1,200 | top three | not seen | 1/102 (1.0%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| 601–1,200 | other | 0–3 | 40/96 (41.7%) (G=28) | 14/40 (35.0%) (death G=14) | 20/40 (50.0%) (death G=17) |
| 601–1,200 | other | 4–8 | 37/96 (38.5%) (G=23) | 5/37 (13.5%) (death G=5) | 14/37 (37.8%) (death G=12) |
| 601–1,200 | other | 9+ | 17/96 (17.7%) (G=13) | 1/17 (5.9%) (death G=1) | 5/17 (29.4%) (death G=5) |
| 601–1,200 | other | not seen | 2/96 (2.1%) (G=2) | 1/2 (50.0%) (death G=1) | 1/2 (50.0%) (death G=1) |
| 1,201–2,400 | ours | 0–3 | 0/0 (not measured) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| 1,201–2,400 | ours | 4–8 | 0/0 (not measured) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| 1,201–2,400 | ours | 9+ | 0/0 (not measured) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| 1,201–2,400 | ours | not seen | 0/0 (not measured) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| 1,201–2,400 | top three | 0–3 | 3/7 (42.9%) (G=3) | 1/3 (33.3%) (death G=1) | 1/3 (33.3%) (death G=1) |
| 1,201–2,400 | top three | 4–8 | 3/7 (42.9%) (G=3) | 0/3 (0.0%) (death G=0) | 0/3 (0.0%) (death G=0) |
| 1,201–2,400 | top three | 9+ | 0/7 (0.0%) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| 1,201–2,400 | top three | not seen | 1/7 (14.3%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| 1,201–2,400 | other | 0–3 | 5/8 (62.5%) (G=4) | 3/5 (60.0%) (death G=3) | 4/5 (80.0%) (death G=3) |
| 1,201–2,400 | other | 4–8 | 3/8 (37.5%) (G=3) | 2/3 (66.7%) (death G=2) | 2/3 (66.7%) (death G=2) |
| 1,201–2,400 | other | 9+ | 0/8 (0.0%) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| 1,201–2,400 | other | not seen | 0/8 (0.0%) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | ours | 0–3 | 0/0 (not measured) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | ours | 4–8 | 0/0 (not measured) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | ours | 9+ | 0/0 (not measured) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | ours | not seen | 0/0 (not measured) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | top three | 0–3 | 1/2 (50.0%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| over 2,400 | top three | 4–8 | 1/2 (50.0%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| over 2,400 | top three | 9+ | 0/2 (0.0%) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | top three | not seen | 0/2 (0.0%) (G=0) | 0/0 (not measured) (death G=0) | 0/0 (not measured) (death G=0) |
| over 2,400 | other | 0–3 | 1/12 (8.3%) (G=1) | 0/1 (0.0%) (death G=0) | 0/1 (0.0%) (death G=0) |
| over 2,400 | other | 4–8 | 4/12 (33.3%) (G=4) | 1/4 (25.0%) (death G=1) | 3/4 (75.0%) (death G=3) |
| over 2,400 | other | 9+ | 6/12 (50.0%) (G=6) | 2/6 (33.3%) (death G=2) | 4/6 (66.7%) (death G=4) |
| over 2,400 | other | not seen | 1/12 (8.3%) (G=1) | 1/1 (100.0%) (death G=1) | 1/1 (100.0%) (death G=1) |

## 6. Every game where our queen jumped

Each row is G=1. Distances over 15 retain their numeric value and are labeled not seen. If the game ends before 30 further rounds, the shorter observation is stated.

| Game (G=1) | Source | Opponent | Map | Each jump and next 30 rounds | Final result |
|---|---|---|---|---|---|
| 980157 | ladder/top1 / dl-20261003 | life is NP hard | Stripes | r18: distance 5 [4–8], died +15 rounds (rammed by enemy); r22: distance 6 [4–8], died +11 rounds (rammed by enemy) | win / elimination |
| 980158 | ladder/top1 / dl-20261003 | life is NP hard | Prisoners Dilemma | r4: distance 6 [4–8], other-side, alive after 30 rounds; r62: distance 16 [not seen], alive after 30 rounds | win / elimination |
| 980563 | ladder/top1 / dl-20261003 | chaoliangUNSW | Prisoners Dilemma | r4: distance 6 [4–8], other-side, alive after 30 rounds; r62: distance 8 [4–8], alive after 30 rounds | win / elimination |
| 983819 | ladder/top1 / dl-20261003 | 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 | Prisoners Dilemma | r4: distance 2 [0–3], other-side, alive after 30 rounds; r32: distance 15 [9+], died +29 rounds (other) | loss / queen rule |
| 983822 | ladder/top1 / dl-20261003 | 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 | Stripes | r31: distance 3 [0–3], other-side, died +10 rounds (rammed by enemy); r35: distance 5 [4–8], died +6 rounds (rammed by enemy) | loss / elimination |
| 986833 | ladder/top1 / dl-20261003 | meowest | Prisoners Dilemma | r4: distance 4 [4–8], other-side, alive after 30 rounds; r62: distance 23 [not seen], alive after 30 rounds | win / elimination |
| 987049 | ladder/top1 / dl-20261003 | SilverSamurai | Portals | r4: distance 4 [4–8], other-side, alive after 30 rounds; r9: distance 17 [not seen], alive after 30 rounds; r141: distance 2 [0–3], other-side, alive after 30 rounds; r146: distance 10 [9+], alive after 30 rounds; r217: distance 2 [0–3], other-side, died +23 rounds (own body); r222: distance 3 [0–3], died +18 rounds (own body); r239: distance 2 [0–3], other-side, died +1 rounds (own body) | loss / longest dragon |
| 988920 | ladder/top1 / dl-20261003 | doofenshmirtz good incorporated | Stripes | r62: distance 2 [0–3], died +21 rounds (other); r66: distance 4 [4–8], other-side, died +17 rounds (other) | loss / elimination |
| 989284 | ladder/top1 / dl-20261003 | UnderTheC | Stripes | r18: distance 5 [4–8], died +25 rounds (wall); r22: distance 4 [4–8], died +21 rounds (wall); r41: distance 1 [0–3], other-side, died +2 rounds (wall) | loss / elimination |
| 989567 | ladder/top1 / dl-20261003 | UnderTheC | Stripes | r18: distance 6 [4–8], alive after 30 rounds; r22: distance 3 [0–3], alive after 30 rounds | win / elimination |
| 990089 | ladder/top1 / dl-20261003 | Kaizen | Prisoners Dilemma | r4: distance 5 [4–8], other-side, alive after 30 rounds; r20: distance 12 [9+], alive after 30 rounds | win / elimination |
| 990232 | ladder/top1 / dl-20261003 | tungtung67 | Prisoners Dilemma | r4: distance 6 [4–8], other-side, alive after 30 rounds; r62: distance 3 [0–3], alive after 30 rounds; r77: distance 5 [4–8], other-side, died +22 rounds (wall); r81: distance 6 [4–8], died +18 rounds (wall) | loss / queen rule |
| 990348 | ladder/top1 / dl-20261003 | Team SKKU | Maze | r100: distance 12 [9+], died +8 rounds (own body) | win / longest dragon |
| 990350 | ladder/top1 / dl-20261003 | Team SKKU | Portals | r4: distance 1 [0–3], other-side, died +6 rounds (team body) | loss / queen rule |
| 993186 | ladder/top1 / dl-20261003 | AllRed | Prisoners Dilemma | r4: distance 5 [4–8], other-side, alive after 30 rounds; r50: distance 14 [9+], alive after 30 rounds; r74: distance 3 [0–3], other-side, alive after 30 rounds; r78: distance 6 [4–8], alive after 30 rounds | win / elimination |
| 993429 | ladder/top1 / dl-20261003 | horse | Maze | r82: distance 10 [9+], died +7 rounds (wall) | loss / queen rule |
| 1002730 | ladder/top1 / dl-20261004 | doofenshmirtz good incorporated | Stripes | r18: distance 3 [0–3], alive after 30 rounds; r22: distance 2 [0–3], died +27 rounds (other) | win / elimination |
| 1003243 | ladder/top1 / dl-20261004 | AllRed | Portals | r4: distance 3 [0–3], other-side, alive after 30 rounds; r8: distance 18 [not seen], alive after 30 rounds; r61: distance 2 [0–3], other-side, died +1 rounds (wall) | loss / queen rule |
| 1003338 | ladder/top1 / dl-20261004 | AllRed | Portals | r4: distance 4 [4–8], other-side, died +5 rounds (team body) | win / longest dragon |
| 1004227 | ladder/top1 / dl-20261004 | avid coders | Portals | r4: distance 5 [4–8], other-side, died +6 rounds (team body) | win / longest dragon |
| 1006424 | ladder/top1 / dl-20261004 | Weneedmoretokens | Portals | r4: distance 3 [0–3], other-side, alive after 30 rounds; r9: distance 9 [9+], alive after 30 rounds; r48: distance 3 [0–3], other-side, died +2 rounds (wall) | loss / queen rule |
| 1006762 | ladder/top1 / dl-20261004 | f2p | Portals | r4: distance 4 [4–8], other-side, died +5 rounds (team body) | win / longest dragon |
| 1008434 | ladder/top1 / dl-20261004 | Shannon | Portals | r4: distance 6 [4–8], other-side, alive after 30 rounds; r9: distance 17 [not seen], alive after 30 rounds; r86: distance 2 [0–3], other-side, died +2 rounds (wall) | loss / queen rule |
| 1010361 | ladder/top1 / dl-20261004 | Weneedmoretokens | Portals | r4: distance 4 [4–8], other-side, died +5 rounds (team body) | win / longest dragon |
| 1010362 | ladder/top1 / dl-20261004 | Weneedmoretokens | Stripes | r18: distance 10 [9+], alive after 30 rounds; r22: distance 10 [9+], alive after 30 rounds | win / elimination |
| 1010770 | ladder/top1 / dl-20261004 | WeLikCoding | Portals | r4: distance 4 [4–8], other-side, died +5 rounds (team body) | win / longest dragon |
| 1017992 | ladder/top1 / dl-20261004 | food | Stripes | r21: distance 2 [0–3], died +9 rounds (other); r25: distance 6 [4–8], died +5 rounds (other) | win / elimination |
| 1021194 | ladder/top1 / dl-20261004 | Shannon | Stripes | r18: distance 5 [4–8], died +19 rounds (rammed by enemy); r22: distance 6 [4–8], died +15 rounds (rammed by enemy) | win / elimination |
| 1021729 | ladder/top1 / dl-20261004 | python.io | Stripes | r18: distance 8 [4–8], alive after 30 rounds; r22: distance 6 [4–8], alive after 30 rounds; r43: distance 5 [4–8], other-side, died +19 rounds (other); r47: distance 4 [4–8], other-side, died +15 rounds (other) | win / elimination |
| 1021750 | ladder/top1 / dl-20261004 | python.io | Maze | r49: distance 20 [not seen], alive after 30 rounds; r81: distance 7 [4–8], died +4 rounds (rammed by enemy) | loss / queen rule |
| 1021859 | ladder/top1 / dl-20261004 | ComTamSuonNuong | Portals | r4: distance 2 [0–3], other-side, died +5 rounds (team body) | loss / queen rule |
| 1021861 | ladder/top1 / dl-20261004 | ComTamSuonNuong | Stripes | r84: distance 9 [9+], died +8 rounds (rammed by enemy); r88: distance 7 [4–8], other-side, died +4 rounds (rammed by enemy) | win / elimination |
| 1022050 | ladder/top1 / dl-20261004 | food | Portals | r4: distance 4 [4–8], other-side, died +5 rounds (team body) | win / longest dragon |
| 1022708 | ladder/top1 / dl-20261004 | avid coders | Portals | r4: distance 4 [4–8], other-side, died +28 rounds (wall); r8: distance 9 [9+], died +24 rounds (wall); r30: distance 2 [0–3], other-side, died +2 rounds (wall) | loss / queen rule |
| 1023828 | ladder/top1 / dl-20261004 | forgot to mention | Maze | r101: distance 9 [9+], died +6 rounds (wall) | win / longest dragon |
| 1023829 | ladder/top1 / dl-20261004 | forgot to mention | Portals | r4: distance 2 [0–3], other-side, died +5 rounds (team body) | loss / queen rule |
| 1023830 | ladder/top1 / dl-20261004 | forgot to mention | Prisoners Dilemma | r4: distance 4 [4–8], other-side, alive after 30 rounds; r62: distance 14 [9+], died +29 rounds (wall) | loss / elimination |
| 1023834 | ladder/top1 / dl-20261004 | forgot to mention | Stripes | r18: distance 3 [0–3], died +28 rounds (rammed by enemy); r22: distance 4 [4–8], died +24 rounds (rammed by enemy) | loss / elimination |
| 1024557 | ladder/top1 / dl-20261004 | Goated | Prisoners Dilemma | r4: distance 2 [0–3], other-side, alive after 30 rounds; r62: distance 4 [4–8], alive after 30 rounds | win / elimination |
| 1025495 | ladder/top1 / dl-20261004 | Weneedmoretokens | Stripes | r18: distance 3 [0–3], died +10 rounds (rammed by enemy); r22: distance 5 [4–8], died +6 rounds (rammed by enemy) | loss / elimination |
| 1025811 | ladder/top1 / dl-20261004 | 中国人不准飞😡😡😡😡😡😡😡 | Prisoners Dilemma | r4: distance 4 [4–8], other-side, alive after 30 rounds; r62: distance 17 [not seen], alive after 30 rounds | win / elimination |
| 1026908 | ladder/top1 / dl-20261004 | Sieberrsec Industrie | Prisoners Dilemma | r4: distance 7 [4–8], other-side, alive after 30 rounds; r62: distance 6 [4–8], alive after 30 rounds; r110: distance 9 [9+], other-side, alive after 30 rounds; r114: distance 12 [9+], alive after 30 rounds | loss / queen rule |
| 1027022 | ladder/top1 / dl-20261004 | avid coders | Portals | r4: distance 4 [4–8], other-side, died +6 rounds (team body) | loss / queen rule |
| 1027812 | ladder/top1 / stride-old | test4 | Prisoners Dilemma | r4: distance 6 [4–8], other-side, alive after 30 rounds | win / elimination |
| 1027814 | ladder/top1 / stride-old | test4 | Portals | r4: distance 1 [0–3], other-side, alive after 30 rounds; r8: distance 18 [not seen], alive after 30 rounds; r70: distance 2 [0–3], other-side, alive after 30 rounds; r75: distance 3 [0–3], alive after 30 rounds; r100: distance 3 [0–3], other-side, alive after 30 rounds; r105: distance 6 [4–8], alive after 30 rounds; r174: distance 3 [0–3], other-side, died +1 rounds (wall) | loss / longest dragon |
| 1027820 | ladder/top1 / stride-old | test4 | Stripes | r18: distance 3 [0–3], died +13 rounds (other); r22: distance 4 [4–8], died +9 rounds (other) | loss / elimination |
| 1027969 | ladder/top1 / stride-old | WeHaveQuizzes | Prisoners Dilemma | r4: distance 6 [4–8], other-side, alive after 30 rounds; r62: distance 4 [4–8], alive after 30 rounds; r84: distance 6 [4–8], other-side, alive after 30 rounds; r88: distance 2 [0–3], alive after 30 rounds; r94: distance 6 [4–8], other-side, alive after 30 rounds; r99: distance 2 [0–3], alive after 30 rounds | loss / elimination |
| 1027971 | ladder/top1 / stride-old | WeHaveQuizzes | Portals | r4: distance 8 [4–8], other-side, alive after 30 rounds; r9: distance 17 [not seen], alive after 30 rounds; r58: distance 3 [0–3], other-side, alive after 30 rounds; r63: distance 5 [4–8], alive after 30 rounds | loss / longest dragon |
| 1029014 | ladder/top1 / stride-new | test4 | Prisoners Dilemma | r4: distance 6 [4–8], other-side, alive after 30 rounds; r62: distance 11 [9+], alive after 30 rounds; r112: distance 6 [4–8], other-side, alive through game end (+17 rounds); r116: distance 19 [not seen], alive through game end (+13 rounds) | win / elimination |
| 1029016 | ladder/top1 / stride-new | test4 | Portals | r4: distance 1 [0–3], other-side, died +6 rounds (team body) | loss / longest dragon |
| 1029022 | ladder/top1 / stride-new | test4 | Stripes | r18: distance 2 [0–3], alive after 30 rounds; r22: distance 4 [4–8], alive after 30 rounds; r65: distance 2 [0–3], died +4 rounds (rammed by enemy); r69: distance 1 [0–3], other-side, died +0 rounds (rammed by enemy) | loss / elimination |
| 1029029 | ladder/top1 / stride-new | WeHaveQuizzes | Prisoners Dilemma | r4: distance 4 [4–8], other-side, alive after 30 rounds | win / elimination |
| 1029031 | ladder/top1 / stride-new | WeHaveQuizzes | Portals | r4: distance 6 [4–8], other-side, died +5 rounds (team body) | loss / longest dragon |
| 1029036 | ladder/top1 / stride-new | WeHaveQuizzes | Maze | r87: distance 12 [9+], died +8 rounds (wall) | loss / longest dragon |
| 1029037 | ladder/top1 / stride-new | WeHaveQuizzes | Stripes | r18: distance 5 [4–8], alive after 30 rounds; r22: distance 6 [4–8], alive after 30 rounds | loss / elimination |
| 1043417 | ladder/top1 / dl-20261004 | pizza | Portals | r4: distance 10 [9+], other-side, died +5 rounds (team body) | win / longest dragon |
| 1043717 | ladder/top1 / dl-20261004 | avid coders | Portals | r4: distance 5 [4–8], other-side, died +5 rounds (own body) | loss / queen rule |
| 1044199 | ladder/top1 / dl-20261004 | test4 | Stripes | r28: distance 8 [4–8], other-side, alive after 30 rounds; r32: distance 7 [4–8], other-side, alive after 30 rounds; r197: distance 6 [4–8], died +1 rounds (wall) | win / elimination |
| 1044208 | ladder/top1 / dl-20261004 | test4 | Portals | r4: distance 1 [0–3], other-side, alive after 30 rounds; r9: distance 17 [not seen], alive after 30 rounds; r48: distance 2 [0–3], other-side, alive after 30 rounds; r53: distance 9 [9+], alive after 30 rounds; r106: distance 1 [0–3], other-side, died +2 rounds (own body) | loss / longest dragon |
| 1044513 | ladder/top1 / dl-20261004 | WeHaveQuizzes | Stripes | r18: distance 5 [4–8], died +11 rounds (wall); r22: distance 6 [4–8], died +7 rounds (wall) | loss / elimination |
| 1044522 | ladder/top1 / dl-20261004 | WeHaveQuizzes | Portals | r4: distance 7 [4–8], other-side, alive after 30 rounds; r9: distance 10 [9+], alive after 30 rounds; r310: distance 2 [0–3], other-side, died +1 rounds (own body) | loss / longest dragon |
| 1045202 | ladder/top1 / dl-20261004 | test4 | Portals | r4: distance 1 [0–3], other-side, alive after 30 rounds; r9: distance 2 [0–3], alive after 30 rounds; r24: distance 3 [0–3], other-side, alive after 30 rounds; r29: distance 3 [0–3], alive after 30 rounds; r35: distance 2 [0–3], other-side, alive after 30 rounds; r40: distance 7 [4–8], alive after 30 rounds; r46: distance 1 [0–3], other-side, alive after 30 rounds; r50: distance 10 [9+], alive after 30 rounds; r154: distance 1 [0–3], other-side, died +2 rounds (wall) | loss / longest dragon |
| 1045378 | ladder/top1 / dl-20261004 | WeHaveQuizzes | Stripes | r20: distance 3 [0–3], alive after 30 rounds; r24: distance 8 [4–8], alive after 30 rounds; r45: distance 4 [4–8], other-side, died +13 rounds (rammed by enemy); r49: distance 3 [0–3], other-side, died +9 rounds (rammed by enemy) | loss / elimination |
| 1045387 | ladder/top1 / dl-20261004 | WeHaveQuizzes | Portals | r4: distance 6 [4–8], other-side, died +5 rounds (team body) | loss / queen rule |
| 1046734 | ladder/top1 / dl-20261004 | tungtung67 | Prisoners Dilemma | r4: distance 6 [4–8], other-side, alive after 30 rounds; r8: distance 11 [9+], alive after 30 rounds | win / elimination |
| 1047319 | ladder/top1 / dl-20261004 | Adrak vali chai | Stripes | r36: distance 3 [0–3], died +12 rounds (rammed by enemy); r40: distance 5 [4–8], died +8 rounds (rammed by enemy) | win / elimination |
| 1048089 | ladder/top1 / dl-20261004 | avid coders | Portals | r4: distance 5 [4–8], other-side, alive after 30 rounds; r9: distance 10 [9+], alive after 30 rounds; r84: distance 3 [0–3], other-side, died +1 rounds (wall) | loss / longest dragon |
| 1049785 | ladder/top1 / dl-20261004 | Sieberrsec Industrie | Prisoners Dilemma | r4: distance 7 [4–8], other-side, alive after 30 rounds; r62: distance 24 [not seen], alive after 30 rounds | loss / queen rule |
| 1051804 | ladder/top1 / dl-20261004 | WeLikCoding | Stripes | r18: distance 3 [0–3], alive after 30 rounds; r22: distance 4 [4–8], alive after 30 rounds; r116: distance 8 [4–8], alive after 30 rounds; r121: distance 10 [9+], alive after 30 rounds; r193: distance 14 [9+], died +22 rounds (rammed by enemy); r197: distance 6 [4–8], other-side, died +18 rounds (rammed by enemy) | win / elimination |
| 1051805 | ladder/top1 / dl-20261004 | WeLikCoding | Prisoners Dilemma | r4: distance 6 [4–8], other-side, alive after 30 rounds; r17: distance 12 [9+], alive after 30 rounds | win / elimination |
| 1051928 | ladder/top1 / dl-20261004 | Um_nik da real goat | Prisoners Dilemma | r4: distance 4 [4–8], other-side, alive after 30 rounds; r50: distance 9 [9+], alive after 30 rounds; r88: distance 5 [4–8], other-side, alive after 30 rounds; r92: distance 22 [not seen], alive after 30 rounds | win / elimination |
| 1052757 | ladder/top1 / dl-20261004 | test4 | Maze | r135: distance 5 [4–8], alive after 30 rounds; r140: distance 6 [4–8], alive after 30 rounds | loss / longest dragon |
| 1052758 | ladder/top1 / dl-20261004 | test4 | Stripes | r18: distance 7 [4–8], alive after 30 rounds; r22: distance 10 [9+], alive after 30 rounds | win / elimination |
| 1052767 | ladder/top1 / dl-20261004 | test4 | Portals | r4: distance 4 [4–8], other-side, died +5 rounds (team body) | loss / longest dragon |
| 1053022 | ladder/top1 / dl-20261004 | WeHaveQuizzes | Stripes | r18: distance 5 [4–8], alive after 30 rounds; r22: distance 3 [0–3], alive after 30 rounds; r61: distance 3 [0–3], died +2 rounds (rammed by enemy) | loss / elimination |
| 1053031 | ladder/top1 / dl-20261004 | WeHaveQuizzes | Portals | r4: distance 8 [4–8], other-side, alive after 30 rounds; r9: distance 17 [not seen], alive after 30 rounds; r49: distance 3 [0–3], other-side, died +2 rounds (own body) | win / longest dragon |
| 1053380 | ladder/top1 / dl-20261004 | test4 | Maze | r92: distance 6 [4–8], other-side, alive after 30 rounds; r94: distance 14 [9+], other-side, alive after 30 rounds; r123: distance 5 [4–8], other-side, alive after 30 rounds | loss / queen rule |
| 1053390 | ladder/top1 / dl-20261004 | test4 | Portals | r4: distance 1 [0–3], other-side, alive after 30 rounds; r9: distance 2 [0–3], alive after 30 rounds; r123: distance 4 [4–8], other-side, died +2 rounds (wall) | win / longest dragon |
| 1053776 | ladder/top1 / dl-20261004 | WeHaveQuizzes | Stripes | r18: distance 5 [4–8], alive after 30 rounds; r22: distance 3 [0–3], alive after 30 rounds; r65: distance 5 [4–8], died +2 rounds (wall) | loss / elimination |
| 1053785 | ladder/top1 / dl-20261004 | WeHaveQuizzes | Portals | r4: distance 4 [4–8], other-side, died +5 rounds (team body) | loss / longest dragon |
| 1058147 | ladder/top1 / passage2-test-old | test4 | Stripes | r28: distance 8 [4–8], other-side, alive after 30 rounds; r32: distance 7 [4–8], other-side, alive after 30 rounds | win / elimination |
| 1058156 | ladder/top1 / passage2-test-old | test4 | Portals | r4: distance 1 [0–3], other-side, alive after 30 rounds; r9: distance 2 [0–3], alive after 30 rounds; r254: distance 2 [0–3], other-side, died +1 rounds (wall) | loss / queen rule |
| 1058367 | ladder/top1 / passage2-test-old | WeHaveQuizzes | Stripes | r18: distance 3 [0–3], died +4 rounds (rammed by enemy) | loss / elimination |
| 1058376 | ladder/top1 / passage2-test-old | WeHaveQuizzes | Portals | r4: distance 7 [4–8], other-side, alive after 30 rounds; r9: distance 10 [9+], alive after 30 rounds; r118: distance 2 [0–3], other-side, died +1 rounds (wall) | loss / queen rule |
| 1058858 | ladder/top1 / passage2-test-new | test4 | Portals | r4: distance 1 [0–3], other-side, alive after 30 rounds; r9: distance 2 [0–3], alive after 30 rounds; r89: distance 2 [0–3], other-side, died +1 rounds (wall) | loss / longest dragon |
| 1059076 | ladder/top1 / passage2-test-new | WeHaveQuizzes | Stripes | r48: distance 2 [0–3], died +1 rounds (wall) | win / elimination |
| 1059085 | ladder/top1 / passage2-test-new | WeHaveQuizzes | Portals | r4: distance 4 [4–8], other-side, died +5 rounds (team body) | win / longest dragon |
| 1063012 | ladder/top1 / qh31-test-old | test4 | Islands | r66: distance 5 [4–8], alive after 30 rounds | loss / longest dragon |
| 1063013 | ladder/top1 / qh31-test-old | test4 | Maze | r122: distance 6 [4–8], died +6 rounds (wall) | win / longest dragon |
| 1063023 | ladder/top1 / qh31-test-old | test4 | Portals | r4: distance 4 [4–8], other-side, alive after 30 rounds; r8: distance 18 [not seen], alive after 30 rounds; r75: distance 2 [0–3], other-side, died +28 rounds (own body); r80: distance 7 [4–8], died +23 rounds (own body); r102: distance 2 [0–3], other-side, died +1 rounds (own body) | loss / longest dragon |
| 1063242 | ladder/top1 / qh31-test-old | WeHaveQuizzes | Stripes | r18: distance 5 [4–8], alive after 30 rounds; r22: distance 3 [0–3], alive after 30 rounds; r49: distance 5 [4–8], alive after 30 rounds; r53: distance 8 [4–8], other-side, died +28 rounds (rammed by enemy) | loss / elimination |
| 1063251 | ladder/top1 / qh31-test-old | WeHaveQuizzes | Portals | r4: distance 6 [4–8], other-side, alive after 30 rounds; r9: distance 10 [9+], alive after 30 rounds; r61: distance 2 [0–3], other-side, died +1 rounds (wall) | loss / longest dragon |
| 1063672 | ladder/top1 / qh31-test-new | test4 | Maze | r148: distance 4 [4–8], other-side, died +4 rounds (team body) | win / longest dragon |
| 1063673 | ladder/top1 / qh31-test-new | test4 | Stripes | r34: distance 3 [0–3], other-side, alive after 30 rounds; r38: distance 4 [4–8], other-side, alive after 30 rounds; r53: distance 6 [4–8], other-side, alive after 30 rounds; r57: distance 5 [4–8], other-side, alive after 30 rounds; r100: distance 3 [0–3], died +5 rounds (rammed by enemy); r104: distance 2 [0–3], other-side, died +1 rounds (rammed by enemy) | loss / elimination |
| 1063682 | ladder/top1 / qh31-test-new | test4 | Portals | r4: distance 1 [0–3], other-side, died +5 rounds (team body) | loss / longest dragon |
| 1063766 | ladder/top1 / qh31-test-new | WeHaveQuizzes | Stripes | r18: distance 5 [4–8], died +17 rounds (rammed by enemy); r22: distance 3 [0–3], died +13 rounds (rammed by enemy); r33: distance 3 [0–3], died +2 rounds (rammed by enemy) | loss / elimination |
| 1063775 | ladder/top1 / qh31-test-new | WeHaveQuizzes | Portals | r4: distance 6 [4–8], other-side, alive after 30 rounds; r9: distance 10 [9+], alive after 30 rounds; r54: distance 3 [0–3], other-side, died +16 rounds (own body); r59: distance 7 [4–8], died +11 rounds (own body); r68: distance 2 [0–3], other-side, died +2 rounds (own body) | win / longest dragon |
| 1067907 | ladder/top1 / tc30-test-new | test4 | Stripes | r34: distance 2 [0–3], other-side, died +24 rounds (own body); r38: distance 3 [0–3], other-side, died +20 rounds (own body) | loss / elimination |
| 1067916 | ladder/top1 / tc30-test-new | test4 | Portals | r4: distance 1 [0–3], other-side, died +20 rounds (wall); r8: distance 2 [0–3], died +16 rounds (wall); r23: distance 1 [0–3], other-side, died +1 rounds (wall) | win / longest dragon |
| 1068053 | ladder/top1 / tc30-test-new | WeHaveQuizzes | Stripes | r18: distance 3 [0–3], died +4 rounds (rammed by enemy) | loss / elimination |
| 1068062 | ladder/top1 / tc30-test-new | WeHaveQuizzes | Portals | r4: distance 7 [4–8], other-side, alive after 30 rounds; r8: distance 10 [9+], alive after 30 rounds; r130: distance 1 [0–3], other-side, alive after 30 rounds; r135: distance 10 [9+], alive after 30 rounds | win / longest dragon |
| 1068692 | ladder/top1 / tc30-dev1-old | dev test 1 :P | Portals | r4: distance 1 [0–3], other-side, died +5 rounds (team body) | loss / longest dragon |
| 1069651 | ladder/top1 / tc30-dev1b-new | dev test 1 :P | Stripes | r18: distance 6 [4–8], alive after 30 rounds; r22: distance 8 [4–8], alive after 30 rounds; r43: distance 9 [9+], other-side, alive after 30 rounds; r47: distance 6 [4–8], other-side, alive after 30 rounds; r70: distance 7 [4–8], died +14 rounds (own body); r74: distance 7 [4–8], died +10 rounds (own body); r83: distance 2 [0–3], died +1 rounds (own body) | loss / elimination |
| 1069660 | ladder/top1 / tc30-dev1b-new | dev test 1 :P | Portals | r4: distance 1 [0–3], other-side, alive after 30 rounds; r9: distance 17 [not seen], alive after 30 rounds; r127: distance 2 [0–3], other-side, alive after 30 rounds; r132: distance 11 [9+], alive after 30 rounds; r215: distance 1 [0–3], other-side, died +2 rounds (wall) | loss / queen rule |
| 1096141 | qh31b-test-old / qh31b-test-old | test4 | Maze | r172: distance 2 [0–3], died +24 rounds (other); r175: distance 2 [0–3], other-side, died +21 rounds (other); r179: distance 5 [4–8], died +17 rounds (other); r182: distance 5 [4–8], died +14 rounds (other) | loss / queen rule |
| 1096142 | qh31b-test-old / qh31b-test-old | test4 | Stripes | r18: distance 3 [0–3], died +28 rounds (rammed by enemy); r22: distance 4 [4–8], died +24 rounds (rammed by enemy) | loss / elimination |
| 1096151 | qh31b-test-old / qh31b-test-old | test4 | Portals | r4: distance 4 [4–8], other-side, died +5 rounds (team body) | loss / longest dragon |
| 1096721 | qh31b-test-old / qh31b-test-old | WeHaveQuizzes | Stripes | r18: distance 5 [4–8], died +17 rounds (other); r22: distance 6 [4–8], died +13 rounds (other) | win / elimination |
| 1096730 | qh31b-test-old / qh31b-test-old | WeHaveQuizzes | Portals | r4: distance 7 [4–8], other-side, alive after 30 rounds; r8: distance 9 [9+], alive after 30 rounds; r126: distance 2 [0–3], other-side, alive after 30 rounds; r131: distance 9 [9+], alive after 30 rounds; r149: distance 2 [0–3], other-side, alive after 30 rounds; r154: distance 16 [not seen], alive after 30 rounds; r276: distance 3 [0–3], other-side, died +1 rounds (wall) | loss / longest dragon |
| 1098451 | qh31b-dev1-old / qh31b-dev1-old | dev test 1 :P | Stripes | r18: distance 9 [9+], alive after 30 rounds; r22: distance 8 [4–8], alive after 30 rounds; r90: distance 3 [0–3], other-side, died +3 rounds (wall) | win / elimination |
| 1098460 | qh31b-dev1-old / qh31b-dev1-old | dev test 1 :P | Portals | r4: distance 1 [0–3], other-side, alive after 30 rounds; r8: distance 18 [not seen], alive after 30 rounds; r58: distance 3 [0–3], other-side, died +2 rounds (wall) | loss / queen rule |

## 7. Elimination among all portal-map games

| Size | Elimination share |
|---|---|
| up to 600 | 251/410 (61.2%) (G=410) |
| 601–1,200 | 417/804 (51.9%) (G=804) |
| 1,201–2,400 | 29/445 (6.5%) (G=445) |
| over 2,400 | 3/288 (1.0%) (G=288) |

The table above uses every included portal-map game, whether either queen jumped or not. For completeness, the following table uses all input games, including non-portal maps.

| Size | Elimination share, including non-portal games |
|---|---|
| up to 600 | 523/851 (61.5%) (G=851) |
| 601–1,200 | 417/804 (51.9%) (G=804) |
| 1,201–2,400 | 29/445 (6.5%) (G=445) |
| over 2,400 | 3/288 (1.0%) (G=288) |

## Raw event hand-checks

Three distinct jumps were printed and checked directly against the original replay. Event indices are zero-based. The initial DRAGON order assigns the ids, and the initial team field assigns A/B. The separate `raw-checks.json` retains the counter's event records. The original replay events below were printed independently of the counter.

### Our queen: game 980157, Stripes, meow A, id 1 (G=1, J=1)

```text
EDGE 560 2 3
EDGE 561 2 3
578 r18 turnStart id=1
579 r18 dragonAction id=1 action=move dirs=[2]
580 r18 dragonUpdate id=1 head=(11,11) tail=(10,10)
1128 r33 dragonAction id=4 action=move dirs=[2]
1129 r33 dragonDeath id=1 reason_code=3 (head-on)
```

The head immediately before event 580 was (10,10), independently recovered from preceding updates/splits. Width 24 gives an edge-index stride of 25. Edge 560 is the north edge of (10,11), and edge 561 is the north edge of (11,11); both have label 3. Moving south from (10,10) crosses edge 560 and lands at (11,11). The normal wrapped Manhattan displacement is 2, greater than one. Confirmed: one counted jump at r18.

At that event the enemy heads were id 0 at (14,1) and id 4 at (21,8). Landing distances are 3+2=5 and 10+3=13; nearest distance is 5, in 4–8. Own/enemy queen start distances are 10/12, so this is not other-side. The queen died during enemy id 4's move at r33: 33−18=15 rounds, within 30 but not within 10. Confirmed against death event 1129.

### Top-three queen: game 1006642, Default, Vibing++ B, id 1 (G=1, J=1)

```text
EDGE 1591 2 1
EDGE 1875 2 1
1773 r19 turnStart id=1
1774 r19 dragonAction id=1 action=move dirs=[2]
1775 r19 dragonUpdate id=1 head=(27,28) tail=(7,22)
32424 r162 dragonAction id=1 action=split
32425 r162 dragonDeath id=1 reason_code=4 (no action)
```

The previous head was (7,23). Width 32 gives stride 33. Edge 1591 is the north edge of (7,24); edge 1875 is the north edge of (27,28). Both have label 1. South crosses the first edge and lands at (27,28). Normal wrapped displacement is 12+5=17, greater than one. Confirmed: one counted jump at r19.

The independently recovered enemy heads were (24,11), (7,7), (19,7), (8,2), (10,29), (20,0), (21,29), (1,30). The closest was id 14 at (21,29): 6+1=7, in 4–8; the next closest was (1,30), at 8. Own/enemy start distances are 7/9, so this is not other-side. Death was at r162: 162−19=143, outside both windows.

### Death within 10: game 980565, Stripes, chaoliangUNSW B, id 0 (G=1, J=1)

```text
EDGE 53 2 6
EDGE 54 2 6
EDGE 78 1 -1
2858 r55 dragonAction id=0 action=move dirs=[0]
2859 r55 tileChange
2860 r55 dragonUpdate id=0 head=(3,0) tail=(5,0)
3348 r60 dragonAction id=0 action=move dirs=[1]
3349 r60 dragonDeath id=0 reason_code=0 (wall)
```

The previous head was (4,1). Edge 54 is the north edge of (4,1); edge 53 is the north edge of (3,1). Both have label 6. North crosses edge 54 and lands on the north side of edge 53, at (3,0). Normal displacement is 1+1=2. Confirmed: one counted jump at r55.

The only enemy head was id 3 at (15,7), distance 12+5=17; none was within 15, confirming “not seen.” Own queen start was (21,1), enemy queen start was (2,10): landing distances are 7 and 3, confirming other-side. At r60 the queen's head was (2,1); its east move hits edge 78, the west edge of (3,1), marked wall. Death code 0 confirms wall. 60−55=5 rounds, within both 10 and 30. This confirms the counted death window, without claiming that the jump caused the death.

## Input checks and limits

- Portal-map parse failures: 0 games. Unknown portal status after load/header failure: 0 games. Total errors: 0.
- Non-portal games excluded: 441. Final survivor count, longest length and total length match replay result fields in all 1947 counted games. Every counted queen is id 0 or 1. Every long queen move matches a paired portal label.
- Independent comparison with existing top1 CSV and queen records: 1,911 ladder games / 3,822 queen-games checked; ending type, queen id, final queen survival, death round, and start-of-round-100 survival had 0 mismatches (validation.json). The 36 portal-map live games / 72 queen-games use the replay-result checks above.
- Round-limit endings use final queen length, then longest dragon, then total length, and the inferred winner is checked against the replay. Draws have their own column and are not wins.
- Portal crossings of ordinary distance one, and attempted portal entries ending in death before a landing update, are outside this detection definition. Intent and whether a portal was necessary were not measured.
- Body deaths use the next requested direction and the map transition, including portals, to identify the body owner at event time. Enemy-body and unresolved collisions go in other. Rammed by enemy means the queen was the non-acting head-on victim of an enemy actor; a queen initiating head-on goes in other.
- The round-100 subset uses eventual jump status, including jumps later than round 100. No matching by opponent, build, map or survival duration was done. These are counts, not controlled tests or causal estimates.
- Death-window denominators include jumps with less than the full window before game end. Their shorter observation is counted separately; absence of a recorded death is not a claim of survival beyond game end.
- Free-cell totals, actual bot visibility, and a usefulness threshold were not measured. No strategic interpretation is made.
- Reproduce: python3 -B data/analysis/queen-portals/count.py; inspect raw-checks.json and record checks in hand-checks.md; then python3 -B data/analysis/queen-portals/count.py --report. games.json stores counts and failures; summary.md is written last.
