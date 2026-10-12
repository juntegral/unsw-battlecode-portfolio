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

## Candidate 1: take the queen

### 1. The claim

**A dragon of ours that has the enemy queen's head in its view and can reach it this turn rams it.** Every dragon
except our own queen, at every length, whatever it costs in segments, in every round, on every map.

It is a rule about one turn. It does not send anybody to look for her.

### 2. Evidence

**Who takes such a turn** (in-view chances taken of all; `h_c1.py` on the lead's `q3v2/`, output `h_out/c1.txt`;
measured; the meow and top-three columns repeat `findings.md` section 3, the others are new):

| Attacker | meow, all builds | meow live bot | our opponents, on OUR queen | Vibing++ | SSS | forgot |
|---|---|---|---|---|---|---|
| 2-3 long | 87 of 231 = 38% | 61 of 164 = 37% | 139 of 146 = 95% | 186 of 186 | 155 of 155 | 221 of 317 = 70% (136 of 139 from round 100 on) |
| 4 long | 5 of 39 | 1 of 26 | 29 of 31 | 25 of 25 | 26 of 26 | 12 of 53 |
| 5-9 long | 5 of 137 = 4% | 4 of 100 | 28 of 49 = 57% | 38 of 38 | 59 of 61 | 21 of 65 |
| 10-12 long | 2 of 39 | 1 of 28 | 1 of 4 | 17 of 18 | 10 of 12 | 0 of 22 |
| all | 99 of 446 = 22% | 67 of 318 = 21% | 197 of 230 = 86% | 266 of 267 | 250 of 254 | 254 of 457 = 56% |
| the attacker is its team's longest dragon | 8 of 117 | 2 of 78 | 17 of 22 | 30 of 30 | 28 of 28 | 4 of 47 |
| own queen alive / already dead | 26% / 21% | 26% / 19% | 85% / 100% | 100% / 99% | 99% / 95% | 52% / 65% |
| rounds 0-99 / 100-299 / 300+ | 34 / 21 / 15% | 35 / 19 / 14% | 93 / 90 / 53% | 100 / 100 / 98% | 100 / 99 / 88% | 40 / 76 / 48% |

| Games | meow | meow live bot | our opponents | Vibing++ | SSS | forgot |
|---|---|---|---|---|---|---|
| this side rammed the enemy queen | 102 of 401 = 25% | 69 of 275 | 251 of 401 = 63% | 318 of 502 = 63% | 320 of 503 = 64% | 303 of 632 = 48% |
| had an in-view chance and never rammed her | 76 = 19% | 49 = 18% | 2 | 0 | 2 | 43 = 7% |

So does each of the three do it? With dragons of 2-3: yes, all three (forgot from round 100 on; before that only when
not outnumbered where it stands, `deep-read-2.md`). With longer dragons at any price: Vibing++ and SSS yes, forgot no.
Our opponents in these games (test4 and WeHaveQuizzes in 313 of the 401) take 95% of such chances on our queen with
2-3-longs and 57% with 5-9-longs. We are the only team in the table that mostly walks away, in every build and run.

**The two sides are equally exposed; only one side uses it.** Sub-session A4 counted turns on which a queen ends
inside the reach of an enemy head she can see: 5.4 per 1,000 rounds for our queen and 5.4 for theirs. They ram on 71%
of those turns, we on 16% (`deep-read-4.md` 5b; measured there).

**What our dragon does instead** (`h_c1walk.py`, output `h_out/c1walk.txt`; measured on all 347 untaken turns in 122
games): a 2-3-long steps away from her (124 of 144 turns end farther from her head); a 4-long splits (24 of 34); a
longer dragon walks on (164 of 169 turns; 5 split). On 25 of the 347 turns it ate a pearl instead. The rule in
our code explains it: of the 178 untaken turns of dragons of 4 or shorter, 131 fail the "at least as many other own
heads in view as enemy heads" test (she is an enemy head herself, so a lone dragon beside a lone queen never
qualifies), 112 have a queen "too short to be worth a trade", 7 come after the round at which trading stops, and only 7
pass all three. Dragons longer than 4 are never allowed to trade at all. Nothing in the code knows that the target is
the queen (item 5).

**The protagonist's wins against its losses** (`h_c1.py` part E; measured; a correlation, since the stronger side gets
near her more often). Vibing++ rammed the enemy queen in 247 of its 316 wins (78%) and in 71 of its 186 losses (38%).
In round-500 games in which the own queen was dead:

| The enemy queen ... | Vibing++ won | SSS | forgot | meow |
|---|---|---|---|---|
| was rammed by this team | 86 of 124 | 61 of 104 | 62 of 110 | 15 of 42 |
| died some other way | 13 of 28 | 21 of 37 | 23 of 44 | 26 of 101 |
| lived | 0 of 38 | 0 of 28 | 0 of 66 | 0 of 73 |

The last row is not a correlation; it is the rule of the game.

**Games that show it and its absence.**

- Shown: 1063780 round 34 (Vibing++'s 5-long #44 sprints 5 steps, 3 of them paid, into forgot's queen and wins the
  game on the queen rule 28 against dead; `deep-read.md`). 1060356 round 143 (an SSS 8-long pays 4 segments for a
  6-step ram and SSS wins with a 3-long queen; `deep-read-2.md`).
- Absent: 1029030 round 234 (Autarky; our 3-long #267 starts its turn one free step from WeHaveQuizzes's 2-long queen,
  with three own heads and no other enemy in view, and steps away; we end with a 93-long dragon and lose to a queen
  of length 2). 1068679 rounds 461 and 469 (weakhold; our 3-long #275 twice has her 2-long queen on the next cell with
  nobody else in view; we end 32 against 4 and lose on the queen rule). 1053784 rounds 448-463 (Trauma; our 8-9-long
  circles her 39-long queen for 18 turns, four of them in view and 4-5 steps away, while our own queen is alive and
  31 long: one ram wins the game outright). All three from `h_out/c1walk.txt` and `deep-read.md`.

**Trials that exist.**

- **qh31 (online, card #31).** What that build did, read from its kept source `data/online/smoke/qh31-bot/main.cpp`
  (`QH_SCOUT`, `QH_MAX_LEN 4`, `QH_QUIET 20`, `QH_REVENGE_ROUND 100`): one hunter at a time. A non-leader of 4 or
  shorter that sees her itself after round 20, and has heard no other hunter for 20 rounds, walks to her last seen
  cell and rams when in reach. Only once our own queen is dead and the round is 100 or later may every small dragon
  that knows her cell hunt. Result (`qh31-test-result.txt`, `qh31-analysis/summary.txt`): 10 wins of 30 against 8 on the
  same pairs (the live bot's four runs average 9.2). In-view chances taken by 2-3-longs 8 of 9 (the live bot in the
  paired run 8 of 20), by longer dragons 2 of 11 (0 of 9). Kills of her queen 11 against 10. Of 338 hunters 8 rammed
  her and 36 died in head-ons with other enemies, 32 of them rammed by the enemy while walking to her.
  **Tested:** the 2-3-long half of this rule, plus a chase that this candidate does not have. **Not tested:** dragons
  of 5 and more, dragons that are not "the hunter", the first 20 rounds.
- **Local.** `QUEEN_HUNT` limited to dragons of 4 or shorter ("H4", `work/plan.md`): 59 wins of 120 against v57 where
  the base had 60 (+10 -11 by pairs), 57 against 58 versus a hunting sparring bot. An older variant with hunting on
  ("QS0PH"): 91 of 156 against 96. Neutral. The local opponents are our own bots, whose queens are dead by round
  30-50 in most games whatever we do.
- `QUEEN_HUNT` was on in v54 and has been off since v55. The team's own note of that day: an opponent's queen "spent
  23% of rounds within our kill reach and was never rammed (QUEEN_HUNT off since v55)".

### 3. Mechanism

At round 500 a living queen beats a dead one, so the enemy queen's life decides three kinds of game:

- **Our queen dead, hers alive: lost for certain** (0 of 73 for us, 0 of 132 for the top three). This is 18% of all
  our games. A ram turns it into a longest-dragon game, which we win 29% of the time (36% of those in which it was we
  who rammed her).
- **Both alive: we lose 11 of 14**, because her queen has been fed and ours is 2-3 long. A ram makes it a win outright
  for as long as ours lives.
- A queen that dies early also stops being her team's "mother" (on maps that start with 2-5 dragons the queen makes
  most new dragons by splitting). Not counted below.

The ram is certain when the rule fires: both queens have already moved this round, the path is free at the start of
the attacker's own turn, and the whole move happens inside that turn. Vibing++ and SSS complete 516 of 521 such turns,
which also shows that "in-view chance" as counted is something a real bot can execute.

### 4. Expected effect

**(a) Games that end differently** (`h_c1.py` part C and `h_joint.py`; inferred from played games). Of our 401 games
176 had at least one in-view chance. In 54 the first one was taken (in 2 more she died in that same round). In 80
the rule would only kill her earlier (she died later anyway, 70 rounds later on average); in 40 she was alive at the
end and the rule gains the kill. Of those 40, 15 are wipe-out losses (no change) and 25 are round-500 losses:

