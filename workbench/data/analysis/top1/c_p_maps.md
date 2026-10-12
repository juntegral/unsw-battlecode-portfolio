## Per-map notes

How to read the tables. One row per 10 rounds unless the first column shows a wider block (50 rounds); every cell is "side A /
side B" (we are A in all 30 of our games read). Units and total length are at the start of the row. "Rammed" = own dragons that
an enemy rammed, "rammers" = own dragons that rammed an enemy, "head-on with a team-mate" = dragons lost when two heads of the
same team met (both die; these are not rams), "boxed" = non-ram deaths with no free cell, "other non-ram" = non-ram deaths
with a free cell. "Board squares" = how many of the 64 squares of an 8x8 grid over the board hold an own head. The last three
columns are about fountains: the share of own heads standing in the own half, natural pearls eaten on fountains of the enemy's
half, and the share of tile-rounds in which a pearl lay uneaten on a fountain of the own half (while it lies there the tile
produces nothing).
The "all games" lines are means per game from `c_agg.py` (`c_out/agg_map_<map>.txt`): meow = our games against 2000+ teams, all
builds; "test4 / WHQ against us" = those two opponents in our games; forgot, SSS, Vibing++ = their games against 2000+ teams.
Units and total length are at round 150; the other counts are sums over rounds 0-149.
Each of our games says which bot played it: "live" or "test build" (trade on contact; it differs from the live bot only on the
four large maps).

### Australia (large, 64x64; we won 1 of 28)

**Supply.** 1,420 natural pearls appear per 500 rounds, 56% of them on 36 fountain tiles: two pockets of 12 tiles each that are
closed by kelp and entered through a portal ((53-57,37-40), by path the one nearer to side A's spawn, and (6-10,23-26) for side
B), and 12 single tiles in the open. 43 pearls appear in rounds 0-9 and then only 5-7 per 10 rounds until somebody starts to
eat them: a fountain with a pearl lying on it is blocked.

**All games** (28 of ours): units at round 150: meow 38, test4 against us 62, WHQ against us 57, forgot 55, SSS 54, Vibing++ 40.
Natural pearls eaten in rounds 0-149: 117 / 259 / 227 / 218 / 219 / 181, of which on fountains of the enemy's half 22 / 81 / 64 /
38 / 38 / 38. Dragons rammed by the enemy: 15.3 / 2.4 / 3.6 / 17.0 / 12.6 / 10.0; dragons that rammed: 3.1 / 15.1 / 15.5 / 15.8 / 13.5 /
13.9. Boxed deaths: 10.5 / 58 / 31 / 30 / 40 / 43. We are the team with the fewest dead-end deaths and the fewest pearls. By build
(`c_out/bybatch_Australia.txt`): the 25 live games have 37 units against 59 at round 150 and total length 91 against 188; the
3 test-build games 47 against 52 and 132 against 140.

**The live bot's typical loss, 1058144 against test4** (queen rule; final 4 units and total 29 against 63 and 571):

<<TABLE 1058144 10 0 149>>

- Rounds 0-29: level (13 units each). 43 natural pearls lie on the board from round 10; at round 20 our heads are nearer to
  28 of them, at round 30 to 12 of 45 (test4: 33).
