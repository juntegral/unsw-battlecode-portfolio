## 4. Per game: the two leaders from round 250

How to read these. `#61` is a dragon id; `(37,3)` a cell (x east, y south, the board wraps). "13 -> 33" is the longest
dragon's length at the two rounds named. "Cut" = the leader keeps 2 and hands the rest to a new id. "P" = potential,
"c" = completeness (longest / P). All numbers are from `python3 e_show.py <game> 250 [--step 10] [--deaths]` and
`python3 e_cutlist.py <game> 390`; boards from `python3 story.py view <game> <round> <x> <y> <radius>` (start of the
round; `A`/`B` heads, `a`/`b` bodies, `*` pearl, `|` and `-` kelp, `O` portal). Belief lines exist only for games whose
sonar is readable (marked).

### Our 14 losses with level total length at round 400

**1. 1027819, Maze, run stride-old (live bot, sonar readable), against test4. Lost 32 to 77.**
- Round 300: 55 units against 49, P 84 against 92, longest 4 against 8. test4's longest is its queen `#0`, 8 long at
  (8,13), with 38 of its 49 heads within 15 cells of her (112 of its 157 segments): the team sits around its home.
- Our zone phase: the dragon that will lead, `#61`, is 3 long at round 325, 8 at 330, 12 at 340 and 16 at 345, all
  inside the box x 37-41, y 0-7 (`story.py track 1027819 61 5`). At the start of round 346 its head is at (37,3), at
  the bottom of a column it has just come down (it moved south three cells in round 345): kelp on its west side, its
  own body north and east, one free cell south, (37,4), and behind that cell the head of a 2-long of ours, `#494`,
  coming up the same column:

  ```
  round 346 start, centre (37,4); rows are y, columns x; A head, a body (all ours here), b enemy body
       333435363738394041
       +-+-+-+-+-+-+-+-+-
    0   . .|* .|a a . . *
       +-+ +-+ + + + + +
    1   .|. . .|a a . . .
       +O+-+-+ + + + + +
    2  |* . .|.|a a . a .
       +-+ +O+ + + + + +
    3  O.|.|.|.|A a . A .        <- the A at (37,3) is our leader #61, 16 long; its body runs up column 37,
       + + + + + + + + +            down column 38 and ends at (41,6)
    4  |.|.|A a|. a . . .
       + + +-+-+ + + + +
    5  |.|AO. .|A a . . .        <- the A at (37,5) is #494, 2 long, moving north
       +O+-+-+ + + + + +
    6   b|. . .|a a a a a
  ```
  It cuts: 16 -> 2 + 14, the 14 go to `#499` with its head at the old tail, (41,6). `#494` steps into (37,4); in round
  347 the 2-long `#61` moves east into the child's body and dies. At round 350, 30 of our 50 dragons that ping still
  say `#61`, 16 long (it is dead); none says `#499`.
- Round 376: `#499` (15) cuts again with two free cells (15 -> 2 + 13, child `#568`). At round 400, 32 of 45 say `#499`
  at 15; it is 2 long and alive.
- Round 401, feeding begins by the clock. The first feeder, `#454` (3 long), dies at (46,14) four steps from `#346`, a
  9-long; its last ping said `#499`, 15 long, news 24 rounds old. The second, `#579` (2), dies at (24,3) next to a
  5-long; test4 eats its pearl. Round 404: the leader `#568` (14) cuts with two free cells (child `#606`, 12).
- Rounds 411-420: 24 dragons die by choice, 15 of them one to three steps from `#606`, 4 next to `#346` (12-16 long), 2
  next to an 8-10-long, 3 next to nothing. `#606` goes 12 -> 25 in those ten rounds and is 34 at round 427.
- Rounds 427, 432, 437: three cuts in ten rounds (34 -> 2 + 32, 33 -> 2 + 31, 33 -> 2 + 31; ids `#622`, `#627`, `#634`;
  one, none and one free cell). From round 421 to 452 seven dragons die by choice: two are the 2-long stubs the cuts
  left behind, the other five die next to a 5-long, a 13-long or nothing. The lineage gets no feeder pearl for 32 rounds
  while it is 31-34 long and has 13 own heads within 15 cells (round 450). At round 450, 9 of 21 still say `#606`, 34
  long; it has been dead since round 428.
- Round 453: four feeders die in one round and a fifth in 454, four of the five next to `#346` (21 long, our second
  longest, 2-7 cells from the leader), one next to the leader `#634` (31); of their 9 pearls the leader eats 4. The
  last ping of the four of round 453 said `#606`, 34 long, news 25 rounds old: the first round
  on which our code treats a leader record as expired (`SONAR_STALE 25`). Inference: they had been waiting for a dead
  34-long, and the 31-long next to them could not replace it in their record because 31 is less than 34.
- Six more leader cuts from round 477 to 499 (three with no free cell) take the longest from 39 to 32.
- test4: its queen runs into herself at round 326, 3 long. Feeding starts at round 350-353 next to its home: `#340`
  and `#511` (3 long) die at (4,22) and (2,19), two steps from `#450` (8 long). `#450`: 8 -> 34 (round 375) -> 58 (400)
  -> 82 (425); 36 feeders with 100 segments in rounds 350-399, 60 pearls, 44 eaten by `#450`; from round 357 to 399, 27
  of its 36 deaths by choice are one to three steps from `#450`. Units 50 -> 37 -> 16 -> 9. Its cuts come late (round 430,
  448, five in round 465, eight in round 491, one at 496) and cost it 94 -> 77 in the last ten rounds.
- Decided: between rounds 350 and 425. Final P 99 against 117, c 0.32 against 0.66; 27 units of ours left, 11 of
  theirs. test4 started 50 rounds earlier with its team already at home and fed one id for 80 rounds.

