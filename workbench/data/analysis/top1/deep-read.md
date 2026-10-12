# Close read of 15 replays of Vibing++ (team 306), sub-session A

Written 2026-10-05 for team meow (1119). Vibing++ is rank 1 by elo in the collected games. Every game below was read with
`story.py events`, `story.py view`, the digest tool and three small scripts written for this pass (`a_pack.py`, `a_open.py`,
`a_box.py`; their outputs are in `a_out/`). A replay shows positions, actions, deaths, pearls and sonar rays. It does not show what
a bot intended, remembered or knew; where a sentence goes beyond what the replay shows it is marked "inference".

The three findings that matter most:

1. **Vibing++ was not seen choosing to throw its queen away.** Every time its queen was cut down by a split that was not an ordinary
   "shed 2" split, or died by her own order (14 events in 8 of the 15 games: 10 splits and 4 deaths), her head had no free
   neighbouring cell. It looks like a choice only because the forced split usually leaves her 3 long.
   This cost three games that were won on the queen rule at that moment (1063789, 1052703, 1067619).
2. **A hunter rams the enemy queen only when she is inside its own 7x7 view**, and then always. All 7 queen kills and all 27 turns
   on which a kill was possible but not made fit this. Six of the seven killers were 5 to 11 long and finished with a sprint of 4 to 6 steps.
3. **Seven of the nine losses were behind by a factor of 1.5 or more in units at some point between round 50 and 100.** In the
   five of them where it was counted, own dragons ate half or less of the natural pearls the opponent ate per 10 rounds in
   rounds 40-90 (a third or less on Trauma and Tower Defense); on Australia they also kept killing themselves at the usual rate.

For our own bot, the appendix at the end is the shortest route to a result: in two of our losses our dragons passed 10 turns on which
the enemy queen was in view and within reach. Vibing++ passed none in the games read here.

## Games read

| # | game id | map | size | opponent (elo) | result | end type | own queen | enemy queen |
|---|---|---|---|---|---|---|---|---|
| 1 | 1063780 | Around UNSW | large | forgot to mention (2288) | win | queen rule, 28 vs dead | alive | rammed r34 by a 5-long, 5-step sprint |
| 2 | 1069168 | Islands | large | tungtung67 (2118) | win | queen rule, 29 vs dead | alive | rammed r223 by an 11-long, 4 steps |
| 3 | 1067620 | Australia | large | forgot to mention (2412) | loss | queen rule, dead vs 39 | rammed r178 by a 9-long, 6 steps | alive |
| 4 | 1063789 | Slithery Fight | large | forgot to mention (2288) | loss | queen rule, 4 vs 50 | alive; forced split 85 -> 3 at r484 | alive |
| 5 | 1067623 | Slithery Fight | large | forgot to mention (2412) | loss | longest, 75 vs 83 | rammed r238 by a 2-long, next cell | rammed r150 by a 10-long, 6 steps |
| 6 | 1064500 | Around UNSW | large | horse (2194) | win | longest, 88 vs 82 | rammed r333 by a 22-long split child | rammed r83 by a 7-long split child, 5 steps |
| 7 | 1052703 | Islands | large | SSS (2335) | loss | longest, 18 vs 44 | died r263 in a one-cell dead end | rammed r216 by a 5-long, 4 steps |
| 8 | 1056036 | Australia | large | SSS (2322) | win | longest, 81 vs 24 | rammed r55 by a 3-long, 2 steps | rammed r472 by a 10-long split child, 4 steps |
| 9 | 1067619 | Maze | medium | forgot to mention (2412) | loss | longest, 68 vs 73 | died r366, blocked by an own 14-long | killed herself r127 |
| 10 | 1063792 | Trauma | medium | forgot to mention (2288) | loss | queen rule, 35 vs 48 | alive | alive |
| 11 | 1064508 | Trauma | medium | horse (2194) | win | queen rule, 32 vs 23 | alive | alive |
| 12 | 1063783 | Portals | small | forgot to mention (2288) | loss | queen rule, dead vs 29 | died r131, blocked by two own tails | alive |
| 13 | 1063793 | Tower Defense | small | forgot to mention (2288) | loss | wiped out r188 | rammed r147 by a 2-long in a corridor | alive |
| 14 | 1063784 | Devil | small | forgot to mention (2288) | win | wipe-out r171 | died r37, blocked by her own child | rammed r36 by a 3-long, next cell |
| 15 | 1064507 | Devil | small | horse (2194) | loss | wiped out r253 | rammed r24 by a 4-long, 4 steps | died r90 (own move) |

8 large, 3 medium, 4 small; 6 wins and 9 losses. Game 15 was read for its opening and the queen's death only. All eight mandatory
games are included. Not read: the two contrast games of team 1119 and the Autarky games. Four more games were checked for one
point each and are not in the counts unless a sentence says so: 1062216 and 1065203 for the surviving queen and the queen kill
(answers a and c), 1067617 (Portals, r132) and 1067612 (Stripes, r31) for the queen's death (answer e).

## Per-game notes

Reading conventions used below. "Own" = Vibing++ (team 306), the protagonist. `#44` is a dragon id, `L5` a length of 5.
"d4" = 4 steps along the shortest path that respects kelp, wrap and portals (dragon bodies ignored).
"In view" = inside the 7x7 square around a dragon's head (at most 3 cells away in each direction).
"Free steps" = the ceil(L/4) steps a dragon may take per turn without losing a segment; every further step costs one segment.
"Reverse split" = a long dragon splits and keeps only its 2 or 3 front segments; the child gets the rest, with its head at the old tail.
"Self-kill" = a death with reason `noaction`. Vibing++ does it by ordering a split that cannot be carried out (the events tool prints
`SPLIT` followed by `DIES (noaction)`); forgot uses the suicide action. Everything in these notes is what the replay shows unless it is marked "inference".

### 1. 1063780 Around UNSW (large), win over forgot to mention, queen rule (own queen 28, forgot queen dead)

