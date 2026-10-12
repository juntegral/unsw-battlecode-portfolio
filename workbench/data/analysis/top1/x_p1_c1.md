## Candidate 1: take the queen

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

### A. The counts

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

### B. Cause or consequence

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

### C. What happens next

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

### D. Sample size

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

### E. Cross-team

Vibing++ and SSS do all of it. forgot does the small-dragon part from round 100 on and not the long-dragon part, and
is level with them. forgot's price for that can be seen (`x_c1e.py`, `x_out/c1e.txt`): it ends 66 of 632 games (10%)
with its own queen dead and hers alive, against 38 of 502 (8%) and 28 of 503 (6%), and in the 55 games in which it
passed up the first chance and took no later one it won 45% (75% when it took the first). That is the size of thing
this rule is worth to a top team: one or two games in a hundred.
A 2000+ team that does the opposite and does well: fandagong takes 47% and is rated 2131; its record in this data
(against the top three) is 26%, so it is no counter-example either way.

### F. Earlier experiments

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

### G. Backfire

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

### H. The code claim

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

### What is left of the claim

| | B | after the attacks |
|---|---|---|
| the behaviour gap | 22% against 86 to 100% | the same; holds against each opponent and in every run |
| games that end differently | 6 to 13 of 401, "7 by the count I trust most" | 6 by reading each game (4 of 275 for the live bot); 3 to 11 by the natural experiment, zero not excluded |
| points | +1.5 to +3.2, most likely +1.5 to +2 | **+0.5 to +2, most likely about +1** |
| what it rests on | the top three do it | two of three do all of it; the online trials of its tested half moved the behaviour and not the end state |
| where it acts | "at every state of the economy" | not in the lowest economy band, where 41% of the chances are; mostly late kills of a fed or last queen |
| cost | one switch, one condition | agreed |
