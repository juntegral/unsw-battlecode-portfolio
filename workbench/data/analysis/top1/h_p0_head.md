# Candidate hypotheses: how our bot can win more (sub-session B)

Written 2026-10-05 for team meow (1119). This file turns the evidence of the top-team study (`findings.md`, the four
close reads `deep-read*.md`, the team's own records and the bot source `mybot2/main.cpp`) into candidate rules for our
bot, all measured the same way so they can be compared. The red team attacks these next; the lead picks one.

I ran no game for this file. Two of the ideas were already tried online by the team in a narrower form (the test
builds qh31 and tc30); what those trials did and did not test is said where they are used. Every number says where it
comes from. "Measured" means counted on replays by the script named; "inferred" means arithmetic on played games or a
reading of the source code; a replay shows positions, orders, deaths, pearls and sonar rays, never what a bot intended
or remembered.

**In short.** Four candidates, each a general rule with no map name and no map-size condition in it:

1. **Take the queen.** A dragon of ours that has the enemy queen's head in view and in reach rams it, at any length.
   +1.5 to +2 points most likely (range up to +3.2). One existing switch.
2. **Our queen is never spent.** She never ends a move inside a visible enemy's reach when another move exists, never
   rams, and gives away two segments instead of all but two when she is boxed in. +0.9 to +2.8 points.
3. **No leader before its time.** No dragon leaves a pearl for a "leader" or stops splitting earlier on some maps
   than on others. +0.4 to +1.5 points. One constant.
4. **Do not give way at contact.** A small dragon that is not outnumbered rams any small enemy head it can reach;
   alone, only a longer one. 0 to +2.4 points; the one online trial of a third of it did not win more.

**My pick is candidate 1, second candidate 2.** They are the two sides of one idea and together are worth about +3
to +5 points. The ranking with reasons, what is not proposed and why, the list of new counts and what could not be
determined are at the end.

## Words

- **Queen**: each team's lowest-numbered dragon. Both queens move before every other dragon in every round.
- **Ram**: a head moves into another head; both dragons die, whatever their lengths.
- **Reach**: the most steps a dragon can take in one turn: 1, 2, 3, 5, 6 for lengths 2, 3, 4, 5, 6 (a quarter of its
  length rounded up is free, every further step costs a segment).
- **View**: the 7x7 square around a head. A dragon knows nothing else unless a team-mate tells it by sonar.
- **In-view chance**: a turn of a non-queen dragon (12 or shorter) that starts with the enemy queen's head inside
  its view and a path of free cells to it no longer than its reach. Because queens move first, a ram on such a turn
  cannot be dodged. "Taken" = the dragon rams her on that turn. Counted by the lead's `extract3.py` (`q3v2/`).
- **How a game ends**: by **wipe-out** (one team has no dragon left), or at round 500. At round 500 the longer living
  queen wins and a living queen beats a dead one (**queen rule**); if both are dead or equal, the longest single dragon
  wins (**longest rule**).
- **Boxed in**: no free cell next to the head. There is no "stay" order, so a boxed-in dragon that cannot split dies.
- **Feeding**: small dragons die on purpose next to one dragon (the queen or the longest) so that it eats their
  pearls and grows. Every top team does it late in the game.
- **Live bot / candidates**: our 401 games against teams rated 2000 or more (map Schooltime left out) are eleven runs.
  275 were played by the live bot of that hour, 126 by test builds (stride, passage2, qh31, tc30). Where the two
  differ, both are given.
- **test4 and WeHaveQuizzes**: the two teams rated just over 2000 that we meet most (313 of the 401 games). "dev test
  1" is a test opponent on the server. "Our opponents" = the other side in our 401 games.
- **Local / online**: local games are played on our machines between our own bots; online games are played on the
  competition server (ladder games, or a "smoke test" of 30 games for a test build). A **card** (#14, #31, ...) is
  an idea ticket in the team's test loop. Labels such as "GB300" or "H4" are the team's names for toggles in its log
  `work/plan.md`.
- **Band**: our total length divided by the enemy's at round 300: under 0.67, 0.67 to 1, 1 to 1.5, over 1.5.
- **Point**: one percentage point of win rate. One game of our 401 is 0.25 points.

## The footing every candidate is put on

**Where our games end up** (`h_states.py`, output `h_out/states.txt`; measured):

| How the game ended | meow, 401 games | won | top three, 1,637 games | won |
|---|---|---|---|---|
| wipe-out, we wiped them out | 67 (17%) | 67 | 455 (28%) | 455 |
| wipe-out, we were wiped out | 103 (26%) | 0 | 267 (16%) | 0 |
| round 500, our queen alive, hers dead | 1 (0.2%) | 1 | 177 (11%) | 177 |
| round 500, both queens alive | 14 (3.5%) | 3 | 159 (10%) | 103 |
| round 500, both queens dead | 143 (36%) | 41 | 447 (27%) | 266 |
| round 500, our queen dead, hers alive | 73 (18%) | 0 | 132 (8%) | 0 |
| all | 401 | 112 = 27.9% | 1,637 | 1,001 = 61.1% |

The live bot alone: 275 games, 77 won (28.0%), the same shares within a point. Queen-rule wins: 4 of our 112 wins, 280
of the top three's 1,001. Our opponents in these same games: our queen dead and theirs alive in 73 round-500 games
(all won by them), the reverse in 1.

**Two readings for every "what would have happened".**

- **Strict**: the rule changes one event (a queen lives, a queen dies) and nothing else on the board. The game is
  re-scored with the final lengths as they were. Where a dead enemy queen leaves a longest-dragon game, "lenient"
  compares our longest with her best dragon other than the queen, "hard" with her longest dragon including the queen's
  own length (as if every pearl the queen ate had gone to another dragon instead).
- **Realistic**: after the changed event we win the new kind of game only as often as we actually win that kind of
  game today, in the same band. Used here: round-500 games with both queens dead, we win 10 of 86 in the lowest band,
  15 of 37, 6 of 7 and 10 of 13 in the higher ones (41 of 143 overall); both queens alive, 3 of 14. A saved queen of
  ours then survives either as often as a top-three queen alive at that round in that band (sub-session A4's
  "reading 2") or only as often as our own queen would with the other kinds of death left at our own rates ("reading 3").

Wipe-outs never change under either reading. Economy candidates cannot be re-scored game by game, so for them the
realistic reading is: our total length at round 300 rises by a stated share, and each game is re-scored with our own
win rate for the band it lands in (`h_econ.py`).

**How big each gap is, as a ceiling** (`h_states.py` part 3; 268 of our games reach round 300, we won 51 of them;
inferred, the lines overlap and must not be added up):

| If this one thing were at the top three's level, inside the same band | wins | change |
|---|---|---|
| everything (their win rate for our mix of bands) | 84.9 | +33.9 |
| our queen alive at the end as often as theirs (still as short as now) | 73.7 | +22.7 |
| the enemy queen dead at the end as often as against them | 58.3 | +7.3 |
| our win rate when both queens are dead (the longest-dragon race) | 57.9 | +6.9 |
| our win rate when both queens are alive (queen length) | 56.1 | +5.1 |
| for comparison, the economy: our win rate per band with THEIR mix of bands | 111.8 | +60.8 |

Reading: the economy is the larger gap (61 wins of 268), the conversion at equal economy the smaller (34 wins). Inside
the conversion gap our own queen's survival is by far the largest piece. The "29% against 60%" in games with both
queens dead is mostly economy: inside the same band it is 12% against 16%, 41% against 51%.

**What a win count can and cannot test.** The team's online comparison is 30 games against 30. At a 28% win rate two
such halves of the same bot differ by 3.5 wins on average through chance alone. Every candidate below is expected to
be worth between 0 and 3 points, that is at most one win in 30. To have four chances in five of seeing a real gain in
the win count one would need about 32,000 games a side for +1 point, 8,000 for +2, 3,600 for +3 and 1,300 for +5. So no
candidate here can be judged by wins; each one names a behaviour number that moves by a factor, not by a few percent,
and can be counted on 20 to 60 new replays with the scripts in this directory.
