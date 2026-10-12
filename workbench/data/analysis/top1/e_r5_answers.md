## 5. Answers to the nine questions

Every number here is in a table of section 2 or in the output file named; "measured" unless marked "inference".
Medians per race unless a line says otherwise. Small maps = 1,200 cells or fewer.

### a. The leader's curve

**When each team starts and how fast it grows** (tables A1, A3; `e_a.py` gives the same every 25 rounds from 150 and
by band of total length at round 400 in `e_out/a_curve.txt`).

| small maps | longest at 300 / 350 / 400 / 450 / end | the final longest's lineage first 8 / 15 / 25 long (round) | leader feeding starts (round) | growth in the 50 rounds after take-off | growth from 400 to the end | units at 300 / 400 / end | share of potential in the longest at 400 / 450 / end |
|---|---|---|---|---|---|---|---|
| meow live bot | 4 / 9 / 10 / 16 / 20 | 336 / 406 / 426 | 401 | 11 | 10 | 26 / 21 / 7 | 0.27 / 0.53 / 0.65 |
| meow test builds | 4 / 8 / 11 / 21 / 30 | 354 / 407 / 423.5 | 401 | 18.5 | 21 | 22 / 21 / 4 | 0.20 / 0.51 / 0.71 |
| test4 (vs us) | 6 / 6 / 13 / 30 / 37 | 386 / 401.5 / 421 | 354 | 16 | 22 | 33 / 16 / 3 | 0.41 / 0.64 / 0.77 |
| WHQ (vs us) | 5 / 16 / 28 / 40 / 45 | 323 / 364 / 389 | 315 | 14 | 26 | 33 / 23 / 4 | 0.43 / 0.65 / 0.80 |
| forgot | 5 / 5 / 16 / 27 / 36 | 374 / 394 / 417 | 373 | 14 | 20 | 24 / 14 / 6 | 0.43 / 0.60 / 0.69 |
| SSS | 6.5 / 16.5 / 26 / 36 / 38.5 | 312 / 356.5 / 372 | 311 | 17 | 15.5 | 37.5 / 19 / 6 | 0.43 / 0.63 / 0.79 |
| Vibing++ | 6 / 5 / 9 / 25 / 36 | 394 / 424 / 438 | 403 | 18.5 | 20 | 29 / 25 / 8 | 0.19 / 0.48 / 0.59 |

On big maps: our longest is 10 / 13 / 14 / 14 / 23 / 35 at rounds 200 / 300 / 350 / 400 / 450 / end with feeding from
round 212 (median); WHQ 15 / 30 / 47 / 55 / 68 / 83 from round 270; test4 15 / 18.5 / 20.5 / 24 / 32.5 / 51 from round
328; forgot 6 / 13 / 29 / 41 / 52 / 55 from 303; SSS 13 / 18 / 33 / 41 / 49 / 56 from 277; Vibing++ 13 / 15 / 19 / 36 /
46 / 57 from 360. Share of potential in the longest at the end: 0.43 (ours), 0.48, 0.29, 0.49, 0.42, 0.39.

- **Share of the team's total length in the longest dragon at the end** (median; `e_out/c_leader.txt`): small maps
  51% (live bot), 57% (test builds), 64% (test4), 68% (WHQ), 53% (forgot), 68% (SSS), 44% (Vibing++); big maps 29%,
  28%, 17%, 32%, 33%, 28%, 25%. At round 400 on small maps, median longest over median total: 10 of 68 for us, 28 of
  82 for WHQ, 26 of 85 for SSS.
- **Start.** Three kinds of clock. Early: WHQ (315 small, 270 big) and SSS (311, 277). Middle: test4 (354, 328) and
  forgot (373, 303). Late: Vibing++ (403, 360) and we (401; 212 on big maps, where the 56-unit rule fires).
- **Speed once started.** The same for everybody: 11-18.5 segments in the 50 rounds after take-off. In the last
  hundred rounds the live bot's longest grows 10 and everybody else's 15.5-26, the test builds' 21.