**2. 1044512, Maze, ladder 4 October (live bot), against WHQ. Lost 74 to 87.**
- WHQ (queen dead since round 244) has 62 units at round 250 and 56 at 275; its first feeders die at round 271 next to
  `#303` (7 long, at (39,9)), which reaches 20, cuts at round 297 with no free cell, and whose 18-long child `#517`
  dies without an order at (42,7) at round 298; its 9 pearls go to other WHQ dragons. At round 333 our 3-long `#595`
  rams WHQ's longest of the time (13) at (24,11) with a 2-step move and we eat its 7 pearls.
- WHQ's real feeding starts at round 351 into `#302`, 7 long at that moment and not the longest (that is `#618`, 11
  long, 20 cells away): 7 -> 12 (358) -> 23 (369) -> 33 (380) -> 52 (400, at (40,12)) -> 65 (425). From round 351 to
  410 sixty WHQ dragons die by choice, every one of them by giving no order (the same way ours do): 51 within three
  steps of a dragon twice their length, 44 of those next to `#302`, and 34 of the 60 at exactly three steps. Of their
  83 pearls the dragon they died next to eats 58, other WHQ dragons 24, we eat 1. The ground is open and the feeders
  stand in a ring:

  ```
  round 366 start, centre (42,9); B head, b body, all WHQ; no kelp in view
       383940414243444546
    5   . . b b . . B b .
    6   . . * b b b b . .
    7   . b B . * . b B .
    8   . b . * . B b b B        <- the B at (43,8) is #302, 18 long
    9   . B . B . . . b .        <- the B at (41,9) is #376 (2 long): gives no order this round and dies
   10   B b . b . . . . .
   11   b B . . . B b . B        <- the B at (43,11) is #198 (2 long): the same
   12   b . . . . b B . b
   13   B . b B . . . . .
  ```
  Thirteen small WHQ heads are in this 9 x 9 view; two die this round, each three cells from the leader's head, and it
  eats a pearl of an earlier feeder at (42,7). The dragon that is fed is cut once in the whole race (round 431, 66 -> 2
  + 64, no free cell). A 32-long second dragon dies without an order next to it at round 485 (12 of its 16 pearls
  eaten): 68 -> 87. 8 units at the end.
- We: our longest goes 4 -> 10 in the hundred rounds of the zone (4, 4, 7, 7, 10 at rounds 300-400, a different id at
  every sample). Feeding from round 401 is fast here: `#622` 10 -> 36 (425, at (8,17)) -> 56 (450) -> 71 (475). In
  rounds 400-449, 58 of our dragons die by choice: 41 within three steps of a dragon twice their length (38 of those
  next to the longest), 5 at four to eight steps, 12 next to nothing; of 77 pearls the dragon they died next to eats
  45, other own dragons 29. Cuts at rounds 458, 480, 485, 494, 499 (the last four with no free cell). 16 units left.
- Decided by the 50 rounds between the two starts: 10 against 52 at round 400, 56 against 68 at round 450. P 80:85 at
  round 300, 104:115 at the end; c 0.71 against 0.76. A race lost on potential and on the clock, not on scatter.

**3. 1063241, Maze, run qh31-test-old (live bot), against WHQ. Lost 81 to 87.**
- WHQ feeds from round 270 (first: two 2-longs at (4,16) and (3,17) next to `#340`, a 4-long). Early on it feeds
  whatever bigger dragon is near: of 56 deaths by choice in rounds 270-349, 51 are within three steps of a dragon twice
  as long but only 17 of those next to the team's longest; at round 325 it has two dragons of 14. Then one takes over:
  27 (350, `#690` at (2,14)) -> 39 (375); four cuts in rounds 382-407 (three with no free cell) hold it at 38-43; 53
  (450) -> 75 (475) -> 87. The end is made of middle-sized dragons: from round 451 to 466 five WHQ dragons of 5, 6, 7,
  9 and 18 long die without an order four to ten cells from the leader, and it eats 21 of their 24 pearls (the
  18-long, `#744`, at (4,23) at round 466: 8 of 9). 7 units at the end.
- We: the zone builds 18 by round 350 (`#669` at (37,6)); cuts at rounds 350 (no free cell) and 365 put it back to
  14-16. Feeding from round 401: 30 feeders in 25 rounds, `#740` 16 -> 48 (425, at (38,7)) -> 70 (450); one cut (round
  441, 62 -> 2 + 60). At round 450 we lead the race 70 to 53. Then it stops: one feeder in rounds 450-474; of our 9
  remaining dragons 3 are within 15 cells of the leader (12 segments; the team's median path distance to it is 26
  steps), the others do not come and grow instead (team total 101 -> 133, second longest 13). 78 against 75 at round
  475, final 81 against 87.
- Decided in the last 50 rounds: P 109 against 110, c 0.74 against 0.79. WHQ's middle-sized dragons died next to its
  leader; ours stood more than 15 cells away. Inference from our code: nothing brings them (`RALLY_FRESH 0`; a dragon
  only walks to the leader from within `FEEDER_APPROACH 15` cells).

**4. 1068052, Maze, run tc30-test-new (test build), against WHQ. Lost 66 to 94.**
- WHQ feeds from round 270 (first: `#244` and `#394`, 3 long, at (43,0) and (44,2) next to `#72`, 10 long) and has 24
  by round 298. That lineage then cuts three times in 13 rounds (rounds 298, 300, 310: 24 -> 22 -> 20 -> 18, two of
  them with no free cell), and at round 311 the 18-long `#609` has no free cell at (43,4) and dies; its 9 pearls go to
  other WHQ dragons. Rebuilt: 12 (350) -> 29 (375, `#595` at (45,12)) -> 30 (400, after a cut with no free cell) -> 47
  (425) -> 76 (450) -> 83; in rounds 350-449, 43 of its 64 deaths by choice are within three steps of the longest. A
  21-long, `#846`, dies without an order three steps from it at (44,14) at round 481 (10 of 11 pearls eaten): 94. 4
  units at the end, c 0.86.
