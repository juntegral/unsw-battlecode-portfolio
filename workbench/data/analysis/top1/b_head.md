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
