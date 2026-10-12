# Close read of SSS (team 91) and "forgot to mention" (team 264), and a three-team comparison (sub-session A2)

Written 2026-10-05 for team meow (1119).

This file is the cross-check of `deep-read.md`, in which sub-session A read 15 games of Vibing++ (team 306, rank 1). The study's rule:
what all three top teams do is probably a real winning factor, what only one does may be a quirk. So the same questions are asked
here of the two other top teams, SSS and forgot, which beat Vibing++ about as often as they lose to it (SSS 34 wins and 39 losses
against Vibing++, forgot 48 and 58; SSS 35 and 29 against forgot; Schooltime left out).

How it was read. 15 games, 8 of them SSS against forgot and read from both sides, so 10 games for SSS and 13 for forgot. Every game
with `b_pack.py` (one page per team: opening, queen, every close approach to the queen, queen kills with the killer's track,
followers, ram chances, deaths of long dragons, feeding), `b_open.py` (economy per 10 rounds), the lead's `digest.py`, and then
`story.py events`, `story.py view` and `b_turn.py` on the rounds that mattered. Counts over the 15 games are from `b_tally.py`;
counts over all games of a team are from `b_chance*.py`, `b_feed.py`, `b_qsplit.py`, `b_qdeath.py` and `b_cand.py`. All outputs
are in `b_out/`. A replay shows positions, actions, deaths, pearls and sonar rays. It does not show what a bot intended, remembered
or knew; such sentences are marked "inference".

Words used. **Queen**: each team's lowest-id dragon; the longer living queen wins at round 500. **Ram**: a head moves into another
head, both die. **Reach**: the most steps a dragon can take in one turn (1, 2, 3, 5, 6 for lengths 2, 3, 4, 5, 6). **In view**: inside
the 7x7 square around a dragon's head. **Free steps**: the ceil(L/4) steps a turn that cost nothing; each further step costs one
segment ("paid"). **d4**: 4 steps along the shortest path that respects kelp, wrap and portals (bodies ignored). `#44` is a dragon id.
**Non-ram death**: any death that is not a head-on; the replay gives the reason as `noaction` (no legal order carried out, or the
suicide order), `self` (moved into its own body), `body` (moved into another body) or `wall` (moved into kelp).
**Boxed in**: no free cell next to the head at the start of the dragon's turn. **Mother split**: a 4-long queen splits 4 -> 2+2 and
so makes a new dragon. **Follower**: a small dragon that keeps the enemy queen in its view round after round.

## The three findings that matter most

1. **The one thing all three teams do to the enemy queen: a 2-3-long that has her in its view and within its reach rams her, every
   time.** Vibing++ 186 of 186 such turns, SSS 155 of 155, forgot 136 of 139 from round 100 on. Everything beyond that differs.
   Vibing++ and SSS also ram with dragons of any length at any price (80 of 81 and 95 of 99). forgot does not: its 4-longs split
   instead (12 of 53 taken), its 5-9-longs mostly walk past (21 of 65), its 10-12-longs always do (0 of 22), and before round 100
   even its 2-3-longs hold back unless they are not outnumbered where they stand (47 of 51 against 38 of 127). None of the three
   rams a queen that is outside the attacker's own 7x7 view, although SSS broadcasts her position to the whole team by sonar
   (her cell is in 26-39% of all SSS pings while she is known); in 1067636 that limit cost SSS a game it could have won with one move.
2. **A queen survives because of where she lives, not because of what happens when an enemy arrives.** SSS's queen is dead by round
   100 in 8% of its large-map games and 7% of its medium ones; forgot's in 30% and 20%. Both queens are 2-3 long and both step away
   from a close enemy one cell at a time; neither team guards her (in close rounds SSS's dragons moved nearer to the intruder 40
   times and further 44 times). The difference: SSS's queen eats less than half of what an average SSS dragon eats (2.1 against 4.7
   natural pearls per 100 rounds, in 10 of 10 games) and stays 11 cells from her spawn while her team is 17 cells out, so she has
   0.65 times the enemy heads near her that an average SSS dragon has. forgot's queen walks out alone in the opening and is rammed
   before round 60 in 19 of its 44 Around UNSW games. What still kills a well-placed queen is what she cannot see or cannot leave:
   a sprint by a dragon of 5 or more (4 of the 11 queen kills read), a corridor end, a portal exit, and for a 2-3-long queen any
   cell with no way out (she dies that way in 10% of SSS's games and 11% of forgot's; 23% for Vibing++, 28% for us).
3. **The end game is decided by which dragon is fed, from when, and with how much of the team, and the three teams run three
   different clocks.** forgot feeds its queen from about round 200-225 whatever the enemy does (8 or longer by round 300 in 175 of
   189 games) and wins 52 of the 71 games in which both queens live to round 500. SSS keeps its queen 2-3 long, feeds a separate
   leader, and turns to the queen at round 300-350 mostly when the enemy queen is alive (8 or longer by round 350 in 27 of 102 such
   games, 3 of 91 with her dead), otherwise in the last 75 rounds or never; it wins 27 of 48 both-alive games and loses outright
   when it feeds the wrong dragon (1060000: a 58-long leader, an 18-long queen, against a 47-long queen). Feeding is the same act in all three: own dragons die by choice next to the queen, about 2.6 segments spent per
   segment she gains. forgot's early clock has two costs: it runs out of feeders (1063806) and its long queen traps herself and
   sheds 2 segments a round (116 times in 88 of 632 games, 2,488 segments).

Also worth knowing, because it corrects the study's own notes: the "self-kills" of small dragons in the opening are not a choice
in any of the three teams. 97-99% of them happen with no free cell next to the head, mostly in one-cell dead ends that hold a
pearl, and the same cells take dragon after dragon. Vibing++, SSS and forgot only differ in the order a trapped dragon gives. The
cost is large (forgot lost 429 segments this way in the first 100 rounds of one game while eating 350 natural pearls) and no top
team avoids it.

## Games read