- **Opening.** 10 dragons each (total length 36, one 10-long, queen 4). In rounds 0-60 own made 46 splits of 4 -> 2+2 and 13 of 5 -> 2+3; the 10-long shed 2 at a time. 21 self-kills in rounds 0-60. Units: r30 22 vs 19, r50 35 vs 34, r80 57 vs 37, r100 61 vs 44. Natural pearls eaten per 10 rounds: own 12, 23, 27, 25, 28, 31, 35 against forgot 8, 19, 24, 24, 15, 25, 19.
- **Queen.** She does not split early. She eats natural pearls near her spawn (43,21): 4 long -> 7 (r20) -> 8 (r50) -> 12 (r80) -> 13 (r130), within 7 cells of the spawn until round 50, later 6-21 cells away, in open water (20-41 of 41 cells reachable within 4 steps). At 12-13 long she has 3-4 free steps and uses them: r127 `WWS`, r129 `WNE`, r132 `EES`, r135 `WWNE`, r136 `NWWS`.
- **Enemy heads near her.** 16 came within 6 steps, 7 times one was within 3 steps (r129-130, 134, 138, 173, 419, 428, 432-433); the closest was 2 steps (r173, forgot #364, 3 long). Each time she moved away with a 2-4 step move; the intruders were 2-3 long (reach 1-2) and never caught up. No ally rammed any of them; she had 0-1 allies within 6 steps at those moments. forgot never had a single turn with a free path to her head within reach (0 chances in `q3`).
- **Her two splits were forced.** r216 at (56,17): her head was at the closed end of a 2-wide corridor, kelp to the north and west, her own body east (57,17) and south (56,18). She split 13 -> 3+10 and walked out south the next round. r449 at (49,35): kelp east, team B bodies on the other three sides (own 22-long #1094 and 9-long #1109 were crowding in to feed her). She split 9 -> 3+6.
- **Queen 3 long, rounds 216-375.** She stays 14-23 cells from her spawn around (52-57, 19-34) with 0-3 allies within 6 steps; no enemy head within 8 steps at any 20-round checkpoint from r200 to r400.
- **Queen fed late.** From r375: 6 (r380), 7 (r400), 9 (r420); after the forced split at r449 she is 3 again and is fed to 28 in 50 rounds: 23 pearls from own self-kills in rounds 450-499. Own #1094 (22 long) kills itself at (50,39) at r453, 6 cells from her (she eats 4 of its 11 pearls); own #1135 (19 long) at (48,36) at r460 (she eats 7 of 10).
- **Enemy queen.** forgot's queen splits at round 0 (4 -> 2+2) and walks east for 12 rounds straight, 16 cells from her spawn by r25, with no ally within 6 steps in rounds 25-28 and 33-34. Killed r34 at (27,35) by own #44.
- **The hunter.** #44 was born at r20 as a 2-long, 4 cells from other own foragers, and was foraging: it ate natural pearls at r24, 26, 28, 29, 31, 32, 33 and split 4 -> 2+2 at r27 and again at r30, when the queen was already in its view (in view from r29, d5). r32: 3 long, d4. r33: 4 long, d4. r34: 5 long (reach 5), she steps west to (27,35); it sprints 5 steps `SSWWS` from (29,32) and rams her. It rammed on the first turn its reach covered the path. One or two team-mates also had her in view from r29; sonar rays from them ended on #44 at r32-33 (3 of 5 rays).
- **Late game.** 71 reverse splits by own dragons of 12+, 19 of them by dragons of 20+ (r303 23 -> 2+21 ... r482 58 -> 2+56, r487 56 -> 2+54). The leader id changes about every 25 rounds because of them. Own 17-long #1078 was rammed at r414 by a forgot 2-long from the next cell; a 16-long (#703) was rammed at r246 in the round it was born.
- **Mid-game contact (digest counts).** Own rams on enemy heads: 96 (per 100 rounds 17, 33, 23, 16, 7); the opponent's rams on own heads: 77. Enemy heads that came within 6 steps of the own queen: 16 (left 15, rammed by an own dragon 1).
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 30, 2-long with a 2-3-step move 3, 3-4-long from the next cell 15, 3-4-long with a 2-4-step move 40, 5-9-long 8, 10 or longer 0. Own lengths at r200: 2-long 31, 3-4-long 20, 5-9-long 4, 10-19-long 3.
- **Sonar.** Rays sent per 100 rounds: own 8722, 15238, 15138, 14018, 8545; opponent 3995, 8808, 8654, 8111, 5650. The values are packed and cannot be read.
- Decisive moment: round 34 at (27,35), the 5-step sprint of a 5-long forager into forgot's 3-long queen; after that own only had to keep its queen alive, and no forgot dragon ever got a path to her within its reach.

### 2. 1069168 Islands (large), win over tungtung67, queen rule (own queen 29, enemy queen dead)

- **Opening.** 5 dragons each (total 12). The own queen is the "mother": she eats 8 natural pearls in 22 rounds and sheds a 2-long child at r23, r30 (8 -> 6+2) and r54 (9 -> 7+2); at r77 she has no free neighbour (kelp north, her own segments 2, 4 and 6 on the other sides), splits 9 -> 3+6 and stays 3 long until round 400. Units: r30 14 vs 15, r50 24 vs 20, r80 44 vs 31, r100 60 vs 30. Only 6 own self-kills in rounds 0-60.
- **Intruders near the queen early.** tungtung67 #4 (3 long) came to 3 steps at r29; she moved away. It came back at r51-52; own #49 (3 long) rammed it from the next cell at r52, 3 steps from her. This is the only intruder an ally removed.
- **Queen routine 77-400.** 3 long, and she travels: (34,3) at r125, (23,34) at r175, (16,30) at r200, (6,17) at r225, (4,28) at r300, (53,34) at r375, up to 44 cells from her spawn and through the enemy half (the enemy spawn is (10,7)). 0-3 allies within 6 steps. 22 enemy heads came within 6 steps, 6 episodes within 3 steps. r201-211: tungtung67 #293 (2 long) and #116 (3 long) stay 3 steps from her for 10 rounds; at r203 #293 starts the round next to her head. She steps away one cell every round (N, N, W, N, N, N, W, W, W, N) and they never close. A 2-long has a reach of 1 and the queen moves first in every round, so it can only hit her if she steps next to it or has nowhere to go.
- **tungtung67's only real chances** were four turns of a 12-long (#605, r409-413) that needed 9-12 steps; it did not sprint.
- **Enemy queen.** 3-6 long, near her spawn, with 2-9 allies within 6 steps. Killed r223 at (15,36).
- **The hunter.** Own #255, born r157 as a 2-long, 9 long at r193 and 11 at r208, at (43,5)-(51,16), 27-29 steps from her. From r208 it heads for her with 2-3 free steps a turn through two portals: d29 (r208), 21 (r213), 15 (r215), 9 (r217), 10, 10, 8, 6, 4 (r222), 2 (r223), then `ESSW` (4 steps, 1 segment paid). It ate nothing after r203. She was inside its own view only in the fatal round. Team-mates had her in view at r187-200 and again at r211-223 (1-3 dragons); #255 started closing at r208-213. Sonar rays ended on #255 in almost every round (1-5 a round), none directly from a dragon that had her in view in the previous 3 rounds. On r219-222 a free path within its reach existed (9, 9, 5 and 3 steps) but she was 13-16 cells away in straight-line terms, behind a portal; it kept walking and rammed on the first turn she was in its view.
- **Late game.** The team stays wide (60 units) until r350 and consolidates late: longest 13-21 until r350, 29 at r400. The 31-long leader #641 is rammed at r427 at (7,17) by a tungtung67 2-long in the round that 2-long was born: its parent #662 split next to the leader and the child stepped onto the leader's head.
- **Queen fed late.** 5 (r400), 9 (r420), 19 (r440), 26 (r460), 29 at the end. 28 pearls from own self-kills in rounds 400-449. At r444 she is boxed in by her own coils (segments 2, 16, 14 and 12 around her head) and splits 19 -> 11+8, the cut in front of segment 12. Five own dragons of 15-19 long kill themselves 3-5 cells from her at r446-452, at (1,0), (2,0), (53,4), (2,1), (8,0); she gets 2, 1, 0, 3, 3 of their pearls, other own dragons the rest.
- **Mid-game contact (digest counts).** Own rams on enemy heads: 97 (per 100 rounds 10, 18, 31, 34, 4); the opponent's rams on own heads: 53. Enemy heads that came within 6 steps of the own queen: 22 (left 18, rammed by an own dragon 2, still near when the queen died or the game ended 2).
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 34, 2-long with a 2-3-step move 4, 3-4-long from the next cell 18, 3-4-long with a 2-4-step move 31, 5-9-long 8, 10 or longer 2. Own lengths at r200: 2-long 25, 3-4-long 23, 5-9-long 11, 10-19-long 2.
- **Sonar.** Rays sent per 100 rounds: own 6596, 15063, 15136, 13233, 5896; opponent 6159, 11417, 16327, 14293, 2697. The values are packed and cannot be read.
- Decisive moment: the own queen survived 320 rounds as a 3-long in the enemy half because nothing longer than 3 ever chased her, and the enemy queen was rammed at r223 by an 11-long that walked 29 steps to her. With both queens alive own would still have won 29 against 3-6.

### 3. 1067620 Australia (large), loss to forgot to mention, queen rule (own queen dead, forgot queen 39)

- **Opening (the game is lost here).** 9 dragons each (total 26). There is no natural pearl within 10 cells of either spawn for the first 30 rounds (0-1 on the count), though 44-47 lie on the board. Own total length: 26 (r10), 26 (r20), 28 (r30), 33 (r40), 30 (r50), 28 (r60), 18 (r80). forgot: 28, 29, 32, 43, 51, 69, 122. Natural pearls eaten per 10 rounds from r30: own 13, 8, 5, 6, 6, 6, 7; forgot 12, 17, 21, 25, 29, 35, 33. Own self-kills per 10 rounds from r30: 2, 6, 4, 3, 4, 2, 5, with only 9-12 units alive. Each self-kill of a 2- or 3-long loses one segment even if the pearl is eaten, so own burned about 26 segments in rounds 30-100 while eating 51 natural pearls. Units at r100: 9 vs 62.
- **Queen.** 4-6 long, never splits, no allies. She walks far (19 cells from spawn at r25, 35 at r150). 20 enemy heads came within 6 steps, 7 episodes within 3 steps. She flees with paid steps: r92 `NNW` (6 -> 5 long), r129 `WWS` (5 -> 4); she is 2 long at r160.
- **Allies do ram intruders while there are allies.** r101: own #100 (2 long) rams forgot #40 (3 long) from the next cell, 6 steps from her. r105: own #17 (3 long, 2-step move) rams forgot #58. r119: own #153 (3 long, 2 steps) rams forgot #89. From r125 she has no ally within 6 steps.
- **forgot shadows her.** forgot #175 (2 long) is within 1-3 steps of her from r143 to r160 (next to her head at the start of r144 and r145), #63 (2 long) within 3-5 steps from r143 to r178. Neither rams: after her move they are never next to her head. At least one forgot dragon has her in view in 37 of the 41 rounds from r138 to r178.
- **Her death, r178 at (0,41).** forgot #159 (born r120 as a 2-long) feeds at (7,34)-(7,37) from r158 to r172, 13-17 steps from her, growing 5 -> 9 on natural pearls. r175: one sonar ray from a forgot dragon that had her in view ends on #159. r176: `WSS` (d11). r177: `WWN` (d7), she comes into its view. r178: she steps north from (0,42) to (0,41); #159 sprints 6 steps `NWSSSW` from (2,39) (3 segments paid) and rams her. Her last 10 moves were single steps (N, E, S, W, N, W, N, N, W, N) inside a pocket with 21-26 cells within 4 steps, with forgot #63 3 steps behind her all the time.
- **After that.** 3 own dragons survive to the end in a pocket around (6,24). At r391-392 own #431 (11 long) splits next to forgot's 37-long #370 and its 2-long front part rams the 37-long from the next cell at (23,37); own #451 eats 12 of the pearls.
- **forgot's queen.** 2-3 long until r200, 10 at r400, then fed: a 25-long kills itself at (21,29) at r402 and she eats 11 of its 13 pearls; 26 at r420, 39 at the end. She sits 0-8 cells from her spawn in open water with 0-2 allies. No own dragon was left to look for her.
- **Mid-game contact (digest counts).** Own rams on enemy heads: 16 (per 100 rounds 4, 6, 1, 4, 1); the opponent's rams on own heads: 13. Enemy heads that came within 6 steps of the own queen: 20 (left 15, rammed by an own dragon 1, rammed an own dragon 2, killed itself 2).
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 8, 2-long with a 2-3-step move 0, 3-4-long from the next cell 3, 3-4-long with a 2-4-step move 5, 5-9-long 0, 10 or longer 0. Own lengths at r200: 3-4-long 3.
- **Sonar.** Rays sent per 100 rounds: own 2342, 1342, 625, 959, 911; opponent 3141, 8077, 8909, 9913, 6115. The values are packed and cannot be read.
- Decisive moment: rounds 30-100. Own never got past 12 units; forgot had 62 at r100.

### 4. 1063789 Slithery Fight (large), loss to forgot to mention, queen rule with both queens alive (own 4, forgot 50)

- **Opening.** Both queens start 25 long and coiled: at round 0 the own queen's head has no free neighbour (own segments 6, 4, 2 and 8 on the four sides), so a split is the only legal action. Own round 0: the queen splits 25 -> 3+22 (cut in front of segment 4) and the 22-long child #14 dies in the same round on an order that is not carried out (`SPLIT` then `DIES (noaction)`); it drops 11 pearls, the queen eats 7. Own total goes 47 -> 38 by r10. forgot's queen sheds 2 per round for 11 rounds (25 -> 3) and loses nothing: r10 23 units / 51 total against own 14 / 38. Own catches up by r80 (59 units / 158 against 61 / 149). 102 own self-kills in rounds 0-60.
- **Queen.** 6-8 long until r200, in open water 5-22 cells from spawn. No enemy head within 3 steps of her until round 483. She is fed from r200: 10 (r220), 13 (r260-320), 19 (r340), 25 (r360), 39 (r380), 54 (r400), 68 (r440), 78 (r460), 85 (r483). 9 + 30 + 18 + 7 pearls from own self-kills in the four 50-round blocks from r300.
- **forgot's queen.** 3 long until r200, pacing between (60,1) and (60,3) next to her spawn (59,4) with 1-7 allies within 6 steps; fed from r200: 17 (r260), 28 (r300), 40 (r360-440), 50 at the end. No own dragon came within 6 steps of her at any checkpoint; own had 0 ram chances on her.
- **The moment the game is thrown away, r483-484 at (21,14).** At r483 the 85-long own queen is ahead 85 to 49. Her last moves: r480 `SWSE`, r481 `SS`, r482 `W`, r483 `N`, a tight U-turn (down column 22, one cell west, back north) that puts her head at (21,14) between her own body on the north, east and south and the body of forgot's 23-long #2282, which has just slid in along column 20, on the west. At the start of r484 she has no free neighbouring cell. She splits 85 -> 3+82. The child #2329 (head at the old tail, (9,4)) lives to the end as the 82-long own leader; the queen ends 4 long. forgot wins the queen rule 50 to 4.
- **Why 3.** Checked with `a_box.py`: her neighbours were north own segment 6, east own segment 4, south own segment 2, west the enemy body. The cut is placed just in front of the nearest own segment that touches her head (segment 4), so she keeps 3. The same rule fits all eight forced queen splits I checked (see answer e). forgot's queen in the same situation (game 12, r397-412) sheds 2 from her tail every round instead and loses 32 segments in 16 rounds; here that would have left the own queen at about 53 against 50, if her tail had unwound in time, which the replay cannot show.
- **Leaders.** r470: forgot's 67-long leader #2191 is rammed at (38,16) by own #2138 (8 long, born r438 with 8 segments): d21 at r460, 13 at r465, 12, 6, 4, 3, then a 3-step move. r491: own 19-long #2306 is rammed by a forgot 6-long that came 30 steps in 10 rounds and sprinted 6.
- **Mid-game contact (digest counts).** Own rams on enemy heads: 61 (per 100 rounds 9, 18, 12, 18, 4); the opponent's rams on own heads: 43. Enemy heads that came within 6 steps of the own queen: 6 (left 2, killed itself 1, rammed an own dragon 1, still near when the queen died or the game ended 2).
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 10, 2-long with a 2-3-step move 6, 3-4-long from the next cell 4, 3-4-long with a 2-4-step move 35, 5-9-long 6, 10 or longer 0. Own lengths at r200: 2-long 25, 3-4-long 24, 5-9-long 9, 10-19-long 3.
- **Sonar.** Rays sent per 100 rounds: own 10138, 14587, 14500, 13630, 5816; opponent 10750, 11679, 12005, 13703, 13555. The values are packed and cannot be read.
- Decisive moment: round 484 at (21,14). Without the split own wins the queen rule 85+ to 50.

### 5. 1067623 Slithery Fight (large), loss to forgot to mention, longest 75 vs 83 (own has 59 units and total 364 against 17 units and 187)

- **Opening.** Same round 0 as game 4 (25 -> 3+22, the 22-long dies at once, queen eats 7 of 11 pearls). This time own stays behind: r30 26 units / 76 total vs 43 / 106, r50 33 / 99 vs 62 / 144, r100 46 / 127 vs 61 / 162.
- **Enemy queen.** forgot's queen (4 long) paces a 6-cell loop at her spawn: (62,3), (61,3), (60,3), (60,4), (61,4), (62,4). Killed r150 at (59,4) by own #680, a 10-long born at r140 as a split child with 10 segments. It never eats; it moves 3 free steps every round straight at her: d22 (r142), 19, 17, 15, 13, 13, 9, 7, then `EEESSS` (6 steps, 3 paid). At r149 it could have reached her with a 10-step sprint (7 segments) and took 3 free steps instead. No own dragon had her in view in rounds 120-150 (one did at r117-119). Inference: it went to the place where she had been seen 30 rounds earlier, or to the mirror image of the own spawn; she had not moved away.
- **Own queen.** 7 long until r150, 0-3 allies within 6 steps. forgot #376 (2 long) follows her from r123 to at least r235, more than 110 rounds. She gets away with paid steps and shrinks: r158 `WNE` (7 -> 6), r163 `WNE` (6 -> 5), r168 `NES` (5 -> 4), r173 `SS` (4 -> 3). From r174 she is 3 long in a pocket around (18-19, 0-2) with 13-20 cells within 4 steps and no ally within 6 steps for 60 rounds; #376 starts the round next to her head at r174, 178, 179, 183, 184 and she steps away each time.
- **Her death, r238 at (2,26).** She walks south down column 0 for 10 rounds (r229-238) with forgot #376 5 steps behind and #702 (3 long) 3 steps to the side; the room narrows from 25 to 15 cells. forgot #890 (2 long, born r175) has walked 31 steps towards her in 30 rounds without eating (d31 at r208, 19 at r228, 11 at r232, 5 at r235, 3 at r236-238) and waits at (2,25). At r238 she moves `EE` to (2,26), next to its head; it rams her from the next cell. One to five forgot dragons had her in view in every round from r198 to r238.
- **Late game.** Both queens dead from r238, so the longest dragon decides. No dragon of 15+ was rammed on either side in the whole game. forgot puts 44% of its length into one dragon (61 at r400, 62 at r450, 83 at r500). Own leader: 39 (r350), 65 (r400), 63 (r425), 63 (r450), 65 (r475), 75 at the end, 21% of its length; the second own dragon is 32-37 long and there are 26 reverse splits by own dragons of 20+ in rounds 319-497 (the 65-long leader itself at r401 and r413).
- **Mid-game contact (digest counts).** Own rams on enemy heads: 72 (per 100 rounds 12, 19, 19, 15, 7); the opponent's rams on own heads: 43. Enemy heads that came within 6 steps of the own queen: 10 (rammed by an own dragon 1, left 6, rammed an own dragon 1, killed itself 2).
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 21, 2-long with a 2-3-step move 4, 3-4-long from the next cell 12, 3-4-long with a 2-4-step move 32, 5-9-long 2, 10 or longer 1. Own lengths at r200: 2-long 26, 3-4-long 25, 5-9-long 8, 10-19-long 3.
- **Sonar.** Rays sent per 100 rounds: own 8020, 13139, 14028, 13587, 13649; opponent 11784, 11990, 13250, 13120, 8712. The values are packed and cannot be read.
- Decisive moment: no single event after r238. Own lost a consolidation race it led in total length by 2 to 1; its leader did not grow between r400 and r475.

### 6. 1064500 Around UNSW (large), win over horse, longest 88 vs 82 (both queens dead)

- **Opening.** Same first 13 queen moves as game 1 (same map and side). Queen sheds one 2-long at r19, then stays 6-7 long. Units: r50 38 vs 35, r80 57 vs 45, r100 58 vs 44. horse made no `noaction` self-kill in rounds 0-100 (its dragons die with reason `self`, by running into their own body); own made 27 in rounds 0-60.
- **Enemy queen.** horse's queen is 2 long from r6 and walks north for 9 rounds straight (r74-82) with no ally within 6 steps. Killed r83 at (10,32) by own #199: at r82 own #92 (9 long) splits 9 -> 2+7, and the 7-long child, born with its head at the old tail (8,29), sprints 5 steps `SEESS` the next round (3 segments paid). Own dragons had her in view from r76.
- **Own queen.** Not a single enemy head within 3 steps of her in 333 rounds. She is fed: 10 (r140), 17 (r200), 22 (r220), 26 (r240-320), and travels with 4-step free moves from (59,24) to (28,7) to (15,63). One to three horse dragons have her in view in 21 of the 22 rounds from r312 to r333.
- **Her death, r333 at (5,58).** horse #684 (14 long at r326, 4 steps from her) grows to 24 and splits at r333; the 22-long child #797 has its head at #684's old tail, next to her path, and rams her in the round it is born with a 2-step move. She had just moved `WNE`, looping back past that tail. No enemy head had been within 6 steps of her for the six rounds before: the danger was a tail.
- **Late game.** Both queens dead. Own rams four horse dragons of 15+: #882 (26 long, r388) by a 5-long with a 3-step move that came 20 steps in 4 rounds; the 38-long horse leader #842 at r392 at (2,8) by own #767 (3 long: d9 at r382, 7, 6, 4, 4, 2, then a 2-step move), own dragons eat 17 of its 19 pearls; #865 (16 long, r396) by a 2-long; #981 (17 long, r479) by a 3-long. horse rams own #967 (28 long, r466) with a 5-long that sprints 5.
- **The collector.** Own #325 (born around r150) is the final leader: 15 (r375), 28 (r400), 42 (r425), 66 (r450), 88 at the end. It eats 8 pearls of horse's 38-long, 10 of own #926 (a 20-long that kills itself at r439 next to it) and 8 of own #960 (18 long, r473).
- **Mid-game contact (digest counts).** Own rams on enemy heads: 91 (per 100 rounds 19, 37, 17, 16, 2); the opponent's rams on own heads: 67. Enemy heads that came within 6 steps of the own queen: 10 (rammed by an own dragon 1, rammed an own dragon 1, left 8).
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 32, 2-long with a 2-3-step move 6, 3-4-long from the next cell 4, 3-4-long with a 2-4-step move 40, 5-9-long 9, 10 or longer 0. Own lengths at r200: 2-long 32, 3-4-long 16, 5-9-long 9, 10-19-long 4.
- **Sonar.** Rays sent per 100 rounds: own 9040, 15127, 15826, 14771, 7067; opponent 9658, 16974, 19189, 15057, 7860. The values are packed and cannot be read.
- Decisive moment: round 392 at (2,8), a 3-long takes out horse's 38-long leader; the final margin is 6.

### 7. 1052703 Islands (large), loss to SSS, longest 18 vs 44 (both queens dead; own has 40 units and total 273 against 8 and 82)

- **Opening.** Identical first 29 queen moves to game 2. SSS is faster: r30 12 vs 18 units, r50 21 vs 34, r60 27 vs 43, r100 43 vs 54. SSS made 48 splits of 4 -> 2+2 in rounds 0-60 (own 27) and no `noaction` self-kill.
- **Enemy queen.** Killed r216 at (5,2). Own and SSS dragons fight 3-6 cells from her at r210-214 (three rams). Own #484, a 2-long born r209, walks into that fight from 14 steps away, eats three corpse pearls (r213-215, 2 -> 5 long) and at r216, with her 4 steps away and in its view for the first time, sprints `ESSS` across the wrap edge (2 paid) while she stands still by splitting 4 -> 2+2. No own dragon had her in view in the 40 rounds before. Own #346 (5 long, acting earlier in the same round, 5 steps and 3 paid segments away, she just outside its view) did not go.
- **Own queen.** 7-11 long, no enemy head within 3 steps in the whole game. From r216 own is winning on the queen rule.
- **Her death, r261-263 at (43,36).** She follows pearls north up column 43: natural pearls at (43,38) and (43,37), then at r261 a corpse pearl of own #574 at (43,36). That cell has kelp on its north, west and east edges; the only way out is south, where her own body is. r262: no free neighbour, she splits 16 -> 2+14; the 14-long child #624 leaves. r263: 2 long, still no free neighbour, a 2-long cannot split; she dies (`noaction`). A head inside a one-cell dead end can never come out, so she was lost when she stepped in at r261; at r260 she still had (42,37) free to the west.
- **Late game.** Own leader #873: 31 (r375), 52 (r400), 68 (r425), its head resting at (51,39) next to a portal mouth. SSS #850 (3 long) walks 24 steps in 10 rounds through two portals ((4,39) to (26,38) at r422-423, then (29,38) to (51,39)), eats one pearl and rams the 69-long from the portal at r426. Own dragons eat 20 of the 35 pearls. In the remaining 74 rounds own does not rebuild: longest 12 (r450), 15 (r475), 18 at the end, with 40 units alive.
- **Mid-game contact (digest counts).** Own rams on enemy heads: 135 (per 100 rounds 14, 37, 39, 36, 9); the opponent's rams on own heads: 86. Enemy heads that came within 6 steps of the own queen: 3 (rammed an own dragon 1, left 2).
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 42, 2-long with a 2-3-step move 13, 3-4-long from the next cell 12, 3-4-long with a 2-4-step move 60, 5-9-long 7, 10 or longer 1. Own lengths at r200: 2-long 31, 3-4-long 22, 5-9-long 6, 10-19-long 2.
- **Sonar.** Rays sent per 100 rounds: own 5494, 13789, 14674, 13589, 10409; opponent 1242, 18507, 22193, 20391, 5149. The values are packed and cannot be read.
- Decisive moment: two. r261 (the queen enters a dead end; alive she wins the queen rule) and r426 (the 69-long is rammed out of a portal; SSS's longest ends 44).

### 8. 1056036 Australia (large), win over SSS, longest 81 vs 24 (both queens dead)

- **Opening.** Same spawn and the same slow start as game 3: total length 26, 26, 24, 29, 29, 26 at r10-60 (SSS 27, 32, 36, 38, 45, 45), 7 self-kills in rounds 40-49 with 11 units alive. It recovers from r70 (natural pearls eaten per 10 rounds 16, 23, 14) because SSS grows more slowly than forgot did: r100 27 units vs 32.
- **Own queen.** 4 long, walks north alone (0-1 allies). SSS #4 (3 long, a starting dragon) has her in view from r40 and stays exactly 5 steps away from r45 to r54, moving parallel to her. A second SSS 3-long (#16) is also 5 steps away. At r55 she steps west, towards #4; it moves `ES` (1 paid step) from (28,35) and rams her at (29,36).
- **Mid-game.** Own dragons of 8-11 long are within sprint range of SSS's 2-long queen on 14 turns in rounds 280-316 (6-11 steps, 3-8 segments to pay) and do not go; on every one of those turns she is 4 or more cells away in each direction, outside their view.
- **Enemy queen.** 2-4 long until r420, 9 at r460, with 3-6 allies within 6 steps. Killed r472 at (40,15) by own #781, a 10-long born at r464 as a split child. It has her in view from r467 and circles for five rounds at 5-8 steps (7 more turns with a path of 6-11 steps not taken); at r472 she moves `ES` to within 4 steps and it sprints `NNNW` (1 paid).
- **Leader kill, r478-479 at (16,32).** SSS's 57-long #789 comes north up column 17. Own #507 (14 long) splits 14 -> 2+12 at r478; the child #791 has its head at the old tail (15,36), moves `NNN` in the round it is born and `NE` at r479 into the leader's head. Own dragons eat all 29 pearls (#768 13, #674 10, #608 5, #745 1).
- **Numbers.** r450: own longest 58, SSS 61 and SSS queen 7. r475: own 75, SSS 59.
- **Mid-game contact (digest counts).** Own rams on enemy heads: 97 (per 100 rounds 3, 19, 26, 27, 22); the opponent's rams on own heads: 83. Enemy heads that came within 6 steps of the own queen: 4 (left 1, rammed an own dragon 2, rammed by an own dragon 1).
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 14, 2-long with a 2-3-step move 4, 3-4-long from the next cell 13, 3-4-long with a 2-4-step move 58, 5-9-long 5, 10 or longer 3. Own lengths at r200: 2-long 35, 3-4-long 21.
- **Sonar.** Rays sent per 100 rounds: own 3661, 11536, 16292, 15515, 13224; opponent 912, 17718, 24037, 22129, 11307. The values are packed and cannot be read.
- Decisive moment: round 472. Until then SSS was winning on the queen rule; after it own led on longest 75 to 59. The leader kill at r479 widened the margin to 81 vs 24 but was not needed for the win.

### 9. 1067619 Maze (medium), loss to forgot to mention, longest 68 vs 73 (both queens dead; own 30 units and total 176, forgot one single 73-long dragon)

- **Opening.** 2 dragons each (total 8). Both queens are the "mother": eat to 4, split 4 -> 2+2, repeat (own at r0, 5, 10, 18, 26, 44, 72, 90, 111). Own is ahead: r50 23 vs 19 units, r100 40 vs 30, r150 54 units / 177 total vs 37 / 87.
- **Enemy queen.** forgot's 2-long queen dies at r127 at (36,10) by the suicide action, with no own dragon near. She too had no free neighbour: kelp east and south, her own second segment west, the tail of a forgot 2-long (#7) north. Own never came within reach of her. From r127 own is winning on the queen rule.
- **Own queen.** 2-3 long until r140 with 3-12 allies within 6 steps, 7 long from r160, fed to 13 (r320) and 18 (r340). No enemy head within 3 steps of her in the whole game.
- **Forced split, r345 at (27,1).** She enters a 2x2 room (cells (27,0), (28,0), (27,1), (28,1), kelp around it except sideways along row 0) as an 18-long and fills it with her own body. No free neighbour: she splits 18 -> 3+15. From r346 she walks round the 2x2 block as a 3-long (W, N, E, S, ...) for 20 rounds; that is how she stands still.
- **Her death, r366.** Own #865 (14 long) comes east along row 0 collecting pearls: (25,0), (26,0), then (27,0), the cell the queen needs next. She has no free neighbour, a 3-long cannot split, she dies (`noaction`). #865 eats her pearl.
- **Late game.** No dragon of 15+ was rammed on either side after r188. forgot: longest 38 (r400), 59 (r450), 73 (r500). Own: 15 (r350), 15 (r400), 12 (r425), 36 (r450), 60 (r475), 68. Own started to build a leader about 50 rounds after forgot did, and only after its queen had died.
- **Mid-game contact (digest counts).** Own rams on enemy heads: 35 (per 100 rounds 1, 7, 10, 14, 3); the opponent's rams on own heads: 23. Enemy heads that came within 6 steps of the own queen: 0.
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 14, 2-long with a 2-3-step move 1, 3-4-long from the next cell 6, 3-4-long with a 2-4-step move 12, 5-9-long 2, 10 or longer 0. Own lengths at r200: 2-long 26, 3-4-long 19, 5-9-long 9, 10-19-long 3.
- **Sonar.** Rays sent per 100 rounds: own 5199, 11552, 12108, 11825, 7023; opponent 1667, 3319, 3738, 4849, 1493. The values are packed and cannot be read.
- Decisive moment: round 366 at (27,1), an own 14-long drives into the queen's 2x2 room. With the queen alive own wins the queen rule 3 to 0.

### 10. 1063792 Trauma (medium), loss to forgot to mention, queen rule with both queens alive (own 35, forgot 48)

- **Opening.** 2 dragons each (total 8). Own stays at 4 units and total 9-10 from r10 to r50, 5 units at r60, 6 at r80, 14 at r100; forgot 7 units at r50, 16 at r80, 25 at r100. Natural pearls eaten per 10 rounds from r30: own 1, 1, 1, 2, 4, 11, 12; forgot 2, 7, 8, 9, 11, 10, 18. There were 7-13 natural pearls within 10 cells of the own spawn in those rounds and 33-47 on the board; own's four dragons did not find them.
- **Queens.** Neither queen ever had an enemy head within 3 steps; neither side had a single ram chance on the other queen. First ram of the game at r158. The game is a race to feed the queen.
- **Own queen.** Mother splits (4 -> 2+2) at r0, 50, 92, 138, 149. From r160 she sits around (45,1), 4 long. Fed in two bursts: 13 own self-kill pearls in rounds 250-299 (4 -> 18 at r300), nothing for 100 rounds (18-19 from r300 to r400), then 12 in rounds 400-499 (35 at the end).
- **forgot's queen.** 2 long until r200 near her spawn with 4-7 allies; fed steadily from r200: 14, 4, 3, 9, 9, 7 pearls per 50 rounds: 15 (r240), 20 (r300), 32 (r400), 48 at the end.
- **Late game.** No dragon of 15+ other than the two queens, no ram on either queen; each queen is her team's longest dragon (own 35 of a total 85, forgot 48 of 104).
- **Mid-game contact (digest counts).** Own rams on enemy heads: 22 (per 100 rounds 0, 3, 10, 6, 3); the opponent's rams on own heads: 10. Enemy heads that came within 6 steps of the own queen: 0.
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 2, 2-long with a 2-3-step move 3, 3-4-long from the next cell 2, 3-4-long with a 2-4-step move 14, 5-9-long 1, 10 or longer 0. Own lengths at r200: 2-long 30, 3-4-long 16.
- **Sonar.** Rays sent per 100 rounds: own 1108, 5790, 6997, 7482, 3708; opponent 1119, 3196, 4010, 4629, 4369. The values are packed and cannot be read.
- Decisive moment: none in one round. Slow opening (14 units vs 25 at r100) and a 100-round pause in feeding the queen (r300-400) while forgot's queen went from 20 to 32.

### 11. 1064508 Trauma (medium), win over horse, queen rule with both queens alive (own 32, horse 23)

- **Opening.** Same spawn and the same first 18 queen moves as game 10, but here the dragons find pearls: 7 units at r30, 12 at r50, 26 at r100 (horse 4, 5, 11). horse makes 3 splits in the first 60 rounds.
- **Own queen.** 2 long until r150, pacing at (46,0); 4-5 long from r180 to r400; no enemy head within 3 steps in the whole game. Fed only in the last 95 rounds: 16 own self-kill pearls in rounds 400-449 and 10 in 450-499: 11 (r420), 16 (r440), 24 (r460), 32 at the end.
- **horse's queen.** 8 long from r200 to r350, 11 at r400, 23 at the end. Own had no ram chance on her.
- **Late game.** As in game 10: the queens are the longest dragons (own 32 of a total 75, horse 23 of 83), nothing else reaches 15, and no own reverse split occurs.
- **Mid-game contact (digest counts).** Own rams on enemy heads: 27 (per 100 rounds 0, 5, 7, 11, 4); the opponent's rams on own heads: 9. Enemy heads that came within 6 steps of the own queen: 0.
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 8, 2-long with a 2-3-step move 3, 3-4-long from the next cell 4, 3-4-long with a 2-4-step move 12, 5-9-long 0, 10 or longer 0. Own lengths at r200: 2-long 25, 3-4-long 11.
- **Sonar.** Rays sent per 100 rounds: own 2526, 6655, 7041, 7581, 4927; opponent 1574, 4382, 10193, 6510, 4007. The values are packed and cannot be read.
- Decisive moment: the opening (26 units vs 11 at r100) and the feeding of the queen from about r405; no contact near either queen.

### 12. 1063783 Portals (small), loss to forgot to mention, queen rule (own queen dead; own ends as one 65-long dragon, forgot has a 31-long and a 29-long queen)

- **Opening.** 3 dragons each (total 9). 98 natural pearls lie on the board from r10. Own splits later than usual (12 of its 16 splits in rounds 0-60 are made at length 5, not 4) and eats 5-6 natural pearls per 10 rounds; forgot makes 40 splits and eats 12-19. Units: r40 8 vs 12, r60 10 vs 18, r100 15 vs 35.
- **Own queen.** 3 long, pacing at (13,4) from r40 to r100 with 3-5 allies within 6 steps. At r121 she reaches 4 and splits 4 -> 2+2.
- **Her death, r131 at (10,5).** No enemy near. Her head has kelp to the west, her own second segment to the north, the tail of own #165 (2 long) to the south (it had just moved east) and the tail of own #169 (5 long) to the east. A 2-long cannot split; she dies (`noaction`). An own 3-long eats her pearl in the same round.
- **forgot's queen.** 3-4 long at column 31 next to her spawn until r220 with 3-9 allies; fed from r200 to 48 (r360). At r397 at (16,4), 42 long, she is boxed in by her own coils in a 2-wide corridor. She splits off 2 from her tail every round for 16 rounds (42 -> 40 -> ... -> 10) and then walks out; she ends 29 long. Own had 3 units at r400 and 1 at r450: nothing small was left that could have rammed a queen standing still for 16 rounds.
- **Late game.** Own leader: 29 (r300), 41 (r325), 52 (r375), 60 (r450), 65; eight reverse splits of the 43-60-long leader in rounds 328-403.
- **Mid-game contact (digest counts).** Own rams on enemy heads: 0 (per 100 rounds 0, 0, 0, 0, 0); the opponent's rams on own heads: 0. Enemy heads that came within 6 steps of the own queen: 0.
- **Roles (digest counts).** No own ram on an enemy head in this game.
- **Sonar.** Rays sent per 100 rounds: own 1912, 5724, 5775, 2234, 382; opponent 3684, 8028, 6901, 3696, 1802. The values are packed and cannot be read.
- Decisive moment: round 131. Own later had the longer dragon (65 vs 31) but no queen.

### 13. 1063793 Tower Defense (small), loss to forgot to mention, wiped out at round 188

- **Opening.** 2 dragons of length 2 each. Own has 2 units until r40 and 3 units from r40 to r80; forgot has 8 at r60, 16 at r80. Natural pearls eaten per 10 rounds from r40: own 2, 0, 0, 1, 14; forgot 2, 10, 9, 19, 8, with 19-22 natural pearls within 10 cells of each spawn. The own queen needs 35 rounds to reach length 4 (first split r35).
- **Own queen.** 2-3 long, no ally within 6 steps for almost the whole game. r114-115: forgot #16 (2 long) is 2 steps away twice; she steps away.
- **Her death, r147 at (1,6).** She splits 4 -> 2+2 at r140 and walks south down column 1, a corridor one cell wide (9-10 cells within 4 steps). forgot #53 (2 long, born r107) had her in view from r117 to r134 across kelp, walks round (35 steps away at r127, 19 at r137, then 14, 12, 10, 8, 6, 4, 2), enters the corridor from the other end and comes north. At r147 she steps to (1,6), next to its head at (1,7), and is rammed. A 2-long cannot turn round in a one-cell corridor.
- **Late game.** None: own has 6 units at r100 and is wiped out at r188.
- **Mid-game contact (digest counts).** Own rams on enemy heads: 7 (per 100 rounds 2, 5, 0, 0, 0); the opponent's rams on own heads: 9. Enemy heads that came within 6 steps of the own queen: 2 (left 1, rammed an own dragon 1).
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 2, 2-long with a 2-3-step move 1, 3-4-long from the next cell 2, 3-4-long with a 2-4-step move 2, 5-9-long 0, 10 or longer 0.
- **Sonar.** Rays sent per 100 rounds: own 636, 762, 0, 0, 0; opponent 1452, 3060, 0, 0, 0. The values are packed and cannot be read.
- Decisive moment: rounds 40-80, three units against sixteen.

### 14. 1063784 Devil (small), win over forgot to mention, wipe-out at round 171 (both queens dead by r37)

- **Opening.** 3 dragons of length 4 each; all split at once. Own makes 10 rams in rounds 0-60 (forgot 2) and 38 splits (forgot 13). Units: r30 10 vs 7, r50 17 vs 6, r100 34 vs 4.
- **Enemy queen.** forgot's 3-long queen walks north up column 13 for four rounds (r33-36) towards own #5 (3 long, a starting dragon that had had her in view since r17 while eating seven natural pearls 4-7 steps away). At r36 she steps next to its head at (13,5) and it rams her from the next cell. In the same rounds own #8 (4 long, 2-step move, r31) and own #25 (2 long, next cell, r36) ram two more forgot dragons.
- **Own queen.** Mother splits at r8, 23, 31, 36. She walks round a 2-wide pocket at (15-16, 0-1) with kelp on three sides. r36: she splits 4 -> 2+2; the child #29 moves one cell south and its tail still lies on (16,1), her only exit. r37: no free neighbour, a 2-long cannot split, she dies (`noaction`). One round of waiting would have saved her.
- **Late game.** None: with both queens dead own hunts the rest down (forgot 4 units at r100, 1 at r150, none at r171) while growing to 52 units.
- **Mid-game contact (digest counts).** Own rams on enemy heads: 19 (per 100 rounds 14, 5, 0, 0, 0); the opponent's rams on own heads: 4. Enemy heads that came within 6 steps of the own queen: 4 (rammed by an own dragon 3, left 1).
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 8, 2-long with a 2-3-step move 2, 3-4-long from the next cell 3, 3-4-long with a 2-4-step move 6, 5-9-long 0, 10 or longer 0.
- **Sonar.** Rays sent per 100 rounds: own 3297, 6244, 0, 0, 0; opponent 1200, 332, 0, 0, 0. The values are packed and cannot be read.
- Decisive moment: rounds 31-36, three rams and the queen kill; forgot never had more than 7 units.

### 15. 1064507 Devil (small), loss to horse, wiped out at round 253 (read for the opening only)

- **Opening.** Same map as game 14. Own queen walks east to the middle. horse #13 (born r11 as a 2-long) comes from 11 steps away, eating and splitting on the way (4 -> 2+2 at r21), and at r24 sprints 4 steps `NWNN` from (16,9) into her at (15,6); she had split 4 -> 2+2 at r21 and was 3 long with no ally within 6 steps.
- Natural pearls eaten per 10 rounds from r20: own 12, 7, 8, 9; horse 13, 15, 18, 18. horse made no `noaction` self-kill. Units: r40 10 vs 16, r60 10 vs 20, r100 14 vs 34.
- **Mid-game contact (digest counts).** Own rams on enemy heads: 33 (per 100 rounds 11, 19, 3, 0, 0); the opponent's rams on own heads: 21. Enemy heads that came within 6 steps of the own queen: 4 (rammed an own dragon 3, died self 1).
- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell 20, 2-long with a 2-3-step move 3, 3-4-long from the next cell 2, 3-4-long with a 2-4-step move 8, 5-9-long 0, 10 or longer 0. Own lengths at r200: 2-long 2, 3-4-long 2.
- **Sonar.** Rays sent per 100 rounds: own 2126, 2173, 150, 0, 0; opponent 5091, 13845, 9792, 0, 0. The values are packed and cannot be read.
- Decisive moment: rounds 20-60; the queen dies at r24 and own eats half as many natural pearls as horse from r30.

## Answers to the eight questions

### a. How does a hunter get to the enemy queen?

Seven enemy queens were rammed by Vibing++ in the 15 games (games 1, 2, 5, 6, 7, 8, 14).

| game, round | killer | 20 / 10 / 5 rounds before | ate on the way | in its own view | last move |
|---|---|---|---|---|---|
| 1063780 r34 | #44, 5 long, born r20 as a 2-long | not born / 12 steps / 5 steps | 7 natural pearls, split twice | from r29 (5 rounds) | 5 steps, 3 paid |
| 1069168 r223 | #255, 11 long, born r157 | 27 / 21 / 10 steps, through two portals | nothing after r203 | only in the fatal round | 4 steps, 1 paid |
| 1067623 r150 | #680, 10 long, split child born r140 | not born / 22 at r142 / 17 steps | nothing | only at its turn in the fatal round | 6 steps, 3 paid |
| 1064500 r83 | #199, 7 long, split child born r82 | not born | nothing | only in the fatal round | 5 steps, 3 paid |
| 1052703 r216 | #484, 5 long, born r209 as a 2-long | not born / not born / 14 steps | 3 corpse pearls of a fight beside her | only in the fatal round | 4 steps, 2 paid |
| 1056036 r472 | #781, 10 long, split child born r464 | not born / 9 at r466 / 6 steps | nothing | from r467 (5 rounds) | 4 steps, 1 paid |
| 1063784 r36 | #5, 3 long, a starting dragon | 4-7 steps for 19 rounds | 7 natural pearls | from r17 | next cell |

- **Length.** 5 or longer in 6 of 7. The sprint was 4-6 steps in 6 of 7 and cost 1-3 segments.
- **From far or near.** Came from 14 or more steps away in 3 of 7 (29, 22 and 14 steps). Was already feeding within 7 steps in 2 of 7 (games 1 and 14). Was born 6-10 steps from her as a split child in 2 of 7 (games 6 and 8).
- **Grew first?** In 2 of 7 (games 1 and 7) a 2-long grew to 5 on the pearls it met and struck in the round it became long enough. In 4 of 7 the hunter was already 7-11 long and ate nothing on the approach.
- **Seen before?** The killer itself had her in view before the fatal round in 3 of 7. Team-mates had her in view within the 10 rounds before in 4 of 7 (games 1, 2, 6, 14). In 1067623 nobody on the team had her in view for 30 rounds and in 1052703 for 40 rounds, yet the hunter walked 22 and 14 steps straight to her; in both she was within 8 cells of her own spawn.
- **Designated hunter or anyone?** Both. Three of seven killers were fresh split children of 7-10 segments that never ate and went straight for her (games 5, 6, 8): that looks like a dispatched hunter (inference). Three were ordinary foragers that took the chance (games 1, 7, 14). One was an 11-long that stopped eating and walked 29 steps (game 2).
- **Two more kills, from games checked only for this question and for c.** 1062216 (Around UNSW, r156): own #149, 10 long, 30 steps away at r146, moves 3 steps a round (23, 20, 18, 17, 14, 10, 6 steps left), then sprints 5 (2 paid); it never had her in view before its last turn, and one team-mate had her in view at r135-138. 1065203 (Australia, r296): own #243, 11-12 long, 34 steps away at r266 and 15 at r286, stays 9-11 steps away for seven rounds, then sprints 4 (1 paid) when she is in its view. Both queens were pacing within 10 cells of their own spawn. With these two, 5 of 9 killers were 10-12 long, and 4 of 9 walked more than 20 steps to a queen that was within 15 cells of her own spawn.
- For comparison, the six rams on the own queen: forgot used a 9-long with a 6-step sprint once (1067620) and 2-longs that she stepped next to twice (1067623, 1063793), each time after forgot dragons had had her in view in at least 34 of the 41 rounds before; horse used a split child born next to her (1064500) and a 4-long with a 4-step sprint (1064507); SSS used a 3-long that stayed 5 steps away for 10 rounds (1056036).

### b. Do they always ram when they can?

Yes, when she is inside the attacker's own view. In the 15 games `q3` lists 34 turns on which an own dragon of at most 12 long had a free path to the enemy queen's head within its reach: 7 taken, 27 not.

- **All 27 not-taken turns had her outside the attacker's 7x7 square at its turn** (4 to 31 cells away in a straight line; in one, 1056036 r467, she was 3 cells away at the start of the round and moved to 5 before the attacker's turn). All 7 taken turns had her inside it.
- All 27 were by dragons 5-11 long. 26 of them would have cost 2-8 segments (paths of 5-11 steps). The exception is 1069168 r222: 3 steps, free, but through a portal with her 13 cells away in straight-line terms; the 11-long walked one step and rammed the next round when she was in view.
- Examples. 1056036 r308 and r315: own #508 (10 long) needs 6 steps (3 paid), she is 4-5 cells away, own queen dead; it moves 3 free steps sideways. 1056036 r465-471: the eventual killer #781 passes seven turns with paths of 6-11 steps. 1067623 r149: #680 needs 10 steps (7 paid), she is 7 cells away; it takes 3 free steps and kills next round with 6. 1052703 r216: own #346 (5 long) needs 5 steps (3 paid), she is 4 cells away; it moves 1 step; another own dragon kills her in the same round.
- The two extra games add 4 missed turns (1062216 r155; 1065203 r287, r288, r295), all by a 10-11-long with her 4-8 cells away and 5-7 segments to pay.
- No turn was found on which a 2-3-long own dragon had such a path and did not ram. None of the 27 involved the team's longest dragon except 1056036 r283 and 1067623 r149.

### c. Why do some queens live on open big maps?

Read closely: 1063780 and 1069168. Checked with the pack script only: 1062216 and 1065203.

- **1063780.** Three things together. The enemy queen died at r34. From r80 to r216 the own queen was 12-13 long, which gives 3-4 free steps a turn; she walked away from 2-3-long intruders on all 7 occasions one came within 3 steps. From r216 she was 3 long and stayed 14-23 cells from her spawn behind 60 own units; no enemy head was within 8 steps at any 20-round checkpoint from r200 to r400. forgot never had one turn with a path to her within reach.
- **1069168.** She was 3 long for 320 rounds and roamed up to 44 cells from her spawn, through the enemy half, with 0-3 allies near. tungtung67's 2-3-long dragons came within 3 steps in 6 episodes (once for 10 rounds in a row) and never closed. Its only real chances were four turns of a 12-long that needed 9-12 steps.
- **1062216** (Around UNSW, win over Team SKKU, queen 50 at the end). She never splits, is 10-13 long from r100 to r280 within about 10 cells of her spawn, and no enemy head comes within 3 steps of her in 500 rounds. The opponent had 3 turns with a path within reach and took none. Fed from r350 (21 pearls in 50 rounds, 20 -> 44).
- **1065203** (Australia, win over a team listed as "Settlers of", queen 48). 11 long from r140 to r340 at (18-22, 22-29), within 10 cells of her spawn, with 1-3 allies. Five episodes (8 rounds) with a 2-3-long within 3 steps; in 5 of the 8 rounds she moves 3 free steps away. The opponent had no chance at all. Fed from r350.
- **What is different from the games where she died.** Not her position or her escort. In all four games nothing of length 4-11 with a sprint ever arrived while she was in its view. A 2-long has a reach of 1 and the queen moves first in every round, so 2-longs alone cannot catch a queen that keeps stepping away in open water. The four large-map deaths needed something else: a 9-long sprinter (1067620), a split child born beside her (1064500), a 3-long that waited 5 steps away until she stepped towards it (1056036), or a narrowing corridor with a second small dragon at its end (1067623).

### d. What does the queen do in the round an enemy gets close?

- **She moves. Nothing else was seen.** Recounted with `a_check.py`: 34 episodes, 151 rounds in all, in which an enemy head started the round within 3 steps of the own queen (per game 7, 6, 7, 2, 7, 0, 0, 1, 0, 0, 0, 0, 2, 1, 1). In all 151 rounds her order was a move: one step in 124, two or three steps in 27. In the episodes printed round by round the move led away from the nearest intruder, with three exceptions that were all fatal: 1056036 r55 (she stepped towards the stalker), 1067623 r238 (two steps east, ending beside a second hunter) and 1063793 r147 (forward in a one-cell corridor, next to the head coming the other way). She never split in such a round (the split at 1063789 r484 came with the enemy head 4 steps away and no free cell) and she never attacked. Two ordinary shed-2 splits were made with an enemy head 4 steps away (1069168 r30, 1064507 r21).
- **She pays segments to get away.** 1067620: r92 `NNW` (6 -> 5), r129 `WWS` (5 -> 4), 2 long by r160. 1067623: r158 `WNE`, r163 `WNE`, r168 `NES`, r173 `SS`, 7 -> 3 in 16 rounds. A 3-long queen has no spare step left, and both queens died after that.
- **Allies.** She had no own head within 6 steps in 128 of the 151 rounds, one in 14 and two or more in 9. In 32 of the 34 episodes no ally did anything about the intruder. Allies rammed an enemy near her in two: 1069168 r52 (a 3-long from the next cell, 3 steps from her) and 1067620 r101-119 (three rams by 2-3-long dragons 6 steps from her, when 2-5 allies were near). No ally was seen moving between her and an intruder. On the wider digest count (enemy heads within 6 steps of her), 10 of 101 intruders in the 15 games were rammed by an own dragon (3 of them in 1063784, 2 in 1069168).
- **Outcome.** 5 of the 34 episodes ended with her rammed (1067620 r178, 1067623 r238, 1056036 r55, 1063793 r147, 1064507 r24); in the others the intruder left or was outrun. The sixth ram on an own queen (1064500 r333) came from a tail that became a head, with no enemy head within 6 steps beforehand.

### e. How do queens avoid killing themselves?

Checked with `a_box.py` on every split order of the own queen in the 15 games (47 orders; output in `a_out/box_all.txt`) plus the deaths in 1067617 and 1067612.

- **Rule 1: no free neighbour and at least 4 long -> split.** 14 of the 47 orders were given with no free neighbouring cell: 10 were carried out and 4 were the fatal orders of a queen too short to split. In the 8 where it can be tested, the cut is placed just in front of the nearest own segment that touches her head: segment 4 touching -> she keeps 3 (1063780 r216 and r449, 1063789 r0 and r484, 1067623 r0, 1067619 r345, 1069168 r77); segment 12 touching -> she keeps 11 (1069168 r444, 19 -> 11+8). The other two: 1052703 r262 (kelp on three sides, 16 -> 2+14) and 1063784 r36 (a 4-long can only split 2+2).
- **Rule 2: as a 2-3-long she walks round a 2x2 block to stay in place** (1067619 r346-366, 1063784 r32-35; forgot's queen paces a 6-cell loop at her spawn in 1067623).
- **It still fails.** 6 of 6 `noaction` deaths of the own queen had no free neighbour and a queen of 2-3 long who therefore could not split (in the four games read closely there was also no enemy head within 6 steps): 1052703 r263 (one-cell dead end), 1067619 r366 (own 14-long's head in her 2x2 room), 1063783 r131 (kelp and two own tails), 1063784 r37 (her own newborn child's tail), 1067617 r132 (body of an own 8-long on two sides), 1067612 r31 (the tail of an enemy 2-long in a dead end). The blocking body belonged to her own team in 4 of 6. In at least 5 of 6 she had made herself 2-3 long by a split 1-21 rounds earlier (1067617 not checked for that).
- **The other 33 queen splits were voluntary** "shed 2" splits with 1-3 free neighbours (4 -> 2+2 on small-start maps, 8 -> 6+2 or 9 -> 7+2 on Islands, Around UNSW and Slithery Fight in the first 60 rounds).
- **Slithery Fight start (25 long).** The queen starts coiled with no free neighbour. Vibing++ cuts in front of segment 4 (25 -> 3+22); the 22-long child then dies in the same round on an order that is not carried out and drops 11 pearls, of which the queen eats 7. forgot sheds 2 from the tail per round for 11 rounds and loses nothing: 23 units and total 51 at r10 against 14 and 38 (both games).
- **It happens to forgot as well.** forgot's 2-long queen died the same way in 1067619 at r127 (kelp on two sides, an allied tail on the third).
- **What forgot does when its long queen is boxed in.** 1063783 r397-412: it splits 2 off the tail every round for 16 rounds (42 -> 10) and keeps the queen as long as it can. Vibing++'s rule would have cut her to 3 at once.

### f. When is the queen fed, and when is she thrown away?

- **Fed in 7 of 15 games** (1, 2, 4, 6, 9, 10, 11). In all seven no enemy head had been within 3 steps of her for at least 45 rounds when the feeding began; in four of them (6, 9, 10, 11) never in the whole game, and in game 4 not until r483. The enemy queen was dead in four (1, 2, 6, 9) and alive in three (4, 10, 11).
- **When.** Late in four: from r375 (1063780), r400 (1069168), r405 (1064508), and the second burst of 1063792 (r400). Earlier in three: r140-240 (1064500, to 26), r200 onwards (1063789, to 85), r250-299 (1063792).
- **How.** Small own dragons kill themselves next to her; at the end, dragons of 15-22 long do it too (1063780 r453 and r460; five dragons of 15-19 in 1069168 r446-452). She gets about a third to two thirds of each big corpse; other own dragons eat the rest.
- **Not fed** when she was being followed (1067620, 1067623) or died early.
- **Thrown away: not seen as a decision.** Each time a long queen was cut down (85 -> 3, 18 -> 3, 16 -> 2, 13 -> 3, 9 -> 3 twice, 19 -> 11, and 25 -> 3 at the start of both Slithery Fight games) she had no free neighbour (answer e). What decides it is geometry: she makes a tight turn so that her own 4th segment touches her head, or enters a dead end, often while collecting pearls (1052703 r261: a corpse pearl in a one-cell dead end; 1063789 r480-483: `SWSE`, `SS`, `W`, `N` among her own coils).

### g. The leader in the last 100 rounds

- **How own dragons of 15+ were rammed after round 300 (8 cases, the queen not counted).** By a 2-4-long from the next cell in 4: 1052703 r426 (69 long, a 3-4-long that came 24 steps in 10 rounds and out of a portal beside the leader's head), 1069168 r427 (31 long, a 2-long born that round by a split next to it), 1064500 r341 (16 long, a 3-long, also through a portal), 1063780 r414 (17 long). By a 3-long with a 2-step move in 1: 1052703 r306 (23 long). By a 5-6-long sprinting 3-6 steps in 3: 1064500 r466 (28 long, approach of 13 steps in 5 rounds), 1063789 r491 (19 long, 30 steps in 10 rounds), 1069168 r400 (18 long).
- **How own dragons killed enemy leaders of 15+ after round 300 (10 cases).** Attackers 2-12 long. 1063789 r470: an 8-long walks 21 steps in 10 rounds and rams the 67-long. 1064500 r392: a 3-long, 9 steps in 10 rounds, rams the 38-long; also r388, r396, r479. 1056036 r479: a 12-long split child rams the 57-long. 1067620 r392, 1069168 r414 and r445: see the split trick below. 1069168 r413: a 5-long, 4-step sprint, 22-long victim.
- **The split trick (4 of the 10).** A long own dragon near an enemy leader splits first, then rams with the cheap part. Either the child, whose head is the old tail, rams within one round (1056036 r478-479: 14 -> 2+12; 1069168 r414: a 6-long child rams in the round it is born), or the 2-long front part rams and the rest walks away (1067620 r391-392: 11 -> 2+9, then the 2-long rams a 37-long; 1069168 r441-445: 23 -> 2+21, then the front part rams a 24-long). horse did the same to the own queen (1064500 r333).
- **How the leader is kept alive.** No escort was seen. What is seen is reverse splits: 19 by own dragons of 20+ in 1063780 (r303-496), 26 in 1067623, 8 by the 43-60-long leader in 1063783. After each one the leader's head is at the old tail, up to its own length away, and the leader is 2 shorter. Whether that is meant as protection or is only a way to turn round cannot be told from the replay.
- **Results of the five games decided by the longest dragon.** The side that killed a 35+ leader after r390 won all three in which that happened (1064500, 1056036 for own; 1052703 against own). The two without any leader kill were lost by 5 and 8 segments (1067619, 1067623) because own had less of its length in one dragon: 39% and 21% against 100% and 44%.

### h. Openings lost

- **Units at round 50-100.** Behind by 1.5 times or more in 7 of 9 losses: 1067620 (9 vs 62 at r100), 1067623 (33 vs 62 at r50), 1052703 (21 vs 34 at r50), 1063792 (14 vs 25 at r100), 1063783 (15 vs 35 at r100), 1063793 (3 vs 16 at r80), 1064507 (10 vs 20 at r60). Not behind: 1063789, 1067619. Of the 6 wins one was behind like that (1056036, 11 vs 19 at r50) and had caught up by r100.
- **Same map, win against loss.**
  - Australia (same spawn): the first 60 rounds are equally bad in both (total length 24-33; at most one natural pearl within 10 cells of the spawn; 2-7 self-kills per 10 rounds from r30 with 9-12 units). The win was against SSS, which had 20 units at r60; the loss against forgot, which had 29 and then 62 at r100.
  - Trauma (same spawn, same first 18 queen moves): in the win own has 7 units at r30; in the loss it eats one natural pearl per 10 rounds until r70 and has 4 units until r50.
  - Devil: in the win own makes 10 rams in 60 rounds and kills the queen at r36; in the loss it loses its queen at r24 and eats half as many natural pearls as horse.
  - Islands (identical first 29 queen moves): 24 units at r50 against tungtung67's 20, 21 against SSS's 34.
- **What goes wrong.** Low natural-pearl intake per unit in every loss where it was counted: 5-8 per 10 rounds against forgot's 17-35 (1067620), 1-2 against 7-9 (1063792), 5-6 against 12-19 (1063783), 0-2 against 9-19 (1063793), 7-9 against 15-18 (1064507). On top of that: self-kills that continue while intake is low (Australia), and the 11 segments lost at round 0 on Slithery Fight.

## Recurring patterns

Counts are over the 15 games. "DOES" = something Vibing++ does; "HAPPENS" = something that happens to it.

### Seen in wins and losses alike

1. **DOES: grows by splitting at length 4 into 2+2.** 15 of 15 games; 46 of 62 own splits in rounds 0-60 in 1063780, 97 of 152 in 1063789. Exception inside one game: on Portals 12 of 16 early splits were made at length 5.
2. **DOES: small dragons kill themselves from the first rounds on, by ordering a split they cannot make.** 15 of 15 (21 in rounds 0-60 in 1063780, 102 in 1063789, 12 with only 9-12 units in 1067620). Each one costs a segment even when the pearl is eaten.
3. **DOES: the queen sheds 2-long children** (eats, splits off 2, repeats). 12 of 15 games; not in 1063780, 1067620, 1056036. On the maps that start with 2-5 dragons (9 games: both Islands, Maze, both Trauma, both Devil, Portals, Tower Defense) she is the main source of new dragons. Best examples: 1067619 (9 splits by r111), 1069168 (r23, r30, r54).
4. **DOES: rams enemy heads with 2-longs from the next cell and 3-4-longs with 2-4-step moves.** 14 of 15 (no ram at all in 1063783). 1063780: 30 and 40 of 96 rams; 1064500: 32 and 40 of 91.
5. **DOES: long dragons (12+) reverse-split.** 11 of 15 (not in 1064508, 1063793, 1063784, 1064507, where nothing got long). 71 in 1063780, 97 in 1063789.
6. **DOES: a boxed-in queen splits just in front of the own segment that touches her head.** 10 splits in 7 games (1063780 twice, 1063789 twice, 1067623, 1069168 twice, 1067619, 1052703, 1063784).
7. **DOES: the queen walks away from every close enemy, paying segments if needed.** 34 of 34 close episodes (151 rounds, all moves); seen in 9 of 15 games, the other six had no close episode (1064500, 1052703, 1067619, 1063792, 1064508, 1063783). Best examples 1063780 r127-136 and 1067623 r158-173.

### Seen in wins

8. **DOES: kills the enemy queen with a 5-11-long that sprints 4-6 steps the moment she is in its view.** 5 of 6 wins include a kill of the enemy queen (not 1064508): four by a 5-11-long sprinting 4-5 steps, one (1063784) by a 3-long from the next cell; three of the five before r100 (r34, r36, r83). Best examples: 1063780 r34, 1069168 r223. The same was done in two losses (1067623 r150, 1052703 r216).
9. **DOES: sends a fresh split child of 7-12 segments, or the 2-long front part left after a split, at a queen or a leader.** 7 strikes in 5 games: 1064500 r82-83, 1056036 r464-472 and r478-479, 1069168 r414 and r441-445 (wins); 1067623 r140-150, 1067620 r391-392 (losses).
10. **DOES: feeds the queen late with self-kills of dragons up to 22 long once she is safe.** 3 of 6 wins (1063780 from r375, 1069168 from r400, 1064508 from r405); queen 28-32 at the end.
11. **HAPPENS: the opponent never brings a sprinter of 4+ within view of the own queen.** 3 of 6 wins (1063780, 1069168, 1064508); not in 1064500, 1056036, 1063784, where the own queen died and the game was won on length or by wipe-out.

### Seen in losses

12. **HAPPENS: behind 1.5 to 1 or worse in units by round 50-100.** 7 of 9 losses; not in 1063789, 1067619. Best examples: 1067620 (9 vs 62), 1063793 (3 vs 16).
13. **HAPPENS: the own queen is cut down or dies with no enemy involved, because her head has no free cell.** 4 of 9 losses (1063789 r484, 1052703 r261-263, 1067619 r345 and r366, 1063783 r131); in three of them own was winning on the queen rule at that moment. Also once in a win (1063784 r37).
14. **HAPPENS: the own queen is followed for dozens of rounds by small enemy dragons with no ally near, and rammed when a second enemy arrives.** 4 of 9 losses: 1067620 (in enemy view in 37 of the last 41 rounds), 1067623 (all of the last 41), 1063793 (the last 34 in a row), and 1064507 (a short approach, 10 rounds). Also in two wins (1064500: 21 of the last 22 rounds; 1056036: the last 30 rounds).
15. **HAPPENS: loses the "longest" race with the larger total length.** 3 of 9 losses: 1067623 (364 vs 187), 1052703 (273 vs 82), 1067619 (176 vs 73).
16. **HAPPENS: never gets a dragon within reach of the enemy queen.** 6 of 9 losses had 0 ram chances on her (1067620, 1063789, 1067619, 1063792, 1063783, 1063793); in four of those she was fed to 29-50. In the wins: 0 chances only in 1064508.

## What the protagonist's losses have in common

Nine losses. Each line is a weakness with its count.

1. **A slow opening is not recovered** (7 of 9 behind by 1.5 times or more by r50-100; five of the seven against forgot, one each against horse and SSS). The one win from such a start (1056036) was against SSS, which grew more slowly there than forgot did on the same map.
2. **The queen is lost to her own team's geometry** (4 of 9): a dead end entered for a pearl, a tight U-turn of a long body, an ally driving through the 2x2 room she circles in, allied tails left next to her head. The split rule then keeps only what lies in front of the blocking segment. Three of these four games were being won on the queen rule.
3. **The queen has no escort and no way to shake a follower** (4 of 9 rammed after being followed). She pays segments to run until she is 2-3 long; allies are not called in.
4. **No answer to an enemy queen that stays home and is fed** (6 of 9 with no ram chance; 1067620: 39, 1063789: 50, 1063792: 48, 1063783: 29). The hunters of the wins need to see her; in these games none got that far.
5. **Consolidation is late or split over several dragons** (3 of 9): the leader stalls at 63-65 for 75 rounds (1067623), is not rebuilt in 74 rounds after it is rammed (1052703: 12 -> 18), or is only started at r425 (1067619).
6. **Leaders rest where a small dragon can appear next to the head**: beside a portal mouth (1052703 r426) or beside an enemy that then splits (1069168 r427, a win).
7. **A mass loss at round 0 on Slithery Fight** (2 of 2 games on that map): 11 of 47 segments.

## Where the lead's first notes were wrong or thin

### 1052703 (Islands, loss to SSS)

- **"Vibing++ split and killed its own living 16-long queen" and "threw away a won game".** The events are right (r262 16 -> 2+14; r263 a split order from a 2-long, death by `noaction`). The reading is wrong: it was not a choice. At r261 she stepped north into (43,36) to eat a corpse pearl of own #574; that cell has kelp on its north, east and west edges and her own body to the south. From r262 she had no free neighbour. The split saved 14 of her 16 segments in child #624. The mistake to learn from is the step into a one-cell dead end at r261, when (42,37) was still free.
- **"rammed by a 4-long SSS dragon stepping onto it from the next cell".** The next cell was the far side of a portal. SSS #850 started the round at (29,38); the leader's head was at (51,39), beside the portal mouth. #850 had walked 24 steps in 10 rounds and through another portal at r422-423. It was a directed approach, not a lurker.
- **Thin.** Not noted: own did not rebuild a leader in the 74 rounds left (12 at r450, 18 at the end, with 40 units); and the enemy queen's killer came in on the corpse pearls of a fight beside her, with no own dragon having had her in view for 40 rounds.

### 1056036 (Australia, win over SSS)

- **"a queen kill at round 472 and a leader kill at round 479 decided it".** The queen kill decided it. At r475 own's longest was already 75 against 59; the leader kill made it 81 against 24 but was not needed.
- **The queen's death at r55** is described correctly. Add: it was she who closed the distance (she stepped west, towards the stalker), and a second SSS 3-long was 5 steps away at r54 and 3 at r55.
- **Thin on the hunter.** #781 had her in view for five rounds and passed seven turns with a path of 6-11 steps before the 4-step strike; 14 earlier turns (r280-316) by own 8-11-longs were also passed, each with her outside the attacker's view. "Sprinted 3 steps" for the leader's killer at r478: those 3 steps were free for a 12-long.

### A pointer for a game I did not read

The lead's note on 1053751 (Slithery Fight) says Vibing++ "reverse-splits at round 0 (25 -> 3+22) and keeps a 6-long queen". In both Slithery Fight games read here the 22-long child died in round 0 and 11 segments were lost. Worth checking there.

## Things I could not determine from replays

1. **What the sonar values say.** Own dragons ping 8,700-15,200 rays per 100 rounds with about 60 units (roughly 2.5 rays per dragon per round), and 1-5 rays a round end on a later killer. The best hints of a relayed target: own #255 in 1069168 walked 29 steps towards a queen it could not see, starting within five rounds of team-mates regaining sight of her; forgot #159 in 1067620 turned towards the own queen one round after a ray from a dragon with her in view ended on it. Neither is proof.
2. **How #680 (1067623) and #484 (1052703) knew where to go** when nobody on the team had the queen in view for 30-40 rounds: memory of an old sighting, a relay, or simply the mirror image of the own spawn. In both cases she was within 8 cells of her spawn.
3. **Why the 22-long child dies at round 0 on Slithery Fight.** The replay shows a split order that is not carried out. Whether that is intended (a quick meal for the queen) or a rule about dragons born in the same round, I cannot tell.
4. **Whether reverse splits of leaders are protection or just turning round.**
5. **Why own did not build or rebuild a leader** in 1067619 (r366-425), 1052703 (after r426) and 1067623 (r400-475).
6. **Whether kelp blocks sight.** "In view" here means inside the 7x7 square only.
7. **Whether the queen saw her stalkers.** At 5 steps (1056036) they were at the edge of her square.
8. **Why the own dragons found so few natural pearls on Trauma, Tower Defense and Portals** in the losses; the pearl count near the spawn was not lower than the opponent's.
9. Not read: the Autarky games of Vibing++. 1062216, 1065203 and the two contrast games of team 1119 were checked with the pack script and a few views only, not move by move.

## Appendix: two of our own games for contrast (team 1119)

Read with `python3 a_pack.py <id> 1119` and one board view; not part of the counts above.

### 1029030 Autarky, loss to WeHaveQuizzes on the queen rule (our queen dead; we end with 24 units, total 159 and a 93-long; they end with one dragon, a 2-long queen)

- **Our queen.** 3 long. Their #40 (2 long) has her in its view for 25 rounds in a row (r107-131), 2-4 steps away. She circles in place (W, N, E, S, W, N, W, W, S) and at r131 steps east from (15,14) to (16,14), next to its head at (17,14); it rams her. Two of our 3-longs were 3-4 steps from her in r129-131 and did nothing about it.
- **Their queen.** 2 long and alone (no ally within 6 steps from r240) for the last 260 rounds. One of our dragons is within 1-6 steps of her at 11 of the 13 checkpoints from r240 to r480.
- **Chances.** We had 7 turns with a free path to her head within reach (r227-248) and took none. On 6 of the 7 she was inside the attacker's view at its turn. r234: she steps west to (38,9), next to the head of our 3-long #267 at (38,10): one free step. It moves east. r236, r238, r240: our 3-long #259 is 2 cells from her (one paid step) and does not go. Our 2-long #199 walks along beside her in r233-235; that cannot work, because she moves first.
- With her dead at r234 both queens would have been dead and the longest dragon would have decided; we ended the game with a 93-long.

### 1053784 Trauma, loss to WeHaveQuizzes with both queens alive (31 vs 39)

- **Same shape as Vibing++'s Trauma games** (10 and 11): no enemy head within 3 steps of our queen in the whole game, a race to feed the queen. Their queen has 6-16 allies within 6 steps from r180 to r300 and is fed in rounds 250-350 (33 pearls: 3 long at r280, 31 at r340, 39 from r420). Ours is fed in rounds 300-400 (18 pearls from our own self-kills: 3 at r320, 23 at r400, 31 at the end). Units at r100: 11 against 21.
- **Chances.** Our 8-9-long #361 circles their 39-long queen from r447 to r469: 18 turns with a free path within reach (4-10 steps), none taken. On 4 of them she was inside its view at its turn with only 2-3 segments to pay (r448, r449, r459, r463; 4-5 steps). One ram there kills a 39-long queen while ours is 28-30 long and alive.

### The contrast

Vibing++ passed no turn on which the enemy queen was in the attacker's view and within reach (0 in 17 games; 9 of 9 kills made at the first such turn). We passed 10 such turns in these two games, and a ram on any one of them would have killed the queen that beat us.