- We: longest 4, 9, 9, 8, 10 at rounds 300-400. In the zone phase our longest dragon cuts itself nine times between
  rounds 337 and 406 at lengths of 9 to 12, seven of the nine with a free cell. From round 401: 28 feeders by round
  425; `#708`, 7 long at round 400 and not the longest, goes 7 -> 29 (425, at (4,22)) -> 62 (450, at (12,15)). Then
  nine cuts in 49 rounds (round 451 with two free cells, eight more with none): 62 -> 63 -> 66, while 16-18 dragons
  with 50-65 segments stand around, 4-6 of them within 15 cells; 17 die by choice in the last 50 rounds, 2 of them
  within three steps of the longest.
- Decided from round 425 on: 29 against 47, 62 against 76 at round 450, then +4 against +18. P 89:89 at round 400,
  101:109 at the end; c 0.65 against 0.86.

**5. 1058146, Maze, run passage2-test-old (live bot), against test4. Lost 49 to 56.**
- test4 does nothing until round 376 (its queen ran into herself at round 278): no death by choice in rounds 250-349.
  Then 37 in 24 rounds, every one by running into itself, 125 segments; the first at (39,11) and (39,5) next to a
  4-long, the third at (43,7) two steps from `#84` (7 long). `#84`: 7 (round 378) -> 36 at round 400 (at (38,8));
  units 55 -> 15 in 25 rounds. It stalls at 39 for 50 rounds; then a 31-long second dragon, `#706`, kills itself three
  cells from it at (45,14) at round 453 and the leader eats 13 of the 16 pearls: 51 by round 459, 55, 56. 10 units at
  the end, 56 / 27 / 17.
- We: `#547` 5 (350) -> 9 (375) -> 13 at round 400 (at (9,17)) -> 40 at round 425 (at (1,21)): 30 deaths by choice in
  rounds 400-424, 20 of them within three steps of it. Cuts at rounds 445, 447, 452, 465, 493, 497 (three with no free
  cell): 48 -> 44 -> 41 -> 49. For those 75 rounds 23-26 of our dragons with 57-94 segments stand by, and they do die:
  39 deaths by choice in rounds 425-499 (104 segments, 57 pearls), but 20 of the 39 next to nothing and 8 next to the
  longest; the dragon they died next to eats 17 pearls, other own dragons 24, test4 5, nobody 8. An 18-long of ours
  dies without an order next to the leader at round 485 (5 of 9 pearls eaten).
- Decided after round 425: we had the higher potential at round 400 (83 against 73) and at round 425 the longer
  dragon (40 against 39). Final c 0.55 against 0.54: both sides scattered; they merged one big dragon into the leader
  and we fed the floor.

**6. 1027971, Portals, run stride-old (live bot, sonar readable), against WHQ. Lost 19 to 30.**
- Round 390: our leader `#500` is 10 long, 16 of our 17 other dragons believe it, 11 of them (30 segments) are within
  15 cells and short enough to feed it. Everything is ready.
- Round 400, one round before feeding starts: `#500` (13) stands at (20,5) with kelp on its west side, its own body
  south, and two free cells, north (20,4) and east (21,5); a 2-long of ours, `#694`, is next to it at (21,4):

  ```
  round 400 start, centre (20,5); A head, a body, all ours; * pearl, | - kelp, O portal
       161718192021222324
       + + + + + + +-+-+
    3  |. . . a a a|* *|.
       + + +-+-+ + +-+-+
    4  |. .|* *|. A aOa a        <- the A at (21,4) is #694, 2 long
       + + +-+-+ + + + +
    5  |. .|* *|A . . A .        <- the A at (20,5) is our leader #500, 13 long; the A at (23,5) is #678, 3 long
       + + +-+-+ + +-+-+
    6  |. . .O. a .|*O*|a
       +-+ + + + + + + +
    7   *|. . . a .|* *|a
  ```
  It cuts: 13 -> 2 + 11 (child `#696`, head at (24,11)). At round 401 `#694` steps to (21,5) and gives the feeder order
  there, next to a leader that is now 2 long; its pearl goes to `#605`, a 9-long eight steps away. `#696` cuts again at
  round 404 (12 -> 2 + 10, one free cell). At rounds 410 and 420, 12 of 13 and 11 of 14 of our dragons still say `#500`,
  13 long (it is 2); by our rules none of them can feed anybody. At round 430 seven of 13 say the new longest, `#605`,
  and it goes 15 -> 23 in ten rounds (seven feeders die one or two steps from it in rounds 426-440, one of them an
  8-long). At round 440 we lead the race 23 to 21.
- Round 449: `#605` (25) cuts with one free cell. At rounds 450, 460 and 470 the team says `#605`, 25 long (it is 2
  long, then dead: 12 of 13, 9 of 9, 12 of 12 pinging dragons); the new ids cut four more times (rounds 456, 460, 467,
  474: 23 -> 17; three of the four with a free cell). Round 480: seven of 11 say `#747` (20); it cuts at 482 and its
  child at 489, both with two free cells; at round 490, 11 of 12 say `#747`, 23 long, and it is 3.
- Our deaths by choice from round 400: 35 (96 segments, 53 pearls). 19 are within three steps of a dragon twice their
  length, 11 of those next to the longest; the dragon they died next to eats 22 pearls, other own dragons 23.
- WHQ's first steady feeders die at round 414-420 ((11,5), (10,7), (7,2), two or three steps from `#707`, 9-13 long)
  with 15 units on the board; `#707` goes 9 -> 24 by round 458 and is cut once (round 459, no free cell). Its last two
  dragons of 9 and 10 die without an order next to the leader at rounds 461 and 497. One dragon of 30 at the end.
