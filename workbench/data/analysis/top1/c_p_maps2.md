### Islands (large, 56x40; we won 0 of 30)

**Supply.** 1,546 natural pearls per 500 rounds, 85% on 26 fountain tiles. Each side has four big fountains 3-6 steps from its
queen's start ((41,6), (47,6), (41,9), (47,9) for side A; 54-79 pearls per 500 rounds each), three corridor tiles at (38-39,12-13),
one at (42,21), four at (42-43,36-38) and one at the bottom edge ((54,36) for A and (1,36) for B, three cells apart across the wrap).

**All games** (30 of ours): units at round 150: meow 36, test4 62, WHQ 57, forgot 57, SSS 57, Vibing++ 46. Natural pearls in
rounds 0-149: 202 / 281 / 241 / 281 / 266 / 227. Dragons rammed by the enemy: 33.8 / 8.3 / 9.6 / 32.3 / 25.1 / 20.6; dragons that rammed:
8.5 / 37.3 / 32.8 / 28.8 / 27.3 / 34.9. Boxed deaths: 24.7 / 27.8 / 31.3 / 37.0 / 50.2 / 33.2. Non-ram deaths with a free cell: 18.4 /
0.5 / 4.4 / 0.2 / 1.5 / 3.9. Meetings (a turn that begins with an enemy head on the next cell): 52.7 per game for us, and we step
away in 88% of them (test4 65%, WHQ 66%, forgot 63%, SSS 52%, Vibing++ 58%).
The 18.4 are steps through a portal onto a body on the far side, which the dragon cannot see: 12.7 onto a team-mate and 5.7
onto an enemy per game in rounds 0-149 (`c_freedeaths.py`; our opponents 3.0; on all large maps together we 6.4 and they
2.2). It is 43% of our non-ram deaths on this map and costs 44 segments a game.
By build (`c_out/bybatch_Islands.txt`): the 27 live games have 35 units against 60 at round 150 and total length 85 against 198;
the 3 test-build games 47 against 55 and 123 against 149; at round 300 both are lost (11 against 62 units, and 18 against 58).

**The live bot against test4, 1063012** (lost on the longest dragon, 11 against 57; 3 units left against 17):

<<TABLE 1063012 10 0 149>>

- For 90 rounds we are level or ahead: 44 units against 39 at round 80, total 102 against 96, and 134 natural pearls
  against 129 in rounds 0-89. Nothing is wrong with the opening.
- From round 70 test4 rams: 6, 7, 3, 6, 8, 9, 4, 2 of our dragons per 10 rounds, 49 in the 150 rounds; we ram 6 times, in 3 of
  56 meetings. test4 eats the dead: 13-30 corpse pearls per 10 rounds in rounds 70-139 against our 2-12. Ten more of ours die with
  a free cell beside them (the step through a portal onto a body).
- Units: 44 at round 100, 26 at round 150, 5 at round 300; test4 46, 62, 63. The test build against the same opponent
  (1067905) makes 21 rams and suffers 32 in rounds 0-149 and has 41 units against 63 at round 150; it is lost as well.

**The test build with a good opening, 1068051 against WHQ** (lost on the longest dragon, 16 against 82):

<<TABLE 1068051 10 0 149>>

<<TABLE 1068051 50 150 349>>

- We lead until round 150: 60 units against 39, total 170 against 91 (the live bot against WHQ on this map an hour earlier,
  1063240: 47 against 61 and 108 against 189; it rams in 6 of 84 meetings, the test build in 11 of 40). Then our units fall 60,
  49, 39, 32, 19 and WHQ's rise 39, 52, 60. The ledger per 50 rounds (`c_ledger.py`): natural pearls 100, 78, 42, 29, 30 for us
  from round 100 and 68, 72, 105, 97, 108 for WHQ; segments we lose to WHQ's rams 58, 99, 63, 41, 32; segments WHQ loses in the
  rams it makes 44, 74, 53, 36, 28. WHQ's rammers are shorter than their victims (2.8 against 3.8 segments on average in
  rounds 150-199) and WHQ eats 38 pearls of our dead in rounds 150-199 while we eat 15 of theirs.