| # | game id | map | size | read for | opponent if not each other | result | end type | SSS queen | forgot queen |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1059834 | Around UNSW | large | SSS, forgot | | SSS won | queen rule, 36 vs dead | alive | rammed r72 by a 5-long, 4 steps |
| 2 | 1063806 | Slithery Fight | large | SSS, forgot | | SSS won | queen rule, 86 vs 62 | alive | alive |
| 3 | 1060000 | Slithery Fight | large | SSS | Kaizen (2084) | SSS lost | queen rule, dead vs 47 | rammed r479 by an 18-long, 5 free steps | (Kaizen's queen alive) |
| 4 | 1059840 | Australia | large | SSS, forgot | | forgot won | longest, 79 vs 27 | rammed r157 by a 3-long, next cell | rammed r208 by a 2-long, next cell |
| 5 | 1060356 | Australia | large | SSS | bread first search (2251) | SSS won | queen rule, 3 vs dead | alive, 3 long | (enemy queen rammed r143 by an 8-long, 6 steps) |
| 6 | 1067641 | Islands | large | SSS, forgot | | forgot won | longest, 63 vs 37 | rammed r166 by a 5-long, 5 steps | rammed r166 by a 3-long, next cell |
| 7 | 1067636 | Maze | medium | SSS, forgot | | forgot won | queen rule, 66 vs dead | rammed r181 by a 3-long, 2 steps | alive |
| 8 | 1067654 | Australia | large | forgot | Sponge (2285) | forgot lost | longest, 41 vs 105 | | rammed r86 by a 2-long, next cell (Sponge's rammed r111 by a 2-long) |
| 9 | 1063814 | Around UNSW | large | forgot | Sponge (2267) | forgot lost | queen rule, dead vs 33 | | rammed r34 by a 3-long, 6 steps over pearls |
| 10 | 1067667 | Around UNSW | large | forgot | bread first search (2233) | forgot won | queen rule, 53 vs 36 | | alive |
| 11 | 1067446 | Maze | medium | forgot | bread first search (2179) | forgot won | queen rule, 108 vs 91 | | alive |
| 12 | 1067620 | Australia | large | forgot (opening and queen kill) | Vibing++ (2313) | forgot won | queen rule, 39 vs dead | | alive (Vibing++'s rammed r178 by a 9-long) |
| 13 | 1067629 | Stripes | small | SSS, forgot | | forgot won | wipe-out r170 | rammed r103 by a 3-long, 3 steps | alive |
| 14 | 1067644 | Tower Defense | small | SSS, forgot | | SSS won | wipe-out r305 | alive | rammed r304 by a 3-long, 2 steps |
| 15 | 1067634 | Portals | small | SSS, forgot | | SSS won | queen rule, 59 vs 53 | alive | alive |

SSS: 10 games (6 large, 1 medium, 3 small; 5 wins, 5 losses). forgot: 13 games (8 large, 2 medium, 3 small; 7 wins, 6 losses),
game 12 read for its opening, its ram chances and its queen kill only. All twelve mandatory games are included. Seven more games
were opened for one point each and are not in the counts of the 15: 1063780, 1063789, 1069168, 1064500 and 1063792 (Vibing++'s
early non-ram deaths, `b_open.py`; the first and third also for its sonar), 1049256 and 1056815 (two SSS turns not taken, `b_turn.py`).

## Per-game notes

Conventions. The team named first in a sentence is the one being read. "Units / total" = number of living dragons and their summed
length. "Own heads within 8 cells" counts wrapped distance without regard to kelp. A "checkpoint" is every 20th round. The opening
tables give, per 10 rounds, the units and total at the start of the block and what happened during it.

### 1. 1059834 Around UNSW (large), SSS beat forgot on the queen rule (SSS queen 36, forgot's queen rammed at round 72)

Read from both sides. SSS is side B (queen #1, spawn (43,21)), forgot side A (queen #0, spawn (20,42)).

- **Opening.** 10 dragons each (total 36, one 10-long, queen 4). Both queens split 4 -> 2+2 at round 0. The 10-long: forgot sheds 2 from the tail per round (10 -> 8+2, 8 -> 6+2, ...); SSS cuts 10 -> 2+8 at once, and the 2-long front part, which stood in a one-cell dead end at (33,22), dies in round 1.

  | rounds | SSS units / total | SSS natural pearls eaten | SSS splits | SSS non-ram deaths | forgot units / total | forgot natural pearls | forgot splits | forgot non-ram deaths |
  |---|---|---|---|---|---|---|---|---|
  | 0-9 | 10 / 36 | 5 | 8 | 3 | 10 / 36 | 5 | 9 | 4 |
  | 10-19 | 15 / 35 | 15 | 5 | 2 | 15 / 35 | 7 | 5 | 2 |
  | 20-29 | 18 / 47 | 32 | 14 | 1 | 18 / 41 | 17 | 7 | 2 |
  | 30-39 | 29 / 74 | 33 | 16 | 7 | 21 / 52 | 18 | 7 | 2 |
  | 40-49 | 36 / 97 | 37 | 25 | 9 | 24 / 62 | 14 | 8 | 6 |
  | 50-59 | 52 / 129 | 32 | 19 | 14 | 26 / 68 | 10 | 9 | 4 |
  | 60-69 | 54 / 137 | 47 | 19 | 10 | 28 / 67 | 16 | 6 | 2 |
  | 70-79 | 62 / 182 | 37 | 10 | 7 | 31 / 79 | 18 | 15 | 5 |
  | 80-89 | 61 / 194 | 36 | 11 | 8 | 37 / 84 | 14 | 5 | 4 |
  | 90-99 | 62 / 215 | 32 | 9 | 9 | 36 / 93 | 7 | 6 | 5 |

  (Units and total are at the start of the block. "Non-ram deaths" = every death that is not a head-on.) Both teams had 18 units at round 20 and the same number of cells visited by round 40 (447 and 449). SSS then ate twice as much from the same ground. SSS's eaters are not only 2- and 3-longs: of 308 natural pearls in rounds 0-100, 73 were eaten by a dragon of 4 or longer (forgot: 1 of 128). SSS splits at 4 (69 of 92 splits in rounds 0-60) and at 5 into 2+3 (15); forgot only at 4 (40 of 45). SSS stops at 62 units from round 70: the limit is 64.
- **Non-ram deaths in the opening are not chosen.** All 36 of forgot's (reason `noaction`, by the suicide order) and 71 of SSS's 72 (58 by a move into its own body, reason `self`; 13 by a move into another body) happened with no free cell next to the head. Kelp on three sides, a one-cell dead end, in 24 of 36 and 49 of 72. The same cells again and again: (30,41) 14 times for forgot, (33,22) 14 times for SSS. A dragon walks in for the pearl, cannot come out, dies and leaves a pearl that draws the next one. Cost in rounds 0-100: SSS 167 segments lost, 77 pearls eaten back; forgot 77 lost, 35 eaten back.
- **Mid-game.** Rams on enemy heads: SSS 61 (10, 12, 12, 16, 11 per 100 rounds), forgot 69 (4, 28, 24, 8, 5). SSS's rams: 16 by a 2-long from the next cell, 28 by a 3-4-long with a 2-step move.
- **forgot's queen.** After her split she is 2 long. She walks east for 14 rounds in a row (rounds 10-23) and south for 9 (24-37), 7-17 cells from her spawn, with no own head within 6 steps at rounds 20, 40 and 60 and one own head within 8 cells. SSS foragers are in that area from round 42.
- **The followers, rounds 52-72.** SSS #100 (2 long, born round 42) and #42 (3 long, born round 15) have her in view from round 52. #100 is 3 steps from her at the start of 11 of the 21 rounds 52-72 and 5 steps in 9, and eats nothing in those rounds; it goes where she goes (rounds 57-64: she moves N, N, W, N, N, E, E, S; it moves W, W, W, W, N, N, N, E). She moves one step every round; in 10 of the 13 rounds that began with an enemy head within 3 steps her step put the nearest enemy head 4 steps away. At round 64 she steps south to (26,38) and #100 and a third SSS 2-long, #53, step next to her head on both sides. She moves first in round 65, so neither can reach her on its turn (a 2-long has a reach of 1). At round 66 forgot's #82 (2 long) rams #53 from the next cell, 3 steps from her: the only help she got.
- **The kill, round 72 at (26,46).** #42 keeps 4 steps away from round 66 to 71. It eats the two corpse pearls of the #82/#53 ram at rounds 69 and 70 (3 -> 5 long). Round 71: it needs 5 steps and she is 4 rows away, outside its 7x7 view; it moves 2 free steps. Round 72: she steps south again, it needs 4 steps and has her in view; it moves `SSSW` (2 paid) and rams her. Sonar rays that ended on #42 in rounds 52-72: 7, three of them from a dragon that had her in view.
- **SSS's queen.** Splits 4 -> 2+2 at rounds 0 and 25, then stays 2-3 long until round 436. At the 25 checkpoints (every 20 rounds) she is 0-21 cells from her spawn, 11 on average, while the other SSS heads average 18-27 cells from it; she has 2-12 own heads within 8 cells every time and an enemy head within 8 cells at 5 of the 25. She moves every round (10-20 different cells per 20 rounds, 459 one-step and 35 two-step moves) and eats little: 10 natural pearls in rounds 0-440. At rounds 332, 348, 359 and 367 she reaches 4 and splits back to 2+2 (1-2 free neighbour cells each time: ordinary "mother" splits).
- **The one intruder, round 276.** forgot's longest dragon, #561 (24 long), eats its way north along corpse pearls and starts round 276 two cells south of her at (36,28). She steps west. SSS #459 (4 long), which acts before #561, moves `NNW` (2 paid) and rams it. forgot had no turn with a free path to her head in 500 rounds (0 chances in `q3v2`).
- **Late game, SSS.** A leader is fed from about round 200 by deliberate deaths next to it (9 dragons, 81 segments, in rounds 200-299; the leader eats 28 of the 43 pearls): #458 is 29 long at round 200 and 44 at 250, #579 54 at 275 and 83 at 375. The queen is fed only from round 441 (the enemy queen had been dead for 370 rounds): 3 (r440), 6 (r444), 10 (r448), 16 (r460), 27 (r480), 36. 28 dragons (92 segments) die within 6 cells of her in rounds 400-499 with a free cell available; she eats 33 of their 50 pearls. The feeders come to 1-2 cells from her head and die by an over-long move (a 2-long moving `SN`, a 3-long `NNS`, a 5-long `EEEW` into itself, a 19-long `EW`), so the pearls lie on her next step.
- **Late game, forgot.** Queen dead, so it builds one dragon: 24 (r275), 38 (r350), 51 (r400), 64 (r450), 88 at the end (51% of its length). Dragons of 32 and 48 kill themselves next to a longer one (r424, r451); the longer one gets 10 of 16 and 13 of 24 pearls. forgot goes from 62 units (r300) to 17.
- **Leaders killed.** forgot's 15-long #462 (r238) by SSS #89, which was 13 long at round 228, split down to 2, walked 14 steps, ate two pearls and sprinted 4. forgot's 24-long (r276, above). forgot's 17-long #1033 (r484): SSS #1032 (15 long) splits 15 -> 2+13 at round 482, four steps from it, and the 2-long front part rams it two rounds later from the next cell. SSS's 25-long #79 (r202) by a forgot 3-long that came 26 steps in 20 rounds; SSS's 21-long (r400) by a forgot 4-long with a 3-step move.
- Decisive moment: round 72 at (26,46). After it SSS only had to keep its queen alive, and forgot never got a dragon within reach of her.

### 2. 1063806 Slithery Fight (large), SSS beat forgot on the queen rule with both queens alive (86 vs 62)

Read from both sides. SSS is side B (queen #1, spawn (59,4)), forgot side A (queen #0, spawn (3,22)).

- **Opening.** 7 dragons each (total 47). Both queens start 25 long, coiled, with no free cell next to the head (own segments 2, 4, 6 and 8 on the four sides). Both do the same thing: split 2 off the tail every round for 11 rounds (25 -> 23+2 ... 5 -> 3+2) and lose nothing. (Vibing++ cuts 25 -> 3+22 here and the 22-long child dies at once: `deep-read.md`, games 4 and 5.)

  | rounds | SSS units / total | SSS natural pearls eaten | SSS splits | SSS non-ram deaths | forgot units / total | forgot natural pearls | forgot splits | forgot non-ram deaths |
  |---|---|---|---|---|---|---|---|---|
  | 0-9 | 7 / 47 | 17 | 21 | 6 | 7 / 47 | 27 | 27 | 9 |
  | 10-19 | 22 / 52 | 13 | 7 | 3 | 25 / 59 | 31 | 18 | 9 |
  | 20-29 | 26 / 61 | 11 | 7 | 2 | 34 / 83 | 35 | 23 | 15 |
  | 30-39 | 31 / 70 | 21 | 12 | 3 | 42 / 98 | 42 | 30 | 19 |
  | 40-49 | 38 / 84 | 21 | 8 | 3 | 49 / 112 | 42 | 28 | 20 |
  | 50-59 | 41 / 99 | 25 | 12 | 3 | 55 / 128 | 36 | 26 | 20 |
  | 60-69 | 47 / 117 | 19 | 7 | 4 | 58 / 139 | 40 | 31 | 22 |
  | 70-79 | 45 / 111 | 19 | 17 | 5 | 62 / 148 | 37 | 28 | 23 |
  | 80-89 | 51 / 118 | 27 | 15 | 5 | 61 / 148 | 24 | 24 | 21 |
  | 90-99 | 59 / 133 | 27 | 13 | 7 | 62 / 151 | 36 | 31 | 31 |

  forgot eats 350 natural pearls in 100 rounds against SSS's 200, and is at the 64-unit limit by round 70. But both teams have the same total length, 137, at round 100. forgot's lead in pearls is spent on deaths: 189 non-ram deaths in rounds 0-100 (429 segments, 204 pearls eaten back) against SSS's 41 (97 segments, 38 eaten back). 188 of forgot's 189 and all 41 of SSS's happened with no free cell next to the head; the same cells are used again and again ((16,7) and (8,8) 13 times each for forgot, (54,18) 14 times for SSS). forgot makes 122 splits of 4 -> 2+2 in rounds 0-60, SSS 40.
- **Mid-game.** Rams on enemy heads: SSS 40 (13, 6, 3, 10, 8 per 100 rounds), forgot 76 (13, 20, 24, 16, 3). Both teams hold 56-63 units from round 100 to round 325.
- **Both queens.** Each stays in her own half behind her team. No enemy head came within 6 steps of either queen in 500 rounds, and neither team had one turn with a free path to the other queen's head (0 chances each in `q3v2`). SSS's queen: 2-4 long until round 305, 4-22 cells from her spawn, 4-14 own heads within 8 cells at every checkpoint from round 20 to 340; two "mother" splits (4 -> 2+2 at rounds 91 and 197). forgot's queen: 3 long until round 205, 1-13 cells from her spawn until round 280.
- **The game is a feeding race.** forgot starts first. Its queen is 6 long at round 213 (SSS's queen is 2 then), 20 at 259, 33 at 300, 50 at 350, 63 at 400, 75 at 425, 78 at 475. SSS starts at round 305, when forgot's queen is already 34: 6 at round 306, 20 at 328, 39 at 350, 61 at 400, 64 at 450, 76 at 475, 85 at 486.
- **How they feed.** Dragons walk to within a few cells of the queen and die there with a free cell available (so by choice). SSS: 49 such deaths (141 segments) in rounds 300-399 and 20 (75 segments) in 400-499; the queen eats 81 of the 120 pearls, other SSS dragons 37. forgot: 28 (67 segments) in rounds 200-299, 29 (74) in 300-399, 6 (42) in 400-499; the queen eats 70 of 103. A 30-long forgot dragon kills itself 4 cells from the queen at round 411 (she eats 11 of 15 pearls); a 29-long SSS dragon runs into itself next to its queen at round 468 (she eats 9 of 15). About 2.6 segments of feeder are spent per segment the queen gains, on both sides.
- **Who runs out.** forgot has 61 units until round 325, then 45 (r350), 31 (r375), 21 (r400), 14 (r425), 10 (r450). In the last 50 rounds its queen eats 5 natural pearls and nothing else. SSS still has 51 units at round 450 and 44 at 475; its queen eats 24 corpse pearls in the last 50 rounds.
- **SSS's queen waits for food by splitting.** Rounds 448-449 at (60,26): she has one free cell (east), and a 2-long SSS feeder (#1250) is coming down column 62 towards it. She splits 68 -> 66+2 and 66 -> 64+2 and so stays where she is. At round 449 the feeder steps to (62,26) and dies on (61,26), the cell next to her head, by a move of two steps (`WE`) that a 2-long cannot pay for. At round 450 she moves `EE` and eats its pearl. Same at rounds 454 and 457 (66 -> 64+2, 65 -> 63+2 with one free cell, a corpse pearl eaten the round after). Each wait costs her 2 segments for one pearl.
- **forgot's queen boxes herself in, round 489 at (36,15).** From round 410 she leaves her half (20-38 cells from her spawn, no own head within 6 steps at rounds 420-480). At rounds 486-489 she makes a tight loop for two natural pearls: `E` (eats at (36,16)), `E`, `N`, `W` (eats at (36,15)). (36,15) has kelp to the north and west; her own segment 2 is east and segment 4 south. From round 490 she splits 2 off her tail every round: 82 -> 62 in ten rounds. With segment 4 as the blocker this could only end at length 3; the game ended first.
- **Leaders.** Neither team builds one: the queen is each team's longest dragon from round 225 (forgot) and 325 (SSS). One enemy dragon of 15+ rammed: forgot's 19-long at round 347 by an SSS 3-long with a 2-step move.
- Decisive moment: rounds 450-486. SSS's queen goes from 64 to 85 on feeders while forgot, with 10-12 units left, adds 5. At round 489, before forgot's queen boxed herself in, SSS already led 85 to 82.

### 3. 1060000 Slithery Fight (large), SSS lost to Kaizen on the queen rule (SSS queen rammed at round 479, Kaizen's queen 47)

Read from the SSS side (side B, queen #1, spawn (59,4)). Kaizen (elo 2084) plays like forgot in the opening: 113 splits of 4 -> 2+2 in rounds 0-60 and suicide orders.

- **Opening.** Same start as game 2: both queens shed 2 from the tail for 11 rounds. Units: r30 40 vs 37, r60 60 vs 51, r100 61 vs 60 (SSS first). Natural pearls eaten in rounds 0-99: SSS 242 (19, 29, 21, 27, 22, 29, 23, 28, 26, 18 per 10 rounds), Kaizen 319. Non-ram deaths in rounds 0-100: SSS 63, all with no free cell (141 segments, 59 pearls eaten back; (54,18) 14 times, as in game 2); Kaizen 163 (390 segments, 195 back). Total length at round 100: 158 vs 146.
- **Mid-game.** Rams on enemy heads: SSS 53 (14, 14, 8, 14, 3 per 100 rounds), Kaizen 78 (7, 28, 23, 13, 7). Both teams hold 60-63 units until round 350. No enemy head came within 3 steps of either queen in the whole game; neither team had a turn with a free path to the other queen (0 chances each).
- **SSS's queen.** 3 long from round 10 to round 437 (one split 4 -> 2+2 at round 181), 3-19 cells from her spawn, 2-15 own heads within 8 cells at every checkpoint. Her head was inside an enemy's view in 26 rounds in all, the last at round 301.
- **Kaizen's queen.** 3-4 long until round 200, then fed slowly: 6 (r230), 11 (r300), 15 (r350), 22 (r390). Round 418 at (19,11): boxed in by her own coil (own segments 6, 10, 2 and 4 on the four sides). She splits 22 -> 2+20. The child, by then 21 long, kills itself 7 cells from her at round 434 and she eats 10 of its 11 pearls. Then she is fed fast: 10 (r440), 19 (r450), 27 (r460), 35 (r480), 47. Dragons of 22, 36 and 36 kill themselves within 5-7 cells of her at rounds 460, 473 and 482 (she eats 2 of 11, 6 of 18 and 8 of 18 pearls).
- **Late game, SSS: the wrong dragon is fed.** From round 350 SSS builds a leader, not the queen: #1166 is 29 long at round 375 and 36 at 400, #1349 37 at 425, 48 at 450, 56 at 475, 58 at the end (39% of the team). The queen is fed only from round 438: 8 (r440), 14 (r460), 18 (r470). With both queens alive the leader counts for nothing: at round 478 the queens stand 18 to 34.
- **SSS had seen her.** Part of Kaizen's queen was inside the view of an SSS head in ten rounds between 364 and 394 (she was 17-22 long then). SSS's queen feeding did not start then (in game 2 it started the round after an SSS dragon saw forgot's 33-long queen).
- **The queen's death, round 479 at (60,4).** From round 475 she walks north up column 60, two steps a round (`NN` five times), with no own head within 6 steps from round 476. Kaizen's #1477 (18 long, a split child born at round 461 with 16 segments) is wandering in SSS's home corner, eating natural pearls (r466, r478); nobody on its team had had her in view since round 441. It is never inside her 7x7 view and she is never inside its view at the start of a round: 5-7 steps apart at rounds 475-479, both moving north. At round 479 she steps to (60,4); on its turn she is 3 rows and 2 columns away and 5 steps off, exactly its free steps. It moves `SSWWS` and rams her.
- **Kills of enemy leaders.** None by SSS after round 300. SSS's 16-long (r356) was rammed by a Kaizen 5-long in the round it was born as a split child.
- Decisive moment: rounds 350-440. SSS fed a leader for 150 rounds (58) and its queen for the last 40 of her life (18); Kaizen fed its queen from round 230 and again from 2 to 47 after her forced split. The ram at round 479 changed nothing: 18 against 34 was already lost.

### 4. 1059840 Australia (large), forgot beat SSS on the longest dragon (79 vs 27; both queens dead)

Read from both sides. SSS is side B (queen #1, spawn (39,44)), forgot side A (queen #0, spawn (24,19)).

- **Opening (the game is decided here).** 9 dragons each (total 26). On this map the natural pearls lie in two fields far from both spawns (west: x 0-16, y 24-40; east: x 40-63, y 16-40); 0-1 pearls lie within 10 cells of either spawn in the first 100 rounds.

  | rounds | SSS units / total | SSS natural pearls eaten | SSS splits | SSS mean distance from spawn | forgot units / total | forgot natural pearls | forgot splits | forgot mean distance from spawn |
  |---|---|---|---|---|---|---|---|---|
  | 0-9 | 9 / 26 | 1 | 3 | 12 | 9 / 26 | 2 | 3 | 12 |
  | 10-19 | 12 / 27 | 4 | 1 | 12 | 12 / 28 | 3 | 1 | 14 |
  | 20-29 | 13 / 31 | 8 | 3 | 21 | 13 / 31 | 5 | 1 | 20 |
  | 30-39 | 16 / 39 | 9 | 5 | 23 | 14 / 36 | 12 | 6 | 21 |
  | 40-49 | 17 / 41 | 6 | 8 | 26 | 20 / 48 | 14 | 7 | 26 |
  | 50-59 | 20 / 44 | 4 | 3 | 27 | 23 / 54 | 19 | 10 | 30 |
  | 60-69 | 19 / 43 | 5 | 2 | 20 | 27 / 66 | 29 | 11 | 32 |
  | 70-79 | 20 / 45 | 4 | 1 | 19 | 33 / 87 | 25 | 18 | 31 |
  | 80-89 | 19 / 44 | 4 | 2 | 18 | 43 / 105 | 30 | 14 | 31 |
  | 90-99 | 19 / 45 | 6 | 3 | 17 | 52 / 134 | 31 | 16 | 30 |

  ("Mean distance" = mean wrapped distance of the non-queen heads from the team's queen spawn at the start of the block.) Level until round 40. Then forgot's dragons are spread over 20 of the 64 squares of 8x8 cells at round 60 and 27 at round 90, with heads in both pearl fields; SSS's are in 9 and 12 squares, all in the middle columns near its spawn (`b_map.py`). Cells visited by round 100: forgot 1,278, SSS 788. At round 60, 14 natural pearls lie in squares where only forgot has a head and 1 in a square where only SSS has. SSS also loses 13 dragons to head-ons in rounds 61-120 and makes 2 rams. Units at round 100: 21 vs 60; at round 120: 17 vs 62.
- **forgot's queen is followed first.** She walks away from home (17 cells at round 20, 41 at round 80). SSS #21 (3 long, born round 0) has her in view from round 21 to 51 and is exactly 4 steps from her at every 3-round checkpoint in that time; it eats nothing and no other SSS dragon is within 8 steps. She moves one step a round and so does it; a 3-long reaches 2, so it never gets a turn with a path within reach. It loses her at round 57 and rams a forgot 4-long at round 69.
- **SSS's queen.** Two "mother" splits (4 -> 2+2 at rounds 40 and 63, both with one free cell), then 2-3 long. She has 0-1 own heads within 8 cells at rounds 40-100: SSS has only 19-21 units on a 64x64 board.
- **Her death, round 157 at (31,57).** forgot #88 (2 long) is within 6 steps of her from round 102 and within 3 steps in rounds 114-123, until SSS #73 (3 long) rams it at round 125. forgot #16 then comes from 20 steps away (d20 at r117, d12 at r132, d2 at r137). #16 is a starting 3-long that has not eaten once in 157 rounds and has crossed the board (about 150 cells). From round 137 to 157 it has her in view every round, 2-4 steps away; she steps away every round (18 of 20 close rounds), down a staircase to the south-west, with no own head within 6 steps from round 148. Rounds 154-156 she goes west along row 58, a corridor with kelp to the south; at round 157 her head is at its closed end (kelp west and south, her body east) and the only free cell is north, next to #16's head. She steps there and #16 rams her from the next cell. A 3-long queen cannot split to stand still.
- **forgot's queen dies, round 208 at (35,20).** From round 160 she walks round one 2x2 block ((34,19), (34,20), (35,20), (35,19)), 6-7 different cells per 20 rounds, with 1-5 own heads within 8 cells. SSS #255 (2 long, born round 200) walks up column 36 and stops at (35,21). She does not leave her loop: at round 208 her next step in the loop is east to (35,20), next to its head, and it rams her. In 2 of her 6 close rounds her step brought her nearer to the enemy head.
- **Mid-game.** Rams on enemy heads: SSS 62 (4, 11, 25, 20, 2 per 100 rounds; 22 by a 2-long from the next cell, 31 by a 3-4-long with a 2-step move), forgot 66 (4, 21, 21, 13, 7). SSS rams as often as forgot with a third to two thirds of its units.
- **Late game.** Both queens are dead, so the longest dragon decides. forgot holds 62 units until round 350 and builds one dragon: 34 (r300), 56 (r350), 62 (r375), 71 (r475), 79. SSS has 20-40 units and a longest of 10-31.
- **SSS still kills leaders.** Five forgot dragons of 15-28 long are rammed by SSS 3-longs between rounds 236 and 370 (r236 a 17-long, r248 a 28-long, r275 a 22-long from 28 steps away in 20 rounds, r298 a 15-long, r370 a 24-long), each with a move of 1-3 steps; four of the five attackers were 2-longs that had eaten one pearl in the 10 rounds before. forgot's leader still reaches 79. SSS's own 24-long is rammed at round 353 by a forgot 5-long with a 4-step sprint.
- Decisive moment: rounds 40-100. forgot spread over the whole board and found both pearl fields; SSS stayed within 17-27 cells of its spawn and had 21 units against 60 at round 100.

### 5. 1060356 Australia (large), SSS beat bread first search on the queen rule (SSS queen alive and 3 long; enemy queen rammed at round 143)

Read from the SSS side (side B, queen #1, spawn (39,44); the same spawn and the same first 31 queen moves as in game 4).

- **Opening.** Here SSS does what forgot did to it in game 4. Natural pearls eaten per 10 rounds: SSS 1, 5, 9, 21, 17, 17, 19, 30, 17, 30; bread first search 1, 1, 1, 1, 2, 2, 7, 10, 3, 7. Units: r30 18 vs 14, r50 32 vs 14, r80 52 vs 19, r100 61 vs 21. SSS's heads are in the west pearl field from round 30 (12 heads there at round 60) and its mean distance from spawn rises to 27-31; cells visited by round 100: 1,299 vs 813. bread first search makes 6 splits in the first 60 rounds. 20 SSS dragons die boxed in during rounds 0-100, 11 of them on one cell of the west field, (10,26) (the same cell took 5 in game 4).
- **Mid-game.** Rams on enemy heads: SSS 50 (2, 13, 7, 13, 15 per 100 rounds), bread first search 56 (4, 10, 17, 13, 12), with 15-31 units against SSS's 60.
- **Enemy queen.** 2 long, alone (no own head within 6 steps in 23 of her 24 close rounds). SSS #33 (2 long) has her in view for 29 rounds (r81-112), 3-5 steps away. SSS #115 takes over: it is born at round 101 as a 9-long split child, splits 9 -> 2+7 at round 106 and, 2 long, has her in view from round 117 to 143, 1-5 steps away, eating nothing. She steps away in 17 of 24 close rounds; at round 137 #115 starts next to her head and she steps off.
- **The kill, round 143 at (29,7).** The 7-long part of that split, #123, stays 9-25 steps from her for 30 rounds (it eats one natural pearl at round 124), comes to 9 steps at rounds 140-142 and waits there: at round 142 it needs 8 steps (6 paid) and she is outside its view, so it moves one step. At round 143 she steps south to (29,7), 6 steps from it and inside its view; it sprints `NNWWWN` (4 paid) and rams her. One to three SSS dragons had her in view in 40 of the 41 rounds before.
- **SSS's queen.** A "mother" for the whole game: eight splits of 4 -> 2+2 (rounds 0, 40, 61, 126, 171, 194, 229, 346), four of them on the same corner cell (46,38). She eats 15 natural pearls in 500 rounds and nothing else: she is never fed and ends 3 long. At the 25 checkpoints she is 0-22 cells from her spawn (10 on average) while the other SSS heads average 20-32 cells from it; 1-7 own heads within 8 cells. Four episodes (7 rounds) with an enemy 2-3-long within 3 steps (r274-277, 368-370, 378, 427): she steps away every time (7 of 7) and the intruders leave; no own dragon rams them.
- **Late game.** With the enemy queen dead SSS builds a leader by deliberate deaths next to it: #105 is 25 long at round 225, 41 at 300, 69 at 400, 95 at 475. At round 493 it is rammed at (56,47) by a bread first search 7-long (a split child born at round 463 with 6 segments) that walked 38 steps in 20 rounds, stayed 3-5 steps away for three rounds and then sprinted 5 (3 paid). SSS ends with a longest dragon of 23 against 26, 48 units, and wins only because its 3-long queen is alive.
- **Kills of enemy leaders.** None: no enemy dragon of 15+ died in the game.
- Decisive moment: round 143 (the queen kill), and before it rounds 30-80 (61 units against 21 at round 100). The 3-long queen near her spawn was what won it: the 95-long leader was lost 7 rounds from the end.

### 6. 1067641 Islands (large), forgot beat SSS on the longest dragon (63 vs 37; both queens rammed in round 166; SSS ends with 41 units and total 237 against 16 and 120)

Read from both sides. SSS is side B but holds queen #0 (spawn (10,7)); forgot is side A with queen #1 (spawn (45,7)).

- **Opening.** 5 dragons each (total 12). Both queens are "mothers" (SSS splits 4 -> 2+2 at rounds 3, 12, 80; forgot at 3, 13, 65, 73).

  | rounds | SSS units / total | SSS natural pearls eaten | SSS splits | SSS non-ram deaths | forgot units / total | forgot natural pearls | forgot splits | forgot non-ram deaths | head-on deaths, each team |
  |---|---|---|---|---|---|---|---|---|---|
  | 0-9 | 5 / 12 | 7 | 3 | 1 | 5 / 12 | 8 | 2 | 0 | 1 |
  | 10-19 | 6 / 15 | 13 | 6 | 0 | 6 / 17 | 12 | 6 | 0 | 0 |
  | 20-29 | 12 / 29 | 13 | 7 | 1 | 12 / 32 | 19 | 8 | 0 | 0 |
  | 30-39 | 18 / 41 | 14 | 5 | 2 | 20 / 51 | 17 | 6 | 0 | 0 |
  | 40-49 | 21 / 53 | 14 | 9 | 2 | 26 / 68 | 22 | 12 | 0 | 3 |
  | 50-59 | 25 / 59 | 21 | 12 | 4 | 35 / 87 | 23 | 12 | 2 | 4 |
  | 60-69 | 29 / 70 | 15 | 12 | 5 | 41 / 101 | 25 | 12 | 2 | 5 |
  | 70-79 | 31 / 72 | 15 | 10 | 6 | 46 / 114 | 20 | 17 | 4 | 10 |
  | 80-89 | 25 / 65 | 12 | 12 | 2 | 49 / 122 | 27 | 19 | 5 | 5 |
  | 90-99 | 30 / 69 | 20 | 12 | 4 | 58 / 141 | 24 | 10 | 3 | 3 |

  forgot again spreads wider: its heads are 15-21 cells from its spawn on average, SSS's 10-15; cells visited by round 100: 1,113 vs 580. From round 40 the two teams ram each other one for one (30 head-on deaths each in rounds 40-99); the team with more units keeps growing, the other stalls at 25-31. Units at round 100: 35 vs 62.
- **Mid-game.** Rams on enemy heads: SSS 115 (18, 27, 30, 32, 8 per 100 rounds; 37 by a 2-long from the next cell, 51 by a 3-4-long with a 2-step move), forgot 105 (13, 36, 29, 19, 8). Of 18 enemy heads that came within 6 steps of SSS's queen, 5 were rammed by an SSS dragon, 3 rammed an SSS dragon and 9 left.
- **SSS's queen** is 2 long and stays 4-19 cells from her spawn with 4-12 own heads within 8 cells at every checkpoint from round 20 to 160. Three intruders are rammed by SSS dragons while within 6 steps of her (r148, r158, r162; attackers 3 long, victims 2 long). In her 9 close rounds she has three or more own heads within 6 steps in 8 and steps away 9 times out of 9. The allies do not turn towards the intruder as a group: in those rounds 25 ally moves ended nearer to the intruder's cell and 25 further from it.
- **Her death, round 166 at (11,4).** forgot's follower #222 (2 long) is 3 steps from her at rounds 155-158 and is rammed by SSS #191 at round 158. forgot #195 (born round 97 as a 2-long, 5 long from round 136, nothing eaten after round 127) comes from 21 steps away at round 126, circles 8-10 steps from her at rounds 154-161 and is 5, 2, 5, 4 and 4 steps away at rounds 162-166. Round 165: it needs 5 steps (3 paid) and she is outside its view; it moves one step. Round 166: she steps west to (11,4), inside its view; it sprints 5 steps `ESSWS` and rams her. She had four own heads within 6 steps at that moment. A 5-long reaches 5; no 2-3-long escort can stop it unless it is rammed first.
- **forgot's queen** walks 16 cells from home by round 40 with no own head near. From about round 155 she walks round one 2x2 block across the wrap edge ((0,6), (0,7), (55,7), (55,6)), with no own head within 6 steps in any of her 15 close rounds.
- **Her death, round 166 at (0,7).** SSS #227 (born round 111 as a 2-long; 3 long after one corpse pearl at round 149) walks 20 steps towards her in 25 rounds (d20 at r126, d10 at r146, d4 at r151) and then stays 2-6 steps from her for 15 rounds. She keeps to her loop. At round 166 her next loop step is south to (0,7), next to its head at (0,8); it rams her from the next cell at no cost.
- **Late game.** Both queens dead from round 166. forgot builds one dragon by suicides next to it: 19 (r175; rammed at r207 by an SSS dragon that had split 4 -> 2+2 five rounds before and eaten one pearl), 23 (r250; a 21-long rammed at r264 by an SSS 2-long that came 23 steps in 5 rounds), then 22 (r325), 42 (r375), 58 (r425), 63 at the end: 52% of its length. SSS does not: its longest is 4-10 until round 300, 16-23 from round 325 to 425, 36 at round 475, with 39-53 units all the time. Its leader gets 5-9 pearls per 50 rounds.
- Decisive moment: round 166 took both queens; after it the game was decided by consolidation, which forgot did and SSS did not (16% of SSS's length in its longest dragon at round 475, 40% of forgot's).

### 7. 1067636 Maze (medium), forgot beat SSS on the queen rule (forgot's queen 66, SSS's queen rammed at round 181; SSS's longest 79)

Read from both sides. SSS is side B (queen #1, spawn (43,8)), forgot side A (queen #0, spawn (4,15)). Maze is 48x24 with portals.

- **Opening.** 2 dragons each (total 8). Both queens are "mothers": 4 -> 2+2 at rounds 0 and 7 (both teams), forgot's again at 17, 43 and 120.

  | rounds | SSS units / total | SSS natural pearls eaten | SSS splits | SSS non-ram deaths | forgot units / total | forgot natural pearls | forgot splits | forgot non-ram deaths |
  |---|---|---|---|---|---|---|---|---|
  | 0-9 | 2 / 8 | 5 | 3 | 0 | 2 / 8 | 3 | 3 | 0 |
  | 10-19 | 5 / 13 | 5 | 3 | 0 | 5 / 11 | 8 | 4 | 0 |
  | 20-29 | 8 / 18 | 8 | 2 | 0 | 9 / 19 | 7 | 3 | 0 |
  | 30-39 | 10 / 26 | 11 | 6 | 3 | 12 / 26 | 9 | 2 | 2 |
  | 40-49 | 13 / 32 | 13 | 6 | 3 | 12 / 32 | 9 | 6 | 1 |
  | 50-59 | 16 / 43 | 12 | 8 | 3 | 17 / 40 | 9 | 5 | 1 |
  | 60-69 | 21 / 51 | 10 | 5 | 4 | 21 / 48 | 7 | 3 | 1 |
  | 70-79 | 22 / 57 | 13 | 6 | 3 | 23 / 54 | 6 | 3 | 3 |
  | 80-89 | 25 / 66 | 17 | 9 | 3 | 23 / 57 | 9 | 6 | 2 |
  | 90-99 | 31 / 81 | 14 | 9 | 5 | 27 / 62 | 8 | 4 | 5 |

  SSS wins the opening here: 35 units against 26 at round 100, 50 against 30 at round 120. No head-on at all before round 100. SSS's 24 non-ram deaths are on five cells ((36,23) ten times, (35,7) eight).
- **Mid-game.** Rams on enemy heads: SSS 29 (0, 11, 6, 10, 2 per 100 rounds), forgot 24 (0, 5, 10, 5, 4). SSS holds 58-61 units from round 150 to 300, forgot 39-56.
- **SSS's queen leaves home.** 2 long. She is 4-12 cells from her spawn until round 80 with 4-9 own heads within 8 cells, then drifts: 14 (r100), 18 (r120), 20 (r140), 21 (r160). At round 177 she steps through a portal from (27,22) into forgot's half at (14,20), 29 cells from home.
- **Her death, round 181 at (32,13).** At round 180 she stands at (14,18) in a corridor one cell wide. The cell to the north is a portal mouth; behind it, at (31,13), lies the pearl of an SSS dragon that died there. She steps through and eats it. (31,13) has kelp to the north and west, the portal (now her own body) to the south and one free cell, east. forgot #39 (3 long), moving east along rows 10-12 since round 173, is at (33,12), two steps from that cell. She must step east; #39 moves `SW` (1 paid) and rams her. #39 had her in view only in that round (and at rounds 152-153), and no forgot dragon had her in view in the two rounds before: a meeting, not a hunt. She could not see what was behind the portal.
- **forgot's queen.** 2-4 long until round 220, 2-17 cells from her spawn, with 5-17 own heads within 8 cells at every checkpoint from round 20 to 320. Fed from round 220 by suicides next to her: 12 (r240), 24 (r260), 33 (r300), 63 (r340), 73 (r400), 96 (r440), 102 (r481). No enemy head came within 3 steps of her in 500 rounds.
- **She traps herself, round 482 at (18,6).** A 102-long in a maze: her head is in a pocket with kelp east and south, her own body north, and a portal mouth west. She does not go through the portal. She splits 2 off her tail every round for 18 rounds (102 -> 66) and the game ends.
- **SSS does not take the shot.** SSS #851 (11-12 long) is on the other side of that portal from round 477 to 490, 5-8 steps from her head. `q3v2` lists four turns with a free path within its reach (r475: 12 steps; r476: 8; r485: 6 steps, 3 paid; r486: 5 steps, 2 paid). On all four her head was outside its 7x7 square (the path ran through the portal), and it walked on. She had been standing still since round 482, and it had had her in view in one of the ten rounds before. SSS's queen was dead; a ram there would have left both queens dead, with SSS's longest dragon at 78 against forgot's next longest of 27 (plus whatever it could have eaten of her 47 pearls in the last 14 rounds).
- **Late game.** SSS builds a leader after its queen's death (#688: 25 at r350, 54 at r400, 76 at r450; 79 at the end, 60% of the team) and goes from 61 units to 14. forgot goes from 56 units (r175) to 10 (r475) and its queen holds 62% of its length. One forgot 25-long kills itself 7 cells from the queen at round 402 (she eats 8 of 13 pearls).
- **Kills of enemy leaders.** None on either side (no dragon of 15+ was rammed).
- Decisive moment: round 180, the step through the portal. After it SSS needed a ram on forgot's queen and its one dragon in range (r485-486) would not ram a queen it could not see.

### 8. 1067654 Australia (large), forgot lost to Sponge on the longest dragon (41 vs 105; both queens dead by round 111)

Read from forgot's side (side A, queen #0, spawn (24,19)). Sponge is "Sponge(Albert and Bob)", elo 2285.

- **Opening.** Same map and spawn as forgot's win in game 4, but here the opponent finds the pearl fields too. Natural pearls eaten per 10 rounds: forgot 2, 1, 2, 9, 17, 13, 10, 9, 19, 10 (92 in all); Sponge 2, 1, 2, 5, 8, 20, 21, 29, 21, 28 (137). Units: r50 21 vs 17, r60 26 vs 24, r70 26 vs 31, r80 31 vs 39, r100 35 vs 48, r150 47 vs 61. At round 60 forgot's heads are in 22 of the 64 squares of 8x8 cells and Sponge's in 14, but Sponge's are in both pearl fields. Nine head-on deaths each in rounds 80-89.
- **forgot's queen.** Splits 4 -> 2+2 at round 0 and walks east: 27 cells from her spawn at round 40, with one own head within 8 cells on average at the checkpoints (1.1). She splits again at round 78 (4 -> 2+2).
- **Her death, round 86 at (52,16).** She walks east along row 16 for six rounds (r81-86), one own 2-long two steps behind her. Sponge #45 (3 long, 20-22 steps away at rounds 56-71; it splits 4 -> 2+2 at round 80 and is 2 long after that) comes north up columns 51-52 and has her in view from round 83. At the start of round 86 it is at (52,17), two steps from her, inside her view. She steps east to (52,16), next to its head, and it rams her from the next cell. She did not turn away: her step made the distance smaller.
- **Sponge's queen dies, round 111 at (28,60).** 4 long, alone. forgot #79 (3 long) is 2 steps from her at rounds 100-101; she steps away. #79 splits 4 -> 2+2 at round 103 and its child #146 (2 long) follows her: 3, 3, 1, 3, 5, 5, 3 steps at rounds 104-110, with her in view every round, eating nothing. At round 111 #146 starts next to her head and she orders a split (4 -> 2+2), which keeps her where she is. #146 rams her at no cost. A second forgot dragon (#79) is rammed 2 cells away in the same round by a Sponge 2-long.
- **Mid-game.** Rams on enemy heads: forgot 111 (7, 35, 42, 18, 9 per 100 rounds; 50 by a 2-long from the next cell), Sponge 123 (9, 35, 39, 25, 15). forgot holds 47-62 units from round 150 to 325 but keeps every dragon 3-5 long: its longest is 3-5 until round 300. The queen is dead, so nothing is fed.
- **Late game.** forgot starts one dragon at about round 320: #461 is 8 long at round 325, 21 at 350, 29 at 375, 42 at 394. Sponge starts at the same time (#397: 18 at r325, 38 at r375, 50 at r425, 76 at r475, 105 at the end) and nobody touches it.
- **forgot's leader is lost, round 394 at (62,30).** Sponge #648 (4 long) walks 30 steps in 20 rounds (d30 at r374, d16 at r384, d11, d10, d8, d6) and rams the 42-long with a 3-step move. forgot rebuilds to 25 (r425), 33 (r450), 41. It has 17-23 units left.
- **Kills of enemy leaders by forgot.** One: round 216, forgot #324 (3 long) walks 34 steps in 20 rounds (d34 at r196, d22, d17, d10, d7, d4) and rams Sponge's longest dragon, a 21-long, with a 2-step move.
- Decisive moment: round 394. Before it forgot's leader was 42 against Sponge's 41. Behind it stands the opening: 47 units against 61 at round 150.

### 9. 1063814 Around UNSW (large), forgot lost to Sponge on the queen rule (forgot's queen rammed at round 34; Sponge's queen 33)

Read from forgot's side (side A, queen #0, spawn (20,42)).

- **Opening.** Natural pearls eaten per 10 rounds: forgot 5, 8, 7, 12, 24, 21, 18, 34, 25, 31; Sponge 4, 8, 24, 29, 19, 33, 27, 20, 24, 15. Units: r30 18 vs 25, r50 27 vs 40, r70 38 vs 53, r100 62 vs 62. forgot loses 20 dragons with no free cell in rounds 0-60 (suicide order) and 43 more in rounds 61-120.
- **forgot's queen.** Her first 22 moves are the same as in game 1 (same map and side): split 4 -> 2+2 at round 0, nine steps north-west, then east for 12 rounds in a row (r10-21). At rounds 23-34 she has no own head within 6 steps.
- **Her death, round 34 at (27,33).** Sponge #50 (born round 24 as a 2-long; it splits 4 -> 2+2 at round 32) is a forager 7-10 steps from her and has never had her in view. At round 34 she steps north to (27,33). On its turn #50 is 3 long with her 3 columns and 3 rows away: it moves 6 steps `SSWWSW`, eating four natural pearls on the way (each gives back the segment a paid step costs), and rams her. One Sponge dragon had had her in view since round 30. Without the pearls a 3-long reaches 2.
- **Mid-game.** Rams on enemy heads: forgot 73 (12, 22, 19, 19, 1 per 100 rounds), Sponge 69 (17, 15, 14, 19, 4). Both teams hold 60-62 units from round 100 to 325.
- **The pattern over all games.** On Around UNSW forgot's queen is dead by round 60 in 19 of its 44 games against 2000+ teams and by round 100 in 27; forgot wins 6 of those 27 and 9 of the other 17 (`b_out/cand_tab.txt`). It is forgot's worst large map (15 wins in 44).
- **Sponge's queen.** 3-7 long until round 175, fed to 12 (r200) and 23 (r250), then left at 23 until round 400, 33 at the end. forgot never had a turn with a free path to her head (0 chances in `q3v2`).
- **Late game.** forgot, queen dead, holds 62 units until round 325 and builds a dragon by suicides next to it. It is rammed five times: an 18-long (r251) and a 25-long (r255) by Sponge 4-longs with 2-step moves, one of them from 20 steps away ten rounds earlier; a 17-long (r269) by a 5-long sprinting 4; a 46-long (r414) by a 5-long sprinting 4; a 47-long (r451) by a 3-long with a 2-step move. It still ends with a 57-long (38% of its length), longer than anything Sponge has (49), with 9 units.
- **Kills of enemy leaders by forgot.** None of 15+.
- Decisive moment: round 34. With its queen dead forgot needed a ram on Sponge's queen and never got a dragon within reach of her in 466 rounds.

### 10. 1067667 Around UNSW (large), forgot beat bread first search on the queen rule with both queens alive (53 vs 36)

Read from forgot's side (side A; here it has the spawn at (43,21) and queen #1).

- **Opening.** Natural pearls eaten per 10 rounds: forgot 3, 10, 29, 16, 20, 21, 17, 21, 20, 20 (177); bread first search 3, 5, 22, 25, 16, 20, 21, 28, 24, 24 (188). Units: r30 25 vs 22, r50 31 vs 31, r70 38 vs 44, r100 46 vs 58, r150 49 vs 59. forgot loses 31 dragons with no free cell in rounds 0-60 and 41 in rounds 61-120 (bread first search's boxed-in dragons die by moving into kelp, reason `wall`).
- **forgot's queen survives the opening this time.** She splits 4 -> 2+2 at round 0 and wanders 9-11 cells from her spawn until round 60 with 0-4 own heads within 8 cells and 3-5 enemy heads within 8 at rounds 40 and 60. Four episodes (18 rounds: r32-40, 49-52, 62, 103-107) with an enemy 2-3-long within 3 steps: she steps away every time (18 of 18), and after her step the nearest enemy head is 4 steps away in almost every round. One enemy 2-long (#48) is 3 steps from her at the start of eight rounds (r32-37 and 39-40) and never gets a turn within reach. Five intruders are rammed by forgot dragons while within 6 steps of her (r76, r115, r119, r165, r328; attackers 2-3 long).
- **Mid-game.** Rams on enemy heads: forgot 73 (6, 19, 34, 11, 3 per 100 rounds), bread first search 104 (13, 24, 32, 31, 4). Of 24 enemy heads that came within 6 steps of forgot's queen, 15 left and 5 were rammed by a forgot dragon.
- **Then she stays home.** From round 80 to the end she is 1-12 cells from her spawn at every checkpoint but one (17 at round 380), and 1-6 from round 120 to 280, while the other forgot heads average 22-35 cells from it. Five "mother" splits (4 -> 2+2 at rounds 82, 140, 146, 168, 181).
- **Feeding.** From round 215: 6 (r220), 10 (r244), 20 (r281), 25 (r325), 33 (r400), 42 (r420), 53 at the end. No enemy head within 3 steps of her after round 107.
- **A second long dragon.** From round 380 forgot also builds a non-queen leader: 40 (r400), 49 (r425), 61 (r450); it ends 62. Units fall from 62 (r350) to 13 (r475). A 25-long is rammed at round 426 by an enemy 3-long that came 19 steps in 20 rounds.
- **Enemy queen.** She sits in a nook next to her spawn ((21,42)-(22,43), 10 cells within 4 steps) for the first 100 rounds and is 3 long until round 424. She is fed only in the last 50 rounds: 30 pearls from own suicides, 3 -> 36. bread first search has 38 units and a total length of 287 at the end, against forgot's 11 and 188.
- **No contact with either queen.** Neither team had a turn with a free path to the other queen's head (0 chances each).
- Decisive moment: none in one round. forgot fed its queen from round 215, bread first search from round 450; 285 rounds of feeding against 50.

### 11. 1067446 Maze (medium), forgot beat bread first search on the queen rule with both queens alive (108 vs 91)

Read from forgot's side (side B, queen #1, spawn (43,8)).

- **Opening.** 2 dragons each. Natural pearls eaten per 10 rounds: forgot 2, 4, 8, 9, 9, 9, 11, 11, 8, 10 (81); bread first search 2, 2, 7, 3, 6, 9, 8, 7, 4, 8 (56). Units: r30 8 vs 7, r50 14 vs 11, r70 20 vs 16, r100 31 vs 23. forgot's queen is the "mother" (4 -> 2+2 at rounds 0, 6, 19). No head-on in the first 100 rounds.
- **forgot's queen.** 2-3 long until round 203. She wanders: 19-29 cells from her spawn at rounds 60-120, with 1-5 own heads within 8 cells, then comes back (3-11 cells from round 140). No enemy head came within 3 steps of her in 500 rounds and neither team had a turn with a free path to the other queen.
- **Mid-game.** Little contact: rams on enemy heads, forgot 19 (0, 2, 7, 7, 3 per 100 rounds), bread first search 20.
- **The team gathers round her before the feeding starts.** Own heads within 8 cells of her: 5 (r120), 13 (r140), 14 (r160), 19 (r180), 21 (r200). Then they die next to her: she is 6 long at round 206, 10 at 208, 20 at 220, 40 at 256, 59 at 300, 77 at 325. She eats 27 corpse pearls in rounds 200-249 and 22 in 250-299. forgot's units: 56 (r200), 37 (r225), 27 (r300), 9 (r400).
- **Boxed in, round 343 at (41,12), and out again at once.** 77 long, she has caught up with her own tail: own segments 2, 8, 76 and 74 on the four sides. She splits 77 -> 75+2; the two cut segments were the ones in her way, and she moves on next round. Cutting in front of segment 8, as Vibing++ does, would have left her 7 long.
- **Late game.** forgot's queen: 84 (r375-400), 89 (r425-450), 101 (r475), 108. A 31-long forgot dragon kills itself 14 cells from her at round 450; she eats 6 of its 16 pearls. bread first search keeps 46-53 units until round 400 with its queen 3 long, then feeds her all at once: 26 (r425), 46 (r450), 69 (r475), 91: 46 corpse pearls and 42 natural pearls in 100 rounds, with its units falling from 46 to 11.
- **Leaders.** None: each queen is her team's longest dragon (65% of the team's length on both sides at round 475).
- Decisive moment: the round each team began to feed. forgot began at 203 and led 84 to 3 at round 400; bread first search began at about 405 and closed to 91 against 108. Twenty rounds more would have been enough for it.

### 12. 1067620 Australia (large), forgot beat Vibing++ on the queen rule (read from forgot's side: the opening, rounds 0-120, and the queen kill)

Sub-session A read this game from Vibing++'s side (`deep-read.md`, game 3). forgot is side A (queen #0, spawn (24,19)).

- **Opening table.**

  | rounds | forgot units / total | forgot natural pearls eaten | forgot splits | forgot boxed-in deaths | forgot cells visited so far | Vibing++ units / total | Vibing++ natural pearls | Vibing++ splits | Vibing++ boxed-in deaths | Vibing++ cells visited |
  |---|---|---|---|---|---|---|---|---|---|---|
  | 0-9 | 9 / 26 | 2 | 3 | 0 | 113 | 9 / 26 | 0 | 2 | 0 | 105 |
  | 10-19 | 12 / 28 | 1 | 0 | 0 | 195 | 11 / 26 | 0 | 0 | 0 | 176 |
  | 20-29 | 12 / 29 | 3 | 2 | 0 | 283 | 11 / 26 | 2 | 0 | 0 | 246 |
  | 30-39 | 14 / 32 | 12 | 3 | 1 | 385 | 11 / 28 | 13 | 5 | 2 | 318 |
  | 40-49 | 16 / 43 | 17 | 11 | 4 | 481 | 12 / 33 | 8 | 5 | 6 | 363 |
  | 50-59 | 21 / 51 | 21 | 11 | 2 | 582 | 9 / 30 | 5 | 6 | 4 | 394 |
  | 60-69 | 29 / 69 | 25 | 12 | 3 | 702 | 9 / 28 | 6 | 5 | 3 | 418 |
  | 70-79 | 35 / 91 | 29 | 18 | 3 | 870 | 8 / 22 | 6 | 4 | 4 | 428 |
  | 80-89 | 48 / 122 | 35 | 20 | 6 | 1,078 | 6 / 18 | 6 | 3 | 2 | 438 |
  | 90-99 | 62 / 151 | 33 | 4 | 4 | 1,315 | 7 / 23 | 7 | 7 | 5 | 454 |

  ("Cells visited" is the number of different cells any own head has stood on by the end of the block.)
- **What forgot does in rounds 40-90.**
  - It spreads. Its heads are in 12 of the 64 squares of 8x8 cells at round 30, 20 at round 60 and 32 at round 90 (Vibing++: 9, 6, 6), and it has heads in both pearl fields from round 60. Mean distance of its heads from its spawn: 29-30 cells from round 40.
  - It splits only at 4 into 2+2 (69 of 79 splits in rounds 31-100), and parent and child part quickly: 6.4-7.3 steps apart five rounds after the split (Vibing++: 4.0-5.3).
  - Almost all eating is done by 2- and 3-longs (163 of 179 natural pearls). It does not sprint to pearls: one paid step in 100 rounds.
  - It loses dragons in pearl-baited dead ends just as Vibing++ does: 23 boxed-in deaths in rounds 0-100 (63 segments, 30 pearls eaten back), 14 of them on five cells of the east field. Vibing++ has 26 (63 segments), 19 of them on five cells of the west field ((9,24), (10,26), (8,23), (7,25), (6,25)). The count is the same; forgot has 20-60 units to lose them from and Vibing++ 9-12.
- **The queen kill, round 178** (A's note has the killer's track). What `q3v2` adds from forgot's side: forgot had 8 turns with the Vibing++ queen in view and a free path within reach, and took one. Not taken: #117 (8 long, r118, 4 steps, 2 paid, she was 5 long); #92 (7 long, r137, 6 steps, 4 paid); and #193, a 12-long born at round 160 as an 11-long split child, on five turns in a row (r169-173: 5, 5, 6, 4 and 8 steps, 2, 2, 3, 1 and 5 paid; she was 3 long). #193 walked beside her for five rounds and never struck. The killer, #159 (9 long), took the first turn on which she was in its view (r178; the shortest free path was 4 steps, it moved 6 and paid 3). The two forgot 2-longs that followed her (#175: 17 rounds in view, 1-5 steps away, next to her head at the start of two rounds; #63: 15 rounds, 3-5 steps) never had a turn within reach.
- Decisive moment: rounds 40-90 (62 units against 7 at round 100), as A wrote.

### 13. 1067629 Stripes (small), forgot beat SSS by wipe-out at round 170 (SSS's queen rammed at round 103)

Read from both sides. forgot is side A with queen #1 (spawn (2,10)); SSS is side B with queen #0 (spawn (21,1)). The board is 24x12.

- **Opening.** 2 dragons of length 2 each. Natural pearls eaten per 10 rounds: forgot 0, 3, 5, 6, 4, 8, 5, 4, 6, 7; SSS 1, 6, 3, 4, 6, 8, 9, 5, 2, 4. Units: r20 3 vs 5, r40 6 vs 5, r60 9 vs 7, r80 11 vs 8, r100 12 vs 5.
- **forgot's queen is the mother and works from one corner.** She walks 10 cells east to the middle of the bottom edge and from round 12 circles one 2x2 block there, eating; every nine rounds she is 4 long on the same corner cell (11,10) (kelp north and west) and splits 4 -> 2+2 (rounds 12, 21, 30, 39, 48). At round 30 she splits, and so stands still, with an SSS 2-long two steps away; nothing comes of it. 15 close rounds in the game: 13 moves and 2 splits; her step made the distance to the nearest enemy head larger in 11 and smaller in 4. She has one or more own heads within 6 steps in 14 of the 15, and forgot dragons ram three intruders within 6 steps of her (r79, r93, r153).
- **SSS's queen** splits twice (r11, r33) and then moves about the middle of the board, 5-12 cells from her spawn, with 1-7 forgot heads within 8 cells of her at every checkpoint.
- **Mid-game.** The teams ram each other from round 55; forgot loses 14 dragons to head-ons in rounds 61-120 and makes 8 rams, but SSS falls from 9 units (r70) to 5 (r100).
- **The kill, round 103 at (17,7).** One to four forgot dragons have her in view in every round from 81 to 103. forgot #54 (2 long, born round 84) is 22 steps from her at round 91 and then comes straight in: 18, 16, 14, 12, 10, 8, 6, 4 steps at rounds 93-102, eating one corpse pearl at round 102 (3 long). She walks east along row 6 towards it (r99-102) with no own head within 6 steps at round 100. Round 103: she steps south to (17,7); she is in its view for the first time; it moves `SWW`, eating a corpse pearl on the way, and rams her. One sonar ray from a forgot dragon that had her in view ended on #54 (r94).
- **After that** SSS has 5 units against 12 and is hunted down by round 170.
- Decisive moment: round 103, after a mid-game in which SSS lost half its units.

### 14. 1067644 Tower Defense (small), SSS beat forgot by wipe-out at round 305 (forgot's queen, its last dragon, rammed at round 304)

Read from both sides. SSS is side B (queen #1, spawn (26,11)), forgot side A (queen #0, spawn (5,4)). The board is 32x16.

- **Opening.** 2 dragons of length 2 each, and almost no pearls at first (4 on the board at round 10, 24 at round 30). Both teams have 2 units until round 50. Natural pearls eaten per 10 rounds from round 50: SSS 4, 11, 11, 2, 3; forgot 5, 4, 6, 7, 6. Units: r60 4 vs 4, r70 8 vs 5, r80 11 vs 6, r100 11 vs 10, r150 12 vs 9.
- **SSS's queen never leaves her room.** At all 16 checkpoints she is 0-7 cells from her spawn. She is the mother (4 -> 2+2 at rounds 64, 116, 191, 300; twice on the corner cell (29,7)), eats 8 natural pearls in 300 rounds and is never fed. No enemy head came within 3 steps of her.
- **Mid-game.** SSS makes 12 rams in rounds 100-199 against forgot's 7 (10 of SSS's 19 rams in the game are by a 3-4-long with a 2-step move). Units: r200 22 vs 6, r250 38 vs 1.
- **forgot's queen is the last dragon.** From round 250 she is alone, 4-6 long, and moves two steps on some turns. SSS has one to five dragons with her in view in every round from 264 to 304 except one. SSS #76 (2-3 long) follows her from round 289 (15 rounds in view, 2-6 steps away). At round 304 she moves `NW` and ends two steps from its head; it moves `WS` (1 paid) and rams her.
- Decisive moment: rounds 100-200, when SSS won the ram exchanges (22 units against 6 at round 200).

### 15. 1067634 Portals (small), SSS beat forgot on the queen rule with both queens alive (59 vs 53)

Read from both sides. SSS is side B (queen #1, spawn (31,10)), forgot side A (queen #0).

- **Opening.** 3 dragons of length 3 each. Natural pearls eaten per 10 rounds: SSS 4, 8, 8, 7, 11, 16, 8, 11, 19, 18 (110); forgot 4, 8, 15, 13, 14, 13, 20, 17, 22, 11 (137). Units: r30 8 vs 10, r50 13 vs 13, r80 23 vs 27, r100 33 vs 34. Non-ram deaths in rounds 0-99: forgot 48, SSS 34.
- **Mid-game.** 32-39 units each from round 100 to 300. Not one head-on ram on either side in 500 rounds. No enemy head came within 3 steps of either queen in 500 rounds, and neither team had a turn with a free path to the other queen (the two halves are joined only by portals).
- **SSS's queen.** 2-3 long until round 255, 0-16 cells from her spawn, with 9-21 own heads within 8 cells at every checkpoint from round 100 to 360: on this small map the whole team is round her.
- **The feeding race.** Both start at the same time: forgot's queen is 6 long at round 297, SSS's at 302. (In forgot's large- and medium-map games the feeding starts at about round 200-220.) forgot leads at first: 23 against 15 at round 350. SSS: 36 (r400), 52 (r450), 59. forgot: 29 (r400), 43 (r450), 53.
- **SSS turns everything into the queen.** 33 dragons die next to her by choice in rounds 300-399 (74 segments; she eats 30 of 41 pearls) and 10 more (47 segments; 19 of 25) in rounds 400-499. Units: 35 (r300), 24 (r350), 9 (r400), 2 (r450), 1 at the end. The queen is the whole team, 59 of 59.
- **forgot keeps a second dragon.** At round 400 its queen is 29 and another dragon is 23; it ends with 6 units and a total of 73, of which the queen has 53. Its queen is boxed in twice and sheds 2 each time (r382: bodies of two own dragons north and east, 28 -> 26+2; r450: an own head east and her own segment 4 south, 43 -> 41+2).
- **SSS's queen waits once more by splitting** (r471: one free cell, 56 -> 54+2).
- Decisive moment: rounds 350-450. SSS's queen gained 37 while forgot's gained 20; forgot ended with 20 segments outside its queen and lost by 6.

## Answers to the eight questions

Where a count is "over all games" it covers every game of that team against opponents rated 2000+, Schooltime left out (SSS 503 games,
forgot 632, Vibing++ 502), and the script and output file are named. "In the games read" means the 15 games above (SSS 10, forgot 13);
those counts are in `b_out/tally15.txt` (`b_tally.py`).

### 1. Ram when in view

A "chance" is one turn of one dragon with a free path to the enemy queen's head no longer than its reach; "in view" means her head is
inside the dragon's 7x7 square on that turn (`q3v2`, the lead's `extract3.py`).

**forgot.** 457 in-view chances over all games, 254 taken. The rule that fits them (`b_chance.py`, `b_chance2.py`, `b_chance3.py`; outputs `b_out/chance*_264*.txt`):

| attacker | when | taken | what it does otherwise |
|---|---|---|---|
| 2-3 long | round 100 or later | 136 of 139 | |
| 2-3 long | rounds 0-99, at least as many other own heads within 4 steps of it as enemy heads there (the queen counted) | 47 of 51 | |
| 2-3 long | rounds 0-99, fewer other own heads within 4 steps than enemy heads there ("outnumbered") | 38 of 127 | moves away (77 of the 96 turns not taken by 2-3-longs) |
| 4 long | any round | 12 of 53 | splits 4 -> 2+2 (40 of the 41 turns not taken) |
| 5-9 long | any round | 21 of 65 | walks on; 11 of 27 taken when she is at least as long as the attacker, 10 of 38 when she is shorter |
| 10-12 long | any round | 0 of 22 | walks on |
| the team's longest dragon | any round | 4 of 47 | |

- **It is a time switch plus a local head count, not a price.** Before round 100 a small forgot dragon rams her only when it is not outnumbered where it stands; from round 100 it always does, even alone among enemies (22 of 24 when the enemy heads within 4 steps outnumbered the other own heads there by two or more). Cost does not explain it: a 3-long takes 13 of 28 free chances and 24 of 47 one-paid-step chances on a 2-long queen. Whether its own queen is alive does not explain it either (65% taken with her dead, 52% alive, over all lengths).
- **The head count holds however the heads are counted.** A second script (`b_chance4.py`) recounted the 178 early turns: with heads inside the attacker's 7x7 view instead of within 4 steps, 66 of 82 taken when not outnumbered and 19 of 96 when outnumbered; within 5 steps, 57 of 71 and 28 of 107; within 3 steps, 33 of 39 and 52 of 139. Which radius forgot really uses I cannot tell; 4 steps and the 7x7 view fit best.
- **Longer dragons are not fighters.** A 4-long splits, as every forgot 4-long does. Dragons of 5 and more mostly walk past. In the game read with the most such turns, 1067620, a 12-long (#193) walked beside Vibing++'s 3-long queen for five turns (r169-173; 4-8 steps, 1-5 paid) and an 8-long and a 7-long passed one turn each (r118, r137); a 9-long took the eighth turn (r178).
- **Being fed, yes; on its way to feed, no.** Of the 31 forgot dragons of 5-12 that passed up an in-view chance (first such turn each, `b_chance5.py`), 19 had eaten pearls of dead team-mates in the 20 rounds before and 7 were the team's longest dragon at that moment: they are dragons the team is growing. None of the 31 died by choice next to its queen or its leader in the 40 rounds after; 8 were rammed, 5 rammed another dragon, 5 split, 6 died elsewhere and 7 were still alive.
- **Other things checked and found not to matter:** a pearl within reach (taken 13 of 48 with a pearl next to it, but those are mostly the early outnumbered turns), an ally about to do it (she was rammed by another forgot dragon in the same round on 3 of the 203 turns not taken), the attacker's age.
- **What it costs.** forgot had an in-view chance in 308 games. In 104 it missed at least one; in 37 of those it never rammed her at all, and won 12 of the 37 (32%). In the 204 games in which it took every chance it won 154 (75%).
- In the games read: 5 of 12 in-view chances taken; the 7 not taken are the ones in 1067620 above (`b_out/mychances15.txt`).

**SSS.** 250 of 254 in-view chances taken over all games, at every length (2-3 long 155 of 155, 4 long 26 of 26, 5-9 long 59 of 61, 10-12 long 10 of 12) and every price (4 paid steps 9 of 9). In the games read: 5 of 5.
- **The 4 not taken are not exceptions to the rule.** Two are turns of a 5-long whose only path ran over cells of its own body that the counting script treats as vacated in time (1049256 r313, 1056815 r452; drawn with `b_turn.py`). Two are 10-step paths costing 7 segments (1055271 r236, a 10-long; 1059358 r421, a 12-long); SSS takes 12 of 12 six-step paths and 3 of the 5 longer ones, the two it left being these 10-step paths, so its search seems to stop at about 7-9 steps (inference).
- **Out of view: never.** 0 of 273 over all games. In 1067636 this cost the game: SSS #851 (12 long) had a free path of 6 and 5 steps (3 and 2 paid) at rounds 485-486 to forgot's 92-94-long queen, who had not moved for three and four rounds; the path ran through a portal, her head was 9 columns away, and it walked on. SSS's own queen was dead.

### 2. How hunters find her

**The kills read** (`b_out/tally15.txt`, section D; tracks in the per-game notes).

| team | game, round | killer | where it was before | in its own view before the fatal round | last move | why she could be caught |
|---|---|---|---|---|---|---|
| SSS | 1059834 r72 | #42, 5 long (3 long until r69) | 4 steps from her for 20 rounds | 13 of the 40 rounds before | 4 steps, 2 paid | it grew from 3 to 5 on two corpse pearls of a ram beside her |
| SSS | 1059840 r208 | #255, 2 long, born r200 | 6-8 steps away at r202-204 | 3 | next cell | she kept walking her 2x2 loop and stepped next to it |
| SSS | 1060356 r143 | #123, 8 long, a split child of 7 born r106 | 9-25 steps away for 30 rounds | 0 | 6 steps, 4 paid | a 2-long of the same team followed her for 24 rounds; the 8-long struck on its first turn in view |
| SSS | 1067641 r166 | #227, 3 long | walked 20 steps in 25 rounds, then 2-6 steps away for 15 rounds | 7 | next cell | she kept her loop and stepped next to it |
| SSS | 1067644 r304 | #76, 3 long | followed her for 15 rounds | 7 | 2 steps, 1 paid | she was forgot's last dragon |
| forgot | 1059840 r157 | #16, 3 long, a starting dragon that never ate | walked 20 steps in 20 rounds, then 2-4 steps away for 21 rounds | 19 | next cell | she ran into the closed end of a corridor |
| forgot | 1067641 r166 | #195, 5 long | 21 steps away 40 rounds before, 8-10 steps for 8 rounds | 3 | 5 steps, 3 paid | first turn in view and in reach |
| forgot | 1067636 r181 | #39, 3 long | walking east, 5 steps from a portal mouth | 2 | 2 steps, 1 paid | she stepped out of the portal next to it |
| forgot | 1067654 r111 | #146, 2 long, born r103 | followed her for 8 rounds | 7 | next cell | she split, and so stood still, with it next to her head |
| forgot | 1067629 r103 | #54, 2-3 long | walked 20 steps in 12 rounds | 0 | 3 steps, a pearl eaten on the way | she was walking towards it |
| forgot | 1067620 r178 | #159, 9 long | fed 13-17 steps away for 14 rounds | 1 | 6 steps, 3 paid (a path of 4 existed) | first turn in view and in reach |

- **Killer length.** SSS: 5 or longer in 2 of 5 (the lead's count over all large-map kills is 64%). forgot: 5 or longer in 2 of 6.
- **A small dragon alone does not catch a queen that keeps stepping away.** Of the 11 kills, 4 needed the queen's own step (she stepped next to or towards the killer in 1059840 r208, 1067641 r166 for forgot's queen and 1067629 r103, and stood still in 1067654 r111); 2 were forced by the map (1059840 r157, a dead end; 1067636 r181, a portal); 4 were sprints of a dragon of 5 or more (1059834 r72, 1060356 r143, 1067641 r166 for SSS's queen, 1067620 r178); and 1 was the last dragon of a beaten team (1067644 r304).
- **Followers exist in both teams and look the same.** A follower here is a non-queen dragon that keeps the enemy queen's head in its view for 6 or more rounds in a row while able to walk to her (path of 6 steps or less). SSS: 14 such streaks in 10 games; forgot: 14 in 13. All 28 are 2 or 3 long. They sit 3-4 steps from her (median distance 3 or 4 in 21 of 28). They eat nothing during the streak in 20 of 28. The longest: SSS #21 in 1059840, 30 rounds at exactly 4 steps; SSS #33 and #115 in 1060356, 29 and 24 rounds; SSS #100 in 1059834, 21 rounds; forgot #16 in 1059840, 20 rounds.
- **Is the follower a role?** What is seen: a 2-3-long that has her in view goes where she goes and stops eating. She moves one step a round and so does it, so the distance stays at 3-4 and it never gets a turn within reach. That needs no special role, only "walk towards a queen you can see" (inference). It ends with the follower ramming her in 4 of 28 streaks, with another dragon ramming her in 4, with the follower rammed in 2 and with her getting away in 18. One dragon does look like a dedicated hunter: forgot #16 in 1059840 was a starting 3-long that ate nothing in 157 rounds and crossed the board.
- **A call for help: yes for SSS, found in the sonar value itself.** A field of SSS's 64-bit sonar value decodes to a board cell, and in the rounds when SSS knows where the enemy queen is that cell is on or within 2 cells of her head in 26% of all SSS pings in 1060356 (r120-143, 1,492 of 5,832) and 39% in 1067641 (r120-166, 1,531 of 3,926); a random cell would be there 0.6% and 1.1% of the time (`b_sonar4.py`). Pings from dragons that cannot see her carry it, so it is relayed. In 1063806 the cell stayed within 2 cells of forgot's queen in 29-52% of pings through rounds 140-179 although no SSS head had her head in view for 20 rounds at a time: she was pacing where she had last been seen, so the team repeats an old sighting. In 1060356 the later killer received rays carrying her cell at rounds 123-127 and 132-133, when it was 14-20 steps from her, and closed in from round 133. SSS sends 1-7 pings a round until round 119 and four per dragon per round from round 120 (130-250 a round) in all three games.
- **forgot: weak.** The same search finds her cell in 5% (1059840, r100-157) and 9% (1067641) of forgot's pings, against 0.6-1.1% by chance: some dragons send it, the team as a whole does not repeat it. Most of forgot's value is positions of its own dragons (the sender's own head in 67% of pings, another own head in 25%; `b_sonar2.py`). Direct rays from a dragon that sees her to the later killer are rare for both teams: of the rays that ended on the killer in the 40 rounds before the 11 kills, 10 of 158 (SSS) and 2 of 131 (forgot) came from a dragon that had had her in view in the last 3 rounds (`b_rays.py`). Whatever reaches the killer comes through relays.
- **Vibing++: not found.** The same search on 1069168 and 1063780 gives nothing above chance.

### 3. A boxed-in queen

"Boxed in" = no free cell next to her head at the start of her turn.

- **A queen of 4 or more: SSS and forgot shed 2 from the tail and stay; they never cut.** Over all games (`b_qsplit.py`, `b_out/qsplit_all.txt`): Vibing++ made 67 cuts that left a queen of 8+ with 2-3 segments, in 61 of 502 games (mean length before 19; 86 -> 3 and 85 -> 3 at the top). SSS made 0 in 503 games and forgot 0 in 632. Instead they split 2 off the tail in round after round: SSS has 29 runs of three or more such rounds in 22 games (526 segments, longest 28 rounds), forgot 116 runs in 88 games (2,488 segments, longest 43 rounds, 11 still running at round 499).
- **In the games read:** both teams' 25-long queens on Slithery Fight shed 2 for nine rounds with no free cell and lose nothing (1063806, 1060000). forgot's fed queen: 82 -> 62 (1063806 r490-499, boxed by her own segment 4 after a tight loop for two pearls), 102 -> 66 (1067636 r482-499, her only exit a portal mouth she did not take), 77 -> 75 (1067446 r343, she had caught her own tail and the two shed segments were the ones in her way), 28 -> 26 and 43 -> 41 (1067634 r382, r450). All 18 SSS queen splits and 22 of forgot's 23 queen splits made with no free cell were of this kind (the other was a 4 -> 2+2).
- **Which rule is better depends on what blocks her.** Blocked by her own tail end or by another dragon that will move: shedding costs 2 and Vibing++'s cut costs everything behind the blocker (1067446: 2 against 70). Blocked by her own segment 4 for good: both end at 3, forgot's rule more slowly, which saved a 62-long queen at round 499 in 1063806. Over all games the shedding turned 5 forgot games and 3 SSS games that were lost on the queen rule with both queens alive into losses they would not have been without it (same games, nothing else changed).
- **A queen of 2-3: she dies, in all three teams.** Over all games (`b_qdeath.py`): SSS's queen died other than by an enemy ram in 50 games (10%); in 48 of the 50 she had no free cell; she was 2-3 long in 44. forgot: 71 games (11%), 66 with no free cell, 70 of them 2-3 long. The reason in the replay differs (SSS's queen moves into a body: `self` 23, `body` 18, into a head 9; forgot's gives the suicide order: `noaction` 51), the situation is the same as Vibing++'s `noaction` deaths.
- **How she gets there.** One-cell dead ends (kelp on three sides): 15 of SSS's 48, 29 of forgot's 66. A team-mate's body on at least one side: 23 of 48 and 20 of 66. An enemy head within 3 steps in only 12 of 50 and 27 of 71. She had split in the 20 rounds before in 32 of 50 and 48 of 71, so the "mother" split that leaves her 2 long is what removes her way out. Maps: Portals 16 of SSS's 50; Maze 12 and Portals 11 of forgot's 71.
- **SSS also splits to wait.** With one free cell and a feeder about to die next to her, SSS's queen splits off 2 and stays (1063806 r448, r449, r454, r457; 1067634 r471). Not seen for forgot or Vibing++.

### 4. How does SSS keep its queen alive?

- **The numbers over all games** (`b_out/cand_tab.txt`): SSS's queen is dead by round 100 in 11 of 139 large-map games and 11 of 147 medium ones (8% and 7%). forgot: 49 of 161 and 38 of 191 (30% and 20%). Vibing++: 13 of 127 and 35 of 147 (10% and 24%). On small maps all three lose her early: 66 of 217, 104 of 280, 124 of 228.
- **She does not forage like the others.** In the 10 games read she eats 2.1 natural pearls per 100 rounds against 4.7 for the average SSS dragon, and less than the average in all 10 (`b_qhome.py`, `b_out/qhome15.txt`). forgot's queen: 3.5 against 4.6.
- **She stays near her spawn.** While she is 5 or shorter she is 10.8 cells from her spawn on average and the other SSS heads 16.7; nearer than they are in 8 of 10 games. She comes back to the same corner cells to split: (46,38) four times in 1060356 and twice in 1059840, (29,7) twice in 1067644. On Tower Defense she is 0-7 cells from her spawn at all 16 checkpoints.
- **So she is inside her own team, not ahead of it.** Own heads within 8 cells: 6.3 for her, 6.5 for the average SSS dragon. Enemy heads within 8 cells: 1.1 for her, 1.7 for the average SSS dragon. forgot's queen: 1.6 against 1.4, more enemies than its average dragon.
- **She stays 2-3 long**, so a mother split never costs much and a ram on her costs the team two segments; but a 3-long queen cannot split to stand still (1059840 r157) and cannot outrun anything.
- **When an enemy head is within 3 steps** (39 rounds in 6 of the 10 games): she moves one step, 39 times of 39; 36 times the step leaves the nearest enemy head further away. The three steps towards an enemy were 1059840 r120, and the two fatal forced ones (1059840 r157, the corridor end; 1067636 r181, the portal pocket). She never splits and never pays for a second step.
- **Allies do not turn towards the intruder.** In those rounds she had no own head within 6 steps in 10, one in 12, two in 4, three or more in 13. Own dragons within 6 steps of her ended their move nearer to the intruder 40 times and further from it 44 times. Six intruders were rammed while within 6 steps of her (1059834 r276, a 24-long by a 4-long; 1059840 r125; 1067641 r148, r158, r162; 1067629 r57), each by a dragon that had the intruder within its own reach. That is the ordinary "ram a head you can reach" behaviour happening near the queen because she lives among her own dragons (inference); no dragon was seen moving between her and an intruder.
- **How she still dies** (5 deaths read): a 5-long sprinting 5 steps while she had four own heads within 6 steps (1067641 r166); an 18-long that she walked towards without ever having it in her view, striking with 5 free steps (1060000 r479); a 3-long follower and a corridor end, with 19-21 SSS units on the board and none near her (1059840 r157); a blind step through a portal (1067636 r181); a 2-3-long that came 20 steps while she walked towards it on a small map (1067629 r103).
- **Answer.** She is steered in two ways that can be seen: kept near home and kept from eating her way outward. She is not steered away from enemies beyond the one-step retreat, and nobody guards her.

### 5. Feeding and the end game

- **When, over all games** (`b_feed.py`, `b_out/feed_all.txt`; round-500 games with the own queen alive at round 300):

  | | Vibing++ (142 games) | SSS (193) | forgot (189) |
  |---|---|---|---|
  | queen first 8 or longer by round 250 | 77 | 0 | 139 |
  | ... by round 300 | 102 | 3 | 175 |
  | ... never | 10 | 79 | 1 |
  | mean queen length at r300 / r400 / r450 / end, enemy queen alive at r300 | 11 / 20 / 29 / 37 | 3 / 16 / 21 / 35 | 23 / 33 / 44 / 50 |
  | same, enemy queen dead by r300 | 12 / 23 / 31 / 38 | 3 / 4 / 9 / 23 | 22 / 34 / 42 / 46 |
  | at r400 the queen is the team's longest dragon | 69 of 110 | 31 of 163 | 110 of 162 |

- **forgot feeds its queen from about round 200-225, whatever the enemy queen is doing.** In the games read she is 6 long at round 206 (1067446), 213 (1063806), 220 (1067667) and 225 (1067636). Two games are later: 297 on Portals (1067634), and 1067620, where she grows on natural pearls to 10 by round 357 and gets her 23 corpse pearls only in rounds 400-449. Before it starts, the small dragons gather: own heads within 8 cells of the queen go from 5 to 21 between rounds 120 and 200 in 1067446.
- **SSS keeps its queen 2-3 long and decides late.** With the enemy queen alive at round 300 (102 games) its queen is 8 or longer by round 350 in 27, only after round 425 in 39 and never in 28. With the enemy queen dead by round 300 (91 games): by round 350 in 3, only after round 425 in 37, never in 51. In the games read: round 305 (1063806, the round after an SSS dragon saw forgot's 33-long queen), 302 (1067634), 438 (1060000, although SSS dragons had seen Kaizen's 17-22-long queen at rounds 364-394), 441 (1059834, enemy queen dead since round 72), never (1060356, enemy queen dead; she ends 3 long and wins).
- **How.** The same in both teams: small dragons walk to within a few cells of the queen and die there with a free cell available. forgot uses the suicide order. SSS's feeders die by a move they cannot pay for (a 2-long moving two steps, reason `noaction`) or by a move into their own body (`self`), ending 1-2 cells from her head. Near the end dragons of 20-36 do it too (forgot 30-long, 1063806 r411; SSS 29-long, r468; Kaizen 36-long twice, 1060000).
- **What it costs.** Each dead feeder leaves half its length as pearls, and the queen gets about two thirds of those: 2.6 to 2.7 segments of feeder per segment she gains, on both sides (1063806: SSS 216 for 81, forgot 183 for 70).
- **Who is the leader.** forgot: the queen while she lives (in 1067667 a second dragon of 62 as well, from round 380); if she is dead, one other dragon from about round 300 (1059834: 34 at r325, 88 at the end; 1067654: 8 at r325; 1067641: 22 at r325, 63 at the end), built the same way, with dragons of 32-57 killing themselves next to a longer one (1059834 r424, r451; 1067620 r432). SSS: a separate dragon from round 200-350 (1059834 #458/#579: 29 at r200, 83 at r375; 1060356 #105: 25 at r225, 95 at r475; 1060000: 29 at r375, 58 at the end), and the queen as well only at the end or when the enemy queen is seen to be long.
- **Share of the team's length in its longest dragon at the end** (final lengths in `games.csv`). forgot: 25% (1059840, 1067620), 29% (1067654), 31% (1063806), 32% (1067636), 33% (1067667), 38% (1063814), 51% (1059834), 52% (1067641), 71% (1067446), 73% (1067634). SSS: 9% (1060356, after its 95-long was rammed), 16% (1067641), 23% (1059834), 29% (1059840), 39% (1063806, 1060000), 60% (1067636), 100% (1067634). forgot is not always the more concentrated team; it is when its queen is dead and one dragon is all it has left to build (1059834, 1067641) or when the game is a pure queen race on a small or medium map (1067446, 1067634).
- **What each does with a queen alive at round 300-400.** forgot: has been feeding her for 100 rounds and keeps on; she is the team. SSS: leaves her 2-3 long near home and, if the enemy queen is dead, may never feed her. Neither hides her; both keep her moving every round.
- **Results with both queens alive at round 500** (`b_out/cand_tab.txt`): forgot wins 52 of 71 (its queen 50.6 long on average against 38.5), Vibing++ 24 of 40 (34.0 against 33.1), SSS 27 of 48 (36.8 against 38.0).

### 6. Leaders: kept alive or lost

- **Lost to small dragons, as with Vibing++.** Own dragons of 15+ rammed in the games read: SSS 12 (attacker 3 long 2, 4 long 3, 5-9 long 7); forgot 21 (2 long 3, 3 long 10, 4 long 6, 5-9 long 2). The attackers walk a long way to them: 38 steps in 20 rounds to SSS's 95-long (1060356 r493, then three rounds 3-5 steps away, then a 5-step sprint); 30 steps in 20 rounds to forgot's 42-long (1067654 r394); 28 steps in 20 rounds by an SSS 3-long to a forgot 22-long (1059840 r275); 34 steps in 20 rounds by a forgot 3-long to a Sponge 21-long (1067654 r216).
- **Kills of enemy dragons of 15+.** SSS: 13 (attacker 2 long 2, 3 long 8, 4 long 3; from the next cell 3, with a 2-3-step move 9, 4+ steps 1). Typical SSS attacker: a 2-long that eats one pearl and rams with a 2-step move (four of five in 1059840). forgot: 7 (3 long 2, 4 long 2, 5-9 long 3).
- **SSS may broadcast the enemy leader's cell as it does the queen's** (weaker evidence). With the enemy queen dead, a field of SSS's sonar value was within 2 cells of the head of the enemy's longest dragon in 20-38% of SSS pings in some 10-round blocks and 0% in the others: rounds 220-229 and 240-249 in 1059834 (SSS rammed forgot's longest at rounds 238 and 276), rounds 220-229 and 250-259 in 1059840 (rams at 236, 248, 275). Chance is 0.6%. The field sits at a different place in the value than the queen's and I found it by the same blind search, so it needs a second look before anyone builds on it (`b_out/sonar4_*_leader.txt`).
- **The split trick** (a long dragon splits and rams with the cheap part). SSS: 1 clear case of 13. 1059834 r482-484: a 15-long splits 15 -> 2+13 four steps from forgot's 17-long and the 2-long front part rams it two rounds later. One more attacker had split in the five rounds before (1067641 r202-207), but that was an ordinary 4 -> 2+2 followed by one pearl. forgot: 0 of 7.
- **Protection: none seen.** No escort, no retreat. SSS's 95-long in 1060356 had an enemy 7-long 3-5 steps from its head for three rounds and did not use its 24 free steps to leave.
- **Reverse splits are something else** (a long dragon keeps 2-3 segments at the front and the rest becomes a child with its head at the old tail). forgot does it when the head has no free cell: 225 of 272 in 13 games; the 2-long front part then dies. SSS does it with a free cell: 63 of 74. For neither team does it look like protection of the leader (inference): forgot's is a rescue of a trapped dragon, SSS's a way to turn round or to drop a 2-long.
- **Merging.** Both teams kill their own long dragons next to a longer one or next to the queen: forgot 18 deaths of 15+ by the suicide order with a free cell, SSS 8 (6 by a move into itself, 2 `noaction`).

### 7. Openings

The table for every game is in the per-game notes. All games in one view (`b_opentab.py`, `b_out/opentab15.txt`):

| game | map | team | units r30 / r50 / r100 | natural pearls eaten r0-39 / r40-89 | non-ram deaths r0-99 | cells visited by r100 |
|---|---|---|---|---|---|---|
| 1059834 | Around UNSW | SSS | 29 / 52 / 62 | 85 / 189 | 70 | 1,162 |
| | | forgot | 21 / 26 / 37 | 47 / 72 | 36 | 1,043 |
| 1063806 | Slithery Fight | SSS | 31 / 41 / 59 | 62 / 111 | 41 | 771 |
| | | forgot | 42 / 55 / 56 | 135 / 179 | 189 | 764 |
| 1060000 | Slithery Fight | SSS | 40 / 50 / 61 | 96 / 128 | 62 | 819 |
| | | Kaizen | 37 / 46 / 60 | 127 / 159 | 160 | 765 |
| 1059840 | Australia | SSS | 16 / 20 / 21 | 22 / 23 | 11 | 788 |
| | | forgot | 14 / 23 / 60 | 22 / 117 | 28 | 1,278 |
| 1060356 | Australia | SSS | 18 / 32 / 61 | 36 / 100 | 19 | 1,299 |
| | | bread first search | 14 / 14 / 21 | 4 / 24 | 1 | 813 |
| 1067641 | Islands | SSS | 18 / 25 / 35 | 47 / 77 | 27 | 580 |
| | | forgot | 20 / 35 / 62 | 56 / 117 | 16 | 1,113 |
| 1067636 | Maze | SSS | 10 / 16 / 35 | 29 / 65 | 24 | 387 |
| | | forgot | 12 / 17 / 26 | 27 / 40 | 15 | 396 |
| 1067654 | Australia | forgot | 12 / 21 / 35 | 14 / 68 | 11 | 1,055 |
| | | Sponge | 12 / 17 / 48 | 10 / 99 | 11 | 940 |
| 1063814 | Around UNSW | forgot | 18 / 27 / 62 | 32 / 122 | 39 | 1,091 |
| | | Sponge | 25 / 40 / 62 | 65 / 123 | 30 | 1,063 |
| 1067667 | Around UNSW | forgot | 25 / 31 / 46 | 58 / 99 | 59 | 1,125 |
| | | bread first search | 22 / 31 / 58 | 55 / 109 | 49 | 976 |
| 1067446 | Maze | forgot | 8 / 14 / 31 | 23 / 48 | 12 | 390 |
| | | bread first search | 7 / 11 / 23 | 14 / 34 | 7 | 291 |
| 1067620 | Australia | forgot | 14 / 21 / 62 | 18 / 127 | 23 | 1,315 |
| | | Vibing++ | 11 / 9 / 9 | 15 / 31 | 27 | 454 |
| 1067629 | Stripes | forgot | 3 / 8 / 12 | 14 / 27 | 4 | 226 |
| | | SSS | 4 / 6 / 5 | 14 / 30 | 19 | 162 |
| 1067644 | Tower Defense | SSS | 2 / 2 / 11 | 2 / 28 | 4 | 174 |
| | | forgot | 2 / 2 / 10 | 0 / 23 | 3 | 144 |
| 1067634 | Portals | SSS | 8 / 13 / 33 | 27 / 65 | 34 | 229 |
| | | forgot | 10 / 13 / 34 | 40 / 86 | 48 | 237 |

- **forgot does not out-eat everybody.** Its natural pearls in rounds 40-89 against the opponent's: 5.1 to 1 and 4.1 to 1 on Australia against SSS and Vibing++, 1.6 and 1.5 to 1 against SSS on Slithery Fight and Islands, 1.4 and 1.3 to 1 on Maze and Portals; but 0.4 to 1 against SSS on Around UNSW, 0.6 on Maze, and 0.7-1.0 against Sponge and bread first search in three games. Ahead by 1.3 or more in 6 of 13 games, behind by 0.9 or less in 5.
- **What it does when it is ahead: it spreads.** On Australia its heads stand in 20 of 64 squares of the board at round 60 (SSS 9, Vibing++ 6) and it has visited 1,278-1,315 cells by round 100 (SSS 788, Vibing++ 454). On Islands 1,113 against 580. Parent and child part faster after a split (6.4-7.3 steps apart after five rounds against Vibing++'s 4.0-5.3 in 1067620). Its eaters are almost all 2-3 long. It does not sprint to pearls (0-4 paid steps per 10 rounds for the whole team; SSS 0-7).
- **SSS when it is ahead** (1059834, 1060356, 1067636): the same, plus longer eaters. It splits at 5 into 2+3 as well as at 4 (15 of 92 early splits in 1059834) and 73 of its 308 natural pearls there were eaten by dragons of 4 or more (forgot: 1 of 128).
- **Split timing.** Both split as soon as a dragon is 4: 4 -> 2+2 is by far the commonest split in rounds 0-60 (1059834: forgot 40 of 45, SSS 69 of 92; 1063806: forgot 122 of 156, SSS 40 of 68). Neither has a "stop splitting" round before the 64-unit limit is reached (forgot at round 70 on Slithery Fight, 90-100 on Australia and Islands; SSS at round 70 on Around UNSW, 100 on Australia).
- **Dead ends and small rooms: both walk in and die.** Non-ram deaths in rounds 0-100 over the games read: forgot 488, of which 484 with no free cell (477 by the suicide order); SSS 317, of which 314 with no free cell (225 by a move into its own body, 89 into another body). The same cells take dragon after dragon: (30,41) 14 times and (33,22) 14 times on Around UNSW, (10,26) 11 times on Australia, (54,18) 14 times on Slithery Fight, (36,23) 10 times on Maze. A dragon walks into a pocket for a pearl, cannot turn, dies, and its pearl draws the next one. On Slithery Fight this cost forgot 429 segments in 100 rounds (204 pearls eaten back) and left it level with SSS at round 100 (137 each) after eating 350 natural pearls to SSS's 200.
- **Self-kills by choice in the opening: none.** 4 of forgot's 488 and 3 of SSS's 317 early non-ram deaths had a free cell.
- **First contact.** From round 40 on the bigger maps the teams ram each other about one for one (1067641: 30 head-on deaths each in rounds 40-99), which holds the smaller team down (SSS 25-31 units from round 50 to 90 while forgot goes from 35 to 58).

### 8. What do they do that Vibing++ does not, and the other way round?

- **The three "self-kill" styles are one behaviour.** Vibing++ orders a split that cannot be made, forgot gives the suicide order, SSS moves into its own body. In all three the dragon had no free cell (Vibing++ 347 of 359 in rounds 0-100 of six of A's games, forgot 484 of 488 and SSS 314 of 317 in the games read). It is not a choice and not a difference between the teams. It does matter for results as a cost that all three pay: see question 7.
- **Reverse splits.** Vibing++ and SSS do them with a free cell as well (38 of 70 in 1063780; 63 of 74 for SSS); forgot only when boxed in (225 of 272). No effect on results was seen.
- **Vibing++ and SSS ram the queen with long dragons; forgot does not** (question 1). It matters: forgot never rammed her in 37 of the 104 games in which it passed up an in-view chance, and won 12 of those 37.
- **Vibing++'s queen grows on her own to 5-13 by round 100-200; SSS's and forgot's stay 2-3.** A 12-13-long queen has 3-4 free steps and walks away from followers (A's finding), and when rammed she is a large loss. The 2-3-long queens of SSS and forgot cost nothing when lost in length terms, but SSS's lives longer because of where she is, and forgot's dies early because of where she goes.
- **Vibing++ cuts a boxed-in queen to 3; SSS and forgot shed 2 a round** (question 3). It decided 1063789 against Vibing++ (85 -> 3 at round 484); forgot's rule left its queen 62 long instead of 3 in 1063806 (a game lost anyway) and cost her 2 instead of 70 in 1067446.
- **forgot feeds from round 200; Vibing++ and SSS late** (question 5). It wins forgot the games in which both queens live (52 of 71) and loses it games in which it runs out of feeders (1063806: 10-14 units from round 425, its queen stuck at 77-82 while SSS's went from 64 to 85).
- **SSS decides whom to feed by what it knows of the enemy queen; forgot does not** (inference from the table in question 5: SSS's queen is 16 long at round 400 when the enemy queen is alive and 4 when she is dead). When SSS gets it wrong it loses outright (1060000: a 58-long leader and an 18-long queen against a 47-long queen).
- **SSS broadcasts the enemy queen's cell to the whole team from round 120; forgot barely; Vibing++ not found** (question 2).
- **SSS's queen waits for feeders by splitting** (5 times in 2 games, 2 segments each). Small cost, no result changed.
- **forgot's queen keeps a 2x2 loop even with an enemy head next to it** (1059840 r208, 1067641 r166) and sometimes steps next to an enemy head (1067654 r86): 11 of her 88 close-round moves ended nearer to the enemy, 3 of them fatal. SSS's and Vibing++'s queens step away (36 of 39, the 3 others forced or harmless; 151 of 151).

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

## What the losses of SSS and of forgot have in common

Counts "over all games" are from `b_out/cand_tab.txt` (`b_cand.py` on the lead's candidate lists; games against 2000+ teams, Schooltime left out). The games read are named.

### SSS (177 losses in 503 games; 5 losses read: 1060000, 1059840, 1067641, 1067636, 1067629)

How its losses end: longest dragon with both queens dead 59; wipe-out with both queens dead 49; queen rule with its queen dead and the enemy's alive 28; queen rule with both alive 21; wipe-out with its queen dead and the enemy's alive 20.

1. **It is not good at the queen race.** With both queens alive at round 500 it wins 27 of 48, with its queen 36.8 long on average against 38.0; 21 of its losses are of this kind. It leaves its queen 2-3 long until round 300-440 and sometimes feeds a leader instead while the enemy queen lives. Read: 1060000 (leader 58, queen 18, enemy queen 47). It won 1063806 and 1067634 only by turning 39% and 100% of the team into the queen in the last 200 rounds.
2. **It loses the longest-dragon race with the bigger team.** 20 of its 59 losses on the longest dragon came with the larger total length, 27 with more units. Read: 1067641 (41 units and total 237, longest 37, against a 63-long); there its leader got 5-9 pearls per 50 rounds after the queen's death.
3. **It can lose the opening on a big map to a team that spreads wider.** Read: 1059840 (21 units against 60 at round 100; 788 cells visited against 1,278) and 1067641 (35 against 62; 580 against 1,113). Australia is its weakest large map (21 wins in 38).
4. **Its queen walks into what she cannot see.** 3 of the 5 queen deaths read: a portal with an enemy beside the exit (1067636 r181), an 18-long 5 steps away with 5 free steps (1060000 r479), the closed end of a corridor with a follower behind her (1059840 r157). Over all games she also dies without an enemy ram in 50 games (10%), 48 of them with no free cell and 16 of the 50 on Portals.
5. **It never rams a queen it cannot see.** 0 of 273 chances out of view over all games. Read: 1067636 r485-486, where one ram on a queen that had stood still for four rounds would have won.
6. **Its 95-long leader can be rammed like anyone's** (1060356 r493, a win only because the 3-long queen was alive). 12 own dragons of 15+ rammed in the 10 games read.

### forgot (273 losses in 632 games; 6 losses read: 1059834, 1063806, 1067654, 1063814, 1067644, 1067634)

How its losses end: queen rule with its queen dead and the enemy's alive 66; longest dragon with both dead 66; wipe-out with both dead 60; wipe-out with its queen dead and the enemy's alive 59; queen rule with both alive 19; other 3.

1. **Its queen dies early.** Dead by round 100 in 191 of 632 games (49 of 161 large, 38 of 191 medium, 104 of 280 small); it wins 76 of those 191 (40%) and 283 of the other 441 (64%). Around UNSW is the extreme: dead by round 60 in 19 of 44 games, 15 wins in 44. Read: 1063814 (r34), 1059834 (r72), 1067654 (r86): 3 of the 6 losses. She walks out of her team in the opening (1067654: 27 cells from her spawn at round 40 with no own head within 6 steps) and does not always step away: 11 of her 88 close-round moves in the games read ended nearer to the enemy head, and 3 of those were her death.
2. **It does not get to the enemy queen.** In 5 of the 6 losses read forgot never had one turn with a free path to her head (1059834, 1063806, 1063814, 1067644, 1067634); in two of them its own queen was dead from round 34 and 72 and a ram on hers was the only way left to win. Its long dragons do not ram her when they do get near (0 of 22 at 10-12 long, 21 of 65 at 5-9 long over all games), and in 37 games it passed up an in-view chance and never killed her (12 wins in those 37).
3. **Its leaders are rammed by small dragons.** 21 own dragons of 15+ rammed in the 13 games read, 19 of them by a 2-4-long. Read: five in 1063814 (18, 25, 17, 46 and 47 long); the 42-long at round 394 that decided 1067654.
4. **A fed queen traps herself.** 116 runs of three or more rounds of shedding in 88 of 632 games, 2,488 segments in all, 11 runs still going at round 499; 5 queen-rule losses would not have been losses without it. Read: 1063806 (82 -> 62 in the last ten rounds), 1067636 (102 -> 66, a win), 1067634 (twice, 2 segments each, lost by 6).
5. **Feeding by the clock burns the team.** Read: 1063806, where it fed from round 205, had 10-14 units from round 425 and its queen stopped at 77-82 while SSS, with 44-51 units left, took its queen from 64 to 85. And it does not always put everything into the queen: 1067634 (53 in the queen, 20 elsewhere, lost by 6).
6. **Dead-end deaths are heaviest for forgot on maze-like maps.** 189 in the first 100 rounds of 1063806 (429 segments) against SSS's 41. (Kaizen, which opens the same way, has 163 against SSS's 63 on the same map.) forgot out-ate SSS 350 to 200 there and was level at round 100.
7. **It loses ram exchanges on small maps to SSS** (1067644: 7 rams against 12 in rounds 100-199, 6 units against 22 at round 200).

### Shared by both

- Neither rams a queen outside the attacker's own view, neither escorts its queen, neither protects a leader, and both lose 2-3-long queens to cells with no way out (SSS 10% of games, forgot 11%).
- Both lose small dragons in dead ends at a steady rate through the whole game (in 1059834, SSS: 45-82 such deaths per 100 rounds).

## Where `deep-read.md` or `findings.md` looks wrong or thin

1. **"Small dragons kill themselves from round 0" is not a behaviour, and not a difference between the teams.** `deep-read.md` (recurring pattern 2, answer h) and the fact sheet treat Vibing++'s early `noaction` deaths as a choice that "costs a segment each time", and the brief sets "Vibing++ self-kills, SSS has none, forgot uses the suicide action" side by side. Checked with `b_open.py` on six of A's games (1063780, 1067620, 1063789, 1069168, 1064500, 1063792): 347 of Vibing++'s 359 non-ram deaths in rounds 0-100 happened with no free cell next to the head. The same holds for forgot (484 of 488 in 13 games), SSS (314 of 317 in 10), and the other teams in those games (tungtung67 20 of 20, horse 26 of 26, bread first search). A dragon with no free cell must still give an order; Vibing++'s bot gives a split order, forgot's the suicide order, SSS's and horse's a move into a body, tungtung67's and bread first search's a move into kelp. The replay then shows `noaction`, `self`, `body` or `wall`. What matters is why so many dragons have no free cell: they walk into one-cell dead ends and small pockets for a pearl ((30,41) on Around UNSW took 14-17 dragons of one team per game) and cannot turn round.
2. **"SSS has no `noaction` deaths in its openings" is true and says nothing.** SSS had 11-72 such forced deaths per game in the first 100 rounds of the six large-map games read, and more than forgot on Around UNSW (72 against 36 in 1059834).
3. **The queen table in `findings.md`, section 4, splits one event over two columns.** "By her own move" (SSS 11%, forgot 4%) and "self-kill (`noaction`)" (SSS 0%, forgot 8%, Vibing++ 22%) are the same thing for these teams: a 2-3-long queen with no free cell. 48 of SSS's 50 and 66 of forgot's 71 such deaths had no free cell (`b_qdeath.py`). The comparable numbers are: Vibing++ 23% of games, forgot 11%, SSS 10%, and ours 28%.
4. **"forgot rams in only 254 of 457, 70% with a 2-3-long attacker" hides a clock.** forgot's 2-3-longs take 85 of 178 in-view chances before round 100 and 136 of 139 after it; before round 100 the chance is taken when the attacker is not outnumbered within 4 steps (47 of 51) and mostly not when it is (38 of 127). The 23% for 4-longs is the split at 4: 40 of the 41 turns not taken were split orders.
5. **"forgot out-ate Vibing++ 2-4 to 1 in rounds 40-90"** (`deep-read.md`, finding 3 and answer h) is a fact about those five games, not about forgot. Against SSS, Sponge and bread first search in the games read here forgot's ratio in rounds 40-89 runs from 0.4 to 5.1 and is below 1 in 7 of 12 games. Where it is far ahead (Australia, Islands) it is by spreading over the board.
6. **"In A's games forgot put 44-100% of its length into one dragon."** In the 11 round-500 games read here the share is 25-73%, and below 40% in 7. SSS's is 9-100%. The high shares are games in which forgot's queen was dead or the game was a pure queen race.
7. **`deep-read.md`, answer g: "whether [reverse splits are] meant as protection or only a way to turn round cannot be told".** The free-cell check tells the two apart for forgot: 225 of its 272 reverse splits were made with no free cell at the head, so they are the rescue of a trapped dragon (the 2-long front part then dies). For SSS 63 of 74 were made with a free cell; in 1063780 Vibing++'s were 38 with and 32 without.
8. **"With three or more allies near, intruders are rammed by an SSS dragon in 27% of approaches" should not be read as an escort.** In the 39 close rounds read, SSS dragons within 6 steps of the queen moved nearer to the intruder 40 times and further from it 44 times. The rams are the ordinary ram on a head within reach, made near the queen because she lives inside her team.
9. **The follower is not a forgot speciality.** `deep-read.md` saw forgot's small dragons follow Vibing++'s queen for 30-110 rounds. SSS has the same followers (14 streaks in 10 games, the longest 30 rounds), and Vibing++'s #3 followed forgot's queen for 20 and 18 rounds in 1067620.
10. **Thin in `deep-read.md` on 1067620 (game 3):** forgot passed seven in-view turns on Vibing++'s queen before the kill, five of them by a 12-long that walked beside her for five rounds (r169-173). And the killer's last move was 6 steps with 3 paid although a 4-step path was free.
11. **Thin in `findings.md`, section 3:** the rule "never outside the attacker's own view" has a price that can be shown: 1067636 r485-486 for SSS. It is a limit of all three bots, not a piece of good judgment.

## Things I could not determine from replays

1. **What makes a forgot 2-3-long hold back before round 100.** The head count within 4 steps separates the turns well (47 of 51 against 38 of 127) but 38 outnumbered dragons rammed all the same and 4 that were not outnumbered did not. Whether the real test is the head count, something it stands for, or a round number other than 100 exactly, the replay does not say.
2. **What forgot's dragons of 5-12 are for** when they walk past a queen in view. They are too long to be foragers (forgot splits at 4), 19 of 31 had been eating dead team-mates' pearls, and none went on to feed the queen or the leader within 40 rounds. A leader in the making that is not to be risked is my reading (inference); the replay does not show a role.
3. **What starts SSS's queen feeding.** It began the round after an SSS dragon saw forgot's 33-long queen (1063806 r304-305) and did not begin after SSS dragons saw Kaizen's 17-22-long queen (1060000 r364-394). A length threshold, a comparison with its own leader, or chance: two games cannot tell.
4. **The full layout of SSS's sonar value.** One field is a cell that tracks the enemy queen; a second field lower in the value tracks her too; the top 12 bits were the same in every value I looked at; a field at bits 10-17 equals the low 8 bits of the round number in 46% of pings (1060356). The bit offsets change with the map size. I did not decode the rest, and I did not find what the cell holds when it is not the queen.
5. **Whether SSS's hunters act on the broadcast cell.** The cell is there and the later killer received it (1060356 r123-133), but its path afterwards was not a straight line to her (14-20 steps away for ten more rounds).
6. **What Vibing++'s sonar says.** The search that finds the queen's cell for SSS finds nothing for Vibing++ in two games. Its value may be packed differently (relative coordinates, a hash, another unit).
7. **Why SSS's dragons stayed within 17-27 cells of their spawn on Australia in 1059840 and spread to 27-31 in 1060356** from the same spawn. In the loss 11 of its 16-20 dragons died with no free cell in the west pearl field in rounds 30-59 and 13 were rammed in rounds 61-120; whether that is the whole reason I cannot say.
8. **Why SSS's queen walked north two steps a round for five rounds in 1060000 (r475-479)** and away from her feeders. Nothing was near her that I could see as a reason.
9. **Why forgot's queen keeps to a 2x2 loop with an enemy head beside it** (1059840 r208, 1067641 r166) but steps away in 18 of 18 close rounds in 1067667. The games are from the same days; I found no condition that separates them.
10. **Whether the queen sees through kelp or portals.** "In view" in this file is the 7x7 square only.
11. **How natural pearls are placed**, and so whether the pearl in a one-cell dead end is ever worth the dragon it costs.
12. **Whether the SSS queen's wait (splitting off 2 beside a feeder) is asked for by a message** from the feeder or is her own rule.
13. **Kaizen.** Its opening and feeding look like forgot's in 1060000 (same splits, suicide orders, the same pace of feeding). Whether it is the same code I cannot know.
14. Not read move by move: the mid-game of the three small-map games beyond the ram counts; forgot's late game in 1067620 (A read that game from the other side).
