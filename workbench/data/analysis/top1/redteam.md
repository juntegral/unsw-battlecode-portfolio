# Red team: an attack on the four candidate hypotheses (sub-session C)

Written 2026-10-05 for team meow (1119). This file tries to break the four candidates of `hypotheses.md`
(sub-session B) by counting everything again from the replays. The words used in the table are explained right
below it; how the work was done is said after that.

## 1. Verdicts

**In short.** B counted well: almost every count in `hypotheses.md` reproduces, several to the unit. What does not
hold up as well is what the counts are taken to be worth. Candidate 1 survives, at about +1 point of win rate
instead of +1.5 to +2. Candidate 2 survives at about half of its range, and half of that again if it is built from
the code that exists. For candidates 3 and 4 the behaviour is exactly as described and I cannot tell the sign of
the result. None of the four can be judged by wins before the freeze. The largest gap I could count that none of
them works on is the longest-dragon race on the smaller maps (section 2, attack I).

| Candidate | Verdict | B's range | The range I would defend | The strongest objection | What would settle it |
|---|---|---|---|---|---|
| 1. Take the queen | **Holds, weaker than claimed** | +1.5 to +3.2 points, most likely +1.5 to +2 | +0.5 to +2, most likely about +1 (4 to 6 games in 401) | Its small-dragon half has been online twice (56 games a side): chances taken 31% to 95%, rams on her queen 16 to 24 games, her queen alive at the end 19 to 16, certain losses 16 to 15, wins 16 to 17. And a dead enemy queen is worth nothing to us in the lowest economy band, where 41% of the games with an untaken chance are. | No test we can run before the freeze. "Our queen dead, hers alive at round 500" should fall from 18% of games to about 12%; seeing that takes about 300 games a side. In 60 + 60 games only the behaviour can be checked (in-view chances taken 22% to over 90%; games with a chance and no ram 19% to under 3%). |
| 2. Our queen is never spent | **Holds, weaker than claimed** | +0.9 to +2.8 points (strict: 34 games) | +0.3 to +1.5, most likely +0.5 to +1 (2 to 4 games in 401) | A queen of ours that takes the safe step in the same situation is alive at the end of the game in 6 to 9% of cases, the same as one that does not. 25 of the 36 strict flips are against one opponent. Built from the existing pieces the veto would have fired on 51 of the 103 fatal turns. On small maps it lifts a gate the team set on measured local losses. | Only many games: our queen alive at round 500 must rise from 10% to 15% of games (about 250 games a side). In 60 + 60 only the behaviour number can be checked (turns ending in reach by choice: 2.4 per 1,000 queen-rounds to under 0.8) and that wipe-outs on maps of 600 cells or fewer do not rise. |
| 3. No leader before its time | **Cannot be told** (the behaviour holds; the sign of the result is open) | +0.4 to +1.5 | -1.2 to +1.3 | All 12 of our wins on these maps are longest-dragon wins, 10 of them with less total length than the enemy at round 300, won with the leader the round-150 switch builds (7 long at round 150, 24 at round 300). On the maps where the rules start at round 300 our leader is 4 long at round 300 and we lose level games the top three win. The economy gain is inferred. | 20 big-map games a side, as B says, but read on three numbers together: pearl taken 58% to 80%; total length at round 300 from 122 to 140 or more; AND our longest dragon at round 400 not under 15 (19 today). If the third fails the trade is the wrong way round. |
| 4. Do not give way at contact | **Cannot be told** (the behaviour holds; the one trial did not win) | 0 to +2.4, single figure +1 | -0.5 to +1.5 | The tested third tripled our rams, added a fifth to our length at round 300 and won 0 of 12 on the maps it changes (6 of 30 in all against 9.2). The untested two thirds are the rams on which we lose segments today (-0.7 a ram), because our team eats 68% of the pearls of a ram it starts where a top team eats 80%. | The swing per ram we start on the two new rows, on 20 big-map games: it must be above zero. And who eats: our share of the pearls of rams we start must reach 75%. If it stays at 68% the rule only trades dragons. |
| 1 + 2 together | weaker than claimed | +3.1 to +5.3 | +1.2 to +2.5 | The upper half of B's range assumes that a saved queen of ours then lives like a top-three queen. Measured, she is alive at the end 6 to 9% of the time. | as for 1 and 2 |

### Words

- **Queen**: each team's lowest-numbered dragon (id 0 or 1). Both queens move before every other dragon each round.
- **Ram**: a head moves into another head; both dragons die.
- **Reach**: the most steps a dragon can take in one turn: a quarter of its length rounded up is free, each further
  step costs one segment. 1, 2, 3, 5, 6 steps for lengths 2, 3, 4, 5, 6. This is the "plain" reach. Every pearl
  eaten on the way pays for one more step ("pearl-paid" reach); the study's files mostly use the plain one.
- **View**: the 7x7 square around a head.
- **In-view chance**: a turn of a non-queen dragon that starts with the enemy queen's head in its view and a path of
  free cells to it no longer than its reach. Because queens move first, a ram on such a turn cannot be dodged.
- **Safe step**: a one-step move of a queen onto a free cell that no enemy head in her view can reach this round.
  **Queen-round**: one round in which a queen is alive.
- **How a game ends**: by **wipe-out**, or at round 500, where a living queen beats a dead one and the longer living
  queen wins (**queen rule**); with both queens dead the longest single dragon wins (**longest rule**). A **certain
  loss** is a round-500 game with our queen dead and hers alive.
- **Leader**: a team's longest dragon. **Leader rules**: in our bot, from a fixed round on, small dragons leave
  pearls near the leader and dragons longer than 4 stop splitting.
- **Swing** of a ram: pearls of the two corpses eaten by the side that started it, minus the dragon it lost, minus
  the same for the other side; in segments.
- **Economy band**: our total length divided by the enemy's at a given round: under 0.67, 0.67 to 1, 1 to 1.5, over 1.5.
- **Live bot / test builds**: our 401 games against teams rated 2000 or more (map Schooltime left out) are 275 games
  of the released bot and 126 of test builds (stride, passage2, qh31, tc30). 313 are against two teams, test4 and
  WeHaveQuizzes.
- **Strict / realistic**: B's two ways to re-score a played game. Strict changes one event (a queen lives, a queen
  dies) and keeps the final lengths. Realistic gives the changed game our own win rate for games of that kind.
- **Flip**: a played loss that a reading turns into a win.
- **Point**: one percentage point of win rate; one game of our 401 is 0.25 points. We win 112 of 401 (27.9%).
- **80% range**: the range in which the true share lies four times out of five, given the sample.

### How this was done

Every number a candidate's case rests on was counted again with scripts written for this file (`x_*.py`, outputs
in `x_out/`); they use only the replay walker `lib.py` and the game list. Where my number differs from B's, both are
given and the reason. I ran no game. "Measured" means counted on replays by the script named; "inferred" means
arithmetic on played games or a reading of the source. A replay shows positions, orders, deaths, pearls and sonar
rays; it does not show what a bot knew or intended.

Cases were looked at by eye with `story.py` and with `x_eye.py`, which draws the board at the start of one dragon's
own turn (`story.py view` draws the start of the round, before both queens have moved): 28 turns for candidate 1,
19 for candidate 2, 18 for candidate 3 and 16 for candidate 4.

For each candidate the attacks follow the lead's list: A the counts, B cause or consequence, C what happens next,
D sample size, E cross-team, F earlier experiments, G backfire, H the code claim. Attack I, the footing, is one
section for all four, after candidate 4.

## 2. Per candidate

### Candidate 1: take the queen