- **By band of total length at round 400** (`a_curve.txt`, `c_leader.txt`): in level games on small maps (0.8-1.25)
  we win 9 of 30 (the red team's count: our longest 12 at round 400 and 28 at the end against the enemy's 16 and 39);
  the top three win 22 of 40. That band is a biased footing (section 2.0): at level POTENTIAL at round 300 or 350 we
  win 11 of 23 and 12 of 24. With level potential at round 400 (table A2, small maps, live bot, 18 races, 5 won) our
  longest is 12.5 / 22.5 / 34.5 at rounds 400 / 450 / end against the enemy's 15.5 / 33 / 40, and we end with 11 units
  against 4.
- **Terrain beyond the size.** Closed, crowded ground completes; open ground does not: final share of potential in the
  longest, all sides: Portals 0.85, Queen Of Spades 0.73, Tower Defense 0.70, weakhold 0.67, Maze 0.64; Slithery Fight
  0.48, Islands 0.47, Australia 0.39, Around UNSW 0.35. And the more closed the ground, the more our leader cuts
  itself: Portals 7.6 cuts a race after round 395, Around UNSW 5.6, Maze 4.2, Slithery Fight 4.2, Australia 2.6,
  weakhold 2.4, Default 1.2 (`e_out/opp.txt`).

### b. Where the leader's length comes from

Lineage of the final longest, small maps, pearls per race in rounds 250-299 / 300-349 / 350-399 / 400-449 / 450-499
(table B1):

| | natural pearls | own dragons dead by choice | other own corpses | enemy corpses | left behind in its own cuts |
|---|---|---|---|---|---|
| meow live bot | 4.0 / 5.0 / 3.7 / 3.5 / 5.0 | 0.1 / 0.2 / 0.2 / **10.2 / 6.1** | 2.2 / 2.0 / 2.0 / 1.7 / 1.5 | 0.2 / 0.4 / 0.3 / 0.4 / 1.2 | 0.0 / 0.7 / 1.4 / 2.3 / 3.7 |
| test4 (vs us) | 3.0 / 4.0 / 4.2 / 5.1 / 5.1 | 0.1 / 1.4 / **8.1** / 10.7 / 8.6 | 2.7 / 2.2 / 2.1 / 1.1 / 1.0 | 0.3 / 0.2 / 0.1 / 0.2 / 0.7 | 0.1 / 0.2 / 1.0 / 1.8 / 4.5 |
| WHQ (vs us) | 3.1 / 3.7 / 3.2 / 3.5 / 4.3 | 1.6 / **7.2 / 9.5** / 12.0 / 8.2 | 2.1 / 2.6 / 2.2 / 1.8 / 1.6 | 0.2 / 0.2 / 0.2 / 0.6 / 0.2 | 0.1 / 1.3 / 1.8 / 1.9 / 1.3 |
| forgot | 3.9 / 3.5 / 4.5 / 5.3 / 7.0 | 0.4 / 0.6 / **7.8** / 8.6 / 6.0 | 2.0 / 2.6 / 2.7 / 2.4 / 3.3 | 0.2 / 0.4 / 0.4 / 0.7 / 0.8 | 0.1 / 0.8 / 0.9 / 2.7 / 4.8 |
| SSS | 3.0 / 2.0 / 2.2 / 2.1 / 2.7 | 0.1 / **6.6 / 7.9** / 7.5 / 6.9 | 2.1 / 1.5 / 1.6 / 0.8 / 1.1 | 0.2 / 0.2 / 0.5 / 0.3 / 0.3 | 0.0 / 0.4 / 1.5 / 1.5 / 0.9 |
| Vibing++ | 3.5 / 3.7 / 4.3 / 5.1 / 6.8 | 0.8 / 1.6 / 2.2 / **10.3 / 6.1** | 2.0 / 2.0 / 2.0 / 1.8 / 1.9 | 0.2 / 0.1 / 0.3 / 0.5 / 0.5 | 0.4 / 0.6 / 0.9 / 2.1 / 1.8 |

- Natural pearls: 3-5 per 50 rounds for every leader, with or without a pearl zone. Paid steps: 0.0 for every team.
  Enemy corpses: under 1.5.