- Decided after round 440. P 39 against 34 at round 400, 40 against 30 at the end; c 0.47 against 1.00. At ten
  samples from round 400 to 490, at least half of our dragons named the true longest at four (rounds 400, 430, 440,
  480) and not one of them did at the other six.

**7. 1045202, Portals, ladder 4 October (live bot), against test4. Lost 28 to 41.**
- test4 (queen dead since round 83) has the higher potential before anybody feeds: P 58 against 43 at round 300, 57
  against 46 at rounds 350 and 375. It feeds from round 321 (first: `#537`, 3 long, at (26,2), three steps from the
  7-long `#676`), slowly at first: 29 deaths by choice in rounds 300-399, all but one by running into itself, 17 of
  them within three steps of its longest. `#870`: 7 (375) -> 20 (400, at (25,7)) -> 32 (425) -> 38 (450) -> 41; one cut
  (round 430) and one odd split at round 472 (44 into 35 + 9; the 9-long kills itself eight rounds later). 12 units
  at round 400, 3 at round 425 and at the end.
- We: the zone leader is 13 at rounds 350-375 (`#851`, then `#1008`, both at (7,7)) through six leader cuts between
  rounds 322 and 376, and 10 at round 400 (`#1017` at (5,8)). Potential at round 400: 44 against 46, level; longest 10
  against 20. Then our feeding burst loses potential instead of converting it: P 44 -> 29 between rounds 400 and 425
  while the longest stays at 10 (cuts at rounds 402, 409, 422). In the last hundred rounds 35 of our dragons die by
  choice (100 segments, 55 pearls): 22 within three steps of a dragon twice their length, but only 8 of those next to
  the longest; the dragon they died next to eats 21 pearls, the longest 10 more, other own dragons 17, nobody 7. A
  pearl eaten by a dragon that is not the leader is halved again when that dragon dies. Then 16 (450), 21 (475), 28;
  4 units at the end.
- Decided between rounds 375 and 425. Final P 33 against 54, c 0.85 against 0.76: we finished cleaner than test4 and
  lost on the potential we had burnt.

**8. 1058858, Portals, run passage2-test-new (test build), against test4. Lost 22 to 37.**
- test4 (queen dead since round 49) feeds a little from round 316 and ends as one dragon: 12 (300) -> 17 (350) -> 23
  (400, `#956` at (31,10)) -> 24 (425) -> 27 (450); an 18-long, `#987`, kills itself two cells from the leader at
  (21,4) at round 455 and the leader eats all 9 pearls: 36 at round 475, 37 at the end, alone on the board from
  round 457.
- We: 15 at round 400 (`#936` at (6,4)), cuts at 405 and 412, 16 at 425, 31 at 450 (`#981` at (10,3)): at round 450 we
  lead the race 31 to 27. In rounds 400-449, 16 of our dragons die by choice, 14 of them within three steps of a
  dragon twice their length, and 18 more (43 segments) die boxed in: P 50 -> 36 -> 40.
- Round 478. We have three dragons: the leader `#990` (35), `#988` (12) and `#981` (9); test4 has one of 36. Our
  potential is 46 against 36. The leader has come down a one-cell-wide column eating natural pearls at (15,3) and
  (15,5); ahead of it are one free cell and a two-cell pearl pocket:

  ```
  round 478 start; A head, a body, all ours; * pearl, | - kelp, O portal
        4 5 6 7 8 910111213141516
       +-+-+-+-+-+-+-+-+-+-+-+-+-
    0   a a a a|* *|. . . a a a|.
       + + + + + + + + + + + + +
    1   aO. . a|*O*|a a a a .|a|.
       +-+-+ + +-+-+ + +-+-+ + +
    2  |*O*|. a aOa a .|* *|.|a|.
       +-+-+ + + + + + +-+-+ + +
    3  |* *|. . a a . .|*O*|.|a|.
       +-+-+ + +-+-+ + +-+-+ + +
    4   a a a .|* *|a a . . .|a|.
       + + + + +-+-+ + + + + + +
    5   a a a A|*O*|. a aOA .|A|.     <- A at (15,5): the leader #990, 35 long; its tail end is at (6,4)
       +-+-+ + +-+-+ + +-+-+ + +         A at (7,5): #988, 12 long; A at (13,5): #981, 9 long
    6  |* *|. a .O. . .|* *|.|.|.
       +O+ + + + + + + + + + + +-
    7  |* *|a a . . . .|*O*|.|* *
  ```
  It cuts, 35 -> 2 + 33, and the child's head appears at the old tail, (6,4). The child cuts at once, 33 -> 2 + 31,
  and its child appears at (15,3); and so on, six cuts in the same round with the head jumping between the two ends
  ((6,4), (15,3), (5,5), (15,1), (4,4), (14,0)): 35 -> 23 in one round, six 2-long stubs left behind. The enemy's only
  dragon is at (27,2), twelve columns away.
- After that: one more cut at round 493 (24 -> 2 + 22); the 12-long splits itself at round 479; in rounds 450-499 nine
  of our dragons die by choice, two of them within three steps of a dragon twice their length, and of their 22 pearls
  the dragon they died next to eats 1, other own dragons 10, nobody 11. Final 22, P 28.
- Decided at round 478, by our own leader. P 50:52 at round 400; c 0.79 against 1.00.