- Our dragons had 11 of the 12 tiles of the pocket of our half in view from round 10 (from outside the kelp) and never ate
  there in 150 rounds. test4's dragons eat inside OUR pocket from round 33 and inside the pocket of their own half from round
  39 (board at round 40: a test4 3-long stands at (7,23) on twelve lying pearls), 4-8 pearls on each of our 11 tiles by
  round 150 (`c_out/tiles_1058144.txt`: natural pearls eaten on the fountains of our half: we 31, test4 87; on those of
  test4's half: test4 99, we 8).
- test4 pays for it: 54 boxed deaths (122 segments) in 150 rounds, 13 of them on one cell, against our 3. It eats 87 of its
  own corpse pearls back and has 63 units at round 120 against our 32.
- From round 60 test4 rams: we lose 13 dragons to rams by round 150 and make 1. Of the 128 natural pearls that appeared within
  6 steps of one of our heads we ate 68 and test4 53; of the 53 with no enemy head within 6 steps we ate 47 after 3.4 rounds
  (test4: 173 of 190 after 3.3 rounds). Undisturbed, the two teams are equally fast.

**The same opponent against forgot, 1046985** (forgot is side A, as we are; forgot won on the longest dragon, 58 against 23):

<<TABLE 1046985 10 0 149>>

- forgot is out-eaten by test4 almost as badly as we are (120 natural pearls against 287 in rounds 0-149; 40 units and total
  96 against 62 and 189 at round 150) and has 1 boxed death against test4's 59. What forgot does that we do not: it rams (14
  rams made and 22 suffered in rounds 0-149; we 1 and 13), and from round 150 it rams far more than test4: 29, 21, 33, 24
  rams per 50 rounds against 8, 2, 7, 1, with rammers of 2.5-3.0 segments on victims of 3.2-4.3, and it eats the corpses
  (104 corpse pearls against 57 in rounds 250-299). Its total goes 96, 94, 137, 168, 170 at rounds 150 to 350 while test4's
  goes 189, 228, 261, 230, 211 (`c_out/ledger_large.txt`), and it ends with a 58-long against a 23-long. An opening deficit
  against test4 on this map is not what separates us from forgot; what happens at the border afterwards is.
- SSS against test4 (1046528, SSS won): 237 natural pearls against 201, 47 boxed deaths against 41. Vibing++ against test4
  (1054789, Vibing++ lost): 92 against 275 and 18 units against 63 at round 150.

