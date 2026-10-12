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