- The difference is feeding. Split by time it sits before round 400: in rounds 400-499 our lineage gets 16.3
  pearls of dragons dead by choice and the others 14.4-20.2; in rounds 300-399 ours gets 0.4 and theirs 8.4-16.7
  (Vibing++ 3.8). Split by what is fed it sits in the whole dragons (two bullets down).
- The team's cost: dragons dead by choice per 50 rounds have a summed length of 49 and 27 (ours, rounds 400-449 and
  450-499), 50 and 30 (our opponents), 31-39 and 20-26 (top three). Per segment a feeder spends, the final lineage
  gains 0.23 (live bot), 0.29 (test builds), 0.24 (our opponents), 0.27-0.29 (top three) on small maps and 0.16 / 0.14 /
  0.09 / 0.15-0.19 on big maps (table B2). Half is lost by the rule of the game; the other quarter is pearls that
  somebody else eats.
- Who eats the pearls of a death by choice, like for like (rounds 300-499, "The same test for every team" in section
  2): final lineage 39% (ours), 39% (our opponents), 45% (top three) on small maps; other own dragons 50-55%; the
  enemy 4.0% of ours (4.7% for the live bot) against 2.3% and 1.2%; nobody 7% against 4% and 3%.
- What is fed: in small feeders we match everybody (42-46 pearls a race from dragons of 2-4 on small maps; the top
  three 35-54; test4 and WHQ 51 and 69). test4 and WHQ add whole dragons: 26-29 pearls a race from dragons of 5 or
  longer against our 5-9 (top three 9-17), about half of them eaten by the final lineage; for our opponents together
  that is 10.7 of the 15.7 segments by which their lineage's intake from deaths by choice exceeds the live bot's
  (`e_merge.py`). On big maps everybody but us does it (38-124 pearls a race from dragons of 5+; ours 14-18).
- How far from the head: we die at three steps in 61% of cases and at one step in 5%; SSS at one step in 64%; the
  others at one step in 10-26%. The dragon fed eats 79-93% of the pearls of a feeder that died one step away, 66-84%
  at two steps and 63-78% at three (SSS 44-45% at three).
- Nearest enemy head when a feeder dies: median 8-11 cells for every team (9 for ours). The enemy's share of the
  pearls rises steeply only when its head is within 4 cells (15% of ours then) or 5-8 cells (8%); 48% of our feeders
  die with an enemy head within 8 cells, 34-41% of the others' (section 2h).

### c. Who the leader is and whether it lasts

| small maps | longest at round 400 is the final longest: same id / same lineage | at round 450 | cuts of the final lineage from round 400: all / with a free cell | longest of 15+ died, per race (how) | per 1,000 rounds with such a leader | steps it takes per 25 rounds at 400 / 450 | natural pearls it eats per 25 rounds at 400 / 450 | second longest / longest at the end | units at the end |
|---|---|---|---|---|---|---|---|---|---|
| meow live bot | 15% / 60% | 28% / 81% | 2.7 / 1.8 | 0.13 (6 rammed, 1 it rammed) | 2.2 | 53 / 59 | 1.5 / 2.3 | 0.33 | 7 |
| meow test builds | 12% / 56% | 32% / 88% | 2.7 / 1.7 | 0.04 (1 rammed) | 0.6 | 65 / 79 | 1.8 / 1.3 | 0.37 | 4 |
| test4 (vs us) | 3% / 59% | 31% / 76% | 2.1 / 1.5 | 0.10 (2 boxed in, 1 rammed) | 1.2 | 38 / 36 | 1.0 / 0.9 | 0.29 | 3 |
| WHQ (vs us) | 18% / 64% | 54% / 85% | 1.7 / 0.2 | 0.21 (6 by choice, 1 rammed, 1 boxed in) | 1.5 | 35 / 41 | 0.3 / 1.8 | 0.23 | 4 |
| forgot | 5% / 52% | 11% / 72% | 3.3 / 0.3 | 0.22 (12 rammed, 2 by an own dragon) | 2.0 | 52 / 56 | 2.2 / 1.7 | 0.30 | 6 |
| SSS | 31% / 79% | 55% / 81% | 1.6 / 1.6 | 0.24 (5 rammed, 4 it rammed, 1 by choice) | 2.0 | 40 / 41 | 0.2 / 0.6 | 0.15 | 6 |
| Vibing++ | 6% / 42% | 30% / 76% | 2.0 / 1.2 | 0.33 (7 rammed, 9 by choice, 4 it rammed, 2 boxed in) | 3.5 | 43 / 52 | 3.1 / 2.1 | 0.39 | 8 |

