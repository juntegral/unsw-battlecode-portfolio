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
