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