(`e_c.py`, `e_cutcost.py`, `e_cx.py` prints the rows side by side from `e_out/c_leader.txt`.)

- **Does it last?** By id, no, for anybody: the longest dragon of round 400 is the final longest in 3-31% of races. By
  lineage it is in 42-79% (ours 56-60%); at round 450 in 72-88%. The longest of round 300 is the final longest's
  ancestor in 9% of our races on small maps: the zone phase does not pick the dragon that will lead.
- **How it is lost.** A leader of 15+ dies in 0.04-0.33 races on small maps and 0.56-2.45 on big ones. Ours die only
  by rams (30 of 31 on small and big maps together for the live bot; the rammer is 2-4 long in 20 of 30); our
  opponents' die mostly boxed in on big maps (81 of 143; WHQ 38 of 55; test4 26 of 49), which ours never do. Per
  1,000 rounds with such a leader ours die at 2.2 (small) and 3.4 (big); test4's at 1.2 and 9.3, WHQ's 1.5 and 5.3,
  forgot's 2.0 and 4.9, SSS's 2.0 and 4.4, Vibing++'s 3.5 and 6.0. Median length lost 16-42; 25-30 rounds later the
  team's longest is 14-24 again (a second dragon takes over, or a new one is built: 3 to 20 in under 20 rounds in
  game 13).
- **Where it lives.** The same place for everybody: 9-15 cells from the own queen's start at round 400 (ours 9), with
  23-31 of 41 cells within four steps free (ours 28), the nearest enemy head 5-7.5 cells away at round 400 and 7-9 at
  round 450. Portals separate it from the enemy's start in a fifth to a half of the small-map races for every
  team. None of the three top teams hides its leader better than we do.
- **How much it moves, and whether it eats on its own.** Ours moves most: 53-59 steps per 25 rounds (test builds
  65-79) against 35-41 for test4, WHQ and SSS; forgot's and Vibing++'s move like ours (52-56, 43-52). It also eats
  the most natural pearls with Vibing++'s and forgot's (1.5-3.2 per 25 rounds; SSS's 0.2-0.7, test4's 0.9-1.5).
  SSS's leader stands and is fed; ours and Vibing++'s walk and eat (`LEADER_ENDGAME_PEARL_MULT 4`; inference from the
  source for ours). In game 8 that walk took our 35-long into a one-wide dead end for two pearls.
- **One leader or several.** Small maps: one. Second longest / longest at the end is 0.15 (SSS) to 0.39 (Vibing++),
  ours 0.33. Big maps: several, for everybody but SSS: 0.57-0.62 (ours), 0.72 (our opponents), 0.62 (forgot), 0.61
  (Vibing++), 0.45 (SSS); WHQ ends big-map races with 83 / 60 / 41. In 38 of our 102 lost races our final longest plus
  half of the rest of our length would have beaten the enemy's final longest (28 of the live bot's 69); for the top
  three that is 22 of 67 losses on small maps and 87 of 114 on big ones. Nobody finishes on big maps.

### d. Our two switches as natural experiments

Tables in section 2d (`e_d.py`).