**9. 1063251, Portals, run qh31-test-old (live bot), against WHQ. Lost 9 to 37.** The extreme case. From round 395 to
499 our longest dragon cuts itself 19 times, about every five rounds, at lengths of 9 to 16, and 15 of the 19 times it
has a free cell (two free cells in nine of them). Longest at rounds 400 / 425 / 450 / 475 / end: 10, 16, 9, 9, 9; we
end with dragons of 9, 9 and 8 and 13 units. In those hundred rounds 39 of our dragons die by choice (100 segments, 55
pearls): 27 within three steps of a dragon twice their length, but that dragon is the team's longest for only 8;
whichever dragon they died next to eats 23 pearls, other own dragons 25. WHQ's queen is its leader until she is cut at
round 341 (15 long, no free cell) and dies a round later; it starts feeding at round 364 ((11,5), one step from
`#644`, 5 long) and feeds that one id to the end with no cut at all: 9 (375) -> 11 (400) -> 22 (425) -> 32 (450) -> 37;
of its 23 feeders 13 die within three steps of it and it eats 34 of their 47 pearls. 2 units at the end. P 44 against
40 at round 400 and 48 against 42 at round 425 in our favour; final P 36 against 39; c 0.25 against 0.95.

**10. 1063682, Portals, run qh31-test-new (test build), against test4. Lost 16 to 33.**
- test4 (queen dead since round 134) feeds from round 293 and has a leader of 26 by round 368 (`#461`). That leader
  is no model either: it is cut with no free cell at (5,10), and the 24-long child then stands still at (21,6) for six
  rounds and sheds a 2-long piece of tail in each of them (24 -> 12 by round 374; `story.py track 1063682 461,902 1`).
  Rebuilt: 11 (400) -> 16 (425) -> 30 (450) -> 28 (475) -> 33; 2 units at the end (33 and 13).
- We: 14 at round 325 (`#725`), then twelve leader cuts between rounds 337 and 409 at lengths of 9 to 16 (ten of them
  with a free cell) and a longest of 10, 8, 9 at rounds 350 / 375 / 400. Feeding from round 412: `#854` 15 (425) -> 20
  (430) -> 23 (435), against test4's 16, 18 and 24 at those rounds. Then cuts at rounds 436, 438, 450, 457, 467, 487, 491 (23 ->
  21 -> 19 -> 17, 18 -> 16, 20 -> 18 -> 16 -> 14; five of the seven with a free cell). In the last hundred rounds 44 of our
  dragons die by choice (116 segments, 64 pearls): 25 within three steps of a dragon twice their length, 12 of those
  next to the longest; the dragon they died next to eats 24 pearls, other own dragons 35. 9 units at the end.
- P 52:51 at round 400, 36:40 at the end; c 0.44 against 0.82.

**11. 1029033, weakhold, run stride-new (test build), against WHQ. Lost 4 to 26.** Not a feeding story until the end.
At round 300 we have 27 units and 65 total length against 13 and 34 (P 39:22). From the zone switch on our team stops
eating: 40 natural pearls in rounds 250-299, then 16, 9 and 3 per 50 rounds (WHQ: 34, 27, 24, 24) while 15-20 of our
dragons a block still die boxed in; total 65 -> 44 by round 400 and P 39 -> 30, while WHQ's P goes 22 -> 29. Our
leader `#311` goes 9 (350) -> 13 (375) -> 14 (400, at (23,13)) -> 17, cuts at round 409 with two free cells (17 -> 2 +
15), its children cut at 418 and 436, and the heir `#397` (14) is rammed at (16,6) at round 448 by a 3-long with a
2-step move. Five rounds earlier our 8-long `#384` had rammed WHQ's 16-long leader at (17,6) after a 7-step sprint;
WHQ's own dragons ate all 8 pearls and it rebuilt to 28 in 30 rounds (then cut itself to 26 with two free cells at
round 475). 5 units and 12 segments left to us at round 450; WHQ ends with 26, 18 and 17.

**12. 1045374, weakhold, ladder 4 October (live bot), against WHQ. Lost 25 to 31.** At round 300: 41 units and 94
total against 19 and 43 (P 54:24). Then the same starvation: 47 natural pearls in rounds 250-299, 26, and 4 in rounds
350-399; total 94 -> 59 by round 400 (P 39:21). The leader `#194` is 12 at round 350 and 14 at rounds 375 and 400, at
(21-23,13-14); the rest of the team is a median 42-44 path steps away from it (the map is a ring of corridors).
Feeding from round 406 is blind: of 28 deaths by choice from round 400 to the end (74 segments, 40 pearls), 21 are next
to no dragon twice their length at all (at (11,14), (9,0), (12,0), (16,5), (13,14) ... with the longest 9 to 23 cells
away), 5 are within three steps of one and 3 of those next to the longest; the dragon they died next to eats 4
pearls, the longest 2 more, other own dragons 23, nobody 9. The leader still reaches 24 by round 450 (`#381` at
(24,1), 10 natural pearls), level with WHQ's 25. Then it cuts itself four times in 15 rounds (455, 462, 465, 469: 24
-> 16), every time with a free cell, as it had three times at rounds 417-425. Final 25 and 14. WHQ is down to 8 units
at round 375, feeds one dragon from round 353 (4 -> 17 by 400; 11 feeders, all one or two steps from it, 13 of 13
pearls eaten by it), is a single dragon of 34 by round 475 and ends 31 after two cuts with no free cell. c 0.68
against 0.97.

**13. 1058363, weakhold, run passage2-test-old (live bot), against WHQ. Lost 16 to 18.** P 41 against 23 from round
300 to 400 (33 units against 16). Leader `#328`: 10 (350) -> 13 (400, at (23,12)) -> 17 (425); it cuts twice at rounds
436-437 (20 -> 18 -> 16, with one and two free cells) and the heir `#432` (16) is rammed at (18,6) at round 439 by a
2-long with a 2-step move; WHQ eats 6 of the 8 pearls. One round earlier a 9-long of ours had killed itself at (18,5),
three cells from a WHQ 2-long. Total 64 -> 46 -> 20 between rounds 400 and 450. Of our 14 deaths by choice from round
400 on, none is within three steps of the longest and 8 are next to nothing. A new leader, `#378`, then goes from 3 to
20 in under 20 rounds (round 469), ahead of WHQ's 17, and cuts itself three times in the last 31 rounds (469, 475,
480: 20 -> 18, 19 -> 17, 17 -> 15; the first two with a free cell). 16 at the end against 18: the three cuts cost 6.
WHQ ends with two dragons of 18 and 17; its own leader was cut four times after round 400, every time with no free
cell. In two of these three weakhold games (11 and 13) three leaders died by a ram in the same passage, (16-18,6).