| Reading | meow, 401 games | live bot, 275 games |
|---|---|---|
| round-500 losses with her alive and an untaken in-view chance | 25 | 15 |
| strict, lenient (our longest beats her best non-queen dragon, or our queen is alive) | 13 | 7 |
| strict, measured share (her team ends with the longest dragon our opponents usually build once their queen is dead) | 7 | 3 |
| strict, hard (our longest beats her longest dragon, queen's length included) | 6 | 3 |
| realistic (we then win at our own rate for both-queens-dead games of that band) | 8.5 | 5.4 |
| the same if only dragons of 4 or shorter may do it (the qh31 limit): strict lenient / hard / realistic | 6 / 4 / 4.2 | 3 / 2 / 2.4 |

Which strict count is nearer the truth can be measured (`h_c1enemy.py`, output `h_out/c1enemy.txt`): in round-500
games our opponents end with a longest dragon of 56 (median) when their queen died before round 300 and of 46 when
she lived, which is 42% and 31% of their total length at round 400; the same order holds in each of three bands of
their total length. A team whose queen is dead puts the length into another dragon. Giving her team that usual share
in one dragon (but never more than its real longest) in each of the 25 games leaves 7 flips, one more than the hard
count.

The 25 games are listed one by one in `h_out/c1flips.txt` (`h_c1flips.py`). Seven of the 13 flips need an attacker
of 5 or longer. In none of the 13 is the dragon that would have rammed needed for the flip: with it taken out of our
final lengths the count is still 13 (in 10 it was dead by the end anyway). A recount of the chances with my own code
and a stricter path test (every body blocks, as in the bot's own search) finds the same 25 games and the same 13 and
6 (`h_c1recount.py`, `h_c1check.py`: 435 chances against the lead's 446, 99 taken in both).

**(b) In points:** +1.5 to +3.2 on our 27.9% (hard strict to lenient strict), realistic +2.1, measured-share strict
+1.7. Live bot: +1.1 to +2.5, realistic +2.0. My single figure: **+1.5 to +2 points (7 or 8 games in 401)**; the
upper end of the range needs an enemy that does not replace its queen with another long dragon, and ours do.

**(c) Where it acts.** Only in games in which one of our heads gets within view and reach of her: 44% of our games.
The first missed chance comes at round 172 in the median game (34 games before round 150, 23 in rounds 150-299, 19
later). The 13 strict flips are 4 on maps over 1,200 cells and 9 on smaller ones; by band 5, 2, 2 and 4, so it acts
at every state of the economy. It does nothing in the 122 games (30%) in which no dragon of ours ever had her in
view and reach and she lived: 59 round-500 losses and 60 wipe-outs. Those are queens behind portals and games in
which we never get near her.

**(d) With the other candidates.** It needs none of them first. With candidate 2 (our own queen) it more than adds:
both rules touch the same game in 10 of our losses, and a saved queen of ours wins outright once hers is dead.
Together they give 49-54 strict flips where the two alone sum to 40-47, and 21.4 realistic wins where the two alone
sum to 19.6 (`h_out/joint.txt`). Candidates 3 and 4 would put more of our dragons near her and so create more
chances; that is not counted.

### 5. What changes in `mybot2/main.cpp`

- `QUEEN_HUNT` (the `constexpr` near line 128): `false` -> `true`. **The toggle exists.** `QUEEN_HUNT_MAX_LEN` stays
  `0`, which means no length limit; `QUEEN_HUNT_STEPS` stays `12`.
- What that switches on is already written: `mark_hunt_targets()` marks the enemy queen's head whenever it is among
  the heads in view, for every dragon that is not the queen, leaders and feeders included; `hunt_path()` searches a
  path of free cells up to `min(sprint_reach(), 12)` steps and `act()` calls it before anything else.
- One condition must change so that the rule does not leak: the first line of `mark_hunt_targets()` returns for
  `is_queen()`, which is false on maps of 600 cells or fewer (`QUEEN_MIN_CELLS`). It must test `real_queen()`, or our
  own queen will ram hers on small maps.
- Deliberately not touched: `QUEEN_CHASE_DIST` stays `0` (no walking towards her), `mark_trade_targets()` and
  `is_trader()` stay as they are (the hunt bypasses their three conditions for this one target).
- Size: one constant and one condition.

### 6. What would show it is wrong

Counted on new replays against test4 and WeHaveQuizzes with `extract3.py`, then `h_c1.py` and `h_c1walk.py`:

1. In-view chances taken must go from 22% to at least 90% overall and at least 85% for attackers of 5-12 (Vibing++
   100%, SSS 98%; qh31 reached 8 of 9 with 2-3-longs). If not, the bot's idea of a free path differs from the
   replay's; `h_c1walk.py` lists the turns.
2. Games with an in-view chance and no kill must go from 19% to under 3%.
3. The enemy queen alive at the end must fall from 40% of games towards 30%, and "round-500 losses with her alive and
   an untaken chance" from 25 in 401 to about none. **If point 1 holds and her queen is still alive at the end in 38%
   or more of games, the chances were on queens that die anyway and the rule is worth the low end or less.**
4. Cost check: our longest dragon at round 400 (median 12 today) must not fall. Dragons of 5 or longer spent on her
   queen: about 0.1 a game is what the played games predict (50 games of 401 had such a chance); far more would mean
   long dragons are being drawn to her.

Wins: the expected gain is 0.6 wins in 30. A win test would need about 8,000 games a side to see +2 points. With
60 + 60 games there are about 50 in-view chances a side, enough for points 1 and 2.

### 7. Known risks

- **The trials do not show a gain in wins.** qh31: +2 in 30 (noise), kills 11 against 10. Local: neutral three times.
- **It spends long dragons.** On the first untaken chance of each of the 122 games the attacker was 5-12 long in 39,
  and the attackers add up to 537 segments (4.4 a game). Against that: 107 of those 122 dragons were dead by the end
  of the game anyway and 2 were our longest dragon at the end. In our round-500 wins the rule would have spent our
  then-longest dragon four times; in three our second dragon still beats her longest, in the fourth the dragon died
  later anyway (`h_out/c1walk.txt`). Dragons longer than 12, which the chance files skip, would have had such a turn
  in 9 of the 401 games, each time with our own queen already dead; the one win among the nine stays a win without
  that dragon (`h_c1long.py`, `h_out/c1long.txt`).
- **Half of the value is the half that only two of three top teams do.** Dragons of 4 or shorter alone give 4-6
  strict flips, not 13. forgot does not ram with long dragons and is level with the other two.
- **The kill is only earlier in 80 of 120 games.** I count nothing for that.
- **The lenient strict count assumes the enemy does nothing else with the pearls** her queen would have eaten. It
  does: with a dead queen our opponents build a longer leader than with a living one (item 4a). The low end of the
  range (6-7 games) is the likelier one.
- **Confounder:** we get chances when we are near her, which is when we are doing well; "we win 66% of the games in
  which we rammed her" is not the size of the effect.
- **Opponents can adapt.** The rule feeds on queens that walk into our reach (5.4 turns per 1,000 rounds today). The
  top teams change their bots often, and a queen that stops doing so gives it nothing; test4's queen already walks a
  four-cell loop a quarter of the time and is almost never rammed on it by anyone (`deep-read-4.md`).
- What qh31's hunters died of (head-ons with other enemies while walking to her) does not apply here: the rule fires
  only on a turn on which the ram is certain.

## Candidate 2: our queen is never spent

### 1. The claim

**Our queen never ends a move inside the reach of an enemy head she can see while another move exists; she never
rams; and when she has no free cell she gives away two segments from her tail, not all but two.** At every length and
on every map.

"On every map" is part of the change: today the queen rules are switched off on maps of 600 cells or fewer
(`QUEEN_MIN_CELLS`), where she is an ordinary small dragon. This candidate removes that map-size switch for the three
things named, and for nothing else.

### 2. Evidence

All counts in this section are sub-session A4's (`deep-read-4.md`, scripts `d_class.py`, `d_expo.py`, `d_haz.py`,
`d_cut.py`, `d_misc.py`; outputs in `d_out/`), measured on every game; the last two rows and the split into parts are
mine (`h_c2.py`, output `h_out/c2.txt`). A **safe step** is a one-step move that ends on a cell no enemy head in her
view can move into this round. A **queen-round** is one round in which a queen is alive.

| | meow, all builds | meow live bot | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| From outside reach she steps into it although a safe step exists (share of such turns) | 0.76% | 0.68% | 0.42% | 0.18% | 0.15% | 0.23% |
| Inside reach with a safe step, she ends in reach again | 19% | 17% | 13% | 10% | 8% | 10% |
| Both together, per 1,000 queen-rounds | 2.66 | 2.54 | 1.46 | 0.81 | 0.57 | 1.05 |
| A turn that ends in reach is punished by a ram | 71% | 72% | 16% (by us) | 44% | 47% | 32% |
| Games in which she died on such a turn | 104 of 401 = 26% | 68 of 275 = 25% | 27 of 401 = 7% | 39 of 632 = 6% | 38 of 503 = 8% | 35 of 502 = 7% |
| No free cell and 6 or longer: cuts herself to 2-3 / gives away 2 from the tail | 40 cuts, never the other | (not split by build) | 85 / 109 | 0 / 1,448 | 0 / 394 | 105 / 78 |
| Rams an enemy head herself although a free safe cell exists (games) | 10 | 8 | 1 | 4 | 0 | 5 |
| All queen deaths per 1,000 queen-rounds | 6.5 | 6.3 | 2.2 | 2.8 | 2.1 | 3.4 |
| Own queen alive at the end, in this team's wins / in its losses (`h_c2.py`) | 25% / 4% | 25% / 4% | 55% / 3% | 58% / 7% | 57% / 12% | 37% / 9% |
| Own queen died on such a turn, in wins / in losses | 16% / 30% | 18% / 27% | 3% / 16% | 3% / 11% | 6% / 11% | 5% / 10% |

So does each of the three do it? Never ending in reach by choice: yes, all three, at a quarter to a third of our rate,
and against test4 and WeHaveQuizzes alone at a sixth (0.4 against our 2.6 per 1,000 queen-rounds). Giving away 2
instead of cutting: SSS and forgot always, Vibing++ not (it cuts to 3, and A's read shows it losing won games that
way). Not ramming with the queen: SSS never, the other two almost never.

**The rule works on the turns on which our queen already follows it** (`d_after.py`; measured). Inside a visible
reach with a safe step on the board: when she took it she was rammed that round in 0.3% of 290 turns and within ten
rounds in 24%; when she did not, 56% and 65% of 68 turns. Outside reach with a small enemy within 4 steps: 0.1% and 19%
of 3,887 turns against 83% and 87% of 69.

**What it costs is small and counted.** The rule would change 149 turns of the queen in 401 games (81 steps into
reach, 68 stays in reach). On 21 of them she ate a pearl: one pearl per 19 games.

**Games that show it and its absence.**

- Absent: 980372 round 94 (Around UNSW; our 2-long queen steps west onto the next cell of her little loop, 2 steps from
  a 3-long that reaches 2; north and east were 4 steps from it). 1023823 round 81 (Australia; she takes a pearl that
  lies between her and the head of forgot's 3-long; east was safe). 990346 round 385 (Slithery Fight; our queen is 57
  long, has no free cell, cuts herself to 2 and dies next round; the enemy queen ends the game 3 long, so one living
  queen of any length wins it). All three from `deep-read-4.md`.
- Shown: 1063780 rounds 127-136 (Vibing++'s queen walks away from a small enemy on all seven occasions one comes
  within 3 steps; `deep-read.md`). 1063783 rounds 397-412 (forgot's 42-long queen is boxed in by her own coils, gives
  away 2 a round for 16 rounds, walks out 10 long and ends the game at 29; `deep-read.md`).

**Trials that exist.** None of this exact rule. What came near it, all local, all against our own bots
(`work/plan.md`):

- A larger number instead of an order: `QUEEN_THREAT_MULT` 3 and 6 and `QUEEN_GUARD_RADIUS` 3 "do not cut rams
  (rammed 9-12)" in 24 games.
- A separate planner for the queen with a "never in reach" veto inside it (`QUEEN_BRAIN`): the queen lived in 7-10 of
  156 games instead of 4, and the team won 69-71 where the base won 95. The note: "queen protection costs 11-26 wins
  and buys 2-5 queen wins". That planner also paid segments to move, searched five steps ahead and scored room; it was
  not this one veto on the normal step chooser.
- Switching the existing queen rules on for small maps cost local wins (small maps 13 against 16 and 7 against 11),
  which is why `QUEEN_MIN_CELLS 600` exists.
- Online, the "no trap" build qn23 (card #23, another rule): boxed-in deaths 15 of 45 against 52 of 215 for the live
  bot, no gain. Card #25 (`QUEEN_WAIT`) never fired, because the cut had already made her 2 long.

### 3. Mechanism

A living queen at round 500 beats a dead one, at any length. 143 of our 401 games (36%) end at round 500 with both
queens dead, and we lose 102 of them; in every one of those a living queen of ours wins outright. In the 73 games that
end with ours dead and hers alive, a living queen of ours is at least a queen-length game, and with candidate 1 a win.
The three parts stop her from dying on turns on which the board offered something better:

- a move out of reach existed (104 deaths),
- two segments would have bought a round and kept the rest of her (14 deaths that follow a cut, 40 cuts in all),
- a free safe cell existed and she rammed instead (10 deaths, all on maps where the rules are off).

### 4. Expected effect

**(a) Games that end differently** (`h_c2.py` part 3 and `h_joint.py`; inferred from played games). "Top-three
survival" and "our own other rates" are the two realistic readings of the footing section.

| Part | deaths (maps over / up to 600 cells) | strict | realistic: top-three survival | realistic: our own other rates |
|---|---|---|---|---|
| never end a move in a visible reach | 104 (68 / 36) | 26 | 8.6 | 2.6 |
| give away 2, never cut | 14 (14 / 0) | 4 | 1.4 | 0.4 |
| never ram | 10 (0 / 10) | 4 | 1.2 | 0.0 |
| **the candidate (all three), meow 401 games** | 128 (82 / 46) | **34** | **11.1** | **3.7** |
| the candidate, live bot 275 games | 87 (57 / 30) | 19 | 6.4 | 2.1 |

The strict count is high because it lets the saved queen live to round 500. Of the 128 deaths 60 are in games that
ended by wipe-out (nothing changes), 11 in round-500 wins, 34 in round-500 losses with the enemy queen dead (each
flips if ours lives) and 23 in round-500 losses with hers alive.

**(b) In points:** realistic +0.9 to +2.8 (strict +8.5). Live bot +0.8 to +2.3. The low end says: she no longer dies
this way but stays as exposed to being cornered and to unseen sprinters as she is today. The high end says she then
lives like a top-three queen, which this rule alone does not make her.

**(c) Where it acts.** On turns with an enemy head in her view: one round in five. Two thirds of the deaths it
touches are on maps where the queen rules are on today, one third where they are off. It does nothing against the
kinds of death it does not name: cornered with no move out of reach (114 games), rammed by an enemy she could not see
(31), a team-mate on her last exit (31), a terrain dead end (30). And nothing in the 170 games that end by wipe-out.

**(d) With the other candidates.** It needs none first. With candidate 1 it more than adds (see candidate 1, item 4d):
together 49-54 strict and 12.3-21.4 realistic wins, +3.1 to +5.3 points. Candidates 3 and 4 do not touch the queen;
candidate 4 would put more of our dragons' rams near her (item 2 there).

### 5. What changes in `mybot2/main.cpp`

- **New block in `pick_direction()`**, after `apply_route(...)`, for `real_queen()`: mark every cell that an enemy
  head visible this round can move into this turn. The pieces exist: `stride_reach_map()`, `spread_kill()` and
  `queen_margin()` already compute exactly that for the queen's multi-step moves (a cell is in reach when
  `queen_margin(cell) <= 0`); the block must use heads seen this round only, not the three-round "ghosts". If any
  scored, not-closed direction is out of reach, subtract `LONG_THREAT_VETO` from every direction that is not; if none
  is, set `cornered = true`. This is the order that dragons of 8 or more already have (`LONG_SAFE_MIN_LENGTH` block);
  today the queen's danger is one term of a sum, `PENALTY_HEAD_RACE 450 x max(0.5, length / 4) x ...`, smallest for
  the shortest queen, which a pearl (`EAT_BONUS 300` plus target bonus) outweighs.
- **Five places must obey the same test or the rule leaks:** in `act()`, `cornered && (is_big() || is_queen()) &&
  sprint_escape(path, true)` and the length test inside `sprint_escape()` must use `real_queen()`; `map_threats()` and
  `threat_at()` choose the queen's danger map by `is_queen()` and must use `real_queen()`, or the paid escape will not
  see the same danger on small maps; `split_child_size()` must return 0 for the real queen while an enemy head is
  near (`QUEEN_SPLIT_CLEAR` is 0 today; 16 of our 251 rammed queens had split with an enemy in view within their last
  three turns); `is_trader()` must test `!real_queen()` instead of `!is_queen()`. `extend_stride()` already treats
  `real_queen()` separately (`stride_caution()` returns 2) and needs no change.
- **`escape_child_size()`**: when `no_move` and `real_queen()`, return `unswbc::Constants::MIN_SIZE` (the child is the
  two tail segments) instead of `length - 2`.
- **Toggles.** None for this rule. `QUEEN_THREAT_MULT 1.0`, `QUEEN_GUARD_RADIUS 0`, `QUEEN_PESSIMIST false` and
  `QUEEN_BRAIN false` are the earlier attempts and stay as they are. `QUEEN_MIN_CELLS 600` stays for the other queen
  rules (portals, the split round, feeding).
- Size: one new block of about thirty lines, seven conditions, one constant.

### 6. What would show it is wrong

Counted on new replays against test4 and WeHaveQuizzes with `d_class.py`, then `d_expo.py`, `d_tab.py`, `d_cut.py`:

1. Turns that end in reach although a safe step existed: from 2.6 per 1,000 queen-rounds to under 0.8 (top three
   0.6-1.1). If not, the code does not do what the rule says; look for the path around it (stride, split, trade).
2. Games in which she dies on such a turn: from 26% to under 8%. Cuts of a queen of 6 or more: from 40 in 401 games
   to none. Own rams with a free safe cell: none.
3. Queen deaths per 1,000 queen-rounds: from 6.5 to about 5; alive at round 300 from 15% to about 22%. **If 1 and 2
   hold and this does not move, the deaths have moved to "cornered" (cornered turns would rise from 2.8 to above 4 per
   1,000 queen-rounds): then the rule only delays her death and is worth the low end.**
4. Cost check: natural pearls eaten by the queen in rounds 0-99 within 10% of today's 4.7 and 3.3 per 100 rounds;
   units at round 100 not lower; wipe-out losses (26% of games today) not higher.

Wins: expected 0.3 to 0.8 wins in 30. Not a win test. Sixty games give about 60 queen deaths, enough for points 1-3.

### 7. Known risks

- **Every earlier attempt to protect the queen lost games locally**, and the 600-cell switch exists because of it. The
  rule here is narrower than all of them (it changes 149 turns in 401 games), but on small maps the team fight
  decides most games (59% of our games there end by wipe-out) and this has not been tried there.
- **A queen saved once meets the next danger.** Against these opponents a turn in reach is punished 71% of the time
  and she is cornered 2.8 times per 1,000 queen-rounds without any choice of hers. That is why the realistic range
  starts at +0.9 points.
- **The safe step can be a bad step.** In 12 of the 104 deaths the only safe step led into a pocket; the rule skips
  closed cells, but it may trade a ram for a boxed-in death in some of the others.
- **The reach test can be wrong.** A head in view may belong to a longer dragon than its visible part shows; dragons
  that move between her turn and the enemy's are not modelled (A4's model called the fatal cell safe in 2% of rams).
- **Giving away 2 a round makes a small dragon each round** inside her own coils. SSS and forgot do exactly this on
  the coiled 25-long start of one map and lose nothing, but our team-mates step onto her last exit (20 "nose to nose"
  deaths), which this candidate does not fix.
- Confounder I could not remove: 60 of the 104 deaths came with our total length under two thirds of the enemy's
  and 19 dragons of ours on the board against 31 (`h_c2.py` part 2b). Where the team is being overrun, a queen saved
  this round may have nowhere to go the next.

## Candidate 3: no leader before its time

### 1. The claim

**Until the team starts to build one long dragon, every dragon eats the pearl next to it and splits at 4. No dragon
leaves a pearl for a "leader", and none stops splitting, at an earlier round on some maps than on others.**

In our code the "leader rules" start at round 150 on maps over 1,200 cells and at round 300 on all others. The change
is to remove that map-size switch: one start, round 300, on every map.

### 2. Evidence

**What the code does after the switch** (read in `mybot2/main.cpp`, not seen in replays). Every dragon keeps track
of the longest own dragon it has heard of in the last 25 rounds, by sight or by sonar; that dragon is its "leader",
however short. From `grow_round` on: a dragon that knows a longer one may not take pearls within 9 cells of that
leader's last known head (181 cells): they are no targets, lose the eating bonus and cost a penalty of 600. A dragon
that knows no longer one is "leader" itself: it never splits, never rams and no longer goes into tight places or
through unknown portals for pearls. Any dragon longer than 4 stops splitting. So from that round on every dragon of
ours is under one of the two halves of the rule.

**What the replays show** (`h_c3.py`, 791 games walked: all 401 of ours, 147 and 345 top-three games on the two map
classes; output `h_out/c3.txt`; measured). The turn counted: a dragon of 2-4 that is not the queen moves, no enemy
head is in its view, and a pearl lies on a free cell next to its head with a way on behind it. Share of such turns on
which its first step takes that pearl:

| Maps over 1,200 cells (our switch: round 150) | meow live bot | our opponents | Vibing++ | SSS | forgot |
|---|---|---|---|---|---|
| rounds 0-149 | 83% of 16,079 | 85% | 88% | 80% | 94% |
| rounds 150-399 | **58% of 18,312** | 84% | 85% | 83% | 94% |
| ... no longer own dragon within 9 cells of the pearl | 73% of 4,152 | 85% | 85% | 88% | 93% |
| ... a longer own dragon within 9 cells | 54% of 14,160 | 84% | 86% | 82% | 94% |
| ... that longer dragon is 3-4 / 5-9 / 10 or more long | 60 / 54 / 46% | 84 / 83 / 85% | 90 / 86 / 82% | 84 / 81 / 82% | 94 / 94 / 95% |
| rounds 150-399, the dragon itself is 2 / 3 / 4 long | 54 / 57 / 88% | 84 / 83 / 86% | (top three together: 88 / 86 / 89%) | | |

| Maps of 1,200 cells or fewer (our switch: round 300) | meow live bot | our opponents | Vibing++ | SSS | forgot |
|---|---|---|---|---|---|
| rounds 0-299 | 88% of 28,107 | 84% | 88% | 87% | 93% |
| rounds 300-399 | **53% of 8,202** | 78% | 88% | 80% | 92% |
| ... a longer own dragon within 9 cells: it is 3-4 / 5-9 / 10 or more long | 57 / 50 / 34% | 74 / 79 / 84% | 89 / 90 / 83% | 78 / 82 / 84% | 93 / 91 / 92% |

So does each of the three do it? Yes: none of the three, and neither of our usual opponents, shows a fall of that
kind before round 400 (their rates move by 6 points at most) or any difference near a longer own dragon. Our fall comes exactly at our own switch on both kinds of
map, in the live bot and in the candidates alike, it is deepest next to the longest dragons, and it hits the 2- and
3-longs and not the 4-longs. That last point fits the code: a 2-long almost always knows of a longer dragon near
it, a 4-long is mostly the longest it knows of. (Inference; the replay cannot show what a dragon knows. The lead's
and A3's count with "within 9 cells of the team's longest dragon of 5+" gave 41% / 58% / 66%; counting any longer
own dragon as the possible leader gives 54% / 73% and explains why the fall is there with no long dragon near.)

**A test of the mechanism** (`h_c3dist.py`, our 401 games, output `h_out/c3dist.txt`; measured). After the switch,
the share of free pearls a 2-3-long takes, by the distance from the pearl to the head of the nearest longer own
dragon:

| Distance in cells | 0-3 | 4-6 | 7-9 | 10-12 | 13-16 | 17 or more | no longer own dragon on the board |
|---|---|---|---|---|---|---|---|
| meow live bot, maps over 1,200 cells | 50% | 51% | 57% | 65% | 69% | 72% | 82% (60 turns) |
| meow live bot, other maps | 46% | 50% | 55% | 62% | 66% | 65% | 65% (167 turns) |
| our opponents, maps over 1,200 cells | 82% | 86% | 84% | 83% | 84% | 85% | |
| our opponents, other maps | 76% | 78% | 78% | 75% | 78% | 80% | 75% |

Our rate rises with the distance and the opponents' is flat. It is a slope, not a step at 9 cells; that is what a
leader position remembered for up to 25 rounds would give, since long dragons move several cells a turn (inference).
The rate stays low even far from every longer dragon, so a second effect of the same switch is likely: a dragon that
takes itself for the leader may no longer go into tight places for pearls (`harvestable()` is false for
`is_leader()`; read in the source, not seen in replays).

**What the switch buys and costs** (`h_c3b.py`, output `h_out/c3b.txt`; means over games that reach the round;
measured). Maps over 1,200 cells:

| From round 150 to round 300 | units | total length | longest dragon |
|---|---|---|---|
| meow live bot (77 games) | 47.2 -> 35.9 | 123.4 -> 121.5 | 5.8 -> 14.2 |
| the three top teams (427 games) | 55.6 -> 58.8 | 164.9 -> 205.8 | 8.6 -> 18.4 |
| our opponents in those games | 60.4 -> 61.2 | 209.5 -> 326.5 | 11.0 -> 23.4 |

With the rule on, our longest dragon grows by 8 segments in 150 rounds; the top three's grows by 10 without any such
rule, and their team grows by 41 segments while ours stands still and loses 11 dragons. On the other maps, where our
switch has not happened yet, our total length grows by 20% in the same rounds (47 to 57; top three 41%).

**Wins against losses.** All 9 wins of the live bot on these maps are longest-dragon wins, and in them we had 54
units and total length 210 at round 300; in the 68 losses 33 units and 109 (`h_c3b.py` part 3). Our wins there are the
games in which the economy held, not games in which an early leader was built at its cost. For the protagonist the
same sign: Vibing++ has 60 units and total 230 at round 300 in its wins on these maps and 48 and 169 in its losses
(`findings.md` section 2). And in round-500 games with both queens dead, how the two teams' total lengths compare at
round 400 says about twice as much about who wins as how their longest dragons compare at round 400 (a simple fit of
win or loss on the two ratios over our 143 such games gives weights of 1.8 and 0.9; for the top three 1.8 and 0.35;
`h_race.py`).

**Games that show it and its absence** (`h_c3game.py`, output `h_out/c3game.txt`; share of such turns eaten per 50
rounds).

- Absent: 1063016 (Around UNSW, 4,096 cells, live bot against test4): 87% in rounds 100-149, then 77%, 72%, 46% in
  the three blocks to round 299; test4 in the same game stays at 67-79%. 1068052 (Maze, 1,152 cells, against
  WeHaveQuizzes): 90% in rounds 200-249 and 48% in rounds 300-349, the switch being at 300 there; WeHaveQuizzes
  84-95%.
- Shown: 1046985 (forgot against test4, Australia, 4,096 cells): 88-100% in every block from round 0 to 499. 1064304
  (SSS against test4, Around UNSW): 79-92% throughout.

**Trials that exist** (`work/plan.md`).

- The same switch moved to 300 on big maps ("GB300"), three local runs: 30 wins of 64 against 20 on one big map (on a
  build with a known bug), 46 of 96 against 48, 73 of 152 against 76. Neutral. Never tried online.
- Card #14 replaced only the split stop by a unit-count test: no local change, "our bot already reaches 60 units
  locally by round 200".
- The opposite direction, the switch at round 200 on every map ("LC200": later on big maps, earlier on small ones):
  52 of 96 locally against 48, then 19 wins of 60 online against dev test 1 where the base had 23.
- Why the local runs say little: both sides are our own bot, both reach the 60-unit limit on a rich board. On the
  ladder we have 47 units at round 150 and the opponent eats what we leave.

### 3. Mechanism

It works through the economy that feeds every end-of-game rule. On these maps we are under two thirds of the enemy's
total length at round 300 in most games (median ratio 0.45 for the live bot) and win 9 of 77. The switch takes a
team of 47 small eaters and tells most of them to stop eating wherever a slightly longer dragon is near; they no
longer reach length 4, so fewer split, so the team shrinks while the enemy eats the pearls left lying (after the
switch 64 pearls a game are declined at least once; our own dragons eat 55% of them within ten rounds, the enemy
5%, and 40% still lie there ten rounds later, during which the tile makes no new pearl).

### 4. Expected effect

**(a) Games.** An economy rule cannot be re-scored game by game. Inferred in two ways, our total length at round 300
on these maps would be 12-24% higher: (i) on the other maps, before the switch, our growth from round 150 to 300 is
half of the top three's and of our opponents' in relative terms (20% against 41% and 47%); half of their growth on
the big maps (25% and 56%) is 12% and 24%, where we have -2%. (ii) Our small dragons would take about 36 more
pearls at once per game in rounds 150-299 at their own earlier rate; they get 55% of those later anyway, so about 16
are lost outright, which is 14% of our total length. Re-scoring every game with our own win rate for the band it
lands in (`h_econ.py`, output `h_out/econ.txt`):

| Our total length at round 300 on maps over 1,200 cells | meow, 401 games | live bot, 275 games |
|---|---|---|
| +15% | +1.8 to +3.8 wins | +1.5 to +3.0 |
| +25% | +3.0 to +6.0 wins | +2.5 to +4.1 |

(The lower number of each pair is a smooth fit of win on the length ratio, the higher the four-band table.) There is
no strict reading.

**(b) In points:** +0.4 to +1.5 on our 27.9%. Live bot: +0.5 to +1.5.

**(c) Where it acts.** Only on maps over 1,200 cells (111 of our 401 games) and only in rounds 150-299. On every
other map the rule asked for is what the bot already does, so nothing changes there. Inside those games it acts in
every state, queens alive or dead.

**(d) With the other candidates.** It adds to all of them. Candidate 4 needs it: the trade-on-contact build led
60 units to 33 and 60 to 39 at round 150 in two games and was behind by rounds 249 and 213, under this same switch
(`deep-read-3.md`). More small dragons alive also means more heads that can meet the enemy queen (candidate 1).

### 5. What changes in `mybot2/main.cpp`

- In the constructor, `grow_round = aggressive ? LEADER_GROW_ROUND : LEADER_GROW_ROUND_BIG;` loses its map-size test:
  `grow_round = LEADER_GROW_ROUND` (300). Equivalent: `LEADER_GROW_ROUND_BIG` 150 -> 300, or the existing toggle
  `LC_LEAD_ROUND` 0 -> 300, which overrides `grow_round`. **A toggle exists.**
- `grow_round` is read in three places, which then all move together: `is_leader()` (and through it the leader's
  bans in `split_child_size()`, `is_trader()`, `harvestable()` and `can_scout_portals()`), `refresh_leader_zone()`
  (and through it `in_leader_pearl_zone()`, `ZONE_PEARL_PENALTY`, `LEADER_PEARL_RADIUS`), and the `length >
  SPLIT_MIN_LENGTH` stop in `split_child_size()`.
- **One thing must follow or the rule leaks:** `feeding_phase()` also starts at round 200 once we have 56 units
  (`FEED_CAP_ROUND 200`, `FEED_CAP_UNITS 56`). Today that is after the big-map switch; with the switch at 300 a team
  that reaches 56 units between rounds 200 and 300 would feed a dragon that is not "leader" yet and still splits.
  Either `FEED_CAP_ROUND` goes to 300, or the three places above test `round > grow_round || feeding_phase()`.
- Not touched: `aggressive` stays as it is for the trade rule (that is candidate 4).
- Size: one constant, plus one constant or three conditions.

### 6. What would show it is wrong

Counted on new replays on maps over 1,200 cells with `h_c3.py` and `h_c3b.py` (or the lead's `recount3.py`):

1. A free pearl next to the head is eaten in rounds 150-299: from 58% to at least 80% (2- and 3-longs from 54-57%
   to at least 80%). If not, the leader zone was not the cause.
2. Units at round 300: from 36 to at least 45. Total length at round 300: from 121 to at least 140. **If point 1
   holds and these do not move, the pearls were not what held the team back, and the rule is worth nothing.**
3. The number that may get worse: our longest dragon at round 300 (14 today) will be shorter. What must not fall is
   the share of round-500 games on these maps that we win on the longest dragon (9 of 77 for the live bot).

Wins: these maps are 10 of a 30-game test (5 of the 15 maps), so the expected gain is 0.1 to 0.4 wins in 30. Not a
win test at any size we can play. Twenty big-map games a side are enough for points 1 and 2.

### 7. Known risks

- **Three local runs of exactly this change were neutral**, and card #14's part of it too.
- **The size of the gain is inferred, not measured.** Nobody has seen our bot play rounds 150-299 on a big map
  without the switch against a ladder opponent.
- **More economy did not become more wins when it was tried.** The trade-on-contact build had 21% more total length
  at round 300 on these maps and won 0 of 12, where our own win rates for the bands it reached predict 1.7
  (`h_c4.py`). That is weak evidence (it happens by chance about one time in seven), but it is the only evidence
  there is.
- **It undoes a deliberate setting.** `LEADER_GROW_ROUND_BIG 150` was chosen at some point (I did not find the reason
  in `work/plan.md`). All our wins on these maps are longest-dragon wins, so an earlier leader may be part of some of
  them. How many could turn: of our 12 wins there (all builds) 2 were won by 1 and 2 segments and the other 10 by 11
  to 62; of the 53 losses with both queens dead 3 were lost by 5 or fewer. A leader that starts later could move
  those five games either way (`h_c3wins.py`, output `h_out/c3wins.txt`).
- **The fall has more than one cause and I can see only their sum.** With no longer own dragon within 9 cells the
  rate is 73%, not 83%, and 17 cells from any it is still 72%. A remembered leader position and the loss of the
  "harvest" rule for self-styled leaders would explain it, and both hang on the same switch; the replay cannot
  confirm either.

## Candidate 4: do not give way at contact

### 1. The claim

**A dragon of 4 or shorter that sees at least as many heads of its own team as enemy heads rams any enemy dragon of 4
or shorter whose head it can reach this turn: longer, same length or shorter. Alone or outnumbered, it rams only one
that is longer than itself.** On every map.

"On every map" is part of the change: today the trade rule has a map-size switch (`AGGRESSIVE_MAX_CELLS 1200`) that
all but forbids such rams on larger maps.

### 2. Evidence

**The lead's and A3's numbers** (`findings.md` 6c, `out2/recount3.txt`; measured). On maps over 1,200 cells the live
bot rams in 8% of meetings (an enemy head on the next cell, both dragons 4 or shorter); our opponents 35%, SSS 41%,
Vibing++ 33%, forgot 35%. It starts 22% of the rams of its games (top three 48-57%) and eats 29% of the pearls rams
leave (49-52%). On smaller maps it rams at meetings like everyone (34% against 31%).

**New here: who rams what, and with whom around** (`h_c4walk.py`, 791 games walked: all 401 of ours and 492 of the
top three; output `h_out/c4walk.txt`; measured). A chance is a turn of a non-queen dragon of 4 or shorter that starts
with the head of an enemy non-queen dragon of 4 or shorter in its view and reachable this turn. "Not outnumbered" =
other own heads in its 7x7 view at least as many as enemy heads there. Share of chances that end in its ram, with the
enemy head on the next cell / 2-3 free steps away:

| Maps over 1,200 cells | meow live bot | tc30 build | our opponents | Vibing++ | SSS | forgot |
|---|---|---|---|---|---|---|
| not outnumbered, enemy longer | 16% / 12% | 87% / 58% | 91% / 83% | 89% / 90% | 98% / 90% | 98% / 83% |
| not outnumbered, enemy same length | 15% / 9% | 87% / 66% | 72% / 55% | 90% / 87% | 98% / 84% | 91% / 57% |
| not outnumbered, enemy shorter | 2% / 0% | 3% / 0% | 48% / 29% | 68% / 55% | 63% / 44% | 78% / 46% |
| alone or outnumbered, enemy longer | 3% / 0% | 4% / 0% | 46% / 42% | 42% / 41% | 93% / 59% | 55% / 20% |
| alone or outnumbered, enemy same length | 3% / 0% | 5% / 0% | 12% / 5% | 19% / 21% | 5% / 0% | 13% / 5% |
| alone or outnumbered, enemy shorter | 3% / 0% | 3% / 0% | 10% / 2% | 6% / 5% | 3% / 0% | 9% / 3% |
| rams made this way, per game | 7.5 | 27.6 | 43.9 | 58.6 | 55.0 | 57.7 |

| Maps of 1,200 cells or fewer | meow live bot | our opponents | Vibing++ | SSS | forgot |
|---|---|---|---|---|---|
| not outnumbered, enemy longer | 88% / 82% | 77% / 56% | 92% / 88% | 98% / 94% | 94% / 58% |
| not outnumbered, enemy same length | 89% / 76% | 64% / 50% | 87% / 83% | 98% / 93% | 83% / 65% |
| not outnumbered, enemy shorter | 11% / 0% | 42% / 27% | 64% / 51% | 83% / 58% | 61% / 45% |
| alone or outnumbered, enemy longer | 11% / 0% | 52% / 34% | 43% / 37% | 83% / 42% | 47% / 26% |
| alone or outnumbered, enemy same length | 9% / 0% | 14% / 6% | 24% / 18% | 16% / 0% | 16% / 9% |
| alone or outnumbered, enemy shorter | 10% / 0% | 12% / 3% | 11% / 6% | 8% / 0% | 11% / 3% |
| rams made this way, per game | 8.3 | 10.8 | 12.7 | 12.2 | 11.0 |

So does each of the three do it? Yes, all three, and both of our usual opponents, on both kinds of map: with the
numbers on their side they ram nearly every small enemy head they can reach, a shorter one in half to four fifths of
the cases; alone, they ram a longer one about half the time and hardly anything else. This is the same head count
our own rule uses (`TRADE_LOCAL_EDGE`). **So the top teams do not "ram alone"; A3's proposal to drop the head count is
not what they do.** What they do and we do not is three things: the same rule on big maps (our switch), shorter
targets when not outnumbered (19 of their 57 rams a game on big maps, 3.6 of 12 on the others; we: 0.2), and longer
targets when alone (4 a game; we: 0.2).

**What such a ram is worth to the side that starts it** (`h_c4pearls.py`, same games, output `h_out/c4pearls.txt`;
measured). Swing = (pearls of the two corpses eaten by the starter's team minus its dragon's length) minus the same
for the other team, in segments per ram, on maps over 1,200 cells:

| Kind of ram | top three | our opponents | meow live bot | tc30 build |
|---|---|---|---|---|
| not outnumbered, victim longer | +2.5 | +3.2 | +2.3 | +2.8 |
| not outnumbered, victim same length | +1.6 | +2.2 | +1.1 | +1.0 |
| not outnumbered, victim shorter | +1.1 | +1.4 | -0.7 (31 rams) | (5 rams) |
| alone or outnumbered, victim longer | +0.4 | +1.2 | -0.8 (34 rams) | (7 rams) |
| alone or outnumbered, victim same length / shorter | -0.2 / -1.1 | +0.7 / 0.0 | -1.0 / -2.1 | |
| all rams it starts: number per game x swing = segments per game | 65 x 1.15 = +75 | 52 x 1.77 = +92 | 8.6 x 0.52 = +4.5 | 29 x 1.19 = +34 |

The top three ram exactly where the swing is positive for them and hold back where it is negative. In our big-map
games the opponent gains 92 segments a game from the rams it starts and we gain 4.5 from ours. For scale: our total
length at round 300 on those maps is 121 and theirs 327. On the smaller maps the two numbers are 9 for us and 14 for
them.

**Wins against losses.** For the top three on big maps this does not separate wins from losses (Vibing++ starts 73
such rams a game in wins and 68 in losses; all three together 64 and 67): among them it is what everybody does. For
us it does: 15 a game in our 9 big-map wins, 8 in the 68 losses (`h_out/c4pearls.txt`); partly cause, partly the
consequence of having the numbers.

**Near our queen** (`h_c4.py`; measured). A small enemy that comes within 4 steps of the own queen is rammed by one
of her team in 1.7% of cases on big maps and 4.9% on the others for the live bot; 9-20% and 13-15% for the top three,
18% and 12% for our opponents. Nobody escorts a queen (`deep-read-2.md`); these are ordinary contact rams that happen
near her.

**Games that show it and its absence** (the pairs table of `deep-read-3.md`, same opponent, same map, same side).
Absent: 1063240 (Islands, live bot against WeHaveQuizzes): 6 of 84 meetings rammed, 6 rams made and 32 suffered in
rounds 0-149, 47 units against 61 at round 150, wiped out at round 449. Shown: 1068051 (the tc30 build, same
pairing): 11 of 40 meetings, 22 rams made and 29 suffered, 60 units against 39 at round 150; and 1051826 (SSS on the
same map against test4, a win).

**The trial that exists: tc30** (online, `tc30-test-result.txt`, `deep-read-3.md`). The build removed the map-size
switch for one test only: on big maps a target showing at least the attacker's own length is enough (the live bot
asks for max(5, own length + 2)). It kept the head count and the 8-unit minimum.

- Behaviour: as the first table shows, it rams like the top three where it is not outnumbered and the enemy is not
  shorter (87%), and as little as the live bot in every other case.
- Economy on big maps: rams started 29 a game instead of 9, swing +34 segments a game instead of +4.5, units at round
  150 52 instead of 47, total length at round 300 147 instead of 121 (+21%). What the opponent gains from its own rams
  did not change (91 a game against both builds).
- Wins: 6 of 30 against the live bot's 9.2. On big maps 0 of 12, where our own win rates for the bands it reached
  predict 1.7 (`h_c4.py`).
- Local (`work/plan.md`): the same idea ("TRADE_EVEN") no gain; dropping the head count ("TLE0") 60 wins of 118 where
  the base had 68, against a rushing copy of our bot.

**Tested:** the first of the three differences, online, with the behaviour and the economy moving as counted here and
the wins not. **Not tested:** shorter targets when not outnumbered, longer targets when alone, and all of it together
with candidate 3.

### 3. Mechanism

Through the economy. A ram kills one dragon on each side; what differs is who eats the pearls of the two corpses, and
the side that starts the ram with friends around eats 70-85% of them. A dragon that steps away instead eats 0.33
pearls in the next ten rounds against 0.70 for the enemy it left, and is rammed anyway in one case in five
(`deep-read-3.md`). On big maps this exchange is the largest single flow between the teams: about 90 segments a game
to the enemy. More units and length move games up the bands of the footing section; more of our dragons ramming near
our own queen also takes away some of the enemies that corner her.

### 4. Expected effect

**(a) Games.** No strict reading. Realistic, by parts, as total length at round 300 on maps over 1,200 cells and our
own win rate per band (`h_econ.py`):

- The tested part gave +21% (measured on 12 games): +2.4 to +5.3 wins in 401 by the band arithmetic. The trial itself
  won none of 12.
- The untested parts, inferred from the swing table: shorter targets when not outnumbered would add up to 20 rams a
  game, worth +1.1 each to the top three and between -0.7 and 0 to us in the few cases we have, plus whatever it
  saves when our longer dragon is not rammed first by the shorter enemy (the opponents make 13.5 such rams a game on
  us at +1.2 to +3.2 each). Somewhere between nothing and another +25 segments.
- Together +21% to +45%: +2.4 to +10 wins in 401; live bot +2.0 to +7.

**(b) In points:** the arithmetic says +0.6 to +2.4. Because the only trial won fewer games, my range is **0 to +2.4,
single figure +1**.

**(c) Where it acts.** Nine tenths of it on maps over 1,200 cells (111 of 401 games), from the first contact (round
20-90) to the end. On the other maps only the "shorter target" and "alone against a longer one" parts are new (about 4
more rams a game). It does nothing where the teams never touch.

**(d) With the other candidates.** It needs candidate 3: the trial's two best openings were lost between rounds 150
and 250 under the leader switch. It overlaps with nothing. It helps candidate 2 a little (rams near our queen) and
candidate 1 not at all.

### 5. What changes in `mybot2/main.cpp`

- `mark_trade_targets()`. Today: `normal_ok` needs `round <= feed_round`, a unit minimum (`TRADE_MIN_UNITS 8`, or
  `AGGRESSIVE_TRADE_MIN_UNITS 1` on maps up to 1,200 cells) and the head count (`TRADE_LOCAL_EDGE 1`); `worth` is
  `parts >= length` on maps up to 1,200 cells and `parts >= max(TRADE_TARGET_MIN_PARTS 5, length + 2)` on larger ones.
  New, for an enemy head showing 4 parts or fewer: if the head count holds, mark it whatever its length; if it does
  not hold, mark it when `parts > length`. No `aggressive` in either test, unit minimum 1 everywhere.
- `ram_path()`: `min(sprint_reach(), aggressive ? AGGRESSIVE_RAM_MAX_STEPS : RAM_MAX_STEPS)` becomes one value.
- Toggles that exist: `TRADE_EVEN` (false) makes `worth` the small-map test on every map, which is the tested part;
  nothing exists for shorter targets or for "alone against a longer one".
- What else must obey: `is_trader()` already keeps out dragons longer than 4, leaders and the queen. `score_step()`
  drops the fear of enemy heads for a trader and adds `TRADE_REWARD 2500 - TRADE_DECAY 80 x distance` towards a marked
  head, so every newly marked head also pulls the dragon towards it from several cells away; that is what makes a
  ram from two or three cells away (a "charge"), and it is also how a wrong mark would drag dragons around.
- Size: two conditions in one function, one in another, two constants.

### 6. What would show it is wrong

Counted on new replays with `h_c4walk.py`, `h_c4pearls.py` and the lead's `recount3.py`:

1. The first table's cells for us must reach, on both kinds of map: not outnumbered 85% / 60% for longer and same
   length, 60% / 45% for shorter; alone against a longer one 40%. Rams made this way on big maps from 7.5 a game to
   at least 45.
2. Swing per ram we start must stay above +0.8 overall (tc30: +1.19). **If the new kinds of ram come in below zero
   for us, as our few cases today suggest, they cost dragons and the rule is wrong for our bot as it is.**
3. What the opponent gains from its own rams on big maps must fall below 92 segments a game. In the tc30 trial it
   did not (91).
4. Units at round 100 not under 42 and at round 150 at least 52 on big maps (tc30's level); wipe-out losses not above
   today's 26% of games.

Wins: 0 to 0.7 expected in 30. Not a win test.

### 7. Known risks

- **The one online trial of its first part won fewer games** (6 against 9.2 of 30; 0 of 12 on the maps it changes).
  That is inside the noise, and the economy did move, but it is the only win evidence and it points the wrong way.
- **The same rams are worth less to us than to the top three.** Where we do start rams with the numbers on our side
  our team eats 68% of the pearls, theirs 78%; on shorter victims 55% against 84% (31 cases). The rule copies when
  they ram, not what happens afterwards.
- **We replace dragons more slowly**: 4.1 pearls eaten per split at length 4 against 3.3 for our opponents
  (`deep-read-3.md`), so an even trade costs us more.
- **Small maps are decided by wipe-out** (59% of our games on maps of 600 cells or fewer); more trades there can end
  games sooner in either direction.
- "Not outnumbered" is my count on the replay's 7x7 squares. The top teams may use another test that only looks like
  it.

## Ranking

Expected points are the realistic ranges of each candidate's item 4, on our 27.9% against teams rated 2000 or more.
"Strict" is added where a game-by-game count exists. All four name a behaviour number that can be counted on 20 to 60
new replays; none can be judged by wins in a 30:30 test.

| Candidate | Strongest evidence in one line | Expected points | How sure | How hard to build | How testable | Depends on |
|---|---|---|---|---|---|---|
| **1. Take the queen** | All three top teams ram a queen in view and reach every time with small dragons (two of them with any dragon); we take 22% of 446 such turns, our opponents 86% of theirs on our queen; 25 of our losses had such a turn and a living enemy queen at the end | **+1.5 to +3.2**, most likely +1.5 to +2 (strict 6-13 games of 401, 7 by the count I trust most) | Behaviour: very sure, the code path exists and a narrower build reached 8 of 9. Wins: fairly sure of the low end | One constant (`QUEEN_HUNT`, exists) and one condition | 60 + 60 games give 50 chances a side: 22% must become 90% | Nothing |
| **2. Our queen is never spent** | In 104 of our 401 games (26%; top three 6-8%) our queen died on a turn with a safe step on the board; when she takes the safe step she is rammed within ten rounds in 19-24% of cases, otherwise 65-87% | **+0.9 to +2.8** (strict 34 games) | Behaviour: fairly sure. Value: wide, it hangs on whether a saved queen then survives | One new block in `pick_direction()`, seven conditions, one constant | 60 games give 60 queen deaths: 2.6 turns in reach by choice per 1,000 queen-rounds must fall under 0.8 | Nothing; worth more with 1 (+1.8 wins) |
| **3. No leader before its time** | Our small dragons take a free pearl beside them in 83% of turns before our own switch round and 58% after it, on both kinds of map; nobody else's rate moves; our total length stands still from round 150 to 300 on big maps | **+0.4 to +1.5** (no strict count) | Behaviour: very sure. Size of the gain: inferred, not measured | One constant (`LC_LEAD_ROUND`, exists) plus `FEED_CAP_ROUND` | 20 big-map games a side: 58% must become 80%, total length at round 300 121 must become 140 | Nothing |
| **4. Do not give way at contact** | With the numbers on their side all three top teams ram nine in ten same-length small enemies on the next cell and six to eight in ten shorter ones; we 15% and 2% on big maps; the exchange moves about 90 segments a game to our opponents there | **0 to +2.4**, single figure +1 | Behaviour and economy: sure for the tested third. Wins: unsure, the one online trial won 6 of 30 against 9.2 | Conditions and constants in `mark_trade_targets()` and `ram_path()` | 20 big-map games a side: rams made 7.5 a game must become 45, swing per ram must stay above +0.8 | 3 (the trial lost its lead under the leader switch) |

**The one I would pick: candidate 1, take the queen.** All three top teams follow it with small dragons almost
without exception (186 of 186, 155 of 155, and forgot 136 of 139 from round 100 on), our own opponents use it against
us four times as often as we use it against them, the reason we do not is one switch in the code that the team
turned off itself, the turn it acts on cannot fail (the queen has already moved), the cost is counted (88% of the
dragons it would spend are dead by the end of the game anyway), and of everything here it has the narrowest gap
between the cautious and the generous reading. It is not the largest gap we have. It is the one most likely to be
real.

**Second: candidate 2, our queen is never spent.** It addresses the largest piece of the conversion gap on the
footing (our queen alive at the end as often as a top-three queen would be +22.7 wins; this rule's own part of that
is 3.7 to 11.1). It is second and not first because every earlier attempt to protect the queen cost games locally,
because it is new code in several places, and because its value depends on what happens to her afterwards. In
expected points the two are close; candidate 1 is the surer and by far the cheaper.

**One candidate or two?** Candidates 1 and 2 are one idea seen from two sides: a queen that ends a turn inside the
reach of an enemy head dies, so theirs is rammed whenever she does and ours never does when she has a choice. Both
queens end such a turn equally often (5.4 times per 1,000 rounds each); they use 71% of ours and we use 16% of
theirs. The state the two rules aim at together, "our queen alive and hers dead at round 500", is 1 of our 401 games
and 177 of the top three's 1,637, every one of them a win. Together they are worth 49-54 strict and 12.3-21.4
realistic wins, +3.1 to +5.3 points, more than the two alone.

I still keep them as two candidates, and the pick is the first alone, for three reasons. They change different
dragons through different code (a switch that exists; a new block). Their ways of failing differ: if candidate 1
fails, nothing happens; if candidate 2 fails, the queen boxes herself in or the team loses the fight on a small map.
And one card should be readable: with both in one build a flat result could not be traced to either. Their
behaviour numbers do not interfere, so once candidate 1's number has moved, candidate 2 can be tested on top of it.

**If build time decides.** The freeze for new submissions is 8 October, 20:00 KST (the team's loop rules). By cost the order
is 1 (a switch), 3 (a constant), 4 (conditions in two functions), 2 (a new block and seven conditions). Candidate 3
changes only games on maps over 1,200 cells and only rounds 150-299, so it is the one that could most safely ride
along with another card; I would still test one thing at a time.

**What would change my mind.**

- Away from candidate 1: if new replays show the chances taken at 90% and the enemy queen still alive at the end in
  38% or more of games, the chances were on queens that die anyway; or if the red team shows that the both-dead
  games it creates are ones we lose more often than our band rates say (the hard strict count, 6 games or +1.5
  points, is the floor I would then use; below +1 point I would rather take candidate 3, which costs one constant).
- To candidate 2 first: if the aim is the largest possible gain rather than the surest, and there is evidence that
  a queen saved from one ram survives the next against test4 and WeHaveQuizzes (for instance queen deaths per 1,000
  queen-rounds falling from 6.5 to under 5 in a first smoke run).
- To candidates 3 and 4 as a pair: if a rerun of the trade-on-contact build together with the leader switch at
  round 300 holds its round-150 lead to round 300 (total length at least 170 where the live bot has 121). The
  economy is the larger gap overall (+61 wins on the footing against +34 for conversion); what is missing is a rule
  shown to close a known part of it.

## Not proposed, and why

Each line gives the number that decided it. The first block is from the lead's list of mechanisms, the second from
the earlier candidate list (`run1/hypotheses.md`), the third from the close reads.

**From the lead's list**

- **The longest-dragon race: start feeding earlier.** The mechanism is real: in round-500 games with both queens
  dead and total length level at round 400 we win 13 of 36 and the top three 95 of 156, our longest there is 17
  against 27 at round 400, and the gap is made between rounds 300 and 400 (our longest grows by 5, theirs by 18; after
  round 400 both grow by about 20; `h_race.py`). But it has been tried directly: feeding from round 330 instead of 400
  (v46) won 24 of 60 online against dev test 1 where the base won 23, and feeding from 330 and 300 won 70 and 69 of
  152 locally where the base won 76 (`work/plan.md`). And the ceiling is small once the economy is held fixed: inside
  the same band our win rate with both queens dead is 12% against 16% and 41% against 51%, worth +6.9 wins of 268
  (`h_states.py`). Of everything dropped this is the one I was least sure about dropping.
- **Team-mates keep off the queen's last exit** (nose to nose 20, a team-mate's body 14, her own child 11 in A4's
  count). The part not already inside candidate 2 is 31 deaths, +6 strict and +0.5 to +2.5 realistic wins (`h_c2.py`).
  Asking team-mates to give way was tried locally and lost: 84 wins of 156 against 96. Vibing++ has the same problem
  (34 nose-to-nose deaths in 502 games) and is rank 1.
- **The queen rules on every map as a whole** (`QUEEN_MIN_CELLS` to 0). Candidate 2 takes only its own tests off
  the switch (the order of moves, the paid escape, the split near an enemy, the ram, the cut). The portal ban was
  tried on all maps and one small map went to 0 wins of 8, because there the queen is the only dragon that reaches
  the food behind the portal early; its deaths are 14, +0 to +2.7 realistic wins.
- **The queen never steps into a place with no way round** (30 terrain dead-end deaths, +0.4 to +4.0 realistic wins).
  It needs a new terrain test on a map she only partly knows, and the neighbouring online trial (qn23, "no trap")
  had more such deaths, not fewer: 8 of 45 games against 15 of 215.
- **Nobody near our queen rams an intruder** (1.7-4.9% against 9-20%). Not a rule of its own: it is candidate 4
  happening near her. No top team moves towards an intruder (SSS dragons near the queen moved nearer 40 times and
  farther 44, `deep-read-2.md`).
- **The split stop for dragons longer than 4** (card #14's subject). It is inside candidate 3, but it is not where
  we differ: after our switch our dragons of 5-9 split on 5% of their turns, the top three's on 9%, our opponents' on
  3%, and our 4-longs on 26% against 18% (`h_c3.py` part C). The eating is what stops.
- **Ramming the enemy's longest dragon late.** No gap: 20 rams per 1,000 rounds of exposure against 21-33
  (`findings.md` section 5).
- **Stride** (free sprint steps). +14% economy locally and no more wins; online 6 wins against 8 on 30 pairs
  (`safer-stride-test-result.txt`). Sprinting does not separate the teams (forgot makes 10 long moves per 50 rounds,
  SSS 43; `deep-read-3.md`).

**From `run1/hypotheses.md`**

- **H1's second half, hunters of 5-9 that walk to her.** The prize is larger than candidate 1's: 44 of our 84
  round-500 losses with her queen alive flip if she dies, and only 13 of those had an in-view chance. But the one
  trial with a walk (qh31) lost 36 hunters in head-ons with other enemies for 8 rams on her, and kills went from 10 to
  11. H1 also kept our longest dragon out and capped the price at 2 segments; I dropped both limits because Vibing++
  and SSS use the longest (30 of 30, 28 of 28) and 7 of the 13 strict flips need an attacker of 5 or more paying 1 to
  3 segments.
- **H2, dragons near our queen ram small intruders.** See "nobody near our queen" above.
- **H3, our queen never dies by her own move.** Kept as the parts of candidate 2 that have a countable fix (the cut,
  the ram); the portal and dead-end parts are above.
- **H4, the queen lives in the quiet rear.** Where she lives is not what differs: our queen spends 44% of her rounds
  more than 10 cells from her start and SSS's 45%; what differs is the price out there (8.1 rams per 1,000 rounds at
  16-25 cells against 2.9; `deep-read-4.md` 5c), which is candidates 2 and 4. The local safe-zone and home-radius
  toggles (card #16) gave no gain in survival.
- **H5, ram their longest late.** No gap, see above.

**From the close reads**

- **A3: "a small dragon rams alone"** (drop the head count). The top three do not: alone or outnumbered they ram a
  same-length enemy on the next cell in 5-24% of cases and a shorter one in 3-11% (`h_c4walk.py`), and such rams
  lose them 0.2 to 1.3 segments each (`h_c4pearls.py`). Locally the same change won 60 of 118 against 68.
- **A2: feed the queen from round 200 by the clock** (forgot only; it wins 52 of 71 games with both queens alive).
  Only one of three does it, and for us both queens are alive at the end in 14 of 401 games.
- **A, A2: send fresh split children at the enemy queen or leader** (Vibing++ only: 4 of 10 leader kills).
- **A2: broadcast the enemy queen's cell by sonar** (SSS only; found in 26-39% of its pings). No top team rams a
  queen outside the attacker's own view (3 of 697 such chances), so the broadcast does not make kills by itself.
- **Openings on maps whose food lies behind a portal or outside the start room.** Known to the team, large on four
  maps, and not a rule that can be stated without the map.

## Counts I made for this file

All scripts are in this directory; outputs are in `h_out/`. Every script reads the lead's and the sub-sessions'
per-game files or walks the replays with `lib.py`; none plays a game. Filter everywhere: opponents rated 2000 or more,
map Schooltime left out.

| Script | What it counts | Output |
|---|---|---|
| `h_base.py` | One row per game and side for meow, the three top teams and meow's opponents: result, end type, run and build, units / total / longest / queen length at rounds 50-450 and at the end, both queens' deaths, every ram chance on either queen (from `q/`, `q3v2/`, `games.csv`) | `h_out/base.json` |
| `h_states.py` | How games end by queen state; the same inside economy bands; our wins if one factor at a time were at the top three's level | `h_out/states.txt` |
| `h_econ.py` | Win rate by own / enemy total length at round 300 in fine bands and by map class; expected wins if our total length at round 300 rose by 10-100%, by the band table and by a smooth fit | `h_out/econ.txt` |
| `h_c1.py` | In-view chances on the enemy queen taken, by team, attacker length, round, own queen alive, attacker = longest, paid steps; games by chance and kill; the what-if "her queen dies on our first untaken chance" under all readings, for any attacker length and for the qh31 limit; wins against losses per team | `h_out/c1.txt` |
| `h_c1walk.py` | Walks our 122 games with an untaken in-view chance: what the dragon did instead on each of the 347 turns, which of our trade rule's three tests failed, what became of the dragon that would have rammed, what the rule would have spent | `h_out/c1walk.json`, `h_out/c1walk.txt` |
| `h_c1flips.py` | The 25 round-500 losses with her queen alive and an untaken in-view chance, one line each: the first chance, what became of the dragon that would have rammed, and every reading of the flip (also with that dragon removed from our final lengths: still 13) | `h_out/c1flips.txt` |
| `h_c1enemy.py` | What our opponents build when their queen is dead: their longest dragon at the end, and its share of their total length at round 400, with the queen alive against dead before round 300; the 25 flippable losses re-scored with that share | `h_out/c1enemy.txt` |
| `h_c1long.py` | Walks our 401 games for the attackers the chance files skip: dragons of 13 or more with her queen in view and within 12 free steps (16 turns in 9 games), with the state of each game | `h_out/c1long.json`, `h_out/c1long.txt` |
| `h_c1recount.py`, `h_c1check.py` | Independent recount of the chance numbers for our 401 games, written without the lead's code and with a stricter path test (435 chances, 99 taken; the lead's 446 and 99); the 25 flippable losses and the flip counts under that stricter test (unchanged) | `h_out/c1recount.json`, `h_out/c1recount.txt`, `h_out/c1check.txt` |
| `h_joint.py` | Candidates 1 and 2 alone and together under the strict and the two realistic readings (A4's survival tables rebuilt) | `h_out/joint.txt` |
| `h_c2.py` | How the own queen ended in wins and in losses, per team; our games by queen rules on / off; each part of candidate 2 (and the parts left out) under the three readings | `h_out/c2.txt` |
| `h_c3.py` | Walks 791 games: a free pearl next to the head eaten or not, before and after our switch round, by whether a longer own dragon is within 9 cells of the pearl and by the dragon's own length; what became of declined pearls; how often dragons of 4 and of 5-9 split | `h_out/c3/`, `h_out/c3.txt` |
| `h_c3dist.py` | Walks our 401 games: after the switch round, the share of free pearls a 2-3-long takes by the distance from the pearl to the nearest longer own dragon (a test of the 9-cell zone), for us and our opponents | `h_out/c3dist.json`, `h_out/c3dist.txt` |
| `h_c3b.py` | Units, total length and longest dragon at rounds 100-450 by map class and team; our big-map wins against losses | `h_out/c3b.txt` |
| `h_c3wins.py` | Our 12 wins on maps over 1,200 cells one by one: the leader at rounds 150 / 300 / 400, the margin on the longest dragon; the close both-dead losses there | `h_out/c3wins.txt` |
| `h_c3game.py` | The count of `h_c3.py` for single games, per 50 rounds and side | `h_out/c3game.txt` |
| `h_c4.py` | Small intruders near the own queen rammed by her team, live bot against the trade-on-contact build and the other teams; the tc30 trial's wins against what our band win rates predict | `h_out/c4.txt` |
| `h_c4walk.py` | Walks the same 791 games: every turn on which a dragon of 4 or shorter could ram an enemy dragon of 4 or shorter (next cell, or 2-3 steps away), taken or not, by relative length and by whether it had as many own heads as enemy heads in view | `h_out/c4w/`, `h_out/c4walk.txt` |
| `h_c4pearls.py` | Walks the same 791 games: every ram between two dragons of 4 or shorter, by relative length and head count at its start, the lengths lost on each side and who ate the pearls of the two corpses: the swing per ram and per game for the side that starts it; wins against losses | `h_out/c4p/`, `h_out/c4pearls.txt` |
| `h_race.py` | Round-500 games with both queens dead: win rate by total-length and by longest-dragon ratio at round 400; which of the two predicts the result; growth of the longest dragon | `h_out/race.txt` |
| `h_peek.py`, `h_build.py`, `h_mdcheck.py` | Show the structure of the per-game files; assemble this file from `h_p*.md`; check its tables and file names | |

Checks against earlier numbers: `h_states.py` reproduces the lead's end-state table (1 of 1, 3 of 14, 41 of 143, 0 of
73) and band table (12 of 168, 16 of 61, 6 of 12, 17 of 27); `h_c1.py` reproduces the lead's chance table (99 of 446)
and the 13 flips of `an4b.py`; `h_joint.py` and `h_c2.py` reproduce A4's worth table within one win (26 strict, 8.6
against A4's 7.4 and 2.6 against 2.4 for the core rule; my realistic numbers also count losses in which both queens
would be alive, at our 3-of-14 rate). `h_c3.py` finds the fall in eating that A3 and the lead found with their own
scripts (83% to 58% here, 82% to 59% and 80% to 56% there). `h_c4walk.py`, summed over the head-count split, gives
the lead's `recount3.py` figures for the top three on big maps (same-length meetings rammed 37% against 34-40%,
shorter enemies 24% against 23-25%) and for our live bot (8% against 9%).