1. **The leader zone.** It does what the code says and nothing for the leader. After the switch a small dragon of
   ours takes a free pearl inside its believed leader's zone in 26% / 22% of turns (small maps, rounds 300-349 /
   350-399) and 24% / 19% (big maps, rounds 150-199 / 200-249); outside the zone 87% / 87% and 77% / 77%. Of the
   pearls left lying in the zone the leader eats 12% / 11% (small) and 7% / 17% (big); an own dragon under 8 eats
   69-73% and 58-69% of them a median 7-10 rounds later; the enemy 2-6% and 8-13%; 6-12% lie for 30 rounds. The
   leader's own natural intake does not rise at the switch (1.7 to 1.6 a game on small maps, 4.0 to 3.4 on big). The
   team's falls from 20.8 to 15.6 a game on small maps and from 79.5 to 52.7 on big maps. On weakhold, where the
   zone's 181 cells are a third of the board, it starves the team: 40 natural pearls in rounds 250-299, then 16, 9
   and 3 (game 11); 47, 26 and 4 (game 12); total length 94 to 59 in a hundred rounds with nobody feeding.
2. **Feeding.** The start is where the code puts it: at round 201-224 when we had 56 units at round 200 (35 of 35
   live-bot games), at 302-375 in queen-feeding mode (20 of 27), at 401-405 otherwise. Early and late starts are
   therefore different kinds of game (the early ones are our richest), and a comparison inside a band has 6 games
   against 17: early 3 won, longest 15 / 58.5 / 75.5 at rounds 400 / 450 / end; late 2 won, 11 / 21 / 28. It shows
   that our feeding can build a 75-long when it has 54 units to spend, not that the start caused it.
3. **Which mechanism builds our leader.** Feeding, and only feeding. Small maps, lineage: the zone phase (rounds
   300-399) brings 8.7 natural pearls, 0.4 feeder pearls and 4.0 pearls of other own corpses in a hundred rounds and
   loses 2.1 in cuts; the feeding phase brings 8.5, 16.3 and 3.2 and loses 6.0. Big maps: from round 250 to 399 the
   lineage gets 1.7-2.6 feeder pearls per 50 rounds out of 18-20 segments of dragons dead by choice, and our longest
   is 10 at round 200 and 14 at round 400.

### e. The trigger of the others

Table in section 2e (`e_e.py`). It is a clock in every bot, tied to the own unit count in four of five.