**14. 1029032, Slithery Fight (1,701 cells), run stride-new (test build), against WHQ. Lost 82 to 113.**
- We feed from round 201 (56 units). `#929`: 21 (250, at (9,7)) -> 34 -> 47 (300, at (0,24)). Then nothing for 100
  rounds: 47, 51, 52, 49 at rounds 325-400 through seven ids. Two things happen in those hundred rounds. The leader
  cuts itself six times (rounds 308, 344, 351, 364, 385, 394; four with a free cell): 12 segments. And of 43 deaths by
  choice (110 segments, 60 pearls) 23 are within three steps of a dragon twice their length but only 8 of those next
  to the longest; the dragon they died next to eats 24 pearls, other own dragons 36. From round 400: 61 feeders in 50
  rounds (160 segments, 86 pearls, 55 eaten by the dragon they died next to), 53 (425) -> 67 (450) -> 79 (475); cuts at
  405, 472 and 494; 82. Even then the dragon next to the feeder is the longest in only 20 of 61 cases from round 400
  on; three own dragons of 14, 26 and 14 die without an order (rounds 404, 460, 477) and the leader eats 3 of their 27
  pearls. 23 units and 189 segments at the end.
- WHQ's queen is its leader until round 248 (23 long; cut, and she dies a round later). The child `#942` is the same id
  from round 250 to the end with no cut: 21 -> 37 (300) -> 62 (350) -> 93 (400, at (52,10)) -> 106 (450) -> 113. From
  round 250 to 399, 115 WHQ dragons die by choice, all without an order, 102 of them within three steps of a dragon
  twice their length (49 of those next to the longest), and the dragon they died next to eats 143 of 189 pearls. A
  second WHQ dragon grows to 70 and dies without an order at (59,11) at round 495, six cells from our leader's head;
  none of its 35 pearls is eaten by anybody in the last five rounds.
- Decided between rounds 300 and 400: P 138:154, 152:154, and 140:122 at the end in our favour; c 0.59 against 0.93.

### Four level races we won

**15. 1023828, Maze, ladder 4 October (live bot, sonar readable), against forgot. Won 92 to 84.** The control case.
Our leader `#265` keeps its id from round 325 to 475: 8 (325, at (1,22)) -> 13 -> 20 -> 25 (400, at (9,21)) -> 47 (425)
-> 77 (450) -> 91 (475); one cut after round 395. Share of our dragons that believe it: 35 of 51 at round 325, 35 of 40
at 350, 32 of 45 at 375, 28 of 42 at 400; 23-30 dragons with 52-76 segments could feed it at every sample. From round
401: 40 feeders in 50 rounds (93 segments, 52 pearls: 37 eaten by it, 9 by other own dragons, 6 by nobody); all 30
that die within three steps of a dragon twice their length die next to the longest. 6 units at the end, c 0.84.
forgot starts at round 364 ((41,8) and (39,5), two and three steps from `#289`, 6 long): 20 at 375, 51 at 400 (at
(38,10)), and then four cuts, three of them with no free cell (rounds 408, 429, 471, 491); 84 at the end with dragons
of 27 and 25 beside it, c 0.70. We had less potential all game (80:97 at round 300, 85:92 at 400, 110:120 at the end)
and won on completeness. This is what our feeding looks like when the leader keeps its id.

**16. 1053031, Portals, ladder 4 October (live bot), against WHQ. Won 42 to 33.** P 41:42 at round 400. Ours: 10 (400,
`#662` at (24,11)) -> 21 (425) -> 21 (450) -> 31 (475) -> 42 through five cuts (rounds 421, 434, 441, 469, 478; three
with two or three free cells; they cost 10); 13 feeders in the last 50 rounds, 17 of their 21 pearls eaten by the
dragon they died next to; 3 units at the end, c 0.89. WHQ (queen dead at round 276) feeds slowly from round 374, has
12, 16 and 22 at rounds 400 / 425 / 450, merges its last two dragons of 13 and 11 at rounds 462 and 468 and is a
single dragon of 32 by round 475 with nothing left to eat: 33. We won with the cuts because WHQ had run out of
material (P 39 against 34 at round 450).

**17. 1063672, Maze, run qh31-test-new (test build), against test4. Won 76 to 64.** test4 feeds from round 318 and
builds `#485` to 30 by round 400 (at (35,10)). At round 405 that leader cuts with two free cells, and a round later
the 28-long child has no free cell at (39,5) and dies (14 pearls: 12 to other test4 dragons, 2 to us); with it and
ten other boxed-in deaths test4 loses 54 segments in rounds 400-449 (P 77 -> 50). `#604` then goes 31 -> 46 -> 64 and
stops there, with 3 units left. Ours: longest 4, 5, 5, 7 at rounds 300-375 and 16 at round 400 (`#690` at (6,19)).
From round 401: 37 feeders in 50 rounds, but spread: `#690` reaches 29, cuts at 422, its children at 428 and 449
(27, 28 at rounds 425 / 450), and meanwhile another dragon, `#221`, 3 long at round 400, is fed to 22 by round 450
and 58 by round 475 (at (3,22)); it wins the race with 76 while the first lineage ends at 30. Of 71 deaths by choice
from round 400 on, 43 are within three steps of a dragon twice their length and 24 of those next to the longest. 8
units at the end, c 0.72 against 0.88; P 86 against 77 at round 400.