**The claim (B's):** any dragon of ours except our own queen that has the enemy queen's head in its view and in reach
rams her, at any length. One switch (`QUEEN_HUNT`) and one condition. B: +1.5 to +3.2 points, most likely +1.5 to +2.

**The strongest argument against it, as its opponent would put it.** "Half of this rule has already been on the
ladder twice, against exactly the two opponents the case rests on, and it did what it was built to do and nothing
came of it. In the two hunt trials (56 games each side) our small dragons took 19 of 20 such chances instead of 15 of
49 and we rammed her queen in 24 games instead of 16. Her queen was still alive at the end in 16 games instead of 19,
the games we lose for certain (our queen dead, hers alive) went from 16 to 15, and we won 17 instead of 16. The extra
kills fell on queens that would have died anyway, only later. The other half, long dragons, is the half that one of
the three top teams does not do and is none the worse for. And where we most need help, the games in which we are far
behind on length, a dead enemy queen has never helped us: we won 0 of the 49 round-500 games in which both queens were
dead, hers before round 300, and we were under two thirds of their length."

What is left after the attacks below: the behaviour gap is real and exactly as B counted it, the code claim is
right, it is cheap and it is very unlikely to lose games. Its worth is smaller than B's range: I would defend
**+0.5 to +2 points, most likely about +1 (4 to 6 games in 401)**, and it cannot be seen in wins.

#### A. The counts

Script `x_c1.py` walks all 2,478 replays (the 2,343 of `games.csv` plus 135 smoke-test games that are not in it) and
stores every turn on which a non-queen dragon starts with the enemy queen's head in its 7x7 view. Tables: `x_c1a.py`,
output `x_out/c1a.txt`. My path test is the strict one (every cell with any dragon segment on it at the start of the
turn is blocked, the attacker's own body included), which is what the bot's own search does.

| In-view chances taken (attacker 12 or shorter) | B (lead's files) | B's own strict recount | mine |
|---|---|---|---|
| meow, all 401 games | 99 of 446 | 99 of 435 | 99 of 435 |
| ... attacker 2-3 / 4 / 5-9 / 10-12 | 87 of 231 / 5 of 39 / 5 of 137 / 2 of 39 | | 87 of 231 / 5 of 39 / 5 of 129 / 2 of 36 |
| meow live bot | 67 of 318 | | 67 of 310 |
| our opponents on our queen | 197 of 230 | | 197 of 228 |
| Vibing++ | 266 of 267 | | 265 of 266 |
| SSS | 250 of 254 | | 250 of 252 |
| forgot | 254 of 457 | | 253 of 451 |
| games in which this side rammed her: meow / opponents / Vibing++ / SSS / forgot | 102 / 251 / 318 / 320 / 303 | | the same five numbers |
| our games with a chance and no ram | 76 | | 75 |

The small differences are the path test: the lead's script lets the attacker's own tail cells free up during the
move, mine does not. **The behaviour gap reproduces.** Things the definitions could hide, checked:

- **Does the dragon know it is the queen?** Yes. A dragon sees the id of every part in view, and the queens were ids
  0 and 1 in all 2,478 games (`x_c1a.py`, last lines). The bot sets `enemy_queen_id` from exactly that.
- **Is the path one the bot could see?** In 427 of our 435 chances a path of the same reach lies wholly inside the
  attacker's own 7x7 view; 8 need a cell it cannot see (13 of 456 when dragons over 12 are counted). Not an issue.
- **Bodies that move between turns** do not matter here: the chance is measured at the start of the attacker's own
  turn and the whole move happens inside that turn.
- **Dragons longer than 12**, which B's files skip: 21 more untaken turns of ours in 11 games; Vibing++ takes 10 of
  17 and SSS 12 of 14 at that length, forgot 1 of 31.
- **A hole in everybody's definition, new here.** "Reach" in the study is free steps plus one step per spare
  segment. A dragon that eats a pearl on the way can pay one more step for it. 284 of the 2,128 rams on a queen in
  the data (13%) were made that way, with more steps than the plain reach (`x_c1far.py`, `x_out/c1far.txt`; example
  987051 round 279: a 3-long of the other side moves five steps, eats three corpse pearls on the way and rams our
  queen). Our opponents made 52 of their 251 rams on our queen like this; we made 3 of our 102. Counted as chances
  (`x_c1p.py`, `x_out/c1p.txt`): in our 401 games there were 99 more turns, on top of the 435, on which one of our
  dragons could reach her head only with a pearl-paid step (71 of them 2-3-longs); we took none, our opponents took
  52 of their 65. The bot's `hunt_path()` plans within the plain reach only, so with the switch on we would still
  take none of these: the rule as coded covers four in five of the real chances.
- **By eye:** 28 turns drawn at the start of the attacker's own turn (`x_eye.py`, cases in `x_out/c1_eye.txt`): the
  first untaken chance of each of B's 13 "flip" games, 12 random untaken turns and 3 with a path outside the view.
  All 28 show her head inside the 7x7 square and a free path of the counted length; the dragon stepped away, split or
  walked on. Examples: 1068679 round 461 (weakhold): our 3-long has her 2-long queen, their last dragon, on the next
  cell with nothing else on the board near, and steps north. 1053784 round 448 (Trauma): our 8-long is five steps
  (three of them paid) from her 39-long queen with nothing between, and walks west. 1063010 round 479 (weakhold): our
  6-long is three steps from her 24-long queen and moves two cells north. 1067909 round 63 (Around UNSW): our 3-long
  is two steps from her 2-long queen with three other enemy heads in view and none of ours, and steps away.

#### B. Cause or consequence

**Across all teams the take-up goes with rating** (`x_c1b.py`, `x_out/c1b.txt`; 23 teams with 15 or more chances,
rank correlation 0.80). Of the 15 teams rated 2100 or more, eleven take 79 to 100%; forgot (57%), fandagong (47%),
aAah (40%) and cheji bt (5%, five games) do not. The eight teams under 2100 take 2 to 56%. So this is something
strong teams do; it does not say why they are strong.

**Natural experiments.** For each game and side I took the first in-view chance and compared games in which it was
taken with games in which it was not, inside the same team (`x_c1b.py`; fits in `x_c1b2.py`, `x_out/c1b2.txt`):

| Team | first chance taken: won | not taken: won | raw gap | gap inside the same economy band and own-queen state | fit holding economy, round and own queen fixed | the same, also holding fixed whether the attacker was outnumbered where it stood |
|---|---|---|---|---|---|---|
| meow | 38 of 54 = 70% | 42 of 121 = 35% | +35 | +12 | +12 (80% range +3 to +21) | +9 (-1 to +19) |
| forgot | 154 of 204 = 75% | 62 of 104 = 60% | +15 | +10 | +8 (+2 to +14) | +5 (-2 to +12) |
| other teams rated 2000+ | 279 of 514 = 54% | 29 of 70 = 41% | +13 | +5 | +2 (-6 to +10) | |
| all of these, with a term per team | | | | +6 | +5 (+1 to +9) | **+2.4 (-1.7 to +6.5)** |

("Economy" = own total length divided by the enemy's at the turn of the chance. The fitted number is the change in
win chance for the games in which the chance was NOT taken.) Reading: most of the raw gap is the winning side being
near her queen. In our taken games we had 3.4 times the enemy's length (median), in the untaken ones 0.84. What is
left once the economy and the local head count are held fixed is +2 to +9 points on 121 games, that is **3 to 11
wins in 401, or +0.7 to +2.7 points, with a range that includes zero**. It does not contradict B's +1.5 to +2. It
does not confirm it either; the pooled number sits at the low end.

forgot is the natural experiment B's file points to. It is 15 points better when it takes the first chance, 5 to 8
once the state is held fixed. Its long dragons mostly pass (16 of 38 first chances taken at length 5-12) and those
games were won 13 of 16 against 14 of 22, at different rounds (225 against 368), so that says little.

#### C. What happens next

B's "strict" reading kills her queen and keeps the rest of the game. Three counts say what really follows.

**1. For us a dead enemy queen is worth nothing when we are far behind, and a lot when we are not**
(`x_c1c.py`, `x_out/c1c.txt`). Our games by state at round R; cells are won of games, our queen dead in all of them:

| Our length / theirs at R | R=200: her queen alive / dead | R=300: alive / dead | R=400: alive / dead |
|---|---|---|---|
| under 0.67 | 8 of 107 / 1 of 29 | 7 of 79 / 3 of 63 | 3 of 60 / 1 of 64 |
| 0.67 to 1 | 9 of 33 / 5 of 11 | 7 of 30 / 8 of 23 | 3 of 22 / 10 of 27 |
| 1 to 1.5 | 3 of 13 / 2 of 2 | 1 of 7 / 5 of 5 | 1 of 8 / 9 of 21 |
| over 1.5 | 11 of 17 / 15 of 17 | 5 of 9 / 8 of 11 | 2 of 8 / 12 of 14 |

The same table for all teams rated 2000+ (about 2,600 team-games at round 200) gives the same shape: with the own
queen dead, in the lowest band her death changes the win rate by -8, -1, -2 and +4 points at rounds 100, 200, 300,
400; in the three higher bands by +15 to +39 from round 200 on. A team far ahead simply wins the longest-dragon game
instead. **50 of our 121 games with an untaken first chance were in the lowest band at that turn, and 16 of B's 25
candidate games were in it at round 300.**

**2. When her queen dies early, her team builds a longer leader than the queen would have been**
(`x_c1c.py` part 4a). Our opponents in round-500 games, by their total length at round 400 (under 80 / 80-160 /
over 160): with the queen alive at the end their best other dragon ends at 9 / 18 / 29 and their longest dragon, the
queen included, at 19 / 36 / 54; with the queen dead before round 300 their best dragon ends at 29 / 50 / 63; dead
after round 300, 24 / 31 / 43. B measured the same thing (56 against 46) and for that reason trusts its low count.
I agree, and it also says which kills count: late ones. In round-500 games with both queens dead and us under two thirds of their
length at round 400 we won 0 of 49 when her queen had died before round 300 and 4 of 23 when she died later
(`x_c1g.py` part 4).

Whether a team that has lost its queen then hunts ours harder cannot be seen: our opponents ram our queen whenever
they can in either case (180 of 211 in-view chances with their own queen alive, 17 of 17 with her dead).

**3. The 25 games, one by one** (`x_c1d.py`, `x_out/c1d.txt`). These are the round-500 losses with her queen alive
and an untaken in-view chance. I recount 25, with 13 flips on B's lenient reading and 6 on the hard one, as B does.
Reading each with one more rule (after her death her team gives the pearls her queen ate from then on to its best
other dragon) leaves **6: 990232, 1029017, 1029030, 1053784, 1063010, 1068679; 4 of them live-bot games**. Four of
the six are kills after round 400 of a queen that is her team's longest or only dragon; that is the kind of chance
this rule is really worth something on. The seven I drop are kills of a queen that was still small at that turn (2
to 6 long) and that her team fed to 23-104 afterwards (1044523, 1045197, 1067904, 1067913, 1067909), or late ones
where her best other dragon plus the queen's later meals still beats our longest (1053380, 1068054).

**4. What the top teams lose when a long dragon does it** (`x_c1c.py` part 4b). Rams on a queen by the team's own
longest dragon of 10 or more: Vibing++ 9 (6 won), SSS 7 (6 won). Three of Vibing++'s were then lost on the longest
dragon by 6 to 8 segments after spending a 29-, an 18- and a 10-long (1055289, 1056426, 1067623). Sixteen cases
cannot say whether those rams cost the games; over all rams by a dragon of 5 or more the top three win 80%, against
61% for games in the same state with her queen alive and 76% with her dead. No sign of harm.

#### D. Sample size

- Shares (80% ranges): we take 38% of chances with 2-3-longs (34 to 42%), 13% with 4-longs (7 to 21%), 4% with
  longer ones (3 to 7%). Solid.
- **The game count is thin and lopsided.** The 25 candidate games: 11 against test4, 8 against WeHaveQuizzes, 4
  against dev test 1, 1 each against tungtung67 and Vibing++. **Ten of the 25 are on one map, Australia, and none
  of those ten flips on the hard reading (one on the lenient).** Maps over 1,200 cells: 16 games, 4 lenient flips, 2
  hard; smaller maps: 9 games, 9 and 4. By run: 6 of the 13 lenient flips are in test builds (tc30 4, stride 2), 7
  in the live bot's 275 games.
- **Against test4 and WeHaveQuizzes separately** the behaviour holds (2-3-longs take 53% and 33%; we ram her in 23%
  and 32% of games). Lenient / hard flips: test4 7 / 2, WeHaveQuizzes 4 / 2.
- **Against the stronger teams** there is nothing to count: 21 games against the top three, 9 with a chance, 4 of 21
  chances taken, one candidate game (Australia against Vibing++, no flip).
- **Do top queens offer the chance at all?** Yes, as often as test4's and WeHaveQuizzes's. Rounds with an in-view
  chance per 1,000 rounds the queen is alive, when the attackers are the top three: test4's queen 2.0,
  WeHaveQuizzes's 3.9, Vibing++'s 3.4, SSS's 3.1, forgot's 2.7. To our dragons: forgot's queen 2.8 (16 games),
  Vibing++'s 4.5 (5 games). So the opening exists at the qualifier level; what such a kill is then worth to us
  depends on not being far behind (item C1).

#### E. Cross-team

Vibing++ and SSS do all of it. forgot does the small-dragon part from round 100 on and not the long-dragon part, and
is level with them. forgot's price for that can be seen (`x_c1e.py`, `x_out/c1e.txt`): it ends 66 of 632 games (10%)
with its own queen dead and hers alive, against 38 of 502 (8%) and 28 of 503 (6%), and in the 55 games in which it
passed up the first chance and took no later one it won 45% (75% when it took the first). That is the size of thing
this rule is worth to a top team: one or two games in a hundred.
A 2000+ team that does the opposite and does well: fandagong takes 47% and is rated 2131; its record in this data
(against the top three) is 26%, so it is no counter-example either way.

#### F. Earlier experiments

- **The team's log** (`work/plan.md`). The hunt was tried locally twice and left off both times on the numbers:
  hunting with every dragon ("QS0PH") won 91 of 156 against 96 for the same build without it; hunting with dragons of
  4 or shorter ("H4") won 57 of 120 against 58 versus a hunting sparring bot and 59 against 60 versus the release
  (+10 -11 by pairs), noted as "REJECTED (no gain even vs the hunter spar)". **B's sentence "`QUEEN_HUNT` was on in
  v54 and has been off since v55" is not what the log says.** v54 had no queen mode at all, and the hunt only exists
  inside queen mode; v55 introduced queen mode without the hunt. As far as the log shows, the hunt has never been in
  a released bot. Local games are a poor witness (the opponent is our own
  bot, whose queen dies by round 30-50 anyway), so these trials do not contradict the candidate; they are simply
  empty.
- **Online, recounted from the replays** (`x_c1f.py`, `x_out/c1f.txt`). qh31 is in `games.csv`. **qh31b, a second
  run of the same idea with a portal fix, finished at 11:18 today and is not in B's file**; its 90 games are in
  `data/online/smoke/qh31b-*`. Both builds hunt with dragons of 4 or shorter and walk towards a queen they have
  seen; candidate 1 does not walk. Against test4 and WeHaveQuizzes, Schooltime left out, 28 pairs each:

| | live bot (the two "-old" halves, 56 games) | hunt builds (56 games) |
|---|---|---|
| in-view chances taken by 2-3-longs | 15 of 49 | 19 of 20 |
| ... by dragons of 5 or more | 0 of 21 | 1 of 23 |
| games in which we rammed her queen | 16 | 24 |
| games with a chance and no ram | 14 | 4 |
| her queen alive at the end | 19 | 16 |
| median round of her queen's death | 213 | 149 |
| our queen dead, hers alive at the end (certain loss) | 16 | 15 |
| both queens dead at the end | 34 | 38 |
| games won | 16 | 17 |
| our own queen: median round of death / alive at the end | 105 / 6 | 76 / 3 |

  In the 10 pairs in which only the hunt build rammed her it won 3 and the live bot 0; in the other 46 pairs it won
  14 and the live bot 16. Against dev test 1 (14 pairs): rams 4 against 1, wins 1 against 3. **What this tests:** the
  small-dragon half, plus a walk that candidate 1 leaves out. **What it says:** the behaviour number moves by the
  factor B asks for (its test 1 and 2) and the end state barely moves (its test 3: her queen alive at the end 34% to
  29%, where B asks for "40% towards 30%" and says the rule is worth the low end or less if it stays at 38%). Fifty-six
  games cannot tell 29% from 34%. It is the only real evidence there is, and it points at "small".
  One thing to watch (`x_c1pairs.py`, `x_out/c1pairs.txt`): in all three hunt runs our own queen died earlier in the
  hunt build than in its pair: 16 pairs earlier against 10 later, 16 against 9, and 8 against 5 against dev test 1
  (40 against 24 in all). That is the one number in the trials that points to harm. It may be noise: two runs of the
  unchanged live bot a day apart differ by 15 against 9, and the passage2 pairs show 16 against 11 with no hunt in
  them. Candidate 1 has no walk, and a walk is the likeliest way for a hunt to change what is around our queen.

#### G. Backfire

Counted in `x_c1g.py` (`x_out/c1g.txt`) on our 401 games.

- **Wins in which the rule would have fired:** 43 of our 112 wins (27 wipe-outs, 16 on the longest dragon). In the
  16 I took the attacker out of our final lengths: the win stands in 15; the 16th (1027973) was 13 against 13 and the
  attacker died 39 rounds later anyway. In one win (1058366, Maze, round 467) the attacker was a 25-long that ended
  the game as our longest at 69; without it we still had a 40-long against her best 14.
- **Our longest dragon as attacker:** 60 untaken turns in 26 games had our longest dragon, 8 or longer, as the
  attacker; 23 of those games were lost anyway and the 3 wins stand. Dragons of 13 or more: 21 turns in 11 games,
  10 lost.
- **What it spends:** on the first untaken chance of 123 games, 584 segments (4.7 a game); 107 of those dragons were
  dead by the end anyway, 53 within 20 rounds.
- **Rams made while outnumbered:** 288 of our 435 chances came with fewer own heads than enemy heads in the
  attacker's view (106 with nobody but her). There the enemy eats the pearls of both corpses. That is a few segments
  a game, on the wrong side of candidate 4's own swing table, and the reason the take-up coefficient shrinks when
  the head count is held fixed.
- **Our own queen as attacker** on maps of 600 cells or fewer, where the bot does not treat her as queen: B's one
  changed condition is needed exactly for this (see H). It is rare: our queen had the enemy queen's head in view and
  reach on 4 turns in 3 such games (she rammed her once, in a game we lost), and on 8 turns in 5 games on larger maps,
  where the rule does not apply to her (`x_c2b.py` part 5).
- **Failed rams:** a few at most. The search takes cells it cannot see for free, and 8 of the 435 paths leave the
  view.

I could not construct a way for this rule to lose more than a game or two in 400. Its risk is that it does little.

#### H. The code claim

Read: `observe()`, `mark_hunt_targets()`, `hunt_path()`, `act()`, `sprint_reach()`, `is_queen()`, `real_queen()`.

- `QUEEN_HUNT` appears in one place, `mark_hunt_targets()`. With it on, every dragon for which `is_queen()` is false
  marks the enemy queen's head when it is among the heads seen this turn; leaders and feeders are not excluded.
  `hunt_path()` then searches breadth-first over cells with `enter_time == 0` (no part of any dragon seen this
  turn, the own body included) up to `min(sprint_reach(), QUEEN_HUNT_STEPS = 12)` steps, and `act()` plays that path
  before feeding, splitting or anything else. Nothing else is switched on: `QUEEN_CHASE_DIST` is 0, so nobody walks
  towards her. **B's description is right.**
- `enemy_queen_id` is 1 minus the own queen's id, or the id of any enemy part with id 0 or 1 in view. It was right in
  all 2,478 games.
- **The one condition B adds is needed and is the only map-size condition in it.** `is_queen()` is false on maps of
  600 cells or fewer unless the home is closed, so without `real_queen()` in the first line our own queen would ram
  hers there.
- Two small things B does not say. The search treats cells it has not seen this turn as free and unknown edges as
  open, so a path that leaves the view can end on a body or kelp (8 of 435 chances). And it is capped at 12 steps and
  at the plain reach, so it will not make the pearl-paid rams of item A.
- A hidden cost in "at any length": a 12-long that needs 12 steps pays 9 segments and then dies. `QUEEN_HUNT_STEPS`
  could be left at 12; 93 of our 357 untaken turns needed 3 or more paid steps.

#### What is left of the claim

| | B | after the attacks |
|---|---|---|
| the behaviour gap | 22% against 86 to 100% | the same; holds against each opponent and in every run |
| games that end differently | 6 to 13 of 401, "7 by the count I trust most" | 6 by reading each game (4 of 275 for the live bot); 3 to 11 by the natural experiment, zero not excluded |
| points | +1.5 to +3.2, most likely +1.5 to +2 | **+0.5 to +2, most likely about +1** |
| what it rests on | the top three do it | two of three do all of it; the online trials of its tested half moved the behaviour and not the end state |
| where it acts | "at every state of the economy" | not in the lowest economy band, where 41% of the chances are; mostly late kills of a fed or last queen |
| cost | one switch, one condition | agreed |

### Candidate 2: our queen is never spent

**The claim (B's):** our queen never ends a move inside the reach of an enemy head she can see while another move
exists; she never rams; and when she has no free cell she gives away two segments from her tail ("sheds") instead
of keeping two and giving away the rest ("cuts"). On every map, also the small ones where the queen rules are off
today. B: +0.9 to +2.8 points (strict reading: 34 games).

**The strongest argument against it, as its opponent would put it.** "A queen saved on this turn is not a queen
alive at round 500. We can see what happens to our queen when she does take the safe step in the very same
situation: she is not rammed that round, and then she is dead within 50 rounds six times out of ten and alive at
the end of the game in 6 to 9% of cases, the same as when she did not take it. The 34 'flips' need her alive at
round 500. Twenty-five of them are against one opponent. A third of the deaths it counts are on small maps, where
the team measured that queen rules lose the fight and switched them off for that reason, and where our queen is
alive at the end in 4 of 145 games whatever she does. Every earlier attempt to protect her cost games, locally and
online. And as B wants it coded, from the pieces that exist, the rule is blind to pearl-paid steps and to the part
of an enemy that lies outside her view."

What is left: the counts are right, the rule is sound as a rule, and its three parts are not equal. I would defend
**+0.3 to +1.5 points (1 to 6 games in 401), most likely about +0.5 to +1**, the low end if it is built from the
existing pieces, and I would not switch it on for maps of 600 cells or fewer without a test of its own.

#### A. The counts

Script `x_c2.py` walks all 2,478 replays and stores every turn of either queen that starts with an enemy head in
her view; tables: `x_c2a.py` (`x_out/c2a.txt`), `x_c2b.py`, `x_c2c.py`, `x_c2cut.py`. My first model used the plain
reach and called 42 of our queen's fatal cells "safe"; the reason is the pearl-paid step (candidate 1, item A). With
pearl-paid steps in the model, as A4 has them, the counts agree:

| | B / A4 | mine (pearl-paid reach) | mine, plain reach |
|---|---|---|---|
| our queen's deaths: rammed after stepping into reach / staying in reach, a safe step on the board | 66 / 38 = 104 | 67 / 39 = 106 | 67 / 17 = 84 |
| rammed, cornered (no safe step) | 114 | 114 | 94 |
| rammed on a cell the model calls safe | 2 | 0 | 42 |
| rammed by an enemy outside her view / boxed in / she rams | 31 / 91 / 19 | 31 / 91 / 19 | the same |
| avoidable rams, live bot / our opponents / forgot / SSS / Vibing++ | 68 / 27 / 39 / 38 / 35 | 70 / 26 / 40 / 38 / 34 | 55 / 28 / 32 / 35 / 31 |
| turns that end in reach by her own choice, per 1,000 queen-rounds: meow / opponents / top three | 2.66 / 1.46 / 0.6 to 1.1 | 2.45 / 1.34 / 0.5 to 0.9 | 1.94 / 1.16 / 0.4 to 0.8 |
| the same against test4 and WeHaveQuizzes only: meow / top three | 2.6 / 0.4 | 2.35 / 0.36 | |
| such a turn is punished by a ram that round: our queen / theirs / top three | 71% / 16% / 32 to 47% | 76% / 19% / 48 to 53% | |
| turns the rule would change in 401 games, and pearls eaten on them | 149, 21 | 138, 22 | 109, 22 |
| a boxed-in queen of 6 or more cuts / sheds: meow, forgot, SSS, Vibing++ | 40 / 0, 0 / 1,448, 0 / 394, 105 / 78 | 39 / 0, 0 / 1,448, 0 / 394, 104 / 74 (+31 other) | |
| all queen deaths per 1,000 queen-rounds: meow / opponents / forgot / SSS / Vibing++ | 6.5 / 2.2 / 2.8 / 2.1 / 3.4 | 6.4 / 2.1 / 2.8 / 2.1 / 3.4 | |

("Queen-round" = one round in which a queen is alive. "Safe step" = a one-step move onto a free cell that no enemy
head in her view can reach this round. My "ends in reach" is measured on the real board after her move, A4's on the
board at the start of her turn; that is the small difference in the rates.) **The behaviour gap reproduces**: our
queen ends a turn in a visible reach by choice three to four times as often as a top-three queen, six times as often
against the same two opponents, and it is punished three times out of four.

By eye (`x_c2pick.py`, `x_eye.py`, `x_out/c2_eye.txt`), 19 turns. Of seven "stepped in" deaths: in three the killer
needed a pearl-paid step (1059073 round 133: our 2-long queen steps beside a pearl that lies between her and a
2-long; 1063016 round 59: two pearls in a row; 1053387 round 90); in two the only "safe" cell was a pocket (1068052
round 165: a one-cell dead end; 1029037 round 72: three cells); two were plain steps next to a head with open water
elsewhere (1058154 round 18, 1063767 round 153). Two cuts: 1044523 and 990346, both round 0 on Slithery Fight (below).

#### B and C. Cause or consequence, and what happens next

**The safe step works for one round and not for the game** (`x_c2b.py` part 1, `x_out/c2b.txt`). Same situation,
our queen, by what she did:

| Situation at the start of her turn | she ended | turns | rammed that round | rammed within 10 rounds | dead of anything within 50 rounds | alive at the end of the game |
|---|---|---|---|---|---|---|
| inside a visible reach, a safe step exists | outside reach | 288 | 0% | 23% | 59% | **9%** |
| | in reach | 56 | 70% | 80% | 80% | 9% |
| outside reach, a small enemy within 4 steps, a safe step exists | outside reach | 922 | 0.1% | 27% | 64% | **6%** |
| | in reach | 80 | 82% | 88% | 91% | 4% |

The first three number columns are A4's table that B quotes (0.3% / 24% against 56% / 65%; mine agree). The last
two are new. On maps of 600 cells or fewer the queen that took the safe step was dead within 50 rounds in 88 to 99%
of cases and alive at the end in 1 of 142. A top-three queen in the same situation after the safe step: dead within
50 rounds in 57 to 61%, alive at the end in 17 to 19%. So the rule turns a death this round into a death a few dozen
rounds later by one of the routes it does not touch, which are already the larger part of her deaths: cornered
(114 of our 362), boxed in (91) or rammed by an enemy she cannot see (31).

**What that makes of the 34 flips** (`x_c2b.py` part 3). My recount of B's table, with the deaths the three parts
touch:

| Part | deaths | in wipe-outs | in round-500 wins | in round-500 losses, her queen alive | in round-500 losses, both dead (flip if ours lives) | expected flips if she then lives as often as our own queen alive at that round | as a top-three queen |
|---|---|---|---|---|---|---|---|
| never end in a visible reach | 106 (B: 104) | 55 | 6 | 19 | 26 (B: 26) | 4.9 | 12.9 |
| shed 2, never cut | 24 (B: 14) | 2 | 8 | 8 | 6 (B: 4) | 0.7 | 2.3 |
| never ram | 10 | 6 | 0 | 0 | 4 (B: 4) | 0.7 | 2.0 |
| all three | 140 (B: 128) | 63 | 14 | 27 | **36 (B: 34)** | 6.3 (B: 3.7) | 17.2 (B: 11.1) |

My two "expected" columns use one survival curve for all games (our queen alive at round 100 is alive at the end
in 15% of games, at round 200 in 26%; a top-three queen in 46% and 56%) and are cruder than B's, which splits by
economy and map size; B's lower numbers are the better ones. The direct measurement is lower still: queens of ours
that took the safe step were alive at the end 6 to 9% of the time. On that, the core rule is worth **26 x 0.06 to
0.09 = about 2 games in 401**, which is A4's own low reading (2.4) and B's low end (2.6). I see no reason to expect
more than that from this rule alone; the high end needs her to "live like a top-three queen", and nothing in the
candidate makes her do that.

**Economy does not explain the gap away, but it bounds the gain.** 60 of the 104 deaths came with our team under
two thirds of the enemy's length (B's own count). The comparison against the same two opponents (ours 2.35 turns by
choice per 1,000 queen-rounds, the top three's 0.36) is the cleanest one there is, and it holds.

**Allies near her do not change what happens at contact** (`x_c2c.py` part 2). With an enemy head within 3 steps, a
2-3-long queen of ours is rammed that round in 10 / 12 / 13 / 19% of turns with 0 / 1 / 2 / 3 or more own heads
within 6 steps; the top three's in 6 to 12% whatever the number. More own dragons near our queen go with more rams,
not fewer (they also take her exits). B was right to drop "defenders near the queen".

#### D. Sample size

- 106 deaths in 401 games is a solid count (80% range 24 to 29% of games). The flips are not: **25 of the 36 strict
  flips are against WeHaveQuizzes, 8 against test4** (`x_c2b.py`, last two blocks). Against test4 our queen dies this
  way just as often (45 deaths against 40), but test4's queen is usually alive at the end, so a living 2-long queen
  of ours would still lose on queen length. The candidate's value against test4 hangs on candidate 1.
- By map size: 28 strict flips on maps over 600 cells, 8 on smaller ones (where 37 of the 50 deaths are in
  wipe-outs).
- Live bot only: 97 deaths, 19 strict flips (B: 87 and 19).
- Against the top three there is no count (21 games).

#### E. Cross-team

- **Never ending in reach by choice:** all three, at a third to a quarter of our rate. Holds.
- **Shed, do not cut:** SSS and forgot always shed; Vibing++ cuts (it keeps 3, we keep 2) and is rank 1. New here
  (`x_c2c.py` part 1): after its 104 cuts Vibing++'s queen is dead within 20 rounds in 17% and it wins 63% of those
  games; after its 44 sheds, 20% and 84%; SSS and forgot after a shed: dead within 20 rounds in 6 to 8%. After our
  39 cuts she is dead within 5 rounds in 44%. So shedding is the better habit, and Vibing++ is somewhat worse off
  when it cuts, but it is not what makes or breaks a top team.
- **This part is mostly one map's opening** (`x_c2cut.py`, `x_out/c2cut.txt`). 29 of our 39 cuts are round 0 to 5
  on Slithery Fight, where the queen starts as a 25-long coil with no free cell. We keep 2 and give 23 to a child;
  SSS and forgot shed 2 a round; Vibing++ keeps 3; test4 splits in half; **WeHaveQuizzes does exactly what we do
  (keeps 2) and its queen is not dead by round 100 in any of its 12 games on that map**. Ours is dead by round 10 in
  13 of 47 games there (all opponents) and never alive at the end; SSS's is alive at the end in 16 of 43, forgot's in
  23 of 35. So the cut is not what kills her there; being left 2 long in the middle of her own team is. The ten
  later cuts are queens of 6 to 61 long; one is a certain thrown win (990346: 57 long at round 385, dead the next
  round, the enemy queen ends 3 long), 1069661 (36 long, dead 22 rounds later, her queen dead at the end) is a
  possible one, three were won anyway.
- **Never ramming:** SSS never does, the others almost never. Our 17 queen rams on small maps came in games of which
  we won 1 (`x_c2b.py` part 5). Holds, and costs nothing visible.

#### F. Earlier experiments

From `work/plan.md` (all local, against our own older bots) and the smoke records:

- A bigger number instead of an order: threat x3 and x6, guard radius 3: "do not cut rams (rammed 9-12)" in 24
  games. This is the nearest thing to the candidate and it failed for the reason B gives (a sum, not an order).
- A separate queen planner with a "never in reach" veto: 69 to 71 wins of 156 where the base won 95; the queen
  alive at the end in 7 to 10 games instead of 4; "queen protection costs 11-26 wins and buys 2-5 queen wins". It did
  much more than the veto. What transfers is the second half of the sentence: even a queen that was protected at
  every step was alive at the end in 7 to 12 of 156 games.
- **The queen rules on small maps.** With the minimal queen rules on every map the local sets went from 16 to 13
  and from 11 to 7 wins on small maps; letting the queen trade again did not bring them back ("queen rules cost on
  small maps ..., not via trading"). `QUEEN_MIN_CELLS 600` exists because of this. B's change list makes
  `map_threats()`, `threat_at()`, `is_trader()`, the split test and the paid escape use `real_queen()`: on small maps
  that is most of what the gate switches off, except the portal ban. B says so under risks. I rate it higher: it is
  the one place where this candidate contradicts a measured result of the team's own.
- **Online: qn23**, the "queen does not walk into traps" build (another rule; recounted in `x_c1f.py`): 8 wins of 42
  against a live rate near 28%, our queen alive at the end in 2, and against test4 and WeHaveQuizzes the team's own
  count is 3 wins of 30 with her median death at round 87 against 114. Too small to blame the rule, but it is the
  only queen-safety rule that has been online and it did not help the queen.
- Too small to say / tested something else: all of the above. None is this veto on the normal step chooser.

#### G. Backfire

- **A queen that refuses a pearl:** she ate a pearl on 22 of the 138 turns the rule would change, 12 of them before
  round 100. One pearl per 18 games. Not a cost.
- **A queen that flees into a dead end:** on 20 of the 138 turns the only safe step was a pocket or a portal step
  (room under 8 cells), and on 13 of the 106 fatal ones. B's veto skips closed cells, so these become "cornered",
  not saved.
- **A queen that stops fighting on small maps:** 44 of the 138 turns, 36 of the 106 deaths and all 10 own rams are on
  maps of 600 cells or fewer. There 85 of our 145 games end by wipe-out (we win 30 of them), the queen is one of a
  handful of dragons, and she is alive at the end in 4 games whatever she does (`x_small.py`). A rule that makes her
  step away there takes a fighter out of a fight that decides six games in ten, and a queen-rule win almost never
  pays it back. The count that could show harm does not exist: nobody has played it.
- **Giving away 2 a round inside her own coil** makes eleven 2-long children next to her head on Slithery Fight
  instead of one 23-long. SSS and forgot do it and lose nothing; whether our small dragons then step onto her last
  exit, as they do in 20 games today, cannot be seen in a replay of the other behaviour.

#### H. The code claim

Read: `pick_direction()` (the `LONG_SAFE_MIN_LENGTH` block), `score_step()`, `map_threats()`, `threat_at()`,
`stride_reach_map()`, `spread_kill()`, `queen_margin()`, `sprint_escape()`, `escape_child_size()`,
`split_child_size()`, `is_trader()`, `is_queen()`, `real_queen()`.

- B's description of today's code is right: for the queen the danger of a cell is one term of a sum
  (`PENALTY_HEAD_RACE` scaled by her length, smallest for a 2-long) and a pearl can outweigh it; dragons of 8 or
  more get an order of preference (`LONG_THREAT_VETO`), the queen does not; `escape_child_size()` returns
  `length - 2` when no cell is enterable.
- **The pieces B wants to reuse do not compute "every cell an enemy head can move into", and the difference is half
  of the candidate.** `stride_reach_map()` gives each enemy a reach from `visible_parts(id)`, the number of its
  segments inside her 7x7 view, and `spread_kill()` counts plain steps. Missing: pearl-paid steps, and the part of an
  enemy that lies outside her view (the killer was only partly in her view in 70 of our 220 rams by a seen enemy; a
  3-long showing 2 or 1 segments in 29 of them). I replayed our queen's turns against four reach models
  (`x_c2vis.py`, `x_c2vis2.py`, `x_out/c2vis.txt`). She moved onto a cell in reach although a free cell out of reach
  existed on 136 turns in 401 games and was rammed that round on 103 of them. A veto would have fired on:

  | reach model | of the 136 turns | of the 103 fatal ones | turns it changes in all | of them false alarms |
  |---|---|---|---|---|
  | true length, pearl-paid steps (the study's "safe step") | 136 | 103 | 136 | 0 |
  | true length, plain steps | 96 | 71 | | |
  | **the existing pieces: visible parts, plain steps** | **62** | **51** | 68 | 0 |
  | the same with one unseen segment assumed (A4's suggestion) | 67 | 59 | 220 | 150 |

  When it fires, the cells it allows are truly safe (61 of 62). But built as B describes it sees half of the deaths
  the candidate is credited with. Guessing one more segment recovers little and triples the turns it changes. To get
  the whole count the team would have to write a reach test that follows pearls and guesses lengths, which is new
  code and not "the pieces exist".
- **It is not "one block".** B lists five more places that must change, and three of them (`map_threats()`,
  `threat_at()`, `is_trader()`) change how the queen scores every step on small maps, not only the three things
  named. That is the hidden map-size condition of this candidate: the rule itself has none, but applying it on small
  maps means lifting most of `QUEEN_MIN_CELLS`.
- `escape_child_size()`: returning 2 for the real queen when no move exists is a one-line change and does what B
  says.

#### What is left of the claim

| | B | after the attacks |
|---|---|---|
| the behaviour gap | 2.66 against 0.6 to 1.1 per 1,000 queen-rounds; 104 deaths | 2.45 against 0.5 to 0.9; 106 deaths |
| games that end differently | 34 strict, 3.7 to 11.1 realistic | 36 strict; about 2 to 6 realistic, and 25 of the 36 against one opponent |
| points | +0.9 to +2.8 | **+0.3 to +1.5** |
| the three parts | one candidate | the veto: sound, worth about 2 games with a perfect reach test and about 1 as B would code it (it fires on 51 of the 103 fatal turns); never ram: free, 0 to 1 game; shed not cut: mostly the Slithery Fight start, plus one or two thrown wins in 400 games |
| on small maps | "part of the change" | untested, against the team's own local result, in the games we are closest to winning |

### Candidate 3: no leader before its time

**The claim (B's):** the "leader rules" (small dragons leave pearls near the longest own dragon they know of; dragons
longer than 4 stop splitting) start at round 300 on every map, instead of round 150 on maps over 1,200 cells. One
constant. B: +0.4 to +1.5 points.

**The strongest argument against it, as its opponent would put it.** "Every one of the twelve games we have won on
these maps was won on the longest dragon, and in ten of them the enemy had more total length than we did at round
300. The dragon that won them grew from 7 segments at round 150 to 24 at round 300; that is the window this
candidate gives back to the small dragons. On the maps where the same rules already start at round 300 our longest
dragon is 4 long at round 300, and there we lose level games that the top three win. The gain is inferred: nobody has
seen our bot play rounds 150 to 300 on a big map without the switch against a ladder opponent, three local runs of
exactly this change were flat, and where the same games can be followed through the switch a full team of ours still
grows 13% under it while the collapse is in games that were lost by round 150."

What is left: the behaviour claim is right to the turn. The economy claim is plausible for half of the games. The
win claim leaves out what the switch buys, and with that put back in I cannot tell its sign: **between -1.2 and +1.3
points, most likely near zero or slightly above.** It is not the candidate that "could most safely ride along".

#### A. The counts

`x_c34.py` walks all 2,478 replays; tables `x_c3a.py` (`x_out/c3a.txt`). The turn counted is B's: a non-queen dragon
of 2 to 4 moves, no enemy head is in its view, and a pearl lies on a free next cell that has a further free
neighbour. Share of such turns on which its first step takes the pearl:

| Maps over 1,200 cells | B: meow live | mine: meow live | mine: our opponents | Vibing++ | SSS | forgot |
|---|---|---|---|---|---|---|
| rounds 0-149 | 83% of 16,079 | 83% of 16,079 | 85% | 89% | 80% | 94% |
| rounds 150-399 | 58% of 18,312 | 58% of 18,312 (59% to round 299, 57% after) | 85% | 86% | 83% | 93% |
| ... the pearl is 0-3 / 4-6 / 7-9 / 10-12 / 13-16 / 17+ cells from the nearest longer own dragon | 50 / 51 / 57 / 65 / 69 / 72% | 51 / 52 / 61 / 70 / 73 / 76% | 82 to 89% | | | |
| ... own length 2 / 3 / 4 | 54 / 57 / 88% | 54 / 57 / 88% | 84 / 83 / 86% | | | |
| in 10-round blocks: rounds 130-139, 140-149, 150-159, 160-169, 170-179 | | 84, 84, **64, 60, 58%** | 86, 86, 85, 85, 84% | top three 90, 89, 89, 89, 89% | | |

| Maps of 1,200 cells or fewer | B: meow live | mine: meow live | our opponents | top three |
|---|---|---|---|---|
| rounds 0-299 | 88% of 28,107 | 88% of 28,107 | 84% | 89% |
| rounds 300-399 | 53% of 8,202 | 53% of 8,202 | 78% | 87% |
| in 10-round blocks: rounds 280-289, 290-299, 300-309, 310-319 | | 85, 83, **64, 51%** | 81, 81, 82, 80% | 88, 88, 88, 88% |

The same turn counts as B's, to the unit. **The fall is real, it comes in the ten rounds after our own switch on
both kinds of map, and nobody else has it.** Units, total length and longest dragon also reproduce (live bot, big
maps, round 150 to 300: 47.2 to 35.9 units, 123 to 122 total, 5.8 to 14.2 longest; top three 55.6 to 58.8, 165 to
206, 8.6 to 18.4).

By eye (`x_pick34.py`, `x_out/c3_eye.txt`): 18 declined pearls after the switch, drawn at the dragon's own turn. In
all 18 a pearl lies on a free next cell with no enemy head in the 7x7 square and the 2-3-long steps elsewhere; in
14 a longer own dragon is within 9 cells of the pearl (a 19-long one cell away in 1063016 round 257; a 4-long two
cells away in 1052760 round 193), in 4 the nearest longer own dragon is 10 to 42 cells away (1045376 round 151: 42
cells). So the zone explains most of it and not all, as B says.

#### B. Cause or consequence

Is the fall the switch, or the state of the game at that point? The switch (`x_c3a.py` part 2). After it the rate
is 60% in the games we won and 58% in the games we lost (big maps), 56% and 52% on the others; it is between 48
and 62% in every economy band that holds more than one game. And the same bot on the smaller maps keeps eating at 86% through rounds 150 to 299. B's reading
holds.

#### C. What happens next: what the switch costs, and what it buys

**What it costs is less clear than B's table suggests.** B infers +12 to +24% total length at round 300 from two
comparisons. Following the same games through the switch (`x_c3stall.py`, `x_out/c3stall.txt`):

| Live bot, maps over 1,200 cells, games that reach round 300 | units at 150 / 200 / 300 (the enemy's) | total length at 150 / 200 / 300 (the enemy's) | longest at 150 / 300 |
|---|---|---|---|
| 56 or more units at round 150 (36 games) | 60 / 58 / 53 (59 / 61 / 61) | 164 / 178 / 185 (205 / 237 / 285) | 7 / 20 |
| fewer (39 games) | 37 / 28 / 20 (62 / 62 / 62) | 91 / 75 / 63 (209 / 282 / 365) | 4 / 9 |
| top three, all their big-map games | 56 / 58 / 59 | 165 / 185 / 207 | 9 / 19 |

"Our total length stands still from round 150 to 300" is the average of two different things. With a full team we
still grow 13% under the leader rules (the top three 25%, our opponents in those games 39%); with 37 units against
62 we are being overrun and lose a third of our length whatever the small dragons eat. For the first half B's +12
to +24% is possible; for the second I see no reason to expect it.

A second check: on the smaller maps the same rules switch on at round 300 and our total length does not fall
afterwards (61, 61, 62 at rounds 300, 350, 400 on the same games; our opponents 99, 99, 95; `x_c3stall.py`). And B's premise that
before the switch we grow "half as fast as the others" on those maps (+20% against +41% and +47%) comes from means
over different sets of games at each round; on the same games it is +24% against +29% and +27%.

**What it buys is the dragon our big-map wins are won with** (`x_c3wins.py`, `x_race2.py`; outputs
`x_out/c3wins.txt`, `x_out/race2.txt`). Our 12 wins on these maps, medians, ours against the enemy's:

| Round | units | total length | longest dragon | wins in which ours is the longer |
|---|---|---|---|---|
| 150 | 60 : 62 | 163 : 227 | 7 : 12 | 3 |
| 200 | 59 : 62 | 177 : 260 | 13 : 15 | 5 |
| 300 | 55 : 62 | 207 : 302 | 24 : 20 | 7 |
| 400 | 56 : 54 | 215 : 270 | 27 : 27 | 5 |
| end | | | 69 : 39 | 12 |

All 12 are round-500 games with both queens dead. In 10 of the 12 the enemy had more total length at round 300.
B's sentence "our wins there are the games in which the economy held, not games in which an early leader was built
at its cost" is half of it: they are games in which we kept 55 to 60 units, and in which a leader built from round
150 on was level with or ahead of the enemy's by round 300 although the enemy had half as much length again.

How much of those wins is the early leader? Two readings.

- **By the margins.** The 12 were won by 1, 2, 11, 19, 20, 23, 41, 41, 42, 47, 53 and 62 segments. Most of the
  final length is fed in after round 400 (27 to 69 in the last hundred rounds, from 55 own units). A leader 6
  segments shorter at round 300 costs the two closest wins, 15 shorter costs three. In 9 of the 12 we also had 56
  units at round 200, so the early-feeding rule (`FEED_CAP_ROUND 200`, 56 units) was feeding that leader from round
  200; B's change list moves that rule to round 300 as well, or ties the leader rules to it, and the two options
  differ by exactly this.
- **By fit** (`x_race3.py`, `x_out/race3.txt`). A fit of win on the two ratios (total length, longest dragon) over
  our 65 both-dead big-map games gives the longest dragon a weight; the same fit over every team in the data gives it
  none at round 300 and a small one at round 400. Priced on our 65 games: total length +15% with the leader as it is
  now, +2 to +3 wins; with the leader halfway to what it is on the smaller maps, 0 to +2; with the leader as short
  as there, **-5 to +2**. For +25%: +3 to +5, +1 to +4, -4 to +4.

B's +1.8 to +6.0 wins is the first of those three cases: it re-scores the games with "our own win rate for the band
they land in", and those rates were earned with the leader the switch builds.

**The reverse experiment is already in our games.** On maps of 1,200 cells or fewer the rules start at round 300,
which is what this candidate asks for everywhere. There, in round-500 games with both queens dead and total length
level at round 400, we win 9 of 30 and the top three 22 of 40; our longest dragon is 5, 12 and 28 long at rounds
300, 400 and the end, the enemy's 7, 16 and 39. On the big maps at level length we won 4 of 6 with a leader of 27,
46 and 58. Small numbers, different maps; but it is the only place where the proposed setting can be seen at work,
and it does not look like the better one for the end game.

#### D. Sample size

- The behaviour: 16,000 to 28,000 turns a cell. Not in doubt.
- The games: 111 big-map games (77 live), 12 wins (9 live). Any statement about wins on these maps rests on 12
  games, B's and mine alike. Six of the 12 wins are on Around UNSW, five on Slithery Fight, one on Australia.
- It acts on 5 of the 15 known maps. What share of the qualifier's maps is over 1,200 cells is not known.
- By opponent the fall is the same (it is our own clock).

#### E. Cross-team

Nobody else stops eating. But the three top teams also end up with a leader: 9 to 19 between rounds 150 and 300 on
big maps, with 59 units and total length up 25%. They get both; we get the leader and lose the growth. So the lesson
from them is not "no leader until round 300" but "a leader that does not cost the small dragons their pearls".
forgot is the cleanest case: its small dragons eat 93 to 94% of such pearls in every phase and its longest dragon is
still 18 long at round 300.

#### F. Earlier experiments

- The same change ("GB300"), three local runs: 30 wins of 64 against 20 on one big map on a build with a known bug;
  46 of 96 against 48, with the one big map in the set at +2 -5; 73 of 152 against 76. Flat.
- The switch at round 200 on every map ("LC200", later on big maps, earlier on small): 52 of 96 against 48 locally,
  then 19 of 60 online against dev test 1 where the base had 23 and the feed-earlier build 24. Inside the noise,
  on the old map pool. The team's note then: an early leader is "easy to snipe on open maps"; it rejected the early
  leader on small maps and kept round 150 on big ones.
- Card #14 (a unit count instead of the round for the split stop): no local change.
- Do they contradict the candidate? No. Do they support it? No. Local games between two copies of our bot cannot
  show a rule whose cost is paid to an opponent that eats what we leave.

#### G. Backfire

Counted above: 2 or 3 of our 12 big-map wins sit within the margin the leader could lose; with B's first option for
the early-feeding rule (move it to round 300) all 9 wins that had 56 units at round 200 lose a hundred rounds of
feeding. Against that, the 53 big-map losses with both queens dead were lost by a median of 48 segments (26 against
74), so a little more economy does not turn many of them.

#### H. The code claim

Read: the constructor, `is_leader()`, `refresh_leader_zone()`, `in_leader_pearl_zone()`, `score_step()`,
`survey_from()`, `split_child_size()`, `feeding_phase()`, `hear_exact()`, `hear_sighting()`.

- B's description is right. `grow_round` is 300 on maps of 1,200 cells or fewer and 150 above, `LC_LEAD_ROUND`
  overrides it, and it is read in the three places named. After it, a pearl within 9 cells (Manhattan) of the
  longest own dragon a dragon knows of loses `EAT_BONUS`, costs `ZONE_PEARL_PENALTY 600` and is not a target; any
  dragon longer than 4 stops splitting; a dragon that knows no longer one is "leader" and stops trading and
  harvesting.
- "The longest own dragon it knows of" can be one segment longer than itself, which is why 2-longs and 3-longs stop
  eating next to 3- and 4-longs (54% with a 3-4-long as the nearest longer dragon). That is the part of the rule
  that looks like a bug, and it could be fixed without moving the round: a leader zone only around a dragon of, say,
  8 or more. I did not count what that would do.
- The `FEED_CAP_ROUND` point is real, and it matters more than B's one sentence gives it (item C).
- No map name is left in it. After the change `grow_round` has no map-size condition.

#### What is left of the claim

| | B | after the attacks |
|---|---|---|
| the behaviour | 83% to 58% at our switch, nobody else | the same, to the turn |
| total length at round 300 on big maps | +12 to +24% (inferred) | possible in the half of the games in which we have a full team; unknown in the other half |
| wins | +1.8 to +6.0 of 401 | -5 to +5: the low half if the later leader loses the longest-dragon race it now wins |
| points | +0.4 to +1.5 | **-1.2 to +1.3; cannot be told** |
| "the one that could most safely ride along with another card" | | no: it is the one candidate whose sign I cannot give |

### Candidate 4: do not give way at contact

**The claim (B's):** a dragon of 4 or shorter that sees at least as many heads of its own team as enemy heads ("not
outnumbered") rams any enemy dragon of 4 or shorter whose head it can reach this turn, longer, equal or shorter;
alone or outnumbered it rams only a longer one. On every map; today the trade rule all but forbids such rams on maps
over 1,200 cells. B: 0 to +2.4 points, single figure +1, and "it needs candidate 3".

**The strongest argument against it, as its opponent would put it.** "The only part of this that has been on the
ladder did everything it promised except win. The trade-on-contact build rammed three times as often, gained six
times as many segments from its rams, had a fifth more length and a longer leader at round 300, and won 0 of 12 on
the maps it changes and 6 of 30 in all, against 9.2. The two parts that have not been tried are exactly the two
kinds of ram on which we lose segments today, because our dragons do not eat what a ram leaves: the top three's team
eats 80% of the pearls of a ram it starts with friends near, ours 68%; alone, 45% against 27%. The rule copies when
they ram, not what they do afterwards. And among the top three themselves, on these maps, the side that rams more
does not win more."

What is left: every count is right, and B's own range already starts at zero. I would put it at **-0.5 to +1.5
points, cannot be told**, with the tested third worth nothing visible so far and the untested two thirds more likely
to cost than to pay until our dragons collect what a ram leaves.

#### A. The counts

`x_c34.py`; tables `x_c4a.py` (`x_out/c4a.txt`). A chance is one (turn, target) pair: a non-queen dragon of 4 or
shorter starts its turn with the head of an enemy non-queen dragon of 4 or shorter in its view and a path of free
cells to it within its reach. Share that ends in its ram, enemy head on the next cell / 2-3 steps away, maps over
1,200 cells:

| | meow live: B, mine | tc30 build: B, mine | our opponents: B, mine | top three, mine (B's three columns agree within 7 points) |
|---|---|---|---|---|
| not outnumbered, enemy longer | 16 / 12, 16 / 11 | 87 / 58, 87 / 58 | 91 / 83, 91 / 82 | 95 / 86 |
| not outnumbered, enemy same length | 15 / 9, 15 / 9 | 87 / 66, 87 / 66 | 72 / 55, 71 / 54 | 92 / 72 |
| not outnumbered, enemy shorter | 2 / 0, 2 / 0 | 3 / 0, 3 / 0 | 48 / 29, 48 / 29 | 69 / 45 |
| alone or outnumbered, enemy longer | 3 / 0, 3 / 0 | 4 / 0, 4 / 0 | 46 / 42, 46 / 41 | 55 / 38 |
| alone or outnumbered, enemy same length | 3 / 0, 3 / 0 | 5 / 0, 5 / 0 | 12 / 5, 12 / 4 | 13 / 7 |
| alone or outnumbered, enemy shorter | 3 / 0, 3 / 0 | 3 / 0, 2 / 0 | 10 / 2, 9 / 2 | 7 / 2 |

On maps of 1,200 cells or fewer the live bot is at 87 / 82 and 88 / 76 for the first two rows, like everybody, and
at 11 / 0 for the rest (B: 88 / 82, 89 / 76, 11 / 0). Rams started per game and the swing per ram (pearls of both
corpses eaten by the starter's team minus its dragon's length, minus the same for the other team), big maps:

| | meow live | tc30 build | our opponents | top three |
|---|---|---|---|---|
| all rams it starts: number per game x swing = segments (B) | 8.6 x 0.52 = +4.5 | 29 x 1.19 = +34 | 52 x 1.77 = +92 | 65 x 1.15 = +75 |
| the same, mine | 10.0 x 0.58 = +6 | 31.0 x 1.15 = +36 | 52.7 x 1.82 = +96 | 65.2 x 1.24 = +81 |
| not outnumbered, victim longer / same / shorter: swing | +2.4 / +1.1 / -0.7 | +2.9 / +1.0 / (4 rams) | +3.5 / +2.3 / +1.3 | +2.8 / +1.7 / +1.0 |
| alone or outnumbered, victim longer / same / shorter: swing | -0.7 / -1.0 / -2.1 | -0.4 / -0.6 / -3.3 | +1.5 / +0.8 / 0.0 | +0.5 / -0.1 / -1.1 |
| share of both corpses' pearls its team eats: not outnumbered / alone | 68% / 27% | 70% / 29% | 86% / 60% | 80% / 45% |

**Everything reproduces.** B's reading of the head count is right too: the top teams do not "ram alone", and the
head count separates what they do very sharply (92% against 13% for an equal enemy on the next cell).

By eye (`x_pick34.py`, `x_out/c4_eye.txt`): 16 turns of the live bot on big maps with an equal or longer small enemy
head on the next cell and at least as many own heads as enemy heads in view. In all 16 the dragon steps away or past;
in 1052760 round 284 a 2-long of ours has a 2-long enemy head directly north, four own heads and no other enemy in
view, and steps west.

#### B. Cause or consequence

- Among the top three on big maps the number of rams a side starts does not go with winning: 63.9 a game in wins,
  66.9 in losses (B: 64 and 67), swing +1.28 and +1.18. On the smaller maps it does for everybody (top three 15.7
  against 12.6, swing +1.37 against +0.61; we 13.8 against 6.2): there the side that is winning has the numbers at
  the meeting. So "they ram more" is what a team with dragons to spare does, and on big maps, where everyone has 55
  to 60 units, it separates nobody.
- For us on big maps it does separate (15.8 rams a game in the 9 wins, 9.2 in the 68 losses). Nine games.
- The comparison that would remove the confounder is the trial itself: same bot, one rule changed (item C).

#### C. What happens next: the trial

The trade-on-contact build (tc30) took the map-size condition off the first two rows of the table and nothing else.
Its 12 big-map games against the live bot's 77 (`x_c4a.py` part 4, `x_c3stall.py`), means, ours against the enemy's:

| | live bot | tc30 build |
|---|---|---|
| chances taken (all six rows together) | 3% of 16,877 | 15% of 2,162 |
| rams it starts per game, swing per ram | 10.0, +0.58 | 31.0, +1.15 |
| rams the enemy starts per game, swing per ram | 52.4, +1.82 | 56.3, +1.70 |
| units at round 150 / 300 | 47 : 60 / 36 : 62 | 52 : 58 / 42 : 59 |
| total length at round 150 / 300 | 123 : 209 / 122 : 327 | 143 : 191 / 147 : 291 |
| longest dragon at round 300 / 400 | 14 / 19 | 19 / 22 |
| how the games ended | 9 won on the longest dragon, 34 lost on it, 23 lost with her queen alive and ours dead, 11 wiped out | 6 lost on the longest dragon, 6 lost with her queen alive and ours dead |

So the rule did what it says, the economy moved as the swing count predicts, the leader was longer, and it won none.
Twelve games against a base rate of 12% is weak: no win in 12 happens by chance about one time in five. But look at
how they were lost. Six of the 12 are games no economy rule can win (our queen dead, hers alive). The other six
were lost on the longest dragon with 147 total length against 291: a fifth more length does not reach a side that
has twice ours. On B's own band table a move from 122 to 147 against about 300 stays inside the lowest band, where
we win 7%.

**Why did the economy not turn into wins, and does the candidate avoid that?** It does not. What stayed the same in
the trial is the enemy's side of the exchange: they still started 56 rams a game at +1.70 each, about 96 segments a
game against our 36. The candidate's two new parts aim at that (ram shorter enemies before they ram us; ram a longer
one when alone), and those are the two rows where our own rams lose segments today (-0.7 and -0.7), because our
team eats 68% of the pearls where a top team eats 80%, and 27% where it eats 45%. A3 measured the same thing from the
other side: a natural pearl at equal distance from one of our heads and an enemy head goes to us 35% of the time,
to the top three 46 to 50% (`deep-read-3.md`). Until that changes, more rams are more even trades followed by an
uneven meal.

The other build that raised our economy tells the same story: "stride" (free sprint steps) gained 14% locally and
won 6 of 30 online where its paired live half won 8 (`safer-stride-test-result.txt`).

**"It needs candidate 3."** B's evidence is two games (1068050 and 1068051: 60 units against 33 and 39 at round
150, behind in total length by rounds 249 and 213). Both are in my files as B describes them. Two games, and the
same build's leader was longer than the live bot's, not shorter; I would not build a dependency on that.

#### D. Sample size

- The behaviour counts: thousands of chances a cell. Not in doubt.
- Swing for the rams we do not make: 31 and 34 rams of the live bot in 77 games in the two rows the candidate adds
  (0.4 a game each). "-0.7" is a number on thirty rams.
- The trial: 12 games on the maps it changes, 30 in all. It cannot carry a verdict either way.
- Nine tenths of it acts on maps over 1,200 cells, 5 of the 15 known maps, where we win 12 of 111.
- By opponent: both of our usual opponents do it to us (test4 and WeHaveQuizzes start 52 rams a game against our 10).

#### E. Cross-team

All three top teams and both of our usual opponents do all of it. There is no 2000+ team in the data that gives
way at contact as we do on big maps and does well. As behaviour to copy it is the best supported of the four; what
is missing is the part of the behaviour that makes it pay.

#### F. Earlier experiments

- Online: tc30, above. 6 wins of 30 against a pooled 9.2; 0 of 12 on big maps.
- Local (`work/plan.md`): equal trades on every map ("TRADE_EVEN") and its variants were run against the release
  with no gain recorded; dropping the head count against a rushing copy of our bot won 60 of 118 where the base won
  68. The second agrees with B's reading (do not ram alone). Neither tests the candidate as written.
- Local games cannot show it: two copies of a bot that steps away never meet like this.

#### G. Backfire

- **More rams while alone.** The candidate adds "alone or outnumbered, ram a longer one". The top three gain +0.5 a
  ram on that row on big maps (SSS -0.1), our opponents +1.5, we -0.7 on 34 rams. It would add about 5 rams a game.
- **Fearless small dragons.** In `score_step()` a dragon that has a marked trade target loses its whole fear of
  enemy heads, not only of the target, and is pulled towards the target from many cells away (`TRADE_REWARD 2500`
  minus 80 a step). Marking shorter enemies whenever we are not outnumbered makes most of our small dragons near an
  enemy "traders" in that sense. On the smaller maps that is already so for equal and longer targets and we hold our
  own there; on big maps it is new.
- **The smaller maps.** 131 of our games there end by wipe-out before round 300 and we win 61 of them. The candidate
  adds about 4 rams a game there, in the rows with the worst swing. I cannot count what that does to those fights.
- **Wipe-outs on big maps** did not rise in the trial (0 of 12 against 11 of 77).

#### H. The code claim

Read: `mark_trade_targets()`, `is_trader()`, `ram_path()`, `guards_big_ally()`, `score_step()`, `pick_direction()`.

- B's description of today's rule is right: `round <= feed_round`, a unit minimum (8, or 1 on maps of 1,200 cells
  or fewer), the head count (`ally heads + 1 - enemy heads >= 1`), and a target that shows at least the attacker's
  length (at least `max(5, length + 2)` on larger maps). One thing B leaves out: at the unit cap (59 or more own
  dragons) the big-map rule already drops to "at least the own length", so in our best openings the live bot trades
  evenly on big maps as well.
- The length test uses `visible_parts`, the segments of the target inside the attacker's view, so "longer, equal,
  shorter" in the code is not always what the replay shows.
- `ram_path()`: the step limit B wants to unify (3 on small maps, 4 on big) cannot bind, because a dragon of 4 or
  shorter reaches at most 3. No change needed there.
- No map name; with `aggressive` taken out of both tests there is no map-size condition left in the trade rule. The
  switch `TRADE_EVEN` exists for the tested third only, as B says.

#### What is left of the claim

| | B | after the attacks |
|---|---|---|
| the behaviour gap | on big maps we ram 15% / 2% where they ram 90% / 60 to 80% | the same |
| what the tested third did | rams x3, +21% length at round 300, 0 wins of 12 | the same; half of those 12 were lost with her queen alive, the other half at half the enemy's length |
| the untested two thirds | "between nothing and another +25 segments" | negative swing for us today on the rows it adds (30-odd rams each); positive only if our team also learns to eat after a ram |
| points | 0 to +2.4, single figure +1 | **-0.5 to +1.5; cannot be told** |
| "needs candidate 3" | two games | two games |

### All candidates, attack I: the footing, and what B did not propose

#### The footing itself

B puts every candidate on "points of win rate" from two kinds of what-if (strict, realistic) and from win rates per
economy band at round 300. I recounted the tables (`x_foot.py`, `x_out/foot.txt`; `x_c1e.py`): the end-state table
and the band table reproduce exactly (12 of 168, 16 of 61, 6 of 12, 17 of 27; +33.9 and +60.8 wins). Four things are
wrong with leaning on it.

1. **It leaves out a third of our games and more than half of our wins.** 133 of our 401 games are over before round
   300, all but two on maps of 1,200 cells or fewer, and we win 61 of them (46%). In the 268 games that reach round
   300 we win 51 (19%). So against teams rated 2000+ we are close to level in the short fights on the smaller maps
   and far behind in every game that goes long. None of B's numbers sees the first kind of game, and two candidates
   act in it (candidate 2 changes what our queen does on small maps; candidate 4 adds trades).
2. **"The economy is the larger gap" is not safe to say.** The economy what-if (our win rate per band with the top
   three's mix of bands, +60.8 wins) takes 93 of its 112 wins from our two upper bands, which hold 12 and 27 games.
   With the 80% ranges of those two rates it is +32 to +90 wins. The conversion what-if (their rates, our mix) is
   +25 to +44. The two ranges overlap, and the two effects multiply rather than add.
3. **The band rates are not a property of the band.** The "realistic" readings re-score a changed game with "our own
   win rate for the band it lands in". But those rates were earned with the bot as it is. Two examples from this
   file: in the lowest band our record with both queens dead depends on when her queen died (0 of 49 before round
   300, 4 of 23 after; candidate 1); and on maps over 1,200 cells our rate inside a band was earned with a leader
   that starts at round 150, which is the thing candidate 3 removes.
4. **The ranking is by confidence and cost, not by points.** All four ranges lie between 0 and +3 points and overlap.
   That is a fair way to rank, but it should be said that way: the table does not show that candidate 1 is worth more
   than candidate 3 or 4, only that it is surer and cheaper.

A different footing that I find more useful, how our 401 games end (`x_foot.py`):

| How it ended | games | won | on maps over 1,200 cells | on smaller maps |
|---|---|---|---|---|
| wipe-out before round 300 | 133 | 61 | 0 of 2 | 61 of 131 |
| wipe-out from round 300 on | 37 | 6 | 0 of 11 | 6 of 26 |
| round 500, both queens dead (longest dragon decides) | 143 | 41 | 12 of 65 | 29 of 78 |
| round 500, our queen dead, hers alive | 73 | 0 | 0 of 33 | 0 of 40 |
| round 500, both alive | 14 | 3 | none | 3 of 14 |
| round 500, ours alive, hers dead | 1 | 1 | none | 1 of 1 |

On it, candidate 1 works on the fourth row (73 certain losses, which become longest-dragon games), candidate 2 on
the third and fourth (a living queen wins the third outright), candidates 3 and 4 on which row a big-map game lands
in. Nothing proposed works on the third row as it is, and that is where the next item sits.

#### Dismissed too quickly: the longest-dragon race

B drops "start feeding earlier" because it was tried (three trials, neutral) and because "the ceiling is small once
the economy is held fixed" (+6.9 wins). I recounted the race by total length at round 400 and by map class
(`x_race.py`, `x_race2.py`; outputs `x_out/race.txt`, `x_out/race2.txt`). Round-500 games with both queens dead:

| Maps of 1,200 cells or fewer; own / enemy total length at round 400 | meow: won | our longest at round 300 / 400 / end against the enemy's | top three: won | their longest at 300 / 400 / end against the enemy's |
|---|---|---|---|---|
| 0.8 to 1.25 (level) | 9 of 30 = 30% | 5 / 12 / 28 against 7 / 16 / 39 | 22 of 40 = 55% | 7 / 21 / 46 against 7 / 18 / 42 |
| over 1.25 (ahead) | 15 of 18 = 83% | 4 / 13 / 36 against 4 / 12 / 18 | 77 of 83 = 93% | 6 / 15 / 39 against 4 / 5 / 13 |

| Maps over 1,200 cells | meow: won | our longest at 300 / 400 / end against the enemy's | top three: won | theirs |
|---|---|---|---|---|
| 0.5 to 0.8 (behind) | 6 of 23 = 26% | 19 / 25 / 51 against 20 / 38 / 52 | 17 of 49 = 35% | 12 / 35 / 41 against 15 / 35 / 59 |
| 0.8 to 1.25 (level) | 4 of 6 | 27 / 46 / 58 against 20 / 33 / 53 | 73 of 116 = 63% | 16 / 41 / 60 against 14 / 30 / 50 |

Two things follow.

- **On the smaller maps we lose level games on the longest dragon that the top three win.** With total length level
  at round 400 we win 30% and they win 55%; our leader is 12 long then and theirs 21, from the same 5 to 7 at round
  300. Over all maps, **14 of our losses came with at least as much total length as the enemy at round 400**
  (`x_out/race.txt` lists them: five on Maze, five on Portals, three on weakhold, one on Slithery Fight; for instance
  1027819, total 136 against 131, longest 13 against 58). At the top three's rates for games at 0.8 or better we
  would win about 40 of those 55 games instead of 29: **+10 wins, 2.7 points**. That ceiling is larger than what I
  would defend for any of the four candidates, B's pick included. It is a ceiling and not a rule: the direct trials
  (feeding from round 330 or 300) were neutral, the online one on an older bot and the old map pool. But "the
  ceiling is small" is not a reason to drop it; +6.9 wins, B's own figure, is as much as B claims for candidate 1.
- **On the big maps the picture is the reverse, and it bears on candidate 3**: there our leader is as long as a top
  team's at the same economy and we convert as well as they do (see candidate 3).

#### The other dismissed items

- **Team-mates off the queen's last exit, the queen rules on every map, dead ends:** I have nothing to add to B;
  each was tried in some form and lost or did nothing.
- **"Keep the queen near her team" / defenders near the queen.** B says where she lives is not what differs. That
  holds in my count as far as it can be tested (candidate 2, items B and C): once an enemy head is within 3 steps
  of a 2-3-long queen, the number of own heads near her does not lower her risk for any team, and for ours it goes
  with a higher one.
- **Hunters that walk to her (the dropped half of the first run's H1).** B's reason stands and the second online
  trial confirms it: qh31b's hunters raised rams on her queen from 8 to 13 games of 28 and the end state did not
  move.

## 3. The pair 1 + 2, and the pair 3 + 4

### Candidates 1 and 2 together

B says they are "two sides of one idea" and worth +3.1 to +5.3 points together, more than the two alone. I recounted
each sentence of that case (`x_c2c.py` part 3, `x_c1e.py`, `x_pair.py`; outputs `x_out/c2c.txt`, `x_out/pair.txt`).

| B's sentence | B | mine | holds? |
|---|---|---|---|
| Both queens end a turn inside a visible enemy reach equally often (per 1,000 queen-rounds) | 5.4 and 5.4 | ours 5.2, theirs 4.5 | roughly. By opponent it is two different things: test4's queen 3.0 against our 4.5; WeHaveQuizzes's 7.1 against our 5.2 |
| They ram on such a turn, we do not | 71% and 16% | 76% and 19% | yes |
| "Our queen alive, hers dead at round 500": games | 1 of 401; 177 of 1,637 for the top three | 1; 178 | yes |
| Round-500 losses in which both rules have something to change | 10 | 11 (25 with a candidate-1 event, 63 with a candidate-2 event) | yes |
| Strict flips: 1 alone, 2 alone, together | 6 to 13, 34, 49 to 54 | 6 to 13, 36, 51 to 56 | yes, as arithmetic |
| Realistic wins together | 12.3 to 21.4 | 17 to 31 with my cruder survival curves; **about 6 to 10 with what was measured** | the arithmetic yes, the inputs no |

The joint number is sound as a sum and unsound in what goes into it. Three inputs carry it:

1. **How long a saved queen lives.** B's two readings bracket "at our own other death rates" and "like a top-three
   queen". The replays answer it directly: our queen, after taking the safe step in the same situation, is alive at
   the end of the game in 6 to 9% of cases (candidate 2, items B and C). That puts candidate 2 at about 2 to 3
   games, below B's bracket.
2. **What a dead enemy queen is worth.** About 6 games by reading the 25 games one by one (candidate 1, item C).
3. **The extra from doing both.** It comes from the 11 losses in which our queen would be saved and hers killed. It
   needs our queen alive at round 500, so it is 11 times that same 6 to 9%, about one game; B's +1.8 and my +1.7 to
   +4.3 use the survival curves again.

So together: **about 6 + 2 or 3 + 1 = 9 or 10 games if everything holds, 5 to 8 more likely, which is +1.2 to +2.5
points; not +3.1 to +5.3.** The upper half of B's range is the assumption that our queen will live like a top-three
queen once she stops stepping into reach, and nothing measured supports that.

"Two sides of one idea" is a fair description of the state both aim at. As work for the team they are two cards
(B says so too): a switch on the attackers that cannot hurt much, and new scoring for the queen that has an open
question on small maps. One real link between them, which B does not state: **against test4 candidate 2 is worth
almost nothing without candidate 1.** test4's queen is alive at the end of 45% of our games, so 13 of the 45
avoidable deaths of our queen against test4 are in round-500 losses with her queen alive, and a living 2-long queen
of ours still loses those on queen length; 7 are in losses with both dead. Against WeHaveQuizzes it is the other way
round (2 and 17).

### Candidates 3 and 4 together

B says candidate 4 "needs" candidate 3, because the trade-on-contact build led at round 150 in two big-map games and
was behind by rounds 213 and 249 "under the leader switch". The two-game story is true, and it is two games. Over
its 12 big-map games that build had more length than the live bot at round 300 (147 against 122) and a longer
leader (19 against 14), and it lost six of them with her queen alive and ours dead and six on the longest dragon at
half the enemy's length. Nothing in those games says that a later leader would have turned them. And the same
switch builds the leader that every one of our big-map wins was won with (candidate 3, item C). I would not treat
the two as one package.

## 4. If I had to pick

**Candidate 1, as B does. But as a small, safe card, not as the gap that explains us.** It is the one candidate
whose behaviour claim survived every recount, whose code claim is right, and for which I could not build a way to
lose more than a game or two in 400. Its honest size is about one point: 4 to 6 games in 401, not 7 or 8.

What I would tell the team with it:

- **Change the condition B names** (`real_queen()` in the first line of `mark_hunt_targets()`), and nothing else.
- **Do not limit it to short dragons "to be safe".** Three of the six games I count as flips need an attacker of 6
  or 8 segments, late, on a fed queen. Both online trials had the limit; that is one reason they show nothing.
- **Do not judge it by wins, and do not expect to see it.** In 60 + 60 games the chances taken will go from about a
  fifth to nearly all, and the win count will be whatever chance makes it. That is what happened twice already.

**The most likely way it disappoints:** exactly that. It works as coded, nothing visible follows, and after a
30-game pair the team concludes either "no effect" or, by luck, "it works". The second most likely: against test4,
whose queen walks a small loop at her spawn and is in our reach half as often as WeHaveQuizzes's, it finds few queens
to kill; and at the qualifier, against teams that out-grow us, the kills land in games in which a dead enemy queen
has never helped us.

**Where I think the lead should decide differently from B:**

1. **The size.** Candidate 1: about +1 point, not +1.5 to +2. The pair 1 + 2: +1.2 to +2.5, not +3.1 to +5.3.
2. **Candidate 2 is not ready as "second".** Its veto is worth about two games unless our queen also starts to live
   longer for other reasons; it needs a pearl-aware reach test that does not exist in the code yet; and its small-map
   half goes against the team's own local result. If it is built, I would build the veto for maps over 600 cells
   only, and add the two repairs that cost nothing on any map (shed instead of cut; the queen does not ram).
3. **Candidate 3 is not the one that "could most safely ride along".** Its behaviour claim is right and its sign in
   wins is unknown: it gives up part of the leader that every one of our big-map wins was won with, for an economy
   gain that is inferred. It should not ride along with anything.
4. **If the lead wants one "excellent" hypothesis and not a safe small one, none of the four is it.** The largest
   gap I could count that no candidate works on is the longest-dragon race on the smaller maps: with total length
   level at round 400 we win 30% of the games in which both queens are dead and the top three win 55%; 14 of our
   losses came with at least as much total length as the enemy. It has no rule yet that survived a trial, which is
   why it is not a candidate. It is where I would look next.
5. **No candidate can be judged by wins before the freeze.** B says this and I agree. It also means that the choice
   between the four rests on the recounts in these files, not on anything the team can still measure.

## 5. Corrections

Numbers and sentences in `hypotheses.md`, `findings.md` or the deep reads that my recount could not reproduce, or
that are right as counts and wrong as statements. Small differences that come only from the path test (strict
against the lead's) are in the tables of section 2 and not repeated here.

| Where | It says | I find | Why |
|---|---|---|---|
| `hypotheses.md`, candidate 1, trials | "`QUEEN_HUNT` was on in v54 and has been off since v55"; in the ranking: "one switch in the code that the team turned off itself" | As far as the log shows, the hunt has never been in a released bot. v54 had no queen mode at all, and the hunt exists only inside queen mode; it was tried locally twice (91 of 156 against 96; 59 of 120 against 60 and 57 against 58) and left off both times | `work/plan.md`: "QS0PH (+hunt) 91", "H4 ... REJECTED (no gain even vs the hunter spar)"; "off since v55" is the note of a later day and means "not on since queen mode exists" |
| `hypotheses.md`, candidate 1, trials | qh31 is the one online trial | A second one, qh31b, finished at 11:18 on 5 October (30 + 30 games against test4 and WeHaveQuizzes, 15 + 15 against dev test 1): rams on her queen 13 against 8 games of 28, wins 8 against 8; against dev test 1 4 against 1 and 1 against 3 | It is in `data/online/smoke/qh31b-*`, not in `games.csv` |
| `findings.md` section 3, and every "chance" count | A chance is a path of free cells no longer than the dragon's reach; "not in view: 1 of 214, 0 of 273 ..." | 284 of the 2,128 rams on a queen in the data (13%) used more steps than that reach, paid for by pearls eaten on the way; 266 of them started with her head in the attacker's view. Our opponents made 52 of their 251 rams on our queen this way | The reach grows by one for every pearl eaten during the move. The lead's file counts these as "kills without a chance", so "Vibing++ takes 266 of 267" is right for plain reach and leaves out 43 more of its kills |
| `hypotheses.md`, candidate 1, item 4c | the rule "acts at every state of the economy" (flips by band 5, 2, 2, 4) | The band count is right. But in the lowest band we won 0 of 49 both-queens-dead games in which her queen died before round 300 and 4 of 23 when she died later; over all teams a dead enemy queen changes the win rate there by -8 to +4 points | `x_c1c.py`, `x_c1g.py` |
| `hypotheses.md`, candidate 1, risks | dragons longer than 12 "would have had such a turn in 9 of the 401 games" (16 turns) | 21 untaken turns in 11 games | B caps the path at 12 steps, I at the dragon's own reach |
| `hypotheses.md`, candidate 1, table | "the attacker is its team's longest dragon: 8 of 117" (meow) | 18 of 181 | I count a dragon as longest when no own dragon is longer (ties included); early in a game many 3-longs are |
| `hypotheses.md`, candidate 2, item 4 | 128 deaths touched: 104 + 14 + 10; strict 34 | 140: 106 + 24 + 10; strict 36 | My "after a cut" is any death within 5 rounds of a cut, rams by an unseen enemy included |
| `hypotheses.md`, candidate 2, item 5 | the pieces to reuse "already compute exactly that" (every cell a visible enemy head can move into) | They compute plain reach from the parts of an enemy that are inside her view; pearl-paid steps and unseen segments are missing. With plain reach and true lengths 84 of the 106 deaths are visible | `stride_reach_map()`, `spread_kill()`; `x_c2a.py`, `x_c2vis.py` |
| `hypotheses.md`, candidate 2, cuts | "40 cuts, never the other" | 39 cuts, 29 of them in rounds 0 to 5 on Slithery Fight (the 25-long coiled start); WeHaveQuizzes makes the same cut there and its queen is not dead by round 100 in any of 12 games | `x_c2cut.py` |
| `hypotheses.md`, candidate 3, "wins against losses" | "Our wins there are the games in which the economy held, not games in which an early leader was built at its cost" | In 10 of our 12 big-map wins the enemy had more total length at round 300 (medians 207 against 302); our longest dragon was the longer one at round 300 in 7 and grew from 7 at round 150 to 24 at round 300 | `x_c3wins.py`, `x_race2.py` |
| `hypotheses.md`, candidate 3, item 4 | on the other maps "our growth from round 150 to 300 is half of the top three's and of our opponents' in relative terms (20% against 41% and 47%)" | On the same games throughout (those that reach round 400): ours +24%, our opponents' +29%, the top three's +27% | B's means are over the games that reach each round, a different set at 150 and at 300; `x_c3stall.py` |
| `hypotheses.md`, candidate 3, item 4 | +1.8 to +6.0 wins from +15 to +25% total length, re-scored with "our own win rate for the band" | -5 to +5: the band rates on these maps were earned with the leader the switch builds; priced with a fit that also counts the longest dragon the range opens downwards | `x_race3.py` |
| `hypotheses.md`, candidate 4, item 5 | on larger maps a target must show `max(5, length + 2)` parts; `ram_path()` needs one step limit instead of two | At the unit cap (59 or more own dragons) the big-map rule already drops to "at least the own length". The two step limits (3 and 4) cannot bind: a dragon of 4 or shorter reaches at most 3 | `mark_trade_targets()` (`at_cap`), `ram_path()` |
| `hypotheses.md`, "Not proposed", feeding earlier | "the ceiling is small once the economy is held fixed" (+6.9 wins) | By total length at round 400: at 0.8 or better we win 29 of 55 both-dead games and the top three 239 of 331; at their rate +10 wins. On maps of 1,200 cells or fewer and level length: 30% against 55% | `x_race.py`, `x_race2.py` |
| `hypotheses.md`, footing | "the economy is the larger gap (61 wins of 268), the conversion ... the smaller (34 wins)" | +32 to +90 against +25 to +44 once the 80% ranges of the band rates are carried through; 93 of the 112 "economy" wins rest on bands with 12 and 27 games. 133 of our 401 games (61 of our 112 wins) are over before round 300 and are in neither number | `x_foot.py` |
| `hypotheses.md`, pair | "both queens end such a turn equally often (5.4 ... each)" | ours 5.2, theirs 4.5 per 1,000 queen-rounds; test4's queen 3.0, WeHaveQuizzes's 7.1 | `x_c2c.py` part 3 |

## 6. What I could not determine

1. **What any of the four rules does in a real game.** I ran none. Every size in this file is arithmetic on games
   that were played, or a comparison inside them that still leaves the winning side looking better.
2. **Whether a kill of her queen causes the win or comes with it.** The comparisons that hold the economy, the round,
   our own queen and the local head count fixed leave +2 to +9 points on the games concerned, with a range that
   includes zero. Only games with the switch on can narrow it, and it takes about 300 a side on the end state to see
   it.
3. **Why our own queen died earlier in all three hunt runs** (40 pairs earlier against 24 later). Two runs of the
   same bot differ as much, so I cannot call it an effect; I cannot rule it out either.
4. **How a veto built from the bot's existing pieces behaves.** I counted what those pieces would see on the turns
   of played games (`x_c2vis.py`); what the queen then does on the next turn, and the turn after, is not in a replay.
5. **Which part of the queen rules cost local wins on small maps.** The log gives the totals (16 to 13 and 11 to 7)
   and says it was not the trading. Candidate 2 switches on the threat map and the trade ban there and leaves the
   portal ban off; nobody has played that mix.
6. **Whether the leader built from round 150 wins our big-map games or only comes with them.** Among all teams the
   longest dragon at round 300 has no weight in who wins a both-queens-dead game once total length is counted; in our
   own 65 such games it has. With 12 wins I cannot tell which is the truth for us.
7. **How much length the round-150 switch costs.** In our big-map games with a full team at round 150 our total
   length still grows 13% to round 300 (the top three 25%, our opponents in those games 39%); in the others we
   collapse whatever the rule. B's +12 to +24% is possible for the first half and unknown for the second.
8. **Whether "feed the longest dragon earlier" would close the gap on the smaller maps.** The gap is measured (30%
   against 55% at level total length). The trials of the simple version were neutral, on an older bot and map pool.
9. **Anything against the three top teams.** We have 21 games against them. The opening exists (their queens offer
   in-view chances as often as test4's and WeHaveQuizzes's); what a kill is then worth to us, I cannot count.
10. **What the qualifier maps are like.** Candidate 3 and nine tenths of candidate 4 act only on maps over 1,200
    cells (5 of the 15 known maps); the shed-not-cut part of candidate 2 is worth most where a queen starts long and
    coiled (one known map). None of this can be said of maps nobody has seen.
11. **Which build played each ladder game.** As B: the two ladder downloads are "the live bot of that hour".
12. **Whether the opponents will change.** test4 and WeHaveQuizzes are the opponents in 313 of our 401 games; the
    numbers for candidates 1 and 2 are, to a large part, numbers about those two bots as they were this week.

## 7. Counts I made

All scripts are in this directory and are my own; they use `lib.py` (the replay walker), `games.csv` and the smoke
folders, and none plays a game. Outputs are in `x_out/`. Filter unless said: opponents rated 2000 or more, map
Schooltime left out. I read the other sub-sessions' scripts only to find out what they counted.

**Walks of the replays**

| Script | What it counts | Output |
|---|---|---|
| `x_games.py` | My game list: the 2,343 games of `games.csv` plus 135 smoke-test games that are not in it (qh31b old and new against test4, WeHaveQuizzes and dev test 1; qn23) | `x_out/games.json` |
| `x_c1.py` | All 2,478 replays, both sides. Every turn of a non-queen dragon with the enemy queen's head in its view or in Manhattan reach: three path tests (strict, strict inside the own view, walls only), head counts in view, both teams' units and lengths at that moment, what the dragon did, whether it rammed her, what became of it. Every queen death with its killer. A timeline every 10 rounds. The final board | `x_out/c1/<game>.json` |
| `x_c2.py` | All 2,478 replays, both queens. Every queen turn with an enemy head in her view or near: the four one-step moves and whether each is in an enemy's reach (plain reach and pearl-paid reach; enemies in view and all), the room behind each, where she really ended and whether that was in reach on the real board, her death and its killer; every queen split; queen-rounds; whether she could reach the enemy queen | `x_out/c2/<game>.json` |
| `x_c34.py` | All 2,478 replays, both sides. Candidate 3: a free pearl on the next cell taken or not (dragon of 2-4, no enemy head in view, a way on), by 10-round block, own length, distance to the nearest longer own dragon and its length; splits and dragon-turns by length class; pearls eaten by class. Candidate 4: every turn on which a dragon of 4 or shorter can reach a small enemy head, by head count, relative length and distance, rammed or not; every ram between two small dragons with who ate the pearls of both corpses | `x_out/c34/<game>.json` |
| `x_c2vis.py`, `x_c2vis2.py` | Our 401 games: for every turn of our queen with an enemy head in view, which one-step moves are "in reach" under four models (the bot's existing pieces: visible parts, no pearls; the same plus one segment; true length; true length with pearl-paid steps) | `x_out/c2vis.json`, `x_out/c2vis.txt` |
| `x_c1p.py` | Our 401 games, both sides: in-view chances on a queen that exist only through a pearl-paid step, taken or not | `x_out/c1p.txt` |
| `x_eye.py`, `x_c1pick.py`, `x_c2pick.py`, `x_pick34.py` | Draws the board at the start of one dragon's own turn; picks the turns looked at by eye for each candidate | `x_out/c1_eye.txt`, `x_out/c2_eye.txt`, `x_out/c3_eye.txt`, `x_out/c4_eye.txt` |

**Tables**

| Script | What it counts | Output |
|---|---|---|
| `x_c1a.py` | The chance table against B's: by team, attacker length, round, own queen, paid steps, head count, queen length; games with a chance and no ram; queen ids | `x_out/c1a.txt` |
| `x_c1far.py` | Rams on a queen that no plain-reach chance explains: 284 of 2,128 are moves longer than the plain reach | `x_out/c1far.txt` |
| `x_c1b.py`, `x_c1b2.py`, `x_logit.py` | Take-up per team against rating over all teams; the first chance of each game taken or not, inside the same team, economy band and own-queen state; logistic fits holding economy, round, own queen, team and the local head count fixed | `x_out/c1b.txt`, `x_out/c1b2.txt` |
| `x_c1c.py` | Win rate by state (round, economy band, own queen, her queen) for us, the top three and all 2000+ teams; how games ended after real rams against the same state with her alive; what a team builds after its queen dies; rams by a team's own longest dragon | `x_out/c1c.txt` |
| `x_c1d.py` | Our 401 games by what happened at the first chance; B's 25 candidate games one by one with the lenient and hard readings recomputed; where they sit by opponent, map and run; our take-up by opponent; how often each team's queen offers a chance and to whom | `x_out/c1d.txt` |
| `x_c1e.py` | Round-500 end states by queen state per team (check of B's footing table) | `x_out/c1e.txt` |
| `x_c1f.py`, `x_c1pairs.py` | Every run of ours recounted from its replays (qh31, qh31b, stride, passage2, tc30, qn23, ladder): wins, chances taken, rams on her queen, end states, our queen; old/new pairs by opponent and map; our queen's death round in each pair | `x_out/c1f.txt`, `x_out/c1pairs.txt` |
| `x_c1g.py` | Backfire of candidate 1: our wins in which the rule would have fired and whether they stand without the attacker; untaken chances by attacker (our longest, 10+, 13+, outnumbered); what the rule would spend; both-dead games by when her queen died | `x_out/c1g.txt` |
| `x_c2a.py` | The queen table against A4's and B's, under the pearl-paid and the plain reach model: turns in reach by choice, how each queen ended, cuts and sheds | `x_out/c2a.txt` |
| `x_c2b.py` | The same situation by what she did (fate that round, within 10 and 50 rounds, at the end); our queen's survival from each round; the deaths each part of candidate 2 touches and what they are worth; the turns the rule would change; her own rams | `x_out/c2b.txt` |
| `x_c2c.py`, `x_c2cut.py` | What follows a cut and a shed, per team; ram risk by own heads near the queen; the mirror (turns in reach, punished or not) per opponent; our cuts one by one and the coiled start on Slithery Fight | `x_out/c2c.txt`, `x_out/c2cut.txt` |
| `x_pair.py` | Candidates 1 and 2 alone and together on our round-500 losses, strict and realistic | `x_out/pair.txt` |
| `x_c3a.py`, `x_c3stall.py`, `x_c3wins.py` | The pearl-taking rate by map class, team and round, around both switch rounds, by distance to a longer own dragon; the same in wins, losses and economy bands; splits; units, total length and longest dragon on the same games through the switch; our 12 big-map wins one by one | `x_out/c3a.txt`, `x_out/c3stall.txt`, `x_out/c3wins.txt` |
| `x_race.py`, `x_race2.py`, `x_race3.py` | Round-500 games with both queens dead: win rate by total length at round 400 and map class, the longest dragon of both sides at rounds 150 to the end; logistic fits of win on total length and longest dragon at rounds 300 and 400; candidate 3's trade priced with those fits | `x_out/race.txt`, `x_out/race2.txt`, `x_out/race3.txt` |
| `x_c4a.py` | Ram chances on small enemy heads taken, by head count, relative length and distance; rams started per game and the swing per ram; wins against losses; the trade-on-contact build against the live bot on big maps | `x_out/c4a.txt` |
| `x_foot.py`, `x_small.py` | B's band table with 80% ranges; the two what-ifs with ranges; how our games end, by map size | `x_out/foot.txt`, `x_out/small.txt` |
| `x_load.py`, `x_show.py`, `x_build.py`, `x_mdcheck.py`, `x_peek.py` | Shared loader; prints one per-game file; assembles this file from `x_p*.md`; checks its tables and file names; a first look at `games.csv` | |