| | 56+ units at round 200 | 30-55 units | under 30 units | moves with the own queen's death? |
|---|---|---|---|---|
| WHQ | round 270-272 (53 of 53 games) | 295 / 303 / 325 | 314 / 334 / 374 | no |
| SSS | 221 / 287 / 302 | 301 / 307 / 332 | 301 / 303 / 321 | no (301 / 300 / 293 / 302 by the queen's death round) |
| forgot | 300 / 303 / 344 (162 of 162) | 362 / 371 / 377 | 373 / 381 / 437 | no |
| Vibing++ | 337 / 360 / 368 | 344 / 369 / 402 | 364 / 403 / 421 | no |
| test4 | 268 / 327 / 374 | 320 / 354 / 378 | 376 / 382 / 392 | yes: 293 / 354 / 391 for a queen dead in rounds 100-199 / 200-299 / 300-399; never before round 258; while she lives it feeds her |
| meow | 201 / 205 / 224 | 331 / 401 / 405 | 402 / 405 / 422 | only through queen-feeding mode |

(Quartile / median / quartile.) Not triggers for anybody: the enemy queen's death, the distance of the nearest enemy
head to the leader (6-9 cells before and at the start), the enemy's longest dragon (8-15 at the start, any). Whether
they test the unit count or the map size cannot be told from replays; both give this table. Between their queen's
death and the start they do not gather (13-20 own heads within 15 cells of the longest, 50 rounds before the start
and at it) and they keep eating (86-106 natural pearls per 50 rounds). SSS's and WHQ's first feeders die next to a
dragon of 4-10 (games 3, 4, 23, 24, 25): they do not wait for a leader to exist; the feeding makes it.

### f. The close read

Stories in section 4. What the winners of the 14 lost races did that we did not, counted over the 14:

- **Started earlier: 11 of 14** (by 25 to 130 rounds; not games 6, 11, 14).
- **Kept the fed dragon's id.** The opponent's fed dragon kept one id for 80 rounds or more while it was fed in 8 of
  the 14 (games 1, 2, 4, 5, 7, 8, 9, 14: for instance rounds 325-430 in game 1, 351-431 in game 2, 248-499 in game
  14); ours was cut 3 to 19 times from round 395 in 13 of the 14 (twice in game 3), and with a free cell in most (15
  of 19 in game 9, 7 of 7 in game 12).
- **Merged the second dragon in the last 50 rounds: 5 of 14** (a 32-long at round 485 in game 2, 18 at 466 in game 3,
  21 at 481 in game 4, 31 at 453 in game 5, 18 at 455 in game 8; 8-13 of its 9-16 pearls eaten by the leader each
  time). We did it once (game 5, 18-long, 5 of 9 pearls) and failed three times in game 14 (3 of 27 pearls).
- **Fed where the leader was.** In game 12, 21 of our 28 deaths by choice were next to no bigger dragon; in game 5,
  20 of 39 after round 425; in game 9, 8 of 39 were next to the longest. WHQ in game 12: 11 of 11 within two steps
  of its longest.
- We were **level or ahead in the longest dragon at some round after 425 and still lost in 7 of 14** (games 3, 5, 6,
  8, 10, 12, 13). In five of the seven the segments our lineage left behind in its own cuts from round 400 are more
  than the margin (5, 6, 8, 12, 13); in game 3 nine dragons stood more than 15 cells away with 52 segments; in game
  10 it was cuts and feeders dying elsewhere.
- **Not different:** speed once started (game 2: our 10 to 56 in 50 rounds against WHQ's 7 to 52 in 50), natural
  pearls, losses of feeder pearls to the enemy (1-3 pearls a game in these 14), leader deaths (two of ours rammed, in
  games 11 and 13, at the same passage where we rammed WHQ's).
- **The other seven** were not lost in the last 75 rounds: potential or clock (1, 2, 4, 7, 14), no leader over 16 at
  any time (9), starved in the zone and then rammed (11).

And the eight wins of ours read: in six the opponent threw the race away (test4 waited for its queen or had no
leader in 21 and 22; test4 lost a 28-long boxed in after a cut in 17; WHQ ended with three leaders, lost big dragons
to our rams and to deaths without an order in 19 and 20; WHQ ran out of material in 16); in one we simply fed one id
for 150 rounds (15).

### g. The earlier trials

From `work/plan.md` (29 September to 2 October; the log has no entry called card #14 or card #22; what is known of
those two is one line each in `findings.md` section 7: "#14 split stop (no gain locally)", "#22 late feeding").

| trial | what was changed | where | result | what the replays say now |
|---|---|---|---|---|
| "ENDGAME 350" | `ENDGAME_ROUND` 400 -> 350 | local, v41 against v41, 96 games | 48 of 96, "neutral, because v41-vs-v41 is symmetric" | a mirror match cannot show a clock: both sides move |
| v46 | `ENDGAME_ROUND` 400 -> 330 | online, 50 games against five top teams and 60 against dev test 1 | 10-40 where v41 had 20-30; games decided before round 330, with identical code, went 6-18 against 11-14, "opponent drift or variance, not v46"; dev test 1 24 of 60 against 23 | no evidence either way; the old bot, the old map pool |
| ef1 | `LC_FEED_ROUND` 330 ("F330"), 300 ("F300"), 330 with `FEEDER_APPROACH` 25 ("F330A") | local against v52, 152 games | 70, 69, 68 where the base won 76 ("early feeding is locally negative again") | in a local game both teams reach "top 39 at round 400, total 220" (the log's own note); an earlier start spends units that are worth more as eaters on a rich board. And the leader it feeds is the same leader: cut 2.7 times a race and unknown to the team for 27 rounds after each cut. More feeding rounds are more rounds of that |
| fe1 | `FEED_EARLY_ROUND` 300 / 250 (dragons up to a set length may feed before the phase), `LC_LEAD_MULT` 2 / 3 | local against v52 | 73, 74, 76, 77 of 152 against 76 | neutral; same reading |
| fl1 | `FEED_LOCAL` 2 / 3: in the feeding phase a dragon dies when a visible own head within 2-3 steps has at least twice its length (not the leader: any) | local against v52 | 70, 74, 69 against 76 | this is the test "die next to a big dragon you can see" in its loosest form, and it feeds local dragons: on the same footing that is what our opponents do on big maps (58% of deaths next to a dragon that is not the longest) for 16% of the pearls to the final lineage against our 26%. A rule that sends pearls to any big dragon is not the rule proposed here |
| rl1 | `RALLY_FRESH` 15 / 25 (dragons farther than `FEEDER_APPROACH` walk to the leader's last known place) | queued 30 September | no result in the log | the log's own reason for it stands: "v41 has RALLY_FRESH=0, so dragons more than FEEDER_APPROACH (15) from the leader never go to it. That is why many small dragons remain at the end". Game 3 was lost that way (9 dragons, 6 beyond 15 cells, 52 segments, margin 6) |
| gb1, q2, sw7 | `LEADER_GROW_ROUND_BIG` 150 -> 300 ("GB300") | local | 30 of 64 against 20 (buggy base); 46 of 96 against 48; 73 of 152 against 76 | candidate 3's subject; the zone's cost is on the ladder, where the enemy eats what we leave (8-13% of the pearls left in the zone on big maps) |
| lc1, v47, as1 | `LC_LEAD_ROUND` 200 on every map (leader, zone and split stop at round 200) | local 52 of 96 against 48; online 19 of 60 against dev test 1 where the base had 23-24; with assassins 44 of 96 | "REJECT global early leader" (the user: fewer expanding dragons, one dragon that is easy to snipe) | agrees with section 2d: the zone phase costs a fifth to a third of the natural intake and gives the leader one pearl per 50 rounds; and with 2h: an early leader of 15-24 is rammed 6.9 times per 1,000 rounds before round 300 against 3.8 after 400 |
| q2 | "BOOT10", "BOOT16" (most likely `FEED_BOOT_LEN` 10 / 16; the log gives only the labels) | local | 43 and 40 of 96 against 48 | rejected by the team; not looked at here |
| LG5k | leader guard | local | 50 of 96 (+5 -3) | too few flips to say |
| be1-be4 | `BIG_ESCAPE_STEPS`, `BIG_ESCAPE_LATE`, `BIG_TRUE_REACH` (a long dragon sprints out of an enemy's reach) | local, four batches, also against a leader-hunting sparring bot | all neutral or negative; "big head-on victims are mostly NOT the leader (second dragons)" | agrees: in races our leader of 15+ dies in 0.13 (small) and 0.56 (big) races, less often than our opponents' on big maps |
| QF3, SF300 (v58, v59) | `QUEEN_GAME_FEED_ROUND` 300, `QUEEN_SAFE_ROUND` 300 (feed a living queen from round 300) | local +11 -4 and +15 -5; adopted | in the live bot | outside this read (queen alive) |
| eg1 | `ENDGAME_ROUND` 350 / 450 | queued 2 October | no result in the log | - |

The team's own diagnosis in the same log is close to this report's and was never turned into a trial: "feeders feed
non-top leaders ... 65% of v42 feeds and 50% of v41 feeds go to a non-top dragon. Leader info splits by region";
"believed length < own length*2 is already a rule, but belief goes stale"; "feeds to a non-top believed leader:
24/37, 18/25, 29/42"; "NEXT: ... refuse to feed a leader much shorter than the max leader length ever heard"; "our
consolidation effectively starts at r430-450; theirs at r350-400"; "growth after r400 is equal. The gap exists AT
r400: they are ahead in r300-400"; "top-3 at r499 e.g. 53/43/34 vs 64/28/7 ... FEED_LEN_RATIO 2 keeps big dragons
from feeding; regions elect separate leaders". No trial touched the three things candidate 5 names: the leader's own
cuts, the stale record after a cut, and dying next to nothing.

**Does what is seen now explain the neutral results of the earlier-start trials?** Partly, and only as an inference.
(1) They were local mirror games on a rich board, where the gap that the ladder shows in rounds 300-399 does not
exist. (2) The one online trial was swamped by drift. (3) An earlier start does not repair what loses the level races
we lose (seven of 14 lost after being level or ahead at round 425 or later). (4) "The enemy eats the pearls" is not
the explanation: 4.7% of the pearls of our deaths by choice on small maps go to the enemy. "The feeders die too far
away or next to the wrong dragon" is half of one: a quarter of our deaths by choice are next to nothing, and of the
rest 61% are three steps from the dragon they feed.

### h. The risks, counted

Tables in section 2h (`e_h.py`), `e_out/cutcost.txt`, `e_out/heir.txt`.

- **An early, long leader is rammed more often, for everybody.** Per 1,000 rounds with a leader of 15-24: 4-7 before
  round 300 against 1-4 after (ours 6.9 / 4.6 / 3.8 for rounds 150-299 / 300-399 / 400-499; our opponents' 3.1 / 1.2 /
  1.2; forgot's 5.2 / 1.6 / 3.7; SSS's 5.9 / 2.0 / 0.9; Vibing++'s 4.3 / 2.6 / 2.1). Ours is rammed two to three times
  as often as our opponents' at every stage; the rammer is 2-4 long in 38 of 62 cases. At 3-4 per 1,000, a leader
  that exists for 100 rounds is rammed in one game in three.
- **What early feeding costs.** Units halve in 50-100 rounds (forgot 52.5 -> 30 -> 19, Vibing++ 56 -> 34 -> 27, our
  opponents 61 -> 46 -> 31; SSS less: 60 -> 51 -> 45), natural intake falls by a tenth to a third (forgot 86 -> 74 ->
  63 per 50 rounds), potential stays flat (97 -> 99.5 -> 101).
- **Does the first starter lose more on wipe-outs or the queen rule?** No. Top-three sides that start at least 25
  rounds before the other side win 352 of 531 games (66%) and 25 of 30 wipe-outs; when the other side starts first
  they win 142 of 288 (49%). For our sides 32 of 111 against 10 of 102. Not a clean effect of the start: the richer
  team has more units and its clock runs earlier.
- **How much of our feeding goes to the enemy.** 5.1% of our feeders' pearls (live bot; test builds 3.5%; our
  opponents 1.8%; forgot 0.6%; SSS 2.1%; Vibing++ 1.7%). 15% when an enemy head is within 4 cells of the dying feeder
  (5% of our feeders), 8% at 5-8 cells (43%), 2% at 9-15, under 1% farther. On big maps, on the like-for-like count,
  10.5% (others 1.8-6.0%). "Our late feeding often feeds the opponent" is one pearl in twenty on small maps and one
  in ten on big ones; seven times as many go to another small dragon of ours.
- **The leader's own cuts as a risk, and whether to forbid the early one.** A cut costs 2 segments (5.4 a race from
  round 400; more than the margin in 10 of our 102 lost races) and, in our team, about 25 rounds of feeding. Making
  the leader wait until it has no free cell, as forgot and WHQ do (0.3 and 0.2 early cuts a race), is not supported
  by what was counted: in three of four of our early cuts the pocket ahead holds four cells or fewer, so the cut
  would come a few rounds later anyway; and waiting is safe for forgot (one leader of 15+ lost boxed in, in 154
  races) but not for WHQ (one in 39 races on small maps, 38 in 35 races on big ones, in its games against us), for a
  reason a replay shows only as the death. Our leaders of 15+ never die boxed in. The candidate leaves the cut as it
  is and repairs what follows it.
- **The heir.** After a leader cut the child dies within one round in 1.6-2.0% of our cuts (0-3.1% for the others)
  and cuts again within three rounds in 10-13% (7-26%). A same-round chain of three or more cuts of the final lineage
  happened in 3 of our 143 races and in 13 of the top three's 447 (from round 350; `e_out/cutcost.txt`).

### i. The rule

Section 7. In one sentence: the team feeds one dragon; that dragon keeps the role through its own cuts (the team follows the new id within a few
rounds); and a dragon gives its life only next to a leader it can see is long.