**The test build with a good opening, 1068050 against WHQ** (lost on the queen rule: our queen dead, WHQ's 70 long):

<<TABLE 1068050 10 0 149>>

- This is what trading on contact does on this map. In rounds 0-149 the test build has 38 meetings and rams in 15 of them; it
  makes 20 rams and suffers 8 (the live bot against the same opponent an hour earlier, 1063239: 4 made, 16 suffered, 2 of 46
  meetings). It eats 64 pearls of ram corpses and WHQ 32. From round 50 only 46-56% of our heads stand in our own half, and we
  eat 40 natural pearls on the fountains of WHQ's half against WHQ's 22 on ours. At round 150 we have 60 units and total 207
  against 33 and 84; the live bot in 1063239 had 51 and 128 against 54 and 148.
- Then the clock. Per 50 rounds (`c_ledger.py`):

| rounds | our units | our total | our natural | our dragons rammed (segments) | WHQ units | WHQ total | WHQ natural | WHQ rams made |
|---|---|---|---|---|---|---|---|---|
| 100-149 | 57 > 60 | 141 > 207 | 92 | 6 (25) | 33 > 33 | 78 > 84 | 55 | 6 |
| 150-199 | 60 > 60 | 207 > 199 | 63 | 17 (65) | 33 > 58 | 84 > 187 | 124 | 17 |
| 200-249 | 60 > 49 | 199 > 172 | 49 | 11 (57) | 58 > 64 | 187 > 235 | 101 | 11 |
| 250-299 | 49 > 54 | 172 > 184 | 42 | 8 (22) | 64 > 45 | 235 > 245 | 107 | 8 |

Our natural intake per 100 dragon-turns falls from 3.05 to 2.08 at round 150 and to 1.7-1.8 later; WHQ's is 3.2-5.2 throughout.
This is the round-150 switch (answer f), in a game that the opening had won. The test build against test4 on this map
(1067904) is behind from the start of the contact (47 units against 61 at round 150, total 107 against 161) but far less than
the live bot in 1063011 (27 against 64, 63 against 232).

### Around UNSW (large, 64x64; we won 6 of 24)

**Supply.** 2,035 natural pearls per 500 rounds, 76% on 84 fountain tiles: a cluster of 17 tiles 21-27 steps from each spawn
((50-56,6-8) and (58-60,11) for side A), a central cluster of about 32 tiles around (28-35,29-34) that both teams reach in 28-37
steps, three tiles at (58-59,26-27) with their mirror at (4-5,36-37), and a few corridor tiles.

**All games** (24 of ours): units at round 150: meow 59, test4 63, WHQ 62, forgot 58, SSS 61, Vibing++ 60, so no unit gap. Total
length at round 150: 157 / 281 / 261 / 151 / 239 / 213. Natural pearls eaten in rounds 0-149: 220 / 383 / 379 / 281 / 387 / 361, of
which on fountains of the enemy's half: 27 / 122 / 109 / 74 / 127 / 110. Own heads in the own half: 78% / 63% / 69% / 77% / 71% / 69%.
Cells visited by round 140: 1,344 / 1,864 / 1,668 / 1,537 / 1,558 / 1,499. Boxed deaths: 45 / 53 / 62 / 86 / 91 / 85. The whole
natural-pearl gap to test4 and WHQ on this map is in the enemy's half: they take 109-122 pearls from our fountains, we take 27
from theirs.

**The live bot against test4, 1063016** (lost on the longest dragon, 73 against 100):

<<TABLE 1063016 10 0 149>>

- No fight is needed to lose this map. test4 has 41 units at round 40 and 61 at round 60; we have 21 and 27. In 150 rounds
  we eat 190 natural pearls and test4 403; on the fountains of the other half we eat 1 and test4 121. From round 20 on 83-97%
  of our heads are in our own half (test4: 63-78%). Only 12 of our dragons are rammed in these 150 rounds and we ram 6 times;
  of 13 meetings we ram in 2.
- The units catch up by round 140 (60 against 64) because test4 is at the 64-unit cap; the total length does not (138
  against 312).

**The test build against test4, 1067909** (lost on the queen rule; final 33 units and total 222 against 61 and 443):

<<TABLE 1067909 10 0 149>>

- Until round 30 we are level or ahead: 18 units against 16 at round 20, 21 against 22 at round 30 (total length 52 against
  50), and we have seen 33 of the 39 fountains of our half (test4: 22 of its own). From round 30 test4 eats 29-39 natural
  pearls per 10 rounds and we 11-18; test4 has 57 units at round 60, we 31.
- Where: `c_out/tiles_1067909.txt`. We eat on the 17 tiles of our near cluster (about 50 pearls in 100 rounds, at the pooled
  rate). The central cluster we reach first (round 10-23) and then lose: by round 100 test4 has eaten on 35 of the 39
  fountains of its half and on 21 of the 39 of ours; we have eaten on 21 of ours and 9 of theirs. The three tiles at (58-59,26-27),
  34-36 steps from our spawn and 43-45 from theirs, give test4 13 pearls from round 26 on and us 1 (at round 99).
- How the centre was lost (events of rounds 22-30 around (31,31)): at round 22 three of our dragons stand in a field of about 30
  lying pearls. `#17` (L4) splits inside a 2x2 nook; next round the parent has only its own tail and its child's tail next to
  its head and dies ("body"). The child `#44` walks away west (9 moves, no pearl). `#38` (L3) eats a pearl and at round 23,
  4 long, eats another and rams test4's 5-long `#20` in the same two-step move (the test build's rule allows a target of its
  own length; the live bot would ask for 6 segments here). `#41` (L2) circles for 8 rounds, eats one corpse pearl at round 29
  and is rammed at round 30 by test4's `#10`, which moved three steps (a charge; eating a pearl on the way pays for a step).
  `#5` (L2) arrives, eats one pearl at round 30 and is rammed in the same round by `#36`, which also moved three steps over
  two pearls. Four of ours and three of theirs are dead by round 30;
  test4's survivors split on the pearls and stay; ours do not come back (85% of our heads are in our own half from round 30,
  64-70% of theirs).
- Against the live game above the test build makes 14 rams instead of 6 and eats 215 natural pearls instead of 190, 18 on
  test4's fountains instead of 1; test4 still eats 382.

**SSS against test4 from our side of the board, 1064304** (SSS won on the longest dragon):

<<TABLE 1064304 10 0 149>>

- SSS has 62 units at round 100 (we 39 and 45 in the two games above), eats 405 natural pearls in rounds 0-149 (we 190 and
  215), 131 of them on fountains of test4's half (we 1 and 18), and has 89 boxed deaths (we 41 and 44). Against SSS it is
  test4 that stays at home (30 pearls from SSS's half).