- By length class (`c_out/mid_1068051.txt`): in rounds 150-199 our 2-longs eat 1.86 natural pearls per 100 dragon-rounds and
  WHQ's 3.08; 3-4-longs 3.11 and 3.78. In rounds 150-209, 23-29 of our 49-60 dragons have not eaten for 20 rounds (WHQ: 11-17
  of 39-53). A pearl lies uneaten on 42-69% of the fountain tile-rounds of our half after round 150 (before: 22-40% from round
  40 on; WHQ's half after round 150: 29-47%).
- Rounds 140-220 dragon by dragon (`c_out/midlist_1068051.txt`; the 28 of our dragons that were 5 or longer at some round):
  9 were rammed, by attackers of 2-4 (`#76` at L12 by an L2 at (26,3) after it left the fountains at (42-43,37-38) at round 180
  and walked 40 cells; `#133` L9 by an L3; `#241` L9 by an L4; `#360` L10 by an L2 five rounds after it was born; `#290` L7 by
  an L2; `#326` L6; `#207` L5; `#316` L5 in the round it was born; `#44` L4). 8 shed their front two segments in a place with
  no way out (12 -> 2+10 twice, 7 -> 2+5 three times, 6 -> 2+4 twice, 5 -> 2+3), the 2-long front part dying the next round.
  The others roam: `#84` (L5 -> 10) stands on 76 different cells in 81 rounds and eats 5 pearls; `#315` (L5) takes 93 steps in
  48 rounds and eats nothing. None of them splits in the ordinary way (our rule: no growth splits above length 4 after round 150
  on maps over 1,200 cells).
- A camper that does not eat: our `#3` (L3) circles six cells next to the fountain (1,36) from round 14 to 26; at round 20 a
  natural pearl lies on (1,36), next to its head at (1,37), with nobody near, and it steps west. It eats one pearl in 13
  rounds. (Why it declined I could not determine; the bot's score for that step is not in the replay.)

**forgot against the same opponent from our side, 1062235** (forgot won on the longest dragon, 84 against 63):

<<TABLE 1062235 50 0 349>>

- forgot has 61-62 units from round 100 to 350. It loses 8-13 dragons to rams per 50 rounds (we 8-26) and makes 9-21 rams
  (we 1-11), replaces its losses (48-74 splits per 50 rounds; we 45, 32, 19, 12 after round 150) and keeps eating 99-129
  natural pearls per 50 rounds. WHQ against forgot stays at 20-37 units.

### Slithery Fight (large, 63x27; we won 5 of 29)

**Supply.** 2,720 natural pearls per 500 rounds, the richest map; 86% on 115 fountain tiles, most of them in narrow corridors and
at their closed ends (rows 0-1 and 25-26, and single cells such as (39,19) and (46,19)).

**All games** (29 of ours): units at round 150: meow 57, test4 62, WHQ 63, forgot 61, SSS 62, Vibing++ 57. Total length at round
150: 160 / 204 / 229 / 160 / 208 / 170. Natural pearls in rounds 0-149: 421 / 409 / 497 / 549 / 388 / 502. Boxed deaths: 242 / 169 / 205 /
262 / 87 / 284. Splits: 322 / 250 / 290 / 356 / 179 / 367. Dragons rammed: 21.5 / 3.8 / 5.1 / 17.3 / 18.4 / 9.6; dragons that rammed: 4.5 /
21.9 / 20.7 / 18.9 / 18.0 / 18.4. We eat as much as test4 here; the length goes into deaths. The test build is no better on this
map (3 games: 53 units against 61 and total 145 against 226 at round 150; the 26 live games 58 against 62 and 162 against 207).

**The live bot against WHQ, 1063252** (lost on the longest dragon, 64 against 94):

<<TABLE 1063252 10 0 149>>

- A level game for 150 rounds: 61 units against 63 and total 176 against 200 at round 150, 456 natural pearls against 447.
  We make 349 new dragons and lose 272 boxed; WHQ 282 and 205. WHQ rams 17 of ours and we ram 2 (1 of 26 meetings). It is lost
  in the second half: total 174 against 256 at round 300.

**The test build against test4, 1067917** (lost on the queen rule; final 21 units and total 153 against 36 and 244):

<<TABLE 1067917 10 0 149>>

- 38 units at round 50 against 58, 40 at round 100 against 64, 42 at round 150 against 63. Per 50 rounds we eat 152, 123, 118
  natural pearls and 66, 115, 125 corpse pearls and lose 73, 100, 100 dragons boxed (148, 209, 208 segments); test4 eats 149,
  143, 149 and 48, 126, 112 and loses 43, 74, 42 (92, 191, 155 segments).
- 274 non-ram deaths in 150 rounds on 34 cells; 37 on (46,19) and 37 on (39,19), one every four rounds on each.
- The form of it (`c_out/ec_1067917.txt`, splits): 57 splits 4 -> 2+2, and 236 splits in which a dragon of 6, 7 or 8 keeps
  only its front two segments (6 -> 2+4: 92, 7 -> 2+5: 63, 8 -> 2+6: 81). Natural pearls by the eater's length: 2: 49, 3: 70,
  4: 103, 5: 37, 6 and more: 136. Our dragons walk into a closed corridor, eat everything in it, grow to 6-8 and then shed the
  front two, which die; the rear part, now a dragon of 4-6 with its head at the old tail, goes back in for the dead front's
  pearl. That makes no new dragon. In our bot this is the "harvest" mode (`harvestable()`: enter a dead end that holds at least
  3 pearls, do not split while harvesting, leave by the escape split). The rule is the same in the live bot and the test build.
- forgot on the same side against test4 (1046988): 294 of its 375 splits are 4 -> 2+2 and its eaters are 2 long (247 pearls) or
  3 long (246); it has as many boxed deaths as we do (275) but 50 units at round 50 and 61 at round 100. Vibing++ (1054792):
  276 boxed deaths, 589 natural pearls, 58 units at round 100.
- All our games on this map, rounds 0-99 (`c_out/midall_1119_Slithery Fight.txt`): 65 splits at length 4 and 125 sheds per game;
  our opponents 120 and 56. On the other three large maps our sheds are 1-17 a game, the same as our opponents', and on
  medium and small maps 5 against 5-6: the shed form is this map's (closed corridors full of fountains), not a general habit.

**SSS against test4 from our side, 1051824** (SSS won on the longest dragon, 22 against 18):

<<TABLE 1051824 10 0 149>>

- SSS eats 344 natural pearls in 150 rounds, a quarter fewer than we do in the live game above (456) and fewer than test4
  (387), makes 170 new dragons and loses 77 boxed (we 349 and 272), and has 61 units and total length 200 at round 150
  against test4's 64 and 167 (we 61 and 176 against WHQ, 42 and 113 against test4). 99 of its 170 splits are at length 4, 37
  at length 5, and only 24 are by dragons of 6-8 that keep their front two segments. Fewer pearls, far fewer deaths, more
  length: on this map the deaths are what our pearls pay for.

### Trauma (medium, 48x24; we won 4 of 27)

**Supply.** 732 natural pearls per 500 rounds; 42% on 10 fountain tiles (a column of five at (13,10-14) and its mirror at
(34,9-13)); the rest on 130 slow tiles. The two start areas are separated by portals; nobody rams before round 150.

**All games** (27 of ours): units at round 150: meow 14, test4 40, WHQ 35, forgot 35, SSS 33, Vibing++ 32. Natural pearls in
rounds 0-149: 48 / 120 / 106 / 110 / 106 / 112, of which on the own fountain column 27 / 66 / 54 / 62 / 60 / 73. Natural pearls per 100
dragon-turns: 4.5 / 4.4 / 5.2 / 4.4 / 5.2 / 4.8, the same for everybody: the gap is the number of dragons, and it is made in the
first 50 rounds. A pearl lies on 76% of our fountain tile-rounds (test4 34%, WHQ 47%).

**Against test4, 1067915** (test build, the same as the live bot on this map; lost on the queen rule):

<<TABLE 1067915 10 0 149>>

- test4 eats on its fountain column from round 20 (from then on a pearl lies on its five tiles in a quarter of the
  tile-rounds); we eat our first fountain pearls after round 60, and a pearl lies on ours in 50-100% of the tile-rounds all
  game. In 150 rounds we eat 24 natural pearls, 13 of them on our column; test4 111 and 66. 7 units against 36 at round 140.
  This is the known problem (the fountains are reached through a portal).

**Against WHQ, 1068061** (same bot; lost by wipe-out at round 467):

<<TABLE 1068061 10 0 149>>

- Here the opponent is as slow as we are. WHQ does not touch its column until round 130 (from round 10 a pearl lies on all
  five tiles in every round) and the game is level: 9 units against 11 at round 130, total 31 against 27. Then WHQ's dragons reach the
  column, eat 45 natural pearls in 20 rounds and are 18 at round 140; we eat 12. The gap of this game is 20 rounds old at
  round 150.

**forgot against test4 from our side, 1046991** (forgot won on the queen rule, 46 against 25):

<<TABLE 1046991 10 0 149>>

- forgot never eats on its fountain column in these 150 rounds (from round 10 a pearl lies on all five tiles in every round;
  test4 eats 57 on its own). It lives on the slow tiles: 43 natural pearls, 3 units at round 50, 9 at round 100, 13 at round 150 against
  test4's 10, 20 and 25. It was as slow as we were against the same opponent and still won: on this map the end game decides
  more than the opening. Over all games forgot does reach the column (62 pearls there against our 27).

### Maze (medium, 48x24; we won 8 of 27)

**Supply.** 1,381 natural pearls per 500 rounds; 49% on 38 fountain tiles, 34 of them narrow corridor cells (two open sides,
20 or fewer cells within four steps).

**All games** (27 of ours): units at round 150: meow 37, test4 48, WHQ 57, forgot 47, SSS 54, Vibing++ 52. Natural pearls in
rounds 0-149: 129 / 156 / 220 / 167 / 189 / 230, of which on fountains of the own half 49 / 44 / 85 / 57 / 86 / 87. Fountains of the
own half eaten from by round 140 (of 19): 9.7 / 12.2 / 18.1 / 12.3 / 15.4 / 15.2. Boxed deaths: 30 / 32 / 53 / 41 / 48 / 68.

**Against WHQ, 1068052** (test build, the same as the live bot on this map; lost on the longest dragon, 66 against 94):

<<TABLE 1068052 10 0 149>>

- The gap opens in rounds 60-89: we eat 2, 7 and 6 natural pearls per 10 rounds and WHQ 13, 25 and 20. From round 70 a pearl
  lies on WHQ's fountains in 37-65% of the tile-rounds; on ours in 92-96% until round 110. In 150 rounds we eat 116 natural
  pearls, 42 on the fountains of our half; WHQ 220 and 99.
- `c_out/tiles_1068052.txt` (rounds 0-150): we eat on 8 of our 19 fountain tiles (43 pearls) and WHQ on all 19 of its own (101
  pearls). (15,5) and (16,5) are in view from round 45 and never eaten; (17,8) and (17,9) from round 61, never; six of the
  eight tiles at (29-31,0-3) are in view from round 62-100 and never eaten; (11,1) and (11,2) are seen at round 30 and first
  eaten at round 53. All of them are corridor cells with two open sides and 6-13 cells within four steps. Our dragons do not
  go into them; WHQ's do and lose 5 dragons on its fountain tiles (we none).

**Against test4, 1067906** (same bot; lost on the queen rule):

<<TABLE 1067906 10 0 149>>

- Level: 154 natural pearls against 140, 43 units against 42 at round 150. test4 leaves its fountains alone as well until
  round 90 (a pearl lies on them in 92-96% of the tile-rounds from round 30), and from round 90 we eat 28 pearls on test4's
  fountains. The game is lost after round 150.

**forgot against test4 from our side, 1046984** (forgot lost on the queen rule):

<<TABLE 1046984 10 0 149>>

- The same picture as our game against test4: 155 natural pearls against 133, 40 units against 36 at round 140, 58 pearls on
  the fountains of its half. On this map the difference in the opening is to WHQ, SSS and Vibing++, who go into the corridors
  (18.1, 15.4 and 15.2 of 19 fountains eaten from), not to test4 or forgot (12.2 and 12.3; we 9.7).

### Tower Defense (small, 32x16; we won 0 of 24)

Known (the start room). The map has one fountain tile by my definition (11 pearls per 500 rounds); 78% of its pearls come from
59 slow tiles (5-9 pearls each per 500 rounds), so the last column of the tables means little here.

**All games**: units at round 150: meow 3, test4 37, WHQ 29, forgot 22, SSS 20, Vibing++ 11; natural pearls in rounds 0-149:
5 / 103 / 88 / 84 / 61 / 42; cells visited by round 140: 64 / 331 / 302 / 291 / 244 / 211.

**Against test4, 1067908** (test build, the same as the live bot on this map; wiped out at round 322):

<<TABLE 1067908 10 0 149>>

- Our two dragons stay in the start room (all heads in the own half, two board squares) and eat 6 pearls in 150 rounds.
  test4's dragons leave at round 50-60 (the share of its heads in its own half falls from 100% to 49%), eat 17 pearls in
  rounds 60-69 and are 31 at round 120.

**Against WHQ, 1068054** (same bot; lost on the queen rule at round 500: our queen dead, WHQ's 32 long):

<<TABLE 1068054 10 0 149>>

- In this game the opponent is stuck too: WHQ has one dragon from round 50 and eats no natural pearl in 150 rounds; we have
  1-3 dragons and eat 4. Neither side leaves its room before round 150. The start room is not only our problem; but the two
  opponents get out in most games (37 and 29 units at round 150 on average) and we have 3.

**forgot against test4 from our side, 1046992** (forgot won on the longest dragon):

<<TABLE 1046992 10 0 149>>

- forgot's two dragons eat their first pearls at round 40-59 and leave at round 60 (heads in the own half: 61% in rounds
  60-69, about half from then on), eat 19, 19, 12 and 10 natural pearls per 10 rounds and are 28 at round 120. test4 is the
  one that stays at 4 units in this game.

### Stripes (small, 24x12; we won 5 of 29)

**Supply.** 459 natural pearls per 500 rounds; 78% on 12 fountain tiles. The two strongest of each half ((11,10) and (12,10) for
side A) lie in a four-cell pocket, (11-12,10-11), closed by kelp. The way in is a portal: a step south from (10,10) comes out
at (11,11) (boards at round 18 of 1067907 and 1068053).

**All games** (29 of ours): units at round 140, or at the last 10-round mark of a shorter game: meow 3, test4 12, WHQ 15, forgot
13, SSS 12, Vibing++ 17. Natural pearls in rounds 0-149: 17 / 54 / 71 / 57 / 68 / 84; per 100 dragon-turns 3.0 / 6.3 / 7.4 / 6.9 / 6.9 /
8.4. With a pearl in view and nobody else as near, our dragons fail to get nearer in 47% of turns (everyone else 26-35%). Of
the pearls that appear within six steps of one of our heads the enemy eats 38% (of theirs we eat 2-10%). Dragons rammed: 3.9 /
1.4 / 0.6 / 4.0 / 3.6 / 2.3; dragons that rammed: 0.8 / 3.8 / 4.3 / 4.4 / 5.2 / 6.3.

**Against test4, 1067907** (test build, the same as the live bot on this map; wiped out at round 140):

<<TABLE 1067907 10 0 139>>

- We eat nothing for 30 rounds. Our queen `#1` walks east along row 10 and is at (9,10) at round 7 with the two pocket pearls
  in view two cells away behind the kelp. She turns south, wanders over (9,11), (10,11), (10,0), (9,1) for ten rounds, and
  stands on the door cell (10,10) at round 18. A test4 2-long (`#5`) is at (13,0) then, two cells from the pocket across the
  wrap. She steps north and walks round the outside of the pocket for the next 15 rounds without going in. (Inference: the
  enemy head near the pocket. Not the queen's portal ban: on a map of 288 cells our bot's queen rules are off, `is_queen()`
  needs more than 600 cells or a closed home, and in the next game she goes through.) Our other dragon `#3` wanders in rows
  6-8, where there are no fountains. test4's two dragons eat their first pearls at rounds 11 and 12 (one of them is its queen,
  through the portal of its own pocket) and are five by round 30.
- From there it is a ram fight between 2-3 dragons of ours and 7-18 of theirs.

**Against WHQ, 1068053** (same bot; wiped out at round 176):

<<TABLE 1068053 10 0 149>>

- The same first 18 rounds, move for move. This time no enemy head is near at round 18: the queen steps south through the
  portal, eats (12,10) at round 20 and (11,10) at round 21, and splits at round 22. In that round WHQ's `#4` (L2) steps through
  the same portal from the other side, from (10,11), and rams her: our queen is dead at round 22. We eat 14 natural pearls in
  150 rounds, 8 of them on our fountains; WHQ 114, of which 54 on its own fountains and 40 on ours; 7 of ours are rammed and
  we ram nobody.

**forgot against test4 from our side, 1046977** (forgot wiped test4 out at round 91):

<<TABLE 1046977 10 0 99>>

- forgot's queen starts on the same cell as ours, (2,10), and walks the same row. She is on the door cell (10,10) at round
  8, goes through, eats (12,10) at round 10 and (11,10) at round 11, splits at round 12, leaves through the portal at round 13
  and is back inside for the next pearl at round 19. Our queen is at the door ten rounds later (round 18) and eats at rounds
  20-21 or not at all. In 90 rounds forgot eats 29 natural pearls on the fountains of its half and 18 on test4's, makes 2 rams
  and has 13 units when test4 has none.

### Portals (small, 32x16; we won 6 of 27)

**Supply.** 1,262 natural pearls per 500 rounds; 96% on 56 fountain tiles: 2x2 blocks closed by kelp and entered through a
portal, and one corridor one cell wide with four of the richest tiles of the map ((15,1), (15,3), (15,5), (15,7) for side A,
32-52 pearls per 500 rounds each). The two teams never meet: there is no ram between the teams in rounds 0-149 in any of our
27 games (`c_agg.py`) and none in 500 rounds in the three games read; by my path map no fountain of one half can be reached
from the other spawn (`c_out/tiles_1063682.txt`). This map is the economy and the end game with nothing in between.

**All games** (27 of ours): units at round 150: meow 19, test4 33, WHQ 25, forgot 37, SSS 30, Vibing++ 23. Natural pearls in
rounds 0-149: 187 / 207 / 140 / 225 / 136 / 110. Natural pearls per 100 dragon-turns: 9.2 / 6.4 / 6.1 / 6.6 / 6.1 / 5.1, ours the highest.
Boxed deaths: 120 / 108 / 42 / 108 / 55 / 40; segments lost in them 307 / 264 / 99 / 255 / 134 / 94. Splits: 141 / 142 / 71 / 156 / 83 / 62.
So for every 100 new dragons we lose 85 boxed, test4 76, WHQ 59, forgot 69, SSS 66 and Vibing++ 65; and we lose a dragon for
every 1.6 natural pearls, test4 for every 1.9, forgot 2.1, SSS 2.5, Vibing++ 2.8, WHQ 3.3. Where the deaths are
(`c_out/deadcells.txt`, 12 games a team): ours on 32 different cells a game, 74% on a cell where a team-mate had died before;
forgot's 110 on 60 cells, 46% on such a cell; 39% of ours come within a round of eating on that cell (forgot 22%, our
opponents 23%).
How the games end (`c_endstate.py`): our 21 losses are 14 on the longest dragon and 7 on the queen rule. At round 300 our total
length is below the opponent's in 20 of the 21; at the end the totals are level (50 against 52) and theirs is in one dragon:
longest 30 against 42, units 5.3 against 2.6, our queen dead in every one.