## What I could not determine

1. **What any rule does in a real game.** Every "expected effect" here is arithmetic on games that were played. No
   game was run. The strict readings change one event and keep the rest of the board; the realistic ones borrow our
   own or the top three's rates for the new state. Neither is a measurement.
2. **What the enemy does once its queen is dead, in that same game.** Across games our opponents end with a longer
   longest dragon when their queen is dead than when she is alive (56 against 46), which is why I trust the low
   strict count of candidate 1 (6 or 7 games) more than the lenient one (13). What a given opponent would have built
   in a given game cannot be seen.
3. **What an earlier kill is worth.** In 80 games candidate 1 would kill her 70 rounds earlier on average without
   changing who is alive at the end. A queen that makes most of her team's new dragons dies with that; I counted
   nothing for it.
4. **How long a saved queen of ours lives.** Candidate 2's range (3.7 to 11.1 wins) is the distance between "at our
   own other death rates" and "like a top-three queen". The turns on which she already steps away (rammed within ten
   rounds in 19-24% of cases) suggest the middle; only games can tell.
5. **What a dragon of ours knows.** Candidate 3's mechanism (the leader is the longest own dragon a dragon has heard
   of; pearls within 9 cells of its last known head are left alone) is read from the source. The replay shows the
   fall at the switch round and a slope with the distance from longer dragons, not the leader each dragon had in
   mind. Why the rate is still 72% and not 83% far from every longer dragon, I can only guess (a position remembered
   for up to 25 rounds; self-styled leaders that no longer go into tight places for pearls).
