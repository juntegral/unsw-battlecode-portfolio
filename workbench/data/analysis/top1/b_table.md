## The three-team table

Vibing++'s cells come from `deep-read.md` (15 games read by sub-session A) and `findings.md` (all games) unless a script of this pass
is named. SSS's and forgot's cells come from the 15 games of this pass (SSS 10, forgot 13) or from all games where it says so.

| # | behaviour | Vibing++ | SSS | forgot |
|---|---|---|---|---|
| 1 | Grows by splitting at length 4 into 2+2 | yes: 15 of 15 games; 46 of 62 early splits in 1063780 | yes: 10 of 10; 69 of 92 in 1059834, and at 5 into 2+3 (15 of 92) | yes: 13 of 13; 40 of 45 in 1059834, 122 of 156 in 1063806 |
| 2 | Small dragons die with no free cell from the first rounds (dead ends, crowding) | yes: 347 of 359 non-ram deaths in rounds 0-100 of six games (`b_open.py`), by a split order that cannot be made | yes: 314 of 317 in 10 games, by a move into its own or another body | yes: 484 of 488 in 13 games, by the suicide order |
| 3 | Small dragons kill themselves by choice in the opening | no (see 2) | no: 3 of 317 had a free cell | no: 4 of 488 |
| 4 | The queen is the "mother" (4 -> 2+2 again and again) | yes: 12 of 15 games | yes: 34 such splits in 10 games, through the whole game (8 in 1060356) | yes: 43 in 13 games, mostly before round 200 |
| 5 | Queen length in rounds 100-200 on large maps | 5-8 (all games); she eats for herself | 2-3 | 2-3 |
| 6 | The queen eats less than an average dragon of her team | not measured | yes: 2.1 against 4.7 natural pearls per 100 rounds, in 10 of 10 games | partly: 3.5 against 4.6 |
| 7 | The queen stays nearer her spawn than the rest of the team | no: 6-23 cells away, up to 44 (1069168) | yes: 10.8 cells against 16.7, in 8 of 10 games | partly: 12.0 against 17.8, but she walks out alone in the opening (27 cells at round 40 in 1067654) |
| 8 | Queen dead by round 100, large / medium / small maps (all games) | 10% / 24% / 54% | 8% / 7% / 30% | 30% / 20% / 37% |
| 9 | The queen steps away from an enemy head within 3 steps | yes: 151 of 151 rounds | yes: 36 of 39 (2 of the 3 others forced) | mostly: 75 of 88; 11 nearer, 3 of them fatal (1059840 r208, 1067641 r166, 1067654 r86) |
| 10 | The queen pays segments to get away | yes: 27 of 151 moves were 2-3 steps (7 -> 3 in 1067623) | no: 39 of 39 one-step moves | no: 85 one-step moves, 3 two-step |
| 11 | Allies turn towards an intruder near the queen | no: nothing done in 32 of 34 episodes | no: 40 ally moves nearer to it, 44 further | no: 24 nearer, 32 further |
| 12 | Intruders rammed near the queen all the same | 10 of 101 intruders | 6 in 10 games (27% of approaches with 3+ allies near, all games) | 13 in 13 games |
| 13 | A 2-3-long rams the enemy queen when she is in its view and reach | yes: 186 of 186 (all games) | yes: 155 of 155 | yes from round 100: 136 of 139; before round 100 only when not outnumbered: 47 of 51 against 38 of 127 |
| 14 | A dragon of 4 or more does the same, at any price | yes: 80 of 81 | yes: 95 of 99 (the 4 others explained) | no: 4-long 12 of 53 (it splits), 5-9 long 21 of 65, 10-12 long 0 of 22 |
| 15 | Rams a queen that is within reach but outside the attacker's own view | no: 1 of 214 | no: 0 of 273 (1067636 r485-486, a won game passed up) | no: 2 of 210 |
| 16 | Queen kills by a dragon of 5+ with a sprint of 4-6 steps | 6 of 7 kills read | 2 of 5 read (64% on large maps, all games) | 2 of 6 read |
| 17 | Small followers: a 2-3-long keeps the enemy queen in view for 6+ rounds, 3-4 steps away | seen (1067620: its #3 for 20 and 18 rounds; killer had her in view before in 3 of 7 kills) | yes: 14 streaks in 10 games, up to 30 rounds | yes: 14 in 13 games, up to 20 rounds |
| 18 | The sonar value carries the enemy queen's cell | not found in 2 games (`b_sonar4.py`) | yes: 26-39% of all pings while she is known (1060356, 1067641), old sightings repeated (1063806) | weak: 5-9% of pings (1059840, 1067641) |
| 19 | Pings from round 0 | yes (8,000-15,000 rays per 100 rounds) | no: 1-7 pings a round until round 119, then four per dragon per round | yes |
| 20 | A boxed-in queen of 4+ is cut just in front of the own segment at her head | yes: 67 cuts in 61 of 502 games (85 -> 3, 86 -> 3) | no: 0 in 503 games | no: 0 in 632 games |
| 21 | A boxed-in queen of 4+ sheds 2 from the tail per round and stays | rarely: 7 runs of 3+ rounds | yes: 29 runs in 22 games, up to 28 rounds | yes: 116 runs in 88 games, up to 43 rounds (102 -> 66 in 1067636) |
| 22 | A boxed-in queen of 2-3 dies | yes: `noaction` in 22% of games | yes: 48 of her 50 non-ram deaths, 10% of games | yes: 66 of 71, 11% of games |
| 23 | The queen splits to wait for a feeder | not seen | yes: 5 times in 2 games (1063806, 1067634) | not seen |
| 24 | Feeds a living queen by deliberate deaths of own dragons next to her | yes: 7 of 15 games | yes: 4 of the 5 games in which she lived past round 430 (not 1060356) | yes: 6 of the 7 games in which she lived past round 220 (in the seventh, 1067644, she was the last dragon) |
| 25 | When the queen feeding starts | she is 11-12 at round 300 by her own eating; fed from round 200-405 | 8+ long by round 350 in 27 of 102 games with the enemy queen alive at round 300 and 3 of 91 with her dead; otherwise the last 75 rounds or never (all games) | round 200-225 whatever the enemy queen does: 8+ long by round 300 in 175 of 189 games |
| 26 | Wins when both queens live to round 500 (all games) | 24 of 40 | 27 of 48 | 52 of 71 |
| 27 | Builds a non-queen leader while its own queen is alive | yes | yes: 1059834 (83), 1060356 (95), 1060000 (58, with the enemy queen alive: lost) | late and second to the queen (1067667: 62 beside a 53-long queen) |
| 28 | Long dragons of 15+ die by choice next to a longer one or the queen | yes: 15-22-longs next to the queen | yes: 8 | yes: 18 |
| 29 | Loses on the longest dragon with the larger total length (all games) | 20 of 53 such losses | 20 of 59 | 12 of 66 |
| 30 | Long dragons reverse-split with a free cell at the head | yes: 38 of 70 in 1063780 (`b_pack.py`) | yes: 63 of 74 | rarely: 47 of 272; the other 225 had no free cell |
| 31 | Leaders of 15+ are rammed by dragons of 2-4 | yes: 5 of 8 | 5 of 12 (7 by a 5-9-long) | 19 of 21 |
| 32 | Rams enemy leaders of 15+ with 2-4-longs that walk 20-38 steps to them | yes | yes: 13 kills, all by 2-4-longs | yes: 7 kills, 4 by 2-4-longs |
| 33 | Split first, then ram a leader with the cheap part | yes: 4 of 10 | 1 of 13 (1059834 r482-484) | no: 0 of 7 |
| 34 | Spreads over the whole board by round 60-90 on Australia and Islands | no: 6 of 64 squares at round 60 (1067620) | sometimes: 9 squares in 1059840, 16 in 1060356 | yes: 20-22 squares at round 60, 27-32 at round 90 |

### What all three do

1. Split at 4 into 2+2 and let the queen be the mother on maps with few starting dragons (rows 1, 4).
2. Lose small dragons, and 2-3-long queens, to cells with no way out; none of the three avoids one-cell dead ends (rows 2, 22).
3. Have the queen step away from a close enemy; give her no escort (rows 9, 11).
4. Ram the enemy queen with a 2-3-long whenever she is in its view and reach, from round 100 on without exception (row 13).
5. Never ram a queen that is outside the attacker's own 7x7 view (row 15).
6. Feed a living queen in the end game by deliberate deaths of own dragons next to her, and merge long dragons the same way (rows 24, 28).
7. Lose leaders to small dragons that walk a long way to them, and kill enemy leaders the same way (rows 31, 32).

### What only one or two do

- Vibing++ and SSS: ram the queen at any length and any price (row 14); reverse-split with a free cell (row 30); build a leader beside a living queen (row 27).
- SSS and forgot: keep the queen 2-3 long until she is fed (row 5); shed 2 per round when a long queen is boxed in (row 21).
- Vibing++ only: a queen that grows on her own to 5-13 and pays segments to flee (rows 5, 10); the cut that leaves a boxed-in queen 3 long (row 20); the split trick as a habit (row 33).
- SSS only: a queen that eats half as much as her team and stays near home (rows 6, 7), with the fewest early queen deaths on large and medium maps (row 8); the enemy queen's cell in a quarter to two fifths of its pings (row 18); feeding that waits for the enemy queen (row 25); the queen waiting for a feeder (row 23).
- forgot only: the head count before round 100 and long dragons that do not ram (rows 13, 14); feeding from round 200 by the clock (row 25), which wins the both-queens-alive games (row 26); the wide spread on big maps (row 34); a queen that sometimes steps towards an enemy head (row 9).