**Against test4, 1063682** (queen-hunt test build, which changes nothing on a map where the teams never meet; lost on the longest dragon, 16 against 33):

<<TABLE 1063682 10 0 149>>

- We eat nearly as much as test4 and have half its units. In 150 rounds we eat 192 natural and 184 corpse pearls and test4
  215 and 156; we make 143 new dragons and lose 123 boxed and 4 in head-ons between team-mates; test4 makes 153 and loses 110
  and 6. 14 units against 32 at round 140. Our dragons die 2-3 long on a few cells ((16,7) 14 times, (22,10) 12, (27,5) 10,
  (19,12) 10 in 150 rounds); (16,7) is the one-cell nook at the bottom of the rich corridor at x=15 (board at round 60: our
  `#57`, L2, has its head in the nook and its tail on (15,7), and no way out). 101 of our 144 splits are 4 -> 2+2. test4 here
  is the one that sheds (77 of its 155 splits are by dragons of 5-7 that keep their front two segments), the reverse of
  Slithery Fight.
- Why the same pearls cost us more dragons than they cost test4 or forgot on this map I did not find out. It is not that we
  take pearls in dead-end cells more readily: a free pearl on a next cell that has no other exit is eaten in 61% of turns by
  us and in 60% by our opponents on small maps (`c_out/adj_1119_small.txt`).

**Against WHQ, 1063251** (live bot; lost on the longest dragon, 9 against 37):

<<TABLE 1063251 10 0 149>>

- We eat half as much again as WHQ (203 natural pearls against 135, 189 corpse pearls against 57) and end the 150 rounds with
  fewer dragons (17 against 24 at round 140): 156 new dragons and 132 boxed deaths for us, 70 and 44 for WHQ. WHQ grows by
  not dying.

**forgot against test4 from our side, 1046982** (forgot lost on the queen rule):

<<TABLE 1046982 10 0 149>>

- forgot eats 226 natural and 159 corpse pearls, makes 157 new dragons and loses 107 boxed: 22 units at round 60 against
  test4's 15 and 35 against 32 at round 140. With the same number of new dragons as we make in 1063251 it loses 25 fewer.

### weakhold (small, 40x15; we won 10 of 27)

Not a problem in the opening: units at round 150: meow 21, test4 9, WHQ 21, forgot 16, SSS 18, Vibing++ 22; natural pearls in
rounds 0-149: 94 / 36 / 98 / 59 / 71 / 131. We lose this map to WHQ later (3 wins in 11); it is also the one map where a loss often
comes with the larger total length at round 300 (8 of 17 losses, `c_endstate.py`).