**18. 1067916, Portals, run tc30-test-new (test build), against test4. Won 49 to 44.** P 39:39 at round 400. Ours: 12
(350) -> 17 (375) -> 20 (400, `#964` at (10,8)) through three cuts with a free cell (rounds 378, 384, 399), one more at
round 420 (32 -> 2 + 30), and then `#972` keeps its id for the last 80 rounds: 31 (425) -> 44 (450) -> 47 -> 49. Of
14 deaths by choice from round 400 on, 11 are within three steps of a dragon twice their length and 10 of those next
to the longest. 3 units at the end, c 0.92. test4 feeds from round 320: 23 (400) -> 35 -> 39 -> 44, one cut (round 417,
no free cell), a single dragon by round 475 with nothing left.

### Four big-map races we won from behind

**19. 1053032, Slithery Fight, ladder 4 October (live bot), against WHQ. Won 92 to 50** with P 113 against 159 at
round 400. We feed from round 202 (26 feeders by 250, `#369` 24 long), lose that leader to a ram at round 266 (27
long, hit at (31,10) by a 5-long with a 5-step move; WHQ eats 9 of its 14 pearls), cut the next ones five times
between rounds 308 and 379 and hold 21, 19, 21 at rounds 350 / 375 / 400. Then `#1476` keeps its id for the 50 rounds
that matter: 21 -> 42 (425) -> 72 (450); 42 deaths by choice in those rounds, 39 within three steps of a dragon twice
their length, 35 of those next to the longest; 48 of 71 feeder pearls eaten by it. One cut at round 450 with three
free cells (72 -> 2 + 70), then 79, 92. WHQ feeds from round 270 and has 55 at round 400, but in several dragons: of
121 WHQ deaths within three steps of a bigger dragon only 32 are next to its longest; its leader is cut seven times
after round 380, every time with no free cell; a 34-long and a 36-long die at rounds 465 and 492 with 7 of their 35
pearls reaching the leader; and at round 498 our 10-long `#1716` rams its 63-long leader at (43,11) with a 5-step
move. It ends with 50, 40 and 26. c 0.76 against 0.47.

**20. 1059086, Slithery Fight, run passage2-test-new (test build), against WHQ. Won 82 to 41** with P 104 against 157
at round 400. Ours: 15-22 from round 200 to 400 through seven ids (51-54 units, so this build does not feed before
round 400); then `#1333` keeps its id for the last hundred rounds: 16 -> 36 (425) -> 56 (450) -> 66 -> 82, with 30 and
32 feeders per 50 rounds and 71 of their 95 pearls eaten by it. WHQ feeds from round 271 but into many dragons (of 133
deaths within three steps of a bigger dragon, 22 are next to its longest) and has 50 / 40 / 35 at round 400. Then it
loses them one by one: a 40-long is rammed at (30,8) at round 403 by our 6-long `#1178` with a 5-step move (we eat 17
of its 20 pearls), a 23-long by our 11-long at round 435, and three of its own big dragons die without an order
(30 long at round 402, 32 at 418, and at round 472 its 65-long leader at (38,23), one round after its third cut with
no free cell in 20 rounds; another WHQ dragon eats 29 of the 33 pearls). 67 at round 450, 39 at 475, and 41, 36 and 34
at the end with 220 segments on the board. c 0.70 against 0.31.

**21. 1053383, Around UNSW (4,096 cells), ladder 4 October (live bot), against test4. Won 96 to 49** with total length
256 against 382 at round 400. We have 60 units at round 200 and 52-56 after that; the first feeders die at round 204
((3,16) and (1,17), three steps from `#329`, 13-14 long). That leader cuts at round 252 with three free cells; the
next one, `#188`, keeps its id from before round 300 to round 438 and grows about 20 per 50 rounds: 31 (300, at
(46,15)) -> 53 -> 71 (400) -> 85 -> 96, fed by 15-25 feeders per 50 rounds; its natural pearls: 0-11 per 50 rounds.
test4's queen dies at round 348; its longest dragon (23) is rammed at (11,1) at round 401 by our 13-long `#494` with
a 5-step move; its first feeders die at round 427. 49 at the end with 27 units and 308 segments unused. c 0.48
against 0.27.

**22. 1063675, Around UNSW, run qh31-test-new (test build), against test4. Won 69 to 49** with total 206 against 406
at round 400. Ours: 17 (200) -> 22 -> 21 -> 28 -> 45 (400, `#655` at (53,20)) -> 42 -> 69, through 13 leader cuts from
round 250 on, 11 of them with a free cell (five between rounds 405 and 444 hold it at 42-46 for 50 rounds). test4
(queen dead at round 362) has a longest of 16-27 until round 450, loses two leaders boxed in (28 long at round 263, 23
at round 425), starts feeding at round 438 and ends with 49, 32 and 27, 40 units and 397 segments. c 0.49 against
0.21.

In all four the opponent threw the race away (test4 by waiting for its queen and then having no leader, WHQ by ending
with three leaders and losing others to our rams and to deaths without an order). In three of the four our leader had
50 or more rounds with one id while feeders died next to it; in the fourth (22) it cut itself 13 times and won
because test4 was worse.

### Eight top-team wins of level races on small maps

**23. 1046530, Portals, SSS against test4. SSS won 56 to 24.** SSS's queen dies at round 285; its first feeders die
at round 306-307 ((20,3), (21,3), (21,4), one or two steps from `#617`, 7-8 long): 9 feeders by round 325 (`#617` 6 ->
15). That leader cuts twice with free cells (rounds 341 and 346), and then `#770` is one id from round 346 to the end
with no cut: 18 (350) -> 28 -> 40 (400, at (21,11)) -> 47 -> 49 -> 56. From round 300 on 51 SSS dragons die by choice
(120 segments, 62 pearls): every one of them within three steps of a dragon twice its length, 36 of the 51 at one
step, 48 next to the longest; it eats 53 of the 62 pearls (85%). A steady 3-12 per 25 rounds, never a burst. 2 units
at the end, c 0.97. test4 feeds from round 320 and has 35 at round 400; that leader, `#723`, has no free cell at
(27,8) at round 400 with an SSS 2-long on the next cell and dies (16 of its 18 pearls go to other test4 dragons);
test4 ends as one dragon of 24.

