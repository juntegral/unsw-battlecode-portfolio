# Our queen's deaths after round 300: main (switch off) against #38 (switch on)

Zhe's question: what killed the queen after round 300 in main and in the stay-near-home version, how long was she, and how did each death happen step by step.

Written 2026-10-07. Read-only work on the kept replays. No games were run and no bot code was changed.

## Short answer

- After round 300 she does not die by wall or by her own body in either version (0 and 0). She is rammed head-on by an enemy head: 3 of 6 deaths in main, 5 of 8 in #38.
- Four deaths per version are on tower_defense and are the same death in both versions (same round, tile, length and killer). Off that map it is 2 deaths in main and 4 in #38, all six head-on.
- The four extra #38 deaths are not new deaths. In those four pairs main's queen had already died before round 300 (rounds 38, 92, 112, 147). With the switch on she lived past 300 and was 6, 22, 27 and 85 long when she was rammed.
- Every head-on after round 300 happened during the enemy's action, never during hers.
- The numbers are too small to say the two versions differ after round 300: 14 and 16 queens were alive at round 300.

## What "after round 300" is

- The queen rule itself is applied once, after round 500: the longer queen wins and a dead queen counts as 0 (`rules/ALL.md` line 182). The rules text has no change at round 300 (the number does not appear in `rules/ALL.md`).
- Round 300 is a constant of our bot. Read from `battlecode/mybot2/main.cpp` at `0e03867` (sha256 equal to `bots/off/main.cpp`):
  `QUEEN_SAFE_ROUND = 300` and `QUEEN_GAME_FEED_ROUND = 300` (lines 149 to 150). From round 300 the queen sets `queen_game` and the feeding phase starts at 300 instead of 400 (lines 522 to 527), and she gets the leader bonus (lines 1776 to 1779), so team-mates walk to her and die next to her to feed her.
  This holds only where `is_queen()` is true: more than 600 cells, or `home_closed` (lines 3332 to 3334).
- In #38 the loop stops at the same round: `QL_UNTIL = 300` (`bots/on/main.cpp` line 136, used at line 3944). So from round 300 both versions run the same queen code. They differ only in where she stands and how long she is when round 300 arrives. Read from code, not tested.
- Measured side of this: the queens that died long after 300 had eaten 18 to 82 pearls from round 300 on, and team-mates die with "no valid action" beside her in the traces below.

## What the files cover

| run | games | replays | covered here |
|---|---|---|---|
| hunter run, against main with QUEEN_HUNT on and QUEEN_CHASE_DIST 8 | 68 pairs = 136 games, 17 maps | `replays/` | yes |
| check run, against plain main | 16 pairs = 32 games, 4 maps (australia, default, queen_of_spades, weakhold) | `~/meow-loop-out/card-38/attempt-1/replays` | yes |
| 400-pair outcome run against main (held-out 160, transposed 160, old 10 80) | 800 games | none: `outcome-plan.json` has `"keep": false` | **no** |

`verify/deaths.json` holds the first two runs (290 rows = 146 deaths of our queen + 144 of the enemy queen). The 400-pair run is not in it and cannot be added: its rows (`held.rows.jsonl`, `transposed.rows.jsonl`, `old10.rows.jsonl`) record winner, lengths and how the game ended, with no queen fields, and no replay was kept. The only replays under `attempt-1` are the 32 of the check run, the smoke picks and the identity checks.

## Counts (measured)

No death falls on round 300 itself, so "round 300 or later" and "after round 300" give the same rows. The earliest is round 324.

Hunter run, 68 games per version:

| | main (switch off) | #38 (switch on) |
|---|---|---|
| queen dead before round 300 | 53 | 48 |
| game over before round 300 with her alive | 1 | 4 |
| queen alive at round 300 | 14 | 16 |
| **died after round 300** | **6** | **8** |
| alive at the end, of the games that reached round 300 | 8 | 8 |
| alive at the end, all games | 9 | 12 |
| died after round 300, tower_defense left out | 2 of 10 | 4 of 12 |

