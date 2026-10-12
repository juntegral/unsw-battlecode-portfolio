## Us against the top three and against our opponents

Large maps and means per game unless a row says otherwise. meow = our 111 large-map games against 2000+ teams (Schooltime left
out), all builds; where the live bot (99 games) and the trade-on-contact test build (12 games) differ, both are in the cell.
"Our opponents" = test4 / WHQ in their games against us (42 and 44 large-map games); "(all)" = every opponent in those 111
games, for the scripts that pool the other side of our games. forgot, SSS, Vibing++ = their own games against 2000+ teams.
Sources: `c_agg.py` (rows 1-4, 6, 12, 21-26, 30-32), `c_tilesall.py` (5), `c_adj.py` (7, 8), `c_contest.py` (9), `c_avoid.py` (10, 11),
`c_ramsteps.py` (13), `c_rams.py` (14, 18), `c_ramlocal.py` and `c_rambatch.py` (15, 16), `c_front.py` (17), `c_midall.py` (19, 20,
27-29), `c_endstate.py` (33, 34), `c_bybatch.py` (the build split of rows 1, 14, 17).

| # | behaviour | meow | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| 1 | Units at round 100 / 150 | 43 / 47 (live 42 / 46, test build 45 / 52) | 56 / 62 and 53 / 59 | 52 / 58 | 54 / 58 | 42 / 50 |
| 2 | Natural pearls eaten, rounds 0-49 / 50-99 / 100-149 | 72 / 91 / 79 | 76 / 125 / 129 and 81 / 122 / 133 | 84 / 121 / 117 | 75 / 118 / 122 | 71 / 113 / 121 |
| 3 | Of those, on fountains of the enemy's half, rounds 50-149 | 34 | 76 and 76 | 58 | 65 | 65 |
| 4 | Own heads standing in the own half, rounds 50-99 | 76% | 68% and 71% | 71% | 72% | 69% |
| 5 | Fountain tiles of the own half eaten from by round 150 | 62% | 80% (all) | 69% | 69% | 69% |
| 6 | Undisturbed pearl within 6 steps: rounds until eaten, rounds 50-99 | 2.6 | 3.0 and 3.1 | 2.6 | 2.6 | 2.0 |
| 7 | Free pearl on the next cell is eaten (dragon of 2-4, a way out behind it, nobody near), rounds 0-149 | 80-82% | 78-84% (all) | 89-91% | 70-78% | 83-87% |
| 8 | The same in rounds 150-299 | 60% (live 59%, test build 62%) | 85% (all) | 91% | 80% | 89% |
| 9 | Natural pearl at the same distance from an own and an enemy head: own team eats it | 35% | 57% (all) | 46% | 48% | 50% |
| 10 | Meeting (enemy head on the next cell, both 4 or shorter): rams it | no: 12% (live 10%, test build 31%) | yes: 36% (all) | yes: 37% | yes: 42% | yes: 36% |
| 11 | The same when shorter than the enemy / of the same length | 18% / 13% (live 14% / 11%, test build 49% / 36%) | 62% / 33% (all) | 63% / 36% | 86% / 41% | 56% / 37% |
| 12 | Enemy head in view: ends the turn farther from it, rounds 50-99 | 34% | 25% and 25% | 22% | 28% | 27% |
| 13 | Rams made by charging (a move of two or more steps that ends in the enemy head), rounds 0-149 | no: 1.0 (test build 3.9) | yes: 13.7 (all) | yes: 8.7 | yes: 10.2 | yes: 12.9 |
| 14 | Share of the game's rams it starts | 24% (live 22%, test build 37%) | 71% and 80% | 48% | 48% | 57% |
| 15 | Pearls of ram corpses (both dragons) eaten by own team | 28% (live 27%, test build 33%) | 67% (all) | 47% | 49% | 50% |
| 16 | The same with equal numbers of other heads within 8 steps | 26% | 62% (all) | 47% | 49% | 48% |
| 17 | Share of the rams that happen in the own half | 58% (live 58%, test build 57%) | 40% (all) | 47% | 48% | 47% |
| 18 | Change in (own - enemy) total length from rams and their pearls, whole game | -110 | +68 and +148 | -16 | -36 | +12 |
| 19 | Splits by a dragon of exactly 4, rounds 0-99 | 56 | 85 (all) | 107 | 75 | 81 |
| 20 | Sheds (a dragon of 5+ keeps its front two segments), rounds 0-99 | 39 | 22 (all) | 9 | 16 | 27 |
| 21 | Boxed deaths, rounds 0-149 | 82 | 78 and 85 | 95 | 67 | 103 |
| 22 | Non-ram deaths with a free cell, rounds 0-149 | 6.4, of which 6.3 steps through a portal onto a body | 0.5 and 3.4 | 0.3 | 1.2 | 4.1 |
| 23 | Moves of two or more steps, rounds 50-99 (segments paid) | 3 (0) | 25 (6) and 40 (6) | 10 (3) | 43 (7) | 38 (5) |
| 24 | A second own head within 2 steps of an eaten pearl, rounds 50-99 | 14 | 30 and 27 | 30 | 35 | 34 |
| 25 | Cells visited by round 90 | 752 | 895 and 787 | 908 | 821 | 677 |
| 26 | Parent-child path distance 5 / 10 rounds after a split, rounds 0-149 | 6.2 / 8.0 | 6.1 / 8.7 and 6.4 / 8.5 | 6.1 / 8.8 | 5.7 / 7.9 | 5.9 / 8.1 |
| 27 | Ordinary splits, rounds 150-199 | 15 | 24 (all) | 59 | 33 | 53 |
| 28 | Natural pearls per 100 dragon-rounds of a 2-long, rounds 150-199 | 1.25 | 2.5 (all) | 2.8 | 2.8 | 3.3 |
| 29 | Dragons alive in rounds 150-199, of length 2 / 3-4 / 5-9 / 10+ | 24 / 16 / 3 / 0.3 | 22 / 24 / 12 / 3 (all) | 30 / 24 / 4 / 0.5 | 26 / 24 / 6 / 1 | 26 / 20 / 4 / 1 |
| 30 | Goes into narrow fountain corridors: Maze, fountains of the own half eaten from by round 140 (of 19) | partly: 9.7 | 12.2 and 18.1 | 12.3 | 15.4 | 15.2 |
| 31 | Eats in a fountain pocket whose door is a portal: Stripes, pearls eaten on own-half fountains in rounds 0-149 | late or not: 7 | 19 and 39 | 28 | 26 | 29 |
| 32 | Dragons that have not eaten for 20 rounds, share at round 90 | 47% | 39% and 39% | 31% | 44% | 28% |
| 33 | Games in which the own total length is below the opponent's at round 300 | 108 of 109 | (ahead of us in 108 of 109) | 82 of 158 | 48 of 139 | 40 of 127 |
| 34 | Wins among those games | 11 = 10% | | 29 = 35% | 24 = 50% | 16 = 40% |

Where we stand apart from all five columns, in the losing direction: rows 3-5, 8-18, 27, 28, 33 and 34. Where we are like the
others: rows 6, 7, 21 and 26. Row 24: we crowd a pearl less than anyone, which is not a loss in itself. Rows 19 and 20: the
shed excess is Slithery Fight alone (125 a game against 56); on the other large maps the fewer splits at 4 follow the fewer
pearls. Rows 10, 11 and 14: the test build is at the others' level at a meeting and still starts only 37% of the rams, because
it charges 3.9 times a game where they charge 9-14 times (row 13).