**24. 1054770, Maze, SSS against test4. SSS won 80 to 52.** SSS (queen dead at 207) starts at round 301 ((38,8),
(38,9), (38,11), one or two steps from `#349`, 5-10 long): 20 feeders in 25 rounds and 22 in the next, `#349` 8 -> 24
(325) -> 45 (350, at (35,8)). It cuts at round 360 with a free cell (46 -> 2 + 44) and no feeder dies for the next 15
rounds; then the child `#663` is one id to round 496: 44 (375) -> 55 (400) -> 70 -> 79 -> 79. Of 76 deaths by choice
from round 300, 73 are within three steps of a dragon twice their length (41 at one step) and 67 next to the longest.
7 units at the end, c 0.82. test4 starts at round 383 (25 at 400, 51 at 425, 64 at 475) and ends 52 with dragons of 19
and 15.

**25. 1051292, Maze, SSS against forgot. SSS won 92 to 73.** SSS starts at round 318 ((46,21) and (45,21), one and two
steps from `#569`, 5 long): `#569` 11 (325, at (42,18)) -> 29 -> 41 -> 54 (400) -> 57, the same id for 110 rounds, 9-22
feeders per 25 rounds until round 400; two cuts with free cells (rounds 431 and 463), 73 (450), 75 (475), 92. Of 91
deaths by choice from round 300, 87 are within three steps of a bigger dragon (54 at one step), 76 next to the
longest. c 0.76. forgot starts at round 369: 11 (375) -> 29 (400) -> 31 -> 57 (450) -> 69 -> 73, four cuts with no free
cell; c 0.65. P 111:94 at round 300, 84:87 at 400 (SSS has spent more by then), 121:113 at the end.

**26. 1069890, Maze, Vibing++ against WHQ. Vibing++ won on total length, longest 77 to 77.** Vibing++ (queen dead at
344) does not feed until round 400: longest 12-16, and that longest cuts itself eleven times between rounds 305 and
386 at 14-16 long, ten of the eleven with a free cell (the same habit as ours; it costs them 2 segments each time and
nothing else, because nobody is feeding yet). First feeders at round 400-401 ((46,6), (42,7), (43,6), three steps
from `#966`, 9-10 long). Then 20 feeders in 25 rounds and a leader that eats on the move (22 natural pearls in rounds
400-449): 13 -> 47 (425, at (37,18)) -> 71 (450) -> 77, one id from round 400 to 468. In rounds 400-449, 50 Vibing++
dragons (116 segments) die boxed in, and no feeder by the test used here dies between rounds 425 and 449 while the
leader goes from 47 to 71 (what it eats then are natural pearls and the pearls of boxed-in team-mates). It ends with 18 units and 166
segments, c 0.62. WHQ feeds from round 272, has 46 at round 400 and 79 at 450, cuts five times with no free cell in
rounds 462-483 (82 -> 76) and ends 77 with a second dragon of 42 unmerged, c 0.68. Neither side finished.

**27. 1055103, Maze, Vibing++ against Quaker Qubits. Vibing++ won 51 to 21.** Before feeding, Vibing++'s longest cuts
itself 19 times between rounds 302 and 399 at 8-15 long (12 with a free cell) and is 7 at round 400. First feeders at
round 403: 7 -> 25 (425, at (10,11)) -> 31 -> 38 -> 51 through three more cuts, with 18 units and 129 segments left
(c 0.54). Quaker Qubits does not feed before round 485: longest 21, 15 units. A win on having a leader at all.

**28. 1061101, weakhold, Vibing++ against horse. Vibing++ won 30 to 19.** Vibing++ (11-20 units, P 20-29) starts at
round 430 ((14,11), two steps from `#456`, 11 long): `#456` 7 (400, at (24,13)) -> 11 -> 23 (450) -> 25 -> 30, one id
and no cut for the last hundred rounds; 3 units at the end, c 0.81. horse feeds its queen from round 307; she is cut
at round 359 (17 long, no free cell) and dies a round later; its later leader is cut 22 more times (12 with no free
cell), seven of them between rounds 485 and 496: 35 -> 19.

**29. 1046978, Queen Of Spades (875 cells), forgot against test4. forgot won 27 to 12.** Two small teams (8-16 units).
forgot starts at round 370: 7 (375) -> 13 (400); that leader is rammed at (20,31) at round 409 by a 4-long with a
2-step move; another dragon goes 10 (425) -> 17 -> 23 -> 27, 3 units at the end, c 0.87. test4 ends with two dragons of
12 and 11 that never merge.

**30. 1058793, Portals, forgot against Kamikaze. forgot won 54 to 44.** forgot starts at round 370 with 37 units: 10
(375, at (11,0)) -> 32 (400) -> 40 -> 41 -> 55 -> 54 through seven cuts after round 400, all with no free cell; 4 units
at the end, c 0.89. Kamikaze starts about ten rounds earlier (15 at 375, 30 at 400) and stalls at 31-36 for 75 rounds
with 5-10 units standing by; 44 at the end.

What the eight have in common: in the 50-100 rounds in which the race is made, the dragon that is fed either keeps its
id (SSS in all three games, Vibing++ in all three) or is cut only when it has no free cell (forgot); the feeders die
one to three steps from that dragon (SSS: at one step, two times in three); and SSS and forgot end with 2-7 units.
Vibing++ does not finish (18 units left in two of three games) and wins anyway. What they do not have in common is the
start: round 301-318 for SSS, 370 for forgot, 400-430 for Vibing++.