6. **How much length the leader switch costs.** +12% to +24% at round 300 is inferred from growth on the other maps
   and from the pearls declined, not measured. The three local trials of the same change were neutral; local games
   are a poor witness, but they are the only trials.
7. **Whether the trade-on-contact build's 0 wins in 12 big-map games is bad luck.** Its economy moved as the swing
   count predicts (+34 segments a game from its own rams, +25 total length at round 300 measured). Our band win rates
   predicted 1.7 wins. Twelve games cannot separate "economy does not convert for us" from chance.
8. **Whether the top teams really count heads.** "Not outnumbered" in candidate 4 is my count of heads in the
   replay's 7x7 squares. It separates their behaviour very sharply (about 90% against 14-19% for same-length enemies
   on the next cell), but their code may test something else that goes with it.
9. **Whether rams on shorter enemies would pay for us.** They pay the top three +1.1 segments each because their
   team eats 84% of the pearls. In our 31 such rams on big maps our team ate 55% and the swing was -0.7. Whether that
   is a property of our bot or of 31 odd cases I cannot tell.
10. **Whether our own queen should ram hers** when both are alive and hers is the longer. Candidate 1 excludes the
    queen as attacker. It would turn a queen-length game we lose (11 of 14) into a longest-dragon game (29%), but I did
    not count how often she has the chance.
11. **Whether `hunt_path()` sees exactly the chances counted here.** It searches cells that are free at that moment,
    like the stricter of my two counts (435 chances, 99 taken). The qh31 build, which used the same function, took 8
    of 9 with 2-3-longs; the one it missed I did not trace.
12. **Which build played each ladder game.** The two ladder downloads are "the live bot of that hour". The live and
    candidate columns agree wherever both are shown, so I pooled where it did not matter.
13. **Whether opponents would adapt.** The top teams update their bots often. Candidates 1 and 4 feed on what the
    enemy does today (queens that walk into reach, small dragons that come to us); a changed opponent changes the
    numbers.
