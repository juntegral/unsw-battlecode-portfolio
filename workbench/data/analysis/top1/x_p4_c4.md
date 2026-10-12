## Candidate 4: do not give way at contact

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

### A. The counts

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

### B. Cause or consequence

- Among the top three on big maps the number of rams a side starts does not go with winning: 63.9 a game in wins,
  66.9 in losses (B: 64 and 67), swing +1.28 and +1.18. On the smaller maps it does for everybody (top three 15.7
  against 12.6, swing +1.37 against +0.61; we 13.8 against 6.2): there the side that is winning has the numbers at
  the meeting. So "they ram more" is what a team with dragons to spare does, and on big maps, where everyone has 55
  to 60 units, it separates nobody.
- For us on big maps it does separate (15.8 rams a game in the 9 wins, 9.2 in the 68 losses). Nine games.
- The comparison that would remove the confounder is the trial itself: same bot, one rule changed (item C).

### C. What happens next: the trial

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

### D. Sample size

- The behaviour counts: thousands of chances a cell. Not in doubt.
- Swing for the rams we do not make: 31 and 34 rams of the live bot in 77 games in the two rows the candidate adds
  (0.4 a game each). "-0.7" is a number on thirty rams.
- The trial: 12 games on the maps it changes, 30 in all. It cannot carry a verdict either way.
- Nine tenths of it acts on maps over 1,200 cells, 5 of the 15 known maps, where we win 12 of 111.
- By opponent: both of our usual opponents do it to us (test4 and WeHaveQuizzes start 52 rams a game against our 10).

### E. Cross-team

All three top teams and both of our usual opponents do all of it. There is no 2000+ team in the data that gives
way at contact as we do on big maps and does well. As behaviour to copy it is the best supported of the four; what
is missing is the part of the behaviour that makes it pay.

### F. Earlier experiments

- Online: tc30, above. 6 wins of 30 against a pooled 9.2; 0 of 12 on big maps.
- Local (`work/plan.md`): equal trades on every map ("TRADE_EVEN") and its variants were run against the release
  with no gain recorded; dropping the head count against a rushing copy of our bot won 60 of 118 where the base won
  68. The second agrees with B's reading (do not ram alone). Neither tests the candidate as written.
- Local games cannot show it: two copies of a bot that steps away never meet like this.

### G. Backfire

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

### H. The code claim

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

### What is left of the claim

| | B | after the attacks |
|---|---|---|
| the behaviour gap | on big maps we ram 15% / 2% where they ram 90% / 60 to 80% | the same |
| what the tested third did | rams x3, +21% length at round 300, 0 wins of 12 | the same; half of those 12 were lost with her queen alive, the other half at half the enemy's length |
| the untested two thirds | "between nothing and another +25 segments" | negative swing for us today on the rows it adds (30-odd rams each); positive only if our team also learns to eat after a ram |
| points | 0 to +2.4, single figure +1 | **-0.5 to +1.5; cannot be told** |
| "needs candidate 3" | two games | two games |