Cause by version, deaths after round 300, with her length at death:

| cause | main (switch off) | #38 (switch on) |
|---|---|---|
| head-on, an enemy head moved into her head | 3: lengths 2, 4, 30 | 5: lengths 4, 6, 22, 27, 85 |
| no valid action (her turn produced no action) | 2: lengths 2, 3 | 2: lengths 2, 3 |
| hit another body (a team-mate's) | 1: length 3 | 1: length 3 |
| wall | 0 | 0 |
| own body | 0 | 0 |
| all | 6: min 2, median 3, max 30 | 8: min 2, median 5, max 85 |

Check run against plain main, 16 games per version: main had no queen alive at round 300 (16 of 16 dead before). #38 had 1 alive at round 300 and she died at round 369, head-on, 2 long. One more #38 game ended before round 300 with her alive.

Queens alive at the end, hunter run, games that reached round 300:

| | main (switch off) | #38 (switch on) |
|---|---|---|
| maps | schooltime 4, trauma 3, default 1 | schooltime 4, trauma 4 |
| final lengths | 3, 3, 3, 3, 32, 37, 39, 65 | 3, 3, 3, 3, 20, 23, 24, 36 |
| wins among them | 4 | 1 |

Her length at round 300, queens alive then: main 2, 2, 2, 3 ×9, 5, 6. #38 2 ×6, 3 ×7, 4, 4, 8.

For scale, the hunter's own queen in the same games (same code as main, facing our bots, which do not hunt): 13 and 14 alive at round 300, 5 and 4 died after it, of which 4 and 4 on tower_defense. Off tower_defense that is 1 death in 19 (around_unsw 3000/0, round 369, 20 long, head-on) against our 6 in 22.

## Every death of our queen after round 300

Side 0 = team A, queen is dragon 0. Side 1 = team B, queen is dragon 1. Replay file = `<name>.replay`.

| run | replay | map (cells) | version | side | round | cause | length | length at r300 | pearls from r300 | action running at her death | enemy queen | game |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hunter | base_around_unsw_3000_1 | around_unsw (4096) | main | 1 | 354 | head-on | 30 | 6 | 24 | enemy #525, 36 long, move WWNWSSEEEEE | dead r99 | win |
| hunter | base_trauma_3000_1 | trauma (1152) | main | 1 | 421 | head-on | 2 | 2 | 0 | enemy #203, 3 long, move N | alive, 43 at the end | loss |
| hunter | base_tower_defense_3000_0 | tower_defense (512) | main | 0 | 403 | no valid action | 3 | 2 | 1 | her own turn, no action | dead r479 | win |
| hunter | base_tower_defense_3001_0 | tower_defense (512) | main | 0 | 403 | no valid action | 2 | 2 | 0 | her own turn, no action | dead r436 | win |
| hunter | base_tower_defense_3000_1 | tower_defense (512) | main | 1 | 432 | head-on | 4 | 3 | 9 | enemy #34, 3 long, move EE | dead r403 | loss |
| hunter | base_tower_defense_3001_1 | tower_defense (512) | main | 1 | 370 | other body | 3 | 3 | 0 | her own move E into a team-mate | dead r403 | loss |
| hunter | candidate_around_unsw_3001_1 | around_unsw (4096) | #38 | 1 | 324 | head-on | 6 | 8 | 4 | enemy #469, 17 long, move WNWW | dead r151 | loss |
| hunter | candidate_default_3001_1 | default (1024) | #38 | 1 | 371 | head-on | 27 | 4 | 23 | enemy #176, 9 long, move NNNE | dead r230 | win |
| hunter | candidate_maze_3001_0 | maze (1152) | #38 | 0 | 330 | head-on | 22 | 4 | 18 | enemy #426, 7 long, move WNNNWW | alive, 126 at the end | loss |
| hunter | candidate_maze_3001_1 | maze (1152) | #38 | 1 | 483 | head-on | 85 | 3 | 82 | enemy #740, 26 long, move SSW | dead r92 | loss |
| hunter | candidate_tower_defense_3000_0 | tower_defense (512) | #38 | 0 | 403 | no valid action | 3 | 2 | 1 | her own turn, no action | dead r479 | win |
| hunter | candidate_tower_defense_3001_0 | tower_defense (512) | #38 | 0 | 403 | no valid action | 2 | 2 | 0 | her own turn, no action | dead r436 | win |
| hunter | candidate_tower_defense_3000_1 | tower_defense (512) | #38 | 1 | 432 | head-on | 4 | 3 | 9 | enemy #34, 3 long, move EE | dead r403 | loss |
| hunter | candidate_tower_defense_3001_1 | tower_defense (512) | #38 | 1 | 370 | other body | 3 | 3 | 0 | her own move E into a team-mate | dead r403 | loss |
| check | candidate_weakhold_13801_0 | weakhold (600) | #38 | 0 | 369 | head-on | 2 | 2 | 0 | enemy #262, 2 long, move W | dead r172 | loss |

"length at r300 8, length at death 6" in the around_unsw #38 row is not a slip: she paid length for sprint steps in between.

The other version in the same pair (same map, seed and side):

| death after r300 | the paired game |
|---|---|
| main, around_unsw 3000/1, r354 | #38 queen died r174, head-on, 2 long |
| main, trauma 3000/1, r421 | #38 queen alive at the end, 36 long (lost 36 to 51 on the queen rule) |
| #38, around_unsw 3001/1, r324 | main queen died r38, head-on, 2 long |
| #38, default 3001/1, r371 | main queen died r147, head-on, 2 long |
| #38, maze 3001/0, r330 | main queen died r92, wall, 3 long |
| #38, maze 3001/1, r483 | main queen died r112, wall, 3 long |
| tower_defense, all four | the same death in both versions |
| check run, #38, weakhold 13801/0, r369 | main queen died r97, wall, 2 long |

## How each head-on happened (measured)

Turn order is by dragon id, so the queen (id 0 or 1) acts before every non-queen dragon in a round. In all 9 head-on deaths after round 300 (8 hunter run, 1 check run) the enemy moved into her head during its own action, later in the same round as her last move.

A dragon sees the 7x7 window around its head (`helper.hpp` line 24, `VISION_RADIUS = 3`). "In her window" below is taken at the start of her last action. "Steps" is the step of the enemy's action on which it entered her tile. Free steps are ceil(length / 4); further steps cost one segment each.

| replay | round | her last action | killer: length, free steps | killer's head in her window | its segments in her window | steps to her head (paid) | group |
|---|---|---|---|---|---|---|---|
| base_around_unsw_3000_1 | 354 | 29 long, move NW (only N was open) | 36, 9 | yes | 2, body cut by the edge | 11 (2) | A |
| candidate_around_unsw_3001_1 | 324 | 6 long, move N | 17, 5 | yes | 4, cut | 4 (0) | A |
| candidate_default_3001_1 | 371 | 26 long, move N | 9, 3 | yes | 2, cut | 4 (1) | A |
| candidate_maze_3001_1 | 483 | 84 long, move WN | 26, 7 | yes | 1, cut | 3 (0) | A |
| candidate_maze_3001_0 | 330 | 22 long, move S | 7, 2 | **no** (3 columns, 4 rows away) | 0 | 6 (4) | B |
| base_ and candidate_tower_defense_3000_1 | 432 | 5 long, move WWW (1 paid) | 3, 1 | **no** (5 columns away) | 0 | 2 (1) | B |
| base_trauma_3000_1 | 421 | 2 long, move W (the only open side) | 3, 1 | yes | 3 | 1 (0) | C |
| check run, candidate_weakhold_13801_0 | 369 | 2 long, move E (the only open side) | 2, 1 | yes | 2 | 1 (0) | C |

- **Group A, 4 deaths (1 main, 3 #38):** she saw the head, moved, and the enemy covered 3 to 11 steps into her new tile. Only 1 to 4 of its segments were inside her window.
- **Group B, 2 situations, 3 rows (1 main, 2 #38, the tower_defense one is the same game in both):** its head was outside her window when she moved. On maze the hunter paid 4 of its 7 segments to reach her. On tower_defense the same head had been in her window two rounds earlier (round 430: she at (26,7), it at (25,9)).
- **Group C, 2 deaths (1 main, 1 #38 in the check run):** she was 2 long with one side open and the enemy head next to that tile.

Per version, hunter run: main A 1, B 1, C 1. #38 A 3, B 2, C 0.

## Step-by-step traces

Columns: round, her head, her length, what each side N E S W held at the start of her action (w kelp, s herself, f free, m or M team-mate body or head, x or X enemy body or head), what she did. Boards: Q her head, q her body, M and m our other dragons, X and x enemy, o pearl, `|` and `-` kelp.

### Main (switch off)

**1. base_around_unsw_3000_1, around_unsw 64x64, side 1, round 354, head-on, 30 long. The common case.**

| round | head | len | N E S W | she did | around her |
|---|---|---|---|---|---|
| 346 | (35,27) | 22 | f s w f | W S E | team-mate #609 (3 long) dies "no valid action" at (35,35) |
| 347 | (35,28) | 22 | w f f s | S S | team-mate #570 (2) dies "no valid action" at (34,32) |
| 348 | (35,30) | 23 | s f f w | S | team-mate #606 (4) dies "no valid action" at (33,32) |
| 349 | (35,31) | 23 | s f w f | W | no enemy head within 8 |
| 350 | (34,31) | 24 | f s w f | W S | 13 pearls within 4 tiles |
| 351 | (33,32) | 26 | s w f f | S | enemy #369 (5 long) at 7, #553 (2) at 7 |
| 352 | (33,33) | 26 | s w f w | S | |
| 353 | (33,34) | 27 | s f f f | W N | enemy #525 (34 long) appears at (28,30), 9 away, and moves E S to (29,31) |
| 354 | (32,33) | 29 | f w s w | N W, to (31,32), eats, 30 long | #525 (36 long) at (29,31): 3 columns and 2 rows away, 2 of its segments in her window |

Then #525 moves W W N W S S E E E E E, eleven steps around the kelp (9 free, 2 paid), and the last one enters (31,32). Both die. She had grown from 6 at round 300 to 30 on dropped pearls. The game was still won on longest dragon, 55 to 31; the enemy queen had died in round 99.

**2. base_trauma_3000_1, trauma 48x24, side 1, round 421, head-on, 2 long. Cornered by one small hunter.**

She was 2 long at round 300 and ate nothing after it. Enemy #203 (3 long) had its head within 8 tiles of hers for 40 rounds in a row before the kill.

| round | head | len | N E S W | she did | enemy #203 at the start of her action |
|---|---|---|---|---|---|
| 416 | (44,0) | 2 | w f f s | S | (42,2), 4 away |
| 417 | (44,1) | 2 | s f f f | E | (43,2), 2 away |
| 418 | (45,1) | 2 | f f f s | E | (44,2), 2 away |
| 419 | (46,1) | 2 | f f f s | E | (45,2), 2 away |
| 420 | (47,1) | 2 | f w f s | N, into the corner (47,0) | (46,2), 2 away. S would be the tile beside its head. It then moves N to (46,1) |
| 421 | (47,0) | 2 | w w s f | W, the only side open | (46,1), which touches (46,0) |

#203 steps N into her head on its one free step. Board at the start of her last action:

```
+-+-+-+-+-+-+-+-+-+-+-+-+-
 . . . . . . Q|. . . . . .
+ + + + + + + + + + + + +
 . . . . . X q|. . . . . .
+ + + + + + + + + + + + +
 . . . . x x .|. . . . . .
```

The enemy queen was alive and 43 long at the end, so this game was lost on the queen rule with or without the ram.

**3. base_tower_defense_3000_0, tower_defense 32x16 (512 cells), side 0, round 403, no valid action, 3 long. The odd one.**

| round | head | len | N E S W | she did | around her |
|---|---|---|---|---|---|
| 399 | (3,2) | 3 | w f s f | W | |
| 400 | (2,2) | 3 | f s f w | S | |
| 401 | (2,3) | 3 | s f f w | S | team-mate #9 (3 long) dies "no valid action" at (5,6) |
| 402 | (2,4) | 3 | s f f w | E | team-mates #6 and #20 (2 long) die "no valid action" at (5,3) and (4,5). Team-mate #50 is 11 long (9 in round 397) |
| 403 | (3,4) | 3 | f f f s | **nothing** | three sides free, no enemy head within 6. #50, now 12 long, has its head at (4,5), two tiles away |

```
 . .|.|.|q . . o . . .
+ + + + + + + + + + +
 . .|.|M|q Q . . . . .          r403, before her turn
+ + + + + + + + + + +
 . .|.|m|. . M m . m m          the M at (4,5) is #50
```

The same death happens in base_tower_defense_3001_0 (round 403, 2 long) and in both #38 twins. In this game 19 of our dragons die with "no valid action" from round 401 on (`verify/none_check.py`).

### #38 (switch on)

**4. candidate_maze_3001_1, maze 48x24, side 1, round 483, head-on, 85 long. The costliest.**

She was 3 long at round 300 and ate 82 pearls after it.

| round | head | len | N E S W | she did | enemy #740 at the start of her action |
|---|---|---|---|---|---|
| 479 | (42,5) | 81 | s s f s | S S E N | (42,0), 21 long, 5 away |
| 480 | (43,6) | 82 | s f s s | E | (43,1), 22 long, 5 away |
| 481 | (44,6) | 82 | s f f s | E E E | (44,0), 23 long, 6 away. It then moves E E E S to (47,1) |
| 482 | (47,6) | 84 | f w f s | N | (47,1), 26 long, same column, 5 rows up: outside her window. It then moves S to (47,2) |
| 483 | (47,5) | 84 | f w s f | W N, to (46,4), eats, 85 long | (47,2), 26 long, 3 rows up: on the edge of her window, only its head visible |

#740 moves S S W, three of its seven free steps, into (46,4). Both die. Board at the start of her last action (kelp runs down the east side of her column):

```
 x . . . . . . X|. . . . . . .       #740's head at (47,2)
+ + + + + + + + + + + + + + +
 x . q q o o . .|. . . . . . .
+ + + + + + + + + + + + + + +
 q q q q q q o .|. . . . . . .
+ + + + + + + + + + + + + + +
 q q q q q . . Q|. . X x x . .       she is at (47,5)
+ + + + + + + + + + + + + +-+
 q q q q q q q q|. . . . . . .
```

The game was lost on longest dragon, 10 to 74. The enemy queen had died in round 92, so until round 483 our live queen was winning the game on the queen rule.

**5. candidate_maze_3001_0, maze 48x24, side 0, round 330, head-on, 22 long. A head she could not see.**

| round | head | len | N E S W | she did | around her |
|---|---|---|---|---|---|
| 325 | (6,4) | 19 | f f s s | E E N | team-mate #463 (2 long) dies "no valid action" at (9,3) |
| 326 | (8,3) | 21 | f f s f | E S | no enemy head within 8 |
| 327 | (9,4) | 22 | s f f s | S | none within 9 |
| 328 | (9,5) | 22 | s f f f | S | none within 9 |
| 329 | (9,6) | 22 | s f f f | S | enemy #426 (7 long) shows up 9 away at (13,12). It moves N W to (12,11) |
| 330 | (9,7) | 22 | s f f f | S, to (9,8) | #426 at (12,11): 3 columns and 4 rows from her, outside her window |

#426 moves W N N N W W, six steps for a 7-long dragon (2 free, 4 paid, it would be 3 long afterwards), into (9,8). Both die. The enemy queen lived and ended 126 long: lost on the queen rule.

**6. candidate_default_3001_1, default 32x32, side 1, round 371, head-on, 27 long. Followed for four rounds.**

| round | head | len | N E S W | she did | enemy #176 (9 long) at the start of her action |
|---|---|---|---|---|---|
| 368 | (9,12) | 26 | s w f f | S | (7,20), 9 away. It moves N N |
| 369 | (9,13) | 26 | s w f f | W | (7,18), 7 away. It moves N N |
| 370 | (8,13) | 26 | f s f f | W N | (7,16), 4 away. It moves W N N to (6,14) |
| 371 | (7,12) | 26 | f f s f | N, to (7,11), eats, 27 long | (6,14): 1 column and 2 rows away, 2 segments in her window |

#176 moves N N N E (3 free, 1 paid) into (7,11). Both die. The game was still won on longest, 33 to 9; the enemy queen had died in round 230.

candidate_around_unsw_3001_1 (round 324, 6 long) is the same shape: enemy #469, 17 long, on her row three tiles east, she steps N, it moves W N W W on four of its five free steps.

### The same in both versions, and the check run

**7. tower_defense 3001/1, round 370, hit another body, 3 long (base_ and candidate_ replays).** She walks east along the south wall of a room. A 9-long team-mate (#5) lies along the row above her and a 2-long team-mate (#7) is ahead of her.

```
|. . m m m . .|.|.
+ + + + + + + + +
|. . q q Q m M|o|.          r370: north #5's body, east #7's body, south kelp, west herself
+-+-+-+-+-+-+ + +
```

In round 369 east was her only free side; in round 370 nothing is free and she moves E into #7. No enemy head within 5 tiles in her last six actions. At 3 long she cannot split to wait. This is the "our own dragons closed her exit" case that `verify/report.md` counts before round 300.

**8. tower_defense 3000/1, round 432, head-on, 4 long (both versions).** Four enemy heads within 7 tiles (#14, #19, #34, #56). She is at (29,8) against the east kelp with #14 (3 long) at (28,10) in her window. She sprints W W W along the row to (26,8), paying one segment. #34 (3 long) is at (24,8), five columns west and outside her window, and moves E E (1 free, 1 paid) into her head.

**9. check run, candidate_weakhold_13801_0, weakhold 40x15, side 0, round 369, head-on, 2 long.** From round 362 she has no way out (`verify/recount.py`: no 16-step path with the other dragons frozen), and from round 365 every action has one open side. She walks N N N W N E N through a one-tile-wide passage to (10,5) and then E. Enemy #262 (2 long) comes west along the same passage; at its last action its own options are kelp, itself, kelp and her head. Both had one move. The opponent here is plain main, with no queen hunt.

## Read from the code, not tested

Line numbers are `battlecode/mybot2/main.cpp` at `0e03867` (= `bots/off/main.cpp`). The replays carry no bot logs (0 `dragonLog` events), so what the bot saw and scored cannot be checked.

1. **The hunter's side.** With `QUEEN_HUNT` on, any non-queen dragon that sees our queen's head makes it a target (lines 2574 to 2583) and may spend its whole sprint, free and paid, up to `QUEEN_HUNT_STEPS = 12` steps, to reach it (line 2623). With `QUEEN_CHASE_DIST = 8` it walks toward her last seen position (lines 578 to 582). That fits what the replays show: 2 to 11 steps, up to 4 paid, one hunter 40 rounds on her heels.
2. **She sizes an enemy by the part she can see.** `map_hits` (lines 3739 to 3795) takes `parts` = segments of that enemy in her window, or the most she saw of it in the last 3 rounds (lines 3753 to 3758, `GHOST_ROUNDS = 3`). A body that runs out of the window counts as at least 3 long (line 3763). Reach = max(free steps of that size, min(full sprint, `QS_PAY_REACH = 3`)) (lines 3759 to 3765, constant at line 131). The older threat map does the same with visible parts (lines 2471 to 2476).
   Applying that formula to what her window showed in the four group A deaths gives a reach of 2, 3, 2 and 2 steps, and the killers came 11, 4, 4 and 3 steps. So the tile she moved to would have been rated out of reach. This is the formula run on replay positions with no memory of earlier sightings, not the bot's own value.
3. **Heads outside the window do not exist for this check.** `map_hits` walks `enemy_heads`, the heads visible this turn. Remembered heads only raise the size of a head that is visible again. `SHARE_SIGHT` is off (line 139). That matches group B.
4. **She moves first.** With the lowest id she commits to a tile before any hunter moves, so a safe tile has to be outside what every nearby head can cover in one action. Nothing in the bot can react after the hunter has moved.
5. **Round 403 on tower_defense looks like the queen feeding herself to the leader.** A feeder that stands within `FEEDER_DIE_DIST = 3` of the visible leader ends its turn with no action (lines 551 to 554, 4924 to 4935, 2334 to 2337), which the engine records as "no valid action". `pick_feed_target` keeps the queen out of this only through `is_queen()` (line 2303), and `is_queen()` is false on a map of 600 cells or fewer unless `home_closed` was set (lines 3332 to 3334, `QUEEN_MIN_CELLS = 600` at line 159). tower_defense has 512 cells, and the feeding phase starts in round 401 there (`ENDGAME_ROUND = 400`, line 44). The board fits: three free sides, no enemy near, a 12-long team-mate two tiles away, three team-mates dying the same way in rounds 401 and 402. `verify/report.md` item 12 left this unexplained and says the bot has no suicide command; the no-output return at lines 551 to 554 is that command.
6. **Round 370 on tower_defense.** Both ways of keeping team-mates off her exits are off: `QUEEN_ALLY_BLOCK = false` (line 163) and `QUEEN_GIVE_WAY = 0` (line 195), and the waiting split needs length 4 (`QW_MIN_LENGTH`, line 124). Same reading as in `verify/report.md`.
7. **Why #38 has more deaths after 300.** Not from different code after 300 (the loop is off). The four pairs above show the queens that #38 kept alive past 300 dying later to the same ram.

## Measured and inferred, side by side

| | measured from the replays | inferred |
|---|---|---|
| counts, causes, lengths, rounds, who moved | yes, 168 games, equal to `verify/deaths.json` row by row | |
| the same four tower_defense deaths in both versions | yes (round, tile, length, killer equal) | that the switch does nothing on that map |
| head-on always on the enemy's action, steps and paid steps | yes | that these are deliberate queen hunts (the check-run death is not: plain main has no hunt) |
| killer's head and segments inside her window | yes, with a plain 7x7 window on replay positions | what the bot's own view held |
| reach her check would have given | the formula run on replay positions | that this is why she chose the tile |
| round 403 = self-feed | board and neighbours' deaths | the code path |
| #38 moves deaths from before 300 to after 300 | the four pairs | that it holds beyond these four |

## Limits

- **Sample.** 14 and 16 queens alive at round 300, 6 and 8 deaths, and 4 of each are one map played the same in both versions. 2 of 10 against 4 of 12 says nothing about a difference between the versions.
- **Opponent.** All but one death are against the hunting spar. Against plain main only one of our queens reached round 300 in 32 games, so there is no after-300 picture against a non-hunting opponent, and the 400-pair run cannot give one (no replays).
- **Maps that kill both queens by design** (autarky_v0, prisoners_dilemma_v0, slithery_fight_v0, rounds 9, 6 and 4): they do not matter after round 300. No queen of either side reaches round 300 there, so they add nothing to these counts and nothing to the denominators.
- **Maps in the after-300 set.** Queens alive at round 300 come from six maps only: schooltime 4, tower_defense 4, trauma 4 in each version, plus around_unsw 1, default 1 (both) and maze 2 (#38). On the other eleven maps she is dead before round 300 in every game.
- **Seeds.** Two seeds per map and both sides. Seven of the eight head-on rows are side 1.
- **Window.** "In her window" ignores what she remembered or was told; "reach by the formula" ignores her 3-round memory of a head's size. Both are stated where used.
- The 4 identical tower_defense pairs were compared on the death row only (round, cause, length, head, last action, last 12 actions), not move by move for the whole game.

## Against the earlier numbers

- `result.md`: queen deaths 59 (53 before round 300) and 56 (48) give 6 and 8 after. Alive at round 300 14 and 16, alive at the end 9 and 12. All equal here. The 9 and 12 include 1 and 4 games that ended before round 300 with her alive.
- `verify/report.md` and `verify/deaths.json`: all 146 rows of our queen equal on round, cause and length (`after300.py list`, last line). Of its totals 28 wall, 16 own body, 3 other body, 64 head-on, 4 no action, the part after round 300 is 0, 0, 2, 8, 4. All four "no action" deaths are after round 300 and all on tower_defense. Its "52 of 64 head-on during an enemy action" fits: all 8 after round 300 are enemy actions, the 12 during her own action are before 300.
- **One thing that did not match the brief for this note:** the queen rule does not start at round 300. It is applied after round 500. Round 300 is our bot's own switch (feeding the queen, and the end of the #38 loop).
- **One thing added to the report:** its "could not determine" for the tower_defense no-action deaths has a candidate explanation in the code (point 5 above). The counts are unchanged.
- The lists in `verify/report.md` cite `~/meow-release/mybot2/main.cpp`. The line numbers here are for the team repo file at `0e03867`; the constants named in both (lines 124, 159, 163, 195) sit on the same lines.

## Script and how to re-run

`after300/after300.py`, read-only, from the `unsw-swarm` root. It reuses the run's replay reader (`harness/replay.py`), the map reader (`card_38_check.load_map`) and the board drawing of `verify/recount.py`; the death rows, window and step counts are rebuilt in it.

```
python3 data/local/hunter38/after300/after300.py list       # counts, denominators, every death, compare with verify/deaths.json (about 5 minutes)
python3 data/local/hunter38/after300/after300.py killers    # the head-on table: window, segments seen, steps, paid steps (about 5 minutes)
python3 data/local/hunter38/after300/after300.py trace base_around_unsw_3000_1 --back 8 --near 9 --radius 6
python3 data/local/hunter38/after300/after300.py trace base_trauma_3000_1 --back 8 --near 9 --radius 6
python3 data/local/hunter38/after300/after300.py trace base_tower_defense_3000_0 --back 6 --near 6
python3 data/local/hunter38/after300/after300.py trace candidate_maze_3001_1 --back 8 --near 10 --radius 7
python3 data/local/hunter38/after300/after300.py trace candidate_maze_3001_0 --back 6 --near 9 --radius 6
python3 data/local/hunter38/after300/after300.py trace candidate_default_3001_1 --back 6 --near 9 --radius 6
python3 data/local/hunter38/after300/after300.py trace candidate_around_unsw_3001_1 --back 6 --near 9 --radius 6
python3 data/local/hunter38/after300/after300.py trace base_tower_defense_3000_1 --back 6 --near 8
python3 data/local/hunter38/after300/after300.py trace base_tower_defense_3001_1 --back 5 --near 5 --radius 4 --boards 3
python3 data/local/hunter38/after300/after300.py trace candidate_weakhold_13801_0 --run plain --back 12 --near 8
```

`trace` prints, per round, her head, length, the four sides, her action, every other head within `--near` tiles, each nearby enemy's action, and the board before her last action and at her death. Rounds are the replay's own labels, 0 to 499.

To watch one in a viewer: the replay files are `data/local/hunter38/replays/<name>.replay` (hunter run) and `~/meow-loop-out/card-38/attempt-1/replays/<name>.replay` (check run).
